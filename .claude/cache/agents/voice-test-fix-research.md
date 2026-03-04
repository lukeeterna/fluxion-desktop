# Voice Test Fix Research — CoVe 2026
> Generato: 2026-03-04 | Agente: voice-engineer | Task Fix 34 test

---

## Suite attuale (senza VAD files)

```
33 FAILED + 6 ERROR + 1064 PASSED + 28 SKIPPED = ~1110 totali
```

---

## Cluster A: ASKING_CLOSE_CONFIRMATION — 25 FAIL

### Sotto-cluster A1: FSM diretta (5 test in `test_booking_state_machine.py`)

**Errore:**
```
AssertionError: assert <BookingState.ASKING_CLOSE_CONFIRMATION> == <BookingState.COMPLETED>
```

**Root cause:** I test si aspettano che dopo `process_message("sì confermo")` in stato CONFIRMING, lo stato diventi `COMPLETED` con `should_exit=True`. L'implementazione attuale in `booking_state_machine.py` righe 2426-2433 aggiunge uno step intermedio:
```python
self.context.state = BookingState.ASKING_CLOSE_CONFIRMATION
return StateMachineResult(
    next_state=BookingState.ASKING_CLOSE_CONFIRMATION,
    response=TEMPLATES["ask_close_confirmation"],
    booking=booking
    # should_exit=False — aspetta risposta utente
)
```
Questo step (chiede "vuole terminare la chiamata?") fu aggiunto dopo la scrittura dei test.

**Bug4 (`test_bug4_completed_state_closes_call`):** Il test si aspetta che in stato COMPLETED su qualsiasi input restituisca `should_exit=True`. L'implementazione risponde "Mi faccia capire meglio" con `should_exit=False`.

### Sotto-cluster A2: `process()` missing (20 test in e2e + altri file)

**Errore:**
```
AttributeError: 'BookingStateMachine' object has no attribute 'process'
```

**Root cause:** `/voice-agent/src/booking_orchestrator.py` riga 75:
```python
result = self.state_machine.process(message, ctx)  # metodo inesistente
```
Il metodo corretto si chiama `process_message(user_input: str)`. L'orchestrator non è stato aggiornato quando la FSM ha rinominato il metodo. Causa il fallimento a cascata di:
- `test_booking_e2e_complete.py` (10 test)
- `test_cancel_reschedule.py` (1 test)
- `test_multi_verticale.py` (3 test)
- `test_pipeline_e2e.py` (1 test)
- `test_whatsapp.py` (1 test)

---

## Cluster B: log_turn() API mismatch — 8 FAIL + 6 ERROR

**I test chiamano:**
```python
logger.log_turn(
    session_id=session_id,   # keyword 'session_id' NON ESISTE
    user_input="...",
    ...
)
```

**L'implementazione ha (`analytics.py` riga 378):**
```python
def log_turn(
    self,
    session_id_or_turn=None,   # rinominato da 'session_id' a 'session_id_or_turn'
    user_input: str = "",
    ...
```

Il parametro fu rinominato per supportare dual-API. I test usano il keyword originale → `TypeError`.
I 6 ERROR sono setup errors della fixture `logger_with_data` che usa `log_turn(session_id=...)`.

**Occorrenze nei test da aggiornare:** `test_analytics.py` righe 61, 204, 219, 235, 250, 274, 351 (×2), 377, 395, 489, 518.

---

## Cluster C: ModuleNotFoundError groq — 1 FAIL

**Test:** `test_voice_agent_complete.py::TestPerformance::test_response_latency`

**Root cause:** `groq_client.py` importa `from groq import Groq, AsyncGroq` a livello modulo. Il package `groq` non è installato su MacBook. Fix: `pytest.importorskip('groq')` o mock.

---

## Fix Proposti (ordine esecuzione)

### Fix 1 — Alias `session_id` in `log_turn()` (15 min)

```python
# analytics.py — backward-compat alias nella signature:
def log_turn(
    self,
    session_id_or_turn=None,
    *,
    session_id=None,          # alias backward-compat
    user_input: str = "",
    ...
) -> str:
    if session_id is not None and session_id_or_turn is None:
        session_id_or_turn = session_id
    ...
```

Risolve: 14 test/error (8 FAIL + 6 ERROR).

### Fix 2 — Alias `process()` in BookingStateMachine (15 min)

```python
# booking_state_machine.py — aggiungere alias:
def process(self, message: str, ctx=None) -> StateMachineResult:
    """Alias di process_message() per compatibilità booking_orchestrator."""
    return self.process_message(message)
```

Risolve: 13+ test cascade (20 FAIL totali del cluster A2, condivisi con fix 3).

### Fix 3 — Aggiorna orchestrator (5 min)

```python
# booking_orchestrator.py riga 75:
# DA: result = self.state_machine.process(message, ctx)
# A:  result = self.state_machine.process_message(message)
```

### Fix 4 — COMPLETED → `should_exit=True` (30 min)

```python
# booking_state_machine.py — branch BookingState.COMPLETED:
elif state == BookingState.COMPLETED:
    return StateMachineResult(
        next_state=BookingState.COMPLETED,
        response="La chiamata è terminata. Arrivederci!",
        should_exit=True
    )
```

Risolve: 2 test (bug4 + related).

### Fix 5 — Aggiornare test ASKING_CLOSE_CONFIRMATION (1-2h)

Aggiornare i 5 test `test_booking_state_machine.py` per gestire il doppio step:
CONFIRMING → ASKING_CLOSE_CONFIRMATION → COMPLETED

Aggiungere helper:
```python
def confirm_and_close(sm: BookingStateMachine, confirm_msg="sì confermo", close_msg="sì grazie") -> StateMachineResult:
    sm.process_message(confirm_msg)   # → ASKING_CLOSE_CONFIRMATION
    return sm.process_message(close_msg)  # → COMPLETED
```

### Fix 6 — Skip/mock groq import (15 min)

```python
# In test_voice_agent_complete.py:
groq = pytest.importorskip('groq', reason="groq not installed")
```

---

## Ordine di esecuzione raccomandato

| # | Fix | File | Effort | Test risolti |
|---|-----|------|--------|--------------|
| 1 | Alias `session_id` in `log_turn()` | `analytics.py` | 15 min | 14 |
| 2 | Alias `process()` in BookingStateMachine | `booking_state_machine.py` | 15 min | 13+ |
| 3 | Fix `.process()` in orchestrator | `booking_orchestrator.py` | 5 min | (risolto da #2) |
| 4 | COMPLETED → `should_exit=True` | `booking_state_machine.py` | 30 min | 2 |
| 5 | Fix test ASKING_CLOSE_CONFIRMATION | `test_booking_state_machine.py` | 1-2h | 5 |
| 6 | Skip/mock groq import | test file | 15 min | 1 |
| **TOTALE** | | | **~3h** | **34+** |

---

## Acceptance Criteria MISURABILI

### Cluster A
- [ ] `test_booking_state_machine.py` → 0 FAIL (da 5 FAIL)
- [ ] `test_booking_e2e_complete.py` → 0 FAIL (da 10 FAIL)
- [ ] `test_cancel_reschedule.py::test_modificare_orario` → PASS
- [ ] `test_multi_verticale.py` → 0 FAIL (da 3 FAIL)
- [ ] `test_pipeline_e2e.py::test_full_booking_flow` → PASS
- [ ] `test_whatsapp.py::test_full_flow_with_mock_pipeline` → PASS

### Cluster B
- [ ] `TestTurnLogging` → 5/5 PASS (da 0/5)
- [ ] `TestFailedQueries` → 2/2 PASS (da 0/2)
- [ ] `TestConversationHistory` → 1/1 PASS (da 0/1)
- [ ] `TestAnalyticsMetrics` → 5/5 PASS + 0 ERROR (da 0/5 + 6 ERROR)
- [ ] `TestDailyMetrics` → 1/1 PASS (da 1 ERROR)

### Suite completa
- [ ] `pytest voice-agent/tests/ --ignore=voice-agent/tests/test_vad*.py -v` → 0 FAIL, 0 ERROR
- [ ] Nessuna regressione su 1064 test precedentemente PASS

---

*Fonte: voice-engineer agent — analisi codebase reale FLUXION 2026-03-04*
