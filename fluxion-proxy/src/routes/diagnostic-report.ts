// ─── Diagnostic Report — S184 α.3.1-F ──────────────────────────────
// Public POST endpoint. Called from FLUXION desktop "Send report" button.
// Body: { user_email, user_message, diagnostic }
//
// Flow:
//   1. Honeypot check (silent 200 if filled)
//   2. Validate input (email, message, payload schema)
//   3. Rate limit per IP (5/h) + per machine_hash (3/h)
//   4. Generate ticket_id (random 8 hex)
//   5. Save record in KV (TTL 30d) for audit/correlation
//   6. Send Resend email to fluxion.gestionale@gmail.com
//   7. Return { ok, ticket_id }
//
// Privacy: payload is privacy-safe by construction (no PII clienti).
// Auth: NO license required (broken installs may not have license activated).

import type { Context } from 'hono';
import type { AppEnv, Env } from '../lib/types';

interface DiagnosticReportRequest {
  user_email?: string;
  user_message?: string;
  diagnostic?: Record<string, unknown>;
  website?: string; // honeypot (Tauri client never sends this; bot would)
}

interface DiagnosticTicket {
  ticket_id: string;
  user_email: string;
  user_message: string;
  diagnostic: Record<string, unknown>;
  ip: string | null;
  machine_hash: string | null;
  created_at: string;
  email_sent: boolean;
}

const RATE_LIMIT_PER_IP_PER_HOUR = 5;
const RATE_LIMIT_PER_MACHINE_PER_HOUR = 3;
const TICKET_TTL_SECONDS = 60 * 60 * 24 * 30; // 30 days
const MAX_MESSAGE_CHARS = 2_000;
const MAX_DIAGNOSTIC_BYTES = 32_000; // sanity cap

const SUPPORT_EMAIL = 'fluxion.gestionale@gmail.com';

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function getClientIp(c: Context<AppEnv>): string | null {
  return (
    c.req.header('cf-connecting-ip') ||
    c.req.header('x-forwarded-for')?.split(',')[0]?.trim() ||
    null
  );
}

function generateTicketId(): string {
  const buf = new Uint8Array(8);
  crypto.getRandomValues(buf);
  return Array.from(buf)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildSupportEmailHtml(ticket: DiagnosticTicket): string {
  const d = ticket.diagnostic as Record<string, unknown>;
  const get = (k: string): string => {
    const v = d[k];
    if (v == null) return '—';
    if (typeof v === 'object') return escapeHtml(JSON.stringify(v));
    return escapeHtml(String(v));
  };
  const networkObj = d['network'] as Record<string, unknown> | undefined;
  const voiceObj = d['voice'] as Record<string, unknown> | undefined;
  const portsObj = d['ports'] as Record<string, unknown> | undefined;
  const dbCheckObj = d['db_path_check'] as Record<string, unknown> | undefined;

  const safeGetNested = (
    obj: Record<string, unknown> | undefined,
    k: string,
  ): string => {
    if (!obj) return '—';
    const v = obj[k];
    if (v == null) return '—';
    if (typeof v === 'object') return escapeHtml(JSON.stringify(v));
    return escapeHtml(String(v));
  };

  return `<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#111;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f7;padding:20px 16px;">
    <tr><td align="center">
      <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:10px;border:1px solid #e5e5e7;">
        <tr><td style="padding:20px 24px 8px;">
          <h1 style="margin:0;font-size:18px;font-weight:700;">🆘 FLUXION Support — Ticket ${ticket.ticket_id}</h1>
          <p style="margin:8px 0 0;color:#555;font-size:13px;">Ricevuto da <strong>${escapeHtml(ticket.user_email)}</strong> · ${escapeHtml(ticket.created_at)}</p>
        </td></tr>

        <tr><td style="padding:8px 24px;">
          <h2 style="margin:12px 0 4px;font-size:14px;color:#1a1a1a;">Descrizione cliente</h2>
          <pre style="white-space:pre-wrap;background:#f9f9fb;border:1px solid #eee;border-radius:6px;padding:10px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;color:#222;">${escapeHtml(ticket.user_message)}</pre>
        </td></tr>

        <tr><td style="padding:8px 24px;">
          <h2 style="margin:12px 0 4px;font-size:14px;color:#1a1a1a;">Sistema</h2>
          <table cellpadding="4" cellspacing="0" style="font-size:13px;color:#222;border-collapse:collapse;">
            <tr><td><strong>App version</strong></td><td>${get('app_version')}</td></tr>
            <tr><td><strong>OS</strong></td><td>${get('os')} ${get('os_version')} (${get('arch')})</td></tr>
            <tr><td><strong>Locale</strong></td><td>${get('locale')}</td></tr>
            <tr><td><strong>FLUXION_ENV</strong></td><td>${get('fluxion_env')}</td></tr>
            <tr><td><strong>Machine hash</strong></td><td>${get('machine_hash')}</td></tr>
          </table>
        </td></tr>

        <tr><td style="padding:8px 24px;">
          <h2 style="margin:12px 0 4px;font-size:14px;color:#1a1a1a;">Database</h2>
          <table cellpadding="4" cellspacing="0" style="font-size:13px;color:#222;">
            <tr><td><strong>Path</strong></td><td>${get('db_path_anonymized')}</td></tr>
            <tr><td><strong>Size</strong></td><td>${get('db_size_bytes')} bytes</td></tr>
            <tr><td><strong>Cloud sync</strong></td><td>${get('cloud_sync_provider')}</td></tr>
            <tr><td><strong>Free disk</strong></td><td>${get('free_disk_bytes')} bytes</td></tr>
            <tr><td><strong>Tables</strong></td><td>${get('tables_count')}</td></tr>
            <tr><td><strong>Clienti</strong></td><td>${get('clienti_count')}</td></tr>
            <tr><td><strong>Appuntamenti</strong></td><td>${get('appuntamenti_count')}</td></tr>
            <tr><td><strong>Last backup (days)</strong></td><td>${get('last_backup_age_days')}</td></tr>
            <tr><td><strong>DB warning</strong></td><td>${safeGetNested(dbCheckObj, 'warning')}</td></tr>
          </table>
        </td></tr>

        <tr><td style="padding:8px 24px;">
          <h2 style="margin:12px 0 4px;font-size:14px;color:#1a1a1a;">Pre-flight probes</h2>
          <table cellpadding="4" cellspacing="0" style="font-size:13px;color:#222;">
            <tr><td><strong>Network status</strong></td><td>${safeGetNested(networkObj, 'status')} (${safeGetNested(networkObj, 'latency_ms')}ms)</td></tr>
            <tr><td><strong>Network msg</strong></td><td>${safeGetNested(networkObj, 'message')}</td></tr>
            <tr><td><strong>Ports msg</strong></td><td>${safeGetNested(portsObj, 'message')}</td></tr>
            <tr><td><strong>Voice ready</strong></td><td>${safeGetNested(voiceObj, 'ready')} — ${safeGetNested(voiceObj, 'status')}</td></tr>
            <tr><td><strong>Voice error</strong></td><td>${safeGetNested(voiceObj, 'error')}</td></tr>
          </table>
        </td></tr>

        <tr><td style="padding:8px 24px;">
          <h2 style="margin:12px 0 4px;font-size:14px;color:#1a1a1a;">Sentry event IDs</h2>
          <pre style="background:#f9f9fb;border:1px solid #eee;border-radius:6px;padding:10px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:#222;">${get('sentry_event_ids')}</pre>
        </td></tr>

        <tr><td style="padding:8px 24px 24px;">
          <h2 style="margin:12px 0 4px;font-size:14px;color:#1a1a1a;">Raw payload</h2>
          <pre style="background:#f9f9fb;border:1px solid #eee;border-radius:6px;padding:10px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:#444;max-height:300px;overflow:auto;">${escapeHtml(JSON.stringify(ticket.diagnostic, null, 2))}</pre>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>`;
}

async function sendSupportEmail(
  env: Env,
  ticket: DiagnosticTicket,
): Promise<boolean> {
  if (!env.RESEND_API_KEY) {
    console.warn('Diagnostic-report: RESEND_API_KEY not set');
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
        from: 'FLUXION Support <onboarding@resend.dev>',
        to: [SUPPORT_EMAIL],
        reply_to: ticket.user_email,
        subject: `[FLUXION ${ticket.ticket_id}] ${ticket.user_message.slice(0, 60).replace(/\n/g, ' ')}`,
        html: buildSupportEmailHtml(ticket),
      }),
    });
    if (!response.ok) {
      const errBody = await response.text().catch(() => '');
      console.error(
        `Diagnostic-report email failed: HTTP ${response.status} ${errBody.slice(0, 200)}`,
      );
      return false;
    }
    return true;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Diagnostic-report email error: ${message}`);
    return false;
  }
}

export async function diagnosticReport(c: Context<AppEnv>) {
  // ── Parse body ─────────────────────────────────────────────────────
  let body: DiagnosticReportRequest;
  try {
    body = await c.req.json<DiagnosticReportRequest>();
  } catch {
    return c.json({ ok: false, error: 'malformed_json' }, 400);
  }

  // ── Honeypot ───────────────────────────────────────────────────────
  if (body.website && body.website.trim() !== '') {
    console.log(`Diagnostic-report honeypot triggered from IP ${getClientIp(c)}`);
    return c.json({ ok: true, ticket_id: 'silent' }, 200);
  }

  // ── Validation ─────────────────────────────────────────────────────
  const userEmail = body.user_email?.toLowerCase().trim() ?? '';
  const userMessage = (body.user_message ?? '').slice(0, MAX_MESSAGE_CHARS).trim();
  const diagnostic = body.diagnostic ?? {};

  if (!userEmail || !isValidEmail(userEmail)) {
    return c.json({ ok: false, error: 'invalid_email' }, 400);
  }
  if (userMessage.length < 5) {
    return c.json({ ok: false, error: 'message_too_short' }, 400);
  }
  // Sanity cap on diagnostic size
  const diagBytes = JSON.stringify(diagnostic).length;
  if (diagBytes > MAX_DIAGNOSTIC_BYTES) {
    return c.json({ ok: false, error: 'diagnostic_too_large' }, 413);
  }

  const ip = getClientIp(c);
  const machineHash =
    typeof diagnostic['machine_hash'] === 'string'
      ? (diagnostic['machine_hash'] as string).slice(0, 32)
      : null;

  // ── Rate limit per IP ──────────────────────────────────────────────
  if (ip) {
    const rlKey = `rl_diag_ip:${ip}`;
    const rlRaw = await c.env.LICENSE_CACHE.get(rlKey);
    const rlCount = rlRaw ? parseInt(rlRaw, 10) : 0;
    if (rlCount >= RATE_LIMIT_PER_IP_PER_HOUR) {
      console.log(`Diagnostic-report rate-limit IP ${ip} (count=${rlCount})`);
      return c.json({ ok: false, error: 'rate_limited_ip' }, 429);
    }
    await c.env.LICENSE_CACHE.put(rlKey, String(rlCount + 1), {
      expirationTtl: 3600,
    });
  }

  // ── Rate limit per machine_hash ────────────────────────────────────
  if (machineHash) {
    const rlMachKey = `rl_diag_mach:${machineHash}`;
    const rlMachRaw = await c.env.LICENSE_CACHE.get(rlMachKey);
    const rlMachCount = rlMachRaw ? parseInt(rlMachRaw, 10) : 0;
    if (rlMachCount >= RATE_LIMIT_PER_MACHINE_PER_HOUR) {
      console.log(
        `Diagnostic-report rate-limit machine ${machineHash} (count=${rlMachCount})`,
      );
      return c.json({ ok: false, error: 'rate_limited_machine' }, 429);
    }
    await c.env.LICENSE_CACHE.put(rlMachKey, String(rlMachCount + 1), {
      expirationTtl: 3600,
    });
  }

  // ── Build ticket ───────────────────────────────────────────────────
  const ticket: DiagnosticTicket = {
    ticket_id: generateTicketId(),
    user_email: userEmail,
    user_message: userMessage,
    diagnostic,
    ip,
    machine_hash: machineHash,
    created_at: new Date().toISOString(),
    email_sent: false,
  };

  // ── Send email ─────────────────────────────────────────────────────
  const emailSent = await sendSupportEmail(c.env, ticket);
  ticket.email_sent = emailSent;

  // ── Persist (30d TTL) for audit/correlation ────────────────────────
  await c.env.LICENSE_CACHE.put(`diag:${ticket.ticket_id}`, JSON.stringify(ticket), {
    expirationTtl: TICKET_TTL_SECONDS,
  });

  console.log(
    `Diagnostic-report ticket=${ticket.ticket_id} email=${userEmail} machine=${machineHash ?? 'none'} email_sent=${emailSent}`,
  );

  if (!emailSent) {
    // We still return ok=true to the client — the ticket is saved in KV and we can
    // re-send manually. Returning 500 would scare the user even though we logged it.
    return c.json(
      {
        ok: true,
        ticket_id: ticket.ticket_id,
        warning: 'email_send_failed_but_logged',
      },
      200,
    );
  }

  return c.json({ ok: true, ticket_id: ticket.ticket_id }, 200);
}
