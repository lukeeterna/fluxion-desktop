// ─── GDPR Download — Signed URL One-Time Verification ──────────────
// Public GET endpoint. Called by lead clicking link in E1 email.
// Query: ?token=<hex>&file=<slug>
//
// Flow:
//   1. Parse query params
//   2. Lookup gdpr_token:{token} in KV
//   3. Verify: matches file_slug, !used, !expired
//   4. Mark token as used (one-time)
//   5. Update lead_event:{email} for analytics
//   6. 302 redirect to landing CDN asset
//
// Compliance: link 72h + one-time use protegge il lead magnet da
// condivisione virale che annulla il valore dell'email gate.

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

const VALID_FILE_SLUGS = [
  'informativa-privacy',
  'registro-trattamenti',
  'consenso-art9-sanitario',
  'guida-gdpr-pmi',
] as const;
type FileSlug = (typeof VALID_FILE_SLUGS)[number];

const FILE_TO_PATH: Record<FileSlug, string> = {
  'informativa-privacy': 'informativa-privacy.docx',
  'registro-trattamenti': 'registro-trattamenti.xlsx',
  'consenso-art9-sanitario': 'consenso-art9-sanitario.pdf',
  'guida-gdpr-pmi': 'guida-gdpr-pmi.html',
};

const ASSET_BASE_URL = 'https://fluxion-landing.pages.dev/assets/gdpr';

interface DownloadToken {
  email: string;
  file_slug: FileSlug;
  expires_at: string;
  used: boolean;
  used_at: string | null;
  created_at: string;
}

function isValidFileSlug(value: string): value is FileSlug {
  return (VALID_FILE_SLUGS as readonly string[]).includes(value);
}

function expiredHtml(message: string): string {
  return `<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Link non valido — FLUXION</title>
  <style>
    body { margin:0; padding:0; background:#f5f5f7; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }
    .wrap { max-width:480px; margin:60px auto; padding:32px; background:#fff; border-radius:12px; border:1px solid #e5e5e7; text-align:center; }
    h1 { color:#1a1a1a; font-size:22px; margin:0 0 12px; }
    p { color:#555; line-height:1.6; margin:8px 0; }
    a.btn { display:inline-block; margin-top:16px; padding:12px 24px; background:#3b82f6; color:#fff; text-decoration:none; border-radius:8px; font-weight:600; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Link non valido o scaduto</h1>
    <p>${message}</p>
    <p>I link di download durano <strong>72 ore</strong> e si possono usare una sola volta. Richiedine uno nuovo dalla pagina dei template.</p>
    <a class="btn" href="https://fluxion-landing.pages.dev/#risorse-gdpr">Richiedi nuovo link</a>
  </div>
</body>
</html>`;
}

export async function gdprDownload(c: Context<AppEnv>) {
  const token = c.req.query('token')?.trim() ?? '';
  const fileSlugRaw = c.req.query('file')?.trim() ?? '';

  if (!token || !/^[a-f0-9]{64}$/.test(token)) {
    return c.html(expiredHtml('Token mancante o malformato.'), 400);
  }
  if (!isValidFileSlug(fileSlugRaw)) {
    return c.html(expiredHtml('File richiesto non valido.'), 400);
  }
  const fileSlug: FileSlug = fileSlugRaw;

  // ── Lookup token in KV ─────────────────────────────────────────────
  const tokenKey = `gdpr_token:${token}`;
  const tokenRaw = await c.env.LICENSE_CACHE.get(tokenKey);
  if (!tokenRaw) {
    return c.html(expiredHtml('Il link è scaduto o è già stato usato.'), 410);
  }

  let tokenData: DownloadToken;
  try {
    tokenData = JSON.parse(tokenRaw) as DownloadToken;
  } catch {
    return c.html(expiredHtml('Token corrotto. Richiedine uno nuovo.'), 500);
  }

  // ── Validate ───────────────────────────────────────────────────────
  if (tokenData.file_slug !== fileSlug) {
    return c.html(expiredHtml('Token non corrispondente al file richiesto.'), 400);
  }
  if (tokenData.used === true) {
    return c.html(
      expiredHtml('Questo link è già stato usato. Richiedine uno nuovo.'),
      410,
    );
  }
  const expiresMs = new Date(tokenData.expires_at).getTime();
  if (Number.isNaN(expiresMs) || expiresMs < Date.now()) {
    return c.html(expiredHtml('Il link è scaduto (validità 72 ore).'), 410);
  }

  // ── Mark used (one-time) ───────────────────────────────────────────
  const now = new Date().toISOString();
  const updated: DownloadToken = {
    ...tokenData,
    used: true,
    used_at: now,
  };
  // Keep KV TTL aligned to original expiration (don't extend lifetime)
  const remainingTtl = Math.max(60, Math.floor((expiresMs - Date.now()) / 1000));
  await c.env.LICENSE_CACHE.put(tokenKey, JSON.stringify(updated), {
    expirationTtl: remainingTtl,
  });

  // ── Update lead_event for analytics (best-effort) ──────────────────
  try {
    const eventKey = `lead_event:${tokenData.email}`;
    const eventRaw = await c.env.LICENSE_CACHE.get(eventKey);
    const events = eventRaw ? JSON.parse(eventRaw) : { downloads: [] };
    if (!Array.isArray(events.downloads)) events.downloads = [];
    events.downloads.push({
      file_slug: fileSlug,
      downloaded_at: now,
      ip: c.req.header('cf-connecting-ip') ?? null,
    });
    events.last_activity = now;
    // Keep events for 1 year for conversion analytics
    await c.env.LICENSE_CACHE.put(eventKey, JSON.stringify(events), {
      expirationTtl: 31_536_000,
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.warn(`gdpr-download: failed to log event for ${tokenData.email}: ${msg}`);
  }

  // ── 302 redirect to asset ──────────────────────────────────────────
  const assetUrl = `${ASSET_BASE_URL}/${FILE_TO_PATH[fileSlug]}`;
  console.log(`gdpr-download OK: email=${tokenData.email} file=${fileSlug}`);
  return c.redirect(assetUrl, 302);
}
