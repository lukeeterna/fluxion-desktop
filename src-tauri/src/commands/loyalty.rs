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
    let rows = sqlx::query_as::<
        _,
        (
            String,
            String,
            Option<String>,
            f64,
            Option<f64>,
            i32,
            i32,
            i32,
        ),
    >(
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
    let row = sqlx::query_as::<
        _,
        (
            String,
            String,
            String,
            String,
            String,
            i32,
            i32,
            Option<String>,
            Option<String>,
        ),
    >(
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
    let rows = sqlx::query_as::<
        _,
        (
            String,
            String,
            String,
            String,
            String,
            i32,
            i32,
            Option<String>,
            Option<String>,
        ),
    >(
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

// ───────────────────────────────────────────────────────────────────
// Pacchetto Management Commands (Delete, Update, Servizi)
// ───────────────────────────────────────────────────────────────────

/// Delete a pacchetto (soft delete - set attivo = 0)
#[tauri::command]
pub async fn delete_pacchetto(
    pool: State<'_, SqlitePool>,
    pacchetto_id: String,
) -> Result<bool, String> {
    // Check if pacchetto has active clienti_pacchetti
    let active_count: (i64,) = sqlx::query_as(
        r#"
        SELECT COUNT(*) FROM clienti_pacchetti
        WHERE pacchetto_id = ? AND stato NOT IN ('completato', 'annullato', 'scaduto')
        "#,
    )
    .bind(&pacchetto_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    if active_count.0 > 0 {
        return Err(format!(
            "Impossibile eliminare: {} clienti hanno questo pacchetto attivo",
            active_count.0
        ));
    }

    // Soft delete (set attivo = 0)
    sqlx::query("UPDATE pacchetti SET attivo = 0, updated_at = datetime('now') WHERE id = ?")
        .bind(&pacchetto_id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete pacchetto: {}", e))?;

    Ok(true)
}

/// Update an existing pacchetto
#[allow(clippy::too_many_arguments)]
#[tauri::command]
pub async fn update_pacchetto(
    pool: State<'_, SqlitePool>,
    pacchetto_id: String,
    nome: String,
    descrizione: Option<String>,
    prezzo: f64,
    prezzo_originale: Option<f64>,
    servizi_inclusi: i32,
    validita_giorni: i32,
) -> Result<Pacchetto, String> {
    sqlx::query(
        r#"
        UPDATE pacchetti
        SET nome = ?, descrizione = ?, prezzo = ?, prezzo_originale = ?,
            servizi_inclusi = ?, validita_giorni = ?, updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(&nome)
    .bind(&descrizione)
    .bind(prezzo)
    .bind(prezzo_originale)
    .bind(servizi_inclusi)
    .bind(validita_giorni)
    .bind(&pacchetto_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update pacchetto: {}", e))?;

    Ok(Pacchetto {
        id: pacchetto_id,
        nome,
        descrizione,
        prezzo,
        prezzo_originale,
        servizi_inclusi,
        validita_giorni,
        attivo: true,
        risparmio: prezzo_originale.map(|orig| orig - prezzo),
    })
}

/// Servizio info for pacchetto composition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PacchettoServizio {
    pub id: String,
    pub pacchetto_id: String,
    pub servizio_id: String,
    pub servizio_nome: String,
    pub servizio_prezzo: f64,
    pub quantita: i32,
}

/// Get servizi linked to a pacchetto
#[tauri::command]
pub async fn get_pacchetto_servizi(
    pool: State<'_, SqlitePool>,
    pacchetto_id: String,
) -> Result<Vec<PacchettoServizio>, String> {
    let rows = sqlx::query_as::<_, (String, String, String, String, f64, i32)>(
        r#"
        SELECT ps.id, ps.pacchetto_id, ps.servizio_id, s.nome, s.prezzo, ps.quantita
        FROM pacchetto_servizi ps
        JOIN servizi s ON s.id = ps.servizio_id
        WHERE ps.pacchetto_id = ?
        ORDER BY s.nome
        "#,
    )
    .bind(&pacchetto_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(rows
        .into_iter()
        .map(|r| PacchettoServizio {
            id: r.0,
            pacchetto_id: r.1,
            servizio_id: r.2,
            servizio_nome: r.3,
            servizio_prezzo: r.4,
            quantita: r.5,
        })
        .collect())
}

/// Add a servizio to a pacchetto
#[tauri::command]
pub async fn add_servizio_to_pacchetto(
    pool: State<'_, SqlitePool>,
    pacchetto_id: String,
    servizio_id: String,
    quantita: Option<i32>,
) -> Result<PacchettoServizio, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let qty = quantita.unwrap_or(1);

    // Get servizio info
    let servizio =
        sqlx::query_as::<_, (String, f64)>("SELECT nome, prezzo FROM servizi WHERE id = ?")
            .bind(&servizio_id)
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| format!("Database error: {}", e))?
            .ok_or_else(|| "Servizio not found".to_string())?;

    // Insert or update (upsert)
    sqlx::query(
        r#"
        INSERT INTO pacchetto_servizi (id, pacchetto_id, servizio_id, quantita)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(pacchetto_id, servizio_id) DO UPDATE SET quantita = quantita + excluded.quantita
        "#,
    )
    .bind(&id)
    .bind(&pacchetto_id)
    .bind(&servizio_id)
    .bind(qty)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to add servizio: {}", e))?;

    // Update servizi_inclusi count in pacchetto
    update_pacchetto_servizi_count(pool.inner(), &pacchetto_id).await?;

    Ok(PacchettoServizio {
        id,
        pacchetto_id,
        servizio_id,
        servizio_nome: servizio.0,
        servizio_prezzo: servizio.1,
        quantita: qty,
    })
}

/// Remove a servizio from a pacchetto
#[tauri::command]
pub async fn remove_servizio_from_pacchetto(
    pool: State<'_, SqlitePool>,
    pacchetto_id: String,
    servizio_id: String,
) -> Result<bool, String> {
    sqlx::query("DELETE FROM pacchetto_servizi WHERE pacchetto_id = ? AND servizio_id = ?")
        .bind(&pacchetto_id)
        .bind(&servizio_id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to remove servizio: {}", e))?;

    // Update servizi_inclusi count in pacchetto
    update_pacchetto_servizi_count(pool.inner(), &pacchetto_id).await?;

    Ok(true)
}

/// Helper: Update servizi_inclusi count based on pacchetto_servizi
async fn update_pacchetto_servizi_count(
    pool: &SqlitePool,
    pacchetto_id: &str,
) -> Result<(), String> {
    let count: (i64,) = sqlx::query_as(
        "SELECT COALESCE(SUM(quantita), 0) FROM pacchetto_servizi WHERE pacchetto_id = ?",
    )
    .bind(pacchetto_id)
    .fetch_one(pool)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    sqlx::query(
        "UPDATE pacchetti SET servizi_inclusi = ?, updated_at = datetime('now') WHERE id = ?",
    )
    .bind(count.0 as i32)
    .bind(pacchetto_id)
    .execute(pool)
    .await
    .map_err(|e| format!("Failed to update count: {}", e))?;

    Ok(())
}

// ═══════════════════════════════════════════════════════════════════
// WhatsApp Marketing - Invio Pacchetti Selettivo
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClienteWhatsAppInfo {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub telefono: String,
    pub is_vip: bool,
    pub loyalty_visits: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvioPacchettoWhatsAppResult {
    pub success: bool,
    pub total_clienti: usize,
    pub messaggi_inviati: usize,
    pub messaggi_falliti: usize,
    pub dettagli: Vec<InvioDettaglio>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvioDettaglio {
    pub cliente_id: String,
    pub nome: String,
    pub telefono: String,
    pub status: String, // "inviato" | "fallito" | "no_telefono" | "no_consenso"
    pub error: Option<String>,
}

/// Get clienti filtrati per invio WhatsApp pacchetti
/// Filtri: "tutti" | "vip" | "vip_3_plus"
#[tauri::command]
pub async fn get_clienti_per_invio_whatsapp(
    pool: State<'_, SqlitePool>,
    filtro: String,
) -> Result<Vec<ClienteWhatsAppInfo>, String> {
    let query = match filtro.as_str() {
        "vip" => {
            r#"
            SELECT id, nome, cognome, telefono, COALESCE(is_vip, 0) as is_vip, 
                   COALESCE(loyalty_visits, 0) as loyalty_visits
            FROM clienti
            WHERE deleted_at IS NULL
              AND consenso_whatsapp = 1
              AND telefono IS NOT NULL
              AND telefono != ''
              AND is_vip = 1
            ORDER BY cognome, nome
            "#
        }
        "vip_3_plus" => {
            r#"
            SELECT id, nome, cognome, telefono, COALESCE(is_vip, 0) as is_vip, 
                   COALESCE(loyalty_visits, 0) as loyalty_visits
            FROM clienti
            WHERE deleted_at IS NULL
              AND consenso_whatsapp = 1
              AND telefono IS NOT NULL
              AND telefono != ''
              AND is_vip = 1
              AND COALESCE(loyalty_visits, 0) >= 3
            ORDER BY cognome, nome
            "#
        }
        _ => {
            // "tutti" - tutti i clienti con consenso WhatsApp
            r#"
            SELECT id, nome, cognome, telefono, COALESCE(is_vip, 0) as is_vip, 
                   COALESCE(loyalty_visits, 0) as loyalty_visits
            FROM clienti
            WHERE deleted_at IS NULL
              AND consenso_whatsapp = 1
              AND telefono IS NOT NULL
              AND telefono != ''
            ORDER BY cognome, nome
            "#
        }
    };

    let rows = sqlx::query_as::<_, (String, String, String, String, i32, i32)>(query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Database error: {}", e))?;

    Ok(rows
        .into_iter()
        .map(|r| ClienteWhatsAppInfo {
            id: r.0,
            nome: r.1,
            cognome: r.2,
            telefono: r.3,
            is_vip: r.4 == 1,
            loyalty_visits: r.5,
        })
        .collect())
}

/// Invia pacchetto via WhatsApp a gruppo di clienti filtrati
#[tauri::command]
pub async fn invia_pacchetto_whatsapp_bulk(
    pool: State<'_, SqlitePool>,
    pacchetto_id: String,
    filtro: String,
    messaggio: String,
) -> Result<InvioPacchettoWhatsAppResult, String> {
    // Get pacchetto info
    let pacchetto = sqlx::query_as::<_, (String, Option<String>, f64, Option<f64>, i32, i32)>(
        "SELECT nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, validita_giorni 
         FROM pacchetti WHERE id = ? AND attivo = 1",
    )
    .bind(&pacchetto_id)
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?
    .ok_or_else(|| "Pacchetto non trovato".to_string())?;

    // Get clienti filtrati
    let clienti = get_clienti_per_invio_whatsapp(pool, filtro).await?;

    let mut dettagli = Vec::new();
    let mut inviati = 0;
    let mut falliti = 0;

    for cliente in &clienti {
        // Personalizza messaggio per ogni cliente
        let messaggio_personalizzato = messaggio
            .replace("{{nome}}", &cliente.nome)
            .replace("{{cognome}}", &cliente.cognome)
            .replace("{{pacchetto}}", &pacchetto.0)
            .replace("{{prezzo}}", &format!("{:.2}", pacchetto.2))
            .replace("{{prezzo_originale}}", &pacchetto.3.map(|p| format!("{:.2}", p)).unwrap_or_default())
            .replace("{{servizi}}", &pacchetto.4.to_string())
            .replace("{{giorni}}", &pacchetto.5.to_string());

        // Simula invio (qui si integrerebbe con il servizio WhatsApp reale)
        // Per ora salva nella coda messaggi
        let result = queue_whatsapp_message_internal(
            &cliente.telefono,
            &messaggio_personalizzato,
            Some("pacchetto_marketing"),
        ).await;

        match result {
            Ok(_) => {
                inviati += 1;
                dettagli.push(InvioDettaglio {
                    cliente_id: cliente.id.clone(),
                    nome: format!("{} {}", cliente.nome, cliente.cognome),
                    telefono: cliente.telefono.clone(),
                    status: "in_coda".to_string(),
                    error: None,
                });
            }
            Err(e) => {
                falliti += 1;
                dettagli.push(InvioDettaglio {
                    cliente_id: cliente.id.clone(),
                    nome: format!("{} {}", cliente.nome, cliente.cognome),
                    telefono: cliente.telefono.clone(),
                    status: "fallito".to_string(),
                    error: Some(e),
                });
            }
        }

        // Rate limiting: max 60 msg/ora = 1 ogni minuto
        // In realtà inviamo subito ma il servizio WhatsApp gestirà il rate limiting
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }

    // Salva report invio nel database
    let _ = sqlx::query(
        r#"
        INSERT INTO whatsapp_invii (id, pacchetto_id, filtro, totale_clienti, inviati, falliti, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        "#,
    )
    .bind(uuid::Uuid::new_v4().to_string())
    .bind(&pacchetto_id)
    .bind(&filtro)
    .bind(clienti.len() as i32)
    .bind(inviati as i32)
    .bind(falliti as i32)
    .execute(pool.inner())
    .await;

    Ok(InvioPacchettoWhatsAppResult {
        success: falliti == 0 || inviati > 0,
        total_clienti: clienti.len(),
        messaggi_inviati: inviati,
        messaggi_falliti: falliti,
        dettagli,
    })
}

/// Helper: Queue WhatsApp message (internal async version)
async fn queue_whatsapp_message_internal(
    phone: &str,
    message: &str,
    template_name: Option<&str>,
) -> Result<String, String> {
    use std::io::Write;
    
    // Create queue directory if not exists
    let queue_dir = std::path::PathBuf::from(".whatsapp-session");
    std::fs::create_dir_all(&queue_dir).map_err(|e| e.to_string())?;
    
    let queue_file = queue_dir.join("message_queue.json");
    
    // Read existing queue
    let mut queue: Vec<serde_json::Value> = if queue_file.exists() {
        let content = std::fs::read_to_string(&queue_file).unwrap_or_default();
        serde_json::from_str(&content).unwrap_or_default()
    } else {
        vec![]
    };
    
    // Add new message
    let msg_id = format!("msg_{}", chrono::Utc::now().timestamp_millis());
    queue.push(serde_json::json!({
        "id": msg_id,
        "phone": phone,
        "message": message,
        "template": template_name,
        "status": "pending",
        "created_at": chrono::Utc::now().to_rfc3339(),
    }));
    
    // Save queue
    let mut file = std::fs::File::create(&queue_file).map_err(|e| e.to_string())?;
    file.write_all(serde_json::to_string_pretty(&queue).unwrap().as_bytes())
        .map_err(|e| e.to_string())?;
    
    Ok(msg_id)
}
