"""
Intent LRU Cache — Fluxion F03 Latency Optimizer
=================================================
Wraps classify_intent with a 100-slot LRU cache keyed on normalized input.
classify_intent is called 4 times per orchestrator.process() turn on the same
string — this eliminates 3 redundant TF-IDF + regex scans per turn (~10-15ms).

Python 3.9 compatible: uses Optional[], List[], Dict[] from typing.
lru_cache is thread-safe in CPython (GIL protects dict ops between await points).
"""
import re
from functools import lru_cache
from typing import Any

try:
    from .intent_classifier import classify_intent
except ImportError:
    from intent_classifier import classify_intent


def _normalize_input(text: str) -> str:
    """Normalize for cache key: strip + lowercase + collapse whitespace."""
    return re.sub(r'\s+', ' ', text.strip().lower())


@lru_cache(maxsize=100)
def _cached_classify(normalized: str) -> Any:
    """
    Cached classify_intent on normalized input.
    NOTE: lru_cache requires hashable args — str is hashable.
    NOTE: Do NOT use lru_cache on async functions.
    """
    return classify_intent(normalized)


def get_cached_intent(user_input: str) -> Any:
    """
    Public API: classify_intent with 100-slot LRU cache.
    Returns IntentResult. Caches by normalized form of user_input.
    """
    return _cached_classify(_normalize_input(user_input))


def clear_intent_cache() -> None:
    """
    Clear cache on session reset to avoid cross-session pollution.
    Call from orchestrator reset() method.
    """
    _cached_classify.cache_clear()
