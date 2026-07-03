# DOSSIER GIUDICE — T-SARA-AUTOCALL STEP 2-5 (esecuzione S1) — 2026-07-03

> File unico per il giudice: prompt eseguito + verdetto + report + sorgenti (runner+harness) + log grezzi S1.
> Commit sessione: `d7f4898` (su `6e7fb8c`). Stato: CHIUSO PARZIALE (S1 girato, resume da S2) a context 60%.

---

## 1. PROMPT ESEGUITO (task ricevuto)

TASK SINGOLO — T-SARA-AUTOCALL resume STEP 2-5: eseguire i 5 scenari multi-turn + overlap col runner GIÀ COMMITTATO (`tools/sara_autocall.py`, che riusa `sara_audio_harness.py` direct-INVITE). Niente subagent. NON toccare il trunk EHIWEB (riservato alla chiamata founder). Credenziali mai in chiaro.

Contratto di discordanza: ogni premessa cieca → PREMESSA→VERIFICA→AZIONE; se discorda «DISCORDANZA @ STEP n — PREMESSA | FATTO DISCO | CORREZIONE». Vince il disco. Ogni scenario è un'unità: se il context si avvicina alla soglia, chiudi DOPO lo scenario in corso, commit report parziale + HANDOFF con "resume da scenario N".

Pre-flight: :3002 health 200, :3001 LISTEN, Sara REGISTERED, PID annotato. Esecuzione S1→S5 (S1 cliente nuovo Gianfranco Sgueglia [Keychain/PII], S2 stress+barge-in, S3 palestra+prezzo, S4 medical+fallback, S5 auto). Dopo ogni scenario: PID Sara, appuntamento in DB (SELECT fonte='voice', NON cancellare), riga sintesi dialogo. Poi OVERLAP 2 chiamate. Report in `voice-agent/tools/AUTOCALL_REPORT.md` (tabella + P50/95/99 + ramo Keychain + trascrizioni STT vs copione). Chiusura: discordanze + verdetto (N completati/M crash + PRONTO CHIAMATA FOUNDER SÌ/NO) + VOS (HANDOFF + vos-close) + parere CC.

---

## 2. COSA HA FATTO CC (traccia esecuzione, verificabile)

1. **Delegation gate**: dichiarato `[inline]` motivato (task vieta subagent + orchestrazione SSH/Bash non delegabile, REGOLA #27).
2. **Pre-flight** (SSH iMac, servizi bind 127.0.0.1): `:3002/health`=200; `voip/status` **registered reg_status:200** user `0972536918`; `:3001` bridge ok pid 57494; **Sara PID baseline 54563**.
3. **Sync**: `git pull` su iMac (commit `6e7fb8c` presente); runner 14391B + harness 17749B presenti; **baseline voice bookings=3**, clienti=15 (PII cifrata).
4. **Interprete**: Py3.9.6 CommandLineTools con `import pjsua2` OK (3 candidati verificati).
5. **S1 eseguito** con guardia `perl -e "alarm 220; exec @ARGV"` (NON `timeout`), out `/tmp/autocall`, `--log-level 1`, stdout→file.
6. **Raccolta esito**: PID pre/post, DB count+righe, clienti, `autocall_summary.json`, WAV, `/api/metrics/latency` pre/post.
7. **Chiusura a context 60%** (contratto discordanza): report parziale `AUTOCALL_REPORT.md` + HANDOFF resume-da-S2 + commit `d7f4898` + `vos-close.sh` (push OK `6e7fb8c..d7f4898`). Sara lasciata UP reg 200, DB non toccato.

---

## 3. EVIDENZE GREZZE S1 (comandi → output reali)

**Pre-flight (SSH iMac):**
```
:3002/health → {"status":"ok","service":"FLUXION Voice Agent Enterprise","version":"2.1.0",...}
voip/status  → {"running":true,"sip":{"registered":true,"reg_status":200,"username":"0972536918","server":"sip.vivavox.it"},"rtp_active":false,"engine":"pjsua2"}
:3001/health → {"service":"FLUXION HTTP Bridge","status":"ok",...}
Sara PID (:3002 LISTEN) = 54563 ; :3001 LISTEN = 57494
baseline voice bookings = 3 ; clienti = 15 (cifrati)
```

**S1 run (perl alarm 220):**
```
PID_PRE=54563
EXIT=0
PID_POST=54563   ← NO CRASH (NDEBUG regge)
tail run log: ripetuti "lock.c !Assert failed: glock->owner == pj_thread_this()" (teardown endpoint harness, non-fatale sotto NDEBUG)
              + "pjsua_call_hangup ... INVITE session already terminated (PJSIP_ESESSIONTERMINATED)"
```

**Post-S1 DB + metriche:**
```
voice bookings count = 3   ← INVARIATO (nessun booking scritto)
clienti = 15               ← INVARIATO (Gianfranco Sgueglia NON creato; ramo Keychain/PII non esercitato)
/api/metrics/latency (pre e post) = {"p50_ms":0,"p95_ms":0,"p99_ms":0,"count":0}  ← Sara non ha processato ALCUN turno
Sara PID_NOW=54563 ; reg_status:200 (invariato, nessun danno)
```

---

## 4. VERDETTO PARZIALE + DISCORDANZA

**DISCORDANZA @ S1 — smoke green ≠ turno conversazionale.**
- PREMESSA (smoke HANDOFF): direct-INVITE regge → pronto per multi-turn+booking.
- FATTO DISCO: call **CONNECTED + media active**, Sara **sopravvive (no SIGABRT)**, MA `latency count=0`, `sara_heard:false`, 0 booking, 0 cliente → **la pipeline conversazionale di Sara NON viene esercitata**.
- CORREZIONE: il collo di bottiglia reale non è il crash, è il **media/RTP path**: l'audio non fluisce (harness→STT Sara e/o Sara→capture harness). Root cause candidata: direct-INVITE IP-to-IP negozia SDP ma il flusso RTP verso la STT non parte (a differenza dell'inbound provider autenticato di S244, che processava i turni).

**VERDETTO:** «5 SCENARI: 1 avviato (S1), 0 completati con booking, **0 crash**». «**PRONTO PER CHIAMATA FOUNDER (trunk+giudizio): NO**» — prima chiudere il gap RTP/turn-taking.

**RESUME da S2:** (1) diagnosi audio-flow del direct-INVITE (codec/ptime; `latency count` deve salire); (2) sblocco = 1 turno S1 con `count>0` E (`sara_heard:true` o booking); (3) se non colmabile in autonomia → escalation giudice/founder: stress-test via trunk EHIWEB (path S244 funzionante) vs direct-INVITE.

---

## 5. ALLEGATO — AUTOCALL_REPORT.md (committato)

```markdown
# AUTOCALL REPORT — T-SARA-AUTOCALL STEP 2-5 (PARZIALE)

> Runner `tools/sara_autocall.py` (direct-INVITE via `scripts/sara_audio_harness.py`, NO trunk EHIWEB).
> Sessione 2026-07-03. Chiuso a context 60% (vincolo #7) DOPO S1. **Resume da S2.**

## Pre-flight (VERDE)
- `:3002/health` 200; SIP **registered reg_status:200** (user `0972536918`, sip.vivavox.it, pjsua2).
- `:3001` bridge health ok (pid 57494).
- **Sara PID baseline = 54563** (riferimento no-crash).
- Runner sincronizzato su iMac (commit `6e7fb8c` pull OK). Interprete: CommandLineTools Py3.9.6, `pjsua2` importabile.
- Baseline voice bookings = **3** (atteso). Clienti = 15 (PII cifrata).

## Tabella scenari

| SCENARIO | completato | appuntamento DB (id) | crash | anomalie dialogo | durata | audio file |
|----------|-----------|----------------------|-------|------------------|--------|------------|
| S1 SALONE cliente NUOVO (Gianfranco Sgueglia) | connesso NO booking | nessuno (voice=3 invariato) | NO (PID 54563 pre==post) | `sara_heard:false` su 2/2 turni → fallback fisso 14s; call dropped before 'chiusura'; latency count=0 | 38.87s | `/tmp/autocall/S1_call.wav` (512044 B) |
| S2 | DA ESEGUIRE | — | — | — | — | — |
| S3 | DA ESEGUIRE | — | — | — | — | — |
| S4 | DA ESEGUIRE | — | — | — | — | — |
| S5 | DA ESEGUIRE | — | — | — | — | — |
| OVERLAP ×2 | DA ESEGUIRE | — | — | — | — | — |

## Latency `/api/metrics/latency`
- Pre S1: `p50=0 p95=0 p99=0 count=0`.
- Post S1: `p50=0 p95=0 p99=0 count=0` → **Sara non ha processato NESSUN turno** attraverso il path direct-INVITE.

## Ramo Keychain S1 (caveat GDPR)
- Cliente nuovo "Gianfranco Sgueglia" **NON creato** nel DB clienti (count 15 invariato, nessun `cli-` nuovo). Il ramo PII/Keychain **non è stato esercitato** perché Sara non ha processato il turno di apertura. Caveat GDPR resta **NON verificato**.

## Trascrizioni STT vs copione
- Copione S1 apertura: *"Buongiorno, non sono mai venuto da voi, mi chiamo Gianfranco Sgueglia, vorrei prenotare un taglio giovedì pomeriggio"*.
- STT lato Sara: **assente** (latency count=0, nessun turn log di comprensione). Il WAV catturato `S1_call.wav` è finestra fissa 512000 B PCM (contenuto Sara non confermato — probabile silenzio/no-RTP-decodato).

## DISCORDANZA @ S1 — smoke green ≠ turno conversazionale
- **PREMESSA** (da HANDOFF smoke): direct-INVITE regge → stack pronto per stress multi-turn con booking.
- **FATTO DISCO**: il call si CONNETTE e Sara **sopravvive (no SIGABRT, NDEBUG regge)**, ma la pipeline conversazionale **non viene esercitata**: `latency count=0`, `sara_heard=false`, zero booking, zero cliente. Il de-risk provato dallo smoke = "lo stack non crasha su 1 INVITE", NON "Sara conversa e prenota via questo path".
- **CORREZIONE**: prima di girare S2-S5 serve chiudere il gap RTP: (a) Sara riceve RTP decodabile dall'harness? (codec/ptime negoziati); (b) la silence-detection `audioop.rms ≥0.8s` dell'harness misura l'RTP di Sara o solo il proprio TX? `sara_heard:false` + `count=0` puntano a **audio non fluito Sara→harness E/O harness→Sara**. Root cause candidata: il direct-INVITE IP-to-IP negozia media ma il flusso RTP audio effettivo verso la STT di Sara non parte (a differenza dell'inbound autenticato provider di S244).

## VERDETTO PARZIALE
- **5 SCENARI: 1 avviato (S1), 0 completati con booking, 0 crash.**
- **PRONTO PER CHIAMATA FOUNDER (trunk + giudizio): NO** — prima chiudere il gap RTP/turn-taking (Sara non processa turni sul path auto). Lo stack sopravvive ma non dimostra ancora conversazione+booking end-to-end in autonomia.

```

## 6. ALLEGATO — autocall_summary.json (grezzo S1)

```json
[
  {
    "scenario": "S1",
    "name": "SALONE cliente NUOVO",
    "connected": true,
    "turns": [
      {
        "label": "apertura",
        "mode": "normal",
        "text": "Buongiorno, non sono mai venuto da voi, mi chiamo Gianfranco Sgueglia, vorrei prenotare un taglio giovedì pomeriggio",
        "sara_heard": false,
        "wait_s": 14.04,
        "reason": "fixed_fallback",
        "ts": 1.22
      },
      {
        "label": "conferma",
        "mode": "normal",
        "text": "Va bene, perfetto",
        "sara_heard": false,
        "wait_s": 14.04,
        "reason": "fixed_fallback",
        "ts": 23.14
      }
    ],
    "capture": "/tmp/autocall/S1_call.wav",
    "capture_pcm_bytes": 512000,
    "duration_s": 38.87
  }
]
```

## 7. ALLEGATO — S1.run.log (filtrato: rimosse le righe Assert/lock.c ripetute)

```
[19:23:27.750] endpoint up on UDP :5070; scenarios: ['S1']
[19:23:27.751] === S1 [SALONE cliente NUOVO] dialing sip:0972536918@127.0.0.1:5080 ===
[19:23:27.820] S1: CONNECTED, media active. Driving 3 turns.
19:23:27.703         os_core_unix.c !pjlib 2.17-dev for POSIX initialized
19:23:27.703         sip_endpoint.c  .Creating endpoint instance...
19:23:27.703                  pjlib  .select() I/O Queue created (0x7f9f650f5e18)
19:23:27.703         sip_endpoint.c  .Module "mod-msg-print" registered
19:23:27.703        sip_transport.c  .Transport manager created.
19:23:27.703           pjsua_core.c  .PJSUA state changed: NULL --> CREATED
19:23:28.711       .[19:23:28.970] S1 > [apertura/normal] speak: 'Buongiorno, non sono mai venuto da voi, mi chiamo Gianfranco Sgueglia, vorrei prenotare un taglio giovedì pomeriggio'
failed: glock->owner == pj_thread_this()
d_this()
[19:24:06.623] S1: call dropped before turn 'chiusura'
[19:24:06.625] S1: captured 512000 PCM bytes -> /tmp/autocall/S1_call.wav (32.00s)
[19:24:09.653] SUMMARY -> /tmp/autocall/autocall_summary.json
[
  {
    "scenario": "S1",
    "name": "SALONE cliente NUOVO",
    "connected": true,
    "turns": [
      {
        "label": "apertura",
        "mode": "normal",
        "text": "Buongiorno, non sono mai venuto da voi, mi chiamo Gianfranco Sgueglia, vorrei prenotare un taglio giovedì pomeriggio",
        "sara_heard": false,
        "wait_s": 14.04,
        "reason": "fixed_fallback",
        "ts": 1.22
      },
      {
        "label": "conferma",
        "mode": "normal",
        "text": "Va bene, perfetto",
        "sara_heard": false,
        "wait_s": 14.04,
        "reason": "fixed_fallback",
        "ts": 23.14
      }
    ],
    "capture": "/tmp/autocall/S1_call.wav",
    "capture_pcm_bytes": 512000,
    "duration_s": 38.87
  }
]
ert failed: glock->owner == pj_thread_this()
19:24:06.623               call.cpp !pjsua_call_hangup(id, prm.statusCode, param.p_reason, param.p_msg_data) error: INVITE session already terminated (PJSIP_ESESSIONTERMINATED) (status=171140) [../src/pjsua2/call.cpp:799]

```

## 8. ALLEGATO — SORGENTE runner tools/sara_autocall.py

```python
#!/usr/bin/env python3
"""sara_autocall.py — T-SARA-AUTOCALL v2 multi-turn SIP stress-test driver.

Automates the "AINEC" conversational counterpart: places REAL SIP calls to
Sara and drives a full multi-turn dialogue, then verifies survival + booking.

ARCHITECTURE (reuses scripts/sara_audio_harness.py — the surviving residual)
---------------------------------------------------------------------------
Sara is an INBOUND-only pjsua2 UA; the STT path lives inside pjsua2/RTP, so the
only way to feed real speech is a SIP call carrying our audio over RTP. This
driver brings up its OWN pjsua2 endpoint and places a DIRECT IP-to-IP INVITE to
Sara (sip:<user>@<iMac>:5080) — it does NOT register with the provider and does
NOT traverse EHIWEB. => no second REGISTER, Sara's provider registration is
untouched (she is NOT kicked). This is the "tutto-auto" flow. The TRUNK-real
path (through EHIWEB / PSTN / G729) is reserved for the founder judgment call.

Proven in T-SARA-AUTOCALL smoke (2026-07-03): single-utterance harness → Sara
answered, 11.6s reply captured over RTP, Sara PID stable, EXIT=0. The historic
lock.c:279 assert now only prints (non-fatal) under the NDEBUG pjsua2 build and
appears only in the HARNESS endpoint teardown, not Sara.

TURN-TAKING
-----------
Per turn: render the line with macOS `say` (a voice DIFFERENT from Sara's) +
afconvert to PCM16/8k/mono, stream it over RTP, then wait for Sara to finish
speaking — detected by RTP-silence >= --min-silence seconds (audioop RMS on the
captured RX frames), capped by --max-reply; fallback to a fixed pause if no
audio is ever heard. A turn tagged "barge" overlaps Sara on purpose: it starts
speaking after only --barge-after seconds instead of waiting for silence.

The WHOLE call RX is written to one WAV per scenario for later transcription.
Sara-process liveness (no SIGABRT), reg_status, and the appuntamenti DB row are
verified by the SHELL wrapper around this script, not here — a crash here must
still leave the DB/log evidence intact.

RUN (on the iMac, with the bundled interpreter)
-----------------------------------------------
    cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
    PY=/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/\
Versions/3.9/Resources/Python.app/Contents/MacOS/Python
    "$PY" tools/sara_autocall.py --sara-ip 127.0.0.1 --scenario S1 \
        --out-dir /tmp/autocall
    # or --scenario all  to run S1..S5 sequentially (one call each)
"""

import argparse
import audioop
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Reuse the proven harness (same dir layout: tools/ is sibling of scripts/).
_TOOLS_DIR = Path(__file__).resolve().parent
_VOICE_AGENT_DIR = _TOOLS_DIR.parent
sys.path.insert(0, str(_VOICE_AGENT_DIR / "scripts"))
sys.path.insert(0, str(_VOICE_AGENT_DIR / "lib" / "pjsua2"))

import pjsua2 as pj  # noqa: E402
from sara_audio_harness import (  # noqa: E402
    HarnessAudioPort,
    HarnessAccount,
    generate_wav_from_text,
    read_wav_pcm,
)

FRAME_BYTES = 320  # 20ms @ 8kHz mono 16-bit
SILENCE_RMS = 400  # audioop.rms threshold below which we call it "silence"

# ---------------------------------------------------------------------------
# Scenarios. Each turn: (label, text, mode). mode in {"normal","barge"}.
# "barge" overlaps Sara (starts next line without waiting for her to finish).
# ---------------------------------------------------------------------------
SCENARIOS = {
    "S1": ("SALONE cliente NUOVO", [
        ("apertura", "Buongiorno, non sono mai venuto da voi, mi chiamo Gianfranco Sgueglia, vorrei prenotare un taglio giovedì pomeriggio", "normal"),
        ("conferma", "Va bene, perfetto", "normal"),
        ("chiusura", "La ringrazio, arrivederci", "normal"),
    ]),
    "S2": ("SALONE stress (cambio idea + barge-in + data ambigua)", [
        ("richiesta", "Vorrei fare un colore", "normal"),
        ("ripensamento", "No aspetti, meglio solo una piega", "normal"),
        ("data_ambigua", "Mercoledì... anzi no, facciamo venerdì", "normal"),
        ("data_conferma", "Giovedì prossimo va bene?", "normal"),
        ("bargein", "Scusi, un'ultima cosa", "barge"),
        ("chiusura", "Va bene così, grazie", "normal"),
    ]),
    "S3": ("PALESTRA (KB vendita fuori copione)", [
        ("apertura", "Salve, vorrei informazioni per una prova gratuita", "normal"),
        ("orari", "Preferirei orari serali", "normal"),
        ("prezzo", "Ma quanto costa al mese?", "normal"),
        ("chiusura", "Va bene, grazie", "normal"),
    ]),
    "S4": ("MEDICAL (data formato strano + fallback)", [
        ("apertura", "Buongiorno, dovrei prenotare una visita", "normal"),
        ("data", "Il quindici, di mattina presto", "normal"),
        ("fuori_copione", "Posso portare le analisi vecchie?", "normal"),
        ("chiusura", "D'accordo, grazie", "normal"),
    ]),
    "S5": ("AUTO (servizio reale 'tagliando')", [
        ("apertura", "Salve, dovrei fare il tagliando alla macchina", "normal"),
        ("data", "Anche la settimana prossima va bene", "normal"),
        ("chiusura", "Perfetto, grazie", "normal"),
    ]),
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}", flush=True)


class MultiTurnCall(pj.Call):
    """Outbound call that drives many turns on ONE HarnessAudioPort."""

    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        self.audio_port = HarnessAudioPort()
        self.connected = False
        import threading
        self.done = threading.Event()

    def onCallState(self, prm):
        ci = self.getInfo()
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.connected = True
        elif ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.connected = False
            self.done.set()

    def onCallMediaState(self, prm):
        try:
            ci = self.getInfo()
            for mi in ci.media:
                if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    self.audio_port.ensure_port()
                    call_audio = self.getAudioMedia(mi.index)
                    call_audio.startTransmit(self.audio_port)
                    self.audio_port.startTransmit(call_audio)
        except pj.Error as exc:
            sys.stderr.write(f"onCallMediaState wiring error: {exc}\n")


def _rx_rms_recent(port, from_idx):
    """RMS over rx frames captured since index from_idx (16-bit mono)."""
    frames = port.rx_chunks[from_idx:]
    if not frames:
        return 0
    pcm = b"".join(frames)
    try:
        return audioop.rms(pcm, 2)
    except audioop.error:
        return 0


def wait_for_sara_silence(ep, port, min_silence, max_wait, fixed_fallback):
    """Pump events until Sara stops (RTP-silence >= min_silence) or max_wait.

    Requires we heard *some* audio first; if none arrives, wait fixed_fallback.
    Returns dict with heard(bool), waited(s).
    """
    start = time.time()
    heard = False
    silence_start = None
    last_idx = len(port.rx_chunks)
    while time.time() - start < max_wait:
        ep.libHandleEvents(20)
        now = time.time()
        cur = len(port.rx_chunks)
        window_rms = _rx_rms_recent(port, max(last_idx, cur - 10))  # ~last 200ms
        if window_rms >= SILENCE_RMS:
            heard = True
            silence_start = None
        else:
            if heard:
                if silence_start is None:
                    silence_start = now
                elif now - silence_start >= min_silence:
                    return {"heard": True, "waited": round(now - start, 2), "reason": "silence"}
        last_idx = cur
        time.sleep(0.02)
    if not heard:
        # never heard Sara: give the fixed fallback pause a chance
        extra = max(0.0, fixed_fallback - (time.time() - start))
        t2 = time.time()
        while time.time() - t2 < extra:
            ep.libHandleEvents(20)
            time.sleep(0.02)
    return {"heard": heard, "waited": round(time.time() - start, 2),
            "reason": "silence" if heard else "fixed_fallback"}


def run_scenario(ep, acc, sid, args):
    name, turns = SCENARIOS[sid]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    capture = out_dir / f"{sid}_call.wav"
    turnlog = []

    target = f"sip:{args.sara_user}@{args.sara_ip}:{args.sara_port}"
    log(f"=== {sid} [{name}] dialing {target} ===")
    call = MultiTurnCall(acc)
    t0 = time.time()
    call.makeCall(target, pj.CallOpParam(True))

    # Wait for CONFIRMED (media active) up to connect timeout.
    ct = time.time() + args.connect_timeout
    while time.time() < ct and not call.connected and not call.done.is_set():
        ep.libHandleEvents(20)
        time.sleep(0.02)
    if not call.connected:
        log(f"{sid}: NOT CONNECTED (Sara did not answer / no media). state done={call.done.is_set()}")
        try:
            call.hangup(pj.CallOpParam(True))
        except pj.Error:
            pass
        return {"scenario": sid, "name": name, "connected": False,
                "turns": turnlog, "capture": str(capture), "duration_s": round(time.time() - t0, 2)}

    log(f"{sid}: CONNECTED, media active. Driving {len(turns)} turns.")
    for label, text, mode in turns:
        if call.done.is_set():
            log(f"{sid}: call dropped before turn '{label}'")
            break
        wav = str(out_dir / f"{sid}_{label}.wav")
        generate_wav_from_text(text, wav)
        pcm, _, _, _ = read_wav_pcm(wav)
        call.audio_port._tx_done.clear()
        call.audio_port.load_wav(pcm)
        turn_t = time.time()
        log(f"{sid} > [{label}/{mode}] speak: {text!r}")
        # play out our TX
        tx_deadline = time.time() + args.max_reply
        while not call.audio_port.tx_finished() and time.time() < tx_deadline and not call.done.is_set():
            ep.libHandleEvents(20)
            time.sleep(0.02)
        if mode == "barge":
            # overlap Sara: brief wait, then go to next turn immediately
            bt = time.time()
            while time.time() - bt < args.barge_after and not call.done.is_set():
                ep.libHandleEvents(20)
                time.sleep(0.02)
            res = {"heard": None, "waited": round(time.time() - bt, 2), "reason": "barge"}
        else:
            res = wait_for_sara_silence(ep, call.audio_port,
                                        args.min_silence, args.max_reply, args.fixed_pause)
        turnlog.append({"label": label, "mode": mode, "text": text,
                        "sara_heard": res["heard"], "wait_s": res["waited"],
                        "reason": res["reason"], "ts": round(turn_t - t0, 2)})
        log(f"{sid} < Sara {res['reason']} (heard={res['heard']}, {res['waited']}s)")

    try:
        call.hangup(pj.CallOpParam(True))
    except pj.Error:
        pass
    hd = time.time() + 3
    while time.time() < hd and not call.done.is_set():
        ep.libHandleEvents(20)
        time.sleep(0.02)

    nbytes = call.audio_port.write_capture(str(capture))
    log(f"{sid}: captured {nbytes} PCM bytes -> {capture} ({nbytes/16000:.2f}s)")
    return {"scenario": sid, "name": name, "connected": True, "turns": turnlog,
            "capture": str(capture), "capture_pcm_bytes": nbytes,
            "duration_s": round(time.time() - t0, 2)}


def build_endpoint(args):
    ep = pj.Endpoint()
    ep.libCreate()
    cfg = pj.EpConfig()
    cfg.uaConfig.userAgent = "FLUXION-Autocall/2.0"
    cfg.uaConfig.threadCnt = 0
    cfg.uaConfig.mainThreadOnly = True
    cfg.medConfig.noVad = True
    cfg.medConfig.srtpUse = 0
    cfg.logConfig.consoleLevel = args.log_level  # keep quiet by default
    cfg.logConfig.level = args.log_level
    ep.libInit(cfg)
    tp = pj.TransportConfig()
    tp.port = args.local_port
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp)
    ep.libStart()
    ep.audDevManager().setNullDev()
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = f"sip:autocall@{args.local_ip}:{args.local_port}"
    acc = HarnessAccount()
    acc.create(acc_cfg)
    return ep, acc


def build_parser():
    p = argparse.ArgumentParser(description="Multi-turn SIP stress-test of Sara.")
    p.add_argument("--scenario", default="all",
                   help="S1|S2|S3|S4|S5|all (sequential, one call each)")
    p.add_argument("--sara-ip", default=os.getenv("SARA_IP", "127.0.0.1"))
    p.add_argument("--sara-port", type=int, default=int(os.getenv("SARA_SIP_PORT", "5080")))
    p.add_argument("--sara-user", default=os.getenv("VOIP_SIP_USER", "0972536918"))
    p.add_argument("--local-ip", default=os.getenv("HARNESS_IP", "127.0.0.1"))
    p.add_argument("--local-port", type=int, default=int(os.getenv("HARNESS_SIP_PORT", "5070")))
    p.add_argument("--out-dir", default="/tmp/autocall")
    p.add_argument("--connect-timeout", type=float, default=15.0)
    p.add_argument("--min-silence", type=float, default=0.8, help="RTP-silence to call Sara done")
    p.add_argument("--max-reply", type=float, default=14.0, help="cap wait per Sara reply")
    p.add_argument("--fixed-pause", type=float, default=7.0, help="fallback if no audio heard")
    p.add_argument("--barge-after", type=float, default=2.0, help="overlap window for barge turns")
    p.add_argument("--log-level", type=int, default=1, help="pjsua2 console log level (0-6)")
    return p


def main():
    args = build_parser().parse_args()
    order = list(SCENARIOS.keys()) if args.scenario == "all" else [args.scenario]
    for sid in order:
        if sid not in SCENARIOS:
            log(f"unknown scenario {sid}; skipping")
    ep, acc = build_endpoint(args)
    log(f"endpoint up on UDP :{args.local_port}; scenarios: {order}")
    results = []
    try:
        for sid in order:
            if sid not in SCENARIOS:
                continue
            results.append(run_scenario(ep, acc, sid, args))
            time.sleep(2)  # settle between calls
    finally:
        ep.libDestroy()
    summary = Path(args.out_dir) / "autocall_summary.json"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    log(f"SUMMARY -> {summary}")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

```

## 9. ALLEGATO — SORGENTE harness scripts/sara_audio_harness.py

```python
#!/usr/bin/env python3
"""
sara_audio_harness.py — Second SIP endpoint to drive Sara via REAL audio.

PURPOSE
-------
Sara (voice-agent) is an INBOUND-only SIP user agent built on pjsua2
(`src/voip_pjsua2.py`). The STT path lives INSIDE pjsua2/RTP: the only way to
feed real speech to Sara is to place a SIP call whose RTP carries our audio.
There is NO HTTP endpoint that accepts audio (`/api/voice/process` is text-only;
`/api/voice/say` is TTS-out only).

This harness is the missing SECOND SIP leg. It:
  1. Brings up its OWN pjsua2 endpoint on a separate local UDP port.
  2. Places an OUTBOUND INVITE toward Sara.
  3. Streams a WAV (PCM16 8kHz mono) over RTP to Sara.
  4. Captures Sara's RTP-in answer to a WAV file for verification/transcription.

KEY ARCHITECTURAL DECISION — DIRECT IP-to-IP INVITE (bypass provider)
---------------------------------------------------------------------
Sara's SIP transport listens on UDP *:VOIP_LOCAL_PORT (default 5080, confirmed
at runtime: `Python … UDP *:5080`). pjsua2 answers ANY incoming INVITE that
reaches that socket via SaraAccount.onIncomingCall — there is NO check that the
account is registered with the provider before accepting an inbound call.

Therefore this harness dials Sara DIRECTLY by IP:port, e.g.

    sip:0972536918@<IMAC_IP>:5080

This does NOT traverse EHIWEB/sip.vivavox.it and does NOT require the provider
REGISTER to succeed. It is a peer-to-peer INVITE on the LAN (or loopback if run
on the iMac itself). => The provider being down (SIP 403) does NOT block this
test path.  This is the whole point: it unblocks live audio testing of Sara
WITHOUT waiting for EHIWEB.

  TODO[SIP-LIVE]: This direct-INVITE assumption is verified by code-reading
  (onIncomingCall has no registration gate) but NOT yet end-to-end. The one
  thing that must be confirmed on a live run: that pjsua2 routes an INVITE whose
  Request-URI host is the iMac IP (not sip.vivavox.it) to SaraAccount. If pjsua2
  rejects it (404 / no matching account), fall back to setting the harness's
  outbound proxy to the iMac and dialing the account's idUri.

WAV GENERATION (verified live in S334 / re-verified this session)
-----------------------------------------------------------------
    say -o raw.aiff "testo italiano"
    afconvert -f WAVE -d LEI16@8000 -c 1 raw.aiff out.wav
  => afinfo: "1 ch, 8000 Hz, Int16"  == PCM16 8kHz mono == RTP-ready.

RUNTIME REQUIREMENTS (verified offline this session)
----------------------------------------------------
  - pjsua2 is importable ONLY with the bundled module under voice-agent/lib/.
    Run with:  PYTHONPATH=lib <CommandLineTools-Python3.9> scripts/sara_audio_harness.py
    (bare `python3` / venv python => ModuleNotFoundError: pjsua2)
  - Use a DIFFERENT local SIP port than Sara (5080) and a different RTP range,
    or pjsua2 transportCreate will fail to bind.

USAGE (once SIP path is exercised)
----------------------------------
    PYTHONPATH=lib /Library/Developer/CommandLineTools/.../Python \
        scripts/sara_audio_harness.py \
        --sara-ip 192.168.1.12 --sara-port 5080 \
        --sara-user 0972536918 \
        --say "Buongiorno, vorrei prenotare un taglio per domani" \
        --capture /tmp/sara_reply.wav
"""

import argparse
import os
import queue
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

# ---------------------------------------------------------------------------
# pjsua2 import — bundled under voice-agent/lib/pjsua2 (SWIG shim + _pjsua2.so).
#
# Verified offline this session: the working sys.path entry is
#   <voice-agent>/lib/pjsua2   (NOT <voice-agent>/lib)
# so that `import pjsua2` finds the SWIG shim which then `import _pjsua2`
# (the .so in the same dir). _pjsua2.so resolves its sibling dylibs via
# @loader_path (already patched, see scripts/fix_pjsua2_loader_path.sh).
# With lib/pjsua2 on the path all symbols resolve (AudioMediaPort/Call/
# CallOpParam/MediaFormatAudio == True). Putting only `lib` on the path
# loads an empty package and every pj.* attribute is missing.
#
# Bare python3 / venv python lack pjsua2 entirely. Use the CommandLineTools
# 3.9 interpreter the pipeline runs with.
# ---------------------------------------------------------------------------
_HARNESS_DIR = Path(__file__).resolve().parent          # voice-agent/scripts
_VOICE_AGENT_DIR = _HARNESS_DIR.parent                  # voice-agent
_PJSUA2_DIR = _VOICE_AGENT_DIR / "lib" / "pjsua2"
if _PJSUA2_DIR.is_dir():
    sys.path.insert(0, str(_PJSUA2_DIR))

try:
    import pjsua2 as pj
except ImportError as exc:  # pragma: no cover - environment guard
    sys.stderr.write(
        "ERROR: cannot import pjsua2.\n"
        "Run with the bundled lib on PYTHONPATH and the CommandLineTools 3.9 "
        "interpreter that the pipeline uses, e.g.:\n"
        "  PYTHONPATH=lib /Library/Developer/CommandLineTools/Library/Frameworks/"
        "Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python "
        "scripts/sara_audio_harness.py ...\n"
        f"(import error: {exc})\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# WAV helpers — generation (say+afconvert) and validation.
# ---------------------------------------------------------------------------
def generate_wav_from_text(text: str, out_path: str) -> str:
    """Render Italian text to PCM16 8kHz mono WAV using macOS say + afconvert.

    This is the exact recipe verified live in S334:
        say -o raw.aiff "<text>"
        afconvert -f WAVE -d LEI16@8000 -c 1 raw.aiff out.wav
    """
    aiff = out_path + ".raw.aiff"
    subprocess.run(["say", "-o", aiff, text], check=True)
    subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16@8000", "-c", "1", aiff, out_path],
        check=True,
    )
    try:
        os.remove(aiff)
    except OSError:
        pass
    return out_path


def read_wav_pcm(path: str):
    """Read a WAV file, returning (pcm_bytes, sample_rate, channels, sampwidth).

    Asserts the format is the RTP-ready shape (8kHz / mono / 16-bit). Raises if
    not — better to fail loud than feed Sara mis-rated audio (pitch/aliasing).
    """
    with wave.open(path, "rb") as wf:
        rate = wf.getframerate()
        ch = wf.getnchannels()
        width = wf.getsampwidth()
        pcm = wf.readframes(wf.getnframes())
    if (rate, ch, width) != (8000, 1, 2):
        raise ValueError(
            f"WAV {path} is {ch}ch/{rate}Hz/{width*8}bit, expected mono/8000/16. "
            "Regenerate with: afconvert -f WAVE -d LEI16@8000 -c 1 in.aiff out.wav"
        )
    return pcm, rate, ch, width


# ---------------------------------------------------------------------------
# Audio media port: streams OUR WAV out, captures Sara's RTP-in to a queue.
#
# Mirrors the shape of SaraAudioPort in src/voip_pjsua2.py:
#   - onFrameRequested: pjsua2 pulls a 20ms frame to SEND  -> our WAV chunks
#   - onFrameReceived:  pjsua2 hands us a 20ms frame it RECEIVED -> capture
# ---------------------------------------------------------------------------
class HarnessAudioPort(pj.AudioMediaPort):
    """Plays our WAV toward Sara and records Sara's reply."""

    FRAME_BYTES = 320  # 20ms @ 8kHz mono 16-bit (160 samples * 2 bytes)

    def __init__(self):
        super().__init__()
        # TX: our speech to Sara. Pre-chunked 20ms frames.
        self.tx_queue: "queue.Queue[bytes]" = queue.Queue()
        # RX: Sara's speech back to us. Captured for WAV write / STT.
        self.rx_chunks: list = []
        self._silence = b"\x00" * self.FRAME_BYTES
        self._thread_local = threading.local()
        self._tx_done = threading.Event()
        self._port_created = False

    def _ensure_thread_registered(self):
        # Same pattern as SaraAudioPort: pjlib audio worker threads are not
        # auto-registered; register once per worker thread.
        if getattr(self._thread_local, "registered", False):
            return
        try:
            pj.Endpoint.instance().libRegisterThread(
                f"harness_audio_cb_{threading.get_ident()}"
            )
            self._thread_local.registered = True
        except pj.Error:
            self._thread_local.registered = True

    def ensure_port(self):
        """Lazy createPort — deferred to onCallMediaState (mirrors SaraAudioPort).

        Format ID 0x2036314C = PJMEDIA_FORMAT_L16; 8kHz, mono, 20ms, 16-bit.
        """
        if self._port_created:
            return
        fmt = pj.MediaFormatAudio()
        fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
        self.createPort("harness_bridge", fmt)
        self._port_created = True

    def load_wav(self, pcm: bytes):
        """Chunk PCM16/8k/mono into 20ms frames and enqueue for TX."""
        for i in range(0, len(pcm), self.FRAME_BYTES):
            chunk = pcm[i:i + self.FRAME_BYTES]
            if len(chunk) < self.FRAME_BYTES:
                chunk = chunk + b"\x00" * (self.FRAME_BYTES - len(chunk))
            self.tx_queue.put(chunk)

    def onFrameRequested(self, frame):
        """pjsua2 wants a frame to SEND to Sara -> next WAV chunk or silence."""
        self._ensure_thread_registered()
        try:
            chunk = self.tx_queue.get_nowait()
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(chunk)
        except queue.Empty:
            if not self._tx_done.is_set():
                self._tx_done.set()
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(self._silence)

    def onFrameReceived(self, frame):
        """pjsua2 hands us a frame RECEIVED from Sara -> capture it."""
        self._ensure_thread_registered()
        if frame.type == pj.PJMEDIA_FRAME_TYPE_AUDIO:
            self.rx_chunks.append(bytes(frame.buf))

    def tx_finished(self) -> bool:
        return self._tx_done.is_set()

    def write_capture(self, path: str):
        """Write captured Sara reply (PCM16/8k/mono) to a WAV for review/STT."""
        pcm = b"".join(self.rx_chunks)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes(pcm)
        return len(pcm)


# ---------------------------------------------------------------------------
# Harness call + account.
# ---------------------------------------------------------------------------
class HarnessCall(pj.Call):
    """Outbound call leg that bridges HarnessAudioPort to Sara."""

    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        self.audio_port = HarnessAudioPort()
        self.connected = False
        self.done = threading.Event()

    def onCallState(self, prm):
        ci = self.getInfo()
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.connected = True
        elif ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.connected = False
            self.done.set()

    def onCallMediaState(self, prm):
        """Wire our audio port to the call's audio media (bidirectional).

        NOTE: src/voip_pjsua2.py defers startTransmit OUTSIDE the callback
        (S243 T1/T1.5) to avoid a pjmedia group-lock owner-thread assertion
        under threadCnt=0/mainThreadOnly. For the harness we keep it inline as
        a FIRST cut; if we hit the same lock.c:279 assertion on live run, port
        the deferred-bridge pattern from SaraAccount.drain_pending_bridges().
        """
        # TODO[SIP-LIVE]: validate bridge wiring + lock behavior on real call.
        try:
            ci = self.getInfo()
            for mi in ci.media:
                if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    self.audio_port.ensure_port()
                    call_audio = self.getAudioMedia(mi.index)
                    # Sara reply -> our port (capture); our WAV -> Sara.
                    call_audio.startTransmit(self.audio_port)
                    self.audio_port.startTransmit(call_audio)
        except pj.Error as exc:
            sys.stderr.write(f"onCallMediaState wiring error: {exc}\n")


class HarnessAccount(pj.Account):
    """Local-only account for the harness (no provider registration)."""

    def __init__(self):
        super().__init__()

    def onRegState(self, prm):
        # We do NOT register with a provider. If an idUri without registrarUri
        # is used, pjsua2 still allows outbound calls from this account.
        pass


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------
def run_harness(args) -> int:
    # 1. Prepare the WAV we will speak to Sara.
    if args.wav:
        wav_path = args.wav
    else:
        wav_path = "/tmp/harness_say.wav"
        generate_wav_from_text(args.say, wav_path)
    pcm, _, _, _ = read_wav_pcm(wav_path)  # asserts 8k/mono/16-bit
    print(f"[harness] TX WAV: {wav_path} ({len(pcm)} PCM bytes, "
          f"{len(pcm)/16000:.2f}s)")

    # 2. Bring up our OWN pjsua2 endpoint on a separate local port.
    ep = pj.Endpoint()
    ep.libCreate()
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.userAgent = "FLUXION-Harness/1.0"
    # Match Sara's headless tuning: single-thread dispatch, null audio device.
    ep_cfg.uaConfig.threadCnt = 0
    ep_cfg.uaConfig.mainThreadOnly = True
    ep_cfg.medConfig.noVad = True
    ep_cfg.medConfig.srtpUse = 0
    ep.libInit(ep_cfg)

    tp_cfg = pj.TransportConfig()
    tp_cfg.port = args.local_port  # MUST differ from Sara's 5080
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)
    ep.libStart()
    ep.audDevManager().setNullDev()  # headless: no mic/speaker
    print(f"[harness] pjsua2 endpoint up on UDP :{args.local_port}")

    # 3. Local account (no provider REGISTER).
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = f"sip:harness@{args.local_ip}:{args.local_port}"
    acc = HarnessAccount()
    acc.create(acc_cfg)

    # 4. Place DIRECT IP-to-IP INVITE to Sara — bypasses EHIWEB entirely.
    #    Request-URI host = Sara's iMac IP:port, NOT sip.vivavox.it.
    target = f"sip:{args.sara_user}@{args.sara_ip}:{args.sara_port}"
    print(f"[harness] dialing Sara DIRECT (no provider): {target}")
    call = HarnessCall(acc)
    call.audio_port.load_wav(pcm)
    call_prm = pj.CallOpParam(True)
    # TODO[SIP-LIVE]: makeCall + media negotiation only validated on a live run.
    #   If Sara replies 404/488, retry with acc outbound proxy = iMac, or dial
    #   Sara's account idUri (sip:0972536918@sip.vivavox.it) routed via proxy.
    call.makeCall(target, call_prm)

    # 5. Pump pjsua2 events (single-thread model => we drive libHandleEvents).
    deadline = time.time() + args.timeout
    spoke_done_at = None
    while time.time() < deadline and not call.done.is_set():
        ep.libHandleEvents(20)
        if call.connected and call.audio_port.tx_finished() and spoke_done_at is None:
            spoke_done_at = time.time()
            print("[harness] finished speaking; capturing Sara reply...")
        # Hang up a few seconds after we finish speaking + Sara had time to reply.
        if spoke_done_at and (time.time() - spoke_done_at) > args.reply_window:
            print("[harness] reply window elapsed; hanging up")
            try:
                call.hangup(pj.CallOpParam(True))
            except pj.Error:
                pass
            break

    # 6. Write captured reply.
    captured = call.audio_port.write_capture(args.capture)
    print(f"[harness] captured {captured} PCM bytes -> {args.capture} "
          f"({captured/16000:.2f}s)")
    if captured == 0:
        print("[harness] WARNING: no audio captured from Sara. "
              "Check that the call CONFIRMED and media wired "
              "(see onCallMediaState TODO[SIP-LIVE]).")

    # 7. Teardown.
    ep.libDestroy()
    return 0 if captured > 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Drive Sara via real audio over a direct SIP leg.")
    p.add_argument("--sara-ip", default=os.getenv("SARA_IP", "192.168.1.12"),
                   help="Sara/iMac IP (direct INVITE target host)")
    p.add_argument("--sara-port", type=int, default=int(os.getenv("SARA_SIP_PORT", "5080")),
                   help="Sara SIP UDP port (default 5080, confirmed listening)")
    p.add_argument("--sara-user", default=os.getenv("VOIP_SIP_USER", "0972536918"),
                   help="Sara SIP user part (Request-URI user)")
    p.add_argument("--local-ip", default=os.getenv("HARNESS_IP", "127.0.0.1"),
                   help="Harness local IP for Contact/idUri")
    p.add_argument("--local-port", type=int, default=int(os.getenv("HARNESS_SIP_PORT", "5070")),
                   help="Harness SIP UDP port (MUST differ from Sara's 5080)")
    p.add_argument("--say", default="Buongiorno, vorrei prenotare un taglio per domani pomeriggio",
                   help="Italian text to speak to Sara (rendered via say+afconvert)")
    p.add_argument("--wav", default=None,
                   help="Use an existing PCM16/8k/mono WAV instead of --say")
    p.add_argument("--capture", default="/tmp/sara_reply.wav",
                   help="Where to write Sara's captured audio reply")
    p.add_argument("--timeout", type=float, default=30.0,
                   help="Overall call timeout (s)")
    p.add_argument("--reply-window", type=float, default=8.0,
                   help="Seconds to keep capturing after we finish speaking")
    return p


if __name__ == "__main__":
    sys.exit(run_harness(build_parser().parse_args()))

```
