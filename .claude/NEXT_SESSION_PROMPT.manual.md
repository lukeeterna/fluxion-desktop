# Prompt ripartenza S267 — STEP 8 XML SDI + BUG-FATT-3 lista totale zero + S265 toast Impostazioni live

## Stato chiusura S266 (NO new commit, master `b904353` MacBook+iMac fast-forward sync già pre-S266)

**VERDE-CON-ASTERISCO** — toast S265 P1 fix CONFIRMED LIVE + 1 fattura test creata DB OK + BUG-FATT-3 nuovo scoperto. Founder fatigue → chiusura strutturata preservando 3 AC pending.

### Consegnato S266
1. ✅ **Toast `Fattura creata` LIVE** — founder report: "fattura creata, toast visto" (S265 P1 ImpostazioniFatturazioneDialog+FatturaDialog fix S265 `69a2f5f` confermato runtime iMac)
2. ✅ **Fattura test in DB iMac** — id `000000000000000018b0c1b033563330`, `numero_completo=1/2026`, `imponibile_totale=10.0`, `iva_totale=0.0`, `totale_documento=10.0`, `deleted_at=NULL`
3. ✅ **Riga `fatture_righe` saved correctly** — `prezzo_unitario=10.0`, `quantita=1.0`, `prezzo_totale=10.0`, `aliquota_iva=0.0`, `natura=N2.2`, `unita_misura=PZ`, `descrizione="testy S266 verifica"`
4. ✅ **Schema 45 col `fatture` runtime confirmed** — Block B AC schema PASS (presenza `imponibile_totale`/`totale_documento`/`sdi_id_trasmissione`/`note_interne`/`deleted_at`)

### Scoperto S266
- 🐛 **BUG-FATT-3** (NON-encryption, P1 S267) — founder report: "non compare 0 quando vedi l'elenco delle fatture, se la apri l'importo è corretto". DB=10.0 ✅, dettaglio UI=10.0 ✅, **lista fatture mostra 0**.

---

## TASK S267 — 3 AC pending + 1 nuovo bug

### P0 — BUG-FATT-3 investigation+fix (lista fatture mostra zero)

**Founder action FIRST:**
1. Refresh pagina app FLUXION (F5 o ricarica tab Fatture)
2. SE persiste → screenshot lista fatture + DevTools Console: `await window.__TAURI__.invoke('get_fatture', {})` per ispezionare payload
3. SE F5 risolve → cache React Query stale bug (mutation invalidate non flushed prima di redirect/render iniziale post-create)

**Hypothesis ordered:**

| # | Causa | Evidenza | Fix |
|---|-------|----------|-----|
| H1 | Stat card `Fatturato` reduce ritorna 0 | `src/pages/Fatture.tsx:117` `reduce((sum, f) => sum + f.totale_documento, 0)` — se f.totale_documento undefined cast NaN→0 | type check + null coalescing `?? 0` |
| H2 | Riga TableCell formatCurrency(undefined) | `src/pages/Fatture.tsx:383` — render undefined → "€0,00" | guard + log |
| H3 | Cache React Query stale | `useCreateFattura` (use-fatture.ts) invalidates `fattureKeys.list()` MA filtri `anno=2026` cache key potrebbe non match | `refetchQueries` invece di `invalidateQueries` |
| H4 | Filtro anno default mismatch | Fattura created con `anno=2026`, lista filtra `anno=anno_corrente` — se default !=2026 fattura non appare | inspect default state |

**Verifica programmatica SSH (post-refresh):**
```bash
ssh imac "sqlite3 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db' \"SELECT id, anno, numero_completo, totale_documento, stato FROM fatture WHERE deleted_at IS NULL;\""
```
Atteso: 1 row anno=2026, totale_documento=10.0, stato=bozza (verificato S266: presente).

### P1 — Block A STEP 8 XML SDI tag plaintext

REGOLA #12: founder GUI required.

**Founder action sequence:**
1. App FLUXION UP iMac
2. Tab Fatture → apri dettaglio fattura `1/2026` (test S266)
3. Click pulsante **"Genera XML"** / **"Invia SDI"** / **"Esporta XML"**
4. File XML deve essere generato/salvato

**Verifica AC STEP 8:**
```bash
# Marker S266 ancora valido /tmp/s266-stamp (touched 2026-05-18 21:55 iMac)
ssh imac "find '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop' -name '*.xml' -newer /tmp/s266-stamp 2>/dev/null"
# Poi inspect:
ssh imac "grep -E '<Denominazione>|<IdCodice>|<Indirizzo>' <xml_file_found>"
```

Atteso (encryption decrypt path corretto):
- `<Denominazione>Automation Business</Denominazione>` **plaintext** (NOT Base64)
- `<IdCodice>02159940762</IdCodice>` plaintext
- `<Sede><Indirizzo>...` plaintext

### P2 — Toast `Impostazioni fatturazione salvate` LIVE

**Founder action:**
1. Impostazioni → Fatturazione → tab Azienda
2. Modifica campo Telefono (qualsiasi valore)
3. Click Salva
4. Conferma toast verde `"Impostazioni fatturazione salvate"` (S265 P1 fix ImpostazioniFatturazioneDialog)

### P3 — Boot2 idempotency (opzionale)

```bash
ssh imac "md5 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db'"
# founder chiude+riapre app, poi:
ssh imac "tail -30 ~/.fluxion/logs/*.log | grep -i 'impostazioni_fatturazione'"
# atteso: "already applied"
```

---

## Acceptance Criteria S267
- [ ] **BUG-FATT-3 root cause identified** — F5 risolve OR hypothesis H1-H4 confermata + fix landed
- [ ] **STEP 8 XML SDI**: tag `<Denominazione>` / `<IdCodice>` / `<Indirizzo>` plaintext
- [ ] **Toast Impostazioni LIVE**: founder conferma toast verde su salva
- [ ] **Boot2 idempotency** (opzionale): log `already applied` + md5 invariato

---

## Vincoli S267
- **Founder GUI required** REGOLA #12 — non delegabile SSH
- **REGOLA #6**: NO Co-Authored-By Claude trailer
- **REGOLA #11**: BUG-FATT-3 audit cross-entity prima di fix puntuale (Clienti/Fornitori/Cassa hanno stesso pattern lista+detail?)
- **Marker `/tmp/s266-stamp` ancora valido** se founder genera XML in S267 senza ri-set

---

## PROMPT START S267 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S267.

Step 1 (P0 BUG-FATT-3): chiedere founder F5 lista fatture
  - SE risolve → cache React Query bug, fix use-fatture.ts mutation invalidate
  - SE persiste → DevTools invoke get_fatture, screenshot, hypothesis H1-H4 walk

Step 2 (P1 STEP 8): founder genera XML SDI dalla fattura test 1/2026 (id 18b0c1b033563330)
  - SSH find XML newer /tmp/s266-stamp
  - grep <Denominazione>/<IdCodice>/<Indirizzo> plaintext

Step 3 (P2 toast Impostazioni): founder modifica telefono Impostazioni → save → toast verify

Step 4 (P3 boot2 opzionale): founder restart app → md5 + log already applied

CLOSE VERDE se P0+P1+P2 PASS (P3 opzionale).
Commit S267: docs(S267): close VERDE — S260 P4 STEP 8 + BUG-FATT-3 fix + toast Impostazioni live
```

---

**Provenienza S266 close**: VERDE-CON-ASTERISCO. Toast UX `Fattura creata` confirmed live + 1 fattura test creata DB iMac. BUG-FATT-3 nuovo scoperto (lista mostra 0, dettaglio OK). STEP 8 XML SDI + toast Impostazioni + boot2 idempotency tutti pending S267 founder fatigue.
