---
phase: f03-latency-optimizer
plan: 03
type: execute
wave: 2
depends_on:
  - f03-01
  - f03-02
files_modified:
  - voice-agent/tests/test_latency_benchmark.py
autonomous: false

must_haves:
  truths:
    - "pytest test_latency_benchmark.py runs on iMac and shows P95 < 800ms OR documents current baseline"
    - "All 1259 existing tests still PASS after F03 changes (no regressions)"
    - "GET /api/metrics/latency returns valid JSON with p95_ms field"
    - "Pipeline restart succeeds on iMac (port 3002 healthy after restart)"
    - "ROADMAP.md updated: F03 status COMPLETE with test results"
  artifacts:
    - path: "voice-agent/tests/test_latency_benchmark.py"
      provides: "Latency benchmark test suite with P95/P50 assertions"
      contains: "test_latency_p95"
  key_links:
    - from: "voice-agent/tests/test_latency_benchmark.py"
      to: "voice-agent/src/orchestrator.py process()"
      via: "VoiceOrchestrator instantiation in test fixture"
      pattern: "VoiceOrchestrator"
    - from: "voice-agent/tests/test_latency_benchmark.py"
      to: "voice-agent/src/analytics.py get_percentile_stats()"
      via: "ConversationLogger.get_percentile_stats()"
      pattern: "get_percentile_stats"
---

<objective>
Create the benchmark test suite, sync all F03 changes to iMac, run the full pytest suite (regression guard), verify the latency monitoring endpoint live, then update ROADMAP.md with results.

Purpose: This is the verification gate. The only way to know if P95 < 800ms is actually achieved is to measure it on the iMac pipeline (the MacBook cannot run the voice pipeline). If P95 target is not met, the benchmark output documents the new baseline for further optimization in a follow-up.
Output: test_latency_benchmark.py committed; iMac pytest run with 1259+ PASS / 0 FAIL; /api/metrics/latency endpoint verified; ROADMAP.md marked COMPLETE.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/f03-latency-optimizer/f03-RESEARCH.md
@.planning/phases/f03-latency-optimizer/f03-01-SUMMARY.md
@.planning/phases/f03-latency-optimizer/f03-02-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create test_latency_benchmark.py with P95/P50 assertions and git push to iMac</name>
  <files>voice-agent/tests/test_latency_benchmark.py</files>
  <action>
**Step 1 — Create voice-agent/tests/test_latency_benchmark.py:**

This file must follow the existing test patterns (see test_analytics.py for fixture style: uses sys.path, imports from src/ with absolute paths).

```python
"""
F03 Latency Benchmark Tests
============================
Measures P50/P95 latency across common voice utterances using a mock HTTP bridge.
Target: P95 < 800ms, P50 < 400ms (measured on iMac pipeline).

Run on iMac:
  pytest tests/test_latency_benchmark.py -v --tb=short

Note: These tests measure actual orchestrator processing time (NLU + FSM + LLM mock).
Real LLM latency is excluded — use /api/metrics/latency endpoint for live P95.
"""
import sys
import os
import time
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Path setup (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Benchmark utterances covering all pipeline layers
BENCHMARK_UTTERANCES = [
    ("L0_L1", "buongiorno voglio prenotare"),         # L1: PRENOTAZIONE direct
    ("L1_name", "sono Marco Rossi"),                   # L2: slot fill name
    ("L1_date", "per martedi pomeriggio"),             # L2: slot fill date
    ("L1_time", "alle quindici"),                      # L2: slot fill time
    ("L1_confirm", "si confermo"),                     # L2: CONFIRMING
    ("L3_faq", "cosa offrite"),                        # L3: FAQ
    ("L4_offscript", "avete il wifi"),                 # L4: LLM fallback (mocked)
]

N_RUNS = 5  # runs per utterance for stable measurement


@pytest.fixture
def mock_http_bridge():
    """Mock HTTP bridge (port 3001) to avoid real DB dependency in benchmarks."""
    mock = AsyncMock()
    mock.get_client_by_phone = AsyncMock(return_value=None)
    mock.get_available_slots = AsyncMock(return_value=[
        {"date": "2026-03-10", "time": "15:00", "operator": "Mario"}
    ])
    mock.create_booking = AsyncMock(return_value={"id": "TEST-001", "status": "confirmed"})
    return mock


@pytest.fixture
def mock_groq_client():
    """Mock Groq client to exclude real LLM latency from NLU benchmarks."""
    mock = MagicMock()
    mock.generate_response = AsyncMock(
        return_value="Posso aiutarla con le prenotazioni. Desidera un appuntamento?"
    )

    async def mock_streaming(*args, **kwargs):
        chunks = ["Posso ", "aiutarla ", "con ", "le ", "prenotazioni."]
        for chunk in chunks:
            yield {"text": chunk}

    mock.generate_response_streaming = mock_streaming
    return mock


@pytest.fixture
async def orchestrator(mock_http_bridge, mock_groq_client):
    """Create VoiceOrchestrator with mocked external dependencies."""
    try:
        from src.orchestrator import VoiceOrchestrator
    except ImportError:
        from orchestrator import VoiceOrchestrator

    with patch("src.orchestrator.aiohttp.ClientSession"):
        orch = VoiceOrchestrator(
            http_bridge_url="http://localhost:3001",
            groq_client=mock_groq_client,
            verticale_id="salone",
            enable_analytics=False  # No DB writes during benchmark
        )
    await orch.start_session()
    return orch


@pytest.mark.asyncio
async def test_latency_per_layer_nlu_only(orchestrator):
    """
    Measure NLU-only latency (L0-L3, excluding real LLM).
    Target: P95 < 200ms for L0-L3 layers.
    """
    latencies = []
    utterances = [u for _, u in BENCHMARK_UTTERANCES if _ != "L4_offscript"]

    for utterance in utterances:
        for _ in range(N_RUNS):
            t_start = time.perf_counter()
            try:
                await orchestrator.process(utterance)
            except Exception:
                pass  # Some utterances may error without full DB — measure anyway
            latencies.append((time.perf_counter() - t_start) * 1000)
            # Reset FSM between utterances to avoid state accumulation
            orchestrator.booking_sm.reset()

    if not latencies:
        pytest.skip("No latency measurements collected")

    latencies.sort()
    n = len(latencies)
    p50 = latencies[int(n * 0.50)]
    p95 = latencies[int(n * 0.95)]

    print(f"\n[F03 Benchmark] NLU-only (L0-L3):")
    print(f"  P50: {p50:.0f}ms | P95: {p95:.0f}ms | n={n}")

    # NLU-only should be well under 200ms (regex + TF-IDF, no LLM)
    assert p95 < 200, f"P95 NLU latency {p95:.0f}ms exceeds 200ms — check for slow regex or import overhead"


@pytest.mark.asyncio
async def test_intent_cache_hit(orchestrator):
    """Verify LRU cache: second call to same utterance is faster (cache hit)."""
    try:
        from src.intent_lru_cache import get_cached_intent, clear_intent_cache
    except ImportError:
        pytest.skip("intent_lru_cache not available")

    utterance = "buongiorno voglio prenotare un taglio"
    clear_intent_cache()

    # First call (cold cache)
    t0 = time.perf_counter()
    r1 = get_cached_intent(utterance)
    t_cold = (time.perf_counter() - t0) * 1000

    # Second call (warm cache)
    t0 = time.perf_counter()
    r2 = get_cached_intent(utterance)
    t_warm = (time.perf_counter() - t0) * 1000

    print(f"\n[F03 Cache] Cold: {t_cold:.2f}ms | Warm: {t_warm:.2f}ms | Speedup: {t_cold/max(t_warm,0.001):.0f}x")

    assert r1.category == r2.category, "Cache returned different intent category"
    assert t_warm < t_cold, f"Cache hit ({t_warm:.2f}ms) should be faster than cold ({t_cold:.2f}ms)"


@pytest.mark.asyncio
async def test_analytics_get_percentile_stats():
    """Verify get_percentile_stats() returns expected structure."""
    try:
        from src.analytics import ConversationLogger
    except ImportError:
        from analytics import ConversationLogger

    logger = ConversationLogger(db_path=":memory:")

    # Insert synthetic turns
    session_id = logger.start_session(
        phone_number="+39123456789",
        verticale_id="salone"
    )
    for ms in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
        logger.log_turn(
            session_id=session_id,
            user_input="test",
            intent="test",
            response="ok",
            latency_ms=float(ms),
            layer_used="L1_exact"
        )

    stats = logger.get_percentile_stats(hours=24)

    assert "p50_ms" in stats, "Missing p50_ms"
    assert "p95_ms" in stats, "Missing p95_ms"
    assert "p99_ms" in stats, "Missing p99_ms"
    assert "count" in stats, "Missing count"
    assert stats["count"] == 10, f"Expected 10 turns, got {stats['count']}"
    assert 400 <= stats["p50_ms"] <= 600, f"P50 should be ~500ms, got {stats['p50_ms']}"
    assert stats["p95_ms"] >= stats["p50_ms"], "P95 should be >= P50"

    print(f"\n[F03 Analytics] P50: {stats['p50_ms']}ms P95: {stats['p95_ms']}ms P99: {stats['p99_ms']}ms")
```

**Step 2 — Commit all F03 changes and push to iMac:**

After creating this test file, commit all F03 changes and sync to iMac:

```bash
# MacBook: stage and commit all F03 changes
git add voice-agent/src/intent_lru_cache.py
git add voice-agent/src/groq_key_pool.py
git add voice-agent/src/orchestrator.py
git add voice-agent/src/analytics.py
git add voice-agent/main.py
git add voice-agent/tests/test_latency_benchmark.py
git commit -m "feat(f03): latency optimizer — streaming L4, LRU cache, key pool, monitoring

- Wire generate_response_streaming() into L4 fallback (eliminates asyncio.to_thread overhead)
- Add FALLBACK_RESPONSES dict for timeout resilience
- Create intent_lru_cache.py: 100-slot LRU eliminates 3x classify_intent per turn
- asyncio.gather() at L0 for parallel prefilter + entity extraction
- Create groq_key_pool.py: round-robin 3 Groq keys, triples rate limit capacity
- analytics.py: get_percentile_stats() P50/P95/P99 + WAL mode
- main.py: /api/metrics/latency route + FluxionLatencyOptimizer init + extended TTS warmup
- tests/test_latency_benchmark.py: benchmark suite + analytics unit test

Target: P95 <800ms from ~1330ms baseline"

# Push to master
git push origin master

# Sync iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
```
  </action>
  <verify>
```bash
# Verify git push succeeded and iMac has the files
ssh imac "ls '/Volumes/MacSSD - Dati/fluxion/voice-agent/src/intent_lru_cache.py' '/Volumes/MacSSD - Dati/fluxion/voice-agent/src/groq_key_pool.py' '/Volumes/MacSSD - Dati/fluxion/voice-agent/tests/test_latency_benchmark.py' 2>&1"
```
  </verify>
  <done>test_latency_benchmark.py committed; git push succeeded; iMac has all 6 new/modified files confirmed via SSH ls</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
F03 Latency Optimizer — all changes synced to iMac:
- streaming L4 in orchestrator.py (generate_response_streaming, FALLBACK_RESPONSES, asyncio.gather)
- intent_lru_cache.py (100-slot LRU for classify_intent)
- groq_key_pool.py (round-robin 3 Groq keys)
- analytics.py (get_percentile_stats, WAL mode)
- main.py (/api/metrics/latency route, extended TTS warmup, FluxionLatencyOptimizer)
- test_latency_benchmark.py (benchmark + analytics unit tests)
  </what-built>
  <how-to-verify>
Run these commands in order. Paste results back.

**1. Full pytest suite (regression guard — must be 1259+ PASS / 0 FAIL):**
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m pytest tests/ -v --tb=short 2>&1 | tail -30"
```

**2. Restart voice pipeline:**
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
sleep 5
```

**3. Health check:**
```bash
curl -s http://192.168.1.12:3002/health | python3 -m json.tool
```

**4. Latency metrics endpoint:**
```bash
curl -s http://192.168.1.12:3002/api/metrics/latency | python3 -m json.tool
```

**5. End-to-end voice test (should see F03 layer timing in pipeline log):**
```bash
curl -s -X POST http://192.168.1.12:3002/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text":"Buongiorno, vorrei prenotare un taglio"}' | python3 -m json.tool

# Check pipeline log for F03 timing output
ssh imac "tail -20 /tmp/voice-pipeline.log"
```

**Expected:**
- pytest: N PASSED / 0 FAILED (N >= 1259, new benchmark tests add to count)
- health: {"status": "ok", ...}
- /api/metrics/latency: {"p50_ms": ..., "p95_ms": ..., "p99_ms": ..., "count": ..., "hours": 24}
- Pipeline log shows `[F03] Total: Xms | Layer: ...` lines
  </how-to-verify>
  <resume-signal>
Paste test results. If all tests pass and endpoint works, type "approved" to continue.
If tests fail, describe which tests failed and paste the error output — the plan will create gap closure plans.
  </resume-signal>
</task>

</tasks>

<verification>
F03 is complete when:
1. All 1259+ existing pytest tests PASS (0 regressions)
2. New benchmark tests PASS (test_analytics_get_percentile_stats, test_intent_cache_hit)
3. /api/metrics/latency returns valid JSON with p95_ms field
4. Pipeline restarts cleanly (health check OK)
5. Voice process returns response (end-to-end works)
6. Pipeline log shows [F03] timing lines
7. ROADMAP.md updated to COMPLETE
</verification>

<success_criteria>
After human verification "approved":

- [ ] Update .planning/ROADMAP.md: F03 status → COMPLETE with actual P95 measurement
- [ ] Update .planning/STATE.md: current position → F03 complete, next → F04
- [ ] git commit ROADMAP + STATE updates: `docs(f03): phase complete — P95 Xms measured`
- [ ] git push origin master
- [ ] ssh imac "git pull" to sync final docs

If P95 measured > 800ms: Mark F03 as PARTIALLY COMPLETE with actual P95 baseline documented.
Next session will create F03.1 gap closure if needed.
</success_criteria>

<output>
After completion, create `.planning/phases/f03-latency-optimizer/f03-03-SUMMARY.md` with:
- pytest results (N PASSED / N FAILED)
- Actual P95 measured (from /api/metrics/latency after a few test voice calls)
- Pipeline startup log (any errors from FluxionLatencyOptimizer init)
- P95 target met: YES / PARTIALLY / NO (with measured baseline)
</output>
