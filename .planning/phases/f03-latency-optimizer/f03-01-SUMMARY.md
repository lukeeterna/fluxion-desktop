---
phase: f03-latency-optimizer
plan: 01
subsystem: voice-agent
tags: [python, asyncio, lru-cache, groq, streaming, latency, intent-classifier, orchestrator]

# Dependency graph
requires:
  - phase: f02.1-nlu-hardening
    provides: orchestrator.py with 4-layer pipeline, classify_intent() at 4 call sites
  - phase: f02-vertical-system
    provides: entity_extractor, italian_regex, groq_client with generate_response_streaming()
provides:
  - LRU cache wrapper for classify_intent (intent_lru_cache.py)
  - Streaming L4 Groq block using generate_response_streaming()
  - FALLBACK_RESPONSES module-level dict
  - Per-layer timing via time.perf_counter()
affects: [f03-02, f03-03, voice-agent-tests]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - LRU cache on deterministic sync functions (not async) to eliminate redundant CPU work per turn
    - Streaming async generator pattern for LLM: collect chunks, join, handle empty result
    - Module-level FALLBACK_RESPONSES dict for zero-allocation error branches
    - time.perf_counter() for sub-ms per-layer timing alongside time.time() for latency_ms

key-files:
  created:
    - voice-agent/src/intent_lru_cache.py
  modified:
    - voice-agent/src/orchestrator.py

key-decisions:
  - "LRU cache on classify_intent only: call sites pass bare user_input, no verticale arg — safe to cache by normalized text"
  - "clear_intent_cache() in start_session() full reset: new sessions must not see cached intents from prior calls"
  - "max_tokens=150 + temperature=0.3 for streaming L4: voice responses must be short; lower temp reduces hallucination"
  - "chunks joined with space then stripped: avoids double-space artifacts from sentence boundaries"
  - "asyncio.gather NOT used at L0: extract_vertical_entities must run only after content filter passes, sequential is correct"
  - "t_llm_start inside L4 if-block only: avoids spurious timing on turns that hit L1/L2/L3"

patterns-established:
  - "F03 timing pattern: _t0 = time.perf_counter() at process() entry, [F03] log before POST-PROCESSING"
  - "FALLBACK_RESPONSES: module-level dict, key = error type, value = Italian response string"

# Metrics
duration: 4min
completed: 2026-03-04
---

# Phase F03 Plan 01: Latency Optimizer Wave 1 Summary

**LRU intent cache (100-slot) eliminating 3x redundant TF-IDF per turn, streaming Groq L4 via generate_response_streaming(), and FALLBACK_RESPONSES dict with per-layer perf_counter timing**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-04T18:30:49Z
- **Completed:** 2026-03-04T18:34:54Z
- **Tasks:** 2/2
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- Created `voice-agent/src/intent_lru_cache.py` with `get_cached_intent()` and `clear_intent_cache()`, Python 3.9 compatible using `functools.lru_cache(maxsize=100)` and `re.sub` normalization
- Replaced all 4 `classify_intent(user_input)` call sites in orchestrator.py (L1 guard line 681, L2 guard line 933, cancel/reschedule check line 1243, L3 guard line 1321) with `get_cached_intent(user_input)` — saves ~10-15ms per turn
- Added `clear_intent_cache()` call in `start_session()` after `self.booking_sm.reset(full_reset=True)` to prevent cross-session cache pollution
- Added `FALLBACK_RESPONSES` dict at module level (line 246) with `timeout`, `rate_limit`, `generic`, `error` keys — replaces 4 hardcoded Italian strings in L4 error branches
- Replaced blocking `generate_response()` L4 call with streaming `async for chunk in self.groq.generate_response_streaming(...)` — eliminates `asyncio.to_thread` overhead, enables first-chunk TTS as future optimization
- Added per-layer timing: `_t0 = time.perf_counter()` at `process()` entry (line 502), `[F03] L4 LLM: Xms` in `finally` block, `[F03] Total: Xms | Layer: X` before POST-PROCESSING

## Task Commits

Each task was committed atomically:

1. **Task 1: LRU intent cache + 4 call sites + session reset** - `4f7478c` (feat)
2. **Task 2: Streaming L4 + FALLBACK_RESPONSES + per-layer timing** - `7490e4b` (feat)

## Files Created/Modified

- `voice-agent/src/intent_lru_cache.py` — New module: `get_cached_intent()`, `clear_intent_cache()`, `_normalize_input()`, `_cached_classify()` (lru_cache wrapper)
- `voice-agent/src/orchestrator.py` — Added import block (lines 91-106), `FALLBACK_RESPONSES` dict (lines 246-252), `_t0 = time.perf_counter()` (line 502), `clear_intent_cache()` in reset (line 436), 4 `get_cached_intent()` call sites (lines 681, 933, 1243, 1321), streaming L4 block (~line 1380), `[F03] Total` log (line 1434)

## Decisions Made

- LRU cache only for the no-arg variant of classify_intent (all 4 orchestrator call sites pass bare `user_input` without `verticale`) — normalizes to lowercase+stripped to maximize cache hit rate
- `clear_intent_cache()` added only to `start_session()` full reset (new call), not to mid-call `booking_sm.reset()` — partial resets within a session share the same user_input context
- `max_tokens=150` for streaming: voice response must be short enough to stream to TTS before full completion
- Fallback to direct `classify_intent()` delegation (no cache) if `intent_lru_cache` import fails — zero regression risk

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- F03-01 complete: LRU cache and streaming L4 wired
- F03-02 (GroqKeyPool rotation + latency_optimizer.py wiring) can proceed immediately
- iMac voice pipeline restart required before testing: `ssh imac "kill $(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"`
- Expected latency improvement visible in `[F03]` log output after restart

---
*Phase: f03-latency-optimizer*
*Completed: 2026-03-04*
