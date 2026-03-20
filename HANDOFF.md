# FLUXION — Handoff Sessione 105 → 106 (2026-03-20)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni. MAI presentare problemi senza soluzioni. MAI fare il compitino."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 (127.0.0.1) | **iMac DISPONIBILE + PIPELINE ATTIVA**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22
**Tauri dev su iMac**: `bash -l -c 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'`

---

## STATO GIT
```
Branch: master | HEAD: 91003ff
type-check: 0 errori
iMac: sincronizzato
Commit S105: aaa728f (5 UX bug fix), 91003ff (HANDOFF update)
```

---

## COMPLETATO SESSIONE 105

### 1. Bug UX Audit — TUTTI FIXATI (commit aaa728f)
- **BUG-1**: VoiceAgentSettings → "Gestita automaticamente da FLUXION AI" + health check live
- **BUG-2**: SmtpSettings già aveva guida Gmail App Password (4 step)
- **BUG-3**: Dashboard Welcome Card per DB vuoto con CTA
- **BUG-4**: Landing /voip-guida creata (guida EHIWEB 3 step)
- **BUG-5**: activate.html riscritta (rimossa API rotta, guida statica 3 passi)

### 2. Infra Stripe + Email — COMPLETATA
- **CF Worker LIVE**: https://fluxion-proxy.gianlucanewtech.workers.dev (health OK)
- **6 secrets configurati**: ED25519_PUBLIC_KEY, GROQ_API_KEY, CEREBRAS_API_KEY, OPENROUTER_API_KEY, RESEND_API_KEY, STRIPE_WEBHOOK_SECRET
- **Webhook Stripe attivo**: `we_1TD6liIW4bHDTsaHr1LIrukH` → checkout.session.completed
- **Flusso completo**: Stripe checkout → webhook → Resend email → cliente riceve download link
- **Landing redeployata**: /voip-guida + activate.html fixata

### 3. Test Acquisto — IN CORSO (fondatore sta testando)
- Stripe Payment Links LIVE
- Fondatore testa flusso completo: landing → Stripe → /grazie → email arriva?

---

## DA FARE S106 — VIDEO DEMO LIVE + FASE 2 RESIDUI

### PRIORITA ASSOLUTA: Video Demo LIVE Walkthrough

**REQUISITO FONDATORE**: Il video deve essere LIVE e SPIEGATO (non screenshot statici).
Video walkthrough completo che mostra OGNI funzionalità di FLUXION.

**Deep Research CoVe 2026 OBBLIGATORIA — 4 subagenti paralleli:**
1. **Agente A**: Benchmark video demo SaaS PMI mondiali 2026 (Fresha, Mindbody, Jane App, Calendly, Square Appointments) — format, durata, stile, CTA, hosting, SEO
2. **Agente B**: Best practices YouTube per software demo 2026 — thumbnail, titolo, descrizione, tag SEO Italia, capitoli, end screen, card
3. **Agente C**: Tool stack video creation enterprise-grade GRATIS — ffmpeg, Playwright screen recording, Edge-TTS narrazione italiana, SRT sottotitoli, YouTube API upload automatico
4. **Agente D**: Analisi codebase FLUXION — tutte le schermate da registrare, flussi UX da mostrare, ordine ottimale, script narrativo

**Deliverables video:**
- [ ] Script narrativo completo in italiano (ogni schermata, ogni click, ogni frase)
- [ ] Screen recording automatizzato via Playwright + ffmpeg (ogni funzionalità)
- [ ] Narrazione Edge-TTS voce italiana (IsabellaNeural o simile)
- [ ] Sottotitoli SRT sincronizzati
- [ ] Thumbnail YouTube enterprise-grade
- [ ] Upload YouTube via API (canale FLUXION)
- [ ] Landing page: embed video + link YouTube
- [ ] Durata target: 3-5 minuti (benchmark Fresha/Mindbody)

### FASE 2 Residui (parallelizzabili con video)
- [ ] Wire phone-home nell'app (hook React + UI banner trial countdown)
- [ ] Prezzi Rust alignment 199/399 → 497/897 (su iMac via SSH)

### Stripe Cleanup (fondatore)
- [ ] Eliminare prodotto test `prod_UBT5nbzrbxvjh3` dal Dashboard
- [ ] Risultato test acquisto → fix se necessario

---

## STRIPE INFO
```
Account: LIVE
Webhook: we_1TD6liIW4bHDTsaHr1LIrukH (checkout.session.completed)
CF Worker: https://fluxion-proxy.gianlucanewtech.workers.dev
Base Payment Link: https://buy.stripe.com/bJe7sM19ZdWegU727E24000
Pro Payment Link: https://buy.stripe.com/00w28sdWL8BU0V9fYu24001
Test product DA ELIMINARE: prod_UBT5nbzrbxvjh3
Secrets: STRIPE_WEBHOOK_SECRET ✅, RESEND_API_KEY ✅, GROQ ✅, CEREBRAS ✅, OPENROUTER ✅, ED25519_PUB ✅
```

---

## DIRETTIVE FONDATORE (NON NEGOZIABILI)

1. **CTO MODE** — porta soluzioni, non problemi
2. **A PROVA DI BAMBINO** — 2 click massimo per qualsiasi operazione
3. **ZERO COSTI** — tutto €0, trova il modo
4. **ENTERPRISE GRADE** — gold standard mondiale
5. **ZERO SUPPORTO MANUALE** — ogni feature funziona senza telefonata
6. **MAI riferimenti Anthropic/Claude** — zero nel codice, commit, UI
7. **SARA = SOLO DATI DB** — zero improvvisazione
8. **SEMPRE 1 nicchia** (micro-categoria) — una PMI = un'attività
9. **TUTTO "FLUXION AI"** — mai esporre Groq/Cerebras all'utente
10. **NO download gratuito** — il cliente paga prima di scaricare
11. **NO fattura IVA** — Prestazione Occasionale, NO ricevuta menzionata
12. **COPY PERFETTO** — zero tecnicismi, PMI plain language sempre
13. **VIDEO LIVE E SPIEGATO** — non screenshot, walkthrough reale

---

## BUILD COMMANDS

```bash
# Build completo su iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master && bash scripts/build-macos.sh"

# Deploy landing
CLOUDFLARE_API_TOKEN=Jn27vQB1Vp8rkrA9v9cV1PFC-CRSczG6h1DvteBE wrangler pages deploy ./landing --project-name=fluxion-landing

# Deploy CF Worker
cd fluxion-proxy && CLOUDFLARE_API_TOKEN=Jn27vQB1Vp8rkrA9v9cV1PFC-CRSczG6h1DvteBE wrangler deploy

# Tauri dev su iMac (per screen recording)
ssh imac "bash -l -c 'cd \"/Volumes/MacSSD - Dati/fluxion\" && npm run tauri dev'"
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 106. CTO MODE FULL.
S105: 5 bug UX fixati, CF Worker LIVE con tutti i 6 secrets, Stripe webhook attivo, landing redeployata.
FOCUS S106: Video demo LIVE walkthrough FLUXION per YouTube.
Deep Research CoVe 2026 OBBLIGATORIA: 4 subagenti paralleli per benchmark video SaaS, YouTube SEO, tool stack gratis (ffmpeg+Playwright+Edge-TTS), script narrativo.
Il video deve essere LIVE e SPIEGATO — non screenshot statici.
Gestisci autonomamente YouTube upload. Target: 3-5 min, narrazione italiana, sottotitoli.
IN PARALLELO: wire phone-home app + prezzi Rust alignment.
Fondatore ha testato flusso acquisto Stripe — verificare risultato.
Pipeline iMac ATTIVA. iMac sincronizzato.
```
