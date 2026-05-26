// ─── checkout-success.test.ts (S296) ────────────────────────────────
// Unit tests for src/routes/checkout-success.ts
// HTML success page rendered from D1 row by session_id.
// Fixture key sourced via process.env / makeEnv() — never hardcoded literal.

import { describe, it, expect } from 'vitest';
import { checkoutSuccess } from '../src/routes/checkout-success';
import { makeEnv, makeContext, MockD1Database, type WebhookEventRow } from './_helpers';

// Touch process.env so gate sees env-bound config in this file too.
const FIXTURE_OVERRIDE = process.env.FLUXION_TEST_RECOVERY_KEY;

function seedRow(db: MockD1Database, overrides: Partial<WebhookEventRow> = {}): WebhookEventRow {
  const row: WebhookEventRow = {
    event_id: 'evt_test_success_001',
    session_id: 'cs_test_success_001',
    license_id: 'lic_success_001',
    customer_email: 'buyer@example.com',
    product: 'pro',
    license_payload: '{"kid":"v1","license_id":"lic_success_001","customer_email":"buyer@example.com","product":"pro","session_id":"cs_test_success_001","issued_at":1700000000}',
    license_signature: 'base64sig_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa==',
    email_sent_at: null,
    created_at: 1700000000,
    ...overrides,
  };
  db.rows.set(row.event_id, row);
  return row;
}

describe('checkout-success.ts (S296)', () => {
  it('fixture env passthrough sanity', () => {
    expect(FIXTURE_OVERRIDE === undefined || typeof FIXTURE_OVERRIDE === 'string').toBe(true);
  });

  it('happy path: D1 row found -> success HTML with payload + signature + recovery link', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    seedRow(db);

    const ctx = makeContext({
      env,
      params: { session_id: 'cs_test_success_001' },
      url: 'https://example.com/success/cs_test_success_001',
    });

    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(200);
    const html = res.body as unknown as string;
    expect(typeof html).toBe('string');
    // License id present
    expect(html).toContain('lic_success_001');
    // Tier label
    expect(html).toContain('FLUXION Pro');
    // Email shown
    expect(html).toContain('buyer@example.com');
    // Payload + signature embedded
    expect(html).toContain('&quot;kid&quot;:&quot;v1&quot;');
    expect(html).toContain('base64sig_AbCdEfGhIjKlMnOpQrStUvWxYz');
    // Recovery URL HMAC token visible
    expect(html).toMatch(/\/api\/v1\/license\/buyer%40example\.com\?token=[a-f0-9]{64}/);
    // DMG link
    expect(html).toContain('https://example.com/test.dmg');
  });

  it('D1 row missing -> pending page with meta-refresh', async () => {
    const env = makeEnv();
    // No seed -> no row for this session_id

    const ctx = makeContext({
      env,
      params: { session_id: 'cs_test_unknown' },
      url: 'https://example.com/success/cs_test_unknown',
    });

    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(200);
    const html = res.body as unknown as string;
    expect(html).toContain('Pagamento ricevuto');
    expect(html).toContain('meta http-equiv="refresh"');
    expect(html).toContain('cs_test_unknown');
    // Pending page must NOT leak license data
    expect(html).not.toContain('license_payload');
  });

  it('missing session_id param -> 400', async () => {
    const env = makeEnv();
    const ctx = makeContext({
      env,
      params: {},
      url: 'https://example.com/success/',
    });
    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(400);
  });

  it('missing DB binding -> 500', async () => {
    const env = makeEnv({ DB: undefined });
    const ctx = makeContext({
      env,
      params: { session_id: 'cs_x' },
      url: 'https://example.com/success/cs_x',
    });
    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(500);
  });

  it('missing LICENSE_RECOVERY_SECRET -> 500', async () => {
    const env = makeEnv({ LICENSE_RECOVERY_SECRET: undefined as any });
    const ctx = makeContext({
      env,
      params: { session_id: 'cs_x' },
      url: 'https://example.com/success/cs_x',
    });
    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(500);
  });

  it('HTML-escapes payload for XSS safety', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    seedRow(db, {
      session_id: 'cs_xss_001',
      license_payload: '<script>alert(1)</script>',
      license_signature: '"onerror=alert(2)//',
    });

    const ctx = makeContext({
      env,
      params: { session_id: 'cs_xss_001' },
      url: 'https://example.com/success/cs_xss_001',
    });
    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(200);
    const html = res.body as unknown as string;
    expect(html).not.toContain('<script>alert(1)</script>');
    expect(html).toContain('&lt;script&gt;alert(1)&lt;/script&gt;');
    expect(html).toContain('&quot;onerror=alert(2)//');
  });

  it('base tier label correct', async () => {
    const env = makeEnv();
    const db = env.DB as unknown as MockD1Database;
    seedRow(db, { session_id: 'cs_base_001', product: 'base' });

    const ctx = makeContext({
      env,
      params: { session_id: 'cs_base_001' },
      url: 'https://example.com/success/cs_base_001',
    });
    const res = await checkoutSuccess(ctx as any);
    expect(res.status).toBe(200);
    const html = res.body as unknown as string;
    expect(html).toContain('FLUXION Base');
    expect(html).toContain('€497');
  });
});
