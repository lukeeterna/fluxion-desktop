ETICHETTA: CONFIRM_FIRST
UNITÀ: T-VOS-TRIGGER-WATCHDOG
CORSIA: REPO+MACCHINA+WEB
RISCHIO: A per installazione; configurazione ruleset founder-gated una tantum
BASE DI RIFERIMENTO: T-VOS-CORE e T-VOS-REMOTE-GUARD VERDI

# T-VOS-TRIGGER-WATCHDOG

## GATE-0 — riservato al giudice

Verificare le due unità precedenti VERDI, nessun lease attivo e nessun effetto esterno aperto. Verificare sulla documentazione corrente che i trigger GitHub Routine supportino PR/release ma non push. CC non auto-dichiara GATE-0.

## Perimetro

- `bin/vos_daemon.py`, `bin/vos_watchdog.py`, `bin/vos_service.py`, `bin/vos_pr_guard.py`;
- tre workflow `.github/workflows/vos-*.yml`;
- `docs/judge/VOS-ROUTINE-PROMPT.md`, `VOS-ROUTINE-SETUP.md`;
- append protocollo 44–52, mandato MD/JSON e test;
- locali non versionati: LaunchAgent e `.git/vos-control/**`.

## Fasi

F1. Applicare file e test senza attivare servizi.
F2. Provare transizioni vietate, doppio lock, owner mismatch, lease perso, verdict stale e STOP durante processo.
F3. Provare il Guard su dispatch, PASS, FAIL, riscrittura LEDGER e path fuori mandato.
F4. Installare i due LaunchAgent; verificare intervallo, log sotto `.git` e assenza di path assoluti versionati.
F5. Configurare Routine e filtri esatti; prova con dispatch innocuo.
F6. Configurare ruleset `master`; finché PR + Guard non sono obbligatori, verdetto ROSSO.
F7. Prova collisione su `vos-control`: uno solo vince. Prova watchdog: heartbeat stale crea STOP.
F8. Prova end-to-end: claim → result branch → dispatch PR → verdict PR → merge → close.
F9. Appendere regole 44–52 e produrre referto/hash.

## Esito

VERDE soltanto dopo prova end-to-end a zero gesti e prove collisione/STOP fail-closed.
