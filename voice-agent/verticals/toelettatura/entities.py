"""
FLUXION Voice Agent - Toelettatura Entity Extraction
Standalone vertical (pet grooming)
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


@dataclass
class BookingRequest:
    """Parsed booking request for pet grooming."""
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    pet_name: Optional[str] = None
    pet_type: Optional[str] = None  # cane/gatto
    pet_size: Optional[str] = None  # piccolo/medio/grande
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: int = 60


class ToelettaturaEntityExtractor:
    """Entity extraction for toelettatura / pet grooming."""

    SERVICE_DURATIONS = {
        "bagno": 45,
        "tosatura": 60,
        "stripping": 90,
        "taglio_unghie": 15,
        "pulizia_orecchie": 15,
        "antiparassitario": 20,
        "bagno_medicato": 45,
        "toelettatura_gatto": 60,
        "cucciolo": 30,
        "completo": 90,
    }

    SERVICE_PATTERNS = {
        "bagno": r"\bbagno\b|lavaggio|shampoo|asciugatura",
        "tosatura": r"tosatura|tosar[ei]|tagli[oa].*pelo|accorciar.*pelo|grooming",
        "stripping": r"stripping|strip|pelo.*morto|sottopelo",
        "taglio_unghie": r"unghie|unghiette|taglio.*ungh",
        "pulizia_orecchie": r"orecchi[ae]|pulizia.*orecchi",
        "antiparassitario": r"antiparassitari[oa]|pulci|zecche|pipett",
        "bagno_medicato": r"bagno.*medicat|dermatit|pelle.*irritat|medicat",
        "toelettatura_gatto": r"gatt[oia]|mici[oa]|felino",
        "cucciolo": r"cucciol[oia]|piccol[oia]|primo.*bagno",
        "completo": r"complet[oa]|tutto|pacchetto.*completo|full",
    }

    PET_TYPE_PATTERNS = {
        "cane": r"\bcane\b|\bcani\b|cagnolino|cucciolo|amico.*peloso",
        "gatto": r"\bgatto\b|\bgatti\b|gattino|micio|felino",
    }

    PET_SIZE_PATTERNS = {
        "piccolo": r"piccol[oa]|taglia.*piccol|toy|mini|chihuahua|yorkshire|maltese|barboncino.*nano",
        "medio": r"medi[oa]|taglia.*medi|cocker|beagle|bulldog|border",
        "grande": r"grand[ei]|taglia.*grand|labrador|pastore|golden|rottweiler|alano|maremmano",
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

    def extract_all(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        return {
            "service": self.extract_service(text_lower),
            "date": self.extract_date(text_lower),
            "time": self.extract_time(text_lower),
            "pet_name": self.extract_pet_name(text),
            "pet_type": self.extract_pet_type(text_lower),
            "pet_size": self.extract_pet_size(text_lower),
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

    def extract_pet_name(self, text: str) -> Optional[str]:
        """Extract pet name."""
        patterns = [
            r"(?:si chiama|nome|il mio.*si chiama)\s+([A-Z][a-zàèéìòù]+)",
            r"(?:per|di)\s+([A-Z][a-zàèéìòù]+)(?:\s+il\s+(?:cane|gatto))?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1)
                stopwords = {"il", "lo", "la", "un", "una", "per", "mio", "mia", "domani", "oggi"}
                if name.lower() not in stopwords:
                    return name
        return None

    def extract_pet_type(self, text: str) -> Optional[str]:
        for pet_type, pattern in self.PET_TYPE_PATTERNS.items():
            if re.search(pattern, text):
                return pet_type
        return None

    def extract_pet_size(self, text: str) -> Optional[str]:
        for size, pattern in self.PET_SIZE_PATTERNS.items():
            if re.search(pattern, text):
                return size
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
            r"(?:nota|allergi[ae]|problem[ai]|comportament|aggressiv|paura)\s*:?\s*(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def calculate_duration(self, service: str, pet_size: str = "medio") -> int:
        base = self.SERVICE_DURATIONS.get(service, 60)
        if pet_size == "grande":
            return int(base * 1.5)
        elif pet_size == "piccolo":
            return int(base * 0.75)
        return base

    def create_booking_request(self, text: str) -> BookingRequest:
        entities = self.extract_all(text)
        service = entities.get("service")
        pet_size = entities.get("pet_size", "medio")
        duration = self.calculate_duration(service, pet_size) if service else 60
        return BookingRequest(
            service=service,
            date=entities.get("date"),
            time=entities.get("time"),
            pet_name=entities.get("pet_name"),
            pet_type=entities.get("pet_type"),
            pet_size=pet_size,
            customer_name=entities.get("customer_name"),
            notes=entities.get("notes"),
            duration_minutes=duration,
        )
