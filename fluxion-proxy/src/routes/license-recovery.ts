// ─── License Recovery — Permanent shareable URL endpoint ────────────
// S295: GET /api/v1/license/:email?token={hmac}
//
// Purpose:
//   Eliminate email as single point of failure for license delivery.
//   Customer stores permanent recovery link (shown on success page +
//   sent via backup email). HMAC token prevents enumeration attack.
//
// Token derivation (deterministic, permanent):
//   token = HMAC-SHA256(LICENSE_RECOVERY_SECRET, normalized_email)
//   normalized_email = email.toLowerCase().trim()
//
// Response: JSON {license_payload, license_signature, license_id, tier}
//   - license_payload: canonical JSON string (input to verify_license_signature_v1)
//   - license_signature: base64-encoded Ed25519 signature
//   - source of truth: D1 webhook_events row (most recent by created_at desc)
//
// Security:
//   - Referrer-Policy: no-referrer (avoid token leak via 3rd-party referrer)
//   - Cache-Control: no-store (token in URL, never cache HTTP layer)
//   - No body params, no PII echo beyond what customer already knows (email = URL param)

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

interface WebhookEventLookup {
  license_id: string;
  customer_email: string;
  product: string;
  license_payload: string;
  license_signature: string;
  created_at: number;
}

// ─── HMAC token helpers ─────────────────────────────────────────────

async function computeRecoveryToken(secret: string, email: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(email.toLowerCase().trim()));
  return [...new Uint8Array(sig)]
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

// ─── Public helper (exported for use by success page + email body) ──

export async function buildRecoveryUrl(
  baseUrl: string,
  secret: string,
  email: string,
): Promise<string> {
  const token = await computeRecoveryToken(secret, email);
  const encoded = encodeURIComponent(email.toLowerCase().trim());
  return `${baseUrl}/api/v1/license/${encoded}?token=${token}`;
}

// ─── Route handler ──────────────────────────────────────────────────

export async function licenseRecovery(c: Context<AppEnv>) {
  // Security headers (set early — apply to all response paths)
  c.header('Referrer-Policy', 'no-referrer');
  c.header('Cache-Control', 'no-store');
  c.header('X-Content-Type-Options', 'nosniff');

  const secret = c.env.LICENSE_RECOVERY_SECRET;
  if (!secret) {
    console.error('LICENSE_RECOVERY_SECRET not configured');
    return c.json({ error: 'Recovery not configured', code: 'CONFIG_ERROR' }, 500);
  }

  if (!c.env.DB) {
    console.error('D1 binding DB missing — license recovery requires D1');
    return c.json({ error: 'Database not configured', code: 'CONFIG_ERROR' }, 500);
  }

  const emailParam = c.req.param('email');
  const tokenParam = c.req.query('token');

  if (!emailParam || !tokenParam) {
    return c.json({ error: 'Missing email or token', code: 'BAD_REQUEST' }, 400);
  }

  // Normalize email (URL decoded by Hono router param)
  const email = emailParam.toLowerCase().trim();

  // Basic email shape check (avoid enum scan with garbage)
  if (!email.includes('@') || email.length > 254) {
    return c.json({ error: 'Invalid email format', code: 'BAD_REQUEST' }, 400);
  }

  // Verify HMAC token (constant-time compare)
  const expectedToken = await computeRecoveryToken(secret, email);
  if (!constantTimeEqual(tokenParam.toLowerCase(), expectedToken)) {
    // Avoid leaking whether email exists — same 403 for bad token OR unknown email
    return c.json({ error: 'Invalid token', code: 'FORBIDDEN' }, 403);
  }

  // Refund gate — flag in KV purchase:{email} (refund.ts:358), NON in D1.
  // STESSA key/normalizzazione: refund.ts:262 `purchase:${body.email.toLowerCase().trim()}`
  // == qui `purchase:${email}` con email = emailParam.toLowerCase().trim() (:100). MATCH verificato.
  const purchaseRaw = await c.env.LICENSE_CACHE.get(`purchase:${email}`);
  if (purchaseRaw) {
    // Entry esiste → DEVE essere JSON valido (writePurchaseKv/refund.ts scrivono sempre JSON.stringify).
    // Parse-error su record reale = stato sospetto → FAIL-CLOSED: nega, mai consegnare la licenza.
    let p: { refunded?: boolean; refunded_at?: string | null };
    try {
      p = JSON.parse(purchaseRaw);
    } catch {
      console.error(`license-recovery: corrupt purchase KV for ${email} — denying (fail-closed)`);
      return c.json({ error: 'Refund check failed', code: 'REFUND_CHECK_FAILED' }, 503);
    }
    if (p.refunded === true) {
      return c.json(
        { error: 'License refunded', code: 'REFUNDED', refunded_at: p.refunded_at ?? null },
        410,
      );
    }
  }
  // purchaseRaw === null → entry mai scritta = cliente pre-flag legittimo → fall-through al lookup D1

  // D1 lookup — most recent license for this email
  const row = await c.env.DB
    .prepare(
      `SELECT license_id, customer_email, product, license_payload, license_signature, created_at
       FROM webhook_events
       WHERE customer_email = ?
       ORDER BY created_at DESC
       LIMIT 1`,
    )
    .bind(email)
    .first<WebhookEventLookup>();

  if (!row) {
    // Token valid but no purchase found → tell client (token verified = email is theirs)
    return c.json({ error: 'No license found for this email', code: 'NOT_FOUND' }, 404);
  }

  return c.json({
    license_id: row.license_id,
    tier: row.product,
    license_payload: row.license_payload,
    license_signature: row.license_signature,
    issued_at: row.created_at,
  });
}
