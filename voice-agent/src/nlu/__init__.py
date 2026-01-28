"""
FLUXION Voice Agent - NLU Module

5-Layer Italian NLU Pipeline:
- Layer 1: Exact match cortesia (O(1) lookup)
- Layer 2: Regex pattern matching for implicit intents
- Layer 2.5: TF-IDF semantic classification (numpy only)
- Layer 3: spaCy NER + UmBERTo intent (optional, requires PyTorch)
- Layer 4: Context management for multi-turn

Performance:
- Layers 1-2.5: ~15ms (no PyTorch)
- Full pipeline: ~100-120ms

100% Offline
"""

from .italian_nlu import ItalianVoiceAgentNLU
from .semantic_classifier import SemanticIntentClassifier, semantic_intent

__all__ = ["ItalianVoiceAgentNLU", "SemanticIntentClassifier", "semantic_intent"]
