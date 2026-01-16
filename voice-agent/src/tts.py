"""
FLUXION Voice Agent - Text-to-Speech
Multi-engine TTS: Chatterbox Italian (primary) + Piper (fallback)

Voice Assistant: Sara
All TTS engines output as "Sara" - the FLUXION voice assistant

TTS Engines (priority order):
1. Chatterbox Italian - Best quality (9/10), 100-150ms CPU, 200MB
2. Piper (fallback) - Fast (50ms), lightweight (60MB)
3. System TTS - macOS say command (last resort)
"""

import os
import tempfile
import asyncio
import logging
from pathlib import Path
from typing import Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# VOICE ASSISTANT: Sara
# ═══════════════════════════════════════════════════════════════════

VOICE_NAME = "Sara"  # Public-facing name for the voice assistant


class TTSEngine(Enum):
    """Available TTS engines."""
    CHATTERBOX = "chatterbox"  # Primary: Best Italian quality
    PIPER = "piper"            # Fallback: Fast, lightweight
    SYSTEM = "system"          # Last resort: macOS say


# Default TTS engine
DEFAULT_ENGINE = TTSEngine.CHATTERBOX

# Internal configs (not exposed to users)
_PIPER_MODEL = "it_IT-paola-medium"

_CHATTERBOX_CONFIG = {
    "model_id": "ayahyaa3/chatterbox-italian-tts",
    "quality": 9.0,
    "latency_ms": "100-150",
    "size_mb": 200,
    "exaggeration": 0.4,
    "cfg": 0.4,
}


# ═══════════════════════════════════════════════════════════════════
# CHATTERBOX TTS (Primary Engine)
# ═══════════════════════════════════════════════════════════════════

class ChatterboxTTS:
    """
    Chatterbox Italian TTS - Best quality for Italian voice agent.
    Quality: 9/10 | Latency: 100-150ms CPU | Size: 200MB
    """

    _model = None

    def __init__(
        self,
        device: str = "cpu",
        exaggeration: float = 0.4,
        cfg: float = 0.4,
        lazy_load: bool = True
    ):
        """
        Initialize Chatterbox TTS.

        Args:
            device: "cpu" or "cuda"
            exaggeration: Voice expressiveness (0.3-0.5 for natural)
            cfg: Guidance scale (0.3-0.5 for stable rhythm)
            lazy_load: Load model on first use (saves startup time)
        """
        self.device = device
        self.exaggeration = exaggeration
        self.cfg = cfg
        self._loaded = False

        if not lazy_load:
            self._load_model()

    def _load_model(self):
        """Load Chatterbox model."""
        if ChatterboxTTS._model is not None:
            self._loaded = True
            return

        try:
            from chatterbox.tts import ChatterboxTTS as CBModel

            logger.info(f"Loading {VOICE_NAME} TTS (device={self.device})...")
            ChatterboxTTS._model = CBModel.from_pretrained(
                _CHATTERBOX_CONFIG["model_id"],
                device=self.device
            )
            self._loaded = True
            logger.info(f"✅ {VOICE_NAME} TTS loaded successfully")

        except ImportError:
            raise RuntimeError(
                f"{VOICE_NAME} TTS not available. Install with:\n"
                "pip install chatterbox-tts torch torchaudio scipy"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load {VOICE_NAME} TTS: {e}")

    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech.

        Args:
            text: Italian text to synthesize

        Returns:
            WAV audio bytes (24kHz)
        """
        self._load_model()

        # Ensure Italian mode with [it] prefix
        if not text.strip().startswith("[it]"):
            text = "[it] " + text

        # Generate audio
        wav = ChatterboxTTS._model.generate(
            text,
            exaggeration=self.exaggeration,
            cfg=self.cfg
        )

        # Save to temp file and read bytes
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        try:
            import torchaudio as ta
            ta.save(output_path, wav, ChatterboxTTS._model.sr)

            with open(output_path, "rb") as f:
                audio_data = f.read()

            return audio_data

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    async def synthesize_to_file(self, text: str, output_path: str) -> str:
        """Convert text to speech and save to file."""
        self._load_model()

        if not text.strip().startswith("[it]"):
            text = "[it] " + text

        wav = ChatterboxTTS._model.generate(
            text,
            exaggeration=self.exaggeration,
            cfg=self.cfg
        )

        import torchaudio as ta
        ta.save(output_path, wav, ChatterboxTTS._model.sr)

        return output_path

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        return {
            "engine": "chatterbox",
            "voice_name": VOICE_NAME,
            "quality": _CHATTERBOX_CONFIG["quality"],
            "latency": _CHATTERBOX_CONFIG["latency_ms"],
            "device": self.device,
            "loaded": self._loaded,
        }


# ═══════════════════════════════════════════════════════════════════
# PIPER TTS (Fallback Engine)
# ═══════════════════════════════════════════════════════════════════

class PiperTTS:
    """Piper TTS wrapper - Fast fallback engine."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        piper_binary: Optional[str] = None,
    ):
        """Initialize Piper TTS."""
        # FLUXION models directory
        self.models_dir = Path(__file__).parent.parent / "models" / "tts"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Find piper binary
        if piper_binary:
            self.piper_binary = Path(piper_binary)
        else:
            import sys
            venv_bin = Path(sys.executable).parent / "piper"

            possible_paths = [
                venv_bin,
                Path.home() / ".local" / "bin" / "piper",
                Path("/usr/local/bin/piper"),
                Path("/usr/bin/piper"),
            ]
            self.piper_binary = None
            for path in possible_paths:
                if path.exists():
                    self.piper_binary = path
                    break

        # Find model
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.models_dir / f"{_PIPER_MODEL}.onnx"
            if not self.model_path.exists():
                system_dir = Path.home() / ".local" / "share" / "piper" / "voices"
                self.model_path = system_dir / f"{_PIPER_MODEL}.onnx"

        self._validate()

    def _validate(self):
        """Validate piper and model exist."""
        if self.piper_binary is None or not self.piper_binary.exists():
            raise RuntimeError("Piper binary not found. Install with: pip install piper-tts")

        if not self.model_path.exists():
            raise RuntimeError(f"Voice model not found: {self.model_path}")

    async def synthesize(self, text: str) -> bytes:
        """Convert text to speech."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                str(self.piper_binary),
                "--model", str(self.model_path),
                "--output_file", output_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate(text.encode())

            if process.returncode != 0:
                raise RuntimeError(f"Piper failed: {stderr.decode()}")

            with open(output_path, "rb") as f:
                audio_data = f.read()

            return audio_data

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    async def synthesize_to_file(self, text: str, output_path: str) -> str:
        """Convert text to speech and save to file."""
        process = await asyncio.create_subprocess_exec(
            str(self.piper_binary),
            "--model", str(self.model_path),
            "--output_file", output_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate(text.encode())

        if process.returncode != 0:
            raise RuntimeError(f"Piper failed: {stderr.decode()}")

        return output_path

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        return {
            "engine": "piper",
            "voice_name": VOICE_NAME,
            "quality": 7.5,
            "model_path": str(self.model_path),
            "piper_binary": str(self.piper_binary),
        }


# ═══════════════════════════════════════════════════════════════════
# SYSTEM TTS (Last Resort Fallback)
# ═══════════════════════════════════════════════════════════════════

class SystemTTS:
    """Fallback TTS using macOS say command."""

    def __init__(self, voice: str = "Alice"):
        self.voice = voice  # macOS Italian voice

    async def synthesize(self, text: str) -> bytes:
        """Synthesize using macOS say command."""
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
            output_path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                "say",
                "-v", self.voice,
                "-o", output_path,
                text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()

            # Convert to WAV
            wav_path = output_path.replace(".aiff", ".wav")
            convert = await asyncio.create_subprocess_exec(
                "afconvert",
                "-f", "WAVE",
                "-d", "LEI16@16000",
                output_path, wav_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await convert.communicate()

            with open(wav_path, "rb") as f:
                audio_data = f.read()

            os.remove(wav_path)
            return audio_data

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        return {
            "engine": "system",
            "voice_name": VOICE_NAME,
            "quality": 5.0,
        }


# ═══════════════════════════════════════════════════════════════════
# TTS FACTORY
# ═══════════════════════════════════════════════════════════════════

def get_tts(
    engine: TTSEngine = DEFAULT_ENGINE,
    use_piper: bool = True,  # Legacy parameter for compatibility
    **kwargs
) -> Union[ChatterboxTTS, PiperTTS, SystemTTS]:
    """
    Get TTS instance with automatic fallback.

    Args:
        engine: TTS engine to use (default: Chatterbox)
        use_piper: Legacy param - if True prefers Piper, else system TTS
        **kwargs: Arguments for TTS constructor

    Returns:
        TTS instance (Sara voice)
    """
    # Handle legacy use_piper parameter
    if not use_piper:
        engine = TTSEngine.SYSTEM

    # Try primary engine: Chatterbox
    if engine == TTSEngine.CHATTERBOX:
        try:
            return ChatterboxTTS(**kwargs)
        except RuntimeError as e:
            logger.warning(f"Chatterbox not available: {e}")
            engine = TTSEngine.PIPER  # Fallback

    # Try fallback: Piper
    if engine == TTSEngine.PIPER:
        try:
            return PiperTTS(**kwargs)
        except RuntimeError as e:
            logger.warning(f"Piper not available: {e}")
            engine = TTSEngine.SYSTEM  # Last resort

    # Last resort: System TTS
    logger.warning("Using system TTS as last resort")
    return SystemTTS()


def get_sara_tts(**kwargs) -> Union[ChatterboxTTS, PiperTTS, SystemTTS]:
    """Get Sara TTS (FLUXION voice assistant)."""
    return get_tts(**kwargs)


# ═══════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════

async def test_tts():
    """Test TTS."""
    print("=" * 60)
    print(f"FLUXION TTS Test - {VOICE_NAME} Voice")
    print("=" * 60)

    test_phrase = f"Buongiorno! Sono {VOICE_NAME}, come posso aiutarla?"

    # Test Chatterbox
    try:
        print(f"\n1. Testing Chatterbox (primary)...")
        tts = ChatterboxTTS()
        audio = await tts.synthesize(test_phrase)
        print(f"   ✅ Generated {len(audio)} bytes")
        print(f"   Info: {tts.get_info()}")
        return True
    except Exception as e:
        print(f"   ❌ Chatterbox not available: {e}")

    # Test Piper fallback
    try:
        print(f"\n2. Testing Piper (fallback)...")
        tts = PiperTTS()
        audio = await tts.synthesize(test_phrase)
        print(f"   ✅ Generated {len(audio)} bytes")
        print(f"   Info: {tts.get_info()}")
        return True
    except Exception as e:
        print(f"   ❌ Piper not available: {e}")

    # System fallback
    print(f"\n3. Testing System TTS (last resort)...")
    tts = SystemTTS()
    audio = await tts.synthesize(test_phrase)
    print(f"   ✅ Generated {len(audio)} bytes")
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_tts())
