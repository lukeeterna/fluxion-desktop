# Project Research Summary

**Project:** FLUXION — Lancio v1.0
**Domain:** Indie desktop software commercial launch — Italian SMB market (saloni, officine, palestre, cliniche)
**Researched:** 2026-03-26
**Confidence:** HIGH

## Executive Summary

FLUXION v1.0 is a complete product. The milestone is not about building product features — the product shipped at v0.9.0 with full CRM, calendar, Sara voice agent, 8 vertical cards, Stripe licensing, and macOS PKG installer. The Lancio v1.0 milestone is a commercial launch pipeline: produce a compelling video demo, optimize the landing page, build a zero-cost lead acquisition machine via WhatsApp outreach, and extend distribution to Windows. Every launch component has a strict sequential dependency chain — screenshots unlock video, video unlocks landing, landing unlocks outreach. Skipping or reordering breaks the funnel before traffic arrives.

The recommended approach is a 6-sprint structure. Sprints 1-4 are internal pre-launch work (seed data, screenshots, video, landing) that must complete before any outreach message is sent. Sprint 5 is the go-to-market activation (WhatsApp Sales Agent, commercialisti channel). Sprint 6 is post-launch amplification (content repurposing, referral program, Windows MSI). The zero-cost constraint is fully honored throughout: Google Places API free tier for lead generation, Playwright WA Web automation with human-in-the-loop for outreach, direct ffmpeg subprocess for video compositing, PyInstaller for cross-platform binary packaging, and CF Worker KV for referral tracking. Every component has a validated €0 alternative with enterprise-grade quality.

The dominant risk is the WhatsApp number ban before achieving critical mass. A perma-ban in week 1 restarts the entire acquisition clock and loses first-mover momentum in each vertical and city. This risk demands a mandatory 4-week warmup protocol (10 msg/day weeks 1-2, 20 msg/day weeks 3-4, with random 90-300s delays and 40%+ template variation) baked into the Sales Agent architecture before the first message is sent. The secondary risk is macOS Gatekeeper on Sequoia 15.1+ causing install failures at purchase — the `/installa` page with animated GIFs is a launch blocker, not a nice-to-have.

---

## Key Findings

### Recommended Stack

The existing stack (Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent) requires no modification for launch. Four new capability areas add targeted Python libraries. The Sales Agent uses `playwright` 1.58.0 (not Selenium — better async, persistent sessions, less detectable) with `google-maps-services-python` for lead sourcing (Google Places API free tier: 28,500 calls/month). The video compositor V6 uses direct `ffmpeg` subprocess calls as primary with `moviepy` 2.2.1 only for frame-accurate overlay timing, plus `edge-tts` for Italian voiceover and `pydub` for audio normalization. The Windows MSI build uses `tauri-action` GitHub Actions with WiX toolset (auto-configured by Tauri bundler), `pyttsx3` for Windows SAPI5 TTS fallback, and `piper-onnx` Python package for cross-platform Piper TTS (eliminates hardcoded path issues). Content repurposing uses `faster-whisper` (already in voice agent stack) + Groq `llama-3.3-70b-versatile` (already used for Sara NLU) for transcript-to-blog generation at zero incremental cost.

**Core technologies:**
- `playwright` 1.58.0 + `playwright-stealth`: WA Web automation — Microsoft-maintained, async-native, persistent browser contexts; superior to Selenium for WA Web SPA handling
- `google-maps-services-python` (Google Places API): Lead sourcing — data quality superior to PagineGialle, free tier covers 28,500 calls/month, returns phone/rating/category/hours
- `ffmpeg` (direct subprocess): Video compositing — already validated in V5 pipeline; 8-10x faster than moviepy for simple encode/concat operations
- `moviepy` 2.2.1: Frame-accurate overlay only — transparency compositing fixed in this version; use narrowly for Sara telefonata scene
- `pyttsx3` + `piper-onnx`: Windows TTS fallback chain — `piper-onnx` is cross-platform by design (no binary path issues); `pyttsx3` wraps SAPI5 for offline fallback
- `PyInstaller` 6.19.0: Windows sidecar binary — must be built on `windows-latest` GitHub Actions runner; macOS cross-compilation is impossible
- `webrtcvad-wheels`: Windows-compatible webrtcvad — pre-compiled wheels replace `webrtcvad` which requires compilation on Windows

### Expected Features

This milestone defines launch mechanics, not product features. The product is already complete.

**Must have (table stakes — blocks first sale if absent):**
- Video demo (4:30-5:00 min) showing all app screens including Pacchetti and Fedeltà — buyers will not pay €497 without seeing the product
- Professional screenshots of every page with realistic Italian data — landing credibility requires complete visual coverage
- Mobile-responsive landing page with 3-tap path to Stripe checkout — 95%+ of WA traffic opens on mobile
- E2E purchase flow verified end-to-end: Stripe → webhook → license email → activation → app unlock
- macOS `/installa` installation guide page with Sequoia 15.1+ Gatekeeper bypass steps (animated GIFs, not static screenshots)
- Pricing above the fold with loss framing: "Un gestionale in abbonamento: €1.800 in 3 anni. FLUXION: €497 una volta."

**Should have (competitive differentiators):**
- WhatsApp outreach Sales Agent (Google Places lead scraping + Playwright automation, 20 msg/day, semi-automated with human review gate)
- Voice notes as WA outreach format (founder records 15-30s voice note; 22-28% response rate vs 8-15% for text)
- Vertical-specific WA message templates (parrucchiere, officina, estetica, palestra, dentista) — personalization beats generic 3-5x
- Commercialisti referral channel (€100 cash referral per conversion; 1 commercialista serves 50+ PMI clients)
- YouTube as video hosting — WA YouTube links get 18-22% CTR; CF Pages has 25MB file limit (blocks direct upload of 42MB+ video)
- UTM parameters on all outreach links (`?utm_source=wa&utm_medium=outreach&utm_campaign=[verticale]-[regione]`) — unrecoverable without from day 1

**Defer to post-launch (Sprint 6 / v1.x):**
- Windows MSI build — unlocks 70% of market but does not block macOS-first sales
- Content repurposing pipeline — requires V6 video as source material; value as amplifier not acquisition
- Referral program — requires 10+ paying clients; zero clients means zero referrers
- Blog/SEO content — long-term play, months to traffic
- Click-to-WhatsApp ads — requires validated LTV before paid acquisition
- Windows EV code signing certificate (€299/year — defer until revenue justifies)

### Architecture Approach

The launch pipeline is three new subsystems running alongside the existing production architecture without modifying it. The core Tauri app, CF Worker, and CF Pages remain unchanged. Subsystem 1 is the screenshot + video pipeline: CGEvent-based navigation on iMac (the only machine that runs the Tauri app) → SCP/git push screenshots to MacBook → ffmpeg compositing on MacBook → Vertex AI Veo3 for AI B-roll clips. Subsystem 2 is the Sales Agent: `lead_generator.py` (already built) generates `leads.json` from Google Places → new `sales-agent/agent.py` reads the JSON and operates Playwright on WA Web with SQLite state tracking. Subsystem 3 is the Windows MSI CI pipeline: GitHub Actions `windows-latest` runner with WiX toolset + pre-built PyInstaller sidecar binary. All subsystems use a pipeline-with-shared-state-file pattern (JSON handoff between stages, no inter-process daemons) which is simple, debuggable, and appropriate for a one-operator launch workload.

**Major components:**
1. `scripts/capture-screenshots.py` (iMac) — CGEvent UI navigation + `screencapture`, all 21+ pages with seed data
2. `scripts/compose-video-v6.py` (MacBook) — ffmpeg + Edge-TTS + Veo3 AI clips → `fluxion-promo-v6.mp4`
3. `sales-agent/agent.py` (MacBook) — Playwright WA Web automation with rate limiter + SQLite state DB
4. `.github/workflows/build-windows.yml` (CI) — WiX MSI + PyInstaller sidecar → GitHub Releases
5. `landing/index.html` V2 — V6 video embed, mobile-first CTA, loss-framing copy

### Critical Pitfalls

1. **WhatsApp number perma-ban** — Enforce 4-week warmup protocol (10 msg/day weeks 1-2, 20 msg/day weeks 3-4). Use `random.gauss(mu=120, sigma=40)` second delays, 5-minute pause every 5 messages, minimum 5 template variants with >40% text difference. Monitor delivery rate (<90% = stop), read rate (<30% = stop), block rate (>2% = 72h cooldown). Keep 2-3 aged backup SIMs. Build warmup scheduler as non-optional parameter in Sales Agent — not a configuration option that can be bypassed.

2. **macOS Gatekeeper failure on Sequoia 15.1+** — The Control-click shortcut was removed in Sequoia 15.1. The 6-step bypass (System Settings → Privacy & Security → Open Anyway → admin password) is non-obvious to PMI owners. The `/installa` page is a launch blocker: ship it before first paid customer, use animated GIFs for each step, link directly from post-purchase Resend email, embed QR code in DMG background image. Test cold install on Sequoia 15.x with zero prior Keychain entries before publishing payment links.

3. **Proxy API rate limits under concurrent load** — Groq free tier is 30 RPM. At 30-50 customers with 3-5 Sara interactions/day, peak hours (10:00-12:00, 15:00-18:00) exhaust the RPM limit. Implement dual key pools (Sales Agent uses off-peak hours; Sara live calls get priority pool). Wire Cerebras fallback (1M TPD) as first fallback. Add request queuing in CF Worker with 15-second retry before failing. This is Sprint 1 prerequisite, not Sprint 5 enhancement.

4. **PagineGialle scraping IP ban + stale data** — PagineGialle uses Cloudflare challenges; static scrapers return empty HTML or get blocked within hours. Their data is 2-4 years stale in Southern Italy. Use Google Places API (primary, free tier) and PagineBianche only as secondary. Validate every number: Italian mobile starts with 3 (3XX XXX XXXX). Dedup by phone number (not business name). Flag leads with no website + no rating + no reviews for manual review queue, not auto-outreach.

5. **Video loses viewer in first 8 seconds** — Opening on the dashboard triggers "questo non fa per me" before any value is communicated. First 8 seconds must show a missed phone call scenario the PMI owner instantly recognizes. PAS formula is mandatory: Problem (15 sec) → Agitate (30 sec) → Solution. Dashboard appears at second 45+. Sara demonstration must appear before minute 2. YouTube thumbnail must show a person in their work context, not the app UI. Validate with YouTube analytics: average view duration must exceed 2:30 on first 100 views.

---

## Implications for Roadmap

Based on combined research, the dependency chain is strict and sequential: seed data → screenshots → video → landing → outreach. This forces a specific phase order.

### Phase 1: Product Ready (Sprint 1)
**Rationale:** Several pre-launch product issues exist (seed data needs Pacchetti + Fedeltà data, phone-home pricing needs to reflect €497/€897, proxy API needs dual-pool rate limiting). These are internal-facing and unblock every subsequent phase. No marketing asset can be finalized without realistic demo data. The proxy rate limit fix is categorized here because it is a prerequisite for Sales Agent activation, not a post-launch patch.
**Delivers:** Correct seed data in DB, accurate prices in Rust, Cerebras fallback wired in CF Worker, Groq dual-pool implemented
**Addresses:** E2E purchase flow (table stakes), Proxy rate limits (PITFALL 8)
**Avoids:** Rate limit exhaustion killing Sara calls during sales agent peak (Pitfall 8); fake data in demo destroying trust (Pitfall 5 contributing factor)

### Phase 2: Screenshot Perfetti (Sprint 2)
**Rationale:** Screenshots are the blocking dependency for Video V6. The two missing screens (Pacchetti + Fedeltà) are specifically required for the video storyboard. All 21 current screenshots require iMac + CGEvent — this cannot be done on MacBook.
**Delivers:** 23+ PNG screenshots of all app pages with realistic Italian seed data
**Uses:** CGEvent Python (Quartz), `screencapture`, `scripts/capture-screenshots.py` V2
**Implements:** iMac capture pipeline → SCP → MacBook handoff
**Avoids:** Launching Video V6 without all scenes (forces rework); landing page with incomplete visual coverage

### Phase 3: Video V6 (Sprint 3)
**Rationale:** Video is the centerpiece of the landing page and the primary asset in all WA outreach messages. YouTube link in WA messages gets 18-22% CTR — without a quality video on YouTube, the Sales Agent has no credible content to send.
**Delivers:** `fluxion-promo-v6.mp4` (4:30-5:00 min) on YouTube, PAS formula structure, all features shown including Pacchetti + Fedeltà
**Uses:** `ffmpeg` direct subprocess, `edge-tts` (IsabellaNeural), `moviepy` 2.2.1 (Sara scene overlay), `google-cloud-aiplatform` Veo3 for 5 new AI clips
**Implements:** `scripts/compose-video-v6.py` (evolves from V5), `scripts/regenerate-clips-v3.py`
**Avoids:** Dashboard-first opening (Pitfall 5); "Kodak/film grain" in Veo3 prompts (causes black borders); `zoompan` without pre-scaling (causes jitter); video hosted on CF Pages (25MB limit)

### Phase 4: Landing + Deploy (Sprint 4)
**Rationale:** The landing page cannot be finalized without the video embed (its centerpiece). This phase also includes the critical `/installa` page — a launch blocker. The E2E purchase flow verification must happen here, before any traffic is sent. No outreach before these are confirmed working.
**Delivers:** `landing/index.html` V2 with V6 video embed, mobile-optimized (3-tap to Stripe), `/installa` page with Sequoia 15.x animated GIF guides, E2E purchase flow verified (Stripe → webhook → license email → activation)
**Uses:** CF Pages `wrangler pages deploy --branch=production`, Resend email with installation link
**Avoids:** Gatekeeper install failures (Pitfall 2); mobile-broken landing killing WA traffic conversion; E2E flow silently broken before paying customers arrive

### Phase 5: Sales Agent WA (Sprint 5)
**Rationale:** Sales Agent is the primary acquisition channel. It can only activate after the full funnel (screenshots + video on YouTube + landing live + E2E verified) is ready. Sending 20 messages/day pointing to a broken or incomplete funnel wastes irreplaceable early-mover lead contacts.
**Delivers:** `sales-agent/agent.py` with Playwright + rate limiter + SQLite state DB; Google Places scraping for 100 leads per vertical per city; 5 vertical WA message templates; commercialisti outreach email + unique ref link
**Uses:** `playwright` 1.58.0, `playwright-stealth`, `google-maps-services-python`, `beautifulsoup4` (PagineBianche secondary), `jinja2` for template engine, `sqlite3` for state tracking
**Avoids:** WA number perma-ban (Pitfall 1 — warmup protocol mandatory); PagineGialle scraping failure (Pitfall 4 — Google Places as primary); fully automated send without human review gate

### Phase 6: Post-Lancio Amplification (Sprint 6)
**Rationale:** These components require either a stable binary (Windows MSI), existing paying clients (referral program), or the final video (content repurposing). None can proceed without prior phases completing. Windows MSI unlocks 70% of the market but does not block first macOS sales.
**Delivers:** Windows MSI build (GitHub Actions WiX + PyInstaller sidecar); content repurposing pipeline (V6 → 5 vertical 30s clips); referral program (?ref= tracking in CF Worker KV, triggered at 30-day + 10 Sara bookings threshold)
**Uses:** `tauri-action` GitHub Actions, `PyInstaller` 6.19.0, `pyttsx3`, `piper-onnx`, `webrtcvad-wheels`, `faster-whisper` + Groq for blog generation
**Avoids:** Windows SmartScreen/AV false positives (Pitfall 3 — VirusTotal pre-release check mandatory, MSI not NSIS); referral at purchase (Pitfall 6 — 30-day trigger enforced); low-quality content repurposing (Pitfall 7 — manual cold-watch test for every clip before publish)

### Phase Ordering Rationale

- The screenshot → video → landing dependency chain is absolute. No step can be parallelized with its predecessor because each phase consumes the output artifact of the previous phase as required input.
- The Sales Agent (Sprint 5) is architecturally independent of Sprints 2-4, but should not activate before them — sending traffic to an incomplete funnel wastes non-recoverable first contacts in each vertical and city.
- The Proxy rate limit fix (Sprint 1) must precede Sales Agent activation (Sprint 5) by design — it is a prerequisite that happens to land in an earlier sprint, not an afterthought.
- Windows MSI (Sprint 6) is deliberately last: it requires a stable binary, and building it before launch creates duplicate work if the Rust codebase changes.
- Content repurposing and referral program both have upstream dependencies (V6 video and paying clients respectively) that make earlier placement physically impossible.

### Research Flags

Phases likely needing `/gsd:research-phase` during planning:
- **Phase 3 (Video V6):** Veo3 prompt engineering is sensitive to exact wording (validated "no Kodak/film grain" constraint from V5). Storyboard scene timing and voiceover pacing require iterative testing. The composition pipeline is complex (3 input sources: AI clips + screenshots + TTS). Research into specific Veo3 prompts for Pacchetti/Fedeltà scenes is warranted before generation.
- **Phase 5 (Sales Agent WA):** WhatsApp Web DOM structure changes without notice. The Playwright selectors for finding a contact and opening a chat window may need verification against the current WA Web DOM before the agent is built. Rate limit thresholds are community-derived and may shift with Meta policy changes.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Product Ready):** Seed data SQL, Rust pricing constants, and CF Worker Groq/Cerebras dual-pool are all established patterns with known implementations. No research needed.
- **Phase 2 (Screenshots):** CGEvent pattern is validated and documented in MEMORY.md. The script pattern exists from S109/S113. Update rather than research.
- **Phase 4 (Landing + Deploy):** CF Pages deploy procedure is established (`--branch=production` pattern documented). E2E verification is manual testing. No research needed.
- **Phase 6 (Windows MSI):** Tauri documentation for WiX is comprehensive. PyInstaller Windows build pattern is documented in STACK.md. GitHub Actions `tauri-action` is official and well-documented.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies verified against PyPI and official docs (2026-03-26). Version numbers confirmed current. Windows compatibility fixes cross-referenced against `windows-compat-research.md` internal research file. |
| Features | HIGH | Based on 9 prior CoVe 2026 research files (272KB, 76+ sections) verified 2026-03-25/26. Feature dependencies map is explicit and verified. Anti-features are backed by conversion data (loss framing 2.1x, voice notes 22-28% CTR) from multiple sources. |
| Architecture | HIGH | Existing codebase analyzed directly (`lead_generator.py`, `compose-final-video.py`, `fluxion-proxy/src/index.ts`). New subsystem designs follow patterns already validated in production (CGEvent, ffmpeg pipeline, CF Worker). No theoretical architecture — all patterns have been executed in prior sprints. |
| Pitfalls | HIGH | WA ban mechanics verified from web search (tisankan.dev 2025) + Meta policy docs. Gatekeeper Sequoia change verified (Apple changelog). Tauri MSI false positives verified from upstream GitHub issue #4749. Referral timing backed by GrowSurf + Cost Analysts B2B referral research. |

**Overall confidence:** HIGH

### Gaps to Address

- **WA Web DOM selectors:** Playwright selectors for finding a contact on WhatsApp Web were not captured in this research. Requires a brief manual inspection of current WA Web DOM before writing `sales-agent/agent.py`. Low risk — patterns are well-documented in the Playwright community — but needs verification during Sprint 5 planning.
- **Veo3 Pacchetti/Fedeltà prompt wording:** The storyboard exists (`storyboard-v6-research.md`) but specific prompt text for the two new scenes (Pacchetti bundles demo, Fedeltà loyalty demo) has not been written. These scenes involve app UI overlay compositing which has specific Veo3 constraints. Validate during Sprint 3 planning.
- **Resend SPF/DKIM for Italian mail providers:** PITFALLS.md flags that `noreply@` domains have high spam filter rates on Libero.it and Alice.it (most common Italian consumer providers). The current Resend configuration uses `fluxion.gestionale@gmail.com`. Verify whether SPF/DKIM is configured on the CF DNS for the sending domain before Sprint 4 deploy — not doing this means post-purchase emails land in spam for a significant percentage of Italian customers.
- **WA Business vs Personal number for outreach:** Research recommends a dedicated SIM for outreach (not the founder's personal number). It is unclear whether an aged SIM is available or needs to be acquired. Confirm before Sprint 5 starts.

---

## Sources

### Primary (HIGH confidence)
- `.claude/cache/agents/growth-first-100-clients-research.md` — WA warmup strategy, rate limits, scraping alternatives, commercialisti channel, 90-120 day first-100-clients timeline
- `.claude/cache/agents/video-sales-outreach-research-2026.md` — PMI psychology, WA message templates, funnel structure, loss framing data
- `.claude/cache/agents/competitor-video-analysis-2026.md` — Fresha/Treatwell/Mindbody/AgendaPro video analysis, demo best practices (701 lines)
- `.claude/cache/agents/landing-v2-optimization-research.md` — Conversion benchmarks, video embed strategy, mobile-first requirements
- `.claude/cache/agents/storyboard-v6-research.md` — V5 lessons learned, V6 storyboard requirements
- `.claude/cache/agents/us-smb-sales-outreach-research-2026.md` — Toast/SMB playbook, value-first framework, message structures
- `.claude/cache/agents/distribution-no-signing-research-2026.md` — macOS Gatekeeper Sequoia changes, Windows MSI vs NSIS false positive comparison
- `.claude/cache/agents/windows-compat-research.md` — `pyttsx3`, `piper-onnx`, `webrtcvad-wheels` Windows-specific fixes
- `CLAUDE.md` permanent architecture decisions (S84) — TTS 3-tier, LLM proxy, distribution, compatibility matrix
- `MEMORY.md` — CGEvent screenshot pattern, Veo3 pipeline, CF Pages deploy constraints

### Secondary (MEDIUM confidence — web search verified 2026-03-26)
- [PyPI playwright 1.58.0](https://pypi.org/project/playwright/) — version confirmed current
- [PyPI moviepy 2.2.1](https://pypi.org/project/moviepy/) — transparency fix confirmed
- [Tauri v2 Windows installer docs](https://v2.tauri.app/distribute/windows-installer/) — WiX + `tauri-action` patterns
- [tauri-apps/tauri GitHub issue #4749](https://github.com/tauri-apps/tauri/issues/4749) — MSI vs NSIS false positive comparison
- [WhatsApp automation ban mechanics](https://tisankan.dev/whatsapp-automation-how-do-you-stay-unbanned/) — ban risk thresholds
- [Google Places API client libraries](https://developers.google.com/maps/documentation/places/web-service/client-libraries) — free tier 28,500 calls/month confirmed
- [GrowSurf: Why referral programs fail](https://growsurf.com/blog/why-referral-programs-fail) — timing and incentive research

### Tertiary (inference / community)
- Groq RPM exhaustion at 30+ concurrent customers — calculated from published Groq free tier limits (14,400 RPD / 30 RPM) against modeled customer usage; exact threshold may vary
- WA Trust score decay at >2% block rate — community-derived threshold, not published by Meta officially; treat as directional guideline

---

*Research completed: 2026-03-26*
*Ready for roadmap: yes*
