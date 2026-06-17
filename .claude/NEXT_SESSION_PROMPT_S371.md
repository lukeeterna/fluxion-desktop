# FLUXION — NEXT SESSION PROMPT — S371 · CHIUSURA T2 (mail licenza) + T1/T3/T4

> Continua da S370. Decisione founder S369: produzione, zero compromessi. Sequenza per irreversibilità.
> Regole: idempotente (verifica alla fonte, non ripetere — REGOLA #30). `.manual.md` può essere stale: i COMMIT battono i doc. Niente `git add -A` cieco. Done-condition ESTERNA per ogni task. Cred in `~/.claude/.env.fluxion-live`, mai in chat. WIP=1.

## STATO T2 — mail licenza brandizzata (BOZZA pronta, NON deployata, NON spedita)
Rifatta a standard enterprise in `fluxion-proxy/src/routes/stripe-webhook.ts` (funzione `buildEmailHtml`). Commit base subagent `86e6cd1` + edit successivi (questa sessione). Anteprima statica: `.claude/cache/mail-licenza-preview.html` (apri con `open`).
Stato design (dopo 4 iterazioni con founder sul logo):
- **Logo = quello VERO** = icona app `src-tauri/icons/icon.png` (nastro teal/silver su quadrato navy), rasterizzata a `landing/assets/fluxion-icon.png` (256px). `logoUrl` template → `https://fluxion-landing.pages.dev/assets/fluxion-icon.png` (NON ancora live: serve deploy landing). Anteprima punta al PNG locale.
  - SCARTATI: `assets/logo.png` (= default Tauri), `landing/assets/fluxion-logo.svg` (= una "F" lettermark, NON è il brand), `logo_fluxion.jpg` (jpg con aloni).
  - File residui creati e non usati: `landing/assets/fluxion-logo-mark.svg` + `fluxion-logo-mark.png` (esperimento "F senza sfondo", scartato — eliminabili).
  - APERTO founder: vuole il quadrato navy o il nastro ritagliato? Raccomandazione CTO = tenere l'icona com'è (il nastro ha parte bianca che su sfondo bianco sparirebbe; ritagliare = alterare, vietato). **Serve OK founder sul logo.**
- Palette chiara "stile fattura", header bianco, tono caldo-PMI.
- **1 passo unico: attivazione licenza** (recovery-link + codice + Impostazioni→Gestione Licenza). RIMOSSA ogni CTA di download (sequenziata a T4; Win v1.0.1 ha 0 asset).
- Footer: SENZA "GDS Software", SENZA P.IVA inventata. Solo Privacy · Disiscriviti.

### CHIUSURA T2 (quando founder dà OK sul render+logo)
1. Deploy landing per rendere live il logo: `cd landing && npx wrangler pages deploy . --project-name=fluxion-landing --branch=main --commit-dirty=true`. Verifica `curl -sI https://fluxion-landing.pages.dev/assets/fluxion-icon.png` → 200 image/png.
2. `cd fluxion-proxy && npm run type-check` (0 err) → `npx wrangler deploy`.
3. **Invio reale** a casella secondaria founder (`gianlucadistasi81@gmail.com`) → verifica in Gmail: logo visibile + copy + render. = DONE esterna T2.

## T1 — CLEANUP S369 (reversibile) — BLOCCATO su risposta founder #2
Verifica alla fonte PRIMA: charge `ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` refunded? landing `?plan=test` contiene `24007`? `plink_1TeCftIW4bHDTsaHJfwJNndD` attivo?
- Refund €1: se licenza S369 GIÀ attivata → refund libero; altrimenti attiva-poi-rimborsa (`license-recovery.ts:128-131` = 410 se refunded). `curl -s -X POST https://api.stripe.com/v1/refunds -u "$STRIPE_LIVE_SECRET_KEY:" -d charge=ch_3Tiz7aIW4bHDTsaH0hyVHVvJ`.
- Ripristina landing: `git checkout landing/checkout-consent.html` → deploy pages → verifica niente `24007`.
- Disattiva link: `curl -s -X POST https://api.stripe.com/v1/payment_links/plink_1TeCftIW4bHDTsaHJfwJNndD -u "$STRIPE_LIVE_SECRET_KEY:" -d active=false`.

## T3 — COPY-PONTE pagina post-pagamento (`checkout-success.ts:156`)
Stessa logica T2: veritiero, niente download Windows. Redeploy worker. DONE: `curl` pagina prod mostra copy nuovo.

## T4 — WINDOWS DOWNLOAD (ARMATO) — parte SOLO se anelli 4-8 = PASS (risposta founder #1)
Release `v1.0.1` `lukeeterna/fluxion-desktop` ha 0 asset (verificato S369) → se nessun installer → BLOCKED-ON build. Dettaglio passi a/b/c/d/e in `.claude/NEXT_SESSION_PROMPT.manual.md` (S370 T4).

## 2 DOMANDE FOUNDER ancora aperte (sblocco T1/T4)
1. Anelli 4-8 (walkthrough nativo): PASS / non-fatti / bloccante?
2. Licenza S369 attivata dalla mail? sì / no (refund libero).

## INVARIATI (hard-gate)
- Sara chiamata-reale TUTTI i verticali (verdetto giudice S365). R1 Sales Agent SOSPESO fino a onboarding VERDE. Magazzino+alert: GATE PASS S361.
