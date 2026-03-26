---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: Lancio
status: Executing Phase 10
stopped_at: "10-02-PLAN.md — checkpoint:human-verify (5 clips + thumbnail generated, awaiting visual approval)"
last_updated: "2026-03-26T17:21:31Z"
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 6
  completed_plans: 1
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-26)

**Core value:** Italian PMI owners manage their entire business from one beautiful desktop app with voice assistant — paying once, owning forever.
**Current focus:** Phase 10 — video-v6

## Current Position

Phase: 10 (video-v6) — EXECUTING
Plan: 2 of 4 — CHECKPOINT (human-verify pending after clip generation)

## Performance Metrics

**Velocity:**

- Total plans completed (v1.0): 0
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 9. Screenshot | TBD | — | — |
| 10. Video V6 | TBD | — | — |
| 11. Landing | TBD | — | — |
| 12. Sales Agent | TBD | — | — |
| 13. Post-Lancio | TBD | — | — |

*Updated after each plan completion*

## Accumulated Context

### Decisions

- Sprint 1 Product Ready (S113): Prezzi 497/897 Rust OK, phone-home wired, seed dati demo in DB, banner fix
- Screenshot via CGEvent iMac (S113): Python CGEvent (Quartz), screencapture -l, WIN_ID=297 (verificare ogni sessione)
- Ordine sprint sequenziale: Screenshot → Video → Landing → Sales → Post — non negoziabile
- Sales Agent WA: Playwright (not Selenium), Google Places API primary (not PagineGialle), warmup 4 settimane non-bypassabile
- Video V6: PAS formula obbligatoria, apertura scena telefono perso (non dashboard), prezzo competitor "centoventi euro al mese"
- Video V6 Plan 01: scene_20 usa 22-pacchetti.png (Phase 9), storyboard 27 scene confermato, voiceover manifest generato
- Video V6 Plan 02: 5 clip V6- prefix (V6-03/04/05/11/13), negativePrompt aggiornato (+celluloid, +distorted hands), thumbnail da V6-05 frame 4s con Pillow gradient
- Landing: CF Pages sempre `--branch=production`, loss framing above fold, /installa con GIF animate Sequoia 15.1+

### Pending Todos

None yet.

### Blockers / Concerns

- Phase 9: Screenshot Pacchetti + Fedeltà da catturare su iMac (iMac potrebbe essere in sleep — svegliare prima)
- Phase 10: Veo3 prompt wording per scene Pacchetti/Fedeltà non ancora scritti — definire durante planning
- Phase 12: WA Web DOM selectors da verificare prima di scrivere agent.py — WA Web cambia senza preavviso
- Phase 12: Confermare disponibilità SIM dedicata per outreach (non numero personale fondatore)
- Phase 11: Verificare SPF/DKIM Resend su CF DNS per evitare spam su Libero.it/Alice.it

## Session Continuity

Last session: 2026-03-26 (S116)
Stopped at: 10-02 checkpoint — 5 V6 clips + thumbnail generated, awaiting human verify
Resume file: None
Next: After approve checkpoint → `/gsd:execute-phase 10 03` (video composition)
