"""
FLUXION Voice Agent - Barbiere Entity Extraction
Sub-vertical of: salone (men's barbershop focus)
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta


@dataclass
class BookingRequest:
    """Parsed booking request for barbiere."""
    service: Optional[str] = None
    date: Optional[str] = None  # YYYY-MM-DD
    time: Optional[str] = None  # HH:MM
    barber: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: int = 30


class BarbiereEntityExtractor:
    """Entity extraction for barbiere/barber shop."""

    SERVICE_DURATIONS = {
        "taglio": 30,
        "barba": 20,
        "taglio_barba": 45,
        "fade": 35,
        "razor": 30,
        "shaving": 20,
        "rasatura": 20,
        "trattamento_barba": 30,
        "colorazione": 60,
        "capelli_lunghi": 40,
        "styling": 20,
    }

    SERVICE_PATTERNS = {
        "taglio": r"tagli[oa]|sforbiciata|accorci|spunt",
        "barba": r"\bbarba\b|regol.*barba",
        "taglio_barba": r"taglio.*barba|barba.*taglio|completo",
        "fade": r"\bfade\b|sfumatura|sfumat[oa]|degradé|degrade",
        "razor": r"\brazor\b|rasoio|lama",
        "shaving": r"shaving|rasatura.*complet|rasatura.*viso",
        "rasatura": r"rasatura|rasa[rt]",
        "trattamento_barba": r"trattamento.*barba|cura.*barba|panno.*caldo|olio.*barba",
        "colorazione": r"color|tint[aou]|meches|colpi.*sole|copertura.*bianchi",
        "capelli_lunghi": r"capelli.*lungh|lungo|ciocche",
        "styling": r"styling|piega|acconciatura|gel|cera",
    }

    DATE_PATTERNS = {
        r"\boggi\b": 0,
        r"\bdomani\b": 1,
        r"dopo\s*domani": 2,
        r"fra\s*(\d+)\s*giorn": None,  # dynamic
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
        """Extract all entities from text."""
        text_lower = text.lower().strip()
        return {
            "service": self.extract_service(text_lower),
            "date": self.extract_date(text_lower),
            "time": self.extract_time(text_lower),
            "barber": self.extract_barber(text_lower),
            "customer_name": self.extract_customer_name(text),
            "notes": self.extract_notes(text_lower),
        }

    def extract_service(self, text: str) -> Optional[str]:
        """Extract service from text using regex patterns."""
        # Check combined first (taglio_barba before taglio or barba alone)
        if re.search(self.SERVICE_PATTERNS["taglio_barba"], text):
            return "taglio_barba"
        for service, pattern in self.SERVICE_PATTERNS.items():
            if service == "taglio_barba":
                continue
            if re.search(pattern, text):
                return service
        return None

    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        today = datetime.now()
        for pattern, days in self.DATE_PATTERNS.items():
            match = re.search(pattern, text)
            if match:
                if days is None:
                    days = int(match.group(1))
                target = today + timedelta(days=days)
                return target.strftime("%Y-%m-%d")

        # Day names
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
        """Extract time from text."""
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

    def extract_barber(self, text: str) -> Optional[str]:
        """Extract barber preference."""
        match = re.search(r"(?:con|da|barbiere)\s+([A-Z][a-zàèéìòù]+)", text, re.IGNORECASE)
        if match:
            name = match.group(1)
            stopwords = {"il", "lo", "la", "un", "una", "per", "alle", "ore", "domani", "oggi"}
            if name.lower() not in stopwords:
                return name
        return None

    def extract_customer_name(self, text: str) -> Optional[str]:
        """Extract customer name from text."""
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
        """Extract notes/special requests."""
        patterns = [
            r"(?:nota|richiesta|speciale|preferisco|vorrei)\s*:?\s*(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def calculate_duration(self, service: str) -> int:
        """Get service duration in minutes."""
        return self.SERVICE_DURATIONS.get(service, 30)

    def create_booking_request(self, text: str) -> BookingRequest:
        """Create a BookingRequest from text."""
        entities = self.extract_all(text)
        service = entities.get("service")
        duration = self.calculate_duration(service) if service else 30
        return BookingRequest(
            service=service,
            date=entities.get("date"),
            time=entities.get("time"),
            barber=entities.get("barber"),
            customer_name=entities.get("customer_name"),
            notes=entities.get("notes"),
            duration_minutes=duration,
        )
