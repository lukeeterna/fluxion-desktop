"""
FLUXION Voice Agent - Gommista Entity Extraction
Sub-vertical of: auto (tire center focus)
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


@dataclass
class BookingRequest:
    """Parsed booking request for tire center."""
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    targa: Optional[str] = None
    modello: Optional[str] = None
    misura_pneumatici: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: int = 45


class GommistaEntityExtractor:
    """Entity extraction for gommista / tire center."""

    SERVICE_DURATIONS = {
        "cambio_gomme": 45,
        "equilibratura": 30,
        "convergenza": 30,
        "deposito": 15,
        "foratura": 30,
        "pneumatici_nuovi": 60,
        "azoto": 15,
        "valvole_tpms": 20,
        "check_up": 15,
    }

    SERVICE_PATTERNS = {
        "cambio_gomme": r"cambio.*gomm|gomm.*cambio|stagional|invernali|estive|cambio.*pneumatic",
        "equilibratura": r"equilibratura|bilanciatura|bilanci|equilibr",
        "convergenza": r"convergenz|assetto|allineament|geometri.*ruot",
        "deposito": r"deposit|custodia|magazzino|conserv.*gomm",
        "foratura": r"foratura|forata|bucata|chiodo|riparaz.*gomm",
        "pneumatici_nuovi": r"pneumatic.*nuov|gomm.*nuov|acquist.*gomm|preventiv.*gomm",
        "azoto": r"\bazoto\b|gonfiaggio.*azoto",
        "valvole_tpms": r"valvol|tpms|sensori.*pressione",
        "check_up": r"check.*up|controll.*gomm|usur|profondità.*battistr",
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
        "mattina": ("08:00", "12:00"),
        "pomeriggio": ("14:00", "18:00"),
    }

    def extract_all(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        return {
            "service": self.extract_service(text_lower),
            "date": self.extract_date(text_lower),
            "time": self.extract_time(text_lower),
            "targa": self.extract_targa(text),
            "modello": self.extract_modello(text_lower),
            "misura_pneumatici": self.extract_misura(text),
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

    def extract_targa(self, text: str) -> Optional[str]:
        """Extract Italian plate number (AB123CD format)."""
        match = re.search(r"\b([A-Z]{2}\s?\d{3}\s?[A-Z]{2})\b", text.upper())
        if match:
            return match.group(1).replace(" ", "")
        return None

    def extract_modello(self, text: str) -> Optional[str]:
        """Extract vehicle model."""
        patterns = [
            r"(?:auto|macchina|veicolo)\s+(?:è\s+)?(?:una?\s+)?([A-Za-z]+\s+[A-Za-z0-9]+)",
            r"(?:fiat|ford|vw|volkswagen|audi|bmw|mercedes|renault|peugeot|citroen|toyota|hyundai|kia)\s+([a-z0-9]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        return None

    def extract_misura(self, text: str) -> Optional[str]:
        """Extract tire size (e.g., 205/55 R16)."""
        match = re.search(r"(\d{3})[/\\](\d{2,3})\s*[Rr]?\s*(\d{2})", text)
        if match:
            return f"{match.group(1)}/{match.group(2)} R{match.group(3)}"
        return None

    def extract_customer_name(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:mi chiamo|sono|nome)\s+([A-Z][a-zàèéìòù]+(?:\s+[A-Z][a-zàèéìòù]+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def extract_notes(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:nota|problema|rumore|vibrazion)\s*:?\s*(.+?)(?:\.|$)",
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
            targa=entities.get("targa"),
            modello=entities.get("modello"),
            misura_pneumatici=entities.get("misura_pneumatici"),
            customer_name=entities.get("customer_name"),
            notes=entities.get("notes"),
            duration_minutes=duration,
        )
