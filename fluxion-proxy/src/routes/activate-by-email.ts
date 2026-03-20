// ─── Email-Based License Activation ─────────────────────────────────
// The customer's email IS the license key.
// App sends email → Worker checks KV for purchase → returns tier + features.
// Zero friction: no codes, no keys, no files.
//
// POST /api/v1/activate-by-email
// Body: { "email": "mario@rossi.it" }
// Response: { "activated": true, "tier": "pro", "features": {...} }

import type { Context } from 'hono';
import type { AppEnv, Env } from '../lib/types';

interface ActivationRequest {
  email: string;
}

interface PurchaseData {
  checkout_session_id: string;
  customer_email: string;
  tier: 'base' | 'pro';
  amount_total: number | null;
  currency: string | null;
  created_at: string;
  email_sent: boolean;
}

const TIER_FEATURES: Record<string, {
  sara_enabled: boolean;
  sara_trial_days: number | null;
  whatsapp_ai: boolean;
  loyalty_advanced: boolean;
  fatturazione_sdi: boolean;
  max_verticals: number;
}> = {
  base: {
    sara_enabled: true,
    sara_trial_days: 30, // 30-day Sara trial for Base
    whatsapp_ai: true,
    loyalty_advanced: false,
    fatturazione_sdi: true,
    max_verticals: 1,
  },
  pro: {
    sara_enabled: true,
    sara_trial_days: null, // Sara forever for Pro
    whatsapp_ai: true,
    loyalty_advanced: true,
    fatturazione_sdi: true,
    max_verticals: 1,
  },
};

export async function activateByEmail(c: Context<AppEnv>) {
  let body: ActivationRequest;
  try {
    body = await c.req.json<ActivationRequest>();
  } catch {
    return c.json({ error: 'Invalid JSON body', code: 'INVALID_BODY' }, 400);
  }

  const email = body.email?.toLowerCase().trim();

  if (!email || !email.includes('@')) {
    return c.json({ error: 'Email required', code: 'EMAIL_REQUIRED' }, 400);
  }

  // Look up purchase in KV
  const kvKey = `purchase:${email}`;
  const raw = await c.env.LICENSE_CACHE.get(kvKey);

  if (!raw) {
    return c.json({
      activated: false,
      error: 'Nessun acquisto trovato per questa email.',
      code: 'PURCHASE_NOT_FOUND',
      hint: 'Verifica di aver usato la stessa email del pagamento Stripe.',
    }, 404);
  }

  let purchase: PurchaseData;
  try {
    purchase = JSON.parse(raw) as PurchaseData;
  } catch {
    return c.json({ error: 'Corrupted purchase data', code: 'DATA_ERROR' }, 500);
  }

  const features = TIER_FEATURES[purchase.tier] ?? TIER_FEATURES.base;

  // Calculate Sara trial expiry for Base tier
  let sara_expires_at: string | null = null;
  if (features.sara_trial_days !== null) {
    const purchaseDate = new Date(purchase.created_at);
    const expiryDate = new Date(purchaseDate.getTime() + features.sara_trial_days * 86400000);
    sara_expires_at = expiryDate.toISOString();
  }

  // Track activation in KV
  const activationKey = `activation:${email}`;
  await c.env.LICENSE_CACHE.put(activationKey, JSON.stringify({
    email,
    tier: purchase.tier,
    activated_at: new Date().toISOString(),
    purchase_date: purchase.created_at,
  }), {
    expirationTtl: 86400 * 365 * 10,
  });

  console.log(`License activated: ${email} — tier: ${purchase.tier}`);

  return c.json({
    activated: true,
    tier: purchase.tier,
    email: purchase.customer_email,
    purchased_at: purchase.created_at,
    features: {
      ...features,
      sara_expires_at,
    },
  });
}
