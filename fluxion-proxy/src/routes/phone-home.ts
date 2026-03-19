// ─── Phone Home Endpoint ───────────────────────────────────────────
// Called on app startup + every 24h. Validates license and returns
// Sara enablement status + trial days remaining.

import type { Context } from 'hono';
import type { AppEnv, PhoneHomeResponse } from '../lib/types';

export async function phoneHome(c: Context<AppEnv>) {
  const license = c.get('license');
  const cacheEntry = c.get('cacheEntry');
  const cacheKey = c.get('cacheKey');
  const trialDays = parseInt(c.env.TRIAL_DAYS, 10);
  const gracePeriodDays = parseInt(c.env.GRACE_PERIOD_DAYS, 10);

  // Update last phone-home timestamp
  const now = new Date();
  cacheEntry.last_phone_home = now.toISOString();

  // Handle trial tracking
  if (license.tier === 'trial' || license.tier === 'base') {
    // Set trial start if first phone-home (server-side timestamp, tamper-proof)
    if (!cacheEntry.trial_started_at) {
      cacheEntry.trial_started_at = now.toISOString();
    }
  }

  // Calculate Sara enablement
  const { saraEnabled, daysRemaining } = calculateSaraStatus(
    license.tier,
    cacheEntry.trial_started_at,
    trialDays,
  );

  // Update cache
  await c.env.LICENSE_CACHE.put(cacheKey, JSON.stringify(cacheEntry), {
    expirationTtl: 86400,
  });

  const response: PhoneHomeResponse = {
    status: 'ok',
    tier: license.tier,
    sara_enabled: saraEnabled,
    sara_days_remaining: daysRemaining,
    server_time: now.toISOString(),
    grace_period_days: gracePeriodDays,
  };

  return c.json(response);
}

// ─── Sara Status Calculator ───────────────────────────────────────

function calculateSaraStatus(
  tier: string,
  trialStartedAt: string | null,
  trialDays: number,
): { saraEnabled: boolean; daysRemaining: number | null } {
  // Pro/Enterprise: Sara always enabled, no trial
  if (tier === 'pro' || tier === 'enterprise') {
    return { saraEnabled: true, daysRemaining: null };
  }

  // Trial/Base: Sara enabled for trialDays then locks
  if (!trialStartedAt) {
    return { saraEnabled: true, daysRemaining: trialDays };
  }

  const startDate = new Date(trialStartedAt);
  const now = new Date();
  const elapsedMs = now.getTime() - startDate.getTime();
  const elapsedDays = Math.floor(elapsedMs / (1000 * 60 * 60 * 24));
  const remaining = Math.max(0, trialDays - elapsedDays);

  return {
    saraEnabled: remaining > 0,
    daysRemaining: remaining,
  };
}
