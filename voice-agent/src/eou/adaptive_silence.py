"""
Adaptive Silence Duration for EOU Detection
============================================

Determines how long Sara should wait in silence before treating a user
utterance as complete.  Three signals are fused:

1. Word count of the partial transcript (fast proxy for utterance length)
2. Sentence-completion probability from sentence_completion.py (if provided)
3. Current FSM state (some states imply the user is thinking longer)

Word-count buckets (baseline):
    ≤ 2 words  →  400 ms  ("sì", "no", "martedì")
    3–6 words  →  600 ms  ("alle tre del pomeriggio")
    > 6 words  →  900 ms  (long answer; user may pause mid-thought)

FSM-state override (applied on top of word-count):
    waiting_name / waiting_date / waiting_service  →  floor lifted to 800 ms
    (user is recalling specific data and often pauses before finishing)

Sentence-completion adjustment (optional, additive):
    probability < 0.3  →  +300 ms  (clearly incomplete — wait more)
    probability > 0.8  →  −100 ms  (clearly complete — respond faster)
    otherwise          →  ±0 ms

Zero new dependencies — only stdlib.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Public constants — used in tests for clear expected values
# ---------------------------------------------------------------------------

# Word-count thresholds
_SHORT_WORD_THRESHOLD: int = 2   # ≤ this → SHORT bucket
_MEDIUM_WORD_THRESHOLD: int = 6  # ≤ this → MEDIUM bucket

# Base silence durations (ms)
SILENCE_SHORT_MS: int = 400    # ≤2 words
SILENCE_MEDIUM_MS: int = 600   # 3-6 words
SILENCE_LONG_MS: int = 900     # >6 words
SILENCE_DEFAULT_MS: int = 700  # no transcript available

# FSM states that require longer patience
_THINKING_STATES: frozenset = frozenset(
    {"waiting_name", "waiting_date", "waiting_service"}
)
SILENCE_THINKING_STATE_MS: int = 800  # minimum when in a thinking-state

# Completion-probability adjustments
_COMPLETION_INCOMPLETE_THRESHOLD: float = 0.3
_COMPLETION_COMPLETE_THRESHOLD: float = 0.8
SILENCE_INCOMPLETE_BONUS_MS: int = 300   # added when prob < 0.3
SILENCE_COMPLETE_REDUCTION_MS: int = 100  # subtracted when prob > 0.8

# Hard limits
SILENCE_MIN_MS: int = 300
SILENCE_MAX_MS: int = 1200


@dataclass
class AdaptiveSilenceConfig:
    """
    Tuning knobs for adaptive silence calculation.

    All values are milliseconds unless noted otherwise.
    Override individual fields to tune Sara's responsiveness without
    touching the function logic.
    """

    short_ms: int = SILENCE_SHORT_MS
    medium_ms: int = SILENCE_MEDIUM_MS
    long_ms: int = SILENCE_LONG_MS
    default_ms: int = SILENCE_DEFAULT_MS
    thinking_state_ms: int = SILENCE_THINKING_STATE_MS
    incomplete_bonus_ms: int = SILENCE_INCOMPLETE_BONUS_MS
    complete_reduction_ms: int = SILENCE_COMPLETE_REDUCTION_MS
    min_ms: int = SILENCE_MIN_MS
    max_ms: int = SILENCE_MAX_MS
    short_word_threshold: int = _SHORT_WORD_THRESHOLD
    medium_word_threshold: int = _MEDIUM_WORD_THRESHOLD
    thinking_states: frozenset = field(default_factory=lambda: _THINKING_STATES)


# Module-level default config (shared, immutable-enough for typical use)
_DEFAULT_CONFIG = AdaptiveSilenceConfig()


def get_adaptive_silence_ms(
    transcript: str,
    fsm_state: str = "",
    completion_probability: Optional[float] = None,
    config: Optional[AdaptiveSilenceConfig] = None,
) -> int:
    """
    Return the recommended end-of-utterance silence duration in milliseconds.

    Parameters
    ----------
    transcript:
        Partial or complete STT transcript for the current user turn.
        May be empty string if STT has not yet returned anything.
    fsm_state:
        Current booking FSM state name (e.g. "waiting_name").
        Pass empty string if unknown.
    completion_probability:
        Optional float in [0.0, 1.0] from sentence_completion.
        When provided, adjusts the base duration up or down.
    config:
        Optional :class:`AdaptiveSilenceConfig` to override defaults.

    Returns
    -------
    int
        Silence duration in milliseconds, clamped to [config.min_ms, config.max_ms].

    Examples
    --------
    >>> get_adaptive_silence_ms("sì")
    400
    >>> get_adaptive_silence_ms("vorrei prenotare un taglio capelli per domani mattina")
    900
    >>> get_adaptive_silence_ms("Marco", fsm_state="waiting_name")
    800
    """
    cfg = config or _DEFAULT_CONFIG

    # --- 1. Word-count base ---
    if not transcript or not transcript.strip():
        base_ms = cfg.default_ms
    else:
        words = transcript.strip().split()
        wc = len(words)
        if wc <= cfg.short_word_threshold:
            base_ms = cfg.short_ms
        elif wc <= cfg.medium_word_threshold:
            base_ms = cfg.medium_ms
        else:
            base_ms = cfg.long_ms

    # --- 2. FSM-state floor ---
    if fsm_state and fsm_state in cfg.thinking_states:
        base_ms = max(base_ms, cfg.thinking_state_ms)

    # --- 3. Sentence-completion adjustment ---
    if completion_probability is not None:
        if completion_probability < _COMPLETION_INCOMPLETE_THRESHOLD:
            base_ms += cfg.incomplete_bonus_ms
        elif completion_probability > _COMPLETION_COMPLETE_THRESHOLD:
            base_ms -= cfg.complete_reduction_ms

    # --- 4. Hard clamp ---
    return max(cfg.min_ms, min(cfg.max_ms, base_ms))
