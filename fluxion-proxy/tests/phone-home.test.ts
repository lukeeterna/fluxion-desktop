// ─── phone-home.test.ts ─────────────────────────────────────────────
// Unit tests for src/routes/phone-home.ts.
// Coverage:
//   - happy path Pro license → status=ok, tier=pro, sara_enabled=true, days_remaining=null
//   - happy path Base trial fresh → trial_started_at set, sara_enabled=true, days_remaining=TRIAL_DAYS
//   - S279 gap fix: purchase.refunded=true → status='revoked', tier='expired', sara_enabled=false
//   - corrupt purchase JSON → falls through to normal flow (no crash, defensive)

import { describe, it, expect } from 'vitest';
import { phoneHome } from '../src/routes/phone-home';
import {
  makeEnv,
  makeContext,
  makeLicense,
  makeCacheEntry,
  MockKVNamespace,
} from './_helpers';

describe('phone-home.ts', () => {
  it('happy path Pro: status=ok, sara always enabled, no trial countdown', async () => {
    const env = makeEnv();
    const license = makeLicense({
      tier: 'pro',
      licensee_email: 'pro@example.com',
      license_id: 'lic_pro_001',
    });
    const cacheEntry = makeCacheEntry({
      license_id: 'lic_pro_001',
      tier: 'pro',
    });

    const ctx = makeContext({
      env,
      variables: {
        license,
        cacheEntry,
        cacheKey: 'lic:lic_pro_001',
      },
    });

    const res = await phoneHome(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).status).toBe('ok');
    expect((res.body as any).tier).toBe('pro');
    expect((res.body as any).sara_enabled).toBe(true);
    expect((res.body as any).sara_days_remaining).toBeNull();
    expect((res.body as any).grace_period_days).toBe(7);
  });

  it('happy path Base trial first call: sets trial_started_at, returns 30 days remaining', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    const license = makeLicense({
      tier: 'base',
      licensee_email: 'base@example.com',
      license_id: 'lic_base_001',
    });
    const cacheEntry = makeCacheEntry({
      license_id: 'lic_base_001',
      tier: 'base',
      trial_started_at: null, // first phone-home
    });

    const ctx = makeContext({
      env,
      variables: {
        license,
        cacheEntry,
        cacheKey: 'lic:lic_base_001',
      },
    });

    const res = await phoneHome(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).status).toBe('ok');
    expect((res.body as any).tier).toBe('base');
    expect((res.body as any).sara_enabled).toBe(true);
    expect((res.body as any).sara_days_remaining).toBe(30);

    // trial_started_at persisted in KV
    const updated = kv.getJson<any>('lic:lic_base_001');
    expect(updated.trial_started_at).not.toBeNull();
    expect(typeof updated.trial_started_at).toBe('string');
  });

  it('S279 gap fix: purchase.refunded=true → status=revoked, tier=expired, sara_enabled=false', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    // Seed refunded purchase for the licensee email
    kv.setJson('purchase:refunded@example.com', {
      checkout_session_id: 'cs_test_001',
      customer_email: 'refunded@example.com',
      tier: 'pro',
      amount_total: 89700,
      currency: 'eur',
      payment_intent: 'pi_test_001',
      created_at: '2026-05-01T00:00:00.000Z',
      email_sent: true,
      refunded: true,
      refunded_at: '2026-05-10T00:00:00.000Z',
      refund_reason: 'test refund',
    });

    const license = makeLicense({
      tier: 'pro',
      licensee_email: 'Refunded@Example.com', // mixed case — must normalize
      license_id: 'lic_revoked_001',
    });
    const cacheEntry = makeCacheEntry({
      license_id: 'lic_revoked_001',
      tier: 'pro',
      last_phone_home: '2020-01-01T00:00:00.000Z', // sentinel old value
    });
    const sentinelOld = cacheEntry.last_phone_home;

    const ctx = makeContext({
      env,
      variables: {
        license,
        cacheEntry,
        cacheKey: 'lic:lic_revoked_001',
      },
    });

    const res = await phoneHome(ctx as any);

    expect(res.status).toBe(200);
    expect((res.body as any).status).toBe('revoked');
    expect((res.body as any).tier).toBe('expired');
    expect((res.body as any).sara_enabled).toBe(false);
    expect((res.body as any).sara_days_remaining).toBe(0);

    // cacheEntry timestamp updated in KV (so we can audit last contact even on revoked).
    // Note: cacheEntry is mutated in-place by the handler — compare against sentinel string.
    const updated = kv.getJson<any>('lic:lic_revoked_001');
    expect(updated.last_phone_home).not.toBe(sentinelOld);
    expect(new Date(updated.last_phone_home).getTime()).toBeGreaterThan(
      new Date(sentinelOld).getTime(),
    );
  });

  it('defensive: corrupt purchase JSON does NOT crash, falls through to normal flow', async () => {
    const env = makeEnv();
    const kv = env.LICENSE_CACHE as unknown as MockKVNamespace;

    // Inject malformed JSON
    await kv.put('purchase:weird@example.com', '{not valid json');

    const license = makeLicense({
      tier: 'pro',
      licensee_email: 'weird@example.com',
      license_id: 'lic_weird_001',
    });
    const cacheEntry = makeCacheEntry({
      license_id: 'lic_weird_001',
      tier: 'pro',
    });

    const ctx = makeContext({
      env,
      variables: {
        license,
        cacheEntry,
        cacheKey: 'lic:lic_weird_001',
      },
    });

    const res = await phoneHome(ctx as any);

    // Corrupt KV value treated as no-purchase → normal flow
    expect(res.status).toBe(200);
    expect((res.body as any).status).toBe('ok');
    expect((res.body as any).tier).toBe('pro');
    expect((res.body as any).sara_enabled).toBe(true);
  });
});
