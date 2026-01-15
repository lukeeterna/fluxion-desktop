"""
FLUXION Voice Agent - NLU Module

4-Layer Italian NLU Pipeline:
- Layer 1: Regex pattern matching for implicit intents
- Layer 2: spaCy NER with blacklist filtering
- Layer 3: UmBERTo intent classification (zero-shot)
- Layer 4: Context management for multi-turn

Performance: ~100-120ms total latency
Model Size: ~450MB (spaCy 43MB + UmBERTo ~400MB)
100% Offline
"""

from .italian_nlu import ItalianVoiceAgentNLU

__all__ = ["ItalianVoiceAgentNLU"]
