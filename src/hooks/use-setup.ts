// ═══════════════════════════════════════════════════════════════════
// FLUXION - Setup Wizard Hooks
// TanStack Query hooks per configurazione iniziale
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { SetupConfig, SetupStatus } from '../types/setup';

// ─────────────────────────────────────────────────────────────────────
// QUERY KEYS
// ─────────────────────────────────────────────────────────────────────

export const setupKeys = {
  all: ['setup'] as const,
  status: () => [...setupKeys.all, 'status'] as const,
  config: () => [...setupKeys.all, 'config'] as const,
};

// ─────────────────────────────────────────────────────────────────────
// QUERIES
// ─────────────────────────────────────────────────────────────────────

/**
 * Hook per verificare lo stato del setup
 */
export function useSetupStatus() {
  return useQuery({
    queryKey: setupKeys.status(),
    queryFn: async (): Promise<SetupStatus> => {
      return await invoke('get_setup_status');
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
  });
}

/**
 * Hook per ottenere la configurazione corrente
 */
export function useSetupConfig() {
  return useQuery({
    queryKey: setupKeys.config(),
    queryFn: async (): Promise<SetupConfig> => {
      return await invoke('get_setup_config');
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
  });
}

// ─────────────────────────────────────────────────────────────────────
// MUTATIONS
// ─────────────────────────────────────────────────────────────────────

/**
 * Hook per salvare la configurazione iniziale
 */
export function useSaveSetupConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: SetupConfig) => {
      return await invoke('save_setup_config', { config });
    },
    onSuccess: () => {
      // Invalida le query per forzare refresh
      queryClient.invalidateQueries({ queryKey: setupKeys.all });
    },
  });
}

/**
 * Hook per resettare il setup (debug/test)
 */
export function useResetSetup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      return await invoke('reset_setup');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: setupKeys.all });
    },
  });
}
