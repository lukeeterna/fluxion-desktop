# FLUXION — Win10/11 Fresh Install Compat Matrix (S184 α.3.3)

> Obiettivo: garantire che FLUXION installi e parta su un Windows fresh
> (post-OOBE, NO Visual Studio, NO Office, NO sviluppatori) senza errori
> "DLL mancante" o "componente runtime non trovato".

## Matrice di compatibilità

| Componente runtime          | Win10 1909 fresh | Win10 22H2 fresh | Win11 22H2 fresh | Approccio FLUXION                     |
| --------------------------- | ---------------- | ---------------- | ---------------- | ------------------------------------- |
| **vcruntime140.dll** (VC++) | ❌ MANCANTE       | ❌ MANCANTE       | ✓ presente       | **Static-linked nel binario Rust**    |
| **WebView2 Runtime**        | ❌ MANCANTE       | ⚠ talvolta       | ✓ presente       | **embedBootstrapper Tauri** (~150KB) |
| **.NET Framework 4.8**      | ✓ presente       | ✓ presente       | ✓ presente       | Non richiesto da FLUXION             |
| **Visual C++ 2015-2022**    | ❌ MANCANTE       | ❌ MANCANTE       | ✓ presente       | Eliminata dipendenza (vedi sopra)     |
| **PowerShell 5.1**          | ✓ presente       | ✓ presente       | ✓ presente       | Usato da setup-win.bat (Defender)    |
| **Microsoft Defender AV**   | attivo           | attivo           | attivo           | Esclusione opzionale via setup-win.bat |
| **Python 3.x**              | ❌ MANCANTE       | ❌ MANCANTE       | ❌ MANCANTE       | Non richiesto: voice-agent in PyInstaller bundle |

## Strategia α.3.3 (riassunto)

### 1. Rust → static CRT linking
**File**: `src-tauri/.cargo/config.toml`

```toml
[target.'cfg(all(target_os = "windows", target_env = "msvc"))']
rustflags = ["-C", "target-feature=+crt-static"]
```

**Effetto**: il binario `fluxion.exe` non dipende più da `vcruntime140.dll` /
`msvcp140.dll`. Self-contained. Niente prompt "VC++ Redistributable mancante"
al primo avvio.

**Trade-off**: ~+1.5MB binario. Trascurabile (totale installer ~520MB).

### 2. WebView2 → embedBootstrapper
**File**: `src-tauri/tauri.conf.json`

```json
"windows": {
  "webviewInstallMode": { "type": "embedBootstrapper" }
}
```

**Effetto**: l'installer NSIS contiene il MicrosoftEdgeWebView2Setup.exe
(~150KB). Se il sistema target non ha WebView2 Evergreen, l'installer lo
scarica e installa silenziosamente al setup time. Funziona anche offline
solo se Edge browser è già presente (in tutti i Win10 build 17134+).

**Alternative valutate**:
- `offlineInstaller`: bundle di ~120MB del WebView2 standalone — troppo
  pesante, scartato.
- `downloadBootstrapper`: scarica al setup time da CDN MS — fallisce se
  no internet, scartato.
- `skip`: assume WebView2 presente — fallisce su Win10 fresh.

### 3. PyInstaller voice-agent → bundled DLLs
**File**: `voice-agent/voice-agent.spec`

PyInstaller include automaticamente le DLL Python richieste (Python 3.11
→ `python311.dll`, `vcruntime140_1.dll`, ecc.) nel bundle `binaries/voice-agent`.
Questo bundle è poi inglobato in FLUXION via `tauri.conf.json::bundle.externalBin`.

### 4. NSIS installer hook → pre-flight checks
**File**: `src-tauri/installer-hooks.nsh`

Esegue PRIMA della copia file:
1. **Win version**: blocca install se < Win10 (build < 10240)
2. **Architecture**: blocca install se non x64 (no Win32, no ARM)
3. **Disk space**: warning se < 1GB liberi su drive target
4. **WebView2 detection**: log only (verrà installato dal bootstrapper se mancante)

Tutti i messaggi sono in italiano (target PMI). Assistenza:
`fluxion.gestionale@gmail.com`.

## Matrice di test

### Manuale (post-α.3.2 VM)
- [ ] **Win10 1909 fresh** (build 18363) — install + first run
- [ ] **Win10 22H2 fresh** (build 19045) — install + first run
- [ ] **Win11 22H2 fresh** (build 22621) — install + first run
- [ ] **Win10 con VC++ Redist installato** — install (non deve duplicare DLL)
- [ ] **Win10 con WebView2 già installato** — install (non deve reinstallare)
- [ ] **Win10 con drive C: < 1GB** — verifica warning + abort

### CI (automatico)
- [ ] `dumpbin /imports fluxion.exe` non contiene `vcruntime140.dll` (verifica static CRT)
- [ ] NSIS installer artifact include `installer-hooks.nsh` compiled-in
- [ ] Smoke test workflow su `windows-latest` runner (vanilla GH-hosted = simile a Win Server 2022 con vc++ già installato — limitato come fresh-install proxy ma comunque utile)

## Risk register

| Rischio                                        | Probabilità | Impatto | Mitigazione                                    |
| ---------------------------------------------- | ----------- | ------- | ---------------------------------------------- |
| `+crt-static` rompe link con DLL di sistema    | Bassa       | Alta    | Test cargo build in CI (smoke-test-installers) |
| WebView2 bootstrapper richiede internet        | Media       | Bassa   | Doc utente: serve internet 1 volta (15MB DL)  |
| NSIS hook fallisce su locali esotici          | Bassa       | Bassa   | Solo italiano + inglese (wizard)              |
| PyInstaller bundle non include vcruntime140_1  | Bassa       | Alta    | Test smoke su Win10 1909 fresh (α.3.2 VM)     |

## Riferimenti

- Tauri v2 NSIS docs: https://v2.tauri.app/distribute/windows-installer/
- Tauri v2 WebView2 install mode: https://v2.tauri.app/reference/config/#windowsconfig
- Rust crt-static RFC: https://rust-lang.github.io/rfcs/1721-crt-static.html
- Microsoft VC++ Redist version map: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
- WebView2 distribution guide: https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution

## Storia

- **α.3.3** (2026-05-02, commit pending): introduzione static CRT + NSIS hooks
- **α.3.2** (TBD, BLOCKED founder): validation manuale su VM Win10/11 fresh
