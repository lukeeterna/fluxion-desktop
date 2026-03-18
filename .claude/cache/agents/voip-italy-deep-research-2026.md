# VoIP Solutions for FLUXION Sara — Deep Research CoVe 2026
**Date**: 2026-03-18 | **Scope**: Complete VoIP landscape for Italian SMB voice AI agent
**Triggered by**: Frustration with EHIWEB VivaVox — need to evaluate ALL alternatives

---

## Executive Summary

FLUXION needs an Italian phone number where Sara (voice AI agent) answers calls. The solution must work behind NAT on a customer's desktop PC, be near-zero-config, and cost-sustainable for a lifetime license model.

**Top 3 Recommendations:**
1. **Telnyx** (BEST OVERALL) — Cloud telephony API with Italian numbers, WebSocket media streaming, no NAT issues, ~€4/month
2. **Twilio** (MOST PROVEN) — Same pattern as Telnyx but ~40% more expensive, largest community
3. **EHIWEB Direct SIP** (CHEAPEST but HARDEST) — Zero recurring cost but requires NAT/port forwarding setup per customer

**Critical Insight**: EHIWEB is a traditional SIP trunk provider, NOT a cloud telephony API. It has no webhooks, no media streaming API, no Call Control. For programmatic voice AI integration, cloud telephony APIs (Telnyx/Twilio) are dramatically simpler and more reliable.

---

## 1. Complete Landscape: All Viable Options

### 1.1 Cloud Telephony APIs (Recommended Category)

These providers handle PSTN termination in the cloud and deliver audio to your application via WebSocket or webhook. **No NAT/port forwarding needed** — the cloud calls YOUR server, not the other way around.

#### A. Telnyx — RECOMMENDED PRIMARY

**What it is**: US-based cloud communications platform with European PoPs (Amsterdam, Frankfurt). Full-featured Voice API with Italian number support.

**Italian Numbers**:
- Geographic DIDs: +39 02 (Milano), +39 06 (Roma), +39 011 (Torino), +39 055 (Firenze), and most major cities
- Mobile numbers: +39 3xx available (limited stock)
- Toll-free: 800/803 numbers available
- Number porting: Supported for Italian numbers

**Pricing (2025-2026 estimates)**:
| Item | Cost |
|------|------|
| Italian DID (geographic) | $1.00–2.00/month |
| Italian DID (mobile) | $2.00–4.00/month |
| Inbound per minute | $0.004–0.008/min |
| Outbound to Italy landline | $0.008–0.015/min |
| Media Streaming (WebSocket) | Included in call cost |
| Setup fee | $0 |
| Monthly minimum | $0 (pay-as-you-go) |

**Monthly cost for typical PMI** (100 calls/month, avg 4 min = 400 min):
- DID: $1.50 + Inbound: $2.40 = **~$3.90/month (~€3.60)**

**Integration Pattern (WebSocket Media Streaming)**:
```
Customer calls +39 02 XXXX XXXX
    → Telnyx PSTN cloud (EU PoP)
    → HTTP webhook to FLUXION server: "call.initiated"
    → FLUXION responds: "answer + start streaming"
    → Telnyx opens WebSocket to FLUXION server
    → Audio flows bidirectionally via WebSocket (mulaw 8kHz)
    → Sara processes: STT → LLM → TTS → send audio back via WebSocket
    → Customer hears Sara respond
```

**Key Advantages**:
- **No NAT issues**: Telnyx makes outbound WebSocket/webhook to YOUR server
- **European PoP**: Amsterdam/Frankfurt = ~30-50ms latency to Italy
- **Call Control API**: Full programmatic control (answer, stream, transfer, hangup)
- **TeXML**: TwiML-compatible markup for simpler setups
- **IP Authentication**: Option for server-to-server without password management
- **SIP trunking also available**: Can be used as traditional SIP trunk if needed
- **GDPR**: EU data processing region available

**Key Disadvantages**:
- Recurring cost (~€4/month per customer)
- Dependency on Telnyx infrastructure
- Requires internet (no offline calls)

**Python Integration Complexity**: LOW — aiohttp WebSocket handler + webhook endpoint. Code already drafted in previous research (`f15-voip-telnyx-research.md`).

---

#### B. Twilio — MOST PROVEN / LARGEST ECOSYSTEM

**What it is**: The original cloud telephony API. Most documented, largest community, highest reliability guarantees.

**Italian Numbers**:
- Geographic DIDs: Wide coverage of Italian city codes
- Mobile: Available with restrictions
- Toll-free: 800 numbers available
- Number porting: Supported

**Pricing (2025-2026 estimates)**:
| Item | Cost |
|------|------|
| Italian DID (local) | $2.00–4.00/month |
| Inbound per minute | $0.005–0.010/min |
| Outbound to Italy landline | $0.010–0.020/min |
| Media Streams (WebSocket) | Included |
| Setup fee | $0 |

**Monthly cost for typical PMI** (400 min inbound):
- DID: $3.00 + Inbound: $3.40 = **~$6.40/month (~€5.90)**

**Integration Pattern (Media Streams)**:
```
TwiML response on call:
<Response>
  <Start>
    <Stream url="wss://your-tunnel.com/sara/stream" />
  </Start>
  <Pause length="3600"/>
</Response>
```

**Key Advantages**:
- Most battle-tested platform globally
- Enormous documentation and community
- SIP Domain feature: can receive SIP from external trunks
- Twilio Functions (serverless) for simple routing
- Excellent Italian number regulatory compliance

**Key Disadvantages**:
- **~40-60% more expensive than Telnyx** for same functionality
- Higher lock-in (Twilio-specific APIs)
- Media Streams format slightly more verbose than Telnyx

**Python Integration Complexity**: LOW — nearly identical to Telnyx pattern.

---

#### C. SignalWire — BEST VALUE CLOUD API

**What it is**: Founded by FreeSWITCH creators. Twilio-compatible API at lower prices.

**Italian Numbers**: Available (geographic DIDs)

**Pricing (2025-2026 estimates)**:
| Item | Cost |
|------|------|
| Italian DID | $1.50–3.00/month |
| Inbound per minute | $0.003–0.005/min |
| Outbound Italy | $0.008–0.012/min |
| Media Streaming | Included |

**Monthly cost for typical PMI** (400 min):
- **~$3.10/month (~€2.85)** — cheapest cloud option

**Key Advantages**:
- Twilio-compatible API (drop-in replacement for most features)
- FreeSWITCH pedigree = battle-tested telephony
- European endpoints (Frankfurt)
- SWML markup (TwiML equivalent)
- AI Gateway native integration
- 30-50% cheaper than Twilio

**Key Disadvantages**:
- Smaller community than Twilio/Telnyx
- Italian number availability may be more limited
- Less documentation for Italian-specific regulatory

**Python Integration Complexity**: LOW — same as Twilio/Telnyx pattern.

---

#### D. Vonage (ex-Nexmo)

**What it is**: Ericsson-owned cloud communications. Enterprise-focused.

**Italian Numbers**: Available but less reliable inventory than Twilio/Telnyx

**Pricing**: Competitive with Twilio but with complex pricing tiers.

**Verdict**: **NOT RECOMMENDED for FLUXION**. Post-Ericsson acquisition, developer experience degraded. Support less responsive. Telnyx and Twilio are superior.

---

#### E. Plivo

**What it is**: India-based cloud telephony, competitive pricing.

**Italian Numbers**: Limited availability. European coverage weaker than Twilio/Telnyx.

**Verdict**: **NOT RECOMMENDED**. Italian number availability unreliable.

---

### 1.2 Traditional SIP Trunk Providers (Italian)

These provide a phone number and SIP credentials. YOUR software registers as a SIP client and handles all call media directly. **Requires NAT/port forwarding** unless using SIP over WebSocket.

#### F. EHIWEB VivaVox — DETAILED ANALYSIS

**What EHIWEB VivaVox actually is**:
EHIWEB is an Italian ISP and VoIP provider (AS49709). VivaVox is their VoIP service for businesses and consumers. It provides:
- An Italian geographic phone number (DID)
- SIP trunk credentials to register with any SIP softphone/hardware phone
- Standard SIP RFC 3261 service

**What VivaVox is NOT**:
- ❌ NOT a cloud telephony API (no webhooks, no Call Control API, no media streaming)
- ❌ NOT a developer platform (no REST API, no SDK, no documentation for programmatic use)
- ❌ NOT designed for AI/voice bot integration
- ❌ Does NOT handle NAT traversal for you (you must configure your own network)
- ❌ Does NOT provide WebSocket media streaming
- ❌ Does NOT have STUN/TURN servers guaranteed to work with all scenarios

**SIP Credentials Structure**:
```
SIP Server:     sip.ehiweb.it (or voip.ehiweb.it)
SIP Port:       5060 (UDP) / 5061 (TLS)
SIP Realm:      ehiweb.it
Username:       <assigned_number> (e.g., 0250150001)
Password:       Set by customer in my.ehiweb.it panel
Codec:          G.711 A-law (PCMA), G.711 µ-law (PCMU), G.729A
```

**Pricing**:
| Item | Cost |
|------|------|
| VivaVox account + number | ~€2–5/month |
| Inbound calls | Often included (or ~€0.01/min) |
| Outbound to Italy | ~€0.01–0.03/min |

**Integration Requirements for Software SIP Client (like FLUXION voip.py)**:
1. **Port forwarding on customer's router**: UDP 5060 + RTP range (10000-20000) → customer's PC
2. **SIP ALG disabled** on customer's router (many routers corrupt SIP packets with ALG enabled)
3. **Static local IP** for the PC (DHCP reservation)
4. **STUN configuration** (stun.ehiweb.it:3478) for NAT traversal
5. **Keep-alive SIP OPTIONS** every 30s to maintain NAT pinhole

**Why EHIWEB is problematic for FLUXION's use case**:
1. **NAT/Firewall nightmare**: Every customer's router is different. Port forwarding setup is NOT zero-config. Many Italian PMI routers (TIM Hub, Vodafone Station, etc.) have notoriously bad SIP ALG implementations.
2. **No API**: You can't programmatically provision numbers, check status, or manage calls.
3. **Support**: EHIWEB support is for traditional VoIP phone users, not developers building AI voice bots.
4. **Reliability varies**: SIP registration can drop, and there's no automatic re-registration notification.
5. **Each customer needs their own EHIWEB account**: FLUXION can't provision numbers centrally.

**When EHIWEB DOES make sense**:
- Customer already has an EHIWEB number and wants Sara to answer it
- Customer's network admin can configure port forwarding
- Cost is critical (near-zero monthly)

---

#### G. Messagenet (messagenet.it)

**What it is**: Italian VoIP provider, similar to EHIWEB. SIP trunks + Italian DIDs.

**Pricing**: Comparable to EHIWEB (~€3-5/month)

**Same limitations as EHIWEB**: No API, no webhooks, requires NAT setup.

**Verdict**: Same category as EHIWEB, no advantage over it.

---

#### H. VoIP.ms (Canadian, Italian numbers available)

**What it is**: Developer-friendly VoIP provider with REST API and Italian number availability.

**Italian Numbers**: Geographic DIDs available (~$0.85/month — very cheap)

**Key Difference from EHIWEB**: VoIP.ms has a REST API for number management and call routing. Can configure "callback" URL for incoming calls.

**Pricing**:
| Item | Cost |
|------|------|
| Italian DID | ~$0.85/month |
| Inbound | ~$0.006–0.01/min |
| Outbound Italy | ~$0.01–0.02/min |

**Verdict**: Better than EHIWEB for developer use, but still SIP-based (NAT issues). Less reliable than Telnyx for Italian numbers.

---

#### I. OVHcloud Telecom

**What it is**: French cloud provider with VoIP services including Italian numbers.

**Italian Numbers**: Available (geographic)

**API**: Has a REST API for provisioning and call management

**Pricing**: Competitive (~€2-3/month per number)

**Verdict**: Interesting alternative but documentation is French-centric. API less mature than Telnyx/Twilio for media streaming.

---

### 1.3 Virtual PBX Solutions (Forward to Webhook/SIP)

#### J. 3CX (Free/Standard)

**What it is**: Software PBX that can forward calls to SIP endpoints.

**Pattern**: 3CX cloud → SIP forward to Sara's SIP bridge on iMac.

**Verdict**: Adds unnecessary complexity layer. FLUXION doesn't need a PBX.

---

#### K. FreePBX/Asterisk (Self-Hosted)

**What it is**: Open-source PBX software.

**Pattern**: Install on a VPS → connect SIP trunk (Telnyx/EHIWEB) → forward audio to Sara.

**Verdict**: Overkill for FLUXION. Same result achievable with direct Telnyx WebSocket.

---

### 1.4 WebRTC-Based Solutions

#### L. Daily.co / LiveKit / Jitsi

**What it is**: WebRTC platforms for browser/app-based voice/video.

**Pattern**: Customer calls a web link (not a phone number) → WebRTC to Sara.

**Verdict**: **NOT suitable** for FLUXION's use case. Customers need to call a regular phone number, not a web link. However, WebRTC could complement for in-app voice (already implemented in FLUXION's open-mic feature).

---

## 2. Provider Comparison Matrix

| Criteria | Telnyx | Twilio | SignalWire | EHIWEB | VoIP.ms | Vonage |
|----------|--------|--------|------------|--------|---------|--------|
| **Italian DIDs** | ✅ Wide | ✅ Wide | ✅ Good | ✅ Native | ⚠️ Limited | ⚠️ Limited |
| **Call Control API** | ✅ Excellent | ✅ Excellent | ✅ Good | ❌ None | ⚠️ Basic | ⚠️ Medium |
| **WebSocket Streaming** | ✅ Native | ✅ Media Streams | ✅ SWML | ❌ None | ❌ None | ❌ None |
| **Webhook on call** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Basic | ✅ Yes |
| **Works behind NAT** | ✅ Yes (cloud→you) | ✅ Yes | ✅ Yes | ❌ Requires port fwd | ❌ Requires port fwd | ✅ Yes |
| **Cost DID/month** | ~$1.50 | ~$3.00 | ~$2.00 | ~€3.00 | ~$0.85 | ~$3.00 |
| **Cost inbound/min** | ~$0.006 | ~$0.008 | ~$0.004 | ~€0.01* | ~$0.008 | ~$0.008 |
| **Total 400min/mo** | **~€3.60** | **~€5.90** | **~€2.85** | **~€0-4** | **~€4.00** | **~€5.50** |
| **EU Data Center** | ✅ AMS/FRA | ✅ FRA | ✅ FRA | ✅ Italy | ❌ Canada | ⚠️ UK |
| **Latency to Italy** | ~30-50ms | ~40-60ms | ~40-60ms | ~10ms (direct) | ~120ms | ~80ms |
| **Zero-config for PMI** | ✅ FLUXION manages | ✅ FLUXION manages | ✅ FLUXION manages | ❌ Customer router | ❌ Customer router | ✅ FLUXION manages |
| **Number porting** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Complex | ✅ Yes |
| **Developer Docs** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ (none) | ⭐⭐⭐ | ⭐⭐⭐ |
| **GDPR Compliance** | ✅ EU region | ✅ EU region | ✅ EU | ✅ Italy native | ⚠️ Canada | ⚠️ |
| **Lock-in** | Low | Medium | Low | Zero | Low | Medium |

*EHIWEB inbound often included in monthly plan

---

## 3. EHIWEB Specific Analysis (Answering User's Frustration)

### What went wrong with EHIWEB

**The core misunderstanding**: EHIWEB VivaVox was designed for connecting hardware SIP phones (Grandstream, Yealink) or softphones (Zoiper, Linphone) to make/receive calls. It was **never designed** for programmatic AI voice agent integration.

**Specific limitations that cause frustration**:

1. **No developer documentation**: EHIWEB provides setup guides for Zoiper, 3CX, Fritz!Box — not for Python SIP libraries.

2. **NAT/Firewall dependency**: When Sara runs on the customer's PC behind a home/office router:
   - The SIP REGISTER goes outbound (works through NAT)
   - But incoming SIP INVITE + RTP audio needs to reach the PC → requires port forwarding
   - Italian ISP routers (TIM Hub, Vodafone Station, FRITZ!Box) often have broken SIP ALG
   - **This is a customer-support nightmare for FLUXION**

3. **No callback/webhook mechanism**: When a call comes in, EHIWEB sends a SIP INVITE to your registered endpoint. If the registration expired, the call fails silently. There's no way to be notified of missed calls via API.

4. **Credential management per customer**: Each FLUXION customer needs their own EHIWEB account, manages their own SIP password in my.ehiweb.it, and FLUXION has no way to verify or test credentials remotely.

5. **RTP port range**: SIP uses UDP 5060 for signaling, but audio flows on random UDP ports (10000-20000). This means you need to forward a RANGE of ports, not just one.

### Is EHIWEB salvageable?

**Yes, but only as an optional "BYOD" (Bring Your Own Device/Number) option for technically savvy customers who already have EHIWEB and can configure their router.** It should NOT be the default or recommended path.

---

## 4. Recommended Architecture for FLUXION

### Architecture: FLUXION Cloud VoIP Proxy (Telnyx-backed)

```
┌─────────────────────────────────────────────────────────────────┐
│  ARCHITECTURE: FLUXION VoIP Proxy                               │
│  (Same pattern as FLUXION LLM Proxy — already decided in S84)  │
└─────────────────────────────────────────────────────────────────┘

CALLER (regular phone)
    │
    │ Calls +39 02 XXXX XXXX (Italian geographic number)
    │
    ▼
TELNYX CLOUD (EU PoP — Amsterdam/Frankfurt)
    │
    │ Webhook: POST https://voip-proxy.fluxion.workers.dev/call
    │
    ▼
FLUXION VoIP PROXY (Cloudflare Workers — same infra as LLM proxy)
    │
    │ Auth: Verify FLUXION license key → find customer's Sara endpoint
    │ Route: Start media streaming to customer's Cloudflare Tunnel
    │
    │ Telnyx Call Control: answer + start_streaming
    │ WebSocket: wss://[customer-tunnel].cfargotunnel.com/sara/voip/stream
    │
    ▼
CUSTOMER'S PC (behind NAT — NO port forwarding needed!)
    │
    │ Cloudflare Tunnel receives WebSocket (outbound connection from PC)
    │
    ▼
SARA VOICE AGENT (Python, port 3002, localhost)
    │ Decode mulaw 8kHz → PCM 16kHz
    │ STT (Groq Whisper) → LLM → TTS
    │ Encode response → mulaw 8kHz
    │
    ▼
WebSocket response → Cloudflare Tunnel → FLUXION Proxy → Telnyx → CALLER
```

### Why This Architecture Wins

1. **ZERO NAT issues**: Cloudflare Tunnel is an outbound connection from the customer's PC. No port forwarding, no SIP ALG, no STUN needed.

2. **ZERO customer configuration**: The phone number is provisioned by FLUXION when the customer activates their license. The customer sees "Your phone number is: +39 02 XXX XXXX" in the app.

3. **Mirrors existing LLM proxy pattern**: FLUXION already decided (S84) to run a proxy for LLM/NLU via Cloudflare Workers. The VoIP proxy uses the same infrastructure, same auth (Ed25519 license key), same pattern.

4. **Cost is manageable**: ~€4/month per customer. With 1,000 customers: ~€4,000/month. Revenue from 1,000 licenses (avg €700): €700,000. VoIP cost = 0.6% of revenue.

5. **Number porting**: If a customer already has an Italian number (EHIWEB, TIM, Vodafone), they can PORT it to Telnyx. FLUXION can facilitate this.

6. **Scalability**: Telnyx handles PSTN, FLUXION proxy handles routing, Sara runs locally. Each component scales independently.

### Cost Analysis

**Per customer monthly VoIP cost** (FLUXION absorbs this, included in license):
| Usage Level | Calls/month | Minutes | Telnyx Cost |
|-------------|-------------|---------|-------------|
| Light (salon) | 50 | 150 | ~€1.50 |
| Medium (clinic) | 150 | 500 | ~€4.50 |
| Heavy (busy clinic) | 300 | 1000 | ~€8.00 |

**Total infrastructure at scale**:
| Customers | Avg monthly VoIP | Total/month | % of license revenue |
|-----------|-----------------|-------------|---------------------|
| 100 | €4 | €400 | 0.08% of €70K |
| 500 | €4 | €2,000 | 0.29% of €350K |
| 1,000 | €4 | €4,000 | 0.57% of €700K |
| 5,000 | €4 | €20,000 | 0.57% of €3.5M |

**Verdict**: VoIP cost is negligible relative to lifetime license revenue. Easily sustainable.

### Optional: BYOD SIP (for power users)

In Settings > Advanced > VoIP, offer:
- "Use your own SIP provider" toggle
- Fields: SIP Server, Username, Password, Port
- This uses the existing `voip.py` direct SIP implementation
- **Clearly marked as advanced, unsupported, "at your own risk"**
- Covers EHIWEB users who insist on their existing number without porting

---

## 5. Top 3 Recommendations — Final Comparison

### RECOMMENDATION 1: Telnyx (PRIMARY — via FLUXION VoIP Proxy)

| Aspect | Detail |
|--------|--------|
| **Role** | Primary VoIP provider for all FLUXION customers |
| **Pattern** | Telnyx Call Control + Media Streaming via Cloudflare Workers proxy |
| **Italian numbers** | Geographic +39 0X, provisioned automatically per customer |
| **Cost per customer** | ~€3-5/month (absorbed by FLUXION, included in license) |
| **NAT/Firewall** | No issues — WebSocket via Cloudflare Tunnel |
| **Integration effort** | ~2-3 days: webhook handler + WebSocket audio bridge + Telnyx API calls |
| **Reliability** | High — Telnyx SLA 99.999%, EU PoP |
| **Customer UX** | Zero-config: "Your Sara phone number is +39 02 XXX XXXX" |
| **GDPR** | ✅ EU data processing, audio stays in EU |

**Pros**: Best balance of cost, reliability, developer experience, zero-config UX
**Cons**: Recurring cost (~€4/mo per customer), dependency on Telnyx

---

### RECOMMENDATION 2: Twilio (FALLBACK / ALTERNATIVE)

| Aspect | Detail |
|--------|--------|
| **Role** | Fallback if Telnyx has issues, or for specific Italian number needs |
| **Pattern** | Twilio Media Streams + TwiML (nearly identical to Telnyx pattern) |
| **Italian numbers** | Wide availability, excellent regulatory compliance |
| **Cost per customer** | ~€5-6/month |
| **Integration effort** | ~1-2 days (Twilio → Telnyx pattern is 90% identical) |

**Pros**: Most proven platform, largest community, best Italian regulatory
**Cons**: 40-60% more expensive than Telnyx, higher lock-in

---

### RECOMMENDATION 3: EHIWEB Direct SIP (BYOD OPTION ONLY)

| Aspect | Detail |
|--------|--------|
| **Role** | Optional "Bring Your Own Number" for tech-savvy customers |
| **Pattern** | Direct SIP registration via `voip.py` on customer's PC |
| **Italian numbers** | Customer's existing EHIWEB number |
| **Cost per customer** | ~€0-3/month (customer already pays EHIWEB) |
| **Integration effort** | Already 80% implemented in `voip.py` (5 gaps to close) |

**Pros**: Zero recurring cost for FLUXION, customer keeps their number
**Cons**: Requires customer to configure router (port forwarding, SIP ALG), support nightmare, not zero-config

---

## 6. Implementation Roadmap

### Phase 1 — Telnyx Integration (3-5 days)

1. **Create Telnyx account** + purchase test Italian DID (~$2)
2. **Set up Cloudflare Worker** for VoIP proxy:
   - `POST /call/webhook` — receives Telnyx call events
   - Looks up customer by DID number → finds their Cloudflare Tunnel URL
   - Answers call + starts media streaming to customer's tunnel
3. **Add WebSocket endpoint** to Sara Python server:
   - `wss://localhost:3002/sara/voip/stream`
   - Receives mulaw 8kHz audio → converts → processes → sends response
   - Code already drafted in `f15-voip-telnyx-research.md`
4. **Test end-to-end**: Phone call → Telnyx → Worker → Tunnel → Sara → response audible

### Phase 2 — Number Provisioning (2-3 days)

1. **Telnyx API integration** in FLUXION proxy:
   - On license activation: provision Italian DID via Telnyx API
   - Store mapping: license_key → DID number → tunnel URL
   - On license deactivation: release DID
2. **Setup Wizard update**:
   - After license verification, display: "Il tuo numero Sara: +39 02 XXX XXXX"
   - Optional: "Vuoi portare il tuo numero esistente?" → number porting flow

### Phase 3 — BYOD SIP (Optional, 1-2 days)

1. Close remaining 5 gaps in `voip.py` (see `f15-voip-codebase-gap.md`)
2. Add UI in Settings > Advanced > VoIP for custom SIP credentials
3. Clearly mark as "advanced, for users with their own SIP provider"

---

## 7. Technical Details: Telnyx WebSocket Audio Format

**Inbound audio from Telnyx**:
```json
{
  "event": "media",
  "sequence_number": "42",
  "media": {
    "track": "inbound",
    "chunk": "42",
    "timestamp": "12345",
    "payload": "<base64-encoded-mulaw-8kHz>"
  }
}
```

**Outbound audio to Telnyx**:
```json
{
  "event": "media",
  "media": {
    "payload": "<base64-encoded-mulaw-8kHz>"
  }
}
```

**Audio conversion pipeline**:
```
INBOUND:  base64 → mulaw 8kHz → PCM16 8kHz → PCM16 16kHz → Whisper STT
OUTBOUND: TTS PCM16 22050Hz → resample 8kHz → mulaw → base64 → WebSocket
```

Python stdlib `audioop` module handles all conversions (available on Python 3.9 iMac):
- `audioop.ulaw2lin()` — mulaw to PCM
- `audioop.lin2ulaw()` — PCM to mulaw
- `audioop.ratecv()` — sample rate conversion

---

## 8. Cost Sustainability Analysis

### FLUXION Business Model Impact

**Assumption**: Average license price €700 (weighted across Base/Pro/Clinic)

| Customers | License Revenue (one-time) | Monthly VoIP Cost | VoIP as % of first-year revenue |
|-----------|---------------------------|--------------------|---------------------------------|
| 100 | €70,000 | €400/mo = €4,800/yr | 6.9% |
| 500 | €350,000 | €2,000/mo = €24,000/yr | 6.9% |
| 1,000 | €700,000 | €4,000/mo = €48,000/yr | 6.9% |
| 5,000 | €3,500,000 | €20,000/mo = €240,000/yr | 6.9% |

**Note**: This is per-year cost against one-time revenue. After year 1, the VoIP cost continues but revenue from those customers is zero (lifetime license). This means:
- **Year 1**: VoIP is 6.9% of revenue — easily sustainable
- **Year 2+**: VoIP becomes an ongoing cost. Need continued new sales to cover existing customer VoIP
- **At steady state** (e.g., 1000 customers, 200 new/year): €48K VoIP cost vs €140K new revenue = 34% — still viable but not trivial

**Mitigation strategies**:
1. **Fair use policy**: Include 200 min/month in license, charge €5/month for heavy users
2. **VoIP optional add-on**: Base license = no phone, Pro/Clinic = phone included
3. **Yearly VoIP subscription**: €49/year for phone service (optional)
4. **Cost optimization**: Telnyx volume discounts kick in at scale

**Recommended approach**: Include VoIP in Pro (€897) and Clinic (€1,497) licenses only. Base (€497) gets WhatsApp + in-app voice but no phone number. This aligns with the natural market: salons that need a phone AI agent are already spending €897+.

---

## 9. Regulatory Considerations for Italian Numbers

### AGCOM Requirements

Italian phone numbers are regulated by AGCOM (Autorità per le Garanzie nelle Comunicazioni). Key requirements:
- **Geographic numbers** (+39 0X): Assigned to a specific geographic area. The customer must have a presence in that area.
- **Nomadic VoIP numbers** (+39 0X with nomadic flag): Can be used anywhere but must declare "nomadic" usage.
- **CLI presentation**: The number shown to the called party must be a valid, assigned number.
- **Emergency services (112)**: VoIP numbers must be registered with a physical address for emergency service routing.

### Telnyx and Italian Regulations

Telnyx handles Italian regulatory compliance for their numbers:
- Address verification required when purchasing Italian DIDs
- Emergency address registration included
- CLI is automatically the purchased DID
- Compliant with AGCOM requirements

### FLUXION's Responsibility

When provisioning numbers via Telnyx API:
- Collect customer's business address during setup
- Submit address verification to Telnyx
- Store emergency address association
- This can be integrated into the Setup Wizard

---

## 10. Latency Analysis: Cloud VoIP vs Direct SIP

### Telnyx Cloud Path
```
Caller → PSTN → Telnyx EU PoP: ~50ms
Telnyx → WebSocket to CF Tunnel: ~30ms
CF Tunnel → Customer PC Sara: ~10ms
Sara processing (STT+LLM+TTS): ~600-800ms
Return path: ~90ms
TOTAL: ~780-980ms
```

### EHIWEB Direct SIP Path
```
Caller → PSTN → EHIWEB → SIP to PC: ~30ms
SIP/RTP processing: ~5ms
Sara processing (STT+LLM+TTS): ~600-800ms
Return RTP path: ~35ms
TOTAL: ~670-870ms
```

**Difference**: ~100ms additional latency for cloud path. This is within acceptable range — Sara's internal processing (600-800ms) dominates total latency. The 100ms cloud hop is imperceptible to humans.

---

## 11. Migration Path from EHIWEB

For the user who already has EHIWEB credentials:

### Option A: Port number to Telnyx
1. Request number porting from EHIWEB to Telnyx
2. Telnyx handles the porting process (2-4 weeks in Italy)
3. Once ported, number works with FLUXION VoIP proxy automatically
4. Customer keeps their existing phone number

### Option B: New Telnyx number + call forwarding
1. Purchase new Italian DID from Telnyx
2. Set up EHIWEB to forward calls to the new number (EHIWEB supports call forwarding)
3. Eventually port or discontinue EHIWEB

### Option C: Keep EHIWEB as BYOD
1. Use `voip.py` direct SIP integration
2. Requires customer to handle NAT/port forwarding
3. FLUXION provides "advanced setup" guide

---

## Appendix: Previous Research Files

This document supersedes and consolidates:
- `f15-voip-architecture-agente-a.md` (2026-03-12) — Android SIP bridge research
- `f15-voip-telnyx-research.md` (2026-03-12) — Provider comparison + code
- `f15-ehiweb-termux-agente-b.md` (2026-03-12) — EHIWEB + Termux analysis
- `f15-voip-codebase-gap.md` (2026-03-12) — Codebase gap analysis

---

*CoVe 2026 Deep Research completed — 2026-03-18*
*Note: Web pricing data based on knowledge cutoff (early 2025) and previous research. Verify current pricing at telnyx.com, twilio.com before purchasing.*
