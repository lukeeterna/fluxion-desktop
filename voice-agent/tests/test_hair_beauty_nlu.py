"""
Tests for Wave A NLU patterns: hair and beauty verticals.
Phase: f-sara-nlu-patterns
Wave: 1 (parallel with Wave B wellness+medico, Wave C auto+professionale)
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from italian_regex import check_vertical_guardrail, GuardrailResult
from entity_extractor import extract_vertical_entities, VerticalEntities


# =============================================================================
# HAIR GUARDRAILS
# =============================================================================

class TestHairGuardrails:
    """Hair vertical blocks auto, medical, palestra, professionale OOS queries."""

    @pytest.mark.parametrize("text", [
        "voglio fare il tagliando",
        "cambio olio dell'auto",
        "portare la macchina dal meccanico",
        "cambio gomme invernali",
        "revisione auto scaduta",
        "pastiglie freni da sostituire",
        "ammaccatura auto sul paraurti",
        "diagnostica auto",
        "devo fare il cambio olio",
        "fare il cambio gomme stagionale",
    ])
    def test_hair_blocks_auto_oos(self, text):
        r = check_vertical_guardrail(text, "hair")
        assert r.blocked is True, f"Expected OOS block for: {text!r}"
        assert r.vertical == "hair"
        assert r.redirect_response != ""

    @pytest.mark.parametrize("text", [
        "visita medica urgente",
        "esame del sangue domani",
        "ricetta medica rinnovo",
        "visita dermatologica",
        "certificato sportivo",
        "analisi del sangue",
        "prelievo sangue",
    ])
    def test_hair_blocks_medical_oos(self, text):
        r = check_vertical_guardrail(text, "hair")
        assert r.blocked is True, f"Expected OOS block for: {text!r}"

    @pytest.mark.parametrize("text", [
        "abbonamento mensile palestra",
        "corso di yoga mattutino",
        "personal trainer disponibile",
        "sala pesi riservata",
        "corso di crossfit",
        "personal training sessione",
        "allenamento personalizzato",
    ])
    def test_hair_blocks_palestra_oos(self, text):
        r = check_vertical_guardrail(text, "hair")
        assert r.blocked is True, f"Expected OOS block for: {text!r}"

    @pytest.mark.parametrize("text", [
        "vorrei un taglio",
        "fare la tinta capelli",
        "balayage naturale",
        "barba sfumata",
        "skin fade",
        "zero ai lati",
        "extension cheratina",
        "correzione colore con Olaplex",
        "trattamento anti-caduta",
        "messa in piega",
        "tagliettino alle punte",
        "ripassatina nuca",
        "acconciatura sposa",
        "stiratura brasiliana",
        "permanente capelli",
        "piega asciugatura",
        "meches colpi di sole",
    ])
    def test_hair_allows_in_scope(self, text):
        r = check_vertical_guardrail(text, "hair")
        assert r.blocked is False, f"Unexpected OOS block for in-scope: {text!r}"

    @pytest.mark.parametrize("text", [
        "vorrei fare il cambio olio",
        "corso di yoga",
        "visita medica",
        "abbonamento mensile palestra",
        "dal meccanico domani",
    ])
    def test_hair_legacy_salone_key(self, text):
        """salone key must give same results as hair key for same inputs."""
        r_hair = check_vertical_guardrail(text, "hair")
        r_salone = check_vertical_guardrail(text, "salone")
        assert r_hair.blocked == r_salone.blocked, (
            f"salone and hair guardrails disagree for: {text!r} "
            f"(hair={r_hair.blocked}, salone={r_salone.blocked})"
        )


# =============================================================================
# BEAUTY GUARDRAILS
# =============================================================================

class TestBeautyGuardrails:
    """Beauty vertical blocks hair-specific, auto, medical, palestra OOS queries."""

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "tinta capelli scura",
        "messa in piega",
        "extension capelli",
        "ritocco radici bianchi",
        "trattamento capelli cheratina",
        "balayage capelli corti",
        "colorazione capelli",
    ])
    def test_beauty_blocks_hair_oos(self, text):
        r = check_vertical_guardrail(text, "beauty")
        assert r.blocked is True, f"Expected OOS block for hair in beauty: {text!r}"
        assert r.vertical == "beauty"
        assert r.redirect_response != ""

    @pytest.mark.parametrize("text", [
        "cambio olio motore",
        "revisione auto",
        "tagliando auto",
        "pneumatici invernali",
        "dal meccanico domani",
        "fare il tagliando",
    ])
    def test_beauty_blocks_auto_oos(self, text):
        r = check_vertical_guardrail(text, "beauty")
        assert r.blocked is True, f"Expected OOS block for auto in beauty: {text!r}"

    @pytest.mark.parametrize("text", [
        "ricetta medica rinnovo",
        "visita medica urgente",
        "esame del sangue",
        "visita ginecologica",
        "visita cardiologica",
    ])
    def test_beauty_blocks_medical_oos(self, text):
        r = check_vertical_guardrail(text, "beauty")
        assert r.blocked is True, f"Expected OOS block for medical in beauty: {text!r}"

    @pytest.mark.parametrize("text", [
        "pulizia viso profonda",
        "peeling enzimatico",
        "radiofrequenza viso",
        "dermaplaning",
        "massaggio drenante",
        "linfodrenaggio gambe",
        "pressoterapia",
        "ricostruzione unghie gel",
        "nail art decorazioni",
        "epilazione laser gambe",
        "laser diodo ascelle",
        "circuito spa",
        "hammam",
        "massaggio anticellulite",
        "semipermanente mani",
        "rimozione gel unghie",
        "microneedling viso",
        "trattamento acne profondo",
    ])
    def test_beauty_allows_in_scope(self, text):
        r = check_vertical_guardrail(text, "beauty")
        assert r.blocked is False, f"Unexpected OOS block for in-scope beauty: {text!r}"


# =============================================================================
# HAIR ENTITY EXTRACTION
# =============================================================================

class TestHairEntityExtraction:
    """Hair vertical entity extraction detects sub-verticals."""

    @pytest.mark.parametrize("text,expected_sub", [
        ("barba sfumata contorno barba", "barbiere"),
        ("fade e zero ai lati", "barbiere"),
        ("skin fade nuca", "barbiere"),
        ("correzione colore con Olaplex", "color_specialist"),
        ("decolorazione capelli", "color_specialist"),
        ("balayage e toning capelli", "color_specialist"),
        ("caduta capelli analisi tricologica", "tricologo"),
        ("PRP capelli anti-caduta", "tricologo"),
        ("trattamento anti-caduta mesoterapia", "tricologo"),
        ("extension cheratina I-tip", "extension_specialist"),
        ("allungamento volume capelli", "extension_specialist"),
        ("extension clip tape", "extension_specialist"),
    ])
    def test_hair_sub_vertical_detection(self, text, expected_sub):
        r = extract_vertical_entities(text, "hair")
        assert r.sub_vertical == expected_sub, (
            f"Expected sub_vertical={expected_sub!r} for {text!r}, got {r.sub_vertical!r}"
        )

    @pytest.mark.parametrize("text", [
        "vorrei un taglio scalato",
        "fare la piega",
        "una permanente ai capelli",
        "meches colpi di sole",
    ])
    def test_hair_unknown_returns_none(self, text):
        r = extract_vertical_entities(text, "hair")
        assert r.sub_vertical is None, (
            f"Expected sub_vertical=None for {text!r}, got {r.sub_vertical!r}"
        )

    @pytest.mark.parametrize("text,expected_sub", [
        ("barba sfumata contorno", "barbiere"),
        ("fade skin fade", "barbiere"),
        ("correzione colore Olaplex", "color_specialist"),
        ("caduta capelli analisi", "tricologo"),
        ("extension cheratina allungamento", "extension_specialist"),
    ])
    def test_salone_alias_entity_extraction(self, text, expected_sub):
        """salone key must give same sub_vertical as hair key."""
        r_hair = extract_vertical_entities(text, "hair")
        r_salone = extract_vertical_entities(text, "salone")
        assert r_salone.sub_vertical == r_hair.sub_vertical, (
            f"salone and hair entity extraction disagree for {text!r}: "
            f"salone={r_salone.sub_vertical!r}, hair={r_hair.sub_vertical!r}"
        )
        assert r_salone.sub_vertical == expected_sub, (
            f"Expected {expected_sub!r} for salone vertical with {text!r}, got {r_salone.sub_vertical!r}"
        )


# =============================================================================
# BEAUTY ENTITY EXTRACTION
# =============================================================================

class TestBeautyEntityExtraction:
    """Beauty vertical entity extraction detects sub-verticals."""

    @pytest.mark.parametrize("text,expected_sub", [
        ("pulizia viso profonda", "estetista_viso"),
        ("radiofrequenza viso lifting", "estetista_viso"),
        ("dermaplaning viso", "estetista_viso"),
        ("microneedling trattamento", "estetista_viso"),
        ("massaggio drenante anticellulite", "estetista_corpo"),
        ("linfodrenaggio gambe pressoterapia", "estetista_corpo"),
        ("cavitazione radiofrequenza corpo", "estetista_corpo"),
        ("ricostruzione unghie gel", "nail_specialist"),
        ("fill-in gel unghie", "nail_specialist"),
        ("nail art forma coffin", "nail_specialist"),
        ("epilazione laser diodo", "epilazione_laser"),
        ("IPL patch test gambe", "epilazione_laser"),
        ("circuito spa hammam", "spa"),
        ("massaggio ayurvedico spa rilassante", "spa"),
        ("day spa percorso benessere", "spa"),
    ])
    def test_beauty_sub_vertical_detection(self, text, expected_sub):
        r = extract_vertical_entities(text, "beauty")
        assert r.sub_vertical == expected_sub, (
            f"Expected sub_vertical={expected_sub!r} for {text!r}, got {r.sub_vertical!r}"
        )

    @pytest.mark.parametrize("text", [
        "prenotare un appuntamento",
        "trattamento benessere generico",
        "servizio al centro estetico",
    ])
    def test_beauty_unknown_returns_none(self, text):
        r = extract_vertical_entities(text, "beauty")
        assert r.sub_vertical is None, (
            f"Expected sub_vertical=None for {text!r}, got {r.sub_vertical!r}"
        )
