// ─── FLUXION Phone Home Client ─────────────────────────────────────
// Contacts the FLUXION Proxy API on startup to validate license,
// check Sara trial status, and cache the result locally.
//
// Grace period: 7 days offline before Sara disables.
// All core gestionale features work WITHOUT phone-home.

const PROXY_BASE_URL = 'https://fluxion-proxy.fluxion.workers.dev';
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
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/phone-home`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${licenseToken}`,
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(10000), // 10s timeout
    });

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
  } catch {
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
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/trial-status`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${licenseToken}`,
      },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) return null;
    return await response.json() as {
      sara_enabled: boolean;
      days_remaining: number | null;
      calls_remaining: number;
    };
  } catch {
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
