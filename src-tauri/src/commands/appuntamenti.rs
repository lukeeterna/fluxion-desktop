// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamenti Commands
// Tauri commands for appuntamenti CRUD operations + conflict detection
// ═══════════════════════════════════════════════════════════════════

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
    pub data_ora_inizio: String,
    pub data_ora_fine: String,
    pub durata_minuti: i64,
    pub stato: String,
    pub prezzo: f64,
    pub sconto_percentuale: f64,
    pub prezzo_finale: f64,
    pub note: Option<String>,
    pub note_interne: Option<String>,
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
    pub start_date: String,  // ISO 8601: YYYY-MM-DD
    pub end_date: String,    // ISO 8601: YYYY-MM-DD
    pub operatore_id: Option<String>,
    pub cliente_id: Option<String>,
    pub stato: Option<String>,
}

// ───────────────────────────────────────────────────────────────────
// Helper Functions
// ───────────────────────────────────────────────────────────────────

/// Calculate end datetime from start + duration
fn calculate_end_datetime(start: &str, duration_minutes: i64) -> Result<String, String> {
    use chrono::{Duration, NaiveDateTime};

    // Parse as NaiveDateTime (no timezone) to keep local time
    // Format: "YYYY-MM-DDTHH:mm:ss" or "YYYY-MM-DDTHH:mm:ss.sssZ"
    let start_clean = start.trim_end_matches('Z');

    let start_dt = NaiveDateTime::parse_from_str(start_clean, "%Y-%m-%dT%H:%M:%S")
        .or_else(|_| NaiveDateTime::parse_from_str(start_clean, "%Y-%m-%dT%H:%M:%S%.f"))
        .map_err(|e| format!("Invalid start datetime '{}': {}", start, e))?;

    let end_dt = start_dt + Duration::minutes(duration_minutes);

    // Return in same format (local time, no timezone)
    Ok(end_dt.format("%Y-%m-%dT%H:%M:%S").to_string())
}

/// Check for conflicts with existing appointments for same operator
async fn check_conflicts(
    pool: &SqlitePool,
    operatore_id: Option<&String>,
    start: &str,
    end: &str,
    exclude_id: Option<&String>,
) -> Result<bool, String> {
    if operatore_id.is_none() {
        return Ok(false); // No operator assigned, no conflicts possible
    }

    let mut query = String::from(
        r#"
        SELECT COUNT(*) as count FROM appuntamenti
        WHERE operatore_id = ?
        AND stato NOT IN ('cancellato', 'no_show')
        AND (
            (data_ora_inizio < ? AND data_ora_fine > ?)
            OR (data_ora_inizio < ? AND data_ora_fine > ?)
            OR (data_ora_inizio >= ? AND data_ora_fine <= ?)
        )
        "#,
    );

    if let Some(_id) = exclude_id {
        query.push_str(" AND id != ?");
    }

    let mut q = sqlx::query_scalar::<_, i64>(&query)
        .bind(operatore_id.unwrap())
        .bind(end)
        .bind(start)
        .bind(end)
        .bind(start)
        .bind(start)
        .bind(end);

    if let Some(id) = exclude_id {
        q = q.bind(id);
    }

    let count = q
        .fetch_one(pool)
        .await
        .map_err(|e| format!("Failed to check conflicts: {}", e))?;

    Ok(count > 0)
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get appuntamenti by date range (for calendar view)
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
#[tauri::command]
pub async fn create_appuntamento(
    pool: State<'_, SqlitePool>,
    input: CreateAppuntamentoInput,
) -> Result<Appuntamento, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    // Calculate end datetime
    let data_ora_fine = calculate_end_datetime(&input.data_ora_inizio, input.durata_minuti)?;

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
#[tauri::command]
pub async fn update_appuntamento(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateAppuntamentoInput,
) -> Result<Appuntamento, String> {
    let now = chrono::Utc::now().to_rfc3339();

    // Fetch current appuntamento
    let current = get_appuntamento(pool.clone(), id.clone()).await?;

    // Determine new values
    let new_start = input
        .data_ora_inizio
        .as_ref()
        .unwrap_or(&current.data_ora_inizio);
    let new_duration = input.durata_minuti.unwrap_or(current.durata_minuti);
    let new_operatore = input.operatore_id.as_ref().or(current.operatore_id.as_ref());

    // Recalculate end datetime if start or duration changed
    let new_end = if input.data_ora_inizio.is_some() || input.durata_minuti.is_some() {
        calculate_end_datetime(new_start, new_duration)?
    } else {
        current.data_ora_fine.clone()
    };

    // Check for conflicts (exclude current appointment)
    let has_conflict = check_conflicts(
        pool.inner(),
        new_operatore,
        new_start,
        &new_end,
        Some(&id),
    )
    .await?;

    if has_conflict {
        return Err("Conflitto: operatore già impegnato in questo orario".to_string());
    }

    // Recalculate price if changed
    let new_prezzo = input.prezzo.unwrap_or(current.prezzo);
    let new_sconto = input.sconto_percentuale.unwrap_or(current.sconto_percentuale);
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

/// Delete appuntamento (set stato = 'cancellato')
#[tauri::command]
pub async fn delete_appuntamento(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query("UPDATE appuntamenti SET stato = 'cancellato', updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete appuntamento: {}", e))?;

    Ok(())
}
