# SKILL: Fluxion Voice Agent (Sara)

> **ID**: fluxion-voice-agent
> **Version**: 1.0.0
> **Category**: AI/Voice
> **Stack**: Python 3.11+ + spaCy + Groq + Chatterbox TTS

---

## Overview

This skill encodes the patterns for the Fluxion Voice Agent "Sara" - an enterprise-grade Italian voice assistant for booking management. It implements a 5-layer RAG pipeline with progressive fallback.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VOICE PIPELINE                           │
├─────────────────────────────────────────────────────────────┤
│  Audio In → STT (Whisper/Groq) → NLU → Orchestrator → TTS  │
│                                    ↓                        │
│                              HTTP Bridge                    │
│                                    ↓                        │
│                           Tauri Backend (SQLite)            │
└─────────────────────────────────────────────────────────────┘
```

## 5-Layer RAG Pipeline

| Layer | Name | Latency | Purpose |
|-------|------|---------|---------|
| L0 | Sentiment | <1ms | Detect greetings, farewells, frustration |
| L1 | Exact Match | <5ms | Keyword-based intent (ORARI, PREZZI) |
| L2 | Intent Classification | <10ms | spaCy + regex for complex intents |
| L3 | FAQ Retrieval | <50ms | FAISS semantic / keyword search |
| L4 | LLM Fallback | <500ms | Groq Llama for unknown queries |

### Layer Implementation

```python
# L0: Sentiment (regex-based)
SENTIMENT_PATTERNS = {
    "CORTESIA": r"\b(buongiorno|buonasera|ciao|salve)\b",
    "CONGEDO": r"\b(arrivederci|grazie|a presto)\b",
    "FRUSTRAZIONE": r"\b(non capisco|ripeti|aiuto)\b",
}

# L1: Exact Match
EXACT_INTENTS = {
    "ORARI": ["orari", "apertura", "chiusura", "quando aprite"],
    "PREZZI": ["quanto costa", "prezzo", "listino", "costo"],
    "PRENOTAZIONE": ["prenotare", "appuntamento", "prenoto"],
}

# L2: spaCy NER + Intent
def classify_intent(text: str) -> Intent:
    doc = nlp(text)
    entities = extract_entities(doc)
    return Intent(name=..., entities=entities, confidence=...)

# L3: FAQ Retrieval
def search_faq(query: str, vertical: str) -> List[FAQ]:
    # FAISS if PyTorch available, else keyword
    return faq_manager.search(query, top_k=3)

# L4: Groq LLM
async def llm_fallback(context: ConversationContext) -> str:
    return await groq_client.chat(
        model="llama-3.1-70b-versatile",
        messages=context.to_messages(),
    )
```

## Entity Extraction

### Supported Entities

| Entity | Examples | Pattern |
|--------|----------|---------|
| DATE | "lunedì", "domani", "15 gennaio" | spaCy + dateparser |
| TIME | "alle 10", "10:30", "mattina" | regex + normalization |
| NOME | "Mario Rossi" | spaCy NER (PER) |
| TELEFONO | "333 1234567" | regex `\d{10}` |
| EMAIL | "mario@example.com" | regex email pattern |
| SERVIZIO | "taglio", "piega", "colore" | fuzzy match vs DB |

### Extraction Pipeline

```python
def extract_entities(text: str) -> Dict[str, Any]:
    doc = nlp(text)
    entities = {}

    # spaCy NER
    for ent in doc.ents:
        if ent.label_ == "PER":
            entities["nome"] = ent.text
        elif ent.label_ == "DATE":
            entities["data"] = parse_italian_date(ent.text)

    # Regex patterns
    if match := re.search(r"\d{10}", text):
        entities["telefono"] = match.group()

    # Time extraction
    if time := extract_time(text):
        entities["ora"] = time

    return entities
```

## Conversation State Machine

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  START   │───▶│ SERVIZIO │───▶│   DATA   │
└──────────┘    └──────────┘    └──────────┘
                                     │
┌──────────┐    ┌──────────┐    ┌────▼─────┐
│ CONFERMA │◀───│  DATI    │◀───│   ORA    │
└──────────┘    └──────────┘    └──────────┘
      │
      ▼
┌──────────┐
│   END    │
└──────────┘
```

### State Transitions

```python
class ConversationState(Enum):
    START = "start"
    SERVIZIO = "servizio"
    DATA = "data"
    ORA = "ora"
    DATI_CLIENTE = "dati_cliente"
    CONFERMA = "conferma"
    END = "end"

def next_state(current: ConversationState, entities: Dict) -> ConversationState:
    if current == ConversationState.START:
        if "servizio" in entities:
            return ConversationState.DATA
        return ConversationState.SERVIZIO
    # ... etc
```

## Disambiguation Handler

### Flow

```
1. "Prenotazione per Mario Rossi"
   → Backend returns 2 matches
   → "Ho trovato 2 clienti. Mi può dire la data di nascita?"

2. User provides date
   → If match: proceed
   → If no match: fallback to soprannome

3. "Mario o Marione?"
   → User says "Marione"
   → Match by soprannome field
```

### Implementation

```python
class DisambiguationHandler:
    async def handle(self, matches: List[Cliente], context: Context) -> str:
        if len(matches) == 1:
            return self.confirm_cliente(matches[0])

        # First attempt: data_nascita
        if not context.disambiguation_attempted:
            context.disambiguation_attempted = True
            context.pending_matches = matches
            return "Ho trovato più clienti. Mi può dire la sua data di nascita?"

        # Fallback: soprannome
        soprannomi = [m.soprannome for m in matches if m.soprannome]
        if soprannomi:
            return f"È {' o '.join(soprannomi)}?"

        return "Mi può dare più informazioni per identificarla?"
```

## TTS Configuration

### Engine Priority

1. **Chatterbox Italian** (Primary)
   - Quality: 9/10
   - Latency: 100-150ms CPU
   - Requires: PyTorch

2. **Piper** (Fallback)
   - Quality: 7.5/10
   - Latency: 50ms
   - Model: `it_IT-paola-medium`

3. **SystemTTS** (Last Resort)
   - Quality: 5/10
   - Uses: macOS `say -v Alice`

### Voice Name

```python
VOICE_NAME = "Sara"  # Unified across all engines
```

## HTTP Bridge Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/clienti/search` | GET | Search clients by name/phone |
| `/api/appuntamenti/create` | POST | Create appointment |
| `/api/appuntamenti/disponibilita` | GET | Check availability |
| `/api/servizi/list` | GET | List services |
| `/api/operatori/list` | GET | List operators |
| `/api/waitlist/add` | POST | Add to VIP waitlist |

## FAQ Vertical System

### Supported Verticals

| Vertical | FAQ File | Count |
|----------|----------|-------|
| salone | `faq_salone.json` | 25 |
| wellness | `faq_wellness.json` | 24 |
| medical | `faq_medical.json` | 24 |
| auto | `faq_auto.json` | 23 |
| altro | `faq_altro.json` | 10 |

### Variable Substitution

```json
{
  "question": "Quali sono i vostri orari?",
  "answer": "Siamo aperti dal {{ORARIO_APERTURA}} alle {{ORARIO_CHIUSURA}}, da {{GIORNI_APERTURA}}.",
  "keywords": ["orari", "apertura", "chiusura"]
}
```

```python
# vertical_loader.py
def load_faq(vertical: str, config: Dict) -> List[FAQ]:
    faqs = load_json(f"faq_{vertical}.json")
    for faq in faqs:
        faq["answer"] = substitute_variables(faq["answer"], config)
    return faqs
```

## Error Handling

### Graceful Degradation

```python
async def process_utterance(text: str) -> str:
    try:
        # L0-L3
        response = await pipeline.process(text)
        if response:
            return response
    except Exception as e:
        logger.warning(f"Pipeline error: {e}")

    # L4 Fallback
    try:
        return await llm_fallback(text)
    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")

    # Ultimate fallback
    return "Mi scusi, non ho capito. Può ripetere?"
```

### Retry Logic

```python
@retry(max_attempts=3, backoff=exponential)
async def call_groq(messages: List[Message]) -> str:
    return await groq_client.chat(messages=messages)
```

## Testing Patterns

### Unit Tests

```python
# test_nlu.py
def test_extract_date_domani():
    result = extract_date("vorrei prenotare per domani")
    assert result == date.today() + timedelta(days=1)

def test_intent_prenotazione():
    intent = classify_intent("vorrei prenotare un taglio")
    assert intent.name == "PRENOTAZIONE"
    assert intent.confidence > 0.8
```

### Integration Tests

```python
# test_orchestrator.py
async def test_full_booking_flow():
    session = await orchestrator.start_session()

    response = await session.process("Buongiorno, vorrei prenotare")
    assert "servizio" in response.lower() or "giorno" in response.lower()

    response = await session.process("Taglio per sabato alle 10")
    assert "nome" in response.lower()

    # ... complete flow
```

## Performance SLA

| Operation | Target | Actual |
|-----------|--------|--------|
| STT (Whisper) | <300ms | ~250ms |
| NLU (L0-L2) | <20ms | ~15ms |
| FAQ Search | <50ms | ~30ms |
| LLM (L4) | <500ms | ~400ms |
| TTS | <200ms | ~150ms |
| **E2E** | <2000ms | ~1500ms |

---

## Usage

When modifying the Voice Agent:

1. **Follow the 5-layer pattern** - Don't bypass layers
2. **Test with pytest** - 426+ tests must pass
3. **Update FAQ files** - Keep keywords relevant
4. **Preserve backward compat** - Don't break HTTP Bridge
5. **Document changes** - Update CLAUDE-VOICE.md
