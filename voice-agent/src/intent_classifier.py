"""
FLUXION Voice Agent - Intent Classifier (Layer 1: Exact Match)

Enterprise-grade intent classification with:
- Exact match for cortesia phrases (O(1) lookup)
- Fuzzy matching for typo tolerance (Levenshtein distance)
- Pattern-based intent classification (regex)

Performance targets:
- Exact match: <1ms
- Fuzzy match: <5ms
- Pattern match: <20ms
"""

import re
import unicodedata
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# INTENT CATEGORIES
# =============================================================================

class IntentCategory(Enum):
    CORTESIA = "cortesia"
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    INFO = "info"
    CONFERMA = "conferma"
    RIFIUTO = "rifiuto"
    OPERATORE = "operatore"  # User wants human operator
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: str
    category: IntentCategory
    confidence: float
    response: Optional[str] = None
    needs_groq: bool = False

    def to_dict(self) -> Dict:
        return {
            "intent": self.intent,
            "category": self.category.value,
            "confidence": self.confidence,
            "response": self.response,
            "needs_groq": self.needs_groq
        }


# =============================================================================
# LAYER 1: EXACT MATCH - CORTESIA PHRASES
# =============================================================================

# Dictionary: normalized_phrase -> (intent_name, category, response)
# 50+ phrases for enterprise coverage
CORTESIA_EXACT: Dict[str, Tuple[str, IntentCategory, str]] = {
    # === SALUTI ===
    "buongiorno": ("greeting_morning", IntentCategory.CORTESIA, "Buongiorno! Sono Paola, come posso aiutarla?"),
    "buonasera": ("greeting_evening", IntentCategory.CORTESIA, "Buonasera! Sono Paola, come posso aiutarla?"),
    "buon pomeriggio": ("greeting_afternoon", IntentCategory.CORTESIA, "Buon pomeriggio! Come posso esserle utile?"),
    "salve": ("greeting_neutral", IntentCategory.CORTESIA, "Salve! Come posso aiutarla oggi?"),
    "ciao": ("greeting_informal", IntentCategory.CORTESIA, "Ciao! Come posso aiutarti?"),
    "buona sera": ("greeting_evening", IntentCategory.CORTESIA, "Buonasera! Sono Paola, come posso aiutarla?"),
    "buon giorno": ("greeting_morning", IntentCategory.CORTESIA, "Buongiorno! Sono Paola, come posso aiutarla?"),
    "pronto": ("greeting_phone", IntentCategory.CORTESIA, "Pronto, sono Paola! Come posso aiutarla?"),
    "si pronto": ("greeting_phone", IntentCategory.CORTESIA, "Buongiorno! Sono Paola, come posso esserle utile?"),

    # === CONGEDI ===
    "arrivederci": ("goodbye_formal", IntentCategory.CORTESIA, "Arrivederci, buona giornata!"),
    "arrivederla": ("goodbye_very_formal", IntentCategory.CORTESIA, "Arrivederla, è stato un piacere assisterla!"),
    "a presto": ("goodbye_soon", IntentCategory.CORTESIA, "A presto! Buona giornata!"),
    "ci vediamo": ("goodbye_informal", IntentCategory.CORTESIA, "Ci vediamo! A presto!"),
    "buona giornata": ("goodbye_day", IntentCategory.CORTESIA, "Grazie, buona giornata anche a lei!"),
    "buona serata": ("goodbye_evening", IntentCategory.CORTESIA, "Grazie, buona serata anche a lei!"),
    "alla prossima": ("goodbye_next", IntentCategory.CORTESIA, "Alla prossima! Buona giornata!"),
    "addio": ("goodbye_final", IntentCategory.CORTESIA, "Arrivederci!"),

    # === RINGRAZIAMENTI ===
    "grazie": ("thanks", IntentCategory.CORTESIA, "Prego!"),
    "grazie mille": ("thanks_big", IntentCategory.CORTESIA, "Di nulla, buona giornata!"),
    "molte grazie": ("thanks_many", IntentCategory.CORTESIA, "Prego, è un piacere!"),
    "ti ringrazio": ("thanks_you", IntentCategory.CORTESIA, "Figurati!"),
    "la ringrazio": ("thanks_formal", IntentCategory.CORTESIA, "Prego, è stato un piacere!"),
    "grazie tante": ("thanks_lots", IntentCategory.CORTESIA, "Di niente!"),
    "mille grazie": ("thanks_thousand", IntentCategory.CORTESIA, "Prego, a disposizione!"),
    "grazie davvero": ("thanks_really", IntentCategory.CORTESIA, "Figuriamoci!"),
    "grazie di tutto": ("thanks_all", IntentCategory.CORTESIA, "Prego, buona giornata!"),

    # === SCUSE ===
    "scusa": ("apology_informal", IntentCategory.CORTESIA, "Nessun problema!"),
    "scusi": ("apology_formal", IntentCategory.CORTESIA, "Nessun problema, mi dica pure."),
    "mi scusi": ("apology_very_formal", IntentCategory.CORTESIA, "Non si preoccupi, mi dica."),
    "perdonami": ("apology_pardon_inf", IntentCategory.CORTESIA, "Figurati, dimmi pure!"),
    "mi perdoni": ("apology_pardon_for", IntentCategory.CORTESIA, "Non c'è problema, mi dica."),
    "chiedo scusa": ("apology_ask", IntentCategory.CORTESIA, "Nessun problema!"),

    # === CONFERME BREVI ===
    "ok": ("ack_ok", IntentCategory.CONFERMA, "Perfetto!"),
    "va bene": ("ack_fine", IntentCategory.CONFERMA, "Ottimo!"),
    "d'accordo": ("ack_agree", IntentCategory.CONFERMA, "Bene!"),
    "perfetto": ("ack_perfect", IntentCategory.CONFERMA, "Benissimo!"),
    "benissimo": ("ack_great", IntentCategory.CONFERMA, "Perfetto!"),
    "ottimo": ("ack_optimal", IntentCategory.CONFERMA, "Bene!"),
    "esatto": ("ack_exact", IntentCategory.CONFERMA, "Perfetto!"),
    "certamente": ("ack_certainly", IntentCategory.CONFERMA, "Bene, procediamo!"),
    "certo": ("ack_sure", IntentCategory.CONFERMA, "Perfetto!"),
    "si": ("ack_yes", IntentCategory.CONFERMA, "Bene!"),
    "si grazie": ("ack_yes_thanks", IntentCategory.CONFERMA, "Perfetto!"),
    "assolutamente": ("ack_absolutely", IntentCategory.CONFERMA, "Benissimo!"),
    "confermo": ("ack_confirm", IntentCategory.CONFERMA, "Prenotazione confermata!"),

    # === NEGAZIONI BREVI ===
    "no": ("neg_no", IntentCategory.RIFIUTO, "D'accordo, mi dica cosa preferisce."),
    "no grazie": ("neg_no_thanks", IntentCategory.RIFIUTO, "Va bene! Posso aiutarla con altro?"),
    "non mi va": ("neg_dont_want", IntentCategory.RIFIUTO, "Capisco. Cosa preferisce?"),
    "niente": ("neg_nothing", IntentCategory.RIFIUTO, "D'accordo. Posso aiutarla con altro?"),
    "lascia stare": ("neg_leave", IntentCategory.RIFIUTO, "Va bene. Mi dica se posso aiutarla con altro."),
    "annulla": ("neg_cancel", IntentCategory.CANCELLAZIONE, "Va bene, annullo. Posso aiutarla con altro?"),

    # === RICHIESTA OPERATORE ===
    "operatore": ("operator_request", IntentCategory.OPERATORE, "La metto in contatto con un operatore, un attimo..."),
    "parlo con una persona": ("operator_person", IntentCategory.OPERATORE, "Certo, la connetto con un operatore."),
    "voglio parlare con qualcuno": ("operator_someone", IntentCategory.OPERATORE, "La metto in contatto con un operatore."),
    "persona vera": ("operator_real", IntentCategory.OPERATORE, "Capisco, la connetto con un operatore."),
    "operatore umano": ("operator_human", IntentCategory.OPERATORE, "Certo, la metto in contatto con un operatore."),
}

# Aliases for common variations (map to canonical form)
CORTESIA_ALIASES: Dict[str, str] = {
    "buondì": "buongiorno",
    "bongiorno": "buongiorno",
    "bongorno": "buongiorno",
    "buongioro": "buongiorno",
    "buongorno": "buongiorno",
    "bonsera": "buonasera",
    "buona seta": "buonasera",
    "grazzie": "grazie",
    "grassie": "grazie",
    "grazia": "grazie",
    "ciaoo": "ciao",
    "ciaooo": "ciao",
    "okk": "ok",
    "okei": "ok",
    "okay": "ok",
    "okkei": "ok",
    "sisi": "si",
    "sissi": "si",
    "nono": "no",
    "arrivederici": "arrivederci",
    "arivederci": "arrivederci",
}


# =============================================================================
# TEXT NORMALIZATION
# =============================================================================

def normalize_input(text: str) -> str:
    """
    Normalize text for matching.

    - Lowercase
    - Remove accents: "è" → "e"
    - Strip whitespace
    - Collapse multiple spaces
    """
    # Lowercase
    text = text.lower()

    # Remove accents: NFD decomposition separates base char from accent
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'  # Mn = Mark, Nonspacing
    )

    # Strip and collapse spaces
    text = ' '.join(text.split())

    return text


# =============================================================================
# LAYER 1: EXACT MATCH
# =============================================================================

def exact_match_intent(text: str, max_distance: int = 2) -> Optional[IntentResult]:
    """
    Layer 1: Exact match with fuzzy fallback.

    1. Normalize input
    2. Check exact match in CORTESIA_EXACT
    3. Check aliases
    4. Fuzzy match with Levenshtein distance <= max_distance

    Args:
        text: User input text
        max_distance: Max Levenshtein distance for fuzzy match (default 2)

    Returns:
        IntentResult if match found, None otherwise

    Performance: <5ms typical
    """
    normalized = normalize_input(text)

    # 1. Exact match (O(1) lookup)
    if normalized in CORTESIA_EXACT:
        intent_name, category, response = CORTESIA_EXACT[normalized]
        return IntentResult(
            intent=intent_name,
            category=category,
            confidence=1.0,
            response=response,
            needs_groq=False
        )

    # 2. Alias lookup
    if normalized in CORTESIA_ALIASES:
        canonical = CORTESIA_ALIASES[normalized]
        if canonical in CORTESIA_EXACT:
            intent_name, category, response = CORTESIA_EXACT[canonical]
            return IntentResult(
                intent=intent_name,
                category=category,
                confidence=0.95,  # Slightly lower for alias
                response=response,
                needs_groq=False
            )

    # 3. Fuzzy match with Levenshtein (for typos)
    # Only for short inputs (likely single words/phrases)
    if len(normalized) <= 20:
        try:
            from Levenshtein import distance

            best_match = None
            best_distance = max_distance + 1

            for phrase in CORTESIA_EXACT.keys():
                d = distance(normalized, phrase)
                if d <= max_distance and d < best_distance:
                    best_distance = d
                    best_match = phrase

            if best_match:
                intent_name, category, response = CORTESIA_EXACT[best_match]
                # Confidence decreases with distance
                confidence = 1.0 - (best_distance * 0.15)
                return IntentResult(
                    intent=intent_name,
                    category=category,
                    confidence=confidence,
                    response=response,
                    needs_groq=False
                )
        except ImportError:
            # Levenshtein not installed, skip fuzzy matching
            pass

    return None


# =============================================================================
# LAYER 2: PATTERN-BASED INTENT CLASSIFICATION
# =============================================================================

# Patterns for each intent category
INTENT_PATTERNS: Dict[IntentCategory, List[str]] = {
    IntentCategory.PRENOTAZIONE: [
        r"(voglio|vorrei|posso|mi\s+servirebbe)\s+(prenotar|fissare|un\s+appuntament)",
        r"\b(prenota|prenotare|prenotazione|appuntamento|appuntamenti)\b",
        r"(mi\s+fissa|mi\s+fa|mi\s+mette|mi\s+prenota)",
        r"\b(disponibil|liber[oai]|slot)\b",
        r"\b(domani|lunedi|martedi|mercoledi|giovedi|venerdi|sabato|domenica)\b.*\b(ora|alle|mattina|pomeriggio)\b",
        # Direct service requests: "vorrei un taglio", "voglio una piega"
        r"(voglio|vorrei|mi\s+serve|mi\s+servirebbe)\s+(un|una|il|la)?\s*(taglio|piega|colore|tinta|barba|trattamento)",
    ],
    IntentCategory.CANCELLAZIONE: [
        r"(annull|cancel|disdic|rinunci)",
        r"(non\s+vengo|non\s+posso|devo\s+uscir)",
        r"(elimina|togli|rimuovi)\s+(appuntament|prenotazion)",
    ],
    IntentCategory.INFO: [
        r"(quanto\s+costa|prezzo|costo|quanto|euro|€)",
        r"(orari[oi]?|aprite|chiudete|quando|che\s+ora)",
        r"(dove|indirizzo|posizione|siete|trovate)",
        r"(accettate|pago|pagamenti|carta|satispay|contanti)",
        r"(fate|offrite|servizi|trattamenti|listino)",
        r"(info|informazion)",
    ],
    IntentCategory.CONFERMA: [
        r"^(si|sì|ok|va\s+bene|d'accordo|perfetto|esatto|confermo)$",
        r"^(confermo|procedi)$",  # Only exact words, not inside other words
    ],
    IntentCategory.RIFIUTO: [
        r"^(no|nope|non|niente)$",
        r"(non\s+mi\s+va|mi\s+dispiace|lascia\s+stare)",
        r"(annulla|stop|basta)",
    ],
    IntentCategory.OPERATORE: [
        r"(operatore|persona|umano|qualcuno)",
        r"(parlo\s+con|voglio\s+parlare)",
    ],
}


def pattern_based_intent(text: str) -> Optional[IntentResult]:
    """
    Layer 2: Pattern-based intent classification.

    Uses regex patterns to classify intent when exact match fails.

    Args:
        text: User input text

    Returns:
        IntentResult with confidence score, None if no pattern matches

    Performance: <20ms typical
    """
    normalized = normalize_input(text)
    scores: Dict[IntentCategory, float] = {}

    for category, patterns in INTENT_PATTERNS.items():
        matches = 0
        for pattern in patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                matches += 1

        if matches > 0:
            # Confidence based on how many patterns matched
            confidence = min(1.0, matches / max(len(patterns), 1) + 0.3)
            scores[category] = confidence

    if not scores:
        return None

    # Return highest confidence match
    best_category = max(scores.items(), key=lambda x: x[1])
    category, confidence = best_category

    return IntentResult(
        intent=category.value,
        category=category,
        confidence=confidence,
        response=None,  # Response determined by downstream handler
        needs_groq=confidence < 0.7  # Low confidence → maybe use Groq
    )


# =============================================================================
# HYBRID CLASSIFIER (PUBLIC API)
# =============================================================================

def classify_intent(text: str, verticale: Optional[Dict] = None) -> IntentResult:
    """
    Hybrid intent classifier: Layer 1 (exact) → Layer 2 (patterns) → Groq fallback.

    This is the main entry point for intent classification.

    Args:
        text: User input text
        verticale: Optional verticale config (for future use)

    Returns:
        IntentResult with classification details

    Flow:
        1. Try exact match (cortesia phrases) - O(1), <1ms
        2. Try pattern matching (regex) - <20ms
        3. Return UNKNOWN with needs_groq=True for LLM fallback
    """
    # Layer 1: Exact match (cortesia)
    exact_result = exact_match_intent(text)
    if exact_result:
        return exact_result

    # Layer 2: Pattern-based
    pattern_result = pattern_based_intent(text)
    if pattern_result and pattern_result.confidence >= 0.4:
        return pattern_result

    # Layer 3: Fallback to Groq (handled by caller)
    return IntentResult(
        intent="unknown",
        category=IntentCategory.UNKNOWN,
        confidence=0.0,
        response=None,
        needs_groq=True
    )


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    # Test cases
    test_phrases = [
        "Buongiorno",
        "buongorno",  # typo
        "Grazie mille",
        "voglio prenotare",
        "quanto costa un taglio",
        "operatore",
        "blablabla random text",
    ]

    print("=== Intent Classifier Test ===\n")
    for phrase in test_phrases:
        result = classify_intent(phrase)
        print(f"Input: '{phrase}'")
        print(f"  → {result.category.value} (confidence: {result.confidence:.2f})")
        if result.response:
            print(f"  → Response: {result.response}")
        print()
