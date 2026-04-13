"""
FLUXION Voice Agent - Odontoiatra Vertical Configuration
Sub-vertical of: medical (dental focus)
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class OdontoiatraConfig:
    """Configuration for studio odontoiatrico / dentista."""
    name: str = "odontoiatra"
    display_name: str = "Studio Odontoiatrico / Dentista"
    language: str = "it-IT"
    settore: str = "Odontoiatria"
    parent_vertical: str = "medical"

    greeting_morning: str = "Buongiorno! Studio odontoiatrico, come posso aiutarla?"
    greeting_afternoon: str = "Buon pomeriggio! Studio odontoiatrico, come posso aiutarla?"
    greeting_evening: str = "Buonasera! Studio odontoiatrico, come posso aiutarla?"

    services: List[str] = field(default_factory=lambda: [
        "visita", "controllo", "igiene", "pulizia", "sbiancamento",
        "otturazione", "devitalizzazione", "estrazione", "impianto",
        "corona", "ortodonzia", "radiografia", "panoramica", "protesi",
    ])

    opening_hours: Dict[str, str] = field(default_factory=lambda: {
        "lunedi": "09:00-13:00, 14:30-19:00",
        "martedi": "09:00-13:00, 14:30-19:00",
        "mercoledi": "09:00-13:00, 14:30-19:00",
        "giovedi": "09:00-13:00, 14:30-19:00",
        "venerdi": "09:00-13:00, 14:30-19:00",
        "sabato": "09:00-13:00",
    })

    prices: Dict[str, str] = field(default_factory=lambda: {
        "visita": "€50",
        "controllo": "€50",
        "igiene": "€80",
        "sbiancamento": "€250",
        "otturazione": "€100",
        "devitalizzazione": "€200",
        "estrazione": "€150",
        "impianto": "da €1.200",
        "corona": "da €500",
        "panoramica": "€60",
    })

    required_slots: List[str] = field(default_factory=lambda: [
        "service", "date", "time"
    ])
    optional_slots: List[str] = field(default_factory=lambda: [
        "doctor_name", "customer_name", "urgency"
    ])

    schema_fields: List[str] = field(default_factory=lambda: [
        "odontogramma", "storico_trattamenti", "allergie",
        "patologie_croniche", "terapie_in_corso", "rischio_carie",
        "rischio_parodontale", "radiografie", "contatto_emergenza"
    ])

    urgency_levels: List[str] = field(default_factory=lambda: [
        "bassa", "media", "alta", "critica"
    ])

    intents: List[str] = field(default_factory=lambda: [
        "PRENOTAZIONE", "CANCELLAZIONE", "SPOSTAMENTO",
        "URGENTE", "INFO", "PREZZI", "ORARI", "SERVIZI", "ANAMNESI"
    ])

    faq_count: int = 11


CONFIG = OdontoiatraConfig()
