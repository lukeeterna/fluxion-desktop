# STEP 1 — FIX-OBS — Report
Date: 2026-07-17 | STEPDIR: vos/runs/20260717/1-FIX-OBS/

---

## (a) capture WAV — root cause e fix

### Root cause
`launch_rig.sh:57` (originale) non esportava `SARA_TEST_CAPTURE`:
```bash
# PRIMA (bug):
export VOIP_SIP_SERVER="$SIP_SERVER" VOICE_ENGINE=go VOIP_BRIDGE_PORT="$BRIDGE_PORT" VOIP_LOCAL_PORT="$LOCAL_PORT"
```

Sequenza di fallimento:
1. `launch_rig.sh` avvia `nohup python3 main.py` senza `SARA_TEST_CAPTURE` in env
2. `main.py:102` chiama `load_dotenv()` — python-dotenv NON sovrascrive env già presenti (default `override=False`), ma qui la var non era presente → non viene impostata
3. `GoEngineVoIPManager.__init__:188` → `self._capture = os.getenv("SARA_TEST_CAPTURE") == "1"` → `False`
4. Nessun WAV scritto in tutta la chiamata

### Fix applicato
`launch_rig.sh:57` (patch — file non tracciato, modificato in-place con bak):
```bash
# DOPO (fix):
export VOIP_SIP_SERVER="$SIP_SERVER" VOICE_ENGINE=go VOIP_BRIDGE_PORT="$BRIDGE_PORT" VOIP_LOCAL_PORT="$LOCAL_PORT" SARA_TEST_CAPTURE=1
```

Nota: `b3_open.sh:60` era già corretto (`VOICE_ENGINE=go SARA_TEST_CAPTURE=1 nohup $ARGV`) — inline env assignment fa override dell'exported env per quella singola invocazione.

### PROVA su rig (iMac, Python 3.9.6)
Test: `test_capture_unit.py` eseguito via `ssh imac 'python3 -' < test_capture_unit.py`

Output reale:
```
CHECK 1 PASS: _capture=True
CHECK 2 PASS: WAV scritto → /Volumes/MacSSD - Dati/FLUXION/.claude/cache/T-SARA-TURNTAKING/calls/call_UNIT-TEST-20260717.wav
CHECK 3 PASS: stereo 2ch @8000Hz 8000 frames (1.00s)
CHECK 4 PASS: rx_rms=2120 tx_rms=1413 (entrambi >0)

=== UNIT TEST WAV CAPTURE: TUTTI I CHECK PASS ===
WAV: /Volumes/MacSSD - Dati/FLUXION/.claude/cache/T-SARA-TURNTAKING/calls/call_UNIT-TEST-20260717.wav
  stereo 2ch @8kHz | rx_rms=2120 | tx_rms=1413
```

rx/tx/mix (stereo L=rx R=tx) confermati scritti con rms>0.

---

## (b) logger — stato e modifiche

### TTS≥160ch — AGGIUNTO (era assente)
File: `voice-agent/src/tts_engine.py`

**EdgeTTSEngine.synthesize()** — aggiunto prima dell'istanza `Communicate`:
```python
if len(text) >= 160:
    logger.warning(
        "[EdgeTTSEngine] testo lungo ≥160ch (%d chars): %r…",
        len(text), text[:50],
    )
```

**PiperTTSEngine.synthesize()** — aggiunto all'ingresso del metodo:
```python
if len(text) >= 160:
    logger.warning(
        "[PiperTTSEngine] testo lungo ≥160ch (%d chars): %r…",
        len(text), text[:50],
    )
```

### Timestamp fine-utterance — GIÀ PRESENTE
`voice-agent/src/voip_goengine.py:812-816`:
```python
logger.info(
    "risposta TTS in coda TX (%dB) | [TARATURA] latenza "
    "fine-utterance→audio-out=%.0fms",
    len(result["audio_response"]), (time.monotonic() - _t_endpoint) * 1000,
)
```

### Slot-result NLU per turno — GIÀ PRESENTE
`voice-agent/src/voip_goengine.py:800-806`:
```python
logger.info(
    "[TARATURA][SLOT] intent=%r servizio=%r servizio_id=%r slots=%r",
    result.get("intent"), result.get("servizio"),
    result.get("servizio_id"), result.get("slots"),
)
```

### Boot log reprompt-timer/VAD/soglia E6 — GIÀ PRESENTE
`voice-agent/src/voip_goengine.py:241-251`:
```python
logger.info(
    "[TARATURA][BOOT] reprompt_timer=%.1fs (voip_goengine.py:87) | "
    "vad_speech_threshold=%d rms (voip_goengine.py:58) | "
    "vad_silence_timeout=%d frame ~%dms endpointing (voip_goengine.py:59) | "
    "vad_min_speech_frames=%d ~%dms (voip_goengine.py:60) | "
    "E6_strike_threshold=3 (booking_state_machine.py:3086)",
    IDLE_REPROMPT_S, VAD_SPEECH_THRESHOLD,
    VAD_SILENCE_TIMEOUT, VAD_SILENCE_TIMEOUT * 20,
    VAD_MIN_SPEECH_FRAMES, VAD_MIN_SPEECH_FRAMES * 20,
)
```
Valori runtime: `reprompt_timer=22.0s | vad_speech_threshold=400 rms | vad_silence_timeout=50 frame ~1000ms | vad_min_speech_frames=15 ~300ms | E6_strike=3`

---

## (c) disclosure STATICA — audit read-only

### Template greeting VoIP (via start_session → session_manager.get_greeting)

**Chiamante nuovo** (`session_manager.py:744`):
```python
# AI-DISCLOSURE (founder GATE2): disclosure obbligatoria (EU AI Act art.50)
return f"{session.business_name}, {saluto.lower()}! Sono Sara, l'assistente virtuale. Come posso aiutarla?"
```
Esempio runtime (ora 20:xx): `"Salone Bella Vita, buonasera! Sono Sara, l'assistente virtuale. Come posso aiutarla?"`

**Chiamante di ritorno** (`session_manager.py:740`):
```python
return f"{session.business_name}, {saluto.lower()}! Bentornato {caller_name}, sono Sara, l'assistente virtuale. Come posso aiutarla?"
```

**Verdetto disclosure: SÌ**
Entrambi i template contengono `"sono Sara, l'assistente virtuale"` — disclosure AI conforme EU AI Act art.50 presente al primo utterance. Nessuna modifica al testo effettuata (audit only).

---

## Modifiche a git

| File | Tipo | Note |
|------|------|------|
| `voice-agent/src/tts_engine.py` | MODIFICA | TTS≥160ch warning aggiunto (2 metodi) |
| `vos/runs/20260717/1-FIX-OBS/test_capture_unit.py` | NUOVO | Prova WAV capture |
| `vos/runs/20260717/1-FIX-OBS/report.md` | NUOVO | Questo file |

File NON a git (non tracked):
- `.claude/cache/T-SARA-TURNTAKING/rig/launch_rig.sh` — SARA_TEST_CAPTURE=1 aggiunto a export

---

VERDICT: VERDE
