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
- ultimo_update: 2026-05-28T07:37:14Z
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
- Stripe (billing) — test env OK (webhook 200 + idempotency verified S307); promote prod pending S308 Task E
- Cloudflare Workers (delivery proxy `fluxion-proxy/`, env test deployato, env prod pending)
- Resend (email delivery licenze, free tier 100/day) — domain `fluxion-app.com` pre-provisioned (id `6f986180-2eaf-41e2-8a40-53ebeefedbf0`), pending DNS verify [vedi C-FLUXI-002]

## CRITIQUE
- [ADDRESSED] [CC] C-LIC-001: Stripe test env operativo (webhook 200 + idempotency verified S307 via `stripe trigger checkout.session.completed`). Promote prod env tracciato in C-FLUXI-002 Task E.
- [ADDRESSED] [CC] C-FLUXI-001: test ADR feature
- [OPEN] [LUKE+CC] C-FLUXI-002: Resend domain verify + sender promote produzione. **S307 closed ROSSO STRUTTURALE** — `FBUG-RESEND-SHARED-SENDER-01` identificato: `onboarding@resend.dev` test-mode restricted to owner (Resend 403 su customer.email !== owner). Stack reale = `fluxion-proxy/` (Cloudflare Worker) + Resend. Sub-task: (A) founder Cloudflare Registrar `fluxion-app.com` ~€10/anno, (B) founder 3 DNS records DKIM+MX+SPF + bonus DMARC, (C) CTO Resend domain verify + code change `sender.ts`/`stripe-webhook.ts` `from: licenze@fluxion-app.com` + deploy test + smoke FDQ-01 fresh, (D) REGOLA #18 founder GO GUI iMac wizard, (E) promote env=production wrangler.toml + Stripe webhook endpoint prod. Evidence: `~/venture-os/state/fdq-01-smoke-S307.json`. Blocker primo €497 sale.
## METRICHE_SOGLIE
<!-- Numeri che dicono "ok" o "rosso". Es: latenza p95 < 500ms, revenue >= €800. -->
- primo sale Stripe (>= €497)
- latenza Voice Agent p95 < 800ms

## STATO_FEATURE
<!-- Matrice feature × stato (DONE|WIP|MISSING|BLOCKED|TBD).
     Lista estratta empiricamente da src-tauri/src/commands/ + src/components/.
     CC FLUXION nella sessione dedicata DEVE aggiornare lo stato dopo audit codice
     (NON valutato in sessione VOS-meta: richiede ispezione moduli). -->
- clienti: TBD — src-tauri/commands/clienti.rs + src/components/clienti
- magazzino: TBD — verificare se esiste modulo dedicato (no match empirico iniziale)
- calendario/appuntamenti: TBD — src-tauri/commands/appuntamenti.rs + appuntamenti_ddd.rs + src/components/calendario
- cassa: TBD — src-tauri/commands/cassa.rs
- fatture/SDI: TBD — src-tauri/commands/fatture.rs + src/components/fatture + sdi-aruba-multi-provider
- listini: TBD — src-tauri/commands/listini.rs
- operatori: TBD — src-tauri/commands/operatori.rs
- orari: TBD — src-tauri/commands/orari.rs
- loyalty: TBD — src-tauri/commands/loyalty.rs
- analytics/dashboard: TBD — src-tauri/commands/{analytics,dashboard}.rs
- audit_trail (GDPR): TBD — src-tauri/commands/audit.rs
- license_ed25519 (activation): WIP — src-tauri/commands/license_ed25519{,_v1}.rs (client). Delivery server SUPERSEDED da `fluxion-proxy/` Cloudflare Worker (S306+). `scripts/license-delivery/` fermo dal 15 Apr, non più asse attivo. Blocker live = C-FLUXI-002 Resend domain verify.
- Voice Agent Sara: TBD — voice-agent/ (STT Whisper + NLU Groq + TTS Piper, verificare health)
- MCP integration: TBD — src-tauri/commands/mcp.rs
- media/upload schede: TBD — src-tauri/commands/media.rs
- FAQ template: TBD — src-tauri/commands/faq_template.rs
- 9 verticali system: TBD — verificare onboarding per-verticale stato

## STATO_AUTONOMIA
<!-- Livello di autonomia operativa concesso al motore/CC su questo progetto.
     Es: L0=ask-always, L1=ask-on-write, L2=ask-on-deploy, L3=full-auto. -->
L0=ask-always

## PROSSIMA_AZIONE
<!-- Una sola azione concreta. Quando completata, aggiornare con la successiva. -->
S308 Task A — **Founder action**: Cloudflare Registrar checkout `fluxion-app.com` (~$10.46/anno, .com wholesale). URL diretto: `https://dash.cloudflare.com/?to=/:account/domains/register/fluxion-app.com`. Persona fisica OK, no P.IVA. Post-registration CTO verifica via CF API zones, poi sblocca Task B (3 DNS records DKIM+MX+SPF). Fonte canonica corrente: `.claude/NEXT_SESSION_PROMPT.manual.md` (S308 plan completo Task A-E + evidence gate). Step finale C-FLUXI-002: primo €497 sale autonomous smoke con Resend production verde → `vos_plan critique resolve /Volumes/MontereyT7/FLUXION C-FLUXI-002`.
