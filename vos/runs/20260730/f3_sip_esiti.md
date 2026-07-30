## Esiti F3-SIP

**Data:** 2026-07-30T18:17:48+02:00
**Rig:** loopback Sara HTTP :3003 · regstub :15062 · SIP :15090 · bridge :8399
**WAV campione:** `/Volumes/MacSSD - Dati/FLUXION/vos/runs/20260730/f3_sip_sample.wav`

### SCN-08 — E6 sulla gamba SIP
**Verdetto:** FAIL
**Tentativo usato:** 2
**Motivo:** INVITE/media non confermati (480 Temporarly unavailable); criteri non maturati: FSM oltre identità, strike 1→2→3, E6, congedo richiamar/no-collega, BYE≤2s
**Chiamata connessa:** ND
**Fine greeting RTP:** ND
**Fine risposta identità RTP:** ND
**Strike 1 timestamp:** ND
**Strike 2 timestamp:** ND
**Strike 3 timestamp:** ND
**E6 timestamp:** ND
**Goodbye-TTS testo timestamp:** ND
**Fine goodbye-TTS RTP:** ND
**BYE timestamp:** ND
**BYE dalla fine goodbye-TTS:** ND
**Congedo contiene «richiamar» e non «collega»:** NO
**Evidenza log VERBATIM:**
ND

### SCN-09 — silenzio → reprompt
**Verdetto:** FAIL
**Tentativo usato:** 2
**Motivo:** INVITE/media non confermati (480 Temporarly unavailable); criteri non maturati: scatto reprompt_timer, trigger entro 25s, reprompt presente
**Chiamata connessa:** ND
**Arming reprompt_timer timestamp:** ND
**Fine greeting-TTS RTP:** ND
**Scatto reprompt_timer timestamp:** ND
**Inizio reprompt RTP:** ND
**Delta trigger dalla fine greeting:** ND
**Delta audio reprompt dalla fine greeting:** ND
**Evidenza log VERBATIM:**
```text
18:17:36 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:37 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:38 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:39 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:41 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:42 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:43 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:44 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:45 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:46 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:47 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
18:17:48 [voip_goengine] INFO: [GATE2R-PY-TX] drained=0 written=0 bytes=0
```
