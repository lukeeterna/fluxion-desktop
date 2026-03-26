# Requirements: FLUXION Lancio v1.0

**Defined:** 2026-03-26
**Core Value:** Italian PMI owners manage their entire business from one beautiful desktop app with voice assistant — paying once, owning forever.

## v1 Requirements

Requirements for commercial launch. Each maps to roadmap phases.

### Screenshots (SCRN)

- [ ] **SCRN-01**: Catturare screenshot Pacchetti (Festa Papà, Estate, Natale) da iMac con dati seed realistici
- [ ] **SCRN-02**: Catturare screenshot Fedeltà (punteggio VIP, timbri, premi) da iMac con dati seed realistici
- [ ] **SCRN-03**: Verificare qualità tutti i 23+ screenshot (dati italiani realistici, zero glitch, zero overlay, 1200x800+)

### Video (VID)

- [ ] **VID-01**: Scrivere copy voiceover V6 con PAS formula — Problem(0:00-0:15) → Agitate(0:15-0:45) → Solution(0:45-5:00)
- [ ] **VID-02**: Generare 5 nuove clip AI Veo3 (scene "dopo FLUXION" — salone organizzato, cliente soddisfatto, notifica WA, etc.)
- [ ] **VID-03**: Assemblare video V6 (4:30-5:00 min) con tutti screenshot + clip AI + voiceover Edge-TTS IsabellaNeural
- [ ] **VID-04**: Mostrare OGNI feature nel video: Dashboard, Calendario, Clienti, Schede, Pacchetti, Fedeltà, Sara, Cassa, Analytics
- [ ] **VID-05**: Creare thumbnail YouTube professionale (1280x720, persona in contesto lavorativo, non UI app)
- [ ] **VID-06**: Upload YouTube con capitoli timestamp, SRT sottotitoli italiani, metadata SEO (keyword front-loaded)
- [ ] **VID-07**: Prezzo competitor corretto nel video: "centoventi euro al mese, millequattrocento all'anno"

### Landing (LAND)

- [ ] **LAND-01**: Embed video YouTube nella landing (above fold o sezione hero dedicata)
- [ ] **LAND-02**: Creare pagina /installa con guida Gatekeeper Sequoia 15.1+ (GIF animate per ogni step, non screenshot statici)
- [ ] **LAND-03**: Ottimizzare landing mobile-first (3-tap path: CTA → Stripe → pagamento)
- [ ] **LAND-04**: Loss framing above the fold: "Un gestionale in abbonamento: €1.800 in 3 anni. FLUXION: €497 una volta."
- [ ] **LAND-05**: Verificare flusso acquisto E2E completo: Landing → Stripe → webhook → email Resend → /grazie → download → install → attiva
- [ ] **LAND-06**: Deploy CF Pages --branch=production con tutti gli aggiornamenti
- [ ] **LAND-07**: Aggiornare screenshot nella landing con quelli nuovi (Sprint 2)

### Sales Agent (SALE)

- [ ] **SALE-01**: Scraper Google Places API per lead PMI italiane (100+ contatti per città/categoria, con telefono/rating/categoria)
- [ ] **SALE-02**: Automazione Playwright WA Web con sessione Chromium persistente e playwright-stealth
- [ ] **SALE-03**: Warmup protocol hardcoded non-bypassabile (10 msg/day settimane 1-2, 20 msg/day settimane 3-4, delay random 90-300s)
- [ ] **SALE-04**: 6 template messaggi WA personalizzati per categoria (parrucchiere, officina, estetica, palestra, dentista, generico PMI)
- [ ] **SALE-05**: Dashboard HTML con funnel completo (scrappati → contattati → risposte → click → acquisti) e controlli pausa/riprendi
- [ ] **SALE-06**: UTM tracking su tutti i link outreach (?utm_source=wa&utm_medium=outreach&utm_campaign=[verticale]-[regione])
- [ ] **SALE-07**: Validazione numeri italiani (mobile 3XX, dedup per telefono, flag lead senza reviews per review manuale)
- [ ] **SALE-08**: SQLite state DB per tracking stato ogni lead (da_contattare → contattato → risposto → convertito)

### Post-lancio (POST)

- [ ] **POST-01**: Windows MSI build via GitHub Actions (tauri-action + WiX + PyInstaller sidecar voice-agent)
- [ ] **POST-02**: Content repurposing: V6 video → 5 clip verticali 30s (9:16) per TikTok/Reels/Shorts
- [ ] **POST-03**: Referral program con ?ref= tracking in CF Worker KV (trigger: 30 giorni + 10 booking Sara completati)
- [ ] **POST-04**: Pagina /installa Windows con guida SmartScreen "Esegui comunque" (GIF animate)
- [ ] **POST-05**: VirusTotal pre-release check obbligatorio prima di pubblicare link download Windows

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Canali Vendita

- **CHAN-01**: Outreach commercialisti (€100 referral per conversione, 1 commercialista = 50+ PMI)
- **CHAN-02**: Click-to-WhatsApp ads (richiede LTV validato prima di paid acquisition)
- **CHAN-03**: Blog/SEO content pipeline (long-term, mesi per traffico organico)

### Distribuzione

- **DIST-01**: Universal Binary macOS (Intel + Apple Silicon in un unico .app)
- **DIST-02**: Windows EV code signing certificate (€299/anno — defer fino a revenue sufficiente)
- **DIST-03**: Auto-update mechanism (GitHub Releases polling + in-app notification)

### Infrastruttura

- **INFR-01**: Groq dual-pool rate limiting (Sara priority vs Sales Agent off-peak)
- **INFR-02**: Cerebras fallback wiring completo nel CF Worker proxy

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Mobile app | Desktop-first, mobile later — PMI usa PC in negozio |
| Multi-nicchia per licenza | 1 PMI = 1 attività, decisione permanente |
| Download gratuito | Il cliente paga PRIMA di scaricare |
| SaaS/abbonamento | Lifetime only, decisione permanente |
| Certificati code signing a pagamento | Ad-hoc codesign + pagina istruzioni, €0 |
| WhatsApp Business API | Zero costi — WA Web automation con Playwright |
| Paid ads | Richiede LTV validato, defer a post-primi-clienti |
| Commercialisti outreach v1.0 | Richiede clienti paganti per credibilità, defer a v1.1 |
| Real-time chat in-app | WhatsApp copre già la comunicazione |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCRN-01 | Phase 9 | Pending |
| SCRN-02 | Phase 9 | Pending |
| SCRN-03 | Phase 9 | Pending |
| VID-01 | Phase 10 | Pending |
| VID-02 | Phase 10 | Pending |
| VID-03 | Phase 10 | Pending |
| VID-04 | Phase 10 | Pending |
| VID-05 | Phase 10 | Pending |
| VID-06 | Phase 10 | Pending |
| VID-07 | Phase 10 | Pending |
| LAND-01 | Phase 11 | Pending |
| LAND-02 | Phase 11 | Pending |
| LAND-03 | Phase 11 | Pending |
| LAND-04 | Phase 11 | Pending |
| LAND-05 | Phase 11 | Pending |
| LAND-06 | Phase 11 | Pending |
| LAND-07 | Phase 11 | Pending |
| SALE-01 | Phase 12 | Pending |
| SALE-02 | Phase 12 | Pending |
| SALE-03 | Phase 12 | Pending |
| SALE-04 | Phase 12 | Pending |
| SALE-05 | Phase 12 | Pending |
| SALE-06 | Phase 12 | Pending |
| SALE-07 | Phase 12 | Pending |
| SALE-08 | Phase 12 | Pending |
| POST-01 | Phase 13 | Pending |
| POST-02 | Phase 13 | Pending |
| POST-03 | Phase 13 | Pending |
| POST-04 | Phase 13 | Pending |
| POST-05 | Phase 13 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0

---
*Requirements defined: 2026-03-26*
*Last updated: 2026-03-26 — traceability complete, all 30 requirements mapped*
