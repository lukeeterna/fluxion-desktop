# Regex/NLU Legacy Code Usage Map

**Date**: 2026-03-17
**Purpose**: Map every public symbol from the 3 legacy NLU files to determine dead vs active code.

---

## Architecture Context

The orchestrator (`orchestrator.py`) now uses a **dual-path** architecture:
1. **PRIMARY**: LLM NLU (`nlu/llm_nlu.py`) — async task launched at turn start, awaited at L1
2. **FALLBACK**: Regex intent classifier (`intent_classifier.py`) — used when LLM NLU fails, times out, or returns confidence < 0.5

Entity extraction (`entity_extractor.py`) is **entirely independent** from intent classification and is used directly by `booking_state_machine.py` and `orchestrator.py` for slot filling. The LLM NLU does NOT replace entity extraction.

---

## File 1: `intent_classifier.py`

### Summary
The entire intent classification pipeline (exact match, pattern-based, semantic TF-IDF) is the **FALLBACK** path. When LLM NLU is available and confident, `classify_intent` is never called. When LLM NLU fails, `classify_intent` is called via `get_cached_intent()`.

| Symbol | Type | Status | Production Usage |
|--------|------|--------|-----------------|
| `IntentCategory` | Enum | **ACTIVE** | Used everywhere in orchestrator for category checks (PRENOTAZIONE, CANCELLAZIONE, etc.). Even LLM NLU results are converted to IntentCategory via `_nlu_to_intent_result()`. **Cannot be removed.** |
| `IntentResult` | Dataclass | **ACTIVE** | Return type used throughout orchestrator. LLM NLU results are converted to IntentResult. **Cannot be removed.** |
| `classify_intent()` | Function | **PARTIALLY DEAD** | Called via `get_cached_intent()` as fallback in 4 places in orchestrator (lines 983, 1251, 1686, 1764). When LLM NLU is working, only lines 1686 and 1764 (cancel/reschedule detection, FAQ layer) still use regex unconditionally. |
| `exact_match_intent()` | Function | **PARTIALLY DEAD** | Called directly in orchestrator line 379 for cortesia response text retrieval. Also called internally by `classify_intent()`. |
| `pattern_based_intent()` | Function | **PARTIALLY DEAD** | Only called internally by `classify_intent()`. Not called directly from production code. |
| `semantic_intent_classify()` | Function | **PARTIALLY DEAD** | Only called internally by `classify_intent()`. Not called directly from production code. |
| `normalize_input()` | Function | **ACTIVE** | Exported in `__init__.py`. Used internally. |
| `CORTESIA_EXACT` | Dict | **PARTIALLY DEAD** | Used by `exact_match_intent()` for cortesia responses. Still useful for response text lookup even when LLM classifies intent. |
| `INTENT_PATTERNS` | Dict | **PARTIALLY DEAD** | Used by `pattern_based_intent()` — fallback only. |
| `CORTESIA_ALIASES` | Dict | **PARTIALLY DEAD** | Used by `exact_match_intent()` — fallback only. |

### Consumers in Production
- `orchestrator.py` — imports `classify_intent`, `IntentCategory`, `IntentResult`, `exact_match_intent`
- `intent_lru_cache.py` — wraps `classify_intent` with LRU cache
- `pipeline.py` — imports `classify_intent`, `IntentCategory` (but pipeline.py itself appears **DEAD** — not imported anywhere)
- `__init__.py` — re-exports all public symbols

### Key Finding
`classify_intent` is a **hot fallback** — it runs on every turn where LLM NLU is unavailable or low-confidence. It is NOT safe to remove yet. However, the 4 call sites in orchestrator (lines 983, 1251, 1686, 1764) could all be migrated to use LLM NLU results when available, which would make `classify_intent` truly dead.

---

## File 2: `entity_extractor.py`

### Summary
Entity extraction is **FULLY ACTIVE** and NOT replaced by LLM NLU. The booking state machine calls these functions dozens of times per turn for slot filling.

| Symbol | Type | Status | Production Usage |
|--------|------|--------|-----------------|
| `extract_date()` | Function | **ACTIVE** | booking_state_machine.py (lines 2227, 2283, 2308, 2407, 2833), orchestrator.py (lines 3252, 3288, 3349, 3359), booking_orchestrator.py (line 168) |
| `extract_time()` | Function | **ACTIVE** | booking_state_machine.py (lines 2283, 2308, 2332, 2411, 2811), orchestrator.py (line 3322), booking_orchestrator.py (line 169) |
| `extract_name()` | Function | **ACTIVE** | booking_state_machine.py (lines 1341, 1913, 3023, 3075) |
| `extract_phone()` | Function | **ACTIVE** | booking_state_machine.py (lines 3249-3250, 3380-3381) |
| `extract_services()` | Function | **ACTIVE** | booking_state_machine.py (line 2071) |
| `extract_all()` | Function | **ACTIVE** | booking_state_machine.py (line 778) — called on every FSM turn |
| `extract_vertical_entities()` | Function | **ACTIVE** | orchestrator.py (line 787) — called for vertical guardrail |
| `extract_exclude_days()` | Function | **ACTIVE** | booking_state_machine.py (lines 2178-2185) |
| `extract_generic_operator()` | Function | **ACTIVE** | booking_state_machine.py (imported at top, used in operator extraction flow) |
| `_normalize_phone_whisper()` | Function | **ACTIVE** | booking_state_machine.py (lines 3261-3262) |
| `extract_time_constraint()` | Function | **ACTIVE** | booking_state_machine.py (imported at top, used for TimeConstraint-aware slot filling) |
| `extract_email()` | Function | **ACTIVE** | Exported in `__init__.py`, used in ExtractionResult |
| `extract_service()` | Function | **ACTIVE** | Exported in `__init__.py` (singular version) |
| `extract_operator()` | Function | **ACTIVE** | Used internally for operator name extraction |
| `extract_operators_multi()` | Function | **ACTIVE** | Used for multi-operator extraction |
| `select_operator_for_gender()` | Function | **ACTIVE** | Used for gender-based operator selection |
| `ExtractedDate` | Dataclass | **ACTIVE** | Used throughout booking_state_machine.py |
| `ExtractedTime` | Dataclass | **ACTIVE** | Used throughout booking_state_machine.py |
| `ExtractedName` | Dataclass | **ACTIVE** | Used in booking_state_machine.py |
| `ExtractionResult` | Dataclass | **ACTIVE** | Core data structure for every FSM handler signature |
| `TimeConstraint` | Dataclass | **ACTIVE** | Used in orchestrator.py (lines 1303-1357) and booking_state_machine.py |
| `TimeConstraintType` | Enum | **ACTIVE** | Used in orchestrator.py and booking_state_machine.py |
| `VerticalEntities` | Dataclass | **ACTIVE** | Used in orchestrator.py for vertical entity extraction |
| `NAME_BLACKLIST` | Set | **ACTIVE** | Used in entity_extractor.py internally (line 985 — local redefinition); also exists separately in `nlu/italian_nlu.py` |

### Key Finding
**entity_extractor.py is 100% active production code.** It cannot be removed or even partially deprecated without a complete rewrite of the booking state machine. The LLM NLU handles intent classification only — entity extraction remains regex-based.

---

## File 3: `nlu/italian_nlu.py`

### Summary
This is the **original** 4-layer NLU pipeline (regex + spaCy + UmBERTo + context). It is **almost entirely dead** — kept only for a single import in orchestrator.py.

| Symbol | Type | Status | Production Usage |
|--------|------|--------|-----------------|
| `ItalianVoiceAgentNLU` | Class | **DEAD** | Imported in orchestrator.py (line 167/170) and instantiated at line 475, BUT the instance (`self.advanced_nlu`) is never actually called in any production code path. It was the pre-LLM-NLU "advanced" pipeline that was superseded. |
| `NLUIntent` | Enum | **DEAD** | Imported in orchestrator.py (line 168/171) but only used in the `_nlu_to_intent_result()` adapter function for mapping — and that function now maps from `nlu.schemas.NLUIntent` (the LLM NLU version), not from `italian_nlu.NLUIntent`. |
| `NLUResult` | Dataclass | **DEAD** | Only used internally by `ItalianVoiceAgentNLU.process()` |
| `NLUEntity` | Dataclass | **DEAD** | Only used internally by spaCy extraction in italian_nlu.py |
| `ConversationContext` | Class | **DEAD** | Only used internally by `ItalianVoiceAgentNLU` |
| `_detect_implicit_intent()` | Function | **DEAD** | Internal to italian_nlu.py |
| `_extract_entities_spacy()` | Function | **DEAD** | Internal, requires spaCy (not installed on iMac) |
| `_classify_intent_umberto()` | Function | **DEAD** | Internal, requires transformers+torch (not on iMac, violates Python 3.9 rule) |
| `NAME_BLACKLIST` | Set | **DEAD** | Separate copy from entity_extractor.py's NAME_BLACKLIST; only used by spaCy extraction in italian_nlu.py |

### Key Finding
**italian_nlu.py is 100% dead code.** The `ItalianVoiceAgentNLU` class is instantiated but never called. Its dependencies (spaCy, transformers, torch) are not even installed on the production iMac. The `NLUIntent` import could be cleaned up since orchestrator now uses `nlu.schemas.NLUIntent` from the LLM NLU module. This entire file can be safely deleted.

---

## File 4: `pipeline.py` (bonus finding)

| Symbol | Status | Notes |
|--------|--------|-------|
| Entire file | **DEAD** | Imports `classify_intent` and `entity_extractor` functions, but `pipeline.py` itself is never imported by main.py, orchestrator.py, or any other production code. Only re-exported via `__init__.py` but never consumed. |

## File 5: `booking_orchestrator.py` (bonus finding)

| Symbol | Status | Notes |
|--------|--------|-------|
| Entire file | **DEAD** | Only imported by `tests/test_booking_e2e_complete.py`. Not used in production. Uses `extract_date` and `extract_time` from entity_extractor. |

---

## Summary Table

| File | Status | Safe to Delete? |
|------|--------|----------------|
| `intent_classifier.py` | **PARTIALLY DEAD** — fallback path still active | NO — still used as fallback when LLM NLU unavailable. `IntentCategory` and `IntentResult` are core types used everywhere. |
| `entity_extractor.py` | **FULLY ACTIVE** | NO — core production code, not replaced by LLM NLU |
| `nlu/italian_nlu.py` | **FULLY DEAD** | YES — can be deleted entirely. Remove import from orchestrator.py lines 167-171 and line 475. |
| `pipeline.py` | **FULLY DEAD** | YES — never imported in production |
| `booking_orchestrator.py` | **FULLY DEAD** | YES — only test imports |

---

## Recommended Cleanup Order

1. **Delete `nlu/italian_nlu.py`** — zero production impact, remove dead imports from orchestrator.py
2. **Delete `pipeline.py`** — zero production impact, remove from `__init__.py` if referenced
3. **Delete `booking_orchestrator.py`** — zero production impact, update/remove the one test that imports it
4. **Migrate orchestrator lines 1686, 1764** to use LLM NLU results instead of `get_cached_intent()` — these are the last 2 places where regex intent classification runs unconditionally even when LLM NLU is available
5. **Long-term**: Once LLM NLU is stable for 2+ weeks, `classify_intent()` and all of `intent_classifier.py` except `IntentCategory`/`IntentResult` can be removed. Extract those two types to a shared `types.py`.
6. **Never touch `entity_extractor.py`** — it is load-bearing production code independent of intent classification architecture.
