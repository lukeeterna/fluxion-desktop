"""
Tests for Wave B NLU patterns: wellness and medico verticals.
Phase: f-sara-nlu-patterns
Wave: 2 (sequential after Wave A hair+beauty)

Run with: pytest voice-agent/tests/test_wellness_medico_nlu.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from italian_regex import check_vertical_guardrail, VERTICAL_SERVICES
from entity_extractor import extract_vertical_entities


# =============================================================================
# WELLNESS GUARDRAILS
# =============================================================================

class TestWellnessGuardrails:
    """Wellness vertical blocks hair, auto, medical OOS; allows fitness/wellness services."""

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "tinta capelli scura",
        "messa in piega capelli",
        "extension capelli cheratina",
        "ritocco radici bianchi",
        "trattamento capelli keratina",
    ])
    def test_wellness_blocks_hair_oos(self, text):
        r = check_vertical_guardrail(text, "wellness")
        assert r.blocked is True, f"Expected blocked=True for: {text!r}"
        assert r.vertical == "wellness"

    @pytest.mark.parametrize("text", [
        "cambio olio motore",
        "tagliando auto scaduto",
        "cambio gomme invernali",
        "portare la macchina dal meccanico",
        "revisione auto ministeriale",
    ])
    def test_wellness_blocks_auto_oos(self, text):
        r = check_vertical_guardrail(text, "wellness")
        assert r.blocked is True, f"Expected blocked=True for: {text!r}"

    @pytest.mark.parametrize("text", [
        "ricetta medica rinnovo",
        "visita cardiologica urgente",
        "esame del sangue",
        "certificato idoneità",
    ])
    def test_wellness_blocks_medical_oos(self, text):
        # NOTE: 'fisioterapia' alone is NOT blocked in wellness (valid service)
        r = check_vertical_guardrail(text, "wellness")
        assert r.blocked is True, f"Expected blocked=True for: {text!r}"

    @pytest.mark.parametrize("text", [
        "corso di yoga mattutino",
        "pilates posturale",
        "yin yoga",
        "WOD crossfit",
        "AMRAP metcon",
        "personal trainer disponibile",
        "scheda allenamento personalizzata",
        "corsia riservata piscina",
        "baby nuoto corso",
        "acquacorrida acqua fitness",
        "judo cintura nera",
        "BJJ muay thai",
        "abbonamento mensile palestra",
        "sala pesi allenamento",
        "kickboxing lezione",
        "spinning indoor cycling",
        "master nuoto vasca 50m",
    ])
    def test_wellness_allows_in_scope(self, text):
        r = check_vertical_guardrail(text, "wellness")
        assert r.blocked is False, f"Expected blocked=False for: {text!r}"

    def test_wellness_fisioterapia_not_blocked(self):
        """fisioterapia is a valid service in wellness context — must NOT be blocked."""
        r = check_vertical_guardrail("fisioterapia post-allenamento", "wellness")
        assert r.blocked is False

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "cambio olio motore",
        "ricetta medica rinnovo",
        "esame del sangue",
        "tinta capelli scura",
    ])
    def test_wellness_legacy_palestra_key(self, text):
        """Legacy 'palestra' key must behave identically to 'wellness'."""
        r_wellness = check_vertical_guardrail(text, "wellness")
        r_palestra = check_vertical_guardrail(text, "palestra")
        assert r_wellness.blocked == r_palestra.blocked, (
            f"palestra and wellness differ for: {text!r}"
        )
        assert r_palestra.blocked is True, f"Expected palestra blocked=True for: {text!r}"

    def test_wellness_redirect_response_set(self):
        r = check_vertical_guardrail("taglio capelli donna", "wellness")
        assert r.blocked is True
        assert r.redirect_response != ""
        assert len(r.redirect_response) > 10


# =============================================================================
# MEDICO GUARDRAILS
# =============================================================================

class TestMedicoGuardrails:
    """Medico vertical blocks hair, beauty nail, auto, palestra OOS; allows medical services."""

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "tinta capelli biondi",
        "messa in piega capelli",
        "la manicure mani",
        "ceretta gambe completa",
        "trucco sposa",
    ])
    def test_medico_blocks_hair_oos(self, text):
        r = check_vertical_guardrail(text, "medico")
        assert r.blocked is True, f"Expected blocked=True for: {text!r}"
        assert r.vertical == "medico"

    @pytest.mark.parametrize("text", [
        "abbonamento mensile palestra",
        "corso di yoga",
        "personal trainer",
        "sala pesi attrezzata",
        "allenamento funzionale personalizzato",
    ])
    def test_medico_blocks_palestra_oos(self, text):
        r = check_vertical_guardrail(text, "medico")
        assert r.blocked is True, f"Expected blocked=True for: {text!r}"

    @pytest.mark.parametrize("text", [
        "cambio olio motore",
        "fare il tagliando",
        "dal meccanico",
        "cambio gomme invernali",
    ])
    def test_medico_blocks_auto_oos(self, text):
        r = check_vertical_guardrail(text, "medico")
        assert r.blocked is True, f"Expected blocked=True for: {text!r}"

    @pytest.mark.parametrize("text", [
        "visita medica",
        "consulto specialistico",
        "esame del sangue analisi",
        "fisioterapia posturale",
        "ciclo di fisioterapia",
        "osteopatia manipolazione",
        "seduta psicologo",
        "terapia cognitivo-comportamentale",
        "nutrizionista piano alimentare",
        "podologia plantari su misura",
        "dentista pulizia denti",
        "sbiancamento denti",
        "psicoterapeuta EMDR",
        "analisi bioimpedenziometrica BIA",
        "invisalign aligner dentale",
        "fisioterapista rieducazione",
        "trattamento osteopatico",
    ])
    def test_medico_allows_in_scope(self, text):
        r = check_vertical_guardrail(text, "medico")
        assert r.blocked is False, f"Expected blocked=False for: {text!r}"

    @pytest.mark.parametrize("text", [
        "taglio capelli donna",
        "abbonamento mensile palestra",
        "cambio olio motore",
        "fare il tagliando",
        "corso di yoga",
    ])
    def test_medico_legacy_medical_key(self, text):
        """Legacy 'medical' key must behave identically to 'medico'."""
        r_medico = check_vertical_guardrail(text, "medico")
        r_medical = check_vertical_guardrail(text, "medical")
        assert r_medico.blocked == r_medical.blocked, (
            f"medico and medical differ for: {text!r}"
        )
        assert r_medical.blocked is True, f"Expected medical blocked=True for: {text!r}"

    def test_medico_redirect_response_set(self):
        r = check_vertical_guardrail("taglio capelli donna", "medico")
        assert r.blocked is True
        assert r.redirect_response != ""
        assert len(r.redirect_response) > 10


# =============================================================================
# WELLNESS ENTITY EXTRACTION
# =============================================================================

class TestWellnessEntityExtraction:
    """Wellness sub-vertical detection via extract_vertical_entities()."""

    @pytest.mark.parametrize("text,expected_sub_vertical", [
        ("corso di yoga nidra", "yoga_pilates"),
        ("hot yoga lezione", "yoga_pilates"),
        ("pilates posturale lezione", "yoga_pilates"),
        ("yin yoga mattutino", "yoga_pilates"),
        ("pilates reformer avanzato", "yoga_pilates"),
        ("WOD crossfit mattina", "crossfit"),
        ("AMRAP metcon allenamento", "crossfit"),
        ("fondamentali crossfit sessione", "crossfit"),
        ("personal trainer scheda allenamento", "personal_trainer"),
        ("plicometria test VO2 max", "personal_trainer"),
        ("allenamento personalizzato programma", "personal_trainer"),
        ("corsia riservata piscina", "piscina"),
        ("baby nuoto corso bambini", "piscina"),
        ("acquacorrida master nuoto", "piscina"),
        ("judo kata kumite", "arti_marziali"),
        ("BJJ muay thai allenamento", "arti_marziali"),
        ("MMA krav maga", "arti_marziali"),
    ])
    def test_wellness_sub_vertical_detection(self, text, expected_sub_vertical):
        r = extract_vertical_entities(text, "wellness")
        assert r.sub_vertical == expected_sub_vertical, (
            f"Expected {expected_sub_vertical!r} for {text!r}, got {r.sub_vertical!r}"
        )

    @pytest.mark.parametrize("text", [
        "abbonamento annuale",
        "ingresso singolo",
        "spinning cyclette",
        "sauna bagno turco",
    ])
    def test_wellness_unknown_returns_none(self, text):
        """Inputs with no sub-vertical keywords return sub_vertical=None."""
        r = extract_vertical_entities(text, "wellness")
        assert r.sub_vertical is None, (
            f"Expected sub_vertical=None for {text!r}, got {r.sub_vertical!r}"
        )

    @pytest.mark.parametrize("text,expected_sub_vertical", [
        ("corso di yoga nidra", "yoga_pilates"),
        ("WOD crossfit mattina", "crossfit"),
        ("personal trainer scheda allenamento", "personal_trainer"),
        ("corsia riservata piscina", "piscina"),
        ("judo kata kumite", "arti_marziali"),
    ])
    def test_palestra_alias_entity_extraction(self, text, expected_sub_vertical):
        """Legacy 'palestra' key works identically to 'wellness' for entity extraction."""
        r_wellness = extract_vertical_entities(text, "wellness")
        r_palestra = extract_vertical_entities(text, "palestra")
        assert r_palestra.sub_vertical == expected_sub_vertical, (
            f"Expected {expected_sub_vertical!r} for palestra+{text!r}, got {r_palestra.sub_vertical!r}"
        )
        assert r_wellness.sub_vertical == r_palestra.sub_vertical


# =============================================================================
# MEDICO ENTITY EXTRACTION
# =============================================================================

class TestMedicoEntityExtraction:
    """Medico specialty detection via extract_vertical_entities()."""

    @pytest.mark.parametrize("text,expected_specialty", [
        ("fisioterapia posturale", "fisioterapia"),
        ("tecarterapia trattamento", "fisioterapia"),
        ("rieducazione motoria seduta", "fisioterapia"),
        ("kinesiotaping applicazione", "fisioterapia"),
        ("seduta psicologo TCC", "psicologo"),
        ("EMDR terapia sessione", "psicologo"),
        ("psicoterapeuta appuntamento", "psicologo"),
        ("nutrizionista BIA analisi", "nutrizionista"),
        ("piano alimentare personalizzato", "nutrizionista"),
        ("dietologo consulenza", "nutrizionista"),
        ("podologo plantari su misura", "podologo"),
        ("verruca plantare trattamento", "podologo"),
        ("unghia incarnita correzione", "podologo"),
        ("osteopata manipolazione", "osteopata"),
        ("trattamento cranio-sacrale osteopatia", "osteopata"),
        ("osteopatia viscerale seduta", "osteopata"),
        ("dentista sbiancamento denti", "odontoiatria"),
        ("invisalign aligner ortodonzia", "odontoiatria"),
        ("visita cardiologica cuore", "cardiologia"),
    ])
    def test_medico_specialty_detection(self, text, expected_specialty):
        r = extract_vertical_entities(text, "medico")
        assert r.specialty == expected_specialty, (
            f"Expected {expected_specialty!r} for {text!r}, got {r.specialty!r}"
        )

    @pytest.mark.parametrize("text,expected_specialty", [
        ("fisioterapia posturale", "fisioterapia"),
        ("seduta psicologo TCC", "psicologo"),
        ("nutrizionista BIA analisi", "nutrizionista"),
        ("podologo plantari su misura", "podologo"),
        ("osteopata manipolazione", "osteopata"),
        ("dentista sbiancamento denti", "odontoiatria"),
    ])
    def test_medico_legacy_medical_specialty(self, text, expected_specialty):
        """Legacy 'medical' key works identically to 'medico' for specialty detection."""
        r_medico = extract_vertical_entities(text, "medico")
        r_medical = extract_vertical_entities(text, "medical")
        assert r_medical.specialty == expected_specialty, (
            f"Expected {expected_specialty!r} for medical+{text!r}, got {r_medical.specialty!r}"
        )
        assert r_medico.specialty == r_medical.specialty

    def test_medico_urgency_preserved(self):
        """Urgency detection must still work alongside specialty."""
        r = extract_vertical_entities("fisioterapia urgente appuntamento", "medico")
        assert r.specialty == "fisioterapia"
        assert r.urgency == "urgente"

    def test_medico_unknown_specialty_returns_none(self):
        r = extract_vertical_entities("vorrei prenotare domani", "medico")
        assert r.specialty is None

    def test_wellness_services_dict_has_keys(self):
        """VERTICAL_SERVICES[wellness] has at least 15 service groups."""
        assert len(VERTICAL_SERVICES["wellness"]) >= 15

    def test_medico_services_dict_has_keys(self):
        """VERTICAL_SERVICES[medico] has at least 18 service groups."""
        assert len(VERTICAL_SERVICES["medico"]) >= 18
