# Sessione: FLUXION IA Branding + Setup Wizard Fix

**Data**: 2026-01-06T18:30:00
**Fase**: 7 - Voice Agent + WhatsApp
**Agente**: rust-backend, react-frontend

## Obiettivi Sessione
1. Fix errori mock_data.sql (completato sessione precedente)
2. Rinominare "Groq" → "FLUXION IA" in tutta l'app
3. Permettere configurazione API key senza .env (via Setup Wizard)

## Test iMac Effettuati (dal utente)

### ✅ mock_data.sql - SUCCESSO
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

### ✅ Setup Wizard - SUCCESSO
```
✅ Setup completato per: ALMA di Di Stasi Mario Gianluca
```

### ⚠️ .env parsing - WARNING (non bloccante)
```
⚠️  .env file not found or invalid: Error parsing line: 'BRAND_TAGLINE=...'
```
Nota: Non bloccante perché ora la chiave FLUXION IA viene salvata nel database.

## Modifiche Effettuate

### 1. Rinominato "Groq" → "FLUXION IA"

#### Frontend
- `src/types/setup.ts`: `groq_api_key` → `fluxion_ia_key`
- `src/components/setup/SetupWizard.tsx`:
  - Label: "FLUXION IA Key (opzionale - per assistente intelligente)"
  - Placeholder: "Inserisci la chiave ricevuta"
  - Helper: "Chiave fornita con la licenza FLUXION per funzionalità AI avanzate"
  - Riepilogo: "FLUXION IA" invece di "API Groq"
- `src/components/rag/RagChat.tsx`:
  - Titolo: "FLUXION IA - Assistente"
  - Messaggio connessione: "✓ FLUXION IA connesso"
- `src/pages/Impostazioni.tsx`:
  - Sezione: "FLUXION IA" invece di "Assistente AI (RAG Test)"
- `src/hooks/use-rag.ts`: Commento aggiornato
- `src/types/rag.ts`: Commento aggiornato

#### Backend (Rust)
- `src-tauri/src/commands/setup.rs`: `groq_api_key` → `fluxion_ia_key`
- `src-tauri/src/commands/rag.rs`:
  - Nuova funzione `get_fluxion_ia_key()`:
    1. Prima legge da DB (impostazioni.fluxion_ia_key)
    2. Fallback a .env (GROQ_API_KEY)
  - `rag_answer()` e `test_groq_connection()` ora usano `State<'_, SqlitePool>`
  - Messaggi errore user-friendly senza menzionare "Groq"
- `src-tauri/src/lib.rs`: Messaggio .env aggiornato

### 2. Logica API Key (IMPORTANTE)

```
┌─────────────────────────────────────────────────────────────┐
│                    Ricerca API Key                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Cerca in DB: SELECT valore FROM impostazioni             │
│    WHERE chiave = 'fluxion_ia_key'                          │
│                                                             │
│ 2. Se non trovata → Fallback a .env GROQ_API_KEY           │
│                                                             │
│ 3. Se nessuna → Errore: "FLUXION IA non configurato.       │
│    Inserisci la chiave nella pagina Impostazioni o nel     │
│    Setup Wizard."                                           │
└─────────────────────────────────────────────────────────────┘
```

## File Modificati
- `src-tauri/src/commands/rag.rs`
- `src-tauri/src/commands/setup.rs`
- `src-tauri/src/lib.rs`
- `src/components/rag/RagChat.tsx`
- `src/components/setup/SetupWizard.tsx`
- `src/hooks/use-rag.ts`
- `src/pages/Impostazioni.tsx`
- `src/types/rag.ts`
- `src/types/setup.ts`

## Commit
- `cbab635`: refactor(branding): rename Groq to FLUXION IA

## CI/CD Status
- Push effettuato, in attesa risultati CI

## Test Pendenti (su iMac - DOMANI)
1. `git pull` per sincronizzare
2. `npm run tauri dev` per avviare app
3. Verificare che Setup Wizard mostri "FLUXION IA Key"
4. Inserire chiave FLUXION IA nel wizard
5. Verificare che FLUXION IA funzioni nelle Impostazioni
6. Verificare che Fatture page mostri i 5 mock records

## Note
- La chiave Groq (`gsk_...`) funziona come "FLUXION IA Key" - è solo un rebranding
- L'utente finale non vedrà mai "Groq" nell'interfaccia
- Il .env è ora opzionale per la chiave AI (può essere configurata via UI)
