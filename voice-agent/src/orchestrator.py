"""
FLUXION Voice Agent - Enterprise Orchestrator

Central orchestration module that coordinates all voice agent components.
Implements the 4-layer RAG pipeline with deterministic intent routing.

Architecture:
    User Input
         ↓
    [L0: Special Commands] → annulla, indietro, aiuto, operatore
         ↓
    [L1: Intent Classifier] → Exact match cortesia (O(1))
         ↓
    [L2: Slot Filler] → Entity extraction + state machine
         ↓
    [L3: RAG Handler] → FAQ retrieval (keyword + semantic)
         ↓
    [L4: Groq LLM] → Complex/fallback queries
         ↓
    Response + TTS

Features:
- Deterministic routing (no LLM for simple queries)
- Session management with persistence
- Client disambiguation with data_nascita
- Availability checking with pausa pranzo
- Operator preference with alternatives
- Waitlist with VIP priority
- GDPR audit logging
- Circuit breaker for API resilience
"""

import time
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime

# Local imports - support both package and direct execution
try:
    from .intent_classifier import classify_intent, IntentCategory, IntentResult
    from .booking_state_machine import BookingStateMachine, BookingState, StateMachineResult
    from .disambiguation_handler import DisambiguationHandler, DisambiguationState, DisambiguationResult
    from .availability_checker import AvailabilityChecker, AvailabilityResult, get_availability_checker
    from .session_manager import SessionManager, VoiceSession, SessionChannel, get_session_manager
    from .groq_client import GroqClient
    from .groq_nlu import GroqNLU
    from .tts import get_tts
except ImportError:
    from intent_classifier import classify_intent, IntentCategory, IntentResult
    from booking_state_machine import BookingStateMachine, BookingState, StateMachineResult
    from disambiguation_handler import DisambiguationHandler, DisambiguationState, DisambiguationResult
    from availability_checker import AvailabilityChecker, AvailabilityResult, get_availability_checker
    from session_manager import SessionManager, VoiceSession, SessionChannel, get_session_manager
    from groq_client import GroqClient
    from groq_nlu import GroqNLU
    from tts import get_tts

# Optional imports
try:
    try:
        from .faq_manager import FAQManager
    except ImportError:
        from faq_manager import FAQManager
    HAS_FAQ_MANAGER = True
except ImportError:
    HAS_FAQ_MANAGER = False

# Vertical FAQ Loader
try:
    try:
        from .vertical_loader import load_faqs_for_vertical, get_faq_path
    except ImportError:
        from vertical_loader import load_faqs_for_vertical, get_faq_path
    HAS_VERTICAL_LOADER = True
except ImportError:
    HAS_VERTICAL_LOADER = False

try:
    try:
        from .sentiment import SentimentAnalyzer, FrustrationLevel
    except ImportError:
        from sentiment import SentimentAnalyzer, FrustrationLevel
    HAS_SENTIMENT = True
except ImportError:
    HAS_SENTIMENT = False

# Guided Dialog Engine (new approach)
try:
    import sys
    from pathlib import Path
    # Add parent directory to path for guided_dialog import
    _voice_agent_root = Path(__file__).parent.parent
    if str(_voice_agent_root) not in sys.path:
        sys.path.insert(0, str(_voice_agent_root))
    from guided_dialog import GuidedDialogEngine, DialogState as GuidedDialogState
    HAS_GUIDED_DIALOG = True
except ImportError as e:
    print(f"[INFO] Guided Dialog not available: {e}")
    HAS_GUIDED_DIALOG = False

# spaCy + UmBERTo NLU (optional upgrade)
try:
    try:
        from .nlu import ItalianVoiceAgentNLU
        from .nlu.italian_nlu import NLUIntent
    except ImportError:
        from nlu import ItalianVoiceAgentNLU
        from nlu.italian_nlu import NLUIntent
    HAS_ADVANCED_NLU = True
except ImportError:
    HAS_ADVANCED_NLU = False
    print("[INFO] Advanced NLU not available. Run: pip install spacy transformers torch")

# WhatsApp client (optional)
try:
    try:
        from .whatsapp import WhatsAppClient, WhatsAppTemplates
    except ImportError:
        from whatsapp import WhatsAppClient, WhatsAppTemplates
    HAS_WHATSAPP = True
except ImportError:
    HAS_WHATSAPP = False


import logging
logger = logging.getLogger(__name__)

# HTTP Bridge URL
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"


class ProcessingLayer(Enum):
    """Which layer handled the request."""
    L0_SPECIAL = "L0_special"
    L1_EXACT = "L1_exact"
    L2_SLOT = "L2_slot"
    L3_FAQ = "L3_faq"
    L4_GROQ = "L4_groq"


# =============================================================================
# SPECIAL COMMANDS (L0)
# =============================================================================

SPECIAL_COMMANDS = {
    # Cancel/Reset
    "annulla": ("reset", "Va bene, annullo. Posso aiutarla con altro?"),
    "ricominciamo": ("reset", "D'accordo, ricominciamo. Come posso aiutarla?"),
    "da capo": ("reset", "Ok, ricominciamo da capo. Cosa desidera?"),

    # Back
    "indietro": ("back", "D'accordo, torniamo indietro."),
    "torna indietro": ("back", "Ok, torniamo al passaggio precedente."),

    # Help
    "aiuto": ("help", "Posso aiutarla a prenotare appuntamenti, verificare disponibilita, o rispondere a domande su orari e prezzi. Cosa preferisce?"),
    "cosa puoi fare": ("help", "Posso prenotare appuntamenti, verificare disponibilita, fornire informazioni su prezzi e orari. Come posso aiutarla?"),

    # Operator escalation
    "operatore": ("escalate", "La metto in contatto con un operatore, un attimo..."),
    "persona": ("escalate", "Certo, la connetto con un operatore."),
    "umano": ("escalate", "La metto in contatto con un operatore."),
    "parlo con qualcuno": ("escalate", "La connetto subito con un operatore."),

    # Repeat
    "ripeti": ("repeat", None),  # Response determined by context
    "non ho capito": ("repeat", None),
    "puoi ripetere": ("repeat", None),
}


@dataclass
class OrchestratorResult:
    """Result from orchestrator processing."""
    response: str
    intent: str
    layer: ProcessingLayer
    latency_ms: float
    audio_bytes: Optional[bytes] = None

    # State
    session_id: Optional[str] = None
    booking_context: Optional[Dict[str, Any]] = None
    client: Optional[Dict[str, Any]] = None

    # Actions
    should_escalate: bool = False
    booking_created: bool = False
    booking_id: Optional[str] = None

    # Disambiguation
    needs_disambiguation: bool = False
    disambiguation_prompt: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response": self.response,
            "intent": self.intent,
            "layer": self.layer.value,
            "latency_ms": self.latency_ms,
            "session_id": self.session_id,
            "should_escalate": self.should_escalate,
            "booking_created": self.booking_created,
            "booking_id": self.booking_id,
        }


class VoiceOrchestrator:
    """
    Enterprise Voice Agent Orchestrator.

    Coordinates all components:
    - Session management
    - Intent classification
    - Slot filling (booking state machine)
    - Client disambiguation
    - Availability checking
    - FAQ retrieval
    - Groq LLM fallback
    - TTS synthesis
    """

    def __init__(
        self,
        verticale_id: str,
        business_name: str,
        groq_api_key: Optional[str] = None,
        use_piper_tts: bool = True,
        http_bridge_url: str = HTTP_BRIDGE_URL,
        use_advanced_nlu: bool = True  # Enable spaCy + UmBERTo NLU
    ):
        """
        Initialize orchestrator.

        Args:
            verticale_id: Business vertical ID
            business_name: Business name (used in greetings)
            groq_api_key: Optional Groq API key (uses env var if not provided)
            use_piper_tts: Use Piper TTS (True) or system fallback (False)
            http_bridge_url: HTTP Bridge URL for database operations
            use_advanced_nlu: Use spaCy + UmBERTo NLU for improved intent detection
        """
        self.verticale_id = verticale_id
        self.business_name = business_name
        self.http_bridge_url = http_bridge_url

        # Initialize components
        self.session_manager = get_session_manager()
        self.groq = GroqClient(api_key=groq_api_key)
        self.tts = get_tts(use_piper=use_piper_tts)
        self._groq_nlu = GroqNLU(api_key=groq_api_key)
        self.booking_sm = BookingStateMachine(groq_nlu=self._groq_nlu)
        self.disambiguation = DisambiguationHandler()
        self.availability = get_availability_checker()

        # WhatsApp client (optional, for post-booking confirmation)
        self._wa_client = None
        if HAS_WHATSAPP:
            try:
                self._wa_client = WhatsAppClient()
                logger.info("[WA] WhatsApp client initialized for booking confirmations")
            except Exception as e:
                logger.warning(f"[WA] WhatsApp client init failed (non-critical): {e}")

        # FAQ Manager (optional) - loads FAQs based on vertical
        self.faq_manager = None
        self._faq_vertical = self._extract_vertical_key(verticale_id)
        if HAS_FAQ_MANAGER:
            self.faq_manager = FAQManager()
            # Load vertical-specific FAQs (async loaded on first session)

        # Sentiment Analyzer (optional)
        self.sentiment = None
        if HAS_SENTIMENT:
            self.sentiment = SentimentAnalyzer()

        # Advanced NLU: spaCy + UmBERTo (optional)
        # Provides improved intent detection for:
        # - "mai stato" → NEW_CLIENT (not "Mai" as name)
        # - "prima volta" → automatic registration flow
        # - Third-party bookings: "per mia madre Maria"
        self.advanced_nlu = None
        if use_advanced_nlu and HAS_ADVANCED_NLU:
            try:
                self.advanced_nlu = ItalianVoiceAgentNLU(preload_models=False)
                print("[NLU] Advanced NLU enabled (spaCy + UmBERTo)")
            except Exception as e:
                print(f"[NLU] Advanced NLU init failed: {e}")

        # Guided Dialog Engine (new approach - guided-first, NLU-validation)
        # Activated when fallback_count >= 2 or explicitly requested
        self.guided_engine = None
        self.use_guided_mode = False
        self.guided_fallback_threshold = 2
        if HAS_GUIDED_DIALOG:
            try:
                # Get DB path from environment or use default
                import os
                db_path = os.environ.get("FLUXION_DB_PATH", "fluxion.db")
                self.guided_engine = GuidedDialogEngine(
                    vertical_id=self._faq_vertical or "salone",
                    db_path=db_path
                )
                print(f"[GUIDED] Guided Dialog Engine initialized for vertical: {self._faq_vertical}")
            except Exception as e:
                print(f"[GUIDED] Guided Dialog init failed: {e}")

        # Current session
        self._current_session: Optional[VoiceSession] = None
        self._last_response: str = ""

        # E4-S1/S2: Cancel/Reschedule flow tracking
        self._pending_cancel: bool = False
        self._pending_reschedule: bool = False
        self._pending_appointments: List[Dict[str, Any]] = []
        self._selected_appointment_id: Optional[str] = None
        self._reschedule_new_date: Optional[str] = None
        self._reschedule_new_time: Optional[str] = None

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def start_session(
        self,
        channel: SessionChannel = SessionChannel.VOICE,
        phone_number: Optional[str] = None
    ) -> OrchestratorResult:
        """
        Start a new conversation session.

        Returns greeting with session ID.
        """
        start_time = time.time()

        # Load business config from database
        db_config = await self._load_business_config()
        if db_config:
            if db_config.get("nome_attivita") and (not self.business_name or self.business_name in ["PLACEHOLDER", "La tua attivita"]):
                self.business_name = db_config["nome_attivita"]
            # Update vertical from config if available
            if db_config.get("categoria_attivita"):
                self._faq_vertical = db_config["categoria_attivita"]

        # Load vertical-specific FAQs (only once per session)
        if self.faq_manager and not self.faq_manager.faqs:
            self._load_vertical_faqs(db_config)

        # Reset booking state machine for new session
        self.booking_sm.reset()
        self.disambiguation = DisambiguationHandler()

        # Create session
        self._current_session = self.session_manager.create_session(
            verticale_id=self.verticale_id,
            business_name=self.business_name,
            channel=channel,
            phone_number=phone_number
        )

        # Get greeting
        greeting = self.session_manager.get_greeting(self._current_session.session_id)
        self._last_response = greeting

        # Synthesize audio
        audio = await self.tts.synthesize(greeting)

        latency = (time.time() - start_time) * 1000

        return OrchestratorResult(
            response=greeting,
            intent="greeting",
            layer=ProcessingLayer.L1_EXACT,
            latency_ms=latency,
            audio_bytes=audio,
            session_id=self._current_session.session_id
        )

    async def process(
        self,
        user_input: str,
        session_id: Optional[str] = None
    ) -> OrchestratorResult:
        """
        Process user input through the 4-layer pipeline.

        This is the main entry point for all user messages.

        Args:
            user_input: User's text input (or transcribed audio)
            session_id: Optional session ID (uses current session if not provided)

        Returns:
            OrchestratorResult with response and metadata
        """
        start_time = time.time()

        # Get or create session
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session:
                # Reset booking SM if switching to a different session
                if self._current_session and self._current_session.session_id != session.session_id:
                    self.booking_sm.reset()
                self._current_session = session
            else:
                # New session ID - reset booking SM and create session with this ID
                if self._current_session:
                    self.booking_sm.reset()
                await self.start_session()
                # Re-register the session under the caller's session_id
                if self._current_session:
                    self.session_manager._sessions[session_id] = self._current_session
                    self._current_session.session_id = session_id
        if not self._current_session:
            await self.start_session()

        # Initialize result
        response: Optional[str] = None
        intent: str = "unknown"
        layer: ProcessingLayer = ProcessingLayer.L4_GROQ
        should_escalate: bool = False
        needs_disambiguation: bool = False

        # =====================================================================
        # LAYER 0: Special Commands
        # =====================================================================
        special_result = self._check_special_command(user_input)
        if special_result:
            action, response = special_result
            intent = action
            layer = ProcessingLayer.L0_SPECIAL

            if action == "escalate":
                should_escalate = True
            elif action == "reset":
                self.booking_sm.reset()
                self.disambiguation.reset()
            elif action == "repeat":
                response = self._last_response or "Mi scusi, non ho nulla da ripetere."
            elif action == "back":
                # Handle back in state machine context
                response = self._handle_back()

        # =====================================================================
        # LAYER 0b: Advanced NLU (spaCy + UmBERTo)
        # Detects: "mai stato", "prima volta" → NEW_CLIENT intent
        # =====================================================================
        if response is None and self.advanced_nlu:
            try:
                # Use Layer 1 only (regex) for fast detection of implicit intents
                nlu_result = self.advanced_nlu.process(user_input, skip_layer3=True)

                if nlu_result.is_new_client and nlu_result.confidence > 0.85:
                    # Detected "new client" intent - trigger registration flow
                    print(f"[NLU] Detected NEW_CLIENT intent: {user_input}")
                    self.booking_sm.context.is_new_client = True
                    # CRITICAL: Also set state to REGISTERING_SURNAME so next turn is processed by L2
                    self.booking_sm.context.state = BookingState.REGISTERING_SURNAME
                    response = "Benvenuto! Piacere di conoscerla. Mi può dire il suo nome e cognome?"
                    intent = "new_client_detected"
                    layer = ProcessingLayer.L1_EXACT

            except Exception as e:
                print(f"[NLU] Advanced NLU error: {e}")

        # =====================================================================
        # LAYER 0c: Sentiment Analysis (escalation check)
        # =====================================================================
        if response is None and self.sentiment:
            sentiment_result = self.sentiment.analyze(user_input)
            if sentiment_result.should_escalate:
                response = "Mi scusi per il disagio. La metto in contatto con un operatore."
                intent = "escalation_frustration"
                layer = ProcessingLayer.L0_SPECIAL
                should_escalate = True

        # =====================================================================
        # LAYER 1: Intent Classification (Exact Match)
        # =====================================================================
        # Skip L1 for confirmations when booking is in CONFIRMING state
        # (let the booking state machine handle "si"/"no" responses)
        booking_in_progress = self.booking_sm.context.state not in [
            BookingState.IDLE, BookingState.COMPLETED, BookingState.CANCELLED
        ]

        # Check if this is the first turn after greeting (total_turns == 0 before this turn is logged)
        is_first_turn = self._current_session and self._current_session.total_turns == 0

        if response is None:
            intent_result = classify_intent(user_input)

            # Handle waitlist confirmation (before normal CONFERMA/RIFIUTO handling)
            if self.booking_sm.context.waiting_for_waitlist_confirm:
                if intent_result.category == IntentCategory.CONFERMA:
                    # User wants to be added to waitlist
                    self.booking_sm.context.waiting_for_waitlist_confirm = False
                    if self.booking_sm.context.client_id:
                        waitlist_result = await self._add_to_waitlist(
                            client_id=self.booking_sm.context.client_id,
                            service=self.booking_sm.context.service or "",
                            preferred_date=self.booking_sm.context.date
                        )
                        if waitlist_result.get("success"):
                            response = "Perfetto, l'ho inserita in lista d'attesa. La contatteremo appena si libera un posto."
                            intent = "waitlist_confirmed"
                            layer = ProcessingLayer.L2_SLOT
                            self.booking_sm.reset()
                        else:
                            response = "Mi scusi, c'è stato un problema. Può riprovare più tardi?"
                            intent = "waitlist_error"
                            layer = ProcessingLayer.L2_SLOT
                elif intent_result.category == IntentCategory.RIFIUTO:
                    # User doesn't want waitlist
                    self.booking_sm.context.waiting_for_waitlist_confirm = False
                    response = "Va bene. Posso aiutarla con altro?"
                    intent = "waitlist_declined"
                    layer = ProcessingLayer.L2_SLOT
                    self.booking_sm.reset()

            # Skip CONFERMA/RIFIUTO when booking is active (handled by L2)
            skip_for_booking = (
                booking_in_progress and
                intent_result.category in [IntentCategory.CONFERMA, IntentCategory.RIFIUTO]
            )

            # Skip CORTESIA on first turn after greeting - greeting already serves as intro
            # This prevents Sara from responding with another greeting when user says "Buongiorno"
            skip_greeting_cortesia = (
                is_first_turn and
                intent_result.category == IntentCategory.CORTESIA
            )

            if not skip_for_booking and not skip_greeting_cortesia and intent_result.response and intent_result.category in [
                IntentCategory.CORTESIA,
                IntentCategory.CONFERMA,
                IntentCategory.RIFIUTO,
                IntentCategory.OPERATORE,
            ]:
                response = intent_result.response
                intent = intent_result.intent
                layer = ProcessingLayer.L1_EXACT

                if intent_result.category == IntentCategory.OPERATORE:
                    should_escalate = True

            # E4-S1: Handle CANCELLAZIONE intent at L1 (before booking SM)
            if response is None and intent_result.category == IntentCategory.CANCELLAZIONE:
                print(f"[L1] Detected CANCELLAZIONE intent: {user_input}")
                if self.booking_sm.context.client_id:
                    # We know the client - get their appointments
                    appointments_result = await self._get_client_appointments(
                        self.booking_sm.context.client_id
                    )
                    appointments = appointments_result.get("appointments", [])

                    if len(appointments) == 0:
                        response = "Non ho trovato appuntamenti a suo nome. Posso aiutarla in altro modo?"
                        intent = "cancel_no_appointments"
                    elif len(appointments) == 1:
                        appt = appointments[0]
                        self._pending_appointments = appointments
                        self._pending_cancel = True
                        self._selected_appointment_id = appt.get("id")
                        response = f"Ho trovato il suo appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. Conferma la cancellazione?"
                        intent = "cancel_confirm_single"
                    else:
                        self._pending_appointments = appointments
                        self._pending_cancel = True
                        appt_list = "\n".join([
                            f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                            for a in appointments[:5]
                        ])
                        response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole cancellare? Mi dica la data."
                        intent = "cancel_multiple"
                else:
                    response = "Per cancellare un appuntamento, mi può dire il suo nome?"
                    intent = "cancel_need_name"
                    # Don't start booking flow - stay at L1
                    self._pending_cancel = True
                layer = ProcessingLayer.L1_EXACT

            # E4-S2: Handle SPOSTAMENTO intent at L1 (before booking SM)
            if response is None and intent_result.category == IntentCategory.SPOSTAMENTO:
                print(f"[L1] Detected SPOSTAMENTO intent: {user_input}")
                if self.booking_sm.context.client_id:
                    appointments_result = await self._get_client_appointments(
                        self.booking_sm.context.client_id
                    )
                    appointments = appointments_result.get("appointments", [])

                    if len(appointments) == 0:
                        response = "Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?"
                        intent = "reschedule_no_appointments"
                    elif len(appointments) == 1:
                        appt = appointments[0]
                        self._pending_appointments = appointments
                        self._pending_reschedule = True
                        self._selected_appointment_id = appt.get("id")
                        response = f"Ho trovato il suo appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. A quale data vuole spostarlo?"
                        intent = "reschedule_ask_new_date"
                    else:
                        self._pending_appointments = appointments
                        self._pending_reschedule = True
                        appt_list = "\n".join([
                            f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                            for a in appointments[:5]
                        ])
                        response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole spostare? Mi dica la data."
                        intent = "reschedule_multiple"
                else:
                    response = "Per spostare un appuntamento, mi può dire il suo nome?"
                    intent = "reschedule_need_name"
                    self._pending_reschedule = True
                layer = ProcessingLayer.L1_EXACT

        # =====================================================================
        # LAYER 2: Disambiguation Check
        # =====================================================================
        if response is None and self.disambiguation.is_waiting:
            # User is providing disambiguation info
            # Route to correct handler based on state
            if self.disambiguation.context.state == DisambiguationState.WAITING_NICKNAME:
                # User responding to "Mario o Marione?"
                disamb_result = self.disambiguation.process_nickname_choice(user_input)
            else:
                # User providing birth date
                disamb_result = self.disambiguation.process_birth_date(user_input)

            if disamb_result.success:
                # Client resolved
                client = disamb_result.client
                self.session_manager.update_client(
                    self._current_session.session_id,
                    client.get("id", ""),
                    f"{client.get('nome', '')} {client.get('cognome', '')}".strip()
                )
                response = disamb_result.response_text
                intent = "disambiguation_resolved"
                layer = ProcessingLayer.L2_SLOT
            elif disamb_result.propose_registration:
                response = disamb_result.response_text
                intent = "propose_registration"
                layer = ProcessingLayer.L2_SLOT
            elif disamb_result.state == DisambiguationState.FAILED:
                response = disamb_result.response_text
                intent = "disambiguation_failed"
                layer = ProcessingLayer.L2_SLOT
                should_escalate = True
            else:
                # Need more info
                response = disamb_result.response_text
                intent = "disambiguation_waiting"
                layer = ProcessingLayer.L2_SLOT

        # =====================================================================
        # LAYER 2: Booking State Machine (Slot Filling)
        # =====================================================================
        print(f"[DEBUG L2] response is None: {response is None}")
        if response is None:
            intent_result = classify_intent(user_input)
            print(f"[DEBUG L2] intent_result.category: {intent_result.category}, booking state: {self.booking_sm.context.state}")

            # Check if this is a booking-related intent OR if we should continue booking flow
            # Allow INFO queries (FAQ) even on first turn - don't force booking flow
            # Only start booking if user explicitly wants to book OR we're already in a flow
            should_process_booking = (
                intent_result.category == IntentCategory.PRENOTAZIONE or
                self.booking_sm.context.state != BookingState.IDLE or
                # First turn: only start booking if not asking for INFO
                (is_first_turn and intent_result.category not in [IntentCategory.INFO, IntentCategory.CORTESIA])
            )

            if should_process_booking:
                sm_result = self.booking_sm.process_message(user_input)
                print(f"[DEBUG L2] sm_result.needs_db_lookup: {sm_result.needs_db_lookup}")
                response = sm_result.response
                # B2: Handle follow_up_response (split registration messages)
                if sm_result.has_follow_up():
                    response = response + "\n\n" + sm_result.follow_up_response
                intent = f"booking_{sm_result.next_state.value}"
                layer = ProcessingLayer.L2_SLOT

                # Check for booking completion
                if sm_result.booking:
                    # E1-S1: VERIFY SLOT AVAILABILITY BEFORE CREATING BOOKING
                    booking_data = sm_result.booking
                    slot_available = True

                    if booking_data.get("date") and booking_data.get("time"):
                        print(f"[DEBUG] Checking slot availability: {booking_data.get('date')} {booking_data.get('time')}")
                        avail_check = await self._check_slot_availability(
                            date=booking_data.get("date"),
                            time=booking_data.get("time"),
                            operator_id=booking_data.get("operator_id"),
                            service=booking_data.get("service")
                        )
                        slot_available = avail_check.get("available", True)

                        if not slot_available:
                            # Slot not available - offer alternatives or waitlist
                            alternatives = avail_check.get("alternatives", [])
                            if alternatives:
                                alt_times = ", ".join([a.get("time", "") for a in alternatives[:3]])
                                response = f"Mi dispiace, l'orario {booking_data.get('time')} non è disponibile. Posso offrirle: {alt_times}. Quale preferisce?"
                                self.booking_sm.context.state = BookingState.WAITING_TIME
                                self.booking_sm.context.time = None
                                self.booking_sm.context.time_display = None
                                intent = "slot_unavailable_alternatives"
                            else:
                                response = f"Mi dispiace, non ci sono posti disponibili per {booking_data.get('date')}. Vuole che la inserisca in lista d'attesa?"
                                self.booking_sm.context.waiting_for_waitlist_confirm = True
                                intent = "slot_unavailable_waitlist"
                            print(f"[DEBUG] Slot unavailable: {response}")

                    # Only create booking if slot is available
                    if slot_available:
                        booking_result = await self._create_booking(sm_result.booking)
                        if booking_result.get("success"):
                            intent = "booking_created"
                            # Fire-and-forget WhatsApp confirmation
                            await self._send_wa_booking_confirmation(sm_result.booking)
                        else:
                            print(f"[DEBUG] Booking creation failed: {booking_result.get('error')}")

                # Check for DB lookups needed
                if sm_result.needs_db_lookup:
                    print(f"[DEBUG] DB Lookup needed: {sm_result.lookup_type} - {sm_result.lookup_params}")
                    if sm_result.lookup_type == "client":
                        # Search for client - use first name only for broader search
                        full_name = sm_result.lookup_params.get("name", "")
                        name_to_search = full_name.split()[0] if full_name else ""
                        print(f"[DEBUG] Searching for client: '{name_to_search}' (from '{full_name}')")
                        client_result = await self._search_client(name_to_search)
                        clienti = client_result.get("clienti", [])
                        print(f"[DEBUG] Client search result: ambiguo={client_result.get('ambiguo')}, count={len(clienti)}")

                        if len(clienti) == 0:
                            # No client found - propose registration
                            print(f"[DEBUG] No client found for '{name_to_search}' - proposing registration")
                            self.booking_sm.context.is_new_client = True
                            response = f"Non ho trovato {full_name} tra i nostri clienti. Vuole registrarsi? Le chiederò nome, telefono ed email."
                            self.booking_sm.context.state = BookingState.PROPOSE_REGISTRATION
                            intent = "propose_registration"

                        elif len(clienti) == 1 and not client_result.get("ambiguo"):
                            # Exactly one client found - greet as returning client
                            cliente = clienti[0]
                            print(f"[DEBUG] Found unique client: {cliente.get('nome')} (ID: {cliente.get('id')})")
                            self.booking_sm.context.client_id = cliente.get("id")
                            full_name = f"{cliente.get('nome', '')} {cliente.get('cognome', '')}".strip()
                            self.booking_sm.context.client_name = full_name
                            display_name = cliente.get('nome', '') or full_name
                            # Build next question based on current state
                            state = self.booking_sm.context.state
                            if state == BookingState.WAITING_SERVICE:
                                next_q = "Come posso aiutarla? Mi dica che trattamento desidera."
                            elif state == BookingState.WAITING_DATE:
                                svc = self.booking_sm.context.service_display or self.booking_sm.context.service or ""
                                next_q = f"Bene, {svc}! Per quale giorno?"
                            elif state == BookingState.WAITING_TIME:
                                next_q = "A che ora le farebbe comodo?"
                            else:
                                next_q = "Come posso aiutarla?"
                            response = f"Bentornato {display_name}! {next_q}"
                            intent = "client_found"

                        elif client_result.get("ambiguo"):
                            # Need disambiguation
                            print(f"[DEBUG] Starting disambiguation for {name_to_search}")
                            disamb = self.disambiguation.start_disambiguation(
                                name_to_search,
                                clienti
                            )
                            response = disamb.response_text
                            needs_disambiguation = True
                            intent = "disambiguation_needed"
                            print(f"[DEBUG] Disambiguation response: {response}")

                    elif sm_result.lookup_type == "availability":
                        # Check availability
                        avail = await self.availability.check_date(
                            sm_result.lookup_params.get("date", ""),
                            sm_result.lookup_params.get("service")
                        )
                        if not avail.has_slots:
                            # No slots available - offer waitlist
                            if self.booking_sm.context.client_id:
                                response = f"{avail.message} Vuole che la inserisca in lista d'attesa? La contatteremo appena si libera un posto."
                                intent = "offer_waitlist"
                                # Store flag for next turn
                                self.booking_sm.context.waiting_for_waitlist_confirm = True
                            else:
                                response = avail.message

                    elif sm_result.lookup_type == "waitlist":
                        # User confirmed waitlist - add to waitlist
                        if self.booking_sm.context.client_id:
                            waitlist_result = await self._add_to_waitlist(
                                client_id=self.booking_sm.context.client_id,
                                service=self.booking_sm.context.service or "",
                                preferred_date=self.booking_sm.context.date
                            )
                            if waitlist_result.get("success"):
                                response = "Perfetto, l'ho inserita in lista d'attesa. La contatteremo appena si libera un posto."
                                intent = "waitlist_added"
                                self.booking_sm.reset()
                            else:
                                response = "Mi scusi, c'è stato un problema. Può riprovare più tardi?"
                                intent = "waitlist_error"
                        else:
                            response = "Mi serve prima il suo nome per la lista d'attesa."
                            intent = "waitlist_need_name"

                    elif sm_result.lookup_type == "create_client":
                        # Create new client in database
                        client_data = sm_result.lookup_params or {}
                        print(f"[DEBUG] Creating new client: {client_data}")
                        create_result = await self._create_client(client_data)
                        if create_result.get("success"):
                            # Store client ID in booking context
                            self.booking_sm.context.client_id = create_result.get("id")
                            print(f"[DEBUG] Client created with ID: {create_result.get('id')}")
                            intent = "client_created"
                        else:
                            print(f"[DEBUG] Client creation failed: {create_result.get('error')}")

                    elif sm_result.lookup_type == "operator":
                        # Search for operators
                        print(f"[DEBUG] Searching operators")
                        operators_result = await self._search_operators()
                        operators = operators_result.get("operatori", [])
                        if operators:
                            # Store operator info if only one, or ask for preference
                            print(f"[DEBUG] Found {len(operators)} operators")
                            if len(operators) == 1:
                                self.booking_sm.context.operator_id = operators[0].get("id")
                                self.booking_sm.context.operator_name = operators[0].get("nome")

        # =====================================================================
        # LAYER 2.5: Appointment Management (Cancel/Reschedule)
        # =====================================================================

        # E4-S1: Handle pending cancel flow
        if self._pending_cancel and response is None:
            response, intent, layer = await self._handle_cancel_flow(user_input)

        # E4-S2: Handle pending reschedule flow
        if self._pending_reschedule and response is None:
            response, intent, layer = await self._handle_reschedule_flow(user_input)

        # Check for new cancel/reschedule intents
        if response is None:
            intent_result = classify_intent(user_input)

            if intent_result.category == IntentCategory.CANCELLAZIONE:
                # E4-S1: User wants to cancel an appointment
                if self.booking_sm.context.client_id:
                    # We know the client - get their appointments
                    appointments_result = await self._get_client_appointments(
                        self.booking_sm.context.client_id
                    )
                    appointments = appointments_result.get("appointments", [])

                    if len(appointments) == 0:
                        response = "Non ho trovato appuntamenti a suo nome. Posso aiutarla in altro modo?"
                        intent = "cancel_no_appointments"
                    elif len(appointments) == 1:
                        # Only one appointment - confirm directly
                        appt = appointments[0]
                        self._pending_appointments = appointments
                        self._pending_cancel = True
                        self._selected_appointment_id = appt.get("id")
                        response = f"Ho trovato il suo appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. Conferma la cancellazione?"
                        intent = "cancel_confirm_single"
                    else:
                        # Multiple appointments - ask which one
                        self._pending_appointments = appointments
                        self._pending_cancel = True
                        appt_list = "\n".join([
                            f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                            for a in appointments[:5]
                        ])
                        response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole cancellare? Mi dica la data."
                        intent = "cancel_multiple"
                    layer = ProcessingLayer.L2_SLOT
                else:
                    response = "Per cancellare un appuntamento, mi può dire il suo nome?"
                    intent = "cancel_need_name"
                    layer = ProcessingLayer.L2_SLOT

            elif intent_result.category == IntentCategory.SPOSTAMENTO:
                # E4-S2: User wants to reschedule an appointment
                if self.booking_sm.context.client_id:
                    # We know the client - get their appointments
                    appointments_result = await self._get_client_appointments(
                        self.booking_sm.context.client_id
                    )
                    appointments = appointments_result.get("appointments", [])

                    if len(appointments) == 0:
                        response = "Non ho trovato appuntamenti a suo nome. Vuole prenotarne uno nuovo?"
                        intent = "reschedule_no_appointments"
                    elif len(appointments) == 1:
                        # Only one appointment - ask for new date/time
                        appt = appointments[0]
                        self._pending_appointments = appointments
                        self._pending_reschedule = True
                        self._selected_appointment_id = appt.get("id")
                        response = f"Ha un appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. Per quando vuole spostarlo?"
                        intent = "reschedule_ask_new_date"
                    else:
                        # Multiple appointments - ask which one
                        self._pending_appointments = appointments
                        self._pending_reschedule = True
                        appt_list = "\n".join([
                            f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                            for a in appointments[:5]
                        ])
                        response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole spostare? Mi dica la data."
                        intent = "reschedule_multiple"
                    layer = ProcessingLayer.L2_SLOT
                else:
                    response = "Per spostare un appuntamento, mi può dire il suo nome?"
                    intent = "reschedule_need_name"
                    layer = ProcessingLayer.L2_SLOT

        # =====================================================================
        # LAYER 3: FAQ Retrieval
        # =====================================================================
        if response is None:
            intent_result = classify_intent(user_input)

            if intent_result.category == IntentCategory.INFO and self.faq_manager:
                faq_result = self.faq_manager.find_answer(user_input)
                if faq_result:
                    response = faq_result.answer
                    intent = f"faq_{faq_result.source}"
                    layer = ProcessingLayer.L3_FAQ

        # =====================================================================
        # LAYER 3.5: Guided Dialog (for off-track conversations during booking)
        # =====================================================================
        if response is None and self.guided_engine and booking_in_progress:
            try:
                # Use guided dialog to help user back on track
                if not hasattr(self, '_guided_context') or self._guided_context is None:
                    # Start guided dialog session
                    _, self._guided_context = self.guided_engine.start_dialog()
                    # Sync existing booking context to guided context
                    self._guided_context.slot_values = {
                        "servizio": self.booking_sm.context.service,
                        "data": self.booking_sm.context.date,
                        "ora": self.booking_sm.context.time,
                        "cliente_nome": self.booking_sm.context.client_name,
                    }

                # Process through guided dialog
                guided_response, guided_state = self.guided_engine.process_user_input(user_input)

                # Check if guided dialog produced a useful response
                if guided_state not in [GuidedDialogState.FALLBACK_3_ESCALATION, GuidedDialogState.ERROR]:
                    response = guided_response
                    intent = f"guided_{guided_state.value}"
                    layer = ProcessingLayer.L3_FAQ  # Using L3 as closest match
                    print(f"[GUIDED] State: {guided_state.value}, Response: {response[:80]}...")
                else:
                    # Guided dialog escalated - reset and let Groq handle
                    self._guided_context = None
                    print(f"[GUIDED] Escalated to Groq after {guided_state.value}")

            except Exception as e:
                print(f"[GUIDED] Error: {e}")
                self._guided_context = None

        # =====================================================================
        # LAYER 4: Groq LLM (Fallback)
        # =====================================================================
        if response is None:
            try:
                # Build context for LLM
                context = self._build_llm_context()

                response = await self.groq.generate_response(
                    messages=[{"role": "user", "content": user_input}],
                    system_prompt=context
                )
                intent = "groq_response"
                layer = ProcessingLayer.L4_GROQ
            except Exception as e:
                print(f"Groq error: {e}")
                response = "Mi scusi, ho avuto un problema tecnico. Puo ripetere?"
                intent = "error_fallback"
                layer = ProcessingLayer.L4_GROQ

        # =====================================================================
        # POST-PROCESSING
        # =====================================================================

        # Store last response for "repeat" command
        self._last_response = response

        # Log turn to session
        latency = (time.time() - start_time) * 1000
        self.session_manager.add_turn(
            session_id=self._current_session.session_id,
            user_input=user_input,
            intent=intent,
            response=response,
            latency_ms=latency,
            layer_used=layer.value
        )

        # Synthesize audio
        audio = await self.tts.synthesize(response)

        # Handle escalation
        if should_escalate:
            self.session_manager.close_session(
                self._current_session.session_id,
                "escalated",
                escalation_reason=intent
            )

        return OrchestratorResult(
            response=response,
            intent=intent,
            layer=layer,
            latency_ms=latency,
            audio_bytes=audio,
            session_id=self._current_session.session_id,
            booking_context=self.booking_sm.context.to_dict(),
            should_escalate=should_escalate,
            needs_disambiguation=needs_disambiguation
        )

    async def end_session(self, outcome: str = "completed") -> bool:
        """End current session."""
        if self._current_session:
            return self.session_manager.close_session(
                self._current_session.session_id,
                outcome
            )
        return False

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _check_special_command(self, text: str) -> Optional[Tuple[str, str]]:
        """Check for special commands (L0)."""
        text_lower = text.lower().strip()

        # Exact match
        if text_lower in SPECIAL_COMMANDS:
            return SPECIAL_COMMANDS[text_lower]

        # Partial match (contains)
        for cmd, (action, response) in SPECIAL_COMMANDS.items():
            if cmd in text_lower:
                return (action, response)

        return None

    async def _load_business_config(self) -> Optional[Dict[str, Any]]:
        """Load business configuration from HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/verticale/config"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"Could not load business config: {e}")
        return None

    def _extract_vertical_key(self, verticale_id: str) -> str:
        """
        Extract vertical key from verticale_id.

        Examples:
            "salone_bella_vita" -> "salone"
            "wellness_gym_fit" -> "wellness"
            "medical_studio_rossi" -> "medical"
            "auto_officina_mario" -> "auto"
        """
        # Known vertical prefixes
        VERTICALS = ["salone", "wellness", "medical", "auto", "altro"]

        verticale_lower = verticale_id.lower()
        for v in VERTICALS:
            if verticale_lower.startswith(v):
                return v

        # Default fallback
        return "altro"

    def _load_vertical_faqs(self, config: Optional[Dict[str, Any]] = None) -> int:
        """
        Load FAQs for current vertical with variable substitution.

        Args:
            config: Business configuration for variable substitution

        Returns:
            Number of FAQs loaded
        """
        if not self.faq_manager:
            return 0

        if not HAS_VERTICAL_LOADER:
            print("[FAQ] Vertical loader not available")
            return 0

        # Build settings dict for variable substitution
        settings = {}
        if config:
            # Map DB config to FAQ variables
            settings.update({
                "NOME_ATTIVITA": config.get("nome_attivita", ""),
                "INDIRIZZO": config.get("indirizzo", ""),
                "TELEFONO": config.get("telefono", ""),
                "EMAIL": config.get("email", ""),
                "ORARI_APERTURA": config.get("orari_formattati", "Lun-Ven 9-18"),
                "METODI_PAGAMENTO": config.get("metodi_pagamento", "contanti, carte"),
            })

        try:
            faqs = load_faqs_for_vertical(self._faq_vertical, settings)
            if faqs:
                for faq in faqs:
                    self.faq_manager.add_faq(
                        question=faq.get("question", ""),
                        answer=faq.get("answer", ""),
                        category=faq.get("category", ""),
                        faq_id=faq.get("id", "")
                    )
            print(f"[FAQ] Loaded {len(faqs)} FAQs for vertical '{self._faq_vertical}'")
            return len(faqs)
        except Exception as e:
            print(f"[FAQ] Error loading FAQs: {e}")
            return 0

    def _handle_back(self) -> str:
        """Handle 'back' command in state machine."""
        state = self.booking_sm.context.state

        if state == BookingState.WAITING_TIME:
            self.booking_sm.context.date = None
            self.booking_sm.context.date_display = None
            self.booking_sm.context.state = BookingState.WAITING_DATE
            return "D'accordo. Per quale giorno desidera?"

        elif state == BookingState.WAITING_DATE:
            self.booking_sm.context.service = None
            self.booking_sm.context.service_display = None
            self.booking_sm.context.state = BookingState.WAITING_SERVICE
            return "D'accordo. Quale servizio desidera?"

        elif state == BookingState.CONFIRMING:
            self.booking_sm.context.time = None
            self.booking_sm.context.time_display = None
            self.booking_sm.context.state = BookingState.WAITING_TIME
            return "D'accordo. A che ora preferisce?"

        return "Mi dica pure cosa vuole cambiare."

    def _build_llm_context(self) -> str:
        """Build system prompt for Groq LLM."""
        return f"""Sei Sara, l'assistente vocale di {self.business_name}.

PERSONALITA':
- Cordiale, professionale, empatica
- Risposte BREVI (max 2-3 frasi)
- Parli italiano con accento neutro
- Usa "Lei" (formale)

CAPACITA':
1. Prenotare appuntamenti
2. Verificare disponibilita
3. Fornire info su orari e prezzi
4. Spostare/cancellare appuntamenti

CONTESTO ATTUALE:
{self._get_context_summary()}

REGOLE:
- NON inventare informazioni
- Se non sai, dì che verifichi
- Rispondi SEMPRE in italiano
"""

    def _get_context_summary(self) -> str:
        """Get current conversation context summary."""
        ctx = self.booking_sm.context
        parts = []

        if ctx.service:
            parts.append(f"Servizio: {ctx.service_display or ctx.service}")
        if ctx.date:
            parts.append(f"Data: {ctx.date_display or ctx.date}")
        if ctx.time:
            parts.append(f"Ora: {ctx.time}")
        if ctx.client_name:
            parts.append(f"Cliente: {ctx.client_name}")

        return "\n".join(parts) if parts else "Nessun contesto"

    async def _search_client(self, name: str) -> Dict[str, Any]:
        """Search for client via HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/clienti/search?q={name}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"Client search error: {e}")
        return {"clienti": [], "ambiguo": False}

    async def _create_booking(self, booking: Dict[str, Any]) -> Dict[str, Any]:
        """Create booking via HTTP Bridge."""
        # Check if we have a client_id - required for booking
        client_id = booking.get("client_id")
        if not client_id:
            print(f"[ERROR] Cannot create booking without client_id!")
            return {"success": False, "error": "client_id is required"}

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/create"
                # Transform field names to match HTTP Bridge API
                payload = {
                    "cliente_id": client_id,
                    "servizio": booking.get("service", ""),
                    "data": booking.get("date", ""),
                    "ora": booking.get("time", ""),
                    "operatore_id": booking.get("operator_id"),
                }
                print(f"[DEBUG] Creating booking: {payload}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    print(f"[DEBUG] Booking creation result: {result}")
                    if resp.status == 200:
                        return result
                    else:
                        print(f"[ERROR] Booking creation failed: {resp.status} - {result}")
                        return {"success": False, "error": result.get("error", "Unknown error")}
        except Exception as e:
            print(f"Booking creation error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _send_wa_booking_confirmation(self, booking: Dict[str, Any]) -> None:
        """
        Send WhatsApp booking confirmation to client.
        Fire-and-forget: logs errors but never fails the booking.
        """
        if not self._wa_client:
            return

        phone = self.booking_sm.context.client_phone
        if not phone:
            logger.info("[WA] No phone number for client, skipping WA confirmation")
            return

        try:
            nome = booking.get("client_name", "")
            servizio = self.booking_sm.context.service_display or booking.get("service", "")
            data = self.booking_sm.context.date_display or booking.get("date", "")
            ora = booking.get("time", "")
            operatore = booking.get("operator_name")

            msg = WhatsAppTemplates.conferma(
                nome=nome,
                servizio=servizio,
                data=data,
                ora=ora,
                operatore=operatore,
                nome_attivita=self.business_name,
            )

            normalized_phone = self._wa_client.normalize_phone(phone)
            result = await self._wa_client.send_message_async(normalized_phone, msg)

            if result.get("success"):
                logger.info(f"[WA] Booking confirmation sent to {normalized_phone}")
            else:
                logger.warning(f"[WA] Failed to send confirmation: {result.get('error')}")
        except Exception as e:
            # Never fail the booking because of WA
            logger.warning(f"[WA] Confirmation send error (non-critical): {e}")

    async def _create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new client via HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/clienti/create"
                payload = {
                    "nome": client_data.get("nome", ""),
                    "cognome": client_data.get("cognome"),
                    "telefono": client_data.get("telefono"),
                    "email": client_data.get("email"),
                    "data_nascita": client_data.get("data_nascita"),
                    "soprannome": client_data.get("soprannome"),
                    "note": client_data.get("note", "Registrato via Voice Agent"),
                }
                print(f"[DEBUG] Creating client: {payload}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    print(f"[DEBUG] Client creation result: {result}")
                    if resp.status == 200:
                        return result
        except Exception as e:
            print(f"Client creation error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _check_slot_availability(
        self,
        date: str,
        time: str,
        operator_id: Optional[str] = None,
        service: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        E1-S1: Check if a specific slot is available before confirming booking.

        Returns:
            {
                "available": True/False,
                "alternatives": [{"time": "10:00"}, {"time": "11:00"}, ...] if not available
            }
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/disponibilita"
                payload = {
                    "data": date,
                    "ora": time,
                    "operatore_id": operator_id,
                    "servizio": service
                }
                print(f"[DEBUG] Checking availability: {payload}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    print(f"[DEBUG] Availability result: {result}")
                    if resp.status == 200:
                        # Parse response - endpoint returns slots array
                        slots = result.get("slots", [])
                        # Check if requested time is in available slots
                        requested_time = time
                        is_available = any(
                            slot.get("ora", "").startswith(requested_time[:5])
                            for slot in slots
                        )
                        # Get alternatives if not available
                        alternatives = []
                        if not is_available and slots:
                            alternatives = [{"time": s.get("ora")} for s in slots[:5]]
                        return {
                            "available": is_available,
                            "alternatives": alternatives
                        }
        except Exception as e:
            print(f"Availability check error: {e}")
        # Default to available if bridge unavailable (fail-open)
        return {"available": True, "alternatives": []}

    async def _search_operators(self) -> Dict[str, Any]:
        """Get available operators via HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/operatori/list"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"Operators search error: {e}")
        return {"operatori": []}

    async def _cancel_booking(self, appointment_id: str) -> Dict[str, Any]:
        """Cancel an existing appointment via HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/cancel"
                payload = {"id": appointment_id}
                print(f"[DEBUG] Cancelling appointment: {appointment_id}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    print(f"[DEBUG] Cancel result: {result}")
                    return result
        except Exception as e:
            print(f"Cancel booking error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _reschedule_booking(self, appointment_id: str, new_date: str, new_time: str) -> Dict[str, Any]:
        """Reschedule an existing appointment via HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/reschedule"
                payload = {
                    "id": appointment_id,
                    "data": new_date,
                    "ora": new_time
                }
                print(f"[DEBUG] Rescheduling appointment: {payload}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    print(f"[DEBUG] Reschedule result: {result}")
                    return result
        except Exception as e:
            print(f"Reschedule booking error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _add_to_waitlist(self, client_id: str, service: str, preferred_date: str = None) -> Dict[str, Any]:
        """Add client to waitlist via HTTP Bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/waitlist/add"
                payload = {
                    "cliente_id": client_id,
                    "servizio": service,
                    "data_preferita": preferred_date,
                    "priorita": "normale"
                }
                print(f"[DEBUG] Adding to waitlist: {payload}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    print(f"[DEBUG] Waitlist result: {result}")
                    return result
        except Exception as e:
            print(f"Waitlist add error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _get_client_appointments(self, client_id: str) -> Dict[str, Any]:
        """
        E4-S1: Get upcoming appointments for a client via HTTP Bridge.

        Returns:
            {"appointments": [{id, data, ora, servizio, operatore_nome}, ...]}
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/cliente/{client_id}"
                print(f"[DEBUG] Getting appointments for client: {client_id}")
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"[DEBUG] Client appointments: {result}")
                        return result
        except Exception as e:
            print(f"Get appointments error: {e}")
        return {"appointments": []}

    async def _handle_cancel_flow(
        self, user_input: str
    ) -> Tuple[Optional[str], str, ProcessingLayer]:
        """
        E4-S1: Handle subsequent turns in cancel flow.

        Returns: (response, intent, layer)
        """
        text_lower = user_input.lower()
        response = None
        intent = "cancel_flow"
        layer = ProcessingLayer.L2_SLOT

        # Check for confirmation (sì/no)
        if self._selected_appointment_id:
            # We're waiting for confirmation
            affirmative = ["sì", "si", "ok", "va bene", "confermo", "certo"]
            negative = ["no", "annulla", "niente", "lascia"]

            if any(word in text_lower for word in affirmative):
                # Confirmed - execute cancellation
                result = await self._cancel_booking(self._selected_appointment_id)
                if result.get("success"):
                    response = "Appuntamento cancellato con successo. Posso aiutarla in altro modo?"
                    intent = "cancel_success"
                else:
                    response = f"Mi dispiace, c'è stato un problema: {result.get('error', 'errore sconosciuto')}. Riprovi più tardi."
                    intent = "cancel_error"
                # Reset state
                self._reset_cancel_reschedule_state()
            elif any(word in text_lower for word in negative):
                response = "D'accordo, non ho cancellato nulla. Posso aiutarla in altro modo?"
                intent = "cancel_aborted"
                self._reset_cancel_reschedule_state()
            else:
                response = "Mi dica sì per confermare la cancellazione o no per annullare."
                intent = "cancel_confirm_repeat"
        else:
            # User should specify which appointment (by date)
            # Try to extract date from input
            from entity_extractor import extract_date
            date_result = extract_date(user_input)

            if date_result:
                target_date = date_result.to_string("%Y-%m-%d")
                # Find matching appointment
                for appt in self._pending_appointments:
                    if appt.get("data") == target_date:
                        self._selected_appointment_id = appt.get("id")
                        response = f"Conferma cancellazione: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}?"
                        intent = "cancel_confirm_selected"
                        break

                if not self._selected_appointment_id:
                    response = f"Non ho trovato appuntamenti per {date_result.to_italian()}. Provi con un'altra data."
                    intent = "cancel_date_not_found"
            else:
                response = "Non ho capito la data. Può dirmi il giorno dell'appuntamento da cancellare?"
                intent = "cancel_need_date"

        return response, intent, layer

    async def _handle_reschedule_flow(
        self, user_input: str
    ) -> Tuple[Optional[str], str, ProcessingLayer]:
        """
        E4-S2: Handle subsequent turns in reschedule flow.

        Returns: (response, intent, layer)
        """
        text_lower = user_input.lower()
        response = None
        intent = "reschedule_flow"
        layer = ProcessingLayer.L2_SLOT

        # Import entity extractor
        from entity_extractor import extract_date, extract_time

        if self._selected_appointment_id and self._reschedule_new_date:
            # We have appointment and new date, waiting for time or confirmation
            if self._reschedule_new_time:
                # All info collected - waiting for confirmation
                affirmative = ["sì", "si", "ok", "va bene", "confermo", "certo"]
                negative = ["no", "annulla", "niente", "lascia"]

                if any(word in text_lower for word in affirmative):
                    # Execute reschedule
                    result = await self._reschedule_booking(
                        self._selected_appointment_id,
                        self._reschedule_new_date,
                        self._reschedule_new_time
                    )
                    if result.get("success"):
                        response = f"Appuntamento spostato a {self._reschedule_new_date} alle {self._reschedule_new_time}. Posso aiutarla in altro modo?"
                        intent = "reschedule_success"
                    else:
                        response = f"Mi dispiace, c'è stato un problema: {result.get('error', 'errore sconosciuto')}. Riprovi più tardi."
                        intent = "reschedule_error"
                    self._reset_cancel_reschedule_state()
                elif any(word in text_lower for word in negative):
                    response = "D'accordo, non ho spostato nulla. Posso aiutarla in altro modo?"
                    intent = "reschedule_aborted"
                    self._reset_cancel_reschedule_state()
                else:
                    response = "Mi dica sì per confermare lo spostamento o no per annullare."
                    intent = "reschedule_confirm_repeat"
            else:
                # Need time
                time_result = extract_time(user_input)
                if time_result:
                    self._reschedule_new_time = time_result.to_string()
                    # Check availability before confirming
                    avail = await self._check_slot_availability(
                        self._reschedule_new_date,
                        self._reschedule_new_time
                    )
                    if avail.get("available"):
                        response = f"Sposto l'appuntamento a {self._reschedule_new_date} alle {self._reschedule_new_time}. Conferma?"
                        intent = "reschedule_confirm"
                    else:
                        alternatives = avail.get("alternatives", [])
                        if alternatives:
                            alt_times = ", ".join([a.get("time", "") for a in alternatives[:3]])
                            response = f"L'orario {self._reschedule_new_time} non è disponibile. Posso offrirle: {alt_times}. Quale preferisce?"
                            self._reschedule_new_time = None
                            intent = "reschedule_time_unavailable"
                        else:
                            response = f"Non ci sono posti disponibili per {self._reschedule_new_date}. Vuole provare un altro giorno?"
                            self._reschedule_new_date = None
                            intent = "reschedule_date_full"
                else:
                    response = "A che ora preferisce il nuovo appuntamento?"
                    intent = "reschedule_need_time"
        elif self._selected_appointment_id:
            # Have appointment, need new date
            date_result = extract_date(user_input)
            if date_result:
                self._reschedule_new_date = date_result.to_string("%Y-%m-%d")
                response = f"Perfetto, {date_result.to_italian()}. A che ora preferisce?"
                intent = "reschedule_got_date"
            else:
                response = "Non ho capito la data. Per quando vuole spostare l'appuntamento?"
                intent = "reschedule_need_date"
        else:
            # Need to select which appointment first
            date_result = extract_date(user_input)
            if date_result:
                target_date = date_result.to_string("%Y-%m-%d")
                for appt in self._pending_appointments:
                    if appt.get("data") == target_date:
                        self._selected_appointment_id = appt.get("id")
                        response = f"Ho selezionato: {appt.get('servizio', 'servizio')} il {appt.get('data', '')}. Per quando vuole spostarlo?"
                        intent = "reschedule_selected"
                        break
                if not self._selected_appointment_id:
                    response = f"Non ho trovato appuntamenti per {date_result.to_italian()}. Provi con un'altra data."
                    intent = "reschedule_date_not_found"
            else:
                response = "Non ho capito. Quale appuntamento vuole spostare? Mi dica la data."
                intent = "reschedule_need_selection"

        return response, intent, layer

    def _reset_cancel_reschedule_state(self):
        """Reset cancel/reschedule flow state."""
        self._pending_cancel = False
        self._pending_reschedule = False
        self._pending_appointments = []
        self._selected_appointment_id = None
        self._reschedule_new_date = None
        self._reschedule_new_time = None


# =============================================================================
# FACTORY
# =============================================================================

def create_orchestrator(
    verticale_id: str,
    business_name: str,
    **kwargs
) -> VoiceOrchestrator:
    """
    Factory function to create orchestrator.

    Args:
        verticale_id: Business vertical ID
        business_name: Business name (MUST use this, not hardcoded)
        **kwargs: Additional config

    Returns:
        Configured VoiceOrchestrator
    """
    return VoiceOrchestrator(
        verticale_id=verticale_id,
        business_name=business_name,
        **kwargs
    )


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("FLUXION Voice Orchestrator - Enterprise Test")
        print("=" * 60)

        # Create orchestrator with custom business name
        orchestrator = create_orchestrator(
            verticale_id="salone_bella_vita",
            business_name="Salone Bella Vita"  # NOT "FLUXION Demo"!
        )

        # Start session
        print("\n1. Starting session...")
        result = await orchestrator.start_session()
        print(f"   Greeting: {result.response}")
        print(f"   Session: {result.session_id[:8]}...")

        # Test booking flow
        print("\n2. Testing booking flow...")

        inputs = [
            "Vorrei prenotare un taglio",
            "domani",
            "alle 15",
            "si confermo"
        ]

        for user_input in inputs:
            print(f"\n   User: {user_input}")
            result = await orchestrator.process(user_input)
            print(f"   Sara: {result.response}")
            print(f"   Layer: {result.layer.value}, Intent: {result.intent}")
            print(f"   Latency: {result.latency_ms:.1f}ms")

        # End session
        await orchestrator.end_session("completed")
        print("\n   Session ended.")

    asyncio.run(test())
