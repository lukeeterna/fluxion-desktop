"""
FLUXION Voice Agent — Multi-Provider LLM Rotation
Zero-cost NLU via Groq, Cerebras, OpenRouter, SambaNova, Google AI Studio.
All OpenAI-compatible APIs — single interface, automatic failover.
"""

import os
import time
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import aiohttp

logger = logging.getLogger("fluxion.nlu.providers")


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""
    name: str
    base_url: str
    model: str
    api_key_env: str           # environment variable name for API key
    timeout_s: float = 2.0
    priority: int = 0          # lower = higher priority

    @property
    def api_key(self) -> Optional[str]:
        return os.environ.get(self.api_key_env)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


# ─────────────────────────────────────────────────────────────────
# Provider registry — ordered by priority (speed + reliability)
# All free tier, no credit card required
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# Default providers — ranked by speed + Italian accuracy
# Groq direct = fastest (~150ms), OpenRouter = most flexible
# Cerebras direct = Qwen3 access (best Italian)
# ─────────────────────────────────────────────────────────────────

DEFAULT_PROVIDERS: List[ProviderConfig] = [
    # S135: Groq-only with higher timeout — Cerebras/OpenRouter too unreliable for VoIP
    ProviderConfig(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.1-8b-instant",
        api_key_env="GROQ_API_KEY",
        timeout_s=3.5,
        priority=0,
    ),
    # Tier 2: Fallbacks (higher timeout, lower priority — only if Groq fails)
    ProviderConfig(
        name="cerebras",
        base_url="https://api.cerebras.ai/v1",
        model="llama3.1-8b",
        api_key_env="CEREBRAS_API_KEY",
        timeout_s=4.0,
        priority=1,
    ),
]


class ProviderRotation:
    """
    Round-robin provider rotation with automatic failover.
    If a provider fails (429, 500, timeout), skip to next.
    All providers use OpenAI-compatible chat completions API.
    """

    def __init__(self, providers: Optional[List[ProviderConfig]] = None):
        all_providers = providers or DEFAULT_PROVIDERS
        # Only keep providers that have API keys configured
        self._providers = sorted(
            [p for p in all_providers if p.is_configured],
            key=lambda p: p.priority,
        )
        self._current_idx = 0
        # Track failures per provider (reset after success)
        self._failures: Dict[str, int] = {}
        self._cooldowns: Dict[str, float] = {}  # provider_name -> cooldown_until timestamp
        self._session: Optional[aiohttp.ClientSession] = None

        if not self._providers:
            logger.warning("[NLU] No LLM providers configured! Set at least GROQ_API_KEY.")
        else:
            names = [p.name for p in self._providers]
            logger.info(f"[NLU] Providers configured: {names}")

    @property
    def has_providers(self) -> bool:
        return len(self._providers) > 0

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _next_provider(self) -> Optional[ProviderConfig]:
        """Get next available provider (skip those in cooldown)."""
        now = time.time()
        for _ in range(len(self._providers)):
            provider = self._providers[self._current_idx]
            self._current_idx = (self._current_idx + 1) % len(self._providers)

            # Skip if in cooldown
            cooldown_until = self._cooldowns.get(provider.name, 0)
            if now < cooldown_until:
                continue

            return provider
        return None

    def _record_failure(self, provider: ProviderConfig):
        """Record failure and set cooldown if too many failures."""
        count = self._failures.get(provider.name, 0) + 1
        self._failures[provider.name] = count
        # Exponential cooldown: 5s, 15s, 30s
        cooldown = min(5 * (2 ** (count - 1)), 30)
        self._cooldowns[provider.name] = time.time() + cooldown
        logger.warning(f"[NLU] Provider {provider.name} failed ({count}x), cooldown {cooldown}s")

    def _record_success(self, provider: ProviderConfig):
        """Reset failure counter on success."""
        self._failures[provider.name] = 0
        self._cooldowns.pop(provider.name, None)

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 200,
    ) -> Optional[Dict[str, Any]]:
        """
        Call LLM via the first available provider.
        Returns parsed tool call arguments (dict) or None if all providers fail.
        """
        if not self._providers:
            return None

        session = await self._get_session()
        tried = set()

        for _ in range(len(self._providers)):
            provider = self._next_provider()
            if provider is None or provider.name in tried:
                break
            tried.add(provider.name)

            try:
                result = await self._call_single(
                    session, provider, messages,
                    temperature, max_tokens,
                )
                if result is not None:
                    self._record_success(provider)
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"[NLU] {provider.name} timeout ({provider.timeout_s}s)")
                self._record_failure(provider)
            except Exception as e:
                logger.warning(f"[NLU] {provider.name} error: {e}")
                self._record_failure(provider)

        logger.error("[NLU] All providers failed!")
        return None

    async def _call_single(
        self,
        session: aiohttp.ClientSession,
        provider: ProviderConfig,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Optional[Dict[str, Any]]:
        """Call a single provider's chat completions endpoint (json_object mode)."""
        url = f"{provider.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        }
        # OpenRouter requires extra headers for free models
        if provider.name.startswith("openrouter"):
            headers["HTTP-Referer"] = "https://fluxion.app"
            headers["X-Title"] = "FLUXION Sara"

        body: Dict[str, Any] = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        timeout = aiohttp.ClientTimeout(total=provider.timeout_s)
        t0 = time.perf_counter()

        async with session.post(url, json=body, headers=headers, timeout=timeout) as resp:
            latency = (time.perf_counter() - t0) * 1000

            if resp.status == 429:
                logger.warning(f"[NLU] {provider.name} rate limited (429)")
                self._record_failure(provider)
                return None

            if resp.status != 200:
                err_text = await resp.text()
                logger.warning(f"[NLU] {provider.name} HTTP {resp.status}: {err_text[:200]}")
                return None

            data = await resp.json()

        # Parse JSON content
        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")

        if content:
            try:
                result = json.loads(content)
                result["_provider"] = provider.name
                result["_latency_ms"] = latency
                result["_model"] = provider.model
                logger.info(
                    f"[NLU] {provider.name}/{provider.model} → "
                    f"intent={result.get('intent')} ({latency:.0f}ms)"
                )
                return result
            except json.JSONDecodeError:
                logger.warning(f"[NLU] {provider.name} invalid JSON: {content[:200]}")
                return None

        logger.warning(f"[NLU] {provider.name} empty response")
        return None
