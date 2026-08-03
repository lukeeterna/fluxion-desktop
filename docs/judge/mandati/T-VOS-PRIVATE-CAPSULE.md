ETICHETTA: CONFIRM_FIRST
UNITÀ: T-VOS-PRIVATE-CAPSULE
CORSIA: REPO+WEB
RISCHIO: A
BASE DI RIFERIMENTO: T-VOS-TRIGGER-WATCHDOG VERDE

# T-VOS-PRIVATE-CAPSULE

## GATE-0 — riservato al giudice

Verificare che CC Web conservi accesso al repository una volta privato e che il giudice indipendente non venga descritto come capace di revisionare hash senza contenuto. Verificare che non vi siano segreti o dati cliente nelle evidenze candidate.

## Perimetro

- `bin/vos_capsule.py`, `bin/vos_witness.py`;
- `docs/judge/PRIVATE-REPO-OPERATIONS.md`;
- append protocollo 53–58;
- mandato MD/JSON e test.

## Fasi

F1. Creare repo fixture, commit base e result commit entro allowlist.
F2. Creare due capsule identiche e verificare byte/hash identici.
F3. Verificare manifest, diff, blob, evidence hash e rifiuto path fuori mandato.
F4. Alterare un byte della capsula: verify deve chiudere ROSSO.
F5. Creare record unsigned solo con flag test; senza firma deve fallire.
F6. Creare chiave fixture OpenSSH, firmare e verificare con allowed-signers.
F7. Ispezionare record pubblico: nessun path, sorgente, URL in chiaro, IP o dato locale.
F8. Prova su un result branch reale e trasferimento controllato al giudice indipendente.

## Esito

VERDE quando capsula e witness sono riproducibili, fail-closed e il limite semantico è dichiarato senza ambiguità.
