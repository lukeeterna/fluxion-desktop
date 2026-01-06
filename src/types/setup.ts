// ═══════════════════════════════════════════════════════════════════
// FLUXION - Setup Wizard Types
// TypeScript types per configurazione iniziale
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ─────────────────────────────────────────────────────────────────────
// ZOD SCHEMAS
// ─────────────────────────────────────────────────────────────────────

export const SetupConfigSchema = z.object({
  // Dati Azienda (obbligatorio solo nome_attivita)
  nome_attivita: z.string().min(2, 'Nome attività richiesto (min 2 caratteri)'),
  partita_iva: z.string().length(11, 'P.IVA deve essere 11 cifre').optional().or(z.literal('')),
  codice_fiscale: z.string().optional().or(z.literal('')),
  indirizzo: z.string().optional().or(z.literal('')),
  cap: z.string().length(5, 'CAP deve essere 5 cifre').optional().or(z.literal('')),
  citta: z.string().optional().or(z.literal('')),
  provincia: z.string().length(2, 'Provincia deve essere 2 lettere').optional().or(z.literal('')),
  telefono: z.string().optional().or(z.literal('')),
  email: z.string().email('Email non valida').optional().or(z.literal('')),
  pec: z.string().email('PEC non valida').optional().or(z.literal('')),

  // Regime Fiscale
  regime_fiscale: z.enum(['RF01', 'RF19']).optional(),

  // FLUXION IA - Chiave API per assistente intelligente (opzionale)
  fluxion_ia_key: z.string().optional().or(z.literal('')),

  // Categoria attività (per FAQ RAG)
  categoria_attivita: z.enum(['salone', 'auto', 'wellness', 'medical', 'altro']).optional(),
});

export const SetupStatusSchema = z.object({
  is_completed: z.boolean(),
  nome_attivita: z.string().nullable().optional(),
  missing_fields: z.array(z.string()),
});

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

export type SetupConfig = z.infer<typeof SetupConfigSchema>;
export type SetupStatus = z.infer<typeof SetupStatusSchema>;

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

export const REGIMI_FISCALI = [
  { value: 'RF01', label: 'Regime Ordinario', description: 'IVA al 22%' },
  { value: 'RF19', label: 'Regime Forfettario', description: 'Nessuna IVA, imposta sostitutiva' },
] as const;

export const CATEGORIE_ATTIVITA = [
  { value: 'salone', label: 'Salone / Parrucchiere', icon: '💇' },
  { value: 'auto', label: 'Officina / Carrozzeria', icon: '🚗' },
  { value: 'wellness', label: 'Centro Benessere / Palestra', icon: '🧘' },
  { value: 'medical', label: 'Studio Medico / Dentista', icon: '🏥' },
  { value: 'altro', label: 'Altro', icon: '🏢' },
] as const;

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

export const defaultSetupConfig: SetupConfig = {
  nome_attivita: '',
  partita_iva: '',
  codice_fiscale: '',
  indirizzo: '',
  cap: '',
  citta: '',
  provincia: '',
  telefono: '',
  email: '',
  pec: '',
  regime_fiscale: 'RF19',
  fluxion_ia_key: '',
  categoria_attivita: 'salone',
};

/**
 * Valida solo P.IVA italiana (11 cifre numeriche)
 */
export function validaPartitaIva(piva: string): boolean {
  if (!piva || piva.length !== 11) return false;
  return /^\d{11}$/.test(piva);
}

/**
 * Calcola se il setup è sufficientemente completato per procedere
 */
export function isSetupMinimallyComplete(config: Partial<SetupConfig>): boolean {
  return !!(config.nome_attivita && config.nome_attivita.length >= 2);
}
