# RUNBOOK P2 — Build Windows MSI (founder Windows env)

> **Tempo stimato totale**: 2.5-3h prima volta (setup toolchain ~90 min) | 30 min run successivi
> **Prerequisito hardware**: Windows 10/11 64-bit, 16GB RAM consigliati (8GB minimo), 25GB disco libero
> **Owner**: Gianluca Di Stasi
> **Esito atteso**: file `Fluxion_1.0.1_x64_it-IT.msi` (~150-250MB) testato su Win10/11 → P0 launch blocker rimosso
> **Riferimento**: `.claude/rules/architecture-distribution.md` § Code Signing / Compatibilita Minima

---

## 🎯 Cosa fa questo runbook

Tauri 2.x build su macOS NON cross-compila per Windows. Il codice Rust + il sidecar PyInstaller voice-agent vanno entrambi compilati **nativamente su Windows**. Questo runbook copre:

1. Setup toolchain Windows da zero
2. Clone repo + dependencies
3. Build sidecar PyInstaller `voice-agent-x86_64-pc-windows-msvc.exe`
4. Build Tauri MSI con WiX (target `it-IT`)
5. Smoke test installer su Win10/11
6. SmartScreen mitigation guide per distribuzione

**Mercato target**: ~80% PMI Italia desktop = Windows. Senza MSI il prodotto non è vendibile a 4 clienti su 5.

---

## ⚡ Quick Start (TL;DR — già fatto il setup)

Se sei già passato dal setup toolchain una volta (vedi `docs/launch/win-build-state.md` se esiste):

```powershell
# PowerShell come Administrator
cd C:\dev\fluxion
git pull origin master

# 1. Sidecar voice-agent.exe
cd voice-agent
.\venv\Scripts\Activate.ps1
pyinstaller voice-agent.spec
copy dist\voice-agent.exe ..\src-tauri\binaries\voice-agent-x86_64-pc-windows-msvc.exe

# 2. Build MSI
cd ..
npm install
npm run tauri build -- --bundles msi

# Output: src-tauri\target\release\bundle\msi\Fluxion_1.0.1_x64_it-IT.msi
```

Se è la prima volta → continua sotto.

---

## 🛠 Step 0 — Setup toolchain Windows (~90 min, una sola volta)

### 0.1 Visual Studio Build Tools 2022

Tauri Rust su Win richiede MSVC linker.

```powershell
# Scarica da: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Run installer → seleziona workload "Desktop development with C++"
# Componenti aggiuntivi richiesti:
#   - MSVC v143 - VS 2022 C++ x64/x86 build tools
#   - Windows 11 SDK (10.0.22621 o successivo)
#   - C++ CMake tools for Windows
```

**Verifica**:
```powershell
where cl.exe
# Atteso: C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.X.X\bin\Hostx64\x64\cl.exe
```

### 0.2 Rust stable

```powershell
# Scarica e lancia: https://win.rustup.rs/x86_64
# Default 1 (Proceed with installation)
# Riavvia PowerShell dopo install

rustup default stable
rustc --version
# Atteso: rustc 1.7X.X (stable)

# Aggiungi target windows-msvc (di default già presente)
rustup target list --installed
# Atteso: x86_64-pc-windows-msvc
```

### 0.3 Node.js 20 LTS

```powershell
# Scarica MSI: https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi
# Install → riavvia PowerShell

node --version
# Atteso: v20.X.X
npm --version
# Atteso: 10.X.X
```

### 0.4 Python 3.11 (per voice-agent sidecar)

```powershell
# Scarica: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
# ⚠️ DURANTE INSTALL: tick "Add python.exe to PATH" + "Install for all users"

python --version
# Atteso: Python 3.11.9
pip --version
# Atteso: pip 24.X.X
```

### 0.5 WebView2 Runtime

Tauri usa WebView2 (Edge Chromium) per il frontend. Su Win11 è già preinstallato. Su Win10:

```powershell
# Scarica Evergreen Bootstrapper: https://developer.microsoft.com/microsoft-edge/webview2/
# Installa silenziosamente: WebView2 si auto-aggiorna
```

L'MSI di Fluxion include `embedBootstrapper` (`tauri.conf.json` riga 51) → l'installer scarica WebView2 se mancante. Per build locale è comunque consigliato averlo.

### 0.6 WiX Toolset (per build MSI)

Tauri scarica WiX 3.x automaticamente al primo build. Forzalo:

```powershell
# Lancia build dummy che fallirà ma scaricherà WiX
mkdir C:\dev\fluxion-bootstrap
cd C:\dev\fluxion-bootstrap
# … (salta — al primo `npm run tauri build` verrà scaricato in %LOCALAPPDATA%\tauri\WixTools)
```

### 0.7 Git

```powershell
# Scarica: https://git-scm.com/download/win
# Install con default → "Use Git from the Windows Command Prompt"

git --version
```

---

## 📥 Step 1 — Clone repo + branch

```powershell
mkdir C:\dev
cd C:\dev
git clone https://github.com/lukeeterna/fluxion-desktop.git fluxion
cd fluxion
git checkout master
git log --oneline -5
# Verifica ultimo commit corrisponde a quello atteso (es. c5e579b)
```

---

## 🐍 Step 2 — Build sidecar voice-agent.exe (~25 min prima volta)

### 2.1 Setup venv Python

```powershell
cd C:\dev\fluxion\voice-agent

python -m venv venv
.\venv\Scripts\Activate.ps1
# Se errore "execution policy": Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-windows.txt
pip install pyinstaller==6.19.0
```

⚠️ **Pin setuptools<70** se PyInstaller fallisce con `_by_version` error (regression noto S194):
```powershell
pip install "setuptools<70" --force-reinstall
```

### 2.2 Verifica modelli Piper presenti

Il bundle PyInstaller richiede `models/tts/it_IT-paola-medium.onnx` (~58MB). Se assente:

```powershell
mkdir models\tts -Force
# Scarica modello Paola Italian medium da HuggingFace
curl -L -o models\tts\it_IT-paola-medium.onnx `
  https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx
curl -L -o models\tts\it_IT-paola-medium.onnx.json `
  https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json
```

Verifica:
```powershell
dir models\tts
# Atteso: it_IT-paola-medium.onnx (~58MB) + .json (~4KB)
```

### 2.3 Build PyInstaller

```powershell
pyinstaller voice-agent.spec --noconfirm
# Output: dist\voice-agent.exe (~200-250MB)
```

### 2.4 Smoke test sidecar

```powershell
dist\voice-agent.exe --version
# Atteso: FLUXION Voice Agent 2.1.0 (python 3.11.X, win32)

dist\voice-agent.exe --health-check
# Atteso: health check OK (no esecuzione server)

# Test HTTP server (porta isolata, NON 3002 per non interferire)
dist\voice-agent.exe --port 3099 --host 127.0.0.1
# In altro PowerShell:
curl http://127.0.0.1:3099/health
# Atteso: {"status": "ok", "service": "FLUXION Voice Agent Enterprise", ...}
# Ctrl+C per stop
```

### 2.5 Copia nel sidecar dir Tauri

```powershell
cd C:\dev\fluxion
mkdir src-tauri\binaries -Force
copy voice-agent\dist\voice-agent.exe src-tauri\binaries\voice-agent-x86_64-pc-windows-msvc.exe
dir src-tauri\binaries
# Atteso: voice-agent-x86_64-pc-windows-msvc.exe
```

⚠️ **Naming critico**: Tauri cerca il sidecar con suffix `-x86_64-pc-windows-msvc.exe` esatto. Vedi `tauri.conf.json:30 externalBin`.

---

## 🦀 Step 3 — Build Tauri MSI (~20 min prima volta)

### 3.1 Frontend dependencies

```powershell
cd C:\dev\fluxion
npm install
# ~3 min, ~700 packages
```

### 3.2 Type check (sanity)

```powershell
npm run type-check
# Atteso: 0 errori TypeScript
```

### 3.3 Build MSI

```powershell
npm run tauri build -- --bundles msi
```

Il flag `--bundles msi` forza WiX (default config `tauri.conf.json:47` ha `targets: ["dmg", "app", "nsis"]` — NSIS è il default Windows, MSI è opt-in via WiX).

**Cosa succede sotto**:
1. `npm run build` → Vite compila React in `dist/`
2. `cargo build --release` → Rust compila `fluxion.exe` (~5 min cold cache)
3. WiX assembla MSI con sidecar + frontend + voice-agent.exe + WebView2 bootstrapper
4. Output: `src-tauri\target\release\bundle\msi\Fluxion_1.0.1_x64_it-IT.msi`

**Errori comuni**:

| Errore | Causa | Fix |
|--------|-------|-----|
| `cargo: linker 'link.exe' not found` | MSVC Build Tools missing | torna a Step 0.1 |
| `external binary not found: voice-agent-x86_64-pc-windows-msvc.exe` | Sidecar non copiato in src-tauri\binaries\ | Step 2.5 |
| `WiX Tools not found, downloading…` | Primo run, è normale | Aspetta download ~50MB |
| `LGHT0204: ICE...` (WiX validation) | Conflict con previous install | reboot Windows, retry |
| `error: linking with link.exe failed: code 1561` | OOM linker | chiudi tutto, +8GB RAM o `set CARGO_BUILD_JOBS=2` |

### 3.4 Verifica output

```powershell
dir src-tauri\target\release\bundle\msi
# Atteso: Fluxion_1.0.1_x64_it-IT.msi (~150-250MB)

# Hash per release notes
certutil -hashfile src-tauri\target\release\bundle\msi\Fluxion_1.0.1_x64_it-IT.msi SHA256
```

---

## 🧪 Step 4 — Smoke test installer

### 4.1 Test su STESSA Windows machine (build host)

```powershell
# Lancia installer
.\src-tauri\target\release\bundle\msi\Fluxion_1.0.1_x64_it-IT.msi
```

Verifica:
1. ✅ Installer in italiano (UI lingua = it-IT)
2. ✅ Installa in `C:\Program Files\Fluxion\` (default WiX 64-bit)
3. ✅ Crea shortcut Start Menu + Desktop
4. ✅ Lancia app dopo install
5. ✅ Splash + main window appare
6. ✅ Voice agent sidecar parte (verifica `tasklist | findstr voice-agent.exe`)

**Acceptance criteria**:
- App lancia in <5 sec
- Crea DB SQLite in `%LOCALAPPDATA%\com.fluxion.desktop\`
- HTTP Bridge porta 3001 risponde: `curl http://127.0.0.1:3001/health`
- Voice agent porta 3002 risponde (mic potrebbe non funzionare su VM, OK)

### 4.2 Test su VM Windows pulita (CRITICO)

Builder host può avere dipendenze "sporche" (Python global, Rust, VS Build Tools). Test su Win10/11 vanilla è il vero gate.

Opzioni VM:
- **VirtualBox** (gratis): scarica Win10 evaluation https://www.microsoft.com/evalcenter/
- **UTM** (gratis Mac, già menzionato in MEMORY S184 — `UTM Win11 8GB`)
- **Hyper-V** (Win Pro built-in)

Steps:
1. VM pulita, NO Python/Node/Rust/VS installati
2. Copia MSI nel VM (drag-drop o shared folder)
3. Lancia installer → verifica SmartScreen mostra warning (atteso, unsigned)
4. Click "More info" → "Run anyway"
5. Install + lancia app
6. Verifica funzionalità base: Setup Wizard, crea cliente, naviga calendario
7. Verifica voice agent: `curl http://127.0.0.1:3002/health` da PowerShell VM

**Criterio PASS**: app installa + lancia + crea cliente senza errori VM Win10/11 pulita.

### 4.3 Test su VM senza WebView2

WebView2 dovrebbe essere auto-installato dall'MSI tramite bootstrapper. Per verificare:

```powershell
# Su VM pulita PRIMA di lanciare MSI
Get-AppxPackage *WebView2* 
# Se vuoto: WebView2 manca

# Lancia MSI Fluxion
# Verifica DURANTE install: download WebView2 (~150MB) parte automatico

# Dopo install verifica
Get-AppxPackage *WebView2*
# Atteso: Microsoft.WebView2 presente
```

---

## 🛡 Step 5 — SmartScreen mitigation (distribuzione unsigned)

Fluxion MSI è **unsigned** (vincolo ZERO COSTI — code signing cert ~€300/anno). SmartScreen mostrerà warning al primo download.

### 5.1 Pagina istruzioni utente

Crea/aggiorna `landing/install-windows.html` con guida visuale:

```
1. Scarica Fluxion_1.0.1_x64_it-IT.msi
2. Doppio click → SmartScreen "Windows ha protetto il PC"
3. Click "Ulteriori informazioni"
4. Click "Esegui comunque"
5. Procedi con installazione
```

Include screenshot (cattura da VM test).

### 5.2 Mitigazione reputazione SmartScreen

SmartScreen reputation accumula nel tempo. Per ridurre friction:

- Pubblica MSI su GitHub Releases (URL stabile + HTTPS)
- NON rinominare file tra release diverse (mantieni schema `Fluxion_{version}_x64_it-IT.msi`)
- Hash SHA256 in release notes
- Dopo ~100-500 download SmartScreen "fiducia" aumenta

### 5.3 Alternativa post-revenue: code signing

Quando revenue >€2k/mese:
- DigiCert / Sectigo EV cert ~€300-500/anno
- Cert su HSM USB token (richiesto da 2024)
- Firma con `signtool.exe sign /fd SHA256 /a Fluxion.msi`
- SmartScreen warning sparisce immediatamente

---

## 📤 Step 6 — Distribuzione

### 6.1 Upload GitHub Release

```powershell
# Crea release v1.0.1-win
gh release create v1.0.1-win `
  --title "Fluxion 1.0.1 — Windows MSI" `
  --notes-file CHANGELOG.md `
  src-tauri\target\release\bundle\msi\Fluxion_1.0.1_x64_it-IT.msi
```

### 6.2 Aggiorna landing page

In `landing/index.html` aggiungi/aggiorna sezione download:
```html
<a href="https://github.com/lukeeterna/fluxion-desktop/releases/download/v1.0.1-win/Fluxion_1.0.1_x64_it-IT.msi">
  Scarica per Windows (10/11 64-bit)
</a>
```

### 6.3 Updater endpoint

Già configurato `tauri.conf.json:65 updater.endpoints`. Verifica `latest.json` su release punta a versione corretta.

---

## ✅ Definizione di PASS

P0 Win MSI è CHIUSO quando:

- [ ] `Fluxion_1.0.1_x64_it-IT.msi` esiste in `src-tauri\target\release\bundle\msi\`
- [ ] Smoke test build host: install + lancia app PASS
- [ ] Smoke test VM Win10 vanilla: install + lancia app PASS
- [ ] Smoke test VM Win11 vanilla: install + lancia app PASS
- [ ] HTTP Bridge 3001 + voice agent 3002 rispondono dentro app
- [ ] DB SQLite creato in `%LOCALAPPDATA%\com.fluxion.desktop\`
- [ ] SHA256 hash documentato in release notes
- [ ] Uploaded GitHub Release v1.0.1-win
- [ ] Landing page link Windows aggiornato

---

## 🚨 Troubleshooting esteso

### Problema: `cargo build` lento (>15 min)

- Disattiva antivirus su `C:\dev\fluxion\target\` (Windows Defender real-time scan rallenta 3-5x)
- Set incremental build: già attivo per Cargo default
- Solo prima compilation è lenta (cold cache). Successive ~2 min.

### Problema: MSI install crash con "0x80070005"

Permessi insufficienti. Run installer come Administrator.

### Problema: voice-agent.exe non parte dentro Fluxion installato

Verifica path sidecar atteso:
```powershell
dir "C:\Program Files\Fluxion\voice-agent-x86_64-pc-windows-msvc.exe"
```

Se assente → MSI build ha skippato externalBin → check `tauri.conf.json:30` + ripeti Step 2.5.

### Problema: STT/TTS non funziona su VM

Audio devices in VM sono virtuali. STT richiede mic reale → test E2E voce reale fai su HW fisico Win, non VM.

### Problema: WebView2 non si installa automaticamente

Modifica `tauri.conf.json:51 webviewInstallMode` → `"type": "downloadBootstrapper"` (download a runtime invece di embed) + rebuild.

---

## ⏭️ Next session prompt post-build

```
Win MSI build PASS — Fluxion_1.0.1_x64_it-IT.msi distribuito su GitHub Release v1.0.1-win.
SHA256: <hash>
Tested: build host + VM Win10 vanilla + VM Win11 vanilla.
Aggiornare ROADMAP_REMAINING.md + HANDOFF.md + PRE-LAUNCH-AUDIT.md
(categoria Build/Distribution → PASS).
P0 launch blocker rimanenti: nessuno se Sara test live già PASS (RUNBOOK-P1).
Gate 3 GREEN → LAUNCH READY.
```

---

## 📚 Riferimenti

- Tauri 2 Windows guide: https://v2.tauri.app/distribute/windows-installer/
- PyInstaller Windows: https://pyinstaller.org/en/stable/usage.html#windows
- WiX Toolset 3.x: https://wixtoolset.org/docs/v3/
- SmartScreen mitigation: `.claude/rules/architecture-distribution.md` § Code Signing
- Spec PyInstaller cross-platform: `voice-agent/voice-agent.spec` (commenti header)
