// ═══════════════════════════════════════════════════════════════════
// FLUXION - Clienti Commands
// CRUD operations for clienti table
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::audit::{log_create, log_delete, log_update};
use crate::AppState;

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
pub async fn get_clienti(state: State<'_, AppState>) -> Result<Vec<Cliente>, String> {
    let clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        ORDER BY cognome ASC, nome ASC
        "#,
    )
    .fetch_all(&state.db)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(clienti)
}

/// Get single cliente by ID
#[tauri::command]
pub async fn get_cliente(state: State<'_, AppState>, id: String) -> Result<Cliente, String> {
    let cliente = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&id)
    .fetch_one(&state.db)
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
    state: State<'_, AppState>,
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
    .execute(&state.db)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    // Fetch and return created cliente
    let cliente = get_cliente(state.clone(), id.clone()).await?;

    // Audit logging
    let _ = log_create(&state, None, "cliente", &id, &cliente).await;

    Ok(cliente)
}

/// Update existing cliente
#[tauri::command]
pub async fn update_cliente(
    state: State<'_, AppState>,
    input: UpdateClienteInput,
) -> Result<Cliente, String> {
    // Get cliente before update for audit
    let cliente_before = get_cliente(state.clone(), input.id.clone()).await?;

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
    .execute(&state.db)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    if result.rows_affected() == 0 {
        return Err(format!("Cliente non trovato: {}", input.id));
    }

    // Fetch and return updated cliente
    let cliente_after = get_cliente(state.clone(), input.id.clone()).await?;

    // Audit logging
    let _ = log_update(
        &state,
        None,
        "cliente",
        &input.id,
        &cliente_before,
        &cliente_after,
    )
    .await;

    Ok(cliente_after)
}

/// Delete cliente (soft delete)
#[tauri::command]
pub async fn delete_cliente(state: State<'_, AppState>, id: String) -> Result<(), String> {
    // Get cliente before delete for audit
    let cliente_before = get_cliente(state.clone(), id.clone()).await?;

    let result = sqlx::query(
        r#"
        UPDATE clienti
        SET deleted_at = datetime('now')
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(&id)
    .execute(&state.db)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    if result.rows_affected() == 0 {
        return Err(format!("Cliente non trovato: {}", id));
    }

    // Audit logging
    let _ = log_delete(&state, None, "cliente", &id, &cliente_before).await;

    Ok(())
}

/// Search clienti by nome, cognome, telefono, email
#[tauri::command]
pub async fn search_clienti(
    state: State<'_, AppState>,
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
    .fetch_all(&state.db)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    Ok(clienti)
}
