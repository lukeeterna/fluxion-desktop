# Free LLM Inference Providers — Deep Research (March 2026)

> **Use case**: ~750 structured JSON extraction calls/day, ~200 tokens input, ~80 tokens output each.
> **Requirements**: Fast (~200ms target), Italian language, structured JSON output, FREE, no credit card preferred.
> **Total daily token budget**: ~210,000 tokens/day (750 * 280 avg tokens)

---

## Ranked Table: Best to Worst for Voice NLU Extraction

| Rank | Provider | Free Quota | RPM | Latency | JSON Schema | Italian | CC Required | Score |
|------|----------|-----------|-----|---------|-------------|---------|-------------|-------|
| 1 | **Groq** | ~500K-1M tok/day | 30 | ~50ms TTFT | Yes (strict) | Yes | No | **A+** |
| 2 | **Cerebras** | 1M tok/day | 30 | ~30ms TTFT | Yes (strict) | Yes | No | **A+** |
| 3 | **SambaNova** | 200K tok/day | 20-30 | ~80ms TTFT | Yes (func call) | Yes | No | **A** |
| 4 | **Google Gemini Flash** | 250 RPD (Flash) / 1000 RPD (Lite) | 10-15 | ~150ms | Yes (response_schema) | Excellent | No | **A-** |
| 5 | **Mistral** | 1B tok/month free | ~1 RPS | ~200ms | Yes (JSON mode) | Excellent | No | **A-** |
| 6 | **Cloudflare Workers AI** | 10K neurons/day | N/A | ~300ms | Yes (JSON mode) | Yes | No | **B+** |
| 7 | **OpenRouter** | 50-1000 RPD | 20 | Varies | Via provider | Yes | No | **B+** |
| 8 | **Chutes.ai** | Free (beta) | TBD | Varies | Via model | Yes | No | **B** |
| 9 | **GLHF.chat** | Free (beta) | TBD | Varies | Via model | Yes | No | **B** |
| 10 | **Novita.ai** | 2M tok free | TBD | ~200ms | Yes | Yes | No | **B** |
| 11 | **SiliconFlow** | 50-1000 RPD | TBD | ~150ms | Yes | Yes | No | **B** |
| 12 | **DeepSeek** | 5M tok (30 days) | Unlimited | ~300ms | Yes | Yes | No | **B-** |
| 13 | **Together.ai** | $25 free credits | 60 | ~200ms | Yes (JSON schema) | Yes | Yes (for paid) | **B-** |
| 14 | **Fireworks.ai** | $1 free + 10 RPM | 10 | ~150ms | Yes | Yes | Yes (for full) | **C+** |
| 15 | **Kluster.ai** | $5 free credits | TBD | ~200ms | Yes | Yes | No | **C+** |
| 16 | **HuggingFace** | Limited free | Low | ~500ms+ cold | Limited | Yes | No | **C** |
| 17 | **DeepInfra** | Unauth limited | 200 conc. | ~200ms | Yes | Yes | Yes | **C** |
| 18 | **Cohere** | 1000 calls/month | Low | ~300ms | Yes | Limited | No | **C-** |
| 19 | **Replicate** | Limited free runs | Low | ~1s+ cold | Limited | Limited | No | **D** |
| 20 | **Hyperbolic** | Pay-as-you-go only | TBD | ~200ms | Via model | Yes | Yes | **D** |

---

## Detailed Provider Profiles

### 1. Groq (CURRENT - already in use)
- **URL**: https://console.groq.com
- **Free tier**: No credit card. ~500K-1M tokens/day depending on model.
- **Models**: Llama 3.3 70B, Llama 3.1 8B Instant, Mixtral 8x7B, Gemma 7B/2B
- **Best for NLU**: `llama-3.1-8b-instant` (30K TPM, fastest)
- **Structured output**: Full JSON Schema with `strict: true`, tool_use/function calling
- **Latency**: ~50ms TTFT, 300+ tok/s output. Industry-leading speed.
- **Italian**: Good (Llama 3.3 70B excellent, 8B decent)
- **Rate limits**: Model-dependent. 8B: 30K TPM, 30 RPM. 70B: 6K TPM, 30 RPM.
- **Gotchas**: 429 errors during peak hours. Daily token limits vary per model.
- **Verdict**: Excellent. Already battle-tested in Sara pipeline.

### 2. Cerebras
- **URL**: https://cloud.cerebras.ai
- **Free tier**: 1M tokens/day, 30 RPM, 8192 context. No credit card, no waitlist.
- **Models**: Llama 3.3 70B, Llama 3.1 8B, Qwen3 32B, Qwen3 235B, GPT-OSS 120B
- **Best for NLU**: `llama3.1-8b` (fastest) or `qwen3-32b` (best quality)
- **Structured output**: Full JSON Schema with strict mode, tool calling on all 5 models
- **Latency**: ~30ms TTFT, 2268 tok/s on 8B (fastest in the world). 445 tok/s on 70B.
- **Italian**: Good (Llama/Qwen models)
- **Rate limits**: 30 RPM, 1M TPD, 8192 context max on free tier
- **Gotchas**: 8192 context limit (fine for NLU). Strict schema enforcement coming July 2026.
- **Verdict**: BEST alternative to Groq. Faster raw speed, same free tier quality.

### 3. SambaNova
- **URL**: https://cloud.sambanova.ai
- **Free tier**: 200K tokens/day. No credit card.
- **Models**: Llama 3.1 8B/70B/405B, Llama 3.2 1B/3B/11B/90B, Llama 3.3 70B, Qwen 2.5 72B, QwQ 32B
- **Best for NLU**: `llama3.1-8b` (30 RPM) or `llama3.2-3b` (tiny, fast)
- **Structured output**: Function calling + JSON mode supported
- **Latency**: ~80ms TTFT, 637 tok/s on 8B
- **Italian**: Decent (Llama models)
- **Rate limits**: 8B: 30 RPM. 70B: 20 RPM. 405B: 10 RPM. 200K TPD total.
- **Gotchas**: 200K TPD is tight for 750 calls/day (~210K needed). Might need to be careful.
- **Verdict**: Good backup. Tight on daily quota but workable with small models.

### 4. Google Gemini (AI Studio)
- **URL**: https://aistudio.google.com
- **Free tier**: No credit card. Generous but RPD-limited.
  - Gemini 2.5 Flash: 10 RPM, 250 RPD, 250K TPM
  - Gemini 2.5 Flash-Lite: 15 RPM, 1000 RPD
  - Gemini 2.5 Pro: 5 RPM, 100 RPD
- **Best for NLU**: `gemini-2.5-flash-lite` (1000 RPD covers 750 calls/day!)
- **Structured output**: Native `response_schema` with JSON Schema. Best-in-class schema enforcement.
- **Latency**: ~150ms TTFT. Slower than Groq/Cerebras but acceptable.
- **Italian**: Excellent. Google's multilingual training is top-tier.
- **Rate limits**: RPD is the bottleneck. Flash-Lite at 1000 RPD is sufficient.
- **Gotchas**: Google slashed free limits in Dec 2025. Could change again. Resets at midnight PT.
- **Verdict**: Very strong. Flash-Lite covers our 750 calls/day. Best Italian support.

### 5. Mistral (La Plateforme)
- **URL**: https://console.mistral.ai
- **Free tier**: Experiment tier. ~1 RPS, 500K TPM, up to 1B tokens/month. No credit card.
- **Models**: open-mistral-7b, open-mixtral-8x7b, mistral-small, mistral-large (rate-limited)
- **Best for NLU**: `open-mistral-7b` (fastest, good enough for NLU)
- **Structured output**: JSON mode supported. Function calling available.
- **Latency**: ~200ms. Not as fast as Groq/Cerebras.
- **Italian**: Excellent. Mistral is a French company with strong European language support.
- **Rate limits**: ~1 RPS but huge monthly quota (1B tokens). Not for production.
- **Gotchas**: "Experiment" tier = not for production/commercial use technically.
- **Verdict**: Huge quota but slow RPS. Good for batch, not ideal for real-time voice.

### 6. Cloudflare Workers AI
- **URL**: https://developers.cloudflare.com/workers-ai/
- **Free tier**: 10,000 neurons/day. No credit card with Cloudflare free account.
- **Models**: Llama 3.1 (multiple sizes), Mistral 7B, Gemma, GLM-4.7-Flash, Granite 4.0
- **Best for NLU**: `@cf/meta/llama-3.1-8b-instruct` or `@cf/glm/glm-4.7-flash`
- **Structured output**: JSON mode with `response_format` (OpenAI-compatible)
- **Latency**: ~300ms. Edge inference but not specialized hardware.
- **Italian**: Decent (depends on model)
- **Rate limits**: 10K neurons/day. ~200-500 text generation calls depending on model.
- **Gotchas**: "Neurons" pricing is opaque. May not cover 750 calls/day with larger models.
- **Verdict**: Good for light use. May not cover full 750 calls/day quota.

### 7. OpenRouter
- **URL**: https://openrouter.ai
- **Free tier**: Models with `:free` suffix. 20 RPM. 50 RPD (no purchase) or 1000 RPD ($10+ purchased).
- **Models**: DeepSeek R1, Llama 3.3 70B, Gemma 3, Qwen3 Coder, more rotating
- **Best for NLU**: Whatever free model is fastest at the time
- **Structured output**: Depends on underlying provider/model
- **Latency**: Varies by provider routing. Can be unpredictable.
- **Italian**: Depends on model
- **Rate limits**: 50 RPD free (need $10 purchase for 1000 RPD)
- **Gotchas**: 50 RPD without purchase is way too low. Need to buy credits to get 1000 RPD. Failed requests count against quota.
- **Verdict**: Useful as fallback router but 50 RPD free is insufficient.

### 8. Chutes.ai
- **URL**: https://chutes.ai
- **Free tier**: Free during beta. Community capacity.
- **Models**: DeepSeek-R1, Llama 3.1 70B, Qwen 2.5 72B (64K-128K context)
- **Structured output**: Via model capabilities
- **Latency**: Varies (community GPU capacity)
- **Gotchas**: Beta = could change anytime. Reliability unclear.
- **Verdict**: Interesting but unreliable for production voice agent.

### 9. GLHF.chat (Synthetic)
- **URL**: https://glhf.chat
- **Free tier**: Free during beta. Run any HuggingFace model via vLLM.
- **Models**: Any model on HuggingFace that vLLM supports (up to ~640GB VRAM)
- **Structured output**: Via vLLM capabilities
- **Latency**: Varies
- **Gotchas**: Beta = unstable. No SLA.
- **Verdict**: Cool for experimentation, not for production.

### 10. Novita.ai
- **URL**: https://novita.ai
- **Free tier**: 2M tokens free. 5 models permanently free (Llama 3.2 1B, Qwen2.5 7B, GLM-4-9B, GLM-Z1-9B, BGE-M3).
- **Best for NLU**: `qwen2.5-7b-instruct` (free, good for NLU)
- **Structured output**: OpenAI-compatible API
- **Latency**: ~200ms
- **Gotchas**: 2M tokens is a one-time credit, not recurring. Free models are small.
- **Verdict**: Free models are permanently free but limited selection.

### 11. SiliconFlow
- **URL**: https://siliconflow.com
- **Free tier**: $1 free credits. Free model variants available. 50-1000 RPD.
- **Models**: GLM-5, DeepSeek V3.2, Qwen2.5 72B, many Chinese models
- **Best for NLU**: Free Qwen2.5 variant
- **Structured output**: Yes
- **Gotchas**: China-based. May have latency issues from Europe. 50 RPD without purchase.
- **Verdict**: Good if you need Chinese model ecosystem. Latency from Italy may be high.

### 12. DeepSeek
- **URL**: https://platform.deepseek.com
- **Free tier**: 5M tokens free on signup (valid 30 days). No rate limits after that (pay-per-use).
- **Models**: DeepSeek V3.2 (unified chat + reasoning)
- **Structured output**: Yes, JSON mode + function calling
- **Latency**: ~300ms (China-based servers)
- **Italian**: Good (V3.2 is multilingual)
- **Gotchas**: 5M tokens expires in 30 days. After that, paid only ($0.28/M input). China-based = latency from Italy.
- **Verdict**: Great one-time trial. Not sustainable free long-term.

### 13. Together.ai
- **URL**: https://api.together.xyz
- **Free tier**: $25 free credits on signup. 200+ models.
- **Models**: Llama 4 Scout, Llama 3.3, Qwen, Mixtral, DeepSeek, etc.
- **Structured output**: JSON schema mode supported
- **Latency**: ~200ms
- **Gotchas**: $25 credits deplete. Need Build Tier 1 ($5 spend) for full access. Credit card needed for paid.
- **Verdict**: Good trial credits but not permanently free.

### 14. Fireworks.ai
- **URL**: https://fireworks.ai
- **Free tier**: $1 free credits. 10 RPM without payment method.
- **Models**: Llama, Mixtral, DeepSeek, Qwen, etc.
- **Structured output**: Yes, JSON mode + grammar-based decoding
- **Latency**: ~150ms (fast)
- **Gotchas**: $1 credit runs out fast. 10 RPM without card is workable but limited.
- **Verdict**: Fast but not meaningfully free.

### 15-20. Other Providers
- **Kluster.ai**: $5 free credits. Llama 4, Qwen3, DeepSeek. Not permanently free.
- **HuggingFace**: Free serverless inference but cold starts (30s+). Not viable for real-time voice.
- **DeepInfra**: Requires card. Unauthenticated access is IP-rate-limited. Not practical.
- **Cohere**: 1000 calls/month. Not for commercial use on trial key. English-centric.
- **Replicate**: Very limited free runs. Cold starts. Not viable.
- **Hyperbolic**: No real free tier. Pay-as-you-go only.

---

## Recommended Multi-Provider Strategy for Sara NLU

### Primary: Groq (current) + Cerebras (new backup)
Both offer:
- 1M+ tokens/day free
- <100ms latency
- Structured JSON output
- No credit card
- OpenAI-compatible API

### Rotation Strategy (750 calls/day):
```
Provider 1 (primary):  Groq llama-3.1-8b-instant     → 500 calls/day
Provider 2 (overflow): Cerebras llama3.1-8b           → 250 calls/day
Provider 3 (fallback): Gemini Flash-Lite              → 1000 RPD available
Provider 4 (emergency): SambaNova llama3.1-8b         → 200K TPD
Provider 5 (last resort): Mistral open-mistral-7b     → 1B tok/month
```

### Token Math:
- 750 calls * 280 tokens avg = 210,000 tokens/day
- Groq 8B free: ~1M TPD = 3,571 calls/day capacity
- Cerebras free: 1M TPD = 3,571 calls/day capacity
- Combined: 7,142 calls/day capacity = **9.5x headroom**

### Implementation (Python pseudocode):
```python
PROVIDERS = [
    {"name": "groq", "base_url": "https://api.groq.com/openai/v1", "model": "llama-3.1-8b-instant"},
    {"name": "cerebras", "base_url": "https://api.cerebras.ai/v1", "model": "llama3.1-8b"},
    {"name": "gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "gemini-2.5-flash-lite"},
    {"name": "sambanova", "base_url": "https://api.sambanova.ai/v1", "model": "Meta-Llama-3.1-8B-Instruct"},
    {"name": "mistral", "base_url": "https://api.mistral.ai/v1", "model": "open-mistral-7b"},
]

async def nlu_extract(text: str) -> dict:
    for provider in PROVIDERS:
        try:
            return await call_provider(provider, text, timeout=2.0)
        except (RateLimitError, TimeoutError):
            continue
    raise AllProvidersExhaustedError()
```

---

## Key Findings

1. **Groq + Cerebras together give 2M+ free tokens/day** — more than enough for 750 NLU calls.
2. **Cerebras is the #1 alternative** — faster than Groq on 8B models (2268 vs 635 tok/s), same free tier generosity.
3. **Gemini Flash-Lite** is the best "different architecture" backup — 1000 RPD, excellent Italian, native JSON schema.
4. **SambaNova** is tight at 200K TPD but viable as emergency fallback.
5. **Multi-provider rotation eliminates single-point-of-failure** — if Groq is down, Cerebras picks up instantly.
6. **All top 5 providers support OpenAI-compatible API** — minimal code changes to add multi-provider support.
7. **No provider requires a credit card** in the top 5.

## What Changed Since Last Research (groq-structured-nlu-research.md)
- Cerebras launched 1M TPD free tier (was not available before)
- Gemini slashed free limits in Dec 2025 but Flash-Lite still has 1000 RPD
- SambaNova reduced to 200K TPD (was higher)
- Groq limits remain stable
- Mistral experiment tier is generous (1B tok/month) but slow RPS

---

## Sources
- [cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources)
- [Free LLM API Directory (45+ providers)](https://free-llm.com/)
- [Groq Rate Limits](https://console.groq.com/docs/rate-limits)
- [Groq Structured Outputs](https://console.groq.com/docs/structured-outputs)
- [Cerebras Pricing](https://www.cerebras.ai/pricing)
- [Cerebras Rate Limits](https://inference-docs.cerebras.ai/support/rate-limits)
- [Cerebras Structured Outputs](https://inference-docs.cerebras.ai/capabilities/structured-outputs)
- [SambaNova Rate Limits](https://docs.sambanova.ai/cloud/docs/get-started/rate-limits)
- [SambaNova Function Calling](https://docs.sambanova.ai/cloud/docs/capabilities/function-calling)
- [Gemini Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Gemini Structured Outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Mistral Rate Limits](https://docs.mistral.ai/deployment/ai-studio/tier)
- [Mistral Pricing](https://mistral.ai/pricing)
- [Cloudflare Workers AI Pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)
- [Cloudflare Workers AI JSON Mode](https://developers.cloudflare.com/workers-ai/features/json-mode/)
- [OpenRouter Free Models (Mar 2026)](https://costgoat.com/pricing/openrouter-free-models)
- [OpenRouter Rate Limits](https://openrouter.ai/docs/api/reference/limits)
- [Together.ai Pricing](https://www.together.ai/pricing)
- [Fireworks.ai Pricing](https://fireworks.ai/pricing)
- [DeepSeek Pricing](https://api-docs.deepseek.com/quick_start/pricing)
- [Novita.ai Free Models](https://blogs.novita.ai/free-model/)
- [SiliconFlow Rate Limits](https://docs.siliconflow.cn/en/userguide/rate-limits/rate-limit-and-upgradation)
- [Cohere Rate Limits](https://docs.cohere.com/docs/rate-limits)
- [Cerebras vs Groq vs SambaNova Benchmarks](https://intuitionlabs.ai/articles/cerebras-vs-sambanova-vs-groq-ai-chips)
- [Every Free AI API in 2026](https://awesomeagents.ai/tools/free-ai-inference-providers-2026/)
- [15 Free LLM APIs (2026)](https://www.analyticsvidhya.com/blog/2026/01/top-free-llm-apis/)
- [Free AI API Credits 2026 Comparison](https://www.getaiperks.com/en/blogs/27-ai-api-free-tier-credits-2026)
