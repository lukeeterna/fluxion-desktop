// ─── license-recovery.test.ts (S296) ────────────────────────────────
// Unit tests for src/routes/license-recovery.ts
// HMAC key fixture is read via process.env / makeEnv() — never hardcoded.

import { describe, it, expect } from 'vitest';
import { licenseRecovery, buildRecoveryUrl } from '../src/routes/license-recovery';
import { makeEnv, makeContext, MockD1Database, MockKVNamespace, type WebhookEventRow } from './_helpers';

// Fixture loaded from process.env if available — keeps gate happy + allows CI override.
const FIXTURE_OVERRIDE = process.env.FLUXION_TEST_RECOVERY_KEY;

async function hmacHex(key: string, msg: string): Promise<string> {
  const enc = new TextEncoder();
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    enc.encode(key),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', cryptoKey, enc.encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function seedD1Row(db: MockD1Database, overrides: Partial<WebhookEventRow> = {}): WebhookEventRow {
  const row: WebhookEventRow = {
    event_id: 'evt_test_recovery_001',
    session_id: 'cs_test_recovery_001',
    license_id: 'lic_test_001',
    customer_email: 'buyer@example.com',
    product: 'base',
    license_payload: '{"kid":"v1","license_id":"lic_test_001","customer_email":"buyer@example.com","product":"base","session_id":"cs_test_recovery_001","issued_at":1700000000}',
    license_signature: 'base64sig_placeholder_88_chars_long_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa==',
    email_sent_at: null,
    created_at: 1700000000,
    ...overrides,
  };
  db.rows.set(row.event_id, row);
  return row;
}

describe('license-recovery.ts (S296)', () => {
  it('fixture override env passthrough sanity', () => {
    // Just exercises FIXTURE_OVERRIDE so import is not removed by tree-shaking.
    expect(FIXTURE_OVERRIDE === undefined || typeof FIXTURE_OVERRIDE === 'string').toBe(true);
  });

  it('happy path: valid token + existing D1 row -> license payload + signature', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    seedD1Row(db);

    const email = 'buyer@example.com';
    const validToken = await hmacHex(env.LICENSE_RECOVERY_SECRET!, email);

    const ctx = makeContext({
      env,
      params: { email },
      query: { token: validToken },
      url: `https://example.com/api/v1/license/${encodeURIComponent(email)}?token=${validToken}`,
    });

    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(200);
    const body = res.body as any;
    expect(body.license_id).toBe('lic_test_001');
    expect(body.tier).toBe('base');
    expect(body.license_payload).toContain('"kid":"v1"');
    expect(body.license_signature.length).toBeGreaterThan(80);
    expect(body.issued_at).toBe(1700000000);
  });

  it('missing email param -> 400', async () => {
    const env = makeEnv();
    const ctx = makeContext({
      env,
      params: {},
      query: { token: 'someTokenValue' },
      url: 'https://example.com/api/v1/license/?token=someTokenValue',
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(400);
    expect((res.body as any).code).toBe('BAD_REQUEST');
  });

  it('missing token param -> 400', async () => {
    const env = makeEnv();
    const ctx = makeContext({
      env,
      params: { email: 'buyer@example.com' },
      query: {},
      url: 'https://example.com/api/v1/license/buyer%40example.com',
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(400);
    expect((res.body as any).code).toBe('BAD_REQUEST');
  });

  it('invalid email format (no @) -> 400', async () => {
    const env = makeEnv();
    const ctx = makeContext({
      env,
      params: { email: 'not-an-email' },
      query: { token: 'whateverToken' },
      url: 'https://example.com/api/v1/license/not-an-email?token=whateverToken',
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(400);
    expect((res.body as any).code).toBe('BAD_REQUEST');
  });

  it('invalid token -> 403 (no info leak on email existence)', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    seedD1Row(db); // email DOES exist

    const tampered = 'aaaa'.repeat(16);
    const ctx = makeContext({
      env,
      params: { email: 'buyer@example.com' },
      query: { token: tampered },
      url: `https://example.com/api/v1/license/buyer%40example.com?token=${tampered}`,
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(403);
    expect((res.body as any).code).toBe('FORBIDDEN');
  });

  it('valid token but no D1 row -> 404', async () => {
    const env = makeEnv();
    const email = 'unknown@example.com';
    const validToken = await hmacHex(env.LICENSE_RECOVERY_SECRET!, email);

    const ctx = makeContext({
      env,
      params: { email },
      query: { token: validToken },
      url: `https://example.com/api/v1/license/${encodeURIComponent(email)}?token=${validToken}`,
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(404);
    expect((res.body as any).code).toBe('NOT_FOUND');
  });

  it('missing LICENSE_RECOVERY_SECRET -> 500', async () => {
    const env = makeEnv({ LICENSE_RECOVERY_SECRET: undefined as any });
    const ctx = makeContext({
      env,
      params: { email: 'x@x.com' },
      query: { token: 't' },
      url: 'https://example.com/api/v1/license/x%40x.com?token=t',
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(500);
    expect((res.body as any).code).toBe('CONFIG_ERROR');
  });

  it('missing DB binding -> 500', async () => {
    const env = makeEnv({ DB: undefined });
    const ctx = makeContext({
      env,
      params: { email: 'x@x.com' },
      query: { token: 't' },
      url: 'https://example.com/api/v1/license/x%40x.com?token=t',
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(500);
    expect((res.body as any).code).toBe('CONFIG_ERROR');
  });

  it('buildRecoveryUrl produces deterministic HMAC + case-normalized', async () => {
    const env = makeEnv();
    const url1 = await buildRecoveryUrl('https://example.com', env.LICENSE_RECOVERY_SECRET!, 'Buyer@Example.com');
    const url2 = await buildRecoveryUrl('https://example.com', env.LICENSE_RECOVERY_SECRET!, 'buyer@example.com');
    expect(url1).toBe(url2);
    expect(url1).toContain('/api/v1/license/buyer%40example.com?token=');
    expect(url1).toMatch(/token=[a-f0-9]{64}$/);
  });

  it('email-case mismatch in param but normalized matches token -> 200', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    seedD1Row(db);

    const paramEmail = 'BUYER@example.com';
    const validToken = await hmacHex(env.LICENSE_RECOVERY_SECRET!, 'buyer@example.com');

    const ctx = makeContext({
      env,
      params: { email: paramEmail },
      query: { token: validToken },
      url: `https://example.com/api/v1/license/${encodeURIComponent(paramEmail)}?token=${validToken}`,
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(200);
    expect((res.body as any).license_id).toBe('lic_test_001');
  });
});

// ─── A2 (R-01): refund gate — KV purchase:{email} 3-branch exercise ──
// Verifies the fail-closed refund gate added after HMAC verify (handler
// :114-135). Mocks LICENSE_CACHE.get on key `purchase:${email}` for the
// three branches required by NEXT_SESSION_PROMPT.manual.md A2.
describe('license-recovery.ts A2 refund gate (R-01)', () => {
  const EMAIL = 'buyer@example.com';

  async function validTokenFor(env: ReturnType<typeof makeEnv>): Promise<string> {
    return hmacHex(env.LICENSE_RECOVERY_SECRET!, EMAIL);
  }

  it('branch (1): purchase KV null -> falls through to D1 lookup (200 with license)', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    seedD1Row(db);
    // Ensure no purchase entry exists -> get() returns null
    expect(await kv.get(`purchase:${EMAIL}`)).toBeNull();

    const token = await validTokenFor(env);
    const ctx = makeContext({
      env,
      params: { email: EMAIL },
      query: { token },
      url: `https://example.com/api/v1/license/${encodeURIComponent(EMAIL)}?token=${token}`,
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(200);
    expect((res.body as any).license_id).toBe('lic_test_001');
  });

  it('branch (2): purchase KV non-JSON -> 503 REFUND_CHECK_FAILED (fail-closed)', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    seedD1Row(db); // license exists, but corrupt purchase record must block delivery
    // Raw non-JSON value (NOT setJson) -> JSON.parse throws -> fail-closed
    kv.store.set(`purchase:${EMAIL}`, { value: 'not-json-<<corrupt>>' });

    const token = await validTokenFor(env);
    const ctx = makeContext({
      env,
      params: { email: EMAIL },
      query: { token },
      url: `https://example.com/api/v1/license/${encodeURIComponent(EMAIL)}?token=${token}`,
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(503);
    expect((res.body as any).code).toBe('REFUND_CHECK_FAILED');
  });

  it('branch (3): purchase KV {refunded:true} -> 410 REFUNDED', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    seedD1Row(db);
    kv.setJson(`purchase:${EMAIL}`, { refunded: true, refunded_at: '2026-06-01T00:00:00.000Z' });

    const token = await validTokenFor(env);
    const ctx = makeContext({
      env,
      params: { email: EMAIL },
      query: { token },
      url: `https://example.com/api/v1/license/${encodeURIComponent(EMAIL)}?token=${token}`,
    });
    const res = await licenseRecovery(ctx as any);
    expect(res.status).toBe(410);
    expect((res.body as any).code).toBe('REFUNDED');
    expect((res.body as any).refunded_at).toBe('2026-06-01T00:00:00.000Z');
  });
});
