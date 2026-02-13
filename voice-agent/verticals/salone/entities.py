"""
Entity Extraction per verticale SALONE
CoVe 2026 - Voice Agent Enterprise
Estrazione entità specifiche per prenotazioni salone
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class CustomerProfile:
    """Profilo cliente per salone"""
    tipo_capelli: Optional[str] = None  # lisci, ricci, mossi, crespi
    lunghezza: Optional[str] = None  # corti, medi, lunghi
    allergie_prodotti: List[str] = field(default_factory=list)
    preferenze_operatore: Optional[str] = None
    storico_trattamenti: List[str] = field(default_factory=list)
    
@dataclass
class BookingRequest:
    """Richiesta di prenotazione estratta"""
    service: Optional[str] = None
    date: Optional[str] = None  # Formato ISO: YYYY-MM-DD
    time: Optional[str] = None  # Formato: HH:MM
    operator: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    duration_minutes: int = 60  # Default durata

class SaloneEntityExtractor:
    """Estrattore entità per il verticale Salone"""
    
    # Mappatura servizi -> durata stimata
    SERVICE_DURATIONS = {
        "taglio": 45,
        "taglio_uomo": 30,
        "taglio_bambino": 30,
        "colore": 90,
        "piega": 30,
        "taglio_colore": 120,
        "meches": 150,
        "balayage": 180,
        "barba": 20,
        "trattamento": 45,
        "manicure": 45,
        "pedicure": 60,
        "ceretta": 30,
        "trucco": 60,
    }
    
    # Pattern servizi
    SERVICE_PATTERNS = {
        r"\b(taglio\s+uomo|taglio\s+maschile)\b": "taglio_uomo",
        r"\b(taglio\s+bambin|taglio\s+bimba)\b": "taglio_bambino",
        r"\b(taglio\s+e\s+colore|colore\s+e\s+taglio)\b": "taglio_colore",
        r"\b(solo\s+)?tagli(o|armi)\b": "taglio",
        r"\b(colore|tint|tintura|tingere)\b": "colore",
        r"\b(pieg|asciugatur|phon)\b": "piega",
        r"\b(meches|meche|colpi\s+di\s+sole)\b": "meches",
        r"\b(balayage|shatush)\b": "balayage",
        r"\b(barba|barb)\b": "barba",
        r"\b(trattament|ricostruz|ristrutturant)\b": "trattamento",
        r"\b(manicur|unghie\s+mani)\b": "manicure",
        r"\b(pedicur|unghie\s+piedi)\b": "pedicure",
        r"\b(cerett|depilaz)\b": "ceretta",
        r"\b(trucc|makeup)\b": "trucco",
    }
    
    # Pattern date relative
    DATE_PATTERNS = {
        r"\b(oggi)\b": 0,
        r"\b(domani)\b": 1,
        r"\b(dopo\s+domani)\b": 2,
        r"\b(fra\s+3\s+giorni|tra\s+3\s+giorni)\b": 3,
        r"\b(fra\s+una\s+settimana|tra\s+una\s+settimana)\b": 7,
        r"\b(prossima\s+settimana)\b": 7,
        r"\b(settimana\s+prossima)\b": 7,
    }
    
    # Pattern orari
    TIME_PATTERNS = [
        r"\b(\d{1,2}):(\d{2})\b",  # 14:30, 9:00
        r"\b(\d{1,2})\s+e\s+(\d{2})\b",  # 14 e 30
        r"\b(le\s+)?(\d{1,2})\b",  # le 14, 15
        r"\b(mattina|pomeriggio|sera)\b",  # periodo del giorno
    ]
    
    # Periodi del giorno
    TIME_PERIODS = {
        "mattina": ("09:00", "12:00"),
        "pomeriggio": ("14:00", "18:00"),
        "sera": ("18:00", "20:00"),
    }
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Estrae tutte le entità rilevanti dal testo
        
        Args:
            text: Testo dell'utente
            
        Returns:
            Dict con tutte le entità estratte
        """
        return {
            "service": self.extract_service(text),
            "date": self.extract_date(text),
            "time": self.extract_time(text),
            "operator": self.extract_operator(text),
            "customer_name": self.extract_customer_name(text),
            "notes": self.extract_notes(text),
        }
    
    def extract_service(self, text: str) -> Optional[str]:
        """Estrae il tipo di servizio richiesto"""
        text_lower = text.lower()
        
        for pattern, service in self.SERVICE_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return service
        
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Estrae la data richiesta (formato YYYY-MM-DD)"""
        text_lower = text.lower()
        
        # Cerca date relative
        for pattern, days_offset in self.DATE_PATTERNS.items():
            if re.search(pattern, text_lower):
                target_date = datetime.now() + timedelta(days=days_offset)
                return target_date.strftime("%Y-%m-%d")
        
        # Cerca formato numerico DD/MM o DD/MM/YYYY
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
        
        # Cerca giorni della settimana
        giorni = {
            "lunedi": 0, "martedi": 1, "mercoledi": 2, "giovedi": 3,
            "venerdi": 4, "sabato": 5, "domenica": 6
        }
        for giorno, target_weekday in giorni.items():
            if re.search(rf"\b{giorno}\b", text_lower):
                today = datetime.now()
                days_ahead = target_weekday - today.weekday()
                if days_ahead <= 0:  # Giorno già passato, prendi prossima settimana
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime("%Y-%m-%d")
        
        return None
    
    def extract_time(self, text: str) -> Optional[str]:
        """Estrae l'orario richiesto (formato HH:MM)"""
        text_lower = text.lower()
        
        # Pattern orario HH:MM
        time_match = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        
        # Pattern "X e Y" (es. "14 e 30")
        time_match = re.search(r"\b(\d{1,2})\s+e\s+(\d{2})\b", text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        
        # Periodi del giorno
        for period, (start, end) in self.TIME_PERIODS.items():
            if re.search(rf"\b{period}\b", text_lower):
                return start  # Restituisce inizio periodo come default
        
        return None
    
    def extract_operator(self, text: str) -> Optional[str]:
        """Estrae il nome dell'operatore preferito"""
        text_lower = text.lower()
        
        # Pattern comuni per operatore
        patterns = [
            r"\b(con|da|preferisco|vorrei)\s+(\w+)\b",
            r"\b(l'\s+)?operatrice\s+(\w+)\b",
            r"\b(l'\s+)?operatore\s+(\w+)\b",
            r"\b(la\s+)?signorina\s+(\w+)\b",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(2)
                # Filtro nomi comuni
                if name not in ["una", "un", "il", "la", "le", "il"]:
                    return name.capitalize()
        
        return None
    
    def extract_customer_name(self, text: str) -> Optional[str]:
        """Estrae il nome del cliente"""
        text_lower = text.lower()
        
        # Pattern per nome cliente
        patterns = [
            r"\b(nome\s+[eè]\s+)?(\w+)\b",  # "nome è Marco" o "Marco"
            r"\b(mi\s+chiamo)\s+(\w+)\b",
            r"\b(sono)\s+(\w+)\b",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(2) if match.lastindex >= 2 else match.group(1)
                if name and len(name) > 2 and name not in ["una", "un", "il", "la", "che", "sono"]:
                    return name.capitalize()
        
        return None
    
    def extract_notes(self, text: str) -> Optional[str]:
        """Estrae note aggiuntive"""
        # Note specifiche da cercare
        note_patterns = [
            r"\b(allergic|sensibil)\b.*\b(a\s+)?(\w+)\b",
            r"\b(prima\s+volta)\b",
            r"\b(non\s+ho\s+mai)\b",
            r"\b(capelli\s+\w+)\b",
        ]
        
        notes = []
        for pattern in note_patterns:
            match = re.search(pattern, text.lower())
            if match:
                notes.append(match.group(0))
        
        return "; ".join(notes) if notes else None
    
    def calculate_duration(self, service: str) -> int:
        """Calcola la durata stimata del servizio"""
        return self.SERVICE_DURATIONS.get(service, 60)
    
    def create_booking_request(self, text: str) -> BookingRequest:
        """Crea una BookingRequest completa dal testo"""
        entities = self.extract_all(text)
        
        duration = self.calculate_duration(entities.get("service") or "taglio")
        
        return BookingRequest(
            service=entities.get("service"),
            date=entities.get("date"),
            time=entities.get("time"),
            operator=entities.get("operator"),
            customer_name=entities.get("customer_name"),
            notes=entities.get("notes"),
            duration_minutes=duration
        )

# Istanza singleton
EXTRACTOR = SaloneEntityExtractor()

def extract(text: str) -> Dict[str, Any]:
    """Funzione helper per estrazione entità"""
    return EXTRACTOR.extract_all(text)
