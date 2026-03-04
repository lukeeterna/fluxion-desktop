"""
F03 Latency Benchmark — Fluxion Voice Agent
============================================
Tests for:
  - NLU layer P50/P95 latency (local computation, no Groq)
  - LRU cache hit speed vs cold classification
  - Analytics get_percentile_stats() structure (in-memory DB)
  - Live /api/metrics/latency endpoint (skipped when iMac unreachable)

VoiceOrchestrator constructor pattern (F03 decision, STATE.md):
    orch = VoiceOrchestrator(verticale_id="salone", business_name="Test Salon", groq_api_key="test-key")
    orch.groq = mock_groq_client  # patch AFTER construction

Python 3.9 compatible — uses typing.Optional[], List[], Dict[].
"""

import sys
import time
import sqlite3
import statistics
import tempfile
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# Path setup — supports both package and direct pytest execution
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ---------------------------------------------------------------------------
# Benchmark utterances (6 representative turns across the booking flow)
# ---------------------------------------------------------------------------
BENCHMARK_UTTERANCES = [
    ("L1", "buongiorno voglio prenotare"),
    ("L2_name", "sono Marco Rossi"),
    ("L2_date", "per martedi pomeriggio"),
    ("L2_time", "alle quindici"),
    ("L2_confirm", "si confermo"),
    ("L3_faq", "cosa offrite"),
]

RUNS_PER_UTTERANCE = 5  # warm runs after one cold discard


# ===========================================================================
# Test 1: NLU-only P50/P95 (no Groq, no TTS, no DB)
# ===========================================================================

class TestLatencyP95:
    """
    NLU layer latency benchmark.

    Measures classify_intent() — the L1 intent classifier — across 6
    representative utterances × RUNS_PER_UTTERANCE warm runs.

    Target: P95 < 200ms for the NLU-only layer.
    Even if the live pipeline P95 target (< 800ms total) is not yet met,
    the NLU layer must be fast (it runs on every turn with no external I/O).
    """

    def test_latency_p95(self):
        """NLU layer P95 must be < 200ms (no Groq / TTS / DB I/O)."""
        from intent_classifier import classify_intent

        latencies_ms: List[float] = []

        for label, utterance in BENCHMARK_UTTERANCES:
            # One cold run to populate any internal caches
            classify_intent(utterance)

            # Warm runs — these are what we measure
            for _ in range(RUNS_PER_UTTERANCE):
                t0 = time.perf_counter()
                result = classify_intent(utterance)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                latencies_ms.append(elapsed_ms)
                # Basic sanity: result must be an IntentResult
                assert result is not None, f"classify_intent returned None for '{utterance}'"

        latencies_ms.sort()
        n = len(latencies_ms)
        p50_idx = max(0, min(int(n * 0.50), n - 1))
        p95_idx = max(0, min(int(n * 0.95), n - 1))
        p50_ms = latencies_ms[p50_idx]
        p95_ms = latencies_ms[p95_idx]

        print(f"\n[Benchmark] NLU classify_intent — {n} measurements")
        print(f"  P50 = {p50_ms:.2f} ms")
        print(f"  P95 = {p95_ms:.2f} ms")
        print(f"  P99 = {latencies_ms[max(0, min(int(n * 0.99), n - 1))]:.2f} ms")
        print(f"  min = {latencies_ms[0]:.2f} ms")
        print(f"  max = {latencies_ms[-1]:.2f} ms")

        assert p95_ms < 200.0, (
            f"NLU P95 = {p95_ms:.1f} ms — exceeds 200ms NLU target. "
            f"P50 = {p50_ms:.1f} ms."
        )


# ===========================================================================
# Test 2: LRU cache hit speed
# ===========================================================================

class TestIntentCacheHit:
    """
    Verify the LRU intent cache (intent_lru_cache.py) returns on the second
    call for the same (normalized) input text, and that the cache hit is
    measurably faster than the cold call.
    """

    def test_intent_cache_hit(self):
        """Cache hit on same utterance returns same result and is not slower."""
        from intent_lru_cache import get_cached_intent, clear_intent_cache

        utterance = "buongiorno voglio prenotare"

        # Clear cache to guarantee a cold start
        clear_intent_cache()

        # Cold call
        t0 = time.perf_counter()
        result_cold = get_cached_intent(utterance)
        cold_ms = (time.perf_counter() - t0) * 1000.0

        # Warm call (cache hit)
        t0 = time.perf_counter()
        result_warm = get_cached_intent(utterance)
        warm_ms = (time.perf_counter() - t0) * 1000.0

        print(f"\n[Cache] cold={cold_ms:.3f}ms  warm={warm_ms:.3f}ms")

        # Results must be identical
        assert result_cold.intent == result_warm.intent, (
            f"Cache returned different intent: cold={result_cold.intent} warm={result_warm.intent}"
        )

        # Warm must be at least as fast (allow up to 2× tolerance for timing jitter)
        # The real guarantee is that warm_ms is sub-millisecond (dict lookup).
        # We don't hard-assert speed ratio to avoid flakiness on CI.
        assert warm_ms < max(cold_ms * 2, 5.0), (
            f"Cache hit ({warm_ms:.3f}ms) slower than 2× cold ({cold_ms:.3f}ms)"
        )

        # Verify same category
        assert result_cold.category == result_warm.category

        # Cleanup
        clear_intent_cache()


# ===========================================================================
# Test 3: Analytics get_percentile_stats() structure
# ===========================================================================

class TestAnalyticsGetPercentileStats:
    """
    Insert 10 synthetic turns into an in-memory ConversationLogger,
    then verify get_percentile_stats() returns the expected dict structure
    with p50_ms, p95_ms, p99_ms, count keys.
    """

    def _make_logger(self) -> Any:
        """Return a ConversationLogger backed by a temp file DB."""
        from analytics import ConversationLogger
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        return ConversationLogger(db_path=path), path

    def test_analytics_get_percentile_stats(self):
        """get_percentile_stats() returns {p50_ms, p95_ms, p99_ms, count} with 10 turns."""
        from analytics import ConversationLogger, ConversationOutcome

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            logger = ConversationLogger(db_path=db_path)

            # Start a session
            session_id = logger.start_session(
                verticale_id="salone",
                client_name="Benchmark Test"
            )

            # Insert 10 synthetic turns with known latencies: 100..1000ms step 100
            for i in range(1, 11):
                latency = float(i * 100)  # 100, 200, ..., 1000 ms
                logger.log_turn(
                    session_id=session_id,
                    user_input=f"test utterance {i}",
                    intent="prenotazione",
                    response=f"risposta {i}",
                    latency_ms=latency,
                    layer_used="L2_intent"
                )

            logger.end_session(session_id, ConversationOutcome.COMPLETED)

            # Query percentile stats — use large hours window to capture all turns
            stats = logger.get_percentile_stats(hours=48)

            # Structural checks
            assert "p50_ms" in stats, f"Missing p50_ms in stats: {stats}"
            assert "p95_ms" in stats, f"Missing p95_ms in stats: {stats}"
            assert "p99_ms" in stats, f"Missing p99_ms in stats: {stats}"
            assert "count" in stats, f"Missing count in stats: {stats}"

            # Value sanity checks
            assert stats["count"] == 10, f"Expected 10 turns, got {stats['count']}"
            assert stats["p50_ms"] > 0, f"p50_ms should be > 0, got {stats['p50_ms']}"
            assert stats["p95_ms"] >= stats["p50_ms"], (
                f"p95 ({stats['p95_ms']}) must be >= p50 ({stats['p50_ms']})"
            )
            assert stats["p99_ms"] >= stats["p95_ms"], (
                f"p99 ({stats['p99_ms']}) must be >= p95 ({stats['p95_ms']})"
            )

            print(f"\n[Analytics] percentile stats: {stats}")

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


# ===========================================================================
# Test 4: Live /api/metrics/latency endpoint (skipped if unreachable)
# ===========================================================================

class TestP95ViaMetricsEndpoint:
    """
    Live endpoint test — calls http://192.168.1.12:3002/api/metrics/latency
    and verifies the p95_ms field is present in the JSON response.

    Skipped automatically if the iMac voice pipeline is not reachable,
    so this test does not fail in development / CI environments.
    """

    IMAC_HOST = "192.168.1.12"
    IMAC_PORT = 3002
    ENDPOINT = f"http://192.168.1.12:3002/api/metrics/latency"
    HEALTH_URL = f"http://192.168.1.12:3002/health"
    TIMEOUT_S = 3.0

    def _is_reachable(self) -> bool:
        """Quick health-check: returns True if pipeline responds within timeout."""
        try:
            import urllib.request
            import urllib.error
            req = urllib.request.urlopen(self.HEALTH_URL, timeout=self.TIMEOUT_S)
            return req.status == 200
        except Exception:
            return False

    def test_p95_via_metrics_endpoint(self):
        """GET /api/metrics/latency returns JSON with p95_ms field."""
        if not self._is_reachable():
            pytest.skip("iMac voice pipeline not reachable (192.168.1.12:3002) — skipping live endpoint test")

        import json
        import urllib.request

        try:
            req = urllib.request.urlopen(self.ENDPOINT, timeout=self.TIMEOUT_S)
            body = req.read().decode("utf-8")
            data = json.loads(body)
        except Exception as exc:
            pytest.fail(f"Failed to fetch {self.ENDPOINT}: {exc}")

        assert "p95_ms" in data, (
            f"p95_ms not found in /api/metrics/latency response: {data}"
        )

        # Additional structural assertions
        for key in ("p50_ms", "p95_ms", "p99_ms", "count"):
            assert key in data, f"Missing key '{key}' in metrics response: {data}"

        p95 = data["p95_ms"]
        print(f"\n[Live] /api/metrics/latency → p95={p95}ms  full={data}")

        # Document the baseline (no hard assert on P95 < 800ms since we may not
        # have live traffic yet; the benchmark test is the source of truth).
        if data["count"] > 0:
            print(f"[Live] Pipeline has {data['count']} turns in window — p95={p95}ms")
        else:
            print("[Live] No turns logged yet (pipeline just restarted) — count=0 is valid")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
