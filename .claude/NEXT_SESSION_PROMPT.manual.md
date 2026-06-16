# FLUXION — NEXT SESSION PROMPT — S370 · chiudere pipeline E2E + fix copy Windows + CLEANUP test €1
> Ruoli: Claude = CTO/firewall · CC = esecutore Mac/Win SSH · Luke = founder (giro fisico).
> Vincoli: WIP=1, anti-falso-verde, dati-first, €0. Verifica commit prima di dire "da fare" (REGOLA #30).

## ⚠️ CLEANUP IN SOSPESO DA S369 — FARE PER PRIMO (atti reali, reversibili)
La sessione S369 ha eseguito un acquisto €1 LIVE reale. Se non già fatto a fine S369:
1. **Rimborsa il €1**: charge `ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` (pi `pi_3Tiz7aIW4bHDTsaH0cldt45C`), €1 su `ilcombeeretrasher@gmail.com`. SOLO DOPO che il founder ha attivato la licenza via recovery (sequencing attiva-poi-rimborsa; `license-recovery.ts:128-131` è 410 se refunded). Comando: `curl -s -X POST https://api.stripe.com/v1/refunds -u "$STRIPE_LIVE_SECRET_KEY:" -d charge=ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` (chiave in `~/.claude/.env.fluxion-live`).
2. **Ripristina landing**: `landing/checkout-consent.html` ha un piano `test`=€1 aggiunto a mano (NON committato). `git checkout landing/checkout-consent.html` poi `cd landing && npx wrangler pages deploy . --project-name=fluxion-landing --branch=main --commit-dirty=true` per riportare prod a soli Base/Pro. Verifica: `curl -sL "https://fluxion-landing.pages.dev/checkout-consent?plan=test"` NON deve più contenere `24007`.
3. **Disattiva link €1**: `curl -s -X POST https://api.stripe.com/v1/payment_links/plink_1TeCftIW4bHDTsaHJfwJNndD -u "$STRIPE_LIVE_SECRET_KEY:" -d active=false`.

## STATO S369 — pipeline cliente E2E (acquisto reale €1 dal funnel landing)
🟢🟢🟢 **ANELLI 1-2-3 VERDI (verificati alla fonte):**
- Anello 1 charge: `ch_3Tiz7a` €1 **succeeded**, `cs_live_a1iJuRsjll…`, email `ilcombeeretrasher@gmail.com`.
- Anello 2 D1 prod `fluxion-webhook-events`.`webhook_events`: riga `evt_1Tiz7c`, `product=base`, `license_id 9972c3c6…`, payload+firma presenti.
- Anello 3 deliverability **CHIUSA**: `email_sent_at` popolato + **founder ha ricevuto la mail** da `licenze@fluxion-app.com`. (Chiude il 🔴 deliverability storico.)
- Infra pronta: worker `fluxion-proxy` deployato (version `598dd141`, copy Passo 2 recovery-link). Landing prod serve €1 a `/checkout-consent?plan=test`.

🟡 **ANELLI 4-8 IN CORSO al momento del handoff** (giro fisico founder): attivazione via recovery-link, wizard (P.IVA errata→toast #2; dropdown step6 #3), clienti B1 (telefono vuoto→toast), CRUD. Dati pronti in `.claude/TEST_DATA_S369.md` (aperto in TextEdit). Riprendere chiedendo al founder l'esito di questi anelli; se PASS e cleanup fatto → S369 gate CHIUSO.

## 🔴 BUG NUOVO (founder-reported S369) — copy "Windows in arrivo" obsoleta
L'app Windows gira da 2026-06-10 (MEMORY project_windows_app_runs_verified). La copy dice ancora "Versione Windows in arrivo". 2 punti:
- `fluxion-proxy/src/routes/stripe-webhook.ts:109` (MAIL licenza)
- `fluxion-proxy/src/routes/checkout-success.ts:156` (PAGINA post-pagamento)
**BLOCCO/DECISIONE**: non esiste `WINDOWS_DOWNLOAD_URL` (solo `DMG_DOWNLOAD_URL_MACOS` in env `lib/types.ts:26`). Prima del fix serve PUBBLICARE l'installer Windows (.msi/.exe, GitHub Release) e aggiungere la var env + bottone "Scarica per Windows". Poi redeploy worker. Fix = ~2 stringhe + 1 var + 1 bottone, ma gated sulla URL reale.

## APERTI MINORI (invariati)
- Sara tutti-i-verticali chiamata-reale = hard-gate pre-vendita (verdetto giudice S365). Restart pipeline: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara_pipeline.log 2>&1 &"`.
- R1 Sales Agent SOSPESO fino a onboarding VERDE.
- Magazzino+alert scorte: GATE PASS S361, confermare vendibile.
