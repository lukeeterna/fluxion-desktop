# Multi-Turn Conversation Test Suite

Comprehensive automated test suite for Sara voice agent that simulates REAL phone conversations with multiple turns (user message → Sara response → next user message).

## Overview

The suite tests complete conversation flows instead of isolated API calls. Each test scenario includes:

- **Setup**: Reset session, optionally choose vertical
- **Multiple turns**: User sends message → validate response structure, FSM state, intent
- **Assertions**: Check response contains expected keywords, FSM transitions are logical, HTTP status codes are correct

## Test Scenarios

### 1. Happy Path (Complete Booking)
```
User: "Buongiorno, vorrei un appuntamento"
Sara: [ask for name]
User: "Marco Rossi"
Sara: [ask for service]
User: "Un taglio per favore"
Sara: [ask for date]
User: "Domani alle 10"
Sara: [ask confirmation]
User: "Sì, confermo"
Sara: [booking confirmed]
User: "Grazie, arrivederci"
Sara: [exit conversation, should_exit=True]
```

**Validates**: Complete end-to-end booking, proper state transitions (WAITING_NAME → WAITING_SERVICE → WAITING_DATE → CONFIRMING → COMPLETED)

### 2. Bare Name from IDLE
```
User: "Marco Rossi" [no booking intent, just name]
Sara: [should NOT ask for greeting again, should ask for service]
```

**Validates**: System recognizes bare name and enters booking state automatically

### 3. Ambiguous Name Disambiguation
```
User: "Vorrei prenotare"
User: "Marco" [common name, might match multiple clients]
Sara: [ask for surname OR disambiguate]
```

**Validates**: Handles name collisions gracefully

### 4. New Client Registration
```
User: "Vorrei prenotare"
User: "Giovanni Nuovi" [not in DB]
Sara: [trigger registration flow, ask for phone/email]
```

**Validates**: New client registration pathway

### 5. Goodbye at Any Point
```
User: [mid-conversation] "Arrivederci"
Sara: [exit gracefully, should_exit=True]
```

**Validates**: Exit intent recognized from any FSM state

### 6. Service Name Corruption Check
```
User: "Vorrei tagliare i capelli e fare la barba"
Sara: [should NOT confuse "barba" (beard service) with "Barbieri" (surname)]
```

**Validates**: STT/NLU doesn't corrupt service names to person names

### 7. FAQ Questions
```
User: "Quanto costa un taglio uomo?"
Sara: [return price from DB or prompt]
User: "Quali sono gli orari?"
Sara: [return business hours]
```

**Validates**: FAQ retrieval, price/hours information

### 8. Cancel/Modify
```
User: [mid-booking] "Voglio annullare"
Sara: [acknowledge cancellation]
```

**Validates**: Cancellation intent during booking

### 9. Operator Escalation
```
User: "Vorrei parlare con un operatore"
Sara: [escalate or offer to connect]
```

**Validates**: Escalation pathway

### 10. Edge Cases
```
User: "" [empty string]
User: "[500+ char gibberish]" [very long]
User: "..." [only punctuation]
User: "3281234567" [phone number]
User: "@#$%^&*()" [special chars]
User: "I want to book a haircut" [English]
```

**Validates**: Graceful handling of malformed input, no crashes

## Running the Tests

### On iMac (Pipeline Running)

```bash
cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent

# Run all tests
python -m pytest tests/e2e/test_multi_turn_conversations.py -v

# Run specific test class
python -m pytest tests/e2e/test_multi_turn_conversations.py::TestHappyPath -v

# Run with verbose output (see each turn)
VERBOSE=1 python -m pytest tests/e2e/test_multi_turn_conversations.py -v

# Run with custom pipeline URL
PIPELINE_URL=http://192.168.1.2:3002 python -m pytest tests/e2e/test_multi_turn_conversations.py -v
```

### Remote from MacBook

```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python -m pytest tests/e2e/test_multi_turn_conversations.py -v"
```

### Direct Execution

```bash
cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent
python tests/e2e/test_multi_turn_conversations.py
```

## Test Output Format

Each test outputs:

```
test_returning_client_complete_booking PASSED                    [100%]
```

Verbose output (VERBOSE=1) shows:

```
[process] 'Buongiorno, vorrei un appuntamento' → state=idle intent=cortesia ms=450
[process] 'Marco Rossi' → state=waiting_service intent=nome ms=320
[process] 'Un taglio per favore' → state=waiting_date intent=servizio ms=280
...
```

## Assertions

Tests use pattern matching (case-insensitive) instead of exact text matching:

```python
assert_response_contains(response, "nome", "chi", "cortesia")
# ✅ passes if response contains any of: "nome", "chi", "cortesia"

assert_response_contains(response, "prezzo", must_not_contain=["non", "gratuito"])
# ✅ passes if response contains "prezzo" but NOT "non" or "gratuito"
```

This makes tests resilient to minor response text changes.

## Response Structure

Each `process()` call returns:

```json
{
  "success": true,
  "transcription": "Buongiorno",
  "response": "Buongiorno! Come posso aiutarti?",
  "intent": "cortesia",
  "fsm_state": "idle",
  "layer": "l1_exact_match",
  "should_exit": false,
  "should_escalate": false,
  "needs_disambiguation": false,
  "session_id": "sess_12345",
  "latency_ms": 450,
  "_latency_ms": 450.5
}
```

Tests validate:
- `success` = True (no server error)
- `response` contains expected keywords (pattern matching)
- `fsm_state` is in expected state set
- `should_exit` = True for goodbye intents
- `should_escalate` = True for operator requests
- `_latency_ms` < 2000ms (reasonable latency)

## FSM States

Valid states tested:

- `idle` — no conversation
- `waiting_name` — asking for client name
- `waiting_surname` — asking for surname (disambiguation)
- `waiting_service` — asking which service
- `waiting_date` — asking for date
- `waiting_time` — asking for time
- `confirming` — asking for confirmation
- `completed` — booking confirmed
- `cancelled` — booking cancelled
- `disambiguating_name` — resolving name collision
- `waiting_operator` — escalated to operator

## Troubleshooting

### "Pipeline not responding at http://127.0.0.1:3002"

**Solution**: Start the pipeline on iMac

```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python main.py"
```

### Tests timeout (30s)

**Possible causes**:
- Pipeline crashed or hung
- Network latency
- Slow NLU/LLM calls

**Solution**: Check pipeline logs

```bash
ssh imac "tail -100 /tmp/voice-pipeline.log"
```

### Unexpected FSM state

Tests may fail if:
1. FSM transitions changed (read booking_state_machine.py)
2. Database schema changed (check vertical services)
3. NLU confidence thresholds changed

**Solution**: Check orchestrator logs and FSM state machine

### Response doesn't contain expected keywords

Likely reasons:
1. Response text generation changed
2. NLU intent classification changed
3. Pipeline running old code

**Solution**: Deploy latest changes and restart pipeline

## Integration with CI/CD

To integrate into CI pipeline:

```bash
#!/bin/bash
set -e

# Run on iMac (requires SSH access)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  python -m pytest tests/e2e/test_multi_turn_conversations.py -v --tb=short"

echo "✅ All multi-turn tests passed"
```

## Design Rationale

### Why Multi-Turn?

Single API calls don't validate:
- FSM state transitions
- Long conversation coherence
- Interruption handling
- Escalation from mid-flow

Real phone conversations are multi-turn. These tests simulate that.

### Why Pattern Matching?

Exact text matching is fragile:
- Minor prompt wording changes break tests
- Localization/variation in responses breaks tests
- Tests become maintenance burden

Pattern matching with keywords is resilient:
- Tests focus on WHAT Sara should communicate (intent)
- Tests tolerate reasonable variation in HOW (wording)
- Tests remain valid as prompts evolve

### Why HTTP Instead of Unit Tests?

Live HTTP tests validate:
- Full pipeline integration (STT → NLU → FSM → TTS)
- Network latency
- Session management
- Real database state

Unit tests validate individual components (entity_extractor, FSM) but miss integration issues.

## Contributing

To add new test scenarios:

1. Create test class inheriting from object (no base class needed)
2. Add test methods with descriptive names
3. Use `ConversationContext` to manage session
4. Assert on response content, FSM state, latency
5. Run: `python -m pytest tests/e2e/test_multi_turn_conversations.py::YourClass -v`

Example:

```python
class TestMyScenario:
    """Description of scenario."""

    def test_my_flow(self):
        """Test a specific conversation flow."""
        ctx = ConversationContext(vertical="salone")
        
        t1 = ctx.turn("User input")
        assert t1["success"]
        assert_response_contains(t1["response"], "expected_keyword")
        assert t1["fsm_state"] in ("expected_state1", "expected_state2")
```

## References

- **Pipeline**: `/Volumes/MacSSD - Dati/fluxion/voice-agent/main.py`
- **FSM**: `/Volumes/MacSSD - Dati/fluxion/voice-agent/src/booking_state_machine.py`
- **Orchestrator**: `/Volumes/MacSSD - Dati/fluxion/voice-agent/src/orchestrator.py`
- **Existing e2e tests**: `tests/e2e/test_sara_stress_per_verticale.py`
