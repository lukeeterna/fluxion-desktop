// ─── Stripe Webhook Handler ─────────────────────────────────────────
// Handles checkout.session.completed events from Stripe.
// Verifies webhook signature (HMAC-SHA256), extracts tier + email,
// generates pending license data, and sends confirmation email via Resend.

import type { Context } from 'hono';
import type { AppEnv, Env } from '../lib/types';

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

// ─── Tier Display Labels ────────────────────────────────────────────

const TIER_LABELS: Record<FluxionTier, string> = {
  base: 'Base',
  pro: 'Pro',
};

// ─── Confirmation Email via Resend ──────────────────────────────────

interface SendEmailParams {
  env: Env;
  customerEmail: string;
  tier: FluxionTier;
  sessionId: string;
}

function buildEmailHtml(tier: FluxionTier): string {
  const tierLabel = TIER_LABELS[tier];
  const downloadUrl = 'https://github.com/nicchiagroup/fluxion/releases/latest';
  const installGuideUrl = 'https://fluxion-landing.pages.dev/installa';

  return `
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f0f0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;">
        <!-- Header -->
        <tr><td style="padding:40px 40px 20px;text-align:center;">
          <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">FLUXION</h1>
          <p style="margin:8px 0 0;color:#888;font-size:14px;">Gestionale per PMI italiane</p>
        </td></tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>

        <!-- Body -->
        <tr><td style="padding:30px 40px;">
          <p style="color:#e0e0e0;font-size:16px;line-height:1.6;margin:0 0 20px;">
            Ciao,
          </p>
          <p style="color:#e0e0e0;font-size:16px;line-height:1.6;margin:0 0 24px;">
            Grazie per aver acquistato <strong style="color:#ffffff;">FLUXION ${tierLabel}</strong>!
            Il tuo ordine è stato confermato con successo.
          </p>

          <!-- Download Section -->
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 24px;">
            <tr><td style="padding:20px 24px;">
              <p style="color:#ffffff;font-size:15px;font-weight:600;margin:0 0 12px;">Scarica FLUXION:</p>
              <p style="margin:0 0 8px;">
                <span style="color:#888;">macOS:</span>
                <a href="${downloadUrl}" style="color:#4a9eff;text-decoration:none;"> Scarica da GitHub Releases</a>
              </p>
              <p style="margin:0;">
                <span style="color:#888;">Windows:</span>
                <span style="color:#666;"> In arrivo prossimamente</span>
              </p>
            </td></tr>
          </table>

          <!-- Install Guide -->
          <p style="color:#e0e0e0;font-size:15px;line-height:1.6;margin:0 0 24px;">
            <strong style="color:#ffffff;">Guida installazione:</strong><br>
            <a href="${installGuideUrl}" style="color:#4a9eff;text-decoration:none;">${installGuideUrl}</a>
          </p>

          <p style="color:#e0e0e0;font-size:15px;line-height:1.6;margin:0 0 24px;">
            La tua licenza verrà attivata automaticamente al primo avvio.
          </p>

          <p style="color:#888;font-size:14px;line-height:1.6;margin:0;">
            Hai bisogno di aiuto? Rispondi a questa email.
          </p>
        </td></tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>

        <!-- Footer -->
        <tr><td style="padding:20px 40px 30px;text-align:center;">
          <p style="color:#555;font-size:13px;margin:0;">— Il team FLUXION</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`.trim();
}

async function sendConfirmationEmail(params: SendEmailParams): Promise<boolean> {
  const { env, customerEmail, tier, sessionId } = params;

  if (!env.RESEND_API_KEY) {
    console.warn(`Checkout ${sessionId}: RESEND_API_KEY not set, skipping email to ${customerEmail}`);
    return false;
  }

  const emailPayload = {
    from: 'FLUXION <noreply@fluxion-landing.pages.dev>',
    to: [customerEmail],
    subject: 'FLUXION — Il tuo ordine è confermato!',
    html: buildEmailHtml(tier),
  };

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(emailPayload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(
        `Checkout ${sessionId}: Resend email failed (${response.status}): ${errorBody}`,
      );
      return false;
    }

    const result = await response.json() as { id: string };
    console.log(
      `Checkout ${sessionId}: Confirmation email sent to ${customerEmail} (Resend ID: ${result.id})`,
    );
    return true;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Checkout ${sessionId}: Email send error: ${message}`);
    return false;
  }
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

  // ── Send Confirmation Email (non-blocking, never fails the webhook) ──
  let emailSent = false;
  try {
    emailSent = await sendConfirmationEmail({
      env: c.env,
      customerEmail,
      tier,
      sessionId: session.id,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Checkout ${session.id}: Unexpected email error: ${message}`);
  }

  // Update KV with email status
  if (emailSent) {
    licenseData.email_sent = true;
    await c.env.LICENSE_CACHE.put(kvKey, JSON.stringify(licenseData), {
      expirationTtl: 86400 * 30,
    });
  }

  return c.json({
    received: true,
    tier,
    email: customerEmail,
    license_pending: true,
    email_sent: emailSent,
  });
}
