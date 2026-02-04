// ═══════════════════════════════════════════════════════════════════
// FLUXION - Setup Verticali Types
// Macro e Micro categorie per settori specifici
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ─────────────────────────────────────────────────────────────────────
// MACRO CATEGORIE
// ─────────────────────────────────────────────────────────────────────

export const MACRO_CATEGORIE = [
  { 
    value: 'medico', 
    label: 'Sanitario / Medico',
    icon: '🏥',
    description: 'Studi medici, dentisti, fisioterapisti'
  },
  { 
    value: 'beauty', 
    label: 'Bellezza / Estetica',
    icon: '💅',
    description: 'Estetiste, centri benessere, nail art'
  },
  { 
    value: 'hair', 
    label: 'Parrucchiere / Barbiere',
    icon: '💇',
    description: 'Saloni, barbieri, hair stylist'
  },
  { 
    value: 'auto', 
    label: 'Automotive',
    icon: '🚗',
    description: 'Officine, carrozzerie, elettrauto'
  },
  { 
    value: 'wellness', 
    label: 'Wellness / Fitness',
    icon: '🧘',
    description: 'Palestre, yoga, centri benessere'
  },
  { 
    value: 'professionale', 
    label: 'Servizi Professionali',
    icon: '💼',
    description: 'Consulenti, commercialisti, avvocati'
  },
] as const;

// ─────────────────────────────────────────────────────────────────────
// MICRO CATEGORIE per Macro
// ─────────────────────────────────────────────────────────────────────

export const MICRO_CATEGORIE: Record<string, Array<{value: string, label: string, hasScheda: boolean}>> = {
  medico: [
    { value: 'odontoiatra', label: 'Odontoiatra / Dentista', hasScheda: true },
    { value: 'fisioterapia', label: 'Fisioterapia / Riabilitazione', hasScheda: true },
    { value: 'medico_generico', label: 'Medico Generico', hasScheda: true },
    { value: 'specialista', label: 'Specialista (cardiologo, etc.)', hasScheda: true },
    { value: 'osteopata', label: 'Osteopata', hasScheda: true },
    { value: 'podologo', label: 'Podologo', hasScheda: true },
    { value: 'psicologo', label: 'Psicologo / Psicoterapeuta', hasScheda: true },
    { value: 'nutrizionista', label: 'Nutrizionista', hasScheda: true },
  ],
  beauty: [
    { value: 'estetista_viso', label: 'Estetista - Trattamenti Viso', hasScheda: true },
    { value: 'estetista_corpo', label: 'Estetista - Trattamenti Corpo', hasScheda: true },
    { value: 'nail_specialist', label: 'Nail Specialist', hasScheda: true },
    { value: 'epilazione_laser', label: 'Centro Epilazione Laser', hasScheda: true },
    { value: 'centro_abbronzatura', label: 'Centro Abbronzatura', hasScheda: true },
    { value: 'spa', label: 'SPA / Centri Benessere', hasScheda: true },
  ],
  hair: [
    { value: 'salone_donna', label: 'Salone Donna', hasScheda: true },
    { value: 'barbiere', label: 'Barbiere Tradizionale', hasScheda: true },
    { value: 'salone_unisex', label: 'Salone Unisex', hasScheda: true },
    { value: 'extension_specialist', label: 'Extension Specialist', hasScheda: true },
    { value: 'color_specialist', label: 'Color Specialist', hasScheda: true },
    { value: 'tricologo', label: 'Tricologo / Caduta Capelli', hasScheda: true },
  ],
  auto: [
    { value: 'officina_meccanica', label: 'Officina Meccanica', hasScheda: true },
    { value: 'carrozzeria', label: 'Carrozzeria', hasScheda: true },
    { value: 'elettrauto', label: 'Elettrauto', hasScheda: true },
    { value: 'gommista', label: 'Gommista / Pneumatici', hasScheda: true },
    { value: 'revisioni', label: 'Centro Revisioni', hasScheda: false },
    { value: 'detailing', label: 'Detailing / Car Care', hasScheda: true },
  ],
  wellness: [
    { value: 'palestra', label: 'Palestra / Fitness', hasScheda: true },
    { value: 'personal_trainer', label: 'Personal Trainer / Studio', hasScheda: true },
    { value: 'yoga_pilates', label: 'Yoga / Pilates Studio', hasScheda: true },
    { value: 'crossfit', label: 'Box CrossFit', hasScheda: true },
    { value: 'piscina', label: 'Centro Nuoto / Piscina', hasScheda: true },
    { value: 'arti_marziali', label: 'Palestra Arti Marziali', hasScheda: true },
  ],
  professionale: [
    { value: 'commercialista', label: 'Studio Commercialista', hasScheda: false },
    { value: 'avvocato', label: 'Studio Legale', hasScheda: false },
    { value: 'consulente', label: 'Consulente / Freelance', hasScheda: false },
    { value: 'agenzia', label: 'Agenzia Immobiliare', hasScheda: false },
    { value: 'architetto', label: 'Studio Architettura', hasScheda: false },
  ],
};

// ─────────────────────────────────────────────────────────────────────
// SCHEMA ZOD AGGIORNATO
// ─────────────────────────────────────────────────────────────────────

export const SetupConfigVerticalSchema = z.object({
  // Dati esistenti
  nome_attivita: z.string().min(2, 'Nome attività richiesto'),
  partita_iva: z.string().optional(),
  codice_fiscale: z.string().optional(),
  indirizzo: z.string().optional(),
  cap: z.string().optional(),
  citta: z.string().optional(),
  provincia: z.string().optional(),
  telefono: z.string().optional(),
  email: z.string().email().optional().or(z.literal('')),
  pec: z.string().optional(),
  regime_fiscale: z.enum(['RF01', 'RF19']).optional(),
  fluxion_ia_key: z.string().optional(),
  
  // Categorie legacy (mantenuta per compatibilità)
  categoria_attivita: z.enum(['salone', 'auto', 'wellness', 'medical', 'altro']).optional(),
  
  // NUOVO: Macro e Micro categoria
  macro_categoria: z.enum([
    'medico', 'beauty', 'hair', 'auto', 'wellness', 'professionale'
  ]).optional(),
  
  micro_categoria: z.string().optional(), // Valore dinamico in base alla macro
  
  // Flag configurazione completata
  setup_completato: z.boolean().default(false),
  setup_step_corrente: z.number().default(1),
});

export type SetupConfigVertical = z.infer<typeof SetupConfigVerticalSchema>;

// ─────────────────────────────────────────────────────────────────────
// MAPPING SCHEDE per Micro Categoria
// ─────────────────────────────────────────────────────────────────────

export const SCHEDE_PER_MICRO_CATEGORIA: Record<string, string> = {
  // Medico
  'odontoiatra': 'odontoiatrica',
  'fisioterapia': 'fisioterapia',
  'osteopata': 'fisioterapia',
  'podologo': 'fisioterapia',
  
  // Beauty
  'estetista_viso': 'estetica',
  'estetista_corpo': 'estetica',
  'nail_specialist': 'estetica',
  'epilazione_laser': 'estetica',
  'centro_abbronzatura': 'estetica',
  'spa': 'estetica',
  
  // Hair
  'salone_donna': 'parrucchiere',
  'barbiere': 'parrucchiere',
  'salone_unisex': 'parrucchiere',
  'extension_specialist': 'parrucchiere',
  'color_specialist': 'parrucchiere',
  'tricologo': 'parrucchiere',
  
  // Auto
  'officina_meccanica': 'veicoli',
  'carrozzeria': 'carrozzeria',
  'elettrauto': 'veicoli',
  'gommista': 'veicoli',
  'detailing': 'veicoli',
};

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

/**
 * Restituisce il tipo di scheda da usare per una micro categoria
 */
export function getTipoScheda(microCategoria: string): string | null {
  return SCHEDE_PER_MICRO_CATEGORIA[microCategoria] || null;
}

/**
 * Verifica se una micro categoria ha una scheda speciale
 */
export function hasSchedaSpeciale(microCategoria: string): boolean {
  return !!SCHEDE_PER_MICRO_CATEGORIA[microCategoria];
}

/**
 * Restituisce le micro categorie per una macro
 */
export function getMicroCategorie(macroCategoria: string): Array<{value: string, label: string, hasScheda: boolean}> {
  return MICRO_CATEGORIE[macroCategoria] || [];
}

/**
 * Restituisce la label di una micro categoria
 */
export function getMicroCategoriaLabel(macro: string, value: string): string {
  const micros = MICRO_CATEGORIE[macro] || [];
  const found = micros.find(m => m.value === value);
  return found?.label || value;
}

/**
 * Restituisce la label di una macro categoria
 */
export function getMacroCategoriaLabel(value: string): string {
  const found = MACRO_CATEGORIE.find(m => m.value === value);
  return found?.label || value;
}
