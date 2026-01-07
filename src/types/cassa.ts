// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cassa/Incassi Types
// Sistema gestionale puro - RT separato per scontrini
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ───────────────────────────────────────────────────────────────────
// Incasso
// ───────────────────────────────────────────────────────────────────

export const IncassoSchema = z.object({
  id: z.string(),
  importo: z.number(),
  metodo_pagamento: z.string(),
  cliente_id: z.string().nullable(),
  appuntamento_id: z.string().nullable(),
  fattura_id: z.string().nullable(),
  descrizione: z.string().nullable(),
  categoria: z.string().nullable(),
  operatore_id: z.string().nullable(),
  data_incasso: z.string(),
  created_at: z.string(),
});

export type Incasso = z.infer<typeof IncassoSchema>;

export const CreateIncassoInputSchema = z.object({
  importo: z.number().positive('Importo deve essere positivo'),
  metodo_pagamento: z.string().min(1, 'Seleziona metodo di pagamento'),
  cliente_id: z.string().optional(),
  appuntamento_id: z.string().optional(),
  descrizione: z.string().optional(),
  categoria: z.string().optional(),
  operatore_id: z.string().optional(),
});

export type CreateIncassoInput = z.infer<typeof CreateIncassoInputSchema>;

// ───────────────────────────────────────────────────────────────────
// Incasso con dettagli (per lista)
// ───────────────────────────────────────────────────────────────────

export const IncassoConDettagliSchema = z.object({
  id: z.string(),
  importo: z.number(),
  metodo_pagamento: z.string(),
  descrizione: z.string().nullable(),
  categoria: z.string().nullable(),
  data_incasso: z.string(),
  cliente_nome: z.string().nullable(),
  servizio_nome: z.string().nullable(),
});

export type IncassoConDettagli = z.infer<typeof IncassoConDettagliSchema>;

// ───────────────────────────────────────────────────────────────────
// Report Giornata
// ───────────────────────────────────────────────────────────────────

export const ReportIncassiGiornataSchema = z.object({
  data: z.string(),
  totale: z.number(),
  totale_contanti: z.number(),
  totale_carte: z.number(),
  totale_satispay: z.number(),
  totale_altro: z.number(),
  numero_transazioni: z.number(),
  incassi: z.array(IncassoConDettagliSchema),
});

export type ReportIncassiGiornata = z.infer<typeof ReportIncassiGiornataSchema>;

// ───────────────────────────────────────────────────────────────────
// Chiusura Cassa
// ───────────────────────────────────────────────────────────────────

export const ChiusuraCassaSchema = z.object({
  id: z.string(),
  data_chiusura: z.string(),
  totale_contanti: z.number(),
  totale_carte: z.number(),
  totale_satispay: z.number(),
  totale_bonifici: z.number(),
  totale_altro: z.number(),
  totale_giornata: z.number(),
  numero_transazioni: z.number(),
  fondo_cassa_iniziale: z.number(),
  fondo_cassa_finale: z.number(),
  note: z.string().nullable(),
  operatore_id: z.string().nullable(),
  created_at: z.string(),
});

export type ChiusuraCassa = z.infer<typeof ChiusuraCassaSchema>;

// ───────────────────────────────────────────────────────────────────
// Report Periodo
// ───────────────────────────────────────────────────────────────────

export const TotaleMetodoSchema = z.object({
  metodo: z.string(),
  totale: z.number(),
  count: z.number(),
});

export type TotaleMetodo = z.infer<typeof TotaleMetodoSchema>;

export const TotaleGiornoSchema = z.object({
  data: z.string(),
  totale: z.number(),
  count: z.number(),
});

export type TotaleGiorno = z.infer<typeof TotaleGiornoSchema>;

export const ReportPeriodoSchema = z.object({
  data_inizio: z.string(),
  data_fine: z.string(),
  totale: z.number(),
  per_metodo: z.array(TotaleMetodoSchema),
  per_giorno: z.array(TotaleGiornoSchema),
  numero_transazioni: z.number(),
});

export type ReportPeriodo = z.infer<typeof ReportPeriodoSchema>;

// ───────────────────────────────────────────────────────────────────
// Metodo Pagamento
// ───────────────────────────────────────────────────────────────────

export const MetodoPagamentoSchema = z.object({
  codice: z.string(),
  nome: z.string(),
  icona: z.string().nullable(),
  attivo: z.number(),
  ordine: z.number(),
});

export type MetodoPagamento = z.infer<typeof MetodoPagamentoSchema>;

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

export function formatImporto(importo: number): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  }).format(importo);
}

export function getMetodoIcon(metodo: string): string {
  const icons: Record<string, string> = {
    contanti: '💵',
    carta: '💳',
    satispay: '📱',
    bonifico: '🏦',
    assegno: '📝',
    buono: '🎁',
    pacchetto: '📦',
    altro: '💰',
  };
  return icons[metodo] || '💰';
}

export function getMetodoColor(metodo: string): string {
  const colors: Record<string, string> = {
    contanti: 'bg-green-100 text-green-800',
    carta: 'bg-blue-100 text-blue-800',
    satispay: 'bg-red-100 text-red-800',
    bonifico: 'bg-purple-100 text-purple-800',
    altro: 'bg-gray-100 text-gray-800',
  };
  return colors[metodo] || 'bg-gray-100 text-gray-800';
}

export function getCategoriaLabel(categoria: string | null): string {
  const labels: Record<string, string> = {
    servizio: 'Servizio',
    prodotto: 'Prodotto',
    pacchetto: 'Pacchetto',
    altro: 'Altro',
  };
  return categoria ? labels[categoria] || categoria : 'Servizio';
}

// Helper per calcolare differenza cassa
export function calcolaDifferenzaCassa(
  chiusura: ChiusuraCassa
): { differenza: number; status: 'ok' | 'eccesso' | 'ammanco' } {
  const atteso = chiusura.fondo_cassa_iniziale + chiusura.totale_contanti;
  const differenza = chiusura.fondo_cassa_finale - atteso;

  if (Math.abs(differenza) < 0.01) {
    return { differenza: 0, status: 'ok' };
  } else if (differenza > 0) {
    return { differenza, status: 'eccesso' };
  } else {
    return { differenza, status: 'ammanco' };
  }
}
