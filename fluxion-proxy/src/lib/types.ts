// ─── Cloudflare Worker Environment Bindings ────────────────────────
export interface Env {
  LICENSE_CACHE: KVNamespace;
  ED25519_PUBLIC_KEY: string;
  GROQ_API_KEY: string;
  CEREBRAS_API_KEY: string;
  OPENROUTER_API_KEY: string;
  ENVIRONMENT: string;
  MAX_NLU_CALLS_PER_DAY: string;
  TRIAL_DAYS: string;
  GRACE_PERIOD_DAYS: string;
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
