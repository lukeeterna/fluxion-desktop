---
phase: f-sara-voice
plan: 05
type: execute
wave: 3
depends_on:
  - f-sara-voice-03
  - f-sara-voice-04
files_modified:
  - voice-agent/tests/test_tts_adaptive.py
  - voice-agent/src/tts_engine.py
autonomous: false

must_haves:
  truths:
    - "test_tts_adaptive.py runs on iMac with 0 FAIL — tests TTSEngineSelector, PiperTTSEngine synthesis, TTSDownloadManager mode persistence"
    - "PiperTTS latency P95 <= 200ms on iMac (measured via test_tts_adaptive.py benchmark)"
    - "curl http://192.168.1.12:3002/api/tts/hardware shows capable=true on iMac (32GB+ RAM, 8 cores)"
    - "Entire pytest suite still at >=1896 PASS / 0 new FAIL after test file addition"
    - "ROADMAP.md F-SARA-VOICE status updated to COMPLETE"
    - "Human verifies SetupWizard step 9 renders correctly in Fluxion.app on iMac"
  artifacts:
    - path: "voice-agent/tests/test_tts_adaptive.py"
      provides: "Automated tests for FluxionTTS Adaptive — engine selector, Piper synthesis, mode persistence, latency benchmark"
      min_lines: 80
  key_links:
    - from: "voice-agent/tests/test_tts_adaptive.py"
      to: "voice-agent/src/tts_engine.py"
      via: "from src.tts_engine import ..."
      pattern: "from src.tts_engine import"
---

<objective>
Write test_tts_adaptive.py, run full pytest suite on iMac, measure P95 latency for Piper, do human UI verify of SetupWizard step 9, and update ROADMAP.md to mark F-SARA-VOICE complete.

Purpose: Verification gate before marking this phase done. Ensures FluxionTTS Adaptive doesn't break existing tests and that P95 latency (Piper) stays under 200ms target on iMac hardware.

Output:
- voice-agent/tests/test_tts_adaptive.py (new file)
- ROADMAP.md updated
- Phase marked COMPLETE
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@voice-agent/src/tts_engine.py
@voice-agent/src/tts_download_manager.py
@.planning/phases/f-sara-voice/f-sara-voice-03-SUMMARY.md
@.planning/phases/f-sara-voice/f-sara-voice-04-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write test_tts_adaptive.py — engine selection + Piper synthesis + latency benchmark</name>
  <files>voice-agent/tests/test_tts_adaptive.py</files>
  <action>
Create voice-agent/tests/test_tts_adaptive.py:

```python
"""
Tests for FluxionTTS Adaptive — TTSEngineSelector, PiperTTSEngine, TTSDownloadManager
Runs on iMac Python 3.9 — no torch/transformers required for these tests.
"""
import asyncio
import time
import pytest
from pathlib import Path

# Adjust sys.path for iMac test runner
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tts_engine import (
    TTSMode, TTSEngineSelector, PiperTTSEngine, QwenTTSEngine, create_tts_engine
)
from tts_download_manager import TTSDownloadManager


# ─── TTSEngineSelector tests ─────────────────────────────────────────────────

class TestTTSEngineSelector:

    def test_detect_hardware_returns_required_keys(self):
        hw = TTSEngineSelector.detect_hardware()
        assert 'ram_gb' in hw
        assert 'cpu_cores' in hw
        assert 'capable' in hw
        assert isinstance(hw['ram_gb'], float)
        assert isinstance(hw['cpu_cores'], int)
        assert isinstance(hw['capable'], bool)

    def test_detect_hardware_ram_positive(self):
        hw = TTSEngineSelector.detect_hardware()
        assert hw['ram_gb'] > 0

    def test_detect_hardware_cores_positive(self):
        hw = TTSEngineSelector.detect_hardware()
        assert hw['cpu_cores'] > 0

    def test_get_mode_fast_override(self):
        hw = {'ram_gb': 32.0, 'cpu_cores': 8, 'avx2': True, 'capable': True}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.FAST)
        assert mode == TTSMode.FAST

    def test_get_mode_quality_override(self):
        hw = {'ram_gb': 4.0, 'cpu_cores': 2, 'avx2': False, 'capable': False}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.QUALITY)
        assert mode == TTSMode.QUALITY

    def test_get_mode_auto_capable_returns_quality(self):
        hw = {'ram_gb': 16.0, 'cpu_cores': 8, 'avx2': True, 'capable': True}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.AUTO)
        assert mode == TTSMode.QUALITY

    def test_get_mode_auto_incapable_returns_fast(self):
        hw = {'ram_gb': 4.0, 'cpu_cores': 2, 'avx2': False, 'capable': False}
        mode = TTSEngineSelector.get_mode_for_hardware(hw, TTSMode.AUTO)
        assert mode == TTSMode.FAST

    def test_get_engine_fast_returns_piper(self):
        engine = TTSEngineSelector.get_engine(TTSMode.FAST)
        assert isinstance(engine, PiperTTSEngine)

    def test_create_tts_engine_fast(self):
        engine = create_tts_engine(TTSMode.FAST)
        assert isinstance(engine, PiperTTSEngine)


# ─── TTSDownloadManager tests ─────────────────────────────────────────────────

class TestTTSDownloadManager:

    def test_read_mode_returns_string(self):
        mode = TTSDownloadManager.read_mode()
        assert mode in ('quality', 'fast', 'auto')

    def test_write_and_read_mode_fast(self, tmp_path, monkeypatch):
        """write_mode persists, read_mode retrieves it."""
        mode_file = tmp_path / ".tts_mode"
        monkeypatch.setattr(
            "tts_download_manager._MODE_FILE", mode_file
        )
        TTSDownloadManager.write_mode('fast')
        assert TTSDownloadManager.read_mode() == 'fast'

    def test_write_and_read_mode_quality(self, tmp_path, monkeypatch):
        mode_file = tmp_path / ".tts_mode"
        monkeypatch.setattr(
            "tts_download_manager._MODE_FILE", mode_file
        )
        TTSDownloadManager.write_mode('quality')
        assert TTSDownloadManager.read_mode() == 'quality'

    def test_write_invalid_mode_raises(self):
        with pytest.raises(AssertionError):
            TTSDownloadManager.write_mode('invalid')

    def test_is_model_downloaded_returns_bool(self):
        result = TTSDownloadManager.is_model_downloaded()
        assert isinstance(result, bool)


# ─── PiperTTSEngine latency benchmark ─────────────────────────────────────────

class TestPiperTTSEngineLatency:
    """
    Latency benchmark: P95 < 200ms for Piper synthesis on iMac.
    Skipped if Piper binary not installed (marked as xfail in CI).
    """

    @pytest.mark.skipif(
        not Path("/usr/local/bin/piper").exists() and
        not Path("/usr/bin/piper").exists(),
        reason="Piper binary not installed"
    )
    def test_piper_synthesis_produces_wav_bytes(self):
        engine = PiperTTSEngine()
        audio = asyncio.get_event_loop().run_until_complete(
            engine.synthesize("Buongiorno, sono Sara.")
        )
        assert isinstance(audio, bytes)
        assert len(audio) > 1000  # at least 1KB of audio

    @pytest.mark.skipif(
        not Path("/usr/local/bin/piper").exists() and
        not Path("/usr/bin/piper").exists(),
        reason="Piper binary not installed"
    )
    def test_piper_p95_latency_under_200ms(self):
        """P95 < 200ms target for Piper on capable hardware."""
        engine = PiperTTSEngine()
        phrase = "Perfetto, ho registrato il suo appuntamento per martedì alle dieci."
        latencies = []
        N = 10
        for _ in range(N):
            t0 = time.perf_counter()
            asyncio.get_event_loop().run_until_complete(engine.synthesize(phrase))
            latencies.append((time.perf_counter() - t0) * 1000)

        latencies.sort()
        p95_idx = int(N * 0.95) - 1
        p95 = latencies[max(p95_idx, 0)]
        print(f"\n[Piper P95] {p95:.0f}ms (target: <200ms) | all: {[f'{x:.0f}' for x in latencies]}")
        assert p95 < 200, f"Piper P95 latency {p95:.0f}ms exceeds 200ms target"
```

After writing the file, commit on MacBook:
```bash
git add voice-agent/tests/test_tts_adaptive.py
git commit -m "test(f-sara-voice): add test_tts_adaptive.py — TTSEngineSelector + PiperTTSEngine + latency benchmark"
git push origin master
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
```

Then run full pytest on iMac:
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/test_tts_adaptive.py -v --tb=short 2>&1 | tail -30"
```

Then run full suite to confirm no regressions:
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10"
```
  </action>
  <verify>
From test_tts_adaptive.py run on iMac:
- TestTTSEngineSelector: all 9 tests PASS
- TestTTSDownloadManager: all 5 tests PASS
- TestPiperTTSEngineLatency: PASS or SKIP (not FAIL)
- Full suite: ≥1896 PASS / 0 new FAIL

From /api/tts/hardware on iMac:
ssh imac "curl -s http://127.0.0.1:3002/api/tts/hardware"
# Expected: {"success": true, "capable": true, "ram_gb": >= 16.0, "cpu_cores": >= 8}
  </verify>
  <done>
- test_tts_adaptive.py exists and runs on iMac
- TestTTSEngineSelector and TestTTSDownloadManager: 14 PASS, 0 FAIL
- Latency tests PASS or SKIP (never FAIL)
- Full pytest suite: ≥1896 PASS / 0 new FAIL
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
    - FluxionTTS Adaptive: QwenTTSEngine + PiperTTSEngine + TTSEngineSelector (plan 01)
    - TTSDownloadManager + /api/tts/hardware + /api/tts/mode endpoints (plan 02)
    - tts.py get_tts() updated to use adaptive engine (plan 03)
    - SetupWizard step 9 voice quality selector + VoiceSaraQuality.tsx in Impostazioni (plan 04)
    - test_tts_adaptive.py with 14 tests + latency benchmark (plan 05 task 1)
  </what-built>
  <how-to-verify>
    On iMac:
    1. Open Fluxion.app (or run in dev mode)
    2. Start a new setup wizard (or reset wizard state)
    3. Navigate to step 9 — verify "Qualità Voce di Sara" appears with hardware info badge
    4. Verify "Alta Qualità" is pre-selected (iMac has ≥8GB RAM, ≥4 cores)
    5. Verify "Veloce (Piper)" option is available
    6. Select "Veloce" → click "Usa Veloce →" → verify confirmation message appears
    7. Go to Impostazioni → Voice Agent → verify VoiceSaraQuality section shows current mode
    8. Verify Sara still responds normally via: curl http://127.0.0.1:3002/api/voice/process -X POST -H "Content-Type: application/json" -d '{"text":"Buongiorno"}'
    9. Confirm voice response is present in audio_base64 field
  </how-to-verify>
  <resume-signal>
    Type "approvato" to mark UI verified and continue to ROADMAP update, OR describe any issues found.
  </resume-signal>
</task>

<task type="auto">
  <name>Task 3: Update ROADMAP.md F-SARA-VOICE to COMPLETE + update STATE.md</name>
  <files>.planning/ROADMAP.md</files>
  <action>
After human approval in checkpoint:

**1. Update ROADMAP.md:**
Find the `### Phase F-SARA-VOICE: f-sara-voice` entry.
Change:
```
**Status:** ⏳ PENDING
**Plans:** TBD

Plans:
- [ ] TBD
```
To:
```
**Status:** ✅ COMPLETE (2026-03-XX) — Piper P95 <200ms on iMac · 14 adaptive TTS tests PASS · SetupWizard step 9 approved
**Plans:** 5 plans in 3 waves

Plans:
- [x] f-sara-voice-01-PLAN.md — Wave 1: tts_engine.py (QwenTTSEngine + PiperTTSEngine + TTSEngineSelector)
- [x] f-sara-voice-02-PLAN.md — Wave 1: tts_download_manager.py + /api/tts/hardware + /api/tts/mode endpoints
- [x] f-sara-voice-03-PLAN.md — Wave 2: tts.py wiring + orchestrator update + iMac sync + pytest verify
- [x] f-sara-voice-04-PLAN.md — Wave 2: SetupWizard step 9 + VoiceSaraQuality.tsx + type-check 0 errors
- [x] f-sara-voice-05-PLAN.md — Wave 3: test_tts_adaptive.py + latency benchmark + human verify + ROADMAP
```
Fill in actual date (2026-03-XX → today's date).

**2. Update STATE.md:**
- Change `Phase: f-sara-nlu-patterns — COMPLETE` to `Phase: f-sara-voice — COMPLETE`
- Update `Last completed plan: f-sara-nlu-patterns-04` to `f-sara-voice-05`
- Update `Last activity` to current date
- Update `Next phase: F-SARA-VOICE` to `Next phase: F17 (Windows build) or p0.5-onboarding-frictionless`

**3. Commit:**
```bash
git add .planning/ROADMAP.md .planning/STATE.md
git commit -m "docs(f-sara-voice): COMPLETE — FluxionTTS Adaptive shipped, P95 Piper verified, step 9 UI approved"
git push origin master
```
  </action>
  <verify>
grep "COMPLETE" /Volumes/MontereyT7/FLUXION/.planning/ROADMAP.md | grep "f-sara-voice"
# Expected: line with COMPLETE and f-sara-voice

git log --oneline -3
# Expected: latest commit has f-sara-voice in message
  </verify>
  <done>
- ROADMAP.md F-SARA-VOICE entry marked COMPLETE with date
- STATE.md updated to reflect f-sara-voice-05 as last completed
- Commit pushed to master
- Phase fully shipped
  </done>
</task>

</tasks>

<verification>
# Full suite on iMac:
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/ -q 2>&1 | tail -5"
# Expected: >= 1896 passed, 0 new failed

# Hardware endpoint:
ssh imac "curl -s http://127.0.0.1:3002/api/tts/hardware"
# Expected: {"success": true, "capable": true/false, "ram_gb": X, ...}

# ROADMAP check:
grep "COMPLETE" /Volumes/MontereyT7/FLUXION/.planning/ROADMAP.md | grep "sara-voice"
</verification>

<success_criteria>
- test_tts_adaptive.py: 14 tests PASS / 0 FAIL on iMac
- Piper P95 < 200ms (or SKIP if binary not installed — measured separately via live test)
- SetupWizard step 9 renders and functions correctly (human approved)
- VoiceSaraQuality.tsx visible in Impostazioni
- Sara voice pipeline still functional after all changes
- ROADMAP.md updated to COMPLETE
- Full pytest suite: ≥1896 PASS / 0 new FAIL
</success_criteria>

<output>
After completion, create .planning/phases/f-sara-voice/f-sara-voice-05-SUMMARY.md
</output>
