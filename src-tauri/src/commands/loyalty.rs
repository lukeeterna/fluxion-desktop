// ═══════════════════════════════════════════════════════════════════
// FLUXION - Loyalty & Pacchetti Commands (Fase 5 - Quick Wins)
// Tessera timbri digitale, VIP, Referral, Pacchetti
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoyaltyInfo {
    pub cliente_id: String,
    pub nome: String,
    pub cognome: String,
    pub loyalty_visits: i32,
    pub loyalty_threshold: i32,
    pub is_vip: bool,
    pub referral_source: Option<String>,
    pub progress_percent: f64,
    pub visits_remaining: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pacchetto {
    pub id: String,
    pub nome: String,
    pub descrizione: Option<String>,
    pub prezzo: f64,
    pub prezzo_originale: Option<f64>,
    pub servizi_inclusi: i32,
    pub validita_giorni: i32,
    pub attivo: bool,
    pub risparmio: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClientePacchetto {
    pub id: String,
    pub cliente_id: String,
    pub pacchetto_id: String,
    pub pacchetto_nome: String,
    pub stato: String,
    pub servizi_usati: i32,
    pub servizi_totali: i32,
    pub data_acquisto: Option<String>,
    pub data_scadenza: Option<String>,
    pub progress_percent: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TopReferrer {
    pub cliente_id: String,
    pub nome: String,
    pub cognome: String,
    pub referral_count: i32,
}

// ───────────────────────────────────────────────────────────────────
// Loyalty Commands
// ───────────────────────────────────────────────────────────────────

/// Get loyalty info for a specific cliente
#[tauri::command]
pub async fn get_loyalty_info(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<LoyaltyInfo, String> {
    let row = sqlx::query_as::<_, (String, String, String, i32, i32, i32, Option<String>)>(
        r#"
        SELECT id, nome, cognome,
               COALESCE(loyalty_visits, 0) as loyalty_visits,
               COALESCE(loyalty_threshold, 10) as loyalty_threshold,
               COALESCE(is_vip, 0) as is_vip,
               referral_source
        FROM clienti
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&cliente_id)
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?
    .ok_or_else(|| "Cliente not found".to_string())?;

    let threshold = if row.4 > 0 { row.4 } else { 10 };
    let progress = (row.3 as f64 / threshold as f64 * 100.0).min(100.0);

    Ok(LoyaltyInfo {
        cliente_id: row.0,
        nome: row.1,
        cognome: row.2,
        loyalty_visits: row.3,
        loyalty_threshold: threshold,
        is_vip: row.5 == 1,
        referral_source: row.6,
        progress_percent: progress,
        visits_remaining: (threshold - row.3).max(0),
    })
}

/// Increment loyalty visits (chiamato quando appuntamento completato)
#[tauri::command]
pub async fn increment_loyalty_visits(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<LoyaltyInfo, String> {
    // Increment visits
    sqlx::query(
        r#"
        UPDATE clienti
        SET loyalty_visits = COALESCE(loyalty_visits, 0) + 1,
            updated_at = datetime('now')
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&cliente_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to increment visits: {}", e))?;

    // Return updated info
    get_loyalty_info(pool, cliente_id).await
}

/// Toggle VIP status
#[tauri::command]
pub async fn toggle_vip_status(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    is_vip: bool,
) -> Result<bool, String> {
    sqlx::query(
        r#"
        UPDATE clienti
        SET is_vip = ?,
            updated_at = datetime('now')
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(if is_vip { 1 } else { 0 })
    .bind(&cliente_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update VIP status: {}", e))?;

    Ok(is_vip)
}

/// Set referral source for cliente
#[tauri::command]
pub async fn set_referral_source(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    referral_source: Option<String>,
    referral_cliente_id: Option<String>,
) -> Result<(), String> {
    sqlx::query(
        r#"
        UPDATE clienti
        SET referral_source = ?,
            referral_cliente_id = ?,
            updated_at = datetime('now')
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&referral_source)
    .bind(&referral_cliente_id)
    .bind(&cliente_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to set referral: {}", e))?;

    Ok(())
}

/// Get top referrers (clienti che hanno portato più amici)
#[tauri::command]
pub async fn get_top_referrers(
    pool: State<'_, SqlitePool>,
    limit: Option<i32>,
) -> Result<Vec<TopReferrer>, String> {
    let limit = limit.unwrap_or(10);

    let rows = sqlx::query_as::<_, (String, String, String, i32)>(
        r#"
        SELECT c.id, c.nome, c.cognome, COUNT(r.id) as referral_count
        FROM clienti c
        INNER JOIN clienti r ON r.referral_cliente_id = c.id
        WHERE c.deleted_at IS NULL AND r.deleted_at IS NULL
        GROUP BY c.id
        HAVING referral_count > 0
        ORDER BY referral_count DESC
        LIMIT ?
        "#,
    )
    .bind(limit)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(rows
        .into_iter()
        .map(|r| TopReferrer {
            cliente_id: r.0,
            nome: r.1,
            cognome: r.2,
            referral_count: r.3,
        })
        .collect())
}

/// Get clienti at loyalty milestone (prossimi al premio)
#[tauri::command]
pub async fn get_loyalty_milestones(
    pool: State<'_, SqlitePool>,
    visits_remaining_max: Option<i32>,
) -> Result<Vec<LoyaltyInfo>, String> {
    let max_remaining = visits_remaining_max.unwrap_or(3);

    let rows = sqlx::query_as::<_, (String, String, String, i32, i32, i32, Option<String>)>(
        r#"
        SELECT id, nome, cognome,
               COALESCE(loyalty_visits, 0) as visits,
               COALESCE(loyalty_threshold, 10) as threshold,
               COALESCE(is_vip, 0) as is_vip,
               referral_source
        FROM clienti
        WHERE deleted_at IS NULL
          AND (COALESCE(loyalty_threshold, 10) - COALESCE(loyalty_visits, 0)) <= ?
          AND (COALESCE(loyalty_threshold, 10) - COALESCE(loyalty_visits, 0)) > 0
        ORDER BY (COALESCE(loyalty_threshold, 10) - COALESCE(loyalty_visits, 0)) ASC
        "#,
    )
    .bind(max_remaining)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(rows
        .into_iter()
        .map(|r| {
            let threshold = if r.4 > 0 { r.4 } else { 10 };
            let progress = (r.3 as f64 / threshold as f64 * 100.0).min(100.0);
            LoyaltyInfo {
                cliente_id: r.0,
                nome: r.1,
                cognome: r.2,
                loyalty_visits: r.3,
                loyalty_threshold: threshold,
                is_vip: r.5 == 1,
                referral_source: r.6,
                progress_percent: progress,
                visits_remaining: (threshold - r.3).max(0),
            }
        })
        .collect())
}

// ───────────────────────────────────────────────────────────────────
// Pacchetti Commands
// ───────────────────────────────────────────────────────────────────

/// Get all active pacchetti
#[tauri::command]
pub async fn get_pacchetti(pool: State<'_, SqlitePool>) -> Result<Vec<Pacchetto>, String> {
    let rows = sqlx::query_as::<_, (String, String, Option<String>, f64, Option<f64>, i32, i32, i32)>(
        r#"
        SELECT id, nome, descrizione, prezzo, prezzo_originale,
               servizi_inclusi, validita_giorni, attivo
        FROM pacchetti
        WHERE attivo = 1
        ORDER BY prezzo ASC
        "#,
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(rows
        .into_iter()
        .map(|r| {
            let risparmio = r.4.map(|orig| orig - r.3);
            Pacchetto {
                id: r.0,
                nome: r.1,
                descrizione: r.2,
                prezzo: r.3,
                prezzo_originale: r.4,
                servizi_inclusi: r.5,
                validita_giorni: r.6,
                attivo: r.7 == 1,
                risparmio,
            }
        })
        .collect())
}

/// Create a new pacchetto
#[tauri::command]
pub async fn create_pacchetto(
    pool: State<'_, SqlitePool>,
    nome: String,
    descrizione: Option<String>,
    prezzo: f64,
    prezzo_originale: Option<f64>,
    servizi_inclusi: i32,
    validita_giorni: Option<i32>,
) -> Result<Pacchetto, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let validita = validita_giorni.unwrap_or(365);

    sqlx::query(
        r#"
        INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, validita_giorni, attivo)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        "#,
    )
    .bind(&id)
    .bind(&nome)
    .bind(&descrizione)
    .bind(prezzo)
    .bind(prezzo_originale)
    .bind(servizi_inclusi)
    .bind(validita)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create pacchetto: {}", e))?;

    Ok(Pacchetto {
        id,
        nome,
        descrizione,
        prezzo,
        prezzo_originale,
        servizi_inclusi,
        validita_giorni: validita,
        attivo: true,
        risparmio: prezzo_originale.map(|orig| orig - prezzo),
    })
}

/// Assign pacchetto to cliente (proposta)
#[tauri::command]
pub async fn proponi_pacchetto(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    pacchetto_id: String,
) -> Result<ClientePacchetto, String> {
    // Get pacchetto info
    let pacchetto = sqlx::query_as::<_, (String, i32)>(
        "SELECT nome, servizi_inclusi FROM pacchetti WHERE id = ?",
    )
    .bind(&pacchetto_id)
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?
    .ok_or_else(|| "Pacchetto not found".to_string())?;

    let id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        r#"
        INSERT INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali)
        VALUES (?, ?, ?, 'proposto', 0, ?)
        "#,
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&pacchetto_id)
    .bind(pacchetto.1)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to propose pacchetto: {}", e))?;

    Ok(ClientePacchetto {
        id,
        cliente_id,
        pacchetto_id,
        pacchetto_nome: pacchetto.0,
        stato: "proposto".to_string(),
        servizi_usati: 0,
        servizi_totali: pacchetto.1,
        data_acquisto: None,
        data_scadenza: None,
        progress_percent: 0.0,
    })
}

/// Mark pacchetto as sold (pagato)
#[tauri::command]
pub async fn conferma_acquisto_pacchetto(
    pool: State<'_, SqlitePool>,
    cliente_pacchetto_id: String,
    metodo_pagamento: String,
    validita_giorni: i32,
) -> Result<ClientePacchetto, String> {
    let scadenza = chrono::Local::now()
        .checked_add_signed(chrono::Duration::days(validita_giorni as i64))
        .map(|d| d.format("%Y-%m-%d").to_string())
        .unwrap_or_default();

    sqlx::query(
        r#"
        UPDATE clienti_pacchetti
        SET stato = 'venduto',
            data_acquisto = datetime('now'),
            data_scadenza = ?,
            metodo_pagamento = ?,
            pagato = 1,
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(&scadenza)
    .bind(&metodo_pagamento)
    .bind(&cliente_pacchetto_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to confirm purchase: {}", e))?;

    // Get updated info
    get_cliente_pacchetto(pool, cliente_pacchetto_id).await
}

/// Use a service from pacchetto
#[tauri::command]
pub async fn usa_servizio_pacchetto(
    pool: State<'_, SqlitePool>,
    cliente_pacchetto_id: String,
) -> Result<ClientePacchetto, String> {
    // First check current status
    let current = sqlx::query_as::<_, (i32, i32, String)>(
        "SELECT servizi_usati, servizi_totali, stato FROM clienti_pacchetti WHERE id = ?",
    )
    .bind(&cliente_pacchetto_id)
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?
    .ok_or_else(|| "Pacchetto not found".to_string())?;

    if current.2 == "completato" || current.2 == "scaduto" {
        return Err("Pacchetto already completed or expired".to_string());
    }

    let new_used = current.0 + 1;
    let new_stato = if new_used >= current.1 {
        "completato"
    } else {
        "in_uso"
    };

    sqlx::query(
        r#"
        UPDATE clienti_pacchetti
        SET servizi_usati = ?,
            stato = ?,
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(new_used)
    .bind(new_stato)
    .bind(&cliente_pacchetto_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to use service: {}", e))?;

    get_cliente_pacchetto(pool, cliente_pacchetto_id).await
}

/// Get cliente pacchetto by ID
#[tauri::command]
pub async fn get_cliente_pacchetto(
    pool: State<'_, SqlitePool>,
    cliente_pacchetto_id: String,
) -> Result<ClientePacchetto, String> {
    let row = sqlx::query_as::<_, (String, String, String, String, String, i32, i32, Option<String>, Option<String>)>(
        r#"
        SELECT cp.id, cp.cliente_id, cp.pacchetto_id, p.nome, cp.stato,
               cp.servizi_usati, cp.servizi_totali, cp.data_acquisto, cp.data_scadenza
        FROM clienti_pacchetti cp
        JOIN pacchetti p ON p.id = cp.pacchetto_id
        WHERE cp.id = ?
        "#,
    )
    .bind(&cliente_pacchetto_id)
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?
    .ok_or_else(|| "Cliente pacchetto not found".to_string())?;

    let progress = if row.6 > 0 {
        (row.5 as f64 / row.6 as f64 * 100.0).min(100.0)
    } else {
        0.0
    };

    Ok(ClientePacchetto {
        id: row.0,
        cliente_id: row.1,
        pacchetto_id: row.2,
        pacchetto_nome: row.3,
        stato: row.4,
        servizi_usati: row.5,
        servizi_totali: row.6,
        data_acquisto: row.7,
        data_scadenza: row.8,
        progress_percent: progress,
    })
}

/// Get all pacchetti for a cliente
#[tauri::command]
pub async fn get_cliente_pacchetti(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Vec<ClientePacchetto>, String> {
    let rows = sqlx::query_as::<_, (String, String, String, String, String, i32, i32, Option<String>, Option<String>)>(
        r#"
        SELECT cp.id, cp.cliente_id, cp.pacchetto_id, p.nome, cp.stato,
               cp.servizi_usati, cp.servizi_totali, cp.data_acquisto, cp.data_scadenza
        FROM clienti_pacchetti cp
        JOIN pacchetti p ON p.id = cp.pacchetto_id
        WHERE cp.cliente_id = ?
        ORDER BY cp.created_at DESC
        "#,
    )
    .bind(&cliente_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(rows
        .into_iter()
        .map(|r| {
            let progress = if r.6 > 0 {
                (r.5 as f64 / r.6 as f64 * 100.0).min(100.0)
            } else {
                0.0
            };
            ClientePacchetto {
                id: r.0,
                cliente_id: r.1,
                pacchetto_id: r.2,
                pacchetto_nome: r.3,
                stato: r.4,
                servizi_usati: r.5,
                servizi_totali: r.6,
                data_acquisto: r.7,
                data_scadenza: r.8,
                progress_percent: progress,
            }
        })
        .collect())
}
