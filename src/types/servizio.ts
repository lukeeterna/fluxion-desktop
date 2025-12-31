// ═══════════════════════════════════════════════════════════════════
// FLUXION - Servizio Types
// TypeScript types for servizi (services)
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// Servizio Entity
// ───────────────────────────────────────────────────────────────────

export interface Servizio {
  id: string;
  nome: string;
  descrizione: string | null;
  categoria: string | null;
  prezzo: number;
  iva_percentuale: number;
  durata_minuti: number;
  buffer_minuti: number;
  colore: string;
  icona: string | null;
  attivo: number;
  ordine: number;
  created_at: string;
  updated_at: string;
}

// ───────────────────────────────────────────────────────────────────
// Zod Schemas for Validation
// ───────────────────────────────────────────────────────────────────

export const createServizioSchema = z.object({
  nome: z.string().min(2, 'Nome richiesto (min 2 caratteri)'),
  descrizione: z.string().optional(),
  categoria: z.string().optional(),
  prezzo: z.number().min(0, 'Prezzo deve essere >= 0'),
  iva_percentuale: z.number().min(0).max(100).optional(),
  durata_minuti: z.number().min(5, 'Durata minima 5 minuti'),
  buffer_minuti: z.number().min(0).optional(),
  colore: z.string().regex(/^#[0-9A-F]{6}$/i, 'Colore invalido (formato #RRGGBB)').optional(),
  icona: z.string().optional(),
  attivo: z.number().min(0).max(1).optional(),
  ordine: z.number().optional(),
});

export const updateServizioSchema = z.object({
  nome: z.string().min(2, 'Nome richiesto (min 2 caratteri)').optional(),
  descrizione: z.string().optional(),
  categoria: z.string().optional(),
  prezzo: z.number().min(0, 'Prezzo deve essere >= 0').optional(),
  iva_percentuale: z.number().min(0).max(100).optional(),
  durata_minuti: z.number().min(5, 'Durata minima 5 minuti').optional(),
  buffer_minuti: z.number().min(0).optional(),
  colore: z.string().regex(/^#[0-9A-F]{6}$/i, 'Colore invalido (formato #RRGGBB)').optional(),
  icona: z.string().optional(),
  attivo: z.number().min(0).max(1).optional(),
  ordine: z.number().optional(),
});

// ───────────────────────────────────────────────────────────────────
// Input Types
// ───────────────────────────────────────────────────────────────────

export type CreateServizioInput = z.infer<typeof createServizioSchema>;
export type UpdateServizioInput = z.infer<typeof updateServizioSchema>;
