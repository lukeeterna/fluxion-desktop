"""
Tests for FLUXION Voice Agent - Backchannel Engine

Validates backchannel injection rules:
- When to inject (FSM state, turn count, sentiment)
- What to inject (context-appropriate phrases)
- Anti-duplication with main response
"""

import sys
import os
import pytest

# Add voice-agent/src to path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from backchannel_engine import (
    BackchannelEngine,
    BACKCHANNELS,
    _COOLDOWN_TURNS,
    _LONG_INPUT_THRESHOLD,
)


@pytest.fixture
def engine():
    return BackchannelEngine()


class TestShouldBackchannel:
    """Tests for should_backchannel() decision logic."""

    def test_should_backchannel_after_name(self, engine):
        """After user provides name in WAITING_NAME state, backchannel is appropriate."""
        engine.tick()  # simulate first turn passed
        result = engine.should_backchannel(
            user_input="Mi chiamo Marco Rossi",
            intent="booking",
            fsm_state="waiting_name",
        )
        assert result is True

    def test_should_backchannel_after_date(self, engine):
        """After user provides date info."""
        engine.tick()
        result = engine.should_backchannel(
            user_input="Giovedi prossimo",
            intent="booking",
            fsm_state="waiting_date",
        )
        assert result is True

    def test_should_backchannel_after_confirm(self, engine):
        """After user confirms something."""
        engine.tick()
        result = engine.should_backchannel(
            user_input="Si confermo",
            intent="booking",
            fsm_state="confirming",
        )
        assert result is True

    def test_no_backchannel_on_greeting(self, engine):
        """First turn (greeting) should never have backchannel."""
        result = engine.should_backchannel(
            user_input="Buongiorno",
            intent="cortesia",
            fsm_state="idle",
            is_first_turn=True,
        )
        assert result is False

    def test_no_backchannel_on_first_turn_counter_zero(self, engine):
        """Turn counter at 0 means first turn -- no backchannel."""
        result = engine.should_backchannel(
            user_input="Vorrei prenotare un taglio",
            intent="booking",
            fsm_state="waiting_name",
        )
        assert result is False

    def test_no_backchannel_when_frustrated(self, engine):
        """Negative sentiment should suppress backchannel."""
        engine.tick()
        result = engine.should_backchannel(
            user_input="Non funziona niente!",
            intent="escalation",
            fsm_state="waiting_service",
            sentiment="negative",
        )
        assert result is False

    def test_no_backchannel_when_angry(self, engine):
        """Angry sentiment should suppress backchannel."""
        engine.tick()
        result = engine.should_backchannel(
            user_input="Ma insomma!",
            intent="escalation",
            fsm_state="waiting_service",
            sentiment="angry",
        )
        assert result is False

    def test_backchannel_cooldown(self, engine):
        """Max 1 backchannel per COOLDOWN_TURNS turns."""
        # Turn 1: tick so we're past first turn
        engine.tick()
        # Should backchannel on first eligible turn
        assert engine.should_backchannel("Marco", "booking", "waiting_name") is True
        # Consume the backchannel
        engine.get_backchannel("info_provided")

        # Turns 2 through COOLDOWN: should be suppressed
        for i in range(_COOLDOWN_TURNS - 1):
            engine.tick()
            assert engine.should_backchannel(
                "qualcosa", "booking", "waiting_date"
            ) is False, f"Should be on cooldown at turn offset {i+1}"

        # After cooldown: should be allowed again
        engine.tick()
        assert engine.should_backchannel("Lunedi", "booking", "waiting_date") is True

    def test_no_backchannel_idle_short_input(self, engine):
        """Idle state with short input should not trigger backchannel."""
        engine.tick()
        result = engine.should_backchannel(
            user_input="ciao",
            intent="cortesia",
            fsm_state="idle",
        )
        assert result is False

    def test_backchannel_long_input(self, engine):
        """Long user input should trigger backchannel regardless of FSM state."""
        engine.tick()
        long_text = "Vorrei sapere se e' possibile prenotare un appuntamento per la prossima settimana, preferibilmente il martedi o il mercoledi"
        assert len(long_text) >= _LONG_INPUT_THRESHOLD
        result = engine.should_backchannel(
            user_input=long_text,
            intent="info",
            fsm_state="idle",
        )
        assert result is True


class TestGetBackchannel:
    """Tests for get_backchannel() phrase selection."""

    def test_backchannel_phrases_not_empty(self):
        """Each context must have at least 2 phrases for variety."""
        for context, phrases in BACKCHANNELS.items():
            assert len(phrases) >= 2, f"Context '{context}' has < 2 phrases"

    def test_get_backchannel_returns_string(self, engine):
        """get_backchannel must return a non-empty string."""
        engine.tick()
        result = engine.get_backchannel("info_provided")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_backchannel_from_each_context(self, engine):
        """Each context key returns a valid phrase."""
        for context in BACKCHANNELS:
            engine._last_backchannel_turn = -10  # reset cooldown
            result = engine.get_backchannel(context)
            assert result in BACKCHANNELS[context], f"'{result}' not in pool for '{context}'"

    def test_backchannel_context_selection_info(self, engine):
        """info_provided context returns from info pool."""
        engine.tick()
        result = engine.get_backchannel("info_provided")
        assert result in BACKCHANNELS["info_provided"]

    def test_backchannel_context_selection_confirmed(self, engine):
        """confirmed context returns from confirmed pool."""
        engine.tick()
        result = engine.get_backchannel("confirmed")
        assert result in BACKCHANNELS["confirmed"]

    def test_backchannel_never_duplicates_response(self, engine):
        """Backchannel must not start with the same word as the response."""
        engine.tick()
        # "Perfetto" is in the info_provided pool -- response starts with "Perfetto"
        # Run multiple times to increase chance of catching duplicates
        for _ in range(20):
            engine._last_backchannel_turn = -10
            bc = engine.get_backchannel("info_provided", response="Perfetto, ho trovato Marco Rossi!")
            assert bc.split()[0].rstrip(",.!") != "Perfetto", \
                f"Backchannel '{bc}' duplicates response start 'Perfetto'"

    def test_backchannel_fallback_when_all_filtered(self, engine):
        """If all phrases would duplicate, fall back to full pool."""
        # Create a scenario where filtering could remove everything
        # "info_provided" has Ok, Perfetto, Benissimo, Capito
        # Response starting with a non-pool word should work fine
        engine.tick()
        bc = engine.get_backchannel("info_provided", response="Allora, dimmi il nome")
        assert bc in BACKCHANNELS["info_provided"]

    def test_unknown_context_falls_back(self, engine):
        """Unknown context key falls back to info_provided."""
        engine.tick()
        result = engine.get_backchannel("nonexistent_context")
        assert result in BACKCHANNELS["info_provided"]


class TestClassifyContext:
    """Tests for classify_context() mapping."""

    def test_classify_confirm_state(self, engine):
        assert engine.classify_context("confirming", "si") == "confirmed"

    def test_classify_info_state(self, engine):
        assert engine.classify_context("waiting_name", "Marco") == "info_provided"

    def test_classify_long_input(self, engine):
        long_text = "x" * _LONG_INPUT_THRESHOLD
        assert engine.classify_context("idle", long_text) == "long_input"

    def test_classify_default(self, engine):
        assert engine.classify_context("idle", "ciao") == "info_provided"


class TestTickAndReset:
    """Tests for tick() and reset() lifecycle."""

    def test_tick_increments_counter(self, engine):
        assert engine._turn_counter == 0
        engine.tick()
        assert engine._turn_counter == 1
        engine.tick()
        assert engine._turn_counter == 2

    def test_reset_clears_state(self, engine):
        engine.tick()
        engine.tick()
        engine.tick()
        engine.get_backchannel("info_provided")
        # Verify state is dirty
        assert engine._turn_counter == 3
        assert engine._last_backchannel_turn == 3

        engine.reset()

        assert engine._turn_counter == 0
        assert engine._last_backchannel_turn < 0  # allows first backchannel

    def test_reset_allows_backchannel_after_tick(self, engine):
        """After reset + tick, backchannel should be allowed."""
        engine.reset()
        engine.tick()
        result = engine.should_backchannel("Marco", "booking", "waiting_name")
        assert result is True
