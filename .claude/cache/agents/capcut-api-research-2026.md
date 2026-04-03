# CapCut API Deep Research — CoVe 2026
> Date: 2026-04-01 | Session: S131
> Purpose: Evaluate CapCutAPI/VectCutAPI for automated FLUXION promo video production

---

## 1. Ecosystem Overview

There are **3 main Python libraries** for programmatic CapCut video production:

| Library | GitHub | Stars | MCP | Approach |
|---------|--------|-------|-----|----------|
| **CapCutAPI** (ashreo) | [ashreo/CapCutAPI](https://github.com/ashreo/CapCutAPI) | Fork | Yes | HTTP REST + MCP, generates `dfd_` draft folders |
| **VectCutAPI** (sun-guannan) | [sun-guannan/VectCutAPI](https://github.com/sun-guannan/VectCutAPI) | ~1.8k | Yes | HTTP REST + MCP, same core as CapCutAPI (upstream) |
| **pyCapCut** (GuanYixuan) | [GuanYixuan/pyCapCut](https://github.com/GuanYixuan/pyCapCut) | Newer | No | Pure Python library, pip installable, template-based |

**Key insight**: `ashreo/CapCutAPI` is a **fork** of `sun-guannan/VectCutAPI` (formerly called CapCutAPI). VectCutAPI is the **upstream/canonical** project with 1.8k stars, 187 commits, active weekly merges.

---

## 2. How It Works

### Architecture
```
Python Script → CapCutAPI/VectCutAPI → generates draft folder (dfd_XXXXX/)
                                         ├── draft_content.json   (project definition)
                                         ├── draft_meta_info.json (metadata)
                                         └── materials/           (linked media files)

Copy dfd_ folder → CapCut draft directory → CapCut opens it → 1-click Export
```

### Draft Directory Locations
- **macOS**: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`
- **Windows**: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\`

### Workflow
1. Python script calls API endpoints (HTTP or MCP) to build a project
2. `save_draft` generates a `dfd_` folder with `draft_content.json`
3. Copy/symlink the folder into CapCut's draft directory
4. Open CapCut Desktop — the project appears in "My Drafts"
5. Click Export in CapCut GUI to render final video

---

## 3. API Endpoints (VectCutAPI / CapCutAPI)

### HTTP REST API (port 9001 default)

| Endpoint | Purpose | Key Parameters |
|----------|---------|----------------|
| `POST /create_draft` | Initialize project | `width`, `height` (e.g., 1080x1920 for vertical) |
| `POST /save_draft` | Persist to disk | `draft_id` |
| `POST /add_video` | Add video track | `video_url`, `start`, `end`, `volume`, `transform_x/y`, `scale_x/y`, transitions |
| `POST /add_audio` | Add audio track | `audio_url`, `start`, `end`, `volume` (0.0-1.0), `speed` |
| `POST /add_image` | Add image asset | `image_url`, `start`, `end`, `transform_x/y`, `scale_x/y` |
| `POST /add_text` | Add text element | `text`, `font_family`, `font_size`, `color`, `shadow_enabled`, `shadow_color`, `background_color` |
| `POST /add_subtitle` | Import SRT | `srt_file`, styling params |
| `POST /add_effect` | Visual effect | Effect type, timing |
| `POST /add_sticker` | Sticker element | Position, animation |
| `GET /get_video_duration` | Media analysis | `video_url` → duration in seconds |

### MCP Protocol (11 tools via stdio)

Same functionality as HTTP, plus:
- `add_video_keyframe` — Animate properties over time
- Sequential workflow: `create_draft` → add media → add keyframes → `save_draft`

**MCP config for Claude Code:**
```json
{
  "mcpServers": {
    "capcut-api": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/VectCutAPI"
    }
  }
}
```

---

## 4. Keyframe Animation (Ken Burns Zoom)

### Supported Properties
| Property | Description | Use Case |
|----------|-------------|----------|
| `scale_x` | Horizontal scale | Zoom in/out |
| `scale_y` | Vertical scale | Zoom in/out |
| `alpha` | Opacity (0.0-1.0) | Fade in/out |

### Ken Burns Example (via MCP)
```python
# Slow zoom from 100% to 120% over 5 seconds
add_video_keyframe(
    draft_id="xxx",
    property_type="scale_x",
    time_points=[0, 5],
    values=[1.0, 1.2]
)
add_video_keyframe(
    draft_id="xxx",
    property_type="scale_y",
    time_points=[0, 5],
    values=[1.0, 1.2]
)
```

### pyCapCut Keyframes (richer)
pyCapCut supports keyframes on **any** property:
- Position (x, y), rotation, scale, opacity
- Audio volume keyframes for ducking
- Per-segment keyframe curves
- Easing via CapCut's internal curve system

---

## 5. Transitions

### Available via API
- `fade_in` / `fade_out` — standard opacity transitions
- Cross-dissolve between clips (via overlapping segments)
- CapCut's internal transition library accessible via effect IDs

### Via pyCapCut (template-based)
- **Entry/exit animations** per segment (slide in, zoom in, etc.)
- **Combination animations** (entry + exit paired)
- **Transition effects** between segments with custom duration
- Can import transition IDs from template projects (access to ALL CapCut transitions)

### CapCut Built-in Transitions (in GUI)
CapCut Desktop has **100+ transitions** including:
- Basic: fade, dissolve, wipe, slide, push
- Professional: zoom blur, light leak, glitch, film burn
- 3D: cube rotation, page flip, sphere
- These can be referenced by resource_id when using template approach

---

## 6. Text Styling Options

| Feature | API Support | Details |
|---------|-------------|---------|
| Font family | Yes | System fonts + CapCut bundled fonts |
| Font size | Yes | Numeric value |
| Color | Yes | Hex format (`#FFFFFF`) |
| Shadow | Yes | `shadow_enabled`, `shadow_color`, `shadow_alpha` |
| Background | Yes | `background_color`, `background_alpha`, `background_radius` |
| Multi-style text | Yes | Different colors per character range |
| Stroke/outline | pyCapCut | Via template approach |
| Text bubbles | pyCapCut | CapCut's bubble text presets |
| "Flower text" | pyCapCut | Animated text effects |
| Text animation | Template | Entry/exit animations from CapCut library |
| Line wrapping | pyCapCut | `max_width` parameter |

---

## 7. Audio Track Management

| Feature | Support | Details |
|---------|---------|---------|
| Volume control | Yes | 0.0-1.0 range |
| Speed adjustment | Yes | Playback speed multiplier |
| Fade in/out | pyCapCut | Duration-based fades |
| Volume keyframes | pyCapCut | Per-frame volume ducking |
| Multiple audio tracks | Yes | Independent tracks on timeline |
| Audio effects | VectCutAPI | Effect IDs from CapCut library |
| SRT subtitle sync | Yes | Auto-timed text from SRT files |

---

## 8. VectCutAPI vs CapCutAPI (ashreo fork)

| Aspect | VectCutAPI (sun-guannan) | CapCutAPI (ashreo) |
|--------|--------------------------|-------------------|
| **Status** | Upstream, actively maintained | Fork, less active |
| **Stars** | ~1.8k | Lower |
| **MCP support** | Yes (native) | Yes (inherited) |
| **Skill integration** | Claude Code skill docs | Basic |
| **Agent platforms** | Coze, Dify, N8N, Claude | Same |
| **Documentation** | English + Chinese | English + Chinese |
| **Weekly merges** | Yes (Monday) | Irregular |
| **Recommendation** | **USE THIS ONE** | Skip, use upstream |

### pyCapCut Comparison
| Aspect | VectCutAPI | pyCapCut |
|--------|-----------|----------|
| **Interface** | HTTP + MCP server | Python library (`pip install`) |
| **Template reuse** | No | Yes (load existing CapCut projects) |
| **Keyframe richness** | scale_x, scale_y, alpha | Any property |
| **Effect access** | Basic | Template-based (ALL CapCut effects) |
| **Learning curve** | Lower (REST calls) | Higher (understand draft format) |
| **Best for** | AI agent integration | Complex automated pipelines |

---

## 9. Quality: CapCut Rendering vs FFmpeg/MoviePy

### Rendering Quality Comparison

| Dimension | CapCut | FFmpeg | MoviePy |
|-----------|--------|--------|---------|
| **Codec control** | H.264/H.265, auto-optimized | Full control (any codec, bitrate, CRF) | Uses FFmpeg backend |
| **Max resolution** | 4K (Pro), 1080p (free) | Unlimited | Unlimited |
| **Motion blur** | Built-in, GPU-accelerated | Manual filter chain | Not native |
| **Easing curves** | Bezier curves in keyframes | Not native | Not native |
| **Color grading** | 50+ LUTs + manual adjust | LUT3D filter, complex | Basic |
| **Text rendering** | Anti-aliased, shadows, effects | drawtext filter (basic) | Pillow-based (basic) |
| **Transitions** | 100+ professional presets | Manual filter graphs | Basic (fade, slide) |
| **Speed ramping** | Smooth with bezier curves | Complex filter setup | Limited |
| **GPU acceleration** | Yes (Metal/CUDA) | Yes (NVENC/QSV/AMF) | No |
| **Batch automation** | No (GUI required) | Yes (CLI) | Yes (Python) |

### Verdict
**CapCut renders significantly higher quality** for:
- Text animations and typography
- Professional transitions (light leaks, glitch, 3D)
- Motion blur and speed ramping
- Color grading with LUTs
- Easing curves on keyframes

**FFmpeg/MoviePy wins for**:
- Full headless automation
- Custom codec parameters
- Batch processing
- No GUI dependency

---

## 10. Export Automation

### Can export be automated? **PARTIALLY — with significant caveats**

#### Current State (2026)
- **NO official CLI** for CapCut export
- **NO headless rendering** mode
- **NO documented AppleScript/Accessibility API** for CapCut

#### Possible Approaches

**A. AppleScript + System Events (macOS) — FRAGILE**
```applescript
tell application "CapCut" to activate
tell application "System Events"
    keystroke "e" using {command down}  -- Export shortcut
    delay 2
    keystroke return  -- Confirm export
end tell
```
- Requires Accessibility permissions
- Breaks with UI updates
- CapCut must be in foreground
- **NOT recommended for production**

**B. Python CGEvent / pyautogui — FRAGILE**
```python
import pyautogui
# Open CapCut, navigate to draft, click Export...
```
- Same fragility as AppleScript
- Pixel-dependent, breaks with resolution changes

**C. Semi-Automated Workflow (RECOMMENDED)**
```
Python generates draft → copy to CapCut drafts →
Human opens CapCut → clicks Export → done
```
- 1-2 minutes manual work per video
- Reliable, no breakage risk
- Can batch-prepare 10+ drafts, export sequentially

**D. CapCut Cloud Rendering (possible future)**
- VectCutAPI mentions "cloud rendering" capability
- Not well documented, may require CapCut Pro account
- Worth monitoring for future automation

---

## 11. CapCut Desktop Requirements

### Version Compatibility
- **CapCut International** (global) or **JianYing** (China) — both supported
- **Minimum**: Any version that uses `draft_content.json` format
- **macOS**: macOS 10.15+ (Catalina), Apple Silicon native
- **Windows**: Windows 10+

### CRITICAL: Encryption Warning
> **CapCut/JianYing Pro (latest versions, post-April 2024) started encrypting `draft_content.json`**
> - This does NOT affect draft **creation** (writing new drafts works fine)
> - This affects draft **reading/template import** from encrypted existing projects
> - **Workaround**: Use CapCut free version (not Pro) for reliable unencrypted drafts
> - **Alternative**: Generate new drafts from scratch (our use case) — NOT affected by encryption

### For FLUXION Use Case
Since we **generate** drafts (not read existing ones), the encryption issue is **NOT a blocker**.
We create fresh `dfd_` folders with our content — CapCut reads them without issues.

---

## 12. Limitations

### Hard Limitations
1. **GUI dependency** — CapCut Desktop MUST be installed for final export/rendering
2. **No headless export** — Someone must click "Export" (or use fragile automation)
3. **No Linux support** — CapCut Desktop only runs on macOS and Windows
4. **Font availability** — Custom fonts must be installed on the system or use CapCut bundled fonts
5. **Pro features gated** — 4K export, some effects require CapCut Pro subscription
6. **Rate limiting** — CapCut may throttle rapid project switching

### Soft Limitations
1. **Draft format undocumented** — reverse-engineered, may change between versions
2. **Effect IDs opaque** — Need to extract from template projects or CapCut assets
3. **No preview without CapCut** — Can't preview generated project without opening GUI
4. **Large draft files** — Complex projects generate large JSON files (10-50MB)
5. **CapCut updates** — Draft format may change, requiring library updates

### Mitigations
- **Pin CapCut version** — Don't auto-update during production
- **Template approach** (pyCapCut) — Extract effect/transition IDs once, reuse
- **Hybrid workflow** — Generate complex projects programmatically, fine-tune in GUI

---

## 13. Comparison with Current FLUXION Video Pipeline

### Current: FFmpeg/MoviePy (S130)
```
Veo 3 clips + TTS audio + background music
    → MoviePy/FFmpeg assembly
    → Direct MP4 output (headless)
    → Quality: functional but basic transitions
```

### Proposed: CapCutAPI Hybrid
```
Veo 3 clips + TTS audio + background music
    → VectCutAPI generates CapCut draft
    → Open in CapCut (1-click export)
    → Quality: professional transitions, text effects, color grading
```

### Decision Matrix

| Criteria | FFmpeg/MoviePy | CapCutAPI | Winner |
|----------|---------------|-----------|--------|
| **Automation** | Full headless | Semi-manual export | FFmpeg |
| **Visual quality** | Basic | Professional | CapCut |
| **Transitions** | Fade only | 100+ types | CapCut |
| **Text effects** | Basic | Rich animations | CapCut |
| **Ken Burns** | Manual affine | Native keyframes | CapCut |
| **Color grading** | LUT filter | Built-in LUTs + manual | CapCut |
| **Motion blur** | Complex | Built-in | CapCut |
| **Batch production** | Easy | Tedious (manual export) | FFmpeg |
| **CI/CD pipeline** | Yes | No | FFmpeg |
| **Zero dependency** | FFmpeg only | CapCut Desktop required | FFmpeg |
| **Cost** | Free | CapCut free (1080p) or Pro ($) | FFmpeg |

---

## 14. Recommended Strategy for FLUXION

### Dual Pipeline Approach

**Pipeline A — Automated (FFmpeg) — for volume/batch**
- Used for: bulk vertical video generation, CI/CD, headless servers
- Quality: good enough for social media, WhatsApp previews
- Fully automated, no human in the loop

**Pipeline B — Premium (CapCutAPI) — for hero content**
- Used for: landing page hero video, vertical showcase videos, sales material
- Quality: professional-grade with CapCut transitions and effects
- Semi-automated: Python generates draft, human clicks Export
- **6 vertical videos**: worth the 10-minute manual export time for premium quality

### Implementation Plan
1. Install VectCutAPI on MacBook (Python 3.10+, ~5 min setup)
2. Create FLUXION video template script using VectCutAPI
3. Generate 6 vertical drafts programmatically
4. Copy to CapCut drafts directory
5. Open CapCut, export each (1-2 min per video)
6. Use exported videos on landing page

### pyCapCut Alternative
For maximum control, consider pyCapCut (`pip install pycapcut`):
- Create a "master template" in CapCut manually with desired transitions/effects
- Use pyCapCut to clone template and swap media/text per vertical
- Preserves ALL CapCut effects from template
- Best of both worlds: design in GUI, automate variations in Python

---

## 15. Quick Start Commands

```bash
# Install VectCutAPI
cd /Volumes/MontereyT7/FLUXION
git clone https://github.com/sun-guannan/VectCutAPI.git tools/vectcut-api
cd tools/vectcut-api
python3 -m venv venv-capcut
source venv-capcut/bin/activate
pip install -r requirements.txt
cp config.json.example config.json
python capcut_server.py  # starts on port 9001

# OR install pyCapCut (simpler)
pip install pycapcut

# Test: create a draft
curl -X POST http://localhost:9001/create_draft \
  -H "Content-Type: application/json" \
  -d '{"width": 1080, "height": 1920}'

# Add video
curl -X POST http://localhost:9001/add_video \
  -H "Content-Type: application/json" \
  -d '{"draft_id": "DRAFT_ID", "video_url": "/path/to/clip.mp4", "start": 0, "end": 10}'

# Save draft
curl -X POST http://localhost:9001/save_draft \
  -H "Content-Type: application/json" \
  -d '{"draft_id": "DRAFT_ID"}'

# Copy generated dfd_ folder to CapCut drafts
cp -r dfd_* ~/Movies/CapCut/User\ Data/Projects/com.lveditor.draft/
```

---

## Sources

- [VectCutAPI (upstream, recommended)](https://github.com/sun-guannan/VectCutAPI) — 1.8k stars, MCP + REST
- [CapCutAPI (ashreo fork)](https://github.com/ashreo/CapCutAPI) — fork of VectCutAPI
- [pyCapCut](https://github.com/GuanYixuan/pyCapCut) — pure Python library, template-based
- [VectCutAPI MCP Documentation](https://github.com/sun-guannan/VectCutAPI/blob/main/MCP_Documentation_English.md)
- [VectCutAPI Skill for Claude Code](https://github.com/sun-guannan/VectCutAPI/blob/main/vectcut-skill/README_EN.md)
- [CapCut Automation Masterclass](https://www.xugj520.cn/en/archives/capcut-automation-api-python-guide.html)
- [capcut-export (encrypted draft warning)](https://github.com/emosheeep/capcut-export)
- [MoviePy Effects Discussion (vs CapCut)](https://github.com/Zulko/moviepy/discussions/2119)
- [CapCut MCP on LobeHub](https://lobehub.com/mcp/fancyboi999-capcut-mcp)
- [DeepWiki: CapCut and Jianying Integration](https://deepwiki.com/sun-guannan/VectCutAPI/11.1-capcut-and-jianying-integration)
