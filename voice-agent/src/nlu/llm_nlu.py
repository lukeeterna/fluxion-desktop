"""
FLUXION Voice Agent — LLM-Based NLU Engine
Enterprise 2026 architecture: LLM structured output replaces 2000 lines of regex.

3-Layer Architecture:
  Layer 0: Profanity filter + trivial fast path (<1ms)
  Layer 1: LLM structured output via multi-provider rotation (~150ms)
  Layer 2: Template fuzzy matching fallback (<10ms, offline)

The LLM naturally handles:
  - Italian conjugations, dialects, informal speech
  - STT errors and typos
  - Name corrections ("mi chiamo Franco Decillis, De spazio cillis")
  - Negation ("non voglio cancellare" ≠ CANCELLAZIONE)
  - Context-aware entity extraction
"""

import time
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List

from .schemas import (
    NLUResult, NLUEntities, SaraIntent, Sentiment,
    SARA_NLU_JSON_MODE, SARA_NLU_JSON_INSTRUCTION,
)
from .providers import ProviderRotation
from .template_fallback import classify_template, check_profanity

logger = logging.getLogger("fluxion.nlu")


# ─────────────────────────────────────────────────────────────────
# System prompt for LLM NLU — the core of the new architecture
# ─────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Sei il modulo NLU di Sara, receptionist virtuale per un'{vertical_desc}.
Analizza il messaggio del cliente ed estrai intent, entità e sentiment.

CONTESTO:
- Stato: {current_state}
- Slot compilati: {filled_slots}
- Verticale: {vertical}
- Servizi: {services}
- Oggi: {today}

REGOLE:
1. Estrai SOLO entità esplicitamente menzionate
2. "non voglio cancellare" → intent=RIFIUTO (la negazione inverte l'intent)
3. Correzione dati ("mi chiamo X, non Y") → intent=CORREZIONE, correction_field=campo
4. Cognomi con prefisso: "De Cillis", "Di Stasi", "La Rosa" sono UN cognome
5. Linguaggio volgare → intent=OSCENITA
6. Vuole parlare con umano → intent=ESCALATION

{json_instruction}"""


# Fast path: single-word inputs that don't need LLM
_FAST_PATH: Dict[str, SaraIntent] = {
    "sì": SaraIntent.CONFERMA,
    "si": SaraIntent.CONFERMA,
    "no": SaraIntent.RIFIUTO,
    "ok": SaraIntent.CONFERMA,
    "esatto": SaraIntent.CONFERMA,
    "confermo": SaraIntent.CONFERMA,
    "grazie": SaraIntent.CORTESIA,
    "prego": SaraIntent.CORTESIA,
    "aiuto": SaraIntent.ESCALATION,
    "operatore": SaraIntent.ESCALATION,
    "arrivederci": SaraIntent.CHIUSURA,
    "ciao": SaraIntent.CORTESIA,
    "buongiorno": SaraIntent.CORTESIA,
    "buonasera": SaraIntent.CORTESIA,
}


class LLMNlu:
    """
    LLM-based NLU engine for Sara voice agent.
    Replaces italian_regex.py (1350 lines) + intent_classifier.py + entity_extractor.py.
    """

    def __init__(self, providers: Optional[ProviderRotation] = None):
        self._providers = providers or ProviderRotation()
        self._call_count = 0
        self._total_latency_ms = 0.0

    async def close(self):
        await self._providers.close()

    @property
    def avg_latency_ms(self) -> float:
        if self._call_count == 0:
            return 0.0
        return self._total_latency_ms / self._call_count

    async def extract(
        self,
        text: str,
        current_state: str = "IDLE",
        filled_slots: Optional[Dict[str, str]] = None,
        vertical: str = "salone",
        services: Optional[List[str]] = None,
    ) -> NLUResult:
        """
        Extract intent + entities + sentiment from user text.
        3-layer cascade: fast_path → LLM → template_fallback.

        Args:
            text: User's raw text input
            current_state: Current FSM state (e.g. "WAITING_NAME")
            filled_slots: Already filled booking slots
            vertical: Business vertical (salone, clinica, officina, etc.)
            services: Available services for this vertical

        Returns:
            NLUResult with intent, entities, sentiment, confidence
        """
        t0 = time.perf_counter()
        text_stripped = text.strip()
        text_lower = text_stripped.lower()

        # ─── Layer 0: Profanity + Fast Path ─────────────────────
        if check_profanity(text_lower):
            return NLUResult(
                intent=SaraIntent.OSCENITA,
                entities=NLUEntities(),
                sentiment=Sentiment.AGGRESSIVO,
                confidence=0.99,
                provider="profanity_filter",
                latency_ms=(time.perf_counter() - t0) * 1000,
                raw_text=text,
            )

        # Fast path for single-word inputs
        if text_lower in _FAST_PATH:
            return NLUResult(
                intent=_FAST_PATH[text_lower],
                entities=NLUEntities(),
                sentiment=Sentiment.NEUTRO,
                confidence=0.99,
                provider="fast_path",
                latency_ms=(time.perf_counter() - t0) * 1000,
                raw_text=text,
            )

        # ─── Layer 1: LLM Structured Output ─────────────────────
        if self._providers.has_providers:
            llm_result = await self._call_llm(
                text, current_state, filled_slots or {}, vertical, services or [],
            )
            if llm_result is not None:
                latency = (time.perf_counter() - t0) * 1000
                self._call_count += 1
                self._total_latency_ms += latency

                result = NLUResult.from_llm_json(
                    llm_result,
                    provider=llm_result.get("_provider", "unknown"),
                    latency_ms=llm_result.get("_latency_ms", latency),
                    raw_text=text,
                )
                return result

        # ─── Layer 2: Template Fuzzy Fallback ────────────────────
        logger.warning("[NLU] LLM unavailable, using template fallback")
        intent_str, confidence = classify_template(text)
        try:
            intent = SaraIntent(intent_str)
        except ValueError:
            intent = SaraIntent.ALTRO

        return NLUResult(
            intent=intent,
            entities=NLUEntities(),
            sentiment=Sentiment.NEUTRO,
            confidence=confidence,
            provider="template_fallback",
            latency_ms=(time.perf_counter() - t0) * 1000,
            raw_text=text,
        )

    async def _call_llm(
        self,
        text: str,
        current_state: str,
        filled_slots: Dict[str, str],
        vertical: str,
        services: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Build prompt and call LLM via provider rotation."""

        # Map vertical to description
        vertical_desc = {
            "hair": "parrucchiere/salone",
            "salone": "parrucchiere/salone",
            "beauty": "centro estetico",
            "estetica": "centro estetico",
            "wellness": "centro benessere/palestra",
            "palestra": "palestra/centro fitness",
            "medico": "studio medico/clinica",
            "medical": "studio medico/clinica",
            "auto": "officina meccanica/carrozzeria",
            "officina": "officina meccanica",
            "professionale": "studio professionale",
        }.get(vertical, "attività commerciale")

        # Format filled slots
        slots_str = json.dumps(filled_slots, ensure_ascii=False) if filled_slots else "nessuno"
        services_str = ", ".join(services[:20]) if services else "non specificati"
        today = datetime.now().strftime("%Y-%m-%d (%A)")

        system_prompt = _SYSTEM_PROMPT.format(
            vertical_desc=vertical_desc,
            current_state=current_state,
            filled_slots=slots_str,
            vertical=vertical,
            services=services_str,
            today=today,
            json_instruction=SARA_NLU_JSON_INSTRUCTION,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]

        return await self._providers.call_llm(
            messages=messages,
            temperature=0.0,
            max_tokens=200,
        )


# ─────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────

def create_llm_nlu() -> LLMNlu:
    """Create LLM NLU engine with default provider rotation."""
    return LLMNlu(ProviderRotation())
