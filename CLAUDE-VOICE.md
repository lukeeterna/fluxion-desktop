# CLAUDE-VOICE.md — Contesto Voice Agent "Sara"
> Context file caricato dall'agente `voice-engineer`.
> Fonte di verità per architettura, stato corrente, constraint e pattern.

---

## 🏗️ Architettura Runtime

```
aiohttp Server (porta 3002, iMac 192.168.1.9)
├── VoiceOrchestrator (src/orchestrator.py)
│   ├── L0: Regex speciali (annulla, aiuto, operatore) — <1ms
│   ├── L1: IntentClassifier pattern+TF-IDF — <5ms
│   ├── L2: BookingStateMachine slot filling — <10ms
│   ├── L3: FAQManager keyword retrieval — <50ms
│   └── L4: GroqClient LLM fallback — <500ms
├── SessionManager (src/session_manager.py)
│   ├── PRIMARY: SQLite locale ~/.fluxion/voice_sessions.db
│   └── SECONDARY: HTTP Bridge 3001 (best-effort, spesso offline)
├── FluxionVAD (src/vad/ten_vad_integration.py) — Silero ONNX
├── FluxionSTT (src/stt.py) — HybridSTT primario
├── FluxionTTS (src/tts.py) — Piper Italian primario
└── FluxionAnalytics (src/analytics.py) — SQLite turn tracking
```

---

## 🐍 Constraint Python (CRITICO)

| Machine | Python | Constraint |
|---------|--------|------------|
| **iMac** (192.168.1.9) | **3.9** | Runtime produzione — NO PyTorch, usa ONNX Runtime |
| **MacBook** | 3.13 | Dev/test only — NO PyTorch su 3.13 |

**REGOLA**: Usare sempre `onnxruntime`, mai `torch`. VAD usa Silero ONNX.

---

## 🔊 Componenti Fluxion (Branding Unificato)

### FluxionSTT (`src/stt.py`)
```python
# Gerarchia classi STT
class STTEngine(ABC):          # Base abstract
class WhisperOfflineSTT(STTEngine):  # PRIMARY - whisper.cpp locale
    # WER: 9-11% italiano, latency: 2-3s, RAM: 1.5GB
    # Formato: raw PCM audio (non compresso → WER basso)
class GroqSTT(STTEngine):      # FALLBACK - Groq Whisper API
    # WER: ~21.7% (audio compresso via HTTP → qualità peggiore)
class HybridSTT(STTEngine):    # ORCHESTRATORE usato in produzione
    # whisper.cpp → fallback Groq se offline
class WhisperCorrector:        # Post-processing correzioni italiane
```

### FluxionTTS (`src/tts.py`)
```python
# Sintetizza testo in audio
tts = get_tts()
audio_bytes: bytes = await tts.synthesize("Buongiorno!")
# Primary: Piper (it_IT-riccardo-medium.onnx)
# Fallback: System TTS macOS
await tts.synthesize_to_file("testo", "output.wav")
```

### FluxionVAD (`src/vad/ten_vad_integration.py`)
```python
class FluxionVAD:
    # Silero ONNX-based Voice Activity Detection
    # NON usa PyTorch - compatibile Python 3.9/3.13
    # Input: audio chunks raw bytes
    # Output: speech/silence detection
```

---

## 🤖 FSM - 23 Stati Esatti (`src/booking_state_machine.py`)

```python
class BookingState(Enum):
    # Base flow
    IDLE = "idle"
    WAITING_NAME = "waiting_name"
    WAITING_SURNAME = "waiting_surname"
    WAITING_SERVICE = "waiting_service"
    WAITING_DATE = "waiting_date"
    WAITING_TIME = "waiting_time"
    WAITING_OPERATOR = "waiting_operator"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    # Phone verification
    CONFIRMING_PHONE = "confirming_phone"

    # New client registration
    PROPOSE_REGISTRATION = "propose_registration"
    REGISTERING_SURNAME = "registering_surname"
    REGISTERING_PHONE = "registering_phone"
    REGISTERING_CONFIRM = "registering_confirm"

    # Availability / Waitlist
    CHECKING_AVAILABILITY = "checking_availability"
    SLOT_UNAVAILABLE = "slot_unavailable"
    PROPOSING_WAITLIST = "proposing_waitlist"
    CONFIRMING_WAITLIST = "confirming_waitlist"
    WAITLIST_SAVED = "waitlist_saved"

    # Graceful close
    ASKING_CLOSE_CONFIRMATION = "asking_close_confirmation"

    # Disambiguation
    DISAMBIGUATING_NAME = "disambiguating_name"
    DISAMBIGUATING_BIRTH_DATE = "disambiguating_birth_date"
```

---

## 🎯 Intent Categories (`src/intent_classifier.py`)

```python
class IntentCategory(Enum):
    CORTESIA = "cortesia"          # buongiorno, grazie, ciao
    PRENOTAZIONE = "prenotazione"  # voglio prenotare, appuntamento
    CANCELLAZIONE = "cancellazione" # cancellare, disdire
    SPOSTAMENTO = "spostamento"    # spostare, cambiare data
    WAITLIST = "waitlist"          # lista d'attesa
    INFO = "info"                  # prezzi, orari, servizi
    CONFERMA = "conferma"          # sì, confermo, ok
    RIFIUTO = "rifiuto"            # no, annulla, non voglio
    OPERATORE = "operatore"        # voglio parlare con qualcuno
    UNKNOWN = "unknown"            # fallback → L4 Groq
```

---

## 🔤 Disambiguazione Fonetica (`src/disambiguation_handler.py`)

```python
# Levenshtein similarity threshold: 70%
# PHONETIC_VARIANTS dict per nomi italiani comuni
PHONETIC_VARIANTS = {
    "Gigio": ["Gino", "Luigi", "Gigio"],
    "Mario": ["Maria", "Marione"],
    # ... altri casi
}

# Gerarchia disambiguazione:
# 1. Controllo PHONETIC_VARIANTS (exact + variants)
# 2. Levenshtein similarity ≥ 0.70
# 3. Chiedi data di nascita
# 4. Chiedi soprannome/nickname
```

---

## 🗄️ Session Persistence (post T2, 2026-02-21)

```python
# PRIMARY (sempre disponibile)
db_path = "~/.fluxion/voice_sessions.db"
# Tables: voice_sessions, voice_audit_log

# SECONDARY (best-effort)
http_bridge = "http://127.0.0.1:3001"  # spesso offline!

# Recovery automatica al restart:
# SessionManager.__init__() → _recover_sessions()
# Carica ACTIVE/IDLE non-scadute da SQLite in memoria
```

---

## 📡 API Endpoints (porta 3002)

```bash
# Health check
GET  http://192.168.1.9:3002/health

# Processa testo (principale)
POST http://192.168.1.9:3002/api/voice/process
Body: {"text": "Buongiorno, sono Marco Rossi", "session_id": "optional"}
Response: {"response": "...", "state": "...", "session_id": "..."}

# Reset sessione
POST http://192.168.1.9:3002/api/voice/reset

# VAD: stream audio chunks
POST http://192.168.1.9:3002/api/vad/start
POST http://192.168.1.9:3002/api/vad/chunk   # binary audio
POST http://192.168.1.9:3002/api/vad/stop
```

---

## ⚡ Latency Budget (Target P95 < 800ms)

| Componente | Attuale | Target | Stato |
|------------|---------|--------|-------|
| STT (Whisper local) | 200-400ms | <300ms | ⚠️ |
| Intent + FSM | 5-15ms | <20ms | ✅ |
| LLM Groq (L4) | 500-800ms | <500ms | ⚠️ |
| TTS Piper | 100-300ms | <200ms | ⚠️ |
| **E2E totale** | **~1330ms** | **<800ms** | 🔴 |

**Nota**: L4 Groq usato solo per UNKNOWN intent. L1-L3 sono <50ms totali.

---

## 🚨 Problemi Noti e Workaround

### HTTP Bridge (3001) offline
- **Sintomo**: `persist_session()` restituisce False
- **Non è un errore**: SQLite locale è primary, Bridge è best-effort
- **Log**: `[SessionManager] Bridge sync warning: HTTP 500`

### Python 3.13 su MacBook
- `import torch` → ImportError (normale, atteso)
- Usare sempre ONNX Runtime per VAD
- Test suite usa mock per componenti ONNX

### WER Alto (21.7% vs target 9-11%)
- **Causa**: GroqSTT usa audio compresso HTTP
- **Fix**: HybridSTT usa WhisperOfflineSTT locale come primary
- Restart pipeline dopo ogni modifica a stt.py

---

## 🔧 Comandi Operativi

```bash
# Restart pipeline su iMac (DOPO ogni modifica Python)
ssh imac "pkill -f 'python main.py'; sleep 1; \
  cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  source venv/bin/activate && \
  nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"

# Log real-time
ssh imac "tail -f /tmp/voice-pipeline.log"

# Test suite (su iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  source venv/bin/activate && \
  python -m pytest tests/ -v --tb=short"

# Test veloce da MacBook
source /Volumes/MontereyT7/FLUXION/voice-agent/venv/bin/activate && \
  cd /Volumes/MontereyT7/FLUXION/voice-agent && \
  python -m pytest tests/test_session_persistence.py -v

# Health check live
curl http://192.168.1.9:3002/health
```

---

## 📁 File Chiave con Path Assoluti

```
voice-agent/
  main.py                              # Entry point aiohttp (3002)
  src/
    orchestrator.py                    # VoiceOrchestrator — pipeline coordinator
    booking_state_machine.py           # BookingStateMachine — 23 stati, 1900+ righe
    booking_orchestrator.py            # BookingOrchestrator — high-level booking
    session_manager.py                 # SessionManager — dual SQLite+Bridge storage
    intent_classifier.py               # IntentCategory, classify_intent()
    disambiguation_handler.py          # DisambiguationHandler, PHONETIC_VARIANTS
    entity_extractor.py                # Estrazione nome/data/ora da testo italiano
    analytics.py                       # ConversationLogger — SQLite analytics
    groq_client.py                     # GroqClient — LLM + circuit breaker
    stt.py                             # HybridSTT (WhisperOfflineSTT + GroqSTT)
    tts.py                             # FluxionTTS (Piper + System fallback)
    vad/ten_vad_integration.py         # FluxionVAD — Silero ONNX
    whatsapp.py                        # WhatsApp Business via ehiweb
    availability_checker.py            # Disponibilità slot + pausa pranzo
    italian_regex.py                   # L0 regex: prefilter, strip_fillers
  tests/
    test_voice_agent_complete.py       # 58 test — suite principale
    test_session_persistence.py        # 27 test — SQLite persistence (T2)
    test_booking_state_machine.py      # FSM unit tests
    test_disambiguation.py             # Phonetic matching tests
  data/
    faq_salone.json                    # FAQ per verticale salone
    faq_medical.json                   # FAQ per verticale medical
```

---

## 🎯 Scenari Test Live (T1 — da eseguire su iMac)

```bash
# 1. Disambiguazione fonetica: "Gino" vs "Gigio"
curl -X POST http://192.168.1.9:3002/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text":"Buongiorno, sono Gino Peruzzi"}'
# Atteso: chiede "Mi scusi, ha detto Gino o Gigio?"

# 2. Flusso prenotazione completo
curl -X POST http://192.168.1.9:3002/api/voice/process \
  -d '{"text":"Vorrei prenotare un taglio per domani alle 15"}'
# Atteso: stato WAITING_NAME → slot filling

# 3. Slot occupato → Waitlist
curl -X POST http://192.168.1.9:3002/api/voice/process \
  -d '{"text":"Mettetemi in lista d'\''attesa"}'
# Atteso: stato PROPOSING_WAITLIST → WAITLIST_SAVED

# 4. Chiusura graceful
curl -X POST http://192.168.1.9:3002/api/voice/process \
  -d '{"text":"Grazie, arrivederci"}'
# Atteso: stato ASKING_CLOSE_CONFIRMATION → WhatsApp inviato → CLOSED
```
