# VoIP Solutions for Italian SMBs (PMI) — Deep Research 2026
**Date**: 2026-03-19 | **Scope**: Complete pricing analysis for FLUXION VoIP integration (Sara voice agent)

---

## Executive Summary

For a typical Italian salon/gym receiving 20-50 calls/day (~2 min average = 40-100 min/day = 1,200-3,000 min/month), the **total monthly VoIP cost ranges from €0 to €20/month** depending on architecture choice.

**RECOMMENDED**: Dual-track approach:
1. **Primary (cheapest)**: Italian SIP provider (EHIWEB/Messagenet) — €0-8/month
2. **Fallback (most flexible)**: Telnyx Call Control + WebSocket — €4-14/month

---

## 1. SIP Trunk Providers — Detailed Pricing

### 1.1 TELNYX (USA/Global — EU endpoints in Amsterdam/Frankfurt)

| Item | Cost (USD) | Cost (EUR approx) |
|------|------------|-------------------|
| Italy DID number (geographic) | ~$1.00-3.00/month | ~€0.90-2.70/month |
| Inbound calls (Italy) | ~$0.004-0.008/min | ~€0.004-0.007/min |
| Outbound to Italy landline | ~$0.007-0.015/min | ~€0.006-0.014/min |
| Outbound to Italy mobile | ~$0.010-0.020/min | ~€0.009-0.018/min |
| SIP trunk base fee | $0 (pay-per-use) | €0 |
| Setup fee | $0 | €0 |
| Minimum commitment | None | None |

**API**: Excellent — Call Control REST API, TeXML, Media Streaming (bidirectional WebSocket), WebRTC SDK
**WebSocket streaming**: Yes — mulaw 8kHz base64, L16 codec support, bidirectional
**Italian IVR**: Via TTS or custom audio
**SIP registration**: IP auth or credential auth

**Monthly estimate (PMI 2,000 min inbound)**:
- DID: ~$2.00
- 2,000 min × $0.006: ~$12.00
- **Total: ~$14/month (~€13)**

**Monthly estimate (PMI 1,200 min inbound)**:
- DID: ~$2.00
- 1,200 min × $0.006: ~$7.20
- **Total: ~$9.20/month (~€8.50)**

Sources:
- [Telnyx Voice API Pricing](https://telnyx.com/pricing/voice-api)
- [Telnyx Italy Phone Numbers](https://telnyx.com/phone-numbers/italy)
- [Telnyx Elastic SIP Pricing](https://telnyx.com/pricing/elastic-sip)
- [Telnyx Media Streaming WebSocket](https://developers.telnyx.com/docs/voice/programmable-voice/media-streaming)

---

### 1.2 TWILIO (USA/Global — EU endpoint in Frankfurt)

| Item | Cost (USD) | Cost (EUR approx) |
|------|------------|-------------------|
| Italy local number | ~$3.00-6.00/month | ~€2.70-5.50/month |
| Inbound calls (Italy) | ~$0.0085-0.010/min | ~€0.008-0.009/min |
| Outbound to Italy landline | ~$0.010-0.020/min | ~€0.009-0.018/min |
| Outbound to Italy mobile | ~$0.030-0.050/min | ~€0.027-0.045/min |
| Media Streams (WebSocket) | Included in call cost | Included |
| Setup fee | $0 | €0 |
| Minimum commitment | None | None |

**API**: Excellent — TwiML, Media Streams (bidirectional WebSocket), REST API, SIP Domains
**WebSocket streaming**: Yes — mulaw 8kHz base64, JSON messages
**Italian IVR**: `<Say language="it-IT">` with Amazon Polly voices

**Monthly estimate (PMI 2,000 min inbound)**:
- DID: ~$4.00
- 2,000 min × $0.0085: ~$17.00
- **Total: ~$21/month (~€19)**

**Monthly estimate (PMI 1,200 min inbound)**:
- DID: ~$4.00
- 1,200 min × $0.0085: ~$10.20
- **Total: ~$14.20/month (~€13)**

Sources:
- [Twilio Voice Pricing Italy](https://www.twilio.com/en-us/voice/pricing/it)
- [Twilio SIP Trunking Italy](https://www.twilio.com/en-us/sip-trunking/pricing/it)
- [Twilio Media Streams](https://www.twilio.com/docs/voice/media-streams)

---

### 1.3 VONAGE / NEXMO (Ericsson — EU presence)

| Item | Cost (USD) | Cost (EUR approx) |
|------|------------|-------------------|
| Italy local number | ~$2.00-4.00/month | ~€1.80-3.60/month |
| Inbound calls (Italy) | ~$0.0095/min | ~€0.009/min |
| Outbound to Italy landline | ~$0.010-0.020/min | ~€0.009-0.018/min |
| Setup fee | $0 | €0 |
| Minimum commitment | None | None |

**API**: Good — Voice API, SIP support, WebSocket limited
**Status 2026**: Post-Ericsson acquisition, focus shifted to enterprise. Less relevant for SMB.

**Monthly estimate (PMI 2,000 min inbound)**:
- DID: ~$3.00
- 2,000 min × $0.0095: ~$19.00
- **Total: ~$22/month (~€20)**

**NOT RECOMMENDED**: Higher cost than Telnyx, less flexible API, uncertain post-acquisition roadmap.

Sources:
- [Vonage Voice API Pricing](https://www.vonage.com/communications-apis/voice/pricing/)
- [Vonage Phone Numbers Pricing](https://www.vonage.com/communications-apis/phone-numbers/pricing/)

---

### 1.4 PLIVO (USA/Global)

| Item | Cost (USD) | Cost (EUR approx) |
|------|------------|-------------------|
| Italy DID number | ~$2.00-4.00/month | ~€1.80-3.60/month |
| Inbound calls | ~$0.0055-0.0085/min | ~€0.005-0.008/min |
| SIP trunk (Zentrunk) | Pay-per-use, no channel fee | €0 base |
| Setup fee | $0 | €0 |

**API**: Good — Voice API, SIP trunking (Zentrunk), REST
**WebSocket**: Limited compared to Telnyx/Twilio

**Monthly estimate (PMI 2,000 min inbound)**:
- DID: ~$3.00
- 2,000 min × $0.007: ~$14.00
- **Total: ~$17/month (~€15.50)**

Sources:
- [Plivo SIP Trunking Italy](https://www.plivo.com/sip-trunking/pricing/it/)
- [Plivo Pricing](https://www.plivo.com/pricing/)

---

### 1.5 SIGNALWIRE (USA — EU endpoint Frankfurt)

| Item | Cost (USD) | Cost (EUR approx) |
|------|------------|-------------------|
| Italy DID number | ~$1.50-3.00/month | ~€1.40-2.70/month |
| Inbound calls | ~$0.003-0.005/min | ~€0.003-0.005/min |
| Outbound to Italy | ~$0.008-0.012/min | ~€0.007-0.011/min |
| Setup fee | $0 | €0 |

**API**: Excellent — SWML (Twilio-compatible), AI Agent native, SIP, WebSocket
**Unique**: Founded by FreeSWITCH creators. Native AI Agent integration.

**Monthly estimate (PMI 2,000 min inbound)**:
- DID: ~$2.00
- 2,000 min × $0.004: ~$8.00
- **Total: ~$10/month (~€9)** — CHEAPEST cloud option

Sources:
- [SignalWire](https://signalwire.com)
- Previous CoVe research (f15-voip-telnyx-research.md)

---

## 2. Italian VoIP Providers

### 2.1 EHIWEB VivaVox (Italian — servers in Italy)

| Item | Cost (EUR, IVA incl.) |
|------|----------------------|
| **VivaVox Free** | €0/month — 1 number free, 100 min included |
| **VivaVox Zero** (a consumo) | €0 canone — fisso 1.39 cent/min, mobile 9.99 cent/min |
| **VivaVox Italia** (scatto) | €0 canone — 15 cent scatto alla risposta, poi tariffa base |
| **VivaVox Flat** | €7.95/month — illimitato fisso + mobile Italia |
| **VivaVox Flat Business** | ~€9.95/month — illimitato + funzionalità business |
| Additional geographic number | €2.00/month |
| Incoming calls (ricezione) | **GRATUITA** su VoIP number |
| Number portability | ~€30 una tantum |
| Setup fee | €0 |
| SIP protocol | Standard SIP (sip.ehiweb.it:5060) |
| Codecs | G.711 PCMA/PCMU, G.729A |

**API**: NONE — traditional SIP trunk provider, no REST API, no WebSocket streaming, no webhooks
**For FLUXION**: Client's existing EHIWEB number registers to `sip.ehiweb.it` via Python SIP client (`voip.py`)

**Monthly estimate (PMI — incoming calls only):**
- VivaVox Zero: €0 canone + incoming FREE = **€0/month** (!!!)
- VivaVox Flat (if also making outbound): **€7.95/month**

**Key advantage**: Incoming calls to VoIP numbers in Italy are FREE for the receiver. The caller pays their normal rate. This means Sara answering inbound calls costs the PMI €0 in per-minute fees.

Sources:
- [EHIWEB VivaVox Tariffe](https://www.ehiweb.it/voip/tariffe-voip/)
- [VivaVox Zero](https://www.ehiweb.it/voip/tariffa-vivavox-zero/)
- [VivaVox Flat](https://www.ehiweb.it/voip/tariffa-vivavox-flat/)

---

### 2.2 MESSAGENET (Italian — servers in Italy)

| Item | Cost (EUR, IVA incl.) |
|------|----------------------|
| First VoIP number | Free with account |
| Additional numbers | Small annual fee |
| Incoming calls | Free (included) |
| Outbound to Italy landline | Varies by plan |
| "Taglia Canone" plan | €96/year (€8/month) — includes 1000 min/month transfer to mobile |
| Transfer overflow | €0.0238/min |
| Number portability | €30 one-time |
| Geographic numbers | 232 Italian districts available |
| SIP protocol | Standard SIP |

**API**: NONE — traditional provider
**For FLUXION**: Similar to EHIWEB, SIP registration via `voip.py`

**Monthly estimate (PMI — incoming only):**
- Basic: **€0/month** (first number free, incoming free)
- With call transfer: ~€8/month

Sources:
- [Messagenet Tariffe](https://messagenet.com/tariffe/)
- [Messagenet VoIP](https://messagenet.com/voip/)
- [Messagenet Numerazioni](https://messagenet.com/voip/numerazioni-voip/)

---

### 2.3 OPENVOIP (Italian)

| Item | Cost (EUR + IVA) |
|------|-----------------|
| Geographic number | €3.00/month + IVA |
| Incoming calls | Included |
| Outbound (a consumo) | Per-second billing, no rounding |
| Outbound Flat | Available (custom quote) |
| Simultaneous channels | Up to 30 free per number |
| Setup fee | €0 |

**API**: Limited
**SIP**: Standard SIP protocol

Sources:
- [OpenVOIP Tariffe](https://www.openvoip.it/tariffe-telefoniche-voip.html)
- [OpenVOIP Numeri Geografici](https://www.openvoip.it/voip-numerazioni-geografiche.html)

---

### 2.4 VOIPVOICE (Italian)

| Item | Details |
|------|---------|
| Geographic number | Available on all Italian prefixes |
| Activation time | A few hours |
| Channels | Up to 30 simultaneous, free |
| GNR (number ranges) | 10/100/1000 DDI available |
| Protocol | Standard SIP |
| Flat plans | Available (custom quote) |

**For FLUXION**: Good option for PMIs wanting Italian-only provider with SIP support.

Sources:
- [VoIPVoice Numeri VoIP](https://www.voipvoice.it/numeri-voip/)

---

### 2.5 ULI (Italian)

| Item | Cost (EUR + IVA) |
|------|-----------------|
| Single geographic number | €3.00/month |
| Incoming calls | Included |

Sources:
- [ULI Numeri VoIP](https://uli.it/numeri-voip.html)

---

### 2.6 VIVAVOX.IT (EHIWEB brand)

| Item | Details |
|------|---------|
| First VoIP number | Free |
| Additional numbers | €2.00/month |
| Calls between VivaVox | Free |

Sources:
- [VivaVox](https://www.vivavox.it/telefonia-voip/numero-voip-gratis-e-servizi/)

---

## 3. Cloud Phone Systems (All-Inclusive Plans)

### 3.1 CLOUDTALK

| Plan | Monthly (annual billing) | Monthly (monthly billing) |
|------|-------------------------|--------------------------|
| Lite | €19/user/month | €27/user/month |
| Essential | €29/user/month | €39/user/month |
| Expert | €49/user/month | €69/user/month |

- Includes 1 local phone number per user
- 500 domestic outbound minutes/user/month (EU)
- Unlimited inbound calls
- Italy coverage: Yes
- API access: Essential plan and above
- IVR: Essential plan and above

**Monthly estimate (1 user, PMI):**
- **€19-29/month** (annual billing)

**NOT RECOMMENDED for FLUXION**: Overkill — we don't need a full call center. Too expensive for just answering calls with Sara.

Sources:
- [CloudTalk Pricing](https://www.cloudtalk.io/pricing/)

---

### 3.2 AIRCALL

| Plan | Monthly (annual billing) | Monthly (monthly billing) |
|------|-------------------------|--------------------------|
| Essentials | $30/user/month | $40/user/month |
| Professional | $50/user/month | $70/user/month |
| Custom | Custom pricing | Custom pricing |

- Minimum 3 seats required
- 1 phone number included, additional $6/number/month
- Italian language support: Yes

**Monthly estimate (3 seats minimum, PMI):**
- **$90+/month (~€82+)** — way too expensive

**NOT RECOMMENDED**: 3-seat minimum kills this for single-location SMBs.

Sources:
- [Aircall Pricing](https://aircall.io/pricing/)

---

### 3.3 3CX

| Plan | Annual Cost |
|------|-------------|
| SMB Free (up to 10 users) | Free (2-month trial, then free tier) |
| Basic Edition | < Pro pricing (new 2026) |
| Pro | From $350/year/system |

- SIP trunk required (separate cost)
- Self-hosted or cloud-hosted
- Italy: Supported via 3rd-party SIP trunks

**NOT RECOMMENDED for FLUXION**: FLUXION IS the PBX replacement. No need for 3CX middleware.

Sources:
- [3CX Pricing](https://www.3cx.com/ordering/pricing/)
- [3CX Pricing Changes 2026](https://www.3cx.com/blog/news/pricing-changes-2026/)

---

## 4. Call Forwarding from Existing Landline (Italian Telcos)

### Cost of Call Forwarding (Trasferimento di Chiamata)

| Telco | Activation | Monthly Fee | Per-Minute Cost |
|-------|-----------|-------------|-----------------|
| **TIM** | Free | €1.25/month | Normal call rate (~€0.05-0.06/min to landline) |
| **Vodafone** | Free | ~€1.00/month | Normal call rate |
| **WINDTRE** | Free | ~€1.00/month | Normal call rate |
| **Fastweb** | Free | ~€1.00/month | €0.062/min + €0.012 scatto (or ~€0.05/min) |

**Important note**: On FTTC/FTTH/ISDN lines, call forwarding is typically INCLUDED at no extra monthly cost.

**Architecture**: Existing landline → Call forwarding → VoIP number (EHIWEB/Messagenet) → Sara

**Monthly estimate (PMI, 2,000 min forwarded)**:
- TIM forwarding: ~€1.25/month + 2,000 × €0.05 = **~€101/month** (!!!)
- This is EXTREMELY expensive for high-volume forwarding

**VERDICT**: Call forwarding is a TERRIBLE option for 20-50 calls/day. The per-minute cost of forwarding makes it prohibitively expensive. Better to port the number to VoIP or get a new VoIP number.

Sources:
- [SOStariffe - Trasferimento Chiamata](https://www.sostariffe.it/internet-casa/guide/trasferimento-di-chiamata-fastweb-tim-vodafone-e-altri-provider-come-fare)
- [TIM Trasferimento](https://www.tim.it/assistenza/per-la-tua-linea/trasferimento-di-chiamata)
- [Taglialabolletta - Trasferimento](https://taglialabolletta.it/trasferimento-di-chiamata)

---

## 5. Alternative: WebRTC Widget (No Phone Number)

| Approach | Monthly Cost | Pros | Cons |
|----------|-------------|------|------|
| WebRTC widget on website | €0 | Zero cost, no phone number needed | Only works on website, not phone |
| Telnyx WebRTC SDK | Included in Telnyx plan | Browser-to-agent directly | Requires Telnyx account |
| Custom WebRTC (self-hosted) | €0 | Full control | Development effort |
| AnveVoice | Free plan available | Easy setup | Limited customization |

**For FLUXION**: WebRTC can be a FREE addon (widget on salon's website/booking page) that connects directly to Sara without any phone number. Good for v1.1 but does NOT replace phone answering capability.

Sources:
- [Telnyx WebRTC](https://telnyx.com/products/webrtc)
- [AnveVoice](https://anvevoice.app)

---

## 6. TOTAL COST OF OWNERSHIP — Comparison Table

### Scenario: Italian salon, 30 calls/day avg, 2 min avg = 1,800 min/month inbound

| Solution | Monthly Cost (EUR) | Setup Cost | API Quality | Complexity |
|----------|-------------------|------------|-------------|------------|
| **EHIWEB VivaVox Zero (SIP direct)** | **€0-2** | €0 | No API (SIP only) | Medium (NAT) |
| **EHIWEB VivaVox Flat** | **€7.95** | €0 | No API (SIP only) | Medium (NAT) |
| **Messagenet (SIP direct)** | **€0-8** | €0 | No API (SIP only) | Medium (NAT) |
| **OpenVOIP (SIP direct)** | **€3.66** | €0 | Limited | Medium (NAT) |
| **Telnyx (Call Control + WS)** | **€8-13** | €0 | Excellent | Low (no NAT) |
| **SignalWire (WebSocket)** | **€7-9** | €0 | Excellent | Low |
| **Plivo (SIP trunk)** | **€12-16** | €0 | Good | Low-Medium |
| **Twilio (Media Streams)** | **€13-19** | €0 | Excellent | Low (no NAT) |
| **Vonage** | **€15-20** | €0 | Good | Low-Medium |
| **CloudTalk** | **€19-29** | €0 | Good | Very Low |
| **Call forwarding (TIM)** | **€101+** | €0 | None | Very Low |
| **Aircall** | **€82+** | €0 | Good | Very Low |

---

## 7. Fixed Monthly Plans (Canone Fisso) — All-Inclusive Options

For PMI owners who want NO SURPRISES on their bill:

| Provider | Plan | Monthly (EUR) | What's Included |
|----------|------|--------------|-----------------|
| **EHIWEB VivaVox Flat** | Flat | **€7.95** | Unlimited Italy landline + mobile |
| **EHIWEB Business Flat** | Flat Business | **~€9.95** | Unlimited + business features |
| **Messagenet Taglia Canone** | Annual | **€8/month** | 1000 min/month transfer |
| **CloudTalk Lite** | Per-user | **€19/user** | Unlimited inbound + 500 min out |

**BEST VALUE**: EHIWEB VivaVox Flat at €7.95/month — unlimited calls, predictable bill, Italian provider, SIP compatible.

---

## 8. Recommended Architecture for FLUXION

### Option A: EHIWEB/Messagenet Direct SIP (CHEAPEST — €0-8/month)

```
Customer's phone calls → PMI landline (or VoIP number)
    │
    ├─ Option 1: PMI already has EHIWEB → incoming calls FREE
    │
    ├─ Option 2: New EHIWEB VivaVox Zero account → €0/month + incoming FREE
    │
    └─ Option 3: Number portability from TIM/Vodafone → EHIWEB (€30 once)
         │
         ↓
    EHIWEB SIP Trunk (sip.ehiweb.it:5060)
         │  SIP INVITE
         ↓
    voip.py on PMI's PC (Python SIP client, already implemented)
         │  G.711 PCMU/PCMA → PCM16 → upsample 8kHz→16kHz
         ↓
    Sara Voice Agent (127.0.0.1:3002)
         │  Process → LLM → TTS
         ↓
    Audio response → downsample → RTP → EHIWEB → Caller hears Sara
```

**Pros**:
- €0-8/month total cost
- Audio never leaves Italy (GDPR)
- No cloud dependency
- voip.py already implemented

**Cons**:
- Requires NAT/port forwarding on router (5060 UDP + RTP 10000-10100 UDP)
- No REST API — all SIP protocol
- More complex setup for non-technical PMI owners

---

### Option B: Telnyx Call Control + WebSocket (FLEXIBLE — €8-14/month)

```
Customer calls Italian number (Telnyx DID: +39 02 XXXX)
    │
    ↓
Telnyx Cloud (EU endpoint: Amsterdam/Frankfurt)
    │  HTTP POST webhook → PMI's Cloudflare Tunnel
    │  Event: call.initiated → Sara answers
    │  Event: call.answered → start_streaming
    ↓
WebSocket bidirectional audio stream
    │  wss://tunnel.pmi.com/sara/telnyx/stream
    │  mulaw 8kHz base64 ↔ Sara processes
    ↓
Sara Voice Agent (localhost)
    │  STT → LLM → TTS → audio back via WebSocket
    ↓
Telnyx sends audio back to caller via PSTN
```

**Pros**:
- No NAT/firewall issues (Telnyx connects outbound to your tunnel)
- Excellent API, WebSocket streaming, call control
- Easy setup: just API key + webhook URL
- Italian DID numbers available

**Cons**:
- €8-14/month cost
- Audio goes through US/EU cloud (latency +50-100ms)
- Dependency on Telnyx cloud availability

---

### Option C: HYBRID (RECOMMENDED for FLUXION Pro tier)

```
FLUXION Pro License:
├── Primary: Telnyx (new Italian DID number for the PMI)
│   └── WebSocket streaming → Sara → responds to callers
│
├── Alternative: BYOD SIP (customer's existing EHIWEB/Messagenet)
│   └── voip.py direct SIP registration → Sara
│
└── Future (v1.1): WebRTC widget on PMI's website
    └── Browser → Sara directly (zero phone cost)
```

**Setup Wizard flow**:
1. "Do you want Sara to answer your business phone?" → Yes
2. "Do you already have a VoIP provider?"
   - Yes → Enter SIP credentials (server, username, password) → voip.py connects
   - No → "We'll set up a new Italian phone number for you" → Telnyx auto-provisioning
3. Test call → Sara answers → Done

---

## 9. Cost Communication to PMI Owner

### What to tell the customer:

**For FLUXION Pro (€897 lifetime + VoIP):**

> "Sara risponde al telefono del tuo salone 24/7. Il costo della linea telefonica VoIP è di circa **€10-15 al mese** — come una normale linea telefonica business. Non è un costo FLUXION, è il costo della linea telefonica."
>
> "Se hai già un provider VoIP (EHIWEB, Messagenet, etc.), il costo aggiuntivo è **€0** — Sara usa la tua linea esistente."

### Pricing tiers for VoIP:

| Customer Situation | Monthly VoIP Cost | Who Pays |
|-------------------|-------------------|----------|
| Already has EHIWEB/VoIP | €0 | Already paying provider |
| New EHIWEB VivaVox Zero | €0 (incoming free) | EHIWEB |
| New EHIWEB VivaVox Flat | €7.95 | Customer pays EHIWEB |
| New Telnyx number (via FLUXION) | ~€10-14 | Customer pays Telnyx |
| Number portability to VoIP | €30 one-time + VoIP plan | Customer |

---

## 10. Provider Feature Matrix

| Feature | Telnyx | Twilio | EHIWEB | SignalWire | Messagenet |
|---------|--------|--------|--------|------------|------------|
| Italy DID numbers | Yes | Yes | Yes (native) | Yes | Yes (native) |
| Call Control API | Excellent | Excellent | None | Excellent | None |
| WebSocket streaming | Yes (bidirectional) | Yes (bidirectional) | No | Yes | No |
| SIP registration | Yes (IP + credential) | Yes (SIP Domains) | Yes (credential) | Yes | Yes |
| EU data center | Amsterdam, Frankfurt | Frankfurt | Italy | Frankfurt | Italy |
| GDPR (data in EU/IT) | Yes (EU region) | Yes (EU region) | Yes (Italy) | Yes (EU) | Yes (Italy) |
| Min commitment | None | None | None | None | None |
| Italian support | English only | English only | Italian | English only | Italian |
| Free tier/trial | $1 credit | $15.50 credit | 100 min free | $5 credit | Free number |
| Best for FLUXION | Cloud fallback | Alternative | Primary (existing) | Budget cloud | Primary (new) |

---

## 11. Key Decision: SIP Direct vs Cloud WebSocket

| Criterion | SIP Direct (EHIWEB) | Cloud WebSocket (Telnyx) |
|-----------|---------------------|--------------------------|
| Monthly cost | €0-8 | €8-14 |
| Setup complexity | High (NAT, port forward) | Low (just API key) |
| Latency | Lower (~20ms less) | Higher (+50-100ms cloud) |
| Reliability | Depends on customer's router | High (Telnyx SLA) |
| GDPR | Best (audio stays in Italy) | Good (EU endpoints) |
| Support burden | Higher (customer router config) | Lower (Telnyx handles telephony) |
| Already implemented | Yes (voip.py) | Partially (WebSocket code ready) |
| Customer UX | Complex setup | Simple setup |

**VERDICT**: For FLUXION Pro tier, offer BOTH:
1. **Default**: Telnyx (simple setup, reliable, €10-14/month)
2. **Advanced**: BYOD SIP for tech-savvy customers or those with existing VoIP (€0/month)

---

## 12. Comparison with Voice AI Competitors

| Platform | Architecture | Cost/min (total) | Italy Support | Data in EU |
|----------|-------------|-----------------|---------------|------------|
| Retell AI | Cloud SIP + CDN | €0.07-0.33/min | Limited | No (US) |
| Vapi | Cloud + custom LLM | €0.05-0.15/min | Limited | No (US) |
| Bland AI | Cloud outbound | €0.05-0.12/min | No | No (US) |
| Twilio + GPT-4o | Media Streams | ~€0.02 + LLM | Yes | Yes (EU) |
| **FLUXION + Sara** | **Local + SIP/WS** | **€0-0.007/min** | **Native Italian** | **Yes (Italy)** |

**FLUXION's competitive advantage**: 10-50x cheaper per minute than any cloud voice AI platform, with native Italian language support and GDPR-compliant local processing.

---

## 13. Action Items for Implementation

### Immediate (for FLUXION Pro launch):

1. **Telnyx account setup**: Create account, provision 1 Italian test DID, configure Call Control webhook
2. **WebSocket endpoint**: Add `/sara/telnyx/stream` to voice agent (code already drafted in f15-voip-telnyx-research.md)
3. **EHIWEB BYOD**: Wire `voip.py` into `main.py` with config from Setup Wizard
4. **Setup Wizard**: Add VoIP configuration step (Telnyx auto or BYOD SIP)
5. **Pricing page**: Communicate "€10-15/month linea telefonica" clearly

### Future (v1.1+):

6. **WebRTC widget**: Free browser-to-Sara calling on PMI website
7. **WhatsApp Cloud API**: Official WhatsApp voice (when available)
8. **Multi-number**: Support multiple DIDs for multi-location PMIs

---

*CoVe 2026 Deep Research — VoIP PMI Italia Pricing*
*File: `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/voip-pmi-italia-pricing-deep-research-2026.md`*
*Based on: web search 2026-03-19, f15-voip-telnyx-research.md (2026-03-12), f15-voip-architecture-agente-a.md, f15-ehiweb-termux-agente-b.md*
