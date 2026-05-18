# Prompt ripartenza S266 — STEP 8 XML SDI + Block B fattura test (founder GUI required)

## Stato chiusura S265 (commit `69a2f5f` master, MacBook+iMac fast-forward sync)

**VERDE-CON-ASTERISCO** — Block A STEP 5/6/7 + Block B schema = 4/5 AC PASS via SSH read-only. Backlog P1 toast UX cross-entity landed.

### Consegnato S265

1. ✅ **STEP 5 marker DB** — `encrypt_impostazioni_fatturazione_pii_v1` applied_at `2026-05-18 09:12:30` rows_processed=1
2. ✅ **STEP 6 backup file** — `fluxion.db.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-20260518-091230` (1.1M) presente
3. ✅ **STEP 7 raw ciphertext** — 4 cols (denominazione/partita_iva/codice_fiscale/indirizzo) Base64 ciphertext verified, NOT plaintext
4. ✅ **Block B schema** — 45 col + presenza confermata `imponibile_totale`, `totale_documento`, `sdi_id_trasmissione`, `note_interne`, `deleted_at`
5. ✅ **S265 P1 toast UX fix** — REGOLA #11 audit cross-entity `src/components/fatture/`:
   - `ImpostazioniFatturazioneDialog.tsx`: `toast.success('Impostazioni fatturazione salvate')` + `toast.error('Errore salvataggio impostazioni', {description})`
   - `FatturaDialog.tsx`: `toast.success('Fattura creata')` + `toast.error('Errore creazione fattura', {description})`
   - 0 errori type-check, lint PASS (17 warnings preesistenti e2e-tests)

### Già confermato live in S264 (founder GUI)
- ✅ STEP 7 UI roundtrip Impostazioni (read+write+persist post-restart) PASS

---

## TASK S266 — verifiche pending (founder GUI required)

### Block A STEP 8: XML SDI tag plaintext

REGOLA #12: requires founder physical action su iMac.

**Founder action sequence:**
1. App FLUXION UP via GUI (launchpad o `npm run tauri dev` da Terminal locale iMac)
2. Tab Fatture → "Nuova Fattura" → cliente esistente → 1 riga (descrizione + importo) → Salva
3. Su fattura emessa, generare XML SDI (pulsante "Genera XML" o "Invia SDI")
4. Aprire file XML generato

**Verifica AC STEP 8:**
- Tag `<CedentePrestatore>...<Anagrafica>...<Denominazione>Automation Business</Denominazione>` **plaintext** (NOT Base64)
- Tag `<IdCodice>02159940762</IdCodice>` plaintext
- Tag `<Sede><Indirizzo>...` plaintext

Comando SSH per verifica programmatica (post-generation):
```bash
ssh imac "find '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop' -name '*.xml' -newer /tmp/stamp 2>/dev/null | head -3"
# Poi inspect: grep -E '<Denominazione>|<IdCodice>|<Indirizzo>' <xml_file>
```

### Block B funzionale: fattura test creation/read

**Founder action:**
1. Crea 1 fattura test (cliente + 1 riga) → conferma toast `"Fattura creata"` (S265 P1 fix)
2. Lista fatture in tab Fatture → fattura appare con totale corretto
3. Modifica Impostazioni Fatturazione (es. cambia telefono) → conferma toast `"Impostazioni fatturazione salvate"` (S265 P1 fix)

**Verifica SSH post-action:**
```bash
ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' \"
  SELECT COUNT(*) as fatture_count FROM fatture;
  SELECT id, numero_completo, totale_documento, deleted_at FROM fatture LIMIT 3;
\""
```

### Block A boot2 idempotency (opzionale, già high-confidence da S262)

Founder chiude+riapre app:
```bash
# md5 DB (atteso: NON cambia tra restart non-data-mutating)
ssh imac "md5 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db'"
# log: cercare "🔐 PII migration (impostazioni_fatturazione): already applied"
```

---

## Acceptance Criteria S266

- [ ] **STEP 8 XML SDI**: tag `<Denominazione>` / `<IdCodice>` / `<Indirizzo>` plaintext in XML generato
- [ ] **Block B fattura test**: 1 fattura creata, lista renderizza, dati DB COUNT=1
- [ ] **S265 toast UX live**: founder vede toast verde "Fattura creata" + "Impostazioni fatturazione salvate"
- [ ] **Boot2 idempotency** (opzionale): log `already applied` per impostazioni_fatturazione

---

## Vincoli S266

- **Context budget**: S266 inizia ~17% boot. Verifica founder GUI + SSH read-only = headroom ampio.
- **Founder physical action required**: REGOLA #12. SE founder non disponibile in S266, scrivere handoff S267 preservando AC.
- **REGOLA #6**: NO Co-Authored-By Claude trailer in commit.
- **REGOLA #9**: STEP 5/6/7 + Block B schema già confermati S265 SSH read-only. Solo STEP 8 + fattura test funzionale pending.

---

## PROMPT START S266 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S266:

Step 1: chiedere founder "App FLUXION UP su iMac e disponibile per fattura test S266?"
  - SE NO → handoff S267, preserve AC.
  - SE SI → procedere.

Step 2 (Block B): founder crea fattura test → verifica toast "Fattura creata" (S265 P1)
  - SSH SELECT COUNT/id/numero_completo/totale_documento/deleted_at

Step 3 (Block A STEP 8): founder genera XML SDI dalla fattura test
  - SSH find XML file più recente
  - grep tag <Denominazione>/<IdCodice>/<Indirizzo> → plaintext atteso

Step 4 (S265 toast UX live): founder modifica telefono Impostazioni → toast "Impostazioni fatturazione salvate"

Step 5 (boot2 opzionale): founder chiude+riapre app
  - md5 stesso valore + log "already applied"

CLOSE VERDE se 3/4 AC PASS (boot2 opzionale).
Commit: docs(S266): close VERDE — S260 P4 STEP 8 + S263 Fatture funzionale live verify
```

---

**Provenienza S265 close**: VERDE-CON-ASTERISCO. STEP 5/6/7 + Block B schema PASS via SSH. S265 P1 toast cross-entity 2 sites fixed. Pending: founder GUI per STEP 8 XML SDI + Block B fattura test creation + toast UX live confirm.
