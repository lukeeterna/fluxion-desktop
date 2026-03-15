---
phase: f-sara-voice
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/tts_engine.py
autonomous: true

must_haves:
  truths:
    - "QwenTTSEngine.synthesize() produces WAV bytes using ONNX/transformers CPU pipeline on Python 3.9"
    - "PiperTTSEngine.synthesize() wraps existing Piper subprocess, identical contract to QwenTTSEngine"
    - "TTSEngineSelector.detect_hardware() returns {ram_gb, cpu_cores, avx2, capable} dict"
    - "TTSEngineSelector.get_engine() returns QwenTTSEngine if mode==quality, PiperTTSEngine otherwise"
    - "QwenTTSEngine gracefully degrades to PiperTTSEngine on import error (no torch/transformers)"
    - "All classes importable in Python 3.9 — no PyTorch, no CUDA, CPU-only ONNX or transformers[cpu]"
  artifacts:
    - path: "voice-agent/src/tts_engine.py"
      provides: "FluxionTTS Adaptive engine layer"
      exports: ["TTSEngineSelector", "QwenTTSEngine", "PiperTTSEngine", "TTSMode"]
      min_lines: 200
  key_links:
    - from: "voice-agent/src/tts_engine.py"
      to: "voice-agent/src/tts.py"
      via: "imported by tts.py in plan 03"
      pattern: "from .tts_engine import"
---

<objective>
Create voice-agent/src/tts_engine.py — the core FluxionTTS Adaptive engine layer.

Purpose: Decouple TTS engine selection from tts.py factory. QwenTTSEngine wraps Qwen3-TTS 0.6B via transformers[cpu] (Python 3.9 compatible, no PyTorch direct import — uses `transformers` pipeline which handles torch internally). PiperTTSEngine wraps existing Piper subprocess logic extracted from PiperTTS in tts.py. TTSEngineSelector detects hardware capabilities and returns the correct engine.

Output: voice-agent/src/tts_engine.py (new file, ~250 lines)
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@voice-agent/src/tts.py
@voice-agent/requirements.txt
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create tts_engine.py with TTSMode enum + TTSEngineSelector + QwenTTSEngine</name>
  <files>voice-agent/src/tts_engine.py</files>
  <action>
Create voice-agent/src/tts_engine.py with this exact structure:

**TTSMode enum (lines 1-30):**
```python
class TTSMode(str, Enum):
    AUTO = "auto"
    QUALITY = "quality"   # Qwen3-TTS
    FAST = "fast"         # Piper
```

**TTSEngineSelector (lines 31-130):**
- `detect_hardware() -> dict`: uses `psutil` for ram_gb (psutil.virtual_memory().total / 1e9), `os.cpu_count()` for cores, platform module for avx2 detection (on macOS/Linux read /proc/cpuinfo or use platform.processor(); on macOS use `sysctl -n machdep.cpu.features` subprocess — catch all exceptions, default avx2=False). Returns: `{"ram_gb": float, "cpu_cores": int, "avx2": bool, "capable": bool}` where `capable = ram_gb >= 8.0 and cpu_cores >= 4`.
- `get_mode_for_hardware(hw: dict, user_pref: TTSMode = TTSMode.AUTO) -> TTSMode`: if user_pref != AUTO return user_pref. If hw["capable"] return QUALITY else FAST.
- `get_engine(mode: TTSMode, reference_audio_path: Optional[str] = None) -> Union["QwenTTSEngine", "PiperTTSEngine"]`: creates QwenTTSEngine if mode==QUALITY, PiperTTSEngine if mode==FAST. On QwenTTSEngine init failure → log warning → fallback to PiperTTSEngine.

**QwenTTSEngine (lines 131-220):**
- Class with `_model = None` class-level singleton
- `__init__(self, model_id="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", reference_audio_path=None, sample_rate=24000, lazy_load=True)`
- `_load_model(self)`: imports from `transformers import pipeline` — uses `pipeline("text-to-speech", model=self.model_id, device="cpu")`. Stores in `QwenTTSEngine._model`. Catches ImportError → raises RuntimeError("transformers not installed").
- `async synthesize(self, text: str) -> bytes`: if not loaded, call `_load_model()`. Run inference in `asyncio.get_event_loop().run_in_executor(None, self._sync_synthesize, text)`. Returns WAV bytes.
- `_sync_synthesize(self, text: str) -> bytes`: calls `_model(text)["audio"]` — converts numpy array to WAV bytes via `soundfile.write` to BytesIO (or `scipy.io.wavfile.write` if soundfile unavailable).
- `get_info(self) -> dict`: returns `{"engine": "qwen3-tts", "model": self.model_id, "loaded": self._loaded, "quality": 9.5}`

NOTE: The `transformers` library handles torch internally. The code must NOT `import torch` directly at module level — only `from transformers import pipeline` inside `_load_model`. This makes the module importable on Python 3.9 without torch being explicitly required at import time.

NOTE: `psutil` may not be in requirements.txt. Import with try/except fallback:
```python
try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False
```
If psutil unavailable, use fallback: `ram_gb = 8.0, cpu_cores = os.cpu_count() or 4`.
  </action>
  <verify>
On MacBook (no iMac needed for this task):
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "from src.tts_engine import TTSEngineSelector, TTSMode, QwenTTSEngine, PiperTTSEngine; hw = TTSEngineSelector.detect_hardware(); print(hw); assert 'capable' in hw; print('OK')"
  </verify>
  <done>
- voice-agent/src/tts_engine.py exists
- TTSEngineSelector, TTSMode, QwenTTSEngine importable from Python 3.9 without torch/transformers installed (lazy imports only)
- detect_hardware() returns dict with ram_gb, cpu_cores, avx2, capable keys
- No import errors at module load time
  </done>
</task>

<task type="auto">
  <name>Task 2: Create PiperTTSEngine in tts_engine.py (extracted from tts.py PiperTTS)</name>
  <files>voice-agent/src/tts_engine.py</files>
  <action>
Append PiperTTSEngine class to voice-agent/src/tts_engine.py (lines 221+):

**PiperTTSEngine (append to same file):**
Extract the subprocess-based Piper logic from the existing `PiperTTS` class in `voice-agent/src/tts.py` (lines ~220-384). Do NOT remove from tts.py yet (that happens in plan 03). This is a clean copy with same subprocess pattern.

Key fields:
- `model_name = "it_IT-paola-medium"`
- `sample_rate = 22050`
- **Binary search order — mirror PiperTTS.__init__ in tts.py exactly:**
  1. `Path(sys.executable).parent / "piper"` (venv bin directory — checked FIRST, same as tts.py)
  2. `models/` subdir of voice-agent root
  3. `piper` on PATH
  4. `piper-tts` on PATH
  Read tts.py PiperTTS.__init__ to confirm the exact search order before implementing — do not deviate from it.
- `async synthesize(self, text: str) -> bytes`: same subprocess approach as PiperTTS in tts.py — write to tempfile, run piper subprocess, read WAV bytes.
- `get_info(self) -> dict`: `{"engine": "piper", "model": self.model_name, "quality": 7.5}`

After PiperTTSEngine, add module-level convenience function:
```python
def create_tts_engine(
    user_pref: TTSMode = TTSMode.AUTO,
    reference_audio_path: Optional[str] = None,
) -> Union[QwenTTSEngine, PiperTTSEngine]:
    """Public factory: detect hardware, apply preference, return engine."""
    hw = TTSEngineSelector.detect_hardware()
    mode = TTSEngineSelector.get_mode_for_hardware(hw, user_pref)
    return TTSEngineSelector.get_engine(mode, reference_audio_path)
```

Also add `psutil` to voice-agent/requirements.txt if not present (add line: `psutil>=5.9.0`).
  </action>
  <verify>
On MacBook:
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "
from src.tts_engine import PiperTTSEngine, create_tts_engine, TTSMode
e = PiperTTSEngine()
print('PiperTTSEngine info:', e.get_info())
e2 = create_tts_engine(TTSMode.FAST)
print('create_tts_engine FAST:', type(e2).__name__)
print('OK')
"
  </verify>
  <done>
- PiperTTSEngine importable and get_info() returns correct dict
- create_tts_engine(TTSMode.FAST) returns PiperTTSEngine instance
- create_tts_engine(TTSMode.AUTO) returns PiperTTSEngine or QwenTTSEngine depending on hardware
- PiperTTSEngine binary search order mirrors PiperTTS.__init__ in tts.py (venv bin first)
- psutil in requirements.txt
  </done>
</task>

</tasks>

<verification>
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "
from src.tts_engine import TTSEngineSelector, TTSMode, QwenTTSEngine, PiperTTSEngine, create_tts_engine
hw = TTSEngineSelector.detect_hardware()
assert set(hw.keys()) >= {'ram_gb', 'cpu_cores', 'capable'}, f'Missing keys: {hw}'
mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.FAST)
assert mode == TTSMode.FAST
mode_auto = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.AUTO)
assert mode_auto in (TTSMode.FAST, TTSMode.QUALITY)
eng = create_tts_engine(TTSMode.FAST)
assert isinstance(eng, PiperTTSEngine)
print('ALL CHECKS PASSED')
"
</verification>

<success_criteria>
- voice-agent/src/tts_engine.py exists with TTSMode, TTSEngineSelector, QwenTTSEngine, PiperTTSEngine, create_tts_engine
- Module importable without torch/transformers/psutil installed (graceful fallbacks)
- detect_hardware() works on iMac (macOS, Python 3.9)
- get_mode_for_hardware(AUTO) returns QUALITY when RAM>=8GB, cores>=4
- PiperTTSEngine binary search order is identical to PiperTTS.__init__ in tts.py
</success_criteria>

<output>
After completion, create .planning/phases/f-sara-voice/f-sara-voice-01-SUMMARY.md
</output>
