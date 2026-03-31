# FLUXION — Roadmap al Lancio (v2 — 2026-03-23, S112)
> **Riscritto da zero.** Il vecchio roadmap era obsoleto e incoerente.
> Ogni sprint ha acceptance criteria misurabili. Niente "a braccio".

---

## STATO ATTUALE

### GIA' FATTO (non toccare)
- CRM + Calendario + Servizi + Operatori + Cassa + Fatture SDI
- Voice Agent Sara: 1975+ test PASS, FSM 23 stati, 5-layer RAG, Edge-TTS
- Schede verticali: Parrucchiere, Veicoli, Odontoiatrica, Estetica, Fitness, Carrozzeria, Fisioterapia
- Loyalty / Fedeltà + Compleanni WA + Pacchetti
- WhatsApp: conferma booking, promemoria -24h/-1h, compleanni
- License Ed25519 offline + Feature gate Sara (Base trial 30gg)
- CF Worker: fluxion-proxy (NLU proxy + Stripe webhook + activate)
- Stripe LIVE: Base €497 + Pro €897 payment links
- Landing LIVE: fluxion-landing.pages.dev con /grazie, /installa, /activate
- Resend email post-acquisto con 3 step guide
- PKG macOS installer (68MB)
- Agent Studio: 58 agenti, 15 dipartimenti

### NON FATTO (blocker lancio)
| # | Blocker | Perché blocca |
|---|---------|---------------|
| 1 | Screenshot belli con dati reali | Video e landing non convincono |
| 2 | Video che dimostra TUTTO FLUXION | Unico strumento marketing efficace |
| 3 | Landing con video embeddato | Il Sales Agent ha bisogno di una landing con video |
| 4 | Sales Agent WA (scraping + outreach) | Senza questo, zero vendite |
| 5 | Prezzi Rust allineati 497/897 | Mismatch backend |
| 6 | Phone-home wired | Trial Sara non scade |
| 7 | Universal Binary macOS | Intel Mac non supportati |
| 8 | Windows MSI | Metà mercato tagliato fuori |
| 9 | Pagina "Come installare" | Gatekeeper/SmartScreen = abbandono |

---

## SPRINT 1 — PRODUCT READY
> **Goal**: App pronta per essere mostrata. Dati demo belli, prezzi corretti.
> **Prerequisito di**: Sprint 2 (screenshot), Sprint 3 (video)
> **Agenti**: engineering/backend-architect, engineering/frontend-developer, infrastructure/imac-operator

### Task
- [ ] **1.1** Allineare prezzi Rust: 199/399 → 497/897 (iMac via SSH, lib.rs)
- [ ] **1.2** Wire phone-home nell'app (hook React + UI banner trial countdown)
- [ ] **1.3** Seed dati demo su iMac:
  - Dashboard: fatturato €4.850 mese, 48 clienti, 9 appuntamenti oggi
  - 3+ clienti VIP con punteggio fedeltà alto (Valeria 14/10, Giuseppe 3/10)
  - 2-3 pacchetti attivi (Festa del Papà, Pacchetto Estate, Promo Natale)
  - Incassi realistici nella cassa (contanti + carte + Satispay)
  - Zero avvisi "non configurato" sulla dashboard
- [ ] **1.4** Rimuovere warning "FLUXION non è ancora completamente configurato" dal demo

### Acceptance Criteria
- [ ] `npm run type-check` → 0 errori
- [ ] Dashboard mostra fatturato > €0, zero warning
- [ ] Pagina Pacchetti mostra almeno 2 pacchetti attivi
- [ ] Fedeltà mostra clienti con punteggio VIP

---

## SPRINT 2 — SCREENSHOT PERFETTI
> **Goal**: Catturare OGNI pagina FLUXION con dati belli. Base per video e landing.
> **Prerequisito di**: Sprint 3 (video)
> **Agenti**: design/screenshot-capturer, infrastructure/imac-operator

### Task
- [x] **2.1** Catturare da iMac via SSH (CGEvent + CGWindowListCreateImage):
  - [x] 01-dashboard.png (con fatturato, clienti VIP, appuntamenti)
  - [x] 02-calendario.png (giornata piena, colori per operatore)
  - [x] 03-clienti.png (lista con fedeltà visibile, badge VIP)
  - [x] 04-servizi.png (servizi con prezzi e durate)
  - [x] 05-operatori.png (profili con turni)
  - [x] 06-fatture.png (fatture emesse con importi)
  - [x] 07-cassa.png (incassi giornata con totali)
  - [x] 08-voice.png (Sara con conversazione attiva)
  - [x] 09-fornitori.png (lista fornitori con contatti)
  - [x] 10-analytics.png (grafici fatturato, servizi top)
  - [x] 11-impostazioni.png (sidebar con tutto configurato ✅)
  - [x] 12-pacchetti.png (Festa Papà, Estate, Natale) ★ NUOVO
  - [x] 13-fedelta.png (punteggio VIP, timbri, premi) ★ NUOVO
- [ ] **2.2** Catturare schede verticali a SCHERMO PIENO (non modal overlay):
  - 14-scheda-parrucchiere.png
  - 15-scheda-veicoli.png
  - 16-scheda-odontoiatrica.png
  - 17-scheda-estetica.png
  - 18-scheda-fitness.png
- [x] **2.3** Verificare: ogni screenshot 1280x720+, dati realistici, zero glitch

### Acceptance Criteria
- [x] 13+ screenshot in landing/screenshots/ (target: 18+ con schedes verticali)
- [x] Ogni screenshot ha dati realistici (166 clienti, €4.850 fatturato, 34 appuntamenti oggi)
- [x] Zero warning, zero overlay, zero popup indesiderati (banner "non configurato" assente)
- [ ] Schede verticali a schermo pieno (non modal su sfondo) — OPTIONAL for video

---

## SPRINT 3 — VIDEO CHE SPACCA
> **Goal**: Video promo 5-7 min che dimostra PIENAMENTE l'utilità di FLUXION.
> **Prerequisito di**: Sprint 4 (landing), Sprint 5 (Sales Agent)
> **Il video è lo strumento di marketing #1. Senza questo il Sales Agent è inutile.**
> **Agenti**: video/video-copywriter, video/video-editor, video/youtube-seo, video/storyboard-designer

### Task
- [ ] **3.1** Riscrittura copy voiceover:
  - Aggiungere sezione PACCHETTI & MARKETING (Festa Papà, Natale, Estate)
  - Aggiungere sezione FEDELTA (punteggio VIP, timbri, premi)
  - Correggere prezzo competitor: "centoventi euro al mese, millequattrocento all'anno"
  - Aggiungere: "Con Sara lavori in maniera ordinata"
  - Mostrare come Sara + pacchetti = fatturato extra
- [ ] **3.2** Aggiornare storyboard JSON con nuove scene:
  - Scena Pacchetti (screenshot 12-pacchetti.png)
  - Scena Fedeltà (screenshot 13-fedelta.png)
  - Scena "con Sara lavori ordinato" (screenshot + clip AI)
- [ ] **3.3** Generare voiceover Edge-TTS con nuovo script
- [ ] **3.4** Assemblare video V6 con nuovi screenshot + nuove scene
- [ ] **3.5** Endcard con logo FLUXION (già creata in S112)
- [ ] **3.6** Preparare metadata YouTube SEO:
  - Titolo ottimizzato (keyword front-loaded, italiano)
  - Descrizione con capitoli (00:00 Introduzione, etc.)
  - Tags italiani (gestionale parrucchiere, software prenotazioni, etc.)
  - SRT sottotitoli italiani
- [ ] **3.7** Upload MANUALE su YouTube Studio (API blocca in PRIVATE)
- [ ] **3.8** Preparare thumbnail con Pillow (1280x720, alta leggibilità)

### Acceptance Criteria
- [ ] Video V6: 5-7 min, 1280x720, H.264 High
- [ ] Sezione Pacchetti/Marketing presente nel video
- [ ] Sezione Fedeltà/VIP presente nel video
- [ ] Prezzo competitor corretto (€120+/mese)
- [ ] Screenshot nel video sono BELLI (non quelli vecchi)
- [ ] YouTube: video pubblicato con capitoli + SRT
- [ ] Thumbnail professionale

---

## SPRINT 4 — LANDING DEFINITIVA + DEPLOY
> **Goal**: Landing con video embeddato, pronta per il Sales Agent.
> **Agenti**: marketing/landing-optimizer, engineering/devops-automator

### Task
- [ ] **4.1** Embed video YouTube nella landing (above fold o sezione dedicata)
- [ ] **4.2** VideoObject JSON-LD schema per Google rich results
- [ ] **4.3** Aggiornare screenshot nella landing con quelli nuovi (Sprint 2)
- [ ] **4.4** Verifica flusso acquisto end-to-end:
  - Landing → video → CTA → Stripe → pagamento → email → /grazie → download → install → attiva
- [ ] **4.5** Deploy CF Pages `--branch=production`
- [ ] **4.6** Test: aprire landing da telefono, tablet, desktop — tutto funziona

### Acceptance Criteria
- [ ] Video visibile sulla landing
- [ ] Flusso acquisto testato end-to-end (fino ad attivazione)
- [ ] Mobile responsive
- [ ] Deploy production verificato

---

## SPRINT 5 — SALES AGENT WHATSAPP (il motore vendite)
> **Goal**: Agente automatico che scrappa PMI e invia WA con link al video/landing.
> **Prerequisito**: Sprint 3 (video) + Sprint 4 (landing) COMPLETATI
> **Questo è il cuore del business. Senza questo, zero vendite.**
> **Agenti**: sales/, marketing/growth-hacker, studio-operations/analytics-reporter

### Architettura
```
SCRAPING (PagineGialle/PagineBianche)
  → Per regione → provincia → città → categoria PMI
  → Estrai: nome attività, telefono, indirizzo, categoria
  → Salva in SQLite locale (leads.db)

OUTREACH (WhatsApp Web — NO API, zero costi)
  → Selenium/Playwright controlla WhatsApp Web
  → Invia messaggio personalizzato per categoria:
    "Ciao [Nome], gestisci [categoria] a [città]?
     Guarda come FLUXION può aiutarti: [link video]"
  → Rate limiting: max 20-30 msg/giorno (per evitare ban WA)
  → Variazione testo (spin) per sembrare naturale
  → Orari invio: lun-ven 9:00-12:00, 14:00-17:00

DASHBOARD (React o semplice HTML)
  → Contattati per regione/città/categoria
  → Risposte ricevute
  → Click su link (UTM tracking)
  → Conversioni (Stripe webhook)
  → Coda messaggi in attesa
  → Stato: scraping / invio / pausa / completato
```

### Task
- [ ] **5.1** Scraper PagineGialle/PagineBianche:
  - Input: regione, provincia, città, categoria (parrucchiere, officina, etc.)
  - Output: lista contatti con telefono in leads.db
  - Rispettare robots.txt e rate limit
- [ ] **5.2** WhatsApp Web automazione (Selenium/Playwright):
  - Login WA Web con QR code (una volta, sessione persistente)
  - Invio messaggi da coda (leads.db → stato: da_contattare → contattato)
  - Rate limiting intelligente (random delay 30-90s tra messaggi)
  - Max 20-30 msg/giorno per non essere bannato
  - Variazione copy per categoria PMI
- [ ] **5.3** Copy messaggi per categoria (6 template):
  - Parrucchiere/Barbiere
  - Officina/Gommista/Elettrauto
  - Centro Estetico/Nail
  - Palestra/Fitness
  - Dentista/Fisioterapista
  - Generico PMI
- [ ] **5.4** Dashboard web (HTML + SQLite):
  - Statistiche per regione/città/categoria
  - Funnel: scrappati → contattati → risposte → click → acquisti
  - Controllo: pausa/riprendi, cambia regione, aggiungi categoria
- [ ] **5.5** UTM tracking sui link (per tracciare da dove arrivano le vendite)
- [ ] **5.6** Automazione: LaunchAgent iMac, gira in background

### Acceptance Criteria
- [ ] Scraper estrae 100+ contatti per città/categoria
- [ ] WA Web invia messaggi senza ban (testato 7 giorni)
- [ ] Dashboard mostra funnel completo
- [ ] Copy personalizzato per almeno 6 categorie PMI
- [ ] Link con UTM tracciabile fino a Stripe conversion

---

## SPRINT 6 — POST-LANCIO (dopo prime vendite)
> **Goal**: Automatizzare supporto, moltiplicare contenuti, scalare.

### Task
- [ ] **6.1** Content repurposing: video V6 → 8 blog post + 30 social post + 13 clip short
- [ ] **6.2** Review collection: dopo appuntamento, WA chiede recensione Google
- [ ] **6.3** Referral program: €100 per vendita referral (commercialisti, consulenti)
- [ ] **6.4** Customer support auto-reply (CF Worker + Claude Haiku)
- [ ] **6.5** Universal Binary macOS (Intel + Apple Silicon)
- [ ] **6.6** Windows MSI build + pagina "Come installare"
- [ ] **6.7** YouTube Shorts (taglio automatico da video lungo)

---

## ORDINE DI ESECUZIONE

```
SPRINT 1 → SPRINT 2 → SPRINT 3 → SPRINT 4 → SPRINT 5
(product)   (screen)   (video)    (landing)   (sales)
                                                 ↓
                                            SPRINT 6
                                          (post-lancio)
```

**Dipendenze chiave:**
- Sprint 2 (screenshot) RICHIEDE Sprint 1 (dati demo belli)
- Sprint 3 (video) RICHIEDE Sprint 2 (screenshot belli)
- Sprint 4 (landing) RICHIEDE Sprint 3 (video da embeddare)
- Sprint 5 (Sales Agent) RICHIEDE Sprint 4 (landing con video = link da mandare)

**Non ci sono scorciatoie. L'ordine è questo.**

---

## NOTE CTO

### Il Sales Agent è il cuore
Il Sales Agent WA è l'unico canale di vendita attivo. YouTube SEO è passivo (arriva chi cerca).
Il Sales Agent va per regione, scrappa le PagineGialle, e contatta proattivamente.
Dashboard aggiornata in tempo reale. Rispetta i limiti WA Web (20-30 msg/giorno).
Per scalare: più numeri WA, più iMac, più regioni in parallelo.

### Il video è il messaggio
Senza un video che dimostra PIENAMENTE FLUXION (inclusi pacchetti, fedeltà, Sara),
il Sales Agent invia un link a una landing che non convince. Il video deve:
- Mostrare OGNI feature (dashboard, calendario, clienti, schede, pacchetti, fedeltà, Sara, cassa)
- Usare prezzi competitor corretti (€120+/mese)
- Dimostrare il valore: "Paghi una volta, usi per sempre"
- Essere bello. Non "decente". BELLO.

### Zero costi
- Scraping: gratuito (requests/BeautifulSoup)
- WA Web: gratuito (Selenium, sessione locale)
- Video: già pagato (Veo 3 clips)
- Landing: CF Pages free
- Dashboard: HTML locale
