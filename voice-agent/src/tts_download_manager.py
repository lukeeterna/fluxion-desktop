"""
FLUXION Voice Agent — TTS Download Manager
Manages Qwen3-TTS model download, mode persistence, and model presence checks.
Mode persisted to: voice-agent/.tts_mode (plain text: "quality", "fast", or "auto")
"""
import logging
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

try:
    from .resource_path import get_bundle_root, get_writable_root
except ImportError:
    from resource_path import get_bundle_root, get_writable_root

_BUNDLE_ROOT = get_bundle_root()
_WRITABLE_ROOT = get_writable_root()
_MODEL_DIR = _WRITABLE_ROOT / "models" / "qwen3-tts"
_MODE_FILE = _WRITABLE_ROOT / ".tts_mode"
_QWEN_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
_REFERENCE_AUDIO = _BUNDLE_ROOT / "assets" / "sara-reference-voice.wav"


class TTSDownloadManager:

    @staticmethod
    def is_model_downloaded() -> bool:
        """Return True if Qwen3-TTS model directory contains config.json."""
        return (_MODEL_DIR / "config.json").exists()

    @staticmethod
    def get_model_dir() -> Path:
        return _MODEL_DIR

    @staticmethod
    def get_reference_audio_path() -> Optional[str]:
        """Return path to Sara reference WAV if it exists, else None."""
        return str(_REFERENCE_AUDIO) if _REFERENCE_AUDIO.exists() else None

    @staticmethod
    def read_mode() -> str:
        """Read persisted TTS mode. Returns 'auto' if not set."""
        try:
            return _MODE_FILE.read_text().strip() or "auto"
        except FileNotFoundError:
            return "auto"

    @staticmethod
    def write_mode(mode: str) -> None:
        """Persist TTS mode ('quality', 'fast', or 'auto') to .tts_mode file."""
        assert mode in ("quality", "fast", "auto"), f"Invalid mode: {mode}"
        _MODE_FILE.write_text(mode)
        logger.info(f"[TTSDownload] TTS mode set to: {mode}")

    @staticmethod
    async def download_qwen_model(
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        """
        Download Qwen3-TTS model using huggingface_hub.snapshot_download.
        Returns True on success, False on failure.
        progress_callback(fraction: float, message: str) called during download.
        """
        try:
            from huggingface_hub import snapshot_download
        except ImportError:
            logger.warning("[TTSDownload] huggingface_hub not installed — cannot download model")
            if progress_callback:
                progress_callback(0.0, "huggingface_hub non installato")
            return False

        try:
            _MODEL_DIR.mkdir(parents=True, exist_ok=True)
            if progress_callback:
                progress_callback(0.05, "Download modello Qwen3-TTS in corso...")

            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: snapshot_download(
                    repo_id=_QWEN_MODEL_ID,
                    local_dir=str(_MODEL_DIR),
                    ignore_patterns=["*.msgpack", "flax_model*"],
                )
            )

            if progress_callback:
                progress_callback(1.0, "Modello scaricato con successo")
            logger.info(f"[TTSDownload] Qwen3-TTS downloaded to {_MODEL_DIR}")
            return True

        except Exception as e:
            logger.error(f"[TTSDownload] Download failed: {e}")
            if progress_callback:
                progress_callback(0.0, f"Download fallito: {e}")
            return False
