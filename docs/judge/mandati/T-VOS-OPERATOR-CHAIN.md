ETICHETTA: CONFIRM_FIRST
UNITÀ: T-VOS-OPERATOR-CHAIN
CORSIA: REPO
RISCHIO: A per file; attivazioni esterne GitHub/Claude/browser restano CONFIRM_FIRST e founder-gated
BASE: a6e1be2aec54980df30781f53a577e6de291a9d6

# T-VOS-OPERATOR-CHAIN

## Obiettivo

Rendere eseguibile e fail-closed la catena operatori non negoziabile, rimuovendo ogni reviewer/autore sostitutivo e separando autore, esecutore macchina, nodo GitHub, reviewer e founder.

## Fasi

F1. Aggiungere contratto Markdown/JSON, role router root, prompt CC locale, prompt nodo CC Web, contratto reviewer, gate e test.
F2. Rimuovere `.github/workflows/fluxion-sonnet-review.yml`, `tools/fluxion_sonnet_reviewer.py` e il legacy `vos/autorun.sh`; non sostituirli con altro autore/reviewer o con push diretto su master.
F3. Rendere `CLAUDE.md` un role router fail-closed che revoca il vecchio ruolo "Architetto Capo" e subordina regole/skill/agent legacy.
F4. Eseguire i test positivi e negativi del gate.
F5. Produrre runbook e challenge content-addressed per attivare fuori repo il Draft Bus/local executor, la Routine CC Web e il browser relay Claude Web; non dichiarare PASS senza prova live e GO founder sullo scope esterno.
F6. Emettere un dispatch innocuo e raccogliere: task Sol, RESULT CC locale, attestazione CC Web, verdict Claude Web Sonnet e prova policy founder.
F7. Dichiarare VERDE soltanto dopo round `SAFE_AUTO` completo a zero gesti e nessuna sostituzione.

## Divieti

Nessun autore diverso da Sol; nessun reviewer diverso da Claude Web Sonnet; nessun GO sintetico; nessun push diretto su master; nessuna modifica runtime/prodotto; nessun uso del workflow Sonnet Actions come prova; nessun ripristino del legacy autorun o del ruolo Claude "Architetto Capo".
