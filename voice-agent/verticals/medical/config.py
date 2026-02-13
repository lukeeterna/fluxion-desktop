"""
Configurazione verticale MEDICAL (Odontoiatria/Fisioterapia)
CoVe 2026 - Voice Agent Enterprise
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MedicalConfig:
    """Configurazione completa per il verticale Medical"""
    
    # Identificazione
    name: str = "medical"
    display_name: str = "Studio Medico / Odontoiatrico"
    settore: str = "Odontoiatria/Fisioterapia"
    language: str = "it-IT"
    
    # Saluto naturale
    greeting: str = "Buongiorno, sono Sara dello studio. Come posso aiutarla?"
    greeting_morning: str = "Buongiorno, sono Sara dello studio. Come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio, sono Sara dello studio. Come posso aiutarla?"
    greeting_evening: str = "Buonasera, sono Sara dello studio. Come posso aiutarla?"
    
    # Servizi offerti
    services: List[str] = field(default_factory=lambda: [
        "visita", "trattamento", "controllo", "pulizia", "sbiancamento",
        "otturazione", "corona", "implante", "ortodonzia", "fisioterapia",
        "riabilitazione", "massaggio", "agopuntura", "consulenza"
    ])
    
    # Slot richiesti per la prenotazione
    required_slots: List[str] = field(default_factory=lambda: ["service", "date", "time"])
    optional_slots: List[str] = field(default_factory=lambda: ["doctor", "customer_name", "urgency"])
    
    # Schema dati paziente (anamnesi)
    schema_fields: List[str] = field(default_factory=lambda: [
        "data_nascita", "patologie_croniche", "allergie", 
        "terapie_in_corso", "contatto_emergenza"
    ])
    
    # Orari di apertura (default)
    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "09:00-13:00, 15:00-19:00",
        "martedi": "09:00-13:00, 15:00-19:00",
        "mercoledi": "09:00-13:00, 15:00-19:00",
        "giovedi": "09:00-13:00, 15:00-19:00",
        "venerdi": "09:00-13:00, 15:00-18:00"
    })
    
    # FAQ specifiche
    faq_count: int = 10
    
    # Intents supportati
    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO", 
        "URGENTE", "INFO", "PREZZI", "ORARI", "SERVIZI"
    ])
    
    # Flag urgenza
    urgency_levels: List[str] = field(default_factory=lambda: [
        "bassa", "media", "alta", "critica"
    ])

# Istanza singleton
CONFIG = MedicalConfig()
