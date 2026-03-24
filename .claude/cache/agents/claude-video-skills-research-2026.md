# Claude Code Video Generation Skills, MCP Servers & Integrations
> Research date: 2026-03-23 | Status: COMPLETE
> Goal: Find tools to generate AI video or cinematic promotional videos via Claude Code

---

## EXECUTIVE SUMMARY

| Approach | Tool | Cost | Best For | Maturity |
|----------|------|------|----------|----------|
| **Remotion Skill** | `remotion-dev/skills` | FREE (local render) | Motion graphics, product demos, branded promo | PRODUCTION (150K+ installs) |
| **Kie.ai MCP** | `@felores/kie-ai-mcp-server` | Free trial + pay-per-use | AI-generated video clips (Veo3, Seedance, Kling 3.0) | PRODUCTION |
| **Kling MCP** | `mcp-kling` | 66 free credits/day (watermarked 720p) | Quick AI video clips | PRODUCTION |
| **Generative Media Skills** | `SamurAIGPT/Generative-Media-Skills` | muapi.ai credits | 100+ AI models, Seedance 2.0, Kling 3.0, Veo3 | PRODUCTION |
| **HF Spaces Gradio API** | Various (Wan2.2, LTX 2.3, CogVideoX) | FREE (public Spaces) | Image-to-video, text-to-video | USABLE (queue waits) |
| **ComfyUI MCP** | `shawnrushefsky/comfyui-mcp` | FREE (local GPU) | Full pipeline control, any diffusion model | PRODUCTION (needs GPU) |
| **Claude-Remotion Kickstart** | `jhartquist/claude-remotion-kickstart` | FREE (MIT) | Template-based promo videos | PRODUCTION |
| **Claude Code Video Toolkit** | `wilwaldon/Claude-Code-Video-Toolkit` | FREE | Remotion + Manim + FFmpeg + YouTube | PRODUCTION |
| **JSON2Video** | json2video.com | Free tier exists | JSON storyboard to video | PRODUCTION |
| **EachLabs Skill** | `eachlabs-video-generation` | EachLabs credits | Text-to-video, image-to-video, talking head | PRODUCTION |
| **SkillBoss** | `heeyo-life/skillboss-skills` | Unknown pricing | 100+ AI services including video | BETA |

---

## 1. REMOTION + CLAUDE CODE (TOP RECOMMENDATION for FLUXION)

### What It Is
React-based programmatic video framework. Claude Code writes TypeScript/React components, Remotion renders to MP4. Launched Jan 2026, went viral (6M views, 150K+ installs, #1 non-platform skill).

### Why It Fits FLUXION
- Takes screenshots as input, generates motion graphics around them
- Perfect for product demo/promo videos showing UI
- Runs 100% locally -- ZERO cost (just Claude Code subscription)
- Generates .mp4 directly from React components
- Supports crossfade, transitions, text animations, branded overlays
- 1080p output, configurable aspect ratios

### Installation
```bash
npx skills add remotion-dev/skills
```

### Starter Template
```bash
# Full starter with pre-built components
git clone https://github.com/jhartquist/claude-remotion-kickstart
cd claude-remotion-kickstart
pnpm install
```
Pre-built components: title slides, code blocks, diagrams, captions.
Slash commands: `/new-composition`, `/generate-image`, `/generate-video`.

### Cost
- Remotion rendering: FREE for individuals / companies <3 employees
- Companies with 3+ employees need Remotion license
- All rendering is local (no cloud costs)

### How to Use for FLUXION Promo Video
1. Install Remotion skill
2. Place screenshots in assets folder
3. Prompt Claude: "Create a 2:40 promo video using these screenshots with crossfade transitions, text overlays in Italian, and Edge-TTS voiceover"
4. Claude generates React components for each scene
5. `npx remotion render` outputs MP4

### Links
- Official docs: https://www.remotion.dev/docs/ai/claude-code
- Skills: https://www.remotion.dev/docs/ai/skills
- Kickstart template: https://github.com/jhartquist/claude-remotion-kickstart
- Video Toolkit: https://github.com/wilwaldon/Claude-Code-Video-Toolkit

---

## 2. KLING AI MCP SERVER

### What It Is
MCP server connecting Claude to Kling AI's video generation API. 13+ tools for video, image, lip-sync, effects.

### Tools Available
- `generate_video` -- text-to-video
- `generate_image_to_video` -- image-to-video (screenshot animation)
- `extend_video` -- extend existing clips
- `create_lipsync` -- lip sync on video
- `apply_video_effect` -- add effects
- `check_video_status` -- async polling
- `get_account_balance` -- check credits

### Free Tier
- 66 free credits/day
- 5s Standard video = 10 credits (6 videos/day free)
- 10s Standard video = 20 credits (3 videos/day free)
- Watermarked, 720p max on free tier

### Paid
- Standard: $6.99/mo (660 credits)
- API: ~$0.07-0.14/second of video

### Installation
```json
{
  "mcpServers": {
    "mcp-kling": {
      "command": "npx",
      "args": ["-y", "mcp-kling@latest"],
      "env": {
        "KLING_ACCESS_KEY": "YOUR_ACCESS_KEY",
        "KLING_SECRET_KEY": "YOUR_SECRET_KEY"
      }
    }
  }
}
```

### Links
- https://github.com/199-mcp/mcp-kling
- https://github.com/revathi-prasad/Claude-klingAI

---

## 3. KIE.AI MCP SERVER (BEST MULTI-MODEL OPTION)

### What It Is
Unified MCP server accessing 33+ AI models with one API key. Smart intent detection auto-selects models. 21 unified tools.

### Video Models Available
Veo 3, Sora 2, Runway Aleph, Seedance, Wan 2.5, Hailuo 02, Kling 3.0, Midjourney

### Audio Models
Suno V5 (music), ElevenLabs (TTS/SFX)

### Key Features
- One API key for ALL models
- Smart quality tier detection (defaults to cheapest)
- SQLite task tracking
- Agent prompts: `/artist`, `/filmographer`
- Tool filtering (whitelist/blacklist)
- 30-50% lower cost than direct APIs

### Free Tier
Free trial available (amount unspecified). Get API key at kie.ai/api-key.

### Installation
```json
{
  "mcpServers": {
    "kie-ai": {
      "command": "npx",
      "args": ["-y", "@felores/kie-ai-mcp-server"],
      "env": {
        "KIE_AI_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Links
- https://github.com/felores/kie-ai-mcp-server
- https://kie.ai/

---

## 4. GENERATIVE MEDIA SKILLS (MUAPI)

### What It Is
CLI + MCP server for 100+ AI models. MIT licensed. Works with Claude Code, Cursor, Gemini CLI.

### Video Generation Models (29 models)
- **Text-to-Video (13)**: Seedance 2.0, Kling 3.0, Veo3, etc.
- **Image-to-Video (16)**: Animate screenshots, add motion

### Key Features
- Native audio-video sync
- Director-level scene creation
- Local file auto-upload to CDN
- Structured JSON outputs
- MCP server exposes 19 tools

### Installation
```bash
npm install -g muapi-cli
# or
pip install muapi-cli
```

### Links
- https://github.com/SamurAIGPT/Generative-Media-Skills
- https://muapi.ai

---

## 5. HUGGINGFACE SPACES (FREE VIDEO GENERATION)

### Our HF MCP Connection
We have `mcp__claude_ai_Hugging_Face__*` tools connected. The `gr1_z_image_turbo_generate` tool is for IMAGE generation only (Z-Image-Turbo), NOT video.

### Free Video Generation Spaces (Gradio API accessible)
These can be called via the HF Gradio Client Python library for free:

| Space | Model | Type | Likes | Trending |
|-------|-------|------|-------|----------|
| [Wan2.2 Animate](https://hf.co/spaces/Wan-AI/Wan2.2-Animate) | Wan2.2 | Image+Text-to-Video | 5019 | 72 |
| [Wan2.2 14B Preview](https://hf.co/spaces/r3gm/wan2-2-fp8da-aoti-preview) | Wan2.2 14B | Image-to-Video | 1477 | 190 |
| [LTX 2.3 Distilled](https://hf.co/spaces/Lightricks/LTX-2-3) | LTX 2.3 | Text/Image-to-Video | 215 | 60 |
| [CogVideoX-5B](https://hf.co/spaces/zai-org/CogVideoX-5B-Space) | CogVideoX-5B | Text-to-Video | 1033 | 4 |
| [LTX-2 Turbo](https://hf.co/spaces/alexnasa/ltx-2-TURBO) | LTX-2 | Text/Image+Audio-to-Video | 325 | 15 |
| [FramePack F1](https://hf.co/spaces/linoyts/FramePack-F1) | FramePack | Image-to-Video | 322 | 3 |
| [Wan2.1](https://hf.co/spaces/Wan-AI/Wan2.1) | Wan2.1 | Text-to-Video | 2038 | 10 |
| [LTX 2.3 Sync](https://hf.co/spaces/linoyts/LTX-2-3-sync) | LTX 2.3 | Text/Image/Audio-to-Video | 29 | 29 |
| [LTX 2.3 First-Last](https://hf.co/spaces/linoyts/LTX-2-3-First-Last-Frame) | LTX 2.3 | Video+Audio from frames | 67 | 41 |

### How to Use HF Spaces for Free Video
```python
from gradio_client import Client

# Example: Wan2.2 Animate (image-to-video)
client = Client("Wan-AI/Wan2.2-Animate")
result = client.predict(
    image="screenshot.png",
    prompt="Smooth camera pan over a business management dashboard",
    api_name="/generate"
)
```

### Limitations
- Queue times can be long (minutes to hours on popular Spaces)
- Free GPU allocation = ZeroGPU (shared, time-limited)
- Quality varies; best for short clips (3-8 seconds)
- NOT via our HF MCP tools directly (those are search/metadata only)
- Need to use `gradio_client` Python library separately

### NO MCP-Enabled Video Spaces Found
Searched for MCP-enabled video generation Spaces: NONE found. MCP Spaces are currently only for text/search tools.

---

## 6. COMFYUI MCP SERVER

### What It Is
MCP bridge to ComfyUI (node-based diffusion UI). Supports video generation with SVD, Mochi, LTX-Video, Hunyuan Video, Cosmos, Wan.

### Features
- 70+ example workflows
- Workflow execution via API-format JSON
- Async task management
- Custom workflow discovery
- Multi-modal: image, video, audio

### Requirements
- Local GPU (VRAM 8GB+ recommended)
- ComfyUI installed
- Docker or Node.js 18+

### Cost
Completely FREE (open source, local execution).

### Links
- https://github.com/shawnrushefsky/comfyui-mcp
- https://github.com/joenorton/comfyui-mcp-server

---

## 7. VEO MCP SERVERS (Google Veo)

Multiple implementations for Google's Veo video generation:
- https://github.com/mario-andreschak/mcp-veo2 (Veo2)
- https://github.com/Porkbutts/veo-mcp-server (Veo)
- https://github.com/waimakers/veo-mcp (Veo)

Requires Google Cloud API access. NOT free (Google AI pricing applies).

---

## 8. JSON-TO-VIDEO TOOLS

### JSON2Video (json2video.com)
- Define scenes, text, images, audio, transitions in JSON
- Cloud rendering API
- Free tier available
- Good for templated promotional videos

### Creatomate (creatomate.com)
- JSON/API video generation
- No-code + code (Node.js, Python, Ruby, PHP)
- Templates or fully custom JSON
- Paid (free trial)

### Shotstack
- Developer-first JSON video editing API
- Timeline, clips, overlays, audio, transitions
- Cloud rendering
- Paid

---

## 9. OTHER NOTABLE TOOLS

### EachLabs Video Generation Skill
- Claude Code skill for EachLabs AI
- Text-to-video, image-to-video, transitions, motion control, talking head, avatar
- Requires EachLabs account/credits
- https://fastmcp.me/skills/details/1911/eachlabs-video-generation

### SkillBoss Skills
- MCP server + Claude Code skills for 100+ AI services
- Includes video generation
- https://github.com/heeyo-life/skillboss-skills

### Adobe MCP Editor
- Claude Code bridge to Premiere Pro / After Effects
- Open projects, apply effects, YouTube-style editing
- Requires Adobe CC subscription
- https://lobehub.com/mcp/codebuffalo0225-claude-ai-mcp-bridge

### Replicate MCP Server
- Interfaces with Replicate API
- Video generation planned (currently image-focused)
- https://replicate.com/docs/reference/mcp

### Manim Skill (Mathematical Animations)
- 3Blue1Brown-style math/science videos
- LaTeX, graphs, 3D objects, geometric proofs
- FREE (open source)
- https://github.com/Yusuke710/manim-skill

---

## RECOMMENDATION FOR FLUXION VIDEO V4

### Strategy: Hybrid Approach (ZERO COST)

**PRIMARY: Remotion + Claude Code Skill**
- Install `remotion-dev/skills`
- Use screenshots from `landing/screenshots/` as input frames
- Claude Code generates React compositions for each of the 15 V4 scenes
- Crossfade transitions between screenshot scenes
- Text overlays (Italian copy from V4 screenplay)
- Edge-TTS voiceover added as audio track
- Local render to MP4 -- completely FREE
- This is the PRODUCTION approach (150K+ installs, battle-tested)

**OPTIONAL ENHANCEMENT: HF Spaces for AI Clips**
- Use `Wan-AI/Wan2.2-Animate` to animate key screenshots (add subtle motion)
- Use `Lightricks/LTX-2-3` for cinematic text-to-video intros
- Free but queue-dependent; generate clips in advance
- Integrate AI clips into Remotion composition

**OPTIONAL ENHANCEMENT: Kling AI for Hero Clips**
- 66 free credits/day = 3-6 short clips
- Use `mcp-kling` for a cinematic opening shot
- Watermarked on free tier (720p) -- may need paid for final version

### Implementation Steps
1. `npx skills add remotion-dev/skills`
2. `git clone https://github.com/jhartquist/claude-remotion-kickstart`
3. Copy screenshots to `public/` folder
4. Prompt Claude with V4 screenplay structure
5. Claude generates 15 React compositions
6. Add Edge-TTS voiceover via ffmpeg
7. `npx remotion render` -- done

### Why NOT Pure AI Video
- AI video generators (Kling, Veo, Seedance) generate FICTIONAL footage
- FLUXION needs to show REAL screenshots of the product
- Remotion: real screenshots + professional motion graphics = best of both worlds
- AI clips can supplement (e.g., cinematic B-roll) but not replace product shots

---

## COST SUMMARY

| Tool | Cost for FLUXION Use Case |
|------|--------------------------|
| Remotion + Claude Code | FREE (individual/small company) |
| HF Spaces (Wan2.2, LTX) | FREE (public Gradio API) |
| Kling free tier | FREE (66 credits/day, watermarked) |
| Kie.ai free trial | FREE (limited trial) |
| ComfyUI | FREE (needs local GPU) |
| Edge-TTS voiceover | FREE (already in stack) |
| ffmpeg post-processing | FREE (already installed) |

**Total cost for FLUXION promo video: EUR 0**
