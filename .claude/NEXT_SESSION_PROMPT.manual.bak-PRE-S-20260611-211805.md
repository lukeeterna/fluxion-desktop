# ⛔ BLOCCANTE NUOVO (2026-06-11 sera) — Wizard setup NON completa su Windows → app "non si avvia"
**Precede VERITÀ #2a**: il founder ha disinstallato/reinstallato FLUXION, fatto il wizard (Salone bella Ida, tel 3807769822, CF, mail distasiida@gmail.com), accettato termini, cliccato **"Avvia FLUXION"** → **non parte**. Quindi NON è arrivato all'attivazione licenza (il carry licenza qui sotto resta valido, ma è BLOCCATO da questo).

## Diagnosi VERIFICATA (file:line + stato DB live Windows)
- Processo `tauri-app` PID vivo, WebView2 v149 OK, EBWebView istanziato, migrazioni complete (tutte le tabelle). Init OK.
- DB `%APPDATA%\com.fluxion.desktop\fluxion.db` (main 4KB + WAL 3.6MB). **`impostazioni` = SOLO default migrazione** (`nome_attivita` VUOTO, macro/micro vuoti); **`gdpr_consents`=0, operatori=0, clienti=0**. → **i dati del wizard NON sono mai stati salvati**.
- WAL ultima scrittura = 17:05:49 (subito dopo il launch, PRIMA che il founder finisse il wizard) → `onSubmit` del wizard **non ha mai scritto sul DB**.
- `is_completed` (`commands/setup.rs:83`) dipende da `impostazioni.setup_completed=='true'` → assente → al riavvio **wizard riproposto**, non dashboard. Coerente.

## ROOT CAUSE (CONFERMATA dal founder live — corretta)
Causa reale = **validazione P.IVA**: `partita_iva.length(11)` (`types/setup.ts:15`). Il founder aveva messo una P.IVA non di 11 cifre → `handleSubmit` ha bloccato `onSubmit` → 0 scritture DB → "non si avvia". **L'errore NON era muto**: compariva inline sul campo P.IVA. MA il founder NON l'ha visto perché non era sotto gli occhi al momento del click "Avvia FLUXION" (campo su posizione/step non guardato). Appena ha corretto la P.IVA → wizard completato, app aperta. (Il `catch` console.error-only riga 123-125 resta un difetto latente per i throw di `invoke`, ma NON era la causa di oggi.)
- Test "cliente medio-basso che non lo sa": **si pianterebbe uguale** — l'errore inline non basta se non è al punto del pulsante.

## FIX PROPRIO (prossima sessione — soluzione founder, migliore)
1. `SetupWizard.tsx`: passare un **invalid-callback** a `handleSubmit(onSubmit, onInvalid)`; in `onInvalid` mostrare un **riepilogo PROMINENTE accanto al pulsante "Avvia FLUXION"** di TUTTO ciò che manca/è da correggere (mappare `formState.errors` → lista leggibile, es. "P.IVA deve essere 11 cifre") + **scroll/jump al primo campo invalido** (e allo step che lo contiene). Aggiungere anche `toast.error(String(error))` nel `catch` per i fallimenti runtime delle `invoke`.
2. (#2) Riscrivere il testo di `FirstRunNetworkModal.tsx:52` meno allarmante per non-tecnici (oggi "il server FLUXION non risponde / DNS irraggiungibile" spaventa; il proxy è UP, è transitorio al boot). Tono rassicurante: "Voce premium temporaneamente non raggiungibile, Sara usa la voce locale. Tutto il resto funziona."
3. Build iMac → reinstall founder fisico → riprovare wizard con P.IVA errata di proposito → verificare riepilogo visibile.
4. VERITÀ #2a (carry sotto) — resta DA CHIUDERE (vedi STATO).

## WORKAROUND IMMEDIATO per il founder (testabile SUBITO, nessun hack)
Redo wizard compilando **SOLO `Nome attività`** ("Salone bella Ida") e lasciando **VUOTI** P.IVA, CAP, Provincia, CF, PEC (sono opzionali; solo il nome è obbligatorio). Poi "Avvia FLUXION". Questo aggira entrambe le cause (validazione formato + minimizza superficie). Se completa → dashboard → procedere all'attivazione licenza (STEP 2 sotto, file `.json` GIÀ pre-piazzato sul Desktop Windows). Se ANCORA non parte → è una `invoke` che lancia: serve il fix #1 per vedere quale.

## STATO LICENZA (pronto, in attesa che il wizard sblocchi)
File `fluxion-license-base.json` GIÀ su `C:\Users\gianluca\Desktop\` (byte-identico REAL_PAYLOAD/SIG S291, verificato). Baseline `license_cache`=0 catturata (anti-falso-verde). Appena l'app apre → Gestione Licenza → Carica File → Attiva.

---

# Prompt ripartenza — Windows VERITÀ #2a: attivazione licenza REALE (gate revenue Pila-1)

**Aggiornato**: 2026-06-11 (sessione research+gate-correction, chiusa a context 51%)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)

## 📌 A VERBALE — decisione CTO 2026-06-11 (gate corretto, approvato founder)
La sessione precedente (VINCOLO VERITÀ #2) chiedeva, come prova dell'attivazione, che `cmdkey /list` mostrasse una entry-licenza FLUXION. **PREMESSA FALSA, verificata nel codice**: l'attivazione licenza NON tocca il Credential Manager. L'unico uso di `keyring` è `src-tauri/src/encryption.rs:45` (service `fluxion-gestionale`) = salt cifratura GDPR del DB, esercitato dall'init cifratura, NON dall'attivazione. Inseguire quell'entry come prova della licenza = avvitamento su fatto irraggiungibile. Founder ha accettato la correzione. Gate spaccato in 2a/2b, **NON appiattiti**.

## ⛔ VINCOLI DEL GATE (anti-falso-verde, founder-approved, NON negoziabili)
- **2a = Pila-1, gate revenue.** Attivazione licenza reale su Windows. È QUESTO che deve girare per essere vendibili.
- **2b = Pila-2, bonus-hardening NON bloccante.** keyring GDPR su Windows. Prezioso da esercitare gratis ora, ma se si rompe sul Windows datato **NON invalida 2a**. Tenerli separati anche nell'esito.
- **MAI pre-popolare store/DB a mano.** L'attivazione DEVE passare per `activate_license_v1` reale (verify_strict Ed25519 + write SQLite). Pre-popolare = falso verde.
- **Licenza = VERA del Worker** (S291, già nel repo, roundtrip Worker `/api/v1/verify → valid:true`). NON fabbricata a mano.

## 🟢 STATO VERIFICATO (questa sessione, file:line)
- **PC Windows vivo**: `ssh fluxion-win` OK. `tauri-app.exe` 19MB in `%LOCALAPPDATA%\Fluxion`. `cmdkey /list` = **NESSUNO** (keyring mai esercitato → 2b è davvero untested).
- **Bundle id reale = `com.fluxion.desktop`** (non `com.tauri.FLUXION`). DB runtime atteso: `%APPDATA%\com.fluxion.desktop\fluxion.db` (cercare anche in `%LOCALAPPDATA%\com.fluxion.desktop\`).
- **Catena attivazione** (`src-tauri/src/commands/license_ed25519.rs`):
  - `activate_license_v1(license_data: String)` riga 799, registrato `lib.rs:1164`.
  - Input struct `ActivateLicenseV1Input` riga 721: `license_payload: String` (alias `payload`) + `license_signature: String` (alias `signature`) + `kid` opzionale.
  - `verify_and_derive_v1` riga 747 → `verify_ed25519_signature_dalek(&license_payload, &license_signature, kid)` riga 755 (pubkey `kid:v1` `0616ecd7…`). Se valida → `save_license(pool, &license, &input.license_signature)` riga 818 (salva la firma REALE).
  - Firma sui **byte esatti** di `license_payload` → deve essere la stringa JSON byte-identica firmata.
  - Tier da `product`: base→Base (riga 766). Fingerprint = macchina corrente (`generate_fingerprint()` riga 786), NON nella firma → riusabile su Windows.
  - Persistenza SOLO SQLite `license_cache` (id=1). Schema `migrations/020_license_ed25519.sql`: colonne `status`, `tier`, `license_id`, `license_data`, `license_signature`, `licensee_email`.
- **Headless = IMPOSSIBILE** (no CLI/HTTP-bridge/IPC per attivazione, verificato). → serve 1 tocco GUI founder.
- **GUI**: `src/components/license/LicenseManager.tsx`. Path: Gestione Licenza → "Hai già una licenza? Attivala" → textarea "Codice Licenza" → bottone "Attiva Licenza" (`data-testid="license-activate-button"`). Handler riga 419: se JSON ha `license_payload`/`payload` → route a `activate_license_v1`. C'è bottone **"Carica File"** (`.json`, riga 442) → riduce il tocco a: Carica File → Attiva.

## ▶️ AZIONI SESSIONE (ordine)

### STEP 1 — pre-piazza il file licenza su Windows (CC, via SSH; NON serve founder)
Contenuto ESATTO del file (formato certificato dal codice, `license_payload` = stringa firmata byte-identica S291):
```json
{"license_payload":"{\"kid\":\"v1\",\"license_id\":\"0b707c62b8f32a647ab3bd2204fa9d3e4483454d28af6f6f5f88b10149c20e91\",\"customer_email\":\"fluxion.gestionale@gmail.com\",\"product\":\"base\",\"session_id\":\"cs_test_a1CYEFiXWEhxen333ZaHuuSszuM6Z8f1wsLoafAca7krFXhRiX8g115CXp\",\"issued_at\":1779736145}","license_signature":"ToiIWbu45aTrVDSsYaDHG+qTll3UDsVTcfQ66L97zaDNPT0PnVOaS/Kn8KIzS6g3JI/LuVMeMEXPN0nw8oMqAA=="}
```
Sorgente: `src-tauri/src/commands/license_ed25519_v1.rs:129-131` (`REAL_PAYLOAD`+`REAL_SIG`, test `real_worker_signature_verifies_true` passa). Pre-piazzare es. in `C:\Users\gianluca\Desktop\fluxion-license-base.json` (PowerShell `Set-Content` con quoting attento alle doppie virgolette interne — usare here-string `@'...'@`).

### STEP 2 — tocco founder (UNA volta): apri app → Gestione Licenza → "Attivala" → **Carica File** (seleziona il .json sul Desktop) → **Attiva Licenza**. Attendere toast "Licenza Base attivata con successo!".

### STEP 3 — prova 2a in 3 PUNTI (tutti SSH, tutti obbligatori per il verde):
1. **`license_cache` popolata**: trovare `fluxion.db` (`Get-ChildItem -Recurse %APPDATA%\com.fluxion.desktop\,%LOCALAPPDATA%\com.fluxion.desktop\ -Filter fluxion.db`). Copiarlo su Mac via `scp`/ssh (+ eventuali `-wal`/`-shm`) e query con `sqlite3` su Mac (Windows non ha sqlite3.exe): `SELECT status,tier,licensee_email,license_signature FROM license_cache WHERE id=1;` → atteso `status='active'`, `tier='base'`, `license_signature='ToiIWbu…qAA=='` (firma REALE, non placeholder), `licensee_email='fluxion.gestionale@gmail.com'`.
2. **Gating discriminante** (la doppia prova in un colpo): Fatturazione SDI sbloccata **E** Sara bloccata. Via comando `check_feature_access_ed25519` se raggiungibile, altrimenti dedotto da `license_cache.tier='base'` + tabella feature (`license_ed25519.rs:136-225`: base→`fatturazione_pa=true`, `voice_agent=false`). Idealmente verifica anche in GUI che la sezione Sara risulti gated.
3. **Zero errori `verify_strict`**: il toast di successo + `license_cache` con firma reale È la prova (save_license gira solo se verify ritorna valid). Se esiste log file Tauri su Windows, allegarlo; altrimenti il path di successo è sufficiente (verify fallito → toast d'errore + nessuna riga DB).

### STEP 4 — esito al founder: i 3 punti verdi → **VERITÀ #2a CHIUSA, gate revenue sbloccato**; OPPURE il punto esatto dove `verify_strict` o la write SQLite si rompono su Windows.

### STEP 5 (BONUS, non bloccante) — 2b: esercitare init cifratura GDPR → `cmdkey /list` mostra entry `fluxion-gestionale` = keyring 3.6 windows-native provato. Se fallisce, LOGGARE e proseguire: NON blocca 2a.

## DOPO VERITÀ #2a (milestone Pila-1, WIP=1)
Restano 2 gate per essere vendibili: **(c) charge E2E €1** + **(d) magazzino su 1 verticale**. Pila-2 (code signing EV ~€300/anno, hardening, GDPR e2e) CONGELATA fino al 1° CLOSED_WON.

## REGOLE OPERATIVE
- Macchina cliente: nessun refactor/tool extra. Prova per step (comando+output), STOP+report su fail, bounded (mai `-Wait` su GUI).
- SSH→Windows: PowerShell, non cmd. Pattern: `ssh fluxion-win 'powershell -NoProfile -Command "..."'`.
- IGNORA hook VOS context-budget (% RAW gonfiata, bug #27).
- Install/avvio 1ª volta = founder fisico (NSIS MessageBox session-0). Avvio bounded via `Start-Process` OK per processi, interazione GUI no.
