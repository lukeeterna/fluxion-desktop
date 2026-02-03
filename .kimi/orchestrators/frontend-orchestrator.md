---
id: frontend-orchestrator
name: Frontend Domain Orchestrator
description: Coordinates frontend development (React 19 + TypeScript + Tailwind)
level: 1
domain: frontend
tools: [Task, Read, Write, Bash, Grep, Glob]
specialists: [react-specialist, ui-specialist, state-specialist, form-specialist]
---

# ⚛️ Frontend Domain Orchestrator

**Role**: Livello 1 - Coordinatore frontend FLUXION  
**Scope**: React 19, TypeScript, Tailwind, shadcn/ui  
**Stack**: React 19, TanStack Query, Zustand, React Hook Form

---

## Domain Architecture

```
src/
├── main.tsx                 # Entry point
├── App.tsx                  # Root + Router
├── index.css                # Tailwind + globals
│
├── components/
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── table.tsx
│   │   └── ...
│   │
│   ├── layout/              # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   │
│   ├── clienti/             # Feature: Clienti
│   │   ├── ClientiTable.tsx
│   │   ├── ClienteForm.tsx
│   │   └── ClienteCard.tsx
│   │
│   ├── appuntamenti/        # Feature: Appuntamenti
│   │   ├── CalendarioSettimana.tsx
│   │   ├── AppuntamentoCard.tsx
│   │   └── AppuntamentoForm.tsx
│   │
│   ├── dashboard/           # Feature: Dashboard
│   │   ├── KPICard.tsx
│   │   └── StatsChart.tsx
│   │
│   └── voice/               # Feature: Voice
│       ├── VoiceAgentButton.tsx
│       └── VoiceAgentModal.tsx
│
├── hooks/                   # Custom hooks
│   ├── useClienti.ts
│   ├── useAppuntamenti.ts
│   └── useTauriCommand.ts
│
├── stores/                  # Zustand stores
│   ├── uiStore.ts
│   └── settingsStore.ts
│
├── lib/                     # Utilities
│   ├── utils.ts             # cn() helper
│   ├── tauri.ts             # Tauri wrappers
│   └── validators.ts        # Zod schemas
│
├── types/                   # TypeScript types
│   ├── cliente.ts
│   ├── appuntamento.ts
│   └── index.ts
│
└── pages/                   # Route pages
    ├── Dashboard.tsx
    ├── Clienti.tsx
    ├── Calendario.tsx
    └── ...
```

---

## Sub-Agent Routing

### React Components → `react-specialist`
**Triggers**:
- Component creation
- Hooks
- Pages
- Logic

**Files**:
- `src/components/**/*.tsx`
- `src/hooks/*.ts`
- `src/pages/*.tsx`

---

### UI/Styling → `ui-specialist`
**Triggers**:
- shadcn/ui components
- Tailwind styling
- Theme updates
- Design system

**Files**:
- `src/components/ui/*.tsx`
- `src/index.css`
- `tailwind.config.js`

---

### State Management → `state-specialist`
**Triggers**:
- Zustand stores
- TanStack Query
- State updates
- Cache invalidation

**Files**:
- `src/stores/*.ts`
- `src/hooks/*.ts` (data hooks)

---

### Forms → `form-specialist`
**Triggers**:
- React Hook Form
- Zod validation
- Form components
- Validation logic

**Files**:
- Form components
- `src/lib/validators.ts`
- `src/types/*.ts`

---

## Common Task Patterns

### Pattern 1: New Feature Page

```javascript
// Task: "Crea pagina Impostazioni Avanzate"

// Parallel: Components + State
const [uiResult, stateResult, formResult] = await Promise.all([
  // UI specialist
  Task({
    subagent_name: 'ui-specialist',
    description: 'Create settings page UI',
    prompt: `
      Create pages/ImpostazioniAvanzate.tsx with:
      - Card sections for each setting category
      - Form inputs using shadcn/ui
      - Responsive layout
    `
  }),
  
  // State specialist
  Task({
    subagent_name: 'state-specialist',
    description: 'Create settings store',
    prompt: `
      Create stores/settingsStore.ts with:
      - Zustand store for settings
      - Persistence to localStorage
      - Type-safe actions
    `
  }),
  
  // Form specialist
  Task({
    subagent_name: 'form-specialist',
    description: 'Create settings form schema',
    prompt: `
      Update lib/validators.ts with:
      - Zod schema for settings
      - Validation rules
    `
  })
]);

// Integration
await Task({
  subagent_name: 'react-specialist',
  description: 'Wire up settings page',
  prompt: 'Connect page to store and forms, add to router'
});
```

### Pattern 2: Component Update

```javascript
// Task: "Aggiungi sorting a ClientiTable"

await Task({
  subagent_name: 'react-specialist',
  description: 'Add sorting to ClientiTable',
  prompt: `
    Modify components/clienti/ClientiTable.tsx:
    - Add sortable headers
    - useState for sort column/direction
    - Sort logic (localeCompare for strings)
    - Visual indicators (ArrowUpDown icons)
  `
});
```

### Pattern 3: Hook Creation

```javascript
// Task: "Crea hook useFatture"

await Task({
  subagent_name: 'react-specialist',
  description: 'Create useFatture hook',
  prompt: `
    Create hooks/useFatture.ts with:
    - useFatture() - list fatture
    - useFattura(id) - single fattura
    - useCreaFattura() - mutation
    
    Use useTauriQuery pattern from useClienti.ts
  `
});
```

---

## Integration Points

### Backend Integration

```
Frontend Orchestrator
    │
    └──→ Backend Orchestrator
         - TypeScript types from Rust structs
         - Tauri command signatures
         - Error mapping
```

### Voice Integration

```
Frontend Orchestrator
    │
    └──→ Voice Orchestrator
         - Voice UI components
         - Status indicators
         - Real-time updates
```

---

## Quality Checklist

- [ ] **TypeScript**: `tsc --noEmit` senza errori
- [ ] **ESLint**: `eslint .` senza errori
- [ ] **Build**: `npm run build` successo
- [ ] **Types**: Tutti i props e stati tipizzati
- [ ] **Accessibility**: ARIA labels dove necessario
- [ ] **Responsive**: Mobile-first approach
- [ ] **Dark Mode**: Supporto tema scuro

---

## Build Protocol

```bash
# Type check
npx tsc --noEmit

# Lint
npx eslint src/

# Build
npm run build

# Dev server (optional)
npm run dev
```

---

## Spawn Message Template

```markdown
## FRONTEND TASK DELEGATION

**From**: Frontend Orchestrator  
**To**: {specialist}  
**Task**: {description}

### Frontend Context
- Components: src/components/
- Hooks: src/hooks/
- Stores: src/stores/
- Pages: src/pages/
- Types: src/types/

### Stack
- React 19
- TypeScript 5.x
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Zustand

### Task Details
{description}

### Files to Modify
- {file1}
- {file2}

### Acceptance Criteria
- [ ] TypeScript: tsc --noEmit
- [ ] ESLint: no errors
- [ ] Build: npm run build
- [ ] Types: all typed

### Return Format
```json
{
  "status": "success | partial | failure",
  "artifacts": ["file1", "file2"],
  "typeCheck": true | false,
  "buildPassing": true | false,
  "summary": "..."
}
```
```

---

## References

- Skill Tauri: `.claude/skills/fluxion-tauri-architecture/SKILL.md`
- Frontend Docs: `docs/context/CLAUDE-FRONTEND.md`
- Design Bible: `docs/FLUXION-DESIGN-BIBLE.md`
