"""
FLUXION Voice Agent - VoIP Module (pjsua2)

Production-grade SIP/VoIP using pjsua2 (pjsip SWIG bindings).
Replaces the hand-rolled voip.py with industry-standard NAT traversal,
codec negotiation, jitter buffer, and RTP transport.

Architecture:
  Phone → EHIWEB SIP → pjsua2 (ICE/STUN/RTP) → SaraAudioPort → Sara Pipeline
  Sara Pipeline → SaraAudioPort → pjsua2 RTP → EHIWEB → Phone
"""

import asyncio
import audioop
import io
import logging
import os
import queue
import struct
import sys
import threading
import time
import wave
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Add pjsua2 lib path
_PJSUA2_LIB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib", "pjsua2")
if _PJSUA2_LIB_DIR not in sys.path:
    sys.path.insert(0, _PJSUA2_LIB_DIR)

# Set DYLD_LIBRARY_PATH for macOS dynamic libraries
if sys.platform == "darwin":
    existing = os.environ.get("DYLD_LIBRARY_PATH", "")
    if _PJSUA2_LIB_DIR not in existing:
        os.environ["DYLD_LIBRARY_PATH"] = _PJSUA2_LIB_DIR + (":" + existing if existing else "")

import pjsua2 as pj


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SIPConfig:
    """EHIWEB SIP configuration."""
    server: str = "sip.vivavox.it"
    port: int = 5060
    username: str = ""
    password: str = ""
    local_port: int = 5090  # 5060=Traccar, 5080=old voip.py
    stun_server: str = "stun.voip.vivavox.it:3478"
    user_agent: str = "FLUXION-Sara/1.0"

    @classmethod
    def from_env(cls) -> "SIPConfig":
        return cls(
            server=os.getenv("VOIP_SIP_SERVER", os.getenv("EHIWEB_SIP_SERVER", "sip.vivavox.it")),
            port=int(os.getenv("VOIP_SIP_PORT", os.getenv("EHIWEB_SIP_PORT", "5060"))),
            username=os.getenv("VOIP_SIP_USER", os.getenv("EHIWEB_SIP_USER", "")),
            password=os.getenv("VOIP_SIP_PASS", os.getenv("EHIWEB_SIP_PASS", "")),
            local_port=int(os.getenv("VOIP_LOCAL_PORT", "5080")),
        )


# =============================================================================
# Audio Bridge: pjsua2 ↔ Sara Pipeline
# =============================================================================

class SaraAudioPort(pj.AudioMediaPort):
    """Bridges pjsua2 conference bridge with Sara voice pipeline.

    - onFrameReceived: caller audio → rx_queue → Sara STT
    - onFrameRequested: Sara TTS → tx_queue → caller
    """

    def __init__(self):
        super().__init__()
        self.rx_queue = queue.Queue(maxsize=200)   # Caller speech → Sara
        self.tx_queue = queue.Queue(maxsize=500)   # Sara speech → caller
        self._silence_frame = b'\x00' * 320        # 20ms silence at 8kHz 16-bit mono

        # Create audio port: 8kHz, mono, 160 samples/frame (20ms), 16-bit
        # Use init() to properly initialize all internal fields (type, detail_type)
        # Manual field assignment leaves detail_type unset, causing assertion crash
        # Format ID 0x2036314C = PJMEDIA_FORMAT_L16 (linear 16-bit PCM)
        fmt = pj.MediaFormatAudio()
        fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
        self.createPort("sara_bridge", fmt)

    def onFrameReceived(self, frame):
        """Called by pjsua2 when audio arrives from the phone call."""
        if frame.type == pj.PJMEDIA_FRAME_TYPE_AUDIO:
            try:
                self.rx_queue.put_nowait(bytes(frame.buf))
            except queue.Full:
                pass  # Drop oldest if full (real-time priority)

    def onFrameRequested(self, frame):
        """Called by pjsua2 when it needs audio to send to the caller."""
        try:
            audio_data = self.tx_queue.get_nowait()
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(audio_data)
        except queue.Empty:
            # Send silence when Sara has nothing to say
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(self._silence_frame)

    def queue_tts_audio(self, audio_data: bytes, src_rate: int = 16000):
        """Queue TTS audio for playback to caller.

        Handles WAV parsing, resampling to 8kHz, and chunking into 20ms frames.
        """
        pcm_data = audio_data

        # Parse WAV header if present
        if audio_data[:4] == b"RIFF":
            try:
                wav_io = io.BytesIO(audio_data)
                with wave.open(wav_io, 'rb') as wf:
                    src_rate = wf.getframerate()
                    pcm_data = wf.readframes(wf.getnframes())
            except Exception as exc:
                logger.warning(f"WAV parse failed: {exc}, using raw at {src_rate}Hz")

        # Resample to 8kHz if needed
        if src_rate != 8000:
            pcm_data, _ = audioop.ratecv(pcm_data, 2, 1, src_rate, 8000, None)

        # Chunk into 20ms frames (320 bytes = 160 samples * 2 bytes)
        chunk_size = 320
        for i in range(0, len(pcm_data), chunk_size):
            chunk = pcm_data[i:i + chunk_size]
            if len(chunk) < chunk_size:
                chunk = chunk + b'\x00' * (chunk_size - len(chunk))
            try:
                self.tx_queue.put_nowait(chunk)
            except queue.Full:
                break  # Don't block, skip remaining

    def get_caller_audio(self, timeout: float = 0.5) -> Optional[bytes]:
        """Get accumulated caller audio (for STT processing).

        Returns PCM 8kHz 16-bit mono, or None if no audio available.
        """
        chunks = []
        try:
            while True:
                chunks.append(self.rx_queue.get_nowait())
        except queue.Empty:
            pass

        if chunks:
            return b''.join(chunks)
        return None

    def clear_tx(self):
        """Clear pending TTS audio (e.g., when caller interrupts)."""
        while not self.tx_queue.empty():
            try:
                self.tx_queue.get_nowait()
            except queue.Empty:
                break


# =============================================================================
# SIP Call Handler
# =============================================================================

class SaraCall(pj.Call):
    """Handles an incoming SIP call, bridging audio to Sara."""

    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        self.audio_port = SaraAudioPort()
        self.connected = False
        self.on_connected = None   # Callback: call connected
        self.on_disconnected = None  # Callback: call ended

    def onCallState(self, prm):
        ci = self.getInfo()
        state = ci.state
        logger.info(f"Call state: {ci.stateText} (state={state})")

        if state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.connected = True
            if self.on_connected:
                self.on_connected(self)
        elif state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.connected = False
            if self.on_disconnected:
                self.on_disconnected(self)

    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for i, mi in enumerate(ci.media):
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
               mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                # Get call's audio media
                call_audio = self.getAudioMedia(i)
                # Bidirectional bridge: call ↔ Sara
                call_audio.startTransmit(self.audio_port)
                self.audio_port.startTransmit(call_audio)
                logger.info("Audio bridge established: call ↔ Sara")


# =============================================================================
# SIP Account
# =============================================================================

class SaraAccount(pj.Account):
    """SIP account that handles incoming calls for Sara."""

    def __init__(self):
        super().__init__()
        self.current_call: Optional[SaraCall] = None
        self.on_incoming_call = None  # Callback for VoIPManager
        self.on_reg_state = None      # Callback for registration state

    def onRegState(self, prm):
        info = self.getInfo()
        is_registered = info.regIsActive
        logger.info(f"Registration: active={is_registered}, status={info.regStatus} {info.regStatusText}")
        if self.on_reg_state:
            self.on_reg_state(is_registered, info.regStatus)

    def onIncomingCall(self, prm):
        call = SaraCall(self, prm.callId)
        ci = call.getInfo()
        logger.info(f"Incoming call from: {ci.remoteUri}")

        # Only handle one call at a time
        if self.current_call and self.current_call.connected:
            logger.warning("Already in a call, rejecting new call")
            call_prm = pj.CallOpParam()
            call_prm.statusCode = 486  # Busy Here
            call.answer(call_prm)
            return

        self.current_call = call

        if self.on_incoming_call:
            self.on_incoming_call(call)


# =============================================================================
# VoIPManager — Drop-in replacement for voip.py VoIPManager
# =============================================================================

class VoIPManager:
    """Production-grade VoIP manager using pjsua2.

    Same interface as the old voip.py VoIPManager:
    - start() / stop()
    - set_pipeline(pipeline)
    - get_status() / hangup()
    """

    def __init__(self, config: Optional[SIPConfig] = None):
        self.config = config or SIPConfig.from_env()
        self.pipeline = None
        self._running = False
        self._registered = False
        self._reg_status = 0
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None  # Main aiohttp event loop

        # pjsua2 objects (created in _pj_thread)
        self._ep: Optional[pj.Endpoint] = None
        self._account: Optional[SaraAccount] = None
        self._transport_id = -1

        # pjsua2 runs in its own thread (it has its own event loop)
        self._pj_thread: Optional[threading.Thread] = None
        self._pj_started = threading.Event()
        self._pj_stop = threading.Event()

        # Audio processing
        self._audio_thread: Optional[threading.Thread] = None
        self._current_call: Optional[SaraCall] = None

        # Simple energy-based VAD for caller speech detection
        self._vad_speech_frames = 0
        self._vad_silence_frames = 0
        self._vad_speech_threshold = 500   # RMS energy threshold
        self._vad_silence_timeout = 35     # 35 frames * 20ms = 700ms silence = end of turn

    def set_pipeline(self, pipeline):
        """Set voice pipeline for processing incoming calls."""
        self.pipeline = pipeline

    async def start(self) -> bool:
        """Start VoIP service (SIP registration + listen for calls)."""
        if self._running:
            return True

        if not self.config.username or not self.config.password:
            logger.error("VoIP: SIP credentials not configured")
            return False

        # Capture the main event loop — coroutines must run here (httpx, groq, etc.)
        self._main_loop = asyncio.get_running_loop()

        # Start pjsua2 in background thread
        self._pj_thread = threading.Thread(target=self._pjsua2_thread, daemon=True)
        self._pj_thread.start()

        # Wait for initialization (max 10s)
        if not self._pj_started.wait(timeout=10):
            logger.error("VoIP: pjsua2 initialization timeout")
            return False

        # Wait a bit for registration
        await asyncio.sleep(3)

        if self._registered:
            self._running = True
            logger.info(f"VoIP started: {self.config.username}@{self.config.server}")
            return True
        else:
            logger.warning(f"VoIP: SIP registration pending (status={self._reg_status})")
            # Still consider it started — registration may complete later
            self._running = True
            return True

    async def stop(self):
        """Stop VoIP service."""
        if not self._running:
            return

        self._pj_stop.set()
        self._running = False

        if self._pj_thread:
            self._pj_thread.join(timeout=5)
            self._pj_thread = None

        logger.info("VoIP service stopped")

    async def hangup(self) -> bool:
        """End current call."""
        if self._current_call and self._current_call.connected:
            try:
                call_prm = pj.CallOpParam()
                self._current_call.hangup(call_prm)
                return True
            except Exception as exc:
                logger.error(f"Hangup error: {exc}")
                return False
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get VoIP status."""
        return {
            "running": self._running,
            "sip": {
                "registered": self._registered,
                "reg_status": self._reg_status,
                "username": self.config.username,
                "server": self.config.server,
            },
            "rtp_active": self._current_call is not None and self._current_call.connected,
            "engine": "pjsua2",
        }

    # =========================================================================
    # pjsua2 Thread (runs pjsip event loop)
    # =========================================================================

    def _pjsua2_thread(self):
        """Background thread running pjsua2 endpoint."""
        try:
            self._init_pjsua2()
            self._pj_started.set()

            # Event loop — poll pjsua2 every 20ms
            while not self._pj_stop.is_set():
                self._ep.libHandleEvents(20)

            # Cleanup
            self._cleanup_pjsua2()

        except Exception as exc:
            logger.error(f"pjsua2 thread error: {exc}", exc_info=True)
            self._pj_started.set()  # Unblock start() even on failure

    def _init_pjsua2(self):
        """Initialize pjsua2 endpoint, transport, and account."""
        # Create endpoint
        self._ep = pj.Endpoint()
        self._ep.libCreate()

        # Endpoint config
        ep_cfg = pj.EpConfig()
        ep_cfg.uaConfig.userAgent = self.config.user_agent
        ep_cfg.uaConfig.stunServer.append(self.config.stun_server)
        # Reduce log verbosity
        ep_cfg.logConfig.level = 3
        ep_cfg.logConfig.consoleLevel = 3

        # No sound device needed — we use AudioMediaPort for Sara bridge
        ep_cfg.medConfig.noVad = True
        # Disable SRTP — not needed for EHIWEB VoIP, avoids SRTP self-test
        # failure when running as headless daemon
        ep_cfg.medConfig.srtpUse = 0  # PJMEDIA_SRTP_DISABLED

        try:
            self._ep.libInit(ep_cfg)
        except pj.Error as e:
            logger.error(f"pjsua2 libInit failed: {e.info()}")
            raise

        # Create UDP transport
        tp_cfg = pj.TransportConfig()
        tp_cfg.port = self.config.local_port
        self._transport_id = self._ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)

        # Start library
        self._ep.libStart()
        logger.info(f"pjsua2 started on port {self.config.local_port}")

        # Create and register SIP account
        acc_cfg = pj.AccountConfig()
        acc_cfg.idUri = f"sip:{self.config.username}@{self.config.server}"
        acc_cfg.regConfig.registrarUri = f"sip:{self.config.server}:{self.config.port}"
        acc_cfg.regConfig.timeoutSec = 300

        # Auth credentials
        cred = pj.AuthCredInfo()
        cred.scheme = "digest"
        cred.realm = "*"
        cred.username = self.config.username
        cred.dataType = 0  # Plain text password
        cred.data = self.config.password
        acc_cfg.sipConfig.authCreds.append(cred)

        # NAT config — use STUN for mapped address
        acc_cfg.natConfig.iceEnabled = True
        acc_cfg.natConfig.sdpNatRewriteUse = 1
        acc_cfg.natConfig.sipOutboundUse = 1
        acc_cfg.natConfig.contactRewriteUse = 1

        # Create account
        self._account = SaraAccount()
        self._account.on_incoming_call = self._on_incoming_call
        self._account.on_reg_state = self._on_reg_state
        self._account.create(acc_cfg)

        logger.info(f"SIP account created: {self.config.username}@{self.config.server}")

    def _cleanup_pjsua2(self):
        """Clean up pjsua2 resources."""
        try:
            if self._current_call and self._current_call.connected:
                call_prm = pj.CallOpParam()
                self._current_call.hangup(call_prm)

            if self._account:
                self._account.shutdown()
                self._account = None

            if self._ep:
                self._ep.libDestroy()
                self._ep = None

        except Exception as exc:
            logger.error(f"pjsua2 cleanup error: {exc}")

    # =========================================================================
    # Callbacks (called from pjsua2 thread)
    # =========================================================================

    def _on_reg_state(self, is_registered: bool, status: int):
        """SIP registration state changed."""
        self._registered = is_registered
        self._reg_status = status
        if is_registered:
            logger.info("SIP REGISTERED successfully")
        else:
            logger.warning(f"SIP registration failed: status={status}")

    def _on_incoming_call(self, call: SaraCall):
        """Incoming call — auto-answer and start audio processing."""
        logger.info("Incoming call — auto-answering...")
        self._current_call = call
        call.on_connected = self._on_call_connected
        call.on_disconnected = self._on_call_disconnected

        # Auto-answer with 200 OK
        call_prm = pj.CallOpParam()
        call_prm.statusCode = 200
        call.answer(call_prm)

    def _on_call_connected(self, call: SaraCall):
        """Call connected — start audio processing thread."""
        logger.info("Call connected, starting audio processing")

        # Start audio processing thread
        self._audio_thread = threading.Thread(
            target=self._audio_processing_loop,
            args=(call,),
            daemon=True
        )
        self._audio_thread.start()

        # Send greeting
        if self.pipeline:
            threading.Thread(
                target=self._send_greeting,
                args=(call,),
                daemon=True
            ).start()

    def _on_call_disconnected(self, call: SaraCall):
        """Call ended — cleanup."""
        logger.info("Call disconnected")
        self._current_call = None
        self._vad_speech_frames = 0
        self._vad_silence_frames = 0

    # =========================================================================
    # Audio Processing (runs in dedicated thread)
    # =========================================================================

    def _audio_processing_loop(self, call: SaraCall):
        """Continuously reads caller audio, detects speech turns, processes via Sara."""
        logger.info("Audio processing loop started")
        audio_buffer = bytearray()
        speech_audio = bytearray()  # Accumulates actual speech frames for STT
        is_speaking = False  # Anti-echo: mute RX while Sara TTS is playing

        while call.connected and self._running:
            # Anti-echo: skip caller audio while Sara is speaking
            if not call.audio_port.tx_queue.empty():
                is_speaking = True
                # Drain any accumulated audio (it's echo from Sara)
                call.audio_port.get_caller_audio(timeout=0.01)
                speech_audio.clear()
                audio_buffer.clear()
                self._vad_speech_frames = 0
                self._vad_silence_frames = 0
                time.sleep(0.02)
                continue
            elif is_speaking:
                # Sara just finished speaking — brief grace period for echo to fade
                is_speaking = False
                time.sleep(0.3)
                call.audio_port.get_caller_audio(timeout=0.01)  # Drain echo tail
                continue

            # Get caller audio from the bridge
            audio = call.audio_port.get_caller_audio(timeout=0.1)
            if not audio:
                time.sleep(0.02)
                continue

            audio_buffer.extend(audio)

            # Simple energy-based VAD on 20ms frames
            frame_size = 320  # 20ms at 8kHz 16-bit mono
            while len(audio_buffer) >= frame_size:
                frame = bytes(audio_buffer[:frame_size])
                del audio_buffer[:frame_size]

                # Calculate RMS energy
                rms = self._calculate_rms(frame)

                if rms > self._vad_speech_threshold:
                    self._vad_speech_frames += 1
                    self._vad_silence_frames = 0
                    speech_audio.extend(frame)  # Keep speech frame for STT
                else:
                    if self._vad_speech_frames > 0:
                        self._vad_silence_frames += 1
                        speech_audio.extend(frame)  # Keep trailing silence too

                # Turn complete: had speech, then 700ms silence
                if self._vad_speech_frames >= 3 and self._vad_silence_frames >= self._vad_silence_timeout:
                    full_audio = bytes(speech_audio)
                    speech_audio.clear()
                    audio_buffer.clear()
                    self._vad_speech_frames = 0
                    self._vad_silence_frames = 0

                    if full_audio and self.pipeline:
                        dur_ms = len(full_audio) / 16  # 8kHz 16-bit = 16 bytes/ms
                        logger.info(f"Speech turn detected: {dur_ms:.0f}ms audio, sending to Sara")
                        self._process_caller_audio(call, full_audio)

        logger.info("Audio processing loop ended")

    def _calculate_rms(self, pcm_data: bytes) -> float:
        """Calculate RMS energy of PCM audio frame."""
        if len(pcm_data) < 2:
            return 0.0
        n_samples = len(pcm_data) // 2
        total = 0
        for i in range(n_samples):
            sample = struct.unpack_from('<h', pcm_data, i * 2)[0]
            total += sample * sample
        return (total / n_samples) ** 0.5

    def _process_caller_audio(self, call: SaraCall, audio_8k: bytes):
        """Process caller audio through Sara pipeline."""
        try:
            # Upsample 8kHz → 16kHz for Whisper STT
            audio_16k, _ = audioop.ratecv(audio_8k, 2, 1, 8000, 16000, None)

            # Schedule on main event loop (where httpx/groq clients live)
            t0 = time.time()
            future = asyncio.run_coroutine_threadsafe(
                self.pipeline.process_audio(audio_16k), self._main_loop
            )
            result = future.result(timeout=30)  # 30s max for STT+NLU+TTS
            elapsed = (time.time() - t0) * 1000

            if result:
                text = result.get("text", "")
                transcription = result.get("transcription", "")
                has_audio = result.get("audio_response") is not None
                audio_len = len(result["audio_response"]) if has_audio else 0
                logger.info(f"Pipeline result ({elapsed:.0f}ms): STT='{transcription}' → response='{text[:80]}' audio={audio_len}B")

                # Queue TTS response
                if has_audio:
                    call.audio_port.queue_tts_audio(result["audio_response"])
                    logger.info("TTS audio queued for playback")
                else:
                    logger.warning("No audio_response from pipeline")
            else:
                logger.warning(f"Pipeline returned None ({elapsed:.0f}ms)")

        except Exception as exc:
            logger.error(f"Audio processing error: {exc}", exc_info=True)

    def _send_greeting(self, call: SaraCall):
        """Send Sara greeting when call connects."""
        try:
            # Brief delay for media to stabilize
            time.sleep(0.5)

            if not self.pipeline:
                return

            # Schedule on main event loop (where TTS/httpx clients live)
            future = asyncio.run_coroutine_threadsafe(
                self.pipeline.greet(), self._main_loop
            )
            greeting = future.result(timeout=15)

            if greeting and greeting.get("audio_response"):
                call.audio_port.queue_tts_audio(greeting["audio_response"])
                logger.info("Greeting queued for playback")

        except Exception as exc:
            logger.error(f"Greeting error: {exc}", exc_info=True)


# =============================================================================
# Test
# =============================================================================

async def test_voip():
    """Test pjsua2 VoIP — register and wait for calls."""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.env"))

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    config = SIPConfig.from_env()
    print(f"SIP: {config.username}@{config.server}:{config.port}")
    print(f"STUN: {config.stun_server}")
    print(f"Local port: {config.local_port}")

    manager = VoIPManager(config)

    print("\nStarting VoIP (pjsua2)...")
    if await manager.start():
        print(f"✅ VoIP started — registered={manager._registered}")
        print(f"Status: {manager.get_status()}")
        print("\nWaiting for incoming calls... (Ctrl+C to stop)")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("❌ VoIP start failed")

    await manager.stop()
    print("VoIP stopped")


if __name__ == "__main__":
    asyncio.run(test_voip())
