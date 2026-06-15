# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-15T15:00:00Z`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Last commit**: `80c30d8 chore(S366): verifica a661bab = solo carry hook, zero src`

## Audit "crea cliente" — COMPLETATO questa sessione

READ-ONLY audit della flow "crea cliente" completato. 4 findings:

### BLOCCANTE (1)
- `ClienteForm.tsx:133` + `ClienteDialog.tsx:128` — `form.handleSubmit(handleSubmit)` senza `onInvalid` callback. Su display 768px l'errore inline su campo off-screen è invisibile, il bottone "Crea Cliente" appare morto. Fix: aggiungere secondo argomento `onInvalid` che chiama `toast.error('Compila i campi obbligatori')`.

### COSMETICI (3)
- `ClienteForm.tsx:41` — `partita_iva` manca validazione formato (11 cifre numeriche), solo `maxLength` HTML.
- `use-clienti.ts:66-77` — `useCreateCliente` senza `onError` a livello hook (il catch in Clienti.tsx compensa, ma call-site futuri con `mutate()` sarebbero silenti).
- `ClienteDialog.tsx:124-147` — nessun toast di successo dopo creazione; il dialog si chiude in silenzio.

## Prossimi step (da NEXT_SESSION_PROMPT.manual.md)

Leggi `.claude/NEXT_SESSION_PROMPT.manual.md` per il contesto completo S367.
Task prioritario: FIX BLOCCANTE sopra (onInvalid callback) → type-check → E2E walkthrough Windows.
