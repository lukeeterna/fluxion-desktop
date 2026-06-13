# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-13T14:00:00Z`
**Sessione**: frontend-developer fix onboarding wizard
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## STATO CHIUSURA

Fix #2 e Fix #3 del SetupWizard COMPLETATI. `tsc --noEmit` EXIT 0.
Modifiche nel working tree, NON committate (founder chiede no-commit).

---

## COSA E' STATO FATTO

### Fix #2 — Riepilogo errori di validazione al click "Avvia FLUXION"
File: `src/components/setup/SetupWizard.tsx`

1. Aggiunto `import { toast } from 'sonner'`
2. Aggiunto `import { AlertCircle } from 'lucide-react'`
3. `onSubmit` catch: `console.error` sostituito con `toast.error('Errore durante il salvataggio', { description: String(error) })`
4. Aggiunto handler `onInvalid` che chiama `toast.error('Controlla i campi evidenziati: alcuni dati non sono validi')`
5. `handleSubmit(onSubmit)` → `handleSubmit(onSubmit, onInvalid)`
6. Aggiunta error box con `data-testid="setup-validation-error-summary"` sopra i Navigation Buttons, visibile solo quando `step === totalSteps && Object.keys(errors).length > 0`, con lista campi in errore

### Fix #3 — Dropdown sovrapposti step 6
File: `src/components/setup/SetupWizard.tsx`

Aggiunto `side="bottom"` e `avoidCollisions={false}` sui due `SelectContent` in step 6 (Categoria Attività e Regime Fiscale). Questo forza apertura sempre verso il basso, impedendo il ribaltamento verso l'alto che causa sovrapposizione tra i due select vicini.
Aggiunti `data-testid` sui `SelectTrigger`: `setup-select-categoria` e `setup-select-regime`.

### Verifica type-check
`npm run type-check` (tsc --noEmit) → EXIT 0, zero errori.

---

## COSA RESTA DA VERIFICARE (E2E nativo — founder)

- Aprire il wizard su Windows nativo (o macOS con app lanciata)
- Step 1: inserire P.IVA con meno di 11 caratteri, cliccare "Avanti" fino a step 7, poi "Avvia FLUXION" → verificare che la error box rossa appaia con i campi in errore e il toast sia visibile
- Step 6: aprire il primo Select (Categoria Attività), selezionare un valore, poi aprire il secondo Select (Regime Fiscale) → verificare che non si sovrappongano
- Nessuna verifica E2E autonoma possibile: richiede build Tauri + installazione Windows/macOS nativa

---

## PROSSIMA SESSIONE

Se il founder conferma i fix visivamente, il wizard onboarding è sbloccato.
Se emergono altri step da correggere, riferire i symptom esatti e step number per fix mirati.
