ETICHETTA: CONFIRM_FIRST
UNITÀ: T-VOS-OPERATOR-CHAIN
CORSIA: REPO
RISCHIO: A per file; attivazioni esterne GitHub/Claude/browser restano CONFIRM_FIRST e founder-gated
BASE: a6e1be2aec54980df30781f53a577e6de291a9d6

# T-VOS-OPERATOR-CHAIN

## Obiettivo

Rendere eseguibile e fail-closed la catena operatori non negoziabile, rimuovendo ogni reviewer sostitutivo e separando autore, esecutore, nodo GitHub, reviewer e founder.

## Fasi

F1. Aggiungere contratto Markdown/JSON, prompt nodo, contratto reviewer, gate e test.
F2. Rimuovere `.github/workflows/fluxion-sonnet-review.yml` e `tools/fluxion_sonnet_reviewer.py`; non sostituirli con altro modello.
F3. Eseguire i test positivi e negativi del gate.
F4. Produrre runbook e challenge content-addressed per attivare fuori repo il Draft Bus executor, la Routine CC Web e il browser relay Claude Web; non installare né dichiarare PASS senza prova live e GO founder sullo scope esterno.
F5. Emettere un dispatch innocuo e raccogliere: task Sol, RESULT CC locale, attestazione CC Web, verdict Claude Web Sonnet e prova policy founder.
F6. Dichiarare VERDE soltanto dopo round `SAFE_AUTO` completo a zero gesti e nessuna sostituzione.

## Divieti

Nessun autore diverso da Sol; nessun reviewer diverso da Claude Web Sonnet; nessun GO sintetico; nessun push diretto su master; nessuna modifica runtime/prodotto; nessun uso del workflow Sonnet Actions come prova.
