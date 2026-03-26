# Stack Research

**Domain:** Desktop PMI software — Lancio v1.0 new capabilities
**Researched:** 2026-03-26
**Confidence:** HIGH (verified against official docs and PyPI)
**Scope:** NEW additions only — existing Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent stack is validated and not re-researched here.

---

## Context: Four Capability Areas

This research covers stack additions for four new features in the Lancio v1.0 milestone:

1. **Sales Agent WA** — scrape PMI contacts from Google Places / PagineBianche, send WhatsApp Web outreach
2. **Video V6 compositing** — produce promo video from AI clips + screenshots + TTS voiceover
3. **Windows MSI build** — cross-compile Tauri app + PyInstaller voice agent for Windows
4. **Content repurposing** — video → transcript → blog posts, YouTube Shorts, social clips

---

## 1. Sales Agent WA (Scraping + WhatsApp Web Automation)

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `playwright` (Python) | 1.58.0 | Browser automation for WhatsApp Web | Microsoft-maintained, async-native, persistent browser contexts for session persistence across restarts. Superior to Selenium for WA Web because it handles modern JS SPAs correctly and has built-in network interception. |
| `playwright-stealth` | latest (Feb 2026) | Reduce WA Web bot fingerprint signals | Patches `navigator.webdriver`, removes "HeadlessChrome" from UA, reduces detection surface. For WhatsApp Web (not hardened anti-bot), this is sufficient. |
| `google-maps-services-python` | latest via PyPI | Google Places API — primary lead source | Official Google SDK. The Places API (New) free tier covers 28,500 calls/month. Data quality is superior to PagineGialle: includes phone, rating, category, website, hours. |
| `beautifulsoup4` | 4.14.3 | PagineBianche HTML scraping — secondary source | Lightweight, no headless browser needed for static HTML. Used only when Google Places returns sparse results for a given zone. |
| `requests` | latest | HTTP for Places API + PagineBianche fetch | Standard. Simpler than httpx for this use case (no async needed for lead scraping pipeline). |
| `sqlite3` (stdlib) | stdlib | Store lead database with outreach state | Zero deps. Leads table with columns: phone, name, category, city, status (pending/sent/replied/converted), sent_at, message_variant. |
| `python-dotenv` | latest | Manage GOOGLE_PLACES_API_KEY safely | Keep key out of source. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `asyncio` (stdlib) | stdlib | Async sleep between WA sends | Use randomized `asyncio.sleep(random.uniform(90, 300))` between sends. Non-negotiable to avoid WA ban. |
| `csv` (stdlib) | stdlib | Export leads to CSV for review before sending | Manual review gate — Gianluca approves batch before agent sends. |
| `jinja2` | latest | Template WA messages with per-lead variables | Fills `[Nome]`, `[attivita]`, `[Citta]` slots. Enforces 40%+ variation rule across messages. |

### Architecture Decision: Playwright over Selenium for WA Web

**Use Playwright.** Selenium requires ChromeDriver maintenance, has worse async support, and is more detectable. Playwright's persistent browser context saves the WA Web QR scan session to a `./data/profile` directory — the agent resumes without re-scanning. Selenium does not persist sessions as cleanly.

**Do NOT use:** `pywhatkit` (uses `web.whatsapp.com` URL directly, unreliable with WA Web changes), `twilio` (paid), `whatsapp-business-api` (requires Meta verification, months of review, not zero cost), `selenium` (inferior to Playwright for this use case).

### Rate Limiting: Non-Negotiable Rules

Based on community data for Italian indie bootstrappers (2024-2025):
- **Max 20 messages/day** for the first 4 weeks (new number)
- **Min 90 seconds** between sends, randomized up to 300s
- **40%+ text variation** between messages via Jinja2 templates
- **Never send** link shorteners (bit.ly). Only full `youtube.com/watch?v=...` URLs with UTM params.
- **3 message variants** per vertical (parrucchiere, officina, estetica) — rotate randomly.

### Installation (Sales Agent — standalone Python script, NOT inside voice agent)

```bash
# In a new sales-agent/ directory (separate from voice-agent/)
pip install playwright==1.58.0 playwright-stealth beautifulsoup4 requests google-maps-services-python jinja2 python-dotenv

# Install Chromium browser binary
python -m playwright install chromium
```

---

## 2. Video V6 Compositing Pipeline

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `ffmpeg` (system binary) | 6.x (already installed) | Video encoding, xfade transitions, audio mixing | Already validated in existing pipeline (V5). Used via subprocess calls. Zero Python overhead for encoding. |
| `Pillow` | latest | Screenshot annotations, title cards, logo burn | Already in use. For V6: use only for logo watermark and static overlays. Do NOT use for animated text (produces low-quality output on MacBook). |
| `edge-tts` | latest | Italian voiceover generation (IsabellaNeural) | Already validated in V5 pipeline. Zero cost, good quality. Generate per-scene audio segments as `.mp3`. |
| `moviepy` | 2.2.1 | Complex timeline orchestration with audio sync | New addition. Use for scenes where frame-accurate audio+video sync is needed (specifically the Sara telefonata scene). MoviePy 2.2.1 fixed transparency compositing. For simple concatenation, prefer direct ffmpeg subprocess. |
| `google-cloud-aiplatform` | latest | Veo 3 clip generation via Vertex AI | Already in use (V5 pipeline). Continue for new AI B-roll clips needed in V6. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json` (stdlib) | stdlib | Scene manifest (video-production-v6.json) | Scene graph definition: clip file, duration, voiceover text, transition type, screenshot overlay coordinates. |
| `subprocess` (stdlib) | stdlib | Invoke ffmpeg binary directly | Prefer over `ffmpeg-python` wrapper for complex filter chains — the wrapper adds indirection without value for our use case. |
| `pathlib` (stdlib) | stdlib | Cross-platform path handling | Used throughout compositing scripts. |
| `pydub` | latest | Audio normalization before mixing | Normalize TTS voiceover to -18 LUFS before mixing with background music. Prevents volume imbalance between scenes. |

### Architecture Decision: Direct ffmpeg subprocess over moviepy for most operations

**Use direct ffmpeg subprocess calls for:** concatenation, xfade transitions, audio mixing, final export.

**Use moviepy only for:** frame-accurate overlay timing (Sara telefonata scene), transparency compositing.

**Rationale:** moviepy 2.2.1 is significantly slower than direct ffmpeg (converts frames to numpy arrays). For a 5-min promo video, direct ffmpeg pipelines run in ~2 minutes; moviepy equivalents take 15-20 minutes. Use moviepy only where its Python-level frame access provides irreplaceable value.

**Do NOT use:** `Remotion` (React/TypeScript video editor — introduces Node.js build complexity with no benefit over the existing Python pipeline; mentioned in video pipeline research but wrong tool for this use case since we already have a working Python compositing system). `OpenCV` (heavy dependency, only needed if perspective-transform PiP compositing is required — defer to post-launch).

### Key Validated ffmpeg Patterns (from video-editing-best-practices-2026.md)

```bash
# Anti-jitter zoom (pre-scale to 8000px)
ffmpeg -loop 1 -i screenshot.png -vf \
  "scale=8000:-1,zoompan=z='min(zoom+0.0015,1.5)':d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p zoom.mp4

# Crossfade transition between two clips
ffmpeg -i clip_a.mp4 -i clip_b.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=4.5[v]" \
  -map "[v]" output.mp4
```

**NEVER use:** `zoompan` without pre-scaling (produces jitter), `drawtext` filter on MacBook (codec limitation — use Pillow for text burn instead), "Kodak/film grain" in Veo 3 prompts (causes black borders).

---

## 3. Windows MSI Build

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `tauri-action` (GitHub Action) | v0 (current) | Cross-compile Tauri app for Windows on `windows-latest` runner | Official Tauri GitHub Action. Handles WiX toolset installation automatically. MSI is preferred over NSIS for lower antivirus false positive rate. |
| WiX Toolset v3 | v3 (via tauri-bundler) | Windows MSI generation | Tauri's bundler uses WiX internally. No manual WiX configuration needed — Tauri handles it. |
| `PyInstaller` | 6.19.0 | Bundle voice agent Python → Windows .exe | Produces self-contained .exe. Validated approach (already done for macOS). For Windows: use `requirements-windows.txt` that excludes `chatterbox-tts`, `torchaudio`, `pipecat-ai`. |
| `pyttsx3` | >=2.90 | Windows SystemTTS fallback (SAPI5) | Required because `say` + `afconvert` are macOS-only. `pyttsx3` wraps Windows SAPI5. Already documented as the fix in windows-compat-research.md. |
| `piper-onnx` | latest | Cross-platform Piper TTS (replaces binary path) | Python package distribution of Piper — eliminates the hardcoded `/usr/local/bin/piper` path problem. Works on Windows x64 without separate binary download. |
| `webrtcvad-wheels` | latest | Windows-compatible webrtcvad | `webrtcvad` requires compilation on Windows. `webrtcvad-wheels` provides pre-compiled wheels. Drop-in replacement. |

### Supporting Libraries / Fixes

| Fix | Area | What to Change |
|-----|------|----------------|
| `sys.platform == "win32"` guard | `voice-agent/src/tts.py` | SystemTTS: route to `pyttsx3` on Windows, `say`+`afconvert` on macOS |
| `%APPDATA%` path for SQLite | `voice-agent/main.py` | Use `os.environ.get("APPDATA")` on win32 instead of `~/Library/Application Support/` |
| Remove hardcoded `/Volumes/` paths | `voice-agent/src/booking_state_machine.py` | Use `FLUXION_DB_PATH` env var only |
| `webviewInstallMode: embedBootstrapper` | `tauri.conf.json` | Embed WebView2 bootstrapper (+1.8MB) — no internet required during install |
| `installMode: "both"` for NSIS | `tauri.conf.json` | Support both user-level and machine-level install for PMI with shared PCs |

### tauri.conf.json Windows additions

```json
{
  "bundle": {
    "windows": {
      "webviewInstallMode": { "type": "embedBootstrapper" },
      "nsis": { "installMode": "both" }
    }
  }
}
```

### PyInstaller Windows spec (key exclusions)

```bash
# requirements-windows.txt — add to voice-agent/
# Exclude: chatterbox-tts, torchaudio, pipecat-ai, aiortc, aioice, av
# Add:
pyttsx3>=2.90
piper-onnx
webrtcvad-wheels

# Build command (on windows-latest GitHub Actions runner):
pyinstaller --onefile --name voice-agent voice-agent/main.py \
  --exclude-module torch --exclude-module torchaudio \
  --exclude-module pipecat --exclude-module chatterbox
```

### SmartScreen Mitigation (no-cost)

- Build MSI (not NSIS .exe) — lower antivirus false positive rate
- Submit to VirusTotal before each release (public page link in release notes)
- Create `landing/installa-windows.html` with SmartScreen "More info → Run anyway" visual guide (3 steps with screenshots)
- Do NOT purchase EV certificate — €300+/year violates zero-cost guardrail

---

## 4. Content Repurposing

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `faster-whisper` | latest | Transcribe promo video to Italian text | Already in voice agent stack. Model `large-v3` on iMac GPU for high accuracy. Produces SRT with timestamps — directly usable for YouTube captions and blog post structure. |
| `groq` Python SDK | latest | LLM summarization for blog post generation | Already in use for Sara NLU. Groq `llama-3.3-70b-versatile` turns transcript + prompt into Italian SEO blog post. Zero additional cost (existing free tier). |
| `ffmpeg` (system binary) | 6.x | Extract audio from video + cut YouTube Shorts | Already in stack. `ffmpeg -ss [start] -t [duration] -i promo.mp4 shorts_clip.mp4` for vertical-format clips. |
| `Pillow` | latest | Thumbnail generation for YouTube + Shorts | Already in stack. Generate 1280x720 thumbnails with FLUXION branding and per-vertical headline text. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `edge-tts` | latest | Generate Italian voiceover for Shorts (if no original audio) | Same TTS already validated for video pipeline. |
| `json` (stdlib) | stdlib | Repurposing manifest: map video timestamps to content pieces | Define which 60s segments become Shorts, which section becomes which blog section. |

### Content Repurposing Pipeline

```
promo-v6.mp4 (5-7 min, 1080p)
    ↓ faster-whisper large-v3 (iMac)
transcript.srt + transcript.txt
    ↓ Groq llama-3.3-70b-versatile
blog-post-italiano.md (1500-2000 parole, SEO)
    ↓ manual review + publish to landing/blog/

promo-v6.mp4
    ↓ ffmpeg -ss [timestamp] -t 58 -vf "scale=1080:1920,setsar=1" (crop to 9:16)
shorts-parrucchiere.mp4 (1 per verticale, <60s)
    ↓ Pillow thumbnail + YouTube upload (manual)
```

**Do NOT use:** `yt-dlp` (for downloading) in the repurposing pipeline — FLUXION owns the source video, no downloading needed. `OpenAI Whisper API` (paid) — use `faster-whisper` local instead.

---

## Alternatives Considered

| Area | Recommended | Alternative | Why Not Alternative |
|------|-------------|-------------|---------------------|
| WA automation | `playwright` 1.58.0 | `selenium` + ChromeDriver | Selenium requires manual ChromeDriver version management, weaker async support, more detectable |
| WA automation | `playwright` 1.58.0 | WhatsApp Business API (official) | Requires Meta approval (weeks/months), requires paid number, violates zero-cost guardrail |
| Lead scraping primary | Google Places API | PagineGialle direct scraping | Google data quality superior (more complete, more current). Free tier (28,500 calls/month) covers all needs. PagineGialle scraping is fragile (structure changes without notice). |
| Video pipeline | Direct ffmpeg subprocess | `moviepy` as primary | moviepy 2.2.1 is 8-10x slower than direct ffmpeg for simple encode/concat operations. Use moviepy only for frame-precise overlay timing. |
| Video pipeline | Direct ffmpeg subprocess | `Remotion` (React) | Introduces full Node.js/React build pipeline for video — unjustified when Python compositing already works. |
| Windows TTS fallback | `pyttsx3` | `gTTS` | gTTS requires internet (Google TTS API). `pyttsx3` is fully offline via SAPI5 — matches offline-first requirement. |
| Windows Piper | `piper-onnx` Python package | Piper binary with hardcoded paths | `piper-onnx` is cross-platform by design. Eliminates all path-hardcoding issues documented in windows-compat-research.md. |
| Transcript | `faster-whisper` local | OpenAI Whisper API | Faster-whisper is already in the stack. Whisper API costs money. `large-v3` on iMac GPU is faster than cloud API for a single video. |
| Blog generation | Groq `llama-3.3-70b` | OpenAI GPT-4o | Groq free tier already used for Sara NLU. Zero additional cost. Quality sufficient for Italian SEO blog posts. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `pywhatkit` | Uses unreliable URL-scheme trick for WA Web, not persistent session, breaks on WA DOM changes | `playwright` with persistent context |
| `selenium` for WA | ChromeDriver version hell, weaker async, more fingerprint surface | `playwright` |
| `bit.ly` in WA messages | WA flags link shorteners as spam signal | Full `youtube.com/watch?v=...` URLs only |
| `drawtext` ffmpeg filter on MacBook | Known codec limitation on macOS ffmpeg build — corrupts text rendering | Pillow for text burn to intermediate PNG, then overlay |
| `zoompan` without pre-scaling | Produces jitter/vibration (ffmpeg pixel rounding) | Pre-scale to 8000px before zoompan |
| `Remotion` | Adds React/Node.js video build pipeline — no benefit over existing Python stack | Direct ffmpeg + moviepy |
| `chatterbox-tts` on Windows | 2.5GB PyTorch dependency, too large for Windows bundle | `piper-onnx` (primary) + `pyttsx3` SAPI5 (fallback) |
| EV Code Signing certificate | €300+/year — violates zero-cost guardrail | MSI + VirusTotal submission + SmartScreen instructions page |
| WhatsApp Business API (Meta) | Meta approval process, paid number required, weeks of setup | `playwright` WA Web automation (20 msg/day limit, zero cost) |

---

## Stack Patterns by Variant

**Sales Agent — initial manual phase (weeks 1-2):**
- Use Google Places API to BUILD the lead list (scraped, stored in SQLite)
- Gianluca reviews CSV exports and sends messages MANUALLY from personal WA
- No `playwright` WA automation yet — build trust score on number first

**Sales Agent — semi-automated phase (weeks 3-4):**
- Playwright opens WA Web, pre-fills messages, pauses for Gianluca approval
- Human-in-the-loop: Playwright prepares, human clicks send
- Max 20 sends/day, randomized 90-300s delay

**Sales Agent — full automation phase (week 5+):**
- Playwright sends autonomously within daily limit
- SQLite tracks state: pending → sent → replied → converted
- Dashboard in terminal (rich library) shows daily stats

**Windows build — GitHub Actions:**
- Trigger on `git tag v*` push
- `macos-latest` runner: universal binary (Intel + Apple Silicon)
- `windows-latest` runner: MSI + voice-agent PyInstaller exe
- Artifacts uploaded to GitHub Releases

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `playwright` 1.58.0 | Python 3.8+ | Chromium bundled, no separate ChromeDriver needed |
| `playwright-stealth` latest | `playwright` 1.58.0 | Port of puppeteer-extra-plugin-stealth; sufficient for WA Web (not hardened anti-bot) |
| `moviepy` 2.2.1 | Python 3.9+ | Transparency compositing fixed in this version. Requires `ffmpeg` system binary. |
| `piper-onnx` latest | Python 3.8+, Windows x64 + macOS | Replaces binary-path approach; model download to `~/.local/share/piper/` |
| `pyttsx3` >=2.90 | Python 3.8+, Windows 10+ SAPI5 | Windows-only TTS fallback; do not import on macOS |
| `PyInstaller` 6.19.0 | Python 3.8-3.14 | Do NOT use with Python 3.10.0 (known bug) |
| `google-maps-services-python` | Python 3.7+ | Use with `GOOGLE_PLACES_API_KEY` env var |
| `beautifulsoup4` 4.14.3 | Python 3.8+ | For PagineBianche scraping (secondary source) |
| `faster-whisper` latest | Python 3.8+, CUDA optional | `large-v3` on iMac GPU for content repurposing transcription |

---

## Sources

- `playwright` 1.58.0 version: [PyPI playwright](https://pypi.org/project/playwright/) — verified current as of 2026-03-26
- `playwright-stealth`: [PyPI playwright-stealth](https://pypi.org/project/playwright-stealth/) — Feb 2026 release
- `google-maps-services-python`: [Google Places API client libraries](https://developers.google.com/maps/documentation/places/web-service/client-libraries) — official
- `beautifulsoup4` 4.14.3: [PyPI beautifulsoup4](https://pypi.org/project/beautifulsoup4/) — Nov 2025 release
- `moviepy` 2.2.1: [PyPI moviepy](https://pypi.org/project/moviepy/) — transparency fix confirmed
- `PyInstaller` 6.19.0: [PyInstaller docs 2026-03-21](https://pyinstaller.org/en/stable/operating-mode.html) — current
- `pyttsx3` for Windows SAPI5: [windows-compat-research.md](../../.claude/cache/agents/windows-compat-research.md) — FLUXION internal research
- `piper-onnx` for cross-platform Piper: [windows-compat-research.md](../../.claude/cache/agents/windows-compat-research.md) — FLUXION internal research
- Tauri 2 Windows MSI + WiX: [v2.tauri.app/distribute/windows-installer](https://v2.tauri.app/distribute/windows-installer/) — official
- `tauri-action` GitHub Action: [tauri-apps/tauri-action](https://github.com/tauri-apps/tauri-action) — official
- WA rate limits + scraping strategy: [growth-first-100-clients-research.md](../../.claude/cache/agents/growth-first-100-clients-research.md) — FLUXION internal research (HIGH confidence)
- Video pipeline patterns: [video-editing-best-practices-2026.md](../../.claude/cache/agents/video-editing-best-practices-2026.md) — FLUXION internal research (HIGH confidence)
- ffmpeg Python wrappers: [typed-ffmpeg PyPI](https://pypi.org/project/typed-ffmpeg/) — Jan 2026

---

*Stack research for: FLUXION Lancio v1.0 — new feature capabilities*
*Researched: 2026-03-26*
