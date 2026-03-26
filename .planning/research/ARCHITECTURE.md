# Architecture Research

**Domain:** Launch pipeline for desktop software (screenshot automation, video compositing, landing page, sales outreach, Windows build)
**Researched:** 2026-03-26
**Confidence:** HIGH — based on existing codebase analysis + verified research files

---

## System Overview

The existing FLUXION architecture has five layers. The launch pipeline adds three new subsystems that sit alongside but do not modify the core app.

```
┌─────────────────────────── EXISTING PRODUCTION ──────────────────────────────┐
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                    Tauri 2.x Desktop App (macOS/Windows)                 │ │
│  │  React 19 + TypeScript UI    ←→    Rust Backend (SQLite WAL)             │ │
│  │  Port 3001 HTTP Bridge       ←→    Python voice-agent sidecar :3002      │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                       │
│                             Ed25519 license key                               │
│                                       │                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐    │
│  │              CF Worker: fluxion-proxy (Hono, Cloudflare)              │    │
│  │  /phone-home  /nlu/chat  /trial-status  /webhook/stripe  /activate    │    │
│  │  KV: purchase:{email}  →  Resend email  →  Ed25519 sign license       │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │              CF Pages: landing (static HTML/CSS/JS)                      │ │
│  │  index, /grazie, /installa, /voip-guida, /activate                       │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │              GitHub Releases: binary hosting (CDN)                       │ │
│  │  Fluxion_1.0.0_macOS.pkg  Fluxion_1.0.0_x64.dmg                         │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────────── NEW SUBSYSTEM 1: Screenshot + Video Pipeline ─────────────────────┐
│                                                                               │
│  iMac (192.168.1.2) — capture host                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  screencapture + Python CGEvent (Quartz)                                │ │
│  │  Navigate Tauri UI → capture → landing/screenshots/ (SCP to MacBook)   │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                              │ SCP / git push                                 │
│  MacBook — compositing host                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  compose-final-video.py                                                 │ │
│  │  Edge-TTS voiceover → ffmpeg concat → Veo3 AI clips → mp4 output       │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                              │                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Google Cloud Vertex AI (Veo 3)                                         │ │
│  │  regenerate-clips-v2.py → ai-clips-v2/ (5-9 sec MP4 per scene)         │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────────── NEW SUBSYSTEM 2: Sales Agent WhatsApp ────────────────────────────┐
│                                                                               │
│  MacBook (orchestrator) or iMac                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  lead_generator.py (EXISTING — Google Maps paste + Places API)          │ │
│  │  → scripts/leads/leads.json  →  wa_links.html (manual outreach)        │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                              │ (NOT YET BUILT)                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  sales-agent/ (NEW)                                                     │ │
│  │  WA Web automation (Selenium/Playwright) → send messages from leads.json│ │
│  │  Rate limiter: max 20 msg/day per WA number + random delay 3-8 min     │ │
│  │  SQLite leads.db: tracks sent_at, replied, status per lead              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Dashboard (local HTML or Tauri window)                                 │ │
│  │  Shows: leads pipeline, sent today, reply rate, conversion              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────────── NEW SUBSYSTEM 3: Windows MSI Build ───────────────────────────────┐
│                                                                               │
│  GitHub Actions (CI) or iMac cross-compilation                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  WiX Toolset → .msi installer                                           │ │
│  │  WebView2 bootstrapper (1.8MB) included                                 │ │
│  │  installMode: "both" (admin + user-level)                               │ │
│  │  Upload to GitHub Releases                                              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### Existing Components (do not modify)

| Component | Location | Responsibility | Status |
|-----------|----------|----------------|--------|
| Tauri app | `src/` + `src-tauri/` | Desktop UI + Rust backend + SQLite | DONE |
| Voice agent sidecar | `voice-agent/` | Sara FSM, STT, TTS, NLU | DONE |
| CF Worker fluxion-proxy | `fluxion-proxy/` | License auth, NLU proxy, Stripe webhook | DONE |
| CF Pages landing | `landing/` | Static HTML, purchase funnel | DONE (needs V6 video) |
| lead_generator.py | `scripts/lead_generator.py` | Google Maps scrape → leads.json + wa_links.html | DONE |
| macOS PKG build | `scripts/build-macos.sh` | 68MB pkg installer | DONE |

### New Components to Build

| Component | Location (proposed) | Responsibility | Builds On |
|-----------|--------------------|--------------------|-----------|
| Screenshot capture script V2 | `scripts/capture-screenshots.py` | CGEvent navigation + screencapture, all 21+ pages | Existing CGEvent pattern |
| Video compositor V6 | `scripts/compose-video-v6.py` | ffmpeg + Edge-TTS + Veo3 clips → mp4 | compose-final-video.py |
| Veo3 clip generator V6 | `scripts/regenerate-clips-v3.py` | 5 new AI clips (Pacchetti, Fedeltà scenes) | regenerate-clips-v2.py |
| Sales Agent WA | `sales-agent/` (new dir) | Selenium WA Web, rate limiter, SQLite status DB | lead_generator.py output |
| Sales dashboard | `sales-agent/dashboard.html` | Local HTML: pipeline view, today's sends, replies | sales-agent SQLite |
| Windows MSI pipeline | `.github/workflows/build-windows.yml` | WiX → msi → GitHub Release | tauri.conf.json |
| Content repurposing | `scripts/clip-repurpose.py` | Chop V6 video → social clips (60s, 30s, 15s) | compose-video-v6.py |

---

## Data Flow: Launch Pipeline

### Flow 1: Screenshot → Video → Landing

```
iMac (Tauri app running)
  → capture-screenshots.py (CGEvent navigate + screencapture)
  → landing/screenshots/*.png (SCP to MacBook or git push)
        │
MacBook
  → regenerate-clips-v3.py → Vertex AI Veo3 → ai-clips-v3/*.mp4
  → compose-video-v6.py:
        Edge-TTS async (it-IT-IsabellaNeural) → /tmp/vo_*.mp3
        ffmpeg concat (clips + screenshots + voiceover + music)
        → landing/assets/fluxion-promo-v6.mp4
        │
  → embed in landing/index.html (hosted video or YouTube)
  → CF Pages deploy --branch=production
```

**Key constraint:** Screenshots must come from the iMac where the Tauri app runs. MacBook cannot run the Rust app. SCP or git push is the handoff mechanism.

### Flow 2: Lead Generation → WhatsApp Outreach

```
Operator (manual step)
  → Google Maps search for vertical (es. "parrucchiere Milano")
  → copy-paste results into input_leads.txt
  → python scripts/lead_generator.py --mode paste --input input_leads.txt
        → scripts/leads/leads.json (structured, deduplicated)
        → scripts/leads/wa_links.html (manual click-to-send, CURRENT)
        │
NEW: python sales-agent/agent.py --leads scripts/leads/leads.json
        → reads leads.json (status != "sent")
        → Selenium: open WA Web, scan QR (once, session saved)
        → rate limiter: max 20 msg/day, random delay 3-8 min between
        → sends templated WA message per vertical (from wa_first_contact_templates.json)
        → updates sales-agent/leads.db: lead_id, sent_at, status
        │
        → sales-agent/dashboard.html (reads leads.db, shows pipeline)
```

**Key constraint:** WA Web automation requires a phone with active WhatsApp and QR scan. This is a human-in-the-loop step (scan once, session persists ~2 weeks). The automation then runs headless.

### Flow 3: Purchase → License → Activation (existing, no changes needed)

```
Landing CTA → Stripe Checkout (hosted)
  → Payment OK → Stripe webhook → CF Worker /webhook/stripe
  → CF KV: purchase:{email} = {tier, timestamp}
  → Resend email: download link + activation guide
  → User installs PKG/MSI
  → Tauri wizard: "Attiva con Email"
  → CF Worker /activate-by-email → Ed25519 sign → license key stored locally
  → phone-home on startup: Ed25519 verify offline → Sara gated by tier
```

This flow is complete and should not be modified during the launch sprint.

### Flow 4: Windows MSI Build

```
GitHub Actions (windows-latest runner)
  → checkout repo
  → install Rust + Tauri CLI
  → npm install + npm run tauri build
  → WiX toolset → .msi (installMode: "both", WebView2 bootstrapper)
  → upload artifact → GitHub Releases v1.0.0
  → update landing /installa page with Windows download link
```

**Key constraint:** PyInstaller sidecar (voice-agent binary) must be pre-built for Windows (`voice-agent-x86_64-pc-windows-msvc.exe`) and checked into `binaries/` before the WiX build runs.

---

## Component Boundaries

### What is strictly iMac-only

- Rust compilation (`cargo build`, `npm run tauri build`)
- Tauri app execution (needed for screenshots)
- CGEvent-based UI navigation (macOS-only Quartz API)
- Voice pipeline runtime (port 3002)

### What is MacBook-only (TypeScript/Python dev)

- Video compositing scripts (ffmpeg available on MacBook)
- Edge-TTS voiceover generation (Python asyncio, network)
- lead_generator.py and sales-agent (Python 3.9+)
- CF Pages deploy (wrangler CLI)
- CF Worker deploy (wrangler CLI)

### What is CI-only (GitHub Actions)

- Windows MSI build (requires Windows runner + WiX)
- macOS universal binary (requires macOS runner for notarization prep)

### What crosses the boundary (handoff points)

| From | To | Mechanism | What moves |
|------|----|-----------|-----------|
| iMac | MacBook | `git push` or `scp` | `landing/screenshots/*.png` |
| MacBook | Vertex AI | HTTPS REST | Veo3 prompt → MP4 response |
| MacBook | CF Pages | `wrangler deploy` | Updated `landing/` directory |
| MacBook | GitHub Releases | `gh release upload` | `.mp4`, `.pkg`, `.msi` |
| MacBook | CF Worker | `wrangler deploy` | Worker code changes |

---

## Recommended Project Structure

```
FLUXION/
├── landing/
│   ├── index.html              # MODIFY: embed V6 video
│   ├── screenshots/            # 21+ PNG captures from iMac
│   └── assets/
│       ├── fluxion-promo-v6.mp4       # NEW: final video
│       └── ai-clips-v3/               # NEW: 5 new Veo3 clips
│
├── scripts/
│   ├── lead_generator.py       # EXISTING — no changes needed
│   ├── capture-screenshots.py  # NEW: CGEvent screenshot automation
│   ├── compose-video-v6.py     # NEW: V6 compositor (evolves V5)
│   ├── regenerate-clips-v3.py  # NEW: Veo3 V6 clips
│   ├── clip-repurpose.py       # NEW: chop video for social
│   └── leads/
│       ├── leads.json          # Lead database (JSON)
│       └── wa_links.html       # Manual outreach dashboard
│
├── sales-agent/                # NEW DIRECTORY
│   ├── agent.py                # WA Web Selenium automation
│   ├── rate_limiter.py         # 20 msg/day, random delays
│   ├── leads.db                # SQLite: sent status, replies
│   └── dashboard.html          # Local pipeline view
│
├── fluxion-proxy/              # EXISTING — minimal changes
│   └── src/                    # No new endpoints needed for launch
│
└── .github/
    └── workflows/
        └── build-windows.yml   # NEW: Windows MSI CI pipeline
```

---

## Architectural Patterns

### Pattern 1: Pipeline Script with Shared State File

**What:** Each pipeline stage reads/writes a JSON or SQLite file as the handoff artifact. No inter-process communication, no shared daemon.

**When to use:** Screenshot pipeline, lead pipeline, video pipeline. All are batch processes run by a human operator, not real-time services.

**Trade-offs:** Simple and debuggable. No resume on crash unless you add checkpointing. Acceptable for 1-operator launch workload.

**Example — video pipeline handoff:**
```python
# Stage 1 (iMac): produces screenshots
# Stage 2 (MacBook): reads screenshots, produces voiceover
vo_files = [f for f in TMPDIR.glob("vo_*.mp3") if f.exists()]
if not vo_files:
    await generate_voiceovers(SCENES)  # Edge-TTS async
# Stage 3: ffmpeg concat
subprocess.run(["ffmpeg", "-f", "concat", "-i", "concat.txt", OUTPUT])
```

### Pattern 2: Idempotent Lead Database

**What:** leads.json is the canonical lead store, deduplicated by phone number. The sales-agent SQLite is an operational overlay that adds `sent_at`, `replied`, `status` without mutating the source JSON.

**When to use:** Sales Agent WA. Separates "what we know about the lead" (JSON) from "what we've done with the lead" (SQLite).

**Trade-offs:** Clean separation. Two sources of truth to keep in sync. Acceptable because JSON is read-only after generation.

**Example — agent reads uncontacted leads:**
```python
with open("scripts/leads/leads.json") as f:
    leads = json.load(f)
sent_phones = db.execute("SELECT phone FROM outreach WHERE status != 'pending'").fetchall()
pending = [l for l in leads if l["telefono"] not in sent_phones]
```

### Pattern 3: Session Persistence for WA Web

**What:** Playwright/Selenium saves the browser profile/session directory after QR scan. Subsequent runs load the saved session without requiring a new QR scan.

**When to use:** Sales Agent WA automation. The QR scan is a human-in-the-loop step that happens once per session (~2 weeks).

**Trade-offs:** Eliminates operator friction. Risk: Meta detects saved sessions as automated. Mitigation: use real Chromium profile directory, not headless.

**Example:**
```python
# Playwright
context = browser.new_context(storage_state="sales-agent/.wa-session.json")
# First run: page.wait_for_selector("#qr-canvas") + operator scans
# Subsequent runs: session already authenticated
context.storage_state(path="sales-agent/.wa-session.json")  # save after auth
```

### Pattern 4: Rate Limiter with Jitter

**What:** A token bucket or simple counter that caps messages at 20/day per WA number, with random delay (3-8 minutes) between sends.

**When to use:** All WA outreach. Non-negotiable for ban avoidance.

**Trade-offs:** Slows throughput (20 msgs × 5.5min avg = ~110 min/day). Correct trade-off: ban = zero throughput.

**Example:**
```python
import time, random
MAX_PER_DAY = 20
DELAY_MIN_S = 3 * 60   # 3 minutes
DELAY_MAX_S = 8 * 60   # 8 minutes

def send_with_rate_limit(message, phone):
    today_sent = db.count_sent_today()
    if today_sent >= MAX_PER_DAY:
        raise StopIteration("Daily limit reached")
    do_send(message, phone)
    db.record_sent(phone)
    time.sleep(random.uniform(DELAY_MIN_S, DELAY_MAX_S))
```

---

## Integration Points

### External Services

| Service | Integration Pattern | Direction | Notes |
|---------|---------------------|-----------|-------|
| Stripe | Webhook → CF Worker → KV | inbound | Already wired, no changes |
| Resend | CF Worker → Resend REST API | outbound | Already wired, no changes |
| Groq/Cerebras | CF Worker NLU proxy | outbound | Already wired, no changes |
| Vertex AI (Veo3) | MacBook scripts → REST | outbound | gcloud auth, €254 credits |
| GitHub Releases | `gh release upload` CLI | outbound | Binary hosting |
| CF Pages | `wrangler pages deploy` CLI | outbound | Always `--branch=production` |
| WhatsApp Web | Selenium/Playwright browser | outbound | QR once per session |
| Google Maps Places API | lead_generator.py | outbound | Optional (paste mode = free) |
| Edge-TTS | Python `edge-tts` library | outbound | Free, streaming |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| iMac captures → MacBook video | SCP / git push screenshots | Manual step per sprint |
| lead_generator → sales-agent | File: `scripts/leads/leads.json` | JSON read-only handoff |
| sales-agent → dashboard | SQLite: `sales-agent/leads.db` | Dashboard reads, agent writes |
| compose-video-v6 → CF Pages | `landing/assets/*.mp4` + wrangler deploy | File-based, then deploy |
| Tauri app → CF Worker | HTTPS with Ed25519 Bearer token | Existing auth pattern |
| GitHub Actions → GitHub Releases | `gh release upload` or `actions/upload-release-asset` | CI artifact upload |

---

## Suggested Build Order

Dependencies run strictly sequential. Phases 1-4 of the internal roadmap map to this order:

```
SPRINT 2: Screenshot Perfetti
  1. capture-screenshots.py V2 (iMac)
     → Depends on: Tauri app with seed data (Sprint 1 DONE)
     → Output: landing/screenshots/ 21+ PNG

SPRINT 3: Video V6
  2. regenerate-clips-v3.py (MacBook → Veo3)
     → Depends on: storyboard-v6-research.md (DONE)
     → Output: ai-clips-v3/*.mp4

  3. compose-video-v6.py (MacBook)
     → Depends on: screenshots (step 1) + AI clips (step 2)
     → Output: landing/assets/fluxion-promo-v6.mp4

SPRINT 4: Landing + Deploy
  4. landing/index.html V2 (MacBook)
     → Depends on: V6 video (step 3)
     → Embed video, update copy, CTA flow

  5. wrangler pages deploy (MacBook)
     → Depends on: index.html V2 (step 4)
     → Result: fluxion-landing.pages.dev live with V6

  6. E2E flow verification
     → Stripe test purchase → webhook → email → activate
     → Depends on: deploy (step 5)

SPRINT 5: Sales Agent WA
  7. sales-agent/agent.py (MacBook)
     → Depends on: leads.json from lead_generator.py (DONE)
     → Playwright/Selenium + rate limiter + SQLite

  8. sales-agent/dashboard.html (MacBook)
     → Depends on: leads.db schema (step 7)

SPRINT 6 (Post-lancio):
  9. Windows MSI build pipeline
     → .github/workflows/build-windows.yml
     → Requires: PyInstaller sidecar pre-built for Windows
     → Depends on: stable codebase (after launch)

  10. clip-repurpose.py
      → Depends on: V6 video final (step 3)
      → Output: 60s, 30s, 15s clips for social
```

**Why this order:**
- Steps 1-3 are linear dependencies (screenshots → AI clips → composite)
- Step 4-5 gate the public landing (no video = no deploy)
- Step 6 validation must happen before real Stripe traffic
- Step 7 is independent of 1-6 architecturally but emotionally: you want the landing ready before sending 20 WA messages/day pointing to it
- Windows MSI is deliberately last — it requires a stable binary and does not block first sales on macOS

---

## Anti-Patterns

### Anti-Pattern 1: Modify the Core App for Launch Artifacts

**What people do:** Add screenshot routes, demo modes, or video-specific UI changes directly into `src/` and commit them to master.

**Why it's wrong:** Pollutes production code with launch-specific hacks. These never get cleaned up. Seed data scripts and capture scripts should be external tools that operate on the running app.

**Do this instead:** Use `scripts/seed-video-demo.sql` (already exists) + external capture scripts. The Tauri app remains unmodified.

### Anti-Pattern 2: Send WA Messages Without Rate Limiting

**What people do:** Loop through all leads and send immediately, or send 50+ per day to maximize reach.

**Why it's wrong:** Meta's trust score system flags identical messages sent to many numbers. A ban means zero outreach capability for weeks. Recovery requires a new phone number.

**Do this instead:** Enforce 20 msg/day hard cap, 3-8 min random delays, vary message slightly per vertical (already done via `wa_first_contact_templates.json`).

### Anti-Pattern 3: Host the Video on CF Pages

**What people do:** Upload the 40-60MB mp4 to `landing/assets/` and let wrangler serve it via CF Pages.

**Why it's wrong:** CF Pages has a 25MB file size limit. A 42MB mp4 (V5 precedent) will fail the deploy. Additionally, CF Pages CDN is not optimized for video streaming (no range request resume, no adaptive bitrate).

**Do this instead:** Host on YouTube (unlisted or public) and embed with `<iframe>`, or upload to GitHub Releases and use a direct link with a `<video>` tag. Both are free. YouTube gives an additional discovery channel.

### Anti-Pattern 4: Build Windows MSI Before macOS is Stable

**What people do:** Parallelize Windows build with feature development to "save time."

**Why it's wrong:** Windows MSI requires a stable binary. If the Rust codebase changes significantly, the WiX manifest and PyInstaller sidecar need to be rebuilt. Doing it before launch creates duplicate work.

**Do this instead:** Windows MSI is Sprint 6 (post-launch). First sales prove the product on macOS. Windows then follows with a known-good binary.

### Anti-Pattern 5: Use Headless Chromium for WA Web

**What people do:** Run Playwright/Selenium with `--headless` flag to avoid seeing the browser.

**Why it's wrong:** WhatsApp Web's anti-bot detection (as of 2025-2026) blocks or degrades sessions in headless Chromium. The QR flow also requires visual rendering.

**Do this instead:** Run in headed mode (visible browser) on MacBook. Set it to a small window, let it run in the background. Use a real Chromium profile directory for session persistence.

---

## Scaling Considerations

This is a launch pipeline operated by one person (the founder). Scale concerns are irrelevant for the launch sprint. The relevant constraint is operator time, not system throughput.

| Constraint | At Launch (0-50 clients) | At 100+ Clients |
|-----------|--------------------------|-----------------|
| WA outreach | 20 msg/day manual curation | Consider CTWA ads (Click-to-WA) |
| Lead sourcing | Google Maps paste mode | Places API with Google Cloud billing |
| Video hosting | YouTube unlisted | Same (YouTube scales infinitely) |
| Windows binary | Build on-demand (GitHub Actions) | Same CI pipeline |
| CF Worker | Free tier (100K req/day) covers all | Same, free tier is enough |

---

## Sources

- Existing codebase: `scripts/lead_generator.py`, `scripts/compose-final-video.py`, `fluxion-proxy/src/index.ts`
- Research files (HIGH confidence, produced 2026-03-25/26):
  - `.claude/cache/agents/growth-first-100-clients-research.md`
  - `.claude/cache/agents/video-sales-outreach-research-2026.md`
  - `.claude/cache/agents/us-smb-sales-outreach-research-2026.md`
  - `.claude/cache/agents/landing-v2-optimization-research.md`
  - `.claude/cache/agents/storyboard-v6-research.md`
- CLAUDE.md: distribution architecture decisions (S84, permanent)
- MEMORY.md: CGEvent screenshot pattern, Veo3 pipeline, CF Pages deploy constraint

---

*Architecture research for: FLUXION Lancio v1.0 — launch + marketing + sales pipeline*
*Researched: 2026-03-26*
