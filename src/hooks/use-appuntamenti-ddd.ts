// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamenti DDD Hooks
// TanStack Query hooks for DDD-layer appuntamenti workflow
// ═══════════════════════════════════════════════════════════════════

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import { toast } from 'sonner';
import type {
  CreaAppuntamentoBozzaDto,
  ProponiAppuntamentoDto,
  ConfermaConOverrideDto,
  RifiutaAppuntamentoDto,
  AppuntamentoDto,
} from '@/types/appuntamento-ddd.types';
import {
  AppuntamentoDtoSchema,
  ProponiAppuntamentoResponseSchema,
} from '@/types/appuntamento-ddd.types';
import { appuntamentiKeys } from './use-appuntamenti';

// Helper to extract error message from unknown error
function getErrorMessage(error: unknown): string {
  if (typeof error === 'string') return error;
  if (error instanceof Error) return error.message;
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: unknown }).message);
  }
  return 'Unknown error';
}

// ───────────────────────────────────────────────────────────────────
// Mutations - State Machine Workflow
// ───────────────────────────────────────────────────────────────────

/**
 * Crea bozza appuntamento (stato: Bozza)
 *
 * @example
 * const { mutate } = useCreaAppuntamentoBozza();
 * mutate({
 *   cliente_id: "...",
 *   operatore_id: "...",
 *   servizio_id: "...",
 *   data_ora: "2026-01-15T14:00:00",
 *   durata_minuti: 60
 * });
 */
export function useCreaAppuntamentoBozza() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (dto: CreaAppuntamentoBozzaDto) => {
      const result = await invoke<unknown>('crea_appuntamento_bozza', { dto });
      return AppuntamentoDtoSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      toast.success('Bozza appuntamento creata', {
        description: `ID: ${data.id}`,
      });
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore creazione bozza', {
        description: errorMsg,
      });
    },
  });
}

/**
 * Valida e proponi appuntamento (stato: Bozza → Proposta)
 *
 * Esegue validazione 3-layer e ritorna validation result con:
 * - hard_blocks: errori bloccanti (impossibile procedere)
 * - warnings: avvisi continuabili con conferma operatore
 * - suggestions: suggerimenti proattivi
 *
 * @example
 * const { mutate, data } = usePropon iAppuntamento();
 * mutate({ appuntamento_id: "..." });
 * if (data?.validation.is_blocked) {
 *   // Mostra hard blocks
 * } else if (data?.validation.has_warnings) {
 *   // Mostra dialog conferma warnings
 * }
 */
export function useProponiAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (dto: ProponiAppuntamentoDto) => {
      const result = await invoke<unknown>('proponi_appuntamento', { dto });
      return ProponiAppuntamentoResponseSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.appuntamento.id) });

      if (data.validation.is_blocked) {
        toast.error('Validazione fallita', {
          description: `${data.validation.hard_blocks.length} errori bloccanti`,
        });
      } else if (data.validation.has_warnings) {
        toast.warning('Appuntamento proposto con avvisi', {
          description: `${data.validation.warnings.length} avvisi da confermare`,
        });
      } else {
        toast.success('Appuntamento proposto', {
          description: 'Nessun problema rilevato',
        });
      }
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore validazione', {
        description: errorMsg,
      });
    },
  });
}

/**
 * Cliente conferma proposta (stato: Proposta → InAttesaOperatore)
 *
 * Invia notifica all'operatore per conferma/rifiuto.
 *
 * @example
 * const { mutate } = useConfermaClienteAppuntamento();
 * mutate("appuntamento-id");
 */
export function useConfermaClienteAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (appuntamentoId: string) => {
      const result = await invoke<unknown>('conferma_cliente_appuntamento', {
        appuntamentoId,
      });
      return AppuntamentoDtoSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
      toast.success('Conferma cliente registrata', {
        description: 'In attesa conferma operatore',
      });
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore conferma cliente', {
        description: errorMsg,
      });
    },
  });
}

/**
 * Operatore accetta appuntamento (stato: InAttesaOperatore → Confermato)
 *
 * @example
 * const { mutate } = useConfermaOperatoreAppuntamento();
 * mutate("appuntamento-id");
 */
export function useConfermaOperatoreAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (appuntamentoId: string) => {
      const result = await invoke<unknown>('conferma_operatore_appuntamento', {
        appuntamentoId,
      });
      return AppuntamentoDtoSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
      toast.success('Appuntamento confermato', {
        description: 'Operatore ha accettato l\'appuntamento',
      });
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore conferma operatore', {
        description: errorMsg,
      });
    },
  });
}

/**
 * Operatore forza conferma con override (stato: InAttesaOperatore → ConfermatoConOverride)
 *
 * Ignora warnings specificati con tracking audit trail:
 * - timestamp override
 * - operatore_id
 * - motivazione (opzionale)
 * - warnings_ignorati (lista tipi warning)
 *
 * @example
 * const { mutate } = useConfermaConOverrideAppuntamento();
 * mutate({
 *   appuntamento_id: "...",
 *   operatore_id: "...",
 *   motivazione: "Cliente urgente",
 *   warnings_ignorati: ["GiornoFestivo", "FuoriOrarioLavorativo"]
 * });
 */
export function useConfermaConOverrideAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (dto: ConfermaConOverrideDto) => {
      const result = await invoke<unknown>('conferma_con_override_appuntamento', { dto });
      return AppuntamentoDtoSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
      toast.warning('Appuntamento confermato con override', {
        description: `${data.override_info?.warnings_ignorati.length || 0} avvisi ignorati`,
      });
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore conferma con override', {
        description: errorMsg,
      });
    },
  });
}

/**
 * Operatore rifiuta appuntamento (stato: InAttesaOperatore → Rifiutato)
 *
 * @example
 * const { mutate } = useRifiutaAppuntamento();
 * mutate({
 *   appuntamento_id: "...",
 *   motivazione: "Non disponibile"
 * });
 */
export function useRifiutaAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (dto: RifiutaAppuntamentoDto) => {
      const result = await invoke<unknown>('rifiuta_appuntamento', { dto });
      return AppuntamentoDtoSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
      toast.error('Appuntamento rifiutato', {
        description: data.note || 'Rifiutato da operatore',
      });
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore rifiuto appuntamento', {
        description: errorMsg,
      });
    },
  });
}

/**
 * Cancella appuntamento (soft delete)
 *
 * Disponibile per stati: Bozza, Proposta, Confermato, ConfermatoConOverride
 *
 * @example
 * const { mutate } = useCancellaAppuntamentoDdd();
 * mutate("appuntamento-id");
 */
export function useCancellaAppuntamentoDdd() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (appuntamentoId: string) => {
      const result = await invoke<unknown>('cancella_appuntamento_ddd', {
        appuntamentoId,
      });
      return AppuntamentoDtoSchema.parse(result);
    },
    // Optimistic update
    onMutate: async (appuntamentoId) => {
      await queryClient.cancelQueries({ queryKey: appuntamentiKeys.lists() });

      const previousData = queryClient.getQueryData(appuntamentiKeys.lists());

      // Rimuovi appuntamento da tutte le liste
      queryClient.setQueriesData<AppuntamentoDto[]>({ queryKey: appuntamentiKeys.lists() }, (old) => {
        if (!old) return old;
        return old.filter((app) => app.id !== appuntamentoId);
      });

      return { previousData };
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
      toast.success('Appuntamento cancellato', {
        description: 'Cancellazione registrata',
      });
    },
    onError: (error: unknown, _variables, context) => {
      // Rollback optimistic update
      if (context?.previousData) {
        queryClient.setQueryData(appuntamentiKeys.lists(), context.previousData);
      }

      const errorMsg = getErrorMessage(error);
      toast.error('Errore cancellazione', {
        description: errorMsg,
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
    },
  });
}

/**
 * Sistema completa appuntamento automaticamente (stato: Confermato → Completato)
 *
 * Chiamato automaticamente da cron job quando data/ora appuntamento è passata.
 * Può anche essere chiamato manualmente dall'operatore.
 *
 * @example
 * const { mutate } = useCompletaAppuntamentoAuto();
 * mutate("appuntamento-id");
 */
export function useCompletaAppuntamentoAuto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (appuntamentoId: string) => {
      const result = await invoke<unknown>('completa_appuntamento_auto', {
        appuntamentoId,
      });
      return AppuntamentoDtoSchema.parse(result);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.lists() });
      queryClient.invalidateQueries({ queryKey: appuntamentiKeys.detail(data.id) });
      toast.success('Appuntamento completato', {
        description: 'Servizio erogato con successo',
      });
    },
    onError: (error: unknown) => {
      const errorMsg = getErrorMessage(error);
      toast.error('Errore completamento', {
        description: errorMsg,
      });
    },
  });
}
