// ═══════════════════════════════════════════════════════════════════
// FLUXION - Servizi Commands
// Tauri commands for servizi CRUD operations
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Servizio {
    pub id: String,
    pub nome: String,
    pub descrizione: Option<String>,
    pub categoria: Option<String>,
    pub prezzo: f64,
    pub iva_percentuale: f64,
    pub durata_minuti: i64,
    pub buffer_minuti: i64,
    pub colore: String,
    pub icona: Option<String>,
    pub attivo: i64,
    pub ordine: i64,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateServizioInput {
    pub nome: String,
    pub descrizione: Option<String>,
    pub categoria: Option<String>,
    pub prezzo: f64,
    pub iva_percentuale: Option<f64>,
    pub durata_minuti: i64,
    pub buffer_minuti: Option<i64>,
    pub colore: Option<String>,
    pub icona: Option<String>,
    pub attivo: Option<i64>,
    pub ordine: Option<i64>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateServizioInput {
    pub nome: Option<String>,
    pub descrizione: Option<String>,
    pub categoria: Option<String>,
    pub prezzo: Option<f64>,
    pub iva_percentuale: Option<f64>,
    pub durata_minuti: Option<i64>,
    pub buffer_minuti: Option<i64>,
    pub colore: Option<String>,
    pub icona: Option<String>,
    pub attivo: Option<i64>,
    pub ordine: Option<i64>,
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get all active servizi
#[tauri::command]
pub async fn get_servizi(
    pool: State<'_, SqlitePool>,
    active_only: Option<bool>,
) -> Result<Vec<Servizio>, String> {
    let query = if active_only.unwrap_or(true) {
        "SELECT * FROM servizi WHERE attivo = 1 ORDER BY ordine ASC, nome ASC"
    } else {
        "SELECT * FROM servizi ORDER BY ordine ASC, nome ASC"
    };

    sqlx::query_as::<_, Servizio>(query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch servizi: {}", e))
}

/// Get single servizio by ID
#[tauri::command]
pub async fn get_servizio(pool: State<'_, SqlitePool>, id: String) -> Result<Servizio, String> {
    sqlx::query_as::<_, Servizio>("SELECT * FROM servizi WHERE id = ?")
        .bind(id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Servizio not found: {}", e))
}

/// Create new servizio
#[tauri::command]
pub async fn create_servizio(
    pool: State<'_, SqlitePool>,
    input: CreateServizioInput,
) -> Result<Servizio, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query(
        r#"
        INSERT INTO servizi (
            id, nome, descrizione, categoria, prezzo, iva_percentuale,
            durata_minuti, buffer_minuti, colore, icona, attivo, ordine,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.nome)
    .bind(&input.descrizione)
    .bind(&input.categoria)
    .bind(input.prezzo)
    .bind(input.iva_percentuale.unwrap_or(22.0))
    .bind(input.durata_minuti)
    .bind(input.buffer_minuti.unwrap_or(0))
    .bind(input.colore.unwrap_or_else(|| "#22D3EE".to_string()))
    .bind(&input.icona)
    .bind(input.attivo.unwrap_or(1))
    .bind(input.ordine.unwrap_or(0))
    .bind(&now)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create servizio: {}", e))?;

    get_servizio(pool, id).await
}

/// Update servizio
#[tauri::command]
pub async fn update_servizio(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateServizioInput,
) -> Result<Servizio, String> {
    let now = chrono::Utc::now().to_rfc3339();

    // Fetch current servizio
    let current = get_servizio(pool.clone(), id.clone()).await?;

    sqlx::query(
        r#"
        UPDATE servizi SET
            nome = ?, descrizione = ?, categoria = ?, prezzo = ?, iva_percentuale = ?,
            durata_minuti = ?, buffer_minuti = ?, colore = ?, icona = ?,
            attivo = ?, ordine = ?, updated_at = ?
        WHERE id = ?
        "#,
    )
    .bind(input.nome.unwrap_or(current.nome))
    .bind(input.descrizione.or(current.descrizione))
    .bind(input.categoria.or(current.categoria))
    .bind(input.prezzo.unwrap_or(current.prezzo))
    .bind(input.iva_percentuale.unwrap_or(current.iva_percentuale))
    .bind(input.durata_minuti.unwrap_or(current.durata_minuti))
    .bind(input.buffer_minuti.unwrap_or(current.buffer_minuti))
    .bind(input.colore.unwrap_or(current.colore))
    .bind(input.icona.or(current.icona))
    .bind(input.attivo.unwrap_or(current.attivo))
    .bind(input.ordine.unwrap_or(current.ordine))
    .bind(&now)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update servizio: {}", e))?;

    get_servizio(pool, id).await
}

/// Delete servizio (soft delete by setting attivo = 0)
#[tauri::command]
pub async fn delete_servizio(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query("UPDATE servizi SET attivo = 0, updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete servizio: {}", e))?;

    Ok(())
}
