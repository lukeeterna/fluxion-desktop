// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fatturazione Elettronica Types (Fase 6)
// TypeScript types + Zod schemas per FatturaPA
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod'

// ───────────────────────────────────────────────────────────────────
// Impostazioni Fatturazione
// ───────────────────────────────────────────────────────────────────

export const ImpostazioniFatturazioneSchema = z.object({
  id: z.string(),
  denominazione: z.string(),
  partita_iva: z.string(),
  codice_fiscale: z.string().nullable(),
  regime_fiscale: z.string(),
  indirizzo: z.string(),
  cap: z.string(),
  comune: z.string(),
  provincia: z.string(),
  nazione: z.string(),
  telefono: z.string().nullable(),
  email: z.string().nullable(),
  pec: z.string().nullable(),
  prefisso_numerazione: z.string().nullable(),
  ultimo_numero: z.number(),
  anno_corrente: z.number(),
  aliquota_iva_default: z.number(),
  natura_iva_default: z.string().nullable(),
  iban: z.string().nullable(),
  bic: z.string().nullable(),
  nome_banca: z.string().nullable(),
})

export type ImpostazioniFatturazione = z.infer<typeof ImpostazioniFatturazioneSchema>

// ───────────────────────────────────────────────────────────────────
// Fattura
// ───────────────────────────────────────────────────────────────────

export const StatoFatturaSchema = z.enum([
  'bozza',
  'emessa',
  'inviata_sdi',
  'accettata',
  'rifiutata',
  'scartata',
  'pagata',
  'annullata',
])

export type StatoFattura = z.infer<typeof StatoFatturaSchema>

export const TipoDocumentoSchema = z.enum([
  'TD01', // Fattura
  'TD04', // Nota di credito
  'TD05', // Nota di debito
  'TD06', // Parcella
  'TD24', // Fattura differita
  'TD25', // Fattura accompagnatoria
])

export type TipoDocumento = z.infer<typeof TipoDocumentoSchema>

export const FatturaSchema = z.object({
  id: z.string(),
  numero: z.number(),
  anno: z.number(),
  numero_completo: z.string(),
  tipo_documento: z.string(),
  data_emissione: z.string(),
  data_scadenza: z.string().nullable(),
  cliente_id: z.string(),
  cliente_denominazione: z.string(),
  cliente_partita_iva: z.string().nullable(),
  cliente_codice_fiscale: z.string().nullable(),
  cliente_indirizzo: z.string().nullable(),
  cliente_cap: z.string().nullable(),
  cliente_comune: z.string().nullable(),
  cliente_provincia: z.string().nullable(),
  cliente_nazione: z.string(),
  cliente_codice_sdi: z.string(),
  cliente_pec: z.string().nullable(),
  imponibile_totale: z.number(),
  iva_totale: z.number(),
  totale_documento: z.number(),
  ritenuta_tipo: z.string().nullable(),
  ritenuta_percentuale: z.number().nullable(),
  ritenuta_importo: z.number().nullable(),
  ritenuta_causale: z.string().nullable(),
  bollo_virtuale: z.number(),
  bollo_importo: z.number(),
  modalita_pagamento: z.string(),
  condizioni_pagamento: z.string(),
  stato: StatoFatturaSchema,
  sdi_id_trasmissione: z.string().nullable(),
  sdi_data_invio: z.string().nullable(),
  sdi_data_risposta: z.string().nullable(),
  sdi_esito: z.string().nullable(),
  sdi_errori: z.string().nullable(),
  xml_filename: z.string().nullable(),
  xml_content: z.string().nullable(),
  appuntamento_id: z.string().nullable(),
  ordine_id: z.string().nullable(),
  fattura_origine_id: z.string().nullable(),
  causale: z.string().nullable(),
  note_interne: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  deleted_at: z.string().nullable(),
})

export type Fattura = z.infer<typeof FatturaSchema>

// ───────────────────────────────────────────────────────────────────
// Riga Fattura
// ───────────────────────────────────────────────────────────────────

export const FatturaRigaSchema = z.object({
  id: z.string(),
  fattura_id: z.string(),
  numero_linea: z.number(),
  descrizione: z.string(),
  codice_articolo: z.string().nullable(),
  quantita: z.number(),
  unita_misura: z.string(),
  prezzo_unitario: z.number(),
  sconto_percentuale: z.number(),
  sconto_importo: z.number(),
  prezzo_totale: z.number(),
  aliquota_iva: z.number(),
  natura: z.string().nullable(),
  servizio_id: z.string().nullable(),
  appuntamento_id: z.string().nullable(),
})

export type FatturaRiga = z.infer<typeof FatturaRigaSchema>

// ───────────────────────────────────────────────────────────────────
// Pagamento
// ───────────────────────────────────────────────────────────────────

export const FatturaPagamentoSchema = z.object({
  id: z.string(),
  fattura_id: z.string(),
  data_pagamento: z.string(),
  importo: z.number(),
  metodo: z.string(),
  iban: z.string().nullable(),
  riferimento: z.string().nullable(),
  note: z.string().nullable(),
})

export type FatturaPagamento = z.infer<typeof FatturaPagamentoSchema>

// ───────────────────────────────────────────────────────────────────
// Fattura Completa (con righe e pagamenti)
// ───────────────────────────────────────────────────────────────────

export const FatturaCompletaSchema = z.object({
  fattura: FatturaSchema,
  righe: z.array(FatturaRigaSchema),
  pagamenti: z.array(FatturaPagamentoSchema),
})

export type FatturaCompleta = z.infer<typeof FatturaCompletaSchema>

// ───────────────────────────────────────────────────────────────────
// Codici Lookup
// ───────────────────────────────────────────────────────────────────

export const CodicePagamentoSchema = z.object({
  codice: z.string(),
  descrizione: z.string(),
})

export type CodicePagamento = z.infer<typeof CodicePagamentoSchema>

export const CodiceNaturaIvaSchema = z.object({
  codice: z.string(),
  descrizione: z.string(),
  riferimento_normativo: z.string().nullable(),
})

export type CodiceNaturaIva = z.infer<typeof CodiceNaturaIvaSchema>

// ───────────────────────────────────────────────────────────────────
// Input Types
// ───────────────────────────────────────────────────────────────────

export const CreateFatturaSchema = z.object({
  cliente_id: z.string().min(1, 'Cliente obbligatorio'),
  tipo_documento: TipoDocumentoSchema.optional(),
  data_emissione: z.string().min(1, 'Data obbligatoria'),
  data_scadenza: z.string().optional(),
  modalita_pagamento: z.string().optional(),
  condizioni_pagamento: z.string().optional(),
  causale: z.string().optional(),
  note_interne: z.string().optional(),
  appuntamento_id: z.string().optional(),
  fattura_origine_id: z.string().optional(),
})

export type CreateFattura = z.infer<typeof CreateFatturaSchema>

export const CreateFatturaRigaSchema = z.object({
  descrizione: z.string().min(1, 'Descrizione obbligatoria'),
  codice_articolo: z.string().optional(),
  quantita: z.number().positive('Quantità deve essere positiva'),
  unita_misura: z.string().optional(),
  prezzo_unitario: z.number().min(0, 'Prezzo non può essere negativo'),
  sconto_percentuale: z.number().min(0).max(100).optional(),
  aliquota_iva: z.number().min(0),
  natura: z.string().optional(),
  servizio_id: z.string().optional(),
  appuntamento_id: z.string().optional(),
})

export type CreateFatturaRiga = z.infer<typeof CreateFatturaRigaSchema>

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

export function getStatoFatturaBadge(stato: StatoFattura): {
  label: string
  variant: 'default' | 'secondary' | 'destructive' | 'outline'
  color: string
} {
  switch (stato) {
    case 'bozza':
      return { label: 'Bozza', variant: 'outline', color: 'gray' }
    case 'emessa':
      return { label: 'Emessa', variant: 'default', color: 'blue' }
    case 'inviata_sdi':
      return { label: 'Inviata SDI', variant: 'secondary', color: 'yellow' }
    case 'accettata':
      return { label: 'Accettata', variant: 'default', color: 'green' }
    case 'rifiutata':
      return { label: 'Rifiutata', variant: 'destructive', color: 'red' }
    case 'scartata':
      return { label: 'Scartata', variant: 'destructive', color: 'red' }
    case 'pagata':
      return { label: 'Pagata', variant: 'default', color: 'emerald' }
    case 'annullata':
      return { label: 'Annullata', variant: 'destructive', color: 'red' }
    default:
      return { label: stato, variant: 'outline', color: 'gray' }
  }
}

export function getTipoDocumentoLabel(tipo: string): string {
  switch (tipo) {
    case 'TD01':
      return 'Fattura'
    case 'TD04':
      return 'Nota di Credito'
    case 'TD05':
      return 'Nota di Debito'
    case 'TD06':
      return 'Parcella'
    case 'TD24':
      return 'Fattura Differita'
    case 'TD25':
      return 'Fattura Accompagnatoria'
    default:
      return tipo
  }
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount)
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

// Validazione Partita IVA italiana
export function validaPartitaIva(piva: string): boolean {
  if (!piva || piva.length !== 11) return false
  if (!/^\d{11}$/.test(piva)) return false

  // Algoritmo Luhn modificato
  let sum = 0
  for (let i = 0; i < 11; i++) {
    const digit = parseInt(piva[i], 10)
    if (i % 2 === 0) {
      sum += digit
    } else {
      const doubled = digit * 2
      sum += doubled > 9 ? doubled - 9 : doubled
    }
  }
  return sum % 10 === 0
}

// Validazione Codice Fiscale italiano
export function validaCodiceFiscale(cf: string): boolean {
  if (!cf || cf.length !== 16) return false
  const pattern = /^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$/i
  return pattern.test(cf)
}
