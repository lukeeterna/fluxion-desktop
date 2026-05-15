O # DOSSIER — Sara Voice Agent FLUXION: bug SIGABRT pjlib `grp_lock_unset_owner_thread`

> **Scopo**: dossier self-contained per delega a Claude.ai (web/desktop, sessione nuova senza contesto codebase). Contiene tutto il necessario per risolvere il bug definitivamente.
>
> **Stato**: bug aperto da 8 sessioni (S232 → S239). Pipeline FLUXION non ha mai erogato audio Sara in produzione SIP live. Tutti i fix tentati hanno migliorato strumentazione/eliminato sotto-bug ma il bug principale persiste.
>
> **Generato**: 2026-05-15 ~16:35 CEST (chiusura S239 ORANGE — F3 falsified come F2).
>
> **Founder context**: Gianluca Di Stasi (Lavello PZ, Italia). FLUXION è desktop SaaS per PMI italiane (saloni, palestre, cliniche, officine). Pricing €497 lifetime. Sara è il differenziatore competitivo. Bug VoIP = product killer. Nessun cliente attivo ancora ma bug deve essere risolto prima del lancio.

---

## 1. Executive summary del bug

### Comportamento osservato
- Cliente telefona a numero EHIWEB SIP `0972536918@sip.vivavox.it`.
- Pipeline pjsua2 risponde con SIP 200 OK in <100ms.
- Audio bridge tra call leg e Sara AudioMediaPort viene stabilito in 0ms (`Audio bridge established: call(slot=1) ↔ Sara(slot=2)`).
- **Immediatamente** dopo lo stabilimento del bridge, l'intero processo Python crasha con SIGABRT.
- Lato chiamante: voice mailbox Vodafone risponde "telefono spento o non raggiungibile" perché la chiamata cade prima dell'erogazione dell'audio Sara.

### Errore C-side che causa SIGABRT
```
Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.
```

Questa è una assertion in `pjlib/src/pj/lock.c:279` (pjsip 2.16-dev). Significa: il thread che sta facendo *release* di un `pj_grp_lock` (group lock) **non è** lo stesso che lo ha acquisito. pjlib usa un meccanismo di group lock con owner tracking; se il thread chiamante (`pj_thread_this()`) non coincide con `glock->owner` settato durante l'acquire, l'assertion fires e abort() killa il processo.

### Faulthandler dump S239 (post-fix F3, smoking gun più recente)
```
Fatal Python error: Aborted

Current thread 0x0000700011add000 (most recent call first):
  File "lib/pjsua2/pjsua2.py", line 13767 in libHandleEvents
  File "src/voip_pjsua2.py", line 708 in _pjsua2_thread          <- thread che ABORTA
  File "threading.py", line 910 in run
  File "threading.py", line 973 in _bootstrap_inner
  File "threading.py", line 930 in _bootstrap

Thread 0x0000000103ea9600 (most recent call first):
  File "selectors.py", line 562 in select
  File "asyncio/base_events.py", line 1854 in _run_once
  File "asyncio/base_events.py", line 596 in run_forever
  File "asyncio/base_events.py", line 629 in run_until_complete
  File "main.py", line 1379 in cli
```

**Solo 2 thread visibili nel dump** (S239, post-fix F3 che ha sostituito il default executor asyncio con uno che registra i worker con pjlib):
1. `_pjsua2_thread` — il thread che aborta. Quello È registrato con pjlib (libRegisterThread chiamato in `_init_pjsua2` indirettamente da `libCreate`).
2. Main asyncio event loop thread — in `selectors.select()`, non sta toccando pjsua2.

**I 2 `concurrent.futures.thread._worker` thread visibili in S238 (pre-F3) sono SPARITI in S239.** Significa che il fix F3 (default executor con `initializer=libRegisterThread`) ha eliminato i TPE workers come sospetti, **ma il bug persiste identico**. Quindi i TPE workers **non erano** il vero colpevole — erano solo dormienti nel pool al momento del dump S238.

---

## 2. Stack tecnico ed environment

### Software stack
| Componente | Versione |
|---|---|
| OS iMac (server VoIP) | macOS 12.x Monterey (Darwin 21.6, x86_64) |
| Python | 3.9.x (CommandLineTools framework) |
| pjsip | **2.16-dev** (built from source, SWIG Python bindings) |
| pjsua2 lib | `voice-agent/lib/pjsua2/` (bundled, no pip install) |
| asyncio | stdlib Python 3.9 |
| aiohttp | per HTTP server porta 3002 |

### Architettura runtime
```
                 +-----------------------------------+
                 | main asyncio event loop thread    |
                 | (Python 3.9, aiohttp server :3002)|
                 +-----------------+-----------------+
                                   |
                          asyncio.create_task ...
                                   |
                                   v
                 +-----------------+-----------------+
                 |  asyncio default ThreadPoolExecutor|
                 |  (S239 F3: initializer=pjlib_init) |
                 |  workers: TTS chunks, STT, groq    |
                 +------------------------------------+

                 +-----------------------------------+
                 | _pjsua2_thread (daemon)           |  <- ABORTA SIGABRT
                 | loop: ep.libHandleEvents(20ms)    |
                 +-----------------+-----------------+
                                   |
                          C-side callbacks
                                   |
                  +----------------+--------------+
                  |                               |
                  v                               v
        +-------------------+         +---------------------+
        | SaraCall          |         | SaraAudioPort       |
        | onIncomingCall    |         | onFrameRequested 50Hz|
        | onCallMediaState  |         | onFrameReceived 50Hz |
        | onCallState       |         | (thread Python      |
        |                   |         |  custom audio_cb)   |
        +-------------------+         +---------------------+

                 +-----------------------------------+
                 | pjmedia clock master thread       |  <- SOSPETTO NUOVO (vedi sez. 6)
                 | (C-only, spawnato internamente    |
                 |  da pjsua_set_null_snd_dev o      |
                 |  conf_bridge clock)               |
                 +-----------------------------------+
```

### Config pjsua2 attiva
```python
ep_cfg.uaConfig.threadCnt = 0          # NO pjsua internal workers
ep_cfg.uaConfig.mainThreadOnly = True  # callbacks solo su pjsua main thread (_pjsua2_thread)
ep_cfg.medConfig.noVad = True
ep_cfg.medConfig.srtpUse = 0           # SRTP disabilitato
# Transport: UDP porta 6080 (5060=Traccar, 5080=old voip.py)
# Audio device: setNullDev() applicato dopo libStart (S237 F1)
# SIP: 0972536918@sip.vivavox.it (EHIWEB VoIP IT)
# NAT: ICE+STUN (stun.voip.vivavox.it:3478)
```

---

## 3. Cronologia tentativi (S232 → S239)

| Sessione | Fix tentato | Esito | Insight residuo |
|---|---|---|---|
| **S232** | Test text-based (no SIP) 147/0/0 | Pipeline funziona offline | Bug emerge solo in SIP live |
| **S233** | Setup live SIP, test prima chiamata reale | Crash su seconda call | hypothesis race condition iniziale |
| **S234** | Reproduce SIGABRT deterministico | Bug emerge sempre, anche prima call | hypothesis: race sul `audio_port` Python lifetime |
| **S235** Fix B+A | (B) lazy `createPort` dentro `onCallMediaState`; (A) guard `getPortId() != PJSUA_INVALID_ID` retry 20ms×25 | Crash persiste | guard non rileva slot invalid — la race non è quella |
| **S236** | Diagnostic patch `_pj_error_info()` helper (estrae `exc.info(True)` invece di `f"{exc}"`) + introspection MRO/refcount/format | Test live cattura **status=506784** "Unknown error 506784" su `pjsua_conf_connect` | OSStatus encoded nel gap pjsua errno 470000-519999. Core Audio open block 14.5s su SSH headless. |
| **S237** Fix F1 | `audDevManager().setNullDev()` dopo `libStart()` (prima di startTransmit) | **startTransmit ora SUCCESS in 0ms!** Bridge wiring riuscito | Nuovo blocker: `grp_lock_unset_owner_thread` assertion subito dopo bridge established |
| **S237** Fix F1-bis | `_ensure_thread_registered()` con `threading.local()` in `onFrameRequested`/`onFrameReceived` (audio callbacks 50Hz) | Crash persiste | callbacks audio ora registrano il loro thread ma assertion fires comunque |
| **S238** Fix F2 | Wrap thread spawn di `on_connected`/`on_disconnected` con `_run_with_pjlib_registration` helper. Aggiunto `faulthandler.enable(all_threads=True)` | Crash persiste. Faulthandler dump rivela 2 `concurrent.futures.thread._worker` non registrati | F2 **falsified** dal dump: thread spawn registrati ma non erano loro il colpevole |
| **S239** Fix F3 | `_install_pjlib_aware_default_executor()` chiamato dopo `_pj_started.wait()`. Sostituisce asyncio default executor con `ThreadPoolExecutor(initializer=_pjlib_thread_initializer)` | Crash persiste. **TPE workers spariscono dal dump** ma SIGABRT identico | F3 **falsified** dal dump: TPE workers non erano il colpevole. Resta solo `_pjsua2_thread` e main asyncio loop nel dump finale. |

### Cosa è FUNZIONANTE oggi (mantenuto in master)
- F1 `setNullDev`: ✅ Core Audio non blocca più, `startTransmit` ritorna 0ms.
- F1-bis `_ensure_thread_registered`: ✅ audio callback thread registrato (idempotente, defensive).
- F2 `_run_with_pjlib_registration`: ✅ thread spawn di on_connected/on_disconnected registrati (defensive, zero overhead).
- F3 `_install_pjlib_aware_default_executor`: ✅ asyncio default executor sostituito con TPE pjlib-aware (defensive, zero overhead — TPE non era il colpevole ma il fix è correct-by-construction).
- `faulthandler.enable(all_threads=True)`: ✅ strumento diagnostico continuo, fondamentale per discriminare hypothesis future.

### Cosa NON funziona ancora
- Bug primario `grp_lock_unset_owner_thread` SIGABRT immediatamente dopo `Audio bridge established`. Vodafone "telefono spento". Sara non parla mai al cliente.

---

## 4. Smoking gun S239 — log completo della call test

Test eseguito 2026-05-15 16:25:23 CEST. Founder chiama 0972536918 da +39 3281536308.

```
16:23:13 [src.voip_pjsua2] INFO: pjsua2 started on port 6080
16:23:13 [src.voip_pjsua2] INFO: pjsua2: null audio device installed (headless mode, S237 F1)
16:23:13 [src.voip_pjsua2] INFO: TURN not configured (STUN only — CGNAT users may have issues)
16:23:13 [src.voip_pjsua2] INFO: E7: UDP keepalive enabled every 15s
16:23:13 [src.voip_pjsua2] INFO: SIP account created: 0972536918@sip.vivavox.it
16:23:13 [src.voip_pjsua2] INFO: S239 F3: asyncio default executor replaced with pjlib-registered TPE
16:23:13 [src.voip_pjsua2] INFO: Registration: active=True, status=200 OK
16:23:13 [src.voip_pjsua2] INFO: SIP REGISTERED successfully
16:23:16 [src.voip_pjsua2] INFO: VoIP started: 0972536918@sip.vivavox.it

16:25:23 [src.voip_pjsua2] INFO: Incoming call from: <sip:3281536308@79.98.45.133>
16:25:23 [src.voip_pjsua2] INFO: Incoming call from: <sip:3281536308@79.98.45.133> -> phone: 3281536308
16:25:23 [src.voip_pjsua2] INFO: Answering call with 200 OK (direct - S153 fix)
16:25:23 [src.voip_pjsua2] INFO: S236 DIAG H1: call_audio=AudioMedia mro=['AudioMedia', 'Media', 'object'] | audio_port=SaraAudioPort mro=['SaraAudioPort', 'AudioMediaPort', 'AudioMedia', 'Media', 'object']
16:25:23 [src.voip_pjsua2] INFO: S236 DIAG H2: audio_port id=4450379568 refcount=2 _port_created=True
16:25:23 [src.voip_pjsua2] INFO: S236 DIAG H3: call.format clockRate=8000 ch=1 bits=16 frameUsec=20000 | sara.format clockRate=8000 ch=1 bits=16 frameUsec=20000
16:25:23 [src.voip_pjsua2] INFO: Audio bridge established: call(slot=1) ↔ Sara(slot=2) after 0ms
Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.

Fatal Python error: Aborted

Current thread 0x0000700011add000 (most recent call first):
  File "lib/pjsua2/pjsua2.py", line 13767 in libHandleEvents
  File "src/voip_pjsua2.py", line 708 in _pjsua2_thread

Thread 0x0000000103ea9600 (most recent call first):
  File "selectors.py", line 562 in select
  File "asyncio/base_events.py", line 1854 in _run_once
  File "asyncio/base_events.py", line 596 in run_forever
  File "asyncio/base_events.py", line 629 in run_until_complete
  File "main.py", line 1379 in cli
```

### Osservazioni chiave del dump S239
1. **Solo 2 thread Python attivi** al momento del crash. Tutti gli altri thread che esistevano prima (`onFrameRequested` audio worker, on_connected daemon, TPE workers) sono **assenti**.
2. Il thread che aborta (`_pjsua2_thread`) è dentro `libHandleEvents(20)` poll loop. Quel thread era stato esplicitamente registrato durante `libCreate()` (pjsua2 main thread setup).
3. Tra `Audio bridge established` e SIGABRT trascorre **tempo non misurato ma < poll cycle 20ms**.
4. Il crash NON arriva nel callback `onCallMediaState` (che è già ritornato — vediamo il log "Audio bridge established" stampato prima). Arriva nel poll successivo di `libHandleEvents`.

### Sequenza interna pjsip presunta (da reverse engineering)
1. `onCallMediaState` esegue `call_audio.startTransmit(audio_port)` + `audio_port.startTransmit(call_audio)` (linee 508-509 di `voip_pjsua2.py`).
2. `startTransmit` C-side chiama `pjsua_conf_connect(src_id, sink_id)` che a sua volta chiama `pjmedia_conf_connect_port` sul conference bridge low-level.
3. `pjmedia_conf_connect_port` acquisisce **`conf->grp_lock`** (group lock del conference bridge) per modificare la routing table.
4. Su acquire, `pj_grp_lock_acquire` setta `glock->owner = pj_thread_this()` — il calling thread (qui `_pjsua2_thread`).
5. La connessione viene completata. **Ma poi pjmedia spawna un clock thread** (master port clock) che è un thread C-side non visibile a Python.
6. Quel clock thread inizia a girare. **Probabilmente acquisisce e rilascia `grp_lock` durante operazioni di pull frame**, ma con identità thread diversa.
7. Al prossimo `libHandleEvents` da `_pjsua2_thread`, pjsip processa eventi pendenti. Uno di questi richiede release di `grp_lock`. Ma il vero owner C-side è il clock thread, non `_pjsua2_thread`. Assertion fires.

---

## 5. Codice rilevante (file `voice-agent/src/voip_pjsua2.py`)

### Helper module-level (linee 39-118)
```python
def _run_with_pjlib_registration(name: str, target: Callable, *args, **kwargs):
    """S238 F2: thread entrypoint che registra con pjlib prima di invocare callback."""
    try:
        pj.Endpoint.instance().libRegisterThread(name)
    except pj.Error:
        pass  # idempotent
    target(*args, **kwargs)


def _pjlib_thread_initializer():
    """S239 F3: ThreadPoolExecutor initializer."""
    try:
        name = f"sara_tpe_{threading.get_ident()}"
        pj.Endpoint.instance().libRegisterThread(name)
    except pj.Error:
        pass
    except Exception:
        logger.debug("S239 F3: TPE initializer ran before Endpoint ready (non-fatal)")


def _install_pjlib_aware_default_executor(loop):
    """S239 F3: replace asyncio default executor con TPE pjlib-aware."""
    new_executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=32,
        thread_name_prefix="asyncio-pjlib",
        initializer=_pjlib_thread_initializer,
    )
    old_executor = getattr(loop, "_default_executor", None)
    loop.set_default_executor(new_executor)
    if old_executor is not None:
        try:
            old_executor.shutdown(wait=False)
        except Exception:
            pass
    logger.info("S239 F3: asyncio default executor replaced with pjlib-registered TPE")
```

### SaraAudioPort (audio bridge SWIG director, linee 197-346)
```python
class SaraAudioPort(pj.AudioMediaPort):
    def __init__(self):
        super().__init__()
        self.rx_queue = queue.Queue(maxsize=500)
        self.tx_queue = queue.Queue(maxsize=3000)
        self._silence_frame = b'\x00' * 320
        self._port_created = False
        self._thread_local = threading.local()

    def _ensure_thread_registered(self):
        """S237 F1-bis: idempotent thread registration with pjlib."""
        if getattr(self._thread_local, "registered", False):
            return
        try:
            ep = pj.Endpoint.instance()
            ep.libRegisterThread(f"sara_audio_cb_{threading.get_ident()}")
            self._thread_local.registered = True
        except pj.Error:
            self._thread_local.registered = True

    def ensure_port(self):
        """S235 Fix B: lazy createPort."""
        if self._port_created:
            return
        fmt = pj.MediaFormatAudio()
        fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)  # L16 PCM 8kHz mono 20ms 16bit
        self.createPort("sara_bridge", fmt)
        self._port_created = True

    def onFrameReceived(self, frame):
        self._ensure_thread_registered()
        if frame.type == pj.PJMEDIA_FRAME_TYPE_AUDIO:
            try:
                self.rx_queue.put_nowait(bytes(frame.buf))
            except queue.Full:
                pass

    def onFrameRequested(self, frame):
        self._ensure_thread_registered()
        try:
            audio_data = self.tx_queue.get_nowait()
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(audio_data)
        except queue.Empty:
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(self._silence_frame)
```

### SaraCall.onCallMediaState (dove avviene il bridge wiring, linee 393-523)
```python
def onCallMediaState(self, prm):
    # S236 H4: register thread first (defensive)
    try:
        pj.Endpoint.instance().libRegisterThread("onCallMediaState")
    except Exception:
        pass

    ci = self.getInfo()
    for i, mi in enumerate(ci.media):
        if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
            try:
                self.audio_port.ensure_port()
            except pj.Error as exc:
                logger.error(f"S236: ensure_port failed | info={_pj_error_info(exc)}")
                continue

            try:
                call_audio = self.getAudioMedia(i)
            except pj.Error as exc:
                logger.warning(f"S236: getAudioMedia({i}) failed | info={_pj_error_info(exc)}")
                continue

            # S235 Fix A: wait until conference bridge slot assigned
            sara_port_id = self.audio_port.getPortId()
            call_port_id = call_audio.getPortId()
            attempts = 0
            while (call_port_id == pj.PJSUA_INVALID_ID or
                   sara_port_id == pj.PJSUA_INVALID_ID) and attempts < 25:
                time.sleep(0.02)
                call_port_id = call_audio.getPortId()
                sara_port_id = self.audio_port.getPortId()
                attempts += 1

            if call_port_id == pj.PJSUA_INVALID_ID or sara_port_id == pj.PJSUA_INVALID_ID:
                logger.error("S235: bridge slot not assigned after 500ms - skipping transmit")
                continue

            # Bidirectional bridge: call <-> Sara
            try:
                call_audio.startTransmit(self.audio_port)    # <-- linea 508
                self.audio_port.startTransmit(call_audio)    # <-- linea 509
                logger.info(f"Audio bridge established: call(slot={call_port_id}) <-> Sara(slot={sara_port_id}) after {attempts*20}ms")
            except pj.Error as exc:
                logger.error(f"S236: startTransmit failed | info={_pj_error_info(exc)}")
```

### VoIPManager.start() + init pjsua2 (linee 613-810)
```python
async def start(self) -> bool:
    if self._running:
        return True
    if not self.config.username or not self.config.password:
        return False
    self._main_loop = asyncio.get_running_loop()
    self._pj_thread = threading.Thread(target=self._pjsua2_thread, daemon=True)
    self._pj_thread.start()
    if not self._pj_started.wait(timeout=10):
        return False
    # S239 F3: replace asyncio default executor with pjlib-aware one
    _install_pjlib_aware_default_executor(self._main_loop)
    await asyncio.sleep(3)
    if self._registered:
        self._running = True
        return True
    ...

def _pjsua2_thread(self):
    """Background thread running pjsua2 endpoint."""
    try:
        self._init_pjsua2()
        self._pj_started.set()
        while not self._pj_stop.is_set():
            self._ep.libHandleEvents(20)   # <-- linea 708, ABORTA QUI
        self._cleanup_pjsua2()
    except Exception as exc:
        logger.error(f"pjsua2 thread error: {exc}", exc_info=True)

def _init_pjsua2(self):
    self._ep = pj.Endpoint()
    self._ep.libCreate()
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.userAgent = self.config.user_agent
    ep_cfg.uaConfig.stunServer.append(self.config.stun_server)
    ep_cfg.uaConfig.threadCnt = 0
    ep_cfg.uaConfig.mainThreadOnly = True
    ep_cfg.medConfig.noVad = True
    ep_cfg.medConfig.srtpUse = 0
    self._ep.libInit(ep_cfg)

    tp_cfg = pj.TransportConfig()
    tp_cfg.port = self.config.local_port
    self._transport_id = self._ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)
    self._ep.libStart()
    self._ep.audDevManager().setNullDev()   # S237 F1
    # ... SIP account creation, NAT config, register
```

---

## 6. Hypothesis residue (in ordine di priorità per Claude.ai)

### N1 — pjmedia clock master thread non registrato (TOP)
**Tesi**: dopo `pjsua_conf_connect` (chiamato da `startTransmit`), pjmedia avvia un *clock master thread* C-side per pullare frame dal conference bridge a 50Hz. Quel thread è creato internamente da pjmedia, **NON è controllato da `threadCnt=0`** (che riguarda solo pjsua worker thread, non pjmedia clock).

Il clock thread acquisisce `conf->grp_lock` per leggere la routing table. Lo rilascia. Ma il release avviene da un thread con identità diversa da quella registrata in pjlib TLS perché il clock thread non è mai stato passato attraverso `pj_thread_register`.

**Evidence**:
- `Audio bridge established after 0ms` log seguito immediatamente da assertion.
- Faulthandler dump S239 mostra solo 2 thread Python ma il clock thread C-only non comparirebbe nel dump Python (è un pthread puro senza Python state).
- Pattern documentato in pjsip-users mailing list per implementazioni custom audio port (es. https://lists.pjsip.org/pipermail/pjsip/2019-October/021871.html — non verificato).

**Fix tentati**:
- F1-bis (`_ensure_thread_registered` in onFrameRequested/Received): NO, perché il clock thread non chiama mai i callback Python — pulla frame dal bridge low-level prima di passare a `onFrame*`.

**Fix proposto N1-a**: spostare il null sound device su un **master port** custom invece di `setNullDev`:
```python
# Sostituire ep.audDevManager().setNullDev() con un null master port esplicito
null_port = pj.MediaPort()  # implementazione custom che ritorna silenzio
# attach al conference bridge come master clock source (cui pjmedia delega clock thread management)
```
Riferimento: `pjmedia_master_port_create` C API.

**Fix proposto N1-b**: bypassare completamente il conference bridge usando direttamente `AudioMediaPlayer` + `AudioMediaRecorder` su WAV pipe FIFO, evitando il clock master. Più invasivo ma rimuove la dipendenza da pjmedia bridge clock.

### N2 — SWIG director pattern + Python GC sul `SaraAudioPort`
**Tesi**: `SaraAudioPort` deriva da `pj.AudioMediaPort` via SWIG director pattern. Director objects in SWIG sono SOGGETTI a Python GC: se il refcount Python va a 0 mentre il C-side ha ancora un riferimento, l'object viene deallocato e i pthread C-side che lo accedono falliscono con state corrotto.

**Evidence**:
- S236 DIAG H2 logga `refcount=2` (basso) per `audio_port`. Reference holders: `self` di `SaraCall` + il frame stack di `onCallMediaState`. Se `onCallMediaState` ritorna prima che il clock thread ne abbia preso reference C-side, GC può kickare.
- `self.audio_port` in `SaraCall.__init__` mantiene reference per la vita della call, ma C-side il refcount Python non viene incrementato perché SWIG director non incrementa Py refcount automaticamente.

**Fix proposto N2**: aggiungere `self.audio_port` a una collection class-level (SaraAccount.active_ports list) per garantire long-lived reference:
```python
class SaraAccount(pj.Account):
    def __init__(self):
        super().__init__()
        self.active_ports = []   # CRITICAL: keep Python references alive
    def onIncomingCall(self, prm):
        call = SaraCall(self, prm.callId)
        self.active_ports.append(call.audio_port)  # prevent GC
        # ...
```

### N3 — pj.Endpoint.instance() return inconsistent
**Tesi**: `Endpoint.instance()` in SWIG potrebbe ritornare wrapper Python diversi a ogni chiamata (anche se C-side è singleton). Se `libRegisterThread` viene chiamato su wrapper A e poi qualcosa internamente chiama via wrapper B, il TLS state pjlib è inconsistente.

**Fix proposto N3**: salvare `ep = pj.Endpoint.instance()` UNA VOLTA al setup e passarlo esplicitamente ovunque serva, eliminando call multipli a `instance()`.

### N4 — Versione pjsip 2.16-dev pre-release con bug noto
**Tesi**: `2.16-dev` è un build dev branch. Possibili bug regressi non in release stable.

**Fix proposto N4**: downgrade a pjsip 2.15 stable LTS, rebuild bindings SWIG. Cost ~2h.

### N5 — Architettura switch: abbandonare pjsua2, usare PJSIP più low-level o switch engine
**Opzioni**:
- **N5-a**: usare `pjsua` legacy C API (no pjsua2 wrapper, no SWIG director). Più verbose ma evita tutti i bug SWIG director threading.
- **N5-b**: `aiortc` (pure Python WebRTC, ma non SIP native — richiede gateway WebRTC<->SIP es. Jambonz, Asterisk).
- **N5-c**: `python-baresip` (binding a baresip C). Diverso engine, stesso C threading pattern.
- **N5-d**: usare `asterisk` come PBX e parlare ARI (Asterisk REST Interface) — separa completamente Sara dal SIP stack. Sara diventa HTTP service che riceve audio stream via ARI. Massima isolation, costo ~1-2 giorni di setup Asterisk Docker.

**Raccomandazione**: se N1-a (master port custom) e N2 (refcount fix) non risolvono entro 1 sessione, valutare **N5-d** (Asterisk ARI). Pattern usato da Twilio, Telnyx, infobip in produzione. Asterisk gestisce SIP, Sara è un endpoint audio HTTP/WebSocket. Zero pjsua2 nel processo Python = zero bug threading pjlib.

---

## 7. Comandi riproducibili (per test in nuova sessione)

### Setup ambiente iMac (gia presente)
```bash
# Repo iMac
cd "/Volumes/MacSSD - Dati/fluxion"
git pull origin master   # current: 4da1352 (S239 F3 fix)

# Pipeline path
cd voice-agent
ls -la lib/pjsua2/   # bundled SWIG bindings, no pip install

# Env vars in voice-agent/.env
VOIP_SIP_USER=0972536918
VOIP_SIP_SERVER=sip.vivavox.it
VOIP_SIP_PASS=<see .env>
VOIP_ENABLED=true
VOIP_LOCAL_PORT=6080
```

### Start pipeline
```bash
ssh imac "lsof -ti:3002 | xargs -r kill -9; sleep 1"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  VOIP_LOCAL_PORT=6080 nohup ./venv/bin/python main.py > /tmp/sara-live.log 2>&1 & \
  echo PID=\$!"
```

### Verify SIP REGISTERED
```bash
sleep 15
ssh imac "curl -s http://127.0.0.1:3002/health"
# expect: {"status": "ok", ...}
ssh imac "grep 'SIP REGISTERED' /tmp/sara-live.log"
```

### Trigger bug (test live)
Founder chiama `0972536918` da cellulare. Pipeline crasha dopo `Audio bridge established`.

### Capture faulthandler dump
```bash
ssh imac "cat /tmp/sara-live.log" | grep -A50 "Audio bridge established"
```

### Cleanup
```bash
ssh imac "lsof -ti:3002 | xargs -r kill -9"
```

---

## 8. File chiave da leggere (paths assoluti su iMac)

| File | Linee chiave | Cosa contiene |
|---|---|---|
| `/Volumes/MacSSD - Dati/fluxion/voice-agent/src/voip_pjsua2.py` | 1-870 | Tutto il codice pjsua2 wrapping. Tutti i fix S232-S239. |
| `/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2/pjsua2.py` | 13767 (libHandleEvents) | SWIG bindings auto-generated. Cercare wrapper Endpoint, AudioMediaPort, Call. |
| `/Volumes/MacSSD - Dati/fluxion/voice-agent/main.py` | 1059-1379 | aiohttp server start, VoIPManager init, asyncio.run entry point. |
| `/Volumes/MacSSD - Dati/fluxion/voice-agent/.env` | VOIP_* | Credenziali SIP, port, server. |

### File research già prodotti (da rileggere)
- `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/s238/pjsua2-clock-master-pattern.md` (388 righe) — research voice-engineer subagent S238 sul pattern clock master pjmedia. **Da leggere prima di scegliere fix N1.**
- `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/s238/faulthandler-analysis.md` — analisi dump S238.
- `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/s239/live-test-log-full.txt` — log S239 completo (post-F3).
- `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/s238/live-test-log-full.txt` — log S238 pre-F3 con TPE workers visibili.

---

## 9. Vincoli di business (NON tecnici)

- **Founder NON sviluppatore**. Soluzioni devono essere autocontenute, comandi shell pronti, no "ora apri X e configura Y a mano".
- **Zero costi**: NO servizi paid (Twilio, Telnyx, ecc.) se richiedono carta di credito. Se la soluzione è Asterisk Docker self-hosted su iMac = OK. Se richiede Telnyx €0.005/min = NO finché non ci sono clienti reali.
- **Hardware fisso**: iMac 2012 macOS 12, MacBook Big Sur 11, no GPU, RAM limitata. Soluzione deve girare lì.
- **Tempo**: bug deve essere fixed entro 1-2 sessioni. Founder è sotto pressione lancio. Workaround temporaneo accettabile se sblocca audio (es: usare pjsua legacy invece di pjsua2 anche se più verbose).

---

## 10. Cosa serve da Claude.ai per chiudere il bug

### Tier 1 (urgente, blocking)
1. **Confermare o falsificare N1** (pjmedia clock master thread): leggere `pjmedia/conference.c` upstream pjsip GitHub (https://github.com/pjsip/pjproject), verificare se conf bridge spawna clock thread interno quando si chiama `pjsua_conf_connect` con pjsua attached al null device.
2. Se N1 confermato: fornire fix in codice Python (modifica a `voip_pjsua2.py`) che:
   - Sostituisce `setNullDev()` con master port custom che gestisce il clock dal main pjsua2 thread, OR
   - Registra esplicitamente il pjmedia clock thread tramite hook (se pjsua2 lo espone).
3. Se N1 falsificato: procedere su N2 (refcount fix) con commit one-shot.

### Tier 2 (se Tier 1 non risolve)
4. Valutare costo/beneficio switch a Asterisk ARI (N5-d). Fornire blueprint setup: docker-compose Asterisk + Python aiohttp client che parla ARI + audio bridge via PJSIP_to_RTP.
5. In alternativa, valutare downgrade pjsip 2.15 stable + rebuild bindings su iMac.

### Tier 3 (long-term hardening)
6. Test suite mock per riprodurre il bug **senza** chiamata SIP reale (es. mock incoming call + simulated audio frames). Permette iterazione veloce senza dipendere da chiamate cellulare founder.

---

## 11. Comando ripartenza per nuova sessione Claude.ai

```
Sono il founder di FLUXION (gestionale italiano per PMI). Ho un bug VoIP critico
che blocca il lancio del mio voice agent "Sara". Pipeline Python 3.9 + pjsua2
(SWIG bindings pjsip 2.16-dev) su iMac macOS 12. SIP REGISTER OK, ma immediatamente
dopo "Audio bridge established" il processo crasha con SIGABRT:

  Assertion failed: (glock->owner == pj_thread_this()),
  function grp_lock_unset_owner_thread, file lock.c, line 279.

Ho gia tentato 9 fix in 8 sessioni (F1 setNullDev OK, F1-bis register audio
callback threads, F2 register on_connected daemon, F3 register asyncio TPE).
Faulthandler dump finale mostra solo 2 thread Python al crash: _pjsua2_thread
(che aborta in libHandleEvents) e main asyncio loop (in selectors.select).
Tutti i thread Python che hanno toccato pjsua2 sono stati registrati con
pj_thread_register. Il bug persiste = il colpevole e' un thread C-only
(pjmedia clock master?) non visibile da Python.

Leggi il dossier completo: DOSSIER-SARA-VOIP-BUG.md (questo file).

Obiettivo: risolvere definitivamente il SIGABRT. Founder NON sviluppatore,
serve patch Python self-contained o blueprint architetturale alternativo
(Asterisk ARI N5-d e' opzione accettabile). Zero costi paid services.

Inizia con N1 (verifica pjmedia clock master thread) leggendo pjsip upstream
GitHub. Poi fix concreto.
```

---

## 12. Cronologia commit (riferimento git)

```
4da1352 fix(S239-F3): pjlib-aware asyncio default executor — register TPE workers
383d892 chore(S238): close session ORANGE — F2 falsified, TPE workers identified as real culprit
7e68045 fix(S238-F2): register Python callback threads with pjlib + faulthandler
5a8bf28 chore(S237): close session ORANGE — F1 success status=506784 resolved, new blocker pjmedia clock thread assertion
cf243b2 fix(S237-F1-bis): register pjlib worker thread in audio frame callbacks
685d44c fix(S237-F1): setNullDev after libStart unblocks startTransmit
db47cc5 fix(S236): _pj_error_info helper + structured pj.Error logging
28ddbd0 fix(S235-A+B): lazy createPort + slot guard
```

---

**FINE DOSSIER**. Per domande tecniche aggiuntive, scrivere a Luke (gianluca.distasi81@gmail.com) o aprire il repo `https://github.com/lukeeterna/fluxion-desktop` (privato, accesso da chiedere).
