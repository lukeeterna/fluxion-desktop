ETICHETTA: CONFIRM_FIRST
UNITÀ: T-VOS-REMOTE-GUARD
CORSIA: MACCHINA_READONLY
RISCHIO: A
BASE DI RIFERIMENTO: unità T-VOS-CORE VERDE

# T-VOS-REMOTE-GUARD — rimozione credenziali e path dal controllo g)

## GATE-0 — riservato al giudice

Il giudice verifica T-VOS-CORE VERDE, il fix HMAC positivo di `vos_machine.py` e la presenza nel vecchio `vos_check.sh` di utente, IP, path e identity file in chiaro. CC non auto-dichiara GATE-0.

## Perimetro

- `bin/vos_remote_check.py`
- `bin/vos_check.sh`
- `docs/judge/REMOTE-CHECK.json`
- `docs/judge/PROTOCOLLO.md` solo append regole 41–43
- `docs/judge/mandati/T-VOS-REMOTE-GUARD.md`
- `docs/judge/mandati/T-VOS-REMOTE-GUARD.json`
- `tests/test_vos_remote_check.py`
- locale non versionato: `.git/vos-remote/runtime.json`

## Fasi

F1. Verificare GATE-0 e salvare il vecchio controllo g) come evidenza privata, senza ripubblicarne i valori.
F2. Applicare script, policy e test. Confermare con grep che nessun vecchio IP, username, path o identity file resti nei file versionati.
F3. Configurare `.git/vos-remote/runtime.json` usando i fatti locali già noti a CC; permessi `0600`; nessun output del valore nel referto.
F4. Test positivi con subprocess mockato e test negativi per host key disabilitata, timeout, output malformato, HEAD/branch/dirty discordanti.
F5. Eseguire il controllo reale g). Se SSH non risponde, mantenere FAIL e chiudere l’unità ROSSA: non attenuare il sensore.
F6. Eseguire `bash bin/vos_check.sh`; devono restare sette risultati a,b,c,c,d,f,g.
F7. Appendere regole 41–43 e produrre hash/referto.

## Esito

VERDE solo se i valori locali non sono più versionati e il controllo reale conserva la semantica fail-closed.
