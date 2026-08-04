ETICHETTA: CONFIRM_FIRST
MODELLO: Claude Code locale
CORSIA: MACCHINA
UNITÀ: T-EXPOSURE v2
UNIT_ID: T-EXPOSURE
RISCHIO: C
BASE ATTESA: 439c71f822ba7b41747a309ca51c197cf42ebb3a

# OBIETTIVO

Eliminare dal nuovo HEAD l'esposizione prodotta da file locali o generati che non devono essere versionati, senza cancellare i dati locali e senza riscrivere la history.

L'unità deve:

1. rimuovere dall'indice Git, preservandone i byte sul disco, ogni database SQLite locale attualmente tracciato;
2. rimuovere dall'indice Git eventuali artefatti di licenza o di sessione/hook già coperti da `.gitignore`;
3. rimuovere dalla root del repository il solo albero locale non tracciato `tools/draft-bus-supervisor/`, trasferendolo su storage privato durevole senza eseguirlo;
4. produrre un inventario content-addressed delle esposizioni ancora presenti nella history;
5. riportare `bin/vos_check.sh` a verde senza indebolire, escludere o aggirare alcun sensore.

Questa unità NON bonifica la history. Un eventuale history rewrite richiede un mandato separato, founder-gated, dopo revoca delle credenziali coinvolte e backup verificato.

# FATTI DI PARTENZA PINNATI

Alla base attesa:

- `src-tauri/fluxion.db` è tracciato nel repository benché `.gitignore` ignori `*.db`, `*.db-shm` e `*.db-wal`;
- il database tracciato contiene dati locali/customer-like e non deve essere aperto o riportato nel referto;
- `.gitignore` contiene già le protezioni per database, `scripts/license-delivery/config.env`, `scripts/license-delivery/orders.db`, `.claude/cache/*.lic` e gli artefatti di handoff/hook;
- l'audit `STATE.RECONCILE.000001` ha misurato `vos_check PASS=8 FAIL=1`;
- l'unico fallimento dichiarato è il path locale non tracciato `tools/draft-bus-supervisor/`;
- `T-MACCHINA` è verificato;
- `origin/master`, repo authority e runtime authority sono allineati alla base attesa.

Se uno di questi fatti non è più vero, chiudere ROSSO senza adattare il mandato.

# PATH AUTORIZZATI

## Path versionati

- `.gitignore`
- `.gitignore.bak-untrack-20260715_180059`
- `src-tauri/fluxion.db`, esclusivamente per la rimozione dall'indice con conservazione byte-per-byte del file locale
- `scripts/license-delivery/config.env`, esclusivamente se tracciato
- `scripts/license-delivery/orders.db`, esclusivamente se tracciato
- `.claude/SESSION_DIRTY.md`, esclusivamente se tracciato
- `.claude/HANDOFF_CURRENT.md`, esclusivamente se tracciato
- `.claude/NEXT_SESSION_PROMPT.md`, esclusivamente se tracciato
- `.claude/NEXT_SESSION_PROMPT.manual.md`, esclusivamente se tracciato
- `.claude/cache/`, esclusivamente per artefatti `*.lic`, `HANDOFF_*` o `NEXT_SESSION_PROMPT*` già ignorati
- `docs/judge/EXPOSURE_HISTORY.json`
- `docs/judge/mandati/T-EXPOSURE.md`
- `docs/judge/mandati/T-EXPOSURE.json`
- `docs/judge/mandati/README.md`
- `docs/judge/SESSIONI.md`
- `docs/judge/LEDGER.md`
- `docs/judge/STATE.md`, esclusivamente `§FATTI`
- `vos/runs/20260804/T-EXPOSURE-v2.md`

## Path locale non versionato

- `tools/draft-bus-supervisor/`, esclusivamente come sorgente del trasferimento
- `~/.local/share/fluxion-draft-bus/supervisor-source-quarantine/<UTC_TIMESTAMP>/`, esclusivamente come destinazione privata

Nessun altro path è autorizzato. È vietato leggere `calls/`, `archive/`, file `.env`, token, password, chiavi, contenuto dei database o payload cliente.

# DIVIETI ASSOLUTI

- Nessun `git add -A`, staging di directory o glob.
- Nessun `git reset`, `clean`, `stash`, `restore`, rebase, filter-branch, filter-repo, BFG o force-push.
- Nessuna cancellazione fisica di DB, WAL, SHM, licenze o tooling locale.
- Nessuna apertura SQLite, dump, query, `strings`, hexdump o stampa dei contenuti.
- Nessuna modifica a `:3002`, telefonia, processi, dati runtime o configurazione IMAP.
- Nessuna modifica ai sensori di `vos_check.sh`.
- Nessun ignore nuovo per mascherare `tools/draft-bus-supervisor/`.
- Nessuna pubblicazione diretta su `master`.
- Nessuna modifica a `STATE.md §DIRETTIVA` o `§CODA IMPIANTO`.

# GATE-0

1. Verificare repository canonico `lukeeterna/fluxion-desktop`.
2. `git rev-parse HEAD` e `git rev-parse origin/master` devono coincidere con `439c71f822ba7b41747a309ca51c197cf42ebb3a`.
3. `python3 bin/vos_machine.py validate` e `python3 bin/vos_machine.py verify --role repo_authority` devono passare.
4. `vos/STOP` e `vos/control/STOP.json` devono essere assenti/non attivi.
5. Nessuna operazione Git deve essere in corso.
6. Nessun writer concorrente deve operare sulla corsia MACCHINA.
7. `git status --porcelain=v1` deve contenere soltanto carve-out dichiarati e `tools/draft-bus-supervisor/`; qualunque altra voce chiude ROSSO.
8. `bash bin/vos_check.sh` deve restituire esattamente `PASS=8 FAIL=1`, con unico FAIL attribuito a `tools/draft-bus-supervisor/`.
9. Registrare la riga APERTA in `docs/judge/SESSIONI.md`.

Se un gate fallisce, non modificare indice, working tree o path locali. Produrre soltanto il referto ROSSO e chiudere la sessione.

# F1 — INVENTARIO CURRENT TREE SENZA LEGGERE I CONTENUTI

Produrre l'elenco dei soli nomi e blob SHA dei file tracciati che ricadono nelle classi:

- `*.db`
- `*.db-shm`
- `*.db-wal`
- `*.lic`
- `scripts/license-delivery/config.env`
- `.claude/SESSION_DIRTY.md`
- `.claude/HANDOFF_CURRENT.md`
- `.claude/NEXT_SESSION_PROMPT*`
- `.claude/HANDOFF_*`
- `.gitignore.bak-untrack-*`

Per ogni path registrare esclusivamente:

- path;
- stato tracked/untracked;
- blob SHA Git, se tracciato;
- dimensione byte;
- regola `.gitignore` applicabile;
- classificazione `DATABASE_LOCAL`, `LICENSE_ARTIFACT`, `HOOK_ARTIFACT`, `BACKUP_GENERATED` o `FALSE_POSITIVE`.

Non calcolare né pubblicare hash del contenuto working-tree di file segreti, salvo il solo `src-tauri/fluxion.db` per la verifica privata prima/dopo prevista in F2.

Condizioni fail-closed:

- un path sensibile tracciato fuori dai PATH AUTORIZZATI;
- un file non ignorato che richiede una nuova decisione;
- un symlink;
- un submodule;
- differenza tra indice e working tree su un path da untrackare;
- contenuto staged preesistente.

# F2 — UNTRACK INDEX-ONLY E CONSERVAZIONE LOCALE

Per ogni path tracciato e già protetto da `.gitignore`:

1. calcolare privatamente SHA-256 e dimensione del file locale;
2. eseguire soltanto `git rm --cached -- <path>`;
3. verificare che il file locale esista ancora;
4. verificare SHA-256 e dimensione invariati;
5. verificare `git check-ignore -q -- <path>`;
6. registrare nel referto soltanto `preserved=true`, dimensione e digest abbreviato a 12 caratteri.

`src-tauri/fluxion.db` deve essere trattato esclusivamente in questo modo. La deroga è limitata alla rimozione dall'indice richiesta dalla presente unità; il file runtime e i suoi byte restano carve-out permanenti.

Se `.gitignore` non copre già un path, non aggiungere una regola per convenienza: chiudere ROSSO e riportare il path.

Rimuovere dall'indice anche `.gitignore.bak-untrack-20260715_180059` soltanto se è tracciato e identico o semanticamente subordinato alla `.gitignore` corrente. Il file locale va preservato e deve risultare ignorato da una regola backup già esistente.

# F3 — TOOLING LOCALE FUORI REPOSITORY

Se `tools/draft-bus-supervisor/` esiste:

1. verificare che ogni suo path sia non tracciato;
2. verificare che nessun processo stia eseguendo file da quell'albero;
3. produrre un manifest locale con path relativo, dimensione e SHA-256;
4. creare la destinazione privata `~/.local/share/fluxion-draft-bus/supervisor-source-quarantine/<UTC_TIMESTAMP>/`;
5. trasferire l'albero senza eseguirlo;
6. verificare il manifest nella destinazione;
7. rimuovere la sorgente soltanto dopo verifica completa;
8. non aggiungere il path a `.gitignore`.

Se un file è tracciato, in uso, cambia durante la copia o non coincide al termine, chiudere ROSSO e lasciare intatta la sorgente.

# F4 — INVENTARIO HISTORY, MAI BONIFICA

Creare `docs/judge/EXPOSURE_HISTORY.json` con schema chiuso:

- `schema_version`;
- `base_commit`;
- `generated_at_utc`;
- `paths`;
- `summary`.

Per ogni path rimosso dall'indice registrare, senza leggere il contenuto:

- path;
- primo commit raggiungibile che lo contiene;
- ultimo commit raggiungibile che lo contiene;
- numero di commit raggiungibili che lo contengono;
- blob SHA distinti;
- dimensione massima;
- classificazione;
- `current_head_tracked=false`;
- `history_still_contains=true`.

Il campo `summary` deve dichiarare esplicitamente:

- la history non è stata riscritta;
- un clone precedente può ancora contenere gli oggetti;
- qualsiasi credenziale reale eventualmente identificata richiede revoca separata;
- un eventuale rewrite richiede mandato separato e GO founder.

Non includere valori, record, email, telefoni, licenze o porzioni di contenuto.

# F5 — PROVE NEGATIVE

Senza modificare file aggiuntivi, dimostrare:

1. `git ls-files --error-unmatch src-tauri/fluxion.db` termina non-zero;
2. `src-tauri/fluxion.db` esiste localmente e ha digest/size uguali a prima;
3. `git check-ignore -q src-tauri/fluxion.db` passa;
4. nessun `*.db`, `*.db-shm`, `*.db-wal` o `*.lic` locale autorizzato risulta tracciato;
5. gli artefatti hook/handoff autorizzati risultano ignorati e non tracciati;
6. `tools/draft-bus-supervisor/` non esiste più sotto la root;
7. la destinazione privata contiene lo stesso manifest;
8. `git log --all` dimostra che la history contiene ancora gli oggetti, senza alcun rewrite;
9. nessun path applicativo o runtime è cambiato.

# F6 — VERIFICA FINALE

Eseguire:

```bash
python3 -m unittest tests.test_vos_apply tests.test_vos_seed_mandates
bash bin/vos_check.sh
```

Criteri obbligatori:

- test VOS verdi;
- `vos_check PASS=9 FAIL=0`;
- repository working tree contenente soltanto i path autorizzati della presente unità;
- nessun file locale sensibile cancellato;
- nessuna history riscritta;
- nessun servizio o processo modificato;
- nessun segreto stampato.

# FASE CHIUSURA

1. Scrivere `vos/runs/20260804/T-EXPOSURE-v2.md` con inventario sanitizzato, prove e verdict.
2. Aggiornare `STATE.md §FATTI` con il solo esito misurato e il nuovo HEAD; non toccare `DIRETTIVA` o `CODA IMPIANTO`.
3. Appendere la riga in `LEDGER.md` con CHIAVE `T-EXPOSURE@439c71f8` e `COMMIT_ESITO=—`.
4. Chiudere la riga in `SESSIONI.md`.
5. Creare un branch dedicato; non lavorare o pubblicare direttamente su `master`.
6. Eseguire `git add --` soltanto sui singoli path autorizzati, nominati uno per uno. Per le rimozioni dall'indice usare i path esatti.
7. Committare soltanto se F1–F6 sono verdi.
8. Pubblicare il branch e aprire una PR verso `master`; non abilitare auto-merge.
9. La PR richiede review indipendente Claude Web `GREEN` prima di qualunque merge.
10. Ultima riga dell'output esattamente `VERDETTO: VERDE` oppure `VERDETTO: ROSSO`.
