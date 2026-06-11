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

### ⚠️ BASELINE ANTI-FALSO-VERDE (firewall — fare PRIMA del tocco)
La riga `license_cache` ATTUALE è già `cs_test_…`. Prima del tocco GUI del founder, **cattura via SSH la baseline corrente** (`SELECT status,tier,license_id,license_signature, json_extract(...,session_id)` o equivalente dal `license_data`/payload) e mtime del DB. La prova pulita di (c) = **delta `session_id: cs_test_ → cs_live_`** sulla riga `id=1` DOPO il tocco, non la sola presenza di una riga `active` (che esiste già). Senza questo delta documentato, "active/base/firma reale" NON prova la giuntura live.

### NON automatizzare questo gate
- **One-shot:** gira una volta per chiudere (c). In produzione chi attiva è il *cliente* = l'umano nel loop → non si automatizza mai, né ora né dopo.
- **Playwright NON pilota l'attivazione** (finestra Tauri/WebView2 nativa, non un browser). Lo strumento corretto sarebbe `tauri-driver`+`msedgedriver`, ma costruirlo per un gate one-shot costa più del gate. **Vietato build di harness per (c).**
- Tocco GUI manuale del founder, una volta. Stop.

### Caveat anti-falso-verde
S317 è stato rimborsato. Il file si attiva comunque (attivazione offline solo-firma → il refund non la blocca). Questo prova **la giuntura del charge**, NON il gate refund a runtime (D4, fail-open) — sono distinti, non conflate.

---

## 2. APERTI MINORI (non bloccano (c), non gonfiare)

- **Discrepanza Sara (check codice, ≤15 min, headless, €0):** la tabella tier dà `voice_agent=false` su Base (`license_ed25519.rs:191-200`) ma l'UI dice "Sara inclusa". O il trial è un layer separato sopra la tabella perpetua (→ promessa regge), o è incoerenza (→ bug che uccide la conversione Day 1). **In parallelo a (c), non come cancello davanti a (c).**
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
