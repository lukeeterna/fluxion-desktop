# Roadmap: FLUXION

## Milestones

- ✅ **v0.9.0 Product** — Phases 1-8 (shipped 2026-03-15)
- 🚧 **v1.0 Lancio** — Phases 9-13 (in progress)

---

<details>
<summary>✅ v0.9.0 Product (Phases 1-8) — SHIPPED 2026-03-15</summary>

Previous phases: F02 (vertical-system-sara), F02.1 (nlu-hardening), F03 (latency-optimizer), audioworklet (vad-fix), f-sara-nlu-patterns, f-sara-voice, p0.5 (onboarding-frictionless), sdi-aruba. All complete as of 2026-03-15. Full details preserved in git history.

Sprint 1 Product Ready also complete (S113): prezzi 497/897 Rust, phone-home, seed dati demo, setup banner fix.

</details>

---

## 🚧 v1.0 Lancio (In Progress)

**Milestone Goal:** Portare FLUXION al primo lancio commerciale — screenshot perfetti di ogni pagina, video promo V6 che mostra tutto il prodotto, landing definitiva con video embeddato, Sales Agent WhatsApp per acquisizione lead, e distribuzione Windows.

**Dependency chain (non-negotiable sequential order):** Screenshots → Video → Landing → Sales Agent → Post-lancio

### Phase 9: Screenshot Perfetti

**Goal:** Tutti i 23+ screenshot dell'app sono catturati da iMac con dati italiani realistici, zero glitch, pronti per compositing video e embedding nella landing.
**Depends on:** Sprint 1 Product Ready (complete — seed data in DB, Pacchetti + Fedeltà dati presenti)
**Requirements:** SCRN-01, SCRN-02, SCRN-03
**Success Criteria** (what must be TRUE):
  1. Screenshot Pacchetti mostra 3 pacchetti distinti (Festa Papà, Estate, Natale) con prezzi, servizi inclusi e badge visivo — verificabile aprendo il PNG
  2. Screenshot Fedeltà mostra almeno un cliente VIP con punteggio alto, timbri accumulati e premi riscattabili — verificabile aprendo il PNG
  3. Tutti i 23+ screenshot sono 1200×800 pixel o superiori, dati italiani realistici (nomi, prezzi in euro, date italiane), zero overlay di sistema operativo, zero elementi UI a metà caricamento
**Plans:** 2 plans

Plans:
- [ ] 09-01-PLAN.md — Seed pacchetti/fedelta data + cattura screenshot Pacchetti e Fedelta da iMac
- [ ] 09-02-PLAN.md — Audit qualita tutti i 23+ screenshot, rifare quelli con glitch o difetti

---

### Phase 10: Video V6

**Goal:** `fluxion-promo-v6.mp4` è pubblicato su YouTube con struttura PAS (Problem 0:00-0:15, Agitate 0:15-0:45, Solution 0:45-5:00), mostra ogni feature del prodotto inclusi Pacchetti e Fedeltà, e il prezzo competitor corretto.
**Depends on:** Phase 9 (tutti gli screenshot pronti)
**Requirements:** VID-01, VID-02, VID-03, VID-04, VID-05, VID-06, VID-07
**Success Criteria** (what must be TRUE):
  1. Il video si apre su una scena di telefono perso (non sulla dashboard), citando un problema che il titolare di PMI riconosce immediatamente — i primi 15 secondi mostrano il problema, non il prodotto
  2. Ogni feature citata nei requisiti (Dashboard, Calendario, Clienti, Schede, Pacchetti, Fedeltà, Sara, Cassa, Analytics) appare visivamente almeno una volta nel video, verificabile scorrendo la timeline
  3. Il video su YouTube ha: titolo con keyword front-loaded, 8 capitoli con timestamp nel description, sottotitoli SRT italiani, thumbnail con persona in contesto lavorativo (non UI app)
  4. Il prezzo competitor pronunciato nel voiceover è "centoventi euro al mese, millequattrocento all'anno" — verificabile ascoltando il segmento Agitate
  5. La durata totale è 4:30-5:00 minuti — verificabile sulla pagina YouTube
**Plans:** 4 plans

Plans:
- [ ] 10-01-PLAN.md — Storyboard JSON V6 (27 scene) + generazione voiceover Edge-TTS
- [ ] 10-02-PLAN.md — 5 nuove clip AI Veo3 + thumbnail YouTube 1280x720
- [ ] 10-03-PLAN.md — Assemblaggio video V6 con ffmpeg + SRT sottotitoli italiani
- [ ] 10-04-PLAN.md — Upload YouTube con capitoli, SRT, metadata SEO + verifica URL

---

### Phase 11: Landing + Deploy

**Goal:** La landing page è live su CF Pages con il video V6 embeddato, loss framing above the fold, mobile-optimized (3-tap a Stripe), pagina /installa con GIF animate per Sequoia 15.1+, e il flusso acquisto E2E verificato end-to-end.
**Depends on:** Phase 10 (URL YouTube video V6 disponibile)
**Requirements:** LAND-01, LAND-02, LAND-03, LAND-04, LAND-05, LAND-06, LAND-07
**Success Criteria** (what must be TRUE):
  1. Aprendo fluxion-landing.pages.dev su mobile, il video YouTube è visibile above the fold o nella prima sezione hero, il testo loss-framing ("Un gestionale in abbonamento: €1.800 in 3 anni. FLUXION: €497 una volta.") è visibile senza scroll, e il bottone CTA principale porta a Stripe in un tap
  2. La pagina /installa mostra GIF animate per ogni step del bypass Gatekeeper su macOS Sequoia 15.1+ (almeno 6 step: System Settings → Privacy & Security → Open Anyway → admin password → confirm → open app) — verificabile su Safari iPhone e Chrome desktop
  3. Eseguendo il flusso completo (click CTA → Stripe test mode → webhook → email Resend → link download → install → attiva con email) senza errori, l'app si sblocca e mostra "Licenziato a: [email]" — verificabile in 10 minuti
  4. Tutti gli screenshot nella landing usano le versioni nuove della Phase 9 (nessun vecchio screenshot con dati placeholder visibile) — verificabile ispezionando le immagini nella pagina
**Plans:** TBD

Plans:
- [ ] 11-01: Aggiornare landing index.html — embed video V6, loss framing above fold, screenshot nuovi Phase 9
- [ ] 11-02: Creare /installa page con GIF animate Gatekeeper Sequoia 15.1+ + ottimizzazione mobile-first
- [ ] 11-03: Verifica flusso acquisto E2E completo + deploy CF Pages --branch=production

---

### Phase 12: Sales Agent WA

**Goal:** Un Sales Agent Python operativo che scrappa lead PMI italiane da Google Places, invia messaggi WA personalizzati per categoria con warmup protocol hardcoded, e traccia lo stato di ogni lead in SQLite con una dashboard HTML funzionante.
**Depends on:** Phase 11 (landing live + flusso acquisto E2E verificato — nessun outreach prima che il funnel sia pronto)
**Requirements:** SALE-01, SALE-02, SALE-03, SALE-04, SALE-05, SALE-06, SALE-07, SALE-08
**Success Criteria** (what must be TRUE):
  1. Eseguendo `python sales-agent/scraper.py --city Milano --category parrucchiere`, il comando produce `leads.json` con 100+ voci contenenti telefono, rating, categoria — e ogni numero è validato come mobile italiano (3XX) con dedup per telefono
  2. Il Sales Agent avvia una sessione WA Web persistente, seleziona il primo lead non contattato dalla coda, invia il template per la categoria corretta con UTM link, attende un delay random 90-300s, poi passa al lead successivo — verificabile osservando WA Web in Chromium
  3. Il sistema rifiuta di superare il rate limit della settimana corrente (10 msg/giorno settimane 1-2, 20 msg/giorno settimane 3-4) anche se l'operatore prova a forzare — questa limitazione non è bypassabile tramite argomenti CLI
  4. Aprendo `sales-agent/dashboard.html` nel browser, il funnel mostra contatori aggiornati per ogni stato (scrappati → contattati → risposte → click UTM → acquisti) con bottoni pausa/riprendi che persistono tra sessioni
**Plans:** TBD

Plans:
- [ ] 12-01: Lead scraper — Google Places API → leads.json con validazione numeri italiani + dedup
- [ ] 12-02: Playwright WA Web automation — sessione Chromium persistente, playwright-stealth, warmup protocol non-bypassabile
- [ ] 12-03: 6 template messaggi personalizzati per categoria + UTM tracking su tutti i link
- [ ] 12-04: SQLite state DB + dashboard HTML con funnel completo + controlli pausa/riprendi

---

### Phase 13: Post-Lancio

**Goal:** Windows MSI distribuibile su GitHub Releases, 5 clip verticali 30s per social media derivate dal V6, e referral program attivo con tracking ?ref= in CF Worker KV.
**Depends on:** Phase 12 (primo lancio avvenuto — Windows e referral richiedono base utenti)
**Requirements:** POST-01, POST-02, POST-03, POST-04, POST-05
**Success Criteria** (what must be TRUE):
  1. Il file `Fluxion_1.0.0_windows_x64.msi` è pubblicato su GitHub Releases, installabile su Windows 10 64-bit senza admin, e il check VirusTotal pre-release mostra 0 detection su motori principali (Windows Defender, Kaspersky, Malwarebytes)
  2. La pagina /installa-windows mostra GIF animate per il bypass SmartScreen "Esegui comunque" — verificabile su Chrome Windows
  3. Cinque clip verticali 30s (formato 9:16) sono presenti in `landing/assets/reels/` — una per categoria (salone, officina, estetica, palestra, dentista) — derivate da segmenti del video V6 con sottotitoli burn-in
  4. Visitando `fluxion-landing.pages.dev?ref=TEST123`, il CF Worker KV registra il click; dopo 30 giorni e 10 booking Sara completati, il referrer riceve notifica email automatica con link riscatto €100
**Plans:** TBD

Plans:
- [ ] 13-01: GitHub Actions workflow build-windows.yml — WiX MSI + PyInstaller sidecar voice-agent Windows
- [ ] 13-02: VirusTotal pre-release check + pagina /installa-windows con GIF SmartScreen
- [ ] 13-03: Content repurposing — V6 → 5 clip 9:16 per TikTok/Reels/Shorts con sottotitoli
- [ ] 13-04: Referral program — ?ref= tracking CF Worker KV + trigger logica 30gg + 10 booking

---

## Progress

**Execution Order:** 9 → 10 → 11 → 12 → 13

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 9. Screenshot Perfetti | v1.0 Lancio | 0/2 | Planned | - |
| 10. Video V6 | v1.0 Lancio | 0/4 | Planned | - |
| 11. Landing + Deploy | v1.0 Lancio | 0/3 | Not started | - |
| 12. Sales Agent WA | v1.0 Lancio | 0/4 | Not started | - |
| 13. Post-Lancio | v1.0 Lancio | 0/4 | Not started | - |

---

*Roadmap created: 2026-03-26 — Milestone v1.0 Lancio*
*Previous milestone (v0.9.0): Phases 1-8, complete 2026-03-15*
