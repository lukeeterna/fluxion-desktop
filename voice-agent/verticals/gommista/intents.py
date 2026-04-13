"""
FLUXION Voice Agent - Gommista Intent Classification
Sub-vertical of: auto (tire center focus)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any


class IntentType(Enum):
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    PREVENTIVO = "preventivo"
    INFO = "info"
    PREZZI = "prezzi"
    ORARI = "orari"
    SERVIZI = "servizi"
    DEPOSITO = "deposito"
    SALUTO = "saluto"
    CONGEDO = "congedo"
    FALLBACK = "fallback"


@dataclass
class Intent:
    type: IntentType
    confidence: float = 0.0
    entities: Dict[str, Any] = field(default_factory=dict)


class GommistaIntentClassifier:
    PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.PRENOTAZIONE: [
            r"prenot|fiss|appuntament",
            r"vorrei.*(?:cambio|equilibratura|convergenza|gomm)",
            r"devo.*(?:cambiare|montare).*gomm",
            r"ho.*(?:foratura|forata|bucata)",
        ],
        IntentType.CANCELLAZIONE: [
            r"cancell|annull|disd",
            r"non posso venire|non ci sono",
        ],
        IntentType.PREVENTIVO: [
            r"preventiv|quotazione|stima",
            r"quanto.*(?:verrebbe|costerebbe|costerebbe)",
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
            r"servizi|cosa.*fate|cosa.*offr",
            r"fate.*(?:equilibratura|convergenza|azoto)",
        ],
        IntentType.DEPOSITO: [
            r"deposit|custodia|magazzin|conserv.*gomm",
            r"dove.*mett.*gomm|ritir.*gomm",
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
