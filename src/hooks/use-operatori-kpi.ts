// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori KPI Hooks (B4)
// TanStack Query hooks per statistiche mensili operatori (v_kpi_operatori)
// ═══════════════════════════════════════════════════════════════════

import { useQuery } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export interface KpiOperatore {
  id: string;
  nome_completo: string;
  mese: string | null;
  appuntamenti_completati: number;
  no_show: number;
  clienti_unici: number;
  fatturato_generato: number;
  ticket_medio: number | null;
}

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const kpiOperatoreKeys = {
  all: ['kpi-operatore'] as const,
  storico: (operatoreId: string, mesi: number) =>
    [...kpiOperatoreKeys.all, 'storico', operatoreId, mesi] as const,
};

// ───────────────────────────────────────────────────────────────────
// Hooks
// ───────────────────────────────────────────────────────────────────

/// Ritorna KPI mensili storici per un operatore (ultimi N mesi con dati)
export function useKpiOperatoreStorico(operatoreId: string, mesi = 12) {
  return useQuery({
    queryKey: kpiOperatoreKeys.storico(operatoreId, mesi),
    queryFn: () =>
      invoke<KpiOperatore[]>('get_kpi_operatore_storico', { operatoreId, mesi }),
    enabled: !!operatoreId,
  });
}
