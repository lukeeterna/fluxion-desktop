// ═══════════════════════════════════════════════════════════════════
// FLUXION - Supplier Management Commands
// CRUD operations for suppliers and supplier orders
// ═══════════════════════════════════════════════════════════════════

use chrono::Utc;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;
use uuid::Uuid;

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
    pub data_consegna_prevista: String,
    pub items: Vec<serde_json::Value>,
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
    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();

    sqlx::query(
        "INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(&supplier.nome)
    .bind(&supplier.email)
    .bind(&supplier.telefono)
    .bind(&supplier.indirizzo)
    .bind(&supplier.citta)
    .bind(&supplier.cap)
    .bind(&supplier.partita_iva)
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
    sqlx::query_as::<_, Supplier>(
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers WHERE id = ?",
    )
    .bind(&supplier_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Supplier not found: {}", e))
}

#[tauri::command]
pub async fn list_suppliers(
    pool: State<'_, SqlitePool>,
    include_inactive: Option<bool>,
) -> Result<Vec<Supplier>, String> {
    let query = if include_inactive.unwrap_or(false) {
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers ORDER BY nome"
    } else {
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers WHERE status = 'active' ORDER BY nome"
    };

    sqlx::query_as::<_, Supplier>(query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Query failed: {}", e))
}

#[tauri::command]
pub async fn update_supplier(
    pool: State<'_, SqlitePool>,
    supplier_id: String,
    update: UpdateSupplierRequest,
) -> Result<Supplier, String> {
    let now = Utc::now().to_rfc3339();

    // Get current supplier first
    let current = sqlx::query_as::<_, Supplier>(
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers WHERE id = ?",
    )
    .bind(&supplier_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Supplier not found: {}", e))?;

    // Apply updates
    let nome = update.nome.unwrap_or(current.nome);
    let email = update.email.or(current.email);
    let telefono = update.telefono.or(current.telefono);
    let indirizzo = update.indirizzo.or(current.indirizzo);
    let citta = update.citta.or(current.citta);
    let cap = update.cap.or(current.cap);
    let partita_iva = update.partita_iva.or(current.partita_iva);
    let status = update.status.unwrap_or(current.status);

    sqlx::query(
        "UPDATE suppliers SET nome=?, email=?, telefono=?, indirizzo=?, citta=?, cap=?, partita_iva=?, status=?, updated_at=?
         WHERE id=?",
    )
    .bind(&nome)
    .bind(&email)
    .bind(&telefono)
    .bind(&indirizzo)
    .bind(&citta)
    .bind(&cap)
    .bind(&partita_iva)
    .bind(&status)
    .bind(&now)
    .bind(&supplier_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Update failed: {}", e))?;

    Ok(Supplier {
        id: supplier_id,
        nome,
        email,
        telefono,
        indirizzo,
        citta,
        cap,
        partita_iva,
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
    let search_term = format!("%{}%", query.to_lowercase());

    sqlx::query_as::<_, Supplier>(
        "SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
         FROM suppliers
         WHERE status = 'active' AND (LOWER(nome) LIKE ? OR LOWER(email) LIKE ? OR telefono LIKE ? OR partita_iva LIKE ?)
         ORDER BY nome
         LIMIT 20",
    )
    .bind(&search_term)
    .bind(&search_term)
    .bind(&search_term)
    .bind(&search_term)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Query failed: {}", e))
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
    let items_json = serde_json::to_string(&order.items)
        .map_err(|e| format!("JSON serialization failed: {}", e))?;

    sqlx::query(
        "INSERT INTO supplier_orders (id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(&order.supplier_id)
    .bind(&order.ordine_numero)
    .bind(&now)
    .bind(&order.data_consegna_prevista)
    .bind(order.importo_totale)
    .bind("draft")
    .bind(&items_json)
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
        data_consegna_prevista: order.data_consegna_prevista,
        importo_totale: order.importo_totale,
        status: "draft".to_string(),
        items: items_json,
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
    let valid_statuses = ["draft", "sent", "confirmed", "delivered", "failed", "cancelled"];
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
