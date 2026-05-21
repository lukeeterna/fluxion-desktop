// ─── stripe-webhook.test.ts ─────────────────────────────────────────
// Unit tests for src/routes/stripe-webhook.ts.
// Coverage:
//   - happy path: checkout.session.completed → KV write (purchase + session)
//   - invalid signature → 400
//   - missing customer email → 200 with warning (Stripe expects 200)
//   - unknown tier (amount mismatch + no metadata.tier) → 200 with warning

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { stripeWebhook } from '../src/routes/stripe-webhook';
import {
  makeEnv,
  makeContext,
  buildStripeSignature,
  mockFetch,
  MockKVNamespace,
} from './_helpers';

describe('stripe-webhook.ts', () => {
  let restoreFetch: (() => void) | null = null;

  beforeEach(() => {
    // Default: Resend POST always succeeds — webhook handler should send email
    restoreFetch = mockFetch(async (input) => {
      const url = typeof input === 'string' ? input : input.url;
      if (url.includes('api.resend.com')) {
        return new Response(JSON.stringify({ id: 're_test_email_id' }), {
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

  it('happy path: writes purchase + session KV with refunded=false', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    const payload = JSON.stringify({
      id: 'evt_test_001',
      object: 'event',
      type: 'checkout.session.completed',
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: 'cs_test_001',
          object: 'checkout.session',
          customer_email: 'buyer@example.com',
          amount_total: 49700,
          currency: 'eur',
          payment_status: 'paid',
          payment_intent: 'pi_test_001',
          metadata: {},
        },
      },
    });

    const sigHeader = await buildStripeSignature(payload, secret);

    const ctx = makeContext({
      env,
      headers: { 'Stripe-Signature': sigHeader },
      rawBody: payload,
    });

    const res = await stripeWebhook(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).received).toBe(true);
    expect((res.body as any).tier).toBe('base');
    expect((res.body as any).email).toBe('buyer@example.com');
    expect((res.body as any).email_sent).toBe(true);

    // Purchase stored under email key
    const purchase = kv.getJson<any>('purchase:buyer@example.com');
    expect(purchase).not.toBeNull();
    expect(purchase.tier).toBe('base');
    expect(purchase.payment_intent).toBe('pi_test_001');
    expect(purchase.refunded).toBe(false);
    expect(purchase.email_sent).toBe(true);

    // Session idempotency key
    const sessionRec = kv.getJson<any>('session:cs_test_001');
    expect(sessionRec).not.toBeNull();
    expect(sessionRec.checkout_session_id).toBe('cs_test_001');
  });

  it('invalid signature → 400 reject without KV write', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    const payload = JSON.stringify({
      id: 'evt_test_002',
      type: 'checkout.session.completed',
      data: { object: { id: 'cs_test_002' } },
    });

    // Build signature with WRONG secret
    const badSig = await buildStripeSignature(payload, 'whsec_WRONG_SECRET');

    const ctx = makeContext({
      env,
      headers: { 'Stripe-Signature': badSig },
      rawBody: payload,
    });

    const res = await stripeWebhook(ctx as any);

    expect(res.status).toBe(400);
    expect((res.body as any).error).toBe('Invalid signature');
    // No purchase written
    expect(kv.store.size).toBe(0);
  });

  it('missing customer email → 200 ack with warning, no KV write', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    const payload = JSON.stringify({
      id: 'evt_test_003',
      type: 'checkout.session.completed',
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: 'cs_test_003',
          customer_email: null,
          amount_total: 49700,
          payment_intent: 'pi_test_003',
          metadata: {},
        },
      },
    });

    const sigHeader = await buildStripeSignature(payload, secret);

    const ctx = makeContext({
      env,
      headers: { 'Stripe-Signature': sigHeader },
      rawBody: payload,
    });

    const res = await stripeWebhook(ctx as any);

    expect(res.status).toBe(200); // Stripe expects 200 to avoid retry storm
    expect((res.body as any).warning).toBe('no_customer_email');
    expect(kv.store.size).toBe(0);
  });

  it('unknown tier (amount=12345 + no metadata.tier) → 200 ack with warning', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    const payload = JSON.stringify({
      id: 'evt_test_004',
      type: 'checkout.session.completed',
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: 'cs_test_004',
          customer_email: 'odd@example.com',
          amount_total: 12345, // not 49700 nor 89700
          payment_intent: 'pi_test_004',
          metadata: {},
        },
      },
    });

    const sigHeader = await buildStripeSignature(payload, secret);

    const ctx = makeContext({
      env,
      headers: { 'Stripe-Signature': sigHeader },
      rawBody: payload,
    });

    const res = await stripeWebhook(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).warning).toBe('unknown_tier');
    // No purchase written when tier is undetermined
    expect(kv.store.size).toBe(0);
  });
});
