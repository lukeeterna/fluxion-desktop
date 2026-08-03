# LEDGER — Storico verdetti unità FLUXION

**REGOLA**: questo file si APPENDE, non si riscrive mai. Ogni riga è immutabile dopo il commit.
Fonte: diff reale del commit. MAI il messaggio di commit come prova di esito.
Formato: `DATA | UNITÀ | CORSIA | COMMIT_BASE | COMMIT_ESITO | VERDETTO | CAUSA | CHIAVE`
(CHIAVE = <nome-unità>@<commit_base>, aggiunta da T-VOS-RUNNER/#45v3/F6. Righe precedenti senza CHIAVE sono compatibili.)

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

2026-08-01 | T-BOOKING-FIX2/#42 | MACCHINA | 917bceee | 5250527b | VERDE | setter unico _set_context_date: lunedì prossimo=2026-08-03 (era 2077-09-13), srv=Taglio Donna (era Taglio Uomo), booking id=9636bbc7 nel DB production, FSM-DATE-SET accepted origin=context_extraction_unambiguous_date | T-BOOKING-FIX2/#42@917bceee
2026-08-02 | T-VOS-RUNNER/#45v3 | MACCHINA | 5250527b | 49737fa6 | VERDE | archivio mandati+README, SESSIONI.md R24, R28-R29 PROTOCOLLO, vos_plan.sh+vos_apply.sh, STOP.esempio, .gitignore vos/STOP, CHIAVE F6, F1: 9636bbc7 NON trovato in nessun DB (né MacBook né iMac), piano F10: 0 unità (0 mandati archiviati) | T-VOS-RUNNER/#45v3@5250527b
2026-08-02 | T-CERT-PREP/#46 | MACCHINA | 49737fa6 | c143dd9 | VERDE | F1: 2 macchine (MacBook=repo auth 49737fa6, iMac=runtime PID 3057); F2: SESSION_DIRTY da global_session_end.sh (db pattern), .gitignore legittimo; F3: engine=go registered=True SARA_TEST_CAPTURE=1 confermato; F4: 17 appuntamenti, 0 conflitti CERT-21; COPIONE scritto docs/judge/CERT-21-COPIONE.md | T-CERT-PREP/#46@49737fa6
2026-08-02 | T-CERT-GATE/#47 | MACCHINA | c143dd9 | 53a0ae8 | VERDE | F1: iMac 2c25742→c143dd9 (stash+ff-only); F2: 4 SHA256 identici iMac=MacBook; F3: vos_check.sh g)+PROTOCOLLO R30; F4: :3002 PID 41118 VOICE_ENGINE=go SARA_TEST_CAPTURE=1 registered=True reg_status=200; F5: COPIONE SSH rimosso; F6: c57e6ade+9636bbc7 già assenti (COUNT=15→15) | T-CERT-GATE/#47@c143dd9
2026-08-03 | T-CERT-RACCOLTA/#48 | MACCHINA | 989c8c6 | dbcfcd5 | VERDE | F1: WAV 3.46MB 113.5s; F2: 6 turni ricostruiti verbatim; F3: a/b/c/d/e tutti SI; F4: latenze 1483–3333ms; F5: 5 anomalie minori (latenza>800ms, farfuglio-cognome state-advance, "Comprendo" su OSCENITA, no strike-label individuali, NEXT_SESSION_PROMPT.md presente) | T-CERT-RACCOLTA/#48@989c8c6
2026-08-03 | T-GUARDRAIL-1/#49 | MACCHINA | a30341d7 | — | VERDE | F1: installer sha OK; 4 SHA256 PASS; F3: R31-33 aggiunte PROTOCOLLO (nessuna sovrascrittura R30); F4: 3 file copiati, ETICHETTA SAFE_AUTO→CONFIRM_FIRST; F5: MacBook=repo_auth, iMac=runtime_auth, stesso origin/master, MACHINES.json ACTIVE senza UUID/IP/user/path; F6: a/b/c PASS fail-closed; BUG verify KeyError repo_root segnalato a Sol | T-GUARDRAIL-1/#49@a30341d7
