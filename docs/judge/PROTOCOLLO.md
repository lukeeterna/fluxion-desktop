# PROTOCOLLO — Invarianti del sistema giudice

1. RUOLI. Sol scrive il codice leggendo il repo a un commit PINNATO, non tocca mai git. CC esegue tutto il lavoro macchina. Il founder ha due soli atti: sigillo estetico e GO sulle azioni che escono dal repo. Il giudice legge in sola lettura, emette blocchi, non giudica le unità conformi.
2. VIETATO che lo stesso modello scriva un artefatto e lo giudichi.
3. Un solo blocco attivo alla volta, cross-venture. Ogni blocco = una sessione CC NUOVA, una consegna. Ogni blocco inizia con la riga MODELLO:.
4. FONTE DI VERITÀ = docs/judge/STATE.md. Gli handoff in prosa sono aboliti. Fa fede il diff, mai il messaggio di commit. Una dichiarazione di assenza vale quanto la copertura dello strumento che l'ha prodotta.
5. CHIUSURA. Ogni unità che scrive ha una FASE CHIUSURA anche su rosso. Ultima riga esattamente «VERDETTO: VERDE» o «VERDETTO: ROSSO». git add solo per path dichiarati, mai add -A. Mai history rewrite. Mai --dangerously-skip-permissions.
6. Quando una sessione stampa VERDETTO, il founder esce senza scriverle nulla.
7. TELEMETRIA. Fa fede solo used_pct dal json della PROPRIA sessione (sonda mtime su /tmp/claude-ctx-*.json), mai la percentuale RAW dell'hook, che sovra-riporta. La protezione reale è la taglia XS/S, non la soglia.
8. CARVE-OUT PERMANENTI, mai toccare: tools/VectCutAPI, src-tauri/fluxion.db, .db-shm, .db-wal (database runtime vivo dei servizi iMac), vos-out/decisions.jsonl (scritto dall'hook VOS, append-only).
9. IRREVERSIBILI. :3002 si tocca solo a B3-PROMOTE con GO esplicito del founder. Nessuna chiamata live del founder nei cicli fix/test. Il telefono è hard-gate una volta per verticale alla certificazione pre-vendita. I valori dei segreti non viaggiano mai, solo i nomi delle variabili.
10. PATH VOLATILI. /tmp solo per artefatti che nascono e muoiono nello stesso mandato; prima di ogni sospensione, salvataggio su storage durevole.

## Memoria del giudice

I quattro file di memoria del giudice e i loro proprietari:
- `docs/judge/LEDGER.md` — proprietario CC (scrive la riga di chiusura ad ogni unità), append-only, mai riscrivere
- `docs/judge/FALSIFICATO.md` — proprietario CC (scrive la voce quando la falsificazione è provata), append-only, mai riscrivere
- `docs/judge/STATE.md §FATTI` — proprietario CC (aggiorna HEAD, stato :3002, esiti misurati, file prodotti)
- `docs/judge/STATE.md §DIRETTIVA` e `§CODA IMPIANTO` — proprietario GIUDICE, CC non scrive mai in queste sezioni
- `docs/judge/BOOT-GIUDICE.md` — prompt fisso per riavviare il giudice senza stato in prosa

Obbligo per ogni FASE CHIUSURA: appendere la riga di LEDGER prima del VERDETTO finale.

Gli handoff del giudice in prosa sono aboliti: lo stato vive nei quattro file sopra.

### Regole permanenti nate da T-JUDGE-STATE/#35

11. ANTI-STANTIO. Ogni unità che misura il runtime confronta PRIMA l'ora di avvio del processo con l'ora dell'ultimo pull. Nessuna misura presa su processo stantio è valida. Evidenza: T-BOOKING-PROVE (ROSSO per processo 31/07 ante-fix Sol) vs T-BOOKING-DIAG2 (VERDE dopo riavvio).
12. NO STAGING DIRECTORY. Nessun agente o script stagia una directory con pattern glob (cp -r, git add -A, rsync --delete, ecc.): solo path dichiarati uno per uno, espliciti.
13. SOL RICEVE SOLO SORGENTE. Al codificatore esterno (Sol) si incolla solo codice sorgente. Mai file di configurazione, mai .env, mai secret — solo i nomi delle variabili, non i valori.
14. CODA IMPIANTO. Nessuna corsia resta ferma se la coda impianto in STATE.md §CODA IMPIANTO non è vuota. Quando una corsia resta senza blocco attivo, si prende la prima voce compatibile con quella corsia, senza attendere il giudice.

### Portabilità

Questa sezione «Memoria del giudice» è PORTABILE alle altre venture del VOS (ARGOS, Guardian). Ogni venture mantiene il proprio set di quattro file sotto `docs/judge/` con la stessa struttura e le stesse regole.
