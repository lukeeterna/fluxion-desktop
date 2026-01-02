// ═══════════════════════════════════════════════════════════════════
// FLUXION - WhatsApp Types
// TypeScript types matching Rust structs (whatsapp.rs)
// ═══════════════════════════════════════════════════════════════════

export interface WhatsAppTemplate {
  id: string;
  nome: string;
  categoria: string; // 'conferma' | 'reminder' | 'marketing' | 'loyalty' | 'waitlist' | 'emergenza' | 'followup' | 'pacchetti' | 'cancellazione'
  descrizione: string | null;
  template_text: string;
  variabili: string | null; // JSON array: ["nome", "data", "servizio", "operatore"]
  predefinito: number; // 0 = custom, 1 = system template
  attivo: number; // 0 = deleted, 1 = active
  uso_count: number;
  ultimo_uso: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateWhatsAppTemplateInput {
  nome: string;
  categoria: string;
  descrizione?: string;
  template_text: string;
  variabili?: string[];
}

export interface UpdateWhatsAppTemplateInput {
  nome?: string;
  categoria?: string;
  descrizione?: string;
  template_text?: string;
  variabili?: string[];
  attivo?: number;
}

export interface FillTemplateInput {
  template_id: string;
  variables: Record<string, string>;
  cliente_id?: string;
  appuntamento_id?: string;
}

// ───────────────────────────────────────────────────────────────────
// Helper Functions
// ───────────────────────────────────────────────────────────────────

/**
 * Parse variabili JSON string to array
 */
export function getTemplateVariables(template: WhatsAppTemplate): string[] {
  if (!template.variabili) return [];
  try {
    return JSON.parse(template.variabili) as string[];
  } catch {
    return [];
  }
}

/**
 * Get category display name
 */
export function getCategoryLabel(categoria: string): string {
  const labels: Record<string, string> = {
    conferma: 'Conferma',
    reminder: 'Promemoria',
    marketing: 'Marketing',
    loyalty: 'Fedeltà',
    waitlist: 'Lista Attesa',
    emergenza: 'Emergenza',
    followup: 'Follow-Up',
    pacchetti: 'Pacchetti',
    cancellazione: 'Cancellazione/Spostamento',
  };
  return labels[categoria] || categoria;
}

/**
 * Get category icon emoji
 */
export function getCategoryIcon(categoria: string): string {
  const icons: Record<string, string> = {
    conferma: '✅',
    reminder: '⏰',
    marketing: '📣',
    loyalty: '⭐',
    waitlist: '📋',
    emergenza: '⚠️',
    followup: '🔄',
    pacchetti: '🎁',
    cancellazione: '🔀',
  };
  return icons[categoria] || '📝';
}

/**
 * Extract placeholders from template text ({{nome}}, {{data}}, etc.)
 */
export function extractPlaceholders(templateText: string): string[] {
  const regex = /\{\{(\w+)\}\}/g;
  const placeholders = new Set<string>();
  let match;

  while ((match = regex.exec(templateText)) !== null) {
    placeholders.add(match[1]);
  }

  return Array.from(placeholders);
}

/**
 * Preview template with filled variables (client-side)
 */
export function previewTemplate(
  templateText: string,
  variables: Record<string, string>
): string {
  let result = templateText;

  for (const [key, value] of Object.entries(variables)) {
    const placeholder = `{{${key}}}`;
    result = result.replace(new RegExp(placeholder, 'g'), value);
  }

  // Handle conditional lines (e.g., {{operatore_line}})
  if (variables['operatore'] && variables['operatore'].trim()) {
    result = result.replace(
      '{{operatore_line}}',
      `👤 Con: ${variables['operatore']}\n`
    );
  } else {
    result = result.replace('{{operatore_line}}', '');
  }

  return result;
}

/**
 * Generate WhatsApp wa.me link
 */
export function generateWhatsAppLink(phone: string, text: string): string {
  // Remove +, spaces, dashes from phone
  const cleanPhone = phone.replace(/[\s\-+]/g, '');

  // URL encode text
  const encodedText = encodeURIComponent(text);

  return `https://wa.me/${cleanPhone}?text=${encodedText}`;
}

/**
 * Check if template is system default (predefinito = 1)
 */
export function isSystemTemplate(template: WhatsAppTemplate): boolean {
  return template.predefinito === 1;
}
