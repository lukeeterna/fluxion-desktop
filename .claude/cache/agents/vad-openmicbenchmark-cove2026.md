# VAD Open-Mic — Benchmark Leader Mondiali (CoVe 2026)

> Agente A — Research completato: 2026-03-14
> Stack analizzato: Retell AI, Vapi.ai, Nuance, Twilio Voice, Google CCAI
> Codebase analizzata: FluxionVAD (Silero ONNX), VADPipelineManager, VADHTTPHandler

---

## Gold Standard Architetturale

### Il modello 2026: Full-Duplex Continuous Listening

Il gold standard 2026 per voice agent su chiamate telefoniche è il **full-duplex streaming continuo** con VAD sempre attivo — non il modello "push-to-talk" o "attendi fine frase". I leader (Retell, Vapi, Google CCAI) operano in modalità in cui il microfono non viene mai chiuso tra turni. L'audio è sempre in ingresso; è il **software** a decidere quando elaborare.

**Pattern architetturale gold standard:**

```
CHIAMATA IN CORSO
     │
     ▼
┌────────────────────────────────────────────┐
│         ALWAYS-ON AUDIO PIPELINE           │
│                                            │
│  Audio stream (16kHz mono PCM) ──────────► │
│                                            │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │  Echo AEC   │──► │  Silero VAD      │   │
│  │  (sempre ON)│    │  (32ms chunks)   │   │
│  └─────────────┘    └──────┬───────────┘   │
│                            │               │
│                     SPEECH_START           │
│                            │               │
│                    ┌───────▼────────┐      │
│                    │  Audio Buffer  │      │
│                    │  (con prefix)  │      │
│                    └───────┬────────┘      │
│                            │               │
│                     SPEECH_END             │
│                     (700ms silence)        │
│                            │               │
│                    ┌───────▼────────┐      │
│                    │  STT (Whisper) │      │
│                    │  → FSM → LLM   │      │
│                    │  → TTS (Piper) │      │
│                    └───────┬────────┘      │
│                            │               │
│              TTS_PLAY ◄────┘               │
│              (con barge-in guard attivo)   │
└────────────────────────────────────────────┘
     │
     ▼
LOOP CONTINUO — MAI CHIUDE IL MIC
```

**La differenza critica**: dopo che Sara risponde (TTS), il VAD NON viene spento. Il microfono resta aperto. L'utente può interrompere in qualsiasi momento.

---

## Come Retell/Vapi Implementano Continuous Listening

### Retell AI (architettura documentata)

Retell usa il modello **WebRTC full-duplex**:

1. **Trasporto**: WebRTC DataChannel o WebSocket per audio bidirezionale simultaneo
2. **VAD client-side**: Silero VAD eseguito lato server, riceve chunk audio continui dal client
3. **Barge-in**: Quando viene rilevato speech durante TTS playback, Retell invia un segnale `interrupt` al client e interrompe la riproduzione audio corrente
4. **End-of-turn**: Retell usa una combinazione di:
   - VAD silence detection (default ~500ms)
   - "Endpointing model" addestrato su dati reali di fine frase (non solo silenzio)
   - Semantica parziale: se il trascritto parziale forma una frase grammaticalmente completa, può anticipare la fine turno
5. **Echo cancellation**: lato client (WebRTC built-in AEC), NON lato server. Il server riceve già audio pulito.

**Pattern chiave Retell**: il server mantiene uno stato `AGENT_SPEAKING` e `USER_SPEAKING` come mutex parziale — quando `AGENT_SPEAKING=true`, i chunk audio in arrivo vengono comunque processati dal VAD per barge-in detection, ma non si avvia STT finché non c'è barge-in confermato.

### Vapi.ai (architettura documentata)

Vapi è costruito sopra WebRTC e usa:

1. **Turn detection dual-mode**:
   - `server_vad`: VAD gestito dal server (Silero) — più accurato, latenza turno ~500ms
   - `semantic_vad`: analisi semantica del trascritto parziale — anticipa fine turno a ~200ms
   - Configurabile via `transcriber.smartEndpointingEnabled`

2. **Smart endpointing**: Vapi usa "smart endpointing" — il trascritto parziale (streaming Deepgram/Whisper) viene analizzato semanticamente. Se l'utente ha detto una frase completa (es. "voglio prenotare martedì"), non si aspetta il silenzio di 700ms.

3. **Barge-in threshold**: Vapi usa `interruptionsEnabled` con un threshold configurabile in ms. Default: 100ms di speech continuo per interrompere TTS.

4. **Loop continuo**: Vapi mantiene una WebSocket aperta per tutta la durata della chiamata. Audio stream IN e OUT sono sullo stesso canale full-duplex. Il VAD è sempre attivo.

**Struttura messaggi Vapi WebSocket** (pattern):
```json
// Client → Server (audio chunk)
{"type": "audio", "audio": "<base64 PCM>", "ts": 1234567890}

// Server → Client (barge-in signal)
{"type": "interrupt", "reason": "user_speech_detected"}

// Server → Client (TTS audio chunk)
{"type": "audio", "audio": "<base64 PCM>", "delta": true}
```

### Pattern comune Retell + Vapi

| Aspetto | Retell | Vapi | Standard derivato |
|---------|--------|------|-------------------|
| Trasporto | WebRTC/WS | WebRTC/WS | WebSocket streaming |
| VAD | Silero server-side | Silero + semantic | Silero continuo |
| Silence threshold | ~500ms | ~500ms | 500-700ms |
| Barge-in | ✅ sempre | ✅ configurabile | Obbligatorio |
| Echo cancellation | WebRTC AEC | WebRTC AEC | AEC lato client |
| Endpointing | Silenzio | Silenzio + semantica | Silenzio ≥ smart |
| Turn model | Mutex parziale | Mutex parziale | SPEAKING flag |

---

## Silero VAD Streaming — Pattern 2026

### Implementazione corrente FLUXION (analisi)

Il codice attuale in `ten_vad_integration.py` implementa già Silero v5 correttamente:
- Chunk size: 512 samples (32ms @ 16kHz) — **CORRETTO** per Silero v5
- Hidden state RNN mantenuto tra chunk: **CORRETTO**
- Silence detection: 700ms (21 chunks a 32ms) — **CORRETTO**
- Prefix padding: 300ms — **CORRETTO**

**Gap identificato**: il VAD viene usato per singola request HTTP, non per una sessione continua. In `vad_http_handler.py`, `process_with_vad_handler` crea un nuovo `FluxionVAD`, processa l'audio e poi chiama `vad.stop()`. Questo è il modello **request/response** — **NON** open-mic continuo.

### Pattern open-mic gold standard per Silero

```python
# PATTERN GOLD STANDARD — sessione continua
class OpenMicSession:
    """
    Sessione VAD continua per telefonata Sara.
    Il VAD resta attivo per tutta la durata della chiamata.
    """

    def __init__(self):
        self.vad = FluxionVAD(VADConfig(
            vad_threshold=0.5,
            silence_duration_ms=600,   # 600ms gold standard per telefonia
            prefix_padding_ms=200,      # 200ms prefix
        ))
        self.vad.start()  # UNA VOLTA — non stop/start tra turni

        # Stato sessione
        self.sara_speaking = False       # TTS in corso
        self.speech_buffer = bytearray()
        self.turn_count = 0

    def process_audio_chunk(self, pcm_chunk: bytes) -> Optional[bytes]:
        """
        Chiamato ogni 32ms per ogni chunk audio in arrivo.
        Ritorna l'audio del turno completo quando end_of_speech.
        """
        result = self.vad.process_audio(pcm_chunk)  # MAI stop() tra turni

        if result.event == "start_of_speech":
            if self.sara_speaking:
                self._handle_barge_in()  # Interrompi TTS
            self.speech_buffer = bytearray(pcm_chunk)

        elif result.state == VADState.SPEAKING:
            self.speech_buffer.extend(pcm_chunk)

        elif result.event == "end_of_speech":
            complete_audio = bytes(self.speech_buffer)
            self.speech_buffer = bytearray()
            self.turn_count += 1
            return complete_audio  # → STT → FSM → LLM → TTS

        return None

    def set_sara_speaking(self, speaking: bool):
        """Aggiorna stato TTS — usato per barge-in detection."""
        self.sara_speaking = speaking
        if not speaking:
            # Dopo TTS: reset VAD hidden state è SBAGLIATO
            # Il VAD deve continuare senza interruzione
            pass

    def close(self):
        """Fine chiamata — SOLO qui si chiude il VAD."""
        self.vad.stop()
```

**Regola critica**: `vad.reset()` va chiamato SOLO se si vuole ignorare il contesto precedente (es. dopo errore). NON va chiamato tra un turno utente e il turno Sara. Lo stato RNN nascosto di Silero mantiene contesto utile.

### Silero v5 — Parametri Ottimali per Telefonia Italiana

| Parametro | Valore attuale | Raccomandato | Note |
|-----------|----------------|--------------|------|
| `vad_threshold` | 0.5 | **0.45-0.5** | 0.4 per ambiente rumoroso |
| `silence_duration_ms` | 700 | **600ms** | Italiano: pause brevi frequenti |
| `prefix_padding_ms` | 300 | **200ms** | Sufficiente per Silero v5 |
| `min_speech_ms` | 500 | **400ms** | Evita falsi positivi brevi |
| Reset tra turni | N/A | **NO reset** | Mantieni hidden state RNN |

---

## Barge-in Pattern

### Definizione

Barge-in = l'utente parla mentre Sara sta rispondendo (TTS in riproduzione). Il sistema deve:
1. **Rilevare** il barge-in (VAD sempre attivo)
2. **Interrompere** il TTS immediatamente
3. **Processare** quello che l'utente sta dicendo

### Pattern implementazione per FLUXION

```python
# Nel gestore della sessione telefonica

class BargeInHandler:
    """
    Gestisce l'interruzione del TTS quando l'utente parla.
    """

    BARGE_IN_THRESHOLD_MS = 200  # Silenzio minimo prima di accettare barge-in

    def __init__(self, tts_player, vad_manager):
        self.tts_player = tts_player
        self.vad_manager = vad_manager
        self._sara_speaking = False
        self._barge_in_speech_ms = 0
        self._barge_in_start = None

    def on_vad_speech_start(self):
        """Callback VAD: utente inizia a parlare."""
        if self._sara_speaking:
            # Inizia a misurare quanto parla l'utente
            self._barge_in_start = time.time()

    def on_audio_chunk_during_tts(self, vad_result):
        """Chiamato ogni chunk mentre Sara parla."""
        if not self._sara_speaking:
            return

        if vad_result.state == VADState.SPEAKING:
            if self._barge_in_start:
                elapsed_ms = (time.time() - self._barge_in_start) * 1000
                if elapsed_ms >= self.BARGE_IN_THRESHOLD_MS:
                    # Barge-in confermato: interrompi TTS
                    self.tts_player.stop()
                    self._sara_speaking = False
                    logger.info(f"Barge-in confermato dopo {elapsed_ms:.0f}ms")
```

**Implementazione FLUXION già parziale**: `VADPipelineManager` in `vad_pipeline_integration.py` già ha `set_speaking()` e rileva `barge_in_detected`. Il gap è che questo manager non è collegato alla sessione telefonica continua.

### Soglia barge-in raccomandata

| Sistema | Threshold default | Note |
|---------|------------------|------|
| Retell | ~100ms | Aggressivo — preferisce reattività |
| Vapi | 100-200ms | Configurabile |
| Google CCAI | 200-300ms | Conservativo — evita falsi |
| **FLUXION racccomandato** | **200ms** | Bilanciato per italiano |

---

## Echo Cancellation

### Il problema

Quando Sara parla (TTS → altoparlante), il microfono capta l'audio di Sara. Il VAD potrebbe rilevare l'audio di Sara come "speech dell'utente" → falsi barge-in → loop infinito.

### Soluzioni per contesto FLUXION

**Contesto attuale**: FLUXION Sara è un voice agent per telefonate. Il canale telefonico (VoIP SIP) ha già AEC (Acoustic Echo Cancellation) integrata nella maggior parte degli endpoint telefonici. Gli smartphone e telefoni IP fanno AEC hardware.

**Per l'HTTP endpoint (test da MacBook)**:
- WebRTC (se usato) ha AEC built-in
- Per test HTTP diretto: non c'è AEC → si usano cuffie

**Strategie software per echo suppression**:

1. **Gate temporale** (più semplice, efficace per VoIP):
   - Quando Sara sta parlando (TTS), aumenta il threshold VAD da 0.5 a **0.7**
   - Riduce falsi positivi causati dall'eco del parlato di Sara
   - Codice: `vad.config.vad_threshold = 0.7 if sara_speaking else 0.5`

2. **Blackout window** (gold standard semplice):
   - Ignora completamente il VAD per i primi 200ms dall'inizio del TTS playback
   - Permette all'audio di Sara di "stabilizzarsi" nel canale
   - Dopo 200ms, barge-in detection torna attiva

3. **Echo reference signal** (avanzato, richiede hardware):
   - Invia il segnale TTS come "reference" all'algoritmo AEC
   - Non applicabile per telefonia esterna

4. **VAD gating + probability smoothing** (gold standard):
   ```python
   if sara_speaking:
       # Durante TTS: richiedi confidence più alta per barge-in
       effective_threshold = 0.75
       min_barge_in_ms = 300  # più conservativo
   else:
       effective_threshold = 0.5
       min_barge_in_ms = 200
   ```

**Raccomandazione per FLUXION**: implementare **gate temporale + soglia adattiva**. È la soluzione più robusta senza richiedere AEC hardware o librerie aggiuntive.

---

## Full-Duplex vs Half-Duplex

### Definizioni

| Modalità | Descrizione | Esempio |
|----------|-------------|---------|
| **Half-duplex** | Uno parla alla volta, alternato. Push-to-talk. | Walkie-talkie |
| **Full-duplex** | Entrambi possono parlare simultaneamente. | Telefono normale |
| **Full-duplex simulato** | Half-duplex con barge-in rapido (<200ms) | Retell, Vapi |

### Architettura attuale FLUXION

L'architettura attuale è **half-duplex**: si aspetta che l'utente finisca di parlare (end_of_speech), poi elabora, poi risponde. Il microfono è implicitamente "chiuso" mentre Sara risponde perché non c'è un loop continuo di ascolto.

**Gap**: dopo che il TTS è completato, il sistema non si rimette immediatamente in ascolto in modo proattivo. Deve aspettare la prossima request HTTP dall'utente.

### Gold standard: Full-duplex simulato

Per un voice agent telefonico, il **full-duplex simulato** è il target corretto:
- Audio in arrivo sempre bufferizzato
- VAD sempre running su audio in arrivo
- Se VAD rileva speech → barge-in (se TTS attivo) o nuovo turno (se idle)
- Il "full-duplex vero" (entrambi parlano contemporaneamente) non è utile per booking — nessuno parla sopra Sara per un booking reale

### Implementazione consigliata per FLUXION

```
SESSIONE TELEFONICA CONTINUA
├── Thread/Task A: Audio INPUT sempre attivo
│   └── → VAD chunk processing (32ms loop)
│       ├── IDLE → attesa speech
│       ├── SPEAKING → buffer accumulo
│       └── end_of_speech → trigger STT/FSM/TTS
│
└── Thread/Task B: Audio OUTPUT (TTS)
    ├── Riceve audio TTS da Piper
    ├── Notifica Task A: sara_speaking=True
    ├── Riproduce audio
    └── Fine: notifica Task A: sara_speaking=False
```

---

## Pattern Architetturale: Speak → Listen → Speak → Listen (Loop Continuo)

### Implementazione gold standard (applicata a FLUXION)

```python
class SaraPhoneSession:
    """
    Sessione telefonica Sara con open-mic continuo.
    Questo è il pattern gold standard per voice agent telefonici 2026.
    """

    STATE_IDLE = "idle"           # Nessuno parla
    STATE_USER_SPEAKING = "user"  # Utente parla
    STATE_SARA_PROCESSING = "proc" # STT/FSM/LLM in corso
    STATE_SARA_SPEAKING = "sara"  # TTS in riproduzione

    def __init__(self, orchestrator, tts, call_id):
        self.orchestrator = orchestrator
        self.tts = tts
        self.call_id = call_id

        # VAD sempre attivo per tutta la sessione
        self.vad = FluxionVAD(VADConfig(
            vad_threshold=0.5,
            silence_duration_ms=600,
            prefix_padding_ms=200,
        ))
        self.vad.start()

        self.state = self.STATE_IDLE
        self.speech_buffer = bytearray()
        self._processing_lock = asyncio.Lock()

    async def on_audio_chunk(self, pcm_chunk: bytes):
        """
        Chiamato ogni 32ms dal carrier telefonico (SIP/RTP).
        Questo è il cuore del loop continuo.
        """
        result = self.vad.process_audio(pcm_chunk)

        if result.event == "start_of_speech":
            if self.state == self.STATE_SARA_SPEAKING:
                # BARGE-IN: utente interrompe Sara
                await self._handle_barge_in()
            self.state = self.STATE_USER_SPEAKING
            self.speech_buffer = bytearray(pcm_chunk)

        elif result.state == VADState.SPEAKING:
            if self.state == self.STATE_USER_SPEAKING:
                self.speech_buffer.extend(pcm_chunk)

                # Protezione max turn
                if len(self.speech_buffer) > 16000 * 2 * 30:  # 30s
                    await self._force_end_turn()

        elif result.event == "end_of_speech":
            if self.state == self.STATE_USER_SPEAKING:
                audio = bytes(self.speech_buffer)
                self.speech_buffer = bytearray()
                self.state = self.STATE_SARA_PROCESSING

                # Non aspettare — fire and forget con asyncio
                asyncio.create_task(self._process_turn(audio))

    async def _process_turn(self, audio: bytes):
        """
        Pipeline completa: STT → FSM → LLM → TTS.
        Il VAD continua a girare in background durante questa fase.
        """
        async with self._processing_lock:
            try:
                # STT
                transcription = await stt.transcribe(audio)
                if not transcription:
                    self.state = self.STATE_IDLE
                    return

                # FSM + LLM
                result = await self.orchestrator.process(
                    user_input=transcription,
                    session_id=self.call_id
                )

                # TTS
                if result.audio_bytes:
                    self.state = self.STATE_SARA_SPEAKING
                    await self._play_tts(result.audio_bytes)

                # Dopo TTS: torna in ascolto automaticamente
                self.state = self.STATE_IDLE
                # VAD è ancora attivo — pronto per prossimo turno

            except Exception as e:
                logger.error(f"Turn processing error: {e}")
                self.state = self.STATE_IDLE

    async def _handle_barge_in(self):
        """Interrompi TTS, prepara per nuovo input utente."""
        self.tts.interrupt()  # Stoppa riproduzione audio
        logger.info(f"[{self.call_id}] Barge-in: Sara interrotta dall'utente")

    async def close(self):
        """Fine chiamata."""
        self.vad.stop()  # SOLO qui si chiude il VAD
        logger.info(f"[{self.call_id}] Sessione chiusa dopo {self.vad} turni")
```

### Integrazione con pipeline HTTP attuale

Il problema FLUXION attuale è che il server è **request/response HTTP** — non ha un loop continuo. Per VoIP (F15 SIP), il loop continuo sarà naturale perché il canale RTP è un stream continuo. Per l'integrazione Tauri (frontend), il loop va emulato con polling rapido o WebSocket.

**Opzioni implementative**:

| Opzione | Complessità | Latenza | Note |
|---------|-------------|---------|------|
| Polling HTTP rapido (50ms) | Bassa | ~50ms | Già compatibile con architettura attuale |
| WebSocket streaming | Media | ~5ms | Ideale per app Tauri |
| VoIP SIP/RTP nativo | Alta | 0ms | F15 — già in sviluppo |

---

## Analisi Gap FLUXION vs Gold Standard

### Stato attuale

| Feature | Gold Standard | FLUXION ora | Gap |
|---------|---------------|-------------|-----|
| VAD continuo | ✅ Sempre attivo | ⚠️ Per-request | **P1** |
| Barge-in | ✅ < 200ms | ⚠️ Implementato ma non connesso a sessione continua | **P1** |
| Echo suppression | ✅ Threshold adattiva | ❌ Non implementata | P2 |
| Loop speak→listen | ✅ Automatico | ❌ Richiede nuova request | **P1** |
| Silence threshold | ✅ 500-600ms | ✅ 700ms (leggermente alto) | P3 |
| Semantic endpointing | ✅ Retell/Vapi | ❌ Solo silenzio | P3 |
| Max turn protection | ✅ 30s | ✅ 30s | ✅ |
| Min speech filter | ✅ 300-400ms | ✅ 300ms | ✅ |
| Prefix padding | ✅ 200ms | ✅ 300ms | ✅ |

### Root cause del bug VAD Open-Mic

Il "microfono che si chiude dopo la risposta di Sara" ha come root cause:

1. **Architettura request/response**: il server non ha una sessione persistente con loop audio continuo
2. **Nessun loop di riascolto post-TTS**: dopo che `process_handler` ritorna una risposta, il client (Tauri/frontend) deve fare una nuova request per iniziare ad ascoltare di nuovo
3. **Barge-in non collegato**: `VADPipelineManager` esiste ma non è integrato nel flusso principale `VoiceAgentHTTPServer`

---

## Recommendation per FLUXION

### Fix P1 — Open-Mic Session State

**Soluzione minima invasiva (raccomandato per S70)**:

Aggiungere uno stato di sessione nel server che traccia se Sara ha finito di parlare e il sistema è in attesa del prossimo turno. Quando il TTS è completato, il server deve segnalare al client che è in attesa di audio — il client non deve aspettare un segnale esterno.

**Implementazione**:

1. Aggiungere campo `session_state` alla risposta del `/api/voice/process`:
   ```json
   {
     "response": "...",
     "audio_base64": "...",
     "session_state": "listening"  // NEW: "listening" | "processing" | "completed"
   }
   ```

2. Il frontend (Tauri), quando riceve `session_state: "listening"`, riattiva immediatamente la registrazione microfonico.

3. Nel server, tracciare lo stato della sessione (già parzialmente implementato con `_current_session_id`).

**Alternativa con WebSocket** (per architettura futura):
- Un endpoint `/api/voice/ws/{session_id}` gestisce l'intera sessione telefonica con loop continuo
- Il VAD gira sempre lato server
- Il client manda audio chunks via WebSocket
- Il server risponde con audio TTS + segnali barge-in via WebSocket

### Fix P2 — Echo Suppression durante TTS

Aggiungere threshold adattiva in `VADHTTPHandler`:
```python
# Durante TTS playback: threshold più alta
effective_threshold = 0.75 if sara_speaking else 0.5
```

### Fix P3 — Silence threshold ottimale

Ridurre `silence_duration_ms` da 700ms a **600ms** per italiano. L'italiano ha pause naturali frequenti ma brevi; 700ms può causare fine-turno prematuro su frasi lunghe o inizio-turno tardivo per input brevi.

### Architettura target (F15 VoIP + Open-Mic)

Con F15 (SIP/RTP), il loop continuo sarà naturale:
```
RTP stream in → VAD → buffer → STT → FSM → LLM → TTS → RTP stream out
                 ↑                                          ↓
                 └──────────── barge-in loop ───────────────┘
```

Il `SaraPhoneSession` pattern descritto sopra è l'architettura target per F15.

---

## Riferimenti Tecnici

- **Silero VAD v5**: https://github.com/snakers4/silero-vad — chunk 512 samples @ 16kHz, hidden state [2,1,128]
- **WebRTC AEC**: standard W3C per echo cancellation lato client
- **Vapi turn detection**: `transcriber.smartEndpointingEnabled` — dual-mode VAD + semantic
- **Retell interrupt signal**: `{"type": "interrupt"}` su WebSocket durante TTS
- **Google CCAI**: usa VAD server-side con CCAI Streaming API, threshold 500ms
- **Nuance Mix**: barge-in configurabile in GRXML grammar, threshold 150-300ms

---

_Research completato: 2026-03-14 | Agente A | Stack: Silero ONNX + aiohttp + Python 3.9_
