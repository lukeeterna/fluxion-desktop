// ─── Cloudflare Worker Environment Bindings ────────────────────────
export interface Env {
  LICENSE_CACHE: KVNamespace;
  // D1 binding (S291) — webhook events dedup + license payload persistence.
  // Optional: production env may not have D1 yet (rolling deploy). Handler
  // must `if (!env.DB)` and fail-soft to KV-only legacy path.
  DB?: D1Database;
  ED25519_PUBLIC_KEY: string;
  // S291 — Worker license signing (Ed25519 standard, separate from legacy NODE-ED25519).
  // ED25519_PRIVATE_KEY_PKCS8: base64 PKCS8 raw — Worker sign side.
  // ED25519_PUBLIC_KEY_V1: hex 32-byte raw — kid:v1 client verify side.
  ED25519_PRIVATE_KEY_PKCS8?: string;
  ED25519_PUBLIC_KEY_V1?: string;
  GROQ_API_KEY: string;
  CEREBRAS_API_KEY: string;
  OPENROUTER_API_KEY: string;
  STRIPE_WEBHOOK_SECRET: string;
  STRIPE_SECRET_KEY: string;
  RESEND_API_KEY: string;
  LEAD_MAGNET_SIGNING_SECRET: string;
  ENVIRONMENT: string;
  MAX_NLU_CALLS_PER_DAY: string;
  TRIAL_DAYS: string;
  GRACE_PERIOD_DAYS: string;
  REFUND_WINDOW_DAYS: string;
  DMG_DOWNLOAD_URL_MACOS: string;
  ADMIN_API_SECRET: string;
  // Optional — F-4 health monitor alert delivery (Discord webhook URL).
  // Unset → state still tracked in KV, but no alert dispatched.
  DISCORD_HEALTH_WEBHOOK_URL?: string;
  // S295 — HMAC secret for license recovery link tokens.
  // Permanent per-customer shareable URL: /api/v1/license/:email?token={hmac}
  // token = HMAC-SHA256(LICENSE_RECOVERY_SECRET, customer_email_normalized)
  // Set via: wrangler secret put LICENSE_RECOVERY_SECRET --env <test|production>
  LICENSE_RECOVERY_SECRET?: string;
  // S295 — Brevo API key (transactional email).
  // Replaces Resend on production rollout post founder Brevo signup.
  // Fallback to RESEND_API_KEY if BREVO_API_KEY missing (gradual rollout safe).
  BREVO_API_KEY?: string;
}

// ─── Hono Context Variables (set/get in middleware) ─────────────────
export interface Variables {
  license: FluxionLicense;
  cacheEntry: LicenseCacheEntry;
  cacheKey: string;
}

// ─── App type for Hono ─────────────────────────────────────────────
export interface AppEnv {
  Bindings: Env;
  Variables: Variables;
}

// ─── License Types (mirrors Rust/TS structures) ────────────────────
export interface LicenseFeatures {
  voice_agent: boolean;
  whatsapp_ai: boolean;
  rag_chat: boolean;
  fatturazione_pa: boolean;
  loyalty_advanced: boolean;
  api_access: boolean;
  max_verticals: number;
}

export interface FluxionLicense {
  version: string;
  license_id: string;
  tier: 'trial' | 'base' | 'pro' | 'enterprise';
  issued_at: string;
  expires_at: string | null;
  hardware_fingerprint: string;
  licensee_name: string | null;
  licensee_email: string | null;
  enabled_verticals: string[];
  max_operators: number;
  features: LicenseFeatures;
}

export interface SignedLicense {
  license: FluxionLicense;
  signature: string; // base64-encoded Ed25519 signature
}

// ─── KV Cache Types ────────────────────────────────────────────────
export interface LicenseCacheEntry {
  license_id: string;
  tier: string;
  hardware_fingerprint: string;
  verified_at: string; // ISO timestamp
  trial_started_at: string | null;
  nlu_calls_today: number;
  nlu_calls_date: string; // YYYY-MM-DD
  last_phone_home: string; // ISO timestamp
}

// ─── API Response Types ────────────────────────────────────────────
export interface PhoneHomeResponse {
  status: 'ok' | 'expired' | 'revoked' | 'invalid';
  tier: string;
  sara_enabled: boolean;
  sara_days_remaining: number | null;
  server_time: string;
  grace_period_days: number;
}

export interface TrialStatusResponse {
  tier: string;
  sara_enabled: boolean;
  days_remaining: number | null;
  calls_remaining: number;
  calls_today: number;
}

// ─── LLM Provider Config ──────────────────────────────────────────
export interface LLMProvider {
  name: string;
  base_url: string;
  model: string;
  api_key_env: keyof Pick<Env, 'GROQ_API_KEY' | 'CEREBRAS_API_KEY' | 'OPENROUTER_API_KEY'>;
  timeout_ms: number;
  extra_headers?: Record<string, string>;
}

export const LLM_PROVIDERS: LLMProvider[] = [
  {
    name: 'groq',
    base_url: 'https://api.groq.com/openai/v1',
    model: 'llama-3.1-8b-instant',
    api_key_env: 'GROQ_API_KEY',
    timeout_ms: 5000,
  },
  {
    name: 'cerebras',
    base_url: 'https://api.cerebras.ai/v1',
    model: 'llama3.1-8b',
    api_key_env: 'CEREBRAS_API_KEY',
    timeout_ms: 5000,
  },
  {
    name: 'openrouter',
    base_url: 'https://openrouter.ai/api/v1',
    model: 'meta-llama/llama-3.1-8b-instruct:free',
    api_key_env: 'OPENROUTER_API_KEY',
    timeout_ms: 8000,
    extra_headers: {
      'HTTP-Referer': 'https://fluxion.app',
      'X-Title': 'FLUXION',
    },
  },
];
