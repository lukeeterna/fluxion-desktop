// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamento DDD Types
// TypeScript types for DDD-layer appuntamenti workflow
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// Zod Schemas (Runtime Validation)
// ───────────────────────────────────────────────────────────────────

export const AppuntamentoStatoSchema = z.enum([
  'Bozza',
  'Proposta',
  'InAttesaOperatore',
  'Confermato',
  'ConfermatoConOverride',
  'Rifiutato',
  'Completato',
  'Cancellato',
]);

export const OverrideInfoDtoSchema = z.object({
  timestamp: z.string(),
  operatore_id: z.string(),
  motivazione: z.string().optional(),
  warnings_ignorati: z.array(z.string()),
});

export const AppuntamentoDtoSchema = z.object({
  id: z.string().uuid(),
  cliente_id: z.string(),
  operatore_id: z.string(),
  servizio_id: z.string(),
  data_ora: z.string(), // ISO 8601
  durata_minuti: z.number().int().positive(),
  stato: AppuntamentoStatoSchema,
  note: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
  override_info: OverrideInfoDtoSchema.optional(),
});

export const WarningDtoSchema = z.object({
  tipo: z.string(),
  messaggio: z.string(),
});

export const SuggestionDtoSchema = z.object({
  tipo: z.string(),
  messaggio: z.string(),
});

export const ValidationResultDtoSchema = z.object({
  is_blocked: z.boolean(),
  has_warnings: z.boolean(),
  has_suggestions: z.boolean(),
  hard_blocks: z.array(z.string()),
  warnings: z.array(WarningDtoSchema),
  suggestions: z.array(SuggestionDtoSchema),
});

export const ProponiAppuntamentoResponseSchema = z.object({
  appuntamento: AppuntamentoDtoSchema,
  validation: ValidationResultDtoSchema,
});

// ───────────────────────────────────────────────────────────────────
// TypeScript Types (Inferred from Zod)
// ───────────────────────────────────────────────────────────────────

export type AppuntamentoStato = z.infer<typeof AppuntamentoStatoSchema>;
export type OverrideInfoDto = z.infer<typeof OverrideInfoDtoSchema>;
export type AppuntamentoDto = z.infer<typeof AppuntamentoDtoSchema>;
export type WarningDto = z.infer<typeof WarningDtoSchema>;
export type SuggestionDto = z.infer<typeof SuggestionDtoSchema>;
export type ValidationResultDto = z.infer<typeof ValidationResultDtoSchema>;
export type ProponiAppuntamentoResponse = z.infer<typeof ProponiAppuntamentoResponseSchema>;

// ───────────────────────────────────────────────────────────────────
// Request DTOs
// ───────────────────────────────────────────────────────────────────

export interface CreaAppuntamentoBozzaDto {
  cliente_id: string;
  operatore_id: string;
  servizio_id: string;
  /** Format: "YYYY-MM-DDTHH:MM:SS" (naive) */
  data_ora: string;
  durata_minuti: number;
}

export interface ProponiAppuntamentoDto {
  appuntamento_id: string;
}

export interface ConfermaConOverrideDto {
  appuntamento_id: string;
  operatore_id: string;
  motivazione?: string;
  warnings_ignorati: string[];
}

export interface RifiutaAppuntamentoDto {
  appuntamento_id: string;
  motivazione?: string;
}

// ───────────────────────────────────────────────────────────────────
// Utility Types
// ───────────────────────────────────────────────────────────────────

export type AppuntamentoWorkflowStep =
  | 'bozza' // Creazione iniziale
  | 'proposta' // Validazione in corso
  | 'attesa-operatore' // In attesa conferma operatore
  | 'confermato' // Confermato
  | 'override' // Confermato con override
  | 'rifiutato' // Rifiutato da operatore
  | 'completato' // Servizio completato
  | 'cancellato'; // Cancellato

/** Helper per mapping stato → workflow step */
export function statoToWorkflowStep(stato: AppuntamentoStato): AppuntamentoWorkflowStep {
  switch (stato) {
    case 'Bozza':
      return 'bozza';
    case 'Proposta':
      return 'proposta';
    case 'InAttesaOperatore':
      return 'attesa-operatore';
    case 'Confermato':
      return 'confermato';
    case 'ConfermatoConOverride':
      return 'override';
    case 'Rifiutato':
      return 'rifiutato';
    case 'Completato':
      return 'completato';
    case 'Cancellato':
      return 'cancellato';
  }
}

/** Helper per check se stato è finale (non modificabile) */
export function isStatoFinale(stato: AppuntamentoStato): boolean {
  return ['Rifiutato', 'Completato', 'Cancellato'].includes(stato);
}

/** Helper per check se stato richiede azione operatore */
export function richiedeAzioneOperatore(stato: AppuntamentoStato): boolean {
  return stato === 'InAttesaOperatore';
}
