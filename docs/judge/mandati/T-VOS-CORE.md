ETICHETTA: CONFIRM_FIRST
UNITÀ: T-VOS-CORE
CORSIA: REPO
RISCHIO: A
BASE DI RIFERIMENTO: 23b8a5c

# T-VOS-CORE — esecutore reale e seeding mandati

## GATE-0 — riservato al giudice

Il giudice verifica che l’HEAD applicato sia `23b8a5c` oppure un suo discendente contenente soltanto il fix positivo di `vos_machine.py`; verifica inoltre che `bin/vos_apply.sh` sia ancora il placeholder descritto nel brief. CC non auto-dichiara GATE-0.

## Perimetro di scrittura

- `bin/vos_common.py`
- `bin/vos_apply.py`
- `bin/vos_apply.sh`
- `bin/vos_seed_mandates.py`
- `docs/judge/PROTOCOLLO.md` esclusivamente appendendo le regole 34–40
- `docs/judge/mandati/T-VOS-CORE.md`
- `docs/judge/mandati/T-VOS-CORE.json`
- `docs/judge/mandates-seed-v1.json`
- `tests/test_vos_apply.py`
- `tests/test_vos_seed_mandates.py`

## Fasi

F1. Verificare GATE-0, worktree pulito e sette controlli esistenti senza modificarne il significato.
F2. Applicare i quattro eseguibili; `vos_apply.sh` deve diventare solo wrapper fail-fast del Python.
F3. Importare il bundle mandati con un solo comando e provare overwrite diverso, SHA errato e bundle troncato.
F4. Eseguire il percorso positivo del runner in un repository temporaneo: worktree isolato, script allowlistato, risultato committato, nessun push nel test.
F5. Eseguire prove negative: `CONFIRM_FIRST`, shell libera, path fuori mandato, STOP e worktree principale sporco.
F6. Appendere le regole 34–40 senza riscrivere il protocollo integrale.
F7. Eseguire `python3 -m unittest tests.test_vos_apply tests.test_vos_seed_mandates` e poi `bash bin/vos_check.sh`.
F8. Referto con hash, prove, diff e verdetto; nessuna esecuzione di runtime o DB.

## Esito decisivo

VERDE soltanto se il placeholder è assente, il positivo crea un vero commit risultato e tutte le prove negative chiudono prima di pubblicare un branch.
