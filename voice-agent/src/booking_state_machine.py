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
    # New client registration states
    PROPOSE_REGISTRATION = "propose_registration"
    REGISTERING_SURNAME = "registering_surname"
    REGISTERING_PHONE = "registering_phone"
    REGISTERING_CONFIRM = "registering_confirm"


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

    # Vertical and correction tracking
    vertical: str = "salone"
    corrections_made: int = 0
    clarifications_asked: int = 0
    operator_gender_preference: Optional[str] = None  # "F" or "M"
    urgency: bool = False

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
    "taglio": ["taglio", "tagli", "tagliare", "sforbiciata", "spuntatina", "accorciare"],
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
    "operator": [
        r"\b(operatore|persona|umano|parlare\s+con)\b",
        r"\b(non\s+capisco|basta|aiuto)\b",
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
    # State entry prompts
    "ask_service": "Perfetto! Quale servizio desidera? Offriamo taglio, piega, colore, barba e trattamenti.",
    "ask_date": "Bene, {service}! Per quale giorno desidera prenotare?",
    "ask_time": "Ottimo, {date}. A che ora preferisce?",
    "ask_time_with_slots": "Ottimo, {date}. Abbiamo disponibilità alle {slots}. Quale orario preferisce?",
    "ask_operator": "Ha un operatore preferito?",
    "ask_name": "Mi può dire il suo nome per favore?",

    # Confirmations
    "confirm_booking": "Perfetto! Riepilogo: {summary}. Conferma?",
    "booking_confirmed": "Prenotazione confermata! {summary}. La aspettiamo!",
    "booking_cancelled": "D'accordo, ho annullato. Posso aiutarla in altro modo?",

    # Errors and clarifications
    "service_not_understood": "Mi scusi, non ho capito il servizio. Può scegliere tra: taglio, piega, colore, barba o trattamento.",
    "date_not_understood": "Non ho capito la data. Può dire ad esempio 'domani', 'lunedì' o '15 gennaio'?",
    "time_not_understood": "Non ho capito l'orario. Può dire ad esempio 'alle 15', 'di pomeriggio' o 'alle 9 e mezza'?",

    # Interruptions
    "reset_ack": "D'accordo, ricominciamo. Quale servizio desidera?",
    "change_ack": "Certo, mi dica cosa vuole cambiare.",
    "operator_escalate": "La metto in contatto con un operatore, un attimo...",

    # Approximate time handling
    "time_approximate": "Per {preference} abbiamo disponibilità alle {slots}. Quale preferisce?",

    # New client registration
    "propose_registration": "Non ho trovato il suo nominativo in archivio. Vuole che la registri come nuovo cliente?",
    "ask_surname": "Perfetto! Qual è il suo cognome?",
    "ask_phone": "Grazie {name}! Mi può dare un numero di telefono per eventuali comunicazioni?",
    "confirm_registration": "Riepilogo registrazione: {name} {surname}, telefono {phone}. Confermo?",
    "registration_complete": "Benvenuto {name}! La registrazione è completata. Procediamo con la prenotazione?",
    "registration_cancelled": "Va bene, nessun problema. Posso aiutarla in altro modo?",
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
        vertical: str = "salone"
    ):
        """
        Initialize state machine.

        Args:
            services_config: Service synonyms mapping (default: DEFAULT_SERVICES)
            reference_date: Reference date for testing (default: now)
            vertical: Business vertical (salone, palestra, medical, auto, restaurant)
        """
        self.services_config = services_config or DEFAULT_SERVICES
        self.reference_date = reference_date
        self.context = BookingContext(vertical=vertical)

    def reset(self):
        """Reset state machine to IDLE."""
        self.context = BookingContext()

    def set_context(self, context: BookingContext):
        """Set context (for resuming conversations)."""
        self.context = context

    def get_context(self) -> BookingContext:
        """Get current context."""
        return self.context

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

        elif state == BookingState.REGISTERING_PHONE:
            return self._handle_registering_phone(user_input, extracted)

        elif state == BookingState.REGISTERING_CONFIRM:
            return self._handle_registering_confirm(user_input, extracted)

        elif state in [BookingState.COMPLETED, BookingState.CANCELLED]:
            # Reset and start new booking flow
            self.reset()
            return self._handle_idle(user_input, extracted)

        # Fallback
        return StateMachineResult(
            next_state=self.context.state,
            response="Mi scusi, non ho capito. Può ripetere?"
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
        # But skip if we're in CONFIRMING state with a specific "cambio X" pattern
        # (those are handled by _handle_confirming for precise state changes)
        if self.context.state == BookingState.CONFIRMING:
            change_targets = ["servizio", "data", "giorno", "ora", "orario", "quando"]
            if any(target in text_lower for target in change_targets):
                # Let _handle_confirming handle this for state-specific changes
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

        # Have name - trigger DB lookup and continue with service
        if self.context.client_name:
            if self.context.service:
                # Have name + service - ask for date
                self.context.state = BookingState.WAITING_DATE
                return StateMachineResult(
                    next_state=BookingState.WAITING_DATE,
                    response=TEMPLATES["ask_date"].format(
                        service=self.context.service_display or self.context.service
                    ),
                    needs_db_lookup=True,
                    lookup_type="client",
                    lookup_params={"name": self.context.client_name}
                )
            else:
                # Have name only - ask for service
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response=TEMPLATES["ask_service"],
                    needs_db_lookup=True,
                    lookup_type="client",
                    lookup_params={"name": self.context.client_name}
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
            # Name collected - need client lookup
            self.context.state = BookingState.WAITING_SERVICE
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response=TEMPLATES["ask_service"],
                needs_db_lookup=True,
                lookup_type="client",
                lookup_params={"name": self.context.client_name}
            )

        # Try to extract name from raw text (regex patterns)
        name = extract_name(text)
        if name:
            self.context.client_name = name.name
            self.context.state = BookingState.WAITING_SERVICE
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response=f"Piacere {name.name}! " + TEMPLATES["ask_service"],
                needs_db_lookup=True,
                lookup_type="client",
                lookup_params={"name": name.name}
            )

        # Fallback: Try spaCy NER for person names
        # This handles cases where user just says "Mario Rossi" without context
        try:
            import spacy
            nlp = spacy.load("it_core_news_sm")
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PER":
                    # Found a person entity
                    extracted_name = ent.text.strip()
                    # Capitalize properly
                    extracted_name = ' '.join(word.capitalize() for word in extracted_name.split())
                    self.context.client_name = extracted_name
                    self.context.state = BookingState.WAITING_SERVICE
                    return StateMachineResult(
                        next_state=BookingState.WAITING_SERVICE,
                        response=f"Piacere {extracted_name}! " + TEMPLATES["ask_service"],
                        needs_db_lookup=True,
                        lookup_type="client",
                        lookup_params={"name": extracted_name}
                    )
        except Exception:
            pass  # spaCy not available, continue to fallback

        # Couldn't extract name
        return StateMachineResult(
            next_state=BookingState.WAITING_NAME,
            response="Non ho capito il nome. Può ripeterlo?"
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

        # Couldn't extract service
        return StateMachineResult(
            next_state=BookingState.WAITING_SERVICE,
            response=TEMPLATES["service_not_understood"]
        )

    def _handle_waiting_date(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_DATE state."""
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
        return StateMachineResult(
            next_state=BookingState.WAITING_DATE,
            response=TEMPLATES["date_not_understood"]
        )

    def _handle_waiting_time(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle WAITING_TIME state."""
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
                f"Le faremo una conferma via SMS. Grazie!"
            )
        elif vertical == "palestra":
            return f"Fantastico! Ho prenotato {summary}. A presto!"
        elif vertical == "medical":
            return (
                f"Prenotazione confermata! {summary}. "
                f"Ricordi la documentazione necessaria. Grazie!"
            )
        elif vertical == "auto":
            return f"Perfetto! {summary}. La contatteremo per aggiornamenti."
        elif vertical == "restaurant":
            return f"Tavolo riservato! {summary}. Vi aspettiamo!"

        return TEMPLATES["booking_confirmed"].format(summary=summary)

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
            self.context.state = BookingState.COMPLETED
            booking = {
                "service": self.context.service,
                "date": self.context.date,
                "time": self.context.time,
                "client_name": self.context.client_name,
                "client_id": self.context.client_id,
                "operator_name": self.context.operator_name,
                "operator_id": self.context.operator_id,
                "created_at": datetime.now().isoformat(),
            }
            return StateMachineResult(
                next_state=BookingState.COMPLETED,
                response=self._build_booking_confirmation_message(),
                booking=booking,
                should_exit=True
            )

        # =====================================================================
        # PHASE 5: Pure negative (NO new entities) → CANCEL
        # =====================================================================
        _, has_rejection = self._detect_correction_or_rejection_signal(text_lower)
        if has_rejection:
            self.context.state = BookingState.CANCELLED
            return StateMachineResult(
                next_state=BookingState.CANCELLED,
                response="Peccato! Se cambi idea, chiamaci pure. Arrivederci!",
                should_exit=True
            )

        # =====================================================================
        # PHASE 6: Fallback → clarification
        # =====================================================================
        self.context.clarifications_asked += 1
        if self.context.clarifications_asked > 2:
            response = (
                "Scusa, non riesco a capire bene. "
                "Dimmi per favore: sì per confermare o no per cambiare qualcosa?"
            )
        else:
            response = f"Per confermare: {self.context.get_summary()}. Va bene?"

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
                # Full name provided: "Mario Rossi"
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
            }
            clean_words = [w for w in raw_words if w.lower() not in _BLACKLIST and len(w) >= 2]

            if clean_words:
                clean_name, clean_surname = sanitize_name_pair(
                    ' '.join(clean_words), None
                )
                if clean_name and clean_surname:
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
                return StateMachineResult(
                    next_state=BookingState.REGISTERING_SURNAME,
                    response="Non ho capito. Può dirmi il suo nome e cognome?"
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
            response="Non ho capito. Può dirmi il suo nome e cognome?"
        )

    def _handle_registering_phone(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle REGISTERING_PHONE state - collect phone number."""
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
            # Got phone - go to confirmation
            self.context.state = BookingState.REGISTERING_CONFIRM
            return StateMachineResult(
                next_state=BookingState.REGISTERING_CONFIRM,
                response=TEMPLATES["confirm_registration"].format(
                    name=self.context.client_name or "",
                    surname=self.context.client_surname or "",
                    phone=self.context.client_phone
                )
            )

        # Couldn't get phone - ask again
        return StateMachineResult(
            next_state=BookingState.REGISTERING_PHONE,
            response="Non ho capito il numero. Può ripeterlo? Ad esempio: 333 123 4567"
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
