// ─── Stripe Webhook Handler ─────────────────────────────────────────
// S291 refactor: Stripe SDK v22 constructEventAsync + D1 dedup +
// replay-safe email re-send + Ed25519 (standard) license signing (kid:v1).
//
// Flow:
//   1. Stripe.constructEventAsync (signature verify via SubtleCryptoProvider)
//   2. D1 SELECT WHERE event_id → if exists: replay path (re-send if email_sent_at IS NULL)
//   3. Compute license_id deterministic (sha256), build payload kid:v1, sign Ed25519
//   4. D1 INSERT OR IGNORE → if meta.changes===0 (race): another worker won, replay path
//   5. Send Resend email → UPDATE email_sent_at = unixepoch() on success
//   6. KV `purchase:{email}` invariato (backward compat activate-by-email.ts)
//
// Backward compat:
//   - KV `purchase:{email}` still written (activate-by-email.ts consumes it)
//   - KV `session:{id}` deprecated (D1 is canonical dedup), still written best-effort
//   - Legacy NODE-ED25519 verify (ed25519.ts) untouched, parallel to new Ed25519 sign

import type { Context } from 'hono';
import Stripe from 'stripe';
import type { AppEnv, Env } from '../lib/types';
import {
  signEd25519,
  computeLicenseId,
  canonicalizeLicensePayload,
  type LicensePayloadV1,
} from '../lib/ed25519-sign';
import { buildRecoveryUrl } from './license-recovery';

// ─── Tier Detection ─────────────────────────────────────────────────

type FluxionTier = 'base' | 'pro';

const AMOUNT_TO_TIER: Record<number, FluxionTier> = {
  49700: 'base', // €497.00
  89700: 'pro',  // €897.00
};

function detectTier(
  amountTotal: number | null,
  metadata: Stripe.Metadata | null,
): FluxionTier | null {
  // S317: accept both `tier` and `plan` metadata keys (landing/PL use `plan`).
  const metaTier = metadata?.tier ?? metadata?.plan;
  if (metaTier === 'base' || metaTier === 'pro') {
    return metaTier;
  }
  if (amountTotal !== null && amountTotal in AMOUNT_TO_TIER) {
    return AMOUNT_TO_TIER[amountTotal];
  }
  return null;
}

// ─── Tier Display Labels ────────────────────────────────────────────

const TIER_LABELS: Record<FluxionTier, string> = {
  base: 'Base',
  pro: 'Pro',
};

// ─── Confirmation Email — Resend ───────────────────────────────────
// S306: Resend-only (Brevo removed). Email body embeds recovery URL
// (permanent HMAC link) + license payload/signature for manual activation copy-paste.

interface EmailBodyArgs {
  tier: FluxionTier;
  customerEmail: string;
  dmgUrl: string;
  recoveryUrl: string;
  licensePayload: string;
  licenseSignature: string;
}

function buildEmailHtml(args: EmailBodyArgs): string {
  const { tier, customerEmail, dmgUrl, recoveryUrl, licensePayload, licenseSignature } = args;
  const tierLabel = TIER_LABELS[tier];
  const macDownloadUrl = dmgUrl;
  const installGuideUrl = 'https://fluxion-landing.pages.dev/come-installare';
  const activateUrl = 'https://fluxion-landing.pages.dev/activate.html';
  const priceLabel = tier === 'pro' ? '897' : '497';

  return `
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f0f0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;">
        <tr><td style="padding:40px 40px 20px;text-align:center;">
          <div style="display:inline-block;width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#10b981,#059669);line-height:64px;font-size:32px;text-align:center;margin-bottom:16px;">&#10003;</div>
          <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">Ordine confermato!</h1>
          <p style="margin:12px 0 0;color:#888;font-size:15px;">FLUXION ${tierLabel} — &euro;${priceLabel}</p>
        </td></tr>
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>
        <tr><td style="padding:30px 40px;">
          <p style="color:#e0e0e0;font-size:16px;line-height:1.6;margin:0 0 20px;">Ciao,</p>
          <p style="color:#e0e0e0;font-size:16px;line-height:1.6;margin:0 0 24px;">
            Grazie per aver scelto <strong style="color:#ffffff;">FLUXION ${tierLabel}</strong>!
            Ecco tutto quello che ti serve per iniziare.
          </p>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 16px;">
            <tr><td style="padding:20px 24px;">
              <p style="color:#4a9eff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 12px;">Passo 1 &mdash; Scarica FLUXION</p>
              <p style="margin:0 0 10px;">
                <a href="${macDownloadUrl}" style="color:#4a9eff;text-decoration:none;font-size:15px;font-weight:600;">&#9660; Scarica per macOS</a>
                <span style="color:#555;font-size:13px;"> &nbsp;(macOS 12 o superiore, Intel/Apple Silicon)</span>
              </p>
              <p style="margin:8px 0 0;color:#888;font-size:12px;">
                Versione Windows in arrivo. Se sei su Windows, scrivi a <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff;text-decoration:none;">fluxion.gestionale@gmail.com</a> per essere avvisato al rilascio.
              </p>
            </td></tr>
          </table>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 16px;">
            <tr><td style="padding:20px 24px;">
              <p style="color:#4a9eff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Passo 2 &mdash; Installa</p>
              <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">
                Apri il file scaricato e segui le istruzioni.
                <a href="${installGuideUrl}" style="color:#4a9eff;text-decoration:none;"> Guida passo-passo</a>
              </p>
            </td></tr>
          </table>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #10b981;margin:0 0 24px;">
            <tr><td style="padding:20px 24px;">
              <p style="color:#10b981;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Passo 3 &mdash; Attiva la licenza</p>
              <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0 0 8px;">Al primo avvio, FLUXION ti chiede la tua email. Inserisci:</p>
              <p style="color:#ffffff;font-size:16px;font-weight:700;background:#1a2a1a;border-radius:6px;padding:10px 16px;margin:0 0 8px;font-family:monospace;">
                ${customerEmail}
              </p>
              <p style="color:#888;font-size:13px;line-height:1.5;margin:0;">
                FLUXION verifica il tuo acquisto automaticamente. Nessun codice da copiare.
                <br><a href="${activateUrl}" style="color:#4a9eff;text-decoration:none;">Istruzioni dettagliate</a>
              </p>
            </td></tr>
          </table>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #4a9eff;margin:0 0 16px;">
            <tr><td style="padding:20px 24px;">
              <p style="color:#4a9eff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Link di recupero permanente</p>
              <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0 0 8px;">
                Salva questo link nelle note o nel gestore password. Ti serve se reinstalli FLUXION o cambi computer:
              </p>
              <p style="margin:0 0 6px;word-break:break-all;">
                <a href="${recoveryUrl}" style="color:#4a9eff;text-decoration:none;font-family:monospace;font-size:12px;">${recoveryUrl}</a>
              </p>
              <p style="color:#666;font-size:12px;line-height:1.5;margin:8px 0 0;">
                Apri il link in qualsiasi browser per riottenere licenza + firma in formato JSON.
              </p>
            </td></tr>
          </table>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 24px;">
            <tr><td style="padding:20px 24px;">
              <p style="color:#888;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Attivazione manuale (solo se richiesta)</p>
              <p style="color:#ccc;font-size:13px;line-height:1.5;margin:0 0 8px;">Payload firmato:</p>
              <pre style="background:#0a0a0a;border:1px solid #2a2a2a;border-radius:6px;padding:10px;font-family:monospace;font-size:11px;color:#9cdcfe;margin:0 0 10px;white-space:pre-wrap;word-break:break-all;">${licensePayload}</pre>
              <p style="color:#ccc;font-size:13px;line-height:1.5;margin:0 0 8px;">Firma Ed25519 (base64):</p>
              <pre style="background:#0a0a0a;border:1px solid #2a2a2a;border-radius:6px;padding:10px;font-family:monospace;font-size:11px;color:#9cdcfe;margin:0;white-space:pre-wrap;word-break:break-all;">${licenseSignature}</pre>
            </td></tr>
          </table>
          <p style="color:#888;font-size:14px;line-height:1.6;margin:0;">
            Hai bisogno di aiuto? Scrivici a <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff;text-decoration:none;">fluxion.gestionale@gmail.com</a>
          </p>
        </td></tr>
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>
        <tr><td style="padding:20px 40px 30px;text-align:center;">
          <p style="color:#555;font-size:13px;margin:0;">FLUXION &mdash; Il gestionale per la tua attivit&agrave;</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`.trim();
}

interface SendEmailParams {
  env: Env;
  customerEmail: string;
  tier: FluxionTier;
  sessionId: string;
  licensePayload: string;
  licenseSignature: string;
  recoveryUrl: string;
}

// S310: upgraded sender to custom domain `fluxion-app.com` (registered CF Registrar
// S309, DKIM+SPF verified S310). Resolves FBUG-RESEND-SHARED-SENDER-01 (S307):
// shared `onboarding@resend.dev` restricted to account-owner email only.
const RESEND_DEFAULT_FROM = 'FLUXION <licenze@fluxion-app.com>';
const RESEND_REPLY_TO = 'fluxion.gestionale@gmail.com';
const EMAIL_SUBJECT = 'FLUXION — Il tuo ordine è confermato!';

async function sendViaResend(
  apiKey: string,
  toEmail: string,
  subject: string,
  htmlContent: string,
  sessionId: string,
): Promise<boolean> {
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: RESEND_DEFAULT_FROM,
        to: [toEmail],
        reply_to: [RESEND_REPLY_TO],
        subject,
        html: htmlContent,
      }),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(
        `Checkout ${sessionId}: Resend email failed (${response.status}): ${errorBody}`,
      );
      return false;
    }

    const result = await response.json() as { id: string };
    console.log(
      `Checkout ${sessionId}: Confirmation email sent via Resend to ${toEmail} (Resend ID: ${result.id})`,
    );
    return true;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Checkout ${sessionId}: Resend send error: ${message}`);
    return false;
  }
}

async function sendConfirmationEmail(params: SendEmailParams): Promise<boolean> {
  const { env, customerEmail, tier, sessionId, licensePayload, licenseSignature, recoveryUrl } = params;

  const html = buildEmailHtml({
    tier,
    customerEmail,
    dmgUrl: env.DMG_DOWNLOAD_URL_MACOS,
    recoveryUrl,
    licensePayload,
    licenseSignature,
  });

  if (env.RESEND_API_KEY) {
    return sendViaResend(env.RESEND_API_KEY, customerEmail, EMAIL_SUBJECT, html, sessionId);
  }

  console.warn(
    `Checkout ${sessionId}: RESEND_API_KEY not set, skipping email to ${customerEmail}`,
  );
  return false;
}

// ─── D1 Helpers ────────────────────────────────────────────────────

interface WebhookEventRow {
  event_id: string;
  session_id: string;
  license_id: string;
  customer_email: string;
  product: string;
  license_payload: string;
  license_signature: string;
  email_sent_at: number | null;
  created_at: number;
}

async function selectWebhookEvent(
  db: D1Database,
  eventId: string,
): Promise<WebhookEventRow | null> {
  const row = await db
    .prepare('SELECT * FROM webhook_events WHERE event_id = ? LIMIT 1')
    .bind(eventId)
    .first<WebhookEventRow>();
  return row ?? null;
}

interface InsertWebhookEventParams {
  eventId: string;
  sessionId: string;
  licenseId: string;
  customerEmail: string;
  product: FluxionTier;
  licensePayload: string;
  licenseSignature: string;
}

/**
 * Returns true if INSERT actually wrote a new row (changes === 1).
 * Returns false if row already existed (changes === 0) — race lost path.
 */
async function insertWebhookEventOrIgnore(
  db: D1Database,
  params: InsertWebhookEventParams,
): Promise<boolean> {
  const result = await db
    .prepare(
      `INSERT OR IGNORE INTO webhook_events
       (event_id, session_id, license_id, customer_email, product, license_payload, license_signature, email_sent_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, NULL)`,
    )
    .bind(
      params.eventId,
      params.sessionId,
      params.licenseId,
      params.customerEmail,
      params.product,
      params.licensePayload,
      params.licenseSignature,
    )
    .run();
  return result.meta.changes === 1;
}

async function markEmailSent(db: D1Database, eventId: string): Promise<void> {
  await db
    .prepare('UPDATE webhook_events SET email_sent_at = unixepoch() WHERE event_id = ? AND email_sent_at IS NULL')
    .bind(eventId)
    .run();
}

// ─── KV Backward-compat Writer ─────────────────────────────────────

interface PurchaseKvData {
  checkout_session_id: string;
  customer_email: string;
  tier: FluxionTier;
  amount_total: number | null;
  currency: string | null;
  payment_intent: string | null;
  created_at: string;
  email_sent: boolean;
  refunded: boolean;
  refunded_at: string | null;
  refund_reason: string | null;
}

async function writePurchaseKv(
  env: Env,
  session: Stripe.Checkout.Session,
  tier: FluxionTier,
  customerEmail: string,
  emailSent: boolean,
): Promise<void> {
  const purchaseData: PurchaseKvData = {
    checkout_session_id: session.id,
    customer_email: customerEmail,
    tier,
    amount_total: session.amount_total,
    currency: session.currency,
    payment_intent: typeof session.payment_intent === 'string' ? session.payment_intent : (session.payment_intent?.id ?? null),
    created_at: new Date().toISOString(),
    email_sent: emailSent,
    refunded: false,
    refunded_at: null,
    refund_reason: null,
  };

  const emailKey = `purchase:${customerEmail.toLowerCase().trim()}`;
  await env.LICENSE_CACHE.put(emailKey, JSON.stringify(purchaseData), {
    expirationTtl: 86400 * 365 * 10, // 10 years — lifetime license
  });
}

// ─── Webhook Handler ────────────────────────────────────────────────

export async function stripeWebhook(c: Context<AppEnv>) {
  const webhookSecret = c.env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    console.error('STRIPE_WEBHOOK_SECRET not configured');
    return c.json({ error: 'Webhook not configured' }, 500);
  }

  if (!c.env.STRIPE_SECRET_KEY) {
    console.error('STRIPE_SECRET_KEY not configured (required for SDK init)');
    return c.json({ error: 'Stripe SDK not configured' }, 500);
  }

  // D1 binding required for S291 dedup. Fail loud — production must have DB set.
  if (!c.env.DB) {
    console.error('D1 binding DB missing — refusing to process webhook unsafely');
    return c.json({ error: 'Database not configured' }, 500);
  }

  if (!c.env.ED25519_PRIVATE_KEY_PKCS8) {
    console.error('ED25519_PRIVATE_KEY_PKCS8 secret missing');
    return c.json({ error: 'License signing not configured' }, 500);
  }

  // Read raw body for signature verification (must NOT be parsed before)
  const rawBody = await c.req.text();
  const signatureHeader = c.req.header('Stripe-Signature');

  if (!signatureHeader) {
    return c.json({ error: 'Missing Stripe-Signature header' }, 400);
  }

  // Stripe SDK requires apiVersion + httpClient null for Workers env.
  // `createSubtleCryptoProvider` enables async signature verification via WebCrypto.
  const stripe = new Stripe(c.env.STRIPE_SECRET_KEY, {
    apiVersion: '2026-04-22.dahlia',
    httpClient: Stripe.createFetchHttpClient(),
  });

  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(
      rawBody,
      signatureHeader,
      webhookSecret,
      undefined,
      Stripe.createSubtleCryptoProvider(),
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Stripe webhook signature verification failed: ${message}`);
    return c.json({ error: 'Invalid signature' }, 400);
  }

  // Handle only checkout.session.completed (FSAF-09 path).
  // Other events acknowledged 200 to prevent Stripe retry storms.
  if (event.type !== 'checkout.session.completed') {
    return c.json({ received: true, type: event.type });
  }

  const session = event.data.object as Stripe.Checkout.Session;

  // Extract customer email
  const customerEmail = session.customer_email
    ?? session.customer_details?.email
    ?? (typeof session.metadata?.email === 'string' ? session.metadata.email : null);

  if (!customerEmail) {
    console.error(`Checkout ${session.id}: no customer email found`);
    return c.json({ received: true, warning: 'no_customer_email' });
  }

  const tier = detectTier(session.amount_total, session.metadata ?? null);

  if (!tier) {
    console.error(
      `Checkout ${session.id}: unknown tier for amount ${session.amount_total}`,
    );
    return c.json({ received: true, warning: 'unknown_tier' });
  }

  // ── Recovery URL (S296) — fail-soft: log if secret missing, email still sent ─
  const baseUrl = new URL(c.req.url).origin;
  let recoveryUrl: string;
  if (c.env.LICENSE_RECOVERY_SECRET) {
    recoveryUrl = await buildRecoveryUrl(baseUrl, c.env.LICENSE_RECOVERY_SECRET, customerEmail);
  } else {
    console.warn(
      `Checkout ${session.id}: LICENSE_RECOVERY_SECRET not set — email recovery URL will be placeholder`,
    );
    recoveryUrl = `${baseUrl}/api/v1/license/${encodeURIComponent(customerEmail.toLowerCase().trim())}?token=NOT_CONFIGURED`;
  }

  // ── REPLAY PATH ──────────────────────────────────────────────────
  // SELECT D1 first: if row exists with email_sent_at IS NULL, re-send and
  // mark sent. If row exists with email_sent_at, idempotent no-op.
  const existing = await selectWebhookEvent(c.env.DB, event.id);
  if (existing) {
    if (existing.email_sent_at === null) {
      console.log(
        `Stripe webhook replay (email pending): event=${event.id} session=${session.id} email=${customerEmail}`,
      );
      const emailSent = await sendConfirmationEmail({
        env: c.env,
        customerEmail,
        tier,
        sessionId: session.id,
        licensePayload: existing.license_payload,
        licenseSignature: existing.license_signature,
        recoveryUrl,
      });
      if (emailSent) {
        await markEmailSent(c.env.DB, event.id);
      }
      return c.json({
        received: true,
        idempotent_replay: true,
        email_resent: emailSent,
        event_id: event.id,
        license_id: existing.license_id,
      });
    }
    console.log(
      `Stripe webhook idempotent replay (email already sent): event=${event.id} session=${session.id}`,
    );
    return c.json({
      received: true,
      idempotent_replay: true,
      email_resent: false,
      event_id: event.id,
      license_id: existing.license_id,
    });
  }

  // ── FIRST-TIME PATH ──────────────────────────────────────────────
  // Compute license_id deterministic + build signed payload.
  const licenseId = await computeLicenseId(session.id, tier, customerEmail);
  const issuedAt = Math.floor(Date.now() / 1000);
  const payload: LicensePayloadV1 = {
    kid: 'v1',
    license_id: licenseId,
    customer_email: customerEmail.toLowerCase().trim(),
    product: tier,
    session_id: session.id,
    issued_at: issuedAt,
  };
  const payloadCanonical = canonicalizeLicensePayload(payload);
  const signature = await signEd25519(c.env.ED25519_PRIVATE_KEY_PKCS8, payloadCanonical);

  // INSERT OR IGNORE — UNIQUE on event_id guarantees dedup atomic.
  const inserted = await insertWebhookEventOrIgnore(c.env.DB, {
    eventId: event.id,
    sessionId: session.id,
    licenseId,
    customerEmail: customerEmail.toLowerCase().trim(),
    product: tier,
    licensePayload: payloadCanonical,
    licenseSignature: signature,
  });

  if (!inserted) {
    // Race lost: another worker invocation just inserted. Treat as replay
    // (re-read row and possibly re-send if email pending).
    console.log(
      `Stripe webhook race lost on D1 INSERT: event=${event.id} session=${session.id} — falling back to replay read`,
    );
    const row = await selectWebhookEvent(c.env.DB, event.id);
    if (row && row.email_sent_at === null) {
      const emailSent = await sendConfirmationEmail({
        env: c.env,
        customerEmail,
        tier,
        sessionId: session.id,
        licensePayload: row.license_payload,
        licenseSignature: row.license_signature,
        recoveryUrl,
      });
      if (emailSent) {
        await markEmailSent(c.env.DB, event.id);
      }
      return c.json({
        received: true,
        idempotent_replay: true,
        race_lost: true,
        email_resent: emailSent,
        event_id: event.id,
        license_id: row.license_id,
      });
    }
    return c.json({
      received: true,
      idempotent_replay: true,
      race_lost: true,
      email_resent: false,
      event_id: event.id,
      license_id: row?.license_id ?? licenseId,
    });
  }

  // Row inserted: send email + KV backward-compat write.
  let emailSent = false;
  try {
    emailSent = await sendConfirmationEmail({
      env: c.env,
      customerEmail,
      tier,
      sessionId: session.id,
      licensePayload: payloadCanonical,
      licenseSignature: signature,
      recoveryUrl,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Checkout ${session.id}: Unexpected email error: ${message}`);
  }

  if (emailSent) {
    await markEmailSent(c.env.DB, event.id);
  }

  // KV `purchase:{email}` backward compat (activate-by-email.ts flow).
  // Best-effort: if KV fails do NOT fail webhook (D1 is authoritative).
  try {
    await writePurchaseKv(c.env, session, tier, customerEmail, emailSent);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Checkout ${session.id}: KV backward-compat write failed: ${message}`);
  }

  console.log(
    `Stripe checkout completed: ${customerEmail} — tier: ${tier} — session: ${session.id} — license: ${licenseId} — email_sent: ${emailSent}`,
  );

  return c.json({
    received: true,
    tier,
    email: customerEmail,
    license_id: licenseId,
    email_sent: emailSent,
    event_id: event.id,
  });
}
