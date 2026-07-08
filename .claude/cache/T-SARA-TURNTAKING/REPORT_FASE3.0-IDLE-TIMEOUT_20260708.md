# REPORT T-SARA-TURNTAKING — FASE 3.0 (IDLE-TIMEOUT livello chiamata)

Data: 2026-07-08 · Gate label (#1c): **IDLE (2ª gamba legittima dell'hangup)** · Verdetto: 🟢 FASE 3.0 CHIUSA (mutazione deployata+compilata, default pjsua2 invariato) · Mutazioni: 1 file (`voip_goengine.py`) · GATE A3(1-4)+(4b) test = FASE 3.2 (sessione fresca)

## 1. Baseline di partenza (stampata, A3)
- `engine:"pjsua2"`, `registered:true`, `reg_status:200`, `rtp_active:false`; health ok v2.1.0; latency **count=18**; PID **79633** `main.py --port 3002`, processo unico, **zero orfani** engine_darwin. DB `fluxion.db` 20 tabelle (`chiamate_voice` presente). Restore point = default pjsua2 (`VOICE_ENGINE` non toccato).

## 2. Verifica sul disco (mandato FASE 3.0)
- Confermato: **NON esiste** idle-timeout a livello chiamata nel path Go. `_audio_processing_loop` gira su `rx_queue.get(timeout=0.1)`; se il chiamante tace del tutto, `speech_frames` non cresce mai → nessun turno completa → **call appesa all'infinito** → numero OCCUPATO per i clienti successivi. `VAD_SILENCE_TIMEOUT=50` (=1s) è solo **fine-turno**, non call-level (distinto correttamente).

## 3. Mutazione applicata (`voip_goengine.py`, #1d)
Backup #1d iMac verificato: `src/voip_goengine.py.bak-PRE-F30-20260708-193738` (size=33089 = versione FASE 2 committata).
- **Costanti**: `IDLE_REPROMPT_S=22.0` (~20-25s), `IDLE_HANGUP_S=18.0` (+~15-20s), `IDLE_REPROMPT_TEXT="Pronto, è ancora in linea?"`, `IDLE_GOODBYE_TEXT="Non la sento più. Grazie per aver chiamato, arrivederci."`.
- **Stato**: `_last_caller_voice_ts` (monotonic ultimo parlato REALE chiamante), `_idle_reprompted`, `_idle_reprompt_ts`. Armati a CALL_START (`_last_caller_voice_ts=now`), disarmati a CALL_END.
- **Riarmo timer**: `_last_caller_voice_ts=now` + `_idle_reprompted=False` sia sul **barge-in** (chiamante prende la parola) sia sul **parlato VAD normale** (`rms>VAD_SPEECH_THRESHOLD`).
- **Thread monitor** `_idle_monitor_loop` (daemon `goengine-idle`, avviato accanto al tx-pump): misura silenzio COMBINATO (né Sara TX/grace né chiamante). Durante TX di Sara non conta. `last_audio = max(_last_caller_voice_ts, _tx_last_frame_ts)` → il conteggio parte dalla FINE del parlato di Sara. Dopo `IDLE_REPROMPT_S` → UN reprompt via `_speak_canned`; se dopo `IDLE_HANGUP_S` dalla fine del reprompt è ancora muto → congedo + **hangup legittimo** loggato `HANGUP timeout-silenzio` + `_hangup_after_drain`.
- **`_speak_canned`**: `pipeline.tts.synthesize(text)` (stessa TTS del cervello, orchestrator.py:511 `self.tts`) → `queue_tts_audio` (stesso sink provato GATE 2R). Best-effort, mai solleva.
- **Complementare alla FSM-HANGUP GUARD (spec 2.3)**: quella sopprime l'auto-hangup su STT sporco; questo è l'UNICO altro hangup lecito per Sara oltre al congedo esplicito mutuo. «Sara non riaggancia mai per prima» resta vero — tranne su silenzio prolungato (2ª gamba legittima da mandato).

## 4. Deploy + verifica (prova grezza)
- `py_compile` OK **MacBook (py3.13)** + **iMac (py3.9)**.
- Sync via ssh+cat (scp rotto da spazi nel path remoto). md5 local==iMac = `4079e6bc8c52318e1e6f9d59a43b91b7`.
- Pipeline riavviata **PID 82763** (`main.py --port 3002`), health ok, `engine:"pjsua2"` (default non toccato), `registered:true`, **`reg_status:200`** (assestata ~14s), processo unico, **zero orfani** engine_darwin. → deploy NON regredisce il default.

## 5. PROSSIMO — FASE 3.1 + 3.2 GATE A3 (sessione fresca, headroom pieno)
- **FASE 3.1 (ADDENDUM W)**: estendere `voice-agent/tools/gospike/uac.go` con `-echo <dB>` (mix ricevuto ~-15dB nel proprio TX) + iniezione utterance a T sopra il parlato di Sara + capture rx/tx/mix.wav + transcript.md SOLO sotto `SARA_TEST_CAPTURE=1` (default OFF, verificare a fine). Scenario committato = regressione permanente.
- **FASE 3.2 GATE A3** done-condition (1-4) + **(4b) NUOVA silenzio-prolungato**: chiamante tace dopo il primo scambio → Sara fa il reprompt → chiude via timeout-silenzio → la call TERMINA (engine libero, zero call appese, log `HANGUP timeout-silenzio`). Artefatti in `.claude/cache/T-SARA-TURNTAKING/calls/<ts>_A3/`. Rosso → UNA iterazione etichettata (GATING/BARGE-IN/FSM-HANGUP/FILLER/IDLE) → ritest → STOP.
- Poi CHECKPOINT context → **FASE 4 GATE B3** founder (rituale 5 mosse; la PAUSA LUNGA ora deve produrre reprompt, non riaggancio immediato né silenzio eterno). Solo su VERDE-A3.

## 6. File toccati + backup #1d
| File | Backup iMac (#1d) | md5 post (local==iMac) |
|------|-------------------|------------------------|
| `voice-agent/src/voip_goengine.py` | `.bak-PRE-F30-20260708-193738` (33089B) | `4079e6bc…` |
