"""
FLUXION Voice Agent — Sales State Machine

Separate FSM for FLUXION sales conversations (WhatsApp inbound).
Uses LLM NLU for intent detection + sales_knowledge_base.json for content.

States:
  IDLE → QUALIFYING_VERTICAL → QUALIFYING_EMPLOYEES → QUALIFYING_VOLUME →
  QUALIFYING_TOOL → QUALIFYING_PAIN → PITCHING → HANDLING_OBJECTION →
  CLOSING → FOLLOWUP_SCHEDULED → COMPLETED → DECLINED

Zero coupling with BookingStateMachine — completely independent module.
"""

import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

logger = logging.getLogger("fluxion.sales.fsm")

try:
    from .sales_kb_loader import (
        get_pitch, get_objection_response, get_qualification_question,
        get_qualification_count, get_closing_message, get_pain_points,
        get_competitive_response, resolve_vertical, sanitize_sales_text,
        get_personality_rules,
    )
except ImportError:
    from sales_kb_loader import (
        get_pitch, get_objection_response, get_qualification_question,
        get_qualification_count, get_closing_message, get_pain_points,
        get_competitive_response, resolve_vertical, sanitize_sales_text,
        get_personality_rules,
    )


class SalesState(Enum):
    """Sales conversation states."""
    IDLE = "idle"
    QUALIFYING_VERTICAL = "qualifying_vertical"
    QUALIFYING_EMPLOYEES = "qualifying_employees"
    QUALIFYING_VOLUME = "qualifying_volume"
    QUALIFYING_TOOL = "qualifying_tool"
    QUALIFYING_PAIN = "qualifying_pain"
    PITCHING = "pitching"
    HANDLING_OBJECTION = "handling_objection"
    CLOSING = "closing"
    FOLLOWUP_SCHEDULED = "followup_scheduled"
    COMPLETED = "completed"
    DECLINED = "declined"


@dataclass
class SalesContext:
    """Sales conversation context — collected during qualification."""
    lead_name: Optional[str] = None
    lead_phone: Optional[str] = None
    vertical: Optional[str] = None           # KB vertical key
    employees: Optional[int] = None
    daily_appointments: Optional[int] = None
    current_tool: Optional[str] = None       # "carta", "fresha", "google calendar", etc.
    missed_calls: Optional[int] = None
    recommended_tier: Optional[str] = None   # "tier_base", "tier_pro", "tier_clinic"
    objection_count: int = 0
    qualification_step: int = 0              # 0-5 index into qualification_questions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lead_name": self.lead_name,
            "lead_phone": self.lead_phone,
            "vertical": self.vertical,
            "employees": self.employees,
            "daily_appointments": self.daily_appointments,
            "current_tool": self.current_tool,
            "missed_calls": self.missed_calls,
            "recommended_tier": self.recommended_tier,
            "objection_count": self.objection_count,
            "qualification_step": self.qualification_step,
        }


@dataclass
class SalesResult:
    """Result from processing a sales message."""
    response: str
    state: SalesState
    context: Dict[str, Any]
    checkout_url: Optional[str] = None       # Set during CLOSING
    followup_wa: Optional[str] = None        # WhatsApp message to send later
    is_terminal: bool = False                # True if COMPLETED or DECLINED


class SalesStateMachine:
    """
    FSM for FLUXION sales conversations.

    Flow: greeting → qualification (5 questions) → pitch → objection handling → closing
    """

    def __init__(self):
        self.state = SalesState.IDLE
        self.ctx = SalesContext()
        self._pre_objection_state: Optional[SalesState] = None

    def reset(self):
        """Reset FSM to initial state."""
        self.state = SalesState.IDLE
        self.ctx = SalesContext()
        self._pre_objection_state = None

    def process(self, text: str, nlu_result: Optional[Dict] = None) -> SalesResult:
        """
        Process user message through sales FSM.

        Args:
            text: User message text
            nlu_result: Optional LLM NLU result dict (intent, entities, etc.)

        Returns:
            SalesResult with response and updated state
        """
        text_stripped = text.strip()
        if not text_stripped:
            return SalesResult(
                response="Non ho capito, puoi ripetere?",
                state=self.state,
                context=self.ctx.to_dict(),
            )

        # Check for objections only during PITCHING and HANDLING states
        # CLOSING has its own "ci penso" / "quanto costa" handling — don't intercept
        _OBJECTION_STATES = (SalesState.PITCHING, SalesState.HANDLING_OBJECTION)
        if self.state in _OBJECTION_STATES:
            objection_resp = get_objection_response(text_stripped)
            if objection_resp:
                result = self._handle_objection(objection_resp)
                self.state = result.state
                return result

            comp = self._check_competitor(text_stripped)
            if comp:
                result = self._handle_objection(comp)
                self.state = result.state
                return result

        # State dispatch
        handler = {
            SalesState.IDLE: self._handle_idle,
            SalesState.QUALIFYING_VERTICAL: self._handle_qualifying_vertical,
            SalesState.QUALIFYING_EMPLOYEES: self._handle_qualifying_employees,
            SalesState.QUALIFYING_VOLUME: self._handle_qualifying_volume,
            SalesState.QUALIFYING_TOOL: self._handle_qualifying_tool,
            SalesState.QUALIFYING_PAIN: self._handle_qualifying_pain,
            SalesState.PITCHING: self._handle_pitching,
            SalesState.HANDLING_OBJECTION: self._handle_after_objection,
            SalesState.CLOSING: self._handle_closing,
            SalesState.FOLLOWUP_SCHEDULED: self._handle_followup,
            SalesState.COMPLETED: self._handle_terminal,
            SalesState.DECLINED: self._handle_terminal,
        }.get(self.state, self._handle_idle)

        result = handler(text_stripped, nlu_result)
        logger.info("[Sales FSM] %s → %s | vertical=%s tier=%s",
                    self.state.value, result.state.value,
                    self.ctx.vertical, self.ctx.recommended_tier)
        self.state = result.state
        return result

    # ─── State Handlers ───────────────────────────────────────────

    def _handle_idle(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Entry point — greet and ask vertical."""
        # Try to extract name from greeting
        name = self._extract_name(text, nlu)
        if name:
            self.ctx.lead_name = name

        # Check if vertical is already mentioned
        vertical = resolve_vertical(text)
        if vertical:
            self.ctx.vertical = vertical
            self.ctx.qualification_step = 1
            q = get_qualification_question(1)
            greeting = f"Ciao{' ' + self.ctx.lead_name if self.ctx.lead_name else ''}! "
            pitch = get_pitch(vertical)
            if pitch:
                greeting += pitch["headline"] + " "
            greeting += q["question"] if q else "Quanti siete a lavorare?"
            return SalesResult(
                response=greeting,
                state=SalesState.QUALIFYING_EMPLOYEES,
                context=self.ctx.to_dict(),
            )

        # No vertical yet — ask
        greeting = f"Ciao{' ' + self.ctx.lead_name if self.ctx.lead_name else ''}! "
        greeting += "Sono Sara di FLUXION. Che tipo di attività hai?"
        return SalesResult(
            response=greeting,
            state=SalesState.QUALIFYING_VERTICAL,
            context=self.ctx.to_dict(),
        )

    def _handle_qualifying_vertical(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Qualify: what type of business."""
        vertical = resolve_vertical(text)
        if not vertical:
            return SalesResult(
                response="Scusa, non ho capito bene. Che tipo di attività hai? "
                         "Parrucchiere, estetista, meccanico, palestra, clinica...?",
                state=SalesState.QUALIFYING_VERTICAL,
                context=self.ctx.to_dict(),
            )

        self.ctx.vertical = vertical
        self.ctx.qualification_step = 1

        pitch = get_pitch(vertical)
        headline = pitch["headline"] + " " if pitch else ""

        q = get_qualification_question(1)
        follow = q["follow_up"] if q else "Quanti siete a lavorare?"

        return SalesResult(
            response=f"Perfetto, conosco bene il settore. {headline}{follow}",
            state=SalesState.QUALIFYING_EMPLOYEES,
            context=self.ctx.to_dict(),
        )

    def _handle_qualifying_employees(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Qualify: how many employees."""
        num = self._extract_number(text)
        if num is not None:
            self.ctx.employees = num
        else:
            # Accept text answers too
            self.ctx.employees = self._guess_employees(text)

        self.ctx.qualification_step = 2
        q = get_qualification_question(2)
        follow = q["follow_up"] if q else "E adesso come gestisci le prenotazioni?"

        return SalesResult(
            response=follow,
            state=SalesState.QUALIFYING_VOLUME,
            context=self.ctx.to_dict(),
        )

    def _handle_qualifying_volume(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Qualify: daily appointment volume."""
        num = self._extract_number(text)
        if num is not None:
            self.ctx.daily_appointments = num

        self.ctx.qualification_step = 3
        q = get_qualification_question(3)
        follow = q["follow_up"] if q else "Quante chiamate pensi di perdere al giorno?"

        return SalesResult(
            response=follow,
            state=SalesState.QUALIFYING_TOOL,
            context=self.ctx.to_dict(),
        )

    def _handle_qualifying_tool(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Qualify: current booking tool."""
        self.ctx.current_tool = text.strip()
        self.ctx.qualification_step = 4

        q = get_qualification_question(4)
        follow = q["follow_up"] if q else "Quante chiamate perdi al giorno mentre lavori?"

        return SalesResult(
            response=follow,
            state=SalesState.QUALIFYING_PAIN,
            context=self.ctx.to_dict(),
        )

    def _handle_qualifying_pain(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Qualify: missed calls (pain point). Then deliver pitch."""
        num = self._extract_number(text)
        if num is not None:
            self.ctx.missed_calls = num

        self.ctx.qualification_step = 5
        # Determine tier
        self.ctx.recommended_tier = self._determine_tier()

        # Deliver vertical-specific pitch
        pitch = get_pitch(self.ctx.vertical) if self.ctx.vertical else None
        if pitch:
            response = f"{pitch['pitch']} {pitch['key_number']}"
        else:
            response = ("Ogni chiamata persa è un cliente perso. FLUXION risolve questo problema: "
                        "Sara risponde al telefono 24 ore su 24, prende gli appuntamenti e manda "
                        "la conferma su WhatsApp. Paghi una volta sola, zero commissioni.")

        response += "\n\nVuoi sapere come funziona nel dettaglio?"

        return SalesResult(
            response=sanitize_sales_text(response),
            state=SalesState.PITCHING,
            context=self.ctx.to_dict(),
        )

    def _handle_pitching(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """After pitch delivery — handle response."""
        text_lower = text.lower()

        # Positive signal → go to closing
        if any(w in text_lower for w in ["sì", "si", "certo", "dimmi", "spiegami",
                                          "come funziona", "interessante", "ok",
                                          "quanto costa", "prezzo"]):
            return self._go_to_closing()

        # Negative signal
        if any(w in text_lower for w in ["no", "non mi interessa", "lascia stare"]):
            self.ctx.objection_count += 1
            if self.ctx.objection_count >= 3:
                return self._decline_gracefully()
            return SalesResult(
                response="Capisco. Solo una curiosità: quante chiamate perdi al giorno "
                         "mentre lavori? Anche solo 2-3 al giorno fanno una differenza enorme a fine mese.",
                state=SalesState.PITCHING,
                context=self.ctx.to_dict(),
            )

        # Ambiguous → assume interest, go to closing
        return self._go_to_closing()

    def _handle_after_objection(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """After handling an objection — return to pre-objection state or closing."""
        text_lower = text.lower()

        # If they're still objecting
        objection_resp = get_objection_response(text)
        if objection_resp:
            return self._handle_objection(objection_resp)

        # Positive → closing
        if any(w in text_lower for w in ["sì", "si", "ok", "dimmi", "va bene",
                                          "quanto costa", "come faccio"]):
            return self._go_to_closing()

        # Still negative
        if any(w in text_lower for w in ["no", "non mi interessa", "basta"]):
            self.ctx.objection_count += 1
            if self.ctx.objection_count >= 3:
                return self._decline_gracefully()

        # Return to where we were
        target = self._pre_objection_state or SalesState.PITCHING
        return SalesResult(
            response="Allora, vuoi che ti spiego come funziona per la tua attività?",
            state=target,
            context=self.ctx.to_dict(),
        )

    def _handle_closing(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Handle response to closing offer."""
        text_lower = text.lower()

        # Accept
        if any(w in text_lower for w in ["sì", "si", "procediamo", "va bene", "ok",
                                          "compro", "voglio", "prendo", "acquisto"]):
            tier = self.ctx.recommended_tier or "tier_pro"
            closing = get_closing_message(tier)
            if closing:
                return SalesResult(
                    response=closing["whatsapp_cta"],
                    state=SalesState.COMPLETED,
                    context=self.ctx.to_dict(),
                    checkout_url=closing.get("checkout_url"),
                    is_terminal=True,
                )
            return SalesResult(
                response="Perfetto! Ti mando il link per attivare FLUXION su WhatsApp.",
                state=SalesState.COMPLETED,
                context=self.ctx.to_dict(),
                is_terminal=True,
            )

        # Wants to think
        if any(w in text_lower for w in ["ci penso", "ci devo pensare", "vediamo",
                                          "devo valutare", "ne parlo"]):
            return SalesResult(
                response="Certo, prenditi il tempo che ti serve. Ti mando un riepilogo "
                         "su WhatsApp così ce l'hai sotto mano. Se hai domande mi trovi qui.",
                state=SalesState.FOLLOWUP_SCHEDULED,
                context=self.ctx.to_dict(),
                followup_wa="24h",
            )

        # Decline
        if any(w in text_lower for w in ["no", "non mi interessa", "lascia stare", "basta"]):
            return self._decline_gracefully()

        # Question about price
        if any(w in text_lower for w in ["quanto costa", "prezzo", "quanto viene"]):
            objection_resp = get_objection_response("quanto costa")
            if objection_resp:
                return SalesResult(
                    response=objection_resp,
                    state=SalesState.CLOSING,
                    context=self.ctx.to_dict(),
                )

        # Default: reiterate offer
        return self._go_to_closing()

    def _handle_followup(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Lead came back after followup was scheduled."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["sì", "si", "ok", "procediamo", "compro", "voglio"]):
            return self._go_to_closing()

        return SalesResult(
            response="Bentornato! Hai avuto modo di pensarci? Posso rispondere a qualsiasi domanda.",
            state=SalesState.PITCHING,
            context=self.ctx.to_dict(),
        )

    def _handle_terminal(self, text: str, nlu: Optional[Dict] = None) -> SalesResult:
        """Terminal states — should not receive messages normally."""
        return SalesResult(
            response="Grazie per il tuo tempo! Se hai bisogno, scrivimi qui.",
            state=self.state,
            context=self.ctx.to_dict(),
            is_terminal=True,
        )

    # ─── Helpers ──────────────────────────────────────────────────

    def _handle_objection(self, response: str) -> SalesResult:
        """Handle an objection with KB response."""
        self.ctx.objection_count += 1
        if self.ctx.objection_count >= 4:
            return self._decline_gracefully()

        self._pre_objection_state = self.state
        return SalesResult(
            response=sanitize_sales_text(response),
            state=SalesState.HANDLING_OBJECTION,
            context=self.ctx.to_dict(),
        )

    def _check_competitor(self, text: str) -> Optional[str]:
        """Check if text mentions a competitor, return competitive response."""
        text_lower = text.lower()
        mapping = {
            "fresha": "vs_fresha",
            "treatwell": "vs_treatwell",
            "google calendar": "vs_google_calendar",
            "google": "vs_google_calendar",
            "carta": "vs_carta_agenda",
            "agenda": "vs_carta_agenda",
            "quaderno": "vs_carta_agenda",
        }
        for keyword, comp_key in mapping.items():
            if keyword in text_lower:
                comp = get_competitive_response(comp_key)
                if comp:
                    return f"{comp['our_advantage']} {comp['killer_line']}"
        return None

    def _go_to_closing(self) -> SalesResult:
        """Transition to CLOSING with tier-specific message."""
        tier = self.ctx.recommended_tier or "tier_pro"
        closing = get_closing_message(tier)
        if closing:
            return SalesResult(
                response=sanitize_sales_text(closing["message"]),
                state=SalesState.CLOSING,
                context=self.ctx.to_dict(),
                checkout_url=closing.get("checkout_url"),
            )
        return SalesResult(
            response="FLUXION ha tre opzioni, tutte con pagamento unico. "
                     "Quale ti interessa sapere di più?",
            state=SalesState.CLOSING,
            context=self.ctx.to_dict(),
        )

    def _decline_gracefully(self) -> SalesResult:
        """Lead declined — exit with class."""
        return SalesResult(
            response="Nessun problema, capisco. Se cambi idea mi trovi qui. "
                     "In bocca al lupo col lavoro!",
            state=SalesState.DECLINED,
            context=self.ctx.to_dict(),
            is_terminal=True,
        )

    def _determine_tier(self) -> str:
        """Determine recommended tier from qualification data."""
        employees = self.ctx.employees or 1

        # Clinic vertical always gets Clinic tier
        if self.ctx.vertical in ("clinica",):
            return "tier_clinic"

        if employees >= 9:
            return "tier_clinic"
        elif employees >= 3:
            return "tier_pro"
        else:
            return "tier_base"

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract first number from text."""
        import re
        # Handle Italian number words
        word_to_num = {
            "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4,
            "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9,
            "dieci": 10, "quindici": 15, "venti": 20, "trenta": 30,
            "cinquanta": 50, "cento": 100,
        }
        text_lower = text.lower()
        for word, num in word_to_num.items():
            if word in text_lower:
                return num

        # Digit extraction
        match = re.search(r'\d+', text)
        if match:
            return int(match.group())
        return None

    def _extract_name(self, text: str, nlu: Optional[Dict] = None) -> Optional[str]:
        """Try to extract lead name from greeting text."""
        if nlu and nlu.get("entities", {}).get("nome"):
            return nlu["entities"]["nome"]

        import re
        # "Sono Marco" / "Mi chiamo Luca"
        m = re.search(r'(?:sono|mi chiamo|io sono)\s+([A-Z][a-zàèéìòù]+)', text, re.IGNORECASE)
        if m:
            return m.group(1).capitalize()
        return None

    def _guess_employees(self, text: str) -> Optional[int]:
        """Guess employee count from text like 'solo io', 'io e mia moglie'."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["solo io", "da solo", "da sola"]):
            return 1
        if any(w in text_lower for w in ["io e", "in due", "siamo in due"]):
            return 2
        if "in tre" in text_lower or "siamo tre" in text_lower:
            return 3
        return None
