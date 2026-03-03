# Project State

## Current Position

- Phase: sdi-aruba-multi-provider
- Last completed plan: sdi-aruba-03
- Status: Wave 2 complete (plans 02+03 both done), Wave 3 pending (plan 04)
- Last activity: 2026-03-03 — Completed sdi-aruba-03-PLAN.md

Progress: [██████░░] 3/4 plans complete (75%)

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

## Blockers / Concerns

- cargo check pending — iMac required for plan 04 (Wave 3) build verification
- ArubaProvider endpoint URL (`ews.aruba.it` pattern) — verify vs official Aruba FE API docs in plan 04
- OpenApiProvider endpoint URL — verify vs official docs in plan 04
- Plan 04 must SSH to iMac to run: cargo check, migration test, integration smoke test

## Session Continuity

Last session: 2026-03-03T19:20:59Z
Stopped at: Completed sdi-aruba-03-PLAN.md
Resume file: None
Next plan: .planning/phases/sdi-aruba-multi-provider/04-verify-typecheck-PLAN.md (Wave 3 — requires iMac SSH)
