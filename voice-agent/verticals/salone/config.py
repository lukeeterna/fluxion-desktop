"""
Configurazione verticale SALONE (Beauty/Hair)
CoVe 2026 - Voice Agent Enterprise
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SaloneConfig:
    """Configurazione completa per il verticale Salone"""
    
    # Identificazione
    name: str = "salone"
    display_name: str = "Salone di Bellezza / Parrucchiere"
    settore: str = "Beauty/Hair"
    language: str = "it-IT"
    
    # Saluto naturale
    greeting: str = "Buongiorno, sono Sara del salone. Come posso aiutarla?"
    greeting_morning: str = "Buongiorno, sono Sara del salone. Come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio, sono Sara del salone. Come posso aiutarla?"
    greeting_evening: str = "Buonasera, sono Sara del salone. Come posso aiutarla?"
    
    # Servizi offerti
    services: List[str] = field(default_factory=lambda: [
        "taglio", "colore", "piega", "barba", "trattamento",
        "meches", "balayage", "shatush", "manicure", "pedicure",
        "ceretta", "trucco", "extension", "permanente", "stiratura"
    ])
    
    # Slot richiesti per la prenotazione
    required_slots: List[str] = field(default_factory=lambda: ["service", "date", "time"])
    optional_slots: List[str] = field(default_factory=lambda: ["operator", "customer_name"])
    
    # Schema dati cliente
    schema_fields: List[str] = field(default_factory=lambda: [
        "tipo_capelli", "lunghezza", "allergie_prodotti", 
        "preferenze_operatore", "storico_trattamenti"
    ])
    
    # Orari di apertura (default)
    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "martedi": "09:00-19:00",
        "mercoledi": "09:00-19:00",
        "giovedi": "09:00-19:00",
        "venerdi": "09:00-19:00",
        "sabato": "09:00-18:00"
    })
    
    # Prezzi base
    prices: Dict[str, str] = field(default_factory=lambda: {
        "taglio_donna": "35 euro",
        "taglio_uomo": "20 euro",
        "taglio_bambino": "15 euro",
        "colore": "a partire da 40 euro",
        "meches": "a partire da 60 euro",
        "balayage": "a partire da 80 euro",
        "piega": "inclusa nel taglio",
        "trattamento": "a partire da 30 euro"
    })
    
    # FAQ specifiche
    faq_count: int = 9
    
    # Intents supportati
    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO", 
        "WAITLIST", "INFO", "PREZZI", "ORARI", "SERVIZI"
    ])

# Istanza singleton
CONFIG = SaloneConfig()
