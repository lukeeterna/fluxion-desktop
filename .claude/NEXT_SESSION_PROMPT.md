# Prompt ripartenza — Mail licenza FLUXION enterprise

**Generato**: `2026-06-16`
**Task completato questa sessione**: riscrittura mail transazionale licenza (stripe-webhook.ts)

## Cosa è stato fatto

- `fluxion-proxy/src/routes/stripe-webhook.ts` — funzione `buildEmailHtml()` completamente riscritta.
  Nuovo design: sfondo chiaro (#f4f6f8), palette "documento d'acquisto", layout table-based responsive,
  logo PNG reale in header scuro, 3 passi numerati con CTA verde su Passo 3 (attivazione licenza).
- Logo URL verificato: `https://fluxion-landing.pages.dev/assets/logo.png` → HTTP 200 image/png.
  L'altro candidato (`/logo.png`) restituisce HTML, non usare.
- Anteprima statica creata: `.claude/cache/mail-licenza-preview.html` (aperta nel browser).

## Cosa NON è stato fatto (fuori scope esplicito)

- Deploy worker (`wrangler deploy`) — non richiesto in questa sessione.
- `npm run type-check` sul proxy — da fare in prossima sessione prima del deploy.
- `templates.ts` (sequenza D+1/D+7 ecc.) — non toccato. Il task era solo la mail licenza.

## Prossima sessione — sequenza raccomandata

1. `cd /Volumes/MontereyT7/FLUXION/fluxion-proxy && npm run type-check` → zero errori
2. Se OK: `wrangler deploy` dal MacBook (o iMac, dipende da configurazione CF)
3. Test smoke: acquisto test Stripe sandbox → verificare che la mail arrivi con il nuovo layout
4. Valutare se allineare `wrapLayout()` in `templates.ts` (sequenza onboarding) allo stesso
   stile chiaro per coerenza brand, oppure tenerla scura (decisione founder)

## Diff concettuale (prima → dopo)

**Prima**: dark theme (#0f0f0f / #1a1a1a), sfondo nero, testo chiaro — look da landing page.
  Problemi: (a) "Windows in arrivo" = falso, (b) indirizzo gmail in corpo, (c) niente logo,
  (d) struttura confusa (passo download macOS in evidenza prima dell'attivazione).

**Dopo**: sfondo chiaro (#f4f6f8 / #ffffff) — look fattura/ricevuta affidabile.
  Logo FLUXION in header scuro (#1a1f2e). Prezzo in evidenza (€497 / €897).
  3 passi: 1=Download (macOS+Windows, link guida), 2=Installa, 3=Attiva (CTA verde primario).
  Box "Salva questo link" separato e visibile. Sezione manuale collassata e de-enfatizzata.
  Supporto via `licenze@fluxion-app.com` (no gmail). Footer legale con P.IVA, Privacy, Unsubscribe.
