# FLUXION

## What This Is

Desktop management software for Italian SMBs (1-15 employees): salons, gyms, clinics, auto shops. Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent "Sara". Lifetime license model (Base €497 / Pro €897), zero SaaS, zero booking fees. Sara handles 24/7 voice bookings with 23-state FSM, 5-layer RAG, Edge-TTS.

## Core Value

Italian PMI owners can manage their entire business (appointments, clients, invoicing, loyalty, marketing) from one beautiful desktop app with a voice assistant that answers the phone — paying once, owning forever.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ CRM + Calendario + Servizi + Operatori + Cassa + Fatture SDI — v0.9.0
- ✓ Voice Agent Sara: 1975+ test PASS, FSM 23 stati, 5-layer RAG, Edge-TTS — v0.9.0
- ✓ 8 Schede verticali (Parrucchiere, Veicoli, Odontoiatrica, Estetica, Fitness, Carrozzeria, Fisioterapia, Medica) — v0.9.0
- ✓ Loyalty/Fedeltà + Compleanni WA + Pacchetti — v0.9.0
- ✓ WhatsApp: conferma booking, promemoria -24h/-1h, compleanni — v0.9.0
- ✓ License Ed25519 offline + Feature gate Sara (Base trial 30gg) — v0.9.0
- ✓ CF Worker: fluxion-proxy (NLU proxy + Stripe webhook + activate) — v0.9.0
- ✓ Stripe LIVE: Base €497 + Pro €897 payment links — v0.9.0
- ✓ Landing LIVE: fluxion-landing.pages.dev con /grazie, /installa, /activate — v0.9.0
- ✓ Resend email post-acquisto con 3 step guide — v0.9.0
- ✓ PKG macOS installer (68MB) — v0.9.0
- ✓ NLU vertical patterns: 6 macro × 17 sub-verticals — v0.9.0
- ✓ Latency optimizer: streaming LLM, LRU cache, Groq key pool — v0.9.0
- ✓ Adaptive TTS: Qwen3-TTS + Piper + SystemTTS fallback chain — v0.9.0
- ✓ AudioWorklet VAD pipeline — v0.9.0
- ✓ Sprint 1 Product Ready: prezzi 497/897 Rust, phone-home, seed dati demo — v0.9.0

### Active

<!-- Current scope: Milestone v1.0 Lancio -->

- [ ] Screenshot perfetti di OGNI pagina FLUXION con dati realistici
- [ ] Video promo V6 (5-7 min) che mostra TUTTO FLUXION
- [ ] Landing definitiva con video embeddato + flusso acquisto E2E
- [ ] Sales Agent WA (scraping PagineGialle + outreach automatico)
- [ ] Post-lancio: content repurposing, referral, Windows MSI

### Out of Scope

<!-- Explicit boundaries. -->

- Real-time chat in-app — non core per PMI, WhatsApp copre
- Mobile app — desktop-first, mobile later
- Multi-nicchia per licenza — 1 PMI = 1 attività, sempre
- Download gratuito — il cliente paga PRIMA di scaricare
- SaaS/abbonamento — lifetime only, decisione permanente
- Certificati code signing a pagamento — ad-hoc codesign, pagina istruzioni

## Current Milestone: v1.0 Lancio v1.0

**Goal:** Portare FLUXION dalla fase di sviluppo al primo lancio commerciale — screenshot perfetti, video promo, landing con video, Sales Agent WA automatico.

**Target features:**
- Screenshot Perfetti (completare Pacchetti + Fedeltà, verifica qualità)
- Video V6 Promo (5-7 min, PAS formula, mostra TUTTO)
- Landing Definitiva + Deploy (video embeddato, flusso E2E)
- Sales Agent WhatsApp (scraping + outreach + dashboard)
- Post-lancio (content repurposing, referral, Windows)

## Context

- **Dev environment**: MacBook (TypeScript/React) + iMac 192.168.1.2 (Rust build + voice pipeline)
- **Voice pipeline**: porta 3002 iMac, HTTP Bridge porta 3001
- **Research completata**: 272KB, 9 file in `.claude/cache/agents/` — trends 2026, growth, landing, competitor, video
- **Key findings research**: VSL morti, voice notes WA 22-28%, loss framing 2.1x, commercialisti arma segreta, €497 ottimale
- **Sprint 1 completato**: prezzi allineati, phone-home wired, seed dati demo, banner nascosto
- **21/23 screenshot catturati**: mancano Pacchetti e Fedeltà
- **Agent Studio**: 58 agenti specializzati in 15 dipartimenti

## Constraints

- **Zero costi**: Tutto deve costare €0 (CF free, GitHub free, Stripe solo %)
- **Enterprise grade**: Zero `any` TS, zero `--no-verify`, HTTPS, WAL mode
- **Ordine sequenziale**: Screenshot→Video→Landing→Sales→Post (dipendenze)
- **iMac required**: Rust build + screenshot capture + voice pipeline solo su iMac
- **Target**: PMI italiane, UI/copy sempre in italiano, UX "a prova di bambino"

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Lifetime vs SaaS | PMI italiane odiano abbonamenti, €497 lifetime = valore percepito alto | ✓ Good |
| Stripe diretto (no LemonSqueezy) | Zero intermediari, 1.5% EU cards, webhook CF Worker | ✓ Good |
| Ed25519 offline licensing | Zero server per validazione, funziona offline | ✓ Good |
| Sales Agent WA (no API, WA Web) | Zero costi, Selenium/Playwright, max 20-30 msg/giorno | — Pending |
| Video > Landing per conversioni | Research 2026: video demo è strumento #1 per SMB software | — Pending |
| Commercialisti come canale | 1 commercialista = 50+ clienti PMI, referral €100 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-26 after milestone v1.0 start*
