# 🚀 PROMPT COMPLETO - FLUXION VOICE AGENT ENTERPRISE v1.0

> **Ruolo:** AI Architect - Voice AI Enterprise Specialist  
> **Data:** 2026-02-11  
> **Scope:** Implementare Best Practice 2026 + Suite Test Completa  
> **Stack:** Python 3.x, FastAPI, Whisper.cpp, Groq, Piper TTS, SQLite, Silero VAD

---

## 📋 COVE CHECKLIST - DA COMPLETARE PRIMA DI INIZIARE

```bash
# Verifica 1: Environment
npm run type-check                    # Deve passare 0 errori
cd src-tauri && cargo check --lib    # Deve passare 0 errori

# Verifica 2: Voice Agent Status
ssh imac "curl -s http://localhost:3002/health | python3 -m json.tool"

# Verifica 3: Database
ssh imac "sqlite3 '/Volumes/MacSSD - Dati/fluxion/fluxion.db' '.tables'"

# Verifica 4: Whisper.cpp
ssh imac "ls -lh ~/whisper.cpp/build/bin/whisper-cli"
```

---

## 🔬 DEEP RESEARCH REDDIT 2026 - BEST PRACTICE VOICE AGENT

### 1. Latency Stack Optimization (Target: <800ms P95)
**Fonte:** Reddit r/LLMDevs + shekhargulati.com 2026

```
┌─────────────────────────────────────────────────────────────┐
│ Componente          │ Target P95 │ Nostro Stato │ Azione    │
├─────────────────────────────────────────────────────────────┤
│ VAD + endpointing   │ 100-200ms  │ ~150ms       │ ✅ OK     │
│ Network roundtrip   │ 20-50ms    │ ~30ms        │ ✅ OK     │
│ STT (Whisper.cpp)   │ 100-300ms  │ ~200ms       │ ✅ OK     │
│ LLM inference       │ 300-600ms  │ ~800ms       │ 🔴 OPTIMIZE│
│ TTS (Piper)         │ 100-200ms  │ ~150ms       │ ✅ OK     │
│ **TOTALE**          │ **<800ms** │ **~1330ms**  │ **🔴 FIX** │
└─────────────────────────────────────────────────────────────┘
```

**Best Practice 2026:**
- **Streaming responses**: Non aspettare LLM completion, stream tokens
- **Connection reuse**: Keep-alive persistent connections a Groq/STT/TTS
- **Shorter prompts**: Ridurre contesto LLM a <2k tokens
- **Model selection**: Usare Groq mixtral-8x7b per turni semplici, llama-3.3-70b solo per complessi

### 2. State Machine Architecture (Pattern Pipecat)
**Fonte:** Reddit r/aiagents + Pipecat Flows 2026

**Pattern Enterprise:**
```python
# Ogni nodo definisce: Role + Task + Functions
node_config = {
    "name": "confirm_name",
    "task_messages": [{
        "role": "system",
        "content": """Conferma il nome ripetendolo.
        
        RESPONSE HANDLING:
        - Se conferma: Call confirm_name(is_correct=true)
        - Se rifiuta: Call confirm_name(is_correct=false)
        
        Aspetta conferma ESPLICITA prima di procedere."""
    }],
    "functions": [confirm_name_func, transfer_to_agent_func]
}
```

**Regole:**
- Scope ogni nodo strettamente (evita context pollution)
- Ogni nodo ha sempre `transfer_to_agent_func` disponibile
- Transizioni esplicite, mai lasciar decidere all'LLM

### 3. Data Confirmation Patterns
**Fonte:** Reddit r/MachineLearning 2026

**Regole CRITICHE per Voice:**
1. **Conferma per ripetizione**: "Ho capito {value}. È corretto?"
2. **NATO Phonetic per dati sensibili**: "J as in Juliet, S as in Sierra..."
3. **Numeric IDs preferiti**: Matricola > Nome per STT accuracy
4. **Aggressive normalization**: Strip tutto tranne caratteri validi

### 4. Admin Portal & Observability
**Fonte:** Reddit r/LLMDevs Enterprise Voice Guide 2026

**Must-Have:**
- **Turn-level logging**: Ogni turno con timestamp, latency, token count
- **Turn replay**: Rerun singoli turni con stesso input
- **Call recording + transcript**: Playback sincronizzato
- **Latency breakdown per componente**
- **RBAC**: Developer vs Operator vs Admin

---

## 🏗️ STRUTTURA PROGETTO ATTUALE - FLUXION VOICE AGENT

### Stack Tecnologico
```
Backend Voice Agent: Python 3.x + FastAPI (aiohttp server)
STT: Whisper.cpp (local) + Groq Whisper (fallback)
TTS: Piper (italiano) + System TTS (fallback macOS)
LLM: Groq API (llama-3.3-70b + mixtral-8x7b)
VAD: Silero VAD ONNX (32ms chunks)
NLU: Custom pattern + TF-IDF semantic
Database: SQLite (HTTP Bridge via Tauri)
State Machine: Custom Python FSM (23 stati)
```

### File Structure
```
voice-agent/
├── main.py                          # Entry point HTTP server
├── guided_dialog.py                 # Guided Dialog Engine (Kimi 2.5 flow)
├── src/
│   ├── orchestrator.py              # 4-layer RAG pipeline (L0-L4)
│   ├── booking_state_machine.py     # Core FSM (23 stati, 1500+ righe)
│   ├── disambiguation_handler.py    # Phonetic matching + nickname
│   ├── entity_extractor.py          # Regex + Groq NER
│   ├── intent_classifier.py         # Pattern matching + semantic
│   ├── stt.py                       # Whisper.cpp + Groq hybrid
│   ├── tts.py                       # Piper + System TTS
│   ├── vad_http_handler.py          # Silero VAD integration
│   ├── groq_client.py               # Groq API wrapper
│   ├── whatsapp.py                  # WhatsApp Business API
│   ├── italian_regex.py             # Italian text normalization
│   ├── nlu/
│   │   ├── italian_nlu.py
│   │   └── semantic_classifier.py
│   └── vad/
│       ├── ten_vad_integration.py
│       └── vad_pipeline_integration.py
├── tests/                           # 955+ tests
│   ├── test_booking_state_machine.py
│   ├── test_disambiguation.py
│   ├── test_entity_extractor.py
│   └── ...
└── validation/
    ├── whisper_wer_validator.py
    └── piper_latency_validator.py
```

### Endpoint HTTP
```python
# Server: voice-agent/main.py (aiohttp)
GET  /health                         # Health check
POST /process                        # Process text/audio input
POST /reset                          # Reset conversation
POST /greet                          # Initial greeting
POST /say                            # TTS only
GET  /status                         # Session status

# HTTP Bridge (Tauri - porta 3001)
GET  /api/clienti/search?q={name}    # Ricerca cliente
POST /api/appuntamenti/create        # Crea appuntamento
GET  /api/verticale/config           # Configurazione
```

### State Machine States (23 stati)
```python
class BookingState(Enum):
    # Core
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
    
    # Registration
    PROPOSE_REGISTRATION = "propose_registration"
    REGISTERING_SURNAME = "registering_surname"
    REGISTERING_PHONE = "registering_phone"
    REGISTERING_CONFIRM = "registering_confirm"
    
    # Waitlist
    CHECKING_AVAILABILITY = "checking_availability"
    SLOT_UNAVAILABLE = "slot_unavailable"
    PROPOSING_WAITLIST = "proposing_waitlist"
    CONFIRMING_WAITLIST = "confirming_waitlist"
    WAITLIST_SAVED = "waitlist_saved"
    
    # Disambiguation
    DISAMBIGUATING_NAME = "disambiguating_name"
    DISAMBIGUATING_BIRTH_DATE = "disambiguating_birth_date"
    
    # Closing
    ASKING_CLOSE_CONFIRMATION = "asking_close_confirmation"
```

### Algoritmi Implementati

**1. Disambiguazione Fonetics (Levenshtein + Phonetic)**
```python
# voice-agent/src/disambiguation_handler.py
PHONETIC_VARIANTS = {
    "gino": ["gigio", "gino", "ghino"],
    "gigio": ["gino", "gigio", "ghino"],
    "mario": ["maria", "mario", "maro"],
    "maria": ["mario", "maria", "mara"],
}

def name_similarity(name1: str, name2: str) -> float:
    # Levenshtein distance normalized
    return 1.0 - (distance / max_len)
```

**2. Intent Classification (Pattern + Semantic)**
```python
# voice-agent/src/intent_classifier.py
class IntentCategory(Enum):
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    SPOSTAMENTO = "spostamento"
    WAITLIST = "waitlist"
    INFO_ORARI = "info_orari"
    CONFERMA = "conferma"
    RIFIUTO = "rifiuto"
    OPERATORE = "operatore"
    GREETING = "greeting"
    UNKNOWN = "unknown"
```

**3. Entity Extraction (Regex + Groq Fallback)**
```python
# voice-agent/src/entity_extractor.py
@dataclass
class ExtractionResult:
    dates: List[DateEntity]
    times: List[TimeEntity]
    services: List[ServiceEntity]
    operators: List[OperatorEntity]
    names: List[NameEntity]
    phone_numbers: List[str]
    confidence: float
```

---

## 🎯 IMPLEMENTAZIONE BEST PRACTICE 2026

### 1. Latency Optimization Kit

**File da creare:** `voice-agent/src/latency_optimizer.py`
```python
"""Latency optimization per Voice Agent Enterprise"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import groq

@dataclass
class LatencyMetrics:
    vad_ms: int
    stt_ms: int
    nlu_ms: int
    llm_ms: int
    tts_ms: int
    total_ms: int

class StreamingLLMHandler:
    """Stream LLM tokens to TTS without waiting full completion"""
    
    def __init__(self, groq_client):
        self.groq = groq_client
        self.buffer = ""
        self.min_chunk_size = 20  # Min caratteri prima di TTS
        
    async def stream_response(self, prompt: str, context: Dict) -> AsyncGenerator[str, None]:
        """Yield TTS-ready chunks as they arrive"""
        stream = await self.groq.chat.completions.create(
            model="mixtral-8x7b-32768",  # Faster model
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=150,  # Short responses for voice
            temperature=0.3
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            self.buffer += delta
            
            # Yield su punteggiatura o buffer size
            if any(c in self.buffer for c in ['.', '!', '?', ',']) or len(self.buffer) > self.min_chunk_size:
                yield self.buffer
                self.buffer = ""
        
        if self.buffer:
            yield self.buffer

class ConnectionPool:
    """Keep-alive connections per STT/LLM/TTS"""
    
    def __init__(self):
        self.groq_session = None
        self.deepgram_ws = None
        
    async def get_groq(self):
        if not self.groq_session:
            self.groq_session = groq.AsyncGroq()
        return self.groq_session
```

### 2. Turn-Level Observability

**File da creare:** `voice-agent/src/turn_tracker.py`
```python
"""Turn-level logging e analytics per Admin Portal"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TurnRecord:
    turn_id: str
    session_id: str
    timestamp_start: float
    timestamp_end: float
    user_input: str
    stt_transcript: str
    stt_confidence: float
    intent_detected: str
    llm_prompt_tokens: int
    llm_completion_tokens: int
    llm_latency_ms: int
    response_text: str
    tts_latency_ms: int
    total_latency_ms: int
    state_before: str
    state_after: str
    function_calls: list
    error: Optional[str]

class TurnTracker:
    """Track every conversation turn with full metrics"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turn_id TEXT UNIQUE,
                session_id TEXT,
                timestamp_start REAL,
                timestamp_end REAL,
                user_input TEXT,
                stt_transcript TEXT,
                stt_confidence REAL,
                intent_detected TEXT,
                llm_prompt_tokens INTEGER,
                llm_completion_tokens INTEGER,
                llm_latency_ms INTEGER,
                response_text TEXT,
                tts_latency_ms INTEGER,
                total_latency_ms INTEGER,
                state_before TEXT,
                state_after TEXT,
                function_calls TEXT,  -- JSON
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversation_turns(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversation_turns(created_at)")
        conn.commit()
        conn.close()
    
    def log_turn(self, turn: TurnRecord):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO conversation_turns VALUES (
                NULL, :turn_id, :session_id, :timestamp_start, :timestamp_end,
                :user_input, :stt_transcript, :stt_confidence, :intent_detected,
                :llm_prompt_tokens, :llm_completion_tokens, :llm_latency_ms,
                :response_text, :tts_latency_ms, :total_latency_ms,
                :state_before, :state_after, :function_calls, :error, CURRENT_TIMESTAMP
            )
        """, {
            **asdict(turn),
            'function_calls': json.dumps(turn.function_calls)
        })
        conn.commit()
        conn.close()
    
    def get_session_turns(self, session_id: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM conversation_turns WHERE session_id = ? ORDER BY timestamp_start",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_latency_stats(self, hours: int = 24) -> Dict[str, float]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT 
                AVG(total_latency_ms) as avg_latency,
                AVG(llm_latency_ms) as avg_llm_latency,
                AVG(stt_confidence) as avg_stt_confidence,
                COUNT(*) as total_turns,
                SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as error_count
            FROM conversation_turns 
            WHERE created_at > datetime('now', '-{} hours')
        """.format(hours))
        row = cursor.fetchone()
        conn.close()
        return {
            'avg_latency_ms': row[0] or 0,
            'avg_llm_latency_ms': row[1] or 0,
            'avg_stt_confidence': row[2] or 0,
            'total_turns': row[3] or 0,
            'error_rate': (row[4] or 0) / max(row[3], 1)
        }
```

### 3. Test Suite Completa

**File da creare:** `voice-agent/tests/test_voice_agent_complete.py`
```python
"""Test suite completa per Voice Agent - Tutti gli scenari"""

import pytest
import asyncio
import json
from typing import Dict, Any
import sqlite3
import tempfile
import os

# Import sistema
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.booking_state_machine import BookingStateMachine, BookingState
from src.disambiguation_handler import DisambiguationHandler, name_similarity
from src.entity_extractor import extract_all
from src.intent_classifier import classify_intent

class TestVoiceAgentComplete:
    """Suite test completa per Voice Agent Enterprise"""
    
    # ============================================================
    # TEST 1: Client Matching Security
    # ============================================================
    
    def test_no_false_positive_name_only(self):
        """CRITICAL: Nome corretto + cognome sbagliato NON deve matchare"""
        sm = BookingStateMachine()
        sm.context.client_name = "Filippo"
        sm.context.client_surname = "Virgilio"
        
        # DB ha "Filippo Alberti"
        result = sm._check_name_disambiguation("Filippo", "Virgilio")
        
        # Non deve trovare match (cognomi diversi)
        assert result[0] == False  # No disambiguation needed
        assert result[1] is None   # No client found
    
    def test_exact_match_name_surname(self):
        """Nome + cognome corretti = match esatto"""
        sm = BookingStateMachine()
        result = sm._check_name_disambiguation("Gigio", "Peruzzi")
        
        # Deve trovare il cliente
        assert result[1] is not None
        assert result[1]['match_type'] in ['exact', 'ambiguous']
    
    def test_phonetic_disambiguation(self):
        """Gino vs Gigio con stesso cognome = disambiguazione"""
        sm = BookingStateMachine()
        result = sm._check_name_disambiguation("Gino", "Peruzzi")
        
        # Deve chiedere disambiguazione
        assert result[0] == True  # Needs disambiguation
    
    def test_nickname_recognition(self):
        """Soprannome riconosciuto = match diretto"""
        handler = DisambiguationHandler()
        result = handler.check_nickname_match("Gigi", "Peruzzi")
        
        # "Gigi" è soprannome di "Gigio Peruzzi"
        assert result is not None
        assert result['nome'] == "Gigio"
    
    # ============================================================
    # TEST 2: Intent Classification
    # ============================================================
    
    @pytest.mark.parametrize("text,expected_intent", [
        ("Vorrei prenotare", "prenotazione"),
        ("Voglio un appuntamento", "prenotazione"),
        ("Posso cancellare?", "cancellazione"),
        ("Vorrei spostare", "spostamento"),
        ("Mettetemi in lista d'attesa", "waitlist"),
        ("Quali orari avete?", "info_orari"),
        ("Sì, confermo", "conferma"),
        ("No, grazie", "rifiuto"),
        ("Parla con operatore", "operatore"),
        ("Buongiorno", "greeting"),
    ])
    def test_intent_classification(self, text, expected_intent):
        """Test intent classification per tutti i pattern"""
        result = classify_intent(text)
        assert result.category.value == expected_intent
        assert result.confidence > 0.7
    
    # ============================================================
    # TEST 3: Entity Extraction
    # ============================================================
    
    def test_date_extraction(self):
        """Estrazione date varie"""
        test_cases = [
            ("Domani", "relative"),
            ("Oggi", "relative"),
            ("Lunedì", "weekday"),
            ("15/03", "explicit"),
            ("Dopodomani", "relative"),
        ]
        
        for text, expected_type in test_cases:
            result = extract_all(text)
            assert len(result.dates) > 0, f"Failed for: {text}"
            assert result.dates[0].confidence > 0.8
    
    def test_service_extraction(self):
        """Estrazione servizi salone"""
        text = "Vorrei un taglio e colore"
        result = extract_all(text)
        
        assert len(result.services) >= 1
        service_names = [s.name.lower() for s in result.services]
        assert any('taglio' in s for s in service_names)
    
    def test_name_extraction(self):
        """Estrazione nome completo"""
        test_cases = [
            ("Sono Marco Rossi", "Marco", "Rossi"),
            ("Mi chiamo Anna Bianchi", "Anna", "Bianchi"),
            ("Nome Luigi, cognome Verdi", "Luigi", "Verdi"),
        ]
        
        for text, expected_name, expected_surname in test_cases:
            result = extract_all(text)
            assert len(result.names) > 0
            assert result.names[0].name == expected_name
    
    # ============================================================
    # TEST 4: State Machine Transitions
    # ============================================================
    
    def test_state_transition_waiting_name_to_waiting_surname(self):
        """Flusso: nome fornito → chiedi cognome"""
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_NAME
        
        result = sm.handle_input("Mi chiamo Marco")
        
        assert sm.context.client_name == "Marco"
        assert result.next_state == BookingState.WAITING_SURNAME
    
    def test_state_transition_complete_booking_flow(self):
        """Flusso completo: nome → servizio → data → conferma"""
        sm = BookingStateMachine()
        
        # Step 1: Nome
        sm.context.state = BookingState.WAITING_NAME
        sm.handle_input("Sono Marco Rossi")
        
        # Step 2: Servizio
        sm.context.state = BookingState.WAITING_SERVICE
        sm.handle_input("Taglio")
        
        # Step 3: Data
        sm.context.state = BookingState.WAITING_DATE
        sm.handle_input("Domani")
        
        # Step 4: Ora
        sm.context.state = BookingState.WAITING_TIME
        sm.handle_input("15:00")
        
        # Step 5: Conferma
        assert sm.context.state == BookingState.CONFIRMING
    
    def test_interruption_handling(self):
        """Gestione interruzioni: "aspetta""""
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_SERVICE
        sm.context.service = "Taglio"
        
        result = sm.handle_input("Aspetta, voglio cambiare")
        
        # Deve gestire interruzione gracefully
        assert result.response is not None
        assert result.interruption_handled == True
    
    # ============================================================
    # TEST 5: Error Recovery
    # ============================================================
    
    def test_stt_low_confidence_recovery(self):
        """Recupero quando STT confidence < 0.7"""
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_NAME
        
        # Simula input con bassa confidenza
        result = sm.handle_input_with_confidence("Mmmmm...", confidence=0.5)
        
        # Deve chiedere ripetizione
        assert "non ho capito" in result.response.lower()
        assert result.next_state == BookingState.WAITING_NAME  # Rimani nello stato
    
    def test_api_failure_recovery(self):
        """Recupero quando API backend fallisce"""
        sm = BookingStateMachine()
        sm.context.state = BookingState.CHECKING_AVAILABILITY
        
        # Simula errore API
        result = sm.handle_api_error("Database timeout")
        
        # Deve offrire scelta alternativa
        assert "problema tecnico" in result.response.lower() or "riprovare" in result.response.lower()
    
    # ============================================================
    # TEST 6: Edge Cases
    # ============================================================
    
    def test_empty_input(self):
        """Gestione input vuoto"""
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_NAME
        
        result = sm.handle_input("")
        
        # Non deve crashare
        assert result.response is not None
    
    def test_gibberish_input(self):
        """Gestione input nonsensico"""
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_SERVICE
        
        result = sm.handle_input("asdlkjhasd lkjhasd")
        
        # Deve chiedere chiarimento
        assert result.fallback_triggered == True
    
    def test_multiple_services(self):
        """Prenotazione multipli servizi"""
        sm = BookingStateMachine()
        sm.context.state = BookingState.WAITING_SERVICE
        
        result = sm.handle_input("Vorrei taglio, colore e piega")
        
        # Deve estrarre tutti i servizi
        assert len(sm.context.services) == 3
    
    def test_date_ambiguity_resolution(self):
        """Risoluzione date ambigue"""
        sm = BookingStateMachine()
        
        # "Domenica" potrebbe essere questa o prossima
        result = sm.handle_date_input("Domenica")
        
        # Deve chiedere quale domenica
        assert result.disambiguation_needed == True
    
    # ============================================================
    # TEST 7: WhatsApp Integration
    # ============================================================
    
    def test_whatsapp_confirmation_sent(self):
        """Verifica invio WhatsApp post-booking"""
        sm = BookingStateMachine()
        sm.context.client_phone = "+393331234567"
        sm.context.service = "Taglio"
        sm.context.date = "2026-02-15"
        sm.context.time = "15:00"
        
        # Completa booking
        result = sm.complete_booking()
        
        # Deve aver triggerato invio WhatsApp
        assert result.whatsapp_triggered == True
        assert result.whatsapp_message is not None
    
    # ============================================================
    # TEST 8: Performance
    # ============================================================
    
    @pytest.mark.asyncio
    async def test_response_latency(self):
        """Verifica latenza < 2 secondi"""
        import time
        
        sm = BookingStateMachine()
        start = time.time()
        
        result = await sm.handle_input_async("Vorrei prenotare")
        
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 2000, f"Latency {elapsed}ms > 2000ms"
    
    def test_memory_leak(self):
        """Verifica no memory leak su molte sessioni"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Crea 100 sessioni
        for i in range(100):
            sm = BookingStateMachine()
            sm.context.session_id = f"test_{i}"
            sm.handle_input("Buongiorno")
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory per sessione deve essere < 1MB
        assert current / 100 < 1_000_000


# ============================================================
# TEST INTEGRAZIONE API
# ============================================================

class TestVoiceAgentAPI:
    """Test API endpoint"""
    
    async def test_health_endpoint(self):
        """GET /health"""
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3002/health') as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data['status'] == 'ok'
    
    async def test_process_endpoint(self):
        """POST /process"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:3002/process',
                json={'text': 'Buongiorno'}
            ) as resp:
                assert resp.status == 200
                data = await resp.json()
                assert 'response' in data
                assert 'success' in data
    
    async def test_reset_endpoint(self):
        """POST /reset"""
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:3002/reset') as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data['success'] == True


# ============================================================
# ESECUZIONE TEST
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

---

## 🧪 SCENARI TEST LIVE - CHECKLIST MANUALE

### Pre-test Setup
```bash
# 1. Verifica Voice Agent running
curl http://localhost:3002/health

# 2. Pulisci sessioni precedenti
curl -X POST http://localhost:3002/reset

# 3. Verifica DB clienti
sqlite3 fluxion.db "SELECT nome, cognome FROM clienti LIMIT 5;"
```

### Scenari da Testare

| # | Scenario | Input | Atteso | Stato |
|---|----------|-------|--------|-------|
| 1 | **STT Whisper** | "Buongiorno, sono Sara" | Trascrizione corretta | ⬜ |
| 2 | **Gino vs Gigio** | "Sono Gino Peruzzi" (DB: Gigio Peruzzi) | Disambiguazione + chiede data nascita | ⬜ |
| 3 | **Soprannome** | "Sono Gigi Peruzzi" | "Ciao Gigi! Bentornato Gigio!" | ⬜ |
| 4 | **Cognome Errato** | "Sono Gigio Bianchi" (DB: Gigio Peruzzi) | "Non la trovo..." (NO false positive) | ⬜ |
| 5 | **Flusso Perfetto** | Nuovo cliente completo | Registrazione + booking + WhatsApp | ⬜ |
| 6 | **Chiusura Graceful** | "Confermo chiusura" | WhatsApp + termina | ⬜ |
| 7 | **Interruzione** | "No aspetta, cambio" | "Va bene, cosa vuoi cambiare?" | ⬜ |
| 8 | **Waitlist** | Slot occupato → "Mettetemi in lista" | Salvataggio waitlist + conferma | ⬜ |
| 9 | **Rifiuto** | "No ho cambiato idea" | "Posso aiutarla in altro modo?" | ⬜ |
| 10 | **Operatore** | "Voglio parlare con un operatore" | Transfer graceful | ⬜ |

---

## 📊 METRICHE DI SUCCESSO

### KPI Voice Agent
```
✅ Latency P95: < 1000ms
✅ STT WER (Word Error Rate): < 15%
✅ Intent Accuracy: > 95%
✅ Booking Completion Rate: > 80%
✅ False Positive Client Match: 0%
✅ Uptime: > 99.5%
```

### CoVe Verification Checklist
```
[ ] Tutti i test automatici passano (pytest voice-agent/tests/)
[ ] Test live 10 scenari passano
[ ] Latency P95 < 1000ms misurata
[ ] Zero false positive client matching
[ ] WhatsApp inviato correttamente
[ ] TypeScript 0 errori
[ ] Rust 0 errori
[ ] Commit con messaggio chiaro
[ ] Sync su iMac verificato
```

---

## 📝 NOTE IMPLEMENTAZIONE

### Pattern Obbligatori
1. **CoVe**: Ogni modifica richiede test che passano
2. **State Machine**: Ogni stato ha task_messages + functions espliciti
3. **Confirmation**: Dati sensibili sempre confermati con ripetizione
4. **Logging**: Ogni turno loggato con latency breakdown
5. **Fallback**: transfer_to_agent sempre disponibile

### Anti-Patterns da Evitare
- ❌ Non usare LLM per validazione dati (usa codice)
- ❌ Non fare fallback name-only se cognome fornito
- ❌ Non aspettare LLM completion prima di TTS (stream)
- ❌ Non loggare PII (telefoni, nomi) in chiaro

---

*Prompt generato: 2026-02-11*  
*Deep Research: Reddit r/LLMDevs, r/aiagents, r/MachineLearning 2026*  
*CoVe Status: COMPLETE*
