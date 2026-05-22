// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Commands
// Tauri commands for operatori CRUD operations
//
// S255 — GDPR encryption (Art.32) for `operatori.{nome, cognome, email,
// telefono}`. Wire mirrors `commands/clienti.rs` S249: encrypt on
// INSERT/UPDATE, decrypt post-fetch. KPI views return ciphertext for
// `nome`/`cognome`; the commands decrypt and compose `nome_completo` in
// Rust (migration 039 dropped the SQL concat).
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

use crate::encryption::{decrypt_field, encrypt_field, ensure_encryption_ready_pool};

// ───────────────────────────────────────────────────────────────────
// S255 — Encryption helpers (mirror of commands/clienti.rs)
// ───────────────────────────────────────────────────────────────────

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

/// Decifra in-place i 4 campi sensibili di un Operatore.
/// Idempotent SOLO se i campi sono cifrati: chiamare su plaintext fa fallire.
fn decrypt_operatore_in_place(o: &mut Operatore) -> Result<(), String> {
    o.nome = decrypt_required(&o.nome)?;
    o.cognome = decrypt_required(&o.cognome)?;
    o.email = decrypt_opt(&o.email)?;
    o.telefono = decrypt_opt(&o.telefono)?;
    Ok(())
}

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
    pub genere: Option<String>,
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
    pub genere: Option<String>,
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
    pub genere: Option<String>,
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
    ensure_encryption_ready_pool(pool.inner()).await?;
    // NOTE post-S255: `ORDER BY nome ASC` ora ordina sul ciphertext Base64
    // (binario, non lessicografico sul plaintext). Acceptable per <100 op;
    // tier-2 (S256+): tag plaintext della prima lettera o blind-index HMAC.
    let query = if active_only.unwrap_or(true) {
        "SELECT * FROM operatori WHERE attivo = 1 ORDER BY nome ASC"
    } else {
        "SELECT * FROM operatori ORDER BY nome ASC"
    };

    let mut ops = sqlx::query_as::<_, Operatore>(query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch operatori: {}", e))?;

    for o in ops.iter_mut() {
        decrypt_operatore_in_place(o)
            .map_err(|e| format!("decrypt operatore {} failed: {}", o.id, e))?;
    }
    Ok(ops)
}

/// S274: pool-based core per testability. Tauri wrapper sotto.
pub async fn internal_get_operatore(pool: &SqlitePool, id: &str) -> Result<Operatore, String> {
    ensure_encryption_ready_pool(pool).await?;
    let mut o = sqlx::query_as::<_, Operatore>("SELECT * FROM operatori WHERE id = ?")
        .bind(id)
        .fetch_one(pool)
        .await
        .map_err(|e| format!("Operatore not found: {}", e))?;

    decrypt_operatore_in_place(&mut o)
        .map_err(|e| format!("decrypt operatore {} failed: {}", id, e))?;
    Ok(o)
}

/// Get single operatore by ID
#[tauri::command]
pub async fn get_operatore(pool: State<'_, SqlitePool>, id: String) -> Result<Operatore, String> {
    internal_get_operatore(pool.inner(), &id).await
}

/// S274: pool-based core per testability. Tauri wrapper sotto.
pub async fn internal_create_operatore(
    pool: &SqlitePool,
    input: CreateOperatoreInput,
) -> Result<Operatore, String> {
    ensure_encryption_ready_pool(pool).await?;
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    // S255: encrypt PII at rest (nome/cognome required, email/telefono opt).
    let nome_ct = encrypt_required(&input.nome)?;
    let cognome_ct = encrypt_required(&input.cognome)?;
    let email_ct = encrypt_opt(&input.email)?;
    let telefono_ct = encrypt_opt(&input.telefono)?;

    sqlx::query(
        r#"
        INSERT INTO operatori (
            id, nome, cognome, email, telefono, ruolo, colore, avatar_url, attivo, genere,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&nome_ct)
    .bind(&cognome_ct)
    .bind(&email_ct)
    .bind(&telefono_ct)
    .bind(input.ruolo.unwrap_or_else(|| "operatore".to_string()))
    .bind(input.colore.unwrap_or_else(|| "#C084FC".to_string()))
    .bind(&input.avatar_url)
    .bind(input.attivo.unwrap_or(1))
    .bind(&input.genere)
    .bind(&now)
    .bind(&now)
    .execute(pool)
    .await
    .map_err(|e| format!("Failed to create operatore: {}", e))?;

    internal_get_operatore(pool, &id).await
}

/// Create new operatore
#[tauri::command]
pub async fn create_operatore(
    pool: State<'_, SqlitePool>,
    input: CreateOperatoreInput,
) -> Result<Operatore, String> {
    internal_create_operatore(pool.inner(), input).await
}

/// S274: pool-based core per testability. Tauri wrapper sotto.
pub async fn internal_update_operatore(
    pool: &SqlitePool,
    id: &str,
    input: UpdateOperatoreInput,
) -> Result<Operatore, String> {
    ensure_encryption_ready_pool(pool).await?;
    let now = chrono::Utc::now().to_rfc3339();

    // Fetch current operatore (returns plaintext post-decrypt — see internal_get_operatore).
    let current = internal_get_operatore(pool, id).await?;

    // S255: merge input over current (plaintext), then re-encrypt PII before UPDATE.
    let nome_plain = input.nome.unwrap_or(current.nome);
    let cognome_plain = input.cognome.unwrap_or(current.cognome);
    let email_plain = input.email.or(current.email);
    let telefono_plain = input.telefono.or(current.telefono);

    let nome_ct = encrypt_required(&nome_plain)?;
    let cognome_ct = encrypt_required(&cognome_plain)?;
    let email_ct = encrypt_opt(&email_plain)?;
    let telefono_ct = encrypt_opt(&telefono_plain)?;

    sqlx::query(
        r#"
        UPDATE operatori SET
            nome = ?, cognome = ?, email = ?, telefono = ?, ruolo = ?,
            colore = ?, avatar_url = ?, attivo = ?, genere = ?, updated_at = ?
        WHERE id = ?
        "#,
    )
    .bind(&nome_ct)
    .bind(&cognome_ct)
    .bind(&email_ct)
    .bind(&telefono_ct)
    .bind(input.ruolo.unwrap_or(current.ruolo))
    .bind(input.colore.unwrap_or(current.colore))
    .bind(input.avatar_url.or(current.avatar_url))
    .bind(input.attivo.unwrap_or(current.attivo))
    .bind(input.genere.or(current.genere))
    .bind(&now)
    .bind(id)
    .execute(pool)
    .await
    .map_err(|e| format!("Failed to update operatore: {}", e))?;

    internal_get_operatore(pool, id).await
}

/// Update operatore
#[tauri::command]
pub async fn update_operatore(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateOperatoreInput,
) -> Result<Operatore, String> {
    internal_update_operatore(pool.inner(), &id, input).await
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

    sqlx::query_as::<_, OperatoreAssenza>("SELECT * FROM operatori_assenze WHERE id = ?")
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

// ───────────────────────────────────────────────────────────────────
// Operatori KPI Statistiche (B4)
// ───────────────────────────────────────────────────────────────────

/// Output type esposto al frontend — mantiene `nome_completo` per non rompere
/// `src/hooks/use-operatori-kpi.ts` (campo composto in Rust post-decrypt,
/// vedi migration 039 che ha rimosso il concat SQL).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KpiOperatore {
    pub id: String,
    pub nome_completo: String,
    pub mese: Option<String>,
    pub appuntamenti_completati: i64,
    pub no_show: i64,
    pub clienti_unici: i64,
    pub fatturato_generato: f64,
    pub ticket_medio: Option<f64>,
}

/// Riga raw dalla view post-039 — `nome` e `cognome` separati (Base64
/// ciphertext quando S255 P1.b è applicato).
#[derive(Debug, Clone, sqlx::FromRow)]
struct KpiOperatoreRaw {
    id: String,
    nome: String,
    cognome: String,
    mese: Option<String>,
    appuntamenti_completati: i64,
    no_show: i64,
    clienti_unici: i64,
    fatturato_generato: f64,
    ticket_medio: Option<f64>,
}

/// Decifra nome+cognome e compone `nome_completo` plaintext.
fn kpi_raw_to_public(r: KpiOperatoreRaw) -> Result<KpiOperatore, String> {
    let nome =
        decrypt_required(&r.nome).map_err(|e| format!("decrypt kpi nome id={}: {}", r.id, e))?;
    let cognome = decrypt_required(&r.cognome)
        .map_err(|e| format!("decrypt kpi cognome id={}: {}", r.id, e))?;
    let nome_completo = if nome.is_empty() && cognome.is_empty() {
        String::new()
    } else if cognome.is_empty() {
        nome
    } else if nome.is_empty() {
        cognome
    } else {
        format!("{} {}", nome, cognome)
    };
    Ok(KpiOperatore {
        id: r.id,
        nome_completo,
        mese: r.mese,
        appuntamenti_completati: r.appuntamenti_completati,
        no_show: r.no_show,
        clienti_unici: r.clienti_unici,
        fatturato_generato: r.fatturato_generato,
        ticket_medio: r.ticket_medio,
    })
}

/// Ritorna KPI mensili storici per un operatore (ultimi N mesi con dati, dalla view v_kpi_operatori)
#[tauri::command]
pub async fn get_kpi_operatore_storico(
    pool: State<'_, SqlitePool>,
    operatore_id: String,
    mesi: Option<i64>,
) -> Result<Vec<KpiOperatore>, String> {
    ensure_encryption_ready_pool(pool.inner()).await?;
    let limit = mesi.unwrap_or(12);

    let raws = sqlx::query_as::<_, KpiOperatoreRaw>(
        "SELECT id, nome, cognome, mese, appuntamenti_completati, no_show,
                clienti_unici, fatturato_generato, ticket_medio
         FROM v_kpi_operatori
         WHERE id = ? AND mese IS NOT NULL
         ORDER BY mese DESC
         LIMIT ?",
    )
    .bind(&operatore_id)
    .bind(limit)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Failed to fetch kpi storico: {}", e))?;

    raws.into_iter().map(kpi_raw_to_public).collect()
}

/// Ritorna top 3 operatori per fatturato del mese corrente (usato da Dashboard W1-B)
#[tauri::command]
pub async fn get_top_operatori_mese(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<KpiOperatore>, String> {
    ensure_encryption_ready_pool(pool.inner()).await?;
    let raws = sqlx::query_as::<_, KpiOperatoreRaw>(
        "SELECT id, nome, cognome, mese, appuntamenti_completati, no_show,
                clienti_unici, fatturato_generato, ticket_medio
         FROM v_kpi_operatori
         WHERE mese = strftime('%Y-%m', 'now')
           AND mese IS NOT NULL
         ORDER BY fatturato_generato DESC
         LIMIT 3",
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Failed to fetch top operatori: {}", e))?;

    raws.into_iter().map(kpi_raw_to_public).collect()
}

// ───────────────────────────────────────────────────────────────────
// Operatori Commissioni (B5)
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct OperatoreCommissione {
    pub id: String,
    pub operatore_id: String,
    pub tipo: String,
    pub percentuale: Option<f64>,
    pub importo_fisso: Option<f64>,
    pub soglia_fatturato: Option<f64>,
    pub bonus_importo: Option<f64>,
    pub valida_dal: String,
    pub valida_al: Option<String>,
    pub servizio_id: Option<String>,
    pub note: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateCommissioneInput {
    pub operatore_id: String,
    pub tipo: String,
    pub percentuale: Option<f64>,
    pub importo_fisso: Option<f64>,
    pub soglia_fatturato: Option<f64>,
    pub bonus_importo: Option<f64>,
    pub valida_dal: String,
    pub valida_al: Option<String>,
    pub servizio_id: Option<String>,
    pub note: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateCommissioneInput {
    pub tipo: String,
    pub percentuale: Option<f64>,
    pub importo_fisso: Option<f64>,
    pub soglia_fatturato: Option<f64>,
    pub bonus_importo: Option<f64>,
    pub valida_dal: String,
    pub valida_al: Option<String>,
    pub servizio_id: Option<String>,
    pub note: Option<String>,
}

/// Ritorna tutte le commissioni di un operatore, ordinate per valida_dal DESC
#[tauri::command]
pub async fn get_operatore_commissioni(
    pool: State<'_, SqlitePool>,
    operatore_id: String,
) -> Result<Vec<OperatoreCommissione>, String> {
    sqlx::query_as::<_, OperatoreCommissione>(
        "SELECT * FROM operatori_commissioni WHERE operatore_id = ? ORDER BY valida_dal DESC",
    )
    .bind(operatore_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Failed to fetch commissioni: {}", e))
}

/// Crea una nuova commissione per l'operatore
#[tauri::command]
pub async fn create_operatore_commissione(
    pool: State<'_, SqlitePool>,
    input: CreateCommissioneInput,
) -> Result<OperatoreCommissione, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query(
        r#"
        INSERT INTO operatori_commissioni
            (id, operatore_id, tipo, percentuale, importo_fisso,
             soglia_fatturato, bonus_importo, valida_dal, valida_al,
             servizio_id, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.operatore_id)
    .bind(&input.tipo)
    .bind(input.percentuale)
    .bind(input.importo_fisso)
    .bind(input.soglia_fatturato)
    .bind(input.bonus_importo)
    .bind(&input.valida_dal)
    .bind(&input.valida_al)
    .bind(&input.servizio_id)
    .bind(&input.note)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create commissione: {}", e))?;

    sqlx::query_as::<_, OperatoreCommissione>("SELECT * FROM operatori_commissioni WHERE id = ?")
        .bind(id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch created commissione: {}", e))
}

/// Aggiorna una commissione esistente
#[tauri::command]
pub async fn update_operatore_commissione(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateCommissioneInput,
) -> Result<OperatoreCommissione, String> {
    sqlx::query(
        r#"
        UPDATE operatori_commissioni
        SET tipo = ?, percentuale = ?, importo_fisso = ?,
            soglia_fatturato = ?, bonus_importo = ?,
            valida_dal = ?, valida_al = ?,
            servizio_id = ?, note = ?
        WHERE id = ?
        "#,
    )
    .bind(&input.tipo)
    .bind(input.percentuale)
    .bind(input.importo_fisso)
    .bind(input.soglia_fatturato)
    .bind(input.bonus_importo)
    .bind(&input.valida_dal)
    .bind(&input.valida_al)
    .bind(&input.servizio_id)
    .bind(&input.note)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update commissione: {}", e))?;

    sqlx::query_as::<_, OperatoreCommissione>("SELECT * FROM operatori_commissioni WHERE id = ?")
        .bind(id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch updated commissione: {}", e))
}

/// Elimina una commissione per ID
#[tauri::command]
pub async fn delete_operatore_commissione(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<(), String> {
    sqlx::query("DELETE FROM operatori_commissioni WHERE id = ?")
        .bind(id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete commissione: {}", e))?;

    Ok(())
}
