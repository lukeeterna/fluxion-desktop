# TEMPLATES_FIRED — testo pronunciato in chiamata 2026-07-17

> **LIMITE**: il logger EdgeTTSEngine tronca il campo `text='…'` a ~40 caratteri.
> Il testo INTEGRALE oltre i 40 char **non è nel log** → `[TRONCATO]`. Il file:riga del
> template nel codice sorgente NON è stato risolto in questa finestra (taglia S) → ND.
> Fonte di ogni riga = `sara_go.log` (numero riga).

## Greeting / disclosure (M1)
- «Salone Demo FLUXION, buongiorno! Come po[TRONCATO]» — sara_go.log:138
- «Salone Demo FLUXION, buon pomeriggio! Co[TRONCATO]» — sara_go.log:139
- «Salone Demo FLUXION, buonasera! Come pos[TRONCATO]» — sara_go.log:140
- «Salone Demo FLUXION, buonasera! Sono Sar[TRONCATO]» — sara_go.log:145 *(variante con nome «Sara»; disclosure «assistente virtuale» NON visibile nel troncamento → ND se pronunciata)*

## Reprompt numero telefono (loop REGISTERING_PHONE)
- «Ha ragione. Mi ripete il numero di telef[TRONCATO]» — sara_go.log:398
- «Mi dispiace. Mi ripete il numero di tele[TRONCATO]» — sara_go.log:431
- «Mi scusi. Mi ripete il numero di telefon[TRONCATO]» — sara_go.log:466
- «Capisco. Mi ripete il numero di telefono[TRONCATO]» — sara_go.log:624
- «Comprendo. Mi ripete il numero di telefo[TRONCATO]» — sara_go.log:712
- «Ha ragione. Perfetto, mi dica il numero [TRONCATO]» — sara_go.log:915

## Escalation «le passo un collega» (trigger E6 3-strike)
- «Comprendo. La passo subito a un collega.» — sara_go.log:451 *(INTEGRO, ≤40 char)*
- «Ha ragione. Certo. La passo subito a un [TRONCATO]» — sara_go.log:650
- «Mi scusi. La passo subito a un collega. » — sara_go.log:874 *(INTEGRO)*
- «Mi dispiace. La passo subito a un colleg[TRONCATO]» — sara_go.log:1011

## Intercalare / filler d'attesa (pre-sintetizzati B1, riga 130-133)
- «Ora verifico...» / «Vediamo...» / «Un attimo che controllo...» / «Un momento...» — sara_go.log:130-133 (INTEGRI)

## Prefissi di scuse/acknowledgment ripetuti («comprendo»)
Osservati come PREFISSO prepeso alla risposta, uno per turno di correzione/retry:
`Comprendo.` · `Capisco.` · `Mi scusi.` · `Mi dispiace.` · `Ha ragione.` · `Certo.` · `Prego.`
→ Fonte = prefisso empatico di reprompt (NON filler d'attesa B1). Evidenza: righe 398,431,451,624,650,712,874,915,1011,1119,1161,1181,1202.

## Fuori orario (M4-adiacente)
- «Al momento siamo fuori dall'orario di ap[TRONCATO]» — sara_go.log:1119

## Conferma numero / congedo
- «Mi scusi. Certo. Ho capito 444385516126,[TRONCATO]» — sara_go.log:1161
- «Capisco. Per confermare, il numero è 444[TRONCATO]» — sara_go.log:1181
- «Non trovo Dbeat tra i nostri clienti. Mi[TRONCATO]» — sara_go.log:158
- «Capisco. Chiaro. Grazie Dbeat Ciao Sara,[TRONCATO]» — sara_go.log:211
- «Ha ragione. Prego. Arrivederci, buona gi[TRONCATO]» — sara_go.log:1202 (congedo, exit=True)

## Congedo/ask templates pre-sintetizzati (warm-up 21:49, non necessariamente in-call)
Es. «E il cognome?», «Mi dice il cognome?», «A che ora vorresti venire?», «Scusa, me lo ridici?»,
«Ti passo un collega, un attimino...», «Arrivederci, buona giornata!» — sara_go.log:11-46 (INTEGRI, ≤40 char).
> ATTENZIONE: questi sono PRE-SINTESI di cache al boot, non prova di pronuncia in chiamata.
