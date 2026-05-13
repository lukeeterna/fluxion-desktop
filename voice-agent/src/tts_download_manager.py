"""
FLUXION Voice Agent — TTS Download Manager
Manages Qwen3-TTS model download, Piper voice auto-download on first run,
mode persistence, and model presence checks.
Mode persisted to: voice-agent/.tts_mode (plain text: "quality", "fast", or "auto")
"""
import logging
import os
import urllib.error
import urllib.request
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

# ── Piper voice model auto-download (S211 P4) ───────────────────────────────
# Source: https://huggingface.co/rhasspy/piper-voices
# Target voice: Italian female "Paola" medium quality (~63MB)
# Used by PiperTTSEngine when bundle/writable/system paths are all empty,
# i.e. first sidecar launch with internet. Falls back to SystemTTS if offline.
_PIPER_VOICE_NAME = "it_IT-paola-medium"
_PIPER_HF_BASE = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "it/it_IT/paola/medium"
)
_PIPER_ONNX_URL = f"{_PIPER_HF_BASE}/{_PIPER_VOICE_NAME}.onnx"
_PIPER_JSON_URL = f"{_PIPER_HF_BASE}/{_PIPER_VOICE_NAME}.onnx.json"
_PIPER_TARGET_DIR = _WRITABLE_ROOT / "models" / "tts"
_PIPER_DOWNLOAD_TIMEOUT_S = 120  # 63MB on a slow consumer link still fits


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

    # ─── Piper voice model auto-download (S211 P4) ──────────────────────
    @staticmethod
    def is_piper_model_present() -> bool:
        """True if it_IT-paola-medium.onnx + .onnx.json exist in writable dir."""
        onnx = _PIPER_TARGET_DIR / f"{_PIPER_VOICE_NAME}.onnx"
        cfg = _PIPER_TARGET_DIR / f"{_PIPER_VOICE_NAME}.onnx.json"
        return onnx.exists() and cfg.exists()

    @staticmethod
    def get_piper_model_path() -> Path:
        """Return canonical target path for Piper ONNX model (may not exist)."""
        return _PIPER_TARGET_DIR / f"{_PIPER_VOICE_NAME}.onnx"

    @staticmethod
    def download_piper_model_sync(
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """
        Synchronously download the Piper Italian voice model from Hugging Face.

        Called by PiperTTSEngine._find_model() on first launch when the model
        is missing from bundle, writable, and system locations. Uses urllib
        (stdlib) to avoid an extra dependency on huggingface_hub for the
        offline-fallback engine.

        Idempotent: returns True immediately if both files already exist.
        Atomic: downloads to .part files then renames, so a killed process
        cannot leave a half-written .onnx that would crash PiperVoice.load().

        Returns:
            True on success (both files present), False on any failure.
        """
        try:
            _PIPER_TARGET_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            logger.error(
                "[TTSDownload] Cannot create Piper target dir %s: %s",
                _PIPER_TARGET_DIR, exc,
            )
            return False

        if TTSDownloadManager.is_piper_model_present():
            logger.info(
                "[TTSDownload] Piper voice already present at %s — skip",
                _PIPER_TARGET_DIR,
            )
            return True

        targets = [
            (_PIPER_ONNX_URL, _PIPER_TARGET_DIR / f"{_PIPER_VOICE_NAME}.onnx"),
            (_PIPER_JSON_URL, _PIPER_TARGET_DIR / f"{_PIPER_VOICE_NAME}.onnx.json"),
        ]

        if progress_callback:
            progress_callback(0.0, "Download voce italiana Sara in corso…")

        logger.info(
            "[TTSDownload] First-run: downloading Piper voice '%s' to %s",
            _PIPER_VOICE_NAME, _PIPER_TARGET_DIR,
        )

        for idx, (url, dest) in enumerate(targets):
            tmp = dest.with_suffix(dest.suffix + ".part")
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "FLUXION-VoiceAgent/1.0"},
                )
                with urllib.request.urlopen(
                    req, timeout=_PIPER_DOWNLOAD_TIMEOUT_S
                ) as resp:
                    total = int(resp.headers.get("Content-Length") or 0)
                    written = 0
                    chunk_size = 1 << 16  # 64 KB
                    with open(tmp, "wb") as fh:
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            fh.write(chunk)
                            written += len(chunk)
                            if progress_callback and total:
                                # weight: onnx ≈ 95 %, json ≈ 5 % of total bytes
                                file_frac = written / total
                                overall = (idx + file_frac) / len(targets)
                                progress_callback(
                                    overall, f"Scarico {dest.name}…"
                                )
                # atomic rename — only swap in once fully written
                os.replace(tmp, dest)
                logger.info(
                    "[TTSDownload] Downloaded %s (%d bytes)", dest.name, written
                )
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
                logger.error(
                    "[TTSDownload] Piper download failed for %s: %s", url, exc
                )
                # cleanup partial file
                try:
                    if tmp.exists():
                        tmp.unlink()
                except OSError:
                    pass
                if progress_callback:
                    progress_callback(0.0, f"Download fallito: {exc}")
                return False

        if progress_callback:
            progress_callback(1.0, "Voce italiana pronta")
        logger.info("[TTSDownload] Piper voice ready at %s", _PIPER_TARGET_DIR)
        return True
