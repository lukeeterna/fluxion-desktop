// ─── Consent Log — Art.59 lett.o D.Lgs 206/2005 Audit Trail ────────
// Public POST endpoint. Called from /checkout-consent.html before redirect to Stripe.
// Body: { plan, cb_a, cb_b, landing_v?, referer?, stripe_link? }
//
// Flow:
//   1. Validate input (plan + entrambe checkbox checked)
//   2. Capture IP + UA + timestamp
//   3. Save in KV: consent_pre:{ip_hash}:{ts_unix} TTL 10y
//      (email non ancora nota — collegamento via Stripe webhook in S176)
//   4. Return 200 con consent_id (può essere correlato post-acquisto)
//
// Compliance: art.59 lett.o richiede "accordo espresso" + "accettazione perdita
// recesso". Cassazione III 13281/2024: onere prova sul professionista.
// AGCM PS12847/2025: €35.000 sanzione per merchant senza checkbox documentata.
// Conservazione 10 anni ex art. 2946 cc + GDPR art.6(1)(c) obbligo legale.

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

interface ConsentRequest {
  plan?: 'base' | 'pro';
  cb_a?: boolean;
  cb_b?: boolean;
  landing_v?: string;
  referer?: string;
  stripe_link?: string;
}

interface ConsentRecord {
  v: 1;
  ts: string;
  ts_unix: number;
  ip: string | null;
  ua: string;
  cb_a: true; // forziamo true: salviamo solo consensi validi
  cb_b: true;
  plan: 'base' | 'pro';
  landing_v: string | null;
  referer: string | null;
  stripe_link: string | null;
  consent_id: string;
}

const TTL_TEN_YEARS_SECONDS = 315_360_000;
const UA_MAX = 512;

function getClientIp(c: Context<AppEnv>): string | null {
  return (
    c.req.header('cf-connecting-ip') ||
    c.req.header('x-forwarded-for')?.split(',')[0]?.trim() ||
    null
  );
}

async function sha256Hex(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function generateConsentId(): string {
  // 16 random bytes hex
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function consentLog(c: Context<AppEnv>) {
  let body: ConsentRequest;
  try {
    body = await c.req.json<ConsentRequest>();
  } catch {
    return c.json({ ok: false, code: 'INVALID_BODY' }, 400);
  }

  if (body.plan !== 'base' && body.plan !== 'pro') {
    return c.json({ ok: false, code: 'INVALID_PLAN' }, 400);
  }
  if (body.cb_a !== true || body.cb_b !== true) {
    return c.json({ ok: false, code: 'CONSENT_INCOMPLETE' }, 400);
  }

  const ip = getClientIp(c);
  const ua = (c.req.header('user-agent') ?? '').slice(0, UA_MAX);
  const now = new Date();
  const tsUnix = Math.floor(now.getTime() / 1000);
  const consentId = generateConsentId();

  const record: ConsentRecord = {
    v: 1,
    ts: now.toISOString(),
    ts_unix: tsUnix,
    ip,
    ua,
    cb_a: true,
    cb_b: true,
    plan: body.plan,
    landing_v: body.landing_v?.slice(0, 64) ?? null,
    referer: body.referer?.slice(0, 512) ?? null,
    stripe_link: body.stripe_link?.slice(0, 256) ?? null,
    consent_id: consentId,
  };

  // Storage: pre-purchase by ip_hash (email not yet known)
  // Stripe webhook in S176 collegherà email→consent via consent_id metadata
  const ipHash = ip ? (await sha256Hex(ip)).slice(0, 16) : 'noip';
  const key = `consent_pre:${ipHash}:${tsUnix}:${consentId}`;

  try {
    await c.env.LICENSE_CACHE.put(key, JSON.stringify(record), {
      expirationTtl: TTL_TEN_YEARS_SECONDS,
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`consent-log KV write failed: ${msg}`);
    return c.json({ ok: false, code: 'STORAGE_ERROR' }, 500);
  }

  console.log(
    `consent-log OK: plan=${body.plan} consent_id=${consentId} ip_hash=${ipHash}`,
  );

  return c.json(
    {
      ok: true,
      consent_id: consentId,
      ts: record.ts,
    },
    200,
  );
}
