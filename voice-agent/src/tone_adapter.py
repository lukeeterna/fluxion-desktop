"""
FLUXION Voice Agent - Tone Adapter

Adapts Sara's response text based on caller sentiment.

Three tone modes:
- EMPATHETIC: frustrated caller -> shorter, more direct, empathetic phrasing
- NEUTRAL: default mode -> professional but warm
- ENTHUSIASTIC: happy caller -> more energy, warmth

Design:
- Pure text transformations, no ML
- Python 3.9 compatible
- Zero external dependencies
- Works with existing SentimentAnalyzer output
"""

import re
import random
from enum import Enum
from typing import List, Optional


class ToneMode(str, Enum):
    EMPATHETIC = "empathetic"      # For frustrated callers
    NEUTRAL = "neutral"            # Default
    ENTHUSIASTIC = "enthusiastic"  # For happy callers


# Empathy prefixes (rotated to avoid repetition)
_EMPATHY_PREFIXES: List[str] = [
    "Capisco.",
    "Ha ragione.",
    "Mi dispiace.",
    "Comprendo.",
    "Mi scusi.",
]

# Enthusiastic prefixes (rotated)
_ENTHUSIASTIC_PREFIXES: List[str] = [
    "Che bello!",
    "Fantastico!",
    "Ottimo!",
    "Benissimo!",
]

# Filler words to strip in empathetic mode (case-insensitive, at sentence start)
_FILLER_PATTERNS: List[re.Pattern] = [
    re.compile(r'^Allora,?\s*', re.IGNORECASE),
    re.compile(r'^Dunque,?\s*', re.IGNORECASE),
    re.compile(r'^Ecco,?\s*', re.IGNORECASE),
    re.compile(r'^Bene,?\s*', re.IGNORECASE),
]

# Backchannel phrases to suppress in empathetic mode
_BACKCHANNEL_PATTERNS: List[re.Pattern] = [
    re.compile(r'^Perfetto!\s*', re.IGNORECASE),
    re.compile(r'^Grande!\s*', re.IGNORECASE),
    re.compile(r'^Fantastico!\s*', re.IGNORECASE),
    re.compile(r'^Benissimo!\s*', re.IGNORECASE),
    re.compile(r'^Ottimo!\s*', re.IGNORECASE),
    re.compile(r'^Che bello!\s*', re.IGNORECASE),
    re.compile(r'^Splendido!\s*', re.IGNORECASE),
    re.compile(r'^Meraviglioso!\s*', re.IGNORECASE),
]


class ToneAdapter:
    """
    Adapts Sara's responses to match the caller's emotional state.

    Tone is updated each turn based on sentiment analysis output.
    EMPATHETIC is sticky (stays until a positive turn resets it).
    ENTHUSIASTIC decays after 2 turns back to NEUTRAL.
    """

    def __init__(self):
        self._current_tone: ToneMode = ToneMode.NEUTRAL
        self._tone_history: List[ToneMode] = []
        self._enthusiastic_turns_remaining: int = 0
        self._empathy_prefix_index: int = 0
        self._enthusiastic_prefix_index: int = 0

    @property
    def current_tone(self) -> ToneMode:
        """Current active tone mode."""
        return self._current_tone

    def update_tone(self, sentiment: str, frustration_level: int) -> ToneMode:
        """
        Update tone based on current turn's sentiment.

        Args:
            sentiment: "positive", "neutral", or "negative" (from Sentiment.value)
            frustration_level: 0-4 int (from FrustrationLevel.value)

        Returns:
            The new ToneMode after this update.
        """
        previous_tone = self._current_tone

        # Frustrated/negative -> EMPATHETIC (sticky until positive)
        if sentiment == "negative" or frustration_level >= 2:
            self._current_tone = ToneMode.EMPATHETIC
            self._enthusiastic_turns_remaining = 0

        # Positive -> ENTHUSIASTIC (for 2 turns), also breaks EMPATHETIC sticky
        elif sentiment == "positive":
            self._current_tone = ToneMode.ENTHUSIASTIC
            self._enthusiastic_turns_remaining = 2

        # Neutral -> decay enthusiastic, keep empathetic sticky
        else:
            if self._current_tone == ToneMode.ENTHUSIASTIC:
                self._enthusiastic_turns_remaining -= 1
                if self._enthusiastic_turns_remaining <= 0:
                    self._current_tone = ToneMode.NEUTRAL
            elif self._current_tone == ToneMode.EMPATHETIC:
                # EMPATHETIC is sticky: stays until positive turn
                pass
            # else: stays NEUTRAL

        self._tone_history.append(self._current_tone)
        return self._current_tone

    def adapt_response(self, response: str, tone: Optional[ToneMode] = None) -> str:
        """
        Modify response text to match the given tone.

        Args:
            response: The original response text.
            tone: Tone to apply. If None, uses current tone.

        Returns:
            Adapted response text.
        """
        if tone is None:
            tone = self._current_tone

        if not response or not response.strip():
            return response

        if tone == ToneMode.NEUTRAL:
            return response

        if tone == ToneMode.EMPATHETIC:
            return self._adapt_empathetic(response)

        if tone == ToneMode.ENTHUSIASTIC:
            return self._adapt_enthusiastic(response)

        return response

    def _adapt_empathetic(self, response: str) -> str:
        """Apply empathetic adaptations to response."""
        text = response

        # 1. Strip backchannel exclamations at the start
        for pattern in _BACKCHANNEL_PATTERNS:
            text = pattern.sub('', text)

        # 2. Strip filler words at the start
        for pattern in _FILLER_PATTERNS:
            text = pattern.sub('', text)

        # 3. Strip trailing exclamation marks (replace with periods)
        # But preserve "?" for questions
        text = re.sub(r'!(\s|$)', r'.\1', text)
        # Clean up double periods
        text = text.replace('..', '.')

        # 4. Re-capitalize first letter after stripping
        text = text.strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # 5. Add empathy prefix (rotate through pool)
        if text:
            prefix = _EMPATHY_PREFIXES[self._empathy_prefix_index % len(_EMPATHY_PREFIXES)]
            self._empathy_prefix_index += 1
            text = f"{prefix} {text}"

        return text

    def _adapt_enthusiastic(self, response: str) -> str:
        """Apply enthusiastic adaptations to response."""
        text = response.strip()

        # Add warmth prefix occasionally (every other turn)
        if self._enthusiastic_prefix_index % 2 == 0 and text:
            # Don't add prefix if the response already starts with an exclamation
            first_sentence_end = min(
                text.find('.') if text.find('.') > 0 else len(text),
                text.find('!') if text.find('!') > 0 else len(text),
                text.find('?') if text.find('?') > 0 else len(text),
            )
            first_part = text[:first_sentence_end].lower()
            # Skip if already enthusiastic
            already_enthusiastic = any(
                kw in first_part
                for kw in ["fantastico", "ottimo", "bello", "benissimo", "splendido", "grande"]
            )
            if not already_enthusiastic:
                prefix = _ENTHUSIASTIC_PREFIXES[
                    (self._enthusiastic_prefix_index // 2) % len(_ENTHUSIASTIC_PREFIXES)
                ]
                text = f"{prefix} {text}"

        self._enthusiastic_prefix_index += 1
        return text

    def get_empathy_prefix(self) -> str:
        """Get the next empathy prefix from the rotation pool."""
        prefix = _EMPATHY_PREFIXES[self._empathy_prefix_index % len(_EMPATHY_PREFIXES)]
        self._empathy_prefix_index += 1
        return prefix

    def reset(self):
        """Reset tone state for a new session."""
        self._current_tone = ToneMode.NEUTRAL
        self._tone_history.clear()
        self._enthusiastic_turns_remaining = 0
        self._empathy_prefix_index = 0
        self._enthusiastic_prefix_index = 0
