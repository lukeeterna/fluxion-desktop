"""
FLUXION Voice Agent - Odontoiatra Entity Extraction
Sub-vertical of: medical (dental focus)
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


@dataclass
class BookingRequest:
    """Parsed booking request for dental clinic."""
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    doctor: Optional[str] = None
    customer_name: Optional[str] = None
    urgency: str = "bassa"
    notes: Optional[str] = None
    duration_minutes: int = 30


class OdontoiatraEntityExtractor:
    """Entity extraction for studio odontoiatrico."""

    SERVICE_DURATIONS = {
        "visita": 30,
        "controllo": 20,
        "igiene": 45,
        "pulizia": 45,
        "sbiancamento": 60,
        "otturazione": 45,
        "devitalizzazione": 90,
        "estrazione": 45,
        "impianto": 120,
        "corona": 60,
        "ortodonzia": 30,
        "radiografia": 15,
        "panoramica": 15,
        "protesi": 60,
    }

    SERVICE_PATTERNS = {
        "visita": r"visit[ae]|prima.*visit|check.*up",
        "controllo": r"controll[oi]|ricontrollo|follow.*up",
        "igiene": r"igien[ei]|pulizia.*dent|detartrasi|ablazione.*tartaro",
        "pulizia": r"pulizia|pulire",
        "sbiancamento": r"sbianc|whitening|denti.*bianc",
        "otturazione": r"otturazion|cari[ae]|piomb|composit|buco.*dent",
        "devitalizzazione": r"devitalizz|canal|endodonz|nervo.*dent",
        "estrazione": r"estrazion|togliere.*dent|levare.*dent|dente.*giudizio",
        "impianto": r"impiant|implantolog|vite.*titanio|osseointeg",
        "corona": r"corona|capsula|faccett|protesi.*fiss",
        "ortodonzia": r"ortodonz|apparecchi|aligners|invisalign|bracket",
        "radiografia": r"radiografi[ae]|rx|raggi|lastrin",
        "panoramica": r"panoramic[ao]|opt|ortopantomografia",
        "protesi": r"protes[ie]|dentiera|mobile|scheletrat",
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
        "pomeriggio": ("14:30", "18:00"),
    }

    URGENCY_PATTERNS = {
        "critica": r"critica|emergenza|sanguin|non respiro|trauma|avulsione",
        "alta": r"urgent|dolore forte|mal.*dent.*forte|ascesso|gonfiore|pus|rotto",
        "media": r"dolore|fastidio|sensibil|gengiv.*sanguin",
        "bassa": r"controll|pulizia|routine|periodic",
    }

    def extract_all(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        return {
            "service": self.extract_service(text_lower),
            "date": self.extract_date(text_lower),
            "time": self.extract_time(text_lower),
            "doctor": self.extract_doctor(text_lower),
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

    def extract_doctor(self, text: str) -> Optional[str]:
        match = re.search(r"(?:con|dottor[e]?|dott\.?)\s+([A-Z][a-zàèéìòù]+)", text, re.IGNORECASE)
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
            r"(?:nota|allergi[ae]|patolgi[ae]|farmac)\s*:?\s*(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def calculate_duration(self, service: str) -> int:
        return self.SERVICE_DURATIONS.get(service, 30)

    def create_booking_request(self, text: str) -> BookingRequest:
        entities = self.extract_all(text)
        service = entities.get("service")
        duration = self.calculate_duration(service) if service else 30
        return BookingRequest(
            service=service,
            date=entities.get("date"),
            time=entities.get("time"),
            doctor=entities.get("doctor"),
            customer_name=entities.get("customer_name"),
            urgency=entities.get("urgency", "bassa"),
            notes=entities.get("notes"),
            duration_minutes=duration,
        )
