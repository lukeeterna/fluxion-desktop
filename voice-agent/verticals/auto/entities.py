"""
Entity Extraction per verticale AUTO
CoVe 2026 - Voice Agent Enterprise
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class BookingRequest:
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    targa: Optional[str] = None
    modello: Optional[str] = None
    km: Optional[int] = None
    urgenza: str = "pianificata"
    notes: Optional[str] = None

class AutoEntityExtractor:
    SERVICE_PATTERNS = {
        r"\btagliando\b": "tagliando",
        r"\b(cambio\s+olio|olio)\b": "cambio_olio",
        r"\b(gomme|pneumatici|cambio\s+gomme)\b": "gomme",
        r"\b(freni|freno|pastiglie)\b": "freni",
        r"\brevisione\b": "revisione",
        r"\bcarrozzeria\b": "carrozzeria",
        r"\b(climatizz|aria\s+condizionata)\b": "climatizzatore",
        r"\b(elettrauto|batteria)\b": "elettrauto",
        r"\b(diagnosi|check|controllo)\b": "diagnosi",
    }
    
    DATE_PATTERNS = {
        r"\b(oggi)\b": 0,
        r"\b(domani)\b": 1,
        r"\b(dopo\s+domani)\b": 2,
    }
    
    TIME_PERIODS = {
        "mattina": ("08:00", "12:00"),
        "pomeriggio": ("14:30", "18:00"),
    }
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        return {
            "service": self.extract_service(text),
            "date": self.extract_date(text),
            "time": self.extract_time(text),
            "targa": self.extract_targa(text),
            "modello": self.extract_modello(text),
            "km": self.extract_km(text),
            "urgenza": self.extract_urgenza(text),
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
    
    def extract_targa(self, text: str) -> Optional[str]:
        # Targa italiana formato: AB123CD
        match = re.search(r"\b([A-Z]{2}\d{3}[A-Z]{2})\b", text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None
    
    def extract_modello(self, text: str) -> Optional[str]:
        # Estrae modello auto dopo "macchina" o "auto"
        match = re.search(r"\b(macchina|auto)\s+(?:e|è)?\s*(?:un|una)?\s*(\w+)\b", text, re.IGNORECASE)
        if match:
            return match.group(2).capitalize()
        return None
    
    def extract_km(self, text: str) -> Optional[int]:
        match = re.search(r"\b(\d{2,6})\s*(km|chilometri)\b", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def extract_urgenza(self, text: str) -> str:
        text_lower = text.lower()
        
        if re.search(r"\b(immediat|subito|non\s+parte)\b", text_lower):
            return "immediata"
        if re.search(r"\b(urgent|entro\s+domani)\b", text_lower):
            return "entro_24h"
        if re.search(r"\b(preferibilmente|questa\s+settimana)\b", text_lower):
            return "entro_3_giorni"
        return "pianificata"
    
    def extract_notes(self, text: str) -> Optional[str]:
        return None
    
    def create_booking_request(self, text: str) -> BookingRequest:
        entities = self.extract_all(text)
        
        return BookingRequest(
            service=entities.get("service"),
            date=entities.get("date"),
            time=entities.get("time"),
            targa=entities.get("targa"),
            modello=entities.get("modello"),
            km=entities.get("km"),
            urgenza=entities.get("urgenza", "pianificata"),
            notes=entities.get("notes")
        )

EXTRACTOR = AutoEntityExtractor()

def extract(text: str) -> Dict[str, Any]:
    return EXTRACTOR.extract_all(text)
