---
paths:
  - "src/**"
  - "*.tsx"
  - "*.ts"
  - "!src-tauri/**"
---

# React Frontend Rules

## Stack
- React 19 + TypeScript + Vite
- Tailwind CSS 3.4 + shadcn/ui components
- State: React Query (server) + Zustand (UI)

## Patterns
- IPC: `const data = await invoke<Type>('command_name', { params })`
- Hooks: `src/hooks/use-*.ts` - one per domain (useCliente, useAppuntamenti)
- Pages: `src/pages/*.tsx` - route components
- Components: `src/components/` - shadcn/ui based

## Rules
- Always TypeScript, never JavaScript
- Always type `invoke<T>()` calls
- Always add `data-testid` on interactive elements for E2E
- Use React Query `useQuery`/`useMutation` for all backend calls
- Use Zustand for UI-only state (sidebar, modals)

## Pre-commit
```bash
npm run type-check   # tsc --noEmit
npm run lint         # eslint
```

## Design System
Reference: `docs/FLUXION-DESIGN-BIBLE.md`
