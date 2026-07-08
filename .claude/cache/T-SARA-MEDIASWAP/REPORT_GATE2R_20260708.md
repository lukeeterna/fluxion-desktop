# REPORT — T-SARA-MEDIASWAP-GO · GATE 2R · 2026-07-08

## VERDETTO PER-GATE
- **GATE A (autonomo, localhost harness, senza founder/trunk): 🟢 VERDE** — prova misurata.
- **GATE B (founder, chiamata reale): ⚪ NON ESEGUITO** — richiede founder presente + context reale ≤50% (superato in questa sessione). Resume one-shot sotto.
- **DIFETTO A (egress TX muto): 🟢 RISOLTO** — etichetta root cause = **ENGINE-RTP-WRITE via cap `txCapFrames=10`**, fix H1.
- **DIFETTO B (engine orfano su shutdown): 🟢 RISOLTO** — reap orfani all'avvio + kill child (atexit + SIGTERM/SIGINT handler + killpg).

## ROOT CAUSE (H1 confermata deterministicamente, poi falsificata sul verde)
Python `_tx_pump` inviava AUDIO_TX **in burst senza pacing**; l'engine (`pushTX`, `txCapFrames=10`=200ms) scartava i frame più vecchi appena il buffer superava → il clock RTP 20ms drenava ~50/s → di un greeting da 452 frame ne sopravvivevano ~11 → **chiamante muto**. Il cap confondeva barge-in con buffering legittimo. Invisibile in GATE 1/gospike perché l'echo gospike scriveva RX→enc.Write nel read-loop, **già paced** e senza passare da pushTX/cap.

## PROVA GREZZA (contatori per anello TX — RED vs POST-fix)
| Anello | RED (no pacing) | GREEN2 (fix, greeting-only) |
|---|---|---|
| PY drained (da _tx_queue) | 452 | 420 |
| PY written (a socket) | 452 | 420 |
| GO rx_audiotx (da socket) | 452 | 420 |
| GO push_acc (nel buffer) | 452 | 420 |
| **GO push_drop (cap 200ms)** | **441** ⬅ smoking gun | **0** |
| **GO rtp_voice (RTP non-silenzio)** | **11** | **419** |
| WAV harness rms_max | **0 (muto)** | **3820 (voce piena)** |

WAV harness POST-fix: `/tmp/gate2r_green2_rx.wav` (192044 B PCM, rms sale 485→3820 su ~9s, greeting "Salone Demo FLUXION, buon pomeriggio!"). GREEN1 con utterance: barge-in corretto a +2.5s (rms 2758 vs echo 215) → greeting troncato di proposito, comportamento voluto.

## FIX APPLICATO (l'unica iterazione #1c)
`voip_goengine.py::_tx_pump` — pacing 20ms su clock monotonico (`FRAME_MS=0.020`, sleep fino al prossimo slot, risincronizza su idle/ritardo, `clear_tx` barge-in preservato). Solo Python, nessun rebuild engine. Anello POST-fix lossless 1:1 (drained≈rx≈push_acc≈rtp_voice=420/420/420/419, push_drop=0).

## FILE TOCCATI + BACKUP (#1d, su iMac)
- `voice-agent/src/voip_goengine.py` — metriche TX + fix H1 pacing + Difetto B. Backup: `.bak-PRE-GATE2R-20260708-172245`, `.bak-PRE-GATE2R-FIX-20260708-173542`, `.bak-PRE-GATE2R-SIGB-20260708-173931`.
- `voice-agent/engine/main.go` — metriche GO-TX (rx_audiotx/push_acc/push_drop/rtp_voice/rtp_silence + payloadType + remote). Backup: `.bak-PRE-GATE2R-20260708-172439`. Binario `engine_darwin_amd64` rebuildato strumentato (gitignored, solo iMac).
- `voice-agent/tools/gospike/main.go` + NUOVO `voice-agent/tools/gospike/uac.go` — modalità UAC harness (`-call`, `-injectwav`). UAS default intatto. Backup: `main.go.bak-PRE-GATE2R-20260708-172730`.
- `voice-agent/main.py` — legge `VOIP_BRIDGE_PORT` env (default 8300, additivo). Backup: `.bak-PRE-GATE2R-20260708-173039`.

## DISCORDANZE
- **git iMac↔MacBook disallineati** (pre-esistente): su iMac `voip_goengine.py`/`engine/main.go`/`gospike/` erano `??` untracked; su MacBook sono tracciati. Correzione: copiati i 5 file iMac→MacBook via tar-over-ssh, committati sul MacBook (sorgente canonico), iMac pull.
- Primo voice-engineer si è fermato a un **budget VOS falso** (REGOLA #27/S351: hook inietta la % RAW del main nei subagent) senza eseguire; ri-spawn fresco con istruzione anti-falso → esecuzione completa.

## STATO FINALE (coerente, verificato alla fonte)
Sara demo **default pjsua2**: `engine:"pjsua2"`, `reg_status:200`, `registered:true`, health ok. **Zero orfani** engine_darwin. Istanza test 3003 bonificata. DB non toccato (nessuna prenotazione: GATE A non esercita FSM booking a fondo). Motore Go resta fallback flaggato (`VOICE_ENGINE=go`) — GATE A verde NON promuove a default (serve GATE B live 5/5 + yes/no founder).

## RESTORE (invariato)
`ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && kill <pid>; sleep 1; nohup /usr/bin/python3 main.py --port 3002 >/tmp/sara.log 2>&1 &"`

## PROSSIMO — GATE B (founder, UNA chiamata reale), resume one-shot
1. Sara demo su iMac: `VOICE_ENGINE=go` + riavvio pipeline 3002 (restore stampato sopra). Verifica tripla: health ok, `engine:"go"`, `reg_status:200`, nessuna doppia REGISTER.
2. Founder chiama `0972536918`: greeting **con disclosure** ("Sono Sara, l'assistente virtuale") udibile? → richiesta prenotazione → PARLARE SOPRA a metà risposta (barge-in ~0.5s) → "ma sei una persona vera?" (attesa: conferma naturale assistente virtuale) → riaggancia. Campiona `/api/metrics/latency` + log durante.
3. Scorecard 5/5: (1) greeting+disclosure udito, (2) risposta nel merito, (3) count aumenta, (4) barge-in ~0.5s, (5) stabilità pre/post. VERDE 5/5 → `VOICE_ENGINE=go` DEFAULT (#1d sul config) + inizio soak. ROSSO → ripristino default pjsua2 + etichetta.
