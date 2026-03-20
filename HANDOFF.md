# FLUXION — Handoff Sessione 102 → 103 (2026-03-20)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni. MAI presentare problemi senza soluzioni. MAI fare il compitino. MAI contare metriche vuote."**

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
Branch: master | HEAD: 27eff8c (pushato + iMac sincronizzato)
type-check: 0 errori
iMac: sincronizzato, DB seed completo (tutte le schede)
```

---

## COMPLETATO SESSIONE 101-102

### 1. F17 macOS Packaging — BUILD v2 COMPLETO
- **PyInstaller sidecar**: 60MB Mach-O x86_64
- **Tauri build v2**: `Fluxion.app` 76MB + `Fluxion_1.0.0_x64.dmg` 71MB
- **Ad-hoc codesign**: firmato + verificato
- **DMG su MacBook**: `releases/v1.0.0/Fluxion_1.0.0_x64.dmg`

### 2. Mock Data RIMOSSI (migration 010 + 012)
- Migration 010 svuotata (era: 8 clienti finti + `setup_completed=true` che saltava il wizard)
- Migration 012 pulita (solo ALTER TABLE, no INSERT operatori demo)
- **DB produzione parte VUOTO** — wizard guida l'utente

### 3. OAuth Google RIMOSSO
- Credenziali erano placeholder → sempre errore 401 "invalid_client"
- Sostituito con guida in-app Gmail App Password (4 step con link diretto)

### 4. Wizard Semplificato (9 → 7 step)
- Rimosso step 8: Groq API key (Sara funziona via proxy, zero config)
- Rimosso step 9: TTS quality selection (auto-detect)
- Wizard: attivita → settore → orari → operatori → fatturazione → licenza → contratto firma

### 5. iMac DB Seed Completo
- 61 clienti, 106 appuntamenti, 59 incassi, 7 fatture, 5 fornitori
- 6 schede mediche, 4 parrucchiere, 3 fitness, 3 estetica, 3 veicoli
- Pronto per demo completa tutti i verticali

### 6. LemonSqueezy — Store NON attivato
- Identity Verification: **REJECTED** → deve essere rifatta
- Test mode bloccato finche non verificato
- Prodotto test €0 creato ma checkout in test mode
- **TODO**: rifare identity verification su LemonSqueezy

---

## DA FARE S103 — CTO MODE FULL

### BLOCCO 0: Deep Research CoVe 2026 — Direttiva CTO + Delivery Pipeline
- Lanciare 2+ subagenti research:
  - **Agente A**: Best practice delivery pipeline software desktop indie (Obsidian, Notion, Calibre, 1Password, Raycast) — come consegnano DMG/EXE post-acquisto, license activation, auto-update
  - **Agente B**: CTO playbook indie software — regole operative enterprise-grade, QA pre-release checklist, PMI user testing framework
- Output: proposta direttiva CTO per CLAUDE.md → founder approva → inserimento
- Output: architettura delivery pipeline completa (LemonSqueezy file hosting + email + license)

### BLOCCO 1: Test Completo Flusso Utente
- CTO testa DMG su MacBook (cancellare prima `~/Library/Application Support/com.fluxion.desktop/`)
- Wizard 7 step → Studio Medico Pro
- Verificare OGNI pagina funziona da zero (dashboard, clienti, calendario, servizi, operatori, fatture, cassa, fornitori, analytics, impostazioni)
- Voice Agent: verificare che sidecar si avvia (check `/tmp/fluxion-voice.log`)

### BLOCCO 2: LemonSqueezy Identity Verification
- Rifare verifica identita (documento + selfie)
- Una volta approvato → attivare live mode
- Upload DMG + MSI come file prodotto
- Configurare email post-acquisto con: download link + license key + guida installazione

### BLOCCO 3: Pagina "Come installare FLUXION"
- `https://fluxion-landing.pages.dev/installa`
- Screenshot macOS Gatekeeper + "Apri comunque"
- Screenshot Windows SmartScreen + "Esegui comunque"
- Box rassicurazione

### BLOCCO 4: Windows MSI Build
- Macchina Windows disponibile
- PyInstaller Windows + Tauri MSI (WiX)

---

## DIRETTIVE FONDATORE (NON NEGOZIABILI)

1. **CTO MODE** — porta soluzioni, non problemi. Anticipa. Proponi proattivamente.
2. **ZERO SUPPORTO MANUALE** — ogni feature deve funzionare senza telefonata
3. **MASSIMA SEMPLICITA** — utenti PMI "medio-bassi" tecnicamente
4. **DEEP RESEARCH PRIMA DI TOCCARE CLAUDE.md** — proponi, founder approva
5. **MAI riferimenti Anthropic/Claude** — zero nel codice, commit, UI
6. **SARA = SOLO DATI DB** — zero improvvisazione
7. **SEMPRE 1 nicchia** — una PMI = un'attivita
8. **TUTTO "FLUXION AI"** — mai esporre Groq/Cerebras/OpenRouter all'utente

---

## BUILD COMMANDS

```bash
# Full rebuild su iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
ssh imac "bash -l -c 'cd \"/Volumes/MacSSD - Dati/fluxion\" && npm run tauri build'"

# Codesign + DMG
ssh imac 'APP="/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/macos/Fluxion.app" && codesign --sign - --force "$APP/Contents/MacOS/voice-agent" && codesign --sign - --force "$APP/Contents/MacOS/tauri-app" && codesign --sign - --force --deep "$APP" && codesign --verify --deep --strict "$APP"'
ssh imac 'DMG="/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/dmg/Fluxion_1.0.0_x64.dmg" && APP="/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/macos/Fluxion.app" && rm -f "$DMG" && hdiutil create -volname "Fluxion" -srcfolder "$APP" -ov -format UDZO "$DMG"'

# Copia DMG su MacBook
scp imac:"/Volumes/MacSSD\ -\ Dati/fluxion/src-tauri/target/release/bundle/dmg/Fluxion_1.0.0_x64.dmg" releases/v1.0.0/

# Test fresh install (cancella DB dev prima)
rm -rf ~/Library/Application\ Support/com.fluxion.desktop/
open releases/v1.0.0/Fluxion_1.0.0_x64.dmg
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 103. CTO MODE FULL.
S102: Build macOS v2 completo (wizard 7 step, no mock data, no OAuth, no Groq key). DMG 71MB firmato pronto.
iMac DB seed completo (tutte le schede). LemonSqueezy identity verification da rifare (rejected).
BLOCCO 0: Deep research CoVe 2026 — direttiva CTO + delivery pipeline per CLAUDE.md (proporre, founder approva).
BLOCCO 1: Test completo flusso utente MacBook (cancellare DB dev prima).
BLOCCO 2: LemonSqueezy activation. BLOCCO 3: Pagina installazione. BLOCCO 4: Windows MSI.
Pipeline iMac ATTIVA. iMac sincronizzato + DB seed completo.
```
