// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cassa Hooks
// TanStack Query hooks per gestione incassi
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  Incasso,
  CreateIncassoInput,
  ReportIncassiGiornata,
  ReportPeriodo,
  ChiusuraCassa,
  MetodoPagamento,
} from '../types/cassa';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const cassaKeys = {
  all: ['cassa'] as const,
  incassiOggi: () => [...cassaKeys.all, 'oggi'] as const,
  incassiGiornata: (data: string) => [...cassaKeys.all, 'giornata', data] as const,
  reportPeriodo: (inizio: string, fine: string) =>
    [...cassaKeys.all, 'report', inizio, fine] as const,
  chiusure: () => [...cassaKeys.all, 'chiusure'] as const,
  metodiPagamento: () => [...cassaKeys.all, 'metodi'] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/**
 * Hook per ottenere incassi di oggi
 */
export function useIncassiOggi() {
  return useQuery({
    queryKey: cassaKeys.incassiOggi(),
    queryFn: async (): Promise<ReportIncassiGiornata> => {
      return await invoke('get_incassi_oggi');
    },
    refetchInterval: 30000, // Refresh ogni 30 secondi
  });
}

/**
 * Hook per ottenere incassi di una giornata specifica
 */
export function useIncassiGiornata(data: string) {
  return useQuery({
    queryKey: cassaKeys.incassiGiornata(data),
    queryFn: async (): Promise<ReportIncassiGiornata> => {
      return await invoke('get_incassi_giornata', { data });
    },
    enabled: !!data,
  });
}

/**
 * Hook per ottenere report incassi per periodo
 */
export function useReportIncassiPeriodo(dataInizio: string, dataFine: string) {
  return useQuery({
    queryKey: cassaKeys.reportPeriodo(dataInizio, dataFine),
    queryFn: async (): Promise<ReportPeriodo> => {
      return await invoke('get_report_incassi_periodo', {
        dataInizio,
        dataFine,
      });
    },
    enabled: !!dataInizio && !!dataFine,
  });
}

/**
 * Hook per ottenere storico chiusure cassa
 */
export function useChiusureCassa(limit?: number) {
  return useQuery({
    queryKey: cassaKeys.chiusure(),
    queryFn: async (): Promise<ChiusuraCassa[]> => {
      return await invoke('get_chiusure_cassa', { limit });
    },
  });
}

/**
 * Hook per ottenere metodi di pagamento attivi
 */
export function useMetodiPagamento() {
  return useQuery({
    queryKey: cassaKeys.metodiPagamento(),
    queryFn: async (): Promise<MetodoPagamento[]> => {
      return await invoke('get_metodi_pagamento');
    },
    staleTime: Infinity, // Non cambia spesso
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/**
 * Hook per registrare un nuovo incasso
 */
export function useRegistraIncasso() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateIncassoInput): Promise<Incasso> => {
      return await invoke('registra_incasso', { input });
    },
    onSuccess: () => {
      // Invalida tutte le query cassa per refresh
      queryClient.invalidateQueries({ queryKey: cassaKeys.all });
    },
  });
}

/**
 * Hook per chiudere cassa
 */
export function useChiudiCassa() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      data: string;
      fondoCassaFinale: number;
      note?: string;
      operatoreId?: string;
    }): Promise<ChiusuraCassa> => {
      return await invoke('chiudi_cassa', {
        data: params.data,
        fondo_cassa_finale: params.fondoCassaFinale,
        note: params.note,
        operatore_id: params.operatoreId,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cassaKeys.all });
    },
  });
}

/**
 * Hook per eliminare incasso
 */
export function useEliminaIncasso() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      return await invoke('elimina_incasso', { id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cassaKeys.all });
    },
  });
}

// ───────────────────────────────────────────────────────────────────
// Utility Hooks
// ───────────────────────────────────────────────────────────────────

/**
 * Hook per ottenere data odierna formattata
 */
export function useDataOggi(): string {
  return new Date().toISOString().split('T')[0];
}

/**
 * Hook per verificare se cassa è già chiusa per una data
 */
export function useCassaChiusa(data: string) {
  const { data: chiusure } = useChiusureCassa();

  return chiusure?.some((c) => c.data_chiusura === data) ?? false;
}
