"""
FLUXION Voice Agent — Acoustic Frustration Detector

Detects caller frustration from raw PCM audio using pure numpy DSP.
No external ML libraries — only numpy (already installed).

Design:
- Three acoustic features: RMS energy, ZCR, F0 pitch via autocorrelation
- Calibration window: first 2-3s of call establishes per-caller baseline
- Rolling history: deque of last ~2s of speech frames (20 × 100ms chunks)
- Italian prosody adjustment: higher thresholds because Italian speakers are
  naturally more expressive than English speakers at rest
- Anti-echo guards: skip analysis when Sara's TTS is playing

Usage:
    detector = AcousticFrustrationDetector(sample_rate=16000)
    detector.calibrate(first_2s_pcm_bytes)
    result = detector.analyze_audio(chunk_pcm_bytes, is_speech=True)
    if result.frustration_score > 0.6:
        # trigger escalation or tone adaptation
"""

import logging
import struct
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Thresholds (Italian prosody — higher than English defaults) ──────────────
_RMS_RATIO_THRESHOLD: float = 2.5      # baseline × 2.5 = raised voice
_PITCH_VAR_THRESHOLD_HZ: float = 30.0  # std-dev Hz above which speech is emotional
_ZCR_HIGH_THRESHOLD: float = 0.18      # fraction of zero-crossings = fast/agitated
_MIN_PITCH_HZ: float = 80.0            # F0 floor (male voice)
_MAX_PITCH_HZ: float = 400.0           # F0 ceiling (female/child)

# Rolling window: 20 frames × 100ms = ~2s of history
_HISTORY_MAXLEN: int = 20

# Scoring weights (must sum to 1.0)
_W_RMS: float = 0.50
_W_PITCH: float = 0.35
_W_ZCR: float = 0.15


@dataclass
class FrustrationResult:
    """Acoustic frustration analysis for a single audio chunk."""
    rms: float               # Root-mean-square energy of the chunk
    zcr: float               # Zero-crossing rate (0.0 – 0.5)
    pitch_hz: float          # Estimated fundamental frequency (Hz); 0.0 = unvoiced
    frustration_score: float # Combined score in [0.0, 1.0]
    is_calibrated: bool      # False until calibration baseline is established


@dataclass
class _FrameFeatures:
    """Internal storage for a single frame's features."""
    rms: float
    zcr: float
    pitch_hz: float


class AcousticFrustrationDetector:
    """Detects caller frustration from acoustic signals using numpy DSP.

    Workflow per call:
    1. Instantiate once per VoIP session.
    2. Feed the first 2-3 seconds of speech to ``calibrate()``.
    3. On every speech chunk from the VAD, call ``analyze_audio()``.
    4. Call ``reset()`` when the call ends (or a new session begins).

    Thread-safety: NOT thread-safe.  Callers must serialize access or use one
    instance per call/session.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        calibration_frames: int = 5,
    ) -> None:
        """
        Args:
            sample_rate: PCM sample rate in Hz.  Must match the audio feed.
            calibration_frames: How many speech frames (each ~100ms) to average
                                for the baseline.  Minimum 3.
        """
        self._sample_rate: int = sample_rate
        self._calibration_frames: int = max(3, calibration_frames)

        # Calibration state
        self._calibration_rms_samples: List[float] = []
        self._calibration_pitch_samples: List[float] = []
        self._baseline_rms: Optional[float] = None
        self._baseline_pitch_std: Optional[float] = None
        self._is_calibrated: bool = False

        # Rolling feature history (speech-only frames)
        self._history: Deque[_FrameFeatures] = deque(maxlen=_HISTORY_MAXLEN)

        # Last known score (returned when non-speech frames arrive)
        self._last_score: float = 0.0

    # ── Public API ────────────────────────────────────────────────────────────

    def calibrate(self, pcm_bytes: bytes) -> None:
        """Feed the first 2-3 seconds of call audio to establish a baseline.

        Can be called multiple times with successive chunks; calibration
        completes automatically once enough speech frames have been collected.
        Subsequent calls after calibration are silently ignored.

        Args:
            pcm_bytes: 16-bit signed little-endian PCM at self._sample_rate.
        """
        if self._is_calibrated:
            return

        samples = self._bytes_to_float32(pcm_bytes)
        if len(samples) < 64:
            return

        rms = self._compute_rms(samples)
        pitch = self._estimate_pitch(samples)

        # Only accumulate voiced frames for calibration
        if rms > 0.001 and pitch > 0.0:
            self._calibration_rms_samples.append(rms)
            self._calibration_pitch_samples.append(pitch)

        if len(self._calibration_rms_samples) >= self._calibration_frames:
            self._baseline_rms = float(np.mean(self._calibration_rms_samples))
            # Pitch std needs at least 2 samples to be meaningful
            if len(self._calibration_pitch_samples) >= 2:
                self._baseline_pitch_std = float(
                    np.std(self._calibration_pitch_samples)
                )
            else:
                self._baseline_pitch_std = _PITCH_VAR_THRESHOLD_HZ * 0.5
            self._is_calibrated = True
            logger.info(
                "AcousticFrustrationDetector calibrated: "
                "baseline_rms=%.4f  baseline_pitch_std=%.1f Hz",
                self._baseline_rms,
                self._baseline_pitch_std,
            )

    def analyze_audio(
        self,
        pcm_bytes: bytes,
        is_speech: bool = True,
        is_tts_playing: bool = False,
    ) -> FrustrationResult:
        """Analyze an audio chunk and return a frustration score.

        Args:
            pcm_bytes: 16-bit signed little-endian PCM at self._sample_rate.
            is_speech: True when VAD has detected active speech.  If False,
                       history is NOT updated; the previous score is returned.
            is_tts_playing: True while Sara's TTS output is playing.  Returns
                            score=0.0 immediately to avoid echo contamination.

        Returns:
            FrustrationResult with a score in [0.0, 1.0].
        """
        # ── Anti-echo guard ───────────────────────────────────────────────────
        if is_tts_playing:
            return FrustrationResult(
                rms=0.0,
                zcr=0.0,
                pitch_hz=0.0,
                frustration_score=0.0,
                is_calibrated=self._is_calibrated,
            )

        samples = self._bytes_to_float32(pcm_bytes)
        if len(samples) < 64:
            return FrustrationResult(
                rms=0.0,
                zcr=0.0,
                pitch_hz=0.0,
                frustration_score=self._last_score,
                is_calibrated=self._is_calibrated,
            )

        # Compute features unconditionally (cheap)
        rms = self._compute_rms(samples)
        zcr = self._compute_zcr(samples)
        pitch = self._estimate_pitch(samples)

        # ── Non-speech: return last known score without updating history ──────
        if not is_speech:
            return FrustrationResult(
                rms=rms,
                zcr=zcr,
                pitch_hz=pitch,
                frustration_score=self._last_score,
                is_calibrated=self._is_calibrated,
            )

        # Update rolling history
        self._history.append(_FrameFeatures(rms=rms, zcr=zcr, pitch_hz=pitch))

        # Compute combined frustration score
        score = self._compute_score(rms, zcr, pitch)
        self._last_score = score

        if score >= 0.6:
            logger.info(
                "Acoustic frustration detected: score=%.2f  rms=%.4f  "
                "zcr=%.3f  pitch=%.1fHz",
                score, rms, zcr, pitch,
            )

        return FrustrationResult(
            rms=rms,
            zcr=zcr,
            pitch_hz=pitch,
            frustration_score=score,
            is_calibrated=self._is_calibrated,
        )

    def reset(self) -> None:
        """Reset detector state for a new call.

        Clears calibration, history, and all accumulated features.
        """
        self._calibration_rms_samples.clear()
        self._calibration_pitch_samples.clear()
        self._baseline_rms = None
        self._baseline_pitch_std = None
        self._is_calibrated = False
        self._history.clear()
        self._last_score = 0.0
        logger.debug("AcousticFrustrationDetector reset.")

    # ── DSP helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _bytes_to_float32(pcm_bytes: bytes) -> np.ndarray:
        """Convert raw 16-bit LE PCM bytes to float32 in [-1, 1]."""
        n_samples = len(pcm_bytes) // 2
        if n_samples == 0:
            return np.zeros(0, dtype=np.float32)
        # struct.unpack is faster than np.frombuffer for small buffers but
        # np.frombuffer avoids Python-level loops for large ones.
        samples = np.frombuffer(pcm_bytes[: n_samples * 2], dtype=np.int16)
        return samples.astype(np.float32) / 32768.0

    @staticmethod
    def _compute_rms(samples: np.ndarray) -> float:
        """Root-mean-square energy of the frame."""
        if len(samples) == 0:
            return 0.0
        return float(np.sqrt(np.mean(samples ** 2)))

    @staticmethod
    def _compute_zcr(samples: np.ndarray) -> float:
        """Zero-crossing rate: fraction of adjacent-sample sign changes."""
        if len(samples) < 2:
            return 0.0
        signs = np.sign(samples)
        # Replace zeros with small positive to avoid ambiguity
        signs[signs == 0] = 1e-9
        crossings = np.sum(np.abs(np.diff(signs))) / 2.0
        return float(crossings / len(samples))

    def _estimate_pitch(self, samples: np.ndarray) -> float:
        """Estimate fundamental frequency (F0) via autocorrelation.

        Uses rfft-based autocorrelation for efficiency.
        Returns 0.0 for unvoiced/noise frames.
        """
        n = len(samples)
        if n < self._sample_rate // _MAX_PITCH_HZ:
            return 0.0

        # Subtract mean (remove DC offset)
        x = samples - np.mean(samples)

        # Autocorrelation via FFT (O(n log n))
        fft_size = 1
        while fft_size < 2 * n:
            fft_size <<= 1
        spectrum = np.fft.rfft(x, n=fft_size)
        power = (spectrum * np.conj(spectrum)).real
        autocorr = np.fft.irfft(power)[:n]

        # Normalize
        if autocorr[0] <= 0.0:
            return 0.0
        autocorr = autocorr / autocorr[0]

        # Search in lag range corresponding to _MIN_PITCH_HZ – _MAX_PITCH_HZ
        lag_min = int(self._sample_rate / _MAX_PITCH_HZ)
        lag_max = int(self._sample_rate / _MIN_PITCH_HZ)
        lag_max = min(lag_max, n - 1)

        if lag_min >= lag_max:
            return 0.0

        search_region = autocorr[lag_min:lag_max]
        peak_idx = int(np.argmax(search_region))
        peak_val = float(search_region[peak_idx])

        # Confidence check: peak must be reasonably strong
        if peak_val < 0.3:
            return 0.0

        best_lag = lag_min + peak_idx
        return float(self._sample_rate / best_lag) if best_lag > 0 else 0.0

    # ── Scoring ───────────────────────────────────────────────────────────────

    def _compute_score(self, rms: float, zcr: float, pitch: float) -> float:
        """Combine acoustic features into a single frustration score [0, 1].

        When calibrated: compares current frame against per-caller baseline.
        When not calibrated: uses absolute thresholds (conservative).
        """
        rms_sub = self._score_rms(rms)
        pitch_sub = self._score_pitch(pitch)
        zcr_sub = self._score_zcr(zcr)

        combined = (_W_RMS * rms_sub) + (_W_PITCH * pitch_sub) + (_W_ZCR * zcr_sub)
        return float(np.clip(combined, 0.0, 1.0))

    def _score_rms(self, rms: float) -> float:
        """Sub-score for energy level.  1.0 = clearly raised voice."""
        if self._is_calibrated and self._baseline_rms and self._baseline_rms > 0.0:
            ratio = rms / self._baseline_rms
            # Smoothly ramp from 1.0× (no frustration) to threshold (full)
            normalized = (ratio - 1.0) / (_RMS_RATIO_THRESHOLD - 1.0)
        else:
            # Fallback: treat RMS > 0.15 as loud (absolute, uncalibrated)
            normalized = rms / 0.15
        return float(np.clip(normalized, 0.0, 1.0))

    def _score_pitch(self, pitch: float) -> float:
        """Sub-score for pitch variability over the rolling window.

        High pitch standard deviation (> threshold) signals emotional arousal.
        Uses the rolling history deque rather than the single current frame.
        """
        voiced_pitches = [f.pitch_hz for f in self._history if f.pitch_hz > 0.0]
        if len(voiced_pitches) < 2:
            return 0.0

        std = float(np.std(voiced_pitches))

        if self._is_calibrated and self._baseline_pitch_std is not None:
            # How much above the caller's own baseline are we?
            baseline = max(self._baseline_pitch_std, 1.0)
            normalized = (std - baseline) / _PITCH_VAR_THRESHOLD_HZ
        else:
            normalized = std / _PITCH_VAR_THRESHOLD_HZ

        return float(np.clip(normalized, 0.0, 1.0))

    def _score_zcr(self, zcr: float) -> float:
        """Sub-score for zero-crossing rate.  1.0 = clearly agitated speech."""
        normalized = zcr / _ZCR_HIGH_THRESHOLD
        return float(np.clip(normalized, 0.0, 1.0))
