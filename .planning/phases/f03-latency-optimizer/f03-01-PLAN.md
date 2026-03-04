---
phase: f03-latency-optimizer
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/orchestrator.py
  - voice-agent/src/intent_lru_cache.py
autonomous: true

must_haves:
  truths:
    - "L4 block uses generate_response_streaming() instead of generate_response()"
    - "FALLBACK_RESPONSES dict defined at module level in orchestrator.py with 'timeout' and 'generic' keys"
    - "classify_intent() called once at top of each L1/L2/L2.5/L3 guard block, result reused"
    - "asyncio.gather() used to run prefilter and extract_vertical_entities in parallel at L0 boundary"
    - "LRU cache (100 slots) wired for intent classification via get_cached_intent()"
    - "Per-layer timing timestamps (t_start, t_nlu, t_llm) stored in orchestrator.process()"
  artifacts:
    - path: "voice-agent/src/intent_lru_cache.py"
      provides: "LRU cache wrapper for classify_intent, Python 3.9 compatible"
      exports: ["get_cached_intent", "clear_intent_cache"]
    - path: "voice-agent/src/orchestrator.py"
      provides: "Updated L4 block with streaming, FALLBACK_RESPONSES, LRU cache, asyncio.gather"
      contains: "generate_response_streaming"
  key_links:
    - from: "voice-agent/src/orchestrator.py L4 block (~line 1355)"
      to: "voice-agent/src/groq_client.py generate_response_streaming()"
      via: "async for chunk in self.groq.generate_response_streaming(...)"
      pattern: "generate_response_streaming"
    - from: "voice-agent/src/orchestrator.py L1 guard (~line 665)"
      to: "voice-agent/src/intent_lru_cache.py"
      via: "intent_result = get_cached_intent(user_input)"
      pattern: "get_cached_intent"
    - from: "voice-agent/src/orchestrator.py L0 boundary (~line 563)"
      to: "asyncio.gather"
      via: "await asyncio.gather(asyncio.to_thread(...), asyncio.to_thread(...))"
      pattern: "asyncio.gather"
---

<objective>
Wire the already-written streaming LLM path into the L4 fallback, add a FALLBACK_RESPONSES dict for timeout resilience, eliminate the 3x classify_intent() redundancy with an LRU cache, and parallelize prefilter+entity extraction at the L0 boundary.

Purpose: These four changes address the three largest latency contributors: L4 blocking LLM call (~50-100ms asyncio.to_thread overhead eliminated by streaming), redundant intent classification (~10-15ms saved per turn), and sequential pre-filter+entity extraction (~30-50ms saved by parallelization).
Output: orchestrator.py with streaming L4, LRU-cached intent, parallel L0 extraction; new intent_lru_cache.py module.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/f03-latency-optimizer/f03-RESEARCH.md

# Key source files (read before implementing)
@voice-agent/src/orchestrator.py
@voice-agent/src/groq_client.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create src/intent_lru_cache.py and wire LRU cache at all 4 classify_intent call sites</name>
  <files>voice-agent/src/intent_lru_cache.py, voice-agent/src/orchestrator.py</files>
  <action>
**Step 1 — Create voice-agent/src/intent_lru_cache.py (new file):**

```python
"""
Intent LRU Cache — Fluxion F03 Latency Optimizer
=================================================
Wraps classify_intent with a 100-slot LRU cache keyed on normalized input.
classify_intent is called 4 times per orchestrator.process() turn on the same
string — this eliminates 3 redundant TF-IDF + regex scans per turn (~10-15ms).

Python 3.9 compatible: uses Optional[], List[], Dict[] from typing.
lru_cache is thread-safe in CPython (GIL protects dict ops between await points).
"""
import re
from functools import lru_cache
from typing import Any

try:
    from .intent_classifier import classify_intent
except ImportError:
    from intent_classifier import classify_intent


def _normalize_input(text: str) -> str:
    """Normalize for cache key: strip + lowercase + collapse whitespace."""
    return re.sub(r'\s+', ' ', text.strip().lower())


@lru_cache(maxsize=100)
def _cached_classify(normalized: str) -> Any:
    """
    Cached classify_intent on normalized input.
    NOTE: lru_cache requires hashable args — str is hashable.
    NOTE: Do NOT use lru_cache on async functions.
    """
    return classify_intent(normalized)


def get_cached_intent(user_input: str) -> Any:
    """
    Public API: classify_intent with 100-slot LRU cache.
    Returns IntentResult. Caches by normalized form of user_input.
    """
    return _cached_classify(_normalize_input(user_input))


def clear_intent_cache() -> None:
    """
    Clear cache on session reset to avoid cross-session pollution.
    Call from orchestrator reset() method.
    """
    _cached_classify.cache_clear()
```

**Step 2 — Update voice-agent/src/orchestrator.py imports (top of file, after existing imports):**

Add after the `from .intent_classifier import classify_intent` import block (around line 48-58). The existing try/except import block already handles both relative and absolute imports. Add a similar pattern:

```python
# F03: Intent LRU cache (100-slot, eliminates 3x classify_intent per turn)
try:
    from .intent_lru_cache import get_cached_intent, clear_intent_cache
    HAS_INTENT_CACHE = True
except ImportError:
    def get_cached_intent(user_input):
        return classify_intent(user_input)
    def clear_intent_cache():
        pass
    HAS_INTENT_CACHE = False
```

**Step 3 — Replace the 4 classify_intent() call sites in orchestrator.py with get_cached_intent():**

- Line 666: `intent_result = classify_intent(user_input)` → `intent_result = get_cached_intent(user_input)`
- Line 918: `intent_result = classify_intent(user_input)` → `intent_result = get_cached_intent(user_input)`
- Line 1228: `intent_result = classify_intent(user_input)` → `intent_result = get_cached_intent(user_input)`
- Line 1306: `intent_result = classify_intent(user_input)` → `intent_result = get_cached_intent(user_input)`

**Step 4 — Add clear_intent_cache() call in the session reset path:**

Find where `self.booking_sm.reset()` is called (around line 592-598 in the special_result "reset" action handler). Add `clear_intent_cache()` immediately after `self.booking_sm.reset()`.

**Constraints:**
- Python 3.9 — no walrus operator, no `X | Y` union syntax, no `match` statement
- The existing `classify_intent` import must remain (used in fallback and type references)
- Use `get_cached_intent` only where the same `user_input` string is passed (all 4 call sites use the same `user_input` variable from `process()`)
  </action>
  <verify>grep -n "get_cached_intent\|clear_intent_cache" /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/src/orchestrator.py | wc -l  # should be at least 5 (4 replacements + 1 import)</verify>
  <done>intent_lru_cache.py exists; orchestrator.py has 4 get_cached_intent() call sites and clear_intent_cache() called on reset; grep confirms no remaining raw classify_intent() calls at those 4 line numbers</done>
</task>

<task type="auto">
  <name>Task 2: Wire streaming L4, add FALLBACK_RESPONSES, parallelize L0 with asyncio.gather, add per-layer timing</name>
  <files>voice-agent/src/orchestrator.py</files>
  <action>
All changes in voice-agent/src/orchestrator.py. Read the file carefully before editing.

**Step 1 — Add FALLBACK_RESPONSES module-level dict (add after existing module-level constants, before the class definition):**

```python
# F03: Canned fallback responses for Groq timeout/unavailability
# Pre-warm these in main.py startup to eliminate TTS latency for these phrases
FALLBACK_RESPONSES = {
    "timeout": "Mi scusi, sto impiegando un po' di tempo. Posso aiutarla a prenotare un appuntamento?",
    "rate_limit": "Mi scusi, sono momentaneamente sovraccarica. Puo ripetere?",
    "generic": "Posso aiutarla principalmente con le prenotazioni. Desidera fissare un appuntamento?",
    "error": "Mi scusi, ho avuto un problema tecnico. Puo ripetere?",
}
```

**Step 2 — Replace the L4 block (lines ~1355-1391) with streaming version:**

Replace the entire `if response is None:` L4 block with:

```python
        # =====================================================================
        # LAYER 4: Groq LLM Fallback (F03: streaming — eliminates asyncio.to_thread overhead)
        # =====================================================================
        if response is None:
            t_llm_start = time.perf_counter()
            try:
                context = self._build_llm_context()
                chunks = []
                async for chunk in self.groq.generate_response_streaming(
                    messages=[{"role": "user", "content": user_input}],
                    system_prompt=context,
                    max_tokens=150,
                    temperature=0.3
                ):
                    chunks.append(chunk["text"])
                response = " ".join(chunks).strip() if chunks else None
                if not response:
                    response = FALLBACK_RESPONSES["generic"]
                intent = "groq_response"
                layer = ProcessingLayer.L4_GROQ
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError as e:
                print(f"[Groq] Timeout LLM: {e}")
                response = FALLBACK_RESPONSES["timeout"]
                intent = "error_fallback"
                layer = ProcessingLayer.L4_GROQ
            except RuntimeError as e:
                err_str = str(e).lower()
                if "rate" in err_str or "429" in err_str or "503" in err_str:
                    print(f"[Groq] Rate limit: {e}")
                    response = FALLBACK_RESPONSES["rate_limit"]
                elif "timeout" in err_str:
                    print(f"[Groq] Timeout: {e}")
                    response = FALLBACK_RESPONSES["timeout"]
                else:
                    print(f"[Groq] LLM error: {e}")
                    response = FALLBACK_RESPONSES["error"]
                intent = "error_fallback"
                layer = ProcessingLayer.L4_GROQ
            except Exception as e:
                print(f"[Groq] Unexpected error: {e}")
                response = FALLBACK_RESPONSES["error"]
                intent = "error_fallback"
                layer = ProcessingLayer.L4_GROQ
            finally:
                _t_llm_ms = (time.perf_counter() - t_llm_start) * 1000
                print(f"[F03] L4 LLM: {_t_llm_ms:.0f}ms")
```

**Step 3 — Parallelize prefilter + extract_vertical_entities at L0 boundary:**

Find the L0 vertical entity extraction block (~lines 551-576). The current structure is:
```
if response is None and HAS_ITALIAN_REGEX:
    pre = prefilter(user_input)   # line 516, ALREADY runs before guardrail
    ...
if response is None and HAS_ITALIAN_REGEX and HAS_VERTICAL_ENTITIES:
    _vert_entities = extract_vertical_entities(user_input, self.verticale_id)
```

The prefilter runs at line 516 (unconditional once HAS_ITALIAN_REGEX). Extract_vertical_entities runs separately at line 563-576.

Replace the sequential `prefilter` call (line 516) and `extract_vertical_entities` call (lines 563-564) with a parallel gather block. At line 515 (the `if HAS_ITALIAN_REGEX:` block), replace:

```python
        if HAS_ITALIAN_REGEX:
            pre = prefilter(user_input)
```

with:

```python
        if HAS_ITALIAN_REGEX:
            # F03: Run prefilter + vertical entity extraction in parallel
            # Both are pure sync CPU functions — safe for asyncio.to_thread
            if HAS_VERTICAL_ENTITIES:
                pre, _vert_entities = await asyncio.gather(
                    asyncio.to_thread(prefilter, user_input),
                    asyncio.to_thread(extract_vertical_entities, user_input, self.verticale_id)
                )
            else:
                pre = await asyncio.to_thread(prefilter, user_input)
                _vert_entities = None
```

Then remove the separate `extract_vertical_entities` call block at lines 563-576 (it is now handled above). Replace it with just the entity storage logic (the `if not hasattr(...)` block), guarded by `if response is None and HAS_VERTICAL_ENTITIES and _vert_entities is not None:`.

**Step 4 — Add per-layer timing at process() start:**

After `start_time = time.time()` (line 477), add:
```python
        # F03: Per-layer timing (perf_counter for sub-ms accuracy)
        _t0 = time.perf_counter()
```

After the L1/L2 processing and before POST-PROCESSING section, add:
```python
        # F03: Log layer timing
        _total_ms = (time.perf_counter() - _t0) * 1000
        print(f"[F03] Total: {_total_ms:.0f}ms | Layer: {layer.value}")
```

**Constraints:**
- Do NOT remove the existing `except asyncio.CancelledError: raise` — it must remain as-is
- Do NOT change `max_tokens` default above 150 — voice responses must be short
- Do NOT call `asyncio.gather` on booking_state_machine.process() — FSM mutates shared state
- `asyncio.to_thread` is Python 3.9+ — confirmed valid for iMac runtime
- Keep the existing `start_time = time.time()` for the main latency_ms calculation — the new `_t0` is additive for logging only
  </action>
  <verify>grep -n "generate_response_streaming\|FALLBACK_RESPONSES\|asyncio.gather\|asyncio.to_thread" /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/src/orchestrator.py | head -20</verify>
  <done>orchestrator.py contains: FALLBACK_RESPONSES dict at module level, generate_response_streaming in L4 block, asyncio.gather at L0 boundary, per-layer print statements; generate_response() (non-streaming) no longer called from process()</done>
</task>

</tasks>

<verification>
After implementing both tasks, run on iMac (execute after git push):

```bash
# 1. Syntax check (Python 3.9 on iMac)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -c 'import src.orchestrator; import src.intent_lru_cache; print(\"OK\")'"

# 2. Quick import smoke test
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -c 'from src.intent_lru_cache import get_cached_intent, clear_intent_cache; r = get_cached_intent(\"buongiorno voglio prenotare\"); print(r.category)'"
```
</verification>

<success_criteria>
- intent_lru_cache.py exists with get_cached_intent() and clear_intent_cache()
- orchestrator.py: 4 classify_intent() call sites replaced with get_cached_intent()
- orchestrator.py: FALLBACK_RESPONSES dict at module level
- orchestrator.py: L4 block uses generate_response_streaming() with max_tokens=150
- orchestrator.py: asyncio.gather() used at L0 for prefilter + extract_vertical_entities
- Python syntax valid on Python 3.9 (no walrus, no X|Y union, no match)
</success_criteria>

<output>
After completion, create `.planning/phases/f03-latency-optimizer/f03-01-SUMMARY.md` with:
- What was changed and in which files (exact line numbers where possible)
- Any decisions made during implementation
- Any deviations from the plan and why
</output>
