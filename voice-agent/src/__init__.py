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

from .entity_extractor import (
    extract_date,
    extract_time,
    extract_name,
    extract_service,
    extract_phone,
    extract_email,
    extract_all,
    ExtractedDate,
    ExtractedTime,
    ExtractedName,
    ExtractionResult,
)

from .booking_state_machine import (
    BookingStateMachine,
    BookingState,
    BookingContext,
    StateMachineResult,
)

# FAQ Retriever (optional - requires sentence-transformers and faiss)
try:
    from .faq_retriever import (
        FAISSFAQRetriever,
        HybridFAQRetriever,
        FAQEntry,
        RetrievalResult,
        create_faq_retriever,
    )
    HAS_FAQ_RETRIEVER = True
except ImportError:
    HAS_FAQ_RETRIEVER = False

# FAQ Manager (hybrid keyword + semantic retrieval)
try:
    from .faq_manager import (
        FAQManager,
        FAQConfig,
        FAQMatch,
        create_faq_manager,
        find_keyword_match,
    )
    HAS_FAQ_MANAGER = True
except ImportError:
    HAS_FAQ_MANAGER = False

# Sentiment Analysis (Week 3 Day 1-2)
from .sentiment import (
    SentimentAnalyzer,
    Sentiment,
    FrustrationLevel,
    SentimentResult,
    analyze_sentiment,
    detect_frustration,
    get_analyzer,
)

# Error Recovery (Week 3 Day 3-4)
from .error_recovery import (
    RecoveryManager,
    RetryConfig,
    TimeoutConfig,
    RecoveryResult,
    CircuitBreaker,
    CircuitState,
    ErrorCategory,
    RecoveryAction,
    retry_with_backoff,
    retry_sync_with_backoff,
    with_timeout,
    with_recovery,
    get_fallback_response,
    get_recovery_manager,
)

# Analytics (Week 3 Day 5-6)
from .analytics import (
    ConversationLogger,
    ConversationOutcome,
    ConversationTurn,
    ConversationSession,
    AnalyticsMetrics,
    get_logger,
)

# VoIP (Week 4)
try:
    from .voip import (
        VoIPManager,
        SIPClient,
        SIPConfig,
        RTPTransport,
        CallSession,
        CallState,
        CallDirection,
    )
    HAS_VOIP = True
except ImportError:
    HAS_VOIP = False
