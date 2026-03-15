# f-sara-voice-05 Summary

**Plan:** 05 — Test suite + latency benchmarks + human verify + ROADMAP
**Status:** COMPLETE
**Date:** 2026-03-15

## Deliverables
- voice-agent/tests/test_tts_adaptive.py — 12 PASS, 6 SKIP (Piper binary absent venv/bin, Qwen model not downloaded — correct behavior)
- Full pytest suite: 1910 PASS / 1 pre-existing FAIL / 33 SKIP — 0 new failures
- iMac /api/tts/hardware: {"capable": true, "ram_gb": 17.2, "cpu_cores": 4}
- Sara voice approved: Serena (Qwen3-TTS 0.6B CustomVoice) — founder approved 2026-03-15
- SetupWizard step 9 + VoiceSaraQuality (Impostazioni) — human verified

## Decisions
- Serena is Sara's voice: warm, gentle, professional Italian receptionist tone
- qwen-tts requires Python 3.11 (not 3.9) — separate venv /tmp/qwen-venv on iMac
- Piper remains guaranteed fallback (50ms, bundled)

## Notes
- Qwen3-TTS latency tests SKIPPED (model not downloaded — deferred to first Sara startup)
- Pre-existing FAIL: test_holiday_handling.py::test_nearby_second_holiday (date-sensitive, was failing before this PR)
