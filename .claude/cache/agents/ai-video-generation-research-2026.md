# AI Video Generation Tools Research — CoVe 2026
> Research date: 2026-03-23
> Purpose: Find BEST free-tier AI video tools for FLUXION ~4min promo video
> Target scenes: Italian PMI (hair salons, mechanics, dentists, gyms, beauty, nail artists) — people working, phones ringing

---

## EXECUTIVE SUMMARY & RECOMMENDATION

### Best Strategy for FLUXION Promo Video (4 min)

**HYBRID APPROACH (recommended):**
1. **Remotion** (FREE, open source) — compose final video programmatically from assets (screenshots, stock footage, text overlays, transitions, voiceover)
2. **Pexels/Pixabay** (FREE, no attribution needed) — real stock footage of salons, mechanics, dentists, gyms
3. **Kling AI + Seedance 2.0** (FREE tier) — generate 5-10 sec AI clips of specific PMI scenes not found in stock
4. **Edge-TTS** (FREE) — Italian voiceover (IsabellaNeural)

**Why not pure AI video?** No free-tier AI tool can generate 4 minutes of coherent, high-quality commercial video. All free tiers cap at 5-15 sec clips with watermarks. The math: 4 min = 240 sec. At best, free tiers give ~30 sec/day of watermarked 720p footage. Would take weeks and still be watermarked.

**Why Remotion wins:** It's React-based, we already know React, it composes videos from assets programmatically (screenshots + stock + AI clips + text + audio), produces MP4 with zero watermarks, zero cost for individuals.

---

## 1. CHINESE AI VIDEO GENERATORS

### 1.1 Kling AI (Kuaishou) — kling3.0
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 66 credits/day (resets daily) — ~3-6 short videos/day |
| **Max duration** | 10 sec per generation (extendable if credits remain) |
| **Resolution** | 720p free, 1080p+ paid |
| **Quality** | 8/10 — excellent realism, good motion, cinematic lighting |
| **Watermark** | YES on free tier |
| **Commercial use** | NO on free tier |
| **API** | Enterprise only ($4,200+ for 30K units); third-party APIs exist (PiAPI, fal.ai) |
| **Image-to-video** | YES — upload screenshot/image, animate it. Start/end frame, motion brush, camera movements |
| **Italian PMI scenes** | Good — can prompt for "Italian hair salon", "mechanic workshop". Realistic people/environments |
| **Automation** | Only via paid API or third-party providers |
| **Best for** | Generating 5-10 sec B-roll clips of PMI scenes |

**Verdict:** Best quality among free Chinese tools. Watermark is the killer — need to crop or use paid tier for clean clips. Good for generating specific PMI scene clips that stock video doesn't cover.

### 1.2 Hailuo AI / MiniMax (Hailuo 2.3)
| Attribute | Detail |
|-----------|--------|
| **Free tier** | Limited daily credits during launch period; exact amount varies |
| **Max duration** | 6-10 sec (768p-6s, 768p-10s, 1080p-6s) |
| **Resolution** | Up to 1080p (even some free generations) |
| **Quality** | 8/10 — excellent character micro-expressions, dynamic action |
| **Watermark** | YES on free tier |
| **Commercial use** | NO on free tier |
| **API** | MiniMax API available (paid) |
| **Image-to-video** | YES — image-to-video, text-to-video, subject reference |
| **Italian PMI scenes** | Good — realistic people, workplace scenes |
| **Best for** | Short character-focused clips, emotional micro-expressions |

**Verdict:** Strong competitor to Kling. Hailuo 2.3 has excellent motion quality. Watermark issue same as Kling.

### 1.3 Seedance 2.0 (ByteDance / Dreamina)
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 60+ daily credits (most generous in market); 2-3 standard generations/day |
| **Max duration** | 15 sec at 720p |
| **Resolution** | 720p free, 1080p paid |
| **Quality** | 9/10 — advanced physics engine, perfect lip-sync, collision physics |
| **Watermark** | YES on free tier |
| **Commercial use** | NO on free tier |
| **API** | Available on paid plans |
| **Image-to-video** | YES — plus multi-modal reference (up to 12 files: 9 images + 3 videos + 3 audio) |
| **Italian PMI scenes** | Excellent — 2K resolution, native audio generation, realistic workplace scenes |
| **Best for** | Highest quality short clips, complex physical interactions |

**Verdict:** BEST quality among all free-tier AI video generators as of March 2026. The multi-modal reference system (12 files input) is unique. Watermark kills commercial use on free tier.

### 1.4 Vidu AI (Chinese)
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 40-80 monthly credits |
| **Quality** | 7/10 |
| **Watermark** | YES |
| **Commercial use** | NO on free tier |
| **Best for** | Experimentation only |

**Verdict:** Weakest free tier among Chinese tools. Skip.

### 1.5 PixVerse
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 60 daily credits, 2 free templates/day |
| **Resolution** | Basic resolution (sub-1080p) |
| **Quality** | 6/10 |
| **Watermark** | Reportedly NO watermark on daily credits (unique advantage!) |
| **Commercial use** | Check ToS — some reports say allowed |
| **Best for** | Quick clips without watermark if confirmed |

**Verdict:** If no-watermark claim is accurate, PixVerse becomes interesting for generating quick B-roll clips. Quality is lower than Kling/Seedance.

---

## 2. WESTERN AI VIDEO GENERATORS

### 2.1 Runway ML (Gen-4)
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 125 ONE-TIME credits (never resets) — ~25 sec of Gen-4 Turbo video |
| **Resolution** | 720p watermarked |
| **Quality** | 8/10 |
| **Watermark** | YES |
| **Commercial use** | NO on free tier |
| **API** | Available on paid plans ($12+/mo) |
| **Image-to-video** | YES (Gen-4 Turbo) |

**Verdict:** Terrible free tier — 25 seconds TOTAL, then done forever. Not viable for our project.

### 2.2 Pika Labs (Pika 2.5)
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 80 credits/month (~3 videos) |
| **Resolution** | 480p only on free tier |
| **Quality** | 7/10 (limited by 480p on free) |
| **Watermark** | YES |
| **Commercial use** | NO on free tier |

**Verdict:** 480p is unusable for commercial video. Skip free tier.

### 2.3 Luma Dream Machine (Ray2)
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 30 generations/month — IMAGES ONLY (Photon model, 720p) |
| **Video generation** | LOCKED behind paid plans ($30+/mo) |

**Verdict:** Free tier cannot generate video at all. Useless for our purpose.

### 2.4 OpenAI Sora 2
| Attribute | Detail |
|-----------|--------|
| **Free tier** | DISCONTINUED January 10, 2026 |
| **Access** | Plus ($20/mo) or Pro ($200/mo) only |

**Verdict:** No free tier exists. Skip.

### 2.5 Google Veo 3
| Attribute | Detail |
|-----------|--------|
| **Free tier** | Available through Google AI Studio with limits |
| **Quality** | 9/10 — native audio generation |
| **Worth checking** | May have free credits for new accounts |

---

## 3. OPEN SOURCE / SELF-HOSTED

### 3.1 Wan 2.2 (Alibaba — BEST Open Source)
| Attribute | Detail |
|-----------|--------|
| **License** | Apache 2.0 — fully free, commercial use OK |
| **Models** | 1.3B (8GB VRAM), 14B (needs 24GB+) |
| **Quality** | 8/10 — most cinematic open-source model |
| **MacBook M1/M2** | POSSIBLE with 1.3B model via ComfyUI + GGUF format + MPS |
| **Requirements** | M2 Max 64GB ideal; M1 16GB = very slow, degraded quality |
| **Duration** | 5-10 sec clips |
| **Setup complexity** | HIGH — ComfyUI + GGUF models + MPS adjustments needed |
| **Space needed** | 50GB+ for models |

**Verdict:** Best open-source option. The 1.3B model CAN run on MacBook but is slow and lower quality. The 14B model needs serious GPU. For our MacBook dev setup, this is technically possible but painful.

### 3.2 HunyuanVideo 1.5 (Tencent)
| Attribute | Detail |
|-----------|--------|
| **License** | Open source, free commercial use |
| **Parameters** | 8.3B (lightweight version) |
| **Quality** | 8/10 — state-of-the-art motion coherence |
| **MacBook** | Possible on consumer GPUs but needs significant VRAM |
| **Online studio** | Free at hunyuanvideo.org (no install needed) |

**Verdict:** Online studio is the easiest path — free, no install, no watermark concerns. Worth testing.

### 3.3 CogVideoX (Tsinghua/Zhipu AI)
| Attribute | Detail |
|-----------|--------|
| **License** | Open source |
| **Models** | 2B (lighter) and 5B (higher quality) |
| **Quality** | 7/10 — 720x480, 8 fps, 6-10 sec |
| **MacBook** | 2B can run on free T4 Colab with quantization |
| **HuggingFace** | Full Diffusers integration |

**Verdict:** Lower quality than Wan 2.2. Use Wan instead.

### 3.4 AnimateDiff
| Attribute | Detail |
|-----------|--------|
| **Purpose** | Adds motion to Stable Diffusion images |
| **VRAM** | 12GB+ for 16 frames at 512x512 |
| **MacBook** | Possible on 16GB+ M1/M2 via MPS, 30-50% GPU speed |
| **Quality** | 6/10 for realistic scenes (better for stylized/anime) |

**Verdict:** Not great for realistic PMI scenes. Better for stylized content.

### 3.5 Stable Video Diffusion (SVD)
| Attribute | Detail |
|-----------|--------|
| **Purpose** | Image-to-video (animate a still image) |
| **VRAM** | 24GB+ needed |
| **MacBook** | NOT viable on MacBook |

**Verdict:** Too heavy for our hardware. Skip.

---

## 4. JSON/API-BASED VIDEO COMPOSITION TOOLS

### 4.1 Remotion (React-based) — RECOMMENDED
| Attribute | Detail |
|-----------|--------|
| **License** | Free for individuals and small teams (<3 employees) |
| **Cost** | €0 for FLUXION (single developer) |
| **Technology** | React components render to MP4/WebM/GIF |
| **Features** | CSS, Canvas, SVG, WebGL, transitions, overlays, audio, images, video clips |
| **Watermark** | NONE — your video, your output |
| **Commercial use** | YES (for individuals/small teams) |
| **Resolution** | Any — 1080p, 4K, whatever you render |
| **Duration** | Unlimited |
| **Screenshots** | Import as `<Img>` components — full control over timing, position, animation |
| **Transitions** | `<TransitionSeries>` with crossfade, slide, wipe, custom |
| **Audio** | Full audio support — voiceover, music, sound effects |
| **Text overlays** | Full React/CSS — any font, any animation, any style |
| **Rendering** | Local on MacBook (uses bundled FFmpeg since v4.0) |
| **Viral in 2026** | Official Claude Code skill — 6M+ views, 25K+ installs |

**PERFECT FIT for FLUXION because:**
1. We already know React/TypeScript
2. Screenshots are just image assets — import and compose freely
3. Stock video clips can be layered as `<Video>` components
4. AI-generated clips can be mixed in as additional assets
5. Voiceover via Edge-TTS → import as `<Audio>`
6. Full programmatic control — change copy/timing/assets via props
7. Zero watermark, zero cost, unlimited duration
8. Can version-control the entire video as code

### 4.2 Shotstack API
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 20 credits = 20 minutes of video |
| **Technology** | JSON timeline → cloud renders → MP4 |
| **Watermark** | On free tier, yes |
| **API** | REST API, JSON-based editing |
| **Features** | Timeline, clips, overlays, audio, transitions, text |
| **Best for** | Server-side automated video generation |

**Verdict:** 20 minutes free is generous but watermarked. Good fallback if Remotion doesn't work out.

### 4.3 Creatomate
| Attribute | Detail |
|-----------|--------|
| **Free tier** | Free signup, credit-based (limited) |
| **Technology** | JSON (RenderScript) → cloud renders → MP4/PNG/GIF |
| **Features** | Full programmatic control via JSON |
| **Watermark** | Likely on free tier |

**Verdict:** Developer-friendly but credit-limited. Remotion is better for our use case (local rendering, no limits).

### 4.4 JSON2Video
| Attribute | Detail |
|-----------|--------|
| **Free tier** | 600 seconds (10 minutes) of rendering |
| **Technology** | JSON → cloud renders → MP4 |
| **Features** | Text, images, audio, subtitles, AI voices (30+ languages) |
| **Watermark** | Unclear on free tier |

**Verdict:** 10 minutes is enough for a 4-min video. But Remotion gives unlimited local rendering.

---

## 5. FREE STOCK VIDEO SOURCES (for real PMI footage)

### 5.1 Pexels
- **License:** Pexels License — free, no attribution, commercial use OK
- **Content:** 56,998+ business videos, 10,000+ hair salon videos, 4K available
- **Italian scenes:** Search "parrucchiere", "salone", "meccanico", "palestra"
- **Quality:** Professional 4K footage
- **Best for:** Real footage of salons, workshops, gyms, dental offices

### 5.2 Pixabay
- **License:** Pixabay License — free, no attribution, commercial use OK
- **Content:** Extensive salon/business footage
- **Quality:** Up to 4K

### 5.3 Coverr.co
- **License:** Free, commercial use
- **Content:** Curated free stock videos

---

## 6. COMPARISON MATRIX — ALL TOOLS

| Tool | Free Clips/Day | Max Duration | Resolution | Watermark | Commercial | Quality | API | Italian Scenes |
|------|---------------|-------------|-----------|-----------|-----------|---------|-----|---------------|
| **Kling AI** | 3-6 | 10 sec | 720p | YES | NO | 8/10 | Paid | Good |
| **Hailuo 2.3** | ~3 | 10 sec | 1080p | YES | NO | 8/10 | Paid | Good |
| **Seedance 2.0** | 2-3 | 15 sec | 720p | YES | NO | 9/10 | Paid | Excellent |
| **Vidu** | 2-3/month | 5 sec | 720p | YES | NO | 7/10 | No | Fair |
| **PixVerse** | ~3 | 5 sec | <1080p | NO? | Check | 6/10 | No | Fair |
| **Runway Gen-4** | 25 sec TOTAL | 10 sec | 720p | YES | NO | 8/10 | Paid | Good |
| **Pika 2.5** | ~3/month | 5 sec | 480p | YES | NO | 7/10 | Paid | Fair |
| **Luma Ray2** | Images only | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Sora 2** | NONE | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Wan 2.2 (local)** | Unlimited | 10 sec | 720p | NONE | YES | 8/10 | Local | Good |
| **HunyuanVideo** | Unlimited | 5-10 sec | 720p | NONE | YES | 8/10 | Local/Web | Good |
| **Remotion** | Unlimited | Unlimited | Any | NONE | YES | N/A* | Local | N/A* |
| **Shotstack** | 20 min total | Unlimited | Any | YES | NO | N/A* | REST | N/A* |
| **JSON2Video** | 10 min total | Unlimited | Any | ? | ? | N/A* | REST | N/A* |
| **Pexels stock** | Unlimited | Varies | 4K | NONE | YES | 9/10 | YES | Good |

*Composition tools — quality depends on input assets

---

## 7. RECOMMENDED PIPELINE FOR FLUXION PROMO VIDEO

### Architecture
```
[Stock Video Clips]     ──┐
  (Pexels/Pixabay)        │
                          ├──→ [Remotion Project] ──→ MP4 (1080p, no watermark)
[FLUXION Screenshots]   ──┤      (React/TypeScript)
  (landing/screenshots/)   │        │
                          │        ├── Transitions (crossfade, slide)
[AI-Generated Clips]    ──┤        ├── Text overlays (Italian copy)
  (Kling/Seedance free)   │        ├── Logo watermark (ours)
                          │        ├── Voiceover (Edge-TTS Isabella)
[Voiceover Audio]       ──┤        └── Background music (royalty-free)
  (Edge-TTS)              │
                          │
[Background Music]      ──┘
  (Pixabay Audio)
```

### Step-by-Step
1. **Download stock footage** from Pexels: hair salon, mechanic, dentist, gym, beauty salon, nail artist — 10-15 clips of people working with hands busy
2. **Generate 3-5 AI clips** via Seedance/Kling free tier for specific scenes not found in stock (e.g., "Italian hairdresser answering phone while cutting hair", "mechanic with greasy hands looking at ringing phone")
3. **Prepare FLUXION screenshots** (already have 17 in `landing/screenshots/`)
4. **Generate voiceover** with Edge-TTS IsabellaNeural (script from V4 screenplay)
5. **Find royalty-free Italian/cinematic music** on Pixabay Audio
6. **Build Remotion project**: compose all assets into 15 scenes per V4 screenplay
7. **Render** locally on MacBook → 1080p MP4, zero watermarks, zero cost

### Cost: €0
- Remotion: free for individuals
- Pexels/Pixabay: free stock, no attribution
- Edge-TTS: free
- Kling/Seedance: free tier (watermarked clips can be used as B-roll behind text overlays that cover the watermark area)
- Background music: Pixabay Audio (free)

### Timeline: 1-2 sessions
- Session 1: Download stock footage + generate AI clips + Remotion project setup
- Session 2: Compose scenes + render + final polish

---

## 8. WATERMARK WORKAROUNDS (for AI-generated clips)

If using watermarked AI clips from Kling/Seedance in the final video:
1. **Overlay text/graphics** on the watermark area
2. **Crop** the watermarked corner (lose some frame)
3. **Use as background** behind semi-transparent FLUXION UI overlay
4. **Blur/vignette** the corners where watermarks typically appear
5. **Only use as quick B-roll** (2-3 sec) where watermark is barely noticeable

**Better approach:** Use stock footage (Pexels) for the main PMI scenes — these are watermark-free, 4K, and commercially licensed. Reserve AI generation only for very specific shots that stock doesn't cover.

---

## 9. ALTERNATIVE: PURE STOCK + SCREENSHOTS (Zero AI Video)

If AI video quality/watermarks prove problematic, a **100% stock + screenshots** approach works:

1. Pexels stock footage of PMI workers (excellent 4K available)
2. FLUXION screenshots with Ken Burns / pan effects (subtle, NOT zoompan)
3. Text overlays with Italian copy
4. Edge-TTS voiceover
5. Composed in Remotion

This is the **safest, fastest, and most professional** approach. AI-generated clips are a nice-to-have bonus, not a requirement.

---

## SOURCES

### Chinese AI Video Generators
- [Kling AI Pricing & Plans](https://www.imagine.art/blogs/kling-ai-pricing)
- [Kling AI Review 2026](https://cybernews.com/ai-tools/kling-ai-review/)
- [Kling AI Complete Guide 2026](https://aitoolanalysis.com/kling-ai-complete-guide/)
- [Hailuo AI Video Review 2026](https://cybernews.com/ai-tools/hailuo-ai-video-generator-review/)
- [MiniMax Hailuo 2.3](https://www.minimax.io/news/minimax-hailuo-23)
- [Seedance 2.0 Pricing Guide](https://blog.laozhang.ai/en/posts/seedance-2-pricing-free-vs-paid-guide)
- [Seedance Review 2026](https://aitoolanalysis.com/seedance-review/)
- [Vidu AI Pricing](https://www.vidu.com/pricing)
- [PixVerse AI Review 2026](https://www.seaart.ai/blog/pixverse-ai-review)

### Western AI Video Generators
- [Runway AI Pricing](https://runwayml.com/pricing)
- [Pika Labs Pricing](https://pika.art/pricing)
- [Luma Dream Machine Pricing 2026](https://lumadreammachine.com/pricing/)
- [Sora 2 Free Tier Discontinued](https://www.aifreeapi.com/en/posts/sora-2-free-tier-discontinued)

### Open Source Models
- [Best Open Source AI Video Models 2026](https://www.pixazo.ai/blog/best-open-source-ai-video-generation-models)
- [Wan 2.2 on MacBook](https://medium.com/@ttio2tech_28094/macbook-macmini-run-wan-2-2-generating-videos-dd0e32eb91b3)
- [HunyuanVideo GitHub](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)
- [CogVideoX on HuggingFace](https://huggingface.co/THUDM/CogVideoX-5b)

### Composition Tools
- [Remotion — Make Videos Programmatically](https://www.remotion.dev/)
- [Shotstack — Cloud Video Editing API](https://shotstack.io/)
- [Creatomate — JSON to Video](https://creatomate.com/)
- [JSON2Video API](https://json2video.com/)

### Free Stock Video
- [Pexels Free Stock Videos](https://www.pexels.com/search/videos/hair%20salon/)
- [Pixabay Salon Videos](https://pixabay.com/videos/search/salon/)
- [Free AI Video Generators Comparison 2026](https://videoai.me/blog/free-ai-video-generators-2026)
- [No Watermark AI Video Generators](https://magichour.ai/blog/free-ai-video-generators-without-watermarks)
