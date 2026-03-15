---
phase: f-sara-voice
plan: 04
subsystem: ui
tags: [react, typescript, tts, voice-quality, setup-wizard, impostazioni]

# Dependency graph
requires:
  - phase: f-sara-voice-02
    provides: /api/tts/hardware and /api/tts/mode HTTP endpoints in voice-agent/main.py
provides:
  - VoiceSaraQuality.tsx — post-install TTS mode selector in Impostazioni
  - SetupWizard step 9 — voice quality selector during first-run wizard
  - VoiceAgentSettings.tsx wired to render VoiceSaraQuality — reachable from UI
affects: [f-sara-voice-05, future-onboarding-improvements]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hardware-aware UI: backend drives capability detection, UI reads response"
    - "Deferred model download: wizard only POSTs mode preference, 1.2GB download deferred to Sara startup"
    - "Offline-graceful fetch: all fetch calls caught silently — component renders degraded state"

key-files:
  created:
    - src/components/impostazioni/VoiceSaraQuality.tsx
  modified:
    - src/components/setup/SetupWizard.tsx
    - src/components/impostazioni/VoiceAgentSettings.tsx

key-decisions:
  - "VoiceSaraQuality.tsx already present in 02e3eee (plan-03 bonus commit) — re-used as-is"
  - "SetupWizard totalSteps bumped from 8 to 9 — step 9 positioned after Groq key step"
  - "useEffect on step===9 triggers hardware detection lazily — no fetch on mount"
  - "VoiceSaraQuality rendered after Groq key section with border-t divider in VoiceAgentSettings"

patterns-established:
  - "TTS mode UI pattern: 3 options (auto/quality/fast), hardware-aware badge, deferred download"
  - "Wizard step useEffect pattern: trigger side-effect only when step matches — avoids eager calls"

# Metrics
duration: 6min
completed: 2026-03-15
---

# Phase f-sara-voice Plan 04: TypeScript UI Summary

**Voice quality selection added to SetupWizard (step 9) and Impostazioni, wired to /api/tts/hardware + /api/tts/mode endpoints — hardware-aware TTS mode picker with deferred 1.2GB download.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-03-15T16:04:08Z
- **Completed:** 2026-03-15T16:10:08Z
- **Tasks:** 3/3
- **Files modified:** 3

## Accomplishments
- Created VoiceSaraQuality.tsx with Automatico/Alta Qualita/Veloce radio selector, hardware info display, and POST /api/tts/mode on save
- Added SetupWizard step 9 with hardware-detected defaults (quality on capable hardware, fast on incapable), useEffect for lazy hardware detection, deferred download messaging
- Wired VoiceSaraQuality into VoiceAgentSettings.tsx — reachable from Impostazioni → Voice Agent

## Task Commits

1. **Task 1: Create VoiceSaraQuality.tsx** - `02e3eee` (feat — committed in plan-03 bonus)
2. **Task 2: Add step 9 to SetupWizard** - `f0c783b` (feat)
3. **Task 3: Wire VoiceSaraQuality into VoiceAgentSettings** - `e36f51a` (feat)

## Files Created/Modified
- `src/components/impostazioni/VoiceSaraQuality.tsx` — Post-install TTS mode selector, fetches /api/tts/hardware + GET /api/tts/mode, POSTs mode on save
- `src/components/setup/SetupWizard.tsx` — totalSteps=9, step 9 TTS quality selector with hardware-aware defaults
- `src/components/impostazioni/VoiceAgentSettings.tsx` — Imports and renders VoiceSaraQuality below Groq key section

## Decisions Made
- VoiceSaraQuality.tsx was already committed in plan-03 final commit (02e3eee) as a bonus artifact — no duplicate commit needed for Task 1
- SetupWizard uses useEffect with `[step]` dependency to trigger hardware detection lazily only when user reaches step 9 — avoids unnecessary fetch on component mount
- Both capable and incapable hardware paths tested in JSX: capable shows "CONSIGLIATO" badge on quality, incapable shows badge on fast + amber warning on quality option
- Selecting "Alta Qualita" in wizard only POSTs mode='quality' to persist preference — actual 1.2GB Qwen3-TTS download deferred to first Sara startup (zero install friction)

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

Note: VoiceSaraQuality.tsx was already present from plan-03's bonus commit (02e3eee). This is not a deviation — the file content matched the plan spec exactly.

## Next Phase Readiness

- f-sara-voice-05 (checkpoint wave): All UI groundwork complete, can proceed to final wave verification
- npm run type-check: 0 errors confirmed
- No blockers
