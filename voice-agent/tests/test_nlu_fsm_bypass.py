"""Regression tests for FX-U3-NLU-FSM-BYPASS-002.

The primary LLM NLU is useful while intent discovery is still required, but it is
pure overhead once the booking FSM owns the next turn deterministically.  These
tests exercise the real ``VoiceOrchestrator.process`` scheduling point with a
minimal in-memory orchestrator so no Groq, HTTP bridge, SQLite, TTS engine, SIP,
or WhatsApp service is contacted.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import sys

import pytest


VOICE_AGENT_ROOT = Path(__file__).resolve().parents[1]
if str(VOICE_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(VOICE_AGENT_ROOT))

from src import orchestrator as orchestrator_mod  # noqa: E402
from src.booking_state_machine import BookingState  # noqa: E402
from src.intent_classifier import IntentCategory  # noqa: E402


FSM_OWNED_STATES = (
    BookingState.WAITING_NAME,
    BookingState.WAITING_SURNAME,
    BookingState.CONFIRMING_NAME,
    BookingState.CONFIRMING_PHONE,
    BookingState.PROPOSE_REGISTRATION,
    BookingState.REGISTERING_SURNAME,
    BookingState.REGISTERING_PHONE,
    BookingState.WAITING_DATE,
    BookingState.WAITING_TIME,
    BookingState.CONFIRMING,
    BookingState.DISAMBIGUATING_NAME,
)

LLM_PRESERVED_STATES = (
    BookingState.IDLE,
    BookingState.WAITING_SERVICE,
)


class _Context(SimpleNamespace):
    def to_dict(self):
        return {"state": self.state.value if self.state else None}


def _make_orchestrator(state: BookingState):
    """Build only the attributes touched by process() on a fast local path."""
    orch = orchestrator_mod.VoiceOrchestrator.__new__(orchestrator_mod.VoiceOrchestrator)

    context = _Context(
        state=state,
        client_name=None,
        client_surname=None,
        service=None,
        date=None,
        time=None,
        operator_gender_preference="any",
        alternative_slots=[],
    )
    orch.booking_sm = SimpleNamespace(context=context)

    orch._llm_nlu = SimpleNamespace(extract=AsyncMock(return_value=None))
    orch._current_session = SimpleNamespace(session_id="u3-test-session", total_turns=1)
    orch.session_manager = MagicMock()
    orch.tts = SimpleNamespace(synthesize=AsyncMock(return_value=b""))
    orch.prosody = SimpleNamespace(inject=lambda text, context=None: text)

    orch.verticale_id = "salone"
    orch._faq_vertical = "salone"
    orch.business_name = "Test FLUXION"

    orch.sentiment = None
    orch.backchannel = None
    orch.tone_adapter = None
    orch.guided_engine = None
    orch.faq_manager = None

    orch._pending_package_proposal = False
    orch._pending_rebook_after_cancel = False
    orch._pending_cancel = False
    orch._pending_reschedule = False
    orch._last_booking_data = None
    orch._whatsapp_sent = False
    orch._time_pressure = False
    orch._session_states = {}

    return orch


@pytest.fixture(autouse=True)
def _disable_optional_prefilters(monkeypatch):
    """Keep the test on the NLU scheduling path only, without external setup."""
    monkeypatch.setattr(orchestrator_mod, "HAS_ITALIAN_REGEX", False)
    monkeypatch.setattr(orchestrator_mod, "HAS_VERTICAL_ENTITIES", False)


@pytest.mark.asyncio
@pytest.mark.parametrize("state", FSM_OWNED_STATES, ids=lambda state: state.value)
async def test_primary_llm_nlu_is_not_started_in_fsm_owned_states(state):
    orch = _make_orchestrator(state)

    result = await orch.process("aiuto")

    assert result.response
    orch._llm_nlu.extract.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("state", LLM_PRESERVED_STATES, ids=lambda state: state.value)
async def test_primary_llm_nlu_is_preserved_where_intent_discovery_is_needed(state):
    orch = _make_orchestrator(state)

    result = await orch.process("aiuto")

    assert result.response
    orch._llm_nlu.extract.assert_called_once()


@pytest.mark.asyncio
async def test_waiting_date_uses_existing_regex_cache_fallback(monkeypatch):
    orch = _make_orchestrator(BookingState.WAITING_DATE)
    fallback_result = SimpleNamespace(
        intent="thanks",
        category=IntentCategory.CORTESIA,
        confidence=1.0,
        response="Prego!",
    )
    cached_intent = MagicMock(return_value=fallback_result)
    monkeypatch.setattr(orchestrator_mod, "get_cached_intent", cached_intent)

    result = await orch.process("grazie")

    orch._llm_nlu.extract.assert_not_called()
    cached_intent.assert_called()
    assert result.response
