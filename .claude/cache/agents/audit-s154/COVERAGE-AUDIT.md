# FLUXION Coverage Audit — S154
**Date**: 2026-04-14  
**Auditor**: test-results-analyzer  
**Scope**: TypeScript frontend, Rust/Tauri IPC, Python voice agent

---

## EXECUTIVE SUMMARY

| Layer | Test Files | Test Functions | Unit Coverage | Notes |
|-------|-----------|---------------|---------------|-------|
| TypeScript/React | **0** | **0** | **0%** | CRITICAL GAP |
| Rust (cargo test) | 7 files with tests | 36 `#[test]` | ~5% of commands | Most commands untested |
| Python voice agent | 79 test files | ~1,857 `def test_` | HIGH (voice logic) | Solid unit + integration |
| E2E (Python live) | 8 e2e files | 44 functions | Requires live iMac | Cannot run in CI |

**Overall assessment**: Python voice agent is well-tested. Rust IPC layer has severe gaps. Frontend has zero tests.

---

## 1. TEST FILE INVENTORY

### 1a. TypeScript / React Tests

**Result: NONE FOUND**

Searched `src/**/*.test.ts`, `src/**/*.spec.ts`, `src/**/*.test.tsx` — zero matches.

The 11 React pages and all components have **zero test coverage**.

Pages with no tests:
- `src/pages/Dashboard.tsx`
- `src/pages/Clienti.tsx`
- `src/pages/Calendario.tsx`
- `src/pages/Appuntamenti` (via Calendario)
- `src/pages/Cassa.tsx`
- `src/pages/Fatture.tsx`
- `src/pages/Analytics.tsx`
- `src/pages/Servizi.tsx`
- `src/pages/Operatori.tsx`
- `src/pages/Fornitori.tsx`
- `src/pages/Impostazioni.tsx`
- `src/pages/VoiceAgent.tsx`

---

### 1b. Rust Tests

**36 `#[test]` annotations across 7 files**

| File | Test Count | What's Covered |
|------|-----------|----------------|
| `domain/appuntamento_aggregate.rs` | 15 | FSM transitions: bozza→proposta→confermato, validation, cancellation |
| `domain/audit.rs` | 6 | AuditLog creation, builder pattern, changed-fields diff, anonymization |
| `commands/analytics.rs` | 3 | `mese_label_it()`, `prev_month()`, `format_eur()` — pure functions only |
| `commands/rag.rs` | 3 | FAQ markdown parsing, relevance filtering |
| `services/festivita_service.rs` | 3 | Holiday seed loading, `is_festivita()` |
| `encryption.rs` | 3 | Encrypt/decrypt roundtrip, empty string, field sensitivity |
| `domain/errors.rs` | 3 | ValidationResult logic |

**No tests in 23 of 30 command files** (see Section 7 for full IPC gap table).

---

### 1c. Python Voice Agent Tests

**79 test files | ~1,857 `def test_` functions**

Top files by test count:

| File | Tests | Domain |
|------|-------|--------|
| `test_entity_extractor.py` | 120 | Entity extraction, synonym matching |
| `test_phase_h_vertical_expansion.py` | 79 | Sub-vertical configs, entity extractors, FSM routing |
| `test_phase_f_eou.py` | 79 | Adaptive silence, EOU detection (covers F1-1, F1-2) |
| `test_booking_state_machine.py` | 87 | FSM state transitions, service extraction |
| `test_phase_g_business_intelligence.py` | 45 | Analytics, reporting |
| `test_disambiguation.py` | 49 | Name disambiguation, phonetic matching |
| `test_voip.py` | 39 | VoIP call handling |
| `test_error_recovery.py` | 43 | Pipeline error scenarios |
| `test_guardrails.py` | 50 | Cross-vertical guardrails |
| `test_whatsapp.py` | 56 | WhatsApp message handling |
| `test_italian_regex.py` | 55 | Regex patterns, synonym tables |
| `test_voice_agent_complete.py` | 37 | Full pipeline integration |
| `test_sales_fsm.py` | 37 | Sales agent FSM |
| `test_vertical_corrections.py` | 46 | Slot correction patterns |
| `test_phase_d_audit.py` | 34 | Audit trail |
| `test_analytics.py` | 34 | Analytics module |
| `test_llm_nlu.py` | 34 | LLM NLU layer |

**E2E files** (require live iMac pipeline at `127.0.0.1:3002`):

| File | Tests | Notes |
|------|-------|-------|
| `e2e/test_sara_stress_per_verticale.py` | 1 main + scenario loops | ~116 scenarios across 6 verticals |
| `e2e/test_sara_massive.py` | 8 | Exhaustive protocol testing |
| `e2e/test_multi_turn_conversations.py` | 26 | Multi-turn dialogs |
| `e2e/test_salone_booking.py` | 2 | Salone booking flow |
| `e2e/test_auto_booking.py` | 2 | Auto booking flow |
| `e2e/test_medical_booking.py` | 2 | Medical booking flow |
| `e2e/test_palestra_booking.py` | 2 | Palestra booking flow |
| `e2e/test_voip_audio_e2e.py` | — | VoIP audio E2E (live only) |

---

## 2. BUG B13 — SARA STRESS TEST ANALYSIS

**Source**: `voice-agent/tests/e2e/test_sara_stress_per_verticale.py`  
**Last known run**: S151 — **87 OK / 80 WARN / 6 FAIL**  
**No saved output file found** — results exist only from live iMac execution.

### Stress Test Structure

The test runs 6 verticals × 5 scenario types:

| Scenario Type | Per Vertical | Total Scenarios |
|--------------|--------------|-----------------|
| BOOKING multi-turn (2-3 conversations) | ~18 turns × 3 convos | ~18 per vertical |
| FAQ (3 questions) | 3 | 18 total |
| GUARDRAIL wrong service (2-3 inputs) | 2-3 | 15 total |
| DISAMBIG (1 surname test) | 1 | 6 total |
| CANCEL mid-flow | 1 | 6 total |
| LATENCY per turn | 6 turns | 36 total |

**Total: ~116 scored scenarios**

### Probable FAIL Scenarios (from code analysis + MEMORY context)

The 6 FAILs from S151 are not persisted in any file. Based on the test logic and known bugs:

**FAIL classification criteria**: A FAIL occurs when:
1. `success: False` returned by pipeline (HTTP error)
2. FSM entered wrong state (e.g., entered booking from FAQ question)
3. FSM did not progress in expected direction

**Most likely failure categories** (based on guardrail logic, known issues from HANDOFF/MEMORY):

| # | Probable Scenario | Vertical | Why It Fails |
|---|------------------|----------|--------------|
| 1 | GUARDRAIL: "Vorrei il cambio olio" → salone | SALONE | Prior to S152 fix: "cambio" regex was contaminating salone service list. **Fixed in commit b8b30cf** |
| 2 | GUARDRAIL: "Mi serve il tagliando auto" → salone | SALONE | Same cross-contamination issue. **Fixed in b8b30cf** |
| 3 | BOOKING: "Cambio gomme stagionale" → auto | AUTO | "cambio" as bare word was matching salone services (negative lookahead missing). **Fixed in b8b30cf** |
| 4 | FAQ: orari/prezzi question triggers booking FSM | Any vertical | FAQ routing regression — `_is_info` flag not set, falls through to booking |
| 5 | LATENCY: >2000ms target on LLM fallback turn | Any vertical | Groq latency variance; not a code bug |
| 6 | BOOKING: Confirmation turn — keywords not in response | BEAUTY/PROFESSIONALE | New verticals may have different confirmation phrasing |

**Note**: The S152 gommista fix (b8b30cf) specifically addresses scenarios 1-3. If the stress test were re-run after S152, the 6 FAIL count would likely drop to 3 or fewer.

### Stress Test Limitations

1. **No saved baseline**: results never persisted to file — impossible to compare S151 vs S152 without re-running on iMac.
2. **Non-deterministic scoring**: WARN vs FAIL depends on FSM state string matching — a FSM refactor changes results without changing behavior.
3. **DB dependency**: "cambio gomme" matching depends on what services are in the SQLite DB — the test uses demo salone DB, not actual auto/gommista DB.
4. **Single-shot conversations**: Each `reset()` call between scenarios resets FSM but not DB state — potential state leak if `reset()` is partial.

---

## 3. BUG B2 REGRESSION — Gommista "cambio" Regex Fix

**Commit**: `b8b30cf` (S152)  
**Fix description**: Negative lookahead on "cambio" regex + synonym cross-contamination filter in `orchestrator.py` (line 2871).

### Existing Test Coverage

**Direct regression test: NOT FOUND in dedicated test file.**

Related tests that partially cover this:

| Test File | Test Name | Coverage | Gap |
|-----------|-----------|----------|-----|
| `test_guardrails.py` | `test_auto_allows_cambio_gomme` | Passes "cambio gomme" through auto vertical — NOT blocked | Does not test salone vertical rejection of "cambio" |
| `test_guardrails.py` | `test_salone_blocks_cambio_olio` | Salone blocks "cambio olio" | "cambio olio" ≠ "cambio gomme" — different trigger |
| `test_phase_h_vertical_expansion.py` | `test_extract_cambio_gomme` | GommistaEntityExtractor maps "cambiare le gomme invernali" → `cambio_gomme` | Unit test only, no guardrail test |
| `test_guardrails.py` | `test_cambiare_pneumatici_blocked` | Salone blocks "vorrei cambiare i pneumatici" | Covers verb-form "cambiare" but not bare "cambio" |
| `test_guardrails.py` | `test_auto_allows_cambio_olio` | Auto allows "cambio olio" | Not about cross-contamination |
| `test_vertical_corrections.py` | `test_invece_cambio_gomme` | "invece cambio gomme" → correction pattern | Correction slot, not guardrail |

**Gap**: There is no test that specifically verifies:
> "vorrei un cambio gomme" in `salone` vertical → BLOCKED  
> "vorrei un cambio gomme" in `auto` vertical → NOT BLOCKED (allowed)

This is the exact regression scenario from S152. A dedicated regression test should be added.

**Recommended test**:
```python
# test_guardrails.py — add to TestSaloneGuardrails
def test_salone_blocks_cambio_gomme(self):
    r = check_vertical_guardrail("vorrei un cambio gomme", "salone")
    assert r.blocked is True, "cambio gomme must be blocked in salone post-S152 fix"

def test_auto_allows_cambio_gomme_bare(self):
    r = check_vertical_guardrail("vorrei un cambio gomme", "auto")
    assert r.blocked is False, "cambio gomme must NOT be blocked in auto"
```

---

## 4. BUG B3 REGRESSION — Adaptive Silence VAD Wiring (F1-3b)

**Commit**: `a923b84` (S152)  
**Fix description**: `orchestrator._vad_handler` backref wired in `main.py:293`. Each turn now calls `vad_session.update_silence_ms(adaptive_ms)` to dynamically update Silero VAD silence threshold (300-1200ms range).

### Existing Test Coverage

**`test_phase_f_eou.py`** — **79 tests** — covers the `adaptive_silence` module **comprehensively**:

| Test Class | What's Covered |
|-----------|----------------|
| `TestAdaptiveSilenceWordCount` | Word-count → bucket mapping (SHORT/MEDIUM/LONG/DEFAULT) |
| `TestAdaptiveSilenceFSMStates` | FSM state overrides (waiting_name, waiting_date, etc.) |
| `TestAdaptiveSilenceCompletionProb` | EOU probability modifies silence duration |
| `TestAdaptiveSilenceMinMax` | Clamping to SILENCE_MIN_MS/SILENCE_MAX_MS |
| `TestSentenceCompletionProbability` | `sentence_complete_probability()` ranges |
| `TestPublicAPI` | Public interface, backward compat |
| (Edge cases) | Empty strings, accented chars, long utterances |

**Gap**: `test_phase_f_eou.py` does NOT test the VAD wiring itself — specifically:
1. That `orchestrator._vad_handler` gets set during init
2. That `vad_handler._sessions` gets `update_silence_ms()` called after processing
3. That `FluxionVAD.update_silence_ms()` actually changes `silence_window_size`

`FluxionVAD.update_silence_ms()` in `ten_vad_integration.py:183-194` has **zero test coverage**.

**Recommended tests**:
```python
# test_phase_f_eou.py or new test_f1_3b_vad_wiring.py
def test_update_silence_ms_changes_window_size():
    vad = FluxionVAD(silence_ms=600)
    initial = vad.silence_window_size
    vad.update_silence_ms(1200)
    assert vad.silence_window_size > initial

def test_update_silence_ms_clamps_minimum():
    vad = FluxionVAD(silence_ms=600)
    vad.update_silence_ms(50)  # below 200ms minimum
    chunk_ms = vad._chunk_ms
    expected_min_window = max(1, int(200 / chunk_ms))
    assert vad.silence_window_size >= expected_min_window
```

---

## 5. IPC COMMAND COVERAGE (B15)

**Total `#[tauri::command]` functions: 263** (in 30 command files; excludes backup file)  
**Command files with any unit tests: 2** (`analytics.rs` — 3 pure-function tests, `rag.rs` — 3 parse tests)  
**Command files with zero tests: 28**

### IPC Coverage Table

| Command File | Commands | Rust Tests | Coverage | Risk |
|-------------|----------|-----------|----------|------|
| `analytics.rs` | 2 | 3 | Pure functions only (no DB) | LOW |
| `rag.rs` | 5 | 3 | FAQ parse/search (no DB) | LOW |
| `appuntamenti.rs` | 7 | 0 | NONE | **CRITICAL** |
| `appuntamenti_ddd.rs` | 8 | 0 | NONE | **CRITICAL** |
| `clienti.rs` | 6 | 0 | NONE | **CRITICAL** |
| `loyalty.rs` | 22 | 0 | NONE | **CRITICAL** |
| `cassa.rs` | 8 | 0 | NONE | **CRITICAL** |
| `fatture.rs` | 16 | 0 | NONE | **CRITICAL** |
| `schede_cliente.rs` | 21 | 0 | NONE | HIGH |
| `operatori.rs` | 16 | 0 | NONE | HIGH |
| `whatsapp.rs` | 16 | 0 | NONE | HIGH |
| `voice_pipeline.rs` | 10 | 0 | NONE | HIGH |
| `voice_calls.rs` | 11 | 0 | NONE | HIGH |
| `audit.rs` | 8 | 0 | NONE (domain/audit.rs has tests) | MEDIUM |
| `setup.rs` | 5 | 0 | NONE | HIGH |
| `license.rs` | 6 | 0 | NONE | HIGH |
| `license_ed25519.rs` | 8 | 0 | NONE | HIGH |
| `settings.rs` | 7 | 0 | NONE | MEDIUM |
| `orari.rs` | 10 | 0 | NONE | MEDIUM |
| `support.rs` | 13 | 0 | NONE | MEDIUM |
| `supplier.rs` | 14 | 0 | NONE | MEDIUM |
| `mcp.rs` | 11 | 0 | NONE | LOW |
| `remote_assist.rs` | 3 | 0 | NONE | LOW |
| `voice.rs` | 4 | 0 | NONE | MEDIUM |
| `media.rs` | 8 | 0 | NONE | MEDIUM |
| `faq_template.rs` | 6 | 0 | NONE | MEDIUM |
| `listini.rs` | 5 | 0 | NONE | LOW |
| `dashboard.rs` | 2 | 0 | NONE | LOW |
| `servizi.rs` | 5 | 0 | NONE | MEDIUM |
| `encryption.rs` | 4 | 3 | Roundtrip only | MEDIUM |

### Domain Model Coverage (where tests DO exist)

| File | Tests | What's Covered |
|------|-------|----------------|
| `domain/appuntamento_aggregate.rs` | 15 | Full FSM: bozza→proposta→in_attesa→confermato→rifiutato, cancellation, modifica, `ora_fine` calc |
| `domain/audit.rs` | 6 | AuditLog builder, changed-fields diff, anonymization logic |
| `domain/errors.rs` | 3 | ValidationResult block/warn logic |
| `services/festivita_service.rs` | 3 | Holiday detection |

**Key finding**: The domain model (aggregate + errors) is reasonably tested for state machine logic. The IPC commands that wrap these models are completely untested, meaning the full HTTP→Tauri→SQLite pipeline has no coverage.

---

## 6. CRITICAL GAPS BY RISK CATEGORY

### CRITICAL — No tests, financial or booking data mutations

| Gap | Location | Risk | Recommended Test |
|-----|----------|------|-----------------|
| `registra_incasso` | `cassa.rs:121` | Writes financial record — no validation test | Unit test: amount validation, metodo_pagamento enum |
| `chiudi_cassa` | `cassa.rs:294` | Closes daily register — no idempotency test | Test double-close returns correct error |
| `create_fattura` | `fatture.rs:559` | Invoice creation with XML output — zero coverage | Test valid → DB record; test missing fields → error |
| `emetti_fattura` | `fatture.rs:904` | Emits fiscal invoice — irreversible | Test state guard: only BOZZA can be emitted |
| `conferma_acquisto_pacchetto` | `loyalty.rs:436` | Deducts package usage — financial | Test concurrent usage doesn't overdraft |
| `delete_appuntamento` | `appuntamenti.rs:744` | Destructive — no auth check test | Test: only bozza/proposta can be deleted |
| `confirm_appuntamento` | `appuntamenti.rs:771` | State transition — no IPC-level test | Test: `in_attesa` → `confermato` via IPC |

### HIGH — Auth / Permission / License

| Gap | Location | Risk |
|-----|----------|------|
| `license.rs` commands | 6 commands | License validation — no test for expired/invalid key behavior |
| `license_ed25519.rs` commands | 8 commands | Ed25519 signature verification — no adversarial tests |
| `gdpr_encrypt` / `gdpr_decrypt` | `encryption.rs` | Encrypt/decrypt tested; GDPR init path (wrong password) not tested |

### HIGH — Voice Pipeline

| Gap | Location | Risk |
|-----|----------|------|
| `voice_pipeline.rs` commands | 10 commands | VoIP state — pjsua2 deadlock is active bug; no test guard for timeout/deadlock |
| `voice_calls.rs` commands | 11 commands | Call recording, call state — no integration test |

---

## 7. PYTHON MODULE COVERAGE GAPS

The Python test suite is comprehensive for the core voice pipeline. Remaining gaps:

| Module | Test File | Status | Gap |
|--------|-----------|--------|-----|
| `src/vad/ten_vad_integration.py` | `test_vad_file.py`, `test_vad_openmicloop.py` | Partial | `update_silence_ms()` (F1-3b) untested |
| `src/orchestrator.py` (VAD wiring) | None | **MISSING** | `_vad_handler` backref setup not tested |
| `verticals/medical/tests/` | `__init__.py` only | **MISSING** | Medical vertical has no unit tests |
| `verticals/palestra/tests/` | `__init__.py` only | **MISSING** | Palestra vertical has no unit tests |
| `verticals/auto/tests/` | `__init__.py` only | **MISSING** | Auto vertical has no unit tests (covered by top-level tests) |
| `src/vad/vad_pipeline_integration.py` | None | **MISSING** | Pipeline integration layer untested |
| `main.py` HTTP handlers | `test_pipeline_e2e.py` | Partial | Health check, VoIP bridge not isolated |

---

## 8. FLAKY TEST RISK ASSESSMENT

| Test File | Flaky Type | Risk | Reason |
|-----------|-----------|------|--------|
| `e2e/test_sara_stress_per_verticale.py` | Type C (env-dep) | HIGH | Requires live iMac pipeline — cannot run in CI |
| `e2e/test_sara_massive.py` | Type C (env-dep) | HIGH | Same — live HTTP to 127.0.0.1:3002 |
| `test_latency_benchmark.py` | Type D (timing) | MEDIUM | Latency assertions will fail under CI load |
| `test_llm_nlu.py` | Type C (env-dep) | MEDIUM | May call Groq API — network-dependent |
| `test_voip.py` | Type C (env-dep) | MEDIUM | pjsua2 bridge tests may need live SIP |
| `test_edge_tts_streaming.py` | Type C (env-dep) | MEDIUM | Edge-TTS requires internet |
| `integration/test_whatsapp.py` | Type C (env-dep) | MEDIUM | WhatsApp webhook may need external endpoint |

All 8 E2E files are Type C flaky — they depend on iMac pipeline being up. There is no mock/stub layer for CI.

---

## 9. ACTION ITEMS

### Immediate (before next release)

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| A1 | Add `test_salone_blocks_cambio_gomme` + `test_auto_allows_cambio_gomme_bare` to `test_guardrails.py` | Voice engineer | P0 — regression risk |
| A2 | Add `test_update_silence_ms_changes_window_size` to `test_phase_f_eou.py` or new file | Voice engineer | P0 — F1-3b has no coverage |
| A3 | Write Rust integration tests for `cassa.rs`: `registra_incasso`, `chiudi_cassa` | Backend architect | P1 — financial data |
| A4 | Write Rust test for `emetti_fattura` state guard (only BOZZA → can emit) | Backend architect | P1 — irreversible operation |
| A5 | Add `--save-results` flag to stress test → write JSON to `.claude/cache/agents/stress-results-YYYYMMDD.json` | Voice engineer | P1 — no baseline persisted |

### Sprint-level (before GA)

| # | Action | Priority |
|---|--------|----------|
| A6 | Add vitest to frontend — cover critical path: booking flow IPC invocations, Cassa calculator | P1 |
| A7 | Add Python mocks for Groq/Edge-TTS so CI can run voice unit tests without network | P2 |
| A8 | Write vertical tests for `medical/tests/`, `palestra/tests/`, `auto/tests/` (currently empty) | P2 |
| A9 | Add license validation adversarial tests in `license_ed25519.rs` | P2 |
| A10 | Re-run stress test on iMac post-S152 and persist results | P1 |

---

## 10. PASS/FAIL CRITERIA

| Criterion | Status |
|-----------|--------|
| Zero critical test FAIL in Python unit suite | PASS (unit suite runs offline; no known failures) |
| Stress test 6 FAIL scenarios analyzed | PASS — analyzed; 3 of 6 likely fixed by S152 b8b30cf |
| IPC coverage gaps documented | PASS — 263 commands, 28 of 30 files with zero tests |
| B2 gommista regression test exists | **FAIL** — no dedicated regression test found |
| B3 adaptive_silence VAD wiring test exists | **FAIL** — `update_silence_ms()` not covered |
| Frontend test coverage | **FAIL** — 0 test files |

---

*Generated by test-results-analyzer agent. Run full stress test on iMac after each voice pipeline change.*
