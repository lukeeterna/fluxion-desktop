# S239 — Prompt ripartenza (handoff S238 → S239)

**Generato**: 2026-05-15 ~16:10 (chiusura S238 ORANGE — F2 hypothesis falsificata, faulthandler ha rivelato veri sospetti)
**Branch**: master @ `7e68045` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED clean (DOWN_OK)

## TL;DR S238 outcome

- ✅ **F2 fix landed** (commit `7e68045`): `_run_with_pjlib_registration` helper wrappa thread daemon di `SaraCall.onCallState` su CONFIRMED/DISCONNECTED, registra con pjlib prima di invocare `on_connected`/`on_disconnected`.
- ✅ **faulthandler.enable(all_threads=True)** abilitato in `voip_pjsua2.py` early → strumento diagnostico continuo per identificare thread non registrati su SIGABRT.
- ❌ **F2 hypothesis FALSIFICATA** dal test live: pipeline ancora crasha, ma il backtrace mostra che il thread che fa abort è `_pjsua2_thread` (registrato), NON i thread Python custom di on_connected (che F2 stava registrando inutilmente).
- 🎯 **VERI SOSPETTI emersi dal faulthandler dump**: 2 thread `concurrent.futures.thread._worker` (ThreadPoolExecutor di Sara pipeline) non registrati con pjlib.

## Smoking gun S238 (`.claude/cache/agents/s238/live-test-log-full.txt` L115-142)

```
16:05:49 Audio bridge established: call(slot=1) ↔ Sara(slot=2) after 0ms
Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.

Fatal Python error: Aborted
Current thread 0x0000700010774000 (most recent call first):
  File "lib/pjsua2/pjsua2.py", line 13767 in libHandleEvents
  File "src/voip_pjsua2.py", line 631 in _pjsua2_thread          ← thread che ABORTA (registrato)

Thread 0x000070000f771000:
  File "python3.9/concurrent/futures/thread.py", line 75 in _worker  ← TPE worker #1 (NON registrato!)
Thread 0x000070000e76e000:
  File "python3.9/concurrent/futures/thread.py", line 75 in _worker  ← TPE worker #2 (NON registrato!)
```

## Root cause analysis aggiornata S239

L'assertion `grp_lock_unset_owner_thread` (lock.c:279) significa cross-thread release: chi fa acquire del lock non è chi fa release.

- `_pjsua2_thread` fa la release dentro `libHandleEvents` → quindi è il release-er.
- L'acquire DEVE essere stato fatto da uno degli altri thread. Gli altri Python thread visibili sono i 2 `concurrent.futures.thread._worker`.
- I TPE workers chiamano metodi pjsua2 (probabilmente indirettamente via `audio_port.queue_tts_audio`, TTS pool tasks, orchestrator async layers) → acquisiscono lock C-side.
- pjsua2/pjlib **richiede** che ogni thread che tocca API pjsua2 sia registrato via `pj_thread_register`. I `_worker` non lo sono.
- Sintomo: `pj_thread_this()` ritorna un valore non-NULL ma diverso da quello settato in `set_owner_thread` (perché TLS slot non allocato correttamente per thread non registrato) → mismatch → assertion.

## Plan S239

### Step 0 — Pre-flight (5 min)
```bash
ssh imac "lsof -ti:3002 || echo DOWN_OK"
git rev-parse HEAD  # deve essere 7e68045 o successivo
```

### Step 1 — Audit ThreadPoolExecutor in Sara pipeline (10 min)
```bash
grep -rn "ThreadPoolExecutor\|run_in_executor\|asyncio.to_thread\|asyncio.get_event_loop" voice-agent/src/ voice-agent/main.py
```
Mappare ogni TPE/executor e identificare i call sites che (direttamente o transitivamente) toccano:
- `audio_port` instances
- `pj.Endpoint` methods
- `pj.Call` methods
- `pj.AudioMedia*` methods
- Qualunque modulo `pjsua2 as pj` API

### Step 2 — Strategia A (light, validazione rapida)

Aggiungere `initializer=` con `libRegisterThread` a OGNI `ThreadPoolExecutor` che può toccare pjsua2:

```python
# Helper module-level (esiste già parziale in voip_pjsua2.py — riusarlo o definire nuovo)
def _pjlib_thread_initializer():
    """ThreadPoolExecutor initializer: register every worker thread with pjlib
    so that pj_grp_lock acquires/releases on SWIG director calls have valid
    owner identity. Required since S238 (faulthandler dump identified TPE
    workers as unregistered cross-thread lock release source)."""
    try:
        import pjsua2 as pj
        pj.Endpoint.instance().libRegisterThread(f"sara_tpe_{threading.get_ident()}")
    except Exception:
        pass  # idempotent: already registered or pj not yet available

# Apply to each ThreadPoolExecutor found in Step 1:
pool = ThreadPoolExecutor(max_workers=N, initializer=_pjlib_thread_initializer)
```

Per `asyncio.to_thread` / default executor: configurare via `loop.set_default_executor(ThreadPoolExecutor(initializer=_pjlib_thread_initializer))` in `main.py`.

### Step 3 — Test live discriminate (5 min)
1. Pipeline restart con `VOIP_LOCAL_PORT=6080`
2. Founder chiama 0972536918, dice "Buongiorno"
3. Discriminatore:
   - ✅ Greeting audible <3s → S239 GREEN
   - ❌ SIGABRT residuo → leggere faulthandler dump:
     - se sparisce TPE worker dal dump e appare altro thread (asyncio loop? Python GC?) → estendere registrazione a quel thread
     - se TPE worker ancora presente → registrazione iniettata non ha effetto, controllare se `initializer` viene chiamato (logger.debug nel init)
     - se faulthandler dump è identico → strategia A insufficient, passare a B

### Step 4 — Strategia B (architectural, se A non basta)

Refactor: serializzare TUTTE le interazioni con oggetti pjsua2 SWIG director attraverso `_pjsua2_thread`.

Pattern pending-jobs queue:
```python
class SaraCall(pj.Call):
    def __init__(self, ...):
        self._pending_pjsua2_ops = queue.Queue()  # thread-safe

    def queue_tts_audio_threadsafe(self, audio_data, src_rate=16000):
        """Public API per thread non-pjsua2: enqueue l'op, _pjsua2_thread la esegue."""
        self._pending_pjsua2_ops.put(("queue_tts_audio", (audio_data, src_rate)))
```

In `_pjsua2_thread` loop:
```python
while not self._stop:
    self._ep.libHandleEvents(20)
    # drain pending ops
    for call in self._active_calls:
        try:
            while True:
                op, args = call._pending_pjsua2_ops.get_nowait()
                getattr(call.audio_port, op)(*args)
        except queue.Empty:
            pass
```

Cambio API breaking: callers TTS devono usare `queue_tts_audio_threadsafe` invece di `queue_tts_audio`. Audit di tutti i call sites (probabile in `voip_pjsua2.py` L1020, L1084 + nei pipeline TTS handler).

**Costo**: ~1 sessione dedicata. Cleaner long-term, pattern raccomandato pjsua2 docs.

## Comando one-liner ripartenza S239

```
Sessione S239 FLUXION. Leggi MEMORY.md "Stato Corrente S238" + .claude/NEXT_SESSION_PROMPT.manual.md + .claude/cache/agents/s238/faulthandler-analysis.md. S238 F2 hypothesis falsificata: faulthandler dump rivela che il vero colpevole NON sono i thread spawn di on_connected (registrati da F2 inutilmente) ma 2 ThreadPoolExecutor _worker non registrati con pjlib. Plan S239: Step 1 audit grep ThreadPoolExecutor in voice-agent/src/ + asyncio.to_thread. Step 2 strategia A iniettare initializer=libRegisterThread su ogni TPE. Step 3 test live. Step 4 strategia B (serializzare via pending-jobs queue) se A fallisce. Mantieni F1+F1-bis+F2+faulthandler (zero overhead, faulthandler è strumento diagnostico continuo).
```

## File modificati S238 (mantenuti in master)

- `voice-agent/src/voip_pjsua2.py`:
  - L17-19 import `faulthandler`
  - L29-35 `faulthandler.enable(all_threads=True)` early
  - L37-58 helper `_run_with_pjlib_registration`
  - L301-323 `SaraCall.onCallState` thread spawn wrappato
- `.claude/cache/agents/s238/pjsua2-clock-master-pattern.md` (research subagent voice-engineer, 388 righe)
- `.claude/cache/agents/s238/faulthandler-analysis.md` (analisi post-test S238)
- `.claude/cache/agents/s238/live-test-log-full.txt` (log iMac salvato 142 righe)

## Cronologia bug onesta (aggiornata)

| Sessione | Stato live SIP | Audio Sara erogato? | Insight chiave |
|----------|----------------|---------------------|----------------|
| S232 | Test text-based 147/0/0 | NO | NON era live SIP |
| S233-S236 | startTransmit fail | NO | Vari workaround, status=506784 isolato |
| S237 | F1 setNullDev → startTransmit SUCCESS 0ms | NO | Nuovo blocker assertion lock |
| S238 | F2 register on_connected threads, faulthandler reveal | NO | **F2 falsified, TPE workers veri sospetti** |

Pipeline FLUXION non ha **mai** erogato audio Sara in produzione SIP live. F1+F2+faulthandler sono progresso strumentale ma il bug rimane aperto. S239 è il primo plan con evidence specifica del thread colpevole (TPE worker).
