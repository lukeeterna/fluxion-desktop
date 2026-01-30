"""
Tests for SARA booking state machine corrections (B1-B7).
Validates 3-level correction logic, name sanitization, slot pre-fill skip,
generic operator extraction, and follow-up responses.
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from booking_state_machine import (
    BookingStateMachine, BookingState, StateMachineResult,
    sanitize_name, sanitize_name_pair,
)
from entity_extractor import extract_generic_operator


# ========== B1: PUNCTUATION IN NAMES ==========

class TestB1PunctuationInNames:
    def test_trailing_period_removed(self):
        """STT artifact: 'Rossi.' → 'Rossi'"""
        result = sanitize_name("Rossi.", is_surname=True)
        assert result == "Rossi"
        assert not result.endswith(".")

    def test_trailing_comma_removed(self):
        """STT artifact: 'Dilevam,' → 'Dilevam'"""
        result = sanitize_name("Dilevam,", is_surname=True)
        assert result == "Dilevam"
        assert "," not in result

    def test_multiple_punctuation_removed(self):
        """STT artifact: 'Mario!!!' → 'Mario'"""
        result = sanitize_name("Mario!!!")
        assert result == "Mario"

    def test_internal_apostrophe_preserved(self):
        """D'Angelo must keep its apostrophe"""
        result = sanitize_name("d'angelo", is_surname=True)
        assert result == "D'Angelo"

    def test_noble_prefix(self):
        """De Luca → de Luca"""
        result = sanitize_name("de luca", is_surname=True)
        assert result == "de Luca"

    def test_registering_surname_strips_punctuation(self):
        """Full flow: _handle_registering_surname strips punctuation"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.REGISTERING_SURNAME
        sm.context.client_name = "Gianluca"
        result = sm.process_message("Distasi.")
        assert sm.context.client_surname == "Distasi"


# ========== B2: SPLIT REGISTRATION RESPONSE ==========

class TestB2SplitRegistration:
    def test_registration_has_follow_up(self):
        """Registration confirm should produce follow_up_response"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.REGISTERING_CONFIRM
        sm.context.client_name = "Mario"
        sm.context.client_surname = "Rossi"
        sm.context.client_phone = "3331234567"
        sm.context.is_new_client = True
        result = sm.process_message("sì confermo")
        assert result.follow_up_response is not None
        assert "trattamento" in result.follow_up_response.lower() or "aiutarla" in result.follow_up_response.lower()

    def test_registration_main_response_has_name(self):
        """Main response should confirm registration with name"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.REGISTERING_CONFIRM
        sm.context.client_name = "Mario"
        sm.context.client_surname = "Rossi"
        sm.context.client_phone = "3331234567"
        sm.context.is_new_client = True
        result = sm.process_message("sì")
        assert "Mario" in result.response

    def test_no_follow_up_in_other_states(self):
        """Follow-up should NOT appear in non-registration states"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.WAITING_SERVICE
        result = sm.process_message("vorrei un taglio")
        assert result.follow_up_response is None


# ========== B3: GENERIC OPERATOR ==========

class TestB3GenericOperator:
    def test_generic_female_operator(self):
        """'con un'operatrice' → gender F, generic"""
        result = extract_generic_operator("con un'operatrice")
        assert result["gender"] == "F"
        assert result["is_generic"] is True
        assert result["name"] is None

    def test_generic_male_operator(self):
        """'con un operatore' → gender M, generic"""
        result = extract_generic_operator("con un operatore")
        assert result["gender"] == "M"
        assert result["is_generic"] is True

    def test_preferisco_donna(self):
        """'preferisco una donna' → gender F"""
        result = extract_generic_operator("preferisco una donna")
        assert result["gender"] == "F"
        assert result["is_generic"] is True

    def test_no_operator_request(self):
        """'vorrei un taglio' → not a generic operator request"""
        result = extract_generic_operator("vorrei un taglio")
        assert result["is_generic"] is False


# ========== B4: CONFIRMING CORRECTIONS ==========

class TestB4ConfirmingCorrections:
    def test_niente_meglio_venerdi_is_correction_not_cancel(self):
        """'niente, meglio venerdì' → date updated, NOT cancelled"""
        sm = BookingStateMachine(
            vertical="salone",
            reference_date=datetime(2026, 1, 27)
        )
        sm.context.state = BookingState.CONFIRMING
        sm.context.service = "taglio"
        sm.context.date = "2026-01-28"
        sm.context.date_display = "mercoledì 28 gennaio"
        sm.context.time = "10:00"
        sm.context.time_display = "alle 10:00"
        result = sm.process_message("niente, meglio venerdì")
        assert result.next_state != BookingState.CANCELLED
        assert result.next_state == BookingState.CONFIRMING

    def test_si_ma_alle_11_is_correction(self):
        """'sì ma alle 11' → time updated, NOT confirmed with old time"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.CONFIRMING
        sm.context.service = "taglio"
        sm.context.date = "2026-02-01"
        sm.context.time = "10:00"
        sm.context.time_display = "alle 10:00"
        result = sm.process_message("sì ma alle 11")
        # Should NOT complete with old time - should correct
        assert result.next_state == BookingState.CONFIRMING
        assert "11" in sm.context.time or "11" in result.response

    def test_pure_si_confirms(self):
        """'sì' alone → COMPLETED"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.CONFIRMING
        sm.context.service = "taglio"
        sm.context.date = "2026-02-01"
        sm.context.time = "10:00"
        sm.context.time_display = "alle 10:00"
        sm.context.service_display = "Taglio"
        sm.context.date_display = "sabato 1 febbraio"
        result = sm.process_message("sì")
        assert result.next_state == BookingState.COMPLETED

    def test_pure_no_cancels(self):
        """'no grazie' → CANCELLED (pure rejection without entities)"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.CONFIRMING
        sm.context.service = "taglio"
        sm.context.date = "2026-02-01"
        sm.context.time = "10:00"
        result = sm.process_message("no grazie")
        assert result.next_state == BookingState.CANCELLED

    def test_correction_counter_increments(self):
        """Each correction increments corrections_made"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.CONFIRMING
        sm.context.service = "taglio"
        sm.context.time = "10:00"
        sm.context.date = "2026-02-01"
        assert sm.context.corrections_made == 0
        sm.process_message("meglio alle 15")
        assert sm.context.corrections_made >= 1


# ========== B5: FORCE UPDATE ==========

class TestB5ForceUpdate:
    def test_force_update_overwrites_time(self):
        """force_update=True overwrites existing time"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.time = "10:00"
        sm._update_context_from_extraction(
            {"time": "17:00"},
            force_update=True
        )
        assert sm.context.time == "17:00"

    def test_no_force_update_preserves(self):
        """force_update=False does NOT overwrite"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.time = "10:00"
        sm._update_context_from_extraction(
            {"time": "17:00"},
            force_update=False
        )
        assert sm.context.time == "10:00"

    def test_force_update_all_fields(self):
        """All fields are updatable with force_update"""
        sm = BookingStateMachine(vertical="salone")
        sm._update_context_from_extraction(
            {
                "service": "colore",
                "date": "2026-02-01",
                "time": "15:00",
                "operator": "Marco"
            },
            force_update=True
        )
        assert sm.context.service == "colore"
        assert sm.context.date == "2026-02-01"
        assert sm.context.time == "15:00"
        assert sm.context.operator_name == "Marco"


# ========== B6: SLOT PRE-FILL SKIP ==========

class TestB6SlotPreFillSkip:
    def test_skip_service_if_provided(self):
        """Service already filled → skip to WAITING_DATE"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.service = "taglio"
        next_state = sm._get_next_required_slot()
        assert next_state == BookingState.WAITING_DATE

    def test_skip_date_if_provided(self):
        """Date already filled → skip to WAITING_TIME"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.service = "taglio"
        sm.context.date = "2026-02-01"
        next_state = sm._get_next_required_slot()
        assert next_state == BookingState.WAITING_TIME

    def test_all_filled_goes_to_confirming(self):
        """All required slots filled → CONFIRMING"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.service = "taglio"
        sm.context.date = "2026-02-01"
        sm.context.time = "10:00"
        next_state = sm._get_next_required_slot()
        assert next_state == BookingState.CONFIRMING


# ========== B7: SURNAME DUPLICATION ==========

class TestB7SurnameDuplication:
    def test_auto_split_full_name(self):
        """'Gianluca Distasi' → name=Gianluca, surname=Distasi"""
        name, surname = sanitize_name_pair("Gianluca Distasi", None)
        assert name == "Gianluca"
        assert surname == "Distasi"

    def test_three_word_name(self):
        """'Marco De Luca' → name=Marco, surname=De Luca (C5)"""
        name, surname = sanitize_name_pair("Marco De Luca", None)
        assert name == "Marco"
        assert surname is not None
        assert "Luca" in surname

    def test_no_duplication(self):
        """If name == surname, remove duplicate"""
        name, surname = sanitize_name_pair("Distasi", "Distasi")
        assert name == "Distasi"
        assert surname is None


# ========== HELPER METHOD TESTS ==========

class TestHelperMethods:
    def test_handle_timeout(self):
        """Timeout returns a valid response"""
        sm = BookingStateMachine(vertical="salone")
        sm.context.state = BookingState.WAITING_SERVICE
        result = sm.handle_timeout()
        assert result.response is not None
        assert "ancora" in result.response.lower() or "riprendere" in result.response.lower()

    def test_format_correction_summary(self):
        """Correction summary formats correctly"""
        sm = BookingStateMachine(vertical="salone")
        summary = sm._format_correction_summary({"ora": "17", "operatore": "Marco"})
        assert "ora → 17" in summary
        assert "operatore → Marco" in summary

    def test_vertical_constructor(self):
        """Constructor sets vertical correctly"""
        sm = BookingStateMachine(vertical="medical")
        assert sm.context.vertical == "medical"

    def test_is_slot_filled(self):
        """_is_slot_filled works for all field types"""
        sm = BookingStateMachine(vertical="salone")
        assert not sm._is_slot_filled("service")
        sm.context.service = "taglio"
        assert sm._is_slot_filled("service")
