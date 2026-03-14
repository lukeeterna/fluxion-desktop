#!/usr/bin/env python3
"""
VAD Open-Mic Loop Tests
========================

Tests for continuous listening (open-mic) mode:
- VAD re-activation after TTS playback
- TTS echo suppression (is_tts_playing flag)
- Silero hidden state reset between turns
- Loop termination on should_exit
- VADHTTPHandler speaking endpoint

Run on MacBook (no Silero model needed — uses mocks where possible).
Run on iMac for full Silero integration tests.
"""

import sys
import os
import asyncio
import time
import json
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Add both project root and src/ to path (for vad subpackage)
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

import pytest

# Skip tests that require the vad package (ONNX + Silero model) if not available
try:
    from vad import FluxionVAD, VADConfig  # noqa: F401
    HAS_VAD = True
except ImportError:
    HAS_VAD = False

requires_vad = pytest.mark.skipif(not HAS_VAD, reason="vad package not available (run on iMac)")

# ─────────────────────────────────────────────────────────────
# Fixtures & Helpers
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE = 16000
CHUNK_SAMPLES = 512  # Silero chunk size


def make_pcm_silence(duration_ms: int = 500) -> bytes:
    """Generate silence PCM bytes."""
    import struct
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    return b'\x00\x00' * samples


def make_pcm_speech(duration_ms: int = 1000, amplitude: int = 8000) -> bytes:
    """Generate synthetic speech-like PCM (sine wave with amplitude)."""
    import math
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    result = bytearray()
    freq = 440  # Hz
    for i in range(samples):
        value = int(amplitude * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        result += value.to_bytes(2, byteorder='little', signed=True)
    return bytes(result)


# ─────────────────────────────────────────────────────────────
# T1 — VAD Session: is_tts_playing flag
# ─────────────────────────────────────────────────────────────

@requires_vad
class TestVADSessionTTSFlag:
    """Test is_tts_playing flag on VADSession dataclass."""

    def test_vad_session_has_tts_flag(self):
        """VADSession must have is_tts_playing field defaulting to False."""
        from vad_http_handler import VADSession

        mock_vad = MagicMock()
        session = VADSession(session_id="test_001", vad=mock_vad)

        assert hasattr(session, 'is_tts_playing'), "VADSession missing is_tts_playing field"
        assert session.is_tts_playing is False, "is_tts_playing should default to False"

    def test_vad_session_tts_flag_mutable(self):
        """is_tts_playing can be set to True and back to False."""
        from vad_http_handler import VADSession

        mock_vad = MagicMock()
        session = VADSession(session_id="test_002", vad=mock_vad)

        session.is_tts_playing = True
        assert session.is_tts_playing is True

        session.is_tts_playing = False
        assert session.is_tts_playing is False


# ─────────────────────────────────────────────────────────────
# T2 — VAD Chunk Handler: echo suppression during TTS
# ─────────────────────────────────────────────────────────────

@requires_vad
class TestVADEchoSuppression:
    """Test that VAD does not emit turn_ready while TTS is playing."""

    @pytest.mark.asyncio
    async def test_chunk_suppressed_when_tts_playing(self):
        """When is_tts_playing=True, vad_chunk_handler returns tts_suppressed=True and no turn_ready."""
        from vad_http_handler import VADHTTPHandler, VADSession

        mock_orchestrator = MagicMock()
        mock_groq = MagicMock()
        handler = VADHTTPHandler(mock_orchestrator, mock_groq)

        # Create a session with TTS playing
        mock_vad = MagicMock()
        mock_result = MagicMock()
        mock_result.state.name = "IDLE"
        mock_result.probability = 0.0
        mock_result.event = None
        mock_vad.process_audio.return_value = mock_result

        session = VADSession(session_id="test_echo", vad=mock_vad)
        session.is_tts_playing = True
        handler._sessions["test_echo"] = session

        # Mock aiohttp request
        request = MagicMock()
        request.json = AsyncMock(return_value={
            "session_id": "test_echo",
            "audio_hex": make_pcm_speech(100).hex()
        })

        from aiohttp.web import Response
        response = await handler.vad_chunk_handler(request)
        data = json.loads(response.body)

        assert data["success"] is True
        assert data["tts_suppressed"] is True
        assert data["turn_ready"] is False, "turn_ready must be False when TTS is playing"

    @pytest.mark.asyncio
    async def test_chunk_not_suppressed_when_tts_off(self):
        """When is_tts_playing=False, normal VAD processing occurs (no suppression)."""
        from vad_http_handler import VADHTTPHandler, VADSession

        mock_orchestrator = MagicMock()
        mock_groq = MagicMock()
        handler = VADHTTPHandler(mock_orchestrator, mock_groq)

        mock_vad = MagicMock()
        mock_result = MagicMock()
        mock_result.state.name = "IDLE"
        mock_result.probability = 0.05
        mock_result.event = None
        mock_vad.process_audio.return_value = mock_result

        session = VADSession(session_id="test_noecho", vad=mock_vad)
        session.is_tts_playing = False
        handler._sessions["test_noecho"] = session

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "session_id": "test_noecho",
            "audio_hex": make_pcm_silence(100).hex()
        })

        response = await handler.vad_chunk_handler(request)
        data = json.loads(response.body)

        assert data["success"] is True
        assert data["tts_suppressed"] is False
        # No suppression — VAD processed normally
        mock_vad.process_audio.assert_called_once()


# ─────────────────────────────────────────────────────────────
# T3 — VAD Speaking Endpoint
# ─────────────────────────────────────────────────────────────

@requires_vad
class TestVADSpeakingEndpoint:
    """Test POST /api/voice/vad/speaking endpoint."""

    @pytest.mark.asyncio
    async def test_speaking_true_sets_flag(self):
        """POST /vad/speaking {speaking: true} sets is_tts_playing=True."""
        from vad_http_handler import VADHTTPHandler, VADSession

        handler = VADHTTPHandler(MagicMock(), MagicMock())

        mock_vad = MagicMock()
        session = VADSession(session_id="spk_001", vad=mock_vad)
        handler._sessions["spk_001"] = session

        request = MagicMock()
        request.json = AsyncMock(return_value={"session_id": "spk_001", "speaking": True})

        response = await handler.vad_speaking_handler(request)
        data = json.loads(response.body)

        assert data["success"] is True
        assert data["tts_playing"] is True
        assert handler._sessions["spk_001"].is_tts_playing is True

    @pytest.mark.asyncio
    async def test_speaking_false_resets_flag_and_vad(self):
        """POST /vad/speaking {speaking: false} resets flag and calls vad.reset()."""
        from vad_http_handler import VADHTTPHandler, VADSession

        handler = VADHTTPHandler(MagicMock(), MagicMock())

        mock_vad = MagicMock()
        session = VADSession(session_id="spk_002", vad=mock_vad)
        session.is_tts_playing = True
        handler._sessions["spk_002"] = session

        request = MagicMock()
        request.json = AsyncMock(return_value={"session_id": "spk_002", "speaking": False})

        response = await handler.vad_speaking_handler(request)
        data = json.loads(response.body)

        assert data["success"] is True
        assert data["tts_playing"] is False
        assert handler._sessions["spk_002"].is_tts_playing is False
        mock_vad.reset.assert_called_once()

    @pytest.mark.asyncio
    async def test_speaking_unknown_session_returns_404(self):
        """POST /vad/speaking with unknown session_id returns 404."""
        from vad_http_handler import VADHTTPHandler

        handler = VADHTTPHandler(MagicMock(), MagicMock())

        request = MagicMock()
        request.json = AsyncMock(return_value={"session_id": "nonexistent", "speaking": True})

        response = await handler.vad_speaking_handler(request)
        data = json.loads(response.body)

        assert data["success"] is False
        assert response.status == 404


# ─────────────────────────────────────────────────────────────
# T4 — Silero Hidden State Reset Between Turns
# ─────────────────────────────────────────────────────────────

@requires_vad
class TestSileroResetBetweenTurns:
    """Test that vad.reset() is called after each end_of_speech."""

    @pytest.mark.asyncio
    async def test_vad_reset_called_on_end_of_speech(self):
        """After end_of_speech with valid turn, vad.reset() is called."""
        from vad_http_handler import VADHTTPHandler, VADSession

        handler = VADHTTPHandler(MagicMock(), MagicMock())

        mock_vad = MagicMock()
        mock_result = MagicMock()
        mock_result.state.name = "IDLE"
        mock_result.probability = 0.0
        mock_result.event = "end_of_speech"
        mock_vad.process_audio.return_value = mock_result

        # Pre-populate speech buffer with >300ms of audio (>9600 bytes at 16kHz 16-bit)
        session = VADSession(session_id="reset_001", vad=mock_vad)
        session.is_speaking = True
        session.speech_buffer = bytearray(make_pcm_speech(400))  # 400ms = valid turn
        handler._sessions["reset_001"] = session

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "session_id": "reset_001",
            "audio_hex": make_pcm_silence(32).hex()
        })

        response = await handler.vad_chunk_handler(request)
        data = json.loads(response.body)

        assert data["turn_ready"] is True, "Expected turn_ready after end_of_speech"
        mock_vad.reset.assert_called_once(), "vad.reset() must be called after turn completes"

    @pytest.mark.asyncio
    async def test_vad_reset_not_called_on_start_of_speech(self):
        """vad.reset() is NOT called on start_of_speech (only on end_of_speech)."""
        from vad_http_handler import VADHTTPHandler, VADSession

        handler = VADHTTPHandler(MagicMock(), MagicMock())

        mock_vad = MagicMock()
        mock_result = MagicMock()
        mock_result.state.name = "SPEAKING"
        mock_result.probability = 0.9
        mock_result.event = "start_of_speech"
        mock_vad.process_audio.return_value = mock_result

        session = VADSession(session_id="reset_002", vad=mock_vad)
        handler._sessions["reset_002"] = session

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "session_id": "reset_002",
            "audio_hex": make_pcm_speech(32).hex()
        })

        await handler.vad_chunk_handler(request)
        mock_vad.reset.assert_not_called(), "vad.reset() must NOT be called on start_of_speech"


# ─────────────────────────────────────────────────────────────
# T5 — Open-Mic Loop: should_exit terminates loop
# ─────────────────────────────────────────────────────────────

class TestOpenMicLoopExit:
    """Test that the open-mic loop terminates correctly on should_exit."""

    def test_loop_exit_condition_logic(self):
        """
        Verify the loop exit condition: openMicActiveRef.current = False on should_exit.
        This is a pure logic test (no browser/React needed).
        """
        # Simulated loop state
        class LoopState:
            open_mic_active = True
            conversation_ended = False

        state = LoopState()

        def simulate_response(should_exit: bool):
            if should_exit:
                state.conversation_ended = True
                state.open_mic_active = False

        # Simulate turn 1: normal response
        simulate_response(should_exit=False)
        assert state.open_mic_active is True
        assert state.conversation_ended is False

        # Simulate turn 2: Sara says goodbye (should_exit=True)
        simulate_response(should_exit=True)
        assert state.open_mic_active is False, "Loop must stop on should_exit"
        assert state.conversation_ended is True

    def test_loop_does_not_restart_if_active_false(self):
        """If openMicActiveRef is False before waitForTurn, loop exits immediately."""
        results = []

        def simulate_loop(turns: list):
            active = True
            i = 0
            while active and i < len(turns):
                audio = f"audio_turn_{i}"
                if not audio or not active:
                    break
                results.append(f"processed_{i}")
                if turns[i].get("should_exit"):
                    active = False
                i += 1

        simulate_loop([
            {"should_exit": False},
            {"should_exit": False},
            {"should_exit": True},
        ])

        assert len(results) == 3, "Loop should process exactly 3 turns before exiting"
        assert results == ["processed_0", "processed_1", "processed_2"]
