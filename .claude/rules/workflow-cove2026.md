# Workflow CoVe 2026 — Protocollo Esecuzione

## Fasi Obbligatorie (ordine NON negoziabile)

```
FASE 0 — SKILL ID:   Identifica skill enterprise-grade per il task
FASE 1 — RESEARCH:   2+ subagenti paralleli → .claude/cache/agents/
FASE 2 — PLAN:       AC misurabili, schema DB documentato
FASE 3 — IMPLEMENT:  Commit atomici, TS strict, zero any
FASE 4 — REVIEW:     /fluxion-code-review 12 dimensioni
FASE 5 — VERIFY:     TEST E2E obbligatorio + type-check 0 errori
FASE 6 — DEPLOY:     git push + sync iMac + update ROADMAP + HANDOFF + MEMORY
```

**MAI saltare una fase. MAI.**

## Regola Subagenti
- Per task >15min: Skill ID → SubAgent Research → Plan → SubAgent Implement → Verify
- MAI implementare senza research subagente
- MAI research inline — sempre subagente
- SEMPRE 2+ subagenti paralleli per research
- Output in `.claude/cache/agents/`

## Deep Research CoVe 2026
Per feature >30min:
1. Benchmarka leader mondiali (Fresha, Mindbody, Jane App)
2. Identifica gap vs competitor
3. Definisci gold standard 2026
4. Implementa sopra lo standard

## Agent Studio
`.claude/agents/INDEX.md` — 58 agenti in 15 dipartimenti
USA l'agente del dipartimento giusto, NON general-purpose se ne esiste uno dedicato

## Model Hierarchy
- **Opus 4.6**: pianificazione, architettura, decisioni critiche
- **Sonnet 4.6**: implementazione, code generation
- **Haiku 4.5**: classificazione veloce, task semplici
