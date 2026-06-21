# S379 — Installer Windows + Fragilità fingerprint + Re-bind (audit read-only)

## Done Task 1 — INSTALLER WINDOWS
**Asset Windows pubblicato:** SÌ ma SOLO in release DRAFT non servibile.
- `gh release list -R lukeeterna/fluxion-desktop`: `v0.0.0-dev`(Draft), `v1.0.1`(Latest), `v1.0.0`.
- Asset per tag (`gh api .../releases`):
  - `v0.0.0-dev` (**draft:true**) → `Fluxion_1.0.1_aarch64.dmg`, **`Fluxion_1.0.1_x64-setup.exe`** (unico installer Win), `Fluxion_aarch64.app.tar.gz`
  - `v1.0.1` (**Latest**) → **0 asset**
  - `v1.0.0` → `Fluxion_1.0.0_macOS.pkg`, `Fluxion_1.0.0_x64.dmg` (0 asset Windows)
- **URL target bottone download Windows:** `https://github.com/lukeeterna/fluxion-desktop/releases/latest/download/Fluxion_1.0.0_windows.msi` — `landing/grazie/index.html:478` (id=`btn-win`).
- **MISMATCH TERMINALE catena landing→download:** il bottone punta a `latest/download/Fluxion_1.0.0_windows.msi`. `latest` = `v1.0.1` con **0 asset**; nessun tag pubblica un asset di nome `Fluxion_1.0.0_windows.msi` (né `.exe` Win). L'unico installer Windows (`Fluxion_1.0.1_x64-setup.exe`) è nella DRAFT `v0.0.0-dev`, che `/releases/latest/` NON serve mai. → **bottone = 404, download Windows rotto.**
- Note copy disallineato: `landing/come-installare.html:254/263/279` e `public/guida-fluxion.html:222` citano `FLUXION-Setup.msi`/`FLUXION-Setup.exe` (terzo nome ancora diverso). `fluxion-proxy/src/routes/checkout-success.ts` non contiene alcun link `releases/download` (0 match).
- **BLOCKED-ON build/release:** serve pubblicare un asset Windows NON-draft con nome che combaci col bottone (o ripuntare il bottone). NON costruito nulla (read-only).

## Done Task 2 — SIZING FRAGILITÀ FORMULA
SANITY CHECK: SHA-256(input base) primi 16 byte hex = `343865fe7623b3063a50941e55e68e29` → **combacia col salvato. OK, metodo valido.**
- a) total_memory in KB (`...:8317080:Windows`) → `3e3a81d91bc159a5bd40c23ef9bad514` — diverso dal salvato 343865fe…: **SÌ**
- b) system_name "Windows 11" (`...:8516689920:Windows 11`) → `8e14706e7adde189c69dc20232517698` — diverso dal salvato 343865fe…: **SÌ**
- **Conferma:** entrambi diversi. Un cambio di UNITÀ memoria (byte→KB) o della STRINGA OS ("Windows"→"Windows 11") rompe il match fingerprint → su client già attivati un update che alteri quelle variabili genera HARDWARE_MISMATCH → re-prompt attivazione. Formula fragile (numeri sopra).

## Done Task 3 — RE-BIND: mismatch terminale o auto-guarisce?
- Le righe 712-714 NON sono una primitiva/funzione: sono un **commento doc** sopra `ActivateLicenseV1Input` (license_ed25519.rs:712-714). Il re-bind reale = `save_license(... ON CONFLICT id=1 UPDATE)`.
- **Chiamanti del re-bind:** `save_license` invocato a `license_ed25519.rs:818` dentro `activate_license_v1` (:799-830) e a `:690`. In `activate_license_v1` il fingerprint è SEMPRE rigenerato `generate_fingerprint()` a `:786` → ogni (ri)attivazione re-binda.
- **MA** il ramo HARDWARE_MISMATCH vive nel path di LETTURA `get_license_status_ed25519` (`fp != fingerprint` a :544, codice "HARDWARE_MISMATCH" a :559) che setta solo `is_valid=false`/`validation_code` — **NON chiama save_license, NON re-binda**. Nessun chiamante collega il ramo mismatch a `activate_license_v1`.
- **Verdetto mismatch terminale: SÌ** (per il path di validazione runtime). L'auto-riparazione esiste SOLO se l'utente RI-ESEGUE manualmente l'attivazione (re-incolla/ricarica la `.lic`), che re-binda via :818. Non c'è ri-bind silenzioso automatico sul mismatch.
