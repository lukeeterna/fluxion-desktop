// ═══════════════════════════════════════════════════════════════════
// FLUXION - Support & Diagnostics Hooks (Fase 4 - Fluxion Care)
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  DiagnosticsInfo,
  SupportBundleResult,
  BackupResult,
  RemoteAssistInstructions,
} from '@/types/support';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const supportKeys = {
  all: ['support'] as const,
  diagnostics: () => [...supportKeys.all, 'diagnostics'] as const,
  backups: () => [...supportKeys.all, 'backups'] as const,
  remoteAssist: () => [...supportKeys.all, 'remote-assist'] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

export function useDiagnosticsInfo() {
  return useQuery({
    queryKey: supportKeys.diagnostics(),
    queryFn: async (): Promise<DiagnosticsInfo> => {
      return await invoke('get_diagnostics_info');
    },
    staleTime: 0, // Always fetch fresh data
    gcTime: 0, // Don't cache
  });
}

export function useBackups() {
  return useQuery({
    queryKey: supportKeys.backups(),
    queryFn: async (): Promise<BackupResult[]> => {
      return await invoke('list_backups');
    },
  });
}

export function useRemoteAssistInstructions() {
  return useQuery({
    queryKey: supportKeys.remoteAssist(),
    queryFn: async (): Promise<RemoteAssistInstructions> => {
      return await invoke('get_remote_assist_instructions');
    },
    staleTime: Infinity, // Never refetch (OS doesn't change)
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

export function useExportSupportBundle() {
  return useMutation({
    mutationFn: async ({
      includeDatabase,
      outputPath,
    }: {
      includeDatabase: boolean;
      outputPath: string;
    }): Promise<SupportBundleResult> => {
      return await invoke('export_support_bundle', {
        includeDatabase,
        outputPath,
      });
    },
  });
}

export function useBackupDatabase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<BackupResult> => {
      return await invoke('backup_database');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supportKeys.backups() });
      queryClient.invalidateQueries({ queryKey: supportKeys.diagnostics() });
    },
  });
}

export function useRestoreDatabase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (backupPath: string): Promise<string> => {
      return await invoke('restore_database', { backupPath });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supportKeys.all });
    },
  });
}

export function useDeleteBackup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (backupPath: string): Promise<string> => {
      return await invoke('delete_backup', {
        backupPath,
        confirmDelete: true
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supportKeys.backups() });
      queryClient.invalidateQueries({ queryKey: supportKeys.diagnostics() });
    },
  });
}
