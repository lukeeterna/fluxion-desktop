"""
FluxionTTS Adaptive — test suite
Tests: TTSEngineSelector, TTSDownloadManager, PiperTTSEngine latency,
       QwenTTSEngine latency (skipif model absent).

Python 3.9 compatible.
"""

import asyncio
import sys
import time
from pathlib import Path

import pytest

# ── Import path: add voice-agent/src to sys.path ──────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tts_engine import (  # noqa: E402
    TTSMode,
    TTSEngineSelector,
    PiperTTSEngine,
    QwenTTSEngine,
    create_tts_engine,
)
from tts_download_manager import TTSDownloadManager  # noqa: E402


# ─── Availability helpers ──────────────────────────────────────────────────────

def _piper_available() -> bool:
    """Return True if PiperTTSEngine can be instantiated (binary + model present)."""
    try:
        PiperTTSEngine()
        return True
    except RuntimeError:
        return False


def _qwen_model_downloaded() -> bool:
    """Return True if Qwen3-TTS model is downloaded."""
    return TTSDownloadManager.is_model_downloaded()


# ═══════════════════════════════════════════════════════════════════════════════
# TestTTSEngineSelector
# ═══════════════════════════════════════════════════════════════════════════════

class TestTTSEngineSelector:

    def test_detect_hardware_returns_required_keys(self):
        """detect_hardware() must return dict with ram_gb, cpu_cores, avx2, capable."""
        hw = TTSEngineSelector.detect_hardware()
        assert isinstance(hw, dict)
        for key in ("ram_gb", "cpu_cores", "avx2", "capable"):
            assert key in hw, f"Missing key: {key}"

    def test_detect_hardware_ram_positive(self):
        """ram_gb must be a positive number."""
        hw = TTSEngineSelector.detect_hardware()
        assert isinstance(hw["ram_gb"], float)
        assert hw["ram_gb"] > 0

    def test_detect_hardware_cores_positive(self):
        """cpu_cores must be a positive integer."""
        hw = TTSEngineSelector.detect_hardware()
        assert isinstance(hw["cpu_cores"], int)
        assert hw["cpu_cores"] >= 1

    def test_get_mode_fast_override(self):
        """FAST user preference overrides hardware — always returns FAST."""
        hw = {"ram_gb": 32.0, "cpu_cores": 16, "avx2": True, "capable": True}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.FAST)
        assert mode == TTSMode.FAST

    def test_get_mode_quality_override(self):
        """QUALITY user preference overrides hardware — always returns QUALITY."""
        hw = {"ram_gb": 2.0, "cpu_cores": 2, "avx2": False, "capable": False}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.QUALITY)
        assert mode == TTSMode.QUALITY

    def test_get_mode_auto_capable_returns_quality(self):
        """AUTO mode on capable hardware (RAM>=8GB, cores>=4) → QUALITY."""
        hw = {"ram_gb": 16.0, "cpu_cores": 8, "avx2": True, "capable": True}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.AUTO)
        assert mode == TTSMode.QUALITY

    def test_get_mode_auto_incapable_returns_fast(self):
        """AUTO mode on incapable hardware (RAM<8GB or cores<4) → FAST."""
        hw = {"ram_gb": 4.0, "cpu_cores": 4, "avx2": False, "capable": False}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.AUTO)
        assert mode == TTSMode.FAST

    def test_get_engine_fast_returns_piper(self):
        """get_engine(FAST) returns a PiperTTSEngine (or raises RuntimeError if piper absent)."""
        if not _piper_available():
            pytest.skip("Piper binary/model not available on this machine")
        engine = TTSEngineSelector.get_engine(TTSMode.FAST)
        assert isinstance(engine, PiperTTSEngine)

    def test_create_tts_engine_fast(self):
        """create_tts_engine(FAST) returns PiperTTSEngine (or raises if piper absent)."""
        if not _piper_available():
            pytest.skip("Piper binary/model not available on this machine")
        engine = create_tts_engine(user_pref=TTSMode.FAST)
        assert isinstance(engine, PiperTTSEngine)


# ═══════════════════════════════════════════════════════════════════════════════
# TestTTSDownloadManager
# ═══════════════════════════════════════════════════════════════════════════════

class TestTTSDownloadManager:

    def test_read_mode_returns_string(self):
        """read_mode() always returns a string ('quality', 'fast', or 'auto')."""
        mode = TTSDownloadManager.read_mode()
        assert isinstance(mode, str)
        assert mode in ("quality", "fast", "auto")

    def test_write_and_read_mode_fast(self, tmp_path, monkeypatch):
        """write_mode('fast') persists and read_mode() returns 'fast'."""
        tmp_mode_file = tmp_path / ".tts_mode"
        import tts_download_manager
        monkeypatch.setattr(tts_download_manager, "_MODE_FILE", tmp_mode_file)

        TTSDownloadManager.write_mode("fast")
        assert TTSDownloadManager.read_mode() == "fast"

    def test_write_and_read_mode_quality(self, tmp_path, monkeypatch):
        """write_mode('quality') persists and read_mode() returns 'quality'."""
        tmp_mode_file = tmp_path / ".tts_mode"
        import tts_download_manager
        monkeypatch.setattr(tts_download_manager, "_MODE_FILE", tmp_mode_file)

        TTSDownloadManager.write_mode("quality")
        assert TTSDownloadManager.read_mode() == "quality"

    def test_write_invalid_mode_raises(self):
        """write_mode() with invalid value raises AssertionError."""
        with pytest.raises(AssertionError):
            TTSDownloadManager.write_mode("turbo")

    def test_is_model_downloaded_returns_bool(self):
        """is_model_downloaded() always returns a bool."""
        result = TTSDownloadManager.is_model_downloaded()
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# TestPiperTTSEngineLatency
# ═══════════════════════════════════════════════════════════════════════════════

class TestPiperTTSEngineLatency:

    @pytest.mark.skipif(not _piper_available(), reason="Piper binary/model not available")
    def test_piper_synthesis_produces_wav_bytes(self):
        """PiperTTSEngine.synthesize() returns non-empty bytes starting with RIFF header."""
        engine = PiperTTSEngine()
        wav = asyncio.get_event_loop().run_until_complete(
            engine.synthesize("Ciao, come posso aiutarti?")
        )
        assert isinstance(wav, bytes)
        assert len(wav) > 100
        assert wav[:4] == b"RIFF", f"Expected RIFF WAV header, got {wav[:4]!r}"

    @pytest.mark.skipif(not _piper_available(), reason="Piper binary/model not available")
    def test_piper_p95_latency_under_200ms(self):
        """PiperTTSEngine P95 latency must be <= 200ms (N=20, warmup=2)."""
        engine = PiperTTSEngine()
        text = "Buongiorno, sono Sara. Come posso aiutarti oggi?"

        N = 20
        warmup = 2
        latencies = []

        loop = asyncio.get_event_loop()

        for i in range(N + warmup):
            t0 = time.perf_counter()
            loop.run_until_complete(engine.synthesize(text))
            elapsed_ms = (time.perf_counter() - t0) * 1000
            if i >= warmup:
                latencies.append(elapsed_ms)

        latencies.sort()
        p95_idx = int(0.95 * len(latencies)) - 1
        p95_ms = latencies[max(p95_idx, 0)]

        print(f"\n[Piper Latency] P50={latencies[len(latencies)//2]:.1f}ms  P95={p95_ms:.1f}ms")
        assert p95_ms <= 200, (
            f"Piper P95 latency {p95_ms:.1f}ms exceeds 200ms threshold"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TestQwenTTSEngineLatency
# ═══════════════════════════════════════════════════════════════════════════════

class TestQwenTTSEngineLatency:

    @pytest.mark.skipif(not _qwen_model_downloaded(), reason="Qwen3-TTS model not downloaded")
    def test_qwen_synthesis_produces_wav_bytes(self):
        """QwenTTSEngine.synthesize() returns non-empty bytes with WAV-like structure."""
        engine = QwenTTSEngine(lazy_load=False)
        wav = asyncio.get_event_loop().run_until_complete(
            engine.synthesize("Ciao, come posso aiutarti?")
        )
        assert isinstance(wav, bytes)
        assert len(wav) > 100

    @pytest.mark.skipif(not _qwen_model_downloaded(), reason="Qwen3-TTS model not downloaded")
    def test_qwen_p95_latency_under_800ms(self):
        """QwenTTSEngine P95 latency must be < 800ms on Intel i5 2019/8GB class hardware (N=20, warmup=2)."""
        engine = QwenTTSEngine(lazy_load=False)
        text = "Buongiorno, sono Sara. Come posso aiutarti oggi?"

        N = 20
        warmup = 2
        latencies = []

        loop = asyncio.get_event_loop()

        for i in range(N + warmup):
            t0 = time.perf_counter()
            loop.run_until_complete(engine.synthesize(text))
            elapsed_ms = (time.perf_counter() - t0) * 1000
            if i >= warmup:
                latencies.append(elapsed_ms)

        latencies.sort()
        p95_idx = int(0.95 * len(latencies)) - 1
        p95_ms = latencies[max(p95_idx, 0)]

        print(f"\n[Qwen3-TTS Latency] P50={latencies[len(latencies)//2]:.1f}ms  P95={p95_ms:.1f}ms")
        assert p95_ms < 800, (
            f"Qwen3-TTS P95 latency {p95_ms:.1f}ms exceeds 800ms threshold"
        )
