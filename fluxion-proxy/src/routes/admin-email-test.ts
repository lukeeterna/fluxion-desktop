// ─── Admin: Email Sequence Test Trigger ─────────────────────────────
// Manual trigger to validate F-3 email templates without waiting D+1..D+30.
// Auth: Bearer ADMIN_API_SECRET
//
// Endpoints:
//   POST /admin/email-sequence/preview  { email, tier, step }   — render + send a single step
//   POST /admin/email-sequence/run-now                           — invoke cron handler immediately

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';
import { sendSequenceStep } from '../email/sender';
import {
  SEQUENCE_TEMPLATES,
  type FluxionTier,
  type SequenceStep,
} from '../email/templates';
import { runEmailSequenceCron } from '../scheduled/email-sequence';

function unauthorized() {
  return new Response(JSON.stringify({ error: 'Unauthorized' }), {
    status: 401,
    headers: { 'Content-Type': 'application/json' },
  });
}

function checkAuth(c: Context<AppEnv>): boolean {
  const auth = c.req.header('Authorization') || '';
  const expected = `Bearer ${c.env.ADMIN_API_SECRET}`;
  return auth === expected;
}

interface PreviewBody {
  email?: string;
  tier?: FluxionTier;
  step?: number;
}

export async function previewSequenceStep(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();

  const body = (await c.req.json().catch(() => ({}))) as PreviewBody;
  const email = body.email?.trim().toLowerCase();
  const tier = body.tier;
  const stepNum = body.step;

  if (!email || !email.includes('@')) {
    return c.json({ error: 'invalid_email' }, 400);
  }
  if (tier !== 'base' && tier !== 'pro') {
    return c.json({ error: 'invalid_tier', allowed: ['base', 'pro'] }, 400);
  }
  if (
    typeof stepNum !== 'number' ||
    !Number.isInteger(stepNum) ||
    stepNum < 1 ||
    stepNum > 5
  ) {
    return c.json({ error: 'invalid_step', allowed: [1, 2, 3, 4, 5] }, 400);
  }

  const step = stepNum as SequenceStep;
  const template = SEQUENCE_TEMPLATES[step];

  const result = await sendSequenceStep({
    env: c.env,
    customerEmail: email,
    tier,
    step,
  });

  return c.json({
    sent: result.ok,
    step,
    days_after_purchase: template.daysAfterPurchase,
    subject: template.subject,
    to: email,
    tier,
    resend_id: result.resendId ?? null,
    error: result.error ?? null,
  });
}

export async function runCronNow(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const stats = await runEmailSequenceCron(c.env);
  return c.json({ ok: true, stats });
}
