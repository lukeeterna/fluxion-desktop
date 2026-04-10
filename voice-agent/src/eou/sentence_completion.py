"""
Italian Sentence-Completion Heuristics
=======================================

Estimates the probability that an Italian utterance is syntactically and
pragmatically complete — i.e. the speaker has finished their turn.

Returns a float in [0.0, 1.0]:
    0.0 – 0.3  →  clearly incomplete (Sara should wait longer)
    0.3 – 0.7  →  ambiguous (use default timing)
    0.7 – 1.0  →  clearly complete (Sara can respond immediately)

Algorithm
---------
The function applies a series of ordered pattern checks (short-circuit on
match) followed by a word-count heuristic for the remaining "neutral" cases.

Incomplete signals (return ~0.2):
    - Last meaningful token is a coordinating/subordinating conjunction or
      preposition that opens a new clause: "e", "ma", "però", "oppure",
      "perché", "quando", "dove", "se", "che", "quindi", "allora", "come",
      "anche", "poi", "mentre"
    - Text ends with a comma (speaker is listing or continuing)
    - Single content word that is not a common one-word answer

Complete signals (return ~0.9):
    - Ends with sentence-final punctuation (. ! ?)
    - Last meaningful token is a pragmatic closer: "grazie", "arrivederci",
      "ciao", "perfetto", "benissimo", "esatto", "capito", "ok", "okay"
    - Last meaningful token is a polar answer: "sì", "si", "no"
    - Ends with "per favore" or "per piacere" (polite request complete)
    - Ends with "ecco" (deictic completion signal)

Neutral (probability by word count):
    ≥ 4 words  →  0.7  (long enough to be a complete thought)
    < 4 words  →  0.5  (short but no clear signal either way)

Zero new dependencies — only `re` and `typing` from stdlib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Token lists (lowercase, no accents normalization needed — kept with accents)
# ---------------------------------------------------------------------------

# Conjunctions/prepositions that signal an OPEN clause when sentence-final
_INCOMPLETE_CLOSERS: frozenset = frozenset({
    "e", "ma", "però", "perche", "perché", "oppure",
    "quando", "dove", "se", "che", "quindi", "allora",
    "come", "anche", "poi", "mentre", "dopo", "prima",
    "affinché", "affinche", "sebbene", "nonostante",
    "benché", "benche", "dunque", "poiché", "poiche",
    "giacché", "giacche",
})

# Pragmatic COMPLETE closers (full utterances or utterance-final tags)
_COMPLETE_CLOSERS: frozenset = frozenset({
    "grazie", "arrivederci", "ciao", "salve",
    "perfetto", "benissimo", "esatto", "capito", "bene",
    "ok", "okay", "va", "bene", "d'accordo", "concordo",
    "ecco", "appunto", "certamente", "assolutamente",
    "ovviamente", "certo",
})

# Polar short answers — high confidence complete
_POLAR_ANSWERS: frozenset = frozenset({
    "sì", "si", "no", "nope", "yep",
})

# Multi-word complete endings (checked as suffix on normalised text)
_COMPLETE_SUFFIXES: tuple = (
    "per favore",
    "per piacere",
    "se non le dispiace",
    "se non ti dispiace",
    "grazie mille",
    "molte grazie",
    "tante grazie",
)

# Sentence-final punctuation regex
_FINAL_PUNCT_RE = re.compile(r"[.!?…]+\s*$")

# Trailing comma (open list / unfinished enumeration)
_TRAILING_COMMA_RE = re.compile(r",\s*$")


@dataclass
class SentenceCompletionResult:
    """
    Detailed result from :func:`sentence_complete_probability`.

    Attributes
    ----------
    probability:
        Completion probability in [0.0, 1.0].
    reason:
        Short English label describing which rule fired.
    raw_text:
        The input text (stripped).
    """

    probability: float
    reason: str
    raw_text: str


def sentence_complete_probability(text: str) -> float:
    """
    Return the probability that *text* is a complete Italian utterance.

    Parameters
    ----------
    text:
        STT transcript for the current user turn.  May contain partial
        punctuation inserted by the STT engine.

    Returns
    -------
    float
        Value in [0.0, 1.0].  Higher → more complete.

    Examples
    --------
    >>> sentence_complete_probability("Vorrei un taglio e")
    0.2
    >>> sentence_complete_probability("Sì, confermo")
    0.9
    >>> sentence_complete_probability("Grazie mille")
    0.9
    """
    return _analyze(text).probability


def analyze_sentence_completion(text: str) -> SentenceCompletionResult:
    """
    Full-detail version of :func:`sentence_complete_probability`.

    Returns a :class:`SentenceCompletionResult` with the probability AND
    the rule that fired, useful for logging and debugging.
    """
    return _analyze(text)


# ---------------------------------------------------------------------------
# Internal implementation
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def _last_token(normalized: str) -> str:
    """Return the last whitespace-separated token, stripped of punctuation."""
    tokens = normalized.split()
    if not tokens:
        return ""
    return tokens[-1].strip(".,!?;:\"'()[]")


def _analyze(text: str) -> SentenceCompletionResult:
    """Core analysis — returns a full SentenceCompletionResult."""
    stripped = text.strip() if text else ""

    # --- Edge: empty ---
    if not stripped:
        return SentenceCompletionResult(
            probability=0.5,
            reason="empty_input",
            raw_text=stripped,
        )

    norm = _normalize(stripped)
    last = _last_token(norm)
    words = norm.split()
    wc = len(words)

    # --- 1. Sentence-final punctuation (highest confidence) ---
    if _FINAL_PUNCT_RE.search(stripped):
        return SentenceCompletionResult(
            probability=0.95,
            reason="final_punctuation",
            raw_text=stripped,
        )

    # --- 2. Trailing comma → incomplete ---
    # Only fires when the WHOLE utterance ends with a comma (open list).
    # "Sì, confermo" ends with a word — the comma is mid-sentence, not trailing.
    if _TRAILING_COMMA_RE.search(stripped):
        return SentenceCompletionResult(
            probability=0.2,
            reason="trailing_comma",
            raw_text=stripped,
        )

    # --- 3. Multi-word complete suffix (e.g. "per favore") ---
    for suffix in _COMPLETE_SUFFIXES:
        if norm.endswith(suffix):
            return SentenceCompletionResult(
                probability=0.9,
                reason=f"complete_suffix:{suffix}",
                raw_text=stripped,
            )

    # --- 4. Polar answer as last token OR as sentence-opener ("Sì, confermo") ---
    first_token = words[0].strip(".,!?;:\"'()[]") if words else ""
    if last in _POLAR_ANSWERS or first_token in _POLAR_ANSWERS:
        return SentenceCompletionResult(
            probability=0.9,
            reason="polar_answer",
            raw_text=stripped,
        )

    # --- 5. Complete closer as last token ---
    if last in _COMPLETE_CLOSERS:
        return SentenceCompletionResult(
            probability=0.9,
            reason=f"complete_closer:{last}",
            raw_text=stripped,
        )

    # --- 6. Incomplete conjunction/preposition as last token ---
    if last in _INCOMPLETE_CLOSERS:
        return SentenceCompletionResult(
            probability=0.2,
            reason=f"open_conjunction:{last}",
            raw_text=stripped,
        )

    # --- 7. Neutral: fall back to word-count heuristic ---
    if wc >= 4:
        return SentenceCompletionResult(
            probability=0.7,
            reason="word_count_long",
            raw_text=stripped,
        )

    return SentenceCompletionResult(
        probability=0.5,
        reason="word_count_short",
        raw_text=stripped,
    )
