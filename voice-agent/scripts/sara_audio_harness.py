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
        # S354: same guarded pattern as src/voip_pjsua2._register_thread_if_needed.
        # MUST check libIsThreadRegistered() first: calling libRegisterThread on a
        # thread pjlib already tracks (the clock thread is partly known) overwrites
        # its pj_thread_desc and corrupts group-lock owner identity → lock.c:279.
        # Register ONLY genuinely-unknown threads.
        if getattr(self._thread_local, "registered", False):
            return
        try:
            ep = pj.Endpoint.instance()
            if not ep.libIsThreadRegistered():
                ep.libRegisterThread(
                    f"harness_audio_cb_{threading.get_ident()}"
                )
        except pj.Error:
            pass
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
        # S354: deferred-bridge confinement, mirrors SaraAccount.drain_pending_bridges.
        # The S353 verdict PROVED the lock.c:279 SIGABRT came from THIS harness's
        # conference-bridge clock thread (harness_bridge), not from Sara: doing
        # ensure_port/getAudioMedia/startTransmit inside onCallMediaState runs on a
        # pjmedia media thread that does NOT own the group lock. So enqueue-only
        # here; the run_harness() libHandleEvents loop (group-lock owner) drains it.
        self._pending_media_index = None   # set by callback, consumed by drain
        self._bridge_done = False
        self._bridge_attempts = 0
        self._BRIDGE_MAX_ATTEMPTS = 25     # 25 * 20ms = 500ms slot wait

    def onCallState(self, prm):
        ci = self.getInfo()
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.connected = True
        elif ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.connected = False
            self.done.set()

    def onCallMediaState(self, prm):
        """ENQUEUE-ONLY (S354). Runs on a pjmedia media thread without the group
        lock. getInfo() only (same op the S353 baseline ran safely), then record
        the active audio media index for the main loop to wire. NO ensure_port /
        getAudioMedia / startTransmit here — those take pjsua2 locks and were the
        source of the harness's lock.c:279 SIGABRT (S353 verdict)."""
        try:
            ci = self.getInfo()
        except pj.Error as exc:
            sys.stderr.write(f"[harness] onCallMediaState getInfo error: {exc}\n")
            return
        for i in range(len(ci.media)):
            mi = ci.media[i]
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                self._pending_media_index = i
                print(f"[harness] onCallMediaState enqueued bridge (media_index={i}) "
                      "— deferred to main loop")
                return

    def drain_bridge(self):
        """Called from run_harness() libHandleEvents loop (group-lock owner).
        Performs ensure_port + getAudioMedia + bidirectional startTransmit OUTSIDE
        the media callback, where the group lock is held. Idempotent / retrying."""
        if self._bridge_done or self._pending_media_index is None:
            return
        try:
            self.audio_port.ensure_port()
        except pj.Error as exc:
            sys.stderr.write(f"[harness] drain ensure_port error: {exc}\n")
            return
        try:
            call_audio = self.getAudioMedia(self._pending_media_index)
        except pj.Error as exc:
            self._bridge_attempts += 1
            if self._bridge_attempts >= self._BRIDGE_MAX_ATTEMPTS:
                sys.stderr.write(
                    f"[harness] drain getAudioMedia unavailable after "
                    f"{self._bridge_attempts * 20}ms — giving up ({exc})\n")
                self._pending_media_index = None
            return
        call_slot = call_audio.getPortId()
        sara_slot = self.audio_port.getPortId()
        if call_slot == pj.PJSUA_INVALID_ID or sara_slot == pj.PJSUA_INVALID_ID:
            self._bridge_attempts += 1
            if self._bridge_attempts >= self._BRIDGE_MAX_ATTEMPTS:
                sys.stderr.write(
                    f"[harness] drain slot not assigned after "
                    f"{self._bridge_attempts * 20}ms — giving up\n")
                self._pending_media_index = None
            return
        try:
            # Sara reply -> our port (capture); our WAV -> Sara.
            call_audio.startTransmit(self.audio_port)
            self.audio_port.startTransmit(call_audio)
            self._bridge_done = True
            print(f"[harness] audio bridge established (deferred): "
                  f"harness(slot={sara_slot}) <-> Sara(slot={call_slot}) "
                  f"after {self._bridge_attempts * 20}ms")
        except pj.Error as exc:
            sys.stderr.write(f"[harness] drain startTransmit error: {exc}\n")


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
        # S354: wire the audio bridge here, on the libHandleEvents (group-lock
        # owner) thread, NOT inside onCallMediaState. This is the harness-side
        # mirror of SaraAccount.drain_pending_bridges and the fix for the
        # harness's own lock.c:279 SIGABRT proven in S353.
        call.drain_bridge()
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
