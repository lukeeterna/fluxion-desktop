// ─── License Authentication Middleware ──────────────────────────────
// Extracts and verifies Ed25519 signed license from Authorization header.
// Caches verification result in KV (24h TTL) to avoid crypto on every request.

import type { Context, Next } from 'hono';
import type { AppEnv, SignedLicense, LicenseCacheEntry } from '../lib/types';
import { verifyEd25519 } from '../lib/ed25519';

const CACHE_TTL_SECONDS = 86400; // 24 hours

/**
 * Auth middleware: verifies license from Bearer token.
 * Sets `c.set('license', ...)` and `c.set('cacheEntry', ...)` on success.
 */
export async function authMiddleware(c: Context<AppEnv>, next: Next) {
  const authHeader = c.req.header('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Missing Authorization header', code: 'AUTH_MISSING' }, 401);
  }

  const token = authHeader.slice(7);

  // Decode the signed license JSON from base64
  let signedLicense: SignedLicense;
  try {
    const decoded = atob(token);
    signedLicense = JSON.parse(decoded) as SignedLicense;
  } catch {
    return c.json({ error: 'Invalid license token', code: 'AUTH_INVALID' }, 401);
  }

  const { license, signature } = signedLicense;

  if (!license?.license_id || !signature) {
    return c.json({ error: 'Malformed license data', code: 'AUTH_MALFORMED' }, 401);
  }

  // Check revocation list first
  const revoked = await c.env.LICENSE_CACHE.get(`revoked:${license.license_id}`);
  if (revoked) {
    return c.json({ error: 'License revoked', code: 'LICENSE_REVOKED' }, 403);
  }

  // Check KV cache for previously verified license
  const cacheKey = `lic:${license.license_id}`;
  const cachedStr = await c.env.LICENSE_CACHE.get(cacheKey);
  let cacheEntry: LicenseCacheEntry | null = null;

  if (cachedStr) {
    cacheEntry = JSON.parse(cachedStr) as LicenseCacheEntry;

    // Verify fingerprint matches (prevents stolen license reuse)
    if (cacheEntry.hardware_fingerprint !== license.hardware_fingerprint) {
      return c.json({
        error: 'Hardware fingerprint mismatch',
        code: 'HARDWARE_MISMATCH',
      }, 403);
    }
  } else {
    // Not cached — full Ed25519 verification
    const licenseJson = JSON.stringify(signedLicense.license);
    const messageBytes = new TextEncoder().encode(licenseJson);

    const isValid = await verifyEd25519(
      c.env.ED25519_PUBLIC_KEY,
      signature,
      messageBytes,
    );

    if (!isValid) {
      return c.json({ error: 'Invalid signature', code: 'AUTH_SIGNATURE_INVALID' }, 401);
    }

    // Check expiration (for non-lifetime licenses)
    if (license.expires_at) {
      const expiresAt = new Date(license.expires_at);
      if (expiresAt < new Date()) {
        return c.json({ error: 'License expired', code: 'LICENSE_EXPIRED' }, 403);
      }
    }

    // Create cache entry
    const now = new Date().toISOString();
    cacheEntry = {
      license_id: license.license_id,
      tier: license.tier,
      hardware_fingerprint: license.hardware_fingerprint,
      verified_at: now,
      trial_started_at: null,
      nlu_calls_today: 0,
      nlu_calls_date: new Date().toISOString().slice(0, 10),
      last_phone_home: now,
    };

    // Save to KV with 24h TTL
    await c.env.LICENSE_CACHE.put(cacheKey, JSON.stringify(cacheEntry), {
      expirationTtl: CACHE_TTL_SECONDS,
    });
  }

  // Set context for downstream handlers
  c.set('license', license);
  c.set('cacheEntry', cacheEntry);
  c.set('cacheKey', cacheKey);

  await next();
}
