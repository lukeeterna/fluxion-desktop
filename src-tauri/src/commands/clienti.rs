// ═══════════════════════════════════════════════════════════════════
// FLUXION - Clienti Commands
// CRUD operations for clienti table
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Cliente {
    pub id: String,

    // Anagrafica
    pub nome: String,
    pub cognome: String,
    pub soprannome: Option<String>, // Per identificazione WhatsApp
    pub email: Option<String>,
    pub telefono: String,
    pub data_nascita: Option<String>,

    // Indirizzo
    pub indirizzo: Option<String>,
    pub cap: Option<String>,
    pub citta: Option<String>,
    pub provincia: Option<String>,

    // Fiscale
    pub codice_fiscale: Option<String>,
    pub partita_iva: Option<String>,
    pub codice_sdi: Option<String>,
    pub pec: Option<String>,

    // Metadata
    pub note: Option<String>,
    pub tags: Option<String>,
    pub fonte: Option<String>,

    // GDPR
    pub consenso_marketing: i32,
    pub consenso_whatsapp: i32,
    pub data_consenso: Option<String>,

    // Loyalty (Fase 5)
    pub loyalty_visits: Option<i32>,
    pub loyalty_threshold: Option<i32>,
    pub is_vip: Option<i32>,
    pub referral_source: Option<String>,
    pub referral_cliente_id: Option<String>,

    // Timestamps
    pub created_at: String,
    pub updated_at: String,
    pub deleted_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateClienteInput {
    pub nome: String,
    pub cognome: String,
    pub soprannome: Option<String>,
    pub telefono: String,
    pub email: Option<String>,
    pub data_nascita: Option<String>,
    pub indirizzo: Option<String>,
    pub cap: Option<String>,
    pub citta: Option<String>,
    pub provincia: Option<String>,
    pub codice_fiscale: Option<String>,
    pub partita_iva: Option<String>,
    pub codice_sdi: Option<String>,
    pub pec: Option<String>,
    pub note: Option<String>,
    pub tags: Option<String>,
    pub fonte: Option<String>,
    pub consenso_marketing: Option<i32>,
    pub consenso_whatsapp: Option<i32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateClienteInput {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub soprannome: Option<String>,
    pub telefono: String,
    pub email: Option<String>,
    pub data_nascita: Option<String>,
    pub indirizzo: Option<String>,
    pub cap: Option<String>,
    pub citta: Option<String>,
    pub provincia: Option<String>,
    pub codice_fiscale: Option<String>,
    pub partita_iva: Option<String>,
    pub codice_sdi: Option<String>,
    pub pec: Option<String>,
    pub note: Option<String>,
    pub tags: Option<String>,
    pub fonte: Option<String>,
    pub consenso_marketing: Option<i32>,
    pub consenso_whatsapp: Option<i32>,
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get all clienti (excluding soft-deleted)
#[tauri::command]
pub async fn get_clienti(pool: State<'_, SqlitePool>) -> Result<Vec<Cliente>, String> {
    let clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        ORDER BY cognome ASC, nome ASC
        "#,
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(clienti)
}

/// Get single cliente by ID
#[tauri::command]
pub async fn get_cliente(pool: State<'_, SqlitePool>, id: String) -> Result<Cliente, String> {
    let cliente = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => format!("Cliente non trovato: {}", id),
        _ => format!("Database error: {}", e),
    })?;

    Ok(cliente)
}

/// Create new cliente
#[tauri::command]
pub async fn create_cliente(
    pool: State<'_, SqlitePool>,
    input: CreateClienteInput,
) -> Result<Cliente, String> {
    // Generate UUID for new cliente
    let id = uuid::Uuid::new_v4().to_string();

    // Insert cliente
    sqlx::query(
        r#"
        INSERT INTO clienti (
            id, nome, cognome, soprannome, telefono, email, data_nascita,
            indirizzo, cap, citta, provincia,
            codice_fiscale, partita_iva, codice_sdi, pec,
            note, tags, fonte,
            consenso_marketing, consenso_whatsapp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.nome)
    .bind(&input.cognome)
    .bind(&input.soprannome)
    .bind(&input.telefono)
    .bind(&input.email)
    .bind(&input.data_nascita)
    .bind(&input.indirizzo)
    .bind(&input.cap)
    .bind(&input.citta)
    .bind(&input.provincia)
    .bind(&input.codice_fiscale)
    .bind(&input.partita_iva)
    .bind(&input.codice_sdi)
    .bind(&input.pec)
    .bind(&input.note)
    .bind(&input.tags)
    .bind(&input.fonte)
    .bind(input.consenso_marketing.unwrap_or(0))
    .bind(input.consenso_whatsapp.unwrap_or(0))
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    // Fetch and return created cliente
    get_cliente(pool, id).await
}

/// Update existing cliente
#[tauri::command]
pub async fn update_cliente(
    pool: State<'_, SqlitePool>,
    input: UpdateClienteInput,
) -> Result<Cliente, String> {
    // Update cliente
    let result = sqlx::query(
        r#"
        UPDATE clienti SET
            nome = ?, cognome = ?, soprannome = ?, telefono = ?, email = ?, data_nascita = ?,
            indirizzo = ?, cap = ?, citta = ?, provincia = ?,
            codice_fiscale = ?, partita_iva = ?, codice_sdi = ?, pec = ?,
            note = ?, tags = ?, fonte = ?,
            consenso_marketing = ?, consenso_whatsapp = ?,
            updated_at = datetime('now')
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&input.nome)
    .bind(&input.cognome)
    .bind(&input.soprannome)
    .bind(&input.telefono)
    .bind(&input.email)
    .bind(&input.data_nascita)
    .bind(&input.indirizzo)
    .bind(&input.cap)
    .bind(&input.citta)
    .bind(&input.provincia)
    .bind(&input.codice_fiscale)
    .bind(&input.partita_iva)
    .bind(&input.codice_sdi)
    .bind(&input.pec)
    .bind(&input.note)
    .bind(&input.tags)
    .bind(&input.fonte)
    .bind(input.consenso_marketing.unwrap_or(0))
    .bind(input.consenso_whatsapp.unwrap_or(0))
    .bind(&input.id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    if result.rows_affected() == 0 {
        return Err(format!("Cliente non trovato: {}", input.id));
    }

    // Fetch and return updated cliente
    get_cliente(pool, input.id).await
}

/// Delete cliente (soft delete)
#[tauri::command]
pub async fn delete_cliente(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    let result = sqlx::query(
        r#"
        UPDATE clienti
        SET deleted_at = datetime('now')
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    if result.rows_affected() == 0 {
        return Err(format!("Cliente non trovato: {}", id));
    }

    Ok(())
}

/// Search clienti by nome, cognome, telefono, email
#[tauri::command]
pub async fn search_clienti(
    pool: State<'_, SqlitePool>,
    query: String,
) -> Result<Vec<Cliente>, String> {
    let search_pattern = format!("%{}%", query);

    let clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        AND (
            nome LIKE ? OR
            cognome LIKE ? OR
            telefono LIKE ? OR
            email LIKE ?
        )
        ORDER BY cognome ASC, nome ASC
        LIMIT 50
        "#,
    )
    .bind(&search_pattern)
    .bind(&search_pattern)
    .bind(&search_pattern)
    .bind(&search_pattern)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(clienti)
}
