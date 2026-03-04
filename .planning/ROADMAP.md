
### Phase F02: f02-vertical-system-sara
**Goal:** Make Sara vertical-aware: guardrails block out-of-scope queries per vertical (L0-pre regex), and service extraction uses the correct vertical's synonym table via services_config fix in orchestrator.
**Status:** ✅ COMPLETE (2026-03-04) — 1197 PASS / 0 FAIL
**Plans:** 3 plans in 2 waves

Plans:
- [x] f02-01-PLAN.md — Guardrails (VERTICAL_GUARDRAILS + check_vertical_guardrail) + test_guardrails.py
- [x] f02-02-PLAN.md — FSM services_config fix + guardrail injection in orchestrator + extract_vertical_entities() + tests
- [x] f02-03-PLAN.md — Full test suite verify + iMac sync + restart pipeline + atomic commit + roadmap update

---

### Phase F02.1: f02.1-nlu-hardening
**Goal:** Fix 7 P0 NLU bugs in Sara: negation guard, WAIT detection, AM/PM time heuristic, STT-truncated day names, extra_entities FSM wiring, verb-form guardrail patterns, SPOSTAMENTO intent hardening.
**Status:** ✅ COMPLETE (2026-03-04) — 1259 PASS / 0 FAIL
**Research:** Complete — `.claude/cache/agents/f02-nlu-ambiguity-research.md`, `f02-nlu-comprehensive-patterns.md`, `r3-italian-nlu-edge-cases.md`
**Plans:** 4 plans in 3 waves

Plans:
- [x] f02.1-01-PLAN.md — Bugs 2,3,4,7: SPOSTAMENTO + no aspetti + AM/PM + STT days + tests
- [x] f02.1-02-PLAN.md — Bug 6: verb-form guardrail patterns (salone/palestra/medical) + tests
- [x] f02.1-03-PLAN.md — Bugs 1,5: negation guard + extra_entities FSM wiring + tests
- [x] f02.1-04-PLAN.md — iMac pytest verify + pipeline restart + human verify + ROADMAP update

---

## Sprint 2026-02-27 — Aggiunte CTO

### Phase: SDI Aruba Multi-Provider (in pianificazione)
**Goal:** Sostituire dipendenza unica Fattura24 con architettura multi-provider pluggabile.
Risparmio: da €96-192/anno a €29.90/anno (Aruba). Retrocompat garantita.
**Plans:** 4 plans in 3 waves

Plans:
- [ ] sdi-aruba-01-PLAN.md — Migration 029 SQL + Rust trait SdiProvider + 3 impl
- [ ] sdi-aruba-02-PLAN.md — Cargo.toml deps + update_impostazioni_fatturazione multi-provider
- [ ] sdi-aruba-03-PLAN.md — UI SdiProviderSettings + TypeScript types + hook aggiornato
- [ ] sdi-aruba-04-PLAN.md — type-check + cargo check iMac + human verify + commit atomico

---

### P0 — Revenue (in corso)
- [x] **Video marketing 70s** — `out/marketing_70s.mp4` ✅ 71.4s 1280x720 €297
- [ ] **LemonSqueezy approvazione** — risposta a Kashish in corso
- [x] **Landing deploy** — https://lukeeterna.github.io/fluxion-desktop/ ✅ LIVE (logo + 6 verticali + €297)
- [ ] **Landing upgrade** — foto verticali + quick wins + linguaggio piano + benchmark competitor

### P0.5 — Onboarding Frictionless (BLOCCA VENDITE se non risolto)
- [ ] **Research DeepDive**: dove il codice richiede Groq API key + Gmail app code → soluzione automatizzata
  - Opzione A: Fluxion fornisce la sua Groq key bundled con licenza (utente zero config)
  - Opzione B: Setup wizard in-app che guida l'utente passo-passo con screenshot
  - Research file: `.planning/research/onboarding-frictionless-2026.md` (da creare)
- [ ] **Guida PDF attrattiva e completa** — per utente finale PMI (non tecnico)

### P1 — Post-approvazione LemonSqueezy
- [ ] **Tutorial video ibrido** (10-15min per verticale)
  - Approccio: Intro/Outro Remotion + screencap OBS su iMac
  - Piano completo: `scripts/video-remotion/TUTORIAL_PLAN.md` (705 righe, 82 scene, 6 verticali)
  - Da fare: installare OBS su iMac, registrare screencap per ogni verticale
  - Priorità: Salone → Palestra → Odontoiatria → Fisioterapia → Estetica → Officina
- [ ] **Test live voice agent** — scenari T1 su iMac
- [ ] **Build v0.9.0 → tag** — solo dopo test live

### P2 — Sicurezza & Privacy (da fare dopo video marketing)
- [ ] **ZeroClaw sandbox**: Docker isolato o macOS Sandbox profile — vedi `.planning/research/security-anonymity-2026.md`
- [ ] **Anonimato operativo**: VPN no-log + DNS-over-HTTPS + browser hardening (ricerca in corso)
- [ ] **Voice agent 0.0.0.0 → 127.0.0.1**: bind locale se Bridge non è su rete pubblica

### P3 — Anti-Context-Rot (workflow permanente)
- [ ] Hook pre-task: auto-write HANDOFF ogni N tool calls
- [ ] /compact obbligatorio a 40% context
- [ ] Commit frequenti come checkpoint (ogni feature = commit)
