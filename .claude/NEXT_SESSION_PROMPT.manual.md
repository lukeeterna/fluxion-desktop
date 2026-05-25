# Prompt ripartenza S291 — Worker License Refactor FASE 2 RESUME (post-blocker CF token D1)

> ## META-VINCOLO S291 (carry-over founder-input S289) — VALIDATE-THEN-IMPLEMENT OBBLIGATORIO
>
> **FASE 1 S290 GIÀ COMPLETATA + GO Luke ricevuto 2026-05-25.** Decisioni chiuse:
> - **Storage dedup**: D1 con UNIQUE su `event_id` + pattern `INSERT OR IGNORE` + `meta.changes===0`
> - **Firma**: WebCrypto Ed25519 nativa (Worker sign) + ed25519-dalek v2.2.0 (Tauri verify)
> - **Stripe verify**: `constructEventAsync` + `Stripe.createSubtleCryptoProvider()` (stripe@^22)
> - **Determinismo**: `license_id = sha256(session_id || product || customer_email)`
> - **Replay logic**: NON 200 cieco — leggi riga, se `email_sent_at IS NULL` ri-invia email leggendo `license_payload` già salvato + UPDATE `email_sent_at`
> - **kid in V1**: payload firmato include `kid:"v1"` già ora, client Tauri map `{v1: pubkey}` (no retrofit dopo)
> - **NO `@noble/ed25519`** preventivo (YAGNI) — fallback solo se test #3 fallisce
>
> **MAI dichiarare anello CHIUSO o ring VERIFIED senza i 3 test reali letti da Luke** (gate visivo):
> - FDQ-01: card 4242 → checkout → licenza firmata → email arriva (log reale)
> - FSAF-05: replay webhook 2x via `stripe events resend` → 1 licenza + 1 email + count D1 invariato + log `meta.changes===0` su 2° INSERT
> - Verify firma: payload valido → true; payload alterato 1 byte → false (sign Worker → verify dalek interop test)

---

## Stato chiusura S290 (CLOSING_ONLY @ 71% context — FASE 2 parzialmente eseguita, blocker infra)

### Done S290

1. **FASE 1 VALIDATE** — 6 domande verificate con fonti primarie ([CF Workers WebCrypto](https://developers.cloudflare.com/workers/runtime-apis/web-crypto/), [docs.stripe.com/webhooks](https://docs.stripe.com/webhooks), [D1 read replication blog](https://blog.cloudflare.com/d1-read-replication-beta/), [crates.io ed25519-dalek](https://crates.io/crates/ed25519-dalek), [CF blog Stripe native](https://blog.cloudflare.com/announcing-stripe-support-in-workers/)). Tabella + raccomandazione singola + rischi consegnati. GO Luke ricevuto con 2 precisazioni embedded sopra (replay email re-send + kid v1).

2. **FASE 2.1 Read baseline** — `fluxion-proxy/src/routes/stripe-webhook.ts` (HMAC custom + KV FSAF-09 dedup S286 funzionante, mantenere backward compat con KV `purchase:{email}` usato da `activate-by-email.ts`) + `fluxion-proxy/src/lib/ed25519.ts` (`NODE-ED25519` legacy verify-only, affiancare con nuovo `Ed25519` standard sign+verify). Stack: Node v22.14.0, wrangler v3.22.0 (Big Sur compat, v4 blocked), `nodejs_compat` flag attivo (stripe-node v22 OK).

3. **FASE 2.2 Ed25519 keypair generata + round-trip Node WebCrypto PASS**:
   - **PUBKEY raw 32-byte hex completo (kid v1, pubblico)**: file `~/.claude/.env.s290-ed25519-pub-raw.hex` (mode 644)
   - **PRIVKEY PKCS8 base64**: file `~/.claude/.env.s290-ed25519-priv-pkcs8.b64` (mode 600, persistito post-/tmp cleanup)
   - Prefix pubkey per sanity check ripartenza: `0616ecd7` (8 char). Lunghezza file 64 char hex.
   - Test interop: Node 22 `webcrypto.subtle.importKey('pkcs8', ...)` + `sign('Ed25519', ...)` -> sig 64-byte -> `importKey('raw', ...)` + `verify('Ed25519', ...)` -> `true` valid / `false` tampered 1-byte. **Stesso runtime di Workers** -> interop pre-validata.

### BLOCKER infra S291 — Founder-action obbligata

`wrangler d1 create fluxion-webhook-events-test` ha fallito con `authentication error 10000`. Anche chiamata REST diretta a `POST /accounts/<ACCOUNT_ID>/d1/database` restituisce stesso errore. Token CF attuale (env vars CLOUDFLARE_API_TOKEN e CF_API_TOKEN, stesso valore, ID prefix `1814e6dc...`) ha permessi solo Workers Scripts + KV, **manca permission D1:Edit**.

Account ID prefix `22ddff3a...` (full visibile in dashboard CF).

**Azione Luke (1 sola, motivata)**:
1. Vai su https://dash.cloudflare.com/profile/api-tokens
2. Modifica token esistente OPPURE crea nuovo Custom Token con questi permessi:
   - Account → Account Settings → Read
   - Account → Workers Scripts → Edit
   - Account → Workers KV Storage → Edit (preserva esistente)
   - Account → D1 → Edit (NUOVO — questo è il mancante)
   - User → User Details → Read
   - User → Memberships → Read
3. Account Resources: Include → Specific account → Gianlucanewtech@gmail.com's Account
4. Salva il nuovo valore in `~/.claude/.env` come variabili CLOUDFLARE_API_TOKEN e CF_API_TOKEN (alias), poi `source ~/.claude/.env` o apri nuova shell.
5. Verifica permission a inizio S291 con pre-flight in fondo a questo prompt.

### Pending S291 (post-token unblock)

| Task | Owner | Note |
|------|-------|------|
| 2.3 D1 create + migration `0001_webhook_events.sql` + binding `[[env.test.d1_databases]]` wrangler.toml | CTO | Schema: `event_id PK UNIQUE, session_id, license_id, license_payload TEXT, license_signature TEXT, email_sent_at INTEGER NULL, created_at INTEGER DEFAULT unixepoch()` |
| 2.4 Refactor `stripe-webhook.ts` | CTO | `npm install stripe@^22 --save` in fluxion-proxy/, `constructEventAsync` + `createSubtleCryptoProvider`, D1 `INSERT OR IGNORE`, replay logic re-send se `email_sent_at IS NULL` (leggi `license_payload` esistente), kid:v1 deterministico, sign Ed25519 importKey PKCS8 da secret. **Mantieni KV `purchase:{email}` separato** (backward compat `activate-by-email.ts` flow, NON toccare). |
| 2.5 `lib/ed25519-sign.ts` + endpoint `POST /api/v1/verify` (debug) | CTO | sign/verify nativo Ed25519 standard (NON NODE-ED25519 legacy); `/verify` test interop dalek (input: payload+sig+kid -> bool). Lasciare `ed25519.ts` esistente (legacy NODE-ED25519 verify) finché client Tauri vecchio in circolo. |
| 2.6 Vitest test idempotency | CTO | 3+ test: replay 2x -> 1 INSERT 1 email; replay con `email_sent_at IS NULL` -> re-send email; verify roundtrip valid/tampered. |
| 2.7 Deploy `--env test` | CTO | `wrangler secret put ED25519_PRIVATE_KEY_PKCS8 --env test` (stdin da `cat ~/.claude/.env.s290-ed25519-priv-pkcs8.b64`); `wrangler secret put ED25519_PUBLIC_KEY_V1 --env test` (stdin da `cat ~/.claude/.env.s290-ed25519-pub-raw.hex`); `wrangler d1 migrations apply fluxion-webhook-events-test --env test --remote`; `wrangler deploy --env test`. |
| 2.8 Test reali 3 gate visivi | CTO | **FDQ-01**: `stripe trigger checkout.session.completed --add coupon=<100%>` su endpoint test; cattura log webhook + `wrangler d1 execute fluxion-webhook-events-test --env test --remote --command "SELECT count(*) FROM webhook_events"` + Resend log. **FSAF-05**: `stripe events resend evt_xxx --webhook-endpoint we_xxx` 2x; cattura log `meta.changes===0` su 2° INSERT + count D1 invariato + Resend 1 send. **Verify**: `curl POST /api/v1/verify` con payload valido (true) + payload alterato 1 byte (false). **Output 3 log incollati in chat per GO production_ready Luke.** |

### Vincoli S291 (non-negoziabili, riconfermati)

- **MAI dichiarare anello CHIUSO o promote VERIFIED senza i 3 test reali letti da Luke** (META-VINCOLO + REGOLA #18).
- **MAI stampare valori chiavi/secret** — SOLO SET/UNSET booleano. Pubkey OK (pubblica), privkey MAI in stdout/file repo.
- **NO mock** su test E2E. Endpoint reali (Stripe TEST CLI + KV worker test + D1 worker test + Resend test inbox).
- **REGOLA #14/#15**: CTO autonomous tutto eccetto fisical iMac + browser founder + token CF refresh.
- **REGOLA #16**: research-first PRIMA di qualsiasi proposta tecnica (no README hype, no training-data guess).
- **CLOSING_ONLY soglia 70-80%**: a S291 monitorare context, chiusura preventiva a 65% se sospetto lungo deploy/test.

### Pre-flight S291 (15s)

```bash
# 1. Env vars set (lettura via os.environ.get pattern bash)
zsh -c 'for V in CLOUDFLARE_API_TOKEN CF_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'

# 2. Keypair S290 persistito
ls -la ~/.claude/.env.s290-ed25519-* 2>&1

# 3. Token D1 permission check (creazione + cleanup immediato)
ACC=$(curl -sS "https://api.cloudflare.com/client/v4/accounts" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq -r '.result[0].id')
echo "Account: $ACC"
RES=$(curl -sS -X POST "https://api.cloudflare.com/client/v4/accounts/$ACC/d1/database" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"_perm_check_S291_delete_me"}')
echo "$RES" | jq '{success, error: .errors[0].message}'
UUID=$(echo "$RES" | jq -r '.result.uuid // empty')
if [ -n "$UUID" ]; then
  curl -sS -X DELETE "https://api.cloudflare.com/client/v4/accounts/$ACC/d1/database/$UUID" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '{success}'
  echo "Token D1 permission OK -> procedi Task 2.3"
fi
```

Atteso: 5/5 SET, 2 file keypair persistiti, D1 create `success:true`, cleanup `success:true`.

### Carry-over backlog (defer post-S291)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card
- **FDQ-02 SCA EU 3DS** (`4000002500003155` browser founder)
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** live verify GUI iMac + **BUG-FATT-5** toast z-index
- **Track E** migration 017 license_revoked status enum
- **Track F** force phone-home post Stripe webhook
- **Resend custom domain** strategica
- **LOGO email template** founder S286
- **wrangler v4 upgrade** (BLOCKED Big Sur)
- **KV cleanup S285-S289 test entries**
- **landing CF Pages re-deploy** post-FBUG-LM-01
- **Migrazione legacy NODE-ED25519 -> Ed25519 standard** in `ed25519.ts` (deprecation rolling con client Tauri vecchi)

### Files modificati S290 da committare (atomic)

- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — S291 scope + blocker token + carry-over Task 2.3-2.8

**Nessun file critico FLUXION modificato S290** (rispettato CLOSING_ONLY @ 71%). Keypair Ed25519 fuori repo (`~/.claude/.env.s290-ed25519-*`, NON committare, NON in repo FLUXION).

Atteso post-Stop S290: 1 commit atomic `.claude/NEXT_SESSION_PROMPT.manual.md`. Ripartenza S291 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267 no sintesi inline).
