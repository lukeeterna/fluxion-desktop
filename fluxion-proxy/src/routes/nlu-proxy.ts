// ─── NLU Proxy Endpoint ────────────────────────────────────────────
// Proxies LLM NLU requests through FLUXION's CF Worker.
// - Rate limits per license (200 calls/day)
// - Provider fallback chain: Groq → Cerebras → OpenRouter
// - Returns 403 if Sara trial expired (Base tier)

import type { Context } from 'hono';
import type { AppEnv, LLMProvider } from '../lib/types';
import { LLM_PROVIDERS } from '../lib/types';

const LEMONSQUEEZY_PRO_URL =
  'https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702';

export async function nluProxy(c: Context<AppEnv>) {
  const license = c.get('license');
  const cacheEntry = c.get('cacheEntry');
  const cacheKey = c.get('cacheKey');
  const maxCalls = parseInt(c.env.MAX_NLU_CALLS_PER_DAY, 10);
  const trialDays = parseInt(c.env.TRIAL_DAYS, 10);

  // ── Check Sara enablement ────────────────────────────────────────
  if (license.tier === 'trial' || license.tier === 'base') {
    if (cacheEntry.trial_started_at) {
      const startDate = new Date(cacheEntry.trial_started_at);
      const elapsed = Math.floor(
        (Date.now() - startDate.getTime()) / (1000 * 60 * 60 * 24),
      );
      if (elapsed >= trialDays) {
        return c.json(
          {
            error: 'Sara trial expired. Upgrade to Pro for unlimited access.',
            code: 'SARA_TRIAL_EXPIRED',
            upgrade_url: LEMONSQUEEZY_PRO_URL,
            remaining_calls: 0,
          },
          403,
        );
      }
    }
  }

  // ── Rate limiting (KV-based) ─────────────────────────────────────
  const today = new Date().toISOString().slice(0, 10);
  if (cacheEntry.nlu_calls_date !== today) {
    cacheEntry.nlu_calls_date = today;
    cacheEntry.nlu_calls_today = 0;
  }

  if (cacheEntry.nlu_calls_today >= maxCalls) {
    return c.json(
      {
        error: 'Daily NLU call limit reached',
        code: 'RATE_LIMIT_EXCEEDED',
        remaining_calls: 0,
      },
      429,
    );
  }

  // ── Parse NLU request body ───────────────────────────────────────
  let body: Record<string, unknown>;
  try {
    body = await c.req.json<Record<string, unknown>>();
  } catch {
    return c.json({ error: 'Invalid JSON body', code: 'BAD_REQUEST' }, 400);
  }

  // ── Provider fallback chain ──────────────────────────────────────
  let lastError = '';

  for (const provider of LLM_PROVIDERS) {
    const apiKey = c.env[provider.api_key_env];
    if (!apiKey) continue;

    try {
      const result = await callProvider(provider, apiKey, body);
      if (result) {
        // Success — increment counter and save
        cacheEntry.nlu_calls_today++;
        await c.env.LICENSE_CACHE.put(cacheKey, JSON.stringify(cacheEntry), {
          expirationTtl: 86400,
        });

        return c.json({
          ...result,
          _meta: {
            provider: provider.name,
            remaining_calls: maxCalls - cacheEntry.nlu_calls_today,
          },
        });
      }
    } catch (err) {
      lastError = `${provider.name}: ${err instanceof Error ? err.message : 'unknown'}`;
    }
  }

  // All providers failed — signal client to use template fallback
  return c.json(
    {
      error: 'All LLM providers unavailable',
      code: 'ALL_PROVIDERS_FAILED',
      fallback: 'template',
      last_error: lastError,
      remaining_calls: maxCalls - cacheEntry.nlu_calls_today,
    },
    503,
  );
}

// ─── Provider Call ────────────────────────────────────────────────

async function callProvider(
  provider: LLMProvider,
  apiKey: string,
  body: Record<string, unknown>,
): Promise<Record<string, unknown> | null> {
  const headers: Record<string, string> = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
    ...provider.extra_headers,
  };

  const requestBody = {
    ...body,
    model: provider.model,
  };

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), provider.timeout_ms);

  try {
    const response = await fetch(`${provider.base_url}/chat/completions`, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.status === 429 || !response.ok) {
      return null;
    }

    return await response.json() as Record<string, unknown>;
  } catch {
    clearTimeout(timeoutId);
    return null;
  }
}
