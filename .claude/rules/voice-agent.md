---
paths:
  - "voice-agent/**"
---

# Voice Agent Rules

## Stack
- Python 3.9 (iMac runtime) / 3.13 (MacBook dev)
- No PyTorch (3.13 limitation) - use ONNX Runtime
- SQLite via sqlite3, HTTP via aiohttp
- Pipeline on port 3002, HTTP Bridge on port 3001

## Architecture: 5-Layer RAG
```
L0: Regex (corrections, quick patterns) - <1ms
L1: Intent Classifier (rule-based + TF-IDF) - <5ms
L2: Booking State Machine (slot filling) - <10ms
L3: FAQ Manager (keyword search) - <50ms
L4: Groq LLM (fallback) - <500ms
```

## Key Files
```
voice-agent/
  main.py                    # Entry point, health check
  src/
    orchestrator.py          # 5-layer pipeline coordinator
    booking_state_machine.py # State machine (IDLE->COLLECTING->CONFIRMING->DONE)
    disambiguation_handler.py # Homonymous client resolution
    intent_classifier.py     # L1 intent detection
    entity_extractor.py      # Name, date, time extraction
    nlu/semantic_classifier.py # TF-IDF L2.5 layer
    vad/ten_vad_integration.py # Silero VAD (ONNX)
    guided_dialog.py         # Guided conversation engine
  tests/                     # pytest suite
```

## Rules
- Always restart pipeline on iMac after Python changes:
  `ssh imac "kill $(lsof -ti:3002); cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"`
- Italian NLU: fuzzy match, Levenshtein distance, handle accents
- 4 verticals: salone, palestra, medical, auto
- Field names match Rust: `servizio`, `data`, `ora`, `cliente_id`
- Test: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && pytest tests/ -v"`
