"""
FLUXION Voice Agent - Comprehensive Italian Regex Patterns (L0 Layer)

Enterprise-grade regex patterns for Italian natural language understanding.
All patterns are pre-compiled for <1ms execution.

Categories:
    1. Filler Words / Interjections (strip before processing)
    2. Confirmation Patterns (conferma)
    3. Rejection Patterns (rifiuto)
    4. Escalation Patterns (operator/human request + WhatsApp call trigger)
    5. Services by Vertical (salone, palestra, medical, auto)
    6. Multi-Service Detection (compound requests)
    7. Inappropriate Content Filter (3 severity levels)
    8. Objections / Corrections / Flow Control

Performance: All patterns pre-compiled, <1ms per match.
"""

import re
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# 1. FILLER WORDS / INTERJECTIONS
# =============================================================================
# Strip these before processing to improve downstream accuracy.
# Covers: hesitations, discourse markers, politeness fillers, STT artifacts.

FILLER_PATTERNS = [
    # Hesitations / thinking sounds
    r"\b(?:ehm+|uhm+|mmh+|hmm+|eee+|aaa+|boh|mah|beh|bah)\b",
    # Discourse markers
    r"\b(?:allora|dunque|ecco|insomma|praticamente|comunque|diciamo|tipo)\b",
    # Politeness fillers (when embedded, not standalone)
    r"\b(?:per\s+favore|per\s+cortesia|per\s+piacere|gentilmente|cortesemente)\b",
    # STT artifacts and interjections
    r"\b(?:ehi|eh|oh|ah|ahi|oh\s+mio\s+dio|oddio|mamma\s+mia)\b",
    # Filler phrases
    r"\b(?:come\s+dire|cioè|in\s+pratica|voglio\s+dire|sai|sa)\b",
    # Softeners
    r"\b(?:magari|eventualmente|volendo|semmai|casomai)\b",
    # Attention getters
    r"\b(?:senti|senta|scolta|ascolta|guardi|guarda)\b",
]

# Pre-compiled combined pattern for stripping fillers
_FILLER_COMPILED = re.compile(
    r"(?:^|\s)(?:" + "|".join(FILLER_PATTERNS) + r")(?:\s|$|[,;.!?])",
    re.IGNORECASE
)


def strip_fillers(text: str) -> str:
    """
    Remove filler words/interjections from text.
    Returns cleaned text with normalized whitespace.
    """
    cleaned = _FILLER_COMPILED.sub(" ", text)
    # Collapse multiple spaces
    return " ".join(cleaned.split()).strip()


def detect_fillers(text: str) -> List[str]:
    """Return list of filler words found in text."""
    return _FILLER_COMPILED.findall(text)


# =============================================================================
# 2. CONFIRMATION PATTERNS
# =============================================================================
# Comprehensive Italian affirmative expressions.

CONFERMA_PATTERNS = [
    # Direct affirmations
    r"^(?:s[iì]|s[iì]\s+s[iì]|certo|certamente|esatto|esattamente|giusto|proprio\s+cos[iì])$",
    # Agreement
    r"^(?:ok(?:ay|ei)?|va\s+bene|d'accordo|perfetto|benissimo|ottimo|bene)$",
    # Confirmation verbs
    r"^(?:confermo|confermato|apposto|tutto\s+(?:bene|ok|giusto|apposto))$",
    # Emphatic affirmations
    r"^(?:assolutamente|sicuramente|ovviamente|naturalmente|senz'altro|senza\s+dubbio|come\s+no)$",
    # Colloquial
    r"^(?:s[iì]\s+grazie|s[iì]\s+certo|s[iì]\s+va\s+bene|s[iì]\s+dai|s[iì]\s+perfetto)$",
    r"^(?:dai|andiamo|procediamo|facciamo|avanti|forza)$",
    # Soft confirmations
    r"^(?:mi\s+(?:sta|va)\s+bene|per\s+me\s+(?:va\s+bene|ok|s[iì]))$",
    r"^(?:ci\s+sto|sono\s+d'accordo|va\s+benissimo|mi\s+sembra\s+(?:bene|giusto|perfetto))$",
    # "quello/quella va bene"
    r"(?:quell[oae]|cos[iì])\s+va\s+bene",
    r"\bconferm[oa](?:re)?\b",
]

_CONFERMA_COMPILED = [re.compile(p, re.IGNORECASE) for p in CONFERMA_PATTERNS]


def is_conferma(text: str) -> Tuple[bool, float]:
    """
    Check if text is a confirmation.
    Returns (is_match, confidence).
    """
    text_clean = text.strip()
    for i, pattern in enumerate(_CONFERMA_COMPILED):
        if pattern.search(text_clean):
            # First patterns (exact match) get higher confidence
            confidence = 1.0 if i < 5 else 0.9
            return (True, confidence)
    return (False, 0.0)


# =============================================================================
# 3. REJECTION PATTERNS
# =============================================================================
# Comprehensive Italian negative expressions.

RIFIUTO_PATTERNS = [
    # Direct negations
    r"^(?:no|no\s+no|nono|nient(?:e|'altro)|macch[eé])$",
    # Polite rejections
    r"^(?:no\s+grazie|non\s+mi\s+(?:va|interessa|serve)|preferisco\s+(?:di\s+)?no)$",
    # Stronger rejections
    r"^(?:assolutamente\s+no|per\s+niente|neanche\s+per\s+(?:sogno|idea)|non\s+se\s+ne\s+parla)$",
    # Cancel/stop
    r"^(?:annulla|stop|basta|lascia(?:mo)?\s+(?:stare|perdere)|lascia)$",
    # Soft rejections
    r"^(?:non\s+(?:credo|penso|direi)|forse\s+no|meglio\s+(?:di\s+)?no|direi\s+di\s+no)$",
    # Rethinking
    r"^(?:ci\s+(?:devo\s+)?penso|ci\s+devo\s+pensare|devo\s+pensarci|non\s+(?:ora|adesso|oggi)|magari\s+(?:dopo|un'altra\s+volta))$",
    # Indifference/rejection
    r"^(?:non\s+mi\s+convince|non\s+fa\s+per\s+me|cambiamo|altra\s+proposta)$",
    # "non voglio" patterns
    r"\bnon\s+(?:voglio|desidero|intendo)\b",
    r"\bho\s+cambiato\s+idea\b",
]

_RIFIUTO_COMPILED = [re.compile(p, re.IGNORECASE) for p in RIFIUTO_PATTERNS]


def is_rifiuto(text: str) -> Tuple[bool, float]:
    """
    Check if text is a rejection.
    Returns (is_match, confidence).
    """
    text_clean = text.strip()
    for i, pattern in enumerate(_RIFIUTO_COMPILED):
        if pattern.search(text_clean):
            confidence = 1.0 if i < 4 else 0.85
            return (True, confidence)
    return (False, 0.0)


# =============================================================================
# 4. ESCALATION PATTERNS (Operator / Human Request)
# =============================================================================
# Triggers WhatsApp CALL to business owner when matched.
# Comprehensive coverage of all Italian variants for requesting a human.

ESCALATION_PATTERNS = [
    # === OPERATOR (indices 0-2) ===
    r"\b(?:operatore|operatrice)\b",
    r"\bpersona\s+(?:vera|reale|umana|in\s+carne\s+e\s+ossa)\b",
    r"\b(?:umano|essere\s+umano)\b",
    # === FRUSTRATION (indices 3-6) - check BEFORE role to catch "non voglio parlare con robot" ===
    r"non\s+(?:sei|è)\s+un[ao']?\s*(?:persona|umano|essere\s+umano)",
    r"sei\s+(?:un\s+)?(?:robot|bot|macchina|computer|intelligenza\s+artificiale)",
    r"non\s+(?:voglio|parlo|intendo)\s+(?:parlar[e]?\s+)?con\s+(?:un\s+)?(?:robot|bot|macchina|computer)",
    r"basta\s+(?:con\s+)?(?:sto|questo|il|'sto)?\s*(?:robot|bot|macchina)",
    # === ROLE (indices 7-13) ===
    r"(?:voglio|vorrei|posso|devo|mi\s+faccia)\s+parlar[e]?\s+con\s+(?:un|una|l[ao']?|il|qualcuno)",
    r"(?:mi\s+)?(?:pass[ai]|mett[ai]|connett[ai]|trasferis[ca]i?)\s+(?:un|una|l[ao']?|il|la)?\s*(?:operatore|operatrice|persona|qualcuno|responsabile|titolare|proprietari[oa]|direttore|direttrice|capo)",
    r"(?:voglio|vorrei|posso|devo|mi\s+faccia)\s+parlar[e]?\s+con\s+(?:il|la|l[ao']?)?\s*(?:titolare|proprietari[oa]|responsabile|direttore|direttrice|gestore|gestrice|patron[e]?|capo|capessa|receptionist|segretari[oa]|addett[oa])",
    r"(?:parlo|parlare)\s+(?:con|col|coll[ao]?)\s+(?:il|la|un|una)?\s*(?:titolare|proprietari[oa]|responsabile|direttore|direttrice|gestore|gestrice|patron[e]?|capo)",
    r"mi\s+(?:faccia|fa|fai)\s+parlare\s+con\s+qualcuno",
    r"c['\u2019]è\s+qualcuno\s+(?:con\s+cui|di)\s+(?:parlare|umano)",
    r"passa(?:mi|re|te(?:mi)?|gli|le)?\s+(?:un|una|qualcuno|il\s+capo|il\s+titolare|la\s+titolare|il\s+proprietario|la\s+proprietaria|il\s+direttore|la\s+direttrice|il\s+responsabile|la\s+responsabile|il\s+gestore|la\s+gestrice)",
    # === CALLBACK (indices 14+) ===
    r"\b(?:chiamate(?:mi)?|richiamate(?:mi)?|fatemi\s+(?:richiamare|chiamare))\b",
    r"\b(?:voglio\s+(?:essere\s+)?(?:richiamato|chiamato|contattato))\b",
    r"\b(?:mi\s+(?:richiami|chiami|contatti)\s+(?:il|la|un)?\s*(?:titolare|responsabile|qualcuno)?)\b",
]

_ESCALATION_COMPILED = [re.compile(p, re.IGNORECASE) for p in ESCALATION_PATTERNS]


def is_escalation(text: str) -> Tuple[bool, float, str]:
    """
    Check if text is an escalation request.
    Returns (is_match, confidence, escalation_type).
    escalation_type: 'operator', 'role', 'frustration', 'callback'
    """
    text_clean = text.strip().lower()

    for i, pattern in enumerate(_ESCALATION_COMPILED):
        if pattern.search(text_clean):
            # Determine type based on pattern index
            # 0-2: operator, 3-6: frustration, 7-13: role, 14+: callback
            if i <= 2:
                esc_type = "operator"
            elif i <= 6:
                esc_type = "frustration"
            elif i <= 13:
                esc_type = "role"
            else:
                esc_type = "callback"
            confidence = 0.95 if i <= 2 or (7 <= i <= 13) else 0.9
            return (True, confidence, esc_type)
    return (False, 0.0, "")


# =============================================================================
# 5. SERVICE PATTERNS BY VERTICAL
# =============================================================================
# Service synonyms for each vertical.

VERTICAL_SERVICES: Dict[str, Dict[str, List[str]]] = {
    "salone": {
        "taglio": ["taglio", "sforbiciata", "spuntatina", "accorciare", "accorciatina", "taglietto",
                   "capelli", "fare i capelli", "taglio capelli", "sistemare i capelli"],
        "taglio_uomo": ["taglio uomo", "taglio maschile", "rasatura"],
        "taglio_bambino": ["taglio bambino", "taglio bimbo", "taglio bimba"],
        "piega": ["piega", "messa in piega", "asciugatura", "styling", "acconciatura"],
        "colore": ["colore", "tinta", "colorazione", "ritocco radici", "copertura bianchi"],
        "meches": ["meches", "mechès", "colpi di sole"],
        "balayage": ["balayage", "degradé", "shatush", "ombré"],
        "trattamento": ["trattamento", "ricostruzione", "cheratina", "botox capelli", "trattamento ristrutturante"],
        "permanente": ["permanente", "ondulazione"],
        "stiratura": ["stiratura", "lisciatura", "stiratura brasiliana", "keratina lisciante"],
        "extension": ["extension", "allungamento"],
        "barba": ["barba", "rifinitura barba", "rasatura barba", "regolazione barba", "barberia"],
        "manicure": ["manicure", "unghie mani", "smalto mani", "nail art", "semipermanente mani", "ricostruzione unghie"],
        "pedicure": ["pedicure", "unghie piedi", "smalto piedi", "semipermanente piedi"],
        "ceretta": ["ceretta", "depilazione", "epilazione", "ceretta gambe", "ceretta braccia", "ceretta inguine"],
        "trucco": ["trucco", "makeup", "trucco sposa", "trucco cerimonia", "make-up"],
        "acconciatura_sposa": ["acconciatura sposa", "pacchetto sposa", "prova trucco sposa"],
    },
    "palestra": {
        "abbonamento": ["abbonamento", "iscrizione", "tessera", "rinnovo"],
        "personal_training": ["personal training", "personal trainer", "pt", "allenamento personalizzato", "sessione individuale"],
        "corso_gruppo": ["corso", "lezione", "classe", "lezione di gruppo"],
        "yoga": ["yoga", "hatha yoga", "vinyasa", "ashtanga", "power yoga"],
        "pilates": ["pilates", "pilates matwork", "pilates reformer"],
        "spinning": ["spinning", "indoor cycling", "ciclismo indoor"],
        "crossfit": ["crossfit", "cross training", "functional training", "allenamento funzionale"],
        "nuoto": ["nuoto", "piscina", "acquagym", "acqua fitness", "idrobike"],
        "boxe": ["boxe", "pugilato", "kick boxing", "kickboxing", "fit boxe"],
        "danza": ["danza", "ballo", "zumba", "hip hop", "danza moderna", "danza classica"],
        "sala_pesi": ["sala pesi", "body building", "bodybuilding", "pesi liberi", "pesistica"],
        "massaggio": ["massaggio", "massaggio sportivo", "massaggio decontratturante"],
        "sauna": ["sauna", "bagno turco", "spa", "area relax", "idromassaggio"],
    },
    "medical": {
        "visita": ["visita", "visita medica", "consulto", "consulenza", "appuntamento medico"],
        "controllo": ["controllo", "check-up", "check up", "screening", "follow-up", "follow up"],
        "esame": ["esame", "analisi", "prelievo", "esame del sangue", "radiografia", "ecografia", "risonanza"],
        "vaccinazione": ["vaccinazione", "vaccino", "richiamo", "dose"],
        "terapia": ["terapia", "seduta", "trattamento", "fisioterapia", "riabilitazione"],
        "odontoiatria": ["dentista", "pulizia denti", "otturazione", "estrazione", "devitalizzazione", "impianto"],
        "oculistica": ["oculista", "visita oculistica", "controllo vista", "esame vista"],
        "dermatologia": ["dermatologo", "visita dermatologica", "controllo nei", "mappatura nei"],
        "cardiologia": ["cardiologo", "elettrocardiogramma", "ecg", "ecocardiogramma", "holter"],
        "ortopedia": ["ortopedico", "visita ortopedica", "radiografia"],
        "ginecologia": ["ginecologo", "visita ginecologica", "pap test", "ecografia"],
        "pediatria": ["pediatra", "visita pediatrica", "bilancio di salute"],
        "certificato": ["certificato", "certificato medico", "certificato sportivo", "idoneità"],
    },
    "auto": {
        "tagliando": ["tagliando", "revisione", "manutenzione ordinaria", "service"],
        "riparazione": ["riparazione", "guasto", "problema", "non funziona", "si è rotto"],
        "cambio_olio": ["cambio olio", "olio motore", "filtro olio"],
        "freni": ["freni", "pastiglie", "dischi freno", "liquido freni"],
        "gomme": ["gomme", "pneumatici", "cambio gomme", "cambio stagionale", "convergenza", "equilibratura", "bilanciatura"],
        "batteria": ["batteria", "avviamento", "non parte", "non si avvia"],
        "ac": ["aria condizionata", "climatizzatore", "ac", "ricarica ac", "condizionatore"],
        "carrozzeria": ["carrozzeria", "ammaccatura", "verniciatura", "riverniciatura", "botta", "graffio", "rigatura"],
        "elettronica": ["elettronica", "centralina", "sensore", "spia", "diagnostica"],
        "frizione": ["frizione", "cambio", "cambio marce", "trasmissione"],
        "sospensioni": ["sospensioni", "ammortizzatori", "assetto"],
        "scarico": ["scarico", "marmitta", "catalizzatore", "fap", "dpf"],
        "revisione": ["revisione", "revisione auto", "collaudo", "bollino blu"],
    },
}


def get_service_synonyms(vertical: str) -> Dict[str, List[str]]:
    """Get service synonyms for a vertical."""
    return VERTICAL_SERVICES.get(vertical, {})


# =============================================================================
# 6. MULTI-SERVICE DETECTION
# =============================================================================
# Detects compound service requests: "taglio e barba", "taglio, barba e colore"

# Connectors between services
_SERVICE_CONNECTORS = r"(?:\s+e\s+|\s*,\s*(?:e\s+)?|\s+(?:con|più|anche|poi(?:\s+anche)?)\s+)"

# Build multi-service patterns dynamically per vertical
def extract_multi_services(text: str, vertical: str = "salone") -> List[str]:
    """
    Extract multiple services from text.
    Handles pairs AND triples: "taglio e barba", "taglio, barba e colore".

    Returns list of matched service IDs.
    """
    services = VERTICAL_SERVICES.get(vertical, {})
    text_lower = text.lower()
    found = []
    found_ids = set()

    # Phase 1: Check each service synonym against text
    for service_id, synonyms in services.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower and service_id not in found_ids:
                found.append(service_id)
                found_ids.add(service_id)
                break

    return found


# Patterns for detecting multi-service intent (without knowing specific services)
MULTI_SERVICE_PATTERNS = [
    # "X e Y" pattern (pair)
    r"\b\w+\s+e\s+\w+\b",
    # "X, Y e Z" pattern (triple)
    r"\b\w+\s*,\s*\w+\s+e\s+\w+\b",
    # "X più Y" / "X con Y"
    r"\b\w+\s+(?:più|con|anche)\s+\w+\b",
    # "anche X" / "aggiungi X"
    r"(?:anche|aggiungi|aggiungere|includi|includere|metti|mettere)\s+(?:un[ao']?\s+)?",
    # "vorrei anche" / "facciamo anche"
    r"(?:vorrei|facciamo|aggiungiamo|mettiamo|includiamo)\s+anche\s+",
]

_MULTI_SERVICE_COMPILED = [re.compile(p, re.IGNORECASE) for p in MULTI_SERVICE_PATTERNS]


def has_multi_service_intent(text: str) -> bool:
    """Check if text contains multi-service intent markers."""
    for pattern in _MULTI_SERVICE_COMPILED:
        if pattern.search(text):
            return True
    return False


# =============================================================================
# 7. INAPPROPRIATE CONTENT FILTER
# =============================================================================
# Three severity levels:
#   Level 1 (MILD): Mild language, tolerated with soft redirect
#   Level 2 (MODERATE): Vulgar language, firm redirect
#   Level 3 (SEVERE): Offensive content, immediate session termination

class ContentSeverity(Enum):
    CLEAN = "clean"
    MILD = "mild"          # Level 1: redirectable
    MODERATE = "moderate"  # Level 2: firm redirect
    SEVERE = "severe"      # Level 3: terminate


@dataclass
class ContentFilterResult:
    severity: ContentSeverity
    matched_pattern: str = ""
    suggested_response: str = ""


# Level 1: Mild expressions (frustration, mild swearing)
_MILD_PATTERNS = [
    r"\b(?:cavolo|accidenti|mannaggia|accipicchia|porca\s+miseria|cribbio)\b",
    r"\b(?:che\s+(?:palle|schifo|noia|barba|rottura)|ma\s+dai|ma\s+va)\b",
    r"\b(?:uff+a?|argh|grr+|pfff+)\b",
    r"\b(?:caspita|capperi|osteria|ostia|madonna)\b",
    r"\b(?:diamine|diavoleria|maledizione|maledetto)\b",
    r"\b(?:cacchio|caspiterina)\b",
]

# Level 2: Vulgar (explicit but not hate speech)
_MODERATE_PATTERNS = [
    r"\b(?:cazzo|minchia|merda|stronz[oai]|vaffanculo|fottere|fottiti|fott[ie])\b",
    r"\b(?:coglion[ei]|cretino|deficiente|idiota|imbecille|stupido)\b",
    r"\b(?:culo|fica|testa\s+di\s+cazzo|pezzo\s+di\s+merda)\b",
    r"\b(?:fanculo|vaffanculo|affanculo|col\s+cazzo)\b",
    r"\b(?:cazzo|caz+o|minch+ia|merd+a)\b",  # With elongated letters
    r"\b(?:str\.?onz|ca\.?zz|min\.?chi)\w*\b",  # Censored attempts
]

# Level 3: Severe (hate speech, threats, blasphemy)
_SEVERE_PATTERNS = [
    # Threats
    r"\b(?:ti\s+(?:ammazzo|uccido|sparo|accoltello|meno|picchio|sgozzo))\b",
    r"\b(?:vi\s+(?:ammazzo|uccido|sparo|faccio\s+(?:fuori|saltare)))\b",
    r"\b(?:ammazzat[ei]|crepa|muori|va['\u2019]\s+a?\s+morire)\b",
    # Hate speech / discrimination
    r"\b(?:neg[hr]o|terron[ei]|froci[oa]?|finocc?hi[oa]?|ricchi[oa]n[ei]?)\b",
    r"\b(?:put+ana|troia|zoccola|bagascia|mignotta)\b",
    r"\b(?:handicappat[oa]|mongol(?:oide)?|ritardat[oa])\b",
    # Italian blasphemy (bestemmie)
    r"\b(?:porco\s+(?:dio|d[i1]o|gesù|cristo|madonna|giuda))\b",
    r"\b(?:dio\s+(?:cane|porco|maiale|bestia|ladro|boia|santo|merda|can[e]?))\b",
    r"\b(?:madonna\s+(?:puttana|troia|zoccola|maiala|boia|ladra))\b",
    r"\b(?:cristo\s+(?:santo|porco|cane|di\s+un\s+dio))\b",
    r"\b(?:ges[uù]\s+(?:cristo|bambino)\s+(?:in\s+bicicletta|ladro))\b",
    r"\b(?:ostia|sacramento)\s+(?:maledett[oa])\b",
    # Sexual harassment
    r"\b(?:sei\s+(?:sexy|gnocca|bona|figa))\b",
    r"\b(?:che\s+(?:tette|culo|figa)|voglio\s+(?:scopar|trombar))\b",
    r"\btett[ea]\b",  # Any mention of "tette/tetta"
    r"\b(?:culo|cul[oi]ne|sedere)\s+(?:grande|grandi|gross[oa]|enorm[ei])\b",
    r"\b(?:gnocc[oa]|bon[oa]|fig[oa]|zoccol[oa])\b",
    r"\b(?:collaboratrice|ragazza|donna|signora)\s+.*\b(?:tett[ea]|culo|seno|figa|bell[oa]|gnocc[oa]|bon[oa])\b",
    r"\b(?:appoggi(?:are|o)\s+la\s+testa|massagg(?:io|i|are))\s+.*\b(?:tett[ea]|seno)\b",
    r"\b(?:scopare?|trombare?|pompa|pompino|sesso)\b",
]

_MILD_COMPILED = [re.compile(p, re.IGNORECASE) for p in _MILD_PATTERNS]
_MODERATE_COMPILED = [re.compile(p, re.IGNORECASE) for p in _MODERATE_PATTERNS]
_SEVERE_COMPILED = [re.compile(p, re.IGNORECASE) for p in _SEVERE_PATTERNS]

# Response templates per severity level
_CONTENT_RESPONSES = {
    ContentSeverity.MILD: "Capisco la frustrazione. Posso aiutarla in qualche modo?",
    ContentSeverity.MODERATE: "La prego di mantenere un linguaggio appropriato. Come posso aiutarla?",
    ContentSeverity.SEVERE: "Mi dispiace, non posso continuare con questo tipo di linguaggio. La conversazione verrà terminata.",
}


def check_content(text: str) -> ContentFilterResult:
    """
    Check text for inappropriate content.
    Returns ContentFilterResult with severity level and suggested response.

    Checks from most severe to least severe (short-circuit on first match).
    """
    text_clean = text.strip()

    # Check severe first
    for pattern in _SEVERE_COMPILED:
        m = pattern.search(text_clean)
        if m:
            return ContentFilterResult(
                severity=ContentSeverity.SEVERE,
                matched_pattern=m.group(0),
                suggested_response=_CONTENT_RESPONSES[ContentSeverity.SEVERE]
            )

    # Check moderate
    for pattern in _MODERATE_COMPILED:
        m = pattern.search(text_clean)
        if m:
            return ContentFilterResult(
                severity=ContentSeverity.MODERATE,
                matched_pattern=m.group(0),
                suggested_response=_CONTENT_RESPONSES[ContentSeverity.MODERATE]
            )

    # Check mild
    for pattern in _MILD_COMPILED:
        m = pattern.search(text_clean)
        if m:
            return ContentFilterResult(
                severity=ContentSeverity.MILD,
                matched_pattern=m.group(0),
                suggested_response=_CONTENT_RESPONSES[ContentSeverity.MILD]
            )

    return ContentFilterResult(severity=ContentSeverity.CLEAN)


# =============================================================================
# 8. OBJECTIONS / CORRECTIONS / FLOW CONTROL
# =============================================================================
# Patterns for mid-conversation corrections and objections.

class CorrectionType(Enum):
    CHANGE_SERVICE = "change_service"
    CHANGE_DATE = "change_date"
    CHANGE_TIME = "change_time"
    CHANGE_OPERATOR = "change_operator"
    GENERIC_CHANGE = "generic_change"
    MISUNDERSTANDING = "misunderstanding"
    WAIT = "wait"
    REPEAT = "repeat"
    SLOWER = "slower"


CORRECTION_PATTERNS: Dict[CorrectionType, List[str]] = {
    # NOTE: CHANGE_DATE and CHANGE_TIME must come BEFORE CHANGE_SERVICE
    # because CHANGE_SERVICE has broad \w+ that would match day names and times
    CorrectionType.CHANGE_DATE: [
        r"(?:no|anzi|veramente|in\s+realtà)[,;]?\s*(?:meglio|preferisco|facciamo)\s+(?:domani|lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica|dopodomani|oggi|la\s+prossima|un\s+altro\s+giorno)",
        r"(?:cambi(?:amo|are)?|spost(?:iamo|are)?)\s+(?:la\s+)?data",
        r"(?:un\s+altro|altra)\s+(?:giorno|data)",
    ],
    CorrectionType.CHANGE_TIME: [
        r"(?:no|anzi|veramente|in\s+realtà)[,;]?\s*(?:meglio|preferisco|facciamo)\s+(?:alle|ore|le)\s+\d{1,2}",
        r"(?:cambi(?:amo|are)?|spost(?:iamo|are)?)\s+(?:l[''\u2019]?\s*)?or(?:a|ario)",
        r"(?:un\s+altro|altra?)\s+(?:ora|orario)",
        r"(?:più\s+)?(?:presto|tardi)\s*(?:se\s+possibile)?",
    ],
    CorrectionType.CHANGE_SERVICE: [
        r"(?:no|anzi|veramente|in\s+realtà),?\s*(?:vorrei|preferisco|meglio|facciamo)\s+(?:un|una|il|la)?\s*\w+",
        r"(?:cambi(?:amo|are)?|modific(?:hiamo|are)?)\s+(?:il\s+)?servizio",
        r"(?:non|niente)\s+\w+,?\s*(?:facciamo|meglio|preferisco|vorrei)\s+\w+",
        r"(?:al\s+posto\s+(?:di|del)|invece\s+(?:di|del))\s+\w+",
    ],
    CorrectionType.CHANGE_OPERATOR: [
        r"(?:no|anzi|veramente|in\s+realtà),?\s*(?:vorrei|preferisco|meglio)\s+(?:con)?\s+[A-Z]\w+",
        r"(?:cambi(?:amo|are)?)\s+(?:l['']?\s*)?operator[ei]",
        r"(?:un\s+altro|altra?)\s+operator[ei]",
    ],
    CorrectionType.MISUNDERSTANDING: [
        r"(?:no\s+)?(?:non\s+)?(?:ho|hai|ha|hanno)\s+(?:capito\s+male|frainteso)",
        r"non\s+(?:è|era)\s+(?:quello|quella|questo|questa)\s+che\s+(?:intendevo|volevo|ho\s+detto)",
        r"non\s+era\s+quello\s+che\s+intendevo",
        r"mi\s+(?:hai?|ha)\s+(?:capito|inteso)\s+male",
        r"no\s+no[,;]?\s+(?:io|intendevo|volevo\s+dire)",
    ],
    CorrectionType.GENERIC_CHANGE: [
        r"(?:aspett[ia]|ferm[ia]|un\s+momento|un\s+attimo)[,;]?\s*(?:ho\s+sbagliato|volevo\s+dire|intendevo)",
        r"(?:mi\s+sono\s+sbagliat[oa]|ho\s+detto\s+male)",
        r"(?:torniamo\s+indietro|ricominciamo|da\s+capo)",
    ],
    CorrectionType.WAIT: [
        r"(?:aspett[iae]|un\s+(?:attimo|momento|secondo|minuto))",
        r"(?:ferma|fermati|stop|pausa)",
        r"(?:mi\s+dia|dammi)\s+(?:un\s+)?(?:attimo|momento|secondo)",
    ],
    CorrectionType.REPEAT: [
        r"(?:(?:puoi|può|puòi)\s+)?ripet(?:ere|i)\b",
        r"(?:non\s+ho\s+(?:capito|sentito)|come\s+(?:ha\s+detto|hai\s+detto|scusi))\b",
        r"(?:scus[ia],?\s+)?(?:cosa\s+(?:ha|hai)\s+detto|(?:ripeta|ridica|ridimmi))",
    ],
    CorrectionType.SLOWER: [
        r"(?:(?:più|un\s+po['']?)\s+)?(?:piano|lentamente|adagio)\b",
        r"(?:parla|parli)\s+(?:più\s+)?(?:piano|lentamente)\b",
        r"(?:rallent[ia]|non\s+(?:vada|andare)\s+(?:così\s+)?(?:veloce|forte))",
    ],
}

_CORRECTION_COMPILED: Dict[CorrectionType, List[re.Pattern]] = {
    ct: [re.compile(p, re.IGNORECASE) for p in patterns]
    for ct, patterns in CORRECTION_PATTERNS.items()
}


def detect_correction(text: str) -> Optional[Tuple[CorrectionType, float]]:
    """
    Detect if user is making a correction or objection.
    Returns (CorrectionType, confidence) or None.
    """
    text_clean = text.strip()

    for correction_type, patterns in _CORRECTION_COMPILED.items():
        for pattern in patterns:
            if pattern.search(text_clean):
                confidence = 0.9
                return (correction_type, confidence)

    return None


# =============================================================================
# 9. RELATIVE DATE DISAMBIGUATION
# =============================================================================
# "prossima settimana" should ask which day, not auto-pick Monday.

AMBIGUOUS_DATE_PATTERNS = [
    r"\b(?:prossima|questa)\s+settimana\b",
    r"\bsettimana\s+(?:prossima|scorsa|corrente)\b",
    r"\b(?:il\s+prossimo|la\s+prossima)\s+(?:mese|fine\s+settimana|weekend)\b",
    r"\b(?:fra|tra)\s+(?:poco|qualche\s+giorno|un\s+po['']?)\b",
    r"\b(?:fra|tra)\s+(?:due|tre|2|3)\s+settiman[ae]\b",
    r"\b(?:uno\s+di\s+questi\s+giorni|appena\s+possibile|prima\s+possibile)\b",
]

_AMBIGUOUS_DATE_COMPILED = [re.compile(p, re.IGNORECASE) for p in AMBIGUOUS_DATE_PATTERNS]


def is_ambiguous_date(text: str) -> bool:
    """Check if text contains an ambiguous date that needs clarification."""
    for pattern in _AMBIGUOUS_DATE_COMPILED:
        if pattern.search(text):
            return True
    return False


# =============================================================================
# COMBINED REGEX PRE-FILTER
# =============================================================================
# Quick function to run all L0 checks in one pass.

@dataclass
class RegexPreFilterResult:
    """Result from the combined L0 regex pre-filter."""
    # Text with fillers stripped
    cleaned_text: str
    # Content filter
    content_severity: ContentSeverity = ContentSeverity.CLEAN
    content_response: str = ""
    # Escalation
    is_escalation: bool = False
    escalation_type: str = ""
    escalation_confidence: float = 0.0
    # Correction
    correction_type: Optional[CorrectionType] = None
    correction_confidence: float = 0.0
    # Ambiguous date
    has_ambiguous_date: bool = False
    # Multi-service
    has_multi_service: bool = False


def prefilter(text: str) -> RegexPreFilterResult:
    """
    Run all L0 regex checks in one pass.
    This should be called FIRST in the orchestrator pipeline.
    """
    result = RegexPreFilterResult(cleaned_text=text)

    # 1. Content filter (check FIRST - may terminate session)
    content = check_content(text)
    result.content_severity = content.severity
    if content.severity != ContentSeverity.CLEAN:
        result.content_response = content.suggested_response
        # For severe content, don't process further
        if content.severity == ContentSeverity.SEVERE:
            return result

    # 2. Strip fillers
    result.cleaned_text = strip_fillers(text)

    # 3. Escalation check
    is_esc, esc_conf, esc_type = is_escalation(text)
    result.is_escalation = is_esc
    result.escalation_type = esc_type
    result.escalation_confidence = esc_conf

    # 4. Correction detection
    correction = detect_correction(text)
    if correction:
        result.correction_type = correction[0]
        result.correction_confidence = correction[1]

    # 5. Ambiguous date
    result.has_ambiguous_date = is_ambiguous_date(text)

    # 6. Multi-service intent
    result.has_multi_service = has_multi_service_intent(text)

    return result
