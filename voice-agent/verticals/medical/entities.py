"""
Entity Extraction per verticale MEDICAL
CoVe 2026 - Voice Agent Enterprise
Estrazione entità specifiche per prenotazioni mediche
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class PatientProfile:
    """Profilo paziente per medical"""
    data_nascita: Optional[str] = None
    patologie_croniche: List[str] = field(default_factory=list)
    allergie: List[str] = field(default_factory=list)
    terapie_in_corso: List[str] = field(default_factory=list)
    contatto_emergenza: Optional[str] = None
    
@dataclass
class BookingRequest:
    """Richiesta di prenotazione estratta"""
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    doctor: Optional[str] = None
    customer_name: Optional[str] = None
    urgency: str = "bassa"  # bassa, media, alta, critica
    notes: Optional[str] = None
    duration_minutes: int = 30

class MedicalEntityExtractor:
    """Estrattore entità per il verticale Medical"""
    
    SERVICE_DURATIONS = {
        "visita": 30,
        "controllo": 20,
        "pulizia": 45,
        "trattamento": 60,
        "sbiancamento": 60,
        "otturazione": 45,
        "fisioterapia": 45,
        "riabilitazione": 60,
        "massaggio": 30,
        "agopuntura": 45,
        "consulenza": 30,
    }
    
    SERVICE_PATTERNS = {
        r"\b(visita|consulto|prima\s+visita)\b": "visita",
        r"\b(controllo|check\s*up|checkup)\b": "controllo",
        r"\b(pulizia\s+denti|igiene\s+orale)\b": "pulizia",
        r"\b(trattament|cura\s+denti)\b": "trattamento",
        r"\b(sbiancamento|sbiancare)\b": "sbiancamento",
        r"\b(otturaz|ottura)\b": "otturazione",
        r"\b(fisio|riabilitaz|recupero)\b": "fisioterapia",
        r"\b(massagg)\b": "massaggio",
        r"\b(agopunt|agopuntura)\b": "agopuntura",
        r"\b(consulenz)\b": "consulenza",
    }
    
    DATE_PATTERNS = {
        r"\b(oggi)\b": 0,
        r"\b(domani)\b": 1,
        r"\b(dopo\s+domani)\b": 2,
        r"\b(fra\s+3\s+giorni|tra\s+3\s+giorni)\b": 3,
        r"\b(fra\s+una\s+settimana)\b": 7,
    }
    
    TIME_PERIODS = {
        "mattina": ("09:00", "12:00"),
        "pomeriggio": ("15:00", "18:00"),
        "sera": ("18:00", "19:00"),
    }
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        return {
            "service": self.extract_service(text),
            "date": self.extract_date(text),
            "time": self.extract_time(text),
            "doctor": self.extract_doctor(text),
            "customer_name": self.extract_customer_name(text),
            "urgency": self.extract_urgency(text),
            "notes": self.extract_notes(text),
        }
    
    def extract_service(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for pattern, service in self.SERVICE_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return service
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        
        for pattern, days_offset in self.DATE_PATTERNS.items():
            if re.search(pattern, text_lower):
                target_date = datetime.now() + timedelta(days=days_offset)
                return target_date.strftime("%Y-%m-%d")
        
        date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?\b", text)
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = int(date_match.group(3)) if date_match.group(3) else datetime.now().year
            try:
                target_date = datetime(year, month, day)
                return target_date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        giorni = {
            "lunedi": 0, "martedi": 1, "mercoledi": 2, "giovedi": 3,
            "venerdi": 4, "sabato": 5
        }
        for giorno, target_weekday in giorni.items():
            if re.search(rf"\b{giorno}\b", text_lower):
                today = datetime.now()
                days_ahead = target_weekday - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime("%Y-%m-%d")
        
        return None
    
    def extract_time(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        
        time_match = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        
        for period, (start, end) in self.TIME_PERIODS.items():
            if re.search(rf"\b{period}\b", text_lower):
                return start
        
        return None
    
    def extract_doctor(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        patterns = [
            r"\b(con|dal|dall')\s+(?:dottor|dottoressa|dott\.?)?\s*(\w+)\b",
            r"\b(dottor|dottoressa)\s+(\w+)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(2).capitalize()
        return None
    
    def extract_customer_name(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        patterns = [
            r"\b(mi\s+chiamo)\s+(\w+)\b",
            r"\b(sono)\s+(\w+)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(2).capitalize()
        return None
    
    def extract_urgency(self, text: str) -> str:
        text_lower = text.lower()
        
        if re.search(r"\b(critica|emergenza|sanguin|non\s+respiro)\b", text_lower):
            return "critica"
        if re.search(r"\b(urgent|dolore\s+forte|male\s+forte|subito)\b", text_lower):
            return "alta"
        if re.search(r"\b(media|presto|possibilmente)\b", text_lower):
            return "media"
        return "bassa"
    
    def extract_notes(self, text: str) -> Optional[str]:
        note_patterns = [
            r"\b(allergic)\b.*\b(a\s+)?(\w+)\b",
            r"\b(prendo|assumo)\b.*\b(farmaci)\b",
            r"\b(prima\s+volta)\b",
        ]
        notes = []
        for pattern in note_patterns:
            match = re.search(pattern, text.lower())
            if match:
                notes.append(match.group(0))
        return "; ".join(notes) if notes else None
    
    def calculate_duration(self, service: str) -> int:
        return self.SERVICE_DURATIONS.get(service, 30)
    
    def create_booking_request(self, text: str) -> BookingRequest:
        entities = self.extract_all(text)
        duration = self.calculate_duration(entities.get("service") or "visita")
        
        return BookingRequest(
            service=entities.get("service"),
            date=entities.get("date"),
            time=entities.get("time"),
            doctor=entities.get("doctor"),
            customer_name=entities.get("customer_name"),
            urgency=entities.get("urgency", "bassa"),
            notes=entities.get("notes"),
            duration_minutes=duration
        )

EXTRACTOR = MedicalEntityExtractor()

def extract(text: str) -> Dict[str, Any]:
    return EXTRACTOR.extract_all(text)
