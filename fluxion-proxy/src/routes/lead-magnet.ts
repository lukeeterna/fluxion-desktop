// ─── Lead Magnet — GDPR Template Email Gate ────────────────────────
// Public POST endpoint. Called from landing inline form.
// Body: { nome, email, consenso_marketing, file_slug, website (honeypot) }
//
// Flow:
//   1. Honeypot check → silent 200 if filled
//   2. Validate input (nome, email, file_slug)
//   3. MX check via cloudflare-dns.com
//   4. Rate limit per IP (3/h) → silent 200 if exceeded
//   5. Idempotency per email (48h re-submit) → silent 200 with new tokens
//   6. Generate 4 signed URL (one per GDPR template) HMAC-SHA256, TTL 72h
//   7. Save lead in KV (no TTL, perpetuo per analytics)
//   8. Save 4 download tokens in KV (TTL 72h)
//   9. Send Resend E1 email with 4 download links + Gianluca firma
//   10. Return 200 sempre (non rivela esito ai bot)
//
// Compliance: Garante FAQ 2024 (single opt-in OK con log), GDPR art.6(1)(f)
// legittimo interesse per email correlate al documento, art.6(1)(a) consenso
// per follow-up commerciale (E4) con checkbox non pre-spuntata.

import type { Context } from 'hono';
import type { AppEnv, Env } from '../lib/types';

interface LeadMagnetRequest {
  nome?: string;
  email?: string;
  consenso_marketing?: boolean;
  file_slug?: string;
  website?: string; // honeypot
}

const VALID_FILE_SLUGS = [
  'informativa-privacy',
  'registro-trattamenti',
  'consenso-art9-sanitario',
  'guida-gdpr-pmi',
] as const;
type FileSlug = (typeof VALID_FILE_SLUGS)[number];

interface FileMeta {
  slug: FileSlug;
  filename: string; // path su CF Pages
  display: string; // nome leggibile per email
}

const FILES: FileMeta[] = [
  {
    slug: 'informativa-privacy',
    filename: 'informativa-privacy.docx',
    display: 'Informativa privacy clienti (DOCX)',
  },
  {
    slug: 'registro-trattamenti',
    filename: 'registro-trattamenti.xlsx',
    display: 'Registro dei trattamenti (XLSX)',
  },
  {
    slug: 'consenso-art9-sanitario',
    filename: 'consenso-art9-sanitario.pdf',
    display: 'Consenso art.9 dati sanitari (PDF)',
  },
  {
    slug: 'guida-gdpr-pmi',
    filename: 'guida-gdpr-pmi.html',
    display: 'Guida GDPR PMI — checklist 15 step (HTML)',
  },
];

interface LeadRecord {
  email: string;
  nome: string;
  consenso_marketing: boolean;
  consented_at: string;
  consent_text: string;
  ip: string | null;
  source: 'gdpr_lead_magnet';
  file_slug_clicked: FileSlug;
  files_sent: FileSlug[];
  created_at: string;
  last_activity: string;
  sequence_step: number;
  sequence_last_sent: string | null;
  converted: boolean;
  converted_at: string | null;
}

interface DownloadToken {
  email: string;
  file_slug: FileSlug;
  expires_at: string;
  used: boolean;
  used_at: string | null;
  created_at: string;
}

const RATE_LIMIT_PER_IP_PER_HOUR = 3;
const RESUBMIT_COOLDOWN_HOURS = 48;
const TOKEN_TTL_SECONDS = 259200; // 72h
const NOME_MIN = 2;
const NOME_MAX = 100;
const CONSENT_TEXT_MARKETING =
  'Sì, voglio anche consigli su come gestire meglio la mia attività';

const SILENT_OK = {
  ok: true,
  message: 'Controlla la tua email entro 60 secondi.',
};

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function isValidFileSlug(value: string): value is FileSlug {
  return (VALID_FILE_SLUGS as readonly string[]).includes(value);
}

function getClientIp(c: Context<AppEnv>): string | null {
  return (
    c.req.header('cf-connecting-ip') ||
    c.req.header('x-forwarded-for')?.split(',')[0]?.trim() ||
    null
  );
}

async function checkMxRecord(domain: string): Promise<boolean> {
  try {
    const res = await fetch(
      `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(domain)}&type=MX`,
      {
        headers: { Accept: 'application/dns-json' },
        cf: { cacheTtl: 3600 } as RequestInitCfProperties,
      },
    );
    if (!res.ok) return true; // fail-open per non bloccare lead validi
    const data = (await res.json()) as { Answer?: unknown[] };
    return Array.isArray(data.Answer) && data.Answer.length > 0;
  } catch {
    return true; // fail-open
  }
}

async function hmacSha256Hex(key: string, message: string): Promise<string> {
  const encoder = new TextEncoder();
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    encoder.encode(key),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign(
    'HMAC',
    cryptoKey,
    encoder.encode(message),
  );
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function generateDownloadTokens(
  env: Env,
  email: string,
): Promise<Array<{ slug: FileSlug; token: string; expires_at: string }>> {
  const expiresAt = new Date(Date.now() + TOKEN_TTL_SECONDS * 1000).toISOString();
  const results: Array<{ slug: FileSlug; token: string; expires_at: string }> = [];

  for (const file of FILES) {
    const message = `${email}|${file.slug}|${expiresAt}`;
    const token = await hmacSha256Hex(env.LEAD_MAGNET_SIGNING_SECRET, message);

    const record: DownloadToken = {
      email,
      file_slug: file.slug,
      expires_at: expiresAt,
      used: false,
      used_at: null,
      created_at: new Date().toISOString(),
    };

    await env.LICENSE_CACHE.put(`gdpr_token:${token}`, JSON.stringify(record), {
      expirationTtl: TOKEN_TTL_SECONDS,
    });

    results.push({ slug: file.slug, token, expires_at: expiresAt });
  }

  return results;
}

function buildLeadEmailHtml(
  nome: string,
  links: Array<{ slug: FileSlug; token: string }>,
  workerBaseUrl: string,
): string {
  const linkRows = FILES.map((f) => {
    const link = links.find((l) => l.slug === f.slug);
    if (!link) return '';
    const url = `${workerBaseUrl}/api/v1/gdpr-download?token=${link.token}&file=${f.slug}`;
    return `
      <tr><td style="padding:8px 0;">
        <a href="${url}" style="display:inline-block;padding:12px 18px;background:#3b82f6;color:#fff;text-decoration:none;border-radius:8px;font-weight:600;font-size:14px;">
          ⬇ ${f.display}
        </a>
      </td></tr>`;
  }).join('');

  const safeNome = nome.replace(/[<>]/g, '');

  return `<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f7;padding:30px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;border:1px solid #e5e5e7;">
        <tr><td style="padding:32px 32px 16px;">
          <h1 style="margin:0;color:#1a1a1a;font-size:22px;font-weight:700;line-height:1.3;">
            Ciao ${safeNome}, i tuoi 4 template GDPR sono pronti
          </h1>
          <p style="margin:12px 0 0;color:#555;font-size:15px;line-height:1.6;">
            Clicca sui link qui sotto per scaricarli. I link funzionano per <strong>72 ore</strong> e sono personali (uso singolo).
          </p>
        </td></tr>
        <tr><td style="padding:8px 32px 16px;">
          <table cellpadding="0" cellspacing="0" width="100%">
            ${linkRows}
          </table>
        </td></tr>
        <tr><td style="padding:0 32px;"><hr style="border:none;border-top:1px solid #e5e5e7;margin:0;"></td></tr>
        <tr><td style="padding:20px 32px 8px;">
          <p style="color:#555;font-size:14px;line-height:1.6;margin:0;">
            I template sono compilabili — sostituisci i campi tra parentesi con i dati della tua attività. La <em>Guida GDPR PMI</em> è una checklist di 15 step da seguire in ordine.
          </p>
          <p style="color:#555;font-size:14px;line-height:1.6;margin:12px 0 0;">
            Buona fortuna,<br>
            <strong style="color:#1a1a1a;">Gianluca di FLUXION</strong>
          </p>
          <p style="color:#777;font-size:13px;line-height:1.6;margin:16px 0 0;">
            <em>P.S.: domani ti mando qualcosa che potrebbe servirti. Se non vuoi più ricevere email, <a href="mailto:fluxion.gestionale@gmail.com?subject=Unsubscribe&body=Rimuovi%20la%20mia%20email" style="color:#3b82f6;">scrivimi qui</a> e ti tolgo subito.</em>
          </p>
        </td></tr>
        <tr><td style="padding:20px 32px 28px;text-align:center;">
          <p style="color:#999;font-size:12px;margin:0;">
            FLUXION — Gestionale italiano per PMI · <a href="https://fluxion-landing.pages.dev/privacy.html" style="color:#999;">Privacy</a>
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;
}

async function sendLeadEmail(
  env: Env,
  email: string,
  nome: string,
  links: Array<{ slug: FileSlug; token: string }>,
): Promise<boolean> {
  if (!env.RESEND_API_KEY) {
    console.warn('Lead-magnet: RESEND_API_KEY not set');
    return false;
  }
  const workerBaseUrl = 'https://fluxion-proxy.gianlucanewtech.workers.dev';
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Gianluca di FLUXION <noreply@fluxion-landing.pages.dev>',
        to: [email],
        subject: `${nome}, i tuoi 4 template GDPR sono pronti`,
        html: buildLeadEmailHtml(nome, links, workerBaseUrl),
      }),
    });
    if (!response.ok) {
      const errBody = await response.text().catch(() => '');
      console.error(`Lead-magnet email failed: HTTP ${response.status} ${errBody.slice(0, 200)}`);
      return false;
    }
    return true;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Lead-magnet email error: ${message}`);
    return false;
  }
}

export async function leadMagnet(c: Context<AppEnv>) {
  // ── Pre-condition: signing secret configured ───────────────────────
  if (!c.env.LEAD_MAGNET_SIGNING_SECRET) {
    console.error('LEAD_MAGNET_SIGNING_SECRET not configured');
    return c.json(SILENT_OK, 200); // silent fail — don't reveal misconfig
  }

  // ── Parse body ─────────────────────────────────────────────────────
  let body: LeadMagnetRequest;
  try {
    body = await c.req.json<LeadMagnetRequest>();
  } catch {
    return c.json(SILENT_OK, 200); // malformed JSON → silent OK
  }

  // ── Honeypot ───────────────────────────────────────────────────────
  if (body.website && body.website.trim() !== '') {
    console.log(`Lead-magnet honeypot triggered from IP ${getClientIp(c)}`);
    return c.json(SILENT_OK, 200);
  }

  // ── Validation ─────────────────────────────────────────────────────
  const nome = body.nome?.trim() ?? '';
  const email = body.email?.toLowerCase().trim() ?? '';
  const fileSlugRaw = body.file_slug?.trim() ?? '';
  const consensoMarketing = Boolean(body.consenso_marketing);

  if (nome.length < NOME_MIN || nome.length > NOME_MAX) {
    return c.json(SILENT_OK, 200);
  }
  if (!email || !isValidEmail(email)) {
    return c.json(SILENT_OK, 200);
  }
  if (!isValidFileSlug(fileSlugRaw)) {
    return c.json(SILENT_OK, 200);
  }
  const fileSlug: FileSlug = fileSlugRaw;

  // ── MX check ───────────────────────────────────────────────────────
  const domain = email.split('@')[1];
  if (!domain) return c.json(SILENT_OK, 200);
  const mxOk = await checkMxRecord(domain);
  if (!mxOk) {
    console.log(`Lead-magnet rejected: no MX for ${domain}`);
    return c.json(SILENT_OK, 200);
  }

  // ── Rate limit per IP ──────────────────────────────────────────────
  const ip = getClientIp(c);
  if (ip) {
    const rlKey = `rl_lead:${ip}`;
    const rlRaw = await c.env.LICENSE_CACHE.get(rlKey);
    const rlCount = rlRaw ? parseInt(rlRaw, 10) : 0;
    if (rlCount >= RATE_LIMIT_PER_IP_PER_HOUR) {
      console.log(`Lead-magnet rate-limit IP ${ip} (count=${rlCount})`);
      return c.json(SILENT_OK, 200);
    }
    await c.env.LICENSE_CACHE.put(rlKey, String(rlCount + 1), {
      expirationTtl: 3600,
    });
  }

  // ── Resubmit cooldown ──────────────────────────────────────────────
  const leadKey = `lead:${email}`;
  const existingRaw = await c.env.LICENSE_CACHE.get(leadKey);
  if (existingRaw) {
    try {
      const existing = JSON.parse(existingRaw) as LeadRecord;
      const lastSent = existing.sequence_last_sent
        ? new Date(existing.sequence_last_sent).getTime()
        : new Date(existing.created_at).getTime();
      const hoursSince = (Date.now() - lastSent) / 3_600_000;
      if (hoursSince < RESUBMIT_COOLDOWN_HOURS) {
        console.log(`Lead-magnet cooldown for ${email} (${hoursSince.toFixed(1)}h)`);
        return c.json(SILENT_OK, 200);
      }
    } catch {
      /* malformed → overwrite */
    }
  }

  // ── Generate signed download tokens (4) ────────────────────────────
  let tokens: Array<{ slug: FileSlug; token: string; expires_at: string }>;
  try {
    tokens = await generateDownloadTokens(c.env, email);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`Lead-magnet token generation failed for ${email}: ${msg}`);
    return c.json(SILENT_OK, 200);
  }

  // ── Send E1 email ──────────────────────────────────────────────────
  const emailSent = await sendLeadEmail(
    c.env,
    email,
    nome,
    tokens.map((t) => ({ slug: t.slug, token: t.token })),
  );

  // ── Save lead record ───────────────────────────────────────────────
  const now = new Date().toISOString();
  const lead: LeadRecord = {
    email,
    nome,
    consenso_marketing: consensoMarketing,
    consented_at: now,
    consent_text: consensoMarketing ? CONSENT_TEXT_MARKETING : '',
    ip,
    source: 'gdpr_lead_magnet',
    file_slug_clicked: fileSlug,
    files_sent: FILES.map((f) => f.slug),
    created_at: now,
    last_activity: now,
    sequence_step: emailSent ? 0 : -1, // -1 = E1 failed, da rinviare
    sequence_last_sent: emailSent ? now : null,
    converted: false,
    converted_at: null,
  };

  // Lead record is permanent (no TTL) for analytics conversion lead → cliente
  await c.env.LICENSE_CACHE.put(leadKey, JSON.stringify(lead));

  console.log(
    `Lead-magnet OK: email=${email} nome=${nome} clicked=${fileSlug} marketing=${consensoMarketing} email_sent=${emailSent}`,
  );

  return c.json(SILENT_OK, 200);
}
