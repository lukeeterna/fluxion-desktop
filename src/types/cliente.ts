// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cliente Types
// TypeScript types matching Rust structs
// ═══════════════════════════════════════════════════════════════════

export interface Cliente {
  id: string;

  // Anagrafica
  nome: string;
  cognome: string;
  soprannome: string | null; // Per identificazione WhatsApp
  email: string | null;
  telefono: string;
  data_nascita: string | null;

  // Indirizzo
  indirizzo: string | null;
  cap: string | null;
  citta: string | null;
  provincia: string | null;

  // Fiscale
  codice_fiscale: string | null;
  partita_iva: string | null;
  codice_sdi: string | null;
  pec: string | null;

  // Metadata
  note: string | null;
  tags: string | null; // JSON string array: ["vip", "fedele"]
  fonte: string | null;

  // GDPR
  consenso_marketing: number; // 0 or 1
  consenso_whatsapp: number; // 0 or 1
  data_consenso: string | null;

  // Loyalty (Fase 5)
  loyalty_visits: number | null;
  loyalty_threshold: number | null;
  is_vip: number | null; // 0 or 1
  referral_source: string | null;
  referral_cliente_id: string | null;

  // Timestamps
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface CreateClienteInput {
  nome: string;
  cognome: string;
  soprannome?: string;
  telefono: string;
  email?: string;
  data_nascita?: string;
  indirizzo?: string;
  cap?: string;
  citta?: string;
  provincia?: string;
  codice_fiscale?: string;
  partita_iva?: string;
  codice_sdi?: string;
  pec?: string;
  note?: string;
  tags?: string;
  fonte?: string;
  consenso_marketing?: number;
  consenso_whatsapp?: number;
}

export interface UpdateClienteInput {
  id: string;
  nome: string;
  cognome: string;
  soprannome?: string;
  telefono: string;
  email?: string;
  data_nascita?: string;
  indirizzo?: string;
  cap?: string;
  citta?: string;
  provincia?: string;
  codice_fiscale?: string;
  partita_iva?: string;
  codice_sdi?: string;
  pec?: string;
  note?: string;
  tags?: string;
  fonte?: string;
  consenso_marketing?: number;
  consenso_whatsapp?: number;
}

// Helper to get full name
export function getClienteFullName(cliente: Cliente): string {
  return `${cliente.nome} ${cliente.cognome}`;
}

// Helper to get formatted phone
export function getClienteFormattedPhone(cliente: Cliente): string {
  // Simple formatting for Italian phones
  const phone = cliente.telefono.replace(/\s/g, '');
  if (phone.startsWith('+39')) {
    return phone.replace('+39', '+39 ');
  }
  return phone;
}

// Helper to parse tags
export function getClienteTags(cliente: Cliente): string[] {
  if (!cliente.tags) return [];
  try {
    return JSON.parse(cliente.tags) as string[];
  } catch {
    return [];
  }
}
