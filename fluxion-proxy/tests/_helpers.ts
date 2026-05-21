// ─── Test Helpers ────────────────────────────────────────────────────
// Lightweight mock of Hono Context + Cloudflare bindings for unit tests
// of route handlers in isolation (no miniflare / workerd dependency).

import type { Env, FluxionLicense, LicenseCacheEntry } from '../src/lib/types';

// ─── In-memory KV mock ───────────────────────────────────────────────

export interface KvEntry {
  value: string;
  expirationTtl?: number;
}

export class MockKVNamespace {
  store = new Map<string, KvEntry>();

  async get(key: string): Promise<string | null> {
    const entry = this.store.get(key);
    return entry ? entry.value : null;
  }

  async put(
    key: string,
    value: string,
    opts?: { expirationTtl?: number },
  ): Promise<void> {
    this.store.set(key, { value, expirationTtl: opts?.expirationTtl });
  }

  async delete(key: string): Promise<void> {
    this.store.delete(key);
  }

  async list(): Promise<{ keys: { name: string }[] }> {
    return { keys: [...this.store.keys()].map((name) => ({ name })) };
  }

  // Test helpers
  setJson(key: string, obj: unknown, expirationTtl?: number) {
    this.store.set(key, { value: JSON.stringify(obj), expirationTtl });
  }

  getJson<T>(key: string): T | null {
    const entry = this.store.get(key);
    return entry ? (JSON.parse(entry.value) as T) : null;
  }
}

// ─── Env builder ─────────────────────────────────────────────────────

export function makeEnv(overrides: Partial<Env> = {}): Env {
  const kv = new MockKVNamespace();
  return {
    LICENSE_CACHE: kv as unknown as KVNamespace,
    ED25519_PUBLIC_KEY: 'c61b3c912cf953e06db979e54b72602da9e3e3cea9554e67a2baa246e7e67d39',
    GROQ_API_KEY: 'gsk_test',
    CEREBRAS_API_KEY: 'csk_test',
    OPENROUTER_API_KEY: 'or_test',
    STRIPE_WEBHOOK_SECRET: 'whsec_test_secret_S279',
    STRIPE_SECRET_KEY: 'sk_test_S279',
    RESEND_API_KEY: 're_test_S279',
    LEAD_MAGNET_SIGNING_SECRET: 'lm_test',
    ENVIRONMENT: 'test',
    MAX_NLU_CALLS_PER_DAY: '200',
    TRIAL_DAYS: '30',
    GRACE_PERIOD_DAYS: '7',
    REFUND_WINDOW_DAYS: '30',
    DMG_DOWNLOAD_URL_MACOS: 'https://example.com/test.dmg',
    ADMIN_API_SECRET: 'admin_test',
    ...overrides,
  };
}

// ─── License + cacheEntry fixtures ───────────────────────────────────

export function makeLicense(overrides: Partial<FluxionLicense> = {}): FluxionLicense {
  return {
    version: '1.0',
    license_id: 'lic_test_001',
    tier: 'base',
    issued_at: '2026-01-01T00:00:00.000Z',
    expires_at: null,
    hardware_fingerprint: 'hw:test:001',
    licensee_name: 'Test User',
    licensee_email: 'test@example.com',
    enabled_verticals: [],
    max_operators: 5,
    features: {
      voice_agent: false,
      whatsapp_ai: false,
      rag_chat: false,
      fatturazione_pa: false,
      loyalty_advanced: false,
      api_access: false,
      max_verticals: 1,
    },
    ...overrides,
  };
}

export function makeCacheEntry(
  overrides: Partial<LicenseCacheEntry> = {},
): LicenseCacheEntry {
  return {
    license_id: 'lic_test_001',
    tier: 'base',
    hardware_fingerprint: 'hw:test:001',
    verified_at: '2026-05-21T10:00:00.000Z',
    trial_started_at: null,
    nlu_calls_today: 0,
    nlu_calls_date: '2026-05-21',
    last_phone_home: '2026-05-21T10:00:00.000Z',
    ...overrides,
  };
}

// ─── Mock Hono Context ───────────────────────────────────────────────
//
// Minimal subset of `Context<AppEnv>` used by the handlers under test.
// We type as `any` at the boundary to avoid bringing in the full Hono
// type graph (heavy generics) — handlers call only a small surface:
//   c.env, c.get, c.set, c.req.text(), c.req.header(), c.req.json(),
//   c.req.raw, c.json(body, status?)

export interface CapturedResponse {
  status: number;
  body: unknown;
}

export interface MockContextOptions {
  env: Env;
  variables?: {
    license?: FluxionLicense;
    cacheEntry?: LicenseCacheEntry;
    cacheKey?: string;
  };
  headers?: Record<string, string>;
  rawBody?: string;
  jsonBody?: unknown;
  ip?: string;
}

export interface MockContext {
  env: Env;
  req: {
    text: () => Promise<string>;
    json: () => Promise<unknown>;
    header: (name: string) => string | undefined;
    raw: Request;
  };
  get: (key: string) => any;
  set: (key: string, value: any) => void;
  json: (body: unknown, status?: number) => CapturedResponse;
  _captured: CapturedResponse | null;
}

export function makeContext(opts: MockContextOptions): MockContext {
  const variables = new Map<string, unknown>();
  if (opts.variables?.license) variables.set('license', opts.variables.license);
  if (opts.variables?.cacheEntry) variables.set('cacheEntry', opts.variables.cacheEntry);
  if (opts.variables?.cacheKey) variables.set('cacheKey', opts.variables.cacheKey);

  const headers = opts.headers ?? {};
  const rawBody = opts.rawBody ?? (opts.jsonBody !== undefined ? JSON.stringify(opts.jsonBody) : '');

  // Construct a fake Request for `c.req.raw` (used by some handlers for CF headers)
  const fakeHeaders = new Headers(headers);
  if (opts.ip) fakeHeaders.set('CF-Connecting-IP', opts.ip);
  const rawReq = new Request('https://example.com/test', {
    method: 'POST',
    headers: fakeHeaders,
    body: rawBody || undefined,
  });

  const ctx: MockContext = {
    env: opts.env,
    req: {
      text: async () => rawBody,
      json: async () => (opts.jsonBody !== undefined ? opts.jsonBody : JSON.parse(rawBody)),
      header: (name: string) => {
        // case-insensitive lookup
        const lower = name.toLowerCase();
        for (const [k, v] of Object.entries(headers)) {
          if (k.toLowerCase() === lower) return v;
        }
        return undefined;
      },
      raw: rawReq,
    },
    get: (key: string) => variables.get(key),
    set: (key: string, value: unknown) => {
      variables.set(key, value);
    },
    json: (body: unknown, status = 200) => {
      const captured = { status, body };
      ctx._captured = captured;
      return captured;
    },
    _captured: null,
  };

  return ctx;
}

// ─── Stripe signature builder ────────────────────────────────────────
// Produces a valid `Stripe-Signature` header (`t=...,v1=...`) for a
// given payload + secret. Mirrors verifyStripeSignature in stripe-webhook.ts.

export async function buildStripeSignature(
  payload: string,
  secret: string,
  timestamp: number = Math.floor(Date.now() / 1000),
): Promise<string> {
  const encoder = new TextEncoder();
  const signedPayload = `${timestamp}.${payload}`;

  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );

  const sigBytes = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(signedPayload),
  );

  const hex = Array.from(new Uint8Array(sigBytes))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');

  return `t=${timestamp},v1=${hex}`;
}

// ─── Global fetch mock ───────────────────────────────────────────────

export type FetchHandler = (input: Request | string, init?: RequestInit) => Promise<Response>;

export function mockFetch(handler: FetchHandler): () => void {
  const original = globalThis.fetch;
  globalThis.fetch = ((input: any, init?: any) => handler(input, init)) as typeof fetch;
  return () => {
    globalThis.fetch = original;
  };
}
