"""
Entity Extraction per verticale PALESTRA
CoVe 2026 - Voice Agent Enterprise
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class MemberProfile:
    abbonamento: Optional[str] = None
    obiettivi: List[str] = field(default_factory=list)
    livello_fitness: Optional[str] = None
    corsi_preferiti: List[str] = field(default_factory=list)

@dataclass
class BookingRequest:
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    trainer: Optional[str] = None
    customer_name: Optional[str] = None
    level: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: int = 60

class PalestraEntityExtractor:
    SERVICE_DURATIONS = {
        "pt": 60,
        "yoga": 60,
        "pilates": 60,
        "spinning": 45,
        "crossfit": 60,
        "zumba": 45,
        "nuoto": 45,
        "lezione": 60,
        "daypass": 120,
    }
    
    SERVICE_PATTERNS = {
        r"\b(personal\s+trainer|pt|personal)\b": "pt",
        r"\byoga\b": "yoga",
        r"\bpilates\b": "pilates",
        r"\b(spinning|ciclismo)\b": "spinning",
        r"\bzumba\b": "zumba",
        r"\bcrossfit\b": "crossfit",
        r"\bnuoto\b": "nuoto",
        r"\b(lezione|classe)\b": "lezione",
        r"\b(day\s*pass|giornaliero)\b": "daypass",
    }
    
    DATE_PATTERNS = {
        r"\b(oggi)\b": 0,
        r"\b(domani)\b": 1,
        r"\b(dopo\s+domani)\b": 2,
    }
    
    TIME_PERIODS = {
        "mattina": ("07:00", "12:00"),
        "pomeriggio": ("14:00", "18:00"),
        "sera": ("18:00", "22:00"),
    }
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        return {
            "service": self.extract_service(text),
            "date": self.extract_date(text),
            "time": self.extract_time(text),
            "trainer": self.extract_trainer(text),
            "customer_name": self.extract_customer_name(text),
            "level": self.extract_level(text),
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
        
        date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", text)
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = datetime.now().year
            try:
                target_date = datetime(year, month, day)
                return target_date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        return None
    
    def extract_time(self, text: str) -> Optional[str]:
        time_match = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            return f"{hour:02d}:{minute:02d}"
        
        text_lower = text.lower()
        for period, (start, _) in self.TIME_PERIODS.items():
            if re.search(rf"\b{period}\b", text_lower):
                return start
        
        return None
    
    def extract_trainer(self, text: str) -> Optional[str]:
        match = re.search(r"\b(con|dal)\s+(trainer|pt)?\s*(\w+)\b", text, re.IGNORECASE)
        if match:
            return match.group(3).capitalize()
        return None
    
    def extract_customer_name(self, text: str) -> Optional[str]:
        patterns = [
            r"\b(mi\s+chiamo)\s+(\w+)\b",
            r"\b(sono)\s+(\w+)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(2).capitalize()
        return None
    
    def extract_level(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        levels = ["principiante", "base", "intermedio", "avanzato", "atleta"]
        for level in levels:
            if level in text_lower:
                return level
        return None
    
    def extract_notes(self, text: str) -> Optional[str]:
        return None
    
    def calculate_duration(self, service: str) -> int:
        return self.SERVICE_DURATIONS.get(service, 60)
    
    def create_booking_request(self, text: str) -> BookingRequest:
        entities = self.extract_all(text)
        duration = self.calculate_duration(entities.get("service") or "lezione")
        
        return BookingRequest(
            service=entities.get("service"),
            date=entities.get("date"),
            time=entities.get("time"),
            trainer=entities.get("trainer"),
            customer_name=entities.get("customer_name"),
            level=entities.get("level"),
            notes=entities.get("notes"),
            duration_minutes=duration
        )

EXTRACTOR = PalestraEntityExtractor()

def extract(text: str) -> Dict[str, Any]:
    return EXTRACTOR.extract_all(text)
