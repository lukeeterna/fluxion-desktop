# FLUXION — S332 resume — R-01 PROD-VERIFIED LIVE. Payment+anti-refund rail venduto-pronto.

> Scritto 2026-06-03 a chiusura S331. LIVE smoke €1 su PROD = VERDE end-to-end.
> Evidenza: `~/venture-os/state/s331-live-smoke-prod-evidence.json`.

## CHIUSO IN S331 (NON ri-fare)
- **LIVE smoke €1 su worker PROD `fluxion-proxy.gianlucanewtech.workers.dev` = VERDE** (Stripe LIVE, soldi veri, costo netto €0):
  acquisto €1 (`pi_3TeF78`) → licenza emessa (KV `email_sent:true`) → `/validate` valid → refund €1 (`re_3TeF78` succeeded) → webhook `charge.refunded` → KV `refunded:true` → `/validate` **revoked** con `refunded_at` reale.
- **FIX DEPLOY PROD**: scoperto che il worker prod era STALE (R-01-ter mai deployato in prod, solo `--env test` in S330). `/validate` rispondeva 401. Risolto con `wrangler deploy` → prod v`570abae7`. Ora R-01-ter è LIVE in produzione.
- Cleanup: payment link smoke `plink_1TeCft` disattivato. Price €1 `price_1TcsBs` mantenuto (riusabile).

## LEZIONE S331 (importante per il futuro)
- "Merged su master" ≠ "deployato in prod". Per i CF Worker, dopo ogni merge che tocca il proxy serve `wrangler deploy` (prod, NO `--env test`). REGOLA #18 (validate-then-implement) ha intercettato il falso "production ready".
- Wrangler 3.114 su macOS 11: `kv key get <key> --namespace-id <id>` (NO `--remote`, è default; NO `kv:key` colon-form non serve). `--remote` = "Unknown argument".

## BLOCKED-ON / RESTA (non blocca il payment rail, già venduto-pronto)
- **Custom domain `fluxion-app.com`**: NS su CF ma nessun record A → attaccare al worker prod (`wrangler` route o Pages custom domain) per go-live brandizzato. Il rail funziona già su `*.workers.dev`.
- **Rami client-side tsc-only** (NON E2E): offline grace -8gg→LOCK, clock-rollback guard, banner `saraEnabled=false`. Richiedono app-run GUI iMac (Keychain, REGOLA #12). Non bloccano il gate server-side.
- **Sara pilastro** (REGOLA #21): "pronto a vendere" richiede Sara testata LIVE su tutti i verticali (chiamata reale). Payment rail OK = necessario NON sufficiente.

## S332 = SARA LIVE-TEST (CONFERMATO da Luke 2026-06-03)
Priorità decisa: il payment rail è verificato LIVE (S331). Il vero gate vendita è Sara (REGOLA #21: payment OK = necessario NON sufficiente). Custom domain `fluxion-app.com` DEMOTO a task atomico separato per il giorno del go-live pubblico (reversibile, 10 min, indipendente).

### PRIMO COMANDO S332
1. PRE-FLIGHT SIP: `curl http://192.168.1.2:3002/health` → verificare `registered:true, reg_status:200, engine:pjsua2, username 0972536918@sip.vivavox.it` (era OK in S323). Se 3002 down → restart via voice-engineer.
2. SCOPE METODOLOGIA 2-LAYER (definita S323, evita avvitamento):
   - Layer 1 (testo, ampio): estendere `test_all_verticals_e2e.py` a tutti i verticali + scenari waitlist/disambiguazione/chiusura/triage. Baseline S323 = 21 OK/8 WARN/0 FAIL.
   - Layer 2 (audio, mirato): harness pjsua2 `sara_audio_harness.py` — golden-path per verticale + scenari STT-sensitivi. NON tutti gli scenari via audio.
   - CTO guida il test via TTS in autonomia (REGOLA #23), MAI chiedere a Luke di chiamare dal telefono.
3. Criterio gate (REGOLA #21): Sara "soddisfa pienamente il cliente" su TUTTI i verticali → solo allora "pronto a vendere" + attivare Sales Agent WA.
