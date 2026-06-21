# Prompt ripartenza — S380 (post S379: Punto 1/2/3 chiusi + scoperto 404 installer Windows)

## 🟢 PILA-1 — 3 punti chiusi
- **Punto 1** CHIUSO per sorgente (S379) + S378. `license_ed25519.rs:544/:558` confronta la colonna **`fingerprint`** (POPOLATA `343865fe…`, scritta all'attivazione `:436`/`:786`), NON `machine_id` (vuoto, irrilevante). `fp == runtime` verificato → niente HARDWARE_MISMATCH. La premessa "§10 confrontava machine_id vuoto" era ERRATA: S378 confrontava il campo giusto. Re-prompt eventuale = legacy orfano (0 mount, riconfermato) o build vecchia.
- **Punto 2** CHIUSO (S379, commit `dfd0330`): wording `LicenseManager.tsx:168` `"bloccato su questo Mac"` → `"licenza attiva"` (node-lock non implementato, dicitura neutra). type-check+lint PASS.
- **Punto 3** CHIUSO (S377): success_url landing puntano ai link Stripe buoni (`…24003` Base / `…24004` Pro).

## 🟡 GIUDICE — atteso verdetto su METODO Punto 1
Prompt self-contained pronto: `.claude/cache/s379-punto1-giudice.md` (aperto in TextEdit S379). Quando Luke incolla la risposta → ingerirla PRIMA di agire. Punto 1 è chiuso per fatto; il giudice valida/contesta il metodo (prova-per-costruzione) e il rischio drift (sotto).

## 🔴 NUOVO — INSTALLER WINDOWS 404 (priorità, BLOCKED-ON build/release)
Catena landing→download ROTTA per Windows (audit S379, `.claude/cache/s379-installer-fingerprint-sizing.md`):
- Bottone `landing/grazie/index.html:478` → `releases/latest/download/Fluxion_1.0.0_windows.msi` = **404**.
- Asset Windows `Fluxion_1.0.1_x64-setup.exe` esiste SOLO nella release **DRAFT** `v0.0.0-dev`. "Latest" `v1.0.1` ha 0 asset; `v1.0.0` solo macOS.
- → Cliente pagante che clicca "scarica Windows" oggi prende un 404. **Blocca la consegna a un cliente che paga ORA.**
- Fix S380: pubblicare l'asset Windows `v1.0.1` come release non-draft (servita da `/latest`) + allineare URL bottone a nome-file/tag reali. Richiede build/release publish (BLOCKED-ON build). NON node-lock.

## 🟠 DEBITO LATENTE — fragilità formula fingerprint (sizing S379, confermato coi numeri)
Stessa macchina pagante, cambiando UNA variabile:
- `total_memory` KB invece di byte (`8317080`) → `3e3a81d9…` ≠ salvato (SÌ diverso).
- `system_name` "Windows 11" invece di "Windows" → `8e14706e…` ≠ salvato (SÌ diverso).
- Re-bind `:712-714` è un COMMENTO, non cablato. Mismatch `:544/:559` = **TERMINALE** (auto-heal solo se l'utente re-incolla la licenza).
- → Un update futuro che cambi versione `sysinfo` (unità memory) o stringa OS manderebbe i clienti GIÀ ATTIVATI in re-prompt terminale. Hardening = fingerprint versionato/normalizzato (task separato, NON urgente, NON node-lock). Coperto dalla domanda #3 del prompt-giudice.

## Ordine S380
1. SE arrivato: ingerire verdetto giudice su Punto 1 (file giudice sopra).
2. PRIORITÀ: fix 404 installer Windows (publish release v1.0.1 Windows non-draft + URL bottone). BLOCKED-ON build.
3. (dopo, non urgente) hardening formula fingerprint se il giudice lo richiede.

## NON toccare: node-lock Q4/Q6, Q5/T2/T3 (verde), wording Punto 2 (fatto), sistema licenza legacy orfano.
⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → fonte = ultimo commit.
