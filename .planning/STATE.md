# Project State

## Current Position

- Phase: f02.1-nlu-hardening (IN PROGRESS)
- Last completed plan: f02.1-01
- Status: Plan 01 of 4 complete — Bugs 7,2,3,4 fixed
- Last activity: 2026-03-04 — Completed f02.1-01-PLAN.md (NLU hardening wave 1)

Progress: [░░░░] Plan 01 of 4 complete in f02.1 phase (25%)

## Accumulated Decisions

| Decision | Made In | Details |
|----------|---------|---------|
| Rust build only on iMac | Global | MacBook cannot run cargo — no cargo check/build here |
| Migration 029 DEFAULT 'fattura24' | sdi-aruba-01 | Retrocompat — existing users keep Fattura24 without config change |
| COALESCE in sdi_provider_factory | sdi-aruba-01 | Null safety — handles rows where sdi_provider may be NULL |
| Fattura24Response before trait | sdi-aruba-01 | Dependency ordering — struct used by Fattura24Provider impl |
| All deps pre-existing | sdi-aruba-01 | async-trait, base64, reqwest, serde_json already in Cargo.toml — confirmed in plan 02 |
| COALESCE in update_impostazioni_fatturazione | sdi-aruba-02 | sdi_provider uses COALESCE(?, sdi_provider) — null input preserves existing value |
| Zod schema must match Rust struct | sdi-aruba-02 | ImpostazioniFatturazioneSchema fields mirror DB columns including 3 new SDI fields |
| SdiProviderSettings before FLUXION IA section | sdi-aruba-03 | Logical placement — SDI config near other integrations (WhatsApp, SMTP) |
| Explicit field mapping in useUpdateImpostazioniFatturazione | sdi-aruba-03 | All 24 fields enumerated explicitly — Tauri invoke named params, no spread |
| Multi-word-only guardrail patterns | f02-01 | No single-word blocks (e.g. 'ceretta' alone) — use context-word patterns |
| Context-word manicure/pedicure patterns | f02-01 | 'la manicure', 'fare la manicure' etc. to avoid false positives in medical |
| _dataclass_gr alias for GuardrailResult | f02-01 | Avoid collision with existing 'dataclass' import in italian_regex.py |
| HAS_VERTICAL_ENTITIES guard separate from HAS_ITALIAN_REGEX | f02-02 | If entity extractor import fails, guardrail still runs (both optional, independent) |
| entity extraction only if response is None | f02-02 | Follows existing L0 pattern — only runs when guardrail did not block |
| Adjective forms in ginecologia keywords | f02-02 | Real users say 'visita ginecologica' not 'una ginecologia' — adjective forms essential |
| F02 phase complete — 1197 PASS / 0 FAIL | f02-03 | All guardrail + entity extractor + orchestrator wiring verified on iMac |
| F03 next: streaming LLM approach | f02-03 | Groq stream=True + FSM template pre-computation to hit P95 <800ms from ~1330ms |
| cambia/modifica require booking object in SPOSTAMENTO | f02.1-01 | Generic verbs split from domain verbs — modal+cambia also requires booking obj |
| _disambiguate_hour_pm PHASE 5 only | f02.1-01 | PM convention applied only to bare digit hours — PHASE 1 (with minutes) unaffected |
| STT truncations as dict entries in DAYS_IT | f02.1-01 | marted/gioved/venerd/mercoled added alongside canonical forms — no regex needed |

## Blockers / Concerns

- F02.1 plans 02-04 remain (Bugs 5,6,1 + entity vertical-awareness + service synonym disambiguation)
- F03 Latency Optimizer after F02.1 complete (P95 <800ms, attuale ~1330ms)
- iMac sync needed for voice pipeline to pick up NLU fixes

## Session Continuity

Last session: 2026-03-04T16:20:44Z
Stopped at: Completed f02.1-01-PLAN.md (Bugs 7,2,3,4 fixed — 94/94 tests PASS)
Resume file: None
Next plan: .planning/phases/f02.1-nlu-hardening/f02.1-02-PLAN.md
