# S249 — Cat 3 P0 #2 Wiring encryption CRUD clienti + migration + E2E

**Generato**: 2026-05-16 fine S248 (CLOSED GREEN — commit `da5475d`)
**Repo**: master `da5475d` (MacBook + iMac sync OK, cargo check ✅ 0 errori)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.

## S248 — Cosa è stato chiuso

**Tutti i task documentazione + decision + step A landed** in commit `da5475d`:

### Task 1 — D3 docs update (CLOSED ✅)
- `CLAUDE.md` riga 263: "6 macro x 17 sotto-verticali" → "8 macro x 50 micro-verticali" + lista macro
- `PRD-FLUXION-COMPLETE.md` riga 151: 6→8 macro, "40+ micro" → "50 micro"
- VOS canonical `~/venture-os/wiki/projects/FLUXION/DECISIONS.md`: nuova entry **D-04** riconcilia count vs D-01 (D-01 storica intatta)
- Verifica codice: `MICRO_CATEGORIE` in `src/types/setup.ts` = medico 10 + beauty 7 + hair 6 + auto 7 + wellness 6 + professionale 5 + pet 4 + formazione 5 = **50**

### Task 2 — Master password flow decision (CLOSED ✅)
- **Scelta: Opzione A** zero-friction, deterministic
- `master_password` = `license_cache.license_key` (immutable post-Stripe activation)
- `device_id` = `license_cache.fingerprint` (SHA-256 hardware, S015)
- Fallback trial pre-activation: `license_key=fingerprint`
- Recovery: ri-attivazione licenza su stesso device → key deterministica
- Edge case license_key change post-attivazione: **rotation command** richiesto pre-Stripe live (S250+)
- Razionale completo + critica strutturale 4-punti + pseudo-rust implementazione:
  `.claude/cache/agents/s248/master-password-flow-decision.md` (188 righe)

### Task 3 step A — Auto-init Tauri command + lazy guard (CLOSED ✅)
Modifiche in `src-tauri/src/encryption.rs` (commit `da5475d`):
- **New** `#[tauri::command] pub async fn gdpr_auto_init_encryption(state)` — legge `license_cache (license_key, fingerprint)`, deriva PBKDF2 input via S247 keychain salt, idempotent su OnceLock già init.
- **New** `pub async fn ensure_encryption_ready(state)` — lazy guard async per code paths CRUD.
- Registrato in `lib.rs` invoke_handler (single-line).
- `cargo check` su iMac: **0 errori**, `ensure_encryption_ready never used` warning atteso (chiamato da S249 step B).

### Task 4 — Sentry DSN (DEFERRED ⏭)
Bloccato founder action: aspetta nuovo trial account email + DSN + auth token. Quando arriva, vedi Task 4 in `.claude/cache/agents/s248/master-password-flow-decision.md` sezione Sentry tracing per strumentazione consigliata.

---

## S249 — Cosa fare

**Effort residuo Task 3**: ~7-11h. Multi-commit atomic. Tutti i passi qui sotto **richiedono context <40%** (file critici).

### Step B — Wiring encryption nel CRUD clienti (~3-4h)

**File**: `src-tauri/src/commands/clienti.rs` (381 righe, già letto S248).

**Helper preliminare** (in cima al file, dopo `use`):
```rust
use crate::encryption::{encrypt_field, decrypt_field, ensure_encryption_ready};

/// Encrypt the 11 SENSITIVE_FIELDS in an Option<String>. Empty/None passes through.
fn encrypt_opt(v: &Option<String>) -> Result<Option<String>, String> {
    match v {
        Some(s) if !s.is_empty() => Ok(Some(encrypt_field(s)?)),
        _ => Ok(v.clone()),
    }
}
fn encrypt_required(v: &str) -> Result<String, String> {
    if v.is_empty() { Ok(String::new()) } else { encrypt_field(v) }
}
fn decrypt_opt(v: &Option<String>) -> Result<Option<String>, String> {
    match v {
        Some(s) if !s.is_empty() => Ok(Some(decrypt_field(s)?)),
        _ => Ok(v.clone()),
    }
}
fn decrypt_cliente_in_place(c: &mut Cliente) -> Result<(), String> {
    c.nome = decrypt_field(&c.nome)?;
    c.cognome = decrypt_field(&c.cognome)?;
    c.telefono = decrypt_field(&c.telefono)?;
    c.email = decrypt_opt(&c.email)?;
    c.data_nascita = decrypt_opt(&c.data_nascita)?;
    c.indirizzo = decrypt_opt(&c.indirizzo)?;
    c.cap = decrypt_opt(&c.cap)?;
    c.citta = decrypt_opt(&c.citta)?;
    c.codice_fiscale = decrypt_opt(&c.codice_fiscale)?;
    c.partita_iva = decrypt_opt(&c.partita_iva)?;
    c.pec = decrypt_opt(&c.pec)?;
    Ok(())
}
```

**Campi SENSITIVE (11)** già definiti `encryption::SENSITIVE_FIELDS`:
`nome, cognome, telefono, email, codice_fiscale, partita_iva, indirizzo, cap, citta, pec, data_nascita`

**NON cifrare**: `id, soprannome, provincia, codice_sdi, note, tags, fonte, consenso_*, loyalty_*, *_at`.
(Razionale: soprannome è alias pubblico WhatsApp, provincia=2 lettere low-entropy, codice_sdi business non-PII, note può contenere PII ma è free-text large field → trade-off ricerca LIKE vs encryption → defer P1; in S249 lasciare plaintext con commento `// FIXME(S250): valutare encrypt note se contiene PII`.)

**Patch funzione per funzione**:

1. `get_clienti` (line 116) — dopo `fetch_all`, ciclo `for c in &mut clienti { decrypt_cliente_in_place(c)?; }`. Aggiungere `ensure_encryption_ready(&state).await?` in cima.
2. `get_cliente` (line 133) — dopo `fetch_one`, `decrypt_cliente_in_place(&mut cliente)?`. Aggiungere guard.
3. `create_cliente` (line 153) — prima di `INSERT`, cifrare ogni campo:
   ```rust
   ensure_encryption_ready(&state).await?;
   let nome_enc = encrypt_required(&input.nome)?;
   let cognome_enc = encrypt_required(&input.cognome)?;
   let tel_enc = encrypt_required(&input.telefono)?;
   let email_enc = encrypt_opt(&input.email)?;
   // ... etc per 11 campi
   ```
   Poi `.bind(&nome_enc).bind(&cognome_enc)...`. Dopo `get_cliente()` per return, decryption avviene automatica.
4. `update_cliente` (line 207) — idem create. Attenzione: `cliente_before` per audit deve essere **plaintext** (perché viene già decifrato in `get_cliente`). `cliente_after` idem.
5. `delete_cliente` (line 274) — non tocca campi, solo audit. `cliente_before` già plaintext. OK no changes.
6. `gdpr_hard_delete_cliente` (line 304) — query interna NON usa `get_cliente`, ma rilegge raw. Aggiungere `decrypt_cliente_in_place` per log audit corretto.
7. `search_clienti` (line 351) — **PROBLEMA NOTO**: `LIKE '%query%'` su campi cifrati = ZERO match. Mitigation tier-1: chiamare `decrypt_cliente_in_place` su risultati e filtrare in-memory (perf OK fino a ~10k clienti per piccola PMI). Tier-2 (S251+): blind-index colonne separate (HMAC del campo lowercase trimmed). Per S249 implementare tier-1 con commento `FIXME(S251): blind-index search per scalabilità`.

**Audit pattern post-step-B**:
- 11 campi cifrati ogni write
- Decifrati ogni read (tier 1 in-memory, OK piccole PMI)
- `consenso_*`, `note`, `provincia`, `codice_sdi` plaintext (con FIXME su `note` per S250)
- Search degraded a in-memory filter post-decrypt

### Step C — Setup hook lib.rs (~1h, FILE CRITICO context <40%)

**File**: `src-tauri/src/lib.rs` riga 592 setup hook.

Aggiungere **dopo** `init_database` ma **prima** `auto-backup`:
```rust
// S249 Cat 3 P0 #2 — Auto-init GDPR encryption from license_cache.
// Non-fatal if license_cache not yet populated (first run): the lazy guard
// in CRUD code paths (ensure_encryption_ready) retries on first sensitive op.
{
    let app_handle = app.handle().clone();
    tauri::async_runtime::spawn(async move {
        if let Some(state) = app_handle.try_state::<crate::AppState>() {
            match crate::encryption::gdpr_auto_init_encryption(state).await {
                Ok(_) => println!("🔐 GDPR encryption ready (license-derived key)"),
                Err(e) => eprintln!("⚠️  GDPR encryption deferred (setup not complete): {}", e),
            }
        }
    });
}
```

**Critica**: spawn separato dal database init (block_on) per non bloccare startup. Se `license_cache` vuota (primissimo run pre-wizard), il deferral è atteso.

### Step D — Migration SQL + Rust runner (~2-3h, FILE CRITICO)

**File nuovo**: `src-tauri/migrations/0XX_encrypt_existing_clienti.sql` (assegna N successivo, controlla `ls migrations/`).

Migration **NON può cifrare in pure SQL** (la chiave PBKDF2 vive in Rust OnceLock). Quindi:
- SQL = solo marker/idempotency table:
  ```sql
  CREATE TABLE IF NOT EXISTS encryption_migration_state (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      version TEXT NOT NULL,
      migrated_at TEXT NOT NULL,
      rows_processed INTEGER NOT NULL DEFAULT 0
  );
  ```
- Rust runner in `src-tauri/src/migrations.rs` (o new module `encryption_migration.rs`): chiamato dopo `init_database` E dopo `gdpr_auto_init_encryption`, dentro atomic transaction:
  ```rust
  pub async fn migrate_clienti_to_encrypted(pool: &SqlitePool) -> Result<u64, String> {
      // Skip if already done
      if let Ok(_) = sqlx::query_scalar::<_, String>(
          "SELECT version FROM encryption_migration_state WHERE id = 1"
      ).fetch_one(pool).await {
          return Ok(0);
      }
      // Backup pre-migration
      // 1. cp fluxion.db -> fluxion.db.pre-encryption-backup-<ts>
      // 2. BEGIN TRANSACTION
      // 3. SELECT * FROM clienti WHERE deleted_at IS NULL
      // 4. for each row: if !looks_encrypted(nome) { encrypt all sensitive, UPDATE row }
      // 5. INSERT INTO encryption_migration_state ('v1', now(), count)
      // 6. COMMIT
      // 7. on Err: ROLLBACK + restore backup
  }
  ```
- `looks_encrypted` heuristic: campo Base64 + length > NONCE_SIZE = già cifrato (idempotent re-run safe).

**Edge case critico**: utenti con DB esistente avranno 10 clienti (vedi `clienti=10` da brief mattutino) → migration **DEVE** girare prima del primo CRUD post-update altrimenti decryption fallisce su plaintext.

### Step E — E2E test su iMac (~1h)

```bash
# 1. Build
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH=\$HOME/.cargo/bin:\$PATH && cd src-tauri && cargo test --lib encryption:: 2>&1 | tail -20"

# 2. Live test via HTTP Bridge (porta 3001)
# Start dev: ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run tauri dev" &
# In altro tab:
curl -X POST http://192.168.1.2:3001/api/clienti \
  -H "Content-Type: application/json" \
  -d '{"nome":"Mario","cognome":"Rossi","telefono":"3331234567"}'

# 3. Verifica raw DB SQLite (campo nome deve essere Base64, NON "Mario")
ssh imac "sqlite3 '/Volumes/MacSSD - Dati/fluxion/src-tauri/fluxion.db' \"SELECT nome, cognome, telefono FROM clienti WHERE nome NOT LIKE 'Mario' LIMIT 5;\""

# 4. Read back
curl http://192.168.1.2:3001/api/clienti
# → JSON con nome="Mario" (decifrato)

# 5. Format E2E in HANDOFF S249-END.md:
# OK [GDPR-CRYPTO] [CREATE_CLIENTE]: Mario Rossi → DB: Base64 encrypted (encryption.rs)
# OK [GDPR-CRYPTO] [READ_CLIENTE]: Base64 → "Mario Rossi" (decryption.rs)
```

## Vincoli S249 (PERMANENTI)

- **Context budget**: Step C+D edit file critici → richiede **<40%**. Se context entra in BLOCK_CRITICAL prima di Step C/D, chiudi VERDE su step B solo e handoff S250.
- **Atomic commits**: ogni step un commit separato per rollback granulare.
- **Test E2E obbligatorio** prima di task completato (rule e2e-testing.md).
- **Zero costi** (nessuna nuova dipendenza, aes-gcm + keyring + pbkdf2 + base64 + rand + sha2 già in Cargo.toml).
- **Backup pre-migration** obbligatorio (Step D).

## Comando ripartenza S249

```bash
cd /Volumes/MontereyT7/FLUXION
git log -1 --format="%h %s"
# Atteso: da5475d feat(S248): gdpr_auto_init_encryption + decision A (license_key+fingerprint)

# Verifica context attuale prima di toccare file critici (Step C/D)
# Se >40%: limitarsi a Step B (clienti.rs CRUD wiring), poi handoff.

cat .claude/cache/agents/s248/master-password-flow-decision.md  # blueprint Task 3
cat .claude/NEXT_SESSION_PROMPT.manual.md                       # questo file

# Step B (clienti.rs wiring, file non-critico): può partire fino al 50%
# Step C (lib.rs setup hook, FILE CRITICO): solo <40%
# Step D (migration SQL+runner, FILE CRITICO): solo <40%
# Step E (E2E iMac): SSH live test post-fix

# Build verification
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH=\$HOME/.cargo/bin:\$PATH && cargo check 2>&1 | tail -10"
```

## Roadmap pre-launch restante (post-S248)

| Fase | Cat | Effort | Stato |
|------|-----|--------|-------|
| B | 3 P0 #1 salt keychain | ~3h | ✅ S247 done |
| B | 3 P0 #2 step A auto_init command | ~1h | ✅ S248 done |
| B | 3 P0 #2 step B-E wiring+migration+E2E | ~7-11h | ⏭ S249 |
| B | 3 P0 #3 CSP Tauri | ~2h | pending |
| B | 3 P0 #4 cargo audit CI | ~2h | pending |
| B | 3 P0 #5 HTTP Bridge auth | ~3-4h | pending |
| B | 4 P0 ipc_bench live | ~1h | pending |
| B | 5 P0 #1-#5 GDPR/FatturaPA | ~14-20h | pending |
| C | 1 Build/Distribution 8 P0 | ~12-16h | pending |
| C | 2 Functional E2E 7 P0 | ~30-50h | pending (post D1/D2 fix) |
| C | 6 Customer Success 5 P0 | ~12-17h | pending |
| D | Pre-launch validation | ~8-12h | pending |

**Totale residuo**: ~74-97h sequential (~57-72h con 2 stream paralleli).

## Stato repo fine S248

- Commit `da5475d` pushed origin/master, iMac sync OK
- `cargo check` su iMac: 0 errori, 16 warnings (tutti pre-esistenti + `ensure_encryption_ready never used` atteso)
- Pipeline iMac DOWN_OK
- Cat 3 P0 #2 step A ✅ done; step B-E ⏭ S249
- Tech debt minore: `tools/VectCutAPI` dirty submodule (ignorato)

## Vincoli mantenuti S248

- Verifica fattuale: `MICRO_CATEGORIE` count letto direttamente in codice, non a memoria
- Una raccomandazione singola: Opt A scelta con critica strutturale 4-punti
- Zero `--no-verify`, zero workaround
- Pattern recognition S185-A: NON tentato Task 3 completo (10-15h, file critici) in singola sessione
- Onestà: cargo check single-line registration NO controindicata, ma wiring CRUD + setup hook + migration DEFERRED esplicitamente
