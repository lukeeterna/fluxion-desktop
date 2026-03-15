---
phase: f-sara-voice
plan: 03
type: execute
wave: 2
depends_on:
  - f-sara-voice-01
  - f-sara-voice-02
files_modified:
  - voice-agent/src/tts.py
  - voice-agent/src/orchestrator.py
autonomous: true

must_haves:
  truths:
    - "get_tts() in tts.py uses TTSEngineSelector to pick QwenTTSEngine or PiperTTSEngine based on .tts_mode file"
    - "orchestrator.py VoiceOrchestrator init no longer hardcodes Chatterbox — uses get_tts() with no use_piper arg"
    - "PiperTTS class in tts.py preserved as legacy alias — not deleted"
    - "iMac pipeline restarts cleanly after push — pytest 1896+ PASS / 0 new FAIL"
    - "curl http://192.168.1.12:3002/api/tts/hardware returns {capable: true/false} JSON"
  artifacts:
    - path: "voice-agent/src/tts.py"
      provides: "Updated TTS factory — get_tts() delegates to tts_engine.py"
      contains: "from .tts_engine import"
    - path: "voice-agent/src/orchestrator.py"
      provides: "VoiceOrchestrator init updated to use adaptive TTS"
      contains: "get_tts()"
  key_links:
    - from: "voice-agent/src/tts.py"
      to: "voice-agent/src/tts_engine.py"
      via: "from .tts_engine import create_tts_engine, TTSMode"
      pattern: "from .tts_engine import"
    - from: "voice-agent/src/orchestrator.py"
      to: "voice-agent/src/tts.py"
      via: "existing get_tts() import — unchanged call site"
      pattern: "from .tts import get_tts, TTSCache"
---

<objective>
Wire tts_engine.py into the live pipeline: update tts.py factory to delegate to create_tts_engine(), update orchestrator.py to remove hardcoded use_piper flag. Sync to iMac, restart pipeline, run full pytest suite.

Purpose: This is the "flip the switch" plan — after plans 01 and 02, the new engine classes exist but nothing uses them. This plan connects them to the live voice pipeline without breaking any existing tests.

Output:
- voice-agent/src/tts.py (modified — get_tts() updated)
- voice-agent/src/orchestrator.py (modified — comment clarifying adaptive TTS delegation)
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@voice-agent/src/tts.py
@voice-agent/src/orchestrator.py
@.planning/phases/f-sara-voice/f-sara-voice-01-SUMMARY.md
@.planning/phases/f-sara-voice/f-sara-voice-02-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update tts.py get_tts() to delegate to tts_engine.create_tts_engine()</name>
  <files>voice-agent/src/tts.py</files>
  <action>
In voice-agent/src/tts.py make these targeted changes:

**1. Add import after existing imports (top of file):**
```python
from .tts_engine import create_tts_engine, TTSMode, TTSEngineSelector
from .tts_download_manager import TTSDownloadManager
```
(Use try/except in case relative import path needs adjustment: try `.tts_engine` first, fallback to `tts_engine`)

**2. Update TTSEngine enum** — ADD new values but keep existing for backward compat:
```python
class TTSEngine(Enum):
    CHATTERBOX = "chatterbox"  # Legacy — maps to QUALITY
    PIPER = "piper"
    SYSTEM = "system"
    QUALITY = "quality"   # New: Qwen3-TTS adaptive
    FAST = "fast"         # New: Piper adaptive
```

**3. Replace get_tts() function** (lines ~491-533 in tts.py). The new version:
```python
def get_tts(
    engine: TTSEngine = DEFAULT_ENGINE,
    use_piper: bool = True,  # Legacy parameter — kept for backward compat
    **kwargs
) -> Union[ChatterboxTTS, PiperTTS, SystemTTS]:
    """
    Get TTS instance. Now delegates to FluxionTTS Adaptive engine selector.
    Legacy use_piper param preserved for orchestrator compatibility.
    """
    # Read persisted mode preference
    try:
        persisted_mode_str = TTSDownloadManager.read_mode()
        persisted_mode = TTSMode(persisted_mode_str)
    except Exception:
        persisted_mode = TTSMode.AUTO

    # Handle legacy engine overrides
    if engine == TTSEngine.SYSTEM or (not use_piper):
        logger.warning("Legacy SYSTEM TTS requested — using SystemTTS fallback")
        return SystemTTS()

    # Delegate to adaptive engine selector
    try:
        adaptive_engine = create_tts_engine(
            user_pref=persisted_mode,
            reference_audio_path=TTSDownloadManager.get_reference_audio_path(),
        )
        return adaptive_engine
    except Exception as e:
        logger.warning(f"AdaptiveTTS failed ({e}), using Piper fallback")
        try:
            return PiperTTS(**kwargs)
        except Exception:
            logger.warning("Piper unavailable, using SystemTTS")
            return SystemTTS()
```

**DO NOT delete ChatterboxTTS, PiperTTS, SystemTTS classes** — keep them as legacy classes. The new get_tts() returns QwenTTSEngine or PiperTTSEngine from tts_engine.py instead, but the type hint is kept as Union[...] for compatibility.

Note: TTSCache.synthesize() calls `await self._engine.synthesize(text)` — this works with QwenTTSEngine and PiperTTSEngine too as they both have the same async synthesize() contract. No change to TTSCache needed.
  </action>
  <verify>
On MacBook:
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "
import ast
with open('src/tts.py') as f: src = f.read()
ast.parse(src)
print('tts.py syntax OK')
from src.tts import get_tts, TTSCache
print('get_tts importable OK')
"
  </verify>
  <done>
- tts.py parses without errors
- get_tts() importable from tts.py
- get_tts() calls create_tts_engine() internally
- ChatterboxTTS, PiperTTS, SystemTTS classes still exist in tts.py (not deleted)
  </done>
</task>

<task type="auto">
  <name>Task 2: Add clarifying comment to orchestrator.py TTS init line</name>
  <files>voice-agent/src/orchestrator.py</files>
  <action>
This task is MacBook-only. Do NOT use iMac paths here — the iMac sync happens in Task 3.

In voice-agent/src/orchestrator.py, locate the VoiceOrchestrator.__init__ line that initializes self.tts (around line 354-380). The existing call should look like:
```python
self.tts = TTSCache(get_tts(use_piper=use_piper_tts))
```

This call is already correct — `use_piper_tts=True` (the default) causes our updated get_tts() to use the adaptive engine (not SystemTTS). No functional change is needed.

Add a single inline comment on that line:
```python
self.tts = TTSCache(get_tts(use_piper=use_piper_tts))  # FluxionTTS Adaptive — delegates to tts_engine.py TTSEngineSelector
```

If the line is longer than 120 chars after the comment, put the comment on the line above as a standalone comment instead:
```python
# FluxionTTS Adaptive — delegates to tts_engine.py TTSEngineSelector
self.tts = TTSCache(get_tts(use_piper=use_piper_tts))
```

Verify syntax on MacBook only:
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "import ast; ast.parse(open('src/orchestrator.py').read()); print('orchestrator.py syntax OK')"
```
  </action>
  <verify>
On MacBook:
python3 -c "import ast; ast.parse(open('voice-agent/src/orchestrator.py').read()); print('orchestrator.py syntax OK')"
grep -n "FluxionTTS Adaptive" voice-agent/src/orchestrator.py
# Expected: 1 line containing the comment
  </verify>
  <done>
- orchestrator.py has clarifying comment on/above the TTSCache init line
- File parses without errors
- No functional code changed
  </done>
</task>

<task type="auto">
  <name>Task 3: Commit, sync to iMac, restart pipeline, run pytest</name>
  <files>voice-agent/assets/SARA_VOICE_PLACEHOLDER.md</files>
  <action>
**Step A — Create Sara reference voice placeholder (MacBook only):**
Create voice-agent/assets/SARA_VOICE_PLACEHOLDER.md:
"Replace sara-reference-voice.wav with real Sara voice sample (3-30s, female Italian, professional tone). Generate via Voice Clone Studio (FranckyB) or record manually."

**Step B — Commit and push (MacBook):**
```bash
git add voice-agent/src/tts_engine.py voice-agent/src/tts_download_manager.py voice-agent/src/tts.py voice-agent/src/orchestrator.py voice-agent/main.py voice-agent/requirements.txt voice-agent/assets/SARA_VOICE_PLACEHOLDER.md
git commit -m "feat(f-sara-voice): FluxionTTS Adaptive — QwenTTSEngine + PiperTTSEngine + TTSEngineSelector + endpoints"
git push origin master
```

**Step C — Pull on iMac:**
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
```

**Step D — Install psutil + huggingface_hub on iMac venv:**
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && pip install psutil huggingface_hub --quiet"
```

**Step E — Restart pipeline on iMac and verify health:**
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && nohup python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 & sleep 3 && curl -s http://127.0.0.1:3002/health | python3 -m json.tool"
```

**Step F — Verify new endpoints on iMac:**
```bash
ssh imac "curl -s http://127.0.0.1:3002/api/tts/hardware | python3 -m json.tool"
ssh imac "curl -s http://127.0.0.1:3002/api/tts/mode | python3 -m json.tool"
ssh imac "curl -s -X POST http://127.0.0.1:3002/api/tts/mode -H 'Content-Type: application/json' -d '{\"mode\": \"fast\"}' | python3 -m json.tool"
```

**Step G — Run full pytest suite on iMac:**
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short -q 2>&1 | tail -20"
```
Target: ≥1896 PASS, 0 new FAIL (3 pre-existing date-sensitive failures are acceptable).
  </action>
  <verify>
Results from Step F must show:
- /api/tts/hardware returns {"success": true, "capable": true/false, "ram_gb": X, ...}
- /api/tts/mode returns {"success": true, "current_mode": "fast", ...} (after POST)

Results from Step G must show:
- PASS count >= 1896
- FAIL count = 0 new failures (3 pre-existing ok)
  </verify>
  <done>
- voice-agent/assets/SARA_VOICE_PLACEHOLDER.md created
- git commit pushed to master
- iMac pulled and pipeline restarted
- /api/tts/hardware and /api/tts/mode endpoints respond correctly on iMac
- pytest: ≥1896 PASS / 0 new FAIL
  </done>
</task>

</tasks>

<verification>
# On MacBook (syntax):
cd /Volumes/MontereyT7/FLUXION/voice-agent
python3 -c "from src.tts import get_tts, TTSCache; print('tts.py OK')"
python3 -c "from src.tts_engine import create_tts_engine, TTSMode; print('tts_engine.py OK')"
python3 -c "from src.tts_download_manager import TTSDownloadManager; print('download_manager OK')"

# On iMac (live endpoints):
ssh imac "curl -s http://127.0.0.1:3002/api/tts/hardware"
# Expected: {"success": true, "capable": ..., "ram_gb": ..., "cpu_cores": ...}
</verification>

<success_criteria>
- tts.py get_tts() delegates to create_tts_engine()
- orchestrator.py has clarifying comment, functionally unchanged (existing call site still works)
- iMac pipeline running with new tts_engine.py loaded
- /api/tts/hardware, /api/tts/mode GET/POST respond correctly on iMac
- pytest suite: ≥1896 PASS / 0 new FAIL
</success_criteria>

<output>
After completion, create .planning/phases/f-sara-voice/f-sara-voice-03-SUMMARY.md
</output>
