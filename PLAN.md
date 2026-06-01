<!-- VOS PLAN — template generico. Compilato da `vos_plan adopt|create|greenfield`.
     Posizione canonica: <project>/PLAN.md (root del progetto).
     Stati CRITIQUE: [OPEN] | [ADDRESSED] | [DEFERRED:motivo]
     Tag confidence TARGET_VALIDATO: VERIFIED:<fonte> | INFERRED | ASSUMPTION
     Non rimuovere le intestazioni `## SECTION` — il motore le usa per il parsing. -->

# PLAN — FLUXION

## META
- project: FLUXION
- path: /Volumes/MontereyT7/FLUXION
- maturità: mature          <!-- mature | maturing | greenfield, CONFERMATA via assess -->
- creato: 2026-05-28T07:37:14Z
- ultimo_update: 2026-06-01 (S320 — payment rail VERIFIED-LIVE S317/S319; gate "pronto a vendere" residuo = Sara live multi-verticale + install/activate)
- modalità_ingaggio: adopt  <!-- adopt | create | greenfield -->

## OBIETTIVO
<!-- Una frase netta. Cosa deve produrre il progetto, per chi, in che orizzonte. -->
gestionale desktop SMB italiano con Voice Agent AI (Sara), €497 one-time, 9 verticali

## GUARDRAIL
<!-- Vincoli non derogabili (budget, stack, compat, founder-decisions). Uno per riga. -->
- macOS Big Sur compat MacBook (no upgrade OS) + iMac 2012 no-AVX2 server
- Python 3.13 + Tauri 2 + React + Rust (stack consolidato, no rewrite)
- T7 USB MacBook = storage primario; verifica `os.path.ismount('/Volumes/MontereyT7')` all'avvio componenti
- Budget LLM hard cap €30/mese (free-tier first, OpenRouter routing)
- 9 verticali al massimo: saloni, medical, palestre, auto, odonto, vet, servizi, immobiliare, assicurazioni (no scope creep settori)
- Voice Agent Sara = pilastro identitario (STT Whisper + NLU Groq + TTS Piper locale)
- Distribuzione: Tauri sign Mac + Win, no Docker, no store-only
- GDPR audit trail obbligatorio (cliente italiano SMB = compliance non opzionale)

## TARGET_VALIDATO
<!-- Chi è l'utente reale. Ogni claim TAG: VERIFIED:<fonte> | INFERRED | ASSUMPTION -->
- SMB italiane 9 verticali (saloni/medical/palestre/auto/odonto/vet/servizi/immobiliare/assicurazioni) [INFERRED:memoria project_fluxion_real_product]
- Microimprese 1-10 dipendenti, titolare = buyer = decision-maker [ASSUMPTION:no interviste validation done]
- Geografico: Italia (lingua, P.IVA, SDI, GDPR) [INFERRED]
- Pricing point €497 one-time [ASSUMPTION:zero paying customer al 2026-05-28]
- Pain primario: gestione clienti+appuntamenti+listino senza essere al PC tutto il giorno (driver Voice Agent Sara) [ASSUMPTION:inferito da blueprint, no JTBD interview]
- Awareness canale principale: video marketing + WA outreach [INFERRED:tool SalesAgentWA in repo]

## METODO
<!-- Come ci arrivi. Fasi, dipendenze, gate. Niente roadmap-novel: bullet brevi. -->
<!-- importato da .planning/ via assess (file vivi soltanto) -->
- ref: `.claude/cache/agents/s227-l4-facility-research.md` (mtime 2026-05-14)
- ref: `.claude/cache/agents/s215-streaming-llm-tts-research.md` (mtime 2026-05-13)
- ref: `voice-agent/requirements.txt` (mtime 2026-05-13)
- ref: `docs/perf/D1-sqlite-query-plans.md` (mtime 2026-05-08)
- ref: `.planning/phases/s185-helpdesk-wiki/PLAN.md` (mtime 2026-05-04)
- ref: `.claude/cache/agents/s185/research-2-wiki-schema.md` (mtime 2026-05-04)
- ref: `.claude/cache/agents/s185/research-1-source-audit.md` (mtime 2026-05-04)
- ref: `ROADMAP_S184_PROGRESS.md` (mtime 2026-05-04)
- ref: `scripts/install/docs/NETWORK-REQUIREMENTS.md` (mtime 2026-05-02)
- ref: `.claude/cache/agents/research-zero-bug-install-s184a3.md` (mtime 2026-05-02)
- ref: `.claude/cache/agents/research-enterprise-packaging-s184a3.md` (mtime 2026-05-02)
- ref: `ROADMAP_S183_S190.md` (mtime 2026-05-01)
- ref: `ROADMAP_S184_REVISED_ALPHA.md` (mtime 2026-05-01)
- ref: `ROADMAP_REMAINING.md` (mtime 2026-04-30)
- ref: `.claude/cache/agents/s175-art59-checkbox-research.md` (mtime 2026-04-28)
- ref: `.claude/cache/agents/s175-email-gate-research.md` (mtime 2026-04-28)
- ref: `.claude/cache/agents/s174-gdpr-template-research.md` (mtime 2026-04-27)
- ref: `.claude/cache/agents/s174-stripe-refund-research.md` (mtime 2026-04-27)
- ref: `.claude/agent-memory/trend-researcher/research_pmi_it_copy_patterns_2026.md` (mtime 2026-04-27)
- ref: `.claude/agent-memory/trend-researcher/research_video_demo_pmi_2026.md` (mtime 2026-04-27)
- ref: `.claude/agent-memory/growth-hacker/project_sales_agent_blueprint.md` (mtime 2026-04-14)
- ref: `tools/SalesAgentWA/SALES-AGENT-BLUEPRINT.md` (mtime 2026-04-14)
- ref: `.claude/cache/agents/research-f2-acoustic-frustration.md` (mtime 2026-04-10)
- ref: `.claude/cache/agents/research-f1-eou-detection.md` (mtime 2026-04-10)
- ref: `.planning/SARA-WORLDCLASS-PLAN.md` (mtime 2026-04-10)
- ref: `.claude/cache/agents/vad-barge-in-research.md` (mtime 2026-04-09)
- ref: `.claude/cache/agents/stt-italian-surnames-research.md` (mtime 2026-04-09)
- ref: `.claude/skills/deep-research.md` (mtime 2026-04-09)
- ref: `.claude/cache/agents/ai-video-gen-free-tier-research-2026.md` (mtime 2026-04-04)
- ref: `.claude/cache/agents/ai-music-gen-free-tier-research-2026.md` (mtime 2026-04-04)
- ref: `tools/VectCutAPI/requirements.txt` (mtime 2026-04-03)
- ref: `tools/VectCutAPI/requirements-mcp.txt` (mtime 2026-04-03)
- ref: `.claude/cache/agents/moviepy-video-research-2026.md` (mtime 2026-04-03)
- ref: `.claude/cache/agents/capcut-api-research-2026.md` (mtime 2026-04-03)
- ref: `.claude/agents/video/verticale-research-agent.md` (mtime 2026-04-01)
- ref: `video-factory/requirements.txt` (mtime 2026-04-01)
- ref: `.claude/cache/agents/universal-voip-solution-research.md` (mtime 2026-03-29)
- ref: `.planning/phases/10-video-v6/10-04-PLAN.md` (mtime 2026-03-26)
- ref: `.planning/phases/10-video-v6/10-03-PLAN.md` (mtime 2026-03-26)
- ref: `.claude/cache/agents/video-sales-outreach-research-2026.md` (mtime 2026-03-26)
- ref: `.claude/cache/agents/us-smb-sales-outreach-research-2026.md` (mtime 2026-03-26)
- ref: `.claude/cache/agents/video-copywriter-v6-research.md` (mtime 2026-03-26)
- ref: `.claude/cache/agents/storyboard-v6-research.md` (mtime 2026-03-26)
- ref: `.claude/cache/agents/landing-v2-optimization-research.md` (mtime 2026-03-25)
- ref: `.claude/cache/agents/growth-first-100-clients-research.md` (mtime 2026-03-25)
- ref: `.claude/cache/agents/vsl-video-sales-research-2026.md` (mtime 2026-03-25)
- ref: `.claude/cache/agents/veo3-clips-v6-research.md` (mtime 2026-03-25)
- ref: `.claude/cache/agents/2026-video-selling-trends-research.md` (mtime 2026-03-25)
- ref: `.claude/agents/verticals/vertical-researcher.md` (mtime 2026-03-23)
- ref: `.claude/agents/design/ux-researcher.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/youtube-vimeo-video-agents-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/missing-business-agents-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/agent-studio-structure-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/background-music-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/json-to-video-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/claude-video-skills-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/kaggle-gpu-video-generation-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/cinematic-ai-video-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/video-pipeline-composition-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/ai-video-generation-research-2026.md` (mtime 2026-03-23)
- ref: `.claude/cache/agents/delivery-pipeline-indie-research-2026.md` (mtime 2026-03-20)
- ref: `voice-agent/requirements-prod.txt` (mtime 2026-03-20)
- ref: `.claude/cache/agents/escalation-human-operator-research-2026.md` (mtime 2026-03-19)
- ref: `.claude/cache/agents/f19-booking-system-deep-research-2026.md` (mtime 2026-03-19)
- ref: `.claude/cache/agents/f19-sara-db-grounded-research.md` (mtime 2026-03-19)
- ref: `.claude/cache/agents/voip-pmi-italia-pricing-deep-research-2026.md` (mtime 2026-03-19)
- ref: `.claude/cache/agents/voip-italy-market-research-2026.md` (mtime 2026-03-19)
- ref: `.claude/cache/agents/distribution-no-signing-research-2026.md` (mtime 2026-03-18)
- ref: `.claude/cache/agents/voip-italy-deep-research-2026.md` (mtime 2026-03-18)
- ref: `.claude/cache/agents/free-llm-providers-2026-research.md` (mtime 2026-03-16)
- ref: `.claude/cache/agents/voice-agent-architecture-2026-research.md` (mtime 2026-03-16)
- ref: `.claude/cache/agents/groq-structured-nlu-research.md` (mtime 2026-03-16)
- ref: `.claude/cache/agents/code-reviewer-enterprise-research.md` (mtime 2026-03-16)
- ref: `.claude/cache/agents/sales-chatbot-benchmark-research.md` (mtime 2026-03-16)
- ref: `.claude/cache/agents/sara-sales-fsm-wiring-research.md` (mtime 2026-03-16)
- ref: `.claude/cache/agents/italian-lead-gen-research.md` (mtime 2026-03-16)
- ref: `.planning/phases/f-sara-voice/f-sara-voice-05-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-voice/f-sara-voice-04-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-voice/f-sara-voice-03-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-voice/f-sara-voice-01-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-voice/f-sara-voice-02-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-voice/f-sara-voice-RESEARCH.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-04-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-03-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-02-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-01-PLAN.md` (mtime 2026-03-15)
- ref: `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-RESEARCH.md` (mtime 2026-03-15)
- ref: `.planning/phases/audioworklet-vad-fix/audioworklet-02-PLAN.md` (mtime 2026-03-14)
- ref: `.planning/phases/audioworklet-vad-fix/audioworklet-01-PLAN.md` (mtime 2026-03-14)
- ref: `.claude/cache/agents/gap-p1-8-research.md` (mtime 2026-03-13)
- ref: `.claude/cache/agents/gap-p1-1-p1-2-research.md` (mtime 2026-03-13)
- ref: `.claude/cache/agents/f15-voip-telnyx-research.md` (mtime 2026-03-12)
- ref: `.claude/cache/agents/temporal-nlu-research-agente-b.md` (mtime 2026-03-12)
- ref: `.claude/cache/agents/temporal-nlu-research-agente-a.md` (mtime 2026-03-12)
- ref: `voice-agent/requirements-docker.txt` (mtime 2026-03-11)
- ref: `.claude/cache/agents/p05-onboarding-research.md` (mtime 2026-03-10)
- ref: `.claude/cache/agents/gap9-analytics-research.md` (mtime 2026-03-10)
- ref: `.claude/cache/agents/gap4-wa-interactive-research.md` (mtime 2026-03-10)
- ref: `.claude/cache/agents/gap5-pdf-listino-research.md` (mtime 2026-03-10)
- ref: `.claude/cache/agents/cove2026-deep-research-market.md` (mtime 2026-03-09)
- ref: `.claude/cache/agents/f06-media-generation-research.md` (mtime 2026-03-07)
- ref: `voice-agent/requirements-ci.txt` (mtime 2026-03-06)
- ref: `.claude/cache/agents/kaggle-flux-research.md` (mtime 2026-03-06)
- ref: `.claude/cache/agents/kaggle-model-hub-path-research.md` (mtime 2026-03-05)
- ref: `.claude/cache/agents/schede-media-upload-research.md` (mtime 2026-03-05)
- ref: `.planning/phases/p0.5-onboarding-frictionless/p0.5-02-PLAN.md` (mtime 2026-03-05)
- ref: `.planning/phases/p0.5-onboarding-frictionless/p0.5-01-PLAN.md` (mtime 2026-03-05)
- ref: `.planning/phases/f03-latency-optimizer/f03-03-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f03-latency-optimizer/f03-02-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f03-latency-optimizer/f03-01-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f03-latency-optimizer/f03-RESEARCH.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02.1-nlu-hardening/f02.1-03-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02.1-nlu-hardening/f02.1-01-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02.1-nlu-hardening/f02.1-02-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02.1-nlu-hardening/f02.1-04-PLAN.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/f02-nlu-ambiguity-research.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02-vertical-system-sara/f02-03-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02-vertical-system-sara/f02-02-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02-vertical-system-sara/f02-01-PLAN.md` (mtime 2026-03-04)
- ref: `.planning/phases/f02-vertical-system-sara/F02-RESEARCH.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/license-feature-gating-research.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/voice-agent-production-issues-research.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/b4-exception-handling-research.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/voice-test-fix-research.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/whatsapp-webhook-research.md` (mtime 2026-03-04)
- ref: `.claude/cache/agents/voice-agent-bugs-research.md` (mtime 2026-03-03)
- ref: `.claude/cache/agents/voice-nlu-italian-research.md` (mtime 2026-03-03)
- ref: `.planning/phases/sdi-aruba-multi-provider/03-ui-impostazioni-PLAN.md` (mtime 2026-03-03)
- ref: `.planning/phases/sdi-aruba-multi-provider/04-verify-typecheck-PLAN.md` (mtime 2026-03-03)
- ref: `.planning/phases/sdi-aruba-multi-provider/01-migration-rust-trait-PLAN.md` (mtime 2026-03-03)
- ref: `.planning/phases/sdi-aruba-multi-provider/02-rust-providers-PLAN.md` (mtime 2026-03-03)
- ref: `.claude/cache/agents/sdi-free-research.md` (mtime 2026-03-03)
- ref: `.claude/cache/agents/test-autonomi-research.md` (mtime 2026-03-03)
- ref: `.claude/cache/agents/landing-screenshots-research.md` (mtime 2026-03-02)
- ref: `.claude/cache/agents/v1-enterprise-plan.md` (mtime 2026-03-02)
- ref: `.claude/cache/agents/sdi-fatturapa-research.md` (mtime 2026-03-02)
- ref: `.claude/cache/agents/cross-platform-deep-research.md` (mtime 2026-02-27)
- ref: `voice-agent/requirements-windows.txt` (mtime 2026-02-27)
- ref: `.claude/cache/agents/windows-compat-research.md` (mtime 2026-02-27)
- ref: `.claude/cache/agents/token-saving-research.md` (mtime 2026-02-27)
- ref: `.claude/cache/agents/lukeagent-research.md` (mtime 2026-02-27)
- ref: `.claude/cache/agents/sub-verticals-research.md` (mtime 2026-02-27)
- ref: `scripts/video-remotion/TUTORIAL_PLAN.md` (mtime 2026-02-27)
- ref: `scripts/license-delivery/requirements.txt` (mtime 2026-02-23)
- ref: `DETERMINISTIC-EXECUTION-PLAN.md` (mtime 2026-02-19)
- ref: `docs/DEEP-RESEARCH-VOICE-AGENT-2026.md` (mtime 2026-02-13)
- ref: `docs/context/VOICE-AGENT-ROADMAP.md` (mtime 2026-02-05)
- ref: `docs/VERTICALS-RESEARCH-COMPLETE.md` (mtime 2026-02-05)
- ref: `docs/LICENSE-RESEARCH-OPENSOURCE.md` (mtime 2026-02-05)
- ref: `docs/GDPR-AUDIT-TRAIL-PLAN.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/3-solutioning/create-architecture/steps/step-04-decisions.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/1-analysis/research/technical-steps/step-06-research-synthesis.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/1-analysis/research/technical-steps/step-05-implementation-research.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/1-analysis/research/research.template.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/1-analysis/research/market-steps/step-06-research-completion.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/1-analysis/research/market-steps/step-04-customer-decisions.md` (mtime 2026-02-05)
- ref: `_bmad/bmm/workflows/1-analysis/research/domain-steps/step-06-research-synthesis.md` (mtime 2026-02-05)
- ref: `.claude/get-shit-done/workflows/execute-plan.md` (mtime 2026-02-05)
- ref: `.claude/get-shit-done/templates/roadmap.md` (mtime 2026-02-05)
- ref: `.claude/get-shit-done/templates/research.md` (mtime 2026-02-05)
- ref: `.claude/get-shit-done/templates/requirements.md` (mtime 2026-02-05)
- ref: `.claude/get-shit-done/templates/planner-subagent-prompt.md` (mtime 2026-02-05)
- ref: `.claude/get-shit-done/references/planning-config.md` (mtime 2026-02-05)
- ref: `.claude/commands/gsd/research-phase.md` (mtime 2026-02-05)
- ref: `.claude/commands/gsd/plan-phase.md` (mtime 2026-02-05)
- ref: `.claude/commands/gsd/plan-milestone-gaps.md` (mtime 2026-02-05)
- ref: `.claude/commands/bmad-bmm-sprint-planning.md` (mtime 2026-02-05)
- ref: `.claude/commands/bmad-bmm-research.md` (mtime 2026-02-05)
- ref: `.claude/agents/gsd-roadmapper.md` (mtime 2026-02-05)
- ref: `.claude/agents/gsd-research-synthesizer.md` (mtime 2026-02-05)
- ref: `.claude/agents/gsd-project-researcher.md` (mtime 2026-02-05)
- ref: `.claude/agents/gsd-planner.md` (mtime 2026-02-05)
- ref: `.claude/agents/gsd-plan-checker.md` (mtime 2026-02-05)
- ref: `.claude/agents/gsd-phase-researcher.md` (mtime 2026-02-05)
- ref: `docs/context/DECISIONS.md` (mtime 2026-01-11)
- ref: `docs/sessions/2026-01-07-15-30-ci-cd-fix-roadmap-fornitori-remote.md` (mtime 2026-01-07)
- ref: `REFACTORING-ROADMAP.md` (mtime 2026-01-03)

## VARIABILI_PREVISTE
<!-- Cosa puoi controllare/variare durante l'esecuzione. Param scelti consapevolmente. -->
- Verticale attivo (default vuoto, scelto in onboarding)
- Voice Agent on/off, lingua (default IT)
- Pricing offer: €497 one-time confermato; bundle features per verticale [DEFERRED: subscription]
- Canale acquisizione: video marketing vs WA outreach vs landing organica

## STACK_TOOL
<!-- Tecnologia attiva. Una libreria/runtime per riga + versione se vincolante. -->
- Tauri 2 (desktop framework cross-platform Mac+Win)
- React 18+ (frontend)
- Rust (backend nativo, SDI providers Aruba multi-provider)
- Python 3.13 (Voice Agent Sara: orchestrazione)
- Whisper (STT)
- Groq (NLU, structured outputs)
- Piper (TTS locale)
- SQLite (storage clienti/servizi/operatori)
- MCP (Model Context Protocol per integrazione)
- Stripe (billing) — test env OK (webhook 200 + idempotency verified S307); prod webhook secret active S313 (LIVE endpoint verify carry-over founder)
- Cloudflare Workers (delivery proxy `fluxion-proxy/`, env test + prod DEPLOYATI; prod version `e18df659-bed2-4491-a8fe-9fef9e398b2e` S313, 13 secrets, /health 200)
- Resend (email delivery licenze, free tier 100/day) — domain `fluxion-app.com` pre-provisioned (id `6f986180-2eaf-41e2-8a40-53ebeefedbf0`), pending DNS verify [vedi C-FLUXI-002]

## CRITIQUE
- [ADDRESSED] [CC] C-FLUXI-001: test ADR feature
- [ADDRESSED] [LUKE] C-FLUXI-002: Primo CLOSED_WON real end-to-end: Stripe Payment Link → webhook proxy → D1 license insert → Ed25519 sign → Resend delivery → wizard activate Keychain. Blocker storico: FBUG-RESEND-SHARED-SENDER-01 (S307) + bug detectTier metadata key mismatch (S317).
## METRICHE_SOGLIE
<!-- Numeri che dicono "ok" o "rosso". Es: latenza p95 < 500ms, revenue >= €800. -->
- primo sale Stripe (>= €497)
- latenza Voice Agent p95 < 800ms

## STATO_FEATURE
<!-- Matrice feature × stato. Vocabolario aggiornato S308.audit-2 (code-truth):
     ESISTE_E_GIRA | ESISTE_NON_TESTATO | SCAFFOLD | ASSENTE.
     Refresh: 2026-05-28 S308.audit-2 — fonte = grep + `tsc --noEmit` PASS + `ssh imac cargo check` PASS (0 err, 10 warn soft) + `ssh imac ls bundle/`.
     E2E=NO su tutta la matrice salvo nota esplicita (nessun harness eseguito in S308.audit-2). -->
- clienti: ESISTE_NON_TESTATO — commands/clienti.rs (7 tauri::command) + pages/Clienti.tsx + components/clienti/{ClienteDialog,ClienteForm,ClientiTable}.tsx. E2E=NO.
- magazzino: ASSENTE — grep `magazzino|sottoscorta|inventario|scorta_minima|reorder|stock_` su *.{rs,sql,tsx,ts} → 0 match in src/ (unico hit: scripts/seed-sara-gommista.sql, seed isolato). Nessun command, nessuna migration, nessuna UI, nessuna tabella. Decisione scope v1.0 vs post-launch = LUKE.
- calendario/appuntamenti: ESISTE_NON_TESTATO — commands/appuntamenti.rs (7) + appuntamenti_ddd.rs + pages/Calendario.tsx + components/calendario/AppuntamentoDialog.tsx. E2E=NO.
- cassa: ESISTE_NON_TESTATO — commands/cassa.rs (8) + pages/Cassa.tsx. E2E=NO.
- fatture/SDI: ESISTE_NON_TESTATO — commands/fatture.rs (17) + pages/Fatture.tsx + components/fatture/{FatturaDetail,FatturaDialog,ImpostazioniFatturazioneDialog}.tsx + migrations 007_fatturazione_elettronica.sql + 026_impostazioni_sdi_key.sql + 029_sdi_multi_provider.sql. E2E=NO (no smoke SDI provider live).
- listini: ESISTE_NON_TESTATO — commands/listini.rs (5) + migration 031_listini_fornitori.sql. UI dedicata non rilevata in src/pages/. E2E=NO.
- operatori: ESISTE_NON_TESTATO — commands/operatori.rs (16) + pages/Operatori.tsx + migrations 012_operatori_voice_agent.sql + 025_operatori_commissioni.sql + 033_operatori_genere.sql. E2E=NO.
- orari: ESISTE_NON_TESTATO — commands/orari.rs (10). E2E=NO.
- loyalty: ESISTE_NON_TESTATO — commands/loyalty.rs (22) + components/loyalty/{LoyaltyProgress,PacchettiAdmin,PacchettiList}.tsx + migrations 005_loyalty_pacchetti_vip.sql + 006_pacchetto_servizi.sql. E2E=NO.
- analytics/dashboard: ESISTE_NON_TESTATO — commands/analytics.rs (2) + commands/dashboard.rs (2) + pages/{Analytics,Dashboard}.tsx. Endpoint minimi (2 cmd per modulo) → audit coverage funzionale separato. E2E=NO.
- audit_trail (GDPR): ESISTE_NON_TESTATO — commands/audit.rs (10). UI consent PARZIALE: solo components/media/MediaConsentModal.tsx + components/setup/SetupWizard.tsx; **nessuna pagina audit-trail dedicata** in src/pages/. E2E=NO.
- license_ed25519 (activation): ESISTE_E_GIRA (lato client) — commands/license_ed25519.rs (9) + license_ed25519_v1.rs + migration 020_license_ed25519.sql + components/license/*. Server delivery `fluxion-proxy/src/routes/stripe-webhook.ts` PASS audit S308.1 (sign+D1+Resend). E2E=NO end-to-end pagamento→email→activate live. Blocker = C-FLUXI-002 (FBUG-RESEND-SHARED-SENDER-01).
- Voice Agent Sara: ESISTE_NON_TESTATO — voice-agent/main.py aiohttp 3002 + src/{booking_state_machine,orchestrator,groq_nlu,disambiguation_handler,...}.py (30+ moduli). Server **NON ATTIVO** durante audit (hook status: 3001+3002 down). Import smoke confermato S308.1 (BookingStateMachine, VoiceOrchestrator import OK Python 3.9.6 iMac). Runtime E2E=NO.
- MCP integration: ESISTE_NON_TESTATO — commands/mcp.rs (11). **Cargo warning lib.rs:839 `unexpected cfg condition value: mcp`** → feature dietro cfg flag mai abilitato di default. E2E=NO.
- media/upload schede: ESISTE_NON_TESTATO — commands/media.rs (8) + components/media/{MediaConsentModal,MediaUploadZone}.tsx + migration 030_cliente_media.sql. E2E=NO.
- FAQ template: ESISTE_NON_TESTATO — commands/faq_template.rs (6) + migration 008_faq_template_soprannome.sql + UI gestione in pages/Impostazioni.tsx. E2E=NO.
- 9 verticali system: ESISTE_NON_TESTATO **CON INCOERENZA DATI** — `src/types/setup.ts:239` MACRO_CATEGORIE = **5 valori** (salone, auto, wellness, medical, altro) · voice-agent/scripts/switch_vertical.sh enumera **9 verticali** (salone, barbiere, beauty, odontoiatra, fisioterapia, gommista, toelettatura, palestra, medical) · CLAUDE.md dichiara "8 macro × 50 micro". Tre fonti discordi. components/schede-cliente/ contiene 10 schede Scheda*.tsx + migrations 027_scheda_fitness, 035_scheda_pet. Allineamento = LUKE decide canonica + CC riallinea. E2E=NO.

## STATO_FEATURE_EXTRA
<!-- Feature non originariamente in PLAN.md, audit S308.audit-2. -->
- Sara input audio reale microfono (SIP/VoIP): SCAFFOLD — voice-agent/src/voip_pjsua2.py + lib/pjsua2/pjsua2.py presenti. main.py:1320 gate `if voip_sip_user: VoIPManager.start()` → default NON parte (log "ℹ️ VoIP non configurato"). commands/voice_calls.rs (11) lato Tauri. E2E=NO (no credenziali SIP attive + server 3002 down).
- Stress-test Sara 9 verticali: ESISTE_NON_TESTATO — voice-agent/scripts/test_all_verticals_e2e.py (harness booking+faq+triage per 9 verticali) + switch_vertical.sh (DB swap + restart pipeline) + create_vertical_dbs.py. Richiede pipeline UP iMac. E2E=NO (non eseguito S308.audit-2).
- Packaging macOS .dmg/.app: ESISTE_E_GIRA — tauri.conf.json targets `["dmg","app","nsis"]` · `ssh imac ls target/release/bundle/dmg/` = `Fluxion_1.0.1_x64.dmg` **89.3MB built 2026-05-25** + Fluxion.app/Contents/MacOS/{tauri-app 19.6MB, voice-agent 77.6MB PyInstaller reale}. NOTA: `signingIdentity:null` → DMG ad-hoc (Gatekeeper warning). E2E=NO (mai installato fine→fine in audit).
- Packaging Windows .msi/.exe: SCAFFOLD — tauri.conf.json target `nsis` + installer-hooks.nsh + wix.language:it-IT configurati. **Nessun artefatto** Windows in target/release/bundle/ (solo dmg+macos). Cross-build mai eseguito. E2E=NO.
- Installer / procedura semplificata: SCAFFOLD — DMG macOS unsigned esiste su iMac. **Sidecar MacBook è placeholder shell-script 296B** (`echo placeholder — exit 1` in src-tauri/binaries/voice-agent-x86_64-apple-darwin) → build deve sempre partire da iMac (binario reale 77MB datato 2026-05-13). Sync MacBook↔iMac assente. Nessuno script installer Windows. E2E=NO.
- Sales Agent WA (PMI segmentate): ESISTE_NON_TESTATO — tools/SalesAgentWA/ 1236 righe core (agent.py 365 + sender.py 419 + scraper.py 452). Sorgenti: Google Places + PagineBianche + OSM Overpass. Segmentazione **per città** (29 città in CITY_COORDS) + **per categoria** (5 keyword set in CATEGORY_KEYWORDS). **Regione/provincia NON supportate** in scraper. wa_session/ presente (Chrome profile), **nessun leads.db** (find tools/SalesAgentWA -name "*.db" → 0). Mai eseguito in produzione. E2E=NO.

## BUILD_RUN_STATUS (S308.audit-2, 2026-05-28)
- `npx tsc --noEmit` (frontend): PASS — 0 errori.
- `ssh imac cargo check` (backend Tauri): PASS — 0 errori, 10 warning soft (unused imports, ambiguous glob re-exports in commands/mod.rs:52+69, cfg flag inesistenti `mcp` e `e2e` in lib.rs:839+851, unused const `OFFLINE_GRACE_DAYS`).
- `npm run type-check` locale: FAIL ambiente (`_cc_pin_trap: command not found` da alias zsh) → bypass via `npx tsc`. Non bloccante codice.
- Servizi runtime: HTTP Bridge 3001 DOWN + Voice Pipeline 3002 DOWN (hook status check inizio sessione). Nessun smoke E2E eseguito in audit.

## CONTEGGIO_FEATURE (23 uniche)
- ESISTE_E_GIRA: 2 (license_ed25519 client, packaging macOS .dmg)
- ESISTE_NON_TESTATO: 17
- SCAFFOLD: 3 (Sara SIP, packaging Windows, installer semplificato)
- ASSENTE: 1 (magazzino)
- E2E=SÌ: 0 · E2E=NO: 22 · E2E=N/A: 1

## STATO_AUTONOMIA
<!-- Livello di autonomia operativa concesso al motore/CC su questo progetto.
     Es: L0=ask-always, L1=ask-on-write, L2=ask-on-deploy, L3=full-auto. -->
L0=ask-always

## PROSSIMA_AZIONE
<!-- Una sola azione concreta. Quando completata, aggiornare con la successiva. -->
PAYMENT RAIL CHIUSO (superato S314): percorso acquisto €497/€897 VERIFIED-E2E-LIVE — smoke €1 reale Base (S317) + Pro (S319), webhook 200 + Ed25519 + D1 + Resend `delivered` su Gmail + refund, costo netto €0. C-FLUXI-002 RESOLVED con Luke GO (S318). Dominio `fluxion-app.com` verificato DKIM/SPF/MX.

GATE "PRONTO A VENDERE" RESIDUO (vincolo founder S320 — REGOLA #21, Sara = pilastro NON deferrabile):
1. **SARA LIVE MULTI-VERTICALE (blocker primario)** — chiamata telefonica reale iMac+smartphone su TUTTI i verticali canonici + stress test reali (interruzioni, nomi difficili, slot pieni). Criterio accettazione = "soddisfa pienamente il cliente", non solo "non crasha". Harness esistente `voice-agent/scripts/test_all_verticals_e2e.py` + `switch_vertical.sh` (richiede pipeline 3002 UP iMac). E2E runtime mai eseguito.
2. **Verticali canonici (LUKE decide)** — 3 fonti discordi (setup.ts=5 macro / switch_vertical.sh=9 / CLAUDE.md 8×50). Lista canonica = prereq per "tutti i verticali" del punto 1.
3. **macOS signing ad-hoc €0 + pagina Gatekeeper** (deciso S319) — CTO autonomo.
4. **DMG download URL pubblico verificato** — oggi DMG 89.3MB solo su iMac `target/release/bundle/`, nessun URL pubblico testato.
5. **Wizard activate GUI live** — unico anello cliente mai eseguito E2E (founder fisicamente all'iMac, REGOLA #12).

SEQUENCING GO-TO-MARKET: tutto sopra pronto → **Sales Agent WA** (`tools/SalesAgentWA/`, 1236 righe, mai acceso, no leads.db) propone/vende FLUXION. Da implementare/attivare solo quando tutto pronto.

CLEANUP minore: C-LIC-001 `[DEFERRED]`→`[ADDRESSED]` (credenziali LIVE attive da S316); correzione doc "23 stati FSM"→15 reali (enum BookingState).