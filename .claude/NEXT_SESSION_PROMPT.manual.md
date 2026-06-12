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

- **Discrepanza Sara — VERIFICATA S362 (backend dice OFF su Base):** `get_license_status` (`license_ed25519.rs:570-573`) restituisce al frontend `features` parsato dalla colonna `features` (per Base `voice_agent=false`), fallback `for_tier` solo se parse fallisce. Il `trial_ends_at` (2026-07-11) è popolato MA **non consultato dopo l'attivazione**: il ramo days_remaining a :517 fira solo `if status=="trial"`; con `status=="active"` va al ramo `expiry` (:528, null) → Lifetime. **Nessun layer-trial sovrascrive `voice_agent` per active/base.** → Backend autorevole: **Sara OFF su Base attivata.** Resta UN solo grep da fare (next session, €0): il gate Sara nel **frontend** legge `features.voice_agent` (→ allora "Sara inclusa" è BUG che uccide conversione Day 1, fix prima di vendere) o legge `trial_ends_at` direttamente (→ promessa regge ma incoerenza concettuale). Pendente quel grep, l'ipotesi forte = **incoerenza/bug**. `trial_started/ends_at` su una riga active = vestigiale (scritto da `init_trial_if_needed` :373 prima dell'attivazione). **In parallelo a (c), non cancello davanti a (c).**
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

**Prossimo atto reale:** §1 percorso 1 — cattura baseline `cs_test_` via SSH, poi recupera da Gmail il file `cs_live_` di S317 e caricalo nell'app, verifica delta a `cs_live_`. Check Sara (§2) in parallelo.
