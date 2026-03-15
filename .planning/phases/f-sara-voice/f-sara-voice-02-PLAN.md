---
phase: f-sara-voice
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/tts_download_manager.py
  - voice-agent/main.py
autonomous: true

must_haves:
  truths:
    - "GET /api/tts/hardware returns {ram_gb, cpu_cores, capable, recommended_mode} JSON — callable before model download"
    - "GET /api/tts/mode returns {current_mode, model_downloaded, reference_audio_path} JSON"
    - "POST /api/tts/mode {mode: 'quality'|'fast'|'auto'} persists preference to voice-agent/.tts_mode (plain text file)"
    - "TTSDownloadManager.download_qwen_model() downloads model to voice-agent/models/qwen3-tts/ with progress callback"
    - "TTSDownloadManager.is_model_downloaded() returns bool — checks for presence of config.json in model dir"
  artifacts:
    - path: "voice-agent/src/tts_download_manager.py"
      provides: "Model download + mode persistence logic"
      exports: ["TTSDownloadManager"]
      min_lines: 100
    - path: "voice-agent/main.py"
      provides: "Three new HTTP endpoints for hardware detection + TTS mode management"
      contains: "/api/tts/hardware"
  key_links:
    - from: "voice-agent/main.py"
      to: "voice-agent/src/tts_download_manager.py"
      via: "TTSDownloadManager imported in main.py handlers"
      pattern: "from src.tts_download_manager import"
---

<objective>
Create voice-agent/src/tts_download_manager.py and add three HTTP endpoints to main.py.

Purpose: The frontend (SetupWizard + Impostazioni) needs to know hardware capability (to show the right UI), current TTS mode, and trigger model download. The download manager handles first-run Qwen3-TTS model download with progress reporting and mode persistence via a simple file (voice-agent/.tts_mode).

Output:
- voice-agent/src/tts_download_manager.py (new file, ~130 lines)
- voice-agent/main.py (3 new endpoints added)
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@voice-agent/main.py
@voice-agent/src/tts.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create tts_download_manager.py with TTSDownloadManager</name>
  <files>voice-agent/src/tts_download_manager.py</files>
  <action>
Create voice-agent/src/tts_download_manager.py:

```python
"""
FLUXION Voice Agent — TTS Download Manager
Manages Qwen3-TTS model download, mode persistence, and model presence checks.
Mode persisted to: voice-agent/.tts_mode (plain text: "quality", "fast", or "auto")
"""
import os
import logging
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

_VOICE_AGENT_DIR = Path(__file__).parent.parent
_MODEL_DIR = _VOICE_AGENT_DIR / "models" / "qwen3-tts"
_MODE_FILE = _VOICE_AGENT_DIR / ".tts_mode"
_QWEN_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
_REFERENCE_AUDIO = _VOICE_AGENT_DIR / "assets" / "sara-reference-voice.wav"


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
```

Add `huggingface_hub>=0.20.0` to voice-agent/requirements.txt if not present.
  </action>
  <verify>
On MacBook:
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "
from src.tts_download_manager import TTSDownloadManager
print('Downloaded:', TTSDownloadManager.is_model_downloaded())
print('Mode:', TTSDownloadManager.read_mode())
TTSDownloadManager.write_mode('fast')
assert TTSDownloadManager.read_mode() == 'fast'
TTSDownloadManager.write_mode('auto')
print('Mode reset:', TTSDownloadManager.read_mode())
print('OK')
"
  </verify>
  <done>
- voice-agent/src/tts_download_manager.py importable in Python 3.9
- TTSDownloadManager.is_model_downloaded(), read_mode(), write_mode() work correctly
- .tts_mode file created and readable
- huggingface_hub in requirements.txt
  </done>
</task>

<task type="auto">
  <name>Task 2: Add /api/tts/hardware, /api/tts/mode GET, /api/tts/mode POST endpoints to main.py</name>
  <files>voice-agent/main.py</files>
  <action>
In voice-agent/main.py, add the following changes:

**1. Import at top of file** (after existing src imports, around line 120):
```python
from src.tts_download_manager import TTSDownloadManager
```
Note: tts_engine import is NOT needed here — TTSEngineSelector is called lazily per request.

**2. In VoiceAgentHTTPServer._setup_routes()** (after the /api/metrics/latency line):
```python
self.app.router.add_get("/api/tts/hardware", self.tts_hardware_handler)
self.app.router.add_get("/api/tts/mode", self.tts_mode_handler)
self.app.router.add_post("/api/tts/mode", self.tts_mode_set_handler)
```

**3. Add three handler methods to VoiceAgentHTTPServer class** (after latency_metrics_handler):

```python
async def tts_hardware_handler(self, request):
    """Return hardware capability for TTS quality selection."""
    try:
        from src.tts_engine import TTSEngineSelector
        hw = TTSEngineSelector.detect_hardware()
        return web.json_response({
            "success": True,
            "ram_gb": round(hw["ram_gb"], 1),
            "cpu_cores": hw["cpu_cores"],
            "avx2": hw.get("avx2", False),
            "capable": hw["capable"],
            "recommended_mode": "quality" if hw["capable"] else "fast",
            "model_downloaded": TTSDownloadManager.is_model_downloaded(),
        })
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def tts_mode_handler(self, request):
    """Return current TTS mode and model status."""
    try:
        return web.json_response({
            "success": True,
            "current_mode": TTSDownloadManager.read_mode(),
            "model_downloaded": TTSDownloadManager.is_model_downloaded(),
            "reference_audio_path": TTSDownloadManager.get_reference_audio_path(),
        })
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def tts_mode_set_handler(self, request):
    """Persist TTS mode preference."""
    try:
        data = await request.json()
        mode = data.get("mode", "auto")
        if mode not in ("quality", "fast", "auto"):
            return web.json_response(
                {"success": False, "error": f"Invalid mode: {mode}"},
                status=400
            )
        TTSDownloadManager.write_mode(mode)
        return web.json_response({"success": True, "mode": mode})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)
```

Also update the health_handler's `"tts"` field from `"system"` to `"adaptive"` to reflect the new engine.
  </action>
  <verify>
On iMac (after sync — sync happens in plan 03, but MacBook can verify syntax):
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "
import ast, sys
with open('main.py') as f:
    src = f.read()
ast.parse(src)
print('main.py syntax OK')
assert '/api/tts/hardware' in src
assert '/api/tts/mode' in src
assert 'tts_hardware_handler' in src
assert 'tts_mode_set_handler' in src
print('All endpoints present')
"
  </verify>
  <done>
- main.py has /api/tts/hardware, /api/tts/mode GET and POST routes
- main.py has tts_hardware_handler, tts_mode_handler, tts_mode_set_handler methods
- main.py parses without syntax errors
- health_handler returns "tts": "adaptive"
  </done>
</task>

</tasks>

<verification>
On MacBook (syntax check only — endpoint functional test happens in plan 03 on iMac):
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "
from src.tts_download_manager import TTSDownloadManager
import ast
with open('main.py') as f:
    src = f.read()
ast.parse(src)
assert 'tts_hardware_handler' in src
assert 'tts_mode_handler' in src
assert 'tts_mode_set_handler' in src
assert 'TTSDownloadManager' in src
print('Plan 02 verification PASSED')
"
</verification>

<success_criteria>
- tts_download_manager.py importable, TTSDownloadManager has is_model_downloaded, read_mode, write_mode, download_qwen_model
- main.py has 3 new endpoints: GET /api/tts/hardware, GET /api/tts/mode, POST /api/tts/mode
- main.py parses without errors
- huggingface_hub added to requirements.txt
</success_criteria>

<output>
After completion, create .planning/phases/f-sara-voice/f-sara-voice-02-SUMMARY.md
</output>
