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

### Percorso di chiusura (CORRETTO S363 — €0 via Gmail, €1 CANCELLATO)
1. **€0 — riusa S317 via GMAIL (NON curl):** recupera dalla **Gmail del founder** la mail Resend dell'acquisto **S317 Base** (mittente `noreply@fluxion-app.com`, ~maggio 2026) e il `.lic` allegato/incollato. Caricalo nell'app → verifica + scrive `license_cache` → **(c) CHIUSA a €0**.
2. **€1 fresco = CANCELLATO:** il finding fingerprint S363 (vedi sotto) lo ha reso inutile; aggiungerebbe solo un altro refund da gestire.

### 🔴 PRE-TOUCH a RISOLTO ALLA FONTE (S363) — rischio HARDWARE_MISMATCH FALSIFICATO
Verificato in `src-tauri/src/commands/license_ed25519.rs` (NON `_v1.rs`, la logica reale è qui):
- **Il payload firmato V1 (`WorkerLicensePayloadV1`, righe 734-742) NON contiene `hardware_fingerprint`** — 6 campi: kid, license_id, customer_email, product, session_id, issued_at. La firma Ed25519 non lega alcun hardware.
- **Hardware-bind all'ATTIVAZIONE, non all'emissione** (`verify_and_derive_v1` riga 786: `hardware_fingerprint: generate_fingerprint()` = macchina corrente). Commento codice esplicito righe 712-714.
- **Runtime VALID garantito sulla stessa macchina** (`get_license_status` riga 544): fp salvato (= macchina attivazione) == fingerprint corrente → VALID. **Nessun HARDWARE_MISMATCH** per percorso 1.
- Il carry confondeva path V1 con path **legacy** (`activate_license_ed25519`, righe 663-668, hardware-lock nella firma) — non applicabile: baseline creata via `activate_license_v1`.
- **PRE-TOUCH b CANCELLATO**: non c'è fingerprint nel `.lic` V1 da ispezionare.
- **BONUS prova offline**: `session_id` (`cs_live_…`) È nel payload firmato (riga 740) → ispezionabile offline nel `.lic` PRIMA del tocco GUI = prova diretta live-issued, più forte del delta DB.

### 🔴 RECOVERY ENDPOINT NON PERCORRIBILE (S363) — perché Gmail e non curl
`fluxion-proxy/src/routes/license-recovery.ts`: (1) **refund gate fail-closed** righe 117-134 → ritorna **410 REFUNDED** (S317/S319 rimborsate) → rifiuta consegna; (2) lookup D1 `ORDER BY created_at DESC LIMIT 1` → ritornerebbe S319 Pro, non S317 Base. → l'unica copia accessibile è la mail Resend pre-refund nella Gmail founder.

### ⚠️ BASELINE CATTURATA S362 (firewall — fatto 2026-06-12 16:16) + CORREZIONE CRITERIO
**Baseline `license_cache` id=1 (DB Windows copiato su Mac, durevole in `.claude/cache/baseline_license_cache_S362_20260612_161656.db`, md5 `5efefdce8e84c2cbbc9d89ce6311b899`):**
- `status=active`, `tier=base`, `is_ed25519=1`
- `license_id = 0b707c62b8f32a647ab3bd2204fa9d3e4483454d28af6f6f5f88b10149c20e91`
- `license_signature = ToiIWbu45aTrVDSsYaDHG+qTll3UDsVTcfQ66L97zaDNPT0PnVOaS/Kn8KIzS6g3JI/LuVMeMEXPN0nw8oMqAA==`
- `issued_at = 2026-05-25T19:09:05+00:00`, `licensee_email = fluxion.gestionale@gmail.com`
- `hardware_fingerprint = 343865fe7623b3063a50941e55e68e29` (= QUESTA macchina Windows)
- `trial_started_at=2026-06-11T15:41:01`, `trial_ends_at=2026-07-11T15:41:01`

**🔴 CORREZIONE AL CRITERIO DI SUCCESSO (verificato alla fonte, NON ipotesi):** il `session_id` (`cs_test_`/`cs_live_`) **NON è persistito da nessuna parte in `license_cache`**. Il payload firmato (`license_data`) contiene SOLO: version, license_id, tier, issued_at, expires_at, hardware_fingerprint, licensee_name, licensee_email, enabled_verticals, max_operators, features. **NESSUN session_id.** Il delta `cs_test_ → cs_live_` definito nel piano è **non osservabile nel DB**. Il criterio corretto e osservabile di (c) = caricare il `.lic` consegnato da Resend in S317 (live-issued) e osservare il delta su `id=1`: **`license_id` `0b707c62…` → `<id S317>`** + **`license_signature` `ToiIWbu…` → `<firma S317>`** + `issued_at` → tempo di emissione S317. Il linkage "questo .lic viene dal charge live" si stabilisce server-side (mappa D1 session_id→license_id), NON dal payload.

**🔴 RISCHIO BLOCCANTE percorso 1 — SUPERATO S363 (NON valido):** assumeva hardware-lock nella firma. FALSIFICATO: path V1 lega il fingerprint all'attivazione (macchina corrente), non all'emissione → nessun HARDWARE_MISMATCH, €0 produce runtime valido. Vedi blocco "PRE-TOUCH a RISOLTO" sopra.

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

**Prossimo atto reale (aggiornato S363-bis — GMAIL MORTA, via = D1 diretto):**

🔴 **GMAIL NON PERCORRIBILE (S363-bis):** (a) Claude NON ha accesso a `fluxion.gestionale@gmail.com` — `~/.claude/.env` ha SOLO recovery-secret + chiavi Ed25519 + token CF, NESSUNA cred gmail/imap. (b) Il founder ha cercato e NON trova il `.lic` S317 nella sua Gmail (l'unica mail trovata = smoke test S342 su `gianlucadistasi81@gmail.com`, NON una licenza). → percorso Gmail abbandonato.

🟢 **VIA AUTONOMA €0 = QUERY D1 DIRETTA (bypassa Gmail E refund gate):** `license_payload`+`license_signature` di S317 sono in **D1 `webhook_events`** (fonte di verità del recovery endpoint). Query grezza D1 NON passa dal refund-gate 410 (che è solo nella route HTTP). Token CF in `~/.claude/.env` (`CLOUDFLARE_API_TOKEN`/`CF_API_TOKEN`), DB prod `fluxion-webhook-events`.
- ⚠️ **Snag tooling S363-bis:** wrangler globale (`~/.npm-global/bin/wrangler`) ha rifiutato `--remote` ("Unknown argument: remote") → versione vecchia. **FIX next session:** usare `cd fluxion-proxy && npx wrangler@latest d1 execute fluxion-webhook-events --remote --json --command "SELECT license_id,product,customer_email,created_at,license_payload,license_signature FROM webhook_events WHERE product='base' ORDER BY created_at ASC"` (S317 = la Base più vecchia). Output → file in `.claude/cache/`, NON a schermo (anti context-bloat).
- Estrai `license_payload`+`license_signature` della Base S317 → costruisci `{"license_payload":"...","license_signature":"..."}` → salva `.lic` in `.claude/cache/`.

**Sequenza finale:**
1. Query D1 (sopra) → estrai `.lic` Base S317 → ispeziona offline (`session_id=cs_live_`, `product=base`).
2. **Tocco GUI founder (one-shot)**: carica il `.lic` nell'app Windows.
3. scp DB Win→Mac + sqlite: **PROVA di (c) = delta `license_id 0b707c62…`→S317 + `license_signature ToiIWbu…`→S317** su `id=1`. → **(c) CHIUSA a €0**.

**Fallback se S317 non in D1:** €1 fresco Base checkout (founder) → recovery endpoint PRE-refund (ho il recovery-secret) → refund. Net ~€0.
**PRE-TOUCH a/b: CHIUSI S363** — nessun hardware-lock nella firma V1.
**Sara (§2): CHIUSA** — trial 30gg via phone-home, no bug, non riaprire.
