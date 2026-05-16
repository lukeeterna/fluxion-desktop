# S252 — Cat 3 P0 #2 chiusura: Step E live + blind-index + scope extension

**Generato**: 2026-05-16 fine S251 (CLOSED GREEN — Step D landed, unit test PASS)
**Repo**: master `03a1b9b` (MacBook + iMac sync OK)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.
**Mandato S181**: CTO decide P0/P1/P2 autonomamente (founder NON dev).

---

## S251 — Cosa è stato chiuso (commit `03a1b9b`)

### Step D — Migration runner `encrypt_clienti_pii` (commit `03a1b9b`)

**Atomico**: SQL migration 038 + `data_migration.rs` runner (~290 righe + 150 righe test) + `lib.rs` wire (declarazione mod + migration 038 in chain + trigger post Step C auto-init).

**Invariants implementati**:
- `VACUUM INTO` backup PRIMA di ogni UPDATE (atomic, WAL-safe).
- 100-row batched transactions; marker = LAST WRITE → crash mid-loop riprende su 2nd run via detection heuristic (`decrypt_field` Ok = già ciphertext → skip).
- Pre-flight `is_encryption_ready()` Err graceful (caller in `lib.rs` logga e prosegue, no crash su cold-start pre-wizard).
- Sentry `capture_message` su failure non-fatale.
- Backup path: `<app_data>/fluxion.db.pre-encryption-bak-<UTC-ts>`.

**Test landed**: `cargo test --lib data_migration::tests::test_encrypt_clienti_pii_basic_and_idempotent` su iMac → **1 passed**. Copre: 10 plaintext rows → tutte cifrate (verify decrypt round-trip), marker inserito con `rows_processed=10`, backup file scritto su disco, 2nd run → `already_applied=true` con 0 rows modified.

**cargo check iMac**: 0 errori (15 warnings dead-code pre-esistenti invariati).

**Trigger in lib.rs** (post Step C Ok branch, solo se encryption ready):
```rust
match data_migration::encrypt_clienti_pii(&pool, &db_path).await {
    Ok(report) if report.already_applied => { /* log already_applied */ }
    Ok(report) => { /* log N encrypted, M skipped, backup path */ }
    Err(e) => { /* log non-fatal + sentry, app boots anyway */ }
}
```

### Step E — Live test live runtime (DEFERRED)

**Status**: NON eseguito in S251. `npm run tauri dev` richiede display GUI macOS → non riproducibile headless via SSH dal MacBook. Unit test (Step D) copre il core path (10 plaintext → ciphertext + marker + idempotent + backup).

**Action S252**: founder o sessione mente fresca lancia app su iMac fisicamente, verifica startup log:
```
🔐 GDPR encryption auto-initialized from license_cache
🔐 PII migration: N rows encrypted, M already ciphertext, backup at /Users/.../fluxion.db.pre-encryption-bak-<ts>
```
Su fresh install (DB nuovo, 0 clienti): aspetta `0 rows encrypted, 0 already ciphertext`. Marker presente. 2nd start: `PII migration: already applied`.

---

## S252 — Cosa fare (effort ~3-4h, mente fresca, FILE CRITICI <40%)

### Priorità ordinata

**P0 — Step E live verification** (~30min, founder fisicamente su iMac)
- Avviare app dev su iMac (`npm run tauri dev`)
- Verificare startup log Step C + Step D
- Seed test: creare 5 clienti via UI con telefono + email + CF
- Inspect `sqlite3 ~/Library/Application Support/.../fluxion.db "SELECT nome, telefono FROM clienti LIMIT 5"` → output Base64 (NON plaintext)
- Verify search per "Mario" via UI funziona (tier-1 in-memory filter pattern S249)
- Restart app → log "PII migration: already applied"
- 2nd seed (3 nuovi clienti) → search funziona, sqlite3 raw verify Base64

**P1 — Scope extension `operatori` PII** (~1.5h, FILE CRITICI <40%)
- Nuovo runner `encrypt_operatori_pii_v1` in `data_migration.rs`
- Marker key separato (`encrypt_operatori_pii_v1`) → idempotente independente da clienti
- Trigger in `lib.rs` post Step D, identico pattern (Ok/Err logging)
- Test unit parallelo (~50 righe)
- Wire `commands/operatori.rs` con `ensure_encryption_ready_pool` + decrypt closure (pattern S249 stabilito su `clienti.rs`)

**P2 — Scope extension `suppliers` PII** (~1h)
- Analogo P1 — runner `encrypt_suppliers_pii_v1` + wire `commands/suppliers.rs`
- Volume tipico: 5-20 fornitori/cliente PMI → no perf concerns

**P3 — Cifratura `fatture.cliente_*` snapshot columns** (~1h)
- Colonne denormalizzate (nome/cognome/indirizzo/CF/PIVA snapshotted a creazione fattura, immutabili)
- Runner `encrypt_fatture_pii_snapshot_v1`
- Wire `commands/fatture.rs` read paths con decrypt (S249 wiring NON ha toccato snapshot columns)
- **Critico per GDPR**: fatture archiviate >10 anni per legge → PII leak rischio se DB esfiltrato

**P4 — Blind-index HMAC su `telefono`** (~1.5h, FILE CRITICI <40%, scale-only)
- Migration 039: `ALTER TABLE clienti ADD COLUMN telefono_bidx TEXT` + index `idx_clienti_telefono_bidx`
- HMAC-SHA256 deterministic con chiave separata da AES key (CipherSweet pattern), salt costante (NON random — deve essere deterministic per match)
- Runner one-shot `compute_telefono_bidx_v1` (idempotent via marker, popola colonna per row esistenti)
- Wire `commands/clienti.rs::search_by_phone` + `http_bridge` Sara endpoint: normalizza input → compute HMAC → WHERE telefono_bidx = ?
- Trade-off: O(log n) lookup vs full-table decrypt → essenziale per Sara <800ms con >1000 clienti
- **Decision aperta**: chiave HMAC dove? Opt A — derivata da master key esistente con HKDF context "telefono-bidx" (zero config). Opt B — separata in keychain. Raccomandazione: Opt A (semplicità + zero friction wizard).

### AC misurabili S252

- P0: founder report log ✓ + sqlite3 raw verify Base64 ✓
- P1-P3: `cargo check` 0 errori + unit test ciascun runner PASS + commit atomico
- P4: Sara search 1000 clienti seeded < 50ms (perf benchmark)

### Comandi start S252

```bash
# 1. Sync verifica
git log --oneline -1   # MacBook
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git log --oneline -1'  # iMac

# 2. /context baseline → se <40% procedere atomico
# 3. P0 Step E: founder lancia app GUI iMac
# 4. P1+P2+P3+P4 in 4 commit atomici separati (mai bundle FILE CRITICI multipli)
```

---

## Riferimenti permanenti

- Decision Opt A master_password derivation: `.claude/cache/agents/s248/master-password-flow-decision.md`
- 11 SENSITIVE_FIELDS list + tier classification: `src-tauri/src/encryption.rs` riga 189
- Pattern wiring uniforme S249 (tier-1 in-memory filter): `src-tauri/src/commands/clienti.rs`
- Step C setup hook S250: `src-tauri/src/lib.rs` linea ~453
- Step D runner S251: `src-tauri/src/data_migration.rs`
- Migration 038 marker schema: `src-tauri/migrations/038_encryption_migration_state.sql`
