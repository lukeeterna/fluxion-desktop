// ─── License Validate — heartbeat revocation check (R-01-ter, Task 3b) ─
// POST /api/v1/license/validate
// Body: { license_id?: string, email?: string }
//
// Logic:
//   read KV purchase:{email} → { status, server_time }
//   - record.refunded === true        → "revoked"
//   - record present, not refunded     → "valid"
//   - record MISSING                   → "valid"  (FAIL-OPEN, see below)
//   - record corrupt (parse error)     → "valid"  (FAIL-OPEN, see below)
//
// DESIGN DECISION — FAIL-OPEN on missing/corrupt KV:
//   We NEVER brick a paying customer because of a flaky or absent KV record.
//   CF KV is eventually-consistent and a record can be momentarily missing.
//   Only an EXPLICIT refunded:true flag (written by stripe-webhook refund path
//   or refund.ts) produces "revoked". Absence of evidence is treated as valid.
//
// server_time is SIGNED with the SAME HMAC primitive + secret used by
// license-recovery.ts (LICENSE_RECOVERY_SECRET, HMAC-SHA256). The client can
// verify server_time integrity to defend its offline clock-rollback guard.

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

interface ValidateRequest {
  license_id?: string;
  email?: string;
}

interface PurchaseRecord {
  refunded?: boolean;
  refunded_at?: string | null;
}

// ─── server_time signing (reuse HMAC primitive from license-recovery.ts) ─

async function signServerTime(secret: string, serverTime: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(serverTime));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export async function licenseValidate(c: Context<AppEnv>): Promise<Response> {
  c.header('Cache-Control', 'no-store');

  let body: ValidateRequest;
  try {
    body = await c.req.json<ValidateRequest>();
  } catch {
    return c.json({ error: 'Body JSON non valido', code: 'INVALID_BODY' }, 400);
  }

  const email = body.email?.toLowerCase().trim() ?? null;
  if (!email || !email.includes('@') || email.length > 254) {
    return c.json({ error: 'Email mancante o non valida', code: 'INVALID_EMAIL' }, 400);
  }

  const serverTime = new Date().toISOString();

  // Sign server_time (fail-soft: if secret missing, return unsigned but log).
  let serverTimeSig: string | null = null;
  if (c.env.LICENSE_RECOVERY_SECRET) {
    serverTimeSig = await signServerTime(c.env.LICENSE_RECOVERY_SECRET, serverTime);
  } else {
    console.warn('license-validate: LICENSE_RECOVERY_SECRET not set — server_time unsigned');
  }

  // Read KV refund gate. FAIL-OPEN on miss/corrupt — never brick paying customers.
  let status: 'valid' | 'revoked' = 'valid';
  let refundedAt: string | null = null;
  const raw = await c.env.LICENSE_CACHE.get(`purchase:${email}`);
  if (raw) {
    try {
      const record = JSON.parse(raw) as PurchaseRecord;
      if (record.refunded === true) {
        status = 'revoked';
        refundedAt = record.refunded_at ?? null;
      }
    } catch {
      // Corrupt record → FAIL-OPEN (stay valid). Refund path writes valid JSON;
      // a parse failure here is treated as "no evidence of refund".
      console.error(`license-validate: corrupt purchase KV for ${email} — fail-open valid`);
    }
  }
  // raw === null → record missing → FAIL-OPEN (stay valid).

  return c.json({
    status,
    server_time: serverTime,
    server_time_sig: serverTimeSig,
    refunded_at: refundedAt,
  });
}
