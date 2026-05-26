# Prompt ripartenza S293 — Resend domain verify + Worker prod deploy + activate-by-payload FE flow

> ## META-VINCOLO S293 (riconfermato S290 GO Luke + S291 evidence + S292 prod infra-ready)
>
> **S292 Tauri kid:v1 verify dalek CLOSED VERDE** — 8/8 tests PASS interop con D1 reale S291 (Gate 3 evidence chiuso).
> **S292 prod infra Worker FASE A CLOSED VERDE** — D1 prod creato, migration applicata, wrangler.toml binding aggiunto, secrets ED25519 prod uploaded.
> **DEFERRED** Worker prod deploy code S291: BLOCKER Resend dominio custom non verified → customer reali email_sent=false con `onboarding@resend.dev` (sandbox solo owner).
>
> **MAI dichiarare anello CHIUSO o ring VERIFIED in prod** senza nuovo set di 3 test reali letti da Luke:
> - FDQ-01 prod: card 4242 → checkout sandbox prod → licenza firmata → email arriva (post Resend domain verify)
> - FSAF-05 prod: replay webhook prod 2x → 1 licenza + 1 email + D1 count invariato
> - Tauri activate-by-payload FE: estrai license_payload+signature da KV/email link → `invoke('verify_license_signature_v1')` → activation success.

---

## Stato chiusura S292 (CLOSED VERDE — Tauri dalek + Worker prod infra-ready)

### Done S292

1. **Pre-flight 4/5 OK**: keypair S290 ENTRAMBI persistiti (`~/.claude/.env.s290-ed25519-priv-pkcs8.b64` mode 600 + `.env.s290-ed25519-pub-raw.hex` mode 644). 4/5 env vars SET (CLOUDFLARE_API_TOKEN, STRIPE_TEST_SECRET_KEY, RESEND_TEST_KEY, STRIPE_WEBHOOK_SECRET_TEST). CLOUDFLARE_ACCOUNT_ID unset (recuperabile da `22ddff3a4ef544511523a841b3dcadf8`). Worker test health 200, D1 test 2 rows S291.

2. **Task HIGH 1 Tauri dalek verify CLOSED VERDE** (commit `25a5ede`):
   - **NEW** `src-tauri/src/commands/license_ed25519_v1.rs` (~210 lines) con `verify_ed25519_signature_dalek(payload, sig_base64, kid)` + `#[tauri::command] verify_license_signature_v1`
   - Pubkey kid:v1 const `FLUXION_PUBLIC_KEY_V1_HEX = "0616ecd7a332de86a984dfafa87eb64915c47fecca7a3b82058a2d56e01ad5d9"`
   - `verify_strict` (RFC 8032 compliant, no malleability)
   - Modulo registrato in `commands/mod.rs` + invoke_handler `lib.rs:1152`
   - **Test 8/8 PASS** su iMac (compile 1m 02s, test 0.00s):
     - `real_worker_signature_verifies_true` — D1 row S291 evt_1TaKKhI... → true
     - `tampered_payload_one_byte_returns_false` — "base" → "prox" → false
     - `tampered_signature_one_byte_returns_false` — bit flip → false
     - `unknown_kid_returns_err`
     - `malformed_signature_base64_returns_err`
     - `wrong_length_signature_returns_err`
     - `tauri_command_response_shape` + `tauri_command_defaults_kid_to_v1`

3. **Roundtrip evidence interop** Worker WebCrypto ↔ Rust dalek su same D1 row:
   - Worker `POST /api/v1/verify` payload+sig D1 reale → `{"kid":"v1","valid":true}`
   - Rust `verify_ed25519_signature_dalek(REAL_PAYLOAD, REAL_SIG, "v1")` → `Ok(true)`
   - **Interop chiuso** — Gate 3 S291 post-evidence promosso verde.

4. **Task HIGH 2 Worker PROD infra FASE A CLOSED VERDE** (commit S292 stesso):
   - **D1 prod created**: `fluxion-webhook-events` id `e065a108-7add-4a13-8f9c-2f61b1d47c9b` region EEUR
   - **Migration 0001 applied** su D1 prod: CREATE TABLE webhook_events + 3 indexes + d1_migrations row (rows_written: 6, size_after: 32768)
   - **wrangler.toml top-level** `[[d1_databases]]` aggiunto sotto KV (binding "DB" → fluxion-webhook-events)
   - **Secrets prod uploaded**: `ED25519_PRIVATE_KEY_PKCS8` (stdin da `~/.claude/.env.s290-ed25519-priv-pkcs8.b64`) + `ED25519_PUBLIC_KEY_V1` (stdin da pub hex). Stesso keypair kid:v1 prod e test (single keypair per kid, da S291 design).
   - **Worker prod deployed code attuale = VECCHIO** (pre-S291 refactor, ultimo code deploy 2026-04-30, successive solo Secret Change). **NON ho fatto `wrangler deploy`** → S291 code D1+sign+Stripe SDK v22 NON è in prod live. Infra ready, code deploy deferred.

5. **Research-first BLOCKER Resend** (REGOLA #16): `grep "from:" stripe-webhook.ts` → `from: 'FLUXION <onboarding@resend.dev>'` (sandbox Resend, solo owner email può ricevere). Deploy worker prod S291 ORA senza dominio custom = revenue blocker — customer reali email_sent=false → Stripe retry storm. **DECISIONE CTO**: infra prod ready, code deploy deferred S293 dopo Resend domain action.

### Note S292

- **Keypair file plaintext `~/.claude/.env.s290-*` ancora presente** (anti-pattern ADDENDUM S291). Migration a macOS Keychain DEFERRED S294+ (priority MED — keypair già in CF Secret prod+test, single-source-of-truth canonical). Backup locale non urgente, CF è authoritative.
- **`/api/v1/verify` debug endpoint ancora live** test env. Cleanup post-interop verified: rimuovere route OR aggiungere `Bearer ADMIN_API_SECRET` auth. LOW priority.
- **wrangler v3.114.17** still in use (v4.94.0 latest blocked Big Sur). Accettato.

### Critica strutturale S292 (REGOLA #4)

1. **Assunzione nascosta CRITICAL**: Resend sandbox `onboarding@resend.dev` rifiuta non-owner recipient → customer arbitrari email_sent=false. **Mitigation S293 mandatory**: dominio custom verified (es. `mail.fluxion.app` MX+DKIM) PRIMA di deploy worker prod code S291. Alternative: log + Discord alert `email_sent_at IS NULL > 1h` + manual replay tooling.
2. **Cosa rompe a 30/60/90gg**: nessun breaking change da infra step. Solo deploy worker prod code S291 attiva path D1+sign — fino a deploy, vecchio path KV-only stays. Rollback = no-op (deploy not done).
3. **Pattern errore noti**: D1 prod creato in region EEUR vs test WEUR — latenza neutra (entrambi EU), zero cross-region issue. wrangler.toml binding name "DB" coerente test+prod, no env-specific code branch.
4. **Sovradimensione**: secrets ED25519 prod uploaded ma non ancora usati (deploy deferred) — accettabile, upload secret è no-op runtime. KV `purchase:{email}` backward-compat preservato post-deploy (activate-by-email flow funzionante).

### Pending S293 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Resend dominio custom verify | founder + CTO | Founder action: registrare dominio (`mail.fluxion.app` o subdomain `fluxion.gianlucanewtech.com`). CTO action: aggiungere MX + DKIM + SPF a CF DNS, verify via `https://api.resend.com/domains` (POST + GET status). Update `from:` in `fluxion-proxy/src/routes/stripe-webhook.ts:152` da `onboarding@resend.dev` a verified domain. Tempo: 30min DNS propagation + 5min code change. Backlog ref: S291 MED + S286 founder backlog. |
| HIGH | Worker prod deploy code S291 | CTO | Post Resend domain: `cd fluxion-proxy && npx wrangler deploy` (no `--env`). Verifica startup log + bindings (KV+D1+Triggers visibili). Smoke test `/health` + `/api/v1/verify` (se kept) + curl Stripe webhook signing valid. |
| HIGH | FDQ-01 prod gate visivo | CTO + founder | Founder action: card 4242 prod checkout (€497 Base con coupon 100% opzionale per zero-cost test). CTO verify: D1 prod row created + signed payload + Resend ID + email arrived inbox. |
| HIGH | FSAF-05 prod gate visivo | CTO | `stripe events resend evt_xxx --webhook-endpoint we_1TRruzIW...` 2x → D1 invariato + Resend calls=1. Replay test su evento prod reale. |
| HIGH | Tauri activate-by-payload FE flow | CTO | Estensione `src/lib/activate-by-email.ts` OR nuovo `src/lib/activate-by-payload.ts`: estrai license_payload+signature da KV `purchase:{email}` (worker GET endpoint required) OR da email link (token-protected D1 read). Chiama `invoke('verify_license_signature_v1', {req:{payload,signature_base64}})` → su `valid:true` salva in localStorage + DB SQLite `license_cache.is_ed25519=1, status='active'`. Gate Tauri legacy → migration path. |
| MED | KV cleanup test entries | CTO | `wrangler kv key list --binding LICENSE_CACHE --env test` + delete `purchase:test+*`, `session:cs_test_*`, `lead:*` non utili. Riduce noise. |
| MED | /api/v1/verify endpoint cleanup | CTO | Post Tauri activate-by-payload verified: rimuovere route + `verify-signature.ts` OR add `Bearer ADMIN_API_SECRET` auth. |
| LOW | Keypair migration macOS Keychain | CTO | Backup locale via `security add-generic-password -s fluxion-ed25519-priv-kid-v1 -w "$PRIV_B64"`. RIMUOVE `~/.claude/.env.s290-*` mode 600 plaintext (anti-pattern ADDENDUM S290). CF Secret resta canonical. |
| LOW | wrangler v4 upgrade | CTO | BLOCKED Big Sur, attesa upgrade macOS o switch dev iMac. |

### Vincoli S293 (non-negoziabili)

- **REGOLA #18 META-VINCOLO**: nuovo set 3 gate (FDQ-01 prod + FSAF-05 prod + activate-by-payload FE) prima di promote ring VERIFIED PROD `chain_map['production_ready']=True`.
- **REGOLA #14/#15**: CTO autonomous tutto eccetto card 4242 real payment prod (founder browser) + domain registration billing (founder).
- **REGOLA #16 research-first**: prima di deploy prod, verify Resend domain status via API direct (no training-data guess).
- **MAI deploy worker prod codice nuovo** se health/smoke pre-deploy fail.
- **CLOSING_ONLY soglia ≥70% post system-reminders**: chiusura preventiva, no Write/Edit critical files.

### Pre-flight S293 (10s)

```bash
# 1. Env vars + keypair S290 ancora persistito
zsh -c 'for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
ls -la ~/.claude/.env.s290-ed25519-* | wc -l  # 2

# 2. Worker prod health + D1 prod state
curl -sS https://fluxion-proxy.gianlucanewtech.workers.dev/health
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
npx wrangler d1 execute fluxion-webhook-events --remote --command "SELECT count(*) FROM webhook_events;"  # atteso 0

# 3. Resend prod domain status
curl -sS -H "Authorization: Bearer $RESEND_API_KEY" https://api.resend.com/domains
# Atteso: customer domain verified (S293 founder action)

# 4. Verify Tauri test ancora passa
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo test --lib commands::license_ed25519_v1 2>&1 | tail -10"
# Atteso: 8 passed
```

### Files modificati S292 (atomic commit + push pre-Stop)

- `src-tauri/src/commands/license_ed25519_v1.rs` (NEW 210 lines) — dalek verify kid:v1 + Tauri command + 8 unit tests
- `src-tauri/src/commands/mod.rs` (+2 lines) — pub mod + re-export
- `src-tauri/src/lib.rs` (+2 lines) — invoke_handler registration
- `fluxion-proxy/wrangler.toml` (+8 lines) — `[[d1_databases]]` top-level prod binding
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — S293 scope
- Fuori repo CF cloud: D1 `fluxion-webhook-events` created + migration applied + secrets `ED25519_PRIVATE_KEY_PKCS8` + `ED25519_PUBLIC_KEY_V1` prod

### Carry-over backlog (defer post-S293)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card (TEST chain)
- **FDQ-02 SCA EU 3DS** (`4000002500003155` browser founder)
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary client)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** live verify GUI iMac + **BUG-FATT-5** toast z-index
- **Track E** migration 017 license_revoked status enum
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** founder S286 (brand-guardian + visual-storyteller)
- **landing CF Pages re-deploy** post-FBUG-LM-01 S287
- **Migrazione legacy NODE-ED25519 → Ed25519 standard** S291 carry-over

Atteso post-Stop S292: 1 commit atomic con tutti i files sopra. Ripartenza S293 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267 no sintesi inline).
