// ═══════════════════════════════════════════════════════════════════
// FLUXION - Sentry Crash Reporter (S184 α.1.2)
// Frontend integration — no-op se VITE_SENTRY_DSN non configurato
// ═══════════════════════════════════════════════════════════════════

import * as Sentry from "@sentry/react";

/**
 * PII filter (GDPR + memory feedback_e2e_test_mode_only.md)
 * Rimuove dati cliente sensibili prima di inviare evento a Sentry.
 */
function scrubPII(event: Sentry.ErrorEvent): Sentry.ErrorEvent | null {
  // Rimuovi campi italiani sensibili (clienti, telefoni, email, codici fiscali)
  const sensitiveKeys = [
    "cliente",
    "cliente_id",
    "telefono",
    "email",
    "codice_fiscale",
    "partita_iva",
    "indirizzo",
    "nome",
    "cognome",
    "soprannome",
    "data_nascita",
    "xml_sdi",
    "fattura",
    "license_key",
    "stripe_payment_intent",
  ];

  const scrub = (obj: unknown): unknown => {
    if (obj === null || typeof obj !== "object") return obj;
    if (Array.isArray(obj)) return obj.map(scrub);
    const result: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
      const lower = k.toLowerCase();
      if (sensitiveKeys.some((s) => lower.includes(s))) {
        result[k] = "[REDACTED]";
      } else {
        result[k] = scrub(v);
      }
    }
    return result;
  };

  if (event.extra) event.extra = scrub(event.extra) as Record<string, unknown>;
  if (event.contexts) event.contexts = scrub(event.contexts) as typeof event.contexts;
  if (event.breadcrumbs) {
    event.breadcrumbs = event.breadcrumbs.map((bc: Sentry.Breadcrumb) => ({
      ...bc,
      data: bc.data ? (scrub(bc.data) as Record<string, unknown>) : undefined,
    }));
  }
  return event;
}

/**
 * Inizializza Sentry crash reporter.
 * No-op silenzioso se VITE_SENTRY_DSN non configurato (dev locale).
 */
export function initSentry(): void {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (!dsn) {
    // Dev locale o DSN non configurato — no-op
    return;
  }

  Sentry.init({
    dsn,
    environment: import.meta.env.MODE,
    release: __APP_VERSION__,
    // S184 α.1 — SOLO error monitoring (free tier safe, zero cost trial)
    // Tracing/Replay/Profiling disabilitati per garantire zero rischio costi
    tracesSampleRate: 0,
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0,
    integrations: [],
    // PII filter mandatory (GDPR + zero customer data leak)
    beforeSend: scrubPII,
    // Ignora errori noti non azionabili
    ignoreErrors: [
      "ResizeObserver loop limit exceeded",
      "Non-Error promise rejection captured",
      "ChunkLoadError",
    ],
  });
}

export const SentryErrorBoundary = Sentry.ErrorBoundary;
export { Sentry };
