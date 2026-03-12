"""
FLUXION Voice Agent - F02 Vertical Guardrail Fixes (S58)

Tests for:
- GAP-G3: Palestra abbonamento → soft escalation (BSM._check_service_vertical_constraint)
- GAP-G2: Medical urgency → 118 advisory (orchestrator medical_urgency intercept)

Run with: pytest voice-agent/tests/test_f02_vertical_fixes.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from booking_state_machine import BookingStateMachine, BookingState, BookingContext


# =============================================================================
# GAP-G3: PALESTRA ABBONAMENTO SOFT ESCALATION
# =============================================================================

class TestPalestraAbbonamentoGuardrail:
    """Palestra 'abbonamento' service must redirect to segreteria, not start booking flow."""

    def _make_bsm_palestra(self) -> BookingStateMachine:
        bsm = BookingStateMachine(vertical="palestra")
        return bsm

    def test_abbonamento_service_does_not_enter_booking_flow(self):
        """When service=abbonamento in palestra, BSM must NOT proceed to WAITING_DATE."""
        bsm = self._make_bsm_palestra()
        bsm.context.service = "abbonamento"
        bsm.context.state = BookingState.WAITING_SERVICE
        result = bsm._handle_waiting_service("voglio rinnovare l'abbonamento", None)
        assert result.next_state == BookingState.WAITING_SERVICE, (
            f"Expected WAITING_SERVICE (soft escalation), got {result.next_state}"
        )
        assert "segreteria" in result.response.lower() or "personal training" in result.response.lower(), (
            f"Expected redirect to segreteria, got: {result.response}"
        )

    def test_abbonamento_response_mentions_alternative(self):
        """Redirect response must suggest alternative bookable services."""
        bsm = self._make_bsm_palestra()
        bsm.context.service = "abbonamento"
        bsm.context.state = BookingState.WAITING_SERVICE
        result = bsm._handle_waiting_service("iscrizione palestra", None)
        response_lower = result.response.lower()
        assert any(kw in response_lower for kw in ["corso", "personal training", "sessione", "prenotare"]), (
            f"Response should suggest bookable alternatives, got: {result.response}"
        )

    def test_non_abbonamento_palestra_service_enters_booking_flow(self):
        """Non-abbonamento palestra service must continue to WAITING_DATE normally."""
        bsm = self._make_bsm_palestra()
        bsm.context.service = "yoga"
        bsm.context.state = BookingState.WAITING_SERVICE
        result = bsm._handle_waiting_service("voglio fare yoga", None)
        assert result.next_state == BookingState.WAITING_DATE, (
            f"yoga should proceed to WAITING_DATE, got {result.next_state}"
        )

    def test_personal_training_palestra_enters_booking_flow(self):
        """personal_training in palestra must proceed to WAITING_DATE."""
        bsm = self._make_bsm_palestra()
        bsm.context.service = "personal_training"
        bsm.context.state = BookingState.WAITING_SERVICE
        result = bsm._handle_waiting_service("voglio un personal trainer", None)
        assert result.next_state == BookingState.WAITING_DATE

    def test_abbonamento_in_salone_vertical_not_intercepted(self):
        """Abbonamento in non-palestra vertical is NOT intercepted by constraint check."""
        bsm = BookingStateMachine(vertical="salone")
        bsm.context.service = "abbonamento"
        bsm.context.state = BookingState.WAITING_SERVICE
        # In salone, "abbonamento" is not a palestra-specific issue — should not block
        result = bsm._check_service_vertical_constraint()
        assert result is None, "Constraint should only fire for palestra vertical"

    def test_check_service_vertical_constraint_returns_none_for_yoga(self):
        """Helper returns None for non-constrained palestra services."""
        bsm = self._make_bsm_palestra()
        bsm.context.service = "yoga"
        result = bsm._check_service_vertical_constraint()
        assert result is None


# =============================================================================
# GAP-G2: MEDICAL URGENCY 118 ADVISORY
# =============================================================================

class TestMedicalUrgencyIntercept:
    """Medical urgency keyword detection in italian_regex (used by orchestrator intercept)."""

    def test_urgency_patterns_exist(self):
        """italian_regex must have urgency patterns for medical vertical detection."""
        from italian_regex import extract_vertical_entities
        result = extract_vertical_entities("ho bisogno subito di un medico", "medical")
        assert result.urgency is True, (
            "'ho bisogno subito' must set urgency=True for medical vertical"
        )

    def test_urgency_pronto_soccorso(self):
        """'pronto soccorso' must trigger urgency."""
        from italian_regex import extract_vertical_entities
        result = extract_vertical_entities("devo andare al pronto soccorso", "medical")
        assert result.urgency is True

    def test_non_urgent_medical_no_urgency(self):
        """Standard booking request must NOT set urgency."""
        from italian_regex import extract_vertical_entities
        result = extract_vertical_entities("vorrei prenotare una visita la prossima settimana", "medical")
        assert not result.urgency, (
            "Standard medical booking must not trigger urgency flag"
        )

    def test_urgency_in_non_medical_vertical(self):
        """Urgency in non-medical vertical should not affect booking flow."""
        from italian_regex import extract_vertical_entities
        # Even if urgency is detected in salone, it shouldn't matter for booking
        result = extract_vertical_entities("ho urgenza di un taglio!", "salone")
        # Just check it doesn't crash — urgency field exists
        assert hasattr(result, 'urgency')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
