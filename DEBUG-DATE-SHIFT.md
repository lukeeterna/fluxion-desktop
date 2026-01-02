# PROMPT PER CLAUDE - DEBUG CRITICO APPUNTAMENTI FLUXION

## CONTESTO PROGETTO
- **App**: FLUXION - Gestionale desktop Tauri 2.x + React 19 + TypeScript + SQLite
- **Ambiente test**: macOS 12 Monterey (iMac)
- **Repository**: github.com/luketerna/fluxion-desktop (branch: master)
- **Path locale**: /Volumes/MontereyT7/FLUXION

## 🔴 PROBLEMA CRITICO NON RISOLTO

### BUG: Date Shift (+1 giorno)

**Sintomo**:
Quando creo un appuntamento selezionando data **03/01/2026 ore 09:49**, 
l'appuntamento viene salvato e visualizzato il giorno **04/01/2026 ore 09:49** (+1 giorno).

**Screenshot disponibili**: /Users/macbook/Downloads/re (3)/
- Schermata 2026-01-02 alle 08.49.56.png → Mostra creazione con data 03/01/2026
- Schermata 2026-01-02 alle 08.50.12.png → Mostra appuntamento salvato su 04/01/2026 (SBAGLIATO)

**Tentativi di fix falliti**:
1. Modificato `AppuntamentoDialog.tsx` riga 50: sostituito `toISOString()` con `getLocalDateTimeString()`
2. Il problema PERSISTE dopo git pull e npm run tauri dev

## FILE RILEVANTI

### Frontend (sospetti):
1. `src/components/calendario/AppuntamentoDialog.tsx`
   - Riga 34-42: Helper `getLocalDateTimeString()` 
   - Riga 50: Default value `data_ora_inizio`
   - Riga 113-142: Logica conversione datetime-local → RFC3339

2. `src/pages/Calendario.tsx`
   - Riga 50-56: Funzione `formatDateISO()`
   - Riga 100-112: Grouping appuntamenti per data
   - Riga 321-335: Props passate a AppuntamentoDialog

### Backend Rust (sospetti):
3. `src-tauri/src/commands/appuntamenti.rs`
   - Riga 94-109: Funzione `calculate_end_datetime()` con parsing NaiveDateTime
   - Riga 274-340: Comando `create_appuntamento`

### Types:
4. `src/types/appuntamento.ts` - Schema Zod e types

## ISTRUZIONI DEBUG

### STEP 1: Analisi Completa Flusso Dati

**Traccia il flusso completo della data**:
1. User seleziona nel datetime-local input: `"2026-01-03T09:49"`
2. Frontend `onSubmit`: quale valore viene costruito? (riga 113-147 AppuntamentoDialog.tsx)
3. Tauri invoke: quale payload JSON viene inviato?
4. Backend Rust: come viene parsato in `create_appuntamento`?
5. Database SQLite: quale valore viene salvato nella colonna `data_ora_inizio`?
6. Query `get_appuntamenti`: quale valore viene restituito?
7. Frontend display: come viene parsato in `new Date(app.data_ora_inizio)`?

**Aggiungi logging**:
- Frontend: `console.log()` in AppuntamentoDialog.tsx riga 144-147
- Backend: `println!()` in appuntamenti.rs riga 276-282

### STEP 2: Verifica Timezone

**Ipotesi**: Il problema potrebbe essere:
- Conversione UTC vs Local nel parsing
- `NaiveDateTime` in Rust trattato come UTC invece che local
- Midnight/DST edge case
- Formato stringa inconsistente

**Controlla**:
1. Quale timezone usa `new Date()` in JavaScript?
2. Come Rust interpreta `"2026-01-03T09:49:00"` (senza Z)?
3. SQLite salva come TEXT o TIMESTAMP?

### STEP 3: Test Isolato

**Crea test minimale**:
```typescript
// In AppuntamentoDialog.tsx, riga 144 circa
console.log('=== DEBUG DATE ===');
console.log('Input raw:', data.data_ora_inizio);
console.log('After format:', dataOraInizio);
console.log('Payload:', payload);
```

```rust
// In appuntamenti.rs, riga 276 circa
println!("=== DEBUG DATE RUST ===");
println!("Input datetime: {}", input.data_ora_inizio);
println!("Calculated end: {}", data_ora_fine);
```

### STEP 4: Possibili Fix

**Se il problema è nel backend Rust**:
- Riga 101-103: Il parsing `NaiveDateTime::parse_from_str` potrebbe interpretare come UTC
- Considera usare `chrono::Local` invece di `NaiveDateTime`

**Se il problema è nel frontend**:
- Riga 134: `new Date(year, month - 1, day, hours, minutes, 0, 0)` crea local time
- Ma poi viene formattato come stringa senza timezone
- Backend potrebbe interpretare come UTC

**Fix Suggerito**:
```typescript
// AppuntamentoDialog.tsx riga 141 circa
// Invece di: dataOraInizio = `${datePart}T${timePart}:00`;
// Prova: dataOraInizio = `${datePart}T${timePart}:00+01:00`; // Timezone esplicito
```

Oppure lato Rust:
```rust
// appuntamenti.rs - Salvare sempre UTC ma convertire in input
use chrono::{DateTime, Local, Utc};
let local_dt = NaiveDateTime::parse_from_str(&input.data_ora_inizio, "%Y-%m-%dT%H:%M:%S")?;
let local_datetime = Local.from_local_datetime(&local_dt).unwrap();
let utc_datetime = local_datetime.with_timezone(&Utc);
// Salva utc_datetime.to_rfc3339()
```

### STEP 5: Verifica Database

```bash
# Sul MacBook, controlla cosa c'è REALMENTE nel DB
cd /Volumes/MontereyT7/FLUXION
sqlite3 src-tauri/target/debug/fluxion.db
SELECT id, data_ora_inizio, created_at FROM appuntamenti ORDER BY created_at DESC LIMIT 5;
.quit
```

Confronta il valore nel DB con quello visualizzato.

## DELIVERABLE RICHIESTO

1. **Root cause esatto**: Dove avviene la conversione sbagliata?
2. **Fix testato**: Codice modificato che risolve il problema
3. **Test proof**: Screenshot che mostra:
   - Input: 03/01/2026 09:49
   - Output calendario: 03/01/2026 09:49 (CORRETTO)
4. **Git commit**: Con messaggio chiaro del fix

## VINCOLI

- ✅ Il fix DEVE funzionare su macOS Monterey 12
- ✅ NON rompere appuntamenti già esistenti nel DB
- ✅ NON usare librerie esterne aggiuntive
- ✅ Test manuale su iMac OBBLIGATORIO prima di confermare

## RISORSE

- Documentazione: `docs/context/CLAUDE-BACKEND.md` e `CLAUDE-FRONTEND.md`
- Design: `docs/FLUXION-DESIGN-BIBLE.md`
- Test checklist: `docs/testing/manual/APPUNTAMENTI-BUG-FIXES.md`

---

**QUESTO È UN BUG BLOCCANTE. L'app è INUTILIZZABILE finché non viene risolto.**
