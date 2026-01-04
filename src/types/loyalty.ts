// ═══════════════════════════════════════════════════════════════════
// FLUXION - Loyalty & Pacchetti Types (Fase 5)
// TypeScript types + Zod schemas per tessera timbri, VIP, referral, pacchetti
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod'

// ───────────────────────────────────────────────────────────────────
// Loyalty Info (Tessera Timbri)
// ───────────────────────────────────────────────────────────────────

export const LoyaltyInfoSchema = z.object({
  cliente_id: z.string(),
  nome: z.string(),
  cognome: z.string(),
  loyalty_visits: z.number(),
  loyalty_threshold: z.number(),
  is_vip: z.boolean(),
  referral_source: z.string().nullable(),
  progress_percent: z.number(),
  visits_remaining: z.number(),
})

export type LoyaltyInfo = z.infer<typeof LoyaltyInfoSchema>

// ───────────────────────────────────────────────────────────────────
// Pacchetto
// ───────────────────────────────────────────────────────────────────

export const PacchettoSchema = z.object({
  id: z.string(),
  nome: z.string(),
  descrizione: z.string().nullable(),
  prezzo: z.number(),
  prezzo_originale: z.number().nullable(),
  servizi_inclusi: z.number(),
  validita_giorni: z.number(),
  attivo: z.boolean(),
  risparmio: z.number().nullable(),
})

export type Pacchetto = z.infer<typeof PacchettoSchema>

export const CreatePacchettoSchema = z.object({
  nome: z.string().min(1, 'Nome obbligatorio'),
  descrizione: z.string().optional(),
  prezzo: z.number().positive('Prezzo deve essere positivo'),
  prezzo_originale: z.number().positive().optional(),
  servizi_inclusi: z.number().int().positive('Servizi deve essere almeno 1'),
  validita_giorni: z.number().int().positive().default(365),
})

export type CreatePacchetto = z.infer<typeof CreatePacchettoSchema>

// ───────────────────────────────────────────────────────────────────
// Cliente Pacchetto (acquisto)
// ───────────────────────────────────────────────────────────────────

export const ClientePacchettoStatoSchema = z.enum([
  'proposto',
  'venduto',
  'in_uso',
  'completato',
  'scaduto',
  'annullato',
])

export type ClientePacchettoStato = z.infer<typeof ClientePacchettoStatoSchema>

export const ClientePacchettoSchema = z.object({
  id: z.string(),
  cliente_id: z.string(),
  pacchetto_id: z.string(),
  pacchetto_nome: z.string(),
  stato: ClientePacchettoStatoSchema,
  servizi_usati: z.number(),
  servizi_totali: z.number(),
  data_acquisto: z.string().nullable(),
  data_scadenza: z.string().nullable(),
  progress_percent: z.number(),
})

export type ClientePacchetto = z.infer<typeof ClientePacchettoSchema>

// ───────────────────────────────────────────────────────────────────
// Referral
// ───────────────────────────────────────────────────────────────────

export const TopReferrerSchema = z.object({
  cliente_id: z.string(),
  nome: z.string(),
  cognome: z.string(),
  referral_count: z.number(),
})

export type TopReferrer = z.infer<typeof TopReferrerSchema>

// ───────────────────────────────────────────────────────────────────
// Pacchetto Servizi (composizione pacchetto)
// ───────────────────────────────────────────────────────────────────

export const PacchettoServizioSchema = z.object({
  id: z.string(),
  pacchetto_id: z.string(),
  servizio_id: z.string(),
  servizio_nome: z.string(),
  servizio_prezzo: z.number(),
  quantita: z.number(),
})

export type PacchettoServizio = z.infer<typeof PacchettoServizioSchema>

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

export function getLoyaltyBadge(info: LoyaltyInfo): {
  label: string
  color: string
  emoji: string
} {
  if (info.is_vip) {
    return { label: 'VIP', color: 'gold', emoji: '👑' }
  }

  const percent = info.progress_percent

  if (percent >= 100) {
    return { label: 'Premio!', color: 'green', emoji: '🎁' }
  } else if (percent >= 80) {
    return { label: 'Quasi!', color: 'cyan', emoji: '⭐' }
  } else if (percent >= 50) {
    return { label: 'A metà', color: 'blue', emoji: '💪' }
  } else if (percent > 0) {
    return { label: 'Iniziato', color: 'gray', emoji: '🚀' }
  } else {
    return { label: 'Nuovo', color: 'gray', emoji: '👋' }
  }
}

export function getPacchettoStatoBadge(stato: ClientePacchettoStato): {
  label: string
  variant: 'default' | 'secondary' | 'destructive' | 'outline'
} {
  switch (stato) {
    case 'proposto':
      return { label: 'Proposto', variant: 'outline' }
    case 'venduto':
      return { label: 'Acquistato', variant: 'default' }
    case 'in_uso':
      return { label: 'In Uso', variant: 'secondary' }
    case 'completato':
      return { label: 'Completato', variant: 'default' }
    case 'scaduto':
      return { label: 'Scaduto', variant: 'destructive' }
    case 'annullato':
      return { label: 'Annullato', variant: 'destructive' }
    default:
      return { label: stato, variant: 'outline' }
  }
}

export function formatRisparmio(pacchetto: Pacchetto): string | null {
  if (!pacchetto.risparmio || !pacchetto.prezzo_originale) return null

  const percentuale = (
    (pacchetto.risparmio / pacchetto.prezzo_originale) *
    100
  ).toFixed(0)

  return `-€${pacchetto.risparmio.toFixed(0)} (${percentuale}%)`
}
