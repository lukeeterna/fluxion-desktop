// ─── stripe-webhook.test.ts ─────────────────────────────────────────
// Unit tests for src/routes/stripe-webhook.ts (S291 refactor).
// Coverage:
//   - happy path: checkout.session.completed → D1 row + signed payload + KV purchase
//   - invalid signature → 400
//   - missing customer email → 200 with warning
//   - unknown tier → 200 with warning
//   - FSAF-05 replay 2x (same event_id) → D1 INSERT OR IGNORE changes=0 → no duplicate email
//   - S291 replay with email_sent_at IS NULL (Resend failed first) → re-send + UPDATE
//   - S291 verify roundtrip (signEd25519 ↔ verifyEd25519Standard) valid/tampered
//   - S291 /api/v1/verify endpoint bool response

import { describe, it, expect, beforeAll, beforeEach, afterEach } from 'vitest';
import { stripeWebhook } from '../src/routes/stripe-webhook';
import { verifySignature } from '../src/routes/verify-signature';
import {
  signEd25519,
  verifyEd25519Standard,
  computeLicenseId,
  canonicalizeLicensePayload,
  type LicensePayloadV1,
} from '../src/lib/ed25519-sign';
import {
  makeEnv,
  makeContext,
  buildStripeSignature,
  mockFetch,
  generateTestKeypair,
  MockKVNamespace,
  MockD1Database,
  type TestKeypair,
  type WebhookEventRow,
} from './_helpers';

describe('stripe-webhook.ts (S291)', () => {
  let restoreFetch: (() => void) | null = null;
  let keypair: TestKeypair;

  beforeAll(async () => {
    // Single keypair shared across tests — generate once for speed.
    keypair = await generateTestKeypair();
  });

  beforeEach(() => {
    // Default: Resend POST succeeds.
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

  function makeWebhookEnv(overrides = {}) {
    return makeEnv({
      ED25519_PRIVATE_KEY_PKCS8: keypair.privatePkcs8Base64,
      ED25519_PUBLIC_KEY_V1: keypair.publicHex,
      ...overrides,
    });
  }

  it('happy path: D1 row + signed payload + KV purchase (S291)', async () => {
    const env = makeWebhookEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;
    const db = env.DB as unknown as MockD1Database;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    const payload = JSON.stringify({
      id: 'evt_test_001',
      object: 'event',
      type: 'checkout.session.completed',
      api_version: '2026-04-22.dahlia',
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
    expect((res.body as any).tier).toBe('base');
    expect((res.body as any).email).toBe('buyer@example.com');
    expect((res.body as any).email_sent).toBe(true);
    expect((res.body as any).license_id).toMatch(/^[0-9a-f]{64}$/);
    expect((res.body as any).event_id).toBe('evt_test_001');

    // D1 row created
    const row = db.rows.get('evt_test_001');
    expect(row).toBeDefined();
    expect(row!.customer_email).toBe('buyer@example.com');
    expect(row!.product).toBe('base');
    expect(row!.email_sent_at).not.toBeNull();
    expect(row!.license_payload).toContain('"kid":"v1"');
    expect(row!.license_signature.length).toBeGreaterThan(80); // base64 of 64 bytes ≈ 88 chars

    // Signed payload verifies with keypair
    const sigValid = await verifyEd25519Standard(
      keypair.publicHex,
      row!.license_signature,
      row!.license_payload,
    );
    expect(sigValid).toBe(true);

    // KV backward-compat write
    const purchase = kv.getJson<any>('purchase:buyer@example.com');
    expect(purchase).not.toBeNull();
    expect(purchase.tier).toBe('base');
    expect(purchase.payment_intent).toBe('pi_test_001');
    expect(purchase.email_sent).toBe(true);
    expect(purchase.refunded).toBe(false);
  });

  it('invalid signature → 400 reject without D1 write', async () => {
    const env = makeWebhookEnv();
    const db = env.DB as unknown as MockD1Database;

    const payload = JSON.stringify({
      id: 'evt_test_002',
      type: 'checkout.session.completed',
      api_version: '2026-04-22.dahlia',
      created: Math.floor(Date.now() / 1000),
      data: { object: { id: 'cs_test_002', customer_email: 'x@x.com', amount_total: 49700, metadata: {} } },
    });

    const badSig = await buildStripeSignature(payload, 'whsec_WRONG_SECRET');
    const ctx = makeContext({
      env,
      headers: { 'Stripe-Signature': badSig },
      rawBody: payload,
    });

    const res = await stripeWebhook(ctx as any);

    expect(res.status).toBe(400);
    expect((res.body as any).error).toBe('Invalid signature');
    expect(db.rows.size).toBe(0);
  });

  it('missing customer email → 200 ack with warning, no D1 row', async () => {
    const env = makeWebhookEnv();
    const db = env.DB as unknown as MockD1Database;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    const payload = JSON.stringify({
      id: 'evt_test_003',
      type: 'checkout.session.completed',
      api_version: '2026-04-22.dahlia',
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

    expect(res.status).toBe(200);
    expect((res.body as any).warning).toBe('no_customer_email');
    expect(db.rows.size).toBe(0);
  });

  it('unknown tier → 200 ack with warning, no D1 row', async () => {
    const env = makeWebhookEnv();
    const db = env.DB as unknown as MockD1Database;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    const payload = JSON.stringify({
      id: 'evt_test_004',
      type: 'checkout.session.completed',
      api_version: '2026-04-22.dahlia',
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: 'cs_test_004',
          customer_email: 'odd@example.com',
          amount_total: 12345,
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
    expect(db.rows.size).toBe(0);
  });

  it('FSAF-05 (S291): replay 2x same event_id → 1 D1 row + 1 email', async () => {
    const env = makeWebhookEnv();
    const db = env.DB as unknown as MockD1Database;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    let resendCalls = 0;
    if (restoreFetch) restoreFetch();
    restoreFetch = mockFetch(async (input) => {
      const url = typeof input === 'string' ? input : input.url;
      if (url.includes('api.resend.com')) {
        resendCalls += 1;
        return new Response(JSON.stringify({ id: 're_test_email_id' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('unexpected fetch', { status: 500 });
    });

    const payload = JSON.stringify({
      id: 'evt_test_replay_005',
      object: 'event',
      type: 'checkout.session.completed',
      api_version: '2026-04-22.dahlia',
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: 'cs_test_replay_005',
          object: 'checkout.session',
          customer_email: 'replay@example.com',
          amount_total: 49700,
          currency: 'eur',
          payment_status: 'paid',
          payment_intent: 'pi_test_replay_005',
          metadata: {},
        },
      },
    });

    // First delivery
    const sig1 = await buildStripeSignature(payload, secret);
    const ctx1 = makeContext({ env, headers: { 'Stripe-Signature': sig1 }, rawBody: payload });
    const res1 = await stripeWebhook(ctx1 as any);
    expect(res1.status).toBe(200);
    expect((res1.body as any).email_sent).toBe(true);
    expect(resendCalls).toBe(1);
    expect(db.rows.size).toBe(1);
    const licenseIdAfter1 = (res1.body as any).license_id;
    const createdAt1 = db.rows.get('evt_test_replay_005')!.created_at;

    // Second delivery (Stripe resend) — same event_id
    const sig2 = await buildStripeSignature(payload, secret);
    const ctx2 = makeContext({ env, headers: { 'Stripe-Signature': sig2 }, rawBody: payload });
    const res2 = await stripeWebhook(ctx2 as any);

    expect(res2.status).toBe(200);
    expect((res2.body as any).idempotent_replay).toBe(true);
    expect((res2.body as any).email_resent).toBe(false);
    expect((res2.body as any).license_id).toBe(licenseIdAfter1);

    // CRITICAL: D1 dedup → no duplicate row, no duplicate email
    expect(resendCalls).toBe(1);
    expect(db.rows.size).toBe(1);
    expect(db.rows.get('evt_test_replay_005')!.created_at).toBe(createdAt1);
  });

  it('S291 replay with email_sent_at IS NULL → re-send email + UPDATE', async () => {
    const env = makeWebhookEnv();
    const db = env.DB as unknown as MockD1Database;
    const secret = env.STRIPE_WEBHOOK_SECRET;

    let resendCalls = 0;
    let failNextResend = true;
    if (restoreFetch) restoreFetch();
    restoreFetch = mockFetch(async (input) => {
      const url = typeof input === 'string' ? input : input.url;
      if (url.includes('api.resend.com')) {
        resendCalls += 1;
        if (failNextResend) {
          // Simulate Resend 500 outage on first delivery
          return new Response(JSON.stringify({ error: 'Internal' }), { status: 500 });
        }
        return new Response(JSON.stringify({ id: 're_test_email_id' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('unexpected fetch', { status: 500 });
    });

    const payload = JSON.stringify({
      id: 'evt_test_resend_006',
      object: 'event',
      type: 'checkout.session.completed',
      api_version: '2026-04-22.dahlia',
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: 'cs_test_resend_006',
          object: 'checkout.session',
          customer_email: 'resend@example.com',
          amount_total: 89700, // pro
          currency: 'eur',
          payment_status: 'paid',
          payment_intent: 'pi_test_resend_006',
          metadata: {},
        },
      },
    });

    // First delivery: Resend fails → D1 row created BUT email_sent_at IS NULL
    const sig1 = await buildStripeSignature(payload, secret);
    const ctx1 = makeContext({ env, headers: { 'Stripe-Signature': sig1 }, rawBody: payload });
    const res1 = await stripeWebhook(ctx1 as any);
    expect(res1.status).toBe(200);
    expect((res1.body as any).email_sent).toBe(false);
    expect(resendCalls).toBe(1);

    const row1 = db.rows.get('evt_test_resend_006')!;
    expect(row1).toBeDefined();
    expect(row1.email_sent_at).toBeNull(); // KEY: pending re-send

    // Second delivery (Stripe resend after Resend recovers): handler must re-send
    failNextResend = false;
    const sig2 = await buildStripeSignature(payload, secret);
    const ctx2 = makeContext({ env, headers: { 'Stripe-Signature': sig2 }, rawBody: payload });
    const res2 = await stripeWebhook(ctx2 as any);

    expect(res2.status).toBe(200);
    expect((res2.body as any).idempotent_replay).toBe(true);
    expect((res2.body as any).email_resent).toBe(true);
    expect(resendCalls).toBe(2); // CRITICAL: re-send happened

    const row2 = db.rows.get('evt_test_resend_006')!;
    expect(row2.email_sent_at).not.toBeNull(); // UPDATE applied
    expect(row2.license_id).toBe(row1.license_id); // license_id stable

    // Third delivery: email already sent → no further re-send
    const sig3 = await buildStripeSignature(payload, secret);
    const ctx3 = makeContext({ env, headers: { 'Stripe-Signature': sig3 }, rawBody: payload });
    const res3 = await stripeWebhook(ctx3 as any);
    expect((res3.body as any).idempotent_replay).toBe(true);
    expect((res3.body as any).email_resent).toBe(false);
    expect(resendCalls).toBe(2); // unchanged
  });

  it('S291 verify roundtrip (signEd25519 ↔ verifyEd25519Standard) valid/tampered', async () => {
    const sessionId = 'cs_test_roundtrip_007';
    const customerEmail = 'roundtrip@example.com';
    const licenseId = await computeLicenseId(sessionId, 'pro', customerEmail);

    const payload: LicensePayloadV1 = {
      kid: 'v1',
      license_id: licenseId,
      customer_email: customerEmail,
      product: 'pro',
      session_id: sessionId,
      issued_at: 1700000000,
    };
    const canonical = canonicalizeLicensePayload(payload);
    const signature = await signEd25519(keypair.privatePkcs8Base64, canonical);

    // Valid signature → true
    const validResult = await verifyEd25519Standard(keypair.publicHex, signature, canonical);
    expect(validResult).toBe(true);

    // Tampered payload (1 byte changed) → false
    const tamperedCanonical = canonical.replace('"pro"', '"bas"');
    expect(tamperedCanonical).not.toBe(canonical);
    const tamperedResult = await verifyEd25519Standard(keypair.publicHex, signature, tamperedCanonical);
    expect(tamperedResult).toBe(false);

    // Tampered signature (flip 1 byte) → false
    const sigBytes = Uint8Array.from(atob(signature), (c) => c.charCodeAt(0));
    sigBytes[0] ^= 0x01;
    let flippedBinary = '';
    for (let i = 0; i < sigBytes.length; i++) flippedBinary += String.fromCharCode(sigBytes[i]);
    const tamperedSig = btoa(flippedBinary);
    const sigTamperedResult = await verifyEd25519Standard(keypair.publicHex, tamperedSig, canonical);
    expect(sigTamperedResult).toBe(false);

    // Deterministic license_id: same inputs → same output
    const licenseIdAgain = await computeLicenseId(sessionId, 'pro', customerEmail);
    expect(licenseIdAgain).toBe(licenseId);

    // license_id changes if any input changes
    const differentId = await computeLicenseId(sessionId, 'pro', 'OTHER@example.com');
    expect(differentId).not.toBe(licenseId);
  });

  it('S291 /api/v1/verify endpoint: bool response on payload+sig', async () => {
    const env = makeWebhookEnv();

    const validCanonical = canonicalizeLicensePayload({
      kid: 'v1',
      license_id: 'a'.repeat(64),
      customer_email: 'endpoint@example.com',
      product: 'base',
      session_id: 'cs_test_endpoint_008',
      issued_at: 1700000000,
    });
    const validSig = await signEd25519(keypair.privatePkcs8Base64, validCanonical);

    // Valid case
    const ctxValid = makeContext({
      env,
      headers: { 'Content-Type': 'application/json' },
      jsonBody: { payload: validCanonical, signature_base64: validSig, kid: 'v1' },
    });
    const resValid = await verifySignature(ctxValid as any);
    expect(resValid.status).toBe(200);
    expect((resValid.body as any).valid).toBe(true);
    expect((resValid.body as any).kid).toBe('v1');

    // Tampered case (1 byte different payload)
    const tamperedPayload = validCanonical.replace('"base"', '"prox"');
    const ctxTamper = makeContext({
      env,
      headers: { 'Content-Type': 'application/json' },
      jsonBody: { payload: tamperedPayload, signature_base64: validSig, kid: 'v1' },
    });
    const resTamper = await verifySignature(ctxTamper as any);
    expect(resTamper.status).toBe(200);
    expect((resTamper.body as any).valid).toBe(false);

    // Unknown kid → 400
    const ctxBadKid = makeContext({
      env,
      headers: { 'Content-Type': 'application/json' },
      jsonBody: { payload: validCanonical, signature_base64: validSig, kid: 'v999' },
    });
    const resBadKid = await verifySignature(ctxBadKid as any);
    expect(resBadKid.status).toBe(400);
    expect((resBadKid.body as any).valid).toBe(false);
  });
});
