# FLUXION Voice Agent - Troubleshooting Guide

## Quick Diagnostics

```python
from src.pipeline import VoicePipeline

# Check pipeline health
pipeline = VoicePipeline(config)

# Check circuit breaker status
status = pipeline.recovery_manager.get_health_status()
print(status)  # {"groq": "closed", "database": "closed"}

# Check analytics
metrics = pipeline.analytics_logger.get_metrics()
print(f"Groq fallback rate: {metrics.groq_usage_percent:.1%}")
print(f"Avg latency: {metrics.avg_latency_ms:.0f}ms")
```

---

## Common Issues

### 1. High Latency (>200ms)

**Symptoms:**
- Responses take too long
- Users complain about slow bot

**Diagnosis:**
```python
# Check which layer is being used most
metrics = logger.get_metrics()
print(metrics.layer_usage)
# {"L1_exact": 10, "L3_faq": 50, "L4_groq": 40}  <- Too much Groq!
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Too many Groq calls | Improve FAQ coverage |
| FAQ semantic search slow | Reduce embedding model size |
| Database slow | Add indexes, optimize queries |
| Network latency | Check HTTP bridge connection |

```python
# Improve FAQ coverage
failed_queries = logger.get_failed_queries(min_count=3)
for query in failed_queries:
    print(f"Add FAQ for: '{query['user_input']}'")
```

---

### 2. Low Intent Accuracy

**Symptoms:**
- Wrong intent detected
- Bot gives irrelevant responses

**Diagnosis:**
```python
from src import classify_intent

# Test specific inputs
result = classify_intent("vorrei disdire l'appuntamento")
print(f"Intent: {result.category}, Confidence: {result.confidence}")

# Check intent distribution
metrics = logger.get_metrics()
print(metrics.intent_distribution)
```

**Solutions:**

| Pattern | Fix |
|---------|-----|
| "disdire" -> INFO instead of CANCELLAZIONE | Add pattern to classifier |
| Low confidence (<0.7) | Add more keywords |
| Ambiguous phrases | Add context-aware rules |

```python
# Add to intent_classifier.py BOOKING_PATTERNS
CANCELLATION_PATTERNS = [
    r"(?:vorrei|voglio|devo)\s+(?:disdire|cancellare|annullare)",
    r"(?:disdetta|cancellazione)\s+(?:appuntamento|prenotazione)",
]
```

---

### 3. FAQ Not Matching

**Symptoms:**
- Bot doesn't answer FAQ questions
- Falls back to Groq for simple questions

**Diagnosis:**
```python
from src import FAQManager

manager = FAQManager()
manager.load_faqs_from_json("data/faq.json")

# Test matching
result = manager.find_answer("quanto costa taglio")
print(result)  # None = no match

# Debug keyword matching
from src.faq_manager import find_keyword_match
match = find_keyword_match("quanto costa taglio", manager.faqs)
print(match)
```

**Solutions:**

| Issue | Fix |
|-------|-----|
| Missing keywords | Add synonyms to FAQ keywords |
| Threshold too high | Lower `keyword_threshold` to 0.2 |
| Typos in user input | Enable fuzzy matching |
| Missing FAQ | Add the missing Q&A |

```json
{
  "question": "Quanto costa un taglio?",
  "keywords": ["prezzo", "costo", "quanto", "taglio", "costa", "euro", "€"],
  "variations": [
    "qual è il prezzo del taglio",
    "quanto viene un taglio",
    "prezzi taglio"
  ]
}
```

---

### 4. False Frustration Detection

**Symptoms:**
- Bot escalates when user isn't frustrated
- "contento" triggers frustration (substring match)

**Diagnosis:**
```python
from src import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze("sono contento del servizio")
print(result.frustration_level)  # Should be NONE
print(result.triggers)           # Should be empty
```

**Solutions:**

| Issue | Fix |
|-------|-----|
| Substring match ("no" in "sono") | Use word boundary matching |
| Single word false positive | Add to exclusion list |
| Threshold too low | Adjust frustration thresholds |

```python
# Word boundary keywords (only match as whole words)
WORD_BOUNDARY_KEYWORDS = {
    "no": 1,
    "ma": 1,
    "mai": 3,
}

# Check using word set, not substring
words = set(text.lower().split())
if "no" in words:  # Not: if "no" in text
    score += 1
```

---

### 5. Circuit Breaker Always Open

**Symptoms:**
- All Groq calls fail immediately
- `E005 CIRCUIT_OPEN` errors

**Diagnosis:**
```python
breaker = pipeline.recovery_manager.get_circuit_breaker("groq")
print(f"State: {breaker.state}")
print(f"Failures: {breaker._failure_count}")
print(f"Last failure: {breaker._last_failure_time}")
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| API key invalid | Check `GROQ_API_KEY` |
| Network issues | Check connectivity |
| Rate limiting | Increase delay between calls |
| Service outage | Wait for recovery timeout |

```python
# Force reset circuit breaker (use with caution)
breaker._state = CircuitState.CLOSED
breaker._failure_count = 0

# Or wait for recovery
# Default recovery_timeout is 30 seconds
```

---

### 6. Entity Extraction Failures

**Symptoms:**
- Dates not recognized
- Times parsed incorrectly
- Names missed

**Diagnosis:**
```python
from src import extract_all

result = extract_all("domani alle tre con Marco", {})
print(f"Date: {result.date}")
print(f"Time: {result.time}")
print(f"Name: {result.name}")
```

**Solutions:**

| Issue | Fix |
|-------|-----|
| "dopodomani" not recognized | Add to relative date patterns |
| "tre e mezza" fails | Add Italian time patterns |
| Name not in Italian names | Add to name database |

```python
# Add relative date
RELATIVE_DATES = {
    "oggi": 0,
    "domani": 1,
    "dopodomani": 2,
    "fra due giorni": 2,
}

# Add time pattern
TIME_PATTERNS.append(r"alle?\s+(\w+)\s+e\s+mezza")  # "tre e mezza"
```

---

### 7. Analytics Not Recording

**Symptoms:**
- No data in metrics
- Session not found errors

**Diagnosis:**
```bash
# Check database exists
ls -la data/analytics.db

# Check tables
sqlite3 data/analytics.db ".tables"

# Check recent entries
sqlite3 data/analytics.db "SELECT COUNT(*) FROM conversations"
```

**Solutions:**

| Issue | Fix |
|-------|-----|
| DB not created | Check db_path permissions |
| Session not started | Ensure `start_session()` called |
| Turns not logged | Check `log_turn()` is called |

```python
# Verify logger is working
from src import get_logger

logger = get_logger()
session = logger.start_session("test")
print(f"Session ID: {session.id}")

turn_id = logger.log_turn(
    session_id=session.id,
    user_input="test",
    intent="test",
    response="test",
    latency_ms=10.0,
    layer_used="L1_exact"
)
print(f"Turn ID: {turn_id}")
```

---

### 8. HTTP Bridge Connection Failed

**Symptoms:**
- `HTTP Bridge error: Connection refused`
- Client search returns empty

**Diagnosis:**
```bash
# Check if bridge is running
curl http://127.0.0.1:3001/api/health

# Check port
lsof -i :3001
```

**Solutions:**

| Issue | Fix |
|-------|-----|
| Bridge not running | Start Tauri backend |
| Wrong port | Check `HTTP_BRIDGE_URL` |
| Firewall blocking | Allow localhost:3001 |

```python
# Update bridge URL
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"

# Or use environment variable
import os
HTTP_BRIDGE_URL = os.environ.get("HTTP_BRIDGE_URL", "http://127.0.0.1:3001")
```

---

### 9. TTS Not Working

**Symptoms:**
- No audio output
- Piper errors

**Diagnosis:**
```bash
# Check Piper installation
which piper
piper --version

# Test Piper directly
echo "Ciao mondo" | piper --model it_IT-paola-medium --output_file test.wav
```

**Solutions:**

| Issue | Fix |
|-------|-----|
| Piper not installed | Run setup.sh |
| Model not found | Download model |
| Audio device issue | Check system audio |

```bash
# Install Piper
pip install piper-tts

# Download Italian model
piper --model it_IT-paola-medium --download

# Fall back to system TTS
pipeline = VoicePipeline(config, use_piper=False)
```

---

## Performance Tuning

### Reduce Groq Usage

```python
# 1. Improve FAQ coverage
failed = logger.get_failed_queries(min_count=2)
# Add FAQs for these queries

# 2. Lower FAQ thresholds
config = FAQConfig(
    keyword_threshold=0.2,      # Was 0.3
    semantic_threshold=0.55     # Was 0.65
)

# 3. Add more exact match patterns
# In intent_classifier.py
EXACT_RESPONSES["ciao"] = "Buongiorno! Come posso aiutarla?"
```

### Reduce Latency

```python
# 1. Disable semantic search (faster keyword-only)
config = FAQConfig(use_semantic=False)

# 2. Reduce timeout
timeout_config = TimeoutConfig(
    groq_api=10.0,  # Was 30.0
    http_bridge=2.0  # Was 5.0
)

# 3. Pre-load FAQs at startup
manager.load_faqs_from_json("data/faq.json")  # Do once at init
```

### Improve Accuracy

```python
# 1. Add FAQ variations
{
    "question": "Quanto costa un taglio?",
    "variations": [
        "qual è il prezzo del taglio",
        "quanto viene un taglio",
        "prezzi taglio",
        "costo taglio uomo",
        "costo taglio donna"
    ]
}

# 2. Add more intent patterns
BOOKING_PATTERNS.append(r"mi\s+prenoti")
BOOKING_PATTERNS.append(r"fissare\s+(?:un\s+)?appuntamento")

# 3. Improve entity extraction
# Add Italian names to database
# Add local time expressions
```

---

## Debugging Tools

### Enable Debug Logging

```python
import logging
logging.getLogger('src').setLevel(logging.DEBUG)

# Or for specific modules
logging.getLogger('src.faq_manager').setLevel(logging.DEBUG)
logging.getLogger('src.sentiment').setLevel(logging.DEBUG)
```

### Test Individual Components

```python
# Test intent classifier
from src import classify_intent
print(classify_intent("vorrei prenotare"))

# Test entity extractor
from src import extract_all
print(extract_all("domani alle 15", {}))

# Test FAQ manager
from src import FAQManager
m = FAQManager()
m.load_faqs_from_json("data/faq.json")
print(m.find_answer("quanto costa"))

# Test sentiment
from src import SentimentAnalyzer
a = SentimentAnalyzer()
print(a.analyze("non funziona mai!"))
```

### Inspect Analytics Data

```bash
# Open SQLite database
sqlite3 data/analytics.db

# Recent conversations
SELECT id, started_at, outcome, total_turns, groq_usage_count
FROM conversations
ORDER BY started_at DESC
LIMIT 10;

# Failed queries
SELECT user_input, intent, layer_used, COUNT(*) as count
FROM conversation_turns
WHERE intent_confidence < 0.7 OR layer_used = 'L4_groq'
GROUP BY user_input
ORDER BY count DESC
LIMIT 20;

# Layer usage distribution
SELECT layer_used, COUNT(*) as count
FROM conversation_turns
GROUP BY layer_used;

# Escalation reasons
SELECT escalation_reason, COUNT(*) as count
FROM conversations
WHERE outcome = 'escalated'
GROUP BY escalation_reason;
```

---

## Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: aiohttp` | Missing dependency | `pip install aiohttp` |
| `GROQ_API_KEY not set` | Missing env var | Set environment variable |
| `Circuit breaker OPEN` | Too many failures | Wait or check API |
| `FAQ file not found` | Wrong path | Check faq_path |
| `Database locked` | Concurrent access | Use connection pool |
| `Piper model not found` | Model not downloaded | Download model |
| `HTTP Bridge timeout` | Backend not running | Start Tauri |

---

## Getting Help

1. Check this troubleshooting guide
2. Review logs: `tail -f voice_agent.log`
3. Check analytics: `get_metrics()`, `get_failed_queries()`
4. Test components individually
5. Check GitHub issues
6. Contact support with:
   - Error message
   - Log excerpt
   - Config (without API keys)
   - Steps to reproduce
