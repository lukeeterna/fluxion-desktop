# Prompt diagnostico Claude.ai — Sara VoIP Bug — Sessione S244 con SMOKING GUN preciso

**Contesto**: sono Gianluca, founder FLUXION. Sto debuggando `grp_lock_unset_owner_thread` SIGABRT in pjsip 2.16-dev su macOS 11 Big Sur (iMac 2012 Intel x86_64) da 12 sessioni (S232-S244). Patch S243 (T0+T1+T1.5+T2 che hai prodotto) tecnicamente funzionava (`bridge wiring enqueued` confermato) ma falsificata dal timing — il crash è UPSTREAM di `startTransmit`.

S244: ho applicato la tua raccomandazione **Opzione 2** (logConfig.level=5 + decor=0xFFFF + stderr dup2 per catturare eventi pjmedia pre-crash). **Test live appena eseguito → bug riprodotto con smoking gun preciso**. Allego sotto.

---

## SMOKING GUN S244 — sequenza C-side completa pre-crash

Repository file completo: 546 righe in `.claude/cache/agents/s244/sara-pjsip-s244.log`. Estratto cronologico **chiave** delle ultime righe pre-SIGABRT (timestamp microsecondi + thread name visibili grazie a decor=0xFFFF):

```
TRACE  19:33:06.308  strm0x7f8564a59a28  pjsua_0       .....Stream strm0x7f8564a59a28 created
DEBUG  19:33:06.308  strm0x7f8564a59a28  pjsua_0       .....Encoder stream started
DEBUG  19:33:06.308  strm0x7f8564a59a28  pjsua_0       .....Decoder stream started
TRACE  19:33:06.309  resample.c          pjsua_0       ......resample created: high quality, in/out rate=8000/16000
TRACE  19:33:06.309  resample.c          pjsua_0       ......resample created: high quality, in/out rate=16000/8000
DEBUG  19:33:06.309  conference.c        pjsua_0       ......Add port 1 (sip:3281536308@79.98.45.133) queued
DEBUG  19:33:06.309  pjsua_media.c       pjsua_0       ....audio updated, stream #0: PCMA (sendrecv)
DEBUG  19:33:06.309  os_core_unix.c      pjsua_0       ...Info: possibly re-registering existing thread
TRACE  19:33:06.311  resample.c          onCallMediaS  !....resample created: high quality, in/out rate=8000/16000
TRACE  19:33:06.311  resample.c          onCallMediaS   ....resample created: high quality, in/out rate=16000/8000
DEBUG  19:33:06.311  conference.c        onCallMediaS   ....Add port 2 (sara_bridge) queued
INFO   19:33:06       src.voip_pjsua2     —             S236 DIAG H2: audio_port refcount=2 _port_created=True
INFO   19:33:06       src.voip_pjsua2     —             S236 DIAG H3: call.format=sara.format (8kHz mono L16 match)
INFO   19:33:06       src.voip_pjsua2     —             S243 T1: bridge wiring enqueued (media_idx=0, queue_depth=1)
*** Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279 ***
Fatal Python error: Aborted

Thread 0x0000700011d7e000 (_pjsua2_thread, most recent first):
  pjsua2.py:13767 in libHandleEvents
  voip_pjsua2.py:806 in _pjsua2_thread

Thread 0x000000011575f600 (main asyncio):
  selectors.py:562 in select
  base_events.py:1854 in _run_once
```

## Tre osservazioni che cambiano la diagnosi

### Osservazione 1 — DUE thread diversi operano sul conference bridge nello stesso instant

Decor `0xFFFF` mostra il thread name nel log pjsip:
- `pjsua_0` (worker thread interno spawnato da `threadCnt=1`) aggiunge **port 1** (call leg) tra `19:33:06.308` e `.309`
- `onCallMediaS` (= `onCallMediaState` Python callback eseguito su `_pjsua2_thread`) aggiunge **port 2** (sara_bridge) a `19:33:06.311`

I due add operano sullo stesso `pjmedia_conf` global. Pattern classico cross-thread race su group lock.

### Osservazione 2 — "possibly re-registering existing thread" è ESPLICITO

Linea `19:33:06.309 os_core_unix.c pjsua_0 ...Info: possibly re-registering existing thread` arriva **prima** del callback `onCallMediaState`. Pjsua sta detectando che lo stesso thread Python ha già `pj_thread_register` flag attivo, e re-registra causando ownership ambiguità sul thread descriptor → grp_lock owner check fallisce dopo.

Questo è il messaggio C di `os_core_unix.c:registry_thread()`. Indica che la sequenza F1-bis/F3 (registrazione TPE pjlib-aware) e il worker pjsua_0 stanno entrambi tentando di registrare lo stesso thread Python = mismatch.

### Osservazione 3 — "Add port N (...) queued" — semantica 2.16-dev

In pjsip 2.15.1 stable la operazione era sincrona, log sarebbe stato `Conf add port N` immediato. In 2.16-dev è `queued`, processata in batch durante successive libHandleEvents tick. Il **queue processing è dove l'assertion scatta**.

Questa è la **prova testuale che 2.16-dev ha un refactor del conference bridge che 2.15.1 non ha** — coerente con tua hypothesis N4 (regressione dev branch).

## Config corrente voip_pjsua2.py

```python
ep_cfg.uaConfig.threadCnt = 1          # S240 T0 (post-revert S153)
ep_cfg.uaConfig.mainThreadOnly = False # S240 T0
ep_cfg.logConfig.level = 5
ep_cfg.logConfig.consoleLevel = 5
ep_cfg.logConfig.filename = "/tmp/sara-pjsip-s244.log"
ep_cfg.logConfig.decor = 0xFFFF
ep_cfg.medConfig.noVad = True
ep_cfg.medConfig.srtpUse = 0
```

`onCallMediaState` callback (semplificato post-T1+T1.5+T2):
```python
def onCallMediaState(self, prm):
    ep_inst = pj.Endpoint.instance()
    try:
        ep_inst.libRegisterThread("sara_call_handler")  # F1-bis
    except pj.Error:
        pass  # already registered
    ci = self.getInfo()
    for i, mi in enumerate(ci.media):
        if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
            call_audio = self.getAudioMedia(i)            # → C: pjsua_call_get_audio_media → ensures port registered
            self._account.ensure_port()                    # → SaraAudioPort.createPort if not created
            self._account.enqueue_bridge(call_audio, i)    # T1: defer startTransmit
            logger.info(f"S243 T1: bridge wiring enqueued (media_idx={i})")
```

`drain_pending_bridges()` chiamato in `_pjsua2_thread` loop OUTSIDE callback (post-libHandleEvents return).

## Cosa ti chiedo S244 (specifico, niente più ranking generico)

### Domanda A — verifica regressione 2.16-dev (PRIORITY)

Lo smoking gun mostra `"Add port N queued"` invece di sync `"Conf add port N"`. **È documentato un refactor `pjmedia_conf` da sync a queued in 2.16-dev?** Controlla:
- pjsip GitHub commits between 2.15 release e master HEAD su `pjmedia/src/pjmedia/conference.c`
- Issue tracker pjsip per "grp_lock owner conference queued"
- Whether 2.15.1 ha lo stesso codice path

Se confermi: **B1 (downgrade 2.15.1) è il fix corretto**. Già ho runbook completo pre-cooked in `.claude/NEXT_SESSION_PROMPT.manual.md`. Procedo subito.

### Domanda B — workaround Python pre-B1 (alternativa B1 se troppo costoso)

Considerato il smoking gun:
- pjsua worker `pjsua_0` aggiunge port 1 PRIMA che `onCallMediaState` venga dispatched
- onCallMediaState (su _pjsua2_thread) aggiunge port 2
- Group lock conference owned by pjsua_0, release by _pjsua2_thread → mismatch

Ipotesi workaround: **eliminare il worker pjsua_0 settando threadCnt=0** (S153 originale, reverted S240 perché causava un altro bug). Se lo rimettiamo:
- threadCnt=0 + mainThreadOnly=True → tutto su _pjsua2_thread → no cross-thread su grp_lock conference
- MA: la deviation S232-S239 (pjmedia event dispatch su _pjsua2_thread mentre pjmedia clock thread invisible C-only fa work) ricomparirebbe

**Però adesso ho F1-bis/F2/F3/F1-S237/T1/T1.5/T2 tutti in place**. Forse threadCnt=0+mainThreadOnly=True + tutti i layer defensive funziona ora dove S153 non funzionava? Vale la pena testarlo (10 min, 2 line change, zero rischio rollback)?

Tua opinione: **conviene un test "threadCnt=0 retry con tutti i defensive layer attivi" PRIMA di B1 downgrade 2h?**

### Domanda C — interpretazione "possibly re-registering existing thread"

Questo messaggio è documentato in pjlib `os_core_unix.c`. Trigger esatto: secondo `pj_thread_register()` chiamato su thread che ha già `pj_thread_local_get(thread_tls_id)` non-null.

Possibili cause:
1. F1-bis `libRegisterThread` in `onCallMediaState` + pjsua worker stesso thread = double register
2. F3 pjlib-aware TPE initializer + pjsua dispatch sullo stesso TPE worker
3. Glitch SWIG: `Endpoint.instance().libRegisterThread()` non idempotent

**Suggerimento Python**: posso usare ctypes per chiamare direttamente `pj_thread_local_get(thread_tls_id)` e verificare se già registrato prima di chiamare `libRegisterThread`?

### Domanda D — se B1 fallisce (toolchain Big Sur), B2 Asterisk ARI

Già ho skeleton non-cooked. Domanda secca: **Asterisk Docker su Big Sur Intel funziona out-of-the-box senza AVX2?** (iMac 2012, no AVX2 — ho già verificato che alcuni Docker image richiedono CPU recente).

Container raccomandato (se hai dati): `andrius/asterisk:latest` o `asterisk:18-alpine` o custom build?

## Vincoli sessione (ricorda)

- Zero-cost (#5 CLAUDE.md): no servizi paid
- iMac 2012 Intel macOS 11 Big Sur, no AVX2, no OS upgrade
- MacBook dev: no Rust/C build
- 0 clienti paganti — Sara bug è blocker hard pre-launch
- Anti-pattern S159: NO switch architetturale fine sessione esausta
- CTO ownership: decido io P0/P1/P2 senza founder review

## Output che mi serve da te

1. **Conferma/falsifica regressione 2.16-dev** su conference.c con commit hash o issue link
2. **Verdetto A vs B vs C vs D ordine**: cosa testo per primo, secondo, terzo
3. Se B (threadCnt=0 retry): patch surgical voip_pjsua2.py con commenti motivati
4. Se C workaround: ctypes pattern per check thread already registered
5. Se D: container Asterisk specifico tested macOS 11 Intel no-AVX2

Formato: ranking + raccomandazione operativa singola motivata. Eviterei nuovamente 4 opzioni se la diagnosi è ora cristallina.

## File contesto disponibili (se ti servono)

- `voice-agent/src/voip_pjsua2.py` (post-S244 patch, 821 righe — posso allegarne sezioni)
- `voice-agent/lib/pjsua2/pjsua2.py` SWIG bindings (50K righe)
- `.claude/cache/agents/s244/sara-pjsip-s244.log` (546 righe smoking gun completo — posso allegare full)
- `.claude/cache/agents/s238/pjsua2-clock-master-pattern.md` (388 righe research)
- `DOSSIER-SARA-VOIP-BUG.md` (603 righe storia bug)
