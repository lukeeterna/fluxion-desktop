// ═══════════════════════════════════════════════════════════════════
// FLUXION - Schede Cliente Hooks
// TanStack Query hooks per gestione schede verticali
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { 
  SchedaOdontoiatrica, 
  SchedaFisioterapia, 
  SchedaEstetica,
  SchedaParrucchiere,
  SchedaVeicoli,
  SchedaCarrozzeria 
} from '../types/scheda-cliente';

// ─────────────────────────────────────────────────────────────────────
// QUERY KEYS
// ─────────────────────────────────────────────────────────────────────

export const schedeKeys = {
  all: ['schede'] as const,
  odontoiatrica: (clienteId: string) => [...schedeKeys.all, 'odontoiatrica', clienteId] as const,
  fisioterapia: (clienteId: string) => [...schedeKeys.all, 'fisioterapia', clienteId] as const,
  estetica: (clienteId: string) => [...schedeKeys.all, 'estetica', clienteId] as const,
  parrucchiere: (clienteId: string) => [...schedeKeys.all, 'parrucchiere', clienteId] as const,
  veicoli: (clienteId: string) => [...schedeKeys.all, 'veicoli', clienteId] as const,
  carrozzeria: (clienteId: string) => [...schedeKeys.all, 'carrozzeria', clienteId] as const,
};

// ─────────────────────────────────────────────────────────────────────
// SCHEDA ODONTOIATRICA
// ─────────────────────────────────────────────────────────────────────

export function useSchedaOdontoiatrica(clienteId: string) {
  return useQuery({
    queryKey: schedeKeys.odontoiatrica(clienteId),
    queryFn: async (): Promise<SchedaOdontoiatrica | null> => {
      try {
        return await invoke('get_scheda_odontoiatrica', { clienteId });
      } catch (error) {
        console.error('Errore caricamento scheda odontoiatrica:', error);
        return null;
      }
    },
    enabled: !!clienteId,
    staleTime: 1000 * 60 * 5, // 5 minuti
  });
}

export function useSaveSchedaOdontoiatrica() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clienteId, data }: { clienteId: string; data: SchedaOdontoiatrica }) => {
      return await invoke('upsert_scheda_odontoiatrica', { clienteId, data });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: schedeKeys.odontoiatrica(variables.clienteId) 
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// SCHEDA FISIOTERAPIA
// ─────────────────────────────────────────────────────────────────────

export function useSchedaFisioterapia(clienteId: string) {
  return useQuery({
    queryKey: schedeKeys.fisioterapia(clienteId),
    queryFn: async (): Promise<SchedaFisioterapia | null> => {
      try {
        return await invoke('get_scheda_fisioterapia', { clienteId });
      } catch (error) {
        console.error('Errore caricamento scheda fisioterapia:', error);
        return null;
      }
    },
    enabled: !!clienteId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useSaveSchedaFisioterapia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clienteId, data }: { clienteId: string; data: SchedaFisioterapia }) => {
      return await invoke('upsert_scheda_fisioterapia', { clienteId, data });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: schedeKeys.fisioterapia(variables.clienteId) 
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// SCHEDA ESTETICA
// ─────────────────────────────────────────────────────────────────────

export function useSchedaEstetica(clienteId: string) {
  return useQuery({
    queryKey: schedeKeys.estetica(clienteId),
    queryFn: async (): Promise<SchedaEstetica | null> => {
      try {
        return await invoke('get_scheda_estetica', { clienteId });
      } catch (error) {
        console.error('Errore caricamento scheda estetica:', error);
        return null;
      }
    },
    enabled: !!clienteId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useSaveSchedaEstetica() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clienteId, data }: { clienteId: string; data: SchedaEstetica }) => {
      return await invoke('upsert_scheda_estetica', { clienteId, data });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: schedeKeys.estetica(variables.clienteId) 
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// SCHEDA PARRUCCHIERE
// ─────────────────────────────────────────────────────────────────────

export function useSchedaParrucchiere(clienteId: string) {
  return useQuery({
    queryKey: schedeKeys.parrucchiere(clienteId),
    queryFn: async (): Promise<SchedaParrucchiere | null> => {
      try {
        return await invoke('get_scheda_parrucchiere', { clienteId });
      } catch (error) {
        console.error('Errore caricamento scheda parrucchiere:', error);
        return null;
      }
    },
    enabled: !!clienteId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useSaveSchedaParrucchiere() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clienteId, data }: { clienteId: string; data: SchedaParrucchiere }) => {
      return await invoke('upsert_scheda_parrucchiere', { clienteId, data });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: schedeKeys.parrucchiere(variables.clienteId) 
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// SCHEDA VEICOLI
// ─────────────────────────────────────────────────────────────────────

export function useSchedaVeicoli(clienteId: string) {
  return useQuery({
    queryKey: schedeKeys.veicoli(clienteId),
    queryFn: async (): Promise<SchedaVeicoli[] | null> => {
      try {
        return await invoke('get_schede_veicoli', { clienteId });
      } catch (error) {
        console.error('Errore caricamento schede veicoli:', error);
        return null;
      }
    },
    enabled: !!clienteId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useSaveSchedaVeicoli() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clienteId, data }: { clienteId: string; data: SchedaVeicoli }) => {
      return await invoke('upsert_scheda_veicoli', { clienteId, data });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: schedeKeys.veicoli(variables.clienteId) 
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// SCHEDA CARROZZERIA
// ─────────────────────────────────────────────────────────────────────

export function useSchedaCarrozzeria(clienteId: string) {
  return useQuery({
    queryKey: schedeKeys.carrozzeria(clienteId),
    queryFn: async (): Promise<SchedaCarrozzeria[] | null> => {
      try {
        return await invoke('get_schede_carrozzeria', { clienteId });
      } catch (error) {
        console.error('Errore caricamento schede carrozzeria:', error);
        return null;
      }
    },
    enabled: !!clienteId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useSaveSchedaCarrozzeria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clienteId, data }: { clienteId: string; data: SchedaCarrozzeria }) => {
      return await invoke('upsert_scheda_carrozzeria', { clienteId, data });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: schedeKeys.carrozzeria(variables.clienteId) 
      });
    },
  });
}
