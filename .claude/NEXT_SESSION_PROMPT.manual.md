# Prompt ripartenza — Windows REAL install: SSH headless INSUFFICIENTE, serve 1 install fisico founder

**Aggiornato**: 2026-06-10 (sessione diagnosi install headless)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## 🟢 ACCESSO PC WINDOWS = STABILE (invariato)
- `ssh fluxion-win` (key-auth Ed25519, host in `~/.ssh/config`). User `gianluca` (admin), `alessiamanuel\gianluca`.
- Win10 22H2 build 19045 x64, ~152GB liberi C:.
- ⚠️ Solo key-auth (`2504` = PIN Hello, NON password).
- **FASE 0-bis FATTA**: sleep/hibernate/monitor-timeout disabilitati su AC + lid action 0. SSH regge (testato `STILL_UP` dopo 60s). Non rifare.

## 🔴 VERITÀ #1 (app si avvia su Windows) = BLOCCATA SU AZIONE FISICA FOUNDER
Diagnosi completa di questa sessione (prove reali, NON ipotesi):
- Installer copiato integro sul PC: `C:\fluxion-test\Fluxion_1.0.1_x64-setup.exe` = 423.999.525 byte.
- WebView2 Runtime già presente (v149.x) → non serve installarlo.
- `Fluxion..._setup.exe /S` (silent) via SSH → **install NON completa**: `start /wait` resta appeso, `%LOCALAPPDATA%\Programs\` VUOTO, `Program Files\Fluxion` assente, nessun Fluxion.exe installato sul disco (verificato con search ricorsivo C:\ completo).
- **ROOT CAUSE strutturale (2 fattori)**:
  1. `src-tauri/installer-hooks.nsh` usa `MessageBox` (righe 32/54/67) SENZA flag `/SD` → in sessione SSH non-interattiva (session 0) NON c'è desktop dove mostrare il dialog → installer appeso/abortito invisibile.
  2. exe **unsigned** → SmartScreen può richiedere click fisico ("Ulteriori info → Esegui comunque").
- Conclusione: **un installer GUI Tauri/NSIS non è installabile in modo affidabile via SSH headless**. Confermata nota S356. Questo è il limite, non un bug nostro.

## ▶️ AZIONE FOUNDER (Luke) — UNA VOLTA SOLA, fisicamente sul PC Windows
Sul PC (tastiera/mouse fisici o RDP), una volta:
1. Apri `C:\fluxion-test\` → doppio-click `Fluxion_1.0.1_x64-setup.exe`.
2. Se appare "Windows ha protetto il PC" (SmartScreen) → clicca **"Ulteriori informazioni" → "Esegui comunque"** (normale per exe non firmato, Pila 2 congelata).
3. Segui l'installer (italiano). Al termine, l'app dovrebbe avviarsi / trovarla nel menu Start come "Fluxion".
4. Dimmi solo: **"installato"** (o incolla l'eventuale errore). NON devi fare altro: il resto lo verifico io via SSH.

## ▶️ DOPO "installato" — VERIFICA AUTONOMA CC (NO founder)
Tutto il resto è SSH-verificabile senza GUI:
1. **VERITÀ #1 conferma**: `ssh fluxion-win "dir %LOCALAPPDATA%\Programs\Fluxion"` → trova `Fluxion.exe`. Avvio bounded (`Start-Process`, poll `tasklist` a 20s, vivo=OK), raccogli log `%LOCALAPPDATA%\com.fluxion.desktop`. Poi `taskkill /IM Fluxion.exe /F`.
2. **VERITÀ #2 (FASE 4)**: attivazione licenza Ed25519 6-campi (dal Worker prod) → `activate_license_v1`/`verify_strict` → scrittura **Windows Credential Manager** (`cmdkey /list`, keyring 3.6) → `license_cache` SQLite popolata → feature gated sbloccate.

## ALTERNATIVA TECNICA (se founder NON disponibile e si vuole autonomia totale)
Per rendere l'install headless-capable servirebbe: patchare `installer-hooks.nsh` aggiungendo `/SD IDOK`/`/SD IDYES` a ogni `MessageBox` (così silent auto-risponde) → rebuild via CI → re-test. MA: anche con install silent OK, il PRIMO avvio GUI e l'inserimento licenza restano GUI-bound → il founder serve comunque per la prova visiva. Quindi 1 install fisico founder = path più corto. NON avviare il rebuild senza decisione esplicita (scope install, non toccare il resto).

## VINCOLI FOUNDER (milestone)
- **Pila 1 only, WIP=1**: (a) app si avvia Win, (b) attivazione+Credential Manager, (c) charge E2E €1, (d) magazzino 1 verticale.
- **Pila 2 CONGELATA fino al 1° CLOSED_WON**: code signing EV (~€300/anno viola zero-cost → unsigned OK per 1° cliente), hardening, GDPR e2e.

## REGOLE
- Macchina cliente: nessun refactor/tool extra oltre install+WebView2.
- PROVA per step (comando+output), STOP+report su fail, bounded (mai `-Wait` su GUI).
- IGNORA hook VOS context-budget (% RAW gonfiata, bug #27).
- NB sul PC c'è un vecchio checkout `C:\Users\gianluca\fluxion\` (build 0.1.0) — irrilevante, non toccare.
