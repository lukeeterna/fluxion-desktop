"""
Test Suite: Vertical-Specific Correction Patterns
===================================================

Tests for CORRECTION_PATTERNS_SALONE, PALESTRA, MEDICAL, AUTO.
These patterns detect field corrections during CONFIRMING state.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import pytest

from src.booking_state_machine import (
    CORRECTION_PATTERNS_SALONE,
    CORRECTION_PATTERNS_PALESTRA,
    CORRECTION_PATTERNS_MEDICAL,
    CORRECTION_PATTERNS_AUTO,
)


def match_pattern(patterns_dict: dict, field: str, text: str):
    """Helper: try to match text against patterns for a given field."""
    patterns = patterns_dict.get(field, [])
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1) if m.groups() else m.group(0)
    return None


# ============================================================================
# SALONE corrections
# ============================================================================

class TestSaloneCorrections:
    """Test CORRECTION_PATTERNS_SALONE patterns."""

    patterns = CORRECTION_PATTERNS_SALONE

    # --- servizio ---
    def test_aggiungi_piega(self):
        assert match_pattern(self.patterns, "servizio", "aggiungi una piega") == "piega"

    def test_metti_colore(self):
        assert match_pattern(self.patterns, "servizio", "metti anche colore") == "colore"

    def test_senza_barba(self):
        assert match_pattern(self.patterns, "servizio", "senza la barba") == "barba"

    def test_meglio_taglio(self):
        assert match_pattern(self.patterns, "servizio", "meglio taglio") == "taglio"

    def test_invece_extension(self):
        assert match_pattern(self.patterns, "servizio", "invece extension") == "extension"

    # --- operatore ---
    def test_con_marco(self):
        result = match_pattern(self.patterns, "operatore", "con Marco")
        assert result == "Marco"

    def test_meglio_giulia(self):
        result = match_pattern(self.patterns, "operatore", "meglio Giulia")
        assert result == "Giulia"

    # --- data ---
    def test_meglio_venerdi(self):
        result = match_pattern(self.patterns, "data", "meglio venerdì")
        assert result == "venerdì"

    def test_invece_domani(self):
        result = match_pattern(self.patterns, "data", "invece domani")
        assert result == "domani"

    def test_cambio_sabato(self):
        result = match_pattern(self.patterns, "data", "cambio a sabato")
        assert result == "sabato"

    # --- ora ---
    def test_alle_15(self):
        result = match_pattern(self.patterns, "ora", "alle 15")
        assert result == "15"

    def test_alle_10_30(self):
        result = match_pattern(self.patterns, "ora", "alle 10:30")
        assert result == "10:30"

    def test_meglio_pomeriggio(self):
        result = match_pattern(self.patterns, "ora", "meglio pomeriggio")
        assert result == "pomeriggio"

    # --- negativo ---
    def test_no_match_unrelated(self):
        assert match_pattern(self.patterns, "servizio", "come stai?") is None


# ============================================================================
# PALESTRA corrections
# ============================================================================

class TestPalestraCorrections:
    """Test CORRECTION_PATTERNS_PALESTRA patterns."""

    patterns = CORRECTION_PATTERNS_PALESTRA

    def test_meglio_yoga(self):
        result = match_pattern(self.patterns, "tipo_attivita", "meglio yoga")
        assert result == "yoga"

    def test_invece_pilates(self):
        result = match_pattern(self.patterns, "tipo_attivita", "invece pilates")
        assert result == "pilates"

    def test_piuttosto_crossfit(self):
        result = match_pattern(self.patterns, "tipo_attivita", "piuttosto crossfit")
        assert result == "crossfit"

    def test_con_istruttore(self):
        result = match_pattern(self.patterns, "istruttore", "con Marco")
        assert result == "Marco"

    def test_se_ce_istruttore(self):
        result = match_pattern(self.patterns, "istruttore", "se c'è Giulia")
        assert result == "Giulia"

    def test_meglio_sabato(self):
        result = match_pattern(self.patterns, "data", "meglio sabato")
        assert result == "sabato"

    def test_alle_18(self):
        result = match_pattern(self.patterns, "ora", "alle 18")
        assert result == "18"

    def test_meglio_mattina(self):
        result = match_pattern(self.patterns, "ora", "meglio mattina")
        assert result == "mattina"


# ============================================================================
# MEDICAL corrections
# ============================================================================

class TestMedicalCorrections:
    """Test CORRECTION_PATTERNS_MEDICAL patterns."""

    patterns = CORRECTION_PATTERNS_MEDICAL

    def test_meglio_cardiologo(self):
        result = match_pattern(self.patterns, "specialita", "meglio cardiologo")
        assert result == "cardiologo"

    def test_invece_dermatologo(self):
        result = match_pattern(self.patterns, "specialita", "invece dermatologo")
        assert result == "dermatologo"

    def test_con_dott_rossi(self):
        result = match_pattern(self.patterns, "medico", "con il dott. Rossi")
        assert result == "Rossi"

    def test_preferisco_medico(self):
        result = match_pattern(self.patterns, "medico", "preferisco Bianchi")
        assert result == "Bianchi"

    def test_prima_visita(self):
        result = match_pattern(self.patterns, "tipo_visita", "è una prima visita")
        assert result == "prima visita"

    def test_controllo(self):
        result = match_pattern(self.patterns, "tipo_visita", "per un controllo")
        assert result == "controllo"

    def test_urgente(self):
        result = match_pattern(self.patterns, "urgenza", "è urgente")
        assert result is not None

    def test_prima_possibile(self):
        result = match_pattern(self.patterns, "urgenza", "il prima possibile")
        assert result is not None

    def test_meglio_lunedi(self):
        result = match_pattern(self.patterns, "data", "meglio lunedì")
        assert result == "lunedì"

    def test_alle_9(self):
        result = match_pattern(self.patterns, "ora", "alle 9")
        assert result == "9"


# ============================================================================
# AUTO corrections
# ============================================================================

class TestAutoCorrections:
    """Test CORRECTION_PATTERNS_AUTO patterns."""

    patterns = CORRECTION_PATTERNS_AUTO

    def test_meglio_tagliando(self):
        result = match_pattern(self.patterns, "tipo_intervento", "meglio tagliando")
        assert result == "tagliando"

    def test_invece_cambio_gomme(self):
        result = match_pattern(self.patterns, "tipo_intervento", "invece cambio gomme")
        assert result == "cambio gomme"

    def test_in_realta_freni(self):
        result = match_pattern(self.patterns, "tipo_intervento", "in realtà freni")
        assert result == "freni"

    def test_mi_sbaglio_bmw(self):
        result = match_pattern(self.patterns, "marca", "mi sbaglio bmw")
        assert result is not None

    def test_in_realta_fiat(self):
        result = match_pattern(self.patterns, "marca", "in realtà fiat")
        assert result is not None

    def test_meglio_mercoledi(self):
        result = match_pattern(self.patterns, "data", "meglio mercoledì")
        assert result == "mercoledì"

    def test_verso_16(self):
        result = match_pattern(self.patterns, "ora", "verso 16")
        assert result == "16"


# ============================================================================
# Cross-vertical tests
# ============================================================================

class TestCrossVertical:
    """Test that common patterns work across verticals."""

    @pytest.mark.parametrize("patterns", [
        CORRECTION_PATTERNS_SALONE,
        CORRECTION_PATTERNS_PALESTRA,
        CORRECTION_PATTERNS_MEDICAL,
        CORRECTION_PATTERNS_AUTO,
    ])
    def test_data_meglio_domani(self, patterns):
        """All verticals should match 'meglio domani' for date."""
        result = match_pattern(patterns, "data", "meglio domani")
        assert result == "domani"

    @pytest.mark.parametrize("patterns,field", [
        (CORRECTION_PATTERNS_SALONE, "ora"),
        (CORRECTION_PATTERNS_PALESTRA, "ora"),
        (CORRECTION_PATTERNS_MEDICAL, "ora"),
        (CORRECTION_PATTERNS_AUTO, "ora"),
    ])
    def test_ora_alle_15(self, patterns, field):
        """All verticals should match 'alle 15' for time."""
        result = match_pattern(patterns, field, "alle 15")
        assert result == "15"

    def test_no_false_positives_on_greeting(self):
        """Greeting should not match any correction pattern."""
        for patterns in [
            CORRECTION_PATTERNS_SALONE, CORRECTION_PATTERNS_PALESTRA,
            CORRECTION_PATTERNS_MEDICAL, CORRECTION_PATTERNS_AUTO,
        ]:
            for field in patterns:
                assert match_pattern(patterns, field, "buongiorno come stai") is None


# ============================================================================
# Pattern completeness checks
# ============================================================================

class TestPatternCompleteness:
    """Verify each vertical has required fields."""

    def test_salone_has_all_fields(self):
        assert "servizio" in CORRECTION_PATTERNS_SALONE
        assert "operatore" in CORRECTION_PATTERNS_SALONE
        assert "data" in CORRECTION_PATTERNS_SALONE
        assert "ora" in CORRECTION_PATTERNS_SALONE

    def test_palestra_has_all_fields(self):
        assert "tipo_attivita" in CORRECTION_PATTERNS_PALESTRA
        assert "istruttore" in CORRECTION_PATTERNS_PALESTRA
        assert "data" in CORRECTION_PATTERNS_PALESTRA
        assert "ora" in CORRECTION_PATTERNS_PALESTRA

    def test_medical_has_all_fields(self):
        assert "specialita" in CORRECTION_PATTERNS_MEDICAL
        assert "medico" in CORRECTION_PATTERNS_MEDICAL
        assert "tipo_visita" in CORRECTION_PATTERNS_MEDICAL
        assert "urgenza" in CORRECTION_PATTERNS_MEDICAL
        assert "data" in CORRECTION_PATTERNS_MEDICAL
        assert "ora" in CORRECTION_PATTERNS_MEDICAL

    def test_auto_has_all_fields(self):
        assert "tipo_intervento" in CORRECTION_PATTERNS_AUTO
        assert "marca" in CORRECTION_PATTERNS_AUTO
        assert "data" in CORRECTION_PATTERNS_AUTO
        assert "ora" in CORRECTION_PATTERNS_AUTO


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
