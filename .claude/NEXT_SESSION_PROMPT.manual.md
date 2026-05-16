# S251 — Cat 3 P0 #2: migration runner (Step D) + E2E live (Step E)

**Generato**: 2026-05-16 fine S250 (CLOSED — Step C landed, Step D+E deferred per context budget gate)
**Repo**: master `9aabfce` (MacBook + iMac sync OK)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.
**Mandato S181**: CTO decide P0/P1/P2 autonomamente (founder NON dev).

---

## S250 — Cosa è stato chiuso (commit `9aabfce`)

**Step C completato in isolamento atomico**. Step D+E NON tentati: context arrivato a 57% durante setup hook editing → soglia `BLOCK_CRITICAL` (50-70%, `.claude/rules/context-budget-gate.md`) attivata → S185-A enforcement (errori migration su file critici si propagano a tutto downstream, corruzione DB possibile).

### Step C — Setup hook (commit `9aabfce`)

`src-tauri/src/lib.rs` `init_database()` post-migrations, pre-service-layer:

```rust
match encryption::auto_init_from_pool(&pool).await {
    Ok(()) => {
        if encryption::is_encryption_ready() {
            println!("🔐 GDPR encryption auto-initialized from license_cache");
        }
    }
    Err(e) => {
        println!(
            "ℹ️  GDPR encryption deferred (CRUD will retry on first sensitive call): {}",
            e
        );
    }
}
```

**Hot path**: `license_cache` row presente → AES key derivata da `license_key + fingerprint` (PBKDF2-SHA256 100k iters, salt random per-installation in OS keychain).
**Cold path**: pre-wizard → log informativo, no crash. Runtime gate `ensure_encryption_ready_pool(pool)` nei 12 file CRUD/read S249 retry lazy.
**Idempotente**: OnceLock 2nd call → Ok early-return.

cargo check iMac: **0 errori**, 15 warnings dead-code pre-esistenti.

---

## S251 — Cosa fare (effort ~2-3h, FILE CRITICI <40%)

### Step D — Migration runner (~2h, FILE CRITICO <40%)

**Goal**: cifrare in-place righe `clienti` plaintext pre-S249 esistenti in DB installati. Idempotente, atomico, crash-safe.

**File da creare** (atomicamente in singolo commit con SQL+Rust+wire):

1. **`src-tauri/migrations/038_encryption_migration_state.sql`** — marker table:
```sql
CREATE TABLE IF NOT EXISTS encryption_migration_state (
    migration_key   TEXT PRIMARY KEY,
    applied_at      TEXT NOT NULL DEFAULT (datetime('now')),
    rows_processed  INTEGER NOT NULL DEFAULT 0,
    backup_path     TEXT
);
```

2. **`src-tauri/src/data_migration.rs`** — runner (~150 righe):
   - `pub async fn encrypt_clienti_pii(pool: &SqlitePool, db_path: &Path) -> Result<MigrationReport, String>`
   - **Pre-flight**: `is_encryption_ready()` → false ⇒ Err("encryption not ready, complete setup wizard first")
   - **Marker check**: `SELECT 1 FROM encryption_migration_state WHERE migration_key = 'encrypt_clienti_pii_v1'` → present ⇒ no-op `MigrationReport::already_applied()`
   - **Backup**: `VACUUM INTO 'fluxion.db.pre-encryption-bak-{ts}'` (atomico, WAL-safe, esclude WAL plaintext residue)
   - **Detection per riga**: `decrypt_field(&value)` ⇒ Ok → già cifrata (skip). Err → plaintext (encrypt). Empty → skip.
   - **Batch processing**: chunks 100 righe/TX, idempotente per ripresa post-crash (detection-based, no progress file separato necessario)
   - **Loop**: `SELECT id, nome, cognome, telefono, email, codice_fiscale, partita_iva, indirizzo, cap, citta, pec, data_nascita FROM clienti` → per-field encrypt se plaintext → UPDATE WHERE id = ?
   - **Marker insert**: post-completion `INSERT INTO encryption_migration_state ...` con counter rows_processed + backup_path
   - **Return**: `MigrationReport { encrypted: N, skipped: M, backup_path: PathBuf }`

3. **`src-tauri/src/lib.rs`** — wire (3 modifiche minime):
   - `mod data_migration;` declaration top
   - `run_migration(&pool, "038", include_str!("../migrations/038_encryption_migration_state.sql")).await?;` in sequenza dopo migration 037
   - Dopo Step C auto-init success block: trigger `data_migration::encrypt_clienti_pii(&pool, &db_path).await` con log success/non-fatal-warning

**AC misurabili Step D**:
- `cargo check` iMac 0 errori
- Test unit: 10 righe plaintext in DB test → tutte cifrate, decrypt round-trip OK, marker presente, backup file esiste
- Test idempotent: 2nd run ⇒ 0 modified rows, return `already_applied()`
- Test crash mid-batch: kill -9 dopo prima TX commit → 2nd run completa correttamente (riprende da riga successiva tramite detection)
- Test cold-start (no encryption ready): runner return Err graceful, no panic

**Rischi noti / scope-out S251**:
- `fatture.cliente_*` snapshot columns (denormalizzate da clienti a creazione fattura) NON cifrate ⇒ partial PII leak ⇒ **FIXME S252** separata
- `operatori.{nome,cognome,telefono,email}` NON in S249 scope ⇒ NON gestiti da questo runner ⇒ S252+
- `suppliers.*` analogo ⇒ S252+

### Step E — E2E live (~30min, dipende Step D, OK <50% context)

**Test cases ordinati**:
1. **Fresh install** + setup wizard + create cliente con telefono+email+CF → `sqlite3 .../fluxion.db "SELECT nome, telefono FROM clienti LIMIT 1"` → verifica output **Base64** (NON plaintext "Mario")
2. **Search "Mario"** via Tauri IPC → restituisce cliente cifrato decifrato in-memory (tier-1 pattern S249)
3. **Sara IPC** POST `http://127.0.0.1:3001/clienti/search?q=339` → match by phone normalized, decrypt OK
4. **GDPR Art.20 export CSV** → contenuto plaintext leggibile
5. **Migration su DB con 5 righe plaintext seed**:
   - Pre: SELECT raw → tutto plaintext
   - Start app (triggera Step C + Step D)
   - Post: SELECT raw → tutto Base64, marker presente, backup file `app.db.pre-encryption-bak-*` esiste
   - 2nd app restart → log "PII migration: already applied", 0 rows modified

**Comandi**:
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && cargo test --lib data_migration:: 2>&1 | tail -20'
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && DATABASE_PATH=/tmp/fluxion-test.db npm run tauri dev > /tmp/sara-live-s251.log 2>&1 &'
ssh imac 'sleep 8 && curl -s -X POST http://127.0.0.1:3001/clienti/create -H "Content-Type: application/json" -d "{\"nome\":\"Mario\",\"cognome\":\"Rossi\",\"telefono\":\"3391234567\"}"'
ssh imac 'sqlite3 /tmp/fluxion-test.db "SELECT nome, telefono FROM clienti LIMIT 3;"'  # verify Base64
```

### Step F (futuro S252) — Blind-index + estensione scope

- HMAC-SHA256 deterministic su `telefono` normalizzato ⇒ colonna indicizzata `telefono_bidx` per O(log n) Sara lookup <800ms scale >10k clienti (CipherSweet pattern)
- Encrypt `fatture.cliente_*` snapshot columns denormalizzate
- Encrypt `operatori.{nome,cognome,telefono,email}` + nuovo runner `encrypt_operatori_pii_v1`
- Encrypt `suppliers.*` analogo

---

## Vincoli context S251

- **Step D = FILE CRITICI** (migration SQL nuova + runner Rust nuovo + lib.rs edit autoritativo). Soglia hard `<40%` (S185-A).
- **Step E** = test, non file critico, OK 40-50%.
- Se context >40% all'inizio S251: chiudi pulito, schedule S251-bis mente fresca.

## Comando di start S251

```bash
# 1. Sync verifica (dovrebbe essere già 9aabfce)
git log --oneline -1   # MacBook
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git log --oneline -1'  # iMac
# 2. /context per misurare baseline
# 3. Se <40% → procedere Step D atomico (SQL+Rust+wire in singolo commit)
# 4. Se ≥40% → kill sessione, schedule S251-bis
```

## Riferimenti permanenti

- Decision Opt A master_password: `.claude/cache/agents/s248/master-password-flow-decision.md`
- 11 SENSITIVE_FIELDS list + tier classification: `src-tauri/src/encryption.rs` riga 189
- Pattern wiring uniforme S249: `src-tauri/src/commands/clienti.rs` (tier-1 in-memory filter pattern)
- Step C setup hook S250: `src-tauri/src/lib.rs` linea ~442 (post-migrations block)
- FIXME residui S252: blind-index telefono + cifrare `fatture.cliente_*` + estendere `operatori`/`suppliers`
