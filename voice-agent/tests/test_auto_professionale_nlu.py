"""
Tests for Wave C NLU patterns: extended auto and professionale verticals.
Phase: f-sara-nlu-patterns
Wave: 3 (sequential after Wave A hair+beauty, Wave B wellness+medico)
Also tests: DURATION_MAP and OPERATOR_ROLES data structures.

Run with: pytest voice-agent/tests/test_auto_professionale_nlu.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from italian_regex import (
    check_vertical_guardrail,
    VERTICAL_SERVICES,
    DURATION_MAP,
    OPERATOR_ROLES,
)
from entity_extractor import extract_vertical_entities


# =============================================================================
# AUTO EXTENDED GUARDRAILS
# =============================================================================

class TestAutoExtendedGuardrails:
    """Auto vertical: existing blocks preserved + new beauty/professionale OOS."""

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "tinta capelli",
        "messa in piega",
        "fare la manicure mani",
        "ceretta gambe completa",
    ])
    def test_auto_still_blocks_salone_oos(self, text: str):
        r = check_vertical_guardrail(text, "auto")
        assert r.blocked is True, f"Expected auto to block salone OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "abbonamento mensile palestra",
        "corso di yoga domani",
        "personal trainer disponibile",
        "personal training sessione",
    ])
    def test_auto_still_blocks_palestra_oos(self, text: str):
        r = check_vertical_guardrail(text, "auto")
        assert r.blocked is True, f"Expected auto to block palestra OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "pulizia viso profonda",
        "epilazione laser gambe",
        "ricostruzione unghie gel",
        "radiofrequenza viso",
    ])
    def test_auto_blocks_beauty_oos(self, text: str):
        r = check_vertical_guardrail(text, "auto")
        assert r.blocked is True, f"Expected auto to block beauty OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "dichiarazione dei redditi 730",
        "consulenza fiscale urgente",
        "apertura partita IVA",
    ])
    def test_auto_blocks_professionale_oos(self, text: str):
        r = check_vertical_guardrail(text, "auto")
        assert r.blocked is True, f"Expected auto to block professionale OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "tagliando scaduto",
        "cambio olio motore",
        "freni consumati",
        "perizia danni carrozzeria",
        "sostituzione parabrezza urgente",
        "diagnosi OBD centralina",
        "impianto GPL conversione",
        "equilibratura ruote",
        "convergenza assetto",
        "cambio stagionale gomme",
        "revisione ministeriale",
        "bollino blu",
        "detailing ceramica",
        "wrapping car",
        "ozono abitacolo",
    ])
    def test_auto_allows_in_scope(self, text: str):
        r = check_vertical_guardrail(text, "auto")
        assert r.blocked is False, f"Expected auto to allow in-scope: '{text}' (blocked by: {r.matched_pattern})"


# =============================================================================
# PROFESSIONALE GUARDRAILS
# =============================================================================

class TestProffessionaleGuardrails:
    """Professionale vertical blocks all other verticals."""

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "tinta capelli biondi",
        "messa in piega",
        "extension capelli",
        "trattamento cheratina capelli",
    ])
    def test_professionale_blocks_hair_oos(self, text: str):
        r = check_vertical_guardrail(text, "professionale")
        assert r.blocked is True, f"Expected professionale to block hair OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "cambio olio motore",
        "tagliando auto",
        "dal meccanico",
        "revisione auto",
        "fare il tagliando",
    ])
    def test_professionale_blocks_auto_oos(self, text: str):
        r = check_vertical_guardrail(text, "professionale")
        assert r.blocked is True, f"Expected professionale to block auto OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "ricetta medica rinnovo",
        "visita medica urgente",
        "esame del sangue",
        "visita cardiologica",
    ])
    def test_professionale_blocks_medical_oos(self, text: str):
        r = check_vertical_guardrail(text, "professionale")
        assert r.blocked is True, f"Expected professionale to block medical OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "abbonamento mensile palestra",
        "corso di yoga",
        "personal trainer",
        "sala pesi attrezzata",
    ])
    def test_professionale_blocks_wellness_oos(self, text: str):
        r = check_vertical_guardrail(text, "professionale")
        assert r.blocked is True, f"Expected professionale to block wellness OOS: '{text}'"

    @pytest.mark.parametrize("text", [
        "dichiarazione dei redditi 730",
        "modello F24 pagamento",
        "apertura partita IVA",
        "busta paga dipendente",
        "bilancio aziendale fine anno",
        "consulenza legale separazione",
        "separazione consensuale",
        "contratto di locazione",
        "recupero crediti urgente",
        "testamento successione",
        "valutazione immobile in vendita",
        "proposta d'acquisto per casa",
        "visita immobile domani pomeriggio",
        "progetto ristrutturazione bagno",
        "SCIA pratiche comunali",
    ])
    def test_professionale_allows_in_scope(self, text: str):
        r = check_vertical_guardrail(text, "professionale")
        assert r.blocked is False, f"Expected professionale to allow in-scope: '{text}' (blocked by: {r.matched_pattern})"

    def test_professionale_redirect_response_not_empty(self):
        r = check_vertical_guardrail("cambio olio motore", "professionale")
        assert r.blocked is True
        assert r.redirect_response != ""
        assert "studio professionale" in r.redirect_response.lower() or "professionale" in r.redirect_response.lower()


# =============================================================================
# AUTO ENTITY EXTRACTION
# =============================================================================

class TestAutoEntityExtraction:
    """Auto sub-vertical detection via keyword matching."""

    @pytest.mark.parametrize("text, expected_sub_vertical", [
        ("perizia danni parabrezza incrinato", "carrozzeria"),
        ("sostituzione parabrezza urgente", "carrozzeria"),
        ("diagnosi OBD centralina motore", "elettrauto"),
        ("impianto GPL conversione", "elettrauto"),
        ("equilibratura gomme convergenza", "gommista"),
        ("cambio stagionale deposito gomme", "gommista"),
        ("revisione ministeriale scaduta", "revisioni"),
        ("bollino blu collaudo", "revisioni"),
        ("detailing ceramica PPF wrapping", "detailing"),
        ("ozono abitacolo sanificazione", "detailing"),
    ])
    def test_auto_sub_vertical_detection(self, text: str, expected_sub_vertical: str):
        r = extract_vertical_entities(text, "auto")
        assert r.sub_vertical == expected_sub_vertical, (
            f"text='{text}' — expected sub_vertical='{expected_sub_vertical}', got '{r.sub_vertical}'"
        )

    @pytest.mark.parametrize("text, expected_plate, expected_brand", [
        ("ho la Fiat targa AB123CD", "AB123CD", "fiat"),
        ("Toyota Yaris targata EF456GH", "EF456GH", "toyota"),
    ])
    def test_auto_targa_brand_still_works(self, text: str, expected_plate: str, expected_brand: str):
        r = extract_vertical_entities(text, "auto")
        assert r.vehicle_plate == expected_plate, (
            f"text='{text}' — expected plate='{expected_plate}', got '{r.vehicle_plate}'"
        )
        assert r.vehicle_brand == expected_brand, (
            f"text='{text}' — expected brand='{expected_brand}', got '{r.vehicle_brand}'"
        )

    def test_auto_generic_no_sub_vertical(self):
        """Generic auto text without sub-vertical keywords returns None."""
        r = extract_vertical_entities("ho un problema con la mia auto", "auto")
        assert r.sub_vertical is None


# =============================================================================
# PROFESSIONALE ENTITY EXTRACTION
# =============================================================================

class TestProffessionaleEntityExtraction:
    """Professionale sub-vertical detection via keyword matching."""

    @pytest.mark.parametrize("text, expected_sub_vertical", [
        ("dichiarazione redditi 730 Unico", "commercialista"),
        ("modello F24 busta paga", "commercialista"),
        ("consulenza legale separazione consensuale", "avvocato"),
        ("contratto di locazione divorzio", "avvocato"),
        ("business plan analisi di mercato", "consulente"),
        ("formazione aziendale due diligence", "consulente"),
        ("valutazione immobile stima", "agenzia_immobiliare"),
        ("visita immobile proposta acquisto", "agenzia_immobiliare"),
        ("progetto ristrutturazione SCIA", "architetto"),
        ("permesso di costruire DIA pratiche", "architetto"),
    ])
    def test_professionale_sub_vertical_detection(self, text: str, expected_sub_vertical: str):
        r = extract_vertical_entities(text, "professionale")
        assert r.sub_vertical == expected_sub_vertical, (
            f"text='{text}' — expected sub_vertical='{expected_sub_vertical}', got '{r.sub_vertical}'"
        )

    def test_professionale_generic_no_sub_vertical(self):
        """Generic professionale text without sub-vertical keywords returns None."""
        r = extract_vertical_entities("vorrei fissare un appuntamento", "professionale")
        assert r.sub_vertical is None


# =============================================================================
# DURATION MAP AND OPERATOR ROLES DATA STRUCTURES
# =============================================================================

class TestDurationMap:
    """Validate DURATION_MAP and OPERATOR_ROLES data structures."""

    def test_duration_map_has_all_verticals(self):
        expected_verticals = {"hair", "beauty", "wellness", "medico", "auto", "professionale"}
        assert expected_verticals == set(DURATION_MAP.keys()), (
            f"DURATION_MAP missing verticals: {expected_verticals - set(DURATION_MAP.keys())}"
        )

    def test_duration_map_values_are_positive_ints(self):
        """Spot check: known durations match expected values."""
        assert DURATION_MAP["hair"]["taglio"] == 30
        assert DURATION_MAP["auto"]["cambio_olio"] == 30
        assert DURATION_MAP["medico"]["visita"] == 30
        # All values must be positive integers
        for vertical, services in DURATION_MAP.items():
            for service, duration in services.items():
                assert isinstance(duration, int) and duration > 0, (
                    f"DURATION_MAP['{vertical}']['{service}'] = {duration} is not a positive int"
                )

    def test_operator_roles_has_all_verticals(self):
        expected_verticals = {"hair", "beauty", "wellness", "medico", "auto", "professionale"}
        assert expected_verticals == set(OPERATOR_ROLES.keys()), (
            f"OPERATOR_ROLES missing verticals: {expected_verticals - set(OPERATOR_ROLES.keys())}"
        )

    def test_operator_roles_content(self):
        """Spot check: known role titles present."""
        assert "fisioterapista" in OPERATOR_ROLES["medico"]
        assert "meccanico" in OPERATOR_ROLES["auto"]
        assert "avvocato" in OPERATOR_ROLES["professionale"]
        assert "parrucchiere" in OPERATOR_ROLES["hair"]
        # All verticals must have at least one role
        for vertical, roles in OPERATOR_ROLES.items():
            assert len(roles) >= 1, f"OPERATOR_ROLES['{vertical}'] is empty"
