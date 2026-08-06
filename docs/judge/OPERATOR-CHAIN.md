# FLUXION — Catena operatori non negoziabile

## Scopo

Questa catena è l'unica architettura autorizzata per portare FLUXION in produzione headless. Trasporto, trigger e verifiche deterministiche non possono acquisire l'autorità di un operatore.

## Operatori

1. **GPT-5.6 Sol Web — autore e orchestratore**
   - scrive architettura, specifiche, codice, patch e test;
   - sceglie la prossima unità dalla roadmap e costruisce i task sigillati;
   - verifica i RESULT e coordina i passaggi;
   - non esegue comandi sulle macchine e non emette la review indipendente del proprio lavoro.

2. **Claude Code locale — esecutore macchina**
   - usa una sessione fresca per ogni unità;
   - applica letteralmente artefatti completi scritti da Sol;
   - esegue gate, test, commit, push e raccolta prove nel perimetro del mandato;
   - non inventa, corregge, amplia o riscrive codice e non giudica semanticamente il risultato.

3. **Claude Code Web — nodo GitHub attivato dagli eventi del repository**
   - parte esclusivamente da eventi GitHub filtrati e da una sessione web fresca;
   - verifica identità di repository, PR, base, head, nonce, mandato e dossier;
   - pubblica soltanto un'attestazione content-addressed del nodo e inoltra l'evento all'orchestratore;
   - non scrive codice prodotto, non esegue la macchina e non emette il verdetto semantico indipendente.

4. **Claude Web / Sonnet — reviewer indipendente e read-only**
   - usa una sessione browser nuova e stateless con modello Sonnet;
   - legge un dossier sigillato legato a base, head e hash;
   - produce soltanto `GREEN`, `RED` o `BLOCKED` con schema chiuso;
   - non modifica repository, PR, runtime, file o task e non coincide con autore, esecutore o nodo GitHub.

5. **Founder — unica autorità per `CONFIRM_FIRST` e irreversibili**
   - il GO è valido soltanto se lega unità, hash del mandato, base/head o nonce e scope richiesti;
   - nessun modello, workflow, commento o precedente consenso può inventare o riutilizzare un GO;
   - nessun gesto founder è richiesto per unità `SAFE_AUTO`, rischio A, già sigillate e prive di effetti esterni.

## Trasporti senza autorità

- Gmail Draft Bus: task e RESULT a schema chiuso; mai email ricevute come input.
- GitHub: branch, PR, commit, eventi, attestazioni e prove.
- Browser relay: trasporta byte esatti fra task Draft e sessione Claude Web; non interpreta né autorizza.

## Divieti di sostituzione

- Claude Code locale o GitHub Actions non possono sostituire Sol come autore.
- Claude Code locale, Claude Code Action o Claude Code Web non possono sostituire Claude Web Sonnet come reviewer indipendente.
- GitHub Actions non è il nodo Claude Code Web: può soltanto adattare e validare eventi deterministici.
- Sol non può auto-revisionare semanticamente il proprio codice.
- Il founder non deve eseguire copia/incolla o comandi ordinari; interviene soltanto nei gate a lui riservati.

## Condizione di funzionamento

La catena è `GREEN` soltanto dopo una prova innocua completa con evidenze osservate di tutti e cinque i ruoli. Una configurazione presente ma non attivata, una bozza non consumata, un workflow senza run o una review prodotta da una superficie diversa valgono `BLOCKED`.
