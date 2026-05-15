# S238 — pjsua2 clock-master pattern & grp_lock_unset_owner_thread assertion

> Research file. Generated 2026-05-15. Source evidence: GitHub raw pjproject@master
> (`pjsip/src/pjsua-lib/pjsua_aud.c`, `pjmedia/src/pjmedia/{master_port,clock_thread,conference}.c`,
> `pjlib/src/pj/lock.c`, `pjsip-apps/src/samples/pjsua2_demo.cpp`) and local
> `voice-agent/lib/pjsua2/pjsua2.py` SWIG wrapper.

---

## TL;DR (5 righe)

1. **`setNullDev()` è il pattern raccomandato** dai sample upstream (`pjsua2_demo.cpp:395`).
   Non sostituirlo con `setNoDev()`: quello disconnette il master port lasciando il conf
   bridge senza clock → frame callbacks (`onFrameRequested`/`onFrameReceived`) non
   verranno MAI invocate (è ciò che osservi: callbacks mai chiamate).
2. Il clock-thread interno spawnato da `pjmedia_clock_start` usa `pj_thread_create`
   (`clock_thread.c:231`) → **è registrato in pjlib**. `pj_thread_this()` ritorna non-NULL.
   La hypothesis "thread anonimo" del prompt è **falsificata**.
3. La vera root cause `grp_lock_unset_owner_thread` assertion = **cross-thread
   release del group lock**. Probabile chiamante: il thread Python `_audio_thread`
   (`voip_pjsua2.py` riga 484/513) chiama `clear_tx()` / `queue_tts_audio()` /
   `get_caller_audio()` sull'audio_port **mentre il clock thread tiene il lock**, o
   chiama `stopTransmit` / disconnect su un thread diverso da chi ha fatto acquire.
4. **F2 raccomandato**: tenere `setNullDev()` MA (a) pre-registrare in pjlib OGNI thread
   Python che tocca `self.audio_port` (incluso `_audio_thread`), (b) serializzare le
   conf-bridge ops sul thread `_pjsua2_thread` via `libHandleEvents` pending-jobs queue
   o `Endpoint.utilTimerSchedule`, (c) NON chiamare metodi `Media*` su thread Python
   ad-hoc.
5. Se F2 non basta: **F3 — fallback `setNoDev()` + custom master clock manuale**
   (richiede driver Python tick 20ms su `_pjsua2_thread` che chiama get/put_frame
   esplicitamente). Più invasivo, da considerare solo se F2 fallisce.

**Onesta**: la falsificazione del clock-thread anonimo è high-confidence (0.95) — sorgente
verificato. La diagnosi cross-thread Python `_audio_thread` è hypothesis (0.70) basata su
lettura del codice: non ho accesso al traceback completo S237-F1-bis che mostra lo stack
frame del thread che fa abort. **Prima cosa da fare in S238**: leggere il SIGABRT
backtrace LLDB/console per identificare quale thread ha chiamato release.

---

## 1. Decode `setNullDev()` vs `setNoDev()` — evidenza diretta

### setNullDev (raccomandato)
File: `pjsua2.py` L6305-L6311 (wrapper docstring) + `pjsua_aud.c:2374-2434`.

```python
# pjsua2.py L6307-L6310
def setNullDev(self):
    """Set pjsua to use null sound device. The null sound device only provides
    the timing needed by the conference bridge, and will not interract with
    any hardware."""
    return _pjsua2.AudDevManager_setNullDev(self)
```

Implementazione C (`pjsua_aud.c:2374`):
```c
PJ_DEF(pj_status_t) pjsua_set_null_snd_dev(void) {
    ...
    /* Get the port0 of the conference bridge. */
    conf_port = pjmedia_conf_get_master_port(pjsua_var.mconf);   // L2408
    ...
    /* Create master port, connecting port0 of the conference bridge to
     * a null port. */
    status = pjmedia_master_port_create(pjsua_var.snd_pool, pjsua_var.null_port,
                                        conf_port, 0, &pjsua_var.null_snd);   // L2414
    ...
    /* Start the master port */
    status = pjmedia_master_port_start(pjsua_var.null_snd);   // L2425
}
```

`pjmedia_master_port_start` → `pjmedia_clock_start` (`master_port.c:137`)
→ `pj_thread_create(clock->pool, "clock", &clock_thread, clock, ...)`
(`clock_thread.c:231`). **`pj_thread_create` è una pjlib API** che alloca un
`pj_thread_desc` e registra il TLS slot. Il thread risultante NON è anonimo:
`pj_thread_this()` ritorna il `pj_thread_t*` corretto.

### setNoDev (NON raccomandato per Sara)
`pjsua2.py` L6313-L6323:
```python
def setNoDev(self):
    """Disconnect the main conference bridge from any sound devices, and let
    application connect the bridge to it's own sound device/master port.
    
    :return: The port interface of the conference bridge,
             so that application can connect this to it's
             own sound device or master port."""
    return _pjsua2.AudDevManager_setNoDev(self)
```

**Punto critico**: `setNoDev` ritorna il port0 ma NON installa nulla. Tocca all'app
piazzare un master clock. Per Sara questo significherebbe scrivere un master port
Python (extra work + extra threading sync). **Non scegliere setNoDev** salvo come
fallback F3.

### Cosa tickaa il conf bridge sotto `setNullDev`
`null_port.c` (L80-L100): `null_put_frame` scarta il frame, `null_get_frame` ritorna
silenzio. Il clock thread chiama master_port_proc che chiama get_frame del DOWNSTREAM
port (conf bridge port0). Conf bridge port0 `get_frame` aggrega tutti gli upstream
`get_frame_pasv` (incluso `SaraAudioPort.onFrameRequested`) e invia il mixdown al
null port (scartato). Speculare per put_frame in direzione opposta.

**Conclusione setNullDev vs setNoDev**: `setNullDev` è l'API corretta per server SIP
headless. Confermato anche dal sample upstream `pjsua2_demo.cpp:395`:
```cpp
ep.libStart();
ep.audDevManager().setNullDev();
```

---

## 2. Clock master selection in `pjmedia_conf_create`

Il conf bridge ha sempre un port0 (master port) creato in
`pjmedia_conf_create` (`conference.c:822`):
```c
conf->master_port->get_frame = &get_frame;
conf->master_port->put_frame = &put_frame;
```

Il port0 **non è** ciò che tickaa il clock. Il tick viene da chi connette qualcosa al
port0:
- **`pjmedia_master_port`** (creato da setNullDev/snd_dev/extra_audio) → clock interno
  (`pjmedia_clock` thread).
- **app custom** → app driver loop.

Domanda specifica del prompt: "esiste `PJMEDIA_CONF_NO_DEVICE`?" → **non trovato** nel
sorgente. La selezione del clock master è implicita: chi chiama
`pjmedia_master_port_create(null_port, conf->master_port, ...)` diventa il driver.

Domanda: "si può forzare `SaraAudioPort` a essere clock master?" → **No, non direttamente**:
`AudioMediaPort.createPort` registra il port come passive port nel conf bridge
(`pjsua_conf_add_port` → `pjmedia_conf_add_passive_port` interno). I passive port
sono pull-based; non possono essere master.

**Workaround possibile (NON raccomandato S238)**: usare `pjmedia_master_port` direct
binding via SWIG per legare conf->master_port a un custom `pjmedia_port` controllato
da driver Python tick. Equivale a F3. Invasivo.

---

## 3. Root cause `grp_lock_unset_owner_thread` assertion

### File `pjlib/src/pj/lock.c:259-286`

```c
static void grp_lock_set_owner_thread(pj_grp_lock_t *glock) {
    if (!glock->owner) {
        glock->owner = pj_thread_this();    // L263 - chi entra primo
        glock->owner_cnt = 1;
    } else {
        pj_assert(glock->owner == pj_thread_this());   // L270 - reentrant check
        glock->owner_cnt++;
    }
}

static void grp_lock_unset_owner_thread(pj_grp_lock_t *glock) {
    pj_assert(glock->owner == pj_thread_this());    // L279 ⟵ TUO SIGABRT
    pj_assert(glock->owner_cnt > 0);                // L281
    if (--glock->owner_cnt <= 0) {
        glock->owner = NULL;
        glock->owner_cnt = 0;
    }
}
```

L'assertion alla L279 scatta se: `release` (`grp_lock_release` → `unset_owner_thread`)
è chiamato da un thread **diverso** da quello che ha fatto `acquire`
(`grp_lock_acquire` → `set_owner_thread`).

### Quando può accadere in Sara

Three scenari plausibili:

#### Scenario A — `_audio_thread` Python tocca port mentre clock-thread tiene lock
Da `voip_pjsua2.py` osservo che dopo `onCallState == CONFIRMED`, viene avviato un
thread Python ad-hoc:
```python
# L274
threading.Thread(target=self.on_connected, args=(self,), daemon=True).start()
```
Questo thread (chiamiamolo T_audio) chiama metodi sul pipeline che probabilmente
toccano `self.audio_port.queue_tts_audio(...)`, `clear_tx()`, ecc. Questi metodi
operano sulla `tx_queue` Python (thread-safe), MA possono triggerare indirettamente
chiamate a `stopTransmit`/`startTransmit`/`getPortInfo` via attributi `Media*` SWIG.
**T_audio NON è registrato in pjlib** (registrazione fatta solo nei frame callbacks
F1-bis). Se T_audio chiama una pjsua2 API che fa `pj_grp_lock_release` su un lock
che è stato acquistato dal clock-thread (o dal `_pjsua2_thread`), → mismatch → abort.

**Fix F2-A**: pre-registrare T_audio in pjlib all'inizio della callback
`on_connected`. Idempotente:
```python
def on_connected_wrapper(call):
    try:
        pj.Endpoint.instance().libRegisterThread("sara_audio_processor")
    except pj.Error:
        pass  # already registered
    real_on_connected(call)
```

#### Scenario B — disconnect on hangup cross-thread
`onCallState == DISCONNECTED` parte un altro thread daemon (L278). Se quel thread
tocca `audio_port` (es. cleanup, dec_ref via Python GC) → cross-thread release.

**Fix F2-B**: anche `on_disconnected` deve essere registrato.

#### Scenario C — Python GC dealloca `SaraAudioPort` su thread garbage collector
Quando `SaraCall` viene rilasciato (fine chiamata), il `__del__` della SWIG director
chiama `pjsua_conf_remove_port` → `pj_grp_lock_dec_ref` → eventualmente
`conf_port_on_destroy` → `pj_grp_lock_destroy`. Il GC thread non è registrato in
pjlib.

**Fix F2-C**: tenere `self.audio_port` con strong ref nel `SaraAccount` (e fare
cleanup esplicito su pjsua2 thread via `libHandleEvents` pending-jobs scheduler).

### Verifica empirica necessaria (S238 prima del fix)

Aggiungere al traceback handler una `faulthandler` Python prima di startTransmit per
catturare lo stack frame del thread che esegue release. Senza questo, l'identità
del thread colpevole rimane hypothesis.

```python
# In voip_pjsua2.py prima del _init_pjsua2 init
import faulthandler
faulthandler.enable(file=sys.stderr, all_threads=True)
```

Questo NON evita il SIGABRT ma stampa il backtrace di TUTTI i thread Python al
momento dell'abort. Sapere chi è il thread colpevole è prerequisito per fix mirato.

---

## 4. Snippet F2 prototype proposto

Sostituire `voip_pjsua2.py` L613-L624 con:

```python
# Start library
self._ep.libStart()
logger.info(f"pjsua2 started on port {self.config.local_port}")

# S237 FIX F1: install null audio device (provides conf bridge clock).
# CONFIRMED upstream pattern: pjsua2_demo.cpp:395 calls setNullDev() right
# after libStart() for the same reason — headless agent, no local mic/spk.
try:
    self._ep.audDevManager().setNullDev()
    logger.info("pjsua2: null audio device installed (headless mode, S237 F1)")
except pj.Error as exc:
    logger.error(f"S237: setNullDev failed | {_pj_error_info(exc)}")
    raise

# S238 FIX F2: enable faulthandler for cross-thread abort diagnostics.
# When grp_lock_unset_owner_thread assertion fires (lock.c:279), we need
# stack frames of ALL Python threads to identify the culprit thread doing
# the cross-thread release. Without this, abort produces only the assertion
# message + clock thread frame (useless).
import faulthandler
if not faulthandler.is_enabled():
    faulthandler.enable(file=sys.stderr, all_threads=True)
```

E in `SaraCall.onCallState` (riga 263-278) aggiungere wrapper di registrazione:

```python
def onCallState(self, prm):
    ci = self.getInfo()
    state = ci.state
    logger.info(f"Call state: {ci.stateText} (state={state})")

    if state == pj.PJSIP_INV_STATE_CONFIRMED:
        self.connected = True
        if self.on_connected:
            # S238 FIX F2: wrap on_connected to register the spawned Python
            # thread with pjlib BEFORE it touches any pjsua2 object. Required
            # because the audio processor thread reaches self.audio_port via
            # SWIG director proxies, and any pjsua2 internal grp_lock release
            # from a non-registered thread → lock.c:279 SIGABRT.
            ep_inst = pj.Endpoint.instance()
            outer_cb = self.on_connected
            def _registered_cb(call):
                try:
                    ep_inst.libRegisterThread("sara_audio_processor")
                except pj.Error:
                    pass  # already registered, idempotent
                outer_cb(call)
            threading.Thread(target=_registered_cb, args=(self,), daemon=True).start()

    elif state == pj.PJSIP_INV_STATE_DISCONNECTED:
        self.connected = False
        if self.on_disconnected:
            ep_inst = pj.Endpoint.instance()
            outer_cb = self.on_disconnected
            def _registered_cb(call):
                try:
                    ep_inst.libRegisterThread("sara_disconnect_handler")
                except pj.Error:
                    pass
                outer_cb(call)
            threading.Thread(target=_registered_cb, args=(self,), daemon=True).start()
```

**E nel codice del pipeline** (qualsiasi thread Python che riceve l'audio dal port e
chiama back per TTS): se quel pipeline usa un proprio thread pool, ciascuno DEVE
essere registrato la prima volta. Cercare nell'orchestratore di Sara dove vengono
spawnati i thread di `tts.synthesize` → `audio_port.queue_tts_audio` e aggiungere
`libRegisterThread` lì come pattern permanente.

---

## 5. Risk assessment (onesto, dove F2 può fallire)

| Risk | Probabilità | Mitigation |
|------|------------|------------|
| L'assertion arriva da Python GC thread (Scenario C) — non da T_audio | medio (0.30) | F2 non basta. Serve esplicito `self.audio_port = None` su pjsua2 thread + tenere strong ref in SaraAccount per durata pjsua2 lib. |
| Registrazione non idempotente: chiamate ripetute leak memory pjsua_pool | basso (0.10) | Docstring API: "each time this function is called, it will allocate some memory". Usare `libIsThreadRegistered()` check prima di registrare. |
| Pipeline Sara ha N thread pool worker dinamici — registrare tutti è viral | medio (0.40) | Decorator/context manager: `@with_pjlib_thread` applicato ai metodi che toccano `audio_port`. |
| `setNullDev` master_port_create fallisce per altro motivo (non headless) | basso (0.05) | Già coperto da try/except S237 F1. |
| Frame callback `onFrameRequested` chiamato dal clock thread MA `_ensure_thread_registered` non basta perché il lock viene preso/rilasciato in C code attorno al callback | basso (0.15) | Inspeziona conference.c get_frame path — non ho trovato grp_lock_acquire/release nel path get_frame (solo add_ref/dec_ref). |

### Probabilità che F2 risolva: ~0.70
Stima onesta. Senza il backtrace di S237-F1-bis SIGABRT (non in mio possesso) non
posso essere più specifico. La hypothesis dominante (T_audio non registrato) è quella
con la spiegazione più lineare del sintomo "assertion fires PRIMA delle frame
callback": prima frame callback = 20ms dopo bridge established, ma T_audio parte
**immediatamente** quando state diventa CONFIRMED (prima dell'audio bridge anche).

---

## 6. F3 fallback outline (se F2 non basta)

Se F2 viene applicato e l'assertion persiste:

1. **Strumentare l'abort** con `faulthandler.dump_traceback_later` + monitoring del
   thread che chiama release. Se è il clock thread o il pjsua2 thread → bug pjsua2
   stesso (irrealistico, upstream sample funziona).

2. **F3-Alt — switch a `setNoDev()` + driver Python**:
   ```python
   # Replace setNullDev with:
   master_port = self._ep.audDevManager().setNoDev()
   # master_port is a Media that bridges conf master port0
   # Drive it manually from _pjsua2_thread:
   while not self._pj_stop.is_set():
       self._ep.libHandleEvents(20)
       # Manual tick: pull frame from master_port (drives the bridge)
       # ... need SWIG access to pjmedia_port_get_frame
   ```
   **Non viable senza ctypes**: `setNoDev` ritorna `void` nel wrapper Python (L6313),
   non un port handle. Servirebbe modifica wrapper + accesso C diretto.

3. **F3 — bypass pjsua2 audio bridge, usare AudioMediaPlayer/Recorder**:
   - `AudioMediaPlayer.createPlayer(file)` legge WAV da disco → conf bridge.
   - Per real-time TTS streaming: scrivere WAV chunks su tmpfs e ricreare player ad
     ogni utterance. Latenza extra ~50-100ms per chunk + disk I/O.
   - Per caller audio → STT: `AudioMediaRecorder.createRecorder(file)` registra WAV
     da conf bridge; poll file da Python thread.
   - **Risk**: latency real-time bridge degrada, perdi barge-in (S142).

**Raccomandazione**: F3 è ultimo resort. Prima esaurire F2 + diagnostica
faulthandler.

---

## 7. Riferimenti (file:linea, master branch verificato 2026-05-15)

Upstream pjproject (GitHub raw):
- `pjsip/src/pjsua-lib/pjsua_aud.c:2374-2434` (`pjsua_set_null_snd_dev`)
- `pjsip/src/pjsua-lib/pjsua_aud.c:1085` (sound device implicit open trigger — S237 F1)
- `pjmedia/src/pjmedia/master_port.c:114` (`pjmedia_master_port_create` → `pjmedia_clock_create`)
- `pjmedia/src/pjmedia/master_port.c:132-137` (`pjmedia_master_port_start` → `pjmedia_clock_start`)
- `pjmedia/src/pjmedia/clock_thread.c:231` (`pj_thread_create("clock", clock_thread)` — pjlib-registered)
- `pjmedia/src/pjmedia/conference.c:438` (`pj_grp_lock_add_ref` on port add)
- `pjmedia/src/pjmedia/conference.c:822` (master port get/put_frame setup)
- `pjmedia/src/pjmedia/null_port.c:80-100` (null_put_frame, null_get_frame)
- `pjlib/src/pj/lock.c:259-286` (grp_lock_set_owner_thread / unset_owner_thread — **assertion site**)
- `pjsip-apps/src/samples/pjsua2_demo.cpp:387-395` (canonical setNullDev usage post libStart)

Local:
- `voice-agent/lib/pjsua2/pjsua2.py:6305-6311` (setNullDev SWIG wrapper + docstring)
- `voice-agent/lib/pjsua2/pjsua2.py:6313-6323` (setNoDev SWIG wrapper + docstring — note "let application connect")
- `voice-agent/lib/pjsua2/pjsua2.py:13720-13738` (libRegisterThread + libIsThreadRegistered)
- `voice-agent/lib/pjsua2/pjsua2.py:6893-6938` (ExtraAudioDevice — alternative for hybrid setups)
- `voice-agent/src/voip_pjsua2.py:633-648` (current libStart + setNullDev call — S237 F1 landed)
- `voice-agent/src/voip_pjsua2.py:120-131` (_ensure_thread_registered helper — F1-bis insufficient)
- `voice-agent/src/voip_pjsua2.py:263-278` (onCallState spawning unregistered Python threads — **F2 target**)

Precedente:
- `.claude/cache/agents/s237/pjmedia-vs-pjsua-bridge-namespace.md` (S237 verdict, contesto)
