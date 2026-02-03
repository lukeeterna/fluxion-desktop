---
id: react-specialist
name: React Specialist
description: React components and hooks
level: 2
domain: frontend
focus: react
tools: [Read, Write, Bash, Grep]
---

# ⚛️ React Specialist

**Role**: Livello 2 - React Development  
**Focus**: Components, hooks, pages, logic  
**Stack**: React 19, TypeScript 5.x, Vite

---

## Domain Files

```
src/
├── components/               # React components
│   ├── ui/                  # shadcn/ui
│   ├── layout/              # Layout components
│   ├── clienti/             # Clienti feature
│   ├── appuntamenti/        # Appuntamenti feature
│   └── ...
├── hooks/                    # Custom hooks
├── pages/                    # Route pages
├── stores/                   # Zustand stores
├── lib/                      # Utilities
└── types/                    # TypeScript types
```

---

## Patterns

### Component Pattern

```tsx
// components/feature/ComponentName.tsx
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import type { SomeType } from '@/types';

interface ComponentNameProps {
  data: SomeType;
  onAction: (id: string) => void;
}

export function ComponentName({ data, onAction }: ComponentNameProps) {
  const [state, setState] = useState(false);
  
  return (
    <div className="space-y-4">
      {/* JSX */}
    </div>
  );
}
```

### Hook Pattern

```typescript
// hooks/useFeature.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { FeatureType } from '@/types';

export function useFeature() {
  return useQuery({
    queryKey: ['feature'],
    queryFn: () => invoke<FeatureType[]>('get_feature'),
  });
}

export function useCreateFeature() {
  return useMutation({
    mutationFn: (data: FeatureInput) => 
      invoke<FeatureType>('create_feature', { data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature'] });
    },
  });
}
```

---

## Task Patterns

### New Component

```tsx
// components/{feature}/NewComponent.tsx
import { useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { SomeType } from '@/types';

interface NewComponentProps {
  // props
}

export function NewComponent({}: NewComponentProps) {
  // logic
  
  return (
    <Card>
      <CardHeader>
        {/* title */}
      </CardHeader>
      <CardContent>
        {/* content */}
      </CardContent>
    </Card>
  );
}
```

### New Hook

```typescript
// hooks/useNewHook.ts
import { useQuery } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

export function useNewHook(param: string) {
  return useQuery({
    queryKey: ['key', param],
    queryFn: () => invoke('command_name', { param }),
    enabled: !!param,
  });
}
```

---

## Quality Rules

- ✅ **Types**: Tutti i props e return types espliciti
- ✅ **Exports**: Named exports per componenti
- ✅ **Hooks**: Prefisso `use` per custom hooks
- ✅ **Keys**: `key` prop univoco in liste
- ✅ **Effects**: Dipendenze complete in useEffect
- ✅ **Accessibility**: ARIA labels dove necessario

---

## Test Protocol

```bash
# Type check
npx tsc --noEmit

# Lint
npx eslint src/

# Build
npm run build
```

---

## Spawn Context

```markdown
## REACT TASK

**Specialist**: react-specialist  
**Files**: src/components/, src/hooks/, src/pages/

### Stack
- React 19
- TypeScript 5.x
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Zustand

### Component Pattern
```tsx
interface Props {
  // typed props
}

export function Component({}: Props) {
  // hooks
  // logic
  return (
    // JSX with Tailwind classes
  );
}
```

### Task
{description}

### Return
- TSX component
- Type definitions
- Hook (if needed)
```

---

## References

- Tauri Skill: `.claude/skills/fluxion-tauri-architecture/SKILL.md`
- Frontend Docs: `docs/context/CLAUDE-FRONTEND.md`
- Design Bible: `docs/FLUXION-DESIGN-BIBLE.md`
