// ═══════════════════════════════════════════════════════════════════
// FLUXION - Clienti Commands
// CRUD operations for clienti table
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

use crate::commands::audit::{log_create, log_delete, log_update};
use crate::encryption::{
    decrypt_field, encrypt_field, ensure_encryption_ready, ensure_encryption_ready_pool,
};
use crate::AppState;

// ───────────────────────────────────────────────────────────────────
// S249 — Encryption helpers (GDPR Art.32)
// ───────────────────────────────────────────────────────────────────
//
// SENSITIVE_FIELDS (11) — cifrati at rest:
//   nome, cognome, telefono, email, codice_fiscale, partita_iva,
//   indirizzo, cap, citta, pec, data_nascita
//
// PLAINTEXT (business / low-entropy / large-text):
//   id, soprannome (alias pubblico WhatsApp), provincia (2 lettere),
//   codice_sdi (B2B identifier), note (free-text, FIXME S250),
//   tags, fonte, consenso_*, loyalty_*, *_at, deleted_at
//
// NOTE search_clienti: tier-1 in-memory filter post-decrypt (OK fino ~10k
// clienti per piccola PMI). Tier-2 (S251+): blind-index HMAC del campo.
//

/// Cifra un Option<String>. None/"" → pass-through.
fn encrypt_opt(v: &Option<String>) -> Result<Option<String>, String> {
    match v {
        Some(s) if !s.is_empty() => Ok(Some(encrypt_field(s)?)),
        _ => Ok(v.clone()),
    }
}

/// Cifra un campo required. "" → pass-through (mai cifrare empty).
fn encrypt_required(v: &str) -> Result<String, String> {
    if v.is_empty() {
        Ok(String::new())
    } else {
        encrypt_field(v)
    }
}

/// Decifra un Option<String>. None/"" → pass-through.
fn decrypt_opt(v: &Option<String>) -> Result<Option<String>, String> {
    match v {
        Some(s) if !s.is_empty() => Ok(Some(decrypt_field(s)?)),
        _ => Ok(v.clone()),
    }
}

/// Decifra un required field. "" → pass-through.
fn decrypt_required(v: &str) -> Result<String, String> {
    if v.is_empty() {
        Ok(String::new())
    } else {
        decrypt_field(v)
    }
}

/// Decifra in-place gli 11 campi sensibili di un Cliente.
/// Idempotent SOLO se i campi sono cifrati: chiamare due volte su plaintext
/// fa fallire la seconda chiamata (decrypt_field rejects non-Base64).
fn decrypt_cliente_in_place(c: &mut Cliente) -> Result<(), String> {
    c.nome = decrypt_required(&c.nome)?;
    c.cognome = decrypt_required(&c.cognome)?;
    c.telefono = decrypt_required(&c.telefono)?;
    c.email = decrypt_opt(&c.email)?;
    c.data_nascita = decrypt_opt(&c.data_nascita)?;
    c.indirizzo = decrypt_opt(&c.indirizzo)?;
    c.cap = decrypt_opt(&c.cap)?;
    c.citta = decrypt_opt(&c.citta)?;
    c.codice_fiscale = decrypt_opt(&c.codice_fiscale)?;
    c.partita_iva = decrypt_opt(&c.partita_iva)?;
    c.pec = decrypt_opt(&c.pec)?;
    Ok(())
}

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
    ensure_encryption_ready(&state).await?;

    let mut clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        ORDER BY cognome ASC, nome ASC
        "#,
    )
    .fetch_all(&state.db)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    // S249 — decrypt the 11 sensitive fields in-place before returning.
    // NOTE: sort order applied SQL-side è quindi sull'ordine cifrato (Base64),
    // non sul cognome plaintext. Trade-off accettato per piccole PMI fino ~10k
    // clienti; frontend può riordinare client-side se serve. Tier-2 (S251):
    // sort_key colonna plaintext-lowercase per ordinamento natura italiana.
    for c in clienti.iter_mut() {
        decrypt_cliente_in_place(c)?;
    }

    // Riordina post-decryption per cognome/nome plaintext naturale.
    clienti.sort_by(|a, b| {
        a.cognome
            .to_lowercase()
            .cmp(&b.cognome.to_lowercase())
            .then_with(|| a.nome.to_lowercase().cmp(&b.nome.to_lowercase()))
    });

    Ok(clienti)
}

/// S273: pool-based core per testability. Tauri wrapper sotto.
pub async fn internal_get_cliente(pool: &SqlitePool, id: &str) -> Result<Cliente, String> {
    ensure_encryption_ready_pool(pool).await?;

    let mut cliente = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(id)
    .fetch_one(pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => format!("Cliente non trovato: {}", id),
        _ => format!("Database error: {}", e),
    })?;

    decrypt_cliente_in_place(&mut cliente)?;

    Ok(cliente)
}

/// Get single cliente by ID
#[tauri::command]
pub async fn get_cliente(state: State<'_, AppState>, id: String) -> Result<Cliente, String> {
    internal_get_cliente(&state.db, &id).await
}

/// S273: pool-based core per testability. Tauri wrapper sotto.
/// NO audit logging here (audit needs AppState — done by Tauri wrapper).
pub async fn internal_create_cliente(
    pool: &SqlitePool,
    input: CreateClienteInput,
) -> Result<Cliente, String> {
    ensure_encryption_ready_pool(pool).await?;

    // Generate UUID for new cliente
    let id = uuid::Uuid::new_v4().to_string();

    // S249 — encrypt the 11 sensitive fields before INSERT.
    let nome_enc = encrypt_required(&input.nome)?;
    let cognome_enc = encrypt_required(&input.cognome)?;
    let telefono_enc = encrypt_required(&input.telefono)?;
    let email_enc = encrypt_opt(&input.email)?;
    let data_nascita_enc = encrypt_opt(&input.data_nascita)?;
    let indirizzo_enc = encrypt_opt(&input.indirizzo)?;
    let cap_enc = encrypt_opt(&input.cap)?;
    let citta_enc = encrypt_opt(&input.citta)?;
    let codice_fiscale_enc = encrypt_opt(&input.codice_fiscale)?;
    let partita_iva_enc = encrypt_opt(&input.partita_iva)?;
    let pec_enc = encrypt_opt(&input.pec)?;

    // Insert cliente (sensitive fields cifrati, plaintext per: soprannome,
    // provincia, codice_sdi, note, tags, fonte, consenso_*).
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
    .bind(&nome_enc)
    .bind(&cognome_enc)
    .bind(&input.soprannome)
    .bind(&telefono_enc)
    .bind(&email_enc)
    .bind(&data_nascita_enc)
    .bind(&indirizzo_enc)
    .bind(&cap_enc)
    .bind(&citta_enc)
    .bind(&input.provincia)
    .bind(&codice_fiscale_enc)
    .bind(&partita_iva_enc)
    .bind(&input.codice_sdi)
    .bind(&pec_enc)
    .bind(&input.note)
    .bind(&input.tags)
    .bind(&input.fonte)
    .bind(input.consenso_marketing.unwrap_or(0))
    .bind(input.consenso_whatsapp.unwrap_or(0))
    .execute(pool)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    // Fetch and return created cliente (auto-decrypted)
    internal_get_cliente(pool, &id).await
}

/// Create new cliente
#[tauri::command]
pub async fn create_cliente(
    state: State<'_, AppState>,
    input: CreateClienteInput,
) -> Result<Cliente, String> {
    let cliente = internal_create_cliente(&state.db, input).await?;

    // Audit logging (cliente è già plaintext post-decryption)
    let _ = log_create(&state, None, "cliente", &cliente.id, &cliente).await;

    Ok(cliente)
}

/// S273: pool-based core per testability. Tauri wrapper sotto.
/// Returns `(cliente_before, cliente_after)` so the wrapper can run audit logging.
pub async fn internal_update_cliente(
    pool: &SqlitePool,
    input: UpdateClienteInput,
) -> Result<(Cliente, Cliente), String> {
    ensure_encryption_ready_pool(pool).await?;

    // Get cliente before update for audit (già plaintext post-decryption)
    let cliente_before = internal_get_cliente(pool, &input.id).await?;

    // S249 — encrypt the 11 sensitive fields before UPDATE.
    let nome_enc = encrypt_required(&input.nome)?;
    let cognome_enc = encrypt_required(&input.cognome)?;
    let telefono_enc = encrypt_required(&input.telefono)?;
    let email_enc = encrypt_opt(&input.email)?;
    let data_nascita_enc = encrypt_opt(&input.data_nascita)?;
    let indirizzo_enc = encrypt_opt(&input.indirizzo)?;
    let cap_enc = encrypt_opt(&input.cap)?;
    let citta_enc = encrypt_opt(&input.citta)?;
    let codice_fiscale_enc = encrypt_opt(&input.codice_fiscale)?;
    let partita_iva_enc = encrypt_opt(&input.partita_iva)?;
    let pec_enc = encrypt_opt(&input.pec)?;

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
    .bind(&nome_enc)
    .bind(&cognome_enc)
    .bind(&input.soprannome)
    .bind(&telefono_enc)
    .bind(&email_enc)
    .bind(&data_nascita_enc)
    .bind(&indirizzo_enc)
    .bind(&cap_enc)
    .bind(&citta_enc)
    .bind(&input.provincia)
    .bind(&codice_fiscale_enc)
    .bind(&partita_iva_enc)
    .bind(&input.codice_sdi)
    .bind(&pec_enc)
    .bind(&input.note)
    .bind(&input.tags)
    .bind(&input.fonte)
    .bind(input.consenso_marketing.unwrap_or(0))
    .bind(input.consenso_whatsapp.unwrap_or(0))
    .bind(&input.id)
    .execute(pool)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    if result.rows_affected() == 0 {
        return Err(format!("Cliente non trovato: {}", input.id));
    }

    // Fetch updated cliente
    let cliente_after = internal_get_cliente(pool, &input.id).await?;

    Ok((cliente_before, cliente_after))
}

/// Update existing cliente
#[tauri::command]
pub async fn update_cliente(
    state: State<'_, AppState>,
    input: UpdateClienteInput,
) -> Result<Cliente, String> {
    let id_for_audit = input.id.clone();
    let (cliente_before, cliente_after) = internal_update_cliente(&state.db, input).await?;

    // Audit logging
    let _ = log_update(
        &state,
        None,
        "cliente",
        &id_for_audit,
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
    let cliente_before = internal_get_cliente(&state.db, &id).await?;

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

/// GDPR Art.17 — Hard delete cliente and all related data permanently.
/// Cascades to: appuntamenti, schede, incassi, waitlist, pacchetti, media.
/// Creates audit log entry before deletion. Irreversible.
#[tauri::command]
pub async fn gdpr_hard_delete_cliente(
    state: State<'_, AppState>,
    id: String,
) -> Result<String, String> {
    // 1. Verify cliente exists (include soft-deleted)
    // NOTE: lettura raw (cifrata). Per audit log post-S249 si potrebbe
    // chiamare `decrypt_cliente_in_place` se serve plaintext nel log
    // gdpr_requests; per ora basta la presenza row.
    let _cliente = sqlx::query_as::<_, Cliente>("SELECT * FROM clienti WHERE id = ?")
        .bind(&id)
        .fetch_optional(&state.db)
        .await
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| format!("Cliente non trovato: {}", id))?;

    // 2. Enable foreign keys for CASCADE
    sqlx::query("PRAGMA foreign_keys = ON")
        .execute(&state.db)
        .await
        .map_err(|e| format!("PRAGMA error: {}", e))?;

    // 3. Log GDPR deletion request in audit
    let _ = sqlx::query(
        r#"INSERT INTO gdpr_requests (id, tipo, cliente_id, stato, dettagli, created_at)
           VALUES (lower(hex(randomblob(16))), 'cancellazione', ?, 'completata',
                   'Hard delete GDPR Art.17 — tutti i dati personali eliminati', datetime('now'))"#,
    )
    .bind(&id)
    .execute(&state.db)
    .await;

    // 4. Hard delete — CASCADE removes related records
    let result = sqlx::query("DELETE FROM clienti WHERE id = ?")
        .bind(&id)
        .execute(&state.db)
        .await
        .map_err(|e| format!("Hard delete failed: {}", e))?;

    if result.rows_affected() == 0 {
        return Err("Cancellazione fallita: nessuna riga eliminata".to_string());
    }

    Ok(format!(
        "Cliente {} eliminato permanentemente (GDPR Art.17). Tutti i dati correlati rimossi.",
        id
    ))
}

/// S273: pool-based core per testability. Tauri wrapper sotto.
///
/// S249 — tier-1 in-memory post-decryption filter. SQL LIKE su campi cifrati
/// non matcha (Base64 ciphertext non contiene il plaintext). Mitigation:
/// SELECT * → decrypt → filter in Rust. Performance OK fino ~10k clienti
/// per piccola PMI target.
pub async fn internal_search_clienti(
    pool: &SqlitePool,
    query: &str,
) -> Result<Vec<Cliente>, String> {
    ensure_encryption_ready_pool(pool).await?;

    let mut clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        "#,
    )
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Database error: {}", e))?;

    // Decifra in-place tutti i clienti pre-filtraggio.
    for c in clienti.iter_mut() {
        decrypt_cliente_in_place(c)?;
    }

    let needle = query.to_lowercase();
    let mut filtered: Vec<Cliente> = clienti
        .into_iter()
        .filter(|c| {
            c.nome.to_lowercase().contains(&needle)
                || c.cognome.to_lowercase().contains(&needle)
                || c.telefono.to_lowercase().contains(&needle)
                || c.email
                    .as_deref()
                    .map(|e| e.to_lowercase().contains(&needle))
                    .unwrap_or(false)
        })
        .collect();

    // Ordina su plaintext naturale e limita.
    filtered.sort_by(|a, b| {
        a.cognome
            .to_lowercase()
            .cmp(&b.cognome.to_lowercase())
            .then_with(|| a.nome.to_lowercase().cmp(&b.nome.to_lowercase()))
    });
    filtered.truncate(50);

    Ok(filtered)
}

/// Search clienti by nome, cognome, telefono, email.
///
/// FIXME(S251): blind-index colonne separate (HMAC del campo lowercase trimmed)
/// per scalabilità >10k clienti senza sacrificare GDPR Art.32.
#[tauri::command]
pub async fn search_clienti(
    state: State<'_, AppState>,
    query: String,
) -> Result<Vec<Cliente>, String> {
    internal_search_clienti(&state.db, &query).await
}
