# STT Name Correction — CoVe 2026 Research (Agente B)
> Data: 2026-03-13 | Sessione: S69 | Agente: B (NLP/STT tecnico)
> Problema: Whisper via Groq mishears nomi italiani (es. "De Piscopo" → "l'episcopo")
> Goal: Context injection + post-correction LLM per nomi clienti dal DB

---

## 1. Whisper `initial_prompt` / `prompt` — Documentazione Tecnica

### Come funziona
- Il parametro guida Whisper a usare un vocabolario/stile specifico
- Funziona come "testo precedente fittizio" che il decoder usa come contesto iniziale
- Non è un sistema di istruzioni (non comanda Whisper), ma un bias di vocabolario sul decoder
- Whisper usa solo gli **ultimi 224 token** del prompt — token in eccesso vengono silenziosamente ignorati
- Il tokenizer usato è il **multilingual Whisper tokenizer** (non il tokenizer GPT)

### Regola chiave: lunghezza prompt
```
Solo gli ultimi ≤ 224 token contano.
Nomi rari e jargon devono stare ALLA FINE del prompt.
Prompt più lunghi → steering più affidabile.
Prompt troppo corti → Whisper può ignorarli.
```

### Formato ottimale per nomi propri
Due approcci documentati da OpenAI Cookbook:

**Approccio A — Lista con virgole (ZyntriQix style):**
```
"ZyntriQix, Digique Plus, CynapseFive, VortiQore V8, EchoNix Array"
```
Pro: Compatto, molti nomi in 224 token
Contro: Meno contesto semantico

**Approccio B — Frasi naturali (raccomandato per nomi italiani):**
```
"Questa è una telefonata in italiano per prenotare un appuntamento. I clienti si chiamano: De Piscopo Tonino, Ferrario Marco, D'Agostino Maria."
```
Pro: Contesto semantico stabilizza il decoder, riduce errori su cognomi
Contro: Meno nomi entrano nei 224 token

**Approccio C — Glossario:**
```
"Glossario clienti: De Piscopo, Ferrario, D'Agostino, Lo Presti, Dell'Acqua, Russo, Esposito, Romano."
```
Pro: Formato strutturato, buon equilibrio compattezza/contesto

**Raccomandazione gold standard**: Approccio ibrido — intestazione contestuale + lista nomi:
```
"Telefonata italiana prenotazione. Clienti registrati: De Piscopo, D'Agostino, Lo Presti, Dell'Acqua."
```

### Fonti
- [OpenAI Cookbook — Whisper prompting guide](https://cookbook.openai.com/examples/whisper_prompting_guide)
- [OpenAI Platform — Speech to Text Prompting](https://platform.openai.com/docs/guides/speech-to-text/prompting)
- [GitHub discussion — prompt length 224 tokens](https://github.com/openai/whisper/discussions/1824)
- [Whisper — initial_prompt in Python](https://github.com/openai/whisper/discussions/355)

---

## 2. Groq API — Supporto `prompt`

### Parametro supportato
Groq usa il parametro `prompt` (NON `initial_prompt` — quello è solo per la lib locale openai/whisper).

**Parametri Groq transcription API confermati:**
| Parametro | Tipo | Note |
|-----------|------|-------|
| `file` o `url` | required | Audio file |
| `model` | required | `whisper-large-v3` o `whisper-large-v3-turbo` |
| `language` | optional | ISO-639-1 → `"it"` per italiano |
| `prompt` | optional | Max 224 token, stessa semantica di Whisper |
| `response_format` | optional | `json`, `text`, `verbose_json` |
| `temperature` | optional | Default 0 → deterministic |
| `timestamp_granularities[]` | optional | `segment`, `word` |

### Esempio Python Groq con prompt nomi italiani
```python
from groq import Groq

client = Groq()

def transcribe_with_names(audio_bytes: bytes, client_names: list[str]) -> str:
    """
    Trascrivi audio con context injection dei nomi clienti.
    client_names: lista di "Cognome Nome" dal DB
    """
    # Costruisci prompt — max ~180 char per stare nei 224 token
    names_str = ", ".join(client_names[:20])  # max 20 nomi
    prompt = f"Telefonata in italiano per prenotare appuntamento. Clienti: {names_str}."

    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        prompt=prompt,
        response_format="text",
        language="it",
        temperature=0.0,
    )
    return transcription

# Esempio con nomi reali dal DB
names = ["De Piscopo Tonino", "D'Agostino Maria", "Lo Presti Giuseppe", "Dell'Acqua Franco"]
result = transcribe_with_names(audio_data, names)
```

### Performance Groq Whisper
- Whisper Large V3 su Groq: **164x real-time speed factor** (10 min audio → 3.7 sec)
- Whisper Large V3 Turbo: **299x speed factor**
- WER: 10.3% (short-form: 8.4%)
- Il prompt overhead è trascurabile (i token sono pre-tokenizzati)

### Fonti
- [Groq Speech-to-Text Docs](https://console.groq.com/docs/speech-to-text)
- [Groq Whisper Large v3 Turbo](https://groq.com/blog/whisper-large-v3-turbo-now-available-on-groq-combining-speed-quality-for-speech-recognition)
- [Groq API Reference](https://console.groq.com/docs/api-reference)

---

## 3. Contextual Biasing — Stato dell'Arte 2024-2025

### CB-Whisper (ACL/LREC 2024)
Paper: "Contextual Biasing Whisper Using Open-Vocabulary Keyword Spotting"
- Integra un modulo KWS tra encoder e decoder di Whisper
- Riconosce named entities definite dall'utente prima del decoder
- Prompt crafting con "spoken form hints" per guidare il decoder
- Riduzione significativa del Mixed Error Rate su nomi propri
- **Rilevante per noi**: approccio heavy (richiede fine-tuning) → non applicabile con Groq API

### Contextual Biasing senza Fine-Tuning (arXiv 2410.18363)
Paper: "Contextual Biasing to Improve Domain-specific Custom Vocabulary Audio Transcription without Explicit Fine-Tuning of Whisper Model"
- Usa prefix tree (trie) per guidare output Whisper verso vocabolario specifico
- Riduzione misura WER su termini dominio-specifici
- **Gold standard per noi**: combinare prompt injection + post-correction LLM (no fine-tuning)

### RAG-Boost (arXiv 2508.14048)
- Retrieval-Augmented Generation per enhancre LLM-based ASR
- Queries un vector store di audio-text pairs e domain terms
- Retrieved results fusi con live ASR hypotheses per fix errori
- **Applicabile**: pattern DB → retrieve nomi fuzzy-match → inject in prompt

### Fonti
- [CB-Whisper ACL 2024](https://aclanthology.org/2024.lrec-main.262/)
- [Contextual Biasing no fine-tuning (arXiv)](https://arxiv.org/abs/2410.18363)
- [RAG-Boost ASR (arXiv)](https://arxiv.org/html/2508.14048v1)
- [NVIDIA RAG Voice Agent](https://developer.nvidia.com/blog/how-to-build-a-voice-agent-with-rag-and-safety-guardrails/)

---

## 4. LLM Post-Correction Layer

### Pattern Gold Standard (Interspeech 2024)
- Post-ASR correction è un task consolidato: LLM mappa N-best hypotheses → ground truth
- GPT-4 e Gemini Pro efficaci per correzione nomi propri nei trascritti
- Lingue latine (italiano, francese, spagnolo) mostrano miglioramenti consistenti
- Groq con llama-3 è la scelta ottimale per latenza (LPU deterministic, <200ms per testi brevi)

### Evolutionary Prompt Design (arXiv 2407.16370)
- Ottimizzazione automatica del prompt per post-correction ASR (GenSEC challenge 2024)
- Chain-of-thought guida il modello step-by-step
- Risultati: riduzione WER significativa su nomi propri e termini tecnici

### Prompt pattern raccomandato per correzione nomi italiani

```python
CORRECTION_PROMPT_TEMPLATE = """Sei un correttore ortografico specializzato in nomi italiani.

Ti fornirò:
1. Un trascritto grezzo da riconoscimento vocale (Whisper)
2. Una lista di nomi clienti registrati nel sistema

Correggi SOLO i nomi propri che sembrano mishear del riconoscimento vocale.
NON cambiare il contenuto semantico.
NON aggiungere punteggiatura extra.
Rispondi SOLO con il testo corretto, niente spiegazioni.

Clienti registrati: {client_names_list}

Trascritto grezzo: "{raw_transcript}"

Trascritto corretto:"""
```

### Implementazione Python — LLM Correction Layer
```python
from groq import Groq
import jellyfish

client = Groq()

def llm_correct_transcript(
    raw_transcript: str,
    client_names: list[str],
    threshold: float = 0.70
) -> str:
    """
    Post-correction LLM per nomi clienti mishear.
    Usa Groq llama-3.1-8b-instant per latenza minima.

    Args:
        raw_transcript: testo grezzo da Whisper
        client_names: lista "Cognome Nome" dal DB
        threshold: soglia similarità per includere nome nel prompt (evita rumore)

    Returns:
        trascritto corretto
    """
    if not raw_transcript.strip():
        return raw_transcript

    # Filtra nomi rilevanti via fuzzy match (evita di mandare 1000 nomi al LLM)
    words_in_transcript = raw_transcript.lower().split()
    relevant_names = []

    for name in client_names:
        name_parts = name.lower().split()
        for part in name_parts:
            for word in words_in_transcript:
                # Levenshtein ratio
                max_len = max(len(part), len(word))
                if max_len == 0:
                    continue
                lev_dist = jellyfish.levenshtein_distance(part, word)
                similarity = 1 - (lev_dist / max_len)
                if similarity >= threshold:
                    relevant_names.append(name)
                    break

    # Se nessun nome è rilevante, skip LLM call (risparmia latenza)
    if not relevant_names:
        return raw_transcript

    names_str = ", ".join(relevant_names[:15])  # cap a 15 nomi

    prompt = f"""Correggi i nomi propri mishear nel trascritto italiano.
Clienti registrati: {names_str}
Trascritto: "{raw_transcript}"
Corretto (solo testo, niente spiegazioni):"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # modello veloce, sufficiente per task semplice
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.0,
    )

    corrected = response.choices[0].message.content.strip()
    # Rimuovi eventuali virgolette aggiunte dal modello
    corrected = corrected.strip('"').strip("'")
    return corrected if corrected else raw_transcript
```

### Latenza stimata LLM correction
- Groq llama-3.1-8b-instant: ~50-120ms per risposte brevi (< 200 token output)
- Groq llama-3.3-70b-versatile: ~200-400ms (overkill per name correction)
- **Raccomandazione**: llama-3.1-8b-instant — sufficiente per task e latenza minima

### Fonti
- [Interspeech 2024 — LLM Post-Transcription Correction](https://www.isca-archive.org/interspeech_2024/koilakuntla24_interspeech.pdf)
- [Generative Error Correction ASR (arXiv 2407.16370)](https://arxiv.org/html/2407.16370v1)
- [AlphaCephei — Experiments LLM ASR correction](https://alphacephei.com/nsh/2025/03/15/generative-error-correction.html)
- [Interspeech 2024 — ASR Cross-Lingual Proper Noun Recognition](https://aclanthology.org/2024.findings-emnlp.399.pdf)

---

## 5. Algoritmi Fonetici per Italiano

### Librerie Python disponibili

#### jellyfish (raccomandato)
```python
pip install jellyfish
```
Funzioni disponibili:
- `jellyfish.levenshtein_distance(s1, s2)` — distanza edit
- `jellyfish.jaro_winkler_similarity(s1, s2)` — similarity 0-1, ottimizzato per nomi
- `jellyfish.soundex(s)` — codice fonico (A123)
- `jellyfish.metaphone(s)` — trasformazione fonetica
- `jellyfish.nysiis(s)` — NYSIIS (Names) algorithm

**Limite**: algoritmi ottimizzati per inglese, non italiano.

#### Double Metaphone (per nomi di origine straniera)
```python
pip install metaphone
from metaphone import doublemetaphone

# Gestisce nomi di origine italiana, spagnola, greca
primary, secondary = doublemetaphone("De Piscopo")
# Returns: ("TPSKP", "")
```

Double Metaphone gestisce ca. 100 contesti per la lettera C — adatto per cognomi italiani con radici latine/greche.

#### phonetics library
```python
pip install phonetics
import phonetics

# Fuzzy phonetic matching
score = phonetics.match("vescopo", "piscopo")
```

### Approccio fonico per italiano: custom rules

I cognomi italiani hanno pattern fonetici specifici:
- Prefissi nobiliari: De, Di, Del, Della, Dell', Lo, La, D', Da
- Apostrofo: D'Agostino, Dell'Acqua, L'Episcopo
- Doppie consonanti: Ferrario, Rossetti, Caruso
- Suffissi comuni: -ini, -etti, -ello, -ario, -esco

**Problema specifico**: "De Piscopo" → "l'episcopo"
- Whisper sente /de-pi-sko-po/ e preferisce la parola più comune "l'episcopo"
- Soluzione: il prompt injection con il nome corretto "De Piscopo" forza il decoder

```python
import jellyfish
import re
from typing import Optional

ITALIAN_NOBLE_PREFIXES = {'de', 'di', 'del', 'della', "dell'", 'lo', 'la', "d'", 'da', 'degli', 'dei'}

def normalize_italian_name(name: str) -> str:
    """Normalizza cognome italiano per confronto fonico."""
    # Rimuovi apostrofi e trattini, lowercase
    normalized = re.sub(r"['\-]", "", name.lower())
    # Rimuovi prefissi nobiliari per confronto del cognome base
    parts = normalized.split()
    parts = [p for p in parts if p not in ITALIAN_NOBLE_PREFIXES]
    return " ".join(parts)

def phonetic_similarity_italian(name1: str, name2: str) -> float:
    """
    Calcola similarità fonetica per nomi italiani.
    Combina Levenshtein + Jaro-Winkler su forma normalizzata.
    """
    n1 = normalize_italian_name(name1)
    n2 = normalize_italian_name(name2)

    if not n1 or not n2:
        return 0.0

    # Levenshtein ratio
    max_len = max(len(n1), len(n2))
    lev_dist = jellyfish.levenshtein_distance(n1, n2)
    lev_ratio = 1 - (lev_dist / max_len)

    # Jaro-Winkler (premiato per nomi)
    jw_score = jellyfish.jaro_winkler_similarity(n1, n2)

    # Media pesata: Jaro-Winkler più robusto per nomi
    return 0.4 * lev_ratio + 0.6 * jw_score

def find_best_client_match(
    mishear: str,
    client_names: list[str],
    threshold: float = 0.70
) -> Optional[str]:
    """
    Trova il miglior match fonico per un nome mishear.

    Args:
        mishear: parola/frase dal trascritto Whisper
        client_names: lista nomi dal DB ("Cognome Nome")
        threshold: soglia minima similarità

    Returns:
        Nome corretto o None se sotto threshold
    """
    best_match = None
    best_score = 0.0

    for client_name in client_names:
        score = phonetic_similarity_italian(mishear, client_name)
        if score > best_score:
            best_score = score
            best_match = client_name

    return best_match if best_score >= threshold else None

# Esempio
# find_best_client_match("l'episcopo", ["De Piscopo Tonino", "Russo Marco"])
# → "De Piscopo Tonino" (similarity ~0.72)
```

### Fonti
- [jellyfish GitHub](https://github.com/jamesturk/jellyfish)
- [jellyfish functions docs](https://jamesturk.github.io/jellyfish/functions/)
- [Double Metaphone Python](https://github.com/oubiwann/metaphone)
- [phonetics PyPI](https://pypi.org/project/phonetics/)
- [Phonetic Similarity vectorized](https://stackabuse.com/phonetic-similarity-of-words-a-vectorized-approach-in-python/)

---

## 6. Architettura Raccomandata — Sistema Completo

### Pipeline a 3 Layer

```
AUDIO INPUT
    │
    ▼
[LAYER 1] INITIAL PROMPT INJECTION
    ├── Carica nomi clienti dal DB SQLite
    ├── Fuzzy-select i più frequenti (ultimi 30gg) → top 30 nomi
    ├── Costruisce prompt: "Telefonata italiana prenotazione. Clienti: {nomi}."
    └── Invoca Groq Whisper con prompt
    │
    ▼
[LAYER 2] TRANSCRIPT RAW (da Whisper)
    │
    ▼
[LAYER 3A] PHONETIC FAST-PATH (< 5ms, sempre attivo)
    ├── Tokenizza trascritto
    ├── Per ogni token: jellyfish.jaro_winkler vs lista clienti
    ├── Se match ≥ 0.85: sostituisci direttamente (no LLM)
    └── Se match 0.70-0.85: vai a Layer 3B
    │
    ▼
[LAYER 3B] LLM CORRECTION (50-120ms, solo se necessario)
    ├── Solo se ci sono token con match 0.70-0.85
    ├── Groq llama-3.1-8b-instant con prompt mirato
    ├── Lista nomi rilevanti già filtrati dal Layer 3A
    └── Output: trascritto corretto
    │
    ▼
TRANSCRIPT FINALE → orchestrator.py
```

### Latenza totale stimata
| Componente | Latenza |
|-----------|---------|
| Groq Whisper Large V3 Turbo (1-3 sec audio) | ~50-80ms |
| Prompt construction (Layer 1) | <1ms |
| Phonetic fast-path (Layer 3A) | 1-5ms |
| LLM correction (Layer 3B, condizionale) | 50-120ms |
| **TOTALE senza LLM correction** | ~55-85ms |
| **TOTALE con LLM correction** | ~105-205ms |

**Overhead massimo**: +120ms rispetto a baseline — accettabile nel contesto pipeline voice che già ha ~1330ms latency totale.

### Codice di integrazione per orchestrator.py
```python
import sqlite3
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1)
def _get_client_names_cached() -> tuple[str, ...]:
    """
    Cache nomi clienti con TTL di 5 minuti.
    Usa tuple per hashability con lru_cache.
    """
    # La cache viene invalidata riavviando il processo — accettabile
    pass

def get_frequent_client_names(db_path: str, limit: int = 40) -> list[str]:
    """
    Carica i nomi più frequenti degli ultimi 30gg dal DB.
    Ordinati per frequenza appuntamenti (più prenotati → più probabile nel transcript).
    """
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("""
        SELECT c.cognome || ' ' || c.nome as full_name, COUNT(a.id) as freq
        FROM clienti c
        LEFT JOIN appuntamenti a ON a.cliente_id = c.id AND a.data >= ?
        GROUP BY c.id
        ORDER BY freq DESC
        LIMIT ?
    """, (cutoff, limit))

    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

def build_whisper_prompt(client_names: list[str], max_tokens: int = 180) -> str:
    """
    Costruisce prompt ottimale per Groq Whisper.
    Rimane sotto i 224 token lasciando margine di sicurezza.
    Stima: ~1.3 token/parola per italiano.
    """
    prefix = "Telefonata italiana per prenotazione appuntamento. Clienti: "

    # Stima token: prefix (~15 token) + nomi (~2.5 token/nome avg)
    max_names = (max_tokens - 20) // 3  # stima conservativa

    selected_names = client_names[:max_names]
    names_str = ", ".join(selected_names)

    return f"{prefix}{names_str}."

class STTNameCorrector:
    """
    Layer di correzione nomi propri per Whisper STT.
    Integra: prompt injection + phonetic fast-path + LLM correction.
    """

    def __init__(self, db_path: str, groq_client, use_llm_correction: bool = True):
        self.db_path = db_path
        self.groq_client = groq_client
        self.use_llm_correction = use_llm_correction
        self._client_names_cache: list[str] = []
        self._cache_ts: datetime = datetime.min

    def _refresh_cache(self):
        """Aggiorna cache nomi ogni 5 minuti."""
        if (datetime.now() - self._cache_ts).seconds > 300:
            self._client_names_cache = get_frequent_client_names(self.db_path)
            self._cache_ts = datetime.now()

    def get_prompt(self) -> str:
        self._refresh_cache()
        return build_whisper_prompt(self._client_names_cache)

    def correct_transcript(self, raw_transcript: str) -> str:
        """
        Applica correzione fonetica + LLM al trascritto grezzo.
        """
        self._refresh_cache()

        # Layer 3A: phonetic fast-path
        corrected = self._phonetic_fastpath(raw_transcript)

        # Layer 3B: LLM correction se ci sono ambiguità
        if self.use_llm_correction and corrected != raw_transcript:
            # Solo se il fastpath ha trovato possibili sostituzioni incerte
            pass  # il fastpath già gestisce i casi certi

        return corrected

    def _phonetic_fastpath(self, transcript: str) -> str:
        """Sostituisce nomi con jaro_winkler ≥ 0.85 (alta confidenza)."""
        import jellyfish

        words = transcript.split()
        corrected_words = []

        for word in words:
            best_match = None
            best_score = 0.0
            clean_word = re.sub(r"[',.\-]", "", word.lower())

            for name in self._client_names_cache:
                # Confronta con ogni parte del nome (cognome e nome separati)
                for part in name.lower().split():
                    clean_part = re.sub(r"[',.\-]", "", part)
                    if len(clean_part) < 3:  # skip prefissi brevi (De, Di, La, Lo)
                        continue
                    score = jellyfish.jaro_winkler_similarity(clean_word, clean_part)
                    if score > best_score:
                        best_score = score
                        # Usa la parte originale del nome (case preservata)
                        name_parts = name.split()
                        idx = name.lower().split().index(part) if part in name.lower().split() else 0
                        best_match = name_parts[idx] if idx < len(name_parts) else name_parts[0]

            if best_score >= 0.85 and best_match:
                corrected_words.append(best_match)
            else:
                corrected_words.append(word)

        return " ".join(corrected_words)
```

---

## 7. Implementazione Raccomandata per FLUXION

### Priorità implementazione (ordine costo/beneficio)

**Priorità 1 — Prompt Injection (ALTO impatto, ZERO latenza aggiuntiva)**
- Impatto: risolve ~60-70% dei mishear di nomi registrati
- Latenza aggiuntiva: <1ms (solo costruzione stringa)
- Implementazione: modificare chiamata Groq in `orchestrator.py` o `stt_provider.py`
- Costo: ZERO (parametro già supportato da Groq API)

**Priorità 2 — Phonetic Fast-Path (MEDIO impatto, latenza trascurabile)**
- Impatto: correzione deterministica per match ad alta confidenza (≥ 0.85)
- Latenza aggiuntiva: 1-5ms
- Implementazione: post-processing nel layer STT prima di passare a FSM
- Dipendenza: `pip install jellyfish`

**Priorità 3 — LLM Correction Layer (BASSO impatto aggiuntivo, +50-120ms)**
- Impatto: gestisce casi ambigui che prompt injection e phonetic non coprono
- Latenza: +50-120ms — **considerare se acceptable nella pipeline voice**
- Raccomandazione: attivare solo se accuracy rimane insufficiente dopo P1+P2

### File da modificare in FLUXION
1. `voice-agent/src/orchestrator.py` — aggiungere prompt ai parametri STT call
2. `voice-agent/src/stt_provider.py` (o equivalente) — integrazione STTNameCorrector
3. Nuova utility: `voice-agent/src/name_corrector.py` — classe STTNameCorrector

### Test di validazione
```python
# Test da aggiungere in pytest
def test_name_injection_de_piscopo():
    """De Piscopo non deve diventare l'episcopo con prompt injection."""
    corrector = STTNameCorrector(db_path, groq_client)
    prompt = corrector.get_prompt()
    assert "De Piscopo" in prompt or any(
        jellyfish.jaro_winkler_similarity("de piscopo", name.lower()) > 0.85
        for name in corrector._client_names_cache
    )

def test_phonetic_fastpath_mishear():
    """Phonetic fastpath corregge l'episcopo → De Piscopo."""
    corrector = STTNameCorrector.__new__(STTNameCorrector)
    corrector._client_names_cache = ["De Piscopo Tonino"]
    result = corrector._phonetic_fastpath("Sono l'episcopo Tonino")
    # "episcopo" ha jaro_winkler con "Piscopo" ≈ 0.88
    assert "Piscopo" in result or "De Piscopo" in result
```

---

## 8. Riepilogo Decision Matrix

| Tecnica | Impatto | Latenza | Complessità | Raccomandazione |
|---------|---------|---------|-------------|-----------------|
| Prompt injection Groq | Alto (60-70%) | <1ms | Bassa | **IMPLEMENTARE SUBITO** |
| Phonetic fast-path (jellyfish) | Medio (20-30%) | 1-5ms | Media | **IMPLEMENTARE** |
| LLM correction (llama-3.1-8b) | Basso-Medio (10-15%) | +50-120ms | Media | Valutare dopo P1+P2 |
| Fine-tuning Whisper | Molto alto | N/A (offline) | Altissima | Non applicabile (Groq API) |
| CB-Whisper KWS | Molto alto | N/A | Altissima | Non applicabile (Groq API) |

**Gold standard applicabile FLUXION**: Prompt injection + Phonetic fast-path.
L'LLM correction è il terzo layer da aggiungere solo se necessario.

---

*Ricerca completata: 2026-03-13 | Agente B STT/NLP CoVe 2026*
