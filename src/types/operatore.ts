// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Types
// TypeScript types for operatori (staff/operators)
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// Operatore Entity
// ───────────────────────────────────────────────────────────────────

export interface Operatore {
  id: string;
  nome: string;
  cognome: string;
  email: string | null;
  telefono: string | null;
  ruolo: string;
  colore: string;
  avatar_url: string | null;
  attivo: number;
  genere: string | null;
  voice_transfer_enabled: number;
  voice_transfer_reachable: number;
  voice_transfer_priority: number;
  created_at: string;
  updated_at: string;
}

// ───────────────────────────────────────────────────────────────────
// Zod Schemas for Validation
// ───────────────────────────────────────────────────────────────────

export const createOperatoreSchema = z.object({
  nome: z.string().min(2, 'Nome richiesto (min 2 caratteri)'),
  cognome: z.string().min(2, 'Cognome richiesto (min 2 caratteri)'),
  email: z.string().email('Email non valida').optional().or(z.literal('')),
  telefono: z.string().min(10, 'Telefono richiesto (min 10 cifre)').optional().or(z.literal('')),
  ruolo: z.enum(['admin', 'operatore', 'reception']).optional(),
  colore: z.string().regex(/^#[0-9A-F]{6}$/i, 'Colore invalido (formato #RRGGBB)').optional(),
  avatar_url: z.string().url('URL non valido').optional().or(z.literal('')),
  attivo: z.number().min(0).max(1).optional(),
  genere: z.enum(['M', 'F']).nullable().optional(),
  voice_transfer_enabled: z.number().int().min(0).max(1).optional(),
  voice_transfer_reachable: z.number().int().min(0).max(1).optional(),
  voice_transfer_priority: z.number().int().min(0).max(9999).optional(),
});

export const updateOperatoreSchema = z.object({
  nome: z.string().min(2, 'Nome richiesto (min 2 caratteri)').optional(),
  cognome: z.string().min(2, 'Cognome richiesto (min 2 caratteri)').optional(),
  email: z.string().email('Email non valida').optional().or(z.literal('')),
  telefono: z.string().min(10, 'Telefono richiesto (min 10 cifre)').optional().or(z.literal('')),
  ruolo: z.enum(['admin', 'operatore', 'reception']).optional(),
  colore: z.string().regex(/^#[0-9A-F]{6}$/i, 'Colore invalido (formato #RRGGBB)').optional(),
  avatar_url: z.string().url('URL non valido').optional().or(z.literal('')),
  attivo: z.number().min(0).max(1).optional(),
  genere: z.enum(['M', 'F']).nullable().optional(),
  voice_transfer_enabled: z.number().int().min(0).max(1).optional(),
  voice_transfer_reachable: z.number().int().min(0).max(1).optional(),
  voice_transfer_priority: z.number().int().min(0).max(9999).optional(),
});

// ───────────────────────────────────────────────────────────────────
// Input Types
// ───────────────────────────────────────────────────────────────────

export type CreateOperatoreInput = z.infer<typeof createOperatoreSchema>;
export type UpdateOperatoreInput = z.infer<typeof updateOperatoreSchema>;

// ───────────────────────────────────────────────────────────────────
// Utility Types
// ───────────────────────────────────────────────────────────────────

export type RuoloOperatore = 'admin' | 'operatore' | 'reception';
