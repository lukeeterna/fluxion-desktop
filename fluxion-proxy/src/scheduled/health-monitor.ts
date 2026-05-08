// ─── Scheduled Health Monitor — F-4 (S188) ──────────────────────────
// Cron */5 * * * * → check critical surfaces, write KV state, alert on transitions.
//
// Targets monitored from CF Worker (public internet only):
//   1. fluxion-landing.pages.dev (CF Pages)
//   2. fluxion-proxy /health (self, sanity)
//   3. Resend API status (api.resend.com, lightweight HEAD)
//   4. Stripe API status (api.stripe.com)
//
// NOT monitored here (no network reach): iMac voice pipeline 192.168.1.2:3002
// → optional future: heartbeat push pattern from iMac to KV.
//
// Alert delivery: Discord webhook (free, zero-cost). Set via:
//   wrangler secret put DISCORD_HEALTH_WEBHOOK_URL
// If unset → state still tracked in KV, but no notification fires.
//
// State transition policy: alert ONLY on healthy↔down crossings, NOT every check.
// Reduces noise; founder gets one ping per outage start + one per recovery.

import type { Env } from '../lib/types';

const CHECK_TIMEOUT_MS = 8000;

interface ProbeTarget {
  id: string;
  label: string;
  url: string;
  method?: 'GET' | 'HEAD';
  okStatuses?: number[]; // default: 2xx + 3xx
  required: boolean; // if false, failure does not flip overall state
}

const TARGETS: ProbeTarget[] = [
  {
    id: 'landing',
    label: 'Landing page (CF Pages)',
    url: 'https://fluxion-landing.pages.dev/',
    method: 'HEAD',
    required: true,
  },
  // NOTE: self-probe rimosso — CF Workers non instrada self-fetch durante scheduled
  //   invocation (ritorna 404 in ~2ms). Se questo handler gira, il worker è up per
  //   definizione: ridondante. Verificato S189-B (2026-05-08).
  {
    id: 'resend',
    label: 'Resend API',
    url: 'https://api.resend.com',
    method: 'GET',
    okStatuses: [200, 401, 403, 404], // unauthenticated probe — any non-5xx = up
    required: false,
  },
  {
    id: 'stripe',
    label: 'Stripe API',
    url: 'https://api.stripe.com/v1',
    method: 'GET',
    okStatuses: [200, 401, 404], // 401 = auth missing, but server responsive
    required: false,
  },
];

type ProbeOutcome = 'up' | 'down';

interface ProbeResult {
  id: string;
  label: string;
  outcome: ProbeOutcome;
  status?: number;
  durationMs: number;
  error?: string;
  required: boolean;
}

async function probe(target: ProbeTarget): Promise<ProbeResult> {
  const startMs = Date.now();
  const okSet = new Set(target.okStatuses ?? []);
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), CHECK_TIMEOUT_MS);
    const res = await fetch(target.url, {
      method: target.method ?? 'GET',
      signal: ctrl.signal,
      headers: { 'User-Agent': 'fluxion-proxy-health-monitor/1.0' },
    });
    clearTimeout(timer);
    const duration = Date.now() - startMs;
    const isOk =
      okSet.size > 0
        ? okSet.has(res.status)
        : res.status >= 200 && res.status < 400;
    return {
      id: target.id,
      label: target.label,
      outcome: isOk ? 'up' : 'down',
      status: res.status,
      durationMs: duration,
      required: target.required,
    };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      id: target.id,
      label: target.label,
      outcome: 'down',
      durationMs: Date.now() - startMs,
      error: message,
      required: target.required,
    };
  }
}

export type OverallState = 'healthy' | 'degraded' | 'down';

interface HealthSnapshot {
  state: OverallState;
  since: string; // ISO timestamp of last state transition
  last_check: string; // ISO timestamp of latest probe run
  last_results: ProbeResult[];
  consecutive_failures: number; // for hysteresis
}

const HEALTH_KEY = 'health:overall';
const STATE_TTL_SECONDS = 60 * 60 * 24 * 7; // 7 days

// Hysteresis: require N consecutive failures before flipping healthy → down.
// Avoids noisy alerts on transient blips.
const FAILURE_THRESHOLD = 2;

function deriveState(results: ProbeResult[]): OverallState {
  const requiredDown = results.filter((r) => r.required && r.outcome === 'down');
  const optionalDown = results.filter((r) => !r.required && r.outcome === 'down');
  if (requiredDown.length > 0) return 'down';
  if (optionalDown.length > 0) return 'degraded';
  return 'healthy';
}

async function loadSnapshot(env: Env): Promise<HealthSnapshot | null> {
  const raw = await env.LICENSE_CACHE.get(HEALTH_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as HealthSnapshot;
  } catch {
    return null;
  }
}

async function saveSnapshot(env: Env, snap: HealthSnapshot): Promise<void> {
  await env.LICENSE_CACHE.put(HEALTH_KEY, JSON.stringify(snap), {
    expirationTtl: STATE_TTL_SECONDS,
  });
}

interface DiscordEnv {
  DISCORD_HEALTH_WEBHOOK_URL?: string;
}

function buildDiscordPayload(
  prev: OverallState,
  next: OverallState,
  results: ProbeResult[],
): Record<string, unknown> {
  const colors: Record<OverallState, number> = {
    healthy: 0x10b981, // green
    degraded: 0xf59e0b, // amber
    down: 0xef4444, // red
  };
  const emoji: Record<OverallState, string> = {
    healthy: '✅',
    degraded: '⚠️',
    down: '🚨',
  };
  const title =
    next === 'healthy'
      ? `${emoji.healthy} FLUXION recovered (was ${prev})`
      : `${emoji[next]} FLUXION ${next} (was ${prev})`;
  const failed = results.filter((r) => r.outcome === 'down');
  const fields = failed.map((r) => ({
    name: r.label,
    value:
      `\`${r.id}\` — ${r.error ? `error: ${r.error}` : `HTTP ${r.status}`}` +
      ` (${r.durationMs}ms)`,
    inline: false,
  }));
  if (next === 'healthy') {
    fields.push({
      name: 'All probes',
      value: results
        .map((r) => `${r.label}: ${r.outcome === 'up' ? '✅' : '❌'} (${r.durationMs}ms)`)
        .join('\n'),
      inline: false,
    });
  }
  return {
    username: 'FLUXION Health Monitor',
    embeds: [
      {
        title,
        color: colors[next],
        timestamp: new Date().toISOString(),
        fields,
        footer: { text: 'fluxion-proxy / scheduled health check' },
      },
    ],
  };
}

async function notifyDiscord(
  env: Env & DiscordEnv,
  prev: OverallState,
  next: OverallState,
  results: ProbeResult[],
): Promise<void> {
  const url = (env as DiscordEnv).DISCORD_HEALTH_WEBHOOK_URL;
  if (!url) {
    console.log(
      `[health] state ${prev}→${next} — DISCORD_HEALTH_WEBHOOK_URL unset, skipping alert`,
    );
    return;
  }
  try {
    const payload = buildDiscordPayload(prev, next, results);
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.text();
      console.error(`[health] Discord webhook failed (${res.status}): ${body}`);
      return;
    }
    console.log(`[health] Discord alert sent: ${prev}→${next}`);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[health] Discord webhook error: ${message}`);
  }
}

export interface HealthCheckSummary {
  prev: OverallState;
  next: OverallState;
  observed: OverallState; // raw, pre-hysteresis
  changed: boolean;
  consecutive_failures: number;
  results: ProbeResult[];
  durationMs: number;
}

export async function runHealthCheck(
  env: Env & DiscordEnv,
): Promise<HealthCheckSummary> {
  const startMs = Date.now();

  const results = await Promise.all(TARGETS.map(probe));
  const observed = deriveState(results);
  const nowIso = new Date().toISOString();

  const prevSnap = await loadSnapshot(env);
  const prevState: OverallState = prevSnap?.state ?? 'healthy';
  const prevFailures = prevSnap?.consecutive_failures ?? 0;

  // Hysteresis: only flip to down/degraded if observed bad twice in a row.
  // Recovery (→ healthy) is immediate so founder isn't kept guessing.
  let nextState: OverallState;
  let nextFailures: number;

  if (observed === 'healthy') {
    nextState = 'healthy';
    nextFailures = 0;
  } else {
    nextFailures = prevFailures + 1;
    if (nextFailures >= FAILURE_THRESHOLD) {
      nextState = observed;
    } else {
      // Hold previous state until threshold reached.
      nextState = prevState === 'healthy' ? 'healthy' : observed;
    }
  }

  const changed = nextState !== prevState;
  const since = changed ? nowIso : (prevSnap?.since ?? nowIso);

  const snapshot: HealthSnapshot = {
    state: nextState,
    since,
    last_check: nowIso,
    last_results: results,
    consecutive_failures: nextFailures,
  };
  await saveSnapshot(env, snapshot);

  if (changed) {
    await notifyDiscord(env, prevState, nextState, results);
  }

  const summary: HealthCheckSummary = {
    prev: prevState,
    next: nextState,
    observed,
    changed,
    consecutive_failures: nextFailures,
    results,
    durationMs: Date.now() - startMs,
  };

  console.log(
    `[health] check done: state=${nextState} observed=${observed} changed=${changed} failures=${nextFailures} duration=${summary.durationMs}ms`,
  );

  return summary;
}

export async function readSnapshot(env: Env): Promise<HealthSnapshot | null> {
  return loadSnapshot(env);
}
