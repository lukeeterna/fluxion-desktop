"""
FLUXION Voice Agent - NLU Module

Architecture 2026 — 3-Layer NLU:
  Layer 0: Profanity filter + fast path (<1ms)
  Layer 1: LLM structured output via multi-provider rotation (~150ms)
  Layer 2: Template fuzzy matching fallback (<10ms, offline)
"""

from .semantic_classifier import SemanticIntentClassifier, semantic_intent

from .schemas import NLUResult, NLUEntities, SaraIntent, Sentiment
from .llm_nlu import LLMNlu, create_llm_nlu

__all__ = [
    "SemanticIntentClassifier", "semantic_intent",
    "NLUResult", "NLUEntities", "SaraIntent", "Sentiment",
    "LLMNlu", "create_llm_nlu",
]
