# Feature Research

**Domain:** Indie desktop software launch — marketing, sales automation, video production for Italian SMB management tool
**Researched:** 2026-03-26
**Confidence:** HIGH (verified against 9 prior research files + fresh web searches)

---

## Context: What Is Already Built

This milestone is NOT about building product features. The product is complete at v0.9.0. The milestone is about **launching the product commercially**. Features here are launch mechanics — what's needed to go from "product exists" to "product sells."

Existing validated features (already shipped, out of scope for this research):
- Full CRM, Calendar, Services, Operators, Cash Register, SDI invoicing
- Voice Agent Sara: 23-state FSM, 5-layer RAG, Edge-TTS
- 8 vertical client cards (all verticals)
- Loyalty/Points, Birthday WA, Packages/Bundles
- WhatsApp notifications (booking confirm, reminders)
- Ed25519 licensing + Stripe LIVE payment links
- macOS PKG installer (68MB)
- CF Worker proxy + Resend email post-purchase
- Landing live at fluxion-landing.pages.dev

---

## Feature Landscape

### Table Stakes (Buyers Expect These Before Purchasing)

Features whose absence causes buyers to distrust or skip the product entirely.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Video demo showing all app screens** | Buyers want to see the product before paying €497; no video = no trust | HIGH | V5 exists but missing Pacchetti/Fedeltà screens; V6 must be 4:30-5:00 min, PAS formula |
| **Professional screenshots of every page** | Landing page credibility; missing screens = product feels unfinished | MEDIUM | 21/23 captured; missing Pacchetti + Fedeltà; require iMac + realistic Italian data |
| **Clear pricing above the fold** | PMI diffida of hidden fees; immediate transparency on €497/€897 lifetime is mandatory | LOW | Already in landing; loss framing vs SaaS must be prominent ("€1.800 in 3 anni vs €497 una volta") |
| **30-day money-back guarantee visible at checkout** | Reduces purchase risk for €500 commitment; +17% conversion when above fold | LOW | Already stated; needs visual prominence |
| **Mobile-responsive landing page** | 95%+ of WA traffic opens on mobile; if landing breaks on phone, conversion dies | MEDIUM | Critical: 3 tap max from WA link to Stripe checkout |
| **E2E purchase flow verification** | Stripe → webhook → license → email → activation must work end-to-end | MEDIUM | Individual pieces live; full E2E test required |
| **Testimonials / social proof section** | 83% of buyers trust peer recommendations; PMI trusts "colleghi di settore" 10x more than brand | MEDIUM | If no real clients yet: use specific vertical scenarios + founder story |

### Differentiators (What Makes FLUXION's Launch Stand Out)

Features that make the launch memorable and create word-of-mouth.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **WhatsApp outreach automation (Sales Agent)** | Zero-cost lead generation at scale; WA response rates 8-25% vs email 2-5%; reaches PMI where they actually live | HIGH | Google Places API (free, 28.5K calls/mo) > PagineGialle scraping; max 20-30 msg/day; semi-automated (prepare + human review + send) |
| **Voice notes as WA outreach format** | 22-28% response rate vs text; feels personal; stands out from every other cold message | MEDIUM | Founder records 15-30s authentic voice note, tool sends to list; not generated audio |
| **Commercialisti as channel partner** | 1 commercialista serves 50+ PMI clients; referral €100 per client = highest-leverage sales channel | LOW | Simple affiliate link + CF Worker tracking; referral fee paid via bank transfer/PayPal; no platform needed |
| **Loss framing copy throughout funnel** | "Un gestionale in abbonamento: €1.800 in 3 anni. FLUXION: €497 una volta." 2.1x conversion lift per research | LOW | Already in V5 copy; must be in WA messages, landing, email, video |
| **Vertical-specific WA message templates** | Parrucchieri get parrucchieri problems; officine get officine problems; personalization beats generic 3-5x | MEDIUM | 5 templates (parrucchiere, officina, estetica, palestra, dentista); each references vertical pain point |
| **YouTube as video hosting (not self-hosted)** | Free CDN, SEO indexing, shareable link works inside WA (18-22% CTR from WA YouTube links); avoids landing page load time | LOW | Unlisted OK for outreach, public for organic; WA link must be YouTube not bit.ly |
| **Content repurposing pipeline** | 1 video V6 → 5 vertical clips (30s each) → blog post → LinkedIn → 3 months content calendar | MEDIUM | OpusClip or manual cut; blog via Cloudflare Pages; zero incremental cost |
| **Referral program (client → client)** | PMI titolari trust colleagues; "Marco della tua zona lo usa già" is highest-trust signal | MEDIUM | Simple: unique URL per client with ?ref=CLIENTCODE; CF Worker tracks; reward: €50 discount on next purchase for referrer (not cash) |

### Anti-Features (Seemingly Good Ideas That Create Problems)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **WhatsApp Business API for outreach** | Official, zero ban risk, high deliverability | Requires Meta business verification, minimum spend ~€80/mo for BSP access, weeks of approval time; kills €0 cost constraint | WA Web automation (Playwright) with strict rate limits: 20 msg/day, 2-5 min delay, human-review step |
| **Paid ads (Meta/Google) for launch** | Fast reach, measurable ROAS | Budget required upfront; for €497 product need €50-150 CAC which eats margin; no budget | Sales Agent WA (€0 CAC) + commercialisti channel (€100 fixed referral) |
| **Free trial / freemium tier** | Reduces purchase hesitation | Conflicts with zero-download-free constraint; attracts tire-kickers not buyers; complicates licensing | 30-day money-back guarantee covers risk removal without free access |
| **Referral platforms (Tapfiliate, ReferralCandy, PartnerStack)** | Professional affiliate tracking, dashboard | All have monthly fees (€49+/mo); zero-cost constraint violated; overkill for <100 clients | CF Worker custom tracking: ?ref=CODE in URL, KV stores referral, manual payout |
| **A/B testing platform (Optimizely, VWO)** | Optimize landing conversion | Monthly cost; not needed until traffic > 1000/day; adds page weight | Manual A/B: change one thing per week, track Stripe conversion rate |
| **Full CRM for sales tracking** | Track leads, pipeline, follow-ups | Another tool to maintain; adds complexity | Notion free or simple spreadsheet for <200 leads |
| **Automated video editing AI for content repurposing** | Save time on clips | Most tools cost €30-100/mo; output quality inconsistent | OpusClip free tier (75 min/mo) + manual trim for top clips |
| **Instagram/TikTok social campaign** | Reach younger audience | PMI decision makers are 35-55 years old; Instagram reaches employees not owners; TikTok zero B2B intent | WhatsApp outreach + YouTube + commercialisti = reaches actual buyers |
| **Multi-channel automated sequence (email + WA + LinkedIn)** | Maximize touchpoints | PMI italiane barely use LinkedIn; email for cold B2B Italy = 2% response; complexity without payoff | WA only for cold; email for post-video follow-up with link |
| **VSL (Video Sales Letter) full-page format** | Converts well for info products | Research 2026: "VSL morti" — PMI italiani skips long autoplay with no controls; feels manipulative | Video on YouTube with controls; landing shows screenshot gallery + benefits |

---

## Feature Dependencies

```
Screenshot Perfetti (all 23 pages)
    └──required by──> Video V6 (Pacchetti + Fedeltà scenes use these screenshots)
                          └──required by──> Landing Definitiva (video embed = landing centerpiece)
                                                └──required by──> Sales Agent WA (links to landing/YouTube)
                                                                      └──enhances──> Commercialisti Channel

Referral Program
    └──requires──> At least 5-10 paying clients (who can refer)
    └──required by──> Post-lancio growth phase

Content Repurposing
    └──requires──> Video V6 (source material)
    └──requires──> Landing definitiva live (blog links there)

WhatsApp Outreach Automation
    └──requires──> Video V6 on YouTube (link to include in messages)
    └──requires──> Landing definitiva mobile-optimized (destination after video)
    └──requires──> 5 vertical message templates (personalization)
    └──requires──> Google Places API key + scraping script

E2E Purchase Flow Verification
    └──requires──> Landing live (already done)
    └──requires──> Stripe webhooks live (already done)
    └──enhances──> Sales Agent WA (buying flow must work before driving traffic)
```

### Dependency Notes

- **Screenshots require iMac:** Rust build environment + CGEvent screenshot capture only on iMac at 192.168.1.2. Cannot shortcut.
- **Video V6 requires all screenshots:** Specifically Pacchetti + Fedeltà are the key missing screens. Sprint 2 (screenshots) must complete before Sprint 3 (video).
- **Sales Agent WA requires YouTube video:** The link in WA messages must be YouTube (not landing) because WA penalizes unknown domains; YouTube links get high CTR (18-22%).
- **Referral program conflicts with pre-launch:** Cannot launch referral until real clients exist. Zero clients = zero referrers. Defer to post-lancio phase.
- **Commercialisti channel is independent:** Can start in parallel with video/landing — just needs a landing page URL and a simple email to send. Does not need full landing optimization.

---

## MVP Definition

### Launch With (v1 — Sprint 1-4)

These must exist before any outreach begins. Sending traffic to an incomplete funnel wastes leads.

- [x] Screenshot perfetti: 21/23 done — complete Pacchetti + Fedeltà screens on iMac
- [ ] Video V6 (4:30-5:00 min) on YouTube — all features shown, PAS formula, loss framing copy
- [ ] Landing definitiva with video embed — mobile-optimized, 3-tap to checkout
- [ ] E2E purchase flow verified: Stripe → webhook → license email → activation → app unlock
- [ ] 5 WA message templates (1 per vertical: parrucchiere, officina, estetica, palestra, dentista)
- [ ] Google Places API lead scraping script (100 leads per vertical per city)
- [ ] Sales Agent WA: semi-automated (prepare list → founder approves → send, 20/day)

### Add After Validation (v1.x — Sprint 5: Post-lancio)

Add once first 10-20 clients are paying and funnel is proven.

- [ ] Content repurposing: Video V6 → 5 vertical clips (30s) for WA warm-up content — trigger: video done
- [ ] Commercialisti outreach email + unique ref link — trigger: landing live
- [ ] Referral program (?ref= tracking in CF Worker) — trigger: first 10 paying clients
- [ ] Windows MSI build — trigger: macOS sales confirmed; needed to unlock Windows-only businesses
- [ ] Blog/content on CF Pages (SEO long-tail: "gestionale parrucchieri Italia") — trigger: sales agent running

### Future Consideration (v2+)

Defer until product-market fit is established (50+ clients).

- [ ] Click-to-WhatsApp ads (CTWA) — paid acquisition; requires validation of LTV first
- [ ] Video testimonials from clients — requires real clients who love the product
- [ ] Reseller program (commercialista becomes reseller, not just referrer) — requires legal structure
- [ ] Windows code signing certificate — €299/year EV cert; defer until revenue justifies it

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Complete screenshots (Pacchetti + Fedeltà) | HIGH | LOW (iMac + CGEvent script) | P1 — blocker for video |
| Video V6 on YouTube | HIGH | HIGH (production time) | P1 — core launch asset |
| Mobile-optimized landing with video | HIGH | MEDIUM | P1 — converts WA traffic |
| E2E purchase flow verification | HIGH | LOW (testing only) | P1 — must work before traffic |
| WA message templates (5 verticals) | HIGH | LOW (copy only) | P1 — needed for outreach |
| Google Places scraping script | HIGH | MEDIUM (Python + API) | P1 — source of leads |
| Sales Agent WA (semi-automated) | HIGH | HIGH (scraping + automation) | P1 — primary acquisition channel |
| Content repurposing (30s clips) | MEDIUM | LOW (OpusClip) | P2 — amplifier |
| Commercialisti outreach | HIGH | LOW (email + ref link) | P2 — high ROI, low effort |
| Referral program tracking | MEDIUM | LOW (CF Worker KV) | P2 — needs clients first |
| Blog posts / SEO content | LOW | MEDIUM | P3 — long-term play |
| Windows MSI build | HIGH | HIGH (WiX, iMac) | P2 — unlocks 70% of market |
| Click-to-WhatsApp ads | MEDIUM | LOW (setup) + MEDIUM (budget) | P3 — after free channels proven |

---

## Competitor Feature Analysis

How competitors handle launch/marketing for SMB management software in Italy:

| Feature | Fresha | Treatwell | AgendaPro | FLUXION Approach |
|---------|--------|-----------|-----------|-----------------|
| Video demo | 60-90s landing video + YouTube tutorials; never shows real pricing | 60-90s marketplace-first; focus on "get new clients" | 3-5 min feature walkthrough; boring, no problem-first | 4:30-5:00 min PAS formula; problem → Sara solution → all features → transparent lifetime pricing |
| Pricing transparency | Hidden: free → 20% marketplace fees revealed later | Hidden: 35% commission on new clients, monthly fee | Shows $19/user/month upfront | Full transparency above fold: €497/€897, loss frame vs subscriptions, 30-day guarantee |
| Social proof | Generic "1M+ businesses" | "150K+ salons in Europe" | Minimal | Zero clients at launch → use vertical-specific scenario proof + founder story |
| Lead acquisition | Marketplace inbound (they bring clients to salons) | Marketplace inbound | Paid ads + SEO | WA outreach cold + commercialisti warm + referral |
| Onboarding | Freemium signup, zero friction | Freemium | 14-day trial | Pay first → email → download → wizard → activate; zero friction after payment |
| Differentiation message | "All-in-one free platform" (fee hidden) | "Get discovered by new clients" | "Multi-platform" | "Paghi una volta, usi per sempre. Zero commissioni. I dati sul tuo computer." |

**Key insight from competitor analysis:** Fresha and Treatwell win on "free to start" positioning but lose on hidden fees. FLUXION must aggressively occupy the "total transparency + lifetime ownership" position because it is factually true and competitors cannot match it without destroying their revenue model.

---

## WA Outreach — Specific Feature Breakdown

This is the most complex launch feature. Breaking down component requirements:

### Must Have (Sales Agent v1)

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Lead discovery | Find Italian PMI by vertical + city | Google Places API `nearbysearch` (free, 28.5K calls/mo); extract name, phone, address, category |
| Phone number normalization | Convert +39 XX formats to WA format | Python: strip spaces, add +39, validate 10-digit mobile |
| Message template engine | 5 vertical templates with variable substitution | Python string templates: {nome_attivita}, {citta}, {link_video} |
| Rate limiting | Max 20 msg/day, 2-5 min randomized delay | Python `time.sleep(random.uniform(120, 300))` between sends |
| Human review queue | Founder approves each message before send | Simple: CLI prompt "Send to [Nome] at [Citta]? [y/n/skip]" |
| WA Web automation | Open web.whatsapp.com, find contact, send | Playwright Python; QR code scan once, session persists |
| Ban detection | Stop if WA account shows warning | Screenshot comparison or DOM check for ban notice |
| Daily log | Track sent/replied/failed | Append-only JSON Lines file per day |

### Nice to Have (Sales Agent v1.5)

| Component | Purpose | Defer Until |
|-----------|---------|-------------|
| Reply detection | Detect when PMI replies to message | 50+ replies/day makes manual tracking hard |
| Follow-up sequence | Send follow-up after 48h no reply | Risk: double outreach increases ban chance; only after testing |
| CRM integration | Export leads + status to spreadsheet | After 100 leads processed |
| Voice note automation | Send pre-recorded voice note | After text message response rates measured |

### Do Not Build (Sales Agent anti-features)

| Component | Why Skip |
|-----------|---------|
| Fully automated send (zero human review) | Ban risk spikes dramatically; quality drops; one wrong message poisons entire vertical in a city |
| Email extraction + email outreach | Italy B2B email = 2% response; extra complexity; GDPR email requirements stricter than WA |
| LinkedIn automation | PMI titolari not on LinkedIn professionally; zero ROI |
| Multi-account rotation (many SIMs) | Complexity explosion; start with 1 account, scale only if needed |

---

## Referral Program — Simple vs Complex

**Recommendation: Build the simple version. Do not use a platform.**

### Simple Version (Build This)

```
Client buys FLUXION → receives email
Email includes: "Hai un salone vicino che potrebbe usare FLUXION?
Condividi questo link: fluxion-landing.pages.dev?ref=MARIO123
Per ogni cliente che acquista, ricevi €50 di sconto sul prossimo rinnovo."

CF Worker:
- ?ref=CLIENTCODE in URL → KV stores {ref: "MARIO123", timestamp}
- On Stripe purchase → webhook checks KV → logs referral
- Founder manually pays €50 discount or gift card on next interaction
```

**Cost:** €0 (CF KV + Worker already running)
**Complexity:** LOW — 1 day implementation
**Trigger:** Activate after first 10 paying clients

### Complex Version (Do NOT Build Yet)

Automated dashboard, affiliate links, multi-tier, automated payouts, Tapfiliate/PartnerStack integration. All cost €49-200/month and require 10x more implementation time. No data yet on whether referral will even work for FLUXION — validate the simple version first.

---

## Sources

- Existing FLUXION research files (272KB, 9 files):
  - `.claude/cache/agents/landing-v2-optimization-research.md` — conversion benchmarks, landing structure
  - `.claude/cache/agents/growth-first-100-clients-research.md` — WA outreach, scraping, 100-client timeline
  - `.claude/cache/agents/video-sales-outreach-research-2026.md` — PMI psychology, WA templates, funnel
  - `.claude/cache/agents/competitor-video-analysis-2026.md` — Fresha/Treatwell/Mindbody/AgendaPro analysis
  - `.claude/cache/agents/us-smb-sales-outreach-research-2026.md` — Toast playbook, channel patterns
  - `.claude/cache/agents/storyboard-v6-research.md` — V5 lessons, V6 requirements
- Web searches (2026-03-26):
  - [Wyzowl Video Marketing Statistics 2026](https://wyzowl.com/video-marketing-statistics/) — video conversion data
  - [B2B Landing Page Conversion Rates 2026](https://firstpagesage.com/seo-blog/b2b-landing-page-conversion-rates/) — 3.8% median SaaS
  - [WhatsApp Automation Stay Unbanned 2025](https://tisankan.dev/whatsapp-automation-how-do-you-stay-unbanned/) — ban risk mechanics
  - [Italian Garante web scraping guidelines 2024](https://www.gamingtechlaw.com/2024/06/garante-privacy-guidelines-web-scraping-artificial-intelligence-ai/) — legal landscape
  - [B2B Referral Program Software 2025](https://cello.so/7-best-b2b-referral-software-2025-guide/) — platform options

---

*Feature research for: FLUXION Lancio v1.0 — launch/marketing/sales features*
*Researched: 2026-03-26*
