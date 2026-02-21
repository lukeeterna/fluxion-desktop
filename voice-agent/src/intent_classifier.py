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

# Italian regex module for robust L0 patterns
try:
    try:
        from .italian_regex import (
            is_conferma, is_rifiuto, is_escalation,
            strip_fillers, detect_correction, CorrectionType,
        )
    except ImportError:
        from italian_regex import (
            is_conferma, is_rifiuto, is_escalation,
            strip_fillers, detect_correction, CorrectionType,
        )
    HAS_ITALIAN_REGEX = True
except ImportError:
    HAS_ITALIAN_REGEX = False

# =============================================================================
# INTENT CATEGORIES
# =============================================================================

class IntentCategory(Enum):
    CORTESIA = "cortesia"
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    SPOSTAMENTO = "spostamento"  # Reschedule appointment
    WAITLIST = "waitlist"  # Request waitlist when slots unavailable
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
    "buongiorno": ("greeting_morning", IntentCategory.CORTESIA, "Buongiorno! Sono Sara, come posso aiutarla?"),
    "buonasera": ("greeting_evening", IntentCategory.CORTESIA, "Buonasera! Sono Sara, come posso aiutarla?"),
    "buon pomeriggio": ("greeting_afternoon", IntentCategory.CORTESIA, "Buon pomeriggio! Come posso esserle utile?"),
    "salve": ("greeting_neutral", IntentCategory.CORTESIA, "Salve! Come posso aiutarla oggi?"),
    "ciao": ("greeting_informal", IntentCategory.CORTESIA, "Ciao! Come posso aiutarti?"),
    "buona sera": ("greeting_evening", IntentCategory.CORTESIA, "Buonasera! Sono Sara, come posso aiutarla?"),
    "buon giorno": ("greeting_morning", IntentCategory.CORTESIA, "Buongiorno! Sono Sara, come posso aiutarla?"),
    "pronto": ("greeting_phone", IntentCategory.CORTESIA, "Pronto, sono Sara! Come posso aiutarla?"),
    "si pronto": ("greeting_phone", IntentCategory.CORTESIA, "Buongiorno! Sono Sara, come posso esserle utile?"),

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
    "esattamente": ("ack_exactly", IntentCategory.CONFERMA, "Perfetto!"),
    "certamente": ("ack_certainly", IntentCategory.CONFERMA, "Bene, procediamo!"),
    "certo": ("ack_sure", IntentCategory.CONFERMA, "Perfetto!"),
    "si": ("ack_yes", IntentCategory.CONFERMA, "Bene!"),
    "sì": ("ack_yes_accent", IntentCategory.CONFERMA, "Bene!"),
    "si si": ("ack_yes_yes", IntentCategory.CONFERMA, "Perfetto!"),
    "si grazie": ("ack_yes_thanks", IntentCategory.CONFERMA, "Perfetto!"),
    "si certo": ("ack_yes_sure", IntentCategory.CONFERMA, "Perfetto!"),
    "si perfetto": ("ack_yes_perfect", IntentCategory.CONFERMA, "Benissimo!"),
    "assolutamente": ("ack_absolutely", IntentCategory.CONFERMA, "Benissimo!"),
    "sicuramente": ("ack_surely", IntentCategory.CONFERMA, "Perfetto!"),
    "ovviamente": ("ack_obviously", IntentCategory.CONFERMA, "Bene!"),
    "naturalmente": ("ack_naturally", IntentCategory.CONFERMA, "Perfetto!"),
    "confermo": ("ack_confirm", IntentCategory.CONFERMA, "Prenotazione confermata!"),
    "confermato": ("ack_confirmed", IntentCategory.CONFERMA, "Perfetto!"),
    "senz'altro": ("ack_without_doubt", IntentCategory.CONFERMA, "Benissimo!"),
    "come no": ("ack_come_no", IntentCategory.CONFERMA, "Perfetto!"),
    "giusto": ("ack_right", IntentCategory.CONFERMA, "Bene!"),
    "proprio cosi": ("ack_proprio", IntentCategory.CONFERMA, "Perfetto!"),
    "ci sto": ("ack_ci_sto", IntentCategory.CONFERMA, "Perfetto!"),
    "procediamo": ("ack_proceed", IntentCategory.CONFERMA, "Bene, procediamo!"),
    "avanti": ("ack_forward", IntentCategory.CONFERMA, "Perfetto, andiamo avanti!"),
    "mi sta bene": ("ack_suits_me", IntentCategory.CONFERMA, "Perfetto!"),
    "mi va bene": ("ack_ok_for_me", IntentCategory.CONFERMA, "Ottimo!"),
    "va benissimo": ("ack_very_fine", IntentCategory.CONFERMA, "Benissimo!"),
    "tutto ok": ("ack_all_ok", IntentCategory.CONFERMA, "Perfetto!"),
    "tutto bene": ("ack_all_good", IntentCategory.CONFERMA, "Bene!"),
    "per me va bene": ("ack_for_me_ok", IntentCategory.CONFERMA, "Perfetto!"),
    "per me ok": ("ack_for_me_ok2", IntentCategory.CONFERMA, "Ottimo!"),
    "sono d'accordo": ("ack_i_agree", IntentCategory.CONFERMA, "Bene!"),
    "dai": ("ack_dai", IntentCategory.CONFERMA, "Perfetto!"),

    # === NEGAZIONI BREVI ===
    "no": ("neg_no", IntentCategory.RIFIUTO, "D'accordo, mi dica cosa preferisce."),
    "no no": ("neg_no_no", IntentCategory.RIFIUTO, "D'accordo. Cosa preferisce?"),
    "no grazie": ("neg_no_thanks", IntentCategory.RIFIUTO, "Va bene! Posso aiutarla con altro?"),
    "no, grazie": ("neg_no_thanks_comma", IntentCategory.RIFIUTO, "Va bene! Posso aiutarla con altro?"),  # CoVe 2026: with comma
    "non mi va": ("neg_dont_want", IntentCategory.RIFIUTO, "Capisco. Cosa preferisce?"),
    "non mi interessa": ("neg_not_interested", IntentCategory.RIFIUTO, "Capisco. Posso aiutarla con altro?"),
    "non mi serve": ("neg_not_needed", IntentCategory.RIFIUTO, "Va bene. Posso aiutarla con altro?"),
    "niente": ("neg_nothing", IntentCategory.RIFIUTO, "D'accordo. Posso aiutarla con altro?"),
    "lascia stare": ("neg_leave", IntentCategory.RIFIUTO, "Va bene. Mi dica se posso aiutarla con altro."),
    "lascia perdere": ("neg_leave_it", IntentCategory.RIFIUTO, "D'accordo. Posso aiutarla con altro?"),
    "meglio di no": ("neg_better_not", IntentCategory.RIFIUTO, "Capisco. Cosa preferisce?"),
    "direi di no": ("neg_id_say_no", IntentCategory.RIFIUTO, "D'accordo. Posso aiutarla con altro?"),
    "non credo": ("neg_dont_think", IntentCategory.RIFIUTO, "Capisco. Posso aiutarla con altro?"),
    "forse no": ("neg_maybe_not", IntentCategory.RIFIUTO, "D'accordo. Mi dica cosa preferisce."),
    "ci devo pensare": ("neg_think_about", IntentCategory.RIFIUTO, "Certo, la ricontatti quando vuole."),
    "preferisco di no": ("neg_prefer_not", IntentCategory.RIFIUTO, "D'accordo. Posso aiutarla con altro?"),
    "non se ne parla": ("neg_out_of_question", IntentCategory.RIFIUTO, "Capisco. Posso aiutarla con altro?"),
    "assolutamente no": ("neg_absolutely_not", IntentCategory.RIFIUTO, "D'accordo. Posso aiutarla con altro?"),
    "per niente": ("neg_not_at_all", IntentCategory.RIFIUTO, "Capisco. Posso aiutarla con altro?"),
    "ho cambiato idea": ("neg_changed_mind", IntentCategory.RIFIUTO, "D'accordo, nessun problema. Posso aiutarla con altro?"),
    "annulla": ("neg_cancel", IntentCategory.CANCELLAZIONE, "Va bene, annullo. Posso aiutarla con altro?"),

    # === FRASI COMPOSTE COMUNI (congedo + ringraziamento) ===
    "grazie arrivederci": ("thanks_goodbye", IntentCategory.CORTESIA, "Prego! Arrivederci, buona giornata!"),
    "grazie mille arrivederci": ("thanks_big_goodbye", IntentCategory.CORTESIA, "Di nulla! Arrivederci, buona giornata!"),
    "grazie a presto": ("thanks_goodbye_soon", IntentCategory.CORTESIA, "Prego! A presto!"),
    "grazie mille a presto": ("thanks_big_goodbye_soon", IntentCategory.CORTESIA, "Di nulla! A presto!"),
    "arrivederci grazie": ("goodbye_thanks", IntentCategory.CORTESIA, "Prego! Arrivederci!"),
    "ok arrivederci": ("ack_goodbye", IntentCategory.CORTESIA, "Arrivederci, buona giornata!"),
    "ok grazie": ("ack_thanks", IntentCategory.CORTESIA, "Prego!"),
    "ok grazie mille": ("ack_thanks_big", IntentCategory.CORTESIA, "Di nulla!"),
    "va bene grazie": ("fine_thanks", IntentCategory.CORTESIA, "Prego! Buona giornata!"),
    "va bene arrivederci": ("fine_goodbye", IntentCategory.CORTESIA, "Arrivederci!"),
    "perfetto arrivederci": ("perfect_goodbye", IntentCategory.CORTESIA, "Arrivederci!"),
    "perfetto grazie": ("perfect_thanks", IntentCategory.CORTESIA, "Prego!"),

    # === RICHIESTA OPERATORE ===
    "operatore": ("operator_request", IntentCategory.OPERATORE, "La metto in contatto con un operatore, un attimo..."),
    "operatrice": ("operator_request_f", IntentCategory.OPERATORE, "La metto in contatto con un'operatrice, un attimo..."),
    "parlo con una persona": ("operator_person", IntentCategory.OPERATORE, "Certo, la connetto con un operatore."),
    "voglio parlare con qualcuno": ("operator_someone", IntentCategory.OPERATORE, "La metto in contatto con un operatore."),
    "voglio parlare con una persona": ("operator_person2", IntentCategory.OPERATORE, "La connetto subito con un operatore."),
    "persona vera": ("operator_real", IntentCategory.OPERATORE, "Capisco, la connetto con un operatore."),
    "persona reale": ("operator_real2", IntentCategory.OPERATORE, "Capisco, la connetto con un operatore."),
    "operatore umano": ("operator_human", IntentCategory.OPERATORE, "Certo, la metto in contatto con un operatore."),
    "essere umano": ("operator_human2", IntentCategory.OPERATORE, "La connetto con un operatore."),
    "passami il titolare": ("operator_owner", IntentCategory.OPERATORE, "La metto in contatto con il titolare."),
    "voglio il titolare": ("operator_owner2", IntentCategory.OPERATORE, "La metto in contatto con il titolare."),
    "parlare col responsabile": ("operator_manager", IntentCategory.OPERATORE, "La connetto con il responsabile."),
    "mi passi il capo": ("operator_boss", IntentCategory.OPERATORE, "La metto in contatto con il responsabile."),
    "richiamatemi": ("operator_callback", IntentCategory.OPERATORE, "Provvedo a farla richiamare."),
    "chiamatemi": ("operator_callback2", IntentCategory.OPERATORE, "Provvedo a farla richiamare."),
    "fatemi chiamare": ("operator_callback3", IntentCategory.OPERATORE, "Provvedo a farla richiamare."),
    "non voglio parlare con un robot": ("operator_no_robot", IntentCategory.OPERATORE, "Capisco, la connetto con un operatore."),
    "sei un robot": ("operator_robot_detect", IntentCategory.OPERATORE, "Sono un assistente virtuale. La connetto con un operatore se preferisce."),
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

    # 1b. Match after stripping punctuation (handles "grazie mille, arrivederci" → "grazie mille arrivederci")
    import re as _re
    normalized_no_punct = ' '.join(_re.sub(r'[^\w\s]', ' ', normalized).split())
    if normalized_no_punct != normalized and normalized_no_punct in CORTESIA_EXACT:
        intent_name, category, response = CORTESIA_EXACT[normalized_no_punct]
        return IntentResult(
            intent=intent_name,
            category=category,
            confidence=0.98,
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
        # Explicit booking intent (wanting to book/take an appointment)
        r"(voglio|vorrei|posso|devo|dovrei|mi\s+servirebbe|mi\s+serve)\s+(prenotar|fissare|prendere\s+(un\s+)?appuntament|un\s+appuntament)",
        # "prendere appuntamento" without modal verb
        r"\bprendere\s+(un\s+)?appuntament",
        # "prenota" or "prenotare" as action (not "annullare la prenotazione")
        r"(mi\s+fissa|mi\s+fa|mi\s+mette|mi\s+prenota)",
        r"\b(prenota|prenotare)\b",  # Action verbs only, not "prenotazione" noun
        # Needing an appointment (positive intent)
        r"(mi\s+serve|ho\s+bisogno\s+di|avrei\s+bisogno\s+di)\s+(un\s+)?appuntament",
        # Standalone "appuntamento" with booking context
        r"(un|per\s+un|per\s+l')\s*appuntament",
        # Check availability
        r"\b(disponibil|liber[oai]|slot)\b",
        # Day + time pattern (scheduling)
        r"\b(domani|lunedi|martedi|mercoledi|giovedi|venerdi|sabato|domenica)\b.*\b(ora|alle|mattina|pomeriggio)\b",
        # Direct service requests: "vorrei un taglio", "voglio una piega"
        r"(voglio|vorrei|mi\s+serve|mi\s+servirebbe)\s+(un|una|il|la)?\s*(taglio|piega|colore|tinta|barba|trattamento)",
    ],
    IntentCategory.CANCELLAZIONE: [
        # Direct cancel keywords with object context (HIGH PRIORITY)
        # Handles: "cancella il mio appuntamento", "annulla l'appuntamento", "disdire la prenotazione"
        r"(annulla|cancella|disdire?)\s+((il|la|l'|lo)\s+)?(mio|mia)?\s*(appuntament|prenotazion|visita)",
        r"(posso|voglio|vorrei|devo)\s+(annullare?|cancellare?|disdire?)\s*((il|la|l')?\s*)?(mia?|mio)?\s*(appuntament|prenotazion)?",
        # Cannot come variations (HIGH PRIORITY) - handle accented and unaccented
        r"non\s+posso\s+(più|piu)?\s*(venire|partecipare|presentarmi)",
        r"non\s+(vengo|ci\s+sono|riesco|faccio)",
        r"devo\s+(uscire?|partire?|andare?|saltare)",
        # Explicit "non posso più" pattern
        r"non\s+posso\s+(più|piu)",
        # Remove/eliminate with context (HIGH PRIORITY)
        r"(voglio|vorrei|devo|posso)?\s*(elimina|eliminare)\s+((il|la|l')?\s+)?(mio|mia)?\s*(appuntament|prenotazion)",
        # Explicit cancel intent patterns (CRITICAL)
        r"(voglio|vorrei|devo|posso)\s+eliminar",
        # "Eliminare" with "mio" pattern
        r"eliminar[e]?\s+(il\s+)?mi[ao]",
    ],
    IntentCategory.SPOSTAMENTO: [
        # Move/change with object
        r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?",
        # CoVe 2026: "cambiare l'orario" specific pattern
        r"(cambia|cambiare)\s+(l['']?\s*)?(orario|ora)",
        # Request to move/change
        r"(posso|vorrei|devo|voglio)\s+(sposta|cambia|modifica|anticipar|posticipare?|rimandare?)",
        # Move earlier/later
        r"(anticipa|anticipare|posticipa|posticipare|rimanda|rimandare)\s*(l[ao]?\s+)?(appuntament|prenotazion|visita)?",
        # Different day/time
        r"(un\s+altro|altra|diverso|diversa)\s+(giorno|data|ora|orario)",
        # Standalone modification keywords
        r"\b(spostare?|anticipare?|posticipare?|rimandare?)\b\s+",
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
        r"^(s[iì]|s[iì]\s+s[iì]|ok(?:ay|ei)?|va\s+bene|d'accordo|perfetto|esatto|esattamente|confermo|confermato)$",
        r"^(certo|certamente|giusto|proprio\s+cos[iì]|benissimo|ottimo|bene)$",
        r"^(assolutamente|sicuramente|ovviamente|naturalmente|senz'altro|senza\s+dubbio|come\s+no)$",
        r"^(s[iì]\s+(?:grazie|certo|va\s+bene|dai|perfetto))$",
        r"^(ci\s+sto|dai|andiamo|procediamo|facciamo|avanti|apposto|tutto\s+(?:bene|ok|giusto|apposto))$",
        r"^(mi\s+(?:sta|va)\s+bene|per\s+me\s+(?:va\s+bene|ok|s[iì])|va\s+benissimo|sono\s+d'accordo)$",
        r"\bconferm[oa](?:re|to)?\b",
    ],
    IntentCategory.RIFIUTO: [
        r"^(no|no\s+no|nono|niente|macch[eé])$",
        r"^(no\s+grazie|non\s+mi\s+(?:va|interessa|serve)|preferisco\s+(?:di\s+)?no)$",
        r"^(assolutamente\s+no|per\s+niente|neanche\s+per\s+(?:sogno|idea)|non\s+se\s+ne\s+parla)$",
        r"^(annulla|stop|basta|lascia(?:mo)?\s+(?:stare|perdere))$",
        r"^(non\s+(?:credo|penso|direi)|forse\s+no|meglio\s+(?:di\s+)?no|direi\s+di\s+no)$",
        r"^(ci\s+(?:devo\s+)?penso|devo\s+pensarci|ho\s+cambiato\s+idea)$",
        r"(non\s+mi\s+(?:va|interessa|serve|convince)|mi\s+dispiace|lascia\s+(?:stare|perdere))",
    ],
    IntentCategory.OPERATORE: [
        r"\b(operatore|operatrice|persona\s+(?:vera|reale|umana)|umano|essere\s+umano)\b",
        r"(parlo\s+con|voglio\s+parlare|mi\s+(?:passi|metta|connetta|trasferisca))",
        r"(parlare\s+con\s+(?:il|la|un|una)?\s*(?:titolare|proprietari[oa]|responsabile|direttore|direttrice|gestore|capo))",
        r"(non\s+(?:voglio|parlo)\s+(?:con\s+)?(?:un\s+)?(?:robot|bot|macchina|computer))",
        r"(sei\s+(?:un\s+)?(?:robot|bot|macchina)|basta\s+(?:con\s+)?(?:sto|questo)?\s*(?:robot|bot))",
        r"(richiamate(?:mi)?|chiamate(?:mi)?|fatemi\s+(?:richiamare|chiamare))",
        r"(voglio\s+(?:essere\s+)?(?:richiamato|chiamato|contattato))",
    ],
    IntentCategory.WAITLIST: [
        # Direct waitlist requests
        r"(mettetemi|mettimi|inseritemi|inseriscimi)\s+(?:in\s+)?(?:lista\s+d'attesa|lista\s+attesa|attesa)",
        r"(voglio|vorrei|posso)\s+(essere\s+)?(?:mettere|inserire)\s+(?:in\s+)?(?:lista\s+d'attesa|attesa)",
        # Wait for availability
        r"(aspetto|aspettare|attendo|attendere)\s+(?:che\s+)?(?:si\s+)?liber",
        r"(avvisate|avvisami|contattate|contattami)\s+quando\s+(?:si\s+)?liber",
        # Accept waitlist proposition
        r"(si|s[iì]|ok|va\s+bene|perfetto)\s+(?:per\s+la\s+)?(?:lista\s+d'attesa|lista\s+attesa|attesa)",
        r"(accetto|accettare)\s+(?:la\s+)?(?:lista\s+d'attesa|lista\s+attesa|attesa)",
        # WhatsApp notification agreement
        r"(mandatemi|inviatemi|scrivetemi|avvisatemi)\s+(?:un\s+)?(?:whatsapp|messaggio|sms)\s+(?:quando)?",
        r"(whatsapp|messaggio|notifica)\s+quando\s+(?:si\s+)?liber",
    ],
}


def pattern_based_intent(text: str) -> Optional[IntentResult]:
    """
    Layer 2: Pattern-based intent classification.

    Uses regex patterns to classify intent when exact match fails.

    CoVe 2026: Enhanced confidence calculation with:
    - Base confidence of 0.65 for any match (was 0.3)
    - Additional 0.1 per extra match
    - Strong intent keywords boost confidence to 0.8+

    Args:
        text: User input text

    Returns:
        IntentResult with confidence score, None if no pattern matches

    Performance: <20ms typical
    """
    normalized = normalize_input(text)
    scores: Dict[IntentCategory, float] = {}

    # Strong intent keywords that indicate clear intent (CoVe 2026)
    STRONG_KEYWORDS = {
        IntentCategory.PRENOTAZIONE: [r'\bprenot', r'\bappuntament', r'\bfissare\b', r'\bprendere\b'],
        IntentCategory.CANCELLAZIONE: [r'\bcancell', r'\bannull', r'\belimin', r'\bdisdir'],
        IntentCategory.SPOSTAMENTO: [r'\bspost', r'\banticip', r'\bposticip', r'\brimand'],
        IntentCategory.WAITLIST: [r'\blista\b', r'\battesa', r'\bavvis'],
        IntentCategory.INFO: [r'\bcosta', r'\bprezzo', r'\borari', r'\bquanto'],
        IntentCategory.CONFERMA: [r'\bs[iì]\b', r'\bok\b', r'\bva\s+bene', r'\bconferm'],
        IntentCategory.RIFIUTO: [r'\bno\b', r'\bnon\b', r'\bannull'],
        IntentCategory.OPERATORE: [r'\boperator', r'\bpersona\b', r'\buman'],
    }

    for category, patterns in INTENT_PATTERNS.items():
        matches = 0
        for pattern in patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                matches += 1

        if matches > 0:
            # CoVe 2026: Enhanced confidence calculation
            # Base confidence 0.65 (was 0.3) + 0.08 per additional match
            base_confidence = 0.65
            bonus = (matches - 1) * 0.08
            
            # Check for strong keywords (CoVe boost)
            strong_match = False
            for strong_pattern in STRONG_KEYWORDS.get(category, []):
                if re.search(strong_pattern, normalized, re.IGNORECASE):
                    strong_match = True
                    break
            
            if strong_match:
                base_confidence = 0.75  # Boost for strong intent keywords
            
            confidence = min(1.0, base_confidence + bonus)
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
# LAYER 2.5: SEMANTIC CLASSIFICATION (TF-IDF)
# =============================================================================

# Lazy load semantic classifier
_semantic_classifier = None


def _get_semantic_classifier():
    """Lazy load semantic classifier."""
    global _semantic_classifier
    if _semantic_classifier is None:
        try:
            from nlu.semantic_classifier import SemanticIntentClassifier
            _semantic_classifier = SemanticIntentClassifier(min_confidence=0.4)
            _semantic_classifier.fit()
        except ImportError:
            return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to load semantic classifier: {e}")
            return None
    return _semantic_classifier


# Map semantic intent names to IntentCategory
SEMANTIC_TO_CATEGORY = {
    "prenotazione": IntentCategory.PRENOTAZIONE,
    "cancellazione": IntentCategory.CANCELLAZIONE,
    "spostamento": IntentCategory.SPOSTAMENTO,
    "waitlist": IntentCategory.WAITLIST,
    "lista_attesa": IntentCategory.WAITLIST,
    "info_orari": IntentCategory.INFO,
    "info_prezzi": IntentCategory.INFO,
    "conferma": IntentCategory.CONFERMA,
    "rifiuto": IntentCategory.RIFIUTO,
    "operatore": IntentCategory.OPERATORE,
    "nuovo_cliente": IntentCategory.UNKNOWN,  # Handled specially
    "saluto": IntentCategory.CORTESIA,
    "congedo": IntentCategory.CORTESIA,
    "ringraziamento": IntentCategory.CORTESIA,
}


def semantic_intent_classify(text: str) -> Optional[IntentResult]:
    """
    Layer 2.5: Semantic classification using TF-IDF.

    Args:
        text: User input text

    Returns:
        IntentResult if confident match, None otherwise

    Performance: ~10ms
    """
    classifier = _get_semantic_classifier()
    if classifier is None:
        return None

    result = classifier.classify(text)
    if result is None:
        return None

    # Map to IntentCategory
    category = SEMANTIC_TO_CATEGORY.get(result.intent, IntentCategory.UNKNOWN)

    return IntentResult(
        intent=result.intent,
        category=category,
        confidence=result.confidence,
        response=None,
        needs_groq=result.confidence < 0.5
    )


# =============================================================================
# HYBRID CLASSIFIER (PUBLIC API)
# =============================================================================

def classify_intent(text: str, verticale: Optional[Dict] = None) -> IntentResult:
    """
    Hybrid intent classifier with semantic layer and italian_regex reinforcement.

    Flow:
        1. Exact match (cortesia phrases) - O(1), <1ms
        1b. Italian Regex pre-filter (conferma/rifiuto/escalation) - <1ms
        2. Pattern matching (regex) - <20ms
        3. Semantic TF-IDF - <10ms
        4. Groq LLM fallback (handled by caller)

    This is the main entry point for intent classification.

    Args:
        text: User input text
        verticale: Optional verticale config (for future use)

    Returns:
        IntentResult with classification details
    """
    # Layer 1: Exact match (cortesia)
    exact_result = exact_match_intent(text)
    if exact_result:
        return exact_result

    # Layer 1b: Italian Regex reinforcement for conferma/rifiuto/escalation
    if HAS_ITALIAN_REGEX:
        # Check conferma
        is_conf, conf_score = is_conferma(text)
        if is_conf and conf_score >= 0.85:
            return IntentResult(
                intent="conferma_regex",
                category=IntentCategory.CONFERMA,
                confidence=conf_score,
                response=None,
                needs_groq=False
            )
        # Check rifiuto
        is_rif, rif_score = is_rifiuto(text)
        if is_rif and rif_score >= 0.85:
            return IntentResult(
                intent="rifiuto_regex",
                category=IntentCategory.RIFIUTO,
                confidence=rif_score,
                response=None,
                needs_groq=False
            )
        # Check escalation
        is_esc, esc_score, esc_type = is_escalation(text)
        if is_esc and esc_score >= 0.85:
            return IntentResult(
                intent=f"operatore_{esc_type}",
                category=IntentCategory.OPERATORE,
                confidence=esc_score,
                response=None,
                needs_groq=False
            )

    # Layer 2: Pattern-based
    pattern_result = pattern_based_intent(text)
    if pattern_result and pattern_result.confidence >= 0.5:
        return pattern_result

    # Layer 2.5: Semantic TF-IDF (for ambiguous patterns)
    semantic_result = semantic_intent_classify(text)
    if semantic_result and semantic_result.confidence >= 0.45:
        return semantic_result

    # Fall back to pattern if available (lower threshold)
    if pattern_result and pattern_result.confidence >= 0.35:
        return pattern_result

    # Layer 4: Fallback to Groq (handled by caller)
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
