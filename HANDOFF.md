# FLUXION — Handoff Sessione 85 → 86 (2026-03-18)

## CTO MANDATE — NON NEGOZIABILE
> **"Screenshot REALI enhanced, landing PERFETTA con copy PMI, video demo con voiceover Isabella, TUTTO autonomo."**
> **"È il nostro biglietto da visita — niente 'accettabile'. Enterprise grade o niente."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **ALTRO PROGETTO SU iMac — NON sovrapporre**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip)

---

## STATO GIT
```
Branch: master | HEAD: 5e95ade
Push: ✅ sincronizzato
type-check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 85

### PyInstaller Sidecar Build ✅ (647778a)
- `voice-agent.spec` aggiornato (rimossi spaCy/torch/italian_nlu, aggiunti edge_tts/nlu/sales)
- `requirements.txt` pulito (da 62 → 32 righe, rimossi legacy deps)
- `build-sidecar.sh` script cross-platform con naming Tauri convention
- `voice_pipeline.rs` — sidecar-first startup + self-healing (30s health check, auto-restart 3x)
- `tauri.conf.json` — `externalBin: ["binaries/voice-agent"]`, category→Business
- **Build testato su iMac**: 59MB, avvio ~2s, NLU PASS, health OK
- Cargo check: PASS (iMac x86_64)

### Code Review Fixes ✅ (647778a)
- `tempfile.mktemp` → `NamedTemporaryFile(delete=False)`
- Silent `except` → `logger.debug()`
- Removed dead `reference_audio_path` parameter

### Screenshot Capture System ✅ (5e95ade)
- `e2e-tests/fixtures/tauri-mock.ts` — mock per TUTTI i Tauri invoke() commands
  - Dati demo realistici: "Salone Bella Vita", 10 clienti IT, 10 servizi, 4 operatori
  - 8 appuntamenti oggi, fatture, cassa, analytics mensili
- `e2e-tests/tests/screenshots.spec.ts` — 11 pagine catturate 1920x1080
- `landing/screenshots/*.png` — 11 screenshot reali

### Skills Create ✅ (5e95ade)
- `fluxion-screenshot-capture` — Tauri mock + Playwright pipeline
- `fluxion-landing-generator` — 12 sezioni, copy PMI, zero gergo tecnico
- `fluxion-video-creator` — ffmpeg slideshow + Edge-TTS voiceover (da completare)

---

## ⚠️ PROBLEMI SCREENSHOT DA FIXARE (S86)

### Screenshot con errori nel mock (mock data shape mismatch):
1. **Fatture** — NaN €: campo `importo` non corrisponde alla shape attesa dalla UI
2. **Cassa** — `report.incassi` era undefined (FIXATO nel mock ma non ri-testato con screenshot)
3. **Analytics** — `wa_confirm_rate` era undefined (FIXATO nel mock ma non ri-testato)
4. **Operatori** — mostrava "Inattivi" perché `attivo: true` invece di `attivo: 1` (FIXATO)

### Screenshot che necessitano enhancement:
- TUTTI gli screenshot necessitano **image enhancement** per la landing:
  - Device frame (MacBook mockup attorno allo screenshot)
  - Ombra, bordi arrotondati
  - Possibile zoom su feature specifiche
  - Z-Image Turbo MCP disponibile per hero images

---

## TASK S86 — LANDING + VIDEO (CTO MANDATE)

### 1. Fix screenshot rimanenti
- Ricompilare mock → rieseguire screenshots → verificare TUTTI 11 senza errori
- Fatture: fixare campo importo nel mock
- Verificare Cassa, Analytics, Operatori ora funzionano

### 2. Image Enhancement
- Device frame (MacBook mockup) attorno a ogni screenshot
- Possibile: Z-Image Turbo per hero images marketing
- Tool: ffmpeg overlay o API esterna (Screenhance, shots.so)

### 3. Landing Page Completa
- Skill: `/fluxion-landing-generator`
- 12 sezioni: Hero, Pain Points, Soluzione, Funzionalità (con screenshot), Sara AI,
  Settori (NON "verticali"), Confronto, Prezzi, Testimonianze, FAQ, CTA, Footer
- Copy: linguaggio semplice per titolari PMI, ZERO gergo tecnico
- Prezzi: Base €497 / Pro €897 / Clinic €1.497
- LemonSqueezy checkout URLs (in MEMORY.md)

### 4. Video Demo
- Skill: `/fluxion-video-creator`
- Edge-TTS IsabellaNeural per voiceover italiano
- ffmpeg slideshow da screenshot + audio
- Sottotitoli SRT auto-generati
- Upload YouTube/Vimeo

### 5. Copy Enterprise
- Ogni funzione spiegata per titolari PMI non tecnici
- Esempi concreti per settore (saloni, palestre, studi medici, officine)
- FAQ reali ("Funziona senza internet?", "Ho bisogno di un tecnico?")

### 6. Cloudflare Workers Proxy API (se tempo)
- Auth Ed25519, rate limit 200/giorno, Groq/Cerebras fallback

---

## ⚠️ REGOLA iMac (S85)
**Altro progetto attivo su iMac (SSH + VNC)**. NON usare iMac per:
- Build Tauri (`npm run tauri build/dev`)
- Test che richiedono porta 3001
USare MacBook per: Playwright (1420), ffmpeg, Edge-TTS, tutto il marketing

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 86. Task:
1. Fix screenshot mock (Fatture NaN, Cassa, Analytics, Operatori) → ri-cattura
2. Image enhancement screenshot (device frame MacBook mockup)
3. Landing page completa con /fluxion-landing-generator
4. Video demo con voiceover Edge-TTS IsabellaNeural
5. Copy PMI-friendly per OGNI funzione
REGOLA: iMac occupato da altro progetto — lavorare SOLO su MacBook.
REGOLA: Enterprise grade — ogni output è il biglietto da visita di FLUXION.
```
