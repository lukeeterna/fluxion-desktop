// ─── activate-by-email.test.ts ──────────────────────────────────────
// Unit tests for src/routes/activate-by-email.ts.
// Coverage:
//   - happy path: valid purchase → tier + features returned + activation tracked
//   - refunded block (regression): purchase.refunded=true → 410 PURCHASE_REFUNDED

import { describe, it, expect } from 'vitest';
import { activateByEmail } from '../src/routes/activate-by-email';
import { makeEnv, makeContext, MockKVNamespace } from './_helpers';

describe('activate-by-email.ts', () => {
  it('happy path: valid Pro purchase → tier+features returned, activation tracked', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    kv.setJson('purchase:buyer@example.com', {
      checkout_session_id: 'cs_test_001',
      customer_email: 'buyer@example.com',
      tier: 'pro',
      amount_total: 89700,
      currency: 'eur',
      payment_intent: 'pi_test_001',
      created_at: '2026-05-01T00:00:00.000Z',
      email_sent: true,
      refunded: false,
    });

    const ctx = makeContext({
      env,
      jsonBody: { email: 'BUYER@example.com' }, // case insensitive
    });

    const res = await activateByEmail(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).activated).toBe(true);
    expect((res.body as any).tier).toBe('pro');
    expect((res.body as any).features.sara_enabled).toBe(true);
    expect((res.body as any).features.sara_expires_at).toBeNull(); // Pro = forever

    // Activation tracked in KV under lowercased email
    const activation = kv.getJson<any>('activation:buyer@example.com');
    expect(activation).not.toBeNull();
    expect(activation.tier).toBe('pro');
  });

  it('refunded purchase: returns 410 PURCHASE_REFUNDED, no activation tracked', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    kv.setJson('purchase:refunded@example.com', {
      checkout_session_id: 'cs_test_002',
      customer_email: 'refunded@example.com',
      tier: 'base',
      amount_total: 49700,
      currency: 'eur',
      payment_intent: 'pi_test_002',
      created_at: '2026-05-01T00:00:00.000Z',
      email_sent: true,
      refunded: true,
      refunded_at: '2026-05-10T00:00:00.000Z',
      refund_reason: 'cambio idea',
    });

    const ctx = makeContext({
      env,
      jsonBody: { email: 'refunded@example.com' },
    });

    const res = await activateByEmail(ctx as any);

    expect(res.status).toBe(410);
    expect((res.body as any).activated).toBe(false);
    expect((res.body as any).code).toBe('PURCHASE_REFUNDED');
    expect((res.body as any).refunded_at).toBe('2026-05-10T00:00:00.000Z');

    // No activation tracked
    expect(kv.getJson('activation:refunded@example.com')).toBeNull();
  });
});
