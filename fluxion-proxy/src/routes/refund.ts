// ─── Refund Route — Garanzia 30 Giorni ──────────────────────────────
// Public POST endpoint. Called from landing form.
// Body: { email, reason }
//
// Flow:
//   1. Validate input (email + reason min length)
//   2. Lookup purchase:{email} in KV → get payment_intent + created_at
//   3. Check eligibility: not already refunded + within 30 days
//   4. Idempotency: check refund:{email} KV
//   5. Stripe Refund API → POST /v1/refunds
//   6. Mark purchase as refunded → blocks future activate-by-email
//   7. Audit log: refund:{email} → {timestamp, reason, stripe_refund_id, amount}
//   8. Send confirmation email via Resend
//   9. Return 200 with refund_id
//
// Compliance: D.Lgs 206/2005 art.21 (pubblicità ingannevole) — la garanzia
// promessa in landing DEVE funzionare. art.59 lett. o) può essere invocato
// dal merchant solo con consenso esplicito a checkout (TODO Stripe Checkout).

import type { Context } from 'hono';
import type { AppEnv, Env } from '../lib/types';

interface RefundRequest {
  email: string;
  reason: string;
}

interface PurchaseData {
  checkout_session_id: string;
  customer_email: string;
  tier: 'base' | 'pro';
  amount_total: number | null;
  currency: string | null;
  payment_intent: string | null;
  created_at: string;
  email_sent: boolean;
  refunded?: boolean;
  refunded_at?: string | null;
  refund_reason?: string | null;
}

interface RefundAuditEntry {
  email: string;
  payment_intent: string;
  stripe_refund_id: string;
  amount: number;
  currency: string;
  reason: string;
  tier: string;
  refunded_at: string;
  ip: string | null;
}

interface StripeRefundResponse {
  id: string;
  object: 'refund';
  amount: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed' | 'canceled' | 'requires_action';
  payment_intent: string;
  created: number;
}

interface StripeError {
  error: {
    type: string;
    code?: string;
    message: string;
  };
}

const REASON_MIN_LENGTH = 10;
const REASON_MAX_LENGTH = 1000;

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

async function callStripeRefund(
  paymentIntent: string,
  reason: string,
  email: string,
  secretKey: string,
): Promise<StripeRefundResponse> {
  const idempotencyKey = `refund_${email.toLowerCase().trim()}_${paymentIntent}`;

  const formBody = new URLSearchParams({
    payment_intent: paymentIntent,
    reason: 'requested_by_customer',
    'metadata[customer_email]': email,
    'metadata[customer_reason]': reason.slice(0, 500),
    'metadata[source]': 'fluxion_garanzia_30gg',
  });

  const response = await fetch('https://api.stripe.com/v1/refunds', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${secretKey}`,
      'Content-Type': 'application/x-www-form-urlencoded',
      'Idempotency-Key': idempotencyKey,
      'Stripe-Version': '2024-12-18.acacia',
    },
    body: formBody.toString(),
  });

  if (!response.ok) {
    const errorBody = (await response.json().catch(() => null)) as StripeError | null;
    const message = errorBody?.error?.message ?? `HTTP ${response.status}`;
    throw new Error(`Stripe refund failed: ${message}`);
  }

  return (await response.json()) as StripeRefundResponse;
}

function buildRefundEmail(
  customerEmail: string,
  amountCents: number,
  currency: string,
  refundId: string,
): string {
  const amountStr = `${(amountCents / 100).toFixed(2)} ${currency.toUpperCase()}`;
  return `<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f0f0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;">
        <tr><td style="padding:40px 40px 20px;text-align:center;">
          <div style="display:inline-block;width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#2563eb);line-height:64px;font-size:32px;text-align:center;margin-bottom:16px;color:#fff;">&#8634;</div>
          <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;">Rimborso processato</h1>
          <p style="margin:12px 0 0;color:#888;font-size:15px;">Garanzia 30 giorni FLUXION</p>
        </td></tr>
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>
        <tr><td style="padding:30px 40px;">
          <p style="color:#e0e0e0;font-size:16px;line-height:1.6;margin:0 0 20px;">Ciao,</p>
          <p style="color:#e0e0e0;font-size:16px;line-height:1.6;margin:0 0 20px;">
            Abbiamo processato il rimborso completo di <strong style="color:#fff;">${amountStr}</strong> sulla tua carta originale.
            L'accredito arriva sul tuo metodo di pagamento entro 5-10 giorni lavorativi (tempi banca).
          </p>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 20px;">
            <tr><td style="padding:16px 20px;">
              <p style="margin:0;color:#888;font-size:13px;">ID rimborso Stripe:</p>
              <p style="margin:4px 0 0;color:#fff;font-family:monospace;font-size:14px;">${refundId}</p>
            </td></tr>
          </table>
          <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0 0 16px;">
            La tua licenza FLUXION &egrave; stata disattivata. Se hai installato l'app, puoi disinstallarla.
          </p>
          <p style="color:#888;font-size:14px;line-height:1.6;margin:0;">
            Se hai un dubbio o vuoi raccontarci cosa non ha funzionato:
            <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff;text-decoration:none;">fluxion.gestionale@gmail.com</a>
          </p>
        </td></tr>
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>
        <tr><td style="padding:20px 40px 30px;text-align:center;">
          <p style="color:#555;font-size:13px;margin:0;">FLUXION &mdash; Garanzia 30 giorni</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;
}

async function sendRefundEmail(
  env: Env,
  customerEmail: string,
  amountCents: number,
  currency: string,
  refundId: string,
): Promise<boolean> {
  if (!env.RESEND_API_KEY) {
    console.warn(`Refund ${refundId}: RESEND_API_KEY not set`);
    return false;
  }
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'FLUXION <noreply@fluxion-landing.pages.dev>',
        to: [customerEmail],
        subject: 'FLUXION — Rimborso processato',
        html: buildRefundEmail(customerEmail, amountCents, currency, refundId),
      }),
    });
    return response.ok;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Refund ${refundId}: email error: ${message}`);
    return false;
  }
}

export async function refund(c: Context<AppEnv>) {
  // ── Stripe key configured? ─────────────────────────────────────────
  if (!c.env.STRIPE_SECRET_KEY) {
    console.error('STRIPE_SECRET_KEY not configured');
    return c.json(
      {
        ok: false,
        error: 'Servizio rimborsi temporaneamente non disponibile. Scrivi a fluxion.gestionale@gmail.com.',
        code: 'REFUND_SERVICE_UNAVAILABLE',
      },
      503,
    );
  }

  // ── Parse body ─────────────────────────────────────────────────────
  let body: RefundRequest;
  try {
    body = await c.req.json<RefundRequest>();
  } catch {
    return c.json({ ok: false, error: 'Body JSON non valido', code: 'INVALID_BODY' }, 400);
  }

  const email = body.email?.toLowerCase().trim();
  const reason = body.reason?.trim() ?? '';

  if (!email || !isValidEmail(email)) {
    return c.json({ ok: false, error: 'Email non valida', code: 'INVALID_EMAIL' }, 400);
  }

  if (reason.length < REASON_MIN_LENGTH || reason.length > REASON_MAX_LENGTH) {
    return c.json(
      {
        ok: false,
        error: `Indica il motivo del rimborso (tra ${REASON_MIN_LENGTH} e ${REASON_MAX_LENGTH} caratteri).`,
        code: 'INVALID_REASON',
      },
      400,
    );
  }

  // ── Idempotency check ──────────────────────────────────────────────
  const auditKey = `refund:${email}`;
  const existingAudit = await c.env.LICENSE_CACHE.get(auditKey);
  if (existingAudit) {
    let prev: RefundAuditEntry | null = null;
    try {
      prev = JSON.parse(existingAudit) as RefundAuditEntry;
    } catch {
      /* ignore */
    }
    return c.json(
      {
        ok: false,
        error: 'Rimborso già processato per questa email.',
        code: 'ALREADY_REFUNDED',
        refunded_at: prev?.refunded_at ?? null,
        stripe_refund_id: prev?.stripe_refund_id ?? null,
      },
      409,
    );
  }

  // ── Lookup purchase ────────────────────────────────────────────────
  const purchaseKey = `purchase:${email}`;
  const purchaseRaw = await c.env.LICENSE_CACHE.get(purchaseKey);
  if (!purchaseRaw) {
    return c.json(
      {
        ok: false,
        error: 'Nessun acquisto trovato per questa email.',
        code: 'PURCHASE_NOT_FOUND',
        hint: 'Verifica di aver usato la stessa email del pagamento Stripe.',
      },
      404,
    );
  }

  let purchase: PurchaseData;
  try {
    purchase = JSON.parse(purchaseRaw) as PurchaseData;
  } catch {
    return c.json({ ok: false, error: 'Dati acquisto corrotti', code: 'DATA_ERROR' }, 500);
  }

  if (purchase.refunded === true) {
    return c.json(
      {
        ok: false,
        error: 'Questo acquisto è già stato rimborsato.',
        code: 'ALREADY_REFUNDED',
        refunded_at: purchase.refunded_at ?? null,
      },
      409,
    );
  }

  if (!purchase.payment_intent) {
    // Acquisti pre-S174 non hanno payment_intent salvato → fallback manuale
    console.error(`Refund denied for ${email}: missing payment_intent (legacy purchase)`);
    return c.json(
      {
        ok: false,
        error:
          'Per questo acquisto serve elaborazione manuale. Scrivi a fluxion.gestionale@gmail.com — risposta entro 24h.',
        code: 'MANUAL_REFUND_REQUIRED',
      },
      422,
    );
  }

  // ── Eligibility: within REFUND_WINDOW_DAYS ─────────────────────────
  const refundWindowDays = parseInt(c.env.REFUND_WINDOW_DAYS ?? '30', 10);
  const purchaseDate = new Date(purchase.created_at);
  const purchaseAge = (Date.now() - purchaseDate.getTime()) / 86400000;

  if (purchaseAge > refundWindowDays) {
    return c.json(
      {
        ok: false,
        error: `Garanzia scaduta. Sono passati ${Math.floor(purchaseAge)} giorni dall'acquisto (limite: ${refundWindowDays}).`,
        code: 'REFUND_WINDOW_EXPIRED',
        days_since_purchase: Math.floor(purchaseAge),
        refund_window_days: refundWindowDays,
      },
      410,
    );
  }

  // ── Stripe Refund API ──────────────────────────────────────────────
  let stripeRefund: StripeRefundResponse;
  try {
    stripeRefund = await callStripeRefund(
      purchase.payment_intent,
      reason,
      email,
      c.env.STRIPE_SECRET_KEY,
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Refund ${email}: Stripe API failed — ${message}`);
    return c.json(
      {
        ok: false,
        error:
          'Errore tecnico Stripe. Scrivi a fluxion.gestionale@gmail.com con questa email — processiamo manualmente.',
        code: 'STRIPE_API_ERROR',
      },
      502,
    );
  }

  // ── Mark purchase as refunded (blocks future activate-by-email) ────
  const refundedAt = new Date().toISOString();
  const updatedPurchase: PurchaseData = {
    ...purchase,
    refunded: true,
    refunded_at: refundedAt,
    refund_reason: reason.slice(0, 500),
  };
  await c.env.LICENSE_CACHE.put(purchaseKey, JSON.stringify(updatedPurchase), {
    expirationTtl: 86400 * 365 * 10,
  });

  // ── Audit log ──────────────────────────────────────────────────────
  const auditEntry: RefundAuditEntry = {
    email,
    payment_intent: purchase.payment_intent,
    stripe_refund_id: stripeRefund.id,
    amount: stripeRefund.amount,
    currency: stripeRefund.currency,
    reason: reason.slice(0, 500),
    tier: purchase.tier,
    refunded_at: refundedAt,
    ip: c.req.header('CF-Connecting-IP') ?? null,
  };
  await c.env.LICENSE_CACHE.put(auditKey, JSON.stringify(auditEntry), {
    expirationTtl: 86400 * 365 * 10,
  });

  // ── Confirmation email (non-blocking) ──────────────────────────────
  const emailSent = await sendRefundEmail(
    c.env,
    email,
    stripeRefund.amount,
    stripeRefund.currency,
    stripeRefund.id,
  );

  console.log(
    `Refund OK: ${email} — tier ${purchase.tier} — ${stripeRefund.amount}${stripeRefund.currency} — refund_id ${stripeRefund.id}`,
  );

  return c.json({
    ok: true,
    refunded: true,
    stripe_refund_id: stripeRefund.id,
    amount: stripeRefund.amount,
    currency: stripeRefund.currency,
    status: stripeRefund.status,
    email_sent: emailSent,
    message: 'Rimborso processato. Accredito in 5-10 giorni lavorativi.',
  });
}
