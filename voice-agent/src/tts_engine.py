"""
FLUXION Voice Agent - FluxionTTS Adaptive Engine Layer
Decouples TTS engine selection from tts.py factory.

Engines:
  - QwenTTSEngine  : Qwen3-TTS 0.6B via transformers[cpu] (quality, lazy)
  - PiperTTSEngine : Piper subprocess wrapper (fast, always available)

Selection:
  - TTSEngineSelector.detect_hardware() → hardware capabilities dict
  - TTSEngineSelector.get_engine(mode)  → correct engine instance
  - create_tts_engine(user_pref)        → public convenience factory

Python 3.9 compatible. No torch/transformers/psutil at module load time.
"""

import asyncio
import logging
import os
import subprocess
import sys
import tempfile
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

# ─── Optional psutil (graceful fallback) ──────────────────────────────────────
try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

# ─── Piper model name (mirrors tts.py) ────────────────────────────────────────
_PIPER_MODEL = "it_IT-paola-medium"


# ═══════════════════════════════════════════════════════════════════
# TTSMode — engine selection preference
# ═══════════════════════════════════════════════════════════════════

class TTSMode(str, Enum):
    """TTS engine selection mode."""
    AUTO = "auto"       # Hardware-based selection
    QUALITY = "quality"  # Qwen3-TTS (high quality, ~400-800ms)
    FAST = "fast"       # Piper (low latency, ~50ms)


# ═══════════════════════════════════════════════════════════════════
# TTSEngineSelector — hardware detection + engine factory
# ═══════════════════════════════════════════════════════════════════

class TTSEngineSelector:
    """
    Detects hardware capabilities and selects the appropriate TTS engine.

    Capable threshold: RAM >= 8 GB AND CPU cores >= 4.
    """

    @staticmethod
    def detect_hardware() -> Dict[str, object]:
        """
        Detect hardware capabilities for TTS engine selection.

        Returns:
            dict with keys:
              ram_gb    (float)  — total system RAM in gigabytes
              cpu_cores (int)   — logical CPU core count
              avx2      (bool)  — AVX2 instruction set available
              capable   (bool)  — RAM >= 8.0 and cpu_cores >= 4
        """
        # ── RAM ──────────────────────────────────────────────────────────────
        if _PSUTIL_AVAILABLE:
            ram_gb: float = psutil.virtual_memory().total / 1e9
        else:
            # Fallback: attempt to read /proc/meminfo (Linux) or sysctl (macOS)
            ram_gb = 8.0  # conservative default
            try:
                if sys.platform == "darwin":
                    out = subprocess.check_output(
                        ["sysctl", "-n", "hw.memsize"], timeout=2
                    )
                    ram_gb = int(out.strip()) / 1e9
                elif sys.platform.startswith("linux"):
                    with open("/proc/meminfo") as fh:
                        for line in fh:
                            if line.startswith("MemTotal:"):
                                kb = int(line.split()[1])
                                ram_gb = kb / 1e6
                                break
            except Exception:
                pass  # use default 8.0

        # ── CPU cores ────────────────────────────────────────────────────────
        cpu_cores: int = os.cpu_count() or 4

        # ── AVX2 detection ───────────────────────────────────────────────────
        avx2 = False
        try:
            if sys.platform == "darwin":
                out = subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.features"], timeout=2
                )
                avx2 = "AVX2" in out.decode("utf-8", errors="replace").upper()
            elif sys.platform.startswith("linux"):
                with open("/proc/cpuinfo") as fh:
                    for line in fh:
                        if line.startswith("flags") and "avx2" in line:
                            avx2 = True
                            break
        except Exception:
            pass  # default avx2=False

        capable: bool = ram_gb >= 8.0 and cpu_cores >= 4

        return {
            "ram_gb": ram_gb,
            "cpu_cores": cpu_cores,
            "avx2": avx2,
            "capable": capable,
        }

    @staticmethod
    def get_mode_for_hardware(
        hw: Dict[str, object],
        user_pref: TTSMode = TTSMode.AUTO,
    ) -> TTSMode:
        """
        Resolve effective TTS mode from hardware caps and user preference.

        Args:
            hw:        Result of detect_hardware()
            user_pref: Explicit preference; AUTO means hardware-based.

        Returns:
            TTSMode.QUALITY or TTSMode.FAST
        """
        if user_pref != TTSMode.AUTO:
            return user_pref
        return TTSMode.QUALITY if hw.get("capable") else TTSMode.FAST

    @staticmethod
    def get_engine(
        mode: TTSMode,
        reference_audio_path: Optional[str] = None,
    ) -> Union["QwenTTSEngine", "PiperTTSEngine"]:
        """
        Instantiate the engine for a given mode.

        QwenTTSEngine init failures fall back to PiperTTSEngine automatically.

        Args:
            mode:                 QUALITY or FAST (AUTO is resolved before calling)
            reference_audio_path: Optional voice reference for Qwen3-TTS.

        Returns:
            QwenTTSEngine (QUALITY) or PiperTTSEngine (FAST / fallback)
        """
        if mode == TTSMode.QUALITY:
            try:
                engine = QwenTTSEngine(reference_audio_path=reference_audio_path)
                logger.info("[TTSEngineSelector] QwenTTSEngine selected (quality mode)")
                return engine
            except Exception as exc:
                logger.warning(
                    f"[TTSEngineSelector] QwenTTSEngine init failed ({exc}), "
                    "falling back to PiperTTSEngine"
                )

        logger.info("[TTSEngineSelector] PiperTTSEngine selected (fast mode)")
        return PiperTTSEngine()


# ═══════════════════════════════════════════════════════════════════
# QwenTTSEngine — Qwen3-TTS 0.6B via transformers[cpu]
# ═══════════════════════════════════════════════════════════════════

class QwenTTSEngine:
    """
    Qwen3-TTS 0.6B CustomVoice via Hugging Face transformers (CPU-only).

    Model: ~1.2 GB download, deferred to first Sara startup (not wizard).
    Latency: ~400-800 ms on modern CPUs.
    Quality: 9.5 / 10.

    NOTE: `import torch` is NEVER called at module level. The transformers
    pipeline manages torch internally — this module remains importable on
    Python 3.9 even when torch is absent (lazy load pattern).
    """

    # Class-level singleton — shared across all instances
    _model = None

    # Sara's approved voice — Serena (warm, gentle, approved by founder 2026-03-15)
    DEFAULT_SPEAKER = "Serena"
    DEFAULT_INSTRUCT = "Speak in a warm, friendly and professional Italian tone, like a receptionist"

    def __init__(
        self,
        model_id: str = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        reference_audio_path: Optional[str] = None,
        sample_rate: int = 24000,
        lazy_load: bool = True,
        speaker: str = "Serena",
        instruct: str = "Speak in a warm, friendly and professional Italian tone, like a receptionist",
    ):
        self.model_id = model_id
        self.reference_audio_path = reference_audio_path
        self.sample_rate = sample_rate
        self.speaker = speaker
        self.instruct = instruct
        self._loaded = False

        if not lazy_load:
            self._load_model()

    def _load_model(self) -> None:
        """
        Load Qwen3-TTS pipeline (once per process via class-level singleton).

        Raises:
            RuntimeError: if transformers is not installed.
        """
        if QwenTTSEngine._model is not None:
            self._loaded = True
            return

        try:
            from transformers import pipeline  # noqa: PLC0415

            logger.info(
                f"[QwenTTSEngine] Loading {self.model_id} on CPU "
                "(first load may take 1-2 min)..."
            )
            QwenTTSEngine._model = pipeline(
                "text-to-speech",
                model=self.model_id,
                device="cpu",
            )
            self._loaded = True
            logger.info("[QwenTTSEngine] Model loaded successfully")

        except ImportError as exc:
            raise RuntimeError(
                "transformers not installed. Install with: "
                "pip install 'transformers[cpu]'"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"[QwenTTSEngine] Failed to load model: {exc}"
            ) from exc

    def _sync_synthesize(self, text: str) -> bytes:
        """
        Synchronous TTS inference (intended for run_in_executor).

        Args:
            text: Italian text to synthesize.

        Returns:
            WAV bytes at self.sample_rate.
        """
        result = QwenTTSEngine._model(text)
        audio_array = result["audio"]  # numpy ndarray

        buf = BytesIO()
        try:
            import soundfile as sf  # noqa: PLC0415
            sf.write(buf, audio_array, self.sample_rate, format="WAV")
        except ImportError:
            # Fallback to scipy
            try:
                import numpy as np  # noqa: PLC0415
                from scipy.io.wavfile import write as wav_write  # noqa: PLC0415

                # Normalise to int16
                audio_int16 = (audio_array * 32767).astype(np.int16)
                wav_write(buf, self.sample_rate, audio_int16)
            except ImportError as exc:
                raise RuntimeError(
                    "Neither soundfile nor scipy is installed. "
                    "Install with: pip install soundfile  (or scipy)"
                ) from exc

        return buf.getvalue()

    async def synthesize(self, text: str) -> bytes:
        """
        Async TTS synthesis — offloads CPU inference to thread pool.

        Args:
            text: Italian text to synthesize.

        Returns:
            WAV bytes.
        """
        if not self._loaded:
            self._load_model()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_synthesize, text)

    def get_info(self) -> dict:
        """Return engine metadata dict."""
        return {
            "engine": "qwen3-tts",
            "model": self.model_id,
            "loaded": self._loaded,
            "quality": 9.5,
            "sample_rate": self.sample_rate,
        }


# ═══════════════════════════════════════════════════════════════════
# PiperTTSEngine — Piper subprocess wrapper (fast, guaranteed fallback)
# ═══════════════════════════════════════════════════════════════════

class PiperTTSEngine:
    """
    Piper TTS subprocess wrapper — fast, lightweight, always-available fallback.

    Binary search order (mirrors PiperTTS.__init__ in tts.py exactly):
      1. venv bin directory   (Path(sys.executable).parent / "piper")
      2. models/ subdir of voice-agent root
      3. "piper" on PATH
      4. "piper-tts" on PATH
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        piper_binary: Optional[str] = None,
    ):
        self.model_name = _PIPER_MODEL
        self.sample_rate = 22050

        # ── Binary location ───────────────────────────────────────────────────
        if piper_binary:
            self.piper_binary: Optional[Path] = Path(piper_binary)
        else:
            self.piper_binary = self._find_piper_binary()

        # ── Model file ────────────────────────────────────────────────────────
        if model_path:
            self.model_path: Optional[Path] = Path(model_path)
        else:
            self.model_path = self._find_model()

        # Validate (raises RuntimeError if not usable)
        self._validate()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _find_piper_binary(self) -> Optional[Path]:
        """Search for piper binary following the canonical search order."""
        venv_bin = Path(sys.executable).parent / "piper"

        if sys.platform == "win32":
            candidates = [
                Path(sys.executable).parent / "piper.exe",
                Path(sys.executable).parent.parent / "Scripts" / "piper.exe",
                Path.home() / "AppData" / "Local" / "Programs" / "piper" / "piper.exe",
                Path("C:/Program Files/piper/piper.exe"),
            ]
        else:
            candidates = [
                venv_bin,                             # 1. venv bin (FIRST)
                Path.home() / ".local" / "bin" / "piper",
                Path("/usr/local/bin/piper"),
                Path("/usr/bin/piper"),
            ]

        for path in candidates:
            if path.exists():
                return path

        # 3. "piper" on PATH
        import shutil
        found = shutil.which("piper")
        if found:
            return Path(found)

        # 4. "piper-tts" on PATH
        found = shutil.which("piper-tts")
        if found:
            return Path(found)

        return None

    def _find_model(self) -> Optional[Path]:
        """Locate the Piper ONNX model file."""
        # Primary: voice-agent/models/tts/
        voice_agent_root = Path(__file__).parent.parent
        models_dir = voice_agent_root / "models" / "tts"
        models_dir.mkdir(parents=True, exist_ok=True)
        primary = models_dir / f"{_PIPER_MODEL}.onnx"
        if primary.exists():
            return primary

        # Fallback: ~/.local/share/piper/voices/
        system_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        fallback = system_dir / f"{_PIPER_MODEL}.onnx"
        if fallback.exists():
            return fallback

        # Return primary path (validation will raise if file absent)
        return primary

    def _validate(self) -> None:
        """Raise RuntimeError if piper binary or model is missing."""
        if self.piper_binary is None or not self.piper_binary.exists():
            raise RuntimeError(
                "Piper binary not found. Install with: pip install piper-tts"
            )
        if self.model_path is None or not self.model_path.exists():
            raise RuntimeError(
                f"Piper voice model not found: {self.model_path}. "
                f"Download {_PIPER_MODEL}.onnx to voice-agent/models/tts/"
            )

    # ── Public API ────────────────────────────────────────────────────────────

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text via Piper subprocess.

        Args:
            text: Italian text to synthesize.

        Returns:
            WAV bytes (22 050 Hz).
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            process = await asyncio.create_subprocess_exec(
                str(self.piper_binary),
                "--model", str(self.model_path),
                "--output_file", output_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate(text.encode())

            if process.returncode != 0:
                raise RuntimeError(
                    f"Piper subprocess failed: {stderr.decode(errors='replace')}"
                )

            with open(output_path, "rb") as fh:
                return fh.read()

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def get_info(self) -> dict:
        """Return engine metadata dict."""
        return {
            "engine": "piper",
            "model": self.model_name,
            "quality": 7.5,
            "sample_rate": self.sample_rate,
        }


# ═══════════════════════════════════════════════════════════════════
# Public factory
# ═══════════════════════════════════════════════════════════════════

def create_tts_engine(
    user_pref: TTSMode = TTSMode.AUTO,
    reference_audio_path: Optional[str] = None,
) -> Union[QwenTTSEngine, PiperTTSEngine]:
    """
    Public factory: detect hardware, apply user preference, return engine.

    Args:
        user_pref:            TTSMode.AUTO (default), QUALITY, or FAST.
        reference_audio_path: Optional reference audio for Qwen3-TTS cloning.

    Returns:
        QwenTTSEngine or PiperTTSEngine depending on mode + hardware.
    """
    hw = TTSEngineSelector.detect_hardware()
    mode = TTSEngineSelector.get_mode_for_hardware(hw, user_pref)
    return TTSEngineSelector.get_engine(mode, reference_audio_path)
