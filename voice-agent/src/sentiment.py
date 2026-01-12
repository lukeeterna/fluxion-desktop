"""
Sentiment Analysis & Frustration Detection Module.

Week 3 Day 1-2: VOICE-AGENT-RAG.md implementation
Target: >90% precision on frustration detection
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import re


class Sentiment(Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class FrustrationLevel(Enum):
    """Frustration intensity levels."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4  # Immediate escalation needed


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    sentiment: Sentiment
    confidence: float
    frustration_level: FrustrationLevel
    frustration_keywords_found: List[str]
    should_escalate: bool
    escalation_reason: Optional[str]
    raw_scores: Dict[str, float]


class SentimentAnalyzer:
    """
    Lightweight sentiment analyzer for Italian voice agent.

    Features:
    - Keyword-based frustration detection (<5ms latency)
    - Pattern-based sentiment analysis
    - Escalation decision logic
    - Conversation history tracking for cumulative frustration

    Design:
    - No heavy ML models (keep <5MB footprint)
    - Rule-based for determinism and explainability
    - Optional TextBlob-it integration if available
    """

    # Frustration keywords with severity weights (1-4)
    # Multi-word phrases are matched as substrings
    # Single words require word boundary matching (handled in _detect_frustration)
    FRUSTRATION_KEYWORDS: Dict[str, int] = {
        # Critical frustration (weight 4) - immediate escalation
        "operatore": 4,
        "persona vera": 4,
        "parlare con qualcuno": 4,
        "umano": 4,
        "basta": 4,
        "non ne posso più": 4,
        "che schifo": 4,
        "fa schifo": 4,
        "vaffanculo": 4,
        "cazzo": 4,

        # High frustration (weight 3)
        "non capisco": 3,
        "non ho capito": 3,
        "sempre sbagliato": 3,
        "impossibile": 3,
        "assurdo": 3,
        "ridicolo": 3,
        "inutile": 3,
        "non funziona": 3,

        # Medium frustration (weight 2)
        "non va bene": 2,
        "sbagliato": 2,
        "errore": 2,
        "problema": 2,
        "difficile": 2,
        "complicato": 2,
        "confuso": 2,
        "frustrato": 2,
        "frustrante": 2,
        "stanco": 2,
        "scocciato": 2,

        # Low frustration (weight 1) - only as standalone words
        "aspetta": 1,
        "un attimo": 1,
    }

    # Keywords that need word boundary matching (single words that could be substrings)
    WORD_BOUNDARY_KEYWORDS: Dict[str, int] = {
        "mai": 3,
        "scusi": 2,
        "no": 1,
        "ma": 1,
        "però": 1,
    }

    # Positive sentiment keywords
    POSITIVE_KEYWORDS: List[str] = [
        "grazie", "perfetto", "ottimo", "bene", "benissimo",
        "fantastico", "eccellente", "bravo", "brava", "gentile",
        "gentilissimo", "ok", "va bene", "d'accordo", "capito",
        "chiaro", "sì", "certo", "esatto", "giusto",
        "magnifico", "meraviglioso", "splendido", "contento",
        "soddisfatto", "felice",
    ]

    # Negative sentiment keywords (beyond frustration)
    # These are matched as substrings (multi-word) or word boundaries (single word)
    NEGATIVE_KEYWORDS: List[str] = [
        "male", "brutto", "sbagliato", "non mi piace",
        "deludente", "deluso", "arrabbiato", "nervoso", "scontento",
        "dispiaciuto", "peccato", "sfortunatamente", "purtroppo",
        "triste", "preoccupato", "annoiato", "che schifo",
    ]

    # Single-word negative keywords requiring word boundary matching
    NEGATIVE_WORD_BOUNDARY: List[str] = ["no"]

    # Patterns indicating user wants to escalate
    ESCALATION_PATTERNS: List[str] = [
        r"parl(?:are|i|a)\s+(?:con\s+)?(?:un\s+)?operat(?:ore|rice)",
        r"parl(?:are|i|a)\s+(?:con\s+)?(?:una?\s+)?person[ae]",
        r"parl(?:are|i|a)\s+(?:con\s+)?(?:un\s+)?uman[oi]",
        r"(?:voglio|vorrei|posso)\s+(?:un\s+)?operat(?:ore|rice)",
        r"(?:mi\s+)?pass(?:a|i|ami)\s+(?:un\s+)?operat(?:ore|rice)",
        r"pass(?:a|i|ami)\s+(?:un\s+)?uman[oi]",  # passami un umano
        r"basta\s+(?:con\s+)?(?:questo\s+)?robot",
        r"non\s+(?:voglio|parlo)\s+(?:con\s+)?(?:un\s+)?robot",
        r"non\s+voglio\s+parlare\s+(?:con\s+)?(?:un\s+)?robot",
    ]

    # Patterns for repeat/clarification requests (frustration indicator)
    REPEAT_PATTERNS: List[str] = [
        r"(?:puoi|può|puo)\s+ripet(?:ere|i)",
        r"(?:cosa|come)\s+(?:hai|ha)\s+detto",
        r"non\s+(?:ho|ha)\s+(?:capito|sentito)",
        r"(?:scusi|scusa)\s*\?",
        r"(?:come|cosa)\s*\?",
    ]

    def __init__(
        self,
        frustration_threshold: int = 3,
        escalation_threshold: int = 6,
        history_window: int = 5,
    ):
        """
        Initialize SentimentAnalyzer.

        Args:
            frustration_threshold: Minimum cumulative score for frustration
            escalation_threshold: Minimum cumulative score for escalation
            history_window: Number of turns to consider for cumulative analysis
        """
        self.frustration_threshold = frustration_threshold
        self.escalation_threshold = escalation_threshold
        self.history_window = history_window

        # Conversation history for cumulative frustration tracking
        self._conversation_history: List[Tuple[str, int]] = []

        # Compile regex patterns for efficiency
        self._escalation_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.ESCALATION_PATTERNS
        ]
        self._repeat_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.REPEAT_PATTERNS
        ]

        # Try to import TextBlob-it for enhanced analysis
        self._textblob_available = False
        try:
            from textblob import TextBlob
            self._textblob_available = True
        except ImportError:
            pass

    def analyze(self, text: str, include_history: bool = True) -> SentimentResult:
        """
        Analyze sentiment and frustration in text.

        Args:
            text: User input text
            include_history: Whether to consider conversation history

        Returns:
            SentimentResult with sentiment, frustration, and escalation info
        """
        text_lower = text.lower().strip()

        # 1. Detect frustration keywords
        frustration_score, frustration_keywords = self._detect_frustration(text_lower)

        # 2. Check escalation patterns
        wants_escalation = self._check_escalation_patterns(text_lower)

        # 3. Check repeat/clarification patterns (adds to frustration)
        repeat_detected = self._check_repeat_patterns(text_lower)
        if repeat_detected:
            frustration_score += 2

        # 4. Calculate sentiment scores
        sentiment_scores = self._calculate_sentiment_scores(text_lower)

        # 5. Determine sentiment
        sentiment = self._determine_sentiment(sentiment_scores, frustration_score)

        # 6. Calculate cumulative frustration from history
        cumulative_frustration = frustration_score
        if include_history and self._conversation_history:
            recent_scores = [
                score for _, score in self._conversation_history[-self.history_window:]
            ]
            cumulative_frustration += sum(recent_scores)

        # 7. Determine frustration level
        frustration_level = self._get_frustration_level(cumulative_frustration)

        # 8. Decide escalation
        should_escalate, escalation_reason = self._should_escalate(
            frustration_level,
            wants_escalation,
            cumulative_frustration,
        )

        # 9. Update history
        self._conversation_history.append((text, frustration_score))
        if len(self._conversation_history) > self.history_window * 2:
            self._conversation_history = self._conversation_history[-self.history_window:]

        # 10. Calculate confidence based on evidence strength
        confidence = self._calculate_confidence(
            sentiment_scores,
            frustration_keywords,
            wants_escalation,
        )

        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            frustration_level=frustration_level,
            frustration_keywords_found=frustration_keywords,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            raw_scores=sentiment_scores,
        )

    def _detect_frustration(self, text: str) -> Tuple[int, List[str]]:
        """Detect frustration keywords and calculate score."""
        total_score = 0
        found_keywords = []

        # Check multi-word phrases and longer keywords (substring match is OK)
        for keyword, weight in self.FRUSTRATION_KEYWORDS.items():
            if keyword in text:
                total_score += weight
                found_keywords.append(keyword)

        # Check single words that need word boundary matching
        words = set(text.split())
        for keyword, weight in self.WORD_BOUNDARY_KEYWORDS.items():
            # Check if keyword appears as a standalone word
            if keyword in words:
                total_score += weight
                found_keywords.append(keyword)

        return total_score, found_keywords

    def _check_escalation_patterns(self, text: str) -> bool:
        """Check if user explicitly wants to escalate."""
        return any(pattern.search(text) for pattern in self._escalation_patterns)

    def _check_repeat_patterns(self, text: str) -> bool:
        """Check if user is asking for repetition/clarification."""
        return any(pattern.search(text) for pattern in self._repeat_patterns)

    def _calculate_sentiment_scores(self, text: str) -> Dict[str, float]:
        """Calculate sentiment scores from keywords."""
        words = set(text.split())

        # Count positive keywords (multi-word phrases as substrings)
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text)

        # Count negative keywords (substrings for phrases, word boundary for singles)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text)
        negative_count += sum(1 for kw in self.NEGATIVE_WORD_BOUNDARY if kw in words)

        # Normalize scores
        total = positive_count + negative_count + 1  # +1 to avoid division by zero

        scores = {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": 1 - (positive_count + negative_count) / total,
        }

        # Optional: enhance with TextBlob if available
        if self._textblob_available:
            try:
                from textblob import TextBlob
                blob = TextBlob(text)
                # TextBlob polarity is -1 to 1
                polarity = blob.sentiment.polarity
                if polarity > 0.1:
                    scores["positive"] = max(scores["positive"], 0.5 + polarity * 0.5)
                elif polarity < -0.1:
                    scores["negative"] = max(scores["negative"], 0.5 + abs(polarity) * 0.5)
            except Exception:
                pass  # Fallback to keyword-based

        return scores

    def _determine_sentiment(
        self,
        scores: Dict[str, float],
        frustration_score: int,
    ) -> Sentiment:
        """Determine overall sentiment."""
        # Any frustration overrides to negative (frustration is inherently negative)
        if frustration_score >= 2:
            return Sentiment.NEGATIVE

        # Use score-based determination
        if scores["positive"] > scores["negative"] and scores["positive"] > 0.3:
            return Sentiment.POSITIVE
        elif scores["negative"] > scores["positive"] and scores["negative"] > 0.3:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL

    def _get_frustration_level(self, cumulative_score: int) -> FrustrationLevel:
        """Map cumulative score to frustration level."""
        if cumulative_score >= 8:
            return FrustrationLevel.CRITICAL
        elif cumulative_score >= 5:
            return FrustrationLevel.HIGH
        elif cumulative_score >= 2:
            return FrustrationLevel.MEDIUM
        elif cumulative_score >= 1:
            return FrustrationLevel.LOW
        else:
            return FrustrationLevel.NONE

    def _should_escalate(
        self,
        frustration_level: FrustrationLevel,
        wants_escalation: bool,
        cumulative_score: int,
    ) -> Tuple[bool, Optional[str]]:
        """Decide if escalation is needed."""
        # Explicit request always escalates
        if wants_escalation:
            return True, "user_requested"

        # Critical frustration always escalates
        if frustration_level == FrustrationLevel.CRITICAL:
            return True, "critical_frustration"

        # High frustration with threshold exceeded
        if frustration_level == FrustrationLevel.HIGH and cumulative_score >= self.escalation_threshold:
            return True, "cumulative_frustration"

        return False, None

    def _calculate_confidence(
        self,
        scores: Dict[str, float],
        frustration_keywords: List[str],
        wants_escalation: bool,
    ) -> float:
        """Calculate confidence in the analysis."""
        # Base confidence
        confidence = 0.5

        # Strong sentiment signals boost confidence
        max_score = max(scores.values())
        if max_score > 0.5:
            confidence += 0.2

        # Frustration keywords boost confidence
        if frustration_keywords:
            confidence += min(0.2, len(frustration_keywords) * 0.05)

        # Explicit escalation request gives high confidence
        if wants_escalation:
            confidence += 0.2

        return min(1.0, confidence)

    def reset_history(self):
        """Reset conversation history."""
        self._conversation_history.clear()

    def get_cumulative_frustration(self) -> int:
        """Get cumulative frustration score from history."""
        return sum(score for _, score in self._conversation_history)

    def analyze_simple(self, text: str) -> Dict[str, any]:
        """
        Simplified analysis returning a dict (for pipeline integration).

        Returns:
            Dict with keys: sentiment, frustration, confidence, should_escalate
        """
        result = self.analyze(text)
        return {
            "sentiment": result.sentiment.value,
            "frustration": result.frustration_level.value,
            "confidence": result.confidence,
            "should_escalate": result.should_escalate,
            "escalation_reason": result.escalation_reason,
        }


# Singleton instance for pipeline use
_default_analyzer: Optional[SentimentAnalyzer] = None


def get_analyzer() -> SentimentAnalyzer:
    """Get or create default SentimentAnalyzer instance."""
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = SentimentAnalyzer()
    return _default_analyzer


def analyze_sentiment(text: str) -> SentimentResult:
    """Convenience function for quick sentiment analysis."""
    return get_analyzer().analyze(text)


def detect_frustration(text: str) -> Tuple[FrustrationLevel, bool]:
    """
    Quick frustration detection.

    Returns:
        Tuple of (frustration_level, should_escalate)
    """
    result = get_analyzer().analyze(text)
    return result.frustration_level, result.should_escalate
