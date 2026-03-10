// ═══════════════════════════════════════════════════════════════════
// FLUXION - Listini Fornitori Hooks (Gap #5)
// TanStack Query hooks per import/lettura listini prezzi
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  ListinoFornitore,
  ListinoRiga,
  ListinoVariazione,
  ImportListinoRequest,
  ImportListinoResult,
} from '@/types/listino';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const listiniKeys = {
  all: ['listini'] as const,
  byFornitore: (fornitoreId: string) => [...listiniKeys.all, 'fornitore', fornitoreId] as const,
  righe: (listinoId: string) => [...listiniKeys.all, 'righe', listinoId] as const,
  variazioni: (rigaId: string) => [...listiniKeys.all, 'variazioni', rigaId] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

export function useListiniFornitore(fornitoreId: string) {
  return useQuery({
    queryKey: listiniKeys.byFornitore(fornitoreId),
    queryFn: () =>
      invoke<ListinoFornitore[]>('get_listini_fornitore', { fornitoreId }),
    enabled: !!fornitoreId,
  });
}

export function useListinoRighe(listinoId: string) {
  return useQuery({
    queryKey: listiniKeys.righe(listinoId),
    queryFn: () => invoke<ListinoRiga[]>('get_listino_righe', { listinoId }),
    enabled: !!listinoId,
  });
}

export function useListinoVariazioni(rigaId: string) {
  return useQuery({
    queryKey: listiniKeys.variazioni(rigaId),
    queryFn: () =>
      invoke<ListinoVariazione[]>('get_listino_variazioni', { listinoRigaId: rigaId }),
    enabled: !!rigaId,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

export function useImportListino() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (request: ImportListinoRequest) =>
      invoke<ImportListinoResult>('import_listino', { request }),
    onSuccess: (_data, variables) => {
      void qc.invalidateQueries({
        queryKey: listiniKeys.byFornitore(variables.fornitore_id),
      });
    },
  });
}

export function useDeleteListino() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ listinoId }: { listinoId: string; fornitoreId: string }) =>
      invoke<void>('delete_listino', { listinoId }),
    onSuccess: (_data, variables) => {
      void qc.invalidateQueries({
        queryKey: listiniKeys.byFornitore(variables.fornitoreId),
      });
    },
  });
}
