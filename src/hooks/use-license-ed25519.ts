// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Ed25519 Hooks
// TanStack Query hooks per gestione licenze offline Ed25519
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { 
  LicenseStatusEd25519, 
  ActivationResultEd25519, 
  TierInfo 
} from '../types/license-ed25519';

// ─────────────────────────────────────────────────────────────────────
// QUERY KEYS
// ─────────────────────────────────────────────────────────────────────

export const licenseEd25519Keys = {
  all: ['license-ed25519'] as const,
  status: () => [...licenseEd25519Keys.all, 'status'] as const,
  tierInfo: () => [...licenseEd25519Keys.all, 'tier-info'] as const,
  feature: (feature: string) => [...licenseEd25519Keys.all, 'feature', feature] as const,
  vertical: (vertical: string) => [...licenseEd25519Keys.all, 'vertical', vertical] as const,
};

// ─────────────────────────────────────────────────────────────────────
// QUERIES
// ─────────────────────────────────────────────────────────────────────

/**
 * Hook per ottenere lo stato licenza Ed25519
 */
export function useLicenseStatusEd25519() {
  return useQuery({
    queryKey: licenseEd25519Keys.status(),
    queryFn: async (): Promise<LicenseStatusEd25519> => {
      return await invoke('get_license_status_ed25519');
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    refetchInterval: 1000 * 60 * 5, // Refetch ogni 5 minuti
  });
}

/**
 * Hook per ottenere info tier
 */
export function useTierInfoEd25519() {
  return useQuery({
    queryKey: licenseEd25519Keys.tierInfo(),
    queryFn: async (): Promise<TierInfo[]> => {
      return await invoke('get_tier_info_ed25519');
    },
    staleTime: 1000 * 60 * 60, // 1 ora
  });
}

/**
 * Hook per verificare accesso a funzionalità
 */
export function useFeatureAccessEd25519(feature: string) {
  return useQuery({
    queryKey: licenseEd25519Keys.feature(feature),
    queryFn: async (): Promise<boolean> => {
      return await invoke('check_feature_access_ed25519', { feature });
    },
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook per verificare accesso a verticale
 */
export function useVerticalAccessEd25519(vertical: string) {
  return useQuery({
    queryKey: licenseEd25519Keys.vertical(vertical),
    queryFn: async (): Promise<boolean> => {
      return await invoke('check_vertical_access_ed25519', { vertical });
    },
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook per ottenere fingerprint macchina
 */
export function useMachineFingerprint() {
  return useQuery({
    queryKey: ['machine-fingerprint'],
    queryFn: async (): Promise<string> => {
      return await invoke('get_machine_fingerprint_ed25519');
    },
    staleTime: Infinity, // Fingerprint non cambia
  });
}

// ─────────────────────────────────────────────────────────────────────
// MUTATIONS
// ─────────────────────────────────────────────────────────────────────

/**
 * Hook per attivare licenza Ed25519
 */
export function useActivateLicenseEd25519() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (licenseData: string): Promise<ActivationResultEd25519> => {
      return await invoke('activate_license_ed25519', { licenseData });
    },
    onSuccess: () => {
      // Invalida tutte le query licenza
      queryClient.invalidateQueries({ queryKey: licenseEd25519Keys.all });
    },
  });
}

/**
 * Hook per disattivare licenza (ritorna a trial)
 */
export function useDeactivateLicenseEd25519() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<void> => {
      return await invoke('deactivate_license_ed25519');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: licenseEd25519Keys.all });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// UTILITY HOOKS
// ─────────────────────────────────────────────────────────────────────

/**
 * Hook combinato per info licenza complete
 */
export function useLicenseInfo() {
  const statusQuery = useLicenseStatusEd25519();
  const tierInfoQuery = useTierInfoEd25519();
  const fingerprintQuery = useMachineFingerprint();

  return {
    status: statusQuery.data,
    tierInfo: tierInfoQuery.data,
    fingerprint: fingerprintQuery.data,
    isLoading: statusQuery.isLoading || tierInfoQuery.isLoading || fingerprintQuery.isLoading,
    isError: statusQuery.isError || tierInfoQuery.isError || fingerprintQuery.isError,
    refetch: () => {
      statusQuery.refetch();
      tierInfoQuery.refetch();
    },
  };
}

/**
 * Hook per verificare se utente ha licenza valida
 */
export function useHasValidLicense() {
  const { data: status } = useLicenseStatusEd25519();
  return status?.is_valid ?? false;
}

/**
 * Hook per verificare se utente è in trial
 */
export function useIsTrial() {
  const { data: status } = useLicenseStatusEd25519();
  return status?.tier === 'trial';
}

/**
 * Hook per verificare se trial sta per scadere
 */
export function useIsTrialExpiring() {
  const { data: status } = useLicenseStatusEd25519();
  if (!status || status.tier !== 'trial') return false;
  return (status.days_remaining || 0) <= 7;
}

/**
 * Hook per ottenere tier corrente
 */
export function useCurrentTier() {
  const { data: status } = useLicenseStatusEd25519();
  return status?.tier || 'none';
}
