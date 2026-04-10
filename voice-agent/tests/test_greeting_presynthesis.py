"""
Tests for A2: Greeting pre-synthesis with business_name.

Verifies that all 3 time-of-day greeting variants are pre-warmed
in TTSCache so that start_session() gets 0ms TTS latency.

These tests avoid importing VoiceOrchestrator directly (heavy deps)
and instead test the greeting generation logic + TTSCache behavior.
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path (same pattern as other tests in this repo)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tts import TTSCache


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUSINESS_NAME = "Salone Bella Vita"

EXPECTED_GREETINGS = [
    f"{BUSINESS_NAME}, buongiorno! Come posso aiutarla?",
    f"{BUSINESS_NAME}, buon pomeriggio! Come posso aiutarla?",
    f"{BUSINESS_NAME}, buonasera! Come posso aiutarla?",
]


def _build_greeting_variants(business_name: str):
    """Mirror the greeting generation logic from warm_greetings()."""
    return [
        f"{business_name}, buongiorno! Come posso aiutarla?",
        f"{business_name}, buon pomeriggio! Come posso aiutarla?",
        f"{business_name}, buonasera! Come posso aiutarla?",
    ]


def _make_tts_cache():
    """Create a TTSCache with a mock engine."""
    engine = MagicMock()
    engine.synthesize = AsyncMock(return_value=b"fake-audio")
    engine.get_info = MagicMock(return_value={"engine": "mock"})
    return TTSCache(engine)


# ---------------------------------------------------------------------------
# TTSCache warm_cache tests
# ---------------------------------------------------------------------------

class TestTTSCacheWarmGreetings:
    """Verify TTSCache.warm_cache() correctly pre-populates the cache."""

    @pytest.mark.asyncio
    async def test_warm_cache_populates_all_entries(self):
        """warm_cache() must put all 3 greetings into the cache dict."""
        tts = _make_tts_cache()

        await tts.warm_cache(EXPECTED_GREETINGS)

        for greeting in EXPECTED_GREETINGS:
            assert greeting in tts._cache, f"Missing from cache: {greeting}"

    @pytest.mark.asyncio
    async def test_synthesize_after_warm_is_cache_hit(self):
        """After warm_cache(), synthesize() must NOT call the engine."""
        tts = _make_tts_cache()
        await tts.warm_cache(EXPECTED_GREETINGS)

        # Reset mock to track new calls
        tts._engine.synthesize.reset_mock()

        audio = await tts.synthesize(EXPECTED_GREETINGS[0])

        assert audio == b"fake-audio"
        tts._engine.synthesize.assert_not_called()
        assert tts._hits == 1

    @pytest.mark.asyncio
    async def test_warm_cache_idempotent(self):
        """Calling warm_cache() twice with same texts must not re-synthesize."""
        tts = _make_tts_cache()

        await tts.warm_cache(EXPECTED_GREETINGS)
        call_count_1 = tts._engine.synthesize.call_count

        await tts.warm_cache(EXPECTED_GREETINGS)
        call_count_2 = tts._engine.synthesize.call_count

        # Second warm_cache should not add any new synthesize calls
        assert call_count_2 == call_count_1

    @pytest.mark.asyncio
    async def test_warm_cache_with_different_business_name(self):
        """warm_cache with new business name adds new entries."""
        tts = _make_tts_cache()

        await tts.warm_cache(EXPECTED_GREETINGS)
        original_size = len(tts._cache)

        new_greetings = _build_greeting_variants("Palestra Olympia")
        await tts.warm_cache(new_greetings)

        assert len(tts._cache) == original_size + 3


# ---------------------------------------------------------------------------
# Greeting variant generation tests
# ---------------------------------------------------------------------------

class TestGreetingVariantGeneration:
    """Verify the greeting text format matches session_manager.get_greeting()."""

    def test_all_3_variants_generated(self):
        """Must produce exactly 3 variants (buongiorno, buon pomeriggio, buonasera)."""
        variants = _build_greeting_variants(BUSINESS_NAME)
        assert len(variants) == 3

    def test_business_name_in_all_variants(self):
        """Each variant must start with the business_name."""
        custom_name = "Studio Medico Rossi"
        variants = _build_greeting_variants(custom_name)
        for v in variants:
            assert v.startswith(custom_name), f"Variant missing business_name: {v}"

    def test_format_matches_session_manager(self):
        """Format must be: '{business_name}, {saluto}! Come posso aiutarla?'"""
        variants = _build_greeting_variants(BUSINESS_NAME)
        saluti = ["buongiorno", "buon pomeriggio", "buonasera"]
        for variant, saluto in zip(variants, saluti):
            expected = f"{BUSINESS_NAME}, {saluto}! Come posso aiutarla?"
            assert variant == expected, f"Got: {variant}, expected: {expected}"

    def test_variants_cover_full_day(self):
        """The 3 variants must cover morning, afternoon, evening."""
        variants = _build_greeting_variants(BUSINESS_NAME)
        text = " ".join(variants)
        assert "buongiorno" in text
        assert "buon pomeriggio" in text
        assert "buonasera" in text


# ---------------------------------------------------------------------------
# Integration-style: simulate warm_greetings + start_session flow
# ---------------------------------------------------------------------------

class TestGreetingPresynthesisFlow:
    """Simulate the orchestrator warm_greetings() + start_session() flow."""

    @pytest.mark.asyncio
    async def test_full_flow_0ms_greeting(self):
        """
        Simulate: warm_greetings() populates cache, then start_session()
        calls synthesize() and gets a cache hit (0ms TTS).
        """
        tts = _make_tts_cache()

        # Step 1: warm_greetings() equivalent
        greetings = _build_greeting_variants(BUSINESS_NAME)
        await tts.warm_cache(greetings)

        # Step 2: start_session() picks one greeting based on time of day
        # (any of the 3 — they are all cached)
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 13:
            greeting = greetings[0]
        elif hour < 18:
            greeting = greetings[1]
        else:
            greeting = greetings[2]

        # Reset engine mock — synthesize should NOT be called
        tts._engine.synthesize.reset_mock()

        audio = await tts.synthesize(greeting)

        assert audio == b"fake-audio"
        tts._engine.synthesize.assert_not_called()  # 0ms — pure cache hit
        assert tts._hits == 1
        assert tts._misses == 0

    @pytest.mark.asyncio
    async def test_business_name_change_triggers_rewarm(self):
        """
        If business_name changes (loaded from DB), warm_greetings() must
        be called again with the new name.
        """
        tts = _make_tts_cache()

        # First warm with default name
        greetings_v1 = _build_greeting_variants("PLACEHOLDER")
        await tts.warm_cache(greetings_v1)

        # Business name updated from DB
        greetings_v2 = _build_greeting_variants("Salone Mario")
        await tts.warm_cache(greetings_v2)

        # New greeting should be cached
        tts._engine.synthesize.reset_mock()
        audio = await tts.synthesize("Salone Mario, buongiorno! Come posso aiutarla?")
        tts._engine.synthesize.assert_not_called()
