# FLUXION — NEXT SESSION PROMPT — S370 · PRE-PRODUCTION, ZERO PARCHEGGI
> Direttiva founder S369: andiamo in produzione, NESSUN compromesso, VIETATO "parcheggiare" fix/feature fondamentali. Le mail devono essere brandizzate (LOGO), curate, copy curata.
> Ruoli: Claude = CTO/firewall · CC = esecutore Mac/Win SSH · Luke = founder (giro fisico + decisioni).
> Regole: WIP=1, anti-falso-verde, dati-first, €0. Done-condition esterna per ogni task (no validazione statica). Verifica commit prima di dire "da fare" (REGOLA #30).

## ⚠️ CLEANUP IN SOSPESO DA S369 — PRIMO ATTO (reversibile)
Acquisto €1 LIVE reale eseguito in S369. Se non già fatto:
1. **Rimborsa €1** charge `ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` SOLO dopo che il founder ha attivato la licenza via recovery (sequencing). `curl -s -X POST https://api.stripe.com/v1/refunds -u "$STRIPE_LIVE_SECRET_KEY:" -d charge=ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` (chiave: `~/.claude/.env.fluxion-live`).
2. **Ripristina landing**: `git checkout landing/checkout-consent.html` (rimuove piano test €1, NON committato) → `cd landing && npx wrangler pages deploy . --project-name=fluxion-landing --branch=main --commit-dirty=true`. Verifica: `curl -sL "https://fluxion-landing.pages.dev/checkout-consent?plan=test"` NON deve più contenere `24007`.
3. **Disattiva link €1**: `curl -s -X POST https://api.stripe.com/v1/payment_links/plink_1TeCftIW4bHDTsaHJfwJNndD -u "$STRIPE_LIVE_SECRET_KEY:" -d active=false`.

## STATO S369 (verificato alla fonte)
🟢 **Anelli E2E 1-3 VERDI**: charge `ch_3Tiz7a` €1 `cs_live` succeeded → D1 prod `webhook_events` `evt_1Tiz7c` `product=base` licenza+firma → **mail RICEVUTA** da `licenze@fluxion-app.com` (🔴 deliverability storica CHIUSA). Worker `fluxion-proxy` deployato v`598dd141`.
🟡 **Anelli 4-8** (giro fisico founder): pagina post-pay copy nuovo / attivazione recovery / wizard #2-#3 / clienti B1 / CRUD — chiedere esito al founder a inizio S370 e CHIUDERE eventuali bloccanti (no parcheggio).

## TASK S370 — TUTTI DA CHIUDERE PRIMA DELLA VENDITA (no parcheggi)

### T1 — WINDOWS PARITY (fondamentale, blocca produzione)
PROBLEMA REALE (verificato): la mail/pagina dicono "Versione Windows in arrivo" ma l'app Windows gira. La copy non è fixabile a vuoto: **non esiste installer Windows pubblicato** (release `v1.0.1` su `lukeeterna/fluxion-desktop` ha 0 asset; macOS punta a v1.0.0).
Sotto-task:
  a. **Pubblicare l'installer Windows** (NSIS `.exe` o `.msi`) come asset di una GitHub Release di `lukeeterna/fluxion-desktop`. Fonte build = pipeline CI "Cross-OS Build Pipeline" (release v1.0.1) o build su box Windows. DECISIONE founder: vedi chiarimento (1).
  b. Aggiungere env `DOWNLOAD_URL_WINDOWS` in `fluxion-proxy/wrangler.*` + tipo in `src/lib/types.ts:26`.
  c. Sostituire la copy "Windows in arrivo" con bottone reale "Scarica per Windows" in: `src/routes/stripe-webhook.ts:109` (MAIL) + `src/routes/checkout-success.ts:156` (PAGINA).
  d. Allineare anche macOS a v1.0.1 (oggi `DMG_DOWNLOAD_URL_MACOS` punta a v1.0.0). Confermare asset v1.0.1 macOS.
  e. Redeploy worker.
DONE: da una macchina Windows, click "Scarica per Windows" dalla mail/pagina → scarica installer reale e si installa. (test esterno, non statico)

### T2 — MAIL BRANDIZZATA E CURATA (requisito produzione, founder-input)
La mail licenza oggi è HTML inline spartano (`stripe-webhook.ts` ~righe 90-170) + `src/email/templates.ts`. Rifare con standard enterprise:
  a. **Logo FLUXION** in testa (asset `landing/logo_fluxion.jpg`; ospitarlo su `https://fluxion-landing.pages.dev/logo_fluxion.jpg` o asset dedicato, riferito via URL assoluto — le mail non supportano inline locale).
  b. Layout responsive, palette brand, copy CURATA (no "scrivi a gmail per Windows"), CTA chiare per i 3 passi (scarica / attiva / supporto).
  c. Coerenza con `email/templates.ts` (lead-magnet) per tono e header/footer.
  d. Delega consigliata: `brand-guardian` (tono/copy) + `frontend-developer`/`content-creator` per HTML email.
DONE: invio reale a casella secondaria → logo visibile + copy curata + render corretto in Gmail (screenshot/verifica founder).

### T3 — chiudere anelli 4-8 S369 + qualunque bloccante emerso (no parcheggio).

### INVARIATI (hard-gate pre-vendita, NON declassare)
- Sara chiamata-reale su TUTTI i verticali (verdetto giudice S365). Restart pipeline: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara_pipeline.log 2>&1 &"`.
- R1 Sales Agent SOSPESO fino a onboarding VERDE.
- Magazzino+alert scorte: GATE PASS S361, confermare vendibile.

## CHIARIMENTI DA FOUNDER (apertura S370)
1. **Windows installer**: esiste già un artifact buildato (CI v1.0.1) da caricare sulla Release, oppure CC deve lanciare la build (serve box Windows/CI attivo)? Formato preferito: NSIS `.exe` (più semplice) o `.msi`?
2. Anelli 4-8: esito del tuo giro (wizard/clienti/CRUD): PASS o bloccanti?
3. Cleanup: licenza già attivata dalla mail? (per rimborsare il €1).
