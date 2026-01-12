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
