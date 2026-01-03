# FLUXION - Agent-Specific Guidelines

**Purpose**: Ensure coherence across specialized agents
**Owner**: Claude Code CEO (Master Orchestrator)

---

## 🎯 GENERAL RULES (All Agents)

1. **Always read** relevant context file (`docs/context/*.md`) BEFORE starting work
2. **Never duplicate** architectural decisions - check `.parlant/decision-log.md` first
3. **Log critical decisions** in session file (`docs/sessions/`)
4. **Follow established patterns**:
   - Backend: DDD (domain → service → infra)
   - Frontend: Component → Hook → API call (TanStack Query)
   - Naming: PascalCase components, camelCase functions, snake_case Rust
5. **Test first**: Write tests before implementation (TDD)
6. **Git workflow**: Never skip commit after milestone
7. **No breaking changes** without architect approval

---

## 🦀 rust-backend Agent

**Context File**: `docs/context/CLAUDE-BACKEND.md`

### Domain Layer
- **Pure business logic** - NO database, NO I/O
- Use `Result<T, DomainError>` for all fallible operations
- State transitions via methods (not public field mutation)
- Value objects immutable

### Service Layer
- Orchestrate domain + infra
- Wrap `RepositoryError` in `ServiceError` (use `#[from]`)
- Async all the way (no blocking in async context)
- Validation via `ValidationService`

### Repository Layer (Infra)
- Implement `AppuntamentoRepository` trait
- Use SQLx with compile-time checks (`sqlx::query!`)
- Soft delete pattern (`deleted_at IS NULL`)
- Transactions for multi-step writes

### Testing
- **Domain tests**: Pure unit tests (no DB)
- **Service tests**: Use `#[tokio::test]` + `.await` (not `futures::executor`)
- **Integration tests**: Real SQLite DB on filesystem (`tests/` dir)
- Coverage target: 95%

### Naming Conventions
```rust
// Structs: PascalCase
struct AppuntamentoAggregate { ... }

// Functions: snake_case
async fn valida_appuntamento(...) { ... }

// Traits: PascalCase
trait AppuntamentoRepository { ... }

// Errors: PascalCase + descriptive
pub enum DomainError {
    DataPassata { ... },
    ConflictOperatore { ... },
}
```

---

## ⚛️ react-frontend Agent

**Context File**: `docs/context/CLAUDE-FRONTEND.md`

### Component Structure
```tsx
// 1. Imports
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Types
interface Props { ... }

// 3. Component
export function ComponentName({ prop }: Props) {
  // 3a. State
  const [state, setState] = useState();

  // 3b. Queries/Mutations
  const { data } = useQuery(...);

  // 3c. Handlers
  const handleClick = () => { ... };

  // 3d. Render
  return <div>...</div>;
}
```

### State Management
- **Server state**: TanStack Query (queries + mutations)
- **Local state**: useState/useReducer
- **Form state**: React Hook Form + Zod validation

### Styling
- **Tailwind CSS 4** - utility classes
- **shadcn/ui components** - consistent design
- **Design tokens**: from `CLAUDE-DESIGN-SYSTEM.md`
- NO inline styles, NO CSS files

### API Calls
- Always via `@tauri-apps/api/core` (`invoke`)
- Wrap in TanStack Query hooks (`useQuery`, `useMutation`)
- Optimistic updates for mutations
- Error handling with toast notifications

---

## 🔧 devops Agent

**Context File**: `docs/context/CLAUDE-DEPLOYMENT.md`

### GitHub Actions
- **Parallel jobs** whenever possible
- **Cache aggressively**: cargo, npm, target/
- **Fail-fast: false** for matrix builds
- **Feature flags**: development, production, testing
- **Timeout**: 15min max per job

### CI/CD Workflow
```yaml
test-backend:
  strategy:
    matrix:
      os: [ubuntu-latest, macos-latest, windows-latest]
  steps:
    - Build frontend FIRST (Tauri needs dist/)
    - Run domain tests
    - Run service tests (with DB)
    - Run integration tests
```

### Build Profiles
- **Debug**: Fast compile, slow runtime
- **Release**: Slow compile, fast runtime + optimizations
- **Test**: Debug + test features enabled

### Dependency Updates
- `cargo update` monthly
- `npm audit fix` weekly
- Pin critical versions (Tauri, React)

---

## 🏗️ architect Agent

**Context File**: `docs/context/CLAUDE-INDEX.md`

### Decision Framework
1. **Problem**: What are we solving?
2. **Options**: List 2-3 alternatives
3. **Trade-offs**: Pros/cons per option
4. **Decision**: Pick ONE with justification
5. **Log**: Create ADR in `.parlant/decision-log.md`

### Architectural Principles
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It (no over-engineering)
- **DRY**: Don't Repeat Yourself (but prefer duplication over wrong abstraction)
- **Separation of Concerns**: Layer isolation (domain ≠ infra)
- **Testability**: If can't test, redesign

### Technology Stack (Locked)
- **Backend**: Rust + Tauri 2.x + SQLite + SQLx
- **Frontend**: React 19 + TypeScript + TanStack Query + Zod
- **Styling**: Tailwind CSS 4 + shadcn/ui
- **Build**: GitHub Actions + cargo + npm
- **Testing**: cargo test + Playwright (E2E)

**No new major dependencies** without CEO approval.

---

## 🔍 code-reviewer Agent

**Agent File**: `.claude/agents/code-reviewer.md`

### Review Checklist
- [ ] Tests added/updated?
- [ ] Error handling complete?
- [ ] Types correct (no `any` unless unavoidable)?
- [ ] Security: No SQL injection, XSS, command injection?
- [ ] Performance: No N+1 queries, unnecessary clones?
- [ ] Naming: Clear, consistent with codebase?
- [ ] Documentation: Comments only where needed (code self-documents)

### Code Smells
❌ **Reject**:
- `unwrap()` in production code (use `?` or handle explicitly)
- `any` types in TypeScript (use proper types)
- Magic numbers (use constants)
- Commented-out code (delete it, git has history)
- Nested ternaries (use if/else)

✅ **Approve**:
- Early returns over deep nesting
- Small, focused functions (<50 lines)
- Meaningful variable names
- Consistent error handling

---

## 🎨 ui-designer Agent

**Context Files**:
- `docs/context/CLAUDE-DESIGN-SYSTEM.md`
- `docs/FLUXION-DESIGN-BIBLE.md`

### Design Tokens
```typescript
// Colors
--navy-900: #0A1A2F  // Primary dark
--cyan-500: #06B6D4   // Accent
--teal-600: #0D9488   // Success
--purple-600: #9333EA // Info

// Spacing (Tailwind)
gap-4, p-6, mt-8, mb-12

// Typography
text-sm, text-base, text-lg, font-semibold
```

### Component Guidelines
- Use shadcn/ui as base
- Extend with Tailwind utilities
- Mobile-first responsive
- Dark mode support (future)

---

## 📝 Session Log Template

Every agent must create session log in `docs/sessions/` after milestone:

```markdown
# Sessione: [Descrizione Milestone]

**Data**: YYYY-MM-DDTHH:MM:SS
**Fase**: [numero fase]
**Agente**: [agent-id]

## Obiettivo
[Cosa dovevi fare]

## Modifiche
- File 1 (modificato/creato/eliminato)
- File 2 (modificato/creato/eliminato)

## Decisioni Architetturali
- [Se applicabile, link ad ADR]

## Test
- [Risultati test]

## Note
- [Problemi risolti, caveat, TODO futuri]

**Status**: ✅ COMPLETATO | 🚧 PARZIALE | ❌ BLOCCATO
```

---

**Last Updated**: 2026-01-03T19:20:00
**Next Review**: After Fase 4 completion
