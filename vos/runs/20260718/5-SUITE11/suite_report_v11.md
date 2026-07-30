# SUITE v1.1 — Report T-SUITE-v1.1-r7 (#34v)
**Data:** 2026-07-18  
**Sessione:** #34v — T-SUITE-v1.1-r7  
**Modello:** Sonnet 4.6  
**Target rig:** http://127.0.0.1:3003 (sara3003, go engine, EdgeTTS IsabellaNeural)  
**[TARATURA][BOOT]:** reprompt_timer=22.0s | vad_speech_threshold=400 rms | vad_silence_timeout=50 frame ~1000ms | vad_min_speech_frames=15 ~300ms | E6_strike_threshold=3

## Tabella riepilogo SCN-01..09

| ID | Nome | Path | Verdict | Note |
|---|---|---|---|---|
| SCN-01 | smoke — health + greeting | HTTP | ND | non eseguito (context limit) |
| SCN-02 | congedo×2 — goodbye ripetuto | HTTP | ND | non eseguito (context limit) |
| SCN-03 | name-gate — «Buonasera» | HTTP | ND | non eseguito (context limit) |
| SCN-04 | ND-by-design (path audio) — E6 text-API assert minimi | HTTP text-API | ND-by-design | path audio ≠ text-API; assert minimi: no crash, empty→empty, fsm invariato |
| SCN-05 | ND-by-design (path audio) — silenzio text-API assert minimi | HTTP text-API | ND-by-design | path audio ≠ text-API; assert minimi: no crash, empty→empty, fsm invariato |
| SCN-06 | context-switch (non barge-in) — input rapido consecutivo | HTTP | ND | relabelato da «barge-in»; non eseguito (context limit) |
| SCN-07 | dettatura numero — inject cifre pulite | HTTP | ND | non eseguito (context limit) |
| SCN-08 | E6-AUDIO — 3 garbage audio → stt_failure → E6 | AUDIO (go engine) | ND | F3 non eseguito: context limit raggiunto prima del test audio |
| SCN-09 | SILENZIO-AUDIO — no inject >22s → reprompt timer | AUDIO (go engine) | ND | F3 non eseguito: context limit raggiunto prima del test audio |

## Stato mandato T-SUITE-v1.1-r7

| Fase | Stato | Evidenza |
|---|---|---|
| GATE-0 | ✅ PASS | HEAD==origin/master 4ce8b5e3; porcelain: solo M fluxion.db*+VectCutAPI |
| F1 REALIGN iMac | ✅ PASS | 6 file Classe A md5 identici; ff-merge 6e7fb8c9→4ce8b5e3; rev-parse iMac=4ce8b5e3; :3002 pid=31760 invariato |
| F2 RIG | ✅ PASS | rig UP in 7s; reg=68473 sara=68476; TTS=EdgeTTS IsabellaNeural; SARA_TEST_CAPTURE=1 |
| F3 SCENARI AUDIO | ❌ ND | context limit 60% hook raggiunto prima dell'esecuzione; VAD routes verificate attive (500 su malformed); harness sara_audio_harness.py identificata; path inject via /api/voice/process-with-vad confermato |
| F4 RELABEL | ✅ PARZIALE | SCN-06→«context-switch (non barge-in)»; SCN-04/05→«ND-by-design (path audio)»; questo report scritto |

## Note tecniche F1 (voip_goengine.py)

`voice-agent/src/voip_goengine.py` su iMac era versione VECCHIA (md5 `c1fac303`).  
origin/master aveva versione NUOVA (md5 `e2a3f2b0`) con:
- **E6-FIX**: `_should_escalate` check aggiunto a `_explicit_goodbye` (necessario per SCN-08)
- **[TARATURA]** logging blocks: BOOT, ENDPOINT, SLOT

Rimozione stale copy e ff-merge → iMac ora ha la versione corretta.

## Infrastruttura RIG confermata

- GUARD OK: solo high-port loopback (127.0.0.1:15062|3003|15090|8399)
- regstub binary: `/voice-agent/tools/gospike/regstub_darwin_amd64` (9MB, 10 Lug 22:34)
- Sara3003 VAD routes: `/api/voice/process-with-vad`, `/api/voice/vad/chunk` ATTIVE
- VAD handler: sessione-based, audio_hex PCM inject supportato
- Reprompt timer: 22.0s (da [TARATURA][BOOT])

## VERDETTO SESSIONE

**VERDETTO: ROSSO** (F3 non eseguito — context limit)

## Esiti F3

**Data**: 2026-07-18 | **Sessione**: auto-close 61% context

### SCN-08 — E6-AUDIO
**FAIL (incomplete — context budget 61%)**
- RIG UP confermato in 7s (sara3003:3003, regstub:15062, SARA_TEST_CAPTURE=1)
- RESET OK, sessione `0b949b1c`
- Inject testo "Sono Marco Rossi, cliente nuovo" → STATE ASKING_PHONE (reply: "Non la trovo tra i nostri clienti, Marco. Mi dà un numero di telefono per regist...")
- Generato noise PCM 16kHz mono 16-bit 24000 campioni (±5000 ampiezza, 48000 bytes) — `/tmp/noise_payload.txt` su iMac
- **INTERROTTO prima dei 3 inject audio** — sessione chiusa per vincolo context budget #7 (61%)
- Strike 1/2/3 e E6 TTS: ND (non eseguiti)

### SCN-09 — SILENZIO-AUDIO
**ND (non eseguito)** — chiuso su context budget prima dello scenario.

### Causa chiusura anticipata
Context 61% (soglia mandatoria vincolo #7 CLAUDE.md). Sessione interrotta dopo RIG UP + testo inject + generazione noise PCM.

### Stato rig a chiusura
- sara3003 (PID 73771): SPENTO
- regstub (PID 73769): SPENTO
- :3002 baseline: RUNNING pid invariato ✓


---

## Esiti F3

**Data:** 2026-07-30T17:27:17+02:00
**Rig:** http://127.0.0.1:3003
**WAV campione:** `/Volumes/MacSSD - Dati/FLUXION/vos_f3_run/f3_audio_sample.wav`

### SCN-08 — E6 sul path AUDIO
**Verdetto:** FAIL
**Motivo:** criteri non maturati: strike 1→2→3, E6, congedo richiamar/no-collega, BYE≤2s
**HTTP:** reset=HTTP 200 · text=HTTP 200 · audio_1=HTTP 200 · audio_2=HTTP 200 · audio_3=HTTP 200
**Strike 1 timestamp:** ND
**Strike 2 timestamp:** ND
**Strike 3 timestamp:** ND
**E6 timestamp:** ND
**Goodbye-TTS testo timestamp:** ND
**Goodbye-TTS fine timestamp:** 17:26:30
**BYE timestamp:** ND
**BYE dalla fine goodbye-TTS:** ND
**Congedo contiene «richiamar» e non «collega»:** NO
**Evidenza log VERBATIM:**
```text
17:26:30 [src.tts_engine] INFO: [EdgeTTSEngine] TTS done: TTFB=340ms download=1821ms total=1885ms method=stream text='Non la trovo tra i nostri clienti, Marco. Mi dà un numero di telefono per registrarla?'
17:26:30 [src.vad.ten_vad_integration] INFO: FluxionVAD (Silero) started
17:26:30 [src.vad.ten_vad_integration] INFO: FluxionVAD (silero) stopped
17:26:30 [aiohttp.access] INFO: 127.0.0.1 [30/Jul/2026:17:26:30 +0200] "POST /api/voice/process-with-vad HTTP/1.1" 200 461 "-" "Python-urllib/3.9"
17:26:30 [src.vad.ten_vad_integration] INFO: FluxionVAD (Silero) started
17:26:30 [src.vad.ten_vad_integration] INFO: FluxionVAD (silero) stopped
17:26:30 [aiohttp.access] INFO: 127.0.0.1 [30/Jul/2026:17:26:30 +0200] "POST /api/voice/process-with-vad HTTP/1.1" 200 462 "-" "Python-urllib/3.9"
17:26:31 [src.vad.ten_vad_integration] INFO: FluxionVAD (Silero) started
17:26:31 [src.vad.ten_vad_integration] INFO: FluxionVAD (silero) stopped
17:26:31 [aiohttp.access] INFO: 127.0.0.1 [30/Jul/2026:17:26:30 +0200] "POST /api/voice/process-with-vad HTTP/1.1" 200 462 "-" "Python-urllib/3.9"
```

### SCN-09 — silenzio → reprompt
**Verdetto:** FAIL
**Motivo:** criteri non maturati: reprompt assente, timestamp/delta >25s
**HTTP:** reset=HTTP 200 · greeting=HTTP 200
**Fine greeting-TTS timestamp:** 17:26:47
**Inizio reprompt timestamp:** ND
**Delta reprompt:** ND
**Evidenza log VERBATIM:**
```text
17:26:47 [src.tts_engine] INFO: [EdgeTTSEngine] TTS done: TTFB=431ms download=840ms total=901ms method=stream text='Mi dica pure, come posso aiutarla?'
```

**[LETTURA PUNTO 3 — SCN-09]** Il reprompt_timer NON si è MAI armato sulla sessione HTTP: `grep -c reprompt /tmp/rig_sara3003.log` = 1, unica occorrenza = riga 110 `[TARATURA][BOOT] reprompt_timer=22.0s (voip_goengine.py:87)` — cioè SOLO la config di boot, ZERO eventi di arming runtime. Il reprompt_timer vive sul path AUDIO della go engine (voip_goengine.py), non sul path HTTP `/api/voice/process`. Quindi **SCN-09 = ND-by-design-path, NON FAIL**. SCN-08 resta **FAIL**: il rumore int16 (±3000-6000, 1.5s) non è stato classificato speech dal Silero VAD (log: "FluxionVAD (Silero) started"→"stopped" immediato), nessuno strike accumulato sul path audio → E6 non raggiunto.
