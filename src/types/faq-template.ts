// ═══════════════════════════════════════════════════════════════════
// FLUXION - FAQ Template Types
// RAG Locale Leggero con template e variabili
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// FAQ Settings (variabili per template)
// ───────────────────────────────────────────────────────────────────

export const FaqSettingSchema = z.object({
  chiave: z.string(),
  valore: z.string(),
  categoria: z.string().nullable(),
  descrizione: z.string().nullable(),
});

export type FaqSetting = z.infer<typeof FaqSettingSchema>;

// ───────────────────────────────────────────────────────────────────
// FAQ Search Result
// ───────────────────────────────────────────────────────────────────

export const FaqSearchResultSchema = z.object({
  domanda: z.string(),
  risposta: z.string(),
  score: z.number(), // 0-1 confidence score
  categoria: z.string().nullable(),
});

export type FaqSearchResult = z.infer<typeof FaqSearchResultSchema>;

// ───────────────────────────────────────────────────────────────────
// Cliente Identificato (per WhatsApp)
// ───────────────────────────────────────────────────────────────────

export const ClienteMinimoSchema = z.object({
  id: z.string(),
  nome: z.string(),
  cognome: z.string(),
  soprannome: z.string().nullable(),
  telefono: z.string(),
});

export type ClienteMinimo = z.infer<typeof ClienteMinimoSchema>;

export const ClienteIdentificatoSchema = z.object({
  id: z.string(),
  nome: z.string(),
  cognome: z.string(),
  soprannome: z.string().nullable(),
  telefono: z.string(),
  match_type: z.enum(['telefono', 'nome', 'soprannome', 'data_nascita', 'ambiguo']),
  ambiguo: z.boolean(),
  candidati: z.array(ClienteMinimoSchema),
});

export type ClienteIdentificato = z.infer<typeof ClienteIdentificatoSchema>;

// ───────────────────────────────────────────────────────────────────
// Categorie FAQ Settings
// ───────────────────────────────────────────────────────────────────

export const FAQ_CATEGORIE = [
  'orari',
  'prenotazioni',
  'pagamenti',
  'consulenza',
  'logistica',
  'prodotti',
  'servizi',
  'frequenze',
  'post_trattamento',
  'cura',
  'faq',
  'igiene',
  'extra',
  'contatti',
  'promozioni',
] as const;

export type FaqCategoria = typeof FAQ_CATEGORIE[number];

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

export function getConfidenceLevel(score: number): 'high' | 'medium' | 'low' {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
}

export function getConfidenceColor(score: number): string {
  const level = getConfidenceLevel(score);
  switch (level) {
    case 'high':
      return 'text-green-600 bg-green-100';
    case 'medium':
      return 'text-yellow-600 bg-yellow-100';
    case 'low':
      return 'text-red-600 bg-red-100';
  }
}

export function formatMatchType(matchType: string): string {
  switch (matchType) {
    case 'telefono':
      return 'Trovato per numero di telefono';
    case 'nome':
      return 'Trovato per nome';
    case 'soprannome':
      return 'Trovato per soprannome';
    case 'data_nascita':
      return 'Trovato per data di nascita';
    case 'ambiguo':
      return 'Risultato ambiguo - seleziona il cliente';
    default:
      return matchType;
  }
}
