# Prompt ripartenza — Windows: VERITÀ #1 GREEN (app gira), prossimo = VERITÀ #2 attivazione licenza

**Aggiornato**: 2026-06-10 (sessione install+avvio Windows reale)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## 📌 A VERBALE — nota CTO (founder, 2026-06-10)
VERITÀ #1 è chiusa per davvero, e bene. Non è la solita CI verde — è prova multipla e fisica: install reale, due processi `tauri-app` vivi a 20s senza crash, e soprattutto la dir `EBWebView` creata, firma che WebView2 si è inizializzato davvero (non un processo zombie). Il muro di due anni — "FLUXION non ha mai girato su Windows" — è caduto con evidenza, non con un'affermazione. **A verbale netto: l'app gira sull'OS dei clienti.**
CC ha fatto la cosa giusta documentando il limite headless (hook NSIS `MessageBox` senza `/SD` appendono in session-0): non l'ha forzato, l'ha nominato. Disciplina corretta.

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

### ⛔ VINCOLO VERITÀ #2 (anti-falso-verde) — founder, NON negoziabile
L'attivazione DEVE passare per il comando reale `activate_license_v1` (che esegue
`verify_strict` + scrittura keyring). NON pre-popolare lo store / il DB a mano:
quello SALTA i due anelli WINDOWS-UNTESTED (verifica firma + Credential Manager)
e produrrebbe un falso verde.
Vie ammesse: (a) comando Tauri/CLI che invoca l'attivazione reale headless, se
esiste — cercarlo PRIMA; (b) founder incolla la chiave in GUI una volta sola.
La via "pre-popola store" è VIETATA come scorciatoia di test.
Prova richiesta = i 3 side-effect post-attivazione-reale: `cmdkey /list` mostra
entry FLUXION · `license_cache` popolata · feature sbloccate. Tutti e tre, o è KO.

### Catena da provare (su Windows reale)
`activate_license_v1` riceve la chiave → `verify_strict` valida la firma Ed25519 → keyring scrive sul **Windows Credential Manager** → `license_cache` SQLite si popola → feature gated sbloccate. Se salti un anello, non hai provato l'attivazione: l'hai bypassata.

### Step
1. **Licenza test = licenza VERA del Worker live**, NON fabbricata a mano (altrimenti `verify_strict` la rifiuta giustamente e non sai se è colpa della chiave o del codice). Chiave dal Worker prod (`fluxion-app.com` / `fluxion-proxy.gianlucanewtech.workers.dev`), **6 campi, firmata davvero**. Verificare il formato col codice di attivazione lato Rust (`activate_license_v1` / `verify_strict` in `src-tauri/src/`).
2. **Invocare l'attivazione REALE** (vedi VINCOLO sopra):
   - (a) cercare PRIMA un comando Tauri/CLI/IPC/HTTP-bridge che invochi `activate_license_v1` headless;
   - (b) se non esiste headless → founder incolla la chiave in GUI **una volta sola** (un tocco), poi tutti i side-effect li legge CC via SSH.
   - (b-store) pre-popolare store/DB = **VIETATO** (falso verde).
3. **Verificare i 3 side-effect (100% SSH, tutti e tre obbligatori)**:
   - Windows Credential Manager: `ssh fluxion-win "cmdkey /list"` → entry FLUXION presente (keyring 3.6).
   - `license_cache` SQLite popolata: trovare il .db in `%LOCALAPPDATA%\com.fluxion.desktop\` o `%APPDATA%`, query tabella.
   - Feature gated sbloccate (Sara etc.).
4. **Esito da mandare al founder**: i 3 side-effect verdi → VERITÀ #2 chiusa; OPPURE il punto preciso dove `verify_strict` o il keyring si rompono su Windows.

## VINCOLI FOUNDER (milestone)
- **Pila 1 only, WIP=1**: (a) app si avvia Win ✅FATTO, (b) attivazione+Credential Manager ⏳, (c) charge E2E €1, (d) magazzino 1 verticale.
- Dopo VERITÀ #2 verde resta solo (c) charge E2E €1 + (d) magazzino su 1 verticale → poi sei vendibile. Due gate, entrambi sì/no con prova.
- **Pila 2 CONGELATA fino al 1° CLOSED_WON**: code signing EV (~€300/anno viola zero-cost → unsigned OK per 1° cliente), hardening, GDPR e2e.

## REGOLE
- Macchina cliente: nessun refactor/tool extra. PROVA per step (comando+output), STOP+report su fail, bounded (mai `-Wait` su GUI).
- IGNORA hook VOS context-budget (% RAW gonfiata, bug #27).
- SSH→Windows: PowerShell gestisce il quoting meglio di cmd (cmd con `\"` annidati dà exit 255). Pattern che funziona: `ssh fluxion-win 'powershell -NoProfile -Command "..."'` (bash single-quote esterno protegge tutto, `$_` resta letterale, per single-quote PS interno usa `'\''`).
- NB vecchio checkout `C:\Users\gianluca\fluxion\` (0.1.0) — irrilevante, non toccare.
