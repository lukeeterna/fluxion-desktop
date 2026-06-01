# NEXT SESSION — FLUXION (post-S326)

> S325 = validazione read-only. S326 = Luke GO su 4 decisioni; eseguiti i 2 task leggeri (B9, B6).
> R-01 e D1 RINVIATI a sessioni DEDICATE SEPARATE (decisione Luke: context fresco per redesign sicurezza + frontend).

## STATO (aggiornato S326)
- Branch `audit/e2e-reality-check-s324`. Master intatto.
- **B9 ✅ FATTO S326**: migrati 3 sender Resend ausiliari a `licenze@fluxion-app.com` (lead-magnet.ts, diagnostic-report.ts, refund.ts) + rimossi commenti S181 obsoleti.
- **B6 ✅ FATTO S326**: `git rm -r scripts/license-delivery/` (7 file dead-code LemonSqueezy/tier clinic €1497).
- **R-01 ⏳ SESSIONE DEDICATA** (prossima, PRIMA priorità — BLOCKER revenue). Vedi sotto.
- **D1 ⏳ SESSIONE DEDICATA SEPARATA** (dopo R-01). Vedi sotto.

## ════ R-01 — SESSIONE DEDICATA (BLOCKER, fare per primo, context fresco) ════

PROBLEMA (verificato a sorgente S325/S326): firma licenza Worker↔Rust NON combacia → `is_valid=false` sempre → nessuna licenza si attiva. Revenue path morto.
- Worker firma 6 campi `LicensePayloadV1 {kid, license_id, customer_email, product, session_id, issued_at(int)}` — `fluxion-proxy/src/lib/ed25519-sign.ts:160-169`, key-order esplicito.
- Rust verifica `serde_json::to_string(&FluxionLicense)` = 11 campi (`license_ed25519.rs:335,350`; struct `:47-80`), con `hardware_fingerprint` DENTRO la firma confrontato a `:642` DOPO verify `:615`.
- Hardware-lock-in-firma IMPOSSIBILE: Worker firma al webhook Stripe, non conosce il fingerprint del cliente.

DECISIONE LUKE (GO S326) — MODELLO (b), da implementare:
1. **Worker INVARIATO**: continua a firmare `LicensePayloadV1` (6 campi, entitlement = chi ha comprato cosa). NON toccare Worker né landing.
2. **Client Rust verifica QUELLA firma**: sostituire la struct verificata con un `LicensePayloadV1` Rust a 6 campi, **stesso key-order del Worker** (`kid, license_id, customer_email, product, session_id, issued_at`), `issued_at` come **int** (unificare i tipi — oggi Rust lo ha come String RFC3339). La canonicalizzazione Rust deve produrre byte identici a `JSON.stringify` del Worker.
3. **Derivazione locale**: dopo verifica firma OK, il client costruisce/deriva la `FluxionLicense` localmente — `tier` da `product`, `enabled_verticals`/`max_operators`/`features` da tier.
4. **Hardware-lock = BIND LOCALE post-verifica**, NON dentro la firma. Al primo avvio dopo attivazione: bind a questa macchina (salva fingerprint in DB locale). Hardware-lock rigido NON è requisito (Luke accetta rischio pirateria su B2B).
5. **Ri-attivazione IN SCOPE**: reinstallo/cambio disco → percorso di ri-bind dalla stessa `email`/`license_id`. Progettare ora, non dopo il primo ticket.
6. **FUORI scope v1**: NO activation server online, NO revoca online.
7. **CHIUSURA = E2E REALE**: carta test `4242 4242 4242 4242` → webhook Stripe → D1 (license persistita) → firma → email Resend → wizard activate nell'app → licenza attivata con successo. + evidence file in `~/venture-os/state/`.
- Nota unit test `license_ed25519.rs:936-978`: passano perché firmano+verificano la stessa struct localmente; NON esercitano l'output reale del Worker → vanno aggiornati per testare contro un payload prodotto dal Worker (o un fixture del suo output canonico).
- File chiave: `fluxion-proxy/src/lib/ed25519-sign.ts`, `fluxion-proxy/src/routes/stripe-webhook.ts:515-516`, `src-tauri/src/commands/license_ed25519.rs` (struct :47-80, verify :320-354, activate :604-680, save_license, get_machine_fingerprint).

## ════ D1 — SESSIONE DEDICATA SEPARATA (dopo R-01) ════

PROBLEMA: 8 micro-verticali con `hasScheda:true` cadono in `default→SchedaBase` (vuota) — `SchedaClienteDynamic.tsx:229-278`.

DECISIONE LUKE (GO S326): NON usare `hasScheda:false`. Implementare:
1. **Creare `SchedaPet.tsx`** — schema Zod GIÀ PRONTO (`src/types/scheda-cliente.ts:480-510`, `SchedaPetSchema`). Copre i 4 micro pet (toelettatura, veterinario, pensione_animali, dog_sitter).
2. **Rimappare i 4 micro non-pet a componenti ESISTENTI** (nessun nuovo schema): dermatologo→`SchedaMedica`, logopedista→`SchedaMedica`, makeup_artist→`SchedaEstetica`, autolavaggio→`SchedaVeicoli`.
- Schemi esistenti confermati S326: Odonto, Fisio, Estetica, Parrucchiere, Fitness, Veicoli, Carrozzeria, Medica, Pet (`scheda-cliente.ts`).
- File: `SchedaClienteDynamic.tsx` (mapping switch :229-278) + nuovo `src/components/schede-cliente/SchedaPet.tsx`.
- Verifica E2E: ogni micro apre la scheda corretta, non SchedaBase vuota.

## VALIDAZIONE COMPLETATA S325 (NON rifare)

### A1 — R-01 Mismatch licenza → VERDETTO DEFINITIVO: interop Worker→Rust NON può funzionare (BLOCKER)
- Worker firma 6 campi `{kid, license_id, customer_email, product, session_id, issued_at(int)}` — `ed25519-sign.ts:160-169`, chiamato `stripe-webhook.ts:515-516`.
- Rust verifica `serde_json::to_string(&FluxionLicense)` = 11 campi diversi (`version, tier, hardware_fingerprint, expires_at, enabled_verticals, max_operators, features`; `issued_at` come String RFC3339) — `license_ed25519.rs:334-350`, struct `:47-80`, activate `:604-616`.
- Solo `license_id` in comune (e `issued_at` con tipo diverso). Firma sempre `false`.
- `hardware_fingerprint` è DENTRO la struct firmata (`:642` confronto dopo verify `:615`) → il Worker non lo conosce al checkout = impossibile produrre FluxionLicense hardware-locked firmata.
- Unit test `:936-978` passano perché firmano+verificano la stessa struct localmente — NON esercitano l'output reale del Worker. Ecco perché missed.

### A2 — Secret Worker: TUTTI E 4 PRESENTI ✅
`STRIPE_WEBHOOK_SECRET`, `STRIPE_SECRET_KEY`, `RESEND_API_KEY`, `ED25519_PRIVATE_KEY_PKCS8` (nome reale, non `ED25519_PRIVATE_KEY`). +9 altri (13 totali).

### A3 — 5/5 confermati: sqlx 0.7 (`Cargo.toml:31`, zero rusqlite) · FSM 14 stati (`booking_state_machine.py:98-116`) · SchedaPet assente · 8 macro×50 micro (`setup.ts:66-196`) · €497/€897 (`checkout-consent.html:125/131`).

### FASE B — conflitti doc/memoria (proposte, da applicare solo dopo OK Luke):
- B1 `PLAN.md:19/27/34` "9 verticali, €497 one-time" → 8 macro×50 micro, 2 tier €497/€897. immobiliare=micro `agenzia`, assicurazioni inesistente.
- B2 `PLAN.md:43-60` METODO = ref ROADMAP inesistenti (dangling).
- B3 `.claude/rules/voice-agent-details.md` "23 stati" → 14.
- B4 COMPILED-STATE: non in workspace (sta ~/venture-os/wiki/projects/FLUXION/) → validare a parte.
- B5 ROADMAP*.md: 0 file nel repo (già rimossi).
- B6 `scripts/license-delivery/*` = stack LemonSqueezy + tier `clinic` €1497 STALE/dead-code.
- B7 `main.py:6/442/475/1112` "4-layer" → 5-layer (L0-L4).
- B8 zero ref `rusqlite` nel codice (= sqlx 0.7).
- B9 SOLO 3 route ausiliarie su `onboarding@resend.dev` (`lead-magnet.ts:276`, `diagnostic-report.ts:186`, `refund.ts:187`). PATH LICENZA OK: `email/sender.ts:33/51` + `stripe-webhook.ts:186/205` usano `licenze@fluxion-app.com`.

### DIVERGENZA MASTER↔codice (correggere nel MASTER):
- **D1**: schede rotte NON solo pet. `SchedaClienteDynamic.tsx:229-278` → 8 micro `hasScheda:true` cadono in `default→SchedaBase`: 4 pet (toelettatura/veterinario/pensione_animali/dog_sitter) + dermatologo + logopedista + makeup_artist + autolavaggio.
- **D2**: `issued_at` tipo diverso (int vs String) oltre allo schema.
- **D3**: secret nome reale `ED25519_PRIVATE_KEY_PKCS8`.

## 4 DECISIONI — TUTTE RISOLTE S326 (GO Luke):
1. **R-01** → GO modello (b). Eseguire in SESSIONE DEDICATA (vedi blocco R-01 sopra). ⏳
2. **B6** → GO. ✅ FATTO S326 (`git rm -r scripts/license-delivery/`).
3. **B9** → GO migrare ora. ✅ FATTO S326 (3 sender → `licenze@fluxion-app.com`).
4. **D1** → GO SchedaPet.tsx + 4 rimappature (NO hasScheda:false). Eseguire in SESSIONE DEDICATA separata (vedi blocco D1 sopra). ⏳

## 3 VERIFICHE MIRATE S325 (read-only, già fatte — NON rifare):

### CHECK 1 — Riassegnazione slot su disdetta: notifica ESISTE_NON_TESTATO · auto-rebook ASSENTE
- Waitlist notify: `orchestrator.py:4798-4803` (GAP-P1-7), `reminder_scheduler.py:351-419` (poll 5min, WhatsApp "SI entro 2h"), endpoint `main.py:406,941-951`.
- `CANCELLED` handler passivo `booking_state_machine.py:973-978`; Rust `appuntamenti.rs:756-777` soft-delete+audit.
- NESSUN auto-booking: `_mark_waitlist_notified` solo timestamp → cliente risponde SI → nuova sessione voce.

### CHECK 2 — GDPR:
- **"conformitas" ASSENTE** (0 match workspace). Compliance nativa: migr `018_gdpr_audit_logs.sql`+`037_gdpr_art9_consent.sql`+`audit.rs`.
- Audit-trail backend VERIFICATO (cablato `clienti.rs:326/412/448`), **UI ASSENTE**.
- Consenso schema VERIFICATO (`SetupWizard.tsx:106-118`), **revoca SCAFFOLD** (no `revoke_consent`).
- **Schede mediche PLAINTEXT** (`schede_cliente.rs` note_cliniche/diagnosi/allergie zero crypto; encrypt `clienti.rs:263-308` solo 11 PII anagrafici). **Gate Art.9 `has_art9_consent`(`audit.rs:459`) NON enforced** prima scritture sanitarie. [FINDING NUOVO peggiore di S324]

### CHECK 3 — Sales/video:
- SalesAgentWA `agent.py:296-365` CLI completa ma MAI eseguito: `leads.db` ASSENTE, logs vuoti, `bs4` non installato. ESISTE_NON_TESTATO.
- **Video-factory VERIFICATO/ESEGUITO** (NON `build_video.py` ma `video-factory/run_all.py`): 9 storyboard + 9 verticali `_final_*.mp4` + landing v4, Veo3 €143.75/24 call (`output/veo3_cost_log.json`). [SMENTISCE audit ESISTE_NON_TESTATO]
- Dashboard "score" ASSENTE (dashboard.py=funnel AARRR; `Analytics.tsx`=business cliente finale, non lead-score).

### CORREZIONI MASTER: (1) video-factory = VERIFICATO non ESISTE_NON_TESTATO. (2) conformitas inesistente. (3) schede mediche plaintext + Art.9 non enforced = finding nuovo.
