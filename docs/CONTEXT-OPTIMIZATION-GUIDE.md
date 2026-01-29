# Claude Code Context Optimization Guide

## The Problem

CLAUDE.md content is injected into **every API message** as system context. A 45k-char CLAUDE.md means every single turn consumes 45k chars of your context window before Claude even reads your question.

**Symptoms:**
- "Large claude.md will impact performance" warning
- Context fills up fast, triggering summarization early
- Long sessions lose track of earlier work
- Slow response times

## What Actually Works (and What Doesn't)

### Loading Behavior (Verified)

| Source | Loading | When |
|--------|---------|------|
| `CLAUDE.md` | **Eager** | Every message |
| `.claude/rules/*.md` (no paths) | **Eager** | Every message |
| `.claude/rules/*.md` (with `paths:`) | **Conditional** | Only when matching files accessed |
| `@file` references in CLAUDE.md | **Eager** (import) | Session start |
| Skills (descriptions) | **Eager** (lightweight) | Session start |
| Skills (full content) | **Lazy** | On invocation only |
| MCP tools (auto mode) | **Lazy** | On demand via MCPSearch |
| Subagents (Task tool) | **Isolated** | Separate context window |
| Child directory CLAUDE.md | **Lazy** | When working in that subtree |

### Common Mistakes

1. **Using `@docs/file.md` in CLAUDE.md to "lazy load"** - This is an IMPORT. It loads eagerly at startup. The opposite of what you want.

2. **Moving content to `.claude/rules/` without `paths:`** - These are also loaded eagerly. Same cost as putting it in CLAUDE.md.

3. **Using `.claude/rules/` WITH `paths:`** - This DOES work for conditional loading, but only triggers when Claude accesses matching files.

## The Correct Strategy

### Architecture

```
project/
├── CLAUDE.md                          # 2-3k chars MAX
│   ├── Identity + critical rules
│   ├── Active state (current sprint)
│   └── Context routing table
│
├── .claude/
│   ├── rules/
│   │   ├── always-loaded.md           # No paths: → always in context
│   │   ├── backend-rules.md           # paths: ["src-tauri/**"] → conditional
│   │   ├── frontend-rules.md          # paths: ["src/**/*.tsx"] → conditional
│   │   └── voice-rules.md             # paths: ["voice-agent/**"] → conditional
│   │
│   └── skills/                        # Lazy-loaded domain knowledge
│       └── my-project/
│           ├── SKILL.md               # Skill definition
│           └── ...
│
├── docs/                              # Reference docs (loaded via Read tool)
│   ├── architecture.md
│   ├── database-schema.md
│   └── voice-pipeline.md
```

### Three Mechanisms for Reducing Context

**1. Conditional Rules (`.claude/rules/` with `paths:` frontmatter)**

Best for: coding standards, patterns, and conventions tied to specific file types.

```markdown
---
paths:
  - "src-tauri/**/*.rs"
  - "src-tauri/migrations/**"
---

# Rust Backend Rules

- Use sqlx for all database queries
- All commands return Result<T, FluxionError>
- Migrations: sequential numbering (001_, 002_, ...)
- Never use unwrap() in production code
```

This content is ONLY loaded when Claude accesses files matching those paths.

**2. Skills (lazy-loaded domain knowledge)**

Best for: workflows, domain expertise, detailed specifications.

Skills load only their description at startup. Full content loads when invoked.

```markdown
# .claude/skills/my-project/SKILL.md
---
name: voice-pipeline
description: Voice agent pipeline patterns, STT/TTS config, NLU layers
disable-model-invocation: true  # Only load when manually invoked
---

## Full Voice Pipeline Documentation
[... 8000 chars of detailed docs ...]
```

With `disable-model-invocation: true`, even the description stays out of context until the user invokes the skill.

**3. Read-on-demand via routing table**

Best for: reference material, schemas, reports, specs.

Put a routing table in CLAUDE.md that tells Claude which files to read for which domains:

```markdown
## Context Routing

Before working on a domain, read the relevant reference doc:

| Domain | Read First |
|--------|-----------|
| Database/migrations | `docs/database-schema.md` |
| Voice agent | `docs/voice-pipeline.md` |
| Deployment | `docs/DEPLOYMENT.md` |
| Business rules | `docs/business-model.md` |
| GDPR/privacy | `docs/gdpr-compliance.md` |
```

Claude uses the Read tool to load these files only when needed for the current task.

## CLAUDE.md Template (General Purpose)

```markdown
# [Project Name]

## Identity
- [1-2 lines: what the project is]
- [Stack: language + framework + database]
- [Key constraint: e.g., offline-first, no SaaS, etc.]

## Critical Rules (always apply)
- [Rule 1: e.g., "Never commit API keys or .env files"]
- [Rule 2: e.g., "All TypeScript, no JavaScript"]
- [Rule 3: e.g., "Run tests before commit: npm test"]
- [Keep to 5-8 rules maximum]

## Active Work
- Branch: `feature/current-work`
- Current task: [1-2 lines]
- Blocked by: [if any]

## Context Routing

Before working on a domain, read the relevant doc:

| Domain | Reference |
|--------|-----------|
| [domain-1] | `docs/[file-1].md` |
| [domain-2] | `docs/[file-2].md` |
| [domain-3] | `docs/[file-3].md` |

## Infrastructure
- [Essential env info: hosts, ports, paths - keep minimal]
```

**Target: under 2000 chars.**

## Measuring Impact

Check your context usage:

```
/context
```

This shows what's consuming your context window. Compare before and after restructuring.

## What This Doesn't Solve

- **First-message context**: Even a small CLAUDE.md is loaded every message. There's no way to have zero baseline cost.
- **Accumulated tool output**: File reads, grep results, and tool outputs accumulate during a session regardless of CLAUDE.md size.
- **Automatic summarization**: When context fills up, Claude Code summarizes the conversation. This happens regardless of CLAUDE.md size, just later with a smaller CLAUDE.md.

The goal is to maximize the **useful conversation turns** before summarization kicks in, by minimizing the fixed per-message overhead.
