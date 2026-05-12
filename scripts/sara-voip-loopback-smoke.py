#!/usr/bin/env python3
"""
Sara VoIP Loopback Smoke Test — esecuzione autonoma su iMac.

Test end-to-end pipeline pjsua2 + audio bridge + Sara orchestrator senza
dipendenza PSTN reale (no cellulare, no founder fisico, no costo).

Architettura:
    [fake-caller pjsua2 :5091] --INVITE--> [Sara pipeline pjsua2 :5080]
                                             |
                                             +-- SaraAudioPort bridge
                                             +-- STT (Whisper local/Groq)
                                             +-- Orchestrator (FSM + RAG)
                                             +-- TTS (Edge/Piper) -> RTP back

Trade-off documentati:
    ✅ Valida:    pjsua2 stack, audio bridge, codec G.711 8kHz, STT/TTS bidi,
                  FSM transitions, DB persistenza
    ❌ NON valida: NAT casa CGNAT, codec PSTN reale, latency rete VivaVox,
                  audio quality cellulare → DID

Esecuzione SOLO da iMac (pjsua2 lib path + pipeline running):
    cd '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2'
    DYLD_LIBRARY_PATH=. PYTHONPATH=. /usr/bin/python3 \\
        '/Volumes/MacSSD - Dati/fluxion/scripts/sara-voip-loopback-smoke.py'

Prerequisiti:
    - Pipeline running su porta 3002 con VoIP REGISTERED su VivaVox (o anche
      solo running=true; INVITE locale bypassa REGISTER status)
    - pjsua2 lib in voice-agent/lib/pjsua2/
    - /usr/bin/python3 (3.9) — NON 3.13 MacBook

Esito atteso PASS:
    1. fake-caller INVITE accettato (200 OK)
    2. RTP audio bidirezionale stabilito
    3. Sara TTS saluto registrato in file WAV output
    4. BYE pulito → call termina con status=200

Esito FAIL:
    - INVITE rifiutato (4xx/5xx) → pipeline non listening o config errata
    - No RTP audio → SaraAudioPort bridge rotto
    - Sara non saluta → orchestrator non iniettato in VoIPManager
    - Crash pjsua2 → bug noto macOS 11 (vedi NOTE CTO RUNBOOK-P1)

STATO ATTUALE (S204 spike):
    ✅ INVITE locale accettato dalla pipeline (log pipeline conferma:
       "Incoming call from: <sip:smoke-caller@127.0.0.1> → 200 OK → Audio bridge established")
    ✅ Pipeline VoIP REGISTERED su VivaVox reale (sip:0972536918@sip.vivavox.it)
    ✅ pjsua2 second endpoint port 5091 OK
    ❌ FAKE-CALLER NON EMETTE ACK su 200 OK → call resta in CONNECTING (state=4),
       non passa a CONFIRMED → audio outbound non parte (pipeline aspetta dialog
       complete) → WAV catturato è 100% silenzio.

TODO S205 (~30 min):
    1. Fix ACK auto-emission in IP-based account:
       opzione A) impostare acc_cfg.regConfig.registrarUri = ""
       opzione B) usare TransportConfig.publicAddress per Contact corretto
       opzione C) handler manuale su CallState=EARLY → call.answer(200)
    2. Verificare onCallState raggiunge PJSIP_INV_STATE_CONFIRMED
    3. Verificare RMS audio WAV > 100 (saluto Sara reale)
    4. Estendere a Scenario 4 Flusso Perfetto:
       - Genera WAV turni cliente via Edge-TTS (text=turno italiano)
       - Inietta in capture_port.tx_queue tra silent frames
       - Wait Sara TTS RX silence threshold > 1s → next turn
       - Verifica DB clienti + appuntamenti post-test

Output:
    /tmp/sara-voip-loopback-YYYYMMDD-HHMMSS.log    (log full)
    /tmp/sara-voip-loopback-YYYYMMDD-HHMMSS.wav    (audio Sara captured)
    /tmp/sara-voip-loopback-report.json            (verdetto PASS/FAIL)
"""

from __future__ import annotations

import json
import os
import sys
import time
import wave
from datetime import datetime
from pathlib import Path

# pjsua2 import must succeed BEFORE anything else
try:
    import pjsua2 as pj
except ImportError as e:
    print(f"FATAL: pjsua2 not importable. Run from lib/pjsua2 dir with DYLD_LIBRARY_PATH=. PYTHONPATH=. : {e}", file=sys.stderr)
    sys.exit(2)


# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

PIPELINE_SIP_PORT = 5080
PIPELINE_SIP_USER = "0972536918"  # Sara's VivaVox DID — INVITE target user part
PIPELINE_HOST = "127.0.0.1"

FAKE_CALLER_PORT = 5091
FAKE_CALLER_USER = "smoke-caller"

# Smoke test: just hold call open for N seconds to capture Sara's greeting
SMOKE_CALL_DURATION_SEC = 15

TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
LOG_FILE = Path(f"/tmp/sara-voip-loopback-{TIMESTAMP}.log")
WAV_FILE = Path(f"/tmp/sara-voip-loopback-{TIMESTAMP}.wav")
REPORT_FILE = Path("/tmp/sara-voip-loopback-report.json")


# ─────────────────────────────────────────────────────────────────
# Audio capture port: receives Sara's TTS audio frames, writes to WAV
# ─────────────────────────────────────────────────────────────────

class CaptureAudioPort(pj.AudioMediaPort):
    """Captures audio FROM Sara (pipeline TTS output) into WAV file."""

    def __init__(self, wav_path: Path):
        super().__init__()
        self._wav_path = wav_path
        self._frames_received = 0
        self._wav_writer: wave.Wave_write | None = None

        fmt = pj.MediaFormatAudio()
        # 0x2036314C = PJMEDIA_FORMAT_L16 (linear 16-bit PCM)
        fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
        self.createPort("smoke_capture", fmt)

        self._open_wav()

    def _open_wav(self) -> None:
        self._wav_writer = wave.open(str(self._wav_path), "wb")
        self._wav_writer.setnchannels(1)
        self._wav_writer.setsampwidth(2)  # 16-bit
        self._wav_writer.setframerate(8000)

    def onFrameReceived(self, frame):
        if frame.type == pj.PJMEDIA_FRAME_TYPE_AUDIO and self._wav_writer:
            try:
                self._wav_writer.writeframes(bytes(frame.buf))
                self._frames_received += 1
            except Exception:
                pass

    def onFrameRequested(self, frame):
        # Send silence (smoke test: caller doesn't speak)
        frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
        frame.buf = pj.ByteVector(b"\x00" * 320)

    def close(self) -> None:
        if self._wav_writer:
            self._wav_writer.close()
            self._wav_writer = None

    @property
    def frames_received(self) -> int:
        return self._frames_received


# ─────────────────────────────────────────────────────────────────
# Call handler
# ─────────────────────────────────────────────────────────────────

class SmokeCall(pj.Call):
    def __init__(self, account: pj.Account, capture_port: CaptureAudioPort):
        super().__init__(account)
        self._capture_port = capture_port
        self.connected = False
        self.terminated = False
        self.last_status = 0

    def onCallState(self, prm):
        info = self.getInfo()
        self.last_status = info.lastStatusCode
        state = info.state
        print(f"[CALL_STATE] state={state} status={info.lastStatusCode} reason={info.lastReason}")

        if state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.connected = True
        elif state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.terminated = True

    def onCallMediaState(self, prm):
        info = self.getInfo()
        for i, media in enumerate(info.media):
            if media.type == pj.PJMEDIA_TYPE_AUDIO and self.getMedia(i):
                audio_media = pj.AudioMedia.typecastFromMedia(self.getMedia(i))
                # Bidi: Sara audio -> capture; capture silence -> Sara
                audio_media.startTransmit(self._capture_port)
                self._capture_port.startTransmit(audio_media)
                print(f"[MEDIA] audio stream {i} active (bidi capture<->call)")


# ─────────────────────────────────────────────────────────────────
# Main test
# ─────────────────────────────────────────────────────────────────

def run_smoke() -> dict:
    result = {
        "timestamp": TIMESTAMP,
        "test": "sara-voip-loopback-smoke",
        "stages": {},
        "verdict": "FAIL",
        "wav_file": str(WAV_FILE),
        "log_file": str(LOG_FILE),
    }

    ep = pj.Endpoint()
    ep.libCreate()

    try:
        # 1. Init pjsua2
        ep_cfg = pj.EpConfig()
        ep_cfg.logConfig.level = 4
        ep_cfg.logConfig.filename = str(LOG_FILE)
        ep_cfg.uaConfig.userAgent = "FLUXION-SmokeCaller/1.0"
        ep.libInit(ep_cfg)
        result["stages"]["libInit"] = "OK"

        # 2. UDP transport on free port
        tp_cfg = pj.TransportConfig()
        tp_cfg.port = FAKE_CALLER_PORT
        ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)
        result["stages"]["transport"] = f"OK port={FAKE_CALLER_PORT}"

        # 3. Start lib
        ep.libStart()
        result["stages"]["libStart"] = "OK"

        # 4. IP-based account (no registration)
        acc_cfg = pj.AccountConfig()
        acc_cfg.idUri = f"sip:{FAKE_CALLER_USER}@{PIPELINE_HOST}:{FAKE_CALLER_PORT}"
        # No registrarUri → no REGISTER attempt
        acc = pj.Account()
        acc.create(acc_cfg)
        result["stages"]["account"] = "OK ip-based"
        time.sleep(0.5)

        # 5. Capture port (Sara audio -> WAV)
        capture_port = CaptureAudioPort(WAV_FILE)
        result["stages"]["capture_port"] = "OK"

        # 6. INVITE to pipeline
        target_uri = f"sip:{PIPELINE_SIP_USER}@{PIPELINE_HOST}:{PIPELINE_SIP_PORT}"
        print(f"[INVITE] -> {target_uri}")
        call = SmokeCall(acc, capture_port)
        call_prm = pj.CallOpParam()
        call_prm.opt.audioCount = 1
        call_prm.opt.videoCount = 0
        call.makeCall(target_uri, call_prm)
        result["stages"]["invite_sent"] = target_uri

        # 7. Wait for connected or timeout
        connect_deadline = time.time() + 8
        while time.time() < connect_deadline and not call.connected and not call.terminated:
            time.sleep(0.2)

        if not call.connected:
            result["stages"]["connected"] = f"FAIL status={call.last_status}"
            return result
        result["stages"]["connected"] = f"OK status={call.last_status}"

        # 8. Hold call open, capture audio
        print(f"[CALL] connected, holding {SMOKE_CALL_DURATION_SEC}s to capture Sara greeting...")
        end_at = time.time() + SMOKE_CALL_DURATION_SEC
        while time.time() < end_at and not call.terminated:
            time.sleep(0.5)

        frames = capture_port.frames_received
        result["stages"]["frames_received"] = frames

        # 9. Hangup
        if not call.terminated:
            hangup_prm = pj.CallOpParam(True)
            try:
                call.hangup(hangup_prm)
            except Exception as e:
                print(f"[HANGUP] error: {e}")
            time.sleep(1.0)
        result["stages"]["hangup"] = "OK"

        capture_port.close()

        # 10. Verdict
        # Smoke PASS if: connected + >50 frames received (>1s audio = greeting)
        if call.connected and frames > 50:
            result["verdict"] = "PASS"
        else:
            result["verdict"] = "FAIL"
            result["stages"]["reason"] = f"frames={frames} (need >50)"

    except pj.Error as e:
        result["stages"]["pjsua2_error"] = e.info()
    except Exception as e:
        result["stages"]["exception"] = repr(e)
    finally:
        try:
            ep.libDestroy()
        except Exception:
            pass

    return result


if __name__ == "__main__":
    print(f"=== Sara VoIP Loopback Smoke Test — {TIMESTAMP} ===")
    print(f"Target: sip:{PIPELINE_SIP_USER}@{PIPELINE_HOST}:{PIPELINE_SIP_PORT}")
    print(f"Caller: sip:{FAKE_CALLER_USER}@{PIPELINE_HOST}:{FAKE_CALLER_PORT}")
    print(f"Logs:   {LOG_FILE}")
    print(f"Audio:  {WAV_FILE}")
    print()

    report = run_smoke()
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    print()
    print(f"=== VERDETTO: {report['verdict']} ===")
    print(json.dumps(report, indent=2))

    sys.exit(0 if report["verdict"] == "PASS" else 1)
