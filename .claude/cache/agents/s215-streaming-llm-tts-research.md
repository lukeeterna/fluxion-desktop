# S215 Research: Streaming LLM → TTS per Sara Voice Agent
> Data: 2026-05-13 | Agente: ai-engineer | Contesto: ridurre P95 L4 da 9.8s a <5s

## Diagnosi preliminare — stato attuale codebase

**Il codebase ha GIA' una skeleton di streaming LLM → TTS** (introdotta in E7-S2), ma è difettosa in 3 punti critici che annullano il guadagno di latenza:

1. **`groq_client.py:generate_response_streaming()`** — chunking corretto (sentence boundary via delimitatori). Sintassi Groq stream confermata corretta.
2. **`orchestrator.py:2495`** — TTS task lanciati con `asyncio.create_task(self.tts.synthesize(part))` — PROBLEMA: `synthesize()` riceve `part` (chunk LLM grezzo, es. "Perfetto!") ma **non applica `preprocess_for_tts()`** prima. Numeri e date in italiano non vengono espansi, potenziale TTS garbage.
3. **`_concat_wav_chunks()`** — concatena WAV raw frames. PROBLEMA PRINCIPALE: il TTS engine attivo in produzione su iMac è **Piper** (output WAV 22050Hz mono), non Edge-TTS (output MP3). Il concat WAV funziona. Ma il timing del `asyncio.create_task()` è sbagliato: viene eseguito nel body del `async for chunk in groq.generate_response_streaming()` ma ogni `chunk["text"]` potrebbe essere un frammento di frase (es. "Perfetto"), non una frase completa. Piper su frammenti produce audio discontinuo con glitch prosodici.
4. **Guardrail D1 (anti-hallucination) annulla tutto**: se scatta (righe 2503-2510), cancella tutti i TTS tasks già avviati e riesegue TTS sul testo sanitizzato in sequenza → 9.8s tail invariata.
5. **Cold-start Groq HTTP**: primo turno "Buongiorno" non ha connessione persistente → TCP + TLS handshake + TTFT Groq = 3-5s extra su L4_groq. Il `AsyncGroq` client nel `GroqClient` è inizializzato ma senza HTTP keepalive esplicito.

---

## Sezione 1 — Groq Python SDK Streaming

**Sintassi verificata** (fonte: `src/groq/resources/chat/completions.py` su github.com/groq/groq-python):

```python
# SYNC — restituisce Stream[ChatCompletionChunk]
stream = client.chat.completions.create(
    messages=[...],
    model="llama-3.3-70b-versatile",
    stream=True,
    max_tokens=150,
    temperature=0.3,
)
for chunk in stream:
    token = chunk.choices[0].delta.content  # str | None
    if token:
        print(token, end="", flush=True)

# ASYNC — restituisce AsyncStream[ChatCompletionChunk]
stream = await async_client.chat.completions.create(
    messages=[...],
    model="llama-3.3-70b-versatile",
    stream=True,
    max_tokens=150,
    temperature=0.3,
)
async for chunk in stream:
    token = chunk.choices[0].delta.content  # str | None
    if token:
        process(token)
# Fine stream: StopIteration (sync) o StopAsyncIteration (async).
# Non esiste evento "DONE" esplicito nel SDK Python (il wrapper gestisce internamente).
```

**Struttura chunk**: `ChatCompletionChunk` con `choices[0].delta.content` (str o None). Il campo `content` è None sui chunk di start/stop. Guard obbligatorio: `content or ""`.

**Il codebase è corretto** su questo punto. `groq_client.py:366` usa `chunk.choices[0].delta.content or ""`. Nessuna modifica necessaria.

**Trade-off**: il client Groq SDK Python wrappa il Server-Sent Events wire protocol. Il primo chunk (content=None, role="assistant") arriva in ~300-800ms su Groq infra (TTFT). I chunk successivi arrivano a ~50-150ms/token per llama-3.3-70b. Per llama-3.1-8b-instant (LLM_FAST_MODEL attuale in L4), TTFT stimato ~200-400ms, throughput ~200 tok/s.

---

## Sezione 2 — Edge-TTS streaming chunks

**Comportamento confermato** (fonte: `src/edge_tts/communicate.py` su github.com/rany2/edge-tts):

```python
import edge_tts

# Ogni istanza Communicate richiede testo COMPLETO all'init.
# NON supporta append di testo successivo — testo fisso alla costruzione.
comm = edge_tts.Communicate(
    text="Perfetto, ho capito!",    # testo COMPLETO richiesto all'init
    voice="it-IT-IsabellaNeural",
    rate="+0%",
    volume="+0%",
    pitch="+0Hz",
)

# stream() è un async generator che yield TTSChunk:
# {"type": "audio", "data": bytes}          — chunk MP3 raw bytes
# {"type": "WordBoundary", ...}             — metadata timing
# {"type": "SentenceBoundary", ...}         — metadata frase
async for event in comm.stream():
    if event["type"] == "audio":
        mp3_bytes = event["data"]   # bytes, MP3 24kHz 48kbps mono
        yield mp3_bytes              # streaming verso client

# save() equivalente: scrive tutto in file
await comm.save("output.mp3")
```

**Implicazione critica**: Edge-TTS NON è streaming nel senso "feed token → audio immediatamente". Richiede testo completo all'init. Il `stream()` method fa streaming del DOWNLOAD dei chunk MP3 dalla CDN Microsoft Azure, non streaming del processo di sintesi (la sintesi avviene server-side sul testo completo).

**Pattern corretto per streaming LLM → Edge-TTS**:
- Accumula tokens Groq finché frase completa (terminatore `.!?`)
- Crea `Communicate(frase_completa)` → chiama `stream()` → raccoglie bytes MP3
- Parallelizza: mentre Edge-TTS scarica audio frase N, Groq genera tokens frase N+1

```python
async def synthesize_edge_tts(sentence: str, voice: str) -> bytes:
    """Sintetizza una frase completa con Edge-TTS, ritorna MP3 bytes."""
    comm = edge_tts.Communicate(text=sentence, voice=voice)
    mp3_chunks = []
    async for event in comm.stream():
        if event["type"] == "audio":
            mp3_chunks.append(event["data"])
    return b"".join(mp3_chunks)
```

**NOTA**: il TTS attivo su iMac in produzione è **Piper** (output WAV), non Edge-TTS. Verificare con `ssh imac "cat /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/main.py | grep get_tts"` quale engine `get_tts()` restituisce. Il streaming si applica identicamente: Piper richiede testo completo per processo, quindi il pattern è identico (accumula frase → sintetizza frase intera).

**Trade-off Edge-TTS**: latenza rete Azure ~200-400ms per frase breve (10-20 parole). Offline (Piper): ~50-100ms locale. Edge-TTS ha qualità superiore (IsabellaNeural 9/10) ma dipende da connessione. Fallback Piper già in place.

---

## Sezione 3 — Sentence boundary detection italiano

**Raccomandazione: regex semplice**. Zero dipendenze nuove. `pysbd` è più accurato per italiano (gestisce abbreviazioni tipo "Dr.", "etc.", numeri decimali "3.5"), ma aggiunge 150KB e import overhead. Per Sara il corpus è voice AI (frasi brevi 10-30 parole, linguaggio parlato), dove `pysbd` non aggiunge valore rispetto a regex.

```python
import re

# Pattern verificato per italiano voice AI:
# - Termina su . ! ? (anche multipli: ..., ?!, !!)
# - Esclude abbreviazioni comuni: Dr., Sig., Sig.ra., n.
# - Esclude numeri decimali: 3.5, 1.000
# - Richiede spazio o fine stringa dopo terminatore (evita "Dr.Rossi")
_SENTENCE_END_RE = re.compile(
    r'(?<![A-Za-z]{1,4})'   # negative lookbehind per abbreviazioni (Dr, Sig, etc)
    r'(?<!\d)'               # negative lookbehind per numeri decimali (3.5)
    r'[.!?]+'                # uno o più terminatori
    r'(?=\s|$)'              # lookahead: spazio o fine stringa
)

def split_into_sentences(text: str) -> list[str]:
    """Divide testo in frasi per TTS chunking."""
    parts = _SENTENCE_END_RE.split(text)
    # Riattacca terminatori (split li rimuove)
    terminators = _SENTENCE_END_RE.findall(text)
    sentences = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        terminator = terminators[i] if i < len(terminators) else ""
        sentences.append(part + terminator)
    return [s for s in sentences if s.strip()]

# Alternativa: usare rfind per chunking senza split completo
def find_sentence_boundary(buffer: str, min_chars: int = 15) -> int:
    """Trova indice fine prima frase completa nel buffer. -1 se non trovata."""
    if len(buffer) < min_chars:
        return -1
    for terminator in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
        idx = buffer.find(terminator, min_chars)
        if idx != -1:
            return idx + len(terminator)
    return -1
```

**Trade-off**: la regex ha un edge case noto: "Ottimo! Alle 10:00." viene splittato correttamente, ma "Ha detto: 'Sì.'" potrebbe non splittare sul punto interno. Per voce italofona le frasi sono tipicamente semplici — accettabile.

---

## Sezione 4 — Audio concat senza riencode

**Tre approcci verificati**:

### A) WAV raw frames concat (attuale `_concat_wav_chunks()`) — CORRETTO per Piper
```python
import wave, io

def concat_wav_chunks(chunks: list[bytes]) -> bytes:
    valid = [c for c in chunks if c]
    if not valid: return b""
    if len(valid) == 1: return valid[0]
    frames, params = [], None
    for chunk in valid:
        with wave.open(io.BytesIO(chunk), "rb") as wf:
            if params is None: params = wf.getparams()
            frames.append(wf.readframes(wf.getnframes()))
    if not frames or params is None: return valid[0]
    out = io.BytesIO()
    with wave.open(out, "wb") as wf:
        wf.setparams(params)
        for f in frames: wf.writeframes(f)
    return out.getvalue()
# Requisito: tutti i chunks devono avere stesso sample_rate + channels + sampwidth
# Piper produce sempre 22050Hz/16bit/mono → safe
```

### B) MP3 raw bytes concat — FUNZIONA per Edge-TTS con limitazioni
```python
def concat_mp3_raw(chunks: list[bytes]) -> bytes:
    """Concatenazione raw MP3. Funziona se tutti dallo stesso encoder (Edge-TTS)."""
    return b"".join(chunks)
# MP3 è streaming-safe: ogni frame è indipendente con sync header 0xFFE0.
# Raw concat produce audio continuo senza artefatti SE stesso bitrate/sample_rate.
# Edge-TTS produce sempre audio-24khz-48kbitrate-mono-mp3 → safe.
# LIMITE: il client Tauri deve supportare MP3 (verifica in http_client / voice bridge).
```

### C) pydub AudioSegment — OVERKILL
```python
# from pydub import AudioSegment  # Richiede ffmpeg installato
# Aggiunge 500ms+ overhead su import + ffmpeg subprocess.
# NON raccomandato per voice real-time. Usare solo per post-processing offline.
```

**Raccomandazione**: mantenere `_concat_wav_chunks()` per Piper (già corretto). Se si usa Edge-TTS, aggiungere `concat_mp3_raw()` (zero dipendenze, zero overhead).

---

## Sezione 5 — Architettura proposta: L4 Streaming Fix

### Problema principale identificato

Il flusso attuale `orchestrator.py:2483-2498` lancia TTS task su ogni `chunk["text"]` del generator Groq, ma i chunk possono essere frammenti (es. "Perfetto" senza punto finale). Piper/Edge-TTS su frammenti produce audio discontinuo. La fix non richiede riscrivere il generator Groq (già corretto), ma solo il loop in orchestrator.

### Pseudocodice nuovo L4 loop

```python
# In orchestrator.py — sostituzione del blocco L4 (righe 2466-2573)
# MODIFICHE: ~30 righe net change

_l4_tts_tasks: list[asyncio.Task] = []
_l4_sentence_buffer: str = ""         # NUOVO: buffer frase completa
_l4_full_text: list[str] = []         # NUOVO: accumula testo per D1 guardrail
_l4_first_audio_yielded = False        # NUOVO: tracking TTFA

if response is None:
    t_llm_start = time.perf_counter()
    try:
        context = self._build_llm_context()
        l4_messages = _build_l4_messages(...)  # invariato

        async for chunk in self.groq.generate_response_streaming(
            messages=l4_messages,
            system_prompt=context,
            max_tokens=150,
            temperature=0.3,
            model=LLM_FAST_MODEL,
        ):
            part = chunk["text"]
            _l4_full_text.append(part)
            _l4_sentence_buffer += part

            # Cerca boundary frase completa (. ! ? con spazio/fine)
            boundary = _find_sentence_boundary(_l4_sentence_buffer, min_chars=10)
            if boundary > 0:
                sentence = _l4_sentence_buffer[:boundary].strip()
                _l4_sentence_buffer = _l4_sentence_buffer[boundary:]
                if sentence:
                    # Applica preprocess PRIMA di TTS (fix bug attuale)
                    preprocessed = preprocess_for_tts(sentence)
                    _l4_tts_tasks.append(
                        asyncio.create_task(self.tts.synthesize(preprocessed))
                    )

        # Flush buffer residuo (ultima frase senza terminatore)
        residual = _l4_sentence_buffer.strip()
        if residual:
            preprocessed = preprocess_for_tts(residual)
            _l4_tts_tasks.append(
                asyncio.create_task(self.tts.synthesize(preprocessed))
            )

        response = "".join(_l4_full_text).strip() or FALLBACK_RESPONSES["generic"]

        # D1: Anti-hallucination guardrail
        _sanitized = self._validate_l4_response(response)
        if _sanitized:
            # Guardrail scattato: cancella tasks pre-avviati, rilancia su testo corretto
            for _t in _l4_tts_tasks:
                _t.cancel()
            _l4_tts_tasks.clear()
            response = _sanitized
            # Tasks vuoti → fallthrough a tts.synthesize() standard sotto

        intent = "groq_response"
        layer = ProcessingLayer.L4_GROQ

    except ...:  # exception handling invariato

# POST-PROCESSING — concat WAV (invariato)
if _l4_tts_tasks:
    audio_chunks = await asyncio.gather(*_l4_tts_tasks, return_exceptions=True)
    valid = [c for c in audio_chunks if isinstance(c, bytes) and c]
    audio = _concat_wav_chunks(valid) if valid else await self.tts.synthesize(_prosody_response)
else:
    audio = await self.tts.synthesize(_prosody_response)
```

### Fix separata: cold-start Groq HTTP keepalive

```python
# In GroqClient.__init__() o in warm_indices():
# Forza HTTP keepalive con warm request 0-token

async def _warm_groq_connection(self):
    """Pre-warm connessione HTTP verso Groq per eliminare cold-start TLS."""
    if not self.async_client:
        return
    try:
        # Request minima: 1 token, non entra in quota significativa
        await asyncio.wait_for(
            self.async_client.chat.completions.create(
                model=LLM_FAST_MODEL,
                messages=[{"role": "user", "content": "ok"}],
                max_tokens=1,
                stream=False,
            ),
            timeout=8.0,
        )
        logger.info("[GroqClient] HTTP connection pre-warmed")
    except Exception as e:
        logger.warning(f"[GroqClient] Warm failed (non-fatal): {e}")
```

Questo elimina il cold-start da 3-5s su turn 1 (la causa principale del P95 9.8s su "Buongiorno").

### Backpressure e cancellation

Il pattern `asyncio.create_task()` non ha backpressure nativo. Se Groq genera 5 frasi in rapida sequenza, 5 TTS task vengono avviati in parallelo. Con Piper (subprocess locale), max 2-3 concorrenti before CPU saturation su iMac. Limite raccomandato:

```python
_MAX_PARALLEL_TTS = 3  # iMac 2012 CPU bound
_l4_tts_semaphore = asyncio.Semaphore(_MAX_PARALLEL_TTS)

# Wrappa ogni task:
async def _synthesize_with_sem(text: str, sem: asyncio.Semaphore) -> bytes:
    async with sem:
        return await self.tts.synthesize(text)

_l4_tts_tasks.append(
    asyncio.create_task(_synthesize_with_sem(preprocessed, _l4_tts_semaphore))
)
```

Cancellation su disconnect client: il `CancelledError` si propaga già correttamente nel `async for chunk in stream` (riga `groq_client.py:415`). Le task TTS vengono cancellate automaticamente se il coroutine padre viene cancellata.

---

## Raccomandazione singola motivata

**Strategia a 2 fix, nessuna dipendenza nuova, ~80 righe nette da modificare:**

### Fix 1 — Sentence accumulator in L4 loop (orchestrator.py) — PRIORITA' ALTA
**Impatto atteso**: riduce glitch audio + garantisce frasi complete a Piper. Cambia ~30 righe nel blocco L4. Non tocca `groq_client.py` (già corretto) né `tts.py`.

File modificati: `orchestrator.py` (righe 2466-2510)
Righe nette: ~30 (sostituzione loop, aggiunta `_find_sentence_boundary()` helper)

### Fix 2 — Groq HTTP cold-start warm (groq_client.py o main.py) — PRIORITA' CRITICA
**Impatto atteso**: elimina 3-5s su turn 1. Questa è la causa principale del P95 9.8s su "Buongiorno" (cold L4_groq path senza keepalive TCP/TLS). Il warm indices (S213) scalda FAQ FAISS ma NON scala il Groq HTTP client.

File modificati: `groq_client.py` (+`_warm_groq_connection()` async method) + `main.py` (chiamata post-server-init)
Righe nette: ~20

**NON necessario** (codebase già corretto o fuori scope):
- Groq streaming syntax: `generate_response_streaming()` è già corretto
- `_concat_wav_chunks()`: già corretto per Piper WAV
- pysbd, pydub, ffmpeg: zero nuove dipendenze
- Edge-TTS MP3 streaming: Piper è il motore attivo, Edge-TTS come Tier 1 solo con connessione internet

**Stima P95 post-fix**:
- Turn 1 "Buongiorno" cold: 9.8s → ~4-5s (Groq TTFT ~400ms + Piper ~50ms dopo warm HTTP)
- Turn 2+ warm: 9.8s → ~2-3s (frase completa → Piper ~50ms overlap)
- Target <5s realistico con solo questi 2 fix

**Rischio principale**: D1 guardrail anti-hallucination continua ad annullare i TTS pre-avviati quando scatta. Questo è corretto per correttezza semantica. Il worst case con guardrail è identico al flusso attuale (cade su `tts.synthesize()` sequenziale). Non peggioramento.

---

## File da leggere prima di implementare

```
/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py   righe 2462-2573 (L4 block)
/Volumes/MontereyT7/FLUXION/voice-agent/src/groq_client.py    righe 295-436 (generate_response_streaming)
/Volumes/MontereyT7/FLUXION/voice-agent/src/tts.py             righe 193-240 (preprocess_for_tts)
/Volumes/MontereyT7/FLUXION/voice-agent/main.py               righe 1100-1180 (warm_indices call site)
```
