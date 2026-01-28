"""
FLUXION Voice Agent - Semantic Intent Classifier (TF-IDF)

Lightweight semantic classification without PyTorch dependency.
Uses character n-grams + TF-IDF + cosine similarity.

E7-S2: Intent accuracy improvement 85% → 92%

Performance: ~10ms per classification
Dependencies: numpy only (no torch, no sklearn)
"""

import re
import math
import unicodedata
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import Counter
import numpy as np


@dataclass
class SemanticMatch:
    """Result of semantic intent matching."""
    intent: str
    confidence: float
    matched_exemplar: str
    exemplar_similarity: float


# =============================================================================
# INTENT EXEMPLARS - Italian booking domain
# =============================================================================

# Each intent has multiple exemplar phrases covering variations
INTENT_EXEMPLARS: Dict[str, List[str]] = {
    "prenotazione": [
        "vorrei prenotare un appuntamento",
        "voglio prenotare",
        "posso prenotare",
        "mi prenota",
        "mi fissa un appuntamento",
        "mi serve un appuntamento",
        "ho bisogno di un appuntamento",
        "vorrei fissare un appuntamento",
        "mi può prenotare",
        "cerco un appuntamento",
        "devo prenotare",
        "potrei prenotare",
        "è possibile prenotare",
        "vorrei un taglio",
        "voglio fare un taglio",
        "mi serve un taglio",
        "voglio una piega",
        "vorrei una tinta",
        "mi fa un colore",
        "prenoto per domani",
        "appuntamento per questa settimana",
        "quando avete disponibilità",
        "avete posto",
        "siete liberi",
    ],
    "cancellazione": [
        "voglio annullare",
        "vorrei annullare il mio appuntamento",
        "devo cancellare l'appuntamento",
        "cancella l'appuntamento",
        "annulla la prenotazione",
        "non posso più venire",
        "non riesco a venire",
        "non ce la faccio",
        "devo disdire",
        "vorrei disdire",
        "elimina il mio appuntamento",
        "vorrei eliminare l'appuntamento",
        "voglio eliminare l'appuntamento",
        "devo eliminare l'appuntamento",
        "posso eliminare l'appuntamento",
        "eliminare la prenotazione",
        "togli l'appuntamento",
        "non vengo più",
        "annullo tutto",
        "cancello tutto",
        "mi è impossibile venire",
        "non posso presentarmi",
    ],
    "spostamento": [
        "voglio spostare l'appuntamento",
        "posso cambiare data",
        "vorrei modificare l'orario",
        "sposta l'appuntamento",
        "cambia l'ora",
        "posticipa l'appuntamento",
        "anticipa l'appuntamento",
        "rimanda l'appuntamento",
        "posso venire un altro giorno",
        "mi sposta l'appuntamento",
        "cambio data",
        "modifica la prenotazione",
        "vorrei un altro orario",
        "posso spostare a un'altra data",
        "mi serve cambiare giorno",
    ],
    "info_orari": [
        "a che ora aprite",
        "quando aprite",
        "che orari fate",
        "siete aperti",
        "fino a che ora siete aperti",
        "orario di apertura",
        "orario di chiusura",
        "a che ora chiudete",
        "quando chiudete",
        "gli orari di apertura",
        "lavorate anche sabato",
        "domenica siete aperti",
        "orari del negozio",
    ],
    "info_prezzi": [
        "quanto costa",
        "qual è il prezzo",
        "i prezzi",
        "il listino",
        "costo del taglio",
        "quanto viene",
        "prezzi dei servizi",
        "quanto mi costa",
        "quanto devo pagare",
        "quanto costano i servizi",
        "listino prezzi",
    ],
    "conferma": [
        "sì",
        "si",
        "sì confermo",
        "confermo",
        "va bene",
        "ok",
        "perfetto",
        "d'accordo",
        "esatto",
        "certamente",
        "assolutamente sì",
        "certo",
        "sicuro",
        "benissimo",
        "ottimo",
        "procedi",
        "va benissimo",
        "è corretto",
    ],
    "rifiuto": [
        "no",
        "no grazie",
        "non mi va",
        "non voglio",
        "lascia stare",
        "annulla",
        "stop",
        "basta",
        "non mi interessa",
        "niente",
        "neanche",
        "assolutamente no",
        "non è quello che voglio",
    ],
    "nuovo_cliente": [
        "non sono mai stato",
        "è la prima volta",
        "sono un nuovo cliente",
        "prima visita",
        "non vi conosco ancora",
        "mai venuto prima",
        "primo appuntamento",
        "non sono cliente",
        "non sono vostro cliente",
        "è la mia prima volta",
    ],
    "operatore": [
        "voglio parlare con una persona",
        "operatore",
        "parlare con qualcuno",
        "persona vera",
        "operatore umano",
        "trasferiscimi a una persona",
        "non voglio parlare con un robot",
        "passami un operatore",
    ],
    "saluto": [
        "buongiorno",
        "buonasera",
        "ciao",
        "salve",
        "buon pomeriggio",
        "pronto",
    ],
    "congedo": [
        "arrivederci",
        "a presto",
        "grazie e arrivederci",
        "alla prossima",
        "buona giornata",
        "ci vediamo",
    ],
    "ringraziamento": [
        "grazie",
        "grazie mille",
        "molte grazie",
        "la ringrazio",
        "ti ringrazio",
        "grazie tante",
    ],
}


# =============================================================================
# TEXT PREPROCESSING
# =============================================================================

def normalize_text(text: str) -> str:
    """
    Normalize Italian text for matching.

    - Lowercase
    - Remove accents: "è" → "e"
    - Collapse whitespace
    - Remove punctuation
    """
    text = text.lower().strip()

    # Remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    # Remove punctuation except apostrophes (important in Italian)
    text = re.sub(r"[^\w\s']", " ", text)

    # Collapse whitespace
    text = ' '.join(text.split())

    return text


def get_character_ngrams(text: str, n_range: Tuple[int, int] = (2, 4)) -> List[str]:
    """
    Extract character n-grams from text.

    Character n-grams work well for Italian due to:
    - Morphological richness
    - Typo tolerance
    - Stemming-like effect

    Args:
        text: Normalized text
        n_range: Min and max n-gram length (default 2-4)

    Returns:
        List of character n-grams
    """
    ngrams = []
    text = f"_{text}_"  # Add boundary markers

    min_n, max_n = n_range
    for n in range(min_n, max_n + 1):
        for i in range(len(text) - n + 1):
            ngrams.append(text[i:i+n])

    return ngrams


def get_word_ngrams(text: str, n_range: Tuple[int, int] = (1, 2)) -> List[str]:
    """
    Extract word n-grams from text.

    Args:
        text: Normalized text
        n_range: Min and max n-gram length (default 1-2)

    Returns:
        List of word n-grams
    """
    words = text.split()
    ngrams = []

    min_n, max_n = n_range
    for n in range(min_n, max_n + 1):
        for i in range(len(words) - n + 1):
            ngrams.append(' '.join(words[i:i+n]))

    return ngrams


# =============================================================================
# TF-IDF VECTORIZER (Pure NumPy)
# =============================================================================

class TFIDFVectorizer:
    """
    Lightweight TF-IDF vectorizer using numpy only.

    Features:
    - Character n-grams (2-4)
    - Word n-grams (1-2)
    - Sublinear TF (log scaling)
    - L2 normalization
    """

    def __init__(self,
                 use_char_ngrams: bool = True,
                 use_word_ngrams: bool = True,
                 char_n_range: Tuple[int, int] = (2, 4),
                 word_n_range: Tuple[int, int] = (1, 2),
                 min_df: int = 1,
                 max_features: int = 5000):
        """
        Initialize vectorizer.

        Args:
            use_char_ngrams: Include character n-grams
            use_word_ngrams: Include word n-grams
            char_n_range: Character n-gram range
            word_n_range: Word n-gram range
            min_df: Minimum document frequency
            max_features: Maximum vocabulary size
        """
        self.use_char_ngrams = use_char_ngrams
        self.use_word_ngrams = use_word_ngrams
        self.char_n_range = char_n_range
        self.word_n_range = word_n_range
        self.min_df = min_df
        self.max_features = max_features

        self.vocabulary_: Dict[str, int] = {}
        self.idf_: Optional[np.ndarray] = None
        self._fitted = False

    def _extract_features(self, text: str) -> List[str]:
        """Extract all features from text."""
        normalized = normalize_text(text)
        features = []

        if self.use_char_ngrams:
            features.extend(f"c:{ng}" for ng in get_character_ngrams(normalized, self.char_n_range))

        if self.use_word_ngrams:
            features.extend(f"w:{ng}" for ng in get_word_ngrams(normalized, self.word_n_range))

        return features

    def fit(self, documents: List[str]) -> 'TFIDFVectorizer':
        """
        Build vocabulary and compute IDF from documents.

        Args:
            documents: List of text documents

        Returns:
            self
        """
        # Count document frequencies
        df = Counter()
        n_docs = len(documents)

        for doc in documents:
            features = set(self._extract_features(doc))
            for f in features:
                df[f] += 1

        # Filter by min_df
        df = {f: count for f, count in df.items() if count >= self.min_df}

        # Limit to max_features (by frequency)
        if len(df) > self.max_features:
            top_features = sorted(df.items(), key=lambda x: -x[1])[:self.max_features]
            df = dict(top_features)

        # Build vocabulary
        self.vocabulary_ = {f: i for i, f in enumerate(sorted(df.keys()))}

        # Compute IDF: log((n_docs + 1) / (df + 1)) + 1 (smooth IDF)
        self.idf_ = np.zeros(len(self.vocabulary_))
        for feature, idx in self.vocabulary_.items():
            self.idf_[idx] = math.log((n_docs + 1) / (df[feature] + 1)) + 1

        self._fitted = True
        return self

    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Transform documents to TF-IDF vectors.

        Args:
            documents: List of text documents

        Returns:
            TF-IDF matrix (n_docs x n_features)
        """
        if not self._fitted:
            raise ValueError("Vectorizer not fitted. Call fit() first.")

        n_docs = len(documents)
        n_features = len(self.vocabulary_)

        # Build TF matrix (sublinear: 1 + log(tf))
        tfidf = np.zeros((n_docs, n_features))

        for doc_idx, doc in enumerate(documents):
            features = self._extract_features(doc)
            tf = Counter(features)

            for feature, count in tf.items():
                if feature in self.vocabulary_:
                    feat_idx = self.vocabulary_[feature]
                    # Sublinear TF
                    tfidf[doc_idx, feat_idx] = (1 + math.log(count)) * self.idf_[feat_idx]

        # L2 normalization
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        tfidf /= norms

        return tfidf

    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(documents)
        return self.transform(documents)


# =============================================================================
# SEMANTIC INTENT CLASSIFIER
# =============================================================================

class SemanticIntentClassifier:
    """
    TF-IDF based semantic intent classifier.

    Uses cosine similarity between query and intent exemplars
    to find the best matching intent.

    Performance: ~10ms per classification
    """

    def __init__(self, min_confidence: float = 0.3):
        """
        Initialize classifier.

        Args:
            min_confidence: Minimum confidence threshold
        """
        self.min_confidence = min_confidence
        self.vectorizer = TFIDFVectorizer()
        self.intent_vectors: Optional[np.ndarray] = None
        self.intent_labels: List[str] = []
        self.exemplar_texts: List[str] = []
        self._fitted = False

    def fit(self, intent_exemplars: Dict[str, List[str]] = None) -> 'SemanticIntentClassifier':
        """
        Fit classifier with intent exemplars.

        Args:
            intent_exemplars: Dict mapping intent names to exemplar phrases.
                            If None, uses built-in INTENT_EXEMPLARS.

        Returns:
            self
        """
        if intent_exemplars is None:
            intent_exemplars = INTENT_EXEMPLARS

        # Flatten exemplars
        self.intent_labels = []
        self.exemplar_texts = []

        for intent, exemplars in intent_exemplars.items():
            for exemplar in exemplars:
                self.intent_labels.append(intent)
                self.exemplar_texts.append(exemplar)

        # Fit vectorizer and transform exemplars
        self.intent_vectors = self.vectorizer.fit_transform(self.exemplar_texts)
        self._fitted = True

        return self

    def classify(self, text: str) -> Optional[SemanticMatch]:
        """
        Classify text intent using cosine similarity.

        Args:
            text: User input text

        Returns:
            SemanticMatch if confidence >= threshold, None otherwise
        """
        if not self._fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")

        # Vectorize query
        query_vector = self.vectorizer.transform([text])[0]

        # Compute cosine similarities
        similarities = np.dot(self.intent_vectors, query_vector)

        # Find best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]

        if best_similarity < self.min_confidence:
            return None

        return SemanticMatch(
            intent=self.intent_labels[best_idx],
            confidence=float(best_similarity),
            matched_exemplar=self.exemplar_texts[best_idx],
            exemplar_similarity=float(best_similarity)
        )

    def classify_with_scores(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Get top-k intent predictions with scores.

        Args:
            text: User input text
            top_k: Number of top predictions

        Returns:
            List of (intent, score) tuples
        """
        if not self._fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")

        # Vectorize query
        query_vector = self.vectorizer.transform([text])[0]

        # Compute cosine similarities
        similarities = np.dot(self.intent_vectors, query_vector)

        # Aggregate by intent (max similarity per intent)
        intent_scores: Dict[str, float] = {}
        for idx, sim in enumerate(similarities):
            intent = self.intent_labels[idx]
            if intent not in intent_scores or sim > intent_scores[intent]:
                intent_scores[intent] = float(sim)

        # Sort by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: -x[1])

        return sorted_intents[:top_k]


# =============================================================================
# GLOBAL INSTANCE (LAZY LOADED)
# =============================================================================

_classifier: Optional[SemanticIntentClassifier] = None


def get_semantic_classifier() -> SemanticIntentClassifier:
    """Get or create global semantic classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = SemanticIntentClassifier()
        _classifier.fit()
    return _classifier


def semantic_intent(text: str) -> Optional[SemanticMatch]:
    """
    Classify intent using semantic similarity.

    Convenience function using global classifier.

    Args:
        text: User input text

    Returns:
        SemanticMatch if confident, None otherwise
    """
    classifier = get_semantic_classifier()
    return classifier.classify(text)


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FLUXION Semantic Intent Classifier - Test")
    print("=" * 60)

    # Initialize classifier
    classifier = SemanticIntentClassifier(min_confidence=0.25)
    classifier.fit()

    print(f"\nVocabulary size: {len(classifier.vectorizer.vocabulary_)}")
    print(f"Total exemplars: {len(classifier.exemplar_texts)}")
    print(f"Intents: {set(classifier.intent_labels)}")

    # Test cases
    test_cases = [
        # Booking
        ("Vorrei prenotare un taglio", "prenotazione"),
        ("Mi può fissare un appuntamento?", "prenotazione"),
        ("Avete posto domani?", "prenotazione"),

        # Cancellation
        ("Devo annullare l'appuntamento", "cancellazione"),
        ("Non posso più venire", "cancellazione"),
        ("Voglio cancellare la prenotazione", "cancellazione"),

        # Reschedule
        ("Posso spostare l'appuntamento?", "spostamento"),
        ("Vorrei cambiare data", "spostamento"),
        ("Mi anticipate l'appuntamento?", "spostamento"),

        # Info
        ("Quanto costa un taglio?", "info_prezzi"),
        ("A che ora aprite?", "info_orari"),

        # Confirm/Reject
        ("Sì, va bene", "conferma"),
        ("No grazie", "rifiuto"),

        # New client
        ("Non sono mai stato da voi", "nuovo_cliente"),
        ("È la prima volta", "nuovo_cliente"),

        # Operator
        ("Voglio parlare con una persona", "operatore"),

        # Greetings
        ("Buongiorno", "saluto"),
        ("Grazie mille", "ringraziamento"),
        ("Arrivederci", "congedo"),
    ]

    print("\n" + "-" * 60)
    print("Test Results:")
    print("-" * 60)

    correct = 0
    total = len(test_cases)

    for text, expected in test_cases:
        result = classifier.classify(text)

        if result:
            actual = result.intent
            conf = result.confidence
            status = "✅" if actual == expected else "❌"
            if actual == expected:
                correct += 1
            print(f"{status} \"{text}\"")
            print(f"   Expected: {expected}, Got: {actual} ({conf:.2f})")
        else:
            print(f"❌ \"{text}\"")
            print(f"   Expected: {expected}, Got: None (below threshold)")

    print("\n" + "=" * 60)
    accuracy = correct / total * 100
    print(f"Accuracy: {correct}/{total} = {accuracy:.1f}%")
    print("=" * 60)
