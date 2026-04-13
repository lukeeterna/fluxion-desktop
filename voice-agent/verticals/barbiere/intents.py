"""
FLUXION Voice Agent - Barbiere Intent Classification
Sub-vertical of: salone (men's barbershop focus)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class IntentType(Enum):
    """Intent types for barbiere vertical."""
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    SPOSTAMENTO = "spostamento"
    WAITLIST = "waitlist"
    INFO = "info"
    PREZZI = "prezzi"
    ORARI = "orari"
    SERVIZI = "servizi"
    SALUTO = "saluto"
    CONGEDO = "congedo"
    FALLBACK = "fallback"


@dataclass
class Intent:
    """Classified intent with confidence."""
    type: IntentType
    confidence: float = 0.0
    entities: Dict[str, Any] = field(default_factory=dict)


class BarbiereIntentClassifier:
    """Intent classifier for barbiere vertical."""

    PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.PRENOTAZIONE: [
            r"prenot|fiss|appuntament",
            r"vorrei.*(?:taglio|barba|fade|razor)",
            r"ho bisogno di|mi serve",
            r"posso\s*(?:prenotare|fissare|venire)",
        ],
        IntentType.CANCELLAZIONE: [
            r"cancell|annull|disd",
            r"non posso venire|non ci sono",
            r"devo annullare|elimina.*prenotazione",
        ],
        IntentType.SPOSTAMENTO: [
            r"spost|cambi.*(?:ora|giorno|data)",
            r"riprogramm|anticipare|posticipare",
            r"posso spostare",
        ],
        IntentType.WAITLIST: [
            r"lista.*attesa|attesa",
            r"se si libera|posto.*libero",
            r"avvisatemi se|chiamatemi se",
        ],
        IntentType.INFO: [
            r"informazion|sapere|chieder|domand",
            r"come funzion|mi dica|vorrei sapere",
        ],
        IntentType.PREZZI: [
            r"prezz|cost|quanto|tariff",
            r"quanto costa|quanto viene|listino",
        ],
        IntentType.ORARI: [
            r"orari|apert|chius",
            r"a che ora|siete aperti|quando.*apert",
        ],
        IntentType.SERVIZI: [
            r"servizi|trattament|cosa.*fate|cosa.*offr",
            r"che.*fate|menu|catalogo",
        ],
        IntentType.SALUTO: [
            r"buongiorno|buon\s*pomeriggio|buonasera|ciao|salve",
        ],
        IntentType.CONGEDO: [
            r"arrivederci|a\s*presto|grazie.*ciao|bye|addio",
        ],
    }

    def __init__(self):
        """Compile regex patterns."""
        self._compiled = {}
        for intent_type, patterns in self.PATTERNS.items():
            self._compiled[intent_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def classify(self, text: str) -> Intent:
        """Classify text into intent with confidence score."""
        text_lower = text.lower().strip()
        best_intent = IntentType.FALLBACK
        best_score = 0.0

        for intent_type, patterns in self._compiled.items():
            score = 0.0
            for pattern in patterns:
                if pattern.search(text_lower):
                    score += 0.5
            if score > best_score:
                best_score = min(score, 1.0)
                best_intent = intent_type

        if best_score < 0.3:
            best_intent = IntentType.FALLBACK
            best_score = 0.0

        return Intent(type=best_intent, confidence=best_score)
