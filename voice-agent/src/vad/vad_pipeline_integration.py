"""
VAD Pipeline Integration for Fluxion Voice Agent
=================================================

Integrates TEN VAD with the existing VoicePipeline for professional
turn-based conversation management.

Features:
- Real-time voice activity detection
- Automatic end-of-turn detection
- Audio buffering with speech region extraction
- Integration with VoicePipeline.process_audio()
"""

import asyncio
import numpy as np
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
import logging
import time

from .ten_vad_integration import FluxionVAD, VADConfig, VADState

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2


@dataclass
class TurnConfig:
    """Configuration for turn-based conversation."""
    # VAD settings
    vad_threshold: float = 0.5
    prefix_padding_ms: int = 300    # Keep 300ms before speech start
    silence_duration_ms: int = 700  # End turn after 700ms silence

    # Turn limits
    max_turn_duration_s: float = 30.0   # Max turn length
    min_turn_duration_ms: int = 500     # Min speech to process

    # Barge-in settings
    allow_barge_in: bool = True
    barge_in_threshold_ms: int = 200    # Min speech to interrupt TTS


@dataclass
class TurnResult:
    """Result from a conversation turn."""
    audio_data: bytes
    duration_ms: int
    was_interrupted: bool = False
    confidence: float = 1.0


class VADPipelineManager:
    """
    Manages VAD-controlled turns for the voice pipeline.

    This class coordinates audio capture, VAD processing, and
    turn detection for natural conversation flow.

    Example:
        manager = VADPipelineManager(pipeline)
        await manager.start()

        # Audio frames come from microphone
        while recording:
            result = manager.process_frame(audio_chunk)
            if result.event == "end_of_speech":
                # Process complete turn
                response = await manager.process_turn()
    """

    def __init__(
        self,
        pipeline,  # VoicePipeline instance
        config: Optional[TurnConfig] = None
    ):
        self.pipeline = pipeline
        self.config = config or TurnConfig()

        # Initialize VAD
        vad_config = VADConfig(
            vad_threshold=self.config.vad_threshold,
            prefix_padding_ms=self.config.prefix_padding_ms,
            silence_duration_ms=self.config.silence_duration_ms
        )
        self.vad = FluxionVAD(vad_config)

        # Turn state
        self.is_listening = False
        self.speech_buffer: List[bytes] = []
        self.prefix_buffer: List[bytes] = []  # For keeping audio before speech
        self.turn_start_time: Optional[float] = None

        # TTS state (for barge-in)
        self.is_speaking = False
        self.barge_in_detected = False

        # Callbacks
        self._on_turn_start: Optional[Callable] = None
        self._on_turn_end: Optional[Callable[[bytes], Any]] = None
        self._on_barge_in: Optional[Callable] = None

        # Stats
        self.stats = {
            "turns_processed": 0,
            "barge_ins": 0,
            "avg_turn_duration_ms": 0.0
        }

        logger.info(f"VADPipelineManager initialized: threshold={self.config.vad_threshold}")

    async def start(self) -> None:
        """Start the VAD pipeline manager."""
        self.vad.start()
        self.is_listening = True
        self.speech_buffer.clear()
        self.prefix_buffer.clear()
        self.turn_start_time = None
        logger.info("VADPipelineManager started")

    async def stop(self) -> None:
        """Stop the VAD pipeline manager."""
        self.is_listening = False
        self.vad.stop()
        logger.info(f"VADPipelineManager stopped. Stats: {self.stats}")

    def on_turn_start(self, callback: Callable) -> None:
        """Register callback for turn start."""
        self._on_turn_start = callback

    def on_turn_end(self, callback: Callable[[bytes], Any]) -> None:
        """Register callback for turn end with audio data."""
        self._on_turn_end = callback

    def on_barge_in(self, callback: Callable) -> None:
        """Register callback for barge-in detection."""
        self._on_barge_in = callback

    def set_speaking(self, speaking: bool) -> None:
        """Set TTS speaking state (for barge-in detection)."""
        self.is_speaking = speaking
        if not speaking:
            self.barge_in_detected = False

    def process_frame(self, audio_chunk: bytes) -> Dict[str, Any]:
        """
        Process an audio frame through VAD.

        Args:
            audio_chunk: Raw PCM audio bytes (16-bit, 16kHz, mono)

        Returns:
            Dict with:
                - state: Current VAD state
                - event: "start_of_speech", "end_of_speech", or None
                - should_process: True if turn is complete and ready
        """
        if not self.is_listening:
            return {"state": "idle", "event": None, "should_process": False}

        # Always buffer recent audio for prefix
        self.prefix_buffer.append(audio_chunk)
        max_prefix_frames = (self.config.prefix_padding_ms * SAMPLE_RATE) // (1000 * len(audio_chunk) // BYTES_PER_SAMPLE)
        if len(self.prefix_buffer) > max(1, max_prefix_frames):
            self.prefix_buffer.pop(0)

        # Process through VAD
        result = self.vad.process_audio(audio_chunk)

        response = {
            "state": result.state.name,
            "probability": result.probability,
            "event": result.event,
            "should_process": False
        }

        # Handle speech start
        if result.event == "start_of_speech":
            self.turn_start_time = time.time()

            # Include prefix audio
            self.speech_buffer = list(self.prefix_buffer)
            self.speech_buffer.append(audio_chunk)

            # Check for barge-in
            if self.is_speaking and self.config.allow_barge_in:
                self.barge_in_detected = True
                self.stats["barge_ins"] += 1
                logger.info("Barge-in detected!")
                if self._on_barge_in:
                    self._on_barge_in()

            if self._on_turn_start:
                self._on_turn_start()

            logger.debug("Turn started")

        # Buffer speech audio
        elif result.state == VADState.SPEAKING:
            self.speech_buffer.append(audio_chunk)

            # Check turn duration limit
            if self.turn_start_time:
                elapsed = time.time() - self.turn_start_time
                if elapsed > self.config.max_turn_duration_s:
                    logger.warning(f"Turn exceeded max duration ({elapsed:.1f}s), forcing end")
                    result.event = "end_of_speech"
                    response["event"] = "end_of_speech"

        # Handle speech end
        if result.event == "end_of_speech":
            turn_audio = b"".join(self.speech_buffer)
            turn_duration_ms = len(turn_audio) * 1000 // (SAMPLE_RATE * BYTES_PER_SAMPLE)

            # Check minimum duration
            if turn_duration_ms >= self.config.min_turn_duration_ms:
                response["should_process"] = True
                response["audio_data"] = turn_audio
                response["duration_ms"] = turn_duration_ms
                response["was_interrupted"] = self.barge_in_detected

                # Update stats
                self.stats["turns_processed"] += 1
                n = self.stats["turns_processed"]
                old_avg = self.stats["avg_turn_duration_ms"]
                self.stats["avg_turn_duration_ms"] = old_avg + (turn_duration_ms - old_avg) / n

                logger.info(f"Turn complete: {turn_duration_ms}ms")

                if self._on_turn_end:
                    self._on_turn_end(turn_audio)
            else:
                logger.debug(f"Turn too short ({turn_duration_ms}ms), ignoring")

            # Reset for next turn
            self.speech_buffer.clear()
            self.turn_start_time = None
            self.barge_in_detected = False

        return response

    async def process_turn(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process a complete turn through the voice pipeline.

        Args:
            audio_data: Complete turn audio

        Returns:
            Pipeline response dict
        """
        return await self.pipeline.process_audio(audio_data)

    async def handle_turn_complete(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle a complete turn from process_frame.

        Args:
            result: Result dict from process_frame

        Returns:
            Pipeline response if turn was processed, None otherwise
        """
        if not result.get("should_process"):
            return None

        audio_data = result.get("audio_data", b"")
        if not audio_data:
            return None

        return await self.process_turn(audio_data)

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            **self.stats,
            "vad_state": self.vad.state.name if self.vad else "stopped"
        }


def create_vad_pipeline_manager(
    pipeline,
    vad_threshold: float = 0.5,
    silence_ms: int = 700,
    allow_barge_in: bool = True
) -> VADPipelineManager:
    """Create a configured VADPipelineManager."""
    config = TurnConfig(
        vad_threshold=vad_threshold,
        silence_duration_ms=silence_ms,
        allow_barge_in=allow_barge_in
    )
    return VADPipelineManager(pipeline, config)
