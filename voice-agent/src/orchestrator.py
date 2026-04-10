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

import re
import io
import time
import wave
import asyncio
import aiohttp
try:
    from .http_client import shared_session
except ImportError:
    from http_client import shared_session
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime

# Local imports - support both package and direct execution
try:
    from .intent_classifier import classify_intent, IntentCategory, IntentResult
    from .booking_state_machine import BookingStateMachine, BookingState, StateMachineResult, TEMPLATES, get_goodbye
    from .disambiguation_handler import DisambiguationHandler, DisambiguationState, DisambiguationResult
    from .availability_checker import AvailabilityChecker, AvailabilityResult, get_availability_checker
    from .session_manager import SessionManager, VoiceSession, SessionChannel, get_session_manager
    from .groq_client import GroqClient, LLM_FAST_MODEL
    from .groq_nlu import GroqNLU
    from .tts import get_tts, TTSCache
    from .audit_client import audit_client
    from .operator_gender import extract_operator_gender_preference
    from .prosody_injector import ProsodyInjector
except ImportError:
    from intent_classifier import classify_intent, IntentCategory, IntentResult
    from booking_state_machine import BookingStateMachine, BookingState, StateMachineResult, TEMPLATES, get_goodbye
    from disambiguation_handler import DisambiguationHandler, DisambiguationState, DisambiguationResult
    from availability_checker import AvailabilityChecker, AvailabilityResult, get_availability_checker
    from session_manager import SessionManager, VoiceSession, SessionChannel, get_session_manager
    from groq_client import GroqClient, LLM_FAST_MODEL
    from groq_nlu import GroqNLU
    from tts import get_tts, TTSCache
    from audit_client import audit_client
    from operator_gender import extract_operator_gender_preference
    from prosody_injector import ProsodyInjector

# Italian Regex module (L0 content filter, escalation, corrections)
try:
    try:
        from .italian_regex import (
            prefilter, check_content, is_escalation as regex_is_escalation,
            ContentSeverity, RegexPreFilterResult,
            strip_fillers, is_ambiguous_date,
            extract_multi_services, get_service_synonyms,
            VERTICAL_SERVICES, check_vertical_guardrail,
            is_time_pressure,
        )
    except ImportError:
        from italian_regex import (
            prefilter, check_content, is_escalation as regex_is_escalation,
            ContentSeverity, RegexPreFilterResult,
            strip_fillers, is_ambiguous_date,
            extract_multi_services, get_service_synonyms,
            VERTICAL_SERVICES, check_vertical_guardrail,
            is_time_pressure,
        )
    HAS_ITALIAN_REGEX = True
except ImportError:
    HAS_ITALIAN_REGEX = False
    print("[INFO] Italian regex module not available")

# F03: Intent LRU cache (100-slot, eliminates 3x classify_intent per turn)
try:
    try:
        from .intent_lru_cache import get_cached_intent, clear_intent_cache
    except ImportError:
        from intent_lru_cache import get_cached_intent, clear_intent_cache
    HAS_INTENT_CACHE = True
except ImportError:
    def get_cached_intent(user_input: str) -> Any:  # type: ignore[misc]
        return classify_intent(user_input)
    def clear_intent_cache() -> None:  # type: ignore[misc]
        pass
    HAS_INTENT_CACHE = False

# Vertical entity extractor (F02)
try:
    try:
        from .entity_extractor import extract_vertical_entities
    except ImportError:
        from entity_extractor import extract_vertical_entities
    HAS_VERTICAL_ENTITIES = True
except ImportError:
    HAS_VERTICAL_ENTITIES = False

try:
    try:
        from .entity_extractor import detect_solito as _detect_solito
    except ImportError:
        from entity_extractor import detect_solito as _detect_solito
except ImportError:
    def _detect_solito(text: str) -> bool:
        return False

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

# B5: Tone Adapter — adapts response text based on caller sentiment
try:
    try:
        from .tone_adapter import ToneAdapter
    except ImportError:
        from tone_adapter import ToneAdapter
    HAS_TONE_ADAPTER = True
except ImportError:
    HAS_TONE_ADAPTER = False

# B4: Backchannel Engine (conversational acknowledgments)
try:
    try:
        from .backchannel_engine import BackchannelEngine
    except ImportError:
        from backchannel_engine import BackchannelEngine
    HAS_BACKCHANNEL = True
except ImportError:
    HAS_BACKCHANNEL = False

# Guided Dialog Engine (new approach)
try:
    import sys
    from pathlib import Path
    # Add parent directory to path for guided_dialog import
    from resource_path import get_bundle_root
    _voice_agent_root = get_bundle_root()
    if str(_voice_agent_root) not in sys.path:
        sys.path.insert(0, str(_voice_agent_root))
    from guided_dialog import GuidedDialogEngine, DialogState as GuidedDialogState
    HAS_GUIDED_DIALOG = True
except ImportError as e:
    print(f"[INFO] Guided Dialog not available: {e}")
    HAS_GUIDED_DIALOG = False

# Legacy Advanced NLU removed (S83) — LLM NLU is now primary
HAS_ADVANCED_NLU = False

# C1: Caller Memory — cross-call persistence for returning callers
try:
    try:
        from .caller_memory import CallerMemory, get_caller_memory, CallerProfile
    except ImportError:
        from caller_memory import CallerMemory, get_caller_memory, CallerProfile
    HAS_CALLER_MEMORY = True
except ImportError:
    HAS_CALLER_MEMORY = False

# F1: EOU (End-of-Utterance) detection — adaptive silence + sentence completion
try:
    try:
        from .eou import get_adaptive_silence_ms, sentence_complete_probability
    except ImportError:
        from eou import get_adaptive_silence_ms, sentence_complete_probability
    HAS_EOU = True
except ImportError:
    HAS_EOU = False

# F2: Acoustic frustration detection — numpy DSP
try:
    try:
        from .acoustic_frustration import AcousticFrustrationDetector
    except ImportError:
        from acoustic_frustration import AcousticFrustrationDetector
    HAS_ACOUSTIC_FRUSTRATION = True
except ImportError:
    HAS_ACOUSTIC_FRUSTRATION = False

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
# WHATSAPP FAQ PATTERNS (L0a) - precompiled for hot path
# =============================================================================
_WA_FAQ_PATTERNS = [
    re.compile(r"\bwhatsapp\b", re.IGNORECASE),
    re.compile(r"\bconferma\s+(?:via|su|per|tramite)\b", re.IGNORECASE),
    re.compile(r"\b(?:mandate|inviate|spedite|mandate)\s+(?:conferma|messaggio|notifica)\b", re.IGNORECASE),
]

# Bug 1 NLU Hardening F02.1: "non voglio cancellare" = keep the booking.
# Must be checked BEFORE L1 CANCELLAZIONE processing.
# Covers: "non voglio cancellare", "no non cancellare", "non cancellare niente",
#          "non annullare", "non disdire", "non eliminare"
_NEGATED_CANCEL = re.compile(
    r"\b(?:no\s+)?non\s+(?:voglio\s+|intendo\s+|desidero\s+|devo\s+|posso\s+)?"
    r"(?:cancellare?|annullare?|disdire?|eliminare?)\b",
    re.IGNORECASE
)

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

# F03: Canned fallback responses for Groq timeout/unavailability
# Pre-warm these in main.py startup to eliminate TTS latency for these phrases
FALLBACK_RESPONSES: Dict[str, str] = {
    "timeout": "Mi scusi, sto impiegando un po' di tempo. Posso aiutarla a prenotare un appuntamento?",
    "rate_limit": "Mi scusi, sono momentaneamente sovraccarica. Puo ripetere?",
    "generic": "Posso aiutarla principalmente con le prenotazioni. Desidera fissare un appuntamento?",
    "error": "Mi scusi, ho avuto un problema tecnico. Puo ripetere?",
}


def _concat_wav_chunks(chunks: List[bytes]) -> bytes:
    """
    Concatenate multiple WAV audio chunks into a single WAV file.

    World-class: enables parallel TTS synthesis across LLM stream chunks,
    then merges results preserving audio quality (same sample rate + channels).
    Gap: no PMI competitor parallelizes LLM streaming with TTS synthesis.
    """
    valid = [c for c in chunks if c]
    if not valid:
        return b""
    if len(valid) == 1:
        return valid[0]

    all_frames: List[bytes] = []
    params = None
    for chunk_bytes in valid:
        try:
            with wave.open(io.BytesIO(chunk_bytes), "rb") as wf:
                if params is None:
                    params = wf.getparams()
                all_frames.append(wf.readframes(wf.getnframes()))
        except Exception:
            pass  # Skip malformed WAV chunks

    if not all_frames or params is None:
        return valid[0]  # Fallback: return first chunk intact

    out_buf = io.BytesIO()
    with wave.open(out_buf, "wb") as wf:
        wf.setparams(params)
        for frames in all_frames:
            wf.writeframes(frames)
    return out_buf.getvalue()


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
    should_exit: bool = False
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
            "should_exit": self.should_exit,
            "booking_created": self.booking_created,
            "booking_id": self.booking_id,
        }


# ═══════════════════════════════════════════════════════════════════
# LLM NLU → IntentResult adapter (2026 architecture)
# ═══════════════════════════════════════════════════════════════════
try:
    try:
        from .nlu.schemas import SaraIntent, NLUResult
    except ImportError:
        from nlu.schemas import SaraIntent, NLUResult

    _SARA_TO_INTENT = {
        SaraIntent.PRENOTAZIONE: IntentCategory.PRENOTAZIONE,
        SaraIntent.CANCELLAZIONE: IntentCategory.CANCELLAZIONE,
        SaraIntent.SPOSTAMENTO: IntentCategory.SPOSTAMENTO,
        SaraIntent.WAITLIST: IntentCategory.WAITLIST,
        SaraIntent.CONFERMA: IntentCategory.CONFERMA,
        SaraIntent.RIFIUTO: IntentCategory.RIFIUTO,
        SaraIntent.CORTESIA: IntentCategory.CORTESIA,
        SaraIntent.CHIUSURA: IntentCategory.CORTESIA,
        SaraIntent.ESCALATION: IntentCategory.OPERATORE,
        SaraIntent.FAQ: IntentCategory.INFO,
        SaraIntent.CORREZIONE: IntentCategory.UNKNOWN,
        SaraIntent.OSCENITA: IntentCategory.UNKNOWN,
        SaraIntent.ALTRO: IntentCategory.UNKNOWN,
    }
    HAS_NLU_SCHEMAS = True
except ImportError:
    HAS_NLU_SCHEMAS = False


def _nlu_to_intent_result(nlu_result: "NLUResult", user_input: str) -> "IntentResult":
    """Convert LLM NLUResult → IntentResult for backward compatibility with L1-L4 pipeline."""
    category = _SARA_TO_INTENT.get(nlu_result.intent, IntentCategory.UNKNOWN)

    # S142 FIX-4: CHIUSURA always gets a goodbye intent name and guaranteed response
    # This ensures should_exit fires even when exact_match_intent finds no match
    if HAS_NLU_SCHEMAS:
        try:
            from .nlu.schemas import SaraIntent as _SI
        except ImportError:
            from nlu.schemas import SaraIntent as _SI
        if nlu_result.intent == _SI.CHIUSURA:
            return IntentResult(
                intent="llm_chiusura_goodbye",  # contains both keywords for should_exit
                category=IntentCategory.CORTESIA,
                confidence=nlu_result.confidence,
                response="Arrivederci, buona giornata!",
            )

    # For cortesia-type categories, get response text from exact_match_intent (fast, <1ms)
    response_text = None
    if category in (IntentCategory.CORTESIA, IntentCategory.CONFERMA,
                    IntentCategory.RIFIUTO, IntentCategory.OPERATORE):
        try:
            try:
                from .intent_classifier import exact_match_intent
            except ImportError:
                from intent_classifier import exact_match_intent
            cortesia_match = exact_match_intent(user_input)
            if cortesia_match and cortesia_match.response:
                response_text = cortesia_match.response
        except Exception:
            pass

    return IntentResult(
        intent=f"llm_{nlu_result.intent.value.lower()}",
        category=category,
        confidence=nlu_result.confidence,
        response=response_text,
    )


# B1: Filler phrases for VoIP — played before slow operations (DB lookup, Groq)
FILLER_PHRASES = [
    "Un momento...",
    "Vediamo...",
    "Un attimo che controllo...",
    "Ora verifico...",
]


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
        self.prosody = ProsodyInjector()
        self.session_manager = get_session_manager()
        self.groq = GroqClient(api_key=groq_api_key)
        # FluxionTTS Adaptive — delegates to tts_engine.py TTSEngineSelector based on .tts_mode file
        self.tts = TTSCache(get_tts(use_piper=use_piper_tts))
        self._groq_nlu = GroqNLU(api_key=groq_api_key)
        _initial_services = VERTICAL_SERVICES.get(verticale_id, {}) if HAS_ITALIAN_REGEX else {}
        self.booking_sm = BookingStateMachine(
            groq_nlu=self._groq_nlu,
            services_config=_initial_services,
        )
        self.booking_sm._business_name = self.business_name  # B3: propagate for goodbye variants
        self.disambiguation = DisambiguationHandler()
        self.availability = get_availability_checker()

        # WhatsApp client (optional, for post-booking confirmation)
        self._wa_client = None
        if HAS_WHATSAPP:
            try:
                self._wa_client = WhatsAppClient()
                logger.info("[WA] WhatsApp client initialized for booking confirmations")
            except (ImportError, OSError, RuntimeError) as e:
                logger.warning("[WA] WhatsApp client init failed (non-critical): %s", e)

        # FAQ Manager (optional) - loads FAQs based on vertical
        self.faq_manager = None
        self._faq_vertical = self._extract_vertical_key(verticale_id)
        self._vertical_explicitly_set = False  # S135: tracks if set_vertical() was called
        if HAS_FAQ_MANAGER:
            self.faq_manager = FAQManager()
            # Load vertical-specific FAQs (async loaded on first session)

        # Sentiment Analyzer (optional)
        self.sentiment = None
        if HAS_SENTIMENT:
            self.sentiment = SentimentAnalyzer()

        # B5: Tone Adapter — adapts response based on caller sentiment
        self.tone_adapter = ToneAdapter() if HAS_TONE_ADAPTER else None

        # F2: Acoustic frustration detector
        self.acoustic_detector = AcousticFrustrationDetector() if HAS_ACOUSTIC_FRUSTRATION else None

        # B4: Backchannel Engine (conversational acknowledgments)
        self.backchannel = BackchannelEngine() if HAS_BACKCHANNEL else None

        # C1: Caller Memory — cross-call persistence for returning callers
        self.caller_memory = get_caller_memory() if HAS_CALLER_MEMORY else None
        self._caller_profile: Optional[CallerProfile] = None if HAS_CALLER_MEMORY else None

        # Advanced NLU: spaCy + UmBERTo (optional)
        # Provides improved intent detection for:
        # - "mai stato" → NEW_CLIENT (not "Mai" as name)
        # - "prima volta" → automatic registration flow
        # - Third-party bookings: "per mia madre Maria"
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
            except (ImportError, OSError, RuntimeError) as e:
                print(f"[GUIDED] Guided Dialog init failed: {e}")

        # STT Name Corrector — CoVe 2026 (Layer 1: prompt injection + Layer 2: phonetic fix)
        self._name_corrector = None
        try:
            from src.name_corrector import STTNameCorrector
            # S135: Use _find_db_path() to locate actual Tauri DB with clienti table
            _nc_db = self._find_db_path() or db_path
            self._name_corrector = STTNameCorrector(_nc_db)
            print(f"[NameCorrector] STT Name Corrector inizializzato — db={_nc_db}")
        except Exception as _nc_err:
            print(f"[NameCorrector] Init fallito (non bloccante): {_nc_err}")

        # LLM NLU Engine (2026 architecture — PRIMARY)
        self._llm_nlu = None
        try:
            from nlu.llm_nlu import create_llm_nlu
            self._llm_nlu = create_llm_nlu()
            logger.info("[NLU-LLM] LLM NLU engine initialized (PRIMARY mode)")
        except Exception as _llm_nlu_err:
            logger.warning("[NLU-LLM] LLM NLU init failed (falling back to regex): %s", _llm_nlu_err)

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

        # S118: Cancel+Rebook — after cancel success, propose rebooking
        self._pending_rebook_after_cancel: bool = False
        self._cancelled_service: Optional[str] = None

        # S118: Package proposal after booking
        self._pending_package_proposal: bool = False
        self._proposed_package: Optional[Dict[str, Any]] = None

        # Track last booking for WhatsApp confirmation
        self._last_booking_data: Optional[Dict[str, Any]] = None
        self._whatsapp_sent: bool = False

        # P1-12: Time pressure flag — client is in a hurry → concise LLM responses
        self._time_pressure: bool = False

        # P1-8: Per-session booking state machines (concurrent sessions)
        self._session_states: Dict[str, "BookingStateMachine"] = {}
        self._session_initial_services: Dict[str, Any] = {}

        # GAP-H2: Business context for Groq system prompt (loaded async in start_session)
        self._business_hours: Optional[str] = None
        self._business_services: Optional[str] = None
        self._business_operators: Optional[str] = None

        # F19: Valid operator names cache (populated from DB, used for entity validation)
        self._valid_operator_names: set = set()
        # F19: Business hours data for slot alternatives
        self._business_hours_open: str = "09:00"
        self._business_hours_close: str = "19:00"

        # GAP-P0-3: Holidays loaded from DB (propagated to availability.config.holidays)
        self._holidays: List[str] = []

        # A2: Greeting pre-synthesis flag — avoids re-warming on every start_session()
        self._greetings_warmed: bool = False
        self._greetings_warmed_for: Optional[str] = None  # business_name used for last warm

        # B1: VoIP filler support — fillers only play during VoIP calls, not text API
        self._is_voip_call: bool = False
        self._fillers_warmed: bool = False

    # =========================================================================
    # GREETING PRE-SYNTHESIS (A2)
    # =========================================================================

    async def warm_greetings(self) -> None:
        """
        Pre-synthesize all 3 time-of-day greeting variants into TTSCache.

        After this call, start_session() greeting TTS is 0ms (cache hit).
        Idempotent: skips if already warmed for the current business_name.
        """
        if self._greetings_warmed and self._greetings_warmed_for == self.business_name:
            return

        greetings = [
            f"{self.business_name}, buongiorno! Come posso aiutarla?",
            f"{self.business_name}, buon pomeriggio! Come posso aiutarla?",
            f"{self.business_name}, buonasera! Come posso aiutarla?",
        ]
        await self.tts.warm_cache(greetings)
        self._greetings_warmed = True
        self._greetings_warmed_for = self.business_name
        logger.info("[A2] Greeting pre-synthesis done for '%s' (3 variants)", self.business_name)

    async def warm_fillers(self) -> None:
        """B1: Pre-synthesize filler phrases into TTSCache.

        Called once during first VoIP greet(). Idempotent.
        """
        if self._fillers_warmed:
            return
        await self.tts.warm_cache(list(FILLER_PHRASES))
        self._fillers_warmed = True
        logger.info("[B1] Filler pre-synthesis done (%d phrases)", len(FILLER_PHRASES))

    async def _get_filler_audio(self) -> Optional[bytes]:
        """B1: Get a random filler phrase as audio bytes.

        Returns None if not in VoIP mode or fillers not warmed.
        Only call this before slow operations (DB lookup, Groq).
        """
        if not self._is_voip_call:
            return None
        import random
        phrase = random.choice(FILLER_PHRASES)
        try:
            return await self.tts.synthesize(phrase)
        except Exception:
            return None

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
            # S135: Only override if not explicitly set by set_vertical()
            if db_config.get("categoria_attivita") and not self._vertical_explicitly_set:
                self._faq_vertical = db_config["categoria_attivita"]

        # GAP-H2: Load business hours/services/operators for Groq system prompt
        await self._load_business_context()

        # Load vertical-specific FAQs AFTER business context (needs service prices)
        if self.faq_manager and not self.faq_manager.faqs:
            self._load_vertical_faqs(db_config)

        # Full reset booking state machine for a brand-new session (new call)
        self.booking_sm.reset(full_reset=True)
        self.booking_sm._business_name = self.business_name  # B3: sync after config load
        clear_intent_cache()  # F03: clear LRU cache to avoid cross-session pollution
        self.disambiguation = DisambiguationHandler()
        # FIX-3 CoVe2026: reset sentiment history — non accumulare tra sessioni diverse
        if self.sentiment:
            self.sentiment.reset_history()
        # B4: Reset backchannel engine for new session
        if self.backchannel:
            self.backchannel.reset()
        # B5: Reset tone adapter for new session
        if self.tone_adapter:
            self.tone_adapter.reset()
        # F2: Reset acoustic frustration detector for new call
        if self.acoustic_detector:
            self.acoustic_detector.reset()
        # P1-12: reset time pressure for new session
        self._time_pressure = False
        # S122: reset ALL pending state flags for new session
        self._pending_cancel = False
        self._pending_reschedule = False
        self._pending_rebook_after_cancel = False
        self._pending_package_proposal = False
        self._proposed_package = None
        self._pending_appointments = []
        self._selected_appointment_id = None

        # C3: Look up caller memory for personalized greeting
        self._caller_profile = None
        if self.caller_memory and phone_number:
            self._caller_profile = self.caller_memory.lookup(phone_number)
            if self._caller_profile and self._caller_profile.is_returning:
                logger.info(f"[C3] Returning caller: {self._caller_profile.client_name} (calls: {self._caller_profile.call_count})")

        # Create session
        self._current_session = self.session_manager.create_session(
            verticale_id=self.verticale_id,
            business_name=self.business_name,
            channel=channel,
            phone_number=phone_number
        )

        # AUDIT: Log session start
        audit_client.log_session_start(
            session_id=self._current_session.session_id,
            phone_number=phone_number,
            verticale_id=self.verticale_id
        )

        # A2: Pre-warm greeting TTS cache (idempotent, skips if already done for this business_name)
        await self.warm_greetings()

        # G5: Proactive anticipation — if returning caller with history,
        # offer "il solito" at greeting (saves 2-3 turns)
        _caller_name = ""
        _proactive_greeting = None
        if self._caller_profile and self._caller_profile.is_returning and self._caller_profile.client_name:
            _caller_name = self._caller_profile.client_name
            # G5: If caller has last_service, proactively offer it
            if (self._caller_profile.last_service
                    and self._caller_profile.call_count >= 2):
                _proactive_greeting = await self._build_proactive_greeting(
                    self._current_session.session_id, self._caller_profile
                )

        if _proactive_greeting:
            greeting = _proactive_greeting
            logger.info("[G5] Proactive greeting for %s: %s", _caller_name, greeting[:80])
        else:
            # C3: personalized greeting for returning callers (no proactive offer)
            greeting = self.session_manager.get_greeting(self._current_session.session_id, caller_name=_caller_name)
        self._last_response = greeting

        # Synthesize audio (0ms cache hit after warm_greetings)
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
        _t0 = time.perf_counter()  # F03: Per-layer timing (sub-ms accuracy)

        # Get or create session
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session:
                # P1-8: Restore per-session booking state machine
                if session_id in self._session_states:
                    self.booking_sm = self._session_states[session_id]
                elif self._current_session and self._current_session.session_id != session.session_id:
                    # Switching sessions: save current BSM under old session_id, load (or init) new one
                    _old_sid = self._current_session.session_id
                    self._session_states[_old_sid] = self.booking_sm
                    if session_id in self._session_states:
                        self.booking_sm = self._session_states[session_id]
                    else:
                        self.booking_sm.reset()
                        self._session_states[session_id] = self.booking_sm
                self._current_session = session
            else:
                # New session ID - full reset and create session with this ID
                if self._current_session:
                    # Save outgoing BSM state before reset
                    _old_sid = self._current_session.session_id
                    self._session_states[_old_sid] = self.booking_sm
                    self.booking_sm.reset(full_reset=True)
                await self.start_session()
                # Re-register the session under the caller's session_id
                if self._current_session:
                    self.session_manager._sessions[session_id] = self._current_session
                    self._current_session.session_id = session_id
                    self._session_states[session_id] = self.booking_sm
        else:
            # No session_id provided
            if self._current_session:
                # Session already exists — reuse it (e.g. VoIP mid-call)
                pass
            else:
                # No session at all — start fresh
                self.booking_sm.reset(full_reset=True)
                self.disambiguation.reset()
                await self.start_session()
        if not self._current_session:
            await self.start_session()

        # F19-FIX8: STT anti-hallucination filter
        # Discard nonsensical transcriptions (URLs, foreign text, ad content)
        if self._is_stt_hallucination(user_input):
            logger.info(f"[F19-STT] Hallucination filtered: '{user_input[:80]}'")
            latency = (time.time() - start_time) * 1000
            return OrchestratorResult(
                response="",  # Silent discard
                intent="stt_hallucination",
                layer=ProcessingLayer.L0_SPECIAL,
                latency_ms=latency,
                session_id=self._current_session.session_id if self._current_session else None,
            )

        # Initialize result
        response: Optional[str] = None
        intent: str = "unknown"
        layer: ProcessingLayer = ProcessingLayer.L4_GROQ
        should_escalate: bool = False
        should_exit: bool = False
        needs_disambiguation: bool = False

        # =====================================================================
        # PRIMARY: LLM NLU (2026 architecture)
        # Fires async task here, awaited at L1 for intent classification.
        # Regex is fallback if LLM fails or confidence < 0.5.
        # =====================================================================
        _llm_nlu_task = None
        _llm_nlu_result = None  # populated when awaited at L1
        if self._llm_nlu:
            _llm_filled_slots = {}
            ctx = self.booking_sm.context
            if ctx.client_name:
                _llm_filled_slots["nome"] = ctx.client_name
            if hasattr(ctx, 'client_surname') and ctx.client_surname:
                _llm_filled_slots["cognome"] = ctx.client_surname
            if ctx.service:
                _llm_filled_slots["servizio"] = ctx.service
            if ctx.date:
                _llm_filled_slots["data"] = ctx.date
            if ctx.time:
                _llm_filled_slots["ora"] = ctx.time

            _llm_nlu_task = asyncio.create_task(
                self._llm_nlu.extract(
                    text=user_input,
                    current_state=ctx.state.value if ctx.state else "IDLE",
                    filled_slots=_llm_filled_slots,
                    vertical=self._faq_vertical or self.verticale_id,
                    services=list(
                        (VERTICAL_SERVICES.get(self.verticale_id, {}) if HAS_ITALIAN_REGEX else {}).keys()
                    )[:20],
                )
            )

        # =====================================================================
        # S118: Package proposal / Rebook-after-cancel have priority over ALL layers
        # =====================================================================
        if self._pending_package_proposal:
            response, intent, layer = await self._handle_package_response(user_input)
            if response:
                pass  # response is set, skip all other layers

        if self._pending_rebook_after_cancel and response is None:
            response, intent, layer = await self._handle_rebook_after_cancel(user_input)
            if response:
                pass  # response is set, skip all other layers

        # =====================================================================
        # LAYER 0-PRE: Italian Regex Pre-Filter (Content + Escalation)
        # =====================================================================

        # GAP-P1-4: Detect operator gender preference — sticky, set once and kept
        if self.booking_sm.context.operator_gender_preference is None:
            _gender_pref = extract_operator_gender_preference(user_input)
            if _gender_pref:
                self.booking_sm.context.operator_gender_preference = _gender_pref
                print(f"[DEBUG] Gender preference detected: {_gender_pref}")

        if HAS_ITALIAN_REGEX:
            # P1-12: Detect time pressure — sticky flag for this session
            if is_time_pressure(user_input):
                self._time_pressure = True

            pre = prefilter(user_input)

            # Content filter: SEVERE → terminate session
            if pre.content_severity == ContentSeverity.SEVERE:
                response = pre.content_response
                intent = "content_filter_severe"
                layer = ProcessingLayer.L0_SPECIAL
                should_escalate = True  # End session

            # Content filter: MODERATE → firm redirect, continue
            elif pre.content_severity == ContentSeverity.MODERATE:
                response = pre.content_response
                intent = "content_filter_moderate"
                layer = ProcessingLayer.L0_SPECIAL
                # Don't terminate, just redirect

            # Content filter: MILD → soft redirect, continue
            elif pre.content_severity == ContentSeverity.MILD:
                # For mild language, log but let it through
                print(f"[L0] Mild language detected: {user_input}")
                # Don't set response - let normal flow continue

            # Escalation via regex (more comprehensive than special commands)
            if response is None and pre.is_escalation:
                intent = f"escalation_{pre.escalation_type}"
                layer = ProcessingLayer.L0_SPECIAL
                should_escalate = True
                esc_phone = await self._trigger_wa_escalation_call(pre.escalation_type)
                response = self._build_escalation_response(esc_phone, self._is_business_hours())

        # =====================================================================
        # LAYER 0-PRE: Vertical Guardrail
        # =====================================================================
        if response is None and HAS_ITALIAN_REGEX:
            _guardrail = check_vertical_guardrail(user_input, self._faq_vertical)
            if _guardrail.blocked:
                response = _guardrail.redirect_response
                intent = f"guardrail_{self.verticale_id}"
                layer = ProcessingLayer.L0_SPECIAL

        # =====================================================================
        # LAYER 0-PRE: Vertical Entity Extraction
        # =====================================================================
        # Run after guardrail (only if not already blocked). Stores vertical-
        # specific entities in context so FSM layers can use them.
        if response is None and HAS_ITALIAN_REGEX and HAS_VERTICAL_ENTITIES:
            _vert_entities = extract_vertical_entities(user_input, self._faq_vertical)
            # Store in booking_sm context for FSM access
            if not hasattr(self.booking_sm.context, 'extra_entities'):
                self.booking_sm.context.extra_entities = {}
            self.booking_sm.context.extra_entities.update({
                k: v for k, v in {
                    'specialty': _vert_entities.specialty,
                    'urgency': _vert_entities.urgency,
                    'visit_type': _vert_entities.visit_type,
                    'vehicle_plate': _vert_entities.vehicle_plate,
                    'vehicle_brand': _vert_entities.vehicle_brand,
                }.items() if v is not None
            })

            # GAP-G2: Medical urgency intercept — 118 advisory before booking flow
            # Triggers for: urgency="urgente" (subito/urgenza keywords) or visit_type="urgenza" (pronto soccorso)
            _is_medical_urgency = (
                _vert_entities.urgency == "urgente"
                or _vert_entities.visit_type == "urgenza"
            )
            if response is None and self.verticale_id == "medical" and _is_medical_urgency:
                response = (
                    "Per urgenze mediche, la consiglio di chiamare il 118 o presentarsi "
                    "direttamente al pronto soccorso. "
                    "Vuole comunque prenotare una visita per una data prossima?"
                )
                intent = "medical_urgency"
                layer = ProcessingLayer.L0_SPECIAL

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
                esc_phone = await self._trigger_wa_escalation_call("explicit_request")
                response = self._build_escalation_response(esc_phone, self._is_business_hours())
            elif action == "reset":
                self.booking_sm.reset()
                self.disambiguation.reset()
            elif action == "repeat":
                response = self._last_response or "Mi scusi, non ho nulla da ripetere."
            elif action == "back":
                # Handle back in state machine context
                response = self._handle_back()

        # =====================================================================
        # LAYER 0a: WhatsApp FAQ (prevent Groq denial)
        # Intercepts questions about WhatsApp before they fall to L4
        # =====================================================================
        if response is None:
            if any(p.search(user_input) for p in _WA_FAQ_PATTERNS):
                response = "Certo! Dopo la prenotazione riceverà una conferma via WhatsApp al numero che ci ha fornito."
                intent = "faq_whatsapp"
                layer = ProcessingLayer.L0_SPECIAL

        # =====================================================================
        # LAYER 0c: Sentiment Analysis (escalation check)
        # =====================================================================
        if response is None and self.sentiment:
            # FIX-1 CoVe2026: NON escalare per sentiment durante booking attivo.
            # L'utente risponde a domande della FSM — "no"/"ma" sono risposte, non frustrazione.
            _is_booking_active = self.booking_sm.context.state not in [
                BookingState.IDLE, BookingState.COMPLETED, BookingState.CANCELLED
            ]
            sentiment_result = self.sentiment.analyze(user_input)
            if sentiment_result.should_escalate and not _is_booking_active:
                intent = "escalation_frustration"
                layer = ProcessingLayer.L0_SPECIAL
                should_escalate = True
                esc_phone = await self._trigger_wa_escalation_call("frustration")
                response = self._build_escalation_response(
                    esc_phone, self._is_business_hours(), prefix="Mi scusi per il disagio. "
                )
            elif sentiment_result.should_escalate and _is_booking_active:
                import logging as _log
                _log.getLogger(__name__).info(
                    f"[SENTIMENT] Escalation soppressa durante booking attivo (state={self.booking_sm.context.state})"
                )

            # B5 + F2: Update tone adapter based on sentiment + acoustic frustration
            _frustration_level = sentiment_result.frustration_level.value
            if self.acoustic_detector and hasattr(self, '_last_acoustic_score'):
                # Fuse: if acoustic frustration is high, boost text frustration level
                if self._last_acoustic_score >= 0.5:
                    _frustration_level = max(_frustration_level, 3)
                elif self._last_acoustic_score >= 0.3:
                    _frustration_level = max(_frustration_level, 2)
            if self.tone_adapter:
                self.tone_adapter.update_tone(
                    sentiment_result.sentiment.value,
                    _frustration_level
                )

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

        # =====================================================================
        # P1-6: Ordinal slot selection (when alternatives were offered)
        # =====================================================================
        if (response is None and
                self.booking_sm.context.alternative_slots and
                self.booking_sm.context.state == BookingState.WAITING_TIME):
            _ordinal_match = re.search(
                r'\b(prim[oa]|second[oa]|terz[oa]|1[°oa]|2[°oa]|3[°oa]|uno|due|tre)\b',
                user_input, re.IGNORECASE
            )
            if _ordinal_match:
                _ordinal_map = {
                    'prim': 0, 'uno': 0, '1': 0,
                    'second': 1, 'due': 1, '2': 1,
                    'terz': 2, 'tre': 2, '3': 2,
                }
                _matched_lower = _ordinal_match.group(0).lower()
                for _key, _idx in _ordinal_map.items():
                    if _key in _matched_lower and _idx < len(self.booking_sm.context.alternative_slots):
                        _selected = self.booking_sm.context.alternative_slots[_idx]
                        self.booking_sm.context.time = _selected.get("time", "")[:5]
                        self.booking_sm.context.time_display = f"alle {self.booking_sm.context.time}"
                        self.booking_sm.context.time_is_approximate = False
                        self.booking_sm.context.alternative_slots = []
                        self.booking_sm.context.state = BookingState.CONFIRMING
                        response = (
                            f"Perfetto, ho selezionato {self.booking_sm.context.time_display}. "
                            + TEMPLATES.get(
                                "confirm_booking",
                                "Riepilogo: {summary}"
                            ).format(summary=self.booking_sm.context.get_summary())
                        )
                        intent = "ordinal_slot_selected"
                        layer = ProcessingLayer.L1_EXACT
                        break

        if response is None:
            # ── PRIMARY: LLM NLU (await task launched at start of turn) ──
            if _llm_nlu_task and not _llm_nlu_result:
                try:
                    _llm_nlu_result = await asyncio.wait_for(_llm_nlu_task, timeout=4.0)
                    _llm_nlu_task = None  # consumed
                except asyncio.TimeoutError:
                    logger.warning("[NLU-LLM] LLM NLU timed out (4s) — falling back to regex")
                    _llm_nlu_task = None
                except Exception as _llm_await_err:
                    logger.warning("[NLU-LLM] LLM NLU error: %s — falling back to regex", _llm_await_err)
                    _llm_nlu_task = None

            if _llm_nlu_result and _llm_nlu_result.confidence >= 0.5 and HAS_NLU_SCHEMAS:
                intent_result = _nlu_to_intent_result(_llm_nlu_result, user_input)
                logger.info(
                    "[NLU-LLM] PRIMARY intent=%s conf=%.2f provider=%s ms=%.0f | input='%s'",
                    _llm_nlu_result.intent.value, _llm_nlu_result.confidence,
                    _llm_nlu_result.provider, _llm_nlu_result.latency_ms,
                    user_input[:80],
                )
            else:
                # FALLBACK: regex intent classifier
                intent_result = get_cached_intent(user_input)
                if _llm_nlu_result:
                    logger.info(
                        "[NLU-LLM] Low confidence (%.2f) — using regex fallback for: '%s'",
                        _llm_nlu_result.confidence, user_input[:80],
                    )

            # S142 FIX-1: Standalone CHIUSURA/goodbye detector — decoupled from L1 response gate
            # Fires BEFORE any other routing to guarantee should_exit even at first turn
            _is_standalone_goodbye = False
            try:
                try:
                    from .intent_classifier import exact_match_intent as _emi
                except ImportError:
                    from intent_classifier import exact_match_intent as _emi
                _emi_result = _emi(user_input)
                if _emi_result and _emi_result.intent and "goodbye" in _emi_result.intent:
                    _is_standalone_goodbye = True
            except Exception:
                pass
            # Also check LLM NLU result
            if HAS_NLU_SCHEMAS and _llm_nlu_result:
                try:
                    from .nlu.schemas import SaraIntent as _SI2
                except ImportError:
                    from nlu.schemas import SaraIntent as _SI2
                if _llm_nlu_result.intent == _SI2.CHIUSURA:
                    _is_standalone_goodbye = True
            # Also check intent_result
            _ir_intent = (intent_result.intent or "").lower()
            if "goodbye" in _ir_intent or "chiusura" in _ir_intent:
                _is_standalone_goodbye = True

            if _is_standalone_goodbye:
                should_exit = True
                if not response:
                    # Use exact match response or fallback
                    if _emi_result and _emi_result.response:
                        response = _emi_result.response
                    else:
                        # B3: Context-aware goodbye
                        _bye_ctx = "booking_done" if self._last_booking_data else "generic"
                        response = get_goodbye(_bye_ctx, self.business_name, date=self.booking_sm.context.date_display or "")
                    intent = "goodbye_standalone"
                    layer = ProcessingLayer.L1_EXACT
                logger.info(f"[S142] Standalone goodbye detected: '{user_input[:40]}' → exit=True")

            # FIX-7 CoVe2026: reset sentiment history se l'utente torna a prenotare
            # dopo aver richiesto l'operatore (evita falsi positivi cross-turn)
            if (self.sentiment and
                    intent_result.category == IntentCategory.PRENOTAZIONE and
                    self.sentiment.get_cumulative_frustration() > 3):
                self.sentiment.reset_history()
                # B5: Also reset tone when sentiment history resets mid-conversation
                if self.tone_adapter:
                    self.tone_adapter.reset()

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
            # S142: Don't skip goodbye intents even on first turn
            _is_goodbye = (intent_result.category == IntentCategory.CORTESIA
                           and intent_result.intent
                           and ("goodbye" in intent_result.intent or "chiusura" in intent_result.intent))
            skip_greeting_cortesia = (
                is_first_turn and
                intent_result.category == IntentCategory.CORTESIA
                and not _is_goodbye  # S142: goodbye always processed
            )

            # S118: Skip cortesia/conferma/rifiuto when cancel/reschedule/rebook flow is active
            _in_appt_mgmt_flow = (
                self._pending_cancel or self._pending_reschedule
                or self._pending_rebook_after_cancel or self._pending_package_proposal
            )
            if response is None and not _in_appt_mgmt_flow and not skip_for_booking and not skip_greeting_cortesia and intent_result.response and intent_result.category in [
                IntentCategory.CORTESIA,
                IntentCategory.CONFERMA,
                IntentCategory.RIFIUTO,
                IntentCategory.OPERATORE,
            ]:
                response = intent_result.response
                intent = intent_result.intent
                layer = ProcessingLayer.L1_EXACT

                # S142: Goodbye intents → close the call
                if intent_result.category == IntentCategory.CORTESIA and intent_result.intent and ("goodbye" in intent_result.intent or "chiusura" in intent_result.intent):
                    should_exit = True
                    logger.info(f"[S142] Goodbye detected: '{intent_result.intent}' → closing call")

                # BUG-4 FIX: When CORTESIA triggers during active booking, append FSM re-prompt
                # so the conversation doesn't stall. E.g., "Grazie" → "Prego! Per quale giorno?"
                elif intent_result.category == IntentCategory.CORTESIA and booking_in_progress:
                    _reprompt = self.booking_sm.get_current_prompt()
                    if _reprompt:
                        response = f"{response} {_reprompt}"

                if intent_result.category == IntentCategory.OPERATORE:
                    should_escalate = True

            # Bug 1 F02.1: Negated cancellation = user wants to KEEP the booking.
            # "non voglio cancellare" contains "cancellare" which triggers CANCELLAZIONE.
            # Override: if the user is negating cancellation, treat as CONFERMA.
            if (response is None and
                    intent_result.category == IntentCategory.CANCELLAZIONE and
                    _NEGATED_CANCEL.search(user_input)):
                response = "Perfetto, il suo appuntamento rimane confermato. Posso aiutarla con altro?"
                intent = "negated_cancel_keep"
                layer = ProcessingLayer.L0_SPECIAL

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
                elif self.booking_sm.context.client_name:
                    # Have name but no client_id — search by name first
                    name = self.booking_sm.context.client_name.split()[0]
                    client_result = await self._search_client(name)
                    clienti = client_result.get("clienti", [])
                    if len(clienti) == 1:
                        self.booking_sm.context.client_id = clienti[0].get("id")
                        appointments_result = await self._get_client_appointments(
                            self.booking_sm.context.client_id
                        )
                        appointments = appointments_result.get("appointments", [])
                        if appointments:
                            self._pending_appointments = appointments
                            self._pending_cancel = True
                            if len(appointments) == 1:
                                appt = appointments[0]
                                self._selected_appointment_id = appt.get("id")
                                response = f"Ho trovato il suo appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. Conferma la cancellazione?"
                                intent = "cancel_confirm_single"
                            else:
                                appt_list = "\n".join([
                                    f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                                    for a in appointments[:5]
                                ])
                                response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole cancellare?"
                                intent = "cancel_multiple"
                        else:
                            response = "Non ho trovato appuntamenti a suo nome. Posso aiutarla in altro modo?"
                            intent = "cancel_no_appointments"
                    else:
                        response = "Per cancellare un appuntamento, mi può dire il suo nome?"
                        intent = "cancel_need_name"
                        self._pending_cancel = True
                else:
                    response = "Per cancellare un appuntamento, mi può dire il suo nome?"
                    intent = "cancel_need_name"
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
                elif self.booking_sm.context.client_name:
                    # Have name but no client_id — search by name first
                    name = self.booking_sm.context.client_name.split()[0]
                    client_result = await self._search_client(name)
                    clienti = client_result.get("clienti", [])
                    if len(clienti) == 1:
                        self.booking_sm.context.client_id = clienti[0].get("id")
                        appointments_result = await self._get_client_appointments(
                            self.booking_sm.context.client_id
                        )
                        appointments = appointments_result.get("appointments", [])
                        if appointments:
                            self._pending_appointments = appointments
                            self._pending_reschedule = True
                            if len(appointments) == 1:
                                appt = appointments[0]
                                self._selected_appointment_id = appt.get("id")
                                response = f"Ho trovato il suo appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. A quale data vuole spostarlo?"
                                intent = "reschedule_ask_new_date"
                            else:
                                appt_list = "\n".join([
                                    f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                                    for a in appointments[:5]
                                ])
                                response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole spostare?"
                                intent = "reschedule_multiple"
                        else:
                            response = "Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?"
                            intent = "reschedule_no_appointments"
                    else:
                        response = "Per spostare un appuntamento, mi può dire il suo nome?"
                        intent = "reschedule_need_name"
                        self._pending_reschedule = True
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
            # Reuse LLM NLU result from L1 if available, else regex fallback
            if _llm_nlu_result and _llm_nlu_result.confidence >= 0.5 and HAS_NLU_SCHEMAS:
                intent_result = _nlu_to_intent_result(_llm_nlu_result, user_input)
            else:
                intent_result = get_cached_intent(user_input)  # regex fallback
            print(f"[DEBUG L2] intent_result.category: {intent_result.category}, booking state: {self.booking_sm.context.state}")

            # Check if this is a booking-related intent OR if we should continue booking flow
            # Allow INFO queries (FAQ) even on first turn - don't force booking flow
            # Only start booking if user explicitly wants to book OR we're already in a flow
            # FIX: LLM NLU may classify FAQ as ALTRO — double-check with regex classifier
            _is_info = intent_result.category == IntentCategory.INFO
            # S123: Always double-check with regex for INFO — LLM may classify
            # "Quanto costa un abbonamento?" as PRENOTAZIONE instead of INFO
            if not _is_info:
                _regex_check = get_cached_intent(user_input)
                if _regex_check.category == IntentCategory.INFO:
                    _is_info = True
                    intent_result = _regex_check  # prefer regex for INFO detection
            # S127: Explicit INFO keyword guard — ensure "orari", "prezzi" etc. always route to FAQ
            _text_lower = user_input.lower()
            _info_kw_explicit = bool(re.search(
                r'\b(orari[o]?|prezz[oi]|cost[oai]|quanto\s+cost|listino|accettate|pagament[oi])\b',
                _text_lower
            ))
            if _info_kw_explicit and not _is_info:
                _is_info = True
                print(f"[DEBUG L2] S127 INFO keyword guard: forced _is_info=True for '{user_input}'")

            # S122: Detect booking-intent signals beyond PRENOTAZIONE classification
            # New client signals
            _has_new_client_signal = any(re.search(p, _text_lower) for p in [
                r"sono\s+nuov[oa]", r"pr[io]ma\s+volta", r"mai\s+stat[oa]",
                r"mai\s+venut[oa]", r"mai\s+prenotato", r"non\s+sono\s+cliente",
                r"non\s+sono\s+registrat", r"nuov[oa]\s+cliente",
                r"mi\s+chiamo\s+[a-zàèéìòù]+", r"non\s+sono\s+mai",
            ])
            # Name provision = likely wants to book ("sono Marco Rossi")
            _has_name = bool(getattr(intent_result, 'entities', None) and intent_result.entities.get("name"))
            if not _has_name:
                # Also check entity extraction for names like "Sono Valeria Greco"
                _has_name = bool(re.search(
                    r'(?:sono|mi\s+chiamo)\s+[A-ZÀ-Ö][a-zàèéìòù]+(?:\s+[A-ZÀ-Ö][a-zàèéìòù]+)?',
                    user_input, re.IGNORECASE
                ))
            # Explicit booking words that classifier might miss
            _has_booking_words = bool(re.search(
                r'\b(?:prenotar[ei]|appuntamento|fissare?|un\s+taglio|una?\s+visita|un\s+trattamento)\b',
                _text_lower
            ))
            # S118: Skip booking SM when cancel/reschedule/rebook/package flow is active
            _in_appointment_mgmt = (
                self._pending_cancel or self._pending_reschedule
                or self._pending_rebook_after_cancel or self._pending_package_proposal
            )
            # S127: _is_info blocks booking start from IDLE (FAQ has priority)
            # Non-IDLE states continue booking unless _is_info AND no booking entities
            _in_idle = self.booking_sm.context.state == BookingState.IDLE
            # S142: Bare name detection in IDLE — "Mario Rossi" or "Marco" (1-2 capitalized words)
            if not _has_name and _in_idle:
                _bare = user_input.strip().rstrip('.!?,;:')
                _words = _bare.split()
                # S142: Case-insensitive — STT often produces lowercase names
                if 1 <= len(_words) <= 3 and all(len(w) >= 2 for w in _words if w):
                    _not_name = {"buongiorno", "buonasera", "ciao", "salve", "grazie", "prego",
                                 "arrivederci", "perfetto", "benissimo", "certamente", "scusi"}
                    if not any(w.lower() in _not_name for w in _words):
                        _has_name = True
                        logger.info(f"[S142] Bare name detected in IDLE: '{_bare}'")
            should_process_booking = (
                not _in_appointment_mgmt and (
                    (intent_result.category == IntentCategory.PRENOTAZIONE and not _is_info) or
                    (not _in_idle and not _is_info) or
                    (_has_new_client_signal and not _is_info) or
                    (_has_name and not _is_info) or
                    (_has_booking_words and not _is_info) or
                    # First turn: only start booking if not asking for INFO
                    (is_first_turn and not _is_info and intent_result.category != IntentCategory.CORTESIA)
                )
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

                # C4: Preferred slot suggestion for returning callers
                if (self._caller_profile and self._caller_profile.is_returning
                        and sm_result.next_state == BookingState.WAITING_DATE
                        and self._caller_profile.preferred_day):
                    _pref = self._caller_profile
                    _suggestion_parts = []
                    if _pref.preferred_day:
                        _suggestion_parts.append(_pref.preferred_day)
                    if _pref.preferred_time:
                        _suggestion_parts.append(f"alle {_pref.preferred_time}")
                    if _suggestion_parts:
                        _slot_hint = " ".join(_suggestion_parts)
                        response = response.rstrip("?").rstrip() + f"? Di solito preferisce {_slot_hint}, va bene anche questa volta?"
                        logger.info(f"[C4] Slot suggestion: {_slot_hint}")

                # Check for booking completion
                if sm_result.booking:
                    # E1-S1: VERIFY SLOT AVAILABILITY BEFORE CREATING BOOKING
                    # P1-1: Enrich booking_data with multi-service info from context
                    booking_data = dict(sm_result.booking)
                    if self.booking_sm.context.services and len(self.booking_sm.context.services) > 1:
                        booking_data["services"] = self.booking_sm.context.services
                        # service_display already contains "Taglio e Barba" from BSM
                    slot_available = True

                    if booking_data.get("date") and booking_data.get("time"):
                        # P0-3: Pass all services for multi-service combo duration
                        multi_services = booking_data.get("services") or (
                            self.booking_sm.context.services if self.booking_sm.context.services and len(self.booking_sm.context.services) > 1 else None
                        )
                        print(f"[DEBUG] Checking slot availability: {booking_data.get('date')} {booking_data.get('time')} services={multi_services}")
                        avail_check = await self._check_slot_availability(
                            date=booking_data.get("date"),
                            time=booking_data.get("time"),
                            operator_id=booking_data.get("operator_id"),
                            service=booking_data.get("service"),
                            services=multi_services
                        )
                        slot_available = avail_check.get("available", True)

                        # World-class: TimeConstraint filtering — trova primo slot che soddisfa constraint
                        time_constraint_type = self.booking_sm.context.time_constraint_type
                        time_constraint_anchor = self.booking_sm.context.time_constraint_anchor

                        # FIX-1: Verifica constraint anche quando slot_available=True.
                        # Es: "dopo le 17" con slot 17:00 → 17:00 < 17:00 non soddisfa AFTER → forza ricerca alternativa.
                        if slot_available and time_constraint_type and time_constraint_anchor:
                            try:
                                try:
                                    from .entity_extractor import TimeConstraint as TC, TimeConstraintType as TCT
                                except ImportError:
                                    from entity_extractor import TimeConstraint as TC, TimeConstraintType as TCT
                                from datetime import time as dt_time
                                anchor_parts = time_constraint_anchor.split(":")
                                anchor_h, anchor_m = int(anchor_parts[0]), int(anchor_parts[1])
                                tc = TC(
                                    constraint_type=TCT(time_constraint_type),
                                    anchor_time=dt_time(anchor_h, anchor_m),
                                )
                                proposed_str = booking_data.get("time", "")
                                if proposed_str:
                                    proposed_h, proposed_m = map(int, proposed_str[:5].split(":"))
                                    if not tc.matches(dt_time(proposed_h, proposed_m)):
                                        # Slot libero ma non soddisfa il constraint → forza ricerca alternativa
                                        slot_available = False
                                        print(f"[TimeConstraint] FIX-1: slot {proposed_str} libero ma non soddisfa {time_constraint_type} {time_constraint_anchor} → cerco alternativa")
                            except Exception as e:
                                print(f"[TimeConstraint] FIX-1 pre-check error: {e}")

                        if time_constraint_type and time_constraint_anchor and not slot_available:
                            try:
                                try:
                                    from .entity_extractor import TimeConstraint as TC, TimeConstraintType as TCT
                                except ImportError:
                                    from entity_extractor import TimeConstraint as TC, TimeConstraintType as TCT
                                from datetime import time as dt_time
                                # Ricostruisci constraint da stringhe in context
                                anchor_parts = time_constraint_anchor.split(":")
                                anchor_h, anchor_m = int(anchor_parts[0]), int(anchor_parts[1])
                                tc = TC(
                                    constraint_type=TCT(time_constraint_type),
                                    anchor_time=dt_time(anchor_h, anchor_m),
                                )
                                # Filtra alternatives per soddisfare il constraint
                                all_slots = avail_check.get("alternatives", [])
                                matching = [
                                    s for s in all_slots
                                    if s.get("time") and tc.matches(
                                        dt_time(*map(int, s["time"][:5].split(":")))
                                    )
                                ]
                                if matching:
                                    # Proponi primo slot che soddisfa constraint
                                    best_slot = matching[0]["time"][:5]
                                    self.booking_sm.context.time = best_slot
                                    self.booking_sm.context.time_display = f"alle {best_slot}"
                                    self.booking_sm.context.time_constraint_type = None  # constraint soddisfatto
                                    self.booking_sm.context.time_constraint_anchor = None
                                    # Aggiorna booking data con slot corretto
                                    booking_data = {**booking_data, "time": best_slot}
                                    slot_available = True  # retry con slot corretto
                                    print(f"[TimeConstraint] {time_constraint_type} {time_constraint_anchor} → primo slot: {best_slot}")
                            except Exception as e:
                                print(f"[TimeConstraint] Filtering error: {e}")

                        if not slot_available:
                            # P1-5: Slot waterfall — store alternatives for ordinal selection (P1-6)
                            # and propose the first slot automatically
                            alternatives = avail_check.get("alternatives", [])
                            if alternatives:
                                # Store for P1-6 ordinal selection
                                self.booking_sm.context.alternative_slots = alternatives[:3]
                                alt_times = [a.get("time", "")[:5] for a in alternatives[:3]]
                                slots_display = " | ".join(
                                    [f"{i + 1}. {t}" for i, t in enumerate(alt_times)]
                                )
                                response = (
                                    f"Mi dispiace, l'orario {booking_data.get('time')} non è disponibile. "
                                    f"Il primo slot libero è alle {alt_times[0]}. "
                                    f"Va bene, oppure preferisce: {slots_display}?"
                                )
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
                            # Enrich booking data with client identity from context
                            # (sm_result.booking may lack client_name/client_phone)
                            self._last_booking_data = {
                                **sm_result.booking,
                                "client_name": self.booking_sm.context.client_name or "",
                                "client_phone": self.booking_sm.context.client_phone or "",
                            }
                            print(f"[DEBUG] Booking created successfully: {booking_result.get('id')}")
                            # Fire-and-forget WhatsApp confirmation immediately after booking —
                            # do NOT wait for formal call close (should_exit) as it may never arrive.
                            if not self._whatsapp_sent:
                                asyncio.ensure_future(
                                    self._send_wa_booking_confirmation(self._last_booking_data)
                                )
                                self._whatsapp_sent = True

                            # S118: Package proposal handled above (after sm_result check)
                        else:
                            print(f"[DEBUG] Booking creation failed: {booking_result.get('error')}")

                # E4: After booking confirmed (state=COMPLETED), check packages
                if (sm_result.next_state == BookingState.COMPLETED
                        and sm_result.booking
                        and self.booking_sm.context.client_id
                        and not self._pending_package_proposal):
                    package_proposal = self._check_package_proposal(
                        client_id=self.booking_sm.context.client_id,
                        service=self.booking_sm.context.service,
                    )
                    if package_proposal:
                        self._pending_package_proposal = True
                        self._proposed_package = package_proposal
                        response = (
                            f"{response} "
                            f"A proposito, abbiamo il pacchetto {package_proposal['nome']}: "
                            f"{package_proposal['servizi_inclusi']} sedute a {package_proposal['prezzo']:.0f} euro "
                            f"invece di {package_proposal['prezzo_originale']:.0f}. "
                            f"Le interessa?"
                        )
                        intent = "booking_created_with_package"

                # Propagate should_exit from state machine (booking completed/cancelled)
                if sm_result.should_exit:
                    should_exit = True

                # Check for DB lookups needed
                if sm_result.needs_db_lookup:
                    logger.debug(f"[DEBUG] DB Lookup needed: {sm_result.lookup_type}")
                    if sm_result.lookup_type == "client":
                        # Search for client - use first name only for broader search
                        full_name = sm_result.lookup_params.get("name", "")
                        name_to_search = full_name.split()[0] if full_name else ""
                        logger.debug(f"[DEBUG] Searching for client: {name_to_search[:1]}*** (len={len(full_name)})")
                        client_result = await self._search_client(name_to_search)
                        clienti = client_result.get("clienti", [])
                        logger.debug(f"[DEBUG] Client search result: ambiguo={client_result.get('ambiguo')}, count={len(clienti)}")

                        if len(clienti) == 0:
                            # No client found - propose registration
                            logger.debug(f"[DEBUG] No client found - proposing registration")
                            self.booking_sm.context.is_new_client = True
                            response = f"Non ho trovato {full_name} tra i nostri clienti. Vuole che la registri come nuovo cliente?"
                            self.booking_sm.context.state = BookingState.PROPOSE_REGISTRATION
                            intent = "propose_registration"

                        elif len(clienti) == 1 and not client_result.get("ambiguo"):
                            # Exactly one client found - greet as returning client
                            cliente = clienti[0]
                            _n = cliente.get('nome', '') or ''
                            logger.debug(f"[DEBUG] Found unique client: {_n[:1]}*** (ID: {cliente.get('id')})")
                            self.booking_sm.context.client_id = cliente.get("id")
                            full_name = f"{cliente.get('nome', '')} {cliente.get('cognome', '')}".strip()
                            self.booking_sm.context.client_name = full_name
                            # FIX: Save phone number for WhatsApp confirmation
                            self.booking_sm.context.client_phone = cliente.get("telefono", "")
                            _ph = self.booking_sm.context.client_phone
                            logger.debug(f"[DEBUG] Client phone saved: ***{_ph[-3:] if len(_ph) >= 3 else '***'}")
                            display_name = cliente.get('nome', '') or full_name
                            # P0-4: Check "il solito" before building greeting
                            if _detect_solito(user_input) and not self.booking_sm.context.solito_resolved:
                                self.booking_sm.context.is_solito = True
                                solito_result = await self._lookup_solito(cliente.get("id"))
                                response, intent = self._apply_solito_to_context(solito_result, display_name)
                                if response is None:
                                    response = f"Bentornato {display_name}! Non trovo prenotazioni precedenti. Che trattamento desidera?"
                                    intent = "client_found"
                            else:
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
                            logger.debug(f"[DEBUG] Starting disambiguation (ambiguous results count={len(clienti)})")
                            disamb = self.disambiguation.start_disambiguation(
                                name_to_search,
                                clienti
                            )
                            response = disamb.response_text
                            needs_disambiguation = True
                            intent = "disambiguation_needed"
                            logger.debug(f"[DEBUG] Disambiguation response sent")

                    elif sm_result.lookup_type == "client_by_name_surname":
                        # Search by name+surname (guided flow)
                        name = sm_result.lookup_params.get("name", "")
                        surname = sm_result.lookup_params.get("surname", "")
                        # S122: Search by surname first (more unique), then filter by name
                        # The HTTP bridge can't match "Anna Bianchi" as a combined field
                        search_query = surname if surname else name
                        logger.debug(f"[DEBUG] Searching client by surname-first strategy (masked)")
                        client_result = await self._search_client(search_query)
                        clienti = client_result.get("clienti", [])

                        # S122: Filter results by name if surname search returned multiple
                        if surname and name and len(clienti) > 1:
                            name_lower = name.lower()
                            filtered = [c for c in clienti if c.get("nome", "").lower() == name_lower]
                            if filtered:
                                clienti = filtered
                                client_result["clienti"] = clienti
                                client_result["ambiguo"] = len(clienti) > 1

                        # If surname search found nothing, try name-only
                        if len(clienti) == 0 and name and surname:
                            logger.debug(f"[DEBUG] Surname search empty, trying name-only")
                            client_result = await self._search_client(name)
                            clienti = client_result.get("clienti", [])
                            # Filter by surname
                            if surname and len(clienti) > 0:
                                surname_lower = surname.lower()
                                filtered = [c for c in clienti if c.get("cognome", "").lower() == surname_lower]
                                if filtered:
                                    clienti = filtered
                                    client_result["clienti"] = clienti
                                    client_result["ambiguo"] = len(clienti) > 1
                        elif len(clienti) == 0 and name and not surname:
                            logger.debug(f"[DEBUG] No results with surname, trying name-only search")
                            client_result = await self._search_client(name)
                            clienti = client_result.get("clienti", [])

                        if len(clienti) == 0:
                            # New client — ask for phone
                            logger.debug(f"[DEBUG] No client found - new client registration")
                            self.booking_sm.context.is_new_client = True
                            self.booking_sm.context.state = BookingState.REGISTERING_PHONE
                            display = name.split()[0] if name else ""
                            response = f"Non la trovo tra i nostri clienti, {display}. Mi dà un numero di telefono per registrarla?"
                            intent = "new_client_phone"

                        elif len(clienti) == 1 and not client_result.get("ambiguo"):
                            # Unique client found
                            cliente = clienti[0]
                            _n2 = cliente.get('nome', '') or ''
                            logger.debug(f"[DEBUG] Found unique client: {_n2[:1]}*** *** (ID: {cliente.get('id')})")
                            self.booking_sm.context.client_id = cliente.get("id")
                            # FIX: Save phone number for WhatsApp confirmation
                            self.booking_sm.context.client_phone = cliente.get("telefono", "")
                            _ph2 = self.booking_sm.context.client_phone
                            logger.debug(f"[DEBUG] Client phone saved: ***{_ph2[-3:] if len(_ph2) >= 3 else '***'}")
                            display = name.split()[0] if name else cliente.get("nome", "")
                            # P0-4: Check "il solito" before building greeting
                            if _detect_solito(user_input) and not self.booking_sm.context.solito_resolved:
                                self.booking_sm.context.is_solito = True
                                solito_result = await self._lookup_solito(cliente.get("id"))
                                response, intent = self._apply_solito_to_context(solito_result, display)
                                if response is None:
                                    self.booking_sm.context.state = BookingState.WAITING_SERVICE
                                    response = f"Bentornato {display}! Non trovo prenotazioni precedenti. Che trattamento desidera?"
                                    intent = "client_found"
                            else:
                                # S126: If service already in context (from first message),
                                # skip WAITING_SERVICE and go to WAITING_DATE
                                if self.booking_sm.context.service:
                                    svc_display = self.booking_sm.context.service_display or self.booking_sm.context.service
                                    self.booking_sm.context.state = BookingState.WAITING_DATE
                                    response = f"Bentornato {display}! {svc_display}, per quale giorno?"
                                    intent = "client_found_with_service"
                                else:
                                    self.booking_sm.context.state = BookingState.WAITING_SERVICE
                                    response = TEMPLATES.get("welcome_back", "Bentornato {name}! Cosa desidera fare oggi?").format(name=display)
                                    intent = "client_found"

                        else:
                            # Ambiguous — start disambiguation
                            print(f"[DEBUG] Ambiguous results for '{search_query}', starting disambiguation")
                            disamb = self.disambiguation.start_disambiguation(
                                name, clienti
                            )
                            response = disamb.response_text
                            needs_disambiguation = True
                            intent = "disambiguation_needed"

                    elif sm_result.lookup_type == "client_by_name_only":
                        # S142: Search by first name only — smart routing
                        # 1 match → go direct to service (skip surname)
                        # 2+ matches → ask surname for disambiguation
                        # 0 matches → new client registration
                        _name_only = sm_result.lookup_params.get("name", "")
                        logger.info(f"[S142] Name-only DB lookup for '{_name_only}'")
                        client_result = await self._search_client(_name_only)
                        clienti = client_result.get("clienti", [])
                        # Filter exact name matches (case-insensitive)
                        _name_lower = _name_only.lower()
                        exact_matches = [c for c in clienti if c.get("nome", "").lower() == _name_lower]

                        if len(exact_matches) == 1:
                            # Unique match — go direct to service!
                            cliente = exact_matches[0]
                            self.booking_sm.context.client_id = cliente.get("id")
                            self.booking_sm.context.client_name = cliente.get("nome", "")
                            self.booking_sm.context.client_surname = cliente.get("cognome", "")
                            self.booking_sm.context.client_phone = cliente.get("telefono", "")
                            display = cliente.get("nome", _name_only)
                            self.booking_sm.context.state = BookingState.WAITING_SERVICE
                            response = TEMPLATES.get("welcome_back", "Bentornato {name}! Cosa desidera fare oggi?").format(name=display) + " " + TEMPLATES.get("ask_service", "Che trattamento desidera?")
                            intent = "client_found"
                            logger.info(f"[S142] Unique match: {display} → direct to service")

                        elif len(exact_matches) > 1:
                            # Multiple matches — ask surname to disambiguate
                            display = _name_only.capitalize()
                            self.booking_sm.context.state = BookingState.WAITING_SURNAME
                            response = f"Ho trovato {len(exact_matches)} clienti con il nome {display}. Mi può dire il cognome?"
                            intent = "ask_surname_disambiguate"
                            logger.info(f"[S142] {len(exact_matches)} matches for '{_name_only}' → asking surname")

                        elif len(clienti) == 1:
                            # Fuzzy single match (name slightly different)
                            cliente = clienti[0]
                            self.booking_sm.context.client_id = cliente.get("id")
                            self.booking_sm.context.client_name = cliente.get("nome", "")
                            self.booking_sm.context.client_surname = cliente.get("cognome", "")
                            self.booking_sm.context.client_phone = cliente.get("telefono", "")
                            display = cliente.get("nome", _name_only)
                            self.booking_sm.context.state = BookingState.WAITING_SERVICE
                            response = f"Bentornato {display}! Che trattamento desidera?"
                            intent = "client_found"

                        else:
                            # No matches — new client
                            display = _name_only.capitalize()
                            self.booking_sm.context.is_new_client = True
                            self.booking_sm.context.state = BookingState.REGISTERING_SURNAME
                            response = f"Non trovo {display} tra i nostri clienti. Mi dice il cognome per registrarla?"
                            intent = "new_client_surname"
                            logger.info(f"[S142] No matches for '{_name_only}' → new client registration")

                    elif sm_result.lookup_type == "availability":
                        # Check availability
                        avail = await self.availability.check_date(
                            sm_result.lookup_params.get("date", ""),
                            sm_result.lookup_params.get("service")
                        )
                        if avail.has_slots:
                            # E3: Suggest 1 best slot (fewer turns), store alternatives
                            slot_times = avail.get_slot_times()
                            if slot_times:
                                date_display = self.booking_sm.context.date_display or sm_result.lookup_params.get("date", "")
                                best_slot = slot_times[0]
                                # Store alternatives for follow-up if user declines
                                self.booking_sm.context.alternative_slots = [
                                    {"time": t} for t in slot_times[1:5]
                                ]
                                # Pre-fill time and go to CONFIRMING for faster flow
                                self.booking_sm.context.time = best_slot
                                self.booking_sm.context.time_display = f"alle {best_slot}"
                                self.booking_sm.context.state = BookingState.CONFIRMING
                                response = f"{date_display}, abbiamo posto alle {best_slot}. Confermiamo?"
                                intent = "slot_suggested"
                        elif not avail.has_slots:
                            # No slots available - offer waitlist
                            if self.booking_sm.context.client_id:
                                response = f"{avail.message} Vuole che la inserisca in lista d'attesa? La contatteremo appena si libera un posto."
                                intent = "offer_waitlist"
                                # Store flag for next turn
                                self.booking_sm.context.waiting_for_waitlist_confirm = True
                            else:
                                response = avail.message

                    elif sm_result.lookup_type == "first_available":
                        # P1-2: Flexible scheduling — find first available slot in next N days
                        service = sm_result.lookup_params.get("service")
                        days_ahead = sm_result.lookup_params.get("days_ahead", 7)
                        exclude_days = sm_result.lookup_params.get(
                            "exclude_days", self.booking_sm.context.exclude_days
                        )
                        print(f"[DEBUG] First-available lookup: service={service}, days_ahead={days_ahead}, exclude={exclude_days}")
                        first_result = await self.availability.check_first_available(
                            service=service,
                            days_ahead=days_ahead,
                            exclude_days=exclude_days,
                        ) if hasattr(self.availability, "check_first_available") else {}
                        if first_result and first_result.get("available"):
                            fa_date = first_result.get("date", "")
                            fa_time = first_result.get("time", "")
                            fa_date_display = first_result.get("date_display", fa_date)
                            self.booking_sm.context.date = fa_date
                            self.booking_sm.context.date_display = fa_date_display
                            self.booking_sm.context.time = fa_time
                            self.booking_sm.context.time_display = f"alle {fa_time}" if fa_time else ""
                            self.booking_sm.context.state = BookingState.CONFIRMING
                            response = f"Il primo slot disponibile è {fa_date_display} {self.booking_sm.context.time_display}. Confermo?"
                            intent = "first_available_found"
                        else:
                            response = "Mi dispiace, non ho trovato slot disponibili nei prossimi giorni. Posso inserirla in lista d'attesa?"
                            self.booking_sm.context.waiting_for_waitlist_confirm = True
                            intent = "first_available_none"

                    elif sm_result.lookup_type == "week_availability":
                        # Check availability for an entire week
                        week_offset = sm_result.lookup_params.get("week_offset", 1)
                        service = sm_result.lookup_params.get("service")
                        print(f"[DEBUG] Week availability check: offset={week_offset}, service={service}")
                        week_result = await self.availability.check_week(week_offset, service)
                        days = week_result.get("available_days", [])

                        if days:
                            day_list = ", ".join(d["day_name"] for d in days[:-1])
                            if len(days) > 1:
                                day_list += " e " + days[-1]["day_name"]
                            else:
                                day_list = days[0]["day_name"]
                            week_labels = {
                                0: "Questa settimana",
                                1: "La settimana prossima",
                                2: "Tra due settimane"
                            }
                            week_label = week_labels.get(week_offset, "La settimana prossima")
                            response = TEMPLATES["week_availability"].format(
                                week=week_label, days=day_list
                            )
                        else:
                            week_labels_no = {
                                0: "questa settimana",
                                1: "la settimana prossima",
                                2: "tra due settimane"
                            }
                            week_label = week_labels_no.get(week_offset, "la settimana prossima")
                            response = TEMPLATES["week_no_availability"].format(week=week_label)
                        intent = "week_availability"

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
                        _cd_safe = {k: (str(v)[:1] + "***" if k in ("nome", "cognome") else "***" + str(v)[-3:] if k == "telefono" else v) for k, v in client_data.items()}
                        logger.debug(f"[DEBUG] Creating new client: {_cd_safe}")
                        create_result = await self._create_client(client_data)
                        if create_result.get("success"):
                            # Store client ID in booking context
                            self.booking_sm.context.client_id = create_result.get("id")
                            print(f"[DEBUG] Client created with ID: {create_result.get('id')}")
                            intent = "client_created"
                        else:
                            print(f"[DEBUG] Client creation failed: {create_result.get('error')}")

                    elif sm_result.lookup_type == "solito":
                        # P0-4: "Il solito" — query last bookings for this client
                        client_id = sm_result.lookup_params.get("client_id")
                        solito_result = await self._lookup_solito(client_id)
                        response, _ = self._apply_solito_to_context(solito_result)
                        if response is None:
                            response = "Non ho trovato appuntamenti precedenti. Che servizio desidera?"

                    elif sm_result.lookup_type == "operator":
                        # Search for operators
                        print(f"[DEBUG] Searching operators")
                        operators_result = await self._search_operators()
                        operators = operators_result.get("operatori", [])
                        if operators:
                            # GAP-P1-4: Filter by gender preference if expressed
                            gender_pref = self.booking_sm.context.operator_gender_preference
                            if gender_pref:
                                filtered = [
                                    op for op in operators
                                    if op.get("genere") == gender_pref
                                ]
                                if filtered:
                                    operators = filtered
                                    print(f"[DEBUG] Filtered to {len(operators)} operators by gender={gender_pref}")
                                else:
                                    print(f"[DEBUG] No operators match gender={gender_pref}, using all {len(operators)}")
                            # Store operator info if only one, or ask for preference
                            print(f"[DEBUG] Found {len(operators)} operators")
                            if len(operators) == 1:
                                self.booking_sm.context.operator_id = operators[0].get("id")
                                self.booking_sm.context.operator_name = operators[0].get("nome")

        # =====================================================================
        # LAYER 2.5: Appointment Management (Cancel/Reschedule)
        # =====================================================================

        # S118: Handle rebook-after-cancel proposal response
        if self._pending_rebook_after_cancel and response is None:
            response, intent, layer = await self._handle_rebook_after_cancel(user_input)

        # E4-S1: Handle pending cancel flow
        if self._pending_cancel and response is None:
            response, intent, layer = await self._handle_cancel_flow(user_input)

        # E4-S2: Handle pending reschedule flow
        if self._pending_reschedule and response is None:
            response, intent, layer = await self._handle_reschedule_flow(user_input)

        # Check for new cancel/reschedule intents
        if response is None:
            if _llm_nlu_result and _llm_nlu_result.confidence >= 0.5 and HAS_NLU_SCHEMAS:
                intent_result = _nlu_to_intent_result(_llm_nlu_result, user_input)
            else:
                intent_result = get_cached_intent(user_input)  # regex fallback

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
            if _llm_nlu_result and _llm_nlu_result.confidence >= 0.5 and HAS_NLU_SCHEMAS:
                intent_result = _nlu_to_intent_result(_llm_nlu_result, user_input)
            else:
                intent_result = get_cached_intent(user_input)  # regex fallback

            if intent_result.category == IntentCategory.INFO and self.faq_manager:
                faq_result = self.faq_manager.find_answer(user_input)
                if faq_result:
                    response = faq_result.answer
                    intent = f"faq_{faq_result.source}"
                    layer = ProcessingLayer.L3_FAQ
                    # P1-7: FAQ mid-booking resume — resume booking after answering
                    if booking_in_progress:
                        _missing = self.booking_sm.context.get_missing_fields() if hasattr(self.booking_sm.context, 'get_missing_fields') else []
                        if _missing:
                            try:
                                _next_q = self.booking_sm._get_state_response(self.booking_sm.context.state)
                            except Exception:
                                _next_q = None
                            if _next_q:
                                response = f"{response} {_next_q}"
                                intent = f"faq_mid_booking_{faq_result.source}"

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

            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"[GUIDED] Error: {e}", )
                self._guided_context = None

        # =====================================================================
        # LAYER 4: Groq LLM (Fallback) — World-class: parallel TTS + fast model
        # Gap: no PMI competitor starts TTS while LLM still generating (1330ms→<800ms)
        # =====================================================================
        _l4_tts_tasks: List[asyncio.Task] = []  # parallel TTS tasks, awaited in order
        if response is None:
            t_llm_start = time.perf_counter()
            try:
                # Build context for LLM
                context = self._build_llm_context()

                # D2: Build conversation history (last 3 turns) for context
                l4_messages = []
                if self._current_session and self._current_session.turns:
                    for turn in self._current_session.turns[-3:]:
                        l4_messages.append({"role": "user", "content": turn.user_input})
                        l4_messages.append({"role": "assistant", "content": turn.response})
                l4_messages.append({"role": "user", "content": user_input})

                chunks = []
                # World-class: llama-3.1-8b-instant 2x faster for short voice responses
                async for chunk in self.groq.generate_response_streaming(
                    messages=l4_messages,
                    system_prompt=context,
                    max_tokens=150,
                    temperature=0.3,
                    model=LLM_FAST_MODEL,
                ):
                    part = chunk["text"]
                    chunks.append(part)
                    # World-class: start TTS synthesis immediately on each chunk
                    # TTS for chunk N overlaps with LLM generating chunk N+1
                    if part.strip():
                        _l4_tts_tasks.append(
                            asyncio.create_task(self.tts.synthesize(part))
                        )
                response = " ".join(chunks).strip() if chunks else None
                if not response:
                    response = FALLBACK_RESPONSES["generic"]
                else:
                    # D1: Anti-hallucination guardrail — validate before returning
                    _sanitized = self._validate_l4_response(response)
                    if _sanitized:
                        print(f"[D1-GUARDRAIL] Replaced hallucinated response")
                        response = _sanitized
                        # Cancel pre-started TTS tasks (response changed)
                        for _t in _l4_tts_tasks:
                            _t.cancel()
                        _l4_tts_tasks.clear()
                intent = "groq_response"
                layer = ProcessingLayer.L4_GROQ
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError as e:
                print(f"[Groq] Timeout LLM: {e}")
                # P1-4: Progressive fallback — try FAQ before generic error
                _faq_fb = self.faq_manager.find_answer(user_input) if self.faq_manager else None
                if _faq_fb:
                    response = _faq_fb.answer
                    intent = "l4_timeout_faq_fallback"
                    layer = ProcessingLayer.L3_FAQ
                else:
                    response = FALLBACK_RESPONSES["timeout"]
                    intent = "error_fallback"
                    layer = ProcessingLayer.L4_GROQ
            except RuntimeError as e:
                # RuntimeError da groq_client.py (include rate limit + generico)
                err_str = str(e).lower()
                if "rate" in err_str or "429" in err_str or "503" in err_str:
                    print(f"[Groq] Rate limit: {e}")
                    # P1-4: Try FAQ before rate-limit message
                    _faq_fb = self.faq_manager.find_answer(user_input) if self.faq_manager else None
                    if _faq_fb:
                        response = _faq_fb.answer
                        intent = "l4_ratelimit_faq_fallback"
                        layer = ProcessingLayer.L3_FAQ
                    else:
                        response = FALLBACK_RESPONSES["rate_limit"]
                        intent = "error_fallback"
                        layer = ProcessingLayer.L4_GROQ
                elif "timeout" in err_str:
                    print(f"[Groq] Timeout: {e}")
                    response = FALLBACK_RESPONSES["timeout"]
                    intent = "error_fallback"
                    layer = ProcessingLayer.L4_GROQ
                else:
                    print(f"[Groq] LLM error: {e}")
                    # P1-4: Try FAQ before generic error
                    _faq_fb = self.faq_manager.find_answer(user_input) if self.faq_manager else None
                    if _faq_fb:
                        response = _faq_fb.answer
                        intent = "l4_error_faq_fallback"
                        layer = ProcessingLayer.L3_FAQ
                    else:
                        response = FALLBACK_RESPONSES["error"]
                        intent = "error_fallback"
                        layer = ProcessingLayer.L4_GROQ
            except Exception as e:
                print(f"[Groq] Unexpected error: {e}")
                # P1-4: Try FAQ before generic error
                _faq_fb = self.faq_manager.find_answer(user_input) if self.faq_manager else None
                if _faq_fb:
                    response = _faq_fb.answer
                    intent = "l4_unexpected_faq_fallback"
                    layer = ProcessingLayer.L3_FAQ
                else:
                    response = FALLBACK_RESPONSES["error"]
                    intent = "error_fallback"
                    layer = ProcessingLayer.L4_GROQ
            finally:
                _t_llm_ms = (time.perf_counter() - t_llm_start) * 1000
                print(f"[F03] L4 LLM: {_t_llm_ms:.0f}ms")

        # =====================================================================
        # POST-PROCESSING
        # =====================================================================

        # F03: Log total per-turn latency
        _total_ms = (time.perf_counter() - _t0) * 1000
        print(f"[F03] Total: {_total_ms:.0f}ms | Layer: {layer.value if hasattr(layer, 'value') else layer}")

        # B4: Backchannel injection — prepend acknowledgment before main response
        _fsm_state_val = self.booking_sm.context.state.value if self.booking_sm.context.state else "idle"
        if self.backchannel and response:
            _is_first = (self._current_session and self._current_session.total_turns == 0)
            _sentiment_label = "neutral"
            if self.sentiment:
                try:
                    _sr = self.sentiment.analyze(user_input)
                    _sentiment_label = getattr(_sr, 'label', 'neutral') or 'neutral'
                except Exception:
                    pass
            if self.backchannel.should_backchannel(
                user_input=user_input,
                intent=intent,
                fsm_state=_fsm_state_val,
                sentiment=_sentiment_label,
                is_first_turn=bool(_is_first),
            ):
                _bc_context = self.backchannel.classify_context(_fsm_state_val, user_input)
                _bc_phrase = self.backchannel.get_backchannel(_bc_context, response=response)
                if _bc_phrase:
                    response = f"{_bc_phrase}. {response}"
            self.backchannel.tick()

        # B5: Tone adaptation — modify response text based on caller sentiment
        if self.tone_adapter and response and not should_escalate:
            response = self.tone_adapter.adapt_response(response)

        # Store last response for "repeat" command
        self._last_response = response

        # Log turn to session (GAP-D3: include FSM state for conversation analytics)
        latency = (time.time() - start_time) * 1000
        _fsm_state = self.booking_sm.context.state.value if self.booking_sm.context.state else None
        self.session_manager.add_turn(
            session_id=self._current_session.session_id,
            user_input=user_input,
            intent=intent,
            response=response,
            latency_ms=latency,
            layer_used=layer.value,
            fsm_state=_fsm_state
        )

        # B6: Prosody injection — natural speech patterns for TTS
        _prosody_ctx = 'default'
        if intent == 'greeting':
            _prosody_ctx = 'greeting'
        elif intent in ('domanda', 'question') or (response and response.rstrip().endswith('?')):
            _prosody_ctx = 'question'
        elif layer == ProcessingLayer.L2_SLOT and _fsm_state in ('confirming', 'confirming_waitlist', 'registering_confirm'):
            _prosody_ctx = 'confirmation'
        elif layer == ProcessingLayer.L3_FAQ or intent in ('INFO', 'info', 'faq'):
            _prosody_ctx = 'info'
        elif should_exit:
            _prosody_ctx = 'goodbye'
        _prosody_response = self.prosody.inject(response, context=_prosody_ctx) if response else response

        # Synthesize audio
        # World-class: if L4 parallel TTS tasks exist, await + concat (already running)
        # otherwise synthesize full response (L0-L3, already fast paths)
        if _l4_tts_tasks:
            try:
                t_tts_start = time.perf_counter()
                audio_chunks = await asyncio.gather(*_l4_tts_tasks)
                audio = _concat_wav_chunks(list(audio_chunks))
                if not audio:
                    audio = await self.tts.synthesize(_prosody_response)
                _tts_parallel_ms = (time.perf_counter() - t_tts_start) * 1000
                print(f"[F03] TTS parallel ({len(_l4_tts_tasks)} chunks): {_tts_parallel_ms:.0f}ms")
            except Exception as _tts_err:
                print(f"[F03] TTS parallel failed ({_tts_err}), fallback to sequential")
                audio = await self.tts.synthesize(_prosody_response)
        else:
            audio = await self.tts.synthesize(_prosody_response)

        # Handle escalation (also ends the call)
        if should_escalate:
            should_exit = True
            # A5: Generate call summary before closing session
            _session_obj = self.session_manager.get_session(self._current_session.session_id)
            if _session_obj:
                _summary = await self._generate_call_summary(_session_obj.turns, outcome="escalated")
                _session_obj.summary = _summary
            # AUDIT: Log session end with escalation
            audit_client.log_session_end(
                session_id=self._current_session.session_id,
                outcome="escalated",
                turns_count=self._current_session.total_turns,
                escalation_reason=intent
            )
            self.session_manager.close_session(
                self._current_session.session_id,
                "escalated",
                escalation_reason=intent
            )

        # Handle call end (booking completed/cancelled)
        if should_exit and not should_escalate:
            # Safety net: send WA if not already sent (e.g. if booking was created
            # in a previous turn and fire-and-forget somehow did not trigger).
            if (self._last_booking_data and not self._whatsapp_sent):
                print("[DEBUG] Safety-net: sending WhatsApp confirmation at call close")
                await self._send_wa_booking_confirmation(self._last_booking_data)
                self._whatsapp_sent = True

            # A5: Generate call summary before closing session
            _session_obj = self.session_manager.get_session(self._current_session.session_id)
            if _session_obj:
                _summary = await self._generate_call_summary(_session_obj.turns, outcome="completed")
                _session_obj.summary = _summary

            # AUDIT: Log session end
            audit_client.log_session_end(
                session_id=self._current_session.session_id,
                outcome="completed",
                turns_count=self._current_session.total_turns
            )
            self.session_manager.close_session(
                self._current_session.session_id,
                "completed"
            )

        # Clean up any unconsumed LLM NLU task (e.g. early-exit paths)
        if _llm_nlu_task and not _llm_nlu_task.done():
            _llm_nlu_task.cancel()

        # P1-8: Persist per-session BSM state for concurrent sessions
        if self._current_session and session_id:
            self._session_states[self._current_session.session_id] = self.booking_sm

        return OrchestratorResult(
            response=response,
            intent=intent,
            layer=layer,
            latency_ms=latency,
            audio_bytes=audio,
            session_id=self._current_session.session_id,
            booking_context=self.booking_sm.context.to_dict(),
            should_escalate=should_escalate,
            should_exit=should_exit,
            needs_disambiguation=needs_disambiguation
        )

    async def end_session(self, outcome: str = "completed") -> bool:
        """End current session."""
        if self._current_session:
            _sid = self._current_session.session_id
            # A5: Generate call summary before closing
            _session_obj = self.session_manager.get_session(_sid)
            if _session_obj and not _session_obj.summary:
                try:
                    _session_obj.summary = await self._generate_call_summary(
                        _session_obj.turns, outcome=outcome
                    )
                except Exception:
                    pass  # Summary is best-effort

            # C1/C3: Record call in caller memory for returning caller recognition
            if self.caller_memory and self._current_session.phone_number:
                try:
                    ctx = self.booking_sm.context
                    # Extract day_of_week from date (e.g. "2026-04-10" → "giovedi")
                    _day = ""
                    if ctx.date:
                        try:
                            import locale
                            _dt = datetime.strptime(ctx.date, "%Y-%m-%d")
                            _days_it = ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"]
                            _day = _days_it[_dt.weekday()]
                        except Exception:
                            pass
                    self.caller_memory.record_call(
                        phone_number=self._current_session.phone_number,
                        client_name=ctx.client_name or "",
                        service=ctx.service or "",
                        operator=ctx.operator_name or "",
                        day_of_week=_day,
                        time_slot=ctx.time or "",
                    )
                    logger.info(f"[C1] Caller memory recorded for {self._current_session.phone_number}")
                except Exception as e:
                    logger.warning(f"[C1] Caller memory record failed (non-critical): {e}")

            # P1-8: Remove ended session from per-session BSM cache
            self._session_states.pop(_sid, None)
            return self.session_manager.close_session(_sid, outcome)
        # P1-8: Cleanup expired sessions from BSM cache (older entries pruned lazily)
        if len(self._session_states) > 50:
            # Keep only the 20 most recently used (dict preserves insertion order in Python 3.7+)
            _keys = list(self._session_states.keys())
            for _k in _keys[:-20]:
                self._session_states.pop(_k, None)
        return False

    # =========================================================================
    # A5: Auto-summary post-call via Groq LLM
    # =========================================================================

    async def _generate_call_summary(self, turns, outcome: str = "completed") -> str:
        """
        Generate a concise Italian summary of the call via Groq LLM.

        Args:
            turns: List of turn objects with .user_input and .response attributes
            outcome: Session outcome string (completed, escalated, etc.)

        Returns:
            Summary string, max 200 chars. Falls back to template on Groq failure.
        """
        n_turns = len(turns)

        # Empty or trivial conversations: template only, skip Groq
        if n_turns == 0:
            return f"Chiamata di 0 turni, esito: {outcome}"

        # Build conversation transcript for LLM (max ~800 chars to stay fast)
        transcript_lines = []
        for t in turns:
            u = getattr(t, 'user_input', '') or ''
            r = getattr(t, 'response', '') or ''
            if u:
                transcript_lines.append(f"Cliente: {u}")
            if r:
                transcript_lines.append(f"Sara: {r}")
        transcript = "\n".join(transcript_lines)
        # Truncate to keep prompt small for fast model
        if len(transcript) > 800:
            transcript = transcript[:800] + "..."

        # If Groq client has no API key (offline mode), use template
        if not getattr(self.groq, 'client', None):
            return f"Chiamata di {n_turns} turni, esito: {outcome}"

        try:
            summary = await self.groq.generate_response(
                messages=[{"role": "user", "content": transcript}],
                system_prompt=(
                    "Riassumi questa conversazione telefonica in 1-2 frasi. "
                    "Solo i fatti: chi ha chiamato, cosa voleva, esito. "
                    "Rispondi SOLO con il riassunto, massimo 200 caratteri."
                ),
                temperature=0.3,
                max_tokens=120,
            )
            # Enforce 200 char limit
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary
        except Exception as e:
            print(f"[A5] Summary generation failed ({e}), using template")
            return f"Chiamata di {n_turns} turni, esito: {outcome}"

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _check_special_command(self, text: str) -> Optional[Tuple[str, str]]:
        """Check for special commands (L0)."""
        text_lower = text.lower().strip()

        # Exact match
        if text_lower in SPECIAL_COMMANDS:
            return SPECIAL_COMMANDS[text_lower]

        # Partial match (whole word boundary)
        for cmd, (action, response) in SPECIAL_COMMANDS.items():
            if re.search(r'\b' + re.escape(cmd) + r'\b', text_lower):
                return (action, response)

        return None

    async def _load_business_config(self) -> Optional[Dict[str, Any]]:
        """Load business configuration from HTTP Bridge, with SQLite fallback."""
        # Try HTTP Bridge first (Tauri must be running)
        try:
            async with shared_session() as session:
                url = f"{self.http_bridge_url}/api/verticale/config"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
            pass  # Bridge offline — SQLite fallback sotto

        # Fallback: read directly from SQLite (when Tauri Bridge is offline)
        return self._load_config_from_sqlite()

    def _load_config_from_sqlite(self) -> Optional[Dict[str, Any]]:
        """Read business config directly from SQLite DB (fallback when Tauri is offline)."""
        import sqlite3
        import os

        db_path = os.environ.get("FLUXION_DB_PATH")
        if not db_path:
            home = os.path.expanduser("~")
            candidates = [
                os.path.join(home, "Library", "Application Support", "com.fluxion.desktop", "fluxion.db"),
                os.path.join(home, "Library", "Application Support", "fluxion", "fluxion.db"),
            ]
            for path in candidates:
                if os.path.exists(path):
                    db_path = path
                    break

        if not db_path or not os.path.exists(db_path):
            logger.debug("SQLite fallback: DB not found, using defaults")
            return None

        try:
            with sqlite3.connect(db_path, timeout=3) as conn:
                cursor = conn.execute(
                    "SELECT chiave, valore FROM impostazioni WHERE chiave IN (?,?,?,?,?)",
                    ("nome_attivita", "whatsapp_number", "telefono", "email", "categoria_attivita")
                )
                rows = {row[0]: row[1] for row in cursor.fetchall()}

            if rows.get("nome_attivita"):
                logger.info(f"SQLite fallback: loaded '{rows['nome_attivita']}' from {db_path}")
                return {
                    "nome_attivita": rows.get("nome_attivita", ""),
                    "whatsapp": rows.get("whatsapp_number", ""),
                    "telefono": rows.get("telefono", ""),
                    "email": rows.get("email", ""),
                    "categoria_attivita": rows.get("categoria_attivita", ""),
                }
        except sqlite3.Error as e:
            logger.warning("[CONFIG] SQLite fallback failed: %s", e)
        except Exception as e:
            logger.error("[CONFIG] Unexpected error in SQLite fallback: %s", e, exc_info=True)
        return None

    async def _load_business_context(self) -> None:
        """Load orari/servizi/operatori from SQLite for Groq system prompt (GAP-H2).

        Populates self._business_hours, self._business_services, self._business_operators.
        Non-fatal: if DB is unavailable or empty, attributes stay None and the
        system prompt omits those sections rather than crashing.
        """
        import json as _json

        db_path = self._find_db_path()
        if not db_path:
            return

        try:
            import sqlite3 as _sqlite3
            conn = _sqlite3.connect(db_path, timeout=3)
            try:
                # ── Orari ──────────────────────────────────────────────────────────
                cursor = conn.execute(
                    "SELECT chiave, valore FROM impostazioni WHERE chiave IN (?,?,?)",
                    ("orario_apertura", "orario_chiusura", "giorni_lavorativi"),
                )
                rows = {r[0]: r[1] for r in cursor.fetchall()}
                ora_ap = rows.get("orario_apertura", "09:00")
                ora_ch = rows.get("orario_chiusura", "19:00")
                giorni_raw = rows.get("giorni_lavorativi", '["lun","mar","mer","gio","ven","sab"]')
                try:
                    giorni = _json.loads(giorni_raw)
                    _GIORNI_IT = {
                        "lun": "Lun", "mar": "Mar", "mer": "Mer",
                        "gio": "Gio", "ven": "Ven", "sab": "Sab", "dom": "Dom",
                    }
                    if len(giorni) >= 2:
                        giorni_str = (
                            _GIORNI_IT.get(giorni[0], giorni[0].title())
                            + "-"
                            + _GIORNI_IT.get(giorni[-1], giorni[-1].title())
                        )
                    else:
                        giorni_str = "-".join(_GIORNI_IT.get(g, g.title()) for g in giorni)
                except Exception:
                    giorni_str = "Lun-Sab"
                self._business_hours = f"{giorni_str} {ora_ap}-{ora_ch}"
                # F19-FIX6: Store raw hours for slot alternatives
                self._business_hours_open = ora_ap
                self._business_hours_close = ora_ch

                # ── Servizi ────────────────────────────────────────────────────────
                cursor = conn.execute(
                    "SELECT nome, prezzo, durata_minuti FROM servizi WHERE attivo=1 ORDER BY ordine LIMIT 50"
                )
                servizi_rows = cursor.fetchall()
                if servizi_rows:
                    self._business_services = "\n".join(
                        f"- {r[0]}: €{r[1]:.0f} ({r[2]}min)" for r in servizi_rows
                    )
                    # S123: Build service pricing map for FAQ variable substitution
                    # S124: Alias generator — FAQ uses short keys, DB has full names
                    self._service_prices = {}
                    # Common modifiers to strip for alias generation
                    _STRIP_WORDS = {
                        "medico", "medica", "generale", "ministeriale",
                        "computerizzata", "computerizzato", "professionale",
                        "completo", "completa", "semplice", "standard",
                        "4", "ruote", "ant", "post",
                        "addominale", "dentale", "trattamento", "sostituzione",
                    }
                    for r in servizi_rows:
                        svc_name = r[0]  # e.g. "Visita Medica Generale"
                        price_str = f"{r[1]:.0f}"
                        durata_str = str(r[2])
                        # Full key (existing behavior)
                        svc_key = svc_name.lower().replace(" ", "_").replace("/", "_").replace(".", "")
                        full_key = svc_key.upper()
                        self._service_prices[f"PREZZO_{full_key}"] = price_str
                        self._service_prices[f"DURATA_{full_key}"] = durata_str
                        # Alias: strip common modifiers
                        words = svc_name.lower().replace("/", " ").replace(".", "").split()
                        short_words = [w for w in words if w not in _STRIP_WORDS]
                        if short_words and short_words != words:
                            short_key = "_".join(short_words).upper()
                            if f"PREZZO_{short_key}" not in self._service_prices:
                                self._service_prices[f"PREZZO_{short_key}"] = price_str
                                self._service_prices[f"DURATA_{short_key}"] = durata_str
                        # Alias: first word only (for 2+ word services)
                        if len(words) >= 2:
                            first_key = words[0].upper()
                            if f"PREZZO_{first_key}" not in self._service_prices:
                                self._service_prices[f"PREZZO_{first_key}"] = price_str
                                self._service_prices[f"DURATA_{first_key}"] = durata_str
                        # Alias: first + last word (for 3+ word services)
                        if len(words) >= 3:
                            fl_key = f"{words[0]}_{words[-1]}".upper()
                            if f"PREZZO_{fl_key}" not in self._service_prices:
                                self._service_prices[f"PREZZO_{fl_key}"] = price_str
                                self._service_prices[f"DURATA_{fl_key}"] = durata_str
                    self._service_prices["LISTA_SERVIZI"] = self._business_services
                    print(f"[S124] Service price aliases: {len(self._service_prices)} keys")

                    # F19-FIX1: Build dynamic services_config from DB services
                    # This REPLACES DEFAULT_SERVICES/VERTICAL_SERVICES with real DB data
                    db_services_config: Dict[str, list] = {}
                    db_service_display: Dict[str, str] = {}
                    # Get vertical synonyms as enrichment source
                    _vertical_synonyms = VERTICAL_SERVICES.get(self.verticale_id, {}) if HAS_ITALIAN_REGEX else {}

                    for row in servizi_rows:
                        svc_name = row[0]  # e.g. "Taglio Uomo", "Colore"
                        svc_key = svc_name.lower().replace(" ", "_")
                        # Start with the service name itself as primary synonym
                        synonyms = [svc_name.lower()]
                        # S122: Split on both spaces AND "/" to handle "Meches/Balayage"
                        import re as _re
                        for word in _re.split(r'[\s/]+', svc_name.lower()):
                            if word not in synonyms and len(word) >= 3:
                                synonyms.append(word)
                        # Enrich with vertical synonyms if a matching key exists
                        for vk, vs in _vertical_synonyms.items():
                            if vk == svc_key or svc_name.lower() in vs or any(
                                s in svc_name.lower() for s in vs[:3]
                            ):
                                for syn in vs:
                                    if syn.lower() not in synonyms:
                                        synonyms.append(syn.lower())
                                break
                        db_services_config[svc_key] = synonyms
                        db_service_display[svc_key] = svc_name

                    # Update FSM with DB-grounded services
                    self.booking_sm.services_config = db_services_config
                    self.booking_sm.service_display_map = db_service_display
                    print(f"[F19] Loaded {len(db_services_config)} services from DB: {list(db_services_config.keys())}")

                # ── Operatori ──────────────────────────────────────────────────────
                cursor = conn.execute(
                    "SELECT id, nome, cognome, specializzazioni, descrizione_positiva "
                    "FROM operatori WHERE attivo=1 LIMIT 20"
                )
                op_rows = cursor.fetchall()
                if op_rows:
                    lines = []
                    op_list = []
                    for r in op_rows:
                        nome = f"{r[1]} {r[2] or ''}".strip()
                        desc = r[4] or ""
                        if not desc and r[3]:
                            try:
                                specs = _json.loads(r[3])
                                if specs:
                                    desc = ", ".join(specs[:3])
                            except Exception:
                                pass
                        lines.append(f"- {nome}" + (f": {desc}" if desc else ""))
                        op_list.append({"id": r[0], "nome": r[1], "cognome": r[2] or ""})
                    self._business_operators = "\n".join(lines)
                    # F19-FIX2: Cache valid operator names for entity validation
                    self._cache_valid_operators(op_list)
                    # F19: Pass valid operators to FSM for entity extraction validation
                    self.booking_sm._valid_operator_names = self._valid_operator_names

                # ── Festività (GAP-P0-3) ───────────────────────────────────────────
                cursor = conn.execute(
                    "SELECT valore FROM impostazioni WHERE chiave='giorni_festivi'"
                )
                row = cursor.fetchone()
                if row and row[0]:
                    try:
                        holidays = _json.loads(row[0])
                    except (ValueError, TypeError):
                        holidays = [d.strip() for d in row[0].split(',') if d.strip()]
                else:
                    # Default: festività nazionali italiane per l'anno corrente
                    from datetime import datetime as _dt
                    _year = _dt.now().year
                    holidays = [
                        f"{_year}-01-01",  # Capodanno
                        f"{_year}-01-06",  # Epifania
                        f"{_year}-04-25",  # Liberazione
                        f"{_year}-05-01",  # Festa del Lavoro
                        f"{_year}-06-02",  # Repubblica
                        f"{_year}-08-15",  # Ferragosto
                        f"{_year}-11-01",  # Ognissanti
                        f"{_year}-12-08",  # Immacolata
                        f"{_year}-12-25",  # Natale
                        f"{_year}-12-26",  # Santo Stefano
                    ]
                self._holidays = holidays
                # Propagate to availability checker so check_date() honours them
                if self.availability:
                    self.availability.config.holidays = holidays
            finally:
                conn.close()
        except Exception as e:
            logger.warning("[CONFIG] Failed to load business context for LLM: %s", e)

    def _extract_vertical_key(self, verticale_id: str) -> str:
        """
        Extract vertical key from verticale_id string.

        Handles both new macro taxonomy (hair/beauty/wellness/medico/auto/professionale)
        and legacy keys (salone/palestra/medical) for backward compatibility.

        Examples:
            "hair" -> "hair"
            "hair_salone_bella" -> "hair"
            "beauty_centro_rosa" -> "beauty"
            "wellness_gym_fit" -> "wellness"
            "medico_studio_rossi" -> "medico"
            "professionale_studio_bianchi" -> "professionale"
            "salone_bella_vita" -> "salone"  (legacy)
            "medical_studio_rossi" -> "medical"  (legacy)
            "auto_officina_mario" -> "auto"
        """
        # New macro keys (setup.ts taxonomy) — check first for priority
        NEW_VERTICALS = ["hair", "beauty", "wellness", "medico", "professionale"]
        # Legacy keys (backward compat with existing businesses)
        LEGACY_VERTICALS = ["salone", "palestra", "medical", "auto", "altro"]

        verticale_lower = verticale_id.lower().strip()

        # Exact match check (covers simple keys like "hair", "auto", etc.)
        all_keys = NEW_VERTICALS + LEGACY_VERTICALS
        if verticale_lower in all_keys:
            return verticale_lower

        # Prefix match for composed IDs like "hair_salone_bella_vita"
        for v in NEW_VERTICALS + LEGACY_VERTICALS:
            if verticale_lower.startswith(v + "_") or verticale_lower.startswith(v + "-"):
                return v

        # Legacy: startswith without separator (old behavior)
        for v in NEW_VERTICALS + LEGACY_VERTICALS:
            if verticale_lower.startswith(v):
                return v

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
                "ORARI_APERTURA": self._business_hours or config.get("orari_formattati", "Lun-Ven 9-18"),
                "METODI_PAGAMENTO": config.get("metodi_pagamento", "contanti, carte"),
            })
        # Enrich with service pricing from loaded business context (servizi table)
        if hasattr(self, '_service_prices'):
            settings.update(self._service_prices)

        try:
            faqs = load_faqs_for_vertical(self._faq_vertical, settings)
            loaded = 0
            skipped_vars = []
            if faqs:
                for faq in faqs:
                    answer = faq.get("answer", "")
                    # D3: Skip FAQs with unresolved variables after substitution
                    unresolved = re.findall(r'\[([A-Z][A-Z0-9_]+)\]', answer)
                    if unresolved:
                        skipped_vars.extend(unresolved)
                        continue
                    self.faq_manager.add_faq(
                        question=faq.get("question", ""),
                        answer=answer,
                        category=faq.get("category", ""),
                        faq_id=faq.get("id", "")
                    )
                    loaded += 1
            if skipped_vars:
                unique_vars = sorted(set(skipped_vars))
                print(f"[FAQ-D3] Skipped {len(skipped_vars)} FAQs with unresolved vars: {unique_vars}")
            print(f"[FAQ] Loaded {loaded}/{len(faqs)} FAQs for vertical '{self._faq_vertical}'")
            return loaded
        except sqlite3.Error as e:
            print(f"[FAQ] SQLite error loading FAQs: {e}")
            return 0
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[FAQ] Bridge error loading FAQs: {e}")
            return 0
        except Exception as e:
            print(f"[FAQ] Unexpected error loading FAQs: {e}")
            return 0

    def set_vertical(self, vertical: str) -> bool:
        """
        Change business vertical at runtime (for testing).
        Reloads FAQs and updates FSM context.

        Args:
            vertical: One of salone, palestra, wellness, medical, auto, altro

        Returns:
            True if changed successfully
        """
        VALID = {"salone", "palestra", "wellness", "medical", "medico", "auto", "altro",
                 "hair", "beauty", "professionale", "pet", "formazione",
                 # S126: Sub-vertical IDs (micro_categoria values)
                 "barbiere", "odontoiatra", "fisioterapia", "gommista",
                 "toelettatura", "veterinario", "estetista_viso", "estetista_corpo",
                 "nail_specialist", "personal_trainer", "yoga_pilates"}
        if vertical not in VALID:
            print(f"[VERTICAL] Unknown vertical '{vertical}', ignoring")
            return False

        self._faq_vertical = vertical
        self._vertical_explicitly_set = True  # S135: prevent start_session() from overriding
        self.verticale_id = vertical
        self.booking_sm.context.vertical = vertical
        # Re-pass services config so FSM uses the correct vertical's synonym list
        if HAS_ITALIAN_REGEX:
            self.booking_sm.services_config = VERTICAL_SERVICES.get(vertical, {})

        # S123: Reload business context from DB (services, operators, hours)
        # This also repopulates _service_prices for FAQ variable substitution
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._load_business_context())
            else:
                loop.run_until_complete(self._load_business_context())
        except Exception as e:
            print(f"[VERTICAL] Warning: could not reload business context: {e}")

        # Reload FAQs with fresh config (needs _service_prices from business context)
        if self.faq_manager and HAS_VERTICAL_LOADER:
            self.faq_manager.faqs = []
            db_config = self._load_config_from_sqlite()
            self._load_vertical_faqs(db_config)

        print(f"[VERTICAL] Switched to '{vertical}'")
        return True

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

    # S135: Sector personality for system prompt
    _SECTOR_PERSONALITY = {
        "salone": {
            "register": "Tu (dopo il primo turno), Lei solo se il cliente lo usa",
            "energy": "Frizzante, gioiosa. Fai sentire speciali",
            "flavor": "Sei l'amica stilista — complimenta, crea attesa, entusiasma",
            "examples": '"Vedrai che risultato!", "Ottima scelta!", "Uscirai benissimo!"',
        },
        "auto": {
            "register": "Tu/Lei flessibile, il settore è informale",
            "energy": "Rassicurante, pratica, diretta. Zero ansia",
            "flavor": "Sei l'amica che 'conosce i ragazzi dell'officina' — tranquillizza",
            "examples": '"Ci pensiamo noi!", "Stia tranquillo!", "I nostri ragazzi sono dei maghi!"',
        },
        "medical": {
            "register": "Lei (sempre). Professionale ma calda",
            "energy": "Calma, precisa, rassicurante. Mai allarmante",
            "flavor": "Segretaria di alto livello — efficiente con un sorriso nella voce",
            "examples": '"È in ottime mani.", "Non si preoccupi.", "Togliamo il pensiero subito."',
        },
        "palestra": {
            "register": "Tu (sempre). Il fitness è informale",
            "energy": "Energica, motivante, sportiva",
            "flavor": "Coach entusiasta — motiva, celebra ogni passo",
            "examples": '"Grande!", "Si fa sul serio!", "Bravo, il primo passo è il più importante!"',
        },
        "beauty": {
            "register": "Tu/Lei ibrido. Elegante",
            "energy": "Calda, lusinghiera. Lusso accessibile",
            "flavor": "Amica sofisticata — 'te lo meriti, concediti questa coccola'",
            "examples": '"Ti meriti un po\' di coccole!", "Uscirai che brilli!", "Oggi ci si dedica!"',
        },
        "wellness": {
            "register": "Lei iniziale, poi Tu se il cliente rilassa",
            "energy": "Calma, accogliente, zen",
            "flavor": "Guida al benessere — tranquillità, relax, equilibrio",
            "examples": '"Si prepari a rilassarsi!", "Un regalo per sé stessi!", "Meraviglia!"',
        },
        "professionale": {
            "register": "Lei (sempre). Impeccabile",
            "energy": "Affidabile, precisa, efficiente",
            "flavor": "Segretaria impeccabile — tutto sotto controllo",
            "examples": '"Ci pensiamo noi a tutto.", "Perfetto, è in agenda.", "Non si preoccupi."',
        },
    }

    def _build_llm_context(self) -> str:
        """Build system prompt for Groq LLM — Sara's soul (S135)."""
        hours_section = f"\nORARI APERTURA:\n{self._business_hours}" if self._business_hours else ""
        services_section = f"\nSERVIZI DISPONIBILI:\n{self._business_services}" if self._business_services else ""
        operators_section = f"\nOPERATORI:\n{self._business_operators}" if self._business_operators else ""

        # S135: Sector personality
        vert = self._faq_vertical or "salone"
        # Map aliases
        vert_key = {"hair": "salone", "medico": "medical", "wellness": "palestra"}.get(vert, vert)
        sector = self._SECTOR_PERSONALITY.get(vert_key, self._SECTOR_PERSONALITY["salone"])

        return f"""Sei Sara, la receptionist di {self.business_name}.

# CHI SEI
Sara, 30 anni, italiana. Non sei un bot — sei l'anima dell'accoglienza.
Calda, frizzante, simpatica, empatica. Parli come un'amica che lavora lì e ti vuole bene.
Hai passione genuina per far sentire le persone benvenute dal primo secondo.

# SETTORE E TONO
- Registro: {sector['register']}
- Energia: {sector['energy']}
- Personalità: {sector['flavor']}
- Frasi tipiche: {sector['examples']}

# COME PARLI
- Risposte BREVI: max 2 frasi. Se basta 1, meglio.
- Micro-reazioni PRIMA dell'info: "Perfetto!", "Certo!", "Ci mancherebbe!"
- Usa "noi" per il business: "Da noi...", "Ti offriamo..."
- Chiudi con calore: "Ti aspettiamo!", "A presto!", "Buona giornata!"
- Usa il nome del cliente appena lo sai
- MAI iniziare con "Allora" — usa "Ecco,", "Guardi,", "Dunque,"
- MAI liste numerate — parla, non elencare

# FRASI TIPICHE DI SARA
"Mi dica pure!", "Ci mancherebbe!", "Un attimino...", "C'è posto!",
"Stia tranquillo/a.", "Ecco fatto!", "Perfetto, segno!"

# QUANDO NON CAPISCI
- MAI dare colpa al cliente. Dai colpa alla linea o alle tue orecchie
- 1ª volta: "Scusa, mi ripeti?"
- 2ª volta: "Perdonami, la linea non aiuta — me lo ridici?"
- 3ª volta: "Mi dispiace, ti passo un collega."

# COSA SAI FARE
1. Prenotare appuntamenti
2. Verificare disponibilità
3. Info su orari, servizi, prezzi
4. Spostare/cancellare appuntamenti
{hours_section}{services_section}{operators_section}
# CONTESTO ATTUALE
{self._get_context_summary()}

# REGOLE ASSOLUTE
- SOLO le informazioni qui sopra. Se non sai: "Verifico con lo staff."
- SEMPRE italiano. MAI dire "intelligenza artificiale" o "algoritmo" — sei una persona.
- MAI inventare prezzi, orari, disponibilità.
- Ogni risposta deve suonare naturale se letta ad alta voce.
- Numeri come parole: "quindici", "trentacinque euro", "alle dieci e mezza"
{self._get_time_pressure_note()}"""

    def _get_time_pressure_note(self) -> str:
        """Returns urgency instruction if client is in a hurry (P1-12)."""
        if getattr(self, "_time_pressure", False):
            return "\n\nURGENZA CLIENTE: Il cliente ha fretta. Rispondi in MAX 1 frase. Vai subito al punto."
        return ""

    # D1: Anti-hallucination guardrail for L4 Groq responses
    _AVAILABILITY_HALLUCINATION_PATTERNS = [
        r"c[''\u2019]è\s+posto",
        r"(?:è|e'|sono)\s+disponibil[ei]",
        r"(?:puoi|può)\s+venire\s+(?:alle|a|il|la|domani|luned|marted|mercoled|gioved|venerd|sabato)",
        r"ti\s+(?:segno|prenoto|confermo)\s+(?:per|alle|il|la)",
        r"ho\s+(?:trovato|visto)\s+(?:un\s+)?(?:posto|slot|buco)",
    ]

    def _validate_l4_response(self, response: str) -> Optional[str]:
        """Validate L4 Groq response against known DB data.

        Returns sanitized response or None if response is safe.
        Detects:
        - Price hallucination (€X not matching any known service price)
        - Availability hallucination (confirming slots without DB check)
        - Operator name hallucination (names not in DB)
        """
        if not response:
            return None

        resp_lower = response.lower()
        issues = []

        # 1. Price hallucination: detect €XX or "XX euro" not matching DB
        known_prices = set()
        if hasattr(self, '_service_prices') and self._service_prices:
            for k, v in self._service_prices.items():
                if k.startswith("PREZZO_"):
                    known_prices.add(v)

        price_matches = re.findall(r'€\s*(\d+)', response) + re.findall(r'(\d+)\s*euro', resp_lower)
        for price in price_matches:
            if known_prices and price not in known_prices:
                issues.append(f"price_{price}")
                print(f"[D1-GUARDRAIL] Price hallucination detected: €{price} not in DB {known_prices}")

        # 2. Availability hallucination: LLM confirms a slot without FSM check
        for pattern in self._AVAILABILITY_HALLUCINATION_PATTERNS:
            if re.search(pattern, resp_lower):
                issues.append("availability")
                print(f"[D1-GUARDRAIL] Availability hallucination detected: '{pattern}' in response")
                break

        # 3. Operator name hallucination: mentions a name not in valid operators
        if self._valid_operator_names:
            # Extract capitalized names from response (potential operator mentions)
            name_candidates = re.findall(r'\b([A-Z][a-z]{2,})\b', response)
            # Exclude common Italian words that look like names
            _COMMON_WORDS = {
                "Sara", "Ciao", "Buongiorno", "Buonasera", "Grazie", "Perfetto",
                "Certo", "Ecco", "Guardi", "Dunque", "Scusa", "Prenoto",
                "Confermo", "Aspetti", "Verifico", "Salve", "Prego",
            }
            for name in name_candidates:
                if name not in _COMMON_WORDS and name.lower() not in {n.lower() for n in self._valid_operator_names}:
                    # Could be client name from context — check
                    ctx = self.booking_sm.context
                    if ctx.client_name and name.lower() in ctx.client_name.lower():
                        continue
                    issues.append(f"operator_{name}")
                    print(f"[D1-GUARDRAIL] Possible operator hallucination: '{name}' not in DB operators")

        if not issues:
            return None

        # Replace hallucinated response with safe fallback
        if "availability" in issues:
            return "Per verificare la disponibilità, posso controllare subito. Che giorno e orario preferisci?"
        if any(i.startswith("price_") for i in issues):
            if self._business_services:
                return f"Ecco i nostri servizi con i prezzi:\n{self._business_services}\nQuale ti interessa?"
            return "Verifico i prezzi con lo staff e ti confermo subito."
        # Operator hallucination is lower severity — log but allow
        return None

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
        """Search for client via HTTP Bridge, with SQLite fallback."""
        try:
            async with shared_session() as session:
                url = f"{self.http_bridge_url}/api/clienti/search?q={name}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        # AUDIT: Log client view if found and not ambiguous
                        if self._current_session and result.get("clienti") and not result.get("ambiguo"):
                            for cliente in result["clienti"]:
                                audit_client.log_client_view(
                                    session_id=self._current_session.session_id,
                                    cliente_id=cliente.get("id", "unknown"),
                                    search_query=name
                                )
                        return result
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for client search: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected client search error: {e}")
        # HTTP Bridge unavailable → SQLite fallback with phonetic variants
        print(f"[DEBUG] HTTP Bridge offline, SQLite fallback search for '{name}'")
        return self._search_client_sqlite_fallback(name)

    def _search_client_sqlite_fallback(self, name: str) -> Dict[str, Any]:
        """Search clients directly in SQLite with phonetic variant support.
        Called when HTTP Bridge is offline. Searches nome/cognome/soprannome
        and expands name tokens with Italian phonetic variants.

        When input has 2+ words: last word is treated as cognome (required filter),
        remaining words are expanded with phonetic variants for nome/soprannome.
        """
        import sqlite3
        try:
            from .disambiguation_handler import PHONETIC_VARIANTS
        except ImportError:
            from disambiguation_handler import PHONETIC_VARIANTS

        db_path = self._find_db_path()
        if not db_path:
            print("[DEBUG] SQLite DB not found for client search fallback")
            return {"clienti": [], "ambiguo": False}

        tokens = name.lower().split()

        # Split: last token = surname filter (when 2+ words), rest = name variants
        if len(tokens) >= 2:
            surname_token = tokens[-1]
            name_tokens = tokens[:-1]
        else:
            surname_token = None
            name_tokens = tokens

        # Expand name tokens with phonetic variants
        name_terms = set(name_tokens)
        for token in name_tokens:
            name_terms.update(PHONETIC_VARIANTS.get(token, []))

        # Build nome/soprannome conditions
        name_conditions = []
        params: list = []
        for term in name_terms:
            pattern = f"%{term}%"
            name_conditions.append("(LOWER(nome) LIKE ? OR LOWER(soprannome) LIKE ?)")
            params.extend([pattern, pattern])

        if not name_conditions:
            return {"clienti": [], "ambiguo": False}

        name_clause = " OR ".join(name_conditions)

        # When surname provided: require cognome LIKE %surname% (reduces false positives)
        if surname_token:
            surname_pattern = f"%{surname_token}%"
            where_clause = f"LOWER(cognome) LIKE ? AND ({name_clause})"
            params = [surname_pattern] + params
        else:
            where_clause = name_clause

        query = f"""
            SELECT id, nome, cognome, telefono, email, soprannome, data_nascita
            FROM clienti
            WHERE deleted_at IS NULL AND ({where_clause})
            ORDER BY cognome ASC, nome ASC
            LIMIT 10
        """

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

            clienti = [
                {
                    "id": r[0], "nome": r[1], "cognome": r[2],
                    "telefono": r[3], "email": r[4],
                    "soprannome": r[5], "data_nascita": r[6],
                }
                for r in rows
            ]
            print(f"[DEBUG] SQLite search '{name}' (name_terms: {name_terms}, surname: {surname_token}): {len(clienti)} results")
            return {"clienti": clienti, "ambiguo": len(clienti) > 1}
        except sqlite3.Error as e:
            print(f"[ERROR] SQLite client search fallback: {e}")
            return {"clienti": [], "ambiguo": False}
        except Exception as e:
            print(f"[ERROR] Unexpected error in SQLite client search: {e}")
            return {"clienti": [], "ambiguo": False}

    async def _create_booking(self, booking: Dict[str, Any]) -> Dict[str, Any]:
        """Create booking via HTTP Bridge."""
        # Check if we have a client_id - required for booking
        client_id = booking.get("client_id")
        if not client_id:
            print(f"[ERROR] Cannot create booking without client_id!")
            return {"success": False, "error": "client_id is required"}

        try:
            async with shared_session() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/create"
                # Transform field names to match HTTP Bridge API
                # Use service_display for multi-service (e.g. "Taglio e Barba")
                servizio = booking.get("service_display") or booking.get("service", "")
                payload = {
                    "cliente_id": client_id,
                    "servizio": servizio,
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
                    if resp.status == 200 and result.get("success"):
                        # AUDIT: Log booking creation
                        if self._current_session:
                            audit_client.log_booking_creation(
                                session_id=self._current_session.session_id,
                                appuntamento_id=result.get("id") or result.get("booking_id", "unknown"),
                                booking_data={**payload, "client_name": booking.get("client_name")}
                            )
                        return result
                    else:
                        print(f"[ERROR] Booking creation failed: {resp.status} - {result}")
                        return {"success": False, "error": result.get("error", "Unknown error")}
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for booking creation: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected booking creation error: {e}")
        # HTTP Bridge unavailable → SQLite fallback
        print("[DEBUG] HTTP Bridge unavailable, falling back to direct SQLite write")
        return await self._create_booking_sqlite_fallback(booking)

    def _find_db_path(self) -> Optional[str]:
        """Find the Fluxion SQLite DB path."""
        import os
        db_path = os.environ.get("FLUXION_DB_PATH")
        if db_path and os.path.exists(db_path):
            return db_path
        home = os.path.expanduser("~")
        candidates = [
            os.path.join(home, "Library", "Application Support", "com.fluxion.desktop", "fluxion.db"),
            os.path.join(home, "Library", "Application Support", "fluxion", "fluxion.db"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    async def _create_booking_sqlite_fallback(self, booking: Dict[str, Any]) -> Dict[str, Any]:
        """Create booking directly in SQLite when HTTP Bridge is unavailable.
        Replicates the logic of handle_crea_appuntamento in http_bridge.rs.
        P0-3: Supports multi-service combo — creates contiguous appointments with gruppo_id.
        """
        import sqlite3
        import uuid
        from datetime import datetime, timedelta

        client_id = booking.get("client_id")
        if not client_id:
            return {"success": False, "error": "client_id required for SQLite fallback"}

        db_path = self._find_db_path()
        if not db_path:
            print("[ERROR] SQLite fallback: DB not found")
            return {"success": False, "error": "DB not found"}

        try:
            multi_services = booking.get("services")
            data = booking.get("date", "")
            ora = booking.get("time", "")
            operatore_id = booking.get("operator_id")
            now = datetime.now().isoformat()

            conn = sqlite3.connect(db_path, timeout=5)
            try:
                # P0-3: Multi-service combo — create contiguous appointments
                if multi_services and len(multi_services) > 1:
                    gruppo_id = uuid.uuid4().hex
                    booking_ids = []
                    current_start = datetime.strptime(f"{data}T{ora}:00", "%Y-%m-%dT%H:%M:%S")

                    for svc_name in multi_services:
                        cursor = conn.execute(
                            "SELECT id, durata_minuti, prezzo, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome LIKE ? LIMIT 1",
                            (f"%{svc_name}%",)
                        )
                        row = cursor.fetchone()
                        servizio_id, durata_minuti, prezzo, buffer_minuti = row if row else ("srv-default", 30, 25.0, 0)

                        slot_totale = int(durata_minuti) + int(buffer_minuti)
                        bid = uuid.uuid4().hex
                        data_ora_inizio = current_start.strftime("%Y-%m-%dT%H:%M:%S")
                        data_ora_fine = (current_start + timedelta(minutes=slot_totale)).strftime("%Y-%m-%dT%H:%M:%S")

                        conn.execute(
                            """INSERT INTO appuntamenti (
                                id, cliente_id, servizio_id, operatore_id,
                                data_ora_inizio, data_ora_fine, durata_minuti,
                                stato, prezzo, sconto_percentuale, prezzo_finale,
                                fonte_prenotazione, note, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'confermato', ?, 0, ?, 'voice', ?, ?)""",
                            (bid, client_id, servizio_id, operatore_id,
                             data_ora_inizio, data_ora_fine, int(durata_minuti),
                             float(prezzo), float(prezzo), f"gruppo:{gruppo_id}", now)
                        )
                        booking_ids.append(bid)
                        current_start = current_start + timedelta(minutes=slot_totale)

                    conn.commit()
                    print(f"[DEBUG] SQLite multi-service booking: {len(booking_ids)} appointments, gruppo={gruppo_id}")
                    return {"success": True, "id": booking_ids[0], "gruppo_id": gruppo_id,
                            "message": f"Appuntamento combo creato per {data} alle {ora} ({len(multi_services)} servizi)"}

                # Single service booking
                booking_id = uuid.uuid4().hex
                servizio_nome = booking.get("service_display") or booking.get("service", "")

                cursor = conn.execute(
                    "SELECT id, durata_minuti, prezzo, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome LIKE ? LIMIT 1",
                    (f"%{servizio_nome}%",)
                )
                row = cursor.fetchone()
                servizio_id, durata_minuti, prezzo, buffer_minuti = row if row else ("srv-default", 30, 25.0, 0)

                # Build timestamps — data_ora_fine includes buffer to block calendar
                slot_totale = int(durata_minuti) + int(buffer_minuti)
                data_ora_inizio = f"{data}T{ora}:00"
                try:
                    start = datetime.strptime(data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
                    data_ora_fine = (start + timedelta(minutes=slot_totale)).strftime("%Y-%m-%dT%H:%M:%S")
                except (ValueError, TypeError) as e:
                    logger.warning("[BOOKING] Formato data non valido '%s': %s", data_ora_inizio, e)
                    data_ora_fine = data_ora_inizio

                conn.execute(
                    """INSERT INTO appuntamenti (
                        id, cliente_id, servizio_id, operatore_id,
                        data_ora_inizio, data_ora_fine, durata_minuti,
                        stato, prezzo, sconto_percentuale, prezzo_finale,
                        fonte_prenotazione, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'confermato', ?, 0, ?, 'voice', ?)""",
                    (booking_id, client_id, servizio_id, operatore_id,
                     data_ora_inizio, data_ora_fine, int(durata_minuti),
                     float(prezzo), float(prezzo), now)
                )
                conn.commit()

                print(f"[DEBUG] SQLite fallback booking created: {booking_id} ({servizio_nome} {data} {ora})")
                return {"success": True, "id": booking_id,
                        "message": f"Appuntamento creato per {data} alle {ora}"}
            finally:
                conn.close()
        except sqlite3.Error as e:
            print(f"[ERROR] SQLite fallback booking failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"[ERROR] Unexpected error in SQLite fallback booking: {e}")
            return {"success": False, "error": str(e)}

    async def _send_wa_booking_confirmation(self, booking: Dict[str, Any]) -> None:
        """
        Send WhatsApp booking confirmation to client.
        Fire-and-forget: logs errors but never fails the booking.
        """
        if not self._wa_client:
            return

        # Diagnostic: log explicitly if WhatsApp service is not connected
        if not self._wa_client.is_connected():
            logger.warning(
                "[WA] WhatsApp non connesso — conferma NON inviata. "
                "Avviare whatsapp-service.cjs e scansionare il QR."
            )
            return

        # Prefer phone from booking dict (enriched with context), fallback to context
        phone = booking.get("client_phone") or self.booking_sm.context.client_phone
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
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            # Never fail the booking because of WA
            logger.warning("[WA] Confirmation send error (non-critical, network): %s", e)
        except Exception as e:
            logger.error("[WA] Unexpected confirmation send error: %s", e, exc_info=True)

    async def _resolve_escalation_phone(self) -> tuple:
        """
        Resolve escalation phone number with fallback chain.
        Returns (phone, source) or (None, None).
        Chain: voice_agent_config.numero_trasferimento → impostazioni.telefono_titolare
               → impostazioni.telefono_attivita → first active operator with phone.
        """
        db_path = self._find_db_path()
        if not db_path:
            return None, None
        try:
            import sqlite3 as _sq
            with _sq.connect(db_path, timeout=3) as conn:
                # 1. voice_agent_config.numero_trasferimento
                try:
                    row = conn.execute(
                        "SELECT numero_trasferimento FROM voice_agent_config LIMIT 1"
                    ).fetchone()
                    if row and row[0] and row[0].strip():
                        return row[0].strip(), "voice_agent_config"
                except Exception:
                    pass
                # 2. impostazioni: telefono_titolare or telefono_attivita
                try:
                    rows = conn.execute(
                        "SELECT chiave, valore FROM impostazioni WHERE chiave IN (?,?)",
                        ("telefono_titolare", "telefono_attivita")
                    ).fetchall()
                    for r in rows:
                        if r[1] and r[1].strip():
                            return r[1].strip(), f"impostazioni.{r[0]}"
                except Exception:
                    pass
                # 3. First active operator with phone
                try:
                    row = conn.execute(
                        "SELECT telefono, nome FROM operatori WHERE attivo=1 AND telefono IS NOT NULL AND telefono != '' LIMIT 1"
                    ).fetchone()
                    if row and row[0]:
                        return row[0].strip(), f"operatore:{row[1]}"
                except Exception:
                    pass
        except Exception as e:
            logger.warning("[ESC] DB error resolving phone: %s", e)
        return None, None

    def _build_escalation_response(self, esc_phone: str, is_bh: bool, prefix: str = "") -> str:
        """Build escalation response based on business hours and phone availability."""
        if not esc_phone:
            return prefix + "Mi dispiace, al momento non riesco a metterla in contatto con un operatore. Può riprovare più tardi."
        if is_bh:
            return (
                f"{prefix}Capisco, la metto in contatto con un operatore. "
                f"Ho inviato una notifica, la ricontatteranno a breve. "
                f"In alternativa può chiamare direttamente il {esc_phone}."
            )
        return (
            f"{prefix}Al momento siamo fuori dall'orario di apertura. "
            f"Ho lasciato un messaggio, la ricontatteranno domani mattina. "
            f"In alternativa può chiamare il {esc_phone} in orario di apertura."
        )

    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        from datetime import datetime
        now = datetime.now()
        try:
            open_h, open_m = map(int, self._business_hours_open.split(":"))
            close_h, close_m = map(int, self._business_hours_close.split(":"))
            now_mins = now.hour * 60 + now.minute
            open_mins = open_h * 60 + open_m
            close_mins = close_h * 60 + close_m
            return open_mins <= now_mins <= close_mins
        except Exception:
            return True  # fail-open: assume business hours

    async def _trigger_wa_escalation_call(self, escalation_type: str) -> str:
        """
        Trigger WhatsApp notification to operator for escalation.
        Returns the escalation phone number (for Sara to read to client as fallback).
        """
        escalation_phone, phone_source = await self._resolve_escalation_phone()
        if not escalation_phone:
            logger.warning("[WA-ESC] No escalation phone found in any source")
            return ""

        logger.info(f"[WA-ESC] Resolved escalation phone from {phone_source}")

        # Build context message
        client_name = self.booking_sm.context.client_name or "Sconosciuto"
        ctx = self.booking_sm.context
        context_parts = []
        if ctx.service_display or ctx.service:
            context_parts.append(f"Servizio: {ctx.service_display or ctx.service}")
        if ctx.date_display or ctx.date:
            context_parts.append(f"Data: {ctx.date_display or ctx.date}")
        if ctx.time_display or ctx.time:
            context_parts.append(f"Ora: {ctx.time_display or ctx.time}")
        if ctx.client_phone:
            context_parts.append(f"Tel cliente: {ctx.client_phone}")
        context_str = " | ".join(context_parts) if context_parts else "nessuna prenotazione in corso"

        is_bh = self._is_business_hours()
        urgency = "URGENTE" if is_bh else "NON URGENTE (fuori orario)"

        msg = (
            f"[{urgency}] Richiesta escalation ({escalation_type}) da: {client_name}.\n"
            f"Stato: {ctx.state.value} | {context_str}.\n"
            f"Richiamarlo al più presto."
        )

        # Try WhatsApp notification
        wa_sent = False
        if self._wa_client:
            try:
                normalized = self._wa_client.normalize_phone(escalation_phone)
                result = await self._wa_client.send_message_async(normalized, msg)
                if result.get("success"):
                    logger.info(f"[WA-ESC] Notification sent to {phone_source}")
                    wa_sent = True
                else:
                    logger.warning(f"[WA-ESC] WA failed: {result.get('error')}")
            except Exception as e:
                logger.warning("[WA-ESC] WA error: %s", e)

        if not wa_sent:
            logger.info("[WA-ESC] WA not available, phone will be read to client")

        return escalation_phone

    async def _create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new client via HTTP Bridge."""
        try:
            async with shared_session() as session:
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
                _pl_safe = {k: (str(v or "")[:1] + "***" if k in ("nome", "cognome") else "***" + str(v or "")[-3:] if k == "telefono" else v) for k, v in payload.items()}
                logger.debug(f"[DEBUG] Creating client: {_pl_safe}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    logger.debug(f"[DEBUG] Client creation result: success={result.get('success')}, id={result.get('id') or result.get('client_id')}")
                    if resp.status == 200 and result.get("success"):
                        # AUDIT: Log client creation
                        if self._current_session:
                            audit_client.log_client_creation(
                                session_id=self._current_session.session_id,
                                cliente_id=result.get("id", "unknown"),
                                cliente_data=payload
                            )
                        return result
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for client creation: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected client creation error: {e}")
        # HTTP Bridge unavailable → SQLite fallback
        print("[DEBUG] HTTP Bridge unavailable, falling back to direct SQLite for client creation")
        return await self._create_client_sqlite_fallback(client_data)

    async def _create_client_sqlite_fallback(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update client directly in SQLite when HTTP Bridge is unavailable.

        Deduplication: if a client with the same nome+cognome (case-insensitive) already
        exists, update the phone number if it changed and return the existing record —
        no duplicate is created.
        """
        import sqlite3
        import uuid
        from datetime import datetime

        db_path = self._find_db_path()
        if not db_path:
            print("[ERROR] SQLite fallback: DB not found for client creation")
            return {"success": False, "error": "DB not found"}

        try:
            now = datetime.now().isoformat()
            nome = client_data.get("nome", "")
            cognome = client_data.get("cognome") or ""
            telefono = client_data.get("telefono") or ""
            email = client_data.get("email")
            note = client_data.get("note", "Registrato via Voice Agent")

            conn = sqlite3.connect(db_path, timeout=5)
            try:
                cursor = conn.cursor()

                # Deduplication check: search by nome+cognome (case-insensitive)
                cursor.execute(
                    "SELECT id, nome, cognome, telefono FROM clienti "
                    "WHERE lower(nome)=lower(?) AND lower(cognome)=lower(?) "
                    "AND (deleted_at IS NULL OR deleted_at = '') "
                    "LIMIT 1",
                    (nome, cognome)
                )
                existing = cursor.fetchone()

                if existing:
                    existing_id, ex_nome, ex_cognome, ex_telefono = existing
                    # Update phone if a new one was provided and it differs
                    if telefono and telefono != ex_telefono:
                        cursor.execute(
                            "UPDATE clienti SET telefono=?, updated_at=? WHERE id=?",
                            (telefono, now, existing_id)
                        )
                        conn.commit()
                        print(
                            f"[DEBUG] SQLite dedup: updated phone for {ex_nome} {ex_cognome} "
                            f"({ex_telefono} -> {telefono})"
                        )
                    else:
                        print(
                            f"[DEBUG] SQLite dedup: found existing client {ex_nome} {ex_cognome} "
                            f"(id={existing_id}), no phone change"
                        )
                    return {
                        "success": True,
                        "id": existing_id,
                        "nome": ex_nome,
                        "cognome": ex_cognome,
                        "telefono": telefono or ex_telefono,
                        "updated": True,
                    }

                # No existing client — insert new record
                client_id = uuid.uuid4().hex
                cursor.execute(
                    """INSERT INTO clienti (id, nome, cognome, telefono, email, note, fonte, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, 'voice', ?)""",
                    (client_id, nome, cognome, telefono, email, note, now)
                )
                conn.commit()

                logger.debug(f"[DEBUG] SQLite fallback client created: {client_id} ({(nome or '')[:1]}*** {(cognome or '')[:1]}***)")
                return {"success": True, "id": client_id, "nome": nome, "cognome": cognome, "telefono": telefono}
            finally:
                conn.close()
        except sqlite3.Error as e:
            print(f"[ERROR] SQLite fallback client creation failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"[ERROR] Unexpected error in SQLite fallback client creation: {e}")
            return {"success": False, "error": str(e)}

    async def _check_slot_availability(
        self,
        date: str,
        time: str,
        operator_id: Optional[str] = None,
        service: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        E1-S1: Check if a specific slot is available before confirming booking.
        P0-3: Supports multi-service combo via `services` param.

        Returns:
            {
                "available": True/False,
                "alternatives": [{"time": "10:00"}, {"time": "11:00"}, ...] if not available
            }
        """
        try:
            async with shared_session() as session:
                url = f"{self.http_bridge_url}/api/appuntamenti/disponibilita"
                payload = {
                    "data": date,
                    "ora": time,
                    "operatore_id": operator_id,
                    "servizio": service
                }
                if services:
                    payload["servizi"] = services
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
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for availability check: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected availability check error: {e}")
        # HTTP Bridge unavailable — fall back to direct SQLite check
        return await self._check_slot_availability_sqlite_fallback(date, time, operator_id, service, services)

    async def _check_slot_availability_sqlite_fallback(
        self,
        date: str,
        time: str,
        operator_id: Optional[str] = None,
        service: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Check slot availability directly via SQLite when HTTP Bridge is offline.
        Checks for exact time conflicts on the same operator.
        P0-3: Supports multi-service combo (sums durations + buffers).
        """
        import sqlite3
        from datetime import datetime, timedelta

        db_path = self._find_db_path()
        if not db_path:
            print("[WARN] SQLite availability check: DB not found — fail-open")
            return {"available": True, "alternatives": []}

        try:
            with sqlite3.connect(db_path, timeout=5) as conn:
                # P0-3: Multi-service combo — sum all durations + buffers
                all_services = services or ([service] if service else [])
                durata_minuti = 0
                buffer_minuti = 0
                services_found = 0
                for svc in all_services:
                    if not svc:
                        continue
                    cur = conn.execute(
                        "SELECT durata_minuti, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome LIKE ? LIMIT 1",
                        (f"%{svc}%",)
                    )
                    row = cur.fetchone()
                    if row:
                        durata_minuti += row[0]
                        buffer_minuti += row[1]
                        services_found += 1
                if services_found == 0:
                    durata_minuti = 30  # default if no service found

                # Total slot occupancy = sum of service durations + sum of buffers
                slot_totale = int(durata_minuti) + int(buffer_minuti)

                # Build timestamps
                new_start_str = f"{date}T{time}:00"
                try:
                    new_start = datetime.strptime(new_start_str, "%Y-%m-%dT%H:%M:%S")
                    new_end = new_start + timedelta(minutes=slot_totale)
                    new_end_str = new_end.strftime("%Y-%m-%dT%H:%M:%S")
                except (ValueError, TypeError) as e:
                    logger.warning("[AVAILABILITY] Formato data non valido '%s': %s", new_start_str, e)
                    new_end_str = new_start_str

                # Check for overlapping bookings on the same operator
                if operator_id:
                    cur = conn.execute(
                        """SELECT COUNT(*) FROM appuntamenti
                           WHERE operatore_id = ?
                           AND stato NOT IN ('cancellato','no_show')
                           AND data_ora_inizio < ?
                           AND data_ora_fine > ?""",
                        (operator_id, new_end_str, new_start_str)
                    )
                else:
                    # No operator specified — check globally on same date/time
                    cur = conn.execute(
                        """SELECT COUNT(*) FROM appuntamenti
                           WHERE stato NOT IN ('cancellato','no_show')
                           AND data_ora_inizio < ?
                           AND data_ora_fine > ?""",
                        (new_end_str, new_start_str)
                    )

                count = cur.fetchone()[0]
                is_available = count == 0

                # P0-2: Check blocchi_orario (pausa pranzo, fasce bloccate operatore)
                if is_available and operator_id:
                    try:
                        slot_time_start = time[:5]  # HH:MM
                        slot_time_end = new_end.strftime("%H:%M") if isinstance(new_end, datetime) else time[:5]
                        # Parse date to get day of week (0=Mon, 6=Sun)
                        slot_date = datetime.strptime(date, "%Y-%m-%d")
                        giorno_settimana = slot_date.weekday()  # 0=Mon matches our schema

                        block_count = conn.execute(
                            """SELECT COUNT(*) FROM blocchi_orario
                               WHERE operatore_id = ?
                               AND attivo = 1
                               AND (
                                   (ricorrente = 1 AND (giorno_settimana IS NULL OR giorno_settimana = ?))
                                   OR
                                   (ricorrente = 0 AND data_specifica = ?)
                               )
                               AND ora_inizio < ?
                               AND ora_fine > ?""",
                            (operator_id, giorno_settimana, date, slot_time_end, slot_time_start)
                        ).fetchone()[0]
                        if block_count > 0:
                            is_available = False
                            print(f"[DEBUG] Slot {date} {time} blocked by blocchi_orario for operator {operator_id}")
                    except Exception as e:
                        # Table may not exist yet — fail-open
                        if "no such table" not in str(e):
                            logger.warning("[AVAILABILITY] Blocchi orario check failed: %s", e)

                # F19-FIX6: Use real business hours from DB for slot alternatives
                try:
                    _open_h = int(self._business_hours_open.split(":")[0])
                    _close_h = int(self._business_hours_close.split(":")[0])
                except (ValueError, AttributeError, IndexError):
                    _open_h, _close_h = 9, 19
                alternatives = []
                if not is_available:
                    for hour in range(_open_h, _close_h):
                        for minute in (0, 30):
                            alt_start_str = f"{date}T{hour:02d}:{minute:02d}:00"
                            alt_end = datetime.strptime(alt_start_str, "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=slot_totale)
                            alt_end_str = alt_end.strftime("%Y-%m-%dT%H:%M:%S")
                            if operator_id:
                                check = conn.execute(
                                    """SELECT COUNT(*) FROM appuntamenti
                                       WHERE operatore_id = ?
                                       AND stato NOT IN ('cancellato','no_show')
                                       AND data_ora_inizio < ?
                                       AND data_ora_fine > ?""",
                                    (operator_id, alt_end_str, alt_start_str)
                                ).fetchone()[0]
                            else:
                                check = conn.execute(
                                    """SELECT COUNT(*) FROM appuntamenti
                                       WHERE stato NOT IN ('cancellato','no_show')
                                       AND data_ora_inizio < ?
                                       AND data_ora_fine > ?""",
                                    (alt_end_str, alt_start_str)
                                ).fetchone()[0]
                            # P0-2: Also check blocchi_orario for alternative slots
                            if check == 0 and operator_id:
                                try:
                                    alt_time_end = alt_end.strftime("%H:%M")
                                    alt_time_start = f"{hour:02d}:{minute:02d}"
                                    block_check = conn.execute(
                                        """SELECT COUNT(*) FROM blocchi_orario
                                           WHERE operatore_id = ?
                                           AND attivo = 1
                                           AND (
                                               (ricorrente = 1 AND (giorno_settimana IS NULL OR giorno_settimana = ?))
                                               OR
                                               (ricorrente = 0 AND data_specifica = ?)
                                           )
                                           AND ora_inizio < ?
                                           AND ora_fine > ?""",
                                        (operator_id, giorno_settimana, date, alt_time_end, alt_time_start)
                                    ).fetchone()[0]
                                    if block_check > 0:
                                        check = 1  # mark as unavailable
                                except Exception:
                                    pass  # fail-open if table missing
                            if check == 0:
                                alternatives.append({"time": f"{hour:02d}:{minute:02d}"})
                            if len(alternatives) >= 5:
                                break
                        if len(alternatives) >= 5:
                            break

                print(f"[DEBUG] SQLite availability: slot {date} {time} operator={operator_id} → available={is_available} (conflicts={count}, durata={durata_minuti}+buffer={buffer_minuti}={slot_totale}min)")
                return {"available": is_available, "alternatives": alternatives}

        except sqlite3.Error as e:
            print(f"[ERROR] SQLite availability check failed: {e}")
            return {"available": True, "alternatives": []}
        except Exception as e:
            print(f"[ERROR] Unexpected error in SQLite availability check: {e}")
            return {"available": True, "alternatives": []}

    async def _search_operators(self) -> Dict[str, Any]:
        """Get available operators via HTTP Bridge, with SQLite fallback (F19-FIX2)."""
        try:
            async with shared_session() as session:
                url = f"{self.http_bridge_url}/api/operatori/list"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        # F19: Cache valid operator names for entity validation
                        self._cache_valid_operators(result.get("operatori", []))
                        return result
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for operators search: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected operators search error: {e}")
        # F19-FIX2: SQLite fallback
        print("[F19] HTTP Bridge offline, SQLite fallback for operators")
        return self._search_operators_sqlite_fallback()

    def _search_operators_sqlite_fallback(self) -> Dict[str, Any]:
        """F19-FIX2: Get operators directly from SQLite when HTTP Bridge is offline."""
        import sqlite3

        db_path = self._find_db_path()
        if not db_path:
            print("[F19] SQLite DB not found for operators fallback")
            return {"operatori": []}

        try:
            with sqlite3.connect(db_path, timeout=3) as conn:
                cursor = conn.execute(
                    "SELECT id, nome, cognome, specializzazioni FROM operatori WHERE attivo=1 LIMIT 20"
                )
                rows = cursor.fetchall()

            operatori = []
            for r in rows:
                op = {
                    "id": r[0],
                    "nome": r[1],
                    "cognome": r[2] or "",
                }
                if r[3]:
                    try:
                        import json as _json
                        op["specializzazioni"] = _json.loads(r[3])
                    except Exception:
                        pass
                operatori.append(op)

            # F19: Cache valid operator names for entity validation
            self._cache_valid_operators(operatori)
            print(f"[F19] SQLite operators fallback: {len(operatori)} operators found")
            return {"operatori": operatori}
        except sqlite3.Error as e:
            print(f"[ERROR] SQLite operators fallback failed: {e}")
            return {"operatori": []}

    def _cache_valid_operators(self, operatori: list) -> None:
        """F19: Cache valid operator names for entity extractor validation."""
        self._valid_operator_names = set()
        for op in operatori:
            nome = op.get("nome", "").strip().lower()
            cognome = op.get("cognome", "").strip().lower()
            if nome:
                self._valid_operator_names.add(nome)
            if cognome:
                self._valid_operator_names.add(cognome)
            if nome and cognome:
                self._valid_operator_names.add(f"{nome} {cognome}")
        print(f"[F19] Cached {len(self._valid_operator_names)} valid operator names: {self._valid_operator_names}")

    async def _build_proactive_greeting(self, session_id: str, profile) -> Optional[str]:
        """
        G5: Build proactive greeting for returning caller with booking history.

        Instead of generic "Bentornato Mario, come posso aiutarla?", Sara says:
        "Bentornato Mario! Vuole ripetere taglio con Luca? Mi dica quando preferisce."

        This pre-populates FSM context with service/operator, skipping 2-3 turns.
        Caller can say "si, martedì alle 10" (1 turn) or "no, vorrei..." (normal flow).
        """
        session = self.session_manager._sessions.get(session_id)
        if not session:
            return None

        hour = datetime.now().hour
        saluto = "Buongiorno" if hour < 12 else ("Buon pomeriggio" if hour < 18 else "Buonasera")
        name = profile.client_name

        svc = profile.last_service
        op = profile.last_operator
        svc_display = svc.capitalize() if svc else ""

        # Pre-populate FSM context so "si" flows straight to WAITING_DATE
        if svc:
            self.booking_sm.context.service = svc.lower()
            self.booking_sm.context.service_display = svc_display
            self.booking_sm.context.services = [svc.lower()]
        if op:
            self.booking_sm.context.operator_name = op
        if name:
            self.booking_sm.context.client_name = name

        # Build natural Italian greeting
        op_str = f" con {op}" if op else ""
        pref_str = ""
        if profile.preferred_day and profile.preferred_time:
            pref_str = f" Di solito il {profile.preferred_day} alle {profile.preferred_time}."

        # Set FSM to WAITING_DATE — service is pre-filled
        self.booking_sm.context.state = BookingState.WAITING_DATE
        self.booking_sm.context.proactive_offer = True

        greeting = (
            f"{session.business_name}, {saluto.lower()}! "
            f"Bentornato {name}! Vuole ripetere {svc_display}{op_str}?"
            f"{pref_str} Mi dica quando preferisce, oppure se desidera altro."
        )
        return greeting

    def _apply_solito_to_context(self, solito_result: dict, display_name: str = "") -> tuple:
        """Apply solito result to booking context. Returns (response, intent) or (None, None) if not found."""
        if not solito_result or not solito_result.get("found"):
            self.booking_sm.context.solito_resolved = True
            return None, None

        svc = solito_result["service"]
        svc_display = solito_result.get("service_display", svc.capitalize())
        op_name = solito_result.get("operator_name", "")

        self.booking_sm.context.service = svc
        self.booking_sm.context.service_display = svc_display
        self.booking_sm.context.services = [svc]
        if solito_result.get("operator_id"):
            self.booking_sm.context.operator_id = solito_result["operator_id"]
            self.booking_sm.context.operator_name = op_name
        self.booking_sm.context.solito_resolved = True

        op_str = f" con {op_name}" if op_name else ""
        day_name = solito_result.get("day_name", "")
        time_str = solito_result.get("time", "")

        msg = f"L'ultima volta ha fatto {svc_display}{op_str}"
        if day_name and time_str:
            msg += f" il {day_name} alle {time_str}"

        if display_name:
            response = f"Bentornato {display_name}! {msg}. Riprenoto lo stesso? Per quale giorno?"
        else:
            response = f"{msg}. Vuole ripetere lo stesso? Mi dica quando preferisce."
        self.booking_sm.context.state = BookingState.WAITING_DATE
        return response, "solito_found"

    async def _lookup_solito(self, client_id: str) -> Dict[str, Any]:
        """P0-4: Query last bookings for a client to resolve 'il solito'.
        Returns the most frequent service + operator + day/time pattern.
        """
        import sqlite3
        from datetime import datetime

        db_path = self._find_db_path()
        if not db_path:
            return {"found": False}

        try:
            with sqlite3.connect(db_path, timeout=5) as conn:
                # Get last 5 completed/confirmed bookings for this client
                rows = conn.execute(
                    """SELECT a.servizio_id, s.nome AS servizio_nome,
                              a.operatore_id, o.nome AS operatore_nome,
                              a.data_ora_inizio
                       FROM appuntamenti a
                       LEFT JOIN servizi s ON a.servizio_id = s.id
                       LEFT JOIN operatori o ON a.operatore_id = o.id
                       WHERE a.cliente_id = ?
                       AND a.stato IN ('completato', 'confermato')
                       ORDER BY a.data_ora_inizio DESC
                       LIMIT 5""",
                    (client_id,)
                ).fetchall()

            if not rows:
                return {"found": False}

            # Most recent booking as base
            last = rows[0]
            servizio_nome = last[1] or "servizio"
            operatore_id = last[2]
            operatore_nome = last[3] or ""

            # Try to find day/time pattern from history
            day_name = ""
            time_str = ""
            if last[4]:
                try:
                    dt = datetime.strptime(last[4][:19], "%Y-%m-%dT%H:%M:%S")
                    giorni_it = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
                    day_name = giorni_it[dt.weekday()]
                    time_str = dt.strftime("%H:%M")
                except (ValueError, IndexError):
                    pass

            print(f"[P0-4] Solito resolved: {servizio_nome} con {operatore_nome} ({day_name} {time_str})")
            return {
                "found": True,
                "service": servizio_nome.lower(),
                "service_display": servizio_nome,
                "operator_id": operatore_id,
                "operator_name": operatore_nome,
                "day_name": day_name,
                "time": time_str
            }
        except Exception as e:
            print(f"[ERROR] Solito lookup failed: {e}")
            return {"found": False}

    async def _cancel_booking(self, appointment_id: str, appointment_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Cancel an existing appointment via HTTP Bridge."""
        try:
            async with shared_session() as session:
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
                    if resp.status == 200 and result.get("success"):
                        # AUDIT: Log booking cancellation
                        if self._current_session:
                            audit_client.log_booking_cancellation(
                                session_id=self._current_session.session_id,
                                appuntamento_id=appointment_id,
                                booking_data=appointment_data or result.get("appointment_data", {})
                            )
                        # GAP-P1-7: Trigger immediate waitlist check on cancellation
                        # Fire-and-forget: does not block the cancel response
                        try:
                            from src.reminder_scheduler import check_and_notify_waitlist
                            asyncio.create_task(check_and_notify_waitlist(self._wa_client))
                        except Exception as _wl_err:
                            print(f"[DEBUG] Waitlist trigger skipped: {_wl_err}")
                    return result
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for cancel booking: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected cancel booking error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _reschedule_booking(
        self, 
        appointment_id: str, 
        new_date: str, 
        new_time: str,
        old_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Reschedule an existing appointment via HTTP Bridge."""
        try:
            async with shared_session() as session:
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
                    if resp.status == 200 and result.get("success"):
                        # AUDIT: Log booking reschedule
                        if self._current_session:
                            new_data = {
                                "data": new_date,
                                "ora": new_time,
                                "servizio": old_data.get("servizio") if old_data else None
                            }
                            audit_client.log_booking_reschedule(
                                session_id=self._current_session.session_id,
                                appuntamento_id=appointment_id,
                                old_data=old_data or {},
                                new_data=new_data
                            )
                    return result
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for reschedule booking: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected reschedule booking error: {e}")
        return {"success": False, "error": "Bridge not available"}

    async def _add_to_waitlist(self, client_id: str, service: str, preferred_date: str = None) -> Dict[str, Any]:
        """Add client to waitlist via HTTP Bridge, with SQLite fallback (F19-FIX5)."""
        # F19-FIX5: Get VIP priority from DB
        priorita = self._get_client_vip_priority(client_id)

        try:
            async with shared_session() as session:
                url = f"{self.http_bridge_url}/api/waitlist/add"
                payload = {
                    "cliente_id": client_id,
                    "servizio": service,
                    "data_preferita": preferred_date,
                    "priorita": priorita,
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
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for waitlist add: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected waitlist add error: {e}")
        # F19-FIX5: SQLite fallback
        print("[F19] HTTP Bridge offline, SQLite fallback for waitlist")
        return self._add_to_waitlist_sqlite_fallback(client_id, service, preferred_date, priorita)

    def _get_client_vip_priority(self, client_id: str) -> str:
        """F19-FIX5: Get VIP priority for client from DB."""
        import sqlite3
        db_path = self._find_db_path()
        if not db_path:
            return "normale"
        try:
            with sqlite3.connect(db_path, timeout=3) as conn:
                cursor = conn.execute(
                    "SELECT is_vip FROM clienti WHERE id = ?", (client_id,)
                )
                row = cursor.fetchone()
            if row and row[0]:
                return "vip"
        except sqlite3.Error as e:
            print(f"[F19] VIP check failed: {e}")
        return "normale"

    def _add_to_waitlist_sqlite_fallback(
        self, client_id: str, service: str, preferred_date: str, priorita: str
    ) -> Dict[str, Any]:
        """F19-FIX5: Add to waitlist directly in SQLite when HTTP Bridge is offline."""
        import sqlite3
        import uuid

        db_path = self._find_db_path()
        if not db_path:
            return {"success": False, "error": "DB not found"}

        try:
            wl_id = uuid.uuid4().hex
            priorita_valore = 50 if priorita == "vip" else 10
            with sqlite3.connect(db_path, timeout=5) as conn:
                conn.execute(
                    """INSERT INTO waitlist (id, cliente_id, servizio, data_preferita, priorita, priorita_valore, stato)
                       VALUES (?, ?, ?, ?, ?, ?, 'attesa')""",
                    (wl_id, client_id, service, preferred_date, priorita, priorita_valore)
                )
                conn.commit()
            print(f"[F19] Waitlist SQLite fallback: added {wl_id} (priorita={priorita})")
            return {"success": True, "id": wl_id}
        except sqlite3.Error as e:
            print(f"[ERROR] SQLite waitlist fallback failed: {e}")
            return {"success": False, "error": str(e)}

    async def _get_client_appointments(self, client_id: str) -> Dict[str, Any]:
        """
        E4-S1: Get upcoming appointments for a client via HTTP Bridge.

        Returns:
            {"appointments": [{id, data, ora, servizio, operatore_nome}, ...]}
        """
        try:
            async with shared_session() as session:
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
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            print(f"[HTTP] Bridge offline for get appointments: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected get appointments error: {e}")
        return {"appointments": []}

    def _get_appointment_by_id(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment data from pending appointments by ID."""
        for appt in self._pending_appointments:
            if appt.get("id") == appointment_id:
                return appt
        return None

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
                # GAP-P1-5: Cancellation window check before executing cancel
                appointment_data = self._get_appointment_by_id(self._selected_appointment_id)
                window_blocked, window_msg = self._check_cancellation_window(appointment_data)
                if window_blocked:
                    response = window_msg
                    intent = "cancel_window_blocked"
                    self._reset_cancel_reschedule_state()
                else:
                    result = await self._cancel_booking(self._selected_appointment_id, appointment_data)
                    if result.get("success"):
                        # S118: Propose rebooking after successful cancel
                        cancelled_service = appointment_data.get("servizio", "") if appointment_data else ""
                        self._pending_rebook_after_cancel = True
                        self._cancelled_service = cancelled_service
                        response = (
                            "Appuntamento cancellato con successo. "
                            "Vuole che le trovi un altro orario disponibile questa settimana?"
                        )
                        intent = "cancel_success_propose_rebook"
                        # Reset cancel state but keep rebook flag
                        self._pending_cancel = False
                        self._pending_appointments = []
                        self._selected_appointment_id = None
                        return response, intent, layer
                    else:
                        response = f"Mi dispiace, c'e stato un problema: {result.get('error', 'errore sconosciuto')}. Riprovi piu tardi."
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
            # S118: If we don't have appointments loaded yet, try to find client by name first
            if not self._pending_appointments and not self.booking_sm.context.client_id:
                # User might be giving their name — search client
                from entity_extractor import extract_name
                name_result = extract_name(user_input)
                search_name = name_result if name_result else user_input.strip()

                if search_name and len(search_name) >= 2:
                    # S118: Search by first word, then filter by full name match
                    parts = search_name.split()
                    search_term = parts[0]  # search by first name
                    client_result = await self._search_client(search_term)
                    clienti = client_result.get("clienti", [])
                    # If multiple results and we have nome+cognome, narrow down
                    if len(clienti) > 1 and len(parts) >= 2:
                        cognome = parts[-1].lower()
                        nome = parts[0].lower()
                        filtered = [c for c in clienti if
                                    c.get("nome", "").lower() == nome and
                                    c.get("cognome", "").lower() == cognome]
                        if filtered:
                            clienti = filtered
                    if len(clienti) == 1:
                        self.booking_sm.context.client_id = clienti[0].get("id")
                        self.booking_sm.context.client_name = f"{clienti[0].get('nome', '')} {clienti[0].get('cognome', '')}".strip()
                        appointments_result = await self._get_client_appointments(
                            self.booking_sm.context.client_id
                        )
                        appointments = appointments_result.get("appointments", [])
                        if len(appointments) == 0:
                            response = "Non ho trovato appuntamenti a suo nome. Posso aiutarla in altro modo?"
                            intent = "cancel_no_appointments"
                            self._reset_cancel_reschedule_state()
                        elif len(appointments) == 1:
                            appt = appointments[0]
                            self._pending_appointments = appointments
                            self._selected_appointment_id = appt.get("id")
                            response = f"Ho trovato il suo appuntamento: {appt.get('servizio', 'servizio')} il {appt.get('data', '')} alle {appt.get('ora', '')}. Conferma la cancellazione?"
                            intent = "cancel_confirm_single"
                        else:
                            self._pending_appointments = appointments
                            appt_list = "\n".join([
                                f"- {a.get('servizio', 'servizio')} il {a.get('data', '')} alle {a.get('ora', '')}"
                                for a in appointments[:5]
                            ])
                            response = f"Ho trovato questi appuntamenti:\n{appt_list}\nQuale vuole cancellare? Mi dica la data."
                            intent = "cancel_multiple"
                        return response, intent, layer
                    elif len(clienti) > 1:
                        response = "Ho trovato più clienti con quel nome. Può dirmi anche il cognome?"
                        intent = "cancel_disambiguate_name"
                        return response, intent, layer

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
                    old_appointment_data = self._get_appointment_by_id(self._selected_appointment_id)
                    result = await self._reschedule_booking(
                        self._selected_appointment_id,
                        self._reschedule_new_date,
                        self._reschedule_new_time,
                        old_data=old_appointment_data
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

    def _get_cancellation_window_hours(self) -> int:
        """
        GAP-P1-5: Legge ore_disdetta da faq_settings.
        Default 24 se non configurato o DB offline.
        """
        import sqlite3 as _sqlite3
        default = 24
        db_path = self._find_db_path()
        if not db_path:
            return default
        try:
            conn = _sqlite3.connect(db_path, timeout=3)
            try:
                row = conn.execute(
                    "SELECT valore FROM faq_settings WHERE chiave = ? LIMIT 1",
                    ("ore_disdetta",)
                ).fetchone()
            finally:
                conn.close()
            if row and row[0] is not None:
                return int(row[0])
        except (_sqlite3.Error, ValueError, TypeError) as e:
            logger.debug("[CANCEL-WINDOW] Could not read ore_disdetta: %s", e)
        return default

    def _check_cancellation_window(
        self,
        appointment_data: Optional[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        GAP-P1-5: Verifica se la cancellazione e dentro la finestra temporale.

        Args:
            appointment_data: dict con 'data' (YYYY-MM-DD) e 'ora' (HH:MM)

        Returns:
            (True, messaggio_rifiuto) se dentro la finestra — cancellazione bloccata
            (False, "") se consentita
        """
        if not appointment_data:
            return False, ""

        appt_date = appointment_data.get("data") or appointment_data.get("date", "")
        appt_time = appointment_data.get("ora") or appointment_data.get("time", "")

        if not appt_date or not appt_time:
            return False, ""

        try:
            appt_dt = datetime.strptime(f"{appt_date} {appt_time}", "%Y-%m-%d %H:%M")
            window_hours = self._get_cancellation_window_hours()
            hours_until = (appt_dt - datetime.now()).total_seconds() / 3600.0
            if hours_until < window_hours:
                msg = (
                    f"Mi dispiace, non posso cancellare l'appuntamento: "
                    f"la disdetta deve essere effettuata almeno {window_hours} ore prima. "
                    f"Per assistenza la prego di contattarci direttamente."
                )
                return True, msg
        except (ValueError, TypeError) as e:
            logger.debug("[CANCEL-WINDOW] Date parse error: %s", e)

        return False, ""

    def _reset_cancel_reschedule_state(self):
        """Reset cancel/reschedule flow state."""
        self._pending_cancel = False
        self._pending_reschedule = False
        self._pending_appointments = []
        self._selected_appointment_id = None
        self._reschedule_new_date = None
        self._reschedule_new_time = None
        self._pending_rebook_after_cancel = False
        self._cancelled_service = None

    async def _handle_rebook_after_cancel(
        self, user_input: str
    ) -> Tuple[Optional[str], str, ProcessingLayer]:
        """
        S118: Handle user response to rebook proposal after cancel.
        If user says yes, start a new booking flow for the same service.
        If no, close gracefully.
        """
        text_lower = user_input.lower()
        layer = ProcessingLayer.L2_SLOT

        affirmative = ["sì", "si", "ok", "va bene", "certo", "volentieri", "magari"]
        negative = ["no", "niente", "basta", "grazie", "non serve", "lascia", "va bene così"]

        if any(word in text_lower for word in affirmative):
            # User wants to rebook — start new booking with same service pre-filled
            service = self._cancelled_service
            self._pending_rebook_after_cancel = False
            self._cancelled_service = None

            if service and self.booking_sm.context.client_id:
                # Pre-fill the service and kick the booking SM into collecting mode
                self.booking_sm.context.service = service
                self.booking_sm.context.state = BookingState.WAITING_DATE
                response = (
                    f"Perfetto! Per quale giorno vuole spostare "
                    f"l'appuntamento di {service}?"
                )
                return response, "rebook_ask_date", layer
            else:
                # No service info — just restart generic booking
                self.booking_sm.context.state = BookingState.WAITING_SERVICE
                response = "Certo! Per quale servizio desidera prenotare?"
                return response, "rebook_ask_service", layer

        elif any(word in text_lower for word in negative):
            self._pending_rebook_after_cancel = False
            self._cancelled_service = None
            response = "Nessun problema. Posso aiutarla in altro modo?"
            return response, "rebook_declined", layer

        else:
            # Unclear — repeat the question
            response = "Mi dica sì se vuole prenotare un nuovo appuntamento, o no se ha finito."
            return response, "rebook_confirm_repeat", layer

    # ─────────────────────────────────────────────────────────────────
    # S118: Package proposal after booking
    # ─────────────────────────────────────────────────────────────────

    def _check_package_proposal(
        self, client_id: Optional[str], service: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        S118: Check if there's an active package matching the booked service
        that the client doesn't already own. Uses SQLite directly.
        """
        if not client_id:
            return None

        try:
            import os
            import sqlite3 as sql3
            # Find DB path (same logic as other SQLite fallbacks)
            home = os.path.expanduser("~")
            db_candidates = [
                os.path.join(home, "Library", "Application Support", "com.fluxion.desktop", "fluxion.db"),
                os.path.join(home, "Library", "Application Support", "fluxion", "fluxion.db"),
            ]
            db_path = None
            for p in db_candidates:
                if os.path.exists(p):
                    db_path = p
                    break
            if not db_path:
                return None

            conn = sql3.connect(db_path)
            conn.row_factory = sql3.Row

            # Get active packages (all or matching service)
            packages = conn.execute(
                """SELECT p.id, p.nome, p.prezzo, p.prezzo_originale,
                          p.servizi_inclusi, p.servizio_tipo_id, p.descrizione
                   FROM pacchetti p
                   WHERE p.attivo = 1
                   ORDER BY p.prezzo ASC""",
            ).fetchall()

            if not packages:
                conn.close()
                return None

            # Check which packages the client doesn't already have (active)
            for pkg in packages:
                existing = conn.execute(
                    """SELECT id FROM clienti_pacchetti
                       WHERE cliente_id = ? AND pacchetto_id = ?
                       AND stato IN ('venduto', 'in_uso', 'proposto')""",
                    (client_id, pkg["id"]),
                ).fetchone()

                if not existing:
                    # Client doesn't have this package — propose it
                    conn.close()
                    return {
                        "id": pkg["id"],
                        "nome": pkg["nome"],
                        "prezzo": pkg["prezzo"],
                        "prezzo_originale": pkg["prezzo_originale"] or pkg["prezzo"],
                        "servizi_inclusi": pkg["servizi_inclusi"],
                        "descrizione": pkg["descrizione"] or "",
                    }

            conn.close()
        except Exception as e:
            print(f"[S118] Package proposal check error: {e}")

        return None

    def _record_package_proposal(self, client_id: str, package_id: str) -> bool:
        """S118: Record that a package was proposed to a client."""
        try:
            import os
            import sqlite3 as sql3
            import uuid
            home = os.path.expanduser("~")
            db_candidates = [
                os.path.join(home, "Library", "Application Support", "com.fluxion.desktop", "fluxion.db"),
                os.path.join(home, "Library", "Application Support", "fluxion", "fluxion.db"),
            ]
            db_path = None
            for p in db_candidates:
                if os.path.exists(p):
                    db_path = p
                    break
            if not db_path:
                return False

            conn = sql3.connect(db_path)
            conn.execute(
                """INSERT INTO clienti_pacchetti
                   (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali)
                   VALUES (?, ?, ?, 'proposto', 0, ?)""",
                (str(uuid.uuid4()), client_id, package_id,
                 self._proposed_package.get("servizi_inclusi", 0) if self._proposed_package else 0),
            )
            conn.commit()
            conn.close()
            print(f"[S118] Package {package_id} proposed to client {client_id}")
            return True
        except Exception as e:
            print(f"[S118] Record package proposal error: {e}")
            return False

    async def _handle_package_response(
        self, user_input: str
    ) -> Tuple[Optional[str], str, ProcessingLayer]:
        """S118: Handle user response to package proposal."""
        text_lower = user_input.lower()
        layer = ProcessingLayer.L2_SLOT

        affirmative = ["sì", "si", "ok", "mi interessa", "certo", "volentieri", "quanto"]
        negative = ["no", "niente", "basta", "non serve", "non mi interessa"]
        # S122: Detect goodbye signals — close the call after handling package
        _goodbye = ["arrivederci", "a presto", "buona giornata", "buonasera", "ciao"]
        _has_goodbye = any(g in text_lower for g in _goodbye)

        if any(word in text_lower for word in affirmative):
            # Record interest
            if self._proposed_package and self.booking_sm.context.client_id:
                self._record_package_proposal(
                    self.booking_sm.context.client_id,
                    self._proposed_package["id"],
                )
            pkg_name = self._proposed_package.get("nome", "pacchetto") if self._proposed_package else "pacchetto"
            self._pending_package_proposal = False
            self._proposed_package = None
            # S122: If user also said goodbye, close the call
            if _has_goodbye:
                summary = self.booking_sm.context.get_summary()
                self.booking_sm.context.state = BookingState.COMPLETED
                response = (
                    f"Ottimo, ho annotato il suo interesse per {pkg_name}! "
                    f"Le invieremo conferma via WhatsApp. {get_goodbye('booking_done', self.business_name, date=self.booking_sm.context.date_display or '')}"
                )
                return response, "package_accepted_close", layer
            response = (
                f"Ottimo! Ho annotato il suo interesse per il pacchetto {pkg_name}. "
                f"L'operatore la contatterà con tutti i dettagli. Posso aiutarla in altro modo?"
            )
            return response, "package_accepted", layer

        elif any(word in text_lower for word in negative) or _has_goodbye:
            self._pending_package_proposal = False
            self._proposed_package = None
            if _has_goodbye:
                self.booking_sm.context.state = BookingState.COMPLETED
                response = f"Nessun problema! {get_goodbye('generic', self.business_name)}"
                return response, "package_declined_close", layer
            response = "Nessun problema! Posso aiutarla in altro modo?"
            return response, "package_declined", layer

        else:
            pkg = self._proposed_package
            if pkg:
                response = (
                    f"Il pacchetto {pkg['nome']} include {pkg['servizi_inclusi']} sedute "
                    f"a {pkg['prezzo']:.0f} euro invece di {pkg['prezzo_originale']:.0f}. "
                    f"Le interessa? Mi dica sì o no."
                )
            else:
                response = "Mi dica sì se le interessa il pacchetto, o no."
            return response, "package_repeat", layer

    # ─────────────────────────────────────────────────────────────────
    # VoIP interface (F15) — called by VoIPManager in voip.py
    # ─────────────────────────────────────────────────────────────────

    async def greet(self, phone_number: str = "") -> dict:
        """Start session and return greeting audio for VoIP calls.

        Called by VoIPManager._on_call_connected() when a SIP call is
        answered. Returns a dict compatible with VoIPManager expectations.
        """
        # B1: Mark this session as VoIP and pre-warm filler phrases
        self._is_voip_call = True
        await self.warm_fillers()

        result = await self.start_session(channel=SessionChannel.VOICE, phone_number=phone_number)
        return {
            "audio_response": result.audio_bytes,
            "text": result.response,
            "session_id": result.session_id,
        }

    async def process_audio(self, audio_bytes: bytes) -> dict:
        """Process raw PCM audio from a VoIP call through the full pipeline.

        Called by VoIPManager._process_audio() on each audio chunk received
        via RTP. Input is PCM 16-bit 16kHz mono (after upsample from 8kHz).

        Returns a dict compatible with VoIPManager:
            audio_response: bytes | None — PCM response (16kHz 16-bit)
            text: str — TTS text
            should_exit: bool — True when call should end (goodbye state)
            transcription: str — STT result
            latency_ms: float
        """
        import io
        import wave as _wave

        # Wrap raw PCM in WAV container — Groq STT expects WAV bytes
        wav_buffer = io.BytesIO()
        with _wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)   # 16-bit
            wf.setframerate(16000)
            wf.writeframes(audio_bytes)
        wav_data = wav_buffer.getvalue()

        # F2: Acoustic frustration analysis (before STT, <2ms overhead)
        self._last_acoustic_score = 0.0
        if self.acoustic_detector:
            _is_tts = getattr(self, '_tts_playing', False)
            _af_result = self.acoustic_detector.analyze_audio(
                audio_bytes, is_speech=True, is_tts_playing=_is_tts
            )
            self._last_acoustic_score = _af_result.frustration_score
            if _af_result.frustration_score >= 0.7:
                logger.info(f"[F2] High acoustic frustration: {_af_result.frustration_score:.2f} "
                           f"(rms={_af_result.rms:.4f}, pitch={_af_result.pitch_hz:.0f}Hz)")

        # S140: State-aware STT prompting — different prompt based on FSM state
        fsm_state = None
        if self.booking_sm:
            try:
                fsm_state = self.booking_sm.current_state
            except Exception:
                pass

        # Name-expecting states get name-biased prompt
        _NAME_STATES = {"IDLE", "WAITING_NAME", "WAITING_SURNAME"}
        fsm_state_name = fsm_state.value if fsm_state else "IDLE"

        if fsm_state_name.upper() in _NAME_STATES and self._name_corrector:
            stt_prompt = self._name_corrector.get_prompt()
        elif self._name_corrector:
            stt_prompt = "Prenotazione appuntamento. Si, no, confermo, annullo, domani, lunedi."
        else:
            stt_prompt = None

        transcription = await self.groq.transcribe_audio(wav_data, prompt=stt_prompt)
        if not transcription or not transcription.strip():
            return {"audio_response": None, "text": "", "should_exit": False}

        # F1: EOU — log sentence completion probability (used by VAD for adaptive silence)
        if HAS_EOU:
            _eou_prob = sentence_complete_probability(transcription)
            _fsm_state_str = fsm_state_name if fsm_state_name else "idle"
            _adaptive_ms = get_adaptive_silence_ms(transcription, _fsm_state_str, _eou_prob)
            logger.debug(f"[F1] EOU: prob={_eou_prob:.2f}, adaptive_silence={_adaptive_ms}ms for '{transcription[:40]}'")

        # Layer 2: phonetic fast-path (Jaro-Winkler ≥ 0.85 → sostituzione deterministica)
        # S142: ONLY apply NameCorrector in name-expecting states
        # Was: applied to ALL text → "farmi"→"Fabbri", "barba"→"Barbieri"
        if self._name_corrector and fsm_state_name.upper() in _NAME_STATES:
            transcription = self._name_corrector.correct(transcription)

        # S140: Common-word rejection during name states
        # "Grazie" is NEVER a valid surname answer — reject and ask to repeat
        _COMMON_WORD_MISHEARS = {
            "grazie", "prego", "buongiorno", "buonasera", "arrivederci",
            "ciao", "salve", "scusi", "perfetto", "benissimo", "certamente",
        }
        if fsm_state_name.upper() in _NAME_STATES:
            cleaned_transcript = transcription.lower().strip().rstrip('.!?,;:')
            if cleaned_transcript in _COMMON_WORD_MISHEARS:
                print(f"[STT] Rejected common-word mishear '{transcription}' during {fsm_state_name}")
                repeat_text = "Non ho capito bene il nome. Può ripeterlo per favore?"
                tts_bytes = await self.tts.synthesize(repeat_text)
                return {
                    "audio_response": tts_bytes,
                    "text": repeat_text,
                    "should_exit": False,
                    "transcription": f"[rejected:{transcription}]",
                    "latency_ms": 0,
                }

        # B1: Pre-generate filler audio for VoIP (played while pipeline processes)
        # Filler is useful before DB-heavy or LLM operations. We generate it
        # optimistically; VoIP layer plays it only if pipeline takes >0ms.
        filler_audio = await self._get_filler_audio()

        # Orchestrator pipeline (text → response + TTS)
        # Pass current session_id to avoid FSM reset between turns
        current_sid = self._current_session.session_id if self._current_session else None
        result = await self.process(user_input=transcription, session_id=current_sid)

        return {
            "audio_response": result.audio_bytes,
            "filler_audio": filler_audio,  # B1: VoIP plays this first
            "text": result.response,
            "should_exit": result.should_exit,
            "transcription": transcription,
            "latency_ms": result.latency_ms,
        }


    def _is_stt_hallucination(self, text: str) -> bool:
        """F19-FIX8: Detect STT hallucinations (Whisper artifacts on silence/noise).

        Known patterns: URLs, ad content, foreign languages, repeated phrases.
        Returns True if the text should be silently discarded.
        """
        if not text or len(text.strip()) < 2:
            return True

        text_stripped = text.strip()

        # URLs (Whisper hallucinates URLs on silence)
        if re.search(r'https?://|www\.|\.\w{2,4}/', text_stripped):
            return True

        # Known Whisper hallucination patterns
        _HALLUCINATION_PATTERNS = [
            r"sottotitoli\s+(?:di|a\s+cura\s+di)",
            r"iscriviti\s+al\s+canale",
            r"corso\s+gratuito",
            r"mesmerism\.info",
            r"amara\.org",
            r"il\s+nostro\s+corso",
            r"grazie\s+per\s+la\s+visione",
            r"music\s*$",  # bare "[Music]" or "music"
            r"^\[.*\]$",  # bare bracketed content like "[Musica]"
        ]
        if any(re.search(p, text_stripped, re.IGNORECASE) for p in _HALLUCINATION_PATTERNS):
            return True

        # Single repeated word/syllable (noise artifact)
        words = text_stripped.split()
        if len(words) >= 3 and len(set(w.lower() for w in words)) == 1:
            return True

        return False


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
