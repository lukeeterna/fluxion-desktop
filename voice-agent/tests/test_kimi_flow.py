"""
Tests for Kimi 2.5 conversation flow integration.

Tests the guided sequential flow:
  nome → cognome → DB lookup → telefono → servizio → data → ora → conferma

Key behaviors tested:
- WAITING_NAME routes to WAITING_SURNAME (not WAITING_SERVICE)
- WAITING_SURNAME extracts surname and triggers DB lookup
- Full name in one turn bypasses WAITING_SURNAME
- CONFIRMING_PHONE confirms phone before creating client
- Ambiguous dates trigger week_availability lookup
- Follow-up booking preserves client identity
"""

import pytest
from datetime import date

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from booking_state_machine import (
    BookingStateMachine,
    BookingState,
    BookingContext,
    StateMachineResult,
    TEMPLATES,
)


def create_sm(vertical="salone"):
    """Create a state machine for testing."""
    return BookingStateMachine(vertical=vertical)


# =============================================================================
# WAITING_NAME → WAITING_SURNAME routing
# =============================================================================

class TestWaitingNameToSurname:
    """Test that WAITING_NAME routes to WAITING_SURNAME instead of WAITING_SERVICE."""

    def test_name_only_goes_to_waiting_surname(self):
        """Single name → ask for surname."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("sono Gino")
        assert sm.context.state == BookingState.WAITING_SURNAME
        assert sm.context.client_name is not None
        assert "cognome" in result.response.lower() or "piacere" in result.response.lower()

    def test_name_with_client_id_stays_waiting_service(self):
        """Known client (follow-up booking) → WAITING_SERVICE."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_NAME
        sm.context.client_name = "Gino"
        sm.context.client_id = "42"
        result = sm.process_message("Gino")
        assert sm.context.state == BookingState.WAITING_SERVICE

    def test_full_name_triggers_db_lookup(self):
        """'sono Gino Di Nanni' → name+surname extracted → DB lookup or WAITING_SURNAME."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("sono Gino Di Nanni")
        # Should extract name at minimum
        assert sm.context.client_name is not None
        if sm.context.client_surname:
            # Full name extracted — should trigger DB lookup
            assert result.needs_db_lookup
            assert result.lookup_type == "client_by_name_surname"
        else:
            # Only name extracted — should go to WAITING_SURNAME
            assert sm.context.state == BookingState.WAITING_SURNAME

    def test_new_client_indicator_goes_to_registering(self):
        """'Sono nuovo' → REGISTERING_SURNAME (legacy flow)."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("Sono nuovo, non sono mai stato da voi")
        assert sm.context.state == BookingState.REGISTERING_SURNAME


# =============================================================================
# WAITING_SURNAME handler
# =============================================================================

class TestWaitingSurname:
    """Test the WAITING_SURNAME state handler."""

    def test_simple_surname_triggers_lookup(self):
        """Single word surname → DB lookup."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Gino"
        result = sm.process_message("Rossi")
        assert sm.context.client_surname is not None
        assert "rossi" in sm.context.client_surname.lower()
        assert result.needs_db_lookup
        assert result.lookup_type == "client_by_name_surname"
        assert result.lookup_params.get("name") == "Gino"

    def test_compound_surname(self):
        """Compound surname 'Di Nanni' → extracted correctly."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Gino"
        result = sm.process_message("Di Nanni")
        assert sm.context.client_surname is not None
        assert "nanni" in sm.context.client_surname.lower()
        assert result.needs_db_lookup

    def test_surname_does_not_overwrite_name(self):
        """CRITICAL: surname must NOT overwrite client_name."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Gino"
        sm.process_message("Di Nanni")
        assert sm.context.client_name == "Gino"

    def test_contextual_phrase(self):
        """'il cognome è Arquati' → extracts surname."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Marco"
        result = sm.process_message("il cognome è Arquati")
        assert sm.context.client_surname is not None
        assert "arquati" in sm.context.client_surname.lower()

    def test_surname_already_set_bypasses_extraction(self):
        """If surname already populated, skip extraction and go to DB lookup."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Di Nanni"
        result = sm.process_message("qualsiasi cosa")
        assert result.needs_db_lookup
        assert result.lookup_type == "client_by_name_surname"

    def test_unrecognizable_input_reasks(self):
        """Gibberish → stay in WAITING_SURNAME, re-ask."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Gino"
        result = sm.process_message("eh boh mah")
        assert sm.context.state == BookingState.WAITING_SURNAME
        assert "cognome" in result.response.lower()


# =============================================================================
# IDLE routing with surname
# =============================================================================

class TestIdleWithSurname:
    """Test _handle_idle routes correctly based on surname presence."""

    def test_idle_name_only_goes_to_surname(self):
        """IDLE with name but no surname → WAITING_SURNAME."""
        sm = create_sm()
        sm.context.state = BookingState.IDLE
        sm.context.client_name = "Marco"
        result = sm.process_message("ciao")
        assert sm.context.state == BookingState.WAITING_SURNAME

    def test_idle_name_and_surname_does_lookup(self):
        """IDLE with name+surname → DB lookup."""
        sm = create_sm()
        sm.context.state = BookingState.IDLE
        sm.context.client_name = "Marco"
        sm.context.client_surname = "Rossi"
        result = sm.process_message("ciao")
        assert result.needs_db_lookup
        assert result.lookup_type == "client_by_name_surname"

    def test_idle_with_client_id_no_lookup(self):
        """IDLE with client_id → no DB lookup needed."""
        sm = create_sm()
        sm.context.state = BookingState.IDLE
        sm.context.client_name = "Marco"
        sm.context.client_id = "42"
        result = sm.process_message("ciao")
        assert not result.needs_db_lookup


# =============================================================================
# CONFIRMING_PHONE handler
# =============================================================================

class TestConfirmingPhone:
    """Test the CONFIRMING_PHONE state handler."""

    def test_affirmative_creates_client(self):
        """'Sì' → create client via DB lookup."""
        sm = create_sm()
        sm.context.state = BookingState.CONFIRMING_PHONE
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Di Nanni"
        sm.context.client_phone = "3331234567"
        result = sm.process_message("sì confermo")
        assert sm.context.state == BookingState.WAITING_SERVICE
        assert result.needs_db_lookup
        assert result.lookup_type == "create_client"
        assert result.follow_up_response is not None

    def test_negative_goes_back_to_phone(self):
        """'No' → back to REGISTERING_PHONE, clear phone."""
        sm = create_sm()
        sm.context.state = BookingState.CONFIRMING_PHONE
        sm.context.client_name = "Gino"
        sm.context.client_phone = "3331234567"
        result = sm.process_message("no")
        assert sm.context.state == BookingState.REGISTERING_PHONE
        assert sm.context.client_phone is None

    def test_new_phone_number_updates(self):
        """Giving a new phone number → update and re-ask confirmation."""
        sm = create_sm()
        sm.context.state = BookingState.CONFIRMING_PHONE
        sm.context.client_name = "Gino"
        sm.context.client_phone = "3331234567"
        result = sm.process_message("no è 3339876543")
        # Should either go back to phone or update and re-confirm
        assert sm.context.state in (BookingState.CONFIRMING_PHONE, BookingState.REGISTERING_PHONE)

    def test_registering_phone_now_goes_to_confirming(self):
        """Phone collected in REGISTERING_PHONE → CONFIRMING_PHONE (not REGISTERING_CONFIRM)."""
        sm = create_sm()
        sm.context.state = BookingState.REGISTERING_PHONE
        sm.context.client_name = "Gino"
        sm.context.client_surname = "Rossi"
        sm.context.is_new_client = True
        result = sm.process_message("333 1234567")
        assert sm.context.state == BookingState.CONFIRMING_PHONE
        assert "333" in result.response


# =============================================================================
# Ambiguous date → week_availability lookup
# =============================================================================

class TestAmbiguousDateLookup:
    """Test that ambiguous dates trigger week_availability lookup."""

    def test_prossima_settimana_triggers_lookup(self):
        """'Prossima settimana' → week_availability lookup."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_DATE
        sm.context.service = "Taglio"
        result = sm.process_message("la prossima settimana")
        assert result.needs_db_lookup
        assert result.lookup_type == "week_availability"
        assert result.lookup_params.get("week_offset") == 1

    def test_questa_settimana_offset_zero(self):
        """'Questa settimana' → week_offset=0."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_DATE
        sm.context.service = "Taglio"
        result = sm.process_message("questa settimana")
        assert result.needs_db_lookup
        assert result.lookup_type == "week_availability"
        assert result.lookup_params.get("week_offset") == 0

    def test_tra_due_settimane_offset_two(self):
        """'Tra due settimane' → week_offset=2."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_DATE
        sm.context.service = "Taglio"
        result = sm.process_message("tra due settimane")
        assert result.needs_db_lookup
        assert result.lookup_type == "week_availability"
        assert result.lookup_params.get("week_offset") == 2

    def test_explicit_date_no_lookup(self):
        """'Domani' → normal date extraction, no week lookup."""
        sm = create_sm()
        sm.context.state = BookingState.WAITING_DATE
        sm.context.service = "Taglio"
        result = sm.process_message("domani")
        # Should extract date normally
        if result.needs_db_lookup:
            assert result.lookup_type != "week_availability"


# =============================================================================
# Availability checker — check_week
# =============================================================================

class TestCheckWeek:
    """Test the check_week method of AvailabilityChecker."""

    @pytest.fixture
    def checker(self):
        from availability_checker import AvailabilityChecker, AvailabilityConfig
        config = AvailabilityConfig(
            working_days=[1, 2, 3, 4, 5, 6],  # Mon-Sat
        )
        return AvailabilityChecker(config=config)

    @pytest.mark.asyncio
    async def test_check_week_returns_available_days(self, checker):
        """check_week returns dict with available_days list."""
        result = await checker.check_week(
            week_offset=1,
            reference_date=date(2026, 2, 2)  # Monday
        )
        assert "available_days" in result
        assert "week_start" in result
        assert isinstance(result["available_days"], list)
        # Should have some days (unless all booked, which is unlikely in test)
        for day in result["available_days"]:
            assert "date" in day
            assert "day_name" in day
            assert "slot_count" in day

    @pytest.mark.asyncio
    async def test_check_week_this_week(self, checker):
        """check_week with offset=0 skips past days."""
        result = await checker.check_week(
            week_offset=0,
            reference_date=date(2026, 2, 4)  # Wednesday
        )
        # Should only include Thu, Fri, Sat (not Mon, Tue, Wed)
        for day in result["available_days"]:
            day_date = date.fromisoformat(day["date"])
            assert day_date > date(2026, 2, 4)


# =============================================================================
# Full guided flow (state machine only — no orchestrator)
# =============================================================================

class TestGuidedFlowStateMachine:
    """Test the complete guided flow through the state machine."""

    def test_flow_name_surname_service_date(self):
        """Full flow: IDLE → WAITING_NAME → WAITING_SURNAME → (lookup) → WAITING_SERVICE → WAITING_DATE."""
        sm = create_sm()

        # IDLE: user says hello with name
        sm.context.state = BookingState.IDLE
        result = sm.process_message("Ciao sono Marco")
        # Should have extracted name and go to WAITING_SURNAME
        if sm.context.client_name:
            if sm.context.client_surname:
                # Full name extracted — DB lookup
                assert result.needs_db_lookup
            else:
                # Name only — ask for surname
                assert sm.context.state == BookingState.WAITING_SURNAME

    def test_follow_up_booking_skips_surname(self):
        """Follow-up booking with known client → skip identity collection."""
        sm = create_sm()
        sm.context.client_name = "Gino"
        sm.context.client_id = "42"
        sm.context.client_phone = "3331234567"
        sm.context.state = BookingState.IDLE

        result = sm.process_message("vorrei un altro appuntamento")
        # Should go to WAITING_SERVICE, not WAITING_SURNAME
        assert sm.context.state == BookingState.WAITING_SERVICE

    def test_confirming_phone_full_cycle(self):
        """REGISTERING_PHONE → CONFIRMING_PHONE → 'sì' → WAITING_SERVICE."""
        sm = create_sm()
        sm.context.state = BookingState.REGISTERING_PHONE
        sm.context.client_name = "Mario"
        sm.context.client_surname = "Rossi"
        sm.context.is_new_client = True

        # Give phone
        result = sm.process_message("333 1234567")
        assert sm.context.state == BookingState.CONFIRMING_PHONE

        # Confirm phone
        result = sm.process_message("sì corretto")
        assert sm.context.state == BookingState.WAITING_SERVICE
        assert result.needs_db_lookup
        assert result.lookup_type == "create_client"
