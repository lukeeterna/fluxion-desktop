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
    from .tts import get_tts
except ImportError:
    from intent_classifier import classify_intent, IntentCategory, IntentResult
    from booking_state_machine import BookingStateMachine, BookingState, StateMachineResult
    from disambiguation_handler import DisambiguationHandler, DisambiguationState, DisambiguationResult
    from availability_checker import AvailabilityChecker, AvailabilityResult, get_availability_checker
    from session_manager import SessionManager, VoiceSession, SessionChannel, get_session_manager
    from groq_client import GroqClient
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

try:
    try:
        from .sentiment import SentimentAnalyzer, FrustrationLevel
    except ImportError:
        from sentiment import SentimentAnalyzer, FrustrationLevel
    HAS_SENTIMENT = True
except ImportError:
    HAS_SENTIMENT = False


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
        http_bridge_url: str = HTTP_BRIDGE_URL
    ):
        """
        Initialize orchestrator.

        Args:
            verticale_id: Business vertical ID
            business_name: Business name (used in greetings)
            groq_api_key: Optional Groq API key (uses env var if not provided)
            use_piper_tts: Use Piper TTS (True) or system fallback (False)
            http_bridge_url: HTTP Bridge URL for database operations
        """
        self.verticale_id = verticale_id
        self.business_name = business_name
        self.http_bridge_url = http_bridge_url

        # Initialize components
        self.session_manager = get_session_manager()
        self.groq = GroqClient(api_key=groq_api_key)
        self.tts = get_tts(use_piper=use_piper_tts)
        self.booking_sm = BookingStateMachine()
        self.disambiguation = DisambiguationHandler()
        self.availability = get_availability_checker()

        # FAQ Manager (optional)
        self.faq_manager = None
        if HAS_FAQ_MANAGER:
            self.faq_manager = FAQManager()

        # Sentiment Analyzer (optional)
        self.sentiment = None
        if HAS_SENTIMENT:
            self.sentiment = SentimentAnalyzer()

        # Current session
        self._current_session: Optional[VoiceSession] = None
        self._last_response: str = ""

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

        # Load business name from database if not set or placeholder
        if not self.business_name or self.business_name in ["PLACEHOLDER", "La tua attivita"]:
            db_config = await self._load_business_config()
            if db_config and db_config.get("nome_attivita"):
                self.business_name = db_config["nome_attivita"]

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
                self._current_session = session
        if not self._current_session:
            await self.start_session()

        # Initialize result
        response: Optional[str] = None
        intent: str = "unknown"
        layer: ProcessingLayer = ProcessingLayer.L4_GROQ
        should_escalate: bool = False

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
        # LAYER 0b: Sentiment Analysis (escalation check)
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

        if response is None:
            intent_result = classify_intent(user_input)

            # Skip CONFERMA/RIFIUTO when booking is active (handled by L2)
            skip_for_booking = (
                booking_in_progress and
                intent_result.category in [IntentCategory.CONFERMA, IntentCategory.RIFIUTO]
            )

            if not skip_for_booking and intent_result.response and intent_result.category in [
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

        # =====================================================================
        # LAYER 2: Disambiguation Check
        # =====================================================================
        if response is None and self.disambiguation.is_waiting:
            # User is providing disambiguation info (birth date)
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
        if response is None:
            intent_result = classify_intent(user_input)

            # Check if this is a booking-related intent
            if intent_result.category == IntentCategory.PRENOTAZIONE or \
               self.booking_sm.context.state != BookingState.IDLE:
                sm_result = self.booking_sm.process_message(user_input)
                response = sm_result.response
                intent = f"booking_{sm_result.next_state.value}"
                layer = ProcessingLayer.L2_SLOT

                # Check for booking completion
                if sm_result.booking:
                    # Create booking via HTTP Bridge
                    booking_result = await self._create_booking(sm_result.booking)
                    if booking_result.get("success"):
                        intent = "booking_created"

                # Check for DB lookups needed
                if sm_result.needs_db_lookup:
                    if sm_result.lookup_type == "client":
                        # Search for client
                        client_result = await self._search_client(
                            sm_result.lookup_params.get("name", "")
                        )
                        if client_result.get("ambiguo"):
                            # Need disambiguation
                            disamb = self.disambiguation.start_disambiguation(
                                sm_result.lookup_params.get("name", ""),
                                client_result.get("clienti", [])
                            )
                            response = disamb.response_text

                    elif sm_result.lookup_type == "availability":
                        # Check availability
                        avail = await self.availability.check_date(
                            sm_result.lookup_params.get("date", ""),
                            sm_result.lookup_params.get("service")
                        )
                        if not avail.has_slots:
                            response = avail.message

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
            should_escalate=should_escalate
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
        return f"""Sei Paola, l'assistente vocale di {self.business_name}.

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
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/create"
                async with session.post(
                    url,
                    json=booking,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"Booking creation error: {e}")
        return {"success": False, "error": "Bridge not available"}


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
            print(f"   Paola: {result.response}")
            print(f"   Layer: {result.layer.value}, Intent: {result.intent}")
            print(f"   Latency: {result.latency_ms:.1f}ms")

        # End session
        await orchestrator.end_session("completed")
        print("\n   Session ended.")

    asyncio.run(test())
