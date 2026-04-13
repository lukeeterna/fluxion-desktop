"""
FLUXION Voice Agent - Toelettatura Vertical Configuration
Standalone vertical (pet grooming)
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ToelettaturaConfig:
    """Configuration for toelettatura / pet grooming."""
    name: str = "toelettatura"
    display_name: str = "Toelettatura / Pet Grooming"
    language: str = "it-IT"
    settore: str = "Cura animali domestici"
    parent_vertical: str = ""

    greeting_morning: str = "Buongiorno! Toelettatura, come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio! Toelettatura, come posso aiutarla?"
    greeting_evening: str = "Buonasera! Toelettatura, come posso aiutarla?"

    services: List[str] = field(default_factory=lambda: [
        "bagno", "tosatura", "stripping", "taglio_unghie",
        "pulizia_orecchie", "antiparassitario", "bagno_medicato",
        "toelettatura_gatto", "cucciolo", "completo",
    ])

    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "09:00-13:00, 14:30-18:30",
        "martedi": "09:00-13:00, 14:30-18:30",
        "mercoledi": "09:00-13:00, 14:30-18:30",
        "giovedi": "09:00-13:00, 14:30-18:30",
        "venerdi": "09:00-13:00, 14:30-18:30",
        "sabato": "09:00-13:00, 14:30-18:30",
    })

    prices: Dict[str, str] = field(default_factory=lambda: {
        "bagno_piccolo": "€25",
        "bagno_medio": "€35",
        "bagno_grande": "€45",
        "tosatura": "€35",
        "tosatura_creativa": "€50",
        "stripping": "€45",
        "taglio_unghie": "€10",
        "pulizia_orecchie": "€10",
        "antiparassitario": "€15",
        "toelettatura_gatto": "€40",
        "cucciolo": "€20",
    })

    required_slots: List[str] = field(default_factory=lambda: [
        "service", "date", "time"
    ])
    optional_slots: List[str] = field(default_factory=lambda: [
        "pet_name", "pet_type", "pet_size", "customer_name"
    ])

    schema_fields: List[str] = field(default_factory=lambda: [
        "nome_animale", "tipo_animale", "razza", "taglia",
        "peso", "allergie", "vaccinazioni", "note_comportamento",
        "storico_trattamenti", "proprietario"
    ])

    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO",
        "INFO", "PREZZI", "ORARI", "SERVIZI", "VACCINI"
    ])

    faq_count: int = 10


CONFIG = ToelettaturaConfig()
