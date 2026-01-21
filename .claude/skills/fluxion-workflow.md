# SKILL: Fluxion Development Workflow

> **ID**: fluxion-workflow
> **Version**: 1.0.0
> **Category**: Workflow / Project Management
> **Integrates**: levnikolaevich/claude-code-skills, alirezarezvani/claude-skills

---

## Overview

This skill defines the development workflow for Fluxion, integrating enterprise-level patterns from external skill repositories. It enforces a structured Epic → Story → Task flow with quality gates.

## Workflow Stages

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  EPIC   │───▶│  STORY  │───▶│  TASK   │───▶│ REVIEW  │───▶│  DONE   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
 Research       RICE Score     Implement      Quality
 Standards      Acceptance     + Test         Gates
               Criteria
```

## 1. Epic Definition

### Template

```markdown
# EPIC: [Nome Feature]

## Obiettivo
[Descrizione dell'obiettivo business in 1-2 frasi]

## Utente Target
[Persona: es. "Titolare salone con 3-5 dipendenti"]

## Success Metrics
- [ ] Metric 1 (quantificabile)
- [ ] Metric 2 (quantificabile)

## Stories
- [ ] STORY-001: [Nome]
- [ ] STORY-002: [Nome]

## Rischi
| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| ... | Alta/Media/Bassa | Alto/Medio/Basso | ... |

## Timeline
- Start: YYYY-MM-DD
- Target: YYYY-MM-DD
```

## 2. Story Definition (RICE Prioritization)

### RICE Score Calculation

```
RICE = (Reach × Impact × Confidence) / Effort

Reach: Utenti impattati (1-1000)
Impact: 0.25 (minimal), 0.5 (low), 1 (medium), 2 (high), 3 (massive)
Confidence: 0.5 (low), 0.8 (medium), 1.0 (high)
Effort: Person-days (1-30)
```

### Story Template

```markdown
# STORY: [ID] [Nome]

## RICE Score
| Factor | Value | Rationale |
|--------|-------|-----------|
| Reach | X | [Quanti utenti] |
| Impact | X | [Quale impatto] |
| Confidence | X | [Quanto sicuri] |
| Effort | X | [Giorni-persona] |
| **RICE** | **X** | Auto-calculated |

## User Story
Come [RUOLO], voglio [AZIONE], così che [BENEFICIO].

## Acceptance Criteria
- [ ] AC1: [Criterio verificabile]
- [ ] AC2: [Criterio verificabile]
- [ ] AC3: [Criterio verificabile]

## Technical Notes
- Files coinvolti: `src/...`, `src-tauri/...`
- Pattern: [Riferimento a skill architettura]
- Dipendenze: [Altre stories/tasks]

## Tasks
- [ ] TASK-001: [Backend] ...
- [ ] TASK-002: [Frontend] ...
- [ ] TASK-003: [Test] ...
```

## 3. Task Execution

### Task Types

| Type | Prefix | Description |
|------|--------|-------------|
| Backend | `[BE]` | Rust commands, migrations, services |
| Frontend | `[FE]` | React components, hooks, pages |
| Test | `[TEST]` | Unit, integration, E2E tests |
| Docs | `[DOC]` | Documentation updates |
| DevOps | `[OPS]` | CI/CD, deployment, infra |

### Task Template

```markdown
# TASK: [ID] [Type] [Nome]

## Obiettivo
[Cosa deve essere implementato]

## Files da Modificare
- `path/to/file.rs` - [Descrizione modifica]
- `path/to/component.tsx` - [Descrizione modifica]

## Implementazione
1. Step 1
2. Step 2
3. Step 3

## Test Requirements
- [ ] Unit test per [funzione]
- [ ] Integration test per [flow]

## Definition of Done
- [ ] Codice implementato
- [ ] Test passano
- [ ] No nuovi warning
- [ ] PR review (se applicabile)
```

### Execution Order (CRITICAL PATH FIRST)

```
1. Database migrations (se necessarie)
2. Rust domain layer (aggregates, entities)
3. Rust repository layer
4. Rust service layer
5. Rust commands (IPC)
6. TypeScript types
7. React hooks
8. React components
9. Tests
10. Documentation
```

## 4. Quality Gates

### Gate 1: Pre-Implementation

- [ ] Story ha RICE score > 5
- [ ] Acceptance criteria sono SMART
- [ ] Dipendenze identificate
- [ ] Pattern architetturali selezionati

### Gate 2: Implementation

- [ ] Segue pattern da `fluxion-tauri-architecture.md`
- [ ] No anti-pattern utilizzati
- [ ] Codice formattato (`cargo fmt`, `prettier`)
- [ ] No warning compiler

### Gate 3: Testing

- [ ] Unit tests coprono nuove funzioni
- [ ] Integration test per flussi critici
- [ ] `cargo test` passa
- [ ] `pytest` passa (se voice-agent coinvolto)

### Gate 4: Review

- [ ] Self-review completata
- [ ] CLAUDE.md aggiornato
- [ ] Changelog entry (se release)

## 5. Audit Integration (levnikolaevich pattern)

### Parallel Audit Workers

```yaml
audits:
  security:
    - SQL injection check
    - XSS prevention
    - Secrets in code
  code_quality:
    - Dead code detection
    - Cyclomatic complexity
    - Code duplication (DRY ~70%)
  dependencies:
    - Outdated packages
    - Security vulnerabilities
    - License compliance
  architecture:
    - Pattern violations
    - Layer boundaries
    - IPC consistency
```

### Run Audit

```bash
# Security audit
cargo audit
npm audit

# Code quality
cargo clippy -- -D warnings
npx eslint src/ --max-warnings 0

# Dead code
cargo +nightly udeps

# Dependencies
cargo outdated
npm outdated
```

## 6. Documentation Pipeline

### Auto-Generated Docs

| Document | Trigger | Content |
|----------|---------|---------|
| `CLAUDE.md` | Session end | Project state |
| `CHANGELOG.md` | Release | Version changes |
| `API.md` | Command change | IPC documentation |

### Update Checklist

- [ ] `CLAUDE.md` → Stato progetto
- [ ] `docs/context/*.md` → Context tecnico
- [ ] `README.md` → Solo se breaking change

## Integration with External Skills

### levnikolaevich/claude-code-skills

```yaml
use_skills:
  - 101_documentation_pipeline  # Auto-gen CLAUDE.md
  - 201_epic_planning          # Epic breakdown
  - 301_story_validator        # RICE + DRY check
  - 401_task_executor          # Priority execution
  - 501_quality_pass           # Quality gates
  - 601_audit_parallel         # 9-worker audit
```

### alirezarezvani/claude-skills

```yaml
use_skills:
  - engineering/backend-engineer     # Rust patterns
  - engineering/frontend-engineer    # React patterns
  - engineering/qa-engineer          # Test strategies
  - product/product-manager-toolkit  # RICE prioritizer
```

## Workflow Commands

### Start New Feature

```
1. Create Epic in docs/epics/
2. Break down into Stories (RICE scored)
3. Create Tasks for each Story
4. Execute Tasks (CRITICAL PATH FIRST)
5. Quality gates at each stage
6. Update CLAUDE.md
```

### Quick Fix / Bug

```
1. Identify root cause
2. Create single Task
3. Implement fix
4. Add regression test
5. Update CLAUDE.md
```

### Refactoring

```
1. Document current state
2. Create refactor Story
3. DRY check (~70% threshold)
4. Implement in small PRs
5. Ensure no behavior change
6. Update architecture docs
```

---

## Checklist per Nuova Feature

```markdown
## Pre-Implementation
- [ ] Epic definito con success metrics
- [ ] Stories con RICE score
- [ ] Tasks ordinati per CRITICAL PATH
- [ ] Pattern architetturali identificati

## Implementation
- [ ] Database migration (se necessaria)
- [ ] Rust backend (domain → repo → service → command)
- [ ] TypeScript types
- [ ] React hooks + components
- [ ] E2E selectors (data-testid)

## Quality
- [ ] cargo test passa
- [ ] pytest passa
- [ ] No warning
- [ ] Audit completato

## Documentation
- [ ] CLAUDE.md aggiornato
- [ ] API.md aggiornato (se nuovi commands)
- [ ] CHANGELOG.md (se release)
```
