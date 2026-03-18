# FLUXION — Handoff Sessione 89 → 90 (2026-03-18)

## CTO MANDATE — NON NEGOZIABILE
> **"COPY E IMMAGINI PERFETTE, NON ACCETTO COMPROMESSI. Code signing GRATIS. Pacchetti auto-installati nel processo. Link con spiegazione CHIARA prima di cliccare. VoIP NON in v1. ARGOS e' ALTRO progetto."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **ARGOS attivo su iMac — NON sovrapporre**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22

---

## STATO GIT
```
Branch: master | HEAD: b2ab31b (pushed)
Uncommitted: HANDOFF.md + ROADMAP + landing (da committare)
type-check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 89

### Task 3: ROADMAP aggiornata ✅
- **F15 VoIP**: piano progressivo v1/v1.1/v1.2 (no VoIP in v1, WebRTC v1.1, Telnyx v1.2)
- **F17 Distribuzione**: strategia gratis (ad-hoc macOS, MSI unsigned Windows, pagina istruzioni)
- **FASE 2**: rimossi riferimenti Apple Developer $99/anno e Windows signing $120/anno
- Timestamp aggiornato a S89

### Task 4: Landing copy VoIP → in-app + WhatsApp ✅
- **Titolo**: "La tua segretaria AI per il telefono" → "Gestionale con AI per PMI italiane. Sara prenota per te 24/7"
- **Meta**: "Sara risponde al telefono" → "Sara gestisce appuntamenti, invia WhatsApp automatici"
- **Hero H1**: "Sara risponde al telefono" → "Sara prenota per te"
- **Hero desc**: "segretaria vocale che prenota al telefono" → "assistente AI che gestisce appuntamenti, manda WhatsApp"
- **Badge**: "Segretaria vocale AI" → "Assistente AI per le prenotazioni"
- **Come funziona**: "Il cliente chiama" → "Il cliente contatta Sara", "Dalla chiamata" → "Dalla richiesta"
- **Mockup**: "Chiamata in entrata" → "Richiesta prenotazione", icona 📞 → 💬
- **Analytics**: "Ogni chiamata" → "Ogni interazione"
- **Screenshot Sara**: "Risponde al telefono" → "Capisce il cliente, prenota l'appuntamento"
- **Comparison table**: "Risponde al telefono da sola" → "Assistente AI che prenota da sola"
- **Pacchetti**: "Sara al telefono sa" → "Sara sa"
- **VIP**: "Il numero di telefono viene abbinato" → "Il cliente viene riconosciuto"
- **3 pilastri Comunicazione**: "Sara risponde al telefono 24/7" → "Sara gestisce le prenotazioni 24/7"
- **Pricing**: "Sara al telefono (solo Pro)" → "Sara AI (solo Pro)", "Sara al telefono" → "Sara AI"
- **Testimonials**: rimossi riferimenti a chiamate/telefono
- **FAQ offline**: "capire cosa dice il cliente al telefono" → "gestire le prenotazioni in automatico"
- **Footer**: rimosso FAQ duplicato, aggiunti link "Come installare" e "Guida"

### Task 1: Pagina "Come installare FLUXION" ✅
- **File**: `landing/come-installare.html`
- Tab macOS / Windows con switch JS
- macOS: 4 step (scarica DMG → trascina in Applicazioni → Gatekeeper 3 sub-step → attiva licenza)
- Windows: 5 step (scarica MSI → avvia → SmartScreen 2 sub-step → installa → attiva licenza)
- Box rassicurazione: "Perche' vedo un avviso di sicurezza?" con confronto Obsidian/Calibre/Logseq
- Sezione VirusTotal: verifica indipendente 0/70+ antivirus
- Troubleshooting: 4 casi comuni (Gatekeeper, SmartScreen, xattr, WebView2)
- Design coerente con landing (Tailwind + Inter + dark theme)

---

## ⚠️ DA FARE S90

### 2. Cloudflare Workers Proxy API (PRIORITA' ALTA)
- Auth Ed25519 (gia' in FLUXION) → Groq + Cerebras fallback
- Zero config per il cliente (niente API key)
- Riferimento: CLAUDE.md sezione "LLM/NLU — Architettura Zero-Config"
- **Effort**: 4-6h

### 5. PyInstaller sidecar build
- Voice agent → binario nativo (gia' infrastruttura in S85)
- Test su macOS reale (iMac necessario per build)
- Target bundle size: ~520MB
- **Effort**: 4-8h (richiede iMac)

### 6. Audit finale UI
- Verificare OGNI pagina, OGNI flusso
- Fix bug residui
- Test VAD live con microfono su iMac (quando disponibile)
- **Effort**: 4-6h

### Landing miglioramenti (se tempo)
- Aggiungere GIF/screenshot reali degli avvisi macOS/Windows nella pagina come-installare
- Video SRT: aggiornare testo "Risponde al telefono" nel sottotitolo

---

## ⚠️ REGOLA iMac (S85-S89)
**ARGOS attivo su iMac (PM2: dashboard, wa-daemon, tg-bot)**. NON usare iMac per:
- Build Tauri (`npm run tauri build/dev`)
- Test che richiedono porta 3001
Usare MacBook per tutto il possibile.

---

## DIRETTIVE CTO (da memory — NON NEGOZIABILI)

1. **COPY E IMMAGINI PERFETTE** — zero compromessi sulla qualita' del copy e del visual
2. **Code signing GRATIS** — ad-hoc macOS + MSI unsigned Windows + pagina istruzioni installazione
3. **Pacchetti auto-installati** — PyInstaller sidecar nel processo di installazione, ZERO intervento utente
4. **Link con spiegazione CHIARA** — pagina visiva "Come installare FLUXION" prima di ogni click
5. **VoIP opzionale** — NON in v1. v1.1 WebRTC gratis, v1.2 Telnyx Pro/Clinic
6. **ARGOS = reference** — NON integrazione. Stack/pattern condivisi, business separati

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 90. Task:
1. Cloudflare Workers Proxy API (zero config cliente)
2. PyInstaller sidecar build (richiede iMac)
3. Audit finale UI
4. Landing: GIF/screenshot reali avvisi installazione + aggiornare SRT video
DIRETTIVE: copy e immagini PERFETTE, signing GRATIS, VoIP NON in v1, ARGOS = solo reference.
```
