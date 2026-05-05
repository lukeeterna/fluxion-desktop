---
title: "Source Summary — Win10 Fresh Compat (S184 α.3.3)"
type: source-summary
slug: win10-fresh-compat-summary
sources_consumed:
  - raw/install/win10-fresh-compat.md
last_ingest: 2026-05-04
status: stable
related:
  - win10-installation
  - network-firewall
verticals: [all]
---

# Source Summary — Win10 Fresh Compat

**Original**: [raw/install/win10-fresh-compat.md](../../raw/install/win10-fresh-compat.md) (110 lines, S184 α.3.3 closure 2026-05-02)

**Source autoritativa interna FLUXION** per compatibilità Win10/11 fresh install. Documenta strategia α.3.3 per eliminazione 100% errori "DLL mancante" su Win10 PMI senza Visual Studio/Office.

## Takeaways

1. **VC++ runtime risolto via static CRT linking** (`+crt-static` rustflag in `src-tauri/.cargo/config.toml`). Elimina dipendenza `vcruntime140.dll`/`msvcp140.dll` su Win10 fresh senza VC++ Redist installato. Trade-off ~+1.5MB binario (trascurabile vs installer 520MB).

2. **WebView2 Runtime via embedBootstrapper** (`tauri.conf.json::bundle.windows.webviewInstallMode`). Installer NSIS contiene `MicrosoftEdgeWebView2Setup.exe` ~150KB. Auto-install silenzioso al setup time se mancante. Alternative valutate e scartate: `offlineInstaller` (120MB troppo pesante), `downloadBootstrapper` (fallisce offline), `skip` (fallisce Win10 fresh).

3. **Python voice-agent via PyInstaller bundled DLLs** (`voice-agent/voice-agent.spec`). Include `python311.dll` + `vcruntime140_1.dll` nel bundle `binaries/voice-agent`. Cliente NON installa Python.

4. **NSIS installer pre-flight checks** (`src-tauri/installer-hooks.nsh`): blocca install se Win <10 (build <10240) o non x64; warning disco <1GB; log WebView2 detection. Tutti messaggi italiani, supporto `fluxion.gestionale@gmail.com`.

5. **Test matrix**: Win10 1909 (build 18363) + Win10 22H2 (build 19045) + Win11 22H2 (build 22621) — manuale post α.3.2 VM. CI gates: `dumpbin /imports` verifica NO `vcruntime140.dll` + smoke-test su `windows-latest` runner.

## Citazioni-chiave

> Static CRT elimina dipendenza vcruntime140.dll/msvcp140.dll. Trade-off ~+1.5MB binario (trascurabile, totale installer ~520MB).
> — [raw/install/win10-fresh-compat.md:21-34]

> embedBootstrapper: l'installer NSIS contiene il MicrosoftEdgeWebView2Setup.exe (~150KB). Se il sistema target non ha WebView2 Evergreen, l'installer lo scarica e installa silenziosamente al setup time. Funziona anche offline solo se Edge browser è già presente (in tutti i Win10 build 17134+).
> — [raw/install/win10-fresh-compat.md:36-47]

> NSIS pre-flight: 1. Win version: blocca install se < Win10 (build < 10240); 2. Architecture: blocca install se non x64; 3. Disk space: warning se < 1GB liberi; 4. WebView2 detection: log only.
> — [raw/install/win10-fresh-compat.md:64-73]

## Pagine wiki impattate

- [[win10-installation]] — CREATED, sezioni Prerequisiti + Procedura + Errori comuni + Win10/11 differences alimentate da questo source
- [[network-firewall]] — UPDATED, riferimento `setup-win.bat` per firewall localhost rules + Defender exclusion
- (potenziali future): `webview2-runtime`, `vc-runtime`, `nsis-installer-hooks` — entity dedicate se support emails fanno emergere domande granulari

## Risk register documentato (dal source)

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| `+crt-static` rompe link DLL sistema | Bassa | Alta | Test cargo build CI smoke-test-installers |
| WebView2 bootstrapper richiede internet | Media | Bassa | Doc utente: serve internet 1 volta (15MB DL) |
| NSIS hook fallisce locali esotici | Bassa | Bassa | Solo italiano + inglese (wizard) |
| PyInstaller bundle non include vcruntime140_1 | Bassa | Alta | Test smoke su Win10 1909 fresh (α.3.2 VM) |

## Riferimenti esterni (dal source)

- Tauri v2 NSIS docs: https://v2.tauri.app/distribute/windows-installer/
- Tauri v2 WebView2 install mode: https://v2.tauri.app/reference/config/#windowsconfig
- Rust crt-static RFC: https://rust-lang.github.io/rfcs/1721-crt-static.html
- Microsoft VC++ Redist version map: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
- WebView2 distribution guide: https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution

## Status

**stable** — fonte tecnica autoritativa interna FLUXION (S184 closure totale 2026-05-04, build #19 SUCCESS Win MSI). Da rivisitare se: (a) Tauri 3.x cambia WebView2 install mode API, (b) Rust crt-static deprecato, (c) feedback support reale Win10 fresh PMI rivela edge case non coperti.
