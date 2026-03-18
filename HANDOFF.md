# FLUXION — Handoff Sessione 87 → 88 (2026-03-18)

## CTO MANDATE — NON NEGOZIABILE
> **"Code signing GRATIS. Pacchetti auto-installati nel processo. Link con spiegazione CHIARA prima di cliccare. VoIP: servono certezze assolute + copy cristallino che il costo e' la LINEA non FLUXION. ARGOS e' ALTRO progetto — specs sono solo REFERENCE di stack/pattern."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **ARGOS attivo su iMac — NON sovrapporre**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22
**ARGOS specs**: `/Volumes/MontereyT7/FLUXION/ARGOS-INTEGRATION-SPECS.md` (READ-ONLY, solo reference pattern)

---

## STATO GIT
```
Branch: master | HEAD: 662a95f (pushed)
Uncommitted:
  - HANDOFF.md (this file)
  - src/pages/Fornitori.tsx (orders null fix)
  - landing/index.html (lightbox + subcategories + video HTML5)
type-check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 87

### git push ✅
- Commit 662a95f pushato a origin/master
- Cloudflare Pages deploy manuale — landing live con prezzi corretti (€497/€897/€1.497)

### Fornitori bug fix ✅ (uncommitted)
- `orders is null` → `const orders = ordersRaw ?? []` — type-check OK

### Landing miglioramenti ✅ (uncommitted)
- **Lightbox**: click-to-enlarge screenshot con overlay scuro, close X/click/Escape
- **Sotto-categorie**: 6 settori con toggle "Scopri le specializzazioni" espandibile
- **Video**: iframe Vimeo → HTML5 `<video>` con `assets/fluxion-demo.mp4`

### VoIP Deep Research ✅
- `.claude/cache/agents/voip-italy-deep-research-2026.md`
- EHIWEB = strumento sbagliato (SIP per telefoni fisici, no API)
- Telnyx ~€3.60/mese o Twilio ~€5.90/mese via WebSocket
- MA: fondatore vuole CERTEZZA ASSOLUTA che serve + copy chiaro

### Audit CTO ✅
- Prodotto software al 85-90% — gestionale completo e funzionante
- 5 blocker vendita identificati (signing, sidecar, proxy, VoIP, installer)
- Priorita' corretta: infrastruttura distribuzione > cosmetica landing

### Memory aggiornata ✅
- `feedback_free_signing_no_pay.md` — code signing GRATIS, NON paga Apple/Windows
- `feedback_voip_clarity.md` — VoIP opzionale, costo = linea telefonica, copy cristallino
- `feedback_voip_misleading.md` — MAI info VoIP superficiali
- `project_argos_integration.md` → rinominato: ARGOS e' reference, NON integrazione

---

## ⚠️ DA FARE S88 — Deep Research CoVe 2026

### 1. COMMIT + PUSH (bloccante, 5 min)
- Committare: Fornitori fix + landing miglioramenti
- Push e ri-deploy landing su CF Pages (deploy manuale da dashboard)

### 2. DEEP RESEARCH: Distribuzione SENZA code signing a pagamento
- Come distribuire Tauri app su macOS SENZA Apple Developer Program?
  - Self-signed? `xattr -cr`? Istruzioni visive nell'installer?
  - Come fanno altri progetti open source (Obsidian, Logseq, etc.)?
- Come distribuire su Windows SENZA code signing?
  - SmartScreen bypass con istruzioni chiare?
  - Come fanno altri indie dev?
- L'installer DEVE includere pagina di spiegazione PRIMA del click
- Pacchetti Python (sidecar) auto-installati nel processo — ZERO intervento utente

### 3. DEEP RESEARCH: VoIP — servono certezze assolute
- Sara PUO' funzionare SENZA VoIP per v1? (solo mic in-app)
- Se VoIP serve: come si collega ESATTAMENTE a FLUXION?
- Flusso utente: cosa deve fare il cliente step by step?
- Il COSTO e' la LINEA TELEFONICA, non FLUXION — copy cristallino
- Processo automatizzato con link guidato
- Valutare se VoIP e' feature Pro/Clinic o se rimandare a v1.1

### 4. Card settori landing — icone professionali
- Emoji brutte (✂️💆🏋️) → SVG/icone/illustrazioni professionali

### 5. guida-pmi.html — proteggere dal deploy pubblico

### 6. Cloudflare Workers Proxy API
- Auth Ed25519 (gia' in FLUXION) → Groq + Cerebras fallback
- Zero config per il cliente (niente API key)

---

## ⚠️ REGOLA iMac (S85-S87)
**ARGOS attivo su iMac (PM2: dashboard, wa-daemon, tg-bot)**. NON usare iMac per:
- Build Tauri (`npm run tauri build/dev`)
- Test che richiedono porta 3001
Usare MacBook per tutto il possibile.

---

## DIRETTIVE CTO (da memory — NON NEGOZIABILI)

1. **Code signing GRATIS** — NON proporre Apple Dev ($99) o Windows signing
2. **Pacchetti auto-installati** — PyInstaller sidecar nel processo di installazione, ZERO intervento utente
3. **Link con spiegazione CHIARA** — pagina visiva prima di ogni click nel processo di installazione
4. **VoIP opzionale** — costo = linea telefonica, NON FLUXION. Copy cristallino. Certezza assoluta prima di implementare
5. **ARGOS = reference** — NON integrazione. Stack/pattern condivisi, business separati

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 88. Task:
1. Commit + push (Fornitori fix + landing improvements)
2. DEEP RESEARCH CoVe 2026: distribuzione Tauri SENZA code signing a pagamento (come fanno Obsidian, Logseq, indie dev?)
3. DEEP RESEARCH CoVe 2026: VoIP certezze assolute — serve davvero per v1? Come si collega? Copy cristallino per il cliente
4. Card settori: emoji → icone professionali
5. Proteggere guida-pmi.html
6. Cloudflare Workers Proxy API (zero config cliente)
DIRETTIVE: signing GRATIS, pacchetti auto-install, link con spiegazione, VoIP opzionale con copy chiaro, ARGOS = solo reference.
```
