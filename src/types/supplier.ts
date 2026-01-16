// ═══════════════════════════════════════════════════════════════════
// FLUXION - Supplier Types
// TypeScript types matching Rust structs for supplier management
// ═══════════════════════════════════════════════════════════════════

export interface Supplier {
  id: string;
  nome: string;
  email: string | null;
  telefono: string | null;
  partita_iva: string | null;
  indirizzo: string | null;
  citta: string | null;
  cap: string | null;
  provincia: string | null;
  paese: string;
  iban: string | null;
  note: string | null;
  categoria: string | null;
  status: 'active' | 'inactive' | 'blocked';
  created_at: string;
  updated_at: string;
}

export interface CreateSupplierInput {
  nome: string;
  email?: string;
  telefono?: string;
  partita_iva?: string;
  indirizzo?: string;
  citta?: string;
  cap?: string;
  provincia?: string;
  paese?: string;
  iban?: string;
  note?: string;
  categoria?: string;
}

export interface UpdateSupplierInput {
  id: string;
  nome: string;
  email?: string;
  telefono?: string;
  partita_iva?: string;
  indirizzo?: string;
  citta?: string;
  cap?: string;
  provincia?: string;
  paese?: string;
  iban?: string;
  note?: string;
  categoria?: string;
  status?: 'active' | 'inactive' | 'blocked';
}

export interface SupplierOrder {
  id: string;
  supplier_id: string;
  ordine_numero: string;
  data_ordine: string;
  data_consegna_prevista: string | null;
  data_consegna_effettiva: string | null;
  importo_totale: number;
  status: 'draft' | 'sent' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  items: string; // JSON array
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderInput {
  supplier_id: string;
  ordine_numero: string;
  data_consegna_prevista?: string;
  importo_totale: number;
  items: string; // JSON array
  notes?: string;
}

export interface SupplierInteraction {
  id: string;
  supplier_id: string;
  order_id: string | null;
  tipo: 'email' | 'whatsapp' | 'call' | 'note';
  messaggio: string | null;
  status: string | null;
  created_at: string;
}

export interface SupplierStats {
  total_orders: number;
  total_spent: number;
  avg_order_value: number;
  last_order_date: string | null;
  pending_orders: number;
}

// Helper to format supplier display name
export function getSupplierDisplayName(supplier: Supplier): string {
  return supplier.nome;
}

// Helper to format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
}

// Order status labels in Italian
export const ORDER_STATUS_LABELS: Record<SupplierOrder['status'], string> = {
  draft: 'Bozza',
  sent: 'Inviato',
  confirmed: 'Confermato',
  shipped: 'Spedito',
  delivered: 'Consegnato',
  cancelled: 'Annullato',
};

// Supplier status labels
export const SUPPLIER_STATUS_LABELS: Record<Supplier['status'], string> = {
  active: 'Attivo',
  inactive: 'Inattivo',
  blocked: 'Bloccato',
};
