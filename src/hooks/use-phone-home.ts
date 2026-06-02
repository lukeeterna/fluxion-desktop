// ═══════════════════════════════════════════════════════════════════
// FLUXION - usePhoneHome Hook
// Runs phone-home on app startup + every 24h interval.
// Provides Sara trial status for UI banners.
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback, useRef } from 'react';
import { invoke } from '@tauri-apps/api/core';
import {
  phoneHome,
  shouldPhoneHome,
  validateLicenseHeartbeat,
  type PhoneHomeResult,
  type LicenseValidateResult,
} from '../lib/phone-home';
import type { LicenseStatus } from '../types/license';

const PHONE_HOME_INTERVAL_MS = 24 * 60 * 60 * 1000; // 24h

export interface PhoneHomeState {
  /** Last phone-home result (null if never ran) */
  result: PhoneHomeResult | null;
  /** Whether Sara AI is currently enabled */
  saraEnabled: boolean;
  /** Days remaining for Sara trial (null = lifetime/no trial) */
  saraDaysRemaining: number | null;
  /** Whether we're currently checking */
  isChecking: boolean;
  /** Current license tier */
  tier: string;
  /** Whether the result came from local cache */
  fromCache: boolean;
  /** Force a phone-home check now */
  refresh: () => Promise<void>;
  /**
   * Result of the anti-refund license validate heartbeat (R-01-ter).
   * null = never ran (no activated license or first boot).
   * decision === 'lock' means the license was revoked (refund/chargeback).
   */
  validateResult: LicenseValidateResult | null;
  /**
   * True when validate heartbeat returned decision === 'lock'.
   * Signals that the app should block Sara and IA features.
   * Derived from validateResult for ergonomic use in components.
   */
  licenseRevoked: boolean;
  /**
   * Days of offline grace remaining before revocation lock kicks in.
   * Non-null only when the offline grace window is ≤2 days.
   * Caller MUST render a "Riconnetti entro N giorni" warning when non-null.
   */
  validateWarningDays: number | null;
}

/**
 * Get the signed license token (base64) from Rust backend.
 * Returns null if no license is activated or command doesn't exist yet.
 */
async function getLicenseToken(): Promise<string | null> {
  try {
    return await invoke<string>('get_license_token_ed25519');
  } catch {
    // Command not yet available or no license — graceful fallback
    return null;
  }
}

/**
 * Get the customer email from the activated license record.
 * Returns null for trial users (no activation) or if unavailable.
 */
async function getLicenseeEmail(): Promise<string | null> {
  try {
    const status = await invoke<LicenseStatus>('get_license_status_ed25519');
    return status.licensee_email ?? null;
  } catch {
    return null;
  }
}

export function usePhoneHome(): PhoneHomeState {
  const [result, setResult] = useState<PhoneHomeResult | null>(null);
  const [validateResult, setValidateResult] = useState<LicenseValidateResult | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const runPhoneHome = useCallback(async () => {
    const token = await getLicenseToken();
    if (!token) {
      // No license token available — skip phone-home silently.
      // All gestionale features work without it.
      return;
    }

    setIsChecking(true);
    try {
      const res = await phoneHome(token);
      setResult(res);

      // S280 Track A — persist phone-home status to SQLite license_cache
      // so that backend `get_license_status_ed25519` sees status='revoked'
      // and `is_valid=false` propagates to all feature/vertical gating.
      // Skip 'offline' (no Worker round-trip happened) — local cache is authoritative.
      if (res.status !== 'offline') {
        try {
          await invoke('sync_license_status_from_phone_home_ed25519', {
            status: res.status,
            tier: res.tier,
            saraEnabled: res.sara_enabled,
            saraDaysRemaining: res.sara_days_remaining,
          });
        } catch {
          // Command not available (older backend) or DB error — silent fallback,
          // localStorage cache still drives UI gating via saraEnabled in this hook.
        }
      }

      // R-01-ter: anti-refund heartbeat — runs alongside phone-home when the
      // customer has an activated license (email present in license_cache).
      const email = await getLicenseeEmail();
      if (email) {
        const vr = await validateLicenseHeartbeat(email);
        setValidateResult(vr);
      }
    } finally {
      setIsChecking(false);
    }
  }, []);

  // Run on mount if needed
  useEffect(() => {
    if (shouldPhoneHome()) {
      runPhoneHome();
    }

    // Set up 24h interval
    intervalRef.current = setInterval(() => {
      runPhoneHome();
    }, PHONE_HOME_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [runPhoneHome]);

  // Revocation lock: true when validate heartbeat says 'lock'.
  // Overrides saraEnabled to disable Sara+IA features on refund/chargeback.
  const licenseRevoked = validateResult?.decision === 'lock';

  return {
    result,
    saraEnabled: licenseRevoked ? false : (result?.sara_enabled ?? true),
    saraDaysRemaining: result?.sara_days_remaining ?? null,
    isChecking,
    tier: result?.tier ?? 'unknown',
    fromCache: result?.from_cache ?? false,
    refresh: runPhoneHome,
    validateResult,
    licenseRevoked,
    validateWarningDays: validateResult?.warning_days ?? null,
  };
}
