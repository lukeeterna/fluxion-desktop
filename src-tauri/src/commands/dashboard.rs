// ═══════════════════════════════════════════════════════════════════
// FLUXION - Dashboard Statistics Commands
// Statistiche per la home page
// ═══════════════════════════════════════════════════════════════════

use chrono::Datelike;
use serde::Serialize;
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize)]
pub struct DashboardStats {
    pub appuntamenti_oggi: i32,
    pub appuntamenti_settimana: i32,
    pub clienti_totali: i32,
    pub clienti_vip: i32,
    pub clienti_nuovi_mese: i32,
    pub fatturato_mese: f64,
    pub fatture_da_pagare: i32,
    pub servizio_top_nome: String,
    pub servizio_top_conteggio: i32,
}

#[derive(Debug, Serialize)]
pub struct AppuntamentoOggi {
    pub id: String,
    pub cliente_nome: String,
    pub servizio_nome: String,
    pub ora: String,
    pub stato: String,
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_dashboard_stats(pool: State<'_, SqlitePool>) -> Result<DashboardStats, String> {
    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();
    let inizio_settimana = get_inizio_settimana();
    let inizio_mese = chrono::Local::now().format("%Y-%m-01").to_string();

    // Appuntamenti oggi
    let appuntamenti_oggi: i32 = sqlx::query_scalar(
        r#"SELECT COUNT(*) FROM appuntamenti
           WHERE DATE(data_ora_inizio) = ?
           AND stato NOT IN ('cancellato', 'no_show')
           AND deleted_at IS NULL"#,
    )
    .bind(&oggi)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Appuntamenti settimana
    let appuntamenti_settimana: i32 = sqlx::query_scalar(
        r#"SELECT COUNT(*) FROM appuntamenti
           WHERE DATE(data_ora_inizio) >= ?
           AND stato NOT IN ('cancellato', 'no_show')
           AND deleted_at IS NULL"#,
    )
    .bind(&inizio_settimana)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Clienti totali
    let clienti_totali: i32 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM clienti WHERE deleted_at IS NULL",
    )
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Clienti VIP
    let clienti_vip: i32 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM clienti WHERE is_vip = 1 AND deleted_at IS NULL",
    )
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Clienti nuovi questo mese
    let clienti_nuovi_mese: i32 = sqlx::query_scalar(
        r#"SELECT COUNT(*) FROM clienti
           WHERE DATE(created_at) >= ? AND deleted_at IS NULL"#,
    )
    .bind(&inizio_mese)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Fatturato mese
    let fatturato_mese: f64 = sqlx::query_scalar(
        r#"SELECT COALESCE(SUM(totale_documento), 0) FROM fatture
           WHERE DATE(data_emissione) >= ?
           AND stato IN ('pagata', 'emessa')
           AND deleted_at IS NULL"#,
    )
    .bind(&inizio_mese)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0.0);

    // Fatture da pagare
    let fatture_da_pagare: i32 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM fatture WHERE stato = 'emessa' AND deleted_at IS NULL",
    )
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Servizio top
    let servizio_top = sqlx::query_as::<_, (String, i32)>(
        r#"SELECT s.nome, COUNT(*) as cnt FROM appuntamenti a
           JOIN servizi s ON a.servizio_id = s.id
           WHERE DATE(a.data_ora_inizio) >= ?
           AND a.deleted_at IS NULL
           GROUP BY a.servizio_id
           ORDER BY cnt DESC LIMIT 1"#,
    )
    .bind(&inizio_mese)
    .fetch_optional(pool.inner())
    .await
    .ok()
    .flatten()
    .unwrap_or(("-".to_string(), 0));

    Ok(DashboardStats {
        appuntamenti_oggi,
        appuntamenti_settimana,
        clienti_totali,
        clienti_vip,
        clienti_nuovi_mese,
        fatturato_mese,
        fatture_da_pagare,
        servizio_top_nome: servizio_top.0,
        servizio_top_conteggio: servizio_top.1,
    })
}

#[tauri::command]
pub async fn get_appuntamenti_oggi(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<AppuntamentoOggi>, String> {
    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();

    let result = sqlx::query_as::<_, (String, String, String, String, String)>(
        r#"SELECT
              a.id,
              c.nome || ' ' || c.cognome as cliente_nome,
              s.nome as servizio_nome,
              TIME(a.data_ora_inizio) as ora,
              a.stato
           FROM appuntamenti a
           JOIN clienti c ON a.cliente_id = c.id
           JOIN servizi s ON a.servizio_id = s.id
           WHERE DATE(a.data_ora_inizio) = ?
           AND a.deleted_at IS NULL
           ORDER BY a.data_ora_inizio
           LIMIT 10"#,
    )
    .bind(&oggi)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore caricamento appuntamenti: {}", e))?;

    Ok(result
        .into_iter()
        .map(|(id, cliente_nome, servizio_nome, ora, stato)| AppuntamentoOggi {
            id,
            cliente_nome,
            servizio_nome,
            ora,
            stato,
        })
        .collect())
}

// Helper function
fn get_inizio_settimana() -> String {
    let today = chrono::Local::now().naive_local().date();
    let weekday = today.weekday().num_days_from_monday();
    let monday = today - chrono::Duration::days(weekday as i64);
    monday.format("%Y-%m-%d").to_string()
}
