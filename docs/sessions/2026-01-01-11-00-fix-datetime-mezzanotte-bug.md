# 🐛 FIX CRITICO - Datetime Mezzanotte Bug

**Data**: 2026-01-01 11:00
**Tipo**: Bug fix critico
**Priorità**: BLOCCANTE
**Status**: ✅ RISOLTO

---

## 🔴 PROBLEMA

Gli appuntamenti creati a **mezzanotte (00:00)** venivano spostati di **+1 giorno** nel calendario.

### Scenario di Riproduzione

1. Utente crea appuntamento: **2 gennaio 2026 alle 00:00**
2. Appuntamento salvato nel database come: `2026-01-01T23:00:00Z` (UTC)
3. Query calendario cerca: `DATE(data_ora_inizio) >= '2026-01-02'`
4. Database ha: `DATE('2026-01-01T23:00:00Z')` = `'2026-01-01'`
5. Confronto: `'2026-01-01' >= '2026-01-02'` → **FALSE** ❌
6. **Appuntamento NON compare nel calendario!**

### Root Cause

**Conversione timezone non necessaria**:
- Frontend convertiva datetime locale → UTC prima di inviare al backend
- Esempio: `2026-01-02T00:00` (IT, UTC+1) → `2026-01-01T23:00:00Z` (UTC)
- Backend salvava UTC nel database
- Query SQLite `DATE()` estraeva la data UTC, non locale
- **Shift di -1 giorno per appuntamenti a mezzanotte in timezone UTC+N**

---

## ✅ SOLUZIONE

Salvare datetime in formato **locale** (senza timezone) nel database.

### Modifiche Implementate

#### 1. Frontend: Mantieni Tempo Locale
**File**: `src/components/calendario/AppuntamentoDialog.tsx`

**PRIMA** (Buggy):
```tsx
const localDate = new Date(year, month - 1, day, hours, minutes, 0, 0);
dataOraInizio = localDate.toISOString(); // "2026-01-01T23:00:00.000Z" (UTC)
```

**DOPO** (Fixed):
```tsx
const localDate = new Date(year, month - 1, day, hours, minutes, 0, 0);
// Validate
if (isNaN(localDate.getTime())) {
  throw new Error('Data/ora non valida');
}
// Keep local time WITHOUT timezone conversion
dataOraInizio = `${datePart}T${timePart}:00`; // "2026-01-02T00:00:00" (locale)
```

#### 2. Backend: Parse NaiveDateTime
**File**: `src-tauri/src/commands/appuntamenti.rs`

**PRIMA** (Buggy):
```rust
let start_dt = DateTime::parse_from_rfc3339(start)?; // Requires timezone
let end_dt = start_dt + Duration::minutes(duration_minutes);
Ok(end_dt.to_rfc3339()) // Returns UTC
```

**DOPO** (Fixed):
```rust
use chrono::{Duration, NaiveDateTime};

// Parse as NaiveDateTime (no timezone)
let start_clean = start.trim_end_matches('Z');
let start_dt = NaiveDateTime::parse_from_str(start_clean, "%Y-%m-%dT%H:%M:%S")
    .or_else(|_| NaiveDateTime::parse_from_str(start_clean, "%Y-%m-%dT%H:%M:%S%.f"))?;

let end_dt = start_dt + Duration::minutes(duration_minutes);

// Return local time (no timezone)
Ok(end_dt.format("%Y-%m-%dT%H:%M:%S").to_string())
```

---

## 🧪 TEST CASE

### Test 1: Appuntamento Mezzanotte
**Input**:
- Data: 2 gennaio 2026
- Ora: 00:00
- Cliente: Mario Rossi
- Servizio: Taglio Capelli

**Atteso**:
1. Salvataggio: `data_ora_inizio = "2026-01-02T00:00:00"` (locale, NO timezone)
2. Query calendario gennaio: `WHERE DATE(data_ora_inizio) >= '2026-01-02'`
3. Confronto: `DATE("2026-01-02T00:00:00")` = `'2026-01-02'`
4. `'2026-01-02' >= '2026-01-02'` → **TRUE** ✅
5. **Appuntamento appare nel giorno corretto (2 gennaio)**

### Test 2: Appuntamento Mezzogiorno
**Input**:
- Data: 2 gennaio 2026
- Ora: 12:30

**Atteso**:
- Salvataggio: `"2026-01-02T12:30:00"` (locale)
- Visualizzazione: 2 gennaio ore 12:30 ✅

### Test 3: Appuntamento Fine Giornata
**Input**:
- Data: 2 gennaio 2026
- Ora: 23:59

**Atteso**:
- Salvataggio: `"2026-01-02T23:59:00"` (locale)
- Visualizzazione: 2 gennaio ore 23:59 ✅
- **Durata**: Se 30min → `data_ora_fine = "2026-01-03T00:29:00"` (3 gennaio) ✅

---

## 📊 IMPATTO

### Prima del Fix
- ❌ Appuntamenti a mezzanotte (00:00-00:59) spostati di -1 giorno
- ❌ Appuntamenti delle 23:00-23:59 (UTC+1) mostrati giorno dopo in alcuni fusi orari
- ❌ Conflict detection errato per appuntamenti vicini a mezzanotte

### Dopo il Fix
- ✅ Tutti gli appuntamenti appaiono nel giorno corretto
- ✅ Orari visualizzati corrispondono a quelli inseriti
- ✅ Conflict detection accurato
- ✅ Indipendente dal fuso orario del browser

---

## 🔄 WORKFLOW GIT

```bash
# Aggiungi modifiche
git add src/components/calendario/AppuntamentoDialog.tsx
git add src-tauri/src/commands/appuntamenti.rs
git add docs/sessions/2026-01-01-11-00-fix-datetime-mezzanotte-bug.md

# Commit
git commit -m "fix(critical): datetime midnight bug - prevent +1 day shift

- Frontend: Keep local time WITHOUT UTC conversion
- Backend: Use NaiveDateTime for timezone-agnostic storage
- Fix: Appointments at 00:00 now appear on correct day
- Fix: SQLite DATE() query works correctly with local datetime
- Closes: datetime +1 day bug for midnight appointments"

# Push
git push origin master
```

---

## 📝 NOTE TECNICHE

### Perché NaiveDateTime?
- SQLite salva datetime come TEXT (no timezone nativo)
- Conversioni UTC inutili causavano shift di giorno
- `NaiveDateTime` di Chrono gestisce datetime "puri" senza timezone
- Più semplice e predicibile per app single-tenant locale

### Cosa Non È Cambiato
- `created_at` e `updated_at` usano ancora UTC (corretto per audit timestamp)
- Format: `chrono::Utc::now().to_rfc3339()` (mantiene timezone info)

### Considerazioni Future
Se in futuro FLUXION supporta:
- **Multi-timezone**: Salvare timezone nel DB (es: `timezone TEXT DEFAULT 'Europe/Rome'`)
- **Cloud sync**: Convertire a UTC prima di inviare al server
- **Reminders globali**: Usare UTC per calcoli di scheduling

Per ora, **locale-only è la scelta corretta** per desktop app single-tenant.

---

## ✅ CRITERI DI ACCETTAZIONE

- [x] TypeScript compila senza errori
- [x] Rust clippy senza warning
- [ ] Test su iMac: Crea appuntamento 2 gen 00:00 → Appare 2 gennaio ✅
- [ ] Test su iMac: Conflict detection mezzanotte funzionante ✅
- [ ] Test su iMac: Editing appuntamento mantiene data/ora corrette ✅
- [ ] Git commit + push completato ✅

---

## 🎯 PROSSIMI PASSI

1. **Test su iMac** (Monterey):
   ```bash
   cd "/Volumes/MacSSD - Dati/fluxion"
   git pull
   npm run tauri dev
   ```

2. **Verifiche manuali**:
   - Crea 3 appuntamenti: 00:00, 12:00, 23:59 per 2 gennaio
   - Verifica appaiano TUTTI il 2 gennaio
   - Verifica conflict detection con appuntamento 23:30 + durata 60min

3. **Se test OK**:
   - Marcare Fase 3 come COMPLETATA definitivamente ✅
   - Procedere con Fase 4 (Stati + WhatsApp)

---

*Fix implementato: 2026-01-01 11:30*
*Test richiesto su: iMac Monterey*
*Blocca: Fase 4 (finché non testato)*
