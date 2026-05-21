// ─── refund.test.ts ─────────────────────────────────────────────────
// Unit tests for src/routes/refund.ts.
// Coverage:
//   - happy path: valid purchase within window → Stripe call → KV marked refunded
//   - already refunded → 409 (no duplicate Stripe call)
//   - outside 30-day window → 410 (no Stripe call)

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { refund } from '../src/routes/refund';
import {
  makeEnv,
  makeContext,
  mockFetch,
  MockKVNamespace,
} from './_helpers';

const TEN_CHARS_REASON = 'Non funziona come pensavo, restituisco grazie.';

describe('refund.ts', () => {
  let restoreFetch: (() => void) | null = null;
  let stripeCalls = 0;

  beforeEach(() => {
    stripeCalls = 0;
    restoreFetch = mockFetch(async (input) => {
      const url = typeof input === 'string' ? input : input.url;
      if (url.includes('api.stripe.com/v1/refunds')) {
        stripeCalls++;
        return new Response(
          JSON.stringify({
            id: 're_test_refund_001',
            object: 'refund',
            amount: 49700,
            currency: 'eur',
            status: 'succeeded',
            payment_intent: 'pi_test_001',
            created: Math.floor(Date.now() / 1000),
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.includes('api.resend.com')) {
        return new Response(JSON.stringify({ id: 're_email_id' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('unexpected fetch', { status: 500 });
    });
  });

  afterEach(() => {
    if (restoreFetch) restoreFetch();
    restoreFetch = null;
  });

  it('happy path: refund succeeds, KV marked refunded, audit log written', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    // Seed purchase within window
    kv.setJson('purchase:buyer@example.com', {
      checkout_session_id: 'cs_test_001',
      customer_email: 'buyer@example.com',
      tier: 'base',
      amount_total: 49700,
      currency: 'eur',
      payment_intent: 'pi_test_001',
      created_at: new Date(Date.now() - 5 * 86400000).toISOString(), // 5 days ago
      email_sent: true,
      refunded: false,
    });

    const ctx = makeContext({
      env,
      jsonBody: { email: 'buyer@example.com', reason: TEN_CHARS_REASON },
    });

    const res = await refund(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).ok).toBe(true);
    expect((res.body as any).refunded).toBe(true);
    expect((res.body as any).stripe_refund_id).toBe('re_test_refund_001');
    expect(stripeCalls).toBe(1);

    // KV purchase marked refunded
    const updated = kv.getJson<any>('purchase:buyer@example.com');
    expect(updated.refunded).toBe(true);
    expect(typeof updated.refunded_at).toBe('string');
    expect(updated.refund_reason).toBe(TEN_CHARS_REASON);

    // Audit log written
    const audit = kv.getJson<any>('refund:buyer@example.com');
    expect(audit).not.toBeNull();
    expect(audit.stripe_refund_id).toBe('re_test_refund_001');
    expect(audit.tier).toBe('base');
  });

  it('already refunded: returns 409 without calling Stripe again', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    // Seed purchase ALREADY refunded
    kv.setJson('purchase:buyer@example.com', {
      checkout_session_id: 'cs_test_002',
      customer_email: 'buyer@example.com',
      tier: 'base',
      amount_total: 49700,
      currency: 'eur',
      payment_intent: 'pi_test_002',
      created_at: new Date(Date.now() - 3 * 86400000).toISOString(),
      email_sent: true,
      refunded: true,
      refunded_at: '2026-05-15T12:00:00.000Z',
      refund_reason: 'gia rimborsato prima sessione',
    });

    const ctx = makeContext({
      env,
      jsonBody: { email: 'buyer@example.com', reason: TEN_CHARS_REASON },
    });

    const res = await refund(ctx as any);

    expect(res.status).toBe(409);
    expect((res.body as any).ok).toBe(false);
    expect((res.body as any).code).toBe('ALREADY_REFUNDED');
    expect((res.body as any).refunded_at).toBe('2026-05-15T12:00:00.000Z');
    // CRITICAL: no second Stripe call
    expect(stripeCalls).toBe(0);
  });

  it('outside 30-day window: returns 410 without calling Stripe', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    // Seed purchase 45 days old (outside default 30-day window)
    kv.setJson('purchase:buyer@example.com', {
      checkout_session_id: 'cs_test_003',
      customer_email: 'buyer@example.com',
      tier: 'pro',
      amount_total: 89700,
      currency: 'eur',
      payment_intent: 'pi_test_003',
      created_at: new Date(Date.now() - 45 * 86400000).toISOString(),
      email_sent: true,
      refunded: false,
    });

    const ctx = makeContext({
      env,
      jsonBody: { email: 'buyer@example.com', reason: TEN_CHARS_REASON },
    });

    const res = await refund(ctx as any);

    expect(res.status).toBe(410);
    expect((res.body as any).ok).toBe(false);
    expect((res.body as any).code).toBe('REFUND_WINDOW_EXPIRED');
    expect((res.body as any).days_since_purchase).toBeGreaterThanOrEqual(45);
    expect(stripeCalls).toBe(0);

    // KV NOT updated (refunded remains false)
    const purchase = kv.getJson<any>('purchase:buyer@example.com');
    expect(purchase.refunded).toBe(false);
  });
});
