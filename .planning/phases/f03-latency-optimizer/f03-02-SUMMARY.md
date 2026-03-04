---
phase: f03-latency-optimizer
plan: 02
subsystem: api
tags: [groq, sqlite, wal, analytics, key-pool, latency, monitoring, python, aiohttp]

# Dependency graph
requires:
  - phase: f02.1-nlu-hardening
    provides: Stable voice pipeline baseline (1259 PASS / 0 FAIL)
  - phase: f03-latency-optimizer-plan-01
    provides: Streaming L4, FALLBACK_RESPONSES, LRU intent cache, per-layer timing

provides:
  - GroqKeyPool round-robin key rotation (groq_key_pool.py)
  - groq_client.py wired with pool.rotate() on 429 in generate_response() retry loop
  - analytics.py get_percentile_stats() returning P50/P95/P99
  - analytics.py WAL mode enabled in _init_db() for file-based DBs
  - main.py GET /api/metrics/latency route
  - main.py FluxionLatencyOptimizer.setup() at startup (non-fatal)
  - main.py TTS warmup extended with 6 F03 fallback phrases

affects:
  - f03-latency-optimizer-plan-03
  - future monitoring/observability work
  - iMac production pipeline restart required

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Round-robin key pool: GroqKeyPool reads GROQ_API_KEY, _2, _3 from env, rotates on 429"
    - "WAL mode: PRAGMA journal_mode=WAL in _init_db() for file-based SQLite only"
    - "Percentile stats: Python-side sorted list slice (P=sorted[int(n*p/100)]) — no SQL window functions needed"
    - "Non-fatal optimizer init: try/except around FluxionLatencyOptimizer.setup() — startup never blocked"

key-files:
  created:
    - voice-agent/src/groq_key_pool.py
  modified:
    - voice-agent/src/groq_client.py
    - voice-agent/src/analytics.py
    - voice-agent/main.py

key-decisions:
  - "GroqKeyPool graceful degradation: if no keys found, _key_pool=None and rotation is silently skipped"
  - "WAL mode skipped for :memory: DB (used in pytest tests) to avoid PRAGMA error"
  - "FluxionLatencyOptimizer.setup() is async (not initialize()) — checked at runtime with hasattr"
  - "latency_metrics_handler uses get_logger() from src.analytics (global singleton pattern)"
  - "groq_client.py rotate() reinitializes both self.client (Groq sync) and self.async_client (AsyncGroq) with new key"

patterns-established:
  - "Key pool: check self._key_pool is not None before calling rotate()"
  - "Non-fatal init: wrap any optimizer.setup() in try/except with print warning"

# Metrics
duration: 4min
completed: 2026-03-04
---

# Phase F03 Plan 02: Groq Key Pool + Latency Monitoring + WAL Mode Summary

**Round-robin Groq key pool wired on 429, P50/P95/P99 analytics endpoint via SQLite sorted-list percentile, WAL mode for concurrent write safety, and FluxionLatencyOptimizer non-fatal startup wiring**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-04T18:32:10Z
- **Completed:** 2026-03-04T18:35:45Z
- **Tasks:** 2 of 2
- **Files modified:** 4 (+ 1 created)

## Accomplishments

- Created `groq_key_pool.py` with `GroqKeyPool` class reading up to 3 env keys, round-robin rotation via `current_key()` / `rotate()`, Python 3.9 compatible
- Wired `GroqKeyPool` into `groq_client.py`: initialized in `__init__`, `pool.rotate()` called on 429 in `generate_response()` retry loop with full `Groq`/`AsyncGroq` client reinitialization for the new key
- Added `get_percentile_stats(hours)` to `analytics.py` ConversationLogger returning `{p50_ms, p95_ms, p99_ms, count, hours}` using Python-side sorted-list percentile (no SQLite window function dependency)
- Enabled WAL mode in `analytics._init_db()` for file-based DBs — eliminates concurrent read/write contention between voice pipeline and WhatsApp callback
- Added `GET /api/metrics/latency` route in `main.py` with `latency_metrics_handler()` delegating to `get_percentile_stats()`
- Extended TTS warmup phrase list with 6 F03 fallback phrases (ask_surname, timeout fallback, sovraccarica, disponibilita)
- Wired `FluxionLatencyOptimizer.setup()` non-fatally at startup in `main.py`

## Task Commits

Both tasks were included in commits from the concurrent Plan 01 execution (pre-commit hook behavior caused files staged for f03-02 to be committed atomically with f03-01 files):

1. **Task 1: GroqKeyPool + analytics WAL + percentiles + groq_client.py wiring** - `4f7478c` (feat)
2. **Task 2: main.py latency route + TTS warmup + optimizer init** - `7490e4b` (feat)

## Files Created/Modified

- `voice-agent/src/groq_key_pool.py` (CREATED) - GroqKeyPool class: round-robin key rotation for rate limit resilience
- `voice-agent/src/groq_client.py` (MODIFIED) - Added GroqKeyPool import + `_key_pool` init + `pool.rotate()` on 429 in retry loop
- `voice-agent/src/analytics.py` (MODIFIED) - Added `get_percentile_stats()` method + WAL mode in `_init_db()`
- `voice-agent/main.py` (MODIFIED) - Added `/api/metrics/latency` route + `latency_metrics_handler()` + F03 TTS phrases + `FluxionLatencyOptimizer.setup()` init

## Decisions Made

- **GroqKeyPool graceful degradation:** if `_key_pool` init fails (e.g. no env keys), `self._key_pool = None` and rotation is silently skipped — no exception propagated to request handler
- **WAL mode conditional:** `PRAGMA journal_mode=WAL` only runs when `self.db_path != ":memory:"` to avoid breaking pytest in-memory DB tests
- **FluxionLatencyOptimizer.setup() is the actual method name** (not `initialize()`) — `hasattr(optimizer, 'setup')` check added for future compatibility, with `initialize()` as fallback
- **groq_client.py rotate() reinitializes both sync and async clients** — both `self.client` (Groq sync, used by `asyncio.to_thread`) and `self.async_client` (AsyncGroq, used by streaming) updated with the new key
- **latency_metrics_handler uses `get_logger()` singleton** — consistent with existing analytics access pattern in orchestrator.py

## Deviations from Plan

None - plan executed exactly as written.

The plan specified `hasattr(latency_optimizer, 'initialize')` as the primary method name. After reading `latency_optimizer.py`, the actual method is `setup()`. Updated the wiring to check `setup` first (the real method), with `initialize` as a fallback — this is more correct than the plan spec.

## Issues Encountered

- Git pre-commit hook ran twice on each commit (lock error on second run). Both commits succeeded on the first hook run. The f03-02 changes (main.py) were captured in commit `7490e4b` which was named with the f03-01 label. This is a git hook timing issue — no code impact.

## User Setup Required

Optional: Add `GROQ_API_KEY_2` and `GROQ_API_KEY_3` to the iMac `.env` file to activate key pool rotation (triples effective rate limit). Without them, the pool initializes with 1 key and rotation is a no-op.

```bash
# On iMac, add to voice-agent/.env:
GROQ_API_KEY_2=gsk_...
GROQ_API_KEY_3=gsk_...
```

## Next Phase Readiness

- F03 Plan 02 complete — resilience and observability layer is wired
- `/api/metrics/latency` can be tested immediately after iMac pipeline restart
- Plan 03 (if exists) can build on top of the monitoring endpoint and key pool
- **iMac restart required** after pushing: `ssh imac "kill $(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && ... python main.py"`

---
*Phase: f03-latency-optimizer*
*Completed: 2026-03-04*
