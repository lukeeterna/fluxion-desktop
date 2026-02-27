"""
Silero VAD Integration for Fluxion Voice Agent
===============================================

Professional Voice Activity Detection using Silero VAD (ONNX Runtime)
or webrtcvad as fallback (NO onnxruntime dependency).

Features:
- Real-time voice activity detection
- Configurable sensitivity thresholds
- Start/End of speech detection
- Audio buffering with prefix padding
- Silence duration detection
- Fallback to webrtcvad if onnxruntime unavailable

Note: File retains original name for import compatibility.
"""

import numpy as np
import os
import struct
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable, List
import logging
import collections

logger = logging.getLogger(__name__)

# Audio constants
BYTES_PER_SAMPLE = 2
SAMPLE_RATE = 16000

# Silero VAD v5 uses fixed 512-sample chunks at 16kHz (32ms per chunk)
SILERO_CHUNK_SAMPLES = 512
SILERO_CHUNK_BYTES = SILERO_CHUNK_SAMPLES * BYTES_PER_SAMPLE  # 1024
SILERO_CHUNK_MS = SILERO_CHUNK_SAMPLES * 1000 // SAMPLE_RATE  # 32

# webrtcvad uses 30ms chunks at 16kHz (480 samples)
WEBRTC_CHUNK_MS = 30
WEBRTC_CHUNK_SAMPLES = 480  # 30ms at 16kHz
WEBRTC_CHUNK_BYTES = WEBRTC_CHUNK_SAMPLES * BYTES_PER_SAMPLE  # 960

# Try to import onnxruntime, fallback to webrtcvad
try:
    import onnxruntime
    HAS_ONNX = True
    logger.info("Using Silero VAD (ONNX Runtime)")
except ImportError:
    HAS_ONNX = False
    logger.info("onnxruntime not available, using webrtcvad fallback")

try:
    import webrtcvad
    HAS_WEBRTC = True
except ImportError:
    HAS_WEBRTC = False


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
    dump_path: str = os.path.join(os.environ.get("TEMP", "/tmp"), "vad_debug")


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

    Uses Silero VAD (ONNX Runtime) for accurate speech detection if available,
    otherwise falls back to webrtcvad.
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
        self._session = None  # onnxruntime.InferenceSession or webrtcvad.Vad
        self._vad_type = "unknown"

        # Silero RNN hidden state
        self._h_state: Optional[np.ndarray] = None
        self._sr_tensor: Optional[np.ndarray] = None

        # webrtcvad state
        self._webrtc_vad = None
        self._webrtc_buffer = bytearray()
        self._webrtc_probs = collections.deque(maxlen=30)  # ~1 second of history

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

        # Resolve model path (for Silero)
        if not self.config.model_path:
            self.config.model_path = self._find_model()

        # Callbacks
        self._on_speech_start: Optional[Callable] = None
        self._on_speech_end: Optional[Callable] = None

    @staticmethod
    def _find_model() -> str:
        """Find the Silero VAD ONNX model file."""
        # voice-agent/models/silero_vad.onnx
        base = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)
        )))
        return os.path.join(base, "models", "silero_vad.onnx")

    def start(self) -> None:
        """Initialize VAD engine with Silero ONNX model or webrtcvad fallback."""
        # Try Silero first if available
        if HAS_ONNX and os.path.exists(self.config.model_path):
            self._start_silero()
        elif HAS_WEBRTC:
            self._start_webrtc()
        else:
            raise RuntimeError(
                "No VAD engine available. Install either onnxruntime+silero "
                "or webrtcvad-wheels."
            )

    def _start_silero(self) -> None:
        """Initialize Silero VAD (ONNX Runtime)."""
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
        self._vad_type = "silero"

        # Silero v5 state: [2, batch=1, 128]
        self._h_state = np.zeros((2, 1, 128), dtype=np.float32)
        self._sr_tensor = np.array(SAMPLE_RATE, dtype=np.int64)

        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info("FluxionVAD (Silero) started")

    def _start_webrtc(self) -> None:
        """Initialize webrtcvad as fallback."""
        self._webrtc_vad = webrtcvad.Vad(2)  # Aggressiveness 2 (medium)
        self._vad_type = "webrtc"
        self._webrtc_buffer = bytearray()
        self._webrtc_probs.clear()

        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info("FluxionVAD (webrtcvad) started")

    def stop(self) -> None:
        """Stop VAD engine."""
        self._session = None
        self._h_state = None
        self._sr_tensor = None
        self._webrtc_vad = None
        self._webrtc_buffer = bytearray()
        self._webrtc_probs.clear()
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.info(f"FluxionVAD ({self._vad_type}) stopped")

    def reset(self) -> None:
        """Reset state without stopping the session."""
        if self._vad_type == "silero" and self._h_state is not None:
            self._h_state = np.zeros((2, 1, 128), dtype=np.float32)
        elif self._vad_type == "webrtc":
            self._webrtc_probs.clear()
        self.state = VADState.IDLE
        self.probe_window.clear()
        self.audio_buffer.clear()
        logger.debug(f"FluxionVAD ({self._vad_type}) reset")

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
        if self._vad_type == "silero":
            return self._process_audio_silero(audio_data)
        elif self._vad_type == "webrtc":
            return self._process_audio_webrtc(audio_data)
        else:
            raise RuntimeError("VAD not started. Call start() first.")

    def _process_audio_silero(self, audio_data: bytes) -> VADResult:
        """Process audio using Silero VAD."""
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

    def _process_audio_webrtc(self, audio_data: bytes) -> VADResult:
        """Process audio using webrtcvad as fallback."""
        # Buffer incoming audio
        self._webrtc_buffer.extend(audio_data)

        # Need 480 samples (960 bytes) for one webrtcvad chunk (30ms)
        if len(self._webrtc_buffer) < WEBRTC_CHUNK_BYTES:
            return VADResult(
                is_speech=self.state == VADState.SPEAKING,
                probability=1.0 if self.state == VADState.SPEAKING else 0.0,
                state=self.state
            )

        # Process all complete chunks in buffer
        while len(self._webrtc_buffer) >= WEBRTC_CHUNK_BYTES:
            audio_chunk = bytes(self._webrtc_buffer[:WEBRTC_CHUNK_BYTES])
            self._webrtc_buffer = self._webrtc_buffer[WEBRTC_CHUNK_BYTES:]

            # webrtcvad expects bytes, returns bool
            is_speech = self._webrtc_vad.is_speech(audio_chunk, SAMPLE_RATE)
            # Convert to probability (webrtcvad is binary)
            prob = 0.9 if is_speech else 0.1
            self._webrtc_probs.append(prob)

        # Use recent average as current probability
        if self._webrtc_probs:
            avg_prob = sum(self._webrtc_probs) / len(self._webrtc_probs)
        else:
            avg_prob = 0.0

        # Update probe window for state machine
        self.probe_window.append(avg_prob)
        if len(self.probe_window) > self.window_size:
            self.probe_window.pop(0)

        # Check state transitions
        return self._check_state_transition(avg_prob)

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

    print(f"Using VAD: {vad._vad_type}")
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
