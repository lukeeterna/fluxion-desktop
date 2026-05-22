# Prompt ripartenza S283 — Track B Gate 1 (chiusura setup CF + deploy worker env test)

## Stato chiusura S282 (VERDE parziale, 2/4 chiavi TEST persistite, CF blocked outage dashboard)

**S282 outcome**: setup credenziali TEST Track B avviato. REGOLA #16 (research-first) applicata correttamente DOPO correzione founder: prima di guidare creazione nuovo token CF avrei dovuto cercare `~/.claude/projects/.../memory/` per pattern recovery noti (`reference_cloudflare_token.md` esistente). Lesson appresa.

### Done S282

1. ✅ Resend TEST API key creata dashboard (name `fluxion-test-S282`, Full access, formato `re_..._...` 36 char). Salvata su iMac `.env` come `RESEND_API_KEY_TEST`.
2. ✅ Stripe TEST Secret Key (sandbox, NON restricted): formato `sk_test_51...` 107 char. Verify live `https://api.stripe.com/v1/balance` → `stripe_auth_ok=True, livemode=False`. Salvata su iMac `.env` come `STRIPE_SECRET_KEY_TEST`.
3. ✅ `fluxion-proxy/wrangler.toml` esteso con blocco `[env.test]` completo:
   - Worker name: `fluxion-proxy-test` (URL `https://fluxion-proxy-test.<subdomain>.workers.dev` post-deploy)
   - KV namespace test: placeholder `PLACEHOLDER_REPLACE_AFTER_WRANGLER_KV_CREATE` (da sostituire dopo `wrangler kv namespace create LICENSE_CACHE --env test`)
   - vars: `ENVIRONMENT="test"` + tutti gli scalari prod replicati
   - NO triggers cron in test env (F-3 email seq + F-4 health monitor sono prod-only)
4. ✅ Memory `reference_track_b_test_keys.md` creata + indicizzata in `MEMORY.md` riga 19 — mappa storage credenziali iMac `.env` + recovery commands (verify presenza + verify live API senza loggare valori) + deploy chain wrangler completo.
5. ✅ Memory `reference_cloudflare_token.md` aggiornata: token CF `cfat_CsHP...` (S189-B 2026-05-08) marcato **DEAD** dopo verify live `/user/tokens/verify` → `Invalid API Token`. Action item S282 documentato.

### Blocker S282 carry-over critici

1. ❌ **CF dashboard outage** `https://www.cloudflarestatus.com/` → "Minor Service Outage" attiva tutta sessione (errore 503 `/api/v4/accounts/.../flags` + dropdown account "caricamento in corso"). NON ho potuto guidare creazione nuovo `CLOUDFLARE_API_TOKEN`. **Verificare status outage all'avvio S283.**
2. ❌ Token `fluxion-tunnel` esistente (Workers Scripts + KV + Pages + Cloudflare Tunnel Write) → **NON ROLLARE** (è il runtime del tunnel `cloudflared` attivo PID 6785 su iMac che espone `http://localhost:3010` → endpoint fluxion-license production). Rolling = outage tunnel = phone-home offline clienti reali.
3. ❌ `STRIPE_WEBHOOK_SECRET_TEST` creabile SOLO post-deploy worker test (serve URL endpoint reale per dashboard.stripe.com/test/webhooks → Add endpoint).

### Diagnostica iMac corrente

- `~/.cloudflared/`: `config.yml` + `fluxion-license.json` cert
- LaunchAgent: `com.fluxion.cloudflared` active
- Process: `/usr/local/bin/cloudflared tunnel --url http://localhost:3010` PID 6785

---

## TASK S283 (CTO autonomous REGOLA #14 + #15, research-first REGOLA #16)

### Step 1 — Verifica CF outage risolto

```bash
curl -s "https://www.cloudflarestatus.com/api/v2/status.json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('CF status:', d['status']['indicator'], '-', d['status']['description'])"
```

Se `status='none'` → procedi Step 2. Se ancora `minor`/`major` → wait + pivot Track F autonomous (force phone-home design spike, zero CF dependency).

### Step 2 — Guida founder creazione token CF nuovo

Founder ha già aperto `https://dash.cloudflare.com/profile/api-tokens` durante S282 ma dropdown "caricamento in corso" mai sbloccato per outage. **NON modificare `fluxion-tunnel` esistente** (vincolo critico).

- Nome nuovo token: `FLUXION-Track-B-S283`
- Account: `Gianlucanewtech@gmail.com's Account`
- Scope minimo Track B:
  - **Workers Scripts** → Edit
  - **Workers KV Storage** → Edit
- IP filter: vuoto (residential IP cambia)
- TTL: 1 anno default OK
- Account resources: include account specifico (era questo che non si sbloccava per outage)
- Founder pasta valore in TextEdit aperto da CC su `/tmp/cf_token.txt` → salva → "fatto"

### Step 3 — Persist + verify CF token

```bash
# Validate format (NO valore in log)
LEN=$(wc -c < /tmp/cf_token.txt | tr -d ' '); PREFIX=$(head -c 6 /tmp/cf_token.txt); echo "len=$LEN prefix=$PREFIX"
# Expected: len in [37-50], prefix=cfat_

# Verify live
TOKEN=$(cat /tmp/cf_token.txt | tr -d '\n\r ')
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print('cf_token_valid=' + str(d.get('success')))"

# Persist iMac .env
VAL=$(cat /tmp/cf_token.txt | tr -d '\n\r ')
ssh imac "grep -v '^CLOUDFLARE_API_TOKEN=' '/Volumes/MacSSD - Dati/fluxion/.env' > /tmp/.env.new && echo 'CLOUDFLARE_API_TOKEN=$VAL' >> /tmp/.env.new && mv /tmp/.env.new '/Volumes/MacSSD - Dati/fluxion/.env'"
unset VAL TOKEN
shred -u /tmp/cf_token.txt 2>/dev/null || rm -f /tmp/cf_token.txt

# Confirm presence
ssh imac "grep -q '^CLOUDFLARE_API_TOKEN=' '/Volumes/MacSSD - Dati/fluxion/.env' && echo PRESENT || echo MISSING"
```

### Step 4 — Deploy Worker env test (autonomous via SSH iMac o MacBook direct)

```bash
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
CF_TOKEN=$(ssh imac "grep '^CLOUDFLARE_API_TOKEN=' '/Volumes/MacSSD - Dati/fluxion/.env' | cut -d= -f2-")
export CLOUDFLARE_API_TOKEN=$CF_TOKEN CLOUDFLARE_ACCOUNT_ID=22ddff3a4ef544511523a841b3dcadf8

# 4.1 Crea KV namespace test
npx wrangler kv namespace create LICENSE_CACHE --env test
# → copy `id` returned, replace `PLACEHOLDER_REPLACE_AFTER_WRANGLER_KV_CREATE` in wrangler.toml

# 4.2 Deploy worker test
npx wrangler deploy --env test
# → output URL endpoint: salva per Step 5

# 4.3 Set secrets test (stdin pipe, NO echo)
for VAR in STRIPE_SECRET_KEY RESEND_API_KEY; do
  VAL=$(ssh imac "grep '^${VAR}_TEST=' '/Volumes/MacSSD - Dati/fluxion/.env' | cut -d= -f2-")
  echo "$VAL" | npx wrangler secret put $VAR --env test
done

# 4.4 ED25519 public key (riusa prod, verifica firma client invariata)
echo "c61b3c912cf953e06db979e54b72602da9e3e3cea9554e67a2baa246e7e67d39" | npx wrangler secret put ED25519_PUBLIC_KEY --env test

unset VAL CF_TOKEN
```

### Step 5 — Crea Stripe TEST webhook endpoint + persist secret

Dashboard `https://dashboard.stripe.com/test/webhooks` → "Add endpoint":
- URL: `https://fluxion-proxy-test.<subdomain>.workers.dev/api/stripe/webhook` (da Step 4.2 output)
- Events: `checkout.session.completed`, `charge.refunded`
- Copy "Signing secret" `whsec_...` (~38 char)
- Pasta in TextEdit `/tmp/stripe_webhook_secret.txt`
- Validate + persist iMac `.env` come `STRIPE_WEBHOOK_SECRET_TEST` + `wrangler secret put STRIPE_WEBHOOK_SECRET --env test`

### Step 6 — E2E smoke test chain card 4242

```bash
# 6.1 Create test checkout session (Stripe API → fluxion-proxy-test worker)
STRIPE_KEY=$(ssh imac "grep '^STRIPE_SECRET_KEY_TEST=' '/Volumes/MacSSD - Dati/fluxion/.env' | cut -d= -f2-")
curl -s https://api.stripe.com/v1/checkout/sessions -u "${STRIPE_KEY}:" \
  -d "mode=payment" \
  -d "line_items[0][price_data][currency]=eur" \
  -d "line_items[0][price_data][product_data][name]=FLUXION Base TEST" \
  -d "line_items[0][price_data][unit_amount]=49700" \
  -d "line_items[0][quantity]=1" \
  -d "success_url=https://fluxion-proxy-test.workers.dev/success" \
  -d "cancel_url=https://fluxion-proxy-test.workers.dev/cancel" \
  -d "customer_email=test+s283@fluxion.it" \
  -d "metadata[tier]=base" | python3 -m json.tool | head -20

# 6.2 Browser test: aprire checkout URL, pagare con 4242 4242 4242 4242 / 12/34 / 123
# 6.3 Verifica chain:
#     a) Stripe webhook firing → check wrangler tail --env test
#     b) KV LICENSE_CACHE test purchase:{email} scritto
#     c) Resend email sandbox arrivata → magic link
#     d) activate-by-email 200 con success
unset STRIPE_KEY
```

---

## Vincoli S283

- **REGOLA #14**: CTO autonomous via SSH+cargo+npm+wrangler. Founder solo creazione token CF dashboard (~30s).
- **REGOLA #15**: NO A/B questions. CTO decide pivot Track F se CF outage persiste.
- **REGOLA #16**: PRIMA di guidare creazione credenziali, CERCA in `~/.claude/projects/.../memory/` per pattern recovery noti.
- **REGOLA #6**: NO `Co-Authored-By` trailer in commit.
- **Context budget**: parti sotto 30% raw. File critici (wrangler.toml deploy) → BLOCK_CRITICAL ≥50% raw.
- **MAI rollare/modificare token CF `fluxion-tunnel`** (runtime tunnel cloudflared production iMac PID 6785).

## File modificati S282 da committare

- `fluxion-proxy/wrangler.toml` (+22 righe `[env.test]` block)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file)
- (memory files in `~/.claude/projects/.../memory/` non sono git-tracked)

## PROMPT START S283

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S282 close + 6 step Track B.

REGOLA #16 attiva: prima di guidare credenziali, cerca memory recovery patterns.
REGOLA #15 attiva: decidi autonomamente pivot Track F se CF outage persiste.

Step 1: verify CF outage status. Se none → Step 2 guida founder token nuovo (FLUXION-Track-B-S283).
Se ancora outage → Track F spike research force phone-home post-refund (autonomous, zero CF).

NON ROLLARE token "fluxion-tunnel" (production runtime, vincolo critico S282).
```

---

**Provenienza S282 close**: VERDE parziale. 2/4 chiavi TEST persistite (Stripe + Resend). 2 blocker carry-over (CF outage + Stripe webhook deploy-dependent). Memory mappa storage creata. wrangler.toml [env.test] ready. Setup infra Track B al ~50%. Resto deploy chain unblock entro 30 min lavoro S283 una volta CF dashboard online.
