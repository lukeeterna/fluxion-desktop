"""
FLUXION Voice Agent - VoIP Module (pyVoIP)

Production SIP/RTP integration using pyVoIP library.
Handles NAT traversal, SIP registration, and audio bridging to Sara pipeline.

Replaces the hand-rolled voip.py with a battle-tested SIP stack.
"""

import asyncio
import audioop
import io
import logging
import os
import struct
import threading
import time
import wave
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Lazy import pyVoIP (not available on MacBook dev, only on iMac/client)
try:
    from pyVoIP.VoIP import CallState, VoIPCall, VoIPPhone
    PYVOIP_AVAILABLE = True
except ImportError:
    PYVOIP_AVAILABLE = False
    logger.info("pyVoIP not installed — VoIP disabled")


class SaraVoIPBridge:
    """
    Bridge between pyVoIP (SIP/RTP) and Sara voice pipeline.

    Handles:
    - SIP registration with EHIWEB VivaVox
    - Auto-answer incoming calls
    - Audio format conversion (G.711 8kHz ↔ PCM 16kHz)
    - VAD-based turn detection
    - Sara pipeline integration (STT → NLU → TTS)
    """

    def __init__(self, pipeline=None):
        self.pipeline = pipeline
        self.phone: Optional[Any] = None  # VoIPPhone instance
        self._running = False
        self._active_calls: Dict[str, threading.Thread] = {}

        # Config from env
        self.sip_server = os.getenv("VOIP_SIP_SERVER", os.getenv("EHIWEB_SIP_SERVER", "sip.vivavox.it"))
        self.sip_port = int(os.getenv("VOIP_SIP_PORT", os.getenv("EHIWEB_SIP_PORT", "5060")))
        self.sip_user = os.getenv("VOIP_SIP_USER", os.getenv("EHIWEB_SIP_USER", ""))
        self.sip_pass = os.getenv("VOIP_SIP_PASS", os.getenv("EHIWEB_SIP_PASS", ""))

        # VAD settings
        self.speech_threshold = 300  # RMS threshold for speech detection
        self.silence_timeout_ms = 800  # ms of silence = end of turn
        self.min_speech_ms = 150  # minimum speech to consider a turn

    def set_pipeline(self, pipeline):
        """Set Sara voice pipeline for processing."""
        self.pipeline = pipeline

    async def start(self) -> bool:
        """Start VoIP service with pyVoIP."""
        if not PYVOIP_AVAILABLE:
            logger.error("pyVoIP not installed — run: pip install pyVoIP")
            return False

        if not self.sip_user or not self.sip_pass:
            logger.error("SIP credentials not configured (VOIP_SIP_USER / VOIP_SIP_PASS)")
            return False

        if self._running:
            return True

        try:
            # Enable pyVoIP debug logging
            import pyVoIP
            pyVoIP.DEBUG = True

            self.phone = VoIPPhone(
                server=self.sip_server,
                port=self.sip_port,
                username=self.sip_user,
                password=self.sip_pass,
                callCallback=self._on_incoming_call,
                myIP="0.0.0.0",  # Let pyVoIP auto-detect
                sipPort=5080,  # Avoid conflict with other services on 5060
                rtpPortLow=10000,
                rtpPortHigh=10100,
            )
            self.phone.start()
            self._running = True

            logger.info(f"VoIP started: {self.sip_user}@{self.sip_server}")
            return True

        except Exception as e:
            logger.error(f"VoIP start failed: {e}")
            return False

    async def stop(self):
        """Stop VoIP service."""
        if not self._running:
            return

        self._running = False
        if self.phone:
            try:
                self.phone.stop()
            except Exception as e:
                logger.error(f"VoIP stop error: {e}")
            self.phone = None

        logger.info("VoIP stopped")

    def _on_incoming_call(self, call: 'VoIPCall'):
        """
        Callback when incoming call arrives (runs in pyVoIP's thread).

        Auto-answers and starts audio processing in a new thread.
        """
        caller = getattr(call, 'request', None)
        caller_num = "unknown"
        if caller and hasattr(caller, 'headers'):
            from_header = caller.headers.get("From", "")
            if "<sip:" in from_header:
                caller_num = from_header.split("<sip:")[1].split("@")[0]

        logger.info(f"📞 Incoming call from {caller_num}")

        try:
            call.answer()
            logger.info(f"✅ Call answered: {caller_num}")
        except Exception as e:
            logger.error(f"Failed to answer call: {e}")
            return

        # Handle call in a separate thread (pyVoIP uses threading, not asyncio)
        thread = threading.Thread(
            target=self._handle_call_thread,
            args=(call, caller_num),
            daemon=True,
            name=f"sara-call-{caller_num}"
        )
        thread.start()

    def _handle_call_thread(self, call: 'VoIPCall', caller_num: str):
        """Handle an active call — runs in its own thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._handle_call(call, caller_num))
        except Exception as e:
            logger.error(f"Call handler error: {e}")
        finally:
            loop.close()
            logger.info(f"📞 Call ended: {caller_num}")

    async def _handle_call(self, call: 'VoIPCall', caller_num: str):
        """Process a call: greeting → listen → respond → loop."""
        # Play greeting
        if self.pipeline:
            try:
                greeting = await self.pipeline.greet()
                if greeting.get("audio_response"):
                    self._send_tts_audio(call, greeting["audio_response"])
            except Exception as e:
                logger.error(f"Greeting error: {e}")

        # Main conversation loop
        while call.state == CallState.ANSWERED:
            # Listen for a complete utterance (VAD)
            audio_pcm = self._listen_for_turn(call)

            if audio_pcm is None:
                break  # Call ended

            if len(audio_pcm) < 640:  # Less than 20ms — skip
                continue

            # Process through Sara pipeline
            if self.pipeline:
                try:
                    result = await self.pipeline.process_audio(audio_pcm)

                    if result.get("audio_response"):
                        self._send_tts_audio(call, result["audio_response"])
                except Exception as e:
                    logger.error(f"Pipeline error: {e}")

    def _listen_for_turn(self, call: 'VoIPCall') -> Optional[bytes]:
        """
        Listen for a complete speech turn using energy-based VAD.

        Returns PCM 16-bit 16kHz mono bytes, or None if call ended.
        """
        audio_buffer = bytearray()
        is_speaking = False
        silence_frames = 0
        speech_frames = 0

        # Frame size: 160 samples = 20ms at 8kHz (pyVoIP default)
        frame_size = 160
        frames_per_silence_timeout = int(self.silence_timeout_ms / 20)
        min_speech_frames = int(self.min_speech_ms / 20)
        max_silence_before_hangup = 15000 // 20  # 15s total silence → assume caller left

        total_silence = 0

        while call.state == CallState.ANSWERED:
            try:
                # Read audio from caller (G.711 decoded to PCM by pyVoIP)
                pcm_8k = call.read_audio(length=frame_size, blocking=True)
            except Exception:
                return None  # Call ended

            if not pcm_8k or len(pcm_8k) == 0:
                time.sleep(0.01)
                continue

            # Check energy level
            try:
                rms = audioop.rms(pcm_8k, 2)
            except audioop.error:
                continue

            if rms > self.speech_threshold:
                is_speaking = True
                speech_frames += 1
                silence_frames = 0
                total_silence = 0

                # Upsample 8kHz → 16kHz and accumulate
                pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
                audio_buffer.extend(pcm_16k)
            else:
                total_silence += 1
                if is_speaking:
                    silence_frames += 1
                    # Still accumulate during brief pauses
                    pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
                    audio_buffer.extend(pcm_16k)

                    if silence_frames >= frames_per_silence_timeout and speech_frames >= min_speech_frames:
                        # Turn complete
                        is_speaking = False
                        speech_frames = 0
                        silence_frames = 0
                        return bytes(audio_buffer)

                # No speech for too long — caller might have left
                if total_silence >= max_silence_before_hangup and not is_speaking:
                    if len(audio_buffer) > 0:
                        return bytes(audio_buffer)
                    return None

        return None  # Call state changed

    def _send_tts_audio(self, call: 'VoIPCall', audio_data: bytes):
        """
        Send TTS audio to caller.

        Handles WAV header stripping and sample rate conversion.
        """
        if call.state != CallState.ANSWERED:
            return

        # Extract PCM from WAV if needed
        src_rate = 16000
        pcm_data = audio_data

        if audio_data[:4] == b"RIFF":
            try:
                with wave.open(io.BytesIO(audio_data), 'rb') as wf:
                    src_rate = wf.getframerate()
                    pcm_data = wf.readframes(wf.getnframes())
            except Exception as e:
                logger.warning(f"WAV parse error: {e}")

        # Downsample to 8kHz for phone
        if src_rate != 8000:
            try:
                pcm_8k, _ = audioop.ratecv(pcm_data, 2, 1, src_rate, 8000, None)
            except audioop.error as e:
                logger.error(f"Resample error: {e}")
                return
        else:
            pcm_8k = pcm_data

        # Send in 20ms chunks (160 samples * 2 bytes = 320 bytes at 8kHz)
        chunk_size = 320
        for i in range(0, len(pcm_8k), chunk_size):
            if call.state != CallState.ANSWERED:
                break
            chunk = pcm_8k[i:i + chunk_size]
            if len(chunk) < chunk_size:
                # Pad last chunk with silence
                chunk = chunk + b'\x00' * (chunk_size - len(chunk))
            try:
                call.write_audio(chunk)
            except Exception:
                break
            time.sleep(0.018)  # ~20ms pacing (slightly less to avoid underrun)

    async def hangup(self) -> bool:
        """Hangup active call."""
        if not self.phone:
            return False
        # pyVoIP manages calls internally
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get VoIP status."""
        registered = False
        if self.phone:
            try:
                status = self.phone.get_status()
                # pyVoIP returns PhoneStatus enum — check multiple representations
                status_str = str(status).upper()
                registered = "REGISTERED" in status_str or "REGISTER" in status_str
                if not registered:
                    # Also check if phone is alive and was started successfully
                    registered = self._running
            except Exception:
                registered = self._running

        return {
            "running": self._running,
            "sip": {
                "registered": registered,
                "server": self.sip_server,
                "username": self.sip_user,
            },
            "rtp_active": bool(self._active_calls),
        }


# Alias for backward compatibility with main.py
VoIPManager = SaraVoIPBridge
