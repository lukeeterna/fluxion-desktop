# Sessione: Setup Wizard + Mock Data Fix

**Data**: 2026-01-06T13:45:00
**Fase**: 7 - Voice Agent + WhatsApp
**Agente**: rust-backend, react-frontend

## Obiettivi Sessione
1. Fix errori mock_data.sql per popolare database fatture
2. Implementare Setup Wizard per configurazione iniziale app

## Problema Iniziale
Il database non veniva popolato correttamente a causa di:
- Schema mismatch tra migration 001 (fatture vecchie) e migration 007 (fatturazione elettronica)
- Migration 007 usa `CREATE TABLE IF NOT EXISTS` che non ricrea tabelle già esistenti
- File .env con valori non quotati causava errore parsing

## Modifiche Effettuate

### 1. Fix mock_data.sql
- **Rimosso**: Sezioni per tabelle migration 007 (impostazioni_fatturazione, fatture_pagamenti, fatture_riepilogo_iva)
- **Adattato**: Schema fatture e fatture_righe a migration 001
- **Schema fatture (001)**: id, numero, anno, numero_completo, cliente_id, imponibile, iva, totale, stato, data_emissione, data_scadenza, metodo_pagamento
- **Schema fatture_righe (001)**: id, fattura_id, descrizione, quantita, prezzo_unitario, iva_percentuale, totale_riga, ordine
- **DELETE**: Modificati per essere più sicuri con WHERE clause

### 2. Setup Wizard (NEW FEATURE)

#### Backend (Rust) - `src-tauri/src/commands/setup.rs`
4 nuovi Tauri commands:
- `get_setup_status`: Verifica se setup completato
- `save_setup_config`: Salva configurazione iniziale
- `get_setup_config`: Ottieni configurazione corrente
- `reset_setup`: Reset setup (per test)

Configurazione salvata in tabella `impostazioni` (già esistente da migration 001).

#### Frontend (React)
- `src/types/setup.ts`: Zod schemas + types
- `src/hooks/use-setup.ts`: TanStack Query hooks
- `src/components/setup/SetupWizard.tsx`: Wizard 4 step
- `src/App.tsx`: Mostra wizard se setup non completato

#### Step del Wizard
1. **Dati Attività**: Nome, P.IVA, CF, telefono, email
2. **Sede Legale**: Indirizzo, CAP, città, provincia, PEC
3. **Configurazione**: Categoria attività, regime fiscale, Groq API key (opzionale)
4. **Riepilogo**: Conferma e salvataggio

### 3. Fix .env
Quotati valori con spazi:
```
AZIENDA_NOME="Automation Business"
AZIENDA_INDIRIZZO="Via degli Ulivi 16"
BRAND_TAGLINE="Gestionale Enterprise per PMI Italiane"
```

## Commit
- `25efcf3`: fix(mock): use migration 001 schema for fatture tables
- `fd265fb`: feat(setup): add Setup Wizard for initial configuration

## CI/CD Status
Run #20751825131:
- ✅ Frontend Tests: SUCCESS
- ✅ Code Quality: SUCCESS
- 🔄 Backend Tests: IN PROGRESS
- 🔄 Build Tauri App: IN PROGRESS

## Test su iMac (TODO)
```bash
# 1. Sincronizza
cd /Volumes/MacSSD\ -\ Dati/fluxion
git pull

# 2. Fix .env (aggiungi virgolette ai valori con spazi)
nano .env
# AZIENDA_NOME="Automation Business"

# 3. Avvia app
npm run tauri dev

# 4. Al primo avvio verrà mostrato Setup Wizard
# Compila i campi e clicca "Completa Setup"

# 5. Dopo setup, importa mock data
sqlite3 ~/Library/Application\ Support/com.fluxion.desktop/fluxion.db < scripts/mock_data.sql
```

## Output Atteso mock_data.sql
```
Clienti|10
Servizi|8
Operatori|6
Pacchetti|3
ClientiPacchetti|3
Appuntamenti|20
Fatture|5
FattureRighe|7
```

## Note
- Il Setup Wizard appare solo al primo avvio (se setup_completed != true)
- Le impostazioni sono modificabili dalla pagina Impostazioni
- La Groq API key è opzionale - serve solo per funzionalità RAG/AI
