// ─── FLUXION Email-Based License Activation ─────────────────────────
// The customer's email IS the license key.
// App sends email to CF Worker → Worker checks purchase in KV → returns tier.
// Zero friction: no codes, no keys, no files.

const PROXY_BASE_URL = import.meta.env.VITE_FLUXION_PROXY_URL || 'https://fluxion-proxy.gianlucanewtech.workers.dev';

export interface ActivationResult {
  activated: boolean;
  tier?: string;
  email?: string;
  purchased_at?: string;
  features?: {
    sara_enabled: boolean;
    sara_trial_days: number | null;
    sara_expires_at: string | null;
    whatsapp_ai: boolean;
    loyalty_advanced: boolean;
    fatturazione_sdi: boolean;
    max_verticals: number;
  };
  error?: string;
  hint?: string;
}

/**
 * Activate license by email.
 * The customer enters their purchase email → we verify with the CF Worker.
 */
export async function activateByEmail(email: string): Promise<ActivationResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/activate-by-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.toLowerCase().trim() }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const data = await response.json() as ActivationResult;
    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    const detail = err instanceof Error ? err.message : String(err);
     
    console.error('[activateByEmail] fetch error:', detail, 'URL:', PROXY_BASE_URL);
    return {
      activated: false,
      error: `Impossibile contattare il server (${detail}). Verifica connessione.`,
    };
  }
}
