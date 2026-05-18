# Prompt ripartenza S264 — STEP 5-8 founder GUI live verify (S260 P4 impostazioni_fatturazione encryption) + verifica funzionale Fatture post-041

## Stato chiusura S263 (commit `8a68406` master)

**VERDE-CON-ASTERISCO** @ context 61% (BLOCK_CRITICAL preventive vincolo #7).

### Consegnato S263 — 4 fix atomici

1. ✅ **BUG-FATT-1 TabsContent wrap** — `ImpostazioniFatturazioneDialog.tsx` `</Tabs>` spostato (riga 415→464). 4° TabsContent SDI era orphan. Bilanciamento verificato.
2. ✅ **BUG-FATT-2 Migration 041** — DROP+RECREATE fatture/righe/riepilogo/pagamenti (45 col allineate a `Fattura` struct Rust). Verificato live 0 righe iMac → zero data loss.
3. ✅ **Gate idempotency 041** — Rust `pragma_table_info('fatture') WHERE name='deleted_at'` skip se già allineato. NO drop al 2° boot.
4. ✅ **Clinic 1 Settore + rename UI** — `LicenseManager.tsx` + `license-ed25519.ts` + `setup.ts` + `SchedaClienteDynamic.tsx`. Grep `nicchia|nicchie` → 0 match user-facing.

### Verifica S263
- `npx tsc --noEmit` 0 errori (MacBook)
- `cargo check` 0 errori 15 warnings preesistenti (iMac)
- `cargo test data_migration::` 4/4 PASS (suite encryption non toccata)
- Lint pre-commit PASS
- Sync iMac fast-forward `c30a99c..8a68406`

---

## TASK S264 — 2 verifiche pending

### Block A: STEP 5-8 live verify S260 P4 impostazioni_fatturazione encryption (founder GUI required)

REGOLA #12: SSH `cargo-tauri tauri dev` blocca su Keychain `User interaction is not allowed`. **Founder DEVE lanciare app fisicamente da iMac** (launchpad → Fluxion oppure `npm run tauri dev` da Terminal locale).

**Sequenza S264 Block A:**

1. **Pre-check stato pre-launch (SSH):**
   ```bash
   ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' \"
     SELECT 'pre-state impostazioni_fatturazione:';
     SELECT denominazione, partita_iva, codice_fiscale FROM impostazioni_fatturazione;
     SELECT 'markers attivi:'; SELECT migration_key, applied_at, rows_processed FROM encryption_migration_state ORDER BY applied_at;
     SELECT 'fatture col count:'; SELECT COUNT(*) FROM pragma_table_info('fatture');
     SELECT 'deleted_at exists:'; SELECT COUNT(*) FROM pragma_table_info('fatture') WHERE name='deleted_at';
   \""
   ```

2. **Founder action**: launch app via GUI iMac. Mantenere aperta.

3. **Post-boot1 verifica STEP 5/6/7/8 (SSH):**
   ```bash
   # STEP 5 — marker DB encrypt_impostazioni_fatturazione_pii_v1 row inserita
   ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' \"SELECT * FROM encryption_migration_state WHERE migration_key='encrypt_impostazioni_fatturazione_pii_v1';\""

   # STEP 6 — backup file su disk
   ssh imac "ls -lh '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/' | grep pre-encrypt_impostazioni_fatturazione"

   # STEP 7 — raw ciphertext Base64 su 4 cols populated
   ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' 'SELECT denominazione, partita_iva, codice_fiscale, indirizzo FROM impostazioni_fatturazione;'"
   # atteso: Base64 (~24+ char per col) NOT plaintext "Automation Business"

   # STEP 8 — HTTP bridge decrypt path
   curl -s http://192.168.1.2:3001/api/impostazioni_fatturazione/get | jq .
   # atteso: plaintext "Automation Business" / "02159940762" / "DSTMGN81S12L738L"
   ```

4. **Boot2 idempotency**: founder chiude e riapre app. Verifica:
   ```bash
   # md5 DB byte-for-byte
   ssh imac "md5 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db'"
   # log app: cercare "🔐 PII migration (impostazioni_fatturazione): already applied"
   ```

5. **STEP 7-8 funzionali (founder action GUI)**:
   - Apri Impostazioni → modifica telefono → salva → chiudi app → riapri → verifica persistenza (encrypt write + decrypt read)
   - Crea fattura test → genera XML SDI → ispeziona file XML → atteso `<Denominazione>Automation Business</Denominazione>` + `<IdCodice>02159940762</IdCodice>` plaintext nei tag

### Block B: Verifica funzionale Fatture post-migration 041

Dopo founder GUI launch (Block A), verificare i 2 bug Fatture S263 fixati:

1. **BUG-FATT-1 (TabsContent)**: aprire pagina Fatture → NO ErrorBoundary. Cliccare "Impostazioni Fatturazione" → dialog apre con 4 tab cliccabili (Azienda/Fiscale/Banca/SDI). Ogni tab deve mostrare contenuto.

2. **BUG-FATT-2 (deleted_at)**: lista fatture deve caricare (anche se vuota, 0 risultati OK no errore "no such column").

3. **Schema verify post-migration 041**:
   ```bash
   ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' \"SELECT COUNT(*) FROM pragma_table_info('fatture'); SELECT name FROM pragma_table_info('fatture') WHERE name IN ('imponibile_totale','deleted_at','sdi_id_trasmissione','note_interne');\""
   # atteso: COUNT=45 + 4 nomi attesi presenti
   ```

4. **Creare 1 fattura test (founder GUI)**: nuova fattura → cliente esistente → 1 riga → salva → emessa. Verifica DB:
   ```bash
   ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' 'SELECT COUNT(*) FROM fatture; SELECT id, numero_completo, totale_documento, deleted_at FROM fatture LIMIT 1;'"
   ```

---

## Acceptance Criteria S264

### Block A (S260 P4 live verify)
- [ ] STEP 5 marker DB inserito boot1
- [ ] STEP 6 backup file `.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-*` esiste
- [ ] STEP 7 raw 4 cols Base64 ciphertext, HTTP bridge restituisce plaintext
- [ ] STEP 8 boot2 `already applied` + md5 idempotency
- [ ] UI roundtrip telefono persiste
- [ ] XML SDI tag plaintext

### Block B (S263 funzionale Fatture)
- [ ] Tab Fatture rendera senza ErrorBoundary
- [ ] Lista fatture carica (anche vuota)
- [ ] Dialog Impostazioni Fatturazione 4 tab funzionanti
- [ ] Schema 45 col + deleted_at presente
- [ ] Fattura test creabile e leggibile

---

## Vincoli S264

- **Context budget**: S264 inizia ~17% boot. Block A+B sono **read-only verify**, no edit critici. Headroom ampio per investigare eventuali nuovi bug.
- **Founder physical action required**: REGOLA #12. Block A STEP 5/6/7/8 + Block B fattura test richiedono GUI iMac.
- **MAI revert encryption** (REGOLA implicita): 4 runner attivi, marker DB e backup safe-deposit.
- **REGOLA #10**: output verificato > verosimile. Se founder non disponibile per GUI launch in S264, scrivere handoff S265 con Block A/B preserved.

---

## PROMPT START S264 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S264:

Step 1: chiedere founder "App FLUXION attualmente UP su iMac via GUI?"
  - SE NO → bloccare. Founder DEVE relaunch fisicamente. Spiegare REGOLA #12.
  - SE SI → procedere.

Step 2 (Block A): SSH pre-check stato + post-boot1 verifica STEP 5/6/7/8
  - sqlite3 marker encrypt_impostazioni_fatturazione_pii_v1
  - ls backup file .pre-encrypt_impostazioni_fatturazione_pii_v1-bak-*
  - sqlite3 raw 4 cols → Base64 ciphertext atteso
  - curl /api/impostazioni_fatturazione/get → plaintext decrypted
  - md5 boot1 baseline

Step 3 (Block A boot2): founder chiude+riapre app
  - md5 DB stesso valore boot1
  - log "already applied"

Step 4 (Block A funzionale): founder UI roundtrip telefono + fattura test XML SDI

Step 5 (Block B): verify Fatture page renders, Impostazioni dialog 4 tab, schema 45 col

CLOSE VERDE se tutti AC PASS.
Commit unico: docs(S264): close VERDE — S260 P4 live verify 8/8 + S263 Fatture funzionale OK
```

---

**Provenienza S263 close**: VERDE-CON-ASTERISCO @ context 61%. 4 fix atomici landed + sync + cargo test 4/4 PASS. Pending: founder GUI launch per chiudere live verify S260 P4 + funzionale Fatture S263.
