"""
FLUXION Voice Agent — Resource Path Helper for PyInstaller

When running as a PyInstaller bundle (frozen), data files are extracted
to sys._MEIPASS (read-only temp dir). Writable files (DBs, logs, state)
go to a persistent directory under ~/.fluxion/voice-agent/.

When running from source, both point to the voice-agent/ directory.
"""

import os
import sys
from pathlib import Path

_frozen = getattr(sys, "frozen", False)


def get_bundle_root() -> Path:
    """Root for bundled read-only data (FAQ, models, verticals config).

    - Frozen: sys._MEIPASS (PyInstaller extraction dir)
    - Source: voice-agent/ directory
    """
    if _frozen:
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


def get_writable_root() -> Path:
    """Root for writable persistent data (DBs, logs, session state).

    - Frozen: ~/.fluxion/voice-agent/ (persistent across runs)
    - Source: voice-agent/ directory (current behavior)
    """
    if _frozen:
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "Fluxion" / "voice-agent"
        elif sys.platform == "win32":
            appdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
            base = Path(appdata) / "Fluxion" / "voice-agent"
        else:
            base = Path.home() / ".fluxion" / "voice-agent"
        base.mkdir(parents=True, exist_ok=True)
        return base
    return Path(__file__).parent.parent


def is_frozen() -> bool:
    """True when running inside a PyInstaller bundle."""
    return _frozen
