"""
FLUXION Voice Agent - Fisioterapia Vertical Configuration
Sub-vertical of: medical (physiotherapy focus)
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class FisioterapiaConfig:
    """Configuration for studio fisioterapico."""
    name: str = "fisioterapia"
    display_name: str = "Studio di Fisioterapia"
    language: str = "it-IT"
    settore: str = "Fisioterapia e riabilitazione"
    parent_vertical: str = "medical"

    greeting_morning: str = "Buongiorno! Studio di fisioterapia, come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio! Studio di fisioterapia, come posso aiutarla?"
    greeting_evening: str = "Buonasera! Studio di fisioterapia, come posso aiutarla?"

    services: List[str] = field(default_factory=lambda: [
        "fisioterapia", "tecarterapia", "ultrasuoni", "laser",
        "onde_urto", "riabilitazione", "massoterapia", "kinesitaping",
        "linfodrenaggio", "elettrostimolazione", "posturale", "prima_visita",
    ])

    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "08:30-12:30, 14:30-19:00",
        "martedi": "08:30-12:30, 14:30-19:00",
        "mercoledi": "08:30-12:30, 14:30-19:00",
        "giovedi": "08:30-12:30, 14:30-19:00",
        "venerdi": "08:30-12:30, 14:30-19:00",
        "sabato": "09:00-13:00",
    })

    prices: Dict[str, str] = field(default_factory=lambda: {
        "fisioterapia": "€45",
        "tecarterapia": "€50",
        "ultrasuoni": "€35",
        "laser": "€40",
        "onde_urto": "€55",
        "riabilitazione": "€50",
        "massoterapia": "€40",
        "kinesitaping": "€25",
        "linfodrenaggio": "€50",
        "elettrostimolazione": "€30",
        "posturale": "€45",
        "prima_visita": "€60",
    })

    required_slots: List[str] = field(default_factory=lambda: [
        "service", "date", "time"
    ])
    optional_slots: List[str] = field(default_factory=lambda: [
        "therapist_name", "customer_name", "urgency"
    ])

    schema_fields: List[str] = field(default_factory=lambda: [
        "motivo_trattamento", "valutazione_funzionale",
        "diagnosi", "sedute_programmate", "esiti",
        "patologie_croniche", "allergie", "terapie_in_corso"
    ])

    urgency_levels: List[str] = field(default_factory=lambda: [
        "bassa", "media", "alta", "critica"
    ])

    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO",
        "URGENTE", "INFO", "PREZZI", "ORARI", "SERVIZI", "ANAMNESI"
    ])

    faq_count: int = 10


CONFIG = FisioterapiaConfig()
