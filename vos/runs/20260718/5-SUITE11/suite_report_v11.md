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
