// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamento Types
// TypeScript types for appuntamenti (appointments)
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// Appuntamento Entity
// ───────────────────────────────────────────────────────────────────

export interface Appuntamento {
  id: string;
  cliente_id: string;
  servizio_id: string;
  operatore_id: string | null;
  data_ora_inizio: string; // ISO 8601
  data_ora_fine: string;   // ISO 8601
  durata_minuti: number;
  stato: StatoAppuntamento;
  prezzo: number;
  sconto_percentuale: number;
  prezzo_finale: number;
  note: string | null;
  note_interne: string | null;
  fonte_prenotazione: FontePrenotazione;
  reminder_inviato: number;
  created_at: string;
  updated_at: string;
}

/// Extended appointment with related entities (for calendar display)
/// Note: fields are flattened (not nested) due to Rust serde(flatten)
export interface AppuntamentoDettagliato {
  // Appuntamento fields (flattened)
  id: string;
  cliente_id: string;
  servizio_id: string;
  operatore_id: string | null;
  data_ora_inizio: string; // ISO 8601
  data_ora_fine: string;   // ISO 8601
  durata_minuti: number;
  stato: StatoAppuntamento;
  prezzo: number;
  sconto_percentuale: number;
  prezzo_finale: number;
  note: string | null;
  note_interne: string | null;
  fonte_prenotazione: FontePrenotazione;
  reminder_inviato: number;
  created_at: string;
  updated_at: string;
  // Related entity fields
  cliente_nome: string;
  cliente_cognome: string;
  cliente_telefono: string;
  servizio_nome: string;
  servizio_colore: string;
  operatore_nome: string | null;
  operatore_cognome: string | null;
  operatore_colore: string | null;
}

// ───────────────────────────────────────────────────────────────────
// Enums
// ───────────────────────────────────────────────────────────────────

export type StatoAppuntamento = 'bozza' | 'confermato' | 'completato' | 'cancellato' | 'no_show';
export type FontePrenotazione = 'manuale' | 'whatsapp' | 'voice' | 'online';

// ───────────────────────────────────────────────────────────────────
// Zod Schemas for Validation
// ───────────────────────────────────────────────────────────────────

export const createAppuntamentoSchema = z.object({
  cliente_id: z.string().uuid('Cliente richiesto'),
  servizio_id: z.string().uuid('Servizio richiesto'),
  operatore_id: z.string().uuid().optional(),
  data_ora_inizio: z.string().refine((val) => {
    const date = new Date(val);
    return !isNaN(date.getTime());
  }, 'Data/ora inizio non valida'),
  durata_minuti: z.number().min(5, 'Durata minima 5 minuti'),
  stato: z.enum(['bozza', 'confermato', 'completato', 'cancellato', 'no_show']).optional(),
  prezzo: z.number().min(0, 'Prezzo deve essere >= 0'),
  sconto_percentuale: z.number().min(0).max(100).optional(),
  note: z.string().optional(),
  note_interne: z.string().optional(),
  fonte_prenotazione: z.enum(['manuale', 'whatsapp', 'voice', 'online']).optional(),
});

export const updateAppuntamentoSchema = z.object({
  cliente_id: z.string().uuid().optional(),
  servizio_id: z.string().uuid().optional(),
  operatore_id: z.string().uuid().optional(),
  data_ora_inizio: z.string().refine((val) => {
    const date = new Date(val);
    return !isNaN(date.getTime());
  }, 'Data/ora inizio non valida').optional(),
  durata_minuti: z.number().min(5, 'Durata minima 5 minuti').optional(),
  stato: z.enum(['bozza', 'confermato', 'completato', 'cancellato', 'no_show']).optional(),
  prezzo: z.number().min(0, 'Prezzo deve essere >= 0').optional(),
  sconto_percentuale: z.number().min(0).max(100).optional(),
  note: z.string().optional(),
  note_interne: z.string().optional(),
  reminder_inviato: z.number().min(0).max(1).optional(),
});

// ───────────────────────────────────────────────────────────────────
// Input Types
// ───────────────────────────────────────────────────────────────────

export type CreateAppuntamentoInput = z.infer<typeof createAppuntamentoSchema>;
export type UpdateAppuntamentoInput = z.infer<typeof updateAppuntamentoSchema>;

// Query params for fetching appointments
export interface GetAppuntamentiParams {
  start_date: string;   // YYYY-MM-DD
  end_date: string;     // YYYY-MM-DD
  operatore_id?: string;
  cliente_id?: string;
  stato?: StatoAppuntamento;
}
