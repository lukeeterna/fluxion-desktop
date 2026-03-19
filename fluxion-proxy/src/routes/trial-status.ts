// ─── Trial Status Endpoint ─────────────────────────────────────────
// Lightweight check for Sara trial status (no NLU call needed).

import type { Context } from 'hono';
import type { AppEnv, TrialStatusResponse } from '../lib/types';

export async function trialStatus(c: Context<AppEnv>) {
  const license = c.get('license');
  const cacheEntry = c.get('cacheEntry');
  const maxCalls = parseInt(c.env.MAX_NLU_CALLS_PER_DAY, 10);
  const trialDays = parseInt(c.env.TRIAL_DAYS, 10);

  let saraEnabled = true;
  let daysRemaining: number | null = null;

  if (license.tier === 'pro' || license.tier === 'enterprise') {
    daysRemaining = null;
  } else if (cacheEntry.trial_started_at) {
    const startDate = new Date(cacheEntry.trial_started_at);
    const elapsed = Math.floor(
      (Date.now() - startDate.getTime()) / (1000 * 60 * 60 * 24),
    );
    daysRemaining = Math.max(0, trialDays - elapsed);
    saraEnabled = daysRemaining > 0;
  } else {
    daysRemaining = trialDays;
  }

  const today = new Date().toISOString().slice(0, 10);
  const callsToday =
    cacheEntry.nlu_calls_date === today ? cacheEntry.nlu_calls_today : 0;

  const response: TrialStatusResponse = {
    tier: license.tier,
    sara_enabled: saraEnabled,
    days_remaining: daysRemaining,
    calls_remaining: maxCalls - callsToday,
    calls_today: callsToday,
  };

  return c.json(response);
}
