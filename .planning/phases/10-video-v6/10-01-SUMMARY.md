---
phase: 10-video-v6
plan: 01
subsystem: video
tags: [edge-tts, storyboard, json, voiceover, mp3, video-production, ffmpeg]

# Dependency graph
requires:
  - phase: 9-screenshot-perfetti
    provides: "22-pacchetti.png and 23-fedelta.png captured on iMac (Phase 9)"
  - phase: research
    provides: "video-copywriter-v6-research.md + storyboard-v6-research.md (S113-114)"
provides:
  - "scripts/video-production-v6.json: 27-scene storyboard, V6 single source of truth"
  - "scripts/generate-v6-voiceover.py: Edge-TTS generation script, async with dialogue support"
  - "tmp-video-build/voice_scene_*.mp3: 22 voiceover MP3s ready for compositing"
  - "tmp-video-build/voiceover-manifest.json: maps all 27 scenes to mp3_path + duration_seconds"
affects: ["10-02-video-compositing", "10-03-video-render", "10-04-video-review"]

# Tech tracking
tech-stack:
  added: ["edge_tts (Python async TTS library, IsabellaNeural + DiegoNeural)"]
  patterns: ["Storyboard JSON as single source of truth for video assembly", "Async TTS generation with asyncio.run(main())", "Dialogue concat with 0.3s silence gaps via ffmpeg"]

key-files:
  created:
    - "scripts/video-production-v6.json"
    - "scripts/generate-v6-voiceover.py"
    - "tmp-video-build/voice_scene_*.mp3 (22 files)"
    - "tmp-video-build/voiceover-manifest.json"
  modified: []

key-decisions:
  - "scene_20 uses 22-pacchetti.png (Phase 9 asset) — first time pacchetti feature visible in any video"
  - "scene_23 voiceover: centoventi euro al mese / quattromilatrecentoventi euro (VID-07 compliance)"
  - "scene_08 is dialogue type with DiegoNeural + IsabellaNeural alternating (35.4s total)"
  - "PAS structure: Problem 0:00-0:08, Agitate 0:08-0:50, Solution 0:50-3:55, CTA 3:55-5:00"
  - "Hook: 4 AI clips x 2s (salone, officina, palestra, elettrauto) — covers 4 macro-verticali in 8s"
  - "Regola rispettata: mai piu di 2 screenshot consecutivi senza break AI clip"

patterns-established:
  - "Storyboard JSON schema: meta + chapters[] + scenes[] with id/type/file/voiceover/trim/transition fields"
  - "Voiceover manifest: scene_id -> {mp3_path, duration_seconds, type, voice}"
  - "Edge-TTS rate: Sara=-5%, Cliente=+0%, both voices identified by voice field in dialogue lines"

requirements-completed: [VID-01, VID-04, VID-07]

# Metrics
duration: 5min
completed: 2026-03-26
---

# Phase 10 Plan 01: V6 Storyboard + Voiceover Summary

**27-scene PAS storyboard JSON + 22 Edge-TTS MP3 voiceovers generated, with correct competitor pricing (centoventi euro al mese) and 22-pacchetti.png as first-ever visual of pacchetti feature**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-26T17:11:59Z
- **Completed:** 2026-03-26T17:16:34Z
- **Tasks:** 2
- **Files modified:** 2 created + 23 MP3 files generated

## Accomplishments
- V6 storyboard JSON with 8 chapters, 27 scenes, all VID-04 features covered (Dashboard, Calendario, Clienti, Schede, Pacchetti, Fedelta, Sara, Cassa, Analytics)
- 22 Edge-TTS voiceover MP3 files generated (5 silent scenes: 01-04 hook + 27 logo splash)
- scene_08 dialogue: 35.4s alternating DiegoNeural (cliente) and IsabellaNeural (Sara)
- scene_23 price section: 35.7s with exact VID-07 strings "centoventi euro al mese" and "quattromilatrecentoventi euro"
- voiceover-manifest.json ready for video compositor in Plan 02

## Task Commits

Each task was committed atomically:

1. **Task 1: Create V6 storyboard JSON with all 27 scenes** - `09f8f7f` (feat)
2. **Task 2: Create voiceover generation script and produce all MP3 files** - `1da6768` (feat)

## Files Created/Modified
- `scripts/video-production-v6.json` - V6 storyboard: 8 chapters, 27 scenes, PAS structure, all file paths verified
- `scripts/generate-v6-voiceover.py` - Edge-TTS generation script with dialogue support, manifest output
- `tmp-video-build/voice_scene_*.mp3` - 22 voiceover MP3 files (28 total including dialogue parts)
- `tmp-video-build/voiceover-manifest.json` - Maps 27 scenes to mp3_path + duration_seconds

## Decisions Made
- scene_20 uses `22-pacchetti.png` (Phase 9 captured) instead of storyboard-research's suggestion of 21-trasformazioni-prima-dopo.png — pacchetti feature now correctly visible for first time
- scene_23 voiceover updated from V5 copy ("seicento euro all'anno") to correct competitor price: "centoventi euro al mese" (€120/mo market rate, €4320 over 3 years)
- Dialogue scene (scene_08) voice identification uses "DiegoNeural"/"IsabellaNeural" strings in voiceover_dialogue array for clean voice dispatch in generator script
- Total voiceover duration is 334.7s (5.6 min) which exceeds video target — this is intentional: compositor (Plan 02) extends/loops clips to match audio duration per scene

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None — edge_tts was already installed, all AI clips and screenshots verified to exist on disk before JSON creation.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 02 (video compositing) can proceed immediately
- voiceover-manifest.json provides all timing data needed by compositor
- All 13 AI clips in landing/assets/ai-clips-v2/ verified present
- All 11 unique screenshots referenced in storyboard verified present in landing/screenshots/
- VID-07 compliance verified: "centoventi euro al mese" appears 4x in JSON

---
*Phase: 10-video-v6*
*Completed: 2026-03-26*
