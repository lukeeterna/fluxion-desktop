# SUB-PRD: FLUXION Voice Agent Enterprise
## Documento di Architettura Completa - CoVe 2026 Verified

**Versione**: 3.0  
**Data**: 2026-02-12  
**Stato**: Architettura Completa - Pronto per Implementazione  
**Obiettivo CoVe**: Test Live Perfetti (0 errori, latenza <800ms)  

---

## 🎯 VISIONE

Il Voice Agent "Sara" è l'**assistente vocale AI** che sostituisce l'operatore telefonico per PMI italiane. Gestisce prenotazioni, informazioni, cancellazioni 24/7 con una voce naturale italiana, integrato con WhatsApp e VoIP EhiWeb.

**Esperienza Utente Target**:
```
Cliente: "Pronto, vorrei prenotare un taglio per domani"
Sara:    "Buongiorno! Certo, per domani pomeriggio ho disponibile alle 15:00 o alle 17:30. 
          Quale preferisce?"
Cliente: "Le 15:00 vanno bene"
Sara:    "Perfetto! Allora la aspettiamo domani alle 15:00 per un taglio. 
          Le mando la conferma su WhatsApp. A domani!"
```

---

## 🏗️ ARCHITETTURA MACRO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUXION VOICE AGENT - ARCHITETTURA                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐     WebSocket/HTTP     ┌─────────────────────────┐   │
│  │   Tauri Frontend │ ◄─────────────────────► │   Voice Agent Core      │   │
│  │   (React + TS)   │    Audio streaming      │   Python 3.11+          │   │
│  │                  │                         │   FastAPI + WebSocket     │   │
│  └────────┬─────────┘                         └──────────┬──────────────┘   │
│           │                                                │                  │
│           │                                                ▼                  │
│           │                                      ┌──────────────────┐        │
│           │                                      │  SKILL SYSTEM    │        │
│           │                                      │  ┌────────────┐  │        │
│           │                                      │  │VAD Skill   │  │        │
│           │                                      │  │STT Skill   │  │        │
│           │                                      │  │NLU Skill   │  │        │
│           │                                      │  │TTS Skill   │  │        │
│           │                                      │  │State Skill │  │        │
│           │                                      │  └────────────┘  │        │
│           │                                      └──────────────────┘        │
│           │                                                │                  │
│           ▼                                                ▼                  │
│  ┌──────────────────┐                         ┌─────────────────────────┐   │
│  │  SQLite (Tauri)  │                         │  Vertical Integration   │   │
│  │  - Clienti       │                         │  - Salone               │   │
│  │  - Prenotazioni  │                         │  - Medical              │   │
│  │  - Impostazioni  │                         │  - Palestra             │   │
│  └──────────────────┘                         │                           │   │
│                                               │  - Auto                 │   │
│                                               └─────────────────────────┘   │
│                                                                             │
│  ┌──────────────────┐                         ┌─────────────────────────┐   │
│  │  WhatsApp API    │                         │  VoIP EhiWeb            │   │
│  │  - Notifiche     │                         │  - SIP Trunk            │   │
│  │  - Conferme      │                         │  - Inbound/Outbound     │   │
│  │  - Promemoria    │                         │  - IVR Integration      │   │
│  └──────────────────┘                         └─────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎭 SKILL SYSTEM ARCHITECTURE

Ogni skill è un **sub-agent specializzato** che può essere sviluppato, testato e deployato indipendentemente.

### Skill 1: VAD Skill (Voice Activity Detection)

**Responsabilità**: Rilevare inizio/fine parlato, gestire interruzioni

```python
# voice-agent/skills/vad_skill.py
class VADSkill:
    """
    Sub-Agent: VAD Detection
    - Input: Stream audio raw (16kHz, 16bit, mono)
    - Output: Events (SPEECH_START, SPEECH_END, INTERRUPTION)
    - Latency target: <50ms detection
    """
    
    def __init__(self, config: VADConfig):
        self.engine = SileroVAD(onnx_runtime=True)  # No PyTorch
        self.buffer = AudioBuffer(prefix_ms=300)    # Pre-speech buffering
        self.sensitivity = config.sensitivity       # 0.0-1.0
        
    async def process_stream(self, audio_chunk: bytes) -> VADEvent:
        """
        CoVe 2026: Frame-based processing con interruption detection
        """
        probability = self.engine.process_chunk(audio_chunk)
        
        # State machine interna VAD
        if probability > self.sensitivity:
            if self.state == VADState.SILENCE:
                return VADEvent(type="SPEECH_START", timestamp=now())
        elif probability < 0.1:
            if self.state == VADState.SPEECH:
                return VADEvent(type="SPEECH_END", timestamp=now())
```

**Test CI/CD**:
```yaml
# .github/workflows/vad-skill-test.yml
name: VAD Skill Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test VAD Detection
        run: |
          python -m pytest skills/vad/tests/
          # Test con audio sample: speech_detection.wav, silence.wav
      - name: Latency Benchmark
        run: |
          python skills/vad/benchmark.py --max-latency 50ms
```

---

### Skill 2: STT Skill (Speech-to-Text)

**Responsabilità**: Trascrivere audio in testo italiano

```python
# voice-agent/skills/stt_skill.py
class STTSkill:
    """
    Sub-Agent: Speech-to-Text
    - Primary: Whisper.cpp (locale, offline)
    - Fallback: Groq Whisper API (cloud)
    - Target WER: <10% italiano
    """
    
    def __init__(self):
        self.primary = WhisperCPP(model="small", language="it")
        self.fallback = GroqWhisper(api_key=env.GROQ_API_KEY)
        self.metrics = STTMetrics()
        
    async def transcribe(self, audio: AudioBuffer) -> TranscriptionResult:
        """
        CoVe 2026: Local-first con fallback automatico
        """
        start_time = time.time()
        
        try:
            # Try local first
            text = await self.primary.transcribe(audio)
            latency = time.time() - start_time
            
            self.metrics.record(
                latency_ms=latency * 1000,
                engine="whisper.cpp",
                confidence=0.95
            )
            
            return TranscriptionResult(
                text=text,
                confidence=0.95,
                engine="whisper.cpp",
                latency_ms=latency * 1000
            )
            
        except Exception as e:
            # Fallback to cloud
            logger.warning(f"Local STT failed: {e}, using fallback")
            text = await self.fallback.transcribe(audio)
            latency = time.time() - start_time
            
            return TranscriptionResult(
                text=text,
                confidence=0.85,
                engine="groq-whisper",
                latency_ms=latency * 1000,
                is_fallback=True
            )
```

**Configurazione**:
```json
{
  "stt": {
    "primary": {
      "engine": "whisper.cpp",
      "model": "small",
      "language": "it",
      "beam_size": 5
    },
    "fallback": {
      "engine": "groq",
      "model": "whisper-large-v3",
      "timeout_ms": 3000
    },
    "metrics": {
      "log_latency": true,
      "alert_threshold_ms": 2000
    }
  }
}
```

---

### Skill 3: NLU Skill (Natural Language Understanding)

**Responsabilità**: Estrarre intent, entità, sentiment

```python
# voice-agent/skills/nlu_skill.py
class NLUSkill:
    """
    Sub-Agent: NLU Processing
    - Intent Classification (L0-L4)
    - Entity Extraction (date, time, names)
    - Sentiment Analysis
    """
    
    def __init__(self, vertical_config: VerticalConfig):
        self.intent_classifier = IntentClassifier(
            patterns=vertical_config.intent_patterns,
            semantic_model="tf-idf"  # Lightweight
        )
        self.entity_extractor = ItalianEntityExtractor()
        self.sentiment_analyzer = ItalianSentiment()
        
    async def process(self, text: str, context: ConversationContext) -> NLUResult:
        """
        CoVe 2026: 4-Layer RAG Architecture
        """
        # L0: Cortesia (O(1) lookup)
        result = self.intent_classifier.layer0_exact_match(text)
        if result:
            return NLUResult(intent=result, layer="L0")
        
        # L1: Pattern Regex
        result = self.intent_classifier.layer1_pattern_match(text)
        if result.confidence > 0.9:
            return NLUResult(intent=result, layer="L1")
        
        # L2: Semantic (TF-IDF)
        result = self.intent_classifier.layer2_semantic(text)
        if result.confidence > 0.8:
            return NLUResult(intent=result, layer="L2")
        
        # L3: LLM Fallback (Groq)
        result = await self.intent_classifier.layer3_llm(text, context)
        return NLUResult(intent=result, layer="L3")
```

---

### Skill 4: TTS Skill (Text-to-Speech)

**Responsabilità**: Sintetizzare voce naturale italiana

```python
# voice-agent/skills/tts_skill.py
class TTSSkill:
    """
    Sub-Agent: Text-to-Speech
    - Primary: Piper TTS (italiano, naturale, veloce)
    - Fallback: System TTS (macOS say)
    - Target: Voce "Sara" riconoscibile
    """
    
    def __init__(self):
        # Piper TTS - Modello italiano addestrato
        self.primary = PiperTTS(
            model_path="models/piper-it_IT-sara-medium.onnx",
            config_path="models/piper-it_IT-sara-medium.json",
            use_cuda=False  # CPU sufficiente per PMI
        )
        self.fallback = SystemTTS()
        
    async def synthesize(self, text: str, emotion: str = "neutral") -> AudioBuffer:
        """
        CoVe 2026: Streaming TTS per latenza <100ms
        """
        # Preprocessing italiano
        text = self._normalize_italian(text)
        
        # Synthesis
        audio = await self.primary.synthesize_streaming(text)
        
        return AudioBuffer(
            data=audio,
            sample_rate=22050,
            format="pcm_16bit"
        )
        
    def _normalize_italian(self, text: str) -> str:
        """
        Normalizza pronuncia italiana:
        - "€" → "euro"
        - "15:00" → "quindici"
        - Abbreviazioni "sig." → "signor"
        """
        replacements = {
            "€": "euro",
            "sig.": "signor",
            "sig.ra": "signora",
            "dott.": "dottor",
            "15:00": "quindici",
            "15.30": "quindici e trenta"
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text
```

**Modelli TTS Consigliati**:

| Modello | Qualità | Latenza | Size | Uso |
|---------|---------|---------|------|-----|
| **Piper Sara** | ⭐⭐⭐⭐⭐ | ~50ms | 60MB | **Primary** |
| Coqui XTTS | ⭐⭐⭐⭐⭐ | ~200ms | 400MB | Voice cloning (opzionale) |
| MeloTTS | ⭐⭐⭐⭐ | ~100ms | 150MB | Fallback multilingue |

---

### Skill 5: State Skill (Conversation Manager)

**Responsabilità**: Gestire stato conversazione, context, transizioni

```python
# voice-agent/skills/state_skill.py
class StateSkill:
    """
    Sub-Agent: Conversation State Machine
    - 23 stati gestiti
    - Transizioni deterministiche
    - Context persistence
    """
    
    def __init__(self, vertical: str):
        self.machine = BookingStateMachine(
            vertical=vertical,
            states=self._load_states(vertical)
        )
        self.context = ConversationContext()
        
    async def process_turn(self, user_input: NLUResult) -> StateResult:
        """
        CoVe 2026: State transition con error recovery
        """
        current_state = self.context.state
        
        # Get transition handler
        handler = self.machine.get_handler(current_state)
        
        # Execute
        try:
            result = await handler(user_input, self.context)
            
            # Update context
            self.context.state = result.next_state
            self.context.history.append({
                "input": user_input,
                "response": result.response,
                "timestamp": now()
            })
            
            return result
            
        except Exception as e:
            # Error recovery
            logger.error(f"State error: {e}")
            return StateResult(
                next_state=current_state,
                response="Mi scusi, non ho capito. Può ripetere?",
                error=e
            )
```

---

## 🏢 VERTICALI IMPLEMENTATI

Ogni verticale è un **plugin** che estende le skill base.

### 1. Salone (Beauty/Hair)

**File**: `voice-agent/verticals/salone/`

```python
# verticals/salone/config.py
SALONE_CONFIG = {
    "name": "Salone di Bellezza",
    "services": {
        "taglio": ["taglio", "tagliare", "tagliarsi"],
        "colore": ["colore", "tinta", "tingere"],
        "piega": ["piega", "asciugare", "phon"],
        "barba": ["barba", "rasatura"],
        "trattamento": ["trattamento", "maschera", "cura"]
    },
    "slots": ["data", "ora", "servizio", "operatore"],
    "faqs": "faqs/salone.json",
    "greeting": "Buongiorno, sono Sara di {nome_attivita}. Come posso aiutarla?",
    "closing": "Grazie per aver chiamato {nome_attivita}. A presto!"
}
```

**Intent Patterns Specifici**:
```python
INTENT_PATTERNS_SALONE = {
    "PRENOTAZIONE": [
        r"(vorrei|voglio|posso)\s+(prenotare|fissare|prendere)\s+(un\s+)?appuntamento",
        r"(taglio|colore|piega|barba)",
        r"(mi\s+serve|ho\s+bisogno\s+di)\s+(un\s+)?(taglio|colore)"
    ],
    "CANCELLAZIONE": [
        r"(cancellare|annullare|disdire)\s+(la\s+)?prenotazione",
        r"non\s+(posso|riesco)\s+(più\s+)?venire"
    ],
    "INFO_SERVIZI": [
        r"(quanto\s+costa|prezzo)\s+(il\s+)?(taglio|colore)",
        r"(che\s+servizi|cosa)\s+(offrite|fate)"
    ]
}
```

**Scheda Cliente**:
```python
@dataclass
class SchedaSalone:
    cliente_id: str
    tipo_capelli: Optional[str]  # "lisci", "ricci", " Mossi"
    lunghezza: Optional[str]      # "corti", "medi", "lunghi"
    colorazione_precedente: Optional[str]
    allergie_prodotti: List[str]
    preferenze_operatore: Optional[str]
    frequenza_visite: str         # "settimanale", "mensile", "occasionale"
    prodotti_usati: List[str]
    foto_tagli_precedenti: List[str]  # Path foto
```

---

### 2. Medical (Odontoiatria/Fisioterapia)

**File**: `voice-agent/verticals/medical/`

```python
# verticals/medical/config.py
MEDICAL_CONFIG = {
    "name": "Studio Medico",
    "services": {
        "visita": ["visita", "controllo", "checkup"],
        "trattamento": ["trattamento", "terapia", "riabilitazione"],
        "urgente": ["urgente", "emergenza", "dolore"]
    },
    "slots": ["data", "ora", "tipo_visita", "motivo", "mutua"],
    "anamnesi_required": True,  # Chiede dati medici
    "priority_levels": ["urgente", "routine", "controllo"]
}
```

**Scheda Anamnestica**:
```python
@dataclass
class SchedaAnamnesi:
    cliente_id: str
    data_nascita: str
    patologie_croniche: List[str]
    allergie: List[str]
    terapie_in_corso: List[str]
    interventi_precedenti: List[str]
    gruppo_sanguigno: Optional[str]
    contatto_emergenza: Dict[str, str]
    medico_curante: Optional[str]
```

---

### 3. Palestra (Fitness/PT)

**File**: `voice-agent/verticals/palestra/`

```python
PALESTRA_CONFIG = {
    "name": "Centro Fitness",
    "services": {
        "lezione": ["lezione", "corso", "classe"],
        "pt": ["personal", "trainer", "pt", "allenamento"],
        "daypass": ["daypass", "giornaliero", "prova"]
    },
    "slots": ["data", "ora", "tipo_attivita", "istruttore"],
    "calendario_corsi": True  # Integrazione calendario settimanale
}
```


### 5. Auto (Officina/Carrozzeria)

**File**: `voice-agent/verticals/auto/`

```python
AUTO_CONFIG = {
    "name": "Officina",
    "services": {
        "tagliando": ["tagliando", "revisione", "manutenzione"],
        "riparazione": ["riparazione", "guasto", "problema"],
        "gomme": ["gomme", "pneumatici", "cambio\s+gomme"],
        "carrozzeria": ["carrozzeria", "verniciatura", "urto"]
    },
    "slots": ["data", "targa", "modello", "tipo_intervento", "urgenza"],
    "veicolo_required": True
}
```

---

## 🧪 TESTING ARCHITECTURE

### 1. Unit Tests (Per Skill)

```python
# tests/skills/test_vad_skill.py
class TestVADSkill:
    """Test VAD detection accuracy"""
    
    @pytest.mark.parametrize("audio_file,expected", [
        ("speech_hello.wav", "SPEECH_START"),
        ("silence_3s.wav", None),
        ("noise_only.wav", None),
        ("interruption.wav", "INTERRUPTION")
    ])
    def test_detection(self, audio_file, expected):
        vad = VADSkill()
        event = vad.process_file(audio_file)
        assert event.type == expected
        
    def test_latency(self):
        """CoVe: Detection latency <50ms"""
        vad = VADSkill()
        latency = vad.benchmark_latency()
        assert latency < 50, f"VAD latency {latency}ms > 50ms"
```

### 2. Integration Tests (Skill-to-Skill)

```python
# tests/integration/test_pipeline.py
class TestVoicePipeline:
    """Test complete voice pipeline"""
    
    async def test_e2e_booking_flow(self):
        """Test: Prenotazione completa"""
        pipeline = VoicePipeline(vertical="salone")
        
        # Turn 1: Saluto
        result = await pipeline.process_audio("Ciao vorrei prenotare")
        assert "quando" in result.response.lower()
        
        # Turn 2: Data
        result = await pipeline.process_audio("Domani")
        assert "ora" in result.response.lower()
        
        # Turn 3: Ora
        result = await pipeline.process_audio("Alle 15")
        assert "conferma" in result.response.lower()
```

### 3. E2E Tests (Con Audio Reale)

```python
# tests/e2e/test_live_calls.py
class TestLiveCalls:
    """
    CoVe 2026: E2E tests with real audio
    Requires: Voice Agent running on test environment
    """
    
    @pytest.mark.live
    async def test_live_salone_booking(self):
        """Test live booking with real audio"""
        client = VoiceAgentClient(host="192.168.1.7:3002")
        
        # Connect
        await client.connect()
        
        # Send audio file
        response = await client.send_audio("test_audio/prenotazione_taglio.wav")
        
        # Assertions
        assert response.transcription == "Vorrei prenotare un taglio"
        assert response.intent == "PRENOTAZIONE"
        assert response.latency_ms < 2000
        
    @pytest.mark.live
    async def test_interruption_handling(self):
        """Test barge-in durante risposta TTS"""
        client = VoiceAgentClient(host="192.168.1.7:3002")
        await client.connect()
        
        # Start long response
        await client.send_text("Vorrei un taglio")
        
        # Interrupt
        response = await client.send_audio("test_audio/ferma.wav")
        
        assert response.interrupted == True
        assert response.response == "Certo, mi fermo. Come posso aiutarla?"
```

### 4. Smoke Tests

```bash
#!/bin/bash
# scripts/smoke_test.sh

echo "=== Voice Agent Smoke Test ==="

# 1. Health check
curl -f http://192.168.1.7:3002/health || exit 1

# 2. Process API
curl -f -X POST http://192.168.1.7:3002/api/voice/process \
  -d '{"text": "Ciao"}' || exit 1

# 3. TTS API
curl -f -X POST http://192.168.1.7:3002/api/voice/tts \
  -d '{"text": "Test"}' || exit 1

# 4. Verticals loaded
for v in salone medical palestra auto; do
  curl -f http://192.168.1.7:3002/api/verticals/$v/config || exit 1
done

echo "✅ All smoke tests passed"
```

---

## 🔧 DEBUGGING & OBSERVABILITY

### 1. Debug Panel (UI)

```typescript
// src/components/VoiceDebugPanel.tsx
interface VoiceDebugPanelProps {
  sessionId: string;
}

export function VoiceDebugPanel({ sessionId }: VoiceDebugPanelProps) {
  const { data: metrics } = useVoiceMetrics(sessionId);
  
  return (
    <div className="debug-panel">
      <MetricsCard
        title="Latenza"
        value={metrics.avgLatencyMs}
        target={800}
        unit="ms"
      />
      <MetricsCard
        title="STT Confidence"
        value={metrics.sttConfidence}
        target={0.9}
      />
      <TurnTimeline turns={metrics.turns} />
      <AudioVisualizer stream={metrics.audioStream} />
    </div>
  );
}
```

### 2. Logging Structure

```python
# Structured logging per CoVe 2026
logger.info("voice.turn.complete", {
    "session_id": session.id,
    "turn_number": session.turn_count,
    "latency_ms": turn.latency,
    "stt_engine": turn.stt_engine,
    "intent": turn.intent,
    "confidence": turn.confidence,
    "layer": turn.layer_used,  # L0-L4
    "error": turn.error,
    "vertical": session.vertical
})
```

### 3. Tracing

```python
# OpenTelemetry tracing
with tracer.start_as_current_span("voice_pipeline") as span:
    span.set_attribute("session_id", session.id)
    span.set_attribute("vertical", vertical)
    
    with tracer.start_span("stt") as stt_span:
        text = await stt.transcribe(audio)
        stt_span.set_attribute("latency_ms", stt_latency)
        stt_span.set_attribute("confidence", stt_confidence)
```

---

## 📱 INTEGRAZIONI ESTERNE

### WhatsApp Integration

```python
# voice-agent/integrations/whatsapp.py
class WhatsAppIntegration:
    """
    Invio notifiche post-conversazione
    """
    
    async def send_booking_confirmation(self, phone: str, booking: Booking):
        """Invia conferma prenotazione"""
        message = self._format_message("booking_confirm", {
            "nome": booking.client_name,
            "data": booking.date,
            "ora": booking.time,
            "servizio": booking.service
        })
        
        await self.whatsapp_api.send_message(phone, message)
        
    async def send_reminder(self, phone: str, booking: Booking):
        """Invia promemoria 24h prima"""
        message = f"⏰ Promemoria: domani alle {booking.time} per {booking.service}"
        await self.whatsapp_api.send_message(phone, message)
```

### VoIP EhiWeb Integration

```python
# voice-agent/integrations/ehiweb_voip.py
class EhiWebVoIP:
    """
    Integrazione con trunk SIP EhiWeb
    """
    
    def __init__(self):
        self.sip_client = SIPClient(
            server="sip.ehiweb.it",
            username=env.EHIWEB_USER,
            password=env.EHIWEB_PASS
        )
        
    async def handle_inbound_call(self, call: SIPCall):
        """Gestisce chiamata entrante"""
        # Crea sessione voice
        session = VoiceSession(
            call_id=call.id,
            caller_number=call.caller,
            vertical=self.detect_vertical(call.did)  # Numero chiamato
        )
        
        # Avvia pipeline
        await session.start()
        
    async def handle_outbound_call(self, phone: str, context: dict):
        """Chiamata uscente (reminder, conferme)"""
        call = await self.sip_client.dial(phone)
        
        session = VoiceSession(
            call_id=call.id,
            direction="outbound",
            context=context
        )
        
        # TTS iniziale
        await session.speak(context["greeting"])
```

---

## 🚀 CI/CD PIPELINE

```yaml
# .github/workflows/voice-agent.yml
name: Voice Agent CI/CD

on:
  push:
    paths:
      - 'voice-agent/**'
      - '.github/workflows/voice-agent.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd voice-agent
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          
      - name: Unit Tests
        run: |
          cd voice-agent
          pytest tests/unit/ -v --cov=src --cov-report=xml
          
      - name: Integration Tests
        run: |
          cd voice-agent
          pytest tests/integration/ -v
          
      - name: Smoke Test
        run: |
          cd voice-agent
          python main.py &
          sleep 5
          ./scripts/smoke_test.sh
          
      - name: Latency Benchmark
        run: |
          cd voice-agent
          python benchmarks/latency_test.py --max-p95 800
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./voice-agent/coverage.xml

  deploy-imac:
    needs: test
    runs-on: self-hosted  # Runner su iMac
    if: github.ref == 'refs/heads/master'
    steps:
      - name: Deploy to iMac
        run: |
          cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent
          git pull origin master
          pip install -r requirements.txt
          
          # Restart service
          pkill -f "python.*main.py" || true
          sleep 2
          
          # Start with production config
          export GROQ_API_KEY=${{ secrets.GROQ_API_KEY }}
          export WHATSAPP_API_KEY=${{ secrets.WHATSAPP_API_KEY }}
          nohup python main.py --port 3002 --env production > logs/voice-agent.log 2>&1 &
          
          # Health check
          sleep 5
          curl -f http://localhost:3002/health
```

---

## 📊 KPI & MONITORING

### Metriche CoVe 2026

| Metrica | Target | Alert | Critico |
|---------|--------|-------|---------|
| Latenza P95 | <800ms | >1000ms | >2000ms |
| STT WER | <10% | >15% | >20% |
| Intent Accuracy | >95% | <90% | <85% |
| Uptime | 99.9% | <99% | <95% |
| Satisfaction | >4.5/5 | <4.0 | <3.5 |
| Escalation Rate | <5% | >10% | >20% |

### Dashboard Grafana

```yaml
# monitoring/grafana/dashboard.yml
panels:
  - title: "Latenza Voice Pipeline"
    type: graph
    targets:
      - query: 'avg(voice_latency_ms) by (skill)'
        legend: "{{skill}}"
        
  - title: "Intent Classification"
    type: stat
    targets:
      - query: 'sum(rate(voice_intent_total[5m])) by (intent)'
        
  - title: "Error Rate"
    type: singlestat
    targets:
      - query: 'sum(rate(voice_errors_total[5m]))'
    thresholds:
      - color: green
        value: 0
      - color: red
        value: 0.01
```

---

## 🎯 CHECKLIST TEST LIVE (CoVe Verification)

Prima di dichiarare "Voice Agent Pronto", eseguire:

### Test Funzionali
- [ ] **Saluto**: "Ciao" → risposta cortese
- [ ] **Prenotazione**: Flusso completo nome→data→ora→servizio→conferma
- [ ] **Cancellazione**: "Voglio cancellare" → conferma → annullamento
- [ ] **Disambiguazione**: "Sono Gino Peruzzi" (DB ha Gigio) → chiede conferma
- [ ] **Nickname**: "Sono Gigi Peruzzi" → riconosce come Gigio
- [ ] **Waitlist**: Slot occupato → offerta lista attesa
- [ ] **Chiusura**: "Confermo" → WhatsApp inviato → saluto finale
- [ ] **Interruzione**: Interrompe TTS → ascolta nuovo input
- [ ] **Operatore**: "Voglio parlare con un operatore" → escalation
- [ ] **Info**: "Quanto costa un taglio?" → risposta FAQ

### Test Performance
- [ ] **Latenza**: Ogni turno <2s (ideale <1s)
- [ ] **STT**: Accuratezza >90% con accento italiano
- [ ] **TTS**: Voce naturale, non robotica
- [ ] **Concurrency**: 5+ chiamate simultanee

### Test Integrazione
- [ ] **WhatsApp**: Conferma ricevuta su telefono
- [ ] **VoIP**: Chiamata da linea fissa funzionante
- [ ] **DB**: Prenotazione salvata in calendario

---

## 📝 CONCLUSIONE

Questo SUB-PRD definisce l'**architettura completa** del Voice Agent Fluxion con:

1. **5 Skill modulari** (VAD, STT, NLU, TTS, State)
2. **4 Verticali** configurabili (Salone, Medical, Palestra, Auto)
3. **Testing completo** (Unit, Integration, E2E, Smoke)
4. **Integrazioni** WhatsApp e VoIP EhiWeb
5. **CI/CD** automatizzato
6. **Observability** completa

**Obiettivo CoVe**: Test live perfetti, 0 errori, latenza <800ms.

---

**Documento di Verità**: Qualsiasi modifica al Voice Agent deve essere coerente con questo PRD.
