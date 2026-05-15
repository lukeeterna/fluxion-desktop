# S238 — Faulthandler analysis (smoking gun thread identity)

> Closed ORANGE 2026-05-15 ~16:10. Test live founder 16:05:49 da 3281536308 → Vodafone "telefono spento" → pipeline crashata SIGABRT.

## Key evidence

Log: `.claude/cache/agents/s238/live-test-log-full.txt` (142 righe).

Sequenza critica L107-115:
```
16:05:49 Incoming call from: <sip:3281536308@79.98.45.133>
16:05:49 Answering call with 200 OK (direct — S153 fix)
16:05:49 S236 DIAG H1: call_audio=AudioMedia mro=[AudioMedia,Media,object] | audio_port=SaraAudioPort mro=[SaraAudioPort,AudioMediaPort,AudioMedia,Media,object]
16:05:49 S236 DIAG H2: audio_port id=4592637168 refcount=2 _port_created=True
16:05:49 S236 DIAG H3: call.format clockRate=8000 ch=1 bits=16 frameUsec=20000 | sara.format ≡ identical
16:05:49 Audio bridge established: call(slot=1) ↔ Sara(slot=2) after 0ms  ← startTransmit SUCCESS (F1)
Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.
```

## Faulthandler dump (l'evidence che mancava in S237)

```
Fatal Python error: Aborted

Current thread 0x0000700010774000 (most recent call first):
  File "lib/pjsua2/pjsua2.py", line 13767 in libHandleEvents
  File "src/voip_pjsua2.py", line 631 in _pjsua2_thread             ← thread che ABORTA

Thread 0x000070000f771000 (most recent call first):
  File "python3.9/concurrent/futures/thread.py", line 75 in _worker  ← TPE worker #1
Thread 0x000070000e76e000 (most recent call first):
  File "python3.9/concurrent/futures/thread.py", line 75 in _worker  ← TPE worker #2
```

## Verdict S238 — F2 hypothesis FALSIFIED

F2 (registrare i thread spawn di `on_connected`/`on_disconnected`) era basato sull'hypothesis che il colpevole fosse il "sara_audio_processor" thread Python custom. **FALSIFICATO dal backtrace**:

1. Il thread che fa abort è `_pjsua2_thread` dentro `libHandleEvents`. Quello È registrato in pjlib (l'abbiamo creato noi con `libRegisterThread` o pjsua2 lo fa internalmente).
2. I thread Python custom (`sara_audio_processor`) NON appaiono nel dump. O non erano ancora partiti (assertion fires PRIMA di `on_connected`, all'establish del bridge), o sono già morti.
3. Compaiono 2 `_worker` thread di `concurrent.futures.thread.ThreadPoolExecutor` — questi sono il VERO sospetto: probabili pool workers di Sara pipeline (TTS, STT, async tasks) che NON sono registrati con pjlib.

## Nuova hypothesis dominante S239

**Cross-thread release** = un `_worker` thread Python (TPE) ha chiamato un metodo pjsua2 (es. via TTS pre-warm chunks, audio processing) che ha acquisito `pj_grp_lock` C-side internamente. Poi `_pjsua2_thread` (registrato) ha tentato il release dentro `libHandleEvents` → mismatch `owner != self` → assertion → SIGABRT.

Worker non registrato sospetto NON è `on_connected` thread (F2 target) ma `concurrent.futures.ThreadPoolExecutor._worker`. Candidati nel codice Sara:
- TTS pool (Edge-TTS/Piper async chunks)
- Orchestrator pool (L1-L4 RAG layer parallel)
- aiohttp executor default

## Plan S239 (NON eseguire ora — closing context)

### Step 1 — Audit TPE worker spawn sites
```bash
grep -rn "ThreadPoolExecutor\|run_in_executor\|asyncio.to_thread" voice-agent/src/
```
Mappare ogni TPE e identificare quale tocca direttamente o indirettamente `audio_port` / `pjsua2 objects`.

### Step 2 — Due strategie alternative
**A) Defensive (light)**: aggiungere `libRegisterThread` come `initializer=` di ogni `ThreadPoolExecutor` che può toccare pjsua2. Pattern:
```python
def _pjlib_init():
    try:
        pj.Endpoint.instance().libRegisterThread(f"sara_tpe_{threading.get_ident()}")
    except Exception:
        pass
pool = ThreadPoolExecutor(max_workers=N, initializer=_pjlib_init)
```

**B) Architectural (heavy)**: serializzare TUTTE le interazioni con audio_port attraverso `_pjsua2_thread` via pending-jobs queue (consigliato dal subagent S238 punto F2-b). Pattern:
- TTS termina → push bytes in `self._pending_tts_queue` (thread-safe Python queue)
- `_pjsua2_thread` loop drena la queue ogni libHandleEvents tick → chiama `audio_port.queue_tts_audio()` dal proprio thread
- Garantisce **single-threaded** access a tutti gli SWIG director objects

Raccomandazione: **B** è cleaner (pattern raccomandato pjsua2). **A** è minimo blast radius per validazione rapida. Iniziare con A su test live, poi refactor in B se ok.

### Step 3 — Test live discriminate
Founder chiama 0972536918 → senti greeting entro 3s = GREEN. Se SIGABRT residuo, faulthandler dump dirà se è ancora TPE worker o altro.

## Risk assessment onesto S239

| Risk | Prob | Mitigation |
|------|------|------------|
| Strategia A non basta perché esistono N TPE in code paths non audit-ati (es. asyncio default pool, requests sessione, httpx pool) | 0.40 | Loggare `threading.enumerate()` in `on_connected` per inventario completo prima del fix |
| Strategia B richiede refactor non triviale (cambia API queue_tts_audio in async) | 0.60 | Acceptable cost se A non risolve. ~1 sessione dedicata |
| Esiste ancora un 3° thread non registrato (Python GC, asyncio loop) e A+B non lo coprono | 0.20 | faulthandler residuo lo rivelerà |
| pjsua2 stesso ha race condition tra `libHandleEvents` e `pjsua_conf_connect` (improbabile, upstream è production-grade) | 0.05 | Last resort: switch engine (F5 S237 plan) |

## Mantenere in master (S238)

- `voice-agent/src/voip_pjsua2.py` F2 wrap `_run_with_pjlib_registration` su on_connected/on_disconnected: **mantenere** (defensive, zero overhead, sicuro)
- `faulthandler.enable(all_threads=True)`: **mantenere** (sarà strumento diagnostico continuo per S239+)
- F1 setNullDev + F1-bis _ensure_thread_registered: **mantenere** (entrambi corretti)

Nessun fix da revertare. F2 era hypothesis ragionevole ex-ante, falsified post-facto. È progresso strumentale (faulthandler ora cattura sempre).
