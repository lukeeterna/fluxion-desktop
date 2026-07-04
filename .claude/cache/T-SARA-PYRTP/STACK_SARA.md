# STACK_SARA — Inventario stack Voice Agent (per giudice, decisione MEDIASWAP vs Asterisk)

> Sorgente disco iMac `/Volumes/MacSSD - Dati/fluxion/voice-agent`, read-only, 2026-07-04.
> Ogni voce con file:riga. Baseline non toccata (Sara `reg_status:200` durante l'inventario).

## 1. SCOPO
Sara = receptionist telefonica INBOUND per PMI italiane. Riceve chiamate sul DID EHIWEB
0972536918 (trunk sip.vivavox.it), fa **booking appuntamenti** (FSM 23 stati), risponde a
**FAQ** e ha un ramo **sales**. health v2.1.0, "4-layer RAG" (main.py /health).

## 2. PIPELINE AUDIO E2E (catena reale)
`SIP/RTP pjsua2` → onFrameReceived (voip_pjsua2.py:208,:267) → **rx_queue** maxsize 500 (:214)
→ VAD (vad_wrapper.py + vad/ten_vad_integration.py) → **STT** (stt.py) → orchestrator.process
(orchestrator.py:906) livelli L0-L4 (:247-253) + **NLU Groq** (groq_nlu.py) + BookingStateMachine
→ **TTS** (tts_engine.py) → **queue_tts_audio** resample 16k→8k audioop.ratecv (:298-317)
→ onFrameRequested TX (:276-282).
- Formati giunzioni: RTP = **L16 PCM 16-bit, 8000 Hz mono** (:254 PJMEDIA_FORMAT_L16); interno
  Sara = 16000 Hz (ratecv 16000→8000 in TX :317). CONFERMATO L16/8k/mono al media-layer.

## 3. MOTORI
- **STT**: requirements/stt.py = `faster-whisper` (CTranslate2 int8) primary + Groq fallback
  (stt.py:4-7). **DISCORDANZA**: health runtime riporta engine `GroqSTT` → attivo a runtime è
  Groq cloud, non whisper locale. Gira: Groq cloud (attivo) / faster-whisper locale (disponibile).
- **TTS** 3-tier (tts_engine.py:6-7,:66-70,:153): EdgeTTS IsabellaNeural (cloud 9/10 ~500ms) /
  Piper it_IT-paola-medium .onnx locale (7/10 ~50ms, tts.py:452) / SystemTTS `say` (OS-native).
- **VAD**: vad_wrapper.py; health "silero-or-webrtc"; presente anche ten_vad (vad/).
- **NLU**: Groq `llama-3.3-70b-versatile` cloud (groq_nlu.py:26).
- **FSM**: BookingStateMachine 23 stati (booking_state_machine.py), param `vertical` default
  "salone", nominati **4**: salone/palestra/medical/auto (:176,:698,:707).

## 4. CONTRATTO MEDIA-LAYER — cosa voip_pjsua2.py fa OLTRE SIP+RTP (da rifare in un sostituto)
1. **Barge-in**: RMS TX tracking (:217,:278-279) + loop con BARGE_IN_MARGIN=500,
   THRESHOLD=4 frame (80ms), echo attenuation (:1127-1159).
2. **Greeting all'answer**: thread _send_greeting con numero chiamante (:1074-1077).
3. **Resample TX** 16k→8k audioop.ratecv (:298-317); RMS frame audioop (:287).
4. **Turn-taking VAD**: soglie tarate telefonia IT (:693,:1194-1196).
5. **Thread confinement S352** (fix crash): _register_thread_if_needed (:83,:433), lazy
   createPort in onCallMediaState (:240-248,:428).
6. **NAT**: ICE+STUN, sdpNatRewrite, contactRewrite (:952-954), TURN opt CGNAT (:959-965),
   UDP keepalive + re-registration SIP (:987).
7. Gestione stato chiamata onCallState (:391), rx drain (:338), clear_tx.
→ Un adapter (pyVoIP o Asterisk-bridge) deve rifare 1-4 (5-6 spariscono se il media-layer
  non è pjsua2; 6 lo fa il provider/Asterisk).

## 5. INTERFACCE ESTERNE
- **:3002** (main.py:382-424): /health, /api/voice/{greet,process,say,reset,status},
  /api/voice/voip/{status,hangup}, /api/metrics/latency, /api/tts/{hardware,mode},
  /api/voice/whatsapp/{callback,send_confirmation,register_pending}, /api/waitlist/trigger,
  /api/sales/{process,reset,status}, /api/voice/set-vertical, /api/supplier-orders/send-email.
- **Write-path → Tauri bridge** `127.0.0.1:3001/api/verticale/config` (main.py:305); :3002 fa
  da fallback config quando bridge offline (:244).
- **Analytics**: src/analytics.py (SQLite) → data/fluxion.db + data/vertical_dbs/*.db per verticale.
- **.env (solo nomi)**: VOIP_SIP_{USER,PASS,SERVER}, VOIP_SIP_PORT(=5060), VOIP_LOCAL_PORT
  (unset→5080), GROQ_* (key pool), SENTRY_DSN_PYTHON, TURN_* (opt).

## 6. DIPENDENZE
- Python **3.9.6** (/usr/bin/python3, system CommandLineTools).
- Pure Python / wheel PyPI: aiohttp, edge-tts, groq, rapidfuzz, jellyfish, python-Levenshtein,
  dateparser, psutil, sentry-sdk. Wheel NATIVE da PyPI: faster-whisper (ctranslate2),
  piper-tts (onnxruntime).
- **UNICA .so custom/bundled** = pjsua2: `lib/pjsua2/_pjsua2.cpython-39-darwin.so` (+ 2 backup).
  È l'anello nativo che MEDIASWAP eliminerebbe sostituendolo con pyVoIP (puro Python).

## 7. DELTA PROMESSA / IMPLEMENTATO
- FSM booking parametrizzata **4 verticali** (salone/palestra/medical/auto) vs data/KB con **12
  FAQ set** (altro,auto,barbiere,beauty,fisioterapia,gommista,medical,odontoiatra,palestra,
  salone,toelettatura,wellness) + vertical_dbs (auto,barbiere,beauty,fisioterapia,gommista,
  medical,odontoiatra,palestra…). CLAUDE.md dichiara 8-9 verticali venduti → **gap FSM(4) vs
  KB/venduti(8+)**: FAQ/dati coprono più verticali del flusso di booking guidato.

## AVVIO / RESTORE (piano)
- PID Sara live = 54563; cmd = `python3 main.py --port 3002` in cwd sopra.
- Restore: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup /usr/bin/python3 main.py --port 3002 >/tmp/sara.log 2>&1 &"` poi verifica health 200 + reg_status:200.
