"""
FLUXION Voice Agent - Vertical Entity Extractor Tests (F02)

Tests for extract_vertical_entities() in entity_extractor.py.
Validates medical specialty/urgency/visit_type and auto plate/brand extraction.

Run with: pytest voice-agent/tests/test_vertical_entity_extractor.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from entity_extractor import extract_vertical_entities, VerticalEntities


# =============================================================================
# MEDICAL -- SPECIALTY
# =============================================================================

class TestMedicalSpecialty:

    def test_cardiologo_detected(self):
        r = extract_vertical_entities("vorrei una visita dal cardiologo", "medical")
        assert r.specialty == "cardiologia"

    def test_dermatologo_detected(self):
        r = extract_vertical_entities("devo fare il controllo dei nei dal dermatologo", "medical")
        assert r.specialty == "dermatologia"

    def test_pediatra_detected(self):
        r = extract_vertical_entities("bilancio di salute per il mio bambino", "medical")
        assert r.specialty == "pediatria"

    def test_oculista_detected(self):
        r = extract_vertical_entities("voglio controllare la vista dall'oculista", "medical")
        assert r.specialty == "oculistica"

    def test_ginecologa_detected(self):
        r = extract_vertical_entities("prenoto una visita ginecologica", "medical")
        assert r.specialty == "ginecologia"

    def test_no_specialty_generic_visit(self):
        r = extract_vertical_entities("vorrei prenotare una visita generica", "medical")
        assert r.specialty is None


# =============================================================================
# MEDICAL -- URGENCY
# =============================================================================

class TestMedicalUrgency:

    def test_urgente_detected(self):
        r = extract_vertical_entities("ho bisogno urgente di una visita", "medical")
        assert r.urgency == "urgente"

    def test_subito_detected(self):
        r = extract_vertical_entities("mi serve un appuntamento subito", "medical")
        assert r.urgency == "urgente"

    def test_presto_detected(self):
        r = extract_vertical_entities("mi serve appena possibile", "medical")
        assert r.urgency == "alta"

    def test_calma_detected(self):
        r = extract_vertical_entities("non ho fretta, quando c'e' posto", "medical")
        assert r.urgency == "bassa"

    def test_no_urgency_neutral(self):
        r = extract_vertical_entities("vorrei prenotare una visita domani", "medical")
        assert r.urgency is None


# =============================================================================
# MEDICAL -- VISIT TYPE
# =============================================================================

class TestMedicalVisitType:

    def test_prima_visita_detected(self):
        r = extract_vertical_entities("e la prima volta che vengo", "medical")
        assert r.visit_type == "prima_visita"

    def test_controllo_detected(self):
        r = extract_vertical_entities("devo fare un follow-up", "medical")
        assert r.visit_type == "controllo"

    def test_vaccino_detected(self):
        r = extract_vertical_entities("devo fare la vaccinazione antinfluenzale", "medical")
        assert r.visit_type == "vaccino"


# =============================================================================
# AUTO -- PLATE
# =============================================================================

class TestAutoPlate:

    def test_targa_standard_detected(self):
        r = extract_vertical_entities("la mia targa e AB123CD", "auto")
        assert r.vehicle_plate == "AB123CD"

    def test_targa_with_spaces(self):
        r = extract_vertical_entities("targa AB 123 CD", "auto")
        assert r.vehicle_plate == "AB123CD"

    def test_targa_lowercase_normalized(self):
        r = extract_vertical_entities("la targa e ab123cd", "auto")
        assert r.vehicle_plate == "AB123CD"

    def test_no_targa_in_generic_text(self):
        r = extract_vertical_entities("devo fare il cambio olio", "auto")
        assert r.vehicle_plate is None


# =============================================================================
# AUTO -- BRAND
# =============================================================================

class TestAutoBrand:

    def test_fiat_detected(self):
        r = extract_vertical_entities("ho una Fiat Punto da portare", "auto")
        assert r.vehicle_brand == "fiat"

    def test_alfa_romeo_detected(self):
        r = extract_vertical_entities("ho un Alfa Romeo Giulia", "auto")
        assert r.vehicle_brand == "alfa romeo"

    def test_volkswagen_detected(self):
        r = extract_vertical_entities("la mia Volkswagen Golf fa rumore", "auto")
        assert r.vehicle_brand == "volkswagen"

    def test_no_brand_if_not_mentioned(self):
        r = extract_vertical_entities("devo fare il tagliando", "auto")
        assert r.vehicle_brand is None


# =============================================================================
# CROSS-VERTICAL ISOLATION
# =============================================================================

class TestVerticalIsolation:

    def test_salone_returns_empty_entities(self):
        r = extract_vertical_entities("voglio un taglio", "salone")
        assert r.specialty is None
        assert r.vehicle_plate is None
        assert r.vehicle_brand is None

    def test_palestra_returns_empty_entities(self):
        r = extract_vertical_entities("yoga alle 18", "palestra")
        assert r.specialty is None
        assert r.vehicle_plate is None

    def test_return_type_is_vertical_entities(self):
        r = extract_vertical_entities("ciao", "medical")
        assert isinstance(r, VerticalEntities)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
