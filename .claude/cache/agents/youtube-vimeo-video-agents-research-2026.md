# YouTube & Vimeo Video Agents Research 2026
> Deep Research CoVe 2026 — Video Marketing Strategy for FLUXION
> Date: 2026-03-23 | Sources: 15+ web searches, official APIs, MCP ecosystem

---

## TABLE OF CONTENTS
1. [YouTube Data API v3 — Upload & Management](#1-youtube-data-api-v3)
2. [Vimeo API — Upload, Embed, Privacy](#2-vimeo-api)
3. [YouTube SEO Best Practices 2026](#3-youtube-seo-2026)
4. [MCP Servers for YouTube/Vimeo](#4-mcp-servers)
5. [Video Marketing Automation Tools](#5-automation-tools)
6. [Italian PMI Market Specifics](#6-italian-market)
7. [YouTube Shorts / Reels B2B Strategy](#7-shorts-strategy)
8. [Video Repurposing Pipeline](#8-repurposing)
9. [Subtitle/SRT Optimization (Italian)](#9-subtitles)
10. [Video SEO — Schema Markup & Sitemaps](#10-video-seo-schema)
11. [AI Agent Team Architecture](#11-agent-team)
12. [FLUXION Action Plan](#12-action-plan)

---

## 1. YouTube Data API v3 — Upload & Management

### Authentication
- **OAuth 2.0 REQUIRED** — service accounts do NOT work for uploads
- Need Google Cloud project with YouTube Data API v3 enabled
- Get refresh token once, use it for all subsequent uploads
- Client type: "Desktop app" in Google Cloud Console

### Upload (videos.insert)
- **Endpoint**: `POST https://www.googleapis.com/upload/youtube/v3/videos`
- Max file size: **256 GB**
- Accepted types: `video/*`
- Quota cost: **1,600 units per upload** (daily limit: 10,000 units = ~6 uploads/day)
- Supports resumable uploads for large files

### CRITICAL RESTRICTION: Unverified API Projects
- **Projects created after July 28, 2020**: all uploaded videos are LOCKED AS PRIVATE
- To make videos public: must pass Google API audit (compliance review)
- **NO workaround exists** — this is enforced server-side
- **Recommendation for FLUXION**: Upload first video manually via YouTube Studio, use API only for metadata updates, thumbnails, and analytics
- Alternative: Apply for API audit (takes weeks, requires privacy policy, TOS compliance)

### Thumbnail Upload (thumbnails.set)
- Max file size: **2 MB**
- Accepted: image/jpeg, image/png
- Quota cost: **50 units**
- Python sample: `youtube/api-samples/python/upload_thumbnail.py`

### Chapters (Timestamps)
- **No dedicated API endpoint** — chapters are set via video description text
- Format: timestamps in description starting with `00:00`
- Minimum 3 timestamps, minimum 10 seconds each
- Format: `MM:SS Title` (under 1 hour) or `HH:MM:SS Title` (over 1 hour)
- YouTube also offers auto-generated chapters (AI-based), but quality is mediocre
- **Best practice**: Always provide manual chapters for SEO + UX

### Metadata Update (videos.update)
- Can update title, description, tags, category, privacy status
- Quota cost: **50 units**
- Useful for A/B testing titles/descriptions programmatically

### Key Python Libraries
```python
# Official Google API Client
pip install google-api-python-client google-auth-oauthlib

# Third-party wrapper
pip install python-youtube  # PyPI: python-youtube
```

### Quota Management
| Operation | Cost (units) |
|-----------|-------------|
| videos.insert (upload) | 1,600 |
| videos.update (metadata) | 50 |
| thumbnails.set | 50 |
| videos.list | 1 |
| search.list | 100 |
| **Daily limit** | **10,000** |

---

## 2. Vimeo API — Upload, Embed, Privacy

### Authentication
- OAuth 2.0 with personal access token or app credentials
- API endpoint: `https://api.vimeo.com`

### Upload Methods
- **Python SDK**: `pip install PyVimeo` — `client.upload(filepath, data={...})`
- **Node.js SDK**: `npm install vimeo` — official Vimeo library
- Default chunk size: 200 MB
- Supports tus (resumable upload protocol)

### Embed Settings
- Domain-level privacy: restrict embeds to specific domains (e.g., `fluxion-landing.pages.dev`)
- Player parameters: `data-vimeo-portrait="false"`, autoplay, loop, etc.
- Customizable player: branding, controls, colors
- oEmbed support for private videos (with additional config)

### Privacy Options
| Setting | Description |
|---------|-------------|
| Public | Anyone can view |
| Unlisted | Only people with link |
| Password | Requires password |
| Domain-restricted | Only on specific domains |
| Private | Only you |

### Pricing (2026)
| Plan | Price | Storage | Key Features |
|------|-------|---------|--------------|
| Free | $0 | 1 GB | Single user, basic |
| Starter | $12/mo | 100 GB | Basic analytics |
| Standard | $25/mo | 5 TB | Team, advanced embed |
| Advanced | $65/mo | 7 TB | Marketing tools, CTA |
| Enterprise | Custom | Unlimited | SSO, branded player |

### FLUXION Recommendation
- **Free tier** (1 GB) is too limited for video hosting
- **For landing page embed**: Use Vimeo Standard ($25/mo) for ad-free player + domain privacy
- **Zero-cost alternative**: Host on YouTube (unlisted) + embed with custom player wrapper
- **Best option**: YouTube for SEO/discovery + Vimeo Standard for landing page premium embed

---

## 3. YouTube SEO Best Practices 2026

### Algorithm Evolution
- **2026 focus**: Viewer satisfaction > raw watch time
- **Retention** outweighs total minutes — a 5-min video with 80% retention beats 20-min with 30%
- AI-powered search (YouTube + Google AI Overviews) increasingly uses structured data

### Title Optimization
- **Keep under 60 characters** (mobile truncation)
- **Front-load the keyword**: "Gestionale per Parrucchieri — FLUXION Demo" (NOT "FLUXION Demo — Gestionale...")
- **Include power words**: "Completo", "Gratis", "2026", "Migliore"
- **Italian-specific**: Use terms PMI actually search: "gestionale", "prenotazioni", "appuntamenti"

### Description Best Practices
- **First 150 characters** appear in search — put keyword + value prop here
- **Include chapters** (timestamps) for rich snippets
- **2000+ characters** for full SEO value
- Include links: landing page, social, related videos
- Italian + English bilingual description for broader reach

### Tags Strategy
- Primary tag = exact target keyword
- Include variations: singular/plural, synonyms
- Mix broad + specific: "gestionale" + "gestionale parrucchieri" + "software prenotazioni salone"
- **Max 500 characters** total for tags
- vidIQ/TubeBuddy can suggest optimal tags

### Example Optimized Metadata for FLUXION
```
Title: Gestionale per Parrucchieri 2026 — FLUXION Demo Completa
Description (first 150 chars): Scopri FLUXION, il gestionale completo per saloni con prenotazioni WhatsApp,
assistente vocale Sara e cassa integrata. Demo completa 2026.

Chapters:
00:00 Introduzione — Il Problema delle PMI
01:15 Dashboard e Calendario
02:30 Prenotazioni WhatsApp Automatiche
03:45 Sara — Assistente Vocale AI
05:00 Schede Clienti e Storico
06:00 Come Acquistare FLUXION

Tags: gestionale parrucchieri, software salone bellezza, prenotazioni online parrucchiere,
gestionale PMI italiano, FLUXION, assistente vocale prenotazioni, WhatsApp prenotazioni,
software gestionale piccole imprese
```

### Thumbnail Best Practices
- **1280x720px** minimum (16:9 aspect ratio)
- **High contrast** text overlay (max 5-6 words)
- **Face + emotion** outperforms abstract graphics 2:1
- **Brand consistency**: same color scheme, logo placement
- **A/B test** via TubeBuddy Legend plan or manually

---

## 4. MCP Servers for YouTube/Vimeo

### YouTube MCP Servers (Top 3 for FLUXION)

#### 1. ZubeidHendricks/youtube-mcp-server (RECOMMENDED)
- **Stars**: 490+ | Most popular YouTube MCP
- **Features**: Video management, Shorts creation, analytics
- **Install**: `npx -y @smithery/cli install @ZubeidHendricks/youtube --client claude`
- **Capabilities**: Get video details, list channel videos, get statistics, search, transcripts, playlist management
- **Requires**: YouTube Data API v3 key

#### 2. Yashkashte5/Youtube-MCP (Production-grade)
- **16 specialized tools** for YouTube analytics/automation
- Channel intelligence, video analytics, SEO scoring, tag analysis
- Comment extraction, keyword analysis, audience insights
- Best for: **Analytics and SEO optimization**

#### 3. anaisbetts/mcp-youtube (Transcript-focused)
- Uses yt-dlp for subtitle/transcript extraction
- Lightweight, focused on content analysis
- Best for: **Transcript extraction and content repurposing**

#### 4. YouTube Analytics MCP (Read-only)
- Real-time YouTube Analytics data via natural language
- No SQL needed — ask Claude directly
- Best for: **Performance monitoring**

### Vimeo MCP Servers
- **No dedicated Vimeo MCP server found** as of March 2026
- Vimeo API is REST-based and can be called via Bash/fetch from Claude Code
- **Opportunity**: Build a simple Vimeo MCP wrapper if needed

### Integration with Claude Code
Add to `.claude.json` or `~/.claude.json`:
```json
{
  "mcpServers": {
    "youtube": {
      "command": "npx",
      "args": ["-y", "@anthropic/youtube-mcp"],
      "env": {
        "YOUTUBE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

---

## 5. Video Marketing Automation Tools

### Free/Low-Cost Tools for FLUXION

| Tool | Cost | Key Feature | Use Case |
|------|------|-------------|----------|
| **TubeBuddy** (free tier) | $0 | Basic SEO, 25 keyword searches/day | Keyword research |
| **vidIQ** (free tier) | $0 | Competitor tracking, AI suggestions | Channel analysis |
| **SocialPilot** | $25/mo | YouTube + multi-platform scheduling | Publishing automation |
| **OpusClip** (free tier) | $0 (limited) | AI video repurposing | Shorts from long video |
| **2short.ai** | $0 (limited) | Highlight detection | Quick clip extraction |
| **Canva** (free) | $0 | Thumbnail design | Thumbnail A/B variants |

### Premium Tools (If Budget Allows)

| Tool | Cost | Key Feature |
|------|------|-------------|
| **TubeBuddy Legend** | $49/mo | A/B thumbnail testing |
| **Sprout Social** | $249/mo | Full YouTube analytics suite |
| **Hootsuite** | $99/mo | Multi-platform dashboard |
| **ContentStudio** | $25/mo | AI content optimization |

### Zero-Cost Automation Stack (RECOMMENDED for FLUXION)
1. **TubeBuddy Free** — keyword research (25/day)
2. **vidIQ Free** — competitor analysis
3. **OpusClip Free** — repurpose 1 long video into Shorts
4. **Canva Free** — thumbnail design
5. **YouTube Studio** — native analytics (free, comprehensive)
6. **YouTube MCP Server** — Claude Code integration for analysis
7. **Custom Python scripts** — upload, metadata update, SRT upload

### Open-Source YouTube Automation
- **darkzOGx/youtube-automation-agent** (GitHub)
  - Fully automated channel management with AI agents
  - Works with FREE Gemini API or OpenAI
  - Creates, optimizes & publishes videos 24/7
  - Configurable posting frequency, privacy settings
  - **Good reference architecture** for building FLUXION's own agent

---

## 6. Italian PMI Market Specifics

### Market Opportunity
- **45 million** Italian monthly YouTube users
- **70% of Italian SMEs** don't have an active YouTube channel
- **Massive competitive advantage** for early movers in 2026
- YouTube Ads cost per lead: **30-50% lower** than Meta/Google Search in Italy

### Content Strategy for Italian PMI
- **Tutorial videos** ("Come fare X") are the most searched and have longest shelf life
- YouTube algorithms favor **consistency and quality over frequency** — perfect for small teams
- **Problem-first approach**: Address pain points PMI owners actually have
- Videos rank on Google Italia for YEARS — evergreen lead generation

### Italian-Specific Keywords (High Volume, Low Competition)
```
gestionale parrucchiere 2026
software prenotazioni salone
gestionale palestra piccola
software gestione clienti PMI
prenotazioni online WhatsApp
assistente vocale prenotazioni
gestionale officina meccanica
software agenda appuntamenti
gestionale centro estetico
programma per gestire clienti
```

### Content Calendar for Italian PMI Audience
| Week | Long-Form (10-15 min) | Shorts (30-60 sec) |
|------|----------------------|---------------------|
| 1 | "Come gestire un salone nel 2026" (tutorial) | 3x feature highlights |
| 2 | "FLUXION Demo Completa" (product) | 3x before/after clips |
| 3 | "Sara: L'assistente vocale per il tuo salone" | 3x Sara conversations |
| 4 | Case study / testimonial | 3x tips for PMI owners |

### Posting Schedule
- **Best times for Italian B2B**: Tuesday-Thursday, 10:00-12:00 or 14:00-16:00
- **Frequency**: 1 long-form/week + 3 Shorts/week minimum
- **Consistency > frequency** for the algorithm

### AI Adoption in Italian SMEs
- By 2026, **45% of Italian SMEs** expected to use AI tools for marketing
- FLUXION's AI features (Sara, WhatsApp automation) are differentiators
- Italian PMI owners respond to **practical demonstrations** over feature lists

---

## 7. YouTube Shorts / Reels B2B Strategy

### Why Shorts Matter for B2B in 2026
- **53% of B2B buyers** watch short-form video before requesting a demo
- Companies with Shorts + long-form see **41% faster channel growth**
- **74% higher subscriber conversion** when Shorts link to longer videos
- YouTube Shorts excels at **educational content** — perfect for software demos

### The "Barbell Strategy" (YouTube's Recommended 2026)
```
SHORT-FORM (< 60 sec)          LONG-FORM (> 10 min)
- Feature highlights            - Full product demos
- Quick tips                    - Tutorials
- Before/after                  - Case studies
- Sara voice clips              - Webinars
- "Did you know?" facts         - Behind the scenes
```
Skip medium-length (3-7 min) — worst of both worlds.

### High-Performing B2B Short Content Types
1. **15-second product feature highlights** — one feature per Short
2. **Quick tutorials** extracted from longer content
3. **Founder/expert clips** — thought leadership
4. **Customer success moments** — testimonials
5. **FAQ responses** — answer one question per Short
6. **Before/after** transformations (manual booking vs. FLUXION)

### Shorts SEO Optimization
- **Title**: Include keyword, under 40 characters
- **Description**: Full keyword-rich description (100+ characters)
- **Hashtags**: #Shorts + 2-3 niche tags (#GestionaleItaliano #SoftwarePMI)
- **Hook in first 2 seconds** — text overlay + movement
- **Vertical 9:16** format, 1080x1920 resolution
- **Add captions** — 85% of Shorts watched on mute

### Platform-Specific Optimization
| Platform | Best For | Tone |
|----------|----------|------|
| YouTube Shorts | Searchable, evergreen content | Educational, professional |
| Instagram Reels | Polished visuals, branding | Aspirational, visual |
| TikTok | Trending, casual | Informal, entertaining |

**FLUXION priority**: YouTube Shorts first (SEO value), then Reels (visual brand).

---

## 8. Video Repurposing Pipeline

### From 1 Long Video to 15+ Content Pieces
```
1 FLUXION Demo Video (6-10 min)
  |
  +---> 5-8 YouTube Shorts (15-60 sec each)
  +---> 5-8 Instagram Reels (same clips, reformatted)
  +---> 1 Blog post (transcript + screenshots)
  +---> 5-10 Social media posts (key frames + quotes)
  +---> 1 Email newsletter (highlights + link)
  +---> 1 Landing page embed (full video)
```

### AI Tools for Repurposing

#### OpusClip (RECOMMENDED — Best in Class 2026)
- **10M+ users**, 172M+ clips generated
- Paste YouTube URL or upload MP4
- AI generates 10-25 clips automatically
- Features: animated captions (97%+ accuracy), virality score, auto-reframe to vertical
- **Free tier**: Limited clips/month
- **API available** for automation integration
- **Price**: Free tier / $15/mo Pro

#### 2short.ai
- Scans video for engaging moments
- Adds animated subtitles, facial tracking
- Exports platform-optimized Shorts
- Less automated than OpusClip (marks highlights, requires manual clipping)

#### Manual/Custom Pipeline (ZERO COST)
```python
# Using ffmpeg + Python (already available on MacBook)
# 1. Extract clips at chapter timestamps
# 2. Add Italian captions from SRT
# 3. Reframe to 9:16 vertical
# 4. Add text overlays with Pillow
# 5. Export as Shorts-ready MP4
```

### Recommended Workflow for FLUXION
1. **Produce** 1 long-form demo video per month
2. **Auto-extract** 8-10 Shorts via OpusClip free tier
3. **Manually refine** top 3-5 clips (add FLUXION branding, CTA)
4. **Schedule** via YouTube Studio (free) or SocialPilot
5. **Track performance** via YouTube Analytics + MCP Server

---

## 9. Subtitle/SRT Optimization (Italian)

### Why SRT Matters for SEO
- Search engines **cannot index video content** directly — captions provide text
- YouTube uses captions for **content understanding and keyword matching**
- Italian SRT with proper keywords improves discoverability in Google.it
- **Accessibility compliance** (growing requirement in EU/Italy)

### SRT Format Best Practices
```srt
1
00:00:00,000 --> 00:00:04,500
FLUXION e il gestionale completo
per il tuo salone di bellezza.

2
00:00:04,500 --> 00:00:09,000
Gestisci prenotazioni, clienti e incassi
tutto da un'unica applicazione.
```

### Optimization Rules
| Rule | Details |
|------|---------|
| **Reading speed** | 10-15 characters/second for Italian |
| **Line length** | Max 42 characters per line |
| **Lines per subtitle** | Max 2 lines |
| **Duration** | Min 1 second, max 7 seconds per subtitle |
| **Accuracy** | Review auto-generated captions (YouTube auto-IT has ~85% accuracy) |
| **Keywords** | Naturally include target keywords in spoken content |
| **Punctuation** | Proper Italian punctuation improves readability |

### Upload Process
1. Generate SRT with Edge-TTS timing or manual sync
2. Review for accuracy (especially Italian terms: "parrucchiere", "gestionale")
3. Upload via YouTube Studio: Video > Subtitles > Add Language > Upload SRT
4. OR via API: `captions.insert` endpoint (50 quota units)

### Multilingual Strategy
- **Primary**: Italian (it) — full SRT
- **Secondary**: English (en) — expand reach to Italian diaspora + international PMI
- YouTube auto-translate is unreliable for technical terms — manual translation recommended

### FLUXION SRT Already Available
- `landing/assets/fluxion-demo.srt` — existing SRT from video V5
- Ensure keyword density covers: gestionale, prenotazioni, WhatsApp, Sara, salone, clienti

---

## 10. Video SEO — Schema Markup & Sitemaps

### VideoObject Schema (JSON-LD)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "FLUXION — Gestionale per Parrucchieri 2026 | Demo Completa",
  "description": "Scopri FLUXION, il gestionale completo per saloni di bellezza con prenotazioni WhatsApp, assistente vocale Sara e cassa integrata.",
  "thumbnailUrl": "https://fluxion-landing.pages.dev/assets/fluxion-demo-thumbnail.png",
  "uploadDate": "2026-03-23T00:00:00+01:00",
  "duration": "PT6M40S",
  "contentUrl": "https://www.youtube.com/watch?v=VIDEO_ID",
  "embedUrl": "https://www.youtube.com/embed/VIDEO_ID",
  "publisher": {
    "@type": "Organization",
    "name": "FLUXION",
    "logo": {
      "@type": "ImageObject",
      "url": "https://fluxion-landing.pages.dev/assets/logo.png"
    }
  },
  "inLanguage": "it",
  "hasPart": [
    {
      "@type": "Clip",
      "name": "Introduzione",
      "startOffset": 0,
      "endOffset": 75,
      "url": "https://www.youtube.com/watch?v=VIDEO_ID&t=0"
    },
    {
      "@type": "Clip",
      "name": "Dashboard e Calendario",
      "startOffset": 75,
      "endOffset": 150,
      "url": "https://www.youtube.com/watch?v=VIDEO_ID&t=75"
    }
  ]
}
</script>
```

### Video Sitemap
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
  <url>
    <loc>https://fluxion-landing.pages.dev/</loc>
    <video:video>
      <video:thumbnail_loc>https://fluxion-landing.pages.dev/assets/fluxion-demo-thumbnail.png</video:thumbnail_loc>
      <video:title>FLUXION — Gestionale per Parrucchieri 2026</video:title>
      <video:description>Gestionale completo per saloni con prenotazioni WhatsApp e assistente vocale Sara.</video:description>
      <video:content_loc>https://www.youtube.com/watch?v=VIDEO_ID</video:content_loc>
      <video:duration>400</video:duration>
      <video:publication_date>2026-03-23T00:00:00+01:00</video:publication_date>
      <video:family_friendly>yes</video:family_friendly>
      <video:restriction relationship="allow">IT</video:restriction>
      <video:tag>gestionale parrucchieri</video:tag>
      <video:tag>software salone bellezza</video:tag>
      <video:tag>prenotazioni WhatsApp</video:tag>
      <video:category>Science &amp; Technology</video:category>
    </video:video>
  </url>
</urlset>
```

### Key Rules
- **ISO 8601 dates** — wrong format = Google rejects entire schema
- **Consistency** across schema, sitemap, and meta tags
- **Structured data matters more than ever in 2026** — AI search relies on it
- Submit video sitemap via Google Search Console
- Use `Clip` schema for chapters — enables "Key Moments" in Google results

---

## 11. AI Agent Team Architecture

### What a Video-Department AI Agent Team Should Do

```
                    VIDEO DEPARTMENT AI AGENTS
                    ==========================

    [STRATEGIST AGENT]
    - Keyword research (Italian PMI terms)
    - Content calendar planning
    - Competitor analysis (what are Italian competitors posting?)
    - Topic selection based on search trends

    [PRODUCTION AGENT]
    - Script generation from templates
    - TTS voiceover generation (Edge-TTS IsabellaNeural)
    - Screenshot capture automation
    - Video composition (ffmpeg pipeline)
    - Thumbnail generation (Canva API or Pillow)

    [SEO AGENT]
    - Title/description optimization
    - Tag generation
    - Chapter timestamp formatting
    - SRT subtitle generation + keyword optimization
    - VideoObject schema generation
    - Video sitemap updates

    [DISTRIBUTION AGENT]
    - Upload to YouTube (API or manual)
    - Upload to Vimeo (API)
    - Embed updates on landing page
    - Cross-post to social platforms

    [REPURPOSING AGENT]
    - Extract Shorts from long-form (OpusClip API or ffmpeg)
    - Reformat for Instagram Reels
    - Generate social media posts from video content
    - Create blog post from transcript

    [ANALYTICS AGENT]
    - YouTube Analytics via MCP Server
    - Performance tracking (views, retention, CTR)
    - A/B test results analysis
    - Monthly report generation
    - Recommendations for next content cycle
```

### Implementation Priority for FLUXION

**Phase 1 (NOW — Zero Cost)**:
1. Manual YouTube upload of promo-v5.mp4
2. Optimized metadata (title, description, chapters, tags)
3. SRT upload (Italian)
4. VideoObject schema on landing page
5. Video sitemap submission

**Phase 2 (Month 1 — Zero Cost)**:
1. Install YouTube MCP Server in Claude Code
2. Extract 5-8 Shorts from promo-v5 using OpusClip free tier
3. Set up content calendar (1 long-form + 3 Shorts/week)
4. TubeBuddy free for keyword research

**Phase 3 (Month 2-3 — Minimal Cost)**:
1. Build custom Python upload/metadata script
2. Automate SRT generation from video pipeline
3. A/B test thumbnails (manual or TubeBuddy Legend trial)
4. Vimeo Standard for landing page premium embed

**Phase 4 (Month 3+ — Scale)**:
1. Full AI agent pipeline (script -> produce -> optimize -> publish)
2. Weekly Shorts automation
3. Analytics dashboard integration
4. Multi-platform distribution (YouTube + Vimeo + Instagram)

---

## 12. FLUXION Action Plan — Immediate Steps

### Step 1: Upload promo-v5.mp4 to YouTube (TODAY)
```
1. Go to YouTube Studio (studio.youtube.com)
2. Upload landing/assets/fluxion-promo-v5.mp4
3. Set metadata:
   - Title: "FLUXION — Gestionale Completo per PMI Italiane | Demo 2026"
   - Description: (use template from Section 3)
   - Tags: (use keywords from Section 6)
   - Chapters: (from video-production-v5.json)
   - Category: Science & Technology
   - Language: Italian
4. Upload thumbnail: landing/assets/fluxion-demo-thumbnail.png
5. Upload SRT: landing/assets/fluxion-demo.srt
6. Set privacy: Public
7. Add end screen + cards
```

### Step 2: Upload to Vimeo (TODAY)
```
1. Create free Vimeo account (if not exists)
2. Upload promo-v5.mp4
3. Set domain privacy: only fluxion-landing.pages.dev
4. Get embed code for landing page
5. Consider upgrading to Standard ($25/mo) for ad-free player
```

### Step 3: Add Video SEO to Landing Page
```
1. Add VideoObject JSON-LD schema to index.html
2. Create video-sitemap.xml
3. Submit to Google Search Console
4. Embed YouTube player (public SEO value) or Vimeo (premium UX)
```

### Step 4: Set Up YouTube MCP Server
```bash
# Add to Claude Code MCP config
npx -y @smithery/cli install @ZubeidHendricks/youtube --client claude

# Or manual config in .claude.json:
# "youtube": { "command": "npx", "args": [...], "env": { "YOUTUBE_API_KEY": "..." } }
```

### Step 5: Create Shorts Pipeline
```
1. Use OpusClip free tier to extract 5-8 Shorts from promo-v5
2. Add FLUXION branding/watermark
3. Upload to YouTube Shorts
4. Schedule 2-3 per week
```

---

## KEY DECISIONS

| Decision | Choice | Reason |
|----------|--------|--------|
| Primary video platform | **YouTube** | SEO, 45M Italian users, free, chapters |
| Landing page embed | **YouTube embed** (free) or **Vimeo Standard** ($25/mo) | Ad-free Vimeo vs. free YouTube |
| Upload method | **Manual** (YouTube Studio) | API audit restriction for new projects |
| Metadata management | **YouTube MCP Server + Python scripts** | Zero cost, Claude Code integration |
| Shorts creation | **OpusClip free tier** | Best AI repurposing, free |
| Thumbnail design | **Canva free** | Professional templates, zero cost |
| Analytics | **YouTube Studio + MCP Server** | Free, comprehensive |
| Subtitles | **Custom SRT upload** | Better accuracy than auto-generated |
| Schema markup | **VideoObject JSON-LD** | Google rich results, AI search |

---

## SOURCES

### YouTube Data API
- [YouTube Data API v3 — videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert)
- [Upload a Video Guide](https://developers.google.com/youtube/v3/guides/uploading_a_video)
- [YouTube API Quota Calculator](https://developers.google.com/youtube/v3/docs)
- [From Zero to First Upload (2025 Guide)](https://medium.com/@dorangao/from-zero-to-first-upload-a-from-scratch-guide-to-publishing-videos-to-youtube-via-api-2025-73251a9324bd)
- [YouTube Upload API Guide 2026](https://getlate.dev/blog/youtube-upload-api)
- [YouTube API Setup Guide 2026](https://zernio.com/blog/youtube-api)

### Vimeo API
- [Vimeo Upload API Guide](https://developer.vimeo.com/api/guides/videos/upload)
- [Vimeo Privacy Settings API](https://help.vimeo.com/hc/en-us/articles/12427776819089)
- [Vimeo Embed Settings Reference](https://developer.vimeo.com/api/reference/response/embed-settings)
- [Vimeo Player SDK](https://developer.vimeo.com/player/sdk/embed)
- [Vimeo Python SDK](https://github.com/vimeo/vimeo.py)
- [Vimeo Node.js Examples](https://developer.vimeo.com/api/libraries/examples/nodejs)

### YouTube SEO 2026
- [YouTube SEO Best Practices 2026](https://seocircular.com/blogs/strategies/youtube-seo-best-practices/)
- [The 2026 YouTube Shift for Business](https://www.techwyse.com/blog/video-marketing/youtube-marketing-shift-for-business-2026)
- [YouTube SEO Optimization Complete Guide 2026](https://influenceflow.io/resources/youtube-seo-optimization-techniques-the-complete-2026-guide/)
- [Search-First YouTube Content Strategy 2026](https://marketingagent.blog/2026/02/16/building-a-search-first-youtube-content-strategy-seo-tips-for-2026/)
- [YouTube SEO: Rank Higher 2026](https://seosherpa.com/youtube-seo/)
- [YouTube Video Marketing for B2B: 2026 Guide](https://whitehat-seo.co.uk/blog/video-marketing-the-youtube-guide)

### MCP Servers
- [ZubeidHendricks/youtube-mcp-server](https://github.com/ZubeidHendricks/youtube-mcp-server)
- [YouTube MCP Server Comparison 2026](https://www.ekamoira.com/blog/youtube-mcp-server-comparison-2026-which-one-should-you-use)
- [anaisbetts/mcp-youtube](https://github.com/anaisbetts/mcp-youtube)
- [sparfenyuk/mcp-youtube](https://github.com/sparfenyuk/mcp-youtube)
- [Yashkashte5/Youtube-MCP](https://glama.ai/mcp/servers/@Yashkashte5/youtube-mcp)
- [Claude Code MCP Docs](https://code.claude.com/docs/en/mcp)

### Video Marketing Automation
- [Best AI Tools for Video Marketing 2026](https://outlierkit.com/blog/best-ai-tools-for-video-marketing)
- [YouTube Marketing Tools 2026 — Sprout Social](https://sproutsocial.com/insights/youtube-marketing-tools/)
- [YouTube Analytics Tools 2026 — Sprout Social](https://sproutsocial.com/insights/youtube-analytics-tools/)
- [YouTube Automation Guide 2026](https://www.revid.ai/blog/youtube-automation)
- [darkzOGx/youtube-automation-agent](https://github.com/darkzOGx/youtube-automation-agent)

### Italian Market
- [YouTube Marketing 2026 Guida Italia](https://www.tready.it/social-media-marketing-news/youtube-marketing-2026-guida/)
- [Video Aziendali per PMI](https://www.paginesispa.it/blog/marketing/il-potere-dei-video-aziendali-di-alta-qualita-vantaggi-per-le-pmi/)
- [Campagne YouTube Ads per PMI Italiane](https://loopsrl.agency/blog/google-ads/campagne-youtube-ads/)
- [Trend Comunicazione Digitale 2026 PMI Italiane](https://www.dscom.it/trend-comunicazione-digitale-2026-guida-pmi-italiane/)
- [Pubblicita su YouTube 2026 Guida PMI](https://myweblab.it/pubblicita-su-youtube/)

### Shorts & Repurposing
- [B2B Short-Form Video Complete Guide 2026](https://koanthic.com/en/b2b-short-form-video-complete-guide-for-2026/)
- [Short-Form Video Strategy 2026 — OpusClip](https://www.opus.pro/blog/short-form-video-strategy-2026)
- [Repurpose One YouTube Video into 50 Content Pieces](https://shortvids.co/guide-to-repurpose-youtube-videos/)
- [OpusClip — AI Video Clipping](https://www.opus.pro/)
- [YouTube Shorts Algorithm 2026 — vidIQ](https://vidiq.com/blog/post/youtube-shorts-algorithm/)
- [Short-Form Video Dominance 2026](https://almcorp.com/blog/short-form-video-mastery-tiktok-reels-youtube-shorts-2026/)

### Video SEO & Schema
- [VideoObject Schema — Google Developers](https://developers.google.com/search/docs/appearance/structured-data/video)
- [Video Schema Markup Guide 2026](https://influenceflow.io/resources/video-schema-markup-and-structured-data-complete-guide-for-2026/)
- [Video SEO Best Practices 2026](https://levitatemedia.com/learn/video-seo-best-practices-2026-advanced-strategies-for-maximum-visibility)
- [Video Schema SEO Guide 2026](https://schemavalidator.org/guides/video-schema-seo-guide)
- [Video SEO Ranking on Google & YouTube 2026](https://www.vdocipher.com/blog/video-seo-best-practices/)

### Subtitles & Chapters
- [YouTube Chapters Guide](https://support.google.com/youtube/answer/9884579)
- [How to Add Timestamps to YouTube 2026](https://screenapp.io/blog/how-to-add-timestamps-to-youtube-videos)
- [YouTube Chapters: Why They Matter 2026](https://humbleandbrag.com/blog/youtube-chapters)
- [YouTube Captioning SEO](https://www.captioningstar.com/blog/youtube-optimization-tips-that-will-boost-your-video-rankings/)
- [Subtitles and SEO — CheckSub](https://www.checksub.com/video-marketing/subtitle-seo-how-improve-video-ranking)
