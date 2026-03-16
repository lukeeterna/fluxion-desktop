# Free LLM API Providers 2026 — Comprehensive Research
> Last updated: 2026-03-16
> Purpose: Find every free inference endpoint supporting structured output (JSON mode) for Sara NLU
> Sources: Reddit (blocked by crawler), GitHub curated lists, aggregator sites, official docs

---

## TIER 1 — PRODUCTION-READY FREE PROVIDERS (Structured Output + Fast + Reliable)

### 1. Groq (groq.com)
- **Status**: ALREADY IN USE by Sara (llama-3.3-70b-versatile)
- **Free tier**: No credit card required
- **Rate limits**: ~30 RPM / 15,000 TPM (varies per model), daily caps apply
- **Models**: Llama 3.3 70B, Llama 3.1 8B, Gemma 2 9B, Mixtral 8x7B
- **Structured output**: YES — `response_format: { type: "json_schema", json_schema: {...} }` (100% schema adherence)
- **JSON mode**: YES — `response_format: { type: "json_object" }`
- **Latency**: ~200-400ms (LPU hardware, fastest in market)
- **Italian**: Good (Llama 3.3 70B handles Italian well)
- **API**: OpenAI-compatible
- **Reliability**: HIGH — well-funded ($640M Series D), production-grade
- **Community sentiment**: Universally praised for speed. Rate limits can be tight for free tier.
- **Risk**: Low — backed by substantial VC funding

### 2. Cerebras (cloud.cerebras.ai)
- **Status**: ALREADY IN USE by Sara (rotation)
- **Free tier**: No credit card, 1M tokens/day
- **Rate limits**: 30 RPM, 60,000 TPM, 1M tokens/day
- **Models**: Llama 3.1 8B, Llama 3.3 70B, Qwen 3-32B, Qwen 3-235B, GPT-OSS-120B
- **Structured output**: YES — JSON schema enforcement via response_format
- **Latency**: ~100-300ms (~1000 tok/s for large models — wafer-scale chip)
- **Italian**: Good (Llama 3.3, Qwen 3 excellent for Italian)
- **API**: OpenAI-compatible
- **Reliability**: HIGH — custom silicon, well-funded
- **Community sentiment**: "Insanely fast", free tier generous. Qwen 3-235B is a hidden gem.
- **Risk**: Low — hardware differentiation moat

### 3. Google AI Studio / Gemini API (ai.google.dev)
- **Status**: BEST free tier overall
- **Free tier**: No credit card required
- **Rate limits** (as of 2026):
  - Gemini 2.5 Pro: 5 RPM, 250K TPM, 100 RPD
  - Gemini 2.5 Flash: 10 RPM, 250K TPM, 250 RPD
  - Gemini 2.5 Flash-Lite: 15 RPM, 250K TPM, 1,000 RPD
- **Models**: Gemini 2.5 Pro, Flash, Flash-Lite (1M context window)
- **Structured output**: YES — native JSON schema support
- **Latency**: ~300-500ms (Flash), ~500-800ms (Pro)
- **Italian**: EXCELLENT — Gemini is top-tier for multilingual/Italian
- **API**: Google-native + OpenAI-compatible adapter available
- **Reliability**: VERY HIGH — Google infrastructure
- **Community sentiment**: "Best free tier in the market." Dec 2025 reduced quotas 50-80%.
- **Risk**: Very low — Google can afford to subsidize forever
- **NOTE**: Free tier data may be used to improve Google models. Daily reset at midnight PT.

### 4. SambaNova (cloud.sambanova.ai)
- **Status**: Strong free tier
- **Free tier**: No credit card (free tier auto when no payment method linked)
- **Rate limits**:
  - Llama 3.1 8B: 30 RPM
  - Llama 3.1 70B / 3.3 70B: 20 RPM
  - Llama 3.1 405B: 10 RPM
  - Llama 3.2 90B: 1 RPM (high demand)
- **Bonus**: $5 free credit (~30M tokens on 8B)
- **Models**: Llama 3.1 (8B/70B/405B), Llama 3.2 (1B/3B/11B/90B), Llama 3.3 70B
- **Structured output**: YES — OpenAI-compatible response_format
- **Latency**: ~200-500ms (custom RDU hardware)
- **Italian**: Good (Llama 3.3 70B)
- **API**: OpenAI-compatible
- **Reliability**: HIGH — custom silicon company
- **Community sentiment**: "Fast and generous free tier." 405B access is unique.
- **Risk**: Low — hardware company with enterprise contracts

---

## TIER 2 — VIABLE FREE PROVIDERS (Good but with caveats)

### 5. Mistral (La Plateforme — console.mistral.ai)
- **Free tier**: "Experiment" plan — no credit card, requires phone verification
- **Rate limits**: 2 RPM, 500K TPM, 1B tokens/month
- **Models**: Mistral Large, Mistral Small, Codestral, Pixtral 12B
- **Structured output**: YES — native JSON mode support
- **Latency**: ~300-600ms
- **Italian**: GOOD — Mistral models trained on European languages
- **API**: OpenAI-compatible
- **Reliability**: MEDIUM-HIGH — well-funded French AI company
- **Community sentiment**: "2 RPM is painful for production but fine for dev."
- **Risk**: Low — EU AI champion, strong funding
- **CAVEAT**: 2 RPM makes it impractical for real-time voice agent. Good as fallback only.

### 6. OpenRouter (openrouter.ai)
- **Free tier**: No credit card, community-subsidized free models
- **Rate limits**: ~20 RPM, ~200 RPD for free models
- **Models (free)**: DeepSeek V3, DeepSeek R1, Llama variants, Qwen variants, Gemini Flash, Mistral — ~24-28 free models
- **Structured output**: YES — router filters for models supporting structured output
- **Latency**: Variable (depends on underlying provider)
- **Italian**: Depends on model selected
- **API**: OpenAI-compatible (unified endpoint)
- **Reliability**: MEDIUM — aggregator, depends on upstream providers
- **Community sentiment**: "Great for testing multiple models. Free models can be slow."
- **Risk**: Medium — community-funded free tier could shrink
- **ADVANTAGE**: Single API, many models. Good for A/B testing.

### 7. Cloudflare Workers AI (developers.cloudflare.com/workers-ai)
- **Free tier**: 10,000 neurons/day (no credit card for free plan)
- **Models**: Llama 3.1/3.2 variants, Mistral 7B, DeepSeek-R1-Distill-Qwen-32B, Whisper (STT)
- **Structured output**: YES (via prompt engineering; native JSON mode on select models)
- **Latency**: ~100-300ms (edge deployment, globally distributed)
- **Italian**: Limited (smaller models, 7B-32B range)
- **API**: REST + Workers binding
- **Reliability**: VERY HIGH — Cloudflare infrastructure
- **Community sentiment**: "Great latency due to edge. 10K neurons/day runs out fast with large models."
- **Risk**: Very low — Cloudflare core business subsidizes AI
- **CAVEAT**: 10K neurons/day = ~50-100 requests with large models. Better for small models.

### 8. GitHub Models (github.com/marketplace/models)
- **Free tier**: All GitHub users, no credit card
- **Rate limits**:
  - High-tier (GPT-4o, o1): 10 RPM, 50 RPD
  - Low-tier (Llama, etc.): 15 RPM, 150 RPD
  - 8K input / 4K output tokens per request
- **Models**: GPT-4o, GPT-4.1, o3, Grok-3, DeepSeek-R1, Llama 3.3
- **Structured output**: YES (GPT-4o supports native structured output)
- **Latency**: ~300-600ms
- **Italian**: GOOD (GPT-4o excellent for Italian)
- **API**: Azure AI Inference (OpenAI-compatible)
- **Reliability**: HIGH — Microsoft/GitHub infrastructure
- **Community sentiment**: "Hidden gem. GPT-4o for free is incredible."
- **Risk**: Low — Microsoft subsidized
- **CAVEAT**: 50 RPD for best models is very limited. Good for fallback.

### 9. Together AI (together.ai)
- **Free tier**: Free credits at signup + free models
- **Free models**: DeepSeek R1 Distilled Llama 70B, Llama 3.3 70B Turbo
- **Structured output**: YES — JSON mode support
- **Latency**: ~200-500ms
- **Italian**: Good (Llama 3.3 70B)
- **API**: OpenAI-compatible
- **Reliability**: HIGH — well-funded, 200+ models
- **Community sentiment**: "Good speed, free models competitive."
- **Risk**: Medium — free models may change
- **Startup program**: Up to $50K credits

### 10. Cohere (cohere.com)
- **Free tier**: No credit card, non-commercial use
- **Rate limits**: 20 RPM, 1,000 requests/month
- **Models**: Command R+, Embed 4, Rerank 3.5
- **Structured output**: YES — native JSON mode
- **Latency**: ~400-800ms
- **Italian**: GOOD — Command R+ trained on many languages
- **API**: Cohere-native + OpenAI-compatible
- **Reliability**: HIGH — enterprise-focused company
- **Community sentiment**: "Best for RAG. Free tier too limited for production."
- **Risk**: Low — enterprise contracts fund free tier
- **CAVEAT**: Non-commercial only. 1K/month too low for voice agent.

---

## TIER 3 — SUPPLEMENTARY / NICHE FREE OPTIONS

### 11. Hugging Face Inference API (huggingface.co)
- **Free tier**: Rate-limited, models up to ~10B params
- **Models**: Thousands (community models, Llama, Mistral, etc.)
- **Structured output**: Via prompt engineering only (no native JSON mode on most)
- **Latency**: Variable, cold starts common on unpopular models
- **Italian**: Depends on model
- **Reliability**: MEDIUM — cold starts, rate limits unpredictable
- **Best for**: Specialized/niche models, embeddings
- **Risk**: Low — HF is the "GitHub of AI"

### 12. NVIDIA NIM (build.nvidia.com)
- **Free tier**: 1,000 API credits at signup (+4,000 requestable)
- **Models**: DeepSeek R1/V3.1, Llama variants, Kimi K2.5, Jamba
- **Structured output**: YES — OpenAI-compatible
- **Latency**: ~200-400ms
- **Italian**: Good (large models)
- **Reliability**: HIGH — NVIDIA infrastructure
- **Risk**: Low — credits-based, not unlimited
- **CAVEAT**: Credits deplete; not truly "free tier"

### 13. glhf.chat
- **Free tier**: FREE during beta (open-ended)
- **Models**: Almost any open-source model from Hugging Face (including 405B!)
- **Structured output**: Via prompt engineering
- **Latency**: Variable
- **Italian**: Depends on model
- **API**: OpenAI-compatible
- **Reliability**: LOW-MEDIUM — beta, small company
- **Community sentiment (HN)**: "Amazing for testing any model. Don't rely on it for production."
- **Risk**: HIGH — beta pricing will end eventually

### 14. Chutes.ai
- **Free tier**: Free plan available
- **Models**: Swappable models via single endpoint
- **Structured output**: Via prompt engineering
- **Latency**: Variable
- **Risk**: HIGH — small/unknown company

### 15. Puter.js (developer.puter.com)
- **Free tier**: No API keys, no signup, serverless
- **Models**: 500+ (GPT, Claude, Gemini, Grok, DeepSeek, etc.)
- **How it works**: "User-Pays" model — your app users pay their own AI costs
- **Structured output**: Depends on underlying model
- **Latency**: Variable
- **CAVEAT**: Not suitable for server-side voice agent (browser-only, user-pays model)
- **Risk**: Medium — novel business model

### 16. Hyperbolic AI (hyperbolic.ai)
- **Free tier**: Free base plan for startups/SMEs
- **Models**: Various open-source models
- **Structured output**: YES — OpenAI-compatible
- **Latency**: Competitive
- **Risk**: Medium — newer company

### 17. DeepInfra (deepinfra.com)
- **Free tier**: Limited free credits at signup
- **Models**: 60+ models, cheapest Llama 405B ($0.80/M tokens)
- **Structured output**: YES
- **Latency**: ~200-400ms
- **Risk**: Medium — pay-as-you-go primarily

### 18. Fireworks AI (fireworks.ai)
- **Free tier**: $1 free credits for new users
- **Models**: 33+ models
- **Structured output**: YES — native JSON mode, function calling
- **Latency**: ~100-300ms (very fast)
- **Risk**: Medium — credits deplete quickly

### 19. SiliconFlow (siliconflow.com)
- **Free tier**: Free models available (Qwen, Llama, GLM, BGE)
- **Models**: Open-source focus
- **Structured output**: YES
- **Latency**: Competitive (2.3x faster than competitors in benchmarks)
- **Italian**: Good (Qwen models)
- **Risk**: Medium — Chinese company

---

## BEST MODELS FOR ITALIAN NLU (Ranked)

1. **Qwen 3-235B** (Cerebras free) — 100+ languages, exceptional Italian, best multilingual
2. **Gemini 2.5 Flash** (Google free) — Top-tier Italian, fast, generous free tier
3. **Llama 3.3 70B** (Groq/Cerebras/SambaNova free) — Strong Italian, versatile
4. **Qwen 3-32B** (Cerebras free) — Great Italian, smaller/faster
5. **Mistral Large** (Mistral free) — European company, good Italian (but 2 RPM limit)
6. **GPT-4o** (GitHub Models free) — Excellent Italian (but 50 RPD limit)
7. **Llama 3.1 8B** (Groq/Cerebras/SambaNova free) — Decent Italian, fast, high limits

---

## RECOMMENDED MULTI-PROVIDER ROTATION FOR SARA NLU

### Primary Stack (all free, all support structured output):
```
Priority 1: Groq — Llama 3.3 70B (fastest, already integrated)
Priority 2: Cerebras — Qwen 3-32B or Llama 3.3 70B (fast, generous limits)
Priority 3: Google AI Studio — Gemini 2.5 Flash (best Italian, 250 RPD)
Priority 4: SambaNova — Llama 3.3 70B (20 RPM, solid backup)
Priority 5: Together AI — Llama 3.3 70B Turbo (free model)
Priority 6: OpenRouter — DeepSeek V3 / free model pool
```

### Rotation Strategy:
- Round-robin across Priority 1-3 for normal load
- Fallback to 4-6 on 429 errors
- All support OpenAI-compatible API = minimal code changes
- Total combined free capacity: ~100+ RPM, ~5000+ RPD

### Implementation Notes:
- All providers use OpenAI-compatible `response_format` for structured output
- `json_schema` mode preferred over `json_object` (100% schema adherence)
- Keep provider rotation in `orchestrator.py` with exponential backoff
- Monitor which providers are fastest for Italian specifically

---

## PROVIDERS TO AVOID

| Provider | Reason |
|----------|--------|
| Puter.js | Browser-only, user-pays — not for server-side NLU |
| glhf.chat | Beta will end, unreliable for production |
| Chutes.ai | Unknown company, no track record |
| Cohere | 1K/month too low, non-commercial only |
| OpenAI free | $5 credits expire in 3 months |

---

## KEY INSIGHTS FROM COMMUNITY

1. **Speed hierarchy** (2026): Cerebras > Groq > Fireworks > SambaNova > Together > Google
2. **Free tier generosity**: Google AI Studio > Cerebras > SambaNova > Groq > Mistral
3. **Italian quality**: Gemini > GPT-4o > Qwen 3 > Llama 3.3 > Mistral > DeepSeek
4. **Structured output reliability**: Groq (100% adherence) = Google = Cerebras > others
5. **Sustainability**: Google, Cloudflare, GitHub Models most likely to remain free long-term
6. **Hidden gems**: Cerebras Qwen 3-235B free, GitHub Models GPT-4o free, SambaNova 405B free
7. **Trend**: Free tiers getting MORE generous in 2026 (competition for developer adoption)

---

## GITHUB CURATED LIST
- **cheahjs/free-llm-api-resources**: https://github.com/cheahjs/free-llm-api-resources
  - Actively maintained (last update: Feb 2026)
  - Covers all providers above + gateway platforms
  - Community-contributed, most comprehensive list available

## SOURCES
- https://github.com/cheahjs/free-llm-api-resources
- https://www.analyticsvidhya.com/blog/2026/01/top-free-llm-apis/
- https://awesomeagents.ai/tools/free-ai-inference-providers-2026/
- https://www.getaiperks.com/en/blogs/27-ai-api-free-tier-credits-2026
- https://www.eesel.ai/blog/free-ai-api
- https://www.teamday.ai/blog/best-free-ai-models-openrouter-2026
- https://costgoat.com/pricing/openrouter-free-models
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://console.groq.com/docs/rate-limits
- https://inference-docs.cerebras.ai/support/rate-limits
- https://docs.sambanova.ai/cloud/docs/get-started/rate-limits
- https://docs.mistral.ai/deployment/ai-studio/tier
- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://www.siliconflow.com/articles/en/best-open-source-LLM-for-Italian
- https://www.zilgist.com/2026/02/groq-api-free-tier-rate-limits-best.html
- https://blog.laozhang.ai/en/posts/gemini-api-free-tier
- https://hypereal.tech/a/free-open-source-llm-apis
- https://developer.puter.com/tutorials/free-llm-api/

> **NOTE**: Reddit (reddit.com) is blocked by Anthropic's web crawler, so direct Reddit URLs could not be retrieved.
> The information above is aggregated from official docs, GitHub, and aggregator sites that reference Reddit discussions.
