// ─── Email Sender — Resend HTTP API wrapper ─────────────────────────
// Generic Resend client + sequence step dispatcher.
// Used by scheduled cron handler and admin trigger endpoint.

import type { Env } from '../lib/types';
import {
  SEQUENCE_TEMPLATES,
  type FluxionTier,
  type SequenceStep,
} from './templates';

export interface SendEmailResult {
  ok: boolean;
  resendId?: string;
  error?: string;
  status?: number;
}

interface SendRawArgs {
  env: Env;
  to: string;
  subject: string;
  html: string;
  context?: string; // log prefix
}

export async function sendRaw(args: SendRawArgs): Promise<SendEmailResult> {
  const { env, to, subject, html, context = 'email' } = args;

  if (!env.RESEND_API_KEY) {
    console.warn(`[${context}] RESEND_API_KEY not set, skipping send to ${to}`);
    return { ok: false, error: 'RESEND_API_KEY_MISSING' };
  }

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'FLUXION <onboarding@resend.dev>',
        to: [to],
        subject,
        html,
      }),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(
        `[${context}] Resend failed (${response.status}): ${errorBody}`,
      );
      return { ok: false, error: errorBody, status: response.status };
    }

    const result = (await response.json()) as { id: string };
    console.log(
      `[${context}] Sent to ${to} (Resend ID: ${result.id}, subject: "${subject}")`,
    );
    return { ok: true, resendId: result.id };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[${context}] Send error: ${message}`);
    return { ok: false, error: message };
  }
}

// ─── Sequence step send ─────────────────────────────────────────────
export interface SendSequenceStepArgs {
  env: Env;
  customerEmail: string;
  tier: FluxionTier;
  step: SequenceStep;
}

export async function sendSequenceStep(
  args: SendSequenceStepArgs,
): Promise<SendEmailResult> {
  const { env, customerEmail, tier, step } = args;
  const template = SEQUENCE_TEMPLATES[step];
  if (!template) {
    return { ok: false, error: `INVALID_STEP_${step}` };
  }

  const html = template.buildHtml({
    customerEmail,
    tier,
    dmgUrl: env.DMG_DOWNLOAD_URL_MACOS,
  });

  return sendRaw({
    env,
    to: customerEmail,
    subject: template.subject,
    html,
    context: `seq-${step}`,
  });
}
