// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Assenze Hooks
// TanStack Query hooks per gestione assenze/ferie operatori
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export type TipoAssenza =
  | 'ferie'
  | 'malattia'
  | 'infortunio'
  | 'permesso'
  | 'formazione'
  | 'maternita'
  | 'altro';

export interface OperatoreAssenza {
  id: string;
  operatore_id: string;
  data_inizio: string;  // YYYY-MM-DD
  data_fine: string;    // YYYY-MM-DD
  tipo: TipoAssenza;
  note: string | null;
  approvata: number;
  created_at: string;
}

export interface CreateAssenzaInput {
  operatore_id: string;
  data_inizio: string;
  data_fine: string;
  tipo: TipoAssenza;
  note?: string;
}

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const operatoreAssenzeKeys = {
  all: ['operatore-assenze'] as const,
  byOperatore: (operatoreId: string) =>
    [...operatoreAssenzeKeys.all, operatoreId] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

export function useOperatoreAssenze(operatoreId: string) {
  return useQuery({
    queryKey: operatoreAssenzeKeys.byOperatore(operatoreId),
    queryFn: async () => {
      const assenze = await invoke<OperatoreAssenza[]>('get_operatore_assenze', {
        operatoreId,
      });
      return assenze;
    },
    enabled: !!operatoreId,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

export function useCreateAssenza() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateAssenzaInput) => {
      const assenza = await invoke<OperatoreAssenza>('create_operatore_assenza', { input });
      return assenza;
    },
    onSuccess: (_data, { operatore_id }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreAssenzeKeys.byOperatore(operatore_id),
      });
    },
  });
}

export function useDeleteAssenza() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, operatoreId }: { id: string; operatoreId: string }) => {
      await invoke('delete_operatore_assenza', { id });
      return operatoreId;
    },
    onSuccess: (_data, { operatoreId }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreAssenzeKeys.byOperatore(operatoreId),
      });
    },
  });
}
