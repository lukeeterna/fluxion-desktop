"""
FLUXION Voice Agent - Prosody Injector

Adds natural speech patterns to TTS text output.

NOT SSML - uses text-level techniques that work with ANY TTS engine:
- Comma insertion for natural pauses
- Ellipsis for thinking pauses
- Period splitting for breath points

Works with Edge-TTS, Piper, and SystemTTS without engine-specific code.
"""

import re
from typing import Optional


# Logical break points in Italian (conjunctions, prepositions)
_BREAK_WORDS = re.compile(
    r'(?<=\S)\s+(dopo|per|con|che|quindi|inoltre|oppure|mentre|perche|anche)\s+',
    re.IGNORECASE,
)

# Day/time patterns for thinking pause
_DATE_TIME_RE = re.compile(
    r'\b(luned[iì]|marted[iì]|mercoled[iì]|gioved[iì]|venerd[iì]|sabato|domenica'
    r'|domani|dopodomani|oggi|alle\s+\d{1,2}[:.]\d{2}|alle\s+\d{1,2})\b',
    re.IGNORECASE,
)

# Italian list without commas: "A B e C" or "A B C e D"
# Matches 2+ bare words before "e/ed" + final word
_BARE_LIST_RE = re.compile(
    r'(\b\w+)\s+(\w+)\s+(e|ed)\s+(\w+)\b',
    re.IGNORECASE,
)

# Contexts where we skip modifications
_PASSTHROUGH_CONTEXTS = {"greeting", "question"}

# Max sentence length before adding breathing pauses
_BREATH_THRESHOLD = 60


class ProsodyInjector:
    """Injects natural prosody patterns into text before TTS synthesis."""

    def inject(self, text: str, context: str = "default") -> str:
        """Apply prosody patterns to text.

        Args:
            text: Raw response text from Sara
            context: "greeting", "confirmation", "question", "info", "goodbye", "default"

        Returns:
            Text with natural prosody markers (commas, periods, ellipsis)
        """
        if not text or not text.strip():
            return text

        # Short text or passthrough contexts: don't modify
        if context in _PASSTHROUGH_CONTEXTS:
            return text
        if len(text) < 30:
            return text

        result = text
        result = self._add_list_rhythm(result)
        result = self._add_breathing_pauses(result)
        if context in ("confirmation", "info"):
            result = self._add_thinking_pause(result)
        result = self._clean_punctuation(result)
        return result

    def _add_breathing_pauses(self, text: str) -> str:
        """Break long sentences into shorter breath groups."""
        sentences = text.split('. ')
        out = []
        for sentence in sentences:
            if len(sentence) > _BREATH_THRESHOLD:
                # Insert comma at first logical break point after 30 chars
                best_pos = None
                for m in _BREAK_WORDS.finditer(sentence):
                    pos = m.start()
                    if pos >= 30:
                        best_pos = pos
                        break
                if best_pos is not None:
                    # Only insert comma if there isn't one already nearby
                    before = sentence[max(0, best_pos - 2):best_pos]
                    if ',' not in before and '.' not in before:
                        sentence = sentence[:best_pos] + ',' + sentence[best_pos:]
            out.append(sentence)
        return '. '.join(out)

    def _add_thinking_pause(self, text: str) -> str:
        """Add '...' before dates/times (thinking effect)."""
        # Only add if text doesn't already contain ellipsis
        if '...' in text:
            return text

        m = _DATE_TIME_RE.search(text)
        if not m:
            return text

        pos = m.start()
        # Don't add at very beginning of text
        if pos < 5:
            return text

        # Check if there's already punctuation just before
        before_char = text[pos - 1] if pos > 0 else ''
        before2 = text[max(0, pos - 2):pos].strip()
        if before_char in '.,;:!?':
            return text

        # Insert ellipsis before the date/time word
        # Find the space before the match
        space_pos = text.rfind(' ', 0, pos)
        if space_pos > 0:
            return text[:space_pos] + '...' + text[space_pos:]
        return text

    def _add_list_rhythm(self, text: str) -> str:
        """Ensure lists have comma-separated rhythm."""

        def _add_comma(m: re.Match) -> str:
            a, b, conj, c = m.group(1), m.group(2), m.group(3), m.group(4)
            # Don't break if words are very short (likely not a list)
            if len(a) < 3 or len(b) < 3 or len(c) < 3:
                return m.group(0)
            return f"{a}, {b}, {conj} {c}"

        return _BARE_LIST_RE.sub(_add_comma, text)

    def _clean_punctuation(self, text: str) -> str:
        """Remove double punctuation artifacts."""
        # Double commas
        text = re.sub(r',\s*,', ',', text)
        # Comma before period
        text = re.sub(r',\s*\.', '.', text)
        # Double periods (but preserve ellipsis)
        text = re.sub(r'(?<!\.)\.\.(?!\.)', '.', text)
        # Double spaces
        text = re.sub(r'  +', ' ', text)
        return text
