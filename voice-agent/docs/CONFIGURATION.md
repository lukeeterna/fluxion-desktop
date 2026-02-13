# FLUXION Voice Agent - Configuration Guide

## Quick Start

```python
from src.pipeline import VoicePipeline
from pathlib import Path

config = {
    "business_name": "Salone Bella Vita",
    "verticale_id": "salone_001",
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Martedi-Sabato",
    "services": ["Taglio", "Piega", "Colore", "Barba"]
}

pipeline = VoicePipeline(
    business_config=config,
    groq_api_key=os.environ["GROQ_API_KEY"],
    use_piper=True,
    faq_path=Path("data/faq_salone.json")
)
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - TTS
TTS_VOICE_MODEL=it_IT-paola-medium
PIPER_EXECUTABLE=/usr/local/bin/piper

# Optional - HTTP Bridge (Tauri backend)
HTTP_BRIDGE_URL=http://127.0.0.1:3001

# Optional - Analytics
ANALYTICS_DB_PATH=data/analytics.db
ANALYTICS_ANONYMIZE=true
ANALYTICS_RETENTION_DAYS=90

# Optional - Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Business Configuration

### Basic Configuration

```python
config = {
    # Required
    "business_name": "Nome Attività",
    "verticale_id": "unique_identifier",

    # Hours
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Martedi-Sabato",

    # Services (for entity extraction)
    "services": ["Taglio", "Piega", "Colore"]
}
```

### Extended Configuration

```python
config = {
    "business_name": "Salone Bella Vita",
    "verticale_id": "salone_bella_vita",

    # Operating hours
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "lunch_break_start": "13:00",  # Optional
    "lunch_break_end": "14:00",
    "working_days": "Martedi-Sabato",
    "closed_days": ["Lunedi", "Domenica"],

    # Services with duration and price
    "services": ["Taglio", "Piega", "Colore", "Barba", "Trattamento"],
    "service_details": {
        "taglio": {"duration": 30, "price": 18},
        "piega": {"duration": 45, "price": 25},
        "colore": {"duration": 90, "price": 45},
        "barba": {"duration": 15, "price": 10},
        "trattamento": {"duration": 60, "price": 35}
    },

    # Operators
    "operators": [
        {"name": "Marco", "specializations": ["taglio", "barba"]},
        {"name": "Laura", "specializations": ["colore", "trattamento"]}
    ],

    # Contact info
    "phone": "+39 02 1234567",
    "address": "Via Roma 123, Milano",
    "email": "info@salonebellita.it"
}
```

---

## FAQ Configuration

### JSON Format (Recommended)

Create `data/faq_<verticale>.json`:

```json
{
  "verticale": "salone",
  "version": "1.0",
  "last_updated": "2026-01-12",

  "settings": {
    "nome_attivita": "Salone Bella Vita",
    "orario_apertura": "09:00",
    "orario_chiusura": "19:00",
    "giorni_apertura": "dal martedì al sabato",
    "telefono": "02 1234567"
  },

  "faqs": [
    {
      "id": "prezzi_taglio",
      "category": "prezzi",
      "question": "Quanto costa un taglio?",
      "answer": "Il taglio uomo costa 18€, il taglio donna parte da 25€.",
      "keywords": ["prezzo", "costo", "quanto", "taglio", "euro"],
      "priority": 1,
      "variations": [
        "qual è il prezzo del taglio",
        "quanto viene un taglio"
      ]
    },
    {
      "id": "orari_apertura",
      "category": "orari",
      "question": "A che ora aprite?",
      "answer": "Siamo aperti dalle {{orario_apertura}} alle {{orario_chiusura}}, {{giorni_apertura}}.",
      "keywords": ["orario", "orari", "aprite", "aperti", "quando"],
      "priority": 1
    },
    {
      "id": "pagamenti",
      "category": "servizi",
      "question": "Accettate carte di credito?",
      "answer": "Sì, accettiamo carte di credito, bancomat e Satispay.",
      "keywords": ["carta", "pagare", "contanti", "bancomat", "satispay"],
      "priority": 2
    }
  ]
}
```

### Markdown Format (Simple)

Create `data/faq_<verticale>.md`:

```markdown
# FAQ {{nome_attivita}}

## Prezzi
- quanto costa un taglio: Il taglio uomo costa 18€, il taglio donna parte da 25€
- quanto costa il colore: Il colore parte da 35€, dipende dalla lunghezza dei capelli
- quanto costa la barba: La barba costa 10€

## Orari
- a che ora aprite: Siamo aperti dalle {{orario_apertura}} alle {{orario_chiusura}}
- siete aperti di lunedì: No, siamo chiusi il lunedì. Siamo aperti {{giorni_apertura}}
- fate orario continuato: Sì, siamo aperti con orario continuato

## Servizi
- fate anche barba: Sì, facciamo taglio barba e rasatura
- avete prodotti in vendita: Sì, vendiamo prodotti per capelli delle migliori marche
- fate trattamenti: Sì, offriamo trattamenti alla cheratina e maschere rigeneranti

## Prenotazioni
- devo prenotare: Consigliamo di prenotare, ma accettiamo anche clienti senza appuntamento
- come prenoto: Può prenotare chiamando il {{telefono}} o tramite questo assistente vocale
- posso disdire: Sì, può disdire fino a 24 ore prima dell'appuntamento

## Altro
- avete parcheggio: Sì, abbiamo parcheggio gratuito per i clienti
- c'è il wifi: Sì, offriamo WiFi gratuito ai clienti
```

---

## Module Configuration

### FAQ Manager

```python
from src import FAQManager, FAQConfig

config = FAQConfig(
    # Threshold for keyword matching (0.0 - 1.0)
    keyword_threshold=0.3,

    # Threshold for semantic similarity (0.0 - 1.0)
    semantic_threshold=0.65,

    # Weights for hybrid scoring
    keyword_weight=0.4,
    semantic_weight=0.6,

    # Maximum results to return
    max_results=3,

    # Use semantic search (requires sentence-transformers)
    use_semantic=True
)

manager = FAQManager(config=config)
```

### Sentiment Analyzer

```python
from src import SentimentAnalyzer

analyzer = SentimentAnalyzer(
    # Frustration level thresholds
    thresholds={
        "low": 1,
        "medium": 2,
        "high": 5,
        "critical": 8
    },

    # Track frustration across turns
    cumulative_tracking=True,

    # Decay factor for cumulative frustration
    decay_factor=0.8
)
```

### Error Recovery

```python
from src import RecoveryManager, RetryConfig, TimeoutConfig

# Retry configuration
retry_config = RetryConfig(
    max_retries=3,
    base_delay=0.5,        # seconds
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True
)

# Timeout configuration
timeout_config = TimeoutConfig(
    default=5.0,           # seconds
    groq_api=30.0,
    db_query=2.0,
    http_bridge=5.0
)

# Circuit breaker settings
manager = RecoveryManager(
    circuit_failure_threshold=5,
    circuit_recovery_timeout=30.0
)
```

### Analytics Logger

```python
from src import ConversationLogger

logger = ConversationLogger(
    # Database path
    db_path="data/analytics.db",

    # Privacy settings
    anonymize_pii=True,          # Anonymize phone/email in logs
    retention_days=90,           # Auto-cleanup after N days

    # Performance
    batch_writes=False,          # Batch DB writes (faster but less reliable)

    # Metrics
    track_faq_effectiveness=True
)
```

---

## Verticale Configurations

### Salone (Hair Salon)

```python
SALONE_CONFIG = {
    "business_name": "Salone Bella Vita",
    "verticale_id": "salone",
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Martedi-Sabato",
    "services": ["Taglio", "Piega", "Colore", "Barba", "Trattamento"],
    "slot_duration": 30,  # minutes
    "booking_advance_days": 30,
    "cancellation_hours": 24
}
```

### Palestra (Gym)

```python
PALESTRA_CONFIG = {
    "business_name": "FitLife Gym",
    "verticale_id": "palestra",
    "opening_hours": "06:00",
    "closing_hours": "22:00",
    "working_days": "Lunedi-Domenica",
    "services": ["Personal Training", "Corso Fitness", "Spinning", "Yoga"],
    "slot_duration": 60,
    "max_participants": 20,  # per class
    "booking_advance_days": 7
}
```

### Clinica (Medical Clinic)

```python
CLINICA_CONFIG = {
    "business_name": "Studio Medico Rossi",
    "verticale_id": "clinica",
    "opening_hours": "08:00",
    "closing_hours": "18:00",
    "working_days": "Lunedi-Venerdi",
    "services": ["Visita Generale", "Specialistica", "Esami", "Vaccinazione"],
    "slot_duration": 30,
    "booking_advance_days": 60,
    "reminder_hours": 48  # Send reminder 48h before
}
```

---

## Pipeline Callbacks

```python
pipeline = VoicePipeline(config)

# Called when speech is transcribed
def on_transcription(text: str):
    print(f"User said: {text}")

# Called when response is generated
def on_response(text: str):
    print(f"Bot says: {text}")

# Called when intent is detected
def on_intent(intent: str):
    print(f"Intent: {intent}")
    update_ui(intent)

# Called when booking action occurs
def on_booking(action: dict):
    if action["action"] == "booking_created":
        send_confirmation_sms(action["context"])

pipeline.on_transcription = on_transcription
pipeline.on_response = on_response
pipeline.on_intent = on_intent
pipeline.on_booking = on_booking
```

---

## Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_agent.log'),
        logging.StreamHandler()
    ]
)

# Set module-specific levels
logging.getLogger('src.groq_client').setLevel(logging.WARNING)
logging.getLogger('src.analytics').setLevel(logging.DEBUG)
```

---

## Production Checklist

- [ ] Set `GROQ_API_KEY` environment variable
- [ ] Configure FAQ file path
- [ ] Set appropriate timeouts for your network
- [ ] Enable analytics with `anonymize_pii=True`
- [ ] Configure circuit breaker thresholds
- [ ] Set up log rotation
- [ ] Test with realistic load
- [ ] Monitor Groq API usage (fallback rate target: <20%)
- [ ] Review escalation triggers for your use case
