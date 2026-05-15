# FLUXION — PRE-LAUNCH AUDIT 6 CATEGORIE (S245)

**Generato**: 2026-05-15
**Repo**: master `30bd1f8`
**Mandato founder S244**: "se devo partire deve essere tutto pronto e pienamente funzionante"
**Vincolo**: NO MVP, NO lancio parziale. Si shippa solo con tutti P0 verdi.

---

## CATEGORIA 1 — BUILD / DISTRIBUTION

### Tabella riassuntiva

| Feature/Aspetto | Stato | Evidence (file:line OR comando) | P0/P1/P2 | Effort |
|-----------------|-------|----------------------------------|----------|--------|
| macOS DMG ad-hoc signed | ⚠️ PARZIALE | `tauri.conf.json:32` `signingIdentity=null` (ad-hoc OK) + `bundle.targets=["dmg","app","nsis"]`. v1.0.0 DMG presente (74MB), v1.0.1 ZERO assets. | **P0** | 2-3h (re-trigger pipeline + asset attach) |
| macOS PKG installer | ❌ ASSENTE | Solo DMG configurato. `bundle.targets` NON include "pkg". v1.0.0 ha `.pkg` (71MB) ma generato fuori pipeline (manuale). | P1 | 2h (script PKG + integrazione CI) |
| Windows MSI/NSIS | ⚠️ PARZIALE | `bundle.targets` include "nsis" + `installer-hooks.nsh` (4907 byte) presente. NSIS lang IT+EN. **MSI NON configurato** (solo NSIS .exe). | **P0** | 3-4h (aggiungere wix MSI target + test signed) |
| Universal Binary (Intel+arm64) | ❌ NO | CI matrix `release-full.yml:36-43` = SOLO `macos-14` (arm64). Intel macos-13 escluso ("runner queue persistente"). Nessun `lipo` UB step. v1.0.0 ha solo `x64.dmg`. | **P0** | 4-6h (riabilitare macos-13 OR fare UB con lipo su iMac) |
| Auto-updater endpoint live | 🔴 **BROKEN** | `curl https://github.com/lukeeterna/fluxion-desktop/releases/latest/download/latest.json` → **HTTP 404**. `tauri.conf.json:71-77` punta a quell'URL ma `latest.json` mai pubblicato. | **P0** | 1h (generare + upload latest.json a v1.0.1) |
| Auto-updater signing key | 🔴 **DISABLED** | `release-full.yml:294-296` commenti: "TAURI_SIGNING_PRIVATE_KEY_PASSWORD secret mismatch — Auto-update infrastructure DISABILITATA temporaneamente". `createUpdaterArtifacts:false` in tauri.conf. Pubkey statica `RWRqEGaKs2CWiWHG...` ma firma assente. | **P0** | 1h founder action: rigenerare key `tauri signer generate` + secrets GH |
| Auto-updater client | ✅ OK | `src/hooks/use-updater.ts` + `src/components/updater/UpdateDialog.tsx` + plugin Rust `lib.rs:568`. Implementazione completa lato app. | — | — |
| Sidecar Voice Agent bundled | 🔴 **PLACEHOLDER** | `src-tauri/binaries/voice-agent-x86_64-apple-darwin` = shell script di 296 byte: `echo "voice-agent placeholder — use Python source in development"; exit 1`. Manca anche arm64 + windows binari. | **P0** | 2-3h per target (build PyInstaller su iMac + Win runner) |
| PyInstaller spec ufficiale | ✅ OK | `voice-agent/voice-agent.spec` esiste, ben strutturato (datas piper/silero_vad, espeak-ng-data inclusi). CI usa CLI inline invece dello spec (tech debt). | P1 | 30min (CI usare `.spec`) |
| Version checking client | ✅ OK (logica), 🔴 endpoint | `use-updater.ts:7` chiama `check()` plugin-updater che colpisce endpoint 404 → fallirà silente. | **P0** | parte di fix endpoint sopra |
| Version sync 3 file | 🔴 **MISMATCH** | `package.json:3 version=1.0.1` / `src-tauri/tauri.conf.json:4 version=1.0.1` / `src-tauri/Cargo.toml:3 version=1.0.0` → Cargo è 1.0.0 mentre Tauri 1.0.1 ⇒ binary `CARGO_PKG_VERSION=1.0.0` ≠ `appVersion`. | **P0** | 5min (bump Cargo.toml a 1.0.1) |
| macOS Gatekeeper mitigation page | ✅ OK | `landing/come-installare.html` (esiste, completa con FAQ + VirusTotal link + Obsidian/Calibre social proof) + `scripts/install/setup-mac.command` rimuove xattr `com.apple.quarantine`. | — | — |
| Windows SmartScreen mitigation | ✅ OK | `scripts/install/setup-win.bat` add Defender exclusion + remove MotW + firewall loopback. Distribuzione separata via GH Releases (NON nel MSI). | P1 | 1h (auto-include in MSI installer-hooks.nsh) |
| Entitlements macOS | ✅ OK | `src-tauri/entitlements.plist`: audio-input, network client/server, files RW, allow-jit, allow-unsigned-executable-memory, disable-library-validation, automation. Coerente con sidecar Python. | — | — |
| Compatibility minima | ⚠️ DRIFT | `tauri.conf.json:33 minimumSystemVersion=10.15` (Catalina). CLAUDE.md `architecture-distribution.md` dichiara **macOS 12+**. Win10+ non vincolato lato MSI. | P1 | 5min (allineare a 12.0) |
| Build script iMac | ⚠️ BROKEN | `scripts/build-on-imac.sh:25 IMAC_IP="192.168.1.7"` ma MEMORY.md attuale = **192.168.1.2** (DHCP fluttua .2/.12). Script chiama `./build-fluxion.sh` su iMac che probabilmente non esiste. | P1 | 30min (env var IMAC_IP + verifica `build-fluxion.sh`) |
| Pipeline CI full release | ⚠️ PARZIALE | `.github/workflows/release-full.yml` 600 righe, job 1-7 (setup→va→tauri→integration→manifest→audit→summary). Linux escluso da bundle (`tech debt #3`). macos-13 escluso. Trigger tag `v*.*.*` OK. | P1 | — (gap = UB già P0 sopra) |
| Distribuzione zero-cost | ✅ OK | CF Pages (`fluxion-landing.pages.dev`) + GitHub Releases gratis. Nessun S3/CDN paid. | — | — |
| Smoke test installer cross-OS | ✅ esiste | `.github/workflows/smoke-test-installers.yml` (5188 byte). v1.0.1 ZERO assets → smoke test mai eseguito su release reale. | P1 | (parte di re-trigger pipeline) |
| AV submission (VirusTotal) | ✅ docs | `scripts/install/docs/av-submission-guide.md` + `virustotal-setup.md` + workflow `virustotal-gate.yml` (9449 byte). Da rieseguire dopo nuovi MSI signed-or-not. | P1 | 1h (submit nuovi installer post-build) |

### Sintesi P0 BLOCKING — Categoria 1

**8 gap P0** che impediscono lancio:

1. **v1.0.1 release ha ZERO assets** → `gh release view v1.0.1 --json assets` → `{"assets":[]}`. Auto-updater 404, nessuno può scaricare. *(re-triggerare pipeline OR ri-upload manuale)*
2. **`latest.json` endpoint 404** → auto-updater non funziona per chi installa v1.0.0 manuale. *(generare + upload)*
3. **Tauri signing key DISABLED** in CI → updater senza firma valida = client rifiuterà download. *(founder rigenera key)*
4. **Sidecar voice-agent = placeholder script** in repo (`exit 1`). PyInstaller binary non viene mai bundle se non da CI, ma CI bypassa con artifact rename. Locale `npm run tauri build` su iMac = sidecar broken. *(build su iMac + commit binari OR fix path artifact)*
5. **Universal Binary mancante** → Mac Intel utenti non hanno DMG dedicato. v1.0.0 aveva solo `x64.dmg` (= Intel). v1.0.1 niente. CLAUDE.md richiede entrambi. *(lipo UB o doppio target)*
6. **MSI Windows mancante** → solo NSIS .exe. CLAUDE.md "Windows MSI unsigned + SmartScreen mitigation page" come deliverable P0. *(aggiungere wix MSI target)*
7. **Version mismatch Cargo 1.0.0 vs Tauri/package 1.0.1** → binary self-report versione sbagliata, auto-updater compara `1.0.0 == latest` e dichiara "up to date" anche se latest=1.0.2. *(bump 5min)*
8. **`createUpdaterArtifacts: false`** in `tauri.conf.json:7` → pipeline non genera mai `.sig` files anche se signing fosse attivo. *(toggle true + verify)*

### Sintesi P1 quality — Categoria 1

- PKG installer macOS (DMG già copre, ma PKG migliora UX silent install gestiti)
- Setup-win.bat embedded in NSIS installer-hooks (oggi richiede download separato)
- `minimumSystemVersion 10.15 → 12.0` allineamento docs/codice
- `IMAC_IP` script build hardcoded `.7` invece di env var
- AV submission rerun post-rebuild
- PyInstaller CI usare `.spec` invece di CLI inline

### Sintesi P2 marketing — Categoria 1

- VirusTotal badge live su landing/installa
- Mirror download via CF Pages (oggi solo GitHub Releases, single point of failure se GH down)

### Dipendenze (sequenza fix P0)

```
[7] bump Cargo.toml 1.0.1
   └─→ [3] founder rigenera Tauri signing key + GH secrets
       └─→ [8] toggle createUpdaterArtifacts=true
           └─→ [4] build sidecar PyInstaller iMac (arm64+x86_64) + Win
               └─→ [5][6] aggiungere matrix macos-13 + wix MSI target in release-full.yml
                   └─→ tag v1.0.2 → trigger pipeline
                       └─→ [1] assets uploaded (DMG arm64, DMG x64, MSI, NSIS, voice-agent x3)
                           └─→ [2] generate-manifest job pubblica latest.json
                               └─→ ✅ Auto-updater funzionale end-to-end
```

**Effort totale P0 Categoria 1**: ~12-16h sequenziali (founder action #3 unico blocker non self-serve).

---

## CATEGORIA 2 — FUNCTIONAL E2E
*[PENDING — audit prossimo]*

## CATEGORIA 3 — SECURITY
*[PENDING]*

## CATEGORIA 4 — PERFORMANCE
*[PENDING]*

## CATEGORIA 5 — COMPLIANCE
*[PENDING]*

## CATEGORIA 6 — CUSTOMER SUCCESS
*[PENDING]*
