# FLUXION Voice Agent
# Italian voice assistant for automatic bookings

__version__ = "0.1.0"

from .intent_classifier import (
    classify_intent,
    exact_match_intent,
    pattern_based_intent,
    normalize_input,
    IntentResult,
    IntentCategory,
)
