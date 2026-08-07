# T-EXPOSURE v2 — Referto di esecuzione (M1–M6)

- UNIT_ID: T-EXPOSURE
- ETICHETTA: CONFIRM_FIRST — RISCHIO: C — CORSIA: MACCHINA
- BASE MINIMA: 439c71f822ba7b41747a309ca51c197cf42ebb3a
- mandate_sha256: 14e21bc77cada3f5105fea4874ffb6f9156bb8b09cbf466c390c45ee1ede63a5
- HEAD di partenza: 2762fb674ca8ff113ffc42dfe4a2efd6fbae883e (== origin/master)
- Branch di risultato: vos/t-exposure-v2-exec-20260807T125833Z
- Esito: PR di esecuzione creata, sistema NON verde (pre-merge)

Nessun contenuto sensibile (DB, licenza, backup, payload) è stato letto, aperto, dumpato o stampato. Solo metadati: path, stato tracked, blob SHA Git, dimensione byte, regola .gitignore, classificazione, digest abbreviato a 12 char.

## GATE-0 — Precondizioni (tutte PASS)

1. Repo canonico: github.com/lukeeterna/fluxion-desktop
2. HEAD == origin/master == 2762fb67
3. merge-base --is-ancestor 439c71f8 HEAD = exit 0
4. mandate SHA-256 == 14e21bc77cad… (== key suffix)
5. vos_machine validate PASS + verify --role repo_authority PASS (machine_id=macbook)
6. vos/STOP e vos/control/STOP.json assenti
7. Nessuna operazione Git in corso
8. Nessun writer concorrente (SESSIONI.md senza APERTA pendente)
9. porcelain = solo carve-out (tools/VectCutAPI, vos-out/decisions.jsonl) + tools/draft-bus-supervisor/
10. Path sensibili tracciati = esattamente i 5 pinnati
11. check-ignore --no-index conferma regola esistente per ciascuno dei 5
12. vos_check.sh = PASS=7 FAIL=1, unico FAIL b) porcelain-dirty: ?? tools/draft-bus-supervisor/
13. Riga APERTA registrata in SESSIONI.md

## M1 — Inventario current tree (senza contenuti)

| path | tracked | blob SHA (git) | bytes | regola .gitignore | classificazione |
|---|---|---|---|---|---|
| src-tauri/fluxion.db | true | df47e6c710e6 | 565248 | .gitignore:74 *.db | DATABASE_LOCAL |
| src-tauri/fluxion.db-shm | true | e5d2c35c6c3f | 32768 | .gitignore:75 *.db-shm | DATABASE_LOCAL |
| src-tauri/fluxion.db-wal | true | 49a9b46aff2b | 358472 | .gitignore:76 *.db-wal | DATABASE_LOCAL |
| .claude/cache/s317.lic | true | c11f7a323439 | 417 | .gitignore:127 .claude/cache/*.lic | LICENSE_ARTIFACT |
| .gitignore.bak-untrack-20260715_180059 | true | ab195ac4c124 | 2494 | .gitignore:147 *.bak-* | BACKUP_GENERATED |

Fail-closed verificati: nessun symlink, nessun submodule tra i 5, nessuna differenza indice-worktree, nessun contenuto staged preesistente, set == 5 pinnati.

## M2 — Branch di risultato e untrack index-only

Branch creato da HEAD: vos/t-exposure-v2-exec-20260807T125833Z.
Per ciascun path: git rm --cached -- <path>, file locale conservato byte-per-byte.

| path | preserved | bytes | digest12 (SHA-256 locale) | check-ignore |
|---|---|---|---|---|
| src-tauri/fluxion.db | true | 565248 | a324a79601e3 | PASS |
| src-tauri/fluxion.db-shm | true | 32768 | 9b0d74217b81 | PASS |
| src-tauri/fluxion.db-wal | true | 358472 | 847d0d602e4c | PASS |
| .claude/cache/s317.lic | true | 417 | c7c548bfe7d8 | PASS |
| .gitignore.bak-untrack-20260715_180059 | true | 2494 | d40c01155895 | PASS |

Nessuna regola .gitignore aggiunta o modificata. Staged = esattamente 5 deletion.

## M3 — Tooling locale fuori repository

- Sorgente: tools/draft-bus-supervisor/ (non tracciata, nessun path in git index, nessun symlink).
- Nessun processo in esecuzione dall'albero (ps + lsof negativi).
- Manifest sorgente: ./supervisor.py  11958  01cd5ca286e106beee1a426a89e0bd68b9cf08c6fb7609ca81a7f054eee0da53 (+ dir vuota runbooks/).
- Destinazione privata durevole: ~/.local/share/fluxion-draft-bus/supervisor-source-quarantine/20260807T125950Z/.
- Copia via cp -R (nessuna esecuzione); manifest destinazione == manifest sorgente (diff vuoto).
- Sorgente rimossa solo dopo verifica completa: tools/draft-bus-supervisor/ non esiste più sotto la root.
- Nessun ignore aggiunto per mascherare il path.

## M4 — Inventario history (mai bonifica)

Creato docs/judge/EXPOSURE_HISTORY.json (schema chiuso: schema_version, base_ancestor, generated_at_utc, paths, summary).

| path | commit_count | first | last | distinct_blob | max_size | class | head_tracked | history_contains |
|---|---|---|---|---|---|---|---|---|
| src-tauri/fluxion.db | 3 | ebd23ce7 | 82230487 | 3 | 565248 | DATABASE_LOCAL | false | true |
| src-tauri/fluxion.db-shm | 3 | 0079d2c3 | 94e583fe | 3 | 32768 | DATABASE_LOCAL | false | true |
| src-tauri/fluxion.db-wal | 3 | 0079d2c3 | 94e583fe | 3 | 358472 | DATABASE_LOCAL | false | true |
| .claude/cache/s317.lic | 1 | 96d40fd8 | 96d40fd8 | 1 | 417 | LICENSE_ARTIFACT | false | true |
| .gitignore.bak-untrack-20260715_180059 | 1 | 169d9e30 | 169d9e30 | 1 | 2494 | BACKUP_GENERATED | false | true |

Summary: history NON riscritta; cloni/fork precedenti possono ancora contenere gli oggetti; credenziali reali richiedono revoca separata; un rewrite richiede mandato separato + GO founder.

## M5 — Prove negative

1. git ls-files --error-unmatch non-zero per tutti e 5 (untracked)
2. Ogni file locale esiste con digest12 e dimensione invariati (vedi M2)
3. git check-ignore -q passa per tutti e 5
4. Nessun altro *.db/*.db-shm/*.db-wal/*.lic/.gitignore.bak-untrack-* tracciato
5. tools/draft-bus-supervisor/ non esiste più sotto la root
6. Destinazione privata contiene lo stesso manifest
7. git log --all mostra oggetti ancora raggiungibili (nessun rewrite)
8. Nessun path applicativo/servizio/processo modificato (:3002 non toccato)
9. vos_apply docs/judge/mandati/T-EXPOSURE.json -> exit 2, rifiuto. Gate statici vos_apply.py:79-84 rifiutano label!=SAFE_AUTO, risk!=A, lane non in {REPO,WEB,MACCHINA_READONLY}: CONFIRM_FIRST/C/MACCHINA tutti rigettati

## Eventi e stato finale (M6)

- execution_pr_created = true
- system_green = false (stato corretto pre-merge)
- next_event = INDEPENDENT_REVIEW_T_EXPOSURE_EXECUTION_PR
- La history NON è stata riscritta; nessun file locale sensibile cancellato; nessun segreto stampato.
