// ─── FLUXION Proxy API — Cloudflare Worker ─────────────────────────
// License validation + LLM NLU proxy + Sara trial management
// Zero cost up to ~500 clients (CF free tier)
//
// Endpoints:
//   POST /api/v1/phone-home          — App startup validation
//   POST /api/v1/nlu/chat            — NLU proxy (Groq → Cerebras → OpenRouter)
//   GET  /api/v1/trial-status        — Sara trial check
//   POST /api/v1/webhook/stripe      — Stripe checkout webhook (no auth, own signature)
//   POST /api/v1/rimborso            — Garanzia 30gg refund (no auth, public form)
//   POST /api/v1/lead-magnet         — GDPR template email gate (no auth, public form)
//   GET  /api/v1/gdpr-download       — Signed URL one-time download (no auth, HMAC token)
//   POST /api/v1/consent-log         — Art.59 checkout consent audit (no auth, public)
//   POST /api/v1/diagnostic-report   — S184 α.3.1-F user-initiated diagnostic (no auth, public)
//   GET  /health                     — Health check (no auth)

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import type { AppEnv, Env } from './lib/types';
import { authMiddleware } from './middleware/auth';
import { phoneHome } from './routes/phone-home';
import { nluProxy } from './routes/nlu-proxy';
import { trialStatus } from './routes/trial-status';
import { stripeWebhook } from './routes/stripe-webhook';
import { verifySignature } from './routes/verify-signature';
import { refund } from './routes/refund';
import { leadMagnet } from './routes/lead-magnet';
import { gdprDownload } from './routes/gdpr-download';
import { consentLog } from './routes/consent-log';
import { diagnosticReport } from './routes/diagnostic-report';
import { licenseRecovery } from './routes/license-recovery';
import { licenseValidate } from './routes/license-validate';
import { checkoutSuccess } from './routes/checkout-success';
import {
  listDomains as adminResendList,
  createDomain as adminResendCreate,
  verifyDomain as adminResendVerify,
  getDomain as adminResendGet,
  deleteDomain as adminResendDelete,
} from './routes/admin-resend';
import {
  previewSequenceStep,
  runCronNow,
} from './routes/admin-email-test';
import { getHealthStatus, runHealthNow } from './routes/health-monitor';
import { runEmailSequenceCron } from './scheduled/email-sequence';
import { runHealthCheck } from './scheduled/health-monitor';

const app = new Hono<AppEnv>();

// ── CORS (allow desktop app + landing origins) ─────────────────────
app.use(
  '/api/*',
  cors({
    origin: [
      'tauri://localhost',
      'https://tauri.localhost',
      'http://localhost',
      'https://fluxion-landing.pages.dev',
    ],
    allowMethods: ['GET', 'POST', 'OPTIONS'],
    allowHeaders: ['Authorization', 'Content-Type'],
    maxAge: 86400,
  }),
);

// ── Health check (no auth) ─────────────────────────────────────────
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    service: 'fluxion-proxy',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// ── Stripe webhook (no auth — uses its own HMAC signature) ──────────
app.post('/api/v1/webhook/stripe', stripeWebhook);

// ── Ed25519 signature verify (S291 debug, no auth — bool-only response) ─
app.post('/api/v1/verify', verifySignature);

// ── Refund — Garanzia 30gg (no auth — email + reason in body) ──────
app.post('/api/v1/rimborso', refund);

// ── Lead magnet — GDPR template email gate (no auth — public form) ──
app.post('/api/v1/lead-magnet', leadMagnet);

// ── GDPR signed URL download (no auth — HMAC token validates request) ─
app.get('/api/v1/gdpr-download', gdprDownload);

// ── Consent log — art.59 audit trail (no auth — public form) ────────
app.post('/api/v1/consent-log', consentLog);

// ── Diagnostic report (no auth — broken installs may lack license) ──
// S184 α.3.1-F: rate-limited (5/h IP + 3/h machine_hash), honeypot, Resend forward
app.post('/api/v1/diagnostic-report', diagnosticReport);

// ── License recovery — permanent shareable URL (S295, no auth, HMAC token) ─
// GET /api/v1/license/:email?token={hmac-sha256(LICENSE_RECOVERY_SECRET, email)}
app.get('/api/v1/license/:email', licenseRecovery);

// ── License validate — heartbeat revocation check (R-01-ter, no auth) ─
// POST /api/v1/license/validate {email} → { status: valid|revoked, server_time signed }
// FAIL-OPEN on missing/corrupt KV. Registered BEFORE authMiddleware (no Bearer license).
app.post('/api/v1/license/validate', licenseValidate);

// ── Checkout success page — Stripe success_url target (S295, no auth) ─
// GET /success/:session_id — renders HTML with license payload + recovery link
app.get('/success/:session_id', checkoutSuccess);

// ── Admin: Resend domain management (auth: Bearer ADMIN_API_SECRET) ─
app.get('/admin/resend/domains', adminResendList);
app.post('/admin/resend/domains', adminResendCreate);
app.get('/admin/resend/domains/:id', adminResendGet);
app.post('/admin/resend/domains/:id/verify', adminResendVerify);
app.delete('/admin/resend/domains/:id', adminResendDelete);

// ── Admin: Email sequence test triggers (S188 F-3) ─────────────────
app.post('/admin/email-sequence/preview', previewSequenceStep);
app.post('/admin/email-sequence/run-now', runCronNow);

// ── Admin: Health monitor (S188 F-4) ───────────────────────────────
app.get('/admin/health/status', getHealthStatus);
app.post('/admin/health/run-now', runHealthNow);

// ── Protected routes (require Ed25519 license) ─────────────────────
app.use('/api/v1/*', authMiddleware);

app.post('/api/v1/phone-home', phoneHome);
app.post('/api/v1/nlu/chat', nluProxy);
app.get('/api/v1/trial-status', trialStatus);

// ── 404 fallback ───────────────────────────────────────────────────
app.notFound((c) => {
  return c.json({ error: 'Not found', code: 'NOT_FOUND' }, 404);
});

// ── Error handler ──────────────────────────────────────────────────
app.onError((err, c) => {
  console.error('Worker error:', err.message);
  return c.json(
    { error: 'Internal server error', code: 'INTERNAL_ERROR' },
    500,
  );
});

// ── Scheduled handler — dispatches by cron expression ──────────────
// wrangler.toml [triggers]:
//   "0 9 * * *"   → daily 09:00 UTC → email sequence (F-3)
//   "*/5 * * * *" → every 5 min     → health monitor (F-4)
async function scheduled(
  controller: ScheduledController,
  env: Env,
  ctx: ExecutionContext,
): Promise<void> {
  const cron = controller.cron;

  if (cron === '0 9 * * *') {
    ctx.waitUntil(
      (async () => {
        try {
          await runEmailSequenceCron(env);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : String(err);
          console.error(`[scheduled] email-sequence cron failed: ${msg}`);
        }
      })(),
    );
    return;
  }

  if (cron === '*/5 * * * *') {
    ctx.waitUntil(
      (async () => {
        try {
          await runHealthCheck(env);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : String(err);
          console.error(`[scheduled] health-monitor cron failed: ${msg}`);
        }
      })(),
    );
    return;
  }

  console.warn(`[scheduled] unrecognised cron expression: ${cron}`);
}

export default {
  fetch: app.fetch.bind(app),
  scheduled,
} satisfies ExportedHandler<Env>;
