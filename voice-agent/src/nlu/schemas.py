"""
FLUXION Voice Agent — NLU Schemas
Dataclasses and JSON schema for LLM-based NLU extraction.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from enum import Enum
import json


class SaraIntent(str, Enum):
    """All intents Sara can handle."""
    PRENOTAZIONE = "PRENOTAZIONE"
    CANCELLAZIONE = "CANCELLAZIONE"
    SPOSTAMENTO = "SPOSTAMENTO"
    WAITLIST = "WAITLIST"
    CONFERMA = "CONFERMA"
    RIFIUTO = "RIFIUTO"
    CORREZIONE = "CORREZIONE"
    CORTESIA = "CORTESIA"
    CHIUSURA = "CHIUSURA"
    ESCALATION = "ESCALATION"
    FAQ = "FAQ"
    OSCENITA = "OSCENITA"
    ALTRO = "ALTRO"


class Sentiment(str, Enum):
    POSITIVO = "POSITIVO"
    NEUTRO = "NEUTRO"
    FRUSTRATO = "FRUSTRATO"
    AGGRESSIVO = "AGGRESSIVO"


@dataclass
class NLUEntities:
    """Entities extracted from user utterance."""
    nome: Optional[str] = None
    cognome: Optional[str] = None
    servizio: Optional[str] = None
    data: Optional[str] = None          # YYYY-MM-DD or relative ("domani")
    ora: Optional[str] = None           # HH:MM
    operatore: Optional[str] = None
    telefono: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def has_any(self) -> bool:
        return any(v is not None for v in asdict(self).values())


@dataclass
class NLUResult:
    """Result of NLU extraction — used by FSM for slot filling."""
    intent: SaraIntent
    entities: NLUEntities
    sentiment: Sentiment
    correction_field: Optional[str] = None  # which field user wants to correct
    confidence: float = 0.0
    provider: str = "unknown"               # which provider answered
    latency_ms: float = 0.0
    raw_text: str = ""                      # original user input

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "entities": self.entities.to_dict(),
            "sentiment": self.sentiment.value,
            "correction_field": self.correction_field,
            "confidence": self.confidence,
            "provider": self.provider,
            "latency_ms": self.latency_ms,
        }

    @classmethod
    def from_llm_json(cls, data: Dict[str, Any], provider: str = "unknown",
                      latency_ms: float = 0.0, raw_text: str = "") -> "NLUResult":
        """Parse LLM structured output into NLUResult."""
        # Intent
        intent_str = data.get("intent", "ALTRO").upper()
        try:
            intent = SaraIntent(intent_str)
        except ValueError:
            intent = SaraIntent.ALTRO

        # Entities
        ent_data = data.get("entities", {})
        entities = NLUEntities(
            nome=ent_data.get("nome"),
            cognome=ent_data.get("cognome"),
            servizio=ent_data.get("servizio"),
            data=ent_data.get("data"),
            ora=ent_data.get("ora"),
            operatore=ent_data.get("operatore"),
            telefono=ent_data.get("telefono"),
        )

        # Sentiment
        sent_str = data.get("sentiment", "NEUTRO").upper()
        try:
            sentiment = Sentiment(sent_str)
        except ValueError:
            sentiment = Sentiment.NEUTRO

        return cls(
            intent=intent,
            entities=entities,
            sentiment=sentiment,
            correction_field=data.get("correction_field"),
            confidence=float(data.get("confidence", 0.5)),
            provider=provider,
            latency_ms=latency_ms,
            raw_text=raw_text,
        )

    @classmethod
    def fallback(cls, raw_text: str = "") -> "NLUResult":
        """Return a safe fallback result when all NLU methods fail."""
        return cls(
            intent=SaraIntent.ALTRO,
            entities=NLUEntities(),
            sentiment=Sentiment.NEUTRO,
            confidence=0.0,
            provider="fallback",
            raw_text=raw_text,
        )


# ─────────────────────────────────────────────────────────────────
# JSON Schema for LLM tool_use / structured output
# ─────────────────────────────────────────────────────────────────

# JSON mode response format — simpler and more reliable than tool_use on 8B models
SARA_NLU_JSON_MODE = {"type": "json_object"}

# JSON schema instruction to include in system prompt (for json_object mode)
SARA_NLU_JSON_INSTRUCTION = """Rispondi SOLO con un JSON valido con questa struttura:
{
  "intent": "PRENOTAZIONE|CANCELLAZIONE|SPOSTAMENTO|WAITLIST|CONFERMA|RIFIUTO|CORREZIONE|CORTESIA|CHIUSURA|ESCALATION|FAQ|OSCENITA|ALTRO",
  "entities": {"nome": "...", "cognome": "...", "servizio": "...", "data": "YYYY-MM-DD", "ora": "HH:MM", "operatore": "...", "telefono": "..."},
  "sentiment": "POSITIVO|NEUTRO|FRUSTRATO|AGGRESSIVO",
  "correction_field": "nome|cognome|servizio|data|ora|operatore|telefono|null",
  "confidence": 0.0-1.0
}
Includi solo le entità effettivamente menzionate. Ometti quelle non dette."""
