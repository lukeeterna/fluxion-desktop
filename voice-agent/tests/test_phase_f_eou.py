"""
Phase F1 — EOU Detection Tests
================================

Covers:
  F1-1  adaptive_silence.get_adaptive_silence_ms()
  F1-2  sentence_completion.sentence_complete_probability()
  Edge  empty strings, single words, very long utterances, accented chars
"""

import sys
import os

# Ensure src is importable when run from voice-agent root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from eou.adaptive_silence import (
    get_adaptive_silence_ms,
    AdaptiveSilenceConfig,
    SILENCE_SHORT_MS,
    SILENCE_MEDIUM_MS,
    SILENCE_LONG_MS,
    SILENCE_DEFAULT_MS,
    SILENCE_THINKING_STATE_MS,
    SILENCE_INCOMPLETE_BONUS_MS,
    SILENCE_COMPLETE_REDUCTION_MS,
    SILENCE_MIN_MS,
    SILENCE_MAX_MS,
)
from eou.sentence_completion import (
    sentence_complete_probability,
    analyze_sentence_completion,
)
from eou import (
    get_adaptive_silence_ms as eou_silence,
    sentence_complete_probability as eou_prob,
)


# ===========================================================================
# F1-1: Adaptive Silence Duration
# ===========================================================================

class TestAdaptiveSilenceWordCount:
    """Word-count buckets — no FSM state, no completion probability."""

    def test_empty_transcript_returns_default(self):
        assert get_adaptive_silence_ms("") == SILENCE_DEFAULT_MS

    def test_none_like_empty_string(self):
        # Callers may strip+empty before calling
        assert get_adaptive_silence_ms("   ") == SILENCE_DEFAULT_MS

    def test_single_word_si(self):
        assert get_adaptive_silence_ms("sì") == SILENCE_SHORT_MS

    def test_single_word_no(self):
        assert get_adaptive_silence_ms("no") == SILENCE_SHORT_MS

    def test_two_words_on_boundary(self):
        # Exactly 2 words → still SHORT bucket
        assert get_adaptive_silence_ms("martedì pomeriggio") == SILENCE_SHORT_MS

    def test_three_words_enters_medium(self):
        assert get_adaptive_silence_ms("alle tre oggi") == SILENCE_MEDIUM_MS

    def test_six_words_on_boundary(self):
        # Exactly 6 words → MEDIUM bucket
        assert get_adaptive_silence_ms("vorrei un taglio capelli per domani") == SILENCE_MEDIUM_MS

    def test_seven_words_enters_long(self):
        assert get_adaptive_silence_ms(
            "vorrei prenotare un taglio capelli per domani mattina"
        ) == SILENCE_LONG_MS

    def test_long_utterance_stays_long(self):
        long = " ".join(["parola"] * 20)
        assert get_adaptive_silence_ms(long) == SILENCE_LONG_MS

    def test_returns_int(self):
        result = get_adaptive_silence_ms("ciao")
        assert isinstance(result, int)


class TestAdaptiveSilenceFSMStates:
    """FSM-state overrides the word-count floor."""

    def test_waiting_name_short_transcript_lifted_to_thinking(self):
        # 1 word ("Marco") → normally 400ms, but state lifts to 800ms
        result = get_adaptive_silence_ms("Marco", fsm_state="waiting_name")
        assert result == SILENCE_THINKING_STATE_MS

    def test_waiting_date_short_lifted(self):
        result = get_adaptive_silence_ms("lunedì", fsm_state="waiting_date")
        assert result == SILENCE_THINKING_STATE_MS

    def test_waiting_service_short_lifted(self):
        result = get_adaptive_silence_ms("taglio", fsm_state="waiting_service")
        assert result == SILENCE_THINKING_STATE_MS

    def test_long_transcript_plus_thinking_state_stays_long(self):
        # 7 words → LONG (900ms) > THINKING (800ms) → stays 900ms
        long = "vorrei prenotare un taglio capelli per domani"
        result = get_adaptive_silence_ms(long, fsm_state="waiting_name")
        assert result == SILENCE_LONG_MS

    def test_medium_transcript_plus_thinking_state_lifted(self):
        # 4 words → MEDIUM (600ms) < THINKING (800ms) → lifted to 800ms
        result = get_adaptive_silence_ms("alle tre di mercoledì", fsm_state="waiting_date")
        assert result == SILENCE_THINKING_STATE_MS

    def test_non_thinking_state_no_override(self):
        # "idle" is not a thinking state
        result = get_adaptive_silence_ms("sì", fsm_state="idle")
        assert result == SILENCE_SHORT_MS

    def test_unknown_state_no_override(self):
        result = get_adaptive_silence_ms("sì", fsm_state="unknown_xyz")
        assert result == SILENCE_SHORT_MS

    def test_empty_fsm_state_no_override(self):
        result = get_adaptive_silence_ms("sì", fsm_state="")
        assert result == SILENCE_SHORT_MS


class TestAdaptiveSilenceCompletionProbability:
    """Sentence-completion probability adjusts base duration."""

    def test_incomplete_probability_adds_bonus(self):
        # 1 word → 400ms base; prob=0.1 (<0.3) → +300ms = 700ms
        result = get_adaptive_silence_ms("e", completion_probability=0.1)
        assert result == SILENCE_SHORT_MS + SILENCE_INCOMPLETE_BONUS_MS

    def test_complete_probability_subtracts(self):
        # 1 word → 400ms base; prob=0.95 (>0.8) → -100ms = 300ms (clamped to min)
        result = get_adaptive_silence_ms("sì", completion_probability=0.95)
        # 400 - 100 = 300 == SILENCE_MIN_MS
        assert result == max(SILENCE_MIN_MS, SILENCE_SHORT_MS - SILENCE_COMPLETE_REDUCTION_MS)

    def test_neutral_probability_no_change(self):
        # prob=0.5 → no adjustment
        result = get_adaptive_silence_ms("Marco Rossi", completion_probability=0.5)
        assert result == SILENCE_SHORT_MS  # 2 words → 400ms, no adjustment

    def test_probability_boundary_exactly_03_is_neutral(self):
        # 0.3 is NOT < 0.3, so no bonus
        result = get_adaptive_silence_ms("sì", completion_probability=0.3)
        assert result == SILENCE_SHORT_MS

    def test_probability_boundary_exactly_08_is_neutral(self):
        # 0.8 is NOT > 0.8, so no reduction
        result = get_adaptive_silence_ms("sì", completion_probability=0.8)
        assert result == SILENCE_SHORT_MS

    def test_incomplete_plus_thinking_state_combined(self):
        # 1 word + thinking state → 800ms base; +300ms bonus = 1100ms (< max)
        result = get_adaptive_silence_ms(
            "e", fsm_state="waiting_name", completion_probability=0.1
        )
        assert result == SILENCE_THINKING_STATE_MS + SILENCE_INCOMPLETE_BONUS_MS

    def test_result_never_below_min(self):
        # Even with complete reduction, must stay >= SILENCE_MIN_MS
        result = get_adaptive_silence_ms("sì", completion_probability=1.0)
        assert result >= SILENCE_MIN_MS

    def test_result_never_above_max(self):
        # Long + incomplete — must not exceed SILENCE_MAX_MS
        long = " ".join(["parola"] * 15)
        result = get_adaptive_silence_ms(long, completion_probability=0.0)
        assert result <= SILENCE_MAX_MS


class TestAdaptiveSilenceConfig:
    """Custom config overrides defaults."""

    def test_custom_short_ms(self):
        # Set both short_ms and min_ms so the clamp does not interfere
        cfg = AdaptiveSilenceConfig(short_ms=250, min_ms=200)
        result = get_adaptive_silence_ms("sì", config=cfg)
        assert result == 250

    def test_custom_long_ms(self):
        cfg = AdaptiveSilenceConfig(long_ms=1000)
        long = " ".join(["parola"] * 10)
        result = get_adaptive_silence_ms(long, config=cfg)
        assert result == 1000

    def test_custom_thinking_states(self):
        cfg = AdaptiveSilenceConfig(thinking_states=frozenset({"confirming"}))
        # "waiting_name" is no longer a thinking state with this config
        result = get_adaptive_silence_ms("sì", fsm_state="waiting_name", config=cfg)
        assert result == SILENCE_SHORT_MS  # no lifting
        # "confirming" IS a thinking state now
        result2 = get_adaptive_silence_ms("sì", fsm_state="confirming", config=cfg)
        assert result2 == SILENCE_THINKING_STATE_MS


class TestAdaptiveSilencePublicExport:
    """Verify the public re-export from eou/__init__.py works."""

    def test_eou_package_export(self):
        result = eou_silence("sì")
        assert result == SILENCE_SHORT_MS


# ===========================================================================
# F1-2: Italian Sentence-Completion Heuristics
# ===========================================================================

class TestSentenceCompletionIncomplete:
    """Patterns that should yield probability ~0.2 (incomplete)."""

    def test_ends_with_conjunction_e(self):
        assert sentence_complete_probability("Vorrei un taglio e") == pytest.approx(0.2)

    def test_ends_with_ma(self):
        assert sentence_complete_probability("Verrei domani ma") == pytest.approx(0.2)

    def test_ends_with_oppure(self):
        assert sentence_complete_probability("Taglio o piega oppure") == pytest.approx(0.2)

    def test_ends_with_perche_accented(self):
        assert sentence_complete_probability("Non posso venire perché") == pytest.approx(0.2)

    def test_ends_with_perche_no_accent(self):
        assert sentence_complete_probability("Voglio sapere perche") == pytest.approx(0.2)

    def test_ends_with_quando(self):
        assert sentence_complete_probability("Voglio sapere quando") == pytest.approx(0.2)

    def test_ends_with_dove(self):
        assert sentence_complete_probability("Non so dove") == pytest.approx(0.2)

    def test_trailing_comma(self):
        assert sentence_complete_probability("Vorrei un taglio,") == pytest.approx(0.2)

    def test_trailing_comma_with_space(self):
        assert sentence_complete_probability("Taglio, piega, ") == pytest.approx(0.2)

    def test_ends_with_pero(self):
        assert sentence_complete_probability("Mi piacerebbe però") == pytest.approx(0.2)


class TestSentenceCompletionComplete:
    """Patterns that should yield probability ~0.9 (complete)."""

    def test_grazie(self):
        assert sentence_complete_probability("Grazie") == pytest.approx(0.9)

    def test_grazie_mille(self):
        assert sentence_complete_probability("Grazie mille") == pytest.approx(0.9)

    def test_arrivederci(self):
        assert sentence_complete_probability("Arrivederci") == pytest.approx(0.9)

    def test_si_confermo(self):
        # "sì" / "si" is a polar answer — polar check fires before closer
        assert sentence_complete_probability("Sì, confermo") >= 0.7

    def test_si_standalone(self):
        assert sentence_complete_probability("Sì") == pytest.approx(0.9)

    def test_no_standalone(self):
        assert sentence_complete_probability("No") == pytest.approx(0.9)

    def test_ok(self):
        assert sentence_complete_probability("Ok") == pytest.approx(0.9)

    def test_per_favore(self):
        assert sentence_complete_probability("Alle tre per favore") == pytest.approx(0.9)

    def test_per_piacere(self):
        assert sentence_complete_probability("Domani mattina per piacere") == pytest.approx(0.9)

    def test_ends_with_period(self):
        assert sentence_complete_probability("Vorrei prenotare per domani.") >= 0.9

    def test_ends_with_question_mark(self):
        assert sentence_complete_probability("Avete disponibilità domani?") >= 0.9

    def test_ends_with_exclamation(self):
        assert sentence_complete_probability("Perfetto!") >= 0.9

    def test_ecco(self):
        assert sentence_complete_probability("Ecco") == pytest.approx(0.9)

    def test_benissimo(self):
        assert sentence_complete_probability("Benissimo") == pytest.approx(0.9)


class TestSentenceCompletionNeutral:
    """Cases that fall back to word-count heuristic."""

    def test_four_words_no_signal_returns_07(self):
        result = sentence_complete_probability("Vorrei venire martedì pomeriggio")
        assert result == pytest.approx(0.7)

    def test_five_words_no_signal_returns_07(self):
        result = sentence_complete_probability("Alle dieci e trenta domani")
        assert result == pytest.approx(0.7)

    def test_short_two_words_no_signal_returns_05(self):
        result = sentence_complete_probability("Marco Rossi")
        # 2 words, no clear signal → 0.5
        assert result == pytest.approx(0.5)

    def test_three_words_no_signal_returns_05(self):
        # 3 words < 4 threshold → 0.5
        result = sentence_complete_probability("Lunedì alle tre")
        assert result == pytest.approx(0.5)


class TestSentenceCompletionEdgeCases:
    """Edge cases: empty, single word, very long, accented text."""

    def test_empty_string_returns_05(self):
        assert sentence_complete_probability("") == pytest.approx(0.5)

    def test_whitespace_only_returns_05(self):
        assert sentence_complete_probability("   ") == pytest.approx(0.5)

    def test_single_unknown_word_returns_05(self):
        # "pronto" is not in any list — falls to word_count_short (0.5)
        assert sentence_complete_probability("Pronto") == pytest.approx(0.5)

    def test_very_long_utterance_neutral(self):
        long = " ".join(["vorrei"] * 20)
        result = sentence_complete_probability(long)
        assert result == pytest.approx(0.7)

    def test_accented_characters_handled(self):
        # "perché" with accent should still detect as incomplete
        assert sentence_complete_probability("Non so perché") == pytest.approx(0.2)

    def test_mixed_case_handled(self):
        # "GRAZIE" uppercase
        assert sentence_complete_probability("GRAZIE") == pytest.approx(0.9)

    def test_extra_spaces_handled(self):
        assert sentence_complete_probability("  Sì  ") == pytest.approx(0.9)

    def test_partial_sentence_with_number(self):
        # "prenotare per il 15" — 4 words, neutral
        result = sentence_complete_probability("prenotare per il 15")
        assert result == pytest.approx(0.7)


class TestAnalyzeSentenceCompletion:
    """Tests for the full-detail analyze_sentence_completion function."""

    def test_returns_result_object(self):
        result = analyze_sentence_completion("sì")
        assert hasattr(result, "probability")
        assert hasattr(result, "reason")
        assert hasattr(result, "raw_text")

    def test_reason_for_final_punctuation(self):
        result = analyze_sentence_completion("Domani va bene.")
        assert result.reason == "final_punctuation"
        assert result.probability >= 0.9

    def test_reason_for_open_conjunction(self):
        result = analyze_sentence_completion("Vorrei un taglio e")
        assert "conjunction" in result.reason or "open" in result.reason

    def test_reason_for_trailing_comma(self):
        result = analyze_sentence_completion("Taglio,")
        assert result.reason == "trailing_comma"

    def test_reason_for_polar_answer(self):
        result = analyze_sentence_completion("sì")
        assert result.reason == "polar_answer"

    def test_raw_text_preserved(self):
        text = "Va bene grazie"
        result = analyze_sentence_completion(text)
        assert result.raw_text == text

    def test_probability_in_range(self):
        for text in ["sì", "no", "e", "ma", "per favore", "", "Vorrei prenotare"]:
            result = analyze_sentence_completion(text)
            assert 0.0 <= result.probability <= 1.0, (
                f"Probability out of range for {text!r}: {result.probability}"
            )


class TestSentenceCompletionPublicExport:
    """Verify the public re-export from eou/__init__.py works."""

    def test_eou_package_export(self):
        result = eou_prob("Grazie")
        assert result == pytest.approx(0.9)


# ===========================================================================
# Integration: adaptive silence + sentence completion together
# ===========================================================================

class TestEOUIntegration:
    """Simulate how orchestrator.py would use both modules together."""

    def test_si_confermo_fast_response(self):
        text = "sì, confermo"
        prob = sentence_complete_probability(text)
        silence = get_adaptive_silence_ms(text, completion_probability=prob)
        # Short text (2 tokens) + complete signal → should be fast
        assert silence <= SILENCE_SHORT_MS  # 400ms - 100ms = 300ms

    def test_vorrei_un_taglio_e_wait_longer(self):
        text = "Vorrei un taglio e"
        prob = sentence_complete_probability(text)
        silence = get_adaptive_silence_ms(text, completion_probability=prob)
        # 4 words in medium bucket (600ms) + incomplete bonus (300ms) = 900ms
        assert silence >= 700  # definitely waiting longer

    def test_waiting_name_short_name_thinking(self):
        text = "Mario"
        prob = sentence_complete_probability(text)
        silence = get_adaptive_silence_ms(
            text, fsm_state="waiting_name", completion_probability=prob
        )
        # 1 word → thinking state floors to 800ms; "Mario" is neutral (0.5) → no adj
        assert silence == SILENCE_THINKING_STATE_MS

    def test_long_complete_utterance_normal_timing(self):
        text = "Vorrei prenotare un taglio capelli per martedì prossimo grazie"
        prob = sentence_complete_probability(text)
        # ends with "grazie" → 0.9 (complete) → -100ms
        silence = get_adaptive_silence_ms(text, completion_probability=prob)
        # 9 words → LONG (900ms); -100ms = 800ms
        assert silence == SILENCE_LONG_MS - SILENCE_COMPLETE_REDUCTION_MS

    def test_empty_transcript_with_thinking_state(self):
        # No words yet, but in waiting_name state
        prob = sentence_complete_probability("")
        silence = get_adaptive_silence_ms("", fsm_state="waiting_name", completion_probability=prob)
        # default (700ms) < thinking (800ms) → lifted to 800ms; prob=0.5 → no adj
        assert silence == SILENCE_THINKING_STATE_MS
