# VAD Open-Mic — Gap Analysis Codebase Attuale (CoVe 2026)

> Agente B — Analisi codebase FLUXION
> Data: 2026-03-14
> Scope: voice-agent/ + src/hooks/use-voice-pipeline.ts

---

## Architettura Attuale (con riferimenti file:linea)

### Stack VAD

| Layer | File | Ruolo |
|-------|------|-------|
| VAD Engine | `voice-agent/src/vad/ten_vad_integration.py` | Silero ONNX (512-sample chunk @16kHz) + webrtcvad fallback |
| VAD State Machine | `ten_vad_integration.py:60` | 2 stati: `IDLE` / `SPEAKING` |
| VAD Pipeline Manager | `voice-agent/src/vad/vad_pipeline_integration.py:56` | Turn manager: buffering + barge-in |
| VAD HTTP Handler | `voice-agent/src/vad_http_handler.py:78` | Endpoints HTTP: `/vad/start`, `/vad/chunk`, `/vad/stop`, `/vad/status` |
| VAD Frontend Hook | `src/hooks/use-voice-pipeline.ts:641` | `useVADRecorder` — ScriptProcessorNode → chunk ogni 100ms → `/vad/chunk` |
| Orchestrator | `voice-agent/src/orchestrator.py:555` | `process()` — 5-layer RAG pipeline |
| Main Server | `voice-agent/main.py:220` | `VoiceAgentHTTPServer` — HTTP server aiohttp |

### Modello ONNX
- **File**: `voice-agent/models/silero_vad.onnx` (cercato via `_find_model()` a `ten_vad_integration.py:155`)
- **Chunk size**: 512 samples = 32ms @16kHz (`SILERO_CHUNK_SAMPLES = 512`)
- **Threshold default**: 0.5 (configurable via `VADConfig.vad_threshold`)
- **Silence window**: 700ms default (`silence_duration_ms`), 500ms nel HTTP handler
- **Prefix padding**: 300ms default (200ms nel HTTP handler)

---

## Flusso Corrente VAD → TTS

### Flusso attuale (STOP-AND-WAIT):

```
[Frontend React]
  useVADRecorder.startListening()              ← avvia ScriptProcessorNode + VAD session
    → GET stream dal microfono
    → ogni 100ms: processAudioBuffer()
      → POST /api/voice/vad/chunk {audio_hex}
        → VADHTTPHandler.vad_chunk_handler()   ← vad_http_handler.py:168
          → session.vad.process_audio(chunk)
          → se result.event == "end_of_speech":
              return {turn_ready: true, turn_audio_hex: ...}

  [Frontend riceve turn_ready=true]
    → resolveStopRef.current(turn_audio_hex)   ← use-voice-pipeline.ts:760
    → stopListening() — FERMA il microfono     ← use-voice-pipeline.ts:869

  [Chiamante del hook (UI component)]
    → POST /api/voice/process {audio_hex}      ← main.py:333 process_handler
      → groq.transcribe_audio(wav_data)        ← STT
      → orchestrator.process(user_input)       ← 5-layer pipeline
        → ... FSM → TTS synthesize(response)   ← orchestrator.py:1816
        → return OrchestratorResult{audio_bytes=...}
    → playAudioFromHex(audio_base64)           ← TTS riprodotto dal frontend

  [Dopo playAudioFromHex().then()]
    → ??? — NESSUN startListening() automatico
    → ??? — Il microfono RIMANE CHIUSO
```

### Punto critico identificato:
`use-voice-pipeline.ts:755-763`: Quando `turn_ready=true`, il hook risolve la promise di stop
con l'audio del turno, poi `stopListening()` ferma stream, AudioContext, VAD session.
**Il ciclo si chiude.** Non c'è riattivazione automatica dopo TTS.

### Dove avviene il ciclo VAD → STT → FSM → TTS:
- **Non esiste un loop continuo** lato server. Il server è stateless per ogni request HTTP.
- Il loop esiste solo **lato frontend** nel componente UI che chiama il hook,
  ma attualmente il componente **non riattiva** il VAD dopo `playAudioFromHex`.
- Riferimento: `main.py:333` — `process_handler` è fire-and-forget HTTP, non ha loop.

---

## Gap Identificati

### GAP-1: Nessun "re-listen" dopo TTS (CRITICO — P1)
**Dove**: Frontend, nel chiamante di `useVADRecorder` / `playAudioFromHex`
**Problema**: Dopo `await playAudioFromHex(response.audio_base64)`, il microfono rimane
spento. Il sistema aspetta un'azione esplicita dell'utente per riattivare l'ascolto.
**Impatto**: In una telefonata reale (VoIP), dopo che Sara risponde, il cliente non può
parlare di nuovo senza che qualcuno chiami `startListening()` manualmente.

### GAP-2: Nessun "Sara is speaking" flag sul backend (P2)
**Dove**: `vad_http_handler.py` / `orchestrator.py`
**Problema**: `VADPipelineManager` ha `set_speaking(bool)` (`vad_pipeline_integration.py:142`)
per barge-in, ma NON è collegato al TTS playback. Il server non sa quando il frontend
sta riproducendo l'audio TTS.
**Impatto**: VAD potrebbe rilevare il suono TTS stesso come speech dell'utente (echo).

### GAP-3: Silero hidden state non resettato tra turni (P2)
**Dove**: `ten_vad_integration.py:228` — `reset()` azzera `_h_state`
**Problema**: `vad_chunk_handler` (`vad_http_handler.py:168`) non chiama `vad.reset()`
tra turni. La sessione VAD è stateful per tutta la durata (`VADSession` in `_sessions`).
Dopo un `end_of_speech`, il buffer viene svuotato (`speech_buffer = bytearray()`) ma
il Silero hidden state RNN porta memoria del turno precedente.
**Impatto**: Probabile degradazione della detection accuracy sul turno successivo.

### GAP-4: `should_exit` non gestisce riavvio VAD
**Dove**: `main.py:383-397` — risposta di `process_handler`
**Problema**: `should_exit=True` (booking completato, saluto finale) viene restituito al
frontend, ma non c'è logica per distinguere "chiudi la chiamata" da "fine turno, riascolta".
**Impatto**: Dopo "Arrivederci!", il sistema dovrebbe terminare la sessione, non riavviare
il VAD. Il frontend deve differenziare i due casi.

### GAP-5: `VADPipelineManager` non usato nella pipeline principale
**Dove**: `voice-agent/src/vad/vad_pipeline_integration.py:56`
**Problema**: `VADPipelineManager` — con barge-in, turn limits, callbacks — esiste ma
non è wired a `VoiceAgentHTTPServer`. Il `VADHTTPHandler` usa direttamente
`FluxionVAD` (livello basso), bypassando il manager di alto livello.
**Impatto**: Barge-in (`is_speaking`, `set_speaking`) non funziona nel flusso HTTP reale.

### GAP-6: Audio TTS riprodotto dal frontend, non dal server
**Dove**: `use-voice-pipeline.ts:1077` — `playAudioFromHex()`
**Problema**: Il TTS audio viene restituito come hex nella risposta HTTP e riprodotto
nel browser/WebView. Il server non controlla la durata di playback, non sa quando
finisce. Non esiste un callback "TTS playback ended" verso il backend.
**Impatto**: Il backend non può orchestrare autonomamente "aspetta fine TTS → riattiva VAD".
Nel contesto VoIP (voip.py), il TTS è gestito diversamente — ma per il flusso WebView
il controllo è interamente nel frontend.

---

## Punti di Inserimento nel Codice

### Punto A — Frontend (principale, per flusso WebView/Tauri):
**File**: Da trovare/creare — il componente React che usa `useVADRecorder`
**Dove globbare**: `src/**/*voice*` o `src/**/*Sara*` o `src/pages/VoiceAgent*`
**Logica da aggiungere**:
```typescript
// Dopo playAudioFromHex(response.audio_base64):
if (!response.should_exit && !response.should_escalate) {
  // Re-arm VAD: riavvia ascolto per il prossimo turno
  await startListening();
}
```
**Note**: Bisogna passare un flag `isSaraPlaying=true` al VADHTTPHandler per sopprimere
falsi positivi VAD durante playback (GAP-2).

### Punto B — `use-voice-pipeline.ts` — Aggiungere `setTTSSpeaking()` al VAD session:
**File**: `/Volumes/MontereyT7/FLUXION/src/hooks/use-voice-pipeline.ts`
**Dove**: Dentro `playAudioFromHex` o nel caller del hook
**Logica**: Prima di `audio.play()` → POST `/api/voice/vad/speaking {speaking: true}`;
all'evento `audio.onended` → POST `/api/voice/vad/speaking {speaking: false}` → `startListening()`
**Endpoint da creare**: `POST /api/voice/vad/speaking` in `vad_http_handler.py`

### Punto C — `vad_http_handler.py` — Aggiungere endpoint `speaking`:
**File**: `/Volumes/MontereyT7/FLUXION/voice-agent/src/vad_http_handler.py`
**Dove**: In `setup_routes()` (riga 115) e nuovo handler
**Logica**: Setta `session.is_tts_playing = True/False`; durante chunk processing,
se `is_tts_playing=True`, sopprime eventi VAD (no forward al frontend).

### Punto D — `vad_chunk_handler` — Reset hidden state tra turni:
**File**: `/Volumes/MontereyT7/FLUXION/voice-agent/src/vad_http_handler.py:243`
**Dove**: Dopo `session.speech_buffer = bytearray()` (riga 243)
**Logica**: `session.vad.reset()` — già implementato in `FluxionVAD.reset()` (`ten_vad_integration.py:228`)

### Punto E — `use-voice-pipeline.ts` — Loop automatico in `useVADRecorder`:
**File**: `/Volumes/MontereyT7/FLUXION/src/hooks/use-voice-pipeline.ts`
**Alternativa**: Aggiungere opzione `autoRestart: boolean` al hook, che dentro
`processAudioBuffer` (riga 728), dopo `resolveStopRef.current(result.turn_audio_hex)`,
non chiude il microfono ma lo mantiene aperto resettando il VAD session buffer.
**Vantaggio**: Non serve fermare/riavviare MediaStream (latenza -300ms).

---

## Rischi di Regression

### RISCHIO-1: Echo VAD (ALTO)
**Scenario**: Microfono aperto durante playback TTS → Silero sente la voce di Sara
e rileva `start_of_speech` → frontend pensa che l'utente stia parlando → invia silenzio
come input al FSM.
**Mitigazione**: GAP-2 fix — `is_tts_playing` flag nel VAD session + echo suppression.
Sara usa `macOS say` o Piper, non cuffie → rischio reale su altoparlante.

### RISCHIO-2: FSM state corruption su riavvio VAD troppo veloce (MEDIO)
**Scenario**: `startListening()` chiama `POST /vad/start` che crea nuova VAD session.
Se viene chiamato prima che `process_handler` abbia terminato, si possono avere
2 sessioni sovrapposte (VAD session ID != orchestrator session ID).
**Impatto**: booking context perso o duplicato.
**Mitigazione**: Aspettare `await playAudioFromHex()` (già una promise) prima di
`startListening()`. Aggiungere lock `isProcessing` nel frontend.

### RISCHIO-3: Stale VAD sessions in `_sessions` dict (BASSO)
**Dove**: `vad_http_handler.py:109` — `self._sessions: Dict[str, VADSession]`
**Scenario**: Con open-mic continuo, sessioni VAD si moltiplicano se il frontend
ricrea sessioni invece di riusarle. `cleanup_stale_sessions()` (riga 419) esiste
ma non viene chiamato automaticamente (manca uno scheduler).
**Mitigazione**: Riusare la stessa VAD session per tutta la durata della chiamata.

### RISCHIO-4: 1477+ test FSM — nessun test per VAD re-activation (BASSO)
**Dove**: `voice-agent/tests/` — test FSM in `tests/test_*.py`
**Scenario**: I test FSM (`booking_state_machine.py`, `orchestrator.py`) non testano
il ciclo VAD → TTS → VAD. Un regression test per open-mic non esiste.
**Mitigazione**: Aggiungere `tests/test_vad_openmicloop.py` con mock del ciclo.

### RISCHIO-5: `should_exit` / `ASKING_CLOSE_CONFIRMATION` con open-mic (MEDIO)
**Scenario**: Open-mic attivo durante stato `ASKING_CLOSE_CONFIRMATION` (FSM state).
L'utente dice "Sì, arrivederci" → Sara risponde → `should_exit=True` → frontend
deve terminare il loop VAD, non riavviarlo.
**Impatto**: Se frontend ignora `should_exit`, VAD rimane aperto a sessione conclusa.
**Mitigazione**: Controllare `should_exit` PRIMA di `startListening()` nel loop.

### RISCHIO-6: Double-trigger su turn_ready (BASSO)
**Dove**: `use-voice-pipeline.ts:754-763`
**Scenario**: Multipli `end_of_speech` events arrivano in rapida successione (edge case
su rumore burst) → `resolveStopRef.current` già null → chunk successivi ignorati.
Con open-mic continuo e auto-restart, si potrebbe fare dispatch di audio vuoto.
**Mitigazione**: Guard `if (resolveStopRef.current)` già presente (riga 760). Sufficiente.

---

## Test Esistenti Rilevanti

### Test VAD attuali:
| File | Classe | Copertura |
|------|--------|-----------|
| `tests/test_vad_file.py` | `TestSileroVADBasic` | start/stop lifecycle, silence, reset, callbacks — NO re-activation |
| `tests/test_vad_file.py` | `TestSileroVADSegments` | speech detection con audio sintetico — NO TTS echo |
| `tests/skills/test_vad_skill.py` | `TestVADSkill` | MOCK-only — non usa FluxionVAD reale |

### Test MANCANTI per Open-Mic:
1. `test_vad_reactivation_after_tts`: VAD reset corretto post-turno
2. `test_vad_tts_suppression`: no `start_of_speech` durante `is_tts_playing=True`
3. `test_vad_openmicloop`: ciclo completo N turni consecutivi senza reset microfono
4. `test_openmicloop_should_exit`: loop si ferma su `should_exit=True`
5. `test_vad_hidden_state_reset`: Silero accuracy turno 2 dopo reset vs no-reset

### Test FSM esistenti (1160 PASS su iMac, non testano VAD):
- 23-stati FSM: tutti coperti da `tests/test_booking_state_machine.py`
- Orchestrator 5-layer: `tests/test_orchestrator.py`
- Nessuno testa il ciclo "VAD end_of_speech → process → TTS → VAD restart"

---

## Stima Effort

| Task | File da modificare | Effort | Rischio |
|------|--------------------|--------|---------|
| T1: Auto-restart VAD nel frontend caller | Componente UI + `use-voice-pipeline.ts` | 2h | BASSO |
| T2: Endpoint `POST /vad/speaking` + `is_tts_playing` flag | `vad_http_handler.py` | 1h | BASSO |
| T3: Reset Silero hidden state tra turni | `vad_http_handler.py:243` (1 riga) | 15min | BASSO |
| T4: `playAudioFromHex` → segnala TTS start/end al backend | `use-voice-pipeline.ts:1077` | 1h | BASSO |
| T5: Wire `VADPipelineManager.set_speaking()` per barge-in reale | `vad_http_handler.py` | 2h | MEDIO |
| T6: 5 nuovi test per open-mic loop | `tests/test_vad_openmicloop.py` | 2h | BASSO |
| **TOTALE** | | **~8h** | |

### Priorità raccomandata:
1. **P0** (blocca flusso telefonata): T1 — auto-restart VAD nel frontend
2. **P1** (previene echo): T2 + T4 — TTS playing flag
3. **P2** (qualità): T3 — Silero hidden state reset
4. **P3** (completezza): T5 + T6 — barge-in reale + test suite

---

## Note Architetturali

### Flusso VoIP (voip.py) vs WebView
Il file `voice-agent/src/voip.py` (1227 righe, non analizzato in questo task) gestisce
il ciclo VAD in modo diverso quando la chiamata arriva via SIP/RTP. Il "Open-Mic" per
VoIP è probabilmente già implementato nel loop RTP nativo. Il gap analizzato qui riguarda
principalmente il flusso **WebView/Tauri** (microfono browser → HTTP chunks → VAD backend).

### `VADPipelineManager` vs `VADHTTPHandler`
`VADPipelineManager` (`vad_pipeline_integration.py`) ha un'API ad alto livello pensata per
streaming continuo. Il `VADHTTPHandler` (`vad_http_handler.py`) usa `FluxionVAD` direttamente.
Per open-mic, è più corretto aggiornare il `VADHTTPHandler` per mantenere la sessione aperta
tra turni, piuttosto che rewire tutto su `VADPipelineManager`.

### Il frontend è il loop orchestrator
Con architettura HTTP (no WebSocket), **il frontend React è necessariamente il loop controller**.
Il server risponde a richieste; non può "pushare" una riattivazione VAD al client.
L'open-mic loop DEVE essere implementato lato frontend (React) con la sequenza:
```
startListening() → [turn_ready] → process() → playAudio() → startListening() → ...
```
La logica di terminazione (`should_exit`) è l'unico modo per uscire dal loop.

---

_Analisi completata: 2026-03-14 — Agente B CoVe 2026_
_File analizzati: 8 (vad/ten_vad_integration.py, vad/vad_pipeline_integration.py, vad/__init__.py, vad_http_handler.py, main.py, orchestrator.py (excerpt), src/hooks/use-voice-pipeline.ts, tests/test_vad_file.py, tests/skills/test_vad_skill.py, src/vad/_INDEX.md)_
