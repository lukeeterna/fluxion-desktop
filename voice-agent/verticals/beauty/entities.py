"""
FLUXION Voice Agent - Beauty Center Entity Extraction
Sub-vertical of: salone (aesthetics focus)
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


@dataclass
class BookingRequest:
    """Parsed booking request for beauty center."""
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    operator: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: int = 45


class BeautyEntityExtractor:
    """Entity extraction for centro estetico / beauty center."""

    SERVICE_DURATIONS = {
        "pulizia_viso": 60,
        "ceretta": 30,
        "manicure": 45,
        "pedicure": 45,
        "massaggio": 60,
        "epilazione_laser": 30,
        "trattamento_viso": 60,
        "trattamento_corpo": 75,
        "laminazione_ciglia": 45,
        "extension_ciglia": 90,
        "trucco": 45,
        "peeling": 45,
        "radiofrequenza": 30,
        "pressoterapia": 45,
        "scrub": 30,
    }

    SERVICE_PATTERNS = {
        "pulizia_viso": r"pulizia.*viso|pulizia.*facciale|viso.*pulizia|facial",
        "ceretta": r"cerett[ae]|depilazion|strappo|ceratura",
        "manicure": r"manicure|unghie.*man|smalto.*man|nail",
        "pedicure": r"pedicure|unghie.*pied|smalto.*pied",
        "massaggio": r"massaggi[oa]|rilassante|decontratturante|linfodrenaggio|drenante",
        "epilazione_laser": r"epilazion.*laser|laser|luce pulsata|diodo",
        "trattamento_viso": r"trattamento.*viso|anti.*rughe|idratante.*viso|filler|botox|acido.*ialuronico",
        "trattamento_corpo": r"trattamento.*corpo|anticellulite|rassodante|modellante",
        "laminazione_ciglia": r"laminazione.*cigli|cigli.*laminazione|brow.*lift",
        "extension_ciglia": r"extension.*cigli|cigli.*extension|ciglia.*finte",
        "trucco": r"trucco|make.*up|cerimonia|sposa|makeup",
        "peeling": r"peeling|esfoliazione|acido.*glicolico",
        "radiofrequenza": r"radiofrequenz|rf|rassodamento",
        "pressoterapia": r"pressoterapia|gambe.*gonfie|ritenzione",
        "scrub": r"\bscrub\b|esfoliante.*corpo",
    }

    DATE_PATTERNS = {
        r"\boggi\b": 0,
        r"\bdomani\b": 1,
        r"dopo\s*domani": 2,
        r"fra\s*(\d+)\s*giorn": None,
        r"fra\s*una\s*settimana|prossima\s*settimana": 7,
    }

    TIME_PATTERNS = [
        r"(\d{1,2})[:\.](\d{2})",
        r"(\d{1,2})\s*e\s*(\d{2})",
        r"(?:alle|le|ore)\s*(\d{1,2})",
    ]

    TIME_PERIODS = {
        "mattina": ("09:00", "12:00"),
        "pomeriggio": ("14:00", "18:00"),
        "sera": ("18:00", "19:00"),
    }

    def extract_all(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        return {
            "service": self.extract_service(text_lower),
            "date": self.extract_date(text_lower),
            "time": self.extract_time(text_lower),
            "operator": self.extract_operator(text_lower),
            "customer_name": self.extract_customer_name(text),
            "notes": self.extract_notes(text_lower),
        }

    def extract_service(self, text: str) -> Optional[str]:
        for service, pattern in self.SERVICE_PATTERNS.items():
            if re.search(pattern, text):
                return service
        return None

    def extract_date(self, text: str) -> Optional[str]:
        today = datetime.now()
        for pattern, days in self.DATE_PATTERNS.items():
            match = re.search(pattern, text)
            if match:
                if days is None:
                    days = int(match.group(1))
                target = today + timedelta(days=days)
                return target.strftime("%Y-%m-%d")

        days_map = {
            "lunedi": 0, "lunedì": 0, "martedi": 1, "martedì": 1,
            "mercoledi": 2, "mercoledì": 2, "giovedi": 3, "giovedì": 3,
            "venerdi": 4, "venerdì": 4, "sabato": 5, "domenica": 6,
        }
        for day_name, day_num in days_map.items():
            if day_name in text:
                current_day = today.weekday()
                diff = (day_num - current_day) % 7
                if diff == 0:
                    diff = 7
                target = today + timedelta(days=diff)
                return target.strftime("%Y-%m-%d")
        return None

    def extract_time(self, text: str) -> Optional[str]:
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                hour = int(groups[0])
                minute = int(groups[1]) if len(groups) > 1 and groups[1] else 0
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return f"{hour:02d}:{minute:02d}"
        for period, (start, _) in self.TIME_PERIODS.items():
            if period in text:
                return start
        return None

    def extract_operator(self, text: str) -> Optional[str]:
        match = re.search(r"(?:con|da)\s+([A-Z][a-zàèéìòù]+)", text, re.IGNORECASE)
        if match:
            name = match.group(1)
            stopwords = {"il", "lo", "la", "un", "una", "per", "alle", "ore", "domani", "oggi"}
            if name.lower() not in stopwords:
                return name
        return None

    def extract_customer_name(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:mi chiamo|sono|nome)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)",
            r"(?:prenot[iao].*(?:per|a nome))\s+([A-Z][a-zàèéìòù]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def extract_notes(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:nota|allergi[ae]|sensibil|pelle)\s*:?\s*(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def calculate_duration(self, service: str) -> int:
        return self.SERVICE_DURATIONS.get(service, 45)

    def create_booking_request(self, text: str) -> BookingRequest:
        entities = self.extract_all(text)
        service = entities.get("service")
        duration = self.calculate_duration(service) if service else 45
        return BookingRequest(
            service=service,
            date=entities.get("date"),
            time=entities.get("time"),
            operator=entities.get("operator"),
            customer_name=entities.get("customer_name"),
            notes=entities.get("notes"),
            duration_minutes=duration,
        )
