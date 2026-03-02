// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Commands
// Tauri commands for operatori CRUD operations
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Operatore {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub email: Option<String>,
    pub telefono: Option<String>,
    pub ruolo: String,
    pub colore: String,
    pub avatar_url: Option<String>,
    pub attivo: i64,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateOperatoreInput {
    pub nome: String,
    pub cognome: String,
    pub email: Option<String>,
    pub telefono: Option<String>,
    pub ruolo: Option<String>,
    pub colore: Option<String>,
    pub avatar_url: Option<String>,
    pub attivo: Option<i64>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateOperatoreInput {
    pub nome: Option<String>,
    pub cognome: Option<String>,
    pub email: Option<String>,
    pub telefono: Option<String>,
    pub ruolo: Option<String>,
    pub colore: Option<String>,
    pub avatar_url: Option<String>,
    pub attivo: Option<i64>,
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get all active operatori
#[tauri::command]
pub async fn get_operatori(
    pool: State<'_, SqlitePool>,
    active_only: Option<bool>,
) -> Result<Vec<Operatore>, String> {
    let query = if active_only.unwrap_or(true) {
        "SELECT * FROM operatori WHERE attivo = 1 ORDER BY nome ASC"
    } else {
        "SELECT * FROM operatori ORDER BY nome ASC"
    };

    sqlx::query_as::<_, Operatore>(query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch operatori: {}", e))
}

/// Get single operatore by ID
#[tauri::command]
pub async fn get_operatore(pool: State<'_, SqlitePool>, id: String) -> Result<Operatore, String> {
    sqlx::query_as::<_, Operatore>("SELECT * FROM operatori WHERE id = ?")
        .bind(id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Operatore not found: {}", e))
}

/// Create new operatore
#[tauri::command]
pub async fn create_operatore(
    pool: State<'_, SqlitePool>,
    input: CreateOperatoreInput,
) -> Result<Operatore, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query(
        r#"
        INSERT INTO operatori (
            id, nome, cognome, email, telefono, ruolo, colore, avatar_url, attivo,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.nome)
    .bind(&input.cognome)
    .bind(&input.email)
    .bind(&input.telefono)
    .bind(input.ruolo.unwrap_or_else(|| "operatore".to_string()))
    .bind(input.colore.unwrap_or_else(|| "#C084FC".to_string()))
    .bind(&input.avatar_url)
    .bind(input.attivo.unwrap_or(1))
    .bind(&now)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create operatore: {}", e))?;

    get_operatore(pool, id).await
}

/// Update operatore
#[tauri::command]
pub async fn update_operatore(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateOperatoreInput,
) -> Result<Operatore, String> {
    let now = chrono::Utc::now().to_rfc3339();

    // Fetch current operatore
    let current = get_operatore(pool.clone(), id.clone()).await?;

    sqlx::query(
        r#"
        UPDATE operatori SET
            nome = ?, cognome = ?, email = ?, telefono = ?, ruolo = ?,
            colore = ?, avatar_url = ?, attivo = ?, updated_at = ?
        WHERE id = ?
        "#,
    )
    .bind(input.nome.unwrap_or(current.nome))
    .bind(input.cognome.unwrap_or(current.cognome))
    .bind(input.email.or(current.email))
    .bind(input.telefono.or(current.telefono))
    .bind(input.ruolo.unwrap_or(current.ruolo))
    .bind(input.colore.unwrap_or(current.colore))
    .bind(input.avatar_url.or(current.avatar_url))
    .bind(input.attivo.unwrap_or(current.attivo))
    .bind(&now)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update operatore: {}", e))?;

    get_operatore(pool, id).await
}

/// Delete operatore (soft delete by setting attivo = 0)
#[tauri::command]
pub async fn delete_operatore(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query("UPDATE operatori SET attivo = 0, updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete operatore: {}", e))?;

    Ok(())
}

// ───────────────────────────────────────────────────────────────────
// Operatori Servizi (B2)
// ───────────────────────────────────────────────────────────────────

/// Ritorna la lista di servizio_ids abilitati per un operatore
#[tauri::command]
pub async fn get_operatore_servizi(
    pool: State<'_, SqlitePool>,
    operatore_id: String,
) -> Result<Vec<String>, String> {
    let ids = sqlx::query_scalar::<_, String>(
        "SELECT servizio_id FROM operatori_servizi WHERE operatore_id = ? ORDER BY priorita ASC",
    )
    .bind(operatore_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Failed to fetch operatore servizi: {}", e))?;

    Ok(ids)
}

/// Sostituisce atomicamente tutti i servizi dell'operatore
#[tauri::command]
pub async fn update_operatore_servizi(
    pool: State<'_, SqlitePool>,
    operatore_id: String,
    servizio_ids: Vec<String>,
) -> Result<(), String> {
    let mut tx = pool
        .inner()
        .begin()
        .await
        .map_err(|e| format!("Transaction error: {}", e))?;

    sqlx::query("DELETE FROM operatori_servizi WHERE operatore_id = ?")
        .bind(&operatore_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| format!("Failed to clear operatore servizi: {}", e))?;

    for (i, servizio_id) in servizio_ids.iter().enumerate() {
        sqlx::query(
            "INSERT INTO operatori_servizi (operatore_id, servizio_id, priorita) VALUES (?, ?, ?)",
        )
        .bind(&operatore_id)
        .bind(servizio_id)
        .bind(i as i64)
        .execute(&mut *tx)
        .await
        .map_err(|e| format!("Failed to insert servizio {}: {}", servizio_id, e))?;
    }

    tx.commit()
        .await
        .map_err(|e| format!("Transaction commit error: {}", e))?;

    Ok(())
}

// ───────────────────────────────────────────────────────────────────
// Operatori Assenze (B2 — ferie, malattia, infortuni)
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct OperatoreAssenza {
    pub id: String,
    pub operatore_id: String,
    pub data_inizio: String,
    pub data_fine: String,
    pub tipo: String,
    pub note: Option<String>,
    pub approvata: i64,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateAssenzaInput {
    pub operatore_id: String,
    pub data_inizio: String,
    pub data_fine: String,
    pub tipo: String,
    pub note: Option<String>,
}

/// Ritorna tutte le assenze di un operatore, ordinate per data_inizio DESC
#[tauri::command]
pub async fn get_operatore_assenze(
    pool: State<'_, SqlitePool>,
    operatore_id: String,
) -> Result<Vec<OperatoreAssenza>, String> {
    sqlx::query_as::<_, OperatoreAssenza>(
        "SELECT * FROM operatori_assenze WHERE operatore_id = ? ORDER BY data_inizio DESC",
    )
    .bind(operatore_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Failed to fetch assenze: {}", e))
}

/// Crea una nuova assenza per l'operatore
#[tauri::command]
pub async fn create_operatore_assenza(
    pool: State<'_, SqlitePool>,
    input: CreateAssenzaInput,
) -> Result<OperatoreAssenza, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query(
        r#"
        INSERT INTO operatori_assenze
            (id, operatore_id, data_inizio, data_fine, tipo, note, approvata, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.operatore_id)
    .bind(&input.data_inizio)
    .bind(&input.data_fine)
    .bind(&input.tipo)
    .bind(&input.note)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create assenza: {}", e))?;

    sqlx::query_as::<_, OperatoreAssenza>(
        "SELECT * FROM operatori_assenze WHERE id = ?",
    )
    .bind(id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Failed to fetch created assenza: {}", e))
}

/// Elimina un'assenza per ID
#[tauri::command]
pub async fn delete_operatore_assenza(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<(), String> {
    sqlx::query("DELETE FROM operatori_assenze WHERE id = ?")
        .bind(id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete assenza: {}", e))?;

    Ok(())
}
