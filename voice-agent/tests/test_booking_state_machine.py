"""
FLUXION Voice Agent - Booking State Machine Tests

Test suite for the booking state machine (Day 6-7):
- Normal booking flow
- State transitions
- Interruption handling
- Entity extraction integration
- Context persistence

Run with: pytest voice-agent/tests/test_booking_state_machine.py -v
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from booking_state_machine import (
    BookingStateMachine,
    BookingState,
    BookingContext,
    StateMachineResult,
    DEFAULT_SERVICES,
)


# =============================================================================
# TEST DATA
# =============================================================================

# Reference date for testing (fixed to avoid flaky tests)
REFERENCE_DATE = datetime(2026, 1, 13, 10, 0, 0)  # Tuesday, January 13, 2026


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_state_machine() -> BookingStateMachine:
    """Create a state machine with fixed reference date."""
    return BookingStateMachine(reference_date=REFERENCE_DATE)


# =============================================================================
# TEST: NORMAL BOOKING FLOW
# =============================================================================

class TestNormalBookingFlow:
    """Test the complete normal booking flow."""

    def test_full_flow_step_by_step(self):
        """Test complete booking flow with separate messages."""
        sm = create_state_machine()

        # Start flow
        result = sm.start_booking_flow()
        assert result.next_state == BookingState.WAITING_SERVICE
        assert "servizio" in result.response.lower()

        # Provide service
        result = sm.process_message("vorrei un taglio")
        assert result.next_state == BookingState.WAITING_DATE
        assert sm.context.service == "taglio"
        assert "giorno" in result.response.lower() or "quando" in result.response.lower()

        # Provide date
        result = sm.process_message("domani")
        assert result.next_state == BookingState.WAITING_TIME
        assert sm.context.date is not None
        assert "ora" in result.response.lower()

        # Provide time
        result = sm.process_message("alle 15")
        assert result.next_state == BookingState.CONFIRMING
        assert sm.context.time == "15:00"
        assert "conferma" in result.response.lower() or "riepilogo" in result.response.lower()

        # Confirm
        result = sm.process_message("sì confermo")
        assert result.next_state == BookingState.COMPLETED
        assert result.booking is not None
        assert result.booking["service"] == "taglio"
        assert result.booking["time"] == "15:00"
        assert result.should_exit is True

    def test_flow_with_all_info_in_one_message(self):
        """Test when user provides all info in one message."""
        sm = create_state_machine()

        # Start flow
        sm.start_booking_flow()

        # Provide everything at once
        result = sm.process_message("vorrei un taglio domani alle 15")

        # Should go directly to confirmation
        assert result.next_state == BookingState.CONFIRMING
        assert sm.context.service == "taglio"
        assert sm.context.time == "15:00"
        assert sm.context.date is not None

    def test_flow_with_service_and_date_in_one_message(self):
        """Test when user provides service and date together."""
        sm = create_state_machine()

        # Start flow
        sm.start_booking_flow()

        # Provide service and date
        result = sm.process_message("taglio per domani")
        assert result.next_state == BookingState.WAITING_TIME
        assert sm.context.service == "taglio"
        assert sm.context.date is not None


# =============================================================================
# TEST: STATE TRANSITIONS
# =============================================================================

class TestStateTransitions:
    """Test state transitions."""

    def test_idle_to_waiting_service(self):
        """Test transition from IDLE to WAITING_SERVICE."""
        sm = create_state_machine()
        result = sm.start_booking_flow()

        assert sm.context.state == BookingState.WAITING_SERVICE
        assert result.next_state == BookingState.WAITING_SERVICE

    def test_waiting_service_to_waiting_date(self):
        """Test transition after providing service."""
        sm = create_state_machine()
        sm.start_booking_flow()

        result = sm.process_message("voglio fare il colore")

        assert sm.context.state == BookingState.WAITING_DATE
        assert sm.context.service == "colore"

    def test_waiting_date_to_waiting_time(self):
        """Test transition after providing date."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("piega")

        result = sm.process_message("lunedì prossimo")

        assert sm.context.state == BookingState.WAITING_TIME
        assert sm.context.date is not None

    def test_waiting_time_to_confirming(self):
        """Test transition after providing time."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")

        result = sm.process_message("alle 10 e mezza")

        assert sm.context.state == BookingState.CONFIRMING
        assert sm.context.time == "10:30"

    def test_confirming_to_completed(self):
        """Test confirmation leads to COMPLETED."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")

        result = sm.process_message("sì va bene")

        assert sm.context.state == BookingState.COMPLETED
        assert result.booking is not None

    def test_confirming_to_cancelled(self):
        """Test rejection leads to CANCELLED."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")

        result = sm.process_message("no annulla")

        assert sm.context.state == BookingState.CANCELLED
        assert result.booking is None


# =============================================================================
# TEST: INTERRUPTION HANDLING
# =============================================================================

class TestInterruptionHandling:
    """Test interruption handling patterns."""

    def test_reset_interruption(self):
        """Test 'ricominciamo' resets the flow."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("colore")
        sm.process_message("domani")

        # User wants to restart
        result = sm.process_message("no aspetta, ricominciamo")

        assert sm.context.state == BookingState.WAITING_SERVICE
        assert sm.context.service is None
        assert sm.context.date is None
        assert sm.context.was_interrupted is False  # Reset clears the flag

    def test_annulla_tutto_interruption(self):
        """Test 'annulla tutto' resets the flow."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio domani alle 15")

        result = sm.process_message("annulla tutto")

        assert sm.context.state == BookingState.WAITING_SERVICE

    def test_change_acknowledgement(self):
        """Test 'aspetta' soft interruption."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")

        result = sm.process_message("aspetta un attimo")

        # Should acknowledge but stay in same state
        assert "cambiare" in result.response.lower() or "dica" in result.response.lower()

    def test_operator_escalation(self):
        """Test 'operatore' triggers escalation."""
        sm = create_state_machine()
        sm.start_booking_flow()

        result = sm.process_message("voglio parlare con un operatore")

        assert result.should_exit is True
        assert result.lookup_type == "operator_escalation"

    def test_basta_escalation(self):
        """Test 'basta' triggers escalation."""
        sm = create_state_machine()
        sm.start_booking_flow()

        result = sm.process_message("basta non capisco")

        assert result.should_exit is True


# =============================================================================
# TEST: CONFIRMATION CHANGES
# =============================================================================

class TestConfirmationChanges:
    """Test changing info during confirmation."""

    def test_change_service_during_confirmation(self):
        """Test changing service when in CONFIRMING state."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")

        # Now in CONFIRMING, want to change service
        result = sm.process_message("cambio servizio")

        assert sm.context.state == BookingState.WAITING_SERVICE
        assert sm.context.service is None

    def test_change_date_during_confirmation(self):
        """Test changing date when in CONFIRMING state."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")

        result = sm.process_message("cambio giorno")

        assert sm.context.state == BookingState.WAITING_DATE
        assert sm.context.date is None

    def test_change_time_during_confirmation(self):
        """Test changing time when in CONFIRMING state."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")

        result = sm.process_message("cambio orario")

        assert sm.context.state == BookingState.WAITING_TIME
        assert sm.context.time is None


# =============================================================================
# TEST: ENTITY EXTRACTION INTEGRATION
# =============================================================================

class TestEntityExtractionIntegration:
    """Test integration with entity extractor."""

    def test_service_synonyms(self):
        """Test service synonym recognition."""
        sm = create_state_machine()
        sm.start_booking_flow()

        test_cases = [
            ("vorrei una sforbiciata", "taglio"),
            ("devo fare la tinta", "colore"),
            ("messa in piega", "piega"),
            ("rasatura", "barba"),
        ]

        for text, expected_service in test_cases:
            sm.reset()
            sm.start_booking_flow()
            sm.process_message(text)
            assert sm.context.service == expected_service, f"Failed for '{text}'"

    def test_date_extraction_in_flow(self):
        """Test date extraction during booking flow."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")

        # Test various date formats
        result = sm.process_message("dopodomani")
        assert sm.context.date is not None
        expected_date = (REFERENCE_DATE + timedelta(days=2)).strftime("%Y-%m-%d")
        assert sm.context.date == expected_date

    def test_time_extraction_in_flow(self):
        """Test time extraction during booking flow."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")

        result = sm.process_message("alle 9 e mezza")
        assert sm.context.time == "09:30"

    def test_approximate_time_handling(self):
        """Test approximate time (pomeriggio, mattina)."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")

        result = sm.process_message("di pomeriggio")
        assert sm.context.time == "15:00"
        assert sm.context.time_is_approximate is True

    def test_name_extraction(self):
        """Test client name extraction."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME

        result = sm.process_message("mi chiamo Laura Bianchi")
        assert sm.context.client_name == "Laura Bianchi"


# =============================================================================
# TEST: CONTEXT PERSISTENCE
# =============================================================================

class TestContextPersistence:
    """Test context serialization and deserialization."""

    def test_context_to_json(self):
        """Test context serialization to JSON."""
        ctx = BookingContext(
            state=BookingState.WAITING_DATE,
            service="taglio",
            service_display="Taglio",
            client_name="Mario",
            turns_count=3
        )

        json_str = ctx.to_json()
        data = json.loads(json_str)

        assert data["state"] == "waiting_date"
        assert data["service"] == "taglio"
        assert data["client_name"] == "Mario"
        assert data["turns_count"] == 3

    def test_context_from_json(self):
        """Test context deserialization from JSON."""
        json_str = json.dumps({
            "state": "confirming",
            "service": "colore",
            "service_display": "Colore",
            "date": "2026-01-15",
            "date_display": "mercoledì 15 gennaio",
            "time": "10:00",
            "time_display": "alle 10:00",
            "client_name": "Anna",
            "client_id": None,
            "client_phone": None,
            "client_email": None,
            "operator_id": None,
            "operator_name": None,
            "operator_requested": False,
            "notes": None,
            "created_at": None,
            "updated_at": None,
            "turns_count": 5,
            "time_is_approximate": False,
            "was_interrupted": False,
            "previous_state": None
        })

        ctx = BookingContext.from_json(json_str)

        assert ctx.state == BookingState.CONFIRMING
        assert ctx.service == "colore"
        assert ctx.date == "2026-01-15"
        assert ctx.time == "10:00"
        assert ctx.client_name == "Anna"

    def test_context_roundtrip(self):
        """Test context serialization roundtrip."""
        original = BookingContext(
            state=BookingState.WAITING_TIME,
            service="piega",
            date="2026-01-20",
            client_name="Giuseppe",
            turns_count=4
        )

        json_str = original.to_json()
        restored = BookingContext.from_json(json_str)

        assert restored.state == original.state
        assert restored.service == original.service
        assert restored.date == original.date
        assert restored.client_name == original.client_name

    def test_resume_from_context(self):
        """Test resuming state machine from saved context."""
        # Create and save context
        ctx = BookingContext(
            state=BookingState.WAITING_TIME,
            service="taglio",
            service_display="Taglio",
            date="2026-01-15",
            date_display="mercoledì 15 gennaio"
        )

        # Create new state machine and restore context
        sm = create_state_machine()
        sm.set_context(ctx)

        # Process should continue from WAITING_TIME
        result = sm.process_message("alle 16")

        assert sm.context.state == BookingState.CONFIRMING
        assert sm.context.time == "16:00"


# =============================================================================
# TEST: CONTEXT METHODS
# =============================================================================

class TestContextMethods:
    """Test BookingContext utility methods."""

    def test_get_summary(self):
        """Test summary generation."""
        ctx = BookingContext(
            service="taglio",
            service_display="Taglio",
            date="2026-01-15",
            date_display="mercoledì 15 gennaio",
            time="10:00",
            time_display="alle 10:00"
        )

        summary = ctx.get_summary()
        assert "Taglio" in summary
        assert "15 gennaio" in summary
        assert "10:00" in summary

    def test_get_summary_with_operator(self):
        """Test summary with operator."""
        ctx = BookingContext(
            service_display="Colore",
            date_display="domani",
            time_display="alle 15:00",
            operator_name="Maria"
        )

        summary = ctx.get_summary()
        assert "Maria" in summary

    def test_is_complete(self):
        """Test completeness check."""
        ctx = BookingContext()
        assert ctx.is_complete() is False

        ctx.service = "taglio"
        assert ctx.is_complete() is False

        ctx.date = "2026-01-15"
        assert ctx.is_complete() is False

        ctx.time = "10:00"
        assert ctx.is_complete() is True

    def test_get_missing_fields(self):
        """Test missing fields detection."""
        ctx = BookingContext()
        missing = ctx.get_missing_fields()
        assert "servizio" in missing
        assert "data" in missing
        assert "ora" in missing

        ctx.service = "taglio"
        missing = ctx.get_missing_fields()
        assert "servizio" not in missing
        assert "data" in missing

    def test_to_dict(self):
        """Test dictionary conversion."""
        ctx = BookingContext(
            state=BookingState.CONFIRMING,
            service="taglio",
            client_name="Mario",
            client_id="123",
            turns_count=5
        )

        d = ctx.to_dict()
        assert d["state"] == "confirming"
        assert d["client"]["name"] == "Mario"
        assert d["client"]["id"] == "123"
        assert d["booking"]["service"] == "taglio"
        assert d["turns"] == 5


# =============================================================================
# TEST: INITIAL CONTEXT
# =============================================================================

class TestInitialContext:
    """Test starting flow with pre-populated context."""

    def test_start_with_client_name(self):
        """Test starting flow with known client."""
        sm = create_state_machine()
        result = sm.start_booking_flow({"client_name": "Mario Rossi"})

        assert sm.context.client_name == "Mario Rossi"
        # Should still ask for service
        assert result.next_state == BookingState.WAITING_SERVICE

    def test_start_with_service(self):
        """Test starting flow with known service."""
        sm = create_state_machine()
        result = sm.start_booking_flow({"service": "taglio"})

        assert sm.context.service == "taglio"
        # Should skip to asking for date
        assert result.next_state == BookingState.WAITING_DATE


# =============================================================================
# TEST: ERROR HANDLING
# =============================================================================

class TestErrorHandling:
    """Test error cases and recovery."""

    def test_unknown_service(self):
        """Test handling of unknown service."""
        sm = create_state_machine()
        sm.start_booking_flow()

        result = sm.process_message("vorrei un massaggio")  # Not in default services

        assert sm.context.state == BookingState.WAITING_SERVICE
        assert "non ho capito" in result.response.lower() or "scegliere" in result.response.lower()

    def test_invalid_date(self):
        """Test handling of unrecognized date."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")

        result = sm.process_message("il giorno blu")

        assert sm.context.state == BookingState.WAITING_DATE
        assert sm.context.date is None

    def test_invalid_time(self):
        """Test handling of unrecognized time."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")

        result = sm.process_message("quando capita")

        assert sm.context.state == BookingState.WAITING_TIME
        assert sm.context.time is None

    def test_recovery_after_error(self):
        """Test recovery after providing invalid then valid input."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")

        # Invalid date
        result = sm.process_message("xyz")
        assert sm.context.state == BookingState.WAITING_DATE

        # Valid date
        result = sm.process_message("domani")
        assert sm.context.state == BookingState.WAITING_TIME
        assert sm.context.date is not None


# =============================================================================
# TEST: CONFIRMATION VARIATIONS
# =============================================================================

class TestConfirmationVariations:
    """Test various confirmation phrases."""

    def test_affirmative_responses(self):
        """Test various 'yes' responses."""
        affirmatives = [
            "sì",
            "si",
            "ok",
            "va bene",
            "d'accordo",
            "confermo",
            "perfetto",
            "certo",
        ]

        for response in affirmatives:
            sm = create_state_machine()
            sm.start_booking_flow()
            sm.process_message("taglio domani alle 15")

            result = sm.process_message(response)
            assert result.next_state == BookingState.COMPLETED, f"Failed for '{response}'"

    def test_negative_responses(self):
        """Test various 'no' responses."""
        negatives = [
            "no",
            "no grazie",
            "annulla",
            "non voglio",
        ]

        for response in negatives:
            sm = create_state_machine()
            sm.start_booking_flow()
            sm.process_message("taglio domani alle 15")

            result = sm.process_message(response)
            assert result.next_state == BookingState.CANCELLED, f"Failed for '{response}'"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
