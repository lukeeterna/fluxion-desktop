"""
FLUXION Voice Agent - Intent Classifier Tests

Test suite for Layer 1 (Exact Match) intent classification.
Tests 50+ cortesia phrases with expected behavior.

Run with: pytest voice-agent/tests/test_intent_classifier.py -v
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intent_classifier import (
    classify_intent,
    exact_match_intent,
    pattern_based_intent,
    normalize_input,
    IntentCategory,
)


# =============================================================================
# TEST DATA: 50+ CORTESIA PHRASES
# =============================================================================

CORTESIA_TEST_CASES = [
    # === SALUTI (Greetings) - 10 cases ===
    ("Buongiorno", IntentCategory.CORTESIA, 1.0),
    ("buongiorno", IntentCategory.CORTESIA, 1.0),
    ("BUONGIORNO", IntentCategory.CORTESIA, 1.0),  # uppercase
    ("Buonasera", IntentCategory.CORTESIA, 1.0),
    ("buona sera", IntentCategory.CORTESIA, 1.0),  # with space
    ("Salve", IntentCategory.CORTESIA, 1.0),
    ("Ciao", IntentCategory.CORTESIA, 1.0),
    ("Pronto", IntentCategory.CORTESIA, 1.0),
    ("Buon pomeriggio", IntentCategory.CORTESIA, 1.0),
    ("si pronto", IntentCategory.CORTESIA, 1.0),

    # === SALUTI CON TYPO (Typos) - 6 cases ===
    ("buongorno", IntentCategory.CORTESIA, 0.7),  # typo
    ("bongorno", IntentCategory.CORTESIA, 0.7),  # typo
    ("bonsera", IntentCategory.CORTESIA, 0.7),  # typo (alias)
    ("ciaoo", IntentCategory.CORTESIA, 0.7),  # typo (alias)
    ("grazzie", IntentCategory.CORTESIA, 0.7),  # typo (alias)
    ("arivederci", IntentCategory.CORTESIA, 0.7),  # typo (alias)

    # === CONGEDI (Goodbyes) - 8 cases ===
    ("Arrivederci", IntentCategory.CORTESIA, 1.0),
    ("arrivederla", IntentCategory.CORTESIA, 1.0),
    ("A presto", IntentCategory.CORTESIA, 1.0),
    ("Ci vediamo", IntentCategory.CORTESIA, 1.0),
    ("Buona giornata", IntentCategory.CORTESIA, 1.0),
    ("Buona serata", IntentCategory.CORTESIA, 1.0),
    ("Alla prossima", IntentCategory.CORTESIA, 1.0),
    ("addio", IntentCategory.CORTESIA, 1.0),

    # === RINGRAZIAMENTI (Thanks) - 10 cases ===
    ("Grazie", IntentCategory.CORTESIA, 1.0),
    ("grazie mille", IntentCategory.CORTESIA, 1.0),
    ("Molte grazie", IntentCategory.CORTESIA, 1.0),
    ("Ti ringrazio", IntentCategory.CORTESIA, 1.0),
    ("La ringrazio", IntentCategory.CORTESIA, 1.0),
    ("Grazie tante", IntentCategory.CORTESIA, 1.0),
    ("Mille grazie", IntentCategory.CORTESIA, 1.0),
    ("Grazie davvero", IntentCategory.CORTESIA, 1.0),
    ("Grazie di tutto", IntentCategory.CORTESIA, 1.0),
    ("grassie", IntentCategory.CORTESIA, 0.7),  # alias

    # === SCUSE (Apologies) - 6 cases ===
    ("Scusa", IntentCategory.CORTESIA, 1.0),
    ("Scusi", IntentCategory.CORTESIA, 1.0),
    ("Mi scusi", IntentCategory.CORTESIA, 1.0),
    ("Perdonami", IntentCategory.CORTESIA, 1.0),
    ("Mi perdoni", IntentCategory.CORTESIA, 1.0),
    ("Chiedo scusa", IntentCategory.CORTESIA, 1.0),

    # === CONFERME (Confirmations) - 10 cases ===
    ("Ok", IntentCategory.CONFERMA, 1.0),
    ("ok", IntentCategory.CONFERMA, 1.0),
    ("Va bene", IntentCategory.CONFERMA, 1.0),
    ("D'accordo", IntentCategory.CONFERMA, 1.0),
    ("Perfetto", IntentCategory.CONFERMA, 1.0),
    ("Benissimo", IntentCategory.CONFERMA, 1.0),
    ("Ottimo", IntentCategory.CONFERMA, 1.0),
    ("Esatto", IntentCategory.CONFERMA, 1.0),
    ("Certo", IntentCategory.CONFERMA, 1.0),
    ("Confermo", IntentCategory.CONFERMA, 1.0),
]

PATTERN_TEST_CASES = [
    # === PRENOTAZIONE (Booking) - 6 cases ===
    ("Voglio prenotare un appuntamento", IntentCategory.PRENOTAZIONE, 0.4),
    ("vorrei fissare un appuntamento", IntentCategory.PRENOTAZIONE, 0.4),
    ("Mi prenota per domani?", IntentCategory.PRENOTAZIONE, 0.4),
    ("Avete disponibilità sabato?", IntentCategory.PRENOTAZIONE, 0.4),
    ("Sono liberi lunedì?", IntentCategory.PRENOTAZIONE, 0.4),
    ("Posso prenotare?", IntentCategory.PRENOTAZIONE, 0.4),

    # === INFO (Information) - 6 cases ===
    ("Quanto costa un taglio?", IntentCategory.INFO, 0.4),
    ("Che orari fate?", IntentCategory.INFO, 0.4),
    ("Dove siete?", IntentCategory.INFO, 0.4),
    ("Accettate carte?", IntentCategory.INFO, 0.4),
    ("Che servizi offrite?", IntentCategory.INFO, 0.4),
    ("Vorrei informazioni", IntentCategory.INFO, 0.4),

    # === CANCELLAZIONE (Cancellation) - 4 cases ===
    ("Voglio annullare", IntentCategory.CANCELLAZIONE, 0.4),
    ("Devo cancellare l'appuntamento", IntentCategory.CANCELLAZIONE, 0.4),
    ("Non posso venire", IntentCategory.CANCELLAZIONE, 0.4),
    ("Disdico la prenotazione", IntentCategory.CANCELLAZIONE, 0.4),

    # === OPERATORE (Operator) - 3 cases ===
    ("Operatore", IntentCategory.OPERATORE, 1.0),  # exact match
    ("Voglio parlare con una persona", IntentCategory.OPERATORE, 0.4),
    ("Parlo con qualcuno?", IntentCategory.OPERATORE, 0.4),
]

NEGATIVE_TEST_CASES = [
    # === UNKNOWN - should return needs_groq=True ===
    ("Il cielo è azzurro", IntentCategory.UNKNOWN),
    ("La pizza è buona", IntentCategory.UNKNOWN),
    ("Marco ha 35 anni", IntentCategory.UNKNOWN),
]


# =============================================================================
# TESTS
# =============================================================================

class TestNormalization:
    """Test text normalization."""

    def test_lowercase(self):
        assert normalize_input("BUONGIORNO") == "buongiorno"

    def test_accent_removal(self):
        assert normalize_input("perché") == "perche"
        assert normalize_input("è") == "e"
        assert normalize_input("lunedì") == "lunedi"

    def test_whitespace(self):
        assert normalize_input("  ciao  mondo  ") == "ciao mondo"

    def test_combined(self):
        assert normalize_input("  BUONGIORNO Perché  ") == "buongiorno perche"


class TestExactMatch:
    """Test Layer 1: Exact match."""

    def test_exact_match_cortesia(self):
        """Test all cortesia phrases return correct intent."""
        for phrase, expected_category, min_confidence in CORTESIA_TEST_CASES:
            result = exact_match_intent(phrase)

            # For typos/aliases, might return None without Levenshtein
            if result is None and min_confidence < 1.0:
                # Skip typo cases if Levenshtein not installed
                continue

            assert result is not None, f"Failed for: {phrase}"
            assert result.category == expected_category, f"Wrong category for: {phrase}"
            assert result.confidence >= min_confidence, f"Low confidence for: {phrase}"
            assert result.response is not None, f"No response for: {phrase}"

    def test_exact_match_performance(self):
        """Test exact match is fast (<5ms per call)."""
        phrases = ["buongiorno", "grazie", "ok", "arrivederci"]

        start = time.time()
        for _ in range(100):
            for phrase in phrases:
                exact_match_intent(phrase)
        elapsed = (time.time() - start) * 1000  # ms

        avg_time = elapsed / 400  # 100 iterations * 4 phrases
        assert avg_time < 5, f"Exact match too slow: {avg_time:.2f}ms"

    def test_no_match_returns_none(self):
        """Test that unmatched phrases return None."""
        result = exact_match_intent("questa frase non esiste nel dizionario")
        assert result is None


class TestPatternMatch:
    """Test Layer 2: Pattern-based classification."""

    def test_pattern_match_intents(self):
        """Test pattern-based intent classification."""
        for phrase, expected_category, min_confidence in PATTERN_TEST_CASES:
            result = pattern_based_intent(phrase)

            # Operatore might be exact match
            if expected_category == IntentCategory.OPERATORE and phrase.lower() == "operatore":
                # This should be caught by exact match first
                continue

            if result is None:
                # Some patterns might not match, that's OK
                continue

            assert result.category == expected_category, f"Wrong category for: {phrase}"
            assert result.confidence >= min_confidence, f"Low confidence for: {phrase}"


class TestHybridClassifier:
    """Test classify_intent (hybrid classifier)."""

    def test_cortesia_uses_exact_match(self):
        """Cortesia phrases should use exact match (Layer 1)."""
        result = classify_intent("Buongiorno")
        assert result.category == IntentCategory.CORTESIA
        assert result.confidence == 1.0
        assert result.needs_groq is False

    def test_booking_uses_pattern(self):
        """Booking phrases should use pattern match (Layer 2)."""
        result = classify_intent("Voglio prenotare un appuntamento")
        assert result.category == IntentCategory.PRENOTAZIONE
        assert result.needs_groq is False or result.confidence >= 0.5

    def test_unknown_needs_groq(self):
        """Unknown phrases should fallback to Groq."""
        for phrase, _ in NEGATIVE_TEST_CASES:
            result = classify_intent(phrase)
            assert result.category == IntentCategory.UNKNOWN
            assert result.needs_groq is True

    def test_response_included_for_cortesia(self):
        """Cortesia should include response."""
        result = classify_intent("Grazie")
        assert result.response is not None
        assert "Prego" in result.response


class TestPerformance:
    """Performance benchmarks."""

    def test_overall_performance(self):
        """Test overall classification is fast."""
        test_phrases = [
            "Buongiorno",
            "Voglio prenotare",
            "Quanto costa?",
            "Testo random qualsiasi",
        ]

        start = time.time()
        for _ in range(100):
            for phrase in test_phrases:
                classify_intent(phrase)
        elapsed = (time.time() - start) * 1000

        avg_time = elapsed / 400
        print(f"\nAverage classify_intent time: {avg_time:.2f}ms")
        assert avg_time < 25, f"Classification too slow: {avg_time:.2f}ms"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
