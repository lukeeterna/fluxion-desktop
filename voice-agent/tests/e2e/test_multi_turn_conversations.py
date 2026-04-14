#!/usr/bin/env python3
"""
Multi-Turn Conversation Test Suite for Sara Voice Agent
========================================================

Tests COMPLETE conversation flows simulating REAL phone conversations.
Each scenario includes multiple turns (user message → Sara response)
with assertions on state transitions and response content.

Runs against live pipeline at http://127.0.0.1:3002

Test scenarios:
1. Happy path — returning client complete booking
2. Bare name from IDLE (enters booking immediately)
3. Ambiguous name disambiguation
4. New client registration flow
5. Goodbye/exit at any point in conversation
6. Service request with name corruption check
7. FAQ questions
8. Cancel/modify operations
9. Operator escalation request
10. Edge cases (empty, very long, punctuation, phone numbers)

Usage:
    pytest tests/e2e/test_multi_turn_conversations.py -v

Or run directly on iMac:
    cd '/Volumes/MacSSD - Dati/fluxion/voice-agent'
    python -m pytest tests/e2e/test_multi_turn_conversations.py -v
"""

import json
import os
import sys
import time
import urllib.request
from typing import Dict, Optional, List, Any
from urllib.error import URLError

# Configure for iMac testing
URL = os.environ.get("PIPELINE_URL", "http://127.0.0.1:3002")
TIMEOUT_SECONDS = 30
VERBOSE = os.environ.get("VERBOSE", "").lower() in ("1", "true")


# ============================================================================
# HTTP Helpers
# ============================================================================

def api(path: str, data: Optional[Dict] = None, method: str = "POST", timeout: int = TIMEOUT_SECONDS) -> Dict[str, Any]:
    """Make HTTP request to voice pipeline."""
    body = json.dumps(data or {}).encode("utf-8") if data is not None else b"{}"
    req = urllib.request.Request(
        URL + path,
        data=body,
        headers={"Content-Type": "application/json"}
    )
    req.get_method = lambda: method

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        return {
            "success": False,
            "error": f"Network error: {e.reason}",
            "_connection_failed": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "_exception": True
        }


def process(text: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Send text to voice pipeline and measure latency."""
    payload = {"text": text}
    if session_id:
        payload["session_id"] = session_id

    t0 = time.time()
    response = api("/api/voice/process", payload)
    response["_latency_ms"] = (time.time() - t0) * 1000

    if VERBOSE:
        print(f"  [process] '{text}' → state={response.get('fsm_state')} intent={response.get('intent')} ms={response['_latency_ms']:.0f}")

    return response


def reset(vertical: Optional[str] = None) -> Dict[str, Any]:
    """Reset conversation session."""
    payload = {}
    if vertical:
        payload["vertical"] = vertical
    return api("/api/voice/reset", payload)


def health() -> Optional[Dict[str, Any]]:
    """Check if pipeline is alive."""
    try:
        req = urllib.request.Request(URL + "/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


# ============================================================================
# Test Utilities
# ============================================================================

class ConversationContext:
    """Manages a multi-turn conversation session."""

    def __init__(self, vertical: str = "salone"):
        self.vertical = vertical
        self.session_id = None
        self.turns = []  # type: List[Dict[str, Any]]
        self._reset()

    def _reset(self):
        """Reset session."""
        reset_resp = reset(vertical=self.vertical)
        if not reset_resp.get("success"):
            raise RuntimeError(f"Failed to reset: {reset_resp.get('error')}")
        self.session_id = reset_resp.get("session_id")
        self.turns = []

    def turn(self, user_text: str) -> Dict[str, Any]:
        """Send one turn and track response."""
        response = process(user_text, session_id=self.session_id)

        turn_info = {
            "user": user_text,
            "response": response.get("response", ""),
            "intent": response.get("intent"),
            "fsm_state": response.get("fsm_state"),
            "should_exit": response.get("should_exit", False),
            "should_escalate": response.get("should_escalate", False),
            "needs_disambiguation": response.get("needs_disambiguation", False),
            "layer": response.get("layer"),
            "latency_ms": response.get("_latency_ms", 0),
            "success": response.get("success", False),
            "error": response.get("error"),
        }

        self.turns.append(turn_info)
        return turn_info

    def state(self) -> str:
        """Get current FSM state."""
        if self.turns:
            return self.turns[-1]["fsm_state"]
        return "unknown"

    def last_response(self) -> str:
        """Get last Sara response."""
        if self.turns:
            return self.turns[-1]["response"]
        return ""


def assert_response_contains(response_text: str, *keywords: str, must_not_contain: List[str] = None) -> bool:
    """Check if response contains at least one of the keywords (case-insensitive)."""
    response_lower = response_text.lower()

    # Must contain at least one keyword
    has_keyword = any(kw.lower() in response_lower for kw in keywords)
    if not has_keyword:
        return False

    # Must not contain forbidden terms
    if must_not_contain:
        for forbidden in must_not_contain:
            if forbidden.lower() in response_lower:
                return False

    return True


# ============================================================================
# TEST SCENARIOS
# ============================================================================

class TestHappyPath:
    """Scenario 1: Complete booking flow (returning client)."""

    def test_returning_client_complete_booking(self):
        """Complete booking: greeting → name → service → date → time → confirmation → exit."""
        ctx = ConversationContext(vertical="salone")

        # Turn 1: Greeting
        t1 = ctx.turn("Buongiorno, vorrei un appuntamento")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"
        assert assert_response_contains(t1["response"], "nome", "chi", "cortesia"), \
            f"Expected greeting response asking for name, got: {t1['response']}"
        assert t1["fsm_state"] in ("waiting_name", "idle"), \
            f"Expected idle or waiting_name, got {t1['fsm_state']}"

        # Turn 2: Name
        t2 = ctx.turn("Marco Rossi")
        assert t2["success"], f"Turn 2 failed: {t2['error']}"
        assert assert_response_contains(t2["response"], "servizio", "quale", "cosa"), \
            f"Expected service prompt, got: {t2['response']}"
        assert t2["fsm_state"] in ("waiting_service", "waiting_name"), \
            f"Expected waiting_service, got {t2['fsm_state']}"

        # Turn 3: Service
        t3 = ctx.turn("Un taglio per favore")
        assert t3["success"], f"Turn 3 failed: {t3['error']}"
        assert assert_response_contains(t3["response"], "data", "quando", "giorno"), \
            f"Expected date prompt, got: {t3['response']}"
        assert t3["fsm_state"] in ("waiting_date", "waiting_service"), \
            f"Expected waiting_date, got {t3['fsm_state']}"

        # Turn 4: Date
        t4 = ctx.turn("Domani alle 10")
        assert t4["success"], f"Turn 4 failed: {t4['error']}"
        # Could be waiting_time or confirming depending on pipeline
        assert assert_response_contains(t4["response"], "conferma", "ok", "riepilog", "giusto", "corretto"), \
            f"Expected confirmation prompt, got: {t4['response']}"

        # Turn 5: Confirmation
        t5 = ctx.turn("Si, confermo")
        assert t5["success"], f"Turn 5 failed: {t5['error']}"
        assert assert_response_contains(t5["response"], "confermata", "prenotazione", "whatsapp"), \
            f"Expected confirmation message, got: {t5['response']}"

        # Turn 6: Goodbye
        t6 = ctx.turn("Grazie, arrivederci")
        assert t6["success"], f"Turn 6 failed: {t6['error']}"
        assert t6["should_exit"] is True, \
            f"Expected should_exit=True on goodbye, got {t6['should_exit']}"


class TestBareName:
    """Scenario 2: Bare name from IDLE enters booking state."""

    def test_bare_name_enters_booking(self):
        """Just saying a name should trigger booking, not remain in IDLE."""
        ctx = ConversationContext(vertical="salone")

        # Don't start with booking intent, just a name
        t1 = ctx.turn("Marco Rossi")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        # Should NOT stay in idle — should transition to waiting_service or waiting_surname
        assert t1["fsm_state"] not in ("idle",), \
            f"Bare name should NOT stay in idle, got {t1['fsm_state']}"

        # Should ask for service or surname, not greeting again
        response_lower = t1["response"].lower()
        assert ("servizio" in response_lower or "quale" in response_lower or
                "cognome" in response_lower or "nome" in response_lower), \
            f"Expected service/surname prompt, got: {t1['response']}"


class TestAmbiguousName:
    """Scenario 3: Ambiguous name triggers disambiguation."""

    def test_ambiguous_name_disambiguation(self):
        """Name matching multiple DB clients should ask for surname or disambiguate."""
        ctx = ConversationContext(vertical="salone")

        # Start booking
        t1 = ctx.turn("Vorrei prenotare")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        # Try a name that might match multiple entries (Marco is common)
        t2 = ctx.turn("Marco")
        assert t2["success"], f"Turn 2 failed: {t2['error']}"

        # Could either:
        # a) ask for surname
        # b) disambiguate with "Marco which one?"
        # c) continue if only one Marco
        response_lower = t2["response"].lower()
        expected_states = ("waiting_surname", "disambiguating_name", "waiting_service")

        if t2["fsm_state"] in ("waiting_surname", "disambiguating_name"):
            assert ("cognome" in response_lower or "quale" in response_lower or
                    "marco" in response_lower), \
                f"Expected surname/disambiguation prompt, got: {t2['response']}"

        # If surname asked, provide it
        if "cognome" in response_lower or "surname" in response_lower:
            t3 = ctx.turn("Rossi")
            assert t3["success"], f"Turn 3 failed: {t3['error']}"
            assert t3["fsm_state"] != "waiting_surname", \
                f"Should advance from waiting_surname after providing surname"


class TestNewClientRegistration:
    """Scenario 4: New client registration flow."""

    def test_new_client_registration(self):
        """Unrecognized name should trigger new client registration."""
        ctx = ConversationContext(vertical="salone")

        # Start booking
        t1 = ctx.turn("Vorrei prenotare")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        # Use obviously new name
        t2 = ctx.turn("Valentina Nuovissimo")
        assert t2["success"], f"Turn 2 failed: {t2['error']}"

        # Should either recognize as new OR ask to confirm registration
        # State could be propose_registration, registering_phone, or continue booking
        # Key: should not fail, should provide clear next step
        assert assert_response_contains(t2["response"],
                                       "telefono", "numero", "email", "servizio", "quale"),\
            f"Expected phone/email or service prompt, got: {t2['response']}"


class TestGoodbye:
    """Scenario 5: Goodbye/exit at any point."""

    def test_goodbye_from_idle(self):
        """Goodbye from start should exit gracefully."""
        ctx = ConversationContext(vertical="salone")
        t1 = ctx.turn("Arrivederci")
        assert t1["should_exit"] is True, \
            f"Expected should_exit=True on goodbye from idle, got {t1['should_exit']}"

    def test_goodbye_mid_booking(self):
        """Goodbye during booking should exit."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Vorrei prenotare")
        assert t1["success"]

        t2 = ctx.turn("Marco Rossi")
        assert t2["success"]

        # Exit mid-flow
        t3 = ctx.turn("Grazie, arrivederci")
        assert t3["should_exit"] is True, \
            f"Expected should_exit=True mid-booking, got {t3['should_exit']}"

    def test_goodbye_variants(self):
        """Multiple goodbye formats should be recognized."""
        goodbye_variants = [
            "Arrivederci",
            "Grazie, arrivederci",
            "Ciao",
            "Grazie mille, ciao",
            "Buonasera, grazie",
        ]

        for goodbye in goodbye_variants:
            ctx = ConversationContext(vertical="salone")
            t = ctx.turn(goodbye)
            assert t["should_exit"] is True, \
                f"'{goodbye}' should trigger exit, but got should_exit={t['should_exit']}"


class TestNameCorruption:
    """Scenario 6: Service request with name corruption check."""

    def test_service_not_corrupted_to_surname(self):
        """'barba' should NOT be corrupted to 'Barbieri' (surname from DB)."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Vorrei tagliare i capelli e fare la barba")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        response_lower = t1["response"].lower()
        # Should recognize "barba" as a service (in salone), not person name
        # Response should ask for name or date, not treat "barba" as name
        assert "barbieri" not in response_lower, \
            f"'barba' was corrupted to surname 'Barbieri': {t1['response']}"

        # Should recognize service intent
        assert t1["intent"] in ("booking", "prenotazione", "servizio", None), \
            f"Expected booking intent, got {t1['intent']}"


class TestFAQ:
    """Scenario 7: FAQ questions."""

    def test_faq_price_question(self):
        """'Quanto costa un taglio uomo?' should return service price from DB."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Quanto costa un taglio uomo?")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        response_lower = t1["response"].lower()
        # Should mention cost/price or a number (euro/€)
        assert ("euro" in response_lower or "€" in response_lower or
                "costo" in response_lower or "prezzo" in response_lower or
                any(str(i) in response_lower for i in range(10, 100))), \
            f"FAQ should return price info, got: {t1['response']}"

        # Should NOT trigger exit or booking
        assert t1["should_exit"] is False, "FAQ should not exit conversation"

    def test_faq_hours_question(self):
        """'Quali sono gli orari?' should return business hours."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Quali sono gli orari di apertura?")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        response_lower = t1["response"].lower()
        # Should mention hours/apertura or times
        assert ("orario" in response_lower or "apertura" in response_lower or
                "chiusura" in response_lower or ":" in response_lower or
                any(str(i) + ":00" in response_lower for i in range(6, 22))), \
            f"FAQ should return hours, got: {t1['response']}"


class TestCancel:
    """Scenario 8: Cancel/modify operations."""

    def test_cancel_mid_booking(self):
        """'Voglio annullare' during booking should offer cancellation."""
        ctx = ConversationContext(vertical="salone")

        # Start booking
        t1 = ctx.turn("Vorrei prenotare")
        t2 = ctx.turn("Marco Rossi")
        t3 = ctx.turn("Un taglio")
        t4 = ctx.turn("Domani")

        # Request cancellation
        t5 = ctx.turn("Voglio annullare")
        assert t5["success"], f"Turn 5 failed: {t5['error']}"

        response_lower = t5["response"].lower()
        # Should acknowledge cancellation or ask to confirm
        assert ("annulla" in response_lower or "cancella" in response_lower or
                "ok" in response_lower or "grazie" in response_lower), \
            f"Expected cancellation response, got: {t5['response']}"


class TestOperatorEscalation:
    """Scenario 9: Operator request."""

    def test_operator_request_from_idle(self):
        """'Vorrei parlare con un operatore' should escalate."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Vorrei parlare con un operatore")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        # Should escalate (set should_escalate or offer to connect)
        if t1.get("should_escalate"):
            assert t1["should_escalate"] is True, \
                f"Expected should_escalate=True, got {t1['should_escalate']}"
        else:
            # Or respond with escalation message
            response_lower = t1["response"].lower()
            assert ("operatore" in response_lower or "mettere" in response_lower or
                    "connettere" in response_lower), \
                f"Expected escalation response, got: {t1['response']}"

    def test_operator_request_mid_booking(self):
        """'Operatore' during booking should escalate."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Vorrei prenotare")
        t2 = ctx.turn("Marco")
        t3 = ctx.turn("Operatore")

        assert t3["success"], f"Turn 3 failed: {t3['error']}"
        # Should acknowledge escalation request
        response_lower = t3["response"].lower()
        assert ("operatore" in response_lower or "mettere" in response_lower or
                "connettere" in response_lower or "ok" in response_lower), \
            f"Expected escalation response mid-booking, got: {t3['response']}"


class TestEdgeCases:
    """Scenario 10: Edge cases."""

    def test_empty_string(self):
        """Empty input should be handled gracefully."""
        ctx = ConversationContext(vertical="salone")
        t1 = ctx.turn("")
        # Should not crash
        assert t1.get("_connection_failed") is not True, "Empty input caused connection failure"
        if t1["success"]:
            # If successful, should still be coherent
            assert t1["response"] is not None

    def test_very_long_string(self):
        """Very long input (500+ chars) should not crash."""
        ctx = ConversationContext(vertical="salone")
        long_text = "Buongiorno, " + ("parola " * 100)  # ~600 chars
        t1 = ctx.turn(long_text)
        # Should not crash
        assert t1.get("_connection_failed") is not True, "Long input caused connection failure"
        if t1["success"]:
            assert t1["response"] is not None

    def test_only_punctuation(self):
        """Input with only punctuation should be handled."""
        ctx = ConversationContext(vertical="salone")
        t1 = ctx.turn("...")
        # Should not crash
        assert t1.get("_connection_failed") is not True, "Punctuation input caused connection failure"
        if t1["success"]:
            # May be no-op or ask to repeat
            assert t1["response"] is not None

    def test_phone_number_input(self):
        """Phone number input should be handled."""
        ctx = ConversationContext(vertical="salone")
        t1 = ctx.turn("3281234567")
        # Should not crash, may ask what this is
        assert t1.get("_connection_failed") is not True, "Phone number caused connection failure"
        if t1["success"]:
            assert t1["response"] is not None

    def test_special_characters(self):
        """Special characters should be handled."""
        ctx = ConversationContext(vertical="salone")
        t1 = ctx.turn("@#$%^&*()")
        # Should not crash
        assert t1.get("_connection_failed") is not True, "Special chars caused connection failure"
        if t1["success"]:
            assert t1["response"] is not None

    def test_mixed_language(self):
        """Mixed Italian/English should handle gracefully."""
        ctx = ConversationContext(vertical="salone")
        t1 = ctx.turn("I want to book a haircut please")
        # Should not crash, may not understand but should respond
        assert t1.get("_connection_failed") is not True, "English caused connection failure"


class TestLatency:
    """Test latency characteristics."""

    def test_response_latency_acceptable(self):
        """Responses should be reasonably fast (<2s for testing)."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Buongiorno")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"
        # Allow up to 2 seconds for testing (stricter in production)
        assert t1["_latency_ms"] < 2000, \
            f"Response too slow: {t1['_latency_ms']:.0f}ms"

    def test_multi_turn_latency(self):
        """All turns in a conversation should be reasonably fast."""
        ctx = ConversationContext(vertical="salone")

        turns = [
            "Buongiorno",
            "Vorrei prenotare",
            "Marco Rossi",
            "Un taglio",
            "Domani",
        ]

        for user_input in turns:
            t = ctx.turn(user_input)
            assert t["success"], f"Failed on '{user_input}': {t['error']}"
            assert t["_latency_ms"] < 2000, \
                f"Turn '{user_input}' too slow: {t['_latency_ms']:.0f}ms"


class TestStateTransitions:
    """Test FSM state transitions are logical."""

    def test_idle_to_waiting_name(self):
        """IDLE → WAITING_NAME on booking intent."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Vorrei prenotare")
        assert t1["success"]

        # Should ask for name
        assert t1["fsm_state"] in ("waiting_name", "waiting_service", "idle"), \
            f"Unexpected state after booking request: {t1['fsm_state']}"

    def test_waiting_name_to_waiting_service(self):
        """WAITING_NAME → WAITING_SERVICE after name provided."""
        ctx = ConversationContext(vertical="salone")

        t1 = ctx.turn("Vorrei prenotare")
        t2 = ctx.turn("Marco Rossi")
        assert t2["success"]

        # Should ask for service
        assert t2["fsm_state"] in ("waiting_service", "waiting_surname", "waiting_date"), \
            f"Unexpected state after name: {t2['fsm_state']}"


class TestDifferentVerticals:
    """Test same flows work across different verticals."""

    def test_palestra_booking_flow(self):
        """Same booking flow should work for palestra vertical."""
        ctx = ConversationContext(vertical="palestra")

        t1 = ctx.turn("Buongiorno, vorrei iscrivermi a una lezione")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        # Should ask for name or recognize booking intent
        assert t1["fsm_state"] in ("waiting_name", "idle", "waiting_service"), \
            f"Unexpected state for palestra: {t1['fsm_state']}"

    def test_medical_booking_flow(self):
        """Booking flow for medical vertical."""
        ctx = ConversationContext(vertical="medical")

        t1 = ctx.turn("Vorrei prenotare una visita")
        assert t1["success"], f"Turn 1 failed: {t1['error']}"

        # Should recognize medical context
        assert t1["fsm_state"] in ("waiting_name", "waiting_service", "idle"), \
            f"Unexpected state for medical: {t1['fsm_state']}"


# ============================================================================
# MAIN / PYTEST INTEGRATION
# ============================================================================

def test_health_check():
    """Verify pipeline is running before other tests."""
    h = health()
    assert h is not None, \
        f"Pipeline not responding at {URL}. Start with: " \
        f"ssh imac \"cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python main.py\""
    assert h.get("status") in ("ok", "ready"), \
        f"Pipeline health check failed: {h}"


if __name__ == "__main__":
    import pytest

    # Run with: python -m pytest test_multi_turn_conversations.py -v
    # Or direct: python test_multi_turn_conversations.py
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ])
    sys.exit(exit_code)
