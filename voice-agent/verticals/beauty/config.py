"""
FLUXION Voice Agent - Beauty Center Vertical Configuration
Sub-vertical of: salone (aesthetics focus)
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class BeautyConfig:
    """Configuration for centro estetico / beauty center."""
    name: str = "beauty"
    display_name: str = "Centro Estetico / Beauty Center"
    language: str = "it-IT"
    settore: str = "Estetica e benessere"
    parent_vertical: str = "salone"

    greeting_morning: str = "Buongiorno! Benvenuta al centro estetico."
    greeting_afternoon: str = "Buon pomeriggio! Benvenuta al centro estetico."
    greeting_evening: str = "Buonasera! Benvenuta al centro estetico."

    services: List[str] = field(default_factory=lambda: [
        "pulizia_viso", "ceretta", "manicure", "pedicure",
        "massaggio", "epilazione_laser", "trattamento_viso",
        "trattamento_corpo", "laminazione_ciglia", "extension_ciglia",
        "trucco", "peeling", "radiofrequenza", "pressoterapia", "scrub",
    ])

    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "chiuso",
        "martedi": "09:00-19:00",
        "mercoledi": "09:00-19:00",
        "giovedi": "09:00-19:00",
        "venerdi": "09:00-19:00",
        "sabato": "09:00-18:00",
    })

    prices: Dict[str, str] = field(default_factory=lambda: {
        "pulizia_viso": "€45",
        "ceretta": "€15",
        "manicure": "€25",
        "pedicure": "€30",
        "massaggio": "€50",
        "epilazione_laser": "€80",
        "trattamento_viso": "€60",
        "trattamento_corpo": "€70",
        "laminazione_ciglia": "€40",
        "extension_ciglia": "€60",
        "trucco": "€35",
        "peeling": "€55",
    })

    required_slots: List[str] = field(default_factory=lambda: [
        "service", "date", "time"
    ])
    optional_slots: List[str] = field(default_factory=lambda: [
        "operator_name", "customer_name"
    ])

    schema_fields: List[str] = field(default_factory=lambda: [
        "fototipo", "tipo_pelle", "allergie_prodotti",
        "sensibilita", "trattamenti_precedenti",
        "controindicazioni", "preferenze_operatore"
    ])

    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO",
        "WAITLIST", "INFO", "PREZZI", "ORARI", "SERVIZI"
    ])

    faq_count: int = 11


CONFIG = BeautyConfig()
