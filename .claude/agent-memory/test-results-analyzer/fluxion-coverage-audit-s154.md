---
name: FLUXION Coverage Audit S154
description: Full coverage audit run 2026-04-14 — key findings on TS/Rust/Python test gaps, IPC command coverage, B2/B3 regression coverage status
type: project
---

S154 audit of FLUXION test suite.

**Why:** First structured coverage audit, requested pre-GA to baseline test health.

**How to apply:** Use findings to prioritize test debt. Always check these gaps before marking a task "done".

Key findings:

- TypeScript/React: ZERO test files. 11 pages untested. Vitest not configured.
- Rust: 36 #[test] annotations in 7 files. 28 of 30 command files have zero tests. Domain model (appuntamento FSM, audit) is tested; IPC commands that call it are not.
- Python: 79 test files, ~1857 test functions. Strong unit coverage on voice logic. E2E suite (8 files) requires live iMac — cannot run in CI.
- IPC total: 263 #[tauri::command] across 30 files. Financial commands (cassa, fatture, loyalty) have zero tests.

B2 (gommista "cambio" fix, commit b8b30cf): No dedicated regression test exists. Closest tests in test_guardrails.py cover cambio_olio and cambio_gomme for auto vertical but not the salone-blocks-cambio-gomme case.

B3 (F1-3b adaptive silence VAD wiring, commit a923b84): test_phase_f_eou.py covers adaptive_silence module with 79 tests but FluxionVAD.update_silence_ms() is untested.

Stress test (test_sara_stress_per_verticale.py): Last known result S151 = 87 OK / 80 WARN / 6 FAIL. Results never persisted to file. Post-S152 fix likely resolves 3 of 6 FAIL scenarios.

Top action items:
- A1: Add salone blocks cambio_gomme regression test to test_guardrails.py
- A2: Add update_silence_ms() unit test to test_phase_f_eou.py
- A3/A4: Rust tests for cassa.rs (registra_incasso) and fatture.rs (emetti_fattura state guard)
- A5: Add --save-results flag to stress test for baseline persistence
- A6: Add vitest to frontend for critical IPC call paths
