"""
FLUXION Voice Agent - Speech-to-Text Module

E7-S1: whisper.cpp offline STT with Groq fallback.

Root cause of WER 21.7%: Groq API uses lossy audio compression.
Solution: whisper.cpp local with raw PCM audio → expected WER 9-11%.

Model selection:
- Whisper Small: 461MB, WER 9-11% Italian, 2-3s latency, 1.5GB RAM
- Best trade-off for desktop app (accuracy vs speed)

Usage:
    stt = get_stt_engine()
    transcription = await stt.transcribe(audio_bytes)
"""

import os
import json
import subprocess
import tempfile
import asyncio
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path


# =============================================================================
# STT INTERFACE
# =============================================================================

class STTEngine(ABC):
    """Abstract base class for Speech-to-Text engines."""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "it"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes (WAV format, 16kHz, mono)
            language: Language code (default: "it" for Italian)

        Returns:
            {
                "text": "transcribed text",
                "confidence": 0.92,
                "language": "it",
                "engine": "whisper_cpp" or "groq",
                "latency_ms": 1500
            }
        """
        pass


# =============================================================================
# WHISPER.CPP OFFLINE ENGINE
# =============================================================================

class WhisperOfflineSTT(STTEngine):
    """
    Offline STT using whisper.cpp.

    Expected WER: 9-11% for Italian (vs 21.7% via Groq).
    Latency: 2-3s on CPU (acceptable for voice agent).

    Setup:
        1. Install whisper.cpp: git clone https://github.com/ggerganov/whisper.cpp && make
        2. Download model: ./models/download-ggml-model.sh small
        3. Set WHISPER_CPP_PATH environment variable
    """

    def __init__(
        self,
        whisper_exe: Optional[str] = None,
        model_path: Optional[str] = None,
        language: str = "it"
    ):
        """
        Initialize whisper.cpp STT.

        Args:
            whisper_exe: Path to whisper.cpp main executable
            model_path: Path to GGML model file (ggml-small.bin recommended)
            language: Default language for transcription
        """
        # Find whisper.cpp executable
        self.whisper_exe = whisper_exe or self._find_whisper_exe()
        self.model_path = model_path or self._find_model()
        self.language = language

        # Validate paths
        if not self.whisper_exe or not Path(self.whisper_exe).exists():
            raise FileNotFoundError(
                f"whisper.cpp executable not found at: {self.whisper_exe}\n"
                "Install: git clone https://github.com/ggerganov/whisper.cpp && make"
            )

        if not self.model_path or not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Whisper model not found at: {self.model_path}\n"
                "Download: ./models/download-ggml-model.sh small"
            )

        print(f"[STT] whisper.cpp initialized: {self.whisper_exe}")
        print(f"[STT] Model: {self.model_path}")

    def _find_whisper_exe(self) -> Optional[str]:
        """Find whisper.cpp executable."""
        # Check environment variable first
        env_path = os.environ.get("WHISPER_CPP_PATH")
        if env_path:
            # Try whisper-cli first (new name), then main (old name)
            for exe_name in ["whisper-cli", "main"]:
                exe = Path(env_path) / exe_name
                if exe.exists():
                    return str(exe)

        # Check common locations
        common_paths = [
            Path.home() / "whisper.cpp" / "build" / "bin" / "whisper-cli",
            Path.home() / "whisper.cpp" / "main",
            Path("/usr/local/bin/whisper-cli"),
            Path("/usr/local/bin/whisper"),
            Path("./resources/whisper.cpp/build/bin/whisper-cli"),
            Path("../resources/whisper.cpp/build/bin/whisper-cli"),
        ]

        for path in common_paths:
            if path.exists():
                return str(path)

        return None

    def _find_model(self) -> Optional[str]:
        """Find Whisper model file."""
        # Check environment variable
        env_model = os.environ.get("WHISPER_MODEL_PATH")
        if env_model and Path(env_model).exists():
            return env_model

        # Check common locations (prefer small model)
        common_paths = [
            Path.home() / "whisper.cpp" / "models" / "ggml-small.bin",
            Path("./resources/whisper.cpp/models/ggml-small.bin"),
            Path("../resources/whisper.cpp/models/ggml-small.bin"),
        ]

        for path in common_paths:
            if path.exists():
                return str(path)

        return None

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio using whisper.cpp.

        Uses subprocess to run whisper.cpp main executable.
        """
        import time
        start_time = time.time()
        lang = language or self.language

        # Write audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            audio_path = f.name

        try:
            # Run whisper.cpp
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        self.whisper_exe,
                        "-m", self.model_path,
                        "-l", lang,
                        "-f", audio_path,
                        "--output-json",
                        "--no-prints",
                        "-otxt",  # Output plain text
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120  # 120 second timeout (ggml-small ~30s on Intel CPU)
                )
            )

            latency_ms = (time.time() - start_time) * 1000

            if result.returncode == 0:
                # Parse output - whisper.cpp outputs to stdout or .txt file
                text = result.stdout.strip()
                if not text:
                    # Try reading from .txt file
                    txt_path = audio_path + ".txt"
                    if Path(txt_path).exists():
                        text = Path(txt_path).read_text().strip()
                        Path(txt_path).unlink()  # Clean up

                return {
                    "text": text,
                    "confidence": 0.92,  # whisper.cpp doesn't output confidence
                    "language": lang,
                    "engine": "whisper_cpp",
                    "latency_ms": latency_ms
                }
            else:
                print(f"[STT] whisper.cpp error: {result.stderr}")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": lang,
                    "engine": "whisper_cpp",
                    "error": result.stderr,
                    "latency_ms": latency_ms
                }

        finally:
            # Clean up temp file
            try:
                Path(audio_path).unlink()
            except Exception:
                pass


# =============================================================================
# FASTER-WHISPER ENGINE (CTranslate2 int8 — 4-6x faster on CPU)
# =============================================================================

class FasterWhisperSTT(STTEngine):
    """
    Offline STT using faster-whisper (CTranslate2 int8 quantization).

    4-6x faster than whisper.cpp on Intel CPU, same accuracy.
    Downloads model from HuggingFace on first use (cached locally).

    Benchmarks su iMac 2012 Intel i5 2.7GHz (4s audio reale):
        tiny  → ~3.8s  (1x real-time)   — errori minori su italiano
        base  → ~4.7s  (1.2x real-time) — accuratezza ottima  ← default
        small → ~14s   (3.5x real-time) — troppo lento per UX

    Usage:
        Set WHISPER_MODEL env var to "tiny", "base" (default), or "small".
    """

    def __init__(self, model_size: str = None):
        self.model_size = model_size or os.environ.get("WHISPER_MODEL", "base")
        self._model = None  # lazy init on first transcribe

        # Validate
        valid = {"tiny", "base", "small", "medium", "large-v2", "large-v3"}
        if self.model_size not in valid:
            raise ValueError(f"Invalid WHISPER_MODEL '{self.model_size}'. Choose: {valid}")

        print(f"[STT] FasterWhisperSTT ready (model={self.model_size}, compute=int8)")

    def _get_model(self):
        """Lazy-load model on first use (downloads from HuggingFace if needed)."""
        if self._model is None:
            from faster_whisper import WhisperModel
            print(f"[STT] Loading faster-whisper/{self.model_size} (int8)...")
            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )
            print(f"[STT] faster-whisper/{self.model_size} loaded")
        return self._model

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "it"
    ) -> Dict[str, Any]:
        """Transcribe audio using faster-whisper in a thread executor."""
        import time
        start_time = time.time()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            audio_path = f.name

        try:
            def _run():
                model = self._get_model()
                segments, info = model.transcribe(
                    audio_path,
                    language=language,
                    beam_size=1,         # faster decode
                    vad_filter=True,     # skip silence
                    vad_parameters={"min_silence_duration_ms": 500},
                )
                text = " ".join(s.text for s in segments).strip()
                return text, info.language

            text, detected_lang = await asyncio.get_event_loop().run_in_executor(
                None, _run
            )

            latency_ms = (time.time() - start_time) * 1000
            return {
                "text": text,
                "confidence": 0.92,
                "language": detected_lang or language,
                "engine": f"faster_whisper_{self.model_size}",
                "latency_ms": latency_ms,
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "engine": f"faster_whisper_{self.model_size}",
                "error": str(e),
                "latency_ms": latency_ms,
            }
        finally:
            try:
                Path(audio_path).unlink()
            except Exception:
                pass


# =============================================================================
# GROQ STT ENGINE (FALLBACK)
# =============================================================================

class GroqSTT(STTEngine):
    """
    Cloud STT using Groq Whisper API.

    WER: ~21.7% due to audio compression.
    Use as fallback when whisper.cpp unavailable.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")

        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=self.api_key)
        print("[STT] Groq STT initialized (cloud fallback)")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "it"
    ) -> Dict[str, Any]:
        """Transcribe audio using Groq Whisper API."""
        import time
        start_time = time.time()

        try:
            # Create file-like object for Groq API
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            transcription = await self.client.audio.transcriptions.create(
                file=("audio.wav", audio_file),
                model="whisper-large-v3",
                language=language,
                response_format="text"
            )

            latency_ms = (time.time() - start_time) * 1000

            return {
                "text": transcription.strip() if isinstance(transcription, str) else transcription.text.strip(),
                "confidence": 0.85,  # Lower confidence due to compression
                "language": language,
                "engine": "groq",
                "latency_ms": latency_ms
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "engine": "groq",
                "error": str(e),
                "latency_ms": latency_ms
            }


# =============================================================================
# HYBRID STT (OFFLINE + FALLBACK)
# =============================================================================

class HybridSTT(STTEngine):
    """
    Hybrid STT engine: FasterWhisper (primary) → whisper.cpp → Groq (fallback).

    Priority:
        1. FasterWhisperSTT (int8 CPU, 4-6x faster than whisper.cpp)
        2. WhisperOfflineSTT (ggml-based whisper.cpp, slower)
        3. GroqSTT (cloud fallback)
    """

    def __init__(self):
        self.primary: Optional[STTEngine] = None
        self.fallback: Optional[STTEngine] = None

        # Try FasterWhisper first (best CPU performance)
        try:
            self.primary = FasterWhisperSTT()
            print("[STT] Primary engine: faster-whisper (int8 CPU)")
        except Exception as e:
            print(f"[STT] faster-whisper not available: {e}")
            # Fall back to whisper.cpp
            try:
                self.primary = WhisperOfflineSTT()
                print("[STT] Primary engine: whisper.cpp (offline)")
            except Exception as e2:
                print(f"[STT] whisper.cpp not available: {e2}")

        # Initialize Groq fallback
        try:
            self.fallback = GroqSTT()
            print("[STT] Fallback engine: Groq (cloud)")
        except Exception as e:
            print(f"[STT] Groq fallback not available: {e}")

        if not self.primary and not self.fallback:
            raise RuntimeError("No STT engine available")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "it"
    ) -> Dict[str, Any]:
        """Transcribe using primary engine, fallback on error."""

        # Try primary (whisper.cpp)
        if self.primary:
            try:
                result = await self.primary.transcribe(audio_data, language)
                if result.get("text"):
                    return result
            except Exception as e:
                print(f"[STT] Primary failed: {e}")

        # Fallback to Groq
        if self.fallback:
            return await self.fallback.transcribe(audio_data, language)

        return {
            "text": "",
            "confidence": 0.0,
            "language": language,
            "engine": "none",
            "error": "No STT engine available"
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_stt_instance: Optional[STTEngine] = None


def get_stt_engine(prefer_offline: bool = True) -> STTEngine:
    """
    Get STT engine instance (singleton).

    Args:
        prefer_offline: If True, prefer whisper.cpp over Groq

    Returns:
        STT engine instance
    """
    global _stt_instance

    if _stt_instance is None:
        if prefer_offline:
            _stt_instance = HybridSTT()
        else:
            try:
                _stt_instance = GroqSTT()
            except Exception:
                _stt_instance = HybridSTT()

    return _stt_instance


# =============================================================================
# POST-PROCESSING CORRECTOR
# =============================================================================

class WhisperCorrector:
    """
    Post-processing correction for common STT errors.

    Fixes domain-specific misrecognitions in Italian booking context.
    """

    def __init__(self):
        # Common misrecognitions in Italian booking domain
        self.replacements = {
            # Service names
            "taglie": "taglio",
            "tiglio": "taglio",
            "coloure": "colore",
            "permanante": "permanente",
            "mescles": "meches",
            "balay": "balayage",
            "piega è": "piega",
            "la piega": "piega",

            # Date/time
            "domenica prossima": "domenica prossimo",
            "il lunedì": "lunedì",
            "oggi è": "oggi",

            # Common STT artifacts
            " .": ".",
            " ,": ",",
            "  ": " ",
        }

    def correct(self, text: str) -> str:
        """Apply corrections to transcribed text."""
        corrected = text
        for wrong, correct in self.replacements.items():
            corrected = corrected.replace(wrong, correct)
        return corrected.strip()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_stt():
        print("Testing STT module...")

        # Get engine
        try:
            stt = get_stt_engine()
            print(f"Engine: {type(stt).__name__}")

            # Test with dummy audio (would need real audio for actual test)
            print("STT module initialized successfully")

        except Exception as e:
            print(f"STT initialization failed: {e}")

    asyncio.run(test_stt())
