// FLUXION - RAG Types
// TypeScript types for Retrieval Augmented Generation with Groq

import { z } from 'zod';

// ============================================================================
// Zod Schemas
// ============================================================================

export const FaqEntrySchema = z.object({
  section: z.string(),
  question: z.string(),
  answer: z.string(),
});

export const RagResponseSchema = z.object({
  answer: z.string(),
  sources: z.array(FaqEntrySchema),
  confidence: z.number(),
  model: z.string(),
});

export const BusinessContextSchema = z.record(z.string(), z.string());

// ============================================================================
// TypeScript Types
// ============================================================================

export type FaqEntry = z.infer<typeof FaqEntrySchema>;
export type RagResponse = z.infer<typeof RagResponseSchema>;
export type BusinessContext = z.infer<typeof BusinessContextSchema>;

// Available FAQ categories
export type FaqCategory =
  | 'salone'
  | 'auto'
  | 'wellness'
  | 'medical'
  | 'ristorante';

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Build business context from app settings
 */
export function buildBusinessContext(settings: {
  nome?: string;
  indirizzo?: string;
  telefono?: string;
  whatsapp?: string;
  email?: string;
  orari?: string;
}): BusinessContext {
  const context: BusinessContext = {};

  if (settings.nome) context['NOME_ATTIVITA'] = settings.nome;
  if (settings.indirizzo) context['INDIRIZZO'] = settings.indirizzo;
  if (settings.telefono) context['TELEFONO'] = settings.telefono;
  if (settings.whatsapp) context['WHATSAPP'] = settings.whatsapp;
  if (settings.email) context['EMAIL'] = settings.email;
  if (settings.orari) context['ORARI_SETTIMANALI'] = settings.orari;

  return context;
}

/**
 * Get confidence level label
 */
export function getConfidenceLabel(confidence: number): {
  label: string;
  color: 'green' | 'yellow' | 'red';
} {
  if (confidence >= 0.7) {
    return { label: 'Alta', color: 'green' };
  } else if (confidence >= 0.4) {
    return { label: 'Media', color: 'yellow' };
  } else {
    return { label: 'Bassa', color: 'red' };
  }
}

/**
 * Category display names
 */
export const FAQ_CATEGORY_LABELS: Record<FaqCategory, string> = {
  salone: 'Salone di Bellezza',
  auto: 'Officina / Carrozzeria',
  wellness: 'Palestra / SPA',
  medical: 'Studio Medico',
  ristorante: 'Ristorante / Bar',
};
