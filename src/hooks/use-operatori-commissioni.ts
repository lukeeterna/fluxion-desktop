// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Commissioni Hooks (B5)
// TanStack Query hooks per gestione commissioni operatori
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export type TipoCommissione =
  | 'percentuale_servizio'
  | 'percentuale_prodotti'
  | 'fisso_mensile'
  | 'soglia_bonus';

export interface OperatoreCommissione {
  id: string;
  operatore_id: string;
  tipo: TipoCommissione;
  percentuale: number | null;
  importo_fisso: number | null;
  soglia_fatturato: number | null;
  bonus_importo: number | null;
  valida_dal: string;       // YYYY-MM-DD
  valida_al: string | null; // YYYY-MM-DD, null = senza scadenza
  servizio_id: string | null;
  note: string | null;
  created_at: string;
}

export interface CreateCommissioneInput {
  operatore_id: string;
  tipo: TipoCommissione;
  percentuale?: number;
  importo_fisso?: number;
  soglia_fatturato?: number;
  bonus_importo?: number;
  valida_dal: string;
  valida_al?: string;
  servizio_id?: string;
  note?: string;
}

export interface UpdateCommissioneInput {
  tipo: TipoCommissione;
  percentuale?: number;
  importo_fisso?: number;
  soglia_fatturato?: number;
  bonus_importo?: number;
  valida_dal: string;
  valida_al?: string;
  servizio_id?: string;
  note?: string;
}

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const operatoreCommissioniKeys = {
  all: ['operatore-commissioni'] as const,
  byOperatore: (operatoreId: string) =>
    [...operatoreCommissioniKeys.all, operatoreId] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

export function useOperatoreCommissioni(operatoreId: string) {
  return useQuery({
    queryKey: operatoreCommissioniKeys.byOperatore(operatoreId),
    queryFn: async () => {
      const commissioni = await invoke<OperatoreCommissione[]>(
        'get_operatore_commissioni',
        { operatoreId },
      );
      return commissioni;
    },
    enabled: !!operatoreId,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

export function useCreateCommissione() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateCommissioneInput) => {
      const commissione = await invoke<OperatoreCommissione>(
        'create_operatore_commissione',
        { input },
      );
      return commissione;
    },
    onSuccess: (_data, { operatore_id }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreCommissioniKeys.byOperatore(operatore_id),
      });
    },
  });
}

export function useUpdateCommissione() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      operatoreId,
      input,
    }: {
      id: string;
      operatoreId: string;
      input: UpdateCommissioneInput;
    }) => {
      const commissione = await invoke<OperatoreCommissione>(
        'update_operatore_commissione',
        { id, input },
      );
      return { commissione, operatoreId };
    },
    onSuccess: (_data, { operatoreId }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreCommissioniKeys.byOperatore(operatoreId),
      });
    },
  });
}

export function useDeleteCommissione() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      operatoreId,
    }: {
      id: string;
      operatoreId: string;
    }) => {
      await invoke('delete_operatore_commissione', { id });
      return operatoreId;
    },
    onSuccess: (_data, { operatoreId }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreCommissioniKeys.byOperatore(operatoreId),
      });
    },
  });
}
