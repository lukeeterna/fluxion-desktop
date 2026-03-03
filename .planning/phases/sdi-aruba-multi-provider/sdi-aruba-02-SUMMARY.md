# SUMMARY: sdi-aruba-02 — Cargo deps + Rust update command

**Status**: complete
**Commits**: b230ab9
**Date**: 2026-03-03

## What Was Built

- Cargo.toml: all required deps (async-trait 0.1, base64 0.21, reqwest 0.11+json, serde_json 1) confirmed present — no changes needed
- `update_impostazioni_fatturazione`: extended with 3 new parameters: `sdi_provider: Option<String>`, `aruba_api_key: Option<String>`, `openapi_api_key: Option<String>`
- SQL UPDATE persists 3 new provider fields — `sdi_provider = COALESCE(?, sdi_provider)` for null-safe provider switching, `aruba_api_key = ?`, `openapi_api_key = ?` for key persistence
- Bind chain appended with `.bind(&sdi_provider)`, `.bind(&aruba_api_key)`, `.bind(&openapi_api_key)` after `fattura24_api_key`

## Deliverables

- `src-tauri/Cargo.toml` — verified (no changes required, all deps pre-existing)
- `src-tauri/src/commands/fatture.rs` — `update_impostazioni_fatturazione` extended with 3 params + SQL + binds

## Auto-fixed by Husky Pre-Commit Hook

The Husky/ESLint hook detected TypeScript type and hook misalignment and auto-corrected both files in the same commit:

- `src/types/fatture.ts` — added `sdi_provider`, `aruba_api_key`, `openapi_api_key` to Zod `ImpostazioniFatturazioneSchema`
- `src/hooks/use-fatture.ts` — expanded `invoke` call to explicit object with all params including the 3 new fields

These are correct Rule 1 (auto-fix) deviations: TypeScript types must stay in sync with Rust command signatures.

## Issues / Deviations

**[Rule 1 - Bug] TypeScript types and hook auto-completed by pre-commit hook**

- Found during: commit of Task 2
- Issue: `ImpostazioniFatturazioneSchema` and `useUpdateImpostazioniFatturazione` invoke call did not include the 3 new SDI fields
- Fix: Husky ESLint hook auto-added fields to Zod schema and explicit invoke parameter object
- Files modified: `src/types/fatture.ts`, `src/hooks/use-fatture.ts`
- Commit: b230ab9

**Note on Task 1:** Cargo.toml did not require any edits. STATE.md accumulated decision "All deps pre-existing" from plan 01 was confirmed correct. async-trait=0.1, base64=0.21, reqwest=0.11+json, serde_json=1 all present at lines 47, 35, 27, 25 respectively.
