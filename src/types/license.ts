// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Types (Phase 8)
// TypeScript types for license management
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ─── License Status Schema ───────────────────────────────────────────

export const LicenseStatusSchema = z.object({
  is_valid: z.boolean(),
  is_activated: z.boolean(),
  tier: z.enum(['trial', 'base', 'ia', 'expired', 'none']),
  status: z.enum(['trial', 'active', 'expired', 'suspended', 'none']),
  days_remaining: z.number().nullable(),
  expiry_date: z.string().nullable(),
  machine_fingerprint: z.string(),
  machine_name: z.string().nullable(),
  trial_ends_at: z.string().nullable(),
  last_validated_at: z.string().nullable(),
  validation_code: z.string(),
});

export type LicenseStatus = z.infer<typeof LicenseStatusSchema>;

// ─── Activation Result Schema ────────────────────────────────────────

export const ActivationResultSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  tier: z.string().nullable(),
  expiry_date: z.string().nullable(),
});

export type ActivationResult = z.infer<typeof ActivationResultSchema>;

// ─── License Tier Info ───────────────────────────────────────────────

export interface LicenseTierInfo {
  name: string;
  description: string;
  features: string[];
  color: string;
  icon: string;
}

export const LICENSE_TIERS: Record<string, LicenseTierInfo> = {
  trial: {
    name: 'Trial',
    description: '30 giorni di prova gratuita',
    features: ['CRM Clienti', 'Calendario', 'Fatturazione', 'Loyalty'],
    color: 'yellow',
    icon: 'Clock',
  },
  base: {
    name: 'FLUXION Base',
    description: 'Licenza annuale gestionale',
    features: ['CRM Clienti', 'Calendario', 'Fatturazione', 'Loyalty', 'Supporto email'],
    color: 'blue',
    icon: 'CheckCircle',
  },
  ia: {
    name: 'FLUXION IA',
    description: 'Licenza annuale con assistente vocale',
    features: [
      'Tutto di Base',
      'Voice Agent',
      'WhatsApp AI',
      'RAG Chat',
      'Supporto prioritario',
    ],
    color: 'purple',
    icon: 'Sparkles',
  },
  expired: {
    name: 'Scaduta',
    description: 'Licenza scaduta - rinnova per continuare',
    features: [],
    color: 'red',
    icon: 'XCircle',
  },
  none: {
    name: 'Nessuna Licenza',
    description: 'Attiva una licenza per utilizzare FLUXION',
    features: [],
    color: 'gray',
    icon: 'AlertCircle',
  },
};

// ─── Feature Access ──────────────────────────────────────────────────

export const IA_FEATURES = ['voice_agent', 'whatsapp_ai', 'rag_chat'] as const;
export type IAFeature = (typeof IA_FEATURES)[number];

// ─── Helper Functions ────────────────────────────────────────────────

export function formatLicenseKey(key: string): string {
  // Format as XXXX-XXXX-XXXX-XXXX
  const cleaned = key.replace(/[^A-Z0-9]/gi, '').toUpperCase();
  const chunks = cleaned.match(/.{1,4}/g) || [];
  return chunks.slice(0, 4).join('-');
}

export function isTrialExpiringSoon(status: LicenseStatus): boolean {
  if (status.tier !== 'trial' || !status.days_remaining) return false;
  return status.days_remaining <= 7;
}

export function getLicenseExpiryMessage(status: LicenseStatus): string | null {
  if (!status.days_remaining) return null;

  if (status.days_remaining <= 0) {
    return status.tier === 'trial'
      ? 'Il periodo di prova è terminato'
      : 'La licenza è scaduta';
  }

  if (status.days_remaining === 1) {
    return status.tier === 'trial'
      ? 'Ultimo giorno di prova!'
      : 'La licenza scade domani!';
  }

  if (status.days_remaining <= 7) {
    return status.tier === 'trial'
      ? `${status.days_remaining} giorni di prova rimanenti`
      : `La licenza scade tra ${status.days_remaining} giorni`;
  }

  return null;
}
