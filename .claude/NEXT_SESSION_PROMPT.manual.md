# S250 — Cat 3 P0 #2: setup hook (Step C) + migration (Step D) + E2E (Step E)

**Generato**: 2026-05-16 fine S249 (CLOSED GREEN — commit `0ed0e25`)
**Repo**: master `0ed0e25` (MacBook sync OK, iMac PENDING `git pull` start S250)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.
**Mandato S181**: CTO decide P0/P1/P2 autonomamente (founder NON dev).

---

## S249 — Cosa è stato chiuso (commit `0ed0e25`)

**Step B esteso autonomamente** da 1 file (clienti.rs) a **12 file** post pattern-recognition rule #11 grep audit cross-file. Scoperti 11 call site addizionali oltre il piano originale che leggono/scrivono i 11 SENSITIVE_FIELDS — committarli separatamente avrebbe lasciato runtime exceptions in produzione una volta lanciata la migration.

### 12 file wired (AES-256-GCM at rest)

| File | Path | Pattern |
|------|------|---------|
| 1. encryption.rs | `src-tauri/src/` | Refactor: `auto_init_from_pool` + `ensure_encryption_ready_pool` per code paths con `&SqlitePool` |
| 2. clienti.rs | `commands/` | CRUD (create/update encrypt, get/search decrypt tier-1 in-memory) |
| 3. http_bridge.rs | `src-tauri/src/` | Sara IPC bridge porta 3001 (create+search clienti) |
| 4. faq_template.rs | `commands/` | Sara name/phone lookup, normalize_phone helper |
| 5. fatture.rs | `commands/` | Invoice: SELECT nome/cognome separati + compose Rust-side (no SQL `\|\|` su ciphertext) |
| 6. loyalty.rs | `commands/` | 4 paths: get_loyalty_info, top_referrers, milestones, whatsapp_interno + compleanno_settimana (rimosso `strftime('%m-%d',...)` broken su Base64) |
| 7. media.rs | `commands/` | PDF export nome cliente |
| 8. support.rs | `commands/` | GDPR Art. 20 portability CSVs (clienti + appuntamenti) |
| 9. appuntamenti.rs | `commands/` | get_appuntamenti JOIN cliente |
| 10. whatsapp.rs | `commands/` | send_booking_confirm_wa decrypt telefono+nome |
| 11. **cassa.rs** ⭐ | `commands/` | get_incassi_giornata: refactor `\|\|` concat (NUOVO post-compact) |
| 12. **dashboard.rs** ⭐ | `commands/` | get_appuntamenti_oggi: refactor `\|\|` concat (NUOVO post-compact via grep) |

⭐ = file scoperti post-compact via grep, NON nella summary pre-compact.

### Pattern uniforme stabilito (riusabile S250+)

```rust
// 1. Gate at function entry (any function with &SqlitePool)
crate::encryption::ensure_encryption_ready_pool(pool).await?;

// 2. Per-field decrypt closure (graceful fallback for legacy plaintext rows)
let dec_str = |s: String| -> String {
    if s.is_empty() { s } else { crate::encryption::decrypt_field(&s).unwrap_or(s) }
};

// 3. Tier-1 read pattern (replaces SQL LIKE/= on now-encrypted columns):
//    SELECT all rows matching non-sensitive predicates
//    → loop decrypt
//    → filter Rust-side .contains()/.eq() lowercase
//    → sort plaintext + take(N)
//    OK fino ~10k clienti per PMI target.
//    FIXME(S251): blind-index HMAC su telefono per Sara latency <800ms scale.
```

### cargo check su iMac

```
Finished `dev` profile [unoptimized + debuginfo] target(s) in 36.83s
0 errors, 15 pre-existing dead-code warnings.
SENSITIVE_FIELDS / is_sensitive_field warning ATTESO — saranno usati dalla migration helper Step D.
```

---

## S250 — Cosa fare (effort residuo ~3-4h)

**Tutti i passi sotto richiedono context <40%** (Step C + Step D = FILE CRITICI per S185-A).

### Step C — Setup hook in lib.rs (~1h, FILE CRITICO <40%)

**File**: `src-tauri/src/lib.rs` (NON modificato in S249).

**Goal**: chiamare `gdpr_auto_init_encryption` **DOPO** che `license_cache` è popolato (post setup wizard o trial trigger) e **PRIMA** della prima query CRUD.

**Strategia**:
- Inietta call nell'`.setup(|app| { ... })` di Tauri Builder, dopo migrations + license_cache check.
- Idempotent: `is_encryption_ready()` early-return evita double-init.
- Fallback graceful: se `license_cache` empty (cold start, prima del wizard), NON crashare. Gate runtime nei CRUD (`ensure_encryption_ready_pool`) li blocca finché wizard non completa.
- Logging: `log::info!("[GDPR] encryption initialized from license_cache (license_key={} fingerprint={})", masked_key, fingerprint_short);`.

**AC misurabili**:
- `cargo check` 0 errori
- Cold start (no license): app si avvia, dashboard mostra "Setup wizard required", no crash.
- Setup wizard completion → `auto_init_from_pool` chiamato → CRUD operativi.

### Step D — Migration runner (~2-3h, FILE CRITICO <40%)

**Goal**: cifrare in-place righe esistenti plaintext nella DB di sviluppo/produzione installata pre-S249.

**Files da creare**:
1. `src-tauri/migrations/00XX_encrypt_pii_at_rest.sql` — solo struttura (NO logica Rust, sqlx migration sequenziale).
2. `src-tauri/src/migrations/encrypt_pii.rs` — Rust runner che:
   - Pre-flight: `is_encryption_ready()` → se false, **abort** con messaggio chiaro
   - Backup: copia `app.db` → `app.db.pre-encryption-bak-{timestamp}` (deve esistere prima di tx)
   - Detect plaintext: query `SELECT id, nome FROM clienti WHERE nome IS NOT NULL LIMIT 1` → check Base64 pattern (length, alphabet)
   - Encrypt loop: per ogni cliente, encrypt 11 SENSITIVE_FIELDS in single TX (atomic), UPDATE WHERE id = ?
   - Counter: tot rows scanned, tot encrypted, tot skipped (già cifrati)
   - Idempotent: re-run su DB già cifrato = no-op
3. Trigger: chiamato post-Step C setup hook se `app.db` exists e contains plaintext.

**Rischi**:
- Crash mid-migration → row state inconsistente (alcune cifrate, altre no). Mitigation: TX per-row + counter persistito su file lock `.encryption-migration-progress.json`, resume capability.
- `fatture.cliente_*` snapshot columns NON cifrate (FIXME S251) → leak parziale. P1 per Step D' separato.

**AC misurabili**:
- Test su DB con 10 righe plaintext: tutte cifrate, decrypt round-trip OK.
- Test idempotent: 2nd run = 0 modified rows.
- Test crash simulation: kill -9 mid-migration → resume completa correttamente.

### Step E — E2E live (~30min, dipende C+D)

**Test cases**:
1. Fresh install + setup wizard + create cliente con telefono+email+CF → SELECT raw DB → verifica Base64 (NON plaintext).
2. Search "Mario" → trova cliente cifrato (tier-1 in-memory works).
3. Sara IPC POST `/clienti/search?q=339` → match by phone normalized, decrypt.
4. Export CSV GDPR Art. 20 → plaintext readable.
5. Migration su DB con 5 righe plaintext → tutte cifrate, no data loss.

**Comandi**:
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && cargo test --lib encryption:: 2>&1 | tail -20'
ssh imac 'curl -s -X POST http://127.0.0.1:3001/clienti/create -H "Content-Type: application/json" -d "{\"nome\":\"Mario\",\"cognome\":\"Rossi\",\"telefono\":\"3391234567\"}"'
ssh imac 'sqlite3 /Users/imac/Library/.../fluxion/app.db "SELECT nome, telefono FROM clienti LIMIT 3;"'  # verify Base64
```

### Step F (futuro S251) — Blind-index secondary

Per scalabilità >10k clienti + Sara latency <800ms: HMAC-SHA256 deterministic su telefono normalizzato → colonna indicizzata `telefono_bidx` per O(log n) lookup senza decifrare. Pattern: CipherSweet/CipherSafe approach. Out of scope S250.

---

## Vincoli context S250

- **Step C + D = FILE CRITICI** (`lib.rs` autoritativo, migration SQL+runner). Soglia hard `<40%` (S185-A).
- **Step E** = test, non file critico, OK 40-50%.
- Se context >40% all'inizio S250: chiudi pulito, schedule S250 mente fresca.

## Comando di start S250

```bash
# 1. Sync iMac
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && git pull origin master'
# 2. Verifica commit corrente
git log --oneline -1  # deve essere 0ed0e25 o successivo
# 3. /context per misurare baseline
# 4. Se <40% → procedere Step C
# 5. Se ≥40% → kill sessione, schedule mente fresca
```

## Riferimenti permanenti

- Decision Opt A master_password: `.claude/cache/agents/s248/master-password-flow-decision.md`
- 11 SENSITIVE_FIELDS list + tier classification: `src-tauri/src/encryption.rs` riga ~189
- Pattern wiring uniforme: vedi sezione "Pattern uniforme stabilito" sopra
- FIXME residui per S251: blind-index telefono + cifrare fatture.cliente_* snapshot columns
