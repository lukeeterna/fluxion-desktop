# REPORT B3-X2-PROVE (#34v) — prova esterna congedo M5 su rig multi-inject

Data: 2026-07-16 · Rig high-port loopback (sara :3003 + regstub 127.0.0.1:15062) · ZERO :3002, ZERO trunk/telefono.

## GATE-0
- HEAD == origin/master == `4312f6c9`. Albero pulito SALVO `M tools/VectCutAPI` (gitlink embedded,
  pointer-only, pre-esistente) → sbloccato dal giudice come carve-out (opzione 3).

## F1 — LAUNCHER (ricetta ricostruita)
Fonti: `REPORT_RIG-A3_2026-07-10-f.md` §56-64 + `rig/D3-DONE_20260710.md` §21.
Artefatto: `launch_rig.sh` (idempotente, SOLO high-port, guard che ABORTA se punta a :3002/trunk/Traccar).
Ricetta effettiva (eseguita su iMac via `ssh imac 'bash -s' < launch_rig.sh`):
```
regstub:  ./tools/gospike/regstub_darwin_amd64 -bind 127.0.0.1 -port 15062
env:      VOIP_SIP_SERVER=127.0.0.1:15062 VOICE_ENGINE=go VOIP_BRIDGE_PORT=8399 VOIP_LOCAL_PORT=15090
sara:     venv/bin/python main.py --port 3003
health:   curl :3003/api/voice/voip/status → "registered": true
```
Guard: confronto ESATTO per-porta (3002/5062/5090) — evita match-substring 15062⊃5062, 15090⊃5090.

## F2 — AVVIO RIG (prova di vita)
`RIG UP (7s): {"running": true, "sip": {"registered": true, "reg_status": 200, "server":"127.0.0.1:15062"}, "engine":"go"}`
regstub `REGISTER 200 OK`; `GoEngine start: registered=True reg_status=200`. Idempotente (kill stale + restart).

## F3 — MULTI-INJECT
Meccanismo: UN injectwav concatenato (8k mono 16-bit) `"Marco Rossi"` + gap silenzio + `"Grazie arrivederci"`,
segmentato dal VAD del go-engine (ZERO modifiche a FSM/engine/NLU/harness). TTS via macOS `say -v Luca` + afconvert.

### run1 (injectat=4000ms, gap 6s) — INVALIDO per timing
Greeting reale ~8s (SPEAKING 22:49:48→56). Turno1 iniettato a t=4-5s cadde DENTRO il greeting → perso, mai trascritto.
Unica STT = turno2 `'Grazie e arrivederci.'` → intent=CORTESIA (in IDLE, FSM non avanzata) → nessun BYE (harness chiude a dur-max 28s).
Precondizione mandato ("turno1 oltre ask_name") NON soddisfatta → run scartato. Capture: `run1_invalid_timing/`.

### run2 (injectat=11000ms, gap 9s) — VALIDO
Turno1 post-greeting, turno2 a t≈21s. Righe log citate (`run2_valid/sara_fsm_transitions.log`):
```
22:52:31 [S142] Bare name detected in IDLE: 'Marco Rossi'
22:52:31 [S142] Bare name in IDLE: 'Marco Rossi' → name=Marco, surname=Rossi   ← FSM OLTRE ask_name
22:52:39 BARGE-IN: rms=5052 ... (turno2)
22:52:40 [RX-MARK] stato=LISTENING                                             ← fine-utterance turno2
22:52:41 [NLU] intent=CHIUSURA (conf=0.80) | input='e arrivederci'
22:52:41 [S142] Standalone goodbye detected: 'e arrivederci' → exit=True       ← transizione goodbye/S142
22:52:42 [EdgeTTSEngine] TTS done: text='Ha ragione. Arrivederci, buona giornata.'
22:52:43 risposta TTS in coda TX (goodbye) — SPEAKING :43→:47
22:52:48.592 HANGUP ricevuto da Python → CALL_END                              ← BYE
```
Harness terminato a ~31s (< dur 40, NESSUN "durata max hangup") = chiuso dal BYE di Sara.

## MISURE CRITERIO "BYE ≤5s dal fine-utterance turno2"
- fine-utterance turno2 (endpoint→LISTENING): **22:52:40**
- BYE (HANGUP→CALL_END): **22:52:48.592**
- Delta letterale = **~8.6s** → ECCEDE i 5s.
- MA l'eccedenza è INTERAMENTE la goodbye-TTS che Sara pronuncia PRIMA di riagganciare
  (`'Ha ragione. Arrivederci, buona giornata.'`, SPEAKING :43→:47 ≈5s) — comportamento by-design
  (S142 "hangup dopo goodbye TTS"). Da fine-goodbye-TTS (LISTENING :48) a BYE = **0.6s**.

## VERDETTO
- Condizioni ROSSE del mandato ("no BYE o transizione assente"): **ENTRAMBE ASSENTI** → run NON rosso.
  - BYE emesso: SÌ (22:52:48.592). Transizione S142/goodbye: SÌ (exit=True 22:52:41).
- Path M5 congedo→BYE: **PROVATO FUNZIONANTE end-to-end** sul rig multi-inject.
- Literal "≤5s dal fine-utterance caller" = 8.6s: NON soddisfatto alla lettera, per goodbye-TTS by-design (0.6s dal fine-TTS).

**🟢 con caveat**: M5 funziona (congedo→goodbye_standalone/CHIUSURA→BYE). Discordanza aperta = interpretazione
della finestra ≤5s (misurare dal fine-utterance caller=8.6s vs dal fine-goodbye-TTS=0.6s) → decide il giudice.

## Artefatti
- `launch_rig.sh` · `inject_multi_gap9s.wav` · `capture_B3X2_20260716/{run1_invalid_timing,run2_valid}/{rx,tx,mix,harness_rx}.wav + harness_timeline.md` · `run2_valid/sara_fsm_transitions.log` · questo report.
