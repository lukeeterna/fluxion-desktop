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

## PRIMO COMANDO S332 (se Luke decide go-live brandizzato)
Custom domain: aggiungere record/route per `fluxion-app.com` → worker prod. Altrimenti: pivot su Sara live-test (REGOLA #21) come prossimo pilastro vendita.
