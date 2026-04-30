// ─── Admin: Resend Domain Management ────────────────────────────────
// Temporary CTO endpoint to manage Resend domains via API.
// Auth: Bearer LEAD_MAGNET_SIGNING_SECRET (reused, no new secret needed).
// Endpoints:
//   GET  /admin/resend/domains          — list all domains
//   POST /admin/resend/domains          — create domain { name }
//   POST /admin/resend/domains/:id/verify — trigger DNS verify

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';

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

async function resendCall(env: AppEnv['Bindings'], path: string, init?: RequestInit) {
  const res = await fetch(`https://api.resend.com${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });
  const text = await res.text();
  let body: unknown;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }
  return { status: res.status, body };
}

export async function listDomains(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const r = await resendCall(c.env, '/domains');
  return c.json(r.body, r.status as 200);
}

export async function createDomain(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const { name, region } = (await c.req.json().catch(() => ({}))) as {
    name?: string;
    region?: string;
  };
  if (!name) {
    return c.json({ error: 'name required' }, 400);
  }
  const r = await resendCall(c.env, '/domains', {
    method: 'POST',
    body: JSON.stringify({ name, region: region || 'eu-west-1' }),
  });
  return c.json(r.body, r.status as 200);
}

export async function verifyDomain(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const id = c.req.param('id');
  const r = await resendCall(c.env, `/domains/${id}/verify`, { method: 'POST' });
  return c.json(r.body, r.status as 200);
}

export async function getDomain(c: Context<AppEnv>) {
  if (!checkAuth(c)) return unauthorized();
  const id = c.req.param('id');
  const r = await resendCall(c.env, `/domains/${id}`);
  return c.json(r.body, r.status as 200);
}
