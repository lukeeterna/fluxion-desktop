"""
Intent Classification per verticale MEDICAL
CoVe 2026 - Voice Agent Enterprise
Pattern regex per rilevamento intenti sanitari in italiano
"""

import re
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

class IntentType(Enum):
    """Tipi di intent supportati dal medical"""
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    SPOSTAMENTO = "spostamento"
    URGENTE = "urgente"
    INFO = "info"
    PREZZI = "prezzi"
    ORARI = "orari"
    SERVIZI = "servizi"
    ANAMNESI = "anamnesi"
    SALUTO = "saluto"
    CONGEDO = "congedo"
    FALLBACK = "fallback"

@dataclass
class Intent:
    """Rappresentazione di un intent rilevato"""
    type: IntentType
    confidence: float
    entities: Dict[str, str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}

class MedicalIntentClassifier:
    """Classificatore intent specifico per il verticale Medical"""
    
    PATTERNS = {
        IntentType.PRENOTAZIONE: [
            r"\b(prenot|fiss|appuntament)\b",
            r"\b(vorrei|posso|mi)\s+(prenotare|fissare)\b",
            r"\b(mi\s+prenoto|fisso)\b",
            r"\b(visita|controllo|trattamento)\b",
            r"\b(vedere|incontrare)\s+(il|la)?\s+(dottor|dottoressa|dott)\b",
        ],
        IntentType.CANCELLAZIONE: [
            r"\b(cancell|annull|disd|elimina)\b",
            r"\b(non\s+posso\s+venire)\b",
            r"\b(non\s+ci\s+sono|non\s+vengo)\b",
            r"\b(rimuov|togli)\b.*\b(prenotaz|appuntament|visita)\b",
        ],
        IntentType.SPOSTAMENTO: [
            r"\b(spost|posticip|anticip|cambiar|modific)\b",
            r"\b(cambiare|modificare)\s+(giorno|orario|data)\b",
            r"\b(altro\s+giorno|altra\s+data)\b",
        ],
        IntentType.URGENTE: [
            r"\b(urgen|emergen|dolore|male|acut)\b",
            r"\b(male\s+alle?|dolore\s+alle?)\b",
            r"\b(non\s+respiro|sanguin)\b",
            r"\b(dolore\s+(forte|intenso))\b",
            r"\b(cadut|rott|frattura)\b",
        ],
        IntentType.INFO: [
            r"\b(info|informaz|sapere|dirmi)\b",
            r"\b(come\s+funziona)\b",
            r"\b(cosa\s+devo)\b",
            r"\b(documenti|referto)\b",
        ],
        IntentType.PREZZI: [
            r"\b(prezz|cost|quanto|tariff)\b",
            r"\b(quanto\s+(costa|viene))\b",
            r"\b(prezzo\s+(di|del|della))\b",
            r"\b(tariffe|listino)\b",
            r"\b(copertura|ticket)\b",
        ],
        IntentType.ORARI: [
            r"\b(orari|apert|chius|quando)\b",
            r"\b(a\s+che\s+ora)\b",
            r"\b(fino\s+a\s+che\s+ora)\b",
            r"\b(giorni\s+di)\b",
        ],
        IntentType.SERVIZI: [
            r"\b(serviz|trattament|specializz|cosa\s+fate)\b",
            r"\b(fate\s+(anche)?)\b",
            r"\b(avete\s+(la|il|i|le))\b",
            r"\b(che\s+(servizi|cure))\b",
        ],
        IntentType.ANAMNESI: [
            r"\b(allergi|patologi|terapi|medicin)\b",
            r"\b(prendo|assumo)\b.*\b(farmaci|medicinali)\b",
            r"\b(malattie|operazioni)\b",
        ],
        IntentType.SALUTO: [
            r"\b(ciao|salve|buongiorno|buonasera|buon\s+pomeriggio|pronto)\b",
        ],
        IntentType.CONGEDO: [
            r"\b(grazie|arrivederci|a\s+presto|buona\s+giornata)\b",
            r"\b(ci\s+sentiamo|a\s+dopo)\b",
        ],
    }
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        self.compiled_patterns: Dict[IntentType, List[re.Pattern]] = {}
        for intent, patterns in self.PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
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
        
        # Estrazione tipo visita
        visit_patterns = {
            "visita": r"\b(visita|consulto)\b",
            "controllo": r"\b(controllo|check)\b",
            "pulizia": r"\b(pulizia|igiene)\b",
            "trattamento": r"\b(trattament|cura)\b",
            "fisioterapia": r"\b(fisio|riabilitaz)\b",
        }
        
        for service, pattern in visit_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities["service"] = service
                break
        
        # Estrazione dottore preferito
        doctor_match = re.search(r"\b(con|dal|dall')\s+(dottor|dottoressa|dott\.?)?\s*(\w+)\b", text, re.IGNORECASE)
        if doctor_match:
            entities["doctor"] = doctor_match.group(3)
        
        # Estrazione livello urgenza
        if re.search(r"\b(urgent|emergenz|subito|adesso)\b", text, re.IGNORECASE):
            entities["urgency"] = "alta"
        
        return entities

CLASSIFIER = MedicalIntentClassifier()

def classify(text: str) -> Intent:
    return CLASSIFIER.classify(text)
