// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Hooks
// TanStack Query hooks for operatori operations
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { Operatore, CreateOperatoreInput, UpdateOperatoreInput } from '@/types/operatore';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const operatoriKeys = {
  all: ['operatori'] as const,
  lists: () => [...operatoriKeys.all, 'list'] as const,
  list: (activeOnly?: boolean) => [...operatoriKeys.lists(), { activeOnly }] as const,
  details: () => [...operatoriKeys.all, 'detail'] as const,
  detail: (id: string) => [...operatoriKeys.details(), id] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/// Get all operatori (active by default)
export function useOperatori(activeOnly: boolean = true) {
  return useQuery({
    queryKey: operatoriKeys.list(activeOnly),
    queryFn: async () => {
      const operatori = await invoke<Operatore[]>('get_operatori', { activeOnly });
      return operatori;
    },
  });
}

/// Get single operatore by ID
export function useOperatore(id: string) {
  return useQuery({
    queryKey: operatoriKeys.detail(id),
    queryFn: async () => {
      const operatore = await invoke<Operatore>('get_operatore', { id });
      return operatore;
    },
    enabled: !!id,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/// Create new operatore
export function useCreateOperatore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateOperatoreInput) => {
      const operatore = await invoke<Operatore>('create_operatore', { input });
      return operatore;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: operatoriKeys.lists() });
    },
  });
}

/// Update operatore
export function useUpdateOperatore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, input }: { id: string; input: UpdateOperatoreInput }) => {
      const operatore = await invoke<Operatore>('update_operatore', { id, input });
      return operatore;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: operatoriKeys.lists() });
      queryClient.invalidateQueries({ queryKey: operatoriKeys.detail(data.id) });
    },
  });
}

/// Delete operatore (soft delete)
export function useDeleteOperatore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await invoke('delete_operatore', { id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: operatoriKeys.lists() });
    },
  });
}
