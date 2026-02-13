"""
Intent Classification per verticale SALONE
CoVe 2026 - Voice Agent Enterprise
Pattern regex per rilevamento intenti in italiano
"""

import re
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

class IntentType(Enum):
    """Tipi di intent supportati dal salone"""
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
    """Rappresentazione di un intent rilevato"""
    type: IntentType
    confidence: float
    entities: Dict[str, str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}

class SaloneIntentClassifier:
    """Classificatore intent specifico per il verticale Salone"""
    
    # Pattern regex per ciascun intent
    PATTERNS = {
        IntentType.PRENOTAZIONE: [
            r"\b(prenot|fiss|appuntament|prenotaz)\b",
            r"\b(vorrei|posso|mi)\s+(prenotare|fissare)\b",
            r"\b(mi)\s+(prenoto|fisso)\b",
            r"\b(vorrei|posso)\s+(venire|andare)\b",
            r"\b(ho\s+bisogno\s+di)\s+(un|una)\b",
            r"\b(vorrei)\s+(un|una)\s+(taglio|piega|colore|appuntamento)\b",
        ],
        IntentType.CANCELLAZIONE: [
            r"\b(cancell|annull|disd|elimina)\b",
            r"\b(non\s+posso\s+venire)\b",
            r"\b(non\s+ci\s+sono)\b",
            r"\b(mi\s+serve\s+cancellare)\b",
            r"\b(rimuov|togli)\b.*\b(prenotaz|appuntament)\b",
        ],
        IntentType.SPOSTAMENTO: [
            r"\b(spost|posticip|anticip|cambiar|modific|spostare)\b",
            r"\b(cambiare|modificare)\s+(giorno|orario|data)\b",
            r"\b(non\s+mi\s+va\s+bene)\b",
            r"\b(lo\s+sposto)\b",
            r"\b(posso\s+spostare)\b",
        ],
        IntentType.WAITLIST: [
            r"\b(waiting\s+list|waitlist|lista\s+attesa)\b",
            r"\b(non\s+c'[eè]\s+posto)\b",
            r"\b(mi\s+metto\s+in\s+lista)\b",
            r"\b(avvis|contatt).{0,20}\b(liber)\b",
            r"\b(se\s+si\s+libera)\b",
        ],
        IntentType.INFO: [
            r"\b(info|informaz|sapere|dirmi)\b",
            r"\b(come\s+funziona)\b",
            r"\b(cosa\s+offrite)\b",
            r"\b(che\s+cos'[eè])\b",
            r"\b(vorrei\s+sapere)\b",
        ],
        IntentType.PREZZI: [
            r"\b(prezz|cost|quanto|tariff)\b",
            r"\b(quanto\s+(costa|viene|pago))\b",
            r"\b(prezzo\s+di)\b",
            r"\b(listino)\b",
            r"\b(tariffe)\b",
        ],
        IntentType.ORARI: [
            r"\b(orari|apert|chius|quando\s+aprite)\b",
            r"\b(a\s+che\s+ora)\b",
            r"\b(fino\s+a\s+che\s+ora)\b",
            r"\b(siete\s+aperti)\b",
            r"\b(giorni\s+di\s+apertura)\b",
        ],
        IntentType.SERVIZI: [
            r"\b(serviz|trattament|cosa\s+fate|offrite)\b",
            r"\b(fate\s+(anche|i))?\b",
            r"\b(avete\s+(la|il|i|le))\b",
            r"\b(che\s+servizi)\b",
        ],
        IntentType.SALUTO: [
            r"\b(ciao|salve|buongiorno|buonasera|buon\s+pomeriggio|pronto)\b",
            r"^\s*(ciao|salve)\s*$",
        ],
        IntentType.CONGEDO: [
            r"\b(grazie|arrivederci|a\s+presto|ciao\s+ciao|buona\s+giornata)\b",
            r"\b(grazie\s+arrivederci)\b",
            r"\b(ci\s+sentiamo)\b",
            r"\b(basta\s+cos[iì])\b",
        ],
    }
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compila i pattern regex per performance"""
        self.compiled_patterns: Dict[IntentType, List[re.Pattern]] = {}
        for intent, patterns in self.PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def classify(self, text: str) -> Intent:
        """
        Classifica il testo e restituisce l'intent rilevato
        
        Args:
            text: Testo dell'utente
            
        Returns:
            Intent con tipo, confidence ed entità estratte
        """
        text_lower = text.lower().strip()
        scores: Dict[IntentType, float] = {}
        
        # Calcola score per ogni intent
        for intent, patterns in self.compiled_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                if matches:
                    score += len(matches) * 0.5
                    # Bonus per match esatti all'inizio
                    if pattern.match(text_lower):
                        score += 0.3
            scores[intent] = min(score, 1.0)
        
        # Trova il miglior match
        if not scores:
            return Intent(IntentType.FALLBACK, 0.0)
        
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # Estrai entità
        entities = self._extract_entities(text_lower)
        
        # Threshold per fallback
        if best_score < 0.3:
            return Intent(IntentType.FALLBACK, best_score, entities)
        
        return Intent(best_intent, best_score, entities)
    
    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Estrae entità dal testo"""
        entities = {}
        
        # Estrazione servizi
        service_patterns = {
            "taglio": r"\b(taglio|tagliarmi|tagliarsi|tagliare)\b",
            "colore": r"\b(color|tint|tingere|tintura)\b",
            "piega": r"\b(pieg|asciugatura|phon)\b",
            "barba": r"\b(barba|barb)\b",
            "meches": r"\b(meches|meche)\b",
            "balayage": r"\b(balayage)\b",
            "trattamento": r"\b(trattament)\b",
            "manicure": r"\b(manicur|unghie)\b",
            "pedicure": r"\b(pedicur|piedi)\b",
        }
        
        for service, pattern in service_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities["service"] = service
                break
        
        # Estrazione operatore preferito
        operator_match = re.search(r"\b(con|da|preferisco)\s+(\w+)\b", text, re.IGNORECASE)
        if operator_match:
            entities["operator"] = operator_match.group(2)
        
        return entities
    
    def get_confidence(self, text: str, intent_type: IntentType) -> float:
        """Restituisce la confidence per un intent specifico"""
        intent = self.classify(text)
        if intent.type == intent_type:
            return intent.confidence
        return 0.0

# Istanza singleton
CLASSIFIER = SaloneIntentClassifier()

def classify(text: str) -> Intent:
    """Funzione helper per classificazione"""
    return CLASSIFIER.classify(text)
