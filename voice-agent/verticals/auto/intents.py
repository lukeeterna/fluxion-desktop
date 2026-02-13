"""
Intent Classification per verticale AUTO
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
    URGENTE = "urgente"
    PREVENTIVO = "preventivo"
    ORARI = "orari"
    SERVIZI = "servizi"
    INFO = "info"
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

class AutoIntentClassifier:
    PATTERNS = {
        IntentType.PRENOTAZIONE: [
            r"\b(prenot|prenotaz|fiss|portare\s+la\s+macchina)\b",
            r"\b(vorrei|posso|devo)\s+(prenotare|fissare|portare)\b",
            r"\b(depositare|lasciare)\s+(la\s+)?(macchina|auto)\b",
            r"\b(tagliando|revisione|cambio\s+olio)\b",
        ],
        IntentType.CANCELLAZIONE: [
            r"\b(cancell|annull|disd)\b",
            r"\b(non\s+posso\s+portare)\b",
            r"\b(rimuov|togli)\b",
        ],
        IntentType.SPOSTAMENTO: [
            r"\b(spost|posticip|anticip|cambiar)\b",
            r"\b(cambiare|modificare)\s+(giorno|data)\b",
            r"\b(altro\s+giorno)\b",
        ],
        IntentType.URGENTE: [
            r"\b(urgen|emergen|subito|immediat)\b",
            r"\b(non\s+parte|non\s+si\s+accende)\b",
            r"\b(luce\s+rossa|spia)\b",
            r"\b(rumore\s+strano|problema\s+grave)\b",
        ],
        IntentType.PREVENTIVO: [
            r"\b(preventiv|costo|quanto\s+costa|stima)\b",
            r"\b(quanto\s+viene)\b",
            r"\b(prezzo\s+approssimativo)\b",
        ],
        IntentType.ORARI: [
            r"\b(orari|apert|chius|quando)\b",
            r"\b(a\s+che\s+ora)\b",
            r"\b(posso\s+venire)\b",
        ],
        IntentType.SERVIZI: [
            r"\b(serviz|tagliand|gomm|cambio\s+olio|freni)\b",
            r"\b(fate\s+(anche)?)\b",
            r"\b(elettrauto|carrozzeria|revisione)\b",
        ],
        IntentType.INFO: [
            r"\b(info|informaz|sapere)\b",
            r"\b(cosa\s+mi\s+serve)\b",
            r"\b(documenti|libretto)\b",
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
        
        # Estrazione targa
        targa_match = re.search(r"\b([A-Z]{2}\d{3}[A-Z]{2}|[A-Z]{2}\s*\d{3}\s*[A-Z]{2})\b", text, re.IGNORECASE)
        if targa_match:
            entities["targa"] = targa_match.group(1).upper()
        
        # Estrazione servizio
        service_patterns = {
            "tagliando": r"\btagliando\b",
            "cambio_olio": r"\b(cambio\s+olio|olio)\b",
            "gomme": r"\b(gomme|pneumatici|pneumatico)\b",
            "freni": r"\b(freni|freno)\b",
            "revisione": r"\brevisione\b",
            "carrozzeria": r"\bcarrozzeria\b",
        }
        
        for service, pattern in service_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities["service"] = service
                break
        
        return entities

CLASSIFIER = AutoIntentClassifier()

def classify(text: str) -> Intent:
    return CLASSIFIER.classify(text)
