# FLUXION Voice Agent - API Documentation

## Overview

The FLUXION Voice Agent is a 5-layer RAG pipeline for Italian voice assistants, designed for automatic booking systems in SMB environments (salons, gyms, clinics, restaurants).

**Architecture:**
```
Layer 0: Sentiment Analysis    (<5ms)   - Frustration detection, escalation triggers
Layer 1: Exact Match           (<1ms)   - Courtesy phrases, confirmations
Layer 2: Intent Classification (<20ms)  - Pattern-based intent detection
Layer 3: FAQ Retrieval         (<50ms)  - Hybrid keyword + semantic search
Layer 4: Groq LLM              (500ms+) - Complex query fallback
```

---

## Core Modules

### 1. Intent Classifier (`src/intent_classifier.py`)

Classifies user intent using pattern matching and keyword detection.

#### Classes

**`IntentCategory`** (Enum)
```python
class IntentCategory(Enum):
    PRENOTAZIONE = "prenotazione"   # Booking request
    CANCELLAZIONE = "cancellazione" # Cancellation
    MODIFICA = "modifica"           # Modification
    INFO = "info"                   # Information request
    CORTESIA = "cortesia"           # Courtesy phrases
    CONFERMA = "conferma"           # Confirmation
    RIFIUTO = "rifiuto"             # Rejection
    OPERATORE = "operatore"         # Operator request
    SCONOSCIUTO = "sconosciuto"     # Unknown
```

**`IntentResult`** (dataclass)
```python
@dataclass
class IntentResult:
    category: IntentCategory
    confidence: float           # 0.0 - 1.0
    response: Optional[str]     # Pre-built response for cortesia/conferma
    matched_pattern: Optional[str]
```

#### Functions

**`classify_intent(text: str) -> IntentResult`**

Main entry point for intent classification.

```python
from src import classify_intent, IntentCategory

result = classify_intent("Vorrei prenotare un taglio")
print(result.category)    # IntentCategory.PRENOTAZIONE
print(result.confidence)  # 0.95
```

**`exact_match_intent(text: str) -> Optional[IntentResult]`**

O(1) lookup for exact phrase matches (greetings, confirmations).

**`pattern_based_intent(text: str) -> IntentResult`**

Regex-based pattern matching for booking intents.

**`normalize_input(text: str) -> str`**

Normalizes text: lowercase, strip, remove extra whitespace.

---

### 2. Entity Extractor (`src/entity_extractor.py`)

Extracts structured entities from Italian natural language text.

#### Classes

**`ExtractedDate`** (dataclass)
```python
@dataclass
class ExtractedDate:
    date: datetime.date
    original_text: str
    is_relative: bool    # "domani", "lunedì prossimo"

    def to_string(self, format: str = "%Y-%m-%d") -> str: ...
    def to_italian(self) -> str: ...  # "lunedì 15 gennaio"
```

**`ExtractedTime`** (dataclass)
```python
@dataclass
class ExtractedTime:
    hour: int
    minute: int
    original_text: str
    is_approximate: bool  # "nel pomeriggio", "verso le 3"

    def to_string(self) -> str: ...  # "15:30"
```

**`ExtractedName`** (dataclass)
```python
@dataclass
class ExtractedName:
    name: str
    original_text: str
    confidence: float
```

**`ExtractionResult`** (dataclass)
```python
@dataclass
class ExtractionResult:
    date: Optional[ExtractedDate]
    time: Optional[ExtractedTime]
    name: Optional[ExtractedName]
    service: Optional[str]
    phone: Optional[str]
    email: Optional[str]
```

#### Functions

**`extract_all(text: str, services_config: Dict) -> ExtractionResult`**

Extract all entities from text in one call.

```python
from src import extract_all

services = {
    "taglio": ["taglio", "tagliare"],
    "colore": ["colore", "tinta"]
}

result = extract_all("Vorrei un taglio domani alle 15", services)
print(result.service)     # "taglio"
print(result.date.date)   # datetime.date(2026, 1, 13)
print(result.time.hour)   # 15
```

**`extract_date(text: str) -> Optional[ExtractedDate]`**

Extract date from Italian text. Supports:
- Relative: "oggi", "domani", "dopodomani"
- Weekdays: "lunedì", "martedì prossimo"
- Absolute: "15 gennaio", "15/01/2026"

**`extract_time(text: str) -> Optional[ExtractedTime]`**

Extract time. Supports:
- Exact: "alle 15:30", "alle tre e mezza"
- Approximate: "nel pomeriggio", "di mattina"
- Italian words: "mezzogiorno", "mezzanotte"

**`extract_name(text: str) -> Optional[ExtractedName]`**

Extract names from patterns like "mi chiamo X", "sono X".

**`extract_service(text: str, services_config: Dict) -> Optional[str]`**

Extract service from configured keywords.

---

### 3. FAQ Manager (`src/faq_manager.py`)

Hybrid keyword + semantic FAQ retrieval system.

#### Classes

**`FAQConfig`** (dataclass)
```python
@dataclass
class FAQConfig:
    keyword_threshold: float = 0.3      # Min keyword match score
    semantic_threshold: float = 0.65    # Min semantic similarity
    keyword_weight: float = 0.4         # Weight for hybrid score
    semantic_weight: float = 0.6
    max_results: int = 3
```

**`FAQMatch`** (dataclass)
```python
@dataclass
class FAQMatch:
    question: str
    answer: str
    confidence: float      # 0.0 - 1.0
    source: str           # "keyword", "semantic", "hybrid"
    category: Optional[str]
```

**`FAQManager`** (class)

```python
from src import FAQManager, FAQConfig

# Initialize
manager = FAQManager(config=FAQConfig(semantic_threshold=0.7))

# Load FAQs from JSON
manager.load_faqs_from_json("data/faq_salone.json")

# Load from Markdown
manager.load_faqs_from_markdown("data/faq_salone.md")

# Find answer
result = manager.find_answer("quanto costa un taglio?")
if result:
    print(result.answer)      # "Il taglio uomo costa 18€..."
    print(result.confidence)  # 0.85
    print(result.source)      # "keyword"
```

#### Functions

**`create_faq_manager(config: FAQConfig = None) -> FAQManager`**

Factory function for creating configured FAQ manager.

**`find_keyword_match(text: str, faqs: List[FAQ]) -> Optional[FAQMatch]`**

Direct keyword matching without semantic search.

---

### 4. Sentiment Analyzer (`src/sentiment.py`)

Italian sentiment and frustration detection for escalation triggers.

#### Classes

**`Sentiment`** (Enum)
```python
class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
```

**`FrustrationLevel`** (Enum)
```python
class FrustrationLevel(Enum):
    NONE = 0      # No frustration detected
    LOW = 1       # Mild impatience
    MEDIUM = 2    # Notable frustration
    HIGH = 3      # High frustration, consider escalation
    CRITICAL = 4  # Immediate escalation required
```

**`SentimentResult`** (dataclass)
```python
@dataclass
class SentimentResult:
    sentiment: Sentiment
    frustration_level: FrustrationLevel
    confidence: float
    triggers: List[str]           # Detected frustration keywords
    should_escalate: bool         # True if escalation recommended
    escalation_reason: Optional[str]  # "user_requested", "frustration_critical"
```

**`SentimentAnalyzer`** (class)

```python
from src import SentimentAnalyzer, FrustrationLevel

analyzer = SentimentAnalyzer()

# Single analysis
result = analyzer.analyze("Non funziona mai questo sistema!")
print(result.frustration_level)  # FrustrationLevel.HIGH
print(result.should_escalate)    # True
print(result.triggers)           # ["mai", "non funziona"]

# Track cumulative frustration across turns
analyzer.analyze("Non capisco")           # LOW
analyzer.analyze("Ancora non funziona")   # Cumulative -> MEDIUM
analyzer.analyze("Basta! Passami un umano")  # -> escalation

# Reset for new conversation
analyzer.reset()
```

#### Functions

**`analyze_sentiment(text: str) -> SentimentResult`**

Stateless sentiment analysis.

**`detect_frustration(text: str) -> Tuple[FrustrationLevel, List[str]]`**

Detect frustration level and return triggers.

**`get_analyzer() -> SentimentAnalyzer`**

Get global analyzer instance (singleton).

---

### 5. Error Recovery (`src/error_recovery.py`)

Retry logic, circuit breaker, and fallback responses.

#### Classes

**`RetryConfig`** (dataclass)
```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 0.5       # seconds
    max_delay: float = 10.0
    exponential_base: float = 2.0
    jitter: bool = True           # Add randomness to prevent thundering herd
```

**`TimeoutConfig`** (dataclass)
```python
@dataclass
class TimeoutConfig:
    default: float = 5.0          # seconds
    groq_api: float = 30.0
    db_query: float = 2.0
    http_bridge: float = 5.0
```

**`CircuitState`** (Enum)
```python
class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject calls
    HALF_OPEN = "half_open" # Testing recovery
```

**`ErrorCategory`** (Enum)
```python
class ErrorCategory(Enum):
    NETWORK = "network"
    TIMEOUT = "timeout"
    SERVICE = "service"
    VALIDATION = "validation"
    UNKNOWN = "unknown"
```

**`CircuitBreaker`** (class)

```python
from src import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,    # Open after 5 failures
    recovery_timeout=30.0,  # Try recovery after 30s
    half_open_max=2         # Allow 2 test calls in half-open
)

if breaker.can_execute():
    try:
        result = await call_api()
        breaker.record_success()
    except Exception:
        breaker.record_failure()
else:
    # Circuit is open, use fallback
    result = get_fallback_response()
```

**`RecoveryManager`** (class)

Orchestrates multiple circuit breakers and fallback strategies.

```python
from src import get_recovery_manager

manager = get_recovery_manager()

# Get circuit breaker for specific service
groq_breaker = manager.get_circuit_breaker("groq")
db_breaker = manager.get_circuit_breaker("database")

# Check health
status = manager.get_health_status()
# {"groq": "closed", "database": "closed"}
```

#### Functions

**`retry_with_backoff(func, config: RetryConfig)`** (async)

Retry async function with exponential backoff.

```python
from src import retry_with_backoff, RetryConfig

config = RetryConfig(max_retries=3, base_delay=1.0)

@retry_with_backoff(config)
async def unstable_api_call():
    return await external_api.call()
```

**`retry_sync_with_backoff(func, config: RetryConfig)`**

Synchronous version of retry decorator.

**`get_fallback_response(intent: str, error_category: ErrorCategory) -> str`**

Get Italian fallback response based on context.

```python
from src import get_fallback_response, ErrorCategory

response = get_fallback_response(
    intent="prenotazione",
    error_category=ErrorCategory.SERVICE
)
# "Mi dispiace, ho avuto un problema tecnico. Può ripetere la sua richiesta?"
```

---

### 6. Analytics Logger (`src/analytics.py`)

Structured conversation logging for metrics and improvement loop.

#### Classes

**`ConversationOutcome`** (Enum)
```python
class ConversationOutcome(Enum):
    COMPLETED = "completed"     # User goal achieved
    ESCALATED = "escalated"     # Transferred to operator
    ABANDONED = "abandoned"     # User left mid-conversation
    ERROR = "error"             # Technical failure
    UNKNOWN = "unknown"         # Incomplete data
```

**`ConversationTurn`** (dataclass)
```python
@dataclass
class ConversationTurn:
    id: str
    conversation_id: str
    turn_number: int
    timestamp: datetime
    user_input: str
    intent: str
    intent_confidence: float
    response: str
    latency_ms: float
    layer_used: str           # "L1_exact", "L2_intent", "L3_faq", "L4_groq"
    sentiment: str
    frustration_level: int
    used_groq: bool
    escalated: bool
    entities_extracted: Dict
```

**`ConversationSession`** (dataclass)
```python
@dataclass
class ConversationSession:
    id: str
    verticale_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    client_id: Optional[str]
    client_name: Optional[str]
    outcome: ConversationOutcome
    total_turns: int
    total_latency_ms: float
    groq_usage_count: int
    escalation_reason: Optional[str]
    booking_created: bool
    booking_id: Optional[str]
```

**`AnalyticsMetrics`** (dataclass)
```python
@dataclass
class AnalyticsMetrics:
    total_conversations: int
    total_turns: int
    avg_turns_per_conversation: float
    avg_latency_ms: float
    groq_usage_percent: float
    escalation_rate: float
    completion_rate: float
    intent_distribution: Dict[str, int]
    layer_usage: Dict[str, int]
    peak_hours: Dict[int, int]
```

**`ConversationLogger`** (class)

```python
from src import ConversationLogger, ConversationOutcome, get_logger

# Get singleton instance
logger = get_logger()

# Or create with custom path
logger = ConversationLogger(db_path="data/analytics.db")

# Start session
session = logger.start_session(verticale_id="salone_bella_vita")

# Log turns
turn_id = logger.log_turn(
    session_id=session.id,
    user_input="Vorrei prenotare un taglio",
    intent="prenotazione",
    response="Certamente! Per quando desidera?",
    latency_ms=45.2,
    layer_used="L3_faq",
    sentiment="neutral",
    frustration_level=0,
    used_groq=False
)

# Update with client info
logger.update_session_client(
    session_id=session.id,
    client_id="client_123",
    client_name="Mario Rossi"
)

# End session
logger.end_session(
    session_id=session.id,
    outcome=ConversationOutcome.COMPLETED,
    booking_id="booking_456"
)

# Get metrics
metrics = logger.get_metrics(
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    verticale_id="salone_bella_vita"
)
print(f"Escalation rate: {metrics.escalation_rate:.1%}")
print(f"Groq usage: {metrics.groq_usage_percent:.1%}")

# Get failed queries for FAQ improvement
failed = logger.get_failed_queries(min_count=3)
for query in failed:
    print(f"'{query['user_input']}' failed {query['count']} times")

# GDPR: Cleanup old data
logger.cleanup_old_data(days=90)
```

#### Functions

**`get_logger(db_path: str = None) -> ConversationLogger`**

Get global logger instance (singleton).

---

## Pipeline Integration

### VoicePipeline (`src/pipeline.py`)

Main orchestrator that integrates all modules.

```python
from src.pipeline import VoicePipeline

config = {
    "business_name": "Salone Bella Vita",
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Martedi-Sabato",
    "services": ["Taglio", "Piega", "Colore"],
    "verticale_id": "salone_bella_vita"
}

pipeline = VoicePipeline(
    business_config=config,
    groq_api_key="your_api_key",
    use_piper=True,
    faq_path=Path("data/faq_salone.json")
)

# Process text input
result = await pipeline.process_text("Vorrei prenotare un taglio per domani")
print(result["response"])       # Bot response
print(result["intent"])         # Detected intent
print(result["booking_action"]) # Booking context

# Process audio input
result = await pipeline.process_audio(audio_bytes)

# Reset conversation (ends analytics session)
pipeline.reset_conversation(
    outcome=ConversationOutcome.COMPLETED,
    escalation_reason=None
)
```

---

## Data Formats

### FAQ JSON Format

```json
{
  "verticale": "salone",
  "faqs": [
    {
      "id": "faq_001",
      "category": "prezzi",
      "question": "Quanto costa un taglio?",
      "answer": "Il taglio uomo costa 18€, il taglio donna parte da 25€.",
      "keywords": ["prezzo", "costo", "quanto", "taglio"],
      "priority": 1
    }
  ],
  "settings": {
    "nome_attivita": "Salone Bella Vita",
    "orario_apertura": "09:00",
    "orario_chiusura": "19:00"
  }
}
```

### FAQ Markdown Format

```markdown
# FAQ Salone

## Prezzi
- quanto costa un taglio: Il taglio uomo costa 18€, donna da 25€
- quanto costa il colore: Il colore parte da 35€

## Orari
- a che ora aprite: Siamo aperti dalle {{orario_apertura}} alle {{orario_chiusura}}
- siete aperti di lunedì: No, siamo chiusi il lunedì
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Overall latency | <200ms | End-to-end without Groq |
| Intent accuracy | >90% | On test set |
| FAQ accuracy | >80% | Correct answer retrieval |
| Frustration detection | >90% precision | False positive rate <10% |
| Groq fallback rate | <20% | Queries requiring LLM |

---

## Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `E001` | NETWORK | Connection failed |
| `E002` | TIMEOUT | Request timed out |
| `E003` | SERVICE | External service error (Groq, DB) |
| `E004` | VALIDATION | Invalid input |
| `E005` | CIRCUIT_OPEN | Circuit breaker preventing calls |

---

## Thread Safety

- `SentimentAnalyzer`: Thread-safe for single analysis, use separate instances for concurrent conversation tracking
- `ConversationLogger`: Thread-safe (SQLite in serialized mode)
- `CircuitBreaker`: Thread-safe with threading.Lock
- `FAQManager`: Thread-safe for reads, not for concurrent FAQ loading

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-06 | Initial release: Intent, Entity, FAQ |
| 0.2.0 | 2026-01-10 | Week 2: FAQManager, E2E tests |
| 0.3.0 | 2026-01-12 | Week 3: Sentiment, Error Recovery, Analytics |
