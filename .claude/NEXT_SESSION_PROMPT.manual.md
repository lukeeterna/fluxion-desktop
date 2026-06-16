# FLUXION — NEXT SESSION PROMPT — S370 · PRODUCTION, NIENTE COMPROMESSI (idempotente, self-biforcante)
> Decisione founder S369: andiamo in produzione, zero compromessi. Sequenza ordinata per IRREVERSIBILITÀ, non "tutto adesso a caso". Il download Windows NON si spedisce prima del walkthrough nativo del founder: spedire un installer non collaudato a un cliente pagante è IL compromesso che la direttiva vieta. Niente è parcheggiato — è ordinato.
> Ruoli: Claude = CTO/firewall · CC = esecutore Mac/Win SSH · Luke = founder (giro fisico + decisioni).
> Regole: idempotente (ogni atto già fatto va VERIFICATO alla fonte e riportato come già-fatto, mai ripetuto — REGOLA #30). Niente `git add -A` cieco. Done-condition ESTERNA per ogni task (no validazione statica). BLOCKED-ON consentito SOLO quando un fatto terminale è fisicamente irraggiungibile in-sessione (rete/build/founder) — non è parcheggiare, è non spacciare per fatto il non-osservato. Cred mai in chat (`~/.claude/.env.fluxion-live`). WIP=1. `tauri-driver` VIETATO. MCP `filesystem:*` per il Mac, mai container Linux.

## APERTURA — chiedi al founder e BIFORCA
1. **Anelli 4-8 S369** (pagina post-pay copy / attivazione recovery / wizard #2-#3 / clienti B1 / CRUD): PASS o bloccanti? → da questa risposta dipende T4.
2. **Licenza S369 già attivata dalla mail?** → determina l'ordine del refund (vincolo fail-closed GAP 2).

## STATO S369 (verificato alla fonte — non ripetere)
🟢 Anelli E2E 1-3 VERDI: charge `ch_3Tiz7a` €1 `cs_live` succeeded → D1 prod `webhook_events` `evt_1Tiz7c` `product=base` licenza+firma → **mail RICEVUTA** da `licenze@fluxion-app.com` (🔴 deliverability storica CHIUSA). Worker `fluxion-proxy` deployato v`598dd141` (copy Passo 2 recovery-link OK, RESTA).
🟡 Anelli 4-8 = giro fisico founder (vedi APERTURA).

## T1 — CLEANUP S369 (PRIMO ATTO, reversibile)
Verifica PRIMA alla fonte lo stato attuale: charge `ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` refunded?; landing `?plan=test` contiene ancora `24007`?; `plink_1TeCftIW4bHDTsaHJfwJNndD` attivo? Poi:
- **Refund €1**: se licenza già attivata O il founder dichiara di non voler testare l'anello-5 su questo charge → refund libero; altrimenti attiva-poi-rimborsa (`license-recovery.ts:128-131` è 410 se refunded). `curl -s -X POST https://api.stripe.com/v1/refunds -u "$STRIPE_LIVE_SECRET_KEY:" -d charge=ch_3Tiz7aIW4bHDTsaH0hyVHVvJ`.
- **Ripristina landing**: `git checkout landing/checkout-consent.html` → `cd landing && npx wrangler pages deploy . --project-name=fluxion-landing --branch=main --commit-dirty=true` → verifica `curl -sL "https://fluxion-landing.pages.dev/checkout-consent?plan=test"` NON contiene più `24007`.
- **Disattiva link €1**: `curl -s -X POST https://api.stripe.com/v1/payment_links/plink_1TeCftIW4bHDTsaHJfwJNndD -u "$STRIPE_LIVE_SECRET_KEY:" -d active=false`.
Fatto terminale: refund id / deploy range / link disabled — non "fatto".

## T2 — MAIL BRANDIZZATA + COPY-PONTE (production, €0, NESSUNA dipendenza da 4-8 → si fa ORA, completa)
Rifare la mail licenza (`stripe-webhook.ts` ~righe 90-170 + `email/templates.ts`) a standard enterprise:
- **Logo FLUXION** in testa via URL assoluto `https://fluxion-landing.pages.dev/logo_fluxion.jpg` (verifica raggiungibile, altrimenti pubblicalo prima).
- Layout responsive, palette brand, **copy curata e veritiera**: NON dice "Windows in arrivo" (l'app Windows esiste) e NON contiene bottone/URL download Windows (sequencing → T4). Instrada all'attivazione via recovery/mail. CTA chiare. Niente "scrivi a gmail".
- Coerenza header/footer con `email/templates.ts`.
- Delega: `brand-guardian` (copy/tono) + `frontend-developer` (HTML email). Diff verificato dal main.
- **Proponi al founder testo + screenshot render PRIMA di chiudere** (copy verso cliente pagante).
DONE (esterna): invio reale a casella secondaria → logo visibile + copy curata + render corretto in Gmail, confermato dal founder.

## T3 — COPY-PONTE sulla PAGINA post-pagamento (`checkout-success.ts:156`)
Stessa logica di T2: veritiero, senza download Windows. Redeploy worker. DONE: `curl` pagina prod mostra copy nuovo, zero "in arrivo".

## T4 — WINDOWS PARITY / DOWNLOAD (ARMATO — parte SOLO se anelli 4-8 = PASS)
Se in apertura il founder conferma 4-8 PASS → esegui; altrimenti NON eseguire, lascialo come primo atto del ritorno founder e dillo nel report (NON è parcheggio: è dipendenza fisica dal walkthrough — spedire un installer non collaudato a un cliente pagante è il compromesso che la direttiva production vieta).
Quando sbloccato:
- a. Verifica che esista un asset installer Windows (NSIS `.exe`/`.msi`). Release `v1.0.1` `lukeeterna/fluxion-desktop` ha **0 asset** (verificato S369) → build necessaria (CI o box Windows); se non disponibile in-sessione → **BLOCKED-ON build**, non puntare ad asset inesistente.
- b. `DOWNLOAD_URL_WINDOWS` in `wrangler.*` + tipo `src/lib/types.ts:26`.
- c. Bottone reale "Scarica per Windows" in mail (`stripe-webhook.ts:109`) + pagina (`checkout-success.ts:156`).
- d. Allinea macOS a v1.0.1 SOLO dopo aver confermato che l'asset v1.0.1 macOS esiste (oggi `DMG_DOWNLOAD_URL_MACOS` punta a v1.0.0; release v1.0.1 ha 0 asset).
- e. Redeploy worker.
DONE (esterna): da una macchina Windows, click dalla mail → scarica installer reale e installa.

## INVARIATI (hard-gate, NON declassare)
- Sara chiamata-reale su TUTTI i verticali (verdetto giudice S365). Restart pipeline: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara_pipeline.log 2>&1 &"`.
- R1 Sales Agent SOSPESO fino a onboarding VERDE.
- Magazzino+alert scorte: GATE PASS S361, da riconfermare vendibile.

## RICHIESTA FINALE A CC
Apri con le 2 domande founder → esegui T1→T2→T3 (sono "adesso", nessuna dipendenza) → proponi testo+render mail per approvazione → tratta T4 secondo l'esito 4-8. Riporta ogni done-condition come esterna-osservata o BLOCKED-ON col fatto esatto mancante.

## DESIGN MAIL — chiarimenti aperti (per fare T2 al primo colpo)
Logo: jpg attuale o PNG trasparente/dark? · Palette: scuro accent blu #4a9eff o chiaro "stile fattura"? · Tono: caldo/PMI o istituzionale? · Mail di riferimento da imitare? · Footer legale (P.IVA/indirizzo/privacy/termini/unsubscribe)? · Stessa veste anche a lead-magnet (`email/templates.ts`) o solo licenza?
