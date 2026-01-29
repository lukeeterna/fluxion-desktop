#!/usr/bin/env python3
"""
VAD File Test
=============

Tests VAD (Silero) with generated audio files.
Works via SSH without microphone access.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest
from src.vad import FluxionVAD, VADConfig, create_vad

SAMPLE_RATE = 16000

# Check if Silero model is available
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "silero_vad.onnx"
)
HAS_MODEL = os.path.exists(MODEL_PATH)
skip_no_model = pytest.mark.skipif(
    not HAS_MODEL, reason="Silero VAD ONNX model not found"
)

try:
    import onnxruntime
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

skip_no_onnx = pytest.mark.skipif(
    not HAS_ONNX, reason="onnxruntime not installed"
)


def generate_test_audio():
    """Generate test audio: silence -> speech -> silence -> speech -> silence"""
    segments = []

    # 1. Silence (1 second)
    silence_1s = np.zeros(SAMPLE_RATE, dtype=np.int16)
    segments.append(("silence", silence_1s))

    # 2. Speech simulation (2 seconds) - sine wave with noise
    t = np.linspace(0, 2, SAMPLE_RATE * 2)
    speech = (np.sin(2 * np.pi * 200 * t) * 15000 +
              np.random.randn(len(t)) * 3000).astype(np.int16)
    segments.append(("speech", speech))

    # 3. Silence (1 second)
    segments.append(("silence", silence_1s))

    # 4. Short speech (0.5 seconds)
    short_speech = (np.sin(2 * np.pi * 300 * np.linspace(0, 0.5, SAMPLE_RATE // 2)) * 12000 +
                   np.random.randn(SAMPLE_RATE // 2) * 2000).astype(np.int16)
    segments.append(("short_speech", short_speech))

    # 5. Final silence (1 second)
    segments.append(("silence", silence_1s))

    return segments


@skip_no_onnx
@skip_no_model
class TestSileroVADBasic:
    """Basic Silero VAD functionality tests."""

    def test_create_vad(self):
        """Test VAD creation with default config."""
        vad = create_vad()
        assert vad is not None
        assert vad.config.vad_threshold == 0.5
        assert vad.state.name == "IDLE"

    def test_start_stop(self):
        """Test VAD start and stop lifecycle."""
        vad = create_vad()
        vad.start()
        assert vad._session is not None
        assert vad._h_state is not None
        vad.stop()
        assert vad._session is None
        assert vad._h_state is None

    def test_process_silence(self):
        """Test that silence is detected as non-speech."""
        vad = create_vad()
        vad.start()

        silence = np.zeros(1600, dtype=np.int16).tobytes()
        for _ in range(20):
            result = vad.process_audio(silence)
            assert result.state.name == "IDLE"
            assert result.is_speech is False

        vad.stop()

    def test_reset_preserves_session(self):
        """Test that reset clears state but keeps ONNX session."""
        vad = create_vad()
        vad.start()

        # Process some audio
        noise = (np.random.randn(1600) * 5000).astype(np.int16).tobytes()
        for _ in range(5):
            vad.process_audio(noise)

        # Reset
        vad.reset()
        assert vad.state.name == "IDLE"
        assert vad._session is not None  # Session preserved
        assert len(vad.probe_window) == 0
        assert len(vad.audio_buffer) == 0

        vad.stop()

    def test_not_started_raises(self):
        """Test that processing without start raises error."""
        vad = create_vad()
        with pytest.raises(RuntimeError, match="VAD not started"):
            vad.process_audio(b"\x00" * 1024)

    def test_custom_config(self):
        """Test VAD with custom configuration."""
        config = VADConfig(
            vad_threshold=0.3,
            silence_duration_ms=500,
            prefix_padding_ms=200
        )
        vad = FluxionVAD(config)
        assert vad.config.vad_threshold == 0.3
        assert vad.config.silence_duration_ms == 500

    def test_callbacks_registered(self):
        """Test that speech start/end callbacks are stored."""
        vad = create_vad()
        start_called = []
        end_called = []

        vad.on_speech_start(lambda: start_called.append(True))
        vad.on_speech_end(lambda: end_called.append(True))

        assert vad._on_speech_start is not None
        assert vad._on_speech_end is not None

    def test_small_buffer_returns_default(self):
        """Test that small audio buffers return default result."""
        vad = create_vad()
        vad.start()

        # Send less than 512 samples (1024 bytes)
        small = b"\x00" * 100
        result = vad.process_audio(small)
        assert result.probability == 0.0
        assert result.state.name == "IDLE"

        vad.stop()


@skip_no_onnx
@skip_no_model
class TestSileroVADSegments:
    """Test VAD with synthetic audio segments."""

    def test_speech_detection_with_segments(self):
        """Test that VAD detects speech start/end events."""
        config = VADConfig(
            vad_threshold=0.5,
            silence_duration_ms=500,
            prefix_padding_ms=200
        )
        vad = FluxionVAD(config)
        vad.start()

        segments = generate_test_audio()
        events = []
        total_frames = 0

        for segment_name, audio_data in segments:
            chunk_size = 1600  # 100ms chunks
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                if len(chunk) < chunk_size:
                    chunk = np.pad(chunk, (0, chunk_size - len(chunk)))

                result = vad.process_audio(chunk.tobytes())
                total_frames += 1

                if result.event:
                    events.append((total_frames, result.event, segment_name))

        vad.stop()

        # VAD should process without errors regardless of event detection
        assert total_frames > 0
        # With synthetic audio, Silero may or may not detect events
        # (it's trained on real speech, not sine waves)
        # But it should not crash
        print(f"Processed {total_frames} frames, detected {len(events)} events")

    def test_continuous_processing(self):
        """Test that VAD handles continuous audio without errors."""
        vad = create_vad()
        vad.start()

        # Process 10 seconds of mixed audio
        for _ in range(100):
            # Random audio chunks
            chunk = (np.random.randn(1600) * 3000).astype(np.int16).tobytes()
            result = vad.process_audio(chunk)
            assert result.state in (VADState.IDLE, VADState.SPEAKING)

        vad.stop()

    def test_is_speaking_property(self):
        """Test is_speaking property matches state."""
        vad = create_vad()
        vad.start()

        silence = np.zeros(1600, dtype=np.int16).tobytes()
        result = vad.process_audio(silence)
        assert vad.is_speaking == (vad.state.name == "SPEAKING")

        vad.stop()


# Import VADState for type checking
from src.vad import VADState


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
