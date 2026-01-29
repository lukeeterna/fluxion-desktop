"""
Silero VAD Integration for Fluxion Voice Agent
===============================================

Professional Voice Activity Detection using Silero VAD (ONNX Runtime).
Replaces ten-vad with higher accuracy (95% vs 92%) and better noise handling.

Features:
- Real-time voice activity detection
- Configurable sensitivity thresholds
- Start/End of speech detection
- Audio buffering with prefix padding
- Silence duration detection
- No PyTorch dependency (ONNX Runtime only)

Note: File retains original name for import compatibility.
"""

import numpy as np
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable, List
import logging

logger = logging.getLogger(__name__)

# Audio constants
BYTES_PER_SAMPLE = 2
SAMPLE_RATE = 16000

# Silero VAD v5 uses fixed 512-sample chunks at 16kHz (32ms per chunk)
SILERO_CHUNK_SAMPLES = 512
SILERO_CHUNK_BYTES = SILERO_CHUNK_SAMPLES * BYTES_PER_SAMPLE  # 1024
SILERO_CHUNK_MS = SILERO_CHUNK_SAMPLES * 1000 // SAMPLE_RATE  # 32


class VADState(Enum):
    """VAD state machine states."""
    IDLE = auto()       # Waiting for speech
    SPEAKING = auto()   # User is speaking


@dataclass
class VADConfig:
    """Configuration for VAD processing."""
    # Frame processing (hop_size_ms kept for backwards compat, internally uses 32ms)
    hop_size_ms: int = 10
    sample_rate: int = 16000

    # Detection thresholds
    vad_threshold: float = 0.5

    # Timing (in ms)
    prefix_padding_ms: int = 300
    silence_duration_ms: int = 700

    # Model path (auto-detected if empty)
    model_path: str = ""

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

    Uses Silero VAD (ONNX Runtime) for accurate speech detection.
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
        self._session = None  # onnxruntime.InferenceSession

        # Silero RNN hidden state
        self._h_state: Optional[np.ndarray] = None
        self._sr_tensor: Optional[np.ndarray] = None

        # State machine
        self.state = VADState.IDLE
        self.probe_window: List[float] = []

        # Window sizes in Silero chunks (32ms each)
        self.silence_window_size = max(1, self.config.silence_duration_ms // SILERO_CHUNK_MS)
        self.prefix_window_size = max(1, self.config.prefix_padding_ms // SILERO_CHUNK_MS)
        self.window_size = max(self.silence_window_size, self.prefix_window_size)

        # Backwards compat: hop_size used by vad_pipeline_integration.py
        self.hop_size = SILERO_CHUNK_SAMPLES

        # Audio buffer
        self.audio_buffer = bytearray()

        # Resolve model path
        if not self.config.model_path:
            self.config.model_path = self._find_model()

        # Callbacks
        self._on_speech_start: Optional[Callable] = None
        self._on_speech_end: Optional[Callable] = None

        logger.info(
            f"FluxionVAD (Silero) initialized: chunk={SILERO_CHUNK_SAMPLES} samples "
            f"({SILERO_CHUNK_MS}ms), window_size={self.window_size}, "
            f"threshold={self.config.vad_threshold}"
        )

    @staticmethod
    def _find_model() -> str:
        """Find the Silero VAD ONNX model file."""
        # voice-agent/models/silero_vad.onnx
        base = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)
        )))
        return os.path.join(base, "models", "silero_vad.onnx")

    def start(self) -> None:
        """Initialize VAD engine with Silero ONNX model."""
        import onnxruntime

        if not os.path.exists(self.config.model_path):
            raise FileNotFoundError(
                f"Silero VAD model not found at: {self.config.model_path}\n"
                "Download: https://github.com/snakers4/silero-vad/raw/master/"
                "src/silero_vad/data/silero_vad.onnx"
            )

        self._session = onnxruntime.InferenceSession(
            self.config.model_path,
            providers=['CPUExecutionProvider']
        )

        # Silero v5 state: [2, batch=1, 128]
        self._h_state = np.zeros((2, 1, 128), dtype=np.float32)
        self._sr_tensor = np.array(SAMPLE_RATE, dtype=np.int64)

        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info("FluxionVAD (Silero) started")

    def stop(self) -> None:
        """Stop VAD engine."""
        self._session = None
        self._h_state = None
        self._sr_tensor = None
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info("FluxionVAD (Silero) stopped")

    def reset(self) -> None:
        """Reset state without stopping the ONNX session."""
        if self._h_state is not None:
            self._h_state = np.zeros((2, 1, 128), dtype=np.float32)
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.debug("FluxionVAD (Silero) reset")

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
        if self._session is None:
            raise RuntimeError("VAD not started. Call start() first.")

        # Buffer incoming audio
        self.audio_buffer.extend(audio_data)

        # Need 512 samples (1024 bytes) for one Silero chunk
        if len(self.audio_buffer) < SILERO_CHUNK_BYTES:
            return VADResult(
                is_speech=self.state == VADState.SPEAKING,
                probability=0.0,
                state=self.state
            )

        # Extract one chunk
        audio_chunk = self.audio_buffer[:SILERO_CHUNK_BYTES]
        self.audio_buffer = self.audio_buffer[SILERO_CHUNK_BYTES:]

        # Convert int16 PCM to float32 normalized [-1.0, 1.0]
        samples_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
        samples_float = samples_int16.astype(np.float32) / 32768.0

        # Run Silero model: input [1, 512], state [2, 1, 128], sr scalar
        ort_inputs = {
            'input': samples_float.reshape(1, -1),
            'state': self._h_state,
            'sr': self._sr_tensor,
        }

        ort_outputs = self._session.run(None, ort_inputs)
        prob = float(ort_outputs[0].item())
        self._h_state = ort_outputs[1]  # Updated hidden state

        # Update probe window
        self.probe_window.append(prob)
        if len(self.probe_window) > self.window_size:
            self.probe_window.pop(0)

        # Check state transitions
        return self._check_state_transition(prob)

    def _check_state_transition(self, current_probe: float) -> VADResult:
        """Check for state transitions based on probe window."""
        old_state = self.state
        event = None

        if self.state == VADState.IDLE:
            # Need enough probes to check prefix window
            if len(self.probe_window) >= self.prefix_window_size:
                prefix_probes = self.probe_window[-self.prefix_window_size:]
                if all(p >= self.config.vad_threshold for p in prefix_probes):
                    self.state = VADState.SPEAKING
                    event = "start_of_speech"
                    logger.info(
                        f"Speech started (last 3 probes: "
                        f"{[f'{p:.2f}' for p in prefix_probes[-3:]]})"
                    )
                    if self._on_speech_start:
                        self._on_speech_start()

        elif self.state == VADState.SPEAKING:
            # Need enough probes to check silence window
            if len(self.probe_window) >= self.silence_window_size:
                silence_probes = self.probe_window[-self.silence_window_size:]
                if all(p < self.config.vad_threshold for p in silence_probes):
                    self.state = VADState.IDLE
                    event = "end_of_speech"
                    logger.info(
                        f"Speech ended (last 3 probes: "
                        f"{[f'{p:.2f}' for p in silence_probes[-3:]]})"
                    )
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
    # Quick self-test
    logging.basicConfig(level=logging.INFO)

    vad = create_vad()
    vad.start()

    # Simulate audio (silence then speech)
    silence = np.zeros(1600, dtype=np.int16).tobytes()  # 100ms silence
    speech = (np.random.randn(1600) * 5000).astype(np.int16).tobytes()

    print("Processing silence...")
    for _ in range(10):
        result = vad.process_audio(silence)
        print(f"  State: {result.state.name}, Prob: {result.probability:.3f}")

    print("\nProcessing speech...")
    for _ in range(50):
        result = vad.process_audio(speech)
        if result.event:
            print(f"  EVENT: {result.event}")

    print("\nProcessing silence again...")
    for _ in range(100):
        result = vad.process_audio(silence)
        if result.event:
            print(f"  EVENT: {result.event}")

    vad.stop()
    print("\nTest complete!")
