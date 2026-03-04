# Project State

## Current Position

- Phase: f02-vertical-system-sara
- Last completed plan: f02-01
- Status: Plan 01 complete (Vertical Guardrails), plans 02+03 pending
- Last activity: 2026-03-04 — Completed f02-01-PLAN.md

Progress: [████████░░░] Plan 01 of 3 complete in current phase (33%)

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

## Blockers / Concerns

- sdi-aruba Wave 3 still pending — cargo check requires iMac SSH (plan 04)
- f02-02 (entity extractor) and f02-03 (orchestrator integration) pending
- Voice pipeline restart required on iMac after any Python changes to voice-agent/

## Session Continuity

Last session: 2026-03-04T14:06:36Z
Stopped at: Completed f02-01-PLAN.md
Resume file: None
Next plan: .planning/phases/f02-vertical-system-sara/f02-02-PLAN.md (entity extractor vertical-aware)
