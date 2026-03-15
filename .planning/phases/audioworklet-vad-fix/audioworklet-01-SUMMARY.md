---
phase: audioworklet-vad-fix
plan: "01"
subsystem: ui
tags: [audioworklet, vad, webaudio, tauri, wkwebview, typescript, react]

# Dependency graph
requires:
  - phase: voice-openmicloop
    provides: useVADRecorder hook with open-mic loop, waitForTurn, notifyTtsSpeaking
provides:
  - AudioWorklet processor file (public/audio-processor.worklet.js) with 4096-sample buffering
  - useVADRecorder migrated from ScriptProcessorNode to AudioWorkletNode
  - All 3 cleanup paths call port.close() + disconnect()
affects:
  - audioworklet-02 (build + human verify on iMac)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AudioWorkletNode replaces ScriptProcessorNode for audio capture in WKWebView"
    - "Worklet accumulates 128-sample frames into 4096-sample chunks before postMessage"
    - "port.close() called in all cleanup paths (stop, cancel, unmount)"

key-files:
  created:
    - public/audio-processor.worklet.js
  modified:
    - src/hooks/use-voice-pipeline.ts

key-decisions:
  - "4096-sample accumulation in worklet matches ScriptProcessorNode buffer size for VAD backend compatibility"
  - ".slice() used for postMessage copy — no transferable to prevent buffer neutering"
  - "AudioWorkletNode not connected to destination — GainNode silencer not needed"
  - "setInterval processAudioBuffer retained unchanged for HTTP chunk dispatch"

patterns-established:
  - "AudioWorklet pattern: public/*.worklet.js + addModule('/filename.worklet.js') + port.onmessage"
  - "Cleanup pattern: port.close() then disconnect() for AudioWorkletNode in all 3 paths"

# Metrics
duration: 3min
completed: 2026-03-15
---

# Phase audioworklet-vad-fix Plan 01: AudioWorklet Migration Summary

**ScriptProcessorNode replaced with AudioWorkletNode in useVADRecorder, fixing WKWebView audio throttling that broke VAD open-mic in production Tauri .app bundle**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-15T08:08:12Z
- **Completed:** 2026-03-15T08:11:35Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `public/audio-processor.worklet.js` — AudioWorkletProcessor subclass that accumulates 128-sample frames into 4096-sample chunks and posts copies to the main thread
- Migrated `useVADRecorder` in `use-voice-pipeline.ts` from `ScriptProcessorNode` + GainNode silencer to `AudioWorkletNode` with `port.onmessage` handler
- All 3 cleanup paths (stopListening, cancelListening, useEffect unmount) updated to call `port.close()` before `disconnect()`
- `processorRef` properly typed as `AudioWorkletNode | null` (removed `any`)
- `npm run type-check` passes with 0 errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Create AudioWorklet processor file** - `f4db853` (feat)
2. **Task 2: Migrate useVADRecorder to AudioWorkletNode** - `fe11f65` (feat)

## Files Created/Modified

- `public/audio-processor.worklet.js` — AudioChunkProcessor class, accumulates 4096 samples, posts Float32Array copies to main thread via port.postMessage
- `src/hooks/use-voice-pipeline.ts` — useVADRecorder migrated to AudioWorkletNode; GainNode silencer removed; all 3 cleanup paths updated

## Decisions Made

- **4096-sample accumulation in worklet**: The VAD backend was tuned for ~4096-sample chunks (matching previous ScriptProcessorNode buffer size). AudioWorklet's native frame size is 128 samples — too small individually. The worklet accumulates frames before posting.
- **.slice() for postMessage**: `this._buffer` is reused across frames. Using a transferable would neuter it after the first postMessage, causing silent data loss on all subsequent frames. `.slice()` creates an independent copy safely.
- **No GainNode silencer**: ScriptProcessorNode required a GainNode connected to destination to prevent garbage collection of the audio graph in WKWebView (RC-3 fix). AudioWorkletNode runs in a dedicated thread and stays alive without a destination connection.
- **setInterval retained**: The 100ms processAudioBuffer interval was not changed — it handles HTTP chunk dispatch to the VAD backend, which is separate from audio capture.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

ESLint `no-undef` errors for `AudioWorkletNode`, `AudioWorkletProcessor`, `MessageEvent`, and `registerProcessor` appear in the ESLint output but are false positives — these are valid DOM/AudioWorklet globals that TypeScript confirms via `tsc --noEmit` (0 errors). The pre-commit hook passes ("PASSED") because the hook script does not fail on ESLint `no-undef` for DOM globals. This is a pre-existing gap in the ESLint browser globals configuration, not introduced by this plan.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- AudioWorklet migration complete on MacBook (TypeScript layer)
- Ready for audioworklet-02: build `.app` on iMac via SSH + human verify Phone button in production
- iMac build required: `src-tauri/` Rust compilation + `public/audio-processor.worklet.js` bundled into `.app`
- Human verify step: open FLUXION.app on iMac, tap Phone button, confirm open-mic VAD works end-to-end

---
*Phase: audioworklet-vad-fix*
*Completed: 2026-03-15*
