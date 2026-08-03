# T-VOS-CORE/#53 — Referto esecuzione

DATA: 2026-08-03
UNITÀ: T-VOS-CORE
CORSIA: MACCHINA
RISCHIO: A
BASE: 23b8a5c0
CHIAVE: T-VOS-CORE@23b8a5c:aa7712d6afcc

---

## GATE-0
- HEAD origin/master: `23b8a5c0` — coincide con base dichiarata
- PLACEHOLDER presente in bin/vos_apply.sh: confermato (riga 118)
- vos_check.sh: PASS=7 FAIL=0

## F1 — Installer
- Candidato canonico: `/Users/macbook/Downloads/install-unit-01(1).sh`
- SHA256 calcolato: `ed0deb4fbf5dc3340de0828faa656b1ac5ca4dceba9f2442ea16c60b51f7cc42` — COINCIDE
- Nessun archivio .zip/.tar.gz trovato in ~/Downloads
- UNIT_STAGE: `/var/folders/wt/df_f2d0j1892qm4jyxgjgfsh0000gn/T/vos-unit01-stage.1ET8rb`
- FILE=11, PAYLOAD_SET_SHA256=c091343f553100d5949b522597e5a47497f82af78b9343870977477f369f1ad4
- MANIFEST verifica: 10/10 OK

## F2 — Quattro eseguibili applicati (mandate F2)
- `bin/vos_common.py` — NUOVO (7428 byte)
- `bin/vos_apply.py` — NUOVO (12830 byte, 291 righe, 0 PLACEHOLDER)
- `bin/vos_apply.sh` — SOSTITUITO: wrapper 4 righe fail-fast, PLACEHOLDER ASSENTE
- `bin/vos_seed_mandates.py` — NUOVO (2847 byte)
- `tests/test_vos_apply.py` — NUOVO (4091 byte)
- `tests/test_vos_seed_mandates.py` — NUOVO (2263 byte)
- `docs/judge/mandates-seed-v1.json` — NUOVO (15884 byte, 8 file nel bundle)

## F3 — Seeding mandati (mandate F3)
### Percorso positivo
```
PYTHONPATH=bin python3 bin/vos_seed_mandates.py docs/judge/mandates-seed-v1.json
→ {"created": 8, "identical": 0}
```
Mandati creati: T-VOS-CORE.json, T-VOS-CORE.md, T-VOS-PRIVATE-CAPSULE.json,
T-VOS-PRIVATE-CAPSULE.md, T-VOS-REMOTE-GUARD.json, T-VOS-REMOTE-GUARD.md,
T-VOS-TRIGGER-WATCHDOG.json, T-VOS-TRIGGER-WATCHDOG.md

### Prove negative
- overwrite diverso → ERRORE: overwrite rifiutato: docs/judge/mandati/T-VOS-CORE.md | EXIT=2
- SHA errato → ERRORE: SHA-256 non coincide per docs/judge/mandati/T-SHA-ERRATO.md | EXIT=2 | file NON creato
- bundle troncato → ERRORE: JSON non valido: ... | EXIT=2

## F4 — Percorso positivo runner (mandate F4)
Coperto da `test_positive_creates_real_result_commit` (test_vos_apply.py):
- worktree isolato creato, script F1 eseguito, out/result.txt='ok'
- result commit creato con vos/control/results/{nonce}.json
- published=False (nessun push)
- mandate_sha256 verificato in envelope ✓

## F5 — Prove negative (mandate F5)
- CONFIRM_FIRST → VOSFailure: etichetta CONFIRM_FIRST non SAFE_AUTO ✓
- shell libera (bash -c 'rm -rf /') → VOSFailure: script shell fuori da bin/ o tests/ ✓
- path fuori mandato (forbidden.txt) → VOSFailure: path fuori mandato ✓
- STOP locale → VOSFailure: freno locale attivo ✓
- worktree sporco → dirty_paths=['README.md'] rilevato ✓

## F6 — PROTOCOLLO regole 34-40 (mandate F6)
- PROTOCOLLO.md era 64 righe, finiva a regola 33
- Append PROTOCOLLO.append.md: 9 righe (regole 34-40)
- PROTOCOLLO.md ora 74 righe, regole 1-33 intatte, 34-40 aggiunte
- Nessun duplicato di numeri

## F7 — Test suite (mandate F7)
```
PYTHONPATH=bin python3 -m unittest tests.test_vos_apply tests.test_vos_seed_mandates -v
Ran 6 tests in 2.274s
OK
EXIT=0
```
4 test in test_vos_apply, 2 in test_vos_seed_mandates — tutti pass.

vos_check.sh (post-modifiche, pre-commit): PASS=6 FAIL=1
- FAIL b) atteso: worktree sporco con modifiche non committate

## ESITO
PLACEHOLDER: ASSENTE
Test: 6/6 OK
Mandati seeded: 8/8
Regole PROTOCOLLO: 34-40 appese senza sovrascrittura
