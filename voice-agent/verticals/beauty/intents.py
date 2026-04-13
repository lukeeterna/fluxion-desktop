"""
FLUXION Voice Agent - Beauty Center Intent Classification
Sub-vertical of: salone (aesthetics focus)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any


class IntentType(Enum):
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    SPOSTAMENTO = "spostamento"
    WAITLIST = "waitlist"
    INFO = "info"
    PREZZI = "prezzi"
    ORARI = "orari"
    SERVIZI = "servizi"
    ALLERGIE = "allergie"
    SALUTO = "saluto"
    CONGEDO = "congedo"
    FALLBACK = "fallback"


@dataclass
class Intent:
    type: IntentType
    confidence: float = 0.0
    entities: Dict[str, Any] = field(default_factory=dict)


class BeautyIntentClassifier:
    PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.PRENOTAZIONE: [
            r"prenot|fiss|appuntament",
            r"vorrei.*(?:pulizia|ceretta|manicure|massaggio|trattamento|epilazione)",
            r"ho bisogno di|mi serve",
            r"posso\s*(?:prenotare|fissare|venire)",
        ],
        IntentType.CANCELLAZIONE: [
            r"cancell|annull|disd",
            r"non posso venire|non ci sono",
        ],
        IntentType.SPOSTAMENTO: [
            r"spost|cambi.*(?:ora|giorno|data)",
            r"riprogramm|anticipare|posticipare",
        ],
        IntentType.WAITLIST: [
            r"lista.*attesa|attesa",
            r"se si libera|posto.*libero",
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
            r"a che ora|siete apert|quando.*apert",
        ],
        IntentType.SERVIZI: [
            r"servizi|trattament|cosa.*fate|cosa.*offr",
            r"che.*fate|menu|catalogo",
        ],
        IntentType.ALLERGIE: [
            r"allergi[ae]|sensibil|pelle.*reattiv|intolleranz",
            r"non posso usare|reazione",
        ],
        IntentType.SALUTO: [
            r"buongiorno|buon\s*pomeriggio|buonasera|ciao|salve",
        ],
        IntentType.CONGEDO: [
            r"arrivederci|a\s*presto|grazie.*ciao|bye",
        ],
    }

    def __init__(self):
        self._compiled = {}
        for intent_type, patterns in self.PATTERNS.items():
            self._compiled[intent_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def classify(self, text: str) -> Intent:
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
