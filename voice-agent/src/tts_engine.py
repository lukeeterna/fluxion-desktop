"""
FLUXION Voice Agent - FluxionTTS Adaptive Engine Layer
Decouples TTS engine selection from tts.py factory.

Engines:
  - EdgeTTSEngine  : Microsoft Edge Neural TTS (quality 9/10, ~500ms TTFB, cloud)
  - PiperTTSEngine : Piper subprocess wrapper (fast 7/10, ~50ms, offline)

Selection:
  - TTSEngineSelector.detect_hardware() → hardware capabilities dict
  - TTSEngineSelector.get_engine(mode)  → correct engine instance
  - create_tts_engine(user_pref)        → public convenience factory

Python 3.9 compatible. No torch/transformers/psutil at module load time.
"""

import asyncio
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

# ─── Optional psutil (graceful fallback) ──────────────────────────────────────
try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

# ─── Optional edge_tts (graceful fallback to Piper/SystemTTS) ─────────────────
try:
    import edge_tts
    _EDGE_TTS_AVAILABLE = True
except ImportError:
    _EDGE_TTS_AVAILABLE = False

# ─── Piper model name (mirrors tts.py) ────────────────────────────────────────
_PIPER_MODEL = "it_IT-paola-medium"


# ═══════════════════════════════════════════════════════════════════
# TTSMode — engine selection preference
# ═══════════════════════════════════════════════════════════════════

class TTSMode(str, Enum):
    """TTS engine selection mode."""
    AUTO = "auto"       # Hardware-based selection
    QUALITY = "quality"  # Edge-TTS IsabellaNeural (high quality, ~500ms)
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
                pass

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
            pass

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
        AUTO with internet → QUALITY (Edge-TTS), else FAST (Piper).
        """
        if user_pref != TTSMode.AUTO:
            return user_pref
        # Edge-TTS requires internet — if available and capable, use quality
        if hw.get("capable") and _EDGE_TTS_AVAILABLE:
            return TTSMode.QUALITY
        return TTSMode.FAST

    @staticmethod
    def get_engine(
        mode: TTSMode,
        reference_audio_path: Optional[str] = None,
    ) -> Union["EdgeTTSEngine", "PiperTTSEngine"]:
        """
        Instantiate the engine for a given mode.
        EdgeTTSEngine init failures fall back to PiperTTSEngine automatically.
        """
        if mode == TTSMode.QUALITY:
            try:
                engine = EdgeTTSEngine()
                logger.info("[TTSEngineSelector] EdgeTTSEngine selected (quality mode)")
                return engine
            except Exception as exc:
                logger.warning(
                    f"[TTSEngineSelector] EdgeTTSEngine init failed ({exc}), "
                    "falling back to PiperTTSEngine"
                )

        logger.info("[TTSEngineSelector] PiperTTSEngine selected (fast mode)")
        return PiperTTSEngine()


# ═══════════════════════════════════════════════════════════════════
# EdgeTTSEngine — Microsoft Edge Neural TTS (quality, cloud free)
# ═══════════════════════════════════════════════════════════════════

class EdgeTTSEngine:
    """
    Microsoft Edge Neural TTS via edge-tts library.

    Voice: it-IT-IsabellaNeural (warm, natural Italian female).
    Quality: 9/10. Latency: ~500ms TTFB, ~900ms total.
    Requires internet. Falls back to PiperTTSEngine/SystemTTS if offline.

    Output: WAV 16kHz 16-bit mono (converted from MP3 via afconvert/ffmpeg).
    """

    # Italian female voices ranked by quality
    DEFAULT_VOICE = "it-IT-IsabellaNeural"
    FALLBACK_VOICE = "it-IT-ElsaNeural"

    def __init__(self, voice: str = DEFAULT_VOICE):
        if not _EDGE_TTS_AVAILABLE:
            raise RuntimeError(
                "edge-tts not installed. Install with: pip install edge-tts"
            )
        self.voice = voice
        self.sample_rate = 16000
        self._converter = self._detect_converter()
        logger.info(
            f"[EdgeTTSEngine] Initialized with voice={voice}, "
            f"converter={self._converter}"
        )

    @staticmethod
    def _detect_converter() -> str:
        """Detect available audio converter for MP3→WAV."""
        if sys.platform == "darwin":
            if shutil.which("afconvert"):
                return "afconvert"
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        raise RuntimeError(
            "No audio converter found. Need afconvert (macOS) or ffmpeg."
        )

    def _convert_mp3_to_wav(self, mp3_path: str, wav_path: str) -> None:
        """Convert MP3 to WAV 16kHz 16-bit mono."""
        if self._converter == "afconvert":
            subprocess.run(
                ["afconvert", "-f", "WAVE", "-d", "LEI16@16000",
                 "-c", "1", mp3_path, wav_path],
                check=True, timeout=10,
                capture_output=True,
            )
        elif self._converter == "ffmpeg":
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path,
                 "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
                 wav_path],
                check=True, timeout=10,
                capture_output=True,
            )

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize Italian text to WAV audio via Edge-TTS.

        Returns:
            WAV bytes (16kHz, 16-bit, mono).

        Raises:
            RuntimeError: if synthesis or conversion fails.
        """
        mp3_path = tempfile.mktemp(suffix=".mp3")
        wav_path = tempfile.mktemp(suffix=".wav")

        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(mp3_path)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._convert_mp3_to_wav, mp3_path, wav_path
            )

            with open(wav_path, "rb") as fh:
                return fh.read()

        except Exception as exc:
            raise RuntimeError(
                f"[EdgeTTSEngine] Synthesis failed for '{text[:50]}...': {exc}"
            ) from exc

        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

    def get_info(self) -> dict:
        """Return engine metadata dict."""
        return {
            "engine": "edge-tts",
            "voice": self.voice,
            "quality": 9.0,
            "sample_rate": self.sample_rate,
            "requires_internet": True,
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

        if piper_binary:
            self.piper_binary: Optional[Path] = Path(piper_binary)
        else:
            self.piper_binary = self._find_piper_binary()

        if model_path:
            self.model_path: Optional[Path] = Path(model_path)
        else:
            self.model_path = self._find_model()

        self._validate()

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
                venv_bin,
                Path.home() / ".local" / "bin" / "piper",
                Path("/usr/local/bin/piper"),
                Path("/usr/bin/piper"),
            ]

        for path in candidates:
            if path.exists():
                return path

        found = shutil.which("piper")
        if found:
            return Path(found)

        found = shutil.which("piper-tts")
        if found:
            return Path(found)

        return None

    def _find_model(self) -> Optional[Path]:
        """Locate the Piper ONNX model file."""
        voice_agent_root = Path(__file__).parent.parent
        models_dir = voice_agent_root / "models" / "tts"
        models_dir.mkdir(parents=True, exist_ok=True)
        primary = models_dir / f"{_PIPER_MODEL}.onnx"
        if primary.exists():
            return primary

        system_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        fallback = system_dir / f"{_PIPER_MODEL}.onnx"
        if fallback.exists():
            return fallback

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

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text via Piper subprocess.

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
) -> Union[EdgeTTSEngine, PiperTTSEngine]:
    """
    Public factory: detect hardware, apply user preference, return engine.

    Args:
        user_pref:            TTSMode.AUTO (default), QUALITY, or FAST.
        reference_audio_path: Unused (kept for API compat).

    Returns:
        EdgeTTSEngine or PiperTTSEngine depending on mode + hardware.
    """
    hw = TTSEngineSelector.detect_hardware()
    mode = TTSEngineSelector.get_mode_for_hardware(hw, user_pref)
    return TTSEngineSelector.get_engine(mode, reference_audio_path)
