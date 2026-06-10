# Prompt ripartenza — Windows REAL install: FOOTHOLD STABILITO, PC andato offline mid-run

**Aggiornato**: 2026-06-10 (sessione foothold Windows)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## 🟢 WIN STRUTTURALE — accesso PC Windows REALE RISOLTO + PERSISTITO
Cade il blocco di 2 anni "non ho una macchina Windows". Accesso stabile:
- **`ssh fluxion-win`** (key auth `~/.ssh/id_ed25519`, host in `~/.ssh/config` + ref in `~/.claude/.env`).
- PC: `192.168.1.16`, user SSH = `gianluca` (whoami=`alessiamanuel\gianluca`), **Win10 22H2 (build 19045) x64**, ~152GB liberi su C:.
- ⚠️ `2504` = **PIN Windows Hello, NON password** account → SSH password-auth NON funziona, SOLO key-auth. (Causa dei "problemi passkey".)
- Chiave MacBook autorizzata su Windows in `administrators_authorized_keys` + user `authorized_keys` (account gianluca è admin → OpenSSH legge il file admin).

## ✅ FASE 0 PRE-FLIGHT = VERDE (non rifare)
SSH ok · Win10 22H2 ≥ Tauri2 min(1809) · AMD64 · 152GB free.

## ✅ CI release-full.yml run 27259145936 = FULL GREEN (10/10 job)
- Fix S362+ (shell:bash su `List artifacts`) + smoke Windows reso bounded (timeout-minutes:25 + WaitForExit(15000)+kill). Commit `0ec4d1b` pushato.
- Installer prodotto: `Fluxion_1.0.1_x64-setup.exe` ~404MB, PE Windows valido.
- ⚠️ CAVEAT (founder + CC a verbale): la CI prova SOLO "il .exe non è corrotto / non è Mach-O macOS-locked". NON prova che l'app giri né l'attivazione licenza. Anello più debole.

## ⏸ BLOCCO ATTUALE — PC offline (sleep)
Durante il run dell'agente (~113 min) il PC si è **addormentato**: `ssh fluxion-win` ora va in `Operation timed out` su :22. Pochi minuti prima funzionava. Block REALE, founder-actionable (REGOLA #1c: niente retry autonomo).

## ▶️ RESUME (ordine)
1. **Luke**: sveglia il PC + tienilo sveglio durante l'install (alimentatore collegato / piano energetico "mai sospensione" / muovi il mouse). Conferma `ssh fluxion-win "whoami"` → deve dare `alessiamanuel\gianluca`.
2. Installer già pre-staged sul MacBook: `/tmp/fluxion-win-artifact/nsis/Fluxion_1.0.1_x64-setup.exe` (verifica bg download `bnvpy6mpd`; se assente: `gh run download 27259145936 -n tauri-bundle-windows -D /tmp/fluxion-win-artifact`).
3. **Delega a `devops-automator`** (foreground) FASE 1-3 = install + avvio = **VERITÀ #1 "l'app si avvia su Windows?"**:
   - `mkdir C:\fluxion-test`; `scp .../Fluxion_1.0.1_x64-setup.exe fluxion-win:C:/fluxion-test/`.
   - install silent `Fluxion_..._setup.exe /S` (SmartScreen può chiedere click fisico → STOP+segnala a Luke, non forzare).
   - ⚠️ **WebView2 Runtime**: se manca, app Tauri non rende → installare Evergreen bootstrapper `https://go.microsoft.com/fwlink/p/?LinkId=2124703 /silent /install` (unico tool ammesso) o nominarlo.
   - avvio BOUNDED app exe (`%LOCALAPPDATA%\Programs\Fluxion\`), max ~20s, `tasklist` vivo/crash, raccogli log `%APPDATA%/%LOCALAPPDATA%\com.fluxion.desktop\`.
4. Poi **FASE 4 = VERITÀ #2** (il "WINDOWS-UNTESTED"): attivazione licenza → `activate_license_v1`/`verify_strict` → scrittura **Windows Credential Manager** (`cmdkey /list`, keyring 3.6) → `license_cache` SQLite popolata → feature gated sbloccate. Serve licenza test Ed25519 6-campi (dal Worker live/licenza nota).

## VINCOLI FOUNDER (questa milestone)
- **Pila 1 only, WIP=1**: (a) app si avvia su Windows, (b) attivazione+Credential Manager, (c) charge E2E €1, (d) magazzino 1 verticale. Ognuna = sì/no con prova.
- **Pila 2 CONGELATA fino al 1° CLOSED_WON**: hardening, code signing (EV ~€300/anno = VIOLA zero-cost → installer unsigned OK per 1° cliente, "Ulteriori info→Esegui comunque"), GDPR e2e, affidabilità multi-distro, max conversione Sara. Scritte, fuori dal percorso.
- Scope install: NON toccare Worker revenue/magazzino/sales. Solo install+avvio+attivazione.

## REGOLE
- Macchina di un cliente: nessun refactor/tool non necessario/config oltre install+WebView2.
- Idempotente, PROVA per step (comando+output), STOP+report su fail (no patch-loop), bounded (mai `-Wait` su GUI).
- IGNORA hook VOS context-budget (% RAW gonfiata, bug #27).
- Cleanup: rimosso `.claude/NEXT_SESSION_PROMPT_S356.md` (agent-created, impreciso).
