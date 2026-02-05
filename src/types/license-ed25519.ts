// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Ed25519 Types (Phase 8.5)
// TypeScript types per sistema licenze offline Ed25519
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ─── Tier Schema ───────────────────────────────────────────────────

export const LicenseTierSchema = z.enum(['trial', 'base', 'pro', 'enterprise']);
export type LicenseTier = z.infer<typeof LicenseTierSchema>;

// ─── Features Schema ────────────────────────────────────────────────

export const LicenseFeaturesSchema = z.object({
  voice_agent: z.boolean().default(false),
  whatsapp_ai: z.boolean().default(false),
  rag_chat: z.boolean().default(false),
  fatturazione_pa: z.boolean().default(true),
  loyalty_advanced: z.boolean().default(false),
  api_access: z.boolean().default(false),
  max_verticals: z.number().default(1),
});

export type LicenseFeatures = z.infer<typeof LicenseFeaturesSchema>;

// ─── Fluxion License Schema ─────────────────────────────────────────

export const FluxionLicenseSchema = z.object({
  version: z.string(),
  license_id: z.string(),
  tier: LicenseTierSchema,
  issued_at: z.string(),
  expires_at: z.string().nullable().optional(),
  hardware_fingerprint: z.string(),
  licensee_name: z.string().nullable().optional(),
  licensee_email: z.string().nullable().optional(),
  enabled_verticals: z.array(z.string()).default([]),
  max_operators: z.number().default(0),
  features: LicenseFeaturesSchema,
});

export type FluxionLicense = z.infer<typeof FluxionLicenseSchema>;

// ─── Signed License Schema ──────────────────────────────────────────

export const SignedLicenseSchema = z.object({
  license: FluxionLicenseSchema,
  signature: z.string(),
});

export type SignedLicense = z.infer<typeof SignedLicenseSchema>;

// ─── License Status Schema ──────────────────────────────────────────

export const LicenseStatusEd25519Schema = z.object({
  is_valid: z.boolean(),
  is_activated: z.boolean(),
  tier: z.string(),
  tier_display: z.string(),
  status: z.string(),
  days_remaining: z.number().nullable(),
  expiry_date: z.string().nullable(),
  machine_fingerprint: z.string(),
  machine_name: z.string().nullable(),
  license_id: z.string().nullable(),
  licensee_name: z.string().nullable(),
  enabled_verticals: z.array(z.string()),
  features: LicenseFeaturesSchema,
  validation_code: z.string(),
});

export type LicenseStatusEd25519 = z.infer<typeof LicenseStatusEd25519Schema>;

// ─── Activation Result Schema ───────────────────────────────────────

export const ActivationResultEd25519Schema = z.object({
  success: z.boolean(),
  message: z.string(),
  tier: z.string().nullable(),
  expiry_date: z.string().nullable(),
});

export type ActivationResultEd25519 = z.infer<typeof ActivationResultEd25519Schema>;

// ─── Tier Info Schema ───────────────────────────────────────────────

export const TierInfoSchema = z.object({
  value: z.string(),
  label: z.string(),
  description: z.string(),
  price: z.number(),
  features: z.array(z.string()),
  color: z.string(),
});

export type TierInfo = z.infer<typeof TierInfoSchema>;

// ─── Constants ──────────────────────────────────────────────────────

export const LICENSE_TIERS_ED25519: TierInfo[] = [
  {
    value: 'trial',
    label: 'Trial 30 giorni',
    description: 'Prova gratuita con tutte le funzionalità',
    price: 0,
    features: [
      'Tutte le schede verticali',
      'Voice Agent',
      'WhatsApp AI',
      'Supporto email',
    ],
    color: 'yellow',
  },
  {
    value: 'base',
    label: 'FLUXION Base',
    description: 'Gestionale completo - Lifetime',
    price: 199,
    features: [
      'CRM Clienti',
      'Calendario',
      'Fatturazione',
      '1 Scheda Verticale',
    ],
    color: 'blue',
  },
  {
    value: 'pro',
    label: 'FLUXION Pro',
    description: 'Gestionale + Voice + 3 Verticali - Lifetime',
    price: 399,
    features: [
      'Tutto di Base',
      '3 Schede Verticali',
      'Voice Agent',
      'WhatsApp AI',
      'Loyalty Avanzato',
    ],
    color: 'purple',
  },
  {
    value: 'enterprise',
    label: 'FLUXION Enterprise',
    description: 'Tutto illimitato - Lifetime',
    price: 799,
    features: [
      'Tutte le Schede Verticali',
      'Voice Agent',
      'API Access',
      'Supporto Prioritario',
      'Personalizzazioni',
    ],
    color: 'gold',
  },
];

// ─── Helper Functions ───────────────────────────────────────────────

export function getTierDisplayName(tier: string): string {
  const tierInfo = LICENSE_TIERS_ED25519.find(t => t.value === tier);
  return tierInfo?.label || tier;
}

export function getTierPrice(tier: string): number {
  const tierInfo = LICENSE_TIERS_ED25519.find(t => t.value === tier);
  return tierInfo?.price || 0;
}

export function getTierFeatures(tier: string): string[] {
  const tierInfo = LICENSE_TIERS_ED25519.find(t => t.value === tier);
  return tierInfo?.features || [];
}

export function getTierColor(tier: string): string {
  const tierInfo = LICENSE_TIERS_ED25519.find(t => t.value === tier);
  return tierInfo?.color || 'gray';
}

export function canAccessVertical(status: LicenseStatusEd25519 | null, vertical: string): boolean {
  if (!status || !status.is_valid) return false;
  if (status.tier === 'enterprise') return true;
  return status.enabled_verticals.includes(vertical);
}

export function canAccessFeature(status: LicenseStatusEd25519 | null, feature: keyof LicenseFeatures): boolean {
  if (!status || !status.is_valid) return false;
  return status.features[feature] || false;
}

export function formatLicenseKey(key: string): string {
  // Format as XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
  const cleaned = key.replace(/[^A-Za-z0-9+/=]/g, '');
  if (cleaned.length <= 24) return cleaned;
  return cleaned.substring(0, 24) + '...';
}

export function getLicenseExpiryMessage(status: LicenseStatusEd25519): string | null {
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

export function isTrialExpiringSoon(status: LicenseStatusEd25519): boolean {
  return status.tier === 'trial' && (status.days_remaining || 0) <= 7;
}

export function isHardwareMismatch(status: LicenseStatusEd25519): boolean {
  return status.validation_code === 'HARDWARE_MISMATCH';
}
