---
phase: sdi-aruba-multi-provider
plan: "03"
subsystem: fatturazione-sdi
tags: [typescript, react, ui, impostazioni, sdi, multi-provider]

dependency-graph:
  requires: [sdi-aruba-01, sdi-aruba-02]
  provides: [SdiProviderSettings UI, ImpostazioniFatturazione TS types with sdi_provider fields, Impostazioni.tsx integration]
  affects: [sdi-aruba-04]

tech-stack:
  added: []
  patterns: [provider-selector-card-ui, dynamic-api-key-input, ErrorBoundary-wrapped-section]

key-files:
  created:
    - src/components/impostazioni/SdiProviderSettings.tsx
  modified:
    - src/types/fatture.ts
    - src/hooks/use-fatture.ts
    - src/pages/Impostazioni.tsx

decisions:
  - "sdi_provider, aruba_api_key, openapi_api_key fields added to ImpostazioniFatturazioneSchema Zod (z.string().default/nullable)"
  - "useUpdateImpostazioniFatturazione explicit field mapping — all 24 fields enumerated instead of spread to Tauri invoke"
  - "SdiProviderSettings uses 3 separate useState values for each key (not a single object) for controlled inputs"
  - "Provider cards styled with cyan active border, provider-specific cost label colors (green/blue/slate)"
  - "SdiProviderSettings integrated before FLUXION IA section, wrapped in ErrorBoundary"

metrics:
  duration: "2m 50s"
  completed: "2026-03-03"
---

# Phase sdi-aruba-multi-provider Plan 03: TypeScript UI SdiProviderSettings Summary

**One-liner:** 3-provider SDI selector UI with dynamic API key inputs integrated into Impostazioni via ErrorBoundary, type-check 0 errors.

**Status:** complete
**Date:** 2026-03-03

## What Was Built

- `src/types/fatture.ts`: Added `sdi_provider: z.string().default('fattura24')`, `aruba_api_key: z.string().nullable()`, `openapi_api_key: z.string().nullable()` to `ImpostazioniFatturazioneSchema` — these fields were already committed by Plan 02 (parallel wave), verified present
- `src/hooks/use-fatture.ts`: `useUpdateImpostazioniFatturazione` now maps all 24 fields explicitly (not spread) with the 3 new provider fields — committed by Plan 02, verified
- `src/components/impostazioni/SdiProviderSettings.tsx`: New component — 3 provider card selector (Aruba/OpenAPI.com/Fattura24) with active state highlight, cost badges in provider-specific colors, description text, dynamic API key Input per provider, doc link per provider, save with toast feedback
- `src/pages/Impostazioni.tsx`: Added import for SdiProviderSettings, renders it in ErrorBoundary before the FLUXION IA section

## Deliverables

| File | Status |
|------|--------|
| `src/components/impostazioni/SdiProviderSettings.tsx` | Created (237 lines) |
| `src/pages/Impostazioni.tsx` | Modified (+5 lines: import + ErrorBoundary render) |
| `src/types/fatture.ts` | Already updated (Plan 02 b230ab9) |
| `src/hooks/use-fatture.ts` | Already updated (Plan 02 b230ab9) |

## Commits

| Hash | Message |
|------|---------|
| b230ab9 | feat(sdi-aruba-02): update_impostazioni_fatturazione — sdi_provider + aruba_api_key + openapi_api_key (Plan 02 parallel, covers Task 1 TS changes) |
| 4e4e28f | feat(sdi-aruba-03): SdiProviderSettings UI + Impostazioni integration + type-check 0 errors |

## Verification

- `npm run type-check`: 0 errors
- ESLint: 0 warnings (pre-commit hook passed)
- Pre-commit checks: PASSED

## Deviations from Plan

### Auto-resolved: Plan 02 already committed Task 1 changes

Task 1 (TypeScript types + hook update) was already committed by Plan 02 (commit b230ab9, run in parallel Wave 2). The exact fields `sdi_provider`, `aruba_api_key`, `openapi_api_key` were added to both `fatture.ts` and `use-fatture.ts` with explicit field mapping. No duplicate commit was created.

No other deviations — plan executed as written.

## Next Phase Readiness

- Plan 04 (verify + type-check + iMac cargo check) can proceed
- SdiProviderSettings is rendering-ready pending Rust backend (Plan 02/04 cargo check on iMac)
- TypeScript types match the Rust struct fields from Plan 01
