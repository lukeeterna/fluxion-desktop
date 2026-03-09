# CoVe 2026 Deep Research — PMI Italiane vs FLUXION
**Data**: 2026-03-09 | **Sessione**: 35 | **Status**: APPROVED CTO

## Executive Summary
FLUXION ha fondamenta tecniche world-class (Sara FSM 23 stati, Groq RAG, Ed25519 licensing).
Ma ha 8 gap enterprise che Fresha risolve e FLUXION no. Non accettiamo mediocrità.

---

## TOP 10 GAP (ordinati per impatto economico PMI)

### 🔴 #1 — LATENCY SARA: 1330ms vs target <800ms [BLOCKING]
- Pain: Sara SEMBRA un bot. Competitor (PolyAI, Twilio ConversationRelay) P50 <500ms.
- Gap: No LLM streaming, no TTS chunking, HTTP Bridge timeout 5s
- Fix: Groq stream=True + TTS partial synthesis on first 20 tokens
- Effort: XL | Revenue: BLOCCA Base→Pro conversion

### 🔴 #2 — REMINDER AUTOMATICI -24h/-1h/-15min [ASSENTE]
- Pain: 30% no-show rate = diretti soldi persi ogni giorno
- Gap: Zero APScheduler, zero reminder_scheduler.py, solo WA immediato post-booking
- Fix: APScheduler + reminder_scheduler.py + WA templates
- Effort: L | Revenue: -40% no-show = +25% slot fill = Pro killer feature

### 🔴 #3 — WAITLIST NOTIFY QUANDO SLOT SI LIBERA [ASSENTE]
- Pain: Slot liberato → nessuno avvisato → slot rimane vuoto
- Gap: waitlist DB esiste ma zero notification trigger su cancellazione
- Fix: check_and_notify_waitlist() ogni 5min + WA button "Conferma slot"
- Effort: M | Revenue: +15-20% conversion on cancellations

### 🔴 #4 — WHATSAPP CONFIRMATION BUTTON [ASSENTE]
- Pain: Cliente dice "sì" per telefono poi non viene
- Gap: WA message è plain text, zero interactive buttons (Fresha: Confermo/Modifica/Cancella)
- Fix: WhatsApp Cloud API interactive messages + callback handler
- Effort: M | Revenue: +5-10% confirmation rate

### 🔴 #5 — PDF IMPORT LISTINO FORNITORI [ASSENTE]
- Pain: Parrucchiere copia-incolla listino PDF fornitore = 30min/giorno = €2-3K/anno perso
- Gap: Fornitori.tsx è CRUD manuale, zero import
- Fix: pdfplumber + Groq parsing + preview UI + bulk INSERT
- Effort: L | Revenue: Clinic-tier differentiator

### 🔴 #6 — TESSERA FEDELTÀ UI + COMPLEANNO WA [SCHEMA ESISTE, UI MANCANTE]
- Pain: Schema loyalty.ts esiste ma titolare non può usarlo
- Gap: Zero UI collegata a loyalty points, zero birthday automation
- Fix: Wire loyalty UI + APScheduler birthday WA (-7 giorni, -1 giorno)
- Effort: M | Revenue: +8% return rate = Pro feature

### 🔴 #7 — SATISPAY API REALE [MANUAL ONLY]
- Pain: Satispay è #1 payment in Italia PMI. FLUXION registra solo manualmente.
- Gap: Zero Satispay API, zero payment request generation
- Fix: Satispay API integration (business.satispay.com)
- Effort: M | Revenue: Pro/Clinic differentiator

### 🔴 #8 — FATTURA AUTO DA APPUNTAMENTO [ASSENTE]
- Pain: 5h/mese perse a creare fatture manualmente da appuntamenti già registrati
- Gap: Zero link appuntamento → fattura, zero 1-click invoice
- Fix: "Emetti Fattura" button in CalendarioDialog → prefill da appuntamento
- Effort: M | Revenue: Clinic-tier justification

### 🔴 #9 — ANALYTICS DASHBOARD + REPORT PDF [ASSENTE]
- Pain: Titolare non sa quale servizio fa guadagnare di più
- Gap: Zero report UI, zero scheduled PDF, zero trend comparison
- Fix: React charts + KPI dashboard + monthly PDF export
- Effort: L | Revenue: Clinic-tier (data-driven decisions = premium)

### 🔴 #10 — CAMPAGNE WHATSAPP BULK + REFERRAL [ASSENTE]
- Pain: PMI spende €500-1000/mese in Facebook ads. ROI 5:1 su WA
- Gap: Zero bulk messaging, zero referral tracking, zero churn prevention
- Fix: WA broadcast list + template messages + referral tracking
- Effort: L | Revenue: Clinic-tier add-on or SaaS upsell

---

## FLUXION vs Fresha 2026

| Feature | FLUXION | Fresha | Gap |
|---------|---------|--------|-----|
| Voice booking | ✅ Sara (lenta) | ✅ (fast) | Latency |
| Latency P50 | 1330ms ❌ | <800ms ✅ | 1.7x più lento |
| Waitlist notify | ❌ | ✅ | ASSENTE |
| Reminders auto | ❌ | ✅ | ASSENTE |
| Marketing campaigns | ❌ | ✅ | ASSENTE |
| Inventory sync | ❌ | ✅ | ASSENTE |
| Analytics KPI | ❌ | ✅ | ASSENTE |
| **Prezzo** | **€497 lifetime** ✅ | **€50/mese** ❌ | Win FLUXION |

FLUXION vince su prezzo. Fresha vince su feature. Obiettivo: vincere su ENTRAMBI.

---

## ROADMAP Q2-Q4 2026 (enterprise level)

### Q2 (Aprile-Giugno) — FOUNDATION
1. Latency optimization (XL)
2. Waitlist notifications (M)
3. PDF supplier import (L)

### Q3 (Luglio-Settembre) — AUTOMATION  
1. Reminder scheduling (L)
2. WhatsApp confirmation buttons (M)
3. Tessera fedeltà UI (M)

### Q4 (Ottobre-Dicembre) — INTELLIGENCE
1. Analytics dashboard + report PDF (L)
2. Satispay real API (M)
3. Fattura auto da appuntamento (M)
4. WhatsApp bulk campaigns (L)
