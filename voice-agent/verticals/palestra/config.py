"""
Configurazione verticale PALESTRA (Fitness/PT)
CoVe 2026 - Voice Agent Enterprise
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class PalestraConfig:
    """Configurazione completa per il verticale Palestra"""
    
    name: str = "palestra"
    display_name: str = "Palestra / Fitness Center"
    settore: str = "Fitness/PT"
    language: str = "it-IT"
    
    greeting: str = "Ciao! Sono Sara della palestra. Come posso aiutarti?"
    greeting_morning: str = "Buongiorno, sono Sara della palestra. Come posso aiutarti?"
    greeting_afternoon: str = "Buon pomeriggio, sono Sara della palestra. Come posso aiutarti?"
    
    services: List[str] = field(default_factory=lambda: [
        "lezione", "pt", "daypass", "mesi", "annuale",
        "yoga", "pilates", "spinning", "crossfit", "zumba",
        "piscina", "sauna", "boxing", "nuoto"
    ])
    
    required_slots: List[str] = field(default_factory=lambda: ["service", "date", "time"])
    optional_slots: List[str] = field(default_factory=lambda: ["trainer", "customer_name", "level"])
    
    schema_fields: List[str] = field(default_factory=lambda: [
        "abbonamento", "obiettivi", "livello_fitness", "corsi_preferiti"
    ])
    
    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "07:00-22:00",
        "martedi": "07:00-22:00",
        "mercoledi": "07:00-22:00",
        "giovedi": "07:00-22:00",
        "venerdi": "07:00-22:00",
        "sabato": "09:00-20:00",
        "domenica": "10:00-14:00"
    })
    
    fitness_levels: List[str] = field(default_factory=lambda: [
        "principiante", "intermedio", "avanzato", "atleta"
    ])
    
    faq_count: int = 10
    
    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO", 
        "INFO", "PREZZI", "ORARI", "CORSI", "ABBONAMENTO"
    ])

CONFIG = PalestraConfig()
