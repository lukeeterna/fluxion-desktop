// ═══════════════════════════════════════════════════════════════════
// FLUXION - Loyalty & Pacchetti Hooks (Fase 5)
// TanStack Query hooks per tessera timbri, VIP, referral, pacchetti
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { invoke } from '@tauri-apps/api/core'
import type {
  LoyaltyInfo,
  Pacchetto,
  ClientePacchetto,
  TopReferrer,
  CreatePacchetto,
  PacchettoServizio,
} from '@/types/loyalty'

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const loyaltyKeys = {
  all: ['loyalty'] as const,
  info: (clienteId: string) => [...loyaltyKeys.all, 'info', clienteId] as const,
  milestones: () => [...loyaltyKeys.all, 'milestones'] as const,
  referrers: () => [...loyaltyKeys.all, 'referrers'] as const,
}

export const pacchettiKeys = {
  all: ['pacchetti'] as const,
  list: () => [...pacchettiKeys.all, 'list'] as const,
  cliente: (clienteId: string) =>
    [...pacchettiKeys.all, 'cliente', clienteId] as const,
  detail: (id: string) => [...pacchettiKeys.all, 'detail', id] as const,
}

// ───────────────────────────────────────────────────────────────────
// Loyalty Queries
// ───────────────────────────────────────────────────────────────────

/** Get loyalty info for a specific cliente */
export function useLoyaltyInfo(clienteId: string | undefined) {
  return useQuery({
    queryKey: loyaltyKeys.info(clienteId ?? ''),
    queryFn: () =>
      invoke<LoyaltyInfo>('get_loyalty_info', { clienteId: clienteId! }),
    enabled: !!clienteId,
    staleTime: 30 * 1000, // 30 seconds
  })
}

/** Get clienti prossimi al traguardo loyalty */
export function useLoyaltyMilestones(visitsRemainingMax?: number) {
  return useQuery({
    queryKey: loyaltyKeys.milestones(),
    queryFn: () =>
      invoke<LoyaltyInfo[]>('get_loyalty_milestones', {
        visitsRemainingMax: visitsRemainingMax ?? 3,
      }),
    staleTime: 60 * 1000, // 1 minute
  })
}

/** Get top referrers */
export function useTopReferrers(limit?: number) {
  return useQuery({
    queryKey: loyaltyKeys.referrers(),
    queryFn: () => invoke<TopReferrer[]>('get_top_referrers', { limit }),
    staleTime: 60 * 1000, // 1 minute
  })
}

// ───────────────────────────────────────────────────────────────────
// Loyalty Mutations
// ───────────────────────────────────────────────────────────────────

/** Increment loyalty visits (chiamato quando appuntamento completato) */
export function useIncrementLoyaltyVisits() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (clienteId: string) =>
      invoke<LoyaltyInfo>('increment_loyalty_visits', { clienteId }),
    onSuccess: (data) => {
      queryClient.setQueryData(loyaltyKeys.info(data.cliente_id), data)
      queryClient.invalidateQueries({ queryKey: loyaltyKeys.milestones() })
    },
  })
}

/** Toggle VIP status */
export function useToggleVipStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ clienteId, isVip }: { clienteId: string; isVip: boolean }) =>
      invoke<boolean>('toggle_vip_status', { clienteId, isVip }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: loyaltyKeys.info(variables.clienteId),
      })
    },
  })
}

/** Set referral source */
export function useSetReferralSource() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      clienteId,
      referralSource,
      referralClienteId,
    }: {
      clienteId: string
      referralSource?: string
      referralClienteId?: string
    }) =>
      invoke('set_referral_source', {
        clienteId,
        referralSource: referralSource ?? null,
        referralClienteId: referralClienteId ?? null,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: loyaltyKeys.info(variables.clienteId),
      })
      queryClient.invalidateQueries({ queryKey: loyaltyKeys.referrers() })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Pacchetti Queries
// ───────────────────────────────────────────────────────────────────

/** Get all active pacchetti */
export function usePacchetti() {
  return useQuery({
    queryKey: pacchettiKeys.list(),
    queryFn: () => invoke<Pacchetto[]>('get_pacchetti'),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/** Get pacchetti for a specific cliente */
export function useClientePacchetti(clienteId: string | undefined) {
  return useQuery({
    queryKey: pacchettiKeys.cliente(clienteId ?? ''),
    queryFn: () =>
      invoke<ClientePacchetto[]>('get_cliente_pacchetti', {
        clienteId: clienteId!,
      }),
    enabled: !!clienteId,
    staleTime: 30 * 1000,
  })
}

/** Get single cliente pacchetto detail */
export function useClientePacchetto(clientePacchettoId: string | undefined) {
  return useQuery({
    queryKey: pacchettiKeys.detail(clientePacchettoId ?? ''),
    queryFn: () =>
      invoke<ClientePacchetto>('get_cliente_pacchetto', {
        clientePacchettoId: clientePacchettoId!,
      }),
    enabled: !!clientePacchettoId,
  })
}

// ───────────────────────────────────────────────────────────────────
// Pacchetti Mutations
// ───────────────────────────────────────────────────────────────────

/** Create a new pacchetto */
export function useCreatePacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreatePacchetto) =>
      invoke<Pacchetto>('create_pacchetto', {
        nome: data.nome,
        descrizione: data.descrizione ?? null,
        prezzo: data.prezzo,
        prezzoOriginale: data.prezzo_originale ?? null,
        serviziInclusi: data.servizi_inclusi,
        validitaGiorni: data.validita_giorni ?? null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pacchettiKeys.list() })
    },
  })
}

/** Propose pacchetto to cliente */
export function useProponiPacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      clienteId,
      pacchettoId,
    }: {
      clienteId: string
      pacchettoId: string
    }) => invoke<ClientePacchetto>('proponi_pacchetto', { clienteId, pacchettoId }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: pacchettiKeys.cliente(data.cliente_id),
      })
    },
  })
}

/** Confirm pacchetto purchase */
export function useConfermaAcquistoPacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      clientePacchettoId,
      metodoPagamento,
      validitaGiorni,
    }: {
      clientePacchettoId: string
      metodoPagamento: string
      validitaGiorni: number
    }) =>
      invoke<ClientePacchetto>('conferma_acquisto_pacchetto', {
        clientePacchettoId,
        metodoPagamento,
        validitaGiorni,
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: pacchettiKeys.cliente(data.cliente_id),
      })
      queryClient.setQueryData(pacchettiKeys.detail(data.id), data)
    },
  })
}

/** Use a service from pacchetto */
export function useUsaServizioPacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (clientePacchettoId: string) =>
      invoke<ClientePacchetto>('usa_servizio_pacchetto', { clientePacchettoId }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: pacchettiKeys.cliente(data.cliente_id),
      })
      queryClient.setQueryData(pacchettiKeys.detail(data.id), data)
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Pacchetto Management (Delete, Update, Servizi)
// ───────────────────────────────────────────────────────────────────

/** Delete a pacchetto (soft delete) */
export function useDeletePacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (pacchettoId: string) =>
      invoke<boolean>('delete_pacchetto', { pacchettoId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pacchettiKeys.list() })
    },
  })
}

/** Update an existing pacchetto */
export function useUpdatePacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      pacchettoId: string
      nome: string
      descrizione?: string
      prezzo: number
      prezzoOriginale?: number
      serviziInclusi: number
      validitaGiorni: number
    }) =>
      invoke<Pacchetto>('update_pacchetto', {
        pacchettoId: data.pacchettoId,
        nome: data.nome,
        descrizione: data.descrizione ?? null,
        prezzo: data.prezzo,
        prezzoOriginale: data.prezzoOriginale ?? null,
        serviziInclusi: data.serviziInclusi,
        validitaGiorni: data.validitaGiorni,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pacchettiKeys.list() })
    },
  })
}

/** Get servizi linked to a pacchetto */
export function usePacchettoServizi(pacchettoId: string | undefined) {
  return useQuery({
    queryKey: [...pacchettiKeys.all, 'servizi', pacchettoId] as const,
    queryFn: () =>
      invoke<PacchettoServizio[]>('get_pacchetto_servizi', {
        pacchettoId: pacchettoId!,
      }),
    enabled: !!pacchettoId,
    staleTime: 30 * 1000,
  })
}

/** Add a servizio to a pacchetto */
export function useAddServizioToPacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      pacchettoId,
      servizioId,
      quantita,
    }: {
      pacchettoId: string
      servizioId: string
      quantita?: number
    }) =>
      invoke<PacchettoServizio>('add_servizio_to_pacchetto', {
        pacchettoId,
        servizioId,
        quantita: quantita ?? null,
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: [...pacchettiKeys.all, 'servizi', data.pacchetto_id],
      })
      queryClient.invalidateQueries({ queryKey: pacchettiKeys.list() })
    },
  })
}

/** Remove a servizio from a pacchetto */
export function useRemoveServizioFromPacchetto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      pacchettoId,
      servizioId,
    }: {
      pacchettoId: string
      servizioId: string
    }) =>
      invoke<boolean>('remove_servizio_from_pacchetto', {
        pacchettoId,
        servizioId,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: [...pacchettiKeys.all, 'servizi', variables.pacchettoId],
      })
      queryClient.invalidateQueries({ queryKey: pacchettiKeys.list() })
    },
  })
}
