// ═══════════════════════════════════════════════════════════════════
// FLUXION - Magazzino Types
// Articoli, movimenti carico/scarico, alert sottoscorta
// ═══════════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────────
// Core domain types (mirrored from Rust structs in magazzino.rs)
// ───────────────────────────────────────────────────────────────────

export interface Articolo {
  id: string;
  nome: string;
  categoria: string | null;
  giacenza: number;
  soglia_minima: number;
  prezzo_acquisto: number | null;
  prezzo_vendita: number | null;
  ean: string | null;
  fornitore_id: string | null;
  alert_notificato: number;
  attivo: number;
  created_at: string;
  updated_at: string;
}

export interface MovimentoMagazzino {
  id: string;
  articolo_id: string;
  tipo: 'carico' | 'scarico';
  quantita: number;
  causale: string | null;
  riferimento: string | null;
  created_at: string;
}

// ───────────────────────────────────────────────────────────────────
// Input types for mutations
// ───────────────────────────────────────────────────────────────────

export interface CreaArticoloInput {
  nome: string;
  categoria?: string;
  sogliaMinima: number;
  prezzoAcquisto?: number;
  prezzoVendita?: number;
  ean?: string;
  fornitoreId?: string;
}

export interface AggiornaArticoloInput {
  id: string;
  nome: string;
  categoria?: string;
  sogliaMinima: number;
  prezzoAcquisto?: number;
  prezzoVendita?: number;
  ean?: string;
  fornitoreId?: string;
}

export interface RegistraMovimentoInput {
  articoloId: string;
  tipo: 'carico' | 'scarico';
  quantita: number;
  causale?: string;
  riferimento?: string;
}

export interface SetSogliaInput {
  id: string;
  sogliaMinima: number;
}
