"""
FLUXION Voice Agent - Guardrail Unit Tests (F02)

Tests for check_vertical_guardrail() in italian_regex.py.
Validates that out-of-scope queries are blocked per vertical.

Run with: pytest voice-agent/tests/test_guardrails.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from italian_regex import check_vertical_guardrail, GuardrailResult


# =============================================================================
# SALONE GUARDRAILS
# =============================================================================

class TestSaloneGuardrails:
    """Salone blocks auto, palestra, medical out-of-scope queries."""

    def test_salone_blocks_cambio_olio(self):
        r = check_vertical_guardrail("vorrei fare il cambio olio", "salone")
        assert r.blocked is True
        assert r.vertical == "salone"
        assert r.redirect_response != ""

    def test_salone_blocks_gomme_invernali(self):
        r = check_vertical_guardrail("devo cambiare le gomme invernali", "salone")
        assert r.blocked is True

    def test_salone_blocks_tagliando_auto(self):
        r = check_vertical_guardrail("quando posso portare l'auto per la revisione auto?", "salone")
        assert r.blocked is True

    def test_salone_blocks_abbonamento_palestra(self):
        r = check_vertical_guardrail("vorrei rinnovare l'abbonamento mensile", "salone")
        assert r.blocked is True

    def test_salone_blocks_corso_yoga(self):
        r = check_vertical_guardrail("posso iscrivermi al corso di yoga?", "salone")
        assert r.blocked is True

    def test_salone_blocks_visita_medica(self):
        r = check_vertical_guardrail("vorrei prenotare una visita medica", "salone")
        assert r.blocked is True

    def test_salone_blocks_esame_sangue(self):
        r = check_vertical_guardrail("devo fare l'esame del sangue", "salone")
        assert r.blocked is True

    def test_salone_allows_taglio(self):
        r = check_vertical_guardrail("vorrei prenotare un taglio", "salone")
        assert r.blocked is False

    def test_salone_allows_colore(self):
        r = check_vertical_guardrail("voglio fare il colore", "salone")
        assert r.blocked is False

    def test_salone_allows_piega(self):
        r = check_vertical_guardrail("prenoto una messa in piega", "salone")
        assert r.blocked is False

    def test_salone_redirect_response_contains_salone(self):
        r = check_vertical_guardrail("cambio olio motore", "salone")
        assert r.blocked is True
        assert "salone" in r.redirect_response.lower() or "capell" in r.redirect_response.lower()


# =============================================================================
# PALESTRA GUARDRAILS
# =============================================================================

class TestPalestraGuardrails:
    """Palestra blocks salone, auto, medical out-of-scope queries."""

    def test_palestra_blocks_taglio_capelli(self):
        r = check_vertical_guardrail("voglio prenotare un taglio capelli", "palestra")
        assert r.blocked is True

    def test_palestra_blocks_tinta_capelli(self):
        r = check_vertical_guardrail("devo fare la tinta capelli", "palestra")
        assert r.blocked is True

    def test_palestra_blocks_cambio_olio(self):
        r = check_vertical_guardrail("cambio olio motore per la mia macchina", "palestra")
        assert r.blocked is True

    def test_palestra_blocks_visita_medica(self):
        r = check_vertical_guardrail("prenoto una visita specialistica", "palestra")
        assert r.blocked is True

    def test_palestra_allows_yoga(self):
        r = check_vertical_guardrail("vorrei iscrivermi al corso di yoga", "palestra")
        assert r.blocked is False

    def test_palestra_allows_personal_trainer(self):
        r = check_vertical_guardrail("voglio un personal trainer", "palestra")
        assert r.blocked is False


# =============================================================================
# MEDICAL GUARDRAILS
# =============================================================================

class TestMedicalGuardrails:
    """Medical blocks salone, palestra, auto out-of-scope queries."""

    def test_medical_blocks_taglio_donna(self):
        r = check_vertical_guardrail("voglio prenotare un taglio donna", "medical")
        assert r.blocked is True

    def test_medical_blocks_manicure(self):
        r = check_vertical_guardrail("vorrei fare la manicure", "medical")
        assert r.blocked is True

    def test_medical_blocks_abbonamento_palestra(self):
        r = check_vertical_guardrail("rinnovo abbonamento annuale palestra", "medical")
        assert r.blocked is True

    def test_medical_blocks_cambio_olio(self):
        r = check_vertical_guardrail("devo fare il cambio olio filtro olio", "medical")
        assert r.blocked is True

    def test_medical_allows_visita_medica(self):
        r = check_vertical_guardrail("vorrei prenotare una visita medica", "medical")
        assert r.blocked is False

    def test_medical_allows_analisi(self):
        r = check_vertical_guardrail("devo fare un prelievo", "medical")
        assert r.blocked is False


# =============================================================================
# AUTO GUARDRAILS
# =============================================================================

class TestAutoGuardrails:
    """Auto blocks salone, palestra, medical out-of-scope queries."""

    def test_auto_blocks_taglio_capelli(self):
        r = check_vertical_guardrail("prenoto un taglio capelli", "auto")
        assert r.blocked is True

    def test_auto_blocks_corso_yoga(self):
        r = check_vertical_guardrail("mi iscrivo al corso di spinning", "auto")
        assert r.blocked is True

    def test_auto_blocks_visita_medica(self):
        r = check_vertical_guardrail("visita specialistica con il cardiologo", "auto")
        assert r.blocked is True

    def test_auto_allows_cambio_olio(self):
        r = check_vertical_guardrail("devo fare il cambio olio", "auto")
        assert r.blocked is False

    def test_auto_allows_cambio_gomme(self):
        r = check_vertical_guardrail("cambio gomme invernali per la mia auto", "auto")
        assert r.blocked is False

    def test_auto_allows_tagliando(self):
        r = check_vertical_guardrail("quando posso portare l'auto per il tagliando?", "auto")
        assert r.blocked is False


# =============================================================================
# EDGE CASES
# =============================================================================

class TestGuardrailEdgeCases:
    """Edge cases: unknown vertical, empty text, matched_pattern populated."""

    def test_unknown_vertical_not_blocked(self):
        r = check_vertical_guardrail("qualsiasi cosa", "wellness")
        assert r.blocked is False

    def test_empty_text_not_blocked(self):
        r = check_vertical_guardrail("", "salone")
        assert r.blocked is False

    def test_blocked_result_has_matched_pattern(self):
        r = check_vertical_guardrail("voglio fare il cambio olio motore", "salone")
        assert r.blocked is True
        assert r.matched_pattern != ""

    def test_return_type_is_guardrail_result(self):
        r = check_vertical_guardrail("ciao", "salone")
        assert isinstance(r, GuardrailResult)


# =============================================================================
# BUG 6: VERB-FORM GUARDRAILS — SALONE
# =============================================================================

class TestSaloneVerbFormGuardrails:
    """Bug 6: Verb-form auto service patterns must block in salone vertical."""

    def test_cambiare_gomme_blocked(self):
        r = check_vertical_guardrail("devo cambiare le gomme si puo farlo", "salone")
        assert r.blocked, "Verb-form 'cambiare le gomme' must be blocked in salone"

    def test_cambiare_pneumatici_blocked(self):
        r = check_vertical_guardrail("vorrei cambiare i pneumatici", "salone")
        assert r.blocked

    def test_fare_tagliando_blocked(self):
        r = check_vertical_guardrail("devo fare il tagliando", "salone")
        assert r.blocked

    def test_portare_macchina_tagliando_blocked(self):
        r = check_vertical_guardrail("devo portare la macchina per il tagliando", "salone")
        assert r.blocked

    def test_cambiare_olio_blocked(self):
        r = check_vertical_guardrail("devo fare il cambio olio", "salone")
        assert r.blocked

    def test_dal_meccanico_blocked(self):
        r = check_vertical_guardrail("devo portare la macchina dal meccanico", "salone")
        assert r.blocked

    def test_far_vedere_macchina_blocked(self):
        r = check_vertical_guardrail("devo far vedere la macchina", "salone")
        assert r.blocked

    def test_fare_revisione_auto_blocked(self):
        r = check_vertical_guardrail("devo fare la revisione auto", "salone")
        assert r.blocked

    def test_cambiare_orario_not_blocked(self):
        """'cambiare orario' is a reschedule request — must NOT be blocked."""
        r = check_vertical_guardrail("vorrei cambiare l'orario", "salone")
        assert not r.blocked, "Reschedule 'cambiare orario' must NOT be blocked by guardrail"

    def test_taglio_capelli_not_blocked(self):
        """Legitimate salone service must not be blocked."""
        r = check_vertical_guardrail("taglio capelli domani", "salone")
        assert not r.blocked

    def test_colore_capelli_not_blocked(self):
        r = check_vertical_guardrail("colorazione capelli", "salone")
        assert not r.blocked


# =============================================================================
# BUG 6: VERB-FORM GUARDRAILS — PALESTRA
# =============================================================================

class TestPalestraVerbFormGuardrails:
    """Bug 6 cross-vertical: verb-form auto patterns must block in palestra too."""

    def test_cambiare_gomme_blocked_palestra(self):
        r = check_vertical_guardrail("devo cambiare le gomme", "palestra")
        assert r.blocked

    def test_fare_tagliando_blocked_palestra(self):
        r = check_vertical_guardrail("fare il tagliando", "palestra")
        assert r.blocked

    def test_yoga_not_blocked(self):
        """Legitimate palestra service not blocked."""
        r = check_vertical_guardrail("corso di yoga martedi", "palestra")
        assert not r.blocked


# =============================================================================
# BUG 6: VERB-FORM GUARDRAILS — MEDICAL
# =============================================================================

class TestMedicalVerbFormGuardrails:
    """Bug 6 cross-vertical: verb-form auto patterns must block in medical too."""

    def test_cambiare_gomme_blocked_medical(self):
        r = check_vertical_guardrail("devo cambiare le gomme", "medical")
        assert r.blocked

    def test_fare_tagliando_blocked_medical(self):
        r = check_vertical_guardrail("fare il tagliando", "medical")
        assert r.blocked

    def test_visita_medica_not_blocked(self):
        """Auto vertical DOES block medical queries — visita medica blocked in auto."""
        r = check_vertical_guardrail("visita medica domani", "auto")
        assert r.blocked  # Auto vertical DOES block medical


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
