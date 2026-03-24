# FLUXION — Handoff Sessione 112 → 113 (2026-03-23)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**
> **"SEMPRE valutare la skill migliore per il task specifico — è una REGOLA."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 3001 | Voice pipeline porta 3002 | **sshd ha Screen Recording + Accessibility**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS, Pillow, gcloud SDK, google-genai

---

## STATO GIT
```
Branch: master | HEAD: 0aee288
type-check: 0 errori
iMac: Tauri dev + Voice pipeline ATTIVI
Modifiche non committate: script video V4/V5, screenplay, ai-clips, storyboard JSON, AGENT STUDIO (58 agenti)
```

---

## COMPLETATO SESSIONE 112

### 1. Agent Studio FLUXION (58 agenti, 15 dipartimenti)
- Struttura `.claude/agents/` organizzata per dipartimento (ispirata a contains-studio/agents)
- 15 dipartimenti: engineering, voice, video, marketing, sales, design, verticals, distribution, infrastructure, whatsapp, customer-success, project-management, studio-operations, testing
- Ogni agente: frontmatter ufficiale Claude Code, model tier (opus/sonnet/haiku), memory: project, accesso .env
- INDEX: `.claude/agents/INDEX.md`
- 24 vecchi agenti flat archiviati in `_archived-flat/`
- 11 GSD system agents mantenuti in root

### 2. Deep Research CoVe 2026 (3 file)
- `agent-studio-structure-research-2026.md` — best practices, repo comparison, format ufficiale
- `youtube-vimeo-video-agents-research-2026.md` — API, SEO, MCP, strategy PMI Italia
- `missing-business-agents-research-2026.md` — 12 agenti business mancanti, differenziatori killer

### 3. ROADMAP v2 — Piano Lancio (6 Sprint)
- ROADMAP_REMAINING.md riscritto DA ZERO (il vecchio era obsoleto S94)
- 6 sprint sequenziali con dipendenze chiare e acceptance criteria misurabili
- Sprint 1→2→3→4→5→6 (ordine non negoziabile)

### 4. Endcard Video
- `tmp-video-build/endcard.png` — logo FLUXION su sfondo scuro
- `landing/assets/fluxion-promo-v5-final.mp4` — V5 + endcard (405s, 42MB)
- MA: video V5 NON è pronto per YouTube (screenshot brutti, mancano pacchetti)

### 5. Feedback Fondatore Salvati
- Screenshot nel video sono "orribili" → ricatturare dopo seed dati belli
- Mancano pacchetti/marketing/fedeltà nel video → aggiungere in V6
- Prezzo competitor sbagliato → "centoventi euro al mese" minimo
- Sales Agent = scraping PagineGialle + WA Web outreach (NON support email)
- Video è lo strumento #1 — senza video convincente il Sales Agent è inutile

---

## DA FARE S113 — SPRINT 1: PRODUCT READY

### 1.1 Allineare prezzi Rust 497/897
- Attuale: probabilmente ancora 199/399 nel backend Rust
- Target: Base €497, Pro €897 in lib.rs / commands
- Build su iMac via SSH dopo modifica

### 1.2 Wire phone-home nell'app
- Codice esiste: `src/lib/phone-home.ts` + CF Worker
- Collegare: hook React + UI banner trial countdown Sara
- Grace period 7gg già implementato

### 1.3 Seed dati demo su iMac
- Dashboard: fatturato €4.850, 48 clienti, 9 appuntamenti oggi
- 3+ clienti VIP con fedeltà alta
- 2-3 pacchetti attivi (Festa Papà, Estate, Natale)
- Incassi realistici (contanti + carte + Satispay)
- Script SQL: `scripts/seed-video-demo.sql` (aggiornare)

### 1.4 Rimuovere warning dashboard demo
- "FLUXION non è ancora completamente configurato" → deve sparire con dati demo

---

## ACCOUNT & CREDENZIALI

### Google Cloud (Video AI)
```
Email: fluxion.gestionale@gmail.com
Project: project-07c591f2-ed4e-4865-8af
Crediti: €254 (scadenza 22 giugno 2026)
Speso: ~$20 (Veo 3 clips)
Auth: gcloud SDK (/usr/local/share/google-cloud-sdk/bin/gcloud)
```

### Stripe
```
Base: https://buy.stripe.com/bJe7sM19ZdWegU727E24000
Pro: https://buy.stripe.com/00w28sdWL8BU0V9fYu24001
```

---

## AGENT STUDIO
```
.claude/agents/
├── engineering/ (6)    ├── voice/ (4)         ├── testing/ (5)
├── design/ (5)         ├── verticals/ (2)     ├── distribution/ (3)
├── video/ (7)          ├── marketing/ (7)     ├── sales/ (3)
├── infrastructure/ (3) ├── whatsapp/ (2)      ├── customer-success/ (3)
├── project-management/ (3) ├── studio-operations/ (5)
├── gsd-*.md (11 system)    ├── _archived-flat/ (24 old)
└── INDEX.md
```

---

## ROADMAP v2 — 6 SPRINT AL LANCIO
```
Sprint 1: Product Ready (prezzi Rust, phone-home, seed dati demo)     ← PROSSIMO
Sprint 2: Screenshot Perfetti (18+ screenshot da iMac con dati belli)
Sprint 3: Video V6 (pacchetti, fedeltà, prezzi corretti, nuovi screen)
Sprint 4: Landing + Deploy (video embeddato, flusso E2E verificato)
Sprint 5: Sales Agent WA (scraping PagineGialle + outreach WA Web)
Sprint 6: Post-lancio (content repurposing, reviews, referral, Windows)
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 113. Sprint 1: Product Ready.
Task: 1.1 Allineare prezzi Rust 497/897 su iMac, 1.2 Wire phone-home,
1.3 Seed dati demo belli, 1.4 Rimuovere warning dashboard.
Entrambi i servizi iMac ATTIVI (3001 + 3002).
```
