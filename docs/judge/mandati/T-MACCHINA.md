ETICHETTA: SAFE_AUTO
UNITÀ: T-MACCHINA
CORSIA: MACCHINA
RISCHIO: A
BASE DI RIFERIMENTO: T-VOS-CORE VERDE

# T-MACCHINA — pubblica stato iMac nel repo + gate anti-stantio

## Perimetro

- `bin/vos_imac_pulse.py`
- `bin/vos_check.sh`
- `docs/judge/IMAC-PULSE.json`
- `docs/judge/mandati/T-MACCHINA.md`
- `docs/judge/mandati/T-MACCHINA.json`
- `tests/test_vos_imac_pulse.py`

## Fasi

F1. Creare `bin/vos_imac_pulse.py`: connette via SSH a iMac (runtime_authority), raccoglie HEAD,
    origine, stato :3002 e SHA256 dei 4 file chiave, scrive `docs/judge/IMAC-PULSE.json`.
    Il file contiene solo dati non sensibili: nessun IP, username o path assoluto è incluso in chiaro.
F2. Creare `tests/test_vos_imac_pulse.py`: test positivi (pulse valido), test negativi
    (file assente, pulse stale > 24h, schema incompleto).
F3. Eseguire `python3 bin/vos_imac_pulse.py` → produce `docs/judge/IMAC-PULSE.json`.
F4. Aggiungere check h) a `bin/vos_check.sh`: legge `docs/judge/IMAC-PULSE.json`,
    verifica esistenza e `probed_at_utc` < 24h. FAIL se assente o stale.
F5. Eseguire `python3 -m unittest tests.test_vos_imac_pulse` — tutti PASS.
F6. Eseguire `bash bin/vos_check.sh` — 8/0 PASS.
F7. Commit, push, iMac pull, vos_check 8/0 PASS su macchina reale.

## Esito

VERDE se `docs/judge/IMAC-PULSE.json` prodotto con stato iMac live,
vos_check.sh 8/0 PASS su MacBook con iMac allineato.
