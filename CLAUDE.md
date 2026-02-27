# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: Saloni, palestre, cliniche, officine (1-15 dipendenti)
- **Model**: Licenza LIFETIME desktop (NO SaaS, NO commissioni)
- **Voice**: "Sara" - assistente vocale prenotazioni (5-layer RAG pipeline)
- **License**: Ed25519 offline, 3 tier (Base/Pro/Enterprise), 6 verticali

## 🏛️ I 3 PILASTRI (Core Business)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXION - I 3 PILASTRI                       │
├─────────────────────────────────────────────────────────────────┤
│  📱 COMUNICAZIONE      🎯 MARKETING        ⚙️ GESTIONE          │
│  WhatsApp + Voice      Loyalty + Pacchetti  Calendario + Schede │
│                                                                  │
│  → Sostituisce l'operatore        → PMI non hanno tempo        │
│  → 24/7 automatico                → Zero-cost marketing         │
│  → Vantaggio competitivo          → Automazione completa        │
└─────────────────────────────────────────────────────────────────┘
```

**Questi 3 pilastri devono essere PERFETTI - sono il cuore del prodotto.**

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
branch: master
phase: Voice Agent Enterprise v2.1.0 - Test Suite Completo + Network Fix
status: 100% test suite (58/58), URL fixato, pronto per test live audio reale
date: 2026-02-12
tests: 
  - voice-agent: 58/58 passing ✅
  - TypeScript: type-check OK ✅
  - Cross-machine: Health ✅ API ✅
fixes_oggi:
  - Frontend URL: localhost:3002 → 192.168.1.7:3002
  - Dependency injection: db_lookup mockable
  - Test suite: 58/58 passati
blockers_test_live:
  - Latenza audio reale da verificare (~1330ms vs <800ms target)
  - Tauri Bridge integrazione non completa
next_step: Test live con audio reale → Build v0.9.0
```

## 🎯 OBIETTIVO: VOICE AGENT ENTERPRISE v1.0 (Best Practice 2026)

### 📱 COMUNICAZIONE PERFETTA (Voice Agent "Sara")

**Stack Tecnologico Fluxion (Branding Unificato):**
```
🎤 STT:  FluxionSTT (Whisper.cpp + Groq Whisper fallback)
🧠 LLM:  Groq API (llama-3.3-70b-versatile)
🔊 TTS:  FluxionTTS (Piper Italian + System fallback)
👂 VAD:  FluxionVAD (Silero ONNX-based, rinominato)
🧭 FSM:  FluxionStateMachine (23 stati, 1500+ righe)
📊 Analytics: FluxionAnalytics (turn-level logging)
```

**CoVe Verification (2026-02-12):**
| Componente | Stato | Note |
|------------|-------|------|
| FluxionSTT | ✅ OK | Whisper.cpp locale + Groq fallback |
| FluxionTTS | ✅ OK | Piper italiano implementato |
| FluxionVAD | ✅ OK | Silero-based, ONNX Runtime |
| FluxionAnalytics | ✅ OK | Turn tracking completo (analytics.py) |
| State Machine (23 stati) | ✅ OK | Esattamente 23 stati confermati |
| Test Suite Completa | ✅ 58/58 | test_voice_agent_complete.py |
| Disambiguazione | ✅ OK | Phonetic matching + Dependency Injection |
| Intent Classification | ✅ OK | Pattern + Semantic (confidence 0.65+) |
| Error Recovery | ✅ OK | handle_input_with_confidence, handle_api_error |
| Test Cross-Machine | ✅ OK | MacBook → iMac (192.168.1.7:3002) |
| Latency Optimizer | ⚠️ NA | Non ancora implementato (TODO v1.1) |
| Streaming LLM | ⚠️ NA | Non ancora implementato (TODO v1.1) |
| **Test Live Audio** | 🔴 **TODO** | Da fare per validare latenza reale |

**Best Practice 2026 Implementate:**
- ✅ **Phonetic Matching**: Levenshtein distance per Gino/Gigio, Maria/Mario
- ✅ **Turn-Level Observability**: FluxionAnalytics con SQLite backend
- ✅ **Intent Pattern Matching**: Regex italiani + Semantic TF-IDF fallback
- ✅ **Connection Pooling**: HTTP keep-alive per Groq API
- ✅ **4-Layer RAG Pipeline**: L0-L4 con escalation graceful
- ✅ **State Machine Strict**: 23 stati con transizioni esplicite
- ✅ **Error Recovery**: Fallback chain per ogni componente

**Fix Recentemente Completati (2026-02-12):**
- ✅ **Test Suite**: 58/58 test passati (CoVe 2026)
- ✅ **Network Fix**: Frontend URL localhost:3002 → 192.168.1.7:3002 (iMac)
- ✅ **Dependency Injection**: `db_lookup` mockable per test unitari
- ✅ **Error Recovery**: `handle_input_with_confidence()`, `handle_api_error()`
- ✅ **Intent Confidence**: Base 0.65 + strong keyword boost
- ✅ **Disambiguazione Fonetics**: PHONETIC_VARIANTS + phonetic ambiguity detection
- ✅ **Soprannomi**: Nickname recognition (Gigi → Gigio, Giovi → Giovanna)
- ✅ **Entity Extraction**: DEFAULT_SERVICES_CONFIG per test
- ✅ **Analytics DB**: In-memory connection reuse fix
- ✅ **WhatsApp Fix**: Invio conferma post-booking con numero corretto
- ✅ **Chiusura Graceful**: Stato `ASKING_CLOSE_CONFIRMATION`

### 🎯 MARKETING (Zero-Cost per PMI)
- ✅ Sistema Loyalty (timbri, VIP, referral)
- ✅ Pacchetti servizi (creazione, sostistica libera)
- ✅ Database: `is_vip`, `loyalty_visits`, `consenso_whatsapp`
- 🔴 **DA FARE**: Invio WhatsApp pacchetti filtrato per VIP/stelle

### ⚙️ GESTIONE (Automazione Completa)
- ✅ Calendario + Booking con state machine
- ✅ 3 Schede verticali complete (Odontoiatrica, Fisioterapia, Estetica)
- ✅ Fatturazione elettronica XML
- 📝 5 Schede placeholder (da fare in Fase 2)

## 📋 TASK CRITICHE DA COMPLETARE

### 🔴 Priorità Massima (Prima del Build)
1. **Test Live Voice Agent** (su iMac)
   - Scenario "Gino vs Gigio" - Verificare disambiguazione fonetica
   - Scenario "Chiusura Graceful" - Conferma WhatsApp e termine chiamata
   - Scenario "Flusso Perfetto" - Booking completo end-to-end
   - Scenario "WAITLIST" - Slot occupato → lista d'attesa

2. **WhatsApp Pacchetti Selettivo**
   - UI in `PacchettiAdmin.tsx` o scheda cliente
   - Filtri: Tutti (con consenso) | VIP | VIP 3+ stelle
   - Template WhatsApp con nome attività
   - Rate limiting 60 msg/ora
   - Tracking invio

3. **Voice Agent Greeting Dinamico**
   - Leggere `nome_attivita` da impostazioni
   - "Buongiorno, sono Sara di {nome_attivita}"
   - Integrare in tutti i messaggi vocali

4. **Build Produzione v0.9.0**
   - Solo dopo test live superati
   - Verificare Fluxion.app ~16MB
   - Tag release v0.9.0

### 🟡 Priorità Media (Voice Agent v1.1)
5. **Latency Optimization Kit**
   - Streaming LLM tokens to TTS
   - Connection pool per Groq
   - Target: P95 < 800ms (attuale ~1300ms)

6. **5 Schede Verticali Placeholder**
   - Parrucchiere, Veicoli, Carrozzeria, Medica, Fitness

## ✅ IMPLEMENTATO (CoVe Verified 2026-02-11)

### Voice Agent Enterprise v1.0 ✅
- **FluxionSTT**: Whisper.cpp offline + Groq Whisper fallback (WER 9-11%)
- **FluxionTTS**: Piper Italian primary + System TTS fallback
- **FluxionVAD**: Silero ONNX-based (rinominato da SileroVAD)
- **FluxionAnalytics**: Turn-level logging completo con SQLite
- **State Machine**: 23 stati esatti, 1500+ righe
- **Disambiguazione**: Levenshtein + PHONETIC_VARIANTS
- **Test**: 780+ test functions, test_booking_e2e_complete.py (535 righe)

### Setup Wizard v2 ✅
- Campi `whatsapp_number`, `ehiweb_number`, `nome_attivita`
- Migration 021
- TypeScript + Rust API

## 📁 FILE CHIAVE (Voice Agent)

```
# Core Voice Agent
voice-agent/main.py                         # Entry point HTTP server (porta 3002)
voice-agent/src/booking_state_machine.py    # 23 stati FSM
voice-agent/src/orchestrator.py             # 4-layer RAG pipeline
voice-agent/src/analytics.py                # FluxionAnalytics (turn tracking)

# Fluxion Components (Branding Unificato)
voice-agent/src/stt.py                      # FluxionSTT (Whisper.cpp + Groq)
voice-agent/src/tts.py                      # FluxionTTS (Piper)
voice-agent/src/vad/ten_vad_integration.py  # FluxionVAD (Silero-based)
voice-agent/src/disambiguation_handler.py   # Phonetic matching
voice-agent/src/intent_classifier.py        # Intent classification

# Test Suite
voice-agent/tests/test_booking_e2e_complete.py    # 20 test E2E
voice-agent/tests/test_booking_state_machine.py   # FSM tests
voice-agent/tests/test_disambiguation.py          # Phonetic tests
voice-agent/tests/test_analytics.py               # Analytics tests

# Validation
voice-agent/validation/whisper_wer_validator.py   # STT accuracy
voice-agent/validation/piper_latency_validator.py # TTS latency
```

## 🔧 COMANDI RAPIDI

```bash
# Test (MacBook)
cd /Volumes/MontereyT7/FLUXION
npm run type-check

# Test Voice Agent (iMac via SSH)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short"

# Test (iMac via SSH - Rust)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && export PATH='/Users/gianlucadistasi/.cargo/bin:$PATH' && cargo test --lib"

# Build (SOLO a fine sviluppo, su iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && export PATH='/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH' && npm run tauri build"

# Sync
git add -A && git commit -m "..." && git push origin master
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
```

## 📚 DOCUMENTAZIONE

- **PRD**: `PRD-FLUXION-COMPLETE.md` ⭐ Documento di verità
- **Prompt**: `PROMPT-COMPLETO-VOICE-AGENT-FINAL.md` - Voice Agent Enterprise
- **CoVe Report**: `COVE-VERIFICATION-REPORT.md` - Verifica autonoma 2026-02-11
- **Agents**: `AGENTS.md` - Istruzioni agenti AI

## Context Status
🟡 **95%** - Voice Agent Enterprise completo (CoVe verified), pronto per test live
Last save: 2026-02-11
Action: Test Live Voice Agent su iMac + Build Finale v0.9.0

## 🧪 TEST LIVE PREPARATI (su iMac)

### Scenari Voice Agent "Sara" (Best Practice 2026):

1. **"Gino vs Gigio"** - Disambiguazione fonetica
   - Input: "Sono Gino Peruzzi" (DB: Gigio Peruzzi)
   - Atteso: "Mi scusi, ha detto Gino o Gigio?"
   - Verifica: Levenshtein similarity ≥70% triggera disambiguazione

2. **"Soprannome VIP"** - Riconoscimento nickname
   - Input: "Sono Gigi Peruzzi" (Gigi = soprannome Gigio)
   - Atteso: "Ciao Gigi! Bentornato Gigio!"
   - Verifica: Nickname → nome canonico

3. **"Chiusura Graceful"** - Post-booking
   - Input: "Confermo chiusura"
   - Atteso: WhatsApp inviato + "Grazie, arrivederci!"
   - Verifica: Stato ASKING_CLOSE_CONFIRMATION

4. **"Flusso Perfetto"** - End-to-end
   - Input: Nuovo cliente completo
   - Atteso: Registrazione + booking + WhatsApp + chiusura
   - Verifica: Analytics logging completo

5. **"WAITLIST"** - Slot occupato
   - Input: "Vorrei domani alle 15" (slot occupato) → "Mettetemi in lista"
   - Atteso: Salvataggio waitlist + conferma WhatsApp
   - Verifica: Stato PROPOSING_WAITLIST → WAITLIST_SAVED

### Endpoint Test:
```bash
# Health check
curl http://localhost:3002/health

# Process text
curl -X POST http://localhost:3002/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text":"Buongiorno, sono Marco Rossi"}'

# Reset session
curl -X POST http://localhost:3002/api/voice/reset
```
