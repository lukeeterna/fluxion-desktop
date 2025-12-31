# ⚛️ FLUXION Frontend - React + TypeScript

> Architettura frontend: React 19, TypeScript 5, TanStack Query, Zustand

---

## 📋 Indice

1. [Stack Tecnologico](#stack-tecnologico)
2. [Struttura Directory](#struttura-directory)
3. [TypeScript Types](#typescript-types)
4. [Custom Hooks](#custom-hooks)
5. [State Management](#state-management)
6. [Tauri Integration](#tauri-integration)
7. [Componenti Pattern](#componenti-pattern)

---

## Stack Tecnologico

| Pacchetto | Versione | Uso |
|-----------|----------|-----|
| **React** | 19.x | UI Framework |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.x | Styling |
| **shadcn/ui** | latest | Component library |
| **TanStack Query** | 5.x | Server state |
| **Zustand** | 4.x | Client state |
| **React Router** | 6.x | Routing |
| **Lucide React** | latest | Icons |
| **date-fns** | 3.x | Date utilities |
| **React Hook Form** | 7.x | Forms |
| **Zod** | 3.x | Validation |

### package.json Dependencies

```json
{
  "dependencies": {
    "@tauri-apps/api": "^2.0.0",
    "@tauri-apps/plugin-sql": "^2.0.0",
    "@tauri-apps/plugin-dialog": "^2.0.0",
    "@tanstack/react-query": "^5.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.0",
    "lucide-react": "^0.300.0",
    "date-fns": "^3.0.0",
    "date-fns-tz": "^2.0.0",
    "react-hook-form": "^7.48.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "class-variance-authority": "^0.7.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^4.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## Struttura Directory

```
src/
├── main.tsx                 # Entry point
├── App.tsx                  # Root component + Router
├── index.css                # Global styles + Tailwind
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
│   │   ├── MainLayout.tsx
│   │   └── PageContainer.tsx
│   │
│   ├── clienti/             # Feature: Clienti
│   │   ├── ClientiTable.tsx
│   │   ├── ClienteForm.tsx
│   │   ├── ClienteCard.tsx
│   │   └── ClienteSearch.tsx
│   │
│   ├── appuntamenti/        # Feature: Appuntamenti
│   │   ├── CalendarioSettimana.tsx
│   │   ├── AppuntamentoCard.tsx
│   │   ├── AppuntamentoForm.tsx
│   │   └── SlotOrario.tsx
│   │
│   ├── dashboard/           # Feature: Dashboard
│   │   ├── KPICard.tsx
│   │   ├── AppuntamentiOggi.tsx
│   │   ├── QuickActions.tsx
│   │   └── StatsChart.tsx
│   │
│   ├── fatture/             # Feature: Fatture
│   │   ├── FattureTable.tsx
│   │   ├── FatturaForm.tsx
│   │   └── FatturaPreview.tsx
│   │
│   ├── voice/               # Feature: Voice Agent
│   │   ├── VoiceAgentButton.tsx
│   │   ├── VoiceAgentModal.tsx
│   │   └── WaveformVisualizer.tsx
│   │
│   └── whatsapp/            # Feature: WhatsApp
│       ├── WhatsAppStatus.tsx
│       ├── ConversationList.tsx
│       └── MessageComposer.tsx
│
├── hooks/                   # Custom hooks
│   ├── useClienti.ts
│   ├── useAppuntamenti.ts
│   ├── useServizi.ts
│   ├── useFatture.ts
│   ├── useImpostazioni.ts
│   └── useTauriCommand.ts
│
├── stores/                  # Zustand stores
│   ├── uiStore.ts
│   ├── authStore.ts
│   └── settingsStore.ts
│
├── lib/                     # Utilities
│   ├── utils.ts             # cn() helper
│   ├── tauri.ts             # Tauri wrappers
│   ├── date.ts              # Date formatting IT
│   └── validators.ts        # Zod schemas
│
├── types/                   # TypeScript types
│   ├── cliente.ts
│   ├── appuntamento.ts
│   ├── servizio.ts
│   ├── fattura.ts
│   └── index.ts
│
└── pages/                   # Route pages
    ├── Dashboard.tsx
    ├── Clienti.tsx
    ├── Calendario.tsx
    ├── Servizi.tsx
    ├── Fatture.tsx
    ├── Impostazioni.tsx
    └── NotFound.tsx
```

---

## TypeScript Types

### types/index.ts

```typescript
// ═══════════════════════════════════════════════════════════════
// FLUXION - TypeScript Types
// ═══════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────
// CLIENTE
// ─────────────────────────────────────────────────────────────────
export interface Cliente {
  id: string;
  nome: string;
  cognome: string;
  email?: string;
  telefono: string;
  dataNascita?: string;
  indirizzo?: string;
  cap?: string;
  citta?: string;
  provincia?: string;
  codiceFiscale?: string;
  partitaIva?: string;
  codiceSdi?: string;
  pec?: string;
  note?: string;
  tags?: string[];
  consensoMarketing: boolean;
  consensoWhatsapp: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ClienteInput {
  nome: string;
  cognome: string;
  email?: string;
  telefono: string;
  note?: string;
}

// ─────────────────────────────────────────────────────────────────
// SERVIZIO
// ─────────────────────────────────────────────────────────────────
export interface Servizio {
  id: string;
  nome: string;
  descrizione?: string;
  categoria?: string;
  prezzo: number;
  ivaPercentuale: number;
  durataMinuti: number;
  bufferMinuti: number;
  colore: string;
  icona?: string;
  attivo: boolean;
  ordine: number;
}

// ─────────────────────────────────────────────────────────────────
// OPERATORE
// ─────────────────────────────────────────────────────────────────
export interface Operatore {
  id: string;
  nome: string;
  cognome: string;
  email?: string;
  telefono?: string;
  ruolo: 'admin' | 'operatore' | 'reception';
  colore: string;
  avatarUrl?: string;
  attivo: boolean;
  servizi: string[]; // IDs servizi
}

// ─────────────────────────────────────────────────────────────────
// APPUNTAMENTO
// ─────────────────────────────────────────────────────────────────
export type StatoAppuntamento = 
  | 'bozza' 
  | 'confermato' 
  | 'completato' 
  | 'cancellato' 
  | 'no_show';

export interface Appuntamento {
  id: string;
  clienteId: string;
  clienteNome: string;
  servizioId: string;
  servizioNome: string;
  operatoreId?: string;
  operatoreNome?: string;
  dataOraInizio: string; // ISO 8601
  dataOraFine: string;
  durataMinuti: number;
  stato: StatoAppuntamento;
  prezzo: number;
  scontoPercentuale: number;
  prezzoFinale: number;
  note?: string;
  noteInterne?: string;
  fontePrenotazione: 'manuale' | 'whatsapp' | 'voice' | 'online';
  reminderInviato: boolean;
}

export interface AppuntamentoInput {
  clienteId: string;
  servizioId: string;
  operatoreId?: string;
  dataOraInizio: string;
  note?: string;
}

// ─────────────────────────────────────────────────────────────────
// FATTURA
// ─────────────────────────────────────────────────────────────────
export type StatoFattura = 
  | 'bozza' 
  | 'emessa' 
  | 'inviata' 
  | 'pagata' 
  | 'annullata';

export interface Fattura {
  id: string;
  numero: number;
  anno: number;
  numeroCompleto: string;
  clienteId: string;
  clienteNome: string;
  imponibile: number;
  iva: number;
  totale: number;
  stato: StatoFattura;
  dataEmissione: string;
  dataScadenza?: string;
  dataPagamento?: string;
  metodoPagamento?: string;
  xmlGenerato: boolean;
  xmlPath?: string;
  righe: FatturaRiga[];
}

export interface FatturaRiga {
  id: string;
  descrizione: string;
  quantita: number;
  prezzoUnitario: number;
  ivaPercentuale: number;
  totaleRiga: number;
}

// ─────────────────────────────────────────────────────────────────
// UI / DASHBOARD
// ─────────────────────────────────────────────────────────────────
export interface KPIStat {
  label: string;
  value: string | number;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  icon: string;
}

export interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
}
```

---

## Custom Hooks

### hooks/useTauriCommand.ts

```typescript
import { invoke } from '@tauri-apps/api/core';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

/**
 * Hook generico per chiamare Tauri commands
 */
export function useTauriQuery<T>(
  key: string[],
  command: string,
  args?: Record<string, unknown>,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: key,
    queryFn: () => invoke<T>(command, args),
    ...options,
  });
}

export function useTauriMutation<TInput, TOutput>(
  command: string,
  options?: {
    onSuccess?: (data: TOutput) => void;
    invalidateKeys?: string[][];
  }
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (input: TInput) => invoke<TOutput>(command, input as Record<string, unknown>),
    onSuccess: (data) => {
      options?.invalidateKeys?.forEach((key) => {
        queryClient.invalidateQueries({ queryKey: key });
      });
      options?.onSuccess?.(data);
    },
  });
}
```

### hooks/useClienti.ts

```typescript
import { useTauriQuery, useTauriMutation } from './useTauriCommand';
import type { Cliente, ClienteInput } from '@/types';

export function useClienti() {
  return useTauriQuery<Cliente[]>(
    ['clienti'],
    'get_clienti'
  );
}

export function useCliente(id: string) {
  return useTauriQuery<Cliente | null>(
    ['clienti', id],
    'get_cliente',
    { id },
    { enabled: !!id }
  );
}

export function useCercaClienti(query: string) {
  return useTauriQuery<Cliente[]>(
    ['clienti', 'search', query],
    'cerca_clienti',
    { query },
    { enabled: query.length >= 2 }
  );
}

export function useCreaCliente() {
  return useTauriMutation<{ cliente: ClienteInput }, Cliente>(
    'crea_cliente',
    { invalidateKeys: [['clienti']] }
  );
}

export function useAggiornaCliente() {
  return useTauriMutation<{ id: string; cliente: Partial<ClienteInput> }, Cliente>(
    'aggiorna_cliente',
    { invalidateKeys: [['clienti']] }
  );
}

export function useEliminaCliente() {
  return useTauriMutation<{ id: string }, void>(
    'elimina_cliente',
    { invalidateKeys: [['clienti']] }
  );
}
```

### hooks/useAppuntamenti.ts

```typescript
import { useTauriQuery, useTauriMutation } from './useTauriCommand';
import type { Appuntamento, AppuntamentoInput } from '@/types';
import { format } from 'date-fns';

export function useAppuntamentiGiorno(data: Date) {
  const dataStr = format(data, 'yyyy-MM-dd');
  
  return useTauriQuery<Appuntamento[]>(
    ['appuntamenti', 'giorno', dataStr],
    'get_appuntamenti_giorno',
    { data: dataStr }
  );
}

export function useAppuntamentiSettimana(dataInizio: Date) {
  const dataStr = format(dataInizio, 'yyyy-MM-dd');
  
  return useTauriQuery<Appuntamento[]>(
    ['appuntamenti', 'settimana', dataStr],
    'get_appuntamenti_settimana',
    { data_inizio: dataStr }
  );
}

export function useCreaAppuntamento() {
  return useTauriMutation<{ appuntamento: AppuntamentoInput }, Appuntamento>(
    'crea_appuntamento',
    { invalidateKeys: [['appuntamenti']] }
  );
}

export function useAggiornaStatoAppuntamento() {
  return useTauriMutation<{ id: string; stato: string }, Appuntamento>(
    'aggiorna_stato_appuntamento',
    { invalidateKeys: [['appuntamenti']] }
  );
}
```

---

## State Management

### stores/uiStore.ts

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Theme
  theme: 'dark' | 'light' | 'system';
  setTheme: (theme: 'dark' | 'light' | 'system') => void;
  
  // Modals
  activeModal: string | null;
  modalData: unknown;
  openModal: (modal: string, data?: unknown) => void;
  closeModal: () => void;
  
  // Calendar
  calendarView: 'day' | 'week' | 'month';
  setCalendarView: (view: 'day' | 'week' | 'month') => void;
  selectedDate: string; // ISO date
  setSelectedDate: (date: string) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Sidebar
      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      
      // Theme
      theme: 'dark',
      setTheme: (theme) => set({ theme }),
      
      // Modals
      activeModal: null,
      modalData: null,
      openModal: (modal, data) => set({ activeModal: modal, modalData: data }),
      closeModal: () => set({ activeModal: null, modalData: null }),
      
      // Calendar
      calendarView: 'week',
      setCalendarView: (view) => set({ calendarView: view }),
      selectedDate: new Date().toISOString().split('T')[0],
      setSelectedDate: (date) => set({ selectedDate: date }),
    }),
    {
      name: 'fluxion-ui',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
        calendarView: state.calendarView,
      }),
    }
  )
);
```

---

## Tauri Integration

### lib/tauri.ts

```typescript
import { invoke } from '@tauri-apps/api/core';
import { message, ask, open, save } from '@tauri-apps/plugin-dialog';
import { writeTextFile, readTextFile } from '@tauri-apps/plugin-fs';

/**
 * Wrapper invoke con error handling
 */
export async function tauriInvoke<T>(
  command: string,
  args?: Record<string, unknown>
): Promise<T> {
  try {
    return await invoke<T>(command, args);
  } catch (error) {
    console.error(`Tauri command "${command}" failed:`, error);
    throw error;
  }
}

/**
 * Dialog helpers
 */
export async function showMessage(
  title: string,
  content: string,
  kind: 'info' | 'warning' | 'error' = 'info'
) {
  await message(content, { title, kind });
}

export async function showConfirm(
  title: string,
  content: string
): Promise<boolean> {
  return await ask(content, { title, kind: 'warning' });
}

export async function selectFile(
  filters?: { name: string; extensions: string[] }[]
) {
  return await open({
    multiple: false,
    filters,
  });
}

export async function saveFile(
  defaultPath?: string,
  filters?: { name: string; extensions: string[] }[]
) {
  return await save({
    defaultPath,
    filters,
  });
}

/**
 * File helpers
 */
export async function exportToFile(
  content: string,
  defaultName: string,
  filters: { name: string; extensions: string[] }[]
) {
  const path = await saveFile(defaultName, filters);
  if (path) {
    await writeTextFile(path, content);
    return path;
  }
  return null;
}
```

---

## Componenti Pattern

### Pattern: Feature Component

```typescript
// components/clienti/ClientiTable.tsx

import { useState } from 'react';
import { useClienti, useEliminaCliente } from '@/hooks/useClienti';
import { useUIStore } from '@/stores/uiStore';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  MoreHorizontal, 
  Pencil, 
  Trash2, 
  Search,
  UserPlus 
} from 'lucide-react';
import type { Cliente } from '@/types';

export function ClientiTable() {
  const [search, setSearch] = useState('');
  const { data: clienti, isLoading, error } = useClienti();
  const elimina = useEliminaCliente();
  const { openModal } = useUIStore();
  
  // Filtra clienti localmente
  const clientiFiltrati = clienti?.filter((c) =>
    `${c.nome} ${c.cognome} ${c.telefono} ${c.email}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );
  
  const handleEdit = (cliente: Cliente) => {
    openModal('cliente-form', { cliente, mode: 'edit' });
  };
  
  const handleDelete = async (id: string) => {
    if (await confirm('Eliminare questo cliente?')) {
      elimina.mutate({ id });
    }
  };
  
  if (isLoading) return <TableSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Cerca clienti..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button onClick={() => openModal('cliente-form', { mode: 'create' })}>
          <UserPlus className="h-4 w-4 mr-2" />
          Nuovo Cliente
        </Button>
      </div>
      
      {/* Table */}
      <div className="rounded-lg border border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Telefono</TableHead>
              <TableHead>Email</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {clientiFiltrati?.map((cliente) => (
              <TableRow key={cliente.id}>
                <TableCell className="font-medium">
                  {cliente.nome} {cliente.cognome}
                </TableCell>
                <TableCell>{cliente.telefono}</TableCell>
                <TableCell>{cliente.email || '-'}</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleEdit(cliente)}>
                        <Pencil className="h-4 w-4 mr-2" />
                        Modifica
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={() => handleDelete(cliente.id)}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Elimina
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
```

---

## 🔗 File Correlati

- Design System: `CLAUDE-DESIGN-SYSTEM.md`
- Backend API: `CLAUDE-BACKEND.md`
- Design Bible: `../FLUXION-DESIGN-BIBLE.md`

---

*Ultimo aggiornamento: 2025-12-28T18:00:00*
