// ─── Email Sender — Resend wrapper ──────────────────────────────────
// S310: upgraded sender to custom domain `fluxion-app.com` (registered CF Registrar
// S309, DKIM+SPF verified S310). Resolves FBUG-RESEND-SHARED-SENDER-01 (S307):
// `onboarding@resend.dev` shared sender restricted to account-owner email only,
// blocking customer email delivery on production. Custom domain unlocks unlimited
// recipients within Resend free tier (100/day, 3000/mo).
//
// Used by scheduled cron handler (F-3 sequenza post-purchase) and admin trigger endpoint.

import type { Env } from '../lib/types';
import {
  SEQUENCE_TEMPLATES,
  type FluxionTier,
  type SequenceStep,
} from './templates';

export interface SendEmailResult {
  ok: boolean;
  providerMessageId?: string;
  provider?: 'resend';
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

const RESEND_DEFAULT_FROM = 'FLUXION <licenze@fluxion-app.com>';
const RESEND_REPLY_TO = 'fluxion.gestionale@gmail.com';

async function sendViaResend(
  apiKey: string,
  to: string,
  subject: string,
  html: string,
  context: string,
): Promise<SendEmailResult> {
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: RESEND_DEFAULT_FROM,
        to: [to],
        reply_to: [RESEND_REPLY_TO],
        subject,
        html,
      }),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(
        `[${context}] Resend failed (${response.status}): ${errorBody}`,
      );
      return { ok: false, error: errorBody, status: response.status, provider: 'resend' };
    }

    const result = (await response.json()) as { id: string };
    console.log(
      `[${context}] Sent via Resend to ${to} (Resend ID: ${result.id}, subject: "${subject}")`,
    );
    return { ok: true, providerMessageId: result.id, provider: 'resend' };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[${context}] Resend send error: ${message}`);
    return { ok: false, error: message, provider: 'resend' };
  }
}

export async function sendRaw(args: SendRawArgs): Promise<SendEmailResult> {
  const { env, to, subject, html, context = 'email' } = args;

  if (env.RESEND_API_KEY) {
    return sendViaResend(env.RESEND_API_KEY, to, subject, html, context);
  }

  console.warn(`[${context}] RESEND_API_KEY not set, skipping send to ${to}`);
  return { ok: false, error: 'NO_EMAIL_PROVIDER_CONFIGURED' };
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
