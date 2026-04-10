"""
Tests for B1 + B2 + B3 humanness improvements.

B1: Filler pre-DB-lookup ("Un momento...")
B2: Mirror in confirmation (name + slot echo)
B3: Goodbye variants by context
"""

import sys
import asyncio
import random
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from booking_state_machine import (
    BookingStateMachine,
    BookingState,
    BookingContext,
    TEMPLATES,
    GOODBYE_VARIANTS,
    get_goodbye,
)
from tts import TTSCache


# =============================================================================
# B1: Filler phrases
# =============================================================================

def _read_orchestrator_source():
    """Read orchestrator.py source without importing it (avoids groq dependency)."""
    orch_path = Path(__file__).parent.parent / "src" / "orchestrator.py"
    return orch_path.read_text(encoding="utf-8")


def _extract_filler_phrases(source: str):
    """Extract FILLER_PHRASES list from source text."""
    import ast
    # Find the FILLER_PHRASES = [...] assignment
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "FILLER_PHRASES":
                    return ast.literal_eval(node.value)
    return None


class TestB1FillerPhrases:
    """B1: Filler phrases for VoIP pre-DB-lookup."""

    def test_filler_phrases_exist(self):
        """At least 4 filler variants are defined."""
        source = _read_orchestrator_source()
        phrases = _extract_filler_phrases(source)
        assert phrases is not None, "FILLER_PHRASES not found in orchestrator.py"
        assert len(phrases) >= 4
        for phrase in phrases:
            assert isinstance(phrase, str)
            assert len(phrase) > 3

    def test_filler_presynthesis(self):
        """warm_cache pre-populates all filler phrases in TTSCache."""
        engine = MagicMock()
        engine.synthesize = AsyncMock(return_value=b"fake-audio")
        engine.get_info = MagicMock(return_value={"engine": "mock"})
        cache = TTSCache(engine)

        source = _read_orchestrator_source()
        phrases = _extract_filler_phrases(source)
        assert phrases is not None

        asyncio.get_event_loop().run_until_complete(
            cache.warm_cache(list(phrases))
        )
        for phrase in phrases:
            assert phrase.strip() in cache._cache, f"'{phrase}' not pre-warmed"

    def test_filler_only_for_voip(self):
        """Orchestrator._is_voip_call must be False by default (text API mode)."""
        source = _read_orchestrator_source()
        # Verify flag exists and defaults to False
        assert "self._is_voip_call" in source, "_is_voip_call flag missing from orchestrator.py"
        assert "self._is_voip_call: bool = False" in source or "self._is_voip_call = False" in source
        # Verify greet() sets it to True (VoIP entry point)
        assert "self._is_voip_call = True" in source, "greet() must set _is_voip_call = True"


# =============================================================================
# B2: Mirror in confirmation
# =============================================================================

class TestB2MirrorConfirmation:
    """B2: Confirmation template includes client name."""

    def _make_bsm(self):
        """Create a BookingStateMachine with mocked NLU."""
        nlu = MagicMock()
        nlu.extract = AsyncMock(return_value=None)
        return BookingStateMachine(groq_nlu=nlu, services_config={"taglio": {}})

    def test_confirm_includes_client_name(self):
        """When client_name is known, confirmation includes it."""
        bsm = self._make_bsm()
        bsm.context.client_name = "Marco"
        bsm.context.service = "taglio"
        bsm.context.service_display = "taglio"
        bsm.context.date = "2026-04-15"
        bsm.context.date_display = "martedi 15 aprile"
        bsm.context.time = "10:00"
        bsm.context.time_display = "alle 10:00"

        text = bsm._format_confirm_booking()
        assert "Marco" in text
        assert "taglio" in text

    def test_confirm_without_name(self):
        """When client_name is None, confirmation still works (no crash)."""
        bsm = self._make_bsm()
        bsm.context.client_name = None
        bsm.context.service = "piega"
        bsm.context.service_display = "piega"
        bsm.context.date = "2026-04-15"
        bsm.context.date_display = "martedi 15 aprile"
        bsm.context.time = "14:00"
        bsm.context.time_display = "alle 14:00"

        text = bsm._format_confirm_booking()
        # Should not contain "None" and should have summary
        assert "None" not in text
        assert "piega" in text

    def test_confirm_has_micro_reaction(self):
        """Confirmation text starts with a micro-reaction."""
        bsm = self._make_bsm()
        bsm.context.client_name = "Giulia"
        bsm.context.service = "colore"
        bsm.context.service_display = "colore"
        bsm.context.date = "2026-04-16"
        bsm.context.date_display = "mercoledi 16 aprile"
        bsm.context.time = "11:00"
        bsm.context.time_display = "alle 11:00"

        # Run multiple times — at least one should have a micro prefix
        texts = [bsm._format_confirm_booking() for _ in range(10)]
        # The micro "confirmed" reactions: Fantastico, Grande, Ecco fatto, Perfetto
        has_micro = any(
            t.startswith("Fantastico") or t.startswith("Grande") or
            t.startswith("Ecco fatto") or t.startswith("Perfetto")
            for t in texts
        )
        assert has_micro, f"No micro-reaction found in: {texts[0][:60]}"


# =============================================================================
# B3: Goodbye variants
# =============================================================================

class TestB3GoodbyeVariants:
    """B3: Context-aware goodbye variants."""

    def test_goodbye_booking_done_includes_date(self):
        """booking_done variant includes the date."""
        text = get_goodbye("booking_done", "Salone Mario", date="martedi 15 aprile")
        assert "Salone Mario" in text
        # Date should appear in at least some variants
        # Not all variants include {date}, so we test with multiple tries
        found_date = False
        for _ in range(20):
            t = get_goodbye("booking_done", "Salone Mario", date="martedi 15 aprile")
            if "martedi 15 aprile" in t:
                found_date = True
                break
        assert found_date, "No booking_done variant includes date"

    def test_goodbye_info_only_variant(self):
        """info_only variant returns a valid goodbye."""
        text = get_goodbye("info_only", "Salone Bella Vita")
        assert "Salone Bella Vita" in text
        assert len(text) > 10

    def test_goodbye_generic_variant(self):
        """generic variant always includes business_name."""
        for _ in range(10):
            text = get_goodbye("generic", "Hair Studio")
            assert "Hair Studio" in text

    def test_goodbye_randomness(self):
        """Two calls don't always return the same string."""
        results = set()
        for _ in range(20):
            results.add(get_goodbye("generic", "Test Salon"))
        # With at least 2 variants, 20 tries should produce >1 unique
        assert len(results) > 1, f"Always returned same: {results}"

    def test_all_goodbye_variants_have_business_name(self):
        """Every variant in GOODBYE_VARIANTS uses {business_name} (except escalated)."""
        for context_key, variants in GOODBYE_VARIANTS.items():
            if context_key == "escalated":
                continue  # Escalated doesn't need business_name
            for v in variants:
                assert "{business_name}" in v, \
                    f"GOODBYE_VARIANTS['{context_key}'] variant missing {{business_name}}: {v}"

    def test_unknown_context_falls_back_to_generic(self):
        """Unknown context key falls back to generic."""
        text = get_goodbye("nonexistent_context", "Salone X")
        assert "Salone X" in text

    def test_escalated_no_business_name_needed(self):
        """Escalated goodbye works without business_name in template."""
        text = get_goodbye("escalated", "Salone Y")
        assert isinstance(text, str)
        assert len(text) > 5
