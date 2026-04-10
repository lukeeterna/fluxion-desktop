"""
Phase E: Audit Backlog P1 — Test Suite
Tests for E1-E7 changes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from booking_state_machine import BookingStateMachine, BookingState, BookingContext, StateMachineResult


def make_sm(vertical="salone", **ctx_overrides):
    """Create a state machine with optional context overrides."""
    sm = BookingStateMachine(vertical=vertical)
    for k, v in ctx_overrides.items():
        setattr(sm.context, k, v)
    return sm


# =============================================================================
# E1: Dead State Removal
# =============================================================================

class TestE1DeadStateRemoval:
    def test_state_count_is_14(self):
        """E1+E4: 23 states reduced to 14."""
        assert len(list(BookingState)) == 14

    def test_removed_states_not_in_enum(self):
        """Removed states should not exist."""
        removed = [
            "CHECKING_AVAILABILITY", "SLOT_UNAVAILABLE", "PROPOSING_WAITLIST",
            "CONFIRMING_WAITLIST", "WAITLIST_SAVED", "WAITING_OPERATOR",
            "REGISTERING_CONFIRM", "DISAMBIGUATING_BIRTH_DATE",
            "ASKING_CLOSE_CONFIRMATION",
        ]
        for name in removed:
            assert not hasattr(BookingState, name), f"{name} should be removed"

    def test_active_states_exist(self):
        """All 14 active states exist."""
        active = [
            "IDLE", "WAITING_NAME", "WAITING_SERVICE", "WAITING_DATE",
            "WAITING_TIME", "CONFIRMING", "COMPLETED", "CANCELLED",
            "WAITING_SURNAME", "CONFIRMING_PHONE", "PROPOSE_REGISTRATION",
            "REGISTERING_SURNAME", "REGISTERING_PHONE", "DISAMBIGUATING_NAME",
        ]
        for name in active:
            assert hasattr(BookingState, name), f"{name} should exist"


# =============================================================================
# E2: Exit Path from Registration
# =============================================================================

class TestE2RegistrationExit:
    @pytest.mark.parametrize("cancel_phrase", [
        "annulla", "no grazie", "lascia perdere", "non mi interessa",
        "non voglio", "ho cambiato idea", "niente",
    ])
    def test_cancel_from_registering_surname(self, cancel_phrase):
        """Cancel during surname collection exits to CANCELLED."""
        sm = make_sm(state=BookingState.REGISTERING_SURNAME, client_name="Mario")
        result = sm.process_message(cancel_phrase)
        assert result.next_state == BookingState.CANCELLED
        assert result.should_exit is True

    @pytest.mark.parametrize("cancel_phrase", [
        "annulla", "no grazie", "lascia perdere",
    ])
    def test_cancel_from_registering_phone(self, cancel_phrase):
        """Cancel during phone collection exits to CANCELLED."""
        sm = make_sm(
            state=BookingState.REGISTERING_PHONE,
            client_name="Mario", client_surname="Rossi"
        )
        result = sm.process_message(cancel_phrase)
        assert result.next_state == BookingState.CANCELLED
        assert result.should_exit is True

    def test_cancel_from_confirming_phone(self):
        """Cancel during phone confirmation exits to CANCELLED."""
        sm = make_sm(
            state=BookingState.CONFIRMING_PHONE,
            client_name="Mario", client_surname="Rossi",
            client_phone="3331234567"
        )
        result = sm.process_message("no grazie, lascia perdere")
        assert result.next_state == BookingState.CANCELLED
        assert result.should_exit is True

    def test_normal_input_not_cancelled(self):
        """Normal surname input should NOT trigger cancel."""
        sm = make_sm(state=BookingState.REGISTERING_SURNAME, client_name="Mario")
        result = sm.process_message("Rossi")
        assert result.next_state != BookingState.CANCELLED


# =============================================================================
# E3: Single Slot Suggestion
# =============================================================================

class TestE3SlotSuggestion:
    def test_slot_rejection_offers_alternatives(self):
        """Declining suggested slot offers alternatives."""
        sm = make_sm(
            state=BookingState.CONFIRMING,
            client_name="Mario", service="taglio", service_display="Taglio",
            date="2026-04-15", date_display="martedì",
            time="10:00", time_display="alle 10:00",
        )
        sm.context.alternative_slots = [
            {"time": "11:30"}, {"time": "14:00"}, {"time": "16:00"}
        ]
        result = sm.process_message("no")
        assert result.next_state == BookingState.WAITING_TIME
        assert "11:30" in result.response
        assert sm.context.alternative_slots == []  # consumed

    def test_explicit_cancel_not_caught_by_alternatives(self):
        """'annulla' should cancel, not offer alternatives."""
        sm = make_sm(
            state=BookingState.CONFIRMING,
            client_name="Mario", service="taglio", service_display="Taglio",
            date="2026-04-15", time="10:00",
        )
        sm.context.alternative_slots = [{"time": "11:30"}]
        result = sm.process_message("annulla")
        assert result.next_state == BookingState.CANCELLED

    def test_no_alternatives_falls_through(self):
        """Without alternatives, 'no' follows normal cancel flow."""
        sm = make_sm(
            state=BookingState.CONFIRMING,
            client_name="Mario", service="taglio",
            date="2026-04-15", time="10:00",
        )
        # No alternative_slots set
        result = sm.process_message("no")
        # Should go to CANCELLED or ask for clarification
        assert result.next_state in (BookingState.CANCELLED, BookingState.CONFIRMING)


# =============================================================================
# E4: Direct Completion (no ASKING_CLOSE_CONFIRMATION)
# =============================================================================

class TestE4DirectCompletion:
    def test_confirmation_goes_to_completed(self):
        """Confirming booking goes directly to COMPLETED."""
        sm = make_sm(
            state=BookingState.CONFIRMING,
            client_name="Mario", client_id="123",
            service="taglio", service_display="Taglio",
            date="2026-04-15", date_display="martedì",
            time="10:00", time_display="alle 10:00",
        )
        result = sm.process_message("sì confermo")
        assert result.next_state == BookingState.COMPLETED
        assert result.should_exit is True
        assert result.booking is not None
        assert "whatsapp" in result.response.lower() or "confermata" in result.response.lower()


# =============================================================================
# E5: Escalation with Context Handoff
# =============================================================================

class TestE5EscalationHandoff:
    def test_operator_escalation_has_context(self):
        """Operator escalation includes collected info."""
        sm = make_sm(
            state=BookingState.WAITING_TIME,
            client_name="Marco", service="taglio", service_display="Taglio",
            date_display="venerdì",
        )
        result = sm.process_message("voglio parlare con un operatore")
        assert result.should_exit is True
        assert result.escalate_to_human is True
        assert "Taglio" in result.response or "annotato" in result.response
        # Summary in lookup_params
        summary = result.lookup_params.get("escalation_summary", {})
        assert summary.get("cliente") == "Marco"
        assert summary.get("servizio") == "Taglio"

    def test_escalation_with_no_context(self):
        """Escalation from IDLE still works."""
        sm = make_sm(state=BookingState.IDLE)
        result = sm.process_message("vorrei un operatore")
        assert result.should_exit is True
        assert result.escalate_to_human is True

    def test_escalation_manager_functions(self):
        """Test escalation_manager module directly."""
        from escalation_manager import build_escalation_summary, format_escalation_response, build_caller_message

        ctx = BookingContext()
        ctx.client_name = "Luigi"
        ctx.service_display = "Piega"
        ctx.date_display = "lunedì"

        summary = build_escalation_summary(ctx, reason="test")
        assert summary["cliente"] == "Luigi"
        assert summary["servizio"] == "Piega"

        formatted = format_escalation_response(summary)
        assert "Luigi" in formatted
        assert "Piega" in formatted

        msg = build_caller_message(summary)
        assert "collega" in msg
        assert "Piega" in msg


# =============================================================================
# E6: Global 3-Strike Escalation
# =============================================================================

class TestE6ThreeStrikeEscalation:
    def test_three_failures_trigger_escalation(self):
        """3 consecutive nonsense inputs trigger auto-escalation."""
        sm = make_sm(state=BookingState.WAITING_SERVICE, client_name="Mario")
        for i in range(2):
            r = sm.process_message("xyz abc 123")
            assert r.should_exit is False
            assert sm.context.consecutive_failures == i + 1

        # 3rd strike
        r = sm.process_message("xyz abc 123")
        assert r.should_exit is True
        assert r.escalate_to_human is True
        assert sm.context.consecutive_failures == 0  # reset after escalation

    def test_progress_resets_counter(self):
        """State change resets the failure counter."""
        sm = make_sm(state=BookingState.WAITING_SERVICE, client_name="Mario")
        sm.process_message("xyz")
        sm.process_message("abc")
        assert sm.context.consecutive_failures == 2

        sm.process_message("vorrei un taglio")
        assert sm.context.consecutive_failures == 0

    def test_escalation_not_triggered_on_exit(self):
        """Already exiting calls shouldn't trigger strike tracking."""
        sm = make_sm(
            state=BookingState.CONFIRMING,
            client_name="Mario", service="taglio",
            date="2026-04-15", time="10:00",
        )
        r = sm.process_message("sì confermo")
        assert r.should_exit is True
        assert r.escalate_to_human is False


# =============================================================================
# E7: VoIP Keepalive (syntax check only — pjsua2 not available on MacBook)
# =============================================================================

class TestE7VoIPKeepalive:
    def test_sip_config_has_keepalive(self):
        """SIPConfig dataclass has keepalive_interval field."""
        import ast
        source = Path(__file__).parent.parent / "src" / "voip_pjsua2.py"
        tree = ast.parse(source.read_text())
        # Check that keepalive_interval is in the SIPConfig class
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id'):
                if node.target.id == 'keepalive_interval':
                    found = True
        assert found, "keepalive_interval not found in voip_pjsua2.py"

    def test_voip_syntax_valid(self):
        """voip_pjsua2.py has valid Python syntax."""
        source = Path(__file__).parent.parent / "src" / "voip_pjsua2.py"
        ast_module = __import__("ast")
        ast_module.parse(source.read_text())
