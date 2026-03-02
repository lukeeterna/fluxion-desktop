// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Servizi Hooks
// TanStack Query hooks per gestione servizi abilitati per operatore
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const operatoreServiziKeys = {
  all: ['operatore-servizi'] as const,
  byOperatore: (operatoreId: string) =>
    [...operatoreServiziKeys.all, operatoreId] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/// Ritorna la lista di servizio_ids abilitati per l'operatore
export function useOperatoreServizi(operatoreId: string) {
  return useQuery({
    queryKey: operatoreServiziKeys.byOperatore(operatoreId),
    queryFn: async () => {
      const ids = await invoke<string[]>('get_operatore_servizi', { operatoreId });
      return ids;
    },
    enabled: !!operatoreId,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/// Sostituisce atomicamente tutti i servizi dell'operatore
export function useUpdateOperatoreServizi() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      operatoreId,
      servizioIds,
    }: {
      operatoreId: string;
      servizioIds: string[];
    }) => {
      await invoke('update_operatore_servizi', { operatoreId, servizioIds });
    },
    onSuccess: (_data, { operatoreId }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreServiziKeys.byOperatore(operatoreId),
      });
    },
  });
}
