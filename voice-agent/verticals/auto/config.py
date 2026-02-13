"""
Configurazione verticale AUTO (Officina)
CoVe 2026 - Voice Agent Enterprise
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class AutoConfig:
    """Configurazione completa per il verticale Auto"""
    
    name: str = "auto"
    display_name: str = "Officina / Centro Auto"
    settore: str = "Officina"
    language: str = "it-IT"
    
    greeting: str = "Buongiorno, sono Sara dell'officina. Come posso aiutarla?"
    greeting_morning: str = "Buongiorno, sono Sara dell'officina. Come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio, sono Sara dell'officina. Come posso aiutarla?"
    
    services: List[str] = field(default_factory=lambda: [
        "tagliando", "riparazione", "gomme", "carrozzeria",
        "cambio_olio", "freni", "elettrauto", "climatizzatore",
        "revisione", "diagnosi", "convergenza"
    ])
    
    required_slots: List[str] = field(default_factory=lambda: ["service", "date", "targa"])
    optional_slots: List[str] = field(default_factory=lambda: ["modello", "km", "urgenza"])
    
    schema_fields: List[str] = field(default_factory=lambda: [
        "targa", "modello", "km", "storico_interventi", "urgenza"
    ])
    
    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "08:00-12:30, 14:30-18:30",
        "martedi": "08:00-12:30, 14:30-18:30",
        "mercoledi": "08:00-12:30, 14:30-18:30",
        "giovedi": "08:00-12:30, 14:30-18:30",
        "venerdi": "08:00-12:30, 14:30-18:30",
        "sabato": "08:00-12:00"
    })
    
    urgenza_levels: List[str] = field(default_factory=lambda: [
        "pianificata", "entro_3_giorni", "entro_24h", "immediata"
    ])
    
    faq_count: = 10
    
    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO", 
        "URGENTE", "PREVENTIVO", "ORARI", "SERVIZI", "INFO"
    ])

CONFIG = AutoConfig()
