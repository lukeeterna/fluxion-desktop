# Groq Structured NLU Research — CoVe 2026
> Date: 2026-03-16 | Use case: Replace regex NLU with LLM structured extraction per voice turn

---

## 1. Groq JSON Mode / Structured Output

### Two Modes Available

| Mode | Format | Guarantee | Models |
|------|--------|-----------|--------|
| **JSON Schema** (`json_schema`) | `response_format: {"type": "json_schema", "json_schema": {...}}` | Strict constrained decoding (100% schema adherence with `strict: true`) | `openai/gpt-oss-20b`, `openai/gpt-oss-120b` only |
| **JSON Object** (`json_object`) | `response_format: {"type": "json_object"}` | Valid JSON guaranteed, but NO schema adherence guarantee | ALL models incl. `llama-3.1-8b-instant`, `llama-3.3-70b-versatile` |

### Key Findings

- **`llama-3.1-8b-instant`** and **`llama-3.3-70b-versatile`** support `json_object` mode but NOT `json_schema` strict mode
- Strict `json_schema` mode is limited to OpenAI GPT-OSS models only (20B, 120B)
- `json_object` mode guarantees valid JSON syntax but the model may produce fields/structure that don't match your expected schema
- **Tool use / function calling** is also supported on llama models — can be used as alternative structured extraction via tool definitions
- Streaming is NOT supported with Structured Outputs
- Cached tokens do not count towards rate limits

### Practical Implication for NLU

With `json_object` mode on llama-3.1-8b-instant:
- Provide a clear system prompt with the exact JSON schema expected
- Include 1-2 few-shot examples in the system prompt
- The model will produce valid JSON ~99%+ of the time with correct structure
- Add a Python `json.loads()` + schema validation fallback (try/except → regex fallback)
- Alternative: Use **tool_use** with a tool definition matching the NLU schema — this forces structured output via function calling

### Recommended Approach

```python
# Option A: json_object mode (simpler)
response_format = {"type": "json_object"}

# Option B: tool_use (more structured, acts like json_schema)
tools = [{
    "type": "function",
    "function": {
        "name": "extract_nlu",
        "description": "Extract intent and entities from user speech",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["PRENOTAZIONE", "CANCELLAZIONE", "FAQ", ...]},
                "entities": {"type": "object", ...},
                "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative", "frustrated"]},
                "requires_escalation": {"type": "boolean"},
                "confidence": {"type": "number"}
            },
            "required": ["intent", "entities", "sentiment", "requires_escalation", "confidence"]
        }
    }
}]
tool_choice = {"type": "function", "function": {"name": "extract_nlu"}}
```

**Recommendation**: Use **tool_use** (Option B) — it provides schema enforcement comparable to json_schema strict mode and works with llama models on Groq.

---

## 2. Groq Free Tier Rate Limits (March 2026)

### Free Plan Limits

| Model | RPM | RPD | TPM | TPD |
|-------|-----|-----|-----|-----|
| `llama-3.1-8b-instant` | 30 | 14,400 | 6,000 | 500,000 |
| `llama-3.3-70b-versatile` | 30 | 1,000 | 12,000 | 100,000 |
| `whisper-large-v3` | 20 | 2,000 | — | — |

### Rate Limit Math for Voice Agent NLU

**Scenario**: Sara handles calls, each call ~10-20 turns, each turn = 1 NLU call

**Using `llama-3.1-8b-instant` (Free tier)**:
- **RPM limit**: 30 req/min → 1 call every 2 seconds → OK for single-call voice agent (human turns ~5-15s)
- **RPD limit**: 14,400 req/day → at 15 turns/call × 50 calls/day = 750 req/day → **well within limit**
- **TPD limit**: 500K tokens/day → at ~150 tokens/turn (prompt+response) × 750 turns = 112,500 tokens → **well within limit**
- **TPM limit**: 6,000 tokens/min → at 150 tokens/turn × 4 concurrent turns = 600 tokens/min → **OK for 1-2 concurrent calls**

**Using `llama-3.3-70b-versatile` (Free tier)**:
- **RPD limit**: 1,000 req/day → 750 req/day is tight, no headroom
- **TPD limit**: 100K tokens → 112,500 tokens/day would EXCEED limit
- **Verdict**: 70B is too constrained on free tier for production NLU

### Answer: Can this run on EVERY turn with Groq free tier?

**YES with `llama-3.1-8b-instant`** for a single-salon deployment (~50 calls/day, ~750 turns/day).

**NO with `llama-3.3-70b-versatile`** — daily token limit too tight.

**At scale (multiple salons)**: Need key rotation or paid tier. With 3 keys on separate orgs = 3× limits = ~2,250 turns/day = ~150 calls/day. Beyond that, Dev tier or Cerebras fallback needed.

---

## 3. Groq Latency Benchmarks

### llama-3.1-8b-instant on Groq LPU

| Metric | Value | Source |
|--------|-------|--------|
| Time to First Token (TTFT) | ~0.13ms (P50) | llm-benchmarks.com, Dec 2025 |
| Output speed | 635 tokens/sec (Artificial Analysis) — 278 tok/s (llm-benchmarks) | Multiple |
| Estimated total for 50-token output | **~80-150ms** (TTFT + 50/635s generation) | Calculated |

### llama-3.3-70b-versatile on Groq LPU

| Metric | Value |
|--------|-------|
| Output speed | ~330 tokens/sec |
| Estimated total for 50-token output | **~200-350ms** |

### Latency Impact vs Current Regex (<5ms)

| Approach | Latency | Delta |
|----------|---------|-------|
| Current regex NLU | <5ms | baseline |
| Groq 8B json_object | ~100-200ms | +100-200ms |
| Groq 70B json_object | ~250-400ms | +250-400ms |
| Groq 8B + network jitter (P95) | ~200-500ms | +200-500ms |

**Impact Assessment**:
- Current Sara pipeline total latency: ~1330ms (STT + NLU + LLM + TTS)
- Adding ~150ms for LLM NLU: total → ~1480ms (+11%)
- This is ACCEPTABLE — NLU replaces regex but runs in parallel with other processing
- **Optimization**: Can run NLU extraction AS the LLM response generation prompt (combine into single call)
- **Best strategy**: Single LLM call does BOTH NLU extraction AND response generation → net latency = 0ms additional

### Is llama-3.1-8b-instant accurate enough for Italian NLU?

- **Intent classification**: YES — 8B models handle classification well, especially with few-shot prompting
- **Entity extraction (names, dates, times)**: YES for common patterns, but Italian quirks (double surnames "De Cillis", phonetic variants) need few-shot examples
- **Sentiment**: YES — basic sentiment is well within 8B capability
- **Recommendation**: Start with 8B, A/B test against regex on 100 real transcripts. If accuracy <95%, upgrade to 70B for entity extraction only

---

## 4. Alternative Free/Cheap Providers

### Provider Comparison (March 2026)

| Provider | Free Tier | RPM | TPD | Structured Output | Latency | Best For |
|----------|-----------|-----|-----|-------------------|---------|----------|
| **Groq** | Yes | 30 | 500K (8B) / 100K (70B) | json_object + tool_use | ~100-200ms (8B) | Primary — fastest TTFT |
| **Cerebras** | Yes | 30 | 1M | json_schema strict + json_object | ~150-300ms | Fallback — highest TPD |
| **Fireworks** | Yes (no CC) | 10 | Unknown | json_schema + grammar mode | ~200-400ms | Backup fallback |
| **Together.ai** | No free tier ($5 min) | — | — | Yes | ~200-400ms | Not viable for zero-cost |
| **OpenRouter** | Free for some models | Varies | Varies | Via underlying provider | Variable | Last resort |

### Cerebras — Strong Alternative

- **Free tier**: 30 RPM, **1M tokens/day** (2× Groq's 8B limit)
- **Models**: Llama 3.3 70B, Qwen3 32B, GPT-OSS 120B
- **Structured output**: Full `json_schema` strict mode support (constrained decoding)
- **Context limit on free**: 8,192 tokens (sufficient for NLU — prompts are ~200 tokens)
- **Latency**: Throughput king (~2600 tok/s on Llama 4 Scout), but higher TTFT than Groq
- **Verdict**: Excellent fallback — more tokens/day, strict schema support, but slightly higher latency

### Recommended Multi-Provider Strategy

```
Primary:   Groq llama-3.1-8b-instant (json_object / tool_use)
Fallback1: Cerebras llama-3.3-70b (json_schema strict) — if Groq rate-limited or down
Fallback2: Fireworks llama-3.1-8b (json_schema) — if both above fail
Emergency: Local regex NLU (current system) — if all APIs fail
```

---

## 5. Key Rotation Strategy

### Critical Finding: Organization-Level Limits

> "Rate limits apply at the **organization level**, not individual users. Spending limits are organization-wide and apply to your total monthly usage across all API endpoints and all API keys in your organization."

This means:
- **Multiple API keys in the SAME org** → shares the same limit → NO benefit
- **Multiple API keys across DIFFERENT orgs** (separate email accounts) → each has independent limits

### 3-Key Rotation (3 Separate Orgs)

| Resource | Per Org (Free) | 3 Orgs Combined |
|----------|---------------|-----------------|
| RPM | 30 | 90 |
| RPD | 14,400 | 43,200 |
| TPD | 500,000 | 1,500,000 |

**Implementation**:
```python
import itertools

GROQ_KEYS = [
    {"key": "gsk_org1_...", "org": "org1"},
    {"key": "gsk_org2_...", "org": "org2"},
    {"key": "gsk_org3_...", "org": "org3"},
]

key_cycle = itertools.cycle(GROQ_KEYS)

def get_next_key():
    """Round-robin across orgs to distribute rate limit load."""
    return next(key_cycle)

async def nlu_extract(text: str) -> dict:
    key_info = get_next_key()
    try:
        return await call_groq(text, api_key=key_info["key"])
    except RateLimitError:
        # Try next key
        key_info = get_next_key()
        return await call_groq(text, api_key=key_info["key"])
    except Exception:
        # Fallback to Cerebras
        return await call_cerebras(text)
```

### Effective Limits with 3-Key Rotation + Cerebras Fallback

- **Effective RPM**: 90 (Groq) + 30 (Cerebras) = 120 RPM
- **Effective TPD**: 1.5M (Groq) + 1M (Cerebras) = 2.5M tokens/day
- **Effective RPD**: 43,200 (Groq) + unlimited (Cerebras within TPD)
- **Covers**: ~16,000 voice turns/day = ~1,000 calls/day → **sufficient for 20+ salons**

---

## 6. Downtime & Fallback Strategy

### Groq Downtime Handling

```
                    ┌─────────────┐
                    │ User Turn   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Groq 8B     │ ← Primary (fastest)
                    │ json_object │
                    └──────┬──────┘
                           │ 429 / 500 / timeout >2s
                    ┌──────▼──────┐
                    │ Cerebras    │ ← Fallback (most tokens)
                    │ json_schema │
                    └──────┬──────┘
                           │ fail
                    ┌──────▼──────┐
                    │ Regex NLU   │ ← Emergency (current system)
                    │ <5ms        │
                    └─────────────┘
```

### Timeout Strategy
- Groq call timeout: **2 seconds** — if exceeded, immediately fallback
- Cerebras call timeout: **3 seconds** — if exceeded, regex fallback
- Total NLU budget: **max 3 seconds** before regex fallback kicks in

---

## 7. Architecture Recommendation

### Option A: Separate NLU Call (Simple, Adds Latency)
```
STT → NLU Extract (Groq 8B, ~150ms) → FSM Logic → LLM Response (Groq 70B) → TTS
                                        Total added: ~150ms
```

### Option B: Combined NLU + Response (Zero Added Latency) ← RECOMMENDED
```
STT → Single LLM Call (Groq 70B) → Parse NLU from structured prefix → FSM + TTS
       "Extract intent/entities AND generate response in one call"
       Total added: 0ms (NLU is embedded in existing LLM call)
```

### Option C: Hybrid (Best Accuracy + Speed)
```
STT → Parallel:
        ├── Groq 8B NLU (json_object, ~150ms) → feed to FSM
        └── Groq 70B Response (streaming, ~300ms TTFT) → TTS
       NLU result used to validate/override FSM state
       Total added: 0ms (parallel execution)
```

**Recommendation**: Start with **Option A** for simplicity and measurability. If latency is a problem, migrate to **Option C** (parallel). Option B is elegant but harder to debug.

---

## 8. Summary & Decision Matrix

| Question | Answer |
|----------|--------|
| Can NLU run on EVERY turn with Groq free tier? | **YES** with 8B, single salon (~50 calls/day) |
| Latency impact vs regex? | **+100-200ms** (8B) — acceptable within 1500ms budget |
| Is 8B accurate enough for Italian? | **Likely YES** for intents + common entities; test on 100 real transcripts |
| How to handle downtime? | **Groq → Cerebras → Regex** cascade with 2s/3s timeouts |
| 3-key rotation effective limit? | **90 RPM, 1.5M TPD** — covers ~1,000 calls/day |
| Best structured output mode? | **tool_use** on Groq (schema enforcement) or **json_schema strict** on Cerebras |

### Next Steps
1. Implement NLU extraction with tool_use on Groq 8B
2. Create test harness: 100 real Italian voice transcripts → compare regex vs LLM accuracy
3. Add Cerebras fallback with json_schema strict mode
4. A/B test 8B vs 70B accuracy on entity extraction (names, dates in Italian)
5. Wire into `booking_state_machine.py` as optional NLU layer (feature-flagged)

---

## Sources
- [Groq Structured Outputs Docs](https://console.groq.com/docs/structured-outputs)
- [Groq Rate Limits](https://console.groq.com/docs/rate-limits)
- [Groq Tool Use](https://console.groq.com/docs/tool-use)
- [Groq Model Deprecation](https://console.groq.com/docs/deprecations)
- [Artificial Analysis — Llama 3.1 8B Providers](https://artificialanalysis.ai/models/llama-3-1-instruct-8b/providers)
- [Artificial Analysis — Groq Provider](https://artificialanalysis.ai/providers/groq)
- [LLM Benchmarks — Groq llama-3.1-8b](https://llm-benchmarks.com/models/groq/llama318binstant)
- [Cerebras vs Groq](https://www.cerebras.ai/blog/cerebras-cs-3-vs-groq-lpu)
- [Cerebras Structured Outputs](https://inference-docs.cerebras.ai/capabilities/structured-outputs)
- [Cerebras Free Tier](https://adam.holter.com/cerebras-opens-a-free-1m-tokens-per-day-inference-tier-and-ccerebras-now-offers-free-inference-with-1m-tokens-per-day-real-speed-benchmarks-show-2600-tokens-sec-on-llama4scout-here-are-the-actual-n/)
- [Fireworks Structured Outputs](https://docs.fireworks.ai/structured-responses/structured-response-formatting)
- [Groq Community — Free Tier Limits](https://community.groq.com/t/is-there-a-free-tier-and-what-are-its-limits/790)
- [Groq Community — Rate Limit FAQ](https://community.groq.com/t/what-are-the-rate-limits-for-the-groq-api-for-the-free-and-dev-tier-plans/42)
