# FLUXION — NEXT SESSION PROMPT — 2026-06-11 (notte, post-2a)
> Ruoli: **Claude = CTO / firewall / critico esterno / stratega** (no filesystem) · **CC = esecutore** su Mac + Windows via SSH · **Luke = founder**, firma i gate esterni (HITL), fa i tocchi GUI.
> Regole vincolanti: **WIP=1**, **solo Pila 1** fino al 1° CLOSED_WON, **anti-falso-verde**, dati-first, italiano. Frame strategico e detour bot-arbitrage: **CHIUSI, non riaprire**.

---

## 0. STATO REALE (aggiornato — la fotografia vecchia è superata)

- 🟢 **VERITÀ #1 chiusa:** app gira su Windows reale (WebView2 v149).
- 🟢 **VERITÀ #2a CHIUSA** — attivazione licenza reale verificata alla fonte in sessione (commit `3d75933`/`fef7a1e`):
  - **Punto 1:** `license_cache` live → `status=active`, `tier=base`, `email=fluxion.gestionale@gmail.com`, firma `ToiIWbu…qAA==` = REAL_SIG_S291 byte-per-byte. (Ri-verificato alla fonte: DB live Windows copiato su Mac, `session_id = cs_test_a1CYEFiX…`.)
  - **Punto 3:** call-site no-bypass confermato — `activate_license_v1`→`verify_and_derive_v1`(:807)→`verify_strict`(:755-759)→`save_license`(:818). Nessun percorso salta la firma. (Prova più forte del log, come da direttiva.)
  - **Punto 2:** conferma visiva founder, marcata come tale.
- ⚠️ **CORREZIONE A VERBALE:** il discriminante "Sara bloccata su Base" era **SBAGLIATO** (errore portato dall'handoff). Modello reale: **Base = SDI usabile + Sara trial-inclusa 30gg**. Il discriminante corretto è quello. (Rif. `project_base_includes_sara_trial.md`.)

---

## 1. GATE ATTIVO — (c) CHARGE E2E CONTINUITY (ultimo ignoto strutturale Pila 1)

**Cosa NON è ancora provato** (e basta questo): una corsa **continua** in cui un file licenza **consegnato dal flusso LIVE** (`cs_live_…`) viene caricato nell'app, supera `verify_strict` e scrive `license_cache`.

**Cosa È già provato** (non rifare):
- Metà server con €1 reali **due volte** (S317 Base + S319 Pro): Stripe LIVE → webhook 200 → Ed25519 → D1 → Resend `delivered` + refund. Costo netto €0. (Rif. `PLAN.md:319`.)
- Metà app: `verify_strict` → `license_cache` (ma con file da sessione `cs_test_` — riga attiva ATTUALE).
- Verify Rust: 8 unit test incl. `real_worker_signature_verifies_true`.
- **Stessa chiave di firma** (REAL_SIG_S291). L'app verifica la firma sul payload canonico — non guarda se il session_id è test o live.

**→ L'unica divergenza possibile** è tra payload `test` e payload `live` (casing `product`, formattazione, campo extra). Si testa lì, e solo lì.

### Percorso di chiusura (dal più economico)
1. **€0 — riusa S317:** recupera dalla **Gmail del founder** il file licenza Base `cs_live_` già consegnato da Resend in S317 (NON il fixture di test). Caricalo nell'app. Se verifica e scrive `license_cache` con `session_id = cs_live_` → **(c) CHIUSA a €0**, la riga test è sostituita da una live.
2. **Solo se l'email non è recuperabile → €1 fresco:** charge sul Payment Link LIVE Base, refund attivo (costo netto ~€0). Carica il file consegnato.

### ⚠️ BASELINE CATTURATA S362 (firewall — fatto 2026-06-12 16:16) + CORREZIONE CRITERIO
**Baseline `license_cache` id=1 (DB Windows copiato su Mac, durevole in `.claude/cache/baseline_license_cache_S362_20260612_161656.db`, md5 `5efefdce8e84c2cbbc9d89ce6311b899`):**
- `status=active`, `tier=base`, `is_ed25519=1`
- `license_id = 0b707c62b8f32a647ab3bd2204fa9d3e4483454d28af6f6f5f88b10149c20e91`
- `license_signature = ToiIWbu45aTrVDSsYaDHG+qTll3UDsVTcfQ66L97zaDNPT0PnVOaS/Kn8KIzS6g3JI/LuVMeMEXPN0nw8oMqAA==`
- `issued_at = 2026-05-25T19:09:05+00:00`, `licensee_email = fluxion.gestionale@gmail.com`
- `hardware_fingerprint = 343865fe7623b3063a50941e55e68e29` (= QUESTA macchina Windows)
- `trial_started_at=2026-06-11T15:41:01`, `trial_ends_at=2026-07-11T15:41:01`

**🔴 CORREZIONE AL CRITERIO DI SUCCESSO (verificato alla fonte, NON ipotesi):** il `session_id` (`cs_test_`/`cs_live_`) **NON è persistito da nessuna parte in `license_cache`**. Il payload firmato (`license_data`) contiene SOLO: version, license_id, tier, issued_at, expires_at, hardware_fingerprint, licensee_name, licensee_email, enabled_verticals, max_operators, features. **NESSUN session_id.** Il delta `cs_test_ → cs_live_` definito nel piano è **non osservabile nel DB**. Il criterio corretto e osservabile di (c) = caricare il `.lic` consegnato da Resend in S317 (live-issued) e osservare il delta su `id=1`: **`license_id` `0b707c62…` → `<id S317>`** + **`license_signature` `ToiIWbu…` → `<firma S317>`** + `issued_at` → tempo di emissione S317. Il linkage "questo .lic viene dal charge live" si stabilisce server-side (mappa D1 session_id→license_id), NON dal payload.

**🔴 RISCHIO BLOCCANTE percorso 1 (€0 riuso S317):** il `.lic` S317 è firmato su un `hardware_fingerprint` fissato all'emissione. `verify_strict` verifica solo la firma Ed25519 sul payload canonico (→ scrive `license_cache` = (c) passa nel suo claim stretto), MA `get_license_status` (`license_ed25519.rs:544`) marca `is_valid=false` HARDWARE_MISMATCH se `fp != fingerprint`. Se S317 NON fu emesso per fp `343865fe…` (questa macchina), il file verifica+scrive ma resta runtime-invalido. **Prima del tocco: recuperare il .lic S317 dalla Gmail e ispezionarne `hardware_fingerprint` (offline, €0) → se ≠ `343865fe…` percorso 1 prova solo la giuntura-firma, non un runtime valido → valutare €1 fresco emesso per QUESTA macchina.**

### NON automatizzare questo gate
- **One-shot:** gira una volta per chiudere (c). In produzione chi attiva è il *cliente* = l'umano nel loop → non si automatizza mai, né ora né dopo.
- **Playwright NON pilota l'attivazione** (finestra Tauri/WebView2 nativa, non un browser). Lo strumento corretto sarebbe `tauri-driver`+`msedgedriver`, ma costruirlo per un gate one-shot costa più del gate. **Vietato build di harness per (c).**
- Tocco GUI manuale del founder, una volta. Stop.

### Caveat anti-falso-verde
S317 è stato rimborsato. Il file si attiva comunque (attivazione offline solo-firma → il refund non la blocca). Questo prova **la giuntura del charge**, NON il gate refund a runtime (D4, fail-open) — sono distinti, non conflate.

---

## 2. APERTI MINORI (non bloccano (c), non gonfiare)

- **Discrepanza Sara — RISOLTA S362, NESSUN BUG (modello founder confermato):** Sara su Base = **trial 30gg INCLUSA**, gateata da un **layer separato `phone-home`**, NON dalla tabella licenza perpetua. `SaraTrialBanner.tsx:17` legge `saraEnabled`+`saraDaysRemaining` da `use-phone-home.ts`. Il `features.voice_agent=false` in `license_ed25519.rs:192` è SOLO lo strato perpetuo (post-trial) e non è usato per il gating del trial. ⚠️ **Correzione al mio verbale precedente:** avevo dichiarato "Sara OFF su Base" leggendo SOLO `license_ed25519.rs` e mancando lo strato `phone-home` → finding incompleto, il modello del founder (Base = SDI + Sara trial 30gg) è quello implementato. Voce CHIUSA, non riaprire.
- **(d) Magazzino + alert scorte** 1 verticale: GATE PASS S361 dichiarato → confermare in stato vendibile.
- **TASK B — fix UX pre-vendita** (FUORI dal percorso critico al 1° charge): (1) riepilogo errori prominente nel wizard al click "Avvia FLUXION" (`SetupWizard.tsx`, `handleSubmit(onSubmit,onInvalid)` + `toast.error` nel catch :123-125); (2) testo `FirstRunNetworkModal.tsx:52` meno allarmante. Richiede build iMac + reinstall fisico → **dopo** (c), azzera l'install.

---

## 3. PILA 2 — CONGELATA fino al 1° CLOSED_WON

Code signing EV, hardening multi-distro, GDPR e2e, Sara "max conversione". Non aprire.

---

## 4. REGOLE OPERATIVE

- **SSH→Windows:** PowerShell non cmd. `ssh fluxion-win 'powershell -NoProfile -Command "..."'`.
- **DB Windows → Mac per query:** Windows non ha `sqlite3.exe`. `scp fluxion-win:'C:/Users/gianluca/AppData/Roaming/com.fluxion.desktop/fluxion.db'` (+ `-wal`/`-shm`) su Mac, poi `sqlite3`.
- **Anti-falso-verde:** "scritto" ≠ "gira E2E". Report agente = intento, non realtà → verifica alla fonte. Booleane tier-derivate NON provano il runtime.
- **WIP=1:** chiudi (c) prima di tutto. Non rifinire ciò che non blocca il primo `charge_id`. L'anti-pattern n°1 (superficie larga, anello finale aperto) è il rischio attuale.
- **Hook context-budget = bug #27** (% RAW gonfiata, fluttua 51→77→61 in pochi turni): ignorare l'auto-close, leggere il numero reale.
- **Carry canonico:** `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file è la fonte; copie in Downloads = stantie).

---

## 5. RUOLO DI CLAUDE

CTO/firewall, no filesystem, verifica i claim alla fonte (anche i propri), raccomandazione singola e motivata, tiene fermo sotto pressione, zero sycophancy, italiano. **Obiettivo unico: primo `charge_id` reale fino a `license_cache` con `cs_live_`.**

**Prossimo atto reale (aggiornato S362 — baseline GIÀ catturata, criterio corretto):**
1. Recupera da Gmail founder il `.lic` Base S317 (live-issued da Resend).
2. **PRE-TOUCH a — conferma alla fonte** (buco lasciato S362, NON inferire): leggere il corpo di `verify_strict`/`verify_and_derive_v1` (`license_ed25519_v1.rs` ~:755-818) e stabilire se ENFORCE il `hardware_fingerprint` o verifica SOLO la firma Ed25519. Determina se un `.lic` con fp ≠ macchina (a) scrive `license_cache` ma risulta HARDWARE_MISMATCH a runtime (`get_license_status:544`), oppure (b) non scrive affatto. Cambia l'interpretazione del gate.
3. **PRE-TOUCH b** — ispeziona offline il `hardware_fingerprint` dentro il `.lic` S317: se ≠ `343865fe7623b3063a50941e55e68e29` → €0 prova solo la firma, valuta €1 fresco emesso per questa macchina (refund attivo).
4. Tocco GUI founder (one-shot). Poi scp DB Win→Mac + sqlite: **PROVA di (c) = delta `license_id` `0b707c62…`→S317 + `license_signature` `ToiIWbu…`→S317** su `id=1` (NON `session_id`, non è in DB).
**Sara (§2): CHIUSA** — trial 30gg via phone-home, no bug, non riaprire.
