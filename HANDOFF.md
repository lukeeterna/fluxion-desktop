# FLUXION — Handoff Sessione 101 → 102 (2026-03-20)

## CTO MANDATE — NON NEGOZIABILE
> **"Basta polishing Sara — il prodotto è pronto. Ora PACKAGING e distribuzione. Zero supporto manuale, helpdesk online adeguato."**

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
Branch: master | HEAD: 18de7d8 (pushato, iMac DA sincronizzare)
type-check: 0 errori
Ultimo commit: fix(email) — rimosso OAuth broken, semplificata Gmail App Password
```

---

## COMPLETATO SESSIONE 101

### 1. F17 macOS Packaging — PRIMO BUILD COMPLETO
- **PyInstaller sidecar**: 60MB Mach-O x86_64, build su iMac Python 3.9 + PyInstaller 6.19
- **Tauri build**: `Fluxion.app` (76MB) + `Fluxion_1.0.0_x64.dmg` (71MB)
- **Ad-hoc codesign**: firmato + verificato (`codesign --verify --deep --strict` OK)
- **DMG integro**: `hdiutil verify` VALID, SHA256: `b545b8de260224c31ec87e70dec3a844f4415ded324ba3fd57da1cdc87f695eb`
- **App lanciata su iMac**: processo attivo, si avvia correttamente
- **Sidecar testato**: `voice-agent --help` funziona, VAD ONNX disponibile

### 2. File creati/modificati
- `entitlements.plist` — macOS entitlements (audio, network, JIT, unsigned lib)
- `src-tauri/tauri.conf.json` — DMG+App targets, WiX per Windows (era NSIS)
- `scripts/build-macos.sh` — script orchestrazione build completo
- `voice-agent/requirements-prod.txt` — deps leggere per PyInstaller
- `src-tauri/binaries/voice-agent-x86_64-apple-darwin` — placeholder (reale solo su iMac)

### 3. Deps installate su iMac per build
- `python-Levenshtein`, `dateparser` installati su Python 3.9 system

### 4. Artefatti build su iMac
- `/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/macos/Fluxion.app`
- `/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/dmg/Fluxion_1.0.0_x64.dmg`

### 5. DMG copiato su MacBook
- `/Volumes/MontereyT7/FLUXION/releases/v1.0.0/Fluxion_1.0.0_x64.dmg`
- **Nota**: DMG va ricostruito dopo fix email (commit 18de7d8)

### 6. OAuth Google RIMOSSO — Gmail App Password (commit 18de7d8)
- Credenziali OAuth erano placeholder (`YOUR_GOOGLE_CLIENT_ID`) → sempre errore 401
- Rimosso bottone OAuth, aggiunta guida in-app 4 step per Gmail App Password
- Link diretto a `myaccount.google.com/apppasswords`
- Rimosso OAuth da Fornitori.tsx

### 7. Decisione architetturale: Onboarding Zero-Friction
- **Sara AI**: funziona via FLUXION Proxy — utente NON configura nulla
- **Groq/OpenRouter/Cerebras**: MAI visibili all'utente, tutto è "FLUXION AI"
- **Wizard**: rimuovere step Groq key — solo: attività, settore, orari, operatori
- **Email**: Gmail App Password (opzionale, guida in-app)
- **WhatsApp**: wa.me 1-tap, zero config
- **Memory**: `memory/project_onboarding_zero_friction.md`

---

## DA FARE S102

### Priorità 0: Wizard Semplificazione (BLOCCANTE)
- Rimuovere step Groq API key dal wizard (Sara usa proxy, non serve)
- Tutti i provider LLM → label "FLUXION AI" (mai Groq/Cerebras/OpenRouter)
- Wizard deve essere: attività → settore → orari → operatori → FINE
- Email setup opzionale, spostato in Impostazioni (non nel wizard)

### Priorità 1: Rebuild macOS + Test Installazione
- Sincronizzare iMac (git pull — ha il fix email)
- Rebuild: `bash scripts/build-macos.sh`
- Nuovo DMG con email fix
- CTO testa su MacBook: DMG → drag → "Apri comunque" → app OK
- **Nota**: cancellare `~/Library/Application Support/com.fluxion.desktop/` prima del test per simulare primo avvio

### Priorità 2: Pagina "Come installare FLUXION" (landing)
- URL: `https://fluxion-landing.pages.dev/installa`
- Screenshot macOS: Gatekeeper warning + "Apri comunque"
- Screenshot Windows: SmartScreen + "Esegui comunque"
- Box rassicurazione "Perché vedo questo avviso?"
- Disclaimer: "Requisiti: Gmail configurato sul PC per notifiche email"
- Research: `.claude/cache/agents/distribution-no-signing-research-2026.md` (sezione 3)

### Priorità 3: Windows MSI Build
- CTO ha macchina Windows disponibile
- GitHub Actions configurabile per Windows build
- Serve: PyInstaller Windows build + Tauri MSI (WiX)
- `tauri.conf.json` già configurato per WiX `it-IT`

### Priorità 4: Audit UI/UX Completo
- Menu dropdown, layout sballati, UX issues
- Lanciare ui-designer subagent per scan tutte le pagine

### Priorità 5: Helpdesk Online
- Struttura self-service (FAQ, guide, troubleshooting)

---

## DIRETTIVE CTO (NON NEGOZIABILI)

1. **STOP POLISHING SARA** — il prodotto è pronto, ora packaging
2. **ZERO SUPPORTO MANUALE** — helpdesk online self-service obbligatorio
3. **F17 È IL BLOCKER** — senza installer, FLUXION non esiste per i clienti
4. **SEMPRE code reviewer** dopo ogni implementazione significativa
5. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare
6. **SARA = SOLO DATI DB** — zero improvvisazione
7. **SEMPRE 1 nicchia** — una PMI = un'attività

---

## BUILD COMMANDS (Referenza)

```bash
# Rebuild completo su iMac (SSH)
ssh imac "bash -l -c 'cd \"/Volumes/MacSSD - Dati/fluxion\" && bash scripts/build-macos.sh'"

# Solo sidecar rebuild
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m PyInstaller --clean voice-agent.spec"

# Solo Tauri rebuild (dopo sidecar)
ssh imac "bash -l -c 'cd \"/Volumes/MacSSD - Dati/fluxion\" && npm run tauri build'"

# Codesign + DMG
ssh imac 'APP="/Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/bundle/macos/Fluxion.app" && codesign --sign - --force --deep "$APP" && codesign --verify --deep --strict "$APP"'

# Copia DMG su MacBook
scp imac:"/Volumes/MacSSD\ -\ Dati/fluxion/src-tauri/target/release/bundle/dmg/Fluxion_1.0.0_x64.dmg" releases/v1.0.0/
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 102. S101: PRIMO BUILD macOS COMPLETATO (76MB app + 71MB DMG, codesign OK) + OAuth rimosso + Gmail App Password semplificato.
Decisione S101: ONBOARDING ZERO-FRICTION — Sara via proxy (zero config), rimuovere Groq key dal wizard, tutto "FLUXION AI" mai nomi provider.
Priorità S102: (0) Semplificare wizard — rimuovere step Groq, (1) Rebuild macOS con fix email + test su Mac pulito, (2) Pagina installazione landing, (3) Windows MSI build (macchina disponibile).
PRIMA DI TESTARE: cancellare ~/Library/Application Support/com.fluxion.desktop/ per simulare primo avvio.
Pipeline iMac ATTIVA (127.0.0.1:3002). iMac DA sincronizzare (git pull).
```
