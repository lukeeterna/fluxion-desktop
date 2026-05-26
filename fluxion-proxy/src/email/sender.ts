// ─── Email Sender — Brevo (primary) + Resend (fallback) wrapper ─────
// Generic email client + sequence step dispatcher.
// S299: gradual rollout to Brevo (pattern S296 stripe-webhook).
// If BREVO_API_KEY set → Brevo. Else Resend. Else skip + warn.
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
  provider?: 'brevo' | 'resend';
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

// Defaults aligned with stripe-webhook.ts S296.
const BREVO_DEFAULT_SENDER_EMAIL = 'noreply@fluxion-app.brevosend.com';
const BREVO_DEFAULT_SENDER_NAME = 'FLUXION';
const RESEND_DEFAULT_FROM = 'FLUXION <onboarding@resend.dev>';

async function sendViaBrevo(
  apiKey: string,
  to: string,
  subject: string,
  html: string,
  context: string,
): Promise<SendEmailResult> {
  try {
    const response = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: {
        'api-key': apiKey,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        sender: { name: BREVO_DEFAULT_SENDER_NAME, email: BREVO_DEFAULT_SENDER_EMAIL },
        to: [{ email: to }],
        subject,
        htmlContent: html,
      }),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(
        `[${context}] Brevo failed (${response.status}): ${errorBody}`,
      );
      return { ok: false, error: errorBody, status: response.status, provider: 'brevo' };
    }

    const result = (await response.json()) as { messageId?: string };
    console.log(
      `[${context}] Sent via Brevo to ${to} (messageId: ${result.messageId ?? 'unknown'}, subject: "${subject}")`,
    );
    return { ok: true, providerMessageId: result.messageId, provider: 'brevo' };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[${context}] Brevo send error: ${message}`);
    return { ok: false, error: message, provider: 'brevo' };
  }
}

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

  // S299 gradual rollout: Brevo primary if key present, else Resend fallback.
  if (env.BREVO_API_KEY) {
    return sendViaBrevo(env.BREVO_API_KEY, to, subject, html, context);
  }

  if (env.RESEND_API_KEY) {
    return sendViaResend(env.RESEND_API_KEY, to, subject, html, context);
  }

  console.warn(`[${context}] Neither BREVO_API_KEY nor RESEND_API_KEY set, skipping send to ${to}`);
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
