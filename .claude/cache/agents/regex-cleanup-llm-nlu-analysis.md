# LLM NLU Integration Analysis — Regex Cleanup Research
> Date: 2026-03-17 | Task: Research only (no code changes)

## Q1: Where exactly in the 5-layer pipeline does LLM NLU get called?

The LLM NLU is called in **two places**, both inside `orchestrator.py process()`:

### Fire point (line 711):
At the **very start** of `process()`, before any layer runs, an async task is created:
```python
_llm_nlu_task = asyncio.create_task(self._llm_nlu.extract(...))
```
This fires in parallel with L0 processing, buying ~50-100ms of latency.

### Await point 1 — L1 (line 960-974):
After L0 (content filter, escalation, guardrail, sentiment) completes with `response is None`, the LLM NLU task is awaited with a **2-second timeout**:
```python
_llm_nlu_result = await asyncio.wait_for(_llm_nlu_task, timeout=2.0)
```
If confidence >= 0.5, result is converted via `_nlu_to_intent_result()` to an `IntentResult` (the legacy format). Otherwise, falls back to `get_cached_intent()` (regex).

### Await point 2 — L2 entry (line 1248):
At the top of L2 (Booking State Machine), the same `_llm_nlu_result` is **reused** (not re-awaited) if available:
```python
if _llm_nlu_result and _llm_nlu_result.confidence >= 0.5:
    intent_result = _nlu_to_intent_result(_llm_nlu_result, user_input)
else:
    intent_result = get_cached_intent(user_input)  # regex fallback
```

### NOT used at L1686 and L1764:
Lines 1686 and 1764 (cancel/reschedule flow at end of L2, and L3 FAQ) **always** use `get_cached_intent()` — they do NOT use the LLM NLU result. This is a gap: these late-pipeline paths ignore the LLM entirely.

### Cleanup at end (line 1995):
Unconsumed LLM NLU tasks are cancelled at the end of `process()`.

---

## Q2: What does LLM NLU output?

`NLUResult` (from `schemas.py`) contains:

| Field | Type | Description |
|-------|------|-------------|
| `intent` | `SaraIntent` enum | 13 values: PRENOTAZIONE, CANCELLAZIONE, SPOSTAMENTO, WAITLIST, CONFERMA, RIFIUTO, CORREZIONE, CORTESIA, CHIUSURA, ESCALATION, FAQ, OSCENITA, ALTRO |
| `entities` | `NLUEntities` | nome, cognome, servizio, data (YYYY-MM-DD), ora (HH:MM), operatore, telefono |
| `sentiment` | `Sentiment` enum | POSITIVO, NEUTRO, FRUSTRATO, AGGRESSIVO |
| `correction_field` | `Optional[str]` | Which field user wants to correct (for CORREZIONE intent) |
| `confidence` | `float` | 0.0-1.0 |
| `provider` | `str` | Which LLM provider answered (groq, cerebras, openrouter) |
| `latency_ms` | `float` | Round-trip time |
| `raw_text` | `str` | Original input |

**Key finding**: LLM NLU extracts **both intent AND entities**, but the `_nlu_to_intent_result()` adapter **DISCARDS all entities**. It only maps `SaraIntent` -> `IntentCategory` and gets a response text from `exact_match_intent()`. The entity extraction from the LLM is completely unused by L2 (booking state machine).

The booking state machine (`booking_state_machine.py`) does its own entity extraction via `entity_extractor.py` functions (`extract_date`, `extract_time`, `extract_name`, etc.) on every `process_message()` call.

---

## Q3: What from `intent_classifier.py` is now redundant vs still needed?

### REDUNDANT (replaced by LLM NLU):
- `classify_intent()` — the main classification function. LLM NLU does this better (handles negation, context, STT errors). Currently kept as fallback when LLM conf < 0.5 or timeout.
- All regex patterns for intent matching inside `classify_intent()`.

### STILL NEEDED:
- **`exact_match_intent()`** (line 276) — Used by `_nlu_to_intent_result()` to get **response text** for CORTESIA/CONFERMA/RIFIUTO/OPERATORE intents. The LLM NLU produces intents but NOT response text. Example: "Buongiorno" -> LLM says `CORTESIA` -> `exact_match_intent("Buongiorno")` returns the canned response "Buongiorno! Come posso aiutarla?"
- **`IntentCategory` enum** — Used everywhere in the pipeline for routing logic.
- **`IntentResult` dataclass** — The universal format consumed by L1-L4 layers.
- **`get_cached_intent()` / `classify_intent()`** — Still the fallback at 4 call sites:
  1. Line 983: L1 fallback when LLM conf < 0.5
  2. Line 1251: L2 entry fallback
  3. Line 1686: Cancel/reschedule flow (always regex, never LLM)
  4. Line 1764: L3 FAQ routing (always regex, never LLM)

### Verdict: `intent_classifier.py` cannot be removed yet.
- `exact_match_intent()` is actively needed for response text generation.
- `classify_intent()` is the fallback path and also the primary path at lines 1686/1764.
- `IntentCategory` and `IntentResult` are the universal interface.

---

## Q4: What from `entity_extractor.py` is now redundant vs still needed?

### STILL NEEDED (heavily used by booking_state_machine.py):
- `extract_date()` — called in BSM for date slot filling + orchestrator lines 3252, 3288
- `extract_time()` — called in BSM for time slot filling + orchestrator line 3288
- `extract_name()` — called in BSM for client name extraction + line 3023
- `extract_service()` / `extract_services()` — called in BSM
- `extract_operator()` — called in BSM
- `extract_all()` — called in BSM
- `ExtractionResult` — dataclass used by BSM
- `TimeConstraint` / `TimeConstraintType` — used in orchestrator lines 1303-1328
- `extract_time_constraint()` — called in BSM
- `extract_phone()` — called in BSM lines 3249, 3380
- `extract_vertical_entities()` — called in orchestrator L0-PRE (line 787)
- `extract_exclude_days()` — called in BSM line 2178

### REDUNDANT (duplicated by LLM NLU but NOT actually wired):
- **In theory**: all entity extraction is duplicated by LLM NLU's `NLUEntities` output. But since the adapter `_nlu_to_intent_result()` discards entities, and BSM does its own extraction, **nothing is actually redundant in practice**.

### Verdict: `entity_extractor.py` CANNOT be removed.
The entire booking state machine depends on it for slot filling. The LLM NLU extracts entities but they're thrown away at the adapter layer. To make entities redundant, the BSM would need to be rewritten to consume `NLUEntities` instead of calling `extract_*()` functions — a major refactor.

---

## Q5: What from `italian_regex.py` is still used for non-NLU purposes?

These functions from `italian_regex.py` are **not intent classification** and are still actively used:

| Function | Used At | Purpose | Replaceable by LLM? |
|----------|---------|---------|---------------------|
| `prefilter()` | orch L734-769 | Content filter (SEVERE/MODERATE/MILD) + escalation detection | Partially (profanity is in template_fallback too, but severity levels are regex-only) |
| `ContentSeverity` | orch L742-756 | Enum for content severity levels | No — structural |
| `check_vertical_guardrail()` | orch L775 | Block out-of-vertical requests ("cambio olio" at salon) | LLM could do this but currently doesn't |
| `is_time_pressure()` | orch L736 | Detect "ho fretta" / "veloce" → concise LLM responses | LLM could extract this as entity but currently doesn't |
| `strip_fillers()` | BSM line 67 | Remove "ehm", "allora", "dunque" from input before entity extraction | Preprocessing — LLM handles natively but BSM still needs clean text for regex extraction |
| `is_ambiguous_date()` | BSM line 67 | Detect "martedi" without specifying which week | Preprocessing — not NLU |
| `extract_multi_services()` | BSM line 67 | "taglio e barba" → ["taglio", "barba"] | LLM returns single `servizio` string, not parsed list |
| `VERTICAL_SERVICES` | orch L438, L718, L2334 | Service catalog per vertical (used as LLM context AND BSM config) | Data dictionary — never replaceable |
| `is_flexible_scheduling()` | BSM line 67 | Detect "quando volete" / "qualsiasi orario" | LLM could but not wired |
| `is_rifiuto()` | BSM line 67 | Detect refusal patterns in BSM context | LLM intent=RIFIUTO, but BSM uses this inline |
| `get_service_synonyms()` | orch L80 (imported but usage unclear) | Map service synonyms | Data dictionary |

### Verdict: `italian_regex.py` CANNOT be removed.
It provides 3 categories of functionality that LLM NLU does not replace:
1. **Content filtering** with severity levels (L0 security layer)
2. **Preprocessing** functions (filler stripping, ambiguous date detection)
3. **Data dictionaries** (VERTICAL_SERVICES, service synonyms)

---

## Q6: How does the fallback work when LLM NLU fails?

### 3-level fallback cascade:

**Level A — Inside `LLMNlu.extract()` (llm_nlu.py):**
1. **Fast path** (line 138): Single-word inputs ("si", "no", "ok", "grazie") return instantly with confidence 0.99, provider="fast_path". No LLM call.
2. **Profanity filter** (line 126): Detected before LLM call, returns OSCENITA with 0.99 confidence.
3. **LLM call fails** → falls to **template_fallback** (line 167-183): Uses rapidfuzz fuzzy matching against ~180 Italian templates. Returns intent with confidence = fuzzy score / 100.

**Level B — Inside `orchestrator.py process()` (line 960-988):**
1. LLM NLU task awaited with **2s timeout**. If `TimeoutError` → `_llm_nlu_result` stays None.
2. If `_llm_nlu_result is None` OR `confidence < 0.5` → falls to `get_cached_intent()` which calls `classify_intent()` from `intent_classifier.py` (the legacy regex classifier).

**Level C — Late pipeline paths (lines 1686, 1764):**
Cancel/reschedule flow and L3 FAQ routing **always** use `get_cached_intent()` regardless of LLM NLU result. These paths never benefit from LLM NLU.

### Confidence threshold: 0.5
- LLM providers typically return 0.8-1.0 for clear intents
- The 0.5 threshold is generous — anything below indicates LLM confusion or garbage output
- Template fallback rarely exceeds 0.85 (fuzzy match ceiling)

### Provider rotation (in `providers.py`):
Groq -> Cerebras -> OpenRouter x3. If all 5 providers fail, `_call_llm()` returns None, triggering template_fallback inside `LLMNlu.extract()`. If even template_fallback returns ALTRO with 0.0, the orchestrator falls to regex via `get_cached_intent()`.

---

## Summary: What Can Be Cleaned Up

### Safe to remove NOW:
- Nothing. All legacy components are actively used as fallbacks or for non-NLU purposes.

### Could be removed with targeted refactoring:

1. **Wire LLM NLU entities to BSM** → Would make half of `entity_extractor.py` functions redundant for the happy path (LLM available). But BSM would still need regex extraction as fallback.

2. **Use `_llm_nlu_result` at lines 1686/1764** → Currently these late-pipeline cancel/reschedule/FAQ paths ignore LLM NLU entirely. Easy fix: check `_llm_nlu_result` before falling to regex.

3. **Move content filter severity into LLM NLU** → Would allow removing `prefilter()` from `italian_regex.py`, but adds latency to a security-critical path (content filtering should be <1ms, not 150ms).

### Architecture debt:
The biggest issue is the **adapter layer** (`_nlu_to_intent_result`) which converts the rich `NLUResult` (intent + entities + sentiment) into the impoverished `IntentResult` (intent + category + response). This forces double work: LLM extracts entities, then BSM re-extracts them with regex. Fixing this requires BSM to accept `NLUEntities` as pre-extracted slots — a significant but high-value refactor.
