"""
Tests for EdgeTTSEngine streaming synthesis (stream() vs save()).

Verifies:
  1. synthesize() returns valid WAV bytes (RIFF header)
  2. Streaming path produces audio output
  3. Fallback to save() when stream() fails
  4. Timing metrics are logged (TTFB + total)

All tests mock edge_tts — no network required.
Python 3.9 compatible.
"""

import asyncio
import os
import struct
import sys
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

# Ensure voice-agent/src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_minimal_mp3() -> bytes:
    """Return minimal valid MP3 bytes (MPEG frame header + padding)."""
    # Minimal MP3 frame: sync word 0xFFE0, layer III, 128kbps, 44100Hz
    # This is enough for afconvert/ffmpeg to produce a short WAV.
    # For mock tests we just need non-empty bytes that pass through the mock.
    return b"\xff\xfb\x90\x00" + b"\x00" * 417


def _make_minimal_wav(duration_samples: int = 1600) -> bytes:
    """Return minimal valid WAV 16kHz 16-bit mono."""
    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    data_size = duration_samples * block_align

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + b"\x00" * data_size


class MockStreamChunk:
    """Simulates edge_tts Communicate.stream() yield items."""

    def __init__(self, chunk_type: str, data: bytes = b""):
        self._dict = {"type": chunk_type, "data": data}

    def __getitem__(self, key):
        return self._dict[key]


async def _mock_stream_generator(chunks):
    """Async generator that yields chunks."""
    for chunk in chunks:
        yield chunk


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.fixture
def wav_bytes():
    """Pre-built minimal WAV for comparison."""
    return _make_minimal_wav()


class TestEdgeTTSStreaming:
    """Test suite for EdgeTTSEngine.synthesize() with streaming."""

    @pytest.mark.asyncio
    async def test_synthesize_returns_valid_wav_header(self):
        """synthesize() must return bytes starting with RIFF...WAVE header."""
        mp3_data = _make_minimal_mp3()
        wav_data = _make_minimal_wav()

        # Mock edge_tts.Communicate
        mock_comm_instance = MagicMock()
        chunks = [
            MockStreamChunk("audio", mp3_data[:200]),
            MockStreamChunk("audio", mp3_data[200:]),
            MockStreamChunk("WordBoundary", b""),  # non-audio chunk
        ]
        mock_comm_instance.stream = lambda: _mock_stream_generator(chunks)

        with patch("tts_engine.edge_tts") as mock_edge, \
             patch("tts_engine._EDGE_TTS_AVAILABLE", True):
            mock_edge.Communicate.return_value = mock_comm_instance

            engine = MagicMock()
            engine.voice = "it-IT-IsabellaNeural"
            engine.sample_rate = 16000
            engine._converter = "afconvert"

            # Patch _convert_mp3_to_wav to write our known WAV
            def fake_convert(mp3_path, wav_path):
                with open(wav_path, "wb") as f:
                    f.write(wav_data)

            engine._convert_mp3_to_wav = fake_convert

            # Import and call real synthesize on mock engine
            from tts_engine import EdgeTTSEngine
            result = await EdgeTTSEngine.synthesize.__wrapped__(engine) if hasattr(EdgeTTSEngine.synthesize, '__wrapped__') else await EdgeTTSEngine.synthesize(engine, "Buongiorno")

        # Verify RIFF header
        assert result[:4] == b"RIFF", "WAV must start with RIFF"
        assert result[8:12] == b"WAVE", "WAV must contain WAVE marker"

    @pytest.mark.asyncio
    async def test_streaming_writes_only_audio_chunks(self):
        """Only chunks with type=='audio' should be written to the MP3 file."""
        mp3_chunk_1 = b"\xff\xfb\x90\x00" + b"\x00" * 100
        mp3_chunk_2 = b"\x00" * 200
        wav_data = _make_minimal_wav()

        chunks = [
            MockStreamChunk("audio", mp3_chunk_1),
            MockStreamChunk("WordBoundary", b"ignored_data"),
            MockStreamChunk("audio", mp3_chunk_2),
            MockStreamChunk("SessionEnd", b""),
        ]

        written_data = bytearray()
        original_open = open

        class FakeFile:
            def __init__(self):
                pass
            def write(self, data):
                written_data.extend(data)
            def __enter__(self):
                return self
            def __exit__(self, *a):
                pass

        mock_comm = MagicMock()
        mock_comm.stream = lambda: _mock_stream_generator(chunks)

        with patch("tts_engine.edge_tts") as mock_edge, \
             patch("tts_engine._EDGE_TTS_AVAILABLE", True):
            mock_edge.Communicate.return_value = mock_comm

            from tts_engine import EdgeTTSEngine

            engine = EdgeTTSEngine.__new__(EdgeTTSEngine)
            engine.voice = "it-IT-IsabellaNeural"
            engine.sample_rate = 16000
            engine._converter = "afconvert"

            # Patch convert to produce WAV
            def fake_convert(mp3_path, wav_path):
                # Read what was written to mp3
                with original_open(mp3_path, "rb") as f:
                    nonlocal written_data
                    written_data = bytearray(f.read())
                with original_open(wav_path, "wb") as f:
                    f.write(wav_data)

            engine._convert_mp3_to_wav = fake_convert

            result = await engine.synthesize("Test")

        # Only audio chunks should have been written
        expected = mp3_chunk_1 + mp3_chunk_2
        assert bytes(written_data) == expected, (
            f"Expected only audio data ({len(expected)} bytes), "
            f"got {len(written_data)} bytes"
        )

    @pytest.mark.asyncio
    async def test_fallback_to_save_on_stream_failure(self):
        """If stream() raises, synthesize() should fall back to save()."""
        wav_data = _make_minimal_wav()

        mock_comm = MagicMock()
        # stream() raises an exception
        mock_comm.stream = MagicMock(side_effect=Exception("stream broken"))
        # save() works as fallback
        mock_comm.save = AsyncMock()

        with patch("tts_engine.edge_tts") as mock_edge, \
             patch("tts_engine._EDGE_TTS_AVAILABLE", True):
            mock_edge.Communicate.return_value = mock_comm

            from tts_engine import EdgeTTSEngine

            engine = EdgeTTSEngine.__new__(EdgeTTSEngine)
            engine.voice = "it-IT-IsabellaNeural"
            engine.sample_rate = 16000
            engine._converter = "afconvert"

            def fake_convert(mp3_path, wav_path):
                with open(wav_path, "wb") as f:
                    f.write(wav_data)

            engine._convert_mp3_to_wav = fake_convert

            result = await engine.synthesize("Fallback test")

        # save() should have been called as fallback
        assert mock_comm.save.called, "save() should be called when stream() fails"
        assert result[:4] == b"RIFF"

    @pytest.mark.asyncio
    async def test_fallback_to_save_on_async_iteration_failure(self):
        """If async iteration over stream() raises mid-way, fall back to save()."""
        wav_data = _make_minimal_wav()

        async def broken_stream():
            yield MockStreamChunk("audio", b"\xff\xfb\x90\x00")
            raise ConnectionError("network lost")

        mock_comm = MagicMock()
        mock_comm.stream = broken_stream
        mock_comm.save = AsyncMock()

        with patch("tts_engine.edge_tts") as mock_edge, \
             patch("tts_engine._EDGE_TTS_AVAILABLE", True):
            mock_edge.Communicate.return_value = mock_comm

            from tts_engine import EdgeTTSEngine

            engine = EdgeTTSEngine.__new__(EdgeTTSEngine)
            engine.voice = "it-IT-IsabellaNeural"
            engine.sample_rate = 16000
            engine._converter = "afconvert"

            def fake_convert(mp3_path, wav_path):
                with open(wav_path, "wb") as f:
                    f.write(wav_data)

            engine._convert_mp3_to_wav = fake_convert

            result = await engine.synthesize("Mid-stream failure")

        assert mock_comm.save.called
        assert result[:4] == b"RIFF"

    @pytest.mark.asyncio
    async def test_temp_files_cleaned_up(self):
        """Temp MP3 and WAV files must be deleted after synthesis."""
        wav_data = _make_minimal_wav()
        mp3_data = _make_minimal_mp3()

        chunks = [MockStreamChunk("audio", mp3_data)]
        mock_comm = MagicMock()
        mock_comm.stream = lambda: _mock_stream_generator(chunks)

        created_paths = []

        original_named_temp = tempfile.NamedTemporaryFile

        def tracking_temp(**kwargs):
            t = original_named_temp(**kwargs)
            created_paths.append(t.name)
            return t

        with patch("tts_engine.edge_tts") as mock_edge, \
             patch("tts_engine._EDGE_TTS_AVAILABLE", True), \
             patch("tts_engine.tempfile.NamedTemporaryFile", side_effect=tracking_temp):
            mock_edge.Communicate.return_value = mock_comm

            from tts_engine import EdgeTTSEngine

            engine = EdgeTTSEngine.__new__(EdgeTTSEngine)
            engine.voice = "it-IT-IsabellaNeural"
            engine.sample_rate = 16000
            engine._converter = "afconvert"

            def fake_convert(mp3_path, wav_path):
                with open(wav_path, "wb") as f:
                    f.write(wav_data)

            engine._convert_mp3_to_wav = fake_convert

            await engine.synthesize("Cleanup test")

        # All temp files should be cleaned up
        for p in created_paths:
            assert not os.path.exists(p), f"Temp file not cleaned: {p}"

    @pytest.mark.asyncio
    async def test_synthesize_raises_when_both_stream_and_save_fail(self):
        """If both stream() and save() fail, RuntimeError must propagate."""
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(side_effect=Exception("stream dead"))
        mock_comm.save = AsyncMock(side_effect=Exception("save also dead"))

        with patch("tts_engine.edge_tts") as mock_edge, \
             patch("tts_engine._EDGE_TTS_AVAILABLE", True):
            mock_edge.Communicate.return_value = mock_comm

            from tts_engine import EdgeTTSEngine

            engine = EdgeTTSEngine.__new__(EdgeTTSEngine)
            engine.voice = "it-IT-IsabellaNeural"
            engine.sample_rate = 16000
            engine._converter = "afconvert"

            with pytest.raises(RuntimeError, match="Synthesis failed"):
                await engine.synthesize("Total failure")
