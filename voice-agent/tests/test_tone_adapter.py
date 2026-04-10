"""
Tests for ToneAdapter — B5 Tone Adaptation.

Verifies that Sara adapts her response tone based on caller sentiment.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from tone_adapter import ToneAdapter, ToneMode


class TestToneDefaults:
    """Default state tests."""

    def test_default_tone_is_neutral(self):
        adapter = ToneAdapter()
        assert adapter.current_tone == ToneMode.NEUTRAL

    def test_reset_clears_tone(self):
        adapter = ToneAdapter()
        adapter.update_tone("negative", 3)
        assert adapter.current_tone == ToneMode.EMPATHETIC
        adapter.reset()
        assert adapter.current_tone == ToneMode.NEUTRAL


class TestToneTransitions:
    """Tone mode transition logic."""

    def test_frustrated_caller_triggers_empathetic(self):
        adapter = ToneAdapter()
        tone = adapter.update_tone("negative", 2)
        assert tone == ToneMode.EMPATHETIC

    def test_frustration_level_alone_triggers_empathetic(self):
        """Even neutral sentiment with high frustration -> EMPATHETIC."""
        adapter = ToneAdapter()
        tone = adapter.update_tone("neutral", 3)
        assert tone == ToneMode.EMPATHETIC

    def test_positive_triggers_enthusiastic(self):
        adapter = ToneAdapter()
        tone = adapter.update_tone("positive", 0)
        assert tone == ToneMode.ENTHUSIASTIC

    def test_empathetic_is_sticky(self):
        """EMPATHETIC stays through neutral turns until positive."""
        adapter = ToneAdapter()
        adapter.update_tone("negative", 2)  # -> EMPATHETIC
        assert adapter.current_tone == ToneMode.EMPATHETIC

        adapter.update_tone("neutral", 0)   # -> still EMPATHETIC (sticky)
        assert adapter.current_tone == ToneMode.EMPATHETIC

        adapter.update_tone("neutral", 0)   # -> still EMPATHETIC
        assert adapter.current_tone == ToneMode.EMPATHETIC

        adapter.update_tone("positive", 0)  # -> ENTHUSIASTIC (breaks sticky)
        assert adapter.current_tone == ToneMode.ENTHUSIASTIC

    def test_enthusiastic_decays(self):
        """ENTHUSIASTIC decays back to NEUTRAL after 2 neutral turns."""
        adapter = ToneAdapter()
        adapter.update_tone("positive", 0)  # -> ENTHUSIASTIC, 2 turns remaining
        assert adapter.current_tone == ToneMode.ENTHUSIASTIC

        adapter.update_tone("neutral", 0)   # turn 1 -> ENTHUSIASTIC (1 remaining)
        assert adapter.current_tone == ToneMode.ENTHUSIASTIC

        adapter.update_tone("neutral", 0)   # turn 2 -> NEUTRAL (0 remaining)
        assert adapter.current_tone == ToneMode.NEUTRAL

    def test_enthusiastic_renewed_by_positive(self):
        """A new positive turn resets the 2-turn counter."""
        adapter = ToneAdapter()
        adapter.update_tone("positive", 0)  # ENTHUSIASTIC, 2 turns
        adapter.update_tone("neutral", 0)   # 1 remaining
        adapter.update_tone("positive", 0)  # re-armed, 2 turns
        adapter.update_tone("neutral", 0)   # 1 remaining
        assert adapter.current_tone == ToneMode.ENTHUSIASTIC


class TestNeutralAdaptation:
    """Neutral mode should be pass-through."""

    def test_neutral_no_change(self):
        adapter = ToneAdapter()
        original = "Buongiorno, come posso aiutarla?"
        result = adapter.adapt_response(original, ToneMode.NEUTRAL)
        assert result == original

    def test_neutral_no_change_default(self):
        """Default tone (NEUTRAL) should pass through."""
        adapter = ToneAdapter()
        original = "Perfetto! Ho prenotato per le 15:00."
        result = adapter.adapt_response(original)
        assert result == original


class TestEmpatheticAdaptation:
    """EMPATHETIC mode text transformations."""

    def test_empathetic_strips_exclamations(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Perfetto! Ho prenotato.", ToneMode.EMPATHETIC)
        # Should not contain "!" (replaced with ".")
        assert "!" not in result
        # Should still contain meaningful content
        assert "prenotato" in result

    def test_empathetic_adds_prefix(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Ho prenotato per le 15:00.", ToneMode.EMPATHETIC)
        # Should start with one of the empathy prefixes
        empathy_starts = ["Capisco.", "Ha ragione.", "Mi dispiace.", "Comprendo.", "Mi scusi."]
        assert any(result.startswith(p) for p in empathy_starts), f"Response should start with empathy prefix: {result}"

    def test_empathetic_strips_backchannel(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Perfetto! Procediamo con la prenotazione.", ToneMode.EMPATHETIC)
        # "Perfetto!" backchannel should be stripped
        assert "Perfetto" not in result or "Perfetto." not in result.split(" ", 1)[0]
        assert "prenotazione" in result

    def test_empathetic_strips_fillers(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Allora, procediamo con la prenotazione.", ToneMode.EMPATHETIC)
        # "Allora," should be removed
        assert "Allora" not in result
        assert "prenotazione" in result

    def test_empathetic_shortens_removes_filler_dunque(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Dunque, vediamo gli orari disponibili.", ToneMode.EMPATHETIC)
        assert "Dunque" not in result
        assert "orari disponibili" in result

    def test_empathetic_preserves_questions(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Per quale giorno desidera prenotare?", ToneMode.EMPATHETIC)
        assert "?" in result

    def test_empathetic_prefix_rotates(self):
        """Empathy prefixes should rotate, not repeat the same one."""
        adapter = ToneAdapter()
        results = []
        for _ in range(5):
            r = adapter.adapt_response("Ok.", ToneMode.EMPATHETIC)
            results.append(r)
        # Not all should be identical (prefix rotates)
        assert len(set(results)) > 1, "Empathy prefix should rotate"

    def test_empathetic_empty_response(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("", ToneMode.EMPATHETIC)
        assert result == ""


class TestEnthusiasticAdaptation:
    """ENTHUSIASTIC mode text transformations."""

    def test_enthusiastic_adds_warmth(self):
        adapter = ToneAdapter()
        result = adapter.adapt_response("Ho prenotato per le 15:00.", ToneMode.ENTHUSIASTIC)
        warmth_words = ["Che bello!", "Fantastico!", "Ottimo!", "Benissimo!"]
        assert any(w in result for w in warmth_words), f"Should contain warmth prefix: {result}"

    def test_enthusiastic_skips_already_enthusiastic(self):
        """Don't double-up if response already starts enthusiastically."""
        adapter = ToneAdapter()
        result = adapter.adapt_response("Fantastico, procediamo!", ToneMode.ENTHUSIASTIC)
        # Should not prepend another "Fantastico!"
        assert not result.startswith("Fantastico! Fantastico")
        assert not result.startswith("Ottimo! Fantastico")

    def test_enthusiastic_keeps_energy(self):
        """Enthusiastic mode should preserve existing exclamation marks."""
        adapter = ToneAdapter()
        original = "Ottimo! La prenotazione e' confermata!"
        result = adapter.adapt_response(original, ToneMode.ENTHUSIASTIC)
        assert "!" in result


class TestIntegrationFlow:
    """End-to-end tone adaptation flows."""

    def test_full_frustrated_then_happy_flow(self):
        """Simulates a caller who starts frustrated and ends happy."""
        adapter = ToneAdapter()

        # Turn 1: frustrated
        adapter.update_tone("negative", 3)
        assert adapter.current_tone == ToneMode.EMPATHETIC
        r1 = adapter.adapt_response("Perfetto! Vediamo gli orari.")
        assert "!" not in r1
        assert any(r1.startswith(p) for p in ["Capisco.", "Ha ragione.", "Mi dispiace.", "Comprendo.", "Mi scusi."])

        # Turn 2: still negative
        adapter.update_tone("neutral", 0)
        assert adapter.current_tone == ToneMode.EMPATHETIC  # sticky

        # Turn 3: positive turn breaks empathetic
        adapter.update_tone("positive", 0)
        assert adapter.current_tone == ToneMode.ENTHUSIASTIC

        # Turn 4-5: neutral decays enthusiastic
        adapter.update_tone("neutral", 0)
        assert adapter.current_tone == ToneMode.ENTHUSIASTIC  # 1 left
        adapter.update_tone("neutral", 0)
        assert adapter.current_tone == ToneMode.NEUTRAL  # decayed

    def test_adapt_uses_current_tone_by_default(self):
        """adapt_response with no tone arg uses current_tone."""
        adapter = ToneAdapter()
        adapter.update_tone("negative", 2)
        result = adapter.adapt_response("Grande! Tutto fatto!")
        # Should be empathetic (no "!")
        assert "!" not in result

    def test_multiple_resets(self):
        """Multiple resets should be idempotent."""
        adapter = ToneAdapter()
        adapter.update_tone("negative", 4)
        adapter.reset()
        adapter.reset()
        assert adapter.current_tone == ToneMode.NEUTRAL
