# Italian Lead Generation Sources — Deep Research CoVe 2026

> **Date**: 2026-03-16
> **Purpose**: Find the BEST zero/low-cost sources of Italian PMI leads for FLUXION autonomous sales agent
> **Target verticals**: Saloni parrucchiere, centri estetici, palestre, cliniche mediche, officine auto, studi professionali
> **Relevant ATECO codes**: 96.02 (parrucchieri/estetisti), 93.13 (palestre), 86.x (ambulatori medici), 45.20 (officine), 69-74 (studi professionali)

---

## Table of Contents
1. [PagineGialle.it](#1-paginegialleeit)
2. [Registro Imprese / InfoCamere](#2-registro-imprese--infocamere)
3. [Atoka.io](#3-atokaio)
4. [Google Maps Places API](#4-google-maps-places-api)
5. [Facebook Pages Search](#5-facebook-pages-search)
6. [Instagram Location/Hashtag Search](#6-instagram-locationhashtag-search)
7. [LinkedIn Company Search](#7-linkedin-company-search)
8. [Yelp / TripAdvisor](#8-yelp--tripadvisor)
9. [Europages.it](#9-europagesit)
10. [Il Sole 24 Ore / PMI databases](#10-il-sole-24-ore--pmi-databases)
11. [ISTAT / Open Data Italia](#11-istat--open-data-italia)
12. [Comuni.it / Portali comunali](#12-comuniit--portali-comunali)
13. [Treatwell / Fresha / Booksy](#13-treatwell--fresha--booksy-listings)
14. [WhatsApp Business Directory](#14-whatsapp-business-directory)
15. [BONUS: OpenAPI.com (Imprese)](#15-bonus-openapicom-imprese)
16. [Legal Framework: Cold Email B2B Italy](#16-legal-framework-cold-email-b2b-italy)
17. [Strategy Summary & Recommended Stack](#17-strategy-summary--recommended-stack)

---

## 1. PagineGialle.it

**What it is**: Italy's equivalent of Yellow Pages. Owned by Italiaonline S.p.A. The largest Italian business directory.

**Data available**:
- Business name: YES
- Phone: YES (landline + mobile)
- Email: SOMETIMES (if listed)
- Address: YES (full address with CAP)
- Category: YES (own category system, maps to ATECO)
- Website: SOMETIMES
- Opening hours: SOMETIMES
- Reviews: YES (limited)

**Free tier / Cost**: Free to browse. No public API. No official data export.

**Legal status**:
- **Italian Garante ruling**: The Garante has specifically FINED (€60,000) a company for creating an online telephone directory by scraping publicly available data. Phone numbers in Italy are subject to special regulation — the Garante prohibits creating generic phone directories from scraped data.
- **robots.txt**: Likely blocks automated access (standard practice for directories).
- **ToS**: Almost certainly prohibits scraping/automated extraction.
- **GDPR**: Phone numbers = personal data under GDPR, even for businesses (especially mobile numbers).

**Data freshness**: 7/10 — Updated regularly by Italiaonline, but many listings are stale (businesses that closed or moved).

**Automation feasibility**: Technically possible with Octoparse/Scrapy templates, but LEGALLY VERY RISKY in Italy.

### VERDICT: **SKIP** (for automated scraping)
> Phone number scraping from directories is explicitly penalized by the Italian Garante. The risk/reward ratio is terrible. Use for MANUAL research only — e.g., verifying individual leads found elsewhere.

---

## 2. Registro Imprese / InfoCamere

**What it is**: The official Italian Business Registry managed by InfoCamere for all Camere di Commercio. EVERY Italian business is legally required to register here.

**Data available**:
- Business name (ragione sociale): YES
- Legal form (SRL, SAS, ditta individuale): YES
- VAT number (P.IVA): YES
- PEC (certified email): YES — legally mandatory for all businesses
- Registered address (sede legale): YES
- ATECO code: YES — **critical for targeting by vertical**
- Registration date: YES
- Status (active/inactive/liquidation): YES
- Revenue bracket: SOMETIMES (via bilanci deposited)
- Phone: NO (not part of registry data)
- Website: NO
- Email (non-PEC): NO

**Free tier / Cost**:
- **Telemaco API**: PAID. Requires registration + per-query fees. Pricing varies by data type (visure camerali ~€5-7 each).
- **Open Data portals**: FREE but LIMITED. Regional Chambers (e.g., opendata.marche.camcom.it) publish aggregate statistics, NOT individual company lists.
- **ISTAT ASIA register**: Statistical data only, no individual company records publicly available.
- **Movimprese (Unioncamere)**: Aggregate demographic data (new registrations, closures by province/sector). FREE. NOT individual records.
- **registroimprese.it API**: Official API exists at `accessoallebanchedati.registroimprese.it/abdo/api`. Requires contract with InfoCamere. NOT free.

**Legal status**: FULLY LEGAL. This is official public registry data. PEC addresses are public by law (DL 179/2012). However, mass extraction for commercial purposes may still require authorization.

**Data freshness**: 10/10 — Updated in real-time as businesses register/modify their records. Source of truth.

**Automation feasibility**: API exists but requires paid contract. Can be accessed via commercial resellers (see OpenAPI.com below).

### VERDICT: **USE** (via commercial API reseller — best ROI source)
> The GOLD STANDARD for Italian business data. PEC is legally mandatory and publicly accessible — this is your #1 outreach channel. Use OpenAPI.com or Atoka as a commercial API layer. Cost: ~€0.015-0.05 per company record via resellers.

---

## 3. Atoka.io (by SpazioDati / Cerved Group)

**What it is**: Italian business intelligence platform. Database of 6M+ Italian companies. Premium data enrichment (web presence, social, technographics).

**Data available**:
- Business name: YES
- VAT / P.IVA: YES
- PEC: YES
- Address (sede legale + operativa): YES
- ATECO code: YES
- Revenue: YES
- Employees: YES
- Website: YES (crawled from web)
- Social profiles: YES (Facebook, Instagram, LinkedIn)
- Phone: YES (from web + directories)
- Email: YES (from web crawling)
- Technographics: YES (what software they use!)

**Free tier / Cost**:
- **Free trial**: Available — email sales@atoka.io for test API token.
- **Paid**: Credit-based system. 1 credit = 1 company lookup. Pricing is custom/enterprise (reportedly €0.03-0.10 per credit depending on volume).
- **No permanently free tier**.

**Legal status**: FULLY LEGAL. Atoka is a Cerved Group company — they have legal agreements with InfoCamere and operate within Italian data protection law. Using their API = you inherit their legal compliance.

**Data freshness**: 9/10 — Daily updates from Registro Imprese + continuous web crawling.

**Automation feasibility**: 10/10 — Full REST API, well-documented at developers.atoka.io. Python connector: `pip install atokaconn`.

### VERDICT: **USE** (if budget allows — best enriched data source)
> Premium option. If you need enriched data (website, social, technographics), Atoka is unbeatable for Italian companies. Negotiate a startup/volume deal. The "technographics" data is GOLD — you can find businesses NOT using any booking software.

---

## 4. Google Maps Places API

**What it is**: Google's API for searching and getting details on local businesses.

**Data available**:
- Business name: YES
- Phone: YES
- Address: YES
- Category: YES (Google business types — "hair_care", "gym", "dentist", etc.)
- Website: YES
- Opening hours: YES
- Rating + reviews: YES
- Photos: YES
- Email: NO (not returned by API)

**Free tier / Cost** (post-March 2025 changes):
- **Nearby Search (Essentials)**: 10,000 free requests/month, then $5 per 1,000
- **Place Details (Basic)**: 10,000 free requests/month, then $5 per 1,000
- **Text Search (Essentials)**: 5,000 free requests/month, then $10 per 1,000
- NOTE: The old $200/month credit was REPLACED by per-SKU free tiers as of March 2025.

**Practical yield at free tier**:
- 10,000 Nearby Search requests with 20 results each = ~200,000 business listings
- Covering all Italian provinces (107) x 6 verticals = 642 searches minimum
- **FREE TIER IS SUFFICIENT** for initial lead database build

**Legal status**: FULLY LEGAL when using the official API. Google's ToS allow commercial use of API results. No GDPR issues with business listing data from Google.

**Data freshness**: 8/10 — Google Maps is well-maintained for Italy. Small towns may have gaps.

**Automation feasibility**: 10/10 — Official REST API, well-documented, Python client libraries available.

### VERDICT: **USE** (primary free source for phone + address + website)
> Your BEST free data source. 10K free searches/month covers ALL Italian provinces across all verticals. Combine with Registro Imprese PEC data for the complete picture. No email, but you get phone + website (which can be scraped for email).

---

## 5. Facebook Pages Search

**What it is**: Meta's directory of business pages on Facebook.

**Data available**:
- Business name: YES
- Category: YES (1,300+ categories including "Parrucchiere", "Palestra", etc.)
- Phone: SOMETIMES
- Address: YES (if local business)
- Email: SOMETIMES
- Website: SOMETIMES
- Followers/likes: YES
- Reviews/ratings: YES
- Opening hours: SOMETIMES

**Free tier / Cost**:
- **Pages Search API**: Requires Facebook app with `pages_read_engagement` permission. Available to verified business apps. FREE within rate limits.
- **Rate limits**: 200 calls/hour per user token.
- **NOTE**: The Facebook Pages Search API was partially deprecated. `search?type=page` endpoint may be restricted.

**Legal status**: Using the official Graph API = LEGAL. Scraping Facebook directly = violates ToS and is legally risky (Meta has sued scrapers). GDPR applies to personal data on pages.

**Data freshness**: 7/10 — Many Italian PMI have Facebook pages, but data quality varies. Many pages are poorly maintained.

**Automation feasibility**: 6/10 — API exists but requires app review, permissions are limited, and search capabilities are restricted compared to what they used to be.

### VERDICT: **MAYBE** (secondary enrichment source only)
> Useful for verifying leads found elsewhere and getting social proof (followers, reviews). NOT reliable as a primary source — too many gaps in business data, API restrictions increasing. Use for enrichment, not discovery.

---

## 6. Instagram Location/Hashtag Search

**What it is**: Finding businesses via Instagram business profiles, location tags, and hashtags.

**Data available**:
- Business name: YES (from profile)
- Category: YES (Instagram business categories)
- Phone: SOMETIMES (business profiles)
- Email: SOMETIMES (business profiles)
- Address: SOMETIMES (location tags)
- Website: YES (bio link)
- Follower count: YES

**Free tier / Cost**:
- **Instagram Graph API**: FREE but requires Business/Creator account + Facebook app. Limited to 200 calls/hour.
- **Basic Display API**: DISCONTINUED (December 2024).
- **Hashtag search**: Official API only allows searching hashtags you're mentioned in.
- **Scraping**: Technically possible but Instagram has aggressive anti-scraping (TLS fingerprinting, behavioral analysis).

**Relevant hashtags**: #saloneparrucchiere #parrucchiere[city] #centrobenessere #estetica[city] #palestraitaliana #studiomedico

**Legal status**: Official API = LEGAL. Scraping = VIOLATES ToS + GDPR risk. Instagram has sued scrapers.

**Data freshness**: 6/10 — Good for beauty/wellness (very Instagram-active), poor for medical/auto/professional.

**Automation feasibility**: 4/10 — Official API too limited for discovery. Scraping too risky and technically difficult.

### VERDICT: **SKIP** (for lead generation)
> Instagram is where beauty businesses MARKET, not where you FIND them efficiently. API too restricted for discovery. Better to find leads elsewhere and then look up their Instagram for enrichment. Use Google Maps / Registro Imprese as primary, then cross-reference.

---

## 7. LinkedIn Company Search

**What it is**: Professional network with company pages for businesses of all sizes.

**Data available**:
- Company name: YES
- Industry: YES
- Size (employees): YES
- Website: YES
- Location: YES
- Description: YES
- Email: NO (not via API)
- Phone: NO (not via API)

**Free tier / Cost**:
- **Official API**: Requires LinkedIn Partnership approval. 5% acceptance rate, 6-month wait. No free tier for company search.
- **Sales Navigator**: €79.99/month — allows searching by industry + location + company size.
- **Scraping**: Technically possible but LinkedIn actively fights it.

**Legal status**:
- **hiQ v. LinkedIn (2022)**: US court ruled scraping PUBLIC profiles doesn't violate CFAA.
- **EU/GDPR**: MORE RESTRICTIVE. Personal data on LinkedIn is protected regardless of public visibility. Scraping Italian LinkedIn profiles for commercial outreach = HIGH RISK of GDPR violation.
- **LinkedIn ToS**: Explicitly prohibits scraping. Can ban accounts and sue civilly.

**Data freshness**: 5/10 for Italian PMI — Most small salons/gyms/clinics do NOT have LinkedIn company pages. Better for professional services (studi legali, commercialisti).

**Automation feasibility**: 2/10 — No free API, scraping legally dangerous in EU, low coverage for target verticals.

### VERDICT: **SKIP**
> LinkedIn is irrelevant for 80% of FLUXION's target market. Parrucchieri and palestre are NOT on LinkedIn. The API is locked behind partnership gates. Scraping is legally toxic under GDPR. Complete waste of effort.

---

## 8. Yelp / TripAdvisor

### Yelp Italy
**Coverage**: MINIMAL. Yelp has almost zero presence in Italy. Italian consumers use Google Maps, TripAdvisor, or Treatwell — NOT Yelp.

**Yelp Fusion API**: Paid only (no more free tier). Starter plan: $7.99/1,000 API calls. Limited to 3 reviews per business.

### TripAdvisor Italy
**Coverage**: GOOD for restaurants and hotels, POOR for salons/gyms/clinics. TripAdvisor is NOT a directory for beauty/wellness/medical.

**API**: Content API requires partnership application. No public free API for business search.

**Data available**: Business name, address, phone, rating, reviews — but only for hospitality/tourism businesses.

### VERDICT: **SKIP** (both)
> Yelp is dead in Italy. TripAdvisor doesn't cover our verticals. Neither provides useful data for parrucchieri, palestre, cliniche, or officine.

---

## 9. Europages.it

**What it is**: European B2B directory. Pan-European business-to-business marketplace.

**Data available**:
- Business name: YES
- Address: YES
- Phone: SOMETIMES
- Email: SOMETIMES
- Website: YES
- Category: YES (own taxonomy)
- Description: YES

**Free tier / Cost**: Free to browse. No public API. Data extraction requires scraping or commercial data services.

**Legal status**: Scraping likely violates ToS. No API = no sanctioned automated access.

**Data freshness**: 5/10 — Many listings are outdated. Self-reported data. Primarily B2B manufacturers/suppliers, NOT consumer-facing PMI.

**Automation feasibility**: 3/10 — No API, scraping required, ToS violation risk.

### VERDICT: **SKIP**
> Europages is B2B industrial/manufacturing focused. Very few parrucchieri, palestre, or cliniche mediche list here. Wrong target audience entirely.

---

## 10. Il Sole 24 Ore / PMI databases

**What it is**: Italy's main financial newspaper. Publishes some business rankings and databases.

**Data available**: Revenue rankings, industry reports, some company profiles. NOT a business directory.

**Free tier**: Some articles free, most paywalled. No API for business search.

**Automation feasibility**: 1/10 — Not a data source, it's a newspaper.

### VERDICT: **SKIP**
> Not a lead source. Useful for market research articles, not for finding individual PMI.

---

## 11. ISTAT / Open Data Italia

**What it is**: Italian National Institute of Statistics + national open data portal (dati.gov.it).

**Data available**:
- Aggregate statistics by ATECO code, province, region: YES
- Number of active businesses per sector per territory: YES
- Individual company records: **NO**
- Contact data: **NO**

**Free tier / Cost**: 100% FREE. Creative Commons Attribution 3.0 license. Downloadable CSV.

**Key portals**:
- `imprese.istat.it` — Enterprise portal with demographic statistics
- `dati.istat.it` — Data warehouse with ATECO breakdown by territory
- `dati.gov.it` — National open data aggregator
- `Movimprese` (Unioncamere) — Business birth/death statistics

**Legal status**: FULLY LEGAL. Public data, open license.

**Data freshness**: 7/10 — Annual/quarterly updates. Not real-time.

**Automation feasibility**: 8/10 — CKAN API on dati.gov.it, CSV downloads available.

### VERDICT: **USE** (for market sizing and territory prioritization, NOT for individual leads)
> ESSENTIAL for strategic planning: "How many parrucchieri are in Milano vs Napoli?" "Which provinces have the most palestre?" Use this to prioritize which cities to target first with Google Maps / Registro Imprese searches. NOT a contact database.

---

## 12. Comuni.it / Portali comunali

**What it is**: Italian municipal websites and portals. Some municipalities maintain local business directories (albi, SUAP registrations).

**Data available**: Varies wildly. Some comuni publish SUAP (Sportello Unico Attivita Produttive) data with business registrations. Most don't.

**Free tier**: Free where available.

**Legal status**: Public administrative data = LEGAL.

**Data freshness**: 3/10 — Extremely inconsistent. Many portals are outdated or broken.

**Automation feasibility**: 1/10 — No standardized API. Every comune is different. Would require custom scrapers for each municipality.

### VERDICT: **SKIP**
> Too fragmented, too inconsistent. The data you'd find here is already in the Registro Imprese (which is centralized). Not worth the effort.

---

## 13. Treatwell / Fresha / Booksy Listings

**What it is**: Online booking platforms for beauty/wellness. Treatwell has 15,000+ salons in Italy. Fresha is growing fast. Booksy is smaller in Italy.

**Data available** (from public listings):
- Business name: YES
- Address: YES
- Phone: SOMETIMES
- Services offered: YES
- Pricing: YES
- Reviews: YES
- Opening hours: YES
- Email: NO (hidden behind platform)
- Website: SOMETIMES

**Free tier / Cost**: Public listings are browsable. No API for third parties.

**Legal status**:
- **Scraping**: VIOLATES ToS of all three platforms. All explicitly prohibit automated data extraction.
- **GDPR**: Business listings are borderline — business name + address is not personal data, but contact details of sole traders (ditte individuali) may be.
- **Competition law**: Using competitor's customer lists for poaching is legally aggressive but not per se illegal if done with public data.
- **Practical risk**: These companies have legal teams and WILL send cease-and-desist letters.

**Data freshness**: 9/10 — Actively maintained by businesses themselves.

**Automation feasibility**: 5/10 — Technically possible to scrape, but legally risky and platforms use anti-bot measures.

**Strategic value**: EXTREMELY HIGH. Every salon on Treatwell/Fresha = a business already using booking software = a business you can CONVERT to FLUXION (no SaaS fees, no commissions).

### VERDICT: **MAYBE** (manual research only, DO NOT scrape)
> The customer lists of Treatwell/Fresha/Booksy are GOLD for competitive targeting. But DO NOT scrape them. Instead: (1) Use Google Maps to find salons, (2) Cross-reference with Treatwell/Fresha to identify which ones use competitors, (3) Target those businesses specifically with your "zero commission" pitch. Manual research, not automated extraction.

---

## 14. WhatsApp Business Directory

**What it is**: WhatsApp's built-in business discovery feature. Businesses with WhatsApp Business accounts appear in search.

**Data available**:
- Business name: YES
- Category: YES
- Address: SOMETIMES
- Phone: YES (it's WhatsApp)
- Description: YES
- Catalog: SOMETIMES
- Website: SOMETIMES

**Free tier / Cost**: Free to search within WhatsApp app.

**Legal status**: No public API for directory search. WhatsApp does NOT allow automated extraction of directory data.

**Data freshness**: 7/10 — Businesses self-register, so data is current for those who maintain it.

**Automation feasibility**: 0/10 — No API. In-app only. Cannot be automated.

### VERDICT: **SKIP** (not actionable for lead gen)
> No API, no way to automate, no way to export. Useless for systematic lead generation. A business with WhatsApp Business = good sign they're digitally active, but you can't discover them this way at scale.

---

## 15. BONUS: OpenAPI.com (Imprese)

**What it is**: Commercial API reseller of Registro Imprese data. Italian company (OpenAPI S.p.A.). Over 15 API services for Italian company data.

**Data available**:
- Business name: YES
- P.IVA: YES
- PEC (certified email): YES — **30 free lookups/month for PEC!**
- Address (sede legale): YES
- ATECO code: YES
- Revenue bracket: YES
- Employees: YES
- Registration date: YES
- Status: YES
- SdI code: YES

**Pricing**:
- **Company Search (list by ATECO/province)**: From €0.015/request
- **PEC lookup**: 30 FREE/month, then €0.03/request
- **Company details**: From €0.015/request
- **"dry_run" mode**: FREE — returns only the COUNT of matching companies (use for market sizing!)
- **Rate limits**: 10,000 requests/minute

**Legal status**: 100% LEGAL. Licensed reseller of official Camera di Commercio data.

**Data freshness**: 10/10 — Real-time sync with Registro Imprese.

**Automation feasibility**: 10/10 — REST API, well-documented, production-ready.

**Key feature**: Search by ATECO + Province = exact targeting. Example: "All active parrucchieri (ATECO 96.02) in Provincia di Milano" = one API call.

### VERDICT: **USE** (primary paid source — extremely cheap)
> THIS IS YOUR #1 LEAD SOURCE. For ~€15-50 you can download EVERY active parrucchiere, palestra, clinica, officina in Italy with their legally-public PEC email. The PEC is the LEGAL outreach channel (see section 16).

---

## 16. Legal Framework: Cold Email B2B Italy

### The Rules

**Italian law on B2B marketing email**:

1. **General rule**: ALL promotional electronic communications (email, SMS, WhatsApp) require **prior opt-in consent** (Art. 130, Codice delle Comunicazioni Elettroniche + GDPR Art. 6).

2. **"Soft spam" exception** (Art. 130, comma 4): You can send promotional email WITHOUT consent ONLY if:
   - The recipient's email was collected during a PREVIOUS SALE
   - You're promoting SIMILAR products/services
   - Clear opt-out in every message
   - Proper privacy notice was given at collection time
   - **This does NOT apply to cold outreach — only to existing customers**

3. **B2B in Italy = same rules as B2C**: Unlike the UK or Germany, Italy does NOT have a general B2B exemption. The Garante treats B2B email marketing the same as B2C. Prior consent is the default requirement.

4. **PEC exception**: PEC (Posta Elettronica Certificata) is a LEGAL communication channel, not a marketing channel. However, PEC addresses are PUBLIC by law and can be used for **legitimate business communications** (not mass marketing).

5. **"Legitimate interest" (Art. 6(1)(f) GDPR)**: Can be argued for B2B cold email IF:
   - You can demonstrate a genuine business reason
   - The recipient would reasonably expect the contact
   - You process minimum necessary data
   - You have an easy opt-out mechanism
   - You've done a documented Legitimate Interest Assessment (LIA)
   - **In Italy, this is RISKIER than in other EU countries** — the Garante is strict

6. **Penalties**: Up to €20M or 4% of global annual revenue. Recent (Feb 2025) Garante sanctions: up to €300,000 for non-granular consents.

### PRACTICAL STRATEGY FOR FLUXION

**LEGAL approach to cold B2B outreach in Italy**:

#### Option A: PEC Outreach (RECOMMENDED)
- PEC addresses are PUBLIC DATA (mandatory for all businesses, published in Registro Imprese)
- Send a SINGLE introductory PEC presenting FLUXION as a business tool
- NOT mass marketing — targeted, personalized, 1-to-1 business communication
- Include clear opt-out and privacy notice
- Legal basis: legitimate interest (LIA documented) for B2B software relevant to their sector
- **Volume**: Keep it LOW (<50/day), PERSONALIZED (mention their business name, sector)
- **Risk level**: LOW if done properly. PEC is a business communication tool.

#### Option B: Website Contact Form
- Find business websites via Google Maps API
- Use their contact form to send a personalized message
- Legal: they published a contact form for receiving communications
- **Volume**: Manual or semi-automated, 20-30/day
- **Risk level**: VERY LOW

#### Option C: Phone Outreach
- Italy has the "Registro delle Opposizioni" (national do-not-call list)
- B2B calls to landlines listed in business directories: ALLOWED (if business number, not personal)
- B2B calls to mobile: MUST check Registro delle Opposizioni first
- **Risk level**: MEDIUM — requires checking the registry

#### Option D: Opt-In Funnel (GOLD STANDARD)
- Run targeted Facebook/Instagram ads to your verticals
- Landing page with lead magnet (e.g., "Guida gratuita: Come aumentare le prenotazioni del 40%")
- Collect EXPLICIT consent for email marketing
- Legal basis: consent (Art. 6(1)(a) GDPR)
- **Risk level**: ZERO — fully compliant
- **Cost**: Ad spend (€5-20/day) but highest quality leads

---

## 17. Strategy Summary & Recommended Stack

### Lead Source Verdict Table

| # | Source | Data Quality | Cost | Legal | Verdict |
|---|--------|-------------|------|-------|---------|
| 1 | PagineGialle.it | 7/10 | Free (scraping) | **ILLEGAL** to scrape phone data | **SKIP** |
| 2 | Registro Imprese / InfoCamere | 10/10 | Paid (API) | **100% LEGAL** | **USE** (via reseller) |
| 3 | Atoka.io | 9/10 | Paid (credits) | **100% LEGAL** | **USE** (if budget) |
| 4 | Google Maps Places API | 8/10 | FREE (10K/mo) | **100% LEGAL** | **USE** (primary free) |
| 5 | Facebook Pages Search | 6/10 | Free (API) | Legal (API only) | **MAYBE** (enrichment) |
| 6 | Instagram Hashtag/Location | 5/10 | Free (limited API) | Risky (scraping) | **SKIP** |
| 7 | LinkedIn Company Search | 3/10 | Paid ($80/mo+) | **RISKY** in EU | **SKIP** |
| 8 | Yelp / TripAdvisor | 2/10 | Paid | Legal (API) | **SKIP** (no Italy coverage) |
| 9 | Europages.it | 4/10 | Free (scraping) | ToS violation | **SKIP** |
| 10 | Il Sole 24 Ore | 1/10 | Paid | N/A | **SKIP** |
| 11 | ISTAT / Open Data | 8/10 (aggregate) | FREE | **100% LEGAL** | **USE** (market sizing) |
| 12 | Comuni.it | 2/10 | Free | Legal | **SKIP** (too fragmented) |
| 13 | Treatwell/Fresha/Booksy | 9/10 | Free (manual) | **RISKY** to scrape | **MAYBE** (manual only) |
| 14 | WhatsApp Business Dir | 5/10 | Free | No API | **SKIP** |
| 15 | OpenAPI.com (Imprese) | 10/10 | €0.015/req | **100% LEGAL** | **USE** (primary paid) |

### Recommended Lead Generation Stack (Zero to Low Cost)

#### Phase 1: Market Sizing (FREE)
1. **ISTAT dati.istat.it** — Download ATECO statistics by province
2. **OpenAPI.com dry_run** — Get exact counts per ATECO + province (FREE)
3. Prioritize top 20 provinces by business density for each vertical

#### Phase 2: Lead Database Build (€15-50 total)
1. **Google Maps Places API** (FREE) — 10K searches/month
   - Search each target province + vertical category
   - Get: name, address, phone, website, rating, reviews
2. **OpenAPI.com** (€0.015-0.03/company) — PEC + ATECO + P.IVA
   - Match Google Maps leads with official registry data
   - Get: PEC email, exact ATECO, VAT number, legal status
3. **Result**: Complete database of ~50,000-200,000 Italian PMI with name, address, phone, PEC, website, ATECO code

#### Phase 3: Enrichment (Optional, if budget)
1. **Atoka.io** — Add social profiles, technographics, revenue data
2. **Facebook Graph API** — Verify social presence, get follower counts
3. **Website scraping** (legal) — Extract non-PEC email from business websites' contact pages

#### Phase 4: Outreach (LEGAL)
1. **PEC outreach** — Personalized 1-to-1 introduction via PEC (legitimate interest basis, documented LIA)
2. **Opt-in funnel** — Facebook/Instagram ads → landing page → lead magnet → consent-based email list
3. **Website contact forms** — Semi-automated personalized outreach
4. **Phone** — Call business landlines from Google Maps data (check Registro Opposizioni for mobiles)

### Total Cost Estimate
| Component | Cost |
|-----------|------|
| Google Maps API | €0 (free tier) |
| ISTAT / Open Data | €0 |
| OpenAPI.com (50K companies) | €750-1,500 |
| OpenAPI.com (PEC only, 50K) | €1,500 |
| Facebook/Instagram ads (optional) | €150-600/month |
| **TOTAL (minimum viable)** | **€0 (Google Maps only)** |
| **TOTAL (recommended)** | **€750-2,000 one-time** |

### Key Insight
> **PEC is your secret weapon.** Every Italian business is LEGALLY REQUIRED to have a PEC, and it's PUBLICLY AVAILABLE in the Registro Imprese. This is a legitimate, legal, B2B communication channel unique to Italy. No other EU country has this. Use OpenAPI.com to get PEC addresses by ATECO code + province, then send personalized introductions. Combined with the FREE Google Maps data for phone/website/reviews, you have the most complete PMI database possible — 100% legally.

---

## Sources

### Web Scraping Legality in Italy
- [iubenda — Is web scraping legal?](https://www.iubenda.com/en/blog/is-web-scraping-legal-what-you-need-to-know-2/)
- [Italian Garante stops web scraping — Morri Rossetti](https://morrirossetti.it/en/insight/publications/the-italian-data-protection-authority-puts-a-stop-to-web-scraping.html)
- [Garante web scraping consultation — Lexology](https://www.lexology.com/library/detail.aspx?g=a052ff3f-f70a-4e1d-9c3c-747ee452aca3)
- [Dentons — To be scraped or not to be scraped](https://www.dentons.com/en/insights/articles/2024/june/18/to-be-scraped-or-not-to-be-scraped)

### Registro Imprese / InfoCamere
- [InfoCamere — Accesso alle Banche Dati](https://www.infocamere.it/accesso-alle-banche-dati)
- [Registro Imprese API](https://accessoallebanchedati.registroimprese.it/abdo/api)
- [OpenAPI.com — Italian Company Search](https://openapi.com/products/italian-company-search)
- [OpenAPI.com — PEC Lookup](https://openapi.com/products/italian-company-registered-email)

### Atoka.io
- [Atoka API Reference](https://developers.atoka.io/v2/companies.html)
- [Atoka Sales Evolution API](https://atoka.io/pages/en/atoka-api/)
- [Atoka Python Connector — GitHub](https://github.com/openpolis/atokaconn)

### Google Maps Places API
- [Places API Pricing (2026)](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing)
- [Google Maps Platform Pricing](https://mapsplatform.google.com/pricing/)

### GDPR / Cold Email Italy
- [GDPR Cold Email Compliance — iscoldemaillegal.com](https://iscoldemaillegal.com/blog/gdpr-cold-email-compliance/)
- [Cold Calling & Emailing Laws Europe 2026 — Dealfront](https://www.dealfront.com/blog/essential-guide-to-cold-calling-and-emailing/)
- [Soft Spam Italia — Osborne Clarke](https://www.osborneclarke.com/it/insights/soft-spam-italia-stiamo-correttamente-applicando-la-norma)
- [Garante — Linee guida spam](https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/2542348)
- [Consent vs Legitimate Interest B2B — Derrick App](https://derrick-app.com/en/consent-vs-legitimate-interest-b2b-2/)

### ISTAT / Open Data
- [ISTAT Portale Imprese](https://imprese.istat.it/)
- [dati.gov.it API](https://www.dati.gov.it/api)
- [Movimprese — Unioncamere](https://www.infocamere.it/registro-imprese-tutte)

### Treatwell
- [Treatwell Italia](https://www.treatwell.it/)
- [Treatwell for Business](https://www.treatwell.it/partners/)

