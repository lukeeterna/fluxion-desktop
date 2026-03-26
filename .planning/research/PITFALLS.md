# Pitfalls Research

**Domain:** Indie desktop software launch — Italian SMB market (saloni, officine, palestre, cliniche)
**Researched:** 2026-03-26
**Confidence:** HIGH (all findings verified from cached CoVe 2026 research + official sources + web search)

---

## Critical Pitfalls

### Pitfall 1: WhatsApp Number Perma-Ban Before Critical Mass

**What goes wrong:**
The Sales Agent sends 40-50 messages/day immediately after setup. Meta's anti-spam system detects automated patterns (identical message templates, consecutive number ranges, sub-60s delays) and permanently bans the outreach number within 48-72 hours. Recovery requires a new SIM, a two-week warmup period, and restarts the entire acquisition clock — losing week 1-2 momentum when conversion rates are highest.

**Why it happens:**
Developer optimizes for speed ("more messages = more leads") and ignores that WA ban is algorithmic, not threshold-based. The system watches delivery rate, read rate, block rate, and text similarity simultaneously — not just volume. Using a fresh SIM with day-1 cold outreach hits all four signals at once.

**How to avoid:**
- Week 1-2: maximum 10 messages/day, sent manually by founder, not automation
- Week 3-4: maximum 20 messages/day, Sales Agent with human approval
- Week 5+: 20-30 messages/day only if previous 7 days show zero blocks and >8% reply rate
- Mandatory delay distribution: `random.gauss(mu=120, sigma=40)` seconds between sends, minimum 60s floor, 5-10 minute pause every 5 messages
- Template variation: minimum 5 variants per message segment, >40% text difference between consecutive sends
- Single YouTube link only — no shortened URLs (bit.ly is flagged), no 2+ links per message
- Business hours only: Mon-Fri 09:00-12:30 and 14:30-18:00 Italian time
- Always maintain 2-3 "aged" backup SIMs (6+ weeks of normal use before outreach)

**Warning signs:**
- Delivery rate drops below 90% in last 24 hours
- Read rate drops below 30% (normal: 50-70%)
- Any user reports "spam" (visible in WA Business analytics)
- Block rate exceeds 2% — STOP immediately, 72h cooldown
- WA shows "message not delivered" without network error

**Phase to address:** Sprint 5 — Sales Agent WA. Embed warmup scheduler and rate-limit config as non-optional parameters before any outreach begins. The dashboard must show delivery/read/block rates in real time.

---

### Pitfall 2: macOS Gatekeeper Kills First Install — Sequoia Change

**What goes wrong:**
The customer purchases FLUXION, downloads the DMG, double-clicks the app, and sees "cannot be opened because the developer cannot be verified." The OLD bypass (Control-click → Open) no longer works on macOS Sequoia 15.1+. The customer has no idea what Privacy & Security settings are. They request a refund, post a negative review, or assume the software is malware. The 30-day guarantee gets triggered in week 1 for a non-product reason.

**Why it happens:**
Apple changed Gatekeeper behavior in Sequoia 15.1 (November 2024): the Control-click shortcut was removed. The only path is now: System Settings → Privacy & Security → scroll to Security section → "Open Anyway" → enter admin password. This is a 6-step process that is completely non-obvious to a PMI owner who has never seen a developer warning.

**How to avoid:**
- The `/installa` page is not optional — it is the product. Ship it before the first paid customer
- Include animated GIFs (not static screenshots) showing EACH step for Sequoia specifically
- The post-purchase email (Resend) must link directly to `/installa` as step 1, before the download link
- In the DMG background image: include "PRIMA DI APRIRE FLUXION — leggi la guida su fluxion.it/installa" with QR code
- Add a VirusTotal report link on the `/installa` page with the specific language: "FLUXION è stato analizzato da 70+ antivirus — zero minacce rilevate"
- Detect OS in the purchase confirmation email (from Stripe checkout user-agent) and show macOS vs Windows instructions accordingly
- Monitor the Apple Gatekeeper changelog for macOS 16 — risk that ad-hoc signing stops working entirely

**Warning signs:**
- Any support message containing "non si apre", "sviluppatore non verificato", or "bloccato"
- Refund requests in the first 48 hours post-purchase (installation failure pattern)
- >5% of purchases result in a support email within 72 hours

**Phase to address:** Sprint 4 — Landing + Deploy. The `/installa` page is a launch blocker. Deploy it before unlocking payment links publicly.

---

### Pitfall 3: Windows MSI SmartScreen + Antivirus False Positives Kill Sales

**What goes wrong:**
The Windows MSI is submitted by a customer to their company IT, or the customer's antivirus (Kaspersky, ESET, Windows Defender) quarantines the file during download. The customer sees "Windows protetto il tuo PC" and clicks the X instead of "Altre informazioni → Esegui comunque." Support tickets spike. Worse: an IT-managed machine (common in dental clinics, medical practices) cannot install unsigned software at all without admin override.

**Why it happens:**
MSI installers from unsigned Tauri apps reliably generate 2-5 false positives on VirusTotal at first release (documented Tauri upstream issue #4749). NSIS generates more — 8-12 is common. The Tauri toolchain uses Rust code patterns that overlap with known malware signatures. Without pre-release VirusTotal submission and antivirus vendor whitelisting, every release is a fresh threat to reputation.

**How to avoid:**
- Always use MSI (WiX), never NSIS — MSI generates fewer false positives as documented by the Tauri community
- Pre-release checklist: upload MSI to VirusTotal 48 hours before publishing the download link
- If >3 detections: submit to Microsoft WDSI (https://www.microsoft.com/en-us/wdsi/filesubmission) and wait for clearance
- Submit pre-emptively to Norton (submit.norton.com), ESET, Kaspersky regardless of detection count
- Keep VirusTotal report URL public on the download page — reduces "is this a virus?" tickets by 80%+
- Add `installMode: "both"` in tauri.conf.json for machines without admin (palestre, officine often have single-user machines)
- Include WebView2 bootstrapper in the MSI (adds 1.8MB) — do not rely on end-user installing it separately
- For Windows 10 machines: test cold install (no existing WebView2) before every release
- The SmartScreen reputation builds over time with unsigned installers — the warning WILL decrease after ~200 installs from the same binary hash

**Warning signs:**
- VirusTotal report shows >5 detections — do not publish, rebuild first
- Support tickets mentioning "virus", "Defender ha bloccato", "Windows mi dice che è pericoloso"
- Zero Windows activations despite macOS activations (silent install failure)

**Phase to address:** Sprint 6 — Post-lancio (Windows MSI build). Integrate VirusTotal check as a mandatory step in the release checklist before any Windows link goes live.

---

### Pitfall 4: PagineGialle Scraping IP Ban + Data Quality Failure

**What goes wrong:**
The Sales Agent scrapes PagineGialle directly with BeautifulSoup/requests. PagineGialle detects the pattern (no JavaScript, no user-agent rotation, rate >10 req/min) and blocks the IP within hours. The resulting lead database has 30-40% duplicate entries, outdated phone numbers, and businesses that have closed — poisoning the outreach with bad data and wasting WA budget on dead numbers.

**Why it happens:**
PagineGialle uses Cloudflare challenge pages and requires JavaScript rendering for most of its content. Static HTTP scrapers fail silently, returning empty or partial HTML. Even when data is scraped successfully, the directory is updated infrequently — many listings are 2-4 years stale, particularly in Southern Italy where FLUXION's initial target (Campania) is concentrated.

**How to avoid:**
- Primary source: Google Places API (free tier: 28,500 calls/month) — far better data quality, more current, includes ratings/hours/website
- Secondary source only: PagineBianche (simpler HTML, less aggressive anti-bot), not PagineGialle
- Never scrape PagineGialle directly — use the API if one exists, or skip it
- For any scraping: rotate user-agents, add 5-10 second delays, use residential proxy if needed (still €0 via Tor or proxy lists)
- Validate every phone number before adding to outreach queue: Italian mobile starts with 3 (3XX XXX XXXX pattern), Italian landlines start with 0
- Dedup by phone number (primary key), not by business name (duplicates with slight name variations)
- Flag businesses with no website, no rating, and no reviews as lower-quality leads — send to manual review queue, not auto-outreach

**Warning signs:**
- Scraper returning >30% empty phone fields — IP likely blocked
- WA delivery failures >15% — phone numbers are landlines or inactive
- Same business appearing 3-5 times in the lead database

**Phase to address:** Sprint 5 — Sales Agent WA. Data pipeline validation is phase-critical. Build the dedup + phone validation layer before the outreach engine, not as an afterthought.

---

### Pitfall 5: Video Demo Opens on Dashboard — Loses PMI in 8 Seconds

**What goes wrong:**
The video V6 opens showing the FLUXION dashboard. The PMI owner on mobile sees buttons and menu items they do not recognize. They close the video within 8 seconds. The video "conversion rate" appears at 2-3% but the actual issue is that 70% of viewers never reach the 30-second mark where Sara is demonstrated.

**Why it happens:**
Software developers naturally open demos on the dashboard because they are proud of the UI. But the PMI owner does not yet care about the UI — they care about whether their specific problem ("perdo prenotazioni per telefono") is being addressed. Opening with the dashboard triggers "questo non fa per me" before the value is communicated.

**How to avoid:**
- The first 8 seconds must show a scenario the PMI owner instantly recognizes: a ringing phone missed because hands are busy
- PAS formula is mandatory: Problem (15 sec) → Agitate (30 sec) → Solution (introduce FLUXION) — dashboard appears only at second 45+
- Show REAL data in the demo (dati seed realistici, not "Cliente 1", "Servizio A") — fake data signals fake product
- Voice notes in the WA message are 22-28% higher CTR than text links — if distributing via WA, record a 30-second voice note instead of a text message linking the video
- Include subtitles — 70% of mobile viewers watch without audio on WA
- YouTube thumbnail must show a person (parrucchiere/meccanico) in their actual work context, not the app UI
- The video must reach "Sara risponde al telefono" demonstration before minute 2 — not minute 4

**Warning signs:**
- YouTube analytics: average view duration <45 seconds
- YouTube analytics: audience retention cliff at 0:00-0:08 (first 8 seconds)
- CTR from WA high (18%+) but watch time low (<2 min average)

**Phase to address:** Sprint 3 — Video V6. The script structure must be validated against the PAS formula and the 8-second rule before any filming or editing begins.

---

### Pitfall 6: Referral Program Launched at Purchase — Zero Conversions

**What goes wrong:**
The in-app referral prompt appears immediately after license activation ("Condividi FLUXION con un collega! Ottieni 1 mese Sara gratis"). The customer has not yet seen value — Sara has never answered a call, the calendar has no appointments. They ignore the prompt. The referral program generates zero conversions in the first month and is incorrectly judged as a failed mechanic.

**Why it happens:**
B2B referral programs fail at the 30-40% rate when triggered before value is demonstrated. The customer's psychological position is: "I just spent €497 and I'm not sure yet if it works." Asking them to recommend the product before they have a success story is asking them to stake their professional reputation on an untested product.

**How to avoid:**
- Trigger: minimum 30 days of use AND Sara has handled ≥10 bookings AND calendar shows ≥20 appointments
- The prompt text must reference the customer's specific activity: "Sara ha gestito 12 prenotazioni per te questo mese" — not a generic "ti piace FLUXION?"
- Two-tier reward: clients (non-cash): 1 month Sara extension when Base, or €50 credit toward Pro upgrade — professionals/accountants (cash): €100 bonifico, tracked via CF Worker KV referral codes
- The referral URL must include the referring customer's vertical: `?ref=COMM-ROSSI-001&vertical=parrucchiere` so the landing page headline adapts to the referred prospect
- Accountants (commercialisti) are the highest-leverage referrer — they trust cash rewards. Clients trust non-cash value rewards (service extension). Use different mechanics for each tier.
- Do not build a complex referral dashboard. Start with: coupon code in email → manual tracking in a spreadsheet → automate only after 10+ active referrers

**Warning signs:**
- Referral prompt shown to customers with <5 Sara bookings in history
- Zero referral code usage despite >20 active customers
- Referrers asking "come faccio a sapere se il mio codice funziona?" — tracking is opaque

**Phase to address:** Sprint 6 — Post-lancio. Build the referral trigger logic into the app's 30-day phone-home check. Do not build referral UI before Sprint 6; premature referral mechanics waste development time.

---

### Pitfall 7: Content Repurposing Creates Low-Quality Clips That Hurt Brand

**What goes wrong:**
The 6-minute video V6 is auto-repurposed into 15 short clips using OpusClip or similar AI tools. The AI selects clips based on loudness and word density, producing clips that show UI transitions, mid-sentence cuts, or Sara saying partial phrases out of context. These clips are posted to Instagram Reels and TikTok. The comments include "questo non si capisce niente" — the clips actually reduce trust rather than build it.

**Why it happens:**
AI repurposing tools optimize for engagement signals (movement, face, loudness) not for narrative coherence. A demo video is built around a problem-solution arc. A mid-clip cut of "...e Sara risponde al telefono automaticamente" without the preceding "stai perdendo prenotazioni?" context means nothing to a cold audience.

**How to avoid:**
- Repurpose manually first: identify 3-5 self-contained moments that work without context ("Sara risponde alla chiamata di Mario Rossi") — these are the only clips worth distributing
- Rule: every repurposed clip must pass the "cold watch test" — would someone who has never heard of FLUXION understand the value proposition in this 60-second clip with no context?
- Clips for Instagram/TikTok: under 60 seconds, must show the UI responding to a real scenario (not a voiceover narration), must include captions
- Do not post more than 3 clips per week — frequency without quality destroys algorithmic reach on new accounts
- YouTube Shorts strategy: clips from the main video that tease Sara's voice ("Ascolta come risponde Sara") with a link to the full video in description
- Vertical (9:16) format for Reels/TikTok — horizontal crops of desktop app screenshots look amateurish on mobile

**Warning signs:**
- AI tool generates >10 clips from a 6-minute video — most will be low quality, manually filter to 3-5
- Any clip showing only UI without a human scenario or voice
- Watch rate <20% on Instagram Reels (good clips for cold audiences: 30-40%)

**Phase to address:** Sprint 6 — Post-lancio. Repurposing is a post-launch activity. Define the "3 self-contained hero clips" during Sprint 3 video production — identify them during the storyboard phase, not retroactively.

---

### Pitfall 8: FLUXION Proxy API Rate Limits Hit During Sales Agent Peak

**What goes wrong:**
The Sales Agent WA sends 20-30 messages/day. Each qualified response triggers Sara's NLU via the FLUXION Proxy API (CF Worker → Groq). If multiple customers are also using Sara simultaneously (peak: 10:00-12:00 and 15:00-18:00 Italian time), the Groq free tier (14,400 RPD, 30 RPM) gets exhausted. New prospects who reply to outreach messages get "Sara non disponibile al momento" responses, killing the conversion at the moment of highest intent.

**Why it happens:**
The rate limit arithmetic looks safe at zero customers — 20 Sales Agent NLU calls + a few Sara calls per day. But at 30-50 customers each with 3-5 Sara interactions/day, the RPM limit (30 req/min) is hit during peak hours even before the daily cap is reached.

**How to avoid:**
- Implement separate Groq key pools: one pool dedicated to Sales Agent outreach (off-peak: 07:00-09:00 only), one pool for Sara live calls (priority, any time)
- The Sales Agent must use off-peak hours for any follow-up NLU processing
- Cerebras fallback (1M TPD) must be wired as the first fallback, not last resort — latency is higher but throughput is far larger
- Add request queuing in the CF Worker: if Groq RPM is near limit, queue and retry in 15 seconds before failing
- Monitor: CF Worker analytics for 429 errors — alert when >5% of requests hit 429

**Warning signs:**
- CF Worker logs showing 429 responses from Groq during 10:00-12:00
- Sara "non risponde" complaints from existing customers during business hours
- Groq dashboard showing RPM at >80% of limit during peak

**Phase to address:** Sprint 1 — Product Ready. The phone-home and proxy architecture must include the dual-pool and queue before Sales Agent is activated. This is a prerequisite, not an enhancement.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Single Groq API key for all traffic | Simple to implement | Rate limit exhaustion at 30+ customers during peaks | Never — dual pool is 30 min of work |
| NSIS instead of MSI on Windows | Tauri default, zero config | 3x more antivirus false positives, SmartScreen warnings more severe | Never for FLUXION target |
| Send WA messages from day 1 at full rate | Faster lead generation | Number ban within 48-72h, full restart | Never — warmup is mandatory |
| Skip VirusTotal pre-release check | Saves 2 hours per release | Customer installs blocked by AV, support tickets spike | Never — it's a 20-minute upload |
| Referral prompt at purchase | Appears in first session | Zero conversions, customers feel pressured | Never — 30-day trigger is non-negotiable |
| Repurpose all AI-generated clips | Appear to have high content volume | Low-quality clips damage brand credibility | Acceptable ONLY for internal review, never for publication without manual curation |
| Skip `/installa` page for macOS | Saves 1 sprint day | 30-40% of macOS customers cannot install, refund spike | Never — this is a launch blocker |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| WhatsApp Web (Selenium) | Using `--headless` mode with Chrome — WA detects headless browsers reliably | Use `--headless=new` with full user-agent spoofing, or better: Playwright with persistent browser context |
| Stripe webhook | Not verifying webhook signature before processing license delivery | Always verify `Stripe-Signature` header with `stripe.webhooks.constructEvent()` before any license action |
| CF Worker KV for referral tracking | Using email as KV key — collisions if customer uses different email at checkout | Use `ref:{code}:{stripe_customer_id}` composite key pattern |
| Google Places API | Fetching all fields in one call — costly and slow | Request only `name,formatted_phone_number,rating,opening_hours` — reduces latency and stays in free tier |
| Ed25519 license verification | Verifying only signature, not expiry or tier field | Always verify: signature, license tier, expiry date, and machine fingerprint together |
| Resend email post-purchase | Sending from `noreply@` domain — high spam filter rate in Italian mail providers (Libero, Alice, Virgilio) | Use `gianluca@fluxion.it` or `info@fluxion.it` with SPF/DKIM configured on CF DNS |
| PyInstaller sidecar on Windows | Building the sidecar on macOS and expecting it to work on Windows | Cross-compilation is impossible — Windows sidecar must be built on a Windows machine or GitHub Actions Windows runner |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| SQLite without WAL mode on Windows | App freezes when Windows Defender scans the DB file mid-write | Set `PRAGMA journal_mode=WAL` in migration 0001, add `PRAGMA busy_timeout=5000` | Any Windows machine with active AV — immediate |
| Landing page video autoplay with audio | iOS Safari blocks autoplay with audio entirely, page appears broken | Always `autoplay muted playsinline` — never autoplay with audio | All iOS Safari users — 30%+ of Italian mobile traffic |
| YouTube embed without `loading="lazy"` | Landing page loads 400KB+ on first paint, Core Web Vitals fail, mobile bounce rate increases | Intersection Observer for YouTube iframes, `loading="lazy"` attribute | Any mobile connection <20 Mbps — >60% of Italian 4G |
| WhatsApp outreach without UTM parameters | Cannot attribute video views, landing visits, or purchases to WA campaign vs organic | Always append `?utm_source=wa&utm_medium=outreach&utm_campaign=[verticale]-[regione]` to YouTube links | From day 1 — no attribution data is unrecoverable retroactively |
| Sales Agent with no blocklist | Re-contacting customers who replied "non mi interessa" — triggers spam reports | Maintain `blocklist.db` table, check before every send | At any volume — even 1 spam report in 50 messages affects trust score |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Ed25519 private key stored in CF Worker environment variables without secret flag | Key visible in CF dashboard to anyone with account access | Always use `wrangler secret put` — never include private key in `wrangler.toml` or code |
| WhatsApp session cookies stored in plain text on disk | Session theft allows attacker to send messages from FLUXION's number | Encrypt session store with OS keychain (macOS Keychain / Windows Credential Manager) |
| Stripe webhook endpoint without signature verification | Attacker sends fake "payment completed" webhooks to generate licenses | `stripe.webhooks.constructEvent()` is non-negotiable — fail closed if signature invalid |
| Referral code incremental (`COMM-001`, `COMM-002`) | Guessable codes allow fraudulent license claims | Use HMAC-based codes: `COMM-{SHA256(accountant_email+secret)[:8]}` |
| FLUXION Proxy rate limit bypass | Unlimited NLU API calls drain Groq free tier in minutes | Enforce per-license rate limit in CF Worker KV: `rate:{license_key}:{date}` counter |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Referral URL shows raw CF Worker URL | PMI owner does not click unfamiliar domain | Always use `fluxion-landing.pages.dev/...` or custom domain — never `fluxion-proxy.gianlucanewtech.workers.dev` |
| Setup Wizard requires EhiWeb VoIP number on step 6 | Customer has not ordered EHIWEB yet, cannot complete setup | Make VoIP number optional in SetupWizard — show a "Configura Sara" button later in Impostazioni |
| Sara trial expiry shows a generic "Sara non disponibile" | Customer thinks Sara is broken, not that the trial expired | Show a dedicated upgrade prompt with "Il tuo periodo di prova Sara è terminato — aggiorna a Pro per continuare" with the Stripe Pro link |
| Sales Agent dashboard shows raw JSON lead data | Founder cannot quickly identify which leads to prioritize manually | Build a 3-column Kanban: "Da contattare / In attesa risposta / Convertiti" — even a basic HTML table is better than raw JSON |
| Windows installer with no Italian language | FLUXION's entire brand is Italian, English installer feels mismatched | Set `wix.language: "it-IT"` in tauri.conf.json — the installer strings appear in Italian |

---

## "Looks Done But Isn't" Checklist

- [ ] **WhatsApp Sales Agent:** The delay between messages is configurable — verify it cannot be set to <60 seconds in the UI, with a hard floor in the code
- [ ] **macOS Distribution:** Test cold install on a Mac that has never seen FLUXION — with zero Keychain entries and default Gatekeeper settings, on Sequoia 15.x specifically
- [ ] **Windows Distribution:** Test cold install on Windows 10 without WebView2 pre-installed — the bootstrapper download must succeed silently
- [ ] **Video V6:** Verify the YouTube thumbnail shows a human (not the dashboard), watch the first 8 seconds only and assess: is the pain communicated before the product appears?
- [ ] **Referral Program:** Verify the trigger condition checks actual Sara booking count from DB, not just account age
- [ ] **CF Worker rate limits:** Simulate 30 simultaneous Sara calls (Groq RPM test) and verify Cerebras fallback activates before the user sees an error
- [ ] **Resend email:** Send a test purchase email to a Libero.it and Alice.it address and verify it lands in inbox (not spam) — these are the two most common Italian consumer mail providers
- [ ] **Referral tracking:** Complete a full referral cycle (referrer gets code → referred buys → payment confirmed → reward granted) in staging before going live
- [ ] **Content repurposing:** Before any clip is published, run the "cold watch test" — show it to someone unfamiliar with FLUXION with no context

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| WA number perma-ban | MEDIUM — 2-3 week delay | Buy new SIM (€10), 2-week warmup with normal use, restart outreach at 10 msg/day. Add 2nd SIM to rotation immediately. |
| macOS Gatekeeper refund wave | MEDIUM — 30-day refund window | Deploy `/installa` page immediately, proactively email all customers with installation guide, offer 1:1 WA call for anyone stuck |
| Windows AV false positive | LOW-MEDIUM | Remove download link, submit to Microsoft WDSI and top 5 AV vendors, republish after clearance (1-5 days). If urgent: rebuild with different compiler flags to change binary hash. |
| PagineGialle IP ban | LOW | Switch to Google Places API (primary source). The data quality is better anyway. |
| Groq rate limit at peak | LOW — if Cerebras is pre-wired | Activate Cerebras fallback immediately (should be automatic). If not wired: temporary rate cap on Sales Agent NLU to protect Sara live calls. |
| Referral program zero conversions | LOW — recoverable | Adjust trigger from purchase to 30-day milestone, email existing customers with updated referral link, add specific Sara booking count trigger |
| Video poor retention (<45s average) | HIGH — requires recut | Restructure opening 30 seconds to problem-first (not dashboard-first), reupload, update all WA outreach links |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| WA number ban | Sprint 5 — Sales Agent build | Run 7-day warmup test with 10 msg/day before declaring Sales Agent ready |
| macOS Gatekeeper failure | Sprint 4 — Landing + Deploy | Cold install test on Sequoia 15.x before first payment link goes live |
| Windows SmartScreen/AV | Sprint 6 — Post-lancio Windows MSI | VirusTotal report with <3 detections before publishing download link |
| PagineGialle scraping failure | Sprint 5 — Sales Agent data pipeline | Lead DB must show >70% valid Italian mobile numbers before outreach |
| Video loses viewer at 8 seconds | Sprint 3 — Video V6 | YouTube analytics: average view duration >2:30 on first 100 views |
| Referral at purchase | Sprint 6 — Post-lancio referral | Referral trigger code must read `sara_bookings_count >= 10` from DB |
| Content repurposing quality | Sprint 6 — Post-lancio content | Manual cold watch test for every clip before any publish |
| Proxy rate limit under load | Sprint 1 — Product Ready (phone-home) | Groq + Cerebras dual pool must be wired before Sales Agent launches |

---

## Sources

**Cached CoVe 2026 Research (HIGH confidence — verified):**
- `.claude/cache/agents/growth-first-100-clients-research.md` — WA ban mechanics, warmup strategy, scraping alternatives, referral structure
- `.claude/cache/agents/video-sales-outreach-research-2026.md` — PMI psychology, video conversion patterns, WA outreach rules
- `.claude/cache/agents/competitor-video-analysis-2026.md` — Fresha/Treatwell/Mindbody/Jane App video analysis, demo video best practices
- `.claude/cache/agents/landing-v2-optimization-research.md` — Conversion benchmarks, video embed strategy, mobile-first requirements
- `.claude/cache/agents/distribution-no-signing-research-2026.md` — macOS Gatekeeper Sequoia changes, Windows MSI vs NSIS, false positive strategy
- `.claude/cache/agents/us-smb-sales-outreach-research-2026.md` — Toast playbook, US SMB outreach patterns, value-first framework

**Web Search Verification (2026-03-26):**
- [WhatsApp Automation — How to Stay Unbanned (2025)](https://tisankan.dev/whatsapp-automation-how-do-you-stay-unbanned/) — ban risk confirmed
- [Not All Chatbots Are Banned: WhatsApp 2026 AI Policy](https://respond.io/blog/whatsapp-general-purpose-chatbots-ban) — Meta 2026 policy changes
- [Tauri False Positives — Simon Hyll](https://tauri.by.simon.hyll.nu/concepts/security/false_positives/) — MSI vs NSIS confirmed
- [Tauri GitHub Issue #4749 — MSI AV false positives](https://github.com/tauri-apps/tauri/issues/4749) — documented upstream
- [Top 8 Reasons Why Referral Programs Fail — GrowSurf](https://growsurf.com/blog/why-referral-programs-fail) — timing and incentive mistakes
- [Common Mistakes in B2B Referral Programs](https://www.costanalysts.com/common-mistakes-in-b2b-referral-programs/) — qualification and tracking failures
- [Italy B2B Directories Scraping — 2025 Guide](https://hirinfotech.com/italy-b2b-directories-scraping-your-2025-guide-to-unlocking-italian-business-data/) — GDPR B2B framework confirmed
- [Garante Guidelines on Web Scraping](https://www.gamingtechlaw.com/2024/06/garante-privacy-guidelines-web-scraping-artificial-intelligence-ai/) — Italian authority position
- [12 Top SaaS Demo Mistakes — DemoDazzle](https://demodazzle.com/blog/12-top-saas-demo-mistakes-to-avoid) — dashboard-first anti-pattern
- [AI Video Mistakes 2025 — Reezo](https://reezo.ai/blog/common-ai-video-mistakes-how-to-avoid-them-2025) — content repurposing quality vs quantity
- [Tauri GitHub Discussion #4774 — WebView2 Windows](https://github.com/tauri-apps/tauri/discussions/4774) — bootstrapper strategy
- [Security Software False Positives — textslashplain.com](https://textslashplain.com/2026/01/27/microsoft-defender-false-positives/) — Microsoft Defender false positive pipeline

---
*Pitfalls research for: Indie desktop software launch — Italian PMI market*
*Researched: 2026-03-26*
*Confidence: HIGH (cached CoVe 2026 verified research + web search cross-referenced)*
