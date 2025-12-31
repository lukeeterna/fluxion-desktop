// ═══════════════════════════════════════════════════════════════════
// FLUXION - Servizi Hooks
// TanStack Query hooks for servizi operations
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { Servizio, CreateServizioInput, UpdateServizioInput } from '@/types/servizio';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const serviziKeys = {
  all: ['servizi'] as const,
  lists: () => [...serviziKeys.all, 'list'] as const,
  list: (activeOnly?: boolean) => [...serviziKeys.lists(), { activeOnly }] as const,
  details: () => [...serviziKeys.all, 'detail'] as const,
  detail: (id: string) => [...serviziKeys.details(), id] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/// Get all servizi (active by default)
export function useServizi(activeOnly: boolean = true) {
  return useQuery({
    queryKey: serviziKeys.list(activeOnly),
    queryFn: async () => {
      const servizi = await invoke<Servizio[]>('get_servizi', { activeOnly });
      return servizi;
    },
  });
}

/// Get single servizio by ID
export function useServizio(id: string) {
  return useQuery({
    queryKey: serviziKeys.detail(id),
    queryFn: async () => {
      const servizio = await invoke<Servizio>('get_servizio', { id });
      return servizio;
    },
    enabled: !!id,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/// Create new servizio
export function useCreateServizio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateServizioInput) => {
      const servizio = await invoke<Servizio>('create_servizio', { input });
      return servizio;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: serviziKeys.lists() });
    },
  });
}

/// Update servizio
export function useUpdateServizio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, input }: { id: string; input: UpdateServizioInput }) => {
      const servizio = await invoke<Servizio>('update_servizio', { id, input });
      return servizio;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: serviziKeys.lists() });
      queryClient.invalidateQueries({ queryKey: serviziKeys.detail(data.id) });
    },
  });
}

/// Delete servizio (soft delete)
export function useDeleteServizio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await invoke('delete_servizio', { id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: serviziKeys.lists() });
    },
  });
}
