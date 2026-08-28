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
        assert result.response.strip()

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
        confirmation_text = result.response.lower()
        assert any(marker in confirmation_text for marker in ("conferma", "riepilogo", "tutto giusto"))

        # E4: Confirm → COMPLETED directly (no ASKING_CLOSE_CONFIRMATION)
        result = sm.process_message("sì confermo")
        assert result.next_state == BookingState.COMPLETED
        assert result.booking is not None
        assert result.booking["service"] == "taglio"
        assert result.booking["time"] == "15:00"
        assert result.should_exit is True

    def test_flow_with_all_info_in_one_message(self):
        """Test when user provides all info in one message."""
        sm = create_state_machine()
        sm.start_booking_flow()
        result = sm.process_message("vorrei un taglio domani alle 15")
        assert result.next_state == BookingState.CONFIRMING
        assert sm.context.service == "taglio"
        assert sm.context.time == "15:00"
        assert sm.context.date is not None

    def test_flow_with_service_and_date_in_one_message(self):
        """Test when user provides service and date together."""
        sm = create_state_machine()
        sm.start_booking_flow()
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
        """E4: Confirmation leads directly to COMPLETED."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")
        result = sm.process_message("sì va bene")
        assert result.next_state == BookingState.COMPLETED
        assert result.booking is not None
        assert result.should_exit is True

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
        result = sm.process_message("no aspetta, ricominciamo")
        assert sm.context.state == BookingState.WAITING_SERVICE
        assert sm.context.service is None
        assert sm.context.date is None
        assert sm.context.was_interrupted is False

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
        assert result.next_state == BookingState.WAITING_DATE
        acknowledgement = result.response.lower()
        assert any(marker in acknowledgement for marker in ("cambiare", "dica", "dimmi"))

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
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")
        result = sm.process_message("cambio servizio")
        assert sm.context.state == BookingState.WAITING_SERVICE
        assert sm.context.service is None

    def test_change_date_during_confirmation(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 15")
        result = sm.process_message("cambio giorno")
        assert sm.context.state == BookingState.WAITING_DATE
        assert sm.context.date is None

    def test_change_time_during_confirmation(self):
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
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("dopodomani")
        assert sm.context.date is not None
        expected_date = (REFERENCE_DATE + timedelta(days=2)).strftime("%Y-%m-%d")
        assert sm.context.date == expected_date

    def test_time_extraction_in_flow(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("alle 9 e mezza")
        assert sm.context.time == "09:30"

    def test_approximate_time_handling(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("di pomeriggio")
        assert sm.context.time == "15:00"
        assert sm.context.time_is_approximate is True

    def test_name_extraction(self):
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        sm.process_message("mi chiamo Laura Bianchi")
        assert sm.context.client_name == "Laura"
        assert sm.context.client_surname == "Bianchi"


# =============================================================================
# TEST: CONTEXT PERSISTENCE
# =============================================================================

class TestContextPersistence:
    def test_context_to_json(self):
        ctx = BookingContext(state=BookingState.WAITING_DATE, service="taglio", service_display="Taglio", client_name="Mario", turns_count=3)
        data = json.loads(ctx.to_json())
        assert data["state"] == "waiting_date"
        assert data["service"] == "taglio"
        assert data["client_name"] == "Mario"
        assert data["turns_count"] == 3

    def test_context_from_json(self):
        json_str = json.dumps({"state": "confirming", "service": "colore", "service_display": "Colore", "date": "2026-01-15", "date_display": "mercoledì 15 gennaio", "time": "10:00", "time_display": "alle 10:00", "client_name": "Anna", "client_id": None, "client_phone": None, "client_email": None, "operator_id": None, "operator_name": None, "operator_requested": False, "notes": None, "created_at": None, "updated_at": None, "turns_count": 5, "time_is_approximate": False, "was_interrupted": False, "previous_state": None})
        ctx = BookingContext.from_json(json_str)
        assert ctx.state == BookingState.CONFIRMING
        assert ctx.service == "colore"
        assert ctx.date == "2026-01-15"
        assert ctx.time == "10:00"
        assert ctx.client_name == "Anna"

    def test_context_roundtrip(self):
        original = BookingContext(state=BookingState.WAITING_TIME, service="piega", date="2026-01-20", client_name="Giuseppe", turns_count=4)
        restored = BookingContext.from_json(original.to_json())
        assert restored.state == original.state
        assert restored.service == original.service
        assert restored.date == original.date
        assert restored.client_name == original.client_name

    def test_resume_from_context(self):
        ctx = BookingContext(state=BookingState.WAITING_TIME, service="taglio", service_display="Taglio", date="2026-01-15", date_display="mercoledì 15 gennaio")
        sm = create_state_machine()
        sm.set_context(ctx)
        sm.process_message("alle 16")
        assert sm.context.state == BookingState.CONFIRMING
        assert sm.context.time == "16:00"


# =============================================================================
# TEST: CONTEXT METHODS
# =============================================================================

class TestContextMethods:
    def test_get_summary(self):
        ctx = BookingContext(service="taglio", service_display="Taglio", date="2026-01-15", date_display="mercoledì 15 gennaio", time="10:00", time_display="alle 10:00")
        summary = ctx.get_summary()
        assert "Taglio" in summary
        assert "15 gennaio" in summary
        assert "10:00" in summary

    def test_get_summary_with_operator(self):
        ctx = BookingContext(service_display="Colore", date_display="domani", time_display="alle 15:00", operator_name="Maria")
        assert "Maria" in ctx.get_summary()

    def test_is_complete(self):
        ctx = BookingContext()
        assert ctx.is_complete() is False
        ctx.service = "taglio"
        assert ctx.is_complete() is False
        ctx.date = "2026-01-15"
        assert ctx.is_complete() is False
        ctx.time = "10:00"
        assert ctx.is_complete() is True

    def test_get_missing_fields(self):
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
        ctx = BookingContext(state=BookingState.CONFIRMING, service="taglio", client_name="Mario", client_id="123", turns_count=5)
        d = ctx.to_dict()
        assert d["state"] == "confirming"
        assert d["client"]["name"] == "Mario"
        assert d["client"]["id"] == "123"
        assert d["booking"]["service"] == "taglio"
        assert d["turns"] == 5


class TestInitialContext:
    def test_start_with_client_name(self):
        sm = create_state_machine()
        result = sm.start_booking_flow({"client_name": "Mario Rossi"})
        assert sm.context.client_name == "Mario Rossi"
        assert result.next_state == BookingState.WAITING_SERVICE

    def test_start_with_service(self):
        sm = create_state_machine()
        result = sm.start_booking_flow({"service": "taglio"})
        assert sm.context.service == "taglio"
        assert result.next_state == BookingState.WAITING_DATE


class TestErrorHandling:
    """Test error cases and recovery."""

    def test_unknown_service(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        result = sm.process_message("vorrei un massaggio")
        assert sm.context.state == BookingState.WAITING_SERVICE
        response_text = result.response.lower()
        assert any(marker in response_text for marker in ("capire", "capito"))
        assert any(marker in response_text for marker in ("trattamento", "servizio"))

    def test_invalid_date(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("il giorno blu")
        assert sm.context.state == BookingState.WAITING_DATE
        assert sm.context.date is None

    def test_invalid_time(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("domani")
        sm.process_message("quando capita")
        assert sm.context.state == BookingState.WAITING_TIME
        assert sm.context.time is None

    def test_recovery_after_error(self):
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        sm.process_message("xyz")
        assert sm.context.state == BookingState.WAITING_DATE
        sm.process_message("domani")
        assert sm.context.state == BookingState.WAITING_TIME
        assert sm.context.date is not None


class TestConfirmationVariations:
    def test_affirmative_responses(self):
        affirmatives = ["sì", "si", "ok", "va bene", "d'accordo", "confermo", "perfetto", "certo"]
        for response in affirmatives:
            sm = create_state_machine()
            sm.start_booking_flow()
            sm.process_message("taglio domani alle 15")
            result = sm.process_message(response)
            assert result.next_state == BookingState.COMPLETED, f"Failed CONFIRMING→COMPLETED for '{response}'"
            assert result.should_exit is True

    def test_negative_responses(self):
        negatives = ["no", "no grazie", "annulla", "non voglio"]
        for response in negatives:
            sm = create_state_machine()
            sm.start_booking_flow()
            sm.process_message("taglio domani alle 15")
            result = sm.process_message(response)
            assert result.next_state == BookingState.CANCELLED, f"Failed for '{response}'"


class TestBugRegression:
    def test_bug1_surname_does_not_overwrite_name(self):
        sm = create_state_machine()
        sm.context.client_name = "Gino"
        sm.context.is_new_client = True
        sm.context.state = BookingState.REGISTERING_SURNAME
        sm.process_message("Di Nanni")
        assert sm.context.client_name == "Gino"
        assert sm.context.client_surname is not None
        assert "nanni" in sm.context.client_surname.lower()

    def test_bug1_surname_single_word_preserved(self):
        sm = create_state_machine()
        sm.context.client_name = "Marco"
        sm.context.state = BookingState.REGISTERING_SURNAME
        sm.process_message("Rossi")
        assert sm.context.client_name == "Marco"
        assert sm.context.client_surname == "Rossi"

    def test_bug1_full_name_repeat_works(self):
        sm = create_state_machine()
        sm.context.client_name = "Gino"
        sm.context.state = BookingState.REGISTERING_SURNAME
        sm.process_message("Gino Di Nanni")
        assert sm.context.client_name == "Gino"
        assert "nanni" in sm.context.client_surname.lower()

    def test_bug1_registration_confirm_shows_full_name(self):
        sm = create_state_machine()
        sm.context.client_name = "Gino"
        sm.context.is_new_client = True
        sm.context.state = BookingState.REGISTERING_SURNAME
        result = sm.process_message("Di Nanni")
        assert sm.context.state == BookingState.REGISTERING_PHONE
        result = sm.process_message("333 1234567")
        assert sm.context.state == BookingState.CONFIRMING_PHONE
        assert "3331234567" in result.response or "333" in result.response

    def test_bug2_multi_service_extraction(self):
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_SERVICE
        sm.process_message("taglio e barba")
        assert sm.context.services is not None
        assert len(sm.context.services) >= 2
        assert "taglio" in sm.context.services
        assert "barba" in sm.context.services

    def test_bug2_service_display_shows_both(self):
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_SERVICE
        sm.process_message("taglio e barba")
        assert sm.context.service_display is not None
        assert "Taglio" in sm.context.service_display
        assert "Barba" in sm.context.service_display

    def test_bug2_booking_includes_services(self):
        sm = create_state_machine()
        sm.context.client_name = "Test"
        sm.context.client_id = "1"
        sm.context.state = BookingState.WAITING_SERVICE
        sm.process_message("taglio e barba")
        sm.process_message("domani")
        sm.process_message("alle 15")
        result = sm.process_message("confermo")
        assert result.booking is not None
        assert result.booking.get("services") is not None
        assert len(result.booking["services"]) >= 2
        assert result.booking.get("service_display") is not None

    def test_bug4_reset_for_new_booking_preserves_client(self):
        sm = create_state_machine()
        sm.context.client_id = "123"
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Di Nanni"
        sm.context.client_phone = "333123456"
        sm.context.service = "taglio"
        sm.context.date = "2026-01-15"
        sm.context.time = "15:00"
        sm.reset_for_new_booking()
        assert sm.context.client_id == "123"
        assert sm.context.client_name == "Gino"
        assert sm.context.client_surname == "Di Nanni"
        assert sm.context.client_phone == "333123456"
        assert sm.context.service is None
        assert sm.context.date is None
        assert sm.context.time is None
        assert sm.context.state == BookingState.IDLE

    def test_bug4_completed_state_closes_call(self):
        sm = create_state_machine()
        sm.context.client_id = "456"
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Di Nanni"
        sm.context.state = BookingState.COMPLETED
        result = sm.process_message("vorrei un altro appuntamento")
        assert result.should_exit is True
        assert "arrivederci" in result.response.lower() or "confermato" in result.response.lower()

    def test_bug4_cancelled_state_closes_call(self):
        sm = create_state_machine()
        sm.context.client_id = "789"
        sm.context.client_name = "Marco"
        sm.context.state = BookingState.CANCELLED
        result = sm.process_message("ho cambiato idea")
        assert result.should_exit is True
        assert "arrivederci" in result.response.lower()

    def test_bug5_client_id_survives_full_booking_cycle(self):
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
        assert result.should_exit is True
        result2 = sm.process_message("vorrei anche una barba")
        assert result2.should_exit is True

    def test_bug5_known_client_skips_lookup(self):
        sm = create_state_machine()
        sm.context.client_id = "existing-456"
        sm.context.client_name = "Gino"
        sm.context.state = BookingState.IDLE
        result = sm.process_message("vorrei prenotare")
        assert sm.context.state == BookingState.WAITING_SERVICE
        assert not result.needs_db_lookup
        assert "Gino" in result.response


class TestWhatsAppFAQ:
    def setup_method(self):
        import re
        self.patterns = [re.compile(r"\bwhatsapp\b", re.IGNORECASE), re.compile(r"\bconferma\s+(?:via|su|per|tramite)\b", re.IGNORECASE), re.compile(r"\b(?:mandate|inviate|spedite)\s+(?:conferma|messaggio|notifica)\b", re.IGNORECASE)]

    def _matches(self, text: str) -> bool:
        return any(p.search(text) for p in self.patterns)

    def test_whatsapp_mention(self): assert self._matches("avete whatsapp?")
    def test_conferma_via_whatsapp(self): assert self._matches("fanno conferma via whatsapp?")
    def test_conferma_su_whatsapp(self): assert self._matches("la conferma su whatsapp arriva?")
    def test_mandate_conferma(self): assert self._matches("mandate conferma dopo la prenotazione?")
    def test_inviate_notifica(self): assert self._matches("inviate notifica al cliente?")
    def test_no_false_positive_on_normal(self): assert not self._matches("vorrei prenotare un taglio")
    def test_no_false_positive_on_greeting(self): assert not self._matches("buongiorno, sono Gino")


class TestBug4BackNavigationFromWaitingTime:
    def _setup_at_waiting_time(self):
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_TIME
        sm.context.service = "taglio"
        sm.context.service_display = "Taglio"
        sm.context.date = "2026-02-09"
        sm.context.date_display = "lunedì 9 febbraio"
        return sm

    def test_date_change_with_marker_and_weekday(self):
        sm = self._setup_at_waiting_time()
        result = sm.process_message("non posso lunedì, facciamo mercoledì")
        assert result.next_state == BookingState.WAITING_DATE
        assert sm.context.date is None

    def test_weekday_without_time(self):
        assert self._setup_at_waiting_time().process_message("meglio mercoledì").next_state == BookingState.WAITING_DATE

    def test_time_still_works(self):
        sm = self._setup_at_waiting_time(); result = sm.process_message("dopo le 17")
        assert result.next_state == BookingState.CONFIRMING and sm.context.time is not None

    def test_weekday_with_time_does_not_back_navigate(self):
        assert self._setup_at_waiting_time().process_message("mercoledì alle 15").next_state == BookingState.CONFIRMING

    def test_conversation_replay(self):
        sm = self._setup_at_waiting_time(); result = sm.process_message("Senti, per forza lunedì non possiamo fare tra mercoledì e giovedì?")
        assert result.next_state == BookingState.WAITING_DATE
        assert sm.context.date is None and sm.context.time is None

    def test_cambio_giorno(self):
        assert self._setup_at_waiting_time().process_message("cambio giorno, voglio giovedì").next_state == BookingState.WAITING_DATE


class TestBug2ServiceCorrectionInWaitingDate:
    def _setup_at_waiting_date(self, services=None, service=None):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_DATE; sm.context.client_name = "Gino"; sm.context.client_id = "123"
        from booking_state_machine import SERVICE_DISPLAY
        if services:
            sm.context.services = services; sm.context.service = services[0]; sm.context.service_display = " e ".join(SERVICE_DISPLAY.get(s, s.capitalize()) for s in services)
        elif service:
            sm.context.service = service; sm.context.services = [service]; sm.context.service_display = SERVICE_DISPLAY.get(service, service.capitalize())
        return sm

    def test_add_service_no_date(self):
        sm = self._setup_at_waiting_date(service="colore"); result = sm.process_message("aggiungi anche i capelli")
        assert result.next_state == BookingState.WAITING_DATE and "taglio" in sm.context.services and "colore" in sm.context.services and "aggiunto" in result.response.lower()

    def test_add_service_with_date(self):
        sm = self._setup_at_waiting_date(service="taglio"); result = sm.process_message("anche barba, venerdì")
        assert "barba" in sm.context.services and "taglio" in sm.context.services and sm.context.date is not None and result.next_state == BookingState.WAITING_TIME

    def test_add_multiple_services(self):
        sm = self._setup_at_waiting_date(service="taglio"); sm.process_message("voglio anche barba e colore")
        assert all(s in sm.context.services for s in ("taglio", "barba", "colore"))

    def test_no_duplicate_services(self):
        sm = self._setup_at_waiting_date(services=["taglio", "barba"]); sm.process_message("voglio anche taglio e colore")
        assert sm.context.services.count("taglio") == 1 and "colore" in sm.context.services

    def test_service_display_updated(self):
        sm = self._setup_at_waiting_date(service="taglio"); sm.process_message("aggiungi barba")
        assert "Taglio" in sm.context.service_display and "Barba" in sm.context.service_display

    def test_no_false_positive_date_only(self):
        sm = self._setup_at_waiting_date(service="taglio"); original_services = list(sm.context.services); sm.process_message("venerdì")
        assert sm.context.services == original_services and sm.context.date is not None


class TestNegatedCancelGuard:
    def test_negated_cancel_regex_matches(self):
        import re
        p = re.compile(r"\bnon\s+(?:voglio|intendo|desidero)\s+(?:cancellare?|annullare?|disdire?)\b", re.IGNORECASE)
        assert p.search("non voglio cancellare") and p.search("non intendo annullare") and p.search("non desidero disdire l'appuntamento")
        assert not p.search("voglio cancellare") and not p.search("cancellare appuntamento") and not p.search("non mi piace questa cosa")

    def test_negated_cancel_regex_case_insensitive(self):
        import re
        p = re.compile(r"\bnon\s+(?:voglio|intendo|desidero)\s+(?:cancellare?|annullare?|disdire?)\b", re.IGNORECASE)
        assert p.search("NON VOGLIO CANCELLARE") and p.search("Non Intendo Annullare")


class TestExtraEntitiesInConfirming:
    def _sm(self, extra, name, service):
        sm = create_state_machine(); sm.start_booking_flow(); sm.context.extra_entities = extra; sm.context.client_name = name; sm.context.service = service; sm.context.state = BookingState.CONFIRMING; return sm

    def test_specialty_in_confirmation(self):
        result = self._sm({'specialty': 'Cardiologia'}, 'Mario Rossi', 'visita').process_message("si confermo")
        if result.response: assert 'Cardiologia' in result.response

    def test_vehicle_plate_in_confirmation(self):
        result = self._sm({'vehicle_plate': 'AB123CD'}, 'Gino Bianchi', 'tagliando').process_message("si confermo")
        if result.response: assert 'AB123CD' in result.response

    def test_empty_extra_entities_no_crash(self):
        assert self._sm({}, 'Luca Verdi', 'taglio').process_message("si confermo") is not None

    def test_no_extra_entities_attr_no_crash(self):
        sm = self._sm({}, 'Luca Verdi', 'taglio')
        if hasattr(sm.context, 'extra_entities'): delattr(sm.context, 'extra_entities')
        assert sm.process_message("si confermo") is not None


import pytest as _pytest

class TestCancelPreIdentification:
    def test_annulla_tutto_in_waiting_name_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message("annulla tutto").next_state == BookingState.IDLE
    def test_cancella_in_waiting_name_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message("cancella").next_state == BookingState.IDLE
    def test_ricominciamo_in_waiting_name_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message("ricominciamo").next_state == BookingState.IDLE
    def test_no_grazie_in_waiting_name_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message("no grazie").next_state == BookingState.IDLE
    def test_lascia_perdere_in_waiting_name_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message("lascia perdere").next_state == BookingState.IDLE
    def test_non_voglio_in_waiting_name_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message("non voglio").next_state == BookingState.IDLE
    def test_annulla_tutto_in_waiting_surname_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_SURNAME; sm.context.client_name = "Marco"; assert sm.process_message("annulla tutto").next_state == BookingState.IDLE
    def test_no_grazie_in_waiting_surname_goes_to_idle(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_SURNAME; sm.context.client_name = "Marco"; assert sm.process_message("no grazie").next_state == BookingState.IDLE
    @_pytest.mark.parametrize("phrase", ["no grazie", "lascia perdere", "non voglio", "ho cambiato idea", "annulla tutto"])
    def test_rejection_phrases_waiting_name_parametric(self, phrase):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; assert sm.process_message(phrase).next_state == BookingState.IDLE
    def test_annulla_tutto_mid_booking_still_goes_to_waiting_service(self):
        sm = create_state_machine(); sm.start_booking_flow(); sm.process_message("taglio"); assert sm.process_message("annulla tutto").next_state == BookingState.WAITING_SERVICE
    def test_response_contains_graceful_exit_phrase(self):
        sm = create_state_machine(); sm.context.state = BookingState.WAITING_NAME; response = sm.process_message("annulla tutto").response.lower(); assert any(kw in response for kw in ["problema", "aspettiamo", "idea", "vuole"])


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
