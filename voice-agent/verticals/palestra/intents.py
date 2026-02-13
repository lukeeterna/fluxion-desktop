"""
Intent Classification per verticale PALESTRA
CoVe 2026 - Voice Agent Enterprise
"""

import re
from enum import Enum
from typing import Dict, List
from dataclasses import dataclass

class IntentType(Enum):
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    SPOSTAMENTO = "spostamento"
    INFO = "info"
    PREZZI = "prezzi"
    ORARI = "orari"
    CORSI = "corsi"
    ABBONAMENTO = "abbonamento"
    SALUTO = "saluto"
    CONGEDO = "congedo"
    FALLBACK = "fallback"

@dataclass
class Intent:
    type: IntentType
    confidence: float
    entities: Dict[str, str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}

class PalestraIntentClassifier:
    PATTERNS = {
        IntentType.PRENOTAZIONE: [
            r"\b(prenot|prenotaz|fiss)\b",
            r"\b(vorrei|posso)\s+(prenotare|fare)\b",
            r"\b(mi\s+iscrivo|voglio\s+iscrivermi)\b",
            r"\b(vorrei\s+fare|prova\s+gratuita)\b",
        ],
        IntentType.CANCELLAZIONE: [
            r"\b(cancell|annull|disd)\b",
            r"\b(non\s+posso\s+venire)\b",
            r"\b(rimuov|togli)\b",
        ],
        IntentType.SPOSTAMENTO: [
            r"\b(spost|posticip|anticip|cambiar)\b",
            r"\b(cambiare|modificare)\s+(giorno|orario)\b",
        ],
        IntentType.INFO: [
            r"\b(info|informaz|sapere)\b",
            r"\b(come\s+funziona)\b",
            r"\b(cosa\s+offrite)\b",
        ],
        IntentType.PREZZI: [
            r"\b(prezz|cost|quanto|tariff|abbonamento)\b",
            r"\b(quanto\s+costa)\b",
        ],
        IntentType.ORARI: [
            r"\b(orari|apert|chius|quando)\b",
            r"\b(a\s+che\s+ora)\b",
        ],
        IntentType.CORSI: [
            r"\b(cors|lezion|lezioni|classi)\b",
            r"\b(yoga|pilates|spinning|zumba|crossfit)\b",
            r"\b(scheda\s+allenamento)\b",
        ],
        IntentType.ABBONAMENTO: [
            r"\b(abbon|iscriz|tessera|membership)\b",
            r"\b(mensile|annuale|trimestrale)\b",
        ],
        IntentType.SALUTO: [
            r"\b(ciao|salve|buongiorno|buonasera)\b",
        ],
        IntentType.CONGEDO: [
            r"\b(grazie|arrivederci|a\s+presto)\b",
        ],
    }
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        self.compiled_patterns: Dict[IntentType, List[re.Pattern]] = {}
        for intent, patterns in self.PATTERNS.items():
            self.compiled_patterns[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def classify(self, text: str) -> Intent:
        text_lower = text.lower().strip()
        scores: Dict[IntentType, float] = {}
        
        for intent, patterns in self.compiled_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                if matches:
                    score += len(matches) * 0.5
                    if pattern.match(text_lower):
                        score += 0.3
            scores[intent] = min(score, 1.0)
        
        if not scores:
            return Intent(IntentType.FALLBACK, 0.0)
        
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        entities = self._extract_entities(text_lower)
        
        if best_score < 0.3:
            return Intent(IntentType.FALLBACK, best_score, entities)
        
        return Intent(best_intent, best_score, entities)
    
    def _extract_entities(self, text: str) -> Dict[str, str]:
        entities = {}
        
        corsi_patterns = {
            "yoga": r"\byoga\b",
            "pilates": r"\bpilates\b",
            "spinning": r"\b(spinning|ciclismo)\b",
            "zumba": r"\bzumba\b",
            "crossfit": r"\bcrossfit\b",
            "nuoto": r"\bnuoto\b",
            "pt": r"\b(personal\s+trainer|pt|personal)\b",
        }
        
        for corso, pattern in corsi_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities["corso"] = corso
                break
        
        return entities

CLASSIFIER = PalestraIntentClassifier()

def classify(text: str) -> Intent:
    return CLASSIFIER.classify(text)
