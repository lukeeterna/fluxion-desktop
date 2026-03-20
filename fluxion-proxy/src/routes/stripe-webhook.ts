// ─── Stripe Webhook Handler ─────────────────────────────────────────
// Handles checkout.session.completed events from Stripe.
// Verifies webhook signature (HMAC-SHA256), extracts tier + email,
// and prepares license generation data.
//
// Future: Ed25519 license signing + Resend email delivery.

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

// ─── Stripe Event Types ─────────────────────────────────────────────

interface StripeCheckoutSession {
  id: string;
  object: 'checkout.session';
  customer_email: string | null;
  amount_total: number | null;
  currency: string | null;
  payment_status: string;
  metadata: Record<string, string>;
}

interface StripeEvent {
  id: string;
  object: 'event';
  type: string;
  data: {
    object: StripeCheckoutSession;
  };
  created: number;
}

// ─── Tier Detection ─────────────────────────────────────────────────

type FluxionTier = 'base' | 'pro';

const AMOUNT_TO_TIER: Record<number, FluxionTier> = {
  49700: 'base', // €497.00
  89700: 'pro',  // €897.00
};

function detectTier(
  amountTotal: number | null,
  metadata: Record<string, string>,
): FluxionTier | null {
  // Prefer explicit tier from metadata
  const metaTier = metadata.tier;
  if (metaTier === 'base' || metaTier === 'pro') {
    return metaTier;
  }

  // Fallback: detect from amount
  if (amountTotal !== null && amountTotal in AMOUNT_TO_TIER) {
    return AMOUNT_TO_TIER[amountTotal];
  }

  return null;
}

// ─── Stripe Signature Verification (HMAC-SHA256) ────────────────────

async function verifyStripeSignature(
  payload: string,
  signatureHeader: string,
  secret: string,
): Promise<boolean> {
  // Parse Stripe-Signature header: "t=timestamp,v1=signature"
  const parts = signatureHeader.split(',');
  let timestamp = '';
  let signature = '';

  for (const part of parts) {
    const [key, value] = part.split('=', 2);
    if (key === 't') timestamp = value;
    if (key === 'v1') signature = value;
  }

  if (!timestamp || !signature) {
    return false;
  }

  // Reject events older than 5 minutes (replay protection)
  const eventAge = Math.abs(Date.now() / 1000 - parseInt(timestamp, 10));
  if (eventAge > 300) {
    return false;
  }

  // Compute expected signature: HMAC-SHA256(secret, "timestamp.payload")
  const signedPayload = `${timestamp}.${payload}`;
  const encoder = new TextEncoder();

  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );

  const signatureBytes = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(signedPayload),
  );

  // Convert to hex for comparison
  const expectedHex = Array.from(new Uint8Array(signatureBytes))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');

  // Constant-time comparison
  if (expectedHex.length !== signature.length) {
    return false;
  }

  let mismatch = 0;
  for (let i = 0; i < expectedHex.length; i++) {
    mismatch |= expectedHex.charCodeAt(i) ^ signature.charCodeAt(i);
  }

  return mismatch === 0;
}

// ─── Webhook Handler ────────────────────────────────────────────────

export async function stripeWebhook(c: Context<AppEnv>) {
  const webhookSecret = c.env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    console.error('STRIPE_WEBHOOK_SECRET not configured');
    return c.json({ error: 'Webhook not configured' }, 500);
  }

  // Read raw body for signature verification
  const rawBody = await c.req.text();
  const signatureHeader = c.req.header('Stripe-Signature');

  if (!signatureHeader) {
    return c.json({ error: 'Missing Stripe-Signature header' }, 400);
  }

  // Verify webhook signature
  const isValid = await verifyStripeSignature(rawBody, signatureHeader, webhookSecret);

  if (!isValid) {
    console.error('Stripe webhook signature verification failed');
    return c.json({ error: 'Invalid signature' }, 400);
  }

  // Parse event
  let event: StripeEvent;
  try {
    event = JSON.parse(rawBody) as StripeEvent;
  } catch {
    return c.json({ error: 'Invalid JSON payload' }, 400);
  }

  // Handle only checkout.session.completed
  if (event.type !== 'checkout.session.completed') {
    // Acknowledge all other events — Stripe expects 200
    return c.json({ received: true, type: event.type });
  }

  const session = event.data.object;

  // Extract customer email
  const customerEmail = session.customer_email ?? session.metadata?.email ?? null;

  if (!customerEmail) {
    console.error(`Checkout ${session.id}: no customer email found`);
    return c.json({ received: true, warning: 'no_customer_email' });
  }

  // Determine tier
  const tier = detectTier(session.amount_total, session.metadata);

  if (!tier) {
    console.error(
      `Checkout ${session.id}: unknown tier for amount ${session.amount_total}`,
    );
    return c.json({ received: true, warning: 'unknown_tier' });
  }

  // ── License Generation Placeholder ──────────────────────────────
  // TODO: Ed25519 sign license + send via Resend email
  // For now, log and store in KV for manual processing

  const licenseData = {
    checkout_session_id: session.id,
    customer_email: customerEmail,
    tier,
    amount_total: session.amount_total,
    currency: session.currency,
    created_at: new Date().toISOString(),
    license_key: null as string | null, // Will be Ed25519-signed key
    email_sent: false,
  };

  // Store pending license in KV
  const kvKey = `pending-license:${session.id}`;
  await c.env.LICENSE_CACHE.put(kvKey, JSON.stringify(licenseData), {
    expirationTtl: 86400 * 30, // 30 days retention
  });

  console.log(
    `Stripe checkout completed: ${customerEmail} — tier: ${tier} — session: ${session.id}`,
  );

  return c.json({
    received: true,
    tier,
    email: customerEmail,
    license_pending: true,
  });
}
