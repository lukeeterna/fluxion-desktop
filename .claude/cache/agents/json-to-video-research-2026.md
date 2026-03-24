# JSON-to-Video Research 2026 (jsontovideo.org + Google Veo 3.1)
> Research date: 2026-03-23 | CoVe 2026 | Per video demo FLUXION V4

---

## 1. jsontovideo.org — Overview

**What is it**: AI video generator that accepts structured JSON prompts and produces cinematic video clips using Veo 3.1, Seedance 2, Wan 2.6, and Kling 2.6 models.

**Core concept**: Instead of writing vague text prompts, you define structured JSON fields (shot, camera, lighting, audio, duration, aspectRatio) and the AI follows exact instructions.

**Key claim**: "Agencies report going from 10 attempts per shot to 2 attempts — 80% faster with 5x cost savings."

---

## 2. jsontovideo.org — Pricing & Free Tier

### Plans (as of March 2026)

| Plan | Price | Credits/month | Notes |
|------|-------|---------------|-------|
| **Starter** | $6.90/mo (annual) | 300 | Entry level |
| **Plus** | $14.90/mo (annual) | 1,000 | Mid tier |
| **Scale** | $39.90/mo (annual) | 3,000 | High volume |

Alternative pricing found (may be different tiers/pages):
- Basic: 200 credits
- Pro: $29.9/mo — 600 credits
- Enterprise: $59.9/mo — 2,000 credits

### Credit Consumption
- **Full HD (1080p)**: 1 credit per second of video
- **4K (3840x2160)**: 4 credits per second of video
- Additional credits consumed for AI-generated assets (images, voiceovers)

### Credit Math for FLUXION Video (20-30 clips x 5-10 sec each)
- 20 clips x 8 sec average = 160 seconds at 1080p = **160 credits**
- 30 clips x 10 sec = 300 seconds at 1080p = **300 credits**
- At 4K: multiply by 4 = **640-1200 credits**

### What each plan can generate (per model)
| Plan | Sora2 Videos | Veo 3.1 Videos | Pro Veo 3.1 Videos |
|------|-------------|----------------|-------------------|
| 200 credits | 50+ | 20 | 4 |
| 600 credits | 150+ | 60 | 12 |
| 2000 credits | 500+ | 200 | 40 |

### Free Tier
- **NOT confirmed**: No clear "free tier with 1000 credits" found
- Site says "Start for free" but specifics are unclear
- The "1000 credits" appears to be the **Plus plan at $14.90/mo**, NOT a free tier
- json2video.com (different service) gives 600 free credits on signup — may be confused with this

### Watermark
- **Not explicitly confirmed for free tier** — paid plans state "no watermark"
- Likely: free tier has watermark, paid tiers do not

### Commercial Use
- **Not explicitly documented** in search results
- Paid plans likely allow commercial use
- Free tier likely restricted (standard industry practice)

### Resolution
- Supports up to **4K (3840x2160)** on paid plans
- Free tier resolution not specified (likely capped at 720p or 1080p)

---

## 3. jsontovideo.org — JSON Schema

### Schema Structure (approximate, from marketing pages)
```json
{
  "shot": "close-up product reveal",
  "camera": {
    "lens": "35mm",
    "movement": "slow dolly left"
  },
  "lighting": {
    "type": "golden hour",
    "shadows": "soft"
  },
  "audio": {
    "style": "upbeat corporate",
    "bpm": 95
  },
  "duration": 8,
  "aspectRatio": "16:9",
  "subject": "..."
}
```

**Note**: Full API documentation not publicly indexed. The schema includes: shot sequence, camera (lens, movement), lighting specs, audio layers, duration, aspect ratio.

### Supported AI Models
1. **Veo 3.1** — Best for brand consistency, predictable outputs, tight control over camera/lighting/audio
2. **Seedance 2** — Best for creative exploration, varied visual styles, artistic/experimental content
3. **Wan 2.6** — Additional model option
4. **Kling 2.6** — Additional model option

Both Veo 3.1 and Seedance 2 share the same JSON schema — template library works across both.

---

## 4. jsontovideo.org — API Integration

### How to call from Python/Claude
- **REST API**: POST JSON payload, receive video URL
- **No Python SDK yet** (json2video.com has Node.js SDK; Python SDK "in pipeline")
- Can be called from any language via HTTP POST
- Supports webhooks for async video completion

### Integration Workflows
- CMS triggers (Shopify → JSON → video → Instagram)
- Spreadsheet batch (100 rows → 100 JSON prompts → overnight render)
- n8n / Zapier integration
- Direct API: POST JSON → receive video URL → embed

---

## 5. Google Veo 3.1 — Free Access Options

### Option A: Google AI Studio Free Tier
- **~10 video generations per day** (some reports say 3-5 per day)
- **720p resolution** cap (1280x720)
- **5-8 seconds** per clip
- **~50-75 generations per month**
- **Watermark/AI metadata** included
- **Commercial use restricted** on free tier
- Access: https://aistudio.google.com/models/veo-3

### Option B: Google Cloud $300 Free Trial (BEST FOR FLUXION)
- **$300 in free credits** for new Google Cloud accounts
- **Valid for 90 days**
- **No charge until manual upgrade**
- Requires: Google account + billing info (credit card)

#### Veo Pricing on Vertex AI
| Model | Without Audio | With Audio |
|-------|--------------|-----------|
| Veo 3.1 Fast | $0.10/sec | $0.15/sec |
| Veo 3.1 Standard | ~$0.30/sec | $0.40/sec |
| Veo 3.0 | $0.50/sec | $0.75/sec |
| Veo 2 (Vertex) | $0.50/sec | — |
| Veo 2 (Gemini API) | $0.35/sec | — |

#### $300 Free Trial — How Much Video?
| Model | Cost/sec | Seconds for $300 | Minutes |
|-------|----------|-------------------|---------|
| Veo 3.1 Fast (no audio) | $0.10 | 3,000 sec | **50 min** |
| Veo 3.1 Fast (with audio) | $0.15 | 2,000 sec | **33 min** |
| Veo 3.1 Standard (with audio) | $0.40 | 750 sec | **12.5 min** |
| Veo 3.0 (with audio) | $0.75 | 400 sec | **6.7 min** |

**For FLUXION demo video (20-30 clips x 5-10 sec = ~160-300 sec total):**
- Veo 3.1 Fast (no audio): 300 sec x $0.10 = **$30** (well within $300)
- Veo 3.1 Standard (with audio): 300 sec x $0.40 = **$120** (within $300)
- Even with retakes (3x): $90-$360 — mostly within budget

### Option C: Gemini Subscriptions
- **Google AI Pro** ($19.99/mo): ~90 Veo 3.1 Fast videos/month
- **Google AI Ultra** ($249.99/mo): ~2,500 Veo 3.1 Fast videos via Flow

### Option D: Student Plan
- 12-month student plan with Veo access

---

## 6. Verdict: Can We Generate 20-30 Clips for Free?

### jsontovideo.org
- **NO truly free tier with 1000 credits** — the "Start for free" is likely a limited trial
- **Cheapest option**: Starter $6.90/mo = 300 credits = enough for ~300 sec at 1080p
- **Plus $14.90/mo** = 1000 credits = plenty for 20-30 clips at 1080p
- **COST: $6.90-$14.90 one month** — NOT free but very cheap
- **RISK**: Platform is relatively new, unclear ToS on commercial use

### Google Cloud $300 Trial (RECOMMENDED)
- **YES — completely free** for new account
- **Veo 3.1 Fast**: $0.10/sec without audio = 3,000 seconds for $300
- **More than enough** for 20-30 clips even with multiple retakes
- **1080p or 4K** available (not limited to 720p like AI Studio free tier)
- **Commercial use**: Allowed on Vertex AI paid/trial tiers
- **No watermark** on Vertex AI API output
- **REQUIRES**: New Google Cloud account + credit card (won't be charged)

### Google AI Studio Free Tier
- **Technically free** but limited: ~10 clips/day, 720p only, 5-8 sec each
- **Could work** for 20-30 clips over 3 days
- **BUT**: 720p resolution, watermarked, commercial use restricted
- **NOT recommended** for production video

---

## 7. RECOMMENDATION FOR FLUXION VIDEO V4

### Best Strategy (ZERO COST):
1. **Google Cloud $300 free trial** → Vertex AI → Veo 3.1 Fast API
2. Generate 30 clips at 1080p, ~8 sec each = 240 sec x $0.10 = **$24**
3. With retakes (avg 3 attempts): $72 — well within $300
4. Use remaining $228 for additional takes, 4K upgrades, or audio generation
5. **No watermark, commercial use allowed, 1080p/4K quality**

### Alternative (if Google Cloud trial not viable):
1. **jsontovideo.org Plus plan**: $14.90 one month = 1000 credits
2. Generate 30 clips at 1080p = 300 credits
3. 700 credits remaining for retakes
4. Cancel after first month

### Python API Call (Google Vertex AI Veo):
```python
import google.cloud.aiplatform as aiplatform
from google.cloud import aiplatform_v1

# Veo 3.1 video generation via Vertex AI
# Endpoint: generateVideo
# Model: veo-3.1-generate-preview
# Docs: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
```

### Python API Call (jsontovideo.org):
```python
import requests

# POST JSON prompt to jsontovideo.org API
# (Exact endpoint TBD — need to sign up for API docs)
response = requests.post(
    "https://api.jsontovideo.org/v1/generate",  # placeholder
    json={
        "shot": "Software dashboard showing Italian calendar with appointments",
        "camera": {"lens": "50mm", "movement": "slow zoom in"},
        "lighting": {"type": "studio", "shadows": "soft"},
        "duration": 8,
        "aspectRatio": "16:9"
    },
    headers={"Authorization": "Bearer API_KEY"}
)
```

---

## 8. Sources

- [jsontovideo.org — Homepage](https://jsontovideo.org/)
- [jsontovideo.org — Pricing](https://jsontovideo.org/pricing)
- [jsontovideo.org — About](https://jsontovideo.org/about-us)
- [Google Veo 3.1 Gemini API Docs](https://ai.google.dev/gemini-api/docs/video)
- [Veo 3.1 Pricing Guide (aifreeapi.com)](https://www.aifreeapi.com/en/posts/veo-3-1-pricing)
- [Google Cloud Veo 3 Free Trial Offer](https://cloud.google.com/resources/offers/north-america-veo3-trial-offer)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)
- [How to Use Google Veo 3 for Free (Hypereal)](https://hypereal.tech/a/free-google-veo-3)
- [Google Veo Pricing Calculator (CostGoat)](https://costgoat.com/pricing/google-veo)
- [StartupFame — jsontovideo.org profile](https://startupfa.me/s/jsontovideo.org)
