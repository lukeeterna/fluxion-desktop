---
phase: f03-latency-optimizer
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/groq_key_pool.py
  - voice-agent/src/groq_client.py
  - voice-agent/src/analytics.py
  - voice-agent/main.py
autonomous: true

must_haves:
  truths:
    - "GET /api/metrics/latency returns JSON with p50_ms, p95_ms, p99_ms, count, hours"
    - "analytics.py has get_percentile_stats() method returning percentile breakdowns"
    - "analytics.py _init_db() enables WAL mode via PRAGMA journal_mode=WAL"
    - "GroqKeyPool class reads GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3 from env"
    - "groq_client.py imports GroqKeyPool and calls pool.rotate() on 429 in the retry loop"
    - "main.py TTS warmup list extended with ask_surname, ask_phone partial phrases"
    - "FluxionLatencyOptimizer imported and initialized in main.py startup"
  artifacts:
    - path: "voice-agent/src/groq_key_pool.py"
      provides: "Round-robin Groq key pool, Python 3.9 compatible"
      exports: ["GroqKeyPool"]
    - path: "voice-agent/src/groq_client.py"
      provides: "GroqKeyPool wired into generate_response() retry loop on 429"
      contains: "GroqKeyPool"
    - path: "voice-agent/src/analytics.py"
      provides: "get_percentile_stats() + WAL mode"
      contains: "get_percentile_stats"
    - path: "voice-agent/main.py"
      provides: "/api/metrics/latency route + FluxionLatencyOptimizer init + TTS warmup"
      contains: "latency_metrics_handler"
  key_links:
    - from: "voice-agent/main.py latency_metrics_handler"
      to: "voice-agent/src/analytics.py get_percentile_stats()"
      via: "logger.get_percentile_stats(hours=24)"
      pattern: "get_percentile_stats"
    - from: "voice-agent/src/analytics.py _init_db"
      to: "SQLite WAL mode"
      via: "conn.execute(\"PRAGMA journal_mode=WAL\")"
      pattern: "journal_mode=WAL"
    - from: "voice-agent/src/groq_client.py generate_response() retry loop"
      to: "voice-agent/src/groq_key_pool.py GroqKeyPool.rotate()"
      via: "self._key_pool.rotate() on 429 RateLimitError"
      pattern: "rotate"
---

<objective>
Add three resilience and observability improvements that are independent of the core latency changes in Plan 01: a round-robin Groq key pool (rate limit resilience) wired into groq_client.py, P50/P95/P99 latency monitoring endpoint, SQLite WAL mode (concurrent write safety), extended TTS warmup, and FluxionLatencyOptimizer wiring.

Purpose: These changes make the pipeline measurable (we can verify P95 < 800ms via the endpoint), more resilient under load (key pool triples effective rate limit), and safer under concurrent voice+WhatsApp writes (WAL mode).
Output: groq_key_pool.py, updated groq_client.py (pool wired on 429), updated analytics.py (WAL + percentiles), updated main.py (monitoring route + optimizer init + extended TTS warmup).
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/phases/f03-latency-optimizer/f03-RESEARCH.md

# Key source files (read before implementing)
@voice-agent/src/analytics.py
@voice-agent/src/groq_client.py
@voice-agent/src/latency_optimizer.py
@voice-agent/main.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create groq_key_pool.py, wire it into groq_client.py on 429, and add get_percentile_stats() + WAL mode to analytics.py</name>
  <files>voice-agent/src/groq_key_pool.py, voice-agent/src/groq_client.py, voice-agent/src/analytics.py</files>
  <action>
**Step 1 — Create voice-agent/src/groq_key_pool.py (new file):**

```python
"""
Groq Key Pool — Fluxion F03 Latency Optimizer
=============================================
Round-robin rotation across up to 3 Groq free-tier API keys.
Triples effective rate limit — rotates on 429 errors.

Python 3.9 compatible: uses List[], Optional[] from typing.
Thread safety: self._index += 1 is safe in asyncio single-thread event loop
(no await between read and write, GIL protects against thread races).

Usage:
    pool = GroqKeyPool()
    key = pool.current_key()
    # on 429 error:
    key = pool.rotate()

Env vars: GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3
"""
import os
from typing import List


class GroqKeyPool:
    """Round-robin Groq API key pool for rate limit resilience."""

    def __init__(self):
        self._keys: List[str] = []
        self._index: int = 0
        # Load from env: GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3
        for suffix in ["", "_2", "_3"]:
            key = os.environ.get("GROQ_API_KEY" + suffix)
            if key and key.strip():
                self._keys.append(key.strip())
        if not self._keys:
            raise ValueError(
                "At least one GROQ_API_KEY must be set in environment. "
                "Optional: GROQ_API_KEY_2, GROQ_API_KEY_3 for rate limit pooling."
            )

    def current_key(self) -> str:
        """Return the current active key (does not advance index)."""
        return self._keys[self._index % len(self._keys)]

    def rotate(self) -> str:
        """Advance to next key and return it. Call on 429 rate limit error."""
        self._index += 1
        return self.current_key()

    @property
    def size(self) -> int:
        """Number of keys in the pool."""
        return len(self._keys)

    def __repr__(self) -> str:
        return f"GroqKeyPool(size={self.size}, current_index={self._index % self.size})"
```

**Step 2 — Wire GroqKeyPool into groq_client.py generate_response() retry loop:**

Read voice-agent/src/groq_client.py carefully before editing.

Add the import at the top of groq_client.py (after existing imports):

```python
# F03: Groq key pool for rate limit resilience
try:
    from .groq_key_pool import GroqKeyPool
    _HAS_KEY_POOL = True
except ImportError:
    try:
        from groq_key_pool import GroqKeyPool
        _HAS_KEY_POOL = True
    except ImportError:
        _HAS_KEY_POOL = False
```

In the `GroqClient.__init__()` method, add pool initialization after the existing `self.api_key = api_key` assignment:

```python
        # F03: Key pool for 429 rotation (falls back gracefully if only 1 key)
        if _HAS_KEY_POOL:
            try:
                self._key_pool = GroqKeyPool()
            except ValueError:
                self._key_pool = None
        else:
            self._key_pool = None
```

In `generate_response()`, find the retry loop that handles rate limit / 429 errors (look for `RateLimitError` or HTTP 429 handling in the retry logic). In that except block, BEFORE sleeping or re-raising, add key rotation:

```python
                # F03: rotate key pool on 429
                if self._key_pool is not None:
                    new_key = self._key_pool.rotate()
                    self.api_key = new_key
                    # Reinitialize Groq client with new key if client object holds the key
                    if hasattr(self, 'client') and self.client is not None:
                        import groq as groq_lib
                        self.client = groq_lib.AsyncGroq(api_key=new_key)
```

NOTE: Read the actual groq_client.py implementation before writing this. The exact attribute names (`self.client`, `self.api_key`) and the retry structure may differ. Adapt the wiring to match the actual code — the goal is: on 429 error in retry loop, call `self._key_pool.rotate()` and update whichever attribute holds the active API key.

**Step 3 — Add get_percentile_stats() method to analytics.py ConversationLogger class:**

Add this method immediately after the existing `get_latency_stats()` method (after line 540, before the `# Analytics Queries` section comment):

```python
    def get_percentile_stats(self, hours: int = 24) -> dict:
        """
        Get P50/P95/P99 latency percentiles from recent turns.

        F03 Latency Optimizer — provides data for /api/metrics/latency endpoint.
        Uses Python-side percentile calculation (SQLite PERCENTILE_CONT not available).

        Args:
            hours: Number of hours to look back (default: 24)

        Returns:
            Dict with p50_ms, p95_ms, p99_ms, count, hours
        """
        from datetime import datetime, timedelta
        since = (datetime.now() - timedelta(hours=hours)).isoformat()

        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT latency_ms FROM conversation_turns "
                "WHERE timestamp > ? AND latency_ms IS NOT NULL ORDER BY latency_ms",
                (since,)
            ).fetchall()

        if not rows:
            return {"p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "count": 0, "hours": hours}

        latencies = [r[0] for r in rows]
        n = len(latencies)

        def _pct(data, p):
            """Return p-th percentile from a sorted list."""
            idx = max(0, min(int(n * p / 100.0), n - 1))
            return round(data[idx], 1)

        return {
            "p50_ms": _pct(latencies, 50),
            "p95_ms": _pct(latencies, 95),
            "p99_ms": _pct(latencies, 99),
            "count": n,
            "hours": hours
        }
```

**Step 4 — Enable WAL mode in analytics.py _init_db():**

Find `_init_db()` (around line 232-236):
```python
    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)
            conn.commit()
```

Replace with:
```python
    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            # F03: WAL mode for concurrent read/write (voice + WhatsApp callback simultaneously)
            # Safe for SQLite 3.7+ (macOS iMac has SQLite 3.39+)
            if self.db_path != ":memory:":
                conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(self.SCHEMA)
            conn.commit()
```

**Constraints:**
- Python 3.9 — use `dict` return type annotation (not `Dict`), or omit annotation
- WAL mode must be skipped for `:memory:` DB (used in tests — WAL not applicable to in-memory)
- Do NOT cache entity results across turns in analytics (dates change)
- The GroqKeyPool wiring in groq_client.py must be non-fatal if pool init fails (only 1 key available is fine — pool simply has size=1 and rotation is a no-op)
  </action>
  <verify>grep -n "get_percentile_stats\|journal_mode=WAL" /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/src/analytics.py && grep -n "GroqKeyPool\|rotate\|_key_pool" /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/src/groq_client.py | head -10</verify>
  <done>groq_key_pool.py exists with GroqKeyPool class; groq_client.py imports GroqKeyPool and calls pool.rotate() on 429 in retry loop; analytics.py has get_percentile_stats() returning {p50_ms, p95_ms, p99_ms, count, hours}; analytics.py _init_db() executes PRAGMA journal_mode=WAL for file-based DBs</done>
</task>

<task type="auto">
  <name>Task 2: Add /api/metrics/latency route to main.py, extend TTS warmup, wire FluxionLatencyOptimizer</name>
  <files>voice-agent/main.py</files>
  <action>
Read voice-agent/main.py carefully before editing. All changes are in main.py.

**Step 1 — Add latency metrics HTTP route:**

In `VoiceAgentHTTPServer._setup_routes()` (around line 181-204), add after the last `add_get` line:

```python
        self.app.router.add_get("/api/metrics/latency", self.latency_metrics_handler)
```

**Step 2 — Add latency_metrics_handler method to VoiceAgentHTTPServer class:**

Add this method to the VoiceAgentHTTPServer class (after status_handler or near the other GET handlers):

```python
    async def latency_metrics_handler(self, request):
        """
        GET /api/metrics/latency
        F03: P50/P95/P99 latency monitoring endpoint.
        Returns JSON: {p50_ms, p95_ms, p99_ms, count, hours}
        """
        try:
            from src.analytics import get_logger
            hours = int(request.rel_url.query.get("hours", "24"))
            logger = get_logger()
            stats = logger.get_percentile_stats(hours=hours)
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
```

**Step 3 — Wire FluxionLatencyOptimizer at startup:**

Find the `async def main(port: int = 3002):` startup function. After the TTS warmup section (after line 573 `print(f"✅ TTS cache pronta...")`), add:

```python
    # F03: Wire FluxionLatencyOptimizer (connection pool + metrics tracking)
    try:
        from src.latency_optimizer import FluxionLatencyOptimizer
        latency_optimizer = FluxionLatencyOptimizer()
        await latency_optimizer.initialize()
        print("✅ Latency optimizer initialized (connection pool + metrics)")
    except Exception as e:
        print(f"⚠️  Latency optimizer init failed (non-fatal): {e}")
```

Note: The try/except makes this non-fatal — if FluxionLatencyOptimizer has dependency issues, startup still succeeds.

**Step 4 — Extend TTS warmup phrase list:**

Find the static_phrases list in the startup function (around lines 562-570):

```python
    static_phrases += [
        "Buongiorno! Come posso aiutarla?",
        "Buon pomeriggio! Come posso aiutarla?",
        "Buonasera! Come posso aiutarla?",
        "Di nulla! Arrivederci, buona giornata!",
        "Grazie, a presto!",
        "Arrivederci, buona giornata!",
    ]
```

Replace this with (adds 6 new phrases for common L4 fallback responses):

```python
    static_phrases += [
        "Buongiorno! Come posso aiutarla?",
        "Buon pomeriggio! Come posso aiutarla?",
        "Buonasera! Come posso aiutarla?",
        "Di nulla! Arrivederci, buona giornata!",
        "Grazie, a presto!",
        "Arrivederci, buona giornata!",
        # F03: Pre-warm L4 fallback phrases (eliminate TTS latency for common fallbacks)
        "Mi scusi, sto impiegando un po' di tempo. Posso aiutarla a prenotare un appuntamento?",
        "Posso aiutarla principalmente con le prenotazioni. Desidera fissare un appuntamento?",
        "Mi scusi, sono momentaneamente sovraccarica. Puo ripetere?",
        "Mi dice il cognome?",
        "Perfetto, le confermo: ",
        "Un momento, verifico la disponibilita.",
    ]
```

**Constraints:**
- web.json_response is already imported via aiohttp (existing pattern in the file — verify by checking other handlers)
- hours query param must be int-cast with fallback to 24
- FluxionLatencyOptimizer.initialize() may be async — check latency_optimizer.py signature. If no async initialize() exists, call what is available (the class constructor itself may do init synchronously — wrap in try/except)
  </action>
  <verify>curl -s http://192.168.1.12:3002/api/metrics/latency | python3 -m json.tool  # after iMac restart in plan 03</verify>
  <done>main.py has /api/metrics/latency route registered in _setup_routes(); latency_metrics_handler() method exists; TTS warmup list has 12+ phrases including FALLBACK_RESPONSES strings; FluxionLatencyOptimizer init attempted at startup</done>
</task>

</tasks>

<verification>
After implementing both tasks, run syntax check locally (MacBook Python 3.9 equivalent check):

```bash
# MacBook syntax check (Python 3.13 but catches 3.9-incompatible syntax)
python3 -c "
import ast, sys
for f in ['voice-agent/src/groq_key_pool.py', 'voice-agent/src/groq_client.py', 'voice-agent/src/analytics.py', 'voice-agent/main.py']:
    try:
        ast.parse(open(f).read()); print(f'OK: {f}')
    except SyntaxError as e: print(f'FAIL: {f}: {e}'); sys.exit(1)
"
```
</verification>

<success_criteria>
- groq_key_pool.py exists with GroqKeyPool class (current_key, rotate, size)
- groq_client.py imports GroqKeyPool and calls pool.rotate() on 429 in generate_response() retry loop
- analytics.py has get_percentile_stats() returning {p50_ms, p95_ms, p99_ms, count, hours}
- analytics.py _init_db() enables WAL mode for file-based DBs
- main.py registers GET /api/metrics/latency route
- main.py TTS warmup list includes FALLBACK_RESPONSES phrases
- FluxionLatencyOptimizer init attempted at startup (non-fatal on failure)
- No Python 3.10+ syntax introduced (no walrus, no X|Y union, no match)
</success_criteria>

<output>
After completion, create `.planning/phases/f03-latency-optimizer/f03-02-SUMMARY.md` with:
- What was changed and in which files (exact methods/lines where possible)
- FluxionLatencyOptimizer.initialize() availability (sync vs async — note what was found)
- GroqKeyPool wiring: which attribute in groq_client.py holds the active key (document actual attribute names used)
- Any deviations from the plan and why
</output>
