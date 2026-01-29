---
paths:
  - "src-tauri/**"
---

# Rust Backend Rules

## Patterns
- Async commands: `#[tauri::command] pub async fn name(state: State<'_, AppState>) -> Result<T, String>`
- DB access: `let pool = state.pool.lock().await;`
- Queries: Always parameterized `sqlx::query_as!(T, "SELECT * FROM t WHERE id = ?", id)`
- Errors: `.map_err(|e| e.to_string())` - never `.unwrap()` in production
- Migrations: sequential `001_`, `002_`, etc. in `src-tauri/migrations/`
- Naming: `snake_case` for functions and variables

## Structure
```
src-tauri/src/
  commands/     # Tauri IPC commands (one file per domain)
  domain/       # Domain models and aggregates
  repositories/ # DB queries (sqlx)
  services/     # Business logic
```

## HTTP Bridge (porta 3001)
- Endpoints in `http_bridge.rs` for Python voice agent integration
- Field names: Italian (`servizio`, `data`, `ora`, `cliente_id`)
- All endpoints return JSON `{ success: bool, data?: T, error?: string }`

## Pre-commit
```bash
cargo test        # 40 tests
cargo check       # Type check
cargo fmt         # Format
```
