// ─── Admin: Health Monitor Endpoints (S188 F-4) ─────────────────────
// Auth: Bearer ADMIN_API_SECRET
//   GET  /admin/health/status   — read latest snapshot from KV
//   POST /admin/health/run-now  — force a probe run + alert evaluation

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';
import { runHealthCheck, readSnapshot } from '../scheduled/health-monitor';

function unauthorized() {
  return new Response(JSON.stringify({ error: 'Unauthorized' }), {
    status: 401,
    headers: { 'Content-Type': 'application/json' },
  });
}

function checkAuth(c: Context<AppEnv>): boolean {
  const auth = c.req.header('Authorization') || '';
  const expected = `Bearer ${c.env.ADMIN_API_SECRET}`;
  return auth === expected;
}

export async function getHealthStatus(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const snap = await readSnapshot(c.env);
  if (!snap) {
    return c.json({ ok: true, snapshot: null, hint: 'no probe run yet' });
  }
  return c.json({ ok: true, snapshot: snap });
}

export async function runHealthNow(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const summary = await runHealthCheck(c.env);
  return c.json({ ok: true, summary });
}
