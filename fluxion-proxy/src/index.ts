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

const app = new Hono<AppEnv>();

// ── CORS (allow desktop app origins) ───────────────────────────────
app.use(
  '/api/*',
  cors({
    origin: ['tauri://localhost', 'https://tauri.localhost', 'http://localhost'],
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
