// ═══════════════════════════════════════════════════════════════════
// FLUXION - Magazzino Hooks
// TanStack Query hooks per articoli, movimenti e alert sottoscorta
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  Articolo,
  MovimentoMagazzino,
  CreaArticoloInput,
  AggiornaArticoloInput,
  RegistraMovimentoInput,
  SetSogliaInput,
} from '@/types/magazzino';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const magazzinoKeys = {
  all: ['magazzino'] as const,
  lista: () => [...magazzinoKeys.all, 'lista'] as const,
  sottoscorta: () => [...magazzinoKeys.all, 'sottoscorta'] as const,
  alertCount: () => [...magazzinoKeys.all, 'alertCount'] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/** Lista completa articoli attivi */
export function useArticoli() {
  return useQuery({
    queryKey: magazzinoKeys.lista(),
    queryFn: () => invoke<Articolo[]>('articolo_lista'),
  });
}

/** Articoli sottoscorta (ordinati per urgenza) */
export function useSottoscorta() {
  return useQuery({
    queryKey: magazzinoKeys.sottoscorta(),
    queryFn: () => invoke<Articolo[]>('magazzino_sottoscorta'),
  });
}

/** Conteggio articoli sottoscorta — usato per il badge sidebar */
export function useMagazzinoAlertCount() {
  return useQuery({
    queryKey: magazzinoKeys.alertCount(),
    queryFn: () => invoke<number>('magazzino_alert_count'),
    staleTime: 60 * 1000, // 1 minuto
    refetchInterval: 5 * 60 * 1000,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/** Crea nuovo articolo */
export function useCreaArticolo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CreaArticoloInput) =>
      invoke<Articolo>('articolo_crea', {
        nome: input.nome,
        categoria: input.categoria,
        sogliaMinima: input.sogliaMinima,
        prezzoAcquisto: input.prezzoAcquisto,
        prezzoVendita: input.prezzoVendita,
        ean: input.ean,
        fornitoreId: input.fornitoreId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.lista() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.sottoscorta() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.alertCount() });
    },
  });
}

/** Aggiorna articolo esistente */
export function useAggiornaArticolo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: AggiornaArticoloInput) =>
      invoke<Articolo>('articolo_aggiorna', {
        id: input.id,
        nome: input.nome,
        categoria: input.categoria,
        sogliaMinima: input.sogliaMinima,
        prezzoAcquisto: input.prezzoAcquisto,
        prezzoVendita: input.prezzoVendita,
        ean: input.ean,
        fornitoreId: input.fornitoreId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.lista() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.sottoscorta() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.alertCount() });
    },
  });
}

/** Soft-delete articolo (attivo = 0) */
export function useEliminaArticolo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoke<void>('articolo_elimina', { id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.all });
    },
  });
}

/** Imposta soglia minima per un articolo */
export function useSetSoglia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: SetSogliaInput) =>
      invoke<Articolo>('articolo_set_soglia', {
        id: input.id,
        sogliaMinima: input.sogliaMinima,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.lista() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.sottoscorta() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.alertCount() });
    },
  });
}

/** Registra movimento carico o scarico */
export function useRegistraMovimento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: RegistraMovimentoInput) =>
      invoke<MovimentoMagazzino>('movimento_registra', {
        articoloId: input.articoloId,
        tipo: input.tipo,
        quantita: input.quantita,
        causale: input.causale,
        riferimento: input.riferimento,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.lista() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.sottoscorta() });
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.alertCount() });
    },
  });
}

/** Ricalcola tutti gli alert al boot — idempotente */
export function useRecomputeAlerts() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => invoke<number>('magazzino_recompute_alerts'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: magazzinoKeys.all });
    },
  });
}
