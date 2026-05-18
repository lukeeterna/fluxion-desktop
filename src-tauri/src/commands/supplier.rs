// ═══════════════════════════════════════════════════════════════════
// FLUXION - Supplier Management Commands
// CRUD operations for suppliers and supplier orders
//
// S257 — GDPR encryption (Art.32) for `suppliers.{nome, email, telefono,
// indirizzo, partita_iva}`. Mirrors S249 (clienti) / S255 (operatori):
// encrypt on INSERT/UPDATE, decrypt post-fetch. Migration 040 dropped
// `UNIQUE(nome)` and `UNIQUE(partita_iva)` (encryption breaks SQL-level
// UNIQUE because nonce-randomized ciphertexts diverge for the same
// plaintext); dedupe enforcement moved here in `create_supplier`.
// `search_suppliers` switched to tier-1 in-memory filter (acceptable for
// <500 supplier; tier-2 blind-index HMAC tracked for later).
// ═══════════════════════════════════════════════════════════════════

use chrono::Utc;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;
use uuid::Uuid;

use crate::encryption::{decrypt_field, encrypt_field, ensure_encryption_ready_pool};

// ───────────────────────────────────────────────────────────────────
// S257 — Encryption helpers (mirror of commands/operatori.rs)
// ───────────────────────────────────────────────────────────────────

/// Encrypt an Option<String>. None/"" → pass-through.
fn encrypt_opt(v: &Option<String>) -> Result<Option<String>, String> {
    match v {
        Some(s) if !s.is_empty() => Ok(Some(encrypt_field(s)?)),
        _ => Ok(v.clone()),
    }
}

/// Encrypt a required field. "" → pass-through (never encrypt empty).
fn encrypt_required(v: &str) -> Result<String, String> {
    if v.is_empty() {
        Ok(String::new())
    } else {
        encrypt_field(v)
    }
}

/// Decrypt an Option<String>. None/"" → pass-through.
fn decrypt_opt(v: &Option<String>) -> Result<Option<String>, String> {
    match v {
        Some(s) if !s.is_empty() => Ok(Some(decrypt_field(s)?)),
        _ => Ok(v.clone()),
    }
}

/// Decrypt a required field. "" → pass-through.
fn decrypt_required(v: &str) -> Result<String, String> {
    if v.is_empty() {
        Ok(String::new())
    } else {
        decrypt_field(v)
    }
}

/// Decrypt in-place the 5 sensitive fields of a Supplier.
/// Idempotent ONLY on ciphertext: calling on plaintext fails (caller chooses
/// best-effort tolerance — see `maybe_decrypt_supplier_in_place`).
fn decrypt_supplier_in_place(s: &mut Supplier) -> Result<(), String> {
    s.nome = decrypt_required(&s.nome)?;
    s.email = decrypt_opt(&s.email)?;
    s.telefono = decrypt_opt(&s.telefono)?;
    s.indirizzo = decrypt_opt(&s.indirizzo)?;
    s.partita_iva = decrypt_opt(&s.partita_iva)?;
    Ok(())
}

// ═══════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct Supplier {
    pub id: String,
    pub nome: String,
    pub email: Option<String>,
    pub telefono: Option<String>,
    pub indirizzo: Option<String>,
    pub citta: Option<String>,
    pub cap: Option<String>,
    pub partita_iva: Option<String>,
    pub status: String,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct SupplierOrder {
    pub id: String,
    pub supplier_id: String,
    pub ordine_numero: String,
    pub data_ordine: String,
    pub data_consegna_prevista: String,
    pub importo_totale: f64,
    pub status: String,
    pub items: String,
    pub notes: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct SupplierInteraction {
    pub id: String,
    pub supplier_id: String,
    pub order_id: Option<String>,
    pub tipo: String,
    pub messaggio: Option<String>,
    pub status: String,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateSupplierRequest {
    pub nome: String,
    pub email: Option<String>,
    pub telefono: Option<String>,
    pub indirizzo: Option<String>,
    pub citta: Option<String>,
    pub cap: Option<String>,
    pub partita_iva: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateSupplierRequest {
    pub nome: Option<String>,
    pub email: Option<String>,
    pub telefono: Option<String>,
    pub indirizzo: Option<String>,
    pub citta: Option<String>,
    pub cap: Option<String>,
    pub partita_iva: Option<String>,
    pub status: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateOrderRequest {
    pub supplier_id: String,
    pub ordine_numero: String,
    pub data_consegna_prevista: Option<String>,
    pub items: String, // JSON string from frontend
    pub importo_totale: f64,
    pub notes: Option<String>,
}

// ═══════════════════════════════════════════════════════════════════
// SUPPLIERS CRUD
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn create_supplier(
    pool: State<'_, SqlitePool>,
    supplier: CreateSupplierRequest,
) -> Result<Supplier, String> {
    ensure_encryption_ready_pool(pool.inner()).await?;

    // S257: pre-INSERT dedupe replaces the dropped UNIQUE(nome)/UNIQUE(partita_iva)
    // SQL constraints (migration 040). Acceptable cost for <500 suppliers;
    // tier-2 (blind-index HMAC) tracked for scale beyond that.
    let existing = list_suppliers(pool.clone(), Some(true)).await?;
    let nome_norm = supplier.nome.trim().to_lowercase();
    let piva_norm = supplier
        .partita_iva
        .as_ref()
        .map(|p| p.trim().to_lowercase())
        .filter(|p| !p.is_empty());
    for e in &existing {
        if e.nome.trim().to_lowercase() == nome_norm {
            return Err(format!(
                "Esiste già un fornitore con nome '{}'",
                supplier.nome
            ));
        }
        if let (Some(p_new), Some(p_old)) = (
            piva_norm.as_ref(),
            e.partita_iva.as_ref().map(|p| p.trim().to_lowercase()),
        ) {
            if !p_old.is_empty() && p_old == *p_new {
                return Err(format!(
                    "Esiste già un fornitore con partita IVA '{}'",
                    supplier.partita_iva.as_deref().unwrap_or("")
                ));
            }
        }
    }

    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();

    // S257: encrypt PII at rest (nome required; email/telefono/indirizzo/p.iva opt).
    let nome_ct = encrypt_required(&supplier.nome)?;
    let email_ct = encrypt_opt(&supplier.email)?;
    let telefono_ct = encrypt_opt(&supplier.telefono)?;
    let indirizzo_ct = encrypt_opt(&supplier.indirizzo)?;
    let partita_iva_ct = encrypt_opt(&supplier.partita_iva)?;

    sqlx::query(
        "INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(&nome_ct)
    .bind(&email_ct)
    .bind(&telefono_ct)
    .bind(&indirizzo_ct)
    .bind(&supplier.citta)
    .bind(&supplier.cap)
    .bind(&partita_iva_ct)
    .bind("active")
    .bind(&now)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Insert failed: {}", e))?;

    Ok(Supplier {
        id,
        nome: supplier.nome,
        email: supplier.email,
        telefono: supplier.telefono,
        indirizzo: supplier.indirizzo,
        citta: supplier.citta,
        cap: supplier.cap,
        partita_iva: supplier.partita_iva,
        status: "active".to_string(),
        created_at: now.clone(),
        updated_at: now,
    })
}

#[tauri::command]
pub async fn get_supplier(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
) -> Result<Supplier, String> {
    ensure_encryption_ready_pool(pool.inner()).await?;
    let mut s = sqlx::query_as::<_, Supplier>(
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers WHERE id = ?",
    )
    .bind(&supplier_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Supplier not found: {}", e))?;

    decrypt_supplier_in_place(&mut s)
        .map_err(|e| format!("decrypt supplier {} failed: {}", supplier_id, e))?;
    Ok(s)
}

#[tauri::command]
pub async fn list_suppliers(
    pool: State<'_, SqlitePool>,
    include_inactive: Option<bool>,
) -> Result<Vec<Supplier>, String> {
    ensure_encryption_ready_pool(pool.inner()).await?;
    // NOTE post-S257: `ORDER BY nome` now orders on the Base64 ciphertext.
    // Acceptable for <500 suppliers; the consumers re-sort post-decrypt if
    // a stable lexicographic order on plaintext is needed. Tier-2 (blind-index
    // or per-row sort key on first letter) tracked for scale.
    let query = if include_inactive.unwrap_or(false) {
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers ORDER BY nome"
    } else {
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers WHERE status = 'active' ORDER BY nome"
    };

    let mut suppliers = sqlx::query_as::<_, Supplier>(query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Query failed: {}", e))?;

    for s in suppliers.iter_mut() {
        decrypt_supplier_in_place(s)
            .map_err(|e| format!("decrypt supplier {} failed: {}", s.id, e))?;
    }
    // Re-sort post-decrypt for stable plaintext-alphabetical order.
    suppliers.sort_by(|a, b| a.nome.to_lowercase().cmp(&b.nome.to_lowercase()));
    Ok(suppliers)
}

#[tauri::command]
pub async fn update_supplier(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
    update: UpdateSupplierRequest,
) -> Result<Supplier, String> {
    ensure_encryption_ready_pool(pool.inner()).await?;
    let now = Utc::now().to_rfc3339();

    // Fetch current (plaintext post-decrypt via get_supplier).
    let current = get_supplier(pool.clone(), supplier_id.clone()).await?;

    // Merge input over current (plaintext).
    let nome_plain = update.nome.unwrap_or(current.nome);
    let email_plain = update.email.or(current.email);
    let telefono_plain = update.telefono.or(current.telefono);
    let indirizzo_plain = update.indirizzo.or(current.indirizzo);
    let citta = update.citta.or(current.citta);
    let cap = update.cap.or(current.cap);
    let partita_iva_plain = update.partita_iva.or(current.partita_iva);
    let status = update.status.unwrap_or(current.status);

    // S257: re-encrypt PII before UPDATE.
    let nome_ct = encrypt_required(&nome_plain)?;
    let email_ct = encrypt_opt(&email_plain)?;
    let telefono_ct = encrypt_opt(&telefono_plain)?;
    let indirizzo_ct = encrypt_opt(&indirizzo_plain)?;
    let partita_iva_ct = encrypt_opt(&partita_iva_plain)?;

    sqlx::query(
        "UPDATE suppliers SET nome=?, email=?, telefono=?, indirizzo=?, citta=?, cap=?, partita_iva=?, status=?, updated_at=?
         WHERE id=?",
    )
    .bind(&nome_ct)
    .bind(&email_ct)
    .bind(&telefono_ct)
    .bind(&indirizzo_ct)
    .bind(&citta)
    .bind(&cap)
    .bind(&partita_iva_ct)
    .bind(&status)
    .bind(&now)
    .bind(&supplier_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Update failed: {}", e))?;

    Ok(Supplier {
        id: supplier_id,
        nome: nome_plain,
        email: email_plain,
        telefono: telefono_plain,
        indirizzo: indirizzo_plain,
        citta,
        cap,
        partita_iva: partita_iva_plain,
        status,
        created_at: current.created_at,
        updated_at: now,
    })
}

#[tauri::command]
pub async fn delete_supplier(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
) -> Result<bool, String> {
    let now = Utc::now().to_rfc3339();

    // Soft delete - mark as inactive
    sqlx::query("UPDATE suppliers SET status = 'inactive', updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&supplier_id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Delete failed: {}", e))?;

    Ok(true)
}

#[tauri::command]
pub async fn search_suppliers(
    pool: State<'_, SqlitePool>,
    query: String,
) -> Result<Vec<Supplier>, String> {
    // S257: SQL `LIKE` on ciphertext yields zero matches. Tier-1 strategy =
    // decrypt the full active set and filter in Rust. Acceptable cost for
    // <500 suppliers; tier-2 (blind-index HMAC per searchable column) is
    // tracked for scale. The 20-row cap is preserved.
    ensure_encryption_ready_pool(pool.inner()).await?;
    let needle = query.trim().to_lowercase();

    let all = list_suppliers(pool, Some(false)).await?;
    if needle.is_empty() {
        return Ok(all.into_iter().take(20).collect());
    }

    let matches: Vec<Supplier> = all
        .into_iter()
        .filter(|s| {
            s.nome.to_lowercase().contains(&needle)
                || s.email
                    .as_deref()
                    .map(|v| v.to_lowercase().contains(&needle))
                    .unwrap_or(false)
                || s.telefono
                    .as_deref()
                    .map(|v| v.to_lowercase().contains(&needle))
                    .unwrap_or(false)
                || s.partita_iva
                    .as_deref()
                    .map(|v| v.to_lowercase().contains(&needle))
                    .unwrap_or(false)
        })
        .take(20)
        .collect();

    Ok(matches)
}

// ═══════════════════════════════════════════════════════════════════
// SUPPLIER ORDERS CRUD
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn create_supplier_order(
    pool: State<'_, SqlitePool>,
    order: CreateOrderRequest,
) -> Result<SupplierOrder, String> {
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();
    let data_consegna = order.data_consegna_prevista.unwrap_or_else(|| now.clone());

    sqlx::query(
        "INSERT INTO supplier_orders (id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(&order.supplier_id)
    .bind(&order.ordine_numero)
    .bind(&now)
    .bind(&data_consegna)
    .bind(order.importo_totale)
    .bind("draft")
    .bind(&order.items)
    .bind(&order.notes)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Insert failed: {}", e))?;

    Ok(SupplierOrder {
        id,
        supplier_id: order.supplier_id,
        ordine_numero: order.ordine_numero,
        data_ordine: now.clone(),
        data_consegna_prevista: data_consegna,
        importo_totale: order.importo_totale,
        status: "draft".to_string(),
        items: order.items,
        notes: order.notes,
        created_at: now,
    })
}

#[tauri::command]
pub async fn get_supplier_order(
    pool: State<'_, SqlitePool>,
    order_id: String,
) -> Result<SupplierOrder, String> {
    sqlx::query_as::<_, SupplierOrder>(
        "SELECT id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at
         FROM supplier_orders WHERE id = ?",
    )
    .bind(&order_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Order not found: {}", e))
}

#[tauri::command]
pub async fn get_supplier_orders(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
) -> Result<Vec<SupplierOrder>, String> {
    sqlx::query_as::<_, SupplierOrder>(
        "SELECT id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at
         FROM supplier_orders WHERE supplier_id = ? ORDER BY data_ordine DESC",
    )
    .bind(&supplier_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Query failed: {}", e))
}

#[tauri::command]
pub async fn list_all_orders(
    pool: State<'_, SqlitePool>,
    status: Option<String>,
    limit: Option<i32>,
) -> Result<Vec<SupplierOrder>, String> {
    let limit_val = limit.unwrap_or(50);

    if let Some(status_filter) = status {
        sqlx::query_as::<_, SupplierOrder>(
            "SELECT id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at
             FROM supplier_orders WHERE status = ? ORDER BY data_ordine DESC LIMIT ?",
        )
        .bind(&status_filter)
        .bind(limit_val)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Query failed: {}", e))
    } else {
        sqlx::query_as::<_, SupplierOrder>(
            "SELECT id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at
             FROM supplier_orders ORDER BY data_ordine DESC LIMIT ?",
        )
        .bind(limit_val)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Query failed: {}", e))
    }
}

#[tauri::command]
pub async fn update_order_status(
    pool: State<'_, SqlitePool>,
    order_id: String,
    status: String,
) -> Result<SupplierOrder, String> {
    // Validate status
    let valid_statuses = [
        "draft",
        "sent",
        "confirmed",
        "delivered",
        "failed",
        "cancelled",
    ];
    if !valid_statuses.contains(&status.as_str()) {
        return Err(format!(
            "Invalid status: {}. Valid: {:?}",
            status, valid_statuses
        ));
    }

    sqlx::query("UPDATE supplier_orders SET status = ? WHERE id = ?")
        .bind(&status)
        .bind(&order_id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Update failed: {}", e))?;

    // Return updated order
    get_supplier_order(pool, order_id).await
}

// ═══════════════════════════════════════════════════════════════════
// SUPPLIER INTERACTIONS
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn log_supplier_interaction(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
    order_id: Option<String>,
    tipo: String,
    messaggio: Option<String>,
    status: String,
) -> Result<SupplierInteraction, String> {
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();

    sqlx::query(
        "INSERT INTO supplier_interactions (id, supplier_id, order_id, tipo, messaggio, status, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(&supplier_id)
    .bind(&order_id)
    .bind(&tipo)
    .bind(&messaggio)
    .bind(&status)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Insert failed: {}", e))?;

    Ok(SupplierInteraction {
        id,
        supplier_id,
        order_id,
        tipo,
        messaggio,
        status,
        created_at: now,
    })
}

#[tauri::command]
pub async fn get_supplier_interactions(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
    limit: Option<i32>,
) -> Result<Vec<SupplierInteraction>, String> {
    let limit_val = limit.unwrap_or(50);

    sqlx::query_as::<_, SupplierInteraction>(
        "SELECT id, supplier_id, order_id, tipo, messaggio, status, created_at
         FROM supplier_interactions WHERE supplier_id = ? ORDER BY created_at DESC LIMIT ?",
    )
    .bind(&supplier_id)
    .bind(limit_val)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Query failed: {}", e))
}

// ═══════════════════════════════════════════════════════════════════
// STATISTICS
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize)]
pub struct SupplierStats {
    pub total_suppliers: i32,
    pub active_suppliers: i32,
    pub total_orders: i32,
    pub pending_orders: i32,
    pub total_spent: f64,
}

#[tauri::command]
pub async fn get_supplier_stats(pool: State<'_, SqlitePool>) -> Result<SupplierStats, String> {
    let total_suppliers: (i32,) = sqlx::query_as("SELECT COUNT(*) FROM suppliers")
        .fetch_one(pool.inner())
        .await
        .unwrap_or((0,));

    let active_suppliers: (i32,) =
        sqlx::query_as("SELECT COUNT(*) FROM suppliers WHERE status = 'active'")
            .fetch_one(pool.inner())
            .await
            .unwrap_or((0,));

    let total_orders: (i32,) = sqlx::query_as("SELECT COUNT(*) FROM supplier_orders")
        .fetch_one(pool.inner())
        .await
        .unwrap_or((0,));

    let pending_orders: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) FROM supplier_orders WHERE status IN ('draft', 'sent', 'confirmed')",
    )
    .fetch_one(pool.inner())
    .await
    .unwrap_or((0,));

    let total_spent: (f64,) = sqlx::query_as(
        "SELECT COALESCE(SUM(importo_totale), 0) FROM supplier_orders WHERE status = 'delivered'",
    )
    .fetch_one(pool.inner())
    .await
    .unwrap_or((0.0,));

    Ok(SupplierStats {
        total_suppliers: total_suppliers.0,
        active_suppliers: active_suppliers.0,
        total_orders: total_orders.0,
        pending_orders: pending_orders.0,
        total_spent: total_spent.0,
    })
}
