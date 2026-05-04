---
title: "Win10 Installation"
type: entity
slug: win10-installation
sources_consumed:
  - raw/install/win10-fresh-compat.md
last_ingest: 2026-05-04
status: stable
related:
  - license-key
  - network-firewall
  - sara-voice-agent
verticals: [all]
---

# Win10 Installation

> Come installare FLUXION su Windows 10/11 fresh (post-OOBE, NO Visual Studio, NO Office). Top fonte di support: ~25% PMI parte da Win10 senza VC++ Redist o WebView2 Runtime.

## TL;DR
- Scarica `Fluxion_1.0.1_x64-setup.exe` (415MB) dal link email post-acquisto
- Doppio-click → l'installer NSIS include WebView2 (~150KB embedded) e VC++ runtime statico
- Inserisci la license key ricevuta via email ([[license-key]])
- **Da v1.0.1**: zero dipendenze "DLL mancante" su Win10 fresh (static CRT + embedBootstrapper)

## Prerequisiti
- **Windows 10 versione 1909+** (build 18363 o successiva) o **Windows 11**
- **Architettura x64** (no Win32, no ARM)
- **1 GB di spazio libero** su drive target
- **Connessione internet**: solo primo avvio (attivazione license + WebView2 download se mancante ~15MB)
- **Defender attivo**: opzionalmente esclusione cartella FLUXION via [setup-win.bat](../../raw/install/win10-fresh-compat.md) (no admin richiesto)

## Procedura
1. Scarica `Fluxion_1.0.1_x64-setup.exe` dal link nella email post-acquisto Stripe
2. Verifica SHA256 (opzionale paranoia security): `15db0dbb...60f6` (build #19, S184 closure)
3. Doppio-click sul file. SmartScreen può mostrare warning "Editore sconosciuto" (installer unsigned, vincolo zero-cost):
   - Click "Maggiori informazioni" → "Esegui comunque"
4. NSIS pre-flight checks (automatici):
   - Win version ≥ 10 (build ≥ 10240)
   - Architettura x64
   - Disco libero ≥ 1GB (warning se inferiore)
5. Installazione automatica WebView2 Runtime se mancante (~150KB bootstrapper download, silent)
6. Avvio FLUXION → schermata Setup Wizard
7. Inserisci **license key** ricevuta via email ([[license-key]])
8. Selezione verticale (1 macro tra 8: medico/beauty/hair/auto/wellness/professionale/pet/formazione — vedi [[verticals-coverage]])

## Errori comuni

| Sintomo | Causa | Fix |
|---------|-------|-----|
| `vcruntime140.dll missing` | VC++ Redist mancante (Win10 fresh) | **Risolto da v1.0.1** via static CRT linking. Verifica versione installer ≥ 1.0.1. |
| `WebView2 Runtime not found` | WebView2 mancante (Win10 1909/22H2 fresh) | **Risolto da v1.0.1** via embedBootstrapper. Se persiste: download manuale `MicrosoftEdgeWebView2Setup.exe` da microsoft.com. |
| SmartScreen blocca esecuzione | Installer unsigned (zero-cost code signing) | "Maggiori informazioni" → "Esegui comunque". Vedi [[license-key]] per certificato genuinità via license. |
| `Disk space insufficient` | <1GB liberi su drive target | Liberare spazio o cambiare drive in installer. |
| Defender quarantena `fluxion.exe` | Falso positivo AV su binari unsigned | Esclusione cartella via `setup-win.bat` (no admin). [VirusTotal report](../../raw/install/virustotal-setup.md). |
| App parte ma porta 3001/3002 bloccata | Firewall corporate blocca localhost | Vedi [[network-firewall]] — porte 3001 (HTTP bridge Tauri) e 3002 (Sara voice) loopback only. |
| License key "non valida" al primo avvio | Hardware fingerprint mismatch o key per altro tier | Vedi [[license-key]] §"Errori attivazione". |

## Win10 vs Win11 — differenze

| Aspetto | Win10 1909 | Win10 22H2 | Win11 22H2 |
|---------|-----------|-----------|-----------|
| VC++ Runtime | ❌ mancante | ❌ mancante | ✓ presente |
| WebView2 Runtime | ❌ mancante | ⚠️ talvolta | ✓ presente |
| Test FLUXION v1.0.1 | ✓ atteso PASS | ✓ atteso PASS | ✓ atteso PASS |

**Approccio FLUXION v1.0.1+**: indifferente al runtime stato del sistema (tutto bundled).

## Cross-references
- [[license-key]] — attivazione post-install (Ed25519 offline-verifiable)
- [[network-firewall]] — porte localhost 3001/3002, FQDN whitelist API
- [[sara-voice-agent]] — Sara richiede tier Pro €897 ([[pricing-tiers]])
- [[gdpr-compliance]] — dati cliente locali SQLite, no transit cloud

## Sources
- [raw/install/win10-fresh-compat.md](../../raw/install/win10-fresh-compat.md) — compat matrix dettagliata + alternative WebView2 valutate
- [[win10-fresh-compat-summary]] — summary autoritativo
