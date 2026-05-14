# S235 — VoIP Audio Bridge Analysis (`voip_pjsua2.py:235` startTransmit failure)

> Research only. NO code modified. Path corretto file: `/Volumes/MontereyT7/FLUXION/voice-agent/src/voip_pjsua2.py` (899 lines).
> SWIG bindings: `/Volumes/MontereyT7/FLUXION/voice-agent/lib/pjsua2/pjsua2.py`.

---

## SEZIONE 1 — Codice Attuale (snippet rilevanti)

### 1.1 `SaraAudioPort` (lines 83–193) — creazione port nel `__init__`

```python
# voip_pjsua2.py:83
class SaraAudioPort(pj.AudioMediaPort):
    """Bridges pjsua2 conference bridge with Sara voice pipeline."""

    def __init__(self):                                          # L90
        super().__init__()                                       # L91
        self.rx_queue = queue.Queue(maxsize=500)                 # L92
        self.tx_queue = queue.Queue(maxsize=3000)                # L93
        self._silence_frame = b'\x00' * 320                      # L94
        self._current_tx_rms = 0.0                               # L95
        # Create audio port: 8kHz, mono, 160 samples/frame (20ms), 16-bit
        # Format ID 0x2036314C = PJMEDIA_FORMAT_L16              # L100
        fmt = pj.MediaFormatAudio()                              # L101
        fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)              # L102
        self.createPort("sara_bridge", fmt)                      # L103  ⬅ REGISTRA AL CONFERENCE BRIDGE
```

**Punto critico**: `createPort()` (L103) chiamato dentro `__init__`. Docstring SWIG (`pjsua2.py:5723-5732`):

> "Create an audio media port and **register it to the conference bridge**."

Quindi `createPort` esegue una pjsua2 native call che tocca lo stato globale del conference bridge.

### 1.2 `SaraCall` (lines 200–238) — istanziazione port nel `__init__`

```python
# voip_pjsua2.py:200
class SaraCall(pj.Call):
    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):        # L203
        super().__init__(acc, call_id)                           # L204
        self.audio_port = SaraAudioPort()   ⬅ qui parte tutta la chain createPort!  # L205
        self.connected = False                                   # L206
        self.on_connected = None                                 # L207
        self.on_disconnected = None                              # L208

    def onCallState(self, prm):                                  # L210
        ci = self.getInfo()                                      # L211
        state = ci.state                                         # L212
        ...

    def onCallMediaState(self, prm):                             # L227
        ci = self.getInfo()                                      # L228
        for i, mi in enumerate(ci.media):                        # L229
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \            # L230
               mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:          # L231
                call_audio = self.getAudioMedia(i)               # L233
                # Bidirectional bridge: call ↔ Sara              # L234
                call_audio.startTransmit(self.audio_port)        # L235  ⬅ ERROR LINE
                self.audio_port.startTransmit(call_audio)        # L236
                logger.info("Audio bridge established: call ↔ Sara")  # L237
```

### 1.3 Chain del caller per istanziare `SaraCall`

```python
# voip_pjsua2.py:260
class SaraAccount(pj.Account):
    def onIncomingCall(self, prm):                               # L260
        call = SaraCall(self, prm.callId)   ⬅ SaraCall.__init__ FIRED HERE  # L261
        ci = call.getInfo()                                      # L262
        ...
        if self.on_incoming_call:                                # L275
            self.on_incoming_call(call)   ⬅ delegate to VoIPManager._on_incoming_call  # L276
```

**Thread context di `onIncomingCall`**: pjsua2 main thread (= `_pjsua2_thread`, perché `threadCnt=0 + mainThreadOnly=True` configurato a L436-437).

Quindi **`SaraCall.__init__` E `SaraAudioPort.createPort()` GIRANO GIÀ SUL pjsua2 MAIN THREAD**. L'ipotesi S234 "Python thread esterno" è **FALSIFICATA** dal codice.

### 1.4 Settings pjsua2 endpoint (L433-437)

```python
ep_cfg.uaConfig.threadCnt = 0           # L436 — no internal worker threads
ep_cfg.uaConfig.mainThreadOnly = True   # L437 — ALL callbacks on _pjsua2_thread
```

Conferma: tutti i callback (`onIncomingCall`, `onCallState`, `onCallMediaState`) sono serializzati sullo stesso `_pjsua2_thread`. Anche `SaraCall.__init__` (chiamato da `onIncomingCall`) gira lì.

### 1.5 Smoking gun runtime (`/tmp/sara-live-s234.log`)

```
20:47:11  Incoming call from: <sip:3281536308@79.98.45.133>     ⬅ onIncomingCall fired
20:47:11  Answering call with 200 OK                            ⬅ call.answer() OK
          Traceback: voip_pjsua2.py:235
                     call_audio.startTransmit(self.audio_port)
                     → pjsua2.Error                              ⬅ RAW SWIG ERROR (no .info())
20:47:27  Call state: CONNECTING  (gap 16s!)
20:47:27  Call state: CONFIRMED
20:47:27  Call state: DISCONNECTED  (Vodafone "telefono spento")
```

Conseguenza: il bridge non si stabilisce → no greeting RTP → Vodafone timeout 16s → caller riceve "telefono spento".

---

## SEZIONE 2 — Diagnosi Root Cause

### 2.1 Ipotesi S234 (createPort su thread Python sbagliato) → **FALSIFICATA**

L'ipotesi diceva: `createPort` chiamato in `SaraCall.__init__` Python thread, non pjsua2 main thread, → port non registrato.

**Evidenza che la falsifica**:
- `onIncomingCall` è un callback di `pj.Account`. Con `mainThreadOnly=True` (L437) tutti i callback sono dispatchati da `libHandleEvents(20)` (L413), che gira nel `_pjsua2_thread` (L405-422).
- `SaraCall(self, prm.callId)` (L261) eredita lo stesso stack → `SaraAudioPort()` (L205) → `createPort()` (L103) tutti sullo stesso thread che ha in mano il pjsua2 mutex.
- Non c'è creazione thread separato fra `onIncomingCall` e `__init__`.

Quindi il thread NON è la root cause.

### 2.2 Root cause REALE — ipotesi rank-ordered per probabilità

#### **H1 (ALTAMENTE PROBABILE) — Race timing: `startTransmit` chiamato prima che il conference bridge slot sia "stabile"**

Il problema **non è thread-safety**, è **ordering temporale di stato pjsua2**:

1. `onIncomingCall` (L260) → `SaraCall.__init__` → `createPort` registra `sara_bridge` al conference bridge → port ottiene un `conf_slot_id`. **OK**.
2. `call.answer(200)` (L585) → INVITE/200 OK dialog → SDP negotiation parte.
3. **Subito dopo** `onCallMediaState` (L227) firato **PRIMA che la SDP O/A sia completamente conclusa** → `mi.status == PJSUA_CALL_MEDIA_ACTIVE` può essere `True` per *uno* slot ma `getAudioMedia(i)` ritorna un `AudioMedia` il cui `conf_slot_id` è ancora `PJSUA_INVALID_ID` (-1) perché il transport RTP non ha ancora "armato" lo slot.
4. `startTransmit` (L235) chiama internamente `pjmedia_conf_connect_port(bridge, src_slot, sink_slot)` — se `src_slot == -1` → `PJ_EINVAL` o `PJMEDIA_ENOTFOUND` → **`pj::Error` raw** (no `.info()` perché lo stack trace SWIG strippa il messaggio quando l'eccezione viene risollevata Python-side).

Smoking gun del gap 16s fra L235 traceback e CONNECTING/CONFIRMED:
- Se il bridge fosse stato "broken from media layer", lo stato non sarebbe arrivato a CONFIRMED.
- Invece CONFIRMED arriva 16s dopo → la SDP O/A si chiude solo tardi → conferma che la chiamata di `startTransmit` è arrivata **prima** che la media sub-system fosse pronta.
- 16s = round-trip timeout di Vodafone (no early-media ACK) → carrier conclude "no media" → DISCONNECT.

#### **H2 (PROBABILE) — `getAudioMedia(i)` ritorna AudioMedia con `conf_slot_id` non ancora assegnato**

Doc `pjsua2.py:11566-11578`:
> "If the specified media index is not audio or invalid or **inactive**, exception will be thrown."

Ma l'eccezione viene tirata SOLO se `mi.status != ACTIVE`. Il check L230-231 è solo `PJMEDIA_TYPE_AUDIO + PJSUA_CALL_MEDIA_ACTIVE`. C'è un secondo stato intermedio `PJSUA_CALL_MEDIA_LOCAL_HOLD / REMOTE_HOLD / ERROR / NONE` che non viene escluso, ma più importante: anche con `ACTIVE` lo `AudioMedia` può avere un `getPortId() == PJSUA_INVALID_ID` se chiamato troppo presto in `onCallMediaState` (il callback fires con micro-jitter rispetto all'assegnazione slot interna).

#### **H3 (POSSIBILE secondario) — `SaraAudioPort.createPort` fatto in `SaraCall.__init__` ESEGUITO PRIMA dell'`onIncomingCall` reject path**

Se in futuro la chiamata viene rejected (L266-271 busy here), il `SaraAudioPort` è già stato registrato al bridge e mai sganciato → leak di slot. NON è la causa S234 (prima chiamata), ma è un bug latente collaterale che amplifica H1 a partire dalla seconda chiamata se la prima ha rejected o errorato.

#### **H4 (IMPROBABILE) — `mainThreadOnly=True` + race con libHandleEvents poll 20ms**

`libHandleEvents(20)` polling ogni 20ms (L413). Se la SDP negotiation conclude *fra* due poll, l'ordering è "compresso" e `onCallMediaState` fires nello stesso tick di `onCallState=CONFIRMED`, con il media sub-system non ancora stabile. Possibile contributing factor ma non root cause primaria.

### 2.3 Conclusione diagnosi

**Root cause primaria**: `startTransmit` chiamato in `onCallMediaState` **senza guard su `getPortId() != PJSUA_INVALID_ID`**. Il conference bridge slot del lato call non è ancora assegnato al firing di `onCallMediaState` per la prima incoming call. Il fix S153 (`lockCodecEnabled=False` + `mainThreadOnly=True`) ha eliminato il deadlock reinv_timer_cb ma ha esposto questa race "porta non pronta" che prima era mascherata dalla sequenza più lenta.

**Ipotesi S234 thread**: FALSIFICATA — il thread è già il main pjsua2 thread.

---

## SEZIONE 3 — Fix Proposti Rank-Ordered

### **FIX A (CONSIGLIATO) — Guard `getPortId() != PJSUA_INVALID_ID` + retry breve in `onCallMediaState`**

**Razionale**: probe lo stato dello slot prima di transmit. Se non pronto, ritry in micro-loop fino a max 500ms (poi rinuncia). Zero modifica architetturale, addresses H1+H2.

**Pseudocodice diff** (`voip_pjsua2.py:227-237`):

```python
def onCallMediaState(self, prm):
    ci = self.getInfo()
    for i, mi in enumerate(ci.media):
        if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
           mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
            try:
                call_audio = self.getAudioMedia(i)
            except pj.Error as exc:
                logger.warning(f"getAudioMedia({i}) failed: {exc}")
                continue

            # S235 FIX A — wait until conference bridge slot is assigned
            sara_port_id = self.audio_port.getPortId()
            call_port_id = call_audio.getPortId()
            attempts = 0
            while (call_port_id == pj.PJSUA_INVALID_ID or
                   sara_port_id == pj.PJSUA_INVALID_ID) and attempts < 25:
                time.sleep(0.02)  # 20ms — match libHandleEvents poll
                call_port_id = call_audio.getPortId()
                sara_port_id = self.audio_port.getPortId()
                attempts += 1

            if call_port_id == pj.PJSUA_INVALID_ID or sara_port_id == pj.PJSUA_INVALID_ID:
                logger.error(
                    f"S235: bridge slot not assigned after 500ms "
                    f"(call={call_port_id}, sara={sara_port_id}) — skipping transmit"
                )
                continue

            try:
                call_audio.startTransmit(self.audio_port)
                self.audio_port.startTransmit(call_audio)
                logger.info(
                    f"Audio bridge established: call(slot={call_port_id}) "
                    f"↔ Sara(slot={sara_port_id}) after {attempts*20}ms"
                )
            except pj.Error as exc:
                logger.error(f"S235: startTransmit failed even after slot ready: {exc}")
```

**Blast radius**: 1 metodo (`onCallMediaState`), ~20 righe. Nessun cambio firma. Compatibile retro (zero-attempt path identico a prima per chiamate fortunate). Tempo aggiuntivo worst-case 500ms (= meglio del 16s timeout Vodafone attuale). NB: `time.sleep` dentro un callback main-thread pjsua2 è OK perché `mainThreadOnly=True` serializza già tutto su quel thread; sospendere brevemente non rompe altri callback (verranno consumati al prossimo `libHandleEvents`).

⚠️ Caveat sleep nel main thread: durante i 500ms eventuali altri eventi pjsua2 sono accodati. Per evitare backpressure preferibile in produzione passare a Fix B (lazy `createPort`) che evita il loop di sleep.

---

### **FIX B (ALTERNATIVO, più pulito architettonicamente) — Lazy `createPort` in `onCallMediaState`**

**Razionale**: spostare `createPort` dal `__init__` Python (in cui pjsua2 non sa ancora che la call avrà media) al callback `onCallMediaState` (in cui pjsua2 ha completato SDP O/A e il media sub-system è stabile). Riduce il timing window.

**Pseudocodice diff**:

```python
# voip_pjsua2.py:90 — SaraAudioPort.__init__ (rimuovi createPort)
def __init__(self):
    super().__init__()
    self.rx_queue = queue.Queue(maxsize=500)
    self.tx_queue = queue.Queue(maxsize=3000)
    self._silence_frame = b'\x00' * 320
    self._current_tx_rms = 0.0
    self._port_created = False  # S235 FIX B

def ensure_port(self):
    """Lazy createPort — call from onCallMediaState only."""
    if self._port_created:
        return
    fmt = pj.MediaFormatAudio()
    fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
    self.createPort("sara_bridge", fmt)
    self._port_created = True

# voip_pjsua2.py:227 — onCallMediaState (call ensure_port)
def onCallMediaState(self, prm):
    ci = self.getInfo()
    for i, mi in enumerate(ci.media):
        if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
           mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
            self.audio_port.ensure_port()   # S235 FIX B
            call_audio = self.getAudioMedia(i)
            try:
                call_audio.startTransmit(self.audio_port)
                self.audio_port.startTransmit(call_audio)
                logger.info("Audio bridge established: call ↔ Sara")
            except pj.Error as exc:
                logger.error(f"S235: startTransmit failed: {exc}")
```

**Blast radius**: 2 metodi modificati, 1 metodo nuovo (`ensure_port`). Più invasivo ma elimina la race per costruzione. Tradeoff: alla seconda chiamata (`__init__` di una nuova `SaraCall`) il port viene ri-creato, va testato che pjsua2 non lamenti "port name conflict" o slot leak fra call. Se necessario nominare port unique: `f"sara_bridge_{id(self)}"`.

**Combina meglio con Fix A**: fai Fix B *e* aggiungi anche il guard `getPortId() != PJSUA_INVALID_ID` di Fix A → cintura + bretelle.

---

### **FIX C (ULTIMA RISORSA, workaround) — try/except retry su startTransmit**

**Razionale**: brutalmente fault-tolerant. Se H1 è transient, retry 5x con sleep 50ms catturando `pj.Error`.

**Pseudocodice diff**:

```python
def onCallMediaState(self, prm):
    ci = self.getInfo()
    for i, mi in enumerate(ci.media):
        if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
           mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
            call_audio = self.getAudioMedia(i)
            for attempt in range(5):  # S235 FIX C
                try:
                    call_audio.startTransmit(self.audio_port)
                    self.audio_port.startTransmit(call_audio)
                    logger.info(f"Audio bridge established (attempt {attempt+1})")
                    break
                except pj.Error as exc:
                    if attempt == 4:
                        logger.error(f"S235: startTransmit FAILED after 5 retries: {exc}")
                        break
                    time.sleep(0.05)
```

**Blast radius**: 1 metodo, ~10 righe. **NON consigliato** perché:
- Maschera diagnostica (non sappiamo se H1 o H2 o H4).
- Non c'è guard sullo stato → potrebbe retry su errore non-transient (es. invalid format) ciclando inutilmente.
- Lascia inalterato il design problema.

Usare solo se Fix A e B non sono applicabili per ragioni che ora non vedo.

---

### Ordine implementazione raccomandato

1. **Fix A da solo** → minimum-blast-radius, alta confidence root cause (H1).
2. Se Fix A non risolve in 2 chiamate test, applicare anche **Fix B** sopra (lazy createPort).
3. **Fix C scartato** salvo evidenza che A+B non bastino.

---

## SEZIONE 4 — Test Discriminate per Validare il Fix

### 4.1 Setup per validation (post fix S235)

Pre-condizioni:
- `ssh imac` pipeline UP con `VOIP_LOCAL_PORT=6080`
- SIP REGISTER 200 OK su sip.vivavox.it (verifica `/api/voice/voip/status`)
- Founder chiama 0972536918 da 3281536308

### 4.2 Cosa cercare nei log post-fix (`/tmp/sara-live-s235.log`)

#### Pattern di SUCCESSO (Fix A attivo):

```
HH:MM:SS  Incoming call from: <sip:3281536308@...>
HH:MM:SS  Answering call with 200 OK
HH:MM:SS  Audio bridge established: call(slot=N) ↔ Sara(slot=M) after Xms
                                                          ^^^^^^^^^^^^^^^
                                                          aspettativa: 0-100ms
HH:MM:SS  Call state: CONFIRMED          ⬅ deve arrivare entro 2s, NON 16s
HH:MM:SS  Call connected, starting audio processing
HH:MM:SS  Greeting queued for playback
HH:MM:SS+0.5  TTS audio queued for playback
```

#### Pattern di FALLIMENTO Fix A (slot mai pronto):

```
HH:MM:SS  Incoming call from: ...
HH:MM:SS  Answering call with 200 OK
HH:MM:SS  S235: bridge slot not assigned after 500ms (call=-1, sara=N) — skipping transmit
```

→ Se questo appare: H1 falsificata, escalate a Fix B (lazy createPort) perché il problema è sulla creazione port lato Sara, non sul timing slot lato call.

#### Pattern di FALLIMENTO Fix A (errore diverso):

```
HH:MM:SS  S235: startTransmit failed even after slot ready: <pj.Error msg>
```

→ Conference bridge in stato corrotto. Investigare H3 (slot leak da call precedenti). Verificare `_cleanup_pjsua2` (L526-542) sta sganciando correttamente l'`audio_port` con `stopTransmit` prima della distruzione (NON lo fa attualmente — tech debt).

### 4.3 Metriche quantitative target

| Metrica                                         | Pre-fix (S234) | Post-fix target |
|-------------------------------------------------|----------------|-----------------|
| Gap 200 OK → CONFIRMED                          | 16s            | <2s             |
| Time-to-greeting (caller hears Sara)            | ∞ (mai)        | <3s             |
| pjsua2.Error count a `voip_pjsua2.py:235`       | 1+ per call    | 0               |
| "Audio bridge established" log line             | assente        | presente, attempts<5 |
| Vodafone "telefono spento" message              | sì             | no              |

### 4.4 Test di regressione 2 chiamate consecutive

Founder chiama 2 volte (call 1 → hangup founder → 10s pausa → call 2). Verificare:
- Entrambe call 1 e call 2 producono "Audio bridge established"
- Nessun `pj.Error` su call 2 (ipotesi H3: slot leak)
- `_current_call` torna a None fra una call e l'altra (verifica L612 `_on_call_disconnected`)

### 4.5 Test stress (deferred S236 se S235 verde su single-call)

3 chiamate in sequenza, validazione patterns stress S232 (SALONE + AUTO + BEAUTY) via PSTN. Output atteso `voice-agent/tests/e2e/live-hw-s235.md` con per-verticale OK/WARN/FAIL.

---

## TL;DR per esecuzione S235

1. **Ipotesi S234 thread Python falsificata**: `SaraAudioPort.createPort` già gira sul pjsua2 main thread (via `mainThreadOnly=True` + `threadCnt=0`).
2. **Root cause vera**: race timing — `onCallMediaState` fires prima che il conference bridge abbia assegnato slot al lato call. `startTransmit` riceve `AudioMedia.getPortId() == PJSUA_INVALID_ID` → `pj.Error` raw SWIG.
3. **Fix consigliato**: Fix A (guard `getPortId()` + retry 20ms × 25 attempts = max 500ms) — 20 righe in 1 metodo, no signature change.
4. **Fix backup**: Fix B (lazy `createPort` in `onCallMediaState`) — più pulito ma più invasivo. Combinabile con A.
5. **Fix da evitare**: Fix C (blind retry) — maschera diagnostica.
6. **Validation E2E**: 2 chiamate consecutive, gap 200 OK→CONFIRMED <2s, no `pj.Error` log, founder sente greeting <3s.

— END S235 RESEARCH —
