# VoIP & Virtual Phone Number Market Research -- Italy 2026

## 1. ITALIAN VoIP PROVIDERS

### EHIWEB VivaVox
- SIP Server: `sip.vivavox.it` (UDP 5060, codec G729.A)
- FLUXION already has an account: numero 0972536918 attivo
- **VivaVox Flat (Consumer)**: **7,95 EUR/mese** (promo, price locked 6 months) -- unlimited calls to landlines+mobiles up to 1,000 min/month, excess at 0,15 EUR/call
- **VivaVox Flat Business**: unlimited calls, price locked permanently from activation
- Activation: free. Number portability: free (authorized AGCOM operator)
- **No programmable API** -- standard SIP registration only. Works with Zoiper, Linphone, PJSIP but no REST API, no webhooks, no programmable IVR.

### VoIPVoice.it
- Italy's first 100% business-oriented VoIP provider (since 2006), ~6,000 customers, 550+ resellers
- Sold through resellers/system integrators only (not direct to SMEs)
- **FLAT 1**: 17,90 EUR/mese (1 channel) | **FLAT 2**: 35,80 EUR/mese (2 channels)
- Certified with 3CX, Yeastar
- No programmable API

### Messagenet
- Italian VoIP operator authorized AGCOM (since 2004)
- **SmartNumber Pro**: business line with unlimited traffic, any of 232 Italian area codes
- **Lyber (virtual PBX)**: **12,00 EUR/mese** +IVA (first extension), **6,00 EUR/mese** +IVA per additional extension
- Number portability: free
- No programmable API

### OpenVOIP
- **Geographic number**: **3,00 EUR/mese** +IVA (any Italian prefix). Activation: free, no contract
- **Virtual PBX FULL**: **11,00 EUR/mese** (4 concurrent calls, 15 extensions)
- **Flat plans (outbound traffic)**:
  - MINI: 9,90 EUR/mese (300 min landlines + 150 min mobiles)
  - SMALL: 19,90 EUR/mese (600 + 300)
  - NORMAL: 39,90 EUR/mese (1,200 + 600)
  - BIG: 69,90 EUR/mese (2,400 + 1,200)
- **All inbound calls: FREE**
- No programmable API

### Clouditalia (now Retelit)
- Historic Italian telco (Arezzo), 14,000 km own fiber
- SIP Trunking + cloud PBX, sold through partners. Pricing not published.
- Not suitable for individual SMEs

### Fastweb Business VoIP
- **NeXXt Communication**: cloud PBX included FREE with any business fiber plan
- **Evolution**: free virtual PBX, 2-8 VoIP lines, unlimited calls Italy
- **Unlimited Business**: **65 EUR/mese** (fiber + PBX + VoIP flat)
- Tied to Fastweb connectivity. No programmable API.

### TIM Business VoIP
- **TIM ComUnica Entry**: **19,90 EUR/mese** (first 12 months, then 24,90), activation 96 EUR (4 EUR/mo x 24), 2-4 VoIP lines
- **TIM ComUnica**: **34,90 EUR/mese** (with direct debit), activation 120 EUR
- 24-month contract. No programmable API.

### Iliad Business
- **No VoIP/fixed line offering** as of March 2026. Mobile only. Not relevant.

---

## 2. INTERNATIONAL PROVIDERS WITH ITALIAN NUMBERS

### Telnyx (RECOMMENDED for FLUXION Pro)
- Full-stack telecom, own global IP backbone, licensed in 30+ countries
- **Italian DID number**: from **~$1/month** (~0,92 EUR)
- **Voice API rates** (general, estimated for Italy):
  - Inbound: ~$0.0055/min (~0,005 EUR)
  - Outbound: ~$0.007/min (~0,0065 EUR)
  - SIP Outbound: ~$0.005/min (~0,0046 EUR)
- **SIP Trunking**: first 10 channels $12/mo, 11-50: $11/mo, 51-250: $9/mo
- Full REST API, webhooks, WebSocket real-time, SIP registration
- Italy regulatory: identity + address proof (< 3 months), Requirement Groups mandatory since Sept 2024
- Number porting supported
- **Customers switching from Twilio save 30-70%**

### Twilio
- CPaaS leader, third-party carrier network (marks up carrier rates)
- **Italian local number**: estimated **$3-6/month** (international numbers range $1-10)
- **Voice rates** (estimated for Italy):
  - Inbound: ~$0.0085/min
  - Outbound to landlines: ~$0.013-0.03/min
  - Outbound to mobiles: ~$0.03-0.06/min
- Full REST API, TwiML, webhooks, SDKs in every language
- Italy regulatory: identity + address proof required. AGCOM blocks international-routed calls with Italian CLI since Nov 19, 2025.
- **30-70% more expensive than Telnyx**

### Vonage (Ericsson)
- Voice API with per-second billing (not per-minute)
- Italian numbers available (+39)
- Pricing: opaque, contact sales required

---

## 3. COST COMPARISON TABLE (typical SME scenario)

Scenario: 1 Italian number, ~500 min/month inbound, ~100 min/month outbound

| Provider | Number/mo | Inbound | Outbound | **Total/mo** | Programmable API? |
|----------|----------|---------|----------|-------------|-------------------|
| **Telnyx** | ~1 EUR | ~2,50 EUR | ~0,65 EUR | **~4-5 EUR** | YES |
| **Twilio** | ~3-6 EUR | ~4,25 EUR | ~3-6 EUR | **~10-18 EUR** | YES |
| **EHIWEB Flat** | 7,95 EUR | included | included | **~8 EUR** | NO |
| **OpenVOIP MINI** | 3+9,90 EUR | free | 300+150 min | **~13 EUR** | NO |
| **Messagenet Lyber** | 12 EUR | included? | metered | **~15-20 EUR** | NO |
| **TIM ComUnica** | 19,90-34,90 | included | included | **~20-35 EUR** | NO |
| **Fastweb** | 65 EUR | included | included | **~65 EUR** | NO |

---

## 4. CALL FORWARDING COSTS (Italian Telcos)

| Operator | Activation | Monthly fee | Per-call cost |
|----------|-----------|-------------|---------------|
| **TIM (fiber)** | Free | Free | As normal outbound call (free if flat plan) |
| **TIM (ADSL)** | Free | 1,25 EUR/mo | As normal outbound call |
| **Vodafone** | Free | Free | As normal outbound call |
| **WINDTRE** | Free | Free | As normal outbound call |

Activation code (universal): `*21*destination_number#`

---

## 5. REGULATORY REQUIREMENTS

- SME does NOT need AGCOM authorization (is customer of authorized operator)
- AGCOM Nov 2025: blocks internationally-routed calls with Italian CLI
- Number portability: guaranteed by law, free, 5-10 business days
- Documents for Italian DID: ID + proof of address (< 3 months) + visura camerale

---

## Sources
- [EHIWEB VivaVox Tariffe](https://www.ehiweb.it/voip/tariffe-voip/)
- [EHIWEB VivaVox Flat](https://www.ehiweb.it/voip/tariffa-vivavox-flat/)
- [Messagenet VoIP Business](https://messagenet.com/voip/)
- [OpenVOIP Tariffe](https://www.openvoip.it/tariffe-telefoniche-voip.html)
- [VoIPVoice Flat](https://www.voipvoice.it/voip-flat/)
- [Fastweb NeXXt Communication](https://www.fastweb.it/piccole-medie-imprese/schede/centralino-ucc/)
- [TIM Business Centralini](https://timbusiness.tim.it/fisso/centralini)
- [Telnyx Pricing](https://telnyx.com/pricing)
- [Telnyx Italy DID Requirements](https://support.telnyx.com/en/articles/1311462-italy-did-requirements)
- [Twilio Italy Voice Pricing](https://www.twilio.com/en-us/voice/pricing/it)
- [VoIP Aziendale Costi 2026](https://bulltech.it/blog/voip-aziendale-costi-guida)
- [Deviazione Chiamata Italia](https://www.sostariffe.it/internet-casa/guide/trasferimento-di-chiamata-fastweb-tim-vodafone-e-altri-provider-come-fare)
