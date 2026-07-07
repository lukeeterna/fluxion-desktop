# REPORT — T-SARA-MEDIASWAP-GO · GATE 1 (COSTRUZIONE + SELFTEST) · 2026-07-08

## VERDETTO: 🟢 VERDE
Motore telefonico Go di Sara costruito (evoluzione del gospike VERDE-PIENO, commit 768e476) +
adapter Python additivo + selftest senza trunk PASS su tutte le done-condition GATE 1.
Reversibilità totale garantita: `VOICE_ENGINE=go|pjsua2`, **default `pjsua2` invariato**;
`voip_pjsua2.py` NON toccato.

## PROVA GREZZA (committata in `.claude/cache/T-SARA-MEDIASWAP/`)
Selftest locale (porta ponte 8399, in-process, zero SIP/trunk):
- **(a) RX→pipeline→metrica**: turno reale processato — STT reale
  `"Buon giorno, ...prenotare un taglio per domani"` → FSM `"...Taglio uomo o Taglio donna..."`
  (L2_slot, latency 93.57ms). `/api/metrics/latency` count **3→4**, incrementato **dal path
  adapter** (`voip_goengine._process_caller_audio → _log_turn_analytics → analytics.log_turn`),
  NON dall'harness. Controprova: `grep log_turn|conversation_turns selftest.log` = **zero righe**,
  eppure il count sale → il +1 è causato solo dall'adapter.
- **(b) TTS→AUDIO_TX**: 254 frame (5080ms) cadenzati catturati (`selftest_tx_capture.wav`).
- **(c) barge-in**: coda TX riempita=202 → dopo trigger RMS/`clear_tx`=0.
- File: `selftest_metrics.json`, `selftest_output.txt`, `selftest.log`, `selftest_tx_capture.wav`.
- Cross-compile portabilità: `GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build` **COMPILA**
  (`engine_windows_amd64.exe` 11.41MB); darwin build 11.58MB. (agent-reported)

## ARCHITETTURA CONSEGNATA
- **Engine Go** `voice-agent/engine/main.go` (+ go.mod/go.sum): SIP invariato dal gospike
  (REGISTER+digest+keepalive+symmetric RTP); **fix #1** bind IPv4 locale auto-rilevato (dial UDP
  al server SIP → LocalAddr; flag `-bind` override; mai `[::]`/`0.0.0.0`); **fix #2** CALL_START
  emesso SOLO a media ATTIVO; codec G.711 lato engine, **PCM16/8k/mono** verso Python; ponte TCP
  framed `tipo(1B)+len(2B BE)+payload` (STATUS/CALL_START/AUDIO_RX/CALL_END ↔ AUDIO_TX/HANGUP);
  barge-in cap buffer TX ≤200ms lato engine (pacing RTP dell'engine). Binari gitignorati.
- **Adapter Python** `voice-agent/src/voip_goengine.py` (NUOVO, additivo): TCP server 127.0.0.1;
  spawn+supervisione binario engine (creds via env, restart backoff); AUDIO_RX→rx_queue (drop-in,
  PCM16/8k); drena queue_tts_audio (ratecv 16k→8k) → AUDIO_TX; barge-in RMS Python (svuota coda TX
  locale); CALL_START→greeting dal cervello; STATUS→cache `/api/voice/voip/status` shape identico
  con `engine:"go"`. **Metrica**: `_log_turn_analytics` usa lo STESSO `get_logger()` singleton letto
  da `/api/metrics/latency` (main.py:858) → una chiamata reale ora incrementa la metrica.
- **Greeting+disclosure AI**: testo nel cervello Python (config), disclosure di natura AI di default.
- **main.py**: flag `VOICE_ENGINE` (default `pjsua2`), edit minimo.

## DISCORDANZE (vince il disco)
- Turno reale in `_process_caller_audio` (~487-503), NON `_process_turn` come da premessa. Wired lì.
- Blocco manuale log_turn nel selftest era ~252-271 (non 255-271). Rimosso.
- go.mod gospike dichiara `go 1.26.4`; floor engine fissato a `go 1.23.0`; Go iMac in
  `/usr/local/Cellar/go` non nel PATH ssh → `GOTOOLCHAIN=local CGO_ENABLED=0`.
- Orchestratore = `VoiceOrchestrator` (non `SaraVoiceOrchestrator`).
- **ROOT CAUSE "count mai >0"**: né `voip_pjsua2.py` né (prima) `voip_goengine.py` scrivevano
  `conversation_turns` dal path VoIP → il gap NON era solo il bug clock-thread pjsua2, era anche
  metrica mai wired sul telefono. Ora wired lato `go` (pjsua2 lasciato invariato per contratto).
- Selftest richiede `KMP_DUPLICATE_LIB_OK=TRUE` (conflitto OpenMP faster-whisper).

## FILE TOCCATI + BACKUP (#1d)
- NUOVI: `voice-agent/engine/{main.go,go.mod,go.sum,selftest.py,.gitignore}`,
  `voice-agent/src/voip_goengine.py`.
- MODIFICATI: `voice-agent/main.py` (bak `main.py.bak-PRE-MEDIASWAP-20260707-234755`),
  `voice-agent/src/voip_goengine.py` (bak `...bak-PRE-MEDIASWAP-METRIC-20260708-000233`),
  `voice-agent/engine/selftest.py` (bak `...bak-PRE-MEDIASWAP-METRIC-20260708-000233`).
- gospike originale `voice-agent/tools/gospike/` INTATTO.

## STATO FINALE (coerente)
Sara baseline **INTATTA**: PID **9257**, health 200, `reg_status:200`, `engine:"pjsua2"` (default
non toccato), `rtp_active:false`. Selftest in-process porta 8399 → **nessun REGISTER concorrente**
sul trunk. `conversation_turns` cresciuto di +N per i turni di selftest (atteso: è la prova della
metrica); bookings-voce non incrementati dal selftest (turno singolo, FSM ferma a L2_slot).
Restore Sara: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup /usr/bin/python3 main.py --port 3002 >/tmp/sara.log 2>&1 &"` → verifica health 200 + reg_status:200.

## PROSSIMO — GATE 2 (sessione fresca, founder presente, rete di casa)
Resume one-shot:
1. Context check (REGOLA #27). Baseline A3: voip/status, PID Sara, **count bookings-voce reale**
   (delta per #3 charge-continuity), comando restore stampato.
2. `VOICE_ENGINE=go` + riavvio Sara su iMac → verifica engine registrato (STATUS 200 nello status).
   Restore = ripartire con default `pjsua2`.
3. Founder chiama **0972536918**: (1) sente greeting con disclosure AI; (2) chiede prenotazione
   salone realistica, Sara risponde nel merito; (3) `/api/metrics/latency` count>0 su chiamata REALE
   (ora possibile grazie al wiring metrica GATE 1); (4) barge-in: parlando sopra Sara si zittisce
   ~0.5s; (5) processo Sara stabile pre/post.
4. Se scatta write-path prenotazione: riporta id + delta DB, NON cancellare.
5. #1c: al 1° rosso, UNA iterazione etichettata (ENGINE-BRIDGE/PIPELINE-RX/TTS-TX/BARGE-IN), poi STOP.
