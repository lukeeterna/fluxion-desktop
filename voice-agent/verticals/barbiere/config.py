"""
FLUXION Voice Agent - Barbiere Vertical Configuration
Sub-vertical of: salone (focused on men's barbershop)
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class BarbiereConfig:
    """Configuration for barbiere/barber shop vertical."""
    name: str = "barbiere"
    display_name: str = "Barbiere / Barber Shop"
    language: str = "it-IT"
    settore: str = "Cura persona maschile"
    parent_vertical: str = "salone"

    # Greeting variants
    greeting_morning: str = "Buongiorno! Benvenuto dal barbiere."
    greeting_afternoon: str = "Buon pomeriggio! Benvenuto dal barbiere."
    greeting_evening: str = "Buonasera! Benvenuto dal barbiere."

    # Services specific to barbiere
    services: List[str] = field(default_factory=lambda: [
        "taglio", "barba", "taglio_barba", "fade", "razor",
        "shaving", "rasatura", "trattamento_barba", "colorazione",
        "capelli_lunghi", "styling"
    ])

    # Opening hours
    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "chiuso",
        "martedi": "09:00-19:00",
        "mercoledi": "09:00-19:00",
        "giovedi": "09:00-19:00",
        "venerdi": "09:00-19:00",
        "sabato": "09:00-18:00",
    })

    # Base prices
    prices: Dict[str, str] = field(default_factory=lambda: {
        "taglio": "€18",
        "barba": "€12",
        "taglio_barba": "€25",
        "fade": "€22",
        "razor": "€20",
        "shaving": "€15",
        "trattamento_barba": "€20",
        "colorazione": "€35",
        "capelli_lunghi": "€25",
    })

    # Booking slots
    required_slots: List[str] = field(default_factory=lambda: [
        "service", "date", "time"
    ])
    optional_slots: List[str] = field(default_factory=lambda: [
        "barber_name", "customer_name"
    ])

    # Schema fields for customer card
    schema_fields: List[str] = field(default_factory=lambda: [
        "tipo_capelli", "lunghezza", "stile_preferito",
        "prodotti_preferiti", "allergie_prodotti",
        "preferenze_operatore", "storico_tagli"
    ])

    # Intent types
    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO",
        "WAITLIST", "INFO", "PREZZI", "ORARI", "SERVIZI"
    ])

    faq_count: int = 10


CONFIG = BarbiereConfig()
