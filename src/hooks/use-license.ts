// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Hooks (Phase 8)
// TanStack Query hooks for license management
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import {
  LicenseStatus,
  LicenseStatusSchema,
  ActivationResult,
  ActivationResultSchema,
} from '@/types/license';

// ─── Query Keys ──────────────────────────────────────────────────────

export const licenseKeys = {
  all: ['license'] as const,
  status: () => [...licenseKeys.all, 'status'] as const,
  fingerprint: () => [...licenseKeys.all, 'fingerprint'] as const,
  featureAccess: (feature: string) => [...licenseKeys.all, 'feature', feature] as const,
};

// ─── Get License Status ──────────────────────────────────────────────

export function useLicenseStatus() {
  return useQuery({
    queryKey: licenseKeys.status(),
    queryFn: async (): Promise<LicenseStatus> => {
      const result = await invoke<LicenseStatus>('get_license_status');
      return LicenseStatusSchema.parse(result);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: true,
  });
}

// ─── Get Machine Fingerprint ─────────────────────────────────────────

export function useMachineFingerprint() {
  return useQuery({
    queryKey: licenseKeys.fingerprint(),
    queryFn: async (): Promise<string> => {
      return invoke<string>('get_machine_fingerprint');
    },
    staleTime: Infinity, // Fingerprint doesn't change
  });
}

// ─── Activate License ────────────────────────────────────────────────

export function useActivateLicense() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (licenseKey: string): Promise<ActivationResult> => {
      const result = await invoke<ActivationResult>('activate_license', {
        licenseKey,
      });
      return ActivationResultSchema.parse(result);
    },
    onSuccess: () => {
      // Invalidate license status to refresh
      queryClient.invalidateQueries({ queryKey: licenseKeys.status() });
    },
  });
}

// ─── Deactivate License ──────────────────────────────────────────────

export function useDeactivateLicense() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<void> => {
      await invoke('deactivate_license');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: licenseKeys.status() });
    },
  });
}

// ─── Validate License Online ─────────────────────────────────────────

export function useValidateLicenseOnline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<LicenseStatus> => {
      const result = await invoke<LicenseStatus>('validate_license_online');
      return LicenseStatusSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(licenseKeys.status(), data);
    },
  });
}

// ─── Check Feature Access ────────────────────────────────────────────

export function useFeatureAccess(feature: string) {
  return useQuery({
    queryKey: licenseKeys.featureAccess(feature),
    queryFn: async (): Promise<boolean> => {
      return invoke<boolean>('check_feature_access', { feature });
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// ─── Helper Hook for License Gate ────────────────────────────────────

export function useLicenseGate() {
  const { data: status, isLoading } = useLicenseStatus();

  return {
    isLoading,
    isValid: status?.is_valid ?? false,
    isActivated: status?.is_activated ?? false,
    isTrial: status?.tier === 'trial',
    isExpired: !status?.is_valid && (status?.tier === 'expired' || status?.tier === 'trial'),
    tier: status?.tier ?? 'none',
    daysRemaining: status?.days_remaining,
    needsActivation: !status?.is_valid && !isLoading,
  };
}
