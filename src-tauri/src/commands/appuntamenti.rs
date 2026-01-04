// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamenti Commands
// Tauri commands for appuntamenti CRUD operations + conflict detection
//
// DATE HANDLING ARCHITECTURE (CRITICAL):
// - Storage: NaiveDateTime (NO timezone, local Italy time)
// - Format DB: TEXT "YYYY-MM-DDTHH:MM:SS" (naive, NO 'Z' suffix)
// - Parsing: NaiveDateTime::parse_from_str("%Y-%m-%dT%H:%M:%S")
// - NO UTC conversions (business locale Italia, 1 timezone)
// ═══════════════════════════════════════════════════════════════════

use chrono::{Datelike, Duration, NaiveDateTime, Weekday};
use serde::{Deserialize, Serialize};
use sqlx::{Row, SqlitePool};
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Appuntamento {
    pub id: String,
    pub cliente_id: String,
    pub servizio_id: String,
    pub operatore_id: Option<String>,
    /// Local time format: "2026-01-03T15:00:00" (naive, NO timezone)
    pub data_ora_inizio: String,
    /// Local time format: "2026-01-03T16:00:00" (naive, NO timezone)
    pub data_ora_fine: String,
    pub durata_minuti: i64,
    /// Stati: 'bozza', 'confermato', 'completato', 'cancellato', 'no_show'
    pub stato: String,
    pub prezzo: f64,
    pub sconto_percentuale: f64,
    pub prezzo_finale: f64,
    pub note: Option<String>,
    pub note_interne: Option<String>,
    /// Fonte: 'manuale', 'whatsapp', 'voice', 'online'
    pub fonte_prenotazione: String,
    pub reminder_inviato: i64,
    pub created_at: String,
    pub updated_at: String,
}

/// Extended appuntamento with related entities (for calendar view)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppuntamentoDettagliato {
    #[serde(flatten)]
    pub appuntamento: Appuntamento,
    pub cliente_nome: String,
    pub cliente_cognome: String,
    pub cliente_telefono: String,
    pub servizio_nome: String,
    pub servizio_colore: String,
    pub operatore_nome: Option<String>,
    pub operatore_cognome: Option<String>,
    pub operatore_colore: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateAppuntamentoInput {
    pub cliente_id: String,
    pub servizio_id: String,
    pub operatore_id: Option<String>,
    /// Format: "YYYY-MM-DDTHH:MM:SS" (naive, NO 'Z')
    pub data_ora_inizio: String,
    pub durata_minuti: i64,
    pub stato: Option<String>,
    pub prezzo: f64,
    pub sconto_percentuale: Option<f64>,
    pub note: Option<String>,
    pub note_interne: Option<String>,
    pub fonte_prenotazione: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateAppuntamentoInput {
    pub cliente_id: Option<String>,
    pub servizio_id: Option<String>,
    pub operatore_id: Option<String>,
    /// Format: "YYYY-MM-DDTHH:MM:SS" (naive, NO 'Z')
    pub data_ora_inizio: Option<String>,
    pub durata_minuti: Option<i64>,
    pub stato: Option<String>,
    pub prezzo: Option<f64>,
    pub sconto_percentuale: Option<f64>,
    pub note: Option<String>,
    pub note_interne: Option<String>,
    pub reminder_inviato: Option<i64>,
}

#[derive(Debug, Deserialize)]
pub struct GetAppuntamentiParams {
    /// ISO 8601: "YYYY-MM-DD"
    pub start_date: String,
    /// ISO 8601: "YYYY-MM-DD"
    pub end_date: String,
    pub operatore_id: Option<String>,
    pub cliente_id: Option<String>,
    pub stato: Option<String>,
}

// ───────────────────────────────────────────────────────────────────
// Helper Functions
// ───────────────────────────────────────────────────────────────────

/// Calculate end datetime from start + duration (NAIVE - NO TIMEZONE)
///
/// # Arguments
/// * `start` - Format: "YYYY-MM-DDTHH:MM:SS" (naive, local Italy time)
/// * `duration_minutes` - Duration in minutes
///
/// # Returns
/// * `Ok(String)` - End datetime in format "YYYY-MM-DDTHH:MM:SS" (naive, NO 'Z')
/// * `Err(String)` - Parse error message
fn calculate_end_datetime(start: &str, duration_minutes: i64) -> Result<String, String> {
    // Remove trailing 'Z' if present (from frontend toISOString bug)
    let start_clean = start.trim_end_matches('Z');

    // Parse as NaiveDateTime (NO timezone) to preserve local time
    let start_dt = NaiveDateTime::parse_from_str(start_clean, "%Y-%m-%dT%H:%M:%S")
        .or_else(|_| {
            // Fallback: try parsing with milliseconds
            NaiveDateTime::parse_from_str(start_clean, "%Y-%m-%dT%H:%M:%S%.f")
        })
        .map_err(|e| format!("Invalid datetime format '{}': {}", start, e))?;

    // Add duration
    let end_dt = start_dt + Duration::minutes(duration_minutes);

    // Return in naive format (NO 'Z' suffix)
    Ok(end_dt.format("%Y-%m-%dT%H:%M:%S").to_string())
}

/// Validate appointment time against business hours, holidays, and past dates
///
/// # Validation Rules
/// 1. No appointments in the past
/// 2. No appointments on Italian holidays
/// 3. Appointment must fall within working hours (orari_lavoro tipo='lavoro')
/// 4. Appointment must NOT overlap with breaks (orari_lavoro tipo='pausa')
/// 5. Appointment must end before closing time
///
/// # Arguments
/// * `pool` - SQLite connection pool
/// * `data_ora_inizio` - Start datetime "YYYY-MM-DDTHH:MM:SS" (naive)
/// * `durata_minuti` - Duration in minutes
/// * `operatore_id` - Optional operator ID
///
/// # Returns
/// * `Ok(())` - Valid appointment time
/// * `Err(String)` - User-friendly error message explaining why invalid
async fn validate_business_hours(
    pool: &SqlitePool,
    data_ora_inizio: &str,
    durata_minuti: i64,
    operatore_id: Option<&String>,
) -> Result<(), String> {
    // Parse data/ora
    let dt =
        NaiveDateTime::parse_from_str(data_ora_inizio.trim_end_matches('Z'), "%Y-%m-%dT%H:%M:%S")
            .map_err(|e| format!("Formato data/ora non valido: {}", e))?;

    let data = dt.date();
    let ora_inizio = dt.time();

    // Calculate ora_fine
    let ora_fine = (dt + Duration::minutes(durata_minuti)).time();

    // CHECK 0: No appointments crossing midnight (NaiveTime wraps, causes validation bugs)
    if ora_fine < ora_inizio {
        return Err(
            "❌ Appuntamento non può estendersi oltre mezzanotte. Scegli un orario precedente."
                .to_string(),
        );
    }

    // CHECK 1: No past appointments
    let now = chrono::Local::now().naive_local();
    if dt < now {
        return Err("❌ Non puoi prenotare nel passato".to_string());
    }

    // CHECK 2: No appointments on Italian holidays
    let data_str = data.format("%Y-%m-%d").to_string();
    let festivo_count: (i64,) =
        sqlx::query_as("SELECT COUNT(*) FROM giorni_festivi WHERE data = ?")
            .bind(&data_str)
            .fetch_one(pool)
            .await
            .map_err(|e| format!("Errore controllo festività: {}", e))?;

    if festivo_count.0 > 0 {
        let festivo: (String,) =
            sqlx::query_as("SELECT descrizione FROM giorni_festivi WHERE data = ? LIMIT 1")
                .bind(&data_str)
                .fetch_one(pool)
                .await
                .map_err(|e| format!("Errore fetch festività: {}", e))?;

        return Err(format!("🔴 Giorno festivo: {}", festivo.0));
    }

    // CHECK 3: Working hours validation
    let giorno_settimana = match data.weekday() {
        Weekday::Sun => 0,
        Weekday::Mon => 1,
        Weekday::Tue => 2,
        Weekday::Wed => 3,
        Weekday::Thu => 4,
        Weekday::Fri => 5,
        Weekday::Sat => 6,
    };

    // Get working hours for this day
    let orari: Vec<(String, String)> = if let Some(op_id) = operatore_id {
        sqlx::query_as(
            "SELECT ora_inizio, ora_fine FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'lavoro' AND (operatore_id = ? OR operatore_id IS NULL)
             ORDER BY ora_inizio"
        )
        .bind(giorno_settimana)
        .bind(op_id)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("Errore fetch orari: {}", e))?
    } else {
        sqlx::query_as(
            "SELECT ora_inizio, ora_fine FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'lavoro' AND operatore_id IS NULL
             ORDER BY ora_inizio",
        )
        .bind(giorno_settimana)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("Errore fetch orari: {}", e))?
    };

    if orari.is_empty() {
        return Err("🔴 Giorno non lavorativo (chiuso)".to_string());
    }

    // Check if appointment falls within working hours
    let mut dentro_fascia_lavoro = false;
    for (fascia_inizio_str, fascia_fine_str) in &orari {
        let fascia_inizio = chrono::NaiveTime::parse_from_str(fascia_inizio_str, "%H:%M")
            .map_err(|e| format!("Formato ora_inizio non valido: {}", e))?;
        let fascia_fine = chrono::NaiveTime::parse_from_str(fascia_fine_str, "%H:%M")
            .map_err(|e| format!("Formato ora_fine non valido: {}", e))?;

        if ora_inizio >= fascia_inizio && ora_fine <= fascia_fine {
            dentro_fascia_lavoro = true;
            break;
        }
    }

    if !dentro_fascia_lavoro {
        let prima_fascia = &orari[0];
        return Err(format!(
            "⏰ Fuori orario lavorativo. Orari: {} - {}",
            prima_fascia.0,
            orari.last().unwrap().1
        ));
    }

    // CHECK 4: No overlap with breaks (pausa pranzo)
    let pause: Vec<(String, String)> = if let Some(op_id) = operatore_id {
        sqlx::query_as(
            "SELECT ora_inizio, ora_fine FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'pausa' AND (operatore_id = ? OR operatore_id IS NULL)"
        )
        .bind(giorno_settimana)
        .bind(op_id)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("Errore fetch pause: {}", e))?
    } else {
        sqlx::query_as(
            "SELECT ora_inizio, ora_fine FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'pausa' AND operatore_id IS NULL",
        )
        .bind(giorno_settimana)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("Errore fetch pause: {}", e))?
    };

    for (pausa_inizio_str, pausa_fine_str) in &pause {
        let pausa_inizio = chrono::NaiveTime::parse_from_str(pausa_inizio_str, "%H:%M")
            .map_err(|e| format!("Formato ora_inizio pausa non valido: {}", e))?;
        let pausa_fine = chrono::NaiveTime::parse_from_str(pausa_fine_str, "%H:%M")
            .map_err(|e| format!("Formato ora_fine pausa non valido: {}", e))?;

        // Check overlap with break
        let overlap = !(ora_fine <= pausa_inizio || ora_inizio >= pausa_fine);
        if overlap {
            return Err(format!(
                "☕ Appuntamento sovrapposto a pausa ({} - {})",
                pausa_inizio_str, pausa_fine_str
            ));
        }
    }

    Ok(())
}

/// Check for conflicts with existing appointments for same operator
///
/// # Logic
/// Two appointments overlap if:
/// - (start1 < end2) AND (end1 > start2)
///
/// # Arguments
/// * `pool` - SQLite connection pool
/// * `operatore_id` - Operator ID to check (None = no conflicts possible)
/// * `start` - Start datetime (naive format)
/// * `end` - End datetime (naive format)
/// * `exclude_id` - Appointment ID to exclude (for updates)
///
/// # Returns
/// * `Ok(true)` - Conflict found
/// * `Ok(false)` - No conflicts
/// * `Err(String)` - Database error
async fn check_conflicts(
    pool: &SqlitePool,
    operatore_id: Option<&String>,
    start: &str,
    end: &str,
    exclude_id: Option<&String>,
) -> Result<bool, String> {
    // No operator assigned → no conflicts possible
    if operatore_id.is_none() {
        return Ok(false);
    }

    let mut query = String::from(
        r#"
        SELECT COUNT(*) as count FROM appuntamenti
        WHERE operatore_id = ?
        AND LOWER(stato) NOT IN ('cancellato', 'eliminato', 'no_show')
        AND (
            (data_ora_inizio < ? AND data_ora_fine > ?)
        )
        "#,
    );

    // Exclude current appointment if updating
    if exclude_id.is_some() {
        query.push_str(" AND id != ?");
    }

    let mut q = sqlx::query_scalar::<_, i64>(&query)
        .bind(operatore_id.unwrap())
        .bind(end)
        .bind(start);

    if let Some(id) = exclude_id {
        q = q.bind(id);
    }

    let count = q
        .fetch_one(pool)
        .await
        .map_err(|e| format!("Failed to check conflicts: {}", e))?;

    Ok(count > 0)
}

/// Get current timestamp in naive format (local time)
fn now_naive() -> String {
    use chrono::Local;
    Local::now()
        .naive_local()
        .format("%Y-%m-%dT%H:%M:%S")
        .to_string()
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get appuntamenti by date range (for calendar view)
///
/// # Query
/// - JOINs: clienti, servizi, operatori (left join)
/// - Filters: date range, operatore, cliente, stato
/// - Excludes: stato IN ('cancellato', 'eliminato')
/// - Order: data_ora_inizio ASC
#[tauri::command]
pub async fn get_appuntamenti(
    pool: State<'_, SqlitePool>,
    params: GetAppuntamentiParams,
) -> Result<Vec<AppuntamentoDettagliato>, String> {
    let mut query = String::from(
        r#"
        SELECT
            a.*,
            c.nome as cliente_nome,
            c.cognome as cliente_cognome,
            c.telefono as cliente_telefono,
            s.nome as servizio_nome,
            s.colore as servizio_colore,
            o.nome as operatore_nome,
            o.cognome as operatore_cognome,
            o.colore as operatore_colore
        FROM appuntamenti a
        INNER JOIN clienti c ON a.cliente_id = c.id
        INNER JOIN servizi s ON a.servizio_id = s.id
        LEFT JOIN operatori o ON a.operatore_id = o.id
        WHERE DATE(a.data_ora_inizio) >= DATE(?)
        AND DATE(a.data_ora_inizio) <= DATE(?)
        AND LOWER(a.stato) NOT IN ('cancellato', 'eliminato')
        "#,
    );

    let mut bindings: Vec<String> = vec![params.start_date.clone(), params.end_date.clone()];

    if let Some(operatore_id) = &params.operatore_id {
        query.push_str(" AND a.operatore_id = ?");
        bindings.push(operatore_id.clone());
    }

    if let Some(cliente_id) = &params.cliente_id {
        query.push_str(" AND a.cliente_id = ?");
        bindings.push(cliente_id.clone());
    }

    if let Some(stato) = &params.stato {
        query.push_str(" AND a.stato = ?");
        bindings.push(stato.clone());
    }

    query.push_str(" ORDER BY a.data_ora_inizio ASC");

    // Build query with dynamic bindings
    let mut q = sqlx::query(&query);
    for binding in bindings {
        q = q.bind(binding);
    }

    let rows = q
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch appuntamenti: {}", e))?;

    let mut result = Vec::new();
    for row in rows {
        result.push(AppuntamentoDettagliato {
            appuntamento: Appuntamento {
                id: row.try_get("id").unwrap(),
                cliente_id: row.try_get("cliente_id").unwrap(),
                servizio_id: row.try_get("servizio_id").unwrap(),
                operatore_id: row.try_get("operatore_id").ok(),
                data_ora_inizio: row.try_get("data_ora_inizio").unwrap(),
                data_ora_fine: row.try_get("data_ora_fine").unwrap(),
                durata_minuti: row.try_get("durata_minuti").unwrap(),
                stato: row.try_get("stato").unwrap(),
                prezzo: row.try_get("prezzo").unwrap(),
                sconto_percentuale: row.try_get("sconto_percentuale").unwrap(),
                prezzo_finale: row.try_get("prezzo_finale").unwrap(),
                note: row.try_get("note").ok(),
                note_interne: row.try_get("note_interne").ok(),
                fonte_prenotazione: row.try_get("fonte_prenotazione").unwrap(),
                reminder_inviato: row.try_get("reminder_inviato").unwrap(),
                created_at: row.try_get("created_at").unwrap(),
                updated_at: row.try_get("updated_at").unwrap(),
            },
            cliente_nome: row.try_get("cliente_nome").unwrap(),
            cliente_cognome: row.try_get("cliente_cognome").unwrap(),
            cliente_telefono: row.try_get("cliente_telefono").unwrap(),
            servizio_nome: row.try_get("servizio_nome").unwrap(),
            servizio_colore: row.try_get("servizio_colore").unwrap(),
            operatore_nome: row.try_get("operatore_nome").ok(),
            operatore_cognome: row.try_get("operatore_cognome").ok(),
            operatore_colore: row.try_get("operatore_colore").ok(),
        });
    }

    Ok(result)
}

/// Get single appuntamento by ID
#[tauri::command]
pub async fn get_appuntamento(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<Appuntamento, String> {
    sqlx::query_as::<_, Appuntamento>("SELECT * FROM appuntamenti WHERE id = ?")
        .bind(id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Appuntamento not found: {}", e))
}

/// Create new appuntamento with conflict detection
///
/// # Steps
/// 1. Calculate end datetime from start + duration
/// 2. Check for conflicts with same operator
/// 3. Calculate final price (prezzo - sconto%)
/// 4. INSERT into database
/// 5. Return created appuntamento
#[tauri::command]
pub async fn create_appuntamento(
    pool: State<'_, SqlitePool>,
    input: CreateAppuntamentoInput,
) -> Result<Appuntamento, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = now_naive();

    // Calculate end datetime (NAIVE - NO TIMEZONE)
    let data_ora_fine = calculate_end_datetime(&input.data_ora_inizio, input.durata_minuti)?;

    // Validate business hours, holidays, and past dates
    validate_business_hours(
        pool.inner(),
        &input.data_ora_inizio,
        input.durata_minuti,
        input.operatore_id.as_ref(),
    )
    .await?;

    // Check for conflicts
    let has_conflict = check_conflicts(
        pool.inner(),
        input.operatore_id.as_ref(),
        &input.data_ora_inizio,
        &data_ora_fine,
        None,
    )
    .await?;

    if has_conflict {
        return Err("Conflitto: operatore già impegnato in questo orario".to_string());
    }

    // Calculate final price
    let sconto = input.sconto_percentuale.unwrap_or(0.0);
    let prezzo_finale = input.prezzo * (1.0 - sconto / 100.0);

    sqlx::query(
        r#"
        INSERT INTO appuntamenti (
            id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine,
            durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale,
            note, note_interne, fonte_prenotazione, reminder_inviato,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.cliente_id)
    .bind(&input.servizio_id)
    .bind(&input.operatore_id)
    .bind(&input.data_ora_inizio)
    .bind(&data_ora_fine)
    .bind(input.durata_minuti)
    .bind(input.stato.unwrap_or_else(|| "confermato".to_string()))
    .bind(input.prezzo)
    .bind(sconto)
    .bind(prezzo_finale)
    .bind(&input.note)
    .bind(&input.note_interne)
    .bind(
        input
            .fonte_prenotazione
            .unwrap_or_else(|| "manuale".to_string()),
    )
    .bind(0)
    .bind(&now)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create appuntamento: {}", e))?;

    get_appuntamento(pool, id).await
}

/// Update appuntamento with conflict detection
///
/// # Steps
/// 1. Fetch current appuntamento
/// 2. Merge input with current values
/// 3. Recalculate end datetime if start/duration changed
/// 4. Check for conflicts (excluding self)
/// 5. Recalculate final price if price/sconto changed
/// 6. UPDATE database
/// 7. Return updated appuntamento
#[tauri::command]
pub async fn update_appuntamento(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateAppuntamentoInput,
) -> Result<Appuntamento, String> {
    let now = now_naive();

    // Fetch current appuntamento
    let current = get_appuntamento(pool.clone(), id.clone()).await?;

    // Determine new values (merge input with current)
    let new_start = input
        .data_ora_inizio
        .as_ref()
        .unwrap_or(&current.data_ora_inizio);
    let new_duration = input.durata_minuti.unwrap_or(current.durata_minuti);
    let new_operatore = input
        .operatore_id
        .as_ref()
        .or(current.operatore_id.as_ref());

    // Recalculate end datetime if start or duration changed
    let new_end = if input.data_ora_inizio.is_some() || input.durata_minuti.is_some() {
        calculate_end_datetime(new_start, new_duration)?
    } else {
        current.data_ora_fine.clone()
    };

    // Validate business hours if datetime or duration changed
    if input.data_ora_inizio.is_some() || input.durata_minuti.is_some() {
        validate_business_hours(pool.inner(), new_start, new_duration, new_operatore).await?;
    }

    // Check for conflicts (exclude current appointment)
    let has_conflict =
        check_conflicts(pool.inner(), new_operatore, new_start, &new_end, Some(&id)).await?;

    if has_conflict {
        return Err("Conflitto: operatore già impegnato in questo orario".to_string());
    }

    // Recalculate final price if price or sconto changed
    let new_prezzo = input.prezzo.unwrap_or(current.prezzo);
    let new_sconto = input
        .sconto_percentuale
        .unwrap_or(current.sconto_percentuale);
    let new_prezzo_finale = new_prezzo * (1.0 - new_sconto / 100.0);

    sqlx::query(
        r#"
        UPDATE appuntamenti SET
            cliente_id = ?, servizio_id = ?, operatore_id = ?,
            data_ora_inizio = ?, data_ora_fine = ?, durata_minuti = ?,
            stato = ?, prezzo = ?, sconto_percentuale = ?, prezzo_finale = ?,
            note = ?, note_interne = ?, reminder_inviato = ?, updated_at = ?
        WHERE id = ?
        "#,
    )
    .bind(input.cliente_id.unwrap_or(current.cliente_id))
    .bind(input.servizio_id.unwrap_or(current.servizio_id))
    .bind(new_operatore)
    .bind(new_start)
    .bind(&new_end)
    .bind(new_duration)
    .bind(input.stato.unwrap_or(current.stato))
    .bind(new_prezzo)
    .bind(new_sconto)
    .bind(new_prezzo_finale)
    .bind(input.note.or(current.note))
    .bind(input.note_interne.or(current.note_interne))
    .bind(input.reminder_inviato.unwrap_or(current.reminder_inviato))
    .bind(&now)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update appuntamento: {}", e))?;

    get_appuntamento(pool, id).await
}

/// Delete appuntamento (SOFT DELETE: set stato = 'cancellato' + deleted_at)
#[tauri::command]
pub async fn delete_appuntamento(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    let now = now_naive();

    sqlx::query(
        "UPDATE appuntamenti SET stato = 'Cancellato', deleted_at = ?, updated_at = ? WHERE id = ?",
    )
    .bind(&now)
    .bind(&now)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to delete appuntamento: {}", e))?;

    Ok(())
}

/// Confirm pending appointment (change stato from 'bozza'/'in_attesa_conferma' to 'confermato')
///
/// Used by operator to approve appointments from WhatsApp, Voice, or other external channels.
/// Validates business hours before confirming.
#[tauri::command]
pub async fn confirm_appuntamento(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<Appuntamento, String> {
    let now = now_naive();

    // Fetch current appointment
    let current = get_appuntamento(pool.clone(), id.clone()).await?;

    // Re-validate business hours (in case schedule changed)
    validate_business_hours(
        pool.inner(),
        &current.data_ora_inizio,
        current.durata_minuti,
        current.operatore_id.as_ref(),
    )
    .await?;

    // Check for conflicts before confirming
    let has_conflict = check_conflicts(
        pool.inner(),
        current.operatore_id.as_ref(),
        &current.data_ora_inizio,
        &current.data_ora_fine,
        Some(&id),
    )
    .await?;

    if has_conflict {
        return Err("Conflitto: operatore già impegnato in questo orario".to_string());
    }

    // Update stato to 'confermato'
    sqlx::query("UPDATE appuntamenti SET stato = 'confermato', updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to confirm appuntamento: {}", e))?;

    get_appuntamento(pool, id).await
}

/// Reject pending appointment (change stato to 'cancellato')
///
/// Used by operator to reject appointments from WhatsApp, Voice, or other external channels.
#[tauri::command]
pub async fn reject_appuntamento(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    let now = now_naive();

    sqlx::query("UPDATE appuntamenti SET stato = 'Cancellato', updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to reject appuntamento: {}", e))?;

    Ok(())
}
