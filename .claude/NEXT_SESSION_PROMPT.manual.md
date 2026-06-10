# Prompt ripartenza — Windows: VERITÀ #1 GREEN (app gira), prossimo = VERITÀ #2 attivazione licenza

**Aggiornato**: 2026-06-10 (sessione install+avvio Windows reale)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## 🟢 ACCESSO PC WINDOWS = STABILE
- `ssh fluxion-win` (key-auth Ed25519, host in `~/.ssh/config`). User `gianluca` (admin), `alessiamanuel\gianluca`.
- Win10 22H2 build 19045 x64, ~152GB liberi C:. Solo key-auth (`2504`=PIN Hello, non password).
- Anti-sleep applicato (standby/hibernate/monitor-timeout 0 su AC + lid action 0). SSH regge.

## 🟢🟢 VERITÀ #1 — "l'app si avvia su Windows?" = SÌ (blocco di 2 anni ROTTO, prova multipla)
- **Install fatta FISICAMENTE dal founder** (doppio-click GUI). L'install headless via SSH NON è possibile: hook NSIS `installer-hooks.nsh` usano `MessageBox` senza `/SD` → in session-0 nessun desktop → installer appeso. Documentato, non riprovare headless.
- Versione installata = **1.0.1** (da registro Uninstall). Aveva rilevato una vecchia 0.1.0 → founder ha scelto "modifica/installa componenti" (corretto: sovrascrive, preserva DB).
- **Install path NON standard**: `C:\Users\gianluca\AppData\Local\Fluxion` (NON sotto `Programs\`). Binario principale = **`tauri-app.exe`** (19MB) + sidecar `voice-agent.exe` (417MB) + `uninstall.exe`.
- **Avvio verificato (SSH bounded)**: `Start-Process tauri-app.exe` → 2 processi `tauri-app` vivi a 20s (PID 37MB+42MB, modello multi-processo WebView2) → niente crash.
- **Prova webview reale**: creata dir `%LOCALAPPDATA%\com.fluxion.desktop\EBWebView\...` (data store WebView2 generato solo se il webview si inizializza). Processo killato pulito.

## 🟡 VERITÀ #2 — PROSSIMO STEP (FASE 4): attivazione licenza + Windows Credential Manager
Tutto SSH-verificabile (no founder). Obiettivo: provare che l'attivazione licenza funziona su Windows reale.
1. **Generare/recuperare licenza test Ed25519 6-campi** dal Worker prod (`fluxion-app.com` / `fluxion-proxy.gianlucanewtech.workers.dev`). Verificare formato col codice di attivazione lato app.
   - Comandi attivazione lato Rust: `activate_license_v1` / `verify_strict` (cercare in `src-tauri/src/`).
2. **Avviare l'app** (`tauri-app.exe`), inserire la licenza. Problema: l'inserimento licenza è GUI → o (a) si guida l'attivazione via IPC/HTTP bridge se esposto, o (b) si pre-popola lo store, o (c) founder incolla la chiave 1 volta nella GUI. Verificare se esiste un comando Tauri/CLI per attivare senza GUI PRIMA di chiedere al founder.
3. **Verificare side-effects** (questi sì 100% SSH):
   - Windows Credential Manager: `ssh fluxion-win "cmdkey /list"` → deve comparire entry FLUXION (keyring 3.6 scrive lì).
   - `license_cache` SQLite popolata: trovare il .db in `%LOCALAPPDATA%\com.fluxion.desktop\` o `%APPDATA%`, query tabella.
   - Feature gated sbloccate (Sara etc.).

## VINCOLI FOUNDER (milestone)
- **Pila 1 only, WIP=1**: (a) app si avvia Win ✅FATTO, (b) attivazione+Credential Manager ⏳, (c) charge E2E €1, (d) magazzino 1 verticale.
- **Pila 2 CONGELATA fino al 1° CLOSED_WON**: code signing EV (~€300/anno viola zero-cost → unsigned OK per 1° cliente), hardening, GDPR e2e.

## REGOLE
- Macchina cliente: nessun refactor/tool extra. PROVA per step (comando+output), STOP+report su fail, bounded (mai `-Wait` su GUI).
- IGNORA hook VOS context-budget (% RAW gonfiata, bug #27).
- SSH→Windows: PowerShell gestisce il quoting meglio di cmd (cmd con `\"` annidati dà exit 255). Pattern che funziona: `ssh fluxion-win 'powershell -NoProfile -Command "..."'` (bash single-quote esterno protegge tutto, `$_` resta letterale, per single-quote PS interno usa `'\''`).
- NB vecchio checkout `C:\Users\gianluca\fluxion\` (0.1.0) — irrilevante, non toccare.
