"""
Tests for AcousticFrustrationDetector (Phase F2-1 + F2-3).

All audio is generated with numpy — no real audio files required.
Follows existing test patterns in voice-agent/tests/.
"""

import math
import os
import struct
import sys
from collections import deque
from typing import List

import numpy as np
import pytest

# Add voice-agent/src to path for direct import (avoids triggering __init__.py
# which pulls in booking_state_machine → escalation_manager, unavailable here)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from acoustic_frustration import (
    AcousticFrustrationDetector,
    FrustrationResult,
    _MIN_PITCH_HZ,
    _MAX_PITCH_HZ,
    _RMS_RATIO_THRESHOLD,
    _ZCR_HIGH_THRESHOLD,
)

# ── Audio generation helpers ─────────────────────────────────────────────────

SAMPLE_RATE = 16000
CHUNK_DURATION = 0.1  # 100 ms
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)


def _make_sine(freq_hz: float, amplitude: float, n_samples: int = CHUNK_SAMPLES) -> bytes:
    """Pure sine wave at freq_hz, float amplitude, 16-bit LE PCM bytes."""
    t = np.arange(n_samples, dtype=np.float32) / SAMPLE_RATE
    wave = amplitude * np.sin(2 * np.pi * freq_hz * t)
    pcm = (np.clip(wave, -1.0, 1.0) * 32767).astype(np.int16)
    return pcm.tobytes()


def _make_noise(amplitude: float, n_samples: int = CHUNK_SAMPLES) -> bytes:
    """White-noise chunk at given amplitude, 16-bit LE PCM bytes."""
    rng = np.random.default_rng(seed=42)
    noise = amplitude * rng.standard_normal(n_samples).astype(np.float32)
    pcm = (np.clip(noise, -1.0, 1.0) * 32767).astype(np.int16)
    return pcm.tobytes()


def _make_silence(n_samples: int = CHUNK_SAMPLES) -> bytes:
    """Zero-valued PCM bytes."""
    return bytes(n_samples * 2)


def _float32_to_bytes(samples: np.ndarray) -> bytes:
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    return pcm.tobytes()


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def detector() -> AcousticFrustrationDetector:
    return AcousticFrustrationDetector(sample_rate=SAMPLE_RATE, calibration_frames=5)


@pytest.fixture()
def calibrated_detector() -> AcousticFrustrationDetector:
    """Detector pre-calibrated with quiet speech (amplitude 0.05)."""
    d = AcousticFrustrationDetector(sample_rate=SAMPLE_RATE, calibration_frames=5)
    # Feed 5 voiced frames at low amplitude + pitch ~150 Hz
    for _ in range(6):
        d.calibrate(_make_sine(150.0, 0.05))
    assert d._is_calibrated, "Fixture should be calibrated after 6 voiced frames"
    return d


# ── 1. RMS from known samples ─────────────────────────────────────────────────

class TestRMS:
    def test_silence_rms_is_zero(self, detector):
        """RMS of an all-zero buffer must be exactly 0.0."""
        result = detector.analyze_audio(_make_silence(), is_speech=True)
        assert result.rms == pytest.approx(0.0, abs=1e-6)

    def test_loud_audio_has_higher_rms(self, detector):
        """Loud chunk must produce higher RMS than quiet chunk."""
        quiet = _make_noise(0.05)
        loud = _make_noise(0.5)
        r_quiet = detector.analyze_audio(quiet, is_speech=True)
        r_loud = detector.analyze_audio(loud, is_speech=True)
        assert r_loud.rms > r_quiet.rms

    def test_rms_known_value(self, detector):
        """Full-scale sine wave (amplitude 1.0) should have RMS ≈ 1/sqrt(2)."""
        sine_bytes = _make_sine(200.0, 1.0, n_samples=SAMPLE_RATE)  # 1 second
        result = detector.analyze_audio(sine_bytes, is_speech=True)
        expected_rms = 1.0 / math.sqrt(2)
        # 16-bit quantisation introduces a small error — allow ±2%
        assert result.rms == pytest.approx(expected_rms, rel=0.02)


# ── 2. Calibration sets baseline correctly ────────────────────────────────────

class TestCalibration:
    def test_not_calibrated_before_enough_frames(self, detector):
        """Detector is not calibrated if fewer than calibration_frames are fed."""
        detector.calibrate(_make_sine(150.0, 0.05))
        assert not detector._is_calibrated

    def test_calibrated_after_enough_frames(self, detector):
        """Feeding enough voiced frames must complete calibration."""
        for _ in range(6):
            detector.calibrate(_make_sine(150.0, 0.05))
        assert detector._is_calibrated

    def test_baseline_rms_matches_input(self, detector):
        """Baseline RMS should be close to the RMS of the calibration signal."""
        amp = 0.08
        for _ in range(6):
            detector.calibrate(_make_sine(200.0, amp))
        expected_rms = amp / math.sqrt(2)
        assert detector._baseline_rms == pytest.approx(expected_rms, rel=0.10)

    def test_calibration_is_idempotent(self, detector):
        """Further calibrate() calls after calibration must not change baseline."""
        for _ in range(6):
            detector.calibrate(_make_sine(150.0, 0.05))
        baseline_after_6 = detector._baseline_rms
        # Feed very loud signal — must not alter baseline
        detector.calibrate(_make_sine(150.0, 0.9))
        assert detector._baseline_rms == baseline_after_6

    def test_silence_frames_do_not_count_toward_calibration(self, detector):
        """Silent frames (rms ≤ 0.001) must be ignored in calibration count."""
        for _ in range(10):
            detector.calibrate(_make_silence())
        assert not detector._is_calibrated


# ── 3. Frustration rises on loud audio ────────────────────────────────────────

class TestFrustrationRises:
    def test_frustration_higher_on_loud_audio(self, calibrated_detector):
        """Audio at 3× baseline RMS must produce a higher score than normal audio."""
        # Normal volume (same as calibration)
        normal = _make_sine(150.0, 0.05)
        # Loud: amplitude is 3× calibration amplitude → RMS ratio ≈ 3.0 (> threshold 2.5)
        loud = _make_sine(150.0, 0.15)

        r_normal = calibrated_detector.analyze_audio(normal, is_speech=True)
        # Feed several loud frames so pitch history also reflects high variance
        for _ in range(5):
            calibrated_detector.analyze_audio(loud, is_speech=True)
        r_loud = calibrated_detector.analyze_audio(loud, is_speech=True)

        assert r_loud.frustration_score > r_normal.frustration_score

    def test_frustration_above_threshold_on_3x_rms(self, calibrated_detector):
        """3× baseline amplitude should push score clearly above 0.0."""
        loud = _make_sine(150.0, 0.15)
        for _ in range(5):
            calibrated_detector.analyze_audio(loud, is_speech=True)
        result = calibrated_detector.analyze_audio(loud, is_speech=True)
        assert result.frustration_score > 0.0


# ── 4. Frustration stays low on normal volume ─────────────────────────────────

class TestFrustrationLow:
    def test_normal_volume_low_score(self, calibrated_detector):
        """Normal speech volume should produce a score below 0.4."""
        normal = _make_sine(150.0, 0.05)
        for _ in range(5):
            calibrated_detector.analyze_audio(normal, is_speech=True)
        result = calibrated_detector.analyze_audio(normal, is_speech=True)
        assert result.frustration_score < 0.4

    def test_silence_gives_near_zero_score(self, calibrated_detector):
        """Silence frames classified as speech must not inflate the score."""
        result = calibrated_detector.analyze_audio(_make_silence(), is_speech=True)
        assert result.frustration_score < 0.2


# ── 5. Anti-echo: score=0 when is_tts_playing ─────────────────────────────────

class TestAntiEchoTTS:
    def test_tts_playing_returns_zero_score(self, calibrated_detector):
        """When is_tts_playing=True, frustration_score must be exactly 0.0."""
        loud = _make_noise(0.9)
        result = calibrated_detector.analyze_audio(
            loud, is_speech=True, is_tts_playing=True
        )
        assert result.frustration_score == 0.0

    def test_tts_playing_returns_zero_rms(self, calibrated_detector):
        """When is_tts_playing=True, all returned values must be 0.0."""
        loud = _make_noise(0.9)
        result = calibrated_detector.analyze_audio(
            loud, is_speech=True, is_tts_playing=True
        )
        assert result.rms == 0.0
        assert result.zcr == 0.0
        assert result.pitch_hz == 0.0

    def test_tts_flag_overrides_speech_flag(self, calibrated_detector):
        """is_tts_playing=True must win even if is_speech=True."""
        loud = _make_noise(0.9)
        result = calibrated_detector.analyze_audio(
            loud, is_speech=True, is_tts_playing=True
        )
        assert result.frustration_score == 0.0


# ── 6. Anti-echo: no history update when is_speech=False ─────────────────────

class TestAntiEchoSpeech:
    def test_non_speech_does_not_update_history(self, calibrated_detector):
        """When is_speech=False, the rolling history must not grow."""
        initial_len = len(calibrated_detector._history)
        loud = _make_noise(0.9)
        calibrated_detector.analyze_audio(loud, is_speech=False)
        assert len(calibrated_detector._history) == initial_len

    def test_non_speech_returns_last_score(self, calibrated_detector):
        """When is_speech=False, the previously computed score must be returned."""
        # Establish a non-zero score first
        loud = _make_noise(0.5)
        r1 = calibrated_detector.analyze_audio(loud, is_speech=True)
        last_score = r1.frustration_score

        # Non-speech frame should return the same last score
        r2 = calibrated_detector.analyze_audio(_make_silence(), is_speech=False)
        assert r2.frustration_score == pytest.approx(last_score, abs=1e-9)

    def test_silence_non_speech_features_still_computed(self, calibrated_detector):
        """Features (rms, zcr, pitch) are still returned even when is_speech=False."""
        loud = _make_noise(0.4)
        result = calibrated_detector.analyze_audio(loud, is_speech=False)
        # rms of white noise at 0.4 amplitude should be positive
        assert result.rms > 0.0


# ── 7. Reset clears state ─────────────────────────────────────────────────────

class TestReset:
    def test_reset_clears_calibration(self, calibrated_detector):
        """After reset(), detector must not be calibrated."""
        calibrated_detector.reset()
        assert not calibrated_detector._is_calibrated

    def test_reset_clears_baseline(self, calibrated_detector):
        """After reset(), baseline values must be None."""
        calibrated_detector.reset()
        assert calibrated_detector._baseline_rms is None
        assert calibrated_detector._baseline_pitch_std is None

    def test_reset_clears_history(self, calibrated_detector):
        """After reset(), the rolling history must be empty."""
        # Feed some speech to populate history
        calibrated_detector.analyze_audio(_make_noise(0.1), is_speech=True)
        assert len(calibrated_detector._history) > 0

        calibrated_detector.reset()
        assert len(calibrated_detector._history) == 0

    def test_reset_clears_last_score(self, calibrated_detector):
        """After reset(), last known score must be 0.0."""
        calibrated_detector.analyze_audio(_make_noise(0.9), is_speech=True)
        calibrated_detector.reset()
        assert calibrated_detector._last_score == 0.0

    def test_is_calibrated_false_in_result_after_reset(self, calibrated_detector):
        """FrustrationResult.is_calibrated must be False after reset."""
        calibrated_detector.reset()
        result = calibrated_detector.analyze_audio(_make_noise(0.1), is_speech=True)
        assert not result.is_calibrated


# ── 8. Pitch estimation from sine wave ────────────────────────────────────────

class TestPitchEstimation:
    @pytest.mark.parametrize("freq_hz", [100.0, 150.0, 200.0, 300.0])
    def test_pitch_sine_wave_accurate(self, detector, freq_hz: float):
        """Autocorrelation pitch estimate must be within ±15% of the true frequency."""
        # Use a longer window (512ms) for better autocorrelation resolution
        n = int(SAMPLE_RATE * 0.512)
        sine_bytes = _make_sine(freq_hz, 0.5, n_samples=n)
        result = detector.analyze_audio(sine_bytes, is_speech=True)
        assert result.pitch_hz > 0.0, f"Expected voiced pitch for {freq_hz}Hz sine"
        assert result.pitch_hz == pytest.approx(freq_hz, rel=0.15), (
            f"Pitch estimate {result.pitch_hz:.1f}Hz too far from {freq_hz}Hz"
        )

    def test_silence_returns_zero_pitch(self, detector):
        """Silent frame should return pitch_hz=0.0 (unvoiced)."""
        result = detector.analyze_audio(_make_silence(), is_speech=True)
        assert result.pitch_hz == 0.0

    def test_pitch_within_human_range(self, detector):
        """Estimated pitch from speech-like sine must be within _MIN_PITCH_HZ – _MAX_PITCH_HZ."""
        sine_bytes = _make_sine(220.0, 0.5, n_samples=SAMPLE_RATE // 2)
        result = detector.analyze_audio(sine_bytes, is_speech=True)
        if result.pitch_hz > 0.0:
            assert _MIN_PITCH_HZ <= result.pitch_hz <= _MAX_PITCH_HZ


# ── 9. Score clipping ─────────────────────────────────────────────────────────

class TestScoreClipping:
    def test_score_never_above_one(self, calibrated_detector):
        """Extremely loud audio must not produce a score > 1.0."""
        max_loud = _make_noise(1.0)
        for _ in range(25):
            result = calibrated_detector.analyze_audio(max_loud, is_speech=True)
        assert result.frustration_score <= 1.0

    def test_score_never_below_zero(self, detector):
        """Score must never be negative, even on silence/noise with no calibration."""
        for chunk in [_make_silence(), _make_noise(0.001)]:
            result = detector.analyze_audio(chunk, is_speech=True)
            assert result.frustration_score >= 0.0

    def test_tts_score_exactly_zero(self, calibrated_detector):
        """TTS-playing score must be exactly 0.0, not merely near 0."""
        result = calibrated_detector.analyze_audio(
            _make_noise(1.0), is_speech=True, is_tts_playing=True
        )
        assert result.frustration_score == 0.0

    def test_score_is_float_not_numpy(self, calibrated_detector):
        """frustration_score must be a plain Python float, not numpy scalar."""
        result = calibrated_detector.analyze_audio(_make_noise(0.1), is_speech=True)
        assert isinstance(result.frustration_score, float)
        assert not isinstance(result.frustration_score, np.floating)


# ── 10. Integration: full calibration + detection cycle ──────────────────────

class TestIntegration:
    def test_full_call_cycle(self):
        """Simulate a full call: calibrate → normal speech → raised voice → detect."""
        d = AcousticFrustrationDetector(sample_rate=SAMPLE_RATE, calibration_frames=5)

        # Phase 1: calibration (calm voice at 150 Hz, amplitude 0.04)
        for _ in range(6):
            d.calibrate(_make_sine(150.0, 0.04))
        assert d._is_calibrated

        # Phase 2: normal speech — score should stay low
        scores_normal: List[float] = []
        for _ in range(10):
            r = d.analyze_audio(_make_sine(150.0, 0.04), is_speech=True)
            scores_normal.append(r.frustration_score)
        avg_normal = sum(scores_normal) / len(scores_normal)
        assert avg_normal < 0.45, f"Expected low score during normal speech, got {avg_normal:.2f}"

        # Phase 3: raised voice (3× baseline amplitude)
        scores_loud: List[float] = []
        for _ in range(10):
            r = d.analyze_audio(_make_sine(300.0, 0.12), is_speech=True)
            scores_loud.append(r.frustration_score)
        avg_loud = sum(scores_loud) / len(scores_loud)
        assert avg_loud > avg_normal, (
            f"Loud scores ({avg_loud:.2f}) should exceed normal scores ({avg_normal:.2f})"
        )

    def test_result_is_calibrated_field(self):
        """is_calibrated field must reflect the detector's actual calibration state."""
        d = AcousticFrustrationDetector(sample_rate=SAMPLE_RATE, calibration_frames=5)
        r_before = d.analyze_audio(_make_noise(0.1), is_speech=True)
        assert not r_before.is_calibrated

        for _ in range(6):
            d.calibrate(_make_sine(150.0, 0.05))
        r_after = d.analyze_audio(_make_noise(0.1), is_speech=True)
        assert r_after.is_calibrated
