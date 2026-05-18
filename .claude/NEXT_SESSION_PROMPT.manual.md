# Prompt ripartenza S262 — VERDE-CON-ASTERISCO close S261 (live verify pending GUI launch)

**Generato**: 2026-05-18 (sessione S261 close ~46% context, vincolo #7 BLOCK_CRITICAL preventive su update file critici)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Last commit master**: `caf2dd9 feat(S260 P4): encryption impostazioni_fatturazione PII — 8 cols (REGOLA #8)`
**Stato**: VERDE-CON-ASTERISCO. Code+tests+audit shipped, **live verify 8-point pending founder GUI launch iMac** (Keychain encryption gate richiede sessione GUI interattiva — SSH `User interaction is not allowed`).

---

## OUTCOME S261 (consegnato)

- **Commit atomico** `caf2dd9` master MacBook+iMac fast-forward sync:
  - `src-tauri/src/data_migration.rs` — runner `encrypt_impostazioni_fatturazione_pii` via `encrypt_table_pii` generic, 8 cols PII (denominazione/partita_iva/codice_fiscale/indirizzo/telefono/email/pec/iban). Test `test_encrypt_impostazioni_fatturazione_pii_basic_and_idempotent` PASS.
  - `src-tauri/src/lib.rs` — wire ordine `clienti → operatori → impostazioni_fatturazione → suppliers` (gated `is_encryption_ready()`).
  - `src-tauri/src/commands/fatture.rs` — `ensure_encryption_ready_pool` gate + encrypt on update + decrypt on get + helpers + XML SDI path (4 call sites `generate_xml_fattura`) auto-decrypt.
- **Cargo test data_migration:: 4/4 PASS** su iMac (clienti+operatori+impostazioni_fatturazione+suppliers).
- **Type-check 0 errori** MacBook.
- **Audit 4-point** re-verify PASS (no views, no UNIQUE su PII cols, no LIKE in fatture.rs, FE types `ImpostazioniFatturazioneSchema` invariati).

---

## LIVE VERIFY PENDING — perché non eseguibile da remoto

SSH-launched `cargo-tauri tauri dev` riproduce:
```
ℹ️  GDPR encryption deferred (CRUD will retry on first sensitive call):
   Keychain read failed: Platform secure storage failure:
   User interaction is not allowed.
```
Tutti i 4 runner encrypt skippano il gate `is_encryption_ready()` perché Keychain richiede sessione GUI interattiva utente. iMac via SSH non ha contesto Keychain unlock.

**Lezione PERMANENTE S261 (candidata REGOLA #12)**: live verify migration encryption-gated da Keychain RICHIEDE app launch via GUI utente. SSH/headless non possibile.

---

## STATO DB iMAC (pre-live-verify)

```
encryption_migration_state:
  encrypt_clienti_pii_v1            2026-05-16 19:38:55  rows=30  (founder GUI boot precedente)
  encrypt_operatori_pii_v1          2026-05-16 20:16:37  rows=2   (founder GUI boot precedente)
  encrypt_suppliers_pii_v1          2026-05-18 07:54:31  rows=3   (founder GUI boot precedente)
  encrypt_impostazioni_fatturazione_pii_v1   PENDING

impostazioni_fatturazione (plaintext):
  id='default' | denominazione='Automation Business' | partita_iva='02159940762' |
  codice_fiscale='DSTMGN81S12L738L' | indirizzo='Via Roma 1' |
  telefono='' | email='' | pec='' | iban=''
```

Runner attesa: cifra 4 cols popolati (denominazione/partita_iva/codice_fiscale/indirizzo). Le 4 cols vuote pass-through (empty string non encrypted, già verificato in test S257).

---

## TASK S262 — Live verify 8-point post-founder-GUI-launch

### Prerequisito (founder action)
Founder lancia FLUXION desktop app sull'iMac fisicamente:
```bash
# Su iMac (terminale fisico, NON SSH)
cd "/Volumes/MacSSD - Dati/FLUXION"
npm run tauri dev
# OPPURE binary già compilato: open target/debug/tauri-app
```

Aspettativa log boot1 (terminal iMac founder):
```
🔐 GDPR encryption auto-initialized from license_cache
🔐 PII migration (clienti): already applied (encrypt_clienti_pii_v1)
🔐 PII migration (operatori): already applied (encrypt_operatori_pii_v1)
🔐 PII migration (impostazioni_fatturazione): 1 rows encrypted, 0 already ciphertext,
   backup at /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-<YYYYMMDD-HHMMSS>
🔐 PII migration (suppliers): already applied (encrypt_suppliers_pii_v1)
```

### Live verify checklist 8-point (Claude esegue da SSH dopo founder ack)

```bash
# 1. Boot1 marker DB inserito
ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' \"SELECT migration_key, applied_at, rows_processed, backup_path FROM encryption_migration_state WHERE migration_key='encrypt_impostazioni_fatturazione_pii_v1';\""
# expect: 1 row con rows_processed=1 + backup_path populated

# 2. Backup file su disk
ssh imac "ls -la '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/' | grep encrypt_impostazioni_fatturazione"
# expect: 1 file .pre-encrypt_impostazioni_fatturazione_pii_v1-bak-<TS>

# 3. Ciphertext on-disk (raw sqlite3)
ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' 'SELECT denominazione, partita_iva, codice_fiscale, indirizzo FROM impostazioni_fatturazione;'"
# expect: 4 valori Base64 ciphertext (NON 'Automation Business' etc.)

# 4. Decrypt path roundtrip (HTTP Bridge /api/impostazioni o IPC get_impostazioni_fatturazione)
ssh imac "curl -s http://127.0.0.1:3001/api/<TBD>"
# OPPURE Tauri IPC via UI: aprire Impostazioni e verificare denominazione='Automation Business' etc.

# 5. Boot2 idempotency log
# Founder restart app → atteso log "PII migration (impostazioni_fatturazione): already applied"

# 6. DB md5 byte-for-byte pre/post boot2
ssh imac "md5 -q '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db'"
# pre-boot2 vs post-boot2 → expect identico (idempotency)

# 7. Form UI Impostazioni save→reload roundtrip
# Founder: apre tab Impostazioni → modifica telefono = '3331234567' → salva → riapre app → verifica '3331234567' presente
# Sotto al cofano: write encrypt → read decrypt → identità

# 8. XML SDI generation roundtrip
# Founder: emette fattura test → verifica XML output contains:
#   <Denominazione>Automation Business</Denominazione>
#   <IdCodice>02159940762</IdCodice>
#   <CodiceFiscale>DSTMGN81S12L738L</CodiceFiscale>
#   <Indirizzo>Via Roma 1</Indirizzo>
# (plaintext nel file XML output, decrypted prima della serializzazione)
```

### CLOSE VERDE quando 8/8 PASS

Update finale:
- MEMORY.md: stato S262 outcome live verify 8/8 PASS
- HANDOFF.md: completare backlog encryption (next P5 = `fatture` denorm snapshot 0 row, P6 = `messaggi_whatsapp`)
- Commit `docs(S262): close VERDE — S260 P4 impostazioni_fatturazione live verify 8/8 PASS`

---

## VINCOLI HARD S262

- **Vincolo #6** zero ARANCIONE: chiusura VERDE solo dopo 8/8 live verify PASS, altrimenti VERDE-CON-ASTERISCO con discrepanza esplicita.
- **Vincolo #7** context budget S262: live verify = mostly SSH commands + assertions → low risk, può procedere fino a ~50%.
- **REGOLA #11 cross-entity audit (S258)**: pattern PII encryption per table sta accumulando — dopo `impostazioni_fatturazione` valutare se serve helper più alto-livello per next batch (`fatture` denorm, `messaggi_whatsapp`).
- **REGOLA #12 candidate (S261)**: live verify encryption-gated migration = founder GUI launch mandatory. Documentare in `feedback_live_verify_keychain_gui_required.md` se replicato in S262.

---

## PROMPT START S262 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S262:
live verify 8-point S260 P4 impostazioni_fatturazione encryption post-founder-GUI-launch.

Pre-flight:
1. CHIEDERE FOUNDER: "App FLUXION desktop attualmente in esecuzione su iMac via GUI?
   (Keychain unlock richiede sessione interattiva utente)"
2. SE NO → guidare founder a lanciare `npm run tauri dev` su iMac fisicamente
3. SE SI → procedere con verifiche 8-point

Sequenza S262:
STEP 1 ssh imac sqlite3 → marker encrypt_impostazioni_fatturazione_pii_v1 present
STEP 2 ssh imac ls → backup file .pre-encrypt_impostazioni_fatturazione_pii_v1-bak-* present
STEP 3 ssh imac sqlite3 → ciphertext on-disk 4 cols populated
STEP 4 HTTP/IPC get_impostazioni → plaintext decrypted roundtrip
STEP 5 boot2 founder restart → atteso "already applied"
STEP 6 md5 pre/post boot2 → byte identico
STEP 7 form UI roundtrip (founder modifica telefono, salva, riapre)
STEP 8 XML SDI fattura test → plaintext nei tag XML

CLOSE VERDE se 8/8 PASS. Commit docs(S262) close VERDE.
Update MEMORY.md outcome S262, HANDOFF backlog encryption next P5/P6.
```

---

**Provenienza S261 close**: VERDE-CON-ASTERISCO @ context ~46% (BLOCK_CRITICAL preventive). Code+tests+audit shipped, gate live verify environmental (GUI Keychain access).
