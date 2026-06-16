================================================================
 FLUXION — REPORT SESSIONE S369 — 16 giugno 2026
 Tema: pipeline cliente E2E con acquisto €1 LIVE dal funnel landing
================================================================

------------------------------------------------------------
 1. COSA È STATO FATTO (con evidenze reali)
------------------------------------------------------------
A) Verifica read-only #0.a/#0.b + GAP 3 (fonte: codice)
   - Checkout landing = Payment Link STATICI in landing/checkout-consent.html
   - Modalità = cs_live REALE (nessun /test/ nell'URL; confermato via API Stripe)
   - From mail licenza = From refund = licenze@fluxion-app.com (dominio verificato S342)
     -> stripe-webhook.ts:190  ==  refund.ts:185

B) Predisposizione test (autonomo via API Stripe live)
   - Trovato + RIATTIVATO il Payment Link €1 (plink_1TeCft...24007)
   - Worker fluxion-proxy DEPLOYATO in prod (version 598dd141, copy Passo 2 recovery-link)
   - Landing: aggiunto piano nascosto "test"=€1 a /checkout-consent?plan=test
     (pulsanti pubblici Base/Pro INTATTI €497/€897 -> zero rischio clienti veri)
   - Deploy landing in PROD (fluxion-landing.pages.dev, branch main) verificato live

C) Acquisto €1 LIVE eseguito dal founder dal funnel landing reale

------------------------------------------------------------
 2. AVANZAMENTO E2E (clausola leg-by-leg S369)
------------------------------------------------------------
 [PASS] Anello 1 — checkout €1 completato
        charge ch_3Tiz7a | €1 | succeeded | cs_live_a1iJuRsjll... | ilcombeeretrasher@gmail.com
 [PASS] Anello 2 — riga in D1 prod
        webhook_events: evt_1Tiz7c | product=base | license_id 9972c3c6... | payload+firma presenti
 [PASS] Anello 3 — DELIVERABILITY (era 🔴 storico, ORA CHIUSA)
        email_sent_at popolato + mail RICEVUTA dal founder, mittente licenze@fluxion-app.com
 [DA CONFERMARE] Anello 4 — pagina post-pagamento copy nuovo (recovery-link)
 [DA CONFERMARE] Anello 5 — attivazione via percorso DEFAULT (link recovery, non carica-file)
 [DA CONFERMARE] Anello 6 — wizard: P.IVA errata->toast (#2); dropdown step6 no overlap (#3)
 [DA CONFERMARE] Anello 7 — clienti B1: telefono vuoto -> toast "Controlla i campi"
 [DA CONFERMARE] Anello 8 — CRUD clienti completo senza bloccanti

 => Anelli 1-3 sono il cuore della "verità #2/#3" (pagamento reale + licenza + mail).
    Mancano solo gli anelli che dipendono dal tuo giro fisico (4-8).

------------------------------------------------------------
 3. BUG NUOVO (segnalato da te) — copy "Windows in arrivo"
------------------------------------------------------------
 La mail/pagina dicono "Versione Windows in arrivo", ma l'app Windows gira già (dal 10/06).
 Posizioni:
   - fluxion-proxy/src/routes/stripe-webhook.ts:109   (MAIL licenza)
   - fluxion-proxy/src/routes/checkout-success.ts:156 (PAGINA post-pagamento)
 BLOCCO: non esiste una URL di download Windows pubblicata (in env c'è solo
 DMG_DOWNLOAD_URL_MACOS). Per togliere "in arrivo" e mettere un bottone reale serve
 prima pubblicare l'installer Windows. -> vedi chiarimenti, punto (a).

------------------------------------------------------------
 4. CLEANUP IN SOSPESO (lo faccio io, reversibile) — vedi punto (c)
------------------------------------------------------------
 1) Rimborso €1 charge ch_3Tiz7a (SOLO dopo che hai attivato la licenza)
 2) Ripristino landing (rimuovo piano test + redeploy prod)
 3) Disattivo link €1 (plink_1TeCft...24007)

------------------------------------------------------------
 5. CHIARIMENTI DI CUI HO BISOGNO DA TE
------------------------------------------------------------
 (a) FIX WINDOWS: dove pubblico l'installer Windows? (GitHub Release .msi/.exe?)
     Mi serve la URL pubblica reale per sostituire "Windows in arrivo" con un
     bottone "Scarica per Windows" in mail + pagina. Senza URL non lo "fixo a vuoto".
 (b) ANELLI 4-8: come è andato il giro? Wizard (#2/#3), clienti B1, CRUD: PASS o
     hai trovato bloccanti? Dimmi e li chiudo/loggo.
 (c) CLEANUP: hai GIÀ attivato la licenza dalla mail? Se sì rimborso subito il €1
     e ripristino landing + disattivo link. Se non ancora, aspetto tua conferma.

------------------------------------------------------------
 6. NEXT PROMPT (S370)
------------------------------------------------------------
 File canonico: .claude/NEXT_SESSION_PROMPT.manual.md
 In sintesi:
   1. CLEANUP S369 (refund €1 + revert landing + disable link) se non già fatto
   2. Confermare/chiudere anelli 4-8 col tuo feedback
   3. FIX copy Windows (gated sulla URL download — punto 5a)
   4. (invariati) Sara chiamata-reale tutti-verticali = hard-gate pre-vendita; R1 sospeso

------------------------------------------------------------
 7. NOTA CONTEXT
------------------------------------------------------------
 Sessione lunga: l'hook VOS segna ~67% (soglia 60%). Lo stato è tutto committato
 (6c6ec6e) + in questo report. Posso continuare per cleanup/anelli 4-8 oppure
 chiudere ordinato: dimmi tu. Niente è perso.
================================================================
