// ─── /api/v1/verify — Ed25519 signature verification endpoint ──────
// S291 debug endpoint for interop testing (Worker sign ↔ ed25519-dalek verify).
// NOT used in production client flow — Tauri verifies locally via ed25519-dalek.
//
// Request:  { payload: string, signature_base64: string, kid?: string }
// Response: { kid: string, valid: boolean }
//
// Public endpoint (no auth) — accepts user-supplied payload, only returns boolean.
// No timing-safe constraints needed (Ed25519 verify constant-time by design).

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';
import { verifyEd25519Standard } from '../lib/ed25519-sign';

interface VerifyRequest {
  payload: string;
  signature_base64: string;
  kid?: string;
}

export async function verifySignature(c: Context<AppEnv>) {
  let body: VerifyRequest;
  try {
    body = await c.req.json<VerifyRequest>();
  } catch {
    return c.json({ error: 'Invalid JSON body' }, 400);
  }

  if (typeof body.payload !== 'string' || typeof body.signature_base64 !== 'string') {
    return c.json({ error: 'payload and signature_base64 required (strings)' }, 400);
  }

  const kid = body.kid ?? 'v1';
  if (kid !== 'v1') {
    return c.json({ kid, valid: false, error: 'unknown_kid' }, 400);
  }

  const publicKeyHex = c.env.ED25519_PUBLIC_KEY_V1;
  if (!publicKeyHex) {
    return c.json({ error: 'ED25519_PUBLIC_KEY_V1 not configured' }, 500);
  }

  const valid = await verifyEd25519Standard(publicKeyHex, body.signature_base64, body.payload);
  return c.json({ kid, valid });
}
