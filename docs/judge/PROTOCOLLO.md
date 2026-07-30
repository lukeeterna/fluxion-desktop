# PROTOCOLLO — Invarianti del sistema giudice

1. RUOLI. Sol scrive il codice leggendo il repo a un commit PINNATO, non tocca mai git. CC esegue tutto il lavoro macchina. Il founder ha due soli atti: sigillo estetico e GO sulle azioni che escono dal repo. Il giudice legge in sola lettura, emette blocchi, non giudica le unità conformi.
2. VIETATO che lo stesso modello scriva un artefatto e lo giudichi.
3. Un solo blocco attivo alla volta, cross-venture. Ogni blocco = una sessione CC NUOVA, una consegna. Ogni blocco inizia con la riga MODELLO:.
4. FONTE DI VERITÀ = docs/judge/STATE.md. Gli handoff in prosa sono aboliti. Fa fede il diff, mai il messaggio di commit. Una dichiarazione di assenza vale quanto la copertura dello strumento che l'ha prodotta.
5. CHIUSURA. Ogni unità che scrive ha una FASE CHIUSURA anche su rosso. Ultima riga esattamente «VERDETTO: VERDE» o «VERDETTO: ROSSO». git add solo per path dichiarati, mai add -A. Mai history rewrite. Mai --dangerously-skip-permissions.
6. Quando una sessione stampa VERDETTO, il founder esce senza scriverle nulla.
7. TELEMETRIA. Fa fede solo used_pct dal json della PROPRIA sessione (sonda mtime su /tmp/claude-ctx-*.json), mai la percentuale RAW dell'hook, che sovra-riporta. La protezione reale è la taglia XS/S, non la soglia.
8. CARVE-OUT PERMANENTI, mai toccare: tools/VectCutAPI, src-tauri/fluxion.db, .db-shm, .db-wal (database runtime vivo dei servizi iMac).
9. IRREVERSIBILI. :3002 si tocca solo a B3-PROMOTE con GO esplicito del founder. Nessuna chiamata live del founder nei cicli fix/test. Il telefono è hard-gate una volta per verticale alla certificazione pre-vendita. I valori dei segreti non viaggiano mai, solo i nomi delle variabili.
10. PATH VOLATILI. /tmp solo per artefatti che nascono e muoiono nello stesso mandato; prima di ogni sospensione, salvataggio su storage durevole.
