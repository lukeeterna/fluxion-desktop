# Frontend Quality Checklist

**Versione**: 1.0
**Ultimo aggiornamento**: 2026-01-03

Checklist obbligatoria per ogni PR/commit frontend (React 19 + TypeScript).

---

## 1. Architettura e Separazione Concerns

- [ ] **No Business Logic in UI**: Solo presentazione e user interaction
- [ ] **Custom Hooks**: Logica riutilizzabile in `src/hooks/`
- [ ] **Feature-Based Structure**: Organizzazione per feature, non per tipo file
- [ ] **TanStack Query**: TUTTE le chiamate Tauri via `useQuery`/`useMutation`
- [ ] **No Prop Drilling**: Usa Context o state management per dati globali

**Esempio CORRETTO**:
```typescript
// ✅ Feature-based structure
src/
  features/
    appuntamenti/
      components/
        AppuntamentoDialog.tsx
        AppuntamentoCard.tsx
      hooks/
        useAppuntamenti.ts
        useConfermaAppuntamento.ts
      types/
        appuntamento.types.ts

// ✅ Custom hook con TanStack Query
export function useAppuntamenti() {
  return useQuery({
    queryKey: ['appuntamenti'],
    queryFn: async () => {
      const result = await invoke<Appuntamento[]>('get_appuntamenti');
      return result;
    },
  });
}

// ✅ Component usa hook
export function AppuntamentiList() {
  const { data: appuntamenti, isLoading } = useAppuntamenti();

  if (isLoading) return <Skeleton />;
  return <>{appuntamenti.map(app => <AppuntamentoCard key={app.id} data={app} />)}</>;
}
```

**Esempio SBAGLIATO**:
```typescript
// ❌ Business logic in component
export function AppuntamentoDialog() {
  const [error, setError] = useState('');

  const handleSubmit = async (data: AppuntamentoDto) => {
    // ❌ Validazione business logic in UI
    if (new Date(data.data_ora) < new Date()) {
      setError('Appuntamento nel passato');
      return;
    }

    // ❌ Chiamata diretta invoke (no TanStack Query)
    await invoke('crea_appuntamento', { dto: data });
  };
}
```

---

## 2. TypeScript

- [ ] **Strict Mode**: `"strict": true` in `tsconfig.json`
- [ ] **No `any`**: Usa tipi espliciti o `unknown`
- [ ] **Zod Schemas**: Validazione runtime per dati da backend
- [ ] **Type Guards**: Usa type guards per narrowing
- [ ] **Enums vs Union Types**: Preferire union types letterali

**Esempio CORRETTO**:
```typescript
// ✅ Zod schema + inferred type
import { z } from 'zod';

export const AppuntamentoSchema = z.object({
  id: z.string().uuid(),
  cliente_id: z.string(),
  operatore_id: z.string(),
  data_ora: z.string().datetime(),
  stato: z.enum(['Bozza', 'Proposta', 'InAttesaOperatore', 'Confermato', 'Rifiutato', 'Completato', 'Cancellato']),
});

export type Appuntamento = z.infer<typeof AppuntamentoSchema>;

// ✅ Runtime validation
export function useAppuntamenti() {
  return useQuery({
    queryKey: ['appuntamenti'],
    queryFn: async () => {
      const result = await invoke<unknown>('get_appuntamenti');
      return z.array(AppuntamentoSchema).parse(result); // Valida runtime
    },
  });
}
```

**Esempio SBAGLIATO**:
```typescript
// ❌ any ovunque
export function useAppuntamenti(): any {
  return useQuery({
    queryKey: ['appuntamenti'],
    queryFn: async () => {
      return await invoke('get_appuntamenti'); // Type: any
    },
  });
}
```

---

## 3. State Management

- [ ] **Server State**: TanStack Query (NO useState per dati backend)
- [ ] **UI State**: useState/useReducer per modals, forms
- [ ] **Global State**: Context API (evitare Redux se possibile)
- [ ] **Form State**: React Hook Form + Zod resolver
- [ ] **Optimistic Updates**: Usa `onMutate` di TanStack Query

**Esempio CORRETTO**:
```typescript
// ✅ Server state con TanStack Query
export function useConfermaAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoke('conferma_appuntamento', { id }),

    // Optimistic update
    onMutate: async (id) => {
      await queryClient.cancelQueries(['appuntamenti']);
      const previousData = queryClient.getQueryData(['appuntamenti']);

      queryClient.setQueryData(['appuntamenti'], (old: Appuntamento[]) =>
        old.map(app => app.id === id ? { ...app, stato: 'Confermato' } : app)
      );

      return { previousData };
    },

    onError: (err, id, context) => {
      queryClient.setQueryData(['appuntamenti'], context?.previousData);
    },

    onSettled: () => {
      queryClient.invalidateQueries(['appuntamenti']);
    },
  });
}

// ✅ UI state locale
export function AppuntamentoDialog({ open, onClose }: Props) {
  const [step, setStep] = useState<'select-client' | 'select-service' | 'select-time'>('select-client');

  return (
    <Dialog open={open} onOpenChange={onClose}>
      {step === 'select-client' && <ClientStep onNext={() => setStep('select-service')} />}
      {/* ... */}
    </Dialog>
  );
}
```

**Esempio SBAGLIATO**:
```typescript
// ❌ Server state in useState
export function AppuntamentiList() {
  const [appuntamenti, setAppuntamenti] = useState<Appuntamento[]>([]);

  useEffect(() => {
    invoke<Appuntamento[]>('get_appuntamenti').then(setAppuntamenti);
  }, []);

  // ❌ Problema: no caching, no refetch, no error handling
}
```

---

## 4. Form Handling

- [ ] **React Hook Form**: TUTTE le form usano `useForm`
- [ ] **Zod Resolver**: Validazione schema con `zodResolver`
- [ ] **Controlled Components**: Usa `Controller` per componenti custom
- [ ] **Error Display**: Mostra `errors[field]?.message`
- [ ] **Submit Disabled**: Disabilita durante `isSubmitting`

**Esempio CORRETTO**:
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const AppuntamentoFormSchema = z.object({
  cliente_id: z.string().min(1, 'Cliente obbligatorio'),
  data_ora: z.string().datetime('Data/ora non valida'),
});

type FormData = z.infer<typeof AppuntamentoFormSchema>;

export function AppuntamentoForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(AppuntamentoFormSchema),
  });

  const mutation = useCreaAppuntamento();

  const onSubmit = (data: FormData) => {
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('cliente_id')} />
      {errors.cliente_id && <p className="text-red-500">{errors.cliente_id.message}</p>}

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Salvataggio...' : 'Salva'}
      </Button>
    </form>
  );
}
```

---

## 5. UI/UX

- [ ] **Loading States**: Skeleton/spinner per async operations
- [ ] **Error States**: Toast/alert per errori
- [ ] **Empty States**: Messaggio + CTA quando lista vuota
- [ ] **Disabled States**: Disabilita bottoni durante operazioni
- [ ] **Accessibility**: ARIA labels, keyboard navigation

**Esempio CORRETTO**:
```typescript
export function AppuntamentiList() {
  const { data, isLoading, error } = useAppuntamenti();

  if (isLoading) return <Skeleton count={5} />;

  if (error) return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription>Errore caricamento appuntamenti</AlertDescription>
    </Alert>
  );

  if (data.length === 0) return (
    <EmptyState
      icon={Calendar}
      title="Nessun appuntamento"
      description="Inizia creando il primo appuntamento"
      action={<Button onClick={openDialog}>Crea Appuntamento</Button>}
    />
  );

  return <>{data.map(app => <AppuntamentoCard key={app.id} data={app} />)}</>;
}
```

---

## 6. Performance

- [ ] **Memo Components**: `React.memo` per component pesanti
- [ ] **useMemo/useCallback**: Per calcoli costosi e funzioni passate come prop
- [ ] **Code Splitting**: `React.lazy` per route grandi
- [ ] **Virtualization**: `react-window` per liste lunghe (100+ items)
- [ ] **Image Optimization**: Lazy load immagini

**Esempio CORRETTO**:
```typescript
// ✅ Memoization
const ExpensiveComponent = React.memo(({ data }: Props) => {
  const processedData = useMemo(() => {
    return data.map(item => heavyComputation(item));
  }, [data]);

  return <>{processedData.map(...)}</>;
});

// ✅ Code splitting
const AppuntamentiPage = React.lazy(() => import('./pages/Appuntamenti'));

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <AppuntamentiPage />
    </Suspense>
  );
}
```

---

## 7. Styling (Tailwind CSS 4)

- [ ] **Design Tokens**: Usa variabili CSS da `globals.css`
- [ ] **Responsive**: Mobile-first (`sm:`, `md:`, `lg:`)
- [ ] **Dark Mode**: Supporta `dark:` variants
- [ ] **Palette Custom**: Usa colori FLUXION (navy, cyan, teal, purple)
- [ ] **No Magic Numbers**: Usa spacing scale Tailwind

**Esempio CORRETTO**:
```tsx
// ✅ Design tokens + responsive
<div className="bg-navy-50 dark:bg-navy-900 p-4 sm:p-6 md:p-8">
  <h2 className="text-2xl font-bold text-navy-900 dark:text-white">
    Appuntamenti
  </h2>
</div>

// globals.css
:root {
  --navy-50: #f0f4f8;
  --navy-900: #0a1929;
}
```

**Esempio SBAGLIATO**:
```tsx
// ❌ Inline styles + magic numbers
<div style={{ backgroundColor: '#f0f4f8', padding: '23px' }}>
  <h2 style={{ fontSize: '24px' }}>Appuntamenti</h2>
</div>
```

---

## 8. Testing

- [ ] **Vitest**: Unit test per hooks e utilities
- [ ] **React Testing Library**: Test componenti
- [ ] **User-Centric Tests**: Test comportamento, non implementazione
- [ ] **Mock Tauri**: Mocka `invoke` per test isolati

**Esempio CORRETTO**:
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { invoke } from '@tauri-apps/api/core';

vi.mock('@tauri-apps/api/core');

test('mostra lista appuntamenti', async () => {
  vi.mocked(invoke).mockResolvedValue([
    { id: '1', cliente_id: 'c1', stato: 'Confermato' },
  ]);

  render(<AppuntamentiList />);

  await waitFor(() => {
    expect(screen.getByText(/Confermato/i)).toBeInTheDocument();
  });
});
```

---

## 9. Error Handling

- [ ] **Error Boundaries**: Wrappa route in `ErrorBoundary`
- [ ] **Toast Notifications**: `sonner` per feedback utente
- [ ] **Retry Logic**: TanStack Query retry automatico (max 3)
- [ ] **User-Friendly Messages**: NO stack trace in UI

**Esempio CORRETTO**:
```typescript
export function useCreaAppuntamento() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: (dto: AppuntamentoDto) => invoke('crea_appuntamento', { dto }),

    onError: (error) => {
      toast({
        title: 'Errore',
        description: 'Impossibile creare appuntamento. Riprova.',
        variant: 'destructive',
      });
    },

    onSuccess: () => {
      toast({
        title: 'Successo',
        description: 'Appuntamento creato',
      });
    },
  });
}
```

---

## Checklist Pre-Commit

Prima di ogni `git commit`:

```bash
# 1. Type check
npm run type-check

# 2. Lint
npm run lint

# 3. Test
npm run test

# 4. Build
npm run build
```

---

## Severity Levels

- **CRITICAL** ❌: XSS vulnerability, `any` types, no error handling
- **HIGH** ⚠️: Missing loading states, no validation, prop drilling
- **MEDIUM** 💡: No memoization, inline styles, magic strings
- **LOW** ℹ️: Missing comments, inconsistent naming

**Regola**: CRITICAL blocca merge. HIGH richiede fix in 24h.
