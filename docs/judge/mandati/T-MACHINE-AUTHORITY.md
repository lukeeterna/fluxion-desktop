ETICHETTA: CONFIRM_FIRST
MODELLO: Claude Code locale
CORSIA: MACCHINA
UNITÀ: T-MACHINE-AUTHORITY
BASE ATTESA: 49737fa

# OBIETTIVO

Rendere esplicita e verificabile la topologia a due macchine. Registrare entrambe le macchine senza persistere seriali o UUID grezzi; assegnare esattamente una `repo_authority` e una `runtime_authority`; impedire che una macchina non registrata o un clone divergente producano stato o misure autoritative.

# PATH AUTORIZZATI

- `bin/vos_machine.py`
- `docs/judge/MACHINES.json`
- `docs/judge/PROTOCOLLO.md`
- `docs/judge/mandati/T-MACHINE-AUTHORITY.md`
- `docs/judge/SESSIONI.md`
- `docs/judge/LEDGER.md`
- `docs/judge/STATE.md`, esclusivamente `§FATTI`
- `vos/runs/20260802/T-MACHINE-AUTHORITY.md`

È vietato leggere `calls/` o `archive/`. È vietato toccare `:3002`, DB, telefonia, history o sorgenti applicativi.

# GATE-0

1. `git rev-parse --short HEAD` deve restituire `49737fa`.
2. `git rev-parse HEAD` deve coincidere con `git rev-parse origin/master`.
3. `bin/vos_check.sh` deve chiudere `PASS=7 FAIL=0` prima di scrivere.
4. `vos/STOP` deve essere assente.
5. Registrare la riga APERTA in `docs/judge/SESSIONI.md` secondo PROTOCOLLO 24/25.
6. Se una condizione fallisce, non modificare alcun path applicativo; produrre il referto ROSSO e chiudere la sessione.

# F1 — INSTALLAZIONE CONTROLLATA

Copiare integralmente dai file consegnati, senza reinterpretazione:

- `bin/vos_machine.py`
- `docs/judge/MACHINES.json`
- `docs/judge/PROTOCOLLO.md`
- questo mandato

Verificare:

```bash
python3 -m py_compile bin/vos_machine.py
python3 -m json.tool docs/judge/MACHINES.json >/dev/null
```

Lo stato iniziale `UNENROLLED` è intenzionale e deve fallire chiuso:

```bash
python3 bin/vos_machine.py validate
```

Il comando deve terminare non-zero con `machine registry is not ACTIVE`.

# F2 — PROBE DELLE DUE MACCHINE

Eseguire `bin/vos_machine.py probe` una volta su ciascuna macchina fisica, usando gli ID logici:

- `macbook-dev`
- `imac-prod`

Ogni probe deve essere prodotto dalla macchina che descrive. Il comando esegue `git fetch origin master` e chiude ROSSO se non può aggiornare il riferimento remoto; non è ammesso confrontare due `origin/master` potenzialmente stantii. Il trasferimento del solo JSON di probe può avvenire via SSH o file; non trasferire `.env`, DB, log, UUID grezzi, la chiave locale `.git/vos-machine/identity-key.bin` o credenziali. I probe devono finire in `/tmp/vos-machine-probes/` sulla macchina che costruirà il registro.

Comando da eseguire su ciascuna macchina, sostituendo soltanto l’ID logico corretto:

```bash
python3 bin/vos_machine.py probe \
  --machine-id macbook-dev \
  --roles repo_mirror \
  --service-port 3002 \
  --output /tmp/vos-machine-probes/macbook-dev.json
```

```bash
python3 bin/vos_machine.py probe \
  --machine-id imac-prod \
  --roles repo_mirror \
  --service-port 3002 \
  --output /tmp/vos-machine-probes/imac-prod.json
```

Se CC locale non dispone di un canale autenticato per eseguire il probe sull’altra macchina, chiudere ROSSO: non dedurre la seconda macchina da documenti o nomi host.

# F3 — ASSEGNAZIONE DELLE AUTORITÀ

Determinare dai fatti osservati:

- `repo_authority`: la macchina dalla quale CC locale effettua realmente commit e push autoritativi;
- `runtime_authority`: la macchina che ospita il clone `/Volumes/MacSSD - Dati/fluxion` e il listener di produzione `:3002`.

Le due autorità possono appartenere alla stessa macchina, ma ciascun ruolo deve avere un solo proprietario. Se i probe non rendono univoco uno dei due ruoli, chiudere ROSSO e non compilare il registro.

Prima della costruzione, verificare che entrambi i probe dichiarino lo stesso `origin_master` e che le macchine designate come autorità abbiano `head_equals_origin_master=true`. Una divergenza chiude ROSSO; non fare merge, rebase o reset dentro questa unità.

Calcolare lo SHA-256 del file `docs/judge/MACHINES.json` iniziale, quindi costruire il registro con i due probe e gli ID autoritativi osservati:

```bash
INITIAL_SHA=$(shasum -a 256 docs/judge/MACHINES.json | awk '{print $1}')
python3 bin/vos_machine.py build-registry \
  --probe /tmp/vos-machine-probes/macbook-dev.json \
  --probe /tmp/vos-machine-probes/imac-prod.json \
  --repo-machine "$REPO_MACHINE_ID" \
  --runtime-machine "$RUNTIME_MACHINE_ID" \
  --output docs/judge/MACHINES.json \
  --expected-sha256 "$INITIAL_SHA"
```

`REPO_MACHINE_ID` e `RUNTIME_MACHINE_ID` devono essere valorizzati con uno dei due ID logici sulla base delle osservazioni sopra, mai per convenzione.

# F4 — VERIFICA INCROCIATA

Sulla `repo_authority`:

```bash
python3 bin/vos_machine.py validate
python3 bin/vos_machine.py verify --role repo_authority
```

Sulla `runtime_authority`, se è una macchina diversa dalla repo authority, trasferire temporaneamente soltanto `bin/vos_machine.py` e il registro appena costruito sotto `/tmp`, quindi eseguire dalla root del clone remoto:

```bash
python3 /tmp/vos_machine.py verify \
  --registry /tmp/MACHINES.json \
  --role runtime_authority
```

La chiave locale HMAC resta sotto `.git/vos-machine/` sulla macchina che ha generato il probe e non viene trasferita. Su ciascuna macchina non proprietaria del ruolo richiesto, la verifica di quel ruolo deve fallire. Conservare nel referto soltanto ID logici, digest, HEAD e ruoli; non riportare identificatori hardware grezzi o path utente in chiaro.

# F5 — CRITERI DI SUCCESSO

L’unità è VERDE soltanto se:

1. il registro è `ACTIVE`;
2. contiene almeno due fingerprint distinti;
3. descrive esattamente una `repo_authority` e una `runtime_authority`;
4. entrambe le autorità erano a `origin/master` al probe;
5. la verifica passa sulle macchine corrette e fallisce sui ruoli errati;
6. nessun processo, DB o servizio è stato modificato.

# FASE CHIUSURA

1. Scrivere `vos/runs/20260802/T-MACHINE-AUTHORITY.md` con probe hash, autorità assegnate, esiti e consumo reale della corsia macchina.
2. Aggiornare `STATE.md §FATTI` con il solo stato verificato delle autorità; non toccare `DIRETTIVA` o `CODA IMPIANTO`.
3. Appendere la riga di `LEDGER.md` con CHIAVE `T-MACHINE-AUTHORITY@49737fa`.
4. Chiudere la riga in `SESSIONI.md`.
5. Eseguire `git add` soltanto sui path autorizzati, nominati uno per uno. Mai `git add -A` e mai staging di directory.
6. Committare e pushare soltanto se tutti i criteri di successo sono soddisfatti; in caso contrario committare esclusivamente referto, registri e fatti necessari alla chiusura ROSSA.
7. Ultima riga dell’output esattamente `VERDETTO: VERDE` oppure `VERDETTO: ROSSO`.
