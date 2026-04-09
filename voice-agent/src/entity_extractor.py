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
from dataclasses import dataclass, field
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


class TimeConstraintType(Enum):
    """World-class: TIMEX3 ISO standard — Dialogflow CX / Amazon Lex pattern."""
    EXACT           = "exact"           # "alle 15:30"
    AFTER           = "after"           # "dopo le 17" — 28% dei casi italiani
    BEFORE          = "before"          # "prima delle 14"
    AROUND          = "around"          # "verso le 15", "intorno alle 15"
    RANGE           = "range"           # "tra le 14 e le 16"
    SLOT            = "slot"            # "mattina", "pomeriggio"
    FIRST_AVAILABLE = "first_available" # "prima possibile", "quando siete liberi"


@dataclass
class TimeConstraint:
    """
    World-class temporal constraint — TIMEX3 ISO standard.
    Identico a Dialogflow CX / Amazon Lex / Cal.com.
    Preserva la semantica: "dopo le 17" → AFTER(17:00), non "17:00" esatto.
    """
    constraint_type: TimeConstraintType
    anchor_time: Optional[time] = None      # AFTER/BEFORE/AROUND/EXACT
    range_start: Optional[time] = None      # RANGE only
    range_end: Optional[time] = None        # RANGE only
    slot_name: Optional[str] = None         # SLOT: "mattina", "pomeriggio"
    original_text: str = ""
    confidence: float = 1.0

    def matches(self, candidate: time) -> bool:
        """True se il candidato soddisfa il constraint. Usato per filtrare slot disponibili."""
        if self.constraint_type == TimeConstraintType.EXACT:
            return candidate == self.anchor_time
        elif self.constraint_type == TimeConstraintType.AFTER:
            return candidate > self.anchor_time
        elif self.constraint_type == TimeConstraintType.BEFORE:
            return candidate < self.anchor_time
        elif self.constraint_type == TimeConstraintType.AROUND:
            delta = abs(
                (candidate.hour * 60 + candidate.minute) -
                (self.anchor_time.hour * 60 + self.anchor_time.minute)
            )
            return delta <= 30
        elif self.constraint_type == TimeConstraintType.RANGE:
            return self.range_start <= candidate <= self.range_end
        elif self.constraint_type in (TimeConstraintType.SLOT, TimeConstraintType.FIRST_AVAILABLE):
            return True
        return True

    def display(self) -> str:
        """Stringa display corretta per Sara — mai 'alle X' per constraint non-EXACT."""
        if self.constraint_type == TimeConstraintType.AFTER:
            return f"dopo le {self.anchor_time.strftime('%H:%M')}"
        elif self.constraint_type == TimeConstraintType.BEFORE:
            return f"prima delle {self.anchor_time.strftime('%H:%M')}"
        elif self.constraint_type == TimeConstraintType.AROUND:
            return f"verso le {self.anchor_time.strftime('%H:%M')}"
        elif self.constraint_type == TimeConstraintType.RANGE:
            return f"tra le {self.range_start.strftime('%H:%M')} e le {self.range_end.strftime('%H:%M')}"
        elif self.constraint_type == TimeConstraintType.EXACT:
            return f"alle {self.anchor_time.strftime('%H:%M')}"
        elif self.constraint_type == TimeConstraintType.FIRST_AVAILABLE:
            return "prima possibile"
        elif self.constraint_type == TimeConstraintType.SLOT:
            return f"in {self.slot_name}"
        return ""


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
    time_constraint: Optional["TimeConstraint"] = None  # World-class: TIMEX3 semantic preservation

    def to_string(self, format: str = "%H:%M") -> str:
        return self.time.strftime(format)

    def get_display(self) -> str:
        """Constraint-aware display — 'dopo le 17:00' non 'alle 17:00'."""
        if self.time_constraint and self.time_constraint.constraint_type != TimeConstraintType.EXACT:
            return self.time_constraint.display()
        return f"alle {self.to_string()}"


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


@dataclass
class ExtractedOperatorList:
    """Multiple operator preferences extracted from Italian text (GAP-P1-8)."""
    names: List[str]        # Ordered preference list (first = highest priority)
    is_any: bool            # True if 'chiunque'/'qualsiasi' fallback present
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
    # STT truncations — Whisper drops the final accented vowel
    "marted": 1,
    "gioved": 3,
    "venerd": 4,
    "mercoled": 2,
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

# Italian ordinal/cardinal words used in date context ("il sette", "il quindici")
_IT_NUMBERS_DATE = {
    'primo': 1, 'uno': 1, 'due': 2, 'tre': 3, 'quattro': 4, 'cinque': 5,
    'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9, 'dieci': 10,
    'undici': 11, 'dodici': 12, 'tredici': 13, 'quattordici': 14,
    'quindici': 15, 'sedici': 16, 'diciassette': 17, 'diciotto': 18,
    'diciannove': 19, 'venti': 20, 'ventuno': 21, 'ventidue': 22,
    'ventitre': 23, 'ventiquattro': 24, 'venticinque': 25,
    'ventisei': 26, 'ventisette': 27, 'ventotto': 28, 'ventinove': 29,
    'trenta': 30, 'trentuno': 31,
}


def _normalize_ordinals_in_date(text: str) -> str:
    """Replace "il <word_number>" → "il <digit>" for date pattern matching.
    Only substitutes within the "il <word>" construction to avoid false positives
    on phrases like "sei fortunato" or "tre volte".
    """
    result = text
    for word, num in _IT_NUMBERS_DATE.items():
        result = re.sub(rf'\bil\s+{word}\b', f'il {num}', result)
    return result


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
    # FIX-7: normalize "il sette" → "il 7", "il quindici" → "il 15", etc.
    # so that the "il \d{1,2}" pattern below picks them up correctly.
    text_lower = _normalize_ordinals_in_date(text_lower)

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

    # 3a. GAP-B6: "fine settimana" / "weekend" → prossimo sabato
    # Must be checked BEFORE DAYS_IT loop to intercept "sabato o domenica".
    # Check "prossimo weekend" FIRST (before plain "fine settimana") to avoid
    # partial match by the shorter pattern.
    _next_weekend_re = re.compile(
        r'\b(?:(?:il\s+)?prossim[oa]\s+(?:fine\s+settiman[ae]|weekend)|'
        r'(?:fine\s+settiman[ae]|weekend)\s+prossim[oa])\b',
        re.IGNORECASE
    )
    _weekend_re = re.compile(
        r'\b(?:(?:questo\s+)?fine\s+settiman[ae]|(?:questo\s+)?weekend|week[-\s]?end|'
        r'sabato\s+o\s+domenica|domenica\s+o\s+sabato)\b',
        re.IGNORECASE
    )

    def _next_saturday(ref: datetime, force_next: bool = False) -> datetime:
        """Return next Saturday relative to ref. force_next always skips current week."""
        today_wd = ref.weekday()  # 0=Mon … 5=Sat … 6=Sun
        if today_wd == 5:  # oggi è sabato
            days_ahead = 7  # sempre la prossima settimana (sabato già passato)
        elif today_wd == 6:  # oggi è domenica
            days_ahead = 6  # sabato della settimana prossima
        else:
            days_ahead = 5 - today_wd  # sabato di questa settimana
            if force_next:
                days_ahead += 7
        return ref + timedelta(days=days_ahead)

    if _next_weekend_re.search(text_lower):
        target_date = _next_saturday(reference_date, force_next=True)
        return ExtractedDate(
            date=target_date,
            original_text="prossimo weekend",
            confidence=0.92,
            is_relative=True
        )
    if _weekend_re.search(text_lower):
        target_date = _next_saturday(reference_date, force_next=False)
        return ExtractedDate(
            date=target_date,
            original_text="fine settimana",
            confidence=0.92,
            is_relative=True
        )

    # 3b. Check "fra/tra X giorni/settimane/mesi" (E1-S2, extended with GAP-B2)
    # Italian number words
    it_numbers = {
        'un': 1, 'uno': 1, 'una': 1,
        'due': 2, 'tre': 3, 'quattro': 4, 'cinque': 5,
        'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9, 'dieci': 10,
    }
    # Pattern with digits — extended to include mes[ei] (GAP-B2)
    fra_pattern = r'(?:fra|tra)\s+(\d+)\s+(giorn[oi]|settiman[ae]|mes[ei])'
    fra_match = re.search(fra_pattern, text_lower)
    if fra_match:
        num = int(fra_match.group(1))
        unit = fra_match.group(2)
        if unit.startswith('settiman'):
            days_delta = num * 7
        elif unit.startswith('mes'):
            days_delta = num * 30
        else:
            days_delta = num
        target_date = reference_date + timedelta(days=days_delta)
        return ExtractedDate(
            date=target_date,
            original_text=fra_match.group(0),
            confidence=0.9,
            is_relative=True
        )

    # Pattern with Italian number words — extended to include mes[ei] (GAP-B2)
    it_num_pattern = '|'.join(it_numbers.keys())
    fra_word_pattern = rf'(?:fra|tra)\s+({it_num_pattern})\s+(giorn[oi]|settiman[ae]|mes[ei])'
    fra_word_match = re.search(fra_word_pattern, text_lower)
    if fra_word_match:
        num_word = fra_word_match.group(1)
        num = it_numbers.get(num_word, 1)
        unit = fra_word_match.group(2)
        if unit.startswith('settiman'):
            days_delta = num * 7
        elif unit.startswith('mes'):
            days_delta = num * 30
        else:
            days_delta = num
        target_date = reference_date + timedelta(days=days_delta)
        return ExtractedDate(
            date=target_date,
            original_text=fra_word_match.group(0),
            confidence=0.9,
            is_relative=True
        )

    # 3c. GAP-B2: "il mese prossimo" / "mese prossimo" / "prossimo mese"
    # → primo giorno del mese successivo (anchor semantics, differs from "fra un mese")
    if re.search(r'\b(?:il\s+)?mes[ei]\s+prossim[oa]\b|\bprossim[oa]\s+mes[ei]\b', text_lower):
        year = reference_date.year
        month = reference_date.month
        if month == 12:
            target_date = datetime(year + 1, 1, 1)
        else:
            target_date = datetime(year, month + 1, 1)
        return ExtractedDate(
            date=target_date,
            original_text="mese prossimo",
            confidence=0.90,
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

    # FIX-8: explicit guard for "il primo" / "primo del mese" → day 1.
    # _normalize_ordinals_in_date() above already converts "il primo" → "il 1"
    # so the pattern below captures it; this guard handles residual forms like
    # bare "primo" without "il" that bypass normalization.
    if re.search(r'\bprimo\b', text_lower) and not re.search(r'\bil\s+1\b', text_lower):
        year = reference_date.year
        month = reference_date.month
        target_date = datetime(year, month, 1)
        if target_date.date() <= reference_date.date():
            if month == 12:
                target_date = datetime(year + 1, 1, 1)
            else:
                target_date = datetime(year, month + 1, 1)
        return ExtractedDate(
            date=target_date,
            original_text="primo",
            confidence=0.9,
            is_relative=True,
        )

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


# Semantic anchors italiani → TimeConstraint (TIMEX3 compliant)
# World-class: Cal.com / Dialogflow CX usano questi mapping per NLU enterprise
_SEMANTIC_ANCHORS: List[Tuple[str, TimeConstraintType, int, int]] = [
    # pattern, tipo, ora, minuti anchor
    (r'\bdopo\s+il\s+lavoro\b',               TimeConstraintType.AFTER,  18, 0),
    (r'\bdopo\s+(?:il\s+)?pranzo\b',           TimeConstraintType.AFTER,  13, 30),
    (r'\ba\s+fine\s+(?:giornata|giorno)\b',    TimeConstraintType.AFTER,  17, 0),
    (r'\bprima\s+di\s+pranzo\b',               TimeConstraintType.BEFORE, 13, 0),
    (r'\bdopo\s+la\s+scuola\b',                TimeConstraintType.AFTER,  16, 0),
    (r'\bbefore\s+work\b|prima\s+del\s+lavoro\b', TimeConstraintType.BEFORE, 9, 0),
]


def _normalize_italian_numbers(text: str) -> str:
    """Replace Italian number words with digits for time extraction.
    Sorted longest-first to avoid partial matches (e.g. 'ventitre' before 'tre')."""
    result = text
    for word, digit in _ITALIAN_NUMBERS.items():
        result = re.sub(r'\b' + re.escape(word) + r'\b', digit, result)
    return result


def _disambiguate_hour_pm(hour: int, text: str) -> int:
    """Italian business hours convention: bare hours 1-8 are PM unless morning context.
    Business hours are 9:00-20:00. "alle tre" → 15:00, "alle sette" → 19:00.
    """
    morning_indicators = [
        "mattina", "di mattina", "stamattina", "mane",
        "am", "a.m.", "prima di mezzogiorno", "del mattino"
    ]
    if 1 <= hour <= 8:
        text_lower = text.lower()
        if not any(ind in text_lower for ind in morning_indicators):
            return hour + 12
    return hour


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

    # =========================================================================
    # PHASE 0.5: Semantic anchors (must check BEFORE other patterns)
    # "dopo il lavoro" → AFTER(18:00), "dopo pranzo" → AFTER(13:30)
    # =========================================================================
    for anchor_pattern, anchor_type, anchor_h, anchor_m in _SEMANTIC_ANCHORS:
        am = re.search(anchor_pattern, text_n)
        if am:
            anchor = time(anchor_h, anchor_m)
            tc = TimeConstraint(
                constraint_type=anchor_type,
                anchor_time=anchor,
                original_text=am.group(0),
                confidence=0.9,
            )
            return ExtractedTime(
                time=anchor,
                original_text=tc.original_text,
                confidence=0.9,
                is_approximate=True,
                time_constraint=tc,
            )

    # Common prefix: "alle", "ore", "le", "per le", "entro le"
    _P = r'(?:alle|ore|le|per\s+le|entro\s+le)\s+'

    # =========================================================================
    # PHASE 0.75: "dopo le X:YY" / "dopo le X e Y" — must come BEFORE PHASE 1
    # otherwise "le X:YY" / "le X e Y" are captured as exact times without constraint
    # =========================================================================
    m = re.search(r'dopo\s+le\s+(\d{1,2}):(\d{2})\b', text_n)
    if m:
        h, mins = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mins <= 59:
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.AFTER,
                anchor_time=time(h, mins),
                original_text=m.group(0),
                confidence=0.9,
            )
            return ExtractedTime(
                time=time(h, mins), original_text=m.group(0),
                confidence=0.9, is_approximate=True, time_constraint=tc,
            )

    m = re.search(r'dopo\s+le\s+(\d{1,2})\s+e\s+(\d{1,2})\b', text_n)
    if m:
        h, mins = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mins <= 59:
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.AFTER,
                anchor_time=time(h, mins),
                original_text=m.group(0),
                confidence=0.9,
            )
            return ExtractedTime(
                time=time(h, mins), original_text=m.group(0),
                confidence=0.9, is_approximate=True, time_constraint=tc,
            )

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
    # PHASE 3: Time range "tra le X e le Y" → midpoint + TimeConstraint
    # Must check BEFORE hour-only to avoid "le 14" matching from "tra le 14 e le 16"
    # =========================================================================
    m = re.search(r'tra\s+le\s+(\d{1,2})\s+e\s+le\s+(\d{1,2})', text_n)
    if m:
        start_h = int(m.group(1))
        end_h = int(m.group(2))
        # FIX-9: apply PM disambiguation so "tra le 3 e le 4" → 15:00-16:00
        start_h = _disambiguate_hour_pm(start_h, text_n)
        end_h = _disambiguate_hour_pm(end_h, text_n)
        if 0 <= start_h <= 23 and 0 <= end_h <= 23:
            mid_h = (start_h + end_h) // 2
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.RANGE,
                range_start=time(start_h, 0),
                range_end=time(end_h, 0),
                original_text=m.group(0),
                confidence=0.7,
            )
            return ExtractedTime(
                time=time(mid_h, 0),
                original_text=m.group(0),
                confidence=0.7,
                is_approximate=True,
                time_constraint=tc,
            )

    # =========================================================================
    # PHASE 4: Approximate patterns — con TimeConstraint (TIMEX3 compliant)
    # Must check BEFORE hour-only to avoid "le 17" matching from "dopo le 17"
    # World-class: preserva semantica "dopo/prima/verso" — identico a Dialogflow CX
    # =========================================================================

    # "dopo le X" — pattern principale AFTER (era la root cause del bug)
    # Nota: "dopo le X:YY" e "dopo le X e Y" gestiti in PHASE 0.75 prima di PHASE 1
    m = re.search(r'dopo\s+le\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.AFTER,
                anchor_time=time(h, 0),
                original_text=m.group(0),
                confidence=0.9,
            )
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.9, is_approximate=True, time_constraint=tc,
            )

    # "dalle X in poi"
    m = re.search(r'dalle\s+(\d{1,2})\s+in\s+poi\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.AFTER,
                anchor_time=time(h, 0),
                original_text=m.group(0),
                confidence=0.9,
            )
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.9, is_approximate=True, time_constraint=tc,
            )

    # "prima delle X" / "prima della X" / "prima di X"
    m = re.search(r'prima\s+(?:delle?|della)\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.BEFORE,
                anchor_time=time(h, 0),
                original_text=m.group(0),
                confidence=0.9,
            )
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.9, is_approximate=True, time_constraint=tc,
            )

    # "verso le X", "intorno alle X", "circa alle X", "sulle X"
    m = re.search(r'(?:verso\s+le|intorno\s+alle?|circa\s+alle?|sulle)\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            tc = TimeConstraint(
                constraint_type=TimeConstraintType.AROUND,
                anchor_time=time(h, 0),
                original_text=m.group(0),
                confidence=0.8,
            )
            return ExtractedTime(
                time=time(h, 0), original_text=m.group(0),
                confidence=0.8, is_approximate=True, time_constraint=tc,
            )

    # =========================================================================
    # PHASE 5: Hour-only exact (LAST of prefix patterns)
    # "alle 17", "le 5", "ore 10"
    # =========================================================================
    m = re.search(r'(?:alle|ore|le)\s+(\d{1,2})\b', text_n)
    if m:
        h = int(m.group(1))
        h = _disambiguate_hour_pm(h, text)  # Bug 3 fix: PM convention
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


def extract_time_constraint(text: str) -> Optional[TimeConstraint]:
    """
    Entry point TIMEX3 — estrae solo il constraint temporale.
    World-class: usare invece di extract_time() quando serve il constraint type.
    """
    result = extract_time(text)
    if result and result.time_constraint:
        return result.time_constraint
    # Se extract_time non ha trovato constraint, controlla FIRST_AVAILABLE
    text_lower = text.lower()
    if re.search(r'\bprima\s+possibile\b|\bsubito\b|\bquando\s+siete\s+liberi\b', text_lower):
        return TimeConstraint(
            constraint_type=TimeConstraintType.FIRST_AVAILABLE,
            original_text=text_lower[:50],
            confidence=0.85,
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
        # Adjectives/compliments STT may capitalize before a real name
        # e.g. "sono bravo Leo" → "Bravo Leo" → "Bravo" estratto come cognome
        "bravo", "brava", "buono", "buona", "certo", "certa",
        "gentile", "grande", "piccolo", "piccola", "vecchio", "vecchia",
        "nuovo", "nuova", "nuovo",
        "signore", "signora", "dottore", "dottoressa", "professore", "professessa",
        "ingegnere", "avvocato",
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
        # Service verbs/nouns across ALL 6 verticals — STT confuses with names
        # Hair (salone)
        "tagliare", "colorare", "tingere", "lavare", "asciugare",
        "acconciare", "decolorare", "schiarire", "lisciare", "arricciare",
        "capelli", "capello", "frangia", "ciocche", "meches", "balayage",
        "shatush", "permanente", "stiratura", "cheratina", "tinta",
        # Beauty (estetica)
        "depilare", "truccare", "cerare", "epilare", "manicure", "pedicure",
        "unghie", "sopracciglia", "ciglia", "viso", "corpo",
        "peeling", "pulizia", "scrub", "filler", "botox",
        # Wellness (palestra/spa)
        "massaggiare", "allenare", "nuotare", "rilassare", "drenare",
        "massaggio", "linfodrenaggio", "pressoterapia", "sauna", "bagno",
        "palestra", "piscina", "yoga", "pilates", "spinning",
        # Medical (medico/clinica)
        "visitare", "esaminare", "diagnosticare", "curare", "operare",
        "visita", "ecografia", "radiografia", "analisi", "esame",
        "terapia", "riabilitazione", "fisioterapia", "ortopedia",
        "odontoiatria", "igiene", "dentale", "pulizia",
        # Auto (officina)
        "riparare", "verniciare", "lucidare", "revisionare", "cambiare",
        "tagliando", "revisione", "gomme", "pneumatici", "freni",
        "carrozzeria", "meccanica", "cambio", "olio", "filtro",
        # Professional (studio)
        "consulenza", "pratica", "perizia", "rogito", "atto",
        "calla", "grazie", "prego", "scusi", "buongiorno", "arrivederci",
        # FAQ/info words STT capitalizes — S126: "orari" was extracted as name
        "orari", "orario", "prezzi", "prezzo", "tariffe", "tariffa",
        "informazioni", "informazione", "info",
        "costi", "costo", "listino",
        "disponibilita", "disponibilità",
        "apertura", "chiusura",
        "parcheggio", "indirizzo", "posizione", "mappa",
        "pagamento", "pagamenti", "contanti", "carta", "bancomat",
        "promozione", "promozioni", "offerta", "offerte", "sconto", "sconti",
        "recensione", "recensioni", "opinioni",
        "attesa", "durata", "tempo",
        "prodotti", "prodotto", "marca", "marche",
        "garanzia", "preventivo", "preventivi",
        # Pronouns, articles, prepositions and function words STT may capitalize
        "vi", "ho", "mi", "si", "se", "ci", "ne", "lo", "la", "le", "li",
        "il", "un", "una", "uno", "gli", "dei", "delle", "del",
        "di", "da", "dal", "dalla", "dallo", "dall",
        "nel", "nella", "nello", "nell", "sul", "sulla", "sullo",
        "al", "alla", "allo", "per", "con", "tra", "fra",
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
        # S140: "Marco di nome Galli di cognome" / "di nome Marco, di cognome Galli"
        # Handles both orderings: nome+cognome or cognome+nome
        (r'(?:di\s+nome\s+)(\w+)(?:\s*,?\s*di\s+cognome\s+)(\w+)', 0.98),
        (r'(\w+)\s+di\s+nome\s+(\w+)\s+di\s+cognome', 0.98),
        # S140: "nome Marco cognome Galli" (without "di")
        (r'\bnome\s+(\w+)\s+cognome\s+(\w+)', 0.97),
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
        # "sono Mario", "sono la Maria", "sono bravo Mario Rossi" - most general, last
        # NOTE: article must be followed by SPACE to avoid "Laura" → "la" + "Ura" bug
        # Captures up to 3 words so leading adjectives can be stripped by blacklist
        (r'(?:sono|io\s+sono)\s+(?:(?:il|la|lo)\s+)?([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+){0,2})', 0.95),
    ]

    for pattern, confidence in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # S140: patterns with 2 groups (nome + cognome) → combine
            if match.lastindex and match.lastindex >= 2:
                nome = match.group(1).strip()
                cognome = match.group(2).strip()
                name = f"{nome} {cognome}"
            else:
                name = match.group(1).strip()

            # Strip blacklisted words:
            # - LEADING blacklisted → skip (e.g., "bravo Leo" → keep "Leo")
            # - TRAILING blacklisted → stop (e.g., "Antonio Vorrei" → keep "Antonio")
            name_words = name.split()
            cleaned_words = []
            leading = True  # still consuming leading qualifiers
            for word in name_words:
                if word.lower() in NAME_BLACKLIST:
                    if leading:
                        continue  # skip leading adjective/title before real name
                    else:
                        break   # stop at trailing garbage
                else:
                    leading = False
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
# MULTI-OPERATOR EXTRACTION (GAP-P1-8)
# =============================================================================

# Trigger patterns: text must match at least one to attempt multi-operator extraction
_MULTI_OP_TRIGGERS = [
    r'\bsia\b.+\bche\b',
    r'\bindifferente tra\b',
    r'\boppure\b',
    r'\bo\s+(?:chiunque|qualsiasi|qualunque)\b',
    # Two capitalized names with "o", "e", or "," between them
    r'[A-ZÀ-Ù][a-zà-ù]+\s+[oe]\s+[A-ZÀ-Ù][a-zà-ù]+',
    r'[A-ZÀ-Ù][a-zà-ù]+,\s*[A-ZÀ-Ù][a-zà-ù]+',
]

# Name token pattern: capitalized Italian name (handles accented chars)
_NAME_TOKEN_PAT = r'\b([A-ZÀ-Ù][a-zà-ù]+(?:\s+[A-ZÀ-Ù][a-zà-ù]+)?)\b'


def extract_operators_multi(text: str) -> Optional[ExtractedOperatorList]:
    """
    Extract multiple operator preferences from Italian text (GAP-P1-8).

    Returns None if text doesn't contain a multi-operator pattern.
    Caller should fall back to extract_operator() if this returns None.

    Handles:
    - "voglio Mario o Giulia"
    - "sia Marco che Laura"
    - "con Marco oppure con Luca"
    - "indifferente tra Marco e Laura"
    - "Marco, Giulia o chiunque"
    """
    # Step 1: Trigger check — avoid false positives on single-operator text
    trigger_matched = any(
        re.search(t, text, re.IGNORECASE) for t in _MULTI_OP_TRIGGERS
    )
    if not trigger_matched:
        return None

    # Step 2: Extract all capitalized name tokens, filter blacklist
    raw_names = re.findall(_NAME_TOKEN_PAT, text)
    # Import blacklist from extract_operator scope — redefine subset for clarity
    _BLACKLIST = {
        "prenotare", "prenotazione", "prenoto", "prendere", "parlare",
        "sapere", "avere", "essere", "fare", "andare", "vedere",
        "vorrei", "voglio", "volevo", "preferirei", "preferisco",
        "taglio", "piega", "colore", "barba", "trattamento", "manicure",
        "appuntamento", "informazioni", "info", "orario", "prezzo",
        "un", "una", "uno", "il", "la", "lo", "le", "gli",
        "per", "con", "da", "di", "in", "su", "tra", "fra",
        "dopo", "prima", "tardi", "domani", "oggi", "mattina", "sera",
    }
    names = [
        n.strip().title()
        for n in raw_names
        if n.strip().lower() not in _BLACKLIST and len(n.strip()) >= 2
    ]

    # Step 3: Detect "any available" fallback
    is_any = bool(re.search(r'\b(chiunque|qualsiasi|qualunque)\b', text, re.IGNORECASE))

    # Need 2+ names OR 1 name + is_any (e.g. "Marco o chiunque")
    if len(names) < 2 and not (len(names) == 1 and is_any):
        return None  # Not actually multi — caller uses extract_operator()

    # Deduplicate while preserving order
    seen: set = set()
    unique_names: List[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique_names.append(n)

    return ExtractedOperatorList(
        names=unique_names,
        is_any=is_any,
        original_text=text,
        confidence=0.85,
    )


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


# BUG-3 FIX: Skip service extraction when words appear in referential context
# "trattamenti che ti ho chiesto" / "quelli di prima" = referring to previously mentioned services
_REFERENTIAL_PATTERNS_COMPILED = [
    re.compile(r"(?:che\s+(?:ti|le|vi)\s+ho\s+(?:chiesto|detto|indicato|menzionato))", re.IGNORECASE),
    re.compile(r"(?:quell[oiae]\s+(?:di|che)\s+(?:prima|detto|chiesto))", re.IGNORECASE),
    re.compile(r"(?:(?:gli|i|le)\s+stess[ieoa]\s+(?:servizi[oa]?|trattament[oi]))", re.IGNORECASE),
    re.compile(r"(?:(?:come\s+)?(?:ho\s+)?(?:già\s+)?detto\s+prima)", re.IGNORECASE),
]


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
    for rp in _REFERENTIAL_PATTERNS_COMPILED:
        if rp.search(text_lower):
            return []  # Referential context — don't extract new services

    words = text_lower.split()
    found_services = []
    found_ids = set()  # Avoid duplicates

    # Phase 1: Exact substring matching — track matched synonym length for specificity
    _matches_with_specificity = []  # (service_id, confidence, matched_synonym_len)
    for service_id, synonyms in services_config.items():
        best_match_len = 0
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            if synonym_lower in text_lower:
                if len(synonym_lower) > best_match_len:
                    best_match_len = len(synonym_lower)
        if best_match_len > 0:
            confidence = 1.0 if best_match_len == len(text_lower.strip()) else 0.95
            _matches_with_specificity.append((service_id, confidence, best_match_len))

    # S122: Specificity + ambiguity filter
    if len(_matches_with_specificity) > 1:
        max_len = max(m[2] for m in _matches_with_specificity)
        # Keep only matches within 70% of the longest match's specificity
        _matches_with_specificity = [
            m for m in _matches_with_specificity
            if m[2] >= max_len * 0.7
        ]

        # S122: When multiple services match at same specificity and one service
        # name contains another (e.g., "Colore" vs "Colore barba" both matching on
        # "colore"), prefer the one whose full name is closest to the matched text
        if len(_matches_with_specificity) > 1:
            # Build user words excluding common filler
            _filler = {"vorrei", "un", "una", "il", "la", "per", "fare", "bene", "voglio"}
            _user_words = set(w for w in text_lower.split() if w not in _filler)
            # Check if any service has ALL its name words in user input
            _exact_name_matches = []
            for m in _matches_with_specificity:
                svc_id = m[0]
                svc_synonyms = services_config.get(svc_id, [])
                if svc_synonyms:
                    # Use "/" split for names like "meches/balayage"
                    svc_name_words = set(re.split(r'[\s/]+', svc_synonyms[0]))
                    if svc_name_words.issubset(_user_words):
                        _exact_name_matches.append(m)
            if _exact_name_matches:
                _matches_with_specificity = _exact_name_matches
            else:
                # No exact name match — prefer shorter service names (less specific)
                # E.g., "Barba" (1 word) over "Colore barba" (2 words)
                min_words = min(len(re.split(r'[\s/]+', services_config.get(m[0], [""])[0])) for m in _matches_with_specificity)
                _matches_with_specificity = [
                    m for m in _matches_with_specificity
                    if len(re.split(r'[\s/]+', services_config.get(m[0], [""])[0])) == min_words
                ]

    # S125: Detect bare-word ambiguity — all matches share same matched substring
    # e.g. "taglio" matches "Taglio Donna", "Taglio Uomo", "Taglio Bambino"
    # In this case, Sara should ask "quale tipo?" instead of booking all 3
    if len(_matches_with_specificity) > 1:
        # Check if all matches share the same matched substring length
        # AND the user input is essentially just that bare word
        _content_words = [w for w in words if w not in {"vorrei", "un", "una", "il", "la", "per", "fare", "bene", "voglio", "di", "mi", "del", "dei"}]
        if len(_content_words) <= 1:
            # User gave a single content word — all matches are ambiguous variants
            # Return with special negative confidence to signal disambiguation needed
            for service_id, confidence, matched_len in _matches_with_specificity:
                found_services.append((service_id, -1.0))
                found_ids.add(service_id)
            return found_services

    # S135: Detect family ambiguity in multi-word input
    # e.g. "taglio barba colore" → taglio matches taglio, taglio_uomo, taglio_bambino, taglio_+_barba
    # Group services by shared prefix (base word), mark families with 3+ members as ambiguous
    if len(_matches_with_specificity) > 3:
        _family_groups: Dict[str, list] = {}
        for m in _matches_with_specificity:
            svc_id = m[0]
            # Extract base word: "taglio_uomo" → "taglio", "taglio_+_barba" → "taglio"
            base = svc_id.split("_")[0]
            _family_groups.setdefault(base, []).append(m)

        # If any family has 3+ members, split into ambiguous vs clear
        _ambiguous_families = {base: members for base, members in _family_groups.items() if len(members) >= 3}
        if _ambiguous_families:
            _clear_matches = []
            _ambig_matches = []
            for m in _matches_with_specificity:
                base = m[0].split("_")[0]
                if base in _ambiguous_families:
                    _ambig_matches.append(m)
                else:
                    _clear_matches.append(m)
            # Return clear services with normal confidence, ambiguous with -1.0
            for service_id, confidence, matched_len in _clear_matches:
                if service_id not in found_ids:
                    found_services.append((service_id, confidence))
                    found_ids.add(service_id)
            for service_id, confidence, matched_len in _ambig_matches:
                if service_id not in found_ids:
                    found_services.append((service_id, -1.0))
                    found_ids.add(service_id)
            return found_services

    # S124: Collect words consumed by Phase 1 multi-word matches
    _consumed_words: set = set()
    for service_id, confidence, matched_len in _matches_with_specificity:
        if service_id not in found_ids:
            found_services.append((service_id, confidence))
            found_ids.add(service_id)
            # Mark individual words of matched multi-word synonyms as consumed
            if matched_len > 0:
                for synonym in services_config.get(service_id, []):
                    if len(synonym) == matched_len and synonym.lower() in text_lower:
                        for w in synonym.lower().split():
                            _consumed_words.add(w)
                        break

    # Phase 2: Fuzzy matching for remaining words (skip consumed words)
    for service_id, synonyms in services_config.items():
        if service_id in found_ids:
            continue
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            for word in words:
                if len(word) < 3 or word in _consumed_words:
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

def _normalize_phone_whisper(text: str) -> Optional[str]:
    """
    Normalize phone number from Whisper digit-by-digit transcriptions.

    Whisper often transcribes phone digits as:
    - Comma-separated: "3,5,0,5,4,8,1,1,1,1"
    - Grouped double digits: "11,11,11" (undici undici → "1"+"1" each)
    - Mixed Italian words: "tre cinque zero..."

    Italian phone numbers: 9-12 digits (mobile 10, landline 9-11, +39 prefix).
    Returns None if result is not a valid Italian phone length.
    """
    # Step 1: Replace Italian single-digit words
    SINGLE_DIGITS = {
        'zero': '0', 'uno': '1', 'una': '1', 'due': '2', 'tre': '3',
        'quattro': '4', 'cinque': '5', 'sei': '6', 'sette': '7',
        'otto': '8', 'nove': '9',
    }
    t = text.lower()
    for word, digit in SINGLE_DIGITS.items():
        t = re.sub(r'\b' + word + r'\b', digit, t)

    # Step 2: Split on any non-digit separator (comma, space, dot, dash)
    tokens = re.split(r'[,\s.\-/]+', t)

    # Step 3: Collect clean tokens (digit-only strings)
    clean_tokens = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        token_digits = re.sub(r'[^\d]', '', token)
        if token_digits:
            clean_tokens.append(token_digits)

    if not clean_tokens:
        return None

    def _strip_prefix(s: str) -> str:
        """Remove +39 country code prefix if present."""
        if s.startswith('39') and len(s) > 11:
            return s[2:]
        return s

    # Strategy A: split every 2-digit token into individual digits
    # "11" → "1"+"1" (Whisper heard "uno uno" as "undici")
    digits_split = []
    for t in clean_tokens:
        if len(t) == 1:
            digits_split.append(t)
        elif len(t) == 2:
            digits_split.extend(list(t))   # "11" → ["1","1"]
        else:
            digits_split.extend(list(t))   # longer block: split all
    result_a = _strip_prefix(''.join(digits_split))
    if 9 <= len(result_a) <= 12:
        return result_a

    # Strategy B: take only first digit of each token
    # When user said 4 × "uno" but Whisper wrote 4 × "11" (double-encoding)
    result_b = _strip_prefix(''.join(t[0] for t in clean_tokens if t))
    if 9 <= len(result_b) <= 12:
        return result_b

    return None


def extract_phone(text: str) -> Optional[str]:
    """
    Extract Italian phone number from text.

    Handles:
    - +39 333 1234567
    - 333.123.4567
    - 333 123 4567
    - 3331234567
    - Whisper digit-by-digit: "3,5,0,5,4,8,1,1,1,1"
    - Whisper grouped doubles: "3,5,0,5,4,8,11,11,11,11" → "3505481111"

    Validation (GAP-P0-1):
    - Min 9 digits, max 13 (with +39 prefix)
    - Landline (starts with 0) returns None — voice agent only needs mobile
    - Overflow numbers (>13 digits after strip) return None
    """

    def _is_valid_mobile(digits: str) -> bool:
        """Validate digit string is a plausible Italian mobile number."""
        # Strip leading +39 / 0039 / 39 for length check
        bare = digits.lstrip('+')
        if bare.startswith('0039'):
            bare = bare[4:]
        elif bare.startswith('39') and len(bare) >= 12:  # fix: was > 11
            candidate = bare[2:]
            if re.match(r'^3[1-8]', candidate):  # AGCOM: only valid mobile ranges
                bare = candidate
        # Landline: starts with 0 → not accepted for voice agent bookings
        if bare.startswith('0'):
            return False
        # Length gate: 9–10 bare digits (Italian mobile standard)
        return 9 <= len(bare) <= 10

    def _normalize_output(digits: str) -> str:
        """
        Normalize extracted phone to consistent output format.
        - +39XXXXXXXXXX → +39XXXXXXXXXX (kept for backward compat)
        - 0039XXXXXXXXXX → XXXXXXXXXX (bare 10-digit)
        - 39XXXXXXXXXX (12 digits, AGCOM range) → XXXXXXXXXX (bare 10-digit)
        """
        if digits.startswith('+'):
            return digits  # E.164 with +: keep as-is
        if digits.startswith('0039'):
            return digits[4:]
        if not digits.startswith('0') and digits.startswith('39') and len(digits) == 12:
            candidate = digits[2:]
            if re.match(r'^3[1-8]', candidate):
                return candidate
        return digits

    # First: try standard patterns (most reliable)
    # Anchored with word boundaries / negative lookahead to avoid partial matches
    # inside longer digit strings (e.g. "33312345678901" must not match first 10 chars)
    # GAP-P1-1: extended prefix group (?:(?:\+|00)?39) to capture 0039 and bare 39
    patterns = [
        r'(?<!\d)(?:(?:\+|00)?39[-.\s]?)?3[1-8]\d[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)',  # Mobile: 333 123 4567
        r'(?<!\d)(?:(?:\+|00)?39[-.\s]?)?0\d{1,3}[-.\s]?\d{6,8}(?!\d)',             # Landline: 02 12345678
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            normalized = re.sub(r'[^\d+]', '', match.group(0))
            if _is_valid_mobile(normalized):
                return _normalize_output(normalized)

    # Fallback: Whisper digit-by-digit normalization
    # Triggered when text contains commas, isolated digits, OR Italian number words
    _ITALIAN_DIGIT_WORDS = {'zero', 'uno', 'una', 'due', 'tre', 'quattro', 'cinque', 'sei', 'sette', 'otto', 'nove'}
    _text_words = set(re.sub(r'[,.]', ' ', text.lower()).split())
    _has_digit_words = len(_text_words & _ITALIAN_DIGIT_WORDS) >= 3  # at least 3 digit words
    if re.search(r'\d[\s,]+\d', text) or _has_digit_words:
        result = _normalize_phone_whisper(text)
        if result and _is_valid_mobile(result):
            return result

    return None


def _normalize_stt_email(text: str) -> str:
    """
    Normalize STT artifacts to email-friendly symbols.
    Whisper may transcribe @ as 'chiocciola'/'at' and . as 'punto'.
    """
    t = text.lower()
    t = re.sub(r'\bchiocciola\b', '@', t)
    t = re.sub(r'\bcommerciale\s+a\b', '@', t)
    # "at" standalone (not part of a word) → @
    t = re.sub(r'(?<![a-z0-9])at(?![a-z0-9])', '@', t)
    # Collapse spaces around @ (e.g. "mario @ gmail" → "mario@gmail")
    t = re.sub(r'\s*@\s*', '@', t)
    # "punto" between alphanumerics (email context) → .
    t = re.sub(r'(?<=[a-z0-9])\s+punto\s+(?=[a-z])', '.', t)
    return t


def _validate_email_candidate(candidate: str) -> Optional[str]:
    """Validate and normalize an email candidate string. Returns lowercase or None."""
    c = candidate.lower()
    if '@' not in c:
        return None
    at_idx = c.index('@')
    local = c[:at_idx]
    domain = c[at_idx + 1:]
    if '..' in local or '..' in domain:
        return None
    if '.' not in domain:
        return None
    tld = domain.rsplit('.', 1)[-1]
    if len(tld) < 2:
        return None
    return c


# Email keywords (anchor priority, high → low) — GAP-P1-2
_EMAIL_ANCHOR_PATTERNS = [
    r'(?:la\s+mia\s+)?(?:e[_-]?mail|mail)\s+(?:è|e|personale\s+è|personale\s+e)',
    r'indirizzo\s+(?:e[_-]?mail|mail)\s*(?:è|e|:)',
    r'(?:e[_-]?mail|mail)\s*(?:è|e|:)',
    r'mia\s+(?:e[_-]?mail|mail)',
]
_EMAIL_PATTERN = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.

    Validation rules:
    - No consecutive dots in local part or domain: test..test@gmail.com → None
    - TLD must be at least 2 chars: test@x.c → None
    - Domain must contain at least one dot: test@gmail → None
    - Always normalised to lowercase: MARIO@GMAIL.COM → mario@gmail.com

    GAP-P1-2 additions:
    - STT artifact normalization: 'chiocciola'→'@', 'at'→'@', 'punto'→'.'
    - Keyword-anchored priority: email after 'la mia email è' takes precedence
    """
    # 1. Normalize STT artifacts
    normalized_text = _normalize_stt_email(text)

    # 2. Keyword-anchored priority search (GAP-P1-2)
    text_lower = normalized_text.lower()
    for anchor_pat in _EMAIL_ANCHOR_PATTERNS:
        anchor_match = re.search(anchor_pat, text_lower)
        if anchor_match:
            post_anchor = normalized_text[anchor_match.end():]
            email_match = re.search(_EMAIL_PATTERN, post_anchor, re.IGNORECASE)
            if email_match:
                validated = _validate_email_candidate(email_match.group(0))
                if validated:
                    return validated

    # 3. Fallback: first email in text (existing behavior)
    match = re.search(_EMAIL_PATTERN, normalized_text, re.IGNORECASE)
    if not match:
        return None
    return _validate_email_candidate(match.group(0))


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
    ambiguous_services: Optional[List[str]] = None  # S125: bare-word ambiguity
    operator: Optional[ExtractedOperator] = None   # Single operator (backward compat)
    operators: List[ExtractedOperator] = field(default_factory=list)  # Multi-op list (GAP-P1-8)
    phone: Optional[str] = None
    email: Optional[str] = None
    is_solito: bool = False  # P0-4: "il solito", "come l'ultima volta", "come sempre"

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


# P0-4: Patterns for "il solito" / "come l'ultima volta"
_SOLITO_PATTERNS = re.compile(
    r"\b(?:il\s+solito|come\s+(?:l['\u2019]ultima\s+volta|sempre|al\s+solito)|"
    r"quello\s+di\s+sempre|la\s+stessa\s+cosa|come\s+l['\u2019]altra\s+volta|"
    r"uguale\s+(?:a\s+)?(?:l['\u2019]ultima\s+volta|all['\u2019]ultima\s+volta|sempre)|stessa\s+cosa)\b",
    re.IGNORECASE
)


def detect_solito(text: str) -> bool:
    """P0-4: Detect 'il solito' pattern in user input."""
    return bool(_SOLITO_PATTERNS.search(text))


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

    # GAP-P1-8: try multi-operator first; fall back to single
    multi = extract_operators_multi(text)
    if multi and len(multi.names) >= 2:
        result.operators = [
            ExtractedOperator(n, multi.original_text, multi.confidence)
            for n in multi.names
        ]
        result.operator = result.operators[0]  # backward compat: primary = first
    else:
        single = extract_operator(text)
        if single:
            result.operator = single
            result.operators = [single]

    result.phone = extract_phone(text)
    result.email = extract_email(text)

    # CoVe 2026: Use default config if none provided (for test compatibility)
    config = services_config if services_config else DEFAULT_SERVICES_CONFIG
    
    # Extract multiple services
    services_results = extract_services(text, config)
    if services_results:
        # S125: Check for bare-word ambiguity (all confidence == -1.0)
        if all(conf < 0 for _, conf in services_results) and len(services_results) > 1:
            result.ambiguous_services = [s[0] for s in services_results]
            # Don't set result.services — ambiguity must be resolved first
        else:
            result.services = [s[0] for s in services_results]
            result.service = services_results[0][0]  # First service for backwards compat

    # P0-4: Detect "il solito" pattern
    result.is_solito = detect_solito(text)

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


# =============================================================================
# VERTICAL-SPECIFIC ENTITY EXTRACTION (F02)
# =============================================================================
# Medical: specialty, urgency, visit_type
# Auto: vehicle_plate (targa italiana), vehicle_brand
# Python 3.9 compatible — regex only, no external libraries.

# --- Medical entities ---

_MEDICAL_SPECIALTIES: Dict[str, List[str]] = {
    "cardiologia": ["cardiologo", "cardiologa", "cardiologia", "cardiologica", "cardiologico", "cuore", "elettrocardiogramma", "ecg"],
    "dermatologia": ["dermatologo", "dermatologa", "dermatologia", "pelle", "nei", "mappatura nei"],
    "ortopedia": ["ortopedico", "ortopedica", "ortopedia", "ossa", "frattura", "articolazione"],
    "ginecologia": ["ginecologo", "ginecologa", "ginecologia", "ginecologica", "ginecologico", "pap test", "ecografia ginecologica"],
    "pediatria": ["pediatra", "pediatria", "bambino", "bimbo", "neonato"],
    "oculistica": ["oculista", "oculistica", "vista", "occhi", "miopia", "astigmatismo"],
    "odontoiatria": ["dentista", "odontoiatra", "denti", "carie", "otturazione", "estrazione",
                     "devitalizzazione", "sbiancamento denti", "invisalign", "aligner dentale",
                     "ortodonzia", "ortodontista", "impianto dentale", "pulizia denti"],
    "neurologia": ["neurologo", "neurologia", "emicrania", "cefalea", "nervo"],
    "endocrinologia": ["endocrinologo", "endocrinologia", "tiroide", "diabete", "ormoni"],
    "reumatologia": ["reumatologo", "reumatologia", "artrite", "artrosi", "fibromialgia"],
    "fisioterapia": ["fisioterapia", "fisioterapista", "fisio", "riabilitazione", "rieducazione",
                     "tecarterapia", "ultrasuoni terapia", "kinesiotaping", "onde d'urto", "dry needling"],
    "osteopata": ["osteopata", "osteopatia", "trattamento osteopatico", "cranio-sacrale",
                  "osteopatia viscerale", "manipolazione osteopatica"],
    "psicologo": ["psicologo", "psicoterapeuta", "psicoterapia", "TCC", "EMDR",
                  "terapia cognitivo-comportamentale", "supporto psicologico",
                  "seduta di coppia", "terapia di coppia"],
    "nutrizionista": ["nutrizionista", "dietologo", "dieta personalizzata", "piano alimentare",
                      "BIA", "bioimpedenziometrica", "alimentazione sportiva"],
    "podologo": ["podologo", "podologia", "plantari", "unghia incarnita", "calli",
                 "verruca plantare", "analisi del passo"],
}

# =============================================================================
# HAIR SUB-VERTICAL KEYWORDS
# =============================================================================
_HAIR_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "barbiere": ["barba sfumata", "contorno barba", "fade", "skin fade", "zero ai lati",
                 "sfumatura progressiva", "degradè uomo", "undercut", "rasatura laterale",
                 "lineetta barba", "barba scultura", "beard shaping"],
    "color_specialist": ["correzione colore", "decolorazione", "toning capelli", "glossing",
                         "Olaplex", "trattamento Olaplex", "schiaritura capelli", "riflessante",
                         "balayage", "shatush", "ombré", "degradé colore"],
    "tricologo": ["caduta capelli", "diradamento capelli", "alopecia", "PRP tricologico",
                  "PRP capelli", "plasma ricco di piastrine", "peeling cuoio capelluto",
                  "analisi tricologica", "mesoterapia capelli", "trattamento anti-caduta"],
    "extension_specialist": ["extension cheratina", "extension clip", "extension tape",
                              "I-tip", "V-tip", "allungamento volume", "allungamento cheratina",
                              "extension capelli"],
}

# =============================================================================
# BEAUTY SERVICE KEYWORDS
# =============================================================================
_BEAUTY_SERVICE_KEYWORDS: Dict[str, List[str]] = {
    "estetista_viso": ["pulizia viso", "pulizia profonda", "peeling viso", "radiofrequenza viso",
                       "LED viso", "dermaplaning", "microneedling", "filler viso",
                       "biorivitalizzazione", "trattamento acne", "maschera viso"],
    "estetista_corpo": ["massaggio drenante", "massaggio anticellulite", "linfodrenaggio",
                        "pressoterapia", "bendaggio drenante", "cavitazione",
                        "radiofrequenza corpo", "endo-sfera", "massaggio rilassante corpo"],
    "nail_specialist": ["ricostruzione gel", "gel unghie", "semipermanente unghie", "nail art",
                        "fill-in gel", "rimozione gel", "forma mandorla", "forma coffin",
                        "french manicure", "ricostruzione unghie", "allungamento gel"],
    "epilazione_laser": ["epilazione laser", "laser diodo", "luce pulsata", "IPL",
                         "epilazione definitiva", "depilazione laser", "patch test laser"],
    "spa": ["circuito spa", "day spa", "hammam", "percorso benessere", "spa di coppia",
            "hot stone massage", "massaggio ayurvedico", "bagno turco"],
}

# =============================================================================
# WELLNESS SUB-VERTICAL KEYWORDS
# =============================================================================
_WELLNESS_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "personal_trainer": ["personal trainer", "PT", "personal training", "allenamento personalizzato",
                          "programma personalizzato", "scheda allenamento", "plicometria",
                          "test VO2 max", "valutazione composizione corporea", "allenamento domicilio"],
    "yoga_pilates": ["yoga", "pilates", "yin yoga", "yoga nidra", "hot yoga", "pranayama",
                      "meditazione guidata", "pilates posturale", "pilates reformer", "restorative yoga"],
    "crossfit": ["crossfit", "WOD", "AMRAP", "EMOM", "metcon", "functional training",
                  "fondamentali crossfit", "open gym", "cross training"],
    "piscina": ["piscina", "nuoto", "corsia riservata", "vasca da 25m", "vasca da 50m",
                 "baby nuoto", "acquacorrida", "master nuoto", "nuoto libero", "acquagym"],
    "arti_marziali": ["judo", "karate", "jiu-jitsu", "BJJ", "muay thai", "kickboxing",
                       "MMA", "krav maga", "kata", "kumite", "randori", "arti marziali"],
}

# =============================================================================
# AUTO SUB-VERTICAL KEYWORDS
# =============================================================================
_AUTO_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "carrozzeria": ["perizia danni", "stima danni", "sostituzione parabrezza", "parabrezza",
                     "lucidatura carrozzeria", "polish", "verniciatura parziale", "ritocco vernice",
                     "tintura paraurti", "auto cortesia", "carrozziere"],
    "elettrauto": ["diagnosi OBD", "centralina motore", "impianto hi-fi", "autoradio",
                    "retrocamera", "sensori parcheggio", "GPS tracker", "immobilizer",
                    "impianto GPL", "impianto metano", "elettrauto"],
    "gommista": ["equilibratura", "bilanciatura gomme", "convergenza", "assetto ruote",
                  "cambio stagionale gomme", "deposito gomme", "foratura", "runflat",
                  "TPMS", "cerchi in lega", "gommista"],
    "revisioni": ["revisione ministeriale", "collaudo", "revisione obbligatoria",
                   "bollino blu", "libretto revisione", "revisione scaduta"],
    "detailing": ["detailing", "cera auto", "ceramica auto", "PPF", "wrapping",
                   "car wrapping", "ozono abitacolo", "sanificazione ozono",
                   "nano ceramica", "protezione ceramica"],
}

# =============================================================================
# PROFESSIONALE SERVICE KEYWORDS
# =============================================================================
_PROFESSIONALE_SERVICE_KEYWORDS: Dict[str, List[str]] = {
    "commercialista": ["dichiarazione dei redditi", "730", "Unico", "modello F24",
                        "busta paga", "apertura partita IVA", "apertura P.IVA",
                        "bilancio", "contabilità", "CU certificazione unica", "liquidazione IVA"],
    "avvocato": ["consulenza legale", "separazione", "divorzio", "contratto di locazione",
                  "contratto di affitto", "recupero crediti", "successione ereditaria",
                  "testamento", "ricorso", "parere legale", "mediazione civile"],
    "consulente": ["consulenza strategica", "business plan", "analisi di mercato",
                    "consulenza HR", "formazione aziendale", "due diligence"],
    "agenzia_immobiliare": ["valutazione immobile", "stima immobile", "proposta d'acquisto",
                              "visita immobile", "appuntamento per casa", "mutuo prima casa",
                              "perizia immobiliare", "affitto commerciale"],
    "architetto": ["progetto ristrutturazione", "DIA", "SCIA", "permesso di costruire",
                    "computo metrico", "rendering 3D", "progetto interni", "sopralluogo tecnico",
                    "certificazione energetica", "pratiche comunali"],
}


_MEDICAL_URGENCY_PATTERNS = [
    (re.compile(r"\b(?:urgente|urgenza|urgentissimo|prima\s+possibile|subito|oggi\s+stesso|immediatamente)\b", re.IGNORECASE), "urgente"),
    (re.compile(r"\b(?:presto|appena\s+possibile|quanto\s+prima|questa\s+settimana)\b", re.IGNORECASE), "alta"),
    (re.compile(r"\b(?:quando\s+c[\u2019'][\xe8e]\s+posto|non\s+ho\s+fretta|con\s+calma|quando\s+volete)\b", re.IGNORECASE), "bassa"),
]

_MEDICAL_VISIT_TYPES = {
    "prima_visita": [r"prima\s+visita", r"prima\s+volta", r"nuovo\s+paziente", r"non\s+sono\s+mai\s+venuto"],
    "controllo": [r"controllo", r"follow.up", r"follow\s+up", r"visita\s+di\s+controllo", r"ricontrollo"],
    "urgenza": [r"urgenza", r"pronto\s+soccorso"],
    "certificato": [r"certificato", r"idoneit[aà]", r"certificazione"],
    "vaccino": [r"vaccino", r"vaccinazione", r"richiamo", r"dose"],
}
_MEDICAL_VISIT_COMPILED: Dict[str, re.Pattern] = {
    vtype: re.compile(r"\b(?:" + "|".join(patterns) + r")\b", re.IGNORECASE)
    for vtype, patterns in _MEDICAL_VISIT_TYPES.items()
}


# --- Auto entities ---

# Italian targa pattern: 2 letters + 3 digits + 2 letters (post-1994)
_TARGA_PATTERN = re.compile(r"\b([A-Z]{2}\s*\d{3}\s*[A-Z]{2})\b", re.IGNORECASE)

_AUTO_BRANDS: List[str] = [
    "alfa romeo", "land rover", "mercedes benz", "audi", "bmw", "chevrolet",
    "chrysler", "citroen", "citro\xebn", "dacia", "fiat", "ford", "honda",
    "hyundai", "jeep", "kia", "lancia", "lexus", "maserati", "mazda",
    "mercedes", "mini", "mitsubishi", "nissan", "opel", "peugeot", "porsche",
    "renault", "seat", "skoda", "smart", "subaru", "suzuki", "tesla",
    "toyota", "volkswagen", "vw", "volvo",
]
# Sort by length descending to match multi-word brands first (e.g. "alfa romeo" before "alfa")
_AUTO_BRANDS.sort(key=len, reverse=True)
_AUTO_BRAND_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(b) for b in _AUTO_BRANDS) + r")\b",
    re.IGNORECASE,
)


@dataclass
class VerticalEntities:
    """Vertical-specific entities extracted from user input."""
    # Medical
    specialty: Optional[str] = None       # e.g. "cardiologia"
    urgency: Optional[str] = None         # "urgente", "alta", "bassa"
    visit_type: Optional[str] = None      # "prima_visita", "controllo", etc.
    # Auto
    vehicle_plate: Optional[str] = None   # Targa italiana, e.g. "AB123CD"
    vehicle_brand: Optional[str] = None   # e.g. "fiat", "audi"
    # Sub-vertical (all verticals)
    sub_vertical: Optional[str] = None    # e.g. "barbiere", "nail_specialist", "estetista_viso"


def extract_vertical_entities(text: str, vertical: str) -> VerticalEntities:
    """
    Extract vertical-specific entities from user input.

    For 'medical': extracts specialty, urgency level, visit type.
    For 'auto': extracts vehicle plate (targa) and brand.
    For other verticals: returns empty VerticalEntities (all fields None).

    Args:
        text: User input text
        vertical: Active vertical ('salone', 'palestra', 'medical', 'auto')

    Returns:
        VerticalEntities dataclass (all fields None if nothing found)
    """
    result = VerticalEntities()
    text_lower = text.strip().lower()

    if vertical in ("medical", "medico"):
        # Specialty detection — keyword match in text
        for specialty, keywords in _MEDICAL_SPECIALTIES.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    result.specialty = specialty
                    break
            if result.specialty:
                break

        # Urgency detection — regex patterns
        for pattern, urgency_level in _MEDICAL_URGENCY_PATTERNS:
            if pattern.search(text):
                result.urgency = urgency_level
                break

        # Visit type detection — regex patterns
        for vtype, pattern in _MEDICAL_VISIT_COMPILED.items():
            if pattern.search(text):
                result.visit_type = vtype
                break

    elif vertical == "auto":
        # Vehicle plate (targa): normalize to uppercase, no spaces
        targa_match = _TARGA_PATTERN.search(text)
        if targa_match:
            result.vehicle_plate = targa_match.group(1).replace(" ", "").upper()

        # Vehicle brand: normalize to lowercase
        brand_match = _AUTO_BRAND_PATTERN.search(text)
        if brand_match:
            result.vehicle_brand = brand_match.group(1).lower()

        # Sub-vertical detection
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _AUTO_SUB_VERTICAL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    elif vertical == "professionale":
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _PROFESSIONALE_SERVICE_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    elif vertical in ("hair", "salone"):
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _HAIR_SUB_VERTICAL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    elif vertical == "beauty":
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _BEAUTY_SERVICE_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    elif vertical in ("wellness", "palestra"):
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _WELLNESS_SUB_VERTICAL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    return result


# =============================================================================
# P1-13: EXCLUDE DAYS EXTRACTION (negative day constraints)
# =============================================================================
# Extracts days the caller explicitly does NOT want.
# Examples: "non il lunedì", "tranne il sabato", "non di mercoledì"

_NEGATIVE_DAY_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?|se\s+non\s+è\s+(?:il|lo|la|un)?\s*)(?:\s+il|\s+di|\s+ogni)?\s*luned[iì]\b", re.IGNORECASE), "monday"),
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?)(?:\s+il|\s+di|\s+ogni)?\s*marted[iì]\b", re.IGNORECASE), "tuesday"),
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?)(?:\s+il|\s+di|\s+ogni)?\s*mercoled[iì]\b", re.IGNORECASE), "wednesday"),
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?)(?:\s+il|\s+di|\s+ogni)?\s*gioved[iì]\b", re.IGNORECASE), "thursday"),
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?)(?:\s+il|\s+di|\s+ogni)?\s*venerd[iì]\b", re.IGNORECASE), "friday"),
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?)(?:\s+il|\s+di|\s+ogni)?\s*sabato\b", re.IGNORECASE), "saturday"),
    (re.compile(r"\b(?:non|tranne|eccetto|escluso?)(?:\s+il|\s+di|\s+ogni)?\s*domenica\b", re.IGNORECASE), "sunday"),
]


def extract_exclude_days(text: str) -> List[str]:
    """
    Extract days the caller explicitly wants to avoid.
    Returns list of English day names (monday, tuesday, ...).
    Used by BookingStateMachine to populate context.exclude_days.
    """
    return [day for pat, day in _NEGATIVE_DAY_PATTERNS if pat.search(text)]
