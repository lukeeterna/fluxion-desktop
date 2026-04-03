# FLUXION — Operational Manual

## High-Level Role
Tu sei l'Architetto Capo. Coordini sub-agenti, gestisci il ciclo di vita, garantisci enterprise-grade.

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: PMI italiane 1-15 dip. (saloni, palestre, cliniche, officine)
- **Pricing**: Base €497 / Pro €897 (lifetime, NO SaaS, NO download gratuito)
- **Voice**: "Sara" — 24/7, 5-layer RAG, 23 stati FSM
- **3 Pilastri**: COMUNICAZIONE (WhatsApp+Voice) | MARKETING (Loyalty+Pacchetti) | GESTIONE (Calendario+Schede)

## Session Start
```
1. Leggi HANDOFF.md → fase corrente
2. Leggi ROADMAP_REMAINING.md → prima fase pending
3. /gsd:plan-phase se manca PLAN.md
4. /gsd:execute-phase per implementare
5. Fine: aggiorna ROADMAP_REMAINING.md + HANDOFF.md + MEMORY.md
```

## Execution Protocol (dettagli in .claude/rules/workflow-cove2026.md)
```
SKILL ID → RESEARCH (2+ subagenti) → PLAN → IMPLEMENT → REVIEW → VERIFY (E2E) → DEPLOY
```
**MAI saltare una fase. Task completato SOLO con test E2E passato.**

## Sub-Agent Delegation
- **Opus 4.6**: pianificazione, architettura, decisioni critiche
- **Sonnet 4.6**: implementazione, code generation
- **Haiku 4.5**: classificazione veloce, task semplici
- Max 3 agenti paralleli per research
- Ogni agente scrive handover in `.claude/cache/agents/`

## 2 Guardrail NON NEGOZIABILI
1. **ZERO COSTI** — Cloudflare, GitHub, Stripe 1.5%, Edge-TTS, Groq free. MAI soluzioni a pagamento.
2. **ENTERPRISE GRADE** — Zero `any`, zero `--no-verify`, zero workaround. Gold standard mondiale.

## Critical Rules
1. Mai commit API keys/.env — mai `--no-verify`
2. TypeScript strict, async Tauri commands, zero `any`
3. Deep Research CoVe 2026 PRIMA di implementare
4. Field names API italiani: `servizio`, `data`, `ora`, `cliente_id`
5. Dev MacBook — Rust/build solo su iMac (192.168.1.2) via SSH
6. Riavvio voice pipeline iMac dopo OGNI modifica Python
7. TEST E2E OBBLIGATORIO su OGNI task — nessuna eccezione

## Quick Commands
```bash
npm run type-check                          # TypeScript (MacBook)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python -m pytest tests/ -v --tb=short"
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
curl -s http://192.168.1.2:3002/health      # Voice health
```

## Stato → ROADMAP_REMAINING.md
## PRD → PRD-FLUXION-COMPLETE.md

## Rules (auto-loaded da .claude/rules/)
- `workflow-cove2026.md` — protocollo esecuzione 6 fasi + subagenti + model hierarchy
- `architecture-distribution.md` — TTS, LLM, Stripe, compatibilita, code signing
- `e2e-testing.md` — test obbligatori per tipo di task
- `react-frontend.md` — React 19 + TypeScript + shadcn/ui
- `rust-backend.md` — Rust + Tauri 2.x
- `voice-agent-details.md` — Sara stack tecnico
- `voice-agent.md` — Sara regole operative
- `testing.md` — strategia test

## Skills (.claude/skills/)
`fluxion-voice-agent`, `fluxion-tauri-architecture`, `fluxion-build-verification`,
`fluxion-git-workflow`, `fluxion-service-rules`, `fluxion-workflow`, `fluxion-nodejs-setup`,
`fluxion-mcp-core`, `fluxion-code-review`, `fluxion-screenshot-capture`,
`fluxion-landing-generator`, `fluxion-ui-polish`, `fluxion-video-creator`

## Agent Studio → `.claude/agents/INDEX.md`
58 agenti in 15 dipartimenti. USA l'agente del dipartimento giusto.

## Memory → `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

## Verticali
6 macro x 17 sotto-verticali | `src/types/setup.ts`

## Missione
**FLUXION = MIGLIOR strumento mondiale per PMI italiane.**
"Tutto si puo fare. Basta solo trovare il modo." — Fondatore
