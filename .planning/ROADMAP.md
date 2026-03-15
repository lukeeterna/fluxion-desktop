
### Phase F-SARA-NLU-PATTERNS: f-sara-nlu-patterns
**Goal:** Complete enterprise-grade rewrite of Sara's NLU layer across all 6 macro-verticals × 17 sub-verticals. Replace partial guardrail patterns and entity tables with comprehensive Italian terminology coverage: technical jargon, regional variants, colloquialisms, synonyms, service durations, operator roles — using Claude's encyclopedic knowledge. Output: `italian_regex.py` patterns + entity extractor tables + pytest coverage ≥95% for all verticals.
**Status:** ⏳ PLANNED (2026-03-15)
**Priority:** P0 — enterprise differentiator, directly impacts booking accuracy for every vertical
**Plans:** TBD

---

### Phase audioworklet: audioworklet-vad-fix
**Goal:** Replace ScriptProcessorNode (deprecated, throttled in WKWebView) with AudioWorkletNode (W3C 2019+ standard, dedicated worker thread) for the open-mic VAD pipeline in use-voice-pipeline.ts. Enables phone button open-mic to work in Tauri .app bundle production.
**Status:** ✅ COMPLETE (2026-03-15) — Phone button approved physical iMac verify
**Research:** Complete — `.claude/cache/agents/vad-openmicloop-cove2026.md`
**Plans:** 2 plans in 2 waves

Plans:
- [ ] audioworklet-01-PLAN.md — Create audio-processor.worklet.js + migrate useVADRecorder to AudioWorkletNode
- [ ] audioworklet-02-PLAN.md — Build on iMac + test phone button in .app bundle + commit

---

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

### Phase F03: f03-latency-optimizer
**Goal:** Ridurre latenza P95 <800ms (attuale ~1330ms). Groq stream=True LLM, asyncio.gather STT+entity parallelo, LRU cache 100 slot, Groq key rotation pool, pre-computation FSM templates, monitoring P50/P95/P99 SQLite. Groq minimization: dal 40% al <15% dei turn con L4 LLM.
**Status:** ✅ COMPLETE (2026-03-04) — 1263 PASS / 0 FAIL
**Research:** Complete — `.planning/phases/f03-latency-optimizer/f03-RESEARCH.md`
**Plans:** 3 plans in 2 waves
**P95 baseline**: 0.3ms NLU-only (test turns); real P95 with LLM to be measured after live sessions. Target <800ms vs ~1330ms.

Plans:
- [x] f03-01-PLAN.md — streaming L4 (generate_response_streaming) + FALLBACK_RESPONSES + LRU cache intent + asyncio.gather L0
- [x] f03-02-PLAN.md — Groq key pool + get_percentile_stats() analytics + WAL mode + /api/metrics/latency route + TTS warmup
- [x] f03-03-PLAN.md — test_latency_benchmark.py + iMac pytest verify (1263 PASS / 0 FAIL) + pipeline restart + endpoint verify + ROADMAP update

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

### Phase P0.5: p0.5-onboarding-frictionless
**Goal:** Remove sales blockers at installation: user can configure Groq API key during wizard (Step 8, already built) AND post-install via Impostazioni. Produce printable HTML/PDF guide for non-technical PMI owners.
**Status:** IN PROGRESS
**Research:** Complete — `.planning/phases/p0.5-onboarding-frictionless/` + planning_context research
**Plans:** 2 plans in 2 waves

Plans:
- [ ] p0.5-01-PLAN.md — VoiceAgentSettings component (Impostazioni → Voice Agent Sara section with groq key save/test)
- [ ] p0.5-02-PLAN.md — public/guida-fluxion.html (printable PMI guide) + human verify full onboarding flow

---

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
