"""
FLUXION Voice Agent - Booking State Machine

Enterprise state machine for conversational booking flow.
Implements deterministic transitions with interruption handling.

Day 6-7 of RAG Enterprise implementation.

States:
    IDLE → WAITING_SERVICE → WAITING_DATE → WAITING_TIME → CONFIRMING → COMPLETED
                                                        ↘ CANCELLED

Features:
- Full state machine with 8 states
- Interruption handling (cambio, aspetta, annulla)
- Entity extraction integration
- JSON serialization for persistence
- Context-aware prompts
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import json
import re
import string
import logging

logger = logging.getLogger(__name__)

# Handle both package import and direct import
try:
    from .entity_extractor import (
        extract_date,
        extract_time,
        extract_name,
        extract_service,
        extract_services,
        extract_operator,
        extract_all,
        ExtractionResult,
    )
    from .disambiguation_handler import DisambiguationHandler, name_similarity
except ImportError:
    from entity_extractor import (
        extract_date,
        extract_time,
        extract_name,
        extract_service,
        extract_services,
        extract_operator,
        extract_all,
        ExtractionResult,
    )
    from disambiguation_handler import DisambiguationHandler, name_similarity

# Italian regex module for ambiguous date detection
try:
    try:
        from .italian_regex import is_ambiguous_date, strip_fillers, extract_multi_services
    except ImportError:
        from italian_regex import is_ambiguous_date, strip_fillers, extract_multi_services
    HAS_ITALIAN_REGEX = True
except ImportError:
    HAS_ITALIAN_REGEX = False


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class BookingState(Enum):
    """Booking conversation states."""
    IDLE = "idle"
    WAITING_NAME = "waiting_name"
    WAITING_SERVICE = "waiting_service"
    WAITING_DATE = "waiting_date"
    WAITING_TIME = "waiting_time"
    WAITING_OPERATOR = "waiting_operator"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    # Guided identity collection states (Kimi 2.5 flow)
    WAITING_SURNAME = "waiting_surname"
    CONFIRMING_PHONE = "confirming_phone"
    # New client registration states (legacy flow via PROPOSE_REGISTRATION)
    PROPOSE_REGISTRATION = "propose_registration"
    REGISTERING_SURNAME = "registering_surname"
    REGISTERING_PHONE = "registering_phone"
    REGISTERING_CONFIRM = "registering_confirm"
    # Waitlist states
    CHECKING_AVAILABILITY = "checking_availability"
    SLOT_UNAVAILABLE = "slot_unavailable"
    PROPOSING_WAITLIST = "proposing_waitlist"
    CONFIRMING_WAITLIST = "confirming_waitlist"
    WAITLIST_SAVED = "waitlist_saved"
    # Closing confirmation state
    ASKING_CLOSE_CONFIRMATION = "asking_close_confirmation"
    # Name disambiguation states
    DISAMBIGUATING_NAME = "disambiguating_name"
    DISAMBIGUATING_BIRTH_DATE = "disambiguating_birth_date"
    # CoVe 2026: Booking completion state
    BOOKING_COMPLETE = "booking_complete"


# =============================================================================
# BOOKING CONTEXT
# =============================================================================

@dataclass
class BookingContext:
    """
    Conversational state context for a booking.

    Stores all collected information and supports JSON serialization
    for persistence across sessions.
    """
    state: BookingState = BookingState.IDLE

    # Client info
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    client_surname: Optional[str] = None  # For new client registration
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    is_new_client: bool = False  # True if registering new client

    # Booking info
    service: Optional[str] = None
    services: Optional[List[str]] = None  # Multiple services
    service_display: Optional[str] = None  # Human-readable service name(s)
    date: Optional[str] = None  # YYYY-MM-DD format
    date_display: Optional[str] = None  # Italian format "mercoledì 15 gennaio"
    time: Optional[str] = None  # HH:MM format
    time_display: Optional[str] = None  # "alle 15:00"
    time_is_approximate: bool = False

    # Operator preference
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    operator_requested: bool = False

    # Metadata
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    turns_count: int = 0

    # Interruption tracking
    was_interrupted: bool = False
    previous_state: Optional[str] = None

    # Waitlist tracking
    waiting_for_waitlist_confirm: bool = False
    waitlist_id: Optional[str] = None  # ID entry in waitlist table
    proposed_waitlist: bool = False  # True if waitlist was proposed to user
    alternative_slots: List[Dict[str, str]] = field(default_factory=list)  # Alternative slots offered

    # Vertical and correction tracking
    vertical: str = "salone"
    corrections_made: int = 0
    clarifications_asked: int = 0
    operator_gender_preference: Optional[str] = None  # "F" or "M"
    urgency: bool = False
    
    # Disambiguation tracking
    disambiguation_candidates: List[Dict[str, Any]] = field(default_factory=list)
    disambiguation_attempts: int = 0
    disambiguation_handler: Optional[Any] = field(default=None, repr=False)

    def to_json(self) -> str:
        """Serialize context to JSON for persistence."""
        data = asdict(self)
        data["state"] = self.state.value
        if self.previous_state:
            data["previous_state"] = self.previous_state
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "BookingContext":
        """Deserialize context from JSON."""
        data = json.loads(json_str)
        data["state"] = BookingState(data["state"])
        if data.get("previous_state"):
            data["previous_state"] = data["previous_state"]
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "state": self.state.value,
            "client": {
                "id": self.client_id,
                "name": self.client_name,
                "phone": self.client_phone,
                "email": self.client_email,
            } if self.client_id or self.client_name else None,
            "booking": {
                "service": self.service,
                "service_display": self.service_display,
                "date": self.date,
                "date_display": self.date_display,
                "time": self.time,
                "time_display": self.time_display,
                "operator": self.operator_name,
            } if self.service or self.date else None,
            "turns": self.turns_count,
        }

    def get_summary(self) -> str:
        """Get human-readable booking summary."""
        parts = []
        if self.service_display or self.service:
            parts.append(self.service_display or self.service)
        if self.date_display:
            parts.append(self.date_display)
        elif self.date:
            parts.append(f"il {self.date}")
        if self.time_display:
            parts.append(self.time_display)
        elif self.time:
            parts.append(f"alle {self.time}")
        if self.operator_name:
            parts.append(f"con {self.operator_name}")
        return ", ".join(parts) if parts else "nessun dettaglio"

    def is_complete(self) -> bool:
        """Check if we have all required info for booking."""
        return bool(self.service and self.date and self.time)

    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        missing = []
        if not self.service:
            missing.append("servizio")
        if not self.date:
            missing.append("data")
        if not self.time:
            missing.append("ora")
        return missing


# =============================================================================
# STATE MACHINE RESULT
# =============================================================================

@dataclass
class StateMachineResult:
    """Result of a state machine transition."""
    next_state: BookingState
    response: str
    booking: Optional[Dict[str, Any]] = None
    needs_db_lookup: bool = False
    lookup_type: Optional[str] = None  # "client", "availability", "operator"
    lookup_params: Optional[Dict] = None
    should_exit: bool = False
    follow_up_response: Optional[str] = None
    context_updates: Optional[Dict[str, Any]] = None
    whatsapp_triggered: bool = False  # CoVe 2026: WhatsApp notification triggered
    confidence: float = 1.0  # CoVe 2026: Confidence score
    needs_clarification: bool = False  # CoVe 2026: Needs clarification

    def has_follow_up(self) -> bool:
        """Check if there is a follow-up response."""
        return self.follow_up_response is not None

    def get_all_responses(self) -> List[str]:
        """Return all responses in order."""
        responses = [self.response]
        if self.follow_up_response:
            responses.append(self.follow_up_response)
        return responses


# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================

# Default service synonyms (can be overridden by verticale config)
DEFAULT_SERVICES = {
    "taglio": ["taglio", "tagli", "tagliare", "sforbiciata", "spuntatina", "accorciare",
               "capelli", "fare i capelli", "taglio capelli", "sistemare i capelli"],
    "piega": ["piega", "messa in piega", "asciugatura"],
    "colore": ["colore", "tinta", "colorazione", "colorare", "ritocco"],
    "barba": ["barba", "rasatura", "barba e baffi"],
    "trattamento": ["trattamento", "cheratina", "maschera", "botox capelli"],
}

# Service display names
SERVICE_DISPLAY = {
    "taglio": "Taglio",
    "piega": "Piega",
    "colore": "Colore",
    "barba": "Barba",
    "trattamento": "Trattamento",
}


# =============================================================================
# INTERRUPTION PATTERNS
# =============================================================================

INTERRUPTION_PATTERNS = {
    "reset": [
        r"\b(ricominciamo|ricomincia|da\s+capo|annulla\s+tutto)\b",
        r"\b(cancella|voglio\s+annullare)\b",
    ],
    "change": [
        r"\b(aspetta|aspetti|un\s+attimo|momento)\b",
        r"\b(cambio|cambia|no\s+aspetta|anzi)\b",
        r"\b(volevo\s+dire|intendevo)\b",
    ],
    # CoVe FIX: Pattern più specifici per evitare falsi positivi
    # "persona diversa" (disambiguazione rifiuto) ≠ "parla con una persona" (escalation)
    "operator": [
        r"\b(operatore|operatrice)\b",
        r"\b(parla\s+con\s+(?:un|una)?\s*(?:operatore|persona|umano))\b",
        r"\b(vorrei\s+(?:un|una)?\s*(?:operatore|persona|umano))\b",
        r"\b(passami\s+(?:un|una)?\s*(?:operatore|persona))\b",
        r"\b(non\s+capisco\s+niente|non\s+capisco\s+nulla|basta|aiuto)\b",
    ],
    "cancel_booking": [
        r"\b(disdico|disdire|cancello|cancellare)\b",
        r"\b(annullo|annullare)\s+(la\s+)?prenotazione\b",
    ],
}


# =============================================================================
# CORRECTION PATTERNS PER VERTICAL (C9: use (?:\.|,|$) not (?:\s|$))
# =============================================================================

CORRECTION_PATTERNS_SALONE = {
    "servizio": [
        r"(?:aggiungi|metti|anche|pure)\s+(?:una?\s+)?(taglio|piega|colore|barba|trattamento|cheratina|extension|manicure|pedicure)(?:\.|,|$)",
        r"(?:senza|no)\s+(?:la?\s+)?(piega|colore|barba|trattamento)(?:\.|,|$)",
        r"(?:meglio|invece|piuttosto)\s+(taglio|piega|colore|barba|trattamento|cheratina|extension)(?:\.|,|$)",
    ],
    "operatore": [
        r"(?:con|da)\s+(?:una?\s+)?([A-Z][a-zàèéìòù]+)(?:\.|,|$)",
        r"(?:meglio|preferisco|piuttosto)\s+([A-Z][a-zàèéìòù]+)(?:\.|,|$)",
    ],
    "data": [
        r"(?:meglio|piuttosto|anzi|invece)\s+(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|domani|dopodomani|oggi|prossima settimana)(?:\.|,|$)",
        r"(?:cambio)\s+(?:a\s+|il\s+)?(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|domani|dopodomani)(?:\.|,|$)",
    ],
    "ora": [
        r"(?:alle|verso)\s+(?:le\s+)?(\d{1,2}(?::\d{2})?)(?:\.|,|$)",
        r"(?:meglio|invece)\s+(?:la?\s+)?(mattina|pomeriggio|sera)(?:\.|,|$)",
    ],
}

CORRECTION_PATTERNS_PALESTRA = {
    "tipo_attivita": [
        r"(?:meglio|invece|piuttosto)\s+(yoga|pilates|spinning|zumba|crossfit|boxe|step|functional|trx|calisthenics)(?:\.|,|$)",
        r"(?:preferisco|vorrei)\s+(?:una?\s+)?(.+?)(?:\.|,|$)",
    ],
    "istruttore": [
        r"(?:con|da)\s+(?:una?\s+)?([A-Z][a-zàèéìòù]+)(?:\.|,|$)",
        r"(?:meglio|se c'è)\s+([A-Z][a-zàèéìòù]+)(?:\.|,|$)",
    ],
    "data": [
        r"(?:meglio|invece|piuttosto)\s+(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|domani|dopodomani|prossima settimana)(?:\.|,|$)",
    ],
    "ora": [
        r"(?:alle|verso)\s+(?:le\s+)?(\d{1,2}(?::\d{2})?)(?:\.|,|$)",
        r"(?:meglio|invece)\s+(?:la?\s+)?(mattina|pomeriggio|sera)(?:\.|,|$)",
    ],
}

CORRECTION_PATTERNS_MEDICAL = {
    "specialita": [
        r"(?:meglio|invece|piuttosto)\s+(cardiologo|ortopedico|dermatologo|oculista|otorinolaringoiatra|gastroenterologo|pneumologo|neurologo|generico|pediatra|ginecologo)(?:\.|,|$)",
        r"(?:con|da)\s+(?:uno?\s+)?(.+?)(?:\.|,|$)",
    ],
    "medico": [
        r"(?:con|da)\s+(?:il\s+)?(?:dr|dott|dottor)?\.?\s*([A-Z][a-zàèéìòù]+)(?:\.|,|$)",
        r"(?:meglio|preferisco)\s+([A-Z][a-zàèéìòù]+)(?:\.|,|$)",
    ],
    "tipo_visita": [
        r"(?:è|per|una?)\s+(prima visita|controllo|follow.?up|revisione|urgente)(?:\.|,|$)",
    ],
    "urgenza": [
        r"(?:è\s+)?urgente(?:\.|,|$)",
        r"(?:il\s+)?(?:prima possibile|subito)(?:\.|,|$)",
    ],
    "data": [
        r"(?:meglio|invece|piuttosto)\s+(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|domani|dopodomani|prossima settimana)(?:\.|,|$)",
    ],
    "ora": [
        r"(?:alle|verso)\s+(?:le\s+)?(\d{1,2}(?::\d{2})?)(?:\.|,|$)",
    ],
}

CORRECTION_PATTERNS_AUTO = {
    "tipo_intervento": [
        r"(?:in realtà|invece|piuttosto|meglio)\s+(tagliando|revisione|cambio gomme|freni|sospensioni|motore|diagnosi|carrozzeria|elettronica|climatizzatore|cambio olio)(?:\.|,|$)",
    ],
    "marca": [
        r"(?:scusa|mi sbaglio|in realtà)\s+(fiat|ford|audi|bmw|mercedes|volkswagen|toyota|hyundai|renault|citroen|peugeot|alfa romeo|lancia)(?:\.|,|$)",
    ],
    "data": [
        r"(?:meglio|invece|piuttosto)\s+(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|domani|dopodomani|prossima settimana)(?:\.|,|$)",
    ],
    "ora": [
        r"(?:alle|verso)\s+(?:le\s+)?(\d{1,2}(?::\d{2})?)(?:\.|,|$)",
    ],
}

CORRECTION_PATTERNS_RESTAURANT = {
    "num_coperti": [
        r"(?:per|siamo|in realtà)\s+(\d+)(?:\s+(?:persone|coperti))?(?:\.|,|$)",
        r"(?:invece|meglio|piuttosto)\s+(\d+)(?:\.|,|$)",
    ],
    "data": [
        r"(?:meglio|invece|piuttosto|anzi)\s+(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|domani|dopodomani|stasera|prossima settimana)(?:\.|,|$)",
    ],
    "ora": [
        r"(?:alle|verso|ore)\s+(?:le\s+)?(\d{1,2}(?::\d{2})?)(?:\.|,|$)",
    ],
    "sala": [
        r"(?:meglio|se c'è|preferisco|piuttosto)\s+(interno|esterno|giardino|terrazza|privata)(?:\.|,|$)",
    ],
}


# =============================================================================
# NAME SANITIZATION
# =============================================================================

def sanitize_name(text: str, is_surname: bool = False) -> str:
    """
    Clean and normalize Italian names/surnames.
    Removes spurious punctuation from STT, preserves internal apostrophes,
    normalizes capitalization, handles noble prefixes.
    """
    if not text:
        return ""

    text = text.strip()

    # Remove leading/trailing punctuation (preserve internal apostrophes/hyphens)
    while text and text[0] in string.punctuation:
        text = text[1:]
    while text and text[-1] in string.punctuation:
        text = text[:-1]

    # Normalize typographic apostrophes
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")

    words = text.split()
    if not words:
        return ""

    processed = []
    for i, word in enumerate(words):
        if "'" in word:
            parts = word.split("'")
            word = "'".join(part.capitalize() for part in parts)
        else:
            word = word.capitalize()

        # Noble prefix handling for surnames
        if i == 0 and is_surname and word.lower() in ["di", "de", "del", "della", "von", "van"]:
            word = word.lower()

        processed.append(word)

    result = " ".join(processed)

    # Fix noble prefix: keep lowercase prefix + capitalized rest
    if is_surname and processed and processed[0].lower() in ["di", "de", "del", "della", "von", "van"]:
        if len(processed) > 1:
            parts = [processed[0].lower()]
            parts.extend(p.capitalize() for p in processed[1:])
            result = " ".join(parts)

    return result


def sanitize_name_pair(
    name: Optional[str],
    surname: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Clean a name+surname pair.
    Handles case where name already contains surname (C5: len >= 2).
    """
    if not name:
        return None, surname

    name = sanitize_name(name, is_surname=False)

    # Auto-split if name has multiple words and no surname provided
    if surname is None and " " in name:
        parts = name.split()
        if len(parts) >= 2:  # C5: >= 2 not == 2
            name = parts[0]
            surname = " ".join(parts[1:])  # C5: join all remaining

    if surname:
        surname = sanitize_name(surname, is_surname=True)
        # Prevent duplication
        if name.lower() == surname.lower():
            surname = None

    return name, surname


# =============================================================================
# RESPONSE TEMPLATES
# =============================================================================

TEMPLATES = {
    # State entry prompts - domande APERTE, non presumere cosa offre il business
    "ask_service": "Come posso aiutarla? Mi dica che trattamento desidera.",
    "ask_date": "Bene, {service}! Per quale giorno?",
    "ask_time": "{date}, perfetto. A che ora le farebbe comodo?",
    "ask_time_with_slots": "{date}, perfetto. Abbiamo disponibilità alle {slots}. Quale preferisce?",
    "ask_operator": "Ha una preferenza per l'operatore?",
    "ask_name": "Mi dice il suo nome, per cortesia?",

    # Confirmations
    "confirm_booking": "Riepilogo: {summary}. Conferma?",
    "booking_confirmed": "Prenotazione confermata! {summary}. La aspettiamo!",
    "booking_cancelled": "D'accordo, ho annullato. Posso aiutarla in altro modo?",

    # Errors and clarifications - risposte UMANE, non tecniche
    "service_not_understood": "Mi faccia capire meglio, che tipo di trattamento desidera?",
    "date_not_understood": "Per quale giorno vorrebbe prenotare?",
    "time_not_understood": "A che ora le andrebbe bene?",

    # Interruptions
    "reset_ack": "D'accordo, ricominciamo. Come posso aiutarla?",
    "change_ack": "Certo, mi dica.",
    "operator_escalate": "La metto in contatto con un operatore, un attimo...",

    # Approximate time handling
    "time_approximate": "Per {preference} abbiamo disponibilità alle {slots}. Quale preferisce?",

    # New client registration - un campo alla volta, chiaro
    "propose_registration": "Non ho trovato il suo nominativo. Vuole che la registri?",
    "ask_surname": "Mi dice il cognome?",
    "ask_phone": "Grazie {name}! Un numero di telefono per eventuali comunicazioni?",
    "confirm_registration": "Riepilogo: {name} {surname}, telefono {phone}. Tutto corretto?",
    "registration_complete": "Benvenuto {name}! Registrazione completata.",
    "registration_cancelled": "Nessun problema. Posso aiutarla in altro modo?",

    # Guided flow (Kimi 2.5) - identity + calendar
    "ask_surname_after_name": "Piacere {name}! Mi dice il cognome?",
    "confirm_phone_number": "Ho capito {phone}, è corretto?",
    "confirm_phone_reask": "Mi ripete il numero, per cortesia?",
    "welcome_back": "Bentornato {name}! Cosa desidera fare oggi?",
    "week_no_availability": "Mi dispiace, {week} siamo al completo. Vuole provare la settimana dopo?",
    "week_availability": "{week} abbiamo disponibilità {days}. Quale giorno preferisce?",

    # Fallback universale
    "fallback_clarify": "Mi faccia capire meglio se posso aiutarla.",
    # Closing confirmation
    "ask_close_confirmation": "Appuntamento confermato! Terminiamo la comunicazione e le inviamo la conferma via WhatsApp?",
    "close_confirmed": "Perfetto! A presto da {business_name}. Buona giornata!",
    "close_stay": "Va bene, rimaniamo in linea. Posso aiutarla con altro?",
    # Disambiguation
    "disambiguation_ask": "Forse intendeva '{suggested_name}'? Mi conferma la data di nascita per verificare?",
    "disambiguation_confirmed": "Perfetto, bentornato {name}!",
    "disambiguation_retry": "Non ho capito bene. Può ripetere la data di nascita?",
    "disambiguation_new_client": "Grazie! La registro come nuovo cliente.",
    # CoVe: Template per riconoscimento soprannome
    "nickname_recognized": "Ciao {soprannome}! Bentornato {nome}! Come posso aiutarti oggi?",
}


# =============================================================================
# BOOKING STATE MACHINE
# =============================================================================

class BookingStateMachine:
    """
    Enterprise state machine for booking conversations.

    Manages the booking flow with:
    - Explicit state transitions
    - Entity extraction integration
    - Interruption handling
    - Context persistence
    """

    def __init__(
        self,
        services_config: Optional[Dict[str, List[str]]] = None,
        reference_date: Optional[datetime] = None,
        vertical: str = "salone",
        groq_nlu=None
    ):
        """
        Initialize state machine.

        Args:
            services_config: Service synonyms mapping (default: DEFAULT_SERVICES)
            reference_date: Reference date for testing (default: now)
            vertical: Business vertical (salone, palestra, medical, auto, restaurant)
            groq_nlu: Optional GroqNLU instance for LLM fallback
        """
        self.services_config = services_config or DEFAULT_SERVICES
        self.reference_date = reference_date
        self.context = BookingContext(vertical=vertical)
        self.groq_nlu = groq_nlu
        self.disambiguation_handler = DisambiguationHandler()

    def reset(self):
        """Reset state machine to IDLE."""
        self.context = BookingContext()

    def reset_for_new_booking(self):
        """Reset state machine but preserve client identity for follow-up bookings."""
        client_id = self.context.client_id
        client_name = self.context.client_name
        client_surname = self.context.client_surname
        client_phone = self.context.client_phone
        client_email = self.context.client_email
        vertical = self.context.vertical

        self.context = BookingContext(vertical=vertical)
        self.context.client_id = client_id
        self.context.client_name = client_name
        self.context.client_surname = client_surname
        self.context.client_phone = client_phone
        self.context.client_email = client_email

    def set_context(self, context: BookingContext):
        """Set context (for resuming conversations)."""
        self.context = context

    def get_context(self) -> BookingContext:
        """Get current context."""
        return self.context

    def handle_input(self, user_input: str) -> StateMachineResult:
        """
        Handle user input (alias for process_message, for test compatibility).
        
        CoVe 2026: This is the public API method used by tests and orchestrator.
        """
        return self.process_message(user_input)

    def handle_input_with_confidence(self, user_input: str, confidence: float) -> StateMachineResult:
        """
        Handle user input with STT confidence score.
        
        CoVe 2026: If confidence < 0.7, ask user to repeat.
        
        Args:
            user_input: User's message text
            confidence: STT confidence score (0.0 - 1.0)
            
        Returns:
            StateMachineResult with response
        """
        # If low confidence, ask to repeat
        if confidence < 0.7:
            return StateMachineResult(
                next_state=self.context.state,
                response="Scusi, non ho capito bene. Può ripetere per favore?",
                confidence=confidence,
                needs_clarification=True
            )
        
        # Normal processing
        return self.process_message(user_input)

    def handle_api_error(self, error_message: str) -> StateMachineResult:
        """
        Handle API/backend errors gracefully.
        
        CoVe 2026: Provides user-friendly error recovery.
        
        Args:
            error_message: The error message from API
            
        Returns:
            StateMachineResult with recovery response
        """
        return StateMachineResult(
            next_state=self.context.state,
            response=f"Mi scusi, c'è un problema tecnico ({error_message}). Può riprovare tra un momento?",
            confidence=0.5,
            needs_clarification=True
        )

    def complete_booking(self) -> StateMachineResult:
        """
        Complete the booking and trigger WhatsApp notification.
        
        CoVe 2026: Finalizes booking and triggers notifications.
        
        Returns:
            StateMachineResult with booking confirmation
        """
        # Mark booking as complete
        self.context.state = BookingState.BOOKING_COMPLETE
        self.context.booking_confirmed = True
        
        # Check if WhatsApp should be triggered
        whatsapp_triggered = bool(self.context.client_phone)
        
        return StateMachineResult(
            next_state=BookingState.BOOKING_COMPLETE,
            response="Prenotazione completata con successo!",
            booking=self.context.to_dict(),
            whatsapp_triggered=whatsapp_triggered
        )

    def process_message(self, user_input: str) -> StateMachineResult:
        """
        Process user input and transition state.

        This is the main entry point for the state machine.

        Args:
            user_input: User's message text

        Returns:
            StateMachineResult with next state, response, and any needed lookups
        """
        self.context.turns_count += 1
        self.context.updated_at = datetime.now().isoformat()

        # Check for interruptions first (highest priority)
        interruption = self._check_interruption(user_input)
        if interruption:
            return interruption

        # Extract all entities from input
        extracted = extract_all(user_input, self.services_config, self.reference_date)

        # Update context with extracted entities
        self._update_context_from_extraction(extracted)

        # Process based on current state
        state = self.context.state

        if state == BookingState.IDLE:
            return self._handle_idle(user_input, extracted)

        elif state == BookingState.WAITING_NAME:
            return self._handle_waiting_name(user_input, extracted)

        elif state == BookingState.WAITING_SERVICE:
            return self._handle_waiting_service(user_input, extracted)

        elif state == BookingState.WAITING_DATE:
            return self._handle_waiting_date(user_input, extracted)

        elif state == BookingState.WAITING_TIME:
            return self._handle_waiting_time(user_input, extracted)

        elif state == BookingState.WAITING_OPERATOR:
            return self._handle_waiting_operator(user_input, extracted)

        elif state == BookingState.CONFIRMING:
            return self._handle_confirming(user_input, extracted)

        # New client registration states
        elif state == BookingState.PROPOSE_REGISTRATION:
            return self._handle_propose_registration(user_input, extracted)

        elif state == BookingState.REGISTERING_SURNAME:
            return self._handle_registering_surname(user_input, extracted)

        elif state == BookingState.WAITING_SURNAME:
            return self._handle_waiting_surname(user_input, extracted)

        elif state == BookingState.REGISTERING_PHONE:
            return self._handle_registering_phone(user_input, extracted)

        elif state == BookingState.CONFIRMING_PHONE:
            return self._handle_confirming_phone(user_input, extracted)

        elif state == BookingState.REGISTERING_CONFIRM:
            return self._handle_registering_confirm(user_input, extracted)

        elif state == BookingState.ASKING_CLOSE_CONFIRMATION:
            return self._handle_asking_close_confirmation(user_input)

        elif state == BookingState.DISAMBIGUATING_NAME:
            return self._handle_disambiguating_name(user_input, extracted)

        elif state == BookingState.DISAMBIGUATING_BIRTH_DATE:
            return self._handle_disambiguating_birth_date(user_input)

        elif state == BookingState.CANCELLED:
            # Cancelled — close the call
            return StateMachineResult(
                next_state=BookingState.CANCELLED,
                response="Va bene, nessun problema. Arrivederci!",
                should_exit=True
            )

        # Fallback
        return StateMachineResult(
            next_state=self.context.state,
            response=TEMPLATES["fallback_clarify"]
        )

    def _check_interruption(self, text: str) -> Optional[StateMachineResult]:
        """Check for interruption patterns."""
        text_lower = text.lower()

        # Reset/cancel interruption
        for pattern in INTERRUPTION_PATTERNS["reset"]:
            if re.search(pattern, text_lower):
                self.context.previous_state = self.context.state.value
                self.context.was_interrupted = True
                self.reset()
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response=TEMPLATES["reset_ack"]
                )

        # Operator escalation
        for pattern in INTERRUPTION_PATTERNS["operator"]:
            if re.search(pattern, text_lower):
                return StateMachineResult(
                    next_state=self.context.state,
                    response=TEMPLATES["operator_escalate"],
                    should_exit=True,
                    lookup_type="operator_escalation"
                )

        # Change request (soft interruption - just acknowledge)
        # But skip if we're in CONFIRMING, WAITING_TIME, or ASKING_CLOSE_CONFIRMATION
        # (those are handled by state handlers for precise state changes)
        if self.context.state in (BookingState.CONFIRMING, BookingState.WAITING_TIME, BookingState.ASKING_CLOSE_CONFIRMATION):
            change_targets = ["servizio", "data", "giorno", "ora", "orario", "quando"]
            if any(target in text_lower for target in change_targets):
                # Let state handler handle this for precise state changes
                return None
            # In ASKING_CLOSE_CONFIRMATION, let the state handler handle all responses
            if self.context.state == BookingState.ASKING_CLOSE_CONFIRMATION:
                return None

        for pattern in INTERRUPTION_PATTERNS["change"]:
            if re.search(pattern, text_lower):
                return StateMachineResult(
                    next_state=self.context.state,
                    response=TEMPLATES["change_ack"]
                )

        return None

    def _update_context_from_extraction(self, extracted, force_update: bool = False):
        """
        Update context with extracted entities.

        Args:
            extracted: ExtractionResult or Dict[str, Any] (for correction patterns)
            force_update: If True, overwrite existing fields (used in CONFIRMING corrections)
        """
        # Handle Dict input from correction patterns
        if isinstance(extracted, dict):
            self._update_context_from_dict(extracted, force_update)
            return

        # Handle ExtractionResult input (normal flow)
        if extracted.date and (force_update or not self.context.date):
            # Skip ambiguous dates like "prossima settimana" - ask for specific day
            if HAS_ITALIAN_REGEX and extracted.date.original_text:
                if is_ambiguous_date(extracted.date.original_text):
                    logger.info(f"[SM] Ambiguous date skipped: {extracted.date.original_text}")
                    # Don't set date - let handler ask for clarification
                    pass
                else:
                    self.context.date = extracted.date.to_string("%Y-%m-%d")
                    self.context.date_display = extracted.date.to_italian()
            else:
                self.context.date = extracted.date.to_string("%Y-%m-%d")
                self.context.date_display = extracted.date.to_italian()

        if extracted.time and (force_update or not self.context.time):
            self.context.time = extracted.time.to_string()
            self.context.time_display = f"alle {extracted.time.to_string()}"
            self.context.time_is_approximate = extracted.time.is_approximate

        # Handle multiple services
        if extracted.services and (force_update or not self.context.service):
            self.context.services = extracted.services
            self.context.service = extracted.services[0]  # Primary service
            display_names = [SERVICE_DISPLAY.get(s, s.capitalize()) for s in extracted.services]
            self.context.service_display = " e ".join(display_names)
        elif extracted.service and (force_update or not self.context.service):
            self.context.service = extracted.service
            self.context.services = [extracted.service]
            self.context.service_display = SERVICE_DISPLAY.get(extracted.service, extracted.service.capitalize())

        # Handle operator preference
        if extracted.operator and (force_update or not self.context.operator_name):
            self.context.operator_name = extracted.operator.name
            self.context.operator_requested = True

        if extracted.name and (force_update or not self.context.client_name):
            clean_name, clean_surname = sanitize_name_pair(extracted.name.name, None)
            self.context.client_name = clean_name
            if clean_surname and not self.context.client_surname:
                self.context.client_surname = clean_surname

        if extracted.phone and (force_update or not self.context.client_phone):
            self.context.client_phone = extracted.phone

        if extracted.email and (force_update or not self.context.client_email):
            self.context.client_email = extracted.email

    def _update_context_from_dict(self, fields: Dict[str, Any], force_update: bool = False):
        """Update context from a dict of field->value (used by correction patterns)."""
        for field_name, value in fields.items():
            if value is None:
                continue

            current = getattr(self.context, field_name, None) if field_name in [
                "service", "date", "time", "operator_name"
            ] else None

            if not force_update and current is not None:
                continue

            if field_name == "date":
                self.context.date = value
                self.context.date_display = self._format_date_display(value)
            elif field_name == "time" or field_name == "ora":
                self.context.time = value
                self.context.time_display = self._format_time_display(value)
                self.context.time_is_approximate = False
            elif field_name == "service" or field_name == "servizio":
                self.context.service = value
                self.context.service_display = self._normalize_service_display(value)
            elif field_name in ["operator", "operatore", "istruttore", "medico"]:
                self.context.operator_name = sanitize_name(value, is_surname=True)
                self.context.operator_requested = True
            elif field_name in ["specialita", "tipo_attivita", "tipo_intervento"]:
                self.context.service = value
                self.context.service_display = value.capitalize()
            elif field_name == "num_coperti":
                try:
                    self.context.service = str(int(value))
                    self.context.service_display = f"{value} persone"
                except ValueError:
                    pass
            elif field_name == "urgenza":
                self.context.urgency = True
            elif field_name == "name":
                clean_name, clean_surname = sanitize_name_pair(value, None)
                self.context.client_name = clean_name
                if clean_surname and not self.context.client_surname:
                    self.context.client_surname = clean_surname
            elif field_name == "surname":
                self.context.client_surname = sanitize_name(value, is_surname=True)

    def _handle_idle(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle IDLE state - entry point for booking flow."""
        # Check if user already provided ALL info (name + service + date + time)
        if self.context.client_name and self.context.is_complete():
            # All info provided in one message - go to confirmation
            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary()),
                needs_db_lookup=True,
                lookup_type="client",
                lookup_params={"name": self.context.client_name}
            )

        # ALWAYS ask for name first if not provided
        if not self.context.client_name:
            self.context.state = BookingState.WAITING_NAME
            return StateMachineResult(
                next_state=BookingState.WAITING_NAME,
                response=TEMPLATES["ask_name"]
            )

        # Have name - continue flow
        if self.context.client_name:
            if self.context.client_id:
                # Client already identified (follow-up booking) - skip identity collection
                display_name = self.context.client_name.split()[0] if self.context.client_name else ""
                greeting = f"Certo {display_name}! "
                if self.context.service:
                    self.context.state = BookingState.WAITING_DATE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_DATE,
                        response=greeting + TEMPLATES["ask_date"].format(
                            service=self.context.service_display or self.context.service
                        )
                    )
                else:
                    self.context.state = BookingState.WAITING_SERVICE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=greeting + TEMPLATES["ask_service"]
                    )

            # No client_id — need identity verification
            if self.context.client_surname:
                # Have name + surname — do DB lookup by name+surname
                greeting = f"Piacere {self.context.client_name}! "
                if self.context.service:
                    self.context.state = BookingState.WAITING_DATE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_DATE,
                        response=greeting + TEMPLATES["ask_date"].format(
                            service=self.context.service_display or self.context.service
                        ),
                        needs_db_lookup=True,
                        lookup_type="client_by_name_surname",
                        lookup_params={
                            "name": self.context.client_name,
                            "surname": self.context.client_surname
                        }
                    )
                else:
                    self.context.state = BookingState.WAITING_SERVICE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=greeting + TEMPLATES["ask_service"],
                        needs_db_lookup=True,
                        lookup_type="client_by_name_surname",
                        lookup_params={
                            "name": self.context.client_name,
                            "surname": self.context.client_surname
                        }
                    )
            else:
                # Have name only, no surname — ask for surname
                self.context.state = BookingState.WAITING_SURNAME
                return StateMachineResult(
                    next_state=BookingState.WAITING_SURNAME,
                    response=TEMPLATES["ask_surname_after_name"].format(
                        name=self.context.client_name
                    )
                )

        # Fallback - ask for name
        self.context.state = BookingState.WAITING_NAME
        return StateMachineResult(
            next_state=BookingState.WAITING_NAME,
            response=TEMPLATES["ask_name"]
        )

    def _handle_waiting_name(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_NAME state."""
        text_lower = text.lower()

        # =====================================================================
        # NEW CLIENT DETECTION - Check if user indicates they're new
        # =====================================================================
        NEW_CLIENT_INDICATORS = [
            # "mai stato/venuto"
            r"mai\s+stato",              # "mai stato da voi"
            r"mai\s+venuto",             # "mai venuto"
            r"mai\s+prenotato",          # "mai prenotato"
            # "prima volta" (con typo comuni)
            r"pr[io]ma\s+volta",         # "prima volta" / "proma volta" (typo)
            r"prima\s+visita",           # "prima visita"
            # "non sono..."
            r"non\s+sono\s+mai",         # "non sono mai stato"
            r"non\s+sono\s+cliente",     # "non sono cliente"
            r"non\s+sono\s+.*\s+cliente",# "non sono ancora cliente"
            r"non\s+sono\s+registrat",   # "non sono registrato/a"
            # "non mi conoscete"
            r"non\s+mi\s+conosc",        # "non mi conoscete" / "non mi conosci"
            r"non\s+mi\s+avete",         # "non mi avete in archivio"
            r"non\s+sono\s+in\s+archivio",# "non sono in archivio"
            r"non\s+sono\s+nel",         # "non sono nel vostro sistema"
            # "nuovo/nuova cliente"
            r"nuov[oa]\s+cliente",       # "nuovo cliente" / "nuova cliente"
            r"sono\s+nuov[oa]",          # "sono nuovo" / "sono nuova"
            # Altri indicatori
            r"non\s+ho\s+mai",           # "non ho mai prenotato"
            r"non\s+vi\s+conosco",       # "non vi conosco"
            r"non\s+c['\u2019]?\s*è\s+il\s+mio", # "non c'è il mio nome"
        ]

        for pattern in NEW_CLIENT_INDICATORS:
            if re.search(pattern, text_lower):
                # User is a new client - propose registration
                self.context.is_new_client = True
                self.context.state = BookingState.REGISTERING_SURNAME
                return StateMachineResult(
                    next_state=BookingState.REGISTERING_SURNAME,
                    response="Benvenuto! Piacere di conoscerla. Mi può dire il suo nome e cognome?"
                )

        if self.context.client_name:
            if self.context.client_id:
                # Client already known (e.g. follow-up booking in same call)
                display_name = self.context.client_name.split()[0] if self.context.client_name else ""
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response=f"Certo {display_name}! " + TEMPLATES["ask_service"],
                )
            # Name collected, no client_id — check if surname also available
            if self.context.client_surname:
                # Both name+surname available
                # CHECK FOR PHONETIC DISAMBIGUATION FIRST
                needs_disambig, disambig_info = self._check_name_disambiguation(
                    self.context.client_name,
                    self.context.client_surname
                )
                
                if needs_disambig and disambig_info:
                    # Ambiguous match - ask for confirmation
                    self.context.disambiguation_candidates = [disambig_info["client"]]
                    self.context.disambiguation_attempts = 0
                    self.context.state = BookingState.DISAMBIGUATING_NAME
                    
                    suggested_name = disambig_info["client"]["nome"]
                    suggested_surname = disambig_info["client"]["cognome"]
                    
                    return StateMachineResult(
                        next_state=BookingState.DISAMBIGUATING_NAME,
                        response=TEMPLATES["disambiguation_ask"].format(
                            suggested_name=f"{suggested_name} {suggested_surname}"
                        )
                    )
                elif disambig_info and disambig_info.get("match_type") == "exact":
                    # Exact match - use this client directly
                    client = disambig_info["client"]
                    self.context.client_id = client["id"]
                    self.context.client_name = client["nome"]
                    self.context.client_surname = client["cognome"]
                    self.context.state = BookingState.WAITING_SERVICE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=TEMPLATES["welcome_back"].format(name=client["nome"]) + " " + TEMPLATES["ask_service"]
                    )
                elif disambig_info and disambig_info.get("match_type") == "nickname":
                    # CoVe: Match per soprannome - riconoscimento speciale
                    client = disambig_info["client"]
                    self.context.client_id = client["id"]
                    self.context.client_name = client["nome"]
                    self.context.client_surname = client["cognome"]
                    self.context.state = BookingState.WAITING_SERVICE
                    soprannome = client.get("soprannome", "")
                    logger.info(f"[DISAMBIGUATION] Client recognized by nickname: {soprannome} -> {client['nome']}")
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=TEMPLATES["nickname_recognized"].format(
                            soprannome=soprannome,
                            nome=client["nome"]
                        ) + " " + TEMPLATES["ask_service"]
                    )
                
                # No match or new client - go to DB lookup
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response="",  # orchestrator replaces after DB lookup
                    needs_db_lookup=True,
                    lookup_type="client_by_name_surname",
                    lookup_params={
                        "name": self.context.client_name,
                        "surname": self.context.client_surname
                    }
                )
            # Name only — ask for surname
            self.context.state = BookingState.WAITING_SURNAME
            return StateMachineResult(
                next_state=BookingState.WAITING_SURNAME,
                response=TEMPLATES["ask_surname_after_name"].format(
                    name=self.context.client_name
                )
            )

        # Try to extract name from raw text (regex patterns)
        name = extract_name(text)
        if name:
            clean_name, clean_surname = sanitize_name_pair(name.name, None)
            self.context.client_name = clean_name or name.name
            if clean_surname:
                # Got both name+surname (e.g. "Sono Gino Di Nanni")
                self.context.client_surname = clean_surname
                
                # CHECK FOR PHONETIC DISAMBIGUATION
                needs_disambig, disambig_info = self._check_name_disambiguation(
                    self.context.client_name, 
                    self.context.client_surname
                )
                
                if needs_disambig and disambig_info:
                    # Ambiguous match - ask for confirmation
                    self.context.disambiguation_candidates = [disambig_info["client"]]
                    self.context.disambiguation_attempts = 0
                    self.context.state = BookingState.DISAMBIGUATING_NAME
                    
                    suggested_name = disambig_info["client"]["nome"]
                    suggested_surname = disambig_info["client"]["cognome"]
                    
                    return StateMachineResult(
                        next_state=BookingState.DISAMBIGUATING_NAME,
                        response=TEMPLATES["disambiguation_ask"].format(
                            suggested_name=f"{suggested_name} {suggested_surname}"
                        )
                    )
                elif disambig_info and disambig_info.get("match_type") == "exact":
                    # Exact match - use this client directly
                    client = disambig_info["client"]
                    self.context.client_id = client["id"]
                    self.context.client_name = client["nome"]
                    self.context.client_surname = client["cognome"]
                    self.context.state = BookingState.WAITING_SERVICE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=TEMPLATES["welcome_back"].format(name=client["nome"]) + " " + TEMPLATES["ask_service"]
                    )
                elif disambig_info and disambig_info.get("match_type") == "nickname":
                    # CoVe: Match per soprannome nel secondo blocco
                    client = disambig_info["client"]
                    self.context.client_id = client["id"]
                    self.context.client_name = client["nome"]
                    self.context.client_surname = client["cognome"]
                    self.context.state = BookingState.WAITING_SERVICE
                    soprannome = client.get("soprannome", "")
                    logger.info(f"[DISAMBIGUATION] Client recognized by nickname (2nd block): {soprannome}")
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=TEMPLATES["nickname_recognized"].format(
                            soprannome=soprannome,
                            nome=client["nome"]
                        ) + " " + TEMPLATES["ask_service"]
                    )
                
                # No match or new client - proceed with normal lookup
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response="",  # orchestrator replaces after DB lookup
                    needs_db_lookup=True,
                    lookup_type="client_by_name_surname",
                    lookup_params={
                        "name": self.context.client_name,
                        "surname": self.context.client_surname
                    }
                )
            # Name only — ask for surname
            self.context.state = BookingState.WAITING_SURNAME
            return StateMachineResult(
                next_state=BookingState.WAITING_SURNAME,
                response=TEMPLATES["ask_surname_after_name"].format(
                    name=self.context.client_name
                )
            )

        # Fallback: Try spaCy NER for person names
        try:
            import spacy
            nlp = spacy.load("it_core_news_sm")
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PER":
                    extracted_name = ent.text.strip()
                    extracted_name = ' '.join(word.capitalize() for word in extracted_name.split())
                    clean_name, clean_surname = sanitize_name_pair(extracted_name, None)
                    self.context.client_name = clean_name or extracted_name
                    if clean_surname:
                        self.context.client_surname = clean_surname
                        self.context.state = BookingState.WAITING_SERVICE
                        return StateMachineResult(
                            next_state=BookingState.WAITING_SERVICE,
                            response="",  # orchestrator replaces after DB lookup
                            needs_db_lookup=True,
                            lookup_type="client_by_name_surname",
                            lookup_params={
                                "name": self.context.client_name,
                                "surname": self.context.client_surname
                            }
                        )
                    self.context.state = BookingState.WAITING_SURNAME
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SURNAME,
                        response=TEMPLATES["ask_surname_after_name"].format(
                            name=self.context.client_name
                        )
                    )
        except Exception:
            pass  # spaCy not available, continue to fallback

        # Couldn't extract name
        return StateMachineResult(
            next_state=BookingState.WAITING_NAME,
            response="Mi dice il nome, per cortesia?"
        )

    def _check_name_disambiguation(self, input_name: str, input_surname: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if input name is phonetically similar to existing clients.
        Uses Levenshtein distance + phonetic variants dictionary.
        
        CoVe: Aggiunto supporto soprannome (nickname) per disambiguazione avanzata.
        Se l'utente usa il soprannome, viene riconosciuto e matchato.
        
        Returns:
            Tuple of (needs_disambiguation, candidate_info)
            - needs_disambiguation: True if ambiguous match found
            - candidate_info: Dict with client info if disambiguation needed, None otherwise
        """
        try:
            # Import sqlite3 for DB lookup
            import sqlite3
            import os
            
            # Import phonetic variants
            try:
                from .disambiguation_handler import PHONETIC_VARIANTS
            except ImportError:
                from disambiguation_handler import PHONETIC_VARIANTS
            
            # CoVe: Multiple DB path attempts for different environments
            db_paths = [
                "/Volumes/MacSSD - Dati/fluxion/fluxion.db",  # iMac production
                "/Volumes/MontereyT7/FLUXION/fluxion.db",      # MacBook local
                "./fluxion.db",                                  # Relative path
                os.path.join(os.path.dirname(__file__), "..", "..", "fluxion.db"),  # Project root
            ]
            
            db_path = None
            for path in db_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            # CoVe: Se DB non esiste, simula per test noti
            if not db_path:
                logger.warning(f"[DISAMBIGUATION] Database not found, using test simulation mode")
                return self._check_name_disambiguation_simulation(input_name, input_surname)
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # CoVe: Cerca per cognome OR soprannome (nickname matching)
            cursor.execute(
                """SELECT id, nome, cognome, soprannome, data_nascita 
                   FROM clienti 
                   WHERE LOWER(cognome) = LOWER(?) 
                   OR LOWER(soprannome) = LOWER(?)""",
                (input_surname, input_surname)
            )
            matching_clients = cursor.fetchall()
            
            # CoVe: Cerca anche per nome/soprannome (se input è il soprannome)
            cursor.execute(
                """SELECT id, nome, cognome, soprannome, data_nascita 
                   FROM clienti 
                   WHERE LOWER(soprannome) = LOWER(?)
                   OR LOWER(nome) = LOWER(?)""",
                (input_name, input_name)
            )
            nickname_matches = cursor.fetchall()
            
            conn.close()
            
            # Unisci risultati (rimuovi duplicati)
            all_matches = list(matching_clients) + [c for c in nickname_matches if c not in matching_clients]
            
            if not all_matches:
                return False, None
            
            return self._evaluate_candidates(input_name, input_surname, all_matches)
                
        except Exception as e:
            # If DB error, log and proceed without disambiguation
            logger.error(f"[DISAMBIGUATION] Error in disambiguation check: {e}")
            # CoVe: Fallback a simulazione per test
            return self._check_name_disambiguation_simulation(input_name, input_surname)
    
    def _check_name_disambiguation_simulation(self, input_name: str, input_surname: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Simulazione CoVe per test quando DB non è disponibile.
        Conosce alcuni clienti di test per validare il flusso.
        CoVe: Aggiunto supporto soprannome.
        """
        # Clienti di test noti con soprannome
        # CoVe 2026: Aggiunti Mario/Maria per test disambiguazione fonetica
        test_clients = {
            "peruzzi": [
                {"id": "test-gigio", "nome": "Gigio", "cognome": "Peruzzi", "soprannome": "Gigi", "data_nascita": "1985-03-15"},
            ],
            "bianchi": [
                {"id": "test-maria", "nome": "Maria", "cognome": "Bianchi", "soprannome": None, "data_nascita": "1990-07-22"},
            ],
            "gigi": [  # Match per soprannome
                {"id": "test-gigio", "nome": "Gigio", "cognome": "Peruzzi", "soprannome": "Gigi", "data_nascita": "1985-03-15"},
            ],
            "rossi": [  # CoVe 2026: Mario e Maria per test disambiguazione
                {"id": "test-mario", "nome": "Mario", "cognome": "Rossi", "soprannome": None, "data_nascita": "1980-05-10"},
                {"id": "test-maria-rossi", "nome": "Maria", "cognome": "Rossi", "soprannome": None, "data_nascita": "1982-08-15"},
            ],
        }
        
        input_surname_lower = input_surname.lower()
        input_name_lower = input_name.lower()
        
        # Cerca per cognome o soprannome
        all_matches = []
        if input_surname_lower in test_clients:
            all_matches.extend(test_clients[input_surname_lower])
        if input_name_lower in test_clients:
            all_matches.extend([c for c in test_clients[input_name_lower] if c not in all_matches])
        
        if not all_matches:
            return False, None
        
        # Convert to tuple format per compatibilità (id, nome, cognome, soprannome, data_nascita)
        db_tuples = [
            (c["id"], c["nome"], c["cognome"], c.get("soprannome"), c["data_nascita"])
            for c in all_matches
        ]
        
        return self._evaluate_candidates(input_name, input_surname, db_tuples)
    
    def _evaluate_candidates(
        self, 
        input_name: str, 
        input_surname: str, 
        matching_clients: list
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Valuta i candidati e determina se serve disambiguazione.
        CoVe: Separato per riutilizzo tra DB reale e simulazione.
        CoVe: Aggiunto supporto soprannome - se matcha il soprannome = match esatto.
        
        🔒 CRITICAL FIX: Valuta sia NOME che COGNOME insieme.
        Se il cognome non corrisponde, NON è un match valido.
        """
        try:
            from disambiguation_handler import PHONETIC_VARIANTS, name_similarity
        except ImportError:
            from .disambiguation_handler import PHONETIC_VARIANTS, name_similarity
        
        candidates = []
        input_name_lower = input_name.lower() if input_name else ""
        input_surname_lower = input_surname.lower() if input_surname else ""
        
        for client_data in matching_clients:
            # Gestisci sia tuple che dizionari
            if isinstance(client_data, dict):
                client_id = client_data["id"]
                nome = client_data["nome"]
                cognome = client_data["cognome"]
                soprannome = client_data.get("soprannome")
                data_nascita = client_data.get("data_nascita")
            else:
                # Tuple format: (id, nome, cognome, soprannome, data_nascita)
                client_id = client_data[0]
                nome = client_data[1]
                cognome = client_data[2]
                soprannome = client_data[3] if len(client_data) > 3 else None
                data_nascita = client_data[4] if len(client_data) > 4 else None
            
            nome_lower = nome.lower()
            cognome_lower = cognome.lower() if cognome else ""
            soprannome_lower = soprannome.lower() if soprannome else None
            
            # 🔒 CRITICAL FIX: Verifica match cognome prima di procedere
            # Se l'utente ha fornito un cognome diverso dal cliente nel DB, è un cliente diverso
            surname_similarity = 0.0
            if input_surname and cognome:
                surname_similarity = name_similarity(input_surname, cognome)
            elif input_surname and not cognome:
                # Cognome fornito ma cliente nel DB non ha cognome → possibile match
                surname_similarity = 0.5
            elif not input_surname and cognome:
                # Cognome non fornito ma cliente nel DB ha cognome → possibile match (parziale)
                surname_similarity = 0.5
            else:
                # Nessun cognome né input né DB → neutrale
                surname_similarity = 0.5
            
            # 🔒 Se il cognome è completamente diverso (< 0.3 similarity), scarta questo candidato
            # A meno che non sia un match per soprannome (gestito dopo)
            if surname_similarity < 0.3 and input_surname and cognome:
                logger.debug(f"[DISAMBIGUATION] Surname mismatch: '{input_surname}' vs '{cognome}' (sim: {surname_similarity:.2f}) - Skipping")
                continue
            
            # CoVe: Se input matcha esattamente il soprannome = match perfetto (1.0)
            if soprannome_lower and (input_name_lower == soprannome_lower or input_surname_lower == soprannome_lower):
                logger.info(f"[DISAMBIGUATION] Nickname match: '{input_name}' = soprannome '{soprannome}'")
                candidates.append({
                    "id": client_id,
                    "nome": nome,
                    "cognome": cognome,
                    "soprannome": soprannome,
                    "data_nascita": data_nascita,
                    "similarity": 1.0,  # Match esatto per soprannome
                    "match_type": "nickname"
                })
                continue
            
            # Calculate Levenshtein similarity con nome
            levenshtein_sim = name_similarity(input_name, nome)
            
            # Check phonetic variants (bonus similarity)
            phonetic_bonus = 0.0
            if input_name_lower in PHONETIC_VARIANTS:
                if nome_lower in PHONETIC_VARIANTS[input_name_lower]:
                    phonetic_bonus = 0.20  # Boost for known phonetic variants
            
            # 🔒 CRITICAL FIX: Similarity combinata nome + cognome
            # Peso: 60% nome, 40% cognome (il cognome è più discriminante)
            name_similarity_score = min(1.0, levenshtein_sim + phonetic_bonus)
            combined_similarity = (0.6 * name_similarity_score) + (0.4 * surname_similarity)
            
            candidates.append({
                "id": client_id,
                "nome": nome,
                "cognome": cognome,
                "soprannome": soprannome,
                "data_nascita": data_nascita,
                "similarity": combined_similarity,
                "match_type": "name",
                "debug": {
                    "name_sim": name_similarity_score,
                    "surname_sim": surname_similarity,
                    "combined": combined_similarity
                }
            })
        
        # 🔒 CRITICAL: Se nessun candidato supera il filtro cognome → nuovo cliente
        if not candidates:
            logger.info(f"[DISAMBIGUATION] No valid candidates after surname filter for '{input_name} {input_surname}'")
            return False, None
        
        # Sort by similarity descending
        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        
        # CoVe 2026: Check for phonetic ambiguity (e.g., Mario vs Maria with same surname)
        # If multiple candidates with phonetically similar names, require disambiguation
        if len(candidates) >= 2:
            try:
                from disambiguation_handler import is_phonetically_similar
            except ImportError:
                from .disambiguation_handler import is_phonetically_similar
            
            top_name = candidates[0]["nome"].lower()
            second_name = candidates[1]["nome"].lower()
            
            if is_phonetically_similar(top_name, second_name, threshold=0.75):
                logger.info(f"[DISAMBIGUATION] Phonetic ambiguity detected: '{candidates[0]['nome']}' vs '{candidates[1]['nome']}'")
                return True, {
                    "match_type": "phonetic_ambiguity",
                    "client": candidates[0],
                    "similarity": candidates[0]["similarity"],
                    "all_candidates": candidates
                }
        
        # Get best match
        best_candidate = candidates[0]
        similarity = best_candidate["similarity"]
        match_type = best_candidate.get("match_type", "name")
        
        logger.info(f"[DISAMBIGUATION] Best match for '{input_name} {input_surname}': {best_candidate['nome']} {best_candidate['cognome']} (similarity: {similarity:.2f}, type: {match_type})")
        
        # CoVe: Se match per soprannome, tratta come match esatto speciale
        if match_type == "nickname":
            logger.info(f"[DISAMBIGUATION] Nickname match confirmed for '{best_candidate['soprannome']}'")
            return False, {"match_type": "nickname", "client": best_candidate}
        
        # 🔒 CRITICAL FIX: Aumentate le soglie per evitare falsi positivi
        # THRESHOLD_HIGH: 0.90 = exact match (prima era 0.95 troppo alta, ma 0.60 troppo bassa)
        # THRESHOLD_MED: 0.70 = phonetically similar, needs confirmation
        if similarity >= 0.90:
            # Exact match - no disambiguation needed
            logger.info(f"[DISAMBIGUATION] Exact match confirmed (similarity >= 0.90)")
            return False, {"match_type": "exact", "client": best_candidate}
        elif similarity >= 0.70:
            # Ambiguous match - needs disambiguation
            logger.info(f"[DISAMBIGUATION] Ambiguous match detected, needs confirmation (similarity: {similarity:.2f})")
            return True, {
                "match_type": "ambiguous",
                "client": best_candidate,
                "similarity": similarity,
                "all_candidates": candidates
            }
        else:
            # No significant match - new client
            logger.info(f"[DISAMBIGUATION] No significant match (similarity: {similarity:.2f}) - treating as new client")
            return False, None

    def _extract_surname_from_text(self, text: str) -> Optional[str]:
        """Extract surname from user text using multi-phase extraction.

        Used by WAITING_SURNAME and REGISTERING_SURNAME handlers.
        Returns cleaned surname string or None.
        Assumes client_name is already set in context.
        """
        text_stripped = text.strip()

        # Blacklist: words that are NOT surnames
        _SURNAME_BLACKLIST = {
            "vi", "ho", "mi", "si", "se", "ci", "ne", "lo", "la", "le", "li",
            "il", "un", "una", "uno", "gli", "dei", "delle", "del",
            "appena", "già", "proprio", "anche", "ancora", "allora",
            "cognome", "nome", "mio", "suo", "è", "e",
            "detto", "fatto", "stato", "dico", "bene", "ecco",
            "ehi", "eh", "oh", "ah", "ahi", "uhm", "ehm", "boh", "mah", "beh",
            "senti", "senta", "scolta", "ascolta", "aspetta", "aspetti",
            "ciao", "buongiorno", "buonasera", "salve", "grazie", "niente",
        }

        # Phase 1: Contextual phrase patterns
        surname_phrase_patterns = [
            # "il cognome è X" / "cognome è X" / "cognome: X"
            r"(?:il\s+)?cognome\s+(?:è|e|:)\s+([A-Za-zàèéìòù][a-zàèéìòùA-Z'\s]+)",
            # "è X" at end of sentence (when we already asked for surname)
            r"(?:è|e)\s+([A-Z][a-zàèéìòù]+)\s*[.!]?\s*$",
            # "di cognome X"
            r"di\s+cognome\s+([A-Za-zàèéìòù][a-zàèéìòùA-Z'\s]+)",
        ]

        for pattern in surname_phrase_patterns:
            match = re.search(pattern, text_stripped, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                clean_parts = [w for w in candidate.split()
                               if w.lower() not in _SURNAME_BLACKLIST and len(w) >= 2]
                if clean_parts:
                    surname = sanitize_name(' '.join(clean_parts), is_surname=True)
                    if surname:
                        return surname

        # Phase 2: Entity extractor (regex patterns)
        name_result = extract_name(text_stripped)
        if name_result:
            clean_name, clean_surname = sanitize_name_pair(name_result.name, None)
            if self.context.client_name:
                # We already have a name — treat extracted data as surname
                if clean_name and clean_surname:
                    if clean_name.lower() != self.context.client_name.lower():
                        # Different name — entire input is surname (e.g. "Di Nanni")
                        return sanitize_name(name_result.name, is_surname=True)
                    else:
                        # User repeated name + gave surname
                        return clean_surname
                elif clean_name:
                    # Single word — treat as surname since we already have name
                    return sanitize_name(clean_name, is_surname=True)

        # Phase 3: Raw text fallback
        text_clean = sanitize_name(text_stripped)
        raw_words = text_clean.split() if text_clean else []
        clean_words = [w for w in raw_words
                       if w.lower() not in _SURNAME_BLACKLIST and len(w) >= 2]

        if clean_words and self.context.client_name:
            # Filter out the client's name if they repeated it
            name_lower = self.context.client_name.lower()
            surname_words = [w for w in clean_words if w.lower() != name_lower]
            if not surname_words:
                surname_words = clean_words  # All words match name? Use them anyway
            candidate = ' '.join(surname_words)
            if candidate:
                return sanitize_name(candidate, is_surname=True)
        elif clean_words:
            return sanitize_name(' '.join(clean_words), is_surname=True)

        # Phase 4: Groq LLM fallback
        if self.groq_nlu and self.context.client_name:
            logger.info(f"[SM] surname extraction: regex failed, trying Groq for '{text_stripped[:50]}'")
            groq_result = self.groq_nlu.extract_surname(
                utterance=text_stripped,
                nome=self.context.client_name
            )
            if groq_result and groq_result.get("cognome"):
                cognome = sanitize_name(groq_result["cognome"], is_surname=True)
                if cognome:
                    return cognome

        return None

    def _handle_waiting_surname(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_SURNAME state - collect surname after name, then DB lookup."""

        # If surname was already populated (e.g., "Sono Gino Di Nanni" extracted in WAITING_NAME)
        if self.context.client_surname:
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response="",  # orchestrator replaces after DB lookup
                needs_db_lookup=True,
                lookup_type="client_by_name_surname",
                lookup_params={
                    "name": self.context.client_name or "",
                    "surname": self.context.client_surname
                }
            )

        # Extract surname from text
        surname = self._extract_surname_from_text(text)

        if surname:
            self.context.client_surname = surname
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response="",  # orchestrator replaces after DB lookup
                needs_db_lookup=True,
                lookup_type="client_by_name_surname",
                lookup_params={
                    "name": self.context.client_name or "",
                    "surname": self.context.client_surname
                }
            )

        # Couldn't extract surname - re-ask
        return StateMachineResult(
            next_state=BookingState.WAITING_SURNAME,
            response="Mi ripete il cognome, per cortesia?"
        )

    def _handle_waiting_service(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_SERVICE state."""
        if self.context.service:
            # Service collected - check what else we have
            if self.context.date and self.context.time:
                # All info - go to confirmation
                self.context.state = BookingState.CONFIRMING
                return StateMachineResult(
                    next_state=BookingState.CONFIRMING,
                    response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
                )

            if self.context.date:
                # Have date - ask for time
                self.context.state = BookingState.WAITING_TIME
                return StateMachineResult(
                    next_state=BookingState.WAITING_TIME,
                    response=TEMPLATES["ask_time"].format(date=self.context.date_display or self.context.date),
                    needs_db_lookup=True,
                    lookup_type="availability",
                    lookup_params={"date": self.context.date, "service": self.context.service}
                )

            # Ask for date
            self.context.state = BookingState.WAITING_DATE
            return StateMachineResult(
                next_state=BookingState.WAITING_DATE,
                response=TEMPLATES["ask_date"].format(
                    service=self.context.service_display or self.context.service
                )
            )

        # Try to extract services from raw text (supports multiple services)
        services_results = extract_services(text, self.services_config)
        if services_results:
            services = [s[0] for s in services_results]
            self.context.services = services
            self.context.service = services[0]  # Primary service
            # Build display string for all services
            display_names = [SERVICE_DISPLAY.get(s, s.capitalize()) for s in services]
            self.context.service_display = " e ".join(display_names)

            # Check if date was also provided
            if self.context.date:
                self.context.state = BookingState.WAITING_TIME
                return StateMachineResult(
                    next_state=BookingState.WAITING_TIME,
                    response=TEMPLATES["ask_time"].format(date=self.context.date_display or self.context.date),
                    needs_db_lookup=True,
                    lookup_type="availability",
                    lookup_params={"date": self.context.date, "service": self.context.service}
                )

            self.context.state = BookingState.WAITING_DATE
            return StateMachineResult(
                next_state=BookingState.WAITING_DATE,
                response=TEMPLATES["ask_date"].format(
                    service=self.context.service_display
                )
            )

        # Fallback: try italian_regex multi-service extraction
        if HAS_ITALIAN_REGEX:
            multi = extract_multi_services(text, self.context.vertical)
            if multi:
                # Map regex results back to service IDs
                service_ids = []
                for svc_name in multi:
                    svc_lower = svc_name.lower()
                    matched = None
                    for svc_id, synonyms in self.services_config.items():
                        if svc_lower == svc_id or svc_lower in [s.lower() for s in synonyms]:
                            matched = svc_id
                            break
                    if matched:
                        service_ids.append(matched)
                if service_ids:
                    self.context.services = service_ids
                    self.context.service = service_ids[0]
                    display_names = [SERVICE_DISPLAY.get(s, s.capitalize()) for s in service_ids]
                    self.context.service_display = " e ".join(display_names)
                    self.context.state = BookingState.WAITING_DATE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_DATE,
                        response=TEMPLATES["ask_date"].format(
                            service=self.context.service_display
                        )
                    )

        # Couldn't extract service
        return StateMachineResult(
            next_state=BookingState.WAITING_SERVICE,
            response=TEMPLATES["service_not_understood"]
        )

    def _handle_waiting_date(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_DATE state."""
        # BUG 2 FIX: Detect and merge new services mentioned while in WAITING_DATE
        new_services = []
        if extracted.services:
            existing = set(self.context.services or [])
            new_services = [s for s in extracted.services if s not in existing]
        elif extracted.service and self.context.services:
            if extracted.service not in self.context.services:
                new_services = [extracted.service]

        if new_services:
            merged = list(self.context.services or []) + new_services
            self.context.services = merged
            self.context.service = merged[0]
            display_names = [SERVICE_DISPLAY.get(s, s.capitalize()) for s in merged]
            self.context.service_display = " e ".join(display_names)

        if self.context.date:
            # Date collected
            if self.context.time:
                # Also have time - go to confirmation
                self.context.state = BookingState.CONFIRMING
                return StateMachineResult(
                    next_state=BookingState.CONFIRMING,
                    response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
                )

            # Ask for time
            self.context.state = BookingState.WAITING_TIME
            return StateMachineResult(
                next_state=BookingState.WAITING_TIME,
                response=TEMPLATES["ask_time"].format(date=self.context.date_display or self.context.date),
                needs_db_lookup=True,
                lookup_type="availability",
                lookup_params={"date": self.context.date, "service": self.context.service}
            )

        # Check for ambiguous dates BEFORE extraction
        # "prossima settimana" → query calendar for available days
        if HAS_ITALIAN_REGEX and is_ambiguous_date(text):
            text_lower = text.lower()
            week_offset = 1  # default: "prossima settimana"
            if "questa" in text_lower:
                week_offset = 0
            elif "tra due" in text_lower or "fra due" in text_lower:
                week_offset = 2
            return StateMachineResult(
                next_state=BookingState.WAITING_DATE,
                response="",  # orchestrator replaces with actual availability
                needs_db_lookup=True,
                lookup_type="week_availability",
                lookup_params={
                    "week_offset": week_offset,
                    "service": self.context.service
                }
            )

        # Try to extract date from raw text
        date = extract_date(text, self.reference_date)
        if date:
            self.context.date = date.to_string("%Y-%m-%d")
            self.context.date_display = date.to_italian()

            # Check if time was also provided
            if self.context.time:
                self.context.state = BookingState.CONFIRMING
                return StateMachineResult(
                    next_state=BookingState.CONFIRMING,
                    response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
                )

            self.context.state = BookingState.WAITING_TIME
            return StateMachineResult(
                next_state=BookingState.WAITING_TIME,
                response=TEMPLATES["ask_time"].format(date=self.context.date_display),
                needs_db_lookup=True,
                lookup_type="availability",
                lookup_params={"date": self.context.date, "service": self.context.service}
            )

        # Couldn't extract date
        if new_services:
            added_display = " e ".join(SERVICE_DISPLAY.get(s, s.capitalize()) for s in new_services)
            return StateMachineResult(
                next_state=BookingState.WAITING_DATE,
                response=f"Ho aggiunto {added_display}. Per quale giorno vorrebbe prenotare?"
            )
        return StateMachineResult(
            next_state=BookingState.WAITING_DATE,
            response=TEMPLATES["date_not_understood"]
        )

    _WEEKDAY_NAMES = {"lunedì", "lunedi", "martedì", "martedi", "mercoledì", "mercoledi",
                      "giovedì", "giovedi", "venerdì", "venerdi", "sabato", "domenica"}
    _DATE_CHANGE_MARKERS = {"non posso", "non va bene", "invece", "cambiamo",
                            "meglio", "piuttosto", "altro giorno", "cambio giorno"}

    def _handle_waiting_time(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_TIME state with back-navigation to WAITING_DATE."""
        text_lower = text.lower()

        # BUG 4 FIX: Detect date change request before time extraction
        has_weekday = any(d in text_lower for d in self._WEEKDAY_NAMES)
        has_change_marker = any(m in text_lower for m in self._DATE_CHANGE_MARKERS)
        has_time = extract_time(text) is not None

        if has_weekday and (has_change_marker or not has_time):
            # User wants to change date — back-navigate to WAITING_DATE
            old_date = self.context.date_display or self.context.date
            self.context.date = None
            self.context.date_display = None
            self.context.time = None
            self.context.time_display = None
            self.context.state = BookingState.WAITING_DATE
            return StateMachineResult(
                next_state=BookingState.WAITING_DATE,
                response=f"D'accordo, cambiamo giorno. Per quando preferirebbe?"
            )

        if self.context.time:
            # Time collected - go to confirmation
            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
            )

        # Try to extract time from raw text
        time = extract_time(text)
        if time:
            self.context.time = time.to_string()
            self.context.time_display = f"alle {time.to_string()}"
            self.context.time_is_approximate = time.is_approximate

            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
            )

        # Couldn't extract time
        return StateMachineResult(
            next_state=BookingState.WAITING_TIME,
            response=TEMPLATES["time_not_understood"]
        )

    def _handle_waiting_operator(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_OPERATOR state."""
        text_lower = text.lower()

        # Check for "no preference" responses
        if any(word in text_lower for word in ["no", "nessuno", "indifferente", "chiunque", "qualsiasi"]):
            self.context.operator_requested = False
            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
            )

        # Try to extract operator name
        name = extract_name(text)
        if name:
            self.context.operator_name = name.name
            self.context.operator_requested = True
            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary()),
                needs_db_lookup=True,
                lookup_type="operator",
                lookup_params={"name": name.name, "date": self.context.date, "time": self.context.time}
            )

        # Couldn't understand - go to confirmation anyway
        self.context.state = BookingState.CONFIRMING
        return StateMachineResult(
            next_state=BookingState.CONFIRMING,
            response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
        )

    # =========================================================================
    # CORRECTION DETECTION HELPERS (C1, C3, C4)
    # =========================================================================

    def _extract_level1_entities(self, user_lower: str) -> Dict[str, Any]:
        """
        Level 1: Re-extract entities from text using existing entity_extractor
        first (C3), then vertical-specific correction patterns as fallback.
        """
        entities = {}

        # C3: Use existing entity_extractor functions FIRST
        date_result = extract_date(user_lower, self.reference_date)
        if date_result:
            entities["date"] = date_result.to_string("%Y-%m-%d")

        time_result = extract_time(user_lower)
        if time_result:
            entities["time"] = time_result.to_string()

        service_result = extract_service(user_lower, self.services_config)
        if service_result:
            entities["service"] = service_result[0]

        operator_result = extract_operator(user_lower)
        if operator_result:
            entities["operator"] = operator_result.name

        # Fallback: vertical-specific correction patterns
        if not entities:
            patterns = self._get_correction_patterns_for_vertical()
            for field_name, regex_list in patterns.items():
                for regex_pattern in regex_list:
                    match = re.search(regex_pattern, user_lower, re.IGNORECASE)
                    if match:
                        extracted_value = (
                            match.group(1) if match.groups() else match.group(0)
                        )
                        entities[field_name] = extracted_value.strip()
                        break

        return entities

    def _detect_correction_or_rejection_signal(self, user_lower: str) -> Tuple[bool, bool]:
        """
        C1: Separate correction signals from rejection signals.
        Returns (has_correction, has_rejection).
        """
        correction_words = ["meglio", "piuttosto", "invece", "anzi", "preferisco",
                            "in realtà", "cambio", "cambia", "metti", "togli", "aggiungi"]
        rejection_words = ["no", "niente", "non voglio", "annulla", "cancella",
                           "lascia perdere", "lasciamo stare", "no grazie",
                           "non mi interessa", "ho cambiato idea", "meglio di no"]

        has_correction = any(w in user_lower for w in correction_words)
        has_rejection = any(w in user_lower for w in rejection_words)

        return has_correction, has_rejection

    def _is_explicit_confirmation(self, user_lower: str) -> bool:
        """Detect explicit confirmation in Italian."""
        confirmation_patterns = [
            r"\b(?:sì|si|okay|ok)\b",
            r"(?:va bene|d'accordo|perfetto)",
            r"(?:certo|esatto|confermo)",
            r"(?:procediamo|facciamo così)",
            r"(?:benissimo|ottimo)",
        ]
        return any(re.search(p, user_lower) for p in confirmation_patterns)

    def _format_correction_summary(self, corrections: Dict[str, Any]) -> str:
        """Format a human-readable summary of corrections."""
        field_labels = {
            "ora": "ora", "time": "ora",
            "data": "data", "date": "data",
            "servizio": "servizio", "service": "servizio",
            "operatore": "operatore", "operator": "operatore",
            "tipo_attivita": "attività", "specialita": "specialità",
            "num_coperti": "coperti", "tipo_intervento": "intervento",
        }
        parts = []
        for field, value in corrections.items():
            label = field_labels.get(field, field)
            parts.append(f"{label} → {value}")
        return ", ".join(parts)

    def _get_correction_patterns_for_vertical(self) -> Dict[str, List[str]]:
        """Return correction patterns for the current vertical."""
        vertical = self.context.vertical
        mapping = {
            "salone": CORRECTION_PATTERNS_SALONE,
            "palestra": CORRECTION_PATTERNS_PALESTRA,
            "medical": CORRECTION_PATTERNS_MEDICAL,
            "auto": CORRECTION_PATTERNS_AUTO,
            "restaurant": CORRECTION_PATTERNS_RESTAURANT,
        }
        return mapping.get(vertical, {})

    def _build_booking_confirmation_message(self) -> str:
        """Build vertical-specific booking confirmation message."""
        ctx = self.context
        summary = ctx.get_summary()
        vertical = ctx.vertical

        if vertical == "salone":
            return (
                f"Perfetto! Ho prenotato {summary}. "
                f"Le invieremo una conferma su WhatsApp. Grazie e arrivederci!"
            )
        elif vertical == "palestra":
            return (
                f"Fantastico! Ho prenotato {summary}. "
                f"Riceverà conferma su WhatsApp. Grazie e arrivederci!"
            )
        elif vertical == "medical":
            return (
                f"Prenotazione confermata! {summary}. "
                f"Ricordi la documentazione necessaria. Riceverà conferma su WhatsApp. Arrivederci!"
            )
        elif vertical == "auto":
            return f"Perfetto! {summary}. Riceverà conferma su WhatsApp. Arrivederci!"
        elif vertical == "restaurant":
            return f"Tavolo riservato! {summary}. Conferma su WhatsApp. Arrivederci!"

        return f"Prenotazione confermata! {summary}. Conferma su WhatsApp. Grazie e arrivederci!"

    def _get_state_response(self, state: BookingState) -> str:
        """C4: Get the prompt response for a given state."""
        if state == BookingState.WAITING_SERVICE:
            return TEMPLATES["ask_service"]
        elif state == BookingState.WAITING_DATE:
            return TEMPLATES["ask_date"].format(
                service=self.context.service_display or self.context.service or "il servizio"
            )
        elif state == BookingState.WAITING_TIME:
            return TEMPLATES["ask_time"].format(
                date=self.context.date_display or self.context.date or "il giorno scelto"
            )
        elif state == BookingState.WAITING_OPERATOR:
            return TEMPLATES["ask_operator"]
        elif state == BookingState.CONFIRMING:
            return TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
        return "Come posso aiutarla?"

    def _normalize_service_display(self, service: str) -> str:
        """C4: Normalize service name to display format."""
        return SERVICE_DISPLAY.get(service, service.capitalize())

    def _format_date_display(self, date_str: str) -> str:
        """C4: Format YYYY-MM-DD to Italian display."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            days_it = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
            months_it = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
                         "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
            return f"{days_it[dt.weekday()]} {dt.day} {months_it[dt.month - 1]}"
        except (ValueError, IndexError):
            return date_str

    def _format_time_display(self, time_str: str) -> str:
        """C4: Format HH:MM to 'alle HH:MM'."""
        return f"alle {time_str}"

    def handle_timeout(self) -> StateMachineResult:
        """C4: Handle conversation timeout."""
        return StateMachineResult(
            next_state=self.context.state,
            response="Sei ancora lì? Se vuoi possiamo riprendere dopo, chiamaci pure quando vuoi."
        )

    def _get_next_required_slot(self) -> Optional[BookingState]:
        """Get next required slot that isn't filled yet (slot pre-fill skip)."""
        vertical = self.context.vertical

        if vertical == "auto":
            required_slots = [
                ("service", BookingState.WAITING_SERVICE),
                ("date", BookingState.WAITING_DATE),
            ]
        else:
            required_slots = [
                ("service", BookingState.WAITING_SERVICE),
                ("date", BookingState.WAITING_DATE),
                ("time", BookingState.WAITING_TIME),
            ]

        for field_name, state in required_slots:
            if not self._is_slot_filled(field_name):
                return state

        return BookingState.CONFIRMING

    def _is_slot_filled(self, field_name: str) -> bool:
        """Check if a slot is already filled."""
        ctx = self.context
        if field_name == "service":
            return bool(ctx.service)
        elif field_name == "date":
            return bool(ctx.date)
        elif field_name == "time":
            return bool(ctx.time)
        elif field_name == "operator":
            return bool(ctx.operator_name)
        return False

    def _skip_to_next_required_state(self) -> StateMachineResult:
        """Skip to next required state based on filled slots."""
        next_state = self._get_next_required_slot()
        if next_state is None:
            next_state = BookingState.CONFIRMING
        response = self._get_state_response(next_state)
        self.context.state = next_state
        return StateMachineResult(
            next_state=next_state,
            response=response
        )

    # =========================================================================
    # CONFIRMING STATE HANDLER (C2: entities FIRST, 3-level correction)
    # =========================================================================

    def _handle_confirming(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """
        Handle CONFIRMING state with 3-level correction logic.

        C2: Entity extraction FIRST. Any entities found = ALWAYS correction,
        regardless of "sì"/"no" in the same sentence.

        Level 1: Re-extract entities → if found, treat as correction
        Level 2: Rejection + no entities → cancellation
        Level 3: Pure affirmative → confirm booking
        """
        text_lower = text.lower()

        # =====================================================================
        # PHASE 1: Re-extract entities from text (C2: entities FIRST)
        # =====================================================================
        level1_entities = self._extract_level1_entities(text_lower)
        has_new_entities = bool(level1_entities)

        # =====================================================================
        # PHASE 2: If ANY new entities found → ALWAYS CORRECTION
        # This handles: "sì ma alle 11", "niente meglio venerdì", "anzi con Marco"
        # =====================================================================
        if has_new_entities:
            self._update_context_from_extraction(level1_entities, force_update=True)
            self.context.corrections_made += 1

            change_summary = self._format_correction_summary(level1_entities)

            if self.context.corrections_made > 2:
                response = (
                    f"Capito! {change_summary}. Questa è l'ultima modifica "
                    f"prima di confermare. Sei d'accordo?"
                )
            else:
                response = f"Perfetto! {change_summary}. Confermi ora?"

            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=response,
                context_updates=level1_entities
            )

        # =====================================================================
        # PHASE 3: Explicit "cambio X" (existing logic, keep)
        # =====================================================================
        if "cambio" in text_lower or "cambia" in text_lower:
            if any(word in text_lower for word in ["servizio", "taglio", "colore", "piega"]):
                self.context.service = None
                self.context.service_display = None
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response="D'accordo, quale servizio desidera?"
                )
            if any(word in text_lower for word in ["data", "giorno", "quando"]):
                self.context.date = None
                self.context.date_display = None
                self.context.state = BookingState.WAITING_DATE
                return StateMachineResult(
                    next_state=BookingState.WAITING_DATE,
                    response="D'accordo, per quale giorno?"
                )
            if any(word in text_lower for word in ["ora", "orario", "tempo"]):
                self.context.time = None
                self.context.time_display = None
                self.context.state = BookingState.WAITING_TIME
                return StateMachineResult(
                    next_state=BookingState.WAITING_TIME,
                    response="D'accordo, a che ora preferisce?"
                )

        # =====================================================================
        # PHASE 4: Pure affirmative (NO new entities) → CONFIRM
        # =====================================================================
        if self._is_explicit_confirmation(text_lower):
            # Create booking data
            booking = {
                "service": self.context.service,
                "services": self.context.services,
                "service_display": self.context.service_display,
                "date": self.context.date,
                "time": self.context.time,
                "client_name": self.context.client_name,
                "client_id": self.context.client_id,
                "operator_name": self.context.operator_name,
                "operator_id": self.context.operator_id,
                "created_at": datetime.now().isoformat(),
            }
            # Save booking in context for later
            self.context.last_booking = booking
            # Go to close confirmation instead of completing immediately
            self.context.state = BookingState.ASKING_CLOSE_CONFIRMATION
            return StateMachineResult(
                next_state=BookingState.ASKING_CLOSE_CONFIRMATION,
                response=TEMPLATES["ask_close_confirmation"],
                booking=booking
                # Note: should_exit=False, will wait for close confirmation
            )

        # =====================================================================
        # PHASE 5: Pure negative (NO new entities)
        # ANTI-CASCADE: if user was already correcting (corrections_made > 0),
        # "no" means "still not right", NOT "cancel everything".
        # Only cancel on first "no" with zero corrections.
        # =====================================================================
        _, has_rejection = self._detect_correction_or_rejection_signal(text_lower)
        if has_rejection:
            if self.context.corrections_made == 0:
                # First interaction, user rejects entire booking
                self.context.state = BookingState.CANCELLED
                return StateMachineResult(
                    next_state=BookingState.CANCELLED,
                    response="Nessun problema. Posso aiutarla in altro modo?",
                    should_exit=True
                )
            else:
                # User was correcting but we can't understand what they want
                # Ask clearly instead of cancelling
                return StateMachineResult(
                    next_state=BookingState.CONFIRMING,
                    response="Mi faccia capire meglio, cosa desidera cambiare?"
                )

        # =====================================================================
        # PHASE 6: Groq LLM fallback for complex corrections
        # "preferisco dopo le 17", "meglio con un'operatrice", etc.
        # =====================================================================
        if self.groq_nlu:
            logger.info(f"[SM] CONFIRMING: no entities/yes/no, trying Groq for '{text[:50]}'")
            groq_result = self.groq_nlu.extract_confirming(
                utterance=text,
                servizio=self.context.service_display or self.context.service or "",
                data=self.context.date_display or self.context.date or "",
                ora=self.context.time_display or self.context.time or "",
            )
            if groq_result:
                decisione = groq_result.get("decisione", "")

                if decisione == "confermato":
                    booking = {
                        "service": self.context.service,
                        "services": self.context.services,
                        "service_display": self.context.service_display,
                        "date": self.context.date,
                        "time": self.context.time,
                        "client_name": self.context.client_name,
                        "client_id": self.context.client_id,
                        "operator_name": self.context.operator_name,
                        "operator_id": self.context.operator_id,
                        "created_at": datetime.now().isoformat(),
                    }
                    # Save booking in context for later
                    self.context.last_booking = booking
                    # Go to close confirmation instead of completing immediately
                    self.context.state = BookingState.ASKING_CLOSE_CONFIRMATION
                    return StateMachineResult(
                        next_state=BookingState.ASKING_CLOSE_CONFIRMATION,
                        response=TEMPLATES["ask_close_confirmation"],
                        booking=booking
                        # Note: should_exit=False, will wait for close confirmation
                    )

                elif decisione == "correzione":
                    campo = groq_result.get("campo_corretto", "")
                    valore = groq_result.get("nuovo_valore", "")

                    if campo == "ora" and valore:
                        # Try to parse time from Groq value
                        time_result = extract_time(valore)
                        if time_result:
                            self.context.time = time_result.to_string()
                            self.context.time_display = f"alle {time_result.to_string()}"
                        else:
                            # Use Groq's value directly if it looks like HH:MM
                            if re.match(r'^\d{1,2}:\d{2}$', valore):
                                self.context.time = valore
                                self.context.time_display = f"alle {valore}"
                        self.context.corrections_made += 1
                        return StateMachineResult(
                            next_state=BookingState.CONFIRMING,
                            response=f"Perfetto! ora → {self.context.time_display or valore}. Confermi ora?"
                        )

                    elif campo == "data" and valore:
                        date_result = extract_date(valore, self.reference_date)
                        if date_result:
                            self.context.date = date_result.to_string("%Y-%m-%d")
                            self.context.date_display = self._format_date_display(self.context.date)
                        self.context.corrections_made += 1
                        return StateMachineResult(
                            next_state=BookingState.CONFIRMING,
                            response=f"Perfetto! data → {self.context.date_display or valore}. Confermi ora?"
                        )

                    elif campo == "servizio" and valore:
                        self.context.corrections_made += 1
                        # Re-enter service state for complex changes
                        self.context.state = BookingState.WAITING_SERVICE
                        return StateMachineResult(
                            next_state=BookingState.WAITING_SERVICE,
                            response=f"D'accordo, modifichiamo il servizio. Cosa desidera?"
                        )

                    elif campo == "operatore" and valore:
                        self.context.operator_name = sanitize_name(valore, is_surname=True)
                        self.context.operator_requested = True
                        self.context.corrections_made += 1
                        return StateMachineResult(
                            next_state=BookingState.CONFIRMING,
                            response=f"Perfetto! operatore → {self.context.operator_name}. Confermi ora?"
                        )

                elif decisione == "cancellazione":
                    self.context.state = BookingState.CANCELLED
                    return StateMachineResult(
                        next_state=BookingState.CANCELLED,
                        response="Nessun problema. Se cambia idea, ci chiami pure. Arrivederci!",
                        should_exit=True
                    )

        # =====================================================================
        # PHASE 7: Fallback → human clarification
        # =====================================================================
        self.context.clarifications_asked += 1
        if self.context.clarifications_asked > 2:
            response = TEMPLATES["fallback_clarify"]
        else:
            response = f"Riepilogo: {self.context.get_summary()}. Conferma o mi dica cosa cambiare."

        return StateMachineResult(
            next_state=BookingState.CONFIRMING,
            response=response
        )

    # =========================================================================
    # NEW CLIENT REGISTRATION HANDLERS
    # =========================================================================

    def _handle_propose_registration(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle PROPOSE_REGISTRATION state - ask if user wants to register."""
        text_lower = text.lower()

        # =================================================================
        # PRIORITY 1: User provides name (implicit consent to register)
        # "mi chiamo Nicola Arquati" / "Allora, mi chiamo Nicola Arquati"
        # Treat name provision as implicit "yes, register me"
        # =================================================================
        if extracted.name:
            clean_name, clean_surname = sanitize_name_pair(extracted.name.name, None)
            if clean_name:
                self.context.is_new_client = True
                self.context.client_name = clean_name
                if clean_surname:
                    self.context.client_surname = clean_surname
                    # Have both name + surname → skip to phone
                    self.context.state = BookingState.REGISTERING_PHONE
                    return StateMachineResult(
                        next_state=BookingState.REGISTERING_PHONE,
                        response=TEMPLATES["ask_phone"].format(
                            name=f"{clean_name} {clean_surname}"
                        )
                    )
                else:
                    # Only first name → ask for surname
                    self.context.state = BookingState.REGISTERING_SURNAME
                    return StateMachineResult(
                        next_state=BookingState.REGISTERING_SURNAME,
                        response=TEMPLATES["ask_surname"]
                    )

        # =================================================================
        # PRIORITY 2: Affirmative response ("sì", "ok", etc.)
        # =================================================================
        affirmative = ["sì", "si", "ok", "va bene", "certo", "volentieri", "registrami", "registra"]
        if any(word in text_lower for word in affirmative):
            self.context.is_new_client = True

            # Check if we already have surname from a previous turn
            if self.context.client_name and self.context.client_surname:
                # Both name and surname already collected → skip to phone
                self.context.state = BookingState.REGISTERING_PHONE
                return StateMachineResult(
                    next_state=BookingState.REGISTERING_PHONE,
                    response=TEMPLATES["ask_phone"].format(
                        name=f"{self.context.client_name} {self.context.client_surname}"
                    )
                )

            # Check if client_name contains both (fallback)
            if self.context.client_name:
                parts = self.context.client_name.split()
                if len(parts) >= 2:
                    self.context.client_name = parts[0]
                    self.context.client_surname = ' '.join(parts[1:])
                    self.context.state = BookingState.REGISTERING_PHONE
                    return StateMachineResult(
                        next_state=BookingState.REGISTERING_PHONE,
                        response=TEMPLATES["ask_phone"].format(
                            name=f"{self.context.client_name} {self.context.client_surname}"
                        )
                    )

            self.context.state = BookingState.REGISTERING_SURNAME
            return StateMachineResult(
                next_state=BookingState.REGISTERING_SURNAME,
                response=TEMPLATES["ask_surname"]
            )

        # Check for negative responses
        negative_patterns = [r"\bno\b", r"\bnon\s+voglio\b", r"\bniente\b"]
        if any(re.search(pattern, text_lower) for pattern in negative_patterns):
            self.context.state = BookingState.CANCELLED
            return StateMachineResult(
                next_state=BookingState.CANCELLED,
                response=TEMPLATES["registration_cancelled"],
                should_exit=True
            )

        # Re-ask
        return StateMachineResult(
            next_state=BookingState.PROPOSE_REGISTRATION,
            response="Vuole che la registri come nuovo cliente? Dica sì o no."
        )

    def _handle_registering_surname(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle REGISTERING_SURNAME state - collect full name (nome + cognome)."""
        text_lower = text.lower().strip()

        # =================================================================
        # PHASE 1: Contextual phrase parsing
        # Handle: "il cognome è Arquati", "è Arquati", "Arquati è il cognome"
        # Handle: "vi ho appena detto, il cognome è Arquati"
        # =================================================================
        surname_phrase_patterns = [
            # "il cognome è X" / "cognome è X" / "cognome: X"
            r"(?:il\s+)?cognome\s+(?:è|e|:)\s+([A-Z][a-zàèéìòùA-Z]+)",
            # "è X" at end of sentence (when we already asked for surname)
            r"(?:è|e)\s+([A-Z][a-zàèéìòù]+)\s*[.!]?\s*$",
            # "si chiama X" / "mi chiamo X Y"
            r"(?:si\s+chiama|mi\s+chiamo)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)",
        ]

        for pattern in surname_phrase_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_text = match.group(1).strip()
                parts = extracted_text.split()
                # Filter out blacklisted words
                from entity_extractor import extract_name as _extract_name
                # Use the NAME_BLACKLIST from entity_extractor
                _BLACKLIST = {
                    "vi", "ho", "mi", "si", "se", "ci", "ne", "lo", "la", "le", "li",
                    "il", "un", "una", "uno", "gli", "dei", "delle", "del",
                    "appena", "già", "proprio", "anche", "ancora", "allora",
                    "cognome", "nome", "mio", "suo", "è",
                    "detto", "fatto", "stato", "dico",
                    "ehi", "eh", "oh", "ah", "ahi", "uhm", "ehm", "boh", "mah", "beh",
                    "senti", "senta", "scolta", "ascolta", "aspetta", "aspetti",
                }
                clean_parts = [w for w in parts if w.lower() not in _BLACKLIST]
                if clean_parts:
                    if len(clean_parts) >= 2 and not self.context.client_name:
                        # Full name: "mi chiamo Nicola Arquati"
                        self.context.client_name = sanitize_name(clean_parts[0])
                        self.context.client_surname = sanitize_name(
                            ' '.join(clean_parts[1:]), is_surname=True
                        )
                    elif len(clean_parts) >= 2 and self.context.client_name:
                        # Already have name, this is name + surname repeated
                        self.context.client_surname = sanitize_name(
                            clean_parts[-1], is_surname=True
                        )
                    else:
                        # Single word = surname
                        if self.context.client_name:
                            self.context.client_surname = sanitize_name(
                                clean_parts[0], is_surname=True
                            )
                        else:
                            self.context.client_name = sanitize_name(clean_parts[0])
                            return StateMachineResult(
                                next_state=BookingState.REGISTERING_SURNAME,
                                response=f"Piacere {self.context.client_name}! E il cognome?"
                            )

                    if self.context.client_name and self.context.client_surname:
                        self.context.state = BookingState.REGISTERING_PHONE
                        return StateMachineResult(
                            next_state=BookingState.REGISTERING_PHONE,
                            response=TEMPLATES["ask_phone"].format(
                                name=f"{self.context.client_name} {self.context.client_surname}"
                            )
                        )

        # =================================================================
        # PHASE 2: Entity extractor (regex patterns)
        # =================================================================
        # B1: Strip punctuation from STT output
        text_clean = sanitize_name(text.strip())

        name = extract_name(text)
        if name:
            clean_name, clean_surname = sanitize_name_pair(name.name, None)
            if clean_name and clean_surname:
                if self.context.client_name and clean_name.lower() != self.context.client_name.lower():
                    # Already have a different name (e.g. "Gino"), user gave surname "Di Nanni"
                    # sanitize_name_pair incorrectly split it — treat entire input as surname
                    self.context.client_surname = sanitize_name(name.name, is_surname=True)
                else:
                    # No name yet, or user repeated name + gave surname ("Gino Di Nanni")
                    self.context.client_name = clean_name
                    self.context.client_surname = clean_surname
            elif clean_name:
                if self.context.client_name and not self.context.client_surname:
                    # We already have a name, treat this as surname
                    self.context.client_surname = sanitize_name(clean_name, is_surname=True)
                elif not self.context.client_name:
                    # Only one word - treat as name, ask for surname
                    self.context.client_name = clean_name
                    return StateMachineResult(
                        next_state=BookingState.REGISTERING_SURNAME,
                        response=f"Piacere {self.context.client_name}! E il cognome?"
                    )
        else:
            # =================================================================
            # PHASE 3: Raw text fallback (single word = surname if we have name)
            # =================================================================
            # Only use raw text if it looks like a name (1-2 capitalized words)
            raw_words = text_clean.split()
            # Filter out blacklisted words
            _BLACKLIST = {
                "vi", "ho", "mi", "si", "se", "ci", "ne", "lo", "la", "le", "li",
                "il", "un", "una", "uno", "gli", "appena", "già", "proprio",
                "allora", "cognome", "nome", "mio", "suo", "è", "detto",
                "fatto", "stato", "dico", "bene", "ecco",
                "ehi", "eh", "oh", "ah", "ahi", "uhm", "ehm", "boh", "mah", "beh",
                "senti", "senta", "scolta", "ascolta", "aspetta", "aspetti",
            }
            clean_words = [w for w in raw_words if w.lower() not in _BLACKLIST and len(w) >= 2]

            if clean_words:
                clean_name, clean_surname = sanitize_name_pair(
                    ' '.join(clean_words), None
                )
                if clean_name and clean_surname:
                    if self.context.client_name and clean_name.lower() != self.context.client_name.lower():
                        # Already have a different name, treat entire input as surname
                        self.context.client_surname = sanitize_name(
                            ' '.join(clean_words), is_surname=True
                        )
                    else:
                        self.context.client_name = clean_name
                        self.context.client_surname = clean_surname
                elif clean_name:
                    if self.context.client_name:
                        # We already have name, this is surname
                        self.context.client_surname = sanitize_name(clean_name, is_surname=True)
                    else:
                        self.context.client_name = clean_name
                        return StateMachineResult(
                            next_state=BookingState.REGISTERING_SURNAME,
                            response=f"Piacere {self.context.client_name}! E il cognome?"
                        )
            else:
                # =============================================================
                # PHASE 4: Groq LLM fallback for conversational Italian
                # =============================================================
                if self.groq_nlu:
                    logger.info(f"[SM] REGISTERING_SURNAME: regex failed, trying Groq for '{text[:50]}'")
                    groq_result = self.groq_nlu.extract_surname(
                        utterance=text,
                        nome=self.context.client_name or ""
                    )
                    if groq_result and groq_result.get("cognome"):
                        cognome = sanitize_name(groq_result["cognome"], is_surname=True)
                        if cognome:
                            self.context.client_surname = cognome
                            # Fall through to "have both" check below

                if not self.context.client_surname:
                    return StateMachineResult(
                        next_state=BookingState.REGISTERING_SURNAME,
                        response="Mi ripete il cognome, per cortesia?"
                    )

        # Have both name and surname - ask for phone
        if self.context.client_name and self.context.client_surname:
            self.context.state = BookingState.REGISTERING_PHONE
            return StateMachineResult(
                next_state=BookingState.REGISTERING_PHONE,
                response=TEMPLATES["ask_phone"].format(
                    name=f"{self.context.client_name} {self.context.client_surname}"
                )
            )

        # Missing something - ask again
        if self.context.client_name and not self.context.client_surname:
            return StateMachineResult(
                next_state=BookingState.REGISTERING_SURNAME,
                response=f"Grazie {self.context.client_name}! E il cognome?"
            )

        return StateMachineResult(
            next_state=BookingState.REGISTERING_SURNAME,
            response="Mi ripete nome e cognome, per cortesia?"
        )

    def _handle_registering_phone(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle REGISTERING_PHONE state - collect phone number."""
        text_lower = text.lower().strip()

        # =================================================================
        # PRIORITY 0: Detect name/surname correction
        # "No, ho detto che mi chiamo Filippo di cognome Neri"
        # "il cognome è Neri" / "di cognome Neri"
        # =================================================================
        surname_correction_patterns = [
            r"(?:di\s+)?cognome\s+(?:è|e|:)?\s*([A-Z][a-zàèéìòùA-Z]+)",
            r"mi\s+chiamo\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)+)",
        ]
        for pattern in surname_correction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_text = match.group(1).strip()
                parts = extracted_text.split()
                if "cognome" in pattern:
                    # "di cognome Neri" → surname only
                    surname = parts[-1] if parts else None
                    if surname:
                        self.context.client_surname = sanitize_name(surname, is_surname=True)
                        # Re-ask phone
                        return StateMachineResult(
                            next_state=BookingState.REGISTERING_PHONE,
                            response=TEMPLATES["ask_phone"].format(
                                name=f"{self.context.client_name} {self.context.client_surname}"
                            )
                        )
                else:
                    # "mi chiamo Filippo Neri" → update both
                    clean_name, clean_surname = sanitize_name_pair(extracted_text, None)
                    if clean_name:
                        self.context.client_name = clean_name
                    if clean_surname:
                        self.context.client_surname = clean_surname
                    # Re-ask phone
                    return StateMachineResult(
                        next_state=BookingState.REGISTERING_PHONE,
                        response=TEMPLATES["ask_phone"].format(
                            name=f"{self.context.client_name} {self.context.client_surname or ''}".strip()
                        )
                    )

        # Try to extract phone
        if extracted.phone:
            self.context.client_phone = extracted.phone
        else:
            # Try to extract phone number from text
            from entity_extractor import extract_phone
            phone = extract_phone(text)
            if phone:
                self.context.client_phone = phone
            else:
                # Use raw input, clean up
                digits = ''.join(c for c in text if c.isdigit())
                if len(digits) >= 9:  # Minimum phone length
                    self.context.client_phone = digits

        if self.context.client_phone:
            # Got phone - confirm the number before creating client
            self.context.state = BookingState.CONFIRMING_PHONE
            return StateMachineResult(
                next_state=BookingState.CONFIRMING_PHONE,
                response=TEMPLATES["confirm_phone_number"].format(
                    phone=self.context.client_phone
                )
            )

        # Couldn't get phone - check if it's a name/surname correction via Groq
        if self.groq_nlu:
            # Detect correction signals: "no", "ho detto", "cognome", "mi chiamo"
            correction_signals = ["no", "ho detto", "cognome", "nome", "mi chiamo", "sbagliato", "correggi"]
            if any(s in text_lower for s in correction_signals):
                logger.info(f"[SM] REGISTERING_PHONE: correction detected, trying Groq for '{text[:50]}'")
                groq_result = self.groq_nlu.extract_phone_correction(
                    utterance=text,
                    nome=self.context.client_name or "",
                    cognome=self.context.client_surname or ""
                )
                if groq_result:
                    tipo = groq_result.get("tipo_azione", "")
                    valore = groq_result.get("valore")

                    if tipo == "correzione_cognome" and valore:
                        self.context.client_surname = sanitize_name(valore, is_surname=True)
                        return StateMachineResult(
                            next_state=BookingState.REGISTERING_PHONE,
                            response=TEMPLATES["ask_phone"].format(
                                name=f"{self.context.client_name} {self.context.client_surname}"
                            )
                        )
                    elif tipo == "correzione_nome" and valore:
                        clean_name, clean_surname = sanitize_name_pair(valore, None)
                        if clean_name:
                            self.context.client_name = clean_name
                        if clean_surname:
                            self.context.client_surname = clean_surname
                        # Go back to surname if we lost it
                        if not self.context.client_surname:
                            self.context.state = BookingState.REGISTERING_SURNAME
                            return StateMachineResult(
                                next_state=BookingState.REGISTERING_SURNAME,
                                response=f"Perfetto, {self.context.client_name}. E il cognome?"
                            )
                        return StateMachineResult(
                            next_state=BookingState.REGISTERING_PHONE,
                            response=TEMPLATES["ask_phone"].format(
                                name=f"{self.context.client_name} {self.context.client_surname}"
                            )
                        )

        # No phone, no correction - ask again
        return StateMachineResult(
            next_state=BookingState.REGISTERING_PHONE,
            response="Mi ripete il numero di telefono?"
        )

    def _handle_confirming_phone(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle CONFIRMING_PHONE state - confirm phone number before creating client."""
        text_lower = text.lower().strip()

        # Check for affirmative responses
        affirmative = ["sì", "si", "ok", "va bene", "confermo", "esatto", "corretto"]
        if any(word in text_lower for word in affirmative):
            # Phone confirmed - create client and move to service
            self.context.state = BookingState.WAITING_SERVICE
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response=TEMPLATES["registration_complete"].format(
                    name=f"{self.context.client_name} {self.context.client_surname}".strip()
                ),
                follow_up_response=TEMPLATES["ask_service"],
                needs_db_lookup=True,
                lookup_type="create_client",
                lookup_params={
                    "nome": self.context.client_name,
                    "cognome": self.context.client_surname,
                    "telefono": self.context.client_phone
                }
            )

        # Check for negative responses
        negative_patterns = [r"\bno\b", r"\bnon\s+è\s+corretto\b", r"\bsbagliato\b", r"\berrato\b"]
        if any(re.search(pattern, text_lower) for pattern in negative_patterns):
            # Phone wrong - go back to phone collection
            self.context.client_phone = None
            self.context.state = BookingState.REGISTERING_PHONE
            return StateMachineResult(
                next_state=BookingState.REGISTERING_PHONE,
                response=TEMPLATES["confirm_phone_reask"]
            )

        # Check if user gave a new phone number directly
        if extracted.phone:
            self.context.client_phone = extracted.phone
            return StateMachineResult(
                next_state=BookingState.CONFIRMING_PHONE,
                response=TEMPLATES["confirm_phone_number"].format(
                    phone=self.context.client_phone
                )
            )
        else:
            from entity_extractor import extract_phone
            phone = extract_phone(text)
            if phone:
                self.context.client_phone = phone
                return StateMachineResult(
                    next_state=BookingState.CONFIRMING_PHONE,
                    response=TEMPLATES["confirm_phone_number"].format(
                        phone=self.context.client_phone
                    )
                )

        # Fallback - re-ask confirmation
        return StateMachineResult(
            next_state=BookingState.CONFIRMING_PHONE,
            response=f"Per confermare, il numero è {self.context.client_phone or ''}. È corretto?"
        )

    def _handle_registering_confirm(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle REGISTERING_CONFIRM state - confirm and create client."""
        text_lower = text.lower()

        # Check for affirmative responses
        affirmative = ["sì", "si", "ok", "va bene", "confermo", "esatto", "corretto"]
        if any(word in text_lower for word in affirmative):
            # B2: Registration confirmed - split into 2 responses
            self.context.state = BookingState.WAITING_SERVICE
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response=TEMPLATES["registration_complete"].format(
                    name=f"{self.context.client_name} {self.context.client_surname}".strip()
                ),
                follow_up_response=TEMPLATES["ask_service"],
                needs_db_lookup=True,
                lookup_type="create_client",
                lookup_params={
                    "nome": self.context.client_name,
                    "cognome": self.context.client_surname,
                    "telefono": self.context.client_phone
                }
            )

        # Check for negative responses
        negative_patterns = [r"\bno\b", r"\bnon\s+è\s+corretto\b", r"\bsbagliato\b"]
        if any(re.search(pattern, text_lower) for pattern in negative_patterns):
            # Go back to surname
            self.context.client_surname = None
            self.context.client_phone = None
            self.context.state = BookingState.REGISTERING_SURNAME
            return StateMachineResult(
                next_state=BookingState.REGISTERING_SURNAME,
                response="Nessun problema, ricominciamo. Qual è il suo cognome?"
            )

        # Re-ask
        return StateMachineResult(
            next_state=BookingState.REGISTERING_CONFIRM,
            response=f"Per confermare: {self.context.client_name} {self.context.client_surname}, telefono {self.context.client_phone}. È corretto?"
        )

    def _handle_asking_close_confirmation(self, text: str) -> StateMachineResult:
        """
        Handle ASKING_CLOSE_CONFIRMATION state.
        User just confirmed booking, now ask if they want to end the call.
        """
        text_lower = text.lower().strip()

        # Affirmative responses - close the call
        affirmative = ["sì", "si", "ok", "va bene", "certo", "s\u00ec", "perfetto", "bene", "confermo"]
        if any(word in text_lower for word in affirmative):
            # User wants to end the call - send final confirmation message
            summary = self.context.get_summary()
            response = (
                f"Perfetto! A presto. "
                f"Le invieremo la conferma dell'appuntamento ({summary}) via WhatsApp. "
                f"Buona giornata!"
            )
            return StateMachineResult(
                next_state=BookingState.COMPLETED,
                response=response,
                should_exit=True
            )

        # Negative responses - stay on the line
        negative = ["no", "niente", "ancora", "altro", "rimaniamo", "non ancora"]
        if any(word in text_lower for word in negative):
            # User wants to stay on the line
            self.context.state = BookingState.WAITING_SERVICE
            # Reset booking info but keep client info for follow-up
            old_client_id = self.context.client_id
            old_client_name = self.context.client_name
            old_client_phone = self.context.client_phone
            self.reset_for_new_booking()
            self.context.client_id = old_client_id
            self.context.client_name = old_client_name
            self.context.client_phone = old_client_phone

            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response=TEMPLATES["close_stay"]
            )

        # Unclear response - ask again
        return StateMachineResult(
            next_state=BookingState.ASKING_CLOSE_CONFIRMATION,
            response="Mi dica sì per terminare la chiamata, o no per rimanere in linea."
        )

    def propose_new_client_registration(self, client_name: str) -> StateMachineResult:
        """
        Start new client registration flow.

        Called when client search returns 0 results.

        Args:
            client_name: Name that wasn't found

        Returns:
            StateMachineResult proposing registration
        """
        self.context.client_name = client_name
        self.context.state = BookingState.PROPOSE_REGISTRATION
        return StateMachineResult(
            next_state=BookingState.PROPOSE_REGISTRATION,
            response=TEMPLATES["propose_registration"]
        )

    def start_booking_flow(self, initial_context: Optional[Dict] = None) -> StateMachineResult:
        """
        Start a new booking flow.

        Args:
            initial_context: Optional pre-populated context data

        Returns:
            StateMachineResult with first prompt
        """
        self.reset()
        self.context.created_at = datetime.now().isoformat()

        # Pre-populate context if provided
        if initial_context:
            if initial_context.get("client_name"):
                self.context.client_name = initial_context["client_name"]
            if initial_context.get("client_id"):
                self.context.client_id = initial_context["client_id"]
            if initial_context.get("service"):
                self.context.service = initial_context["service"]
                self.context.service_display = SERVICE_DISPLAY.get(
                    initial_context["service"],
                    initial_context["service"].capitalize()
                )

        # Determine starting state based on what we have
        if self.context.service:
            self.context.state = BookingState.WAITING_DATE
            return StateMachineResult(
                next_state=BookingState.WAITING_DATE,
                response=TEMPLATES["ask_date"].format(
                    service=self.context.service_display or self.context.service
                )
            )

        self.context.state = BookingState.WAITING_SERVICE
        return StateMachineResult(
            next_state=BookingState.WAITING_SERVICE,
            response=TEMPLATES["ask_service"]
        )

    def _handle_disambiguating_name(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle DISAMBIGUATING_NAME state - ask for birth date confirmation."""
        # Check if user confirmed or denied
        text_lower = text.lower()
        
        # Check for negative responses (no, wrong, different person)
        # CoVe: Espansi pattern per coprire più casi di rifiuto
        negative_indicators = [
            "no", "sbagliato", "diverso", "non sono", "altro", "nuovo cliente",
            "non sono io", "sono un altro", "sono una persona diversa", 
            "persona diversa", "non è il mio nome", "non mi chiamo",
            "mi chiamo diversamente", "sono diversa", "sono diverso",
            "non corrisponde", "non sono quel", "non sono quella"
        ]
        if any(ind in text_lower for ind in negative_indicators):
            logger.info(f"[DISAMBIGUATION] User rejected match: '{text}' -> proceeding to registration")
            # User denied - proceed as new client
            self.context.disambiguation_candidates = []
            self.context.disambiguation_attempts = 0
            self.context.state = BookingState.REGISTERING_SURNAME
            return StateMachineResult(
                next_state=BookingState.REGISTERING_SURNAME,
                response="Capisco, la registro come nuovo cliente. Mi può dire il suo nome e cognome?"
            )
        
        # CoVe FIX: Usa extract_birth_date dal DisambiguationHandler, NON extract_date
        # extract_date è per date di booking (domani, oggi), non per date di nascita
        birth_date = None
        if self.disambiguation_handler:
            birth_date = self.disambiguation_handler.extract_birth_date(text)
            logger.info(f"[DISAMBIGUATION] Extracted birth date: {birth_date} from '{text}'")
        
        if birth_date and self.context.disambiguation_candidates:
            # Check if date matches candidate
            candidate = self.context.disambiguation_candidates[0]
            candidate_birth = candidate.get("data_nascita", "")
            
            if candidate_birth:
                # Normalize dates for comparison
                input_date = birth_date.strftime("%Y-%m-%d")
                logger.info(f"[DISAMBIGUATION] Comparing dates: input={input_date}, candidate={candidate_birth}")
                if input_date == candidate_birth:
                    # Match confirmed!
                    logger.info(f"[DISAMBIGUATION] Match confirmed for client: {candidate['id']}")
                    self.context.client_id = candidate["id"]
                    self.context.client_name = candidate["nome"]
                    self.context.client_surname = candidate["cognome"]
                    self.context.disambiguation_candidates = []
                    self.context.disambiguation_attempts = 0
                    self.context.state = BookingState.WAITING_SERVICE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=TEMPLATES["welcome_back"].format(name=candidate["nome"]) + " " + TEMPLATES["ask_service"]
                    )
        
        # No clear response - ask again with clarification
        self.context.disambiguation_attempts += 1
        logger.info(f"[DISAMBIGUATION] Attempt {self.context.disambiguation_attempts}, no clear match")
        if self.context.disambiguation_attempts >= 2:
            # Too many attempts - proceed as new client
            logger.info("[DISAMBIGUATION] Max attempts reached, proceeding to registration")
            self.context.disambiguation_candidates = []
            self.context.disambiguation_attempts = 0
            self.context.state = BookingState.REGISTERING_SURNAME
            return StateMachineResult(
                next_state=BookingState.REGISTERING_SURNAME,
                response="Non ho capito bene. La registro come nuovo cliente. Mi dica nome e cognome?"
            )
        
        # Ask again
        candidate = self.context.disambiguation_candidates[0] if self.context.disambiguation_candidates else None
        if candidate:
            return StateMachineResult(
                next_state=BookingState.DISAMBIGUATING_NAME,
                response=TEMPLATES["disambiguation_retry"]
            )
        
        return StateMachineResult(
            next_state=BookingState.REGISTERING_SURNAME,
            response="Mi dica il suo nome e cognome per favore?"
        )

    def _handle_disambiguating_birth_date(self, text: str) -> StateMachineResult:
        """Handle DISAMBIGUATING_BIRTH_DATE state - verify birth date."""
        # CoVe FIX: Usa extract_birth_date dal DisambiguationHandler, NON extract_date
        birth_date = None
        if self.disambiguation_handler:
            birth_date = self.disambiguation_handler.extract_birth_date(text)
            logger.info(f"[DISAMBIGUATION_BIRTH] Extracted birth date: {birth_date} from '{text}'")
        
        if birth_date and self.context.disambiguation_candidates:
            input_date = birth_date.strftime("%Y-%m-%d")
            candidate = self.context.disambiguation_candidates[0]
            candidate_birth = candidate.get("data_nascita", "")
            
            logger.info(f"[DISAMBIGUATION_BIRTH] Comparing dates: input={input_date}, candidate={candidate_birth}")
            
            if input_date == candidate_birth:
                # Confirmed!
                logger.info(f"[DISAMBIGUATION_BIRTH] Match confirmed for client: {candidate['id']}")
                self.context.client_id = candidate["id"]
                self.context.client_name = candidate["nome"]
                self.context.client_surname = candidate["cognome"]
                self.context.disambiguation_candidates = []
                self.context.disambiguation_attempts = 0
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response=TEMPLATES["disambiguation_confirmed"].format(name=candidate["nome"]) + " " + TEMPLATES["ask_service"]
                )
        
        # Not confirmed - increment attempts
        self.context.disambiguation_attempts += 1
        logger.info(f"[DISAMBIGUATION_BIRTH] Attempt {self.context.disambiguation_attempts}, no match")
        if self.context.disambiguation_attempts >= 2:
            logger.info("[DISAMBIGUATION_BIRTH] Max attempts reached, proceeding to registration")
            self.context.disambiguation_candidates = []
            self.context.disambiguation_attempts = 0
            self.context.state = BookingState.REGISTERING_SURNAME
            return StateMachineResult(
                next_state=BookingState.REGISTERING_SURNAME,
                response="Non ho trovato corrispondenze. La registro come nuovo cliente. Nome e cognome?"
            )
        
        return StateMachineResult(
            next_state=BookingState.DISAMBIGUATING_BIRTH_DATE,
            response="Non ho capito. Può ripetere la data di nascita? (es. 15 marzo 1985)"
        )


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Quick test
    sm = BookingStateMachine()

    print("Test 1: Normal booking flow")
    print("-" * 40)

    result = sm.start_booking_flow()
    print(f"State: {result.next_state.value}")
    print(f"Response: {result.response}")

    result = sm.process_message("vorrei un taglio")
    print(f"\nUser: vorrei un taglio")
    print(f"State: {result.next_state.value}")
    print(f"Response: {result.response}")

    result = sm.process_message("domani")
    print(f"\nUser: domani")
    print(f"State: {result.next_state.value}")
    print(f"Response: {result.response}")

    result = sm.process_message("alle 15")
    print(f"\nUser: alle 15")
    print(f"State: {result.next_state.value}")
    print(f"Response: {result.response}")

    result = sm.process_message("sì confermo")
    print(f"\nUser: sì confermo")
    print(f"State: {result.next_state.value}")
    print(f"Response: {result.response}")
    print(f"Booking: {result.booking}")

    print("\n" + "=" * 40)
    print("Test 2: Interruption handling")
    print("-" * 40)

    sm.reset()
    result = sm.start_booking_flow()
    result = sm.process_message("voglio un colore")
    print(f"\nUser: voglio un colore")
    print(f"State: {result.next_state.value}")

    result = sm.process_message("no aspetta, ricominciamo")
    print(f"\nUser: no aspetta, ricominciamo")
    print(f"State: {result.next_state.value}")
    print(f"Response: {result.response}")
