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
  const { tier, customerEmail, recoveryUrl, licensePayload, licenseSignature } = args;
  const tierLabel = TIER_LABELS[tier];
  const installGuideUrl = 'https://fluxion-landing.pages.dev/come-installare';
  const activateUrl = 'https://fluxion-landing.pages.dev/activate.html';
  const priceLabel = tier === 'pro' ? '897' : '497';
  const logoUrl = 'https://fluxion-landing.pages.dev/assets/fluxion-logo-mark.png';

  return `
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,sans-serif;">

  <!-- Preheader (nascosto, visibile solo nell'anteprima client email) -->
  <span style="display:none;visibility:hidden;color:transparent;height:0;width:0;overflow:hidden;max-height:0;max-width:0;">Il tuo acquisto FLUXION ${tierLabel} &egrave; confermato. Attiva la tua licenza in un minuto.</span>

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 16px 48px;">
    <tr><td align="center">

      <!-- ── WRAPPER CARD ── -->
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;border:1px solid #e2e6ea;overflow:hidden;">

        <!-- HEADER BAND — sfondo chiaro per fondere col fondo grigio del logo JPG -->
        <tr>
          <td style="background:#f0f2f5;padding:28px 40px;text-align:center;border-bottom:1px solid #e2e6ea;">
            <img src="${logoUrl}" alt="FLUXION" width="120" height="auto" style="display:block;margin:0 auto;border:0;">
          </td>
        </tr>

        <!-- HERO -->
        <tr>
          <td style="padding:36px 40px 28px;border-bottom:1px solid #eaecef;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="vertical-align:middle;padding-right:16px;">
                  <p style="margin:0 0 6px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#6b7a8d;">Riepilogo acquisto</p>
                  <h1 style="margin:0 0 8px;font-size:26px;font-weight:700;color:#111827;letter-spacing:-0.4px;">Benvenuto in FLUXION!</h1>
                  <p style="margin:0;font-size:15px;color:#4b5563;line-height:1.5;">
                    Il tuo <strong>FLUXION ${tierLabel}</strong> &egrave; attivo.
                    Segui il passo qui sotto per iniziare a usarlo subito.
                  </p>
                </td>
                <td style="vertical-align:middle;white-space:nowrap;text-align:right;">
                  <p style="margin:0;font-size:28px;font-weight:800;color:#111827;">&euro;${priceLabel}</p>
                  <p style="margin:4px 0 0;font-size:12px;color:#6b7a8d;font-weight:600;">PAGAMENTO RICEVUTO</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- BODY: 1 STEP -->
        <tr>
          <td style="padding:28px 40px 0;">

            <!-- STEP 1: Attiva (highlight verde) -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
              <tr>
                <td style="vertical-align:top;width:36px;padding-top:2px;">
                  <div style="width:28px;height:28px;border-radius:50%;background:#16a34a;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:#ffffff;">1</div>
                </td>
                <td style="vertical-align:top;padding-left:12px;border:2px solid #16a34a;border-radius:6px;padding:16px 20px 16px 20px;background:#f0fdf4;">
                  <p style="margin:0 0 6px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#15803d;">Attiva la tua licenza</p>
                  <p style="margin:0 0 12px;font-size:14px;color:#374151;line-height:1.55;">
                    Clicca il pulsante verde qui sotto: si apre la pagina con il tuo codice licenza.
                    Copialo e incollalo in FLUXION da
                    <strong>Impostazioni &rarr; Gestione Licenza &rarr; Codice Licenza</strong>.
                  </p>
                  <p style="margin:0 0 12px;font-size:13px;color:#4b5563;">
                    Licenza intestata a:&nbsp;
                    <span style="font-family:monospace;font-weight:600;color:#111827;background:#e8f5e9;border-radius:4px;padding:2px 8px;">${customerEmail}</span>
                  </p>
                  <table cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="background:#16a34a;border-radius:5px;padding:11px 24px;">
                        <a href="${recoveryUrl}" style="color:#ffffff;font-size:14px;font-weight:700;text-decoration:none;">Recupera il codice licenza</a>
                      </td>
                    </tr>
                  </table>
                  <p style="margin:12px 0 0;font-size:12px;color:#6b7a8d;line-height:1.5;">
                    <a href="${activateUrl}" style="color:#2563eb;text-decoration:none;">Istruzioni dettagliate</a>
                    &nbsp;&mdash;&nbsp;
                    In fondo a questa email trovi anche il codice completo per l&rsquo;attivazione manuale.
                  </p>
                </td>
              </tr>
            </table>

          </td>
        </tr>

        <!-- SALVA IL LINK box -->
        <tr>
          <td style="padding:0 40px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fc;border:1px solid #d1d5db;border-radius:6px;">
              <tr>
                <td style="padding:16px 20px;">
                  <p style="margin:0 0 4px;font-size:13px;font-weight:700;color:#374151;">Salva questo link (ti servirà sempre)</p>
                  <p style="margin:0 0 8px;font-size:13px;color:#6b7a8d;line-height:1.5;">
                    Se reinstalli FLUXION o cambi computer, apri questo link in qualsiasi browser per recuperare la tua licenza:
                  </p>
                  <p style="margin:0;word-break:break-all;">
                    <a href="${recoveryUrl}" style="color:#2563eb;font-size:12px;font-family:monospace;text-decoration:none;">${recoveryUrl}</a>
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ATTIVAZIONE MANUALE (collassata) -->
        <tr>
          <td style="padding:0 40px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fc;border:1px solid #e2e6ea;border-radius:6px;">
              <tr>
                <td style="padding:14px 20px;">
                  <p style="margin:0 0 10px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.4px;color:#9ca3af;">Attivazione manuale &mdash; solo se richiesta dal supporto</p>
                  <p style="margin:0 0 6px;font-size:12px;color:#6b7a8d;">Payload firmato:</p>
                  <pre style="margin:0 0 12px;background:#ffffff;border:1px solid #e2e6ea;border-radius:4px;padding:10px;font-size:11px;color:#374151;white-space:pre-wrap;word-break:break-all;font-family:monospace;">${licensePayload}</pre>
                  <p style="margin:0 0 6px;font-size:12px;color:#6b7a8d;">Firma Ed25519 (base64):</p>
                  <pre style="margin:0;background:#ffffff;border:1px solid #e2e6ea;border-radius:4px;padding:10px;font-size:11px;color:#374151;white-space:pre-wrap;word-break:break-all;font-family:monospace;">${licenseSignature}</pre>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- SUPPORTO -->
        <tr>
          <td style="padding:0 40px 32px;">
            <p style="margin:0;font-size:14px;color:#6b7a8d;line-height:1.6;">
              Hai domande? Rispondi a questa email oppure scrivici a
              <a href="mailto:licenze@fluxion-app.com" style="color:#2563eb;text-decoration:none;font-weight:500;">licenze@fluxion-app.com</a>.
              Rispondiamo entro un giorno lavorativo.
            </p>
          </td>
        </tr>

        <!-- FOOTER LEGALE -->
        <tr>
          <td style="background:#f8f9fc;border-top:1px solid #eaecef;padding:20px 40px;text-align:center;">
            <p style="margin:0 0 6px;font-size:12px;color:#9ca3af;">
              FLUXION &mdash; Gestionale per PMI italiane
            </p>
            <p style="margin:0 0 6px;font-size:11px;color:#b0b8c1;">
              <a href="https://fluxion-app.com/privacy" style="color:#9ca3af;text-decoration:none;">Privacy</a>
              &nbsp;&bull;&nbsp;
              <a href="mailto:licenze@fluxion-app.com?subject=Disiscrivimi%20dalla%20sequenza%20email" style="color:#9ca3af;text-decoration:none;">Disiscriviti</a>
            </p>
            <p style="margin:0;font-size:11px;color:#d1d5db;">
              Hai ricevuto questa email perch&eacute; hai acquistato FLUXION ${tierLabel}.
            </p>
          </td>
        </tr>

      </table>
      <!-- /WRAPPER CARD -->

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

// ─── R1 Sales Agent — Conversion Attribution (§6.7) ────────────────
// Maps a paid checkout back to the originating WhatsApp lead via the
// `client_reference_id` ("lead_<id>") carried by the payment link (checkout.py).
// INSERT OR IGNORE on session_id (UNIQUE) → idempotent across Stripe retries.
// Best-effort: never throws into the webhook path (D1 conversions are analytics,
// license issuance is authoritative and must not be blocked by an attribution miss).
async function recordConversion(
  db: D1Database,
  session: Stripe.Checkout.Session,
  customerEmail: string | null,
): Promise<void> {
  const ref = session.client_reference_id;
  if (!ref || !ref.startsWith('lead_')) {
    return; // not a Sales Agent lead (organic/landing purchase) — nothing to attribute.
  }
  const leadId = ref.slice(5);
  try {
    await db
      .prepare(
        `INSERT OR IGNORE INTO conversions (lead_id, session_id, amount, email, at)
         VALUES (?, ?, ?, ?, ?)`,
      )
      .bind(
        leadId,
        session.id,
        session.amount_total,
        customerEmail,
        new Date().toISOString(),
      )
      .run();
    console.log(`Conversion attributed: lead=${leadId} session=${session.id} amount=${session.amount_total}`);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Conversion attribution failed (best-effort): lead=${leadId} session=${session.id}: ${message}`);
  }
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

// ─── Refund / Chargeback Handler (R-01-ter) ────────────────────────
// On charge.refunded / charge.dispute.created → set purchase:{email}.refunded=true.
// Email extraction:
//   - charge.refunded: event.data.object is a Charge → billing_details.email ?? receipt_email.
//   - charge.dispute.created: event.data.object is a Dispute → dispute.charge is a string
//     charge id (webhook payloads are NOT expanded) → stripe.charges.retrieve() → email.
// Fail-soft: any KV-miss / parse-fail / lookup error → still 200 (avoid Stripe retry storm),
// and write a minimal record with refunded:true so the gate denies future activation.

interface RefundFlagResult {
  email: string | null;
  reason: string | null;
}

/**
 * Resolve customer email from a Stripe Charge object.
 * Precedence: billing_details.email ?? receipt_email (per Stripe Charge shape).
 */
function emailFromCharge(charge: Stripe.Charge): string | null {
  return charge.billing_details?.email ?? charge.receipt_email ?? null;
}

async function resolveRefundEmail(
  stripe: Stripe,
  event: Stripe.Event,
): Promise<RefundFlagResult> {
  if (event.type === 'charge.refunded') {
    const charge = event.data.object as Stripe.Charge;
    return { email: emailFromCharge(charge), reason: 'refund' };
  }
  // charge.dispute.created → object is a Dispute. `dispute.charge` is a string id
  // (or expandable Charge). Retrieve the Charge to read its email.
  const dispute = event.data.object as Stripe.Dispute;
  const chargeId = typeof dispute.charge === 'string' ? dispute.charge : dispute.charge?.id ?? null;
  if (!chargeId) {
    return { email: null, reason: 'dispute' };
  }
  const charge = await stripe.charges.retrieve(chargeId);
  return { email: emailFromCharge(charge), reason: 'dispute' };
}

/**
 * Mark purchase:{email}.refunded=true. If the KV record is missing or corrupt,
 * write a minimal stub (fail-soft) so the license gate denies activation anyway.
 */
async function markPurchaseRefunded(
  env: Env,
  email: string,
  reason: string,
): Promise<void> {
  const key = `purchase:${email.toLowerCase().trim()}`;
  const refundedAt = new Date().toISOString();
  const raw = await env.LICENSE_CACHE.get(key);

  let data: PurchaseKvData;
  if (raw) {
    try {
      data = JSON.parse(raw) as PurchaseKvData;
    } catch {
      // Corrupt record → rebuild minimal stub flagged refunded (fail-soft, deny on gate).
      console.error(`Refund event: corrupt purchase KV for ${email} — writing minimal refunded stub`);
      data = {
        checkout_session_id: '',
        customer_email: email.toLowerCase().trim(),
        tier: 'base',
        amount_total: null,
        currency: null,
        payment_intent: null,
        created_at: refundedAt,
        email_sent: false,
        refunded: false,
        refunded_at: null,
        refund_reason: null,
      };
    }
  } else {
    // KV-miss → minimal stub flagged refunded so the gate can deny.
    console.warn(`Refund event: no purchase KV for ${email} — writing minimal refunded stub`);
    data = {
      checkout_session_id: '',
      customer_email: email.toLowerCase().trim(),
      tier: 'base',
      amount_total: null,
      currency: null,
      payment_intent: null,
      created_at: refundedAt,
      email_sent: false,
      refunded: false,
      refunded_at: null,
      refund_reason: null,
    };
  }

  data.refunded = true;
  data.refunded_at = refundedAt;
  data.refund_reason = reason;

  await env.LICENSE_CACHE.put(key, JSON.stringify(data), {
    expirationTtl: 86400 * 365 * 10, // 10 years — lifetime license
  });
}

async function handleRefundEvent(
  c: Context<AppEnv>,
  stripe: Stripe,
  event: Stripe.Event,
): Promise<Response> {
  try {
    const { email, reason } = await resolveRefundEmail(stripe, event);
    if (!email) {
      // No email resolvable → fail-soft 200 (cannot flag, avoid retry storm).
      console.error(`Refund event ${event.id} (${event.type}): no email resolvable — acknowledging 200`);
      return c.json({ received: true, type: event.type, warning: 'no_email' });
    }
    await markPurchaseRefunded(c.env, email, reason ?? 'refund');
    console.log(`Refund event ${event.id} (${event.type}): purchase:${email} marked refunded`);
    return c.json({ received: true, type: event.type, refunded: true, email });
  } catch (err: unknown) {
    // Fail-soft: never 5xx on a refund event (Stripe would retry-storm).
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Refund event ${event.id} (${event.type}): handler error (fail-soft 200): ${message}`);
    return c.json({ received: true, type: event.type, warning: 'refund_handler_error' });
  }
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

  // ── REFUND / CHARGEBACK PATH (R-01-ter) ──────────────────────────
  // charge.refunded + charge.dispute.created → flag KV purchase:{email}.refunded.
  // KV key + email normalization MUST match refund.ts:365 / license-recovery.ts:117
  // (`purchase:${email.toLowerCase().trim()}`). Drives /license/validate + recovery gate.
  if (event.type === 'charge.refunded' || event.type === 'charge.dispute.created') {
    return handleRefundEvent(c, stripe, event);
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

  // R1 (§6.7): attribute the conversion to the originating WA lead.
  // Idempotent (INSERT OR IGNORE on session_id) + best-effort → safe before replay path.
  await recordConversion(c.env.DB, session, customerEmail);

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
