# Prompt diagnostico Claude.ai — Sara VoIP Bug post-S243

**Contesto**: sono Gianluca, founder FLUXION (gestionale desktop PMI italiane + Voice Agent AI "Sara"). Sto debuggando un bug `grp_lock_unset_owner_thread` SIGABRT in pjsip 2.16-dev su macOS Big Sur (iMac 2012 Intel x86_64). Ho già fatto 9 fix S232-S243 senza risolvere. La tua patch S243 (T1 defer startTransmit + T1.5 remove blocking poll + T2 refcount hardening) è stata applicata e testata live ma **FALSIFICATA con timing diverso**.

## Stato post-S243

**Repo MacBook+iMac sync**: commit `161ecef` master
**File patchato**: `voice-agent/src/voip_pjsua2.py` (cambi T1+T1.5+T2 applicati surgicalmente via Edit tool perché hunk counts patch erano malformati — contenuto patch identico al tuo output, 8 sezioni discrete)

**Test live S243**: chiamata da 3281536308 → 0972536918, esito "Vodafone telefono spento o non raggiungibile" lato chiamante.

## Smoking gun S243 (log iMac `/tmp/sara-live-s243.log`)

```
18:36:24 pjsua2 started on port 6080
18:36:24 pjsua2: null audio device installed (headless mode, S237 F1)
18:36:24 S239 F3: asyncio default executor replaced with pjlib-registered TPE
18:36:24 Registration: active=True, status=200 OK
18:36:24 SIP REGISTERED successfully
18:36:27 VoIP started: 0972536918@sip.vivavox.it

18:40:31 Incoming call from: <sip:3281536308@79.98.45.133>
18:40:31 Answering call with 200 OK (direct — S153 fix)
18:40:31 S236 DIAG H1: call_audio=AudioMedia mro=[AudioMedia,Media,object] | audio_port=SaraAudioPort mro=[SaraAudioPort,AudioMediaPort,AudioMedia,Media,object]
18:40:31 S236 DIAG H2: audio_port id=4450150144 refcount=2 _port_created=True
18:40:31 S236 DIAG H3: call.format clockRate=8000 ch=1 bits=16 frameUsec=20000 | sara.format clockRate=8000 ch=1 bits=16 frameUsec=20000
18:40:31 S243 T1: bridge wiring enqueued (media_idx=0, queue_depth=1)

Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.
Fatal Python error: Aborted

Thread 0x0000700015b85000 (most recent call first):
  File "/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/pjsua2.py", line 13767 in libHandleEvents
  File "/Volumes/MacSSD - Dati/FLUXION/voice-agent/src/voip_pjsua2.py", line 793 in _pjsua2_thread
```

## Cosa è cambiato vs S242

| | S242 (T0 solo) | S243 (T0+T1+T1.5+T2) |
|---|---|---|
| Crash | DOPO `startTransmit` ("Audio bridge established 0ms" → SIGABRT) | PRIMA di drain_pending_bridges (subito dopo "bridge wiring enqueued") |
| Faulthandler | `_pjsua2_thread` + main asyncio | SOLO `_pjsua2_thread` (asyncio dormiente) |
| Drain log "Audio bridge established (deferred)" | N/A | **MAI raggiunto** |
| `S243 T1: bridge slot not assigned` | N/A | **MAI raggiunto** (drain neanche chiamato 1x) |

## Implicazione critica

La tua patch T1+T1.5+T2 ha tecnicamente funzionato:
- ✅ `startTransmit` NON chiamato in callback context (T1)
- ✅ Nessun `time.sleep(0.02)` blocking dentro callback (T1.5)
- ✅ `active_calls/_pending_bridges` mantengono refcount (T2)

**Ma il bug arriva PRIMA**. Tra l'ultimo log Python (`S243 T1: bridge wiring enqueued`) e il primo log successivo dovrebbe esserci:
1. Return da `onCallMediaState` al pjsip callback dispatch
2. Return da pjsip dispatch al `libHandleEvents(20)` call
3. Loop: nuovo `libHandleEvents(20)` tick
4. Chiamata a `self._account.drain_pending_bridges()`

L'assertion scatta da qualche parte qui dentro, su un thread C che non logga niente da Python.

## Hypothesis residue (richiedo tuo ranking)

### N1 — `ensure_port()` / `getAudioMedia()` triggerano pjmedia clock master C-thread
Stesso pattern S239 N1 da `.claude/cache/agents/s238/pjsua2-clock-master-pattern.md` (388 righe research voice-engineer):
> pjmedia clock master thread spawnato internamente da pjmedia conference bridge al primo port register, non controllato da `threadCnt=0` (riguarda solo pjsua workers, non pjmedia clock).

`ensure_port()` chiama `AudioMediaPort.createPort()` → registra port in pjmedia conf bridge → spawn clock master thread → thread non pjlib-registered → al prossimo grp_lock release abort.

S236 DIAG H1/H2/H3 loggano prima di T1 enqueue, quindi `ensure_port()` e `getAudioMedia(i)` sono già stati eseguiti senza crash immediato. Il C-thread spawnato dorme/lavora per qualche ms poi fa unset grp_lock.

**Smoking gun a sostegno**: PJSUA `..pjsua state changed: NULL --> CREATED` e `..registration success` arrivano DOPO il faulthandler dump, quindi sono buffered output pjsua C stderr che esce solo quando il processo aborta. Significa che pjsua C runtime ha `_pjsua_clock_thread` o simile attivo che fa work in background.

### N2 — `drain_pending_bridges()` chiamato 1x e qualcosa lì triggera assertion
Possibile: `call_audio.getPortId()` o `audio_port.getPortId()` o `call.getInfo()` chiama pjsua API che entra in grp_lock su thread che era già "owned" da pjmedia clock thread → cross-thread release assertion.

Ma drain è chiamato in `_pjsua2_thread` che È pjlib-registered. Quindi NON dovrebbe essere lui.

Caveat: nessun log "drain iteration raised" o "bridge slot not assigned" appare, quindi drain non ha eccezioni Python. Ma l'assertion C scatta fuori dal Python try/except.

### N3 — Vivavox.it RTP / SDP attivati al 200 OK risposta scatenano pjmedia teardown su SDP rinegoziazione
Vivavox dopo 200 OK invia ACK + RTP. Se SDP negoziato richiede G.722 (16kHz) ma SaraAudioPort hard-coded L16 8kHz, pjmedia resampler entra in pjmedia clock thread per resampling on-the-fly → unset grp_lock su thread spawnato lazy.

S236 DIAG H3 mostra `call.format clockRate=8000` però — sembra G.711 negoziato. Format match perfetto. Quindi N3 meno probabile.

### N4 — Regressione 2.16-dev specifica
Bug `grp_lock_unset_owner_thread` non riproducibile su pjsip 2.15 LTS stable. Path B1 plan: downgrade `git checkout 2.15.1` rebuild SWIG su iMac Big Sur. Effort ~2h. Rischio: SWIG/libtool compatibility macOS 11.

### N5 — Architectural: switch a Asterisk ARI
Eliminare pjsua2 totalmente. Container Docker Asterisk + REST/WebSocket ARI da Python. Battle-tested, no SWIG director hell. Effort 1-2 sessioni refactor.

## Cosa ti chiedo

1. **Decode `_pjsua2_thread` aborting in `libHandleEvents` line 13767**: trova nel sorgente pjsip 2.16-dev qual è la C function chiamata da line 13767 di pjsua2.py SWIG generated, e quale grp_lock prova a fare unset. Hypothesis: `pjsua_media_state_event_processor` o `pjmedia_clock_thread` body.

2. **Rank N1/N2/N3/N4/N5** con motivazione tecnica e ordine di test consigliato. Vincolo: zero-cost, iMac 2012 Big Sur, macbook dev solo TypeScript/React (no Rust/C build).

3. **Se N1 confermato**: c'è un workaround Python-side? (es. hook `pjmedia_clock_register_thread_cb` via ctypes prima del `createPort`?) Oppure è obbligatorio downgrade 2.15 LTS / Asterisk?

4. **Se N4 ti sembra dominante**: fornisci comandi git checkout + ./configure + make per pjsip 2.15.1 testati su macOS 11 Big Sur Intel x86_64 (toolchain: Xcode CLT, brew autoconf/automake/libtool/swig disponibili).

5. **Se N5 ti sembra l'unica strada pulita**: fornisci skeleton Python aiohttp client che parla con Asterisk ARI WebSocket events + REST channel control, equivalente funzionale del file `voice-agent/src/voip_pjsua2.py` (SIP register, incoming call, audio bridge bidirezionale, RTP G.711 8kHz mono → pipe in/out a esistente `pipeline.process_audio()`).

## File contesto repo (se ti servono path)

- `voice-agent/src/voip_pjsua2.py` (post-patch S243, 800 righe ca)
- `voice-agent/lib/pjsua2/pjsua2.py` (SWIG bindings, 50K+ righe)
- `voice-agent/lib/pjsua2/_pjsua2.so` (shared lib pjsip 2.16-dev compiled)
- `.claude/cache/agents/s238/pjsua2-clock-master-pattern.md` (research voice-engineer, 388 righe — disponibile su richiesta)
- `DOSSIER-SARA-VOIP-BUG.md` (603 righe storia bug — disponibile su richiesta)

## Vincoli sessione

- Zero-cost: no servizi paid, no nuovo hardware
- iMac 2012 Intel, macOS 11 Big Sur (no upgrade OS), no AVX2
- MacBook dev: no Rust/C build, solo Python sync via ssh imac git pull
- Production-grade: no workaround sporchi, fix duraturo
- FLUXION ha 0 clienti paganti — bug Sara è blocker hard pre-launch S244+

Aspetto la tua analisi con ranking + patch git apply-ready (formato unified diff con hunk counts CORRETTI, hai sbagliato in S243 e ho dovuto applicare a mano via Edit) oppure runbook B1 (downgrade 2.15) oppure skeleton B2 (Asterisk ARI).
