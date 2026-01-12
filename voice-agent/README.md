# FLUXION Voice Agent

Italian voice assistant for automatic bookings in SMB environments.

## Features

- **5-Layer RAG Pipeline** - Fast, accurate responses with intelligent fallback
- **Italian NLU** - Intent classification, entity extraction optimized for Italian
- **Hybrid FAQ Search** - Keyword + semantic retrieval for >80% accuracy
- **Sentiment Analysis** - Frustration detection with escalation triggers
- **Error Recovery** - Circuit breaker, retry logic, graceful fallbacks
- **Analytics** - Conversation logging, metrics, improvement loop

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Pipeline                            │
├─────────────────────────────────────────────────────────────┤
│  L0: Sentiment Analysis        (<5ms)   Frustration check   │
│  L1: Exact Match               (<1ms)   Cortesia, conferma  │
│  L2: Intent Classification     (<20ms)  Pattern matching    │
│  L3: FAQ Retrieval             (<50ms)  Keyword + semantic  │
│  L4: Groq LLM                  (500ms+) Complex fallback    │
└─────────────────────────────────────────────────────────────┘
         │                                      │
         ▼                                      ▼
    ┌─────────┐                          ┌──────────┐
    │ TTS     │                          │ Analytics│
    │ (Piper) │                          │ (SQLite) │
    └─────────┘                          └──────────┘
```

## Quick Start

```bash
# Setup
./setup.sh

# Set API key
export GROQ_API_KEY=your_api_key

# Run tests
python -m pytest tests/ -v

# Start pipeline
python main.py
```

## Usage

```python
from src.pipeline import VoicePipeline

config = {
    "business_name": "Salone Bella Vita",
    "verticale_id": "salone",
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "services": ["Taglio", "Piega", "Colore"]
}

pipeline = VoicePipeline(config)

# Process user input
result = await pipeline.process_text("Vorrei prenotare un taglio per domani")
print(result["response"])  # "Certamente! A che ora preferisce?"
print(result["intent"])    # "prenotazione"
```

## Modules

| Module | Description |
|--------|-------------|
| `intent_classifier` | Pattern-based intent detection |
| `entity_extractor` | Date, time, name, service extraction |
| `faq_manager` | Hybrid keyword + semantic FAQ search |
| `sentiment` | Italian frustration detection |
| `error_recovery` | Circuit breaker, retry, fallbacks |
| `analytics` | Conversation logging and metrics |

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Overall latency | <200ms | Achieved (w/o Groq) |
| Intent accuracy | >90% | Achieved |
| FAQ accuracy | >80% | Achieved |
| Frustration precision | >90% | Achieved |
| Groq fallback rate | <20% | In progress |

## Verticales

Pre-configured for Italian SMB sectors:

- **Salone** - Hair salons
- **Palestra** - Gyms
- **Ristorante** - Restaurants
- **Clinica** - Medical clinics

## Documentation

- [API Reference](docs/API.md) - Complete module documentation
- [Configuration](docs/CONFIGURATION.md) - Setup and configuration guide
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## Development

### Project Structure

```
voice-agent/
├── src/
│   ├── __init__.py          # Module exports
│   ├── pipeline.py          # Main orchestrator
│   ├── intent_classifier.py # Intent detection
│   ├── entity_extractor.py  # Entity extraction
│   ├── faq_manager.py       # FAQ retrieval
│   ├── sentiment.py         # Sentiment analysis
│   ├── error_recovery.py    # Error handling
│   ├── analytics.py         # Conversation logging
│   ├── groq_client.py       # Groq API client
│   └── tts.py               # Text-to-speech
├── tests/
│   ├── test_intent.py
│   ├── test_entity.py
│   ├── test_faq_manager.py
│   ├── test_sentiment.py
│   ├── test_error_recovery.py
│   └── test_analytics.py
├── data/
│   ├── faq_salone.json
│   └── faq_salone.md
├── docs/
│   ├── API.md
│   ├── CONFIGURATION.md
│   └── TROUBLESHOOTING.md
└── README.md
```

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific module
python -m pytest tests/test_sentiment.py -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Results

```
Week 1: 108 tests - Intent, Entity extraction
Week 2: 127 tests - FAQ Manager, E2E, Multi-verticale
Week 3: 163 tests - Sentiment (86), Error Recovery (43), Analytics (34)
─────────────────────────────────────────────────────────────
Total:  318 passed, 39 skipped (async)
```

## Roadmap

- [x] Week 1: Core NLU (Intent, Entity extraction)
- [x] Week 2: FAQ Retrieval (Keyword + Semantic)
- [x] Week 3: Error Handling + Analytics
- [ ] Week 4: VoIP Integration (Ehiweb SIP)
- [ ] Week 5: WhatsApp Integration
- [ ] Week 6: Production Deployment

## License

Proprietary - FLUXION Enterprise

## Credits

- Groq API for LLM inference
- Piper TTS for Italian voice synthesis
- Sentence Transformers for semantic search
