"""
FLUXION Voice Agent - Gommista Vertical Configuration
Sub-vertical of: auto (tire center focus)
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class GommistaConfig:
    """Configuration for gommista / centro pneumatici."""
    name: str = "gommista"
    display_name: str = "Gommista / Centro Pneumatici"
    language: str = "it-IT"
    settore: str = "Pneumatici e servizi auto"
    parent_vertical: str = "auto"

    greeting_morning: str = "Buongiorno! Centro pneumatici, come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio! Centro pneumatici, come posso aiutarla?"
    greeting_evening: str = "Buonasera! Centro pneumatici, come posso aiutarla?"

    services: List[str] = field(default_factory=lambda: [
        "cambio_gomme", "equilibratura", "convergenza",
        "deposito", "foratura", "pneumatici_nuovi",
        "azoto", "valvole_tpms", "check_up",
    ])

    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "08:00-12:30, 14:00-18:30",
        "martedi": "08:00-12:30, 14:00-18:30",
        "mercoledi": "08:00-12:30, 14:00-18:30",
        "giovedi": "08:00-12:30, 14:00-18:30",
        "venerdi": "08:00-12:30, 14:00-18:30",
        "sabato": "08:00-12:30",
    })

    prices: Dict[str, str] = field(default_factory=lambda: {
        "cambio_gomme": "€40",
        "equilibratura": "€20",
        "convergenza": "€45",
        "deposito": "€30",
        "foratura": "€15",
        "azoto": "€5",
        "valvole_tpms": "€20",
        "check_up": "€15",
    })

    required_slots: List[str] = field(default_factory=lambda: [
        "service", "date"
    ])
    optional_slots: List[str] = field(default_factory=lambda: [
        "time", "vehicle_model", "customer_name"
    ])

    schema_fields: List[str] = field(default_factory=lambda: [
        "targa", "modello", "misura_pneumatici",
        "marca_preferita", "storico_cambi", "deposito_attivo"
    ])

    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "PREVENTIVO",
        "INFO", "PREZZI", "ORARI", "SERVIZI", "DEPOSITO"
    ])

    faq_count: int = 10


CONFIG = GommistaConfig()
