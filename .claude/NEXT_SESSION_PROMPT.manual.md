# Prompt ripartenza S268 — 4 bug BUG-FATT-3/4/5/6 + boot2 idempotency

## Stato chiusura S267 (NO new code commit, master `ccd0ebd` MacBook+iMac fast-forward sync)

**VERDE-CON-ASTERISCO** — STEP 8 XML SDI AC PRIMARY landed live verified (5 tag plaintext encryption decrypt OK). 4 bug FE/cache/UX raccolti per S268. Context 55% chiusura ordinata BLOCK_CRITICAL gate.

### Consegnato S267
1. ✅ **STEP 8 XML SDI plaintext AC PASS** — Fattura `1/2026` emessa via founder GUI → XML in DB (`fatture.xml_content`, filename `IT02159940762_00001.xml`, 3411 byte). Tag plaintext verified:
   - `<IdCodice>02159940762</IdCodice>` (P.IVA Cedente decrypted from `impostazioni_fatturazione.partita_iva` Base64)
   - `<CodiceFiscale>DSTMGN81S12L738L</CodiceFiscale>` (CF Cedente decrypted)
   - `<Denominazione>Automation Business</Denominazione>` (Denominazione Cedente decrypted)
   - `<Indirizzo>Via Roma 1</Indirizzo>` `<CAP>85100</CAP> <Comune>Potenza</Comune> <Provincia>PZ</Provincia>` (Sede Cedente plaintext, comune/cap NOT encrypted by design S260)
   - Cliente Anna Bianchi tag plaintext (no encryption clienti su xml lato BookingStateMachine — sara consumers tier)
2. ✅ **P0 BUG-FATT-3 root cause** — F5 risolve → cache React Query stale post-create. `useCreateFattura.onSuccess` invalida `fattureKeys.all` MA `add_riga_fattura` (separato) ricalcola `totale_documento` post-create → race window: refetch 1 con totale=0, poi refetch 2 con totale=10. F5 force-refetch sincronizza.
3. ✅ **Domanda IVA forfettario chiarita founder** — RF19 → aliquota=0, natura N2.2, no bollo €77,47 floor. Comportamento corretto.

### Scoperto S267 (4 bug nuovi defer S268)
- 🐛 **BUG-FATT-3** (P0): cache stale Fatture lista mostra `totale_documento=0` finché F5 manuale. Fix audit cross-entity REGOLA #11 (Clienti/Fornitori/Cassa hanno stesso pattern `invalidateQueries` post-mutation con sub-mutations? Probabilmente NO perché Clienti non ha `add_riga` cascata).
- 🐛 **BUG-FATT-4** (P1): `update_impostazioni_fatturazione` save fallisce silenzioso quando founder compila SOLO telefono (campo era vuoto pre-S267). Live evidence: telefono col plaintext (idx 10, TEXT) rimasta NULL in DB post-save. mutateAsync throwa (modal resta aperto = catch entrato). Stack trace non recuperato (logs non scritti su filesystem).
- 🐛 **BUG-FATT-5** (P1): Sonner toast `toast.error('Errore salvataggio impostazioni')` NON visibile founder quando Dialog Impostazioni aperto. Classic z-index shadcn Dialog overlay > Sonner toaster. Fix globale: bump `<Toaster />` z-index OR `position="top-center"` per scappare Dialog overlay.
- 🐛 **BUG-FATT-6** (P2): pulsante "Download XML" su fattura emessa = no-op (no save dialog, no file scritto). XML è in DB (`fatture.xml_content`) ma il command `get_fattura_xml` FE→Rust ritorna stringa ma il FE NON salva tramite Tauri fs plugin / save dialog.

### Deferred S268 secondario
- ⏳ **P3 boot2 idempotency** `impostazioni_fatturazione`: founder restart app → `tail logs | grep 'already applied'` + md5 DB invariato. Low priority log-only verify.

---

## TASK S268 — 4 bug fix + audit

### P0 — BUG-FATT-3 cache stale Fatture lista

**Investigation step 1 (read-only)**: confermare race window `useCreateFattura → add_riga_fattura`. Aprire `src-tauri/src/commands/fatture.rs` cerca `add_riga_fattura` — verifica se ricalcola `totale_documento` su `fatture` row OR se rimane 0 fino a `emetti_fattura`.

**Fix candidato**: cambiare `useCreateFattura.onSuccess` da `invalidateQueries({queryKey: fattureKeys.all})` a:
- Opzione A: `refetchQueries({queryKey: fattureKeys.list()})` (force refetch immediato)
- Opzione B: rimuovere invalidate da `useCreateFattura`, lasciare solo a `useAddRigaFattura.onSuccess` (chain pattern: nessun refetch finché righe non aggiunte)
- Opzione C: rendere `add_riga_fattura` ricalcolare + return `Fattura` updated (commands già fa? verificare)

**Audit cross-entity REGOLA #11**: grep `useMutation` + `onSuccess` in:
- `src/hooks/use-clienti.ts`
- `src/hooks/use-fornitori.ts`  
- `src/hooks/use-cassa.ts` o equivalente
- `src/hooks/use-appuntamenti.ts`

Cerca pattern simili (create + add_subitem) per identificare se bug è isolato Fatture o sistemico.

### P1 — BUG-FATT-4 save Impostazioni fallisce telefono solo

**Founder action sequence (richiede DevTools open)**:
1. App FLUXION iMac → Impostazioni → tab Azienda
2. Apri DevTools (Cmd+Opt+I) → tab Console
3. Modifica campo telefono → click Salva
4. Console mostra stack trace `Errore aggiornamento impostazioni: ...`
5. Founder copia errore + screenshot per S268

**Hypothesis ordered**:
| # | Causa | Verifica |
|---|-------|----------|
| H1 | `update_impostazioni_fatturazione` Rust command valida campi obbligatori (denominazione/partita_iva) → throw se vuoti dopo encrypt round-trip stale | grep command Rust |
| H2 | Encryption gate richiede campi PII tutti popolati altrimenti throw | check `commands/impostazioni_fatturazione.rs` |
| H3 | Form `form.telefono \|\| undefined` → undefined viene serializzato `null` in IPC → backend Rust riceve `None` → no update fatto MA no error | unlikely (telefono ok per null) |

### P1 — BUG-FATT-5 Sonner toast coperto Dialog

**Fix globale**: file `src/main.tsx` o `src/App.tsx` dove `<Toaster />` di Sonner è mounted.

Cambia da:
```tsx
<Toaster />
```
A:
```tsx
<Toaster position="top-center" toastOptions={{ style: { zIndex: 9999 } }} />
```

Verifica z-index DialogOverlay shadcn → setta toaster z-index > overlay (di default Sonner usa `999999`, ma può essere override da DialogOverlay z-50 = 50).

### P2 — BUG-FATT-6 Download XML no-op

**Investigation**: 
1. Trova handler pulsante Download in `src/pages/Fatture.tsx` o `src/components/fatture/FatturaDetail.tsx`
2. Verifica usa Tauri `save` dialog plugin OR window.URL.createObjectURL
3. Probabile bug: chiama `get_fattura_xml` ritorna stringa MA non triggera save (manca step blob/file)

### P3 — Boot2 idempotency `impostazioni_fatturazione` (low priority)

```bash
ssh imac "md5 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db'"
# founder restart app, poi:
ssh imac "ps aux | grep -i fluxion | grep -v grep"  # verify app booted
ssh imac "md5 '/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db'"  # invariato
```

---

## Acceptance Criteria S268

- [ ] **BUG-FATT-3 fix landed**: cache invalidate refactored, audit cross-entity completato, regression test (create fattura → totale visibile in lista senza F5)
- [ ] **BUG-FATT-4 root cause + fix**: stack trace via DevTools console, fix backend O FE
- [ ] **BUG-FATT-5 toast visibility**: Sonner z-index globale fix, regression test (modal aperto + toast.error → toast visibile)
- [ ] **BUG-FATT-6 Download XML**: pulsante triggera save dialog, file XML scritto su disco founder
- [ ] **P3 boot2 idempotency**: log `already applied` OK (opzionale)

---

## Vincoli S268

- **Founder GUI required** REGOLA #12 per BUG-FATT-4 (DevTools stack trace) + BUG-FATT-6 (save dialog test)
- **REGOLA #11**: audit cross-entity OBBLIGATORIO per BUG-FATT-3 prima di fix puntuale
- **REGOLA #6**: NO Co-Authored-By Claude trailer
- **Context budget**: parti da sessione fresca (S267 chiusa a 55%, S268 deve essere <30% raw post-boot per editare file critici tipo `use-fatture.ts` se BUG-FATT-3 fix richiede)

---

## PROMPT START S268 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S268.

Step 1 (P0 BUG-FATT-3): investigation add_riga_fattura ricalcolo + audit cross-entity hooks (clienti/fornitori/cassa/appuntamenti)
  - Read-only grep, NO edit fino a hypothesis confermata
  - Fix candidato: refetchQueries vs invalidateQueries vs chain pattern

Step 2 (P1 BUG-FATT-4): founder Impostazioni → tab Azienda → DevTools Console → modifica telefono → click Salva → copia stack trace
  - SE error visibile → fix mirato backend O FE
  - SE nessun error console → bug rendering Sonner toast (link a BUG-FATT-5)

Step 3 (P1 BUG-FATT-5): grep <Toaster /> in src/main.tsx o src/App.tsx
  - Aggiungi position="top-center" + z-index 9999
  - Regression test: modal aperto + simulated error → toast visible

Step 4 (P2 BUG-FATT-6): trova handler Download XML in Fatture.tsx o FatturaDetail.tsx
  - Verifica Tauri save dialog plugin path
  - Fix: use Tauri @tauri-apps/plugin-dialog::save + writeTextFile

Step 5 (P3 opzionale): boot2 idempotency log verify

CLOSE VERDE se P0+P1 BUG-FATT-3/4/5 PASS (P2 BUG-FATT-6 + P3 opzionale).
Commit S268: fix(S268): BUG-FATT-3/4/5 — cache stale + impostazioni save + toast visibility
```

---

**Provenienza S267 close**: VERDE-CON-ASTERISCO. STEP 8 XML SDI plaintext AC PRIMARY shipped live verified (5 tag plaintext, encryption decrypt path su `impostazioni_fatturazione` 4 cols PII OK). 4 bug FE/cache/UX scoperti durante founder GUI verify → defer S268 con root cause hypothesis + fix candidates documentati. Context budget gate BLOCK_CRITICAL rispettato (no edit code).
