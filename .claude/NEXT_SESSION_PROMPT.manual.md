# FLUXION — S331 resume — MASTER R-01 chiuso (G3 verde + merge). Next: LIVE smoke €1 (gated Luke)

> Scritto 2026-06-02 a chiusura S330. R-01-ter VERIFICATO e MERGED su master.
> NON ri-aprire G1/G2/G3 — tutti verdi. Evidenza: `~/venture-os/state/s330-g3-deploy-evidence.json`.

## CHIUSO IN S330 (NON ri-fare)
- **G3 E2E refund → revocation = VERDE LIVE** sul worker test `fluxion-proxy-test.gianlucanewtech.workers.dev` (v0d4cf51e):
  refund Stripe TEST `re_3TdyjW...` → webhook → KV `purchase:{email}.refunded` → `POST /api/v1/license/validate` ritorna `status:"revoked"` con `refunded_at` reale. Catena anti-refund provata end-to-end.
- Deploy `wrangler deploy --env test` OK. Secret env.test già tutti presenti (S282). Webhook TEST `we_1TaI32` già sottoscrive `charge.refunded` + `charge.dispute.created`.
- Fail-open verificato: `/validate` su email ignota → `valid`.
- **MERGE branch→master FATTO** in S330 → MASTER R-01 chiuso.

## SCOPERTA DI PROCESSO S330 (importante)
- I **subagent in background hanno Bash/Write NEGATI** (solo Read/Grep) — non possono far emergere l'approvazione permessi interattiva. Conseguenza: deploy/curl/wrangler NON delegabili a subagent; vanno eseguiti nella sessione main. Due tentativi di delega a `devops-automator` falliti per questo (+ falso-positivo hook context-budget che li auto-chiudeva). Aggiornare la strategia di delega per task che richiedono Bash con approvazione.
- Hook VOS context-budget riportava 60-69% RAW = **falso positivo** (context reale ~38% dichiarato da Luke). NON fidarsi del badge RAW per i gate critici.

## NON COPERTO da E2E S330 (rami client-side, tsc-verified only)
- offline grace -8gg → LOCK (`use-phone-home.ts`); clock-rollback guard; app `saraEnabled=false` + banner revoked.
  Richiedono app-run GUI su iMac (Keychain, REGOLA #12). Non bloccano il gate server-side production-critical.

## BLOCKED-ON (dipende da Luke / mondo reale)
- **LIVE smoke €1** sul worker di PRODUZIONE (`fluxion-proxy` prod, Stripe LIVE): acquisto €1 → refund → `/validate revoked` LIVE. REGOLA #18: nessun "production ready" senza output reale letto da Luke. = decisione di Luke (soldi veri), non tecnica.
- Custom domain `fluxion-app.com`: NS su CF ma **nessun record A** → per il go-live di produzione attaccare il custom domain al worker prod (`wrangler` route / Pages custom domain). Non blocca R-01.

## PRIMO COMANDO S331 (se Luke dà GO vendita)
Pre-flight: `curl -s https://status.stripe.com/` + worker prod `/health`. Poi LIVE smoke €1 (vedi pattern S317/S319 in MEMORY.md).
