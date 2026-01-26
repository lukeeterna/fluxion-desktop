# Session 2026-01-26 - VAD Integration Bug Fixes

## Summary

Fixed critical bugs in Voice Agent VAD integration that prevented proper audio processing when manually stopping the microphone.

## Issues Fixed

### 1. Manual Mic Stop Not Processing Audio (BUG-VAD-01)

**Problem:** When user manually clicked stop on microphone, the recorded audio was discarded and not sent for processing.

**Root Cause:** The `stopListening` function in `useVADRecorder` hook only returned audio if VAD had detected an `end_of_speech` event. When user manually stopped before VAD detected end of speech, `turnAudioRef.current` was null.

**Solution:**
- Added `allAudioRef` to track ALL recorded audio (not just pending chunks)
- On manual stop, concatenate all chunks and encode to WAV with proper header
- VAD turn audio still takes priority when available

**Commit:** `fe77613`

### 2. React Hooks "Should have a queue" Error (BUG-VAD-02)

**Problem:** App crashed with React error "Should have a queue. You are likely calling Hooks conditionally".

**Root Cause:** The cleanup `useEffect` called `cancelListening()` which called `setState()` after the component was unmounted.

**Solution:**
- Added `isMountedRef` to track component mount state
- Added `isMountedRef.current` checks before all `setState` calls
- Simplified cleanup `useEffect` to directly release resources without calling `cancelListening`
- Stop VAD session silently on unmount (fire-and-forget)

**Commit:** `c7dc35c`

## Files Modified

- `src/hooks/use-voice-pipeline.ts` - Major refactor of `useVADRecorder` hook
  - Added `allAudioRef` for complete audio tracking
  - Added `isMountedRef` for safe state updates
  - WAV encoding for manual stop fallback
  - Proper cleanup without setState after unmount

## Tests

- TypeScript type-check: ✅
- ESLint: ✅
- E2E Smoke Tests: 5/5 ✅
- E2E Voice Agent Tests: 7/7 ✅

## Commits

1. `fe77613` - fix(voice): manual mic stop now returns recorded audio
2. `c7dc35c` - fix(voice): prevent React setState after unmount in VAD hook

## Next Steps

- [ ] Voice Agent UX Polish (visual feedback improvements)
- [ ] Test VAD with different accents/noise levels
- [ ] Consider adding audio level meter visualization
- [ ] Test SMTP Email functionality
