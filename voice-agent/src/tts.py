"""
FLUXION Voice Agent - Text-to-Speech
Piper TTS integration (offline, Italian voices)
"""

import os
import subprocess
import tempfile
import asyncio
from pathlib import Path
from typing import Optional

# Default voice model
DEFAULT_VOICE = "it_IT-paola-medium"

# Voice models available
VOICES = {
    "it_IT-paola-medium": "Paola (Femmina) - Voce calda e professionale",
    "it_IT-riccardo-medium": "Riccardo (Maschio) - Voce chiara",
}


class PiperTTS:
    """Piper Text-to-Speech wrapper."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        voice: str = DEFAULT_VOICE,
        piper_binary: Optional[str] = None
    ):
        """
        Initialize Piper TTS.

        Args:
            model_path: Full path to .onnx model file
            voice: Voice name (e.g., "it_IT-paola-medium")
            piper_binary: Path to piper executable
        """
        self.voice = voice

        # Find piper binary
        if piper_binary:
            self.piper_binary = Path(piper_binary)
        else:
            # Try common locations
            possible_paths = [
                Path.home() / ".local" / "bin" / "piper",
                Path("/usr/local/bin/piper"),
                Path("/usr/bin/piper"),
                Path.cwd() / "piper" / "piper",
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
            # Try common locations
            models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
            self.model_path = models_dir / f"{voice}.onnx"

        self._validate()

    def _validate(self):
        """Validate piper and model exist."""
        if self.piper_binary is None or not self.piper_binary.exists():
            raise RuntimeError(
                f"Piper binary not found. Install with: pip install piper-tts"
            )

        if not self.model_path.exists():
            raise RuntimeError(
                f"Voice model not found: {self.model_path}\n"
                f"Download from: https://github.com/rhasspy/piper/releases"
            )

    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech.

        Args:
            text: Text to synthesize

        Returns:
            WAV audio bytes
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        try:
            # Run piper
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

            # Read audio
            with open(output_path, "rb") as f:
                audio_data = f.read()

            return audio_data

        finally:
            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)

    async def synthesize_to_file(self, text: str, output_path: str) -> str:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to synthesize
            output_path: Output file path

        Returns:
            Output file path
        """
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

    @staticmethod
    def list_voices() -> dict:
        """List available Italian voices."""
        return VOICES

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        return {
            "voice": self.voice,
            "model_path": str(self.model_path),
            "piper_binary": str(self.piper_binary),
            "model_exists": self.model_path.exists(),
            "piper_exists": self.piper_binary.exists() if self.piper_binary else False
        }


# Fallback TTS using system commands
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

            # Convert to WAV using afconvert
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


def get_tts(use_piper: bool = True, **kwargs) -> PiperTTS | SystemTTS:
    """
    Get TTS instance.

    Args:
        use_piper: Use Piper TTS (recommended)
        **kwargs: Arguments for TTS constructor

    Returns:
        TTS instance
    """
    if use_piper:
        try:
            return PiperTTS(**kwargs)
        except RuntimeError:
            print("Warning: Piper not available, using system TTS")
            return SystemTTS()
    else:
        return SystemTTS()


# Test
async def test_tts():
    """Test TTS."""
    try:
        tts = PiperTTS()
        audio = await tts.synthesize("Ciao! Sono Sara, l'assistente vocale.")
        print(f"Generated {len(audio)} bytes of audio")
        return True
    except Exception as e:
        print(f"Piper TTS not available: {e}")
        print("Using system TTS fallback...")
        tts = SystemTTS()
        audio = await tts.synthesize("Ciao! Sono Sara.")
        print(f"Generated {len(audio)} bytes with system TTS")
        return True


if __name__ == "__main__":
    asyncio.run(test_tts())
