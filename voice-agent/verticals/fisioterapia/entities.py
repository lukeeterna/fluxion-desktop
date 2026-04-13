"""
FLUXION Voice Agent - Fisioterapia Entity Extraction
Sub-vertical of: medical (physiotherapy focus)
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


@dataclass
class BookingRequest:
    """Parsed booking request for physiotherapy clinic."""
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    therapist: Optional[str] = None
    customer_name: Optional[str] = None
    urgency: str = "bassa"
    notes: Optional[str] = None
    duration_minutes: int = 45


class FisioterapiaEntityExtractor:
    """Entity extraction for studio fisioterapico."""

    SERVICE_DURATIONS = {
        "fisioterapia": 45,
        "tecarterapia": 30,
        "ultrasuoni": 20,
        "laser": 20,
        "onde_urto": 20,
        "riabilitazione": 60,
        "massoterapia": 45,
        "kinesitaping": 20,
        "linfodrenaggio": 45,
        "elettrostimolazione": 30,
        "posturale": 45,
        "prima_visita": 45,
    }

    SERVICE_PATTERNS = {
        "fisioterapia": r"fisioterapi[ae]|sedut[ae]|manipolazion|terapia.*manual",
        "tecarterapia": r"tecar|tecarterapia|diatermia",
        "ultrasuoni": r"ultrasuon|ecograf|us\b",
        "laser": r"\blaser\b|laserterapia|hilt",
        "onde_urto": r"onde.*urto|shock.*wave|extracorpore",
        "riabilitazione": r"riabilitazion|riabilit|post.*operatori|post.*chirurg",
        "massoterapia": r"massaggio|massoterapia|decontrattur|miofasciale",
        "kinesitaping": r"kinesio|taping|bendaggio.*funzionale|cerott",
        "linfodrenaggio": r"linfodrenaggio|drenaggio.*linfatico|vodder",
        "elettrostimolazione": r"elettrostimolazion|tens|correnti|elettroterap",
        "posturale": r"postur[ae]|ginnastica.*posturale|rieducazione.*posturale|mezieres",
        "prima_visita": r"prima.*visit|valutazion|assessment",
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
        "mattina": ("08:30", "12:00"),
        "pomeriggio": ("14:30", "18:00"),
    }

    URGENCY_PATTERNS = {
        "critica": r"critica|emergenza|paralisi|non sento|trauma.*spinal",
        "alta": r"urgent|dolore forte|blocco|colpo.*strega|sciatica.*acut|non riesco.*muov",
        "media": r"dolore|rigidità|limitazion|infiammazion",
        "bassa": r"controll|routine|manteniment|prevenzione",
    }

    def extract_all(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        return {
            "service": self.extract_service(text_lower),
            "date": self.extract_date(text_lower),
            "time": self.extract_time(text_lower),
            "therapist": self.extract_therapist(text_lower),
            "customer_name": self.extract_customer_name(text),
            "urgency": self.extract_urgency(text_lower),
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

    def extract_therapist(self, text: str) -> Optional[str]:
        match = re.search(r"(?:con|dottor[e]?|dott\.?|fisioterapist[ae])\s+([A-Z][a-zàèéìòù]+)", text, re.IGNORECASE)
        if match:
            return match.group(1)
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

    def extract_urgency(self, text: str) -> str:
        for level, pattern in self.URGENCY_PATTERNS.items():
            if re.search(pattern, text):
                return level
        return "bassa"

    def extract_notes(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:nota|diagnosi|operat[oi]|intervento)\s*:?\s*(.+?)(?:\.|$)",
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
            therapist=entities.get("therapist"),
            customer_name=entities.get("customer_name"),
            urgency=entities.get("urgency", "bassa"),
            notes=entities.get("notes"),
            duration_minutes=duration,
        )
