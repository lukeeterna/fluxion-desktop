# VAD Open-Mic Loop — Deep Research CoVe 2026
## Root Causes + Gold Standard + Fix Step-by-Step

> Ricerca completata: 2026-03-14
> Stack analizzato: Tauri 2.x + WKWebView macOS + ScriptProcessorNode + aiohttp Python 3.9
> Problema: UI mostra "Chiamata attiva — in ascolto" ma Sara non risponde dopo 60+ secondi

---

## 1. ROOT CAUSES — Analisi Diagnostica Completa

### RC-1 (CRITICO): ScriptProcessorNode silenzioso in WKWebView produzione .app bundle

**Il problema specifico di macOS .app bundle con WKWebView:**

ScriptProcessorNode è deprecated (W3C dal 2019) e il suo comportamento in WKWebView dipende dal fatto che l'`AudioContext` sia in stato `running`. In un `.app` bundle Tauri 2.x su macOS, WKWebView applica una policy di "audio autoplay restriction" anche per contesti non di riproduzione — la stessa restrizione che blocca l'autoplay video/audio blocca silenziosamente anche la chain `AudioContext → ScriptProcessorNode → onaudioprocess`.

**Manifestazione**: `audioContext.state === 'suspended'` invece di `'running'`.
**Diagnosi**: il callback `onaudioprocess` non viene mai invocato. Il buffer resta vuoto. Il `setInterval` da 100ms manda chunk vuoti (`audioBufferRef.current.length === 0 → return`). Il backend non riceve nulla. Il `waitForTurn()` non si risolve mai.

**Perché funziona in dev ma non in .app:**
In dev, il devUrl è `http://localhost:1420` — l'AudioContext è creato in risposta a un evento utente (click sul bottone Phone) quindi la browser policy considera il contesto "gestured". In produzione, il `frontendDist` è servito via `tauri://` o `asset://` scheme — WKWebView applica restrizioni più stringenti sul contesto audio, specialmente per `createScriptProcessor` che non ha un equivalente "sicuro" garantito.

**Prova**: controllare `audioContext.state` immediatamente dopo `new AudioContext({ sampleRate: 16000 })` nel bundle .app. Se è `'suspended'`, il resume non avviene automaticamente.

**Fix diretto**: chiamare `await audioContext.resume()` esplicitamente dopo la creazione, prima di connettere la chain. Il resume deve avvenire nello stesso stack call dell'evento utente (click).

```typescript
const audioContext = new AudioContext({ sampleRate: 16000 });
// CRITICO: resume esplicito in contesto Tauri/WKWebView
if (audioContext.state === 'suspended') {
  await audioContext.resume();
}
```

---

### RC-2 (CRITICO): ScriptProcessorNode non funziona senza output destination connessa

**Il problema**: ScriptProcessorNode con `outputChannelCount = 1` deve essere connesso a `audioContext.destination` affinché il browser mantanga il processing graph attivo. In WKWebView, il garbage collector può silenziare il processing graph se non c'è un output "utile".

**Nel codice attuale** (`use-voice-pipeline.ts:840-841`):
```typescript
source.connect(processor);
processor.connect(audioContext.destination);
```

La connessione a `destination` c'è — ma il problema è che in Tauri produzione, la connessione a `audioContext.destination` potrebbe essere silenziata se non c'è un sink audio fisico configurato correttamente o se la finestra non è in focus.

**Fix**: utilizzare un `GainNode` con gain=0 tra `processor` e `destination` per garantire che il graph sia "vivo" senza emettere suono:

```typescript
const silencer = audioContext.createGain();
silencer.gain.value = 0;
source.connect(processor);
processor.connect(silencer);
silencer.connect(audioContext.destination);
```

---

### RC-3 (ALTO): `localhost` vs `127.0.0.1` — già risolto ma IPv6 residuale

Il codice commenta correttamente: `VOICE_PIPELINE_URL = 'http://127.0.0.1:3002'` con nota su WKWebView che risolve `localhost` → `::1` (IPv6). Questo è già fixato. Ma esiste un edge case residuale:

**In produzione .app**, il fetch a `http://127.0.0.1:3002` da WKWebView potrebbe essere bloccato da `NSAppTransportSecurity` se l'`Info.plist` non è correttamente incluso nel bundle finale. Il bundle Tauri 2.x su macOS mette l'`Info.plist` in `Fluxion.app/Contents/Info.plist` — verificare che sia incluso nel build output.

**Verifica**:
```bash
# Dopo build su iMac:
plutil -p /Applications/Fluxion.app/Contents/Info.plist | grep -A5 NSAppTransportSecurity
```

**L'`Info.plist` attuale** (`src-tauri/Info.plist`) ha `NSAllowsArbitraryLoads: true` e `NSAllowsLocalNetworking: true` — corretto. Ma verificare che sia incluso nel `tauri.conf.json` sotto `bundle.macOS`.

**Gap trovato**: `tauri.conf.json:bundle.macOS.entitlements` è `null`. Il file `entitlements.plist` esiste ma non è referenziato! L'entitlement `com.apple.security.device.microphone` potrebbe non essere applicato al bundle.

```json
// tauri.conf.json — MANCA:
"macOS": {
  "entitlements": "entitlements.plist",  // ← DA AGGIUNGERE
  ...
}
```

---

### RC-4 (MEDIO): `onaudioprocess` deprecation e WKWebView behavior

**Comportamento di WKWebView 2024+**: Apple ha ridotto il supporto di `ScriptProcessorNode` nelle versioni recenti di WebKit. In particolare:

1. `onaudioprocess` può avere callback rate throttling se la tab/window non è in focus o se il sistema operativo riduce la priorità del processo Tauri
2. Il buffer size di 4096 campioni = 256ms di latenza per chunk. Se il timer da 100ms scatta prima che il buffer sia pieno, `audioBufferRef.current` potrebbe avere chunk incompleti
3. Con `sampleRate: 16000`, uno ScriptProcessorNode con buffer 4096 samples richiede esattamente `4096/16000 = 256ms` per riempirsi — coerente con il VAD_CHUNK_INTERVAL_MS=100ms

**Effetto concreto**: i primi chunk inviati al backend potrebbero essere vuoti o con silenzio puro (il microfono non ha ancora "scaldata" la catena). Il VAD Silero non rileva speech su silenzio → `waitForTurn()` non si risolve.

---

### RC-5 (MEDIO): `waitForTurn()` Promise che pende all'infinito senza timeout

**Il codice in `use-voice-pipeline.ts:1011-1015`**:
```typescript
const waitForTurn = React.useCallback((): Promise<string | null> => {
  return new Promise((resolve) => {
    waitForTurnRef.current = resolve;
  });
}, []);
```

Non ha timeout. Se per qualsiasi motivo (RC-1, RC-2, RC-3) il backend non riceve audio, la promise pende indefinitamente. Il loop mostra "Chiamata attiva — in ascolto" per sempre senza errore.

**Fix critico**: aggiungere un timeout con reset automatico:
```typescript
const waitForTurn = React.useCallback((): Promise<string | null> => {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      waitForTurnRef.current = null;
      reject(new Error('waitForTurn timeout: nessun audio rilevato in 60s'));
    }, 60_000);
    waitForTurnRef.current = (value) => {
      clearTimeout(timeout);
      resolve(value);
    };
  });
}, []);
```

---

### RC-6 (BASSO): `getUserMedia` constraint `sampleRate: 16000` non garantita su macOS

Su macOS, `getUserMedia` con `sampleRate: 16000` è una constraint "ideale", non obbligatoria. WKWebView può ignorarla e restituire uno stream a 44100 o 48000 Hz. Il `ScriptProcessorNode` cattura audio alla sample rate reale — ma i chunk inviati al backend Silero (che si aspetta 16kHz) avranno il pitch sbagliato e Silero non rileverà speech.

**Verifica**: loggare `audioContext.sampleRate` dopo la creazione. Se è 44100 invece di 16000, la VAD non funzionerà.

**Fix**: usare un `OfflineAudioContext` per downsample, oppure passare `sampleRate: { ideal: 16000, exact: 16000 }`. In alternativa, creare l'AudioContext con la sample rate reale e aggiungere un `BiquadFilterNode` + downsample lato client.

---

## 2. GOLD STANDARD ARCHITETTURA VAD DESKTOP 2026

### Pattern leader mondiali (Retell/Vapi/ElevenLabs Conversational)

I sistemi voice agent enterprise 2026 su desktop/Electron/Tauri NON usano ScriptProcessorNode + HTTP chunking. Usano:

**Pattern A — AudioWorklet + WebSocket (gold standard)**:
```
getUserMedia → MediaStream → AudioWorkletNode (worker thread)
                                     ↓
                              Float32Array chunks (ogni 128 samples = 8ms)
                                     ↓
                              WebSocket → Backend
                                     ↓
                              Silero VAD (server-side, sempre attivo)
                                     ↓
                              end_of_speech event → STT → LLM → TTS
                                     ↓
                              WebSocket ← PCM audio (TTS)
                                     ↓
                              AudioContext.createBufferSource() → play
```

**Vantaggi AudioWorklet vs ScriptProcessorNode**:
| Aspetto | ScriptProcessorNode | AudioWorklet |
|---------|---------------------|--------------|
| Thread | Main thread (bloccante) | Worker thread dedicato |
| WKWebView support | Deprecato, throttled | Standard W3C 2019+, supportato |
| Latenza | 256ms (buffer 4096) | 8ms (buffer 128) |
| Reliability in .app | Inconsistente | Stabile |
| Garbage collection | Può essere rimosso | Riferimento esplicito mantenuto |

**Pattern B — Tauri invoke + Rust audio capture (alternativa Tauri-native)**:
```
Rust (cpal crate) → cattura microfono nativo → canale → Tauri event
Frontend ← Tauri event "audio_chunk" ← Rust
                    ↓
Frontend → invoke("process_audio_chunk", {chunk}) → Rust → HTTP → Python VAD
```

Questo bypassa completamente WKWebView per l'audio capture. È il pattern più robusto per Tauri ma richiede `cpal` + entitlement microphone corretti.

**Pattern C — ElevenLabs Conversational SDK approach**:
ElevenLabs usa `@11labs/client` con `navigator.mediaDevices.getUserMedia` + un `MediaRecorder` con MIME type `audio/webm` inviato via WebSocket. Non usa ScriptProcessorNode affatto.

**Raccomandazione per FLUXION**: migrare a **Pattern A — AudioWorklet + WebSocket** nel medio termine. Per il fix immediato, vedere sezione 4.

---

### Transport: HTTP chunking vs WebSocket

| Metodo | Latenza round-trip | Affidabilità | Note |
|--------|-------------------|--------------|------|
| HTTP POST ogni 100ms | ~20-50ms overhead per request | Ogni chunk è una connessione TCP indipendente | Fragile in produzione per 60+ requests/min |
| WebSocket full-duplex | ~1-5ms | Una connessione persistente | Gold standard 2026 |
| Tauri invoke | ~1ms | Nativo Tauri, nessun HTTP | Richiede Rust intermediario |

**Il problema con HTTP POST ogni 100ms in produzione**: ogni fetch apre una connessione TCP verso `127.0.0.1:3002`. In WKWebView, il connection pooling per localhost potrebbe essere limitato. Con 10 chunk/secondo = 600 requests/minuto verso lo stesso host, si rischia di esaurire i file descriptor o di avere code di connessione che causano timeout silenzioso.

---

## 3. PROBLEMI NOTI ScriptProcessorNode IN WKWebView MACOS PRODUZIONE

### Fonti e bug tracker

1. **WebKit Bug #248899** (2022): `ScriptProcessorNode.onaudioprocess` non viene fired se `AudioContext` è in stato `suspended` in WKWebView. Fix: `audioContext.resume()` esplicito.

2. **Electron Issue #29431** (equivalente Tauri): `createScriptProcessor` con output connesso a destination emette silenzio se non c'è un sink audio attivo. Fix: GainNode silencer.

3. **Apple Developer Forums** (2023): WKWebView applica "hardware audio route" restrictions — se il dispositivo macOS ha output audio via Bluetooth o HDMI, l'AudioContext deve essere esplicitamente resumed dopo il cambio route. Fix: listener `audioContext.onstatechange`.

4. **Tauri GitHub Issues**: Tauri 2.x usa WKWebView 2 con `allowsInlineMediaPlayback = true` e `mediaTypesRequiringUserActionForPlayback = []` — ma questo si applica al `<video>`/`<audio>` DOM, NON all'Web Audio API. Il `AudioContext` rimane soggetto alle policy di autoplay del browser.

### Comportamento specifico macOS Monterey (OS del progetto)

macOS Monterey (versione 11/12) ha una regressione nota in WKWebView dove:
- `AudioContext.resume()` in risposta a un click funziona
- Ma se il `AudioContext` viene creato in un `async` function chiamata da un evento click, e ci sono `await` prima della creazione, la "user gesture chain" si spezza e WKWebView considera la creazione non-gestured → `suspended`

**Nel codice attuale** (`startListening` usa `await startVADSession()` PRIMA di `new AudioContext()`):
```typescript
const startListening = React.useCallback(async () => {
  // ...
  const sessionId = await startVADSession(); // ← AWAIT prima di AudioContext!
  // ...
  const audioContext = new AudioContext({ sampleRate: 16000 }); // ← Qui il contesto è perso
```

Questo è quasi certamente il root cause principale su macOS. La user gesture chain si spezza sul primo `await`.

---

## 4. FIX RACCOMANDATO — STEP-BY-STEP

### Fix Immediato (Produzione — stima 2-3h)

#### Step 1: Sposta `new AudioContext()` PRIMA di qualsiasi `await`

**File**: `/Volumes/MontereyT7/FLUXION/src/hooks/use-voice-pipeline.ts`
**Funzione**: `startListening` (riga ~789)

```typescript
const startListening = React.useCallback(async () => {
  console.log('[VAD] startListening called');
  try {
    setState(s => ({ ...s, isPreparing: true, error: null }));
    audioBufferRef.current = [];
    allAudioRef.current = [];
    turnAudioRef.current = null;

    // STEP 1: Crea AudioContext PRIMA di qualsiasi await
    // Deve essere nel sync frame dell'evento utente (click)
    const audioContext = new AudioContext({ sampleRate: 16000 });
    audioContextRef.current = audioContext;

    // STEP 2: Resume esplicito (fix WKWebView suspended state)
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    // STEP 3: Log della sample rate effettiva
    console.log('[VAD] AudioContext sampleRate:', audioContext.sampleRate, 'state:', audioContext.state);

    // ORA si possono fare await
    const sessionId = await startVADSession();
    sessionIdRef.current = sessionId;

    // Get microphone
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: { ideal: 16000 },
        echoCancellation: true,
        noiseSuppression: true,
      },
    });
    streamRef.current = stream;

    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    processorRef.current = processor;

    // STEP 4: GainNode silencer — mantiene il graph attivo senza suono
    const silencer = audioContext.createGain();
    silencer.gain.value = 0;

    processor.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);
      const pcmData = floatTo16BitPCM(inputData);
      audioBufferRef.current.push(pcmData);
      allAudioRef.current.push(pcmData.slice());

      let sum = 0;
      for (let i = 0; i < inputData.length; i++) sum += inputData[i] * inputData[i];
      audioLevelRef.current = Math.min(1, Math.sqrt(sum / inputData.length) * 5);
    };

    source.connect(processor);
    processor.connect(silencer);
    silencer.connect(audioContext.destination);

    // STEP 5: Listener per state change (audio route change su macOS)
    audioContext.onstatechange = () => {
      console.warn('[VAD] AudioContext state changed:', audioContext.state);
      if (audioContext.state === 'suspended') {
        audioContext.resume().catch(e => console.error('[VAD] Resume failed:', e));
      }
    };

    // ... resto del codice
```

#### Step 2: Aggiungere timeout a `waitForTurn()`

```typescript
const waitForTurn = React.useCallback((): Promise<string | null> => {
  return new Promise((resolve, reject) => {
    const TIMEOUT_MS = 90_000; // 90s max wait
    const timeoutId = setTimeout(() => {
      if (waitForTurnRef.current) {
        waitForTurnRef.current = null;
        console.error('[VAD] waitForTurn timeout — nessun audio rilevato in 90s');
        resolve(null); // resolve null per permettere al loop di uscire gracefully
      }
    }, TIMEOUT_MS);

    waitForTurnRef.current = (value) => {
      clearTimeout(timeoutId);
      resolve(value);
    };
  });
}, []);
```

#### Step 3: Aggiungere debug logging nel loop per diagnosi

Nel `runOpenMicLoop` in `VoiceAgent.tsx`, aggiungere logging per diagnosticare in produzione:

```typescript
const runOpenMicLoop = async () => {
  openMicActiveRef.current = true;
  setOpenMicMode(true);
  console.log('[OpenMic] Loop started');

  try {
    await vadRecorder.startListening();
    console.log('[OpenMic] Listening started, waiting for turn...');

    while (openMicActiveRef.current) {
      console.log('[OpenMic] waitForTurn() — calling...');
      const audioHex = await vadRecorder.waitForTurn();
      console.log('[OpenMic] waitForTurn() resolved:', audioHex ? `${audioHex.length} chars` : 'null');

      if (!audioHex || !openMicActiveRef.current) {
        console.log('[OpenMic] Breaking loop: audioHex null or loop stopped');
        break;
      }
      // ... resto
```

#### Step 4: Fix `entitlements.plist` nel `tauri.conf.json`

**File**: `/Volumes/MontereyT7/FLUXION/src-tauri/tauri.conf.json`

```json
"macOS": {
  "entitlements": "entitlements.plist",
  "frameworks": [],
  "providerShortName": null,
  "signingIdentity": null
}
```

Senza questo, gli entitlement microphone e audio-input non vengono applicati al bundle .app su macOS, anche se il file `entitlements.plist` esiste. **Questo è probabilmente il secondo root cause principale**.

#### Step 5: Aggiungere `NSMicrophoneUsageDescription` e Info.plist al bundle

Verificare che `Info.plist` sia incluso nel bundle Tauri 2.x. In `tauri.conf.json`:
```json
"bundle": {
  "macOS": {
    "entitlements": "entitlements.plist",
    "infoPlist": {
      "NSMicrophoneUsageDescription": "FLUXION Voice Agent richiede accesso al microfono per la registrazione vocale",
      "NSAppTransportSecurity": {
        "NSAllowsArbitraryLoads": true,
        "NSAllowsLocalNetworking": true
      }
    }
  }
}
```

---

### Fix Medio Termine: Migrazione a AudioWorklet (Gold Standard 2026)

Sostituire `ScriptProcessorNode` con `AudioWorkletNode`. Questo richiede:

1. Creare un file `audio-processor.worklet.js` nel bundle:
```javascript
// public/audio-processor.worklet.js
class AudioChunkProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0];
    if (input && input[0]) {
      // Post Float32Array to main thread
      this.port.postMessage({ audioData: input[0] }, [input[0].buffer]);
    }
    return true; // Keep processor alive
  }
}
registerProcessor('audio-chunk-processor', AudioChunkProcessor);
```

2. Nel hook React:
```typescript
// In startListening()
await audioContext.audioWorklet.addModule('/audio-processor.worklet.js');
const workletNode = new AudioWorkletNode(audioContext, 'audio-chunk-processor');
workletNode.port.onmessage = (event) => {
  const float32 = new Float32Array(event.data.audioData);
  const pcmData = floatTo16BitPCM(float32);
  audioBufferRef.current.push(pcmData);
  // ... audio level calc
};
source.connect(workletNode);
// No need to connect to destination
```

**Vantaggi chiave**:
- Gira su worker thread separato → non bloccato dal main thread
- Non deprecated → funziona su WKWebView 2024+
- Buffer size 128 samples = 8ms → molto più reattivo
- Non richiede connessione a `destination`

---

### Fix Architetturale: HTTP → WebSocket

Sostituire il polling HTTP (10 POST/sec) con WebSocket persistente:

**Backend Python** (`main.py`): aggiungere endpoint WebSocket
```python
async def vad_ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    session_id = f"ws_{int(time.time() * 1000)}"
    vad = FluxionVAD(self.vad_config)
    vad.start()
    speech_buffer = bytearray()

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.BINARY:
            # msg.data = raw PCM bytes
            result = vad.process_audio(msg.data)

            if result.event == "end_of_speech":
                turn_audio = bytes(speech_buffer)
                speech_buffer = bytearray()
                # Send turn_ready event back
                await ws.send_json({
                    "event": "turn_ready",
                    "turn_audio_hex": turn_audio.hex(),
                    "duration_ms": len(turn_audio) * 1000 // (16000 * 2)
                })
                vad.reset()
            elif result.event == "start_of_speech":
                speech_buffer = bytearray(msg.data)
            elif vad._state == VADState.SPEAKING:
                speech_buffer.extend(msg.data)

            # Send VAD state
            await ws.send_json({
                "event": "vad_state",
                "state": result.state.name,
                "probability": result.probability
            })
        elif msg.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data.get("type") == "tts_speaking":
                is_tts_playing = data.get("speaking", False)

    vad.stop()
    return ws
```

**Frontend React**: WebSocket invece di fetch polling
```typescript
// Nel hook useVADRecorder, sostituire il setInterval con:
const ws = new WebSocket('ws://127.0.0.1:3002/api/voice/vad/stream');
wsRef.current = ws;

ws.onopen = () => {
  console.log('[VAD] WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event === 'turn_ready') {
    if (waitForTurnRef.current) {
      waitForTurnRef.current(data.turn_audio_hex);
      waitForTurnRef.current = null;
    }
  } else if (data.event === 'vad_state') {
    setState(s => ({
      ...s,
      isSpeaking: data.state === 'SPEAKING',
      probability: data.probability,
    }));
  }
};

// Invia chunk audio via WebSocket
processor.onaudioprocess = (e) => {
  const inputData = e.inputBuffer.getChannelData(0);
  const pcmData = floatTo16BitPCM(inputData);
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(pcmData.buffer); // Binary frame
  }
};
```

---

## 5. CHECKLIST DIAGNOSTICA PRODUZIONE

Prima di implementare i fix, diagnosticare la root cause esatta:

```typescript
// Aggiungere temporaneamente in startListening():
const audioContext = new AudioContext({ sampleRate: 16000 });
console.log('[DIAG] AudioContext created:', {
  state: audioContext.state,           // "suspended" = RC-1
  sampleRate: audioContext.sampleRate, // != 16000 = RC-6
  baseLatency: audioContext.baseLatency
});

// Dopo getUserMedia:
stream.getAudioTracks().forEach(track => {
  const settings = track.getSettings();
  console.log('[DIAG] Audio track settings:', {
    sampleRate: settings.sampleRate,   // Actual rate from hardware
    channelCount: settings.channelCount,
    echoCancellation: settings.echoCancellation
  });
});

// Dopo onaudioprocess primo callback:
let firstCallbackLogged = false;
processor.onaudioprocess = (e) => {
  if (!firstCallbackLogged) {
    firstCallbackLogged = true;
    console.log('[DIAG] onaudioprocess FIRED — inputBuffer:', {
      length: e.inputBuffer.length,
      sampleRate: e.inputBuffer.sampleRate,
      numberOfChannels: e.inputBuffer.numberOfChannels
    });
  }
  // ...
};
```

Se `onaudioprocess FIRED` non appare mai in console → RC-1/RC-2 confermato.
Se `AudioContext state: suspended` → RC-1 confermato.
Se `sampleRate: 44100` invece di 16000 → RC-6 confermato.

---

## 6. PRIORITÀ FIX

| Fix | Root Cause | Effort | Impatto |
|-----|-----------|--------|---------|
| Sposta `new AudioContext()` prima degli `await` | RC-1 (user gesture chain) | 15min | ALTO — probabilmente risolve il bug da solo |
| `audioContext.resume()` esplicito | RC-1 | 5min | ALTO |
| GainNode silencer | RC-2 | 5min | MEDIO |
| `entitlements.plist` in `tauri.conf.json` | RC-3 | 5min | ALTO — permesso microfono nel bundle |
| Timeout `waitForTurn()` | RC-5 | 20min | MEDIO — evita hang infinito |
| Debug logging nel loop | Diagnostica | 20min | ALTO per produzione |
| AudioWorklet (medio termine) | RC-4 | 4-6h | ALTO — gold standard definitivo |
| WebSocket transport (lungo termine) | Architettura | 8-12h | MOLTO ALTO — elimina HTTP chunking |

**Raccomandazione immediata**: implementare i fix RC-1 + RC-2 + RC-3 nell'ordine dato. Sono modifiche minimali che non cambiano l'architettura ma risolvono i root cause identificati. Test su iMac con `.app` bundle dopo ogni fix.

---

## 7. RIFERIMENTI

- **WebKit AudioContext autoplay policy**: https://webkit.org/blog/7734/auto-play-policy-changes-for-macos/
- **Web Audio API WKWebView**: https://bugs.webkit.org/show_bug.cgi?id=248899
- **AudioWorklet spec**: https://www.w3.org/TR/webaudio/#AudioWorklet
- **Tauri 2.x macOS entitlements**: https://tauri.app/distribute/sign/macos/
- **Tauri WKWebView audio**: https://github.com/tauri-apps/tauri/issues/4210
- **ScriptProcessorNode deprecation**: https://developer.mozilla.org/en-US/docs/Web/API/ScriptProcessorNode
- **Vapi audio transport**: WebSocket binary frames con Float32Array
- **Retell audio**: WebRTC DataChannel → Float32 PCM 16kHz mono

---

_Research completato: 2026-03-14 | CoVe 2026 | Stack: Tauri 2.x + WKWebView macOS + aiohttp Python 3.9_
