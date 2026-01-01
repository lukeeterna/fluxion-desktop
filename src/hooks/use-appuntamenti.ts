// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamenti Hooks
// TanStack Query hooks for appuntamenti operations
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  Appuntamento,
  AppuntamentoDettagliato,
  CreateAppuntamentoInput,
  UpdateAppuntamentoInput,
  GetAppuntamentiParams,
} from '@/types/appuntamento';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const appuntamentiKeys = {
  all: ['appuntamenti'] as const,
  lists: () => [...appuntamentiKeys.all, 'list'] as const,
  list: (params: GetAppuntamentiParams) => [...appuntamentiKeys.lists(), params] as const,
  details: () => [...appuntamentiKeys.all, 'detail'] as const,
  detail: (id: string) => [...appuntamentiKeys.details(), id] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/// Get appuntamenti by date range (for calendar view)
export function useAppuntamenti(params: GetAppuntamentiParams) {
  return useQuery({
    queryKey: appuntamentiKeys.list(params),
    queryFn: async () => {
      const appuntamenti = await invoke<AppuntamentoDettagliato[]>('get_appuntamenti', { params });
      return appuntamenti;
    },
    // Refetch when window gains focus (to sync data)
    refetchOnWindowFocus: true,
  });
}

/// Get single appuntamento by ID
export function useAppuntamento(id: string) {
  return useQuery({
    queryKey: appuntamentiKeys.detail(id),
    queryFn: async () => {
      const appuntamento = await invoke<Appuntamento>('get_appuntamento', { id });
      return appuntamento;
    },
    enabled: !!id,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/// Create new appuntamento
export function useCreateAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateAppuntamentoInput) => {
      const appuntamento = await invoke<Appuntamento>('create_appuntamento', { input });
      return appuntamento;
    },
    onSuccess: () => {
      // Invalidate all appointment lists (all date ranges)
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
    },
    onError: (error: unknown) => {
      // Conflict errors will be shown in UI
      const errorMsg = typeof error === 'string' ? error : (error as any)?.message || 'Unknown error';
      console.error('Failed to create appuntamento:', errorMsg);
    },
  });
}

/// Update appuntamento
export function useUpdateAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, input }: { id: string; input: UpdateAppuntamentoInput }) => {
      const appuntamento = await invoke<Appuntamento>('update_appuntamento', { id, input });
      return appuntamento;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
    },
    onError: (error: unknown) => {
      const errorMsg = typeof error === 'string' ? error : (error as any)?.message || 'Unknown error';
      console.error('Failed to update appuntamento:', errorMsg);
    },
  });
}

/// Delete appuntamento (set stato = 'cancellato')
export function useDeleteAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await invoke('delete_appuntamento', { id });
    },

    // ✅ FIX BUG #2: Optimistic update per rimozione immediata
    onMutate: async (id: string) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: appuntamentiKeys.lists() });

      // Snapshot previous value for rollback
      const previousQueries = queryClient.getQueriesData({ queryKey: appuntamentiKeys.lists() });

      // Optimistically remove from all cached queries
      queryClient.setQueriesData<AppuntamentoDettagliato[]>(
        { queryKey: appuntamentiKeys.lists() },
        (old) => {
          if (!old) return [];
          return old.filter(a => a.appuntamento.id !== id);
        }
      );

      return { previousQueries };
    },

    onError: (err, id, context) => {
      // Rollback on error
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },

    onSuccess: () => {
      // Toast handled in CalendarioPage
    },

    // Always refetch to ensure consistency
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
    },
  });
}
