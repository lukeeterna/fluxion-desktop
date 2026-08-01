# LEDGER — Storico verdetti unità FLUXION

**REGOLA**: questo file si APPENDE, non si riscrive mai. Ogni riga è immutabile dopo il commit.
Fonte: diff reale del commit. MAI il messaggio di commit come prova di esito.
Formato: `DATA | UNITÀ | CORSIA | COMMIT_BASE | COMMIT_ESITO | VERDETTO | CAUSA`

---

2026-07-30 | T-MIGRA-V2 | REPO | — | f515125 | VERDE | struttura docs/judge + vos_check.sh 7/7 istituita | msg divergente (msg: chore(vos-v2))
2026-07-30 | T-B3-PROMOTE | MACCHINA | 13f36040 | 53a8ecdc | VERDE | go engine avviata su :3002, SIP registered=True reg_status=200, RUNBOOK-AVVIO scritto
2026-07-31 | T-STRESS-VERTICALI v2 | MACCHINA | bfa135e | bfa135e | ROSSO | 6/6 verticali FAIL, FAIL_SARA=15, verticale_pronto=solo Parrucchiere, booking loop su tutti
2026-08-01 | T-BOOKING-DIAG | MACCHINA | e0cfcc4 | e0cfcc4 | VERDE | loop waiting_date diagnosticato: L1_exact SPOSTAMENTO senza guard booking_in_progress, superficie fix identificata
2026-08-01 | T-BOOKING-FIX | MACCHINA | 1e6c628 | 9c84814b | ROSSO | fix Sol applicato (L4 guard), prove di verifica non disponibili — STATE.md aggiornato ma esito non misurato in sessione
2026-08-01 | T-BOOKING-PROVE | MACCHINA | 348d459 | 348d459 | ROSSO | misura invalida: processo :3002 stantio (avviato 31 lug ante-fix), loop confermato su codice pre-fix in memoria
2026-08-01 | T-BOOKING-DIAG2 | MACCHINA | 1a46ede | 1a46ede | VERDE | causa reale identificata: processo pre-fix in memoria; dopo riavvio guard funziona, L1_exact non intercetta più in booking context
2026-08-01 | T-BOOKING-END | MACCHINA | f436160 | f436160 | ROSSO | booking bloccato a turno 8: FSM produce date=2077-09-13 (corrotta), availability_checker risponde too_far, 0 appuntamenti nel DB
2026-08-01 | T-WEB-BRIDGE | REPO | 7769074 | 7769074 | VERDE | ROADMAP-PRODUZIONE.md creata, stato 31/07 documentato, falsificati e unità residue U1-U9 strutturate | msg divergente (msg: docs(T-ROADMAP))
