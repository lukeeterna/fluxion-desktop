// ─── FLUXION Phone Home Client ─────────────────────────────────────
// Contacts the FLUXION Proxy API on startup to validate license,
// check Sara trial status, and cache the result locally.
//
// Grace period: 7 days offline before Sara disables.
// All core gestionale features work WITHOUT phone-home.

const PROXY_BASE_URL = import.meta.env.VITE_FLUXION_PROXY_URL || 'https://fluxion-proxy.gianlucanewtech.workers.dev';
const GRACE_PERIOD_DAYS = 7;
const PHONE_HOME_INTERVAL_MS = 24 * 60 * 60 * 1000; // 24h

// ─── Types ─────────────────────────────────────────────────────────

export interface PhoneHomeResult {
  status: 'ok' | 'expired' | 'revoked' | 'invalid' | 'offline';
  tier: string;
  sara_enabled: boolean;
  sara_days_remaining: number | null;
  server_time: string | null;
  grace_period_days: number;
  from_cache: boolean;
}

interface PhoneHomeCache {
  result: PhoneHomeResult;
  cached_at: string; // ISO timestamp
}

const CACHE_KEY = 'fluxion_phone_home_cache';

// ─── Phone Home ────────────────────────────────────────────────────

/**
 * Perform phone-home license validation.
 * Returns cached result if offline (within grace period).
 *
 * @param licenseToken - Base64-encoded signed license JSON
 */
export async function phoneHome(licenseToken: string): Promise<PhoneHomeResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/phone-home`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${licenseToken}`,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({})) as Record<string, unknown>;
      const code = (errorData.code as string) || 'UNKNOWN';

      // Handle specific error codes
      if (code === 'LICENSE_REVOKED') {
        return {
          status: 'revoked',
          tier: 'none',
          sara_enabled: false,
          sara_days_remaining: 0,
          server_time: null,
          grace_period_days: 0,
          from_cache: false,
        };
      }

      if (code === 'LICENSE_EXPIRED' || code === 'SARA_TRIAL_EXPIRED') {
        return {
          status: 'expired',
          tier: 'base',
          sara_enabled: false,
          sara_days_remaining: 0,
          server_time: null,
          grace_period_days: 0,
          from_cache: false,
        };
      }

      // Other errors — fall through to offline cache
      throw new Error(`Phone-home failed: ${code}`);
    }

    const data = await response.json() as PhoneHomeResult;
    const result: PhoneHomeResult = { ...data, from_cache: false };

    // Cache successful result
    saveCache(result);

    return result;
  } catch (err) {
    clearTimeout(timeoutId);
     
    console.error('[phoneHome] fetch error:', err instanceof Error ? err.message : String(err));
    // Offline or network error — use cached result with grace period
    return getOfflineResult();
  }
}

/**
 * Check Sara trial status without making an NLU call.
 */
export async function checkTrialStatus(licenseToken: string): Promise<{
  sara_enabled: boolean;
  days_remaining: number | null;
  calls_remaining: number;
} | null> {
  const controller2 = new AbortController();
  const timeoutId2 = setTimeout(() => controller2.abort(), 5000);
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/trial-status`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${licenseToken}`,
      },
      signal: controller2.signal,
    });
    clearTimeout(timeoutId2);

    if (!response.ok) return null;
    return await response.json() as {
      sara_enabled: boolean;
      days_remaining: number | null;
      calls_remaining: number;
    };
  } catch {
    clearTimeout(timeoutId2);
    return null;
  }
}

/**
 * Check if phone-home should run (>24h since last successful check).
 */
export function shouldPhoneHome(): boolean {
  const cached = loadCache();
  if (!cached) return true;

  const elapsed = Date.now() - new Date(cached.cached_at).getTime();
  return elapsed > PHONE_HOME_INTERVAL_MS;
}

// ─── License Validate Heartbeat (R-01-ter, Task 3d) ───────────────
// Calls POST /api/v1/license/validate to detect refund/chargeback revocation.
// Reuses GRACE_PERIOD_DAYS (7) offline tolerance + last_validated_at clock guard.
//
//   server "valid"   → update last_validated_at, decision = 'valid'
//   server "revoked" → decision = 'lock' (immediate)
//   offline          → 'valid' if (now - last_validated_at) < 7d, else 'lock'
//   clock rolled back (now < last_validated_at) → 'lock'
// Pre-lock banner when <2 days of grace remain: caller surfaces warning_days.
// NEVER a silent lock — caller MUST render warning_days when present.

const VALIDATE_CACHE_KEY = 'fluxion_license_validate_last_ok';
const VALIDATE_GRACE_WARN_DAYS = 2;

export interface LicenseValidateResult {
  decision: 'valid' | 'lock';
  source: 'online' | 'offline';
  status: 'valid' | 'revoked' | 'offline';
  /** Days of grace remaining (offline path). When <=2 → caller shows reconnect banner. */
  warning_days: number | null;
  last_validated_at: string | null;
}

interface ValidateServerResponse {
  status: 'valid' | 'revoked';
  server_time: string;
  server_time_sig: string | null;
  refunded_at: string | null;
}

function loadValidateLastOk(): string | null {
  try {
    return localStorage.getItem(VALIDATE_CACHE_KEY);
  } catch {
    return null;
  }
}

function saveValidateLastOk(iso: string): void {
  try {
    localStorage.setItem(VALIDATE_CACHE_KEY, iso);
  } catch {
    /* localStorage unavailable */
  }
}

/**
 * Heartbeat license validation against /license/validate.
 * @param email - Customer email (license-bound identity).
 */
export async function validateLicenseHeartbeat(email: string): Promise<LicenseValidateResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/license/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`validate failed: HTTP ${response.status}`);
    }

    const data = (await response.json()) as ValidateServerResponse;

    if (data.status === 'revoked') {
      return {
        decision: 'lock',
        source: 'online',
        status: 'revoked',
        warning_days: null,
        last_validated_at: loadValidateLastOk(),
      };
    }

    // "valid" → persist last_validated_at (server_time preferred — authoritative clock).
    const nowIso = data.server_time || new Date().toISOString();
    saveValidateLastOk(nowIso);
    return {
      decision: 'valid',
      source: 'online',
      status: 'valid',
      warning_days: null,
      last_validated_at: nowIso,
    };
  } catch (err) {
    clearTimeout(timeoutId);
    console.error('[validateLicenseHeartbeat] offline/error:', err instanceof Error ? err.message : String(err));
    return evaluateOfflineGrace();
  }
}

/**
 * Offline grace evaluation + clock-rollback guard.
 * Allows operation if last successful validate was within GRACE_PERIOD_DAYS.
 */
function evaluateOfflineGrace(): LicenseValidateResult {
  const lastOk = loadValidateLastOk();
  if (!lastOk) {
    // Never validated online → allow (first-run grace), no last_validated_at yet.
    return {
      decision: 'valid',
      source: 'offline',
      status: 'offline',
      warning_days: GRACE_PERIOD_DAYS,
      last_validated_at: null,
    };
  }

  const lastMs = new Date(lastOk).getTime();
  const nowMs = Date.now();

  // Clock-rollback guard: now earlier than last validation → suspicious → lock.
  if (Number.isFinite(lastMs) && nowMs < lastMs) {
    return {
      decision: 'lock',
      source: 'offline',
      status: 'offline',
      warning_days: null,
      last_validated_at: lastOk,
    };
  }

  const elapsedDays = (nowMs - lastMs) / (1000 * 60 * 60 * 24);
  if (elapsedDays >= GRACE_PERIOD_DAYS) {
    return {
      decision: 'lock',
      source: 'offline',
      status: 'offline',
      warning_days: 0,
      last_validated_at: lastOk,
    };
  }

  const remaining = Math.max(0, Math.ceil(GRACE_PERIOD_DAYS - elapsedDays));
  return {
    decision: 'valid',
    source: 'offline',
    status: 'offline',
    // Surface warning only when within the pre-lock window (<2 days remaining).
    warning_days: remaining <= VALIDATE_GRACE_WARN_DAYS ? remaining : null,
    last_validated_at: lastOk,
  };
}

// ─── Cache Helpers ─────────────────────────────────────────────────

function saveCache(result: PhoneHomeResult): void {
  const cache: PhoneHomeCache = {
    result,
    cached_at: new Date().toISOString(),
  };
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
  } catch {
    // localStorage might not be available
  }
}

function loadCache(): PhoneHomeCache | null {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as PhoneHomeCache;
  } catch {
    return null;
  }
}

function getOfflineResult(): PhoneHomeResult {
  const cached = loadCache();

  if (!cached) {
    // Never connected — allow Sara for first launch (trial start)
    return {
      status: 'offline',
      tier: 'trial',
      sara_enabled: true,
      sara_days_remaining: 30,
      server_time: null,
      grace_period_days: GRACE_PERIOD_DAYS,
      from_cache: false,
    };
  }

  // Check grace period
  const elapsed = Date.now() - new Date(cached.cached_at).getTime();
  const elapsedDays = Math.floor(elapsed / (1000 * 60 * 60 * 24));

  if (elapsedDays > GRACE_PERIOD_DAYS) {
    // Grace period exceeded — disable Sara
    return {
      ...cached.result,
      status: 'offline',
      sara_enabled: false,
      sara_days_remaining: 0,
      from_cache: true,
    };
  }

  // Within grace period — use cached result
  return {
    ...cached.result,
    status: 'offline',
    from_cache: true,
  };
}
