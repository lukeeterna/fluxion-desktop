# FLUXION — Feature Audit (READ-ONLY) — 2026-06-08

Audit di due feature con prove dal filesystem. Nessuna modifica/build/deploy eseguita.
Tassonomia: ❌ ASSENTE · 📝 SCRITTO_NON_TESTATO · 🧪 TESTATO_LOCALE · 🚀 FUNZIONANTE_VERIFICATO.

---

## PARTE 1 — MAGAZZINO CON ALERT SOTTOSCORTA AUTOMATICI

| Strato | Stato | Prova |
|--------|-------|-------|
| 1.1 Data model | ❌ ASSENTE | `Grep` su `src-tauri/migrations` per `magazzino\|giacenz\|scorta\|sottoscorta\|soglia\|riordino\|inventory\|stock\|warehouse\|reorder\|min_stock\|low_stock\|quantit` → soli match NON pertinenti: `006_pacchetto_servizi.sql:19 quantita` (servizi pacchetto), `005_loyalty:16 loyalty_threshold`, `025_operatori_commissioni.sql:13/20 soglia_bonus/soglia_fatturato`, `007_fatturazione:158 quantita` + `041:134 quantita` (righe fattura). Nessuna tabella articoli/prodotti/giacenze/movimenti. Le 44 migration esaminate non contengono inventario. |
| 1.2 Backend (Rust/sqlx) | ❌ ASSENTE | `Grep` su `src-tauri/src` per `magazzino\|giacenz\|scorta\|sottoscorta\|riordino\|inventory\|stock\|warehouse\|reorder\|min_stock\|low_stock` → **No matches found**. Nessun comando di carico/scarico/lettura stock/set soglia. Il file più vicino, `commands/supplier.rs`, gestisce fornitori/ordini, non giacenze. |
| 1.3 Logica alert | ❌ ASSENTE | Nessun calcolo `giacenza < soglia` esiste: dipende da 1.1/1.2 entrambi assenti (vedi grep sopra). |
| 1.4 **AUTOMATICI (il cuore)** | ❌ ASSENTE | Non esiste né alert automatico né query manuale: zero codice inventario in backend e DB. Non c'è rilevamento all'apertura app, a ogni movimento, schedulato, né badge/notifica sottoscorta. |
| 1.5 UI | ❌ ASSENTE | `Glob src/pages/*.tsx` → Operatori, VoiceAgent, Calendario, Servizi, Analytics, Dashboard, Impostazioni, Fornitori, Cassa, Fatture, Clienti. **Nessuna pagina Magazzino/Inventario.** `Grep src/` per termini warehouse → **No matches found**. |
| 1.6 Catena E2E | ❌ ASSENTE | Nessun anello esiste (UI/comando/DB/alert tutti assenti). |
| 1.7 Test | ❌ ASSENTE | Nessun test possibile su codice inesistente (grep backend a 0). |

**Quanto c'è di adiacente (NON è magazzino):**
- `016_suppliers.sql` — `suppliers`, `supplier_orders` (items = JSON, **nessuna giacenza**), `supplier_interactions`.
- `031_listini_fornitori.sql` — `listini_fornitori` / `listino_righe` (`codice_articolo`, `descrizione`, `prezzo_acquisto`, `ean`) / `listino_variazioni`. È import listini-prezzo fornitori, **non** quantità a magazzino né soglie.

### VERDETTO P1
**Magazzino-con-alert-automatici = ❌ ASSENTE (zero strati).** Per un'estetista che lo usi manca *tutto*, ordinatamente:
1. Migration schema: tabella `articoli` (con `giacenza`, `soglia_minima`), tabella `movimenti_magazzino` (carico/scarico).
2. Comandi Rust sqlx: `crea/lista articoli`, `registra movimento` (aggiorna giacenza), `set soglia`, `lista sottoscorta`.
3. Logica alert: query `giacenza <= soglia_minima` + **trigger automatico** (es. al boot / dopo ogni scarico / badge sidebar / notifica).
4. UI React: pagina Magazzino (lista, edit soglia, evidenza sottoscorta) + hook + route.
5. Catena E2E cablata + test (Rust su movimenti, vitest su UI alert).

---

## PARTE 2 — SUPPORTO / INSTALLER WINDOWS

| Strato | Stato | Prova |
|--------|-------|-------|
| 2.1 Bundle config | 📝 SCRITTO_NON_TESTATO | `tauri.conf.json:47` `targets: ["dmg","app","nsis"]` (nsis = Windows). `:48-60` blocco `windows`: `webviewInstallMode embedBootstrapper`, `wix.language it-IT`, `nsis.installerHooks ./installer-hooks.nsh`, lingue Italian/English. Windows è configurato. |
| 2.2 CI | 📝 SCRITTO_NON_TESTATO | `.github/workflows/release-full.yml:47` matrix include `windows-latest` / `x86_64-pc-windows-msvc`; `:332-333` raccoglie `bundle/nsis/*.exe` e `bundle/msi/*.msi`; `:458` artefatto `Fluxion_${VERSION}_x64-setup.nsis.zip`. Esistono anche `verify-windows-static-crt.yml` e `smoke-test-installers.yml`. È il path €0 per buildare Windows da Mac. (Esito reale delle run NON verificato.) |
| 2.3 Codice platform-specific | 📝 (gestito) | `#[cfg(target_os="windows")]`/`#[cfg(windows)]` già presenti: `commands/voice.rs:18,133`, `voice_pipeline.rs:517,666,725`, `whatsapp.rs:80`, `license.rs:178`, `preflight.rs:249`. Branch macOS-only residui = solo diagnostica disco (`support.rs:141`, `remote_assist.rs:109`) che su non-mac ritornano "Unknown"/"not available" → cosmetico, non bloccante. `preflight.rs:249` ha già il branch Windows (wmic). |
| 2.4 **NODO CRITICO: storage credenziali** | 📝 SCRITTO_NON_TESTATO (cross-platform) | `Cargo.toml:58` `keyring = { version = "3.6", features = ["apple-native", "windows-native"] }` → **già cross-platform** (macOS Keychain + Windows Credential Manager). `encryption.rs:16,45` usa `keyring::Entry` per il salt PBKDF2; commento `:41` "macOS Keychain Services / Windows Credential Manager (via keyring)". **NON è macOS-only → Windows NON richiede un port di questo strato.** |
| 2.5 Altro macOS-lock | 📝 (cross-platform) | Fingerprint licenza `license.rs:145-158` = `hostname + cpu_brand + total_memory` via crate `sysinfo` (cross-platform, **nessun** IORegistry/system_profiler). Path DB `lib.rs:163-171` via `app.path().app_data_dir()` (Tauri, cross-platform) + `lib.rs:127` normalizza backslash Windows. Gli `/Users/...` hardcoded trovati sono **solo in `#[cfg(test)]`** (`diagnostic.rs:366`, `lib.rs:1272+`). Residuo reale: `voice_pipeline.rs:736-739` fallback path Python macOS, ma con branch Windows già presenti accanto. |
| 2.6 Artefatto Windows | ❌ non prodotto localmente | `Glob **/*.{msi,exe,nsis}` → **No files found**. Nessun installer Windows mai prodotto su questa macchina. (Eventuali artefatti su GitHub Releases NON verificati.) |

### VERDETTO P2
**Windows = (a) build-config di distanza, NON un port del livello credenziali.** Lo strato critico (keyring windows-native, fingerprint via sysinfo, app_data_dir cross-platform, license in SQLite) è già portabile; i branch `cfg(windows)` esistono; tauri.conf + CI release-full.yml producono nsis/msi. Lavoro reale onesto: **basso-medio** = (1) lanciare/verde la run CI Windows reale, (2) pulire 2-3 diagnostiche macOS-only (cosmetiche), (3) **testare a runtime su Windows reale** (boot, Keychain→Credential Manager, sidecar voice-agent, NSIS install + WebView2 bootstrapper). Niente riscrittura del livello licenza.

Passi minimi ordinati (NON eseguiti):
1. Eseguire la run CI Windows di `release-full.yml`, ottenere `.exe`/`.msi` verdi.
2. Smoke-test installer su Windows reale (NSIS + WebView2 embed bootstrapper).
3. Verificare runtime: salt in Windows Credential Manager, fingerprint stabile, attivazione licenza, avvio sidecar `voice-agent`.
4. (Cosmetico) portare disk-free di `support.rs`/`remote_assist.rs` su Windows.

---

## NON VERIFICATO / NON ACCESSIBILE
- **Esito reale delle run CI** (`release-full.yml`, `verify-windows-static-crt.yml`, `smoke-test-installers.yml`): non eseguito `gh run`, nessun accesso rete. Stato CI = ignoto.
- **Runtime su Windows**: nessun test eseguito (vietato dal mandato + non disponibile la piattaforma). Tutto P2 resta al massimo 📝.
- **`installer-hooks.nsh`** referenziato in `tauri.conf.json:56`: esistenza/contenuto non aperti in questo audit.
- **GitHub Releases remoti**: non verificato se un `.msi/.exe` sia mai stato pubblicato (controllato solo il filesystem locale → nessun artefatto).
- **`gh`/network**: non usato (read-only locale).
