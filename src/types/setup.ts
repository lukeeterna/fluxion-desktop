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

  // Categoria attività legacy (mantenuta per compatibilità)
  categoria_attivita: z.enum(['salone', 'auto', 'wellness', 'medical', 'altro']).optional(),
  
  // NUOVO: Macro e Micro categoria per verticali
  macro_categoria: z.enum(['medico', 'beauty', 'hair', 'auto', 'wellness', 'professionale']).optional(),
  micro_categoria: z.string().optional(), // Valore dinamico in base alla macro
  
  // NUOVO: Tier licenza selezionato
  license_tier: z.enum(['trial', 'base', 'pro', 'enterprise']).optional(),
  
  // NUOVO: Configurazione comunicazioni (Step 6)
  whatsapp_number: z.string().optional().or(z.literal('')),
  ehiweb_number: z.string().optional().or(z.literal('')),

  // NUOVO: Groq API key per Voice Agent Sara (Step 7)
  groq_api_key: z.string().optional().or(z.literal('')),
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
// MACRO CATEGORIE (Nuovo sistema verticali)
// ─────────────────────────────────────────────────────────────────────

export const MACRO_CATEGORIE = [
  { 
    value: 'medico', 
    label: 'Sanitario / Medico',
    icon: '🏥',
    description: 'Studi medici, dentisti, fisioterapisti',
    color: 'red'
  },
  { 
    value: 'beauty', 
    label: 'Bellezza / Estetica',
    icon: '💅',
    description: 'Estetiste, centri benessere, nail art',
    color: 'pink'
  },
  { 
    value: 'hair', 
    label: 'Parrucchiere / Barbiere',
    icon: '💇',
    description: 'Saloni, barbieri, hair stylist',
    color: 'purple'
  },
  { 
    value: 'auto', 
    label: 'Automotive',
    icon: '🚗',
    description: 'Officine, carrozzerie, elettrauto',
    color: 'blue'
  },
  { 
    value: 'wellness', 
    label: 'Wellness / Fitness',
    icon: '🧘',
    description: 'Palestre, yoga, centri benessere',
    color: 'green'
  },
  { 
    value: 'professionale', 
    label: 'Servizi Professionali',
    icon: '💼',
    description: 'Consulenti, commercialisti, avvocati',
    color: 'gray'
  },
] as const;

// ─────────────────────────────────────────────────────────────────────
// MICRO CATEGORIE per Macro
// ─────────────────────────────────────────────────────────────────────

export const MICRO_CATEGORIE: Record<string, Array<{value: string, label: string, hasScheda: boolean, schedaType?: string}>> = {
  medico: [
    { value: 'odontoiatra', label: 'Odontoiatra / Dentista', hasScheda: true, schedaType: 'odontoiatrica' },
    { value: 'fisioterapia', label: 'Fisioterapia / Riabilitazione', hasScheda: true, schedaType: 'fisioterapia' },
    { value: 'medico_generico', label: 'Medico Generico', hasScheda: true, schedaType: 'medica' },
    { value: 'specialista', label: 'Specialista (cardiologo, etc.)', hasScheda: true, schedaType: 'medica' },
    { value: 'osteopata', label: 'Osteopata', hasScheda: true, schedaType: 'fisioterapia' },
    { value: 'podologo', label: 'Podologo', hasScheda: true, schedaType: 'fisioterapia' },
    { value: 'psicologo', label: 'Psicologo / Psicoterapeuta', hasScheda: true, schedaType: 'medica' },
    { value: 'nutrizionista', label: 'Nutrizionista', hasScheda: true, schedaType: 'medica' },
  ],
  beauty: [
    { value: 'estetista_viso', label: 'Estetista - Trattamenti Viso', hasScheda: true, schedaType: 'estetica' },
    { value: 'estetista_corpo', label: 'Estetista - Trattamenti Corpo', hasScheda: true, schedaType: 'estetica' },
    { value: 'nail_specialist', label: 'Nail Specialist', hasScheda: true, schedaType: 'estetica' },
    { value: 'epilazione_laser', label: 'Centro Epilazione Laser', hasScheda: true, schedaType: 'estetica' },
    { value: 'centro_abbronzatura', label: 'Centro Abbronzatura', hasScheda: true, schedaType: 'estetica' },
    { value: 'spa', label: 'SPA / Centri Benessere', hasScheda: true, schedaType: 'estetica' },
  ],
  hair: [
    { value: 'salone_donna', label: 'Salone Donna', hasScheda: true, schedaType: 'parrucchiere' },
    { value: 'barbiere', label: 'Barbiere Tradizionale', hasScheda: true, schedaType: 'parrucchiere' },
    { value: 'salone_unisex', label: 'Salone Unisex', hasScheda: true, schedaType: 'parrucchiere' },
    { value: 'extension_specialist', label: 'Extension Specialist', hasScheda: true, schedaType: 'parrucchiere' },
    { value: 'color_specialist', label: 'Color Specialist', hasScheda: true, schedaType: 'parrucchiere' },
    { value: 'tricologo', label: 'Tricologo / Caduta Capelli', hasScheda: true, schedaType: 'parrucchiere' },
  ],
  auto: [
    { value: 'officina_meccanica', label: 'Officina Meccanica', hasScheda: true, schedaType: 'veicoli' },
    { value: 'carrozzeria', label: 'Carrozzeria', hasScheda: true, schedaType: 'carrozzeria' },
    { value: 'elettrauto', label: 'Elettrauto', hasScheda: true, schedaType: 'veicoli' },
    { value: 'gommista', label: 'Gommista / Pneumatici', hasScheda: true, schedaType: 'veicoli' },
    { value: 'revisioni', label: 'Centro Revisioni', hasScheda: false },
    { value: 'detailing', label: 'Detailing / Car Care', hasScheda: true, schedaType: 'veicoli' },
  ],
  wellness: [
    { value: 'palestra', label: 'Palestra / Fitness', hasScheda: true, schedaType: 'fitness' },
    { value: 'personal_trainer', label: 'Personal Trainer / Studio', hasScheda: true, schedaType: 'fitness' },
    { value: 'yoga_pilates', label: 'Yoga / Pilates Studio', hasScheda: true, schedaType: 'fitness' },
    { value: 'crossfit', label: 'Box CrossFit', hasScheda: true, schedaType: 'fitness' },
    { value: 'piscina', label: 'Centro Nuoto / Piscina', hasScheda: true, schedaType: 'fitness' },
    { value: 'arti_marziali', label: 'Palestra Arti Marziali', hasScheda: true, schedaType: 'fitness' },
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
// LICENSE TIERS
// ─────────────────────────────────────────────────────────────────────

export const LICENSE_TIERS = [
  {
    value: 'trial',
    label: 'Trial 30 giorni',
    description: 'Prova gratuita con tutte le funzionalità',
    price: 0,
    features: ['Tutte le schede verticali', 'Voice Agent', 'Supporto'],
    color: 'yellow',
  },
  {
    value: 'base',
    label: 'FLUXION Base',
    description: 'Gestionale completo - Lifetime',
    price: 199,
    features: ['CRM Clienti', 'Calendario', 'Fatturazione', '1 Scheda Verticale'],
    color: 'blue',
  },
  {
    value: 'pro',
    label: 'FLUXION Pro',
    description: 'Gestionale + 3 Verticali - Lifetime',
    price: 399,
    features: ['Tutto di Base', '3 Schede Verticali', 'Loyalty Avanzato', 'Voice Agent'],
    color: 'purple',
  },
  {
    value: 'enterprise',
    label: 'FLUXION Enterprise',
    description: 'Tutto illimitato - Lifetime',
    price: 799,
    features: ['Tutte le Schede Verticali', 'Voice Agent', 'API Access', 'Supporto Prioritario'],
    color: 'gold',
  },
] as const;

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS LEGACY
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
  macro_categoria: undefined,
  micro_categoria: undefined,
  license_tier: 'trial',
  whatsapp_number: '',
  ehiweb_number: '',
  groq_api_key: '',
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

/**
 * Restituisce il tipo di scheda da usare per una micro categoria
 */
export function getTipoScheda(microCategoria: string): string | null {
  for (const macro of Object.values(MICRO_CATEGORIE)) {
    const found = macro.find(m => m.value === microCategoria);
    if (found?.schedaType) return found.schedaType;
  }
  return null;
}

/**
 * Verifica se una micro categoria ha una scheda speciale
 */
export function hasSchedaSpeciale(microCategoria: string): boolean {
  return !!getTipoScheda(microCategoria);
}

/**
 * Restituisce le micro categorie per una macro
 */
export function getMicroCategorie(macroCategoria: string): Array<{value: string, label: string, hasScheda: boolean, schedaType?: string}> {
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

/**
 * Mappa micro categoria a componente scheda
 */
export const SCHEDE_PER_MICRO_CATEGORIA: Record<string, string> = {
  // Medico
  'odontoiatra': 'odontoiatrica',
  'fisioterapia': 'fisioterapia',
  'osteopata': 'fisioterapia',
  'podologo': 'fisioterapia',
  'medico_generico': 'medica',
  'specialista': 'medica',
  'psicologo': 'medica',
  'nutrizionista': 'medica',
  
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
  
  // Wellness
  'palestra': 'fitness',
  'personal_trainer': 'fitness',
  'yoga_pilates': 'fitness',
  'crossfit': 'fitness',
  'piscina': 'fitness',
  'arti_marziali': 'fitness',
};
