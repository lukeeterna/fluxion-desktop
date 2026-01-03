// ═══════════════════════════════════════════════════════════════════
// FLUXION - Orari & Festività Types
// TypeScript types for working hours and Italian holidays
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// Database Types (from Rust)
// ───────────────────────────────────────────────────────────────────

export interface OrarioLavoro {
  id: string;
  giorno_settimana: number; // 0=domenica, 1=lunedì, ..., 6=sabato
  ora_inizio: string;        // "HH:MM"
  ora_fine: string;          // "HH:MM"
  tipo: 'lavoro' | 'pausa';
  operatore_id: string | null;
}

export interface GiornoFestivo {
  id: string;
  data: string;        // "YYYY-MM-DD"
  descrizione: string;
  ricorrente: number;  // 0 | 1
}

export interface ValidazioneOrarioResult {
  disponibile: boolean;
  motivo?: string;
}

// ───────────────────────────────────────────────────────────────────
// Input Types (create/update)
// ───────────────────────────────────────────────────────────────────

export interface CreateOrarioLavoroInput {
  giorno_settimana: number;
  ora_inizio: string;
  ora_fine: string;
  tipo: 'lavoro' | 'pausa';
  operatore_id?: string | null;
}

export interface CreateGiornoFestivoInput {
  data: string;
  descrizione: string;
  ricorrente: number;
}

// ───────────────────────────────────────────────────────────────────
// Zod Schemas
// ───────────────────────────────────────────────────────────────────

export const createOrarioLavoroSchema = z.object({
  giorno_settimana: z.number().int().min(0).max(6),
  ora_inizio: z.string().regex(/^\d{2}:\d{2}$/, 'Formato HH:MM richiesto'),
  ora_fine: z.string().regex(/^\d{2}:\d{2}$/, 'Formato HH:MM richiesto'),
  tipo: z.enum(['lavoro', 'pausa']),
  operatore_id: z.string().optional().nullable(),
});

export const createGiornoFestivoSchema = z.object({
  data: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato YYYY-MM-DD richiesto'),
  descrizione: z.string().min(1, 'Descrizione obbligatoria'),
  ricorrente: z.number().int().min(0).max(1),
});

// ───────────────────────────────────────────────────────────────────
// UI Helper Types
// ───────────────────────────────────────────────────────────────────

export const GIORNI_SETTIMANA = [
  { value: 1, label: 'Lunedì' },
  { value: 2, label: 'Martedì' },
  { value: 3, label: 'Mercoledì' },
  { value: 4, label: 'Giovedì' },
  { value: 5, label: 'Venerdì' },
  { value: 6, label: 'Sabato' },
  { value: 0, label: 'Domenica' },
] as const;

export function getGiornoLabel(giorno: number): string {
  const found = GIORNI_SETTIMANA.find(g => g.value === giorno);
  return found?.label || 'Sconosciuto';
}
