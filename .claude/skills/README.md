# Fluxion Skills for Claude Code

Questa directory contiene le skills personalizzate per il progetto Fluxion, integrate con le repository enterprise esterne.

## Skills Disponibili

| Skill | File | Descrizione |
|-------|------|-------------|
| **Architettura** | `fluxion-tauri-architecture.md` | Pattern Tauri + React + Rust |
| **Voice Agent** | `fluxion-voice-agent.md` | Pipeline RAG 5-layer, TTS Sara |
| **Workflow** | `fluxion-workflow.md` | Epic→Story→Task, RICE, quality gates |

## Come Usare

Claude Code legge automaticamente queste skills quando lavora sul progetto Fluxion. Le skills definiscono:

1. **Pattern obbligatori** - Come strutturare codice Rust e React
2. **Convenzioni** - Naming, file structure, testing
3. **Workflow** - Come pianificare e implementare feature
4. **Quality gates** - Checklist prima di completare task

## Skills Enterprise Integrate

### levnikolaevich/claude-code-skills (84 skills)

```yaml
Documentation (1XX): Auto-gen CLAUDE.md, architecture.md
Planning (2XX): Epic breakdown, RICE prioritization
Task Management (3XX): Story validator, DRY check
Execution (4XX): Priority-based task executor
Quality (5XX): Code review, automated tests
Audit (6XX): 9 parallel auditors (security, deps, etc.)
Bootstrap (7XX): Multi-tech scaffolding
```

### alirezarezvani/claude-skills (42 skills)

```yaml
Engineering: Backend, Frontend, QA, DevOps, Security
Product: RICE prioritizer, PRD generator, OKR cascade
Project: Scrum Master, Jira Expert, Confluence
```

## Aggiungere Nuove Skills

1. Crea file `.md` in questa directory
2. Segui il template delle skills esistenti
3. Documenta in questo README
4. Aggiorna sezione Skills in `CLAUDE.md`

## Struttura Skill

```markdown
# SKILL: [Nome]

> **ID**: skill-id
> **Version**: 1.0.0
> **Category**: [Category]

## Overview
[Descrizione]

## Patterns
[Pattern obbligatori]

## Anti-Patterns (AVOID)
[Cosa evitare]

## Examples
[Esempi codice]
```
