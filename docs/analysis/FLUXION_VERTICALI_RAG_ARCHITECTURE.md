# FLUXION Verticali Enterprise + RAG Architecture

> **Risposta al Prompt Pre-Implementation Consultation**
> **Data**: Gennaio 2026
> **Target**: 5 Verticali PMI (Salone, Palestra, Studio Medico, Officina, Altro)

---

## 1. INIT SYSTEM CON CHIAVE VERTICALE

### 1.1 Come Funziona Oggi in FLUXION

La chiave verticale viene scelta dall'utente durante il **Setup Wizard** (primo avvio).

```typescript
// src/types/setup.ts - CATEGORIE_ATTIVITA
export const CATEGORIE_ATTIVITA = [
  { value: 'salone', label: 'Salone / Parrucchiere', icon: '💇' },
  { value: 'auto', label: 'Officina / Carrozzeria', icon: '🚗' },
  { value: 'wellness', label: 'Centro Benessere / Palestra', icon: '🧘' },
  { value: 'medical', label: 'Studio Medico / Dentista', icon: '🏥' },
  { value: 'altro', label: 'Altro', icon: '🏢' },
] as const;

// Zod schema con enum validato
categoria_attivita: z.enum(['salone', 'auto', 'wellness', 'medical', 'altro'])
```

### 1.2 Persistenza nel Database SQLite

```sql
-- La chiave verticale viene salvata nella tabella setup
CREATE TABLE setup (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    business_name TEXT NOT NULL,
    business_type TEXT DEFAULT 'salone',  -- ← CHIAVE VERTICALE
    address TEXT,
    phone TEXT,
    email TEXT,
    ...
);

-- Query per recuperare il verticale
SELECT business_type FROM setup WHERE id = 1;
-- Risultato: 'salone' | 'wellness' | 'medical' | 'auto' | 'altro'
```

### 1.3 Caricamento Dinamico Moduli

```
FLUXION_VERTICALE = "palestra"  # Valore da DB setup.business_type

Sistema carica automaticamente:
├─ FAQ Knowledge Base      → voice-agent/data/faq_{verticale}_test.json
├─ Voice Agent Prompts     → voice-agent/prompts/prompt_{verticale}.md
├─ Servizi Default         → Popolati da INSERT INTO servizi al setup
├─ Orari Default           → Template orari per verticale
└─ Embeddings Cache        → voice-agent/cache/embeddings_{verticale}.pkl
```

**Implementazione Python (Voice Agent):**

```python
# voice-agent/src/faq_manager.py
import os
from pathlib import Path

class FAQManager:
    def __init__(self, verticale: str):
        self.verticale = verticale
        self.data_dir = Path(__file__).parent.parent / "data"
        self.cache_dir = Path(__file__).parent.parent / "cache"

    def load_faq_file(self) -> str:
        """Carica FAQ per verticale specifico."""
        # Priorità: JSON > MD > fallback generico
        json_path = self.data_dir / f"faq_{self.verticale}_test.json"
        md_path = self.data_dir / f"faq_{self.verticale}.md"

        if json_path.exists():
            return self._load_json(json_path)
        elif md_path.exists():
            return self._load_md(md_path)
        else:
            # Fallback a FAQ generiche
            return self._load_generic()

    def get_embeddings_cache_path(self) -> Path:
        """Path cache embeddings per verticale."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir / f"embeddings_{self.verticale}.pkl"
```

### 1.4 Dove Cachare Embeddings (Raccomandazione)

```
Struttura consigliata:
fluxion/
├─ voice-agent/
│  ├─ cache/                          # ← CACHE EMBEDDINGS
│  │  ├─ embeddings_salone.npy        # NumPy array (più veloce)
│  │  ├─ embeddings_palestra.npy
│  │  ├─ embeddings_medical.npy
│  │  ├─ index_salone.faiss           # FAISS index (opzionale)
│  │  └─ faqs_salone.json             # FAQ metadata
│  ├─ data/
│  │  ├─ faq_salone_test.json         # FAQ source
│  │  ├─ faq_palestra_test.json
│  │  └─ faq_studio_test.json
```

**Path raccomandato:**
```python
# Relativo all'app FLUXION
CACHE_DIR = Path(__file__).parent.parent / "cache"  # voice-agent/cache/

# Oppure in user data directory (persistente)
import appdirs
CACHE_DIR = Path(appdirs.user_cache_dir("fluxion")) / "embeddings"
# macOS: ~/Library/Caches/fluxion/embeddings/
# Windows: C:\Users\<user>\AppData\Local\fluxion\Cache\embeddings\
```

### 1.5 Sincronizzazione Schema DB + Migrations

```sql
-- Il verticale NON cambia lo schema DB principale
-- Le tabelle sono generiche, i DATI sono verticale-specific

-- Tabella servizi: stessa struttura per tutti i verticali
CREATE TABLE servizi (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    prezzo REAL,
    durata INTEGER,  -- minuti
    categoria TEXT,  -- può variare per verticale
    attivo INTEGER DEFAULT 1
);

-- I DATI cambiano per verticale (seed durante setup):

-- Per 'salone':
INSERT INTO servizi (nome, prezzo, durata) VALUES
('Taglio Donna', 35, 60),
('Piega', 20, 30),
('Colore', 55, 90);

-- Per 'palestra':
INSERT INTO servizi (nome, prezzo, durata) VALUES
('Abbonamento Mensile', 45, 0),
('Personal Training', 50, 60),
('Corso Yoga', 10, 60);
```

---

## 2. RAG ARCHITETTURA (IBRIDA)

### 2.1 Flusso Completo Query

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE FLUXION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   QUERY UTENTE (Sara/WhatsApp)                                              │
│   "Quanto costa un taglio?"                                                 │
│            │                                                                │
│            ▼                                                                │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 1: KEYWORD MATCH (< 5ms)                                     │   │
│   │ ├─ Pattern: "quanto costa" → categoria PREZZO                      │   │
│   │ └─ Se match esatto: ritorna risposta da FAQ template               │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│            │ no match                                                       │
│            ▼                                                                │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 2: DATABASE LOOKUP (< 20ms)                                  │   │
│   │ ├─ Query: SELECT nome, prezzo FROM servizi WHERE nome LIKE '%tag%' │   │
│   │ ├─ Variabili: {{SERVIZIO}} = "Taglio", {{PREZZO}} = "35"          │   │
│   │ └─ Template: "Il {{SERVIZIO}} costa {{PREZZO}}€"                   │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│            │ no match                                                       │
│            ▼                                                                │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 3: SEMANTIC SEARCH (< 100ms)                                 │   │
│   │ ├─ Embedding query con sentence-transformers                       │   │
│   │ ├─ Similarity search su FAISS index (FAQ verticale)                │   │
│   │ ├─ Threshold: 0.55 (semantic), 0.75 (high confidence)             │   │
│   │ └─ Hybrid boost: +0.2 per keyword match                            │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│            │ no match (similarity < threshold)                              │
│            ▼                                                                │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 4: GROQ LLM FALLBACK (< 500ms)                               │   │
│   │ ├─ Prompt: sistema + contesto verticale + query                    │   │
│   │ ├─ Model: llama-3.3-70b-versatile                                  │   │
│   │ └─ Se troppo complesso: "Mi scusi, la metto in contatto con..."    │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│            │ final fallback                                                 │
│            ▼                                                                │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │ FALLBACK RESPONSE                                                  │   │
│   │ "Mi dispiace, non ho informazioni su questo. Vuole che la metta   │   │
│   │  in contatto con il proprietario?"                                 │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Risposte alle Domande Tecniche

#### ✅ Python Library per TF-IDF / Similarity Search

```python
# OPZIONE 1: sklearn TfidfVectorizer (leggero, no GPU)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TfidfRetriever:
    def __init__(self, documents: list[str]):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode',
            stop_words=None,  # Italiano non supportato di default
            ngram_range=(1, 2),  # Bigrams per frasi italiane
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        self.documents = documents

    def search(self, query: str, top_k: int = 3) -> list[tuple[int, float]]:
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [(i, similarities[i]) for i in top_indices]

# OPZIONE 2: sentence-transformers + FAISS (più accurato, raccomandato)
# Già implementato in voice-agent/src/faq_retriever.py

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SemanticRetriever:
    MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # Italiano supportato

    def __init__(self):
        self.model = SentenceTransformer(self.MODEL)
        self.index = None
        self.documents = []

    def build_index(self, documents: list[str]):
        self.documents = documents
        embeddings = self.model.encode(documents, convert_to_numpy=True)
        embeddings = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 3) -> list[tuple[int, float]]:
        query_emb = self.model.encode([query], convert_to_numpy=True).astype(np.float32)
        faiss.normalize_L2(query_emb)
        scores, indices = self.index.search(query_emb, top_k)
        return [(idx, score) for idx, score in zip(indices[0], scores[0])]
```

**Raccomandazione FLUXION:** Usare `HybridFAQRetriever` (già implementato) che combina:
- Semantic search (FAISS + sentence-transformers)
- Keyword boost (+0.2 per match esatti)

#### ✅ Latenza Target: < 200ms (Voice Call)

**Benchmark FLUXION attuale:**

| Layer | Latenza | Accettabile |
|-------|---------|-------------|
| L1: Keyword Match | < 5ms | ✅ |
| L2: DB Lookup | < 20ms | ✅ |
| L3: Semantic Search | 50-100ms | ✅ |
| L4: Groq LLM | 300-500ms | ⚠️ Solo fallback |
| **Totale (L1-L3)** | **< 125ms** | ✅ |

**Per voice call real-time:**
- Target: < 200ms end-to-end
- L1+L2+L3: ~125ms (accettabile)
- L4 solo se necessario (degrada a 500ms)

#### ✅ Come Cachare TF-IDF / Embeddings in Memoria

```python
# voice-agent/src/faq_manager.py
import pickle
from pathlib import Path

class CachedFAQRetriever:
    """Retriever con cache embeddings in memoria e disco."""

    _instance = None  # Singleton per mantenere in RAM
    _cache = {}       # In-memory cache per verticale

    @classmethod
    def get_instance(cls, verticale: str):
        """Singleton pattern - una istanza per processo."""
        if cls._instance is None:
            cls._instance = cls()

        if verticale not in cls._cache:
            cls._cache[verticale] = cls._load_or_build(verticale)

        return cls._cache[verticale]

    @staticmethod
    def _load_or_build(verticale: str):
        """Carica da cache disco o costruisce index."""
        cache_path = Path(f"voice-agent/cache/embeddings_{verticale}.pkl")

        if cache_path.exists():
            # Carica da disco (< 100ms)
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        else:
            # Costruisce e salva (prima volta, ~5s)
            retriever = HybridFAQRetriever()
            retriever.add_faqs(load_faqs_for_verticale(verticale))
            retriever.build_index()

            # Salva cache
            cache_path.parent.mkdir(exist_ok=True)
            with open(cache_path, "wb") as f:
                pickle.dump(retriever, f)

            return retriever

# Uso:
retriever = CachedFAQRetriever.get_instance("salone")
results = retriever.retrieve("quanto costa un taglio?")
```

**Strategia cache:**
1. **Prima chiamata**: Build index (~5s), salva su disco
2. **Chiamate successive**: Carica da disco (< 100ms)
3. **In memoria**: Singleton mantiene index in RAM per processo
4. **Invalidazione**: Rebuild se FAQ modificate (hash check)

#### ✅ Gestione Multi-threaded (WhatsApp + Voice Concurrent)

```python
# voice-agent/src/server.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

class RAGServer:
    """Server RAG con gestione concorrente."""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.retriever_lock = asyncio.Lock()
        self._retrievers = {}  # Cache per verticale

    async def query(self, verticale: str, query: str) -> str:
        """Query thread-safe per RAG."""
        # Ottieni retriever (thread-safe)
        async with self.retriever_lock:
            if verticale not in self._retrievers:
                self._retrievers[verticale] = self._init_retriever(verticale)

        retriever = self._retrievers[verticale]

        # Esegui search in thread pool (non blocca event loop)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            retriever.retrieve,
            query
        )

        return self._format_response(result)

    def _init_retriever(self, verticale: str):
        """Inizializza retriever per verticale."""
        retriever = HybridFAQRetriever()

        # Carica FAQ da file verticale
        faq_path = Path(f"voice-agent/data/faq_{verticale}_test.json")
        if faq_path.exists():
            import json
            with open(faq_path) as f:
                faqs = json.load(f)
            retriever.add_faqs(faqs)

        retriever.build_index()
        return retriever
```

**Architettura concorrenza FLUXION:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONCURRENT RAG QUERIES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   WhatsApp Thread ────┐                                         │
│                       │                                         │
│   Voice Call #1 ──────┼────▶ ThreadPoolExecutor (4 workers)    │
│                       │              │                          │
│   Voice Call #2 ──────┘              ▼                          │
│                             ┌─────────────────┐                 │
│                             │ Shared Retriever │                │
│                             │ (thread-safe)    │                │
│                             │                  │                │
│                             │ ┌─────────────┐ │                 │
│                             │ │ salone      │ │                 │
│                             │ │ retriever   │ │                 │
│                             │ └─────────────┘ │                 │
│                             │ ┌─────────────┐ │                 │
│                             │ │ palestra    │ │                 │
│                             │ │ retriever   │ │                 │
│                             │ └─────────────┘ │                 │
│                             └─────────────────┘                 │
│                                                                 │
│   Concurrency: 4 RAG queries simultanee                        │
│   Lock: Solo per init retriever, non per search                │
│   Memory: ~200MB per retriever (shared tra threads)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. INTEGRAZIONE .MD + DATABASE

### 3.1 Struttura Cartelle FLUXION

```
fluxion/
├─ voice-agent/
│  ├─ data/                           # Knowledge Base files
│  │  ├─ faq_salone_test.json         # 23 FAQ salone (Q&A strutturate)
│  │  ├─ faq_palestra_test.json       # 10 FAQ palestra
│  │  ├─ faq_studio_test.json         # 10 FAQ studio medico
│  │  └─ faq_auto.md                  # FAQ officina (markdown)
│  │
│  ├─ prompts/                        # Voice Agent system prompts
│  │  ├─ prompt_beauty.md             # Prompt salone (60+ variabili)
│  │  ├─ prompt_wellness.md           # Prompt palestra
│  │  ├─ prompt_medical.md            # Prompt studio medico
│  │  └─ prompt_auto.md               # Prompt officina
│  │
│  ├─ cache/                          # Embeddings cache (runtime)
│  │  ├─ embeddings_salone.npy
│  │  ├─ index_salone.faiss
│  │  └─ faqs_salone.json
│  │
│  └─ src/
│     ├─ faq_retriever.py             # FAISS semantic search
│     ├─ faq_manager.py               # Hybrid retrieval (keyword + semantic)
│     └─ orchestrator.py              # 4-layer pipeline
│
├─ src-tauri/
│  ├─ migrations/                     # SQLite schema (universal)
│  │  ├─ 001_init.sql                 # Core tables
│  │  └─ ...
│  └─ src/
│     └─ commands/
│        └─ faq_template.rs           # Rust: variabili DB → FAQ
│
└─ src/
   └─ types/
      └─ setup.ts                     # CATEGORIE_ATTIVITA enum
```

### 3.2 Formato FAQ JSON (Verticale-Specific)

```json
// voice-agent/data/faq_salone_test.json
[
  {
    "id": "faq_prezzo_taglio",
    "question": "Quanto costa un taglio?",
    "answer": "Il {{SERVIZIO}} costa {{PREZZO}}€ e dura circa {{DURATA}} minuti.",
    "category": "pricing",
    "keywords": ["prezzo", "costo", "taglio", "quanto"],
    "db_query": "SELECT nome, prezzo, durata FROM servizi WHERE nome LIKE '%taglio%'",
    "variables": ["SERVIZIO", "PREZZO", "DURATA"]
  },
  {
    "id": "faq_orari",
    "question": "Quali sono gli orari di apertura?",
    "answer": "Siamo aperti {{ORARI_APERTURA}}. Per appuntamenti {{TELEFONO}}.",
    "category": "hours",
    "keywords": ["orari", "apertura", "quando", "aperto"],
    "db_query": "SELECT giorno, apertura, chiusura FROM orari WHERE attivo = 1",
    "variables": ["ORARI_APERTURA", "TELEFONO"]
  },
  {
    "id": "faq_pagamento",
    "question": "Quali metodi di pagamento accettate?",
    "answer": "Accettiamo {{METODI_PAGAMENTO}}.",
    "category": "payment",
    "keywords": ["pagamento", "carta", "contanti", "satispay", "bancomat"],
    "variables": ["METODI_PAGAMENTO"]
  }
]
```

### 3.3 Variabili DB → FAQ (Runtime)

```python
# voice-agent/src/faq_template.py
import re
from typing import Dict, Any

class FAQTemplateEngine:
    """Sostituisce variabili {{...}} con dati dal DB."""

    def __init__(self, db_connection):
        self.db = db_connection
        self._cache = {}  # Cache variabili comuni

    def render(self, template: str, context: Dict[str, Any] = None) -> str:
        """
        Renderizza template FAQ con variabili DB.

        Args:
            template: "Il {{SERVIZIO}} costa {{PREZZO}}€"
            context: Override manuale variabili

        Returns:
            "Il Taglio costa 35€"
        """
        # Trova tutte le variabili {{...}}
        variables = re.findall(r'\{\{(\w+)\}\}', template)

        result = template
        for var in variables:
            # Priority: context override > cache > DB query
            if context and var in context:
                value = context[var]
            elif var in self._cache:
                value = self._cache[var]
            else:
                value = self._query_variable(var)
                self._cache[var] = value

            result = result.replace(f"{{{{{var}}}}}", str(value))

        return result

    def _query_variable(self, var_name: str) -> str:
        """Query DB per ottenere valore variabile."""
        queries = {
            "NOME_ATTIVITA": "SELECT business_name FROM setup WHERE id = 1",
            "INDIRIZZO": "SELECT address FROM setup WHERE id = 1",
            "TELEFONO": "SELECT phone FROM setup WHERE id = 1",
            "ORARI_APERTURA": self._format_orari,
            "LISTA_SERVIZI": self._format_servizi,
            "LISTA_OPERATORI": self._format_operatori,
            "METODI_PAGAMENTO": "SELECT payment_methods FROM setup WHERE id = 1",
        }

        if var_name in queries:
            query = queries[var_name]
            if callable(query):
                return query()
            else:
                result = self.db.execute(query).fetchone()
                return result[0] if result else ""

        return f"[{var_name}]"  # Placeholder se non trovato

    def _format_orari(self) -> str:
        """Formatta orari apertura."""
        rows = self.db.execute(
            "SELECT giorno, apertura, chiusura FROM orari WHERE attivo = 1 ORDER BY id"
        ).fetchall()

        # Raggruppa giorni con stessi orari
        # Lun-Ven 9:00-18:00, Sab 9:00-13:00
        return self._group_schedule(rows)

    def _format_servizi(self) -> str:
        """Formatta lista servizi con prezzi."""
        rows = self.db.execute(
            "SELECT nome, prezzo, durata FROM servizi WHERE attivo = 1"
        ).fetchall()

        return ", ".join([f"{r[0]} (€{r[1]}, {r[2]} min)" for r in rows])

    def _format_operatori(self) -> str:
        """Formatta lista operatori."""
        rows = self.db.execute(
            "SELECT nome FROM operatori WHERE attivo = 1"
        ).fetchall()

        return ", ".join([r[0] for r in rows])
```

### 3.4 Flusso Completo: Query → DB → Risposta

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FAQ TEMPLATE + DB INTEGRATION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. QUERY UTENTE                                                          │
│      "Quanto costa un taglio?"                                             │
│                                                                             │
│   2. FAQ RETRIEVER trova match:                                            │
│      {                                                                      │
│        "id": "faq_prezzo_taglio",                                          │
│        "answer": "Il {{SERVIZIO}} costa {{PREZZO}}€",                      │
│        "db_query": "SELECT nome, prezzo FROM servizi WHERE nome LIKE..."   │
│      }                                                                      │
│                                                                             │
│   3. DB LOOKUP                                                             │
│      ┌────────────────────────────────────────────────────────────────┐    │
│      │ SQLite: servizi table                                         │    │
│      │ ┌──────────────┬─────────┬─────────┐                         │    │
│      │ │ nome         │ prezzo  │ durata  │                         │    │
│      │ ├──────────────┼─────────┼─────────┤                         │    │
│      │ │ Taglio Donna │ 35      │ 60      │ ← match                 │    │
│      │ │ Taglio Uomo  │ 18      │ 30      │                         │    │
│      │ └──────────────┴─────────┴─────────┘                         │    │
│      └────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│   4. TEMPLATE RENDERING                                                     │
│      Template: "Il {{SERVIZIO}} costa {{PREZZO}}€"                         │
│      Variables: SERVIZIO = "Taglio Donna", PREZZO = "35"                   │
│      Output: "Il Taglio Donna costa 35€"                                   │
│                                                                             │
│   5. RISPOSTA SARA                                                          │
│      "Il Taglio Donna costa 35€ e dura circa 60 minuti.                    │
│       Vuole prenotare un appuntamento?"                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. RIEPILOGO ARCHITETTURA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUXION VERTICALI + RAG ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SETUP WIZARD                                                              │
│   ┌─────────────────┐                                                      │
│   │ Seleziona:      │                                                      │
│   │ ☑ Salone        │──────▶ setup.business_type = 'salone'               │
│   │ ☐ Palestra      │                                                      │
│   │ ☐ Studio Medico │                                                      │
│   └─────────────────┘                                                      │
│            │                                                                │
│            ▼                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                         RUNTIME LOADING                              │  │
│   │                                                                      │  │
│   │   faq_salone_test.json ──▶ HybridFAQRetriever ──▶ FAISS Index      │  │
│   │                                   │                                  │  │
│   │   SQLite DB ──────────────────────┼──▶ Variabili {{...}}            │  │
│   │   (servizi, orari, operatori)     │                                  │  │
│   │                                   ▼                                  │  │
│   │                          FAQ Template Engine                         │  │
│   │                                   │                                  │  │
│   │                                   ▼                                  │  │
│   │                          Sara Voice Response                         │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   PERFORMANCE:                                                              │
│   ├─ Keyword match: < 5ms                                                  │
│   ├─ DB lookup: < 20ms                                                     │
│   ├─ Semantic search: < 100ms                                              │
│   ├─ Template render: < 5ms                                                │
│   └─ TOTALE: < 130ms (voice-ready)                                         │
│                                                                             │
│   CONCURRENCY:                                                              │
│   ├─ ThreadPoolExecutor(4 workers)                                         │
│   ├─ Singleton retriever per verticale                                     │
│   └─ Lock solo per init, non per search                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. RISPOSTE FINALI

| Domanda | Risposta |
|---------|----------|
| **Caricamento dinamico moduli Python** | Singleton pattern + lazy loading per verticale |
| **Path cache embeddings** | `voice-agent/cache/embeddings_{verticale}.npy` |
| **Sincronizzazione schema DB** | Schema universale, solo DATI cambiano per verticale |
| **Library TF-IDF** | `sentence-transformers` + `faiss-cpu` (già implementato) |
| **Latenza RAG < 200ms** | ✅ ~125ms (L1+L2+L3) |
| **Cache TF-IDF in memoria** | Singleton + pickle su disco |
| **Multi-threaded concurrent** | ThreadPoolExecutor + asyncio, lock solo per init |

---

*Generato: 2026-01-15 - FLUXION Phase 7 Complete*
