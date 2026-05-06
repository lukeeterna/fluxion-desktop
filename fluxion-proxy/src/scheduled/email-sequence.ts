// ─── Scheduled Cron Handler — F-3 Email Sequence ────────────────────
// Daily cron: scan all purchase:{email} keys, advance sequence step where due.
// Trigger: wrangler.toml [triggers] crons = ["0 9 * * *"] → runs daily 09:00 UTC.
//
// Sequence schedule (days after purchase):
//   step 1 → D+1 activation reminder
//   step 2 → D+2 first-access tutorial
//   step 3 → D+3 tips & tricks
//   step 4 → D+7 power user feedback
//   step 5 → D+30 review request
//
// State machine: purchase.sequence_step monotonically increases 0 → 5.
// Idempotency: key advances only after successful Resend send.

import type { Env } from '../lib/types';
import { sendSequenceStep } from '../email/sender';
import {
  SEQUENCE_ORDER,
  SEQUENCE_TEMPLATES,
  type FluxionTier,
  type SequenceStep,
} from '../email/templates';

interface PurchaseRecord {
  customer_email: string;
  tier: FluxionTier;
  created_at: string;
  email_sent?: boolean; // welcome email
  refunded?: boolean;
  sequence_step?: number; // 0 = welcome only, 1..5 advancing
  last_sequence_email_at?: string | null;
  sequence_unsubscribed?: boolean;
  // additional fields ignored
  [k: string]: unknown;
}

const RESEND_FREE_TIER_DAILY_LIMIT = 100;
// Safety margin: leave headroom for confirmation emails + diagnostic reports.
const MAX_SEQUENCE_SENDS_PER_RUN = 80;

// Minimum gap between two sequence emails to the same address.
// Prevents step-2 + step-3 from firing on consecutive cron runs if D+2 was skipped.
const MIN_HOURS_BETWEEN_SENDS = 18;

function daysSince(iso: string, nowMs: number): number {
  const ts = Date.parse(iso);
  if (Number.isNaN(ts)) return -1;
  return Math.floor((nowMs - ts) / 86_400_000);
}

function hoursSince(iso: string | null | undefined, nowMs: number): number {
  if (!iso) return Infinity;
  const ts = Date.parse(iso);
  if (Number.isNaN(ts)) return Infinity;
  return (nowMs - ts) / 3_600_000;
}

function nextDueStep(
  purchase: PurchaseRecord,
  nowMs: number,
): SequenceStep | null {
  if (purchase.refunded) return null;
  if (purchase.sequence_unsubscribed) return null;

  const currentStep = purchase.sequence_step ?? 0;
  const days = daysSince(purchase.created_at, nowMs);
  if (days < 0) return null;

  const hoursSinceLast = hoursSince(purchase.last_sequence_email_at, nowMs);
  if (hoursSinceLast < MIN_HOURS_BETWEEN_SENDS) return null;

  for (const step of SEQUENCE_ORDER) {
    if (step <= currentStep) continue;
    const due = SEQUENCE_TEMPLATES[step].daysAfterPurchase;
    if (days >= due) return step;
    break; // ordered, can stop
  }
  return null;
}

export interface CronStats {
  scanned: number;
  sent: number;
  skipped: number;
  errors: number;
  byStep: Record<string, number>;
  durationMs: number;
}

export async function runEmailSequenceCron(env: Env): Promise<CronStats> {
  const startMs = Date.now();
  const stats: CronStats = {
    scanned: 0,
    sent: 0,
    skipped: 0,
    errors: 0,
    byStep: {},
    durationMs: 0,
  };

  let cursor: string | undefined;
  let safetyLoops = 0;

  do {
    // KV.list pagination — up to 1000 keys per page, prefix-filtered.
    const page = await env.LICENSE_CACHE.list({
      prefix: 'purchase:',
      cursor,
      limit: 1000,
    });

    for (const { name: key } of page.keys) {
      if (stats.sent >= MAX_SEQUENCE_SENDS_PER_RUN) break;

      stats.scanned++;
      const raw = await env.LICENSE_CACHE.get(key);
      if (!raw) {
        stats.skipped++;
        continue;
      }

      let purchase: PurchaseRecord;
      try {
        purchase = JSON.parse(raw) as PurchaseRecord;
      } catch {
        console.error(`[seq-cron] malformed JSON at ${key}`);
        stats.errors++;
        continue;
      }

      if (
        !purchase.customer_email ||
        !purchase.created_at ||
        (purchase.tier !== 'base' && purchase.tier !== 'pro')
      ) {
        stats.skipped++;
        continue;
      }

      const step = nextDueStep(purchase, startMs);
      if (step === null) {
        stats.skipped++;
        continue;
      }

      const result = await sendSequenceStep({
        env,
        customerEmail: purchase.customer_email,
        tier: purchase.tier,
        step,
      });

      if (!result.ok) {
        console.error(
          `[seq-cron] step ${step} failed for ${purchase.customer_email}: ${result.error}`,
        );
        stats.errors++;
        continue;
      }

      // Advance state ONLY on successful send (idempotent retry on next run).
      const updated: PurchaseRecord = {
        ...purchase,
        sequence_step: step,
        last_sequence_email_at: new Date().toISOString(),
      };
      await env.LICENSE_CACHE.put(key, JSON.stringify(updated), {
        expirationTtl: 86_400 * 365 * 10, // preserve 10y TTL
      });

      stats.sent++;
      stats.byStep[String(step)] = (stats.byStep[String(step)] ?? 0) + 1;
    }

    cursor = page.list_complete ? undefined : page.cursor;
    safetyLoops++;
    if (safetyLoops > 10) {
      console.warn('[seq-cron] safety loop break at 10 pages (10k keys)');
      break;
    }
  } while (cursor && stats.sent < MAX_SEQUENCE_SENDS_PER_RUN);

  stats.durationMs = Date.now() - startMs;

  console.log(
    `[seq-cron] done: scanned=${stats.scanned} sent=${stats.sent} skipped=${stats.skipped} errors=${stats.errors} duration=${stats.durationMs}ms byStep=${JSON.stringify(stats.byStep)}`,
  );

  if (stats.sent >= RESEND_FREE_TIER_DAILY_LIMIT) {
    console.warn(
      `[seq-cron] approaching Resend free tier daily limit (${stats.sent}/${RESEND_FREE_TIER_DAILY_LIMIT})`,
    );
  }

  return stats;
}
