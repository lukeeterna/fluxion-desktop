// ═══════════════════════════════════════════════════════════════════
// FLUXION - Orari & Festività Hooks
// TanStack Query hooks for working hours and holidays
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  OrarioLavoro,
  GiornoFestivo,
  CreateOrarioLavoroInput,
  CreateGiornoFestivoInput,
  ValidazioneOrarioResult,
} from '@/types/orari';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const orariKeys = {
  all: ['orari'] as const,
  orariLavoro: () => [...orariKeys.all, 'lavoro'] as const,
  orarioLavoro: (giorno?: number, operatore?: string) =>
    [...orariKeys.orariLavoro(), { giorno, operatore }] as const,
  festivi: () => [...orariKeys.all, 'festivi'] as const,
  festiviAnno: (anno?: number) => [...orariKeys.festivi(), { anno }] as const,
};

// ───────────────────────────────────────────────────────────────────
// Orari Lavoro - Queries
// ───────────────────────────────────────────────────────────────────

export function useOrariLavoro(giorno?: number, operatore_id?: string) {
  return useQuery({
    queryKey: orariKeys.orarioLavoro(giorno, operatore_id),
    queryFn: async () => {
      const orari = await invoke<OrarioLavoro[]>('get_orari_lavoro', {
        giornoSettimana: giorno,
        operatoreId: operatore_id,
      });
      return orari;
    },
  });
}

export function useCreateOrarioLavoro() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateOrarioLavoroInput) => {
      const orario = await invoke<OrarioLavoro>('create_orario_lavoro', { input });
      return orario;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orariKeys.orariLavoro() });
    },
  });
}

export function useDeleteOrarioLavoro() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await invoke('delete_orario_lavoro', { id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orariKeys.orariLavoro() });
    },
  });
}

// ───────────────────────────────────────────────────────────────────
// Giorni Festivi - Queries
// ───────────────────────────────────────────────────────────────────

export function useGiorniFestivi(anno?: number) {
  return useQuery({
    queryKey: orariKeys.festiviAnno(anno),
    queryFn: async () => {
      const festivi = await invoke<GiornoFestivo[]>('get_giorni_festivi', { anno });
      return festivi;
    },
  });
}

export function useIsGiornoFestivo(data: string) {
  return useQuery({
    queryKey: [...orariKeys.festivi(), 'check', data],
    queryFn: async () => {
      const isFestivo = await invoke<boolean>('is_giorno_festivo', { data });
      return isFestivo;
    },
    enabled: !!data,
  });
}

export function useCreateGiornoFestivo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateGiornoFestivoInput) => {
      const festivo = await invoke<GiornoFestivo>('create_giorno_festivo', { input });
      return festivo;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orariKeys.festivi() });
    },
  });
}

export function useDeleteGiornoFestivo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await invoke('delete_giorno_festivo', { id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orariKeys.festivi() });
    },
  });
}

// ───────────────────────────────────────────────────────────────────
// Validazione Orario
// ───────────────────────────────────────────────────────────────────

export function useValidaOrarioAppuntamento() {
  return useMutation({
    mutationFn: async ({
      data_ora_inizio,
      durata_minuti,
      operatore_id,
    }: {
      data_ora_inizio: string;
      durata_minuti: number;
      operatore_id?: string;
    }) => {
      const result = await invoke<ValidazioneOrarioResult>('valida_orario_appuntamento', {
        dataOraInizio: data_ora_inizio,
        durataMinuti: durata_minuti,
        operatoreId: operatore_id,
      });
      return result;
    },
  });
}
