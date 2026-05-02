// ─── FLUXION Proxy API — Cloudflare Worker ─────────────────────────
// License validation + LLM NLU proxy + Sara trial management
// Zero cost up to ~500 clients (CF free tier)
//
// Endpoints:
//   POST /api/v1/phone-home          — App startup validation
//   POST /api/v1/nlu/chat            — NLU proxy (Groq → Cerebras → OpenRouter)
//   GET  /api/v1/trial-status        — Sara trial check
//   POST /api/v1/webhook/stripe      — Stripe checkout webhook (no auth, own signature)
//   POST /api/v1/activate-by-email   — Email-based license activation (no auth)
//   POST /api/v1/rimborso            — Garanzia 30gg refund (no auth, public form)
//   POST /api/v1/lead-magnet         — GDPR template email gate (no auth, public form)
//   GET  /api/v1/gdpr-download       — Signed URL one-time download (no auth, HMAC token)
//   POST /api/v1/consent-log         — Art.59 checkout consent audit (no auth, public)
//   POST /api/v1/diagnostic-report   — S184 α.3.1-F user-initiated diagnostic (no auth, public)
//   GET  /health                     — Health check (no auth)

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import type { AppEnv } from './lib/types';
import { authMiddleware } from './middleware/auth';
import { phoneHome } from './routes/phone-home';
import { nluProxy } from './routes/nlu-proxy';
import { trialStatus } from './routes/trial-status';
import { stripeWebhook } from './routes/stripe-webhook';
import { activateByEmail } from './routes/activate-by-email';
import { refund } from './routes/refund';
import { leadMagnet } from './routes/lead-magnet';
import { gdprDownload } from './routes/gdpr-download';
import { consentLog } from './routes/consent-log';
import { diagnosticReport } from './routes/diagnostic-report';
import {
  listDomains as adminResendList,
  createDomain as adminResendCreate,
  verifyDomain as adminResendVerify,
  getDomain as adminResendGet,
  deleteDomain as adminResendDelete,
} from './routes/admin-resend';

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

// ── Email-based activation (no auth — email is the credential) ──────
app.post('/api/v1/activate-by-email', activateByEmail);

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

// ── Admin: Resend domain management (auth: Bearer LEAD_MAGNET_SIGNING_SECRET) ─
app.get('/admin/resend/domains', adminResendList);
app.post('/admin/resend/domains', adminResendCreate);
app.get('/admin/resend/domains/:id', adminResendGet);
app.post('/admin/resend/domains/:id/verify', adminResendVerify);
app.delete('/admin/resend/domains/:id', adminResendDelete);

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

export default app;
