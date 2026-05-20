# Prompt ripartenza S269 — live verify founder GUI S268 BUG-FATT-3/4/5/6 fix

## Stato chiusura S268 (commit `08918a7` master, MacBook+iMac sync)

**VERDE-CON-ASTERISCO** — 4 bug FE/cache/UX fix landed code + type-check 0 errori + cargo check 0 errori + data_migration 4/4 PASS. Live verify pending founder GUI launch (REGOLA #12 Keychain gate).

### Consegnato S268

1. ✅ **BUG-FATT-3 (P0 cache stale)** — `src/hooks/use-fatture.ts`:
   - `useAddRigaFattura.onSuccess` + `useRegistraPagamento.onSuccess` ora invalidano `fattureKeys.all` invece di `fattureKeys.list()`.
   - **Root cause**: TanStack Query v5 prefix match — `['fatture', 'list', undefined]` (no filters) NON matcha `['fatture', 'list', {anno: 2026}]` (con filters). Pattern coerente con `useCreateFattura`/`useEmettiFattura` (già usano `fattureKeys.all`).
   - **Audit cross-entity REGOLA #11**: bug isolato a `use-fatture.ts` (3-elem queryKey con filters object). Altri domain hooks (`use-clienti`, `use-fornitori`, `use-loyalty`, `use-appuntamenti`) usano `lists()` 2-elem → prefix match OK.

2. ✅ **BUG-FATT-4 (P1 save Impostazioni telefono)** — `src/hooks/use-fatture.ts::useUpdateImpostazioniFatturazione`:
   - Args **snake_case → camelCase** (Tauri 2.x default convention).
   - Required `String` Rust fields (`denominazione`/`partitaIva`/`regimeFiscale`/`indirizzo`/`cap`/`comune`/`provincia`) default `''` invece di `null` (encrypt_required pass-through accetta vuoto).
   - `nazione` rimosso (extra field non presente in signature Rust).

3. ✅ **BUG-FATT-5 (P1 toast invisibile)** — `src/App.tsx`:
   - `<Toaster />` globale montato in `<App>` con `position='top-center'`, `richColors`, `closeButton`, `zIndex 9999`.
   - **Root cause più grave del previsto**: Toaster NON era mai montato in App/main/MainLayout — TUTTI i `toast.success`/`toast.error` silenziosi end-to-end (non solo dentro Dialog overlay come ipotizzato). Anche la conferma S266 "Fattura creata toast visto" era probabilmente confusione con altro feedback UI (modal close).

4. ✅ **BUG-FATT-6 (P2 Download XML no-op)**:
   - Nuovo command Rust `save_fattura_xml_to_file` in `src-tauri/src/commands/fatture.rs` (path validato `.xml` + parent dir esiste + `std::fs::write`).
   - Registrato in `lib.rs` invoke_handler.
   - Capability `dialog:allow-save` aggiunta in `src-tauri/capabilities/default.json`.
   - FE handler in `src/pages/Fatture.tsx` + `src/components/fatture/FatturaDetail.tsx` refactored: `@tauri-apps/plugin-dialog::save` per ottenere path utente + `invoke('save_fattura_xml_to_file', {fatturaId, path})`. Pattern `<a download>` + `Blob.createObjectURL` NON funziona in WKWebView/WebView2.

### Verify S268
- ✅ `npx tsc --noEmit` → 0 errori
- ✅ Pre-commit ESLint → 0 errors, 17 warnings preesistenti `any` (non blocker, non in file S268)
- ✅ `cargo check` iMac → 0 errori, 2 warning preesistenti (`license_ed25519`, `listini` unused import, non toccati)
- ✅ `cargo test data_migration::` → **4/4 PASS** (suite encryption non toccata da S268, sanity check)
- ⏳ **Live verify founder GUI**: PENDING — Keychain gate REGOLA #12 richiede founder launch app fisicamente su iMac

---

## TASK S269 — Live verify 4 bug fix

### Step 1: founder launch app GUI su iMac
```bash
ssh imac 'osascript -e "tell application \"FLUXION\" to activate"'
# OPPURE founder doppio click icona FLUXION dock iMac
```
Attendere boot completo (HTTP Bridge :3001 attivo, app finestra visibile).

### Step 2: BUG-FATT-3 regression test (cache stale)
1. Founder → tab Fatture → click "Nuova fattura"
2. Cliente: qualsiasi cliente esistente, riga `prezzo_unitario=15, quantita=1`, aliquota=0 (forfettario)
3. Conferma + chiudi dialog
4. **Acceptance**: lista Fatture mostra fattura con `Totale = 15,00 €` SUBITO (NO F5 necessario).
5. **FAIL se**: lista mostra `0,00 €` finché F5.

### Step 3: BUG-FATT-4 regression test (save Impostazioni)
1. Founder → Impostazioni → tab Fatturazione → Apri Dialog Impostazioni
2. Tab Azienda → campo Telefono → digita `+39 0971 123456`
3. Click "Salva impostazioni"
4. **Acceptance**: toast verde `"Impostazioni fatturazione salvate"` visibile + modal si chiude.
5. **Verify DB**:
```bash
ssh imac 'sqlite3 "/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db" "SELECT length(telefono), substr(telefono,1,30) FROM impostazioni_fatturazione WHERE id=\"default\""'
# Expected: length > 0 + Base64 ciphertext (es. "1aBcDeFg...")
```
6. **FAIL se**: modal resta aperto OR telefono in DB rimane NULL.

### Step 4: BUG-FATT-5 regression test (toast visibility)
1. Già coperto da Step 3 (toast deve essere visibile).
2. **Acceptance ulteriore**: aprire Dialog modal qualsiasi (es. Nuova fattura) → simulare errore (provare submit form vuoto) → toast `red` deve essere visibile sopra il modal.

### Step 5: BUG-FATT-6 regression test (Download XML)
1. Founder → tab Fatture → riga fattura `1/2026` (creata S267) → click bottone Download icon
2. **Acceptance**: si apre dialog OS "Salva con nome" → founder seleziona path es. `~/Desktop/test-fattura.xml` → conferma.
3. **Acceptance**: toast verde `"XML scaricato"` con description path.
4. **Verify file**:
```bash
ssh imac 'ls -la /Users/gianlucadistasi/Desktop/test-fattura.xml && head -c 200 /Users/gianlucadistasi/Desktop/test-fattura.xml'
# Expected: file ~3411 byte + inizia con "<?xml version=\"1.0\" encoding=\"UTF-8\"?>..."
```
5. **FAIL se**: nessun dialog OS, OR file non scritto, OR contenuto malformed.

### Step 6 (P3 opzionale): boot2 idempotency impostazioni_fatturazione
```bash
ssh imac 'md5 "/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db"'
# Founder kill app + relaunch GUI iMac
ssh imac 'md5 "/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db"'  # invariato attesa
ssh imac 'tail -100 ~/Library/Logs/com.fluxion.desktop/*.log 2>/dev/null | grep -i "impostazioni.*already applied"'
```

---

## Acceptance Criteria S269

- [ ] **BUG-FATT-3**: regression test create fattura → lista mostra totale corretto senza F5 (Step 2)
- [ ] **BUG-FATT-4**: regression test save telefono → DB ciphertext salvato + toast visibile (Step 3)
- [ ] **BUG-FATT-5**: regression test toast sopra modal (Step 4 already covered da Step 3)
- [ ] **BUG-FATT-6**: regression test save dialog OS + file scritto + content OK (Step 5)
- [ ] **P3 opzionale**: boot2 idempotency log + md5 invariato (Step 6)

CLOSE VERDE se Step 2+3+5 PASS (BUG-FATT-3/4/5/6 confermati).
Commit S269 (solo se needed fix bonus durante live verify): `fix(S269): live verify S268 + fix bonus`

---

## Vincoli S269

- **REGOLA #12**: founder GUI launch fisicamente su iMac REQUIRED per Step 1
- **REGOLA #11**: audit cross-entity già fatto in S268, no re-audit necessario
- **REGOLA #6**: NO Co-Authored-By Claude trailer su commit
- **Context budget**: parti fresca, sessione corta (~30% raw post-boot OK per live verify)

---

## File modificati S268 (riferimento)

- `src/hooks/use-fatture.ts` — BUG-FATT-3 + BUG-FATT-4
- `src/App.tsx` — BUG-FATT-5 Toaster globale
- `src/pages/Fatture.tsx` — BUG-FATT-6 download handler refactor
- `src/components/fatture/FatturaDetail.tsx` — BUG-FATT-6 download handler refactor
- `src-tauri/src/commands/fatture.rs` — nuovo command `save_fattura_xml_to_file`
- `src-tauri/src/lib.rs` — register handler
- `src-tauri/capabilities/default.json` — `dialog:allow-save`

---

## PROMPT START S269 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S269.

Step 1: founder launch app GUI iMac (REGOLA #12 Keychain gate).
Step 2: BUG-FATT-3 regression — crea fattura test → verify lista mostra totale senza F5.
Step 3: BUG-FATT-4 regression — modifica telefono Impostazioni → verify toast + DB ciphertext.
Step 4: BUG-FATT-5 implicito in Step 3 + simulare error con modal aperto.
Step 5: BUG-FATT-6 regression — click Download XML su fattura 1/2026 → verify dialog OS + file scritto.
Step 6 (opzionale): boot2 idempotency impostazioni_fatturazione log + md5 DB.

CLOSE VERDE se Step 2+3+5 PASS.
```

---

**Provenienza S268 close**: VERDE-CON-ASTERISCO. 4 bug FE/cache/UX/WebView fix landed code-side con type-check 0 errori + cargo check 0 errori + data_migration tests 4/4 PASS. Audit cross-entity REGOLA #11 PASS (bug isolato a `use-fatture.ts` 3-elem queryKey). Pattern Tauri 2.x camelCase convention applicato. WebView download anti-pattern (Blob+anchor) sostituito con plugin-dialog::save + Rust command nativo std::fs::write. Live verify schedulata S269 founder GUI presence.
