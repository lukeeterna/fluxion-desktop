# Fluxion Voice Agent Skill

## Description
Voice Agent "Sara" - Assistente vocale per prenotazioni PMI italiane.
Architettura: Guided-First + NLU-Validation.

## When to Use
- Quando si lavora su voice-agent/ directory
- Quando si implementa NLU, TTS, STT
- Quando si gestiscono conversazioni guidate
- Quando si aggiungono FAQ o verticali
- Quando si testa il flusso prenotazione

## Architecture

### Paradigma: Guided-First
```
USER INPUT
    ↓
GREETING (propone opzioni)
    ↓
SLOT COLLECTION LOOP
  ├─ Proponi opzioni
  ├─ Valida input (fuzzy match)
  ├─ Se valido → next slot
  └─ Se invalido → fallback++
    ↓
fallback >= 2 → GUIDED MODE (opzioni numerate)
    ↓
fallback >= 3 → ESCALATION (operatore umano)
    ↓
RECAP + CONFIRM + SAVE BOOKING
```

### File Structure
```
voice-agent/
├── guided_dialog.py         # Core engine (Guided-First)
├── src/
│   ├── orchestrator.py      # 4-layer RAG (legacy)
│   ├── booking_state_machine.py
│   ├── nlu/                 # Intent + Entity extraction
│   ├── tts.py              # Text-to-Speech
│   └── faq_manager.py      # FAQ retrieval
├── data/
│   ├── verticals/          # JSON config per verticale
│   │   ├── salone.json
│   │   ├── palestra.json
│   │   ├── medical.json
│   │   └── auto.json
│   └── faq_*.json          # FAQ files
└── tests/
    └── test_guided_dialog.py
```

### Slot Collection Order
```python
SLOT_ORDER = [
    "servizio",      # Cosa? (taglio, piega, colore)
    "operatore",     # Chi? (Marco, Giulia, chiunque)
    "data",          # Quando? (domani, martedi, 28/01)
    "ora",           # A che ora? (10:00, mattina)
    "cliente_nome",  # Nome (se nuovo cliente)
    "cliente_tel",   # Telefono (se nuovo cliente)
]
```

### Fuzzy Matching Italiano
```python
# Ordinali
"1" | "uno" | "primo" | "il primo" → index 0

# Date relative
"oggi" → datetime.now()
"domani" → +1 day
"martedi" → next Tuesday

# Fasce orarie
"mattina" → "09:00"
"pomeriggio" → "14:00"

# Conferme
"si" | "va bene" | "ok" → True
"no" | "annulla" → False
```

### Vertical Config Schema
```json
{
  "vertical_id": "salone",
  "slots_order": ["servizio", "operatore", "data", "ora"],
  "prompts": {
    "greeting_standard": "Buongiorno! Sono Sara...",
    "ask_servizio": "Quale servizio vi interessa?",
    "fallback_soft": "Scusate, non ho capito...",
    "escalation_message": "Vi passo a un collega..."
  },
  "faq_inline": [
    {
      "triggers": ["prezzo", "costo"],
      "risposta": "Taglio uomo 20 euro..."
    }
  ]
}
```

## Rules
1. SEMPRE usare Guided-First approach (proponi opzioni, poi valida)
2. SEMPRE implementare fuzzy matching per input italiano
3. MAI usare NLU come prima linea - solo per validazione
4. SEMPRE avere 3 livelli fallback: soft → numerate → escalation
5. SEMPRE loggare conversazioni per analytics
6. MAI salvare dati sensibili senza consenso GDPR
7. SEMPRE testare con input ambigui ("boh", "non so", "mah")

## Python Stack
- Python 3.13 (no PyTorch)
- SQLite per DB
- FastAPI per HTTP bridge (porta 3001)
- No sentence-transformers (FAISS disabilitato)

## Test Commands
```bash
# Run self-test
python voice-agent/guided_dialog.py

# Run test suite
pytest voice-agent/tests/test_guided_dialog.py -v
```

## Files to Reference
- `voice-agent/guided_dialog.py` - Core engine
- `voice-agent/data/verticals/*.json` - Vertical configs
- `docs/context/VOICE-AGENT-RAG-ENTERPRISE.md` - Architecture docs
