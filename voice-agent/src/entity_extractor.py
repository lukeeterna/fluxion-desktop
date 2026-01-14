"""
FLUXION Voice Agent - Entity Extractor

Extracts structured entities from Italian natural language:
- Dates: "domani", "lunedì", "15 gennaio", "la prossima settimana"
- Times: "alle 15", "di pomeriggio", "mattina presto"
- Names: "sono Mario", "mi chiamo Laura"
- Services: matched against verticale config
- Phone/Email: standard regex patterns

Performance targets:
- Date extraction: <10ms
- Time extraction: <5ms
- Name extraction: <5ms
- Total: <20ms
"""

import re
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Try to import dateparser for advanced date parsing
try:
    import dateparser
    HAS_DATEPARSER = True
except ImportError:
    HAS_DATEPARSER = False
    print("[WARN] dateparser not installed, using fallback date parsing")


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class TimeSlot(Enum):
    """Time slots for approximate time extraction."""
    MATTINA_PRESTO = "08:00"
    MATTINA = "10:00"
    MEZZOGIORNO = "12:00"
    PRANZO = "13:00"
    POMERIGGIO = "15:00"
    TARDO_POMERIGGIO = "17:00"
    SERA = "19:00"


@dataclass
class ExtractedDate:
    """Extracted date with confidence."""
    date: datetime
    original_text: str
    confidence: float
    is_relative: bool  # True for "domani", False for "15 gennaio"

    def to_string(self, format: str = "%Y-%m-%d") -> str:
        return self.date.strftime(format)

    def to_italian(self) -> str:
        """Format date in Italian style: "lunedì 15 gennaio"."""
        days_it = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
        months_it = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
                     "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]

        day_name = days_it[self.date.weekday()]
        day_num = self.date.day
        month_name = months_it[self.date.month - 1]

        return f"{day_name} {day_num} {month_name}"


@dataclass
class ExtractedTime:
    """Extracted time with confidence."""
    time: time
    original_text: str
    confidence: float
    is_approximate: bool  # True for "pomeriggio", False for "15:30"

    def to_string(self, format: str = "%H:%M") -> str:
        return self.time.strftime(format)


@dataclass
class ExtractedName:
    """Extracted person name."""
    name: str
    original_text: str
    confidence: float


@dataclass
class ExtractedOperator:
    """Extracted operator preference."""
    name: str
    original_text: str
    confidence: float


# =============================================================================
# ITALIAN DAY/MONTH MAPPINGS
# =============================================================================

# Day name to weekday (0=Monday, 6=Sunday)
DAYS_IT = {
    "lunedi": 0, "lunedì": 0,
    "martedi": 1, "martedì": 1,
    "mercoledi": 2, "mercoledì": 2,
    "giovedi": 3, "giovedì": 3,
    "venerdi": 4, "venerdì": 4,
    "sabato": 5,
    "domenica": 6,
}

# Month name to month number
MONTHS_IT = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}

# Relative date keywords (ordered by length - longest first to avoid substring matches)
RELATIVE_DATES = [
    ("dopodomani", 2),
    ("domani", 1),
    ("oggi", 0),
    ("ieri", -1),
]

# Time slot keywords (ordered by length - longest first to avoid substring matches)
TIME_SLOTS = [
    ("tardo pomeriggio", TimeSlot.TARDO_POMERIGGIO),
    ("fine pomeriggio", TimeSlot.TARDO_POMERIGGIO),
    ("mattina presto", TimeSlot.MATTINA_PRESTO),
    ("nel pomeriggio", TimeSlot.POMERIGGIO),
    ("prima mattina", TimeSlot.MATTINA_PRESTO),
    ("ora di pranzo", TimeSlot.PRANZO),
    ("mezzogiorno", TimeSlot.MEZZOGIORNO),
    ("pomeriggio", TimeSlot.POMERIGGIO),
    ("mattinata", TimeSlot.MATTINA),
    ("stasera", TimeSlot.SERA),
    ("mattina", TimeSlot.MATTINA),
    ("serata", TimeSlot.SERA),
    ("pranzo", TimeSlot.PRANZO),
    ("sera", TimeSlot.SERA),
]


# =============================================================================
# DATE EXTRACTION
# =============================================================================

def extract_date(text: str, reference_date: Optional[datetime] = None) -> Optional[ExtractedDate]:
    """
    Extract date from Italian natural language text.

    Handles:
    - Relative: "oggi", "domani", "dopodomani"
    - Day names: "lunedì", "martedì prossimo"
    - Explicit: "15 gennaio", "il 20"
    - Week references: "la prossima settimana", "questa settimana"

    Args:
        text: Input text in Italian
        reference_date: Reference date for relative calculations (default: now)

    Returns:
        ExtractedDate or None if no date found
    """
    if reference_date is None:
        reference_date = datetime.now()

    text_lower = text.lower().strip()

    # 1. Check relative dates first (most common)
    # List is ordered longest-first to avoid substring matches
    for keyword, days_delta in RELATIVE_DATES:
        if keyword in text_lower:
            target_date = reference_date + timedelta(days=days_delta)
            return ExtractedDate(
                date=target_date,
                original_text=keyword,
                confidence=1.0,
                is_relative=True
            )

    # 2. Check day names (e.g., "lunedì", "martedì prossimo")
    for day_name, weekday in DAYS_IT.items():
        if day_name in text_lower:
            # Calculate next occurrence of this weekday
            today_weekday = reference_date.weekday()
            days_ahead = (weekday - today_weekday) % 7

            # If it's today and "prossimo" is mentioned, go to next week
            if days_ahead == 0:
                if "prossimo" in text_lower or "prossima" in text_lower:
                    days_ahead = 7
                else:
                    # Same day - could be today or next week
                    # Default to next week to avoid past dates
                    days_ahead = 7

            target_date = reference_date + timedelta(days=days_ahead)
            return ExtractedDate(
                date=target_date,
                original_text=day_name,
                confidence=0.95,
                is_relative=True
            )

    # 3. Check "prossima settimana" / "questa settimana"
    if "prossima settimana" in text_lower or "settimana prossima" in text_lower:
        # Next Monday
        today_weekday = reference_date.weekday()
        days_until_monday = (7 - today_weekday) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        target_date = reference_date + timedelta(days=days_until_monday)
        return ExtractedDate(
            date=target_date,
            original_text="prossima settimana",
            confidence=0.85,
            is_relative=True
        )

    if "questa settimana" in text_lower:
        # Stay in current week - suggest tomorrow or next available day
        target_date = reference_date + timedelta(days=1)
        return ExtractedDate(
            date=target_date,
            original_text="questa settimana",
            confidence=0.75,
            is_relative=True
        )

    # 4. Check explicit dates: "15 gennaio", "il 20", "20/01"
    # Pattern: day + month name
    for month_name, month_num in MONTHS_IT.items():
        pattern = rf'(\d{{1,2}})\s*(?:di\s+)?{month_name}'
        match = re.search(pattern, text_lower)
        if match:
            day = int(match.group(1))
            year = reference_date.year

            # If date is in the past, assume next year
            try:
                target_date = datetime(year, month_num, day)
                if target_date < reference_date:
                    target_date = datetime(year + 1, month_num, day)

                return ExtractedDate(
                    date=target_date,
                    original_text=match.group(0),
                    confidence=0.95,
                    is_relative=False
                )
            except ValueError:
                # Invalid date (e.g., 31 febbraio)
                continue

    # Pattern: "il 20" (day only, assume current/next month)
    match = re.search(r'\bil\s+(\d{1,2})\b', text_lower)
    if match:
        day = int(match.group(1))
        if 1 <= day <= 31:
            year = reference_date.year
            month = reference_date.month

            try:
                target_date = datetime(year, month, day)
                if target_date < reference_date:
                    # Move to next month
                    if month == 12:
                        target_date = datetime(year + 1, 1, day)
                    else:
                        target_date = datetime(year, month + 1, day)

                return ExtractedDate(
                    date=target_date,
                    original_text=match.group(0),
                    confidence=0.8,
                    is_relative=False
                )
            except ValueError:
                pass

    # 5. Try dateparser as fallback (if available)
    if HAS_DATEPARSER:
        try:
            parsed = dateparser.parse(
                text,
                languages=['it'],
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': reference_date
                }
            )
            if parsed:
                return ExtractedDate(
                    date=parsed,
                    original_text=text,
                    confidence=0.7,
                    is_relative=False
                )
        except Exception:
            pass

    return None


# =============================================================================
# TIME EXTRACTION
# =============================================================================

def extract_time(text: str) -> Optional[ExtractedTime]:
    """
    Extract time from Italian natural language text.

    Handles:
    - Exact: "alle 15", "15:30", "ore 10"
    - Approximate: "di pomeriggio", "mattina", "sera"
    - Ranges: "tra le 14 e le 16" (returns midpoint)

    Args:
        text: Input text in Italian

    Returns:
        ExtractedTime or None if no time found
    """
    text_lower = text.lower().strip()

    # 1. Check exact time patterns first
    # Pattern: "alle 15", "alle 15:30", "ore 10", "10:30"
    patterns = [
        (r'(?:alle|ore)\s*(\d{1,2})[:.](\d{2})', True),  # alle 15:30
        (r'(?:alle|ore)\s*(\d{1,2})\b', False),  # alle 15
        (r'\b(\d{1,2})[:.](\d{2})\b', True),  # 15:30 (standalone)
        (r'\b(\d{1,2})\s*(?:e\s+(?:mezza|mezzo|trenta))', False),  # 15 e mezza
    ]

    for pattern, has_minutes in patterns:
        match = re.search(pattern, text_lower)
        if match:
            hour = int(match.group(1))

            if has_minutes and len(match.groups()) > 1:
                minute = int(match.group(2))
            elif "mezza" in text_lower or "mezzo" in text_lower or "trenta" in text_lower:
                minute = 30
            else:
                minute = 0

            # Validate hour (0-23)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return ExtractedTime(
                    time=time(hour, minute),
                    original_text=match.group(0),
                    confidence=1.0,
                    is_approximate=False
                )

    # 2. Check time slot keywords (list is ordered longest-first)
    for slot_name, slot_enum in TIME_SLOTS:
        if slot_name in text_lower:
            hour, minute = map(int, slot_enum.value.split(':'))
            return ExtractedTime(
                time=time(hour, minute),
                original_text=slot_name,
                confidence=0.8,
                is_approximate=True
            )

    # 3. Check time ranges: "tra le 14 e le 16"
    match = re.search(r'tra\s+le\s+(\d{1,2})\s+e\s+le\s+(\d{1,2})', text_lower)
    if match:
        start_hour = int(match.group(1))
        end_hour = int(match.group(2))
        if 0 <= start_hour <= 23 and 0 <= end_hour <= 23:
            # Return midpoint
            mid_hour = (start_hour + end_hour) // 2
            return ExtractedTime(
                time=time(mid_hour, 0),
                original_text=match.group(0),
                confidence=0.7,
                is_approximate=True
            )

    return None


# =============================================================================
# NAME EXTRACTION
# =============================================================================

def extract_name(text: str) -> Optional[ExtractedName]:
    """
    Extract person name from Italian text.

    Handles:
    - "sono Mario"
    - "mi chiamo Laura Rossi"
    - "chiamami Luca"
    - "il mio nome è Giovanni"
    - "sono il signor Bianchi"

    Args:
        text: Input text in Italian

    Returns:
        ExtractedName or None if no name found
    """
    text_lower = text.lower()

    # Patterns for name introduction (ordered by specificity - most specific first)
    patterns = [
        # "sono il signor/la signora Bianchi" - specific pattern first
        (r'sono\s+(?:il\s+signor|la\s+signora)\s+([A-Z][a-zàèéìòù]+)', 0.9),
        # "parlo per Mario Rossi" / "a nome di"
        (r'(?:parlo\s+per|a\s+nome\s+di)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)', 0.85),
        # "prenotazione per Mario Rossi" / "appuntamento per"
        (r'(?:prenotazione|appuntamento|prenota|prenotare)\s+per\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)', 0.9),
        # "per Mario Rossi" (standalone)
        (r'\bper\s+([A-Z][a-zàèéìòù]+\s+[A-Z][a-zàèéìòù]+)\b', 0.85),
        # "il mio nome è Giovanni"
        (r'(?:il\s+)?mio\s+nome\s+(?:è|e)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)', 0.95),
        # "mi chiamo Laura"
        (r'mi\s+chiamo\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)', 0.95),
        # "chiamami Luca"
        (r'chiamami\s+([A-Z][a-zàèéìòù]+)', 0.9),
        # "sono Mario", "sono la Maria" - most general, last
        (r'(?:sono|io\s+sono)\s+(?:il|la|lo)?\s*([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)', 0.95),
    ]

    for pattern, confidence in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Capitalize properly
            name = ' '.join(word.capitalize() for word in name.split())

            return ExtractedName(
                name=name,
                original_text=match.group(0),
                confidence=confidence
            )

    return None


# =============================================================================
# OPERATOR EXTRACTION
# =============================================================================

def extract_operator(text: str) -> Optional[ExtractedOperator]:
    """
    Extract operator preference from Italian text.

    Handles:
    - "con l'operatrice Laura"
    - "con l'operatore Marco"
    - "con Laura Neri"
    - "vorrei Laura"
    - "preferisco Marco"

    Args:
        text: Input text in Italian

    Returns:
        ExtractedOperator or None if no operator found
    """
    # Patterns for operator preference (ordered by specificity)
    # Note: Handle various apostrophe forms and spaces
    patterns = [
        # "con l'operatrice/operatore X" - handle ', ', l operatrice
        (r"con\s+l['\u2019\s]?\s*(?:operatrice|operatore)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)", 0.95),
        # "con la/il X" (operator context)
        (r"con\s+(?:la|il)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)", 0.9),
        # "con X Y" followed by name (2 words)
        (r"\bcon\s+([A-Z][a-zàèéìòù]+\s+[A-Z][a-zàèéìòù]+)\b", 0.85),
        # "con X" single name (not at start of sentence, likely operator context)
        (r"\bcon\s+([A-Z][a-zàèéìòù]+)\b(?!\s+(?:il|la|lo|un|una|l))", 0.8),
        # "vorrei/preferisco X"
        (r"(?:vorrei|preferisco|preferirei)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)", 0.75),
    ]

    for pattern, confidence in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Capitalize properly
            name = ' '.join(word.capitalize() for word in name.split())

            return ExtractedOperator(
                name=name,
                original_text=match.group(0),
                confidence=confidence
            )

    return None


# =============================================================================
# SERVICE EXTRACTION
# =============================================================================

def extract_service(text: str, services_config: Dict[str, List[str]]) -> Optional[Tuple[str, float]]:
    """
    Extract service name using synonym matching.

    Args:
        text: Input text
        services_config: Dict mapping service_id to list of synonyms
            Example: {"taglio": ["taglio", "sforbiciata", "spuntatina"]}

    Returns:
        Tuple of (service_id, confidence) or None
    """
    text_lower = text.lower()

    best_match = None
    best_confidence = 0.0

    for service_id, synonyms in services_config.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower:
                # Exact match
                confidence = 1.0 if synonym.lower() == text_lower.strip() else 0.9
                if confidence > best_confidence:
                    best_match = service_id
                    best_confidence = confidence

    return (best_match, best_confidence) if best_match else None


def extract_services(text: str, services_config: Dict[str, List[str]]) -> List[Tuple[str, float]]:
    """
    Extract MULTIPLE services from text.

    Args:
        text: Input text (e.g., "taglio e barba")
        services_config: Dict mapping service_id to list of synonyms

    Returns:
        List of (service_id, confidence) tuples for all found services
    """
    text_lower = text.lower()
    found_services = []
    found_ids = set()  # Avoid duplicates

    for service_id, synonyms in services_config.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower and service_id not in found_ids:
                confidence = 1.0 if synonym.lower() == text_lower.strip() else 0.9
                found_services.append((service_id, confidence))
                found_ids.add(service_id)
                break  # Found this service, move to next

    return found_services


# =============================================================================
# PHONE/EMAIL EXTRACTION
# =============================================================================

def extract_phone(text: str) -> Optional[str]:
    """
    Extract Italian phone number from text.

    Handles:
    - +39 333 1234567
    - 333.123.4567
    - 333 123 4567
    - 3331234567
    """
    # Remove common separators for matching
    patterns = [
        r'(?:\+39[-.\s]?)?3\d{2}[-.\s]?\d{3}[-.\s]?\d{4}',  # Mobile: 333 123 4567
        r'(?:\+39[-.\s]?)?0\d{1,3}[-.\s]?\d{6,8}',  # Landline: 02 12345678
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Normalize: keep only digits and leading +
            phone = match.group(0)
            normalized = re.sub(r'[^\d+]', '', phone)
            return normalized

    return None


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0).lower() if match else None


# =============================================================================
# COMBINED EXTRACTOR
# =============================================================================

@dataclass
class ExtractionResult:
    """Combined extraction result."""
    date: Optional[ExtractedDate] = None
    time: Optional[ExtractedTime] = None
    name: Optional[ExtractedName] = None
    service: Optional[str] = None
    services: Optional[List[str]] = None  # Multiple services
    operator: Optional[ExtractedOperator] = None  # Operator preference
    phone: Optional[str] = None
    email: Optional[str] = None

    def has_booking_info(self) -> bool:
        """Check if we have enough info for a booking."""
        return self.date is not None and self.time is not None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "date": self.date.to_string() if self.date else None,
            "date_italian": self.date.to_italian() if self.date else None,
            "time": self.time.to_string() if self.time else None,
            "name": self.name.name if self.name else None,
            "service": self.service,
            "services": self.services,
            "operator": self.operator.name if self.operator else None,
            "phone": self.phone,
            "email": self.email,
        }


def extract_all(
    text: str,
    services_config: Optional[Dict] = None,
    reference_date: Optional[datetime] = None
) -> ExtractionResult:
    """
    Extract all entities from text.

    Args:
        text: Input text
        services_config: Optional service synonyms config
        reference_date: Optional reference date for date extraction (for testing)

    Returns:
        ExtractionResult with all extracted entities
    """
    result = ExtractionResult()

    result.date = extract_date(text, reference_date)
    result.time = extract_time(text)
    result.name = extract_name(text)
    result.operator = extract_operator(text)  # Extract operator preference
    result.phone = extract_phone(text)
    result.email = extract_email(text)

    if services_config:
        # Extract multiple services
        services_results = extract_services(text, services_config)
        if services_results:
            result.services = [s[0] for s in services_results]
            result.service = services_results[0][0]  # First service for backwards compat

    return result


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Entity Extractor Test ===\n")

    test_cases = [
        # Dates
        ("Vorrei un appuntamento per domani", "date"),
        ("Mi prenota per lunedì?", "date"),
        ("Il 15 gennaio va bene", "date"),
        ("La prossima settimana", "date"),

        # Times
        ("Alle 15:30", "time"),
        ("Di pomeriggio", "time"),
        ("Verso le 10 e mezza", "time"),
        ("Tra le 14 e le 16", "time"),

        # Names
        ("Sono Mario Rossi", "name"),
        ("Mi chiamo Laura", "name"),
        ("Chiamami Luca", "name"),

        # Phone/Email
        ("Il mio numero è 333 123 4567", "phone"),
        ("Email: mario@email.com", "email"),

        # Combined
        ("Sono Mario, vorrei prenotare domani alle 15", "all"),
    ]

    for text, entity_type in test_cases:
        print(f"Input: \"{text}\"")

        if entity_type == "date":
            result = extract_date(text)
            if result:
                print(f"  → Date: {result.to_italian()} ({result.to_string()})")
                print(f"  → Confidence: {result.confidence:.2f}")
        elif entity_type == "time":
            result = extract_time(text)
            if result:
                print(f"  → Time: {result.to_string()}")
                print(f"  → Approximate: {result.is_approximate}")
        elif entity_type == "name":
            result = extract_name(text)
            if result:
                print(f"  → Name: {result.name}")
        elif entity_type == "phone":
            result = extract_phone(text)
            if result:
                print(f"  → Phone: {result}")
        elif entity_type == "email":
            result = extract_email(text)
            if result:
                print(f"  → Email: {result}")
        elif entity_type == "all":
            result = extract_all(text)
            print(f"  → {result.to_dict()}")

        print()
