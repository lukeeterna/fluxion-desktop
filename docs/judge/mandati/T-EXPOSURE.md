ETICHETTA: CONFIRM_FIRST
MODELLO: Claude Code locale
CORSIA: MACCHINA
UNITÀ: T-EXPOSURE v2
UNIT_ID: T-EXPOSURE
RISCHIO: C
BASE MINIMA: 439c71f822ba7b41747a309ca51c197cf42ebb3a

# OBIETTIVO

Rimuovere dal nuovo HEAD l'esposizione prodotta da file locali o generati che non devono essere versionati, preservandone byte-per-byte le copie locali, trasferire fuori repository il tooling locale non tracciato e produrre un inventario content-addressed delle esposizioni ancora raggiungibili nella history.

Questa unità NON riscrive né bonifica la history. Un eventuale history rewrite richiede un mandato separato, founder-gated, dopo revoca delle credenziali coinvolte e backup verificato.

Il workflow è sequenziale e usa sessioni fresche:

1. questa PR sigilla il mandato;
2. dopo review indipendente GREEN e GO founder legato all'hash del mandato, una nuova sessione Claude Code prepara la PR di esecuzione;
3. Claude Web revisiona la PR di esecuzione;
4. dopo GREEN, il workflow esegue il merge autorizzato e una nuova sessione post-merge riconcilia repo authority e runtime authority;
5. il ciclo si chiude soltanto quando una riconciliazione misura tutti gli otto esiti di `bin/vos_check.sh` verdi, eventualmente passando dal mandato T-MACCHINA per riallineamento/pulse senza riaprire questa diagnosi.

Nessuna fase successiva è autorizzata se la precedente non ha prodotto l'evento e le prove richieste.

# FATTI DI PARTENZA PINNATI

Alla base minima:

- i path sensibili tracciati da rimuovere dall'indice sono esattamente:
  - `src-tauri/fluxion.db`;
  - `src-tauri/fluxion.db-shm`;
  - `src-tauri/fluxion.db-wal`;
  - `.claude/cache/s317.lic`;
  - `.gitignore.bak-untrack-20260715_180059`;
- `.gitignore` protegge già rispettivamente `*.db`, `*.db-shm`, `*.db-wal`, `.claude/cache/*.lic` e `*.bak-*`;
- `tools/draft-bus-supervisor/` è un albero locale non tracciato;
- `bin/vos_check.sh` emette esattamente otto esiti nominali: a, b, c/STATE, c/PROTOCOLLO, d, f, g, h;
- nello stato pre-esecuzione atteso, `vos_check` deve misurare `PASS=7 FAIL=1`, con unico FAIL `b) porcelain-dirty` attribuibile a `tools/draft-bus-supervisor/`;
- `T-MACCHINA` è verificato;
- repo authority, runtime authority e `origin/master` sono allineati al checkpoint corrente prima dell'esecuzione.

Se uno di questi fatti non è più vero, chiudere ROSSO senza adattare il mandato.

# PATH AUTORIZZATI

## Path versionati modificabili nella PR di esecuzione

- `src-tauri/fluxion.db`, esclusivamente per `git rm --cached --` con conservazione byte-per-byte locale;
- `src-tauri/fluxion.db-shm`, esclusivamente per `git rm --cached --` con conservazione byte-per-byte locale;
- `src-tauri/fluxion.db-wal`, esclusivamente per `git rm --cached --` con conservazione byte-per-byte locale;
- `.claude/cache/s317.lic`, esclusivamente per `git rm --cached --` con conservazione byte-per-byte locale;
- `.gitignore.bak-untrack-20260715_180059`, esclusivamente per `git rm --cached --` con conservazione byte-per-byte locale;
- `docs/judge/EXPOSURE_HISTORY.json`;
- `docs/judge/SESSIONI.md`;
- `docs/judge/LEDGER.md`;
- `docs/judge/STATE.md`, esclusivamente `§FATTI`;
- `vos/runs/20260804/T-EXPOSURE-v2.md`.

Nessun altro path versionato è autorizzato. `.gitignore`, i sensori, `§DIRETTIVA` e `§CODA IMPIANTO` restano in sola lettura.

## Path locali non versionati

- `tools/draft-bus-supervisor/`, esclusivamente come sorgente del trasferimento;
- `~/.local/share/fluxion-draft-bus/supervisor-source-quarantine/<UTC_TIMESTAMP>/`, esclusivamente come destinazione privata durevole;
- le copie locali dei cinque path rimossi dall'indice, esclusivamente per verifica privata di esistenza, dimensione e digest prima/dopo.

Il path locale `tools/draft-bus-supervisor/` non appartiene all'allowlist Git del manifest perché non deve mai entrare nell'indice.

È vietato leggere `calls/`, `archive/`, file `.env`, token, password, chiavi, contenuto dei database, contenuto della licenza o payload cliente.

# DIVIETI ASSOLUTI

- Nessun `git add -A`, staging di directory o glob.
- Nessun `git reset`, `clean`, `stash`, `restore`, rebase, filter-branch, filter-repo, BFG o force-push.
- Nessuna cancellazione fisica di DB, WAL, SHM, licenza, backup o tooling locale prima della copia verificata.
- Nessuna apertura SQLite, dump, query, `strings`, hexdump o stampa dei contenuti.
- Nessuna modifica o riavvio di `:3002`, telefonia, processi applicativi, dati runtime o configurazione IMAP.
- Nessuna modifica ai sensori di `bin/vos_check.sh`.
- Nessun nuovo ignore per mascherare `tools/draft-bus-supervisor/`.
- Nessun push diretto su `master`.
- Nessun auto-merge.
- Nessuna modifica a `STATE.md §DIRETTIVA` o `§CODA IMPIANTO`.
- Nessuna esecuzione tramite `vos_apply`: `CONFIRM_FIRST`, rischio C e corsia MACCHINA devono essere rifiutati dall'esecutore automatico.

# GATE-0 — PRECONDIZIONI SULLA REPO AUTHORITY

1. Verificare repository canonico `lukeeterna/fluxion-desktop`.
2. `git rev-parse HEAD` deve coincidere con `git rev-parse origin/master`.
3. `git merge-base --is-ancestor 439c71f822ba7b41747a309ca51c197cf42ebb3a HEAD` deve terminare zero.
4. Il Markdown e il manifest sigillati devono essere presenti su HEAD; l'hash SHA-256 del Markdown deve coincidere con `mandate_sha256` e con il suffisso della `key`.
5. `python3 bin/vos_machine.py validate` e `python3 bin/vos_machine.py verify --role repo_authority` devono passare.
6. `vos/STOP` e `vos/control/STOP.json` devono essere assenti/non attivi.
7. Nessuna operazione Git deve essere in corso.
8. Nessun writer concorrente deve operare sulla corsia MACCHINA.
9. `git status --porcelain=v1` deve contenere soltanto carve-out permanenti già dichiarati e `tools/draft-bus-supervisor/`; qualunque altra voce chiude ROSSO.
10. L'insieme dei path sensibili tracciati nelle classi `*.db`, `*.db-shm`, `*.db-wal`, `*.lic`, `.gitignore.bak-untrack-*` deve coincidere esattamente con i cinque path elencati nei FATTI DI PARTENZA PINNATI.
11. `git check-ignore` deve confermare una regola già esistente per ciascuno dei cinque path.
12. `bash bin/vos_check.sh` deve emettere esattamente otto esiti e il riepilogo `PASS=7 FAIL=1`; l'unico FAIL deve essere `b) porcelain-dirty` e deve citare soltanto `tools/draft-bus-supervisor/`.
13. Registrare la riga APERTA in `docs/judge/SESSIONI.md`.

Se un gate fallisce, non modificare indice, working tree o path locali. Produrre soltanto il referto ROSSO e chiudere la sessione.

# M1 — INVENTARIO CURRENT TREE SENZA CONTENUTI

Per ciascuno dei cinque path registrare esclusivamente path, stato tracked, blob SHA Git, dimensione byte, regola `.gitignore` applicabile e classificazione `DATABASE_LOCAL`, `LICENSE_ARTIFACT` o `BACKUP_GENERATED`.

Non riportare hash completi del working tree, valori, record o porzioni di contenuto.

Condizioni fail-closed: insieme diverso dai cinque path pinnati; path sensibile tracciato fuori allowlist; file non ignorato; symlink; submodule; differenza tra indice e working tree su un path da untrackare; contenuto staged preesistente.

# M2 — BRANCH DI RISULTATO E UNTRACK INDEX-ONLY

1. Creare un branch dedicato da HEAD, senza pubblicarlo ancora.
2. Per ciascuno dei cinque path:
   - calcolare privatamente SHA-256 e dimensione;
   - eseguire soltanto `git rm --cached -- <path>`;
   - verificare che il file locale esista ancora;
   - verificare SHA-256 e dimensione invariati;
   - verificare `git check-ignore -q -- <path>`;
   - registrare nel referto soltanto `preserved=true`, dimensione e digest abbreviato a 12 caratteri.
3. Nessuna regola `.gitignore` può essere aggiunta o modificata.

Se un byte locale cambia o un path non è già ignorato, chiudere ROSSO.

# M3 — TOOLING LOCALE FUORI REPOSITORY

Se `tools/draft-bus-supervisor/` esiste:

1. verificare che ogni suo path sia non tracciato;
2. verificare che nessun processo stia eseguendo file da quell'albero;
3. produrre un manifest locale con path relativo, dimensione e SHA-256;
4. creare la destinazione privata `~/.local/share/fluxion-draft-bus/supervisor-source-quarantine/<UTC_TIMESTAMP>/`;
5. copiare l'albero senza eseguirlo;
6. verificare il manifest nella destinazione;
7. rimuovere la sorgente soltanto dopo verifica completa;
8. non aggiungere il path a `.gitignore`.

Se un file è tracciato, in uso, cambia durante la copia o non coincide al termine, chiudere ROSSO e lasciare intatta la sorgente.

# M4 — INVENTARIO HISTORY, MAI BONIFICA

Creare `docs/judge/EXPOSURE_HISTORY.json` con schema chiuso: `schema_version`, `base_ancestor`, `generated_at_utc`, `paths`, `summary`.

Per ciascuno dei cinque path registrare, senza leggere il contenuto: path, primo e ultimo commit raggiungibile che lo contiene, numero di commit, blob SHA distinti, dimensione massima, classificazione, `current_result_head_tracked=false`, `history_still_contains=true`.

Il `summary` deve dichiarare che la history non è stata riscritta, clone precedenti possono ancora contenere gli oggetti, credenziali reali richiedono revoca separata e un rewrite richiede mandato separato e GO founder. Non includere valori o porzioni di contenuto.

# M5 — PROVE NEGATIVE

Dimostrare:

1. `git ls-files --error-unmatch` termina non-zero per ciascuno dei cinque path;
2. ciascun file locale esiste e conserva digest e dimensione;
3. `git check-ignore -q` passa per ciascuno dei cinque path;
4. nessun altro `*.db`, `*.db-shm`, `*.db-wal`, `*.lic` o `.gitignore.bak-untrack-*` autorizzato risulta tracciato;
5. `tools/draft-bus-supervisor/` non esiste più sotto la root;
6. la destinazione privata contiene lo stesso manifest;
7. `git log --all` dimostra che la history contiene ancora gli oggetti, senza rewrite;
8. nessun path applicativo, servizio o processo è cambiato;
9. `vos_apply` rifiuta il manifest perché `label=CONFIRM_FIRST`, `risk=C` e `lane=MACCHINA`.

# M6 — COMMIT, VERIFICA PRE-PR E PR DI ESECUZIONE

1. Scrivere `vos/runs/20260804/T-EXPOSURE-v2.md` con inventario sanitizzato, prove, eventi e stato.
2. Aggiornare `STATE.md §FATTI` soltanto con l'esito misurato; non dichiarare il sistema verde e non toccare `DIRETTIVA` o `CODA IMPIANTO`.
3. Appendere in `LEDGER.md` la riga `T-EXPOSURE@439c71f8` con `COMMIT_ESITO=—`.
4. Chiudere la riga in `SESSIONI.md`.
5. Eseguire `git add --` soltanto sui singoli path autorizzati, nominati uno per uno.
6. Committare sul branch dedicato e verificare working tree pulito.
7. Eseguire `python3 -m unittest tests.test_vos_apply tests.test_vos_seed_mandates`.
8. Eseguire `bash bin/vos_check.sh`: sul branch di risultato deve emettere `PASS=7 FAIL=1`, con unico FAIL `a) HEAD!=origin/master`; tutti gli altri sette esiti devono essere PASS. Questo è lo stato corretto pre-merge e non equivale a produzione.
9. Pubblicare il branch e aprire una PR verso `master`; non abilitare auto-merge.
10. La sessione termina con `execution_pr_created=true`, `system_green=false`, `next_event=CLAUDE_WEB_REVIEW_T_EXPOSURE_EXECUTION_PR` e ultima riga `VERDETTO: VERDE` oppure `VERDETTO: ROSSO`.

# M7 — REVIEW, MERGE E RICONCILIAZIONE POST-MERGE

Questa fase non viene eseguita nella sessione M1–M6.

1. Claude Web revisiona indipendentemente la PR di esecuzione.
2. Solo con verdetto GREEN e con il GO founder legato al presente `mandate_sha256` il workflow può eseguire il merge; nessun auto-merge.
3. Dopo il merge, aprire una nuova sessione Claude Code.
4. Verificare su repo authority `HEAD==origin/master` e che la base minima resti antenata.
5. Riallineare runtime authority con fast-forward soltanto nel perimetro autorizzato dal GO, senza riavviare servizi e verificando prima/dopo la conservazione dei DB locali.
6. Se il pulse è stale o il sensore macchina non è verde, eseguire il mandato T-MACCHINA come unità separata e sessione fresca.
7. Eseguire una nuova `STATE.RECONCILE` read-only.
8. La chiusura globale richiede esattamente otto esiti `vos_check`, `PASS=8 FAIL=0`, nessun segreto stampato, nessun file locale sensibile cancellato e nessuna history riscritta.
9. Solo allora emettere `T_EXPOSURE_COMPLETE` e rendere eleggibile la successiva unità della coda.

# PASSO MANIFEST F1 — VALIDAZIONE DEL CONTROL PLANE

Il solo passo dichiarato nel manifest è:

```bash
python3 -m unittest tests.test_vos_apply tests.test_vos_seed_mandates
```

Gli identificatori delle operazioni manuali sono `M1..M7` e non collidono con `F1`. Il manifest non è auto-eseguibile e `vos_apply` deve rifiutarlo prima di qualunque effetto.
