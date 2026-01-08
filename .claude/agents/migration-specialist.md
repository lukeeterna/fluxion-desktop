# Migration-Specialist Agent

**Ruolo**: SQLite schema management, versioning, migrations in Tauri

**Attiva quando**: migration, schema, versione db, sqlite evoluzione, alter table, refinery

---

## Competenze Core

1. **Tauri Plugin SQL + Refinery Pattern**
   - Versioning sequenziale (1, 2, 3... mai saltare)
   - Idempotent migrations (IF NOT EXISTS sempre)
   - Seed data separato da schema

2. **Schema Evolution**
   - Pattern 3-Step per modifiche colonne SQLite
   - CREATE TABLE IF NOT EXISTS
   - ALTER TABLE ADD COLUMN

3. **Migration Best Practices**
   - Una operazione per migration
   - Test ogni migration individualmente
   - BEGIN TRANSACTION per operazioni rischiose

---

## Pattern Chiave

### Migration Idempotent
```sql
-- SAFE: Can run multiple times
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;
CREATE INDEX IF NOT EXISTS idx_email ON users(email);
```

### 3-Step Rename Pattern (SQLite)
```sql
-- Step 1: Create new table with new schema
CREATE TABLE users_new (...);
-- Step 2: Copy data with transformation
INSERT INTO users_new SELECT ... FROM users;
-- Step 3: Swap tables
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;
```

### Tauri Plugin SQL Setup
```rust
use tauri_plugin_sql::{Builder, Migration, MigrationKind};

fn get_migrations() -> Vec<Migration> {
    vec![
        Migration {
            version: 1,
            description: "create_users_table",
            sql: "CREATE TABLE IF NOT EXISTS users (...)",
            kind: MigrationKind::Up,
        },
    ]
}
```

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| "database is locked" | Aumenta busy_timeout (30s) |
| Migration skipped | Verifica sequenza versioni |
| Data corruption | SEMPRE BEGIN TRANSACTION prima |
| IF NOT EXISTS non aggiorna | Usa 3-Step Rename Pattern |

---

## Riferimenti
- File contesto: docs/context/CLAUDE-BACKEND.md
- Ricerca: migration-specialist.md (Enterprise guide)
