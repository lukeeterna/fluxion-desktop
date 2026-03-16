"""
FLUXION Voice Agent — Template Fallback NLU (Offline)
Fuzzy sentence matching on 5 core intents — replaces regex as emergency fallback.
Uses rapidfuzz for fast Levenshtein matching (<1ms per classification).
No cloud, no training, no regex chaos.
"""

import logging
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass

logger = logging.getLogger("fluxion.nlu.template_fallback")

# Try rapidfuzz first (C-speed), fall back to fuzzywuzzy, then basic
try:
    from rapidfuzz import fuzz, process as rf_process
    _FUZZY_ENGINE = "rapidfuzz"
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process as rf_process
        _FUZZY_ENGINE = "fuzzywuzzy"
    except ImportError:
        _FUZZY_ENGINE = None
        logger.warning("[NLU] No fuzzy matching library available (install rapidfuzz)")


# ─────────────────────────────────────────────────────────────────
# Intent templates — ~50 phrases per intent, Italian natural language
# These cover the 5 core intents + confirmation/rejection/closure
# ─────────────────────────────────────────────────────────────────

INTENT_TEMPLATES: Dict[str, List[str]] = {
    "PRENOTAZIONE": [
        "vorrei prenotare",
        "voglio prenotare",
        "posso prenotare",
        "mi prenota un appuntamento",
        "fissa un appuntamento",
        "fissami un appuntamento",
        "ho bisogno di un appuntamento",
        "vorrei fissare",
        "mi serve un appuntamento",
        "prenota per me",
        "devo prenotare",
        "potrei prenotare",
        "è possibile prenotare",
        "mi può prenotare",
        "cerco un appuntamento",
        "prenoto",
        "avrei bisogno di prenotare",
        "vorrei venire",
        "posso venire",
        "mi piacerebbe prenotare",
        "voglio un appuntamento",
        "mi fissa",
        "mi può fissare un appuntamento",
        "vorrei prendere un appuntamento",
    ],
    "CANCELLAZIONE": [
        "vorrei cancellare",
        "voglio cancellare",
        "devo cancellare",
        "cancella il mio appuntamento",
        "annulla l'appuntamento",
        "disdici",
        "non vengo più",
        "non posso venire",
        "devo annullare",
        "cancella la prenotazione",
        "elimina l'appuntamento",
        "vorrei annullare",
        "posso cancellare",
        "non riesco a venire",
        "devo disdire",
        "mi cancella l'appuntamento",
    ],
    "SPOSTAMENTO": [
        "vorrei spostare",
        "voglio spostare",
        "posso spostare",
        "cambia la data",
        "cambiare orario",
        "anticipare l'appuntamento",
        "posticipare",
        "mi sposta l'appuntamento",
        "vorrei cambiare giorno",
        "posso cambiare ora",
        "devo spostare",
        "rimandare",
        "riprogrammare",
        "cambia l'appuntamento",
        "vorrei un altro giorno",
        "mi cambia l'orario",
    ],
    "WAITLIST": [
        "lista d'attesa",
        "lista attesa",
        "se si libera un posto",
        "se si libera",
        "primo posto disponibile",
        "appena si libera",
        "mettetemi in lista",
        "in coda",
        "aspetto un posto",
        "voglio aspettare che si liberi",
        "avvisatemi se si libera",
        "chiamatemi se c'è una cancellazione",
    ],
    "CONFERMA": [
        "sì",
        "si",
        "esatto",
        "confermo",
        "va bene",
        "perfetto",
        "ok",
        "d'accordo",
        "giusto",
        "corretto",
        "certamente",
        "certo",
        "assolutamente",
        "proprio così",
        "sì grazie",
        "confermato",
        "tutto giusto",
    ],
    "RIFIUTO": [
        "no",
        "non voglio",
        "no grazie",
        "non mi va",
        "non sono d'accordo",
        "assolutamente no",
        "per niente",
        "neanche per sogno",
        "non mi interessa",
        "lascia stare",
        "non è quello che voglio",
        "sbagliato",
        "non è corretto",
    ],
    "CHIUSURA": [
        "arrivederci",
        "a presto",
        "grazie arrivederci",
        "buona giornata",
        "ci vediamo",
        "alla prossima",
        "addio",
        "ciao",
        "grazie mille arrivederci",
        "nient'altro grazie",
        "basta così",
        "ho finito",
    ],
    "CORTESIA": [
        "buongiorno",
        "buonasera",
        "buon pomeriggio",
        "salve",
        "ciao",
        "grazie",
        "grazie mille",
        "prego",
        "scusi",
        "mi scusi",
    ],
    "ESCALATION": [
        "voglio parlare con un operatore",
        "mi passi un operatore",
        "operatore umano",
        "voglio parlare con una persona",
        "mi passi qualcuno",
        "non voglio parlare con un robot",
        "aiuto",
        "ho bisogno di aiuto",
        "chi c'è di umano",
        "passami il titolare",
    ],
}

# Flatten all templates for matching
_ALL_TEMPLATES: List[Tuple[str, str]] = []  # (template_text, intent)
for intent, templates in INTENT_TEMPLATES.items():
    for t in templates:
        _ALL_TEMPLATES.append((t, intent))

# Profanity word list (Italian common)
_PROFANITY_WORDS = {
    "cazzo", "merda", "minchia", "stronzo", "stronza", "vaffanculo",
    "fanculo", "puttana", "troia", "bastardo", "bastarda", "coglione",
    "porco", "madonna", "dio", "porcodio", "dioporco", "porcamadonna",
    "diocane", "porcatroia", "cazzata", "incazzato", "incazzata",
    "del cazzo", "di merda", "figlio di puttana",
}

# Threshold for fuzzy matching
_FUZZY_THRESHOLD = 65  # minimum similarity score (0-100)


def check_profanity(text: str) -> bool:
    """Check if text contains Italian profanity."""
    words = text.lower().split()
    text_lower = text.lower()
    # Check individual words
    for w in words:
        if w in _PROFANITY_WORDS:
            return True
    # Check multi-word phrases
    for phrase in _PROFANITY_WORDS:
        if " " in phrase and phrase in text_lower:
            return True
    return False


def classify_template(text: str) -> Tuple[str, float]:
    """
    Classify text against intent templates using fuzzy matching.

    Returns:
        Tuple of (intent, confidence_0_to_1)
    """
    if not _FUZZY_ENGINE:
        return "ALTRO", 0.0

    text_lower = text.lower().strip()
    if not text_lower:
        return "ALTRO", 0.0

    # Check profanity first
    if check_profanity(text_lower):
        return "OSCENITA", 0.99

    # Exact match on short inputs (si/no/ciao)
    for template_text, intent in _ALL_TEMPLATES:
        if text_lower == template_text:
            return intent, 0.99

    # Fuzzy match across all templates
    template_texts = [t[0] for t in _ALL_TEMPLATES]
    result = rf_process.extractOne(
        text_lower,
        template_texts,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=_FUZZY_THRESHOLD,
    )

    if result is None:
        return "ALTRO", 0.0

    matched_text, score, idx = result
    intent = _ALL_TEMPLATES[idx][1]
    confidence = score / 100.0

    logger.debug(f"[TEMPLATE] '{text_lower}' → {intent} ({score}%) matched='{matched_text}'")
    return intent, confidence
