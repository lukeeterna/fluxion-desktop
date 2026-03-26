# FLUXION — Handoff Sessione 113 → 114 (2026-03-25)

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
Branch: master | HEAD: 7272542
type-check: 0 errori
iMac: Tauri dev + Voice pipeline ATTIVI
Modifiche non committate: script video V4/V5, screenplay, ai-clips, storyboard JSON, AGENT STUDIO (58 agenti), 21 screenshot nuovi
```

---

## COMPLETATO SESSIONE 113

### 1. Screenshot 8 Schede Verticali + Selector + Trasformazioni (CGEvent iMac)
- **21 screenshot totali** in `landing/screenshots/` (01-21, numerazione pulita)
- Vecchi screenshot spostati in `landing/screenshots/_old/`
- Coordinate calibrate: WIN_X=360, WIN_Y=72, W=1200, H=800, immagine 1:1
- Edit icon: abs X=1443, Y=470+(row*49). Tab Scheda: X=1135, Y=258
- Tile selector: Left X=850, Right X=1060. Rows Y: 472, 555, 632, 710
- **NOTA**: ogni click su tile salva permanentemente il tipo per quel cliente

| # | File | Contenuto |
|---|------|-----------|
| 01-11 | Pagine principali | Dashboard→Impostazioni (22 Mar) |
| 12 | scheda-parrucchiere | Capelli, Colorazioni, Allergie, Preferenze, Prodotti, Trasformazioni |
| 13 | scheda-fitness | Profilo, Misurazioni, Scheda, Salute, Progress |
| 14 | scheda-estetica | Fototipo Fitzpatrick, Pelle, Allergie, Trattamenti, Corpo |
| 15 | scheda-medica | Anamnesi, Allergie, Farmaci, Visite, Parametri vitali |
| 16 | scheda-fisioterapia | Generale, Zone, Valutazioni, Sedute |
| 17 | scheda-odontoiatrica | Odontogramma interattivo, Anamnesi, Trattamenti |
| 18 | scheda-veicoli | Veicoli, Interventi, + Nuovo Veicolo |
| 19 | scheda-carrozzeria | Pratiche, Preventivi, Sinistri, Lavorazioni |
| 20 | scheda-selector | 8 verticali selezionabili |
| 21 | trasformazioni-prima-dopo | Foto Prima/Dopo con upload |

### 2. Sprint 1 — PRODUCT READY: Verificato COMPLETO
- Prezzi 497/897 GIA' nel Rust (lib.rs + license_ed25519.rs) ✅
- Phone-home GIA' wired (usePhoneHome + SaraTrialBanner in MainLayout) ✅
- Seed SQL pronto (scripts/seed-video-demo.sql, 203 righe) ✅
- Banner dashboard GIA' nascosto per items opzionali (commit 7272542) ✅

### 3. Processo IMPRESSO A FUOCO in CLAUDE.md
```
RESEARCH (Skill Agents) → GSD PLAN → SKILL IMPLEMENT → CODE REVIEW → VERIFY → DEPLOY
```
- Aggiunto in CLAUDE.md sezione "PROCESSO ESECUZIONE COMPLETO"
- Aggiunto riferimento Agent Studio (58 agenti, 15 dipartimenti)
- MAI saltare una fase, MAI usare general-purpose se esiste agente specializzato

### 4. Deep Research CoVe 2026 — 10 Agenti Lanciati
**TUTTI COMPLETATI (240KB totali):**

| File | Size | Contenuto chiave |
|------|------|-----------------|
| `2026-video-selling-trends-research.md` | 19KB | VSL morti, voice notes 22-28%, calcolatore perdite, commercialisti arma segreta |
| `veo3-clips-v6-research.md` | 3KB | Prompt V6, parametri, 5 nuove clip necessarie |
| `video-copywriter-v6-research.md` | 30KB | Bozza script V6 completa, PAS formula, timing |
| `storyboard-v6-research.md` | 25KB | Sequenza scene V6 ottimale, ritmo, transizioni |
| `growth-first-100-clients-research.md` | 28KB | 90-120gg per 100 clienti, YT link in WA (18-22% CTR), commercialisti SUBITO, Google Places API, max 20 msg/gg WA |
| `landing-v2-optimization-research.md` | 31KB | Struttura landing V2 sezione per sezione, CTA, mobile |
| `video-sales-outreach-research-2026.md` | 33KB | Psicologia PMI, WA outreach, funnel completo |
| `competitor-video-analysis-2026.md` | 34KB | Fresha/Treatwell/Mindbody analisi video |
| `us-smb-sales-outreach-research-2026.md` | 37KB | US playbook, value-first, message frameworks |

### 5. Key Findings dalla Research Completata
- **VSL MORTI** → formato "Problem, Proof, Price" 5-6 min max
- **Voice notes WA = 22-28% risposte** vs <1% messaggi generici
- **"Calcolatore Perdite PMI"** = lead magnet gratuito (web tool da costruire)
- **Commercialisti = arma segreta** → 1 commercialista = 50+ clienti PMI
- **Loss framing 2.1x meglio** → "Stai perdendo €3.200/anno"
- **Mostrare prezzo SUBITO** → nasconderlo = -23% conversioni in Italia
- **Primi 3 secondi video**: telefono che squilla in salone vuoto, NON logo intro
- **€497 lifetime è accidentalmente ottimale** → prezzo alto = qualità percepita alta
- **Loom-style casual > polished production** per software demo SMB (2.3x conversioni)
- **Short clips per social**: tagliare 10-15 vertical clips da V6 per TikTok/Reels/Shorts

---

## DA FARE S114

### IMMEDIATO: Completare Research + GSD Planning
1. Aspettare completamento 7 agenti di research rilanciati
2. Sintetizzare 10 file research in strategia unica
3. `/gsd:new-milestone` — "Lancio v1.0" con 5 sprint come fasi
4. `/gsd:plan-phase` per ogni sprint

### Sprint 2 — SCREENSHOT PERFETTI (quasi done)
- ✅ 21 screenshot catturati
- ❌ **2.3** Screenshot Pacchetti (Festa Papà, Estate, Natale) — DA CATTURARE
- ❌ **2.4** Screenshot Fedeltà (punteggio VIP, timbri, premi) — DA CATTURARE
- ❌ **2.5** Verifica qualità tutti gli screenshot

### Sprint 3 — VIDEO V6
- Basare su research completata (2026-video-selling-trends-research.md)
- Blueprint video: Problem(0:00-0:30) → Solution(0:30-1:00) → Walkthrough(1:00-3:30) → Verticals(3:30-4:30) → Price(4:30-5:00) → CTA(5:00-5:30)
- Nuove clip Veo 3 necessarie (5 clip "dopo FLUXION")
- Copy V6 da scrivere con video-copywriter agent

### Sprint 4-6
- Vedi ROADMAP_REMAINING.md

---

## ACCOUNT & CREDENZIALI

### Google Cloud (Video AI)
```
Email: fluxion.gestionale@gmail.com
Project: project-07c591f2-ed4e-4865-8af
Crediti: €254 (scadenza 22 giugno 2026)
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

## RESEARCH FILES SESSIONE 113-114 (240KB+ totali)
```
.claude/cache/agents/
├── 2026-video-selling-trends-research.md     ← 19KB ✅ GOLD
├── veo3-clips-v6-research.md                 ← 3KB ✅
├── growth-first-100-clients-research.md      ← 28KB ✅ (754 righe, roadmap 90-120gg)
├── landing-v2-optimization-research.md       ← 31KB ✅
├── competitor-video-analysis-2026.md         ← 35KB ✅ (701 righe, confermato completo)
├── video-copywriter-v6-research.md           ← 29KB ✅ (rilanciato per approfondimento)
├── storyboard-v6-research.md                 ← 25KB ✅ (rilanciato per approfondimento)
├── video-sales-outreach-research-2026.md     ← 32KB ✅ (rilanciato per approfondimento)
├── us-smb-sales-outreach-research-2026.md    ← 36KB ✅ (rilanciato per approfondimento)
```
**TUTTI COMPLETATI E VERIFICATI** — 272KB totale, 9/9 file pronti per GSD planning

---

## ROADMAP v2 — 6 SPRINT AL LANCIO
```
Sprint 1: Product Ready ✅ COMPLETATO (S113)
Sprint 2: Screenshot Perfetti (21/23 catturati, mancano pacchetti + fedeltà)  ← PROSSIMO
Sprint 3: Video V6 (basato su research 2026)
Sprint 4: Landing + Deploy (video embeddato, flusso E2E)
Sprint 5: Sales Agent WA (scraping + outreach + voice notes)
Sprint 6: Post-lancio (content repurposing, referral, Windows)
```

---

## QUALITA' RESEARCH — VERIFICATA ✅
```
6374 righe totali | 272KB | 9 file | 76+ sezioni strutturate
PMI outreach: 1118L 12sez | Storyboard: 971L 10sez | Copywriter: 751L 13sez
Growth: 753L 12sez | Competitor: 700L 6sez | US SMB: 806L 11sez
Landing: 782L 13sez | Trends: 440L 10sez | Veo3: 53L (prompt tecnici)
```

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 114. Research 272KB COMPLETA e VERIFICATA.
COMANDO: /gsd:new-milestone
- Nome: "Lancio v1.0"
- 5 fasi: Sprint 2 (Screenshot), Sprint 3 (Video V6), Sprint 4 (Landing),
  Sprint 5 (Sales Agent WA), Sprint 6 (Post-lancio)
- Sprint 1 già completato (S113)
- Research: .claude/cache/agents/ (9 file, 272KB, 6374 righe)
- BLOCCANTI VIDEO: screenshot PacchettiAdmin + LoyaltyProgress (iMac)
- Servizi iMac ATTIVI (3001 + 3002)
```
