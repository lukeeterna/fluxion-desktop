# Prompt ripartenza S261 — VERDE-CON-ASTERISCO close S260 (stash WIP)

**Generato**: 2026-05-18 (sessione S260 close auto ~61% context, vincolo #7 BLOCK_CRITICAL)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Last commit master**: `7c8ac00 docs(S259): close VERDE — P3.a UX toast cross-entity + P3.b audit next target`
**Stato**: VERDE-CON-ASTERISCO. Stash@{0} `S260-WIP-steps-3-4-5-partial` contiene 3 file modificati corretti, NON committati per evitare drift sopra 50% context.

---

## CONTEXT CLOSE S260 (perché chiusura auto)

Trigger: context al ~61% durante STEP 5 (refactor `update_impostazioni_fatturazione` con 21 parametri + merge plaintext/ciphertext). Vincolo #7 (`context-budget-gate.md`): sopra 50% **BLOCK_CRITICAL** su file con AC schema/migration/wiring (data_migration runner, lib.rs boot wiring, commands fatture XML SDI). Continuare = rischio drift su STEP 6 (audit), STEP 7 (test), STEP 8 (live verify iMac 8-point) tutti file-critici.

Decisione: chiusura VERDE-CON-ASTERISCO con stash WIP corretto preservato, ripartenza S261 con context fresco ≤25%.

---

## STATO TECNICO WIP (in stash@{0})

### File modificati nello stash (3 file)

1. **`src-tauri/src/data_migration.rs`** (STEP 3 + STEP 7-partial)
   - **DONE**: costanti `MIGRATION_KEY_IMPOSTAZIONI_FATTURAZIONE` + `ENCRYPTABLE_COLUMNS_IMPOSTAZIONI_FATTURAZIONE` (8 cols: `denominazione, partita_iva, codice_fiscale, indirizzo, telefono, email, pec, iban`)
   - **DONE**: wrapper `encrypt_impostazioni_fatturazione_pii(pool, db_path)` che invoca `encrypt_table_pii` generico (refactor S255)
   - **DONE**: docstring modulo aggiornato `* impostazioni_fatturazione — S260 (P4) — 8 sensitive columns`
   - **DONE**: aggiunto `CREATE TABLE impostazioni_fatturazione` minimale in `seed_minimal_schema` (per test futuro)
   - **TODO S261**: scrivere test `test_encrypt_impostazioni_fatturazione_pii_basic_and_idempotent` (pattern S255/S257), includere `seed_plaintext_impostazioni_fatturazione` (1 row singleton `id='default'`)

2. **`src-tauri/src/lib.rs`** (STEP 4)
   - **DONE**: block boot wiring tra `encrypt_operatori_pii` e `encrypt_suppliers_pii` aggiunto: stesso pattern (Ok already_applied / Ok report / Err sentry warn no-crash). Ordine canonico: `clienti → operatori → impostazioni_fatturazione → suppliers`.

3. **`src-tauri/src/commands/fatture.rs`** (STEP 5)
   - **DONE**: import `encrypt_field, decrypt_field, ensure_encryption_ready_pool`
   - **DONE**: helpers locali `encrypt_opt/encrypt_required/decrypt_opt/decrypt_required/decrypt_impostazioni_in_place` (mirror `commands/operatori.rs`)
   - **DONE**: `get_impostazioni_fatturazione` → `ensure_encryption_ready_pool` gate + fetch + `decrypt_impostazioni_in_place`
   - **DONE**: `update_impostazioni_fatturazione` → `ensure_encryption_ready_pool` gate + pre-encrypt 8 cols (`denominazione_ct/partita_iva_ct/...`) prima dell'UPDATE SQL
   - **VERIFICATO**: `sdi_provider_factory` (line ~344) query diretta `fattura24_api_key/aruba_api_key/openapi_api_key + sdi_provider` — NON tocca cols PII encrypted, SAFE no refactor.
   - **VERIFICATO**: 4 call sites `get_impostazioni_fatturazione` in XML SDI generation (`generate_xml_fattura` lines 592/879/986/1190) — tutti consumano return già decrypted, **path automatico**.

### Audit 4-point già verificato S260 (re-verify rapido S261)
- **Views**: ✓ NO views referencing `impostazioni_fatturazione` (grep migrations).
- **UNIQUE**: ✓ solo `PRIMARY KEY (id)`, no UNIQUE su PII cols (schema `007_fatturazione_elettronica.sql`).
- **LIKE**: ✓ NO `LIKE` queries on impostazioni cols.
- **FE types**: ✓ `src/types/fatture.ts::ImpostazioniFatturazioneSchema` invariato (BE ritorna plaintext post-decrypt).

### DB iMac stato (riferimento live verify)
- Row populated `id='default'`: `Automation Business | 02159940762 | DSTMGN81S12L738L | Via Roma 1 | (telefono/email/pec/iban tutti vuoti)`.
- Quindi runner S260 cifrerà SOLO 4 cols popolati: `denominazione/partita_iva/codice_fiscale/indirizzo`. Backup `fluxion.db.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-TS` atteso post-boot1.

---

## TASK S261 — Completare S260 P4 (~30-45 min)

### Pre-flight S261
```bash
cd /Volumes/MontereyT7/FLUXION
git stash list | head -1                              # expect "S260-WIP-steps-3-4-5-partial"
git log --oneline -1                                   # expect 7c8ac00 (S259 close)
git stash pop                                          # restore WIP 3 files
git status --short                                     # expect 3 src-tauri files modified
```

### STEP 7 — Test parallel
File `src-tauri/src/data_migration.rs` (già stash):
1. Aggiungere `seed_plaintext_impostazioni_fatturazione(pool)` helper: INSERT 1 row `id='default'` con 8 cols PII plaintext (`'Automation Business', '02159940762', 'DSTMGN81S12L738L', 'Via Roma 1', '3331234567', 'a@b.it', 'pec@pec.it', 'IT60X0542811101000000123456'`).
2. Aggiungere test `test_encrypt_impostazioni_fatturazione_pii_basic_and_idempotent` (mirror S257 suppliers test):
   - First run → `encrypted_rows == 1`, backup filename contains `encrypt_impostazioni_fatturazione_pii_v1`, round-trip decrypt 8 cols.
   - Second run → `already_applied == true`.
   - Cleanup db + backup + wal + shm.

### STEP 6 — Audit 4-point re-verify (rapido)
```bash
grep -rn "impostazioni_fatturazione" src-tauri/migrations/ | grep -i view  # expect empty
grep -n "UNIQUE" src-tauri/migrations/007_fatturazione_elettronica.sql      # expect no UNIQUE on PII cols
grep -rn "LIKE" src-tauri/src/commands/fatture.rs                           # expect empty
grep -n "ImpostazioniFatturazione" src/types/fatture.ts                     # expect invariato
```

### STEP 8 — Build + commit + sync + live verify
```bash
# 1. Type-check + cargo test (MacBook)
npm run type-check
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo test --manifest-path src-tauri/Cargo.toml --lib data_migration:: -- --nocapture"
# expect: 4 test PASS (clienti + operatori + suppliers + impostazioni_fatturazione)

# 2. Commit atomico
git add src-tauri/src/data_migration.rs src-tauri/src/lib.rs src-tauri/src/commands/fatture.rs
git commit -m "$(cat <<'EOF'
feat(S260 P4): encryption impostazioni_fatturazione PII — 8 cols (REGOLA #8)

Runner encrypt_impostazioni_fatturazione_pii_v1 (singleton id='default', 8 PII
cols: denominazione, partita_iva, codice_fiscale, indirizzo, telefono, email,
pec, iban). Pattern S255 replicato via generic encrypt_table_pii.

Wire lib.rs ordine: clienti → operatori → impostazioni_fatturazione → suppliers.

commands/fatture.rs: ensure_encryption_ready_pool gate + encrypt on update +
decrypt on get. XML SDI generator path (4 call sites) usa get_impostazioni_
fatturazione → decrypted automaticamente.

Audit 4-point PASS: no views, no UNIQUE on PII cols, no LIKE, FE types invariati.

Test test_encrypt_impostazioni_fatturazione_pii_basic_and_idempotent PASS (1 row
singleton + idempotency + backup filename embed migration_key).
EOF
)"

# 3. Push + iMac sync
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"

# 4. Live verify 8-point su iMac (boot pipeline FLUXION desktop app)
# 4.1 Boot1: log marker `🔐 PII migration (impostazioni_fatturazione): N rows encrypted`
# 4.2 Marker DB: SELECT * FROM encryption_migration_state WHERE migration_key='encrypt_impostazioni_fatturazione_pii_v1'
# 4.3 Backup file su disk: ls -la Library/Application*/com.fluxion.desktop/fluxion.db.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-*
# 4.4 Ciphertext on-disk: sqlite3 ... 'SELECT denominazione, partita_iva FROM impostazioni_fatturazione' → Base64
# 4.5 HTTP/IPC GET impostazioni → plaintext decrypted (Automation Business + 02159940762)
# 4.6 Boot2 idempotency: log "already applied" + DB byte-for-byte identità (md5 prima/dopo restart)
# 4.7 Form UI Impostazioni save→reload roundtrip (modificare campo telefono, salvare, riaprire)
# 4.8 XML SDI generation roundtrip: emettere fattura test → XML contiene plaintext `<Denominazione>Automation Business</Denominazione>` + `<IdCodice>02159940762</IdCodice>`
```

---

## RACCOMANDAZIONE PROCEDURALE S261 — start cold

1. **Apertura sessione fresca**: NON aprire altri file prima del pop. Context boot atteso ~18-22%.
2. **Pre-flight `pop` immediato**: prima azione `git stash pop`. Verificare i 3 file unstaged (expected from stash@{0}).
3. **STEP 7 PRIMA di STEP 6/8** (priorità inverted vs piano S260): test parallel valida correttezza runner senza dipendenza da iMac. Cargo test su MacBook = no SSH overhead.
4. **Live verify dopo commit+push+sync iMac**: protegge da rollback se problema scoperto in test.

---

## VINCOLI HARD (riconferma S261)

- **Vincolo #6** zero ARANCIONE: chiusura S260 = VERDE-CON-ASTERISCO (lavoro corretto in stash, master pulito, prompt resume completo). NON arancione.
- **Vincolo #7** context budget: S261 start ≤25% required. Se boot >30% → flag esplicito + scrutiny step.
- **Vincolo #8** (MEMORY REGOLA #8): audit 4-point PII encryption per table — già verificato S260, re-verify rapido S261.
- **Vincolo #9** (MEMORY REGOLA #9): test live = `license_cache` populated PRIMA. iMac post-S258 ha license attivata → OK.
- **REGOLA #5** sessione end: commit atomico + sync iMac OBBLIGATORI dopo STEP 7/STEP 8 verify.
- **REGOLA #6** NO trailer Co-Authored-By in commit (italian copy).

---

## PROMPT START S261 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S261:
recupera stash S260 P4 WIP (steps 3-4-5 DONE) e completa STEP 7 (test parallel),
STEP 6 (audit re-verify), STEP 8 (build + commit + iMac sync + live verify 8-point).

Pre-flight:
1. git stash list — expect stash@{0} "S260-WIP-steps-3-4-5-partial"
2. git stash pop — restore 3 src-tauri files
3. git status --short — expect 3 file modified
4. Context start expected ~18-22% (≤25% hard, fresh session window)

Sequenza S261:
STEP 7 test parallel (data_migration.rs: seed_plaintext_impostazioni_fatturazione +
test_encrypt_impostazioni_fatturazione_pii_basic_and_idempotent, mirror S257) →
STEP 6 audit 4-point re-verify rapido (4 grep) →
npm run type-check (MacBook) →
ssh imac cargo test data_migration:: (expect 4 PASS) →
git commit atomico (template in prompt.manual.md) →
git push + ssh imac git pull →
STEP 8 live verify 8-point su iMac (boot1 marker + ciphertext + backup +
decrypt path + boot2 idempotency + form UI roundtrip + XML SDI roundtrip).

CLOSE VERDE quando 8/8 live verify PASS. Update MEMORY.md S261 outcome +
HANDOFF + ROADMAP_REMAINING + commit docs(S261) close VERDE.
```

---

**Provenienza S260 close**: VERDE-CON-ASTERISCO @ context ~61% (vincolo #7 BLOCK_CRITICAL su STEP 6/7/8 file-critici). Stash WIP corretto preservato. Master pulito (7c8ac00). Prompt ripartenza completo per S261 fresh.
