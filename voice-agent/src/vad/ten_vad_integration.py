"""
TEN VAD Integration for Fluxion Voice Agent
============================================

Professional Voice Activity Detection using ten-vad library.
Standalone implementation - NO cloud dependencies.

Features:
- Real-time voice activity detection
- Configurable sensitivity thresholds
- Start/End of speech detection
- Audio buffering with prefix padding
- Silence duration detection
"""

import numpy as np
from ten_vad import TenVad
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Callable, List
import logging

logger = logging.getLogger(__name__)

# Audio constants
BYTES_PER_SAMPLE = 2
SAMPLE_RATE = 16000


class VADState(Enum):
    """VAD state machine states."""
    IDLE = auto()       # Waiting for speech
    SPEAKING = auto()   # User is speaking


@dataclass
class VADConfig:
    """Configuration for VAD processing."""
    # Frame processing
    hop_size_ms: int = 10           # 10ms frames (standard)
    sample_rate: int = 16000        # 16kHz audio

    # Detection thresholds
    vad_threshold: float = 0.5      # Voice probability threshold

    # Timing (in ms)
    prefix_padding_ms: int = 300    # Audio to keep before speech start
    silence_duration_ms: int = 700  # Silence before end-of-speech

    # Debug
    dump_audio: bool = False
    dump_path: str = "/tmp/vad_debug"


@dataclass
class VADResult:
    """Result from VAD processing."""
    is_speech: bool
    probability: float
    state: VADState
    state_changed: bool = False
    event: Optional[str] = None  # "start_of_speech" or "end_of_speech"


class FluxionVAD:
    """
    Professional Voice Activity Detection for Fluxion.

    Uses TEN VAD library for accurate speech detection.
    Provides start/end of speech events for turn management.

    Example:
        vad = FluxionVAD()
        vad.start()

        # Process audio frames
        result = vad.process_audio(audio_bytes)
        if result.event == "start_of_speech":
            # User started speaking
        elif result.event == "end_of_speech":
            # User finished speaking - process STT
    """

    def __init__(self, config: Optional[VADConfig] = None):
        self.config = config or VADConfig()
        self.vad: Optional[TenVad] = None

        # State machine
        self.state = VADState.IDLE
        self.probe_window: List[float] = []

        # Calculate window sizes (in frames)
        self.hop_size = self.config.hop_size_ms * self.config.sample_rate // 1000
        self.silence_window_size = (
            self.config.silence_duration_ms // self.config.hop_size_ms
        )
        self.prefix_window_size = (
            self.config.prefix_padding_ms // self.config.hop_size_ms
        )
        self.window_size = max(self.silence_window_size, self.prefix_window_size)

        # Audio buffer
        self.audio_buffer = bytearray()

        # Callbacks
        self._on_speech_start: Optional[Callable] = None
        self._on_speech_end: Optional[Callable] = None

        logger.info(f"FluxionVAD initialized: hop_size={self.hop_size}, "
                   f"window_size={self.window_size}, threshold={self.config.vad_threshold}")

    def start(self) -> None:
        """Initialize VAD engine."""
        self.vad = TenVad(self.hop_size)
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info("FluxionVAD started")

    def stop(self) -> None:
        """Stop VAD engine."""
        self.vad = None
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info("FluxionVAD stopped")

    def reset(self) -> None:
        """Reset state without stopping."""
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.debug("FluxionVAD reset")

    def on_speech_start(self, callback: Callable) -> None:
        """Register callback for speech start event."""
        self._on_speech_start = callback

    def on_speech_end(self, callback: Callable) -> None:
        """Register callback for speech end event."""
        self._on_speech_end = callback

    def process_audio(self, audio_data: bytes) -> VADResult:
        """
        Process audio frame and detect voice activity.

        Args:
            audio_data: Raw PCM audio bytes (16-bit, 16kHz, mono)

        Returns:
            VADResult with speech detection status and events
        """
        if self.vad is None:
            raise RuntimeError("VAD not started. Call start() first.")

        # Buffer incoming audio
        self.audio_buffer.extend(audio_data)

        # Need enough samples for one hop
        bytes_per_hop = self.hop_size * BYTES_PER_SAMPLE
        if len(self.audio_buffer) < bytes_per_hop:
            return VADResult(
                is_speech=self.state == VADState.SPEAKING,
                probability=0.0,
                state=self.state
            )

        # Extract one hop worth of audio
        audio_chunk = self.audio_buffer[:bytes_per_hop]
        self.audio_buffer = self.audio_buffer[bytes_per_hop:]

        # Convert to numpy and process
        samples = np.frombuffer(audio_chunk, dtype=np.int16)
        probe, _flag = self.vad.process(samples)

        # Update probe window
        self.probe_window.append(probe)
        if len(self.probe_window) > self.window_size:
            self.probe_window.pop(0)

        # Check state transitions
        result = self._check_state_transition(probe)

        return result

    def _check_state_transition(self, current_probe: float) -> VADResult:
        """Check for state transitions based on probe window."""
        if len(self.probe_window) < self.window_size:
            return VADResult(
                is_speech=self.state == VADState.SPEAKING,
                probability=current_probe,
                state=self.state
            )

        old_state = self.state
        event = None

        if self.state == VADState.IDLE:
            # Check for speech start
            prefix_probes = self.probe_window[-self.prefix_window_size:]
            all_above = all(p >= self.config.vad_threshold for p in prefix_probes)

            if all_above:
                self.state = VADState.SPEAKING
                event = "start_of_speech"
                logger.info(f"Speech started (probes: {prefix_probes[-3:]})")

                if self._on_speech_start:
                    self._on_speech_start()

        elif self.state == VADState.SPEAKING:
            # Check for speech end
            silence_probes = self.probe_window[-self.silence_window_size:]
            all_below = all(p < self.config.vad_threshold for p in silence_probes)

            if all_below:
                self.state = VADState.IDLE
                event = "end_of_speech"
                logger.info(f"Speech ended (probes: {silence_probes[-3:]})")

                if self._on_speech_end:
                    self._on_speech_end()

        return VADResult(
            is_speech=self.state == VADState.SPEAKING,
            probability=current_probe,
            state=self.state,
            state_changed=self.state != old_state,
            event=event
        )

    @property
    def is_speaking(self) -> bool:
        """Check if currently detecting speech."""
        return self.state == VADState.SPEAKING


# Convenience function for quick testing
def create_vad(
    threshold: float = 0.5,
    silence_ms: int = 700,
    prefix_ms: int = 300
) -> FluxionVAD:
    """Create a configured VAD instance."""
    config = VADConfig(
        vad_threshold=threshold,
        silence_duration_ms=silence_ms,
        prefix_padding_ms=prefix_ms
    )
    return FluxionVAD(config)


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)

    vad = create_vad()
    vad.start()

    # Simulate audio (silence then speech)
    silence = np.zeros(1600, dtype=np.int16).tobytes()  # 100ms silence
    speech = (np.random.randn(1600) * 5000).astype(np.int16).tobytes()  # Simulated speech

    print("Processing silence...")
    for _ in range(10):
        result = vad.process_audio(silence)
        print(f"  State: {result.state.name}, Prob: {result.probability:.3f}")

    print("\nProcessing speech...")
    for _ in range(50):
        result = vad.process_audio(speech)
        if result.event:
            print(f"  EVENT: {result.event}")
        # print(f"  State: {result.state.name}, Prob: {result.probability:.3f}")

    print("\nProcessing silence again...")
    for _ in range(100):
        result = vad.process_audio(silence)
        if result.event:
            print(f"  EVENT: {result.event}")

    vad.stop()
    print("\nTest complete!")
