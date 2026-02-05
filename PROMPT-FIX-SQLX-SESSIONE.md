# PROMPT SESSIONE - Fix Completo SQLx 0.8+ Migration
**Data**: Nuova Sessione  
**Obiettivo**: Fix totale errori compilazione Tauri/SQLx  
**Priorità**: Alta

---

## 🎯 STACK ERRORI IDENTIFICATI

### Errore 1: SqlitePool Import Mancante
**File**: `src/commands/appuntamenti.rs`, `src/commands/clienti.rs`, etc.  
**Errore**: `cannot find type SqlitePool in this scope`
```rust
// FIX RICHIESTO:
use sqlx::SqlitePool;  // Aggiungere agli import
```

### Errore 2: State vs AppState Confusione  
**File**: `src/commands/appuntamenti.rs` (linee 672, 676, 679)
**Errore**: `cannot find value state in this scope`
```rust
// PROBLEMA:
.execute(&state.db)  // state è State<'_, SqlitePool>, non AppState

// FIX RICHIESTO:
.execute(&*pool)  // Usare pool direttamente
```

### Errore 3: sqlx::query! Macro Richiede DATABASE_URL
**File**: `src/commands/audit.rs` (linee 277, 302)
**Errore**: `error returned from database: no such table`
```rust
// PROBLEMA:
sqlx::query_as!(GdprSettingRow, "SELECT ...")  // Macro compile-time check

// FIX OPZIONE A - Usare query_as normale:
sqlx::query_as::<_, GdprSettingRow>("SELECT ...")

// FIX OPZIONE B - sqlx prepare:
// cargo sqlx prepare --database-url sqlite://fluxion.db
```

### Errore 4: FromRow Trait Non Implementato
**File**: `src/commands/schede_cliente.rs`
**Errore**: `the trait bound FromRow<...> is not satisfied`
```rust
// FIX RICHIESTO:
#[derive(sqlx::FromRow)]  // Aggiungere derive
pub struct SchedaOdontoiatricaRow {
    // ...
}
```

### Errore 5: Tuple Troppo Grandi (>16 elementi)
**File**: `src/commands/schede_cliente.rs`
**Errore**: `FromRow not satisfied for tuple (...)`
```rust
// PROBLEMA:
let row: Option<(String, String, ..., 20+ types)> = sqlx::query_as(...)

// FIX RICHIESTO:
// Usare struct con #[derive(sqlx::FromRow)] invece di tuple
```

### Errore 6: Match Non Esaustivo
**File**: `src/services/audit_service.rs` (linee 286, 351, 428)
**Errore**: `non-exhaustive patterns`
```rust
// FIX RICHIESTO:
match action {
    AuditAction::Create => ...,
    AuditAction::Update => ...,
    // Aggiungere:
    AuditAction::Export => ...,
    AuditAction::Anonymize => ...,
    AuditAction::Login => ...,
    AuditAction::Logout => ...,
}
```

### Errore 7: Type Annotations Needed
**File**: `src/commands/appuntamenti.rs`
**Errore**: `type annotations needed`
```rust
// FIX: Specificare tipi espliciti nelle chiusure
.map(|row: ClienteRow| { ... })
```

---

## 📁 FILE DA MODIFICARE

### Alta Priorità (Blocca Build)
1. `src/commands/mod.rs` - Ripristinare `pub mod schede_cliente`
2. `src/commands/schede_cliente.rs` - Fix FromRow + tuples
3. `src/commands/appuntamenti.rs` - Fix state/pool confusione
4. `src/commands/audit.rs` - Fix query! macro
5. `src/services/audit_service.rs` - Fix match esaustivi

### Media Priorità (Warning)
6. `src/commands/clienti.rs` - Aggiungere import SqlitePool
7. `src/infra/repositories/audit_repository.rs` - Verificare fix

---

## 🔧 COMANDI PER RICERCA SOLUZIONI

### Reddit Research
```bash
# Cercare pattern sqlx 0.8+ su Reddit
curl "https://www.reddit.com/r/rust/search.json?q=sqlx+0.8+FromRow&sort=new&limit=10"
curl "https://www.reddit.com/r/rust/search.json?q=sqlx+sqlite+tauri&sort=new&limit=10"

# Tauri v2 patterns
curl "https://www.reddit.com/r/rust/search.json?q=tauri+v2+sqlite&sort=new&limit=10"
```

### GitHub Research
```bash
# Trovare repo con pattern simili
github-search "sqlx 0.8 FromRow derive" language:rust
github-search "tauri sqlx sqlite pool" language:rust

# Esempi specifici:
# - https://github.com/search?q=sqlx+FromRow+derive+struct&type=code
# - https://github.com/search?q=tauri+sqlite+sqlx+example&type=code
```

---

## 📋 CHECKLIST FIX

### Step 1: Database Setup
- [ ] Verificare `DATABASE_URL` o eseguire `sqlx prepare`
- [ ] Creare tabelle mancanti (`gdpr_settings`, `audit_log`, etc.)
- [ ] Verificare migration 019 e 020 esistano

### Step 2: Fix Importazioni
- [ ] Aggiungere `use sqlx::SqlitePool;` dove mancante
- [ ] Verificare `use sqlx::FromRow;` dove necessario

### Step 3: Fix Structs
- [ ] Aggiungere `#[derive(sqlx::FromRow)]` a tutte le Row structs
- [ ] Convertire tuple >16 elementi in struct dedicate

### Step 4: Fix Query
- [ ] Sostituire `sqlx::query!` con `sqlx::query_as::<_, Type>`
- [ ] Fix riferimenti `state.db` → `&*pool`

### Step 5: Fix Pattern Matching
- [ ] Completare match `AuditAction` con tutte le varianti
- [ ] Aggiungere `_ => ...` dove appropriato

### Step 6: Ripristino Moduli
- [ ] Ripristinare `pub mod schede_cliente` in `mod.rs`
- [ ] Ripristinare re-exports
- [ ] Ripristinare comandi in `lib.rs`

---

## 🧪 TEST POST-FIX

```bash
# 1. Verifica build
cd src-tauri
export DATABASE_URL="sqlite:fluxion.db"
cargo check --lib

# 2. Verifica build completa
cargo build --release

# 3. Test app
cd ..
npm run tauri dev

# 4. Test specifici
cargo test --lib
```

---

## 📊 STATO ATTUALE (Riferimento)

### Moduli Disabilitati Temporaneamente
```rust
// In src/commands/mod.rs:
// pub mod schede_cliente;

// In src/lib.rs:
// commands::schede_cliente::*
// commands::audit::*
```

### Comandi Funzionanti
- ✅ operatori
- ✅ clienti (base)
- ✅ appuntamenti (parziale)
- ✅ servizi
- ✅ license_ed25519

---

## 💾 BACKUP

Prima di iniziare:
```bash
cp -r src-tauri/src src-tauri/src.backup.$(date +%Y%m%d)
cp src-tauri/fluxion.db src-tauri/fluxion.db.backup.$(date +%Y%m%d)
```

---

## 🔗 RISORSE

- SQLx 0.8 Changelog: https://github.com/launchbadge/sqlx/blob/main/CHANGELOG.md
- SQLx FromRow: https://docs.rs/sqlx/latest/sqlx/trait.FromRow.html
- Tauri v2 SQL: https://v2.tauri.app/plugin/sql/

---

**INIZIA SESSIONE CON**: "Fix SQLx 0.8+ migration per FLUXION"
