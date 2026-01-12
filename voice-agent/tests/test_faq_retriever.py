"""
FLUXION Voice Agent - FAQ Retriever Tests

Test suite for semantic FAQ retrieval (Week 2 Day 1-2):
- Embedding generation
- FAISS index creation
- Similarity search accuracy
- Hybrid keyword boosting

Run with: pytest voice-agent/tests/test_faq_retriever.py -v

Note: These tests require sentence-transformers and faiss-cpu to be installed.
Skip with: pytest voice-agent/tests/test_faq_retriever.py -v -k "not slow"
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Check if dependencies are available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


# Skip all tests if dependencies not available
pytestmark = pytest.mark.skipif(
    not (HAS_NUMPY and HAS_SENTENCE_TRANSFORMERS),
    reason="sentence-transformers or numpy not installed"
)


from faq_retriever import (
    FAISSFAQRetriever,
    HybridFAQRetriever,
    FAQEntry,
    RetrievalResult,
    create_faq_retriever,
)


# =============================================================================
# TEST DATA
# =============================================================================

SAMPLE_FAQS = [
    {
        "id": "faq_001",
        "question": "Quanto costa un taglio donna?",
        "answer": "Il taglio donna costa €35.",
        "category": "prezzi",
        "keywords": ["prezzo", "costo", "taglio", "donna"]
    },
    {
        "id": "faq_002",
        "question": "Quanto costa un taglio uomo?",
        "answer": "Il taglio uomo costa €18.",
        "category": "prezzi",
        "keywords": ["prezzo", "costo", "taglio", "uomo"]
    },
    {
        "id": "faq_003",
        "question": "A che ora aprite?",
        "answer": "Apriamo alle 9:00.",
        "category": "orari",
        "keywords": ["ora", "aprite", "apertura"]
    },
    {
        "id": "faq_004",
        "question": "Siete aperti il lunedì?",
        "answer": "No, il lunedì siamo chiusi.",
        "category": "orari",
        "keywords": ["lunedì", "aperti", "chiusi"]
    },
    {
        "id": "faq_005",
        "question": "Accettate Satispay?",
        "answer": "Sì, accettiamo Satispay.",
        "category": "pagamenti",
        "keywords": ["satispay", "pagamento", "pagare"]
    },
    {
        "id": "faq_006",
        "question": "Quanto costa il colore?",
        "answer": "Il colore costa €55.",
        "category": "prezzi",
        "keywords": ["prezzo", "costo", "colore", "tinta"]
    },
    {
        "id": "faq_007",
        "question": "C'è parcheggio?",
        "answer": "Sì, parcheggio gratuito davanti al salone.",
        "category": "parcheggio",
        "keywords": ["parcheggio", "auto", "parcheggiare"]
    },
    {
        "id": "faq_008",
        "question": "Devo prenotare?",
        "answer": "Consigliamo la prenotazione.",
        "category": "prenotazioni",
        "keywords": ["prenotare", "appuntamento"]
    },
]

# Query -> Expected FAQ ID mappings for accuracy testing
ACCURACY_TEST_CASES = [
    # Exact/near-exact queries
    ("Quanto costa un taglio donna?", "faq_001"),
    ("Quanto costa il taglio uomo?", "faq_002"),
    ("A che ora aprite?", "faq_003"),
    ("Siete aperti lunedì?", "faq_004"),
    ("Accettate Satispay?", "faq_005"),

    # Paraphrased queries
    ("Qual è il prezzo del taglio donna?", "faq_001"),
    ("Quanto devo pagare per un taglio?", "faq_001"),  # Should match taglio donna or uomo
    ("Quando aprite la mattina?", "faq_003"),
    ("Il lunedì siete aperti?", "faq_004"),
    ("Posso pagare con Satispay?", "faq_005"),

    # Semantic variations
    ("Quanto costa farsi i capelli?", "faq_001"),  # Should match taglio
    ("Che orario fate?", "faq_003"),
    ("Avete il parcheggio?", "faq_007"),
    ("Serve prenotazione?", "faq_008"),
]


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def retriever():
    """Create a basic retriever with sample FAQs."""
    r = FAISSFAQRetriever()
    r.add_faqs(SAMPLE_FAQS)
    r.build_index()
    return r


@pytest.fixture
def hybrid_retriever():
    """Create a hybrid retriever with sample FAQs."""
    r = HybridFAQRetriever()
    r.add_faqs(SAMPLE_FAQS)
    r.build_index()
    return r


# =============================================================================
# TEST: BASIC FUNCTIONALITY
# =============================================================================

class TestBasicFunctionality:
    """Test basic retriever functionality."""

    def test_add_faqs(self):
        """Test adding FAQs."""
        r = FAISSFAQRetriever()
        count = r.add_faqs(SAMPLE_FAQS)
        assert count == len(SAMPLE_FAQS)

    def test_add_single_faq(self):
        """Test adding a single FAQ."""
        r = FAISSFAQRetriever()
        faq_id = r.add_faq("Test question?", "Test answer.", category="test")
        assert faq_id.startswith("faq_")

    def test_build_index(self, retriever):
        """Test index building."""
        assert retriever._index_built is True
        assert retriever._embeddings is not None
        assert len(retriever._faqs) == len(SAMPLE_FAQS)

    def test_clear(self, retriever):
        """Test clearing retriever."""
        retriever.clear()
        assert len(retriever._faqs) == 0
        assert retriever._index_built is False

    def test_get_stats(self, retriever):
        """Test statistics."""
        stats = retriever.get_stats()
        assert stats["faq_count"] == len(SAMPLE_FAQS)
        assert stats["index_built"] is True
        assert stats["embedding_dim"] == 384


# =============================================================================
# TEST: RETRIEVAL
# =============================================================================

class TestRetrieval:
    """Test retrieval functionality."""

    def test_retrieve_exact_query(self, retriever):
        """Test retrieval with exact query."""
        results = retriever.retrieve("Quanto costa un taglio donna?", top_k=1)
        assert len(results) >= 1
        assert results[0].faq.id == "faq_001"
        assert results[0].similarity > 0.8

    def test_retrieve_returns_list(self, retriever):
        """Test that retrieve returns a list."""
        results = retriever.retrieve("taglio", top_k=3)
        assert isinstance(results, list)

    def test_retrieve_top_k(self, retriever):
        """Test top_k parameter."""
        results = retriever.retrieve("prezzo", top_k=2)
        assert len(results) <= 2

    def test_retrieve_threshold(self, retriever):
        """Test threshold filtering."""
        # High threshold should return fewer results
        results_high = retriever.retrieve("prezzo", top_k=5, threshold=0.7)
        results_low = retriever.retrieve("prezzo", top_k=5, threshold=0.3)
        assert len(results_low) >= len(results_high)

    def test_retrieve_no_match(self, retriever):
        """Test retrieval with unrelated query."""
        results = retriever.retrieve("xyz123 gibberish text", top_k=1, threshold=0.8)
        assert len(results) == 0

    def test_retrieve_answer(self, retriever):
        """Test retrieve_answer convenience method."""
        result = retriever.retrieve_answer("Quanto costa un taglio donna?")
        assert result is not None
        answer, similarity = result
        assert "€35" in answer
        assert similarity > 0.7

    def test_retrieve_answer_no_match(self, retriever):
        """Test retrieve_answer with no match."""
        result = retriever.retrieve_answer("xyz gibberish", threshold=0.9)
        assert result is None

    def test_category_filter(self, retriever):
        """Test category filtering."""
        results = retriever.retrieve("quanto costa", top_k=5, threshold=0.3, category="prezzi")
        for r in results:
            assert r.faq.category == "prezzi"

    def test_result_structure(self, retriever):
        """Test RetrievalResult structure."""
        results = retriever.retrieve("taglio", top_k=1)
        assert len(results) > 0

        result = results[0]
        assert isinstance(result, RetrievalResult)
        assert isinstance(result.faq, FAQEntry)
        assert 0 <= result.similarity <= 1
        assert result.rank == 1

    def test_result_to_dict(self, retriever):
        """Test RetrievalResult to_dict."""
        results = retriever.retrieve("taglio", top_k=1)
        result_dict = results[0].to_dict()

        assert "id" in result_dict
        assert "question" in result_dict
        assert "answer" in result_dict
        assert "similarity" in result_dict
        assert "rank" in result_dict


# =============================================================================
# TEST: HYBRID RETRIEVER
# =============================================================================

class TestHybridRetriever:
    """Test hybrid retriever with keyword boosting."""

    def test_keyword_boost(self, hybrid_retriever):
        """Test that keywords boost similarity scores."""
        # Query with exact keyword match
        results = hybrid_retriever.retrieve("Satispay", top_k=1, threshold=0.3)
        assert len(results) > 0
        assert results[0].faq.id == "faq_005"

    def test_hybrid_vs_basic(self):
        """Test that hybrid retriever can outperform basic on keyword queries."""
        basic = FAISSFAQRetriever()
        basic.add_faqs(SAMPLE_FAQS)
        basic.build_index()

        hybrid = HybridFAQRetriever()
        hybrid.add_faqs(SAMPLE_FAQS)
        hybrid.build_index()

        # Query with specific keyword
        query = "Satispay"
        basic_results = basic.retrieve(query, top_k=1, threshold=0.3)
        hybrid_results = hybrid.retrieve(query, top_k=1, threshold=0.3)

        if basic_results and hybrid_results:
            # Hybrid should have higher or equal similarity due to keyword boost
            assert hybrid_results[0].similarity >= basic_results[0].similarity * 0.9


# =============================================================================
# TEST: ACCURACY
# =============================================================================

class TestAccuracy:
    """Test retrieval accuracy."""

    @pytest.mark.slow
    def test_accuracy_exact_queries(self, retriever):
        """Test accuracy on exact/near-exact queries."""
        correct = 0
        total = 5  # First 5 test cases are exact

        for query, expected_id in ACCURACY_TEST_CASES[:5]:
            results = retriever.retrieve(query, top_k=1, threshold=0.4)
            if results and results[0].faq.id == expected_id:
                correct += 1
            else:
                print(f"MISS: '{query}' -> expected {expected_id}, got {results[0].faq.id if results else 'None'}")

        accuracy = correct / total
        print(f"\nExact query accuracy: {accuracy*100:.1f}% ({correct}/{total})")
        assert accuracy >= 0.8, f"Accuracy {accuracy*100:.1f}% < 80%"

    @pytest.mark.slow
    def test_accuracy_paraphrased(self, retriever):
        """Test accuracy on paraphrased queries."""
        correct = 0
        total = 5  # Test cases 5-9 are paraphrased

        for query, expected_id in ACCURACY_TEST_CASES[5:10]:
            results = retriever.retrieve(query, top_k=1, threshold=0.4)
            if results and results[0].faq.id == expected_id:
                correct += 1
            else:
                actual = results[0].faq.id if results else 'None'
                print(f"MISS: '{query}' -> expected {expected_id}, got {actual}")

        accuracy = correct / total
        print(f"\nParaphrased accuracy: {accuracy*100:.1f}% ({correct}/{total})")
        # Paraphrased queries are harder, so lower threshold
        assert accuracy >= 0.6, f"Accuracy {accuracy*100:.1f}% < 60%"

    @pytest.mark.slow
    def test_overall_accuracy(self, retriever):
        """Test overall accuracy across all test cases."""
        correct = 0
        total = len(ACCURACY_TEST_CASES)

        for query, expected_id in ACCURACY_TEST_CASES:
            results = retriever.retrieve(query, top_k=1, threshold=0.35)
            if results and results[0].faq.id == expected_id:
                correct += 1

        accuracy = correct / total
        print(f"\nOverall accuracy: {accuracy*100:.1f}% ({correct}/{total})")
        # Target: >70% overall accuracy
        assert accuracy >= 0.7, f"Accuracy {accuracy*100:.1f}% < 70%"


# =============================================================================
# TEST: PERFORMANCE
# =============================================================================

class TestPerformance:
    """Test retrieval performance."""

    @pytest.mark.slow
    def test_query_latency(self, retriever):
        """Test single query latency is <100ms."""
        query = "Quanto costa un taglio?"

        # Warm up
        retriever.retrieve(query, top_k=1)

        # Measure
        start = time.time()
        for _ in range(10):
            retriever.retrieve(query, top_k=3)
        elapsed = (time.time() - start) * 1000 / 10

        print(f"\nAverage query latency: {elapsed:.1f}ms")
        assert elapsed < 100, f"Query latency {elapsed:.1f}ms > 100ms"

    def test_index_build_time(self):
        """Test index build time is reasonable."""
        r = FAISSFAQRetriever()
        r.add_faqs(SAMPLE_FAQS)

        start = time.time()
        r.build_index()
        elapsed = (time.time() - start) * 1000

        print(f"\nIndex build time: {elapsed:.1f}ms")
        # First build includes model loading, so higher threshold
        assert elapsed < 30000, f"Index build time {elapsed:.1f}ms > 30s"


# =============================================================================
# TEST: PERSISTENCE
# =============================================================================

class TestPersistence:
    """Test saving and loading index."""

    @pytest.mark.slow
    def test_save_and_load(self, retriever, tmp_path):
        """Test saving and loading index."""
        save_dir = tmp_path / "faq_index"

        # Save
        retriever.save_index(str(save_dir))
        assert (save_dir / "faqs.json").exists()
        assert (save_dir / "embeddings.npy").exists()

        # Load into new retriever
        new_retriever = FAISSFAQRetriever()
        success = new_retriever.load_index(str(save_dir))
        assert success is True
        assert len(new_retriever._faqs) == len(SAMPLE_FAQS)

        # Verify retrieval works
        results = new_retriever.retrieve("taglio", top_k=1)
        assert len(results) > 0


# =============================================================================
# TEST: FACTORY FUNCTION
# =============================================================================

class TestFactory:
    """Test factory function."""

    def test_create_basic_retriever(self):
        """Test creating basic retriever."""
        r = create_faq_retriever(SAMPLE_FAQS, hybrid=False)
        assert isinstance(r, FAISSFAQRetriever)
        assert not isinstance(r, HybridFAQRetriever)

    def test_create_hybrid_retriever(self):
        """Test creating hybrid retriever."""
        r = create_faq_retriever(SAMPLE_FAQS, hybrid=True)
        assert isinstance(r, HybridFAQRetriever)

    def test_create_empty_retriever(self):
        """Test creating empty retriever."""
        r = create_faq_retriever()
        assert len(r._faqs) == 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-k", "not slow"])
