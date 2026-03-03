# Project State

## Current Position

- Phase: sdi-aruba-multi-provider
- Last completed plan: sdi-aruba-01
- Status: Wave 1 complete, Wave 2 pending
- Last activity: 2026-03-03 — Completed sdi-aruba-01-PLAN.md

Progress: [██░░] 1/4 plans complete (25%)

## Accumulated Decisions

| Decision | Made In | Details |
|----------|---------|---------|
| Rust build only on iMac | Global | MacBook cannot run cargo — no cargo check/build here |
| Migration 029 DEFAULT 'fattura24' | sdi-aruba-01 | Retrocompat — existing users keep Fattura24 without config change |
| COALESCE in sdi_provider_factory | sdi-aruba-01 | Null safety — handles rows where sdi_provider may be NULL |
| Fattura24Response before trait | sdi-aruba-01 | Dependency ordering — struct used by Fattura24Provider impl |
| All deps pre-existing | sdi-aruba-01 | async-trait, base64, reqwest, serde_json already in Cargo.toml |

## Blockers / Concerns

- cargo check pending — iMac required for Wave 3 (plan 04) and any build verification
- ArubaProvider endpoint URL (`ews.aruba.it/...`) to be confirmed against official Aruba FE API docs in plan 02
- OpenApiProvider endpoint URL (`api.openapi.com/efatt/v1/send`) to be confirmed in plan 02

## Session Continuity

Last session: 2026-03-03T19:15:00Z
Stopped at: Completed sdi-aruba-01-PLAN.md
Resume file: None
Next plan: .planning/phases/sdi-aruba-multi-provider/02-rust-providers-PLAN.md
