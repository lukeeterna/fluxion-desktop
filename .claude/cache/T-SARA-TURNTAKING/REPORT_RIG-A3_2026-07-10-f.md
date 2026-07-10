# REPORT RIG-A3 — T-SARA-TURNTAKING (sessione 2026-07-10-f)

> Rito di chiusura C1. Verdetto + prove + discordanze + file/restore. Stato verificato ALLA FONTE.

## VERDETTO

- **FASE 1 RIG-FIX (regstub) 🟢 VERDE** — stub SIP loopback costruito e provato. Commit `ca59cde` (pushed).
- **D3 (soak ≥5min no crash Timer_B) 🟢 VERDE** — engine registrato contro stub, ~11 min continuativi, 0 crash.
- **FASE 2 GATE A3: 1/5 🟢 (ECO ereditato) + BARGE-IN 🔴 RED (BLOCKED-ON turn-taking-RX)**.
  Restano pending: FILLER, SILENZIO, NO-HANGUP.
- **FASE 4 (B3 founder) — NON eseguita** (chiusura ordinata su richiesta founder).

## PROVE

### FASE 1 — regstub (deliverable core, committato ca59cde)
- Sorgente: `voice-agent/tools/gospike/cmd/regstub/main.go` (sipgo v1.4.3, UAS loopback 200 OK a
  REGISTER+OPTIONS, ~88 righe). Build A0 in-place iMac, go.mod INTATTO.
- Cura il crash Timer_B: engine puntato a registrar reale muto andava in Timer_B→exit rc=1→restart→
  "bind in use" ~ogni 1-2 min. Con lo stub, l'engine registra (reg_status 200) e resta su.

### D3 — soak (prova alla fonte, `ssh imac`, 2026-07-10T20:56Z)
- engine child PID **16147 invariato**, uptime 10:51 (~11 min continuativi).
- 3003 go-engine: `registered:true reg_status:200 server:127.0.0.1:15062 engine:"go"`.
- **Timer_B / Assert glock / lock.c:279 / re-registering = 0** in TUTTI i log rig (sara3003.log 1705 righe).
- Stub: 37+ REGISTER 200 OK (RetryInterval 25s). Log TX vivo (`GATE2R-PY-TX drained=390`) senza freeze.
- Sonda inbound INVITE: `ANSWERED` + `MEDIA PCMU` negoziato (RX rms 1667-3291) → rig USABILE.
  Errore "Serve terminato: bind already in use" (diago Serve/Register double-bind) = BENIGNO.
- Artefatti: `.claude/cache/T-SARA-TURNTAKING/rig/{D3-DONE_20260710.md, invite_probe/*.wav}` (committati ca59cde).

### FASE 2 A3 — ECO 🟢 (ereditato verde da sessione -e, NON ri-testato)
- Sara non trascrive l'eco -15dB della propria greeting → zero STT/intent spurii sul path Go.

### FASE 2 A3 — BARGE-IN 🔴 RED (nuovo, questa sessione)
- Dir: `calls/20260710-232633_A3-bargein/` (mix 512KB, rx/tx 256KB, harness.log, VERDETTO.md).
- Harness inietta tono 300Hz/3s a t=2.5s (metà greeting). Engine: greeting TX prosegue (rtp_voice 31→441)
  SENZA interruzione; **ZERO marker RX-side/VAD/barge/clear_tx** in tutta la finestra.
- Barge-in NON scattato. Logica barge-in ESISTE (`voip_goengine.py:591-702`) ma il path caller-audio→VAD
  non registra attività durante l'iniezione loopback. Dettaglio + root-cause in `VERDETTO.md`.

## DISCORDANZE / CONTRADDIZIONI APERTE
1. Incidente rig: `scp -r` su path remoto NON quotato (`/Volumes/MacSSD - Dati/...`) → la shell remota
   ha splittato sullo spazio → copia ricorsiva di `/Volumes/MacSSD` (volume iMac) in `rig/MacSSD/` (~4.6G).
   Processo killato, dir esclusa via `.gitignore`. **DA RIMUOVERE A MANO** (rm -rf hard-bloccato dai permessi):
   `rm -rf '/Volumes/MontereyT7/FLUXION/.claude/cache/T-SARA-TURNTAKING/rig/MacSSD'`.
2. BARGE-IN RED NON è confound del rig (engine stabile, D3 verde): è un gap RX-side reale o di logging
   del go-engine. Va isolato con strumentazione engine-side in sessione fresca, NON per tentativi harness.
3. Path capture BARGE-IN scritto sotto `voice-agent/.claude/...` (cwd harness) vs D1/ECO sotto repo-root
   `.claude/...`. Riallineato a repo-root nel commit di chiusura.

## FILE / RESTORE
- Commit sessione: `ca59cde` (regstub+D3, pushed) + commit di chiusura (BARGE-IN artefatti+report+HANDOFF).
- Baseline 3002 (pjsua2) intatto per tutta la sessione (mai toccato). Trunk EHIWEB mai toccato (A3 solo localhost).
- RESTORE 3002 se cadesse:
  `ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"`

## RILANCIO RIG A3 (sessione fresca, un colpo)
```
# su iMac: regstub + engine + sara3003 su porte alte (Traccar tiene 5062/5090, NON toccare PID 55874)
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent"; \
  nohup ./tools/gospike/regstub_darwin_amd64 -bind 127.0.0.1 -port 15062 >/tmp/regstub.log 2>&1 & \
  set -a; source .env; set +a; export VOIP_SIP_SERVER=127.0.0.1:15062 VOICE_ENGINE=go VOIP_BRIDGE_PORT=8399 VOIP_LOCAL_PORT=15090; \
  nohup python main.py --port 3003 >/tmp/sara3003.log 2>&1 &'
# poi harness A3 come BARGE-IN sopra, cambiando scenario/-injectat.
```

## PROSSIMO PASSO
1. Strumentare RX-side go-engine (voip_goengine._turn_loop / _process_caller_audio) con log RMS/echo_floor
   per capire se l'audio iniettato raggiunge la VAD → risolvere BARGE-IN RED.
2. Completare A3: FILLER (ZERO-bank atteso), SILENZIO (`-dur ≥60s`, reprompt ~22s + hangup ~+18s),
   NO-HANGUP (BLOCKED-ON se non riproducibile in harness).
3. Solo dopo 5/5 con prove → FASE 4 GATE B3 (chiamata reale DID 0972536918, founder, context ≤50%).
