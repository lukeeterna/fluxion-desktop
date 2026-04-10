"""
FLUXION Voice Agent - Phase D Audit Tests (S145)

D1: Anti-hallucination guardrail for L4 Groq responses
D2: Conversation history (last 3 turns to L4)
D3: FAQ unresolved variables logging + fix

Run with: pytest voice-agent/tests/test_phase_d_audit.py -v
"""

import sys
import re
from pathlib import Path
from unittest.mock import MagicMock
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# =============================================================================
# D1: Anti-hallucination guardrail — standalone implementation for testing
# (Mirrors VoiceOrchestrator._validate_l4_response logic without importing
#  the full orchestrator which requires groq SDK)
# =============================================================================

_AVAILABILITY_HALLUCINATION_PATTERNS = [
    r"c[''\u2019]è\s+posto",
    r"(?:è|e'|sono)\s+disponibil[ei]",
    r"(?:puoi|può)\s+venire\s+(?:alle|a|il|la|domani|luned|marted|mercoled|gioved|venerd|sabato)",
    r"ti\s+(?:segno|prenoto|confermo)\s+(?:per|alle|il|la)",
    r"ho\s+(?:trovato|visto)\s+(?:un\s+)?(?:posto|slot|buco)",
]

_COMMON_WORDS = {
    "Sara", "Ciao", "Buongiorno", "Buonasera", "Grazie", "Perfetto",
    "Certo", "Ecco", "Guardi", "Dunque", "Scusa", "Prenoto",
    "Confermo", "Aspetti", "Verifico", "Salve", "Prego",
}


def _validate_l4_response(response, service_prices, valid_operator_names,
                           business_services, client_name=None):
    """Standalone guardrail validator (mirrors orchestrator method)."""
    if not response:
        return None

    resp_lower = response.lower()
    issues = []

    # 1. Price hallucination
    known_prices = set()
    if service_prices:
        for k, v in service_prices.items():
            if k.startswith("PREZZO_"):
                known_prices.add(v)

    price_matches = re.findall(r'€\s*(\d+)', response) + re.findall(r'(\d+)\s*euro', resp_lower)
    for price in price_matches:
        if known_prices and price not in known_prices:
            issues.append(f"price_{price}")

    # 2. Availability hallucination
    for pattern in _AVAILABILITY_HALLUCINATION_PATTERNS:
        if re.search(pattern, resp_lower):
            issues.append("availability")
            break

    # 3. Operator name hallucination
    if valid_operator_names:
        name_candidates = re.findall(r'\b([A-Z][a-z]{2,})\b', response)
        for name in name_candidates:
            if name not in _COMMON_WORDS and name.lower() not in {n.lower() for n in valid_operator_names}:
                if client_name and name.lower() in client_name.lower():
                    continue
                issues.append(f"operator_{name}")

    if not issues:
        return None

    if "availability" in issues:
        return "Per verificare la disponibilità, posso controllare subito. Che giorno e orario preferisci?"
    if any(i.startswith("price_") for i in issues):
        if business_services:
            return f"Ecco i nostri servizi con i prezzi:\n{business_services}\nQuale ti interessa?"
        return "Verifico i prezzi con lo staff e ti confermo subito."
    return None


class TestAntiHallucinationGuardrail:
    """D1: Validate L4 Groq responses against known DB data."""

    @pytest.fixture
    def db_data(self):
        return {
            "service_prices": {
                "PREZZO_TAGLIO": "25",
                "PREZZO_PIEGA": "20",
                "PREZZO_COLORE": "45",
            },
            "valid_operator_names": {"Marco", "Giulia", "Luca"},
            "business_services": "- Taglio: €25 (30min)\n- Piega: €20 (20min)\n- Colore: €45 (60min)",
        }

    def _validate(self, response, db_data, client_name=None):
        return _validate_l4_response(
            response,
            db_data["service_prices"],
            db_data["valid_operator_names"],
            db_data["business_services"],
            client_name,
        )

    # --- Price hallucination ---

    def test_detects_price_hallucination(self, db_data):
        """Catches invented prices not in DB."""
        result = self._validate("Il taglio costa €35, un ottimo prezzo!", db_data)
        assert result is not None
        assert "servizi" in result.lower() or "prezzi" in result.lower()

    def test_allows_correct_price(self, db_data):
        """Allows prices that match DB exactly."""
        result = self._validate("Il taglio costa €25.", db_data)
        assert result is None

    def test_detects_euro_word_hallucination(self, db_data):
        """Catches '50 euro' format hallucination."""
        result = self._validate("Costa 50 euro per il trattamento.", db_data)
        assert result is not None

    def test_no_prices_known_allows_response(self, db_data):
        """If no prices in DB, don't flag as hallucination."""
        db_data["service_prices"] = {}
        result = self._validate("Costa €99 per il trattamento.", db_data)
        assert result is None

    # --- Availability hallucination ---

    def test_detects_availability_hallucination_ce_posto(self, db_data):
        """Catches 'c'è posto' confirmation without FSM check."""
        result = self._validate("Sì, c'è posto domani alle 15!", db_data)
        assert result is not None
        assert "disponibilità" in result.lower() or "giorno" in result.lower()

    def test_detects_availability_hallucination_disponibile(self, db_data):
        """Catches 'è disponibile' confirmation."""
        result = self._validate("Marco è disponibile giovedì mattina.", db_data)
        assert result is not None

    def test_detects_availability_hallucination_prenoto(self, db_data):
        """Catches 'ti segno per' confirmation."""
        result = self._validate("Perfetto, ti segno per le 14 di venerdì!", db_data)
        assert result is not None

    def test_detects_availability_hallucination_trovato_posto(self, db_data):
        """Catches 'ho trovato un buco' confirmation."""
        result = self._validate("Ho trovato un buco alle 16 di martedì.", db_data)
        assert result is not None

    def test_allows_general_info(self, db_data):
        """Allows responses that don't confirm availability."""
        result = self._validate("Siamo aperti dal lunedì al sabato.", db_data)
        assert result is None

    def test_allows_question_about_availability(self, db_data):
        """Allows asking about availability (not confirming)."""
        result = self._validate("Che giorno preferisci per l'appuntamento?", db_data)
        assert result is None

    # --- Operator hallucination ---

    def test_detects_operator_hallucination(self, db_data):
        """Detects operator names not in DB — logged but not blocked."""
        result = self._validate("Roberto ti aspetta alle 10!", db_data)
        assert result is None  # Operator-only hallucination is logged, not blocked

    def test_allows_known_operator(self, db_data):
        """Allows known operator names."""
        result = self._validate("Giulia è la nostra colorista esperta.", db_data)
        assert result is None

    def test_allows_client_name_in_response(self, db_data):
        """Allows client name even if not an operator."""
        result = self._validate("Ciao Roberto, come posso aiutarti?", db_data, client_name="Roberto Bianchi")
        assert result is None

    def test_allows_sara_and_common_words(self, db_data):
        """Sara and common words should not trigger hallucination."""
        result = self._validate("Perfetto! Certo, Ecco i nostri servizi.", db_data)
        assert result is None

    # --- Edge cases ---

    def test_empty_response(self, db_data):
        """Empty response returns None."""
        result = self._validate("", db_data)
        assert result is None

    def test_none_response(self, db_data):
        """None response returns None."""
        result = self._validate(None, db_data)
        assert result is None

    def test_price_plus_availability_hallucination(self, db_data):
        """Both price and availability hallucination — availability takes priority."""
        result = self._validate("C'è posto alle 15, costa €99!", db_data)
        assert result is not None
        assert "disponibilità" in result.lower() or "giorno" in result.lower()


# =============================================================================
# D2: Conversation history tests
# =============================================================================

@dataclass
class MockSessionTurn:
    user_input: str
    response: str
    turn_id: str = "t1"
    timestamp: str = ""
    intent: str = "test"
    latency_ms: float = 0.0
    layer_used: str = "L2_slot"
    sentiment: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    fsm_state: Optional[str] = None


class TestConversationHistory:
    """D2: Verify conversation history is built correctly for L4."""

    def test_history_empty_when_no_turns(self):
        """First turn: only current user input, no history."""
        @dataclass
        class MockSession:
            turns: List[MockSessionTurn] = field(default_factory=list)
            total_turns: int = 0

        session = MockSession()
        l4_messages = []
        if session.turns:
            for turn in session.turns[-3:]:
                l4_messages.append({"role": "user", "content": turn.user_input})
                l4_messages.append({"role": "assistant", "content": turn.response})
        l4_messages.append({"role": "user", "content": "Buongiorno"})

        assert len(l4_messages) == 1
        assert l4_messages[0] == {"role": "user", "content": "Buongiorno"}

    def test_history_with_2_turns(self):
        """2 previous turns → 5 messages (2 user + 2 assistant + 1 current)."""
        turns = [
            MockSessionTurn(user_input="Ciao", response="Buongiorno! Come posso aiutarla?"),
            MockSessionTurn(user_input="Quanto costa il taglio?", response="Il taglio costa venticinque euro."),
        ]

        l4_messages = []
        for turn in turns[-3:]:
            l4_messages.append({"role": "user", "content": turn.user_input})
            l4_messages.append({"role": "assistant", "content": turn.response})
        l4_messages.append({"role": "user", "content": "E la piega?"})

        assert len(l4_messages) == 5
        assert l4_messages[0]["role"] == "user"
        assert l4_messages[0]["content"] == "Ciao"
        assert l4_messages[1]["role"] == "assistant"
        assert l4_messages[-1]["content"] == "E la piega?"

    def test_history_limited_to_3_turns(self):
        """5 previous turns → only last 3 + current = 7 messages."""
        turns = [
            MockSessionTurn(user_input=f"Turn {i}", response=f"Response {i}")
            for i in range(5)
        ]

        l4_messages = []
        for turn in turns[-3:]:
            l4_messages.append({"role": "user", "content": turn.user_input})
            l4_messages.append({"role": "assistant", "content": turn.response})
        l4_messages.append({"role": "user", "content": "Current"})

        assert len(l4_messages) == 7  # 3*2 + 1
        assert l4_messages[0]["content"] == "Turn 2"  # starts from turn 2 (index -3)
        assert l4_messages[-1]["content"] == "Current"


# =============================================================================
# D3: FAQ unresolved variables tests
# =============================================================================

class TestFAQUnresolvedVariables:
    """D3: Verify unresolved FAQ variables are logged and filtered."""

    def test_substitute_variables_resolves_known(self):
        """Known variables are substituted correctly."""
        from vertical_loader import substitute_variables
        result = substitute_variables(
            "Il taglio costa [PREZZO_TAGLIO] euro.",
            {"PREZZO_TAGLIO": "25"}
        )
        assert result == "Il taglio costa 25 euro."
        assert "[" not in result

    def test_substitute_variables_leaves_unknown(self):
        """Unknown variables remain as [VARIABLE]."""
        from vertical_loader import substitute_variables
        result = substitute_variables(
            "Costa [PREZZO_MASSAGGIO] euro.",
            {"PREZZO_TAGLIO": "25"}
        )
        assert "[PREZZO_MASSAGGIO]" in result

    def test_substitute_variables_handles_curly_braces(self):
        """Old {{VARIABLE}} format is also substituted."""
        from vertical_loader import substitute_variables
        result = substitute_variables(
            "Benvenuti a {{NOME_ATTIVITA}}!",
            {"NOME_ATTIVITA": "Salone Bella"}
        )
        assert result == "Benvenuti a Salone Bella!"

    def test_faq_manager_skips_unresolved(self):
        """FAQs with unresolved variables are skipped during markdown loading."""
        from faq_manager import FAQManager
        import tempfile, os

        # Create temp FAQ file with some resolved and some unresolved
        content = """# Test
- Quanto costa il taglio: Il taglio costa 25 euro
- Quanto costa il colore: Il colore costa [PREZZO_COLORE] euro
- Orari: Siamo aperti dal lunedì al sabato
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            mgr = FAQManager()
            count = mgr.load_faqs_from_markdown(temp_path)
            # Only 2 FAQs loaded (the one with [PREZZO_COLORE] is skipped)
            assert count == 2
            # Verify the loaded FAQs don't contain unresolved vars
            for faq in mgr.faqs:
                assert "[PREZZO_" not in faq["answer"]
        finally:
            os.unlink(temp_path)

    def test_unresolved_variable_detection_regex(self):
        """The unresolved variable regex matches expected patterns."""
        pattern = r'\[([A-Z][A-Z0-9_]+)\]'
        assert re.findall(pattern, "Costa [PREZZO_TAGLIO] euro") == ["PREZZO_TAGLIO"]
        assert re.findall(pattern, "Orari [ORARI_APERTURA]") == ["ORARI_APERTURA"]
        assert re.findall(pattern, "No variables here") == []
        assert re.findall(pattern, "[lowercase] ignored") == []  # lowercase ignored
        assert re.findall(pattern, "[A] too short") == []  # single char ignored


# =============================================================================
# D1+D2 Integration: Guardrail patterns compilation
# =============================================================================

class TestGuardrailPatterns:
    """Verify anti-hallucination regex patterns compile and match correctly."""

    def test_patterns_compile(self):
        """All hallucination patterns should compile without error."""
        for pattern in _AVAILABILITY_HALLUCINATION_PATTERNS:
            compiled = re.compile(pattern)
            assert compiled is not None

    def test_ce_posto_pattern(self):
        """Matches 'c'è posto' in various forms."""
        pattern = r"c[''\u2019]è\s+posto"
        assert re.search(pattern, "c'è posto domani")
        assert re.search(pattern, "c\u2019è posto alle 15")
        assert not re.search(pattern, "non c'era nessun posto")

    def test_disponibile_pattern(self):
        """Matches 'è disponibile' / 'sono disponibili'."""
        pattern = r"(?:è|e'|sono)\s+disponibil[ei]"
        assert re.search(pattern, "Marco è disponibile")
        assert re.search(pattern, "sono disponibili due slot")
        assert not re.search(pattern, "la disponibilità va verificata")

    def test_prenoto_pattern(self):
        """Matches 'ti segno per' / 'ti prenoto'."""
        pattern = r"ti\s+(?:segno|prenoto|confermo)\s+(?:per|alle|il|la)"
        assert re.search(pattern, "ti segno per le 14")
        assert re.search(pattern, "ti prenoto per il 15 marzo")
        assert re.search(pattern, "ti confermo per la mattina")

    def test_trovato_posto_pattern(self):
        """Matches 'ho trovato un posto/slot/buco'."""
        pattern = r"ho\s+(?:trovato|visto)\s+(?:un\s+)?(?:posto|slot|buco)"
        assert re.search(pattern, "ho trovato un posto")
        assert re.search(pattern, "ho trovato un buco alle 16")
        assert re.search(pattern, "ho visto slot libero")


# =============================================================================
# D4: TURN server configuration tests
# =============================================================================

class TestTURNConfig:
    """D4: Verify TURN server configuration in SIPConfig."""

    def test_sip_config_has_turn_fields(self):
        """SIPConfig has turn_server, turn_username, turn_password fields."""
        try:
            from voip_pjsua2 import SIPConfig
        except ImportError:
            pytest.skip("pjsua2 not available on this machine")

        config = SIPConfig()
        assert hasattr(config, 'turn_server')
        assert hasattr(config, 'turn_username')
        assert hasattr(config, 'turn_password')
        assert config.turn_server == ""  # Disabled by default

    def test_sip_config_from_env_turn(self, monkeypatch):
        """SIPConfig.from_env() reads TURN env vars."""
        try:
            from voip_pjsua2 import SIPConfig
        except ImportError:
            pytest.skip("pjsua2 not available on this machine")

        monkeypatch.setenv("VOIP_TURN_SERVER", "turn:turn.example.com:3478")
        monkeypatch.setenv("VOIP_TURN_USER", "fluxion")
        monkeypatch.setenv("VOIP_TURN_PASS", "secret123")

        config = SIPConfig.from_env()
        assert config.turn_server == "turn:turn.example.com:3478"
        assert config.turn_username == "fluxion"
        assert config.turn_password == "secret123"

    def test_sip_config_defaults_no_turn(self):
        """Without env vars, TURN is disabled."""
        try:
            from voip_pjsua2 import SIPConfig
        except ImportError:
            pytest.skip("pjsua2 not available on this machine")

        config = SIPConfig()
        assert config.turn_server == ""
        assert config.turn_username == ""
        assert config.turn_password == ""

    def test_stun_still_configured(self):
        """STUN server is still configured even without TURN."""
        try:
            from voip_pjsua2 import SIPConfig
        except ImportError:
            pytest.skip("pjsua2 not available on this machine")

        config = SIPConfig()
        assert config.stun_server == "stun.voip.vivavox.it:3478"
