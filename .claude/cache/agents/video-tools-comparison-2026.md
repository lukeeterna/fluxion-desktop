# Video Tools Comparison: Shotstack vs Manim vs MoviePy — CoVe 2026
> **Data**: 2026-04-01 | **Obiettivo**: Valutare alternative per pipeline video FLUXION
> **Contesto**: Pipeline attuale usa FFmpeg-python (assembly.py) + Veo 3 clips + Edge-TTS voiceover
> **Target output**: Video promozionali 90s verticali (1080x1920) per 9 verticali PMI

---

## 1. SHOTSTACK API

### 1A. Overview
Shotstack is a cloud-based video editing API that accepts JSON templates and renders MP4 videos server-side. REST API with Python SDK available (`shotstack-sdk-python`). No local rendering required — everything happens in Shotstack's cloud infrastructure.

### 1B. API Capabilities
- **Input**: JSON schema defining timeline, tracks, clips, assets
- **Output**: MP4 (H.264), GIF
- **Workflow**: POST JSON → polling for render status → download rendered file
- **SDK**: Python, Node.js, PHP, Ruby — official SDKs on GitHub
- **Templates**: Pre-built library of JSON templates (Ken Burns slideshows, lower thirds, etc.)
- **Create API**: AI-powered asset generation (text-to-speech, text-to-image) built into the pipeline

### 1C. Free Tier & Pricing

| Plan | Cost | Credits/month | Notes |
|------|------|---------------|-------|
| **Free** | $0 | 20 min video + 100 images | Sandbox watermark, max 10 min per render |
| **Pay-as-you-go** | $0.40/min | Min purchase 25 credits ($10) | Credits valid 1 year |
| **Subscription** | from $39/mo | 200 min | $0.20/min effective |
| **Starter** | $69/mo | 50 min | Lower entry point |
| **Unlimited** | $1,500/mo | Unlimited | Higher concurrency, dedicated infra |
| **Enterprise** | Custom | Custom | SLA, dedicated support |

**Credit math for FLUXION (9 verticali x 90s each):**
- 9 videos x 1.5 min = 13.5 min total = **13.5 credits**
- Free tier (20 min/month) covers ALL 9 videos with room to spare
- Re-renders for iteration: ~40 min total = still within free + small pay-as-you-go

**Watermark caveat**: Free tier renders in sandbox = watermark. Production renders require credits (free 20 min/month are production credits, watermark-free). If over free allowance, renders get watermark unless on paid plan.

### 1D. Features Detail

**Ken Burns Effect:**
- Native support via `effect` property on image assets
- Motions: `zoomIn`, `zoomOut`, `slideLeft`, `slideRight`, `slideUp`, `slideDown`
- 3 speed presets: slow, normal, fast
- Requirement: source images must be 10-15% larger than output resolution to avoid blank edges during pan/zoom

**Text Overlays:**
- Native `title` asset type with font, size, color, position, background
- Lower thirds, captions, CTAs all possible via JSON
- AI auto-captioning available (transcribe audio → overlay subtitles)

**Transitions:**
- Crossfade, dissolve, slide, wipe between clips
- Applied per-clip via `transition` property
- Duration configurable

**Audio Mixing:**
- `soundtrack` property on timeline for background music
- Multiple audio tracks supported
- Volume control per track (`volume` property 0-1)
- Built-in AI TTS for voiceover generation (multiple voices)

**Vertical Video:**
- Full support for custom resolutions including 1080x1920
- Set `width: 1080, height: 1920` in output configuration
- All effects/transitions work at any aspect ratio

### 1E. Render Performance
- **Speed**: ~20 seconds per minute of video (3x real-time)
- **90s video estimate**: ~30 seconds render time
- **Resolution independence**: render time does NOT increase with higher resolution
- **Max duration**: 10 min (sandbox), 3 hours (production)
- **Concurrency**: 1 req/s sandbox, 10 req/s production

### 1F. Output Quality
- **Format**: MP4 (H.264)
- **Resolutions**: SD, HD (720p), Full HD (1080p), custom
- **4K**: Available on high-volume/enterprise plans only
- **Quality setting**: `quality` parameter (low/medium/high) in output config
- **Bitrate control**: Not directly exposed — quality preset controls it
- **FPS**: Configurable (24, 25, 30 fps)
- **Limitation**: Some users report quality loss vs source assets at HD — compression artifacts possible

### 1G. Pros & Cons for FLUXION

**Pros:**
- Zero local dependencies — no FFmpeg, no Python video libs
- JSON template = version-controllable, parameterizable per vertical
- Ken Burns, transitions, text, audio ALL built-in
- 30s render for 90s video (vs minutes locally)
- Free 20 min/month covers our 9 videos
- Python SDK ready to use
- Cloud rendering = works on any dev machine

**Cons:**
- Cloud dependency — requires internet to render
- Watermark on sandbox renders (testing iterations)
- Quality not as controllable as raw FFmpeg (no bitrate fine-tuning)
- Max 1080p on free/starter plans (not 4K)
- Vendor lock-in risk
- $0.40/min if exceeding free tier during iteration
- GUARDRAIL 1 concern: free for production runs, but heavy iteration could cost

---

## 2. MANIM (Community Edition v0.20)

### 2A. Overview
Manim (Mathematical Animation Engine) is an open-source Python library created by Grant Sanderson (3Blue1Brown) for creating programmatic animations. Community fork (ManimCE) is actively maintained. Originally designed for mathematical/educational content, NOT for video production or photo-based content.

### 2B. Capabilities for FLUXION Use Case

**What Manim CAN do:**
- Programmatic scene composition in Python
- Smooth animations: fade, scale, transform, move
- `ImageMobject` class for displaying raster images (PNG, JPG)
- `Text` and `MarkupText` for text rendering (Pango-based)
- Custom fonts via system font installation
- Scene-based architecture (multiple scenes → concatenated video)
- 1080p and 4K output natively
- MP4 (H.264) and GIF output

**What Manim CANNOT do well:**
- NOT designed for video editing (no clip trimming, no timeline)
- NO native audio mixing or soundtrack support
- NO native Ken Burns effect on images (must be coded manually via `.animate.scale().shift()`)
- NO native transitions between scenes (crossfade must be manually coded)
- Image handling is basic — `ImageMobject` is for displaying, not compositing
- NO native video import/overlay (can't layer video clips)
- Performance degrades with large raster images (designed for vector graphics)

### 2C. Rendering Quality
- **Vector-first**: Manim renders vector graphics beautifully (shapes, text, equations)
- **Raster images**: Displayed via `ImageMobject` with resampling (nearest, linear, cubic, lanczos)
- **Text**: Excellent quality via Pango — supports any system font, full Unicode (Italian characters included)
- **Output**: MP4 H.264, configurable quality flags (-ql low, -qm medium, -qh 1080p60, -qk 4K60)

### 2D. Font & Text Support
- Pango-based text rendering (industry standard)
- Any system-installed font available
- Full Unicode support — Italian characters (accented vowels, etc.) work perfectly
- `MarkupText` supports bold, italic, color, size via Pango markup
- LaTeX rendering also available for special formatting
- **Quality**: Broadcast-quality text rendering — superior to FFmpeg drawtext

### 2E. Performance
- **Renderer**: Cairo (CPU) by default, OpenGL (GPU) available
- **Cairo 1080p**: Slow — minutes for complex scenes, seconds for simple ones
- **OpenGL**: Much faster, supports real-time preview
- **Estimated 90s 1080p video**: 5-15 minutes rendering (Cairo), 1-3 minutes (OpenGL)
- **Bottleneck**: Large raster images (screenshots) significantly slower than vector content
- **Dev workflow**: Use -ql (480p15) for iteration, -qh (1080p60) for final only

### 2F. macOS Compatibility
- Requires: `brew install cairo pkg-config pango` (Homebrew)
- Python 3.8+ required
- FFmpeg required for video encoding
- Apple Silicon (M1+) supported
- **macOS 11 Big Sur**: Supported but may need Homebrew workarounds for Cairo/Pango
- **macOS 12 Monterey**: Fully supported

### 2G. Learning Curve
- **For math animations**: Moderate — well-documented, many tutorials
- **For video production**: STEEP — fighting against the tool's design
  - No timeline concept — everything is scene-based with `play()` calls
  - Audio must be added post-render (e.g., with FFmpeg)
  - Ken Burns on photos requires manual animation code
  - Transitions between scenes require custom implementation
  - Essentially: you'd write 500+ lines of Python to do what FFmpeg does in 50 lines

### 2H. Pros & Cons for FLUXION

**Pros:**
- Free, open-source (MIT license)
- Beautiful text rendering
- Programmatic — version-controllable
- Good for animated text overlays and motion graphics
- Could complement FFmpeg for specific text animation segments

**Cons:**
- NOT designed for photo/video composition — wrong tool for the job
- No audio support — must use FFmpeg anyway for final assembly
- Slow rendering for raster-heavy content
- Heavy dependencies (Cairo, Pango, FFmpeg, LaTeX optional)
- Massive over-engineering for our use case (slideshow + voiceover + Ken Burns)
- Dev time: 40-80 hours to build what Shotstack/FFmpeg does natively
- Community mostly focused on math — limited help for video production use cases

---

## 3. MOVIEPY (Current Baseline)

### 3A. Quick Summary
MoviePy is a Python library for video editing (cut, concatenate, composite, effects, text). Our current assembly.py uses `ffmpeg-python` (thin FFmpeg wrapper) rather than MoviePy directly, but MoviePy is the standard Python alternative.

### 3B. Key Characteristics
- **Cost**: Free, open-source (MIT)
- **Ken Burns**: Manual implementation via `resize` + `crop` with time functions
- **Text**: `TextClip` via ImageMagick — decent quality, but depends on ImageMagick install
- **Transitions**: `CrossFadeIn`/`CrossFadeOut`, `CompositeVideoClip` for overlays
- **Audio**: Native audio mixing, concatenation, volume control
- **Performance**: Slower than raw FFmpeg — loads frames into memory
- **macOS 11**: Compatible with Python 3.8+, requires FFmpeg + ImageMagick
- **Dev time**: Moderate — well-documented, many examples
- **Output**: Any FFmpeg-supported format (H.264, ProRes, etc.)
- **Limitation**: Memory-hungry for long/high-res videos, no GPU acceleration

---

## 4. CAPCUT API

### 4A. Status
As of April 2026, **CapCut does NOT offer a public API** for automated video rendering. Their "Open Platform" is limited to building plugins inside the CapCut editor. No server-side/headless rendering available.

### 4B. Community Workarounds
- `VectCutAPI` (GitHub) — open-source reverse-engineered API with MCP support
- Unreliable, could break at any time
- **Verdict**: NOT viable for production pipeline

---

## 5. COMPARISON MATRIX

| Feature | MoviePy | CapCut API | Shotstack | Manim |
|---------|---------|------------|-----------|-------|
| **Headless (no GUI)** | Yes | No (no public API) | Yes (cloud API) | Yes (CLI) |
| **Cost** | Free (MIT) | N/A | Free 20min/mo, then $0.40/min | Free (MIT) |
| **Ken Burns** | Manual code | N/A | Native (6 motions, 3 speeds) | Manual code (complex) |
| **Text quality** | Medium (ImageMagick) | N/A | Good (built-in) | Excellent (Pango) |
| **Transitions** | Basic (crossfade) | N/A | Good (fade, slide, wipe) | Manual only |
| **Audio mixing** | Native | N/A | Native (soundtrack + TTS) | None (post-process) |
| **macOS 11 compat** | Yes | N/A | Yes (cloud, no local deps) | Yes (needs Homebrew) |
| **Vertical 1080x1920** | Yes | N/A | Yes (custom resolution) | Yes |
| **Dev time estimate** | 8-15h | N/A | 4-8h | 40-80h |
| **Output quality** | High (FFmpeg backend) | N/A | Good (H.264, some compression) | High (vector+raster) |
| **Render speed (90s)** | 2-5 min local | N/A | ~30s cloud | 5-15 min local |
| **Dependencies** | FFmpeg + ImageMagick | N/A | None (cloud API) | Cairo + Pango + FFmpeg |
| **Vendor lock-in** | None | N/A | Medium (cloud dependency) | None |
| **Parameterization** | Python code | N/A | JSON templates | Python code |
| **Offline capable** | Yes | N/A | No (requires internet) | Yes |
| **Bitrate control** | Full (FFmpeg) | N/A | Limited (quality presets) | Full (FFmpeg) |

---

## 6. RECOMMENDATION FOR FLUXION

### 6A. Current Pipeline Assessment
The current `assembly.py` uses `ffmpeg-python` (thin wrapper around FFmpeg CLI). This is:
- **Working**: Produces 9x16 and 16x9 videos with text overlays, voiceover, music
- **Free**: Zero cost
- **Full control**: Bitrate, codec, resolution, all FFmpeg filters available
- **Limitation**: Ken Burns and transitions require complex filter graphs, text quality is basic

### 6B. Ranked Recommendations

**Rank 1: Shotstack API (for production pipeline)**
- Best fit for FLUXION's use case: JSON template per vertical, Ken Burns native, audio mixing, vertical video
- Free 20 min/month covers all 9 videos
- 30s render time vs 2-5 min locally
- Dev time: 4-8h to build template + API integration
- Risk: cloud dependency, vendor lock-in
- **GUARDRAIL 1 compliance**: Free tier sufficient for production. Iteration in sandbox (watermarked) is free. Only risk is heavy re-iteration exceeding 20 min/month.

**Rank 2: FFmpeg-python (current, enhanced)**
- Already working — enhance with Ken Burns filter complex, better transitions
- Zero cost, zero vendor risk, full control
- Dev time: 8-15h to add Ken Burns + transitions to existing assembly.py
- Recommended if: Shotstack free tier proves insufficient or quality unacceptable

**Rank 3: MoviePy (alternative to raw FFmpeg)**
- Slightly easier API than raw FFmpeg for compositing
- Same capabilities, worse performance
- Only worth switching if FFmpeg filter graphs become unmaintainable
- Dev time: 10-20h (rewrite assembly.py + add features)

**Rank 4: Manim (NOT recommended)**
- Wrong tool for the job — designed for math animations, not video production
- Would require FFmpeg anyway for audio + final assembly
- 40-80h dev time for inferior result
- Only useful if: we need broadcast-quality animated text overlays (consider as a text-animation sub-tool only)

### 6C. Hybrid Strategy (Gold Standard)
```
PRODUCTION PIPELINE:
  Veo 3 clips (AI footage) ──┐
  Screenshots FLUXION ────────┤
  Edge-TTS voiceover ─────────┤──→ Shotstack API (JSON template) ──→ MP4 1080x1920
  Background music ────────────┤
  Text overlays (CTA, prezzi) ┘

FALLBACK (if Shotstack unavailable/over-quota):
  Same assets ──→ FFmpeg-python assembly.py (enhanced) ──→ MP4 1080x1920
```

### 6D. Shotstack Integration Sketch
```python
# Per-vertical JSON template
template = {
    "timeline": {
        "soundtrack": {"src": voiceover_url, "effect": "fadeOut"},
        "background": "#000000",
        "tracks": [
            {  # Track 1: Text overlays (top layer)
                "clips": [
                    {"asset": {"type": "title", "text": "FLUXION", "style": "subtitle"},
                     "start": 0, "length": 3, "transition": {"in": "fade"}},
                    {"asset": {"type": "title", "text": "€497 — Licenza Lifetime"},
                     "start": 80, "length": 10}
                ]
            },
            {  # Track 2: Screenshots + Ken Burns
                "clips": [
                    {"asset": {"type": "image", "src": screenshot_url},
                     "start": 0, "length": 8,
                     "effect": "zoomIn",
                     "transition": {"out": "fade"}},
                    # ... more clips
                ]
            },
            {  # Track 3: Veo 3 B-roll clips
                "clips": [
                    {"asset": {"type": "video", "src": veo3_clip_url},
                     "start": 8, "length": 10,
                     "transition": {"in": "fade", "out": "fade"}}
                ]
            }
        ]
    },
    "output": {
        "format": "mp4",
        "resolution": "hd",
        "aspectRatio": "9:16",
        "fps": 30
    }
}
```

---

## 7. COST ANALYSIS (GUARDRAIL 1)

| Scenario | Shotstack Cost | FFmpeg Cost |
|----------|---------------|-------------|
| 9 videos x 90s (initial) | Free (13.5 min < 20 min quota) | Free |
| 9 videos x 3 iterations | Free (40.5 min → 20 free + $8.20) | Free |
| Monthly refresh (9 videos) | Free if <= 20 min | Free |
| 50 videos (future verticals) | ~$30 ($0.40 x 75 min) | Free |

**Verdict**: For current scope (9 videos, occasional re-render), Shotstack free tier is sufficient. If video production scales significantly, FFmpeg fallback avoids cost escalation.

---

## Sources

### Shotstack
- [Shotstack Pricing](https://shotstack.io/pricing/)
- [Shotstack Limitations](https://shotstack.io/docs/guide/architecting-an-application/limitations/)
- [Shotstack API Reference](https://shotstack.io/docs/api/)
- [Ken Burns Templates](https://shotstack.io/templates/ken-burns-effect-slideshow/)
- [Ken Burns Community Discussion](https://community.shotstack.io/t/ken-burns-effect/136)
- [Rendering Speeds Benchmark](https://shotstack.io/learn/rendering-speeds-benchmark/)
- [Output Quality Discussion](https://community.shotstack.io/t/output-video-quality-is-not-as-good-as-original-asset-with-hd/570)
- [Shotstack Python SDK](https://github.com/shotstack/shotstack-sdk-python)
- [Audio Mixing Discussion](https://community.shotstack.io/t/how-can-i-stitch-multiple-audio-files-and-add-background-music/583)
- [Resize and Crop Guide](https://shotstack.io/learn/crop-resize-videos/)

### Manim
- [Manim Community v0.20.1 — Installation](https://docs.manim.community/en/stable/installation.html)
- [Manim ImageMobject](https://docs.manim.community/en/stable/reference/manim.mobject.types.image_mobject.ImageMobject.html)
- [Manim Text Rendering Guide](https://docs.manim.community/en/stable/guides/using_text.html)
- [Manim Output Settings](https://docs.manim.community/en/stable/tutorials/output_and_config.html)
- [Manim Performance Guide](https://docs.manim.community/en/stable/contributing/performance.html)
- [Using Manim for UI Animations — Smashing Magazine](https://www.smashingmagazine.com/2025/04/using-manim-making-ui-animations/)
- [Manim OpenGL Renderer Guide](https://nkugwamarkwilliam.medium.com/mastering-manims-opengl-renderer-a-comprehensive-guide-for-2025-dd31df7460ac)
- [3b1b/manim GitHub](https://github.com/3b1b/manim)

### MoviePy & Comparisons
- [Video as Code: Which Library Should You Choose?](https://sumeetkg.medium.com/video-as-code-which-library-should-you-choose-8807ac1bda6b)
- [Best Open Source Video Editor SDKs 2025](https://img.ly/blog/best-open-source-video-editor-sdks-2025-roundup/)
- [CapCut API Status 2026](https://samautomation.work/capcut-api/)

### Existing FLUXION Research
- `.claude/cache/agents/video-pipeline-composition-research-2026.md` — Remotion + MoviePy analysis
- `.claude/cache/agents/json-to-video-research-2026.md` — jsontovideo.org + Veo 3.1 analysis
