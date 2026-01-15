"""
FLUXION Voice Agent - Italian NLU Pipeline

4-Layer Architecture:
├── Layer 1: Implicit Intent Detection (Regex)     ~1ms
├── Layer 2: spaCy NER + Entity Extraction        ~20ms
├── Layer 3: UmBERTo Intent Classification        ~80ms
└── Layer 4: Context Management + Validation      ~5ms

Total: ~100-120ms

Resolves critical problems:
1. "Io non sono mai stato da voi" → NEW_CLIENT (not "Mai" as name)
2. "È la prima volta che vengo" → NEW_CLIENT auto-registration
3. "Vorrei prenotare per mia madre Maria" → Maria is client, not caller
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Lazy imports for optional heavy dependencies
_spacy = None
_nlp_model = None
_intent_classifier = None
_sbert_model = None

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class NLUIntent(str, Enum):
    """Supported intents for booking voice agent."""
    NUOVO_CLIENTE = "nuovo_cliente"
    PRENOTAZIONE = "prenotazione"
    CANCELLAZIONE = "cancellazione"
    MODIFICA = "modifica"
    INFO_ORARI = "info_orari"
    INFO_PREZZI = "info_prezzi"
    CONFERMA = "conferma"
    RIFIUTO = "rifiuto"
    CORREZIONE = "correzione"
    RICHIESTA_OPERATORE = "richiesta_operatore"
    SALUTO = "saluto"
    SCONOSCIUTO = "sconosciuto"


@dataclass
class NLUEntity:
    """Extracted entity."""
    text: str
    label: str  # PERSON, DATE, GPE, etc.
    start: int
    end: int
    confidence: float = 0.9


@dataclass
class NLUResult:
    """Complete NLU processing result."""
    text: str
    intent: NLUIntent
    confidence: float
    layer: str  # Which layer produced the result
    entities: List[NLUEntity] = field(default_factory=list)
    slots: Dict[str, Any] = field(default_factory=dict)
    clarification: Optional[Dict] = None
    is_new_client: bool = False

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "intent": self.intent.value,
            "confidence": self.confidence,
            "layer": self.layer,
            "entities": [{"text": e.text, "label": e.label} for e in self.entities],
            "slots": self.slots,
            "is_new_client": self.is_new_client,
            "clarification": self.clarification,
        }


# =============================================================================
# LAYER 1: IMPLICIT INTENT DETECTION (REGEX)
# =============================================================================

# Patterns for implicit intents (Italian idioms)
IMPLICIT_PATTERNS = {
    NLUIntent.NUOVO_CLIENTE: [
        r"non\s+(sono\s+)?mai\s+(stato|venuto|venuta)",
        r"(è\s+)?la\s+prima\s+(volta|visita)",
        r"non\s+(vi\s+)?conosco",
        r"non\s+sono\s+cliente",
        r"primo\s+appuntamento",
        r"prima\s+visita",
        r"non\s+sono\s+.*\s+cliente",
        r"mai\s+stato\s+da\s+voi",
        r"mai\s+venuto\s+da\s+voi",
    ],
    NLUIntent.CONFERMA: [
        r"^\s*(sì|si|okay|ok|va\s+bene|d'accordo|perfetto|esatto|certo|certamente)\s*[.!]?\s*$",
        r"^\s*(sì|si)[,\s]+(confermo|conferma|esatto|va\s+bene)",
        r"^(confermo|conferma|confermato)\s*[.!]?\s*$",
    ],
    NLUIntent.RIFIUTO: [
        r"^\s*(no|non|non\s+voglio|annulla|lascia\s+stare|cancella)\s*[.!]?\s*$",
        r"^\s*(no)[,\s]+(annulla|cancella|lascia|non\s+voglio)",
        r"^(annulla|annullato|cancella|cancellato)\s*[.!]?\s*$",
    ],
    NLUIntent.CORREZIONE: [
        r"no\s+aspetta",
        r"volevo\s+dire",
        r"\banzi\b",
        r"mi\s+sono\s+sbagliato",
        r"scusa.*volevo",
        r"no\s+meglio",
    ],
    NLUIntent.SALUTO: [
        r"^(buongiorno|buonasera|arrivederci|ciao|grazie|a\s+presto|salve)",
    ],
    NLUIntent.RICHIESTA_OPERATORE: [
        r"parl(are|o)\s+con\s+un\s+operatore",
        r"operatore\s+umano",
        r"persona\s+reale",
        r"vorrei\s+parlare\s+con\s+qualcuno",
    ],
}

# Blacklist for name extraction
NAME_BLACKLIST = {
    # Italian adverbs/expressions that look like names
    "mai", "sempre", "spesso", "forse", "quasi", "molto", "poco",
    # Past participles
    "stato", "venuto", "venuta", "andato", "andata", "fatto", "detto", "visto",
    # Common expressions
    "volta", "cliente", "nuovo", "nuova", "prima", "primo",
    # Other
    "aspetta", "volevo", "anzi", "scusa", "prego",
}


def _detect_implicit_intent(text: str) -> Optional[NLUResult]:
    """
    Layer 1: Regex pattern matching for implicit intents.
    Latency: <1ms
    Coverage: ~40% of typical booking utterances
    """
    text_lower = text.lower().strip()

    for intent, patterns in IMPLICIT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return NLUResult(
                    text=text,
                    intent=intent,
                    confidence=0.95,
                    layer="L1_regex",
                    is_new_client=(intent == NLUIntent.NUOVO_CLIENTE),
                )

    return None


# =============================================================================
# LAYER 2: spaCy NER + ENTITY EXTRACTION
# =============================================================================

def _load_spacy():
    """Lazy load spaCy model."""
    global _spacy, _nlp_model

    if _nlp_model is not None:
        return _nlp_model

    try:
        import spacy
        _spacy = spacy

        # Try large model first, fallback to small
        try:
            _nlp_model = spacy.load("it_core_news_lg")
            logger.info("Loaded spaCy it_core_news_lg (43MB)")
        except OSError:
            try:
                _nlp_model = spacy.load("it_core_news_sm")
                logger.info("Loaded spaCy it_core_news_sm (13MB)")
            except OSError:
                logger.warning("No Italian spaCy model found. Run: python -m spacy download it_core_news_lg")
                return None

        return _nlp_model

    except ImportError:
        logger.warning("spaCy not installed. Run: pip install spacy")
        return None


def _extract_entities_spacy(text: str) -> List[NLUEntity]:
    """
    Layer 2: Extract entities using spaCy NER.
    Latency: ~20ms
    Entities: PERSON, DATE, GPE, ORG
    """
    nlp = _load_spacy()
    if nlp is None:
        return []

    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        # Filter blacklisted words
        if ent.text.lower() in NAME_BLACKLIST:
            logger.debug(f"Filtered blacklisted entity: {ent.text}")
            continue

        entities.append(NLUEntity(
            text=ent.text,
            label=ent.label_,
            start=ent.start_char,
            end=ent.end_char,
            confidence=0.90,
        ))

    return entities


def _fill_slots(text: str, entities: List[NLUEntity]) -> Dict[str, Any]:
    """Fill slots from extracted entities."""
    slots = {}

    # PERSON → cliente_nome
    person_ents = [e for e in entities if e.label == "PERSON"]
    if person_ents:
        nome = person_ents[0].text

        # Check for third-party booking: "per mia madre Maria"
        if _is_third_party(text, nome):
            slots["cliente_nome"] = nome
            slots["cliente_tipo"] = "terza_persona"
        else:
            slots["cliente_nome"] = nome
            slots["cliente_tipo"] = "primo_contatto"

    # DATE → data
    date_ents = [e for e in entities if e.label == "DATE"]
    if date_ents:
        slots["data_raw"] = date_ents[0].text

    return slots


def _is_third_party(text: str, name: str) -> bool:
    """Detect if name refers to third person (not caller)."""
    pattern = rf"per\s+(mio|mia|miei|mie|suo|sua|suoi|sue)\s+\w*\s*{re.escape(name)}"
    return bool(re.search(pattern, text.lower(), re.IGNORECASE))


# =============================================================================
# LAYER 3: UmBERTo INTENT CLASSIFICATION
# =============================================================================

def _load_intent_classifier():
    """Lazy load UmBERTo zero-shot classifier."""
    global _intent_classifier

    if _intent_classifier is not None:
        return _intent_classifier

    try:
        from transformers import pipeline
        import torch

        device = 0 if torch.cuda.is_available() else -1

        _intent_classifier = pipeline(
            "zero-shot-classification",
            model="Musixmatch/umberto-commoncrawl-cased-v1",
            device=device,
        )
        logger.info(f"Loaded UmBERTo intent classifier (device={device})")
        return _intent_classifier

    except ImportError:
        logger.warning("transformers not installed. Run: pip install transformers torch")
        return None
    except Exception as e:
        logger.error(f"Failed to load UmBERTo: {e}")
        return None


# Intent labels for zero-shot classification
INTENT_LABELS = [
    "nuovo cliente",
    "prenotazione appuntamento",
    "cancellazione appuntamento",
    "modifica appuntamento",
    "informazioni orari",
    "informazioni prezzi",
    "conferma",
    "rifiuto",
    "correzione",
    "richiesta operatore",
    "saluto",
]

# Map classifier labels to NLUIntent
LABEL_TO_INTENT = {
    "nuovo cliente": NLUIntent.NUOVO_CLIENTE,
    "prenotazione appuntamento": NLUIntent.PRENOTAZIONE,
    "cancellazione appuntamento": NLUIntent.CANCELLAZIONE,
    "modifica appuntamento": NLUIntent.MODIFICA,
    "informazioni orari": NLUIntent.INFO_ORARI,
    "informazioni prezzi": NLUIntent.INFO_PREZZI,
    "conferma": NLUIntent.CONFERMA,
    "rifiuto": NLUIntent.RIFIUTO,
    "correzione": NLUIntent.CORREZIONE,
    "richiesta operatore": NLUIntent.RICHIESTA_OPERATORE,
    "saluto": NLUIntent.SALUTO,
}


def _classify_intent_umberto(text: str) -> Optional[tuple]:
    """
    Layer 3: Zero-shot intent classification with UmBERTo.
    Latency: ~80ms (CPU), ~30ms (GPU)
    """
    classifier = _load_intent_classifier()
    if classifier is None:
        return None

    try:
        result = classifier(
            text,
            INTENT_LABELS,
            multi_label=False,
        )

        top_label = result["labels"][0]
        top_score = float(result["scores"][0])

        intent = LABEL_TO_INTENT.get(top_label, NLUIntent.SCONOSCIUTO)
        return (intent, top_score)

    except Exception as e:
        logger.error(f"UmBERTo classification failed: {e}")
        return None


# =============================================================================
# LAYER 4: CONTEXT MANAGEMENT
# =============================================================================

class ConversationContext:
    """Multi-turn conversation context manager."""

    def __init__(self):
        self.cliente_nome: Optional[str] = None
        self.data: Optional[str] = None
        self.ora: Optional[str] = None
        self.servizio: Optional[str] = None
        self.operatore: Optional[str] = None
        self.nuovo_cliente: bool = False
        self.turno: int = 0
        self.last_intent: Optional[NLUIntent] = None

    def update(self, result: NLUResult) -> None:
        """Update context from NLU result."""
        self.turno += 1
        self.last_intent = result.intent

        if result.is_new_client:
            self.nuovo_cliente = True

        # Update slots
        if "cliente_nome" in result.slots:
            self.cliente_nome = result.slots["cliente_nome"]
        if "data" in result.slots or "data_raw" in result.slots:
            self.data = result.slots.get("data") or result.slots.get("data_raw")
        if "ora" in result.slots:
            self.ora = result.slots["ora"]
        if "servizio" in result.slots:
            self.servizio = result.slots["servizio"]
        if "operatore" in result.slots:
            self.operatore = result.slots["operatore"]

    def to_dict(self) -> Dict:
        return {
            "cliente_nome": self.cliente_nome,
            "data": self.data,
            "ora": self.ora,
            "servizio": self.servizio,
            "operatore": self.operatore,
            "nuovo_cliente": self.nuovo_cliente,
            "turno": self.turno,
        }

    def reset(self) -> None:
        """Reset context for new conversation."""
        self.__init__()


# =============================================================================
# MAIN NLU CLASS
# =============================================================================

class ItalianVoiceAgentNLU:
    """
    4-Layer Italian NLU Pipeline for FLUXION Voice Agent.

    Usage:
        nlu = ItalianVoiceAgentNLU()
        result = nlu.process("Io non sono mai stato da voi")
        print(result.intent)  # NLUIntent.NUOVO_CLIENTE
    """

    def __init__(self, preload_models: bool = False):
        """
        Initialize NLU pipeline.

        Args:
            preload_models: If True, load spaCy and UmBERTo immediately.
                           If False (default), lazy load on first use.
        """
        self.context = ConversationContext()
        self._models_loaded = False

        if preload_models:
            self._preload_models()

    def _preload_models(self) -> None:
        """Preload all ML models (spaCy + UmBERTo)."""
        logger.info("Preloading NLU models...")
        _load_spacy()
        _load_intent_classifier()
        self._models_loaded = True
        logger.info("NLU models loaded.")

    def process(self, text: str, skip_layer3: bool = False) -> NLUResult:
        """
        Process utterance through 4-layer pipeline.

        Args:
            text: Italian text to process
            skip_layer3: If True, skip UmBERTo (faster, less accurate)

        Returns:
            NLUResult with intent, entities, slots
        """
        text = text.strip()
        if not text:
            return NLUResult(
                text=text,
                intent=NLUIntent.SCONOSCIUTO,
                confidence=0.0,
                layer="empty",
            )

        # LAYER 1: Implicit Intent Detection (Regex)
        # Latency: <1ms
        implicit_result = _detect_implicit_intent(text)
        if implicit_result and implicit_result.confidence > 0.85:
            # Also extract entities for context
            entities = _extract_entities_spacy(text)
            implicit_result.entities = entities
            implicit_result.slots = _fill_slots(text, entities)
            self.context.update(implicit_result)
            return implicit_result

        # LAYER 2: spaCy NER + Entity Extraction
        # Latency: ~20ms
        entities = _extract_entities_spacy(text)
        slots = _fill_slots(text, entities)

        # LAYER 3: UmBERTo Intent Classification
        # Latency: ~80ms
        intent = NLUIntent.SCONOSCIUTO
        confidence = 0.5
        layer = "L2_spacy"

        if not skip_layer3:
            umberto_result = _classify_intent_umberto(text)
            if umberto_result:
                intent, confidence = umberto_result
                layer = "L3_umberto"

        # Build result
        result = NLUResult(
            text=text,
            intent=intent,
            confidence=confidence,
            layer=layer,
            entities=entities,
            slots=slots,
            is_new_client=(intent == NLUIntent.NUOVO_CLIENTE),
        )

        # LAYER 4: Context validation
        # Latency: <5ms
        if confidence < 0.7:
            result.clarification = {
                "type": "confirmation",
                "message": f"Ho capito che vuoi {intent.value}. Giusto?",
                "confidence": confidence,
            }

        self.context.update(result)
        return result

    def reset_context(self) -> None:
        """Reset conversation context."""
        self.context.reset()

    def get_context(self) -> Dict:
        """Get current conversation context."""
        return self.context.to_dict()


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("FLUXION Italian NLU Pipeline - Test")
    print("=" * 60)

    nlu = ItalianVoiceAgentNLU(preload_models=False)

    test_cases = [
        # Critical test cases from research
        ("Io non sono mai stato da voi", NLUIntent.NUOVO_CLIENTE),
        ("È la prima volta che vengo", NLUIntent.NUOVO_CLIENTE),
        ("Vorrei prenotare per mia madre Maria", NLUIntent.PRENOTAZIONE),

        # Confirm/Reject
        ("Sì, va bene", NLUIntent.CONFERMA),
        ("Sì, confermo", NLUIntent.CONFERMA),
        ("Confermo", NLUIntent.CONFERMA),
        ("No, annulla", NLUIntent.RIFIUTO),

        # Corrections
        ("No aspetta, volevo domani", NLUIntent.CORREZIONE),

        # Booking
        ("Vorrei prenotare un taglio per domani alle 15", NLUIntent.PRENOTAZIONE),
    ]

    for text, expected_intent in test_cases:
        print(f"\nInput: \"{text}\"")
        result = nlu.process(text, skip_layer3=True)  # Skip UmBERTo for quick test

        status = "✅" if result.intent == expected_intent else "❌"
        print(f"  {status} Intent: {result.intent.value} (expected: {expected_intent.value})")
        print(f"     Layer: {result.layer}, Confidence: {result.confidence:.2f}")

        if result.entities:
            print(f"     Entities: {[(e.text, e.label) for e in result.entities]}")
        if result.slots:
            print(f"     Slots: {result.slots}")
        if result.is_new_client:
            print(f"     → NEW CLIENT DETECTED")

    print("\n" + "=" * 60)
    print("Test complete.")
