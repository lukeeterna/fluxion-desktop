"""
Integration tests for NLU vertical pipeline: orchestrator key mapping + guardrail + entity extraction.
Phase: f-sara-nlu-patterns (Wave D)
Verifies: all 6 macro-verticals wire correctly end-to-end after Waves A/B/C.
Tests run on iMac where pytest suite executes.
"""

import pytest


def _extract_vertical_key_impl(verticale_id: str) -> str:
    """Standalone implementation of orchestrator._extract_vertical_key for testing."""
    NEW_VERTICALS = ["hair", "beauty", "wellness", "medico", "professionale"]
    LEGACY_VERTICALS = ["salone", "palestra", "medical", "auto", "altro"]
    verticale_lower = verticale_id.lower().strip()
    all_keys = NEW_VERTICALS + LEGACY_VERTICALS
    if verticale_lower in all_keys:
        return verticale_lower
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v + "_") or verticale_lower.startswith(v + "-"):
            return v
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v):
            return v
    return "altro"


class TestVerticalKeyMapping:
    """Tests for _extract_vertical_key logic — all 6 new macro keys + legacy keys."""

    @pytest.mark.parametrize("verticale_id,expected", [
        # New macro keys — exact match
        ("hair", "hair"),
        ("beauty", "beauty"),
        ("wellness", "wellness"),
        ("medico", "medico"),
        ("auto", "auto"),
        ("professionale", "professionale"),
        # New macro keys — composed IDs (underscore separator)
        ("hair_salone_bella_vita", "hair"),
        ("hair-centro-capelli", "hair"),
        ("beauty_centro_rosa", "beauty"),
        ("wellness_gym_fit", "wellness"),
        ("medico_studio_rossi", "medico"),
        ("professionale_studio_bianchi", "professionale"),
        # Legacy keys — exact match
        ("salone", "salone"),
        ("palestra", "palestra"),
        ("medical", "medical"),
        ("altro", "altro"),
        # Legacy keys — composed IDs
        ("salone_bella_vita", "salone"),
        ("palestra_fit_club", "palestra"),
        ("medical_studio_medico", "medical"),
        # Unknown IDs
        ("unknown_xyz", "altro"),
        ("", "altro"),
    ])
    def test_extract_vertical_key(self, verticale_id: str, expected: str) -> None:
        assert _extract_vertical_key_impl(verticale_id) == expected, (
            f"verticale_id={verticale_id!r}: expected {expected!r}, "
            f"got {_extract_vertical_key_impl(verticale_id)!r}"
        )


class TestNLUPipelineIntegration:
    """Tests guardrail check with vertical key extraction — simulates orchestrator runtime."""

    @pytest.mark.parametrize("verticale_id,text,expect_blocked", [
        # hair vertical — blocks auto OOS
        ("hair", "voglio fare il tagliando", True),
        ("hair_salone_bella", "cambio olio motore", True),
        # hair vertical — allows hair services
        ("hair", "vorrei un taglio capelli", False),
        ("hair_salone_bella", "barba sfumata fade", False),
        # beauty vertical — blocks hair OOS
        ("beauty", "taglio capelli donna", True),
        ("beauty_centro_rosa", "tinta capelli biondi", True),
        # beauty vertical — allows beauty services
        ("beauty", "pulizia viso profonda", False),
        ("beauty_centro_rosa", "epilazione laser gambe", False),
        # wellness vertical — blocks auto OOS
        ("wellness", "cambio olio motore", True),
        ("wellness_gym_fit", "tagliando auto scaduto", True),
        # wellness vertical — allows fitness
        ("wellness", "corso di yoga mattutino", False),
        ("wellness_gym_fit", "WOD crossfit domani", False),
        # medico vertical — blocks palestra OOS
        ("medico", "abbonamento mensile palestra", True),
        ("medico_studio_rossi", "corso di yoga", True),
        # medico vertical — allows medical services
        ("medico", "visita medica specialistica", False),
        ("medico_studio_rossi", "fisioterapia posturale", False),
        # auto vertical — blocks hair OOS
        ("auto", "taglio capelli donna", True),
        ("auto_officina", "tinta capelli biondi", True),
        # auto vertical — allows auto services
        ("auto", "cambio olio motore", False),
        ("auto_officina", "revisione ministeriale", False),
        # professionale vertical — blocks auto OOS
        ("professionale", "cambio olio motore", True),
        ("professionale_studio", "fare il tagliando", True),
        # professionale vertical — allows professionale services
        ("professionale", "dichiarazione dei redditi 730", False),
        ("professionale_studio", "consulenza legale separazione", False),
        # legacy keys still work
        ("salone", "cambio olio motore", True),
        ("salone_bella_vita", "taglio capelli donna", False),
        ("medical_studio", "abbonamento palestra", True),
        ("medical_studio", "visita medica", False),
    ])
    def test_guardrail_with_vertical_key(self, verticale_id: str, text: str, expect_blocked: bool) -> None:
        from src.italian_regex import check_vertical_guardrail
        vertical_key = _extract_vertical_key_impl(verticale_id)
        result = check_vertical_guardrail(text, vertical_key)
        assert result.blocked == expect_blocked, (
            f"vertical_key={vertical_key!r}, text={text!r}: "
            f"expected blocked={expect_blocked}, got {result.blocked}"
        )


class TestSubVerticalExtraction:
    """Tests sub_vertical field from extract_vertical_entities for non-medico verticals."""

    @pytest.mark.parametrize("verticale_id,text,expected_sub_vertical", [
        # hair
        ("hair", "barba sfumata fade skin", "barbiere"),
        ("hair_salone_bella", "correzione colore Olaplex", "color_specialist"),
        # beauty
        ("beauty", "pulizia viso profonda", "estetista_viso"),
        ("beauty_centro_rosa", "ricostruzione unghie gel", "nail_specialist"),
        # wellness
        ("wellness", "corso di yoga nidra", "yoga_pilates"),
        ("wellness_gym_fit", "BJJ muay thai", "arti_marziali"),
        # auto
        ("auto", "diagnosi OBD centralina", "elettrauto"),
        ("auto_officina", "detailing ceramica PPF", "detailing"),
        # professionale
        ("professionale", "dichiarazione 730 Unico", "commercialista"),
        ("professionale_studio", "consulenza legale divorzio", "avvocato"),
        # Legacy aliases
        ("salone", "extension cheratina I-tip", "extension_specialist"),
    ])
    def test_sub_vertical_extraction(self, verticale_id: str, text: str, expected_sub_vertical: str) -> None:
        from src.entity_extractor import extract_vertical_entities
        vertical_key = _extract_vertical_key_impl(verticale_id)
        result = extract_vertical_entities(text, vertical_key)
        assert result.sub_vertical == expected_sub_vertical, (
            f"vertical_key={vertical_key!r}, text={text!r}: "
            f"expected sub_vertical={expected_sub_vertical!r}, got {result.sub_vertical!r}"
        )


class TestMedicoSpecialtyExtraction:
    """Tests specialty field from extract_vertical_entities for medico vertical."""

    @pytest.mark.parametrize("verticale_id,text,expected_specialty", [
        ("medico", "fisioterapia posturale tecarterapia", "fisioterapia"),
        ("medico_studio", "seduta psicologo TCC", "psicologo"),
        ("medico_studio_rossi", "osteopata manipolazione osteopatica", "osteopata"),
        ("medical_studio", "nutrizionista BIA piano alimentare", "nutrizionista"),
    ])
    def test_medico_specialty_extraction(self, verticale_id: str, text: str, expected_specialty: str) -> None:
        from src.entity_extractor import extract_vertical_entities
        vertical_key = _extract_vertical_key_impl(verticale_id)
        result = extract_vertical_entities(text, vertical_key)
        assert result.specialty == expected_specialty, (
            f"vertical_key={vertical_key!r}, text={text!r}: "
            f"expected specialty={expected_specialty!r}, got {result.specialty!r}"
        )
