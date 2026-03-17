"""
Tests for Sara Sales FSM — F18 Sales Agent

Tests the complete sales conversation flow:
  greeting → qualification → pitch → objection handling → closing
"""

import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from sales_state_machine import SalesStateMachine, SalesState
from sales_kb_loader import (
    load_sales_kb, get_pitch, get_objection_response,
    get_closing_message, resolve_vertical, sanitize_sales_text,
    get_qualification_question, get_pain_points, get_competitive_response,
)


# ═══════════════════════════════════════════════════════════════
# KB Loader Tests
# ═══════════════════════════════════════════════════════════════

class TestKBLoader:
    """Test sales knowledge base loading."""

    def test_load_kb(self):
        kb = load_sales_kb()
        assert "product_pitch" in kb
        assert "objections" in kb
        assert "closing_messages" in kb
        assert len(kb["product_pitch"]) >= 8

    def test_get_pitch_parrucchiere(self):
        pitch = get_pitch("parrucchiere")
        assert pitch is not None
        assert "headline" in pitch
        assert "pitch" in pitch
        assert "key_number" in pitch
        assert "telefonate" in pitch["headline"].lower() or "tagli" in pitch["headline"].lower()

    def test_get_pitch_unknown_vertical(self):
        assert get_pitch("gelateria") is None

    def test_get_objection_costa_troppo(self):
        resp = get_objection_response("costa troppo questo prodotto")
        assert resp is not None
        assert "investimento" in resp.lower() or "conti" in resp.lower()

    def test_get_objection_no_match(self):
        assert get_objection_response("che bel tempo oggi") is None

    def test_get_objection_fresha(self):
        resp = get_objection_response("uso Fresha")
        assert resp is not None
        assert "commissioni" in resp.lower() or "20%" in resp

    def test_get_closing_tier_pro(self):
        closing = get_closing_message("tier_pro")
        assert closing is not None
        assert "897" in closing["message"]
        assert "checkout_url" in closing
        assert closing["checkout_url"].startswith("https://")

    def test_resolve_vertical_direct(self):
        assert resolve_vertical("parrucchiere") == "parrucchiere"
        assert resolve_vertical("meccanico") == "meccanico"
        assert resolve_vertical("palestra") == "palestra"

    def test_resolve_vertical_alias(self):
        assert resolve_vertical("barbiere") == "parrucchiere"
        assert resolve_vertical("officina") == "meccanico"
        assert resolve_vertical("centro estetico") == "estetista"
        assert resolve_vertical("avvocato") == "studio_professionale"
        assert resolve_vertical("dentista") == "clinica"

    def test_resolve_vertical_substring(self):
        assert resolve_vertical("ho un salone di bellezza") == "parrucchiere"
        assert resolve_vertical("lavoro in una palestra") == "palestra"

    def test_resolve_vertical_unknown(self):
        assert resolve_vertical("gelateria") is None

    def test_sanitize_sales_text(self):
        text = "Il nostro software usa intelligenza artificiale nel cloud"
        sanitized = sanitize_sales_text(text)
        assert "software" not in sanitized.lower() or "strumento" in sanitized
        assert "cloud" not in sanitized.lower() or "sul tuo computer" in sanitized

    def test_get_qualification_questions(self):
        q0 = get_qualification_question(0)
        assert q0 is not None
        assert "question" in q0

    def test_get_pain_points(self):
        pains = get_pain_points("parrucchiere")
        assert len(pains) >= 4
        assert any("telefono" in p.lower() for p in pains)

    def test_get_competitive_response(self):
        comp = get_competitive_response("vs_fresha")
        assert comp is not None
        assert "killer_line" in comp


# ═══════════════════════════════════════════════════════════════
# Sales FSM Tests
# ═══════════════════════════════════════════════════════════════

class TestSalesFSM:
    """Test sales state machine transitions."""

    def setup_method(self):
        self.fsm = SalesStateMachine()

    def test_initial_state(self):
        assert self.fsm.state == SalesState.IDLE

    def test_reset(self):
        self.fsm.state = SalesState.PITCHING
        self.fsm.ctx.vertical = "parrucchiere"
        self.fsm.reset()
        assert self.fsm.state == SalesState.IDLE
        assert self.fsm.ctx.vertical is None

    # ─── Full Flow Tests ──────────────────────────────────────

    def test_full_flow_parrucchiere(self):
        """Complete sales flow: greeting → qualification → pitch → close."""
        # Step 1: Greeting
        r = self.fsm.process("Ciao, sono Marco")
        assert r.state == SalesState.QUALIFYING_VERTICAL
        assert "tipo di attività" in r.response.lower() or "Sara" in r.response

        # Step 2: Vertical
        r = self.fsm.process("Ho un salone da parrucchiere")
        assert r.state == SalesState.QUALIFYING_EMPLOYEES
        assert self.fsm.ctx.vertical == "parrucchiere"

        # Step 3: Employees
        r = self.fsm.process("Siamo in 4")
        assert r.state == SalesState.QUALIFYING_VOLUME
        assert self.fsm.ctx.employees == 4

        # Step 4: Volume
        r = self.fsm.process("Circa 20 appuntamenti al giorno")
        assert r.state == SalesState.QUALIFYING_TOOL
        assert self.fsm.ctx.daily_appointments == 20

        # Step 5: Tool
        r = self.fsm.process("Uso carta e penna")
        assert r.state == SalesState.QUALIFYING_PAIN

        # Step 6: Pain → Pitch
        r = self.fsm.process("Almeno 5 chiamate perse al giorno")
        assert r.state == SalesState.PITCHING
        assert self.fsm.ctx.missed_calls == 5
        assert self.fsm.ctx.recommended_tier == "tier_pro"  # 4 employees

        # Step 7: Interest → Closing
        r = self.fsm.process("Sì, dimmi di più")
        assert r.state == SalesState.CLOSING
        assert "897" in r.response  # Pro tier

        # Step 8: Accept
        r = self.fsm.process("Ok, procediamo")
        assert r.state == SalesState.COMPLETED
        assert r.is_terminal
        assert r.checkout_url is not None

    def test_flow_with_vertical_in_greeting(self):
        """Vertical mentioned in first message — skip qualifying_vertical."""
        r = self.fsm.process("Ciao, ho un'officina meccanica")
        assert r.state == SalesState.QUALIFYING_EMPLOYEES
        assert self.fsm.ctx.vertical == "meccanico"

    def test_flow_clinica_gets_clinic_tier(self):
        """Clinica vertical always gets Clinic tier."""
        self.fsm.process("Ciao")
        self.fsm.process("Ho uno studio medico")
        assert self.fsm.ctx.vertical == "clinica"
        self.fsm.process("5 persone")
        self.fsm.process("30 pazienti")
        self.fsm.process("Agenda cartacea")
        r = self.fsm.process("10 chiamate perse")
        assert self.fsm.ctx.recommended_tier == "tier_clinic"

    def test_solo_operator_gets_base_tier(self):
        """1 employee → Base tier."""
        self.fsm.process("Ciao")
        self.fsm.process("Sono estetista")
        self.fsm.process("Solo io")
        assert self.fsm.ctx.employees == 1
        self.fsm.process("8 al giorno")
        self.fsm.process("WhatsApp")
        r = self.fsm.process("3 chiamate")
        assert self.fsm.ctx.recommended_tier == "tier_base"

    # ─── Objection Handling ───────────────────────────────────

    def test_objection_costa_troppo(self):
        """Objection during pitching."""
        self.fsm.state = SalesState.PITCHING
        self.fsm.ctx.vertical = "parrucchiere"
        r = self.fsm.process("Costa troppo")
        assert r.state == SalesState.HANDLING_OBJECTION
        assert "investimento" in r.response.lower() or "conti" in r.response.lower()
        assert self.fsm.ctx.objection_count == 1

    def test_objection_fresha_competitor(self):
        """Competitor mention during pitching triggers competitive response."""
        self.fsm.state = SalesState.PITCHING
        self.fsm.ctx.vertical = "parrucchiere"
        r = self.fsm.process("Ma io uso Fresha")
        assert r.state == SalesState.HANDLING_OBJECTION
        assert "commissioni" in r.response.lower() or "ZERO" in r.response

    def test_three_objections_decline(self):
        """4 objections → graceful decline."""
        self.fsm.state = SalesState.PITCHING
        self.fsm.ctx.vertical = "parrucchiere"
        self.fsm.process("costa troppo")
        self.fsm.process("non mi serve")
        self.fsm.process("non ho tempo")
        r = self.fsm.process("troppo caro davvero")
        assert r.state == SalesState.DECLINED
        assert r.is_terminal
        assert "bocca al lupo" in r.response.lower() or "nessun problema" in r.response.lower()

    def test_objection_then_interest(self):
        """Objection → positive signal → closing."""
        self.fsm.state = SalesState.PITCHING
        self.fsm.ctx.vertical = "parrucchiere"
        self.fsm.ctx.recommended_tier = "tier_pro"
        r = self.fsm.process("costa troppo")
        # process() updates self.state from result
        assert self.fsm.state == SalesState.HANDLING_OBJECTION
        r = self.fsm.process("ok, dimmi di più")
        assert r.state == SalesState.CLOSING

    # ─── Closing Variants ─────────────────────────────────────

    def test_closing_ci_penso(self):
        """'Ci penso' → followup scheduled."""
        self.fsm.state = SalesState.CLOSING
        self.fsm.ctx.recommended_tier = "tier_pro"
        r = self.fsm.process("Ci devo pensare")
        assert r.state == SalesState.FOLLOWUP_SCHEDULED
        assert r.followup_wa == "24h"

    def test_closing_decline(self):
        """'No' at closing → decline."""
        self.fsm.state = SalesState.CLOSING
        r = self.fsm.process("No, non mi interessa")
        assert r.state == SalesState.DECLINED
        assert r.is_terminal

    def test_closing_price_question(self):
        """Price question during closing → answer and stay in closing."""
        self.fsm.state = SalesState.CLOSING
        self.fsm.ctx.recommended_tier = "tier_pro"
        r = self.fsm.process("Quanto costa esattamente?")
        assert r.state in (SalesState.CLOSING, SalesState.HANDLING_OBJECTION)

    # ─── Edge Cases ───────────────────────────────────────────

    def test_empty_message(self):
        r = self.fsm.process("")
        assert r.state == SalesState.IDLE
        assert "non ho capito" in r.response.lower()

    def test_name_extraction_sono(self):
        """'Sono Marco' extracts name."""
        r = self.fsm.process("Ciao, sono Marco")
        assert self.fsm.ctx.lead_name == "Marco"

    def test_name_extraction_mi_chiamo(self):
        """'Mi chiamo Luca' extracts name."""
        r = self.fsm.process("Mi chiamo Luca, ho bisogno di info")
        assert self.fsm.ctx.lead_name == "Luca"

    def test_number_extraction_italian_words(self):
        """Italian number words are extracted correctly."""
        self.fsm.state = SalesState.QUALIFYING_EMPLOYEES
        self.fsm.ctx.vertical = "parrucchiere"
        r = self.fsm.process("Siamo in cinque")
        assert self.fsm.ctx.employees == 5

    def test_employee_guess_solo_io(self):
        """'Solo io' → 1 employee."""
        self.fsm.state = SalesState.QUALIFYING_EMPLOYEES
        self.fsm.ctx.vertical = "estetista"
        r = self.fsm.process("Solo io")
        assert self.fsm.ctx.employees == 1

    def test_followup_return_positive(self):
        """Lead returns with 'sì' after followup → closing."""
        self.fsm.state = SalesState.FOLLOWUP_SCHEDULED
        r = self.fsm.process("Sì, procediamo")
        assert r.state == SalesState.CLOSING

    def test_followup_return_generic(self):
        """Lead returns with generic message → re-engage in pitching."""
        self.fsm.state = SalesState.FOLLOWUP_SCHEDULED
        r = self.fsm.process("Ciao, ho pensato")
        assert r.state == SalesState.PITCHING

    def test_terminal_state_responds(self):
        """Terminal states still respond gracefully."""
        self.fsm.state = SalesState.COMPLETED
        r = self.fsm.process("Grazie")
        assert r.is_terminal
        assert r.state == SalesState.COMPLETED

    def test_vertical_aliases_coverage(self):
        """All 8 KB verticals are reachable via aliases."""
        verticals_reached = set()
        test_inputs = [
            "parrucchiere", "meccanico", "gommista", "carrozziere",
            "estetista", "palestra", "clinica", "avvocato",
        ]
        for inp in test_inputs:
            v = resolve_vertical(inp)
            assert v is not None, f"Vertical not resolved for: {inp}"
            verticals_reached.add(v)
        assert len(verticals_reached) == 8
