# NEXT SESSION — FLUXION S326

> S325 ha COMPLETATO la validazione FLUXION_MASTER (read-only, report consegnato a Luke).
> Nessuna modifica al codice applicata. S326 = decisioni Luke + design fix R-01.

## STATO
- Branch `audit/e2e-reality-check-s324`. Master intatto.
- Report validazione completo in conversazione S325 (FASE A + FASE B + divergenze MASTER).

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

## DA FARE S326 — 4 DECISIONI LUKE PENDENTI (await yes/no, NO modifiche prima):
1. **R-01 fix di design** (BLOCKER): Worker emette FluxionLicense completa OPPURE client Rust verifica LicensePayloadV1 e deriva FluxionLicense? Nodo hardware_fingerprint (no al Worker al checkout) → rinuncia hardware-lock in firma o flusso attivazione a 2 passi? → progettare in sessione dedicata dopo scelta Luke.
2. **B6**: archiviare/cancellare `scripts/license-delivery/` (LemonSqueezy)?
3. **B9**: migrare 3 route ausiliarie a `fluxion-app.com` ora o backlog?
4. **D1**: implementare SchedaPet.tsx + 4 mapping mancanti, OPPURE correggere `setup.ts` (hasScheda:false dove scheda non esiste)?

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
