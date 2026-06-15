# AUDIT — "crea cliente" (S367 TASK-1) — 2026-06-15

> Read-only audit, scope STRETTO al solo flusso *create cliente*. Verificato alla fonte dal main (firewall), non solo dal report agente.
> Done-condition slice (verdetto giudice S365): non-tecnico completa il ciclo su Windows nativo, ZERO inciampi BLOCCANTI.

## Esito: 1 BLOCCANTE · 2 COSMETICI · 1 finding agente RESPINTO (falso positivo)

---

## 🔴 BLOCCANTE (1) — CONFERMATO ALLA FONTE

### B1 — submit invalido senza feedback al pulsante
- **File:line**: `src/components/clienti/ClienteForm.tsx:133`
- **Cosa**: `onSubmit={form.handleSubmit(handleSubmit)}` non ha il 2° argomento `onInvalid`. Su submit invalido react-hook-form imposta SOLO gli errori inline sotto i campi; nessun `toast.error` né riepilogo prominente vicino al pulsante. Il form è lungo (anagrafica + indirizzo + dati fiscali + consensi in grid 2-col): l'errore (es. su `nome`/`telefono` in alto) è fuori schermo quando il non-tecnico clicca "Salva" in fondo → il pulsante sembra morto, l'utente si blocca senza spiegazione. Stessa famiglia del difetto wizard (`SetupWizard.tsx` P.IVA inline-non-visto).
- **Test falsificabile (Windows nativo)**: apri Nuovo Cliente, lascia `telefono` vuoto (o `nome` 1 carattere), scorri il pulsante "Salva" in vista, clicca. **PASS** se appare un messaggio/riepilogo visibile che dice cosa correggere. **FAIL** se il pulsante non produce alcun feedback visibile.
- **Fix indicato (next session, NON applicato in audit)**: `form.handleSubmit(handleSubmit, onInvalid)` con `onInvalid` → `toast.error` + eventuale riepilogo errori.

---

## 🟡 COSMETICI (2)

### C1 — P.IVA opzionale, nessuna validazione di formato
- **File:line**: `src/components/clienti/ClienteForm.tsx:41` → `partita_iva: z.string().optional()`
- **Cosa**: P.IVA è opzionale e senza check formato. **NB correzione assunzione storica**: il blocco `.length(11)` è in `SetupWizard.tsx`, NON nel create-cliente. Qui un cliente privato NON è forzato a inserire P.IVA = corretto. Cosmetico: una P.IVA malformata passerebbe (rileva solo a valle, se userà la fatturazione SDI).
- **Test**: crea cliente con P.IVA "123" → PASS (cliente creato); regressione solo se in futuro serve SDI.

### C2 — nessun toast di conferma alla creazione
- **File:line**: `src/pages/Clienti.tsx` ~93-95 (post `mutateAsync` success path)
- **Cosa**: su creazione riuscita non c'è `toast.success`; la conferma implicita è chiusura dialog + refresh lista. Cosmetico (feedback implicito sufficiente, migliorabile).
- **Test**: crea cliente valido → PASS se compare in lista e il dialog si chiude.

---

## ❌ FINDING AGENTE RESPINTO (falso positivo)
- Agente: "mutation senza `onError` a livello hook (`use-clienti.ts:69`)" classificato cosmetico.
- **Realtà alla fonte**: `useCreateCliente` (`use-clienti.ts:69`) non ha `onError`, MA il chiamante lo gestisce: `Clienti.tsx:93` `await createMutation.mutateAsync()` in `try`, `catch`→`toast.error('Errore salvataggio cliente', {description:String(error)})` a `Clienti.tsx:98`. Per REGOLA #11 = GESTITO. Non è un difetto.
- Inoltre la citazione agente "no success toast → `ClienteDialog.tsx:95`" era ERRATA (riga 95 = rendering storico appuntamenti, non il submit). Citazione corretta = `Clienti.tsx` success path.

---

## Note igiene
- Audit read-only: ZERO modifiche a `src/`/`src-tauri/`.
- Commit `d4a20ff` apparso durante l'audit = artefatto auto-close hook VOS (tocca solo `.claude/NEXT_SESSION_PROMPT.md` + `SESSION_DIRTY.md`, NON src, NON il carry canonico `.manual.md`). Reversibile.
- Prossimo (ordine vincolante S367): item 2 = slice gestione clienti CRUD-E2E. Il fix di B1 va sul percorso del walkthrough nativo founder (hard-gate).

---

# AUDIT PARTE 2 — ciclo CRUD (cerca / modifica / archivia-elimina) — 2026-06-15

> Stesso scope-discipline: read-only, escluso "associa azione verticale" (schede, slice separata). Findings agente VERIFICATI alla fonte dal main.

## Esito parte 2: 0 BLOCCANTI · 4 COSMETICI · 1 BLOCCANTE-claim agente RESPINTO · delete-confirm PASS

### ❌ FINDING AGENTE RESPINTO (falso positivo) — era l'unico "BLOCCANTE"
- Agente: "form stale su riapertura dialog — Radix tiene `DialogContent` montato via CSS visibility, `useForm` non si re-inizializza" (`ClienteDialog.tsx:152`, `ClienteForm.tsx:79-101`).
- **Verifica alla fonte**: (1) `ClienteForm.tsx` NON ha `form.reset`/`useEffect` (grep zero match) → premessa "solo defaultValues al mount" corretta. **MA** (2) `ClienteDialog.tsx:151` = Radix `<Dialog open>`+`<DialogContent>` SENZA `forceMount` → Radix **smonta** il contenuto alla chiusura (comportamento default) → `ClienteForm` si **rimonta** a ogni apertura con i `defaultValues` del nuovo cliente. (3) `cliente` cambia solo con `open=false` (dialog modale copre la lista → nessuno swap in-place). → **Nessun dato stale. NON è un bug.** La premessa "Radix tiene montato" è errata per Radix.

### 🟢 DELETE-CON-CONFERMA — PASS (verificato)
`Clienti.tsx:81-84,102-113,228-253`: trash → `AlertDialog` con nome cliente esplicito + "Questa azione non può essere annullata" + bottone rosso "Elimina" disabilitato durante `isPending` + `catch`→`toast.error('Errore eliminazione cliente')`. Nessun path di delete senza conferma. Corretto.

### 🟡 COSMETICI (4 — backlog, NON bloccano la done-condition)
1. **Empty-state ambiguo su ricerca** (`ClientiTable`/`Clienti.tsx`): a ricerca senza match mostra "Inizia aggiungendo il tuo primo cliente" → un non-tecnico può pensare che il DB sia vuoto. Fix cheap = stringa contestuale "nessun risultato per questa ricerca". *Test*: cerca "zzz" → PASS se messaggio dice "nessun risultato".
2. **`useSearchClienti` dead code** (`use-clienti.ts:51-57`): definito, mai usato (la pagina filtra in-memory su `useClienti()`). Housekeeping, nessun impatto UX (filtro 1-char funziona).
3. **Niente debounce sul search** (`Clienti.tsx:192-209`): irrilevante a 1-15 dipendenti. Backlog scale.
4. **`AlertDialogAction` chiude prima dell'async** (`Clienti.tsx:244-250`): su delete fallito il dialog è già chiuso (Radix close primitive) ma il toast.error appare e il cliente resta in lista → recuperabile (ritenta). Cosmetico.
5. *(nota, famiglia di B1)* edit dialog `overflow-hidden` + scroll interno (`ClienteDialog.tsx:152,162`): il bottone "Aggiorna Cliente" può finire sotto il fold su 1366×768. Scrollabile → non blocca, ma poco evidente. Backlog.

## CONCLUSIONE SLICE GESTIONE CLIENTI (S367)
Dopo il fix B1 (committato `0232090`), il ciclo cliente (crea/cerca/modifica/elimina) ha **ZERO BLOCCANTI noti** all'audit statico. Restano solo cosmetici (backlog). → Pronto per il **walkthrough nativo founder** (build iMac + reinstall Windows), che è l'hard-gate che porta la slice a VERDE per verdetto giudice. Un giro pulito che non genera nuovi BLOCCANTI = done (niente quarto decimale).
