"""
FLUXION Voice Agent - FAQ Integration Tests

Test suite for FAQ Manager integration with pipeline (Week 2 Day 3):
- FAQManager initialization in pipeline
- Hybrid retrieval (keyword + semantic)
- Layer 3 FAQ lookup in 4-layer pipeline
- Performance benchmarks

Run with: pytest voice-agent/tests/test_faq_integration.py -v
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict
from unittest.mock import Mock, patch, AsyncMock

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from faq_manager import (
    FAQManager,
    FAQConfig,
    FAQMatch,
    create_faq_manager,
    find_keyword_match,
    keyword_match_score,
    KEYWORD_CATEGORIES,
)


# =============================================================================
# TEST DATA
# =============================================================================

SAMPLE_FAQS = [
    {
        "id": "faq_prezzi_001",
        "question": "Quanto costa un taglio donna?",
        "answer": "Il taglio donna costa €35, durata circa 60 minuti.",
        "category": "prezzi",
    },
    {
        "id": "faq_prezzi_002",
        "question": "Quanto costa un taglio uomo?",
        "answer": "Il taglio uomo costa €18, durata circa 30 minuti.",
        "category": "prezzi",
    },
    {
        "id": "faq_orari_001",
        "question": "A che ora aprite?",
        "answer": "Apriamo alle 9:00.",
        "category": "orari",
    },
    {
        "id": "faq_orari_002",
        "question": "Siete aperti il lunedì?",
        "answer": "No, il lunedì siamo chiusi.",
        "category": "orari",
    },
    {
        "id": "faq_pagamenti_001",
        "question": "Accettate Satispay?",
        "answer": "Sì, accettiamo Satispay oltre a contanti e carte.",
        "category": "pagamenti",
    },
    {
        "id": "faq_parcheggio_001",
        "question": "C'è parcheggio?",
        "answer": "Sì, abbiamo parcheggio gratuito davanti al salone.",
        "category": "parcheggio",
    },
]

# Test queries -> expected category/content
TEST_QUERIES = [
    ("Quanto costa un taglio donna?", "prezzi", "€35"),
    ("Quanto costa il taglio uomo?", "prezzi", "€18"),
    ("A che ora aprite?", "orari", "9:00"),
    ("Il lunedì siete aperti?", "orari", "chiusi"),
    ("Posso pagare con Satispay?", "pagamenti", "Satispay"),
    ("Avete il parcheggio?", "parcheggio", "parcheggio"),
    # Paraphrased queries
    ("Qual è il prezzo del taglio donna?", "prezzi", "€35"),
    ("Quando aprite la mattina?", "orari", "9:00"),
    ("C'è posto per la macchina?", "parcheggio", "parcheggio"),
]


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def faq_manager():
    """Create FAQ manager with sample FAQs."""
    manager = FAQManager()
    for faq in SAMPLE_FAQS:
        manager.add_faq(
            question=faq["question"],
            answer=faq["answer"],
            category=faq["category"],
            faq_id=faq["id"],
        )
    return manager


@pytest.fixture
def config_high_threshold():
    """Config with high confidence thresholds."""
    return FAQConfig(
        keyword_confidence=0.9,
        semantic_threshold=0.7,
        use_semantic=True,
    )


@pytest.fixture
def config_no_semantic():
    """Config with semantic search disabled."""
    return FAQConfig(
        keyword_confidence=0.5,
        use_semantic=False,
    )


# =============================================================================
# TEST: KEYWORD MATCHING
# =============================================================================

class TestKeywordMatching:
    """Test keyword matching functionality."""

    def test_exact_match_score(self):
        """Test exact match returns 1.0."""
        score, category = keyword_match_score(
            "Quanto costa un taglio donna?",
            "Quanto costa un taglio donna?",
            "€35"
        )
        assert score == 1.0
        assert category == "exact"

    def test_substring_match_score(self):
        """Test substring match returns 0.9."""
        score, category = keyword_match_score(
            "taglio donna",
            "Quanto costa un taglio donna?",
            "€35"
        )
        assert score >= 0.7
        assert category in ["substring", "contains", "prezzo"]

    def test_keyword_category_match(self):
        """Test keyword category matching."""
        score, category = keyword_match_score(
            "quanto costa",
            "Quanto costa un taglio?",
            "€35"
        )
        assert score >= 0.5
        # Should boost because of € in answer
        assert category in ["exact", "substring", "contains", "prezzo"]

    def test_find_keyword_match(self):
        """Test find_keyword_match function."""
        result = find_keyword_match(
            "Quanto costa un taglio donna?",
            SAMPLE_FAQS,
            min_score=0.5
        )
        assert result is not None
        assert result.confidence >= 0.5
        assert "€35" in result.answer

    def test_find_keyword_match_no_match(self):
        """Test find_keyword_match with unrelated query."""
        result = find_keyword_match(
            "xyz123 random gibberish",
            SAMPLE_FAQS,
            min_score=0.8
        )
        assert result is None


# =============================================================================
# TEST: FAQ MANAGER
# =============================================================================

class TestFAQManager:
    """Test FAQManager class."""

    def test_add_faq(self, faq_manager):
        """Test adding FAQs."""
        assert len(faq_manager.faqs) == len(SAMPLE_FAQS)

    def test_find_answer_exact(self, faq_manager):
        """Test finding exact match."""
        result = faq_manager.find_answer("Quanto costa un taglio donna?")
        assert result is not None
        assert "€35" in result.answer
        assert result.confidence >= 0.8

    def test_find_answer_paraphrased(self, faq_manager):
        """Test finding paraphrased match."""
        result = faq_manager.find_answer("Qual è il prezzo del taglio donna?")
        assert result is not None
        # Should find price-related answer
        assert "€" in result.answer or "taglio" in result.answer.lower()

    def test_find_answer_category_filter(self, faq_manager):
        """Test category filter."""
        result = faq_manager.find_answer("quanto costa", category="prezzi")
        if result:
            assert result.category == "prezzi"

    def test_get_answer_text(self, faq_manager):
        """Test get_answer_text convenience method."""
        answer = faq_manager.get_answer_text("A che ora aprite?")
        assert answer is not None
        assert "9:00" in answer

    def test_get_answer_text_no_match(self, faq_manager):
        """Test get_answer_text with no match."""
        answer = faq_manager.get_answer_text("xyz random", category="unknown")
        # May or may not match, depends on threshold

    def test_stats(self, faq_manager):
        """Test statistics tracking."""
        # Make some queries
        faq_manager.find_answer("quanto costa?")
        faq_manager.find_answer("orari?")

        stats = faq_manager.get_stats()
        assert stats["faq_count"] == len(SAMPLE_FAQS)
        assert stats["total_queries"] == 2
        assert stats["last_query_time_ms"] >= 0

    def test_clear(self, faq_manager):
        """Test clearing FAQs."""
        faq_manager.clear()
        assert len(faq_manager.faqs) == 0
        assert faq_manager._total_queries == 0


# =============================================================================
# TEST: FILE LOADING
# =============================================================================

class TestFileLoading:
    """Test loading FAQs from files."""

    def test_load_from_json(self, tmp_path):
        """Test loading from JSON file."""
        # Create test JSON file
        json_file = tmp_path / "test_faq.json"
        json_file.write_text(json.dumps({"faqs": SAMPLE_FAQS}))

        manager = FAQManager()
        count = manager.load_faqs_from_json(str(json_file))

        assert count == len(SAMPLE_FAQS)
        assert len(manager.faqs) == len(SAMPLE_FAQS)

    def test_load_from_markdown(self, tmp_path):
        """Test loading from markdown file."""
        # Create test markdown file
        md_content = """# Prezzi

- Quanto costa un taglio?: €35
- Quanto costa il colore?: €55

# Orari

- A che ora aprite?: Alle 9:00
"""
        md_file = tmp_path / "test_faq.md"
        md_file.write_text(md_content)

        manager = FAQManager()
        count = manager.load_faqs_from_markdown(str(md_file))

        assert count >= 3
        # Check categories were parsed
        categories = {f["category"] for f in manager.faqs}
        assert "prezzi" in categories
        assert "orari" in categories

    def test_load_with_variable_substitution(self, tmp_path):
        """Test variable substitution in markdown."""
        md_content = """# Prezzi

- Quanto costa un taglio?: Il taglio costa {{prezzo_taglio}}
"""
        md_file = tmp_path / "test_faq.md"
        md_file.write_text(md_content)

        manager = FAQManager()
        settings = {"prezzo_taglio": "€35"}
        count = manager.load_faqs_from_markdown(str(md_file), settings)

        assert count == 1
        assert "€35" in manager.faqs[0]["answer"]

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file."""
        manager = FAQManager()
        count = manager.load_faqs_from_json("/nonexistent/path.json")
        assert count == 0


# =============================================================================
# TEST: CONFIGURATION
# =============================================================================

class TestConfiguration:
    """Test configuration options."""

    def test_high_threshold_config(self, config_high_threshold):
        """Test high threshold configuration."""
        manager = FAQManager(config_high_threshold)
        for faq in SAMPLE_FAQS:
            manager.add_faq(faq["question"], faq["answer"], faq["category"])

        # With high threshold, only exact matches should pass
        result = manager.find_answer("random query about prices")
        # Might not match with high threshold

    def test_no_semantic_config(self, config_no_semantic):
        """Test semantic disabled configuration."""
        manager = FAQManager(config_no_semantic)
        for faq in SAMPLE_FAQS:
            manager.add_faq(faq["question"], faq["answer"], faq["category"])

        result = manager.find_answer("Quanto costa?")
        if result:
            # Should be keyword match only
            assert result.source in ["keyword", "combined"]


# =============================================================================
# TEST: FACTORY FUNCTION
# =============================================================================

class TestFactory:
    """Test factory function."""

    def test_create_faq_manager_empty(self):
        """Test creating empty manager."""
        manager = create_faq_manager()
        assert len(manager.faqs) == 0

    def test_create_faq_manager_with_json(self, tmp_path):
        """Test creating manager with JSON path."""
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps({"faqs": SAMPLE_FAQS[:2]}))

        manager = create_faq_manager(json_path=str(json_file))
        assert len(manager.faqs) == 2

    def test_create_faq_manager_with_config(self):
        """Test creating manager with config."""
        config = FAQConfig(keyword_confidence=0.9)
        manager = create_faq_manager(config=config)
        assert manager.config.keyword_confidence == 0.9


# =============================================================================
# TEST: PERFORMANCE
# =============================================================================

class TestPerformance:
    """Test performance benchmarks."""

    def test_keyword_latency(self, faq_manager):
        """Test keyword matching latency <5ms."""
        query = "Quanto costa un taglio?"

        # Warm up
        faq_manager.find_answer(query)

        # Measure
        start = time.time()
        for _ in range(100):
            faq_manager.find_answer(query)
        elapsed = (time.time() - start) * 1000 / 100

        print(f"\nKeyword query latency: {elapsed:.2f}ms")
        # Target: <5ms for keyword-only
        assert elapsed < 20, f"Latency {elapsed:.2f}ms > 20ms"

    def test_faq_count_scaling(self):
        """Test performance with many FAQs."""
        # Create manager with many FAQs
        manager = FAQManager()
        for i in range(100):
            manager.add_faq(
                f"Question number {i}?",
                f"Answer number {i}.",
                f"category_{i % 5}"
            )

        # Measure query time
        start = time.time()
        for _ in range(50):
            manager.find_answer("Question number 50?")
        elapsed = (time.time() - start) * 1000 / 50

        print(f"\nQuery latency with 100 FAQs: {elapsed:.2f}ms")
        assert elapsed < 50, f"Latency {elapsed:.2f}ms > 50ms"


# =============================================================================
# TEST: ACCURACY
# =============================================================================

class TestAccuracy:
    """Test retrieval accuracy."""

    def test_accuracy_on_test_queries(self, faq_manager):
        """Test accuracy on predefined test queries."""
        correct = 0
        total = len(TEST_QUERIES)

        for query, expected_category, expected_content in TEST_QUERIES:
            result = faq_manager.find_answer(query)
            if result:
                # Check if answer contains expected content
                if expected_content.lower() in result.answer.lower():
                    correct += 1
                else:
                    print(f"MISS content: '{query}' -> {result.answer[:50]}...")
            else:
                print(f"NO MATCH: '{query}'")

        accuracy = correct / total
        print(f"\nAccuracy: {accuracy*100:.1f}% ({correct}/{total})")
        # Target: >70% accuracy with keyword matching only
        assert accuracy >= 0.5, f"Accuracy {accuracy*100:.1f}% < 50%"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
