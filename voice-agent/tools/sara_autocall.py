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
