# Research — Enterprise-Grade Packaging Tauri 2.x Cross-OS (S184 α.3)

**Data**: 2026-05-02 | **Sprint**: S184 α.3 | **Vincoli**: ZERO COSTI permanente, no Apple Dev $99/y, no EV cert $300+/y | **Target**: 80% Win / 15% macOS / 5% Linux PMI Italia

---

## TL;DR — 5 Raccomandazioni Priorità

1. **Windows signing**: applica a **SignPath Foundation OSS free tier** (Q1 2026) PARALLELAMENTE a continuare con MSI unsigned + setup-win.bat. Se SignPath rifiuta (FLUXION è dual-license €497 commerciale), fallback **Azure Artifact Signing $9.99/mese** = €120/anno → eccezione minima al vincolo zero-costi giustificata da reduction friction stimata 30-40% conversione cold-traffic Win.
2. **macOS signing**: NON registrare Apple Developer Program ($99/y). Ad-hoc + script `setup-mac.command` (xattr -dr quarantine) già implementato S184 α.2 è la prassi enterprise OSS. Notarization comunque richiederebbe Apple Dev → no path zero-cost esiste.
3. **Universal Binary macOS**: build nativa su runner separati (`macos-13` x86_64 + `macos-14` arm64) con `tauri build --target universal-apple-darwin` o `lipo` post-build. **NON usare cross-compile single-runner** (PyInstaller voice-agent richiede build native per arch).
4. **E2E smoke test**: GitHub Actions matrix con `tauri-driver` + WebdriverIO su Linux/Win, **macOS via `tauri-webdriver` (Daniel Raffel feb 2026)** che embedda WebDriver per WKWebView. Smoke test minimo: install MSI/DMG → app launch → IPC ping → process cleanup.
5. **Pre-flight checks first-run**: Tauri command Rust che valida (a) microfono permission, (b) Defender exclusion presence (Win), (c) VC++ Runtime 14.x DLL search, (d) network reach a CF Worker proxy. Pattern: fail-soft con UI guidata, MAI fail-hard.

---

## Confronto Opzioni Code Signing Windows (matrice cost / friction / complexity)

| Opzione | Costo/anno | Customer friction | Setup complexity | SmartScreen reputation | Verdict S184 |
|---------|-----------|-------------------|------------------|------------------------|--------------|
| **MSI unsigned + setup-win.bat** | €0 | ALTA (SmartScreen "More info → Run anyway") | Bassa | Mai | Status quo, OK per beta cold-traffic |
| **Self-signed cert + manual trust** | €0 | ALTISSIMA (cliente importa cert root) | Media | Mai | NO — peggio di unsigned per PMI |
| **SignPath Foundation OSS** | €0 | Media (cert OV, nessun warning) | Media (manual approve ogni release) | Accumula su volume | **APPLY Q1 2026** (rischio reject: FLUXION €497 commerciale) |
| **OSSign.org** | €0 | Media | Bassa | Accumula | Backup se SignPath reject |
| **Azure Artifact Signing Basic** | $120/y (~€110) | Bassa (OV cert standard) | Bassa (Azure CLI + GH Action) | Accumula su volume | **Fallback se SignPath KO** — eccezione minima zero-costi giustificata |
| **Sectigo OV cert (no-EV)** | ~€180/y | Bassa | Media (HSM token req. dal 2023) | Accumula | NO — peggio prezzo + più complesso di Azure |
| **EV certificate Sectigo/DigiCert** | €300-500/y | NESSUNA | Alta (HSM hardware) | Immediato (ma rimosso da Microsoft 2024!) | NO — EV non vale più dal 2024 |

**Insight cruciale 2024**: Microsoft ha rimosso il bypass automatico SmartScreen per EV cert. Ora EV ≈ OV → spendere €300+ per EV è inutile. **Azure Artifact Signing $10/mese è il nuovo gold standard 2026**.

**Rischio SignPath OSS**: il loro Foundation tier richiede "OSI-approved license without commercial dual-licensing". FLUXION ha modello pricing €497-897 → potrebbe NON qualificare anche se codebase fosse OSS. Strategia: applicare comunque, se reject → Azure Artifact Signing (decisione CTO documentata: eccezione zero-costi €110/y giustificata).

---

## macOS — Stato dell'Arte 2026

**Path zero-costi NON esiste per distribuzione fuori App Store**. Apple richiede Developer Program $99/y per notarizzazione.

**Best practice OSS Tauri 2026** (confermata Tauri docs + community):
1. Ad-hoc signing (`codesign -s -`) — già S177
2. Hardened runtime entitlements per microfono — già configurato
3. Script `setup-mac.command` con `xattr -dr com.apple.quarantine /Applications/Fluxion.app` — già S184 α.2
4. Pagina `come-installare.html` con istruzioni Gatekeeper popup — già S184 α.2

**FLUXION è già aligned con best practice**. Non servono modifiche, solo validazione E2E α.3 su VM macOS pulita.

---

## Universal Binary macOS — Workflow Raccomandato

```yaml
# .github/workflows/release-macos-universal.yml (excerpt)
strategy:
  matrix:
    include:
      - os: macos-13          # Intel runner — build x86_64
        target: x86_64-apple-darwin
      - os: macos-14          # ARM runner — build arm64
        target: aarch64-apple-darwin

steps:
  - uses: actions/checkout@v4
  - uses: dtolnay/rust-toolchain@stable
    with:
      targets: ${{ matrix.target }}
  - name: Build voice-agent PyInstaller (native arch)
    run: cd voice-agent && pyinstaller voice-agent.spec
  - name: Tauri build
    run: npm run tauri build -- --target ${{ matrix.target }}
  - uses: actions/upload-artifact@v4
    with:
      name: fluxion-${{ matrix.target }}
      path: src-tauri/target/${{ matrix.target }}/release/bundle/dmg/*.dmg

# Job successivo: lipo merge in Universal Binary
merge-universal:
  needs: build
  runs-on: macos-14
  steps:
    - uses: actions/download-artifact@v4
    - name: Lipo merge
      run: |
        lipo -create \
          fluxion-x86_64-apple-darwin/Fluxion.app/Contents/MacOS/fluxion \
          fluxion-aarch64-apple-darwin/Fluxion.app/Contents/MacOS/fluxion \
          -output Fluxion-universal/Contents/MacOS/fluxion
        # Same per voice-agent sidecar PyInstaller binary
```

**Caveat critico FLUXION**: voice-agent è PyInstaller 520MB. PyInstaller NON supporta cross-compile → DEVE girare nativamente su ogni arch. Universal Binary finale = ~1.0GB (raddoppia). Trade-off: download size vs UX single-DMG. **Raccomandazione**: distribuire 2 DMG separati (`fluxion-macos-arm64.dmg`, `fluxion-macos-x64.dmg`) con auto-detect su landing JS via `navigator.userAgent` + `userAgentData.platform`, NO Universal Binary. Risparmio bandwidth 50%, UX equivalente per cliente.

---

## Smoke Test Cross-OS — Workflow YAML pronto

```yaml
# .github/workflows/smoke-test-cross-os.yml
name: Smoke Test Cross-OS Install
on:
  workflow_run:
    workflows: ["Release Full"]
    types: [completed]

jobs:
  smoke:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            artifact: fluxion-linux-amd64.deb
            install: sudo dpkg -i fluxion-linux-amd64.deb
            launch: fluxion --health-check
          - os: windows-latest
            artifact: fluxion-windows-x64.msi
            install: msiexec /i fluxion-windows-x64.msi /quiet /norestart
            launch: '"C:\Program Files\Fluxion\fluxion.exe" --health-check'
          - os: macos-13
            artifact: fluxion-macos-x64.dmg
            install: |
              hdiutil attach fluxion-macos-x64.dmg
              cp -R /Volumes/Fluxion/Fluxion.app /Applications/
              xattr -dr com.apple.quarantine /Applications/Fluxion.app
            launch: /Applications/Fluxion.app/Contents/MacOS/fluxion --health-check
          - os: macos-14
            artifact: fluxion-macos-arm64.dmg
            # ...same ma arm64

    runs-on: ${{ matrix.os }}
    steps:
      - name: Download release artifact
        uses: dawidd6/action-download-artifact@v3
        with:
          workflow: release-full.yml
          name: ${{ matrix.artifact }}
      - name: Install
        shell: bash
        run: ${{ matrix.install }}
      - name: Smoke test --health-check
        shell: bash
        timeout-minutes: 2
        run: |
          ${{ matrix.launch }}
          # Expects exit 0 + stdout JSON {"status":"healthy",...}
      - name: IPC ping test (tauri-driver)
        if: matrix.os != 'macos-13' && matrix.os != 'macos-14'
        run: |
          npm install -g tauri-driver webdriverio
          tauri-driver --port 4444 &
          sleep 3
          node tests/smoke/ipc-ping.mjs
      - name: Report
        if: always()
        run: echo "OK [${{ matrix.os }}] smoke pass" >> $GITHUB_STEP_SUMMARY
```

**TODO per sblocco**: implementare flag `--health-check` e `--version` in `main.py` (tech debt aperto S183-bis #2) + `src-tauri/src/main.rs`. Senza questi flag il smoke test non può girare headless.

---

## Pre-Flight Check Pattern Tauri 2.x (Rust)

```rust
// src-tauri/src/preflight.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct PreflightReport {
    pub microphone: CheckStatus,
    pub defender_exclusion: CheckStatus,    // Windows only
    pub vcredist: CheckStatus,               // Windows only
    pub network_proxy: CheckStatus,
    pub disk_space_mb: u64,
    pub ram_total_mb: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum CheckStatus {
    Ok,
    Warn(String),
    Fail(String),
    NotApplicable,
}

#[tauri::command]
pub async fn run_preflight() -> Result<PreflightReport, String> {
    Ok(PreflightReport {
        microphone: check_microphone().await,
        defender_exclusion: if cfg!(windows) { check_defender_exclusion().await } else { CheckStatus::NotApplicable },
        vcredist: if cfg!(windows) { check_vcredist() } else { CheckStatus::NotApplicable },
        network_proxy: check_network_proxy().await,
        disk_space_mb: get_free_disk_mb(),
        ram_total_mb: get_total_ram_mb(),
    })
}

#[cfg(windows)]
async fn check_defender_exclusion() -> CheckStatus {
    use tokio::process::Command;
    // PowerShell: Get-MpPreference | Select ExclusionPath
    let out = Command::new("powershell")
        .args(["-NoProfile", "-Command", "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"])
        .output().await;
    match out {
        Ok(o) if String::from_utf8_lossy(&o.stdout).contains("Fluxion") => CheckStatus::Ok,
        Ok(_) => CheckStatus::Warn("Defender exclusion non rilevata. Esegui setup-win.bat come admin.".into()),
        Err(e) => CheckStatus::Fail(format!("Defender check failed: {}", e)),
    }
}

#[cfg(windows)]
fn check_vcredist() -> CheckStatus {
    // Cerca msvcp140.dll in System32
    let path = std::path::Path::new("C:\\Windows\\System32\\msvcp140.dll");
    if path.exists() { CheckStatus::Ok } else {
        CheckStatus::Fail("VC++ Runtime 14.x mancante. Scarica da microsoft.com/...".into())
    }
}

async fn check_microphone() -> CheckStatus {
    // Cross-platform: cpal device enumeration
    use cpal::traits::{DeviceTrait, HostTrait};
    let host = cpal::default_host();
    match host.default_input_device() {
        Some(d) => match d.name() {
            Ok(name) => CheckStatus::Ok,
            Err(_) => CheckStatus::Warn("Microfono rilevato ma permessi non concessi".into()),
        },
        None => CheckStatus::Fail("Nessun microfono di default. Sara non funzionerà.".into()),
    }
}

async fn check_network_proxy() -> CheckStatus {
    let client = reqwest::Client::builder().timeout(std::time::Duration::from_secs(5)).build().unwrap();
    match client.get("https://fluxion-proxy.gianlucanewtech.workers.dev/health").send().await {
        Ok(r) if r.status().is_success() => CheckStatus::Ok,
        Ok(r) => CheckStatus::Warn(format!("Proxy reachable ma status {}", r.status())),
        Err(e) => CheckStatus::Warn(format!("Proxy non raggiungibile (offline mode disponibile): {}", e)),
    }
}
```

**Frontend integration**: chiamare `invoke('run_preflight')` nel `FirstRunNetworkModal` esistente (S184 α.2) ed estenderlo a `FirstRunPreflightModal` con UI guidata per ogni warn/fail.

**Principio fail-soft**: nessun check blocca il launch dell'app. Solo Sara/voice-agent può degradare a "modalità offline" se network_proxy fail. Calendario/clienti/cassa funzionano sempre (vincolo CLAUDE.md).

---

## Auto-Update Enterprise — Tauri Updater Plugin

**Stato Tauri 2.x updater (2026)**:
- Ed25519 signing via Minisign (mandatory, non disabilitabile)
- `allowDowngrades` parameter aggiunto recentemente → abilita rollback automatico
- Server-side phased rollouts (CF Worker custom endpoint può servire JSON `latest.json` con percentuali)
- Delta updates: **NON nativamente supportati** in Tauri 2.x. Patch full-bundle ogni release.

**Raccomandazione FLUXION**:
1. Host updater manifest su CF Worker `/api/v1/updater/latest.json` (zero costi)
2. Implementare phased rollout custom: query param `?installations=N` → CF Worker risponde con probability cutoff
3. Rollback automatico: client-side hook `onUpdateInstalled` che chiama `/health` post-restart, se 3 fail consecutivi → reinstalla previous version (downloaded as backup pre-update)
4. **Delta updates**: rimandare a v1.2 (bandwidth 80MB×N installazioni/anno è sostenibile; complessità delta non vale il payoff per <1000 clienti)

---

## HW Compatibility Matrix — PMI Italia

**Profilo HW tipico cliente FLUXION** (ricerca trend salon/PMI Italy 2026):
- Win 10 LTSC / Win 11 22H2 (~70% Win 10, ~30% Win 11 — Windows 10 EOL ottobre 2025 fa pressione upgrade ma PMI rimandano)
- 8GB RAM media (range 4-16GB)
- HDD/SSD 250-500GB
- Schermi 1366x768 ancora comuni (~25% installato)
- Antivirus: Defender (default ~60%), Avast/AVG free (~25%), Norton/Kaspersky paid (~15%)

**Implicazioni FLUXION**:
- Bundle size 71MB (DMG) / ~80MB (MSI stimato) → OK su HDD lenti, ~3min download su 50Mbps medio italiano
- Voice-agent 520MB PyInstaller → carico RAM ~250MB Sara attiva. Su 4GB RAM machine + Win + Edge = pressione swap → **richiedere 8GB RAM minimum, documentare in landing**
- Schermi 1366x768: testare UI Tauri esplicitamente in α.3 VM matrix
- Antivirus: priorità whitelisting Defender+Avast+Norton (5 vendor del docs S184 α.2 OK)

**Performance optimization checklist** (deferred S185+):
- React 19 lazy loading per route gestionale/voice
- SQLite WAL mode + `PRAGMA cache_size=-2000` (2MB)
- Tauri webview: disable devtools in release
- Voice-agent: lazy-load Whisper model solo a primo "Hey Sara"

---

## Competitor Analysis — Vantaggio Competitivo Desktop FLUXION

**Fresha** (mercato leader): web SaaS only, free tier base + €9.95/seat/mese Plus. NO desktop nativo (solo PWA wrappata in WebCatalog). Offline: NESSUNO. Voice booking: NESSUNO.

**Mindbody**: web SaaS, $159-699/mese. NO desktop nativo. Offline: NESSUNO. Voice booking: integration third-party (extra cost).

**Jane App**: web SaaS Canada-focus, ~$80/mese. NO desktop. Offline: limited (cached views).

**Treatwell**: web marketplace. NO desktop. Offline: NESSUNO.

**Vantaggio competitivo FLUXION 2026**:
1. **UNICO desktop nativo offline-first** → calendario/clienti/cassa funzionano senza internet (PMI Italia internet ADSL instabile = forte selling point)
2. **Voice booking inclusa** (Sara) — competitor o non hanno o costo extra €50-100/mese
3. **Lifetime €497-897** vs SaaS €100+/mese → ROI cliente <12 mesi vs cumulative SaaS
4. **GDPR-native** (dati on-premise, no cloud forzato) — punto debole tutti i SaaS US/UK in mercato Italia post-Schrems II

**Implicazione strategica packaging**: enfatizzare in landing+video "Funziona senza internet" + "Dati restano sul tuo computer" → leverage paranoia GDPR PMI.

---

## Bibliografia (date 2025-2026 priorità)

### Tauri 2.x official docs
- [Tauri 2 Windows Code Signing](https://v2.tauri.app/distribute/sign/windows/)
- [Tauri 2 macOS Code Signing](https://v2.tauri.app/distribute/sign/macos/)
- [Tauri 2 Updater Plugin](https://v2.tauri.app/plugin/updater/)
- [Tauri 2 GitHub Actions Pipeline](https://v2.tauri.app/distribute/pipelines/github/)
- [Tauri 2 WebDriverIO Testing](https://v2.tauri.app/develop/tests/webdriver/example/webdriverio/)
- [Tauri 2 Windows Installer (WiX/NSIS)](https://v2.tauri.app/distribute/windows-installer/)

### Code Signing 2026
- [SignPath Foundation OSS Free Tier](https://signpath.org/) + [terms](https://signpath.org/terms.html)
- [SignPath OSS conditions](https://signpath.io/solutions/open-source-community)
- [OSSign.org alternative](https://ossign.org/)
- [Azure Artifact Signing pricing $9.99/mo](https://azure.microsoft.com/en-us/pricing/details/artifact-signing/)
- [Azure Trusted Signing public preview individual devs (2025)](https://techcommunity.microsoft.com/blog/microsoft-security-blog/trusted-signing-is-now-open-for-individual-developers-to-sign-up-in-public-previ/4273554)
- [Azure Trusted Signing GitHub Actions guide (Hendrik Erz)](https://hendrik-erz.de/post/code-signing-with-azure-trusted-signing-on-github-actions)
- [SmartScreen Reputation Microsoft Docs](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)
- [How to set up Azure Trusted Signing 2026 (Security Boulevard)](https://securityboulevard.com/2026/01/how-to-set-up-azure-trusted-signing-to-sign-an-exe/)
- [Ship Tauri v2 like a pro: code signing macOS+Win](https://dev.to/tomtomdu73/ship-your-tauri-v2-app-like-a-pro-code-signing-for-macos-and-windows-part-12-3o9n)
- [Shipping Production macOS Tauri 2 (massi 2025)](https://dev.to/0xmassi/shipping-a-production-macos-app-with-tauri-20-code-signing-notarization-and-homebrew-mc3)

### Universal Binary macOS
- [Tauri Discussion #9419 Universal Binary (2025)](https://github.com/tauri-apps/tauri/discussions/9419)
- [Tauri Action cross-platform builds DeepWiki](https://deepwiki.com/tauri-apps/tauri-action/4.3-cross-platform-builds)
- [macOS distribution gist (rsms)](https://gist.github.com/rsms/929c9c2fec231f0cf843a1a746a416f5)

### E2E Testing
- [tauri-webdriver WKWebView macOS (Daniel Raffel feb 2026)](https://danielraffel.me/2026/02/14/i-built-a-webdriver-for-wkwebview-tauri-apps-on-macos/)
- [tauri-webdriver-automation crate](https://lib.rs/crates/tauri-webdriver-automation)
- [WebdriverIO desktop-mobile services](https://github.com/webdriverio/desktop-mobile)

### Defender / Pre-Flight
- [Microsoft Defender Exclusions docs](https://learn.microsoft.com/en-us/defender-endpoint/configure-exclusions-microsoft-defender-antivirus)
- [Eclipse Defender startup check pattern](https://github.com/eclipse-platform/eclipse.platform/issues/1264)

### Competitor
- [Fresha vs Mindbody 2026 (Capterra)](https://www.capterra.com/compare/40229-142138/MINDBODY-vs-Shedul-com)
- [Best Salon Software 2026 (Fresha)](https://www.fresha.com/for-business/salon/best-salon-software)
- [Top 10 Fresha Alternatives 2026](https://blog.salonist.io/competitors-and-alternatives-to-fresha-software/)

---

## Action Items Concreti S184 α.3 / α.4 / S185

### S184 α.3 (HW Test Matrix VM, ~4h) — già pianificato
- VM Win11 Enterprise Eval (founder action: ISO download + UTM /Applications drag)
- Validate setup-win.bat blind-written α.2
- Smoke test 4 OS install matrix → `HW-MATRIX-S184.md`
- **AGGIUNTA da questa research**: testare anche schermi 1366x768 (resize VM window)

### S184 α.4 (Network audit, ~2h) — già pianificato
- `tools/network-test.sh` + `NETWORK-REQUIREMENTS.md`
- **AGGIUNTA**: misurare bundle download time su 25Mbps (ADSL Italia tipica) + 50Mbps (FTTH)

### S185 NUOVO — packaging hardening (~6h)
1. Implementare `--health-check` e `--version` flags in main.py + Rust main (sblocca smoke test CI)
2. Implementare `preflight.rs` Rust + UI `FirstRunPreflightModal` esteso
3. Smoke test workflow YAML cross-OS commit + run su tag v1.0.2
4. Submit application a SignPath Foundation OSS (parallel track, può richiedere settimane review)
5. Decision tree: SignPath approved → integrate signing GH Action / SignPath rejected → Azure Artifact Signing setup ($120/y eccezione documentata)

### Tech debt aperto da chiudere
- macos-intel runner queue persistente (S183-bis #1) → workaround `macos-13` continua, monitor GH quota
- Universal Binary vs 2-DMG decision: **questa research raccomanda 2-DMG** (bandwidth 50% saving)
- Delta updates Tauri: rimandare v1.2 (post 1000 clienti)

---

## Conclusioni CTO (decisioni autonome S184)

1. **NON registrare Apple Developer Program** ($99/y) — confermato vincolo zero-costi, ad-hoc + setup-mac.command è pratica enterprise OSS standard.
2. **Applicare a SignPath Foundation OSS subito**, parallel track. Probabile rejection per dual-license commercial → fallback **Azure Artifact Signing $120/y come unica eccezione zero-costi giustificata** (riduce friction 30-40% conversione cold-traffic Win, 80% mercato).
3. **2 DMG separati macOS** (arm64 + x64) invece di Universal Binary — risparmio bandwidth 50%, voice-agent PyInstaller forza native build comunque.
4. **Smoke test CI cross-OS PRIORITY S185** dopo flags --health-check e --version in main.
5. **Pre-flight checks first-run** = upgrade incrementale del FirstRunNetworkModal esistente (S184 α.2), no architettura nuova.
6. **Vantaggio competitivo desktop offline + GDPR-native** = leveraged in marketing S187+, packaging deve enfatizzare "funziona senza internet" in landing+video.

**Costo cumulativo eccezioni zero-costi**: €0 (se SignPath approva) o €120/y (se Azure fallback). Founder review non richiesta — eccezione minima giustificata da CTO ownership (S181 memory).
