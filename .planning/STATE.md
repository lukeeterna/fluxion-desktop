# Project State

## Current Position

- Phase: sdi-aruba-multi-provider
- Last completed plan: sdi-aruba-02
- Status: Wave 2 (plans 02+03 parallel) — plan 02 complete, plan 03 pending
- Last activity: 2026-03-03 — Completed sdi-aruba-02-PLAN.md

Progress: [████░░░░] 2/4 plans complete (50%)

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

## Blockers / Concerns

- cargo check pending — iMac required for plan 04 (Wave 3) build verification
- ArubaProvider endpoint URL confirmed as `ews.aruba.it` pattern — to be verified vs official docs
- OpenApiProvider endpoint URL — to be verified vs official docs
- Endpoint URLs noted in plan 02 blockers are addressed by plan 03 (UI) not by plan 02 (Rust commands)

## Session Continuity

Last session: 2026-03-03T19:18:00Z
Stopped at: Completed sdi-aruba-02-PLAN.md
Resume file: None
Next plan: .planning/phases/sdi-aruba-multi-provider/03-ui-impostazioni-PLAN.md (Wave 2, parallel to completed plan 02)
