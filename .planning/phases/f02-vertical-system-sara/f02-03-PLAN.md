---
phase: f02-vertical-system-sara
plan: 03
type: execute
wave: 3
depends_on:
  - f02-02
files_modified:
  - ROADMAP_REMAINING.md
autonomous: false

must_haves:
  truths:
    - "Full test suite passes: 1160 original tests + all new guardrail and entity extractor tests"
    - "TypeScript type-check passes: 0 errors"
    - "Voice pipeline restarts successfully on iMac after Python changes"
    - "iMac health check returns 200 OK"
    - "ROADMAP_REMAINING.md F02 status updated to done with commit hash"
    - "Atomic commit created: feat(voice-agent): F02 vertical guardrails + entity extractor"
  artifacts:
    - path: "ROADMAP_REMAINING.md"
      provides: "F02 status marked done with commit hash"
      contains: "F02"
  key_links:
    - from: "voice-agent/tests/test_guardrails.py"
      to: "voice-agent/src/italian_regex.py"
      via: "pytest run on iMac confirms guardrail tests pass in Python 3.9 runtime"
      pattern: "pytest.*test_guardrails"
    - from: "voice-agent/tests/test_vertical_entity_extractor.py"
      to: "voice-agent/src/entity_extractor.py"
      via: "pytest run confirms entity extractor tests pass"
      pattern: "pytest.*test_vertical_entity_extractor"
---

<objective>
Verify F02 implementation end-to-end, commit, sync to iMac, restart voice pipeline, and close the phase.

Purpose: F02 is a blocker for the first sale. This plan gates completion with: full test suite green on iMac (Python 3.9), voice pipeline live, and a clean atomic commit.

Output: Passing test suite, restarted voice pipeline on iMac, atomic commit, updated ROADMAP_REMAINING.md.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/f02-vertical-system-sara/f02-01-SUMMARY.md
@.planning/phases/f02-vertical-system-sara/f02-02-SUMMARY.md
@ROADMAP_REMAINING.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: TypeScript check + full pytest suite on MacBook + atomic commit</name>
  <files>
    voice-agent/src/italian_regex.py
    voice-agent/src/orchestrator.py
    voice-agent/src/entity_extractor.py
    voice-agent/tests/test_guardrails.py
    voice-agent/tests/test_vertical_entity_extractor.py
  </files>
  <action>
Run the following verification sequence from the MacBook. Stop and report any failure before proceeding.

**Step 1 — TypeScript check (must be 0 errors):**
```bash
cd /Volumes/MontereyT7/FLUXION
npm run type-check 2>&1 | tail -10
```

**Step 2 — MacBook Python smoke tests for new code (Python 3.13 on MacBook, Python 3.9 on iMac — code must be compatible with both):**
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_guardrails.py tests/test_vertical_entity_extractor.py -v --tb=short 2>&1 | tail -20
```

Both test files must show 0 FAILED, 0 ERROR.

**Step 3 — Full test suite on MacBook (skip iMac-only tests):**
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10
```

Must show: existing 1160 PASS + new guardrail/entity tests PASS, 0 FAIL.

**Step 4 — Atomic commit:**
```bash
cd /Volumes/MontereyT7/FLUXION
git add voice-agent/src/italian_regex.py \
        voice-agent/src/entity_extractor.py \
        voice-agent/src/orchestrator.py \
        voice-agent/tests/test_guardrails.py \
        voice-agent/tests/test_vertical_entity_extractor.py
git commit -m "feat(voice-agent): F02 vertical guardrails + entity extractor

- Add VERTICAL_GUARDRAILS + check_vertical_guardrail() to italian_regex.py
  (4 verticals, multi-word patterns only, pre-compiled, <2ms runtime)
- Fix orchestrator: BookingStateMachine now receives services_config from
  VERTICAL_SERVICES[verticale_id] at init and in set_vertical()
- Inject guardrail check at L0-pre in orchestrator.process()
- Wire extract_vertical_entities() in process() after guardrail pass,
  results stored in booking_sm.context.extra_entities
- Add extract_vertical_entities() to entity_extractor.py:
  medical (specialty/urgency/visit_type), auto (plate/brand)
- Add test_guardrails.py (28+ tests) and test_vertical_entity_extractor.py (23+ tests)
- AC-1: guardrails block out-of-scope for 4 verticals
- AC-2: vertical service extraction wired correctly
- AC-3: medical specialty/urgency/visit_type extracted and available in FSM context
- AC-4: auto plate/brand extracted and available in FSM context
- AC-5: full test suite stays green"
```

Record the commit hash for ROADMAP_REMAINING.md update.

**Step 5 — Push to master:**
```bash
git push origin master
```
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION
git log --oneline -3
```
Must show the F02 commit as the most recent commit.

Confirm push succeeded:
```bash
git log origin/master --oneline -1
```
Must show the same F02 commit hash as local HEAD.
  </verify>
  <done>
TypeScript type-check: 0 errors.
MacBook pytest: new tests pass (0 FAIL).
Full test suite: 1160+ PASS, 0 FAIL.
Git commit exists with message starting "feat(voice-agent): F02 vertical guardrails".
Commit pushed to origin master (local HEAD matches origin/master).
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
F02 implementation:
- Guardrails: out-of-scope query blocking in italian_regex.py
- FSM services_config fix in orchestrator.py
- Vertical entity extractor (medical + auto) in entity_extractor.py, wired into orchestrator.process()
- New tests: test_guardrails.py + test_vertical_entity_extractor.py
Committed and pushed to master.
  </what-built>
  <how-to-verify>
**Step A — Sync iMac and run full test suite:**
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m pytest tests/ -v --tb=short -q 2>&1 | tail -15"
```
Expected: 1160+ PASS (including new guardrail + entity tests), 0 FAIL.

**Step B — Restart voice pipeline on iMac:**
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
for i in 1 2 3; do curl -s http://192.168.1.12:3002/health && break || sleep 3; done
```
Expected: `{"status": "ok", ...}` — HTTP 200.

**Step C — Smoke test guardrail via voice pipeline:**
```bash
curl -s -X POST http://192.168.1.12:3002/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "voglio cambiare le gomme invernali", "vertical": "salone"}' | python3 -m json.tool
```
Expected response should contain a redirect message about salone/capelli (NOT a booking flow for tires).

Note: If the `vertical` param is not accepted at the HTTP level, that is acceptable for this sprint — the orchestrator internal routing fix (services_config) is what matters. Focus on test suite results.
  </how-to-verify>
  <resume-signal>Type "approved" if iMac tests pass and pipeline is live, or describe any failures.</resume-signal>
</task>

<task type="auto">
  <name>Task 3: Update ROADMAP_REMAINING.md F02 status to done</name>
  <files>ROADMAP_REMAINING.md</files>
  <action>
Read `ROADMAP_REMAINING.md` then update the F02 row in the BLOCKERS table.

Find:
```
| **F02** | Vertical system Sara (guardrails + entity extractor) | 3h | 🔄 NEXT |
```

Replace with:
```
| **F02** | Vertical system Sara (guardrails + entity extractor) | 3h | ✅ {COMMIT_HASH} |
```

Where `{COMMIT_HASH}` is the short hash from the F02 commit (first 7 chars from `git log --oneline -1`).

Then commit:
```bash
git add ROADMAP_REMAINING.md
git commit -m "chore(roadmap): F02 done ✅ → F03 Latency optimizer NEXT"
git push origin master
```

Also update HANDOFF.md and MEMORY.md to reflect F02 complete and F03 as next phase. In HANDOFF.md, update the current phase field. In MEMORY.md, update the "PROSSIMO" line and add F02 to the completed task queue table.
  </action>
  <verify>
```bash
grep "F02" /Volumes/MontereyT7/FLUXION/ROADMAP_REMAINING.md
```
Must show `✅` for F02 row.

```bash
grep "F03" /Volumes/MontereyT7/FLUXION/ROADMAP_REMAINING.md | head -3
```
F03 should still show `⏳` (it is now the next phase).
  </verify>
  <done>
ROADMAP_REMAINING.md: F02 row shows `✅ {commit_hash}`.
HANDOFF.md: updated to reflect F03 as next phase.
MEMORY.md: F02 added to completed tasks, PROSSIMO updated to F03.
Commit pushed to origin master.
  </done>
</task>

</tasks>

<verification>
F02 is complete when ALL of the following are true:

1. `git log --oneline -3` shows the F02 feat commit and roadmap chore commit
2. `ssh imac "... pytest tests/ -q 2>&1 | tail -5"` shows 1160+ PASS, 0 FAIL
3. `curl http://192.168.1.12:3002/health` returns `{"status": "ok", ...}`
4. `grep "✅" ROADMAP_REMAINING.md | grep F02` returns the F02 row
5. `grep "VERTICAL_GUARDRAILS" voice-agent/src/italian_regex.py` returns a match
6. `grep "services_config=VERTICAL_SERVICES" voice-agent/src/orchestrator.py` returns a match
7. `grep "extract_vertical_entities" voice-agent/src/entity_extractor.py` returns a match
8. `grep "extract_vertical_entities(user_input" voice-agent/src/orchestrator.py` returns a match
</verification>

<success_criteria>
- All acceptance criteria met:
  - AC-1: `check_vertical_guardrail()` blocks out-of-scope queries for salone, palestra, medical, auto
  - AC-2: `BookingStateMachine` uses `VERTICAL_SERVICES[verticale_id]` for service extraction
  - AC-3: Medical entities (specialty, urgency, visit_type) extracted by `extract_vertical_entities()` and stored in FSM context
  - AC-4: Auto entities (vehicle_plate, vehicle_brand) extracted by `extract_vertical_entities()` and stored in FSM context
  - AC-5: Full test suite 1160+ PASS, 0 FAIL on iMac (Python 3.9)
- F02 marked done in ROADMAP_REMAINING.md
- Voice pipeline live on iMac at http://192.168.1.12:3002
- Atomic commit pushed to master
</success_criteria>

<output>
After completion, create `.planning/phases/f02-vertical-system-sara/f02-03-SUMMARY.md`
</output>
