"""
FLUXION Voice Agent - Booking date-integrity regression suite.

Locks two invariants of the FSM's booking-date write path
(``booking_state_machine.py``):

Guard 1 (``_set_context_date``, the single chokepoint): the ISO date stored
in ``context.date`` after a fresh WAITING_DATE turn matches, character for
character, the ISO date the canonical entity extractor resolves for the
same text/reference, and no out-of-horizon date can ever be written.

Guard 2 (correction-rejection callers): rejecting a date-correction attempt
while ``context.date`` already holds a previously-accepted value must clear
that stale value, so the caller's next valid date is actually captured
instead of being silently discarded in favor of the old one.

All dates are derived from ``datetime.now()`` captured once per test --
never a hardcoded year -- so this suite does not age out.

Run with: pytest voice-agent/tests/test_booking_date_integrity.py -v
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from booking_state_machine import BookingStateMachine, BookingState
from entity_extractor import extract_date
from availability_checker import AvailabilityConfig


# =============================================================================
# HELPERS
# =============================================================================

def _setup_at_waiting_date(reference: datetime) -> BookingStateMachine:
    """Create a state machine at WAITING_DATE with a service already selected."""
    sm = BookingStateMachine(reference_date=reference)
    sm.context.state = BookingState.WAITING_DATE
    sm.context.client_name = "Gino"
    sm.context.client_id = "123"
    sm.context.service = "taglio"
    sm.context.services = ["taglio"]
    sm.context.service_display = "Taglio"
    return sm


def _drive_to_confirming(reference: datetime):
    """Drive a fresh SM through 'lunedi prossimo' + 'alle 10' to CONFIRMING."""
    sm = _setup_at_waiting_date(reference)

    r1 = sm.process_message("lunedi prossimo")
    assert r1.next_state == BookingState.WAITING_TIME, (
        f"setup precondition failed: expected WAITING_TIME, got {r1.next_state}"
    )

    r2 = sm.process_message("alle 10")
    assert r2.next_state == BookingState.CONFIRMING, (
        f"setup precondition failed: expected CONFIRMING, got {r2.next_state}"
    )

    accepted_date = sm.context.date
    assert accepted_date is not None, "setup precondition failed: no date accepted"
    return sm, accepted_date


class _StubGroqNLU:
    """Minimal groq_nlu stand-in exposing only extract_confirming()."""

    def __init__(self, campo_corretto: str, nuovo_valore: str):
        self._campo_corretto = campo_corretto
        self._nuovo_valore = nuovo_valore

    def extract_confirming(self, utterance, servizio, data, ora):
        return {
            "decisione": "correzione",
            "campo_corretto": self._campo_corretto,
            "nuovo_valore": self._nuovo_valore,
        }


# =============================================================================
# GUARD 1 -- FSM date-write horizon/identity guard (_set_context_date)
# =============================================================================

class TestGuard1DateWriteChokepoint:

    def test_row1_narrow_scenario_matches_extractor_and_stays_in_horizon(self):
        """'lunedi prossimo' from a fresh WAITING_DATE: FSM date == extractor date."""
        reference = datetime.now()
        sm = _setup_at_waiting_date(reference)

        extractor_result = extract_date("lunedi prossimo", reference)
        assert extractor_result is not None
        expected_iso = extractor_result.to_string("%Y-%m-%d")

        result = sm.process_message("lunedi prossimo")

        assert sm.context.date == expected_iso
        assert result.next_state == BookingState.WAITING_TIME

        max_advance_days = AvailabilityConfig.for_vertical(sm.context.vertical).max_advance_days
        days_ahead = (datetime.strptime(expected_iso, "%Y-%m-%d").date() - reference.date()).days
        assert 0 <= days_ahead <= max_advance_days

    def test_row2_setter_rejects_out_of_horizon_and_leaves_date_untouched(self):
        """A synthetic out-of-horizon ISO date must never become context.date."""
        reference = datetime.now()
        sm = _setup_at_waiting_date(reference)
        max_advance_days = AvailabilityConfig.for_vertical(sm.context.vertical).max_advance_days
        out_of_horizon = (reference + timedelta(days=max_advance_days + 30)).strftime("%Y-%m-%d")

        assert sm.context.date is None

        accepted = sm._set_context_date(out_of_horizon, origin="test_guard1_row2")

        assert accepted is False
        assert sm.context.date is None


# =============================================================================
# GUARD 2 -- Correction-rejection must clear stale date
# =============================================================================

class TestGuard2CorrectionRejectionClearsStaleDate:
    """Rejecting a date correction must never leave a stale context.date behind."""

    def test_row1_confirming_level1_entity_correction_rejection(self):
        """CONFIRMING + out-of-horizon correction, then a new valid date must win."""
        reference = datetime.now()
        sm, accepted_date = _drive_to_confirming(reference)

        reject = sm.process_message("tra 90 giorni")
        assert reject.next_state == BookingState.WAITING_DATE
        assert sm.context.date is None, "stale date must be cleared on rejected correction"
        assert sm.context.date_display is None

        expected_new_iso = extract_date("dopodomani", reference).to_string("%Y-%m-%d")
        result = sm.process_message("dopodomani")

        assert sm.context.date == expected_new_iso
        assert sm.context.date != accepted_date
        assert result.next_state == BookingState.CONFIRMING

    def test_row2_backtrack_trigger_correction_rejection(self):
        """Backtrack correction ('no, volevo...') to an out-of-horizon date must clear stale state."""
        reference = datetime.now()
        sm, accepted_date = _drive_to_confirming(reference)

        reject = sm.process_message("no, volevo tra 90 giorni")
        assert reject.next_state == BookingState.WAITING_DATE
        assert sm.context.date is None, "stale date must be cleared on rejected correction"
        assert sm.context.date_display is None

        expected_new_iso = extract_date("dopodomani", reference).to_string("%Y-%m-%d")
        result = sm.process_message("dopodomani")

        assert sm.context.date == expected_new_iso
        assert sm.context.date != accepted_date
        assert result.next_state == BookingState.CONFIRMING

    def test_row3_groq_fallback_correction_rejection(self):
        """Groq-fallback correction (campo_corretto='data') to an out-of-horizon date must clear stale state."""
        reference = datetime.now()
        sm, accepted_date = _drive_to_confirming(reference)
        sm.groq_nlu = _StubGroqNLU(campo_corretto="data", nuovo_valore="tra 90 giorni")

        reject = sm.process_message("mah")
        assert reject.next_state == BookingState.WAITING_DATE
        assert sm.context.date is None, "stale date must be cleared on rejected correction"
        assert sm.context.date_display is None

        expected_new_iso = extract_date("dopodomani", reference).to_string("%Y-%m-%d")
        result = sm.process_message("dopodomani")

        assert sm.context.date == expected_new_iso
        assert sm.context.date != accepted_date
        assert result.next_state == BookingState.CONFIRMING
