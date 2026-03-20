# FLUXION — Handoff Sessione 103 → 104 (2026-03-20)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni. MAI presentare problemi senza soluzioni. MAI fare il compitino."**

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
Branch: master | HEAD: cd219da (da committare: CLAUDE.md + research files)
type-check: 0 errori
iMac: sincronizzato, DB seed completo (tutte le schede)
```

---

## COMPLETATO SESSIONE 103

### 1. CLAUDE.md — 2 Guardrail + Cleanup
- **GUARDRAIL 1: ZERO COSTI** — tutto deve costare €0, trova il modo
- **GUARDRAIL 2: ENTERPRISE GRADE** — gold standard mondiale, trova il modo
- Rimosso vecchio blocco verbose "Enterprise Grade"
- Code signing aggiornato: ad-hoc gratuito (no Apple Dev $99, no Azure $120)
- LemonSqueezy → Stripe Checkout diretto
- Aggiunta sezione pagamento: Stripe + Ed25519 + Resend free

### 2. Deep Research CoVe 2026 (2 subagenti)
- `.claude/cache/agents/delivery-pipeline-indie-research-2026.md` — analisi 8 software (Obsidian, Raycast, Sublime Text, 1Password, etc.)
- `.claude/cache/agents/cto-playbook-indie-2026.md` — QA checklist, user testing PMI, go-to-market, post-launch ops

### 3. Tier DEFINITIVO (memorizzato)
- **NO download gratuito** — il cliente PAGA prima di scaricare
- **Base €497**: gestionale + WA + Sara 30gg trial + proposta EHIWEB
- **Pro €897**: 1 nicchia (micro-categoria: es. Dentista, Barbiere, Officina) + Sara per sempre
- **SEMPRE 1 sola nicchia** = micro-categoria (17 disponibili in `setup.ts`)
- **LemonSqueezy RIMOSSO** — sostituito con Stripe Checkout diretto (1.5% EU, zero piattaforma)
- Durante trial 30gg: proporre EHIWEB VoIP con copy eloquente + link attivazione semplice

### 4. Decisioni Confermate
- Ed25519 license system: già implementato (831 righe Rust), sicuro, offline-first
- Anti-piracy: nag screen + feature gating (modello Sublime Text), MAI blocco totale
- CF Worker `TRIAL_DAYS` = 30 (invariato)
- GitHub Releases per hosting binari (CDN globale, gratuito)
- Resend free tier per email delivery licenze (3000/mese)

---

## DA FARE S104

### BLOCCO 1: Commit + Sync
- Committare CLAUDE.md + research files
- Sync iMac

### BLOCCO 2: Test Completo Flusso Utente
- CTO testa DMG su MacBook (cancellare prima `~/Library/Application Support/com.fluxion.desktop/`)
- Wizard 7 step → Studio Medico Pro
- Verificare OGNI pagina funziona da zero
- Voice Agent: verificare sidecar si avvia

### BLOCCO 3: Stripe Checkout Setup
- Creare account Stripe (fondatore)
- Creare 2 prodotti: Base €497, Pro €897
- Aggiungere webhook route al CF Worker (`/webhook/stripe`)
- Aggiungere ED25519_PRIVATE_KEY come secret CF Worker
- Aggiungere RESEND_API_KEY come secret CF Worker
- Sostituire checkout URLs LemonSqueezy → Stripe in tutto il codebase

### BLOCCO 4: EHIWEB VoIP Proposal in-app
- Copy eloquente durante trial Sara (proposta VoIP)
- Link attivazione semplice EHIWEB
- Spiegazione chiara: "Sara risponde al telefono anche quando non ci sei"

### BLOCCO 5: Pagina "Come installare FLUXION"
- `https://fluxion-landing.pages.dev/installa`
- Screenshot macOS Gatekeeper + "Apri comunque"
- Screenshot Windows SmartScreen + "Esegui comunque"

### BLOCCO 6: Windows MSI Build

---

## DIRETTIVE FONDATORE (NON NEGOZIABILI)

1. **CTO MODE** — porta soluzioni, non problemi
2. **ZERO COSTI** — tutto €0, trova il modo
3. **ENTERPRISE GRADE** — gold standard mondiale
4. **ZERO SUPPORTO MANUALE** — ogni feature funziona senza telefonata
5. **MASSIMA SEMPLICITÀ** — utenti PMI "medio-bassi" tecnicamente
6. **MAI riferimenti Anthropic/Claude** — zero nel codice, commit, UI
7. **SARA = SOLO DATI DB** — zero improvvisazione
8. **SEMPRE 1 nicchia** (micro-categoria) — una PMI = un'attività
9. **TUTTO "FLUXION AI"** — mai esporre Groq/Cerebras all'utente
10. **NO download gratuito** — il cliente paga prima di scaricare

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
Leggi HANDOFF.md. Sessione 104. CTO MODE FULL.
S103: CLAUDE.md aggiornato (2 guardrail: ZERO COSTI + ENTERPRISE GRADE). LemonSqueezy RIMOSSO → Stripe Checkout.
Tier DEFINITIVO: Base €497 (gestionale+WA+Sara 30gg trial+proposta EHIWEB) / Pro €897 (1 nicchia+Sara sempre). NO download gratuito.
Research completata: delivery pipeline + CTO playbook (in .claude/cache/agents/).
BLOCCO 1: Commit + sync. BLOCCO 2: Test fresh install DMG. BLOCCO 3: Stripe setup. BLOCCO 4: EHIWEB proposal in-app.
Pipeline iMac ATTIVA. iMac sincronizzato + DB seed completo.
```
