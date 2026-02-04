# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: Saloni, palestre, cliniche, officine (1-15 dipendenti)
- **Model**: Licenza LIFETIME desktop (NO SaaS, NO commissioni)
- **Voice**: "Sara" - assistente vocale prenotazioni (5-layer RAG pipeline)
- **License**: Ed25519 offline, 3 tier (Base/Intermedia/Full), 6 verticali

## Critical Rules
1. Never commit API keys, secrets, or .env files
2. Always TypeScript (never JS), always async Tauri commands
3. Run tests before commit (see `.claude/rules/testing.md` for checklist)
4. A task is NOT complete until code works AND is verified (DB records, E2E)
5. Italian field names in APIs: `servizio`, `data`, `ora`, `cliente_id`
6. Dev on MacBook, test on iMac (192.168.1.7) - Tauri needs macOS 12+
7. Restart voice pipeline on iMac after ANY Python change

## Active Sprint
```yaml
branch: feat/workflow-tools
phase: Research & Architecture (Micro-categorie + License System)
status: Context 71.4% - CHECKPOINT for tomorrow
tests: 955 passing (voice-agent)
next_step: Implementazione Fase 1 (Parrucchiere + Estetista + License)
```

## Stato Attuale (2026-02-03)

### Completato Oggi
1. **Research 6 Verticali**: Meccanico, Fisioterapia, Dentista, Fitness, Parrucchiere, Estetista + Chirurgia estetica
2. **Benchmark Competitor**: Analisi 20+ prodotti, Fluxion 97% più economico (Lifetime vs SaaS)
3. **Micro-categorie**: 100+ categorie mappate (dentista → implantologo, fisio → sportivo, etc.)
4. **License System**: Deciso Ed25519 offline-first, 3 tier (€199/€399/€799), hardware-locked
5. **Voice Agent Analysis**: Identificati problemi reali (nomi composti, date relative, servizi multipli)
6. **Prompts Creati**: 
   - `IDENTIFICA-MICRO-CATEGORIE-VOICE-STACK.prompt.md` (merged con analisi stack)
   - Prompt per Kimi Pro ricerca mercato

### Documenti Creati
- `docs/VERTICALS-FINAL-6.md` - Schema 6 verticali completo
- `docs/BENCHMARK-COMPETITORS.md` - Analisi prezzi competitor
- `docs/MICRO-CATEGORIE-PMI.md` - 100+ micro-categorie
- `docs/INFRASTRUCTURE-MOCKUP.md` - Architettura implementazione
- `.kimi/prompts/IDENTIFICA-MICRO-CATEGORIE-VOICE-STACK.prompt.md` - Prompt ricerca

### Problemi Voice Agent Identificati (dalle conversazioni)
1. **Nomi/Cognomi**: "Gino Di Nanni" → perde "Gino" o "Nanni"
2. **Date relative**: "settimana prossima" → non capisce (fix parziale in place)
3. **Vincoli orari**: "dopo le 17" → propone orari sbagliati
4. **Servizi multipli**: "taglio, colore e barba" → a volte perde pezzi
5. **Persistenza**: Dopo prenotazione, perde contesto su nuove domande

### Decisioni Business
- **Modello vendita**: Passaparola → Contatto diretto → Bonifico Revolut
- **Installazione**: Remota da te (AnyDesk/TeamViewer)
- **Configurazione**: Tu installi licenza + Keygen + Gmail SMTP
- **Wizard primo avvio**: Utente seleziona macro → micro categoria
- **Supporto**: Remoto incluso (WhatsApp + AnyDesk)

### Prossimi Step (Domani)
1. Utente fornisce output dal prompt di ricerca micro-categorie
2. Implementazione Fase 1:
   - Sistema licenze Ed25519
   - Verticali: Parrucchiere + Estetista
   - DB migrations
   - Rust domain layer
   - React UI
3. Test Voice Agent su casi reali

## Technical Notes

### Voice Agent Stack (Stato Attuale)
```
L0 (Regex): ✅ OK - Filler, conferme, escalation
L1 (Intent): ✅ OK - 10 intents base
L2 (Entities): ⚠️ Problematico - Nomi composti, date relative
L3 (RAG): ✅ OK - FAQ semplici
L4 (LLM): ⚠️ Fallback lento
```

### License System Architecture
```
Ed25519 Keypair (embedded in binary)
  ↓
License JSON (hardware_fingerprint + verticals + tier)
  ↓
Offline verification (no server)
  ↓
Unlock verticals in UI
```

### Database Schema (Da creare)
- `licenze_config` (singleton)
- `par_colorazioni`, `par_tagli`
- `est_analisi_pelle`, `est_trattamenti`
- (e altri 4 verticali in Fasi successive)

## Checkpoint Files (per ripartenza)
- `docs/VERTICALS-FINAL-6.md`
- `.kimi/prompts/IDENTIFICA-MICRO-CATEGORIE-VOICE-STACK.prompt.md`
- `docs/BENCHMARK-COMPETITORS.md`
- `docs/MICRO-CATEGORIE-PMI.md`

## Context Status
⚠️ **71.4%** - Compact imminent
Last save: 2026-02-03 18:45
Action: Ripartire dai file di documento, non dal contesto conversazione.
