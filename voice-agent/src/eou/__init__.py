"""
Fluxion EOU Module
==================

End-of-Utterance detection for Sara voice agent.
Uses zero external dependencies — pure stdlib + heuristics.

Components:
- adaptive_silence: context-aware silence threshold (400-900ms)
- sentence_completion: Italian sentence-completion probability (0.0-1.0)
"""

from .adaptive_silence import get_adaptive_silence_ms, AdaptiveSilenceConfig
from .sentence_completion import sentence_complete_probability, SentenceCompletionResult

__all__ = [
    "get_adaptive_silence_ms",
    "AdaptiveSilenceConfig",
    "sentence_complete_probability",
    "SentenceCompletionResult",
]
