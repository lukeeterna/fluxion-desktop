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
