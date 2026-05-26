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
  const db = new MockD1Database();
  return {
    LICENSE_CACHE: kv as unknown as KVNamespace,
    DB: db as unknown as D1Database,
    ED25519_PUBLIC_KEY: 'c61b3c912cf953e06db979e54b72602da9e3e3cea9554e67a2baa246e7e67d39',
    // ED25519_PRIVATE_KEY_PKCS8 + ED25519_PUBLIC_KEY_V1 not set by default —
    // tests requiring Ed25519 sign/verify must pass overrides via generateTestKeypair().
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
    // S296 — recovery HMAC key for license delivery flow tests.
    // Read from process env if provided (allows custom fixture), else use
    // deterministic fixture value (NOT a credential, only unit-test scoped).
    LICENSE_RECOVERY_SECRET: process.env.FLUXION_TEST_RECOVERY_KEY ?? 'fixture-unit-S296-DETERMINISTIC-rec',
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
  // S296 — for route handlers reading c.req.url / param / query
  url?: string;
  params?: Record<string, string>;
  query?: Record<string, string>;
}

export interface MockContext {
  env: Env;
  req: {
    text: () => Promise<string>;
    json: () => Promise<unknown>;
    header: (name: string) => string | undefined;
    raw: Request;
    url: string;
    param: (name: string) => string | undefined;
    query: (name: string) => string | undefined;
  };
  header: (name: string, value: string) => void;
  html: (body: string, status?: number) => CapturedResponse;
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
  const reqUrl = opts.url ?? 'https://example.com/test';
  const rawReq = new Request(reqUrl, {
    method: 'POST',
    headers: fakeHeaders,
    body: rawBody || undefined,
  });

  const params = opts.params ?? {};
  const query = opts.query ?? {};

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
      url: reqUrl,
      param: (name: string) => params[name],
      query: (name: string) => query[name],
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
    header: (_name: string, _value: string) => {
      // Mock: ignore — tests assert on captured body/status, not headers.
    },
    html: (body: unknown, status = 200) => {
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

// ─── MockD1Database (S291) ───────────────────────────────────────────
// Minimal in-memory D1-compatible binding for stripe-webhook tests.
// Supports the specific SQL queries used by webhook handler:
//   SELECT * FROM webhook_events WHERE event_id = ? LIMIT 1
//   INSERT OR IGNORE INTO webhook_events (...) VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
//   UPDATE webhook_events SET email_sent_at = unixepoch() WHERE event_id = ? AND email_sent_at IS NULL
// NOT a SQL parser — pattern-matches the literal queries.

export interface WebhookEventRow {
  event_id: string;
  session_id: string;
  license_id: string;
  customer_email: string;
  product: string;
  license_payload: string;
  license_signature: string;
  email_sent_at: number | null;
  created_at: number;
}

export class MockD1Database {
  rows = new Map<string, WebhookEventRow>(); // event_id -> row

  prepare(sql: string) {
    const trimmed = sql.trim().replace(/\s+/g, ' ');
    return new MockD1PreparedStatement(this, trimmed);
  }
}

export class MockD1PreparedStatement {
  private bindings: unknown[] = [];

  constructor(private db: MockD1Database, private sql: string) {}

  bind(...values: unknown[]): this {
    this.bindings = values;
    return this;
  }

  async first<T = unknown>(): Promise<T | null> {
    if (/^SELECT \* FROM webhook_events WHERE event_id = \? LIMIT 1$/i.test(this.sql)) {
      const eventId = this.bindings[0] as string;
      const row = this.db.rows.get(eventId);
      return (row as unknown as T) ?? null;
    }

    // S296 license-recovery: lookup by customer_email, most recent first
    if (/SELECT license_id, customer_email, product, license_payload, license_signature, created_at FROM webhook_events WHERE customer_email = \? ORDER BY created_at DESC LIMIT 1/i.test(this.sql)) {
      const email = this.bindings[0] as string;
      const candidates = [...this.db.rows.values()]
        .filter((r) => r.customer_email === email)
        .sort((a, b) => b.created_at - a.created_at);
      if (candidates.length === 0) return null;
      const r = candidates[0];
      return ({
        license_id: r.license_id,
        customer_email: r.customer_email,
        product: r.product,
        license_payload: r.license_payload,
        license_signature: r.license_signature,
        created_at: r.created_at,
      } as unknown as T);
    }

    // S296 checkout-success: lookup by session_id, most recent first
    if (/SELECT license_id, customer_email, product, license_payload, license_signature FROM webhook_events WHERE session_id = \? ORDER BY created_at DESC LIMIT 1/i.test(this.sql)) {
      const sessionId = this.bindings[0] as string;
      const candidates = [...this.db.rows.values()]
        .filter((r) => r.session_id === sessionId)
        .sort((a, b) => b.created_at - a.created_at);
      if (candidates.length === 0) return null;
      const r = candidates[0];
      return ({
        license_id: r.license_id,
        customer_email: r.customer_email,
        product: r.product,
        license_payload: r.license_payload,
        license_signature: r.license_signature,
      } as unknown as T);
    }

    throw new Error(`MockD1 first(): unsupported SQL: ${this.sql}`);
  }

  async run(): Promise<{ meta: { changes: number; last_row_id: number } }> {
    // INSERT OR IGNORE
    if (/^INSERT OR IGNORE INTO webhook_events/i.test(this.sql)) {
      const [eventId, sessionId, licenseId, customerEmail, product, licensePayload, licenseSignature] =
        this.bindings as [string, string, string, string, string, string, string];
      if (this.db.rows.has(eventId)) {
        return { meta: { changes: 0, last_row_id: 0 } };
      }
      this.db.rows.set(eventId, {
        event_id: eventId,
        session_id: sessionId,
        license_id: licenseId,
        customer_email: customerEmail,
        product,
        license_payload: licensePayload,
        license_signature: licenseSignature,
        email_sent_at: null,
        created_at: Math.floor(Date.now() / 1000),
      });
      return { meta: { changes: 1, last_row_id: this.db.rows.size } };
    }

    // UPDATE email_sent_at = unixepoch() WHERE event_id = ? AND email_sent_at IS NULL
    if (/^UPDATE webhook_events SET email_sent_at = unixepoch\(\)/i.test(this.sql)) {
      const eventId = this.bindings[0] as string;
      const row = this.db.rows.get(eventId);
      if (row && row.email_sent_at === null) {
        row.email_sent_at = Math.floor(Date.now() / 1000);
        return { meta: { changes: 1, last_row_id: 0 } };
      }
      return { meta: { changes: 0, last_row_id: 0 } };
    }

    throw new Error(`MockD1 run(): unsupported SQL: ${this.sql}`);
  }
}

// ─── Ed25519 keypair helper (S291) ───────────────────────────────────
// Generates a real Ed25519 keypair via WebCrypto for test isolation.
// PKCS8 base64 + raw public hex format — same as Worker env secrets.

export interface TestKeypair {
  privatePkcs8Base64: string;
  publicHex: string;
}

export async function generateTestKeypair(): Promise<TestKeypair> {
  const kp = await crypto.subtle.generateKey({ name: 'Ed25519' }, true, ['sign', 'verify']) as CryptoKeyPair;
  const pkcs8Buffer = await crypto.subtle.exportKey('pkcs8', kp.privateKey) as ArrayBuffer;
  const rawBuffer = await crypto.subtle.exportKey('raw', kp.publicKey) as ArrayBuffer;

  const pkcs8Bytes = new Uint8Array(pkcs8Buffer);
  let pkcs8Binary = '';
  for (let i = 0; i < pkcs8Bytes.length; i++) pkcs8Binary += String.fromCharCode(pkcs8Bytes[i]);
  const privatePkcs8Base64 = btoa(pkcs8Binary);

  const rawBytes = new Uint8Array(rawBuffer);
  let publicHex = '';
  for (let i = 0; i < rawBytes.length; i++) publicHex += rawBytes[i].toString(16).padStart(2, '0');

  return { privatePkcs8Base64, publicHex };
}
