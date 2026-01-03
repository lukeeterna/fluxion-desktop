# FLUXION - Architectural Decision Log

**Maintained by**: Claude Code CEO (Master Orchestrator)
**Purpose**: Track critical architectural decisions for cross-session coherence
**Format**: ADR (Architecture Decision Record)

---

## ADR-001: Domain-Driven Design Layer (2026-01-02)

**Status**: ✅ Implemented
**Context**: Bisogno di separare logica business da infrastruttura
**Decision**: Implementare DDD con 3 layer:
- **Domain**: Pure business logic (aggregate, value objects, errors)
- **Service**: Orchestration + validation
- **Infra**: Repository pattern (SQLite via SQLx)

**Consequences**:
- ✅ PRO: Testabilità, separazione concerns, evoluzione indipendente layer
- ❌ CON: Più boilerplate iniziale (mitigato con code generation)

**Implemented by**: rust-backend agent
**Session**: 2026-01-02-14-30-ddd-refactoring.md

---

## ADR-002: State Machine Workflow Appuntamenti (2026-01-02)

**Status**: ✅ Implemented
**Context**: Gestione transizioni stato appuntamenti complex
**Decision**: State machine con 8 stati + regole transizione:
```
Bozza → Proposta → InAttesaCliente/InAttesaOperatore → Confermato → Completato
        ↓
        RifiutatoDaCliente/RifiutatoDaOperatore
        ↓
        Cancellato
```

**Consequences**:
- ✅ PRO: Transizioni esplicite, audit trail, validazione per stato
- ❌ CON: Più complesso di semplice CRUD

**Implemented by**: rust-backend agent
**Session**: 2026-01-02-14-30-ddd-refactoring.md

---

## ADR-003: 3-Layer Validation System (2026-01-02)

**Status**: ✅ Implemented
**Context**: Bilanciare rigidità regole con flessibilità operatore
**Decision**: 3 livelli validazione:
1. **Hard Blocks**: Errori critici (data passata, overlap, mezzanotte wrap)
2. **Warnings**: Validabili con override (fuori orario, festività)
3. **Suggestions**: Ottimizzazioni UX (durata consigliata)

**Consequences**:
- ✅ PRO: Flessibilità con audit, UX migliore, override tracciato
- ❌ CON: Complessità validazione, UI più articolata

**Implemented by**: rust-backend + react-frontend agents
**Session**: 2026-01-02-14-30-ddd-refactoring.md

---

## ADR-004: GitHub Actions Autonomous Log Acquisition (2026-01-03)

**Status**: ✅ Implemented
**Context**: Loop infiniti debug CI/CD, dipendenza utente per log
**Decision**: Implementare acquisizione autonoma log via GitHub API:
- API pubblica per metadata job (status, steps, conclusion)
- Identificazione step fallito senza token admin
- Fallback a request screenshot se serve log completo

**Consequences**:
- ✅ PRO: CEO agent autonomo, fix più rapidi, zero loop
- ❌ CON: Log testuali completi richiedono ancora token admin (future)

**Implemented by**: claude-code-ceo
**Session**: 2026-01-03-19-00-autonomous-log-acquisition.md

---

## ADR-005: Parlant Integration for Cross-Session Coherence (2026-01-03)

**Status**: 🚧 In Progress
**Context**: Perdita contesto tra sessioni, decisioni duplciate
**Decision**: Integrare Parlant framework per:
- Persistent memory (docs/sessions/)
- Agent handoff guidelines
- Decision log automatico
- Coherence rules enforcement

**Consequences**:
- ✅ PRO: Coerenza architetturale, context retention, decisioni tracciabili
- ❌ CON: Setup iniziale, training agenti su guidelines

**Implemented by**: claude-code-ceo
**Session**: 2026-01-03-19-00-parlant-integration.md

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title] (YYYY-MM-DD)

**Status**: 🚧 Proposed | ✅ Implemented | ❌ Rejected | 🔄 Superseded
**Context**: [Problema da risolvere]
**Decision**: [Scelta fatta]

**Consequences**:
- ✅ PRO: [Vantaggi]
- ❌ CON: [Svantaggi]

**Implemented by**: [agente]
**Session**: [file sessione]
```

---

**Last updated**: 2026-01-03T19:15:00
**Next review**: Before Fase 4 kickoff
