// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fornitori Hooks
// TanStack Query hooks for supplier CRUD operations
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  Supplier,
  CreateSupplierInput,
  UpdateSupplierInput,
  SupplierOrder,
  CreateOrderInput,
  SupplierInteraction,
  SupplierStats,
} from '@/types/supplier';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const fornitoriKeys = {
  all: ['fornitori'] as const,
  lists: () => [...fornitoriKeys.all, 'list'] as const,
  list: (filters?: string) => [...fornitoriKeys.lists(), { filters }] as const,
  details: () => [...fornitoriKeys.all, 'detail'] as const,
  detail: (id: string) => [...fornitoriKeys.details(), id] as const,
  search: (query: string) => [...fornitoriKeys.all, 'search', query] as const,
  orders: (supplierId: string) => [...fornitoriKeys.all, 'orders', supplierId] as const,
  allOrders: () => [...fornitoriKeys.all, 'allOrders'] as const,
  interactions: (supplierId: string) => [...fornitoriKeys.all, 'interactions', supplierId] as const,
  stats: (supplierId: string) => [...fornitoriKeys.all, 'stats', supplierId] as const,
};

// ───────────────────────────────────────────────────────────────────
// Supplier Queries
// ───────────────────────────────────────────────────────────────────

/**
 * Get all suppliers
 */
export function useFornitori() {
  return useQuery({
    queryKey: fornitoriKeys.lists(),
    queryFn: () => invoke<Supplier[]>('list_suppliers'),
  });
}

/**
 * Get single supplier by ID
 */
export function useFornitore(id: string) {
  return useQuery({
    queryKey: fornitoriKeys.detail(id),
    queryFn: () => invoke<Supplier>('get_supplier', { id }),
    enabled: !!id,
  });
}

/**
 * Search suppliers
 */
export function useSearchFornitori(query: string) {
  return useQuery({
    queryKey: fornitoriKeys.search(query),
    queryFn: () => invoke<Supplier[]>('search_suppliers', { query }),
    enabled: query.length >= 2,
  });
}

/**
 * Get supplier stats
 */
export function useFornitoreStats(supplierId: string) {
  return useQuery({
    queryKey: fornitoriKeys.stats(supplierId),
    queryFn: () => invoke<SupplierStats>('get_supplier_stats', { supplierId }),
    enabled: !!supplierId,
  });
}

// ───────────────────────────────────────────────────────────────────
// Supplier Mutations
// ───────────────────────────────────────────────────────────────────

/**
 * Create new supplier
 */
export function useCreateFornitore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (supplier: CreateSupplierInput) =>
      invoke<Supplier>('create_supplier', { supplier }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.lists() });
    },
  });
}

/**
 * Update existing supplier
 */
export function useUpdateFornitore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (supplier: UpdateSupplierInput) =>
      invoke<Supplier>('update_supplier', { supplier }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.detail(data.id) });
    },
  });
}

/**
 * Delete supplier
 */
export function useDeleteFornitore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoke<void>('delete_supplier', { id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.all });
    },
  });
}

// ───────────────────────────────────────────────────────────────────
// Order Queries & Mutations
// ───────────────────────────────────────────────────────────────────

/**
 * Get orders for a supplier
 */
export function useFornitoreOrders(supplierId: string) {
  return useQuery({
    queryKey: fornitoriKeys.orders(supplierId),
    queryFn: () => invoke<SupplierOrder[]>('get_supplier_orders', { supplierId }),
    enabled: !!supplierId,
  });
}

/**
 * Get all orders
 */
export function useAllOrders() {
  return useQuery({
    queryKey: fornitoriKeys.allOrders(),
    queryFn: () => invoke<SupplierOrder[]>('list_all_orders'),
  });
}

/**
 * Create order
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (order: CreateOrderInput) =>
      invoke<SupplierOrder>('create_supplier_order', { order }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.orders(data.supplier_id) });
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.allOrders() });
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.stats(data.supplier_id) });
    },
  });
}

/**
 * Update order status
 */
export function useUpdateOrderStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: SupplierOrder['status'] }) =>
      invoke<SupplierOrder>('update_order_status', { id, status }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.orders(data.supplier_id) });
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.allOrders() });
    },
  });
}

// ───────────────────────────────────────────────────────────────────
// Interaction Queries
// ───────────────────────────────────────────────────────────────────

/**
 * Get interactions for a supplier
 */
export function useFornitoreInteractions(supplierId: string) {
  return useQuery({
    queryKey: fornitoriKeys.interactions(supplierId),
    queryFn: () => invoke<SupplierInteraction[]>('get_supplier_interactions', { supplierId }),
    enabled: !!supplierId,
  });
}

/**
 * Log interaction
 */
export function useLogInteraction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (interaction: {
      supplierId: string;
      orderId?: string;
      tipo: SupplierInteraction['tipo'];
      messaggio?: string;
      status?: string;
    }) => invoke<SupplierInteraction>('log_supplier_interaction', { interaction }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: fornitoriKeys.interactions(data.supplier_id) });
    },
  });
}
