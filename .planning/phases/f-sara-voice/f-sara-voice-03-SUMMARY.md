---
phase: f-sara-voice
plan: 03
subsystem: voice
tags: [tts, python, piper, qwen3-tts, adaptive, orchestrator, pipeline]

# Dependency graph
requires:
  - phase: f-sara-voice-01
    provides: "tts_engine.py with QwenTTSEngine + PiperTTSEngine + TTSEngineSelector"
  - phase: f-sara-voice-02
    provides: "TTSDownloadManager + .tts_mode persistence + 3 HTTP TTS endpoints in main.py"
provides:
  - "tts.py get_tts() delegates to create_tts_engine() via TTSEngineSelector"
  - "Adaptive TTS wired into live voice pipeline (orchestrator.py)"
  - "All legacy classes preserved (ChatterboxTTS, PiperTTS, SystemTTS)"
  - "iMac pipeline running with adaptive engine, 1897 PASS / 0 new FAIL"
affects:
  - f-sara-voice-04
  - f-sara-voice-05

# Tech tracking
tech-stack:
  added: [psutil, huggingface_hub (installed on iMac)]
  patterns: [try/except double-import pattern for relative+absolute imports, adaptive-with-fallback chain]

key-files:
  created:
    - voice-agent/assets/SARA_VOICE_PLACEHOLDER.md
  modified:
    - voice-agent/src/tts.py
    - voice-agent/src/orchestrator.py

key-decisions:
  - "get_tts() uses _ADAPTIVE_ENGINE_AVAILABLE flag — clean degradation if tts_engine.py import fails"
  - "use_piper=False legacy -> SystemTTS preserved without modification"
  - "Adaptive fallback chain: create_tts_engine -> PiperTTS -> SystemTTS"
  - "Comment-only change in orchestrator.py — functionally unchanged call site"

patterns-established:
  - "try/except _ADAPTIVE_ENGINE_AVAILABLE flag pattern for optional module wiring"
  - "Double-import try block (relative .module then bare module) for package+direct execution compat"

# Metrics
duration: 18min
completed: 2026-03-15
---

# Phase f-sara-voice Plan 03: Python Wiring + iMac Sync Summary

**tts.py get_tts() now delegates to FluxionTTS Adaptive TTSEngineSelector with PiperTTS->SystemTTS fallback chain — pipeline confirmed 1897 PASS / 0 new FAIL on iMac**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-03-15T16:02:55Z
- **Completed:** 2026-03-15T16:20:55Z
- **Tasks:** 3
- **Files modified:** 3 (tts.py, orchestrator.py, assets/SARA_VOICE_PLACEHOLDER.md)

## Accomplishments

- Wired `create_tts_engine()` from tts_engine.py into `get_tts()` in tts.py — the adaptive engine is now the live path
- Preserved all legacy classes (ChatterboxTTS, PiperTTS, SystemTTS) and backward-compatible `use_piper=False` behavior
- Added clarifying comment in orchestrator.py above TTSCache init — call site functionally unchanged
- Synced to iMac, installed psutil + huggingface_hub, restarted pipeline
- Verified `/api/tts/hardware` and `/api/tts/mode` endpoints respond correctly (RAM 17.2GB, capable=true, mode=auto)
- Full pytest suite: 1897 PASS / 2 pre-existing FAIL / 0 new FAIL

## Task Commits

Each task was committed atomically:

1. **Task 1: Update tts.py get_tts() to delegate to tts_engine.create_tts_engine()** - `33d899f` (feat)
2. **Task 2: Add clarifying comment to orchestrator.py TTSCache init line** - `813c016` (feat)
3. **Task 3: Commit, sync iMac, restart pipeline, run pytest** - `02e3eee` (chore — placeholder asset)

## Files Created/Modified

- `voice-agent/src/tts.py` - Added adaptive engine imports + _ADAPTIVE_ENGINE_AVAILABLE flag; extended TTSEngine enum (QUALITY, FAST); replaced get_tts() to delegate to create_tts_engine() with graceful fallback chain
- `voice-agent/src/orchestrator.py` - Added one-line clarifying comment above TTSCache init; no functional change
- `voice-agent/assets/SARA_VOICE_PLACEHOLDER.md` - Placeholder README for sara-reference-voice.wav (Qwen3-TTS voice cloning)

## Decisions Made

- `_ADAPTIVE_ENGINE_AVAILABLE` flag at module level: clean degradation if tts_engine.py unavailable (e.g., partial deploy)
- Fallback chain `create_tts_engine() -> PiperTTS -> SystemTTS`: matches behavior of plans 01+02 design
- `use_piper=False` legacy path preserved explicitly (maps to SystemTTS, no audio mode)
- Comment-only change in orchestrator.py: keeping call site untouched reduces regression risk

## Deviations from Plan

### Minor Adaptation

**venv not in voice-agent/ on iMac**

- **Found during:** Task 3 (Step D — install requirements on iMac)
- **Issue:** `source venv/bin/activate` failed (no venv directory in voice-agent/)
- **Fix:** Used Python 3.9 directly (`/Library/Developer/CommandLineTools/.../Python -m pip install`)
- **Impact:** None — packages installed successfully, pipeline started clean

---

**Total deviations:** 1 minor adaptation (Rule 3 - Blocking, auto-resolved)
**Impact on plan:** Zero scope change, installation successful via direct Python path.

## Issues Encountered

- 2 pre-existing pytest failures confirmed (not introduced by this plan):
  - `test_holiday_handling.py::test_nearby_second_holiday` — date-sensitive holiday detection (CLOSED vs HOLIDAY enum)
  - `test_multi_verticale.py::test_intent_latency_consistency` — P95 21ms vs 10ms target (known latency issue from f03 notes)
- Both were failing before this plan and are unrelated to TTS wiring

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- FluxionTTS Adaptive is fully wired into the live pipeline
- `/api/tts/hardware`, `/api/tts/mode` (GET + POST) all operational on iMac
- Qwen3-TTS model not yet downloaded (model_downloaded: false) — download deferred to first Sara session
- Sara reference voice WAV not yet present — voice cloning mode will use generic voice until provided
- Ready for f-sara-voice-04 (UI settings panel in React + Tauri)

---
*Phase: f-sara-voice*
*Completed: 2026-03-15*
