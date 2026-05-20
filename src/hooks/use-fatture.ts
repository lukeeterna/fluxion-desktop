// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fatturazione Elettronica Hooks (Fase 6)
// TanStack Query hooks per fatture, righe, pagamenti
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { invoke } from '@tauri-apps/api/core'
import type {
  ImpostazioniFatturazione,
  Fattura,
  FatturaCompleta,
  FatturaRiga,
  FatturaPagamento,
  CodicePagamento,
  CodiceNaturaIva,
} from '@/types/fatture'

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const fattureKeys = {
  all: ['fatture'] as const,
  list: (filters?: { anno?: number; stato?: string; cliente_id?: string }) =>
    [...fattureKeys.all, 'list', filters] as const,
  detail: (id: string) => [...fattureKeys.all, 'detail', id] as const,
  impostazioni: () => [...fattureKeys.all, 'impostazioni'] as const,
  codiciPagamento: () => [...fattureKeys.all, 'codici-pagamento'] as const,
  codiciNaturaIva: () => [...fattureKeys.all, 'codici-natura-iva'] as const,
}

// ───────────────────────────────────────────────────────────────────
// Impostazioni Queries
// ───────────────────────────────────────────────────────────────────

export function useImpostazioniFatturazione() {
  return useQuery({
    queryKey: fattureKeys.impostazioni(),
    queryFn: () => invoke<ImpostazioniFatturazione>('get_impostazioni_fatturazione'),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useUpdateImpostazioniFatturazione() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<ImpostazioniFatturazione>) =>
      // S268 BUG-FATT-4: Tauri 2.x default convention args Rust snake_case → JS
      // camelCase auto-mapping. snake_case lato JS è ignorato → Rust `denominazione: String`
      // (required) throws "missing required key". Allineato a pattern useCreateFattura/useAddRigaFattura.
      // Required String fields (denominazione/partita_iva/regime_fiscale/indirizzo/cap/comune/provincia)
      // passano stringa vuota se data missing (Rust accetta "" via encrypt_required pass-through).
      // `nazione` rimosso: non presente nella signature Rust update_impostazioni_fatturazione.
      invoke<ImpostazioniFatturazione>('update_impostazioni_fatturazione', {
        denominazione: data.denominazione ?? '',
        partitaIva: data.partita_iva ?? '',
        codiceFiscale: data.codice_fiscale ?? null,
        regimeFiscale: data.regime_fiscale ?? 'RF19',
        indirizzo: data.indirizzo ?? '',
        cap: data.cap ?? '',
        comune: data.comune ?? '',
        provincia: data.provincia ?? '',
        telefono: data.telefono ?? null,
        email: data.email ?? null,
        pec: data.pec ?? null,
        prefissoNumerazione: data.prefisso_numerazione ?? null,
        aliquotaIvaDefault: data.aliquota_iva_default ?? 0,
        naturaIvaDefault: data.natura_iva_default ?? null,
        iban: data.iban ?? null,
        bic: data.bic ?? null,
        nomeBanca: data.nome_banca ?? null,
        fattura24ApiKey: data.fattura24_api_key ?? null,
        sdiProvider: data.sdi_provider ?? null,
        arubaApiKey: data.aruba_api_key ?? null,
        openapiApiKey: data.openapi_api_key ?? null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.impostazioni() })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Fatture Queries
// ───────────────────────────────────────────────────────────────────

export function useFatture(filters?: {
  anno?: number
  stato?: string
  cliente_id?: string
}) {
  return useQuery({
    queryKey: fattureKeys.list(filters),
    queryFn: () =>
      invoke<Fattura[]>('get_fatture', {
        anno: filters?.anno ?? null,
        stato: filters?.stato ?? null,
        cliente_id: filters?.cliente_id ?? null,
      }),
    staleTime: 30 * 1000,
  })
}

export function useFattura(fatturaId: string | undefined) {
  return useQuery({
    queryKey: fattureKeys.detail(fatturaId ?? ''),
    queryFn: () =>
      invoke<FatturaCompleta>('get_fattura', { fatturaId: fatturaId! }),
    enabled: !!fatturaId,
  })
}

// ───────────────────────────────────────────────────────────────────
// Fatture Mutations
// ───────────────────────────────────────────────────────────────────

export function useCreateFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      cliente_id: string
      tipo_documento?: string
      data_emissione: string
      data_scadenza?: string
      modalita_pagamento?: string
      condizioni_pagamento?: string
      causale?: string
      note_interne?: string
      appuntamento_id?: string
      fattura_origine_id?: string
    }) =>
      invoke<Fattura>('create_fattura', {
        clienteId: data.cliente_id,
        tipoDocumento: data.tipo_documento ?? null,
        dataEmissione: data.data_emissione,
        dataScadenza: data.data_scadenza ?? null,
        modalitaPagamento: data.modalita_pagamento ?? null,
        condizioniPagamento: data.condizioni_pagamento ?? null,
        causale: data.causale ?? null,
        noteInterne: data.note_interne ?? null,
        appuntamentoId: data.appuntamento_id ?? null,
        fatturaOrigineId: data.fattura_origine_id ?? null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

export function useEmettiFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fatturaId: string) =>
      invoke<Fattura>('emetti_fattura', { fatturaId }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
      queryClient.setQueryData(fattureKeys.detail(data.id), (old: FatturaCompleta | undefined) =>
        old ? { ...old, fattura: data } : undefined
      )
    },
  })
}

export function useAnnullaFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ fatturaId, motivo }: { fatturaId: string; motivo?: string }) =>
      invoke<Fattura>('annulla_fattura', { fatturaId, motivo: motivo ?? null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

export function useDeleteFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fatturaId: string) =>
      invoke<boolean>('delete_fattura', { fatturaId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Righe Fattura Mutations
// ───────────────────────────────────────────────────────────────────

export function useAddRigaFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      fattura_id: string
      descrizione: string
      codice_articolo?: string
      quantita: number
      unita_misura?: string
      prezzo_unitario: number
      sconto_percentuale?: number
      aliquota_iva: number
      natura?: string
      servizio_id?: string
      appuntamento_id?: string
    }) =>
      invoke<FatturaRiga>('add_riga_fattura', {
        fatturaId: data.fattura_id,
        descrizione: data.descrizione,
        codiceArticolo: data.codice_articolo ?? null,
        quantita: data.quantita,
        unitaMisura: data.unita_misura ?? null,
        prezzoUnitario: data.prezzo_unitario,
        scontoPercentuale: data.sconto_percentuale ?? null,
        aliquotaIva: data.aliquota_iva,
        natura: data.natura ?? null,
        servizioId: data.servizio_id ?? null,
        appuntamentoId: data.appuntamento_id ?? null,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: fattureKeys.detail(variables.fattura_id),
      })
      // S268 BUG-FATT-3: usare fattureKeys.all per matchare list queries con
      // qualsiasi filters (es. {anno: 2026}). fattureKeys.list() = ['fatture', 'list', undefined]
      // NON matcha ['fatture', 'list', {anno: 2026}] in TanStack Query v5 prefix match.
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

export function useDeleteRigaFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (rigaId: string) =>
      invoke<boolean>('delete_riga_fattura', { rigaId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Pagamenti Mutations
// ───────────────────────────────────────────────────────────────────

export function useRegistraPagamento() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      fattura_id: string
      data_pagamento: string
      importo: number
      metodo: string
      iban?: string
      riferimento?: string
      note?: string
    }) =>
      invoke<FatturaPagamento>('registra_pagamento', {
        fatturaId: data.fattura_id,
        dataPagamento: data.data_pagamento,
        importo: data.importo,
        metodo: data.metodo,
        iban: data.iban ?? null,
        riferimento: data.riferimento ?? null,
        note: data.note ?? null,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: fattureKeys.detail(variables.fattura_id),
      })
      // S268 BUG-FATT-3: vedi commento in useAddRigaFattura.
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Codici Lookup Queries
// ───────────────────────────────────────────────────────────────────

export function useCodiciPagamento() {
  return useQuery({
    queryKey: fattureKeys.codiciPagamento(),
    queryFn: () => invoke<CodicePagamento[]>('get_codici_pagamento'),
    staleTime: Infinity, // Never stale - static data
  })
}

export function useCodiciNaturaIva() {
  return useQuery({
    queryKey: fattureKeys.codiciNaturaIva(),
    queryFn: () => invoke<CodiceNaturaIva[]>('get_codici_natura_iva'),
    staleTime: Infinity, // Never stale - static data
  })
}

// ───────────────────────────────────────────────────────────────────
// XML Download
// ───────────────────────────────────────────────────────────────────

export function useGetFatturaXml() {
  return useMutation({
    mutationFn: (fatturaId: string) =>
      invoke<string>('get_fattura_xml', { fatturaId }),
  })
}

// ───────────────────────────────────────────────────────────────────
// SDI Integration — Invio via intermediario Fattura24
// ───────────────────────────────────────────────────────────────────

export function useInviaSdiFattura() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fatturaId: string) =>
      invoke<Fattura>('invia_sdi_fattura', { fatturaId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}

export function useAggiornaEsitoSdi() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      fatturaId,
      esito,
      errori,
    }: {
      fatturaId: string
      esito: string
      errori?: string
    }) =>
      invoke<Fattura>('aggiorna_sdi_esito', {
        fatturaId,
        esito,
        errori: errori ?? null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.all })
    },
  })
}
