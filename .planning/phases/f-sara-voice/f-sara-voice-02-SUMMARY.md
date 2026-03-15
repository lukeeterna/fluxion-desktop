---
phase: f-sara-voice
plan: 02
subsystem: voice
tags: [tts, qwen3-tts, download-manager, huggingface-hub, http-endpoints, python, adaptive-tts]

requires:
  - phase: f-sara-voice-01
    provides: TTSEngineSelector.detect_hardware() used in tts_hardware_handler

provides:
  - TTSDownloadManager class with is_model_downloaded(), read_mode(), write_mode(), download_qwen_model()
  - Mode persistence via voice-agent/.tts_mode (plain text file)
  - GET /api/tts/hardware — returns {ram_gb, cpu_cores, avx2, capable, recommended_mode, model_downloaded}
  - GET /api/tts/mode — returns {current_mode, model_downloaded, reference_audio_path}
  - POST /api/tts/mode — persists mode preference (quality/fast/auto) to .tts_mode file

affects:
  - f-sara-voice-03 (tts.py refactor uses TTSDownloadManager.read_mode())
  - f-sara-voice-04 (Sara orchestrator startup reads mode via TTSDownloadManager)
  - f-sara-voice-05 (integration checkpoint verifies all three endpoints live)
  - Frontend SetupWizard + Impostazioni (consume these endpoints for TTS selection UI)

tech-stack:
  added:
    - huggingface_hub>=0.20.0 (model download via snapshot_download)
  patterns:
    - Plain-text file for lightweight mode persistence (.tts_mode — no DB needed)
    - Progress callback pattern: Callable[[float, str], None] for download progress
    - Lazy import of huggingface_hub inside download_qwen_model() — Python 3.9 safe

key-files:
  created:
    - voice-agent/src/tts_download_manager.py
  modified:
    - voice-agent/main.py (3 new endpoints + TTSDownloadManager import)
    - voice-agent/requirements.txt (huggingface_hub>=0.20.0 added)

key-decisions:
  - "Mode file .tts_mode is plain text (quality/fast/auto) — no JSON, no DB, readable by any tool"
  - "download_qwen_model() returns bool — caller decides error UX, never raises"
  - "tts_hardware_handler imports TTSEngineSelector lazily (inside handler) — no startup cost if endpoint unused"
  - "recommended_mode derived from capable flag: True→quality, False→fast"
  - "huggingface_hub imported with try/except inside download_qwen_model() — graceful if not installed"

patterns-established:
  - "HTTP endpoint + file-backed persistence: read_mode()/write_mode() operate on .tts_mode without DB"
  - "Progress callback: async downloader accepts Optional[Callable[[float, str], None]] for UI feedback"

duration: 10min
completed: 2026-03-15
---

# Phase f-sara-voice Plan 02: TTS Download Manager + HTTP Endpoints Summary

**TTSDownloadManager with mode persistence (.tts_mode) + three HTTP endpoints (GET /api/tts/hardware, GET /api/tts/mode, POST /api/tts/mode) enabling frontend TTS quality selection and Qwen3-TTS first-run download**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-15T15:53:40Z
- **Completed:** 2026-03-15T16:07:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `voice-agent/src/tts_download_manager.py` (79 lines) — TTSDownloadManager with all four required methods
- Added 3 HTTP endpoints to `voice-agent/main.py`: GET /api/tts/hardware, GET /api/tts/mode, POST /api/tts/mode
- Mode persistence verified: write_mode('fast') → read_mode() returns 'fast', write_mode('auto') resets correctly
- All endpoints backed by import-guarded, exception-safe handlers returning JSON {success: bool, ...}
- huggingface_hub added to requirements.txt for snapshot_download model fetching

## Task Commits

Each task was committed atomically:

1. **Task 1: Create tts_download_manager.py** - `1c137c2` (feat)
   - TTSDownloadManager class, .tts_mode file persistence, huggingface_hub in requirements.txt
2. **Task 2: Add /api/tts endpoints to main.py** - `74bcb00` (included in plan 01 docs commit)
   - Import + 3 route registrations + 3 handler methods + health tts field updated

**Plan metadata:** to be committed with this SUMMARY

## Files Created/Modified

- `voice-agent/src/tts_download_manager.py` — TTSDownloadManager class (new, 79 lines)
- `voice-agent/main.py` — 3 new TTS endpoints + TTSDownloadManager import + tts field "adaptive"
- `voice-agent/requirements.txt` — huggingface_hub>=0.20.0 added

## Decisions Made

- **Plain text .tts_mode:** A simple text file (not JSON, not SQLite) keeps the mode readable from shell, git-trackable if desired, and writable with one `Path.write_text()` call. Read default is "auto" on FileNotFoundError.
- **download_qwen_model() returns bool:** The download step is long-running and the UI needs to handle failure UX. Returning False instead of raising keeps the handler simple and the caller in control.
- **Lazy import in tts_hardware_handler:** `from src.tts_engine import TTSEngineSelector` inside the handler body avoids any startup cost on import — consistent with the lazy-import pattern established in plan 01.
- **recommended_mode is computed, not stored:** It's derived from `hw["capable"]` at request time so it always reflects current hardware state.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] tts_engine.py already existed from plan 01**
- **Found during:** Pre-execution check
- **Issue:** Plan 02 depends on `TTSEngineSelector` from `tts_engine.py`. File was already created and committed in plan 01 (commit f5d21f1) — no action needed.
- **Fix:** No action required — confirmed importable (`from src.tts_engine import TTSEngineSelector` works).
- **Files modified:** None (no deviation needed)
- **Verification:** `python3 -c "from src.tts_engine import TTSEngineSelector; print(TTSEngineSelector.detect_hardware())"` → success

**2. [Rule 3 - Blocking] main.py TTS endpoints already committed in plan 01 docs commit**
- **Found during:** Task 2 commit attempt
- **Issue:** Commit 74bcb00 (plan 01 SUMMARY docs commit) already included main.py with the 3 TTS endpoints, TTSDownloadManager import, and tts field "adaptive". The changes I applied were identical to what was already committed.
- **Fix:** Confirmed "nothing to commit" — all task 2 changes were already committed correctly.
- **Verification:** All assertions in plan 02 verification pass; `git show --stat HEAD` confirms main.py in 74bcb00.

---

**Total deviations:** 2 (both Rule 3 — pre-existing work, no code changes required)
**Impact on plan:** Zero scope change. Previous session pre-committed task 2 as part of plan 01's SUMMARY commit. All success criteria verified.

## Issues Encountered

None. All imports resolved cleanly. Verification passed on all assertions.

## User Setup Required

None — no external service configuration required for this plan.

The Qwen3-TTS model download (triggered by `download_qwen_model()`) requires internet access and approximately 1.2 GB disk space, but this happens at user-initiated first-run, not during setup.

## Next Phase Readiness

- Plan 03 (tts.py refactor): TTSDownloadManager.read_mode() available, TTSEngineSelector importable — ready
- Plan 04 (Sara orchestrator): all primitives available (read_mode, is_model_downloaded, detect_hardware)
- Frontend: GET /api/tts/hardware and GET /api/tts/mode available at voice-agent port 3002

---
*Phase: f-sara-voice*
*Completed: 2026-03-15*
