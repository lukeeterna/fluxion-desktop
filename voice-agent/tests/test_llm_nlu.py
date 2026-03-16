"""
Tests for the LLM-based NLU engine (2026 architecture).
Tests Layer 0 (profanity + fast path) and Layer 2 (template fallback).
Layer 1 (LLM) tested separately with live API calls.
"""

import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlu.schemas import NLUResult, NLUEntities, SaraIntent, Sentiment
from nlu.template_fallback import classify_template, check_profanity, INTENT_TEMPLATES
from nlu.llm_nlu import LLMNlu, _FAST_PATH
from nlu.providers import ProviderConfig, ProviderRotation


# ─────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────

class TestNLUSchemas:
    def test_sara_intent_values(self):
        """All core intents exist."""
        assert SaraIntent.PRENOTAZIONE.value == "PRENOTAZIONE"
        assert SaraIntent.CANCELLAZIONE.value == "CANCELLAZIONE"
        assert SaraIntent.SPOSTAMENTO.value == "SPOSTAMENTO"
        assert SaraIntent.WAITLIST.value == "WAITLIST"
        assert SaraIntent.CONFERMA.value == "CONFERMA"
        assert SaraIntent.RIFIUTO.value == "RIFIUTO"
        assert SaraIntent.CORREZIONE.value == "CORREZIONE"
        assert SaraIntent.OSCENITA.value == "OSCENITA"

    def test_nlu_result_from_llm_json(self):
        """Parse LLM structured output correctly."""
        data = {
            "intent": "PRENOTAZIONE",
            "entities": {
                "nome": "Franco",
                "cognome": "De Cillis",
                "servizio": "taglio",
            },
            "sentiment": "POSITIVO",
            "correction_field": None,
            "confidence": 0.95,
        }
        result = NLUResult.from_llm_json(data, provider="groq", latency_ms=150)
        assert result.intent == SaraIntent.PRENOTAZIONE
        assert result.entities.nome == "Franco"
        assert result.entities.cognome == "De Cillis"
        assert result.entities.servizio == "taglio"
        assert result.sentiment == Sentiment.POSITIVO
        assert result.confidence == 0.95
        assert result.provider == "groq"

    def test_nlu_result_from_llm_json_unknown_intent(self):
        """Unknown intent falls back to ALTRO."""
        data = {"intent": "NONEXISTENT", "sentiment": "NEUTRO", "confidence": 0.5}
        result = NLUResult.from_llm_json(data)
        assert result.intent == SaraIntent.ALTRO

    def test_nlu_result_fallback(self):
        """Fallback result is safe default."""
        result = NLUResult.fallback("test input")
        assert result.intent == SaraIntent.ALTRO
        assert result.confidence == 0.0
        assert result.provider == "fallback"

    def test_entities_to_dict_filters_none(self):
        """to_dict only includes non-None fields."""
        entities = NLUEntities(nome="Franco", cognome=None, servizio="taglio")
        d = entities.to_dict()
        assert "nome" in d
        assert "servizio" in d
        assert "cognome" not in d

    def test_entities_has_any(self):
        assert NLUEntities(nome="Franco").has_any()
        assert not NLUEntities().has_any()

    def test_json_instruction_valid(self):
        """SARA_NLU_JSON_INSTRUCTION contains key fields."""
        from nlu.schemas import SARA_NLU_JSON_INSTRUCTION
        assert "intent" in SARA_NLU_JSON_INSTRUCTION
        assert "entities" in SARA_NLU_JSON_INSTRUCTION
        assert "sentiment" in SARA_NLU_JSON_INSTRUCTION

    def test_correction_result(self):
        """Correction intent includes field."""
        data = {
            "intent": "CORREZIONE",
            "entities": {"cognome": "De Cillis"},
            "sentiment": "NEUTRO",
            "correction_field": "cognome",
            "confidence": 0.9,
        }
        result = NLUResult.from_llm_json(data)
        assert result.intent == SaraIntent.CORREZIONE
        assert result.correction_field == "cognome"
        assert result.entities.cognome == "De Cillis"


# ─────────────────────────────────────────────────────────────────
# Profanity Filter
# ─────────────────────────────────────────────────────────────────

class TestProfanityFilter:
    def test_detects_profanity(self):
        assert check_profanity("vaffanculo")
        assert check_profanity("sei uno stronzo")
        assert check_profanity("che cazzo vuoi")

    def test_clean_text_passes(self):
        assert not check_profanity("vorrei prenotare un taglio")
        assert not check_profanity("buongiorno, sono Marco")
        assert not check_profanity("posso avere un appuntamento domani?")

    def test_multi_word_profanity(self):
        assert check_profanity("sei figlio di puttana")
        assert check_profanity("questo posto è di merda")


# ─────────────────────────────────────────────────────────────────
# Template Fallback
# ─────────────────────────────────────────────────────────────────

class TestTemplateFallback:
    def test_exact_match(self):
        intent, conf = classify_template("vorrei prenotare")
        assert intent == "PRENOTAZIONE"
        assert conf > 0.9

    def test_fuzzy_match_prenotazione(self):
        intent, conf = classify_template("voglio prenotarmi per un appuntamento")
        assert intent == "PRENOTAZIONE"
        assert conf > 0.5

    def test_cancellazione(self):
        intent, conf = classify_template("devo cancellare l'appuntamento")
        assert intent == "CANCELLAZIONE"
        assert conf > 0.6

    def test_spostamento(self):
        intent, conf = classify_template("posso spostare a domani?")
        assert intent == "SPOSTAMENTO"
        assert conf > 0.5

    def test_waitlist(self):
        intent, conf = classify_template("mettimi in lista d'attesa")
        assert intent == "WAITLIST"
        assert conf > 0.5

    def test_conferma(self):
        intent, conf = classify_template("sì")
        assert intent == "CONFERMA"
        assert conf > 0.9

    def test_rifiuto(self):
        intent, conf = classify_template("no")
        assert intent == "RIFIUTO"
        assert conf > 0.9

    def test_chiusura(self):
        intent, conf = classify_template("arrivederci")
        assert intent == "CHIUSURA"
        assert conf > 0.9

    def test_escalation(self):
        intent, conf = classify_template("voglio parlare con una persona")
        assert intent == "ESCALATION"
        assert conf > 0.5

    def test_profanity_via_template(self):
        intent, conf = classify_template("vaffanculo")
        assert intent == "OSCENITA"
        assert conf > 0.9

    def test_unknown_text(self):
        intent, conf = classify_template("il cielo è azzurro e le nuvole bianche")
        # Should either be ALTRO or very low confidence
        assert conf < 0.7 or intent == "ALTRO"

    def test_empty_text(self):
        intent, conf = classify_template("")
        assert intent == "ALTRO"
        assert conf == 0.0


# ─────────────────────────────────────────────────────────────────
# Fast Path
# ─────────────────────────────────────────────────────────────────

class TestFastPath:
    def test_all_fast_path_entries_are_valid_intents(self):
        for word, intent in _FAST_PATH.items():
            assert isinstance(intent, SaraIntent), f"'{word}' maps to invalid intent"

    def test_fast_path_covers_basics(self):
        assert "sì" in _FAST_PATH
        assert "si" in _FAST_PATH
        assert "no" in _FAST_PATH
        assert "ok" in _FAST_PATH
        assert "aiuto" in _FAST_PATH
        assert "arrivederci" in _FAST_PATH


# ─────────────────────────────────────────────────────────────────
# Provider Config
# ─────────────────────────────────────────────────────────────────

class TestProviderConfig:
    def test_unconfigured_provider(self):
        p = ProviderConfig(
            name="test",
            base_url="https://test.com/v1",
            model="test-model",
            api_key_env="NONEXISTENT_KEY_12345",
        )
        assert not p.is_configured
        assert p.api_key is None

    def test_provider_rotation_no_keys(self):
        """Rotation with no configured providers is safe."""
        rotation = ProviderRotation(providers=[
            ProviderConfig(
                name="fake",
                base_url="https://fake.com",
                model="fake",
                api_key_env="NONEXISTENT_KEY_99999",
            ),
        ])
        assert not rotation.has_providers


# ─────────────────────────────────────────────────────────────────
# LLMNlu Integration (offline — tests fast_path + template only)
# ─────────────────────────────────────────────────────────────────

class TestLLMNluOffline:
    """Test LLMNlu without any API keys (Layer 0 + Layer 2 only)."""

    @pytest.fixture
    def nlu(self):
        # Create with no providers configured
        rotation = ProviderRotation(providers=[])
        return LLMNlu(providers=rotation)

    @pytest.mark.asyncio
    async def test_fast_path_si(self, nlu):
        result = await nlu.extract("sì")
        assert result.intent == SaraIntent.CONFERMA
        assert result.provider == "fast_path"
        assert result.latency_ms < 10

    @pytest.mark.asyncio
    async def test_fast_path_no(self, nlu):
        result = await nlu.extract("no")
        assert result.intent == SaraIntent.RIFIUTO
        assert result.provider == "fast_path"

    @pytest.mark.asyncio
    async def test_profanity_blocked(self, nlu):
        result = await nlu.extract("vaffanculo")
        assert result.intent == SaraIntent.OSCENITA
        assert result.sentiment == Sentiment.AGGRESSIVO
        assert result.provider == "profanity_filter"

    @pytest.mark.asyncio
    async def test_template_fallback_prenotazione(self, nlu):
        result = await nlu.extract("vorrei prenotare un appuntamento")
        assert result.intent == SaraIntent.PRENOTAZIONE
        assert result.provider == "template_fallback"

    @pytest.mark.asyncio
    async def test_template_fallback_cancellazione(self, nlu):
        result = await nlu.extract("cancella il mio appuntamento")
        assert result.intent == SaraIntent.CANCELLAZIONE
        assert result.provider == "template_fallback"

    @pytest.mark.asyncio
    async def test_unknown_falls_to_altro(self, nlu):
        result = await nlu.extract("la capitale della Francia è Parigi")
        # Either ALTRO or low confidence
        assert result.confidence < 0.7 or result.intent == SaraIntent.ALTRO


# ─────────────────────────────────────────────────────────────────
# NLU Result serialization
# ─────────────────────────────────────────────────────────────────

class TestNLUResultSerialization:
    def test_to_dict(self):
        result = NLUResult(
            intent=SaraIntent.PRENOTAZIONE,
            entities=NLUEntities(nome="Franco", servizio="taglio"),
            sentiment=Sentiment.POSITIVO,
            confidence=0.95,
            provider="groq",
            latency_ms=150,
        )
        d = result.to_dict()
        assert d["intent"] == "PRENOTAZIONE"
        assert d["entities"]["nome"] == "Franco"
        assert d["sentiment"] == "POSITIVO"
        assert d["provider"] == "groq"
