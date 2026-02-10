"""
VAD HTTP Handler for Fluxion Voice Agent
=========================================

Adds VAD-enabled endpoints to the voice pipeline HTTP server.
Supports both streaming audio and chunked processing.

Endpoints:
- POST /api/voice/vad/start - Start VAD session
- POST /api/voice/vad/chunk - Process audio chunk
- POST /api/voice/vad/stop - Stop VAD session
- GET  /api/voice/vad/status - Get VAD state
"""

import asyncio
import time
import struct
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from aiohttp import web
import logging

from vad import FluxionVAD, VADConfig, VADState

logger = logging.getLogger(__name__)


def add_wav_header(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """
    Add WAV header to raw PCM audio data.
    
    Groq Whisper API expects a valid WAV file, not raw PCM.
    This function creates a proper WAV header for the PCM data.
    
    Args:
        pcm_data: Raw PCM audio bytes (16-bit signed integer)
        sample_rate: Sample rate in Hz (default: 16000)
        channels: Number of channels (default: 1 for mono)
        bits_per_sample: Bits per sample (default: 16)
    
    Returns:
        Complete WAV file as bytes
    """
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_data)
    
    # WAV header structure
    header = b'RIFF'
    header += struct.pack('<I', 36 + data_size)  # Chunk size
    header += b'WAVE'
    header += b'fmt '
    header += struct.pack('<I', 16)              # Subchunk1 size (16 for PCM)
    header += struct.pack('<H', 1)               # Audio format (1 = PCM)
    header += struct.pack('<H', channels)        # Number of channels
    header += struct.pack('<I', sample_rate)     # Sample rate
    header += struct.pack('<I', byte_rate)       # Byte rate
    header += struct.pack('<H', block_align)     # Block align
    header += struct.pack('<H', bits_per_sample) # Bits per sample
    header += b'data'
    header += struct.pack('<I', data_size)       # Data chunk size
    
    return header + pcm_data


@dataclass
class VADSession:
    """Active VAD session state."""
    session_id: str
    vad: FluxionVAD
    speech_buffer: bytearray = field(default_factory=bytearray)
    is_speaking: bool = False
    turn_start_time: Optional[float] = None
    total_chunks: int = 0
    events: list = field(default_factory=list)


class VADHTTPHandler:
    """
    HTTP handler for VAD-enabled voice processing.

    Supports two modes:
    1. Chunked mode: Frontend sends audio chunks, backend detects turns
    2. Complete mode: Frontend sends complete audio after user stops

    Usage:
        handler = VADHTTPHandler(orchestrator, groq_client)
        handler.setup_routes(app)
    """

    def __init__(
        self,
        orchestrator,
        groq_client,
        vad_config: Optional[VADConfig] = None
    ):
        self.orchestrator = orchestrator
        self.groq = groq_client

        # VAD configuration optimized for Italian speech
        self.vad_config = vad_config or VADConfig(
            vad_threshold=0.4,          # Sensitive enough for soft speech
            silence_duration_ms=500,     # 500ms silence = end of turn
            prefix_padding_ms=200,       # Keep 200ms before speech
            hop_size_ms=10              # 10ms frame resolution
        )

        # Active VAD sessions (session_id -> VADSession)
        self._sessions: Dict[str, VADSession] = {}

        # Callbacks
        self._on_turn_complete: Optional[Callable] = None
        self._on_barge_in: Optional[Callable] = None

    def setup_routes(self, app: web.Application):
        """Setup VAD HTTP routes."""
        # VAD endpoints
        app.router.add_post("/api/voice/vad/start", self.vad_start_handler)
        app.router.add_post("/api/voice/vad/chunk", self.vad_chunk_handler)
        app.router.add_post("/api/voice/vad/stop", self.vad_stop_handler)
        app.router.add_get("/api/voice/vad/status", self.vad_status_handler)

        # Auto-VAD process endpoint (combines chunk processing with auto-STT)
        app.router.add_post("/api/voice/process-with-vad", self.process_with_vad_handler)

        # Shorthand routes
        app.router.add_post("/vad/start", self.vad_start_handler)
        app.router.add_post("/vad/chunk", self.vad_chunk_handler)
        app.router.add_post("/vad/stop", self.vad_stop_handler)
        app.router.add_get("/vad/status", self.vad_status_handler)

    async def vad_start_handler(self, request: web.Request) -> web.Response:
        """Start a new VAD session."""
        try:
            data = await request.json() if request.body_exists else {}
            session_id = data.get("session_id", f"vad_{int(time.time() * 1000)}")

            # Create VAD instance
            vad = FluxionVAD(self.vad_config)
            vad.start()

            # Store session
            session = VADSession(
                session_id=session_id,
                vad=vad
            )
            self._sessions[session_id] = session

            logger.info(f"VAD session started: {session_id}")

            return web.json_response({
                "success": True,
                "session_id": session_id,
                "config": {
                    "threshold": self.vad_config.vad_threshold,
                    "silence_ms": self.vad_config.silence_duration_ms,
                    "prefix_ms": self.vad_config.prefix_padding_ms
                }
            })

        except Exception as e:
            logger.error(f"VAD start error: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def vad_chunk_handler(self, request: web.Request) -> web.Response:
        """
        Process an audio chunk through VAD.

        Request:
            {
                "session_id": "vad_123",
                "audio_hex": "hex-encoded PCM audio"
            }

        Response:
            {
                "success": true,
                "state": "SPEAKING" | "IDLE",
                "probability": 0.85,
                "event": "start_of_speech" | "end_of_speech" | null,
                "turn_ready": true/false,
                "turn_audio_hex": "..." (if turn_ready)
            }
        """
        try:
            data = await request.json()
            session_id = data.get("session_id")
            audio_hex = data.get("audio_hex", "")

            if not session_id or session_id not in self._sessions:
                return web.json_response({
                    "success": False,
                    "error": "Invalid or missing session_id"
                }, status=400)

            session = self._sessions[session_id]
            audio_chunk = bytes.fromhex(audio_hex)

            # Process through VAD
            result = session.vad.process_audio(audio_chunk)
            session.total_chunks += 1

            response = {
                "success": True,
                "state": result.state.name,
                "probability": result.probability,
                "event": result.event,
                "turn_ready": False
            }

            # Handle speech start
            if result.event == "start_of_speech":
                session.is_speaking = True
                session.turn_start_time = time.time()
                session.speech_buffer = bytearray(audio_chunk)
                session.events.append(("start", time.time()))
                logger.debug(f"[{session_id}] Speech started")

            # Buffer speech audio
            elif session.is_speaking:
                session.speech_buffer.extend(audio_chunk)

            # Handle speech end
            if result.event == "end_of_speech":
                session.is_speaking = False
                session.events.append(("end", time.time()))

                # Return accumulated turn audio
                turn_audio = bytes(session.speech_buffer)
                duration_ms = len(turn_audio) * 1000 // (16000 * 2)

                if duration_ms >= 300:  # Minimum 300ms
                    response["turn_ready"] = True
                    response["turn_audio_hex"] = turn_audio.hex()
                    response["turn_duration_ms"] = duration_ms
                    logger.info(f"[{session_id}] Turn complete: {duration_ms}ms")
                else:
                    logger.debug(f"[{session_id}] Turn too short: {duration_ms}ms")

                session.speech_buffer = bytearray()
                session.turn_start_time = None

            return web.json_response(response)

        except Exception as e:
            logger.error(f"VAD chunk error: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def vad_stop_handler(self, request: web.Request) -> web.Response:
        """Stop a VAD session."""
        try:
            data = await request.json() if request.body_exists else {}
            session_id = data.get("session_id")

            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                session.vad.stop()

                stats = {
                    "total_chunks": session.total_chunks,
                    "events": len(session.events)
                }

                del self._sessions[session_id]
                logger.info(f"VAD session stopped: {session_id}")

                return web.json_response({
                    "success": True,
                    "session_id": session_id,
                    "stats": stats
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Session not found"
                }, status=404)

        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def vad_status_handler(self, request: web.Request) -> web.Response:
        """Get VAD session status."""
        session_id = request.query.get("session_id")

        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            return web.json_response({
                "success": True,
                "session_id": session_id,
                "state": session.vad.state.name if session.vad else "STOPPED",
                "is_speaking": session.is_speaking,
                "buffer_size": len(session.speech_buffer),
                "total_chunks": session.total_chunks
            })
        else:
            return web.json_response({
                "success": True,
                "active_sessions": list(self._sessions.keys())
            })

    async def process_with_vad_handler(self, request: web.Request) -> web.Response:
        """
        Process audio with automatic VAD turn detection.

        This endpoint accepts complete audio and validates it through VAD
        before processing through the full pipeline.

        Request:
            {
                "audio_hex": "hex-encoded PCM audio",
                "session_id": "optional orchestrator session id"
            }

        Response:
            Same as /api/voice/process but with added VAD info
        """
        try:
            data = await request.json()
            audio_hex = data.get("audio_hex", "")
            session_id = data.get("session_id")

            if not audio_hex:
                return web.json_response({
                    "success": False,
                    "error": "Missing audio_hex"
                }, status=400)

            audio_data = bytes.fromhex(audio_hex)

            # Quick VAD validation
            vad = FluxionVAD(self.vad_config)
            vad.start()

            # Process entire audio to check for speech
            chunk_size = 320  # 10ms at 16kHz
            has_speech = False
            max_prob = 0.0

            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                if len(chunk) < chunk_size:
                    chunk = chunk + bytes(chunk_size - len(chunk))
                result = vad.process_audio(chunk)
                max_prob = max(max_prob, result.probability)
                if result.probability > self.vad_config.vad_threshold:
                    has_speech = True

            vad.stop()

            if not has_speech:
                return web.json_response({
                    "success": True,
                    "vad": {
                        "has_speech": False,
                        "max_probability": max_prob,
                        "skipped": True
                    },
                    "response": "",
                    "transcription": ""
                })

            # Speech detected - process through pipeline
            # Add WAV header to PCM data before sending to Groq (Groq expects WAV, not raw PCM)
            wav_data = add_wav_header(audio_data)
            transcription = await self.groq.transcribe_audio(wav_data)

            result = await self.orchestrator.process(
                user_input=transcription,
                session_id=session_id
            )

            # Build response
            response = {
                "success": True,
                "vad": {
                    "has_speech": True,
                    "max_probability": max_prob
                },
                "transcription": transcription,
                "response": result.response,
                "intent": result.intent,
                "layer": result.layer.value,
                "audio_base64": result.audio_bytes.hex() if result.audio_bytes else "",
                "session_id": result.session_id,
                "latency_ms": result.latency_ms
            }

            if result.booking_created:
                response["booking_action"] = {
                    "action": "booking_created",
                    "booking_id": result.booking_id,
                    "context": result.booking_context
                }
            elif result.booking_context:
                response["booking_action"] = {
                    "action": "booking_in_progress",
                    "context": result.booking_context
                }

            return web.json_response(response)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    def cleanup_stale_sessions(self, max_age_seconds: int = 300):
        """Remove VAD sessions older than max_age_seconds."""
        now = time.time()
        stale = [
            sid for sid, session in self._sessions.items()
            if session.turn_start_time and (now - session.turn_start_time) > max_age_seconds
        ]
        for sid in stale:
            self._sessions[sid].vad.stop()
            del self._sessions[sid]
            logger.info(f"Cleaned up stale VAD session: {sid}")
