# BARGE-IN — VERDETTO 🔴 RED (rig stabile, NON confound) — 2026-07-10-f

## Setup
- Rig A3 stabile (regstub :15062, engine PID 16147, sara3003 :3003) — engine NON crasha (D3 verde).
- Harness: `gospike -call sip:0972536918@127.0.0.1:15090 -port 15082 -injectat 2500 -echo 0 -dur 16`
  con `SARA_TEST_CAPTURE=1`. Utterance iniettata = `beepPCM(300Hz, 3s)` (default, uac.go:98) —
  tono con energia reale (`utter_samples=24000`), NON silenzio.

## Osservazione
- Harness: iniezione attiva `injecting=true` a t=3,4,5s (metà greeting).
- Engine (sara3003.log, finestra 23:26:33–50): `greeting in coda TX` + `GATE2R-GO-TX` con
  `rtp_voice` che cresce 31→441 SENZA interruzioni per tutta la finestra di iniezione.
- **ZERO marker RX-side**: nessun `echo_floor`, `GATE2R-PY-RX`, `vad`, `turn`, `barge`, `clear_tx`
  in tutta la finestra della chiamata (grep = 0 righe).
- Sara ha finito la greeting ignorando il tono → **barge-in NON scattato**.

## Root cause (ipotesi, #1c consumata — NON riaprire in questa sessione)
La logica barge-in ESISTE lato Python (`voip_goengine.py:55-73,591-702`: `thr=max(500, 2.5·echo_floor)`
sostenuto ~260ms → `_clear_tx`). Ma durante l'iniezione l'engine NON registra ALCUNA attività
RX-side/VAD. Il path caller-audio→VAD/barge-in del go-engine non ha processato (o non logga)
l'audio iniettato in questa configurazione loopback. Distinguere "gap di logging" vs "gap di wiring
RX→VAD" richiede strumentazione engine-side dedicata = **investigazione NUOVA, fuori scope sessione**.

## Etichetta
🔴 **RED / BLOCKED-ON turn-taking-RX** (DEBITO registrato). NON è instabilità del rig (engine su,
D3 verde). NON è un pass. Prossima sessione: instrumentare RX-side del go-engine PRIMA di ri-testare.
