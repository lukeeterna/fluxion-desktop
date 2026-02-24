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

            # Same day requested → always default to next week
            if days_ahead == 0:
                days_ahead = 7
            # "settimana prossima" + specific day → push to next week
            # Only when day is still in current week (weekday > today_weekday)
            # If weekday < today_weekday, modulo already wrapped to next week
            elif ("settimana prossima" in text_lower or "prossima settimana" in text_lower):
                if weekday > today_weekday:
                    days_ahead += 7

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

    # 3b. Check "fra/tra X giorni/settimane" (E1-S2)
    # Italian number words
    it_numbers = {
        'un': 1, 'uno': 1, 'una': 1,
        'due': 2, 'tre': 3, 'quattro': 4, 'cinque': 5,
        'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9, 'dieci': 10,
    }
    # Pattern with digits
    fra_pattern = r'(?:fra|tra)\s+(\d+)\s+(giorn[oi]|settiman[ae])'
    fra_match = re.search(fra_pattern, text_lower)
    if fra_match:
        num = int(fra_match.group(1))
        unit = fra_match.group(2)
        if unit.startswith('settiman'):
            days_delta = num * 7
        else:
            days_delta = num
        target_date = reference_date + timedelta(days=days_delta)
        return ExtractedDate(
            date=target_date,
            original_text=fra_match.group(0),
            confidence=0.9,
            is_relative=True
        )

    # Pattern with Italian number words (fra due settimane, tra una settimana)
    it_num_pattern = '|'.join(it_numbers.keys())
    fra_word_pattern = rf'(?:fra|tra)\s+({it_num_pattern})\s+(giorn[oi]|settiman[ae])'
    fra_word_match = re.search(fra_word_pattern, text_lower)
    if fra_word_match:
        num_word = fra_word_match.group(1)
        num = it_numbers.get(num_word, 1)
        unit = fra_word_match.group(2)
        if unit.startswith('settiman'):
            days_delta = num * 7
        else:
            days_delta = num
        target_date = reference_date + timedelta(days=days_delta)
        return ExtractedDate(
            date=target_date,
            original_text=fra_word_match.group(0),
            confidence=0.9,
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
# TIME EXTRACTION - Comprehensive Italian patterns
# =============================================================================

# Italian number words → digits (for Whisper transcriptions in words)
_ITALIAN_NUMBERS = {
    # Hours (longest first to avoid partial matches)
    "ventiquattro": "24", "ventitre": "23", "ventitré": "23",
    "ventidue": "22", "ventuno": "21", "diciannove": "19",
    "diciotto": "18", "diciassette": "17", "sedici": "16",
    "quindici": "15", "quattordici": "14", "tredici": "13",
    "dodici": "12", "undici": "11", "venti": "20",
    "dieci": "10", "nove": "9", "otto": "8", "sette": "7",
    "sei": "6", "cinque": "5", "quattro": "4", "tre": "3",
    "due": "2",
    # NOTE: "un"/"una" excluded - too common in Italian, causes
    # false matches ("un quarto" → "1 quarto" breaks patterns)
    # Minutes as words
    "cinquantacinque": "55", "cinquanta": "50",
    "quarantacinque": "45", "quaranta": "40",
    "trentacinque": "35", "trenta": "30", "venticinque": "25",
}


def _normalize_italian_numbers(text: str) -> str:
    """Replace Italian number words with digits for time extraction.
    Sorted longest-first to avoid partial matches (e.g. 'ventitre' before 'tre')."""
    result = text
    for word, digit in _ITALIAN_NUMBERS.items():
        result = re.sub(r'\b' + re.escape(word) + r'\b', digit, result)
    return result


def extract_time(text: str) -> Optional[ExtractedTime]:
    """
    Extract time from Italian natural language text.

    Comprehensive handling of ALL Italian time expressions.
    Patterns ordered by specificity: minutes-first to prevent
    "alle 17 e 30" from matching as "alle 17" (= 17:00).

    Exact (confidence 1.0):
        "alle 15:30", "le 15.30", "17 e 30", "5 e mezza",
        "le 8 e un quarto", "le 6 meno un quarto"
    With AM/PM (confidence 0.95):
        "le 5 del pomeriggio", "le 3 di notte"
    Approximate (confidence 0.85):
        "dopo le 17", "prima delle 14", "verso le 15"
    Slot-based (confidence 0.8):
        "mattina", "pomeriggio", "sera", "tardo pomeriggio"
    Range (confidence 0.7):
        "tra le 14 e le 16" (returns midpoint)
    """
    text_lower = text.lower().strip()

    # Phase 0: Normalize Italian number words to digits
    # "diciassette e trenta" → "17 e 30"
    text_n = _normalize_italian_numbers(text_lower)

    # Common prefix: "alle", "ore", "le", "per le", "entro le"
    _P = r'(?:alle|ore|le|per\s+le|entro\s+le)\s+'

    # =========================================================================
    # PHASE 1: Exact times WITH minutes (highest priority, check FIRST)
    # =========================================================================

    # --- "X e un quarto" → XX:15 ---
    m = re.search(_P + r'(\d{1,2})\s+e\s+un\s+quarto\b', text_n)
    if not m:
        m = re.search(r'\b(\d{1,2})\s+e\s+un\s+quarto\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 15), original_text=m.group(0),
                confidence=1.0, is_approximate=False
            )

    # --- "X meno un quarto" → (X-1):45 ---
    m = re.search(_P + r'(\d{1,2})\s+meno\s+un\s+quarto\b', text_n)
    if not m:
        m = re.search(r'\b(\d{1,2})\s+meno\s+un\s+quarto\b', text_n)
    if m:
        h = (int(m.group(1)) - 1) % 24
        return ExtractedTime(
            time=time(h, 45), original_text=m.group(0),
            confidence=1.0, is_approximate=False
        )

    # --- "X meno Y" → (X-1):(60-Y) ---
    m = re.search(_P + r'(\d{1,2})\s+meno\s+(\d{1,2})\b', text_n)
    if not m:
        m = re.search(r'\b(\d{1,2})\s+meno\s+(\d{1,2})\b', text_n)
    if m:
        h = (int(m.group(1)) - 1) % 24
        mins = 60 - int(m.group(2))
        if 0 <= mins <= 59:
            return ExtractedTime(
                time=time(h, mins), original_text=m.group(0),
                confidence=1.0, is_approximate=False
            )

    # --- "X e mezza/mezzo" → XX:30 ---
    m = re.search(_P + r'(\d{1,2})\s+e\s+(?:mezza|mezzo)\b', text_n)
    if not m:
        m = re.search(r'\b(\d{1,2})\s+e\s+(?:mezza|mezzo)\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 30), original_text=m.group(0),
                confidence=1.0, is_approximate=False
            )

    # --- "X e Y" (number e number) → XX:YY ---
    # Handles: "17 e 30", "alle 17 e 30", "le 5 e 45"
    m = re.search(_P + r'(\d{1,2})\s+e\s+(\d{1,2})\b', text_n)
    if not m:
        m = re.search(r'\b(\d{1,2})\s+e\s+(\d{1,2})\b', text_n)
    if m:
        h, mins = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mins <= 59:
            return ExtractedTime(
                time=time(h, mins), original_text=m.group(0),
                confidence=1.0, is_approximate=False
            )

    # --- "X:YY" or "X.YY" → XX:YY ---
    # Handles: "15:30", "alle 15.30", "le 17:00"
    m = re.search(_P + r'(\d{1,2})[:.](\d{2})\b', text_n)
    if not m:
        m = re.search(r'\b(\d{1,2})[:.](\d{2})\b', text_n)
    if m:
        h, mins = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mins <= 59:
            return ExtractedTime(
                time=time(h, mins), original_text=m.group(0),
                confidence=1.0, is_approximate=False
            )

    # =========================================================================
    # PHASE 2: Hour with AM/PM context
    # "le 5 del pomeriggio" → 17:00
    # =========================================================================
    m = re.search(
        r'(?:alle|ore|le)\s+(\d{1,2})\s+(?:del\s+pomeriggio|di\s+pomeriggio|di\s+sera|della?\s+sera)',
        text_n
    )
    if m:
        h = int(m.group(1))
        if h <= 12:
            h += 12
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.95, is_approximate=False
            )

    m = re.search(
        r'(?:alle|ore|le)\s+(\d{1,2})\s+(?:del\s+mattino|di\s+mattina|della?\s+mattina)',
        text_n
    )
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.95, is_approximate=False
            )

    # =========================================================================
    # PHASE 3: Time range "tra le X e le Y" → midpoint
    # Must check BEFORE hour-only to avoid "le 14" matching from "tra le 14 e le 16"
    # =========================================================================
    m = re.search(r'tra\s+le\s+(\d{1,2})\s+e\s+le\s+(\d{1,2})', text_n)
    if m:
        start_h = int(m.group(1))
        end_h = int(m.group(2))
        if 0 <= start_h <= 23 and 0 <= end_h <= 23:
            mid_h = (start_h + end_h) // 2
            return ExtractedTime(
                time=time(mid_h, 0),
                original_text=m.group(0),
                confidence=0.7,
                is_approximate=True
            )

    # =========================================================================
    # PHASE 4: Approximate patterns
    # Must check BEFORE hour-only to avoid "le 17" matching from "dopo le 17"
    # =========================================================================

    # "dopo le X e Y" / "dopo le X"
    m = re.search(r'dopo\s+le\s+(\d{1,2})\s+e\s+(\d{1,2})\b', text_n)
    if m:
        h, mins = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mins <= 59:
            return ExtractedTime(
                time=time(h, mins), original_text=m.group(0),
                confidence=0.85, is_approximate=True
            )

    m = re.search(r'dopo\s+le\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.85, is_approximate=True
            )

    # "prima delle X"
    m = re.search(r'prima\s+delle?\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.85, is_approximate=True
            )

    # "verso le X", "intorno alle X", "circa alle X", "sulle X"
    m = re.search(r'(?:verso\s+le|intorno\s+alle?|circa\s+alle?|sulle)\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.8, is_approximate=True
            )

    # =========================================================================
    # PHASE 5: Hour-only exact (LAST of prefix patterns)
    # "alle 17", "le 5", "ore 10"
    # =========================================================================
    m = re.search(r'(?:alle|ore|le)\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=1.0, is_approximate=False
            )

    # =========================================================================
    # PHASE 6: Time slot keywords (longest-first)
    # "mattina", "pomeriggio", "sera", "tardo pomeriggio"
    # =========================================================================
    for slot_name, slot_enum in TIME_SLOTS:
        if slot_name in text_n:
            hour, minute = map(int, slot_enum.value.split(':'))
            return ExtractedTime(
                time=time(hour, minute),
                original_text=slot_name,
                confidence=0.8,
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

    # =========================================================================
    # BLACKLIST: Words that should NOT be extracted as names
    # =========================================================================
    # These are common Italian words that regex might incorrectly match as names
    NAME_BLACKLIST = {
        # Adverbs/expressions that look like names
        "mai", "sempre", "spesso", "forse", "quasi", "molto", "poco",
        # Common verbs in past participle that look like names
        "stato", "venuto", "andato", "fatto", "detto", "visto",
        # Common Italian verbs (infinitive + conjugations) that STT may capitalize
        "vorrei", "voglio", "volevo", "vorrebbe",
        "prenotare", "prenoterei", "prenoto",
        "chiamare", "chiamo", "chiamerei",
        "prendere", "prendo", "prenderei",
        "avere", "essere", "fare", "andare", "vedere",
        "sapere", "potere", "dovere",
        "parlare", "parlo", "chiedere", "chiedo",
        "disdire", "annullare", "spostare", "cambiare", "modificare",
        "confermare", "confermo",
        # Expressions with "mai"
        "volta",  # "prima volta"
        # Other common words
        "cliente", "nuovo", "nuova", "prima", "primo",
        # Booking-related words that STT may capitalize
        "appuntamento", "prenotazione", "taglio", "piega", "barba",
        "trattamento", "servizio", "visita",
        "calla", "grazie", "prego", "scusi", "buongiorno", "arrivederci",
        # Pronouns, articles and function words STT may capitalize
        "vi", "ho", "mi", "si", "se", "ci", "ne", "lo", "la", "le", "li",
        "il", "un", "una", "uno", "gli", "dei", "delle", "del",
        # Common verbs/adverbs that appear in frustration phrases
        "appena", "già", "proprio", "anche", "ancora", "allora",
        "ecco", "bene", "male", "pure", "solo", "tanto",
        # Filler phrases STT captures as names
        "cognome", "nome", "mio", "suo", "è",
        # Interjections STT may capitalize
        "ehi", "eh", "oh", "ah", "ahi", "uhm", "ehm", "boh", "mah", "beh",
        "senti", "senta", "scolta", "ascolta", "aspetta", "aspetti",
        # Greetings/farewells that STT capitalizes
        "ciao", "salve", "buonasera", "buonanotte", "addio",
        "tutti", "arrivederla", "saluti",
        # Common words that appear in conversational closings
        "grazie", "niente", "basta", "stop", "fine", "ok",
        # Temporal/date words that should NEVER be names
        # (bug: "prenotare per domani" → "Domani" extracted as name)
        "domani", "dopodomani", "oggi", "ieri",
        "lunedi", "lunedì", "martedi", "martedì",
        "mercoledi", "mercoledì", "giovedi", "giovedì",
        "venerdi", "venerdì", "sabato", "domenica",
        "mattina", "pomeriggio", "sera", "notte",
        "settimana", "mese", "anno", "giorno", "giorni",
        "alle", "ore", "dopo", "prima", "tardi", "presto",
    }

    # Check for NEW CLIENT indicators - these should not trigger name extraction
    NEW_CLIENT_PATTERNS = [
        r"mai\s+stato",          # "mai stato da voi"
        r"mai\s+venuto",         # "mai venuto"
        r"prima\s+volta",        # "prima volta che vengo"
        r"non\s+sono\s+mai",     # "non sono mai stato"
        r"nuovo\s+cliente",      # "sono un nuovo cliente"
        r"nuova\s+cliente",      # "sono una nuova cliente"
        r"non\s+sono\s+cliente", # "non sono cliente"
    ]

    # If text matches new client patterns, return None (don't extract name)
    for pattern in NEW_CLIENT_PATTERNS:
        if re.search(pattern, text_lower):
            return None

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
        # NOTE: article must be followed by SPACE to avoid "Laura" → "la" + "Ura" bug
        (r'(?:sono|io\s+sono)\s+(?:(?:il|la|lo)\s+)?([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)', 0.95),
    ]

    for pattern, confidence in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()

            # Strip trailing blacklisted words (e.g., "Antonio Vorrei" → "Antonio")
            name_words = name.split()
            cleaned_words = []
            for word in name_words:
                if word.lower() in NAME_BLACKLIST:
                    break  # Stop at first blacklisted word
                cleaned_words.append(word)

            # If ALL words were blacklisted, skip this match
            if not cleaned_words:
                continue

            name = ' '.join(word.capitalize() for word in cleaned_words)

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
    # Blacklist of common Italian words that are NOT operator names
    # These get falsely matched by "vorrei X" pattern
    OPERATOR_BLACKLIST = {
        # Verbs (infinitive and common conjugations)
        "prenotare", "prenotazione", "prenoto", "prendere", "parlare",
        "sapere", "avere", "essere", "fare", "andare", "vedere", "chiedere",
        "chiamare", "cambiare", "annullare", "disdire", "confermare",
        "vorrei", "voglio", "volevo", "preferirei", "preferisco",
        # Service words
        "taglio", "piega", "colore", "barba", "trattamento", "manicure",
        "pedicure", "massaggio", "ceretta", "extension",
        # Common nouns
        "appuntamento", "informazioni", "info", "orario", "prezzo",
        "costo", "servizio", "giorno", "ora", "settimana", "mese",
        # Articles, prepositions and pronouns
        "un", "una", "uno", "il", "la", "lo", "le", "gli", "che", "chi",
        "per", "con", "da", "di", "in", "su", "tra", "fra", "al", "del",
        # Time/schedule words that follow "preferisco" but aren't names
        "dopo", "prima", "tardi", "presto", "domani", "oggi", "sempre",
        "subito", "adesso", "mattina", "pomeriggio", "sera", "notte",
    }

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
            name_words = name.split()

            # Filter out blacklisted words from the name
            # Keep only words that could be proper names
            valid_words = [w for w in name_words if w.lower() not in OPERATOR_BLACKLIST]

            # If no valid words remain, skip this match
            if not valid_words:
                continue

            # Capitalize properly
            name = ' '.join(word.capitalize() for word in valid_words)

            return ExtractedOperator(
                name=name,
                original_text=match.group(0),
                confidence=confidence
            )

    return None


# =============================================================================
# GENERIC OPERATOR EXTRACTION (B3)
# =============================================================================

def extract_generic_operator(user_text: str) -> Dict:
    """
    Extract generic operator requests without a specific name.

    Returns:
        Dict with gender ("M", "F", None), name (None), is_generic (bool)
    """
    user_lower = user_text.lower().strip()

    female_patterns = [
        r"con\s+un[a']?\s*operatrice",
        r"con\s+una?\s+donna",
        r"preferisco\s+una?\s+donna",
        r"vorrei\s+una?\s+ragazza",
        r"una\s+donna\s+se\s+possibile",
        r"preferibilmente\s+(?:una?\s+)?donna",
    ]

    male_patterns = [
        r"con\s+un\s+operatore",
        r"con\s+un\s+uomo",
        r"preferisco\s+un\s+uomo",
        r"vorrei\s+un\s+ragazzo",
        r"un\s+uomo\s+se\s+possibile",
        r"preferibilmente\s+(?:un\s+)?uomo",
    ]

    generic_patterns = [
        r"con\s+qualcuno\s+di\s+bravo",
        r"chi\s+è\s+disponibile",
        r"con\s+chi\s+volete",
        r"scegliete\s+voi",
    ]

    for pattern in female_patterns:
        if re.search(pattern, user_lower):
            return {"gender": "F", "name": None, "is_generic": True}

    for pattern in male_patterns:
        if re.search(pattern, user_lower):
            return {"gender": "M", "name": None, "is_generic": True}

    for pattern in generic_patterns:
        if re.search(pattern, user_lower):
            return {"gender": None, "name": None, "is_generic": True}

    return {"gender": None, "name": None, "is_generic": False}


def select_operator_for_gender(
    gender: Optional[str],
    available_operators: List[Dict],
) -> Optional[Dict]:
    """Select an operator matching the requested gender, or first available."""
    if not available_operators:
        return None
    if gender is None:
        return available_operators[0]
    filtered = [op for op in available_operators if op.get("gender") == gender]
    return filtered[0] if filtered else available_operators[0]


# =============================================================================
# SERVICE EXTRACTION (E1-S3: Fuzzy Matching)
# =============================================================================

def _levenshtein_ratio(s1: str, s2: str) -> float:
    """
    Calculate Levenshtein similarity ratio between two strings.
    Returns value between 0.0 (completely different) and 1.0 (identical).
    """
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    # Simple Levenshtein distance implementation
    len1, len2 = len(s1), len(s2)
    if len1 > len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1

    current_row = range(len1 + 1)
    for i in range(1, len2 + 1):
        previous_row, current_row = current_row, [i] + [0] * len1
        for j in range(1, len1 + 1):
            add, delete, change = previous_row[j] + 1, current_row[j-1] + 1, previous_row[j-1]
            if s1[j-1] != s2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)

    distance = current_row[len1]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)


def extract_service(
    text: str,
    services_config: Dict[str, List[str]],
    fuzzy_threshold: float = 0.8
) -> Optional[Tuple[str, float]]:
    """
    Extract service name using synonym matching with fuzzy fallback.

    E1-S3: Supports typo tolerance (e.g., "coloure" → "Colore")

    Args:
        text: Input text
        services_config: Dict mapping service_id to list of synonyms
            Example: {"taglio": ["taglio", "sforbiciata", "spuntatina"]}
        fuzzy_threshold: Minimum similarity for fuzzy match (default 0.8)

    Returns:
        Tuple of (service_id, confidence) or None
    """
    text_lower = text.lower().strip()
    words = text_lower.split()

    best_match = None
    best_confidence = 0.0

    # Phase 1: Exact substring matching (fast path)
    for service_id, synonyms in services_config.items():
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            if synonym_lower in text_lower:
                # Exact match gets higher confidence
                confidence = 1.0 if synonym_lower == text_lower else 0.95
                if confidence > best_confidence:
                    best_match = service_id
                    best_confidence = confidence

    # Phase 2: Fuzzy matching if no exact match (E1-S3)
    if best_confidence < 0.9:
        for service_id, synonyms in services_config.items():
            for synonym in synonyms:
                synonym_lower = synonym.lower()
                # Try each word in the input
                for word in words:
                    if len(word) < 3:  # Skip short words
                        continue
                    ratio = _levenshtein_ratio(word, synonym_lower)
                    # Apply penalty first, then check threshold
                    penalized_ratio = ratio * 0.95  # Slight penalty for fuzzy
                    if ratio >= fuzzy_threshold and penalized_ratio > best_confidence:
                        best_match = service_id
                        best_confidence = penalized_ratio

    return (best_match, best_confidence) if best_match else None


def extract_services(
    text: str,
    services_config: Dict[str, List[str]],
    fuzzy_threshold: float = 0.8
) -> List[Tuple[str, float]]:
    """
    Extract MULTIPLE services from text with fuzzy matching.

    E1-S3: Supports typo tolerance for multiple services

    Args:
        text: Input text (e.g., "taglio e barba")
        services_config: Dict mapping service_id to list of synonyms
        fuzzy_threshold: Minimum similarity for fuzzy match (default 0.8)

    Returns:
        List of (service_id, confidence) tuples for all found services
    """
    text_lower = text.lower()
    words = text_lower.split()
    found_services = []
    found_ids = set()  # Avoid duplicates

    # Phase 1: Exact substring matching
    for service_id, synonyms in services_config.items():
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            if synonym_lower in text_lower and service_id not in found_ids:
                confidence = 1.0 if synonym_lower == text_lower.strip() else 0.95
                found_services.append((service_id, confidence))
                found_ids.add(service_id)
                break

    # Phase 2: Fuzzy matching for remaining words
    for service_id, synonyms in services_config.items():
        if service_id in found_ids:
            continue
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            for word in words:
                if len(word) < 3:
                    continue
                ratio = _levenshtein_ratio(word, synonym_lower)
                if ratio >= fuzzy_threshold and service_id not in found_ids:
                    found_services.append((service_id, ratio * 0.9))
                    found_ids.add(service_id)
                    break
            if service_id in found_ids:
                break

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

    def __post_init__(self):
        """Ensure services is never None (for test compatibility)."""
        if self.services is None:
            self.services = []

    @property
    def dates(self) -> List[ExtractedDate]:
        """Return list of dates (for test compatibility)."""
        return [self.date] if self.date else []

    @property
    def confidence(self) -> float:
        """Calculate overall extraction confidence (for test compatibility)."""
        confidences = []
        if self.date:
            confidences.append(self.date.confidence)
        if self.time:
            confidences.append(self.time.confidence)
        if self.name:
            confidences.append(self.name.confidence)
        if self.services:
            confidences.append(0.9)
        if self.phone:
            confidences.append(1.0)
        if self.email:
            confidences.append(1.0)
        
        if not confidences:
            return 0.0
        return sum(confidences) / len(confidences)

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


# Default salon services config for test compatibility (CoVe 2026)
DEFAULT_SERVICES_CONFIG = {
    "taglio": ["taglio", "tagli", "tagliarmi", "tagliarsi", "tagliare", "tagliarsi i capelli", "capelli", "capello"],
    "colore": ["colore", "colorare", "tinta", "tingere", "tingo", "colorazione"],
    "barba": ["barba", "barbe", "barbiere", "radere", "rasatura"],
    "piega": ["piega", "piegare", "asciugare", "phon", "piastra"],
    "trattamento": ["trattamento", "trattamenti", "cura", "maschera", "maschere"],
    "shampoo": ["shampoo", "lavaggio", "lavare", "lavata"],
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
        services_config: Optional service synonyms config (uses DEFAULT_SERVICES_CONFIG if None)
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

    # CoVe 2026: Use default config if none provided (for test compatibility)
    config = services_config if services_config else DEFAULT_SERVICES_CONFIG
    
    # Extract multiple services
    services_results = extract_services(text, config)
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
