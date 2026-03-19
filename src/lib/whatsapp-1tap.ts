// ─── FLUXION WhatsApp 1-Tap ────────────────────────────────────────
// Zero-cost WhatsApp integration via wa.me deep links.
// No API key, no WhatsApp Business API, no risk of ban.
// Works cross-platform: opens WhatsApp app with pre-filled message.
//
// Architecture: wa.me/{phone}?text={encoded_message}
// Decisione CTO S90: Opzione A — 1-tap safe, zero costo

import { openUrl } from '@tauri-apps/plugin-opener';

// ─── Phone Number Normalization ────────────────────────────────────

/**
 * Normalize Italian phone number to international format (no + prefix for wa.me).
 * wa.me requires format: 393331234567 (country code + number, no +, no spaces)
 *
 * @example normalizePhone('+39 333 123 4567') → '393331234567'
 * @example normalizePhone('333 1234567') → '393331234567'
 * @example normalizePhone('0039 333 1234567') → '393331234567'
 */
export function normalizePhone(phone: string): string {
  // Remove all non-digit characters
  let digits = phone.replace(/\D/g, '');

  // Handle Italian prefixes
  if (digits.startsWith('0039')) {
    digits = '39' + digits.slice(4);
  } else if (digits.startsWith('39') && digits.length >= 11) {
    // Already has country code
  } else if (digits.startsWith('3') && digits.length === 10) {
    // Italian mobile without country code (3xx xxx xxxx)
    digits = '39' + digits;
  } else if (digits.startsWith('0') && digits.length >= 9) {
    // Italian landline (0xx xxx xxxx)
    digits = '39' + digits;
  }

  return digits;
}

// ─── wa.me URL Builder ─────────────────────────────────────────────

/**
 * Build a wa.me deep link URL.
 * Opens WhatsApp with pre-filled message to the specified number.
 */
export function buildWhatsAppUrl(phone: string, message: string): string {
  const normalized = normalizePhone(phone);
  const encoded = encodeURIComponent(message);
  return `https://wa.me/${normalized}?text=${encoded}`;
}

// ─── Send WhatsApp 1-Tap ──────────────────────────────────────────

/**
 * Open WhatsApp with pre-filled message via Tauri opener plugin.
 * The user taps "Send" in WhatsApp to complete.
 */
export async function sendWhatsApp1Tap(
  phone: string,
  message: string,
): Promise<void> {
  const url = buildWhatsAppUrl(phone, message);
  await openUrl(url);
}

// ─── Message Templates (Italian) ──────────────────────────────────

export interface WhatsAppTemplateParams {
  nome_cliente: string;
  nome_attivita: string;
  servizio?: string;
  data?: string; // e.g. "martedì 11 marzo"
  ora?: string; // e.g. "10:30"
  operatore?: string;
}

/**
 * Pre-built WhatsApp message templates for Italian PMI.
 * Each returns a ready-to-send message string.
 */
export const whatsappTemplates = {
  /**
   * Conferma prenotazione — inviata dopo la creazione dell'appuntamento
   */
  conferma: (p: WhatsAppTemplateParams): string =>
    `Ciao ${p.nome_cliente}! ✅\n\n` +
    `Il tuo appuntamento presso *${p.nome_attivita}* è confermato:\n\n` +
    `📅 ${p.data || ''}\n` +
    `🕐 ${p.ora || ''}\n` +
    (p.servizio ? `💇 ${p.servizio}\n` : '') +
    (p.operatore ? `👤 ${p.operatore}\n` : '') +
    `\nTi aspettiamo! Per modifiche, rispondi a questo messaggio.`,

  /**
   * Promemoria 24h — inviato il giorno prima dell'appuntamento
   */
  reminder24h: (p: WhatsAppTemplateParams): string =>
    `Ciao ${p.nome_cliente}! 📋\n\n` +
    `Ti ricordiamo il tuo appuntamento di *domani* presso ${p.nome_attivita}:\n\n` +
    `🕐 ${p.ora || ''}\n` +
    (p.servizio ? `💇 ${p.servizio}\n` : '') +
    `\nTi aspettiamo! Rispondi se hai bisogno di spostare.`,

  /**
   * Cancellazione — inviata quando l'appuntamento viene cancellato
   */
  cancellazione: (p: WhatsAppTemplateParams): string =>
    `Ciao ${p.nome_cliente},\n\n` +
    `Il tuo appuntamento presso ${p.nome_attivita}` +
    (p.data ? ` del ${p.data}` : '') +
    (p.ora ? ` alle ${p.ora}` : '') +
    ` è stato cancellato.\n\n` +
    `Per prenotare un nuovo appuntamento, rispondi a questo messaggio o chiamaci.`,

  /**
   * Compleanno — inviato 7 giorni prima del compleanno
   */
  compleanno: (p: WhatsAppTemplateParams): string =>
    `Ciao ${p.nome_cliente}! 🎂\n\n` +
    `*${p.nome_attivita}* ti augura buon compleanno! 🎉\n\n` +
    `Per festeggiare, ti offriamo uno sconto speciale sul tuo prossimo appuntamento.\n` +
    `Rispondi per prenotare! 💫`,

  /**
   * Follow-up — inviato N giorni dopo l'ultimo appuntamento
   */
  followUp: (p: WhatsAppTemplateParams): string =>
    `Ciao ${p.nome_cliente}! 👋\n\n` +
    `È da un po' che non ci vediamo da *${p.nome_attivita}*.\n\n` +
    `Vuoi prenotare il tuo prossimo appuntamento? Rispondi a questo messaggio e ci pensiamo noi! 📅`,

  /**
   * Waitlist — inviato quando si libera uno slot
   */
  waitlist: (p: WhatsAppTemplateParams): string =>
    `Ciao ${p.nome_cliente}! 🎯\n\n` +
    `Buone notizie! Si è liberato un posto presso *${p.nome_attivita}*:\n\n` +
    `📅 ${p.data || ''}\n` +
    `🕐 ${p.ora || ''}\n` +
    (p.servizio ? `💇 ${p.servizio}\n` : '') +
    `\nVuoi confermare? Rispondi "Sì" entro 2 ore per prenotare.`,
} as const;

// ─── Template Keys Type ───────────────────────────────────────────
export type WhatsAppTemplateKey = keyof typeof whatsappTemplates;
