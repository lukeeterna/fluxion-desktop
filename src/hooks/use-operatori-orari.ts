// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Orari Hooks
// TanStack Query hooks per gestione orari settimanali per operatore
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export interface OrarioLavoro {
  id: string;
  giorno_settimana: number; // 0=domenica, 1=lunedì ... 6=sabato
  ora_inizio: string;       // "HH:MM"
  ora_fine: string;         // "HH:MM"
  tipo: 'lavoro' | 'pausa';
  operatore_id: string | null;
}

export interface SetOrarioInput {
  giorno_settimana: number;
  ora_inizio: string;
  ora_fine: string;
  tipo: 'lavoro' | 'pausa';
}

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const operatoreOrariKeys = {
  all: ['operatore-orari'] as const,
  byOperatore: (operatoreId: string) =>
    [...operatoreOrariKeys.all, operatoreId] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/// Ritorna tutti gli orari specifici dell'operatore (operatore_id = id, NON NULL)
export function useOperatoreOrari(operatoreId: string) {
  return useQuery({
    queryKey: operatoreOrariKeys.byOperatore(operatoreId),
    queryFn: () =>
      invoke<OrarioLavoro[]>('get_orari_operatore', { operatoreId }),
    enabled: !!operatoreId,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/// Sostituisce atomicamente tutti gli orari dell'operatore
export function useSetOrariOperatore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      operatoreId,
      orari,
    }: {
      operatoreId: string;
      orari: SetOrarioInput[];
    }) =>
      invoke<OrarioLavoro[]>('set_orari_operatore', { operatoreId, orari }),
    onSuccess: (_data, { operatoreId }) => {
      queryClient.invalidateQueries({
        queryKey: operatoreOrariKeys.byOperatore(operatoreId),
      });
    },
  });
}
