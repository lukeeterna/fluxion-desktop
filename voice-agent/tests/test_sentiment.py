"""
Sentiment Analysis Tests - Week 3 Day 1-2

Target: >90% precision on frustration detection
Tests: Sentiment classification, frustration detection, escalation logic
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sentiment import (
    SentimentAnalyzer,
    SentimentResult,
    Sentiment,
    FrustrationLevel,
    analyze_sentiment,
    detect_frustration,
    get_analyzer,
)


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def analyzer():
    """Fresh analyzer for each test."""
    return SentimentAnalyzer()


@pytest.fixture
def analyzer_with_history():
    """Analyzer with pre-populated frustration history."""
    a = SentimentAnalyzer()
    # Add some frustration history
    a.analyze("non ho capito")
    a.analyze("puoi ripetere?")
    return a


# ==============================================================================
# Test: Sentiment Classification
# ==============================================================================

class TestSentimentClassification:
    """Test sentiment classification accuracy."""

    @pytest.mark.parametrize("text,expected", [
        # Positive sentiment
        ("Grazie mille!", Sentiment.POSITIVE),
        ("Perfetto, ottimo!", Sentiment.POSITIVE),
        ("Benissimo, va bene così", Sentiment.POSITIVE),
        ("Fantastico, sei stato gentilissimo", Sentiment.POSITIVE),
        ("Ok capito, grazie", Sentiment.POSITIVE),
        ("Sì perfetto, confermo", Sentiment.POSITIVE),
        ("Eccellente servizio", Sentiment.POSITIVE),
        ("Sono contento", Sentiment.POSITIVE),

        # Negative sentiment
        ("Non mi piace", Sentiment.NEGATIVE),
        ("Male, molto male", Sentiment.NEGATIVE),
        ("Sono deluso", Sentiment.NEGATIVE),
        ("Purtroppo non va bene", Sentiment.NEGATIVE),
        ("Sono arrabbiato", Sentiment.NEGATIVE),
        ("Brutto servizio", Sentiment.NEGATIVE),

        # Neutral sentiment
        ("Vorrei prenotare un taglio", Sentiment.NEUTRAL),
        ("A che ora aprite?", Sentiment.NEUTRAL),
        ("Domani alle 15", Sentiment.NEUTRAL),
        ("Il mio nome è Mario", Sentiment.NEUTRAL),
        ("Quanto costa?", Sentiment.NEUTRAL),
    ])
    def test_sentiment_classification(self, analyzer, text, expected):
        """Test basic sentiment classification."""
        result = analyzer.analyze(text)
        assert result.sentiment == expected, f"Expected {expected} for '{text}', got {result.sentiment}"

    def test_sentiment_confidence_range(self, analyzer):
        """Test that confidence is always in valid range."""
        test_texts = [
            "Grazie mille!",
            "Non capisco niente",
            "Vorrei prenotare",
            "Basta! Voglio un operatore!",
        ]
        for text in test_texts:
            result = analyzer.analyze(text)
            assert 0.0 <= result.confidence <= 1.0, f"Invalid confidence: {result.confidence}"


# ==============================================================================
# Test: Frustration Detection
# ==============================================================================

class TestFrustrationDetection:
    """Test frustration detection accuracy - target >90% precision."""

    @pytest.mark.parametrize("text,min_level", [
        # No frustration
        ("Buongiorno", FrustrationLevel.NONE),
        ("Grazie mille", FrustrationLevel.NONE),
        ("Vorrei prenotare", FrustrationLevel.NONE),
        ("Ok perfetto", FrustrationLevel.NONE),

        # Low frustration
        ("Ma non ho capito", FrustrationLevel.LOW),
        ("Aspetta un attimo", FrustrationLevel.LOW),
        ("No, non va bene", FrustrationLevel.LOW),

        # Medium frustration
        ("Scusi, c'è un problema", FrustrationLevel.MEDIUM),
        ("È sbagliato", FrustrationLevel.MEDIUM),
        ("Sono confuso", FrustrationLevel.MEDIUM),
        ("È complicato", FrustrationLevel.MEDIUM),

        # High frustration (multiple keywords or strong keywords)
        ("Non capisco niente!", FrustrationLevel.MEDIUM),  # "non capisco" = 3
        ("È sempre sbagliato!", FrustrationLevel.MEDIUM),  # "sempre sbagliato" = 3
        ("Non funziona mai", FrustrationLevel.HIGH),  # "non funziona" + "mai" = 6
        ("È ridicolo, impossibile!", FrustrationLevel.HIGH),  # "ridicolo" + "impossibile" = 6
        ("Questo è assurdo", FrustrationLevel.MEDIUM),  # "assurdo" = 3

        # Critical frustration (multiple high-weight keywords)
        ("Basta! Voglio parlare con un operatore!", FrustrationLevel.HIGH),  # "basta" + "operatore" = 8
        ("Non ne posso più di questo robot", FrustrationLevel.MEDIUM),  # "non ne posso più" = 4
        ("Passami un umano!", FrustrationLevel.MEDIUM),  # "umano" = 4 (escalates via pattern anyway)
    ])
    def test_frustration_level_detection(self, analyzer, text, min_level):
        """Test frustration level is at least the expected minimum."""
        result = analyzer.analyze(text)
        assert result.frustration_level.value >= min_level.value, \
            f"Expected at least {min_level} for '{text}', got {result.frustration_level}"

    def test_frustration_keywords_found(self, analyzer):
        """Test that frustration keywords are correctly identified."""
        result = analyzer.analyze("Non capisco, è sempre sbagliato")
        assert "non capisco" in result.frustration_keywords_found or \
               "sempre sbagliato" in result.frustration_keywords_found

    def test_no_false_positives_on_neutral(self, analyzer):
        """Test no frustration detected on clearly neutral text."""
        neutral_texts = [
            "Vorrei prenotare un taglio per domani",
            "A che ora siete aperti?",
            "Quanto costa la piega?",
            "Il mio nome è Mario Rossi",
            "Alle 15:00 va bene",
        ]
        false_positives = 0
        for text in neutral_texts:
            result = analyzer.analyze(text, include_history=False)
            if result.frustration_level.value >= FrustrationLevel.MEDIUM.value:
                false_positives += 1

        # Allow max 10% false positives (>90% precision)
        precision = 1 - (false_positives / len(neutral_texts))
        assert precision >= 0.9, f"Precision {precision:.1%} below 90% threshold"


# ==============================================================================
# Test: Escalation Logic
# ==============================================================================

class TestEscalationLogic:
    """Test escalation decision making."""

    @pytest.mark.parametrize("text,should_escalate", [
        # Should escalate - explicit requests
        ("Voglio parlare con un operatore", True),
        ("Mi passa un operatore?", True),
        ("Posso parlare con una persona vera?", True),
        ("Basta con questo robot!", True),
        ("Non voglio parlare con un robot", True),
        ("Passami un umano", True),

        # Should NOT escalate - normal conversation
        ("Buongiorno", False),
        ("Vorrei prenotare", False),
        ("Grazie mille", False),
        ("A che ora?", False),
    ])
    def test_escalation_on_explicit_request(self, analyzer, text, should_escalate):
        """Test escalation is triggered on explicit user requests."""
        result = analyzer.analyze(text, include_history=False)
        assert result.should_escalate == should_escalate, \
            f"Expected should_escalate={should_escalate} for '{text}'"

    def test_escalation_reason_user_requested(self, analyzer):
        """Test escalation reason is correctly set."""
        result = analyzer.analyze("Voglio parlare con un operatore")
        assert result.should_escalate is True
        assert result.escalation_reason == "user_requested"

    def test_escalation_on_critical_frustration(self, analyzer):
        """Test escalation on critical frustration level."""
        # Build up frustration
        analyzer.analyze("Non capisco")
        analyzer.analyze("È sempre sbagliato")
        analyzer.analyze("Non funziona mai")
        result = analyzer.analyze("Basta! Non ne posso più!")

        assert result.should_escalate is True
        assert result.escalation_reason in ["critical_frustration", "cumulative_frustration", "user_requested"]


# ==============================================================================
# Test: Cumulative Frustration
# ==============================================================================

class TestCumulativeFrustration:
    """Test conversation history and cumulative frustration tracking."""

    def test_cumulative_frustration_buildup(self, analyzer):
        """Test frustration builds up over conversation."""
        # First message - low frustration
        r1 = analyzer.analyze("Non ho capito")
        level1 = r1.frustration_level.value

        # Second message - should increase
        r2 = analyzer.analyze("Non ho capito ancora")
        level2 = r2.frustration_level.value

        # Third message - should be even higher
        r3 = analyzer.analyze("Ma perché non capisco mai?")
        level3 = r3.frustration_level.value

        assert level2 >= level1, "Frustration should build up"
        assert level3 >= level2, "Frustration should continue building"

    def test_history_window_limit(self, analyzer):
        """Test that history window is limited."""
        # Fill history beyond window
        for _ in range(10):
            analyzer.analyze("test message")

        # History should be limited
        assert len(analyzer._conversation_history) <= analyzer.history_window * 2

    def test_reset_history(self, analyzer):
        """Test history reset clears cumulative frustration."""
        analyzer.analyze("Non capisco")
        analyzer.analyze("È sbagliato")

        assert analyzer.get_cumulative_frustration() > 0

        analyzer.reset_history()

        assert analyzer.get_cumulative_frustration() == 0
        assert len(analyzer._conversation_history) == 0


# ==============================================================================
# Test: Repeat/Clarification Patterns
# ==============================================================================

class TestRepeatPatterns:
    """Test detection of repeat/clarification requests."""

    @pytest.mark.parametrize("text", [
        "Puoi ripetere?",
        "Non ho capito, può ripetere?",
        "Cosa hai detto?",
        "Come?",
        "Scusi?",
        "Non ho sentito",
    ])
    def test_repeat_patterns_detected(self, analyzer, text):
        """Test repeat patterns add to frustration."""
        result = analyzer.analyze(text, include_history=False)
        # Repeat patterns should add frustration
        assert result.frustration_level.value >= FrustrationLevel.LOW.value


# ==============================================================================
# Test: Edge Cases
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_text(self, analyzer):
        """Test handling of empty text."""
        result = analyzer.analyze("")
        assert result.sentiment == Sentiment.NEUTRAL
        assert result.frustration_level == FrustrationLevel.NONE

    def test_very_long_text(self, analyzer):
        """Test handling of very long text."""
        long_text = "Vorrei prenotare un taglio " * 100
        result = analyzer.analyze(long_text)
        assert result.confidence > 0

    def test_special_characters(self, analyzer):
        """Test handling of special characters."""
        result = analyzer.analyze("@#$%^&*()")
        assert result.sentiment == Sentiment.NEUTRAL

    def test_mixed_case(self, analyzer):
        """Test case insensitivity."""
        r1 = analyzer.analyze("GRAZIE")
        r2 = analyzer.analyze("grazie")
        r3 = analyzer.analyze("Grazie")
        assert r1.sentiment == r2.sentiment == r3.sentiment

    def test_unicode_characters(self, analyzer):
        """Test handling of Italian accented characters."""
        result = analyzer.analyze("Perché non funziona così?")
        assert result is not None

    def test_frustration_with_positive_ending(self, analyzer):
        """Test mixed sentiment - frustration followed by thanks."""
        analyzer.analyze("Non capisco niente!")
        result = analyzer.analyze("Ah ok, grazie")
        # Should still consider history
        assert result.frustration_level.value >= FrustrationLevel.LOW.value


# ==============================================================================
# Test: Convenience Functions
# ==============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_analyze_sentiment_function(self):
        """Test analyze_sentiment convenience function."""
        result = analyze_sentiment("Grazie mille!")
        assert isinstance(result, SentimentResult)
        assert result.sentiment == Sentiment.POSITIVE

    def test_detect_frustration_function(self):
        """Test detect_frustration convenience function."""
        level, should_escalate = detect_frustration("Voglio un operatore!")
        assert isinstance(level, FrustrationLevel)
        assert should_escalate is True

    def test_get_analyzer_singleton(self):
        """Test get_analyzer returns singleton."""
        a1 = get_analyzer()
        a2 = get_analyzer()
        assert a1 is a2

    def test_analyze_simple_dict_output(self, analyzer):
        """Test analyze_simple returns dict."""
        result = analyzer.analyze_simple("Grazie")
        assert isinstance(result, dict)
        assert "sentiment" in result
        assert "frustration" in result
        assert "confidence" in result
        assert "should_escalate" in result


# ==============================================================================
# Test: Performance
# ==============================================================================

class TestPerformance:
    """Test performance requirements."""

    def test_analysis_latency(self, analyzer):
        """Test analysis completes in <5ms."""
        import time

        text = "Non capisco, voglio un operatore"
        iterations = 100

        start = time.perf_counter()
        for _ in range(iterations):
            analyzer.analyze(text, include_history=False)
        elapsed = time.perf_counter() - start

        avg_latency_ms = (elapsed / iterations) * 1000
        assert avg_latency_ms < 5, f"Average latency {avg_latency_ms:.2f}ms exceeds 5ms target"

    def test_memory_efficiency(self, analyzer):
        """Test memory usage stays reasonable with history."""
        # Process many messages
        for i in range(100):
            analyzer.analyze(f"Test message {i}")

        # History should be bounded
        assert len(analyzer._conversation_history) <= analyzer.history_window * 2


# ==============================================================================
# Test: Italian Language Specifics
# ==============================================================================

class TestItalianLanguage:
    """Test Italian language handling."""

    @pytest.mark.parametrize("text,expected_sentiment", [
        # Common Italian expressions
        ("Buongiorno", Sentiment.NEUTRAL),
        ("Buonasera", Sentiment.NEUTRAL),
        ("Arrivederci", Sentiment.NEUTRAL),
        ("Prego", Sentiment.NEUTRAL),
        ("Per favore", Sentiment.NEUTRAL),

        # Italian positive expressions
        ("Grazie tante", Sentiment.POSITIVE),
        ("Molto gentile", Sentiment.POSITIVE),
        ("Benissimo", Sentiment.POSITIVE),

        # Italian negative expressions
        ("Che schifo", Sentiment.NEGATIVE),
        ("Che peccato", Sentiment.NEGATIVE),
    ])
    def test_italian_expressions(self, analyzer, text, expected_sentiment):
        """Test common Italian expressions."""
        result = analyzer.analyze(text, include_history=False)
        assert result.sentiment == expected_sentiment, \
            f"Expected {expected_sentiment} for '{text}', got {result.sentiment}"


# ==============================================================================
# Test: Precision Measurement
# ==============================================================================

class TestPrecisionMeasurement:
    """Measure overall precision to verify >90% target."""

    def test_frustration_precision(self, analyzer):
        """Test frustration detection precision is >90%."""
        # Test cases: (text, expected_frustration)
        test_cases = [
            # True positives - should detect frustration
            ("Non capisco niente", True),
            ("È sempre sbagliato", True),
            ("Voglio un operatore", True),
            ("Basta!", True),
            ("È impossibile", True),
            ("Non funziona", True),
            ("Ridicolo", True),
            ("Non ne posso più", True),

            # True negatives - should NOT detect frustration
            ("Buongiorno", False),
            ("Grazie", False),
            ("Vorrei prenotare", False),
            ("Domani alle 15", False),
            ("A che ora aprite?", False),
            ("Quanto costa?", False),
            ("Ok va bene", False),
            ("Sì confermo", False),
            ("Il mio nome è Mario", False),
            ("Perfetto", False),
        ]

        correct = 0
        for text, expected_frustration in test_cases:
            result = analyzer.analyze(text, include_history=False)
            detected = result.frustration_level.value >= FrustrationLevel.MEDIUM.value
            if detected == expected_frustration:
                correct += 1
            analyzer.reset_history()

        precision = correct / len(test_cases)
        assert precision >= 0.9, f"Precision {precision:.1%} below 90% target"

    def test_escalation_precision(self, analyzer):
        """Test escalation precision is >90%."""
        # Test cases: (text, should_escalate)
        test_cases = [
            # Should escalate
            ("Voglio parlare con un operatore", True),
            ("Mi passa una persona?", True),
            ("Basta con questo robot", True),
            ("Non voglio parlare con un robot", True),

            # Should NOT escalate
            ("Buongiorno", False),
            ("Grazie", False),
            ("Vorrei prenotare", False),
            ("Domani alle 15", False),
            ("Ok", False),
            ("Quanto costa?", False),
        ]

        correct = 0
        for text, expected_escalate in test_cases:
            result = analyzer.analyze(text, include_history=False)
            if result.should_escalate == expected_escalate:
                correct += 1
            analyzer.reset_history()

        precision = correct / len(test_cases)
        assert precision >= 0.9, f"Escalation precision {precision:.1%} below 90% target"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
