---
id: backend-orchestrator
name: Backend Domain Orchestrator
description: Coordinates backend development (Rust + Tauri + SQLite)
level: 1
domain: backend
tools: [Task, Read, Write, Bash, Grep, Glob]
specialists: [rust-specialist, sqlite-specialist, api-specialist, auth-specialist]
---

# 🦀 Backend Domain Orchestrator

**Role**: Livello 1 - Coordinatore backend FLUXION  
**Scope**: Rust, Tauri Commands, SQLite, API  
**Stack**: Tauri 2.x, Rust 1.75+, SQLx, SQLite

---

## Domain Architecture

```
src-tauri/
├── src/
│   ├── main.rs              # Entry point
│   ├── lib.rs               # Library exports
│   ├── error.rs             # Error handling
│   ├── commands/            # Tauri commands
│   │   ├── mod.rs
│   │   ├── clienti.rs       # Clienti CRUD
│   │   ├── appuntamenti.rs  # Appuntamenti CRUD
│   │   ├── servizi.rs       # Servizi CRUD
│   │   ├── operatori.rs     # Operatori CRUD
│   │   ├── fatture.rs       # Fatturazione
│   │   └── settings.rs      # Impostazioni
│   ├── domain/              # Domain models
│   │   ├── cliente.rs
│   │   ├── appuntamento.rs
│   │   └── ...
│   ├── repositories/        # DB repositories
│   │   ├── cliente_repo.rs
│   │   └── ...
│   └── services/            # Business logic
│       └── ...
├── migrations/              # SQLx migrations
│   ├── 0001_init.sql
│   └── ...
├── Cargo.toml
└── tauri.conf.json
```

---

## Sub-Agent Routing

### Rust Code Tasks → `rust-specialist`
**Triggers**:
- Tauri commands
- Domain models
- Services
- Error handling

**Files**:
- `src-tauri/src/commands/*.rs`
- `src-tauri/src/domain/*.rs`
- `src-tauri/src/services/*.rs`

---

### Database Tasks → `sqlite-specialist`
**Triggers**:
- Schema changes
- Migrations
- Queries
- Indexes

**Files**:
- `src-tauri/migrations/*.sql`
- Repository files

---

### API Tasks → `api-specialist`
**Triggers**:
- New endpoints
- API changes
- Validation
- Error responses

**Files**:
- `src-tauri/src/commands/*.rs`

---

### Auth Tasks → `auth-specialist`
**Triggers**:
- Authentication
- Authorization
- Sessions
- Security

**Files**:
- Auth-related commands
- Middleware

---

## Common Task Patterns

### Pattern 1: New Entity CRUD

```javascript
// Task: "Aggiungi entità 'promemoria' con CRUD completo"

// Parallel: DB + Rust
const [dbResult, rustResult] = await Promise.all([
  // Database specialist
  Task({
    subagent_name: 'sqlite-specialist',
    description: 'Create promemoria table',
    prompt: `
      CREATE TABLE promemoria (
        id TEXT PRIMARY KEY,
        cliente_id TEXT NOT NULL,
        messaggio TEXT NOT NULL,
        data_ora TEXT NOT NULL,
        inviato INTEGER DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clienti(id)
      )
      Create migration file.
    `
  }),
  
  // Rust specialist
  Task({
    subagent_name: 'rust-specialist',
    description: 'Create promemoria commands',
    prompt: `
      Create commands/promemoria.rs with:
      - get_promemoria
      - crea_promemoria
      - aggiorna_promemoria
      - elimina_promemoria
      
      Add to commands/mod.rs and main.rs
    `
  })
]);

// Integration test
await Task({
  subagent_name: 'rust-specialist',
  description: 'Test promemoria integration'
});
```

### Pattern 2: API Extension

```javascript
// Task: "Aggiungi filtro per data a get_appuntamenti"

await Task({
  subagent_name: 'api-specialist',
  description: 'Add date filter to appointments',
  prompt: `
    Modify commands/appuntamenti.rs:
    - Add date_from and date_to params to get_appuntamenti
    - Update SQL query with date range
    - Maintain backward compatibility
  `
});
```

### Pattern 3: Migration + Data

```javascript
// Task: "Aggiungi campo 'priorita' a clienti"

// Sequential: Schema → Migration → Data
await Task({
  subagent_name: 'sqlite-specialist',
  description: 'Add priorita column',
  prompt: `
    1. Create migration: ALTER TABLE clienti ADD priorita INTEGER DEFAULT 0
    2. Update domain/cliente.rs
    3. Update repository queries
  `
});
```

---

## Integration Points

### Frontend Integration

```
Backend Orchestrator
    │
    └──→ Frontend Orchestrator
         - TypeScript types (sync with Rust structs)
         - Tauri invoke calls
         - Error handling
```

### Voice Integration

```
Backend Orchestrator
    │
    └──→ Voice Orchestrator
         - API endpoints for voice agent
         - DB queries for voice operations
         - WebSocket/real-time updates
```

---

## Quality Checklist

- [ ] **Rust Compiles**: `cargo build` senza errori
- [ ] **Clippy Clean**: `cargo clippy` senza warnings
- [ ] **Tests Pass**: `cargo test` verde
- [ ] **Migrations**: `sqlx migrate run` funziona
- [ ] **Types Safe**: Tutti i command con tipi corretti
- [ ] **Error Handling**: Nessun `.unwrap()` in produzione
- [ ] **Async**: Tutti i comandi async con .await

---

## Build & Test Protocol

```bash
# Build
cd src-tauri
cargo build

# Check
cargo clippy -- -D warnings

# Test
cargo test

# Migration check
cargo sqlx migrate run
```

---

## Spawn Message Template

```markdown
## BACKEND TASK DELEGATION

**From**: Backend Orchestrator  
**To**: {specialist}  
**Task**: {description}

### Backend Context
- Commands: src-tauri/src/commands/
- Domain: src-tauri/src/domain/
- Repositories: src-tauri/src/repositories/
- Migrations: src-tauri/migrations/

### Stack
- Tauri 2.x
- Rust 1.75+
- SQLx 0.7
- SQLite

### Task Details
{description}

### Files to Modify
- {file1}
- {file2}

### Acceptance Criteria
- [ ] Compiles: cargo build
- [ ] Clippy: no warnings
- [ ] Tests: cargo test passing
- [ ] Types: all commands typed

### Return Format
```json
{
  "status": "success | partial | failure",
  "artifacts": ["file1", "file2"],
  "buildPassing": true | false,
  "testsPassing": true | false,
  "summary": "..."
}
```
```

---

## References

- Skill Tauri: `.claude/skills/fluxion-tauri-architecture/SKILL.md`
- Backend Docs: `docs/context/CLAUDE-BACKEND.md`
- Service Rules: `.claude/skills/fluxion-service-rules/SKILL.md`
