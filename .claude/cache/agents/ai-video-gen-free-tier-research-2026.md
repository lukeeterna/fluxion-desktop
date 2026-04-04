# AI Video Generation — Free Tier Deep Research (April 2026)

> **Research date:** 2026-04-03
> **Purpose:** Identify best FREE TIER AI video tools for generating professional 30-60 sec vertical (9:16) marketing videos for Italian PMI
> **Context:** FLUXION Sprint 3 — 9 sector-specific promo videos (parrucchiere, palestra, clinica, officina, estetista, nail artist, barbiere, spa, tatuatore)
> **Prior research:** `ai-video-generation-research-2026.md` (2026-03-23) — this file supersedes it with April 2026 updates

---

## EXECUTIVE SUMMARY

### Major Changes Since March 23 Research

1. **Sora is DEAD** — OpenAI shut down Sora standalone + API on March 24, 2026. $15M/day costs, $2.1M total revenue. Eliminated from consideration.
2. **Veo 3.1 launched** — Google released Veo 3.1 + Veo 3.1 Lite + Veo 3.1 Fast tiers. Free tier now 10 clips/month via Google Vids. NO watermark.
3. **Seedance 2.0 in CapCut** — ByteDance rolled out Seedance 2.0 in CapCut (March 26). Expanding to Europe. Free credits via Dreamina.
4. **Kling 3.0 launched** — "Omni One" architecture, physics-accurate motion. Still 66 free credits/day, still watermarked.

### TOP RECOMMENDATION for FLUXION

**Primary: Google Veo 3.1 via Vertex AI API** (we already have Google Cloud with ~EUR234 credits remaining)
- API scriptable for batch generation
- No watermark
- Supports 9:16 vertical
- Image-to-video supported (can animate our screenshots)
- $0.15-0.75/sec depending on tier
- With EUR234 credits: 312-1,560 seconds of video (39-195 eight-second clips)

**Secondary: Kling 3.0 free tier** for quick test iterations (66 credits/day, watermarked)

**Tertiary: Dreamina/Seedance 2.0** for supplementary clips (if available in Italy)

**The hard truth:** For COMMERCIAL USE without watermarks, truly free options are nearly nonexistent. The only viable "free" path is Google Cloud credits we already have.

---

## TOOL-BY-TOOL ANALYSIS

### 1. Google Veo 3 / 3.1

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Current version** | Veo 3.1 (+ Lite, Fast tiers) | HIGH |
| **Free tier (Google Vids)** | 10 clips/month, 720p, 8 sec, NO watermark | HIGH |
| **Free tier (AI Studio)** | ~10 generations/day at 720p | MEDIUM |
| **Free tier (Vertex AI)** | $300 new account credits (we have ~EUR234 remaining) | HIGH |
| **Vertex AI pricing** | Fast: $0.15/s, Standard: $0.40/s, Premium: $0.75/s | HIGH |
| **Max duration** | 8 seconds per generation | HIGH |
| **Resolution** | 720p free, up to 4K on paid | HIGH |
| **Watermark** | NO — not even on free tier | HIGH |
| **Commercial use** | YES on paid/Vertex AI | HIGH |
| **API** | YES — Gemini API + Vertex AI (GA endpoints) | HIGH |
| **Image-to-video** | YES — single image, multi-image reference, first+last frame control | HIGH |
| **Video-to-video** | YES — reference-to-video, style transfer | MEDIUM |
| **9:16 vertical** | YES — native support for portrait (9:16) and landscape (16:9) | HIGH |
| **Native audio** | YES — Veo 3.1 generates synchronized audio/dialogue | HIGH |
| **Batch scripting** | YES — API supports automated pipelines | HIGH |

**Critical note:** Preview endpoints deprecated April 2, 2026. Must use GA endpoints.

**Cost projection for FLUXION (9 videos x 7 clips each = 63 clips):**
- Fast tier (good enough for marketing): 63 clips x 8 sec x $0.15 = ~$75 (EUR70)
- Standard tier: 63 clips x 8 sec x $0.40 = ~$200 (EUR185)
- We have EUR234 credits — MORE than enough for all 9 videos

**Verdict: BEST OPTION. We already have credits. API scriptable. No watermark. 9:16 supported. Image-to-video for animating screenshots. This is the clear winner.**

---

### 2. Seedance 2.0 (ByteDance / Dreamina / CapCut)

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Current version** | Seedance 2.0 | HIGH |
| **Free tier (Dreamina)** | ~225 daily tokens (shared across all tools) = 1-2 videos/day | MEDIUM |
| **Free tier (CapCut)** | Requires CapCut Pro subscription in most markets | HIGH |
| **New account bonus** | ~800 seconds of free credits | MEDIUM |
| **Max duration** | Up to 15 seconds per clip | HIGH |
| **Resolution** | Up to 2K | HIGH |
| **Watermark** | YES on free tier (Dreamina watermark) | MEDIUM |
| **Commercial use** | Unclear on free tier; likely NO | LOW |
| **API** | NO public API. BytePlus offers 2M free API tokens (enterprise) | MEDIUM |
| **Image-to-video** | YES — but will NOT process images with real faces | HIGH |
| **Video-to-video** | YES — reference video input supported | MEDIUM |
| **9:16 vertical** | YES — 6 aspect ratios supported | HIGH |
| **Italy/Europe access** | Expanding but NOT confirmed for Italy specifically. Available via Dreamina web globally. | LOW |
| **Batch scripting** | NO — web UI only, no API for free tier | HIGH |
| **Face restriction** | Will NOT generate video from images containing real faces | HIGH |

**Drawbacks for FLUXION:**
1. No API = no batch automation (we need 9 x 7 = 63 clips minimum)
2. Face restriction blocks animating any screenshot with people
3. Watermark on free tier
4. Italy access uncertain via CapCut (Dreamina web probably works)

**Verdict: SUPPLEMENTARY ONLY. Good quality but no API, watermarks, and face restrictions make it unsuitable as primary tool. Use Dreamina web for a few supplementary clips where Veo falls short.**

---

### 3. Kling 3.0 (Kuaishou)

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Current version** | Kling 3.0 ("Omni One" architecture) | HIGH |
| **Free tier** | 66 credits/day, replenished every 24 hours | HIGH |
| **Credits per video** | Standard 5s: ~10 credits, Pro 5s: ~35 credits | HIGH |
| **Effective free clips** | 3-6 short videos/day (standard mode) | HIGH |
| **Max duration** | 5-10 seconds per generation | HIGH |
| **Resolution** | 720p on free tier (1080p+ paid) | HIGH |
| **Watermark** | YES on free tier | HIGH |
| **Commercial use** | NO on free tier | HIGH |
| **API** | YES — official API at $0.084-0.168/sec. Third-party: fal.ai, PiAPI, Crazyrouter (~30% cheaper) | HIGH |
| **Image-to-video** | YES — JPG/PNG input, min 300x300px, up to 10MB | HIGH |
| **Video-to-video** | YES — video extension, editing | MEDIUM |
| **9:16 vertical** | YES — native support for 9:16, 16:9, 1:1 | HIGH |
| **Motion quality** | Best-in-class for realistic human movement and physics | HIGH |
| **Batch scripting** | NO on free tier (sequential only). YES on paid API. | HIGH |

**Cost projection (paid API, if needed):**
- 63 clips x 5 sec x $0.084 = ~$26 (standard mode, cheapest)
- Via third-party at 30% discount: ~$18

**Free tier strategy:**
- 66 credits/day = ~6 standard clips/day
- 63 clips needed = ~11 days of daily usage
- BUT: watermarked and non-commercial

**Verdict: BEST FREE TIER FOR TESTING. Use daily free credits to iterate on prompts before spending Veo credits. For final production, Veo is better (no watermark, we have credits). Kling API is cheapest paid option if Veo credits run out.**

---

### 4. Runway Gen-4 / Gen-4.5

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Current version** | Gen-4.5 | HIGH |
| **Free tier** | 125 ONE-TIME credits (not recurring). ~25 seconds of Gen-4 Turbo video. | HIGH |
| **Max duration** | 5-10 seconds per generation | MEDIUM |
| **Resolution** | 720p on free tier | HIGH |
| **Watermark** | YES on free tier | HIGH |
| **Commercial use** | NO on free tier | HIGH |
| **API** | YES — professional-grade API | HIGH |
| **Image-to-video** | YES (Gen-4 Turbo only on free tier, not full Gen-4) | MEDIUM |
| **9:16 vertical** | YES | MEDIUM |
| **Quality** | Best professional editing suite, cinematic output | HIGH |

**Verdict: NOT VIABLE for free use. 125 credits total = ~25 seconds of video, ONCE. That's one clip. Paid plans start $12/month. Professional tool, professional pricing. SKIP for FLUXION zero-cost requirement.**

---

### 5. Pika 2.2

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Current version** | Pika 2.2 (some sources say 2.5) | MEDIUM |
| **Free tier** | 80-150 credits/month. ~5-8 videos at 480p. | MEDIUM |
| **Resolution** | 480p on free tier (!) | HIGH |
| **Watermark** | YES on free tier | HIGH |
| **Commercial use** | NO on free tier | HIGH |
| **API** | Limited | LOW |
| **Image-to-video** | YES (image-to-video only on free tier) | MEDIUM |
| **9:16 vertical** | YES | MEDIUM |
| **Quality** | Creative/stylized, less photorealistic than Kling/Veo | MEDIUM |

**Verdict: SKIP. 480p free tier is unusable for commercial video. Watermarked. Limited credits. Not competitive.**

---

### 6. Hailuo AI / MiniMax (Hailuo 2.3)

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Current version** | Hailuo 2.3 | MEDIUM |
| **Free tier** | ~3 videos/day (down from previously unlimited) | HIGH |
| **Max duration** | 6 seconds at 1080p | HIGH |
| **Resolution** | 1080p even on free tier | MEDIUM |
| **Watermark** | YES on free tier | HIGH |
| **Commercial use** | NO on free tier | HIGH |
| **API** | MiniMax API available (paid) | MEDIUM |
| **Image-to-video** | YES — image-to-video, subject reference | HIGH |
| **9:16 vertical** | YES | MEDIUM |
| **Quality** | Excellent character micro-expressions, dynamic action | HIGH |

**Verdict: DECENT FOR SUPPLEMENTARY CLIPS. 3 free clips/day at 1080p is usable for testing. Watermark blocks commercial use. Good for iterating prompts alongside Kling.**

---

### 7. Luma Dream Machine

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Free tier** | 30 generations/month OR 500 credits/month (sources conflict) | LOW |
| **Resolution** | 720p "draft" quality on free tier | MEDIUM |
| **Watermark** | YES on free tier | HIGH |
| **Commercial use** | NO on free tier | HIGH |
| **API** | YES — Luma API available | MEDIUM |
| **Image-to-video** | YES | MEDIUM |
| **9:16 vertical** | YES | LOW |

**Verdict: SKIP. Watermarked, draft quality, no commercial use. Nothing it does better than Kling or Veo for our use case.**

---

### 8. Genmo / Mochi

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Free tier** | 200 initial credits + 50/month. Watermarked. | MEDIUM |
| **Open source** | YES — Apache 2.0, but requires 4x H100 GPUs | HIGH |
| **Resolution** | Standard on free | MEDIUM |
| **Watermark** | YES on free tier | MEDIUM |
| **Commercial use** | NO on free tier (YES if self-hosted) | MEDIUM |
| **API** | Hosted playground + open-source weights | HIGH |

**Verdict: SKIP. Open-source option requires enterprise GPU hardware we don't have. Web free tier is too limited.**

---

### 9. Sora (OpenAI)

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Status** | SHUT DOWN March 24, 2026 | HIGH |
| **Reason** | $15M/day operating cost, $2.1M total revenue, safety concerns, leaked model access | HIGH |
| **Legacy** | Sora 1 still accessible via ChatGPT Plus ($20/month) with limited generations | MEDIUM |

**Verdict: DEAD. Do not consider. Not available standalone or via API.**

---

### 10. Dreamina Seedance via CapCut Desktop

| Attribute | Detail | Confidence |
|-----------|--------|------------|
| **Status** | Rolling out since March 26, 2026. Select markets first. | HIGH |
| **Markets confirmed** | Brazil, Indonesia, Malaysia, Mexico, Philippines, Thailand, Vietnam. Expanding to Europe. | HIGH |
| **Italy access** | NOT CONFIRMED. Dreamina web likely accessible globally. CapCut integration may be geo-restricted. | LOW |
| **Requires** | CapCut Pro subscription for AI features in most markets | HIGH |

**Verdict: NOT RELIABLE for Italy. We already have pyCapCut for editing. Dreamina web is the fallback access method.**

---

## COMPARISON MATRIX

| Tool | Free Clips/Day | Duration | Resolution | Watermark | Commercial | API | 9:16 | I2V | Batch |
|------|---------------|----------|-----------|-----------|------------|-----|------|-----|-------|
| **Veo 3.1 (Vids)** | ~0.3/day (10/mo) | 8s | 720p | NO | Unclear | NO | YES | YES | NO |
| **Veo 3.1 (Vertex)** | Credits-based | 8s | up to 4K | NO | YES | YES | YES | YES | YES |
| **Seedance 2.0** | 1-2/day | 15s | 2K | YES | NO | NO | YES | YES* | NO |
| **Kling 3.0** | 3-6/day | 5-10s | 720p | YES | NO | YES (paid) | YES | YES | NO (free) |
| **Runway Gen-4** | 1 total | 5-10s | 720p | YES | NO | YES (paid) | YES | YES | NO (free) |
| **Pika 2.2** | ~0.3/day | 5-10s | 480p | YES | NO | Limited | YES | YES | NO |
| **Hailuo 2.3** | 3/day | 6s | 1080p | YES | NO | YES (paid) | YES | YES | NO |
| **Luma** | ~1/day | varies | 720p | YES | NO | YES (paid) | YES | YES | NO |
| **Genmo** | ~2 initial | varies | Standard | YES | NO | OSS | ? | NO | NO |
| **Sora** | DEAD | - | - | - | - | - | - | - | - |

*Seedance blocks real faces in image-to-video

---

## IMAGE-TO-VIDEO CAPABILITIES (Critical for FLUXION)

We have existing assets: Veo 2.0 clips + app screenshots. Which tools can animate them?

### Best for Screenshot Animation
1. **Veo 3.1** — First-frame + last-frame control. Up to 3 reference images for subject consistency. Best option.
2. **Kling 3.0** — Motion brush lets you define how specific parts of the image should move. Excellent for UI demos.
3. **Hailuo 2.3** — Subject reference maintains appearance. Good for product shots.

### Best for Extending Existing Clips
1. **Kling 3.0** — Video extension feature. Start from existing clip, generate continuation.
2. **Veo 3.1** — Reference-to-video capability. Style transfer from existing footage.

### Face Restrictions
- **Seedance 2.0**: Will NOT process images with real faces (safety restriction)
- **Veo 3.1**: No known face restriction for I2V
- **Kling 3.0**: No known face restriction for I2V

---

## VIDEO-TO-VIDEO CAPABILITIES

| Tool | Extend Clip | Style Transfer | Edit/Replace | Lip Sync |
|------|------------|----------------|-------------|----------|
| Veo 3.1 | Reference-based | YES | NO | NO |
| Kling 3.0 | YES (direct extend) | MEDIUM | Motion brush | NO |
| Seedance 2.0 | Reference video input | YES | NO | NO |
| Runway Gen-4 | YES (paid only) | YES | YES | NO |

---

## PROMPT ENGINEERING FOR COMMERCIAL VIDEO

### The 8-Layer Control Framework (2026 Best Practice)

Based on industry research, professional AI video prompts in 2026 use 8 control layers:

1. **Subject**: Who/what is in the frame
2. **Emotion**: Mood, facial expression, body language
3. **Optics**: Camera type, lens, focal length, DOF
4. **Motion**: Camera movement (dolly, tracking, pan), subject movement
5. **Lighting**: Time of day, light source, color temperature
6. **Style**: Commercial photography, cinematic, documentary
7. **Audio**: Background sounds, music mood (if supported)
8. **Continuity**: Scene consistency across multiple clips

### Example Prompt Template for FLUXION PMI Videos

```
PROMPT TEMPLATE (Italian hair salon — vertical 9:16):

"Professional Italian hair salon interior, warm amber lighting.
A female hairdresser (30s) styling a client's hair with confident,
skilled movements. Modern salon equipment visible.
Camera: Smooth slow dolly-in, 24fps, shallow depth of field,
bokeh background. Style: Commercial photography, warm color grade,
high contrast. Aspect ratio: 9:16 portrait."
```

### Key Tips
- **Be specific about Italian setting**: mention "Italian", warm Mediterranean colors, specific Italian business elements
- **Specify 9:16 explicitly** in the prompt AND in API parameters
- **Include camera movement** for professional feel (static shots look amateur)
- **Mention lighting** — warm, inviting tones for service businesses
- **Avoid text in frame** — AI-generated text is always garbled
- **Generate 3-5 variations** of each clip and pick the best

---

## MULTI-ACCOUNT STRATEGY ANALYSIS

### Viability by Platform

| Platform | Multi-Account Viable? | Risk | Notes |
|----------|----------------------|------|-------|
| Veo (AI Studio) | YES — Google accounts are free | LOW | Different Google accounts, 10 clips/month each |
| Veo (Vertex AI) | YES — multiple GCP projects | LOW | $300 free credits per new GCP account |
| Kling 3.0 | YES — email signup only | LOW | 66 credits/day per account |
| Dreamina | YES — Google/TikTok/email signup | LOW | Daily credits per account |
| Hailuo | YES — basic signup | LOW | 3 clips/day per account |
| Runway | NO value — 125 credits total | N/A | Not enough to justify effort |
| Pika | MAYBE — 80-150/month | LOW | 480p makes it not worth it |

### Recommended Multi-Account Strategy

For maximum free output without spending money:

1. **3x Google accounts on Veo AI Studio** = 30 clips/month at 720p, NO watermark
2. **3x Kling accounts** = 18 clips/day for prompt iteration (watermarked)
3. **2x Dreamina accounts** = 4-6 clips/day for supplementary content (watermarked)
4. **1x GCP account with EUR234 credits** = ~150+ production-quality clips via API (NO watermark, 1080p, commercial use)

**Total monthly free capacity (watermark-free, commercial):**
- Veo AI Studio: 30 clips (720p, suitable for social media)
- Veo Vertex API: 150+ clips from existing credits (1080p, professional)

**Total monthly free capacity (watermarked, iteration only):**
- Kling: ~540 clips/month (18/day x 30)
- Dreamina: ~120 clips/month (4/day x 30)
- Hailuo: ~90 clips/month (3/day x 30)

---

## DEFINITIVE RECOMMENDATION FOR FLUXION

### Strategy: Two-Phase Pipeline

#### Phase 1: Prompt Iteration (FREE, watermarked)
- Use **Kling 3.0 free tier** (66 credits/day) to test and refine prompts
- Generate 3-5 variations per scene, pick best prompt
- Use 9:16 vertical, standard mode
- Result: Proven prompts for all 63 clips across 9 verticals
- Timeline: 3-5 days of iteration

#### Phase 2: Production Generation (EUR234 GCP credits)
- Use **Veo 3.1 API via Vertex AI** with proven prompts from Phase 1
- Batch script using Python (we already have the infrastructure)
- Generate at Fast tier ($0.15/sec) for cost efficiency
- 63 clips x 8 sec x $0.15 = ~$75 (EUR70)
- Leaves EUR164 for re-generations and additional clips
- Result: 63+ watermark-free, commercial-use, 1080p vertical clips
- Timeline: 1 day of scripted batch generation

#### Phase 3: Assembly (FREE)
- Use **pyCapCut** (already set up) or **Remotion** to assemble final videos
- Add Italian voiceover via Edge-TTS (already integrated)
- Add text overlays, transitions, music
- Export 9 final vertical marketing videos

### Cost Summary

| Item | Cost |
|------|------|
| Prompt iteration (Kling free) | EUR0 |
| Production clips (Veo 3.1 Fast, 63 clips) | ~EUR70 from existing GCP credits |
| Re-generations buffer (20 extra clips) | ~EUR20 from existing GCP credits |
| Assembly (pyCapCut/Remotion) | EUR0 |
| Voiceover (Edge-TTS) | EUR0 |
| **TOTAL NEW SPENDING** | **EUR0** (using existing GCP credits) |

### API Script Architecture

```python
# Pseudocode for batch Veo 3.1 generation
from google.cloud import aiplatform

VERTICALS = ["parrucchiere", "palestra", "clinica", "officina",
             "estetista", "nail_artist", "barbiere", "spa", "tatuatore"]

for vertical in VERTICALS:
    prompts = load_proven_prompts(f"prompts/{vertical}.json")
    for i, prompt in enumerate(prompts):
        result = veo31_generate(
            prompt=prompt,
            aspect_ratio="9:16",
            duration_seconds=8,
            resolution="1080p",
            model="veo-3.1-fast",  # cheapest tier
            generate_audio=False,  # we add our own VO
        )
        save_clip(result, f"output/{vertical}/clip_{i:02d}.mp4")
```

---

## RISKS AND MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Veo API deprecation (preview endpoints killed April 2) | HAPPENED | HIGH | Use GA endpoints only |
| GCP credits expire | MEDIUM | HIGH | Check expiry date; use them now |
| Kling changes free tier | LOW | LOW | Only used for iteration, not production |
| Veo quality insufficient for commercial use | LOW | MEDIUM | Test first with 2-3 clips before full batch |
| Italy-specific scenes look generic | MEDIUM | MEDIUM | Use detailed prompts with Italian elements; use screenshot I2V |
| 8-second clips feel too short | MEDIUM | LOW | Plan shot composition for 8s; assemble multiple clips in editor |

---

## SOURCES

### HIGH Confidence (Official Documentation)
- Google Veo 3.1 Vertex AI docs: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
- Vertex AI Pricing: https://cloud.google.com/vertex-ai/generative-ai/pricing
- Gemini API video generation: https://ai.google.dev/gemini-api/docs/video
- Kling API docs: https://app.klingai.com/global/dev/document-api/apiReference/model/imageToVideo
- Runway pricing: https://runwayml.com/pricing

### MEDIUM Confidence (Verified by multiple credible sources)
- Sora shutdown (March 24, 2026): TechCrunch, 9to5Mac, multiple sources confirm
- Seedance 2.0 CapCut rollout: TechCrunch https://techcrunch.com/2026/03/26/bytedances-new-ai-video-generation-model-dreamina-seedance-2-0-comes-to-capcut/
- Kling 3.0 66 credits/day: Multiple review sites confirm
- Veo 3.1 Lite announcement: https://blog.google/innovation-and-ai/technology/ai/veo-3-1-lite/

### LOW Confidence (WebSearch only, needs validation)
- Exact daily limits on Dreamina free tier (sources conflict: 150 vs 225 daily tokens)
- Pika 2.2 exact free tier credits (sources say 80-150/month)
- Hailuo exact daily limit (some say 3/day, others say more)
- Whether Veo AI Studio free tier has watermarks (likely no, but verify before relying on it)

---

## CHANGELOG vs MARCH 23 RESEARCH

| Item | March 23 | April 3 (this file) |
|------|----------|---------------------|
| Sora | Available via ChatGPT Plus | SHUT DOWN (March 24) |
| Veo | Veo 3 only | Veo 3.1 + Lite + Fast tiers |
| Kling | Kling 3.0 (just launched) | Kling 3.0 (confirmed stable) |
| Seedance | Dreamina web only | Now in CapCut (select markets) |
| Recommendation | Hybrid: Remotion + stock + AI clips | Veo 3.1 API batch + Kling iteration |
| Strategy | Unclear on batch approach | Clear two-phase pipeline |
| Budget | Pure free concern | EUR234 GCP credits = EUR0 new cost |
