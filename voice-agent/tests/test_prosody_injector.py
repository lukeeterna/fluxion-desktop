"""Tests for ProsodyInjector — text-level prosody for TTS."""
import sys
import os
import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from prosody_injector import ProsodyInjector


@pytest.fixture
def pi():
    return ProsodyInjector()


class TestBreathingPauses:
    def test_long_sentence_gets_pause(self, pi):
        """Sentences >60 chars should get a comma at a logical break."""
        text = "Ho trovato uno slot disponibile per lei domani dopo le quindici e trenta"
        result = pi.inject(text)
        # Should have more commas than original (which has zero)
        assert result.count(',') > text.count(',')

    def test_short_sentence_unchanged(self, pi):
        """Short sentences (<30 chars) pass through unchanged."""
        text = "Va bene, confermo."
        result = pi.inject(text)
        assert result == text

    def test_medium_sentence_no_forced_break(self, pi):
        """Sentences 30-60 chars should not get forced breathing pauses."""
        text = "Perfetto, ho registrato la sua email qui."
        result = pi.inject(text, context="default")
        # No extra commas added (sentence is under 60 chars)
        assert result.count(',') == text.count(',')


class TestListRhythm:
    def test_adds_commas_to_bare_list(self, pi):
        """'taglio piega e colore' should become 'taglio, piega, e colore'."""
        text = "Offriamo taglio piega e colore per tutti i clienti"
        result = pi.inject(text)
        assert "taglio, piega, e colore" in result

    def test_existing_commas_preserved(self, pi):
        """Already comma-separated lists should not get doubled."""
        text = "Offriamo taglio, piega e colore per tutti i clienti"
        result = pi.inject(text)
        assert ",," not in result

    def test_short_words_not_listed(self, pi):
        """Very short words (< 3 chars) should not be treated as list items."""
        text = "Il mio amico ha un cane e un gatto a casa sua"
        result = pi.inject(text)
        # "un" is 2 chars — should not add commas around it
        assert "un, cane" not in result


class TestThinkingPause:
    def test_confirmation_adds_ellipsis_before_date(self, pi):
        """In confirmation context, dates get a thinking pause."""
        text = "Perfetto, allora la prenoto per mercoledi alle 15"
        result = pi.inject(text, context="confirmation")
        assert "..." in result

    def test_info_context_adds_ellipsis(self, pi):
        """Info context also gets thinking pauses."""
        text = "Il prossimo slot libero sarebbe domani alle 10"
        result = pi.inject(text, context="info")
        assert "..." in result

    def test_default_context_no_ellipsis(self, pi):
        """Default context should NOT add thinking pauses."""
        text = "Il prossimo slot libero sarebbe domani alle dieci"
        result = pi.inject(text, context="default")
        assert "..." not in result

    def test_existing_ellipsis_not_doubled(self, pi):
        """If text already has ellipsis, don't add another."""
        text = "Vediamo... il prossimo slot sarebbe mercoledi alle 15 del mattino"
        result = pi.inject(text, context="confirmation")
        assert result.count("...") == 1


class TestContextPassthrough:
    def test_greeting_not_modified(self, pi):
        """Greetings pass through unchanged."""
        text = "Buongiorno, sono Sara di Salone Bella Vita! Come posso aiutarla?"
        result = pi.inject(text, context="greeting")
        assert result == text

    def test_question_not_modified(self, pi):
        """Questions pass through unchanged."""
        text = "Per quale giorno desidera prenotare l'appuntamento?"
        result = pi.inject(text, context="question")
        assert result == text


class TestEdgeCases:
    def test_empty_string_safe(self, pi):
        """Empty input returns empty output."""
        assert pi.inject("") == ""
        assert pi.inject("   ") == "   "

    def test_none_like_empty(self, pi):
        """None-ish values are safe."""
        assert pi.inject("") == ""

    def test_no_double_commas(self, pi):
        """Never produce double commas."""
        text = "Il servizio include taglio, piega, e colore per il trattamento completo e finale"
        result = pi.inject(text)
        assert ",," not in result
        assert ", ," not in result

    def test_no_double_periods(self, pi):
        """Never produce double periods (except ellipsis)."""
        text = "Abbiamo verificato la disponibilita. Il posto e confermato per lei."
        result = pi.inject(text)
        # No ".." that isn't part of "..."
        import re
        non_ellipsis_double = re.findall(r'(?<!\.)\.\.(?!\.)', result)
        assert len(non_ellipsis_double) == 0

    def test_semantic_content_preserved(self, pi):
        """Words must not be changed, only punctuation added."""
        text = "Perfetto allora la prenoto per un taglio piega e colore con Marco"
        result = pi.inject(text, context="confirmation")
        # Strip all punctuation and compare words
        import re
        words_orig = re.findall(r'\w+', text)
        words_result = re.findall(r'\w+', result)
        assert words_orig == words_result


class TestConfirmationIntegration:
    def test_full_confirmation_natural(self, pi):
        """A typical confirmation response should sound natural."""
        text = "Allora taglio con Marco mercoledi alle 15. Tutto giusto?"
        result = pi.inject(text, context="confirmation")
        # Should have ellipsis before date
        assert "..." in result
        # Original words preserved
        assert "Marco" in result
        assert "Tutto giusto?" in result
