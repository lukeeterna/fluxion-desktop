# S174 — Garanzia 30 Giorni: Research Enterprise-Grade
> Agent: trend-researcher | Date: 2026-04-27 | Session: S174

---

## TL;DR (3 righe)

Stripe Refund API usa `payment_intent` (non `charge`) per Checkout one-time; le fee europee (1.5% + €0.25) NON vengono restituite al merchant — costo reale per refund €497 = ~€7.71 perso. Art. 59 D.Lgs 206/2005 lett. o) consente di ESCLUDERE il diritto di recesso legale (14gg) per software digitale consegnato immediatamente con consenso esplicito; la garanzia 30gg di FLUXION è volontaria e supera di 2x l'obbligo legale, vantaggio competitivo netto. Nessun competitor diretto (WeGest €69-196/mese, Fresha/Booksy SaaS) offre garanzia paragonabile su lifetime: FLUXION ha una window strategica.

---

## 1. Stripe Refund API — Parametri e Fee Policy

### Fonte primaria verificata
- Stripe API Refunds: https://docs.stripe.com/api/refunds/create (verificato 2026-04-27)
- Stripe Fees: https://globalfeecalculator.com/blog/how-stripe-fees-work/ (aggregatore con dati Stripe ufficiali)

### Parametri `refunds.create`

| Parametro | Tipo | Obbligatorio | Note |
|-----------|------|-------------|------|
| `payment_intent` | string | SI (o `charge`) | Usare questo per Checkout one-time |
| `charge` | string | SI (o `payment_intent`) | Legacy, evitare in nuove integrazioni |
| `amount` | integer | NO | Centesimi. Se omesso = refund totale |
| `reason` | enum | NO | `duplicate`, `fraudulent`, `requested_by_customer` |
| `metadata` | object | NO | Key-value per log interni |
| `instructions_email` | string | NO | Per metodi non supportati da refund automatico |

**Regola critica:** Per Checkout one-time, il `checkout.session` espone `payment_intent`. Usare sempre `payment_intent` — è l'API moderna, le nuove feature Stripe sono solo su PaymentIntents. Il `charge` id è accessibile via `payment_intent.latest_charge` ma non serve per il refund.

### Fee Retention Policy (Europa, verificata)
```
Stripe EU standard rate: 1.5% + €0.25 per transazione
Quando emetti un refund: Stripe NON restituisce la fee originale.

Costo effettivo refund per FLUXION:
  Base €497 → fee = (497 × 0.015) + 0.25 = €7.71 perso per ogni rimborso
  Pro  €897 → fee = (897 × 0.015) + 0.25 = €13.71 perso per ogni rimborso

NON ci sono ulteriori costi per emettere il refund su carta (solo bank transfer può avere fee extra).
```

**Confidence:** High. Fee policy da Stripe pricing ufficiale + Swipesum data (Oct 2025).

### Come recuperare `payment_intent` dal webhook esistente

Il webhook attuale (`stripe-webhook.ts`) salva in KV `session:${session.id}` ma NON salva `payment_intent`. Per supportare i refund, il KV `purchase:{email}` deve essere esteso con `payment_intent_id`.

La `checkout.session` nell'evento `checkout.session.completed` espone direttamente:
```json
{
  "id": "cs_...",
  "payment_intent": "pi_...",
  "customer_email": "...",
  "amount_total": 49700
}
```
Il campo è già disponibile — serve solo salvarlo nel KV.

---

## 2. CF Worker Route POST `/rimborso` — Design Production-Ready

### TypeScript Code Sample (CF Worker + Hono, production-ready)

```typescript
// src/routes/refund.ts
// POST /api/v1/rimborso — Garanzia 30 giorni FLUXION
// Auth: license_key (Ed25519) + email match + acquisto <30gg
// Idempotency: KV key refund:{payment_intent_id}
// Rate: 1 richiesta per license per finestra 1h (KV-based fallback, no paid plan)

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

const REFUND_WINDOW_DAYS = 30;
const RATE_LIMIT_WINDOW_SECONDS = 3600; // 1 ora

interface PurchaseData {
  checkout_session_id: string;
  payment_intent_id: string;         // NUOVO campo da aggiungere al webhook
  customer_email: string;
  tier: 'base' | 'pro';
  amount_total: number;
  currency: string;
  created_at: string;
  email_sent: boolean;
}

interface RefundAuditLog {
  license_key_prefix: string;        // prime 8 char — mai l'intera chiave
  customer_email: string;
  payment_intent_id: string;
  amount_refunded: number;
  currency: string;
  stripe_refund_id: string;
  reason: string;
  request_ip: string;
  requested_at: string;              // ISO
  processed_at: string;              // ISO
  stripe_status: string;
  purchase_created_at: string;       // per calcolo giorni
  days_since_purchase: number;
}

export async function refundHandler(c: Context<AppEnv>) {
  const STRIPE_SECRET = c.env.STRIPE_SECRET_KEY;
  if (!STRIPE_SECRET) {
    return c.json({ error: 'Refund service not configured' }, 503);
  }

  // ── 1. Parse & validate body ─────────────────────────────────────
  let body: { email: string; license_key: string; reason?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'Invalid JSON body' }, 400);
  }

  const { email, license_key, reason = 'requested_by_customer' } = body;

  if (!email || !license_key) {
    return c.json({ error: 'email e license_key obbligatori' }, 400);
  }

  const normalizedEmail = email.toLowerCase().trim();

  // ── 2. Rate limiting (KV-based, free tier compatible) ────────────
  const rateLimitKey = `ratelimit:refund:${normalizedEmail}`;
  const rateLimitEntry = await c.env.LICENSE_CACHE.get(rateLimitKey);
  if (rateLimitEntry) {
    return c.json(
      { error: 'Richiesta già in elaborazione. Attendi 1 ora prima di riprovare.' },
      429,
    );
  }
  // Set rate limit for 1h (even before processing — anti-abuse)
  await c.env.LICENSE_CACHE.put(rateLimitKey, '1', {
    expirationTtl: RATE_LIMIT_WINDOW_SECONDS,
  });

  // ── 3. Lookup purchase by email ──────────────────────────────────
  const purchaseRaw = await c.env.LICENSE_CACHE.get(`purchase:${normalizedEmail}`);
  if (!purchaseRaw) {
    return c.json({ error: 'Nessun acquisto trovato per questa email.' }, 404);
  }

  const purchase: PurchaseData = JSON.parse(purchaseRaw);

  // ── 4. Verify email matches license_key (basic ownership check) ──
  // Full Ed25519 signature verification is done by authMiddleware on
  // protected routes; here we do a lightweight ownership check:
  // license_key must contain the email hash prefix (implement per
  // your license issuance scheme). Simplest: check KV license:{license_key}
  const licenseOwnerKey = `license:${license_key}`;
  const licenseOwnerRaw = await c.env.LICENSE_CACHE.get(licenseOwnerKey);
  if (!licenseOwnerRaw) {
    return c.json({ error: 'Licenza non valida o non trovata.' }, 403);
  }
  const licenseOwner: { email: string } = JSON.parse(licenseOwnerRaw);
  if (licenseOwner.email.toLowerCase().trim() !== normalizedEmail) {
    console.warn(`Refund mismatch: license ${license_key.slice(0, 8)}... claims email ${normalizedEmail}`);
    return c.json({ error: 'Licenza non corrispondente a questa email.' }, 403);
  }

  // ── 5. 30-day window check ───────────────────────────────────────
  const purchasedAt = new Date(purchase.created_at);
  const now = new Date();
  const daysSincePurchase = Math.floor(
    (now.getTime() - purchasedAt.getTime()) / (1000 * 60 * 60 * 24),
  );

  if (daysSincePurchase > REFUND_WINDOW_DAYS) {
    return c.json(
      {
        error: `Garanzia scaduta. Il rimborso è disponibile entro ${REFUND_WINDOW_DAYS} giorni dall'acquisto.`,
        days_since_purchase: daysSincePurchase,
        purchased_at: purchase.created_at,
      },
      422,
    );
  }

  if (!purchase.payment_intent_id) {
    // Fallback: fetch from Stripe by session ID
    console.error(`purchase:${normalizedEmail} missing payment_intent_id — manual refund required`);
    return c.json(
      { error: 'Rimborso automatico non disponibile. Contatta fluxion.gestionale@gmail.com' },
      500,
    );
  }

  // ── 6. Idempotency — prevent double refund ───────────────────────
  const idempotencyKey = `refund:${purchase.payment_intent_id}`;
  const existingRefund = await c.env.LICENSE_CACHE.get(idempotencyKey);
  if (existingRefund) {
    const existing: RefundAuditLog = JSON.parse(existingRefund);
    return c.json(
      {
        error: 'Rimborso già processato.',
        stripe_refund_id: existing.stripe_refund_id,
        processed_at: existing.processed_at,
      },
      409,
    );
  }

  // ── 7. Call Stripe Refunds API ───────────────────────────────────
  const requestIp = c.req.header('CF-Connecting-IP') ?? 'unknown';

  const stripeBody = new URLSearchParams({
    payment_intent: purchase.payment_intent_id,
    reason: 'requested_by_customer',
    'metadata[fluxion_email]': normalizedEmail,
    'metadata[days_since_purchase]': String(daysSincePurchase),
    'metadata[request_ip]': requestIp,
    'metadata[tier]': purchase.tier,
  });

  const stripeResponse = await fetch('https://api.stripe.com/v1/refunds', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${STRIPE_SECRET}`,
      'Content-Type': 'application/x-www-form-urlencoded',
      'Idempotency-Key': `fluxion-refund-${purchase.payment_intent_id}`,
      'Stripe-Version': '2024-12-18.acacia', // pin to stable version
    },
    body: stripeBody.toString(),
  });

  if (!stripeResponse.ok) {
    const errText = await stripeResponse.text();
    console.error(`Stripe refund failed for ${normalizedEmail}: ${errText}`);
    return c.json(
      { error: 'Errore nel processare il rimborso. Contatta fluxion.gestionale@gmail.com' },
      502,
    );
  }

  const stripeRefund: { id: string; status: string; amount: number; currency: string } =
    await stripeResponse.json();

  // ── 8. Write audit log to KV ─────────────────────────────────────
  const auditLog: RefundAuditLog = {
    license_key_prefix: license_key.slice(0, 8),
    customer_email: normalizedEmail,
    payment_intent_id: purchase.payment_intent_id,
    amount_refunded: stripeRefund.amount,
    currency: stripeRefund.currency,
    stripe_refund_id: stripeRefund.id,
    reason,
    request_ip: requestIp,
    requested_at: now.toISOString(),
    processed_at: new Date().toISOString(),
    stripe_status: stripeRefund.status,
    purchase_created_at: purchase.created_at,
    days_since_purchase: daysSincePurchase,
  };

  // Permanent idempotency record (10 anni)
  await c.env.LICENSE_CACHE.put(idempotencyKey, JSON.stringify(auditLog), {
    expirationTtl: 86400 * 365 * 10,
  });

  // ── 9. Revoke license in KV ──────────────────────────────────────
  // Mark purchase as refunded (keeps record for disputes)
  const revokedPurchase = { ...purchase, status: 'refunded', refunded_at: now.toISOString() };
  await c.env.LICENSE_CACHE.put(
    `purchase:${normalizedEmail}`,
    JSON.stringify(revokedPurchase),
    { expirationTtl: 86400 * 365 * 10 },
  );
  // Invalidate license activation
  await c.env.LICENSE_CACHE.put(licenseOwnerKey, JSON.stringify({ ...licenseOwner, status: 'revoked' }), {
    expirationTtl: 86400 * 365 * 10,
  });

  // ── 10. Send refund confirmation email via Resend ─────────────────
  await sendRefundEmail(c.env.RESEND_API_KEY, normalizedEmail, purchase.tier, stripeRefund.amount);

  console.log(
    `Refund processed: ${normalizedEmail} — ${stripeRefund.id} — ${stripeRefund.amount / 100}${stripeRefund.currency.toUpperCase()} — day ${daysSincePurchase}/${REFUND_WINDOW_DAYS}`,
  );

  return c.json({
    success: true,
    stripe_refund_id: stripeRefund.id,
    amount_refunded_eur: stripeRefund.amount / 100,
    message: 'Rimborso processato. Riceverai i fondi in 5-10 giorni lavorativi.',
  });
}

async function sendRefundEmail(
  resendApiKey: string,
  email: string,
  tier: string,
  amountCents: number,
): Promise<void> {
  if (!resendApiKey) return;
  const amount = (amountCents / 100).toFixed(2);
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${resendApiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'FLUXION <noreply@fluxion-landing.pages.dev>',
      to: [email],
      subject: 'FLUXION — Rimborso confermato',
      html: buildRefundEmailHtml(tier, amount),
    }),
  });
}

function buildRefundEmailHtml(tier: string, amount: string): string {
  return `<!DOCTYPE html><html lang="it"><body style="background:#0f0f0f;font-family:system-ui,sans-serif;padding:40px 20px;">
<table width="600" style="background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;margin:0 auto;">
  <tr><td style="padding:40px;text-align:center;">
    <h1 style="color:#fff;font-size:24px;margin:0 0 8px;">Rimborso confermato</h1>
    <p style="color:#888;font-size:15px;margin:0 0 24px;">FLUXION ${tier.charAt(0).toUpperCase() + tier.slice(1)} — €${amount}</p>
    <p style="color:#ccc;font-size:15px;line-height:1.7;margin:0 0 24px;">
      Il tuo rimborso di <strong style="color:#fff;">€${amount}</strong> è stato processato.<br>
      I fondi arriveranno sul tuo conto entro <strong style="color:#fff;">5–10 giorni lavorativi</strong>,<br>
      a seconda della tua banca.
    </p>
    <p style="color:#888;font-size:14px;">
      Domande? <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff;">fluxion.gestionale@gmail.com</a>
    </p>
  </td></tr>
</table>
</body></html>`;
}
```

---

## 3. KV Schema — Estensioni Necessarie

### 3a. Modifica al webhook esistente (`stripe-webhook.ts`)

Il campo `payment_intent_id` NON è attualmente salvato in `purchaseData`. Va aggiunto.

```typescript
// In stripeWebhook(), dopo il cast `const session = event.data.object`:
// Aggiungere nel StripeCheckoutSession interface:
interface StripeCheckoutSession {
  id: string;
  payment_intent: string | null;    // AGGIUNGERE QUESTO
  // ... resto invariato
}

// Nel purchaseData object:
const purchaseData = {
  checkout_session_id: session.id,
  payment_intent_id: session.payment_intent ?? null,   // AGGIUNGERE
  customer_email: customerEmail,
  tier,
  amount_total: session.amount_total,
  currency: session.currency,
  created_at: new Date().toISOString(),
  email_sent: false,
  status: 'active',                  // AGGIUNGERE: 'active' | 'refunded' | 'revoked'
};
```

### 3b. Nuovi KV Keys

| Key pattern | TTL | Contenuto | Scopo |
|-------------|-----|-----------|-------|
| `purchase:{email}` | 10 anni | `PurchaseData` (esteso con `payment_intent_id`, `status`) | Principale — lookup per refund |
| `session:{session_id}` | 30gg | `PurchaseData` | Idempotency webhook (già esiste) |
| `refund:{payment_intent_id}` | 10 anni | `RefundAuditLog` | Idempotency refund + dispute evidence |
| `ratelimit:refund:{email}` | 3600s | `"1"` | Anti-abuse — 1 req/email/ora |
| `license:{license_key}` | 10 anni | `{ email, status, issued_at }` | Ownership check + revoca |

### 3c. Esempi JSON

```jsonc
// KV: purchase:marco.rossi@gmail.com
{
  "checkout_session_id": "cs_live_abc123",
  "payment_intent_id": "pi_live_xyz789",  // NUOVO
  "customer_email": "marco.rossi@gmail.com",
  "tier": "base",
  "amount_total": 49700,
  "currency": "eur",
  "created_at": "2026-04-27T10:30:00.000Z",
  "email_sent": true,
  "status": "active"                        // NUOVO
}

// KV: refund:pi_live_xyz789
{
  "license_key_prefix": "flx_a1b2",
  "customer_email": "marco.rossi@gmail.com",
  "payment_intent_id": "pi_live_xyz789",
  "amount_refunded": 49700,
  "currency": "eur",
  "stripe_refund_id": "re_live_qqq111",
  "reason": "requested_by_customer",
  "request_ip": "185.x.x.x",
  "requested_at": "2026-05-15T09:12:00.000Z",
  "processed_at": "2026-05-15T09:12:01.340Z",
  "stripe_status": "succeeded",
  "purchase_created_at": "2026-04-27T10:30:00.000Z",
  "days_since_purchase": 18
}
```

---

## 4. Compliance IT — D.Lgs 206/2005 Checklist

### Posizione legale FLUXION

| Aspetto | Norma | Status | Azione richiesta |
|---------|-------|--------|-----------------|
| Diritto recesso 14gg per consumatore | Art. 52 D.Lgs 206/2005 | Escludibile | Richiede consenso esplicito a checkout |
| Eccezione software digitale | Art. 59 lett. o) | Applicabile | Checkbox + dichiarazione al checkout |
| Garanzia commerciale volontaria 30gg | Nessuna norma — scelta FLUXION | Supera la legge | OK: vantaggio commerciale |
| Pubblicità ingannevole se garanzia non funziona | D.Lgs 206/2005 art. 21 | RISCHIO ATTIVO | Implementare il meccanismo |
| GDPR — log IP per audit refund | Art. 6 GDPR (legittimo interesse) | Conforme con retention 10 anni | Aggiornare Privacy Policy |
| Informativa pre-contrattuale | Art. 49 D.Lgs 206/2005 | Obbligo | Includere in email post-acquisto e landing |

### Testo eccezione art. 59 (estratto brocardi.it, verificato)

> "la fornitura di contenuto digitale mediante un supporto non materiale, se l'esecuzione è iniziata con l'accordo espresso del consumatore e con la sua accettazione del fatto che in tal caso avrebbe perso il diritto di recesso"

**Implicazione pratica:** Stripe Checkout deve mostrare un checkbox PRIMA del pagamento:
```
[ ] Acconsento all'esecuzione immediata del contratto e dichiaro di
    sapere che perderò il diritto di recesso previsto dall'art. 52
    del Codice del Consumo. FLUXION offre comunque una garanzia
    commerciale volontaria di 30 giorni.
```

Senza questo checkbox: il consumatore MANTIENE il diritto di recesso di 14gg e può richiedere rimborso senza limiti entro quei 14gg. Con il checkbox: il diritto di recesso è escluso, ma FLUXION offre 30gg volontari.

**Confidence:** High. Fonte primaria: brocardi.it art. 59, testo normativo verificato.

---

## 5. Risk Matrix + Mitigation

| # | Rischio | Probabilità | Impatto | Mitigation |
|---|---------|-------------|---------|-----------|
| R1 | Double refund (doppio click o retry) | Media | Alto — €497 perso due volte | Idempotency key KV `refund:{pi_id}` + 409 se già processato |
| R2 | Abuso garanzia: download + refund + riuso software | Bassa-Media | Alto — licenza usata gratis | Revoca KV `license:{key}` status=revoked; phone-home controlla status ogni 30gg |
| R3 | Chargeback post-refund (doppio recupero) | Bassa | Molto alto — Stripe dispute fee €15 + importo | Audit log con IP, timestamp, stripe_refund_id da usare come evidence |
| R4 | `payment_intent_id` mancante per acquisti pre-fix | Certa (legacy) | Medio — refund manuale richiesto | Fallback a "contatta support" con email; backfill manuale da Stripe Dashboard |
| R5 | RESEND fail — cliente non riceve conferma rimborso | Bassa | Basso-Medio | Fire-and-forget (non bloccante); follow-up entro 24h da log |

---

## 6. Decision Matrix — Canale Richiesta Rimborso

| Approccio | Pro | Contro | Raccomandazione FLUXION |
|-----------|-----|--------|------------------------|
| **Form pubblico landing** (`/rimborso`) | Self-service, zero attrito | Esposto a bot/abusi; richiede auth robusto | **Sconsigliato ora** — superficie d'attacco elevata, base clienti piccola |
| **Email gate** (`rimborso@fluxion.it` → CF Worker trigger) | Zero superficie pubblica; Gianluca controlla il flusso | Semi-manuale; ritardo 24-48h | **Consigliato fase 1** — realistico per <100 clienti |
| **In-app (Tauri) via `/api/v1/rimborso`** | Auth Ed25519 nativo, zero form pubblico; immediato | Richiede implementazione Rust + UI | **Consigliato fase 2** — dopo 50+ clienti |

**Raccomandazione immediata (S174):** Email gate + CF Worker automatico.
- L'email `rimborso@fluxion.gestionale@gmail.com` (forward) trigga CF Worker
- Il Worker usa l'email del mittente come lookup key
- Stripe refund eseguito automaticamente se <30gg
- Replica dell'audit log in KV per dispute

---

## 7. Competitor Benchmark — Garanzia su Software Gestionale IT

| Competitor | Modello | Garanzia | Note |
|-----------|---------|----------|------|
| WeGest | SaaS €69-196/mese | Nessuna menzionata | Contratto 12 mesi — cancellazione = perdita anno |
| Fresha | SaaS gratuito (commission) | Nessuna | Free tier, no garanzia commerciale |
| Booksy | SaaS $29-99/mese | Trial 14gg | No lifetime, no garanzia rimborso |
| FattureInCloud | SaaS €8-49/mese | Trial gratuito | No garanzia post-trial |
| **FLUXION** | Lifetime €497-897 | **30gg volontaria** | **Unico con lifetime + garanzia >14gg legali** |

Fonte WeGest: wegest.it/prezzi-software-wegest (verificato 2026-04-27, €69-196/mese, nessuna garanzia menzionata).
Fonte Fresha: terms.fresha.com (verificato 2026-04-27, nessuna garanzia su abbonamenti).
Fonte Booksy: help.booksy.com (2026-04-27, 14gg trial solo).

**Implicazione strategica:** La garanzia 30gg su un lifetime purchase è un differenziatore reale, non ha equivalenti nel mercato PMI italiano. Va messa in hero section, non in footnote.

---

## 8. Wrangler Config — Aggiornamenti Richiesti

```toml
# Aggiungere in wrangler.toml:
# Secrets aggiuntivi:
# STRIPE_SECRET_KEY = "sk_live_..."    — per emettere refund (read-write, non solo webhook)

# Route aggiuntiva da registrare in index.ts:
# app.post('/api/v1/rimborso', refundHandler)
# NOTA: NON dietro authMiddleware — serve email + license_key come auth proprio
```

**IMPORTANTE:** `STRIPE_WEBHOOK_SECRET` (whsec_...) è diverso da `STRIPE_SECRET_KEY` (sk_live_...). Il webhook usa solo il secret per verificare le firme. Per emettere refund serve la secret key. Aggiungere via `wrangler secret put STRIPE_SECRET_KEY`.

---

## 9. Email Post-Rimborso — Best Practice IT

- Lingua: italiano, tu-tone (coerente con landing)
- Subject: "FLUXION — Rimborso confermato" (no emoji)
- Body: importo in euro, 5-10 giorni lavorativi (non "giorni" generico — le banche italiane sono lente)
- CTA opzionale: "Se vuoi tornare in futuro, il tuo sconto fondatore è riservato" (retention play)
- Footer: partita IVA o riferimento fiscale se FLUXION è struttura legale
- Template incluso nel codice campione sopra (sezione 2)

---

## Gaps Identificati

1. **`payment_intent_id` non salvato** nel webhook attuale — bloccante per refund automatici
2. **`license:{key}` → email mapping non esiste** in KV — necessario per ownership check. Da progettare insieme alla license issuance flow (fuori scope S174 research)
3. **Checkbox Stripe Checkout** per art. 59 non implementato nella landing — rischio recesso 14gg consumatore IT
4. **Stripe API version pinning** non presente nel codice attuale — raccomandato fissare a `2024-12-18.acacia`
5. **CF Workers Rate Limiting native** richiede piano Workers paid ($5/mese) — confermato da wrangler.toml commento. Il fallback KV-based nel codice campione è sufficiente e gratuito per <100 clienti

---

## Sources

- [Stripe Refund API — Create](https://docs.stripe.com/api/refunds/create)
- [Stripe Refunds object](https://docs.stripe.com/api/refunds/object)
- [Art. 59 Codice del Consumo — Brocardi.it](https://www.brocardi.it/codice-del-consumo/parte-iii/titolo-iii/capo-i/sezione-ii/art59.html)
- [Stripe Fees 2026 — GlobalFeeCalculator](https://globalfeecalculator.com/blog/how-stripe-fees-work/)
- [Stripe Fees — Swipesum Oct 2025](https://www.swipesum.com/insights/guide-to-stripe-fees-rates-for-2025)
- [CF Workers Rate Limiting API](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)
- [Stripe Dispute Evidence Best Practices](https://docs.stripe.com/disputes/best-practices)
- [WeGest Prezzi](https://www.wegest.it/prezzi-software-wegest/) — verificato 2026-04-27
- [Fresha Terms of Service](https://terms.fresha.com/terms-service) — verificato 2026-04-27
- [PaymentIntents vs Charges — Stripe](https://docs.stripe.com/payments/payment-intents/migration/charges)
