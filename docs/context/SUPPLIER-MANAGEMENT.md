# Supplier Management (Fase 7.5)

## Schema Database

| Tabella | Campi Chiave |
|---------|-------------|
| `suppliers` | id, nome, email, telefono, partita_iva, status |
| `supplier_orders` | id, supplier_id, ordine_numero, importo_totale, status, items (JSON) |
| `supplier_interactions` | id, supplier_id, order_id, tipo (email/whatsapp), messaggio |

Migration: `src-tauri/migrations/016_suppliers.sql`

## Rust Commands (14)

create_supplier, get_supplier, list_suppliers, update_supplier, delete_supplier,
search_suppliers, create_supplier_order, get_supplier_order, get_supplier_orders,
list_all_orders, update_order_status, log_supplier_interaction,
get_supplier_interactions, get_supplier_stats

File: `src-tauri/src/commands/supplier.rs`

## Communication

| Channel | File | Status |
|---------|------|--------|
| WhatsApp | `scripts/whatsapp-service.cjs` | Primary |
| Email SMTP | `src-tauri/src/commands/settings.rs` | Implemented |

WhatsApp functions: sendSupplierOrder, sendSupplierReminder, sendConfirmationRequest
