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
        assert "aiutarla" in result.response.lower() or "trattamento" in result.response.lower()

        # Provide service
        result = sm.process_message("vorrei un taglio")
        assert result.next_state == BookingState.WAITING_DATE
        assert sm.context.service == "taglio"
        assert "giorno" in result.response.lower() or "quando" in result.response.lower()

        # Provide date
        result = sm.process_message("domani")
        assert result.next_state == BookingState.WAITING_TIME
        assert sm.context.date is not None
        assert "ora" in result.response.lower() or "comodo" in result.response.lower()

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
        """Test client name extraction (B7: auto-split name/surname)."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME

        result = sm.process_message("mi chiamo Laura Bianchi")
        assert sm.context.client_name == "Laura"
        assert sm.context.client_surname == "Bianchi"


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
        assert "capire" in result.response.lower() or "trattamento" in result.response.lower()

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
# BUG REGRESSION TESTS (Gino conversation)
# =============================================================================

class TestBugRegression:
    """Regression tests for bugs found during Gino live conversation."""

    # --- BUG 1: Registration summary loses first name ---

    def test_bug1_surname_does_not_overwrite_name(self):
        """BUG 1: 'Di Nanni' in REGISTERING_SURNAME must NOT overwrite client_name 'Gino'."""
        sm = create_state_machine()
        sm.context.client_name = "Gino"
        sm.context.is_new_client = True
        sm.context.state = BookingState.REGISTERING_SURNAME

        result = sm.process_message("Di Nanni")

        assert sm.context.client_name == "Gino", f"client_name was overwritten to '{sm.context.client_name}'"
        assert sm.context.client_surname is not None, "client_surname not set"
        assert "nanni" in sm.context.client_surname.lower(), f"client_surname wrong: '{sm.context.client_surname}'"

    def test_bug1_surname_single_word_preserved(self):
        """Single-word surname preserves existing client_name."""
        sm = create_state_machine()
        sm.context.client_name = "Marco"
        sm.context.state = BookingState.REGISTERING_SURNAME

        sm.process_message("Rossi")
        assert sm.context.client_name == "Marco"
        assert sm.context.client_surname == "Rossi"

    def test_bug1_full_name_repeat_works(self):
        """If user repeats full name 'Gino Di Nanni', both are set correctly."""
        sm = create_state_machine()
        sm.context.client_name = "Gino"
        sm.context.state = BookingState.REGISTERING_SURNAME

        sm.process_message("Gino Di Nanni")
        assert sm.context.client_name == "Gino"
        assert "nanni" in sm.context.client_surname.lower()

    def test_bug1_registration_confirm_shows_full_name(self):
        """Registration flow: surname → phone → phone confirmation."""
        sm = create_state_machine()
        sm.context.client_name = "Gino"
        sm.context.is_new_client = True
        sm.context.state = BookingState.REGISTERING_SURNAME

        # Provide surname
        result = sm.process_message("Di Nanni")
        assert sm.context.state == BookingState.REGISTERING_PHONE

        # Provide phone → goes to CONFIRMING_PHONE (phone confirmation step)
        result = sm.process_message("333 1234567")
        assert sm.context.state == BookingState.CONFIRMING_PHONE
        assert "3331234567" in result.response or "333" in result.response

    # --- BUG 2: Multi-service ignored ---

    def test_bug2_multi_service_extraction(self):
        """'taglio e barba' must extract both services."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_SERVICE

        result = sm.process_message("taglio e barba")
        assert sm.context.services is not None
        assert len(sm.context.services) >= 2, f"Expected >=2 services, got {sm.context.services}"
        assert "taglio" in sm.context.services
        assert "barba" in sm.context.services

    def test_bug2_service_display_shows_both(self):
        """service_display must show 'Taglio e Barba', not just 'Taglio'."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_SERVICE

        sm.process_message("taglio e barba")
        assert sm.context.service_display is not None
        assert "Taglio" in sm.context.service_display
        assert "Barba" in sm.context.service_display

    def test_bug2_booking_includes_services(self):
        """Booking dict must include services (plural) and service_display."""
        sm = create_state_machine()
        sm.context.client_name = "Test"
        sm.context.client_id = "1"

        # Build a complete booking with multi-service
        sm.context.state = BookingState.WAITING_SERVICE
        sm.process_message("taglio e barba")
        sm.process_message("domani")
        sm.process_message("alle 15")
        result = sm.process_message("confermo")

        assert result.booking is not None, "No booking object created"
        assert result.booking.get("services") is not None, "services not in booking"
        assert len(result.booking["services"]) >= 2
        assert result.booking.get("service_display") is not None

    # --- BUG 4: Session resets after booking ---

    def test_bug4_reset_for_new_booking_preserves_client(self):
        """reset_for_new_booking preserves client info but clears booking info."""
        sm = create_state_machine()
        sm.context.client_id = "123"
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Di Nanni"
        sm.context.client_phone = "333123456"
        sm.context.service = "taglio"
        sm.context.date = "2026-01-15"
        sm.context.time = "15:00"

        sm.reset_for_new_booking()

        # Client info preserved
        assert sm.context.client_id == "123"
        assert sm.context.client_name == "Gino"
        assert sm.context.client_surname == "Di Nanni"
        assert sm.context.client_phone == "333123456"
        # Booking info cleared
        assert sm.context.service is None
        assert sm.context.date is None
        assert sm.context.time is None
        assert sm.context.state == BookingState.IDLE

    def test_bug4_completed_state_closes_call(self):
        """After COMPLETED, call should end (VoIP simulation)."""
        sm = create_state_machine()
        sm.context.client_id = "456"
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Di Nanni"
        sm.context.state = BookingState.COMPLETED

        result = sm.process_message("vorrei un altro appuntamento")

        # COMPLETED now ends the call (should_exit=True)
        assert result.should_exit is True
        assert "arrivederci" in result.response.lower() or "confermato" in result.response.lower()

    def test_bug4_cancelled_state_closes_call(self):
        """After CANCELLED, call should end (VoIP simulation)."""
        sm = create_state_machine()
        sm.context.client_id = "789"
        sm.context.client_name = "Marco"
        sm.context.state = BookingState.CANCELLED

        result = sm.process_message("ho cambiato idea")

        # CANCELLED now ends the call (should_exit=True)
        assert result.should_exit is True
        assert "arrivederci" in result.response.lower()

    # --- BUG 5: Just-registered client not found ---

    def test_bug5_client_id_survives_full_booking_cycle(self):
        """client_id set during registration survives through booking completion."""
        sm = create_state_machine()
        sm.context.client_id = "new-123"
        sm.context.client_name = "Gino"
        sm.context.state = BookingState.WAITING_SERVICE

        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")
        result = sm.process_message("confermo")

        assert result.booking is not None
        assert result.booking.get("client_id") == "new-123"
        assert sm.context.state == BookingState.COMPLETED

        # After COMPLETED, call ends (VoIP simulation)
        result2 = sm.process_message("vorrei anche una barba")
        assert result2.should_exit is True

    def test_bug5_known_client_skips_lookup(self):
        """When client_id is already set, _handle_idle skips DB lookup."""
        sm = create_state_machine()
        sm.context.client_id = "existing-456"
        sm.context.client_name = "Gino"
        sm.context.state = BookingState.IDLE

        result = sm.process_message("vorrei prenotare")

        # Should go to WAITING_SERVICE without DB lookup
        assert sm.context.state == BookingState.WAITING_SERVICE
        assert not result.needs_db_lookup, "Should not need DB lookup when client_id is set"
        assert "Gino" in result.response


# =============================================================================
# WHATSAPP FAQ PATTERN TESTS
# =============================================================================

class TestWhatsAppFAQ:
    """Test WhatsApp FAQ pattern detection (L0a handler)."""

    def setup_method(self):
        import re
        # Mirror the patterns from orchestrator._WA_FAQ_PATTERNS
        self.patterns = [
            re.compile(r"\bwhatsapp\b", re.IGNORECASE),
            re.compile(r"\bconferma\s+(?:via|su|per|tramite)\b", re.IGNORECASE),
            re.compile(r"\b(?:mandate|inviate|spedite)\s+(?:conferma|messaggio|notifica)\b", re.IGNORECASE),
        ]

    def _matches(self, text: str) -> bool:
        return any(p.search(text) for p in self.patterns)

    def test_whatsapp_mention(self):
        assert self._matches("avete whatsapp?")

    def test_conferma_via_whatsapp(self):
        assert self._matches("fanno conferma via whatsapp?")

    def test_conferma_su_whatsapp(self):
        assert self._matches("la conferma su whatsapp arriva?")

    def test_mandate_conferma(self):
        assert self._matches("mandate conferma dopo la prenotazione?")

    def test_inviate_notifica(self):
        assert self._matches("inviate notifica al cliente?")

    def test_no_false_positive_on_normal(self):
        assert not self._matches("vorrei prenotare un taglio")

    def test_no_false_positive_on_greeting(self):
        assert not self._matches("buongiorno, sono Gino")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
