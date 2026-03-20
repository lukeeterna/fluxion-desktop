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
Branch: master | HEAD: 699e863 (pushato + iMac sincronizzato)
type-check: 0 errori
iMac: sincronizzato
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
- CTO deve testare: aprire DMG → drag in Applicazioni → primo avvio → "Apri comunque"

---

## DA FARE S102

### Priorità 0: Test Installazione Mac "Pulito" (CTO test manuale)
- CTO testa DMG su MacBook (no Rust, simula utente reale)
- Apertura DMG → drag Fluxion.app in /Applications → primo avvio
- Verificare: Gatekeeper warning → Privacy > "Apri comunque" → app si apre
- Verificare: sidecar voice-agent si avvia dentro l'app
- **Se problemi**: riportare in S102 per fix

### Priorità 1: Pagina "Come installare FLUXION" (landing)
- URL: `https://fluxion-landing.pages.dev/installa`
- Screenshot macOS: Gatekeeper warning + "Apri comunque"
- Screenshot Windows: SmartScreen + "Esegui comunque"
- Box rassicurazione "Perché vedo questo avviso?"
- Research: `.claude/cache/agents/distribution-no-signing-research-2026.md` (sezione 3)

### Priorità 2: Windows MSI Build
- CTO ha macchina Windows disponibile
- GitHub Actions configurabile per Windows build
- Serve: PyInstaller Windows build + Tauri MSI (WiX)
- `tauri.conf.json` già configurato per WiX `it-IT`

### Priorità 3: Audit UI/UX Completo
- Menu dropdown, layout sballati, UX issues
- Lanciare ui-designer subagent per scan tutte le pagine

### Priorità 4: Helpdesk Online
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
Leggi HANDOFF.md. Sessione 102. S101: PRIMO BUILD macOS COMPLETATO — Fluxion.app 76MB + DMG 71MB, ad-hoc codesign OK.
CTO ha testato DMG su MacBook: [RIPORTARE RISULTATO TEST QUI].
Priorità S102: (1) Pagina "Come installare FLUXION" per landing, (2) Windows MSI build (macchina Windows disponibile), (3) Audit UI/UX.
Pipeline iMac ATTIVA (127.0.0.1:3002). iMac sincronizzato.
```
