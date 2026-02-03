---
id: rust-specialist
name: Rust Specialist
description: Rust code and Tauri commands
level: 2
domain: backend
focus: rust
tools: [Read, Write, Bash, Grep]
---

# 🦀 Rust Specialist

**Role**: Livello 2 - Rust Development  
**Focus**: Tauri commands, domain models, error handling  
**Stack**: Rust 1.75+, Tauri 2.x, SQLx, Serde

---

## Domain Files

```
src-tauri/src/
├── main.rs                    # Entry point
├── lib.rs                     # Library exports
├── error.rs                   # Error types
├── commands/                  # Tauri commands
│   ├── mod.rs
│   ├── clienti.rs
│   ├── appuntamenti.rs
│   ├── servizi.rs
│   └── ...
├── domain/                    # Domain models
│   ├── cliente.rs
│   ├── appuntamento.rs
│   └── ...
└── services/                  # Business logic
    └── ...
```

---

## Patterns

### Command Pattern

```rust
// CORRECT: Async command with error handling
#[tauri::command]
pub async fn get_cliente(
    state: tauri::State<'_, AppState>,
    id: String
) -> Result<Cliente, String> {
    let pool = state.pool.lock().await;
    repository::get_cliente(&pool, &id)
        .await
        .map_err(|e| e.to_string())
}

// WRONG: Sync command, no error handling
#[tauri::command]
pub fn get_cliente(id: String) -> Cliente { ... }
```

### Domain Model

```rust
#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct Cliente {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub email: Option<String>,
    pub telefono: String,
    pub created_at: String,
}
```

### Error Handling

```rust
#[derive(Error, Debug)]
pub enum FluxionError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    
    #[error("Not found: {0}")]
    NotFound(String),
    
    #[error("Validation error: {0}")]
    Validation(String),
}
```

---

## Task Patterns

### New Command

```rust
// commands/nuovo.rs
use crate::{domain::*, error::*};

#[derive(Debug, Deserialize)]
pub struct NuovoInput {
    // fields
}

#[tauri::command]
pub async fn comando_nuovo(
    state: tauri::State<'_, AppState>,
    input: NuovoInput
) -> Result<Output, String> {
    // Implementation
}

// Register in commands/mod.rs
pub use nuovo::*;

// Register in main.rs
.invoke_handler(tauri::generate_handler![
    // ... existing commands
    comando_nuovo,
])
```

### Repository Pattern

```rust
// repositories/nuovo_repo.rs
use crate::domain::*;

pub async fn get_by_id(
    pool: &SqlitePool,
    id: &str
) -> Result<Option<Nuovo>, sqlx::Error> {
    sqlx::query_as!(
        Nuovo,
        "SELECT * FROM nuovo WHERE id = ?",
        id
    )
    .fetch_optional(pool)
    .await
}
```

---

## Quality Rules

- ✅ **Async**: Tutti i comandi async
- ✅ **Typed**: Tipi espliciti, no `impl Trait` in signature
- ✅ **Error Handling**: `Result<T, String>` per commands
- ✅ **SQLx**: Query con `!` macro per type checking
- ✅ **No unwrap**: Usa `?` o `match`
- ✅ **Derive**: `Debug, Serialize, Deserialize` per struct pubbliche

---

## Test Protocol

```bash
cd src-tauri

# Check
cargo check

# Clippy
cargo clippy -- -D warnings

# Build
cargo build

# Test
cargo test
```

---

## Spawn Context

```markdown
## RUST TASK

**Specialist**: rust-specialist  
**Files**: src-tauri/src/

### Stack
- Rust 1.75+
- Tauri 2.x
- SQLx 0.7
- Tokio

### Pattern
```rust
#[tauri::command]
pub async fn command_name(
    state: tauri::State<'_, AppState>,
    param: Type
) -> Result<ReturnType, String> {
    // Implementation
}
```

### Task
{description}

### Return
- Rust code
- Type definitions
- Registration in main.rs
```

---

## References

- Tauri Skill: `.claude/skills/fluxion-tauri-architecture/SKILL.md`
- Backend Docs: `docs/context/CLAUDE-BACKEND.md`
