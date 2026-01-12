"""
FLUXION Voice Agent - FAQ Manager

Hybrid FAQ retrieval combining keyword matching and semantic search.
Part of the 4-layer RAG pipeline (Layer 3).

Week 2 Day 3: Semantic FAQ Retrieval Integration

Architecture:
    1. Keyword matching (fast, <5ms) - handles exact/near-exact queries
    2. Semantic search (slower, ~50ms) - handles paraphrased queries
    3. Combined scoring for best accuracy

Performance targets:
    - Keyword match: <5ms
    - Semantic fallback: <100ms
    - Overall accuracy: >90%
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import time

# Try to import semantic retriever (optional dependency)
try:
    from .faq_retriever import (
        FAISSFAQRetriever,
        HybridFAQRetriever,
        create_faq_retriever,
        RetrievalResult,
    )
    HAS_SEMANTIC = True
except ImportError:
    try:
        from faq_retriever import (
            FAISSFAQRetriever,
            HybridFAQRetriever,
            create_faq_retriever,
            RetrievalResult,
        )
        HAS_SEMANTIC = True
    except ImportError:
        HAS_SEMANTIC = False
        print("[INFO] Semantic FAQ retrieval not available (missing sentence-transformers)")


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FAQMatch:
    """Result of FAQ lookup."""
    answer: str
    question: str
    confidence: float
    source: str  # "keyword", "semantic", or "combined"
    category: str = ""
    faq_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "question": self.question,
            "confidence": self.confidence,
            "source": self.source,
            "category": self.category,
            "faq_id": self.faq_id,
        }


@dataclass
class FAQConfig:
    """Configuration for FAQ manager."""
    # Thresholds
    keyword_confidence: float = 0.8  # Confidence for keyword matches
    semantic_threshold: float = 0.55  # Minimum semantic similarity
    semantic_high_confidence: float = 0.75  # High-confidence semantic match

    # Behavior
    use_semantic: bool = True  # Enable semantic search
    prefer_keyword: bool = True  # Prefer keyword matches over semantic
    combine_scores: bool = True  # Combine keyword and semantic scores

    # Performance
    max_semantic_results: int = 3
    cache_embeddings: bool = True


# =============================================================================
# KEYWORD MATCHING
# =============================================================================

# Keyword categories for fast matching
KEYWORD_CATEGORIES = {
    "prezzo": {
        "keywords": ["quanto costa", "prezzo", "prezzi", "costo", "costa", "euro", "€"],
        "boost": 2.0,  # Price queries are common, boost them
    },
    "orario": {
        "keywords": ["orario", "orari", "aprite", "chiudete", "aperti", "chiusi",
                     "quando apre", "a che ora", "apertura", "chiusura"],
        "boost": 1.5,
    },
    "servizio": {
        "keywords": ["taglio", "piega", "colore", "tinta", "barba", "trattamento",
                     "cheratina", "servizi", "servizio"],
        "boost": 1.0,
    },
    "pagamento": {
        "keywords": ["pagare", "pagamento", "carta", "contanti", "satispay",
                     "bancomat", "bonifico", "accettate"],
        "boost": 1.5,
    },
    "prenotazione": {
        "keywords": ["prenotare", "prenoto", "prenotazione", "appuntamento",
                     "disdire", "cancellare", "spostare"],
        "boost": 1.0,
    },
    "parcheggio": {
        "keywords": ["parcheggio", "parcheggiare", "posteggio", "auto", "macchina"],
        "boost": 1.0,
    },
    "contatti": {
        "keywords": ["telefono", "numero", "whatsapp", "email", "indirizzo",
                     "dove siete", "come vi trovo"],
        "boost": 1.0,
    },
    "varie": {
        "keywords": ["wifi", "internet", "bambini", "cane", "domicilio", "casa",
                     "prodotti", "shampoo"],
        "boost": 0.8,
    },
}


def keyword_match_score(query: str, faq_question: str, faq_answer: str) -> Tuple[float, str]:
    """
    Calculate keyword match score between query and FAQ.

    Returns:
        Tuple of (score, matched_category)
        Score capped at 1.0, with exact match being highest priority.
    """
    query_lower = query.lower().strip()
    question_lower = faq_question.lower().strip()

    # Exact match - highest priority
    if query_lower == question_lower:
        return 1.0, "exact"

    # Check for word-level exact match (handles punctuation differences)
    query_words = set(query_lower.replace("?", "").replace("!", "").split())
    question_words = set(question_lower.replace("?", "").replace("!", "").split())
    if query_words == question_words:
        return 0.99, "exact_words"

    # Query is substring of question
    if query_lower in question_lower:
        # More specific: longer match = higher score
        ratio = len(query_lower) / len(question_lower)
        return 0.85 + (ratio * 0.1), "substring"

    # Question is substring of query
    if question_lower in query_lower:
        ratio = len(question_lower) / len(query_lower)
        return 0.80 + (ratio * 0.1), "contains"

    # Word overlap scoring (more accurate than keyword categories for specific matches)
    common_words = query_words & question_words
    if common_words:
        # Exclude common words (stop words)
        stop_words = {"un", "una", "il", "la", "lo", "i", "le", "gli", "che", "di", "a", "da", "in", "per", "con"}
        meaningful_common = common_words - stop_words
        meaningful_query = query_words - stop_words
        meaningful_question = question_words - stop_words

        if meaningful_common and meaningful_query and meaningful_question:
            # Jaccard-like similarity
            jaccard = len(meaningful_common) / len(meaningful_query | meaningful_question)
            if jaccard >= 0.5:
                return 0.7 + (jaccard * 0.2), "word_overlap"

    # Keyword category matching (fallback for fuzzy matching)
    best_score = 0.0
    matched_category = ""

    for category, config in KEYWORD_CATEGORIES.items():
        keywords = config["keywords"]
        boost = config["boost"]

        # Count keyword matches in query
        query_matches = sum(1 for kw in keywords if kw in query_lower)

        # Count keyword matches in FAQ question
        faq_matches = sum(1 for kw in keywords if kw in question_lower)

        if query_matches > 0 and faq_matches > 0:
            # Score based on overlap, capped to prevent exceeding direct matches
            overlap = min(query_matches, faq_matches) / max(query_matches, faq_matches)
            score = overlap * boost * 0.5  # Max 0.5 * 2.0 = 1.0 for category match

            # Small boost if answer contains price (€)
            if "€" in faq_answer and any(kw in query_lower for kw in ["prezzo", "costa", "costo"]):
                score = min(score * 1.1, 0.75)  # Cap at 0.75

            if score > best_score:
                best_score = score
                matched_category = category

    return min(best_score, 0.75), matched_category  # Cap category matches at 0.75


def find_keyword_match(
    query: str,
    faqs: List[Dict[str, str]],
    min_score: float = 0.5
) -> Optional[FAQMatch]:
    """
    Find best FAQ match using keyword matching.

    Args:
        query: User query
        faqs: List of FAQ dicts with 'question', 'answer', 'category', 'id' keys
        min_score: Minimum score threshold

    Returns:
        FAQMatch if found, None otherwise
    """
    best_match = None
    best_score = 0.0

    for faq in faqs:
        question = faq.get("question", "")
        answer = faq.get("answer", "")

        score, category = keyword_match_score(query, question, answer)

        if score > best_score and score >= min_score:
            best_score = score
            best_match = FAQMatch(
                answer=answer,
                question=question,
                confidence=score,
                source="keyword",
                category=faq.get("category", category),
                faq_id=faq.get("id", ""),
            )

    return best_match


# =============================================================================
# FAQ MANAGER
# =============================================================================

class FAQManager:
    """
    Hybrid FAQ manager combining keyword and semantic search.

    Usage:
        ```python
        manager = FAQManager()
        manager.load_faqs_from_json("data/faq_salone.json")

        # Or load from markdown
        manager.load_faqs_from_markdown("data/faq_salone.md")

        # Query
        result = manager.find_answer("Quanto costa un taglio?")
        if result:
            print(f"Answer: {result.answer} (confidence: {result.confidence})")
        ```
    """

    def __init__(self, config: Optional[FAQConfig] = None):
        """
        Initialize FAQ manager.

        Args:
            config: Optional configuration
        """
        self.config = config or FAQConfig()
        self.faqs: List[Dict[str, Any]] = []
        self._semantic_retriever = None
        self._semantic_ready = False

        # Stats
        self._keyword_hits = 0
        self._semantic_hits = 0
        self._total_queries = 0
        self._last_query_time_ms = 0

    def load_faqs_from_json(self, path: str) -> int:
        """
        Load FAQs from JSON file.

        Expected format:
        {
            "faqs": [
                {"id": "faq_001", "question": "...", "answer": "...", "category": "..."},
                ...
            ]
        }

        Returns:
            Number of FAQs loaded
        """
        faq_path = Path(path)
        if not faq_path.exists():
            print(f"[WARN] FAQ file not found: {path}")
            return 0

        with open(faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        faqs = data.get("faqs", data) if isinstance(data, dict) else data
        if not isinstance(faqs, list):
            faqs = [faqs]

        self.faqs.extend(faqs)
        self._semantic_ready = False  # Need to rebuild index

        print(f"   [FAQ] Loaded {len(faqs)} FAQs from {path}")
        return len(faqs)

    def load_faqs_from_markdown(self, path: str, settings: Optional[Dict] = None) -> int:
        """
        Load FAQs from markdown file.

        Expected format:
        ```
        # Category Name

        - question: answer
        - another question: another answer
        ```

        Returns:
            Number of FAQs loaded
        """
        faq_path = Path(path)
        if not faq_path.exists():
            print(f"[WARN] FAQ file not found: {path}")
            return 0

        content = faq_path.read_text(encoding="utf-8")

        # Substitute variables if settings provided
        if settings:
            def replace_var(match):
                var_name = match.group(1)
                return settings.get(var_name, f"[{var_name}]")
            content = re.sub(r'\{\{(\w+)\}\}', replace_var, content)

        # Parse markdown
        faqs = []
        current_category = ""
        faq_id = 0

        for line in content.split("\n"):
            line = line.strip()

            # Category header
            if line.startswith("#"):
                current_category = line.lstrip("#").strip().lower()
                continue

            # FAQ entry: "- question: answer"
            if line.startswith("- ") and ":" in line:
                parts = line[2:].split(":", 1)
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()

                    # Skip entries with unresolved variables
                    if "[" in answer:
                        continue

                    faqs.append({
                        "id": f"faq_{faq_id:03d}",
                        "question": question,
                        "answer": answer,
                        "category": current_category,
                    })
                    faq_id += 1

        self.faqs.extend(faqs)
        self._semantic_ready = False

        print(f"   [FAQ] Loaded {len(faqs)} FAQs from {path}")
        return len(faqs)

    def add_faq(
        self,
        question: str,
        answer: str,
        category: str = "",
        faq_id: Optional[str] = None
    ) -> str:
        """
        Add a single FAQ.

        Returns:
            FAQ ID
        """
        faq_id = faq_id or f"faq_{len(self.faqs):03d}"
        self.faqs.append({
            "id": faq_id,
            "question": question,
            "answer": answer,
            "category": category,
        })
        self._semantic_ready = False
        return faq_id

    def _ensure_semantic_ready(self) -> bool:
        """
        Ensure semantic retriever is ready.

        Returns:
            True if semantic search is available
        """
        if not self.config.use_semantic:
            return False

        if not HAS_SEMANTIC:
            return False

        if self._semantic_ready and self._semantic_retriever:
            return True

        # Build semantic index
        if not self.faqs:
            return False

        try:
            self._semantic_retriever = create_faq_retriever(
                self.faqs,
                hybrid=True,
            )
            self._semantic_retriever.build_index()
            self._semantic_ready = True
            return True
        except Exception as e:
            print(f"[WARN] Could not initialize semantic retriever: {e}")
            return False

    def find_answer(
        self,
        query: str,
        category: Optional[str] = None
    ) -> Optional[FAQMatch]:
        """
        Find best answer for a query.

        Uses hybrid approach:
        1. Try keyword matching first (fast)
        2. Fall back to semantic search if no keyword match
        3. Optionally combine scores

        Args:
            query: User query
            category: Optional category filter

        Returns:
            FAQMatch if found, None otherwise
        """
        start_time = time.time()
        self._total_queries += 1

        # Filter by category if specified
        faqs_to_search = self.faqs
        if category:
            faqs_to_search = [f for f in self.faqs if f.get("category") == category]

        # Step 1: Try keyword matching
        keyword_result = find_keyword_match(
            query,
            faqs_to_search,
            min_score=0.5
        )

        if keyword_result and keyword_result.confidence >= self.config.keyword_confidence:
            # High-confidence keyword match - use it
            self._keyword_hits += 1
            self._last_query_time_ms = (time.time() - start_time) * 1000
            print(f"   [FAQ] Keyword match: {keyword_result.confidence:.2f} ({self._last_query_time_ms:.1f}ms)")
            return keyword_result

        # Step 2: Try semantic search
        semantic_result = None
        if self._ensure_semantic_ready():
            try:
                results = self._semantic_retriever.retrieve(
                    query,
                    top_k=self.config.max_semantic_results,
                    threshold=self.config.semantic_threshold,
                    category=category,
                )
                if results:
                    best = results[0]
                    semantic_result = FAQMatch(
                        answer=best.faq.answer,
                        question=best.faq.question,
                        confidence=best.similarity,
                        source="semantic",
                        category=best.faq.category,
                        faq_id=best.faq.id,
                    )
            except Exception as e:
                print(f"[WARN] Semantic search failed: {e}")

        # Step 3: Decide which result to use
        result = None

        if keyword_result and semantic_result:
            # Both have results - combine or choose
            if self.config.combine_scores:
                # Combine scores with weighted average
                combined_confidence = (
                    keyword_result.confidence * 0.4 +
                    semantic_result.confidence * 0.6
                )

                # Use the one with higher individual confidence
                if keyword_result.confidence >= semantic_result.confidence:
                    result = keyword_result
                    result.confidence = combined_confidence
                    result.source = "combined"
                else:
                    result = semantic_result
                    result.confidence = combined_confidence
                    result.source = "combined"
            else:
                # Choose based on preference
                if self.config.prefer_keyword:
                    result = keyword_result
                else:
                    result = semantic_result if semantic_result.confidence > keyword_result.confidence else keyword_result

        elif keyword_result:
            result = keyword_result
            self._keyword_hits += 1

        elif semantic_result:
            result = semantic_result
            self._semantic_hits += 1

        self._last_query_time_ms = (time.time() - start_time) * 1000

        if result:
            print(f"   [FAQ] {result.source} match: {result.confidence:.2f} ({self._last_query_time_ms:.1f}ms)")
        else:
            print(f"   [FAQ] No match for: {query[:50]}... ({self._last_query_time_ms:.1f}ms)")

        return result

    def get_answer_text(self, query: str, category: Optional[str] = None) -> Optional[str]:
        """
        Convenience method to get just the answer text.

        Returns:
            Answer string or None
        """
        result = self.find_answer(query, category)
        return result.answer if result else None

    def get_stats(self) -> Dict[str, Any]:
        """Get FAQ manager statistics."""
        return {
            "faq_count": len(self.faqs),
            "total_queries": self._total_queries,
            "keyword_hits": self._keyword_hits,
            "semantic_hits": self._semantic_hits,
            "keyword_hit_rate": self._keyword_hits / max(1, self._total_queries),
            "semantic_available": HAS_SEMANTIC and self._semantic_ready,
            "last_query_time_ms": self._last_query_time_ms,
        }

    def clear(self):
        """Clear all FAQs."""
        self.faqs = []
        self._semantic_retriever = None
        self._semantic_ready = False
        self._keyword_hits = 0
        self._semantic_hits = 0
        self._total_queries = 0


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_faq_manager(
    json_path: Optional[str] = None,
    markdown_path: Optional[str] = None,
    settings: Optional[Dict] = None,
    config: Optional[FAQConfig] = None
) -> FAQManager:
    """
    Factory function to create configured FAQ manager.

    Args:
        json_path: Path to JSON FAQ file
        markdown_path: Path to markdown FAQ file
        settings: Variable substitutions for markdown
        config: FAQ configuration

    Returns:
        Configured FAQManager
    """
    manager = FAQManager(config)

    if json_path:
        manager.load_faqs_from_json(json_path)

    if markdown_path:
        manager.load_faqs_from_markdown(markdown_path, settings)

    return manager


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

def find_faq_answer_hybrid(
    text: str,
    qa_dict: Dict[str, str],
    faqs: Optional[List[Dict]] = None,
    semantic_retriever: Optional[Any] = None
) -> Optional[str]:
    """
    Legacy-compatible function for hybrid FAQ lookup.

    Can be used as drop-in replacement for the old find_faq_answer function.

    Args:
        text: User query
        qa_dict: Legacy question->answer dictionary
        faqs: Optional list of FAQ dicts for semantic search
        semantic_retriever: Optional pre-configured semantic retriever

    Returns:
        Answer string or None
    """
    # Convert qa_dict to FAQ list if needed
    if faqs is None and qa_dict:
        faqs = [
            {"id": f"faq_{i}", "question": q, "answer": a}
            for i, (q, a) in enumerate(qa_dict.items())
        ]

    if not faqs:
        return None

    # Use FAQManager for lookup
    manager = FAQManager()
    manager.faqs = faqs

    if semantic_retriever:
        manager._semantic_retriever = semantic_retriever
        manager._semantic_ready = True

    result = manager.find_answer(text)
    return result.answer if result else None


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    print("=== FAQ Manager Test ===\n")

    # Create test FAQs
    test_faqs = [
        {"id": "001", "question": "Quanto costa un taglio donna?", "answer": "€35", "category": "prezzi"},
        {"id": "002", "question": "A che ora aprite?", "answer": "Alle 9:00", "category": "orari"},
        {"id": "003", "question": "Accettate Satispay?", "answer": "Sì, accettiamo Satispay", "category": "pagamenti"},
        {"id": "004", "question": "C'è parcheggio?", "answer": "Sì, parcheggio gratuito", "category": "servizi"},
        {"id": "005", "question": "Devo prenotare?", "answer": "Consigliamo la prenotazione", "category": "prenotazioni"},
    ]

    # Create manager
    manager = FAQManager()
    for faq in test_faqs:
        manager.add_faq(faq["question"], faq["answer"], faq["category"], faq["id"])

    # Test queries
    test_queries = [
        "Quanto costa un taglio?",
        "Qual è il prezzo del taglio donna?",
        "Che orario fate?",
        "Posso pagare con Satispay?",
        "Avete il parcheggio?",
        "Serve prenotazione?",
    ]

    print("--- Test Queries ---\n")
    for query in test_queries:
        result = manager.find_answer(query)
        if result:
            print(f"Q: {query}")
            print(f"A: {result.answer} [{result.source}, {result.confidence:.2f}]")
            print()
        else:
            print(f"Q: {query}")
            print("A: No match\n")

    # Stats
    print("--- Stats ---")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
