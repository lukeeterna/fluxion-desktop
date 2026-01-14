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
        reference_date: Optional[datetime] = None
    ):
        """
        Initialize state machine.

        Args:
            services_config: Service synonyms mapping (default: DEFAULT_SERVICES)
            reference_date: Reference date for testing (default: now)
        """
        self.services_config = services_config or DEFAULT_SERVICES
        self.reference_date = reference_date
        self.context = BookingContext()

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

    def _update_context_from_extraction(self, extracted: ExtractionResult):
        """Update context with extracted entities."""
        if extracted.date and not self.context.date:
            self.context.date = extracted.date.to_string("%Y-%m-%d")
            self.context.date_display = extracted.date.to_italian()

        if extracted.time and not self.context.time:
            self.context.time = extracted.time.to_string()
            self.context.time_display = f"alle {extracted.time.to_string()}"
            self.context.time_is_approximate = extracted.time.is_approximate

        # Handle multiple services
        if extracted.services and not self.context.service:
            self.context.services = extracted.services
            self.context.service = extracted.services[0]  # Primary service
            # Build display string for all services
            display_names = [SERVICE_DISPLAY.get(s, s.capitalize()) for s in extracted.services]
            self.context.service_display = " e ".join(display_names)
        elif extracted.service and not self.context.service:
            self.context.service = extracted.service
            self.context.services = [extracted.service]
            self.context.service_display = SERVICE_DISPLAY.get(extracted.service, extracted.service.capitalize())

        # Handle operator preference
        if extracted.operator and not self.context.operator_name:
            self.context.operator_name = extracted.operator.name
            self.context.operator_requested = True

        if extracted.name and not self.context.client_name:
            self.context.client_name = extracted.name.name

        if extracted.phone and not self.context.client_phone:
            self.context.client_phone = extracted.phone

        if extracted.email and not self.context.client_email:
            self.context.client_email = extracted.email

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

        # Try to extract name from raw text
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

    def _handle_confirming(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle CONFIRMING state."""
        text_lower = text.lower()

        # Check if they want to change something FIRST
        # (must be before negative check because "giorno" contains "no")
        if "cambio" in text_lower or "cambia" in text_lower:
            # Determine what they want to change
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

        # Check for affirmative responses
        affirmative = ["sì", "si", "ok", "va bene", "d'accordo", "confermo", "perfetto", "certo", "esatto"]
        if any(word in text_lower for word in affirmative):
            self.context.state = BookingState.COMPLETED

            # Build booking data
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
                response=TEMPLATES["booking_confirmed"].format(summary=self.context.get_summary()),
                booking=booking,
                should_exit=True
            )

        # Check for negative responses (use word boundaries to avoid "giorno" matching "no")
        negative_patterns = [r"\bno\b", r"\bnope\b", r"\bannulla\b", r"\bcancella\b", r"\bnon voglio\b"]
        if any(re.search(pattern, text_lower) for pattern in negative_patterns):
            self.context.state = BookingState.CANCELLED
            return StateMachineResult(
                next_state=BookingState.CANCELLED,
                response=TEMPLATES["booking_cancelled"],
                should_exit=True
            )

        # Re-ask for confirmation
        return StateMachineResult(
            next_state=BookingState.CONFIRMING,
            response=f"Per confermare: {self.context.get_summary()}. Va bene?"
        )

    # =========================================================================
    # NEW CLIENT REGISTRATION HANDLERS
    # =========================================================================

    def _handle_propose_registration(self, text: str, extracted: ExtractionResult) -> StateMachineResult:
        """Handle PROPOSE_REGISTRATION state - ask if user wants to register."""
        text_lower = text.lower()

        # Check for affirmative responses
        affirmative = ["sì", "si", "ok", "va bene", "certo", "volentieri", "registrami", "registra"]
        if any(word in text_lower for word in affirmative):
            self.context.is_new_client = True
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
        """Handle REGISTERING_SURNAME state - collect surname."""
        # Try to extract surname from text
        # Simple heuristic: take first capitalized word or the whole input
        text_clean = text.strip()

        # Extract name if present
        if extracted.name:
            # Could be full name "Mario Rossi" → surname = Rossi
            parts = extracted.name.name.split()
            if len(parts) >= 2:
                self.context.client_surname = parts[-1]  # Last word as surname
            else:
                self.context.client_surname = text_clean.title()
        else:
            # Use the input as surname
            self.context.client_surname = text_clean.title()

        self.context.state = BookingState.REGISTERING_PHONE
        return StateMachineResult(
            next_state=BookingState.REGISTERING_PHONE,
            response=TEMPLATES["ask_phone"].format(name=self.context.client_name or "")
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
            # Registration confirmed - need to create client via API
            self.context.state = BookingState.WAITING_SERVICE
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,
                response=TEMPLATES["registration_complete"].format(
                    name=f"{self.context.client_name} {self.context.client_surname}".strip()
                ) + " " + TEMPLATES["ask_service"],
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
