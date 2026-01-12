"""
FLUXION Voice Agent - Semantic FAQ Retriever

Enterprise FAQ retrieval using FAISS + sentence-transformers.
Part of the 4-layer RAG pipeline (Layer 3).

Week 2 Day 1-2: Embeddings Setup

Features:
- Multilingual embeddings (Italian + German support)
- FAISS vector store for fast similarity search
- Threshold-based filtering
- Lazy model loading for fast startup
- Cache-friendly design

Performance targets:
- Model loading: <5s (first query)
- Embedding generation: <50ms per query
- Similarity search: <30ms for 1000 docs
- Total retrieval: <100ms
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import time

# Lazy imports for optional dependencies
_sentence_transformer = None
_faiss = None
_np = None


def _lazy_import():
    """Lazy import heavy dependencies."""
    global _sentence_transformer, _faiss, _np

    if _np is None:
        import numpy as np
        _np = np

    if _faiss is None:
        try:
            import faiss
            _faiss = faiss
        except ImportError:
            print("[WARN] faiss not installed, using fallback similarity search")
            _faiss = False

    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformer = SentenceTransformer
        except ImportError:
            print("[WARN] sentence-transformers not installed")
            _sentence_transformer = False


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FAQEntry:
    """Single FAQ entry."""
    id: str
    question: str
    answer: str
    category: str = ""
    keywords: List[str] = field(default_factory=list)
    embedding: Optional[Any] = None  # numpy array

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without embedding)."""
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "keywords": self.keywords,
        }


@dataclass
class RetrievalResult:
    """Result of a retrieval query."""
    faq: FAQEntry
    similarity: float
    rank: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.faq.id,
            "question": self.faq.question,
            "answer": self.faq.answer,
            "category": self.faq.category,
            "similarity": round(self.similarity, 4),
            "rank": self.rank,
        }


# =============================================================================
# FAQ RETRIEVER
# =============================================================================

class FAISSFAQRetriever:
    """
    Semantic FAQ retriever using FAISS + sentence-transformers.

    Uses paraphrase-multilingual-MiniLM-L12-v2 for Italian support.
    Embedding dimension: 384.

    Example:
        ```python
        retriever = FAISSFAQRetriever()
        retriever.add_faqs([
            {"id": "faq_001", "question": "Quanto costa un taglio?", "answer": "€25"},
            {"id": "faq_002", "question": "Siete aperti il lunedì?", "answer": "Sì, 9-18"},
        ])
        results = retriever.retrieve("Qual è il prezzo del taglio?", top_k=3)
        ```
    """

    # Default model - multilingual with Italian support
    DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM = 384

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        cache_dir: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize retriever.

        Args:
            model_name: Sentence transformer model name
            cache_dir: Directory for caching embeddings
            device: Device for model inference ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.device = device
        self.cache_dir = Path(cache_dir) if cache_dir else None

        # Lazy-loaded components
        self._model = None
        self._index = None
        self._faqs: List[FAQEntry] = []
        self._embeddings = None
        self._index_built = False

        # Performance tracking
        self._load_time_ms = 0
        self._last_query_time_ms = 0

    @property
    def model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            _lazy_import()
            if _sentence_transformer is False:
                raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")

            start = time.time()
            self._model = _sentence_transformer(self.model_name, device=self.device)
            self._load_time_ms = (time.time() - start) * 1000
            print(f"   [EMBEDDINGS] Model loaded in {self._load_time_ms:.0f}ms")

        return self._model

    def add_faqs(self, faqs: List[Dict[str, Any]]) -> int:
        """
        Add FAQs to the retriever.

        Args:
            faqs: List of FAQ dictionaries with 'id', 'question', 'answer' keys

        Returns:
            Number of FAQs added
        """
        _lazy_import()

        added = 0
        for faq_dict in faqs:
            faq = FAQEntry(
                id=faq_dict.get("id", f"faq_{len(self._faqs)}"),
                question=faq_dict["question"],
                answer=faq_dict["answer"],
                category=faq_dict.get("category", ""),
                keywords=faq_dict.get("keywords", []),
            )
            self._faqs.append(faq)
            added += 1

        # Mark index as needing rebuild
        self._index_built = False
        return added

    def add_faq(self, question: str, answer: str, category: str = "", faq_id: Optional[str] = None) -> str:
        """
        Add a single FAQ.

        Args:
            question: FAQ question
            answer: FAQ answer
            category: Optional category
            faq_id: Optional ID (auto-generated if not provided)

        Returns:
            FAQ ID
        """
        faq_id = faq_id or f"faq_{len(self._faqs):03d}"
        self._faqs.append(FAQEntry(
            id=faq_id,
            question=question,
            answer=answer,
            category=category,
        ))
        self._index_built = False
        return faq_id

    def build_index(self, force: bool = False) -> None:
        """
        Build FAISS index from current FAQs.

        Args:
            force: Force rebuild even if index exists
        """
        if self._index_built and not force:
            return

        if not self._faqs:
            print("[WARN] No FAQs to index")
            return

        _lazy_import()

        # Generate embeddings for all questions
        questions = [faq.question for faq in self._faqs]

        start = time.time()
        embeddings = self.model.encode(
            questions,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        encode_time = (time.time() - start) * 1000

        # Store embeddings
        self._embeddings = embeddings.astype(_np.float32)

        # Create FAISS index
        if _faiss and _faiss is not False:
            dimension = embeddings.shape[1]
            self._index = _faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)

            # Normalize embeddings for cosine similarity
            _faiss.normalize_L2(self._embeddings)
            self._index.add(self._embeddings)
        else:
            # Fallback: manual cosine similarity
            self._index = None
            # Normalize for cosine similarity
            norms = _np.linalg.norm(self._embeddings, axis=1, keepdims=True)
            self._embeddings = self._embeddings / norms

        self._index_built = True
        print(f"   [EMBEDDINGS] Index built: {len(self._faqs)} FAQs in {encode_time:.0f}ms")

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.5,
        category: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant FAQs for a query.

        Args:
            query: User query text
            top_k: Maximum number of results
            threshold: Minimum similarity threshold (0-1)
            category: Optional category filter

        Returns:
            List of RetrievalResult sorted by similarity (descending)
        """
        if not self._faqs:
            return []

        # Build index if needed
        if not self._index_built:
            self.build_index()

        _lazy_import()

        start = time.time()

        # Encode query
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            show_progress_bar=False
        ).astype(_np.float32)

        # Normalize for cosine similarity
        if _faiss and _faiss is not False:
            _faiss.normalize_L2(query_embedding)

            # Search
            scores, indices = self._index.search(query_embedding, min(top_k * 2, len(self._faqs)))
            scores = scores[0]
            indices = indices[0]
        else:
            # Fallback: manual cosine similarity
            query_norm = query_embedding / _np.linalg.norm(query_embedding)
            scores = _np.dot(self._embeddings, query_norm.T).flatten()
            indices = _np.argsort(scores)[::-1][:top_k * 2]
            scores = scores[indices]

        self._last_query_time_ms = (time.time() - start) * 1000

        # Build results
        results = []
        rank = 1
        for idx, score in zip(indices, scores):
            if idx < 0 or idx >= len(self._faqs):
                continue

            # Apply threshold
            if score < threshold:
                continue

            faq = self._faqs[idx]

            # Apply category filter
            if category and faq.category != category:
                continue

            results.append(RetrievalResult(
                faq=faq,
                similarity=float(score),
                rank=rank
            ))
            rank += 1

            if len(results) >= top_k:
                break

        return results

    def retrieve_answer(
        self,
        query: str,
        threshold: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        Retrieve the best answer for a query.

        Convenience method that returns just the answer string.

        Args:
            query: User query text
            threshold: Minimum similarity threshold

        Returns:
            Tuple of (answer, similarity) or None if no match
        """
        results = self.retrieve(query, top_k=1, threshold=threshold)
        if results:
            return (results[0].faq.answer, results[0].similarity)
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "faq_count": len(self._faqs),
            "index_built": self._index_built,
            "model_name": self.model_name,
            "model_load_time_ms": self._load_time_ms,
            "last_query_time_ms": self._last_query_time_ms,
            "embedding_dim": self.EMBEDDING_DIM,
            "using_faiss": _faiss is not False and _faiss is not None,
        }

    def clear(self) -> None:
        """Clear all FAQs and index."""
        self._faqs = []
        self._embeddings = None
        self._index = None
        self._index_built = False

    def save_index(self, path: str) -> None:
        """
        Save FAQs and embeddings to disk.

        Args:
            path: Directory path for saving
        """
        _lazy_import()

        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save FAQs as JSON
        faqs_data = [faq.to_dict() for faq in self._faqs]
        with open(save_dir / "faqs.json", "w", encoding="utf-8") as f:
            json.dump(faqs_data, f, ensure_ascii=False, indent=2)

        # Save embeddings
        if self._embeddings is not None:
            _np.save(save_dir / "embeddings.npy", self._embeddings)

        # Save FAISS index
        if _faiss and _faiss is not False and self._index is not None:
            _faiss.write_index(self._index, str(save_dir / "index.faiss"))

        print(f"   [EMBEDDINGS] Saved index to {path}")

    def load_index(self, path: str) -> bool:
        """
        Load FAQs and embeddings from disk.

        Args:
            path: Directory path for loading

        Returns:
            True if loaded successfully
        """
        _lazy_import()

        load_dir = Path(path)
        if not load_dir.exists():
            return False

        # Load FAQs
        faqs_path = load_dir / "faqs.json"
        if faqs_path.exists():
            with open(faqs_path, "r", encoding="utf-8") as f:
                faqs_data = json.load(f)
            self._faqs = [
                FAQEntry(
                    id=faq["id"],
                    question=faq["question"],
                    answer=faq["answer"],
                    category=faq.get("category", ""),
                    keywords=faq.get("keywords", []),
                )
                for faq in faqs_data
            ]

        # Load embeddings
        embeddings_path = load_dir / "embeddings.npy"
        if embeddings_path.exists():
            self._embeddings = _np.load(embeddings_path)

        # Load FAISS index
        index_path = load_dir / "index.faiss"
        if _faiss and _faiss is not False and index_path.exists():
            self._index = _faiss.read_index(str(index_path))
            self._index_built = True
        elif self._embeddings is not None:
            # Rebuild index from embeddings
            self._index_built = True

        print(f"   [EMBEDDINGS] Loaded index from {path} ({len(self._faqs)} FAQs)")
        return True


# =============================================================================
# KEYWORD-ENHANCED RETRIEVER
# =============================================================================

class HybridFAQRetriever(FAISSFAQRetriever):
    """
    Hybrid retriever combining semantic similarity with keyword matching.

    Useful when semantic search alone might miss keyword-specific queries
    (e.g., "Satispay" payment method).
    """

    def __init__(self, *args, keyword_boost: float = 0.2, **kwargs):
        """
        Initialize hybrid retriever.

        Args:
            keyword_boost: Boost factor for keyword matches (0-1)
        """
        super().__init__(*args, **kwargs)
        self.keyword_boost = keyword_boost

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.5,
        category: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve with keyword boosting.

        Keywords in FAQ entries boost similarity score.
        """
        # Get semantic results
        results = super().retrieve(query, top_k=top_k * 2, threshold=threshold * 0.8, category=category)

        if not results:
            return results

        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Apply keyword boost
        boosted_results = []
        for result in results:
            boost = 0.0

            # Check FAQ keywords
            for keyword in result.faq.keywords:
                if keyword.lower() in query_lower:
                    boost += self.keyword_boost

            # Check if query words appear in question
            question_words = set(result.faq.question.lower().split())
            overlap = len(query_words & question_words) / max(len(query_words), 1)
            boost += overlap * self.keyword_boost * 0.5

            # Apply boost (capped at 1.0)
            new_similarity = min(1.0, result.similarity + boost)

            boosted_results.append(RetrievalResult(
                faq=result.faq,
                similarity=new_similarity,
                rank=result.rank
            ))

        # Re-sort by boosted similarity
        boosted_results.sort(key=lambda x: x.similarity, reverse=True)

        # Re-rank and apply threshold
        final_results = []
        for i, result in enumerate(boosted_results[:top_k]):
            if result.similarity >= threshold:
                final_results.append(RetrievalResult(
                    faq=result.faq,
                    similarity=result.similarity,
                    rank=i + 1
                ))

        return final_results


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_faq_retriever(
    faqs: Optional[List[Dict]] = None,
    hybrid: bool = True,
    **kwargs
) -> FAISSFAQRetriever:
    """
    Factory function to create FAQ retriever.

    Args:
        faqs: Optional list of FAQ dictionaries to pre-load
        hybrid: Use hybrid (keyword-enhanced) retriever
        **kwargs: Additional arguments for retriever

    Returns:
        Configured FAQRetriever instance
    """
    retriever_class = HybridFAQRetriever if hybrid else FAISSFAQRetriever
    retriever = retriever_class(**kwargs)

    if faqs:
        retriever.add_faqs(faqs)

    return retriever


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    print("=== FAQ Retriever Test ===\n")

    # Sample FAQs (Italian salon)
    sample_faqs = [
        {
            "id": "faq_001",
            "question": "Quanto costa un taglio donna?",
            "answer": "Il taglio donna costa €35. Se lo abbini alla piega, è €55.",
            "category": "pricing",
            "keywords": ["prezzo", "costo", "taglio"]
        },
        {
            "id": "faq_002",
            "question": "Siete aperti il lunedì?",
            "answer": "Sì, siamo aperti dal lunedì al venerdì dalle 9 alle 18, sabato dalle 9 alle 17.",
            "category": "hours",
            "keywords": ["orario", "aperti", "lunedì"]
        },
        {
            "id": "faq_003",
            "question": "Quanto costa il colore?",
            "answer": "Il colore parte da €45. Per colorazioni particolari, contattaci per un preventivo.",
            "category": "pricing",
            "keywords": ["prezzo", "costo", "colore", "tinta"]
        },
        {
            "id": "faq_004",
            "question": "Accettate Satispay?",
            "answer": "Sì, accettiamo contanti, carta di credito, bancomat e Satispay.",
            "category": "payment",
            "keywords": ["pagamento", "satispay", "carta", "contanti"]
        },
        {
            "id": "faq_005",
            "question": "Devo prenotare per un taglio?",
            "answer": "Consigliamo la prenotazione per garantire disponibilità, ma accettiamo anche clienti senza appuntamento.",
            "category": "booking",
            "keywords": ["prenotare", "appuntamento", "taglio"]
        },
    ]

    # Create retriever
    print("Creating retriever...")
    retriever = create_faq_retriever(sample_faqs, hybrid=True)

    # Build index
    print("Building index...")
    retriever.build_index()

    # Test queries
    test_queries = [
        "Qual è il prezzo del taglio?",
        "A che ora aprite?",
        "Posso pagare con Satispay?",
        "Quanto costa farsi i capelli?",
        "Serve prenotazione?",
    ]

    print("\n--- Test Queries ---")
    for query in test_queries:
        results = retriever.retrieve(query, top_k=2, threshold=0.4)
        print(f"\nQ: {query}")
        if results:
            for r in results:
                print(f"   [{r.similarity:.2f}] {r.faq.question}")
                print(f"   A: {r.faq.answer[:60]}...")
        else:
            print("   No match found")

    # Stats
    print("\n--- Stats ---")
    stats = retriever.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
