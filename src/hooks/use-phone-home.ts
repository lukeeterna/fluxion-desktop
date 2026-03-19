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
  type PhoneHomeResult,
} from '../lib/phone-home';

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

export function usePhoneHome(): PhoneHomeState {
  const [result, setResult] = useState<PhoneHomeResult | null>(null);
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

  return {
    result,
    saraEnabled: result?.sara_enabled ?? true, // Default true until phone-home says otherwise
    saraDaysRemaining: result?.sara_days_remaining ?? null,
    isChecking,
    tier: result?.tier ?? 'unknown',
    fromCache: result?.from_cache ?? false,
    refresh: runPhoneHome,
  };
}
