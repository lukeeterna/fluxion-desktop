// ═══════════════════════════════════════════════════════════════════
// FLUXION - Clienti Hooks
// TanStack Query hooks for CRUD operations
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { Cliente, CreateClienteInput, UpdateClienteInput } from '@/types/cliente';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const clientiKeys = {
  all: ['clienti'] as const,
  lists: () => [...clientiKeys.all, 'list'] as const,
  list: (filters?: string) => [...clientiKeys.lists(), { filters }] as const,
  details: () => [...clientiKeys.all, 'detail'] as const,
  detail: (id: string) => [...clientiKeys.details(), id] as const,
  search: (query: string) => [...clientiKeys.all, 'search', query] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/**
 * Get all clienti
 */
export function useClienti() {
  return useQuery({
    queryKey: clientiKeys.lists(),
    queryFn: () => invoke<Cliente[]>('get_clienti'),
  });
}

/**
 * Get single cliente by ID
 */
export function useCliente(id: string) {
  return useQuery({
    queryKey: clientiKeys.detail(id),
    queryFn: () => invoke<Cliente>('get_cliente', { id }),
    enabled: !!id,
  });
}

/**
 * Search clienti
 */
export function useSearchClienti(query: string) {
  return useQuery({
    queryKey: clientiKeys.search(query),
    queryFn: () => invoke<Cliente[]>('search_clienti', { query }),
    enabled: query.length >= 2, // Only search if query is at least 2 chars
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/**
 * Create new cliente
 */
export function useCreateCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CreateClienteInput) =>
      invoke<Cliente>('create_cliente', { input }),
    onSuccess: () => {
      // Invalidate and refetch clienti list
      queryClient.invalidateQueries({ queryKey: clientiKeys.lists() });
    },
  });
}

/**
 * Update existing cliente
 */
export function useUpdateCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: UpdateClienteInput) =>
      invoke<Cliente>('update_cliente', { input }),
    onSuccess: (data) => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: clientiKeys.lists() });
      // Invalidate specific detail
      queryClient.invalidateQueries({ queryKey: clientiKeys.detail(data.id) });
    },
  });
}

/**
 * Delete cliente (soft delete)
 */
export function useDeleteCliente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoke<void>('delete_cliente', { id }),
    onSuccess: () => {
      // Invalidate all clienti queries
      queryClient.invalidateQueries({ queryKey: clientiKeys.all });
    },
  });
}
