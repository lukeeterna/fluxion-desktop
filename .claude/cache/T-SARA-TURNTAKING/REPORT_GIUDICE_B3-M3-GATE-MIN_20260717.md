# REPORT GIUDICE — MANDATO #34v M3-GATE-MIN — PREMESSA FALSIFICATA (STOP pre-implementazione)

Data: 2026-07-17 · Conversazione CC nuova · Taglia S · Nessun codice FSM modificato (verifica-premessa richiesta dal mandato stesso: «PREMESSE CIECHE (verificale)»).

## GATE-0 (verde)
- `git status --porcelain` = solo `M tools/VectCutAPI` (residuo ammesso).
- HEAD == origin/master == `c54ec270874f8d8c2d965ad29be03b50becf4b89`.

## VERDETTO
**ROSSO strutturale in F1 (pre-rig): la premessa del mandato è falsificata dal codice.** Il gate «riusa gli stati ESISTENTI ask_name/ask_phone, raccogli, POI CONFIRMING» NON è implementabile entro i vincoli del mandato stesso (solo-stati-esistenti + niente persistenza/recognition BRAINSYNC + nessuna nuova feature). Nessun fix speculativo shippato su file FSM critico (`booking_state_machine.py`, 216KB, sotto lavoro BRAINSYNC attivo).

## PROVE (file:riga)
Tutte in `voice-agent/src/booking_state_machine.py`.

1. **NOME già gated prima di CONFIRMING (t1 già verde senza modifiche).**
   `_handle_idle` riga **1374**: `if not self.context.client_name:` → `self.context.state = BookingState.WAITING_NAME` + `response=TEMPLATES["ask_name"]` (righe 1379, 1437-1440). Booking multi-slot senza nome (>3 parole → non bare-name, riga 1423-1426) ricade qui. → «Sara chiede il nome» è comportamento ATTUALE, non da aggiungere.

2. **Il riepilogo CONFIRMING NON contiene il telefono.**
   `_format_confirm_booking` righe **751-769**: usa solo `client_name` + `get_summary()` (servizio/data/ora). Nessun `client_phone` nella conferma.

3. **Il telefono è raccolto DOPO la conferma ed è legato alla creazione/persistenza cliente (BRAINSYNC, VIETATO dal mandato).**
   L'unico percorso di cattura telefono esistente è il sotto-flusso registrazione nuovo cliente:
   `PROPOSE_REGISTRATION` (`_handle_propose_registration` **3638**) → `REGISTERING_SURNAME`/`REGISTERING_PHONE` → `_handle_registering_phone` (**3960**) che a riga **4044** passa a `CONFIRMING_PHONE` → conferma numero → creazione cliente. Riusare `REGISTERING_PHONE` dal gate trascina dentro creazione/persistenza cliente = territorio recognition/persistence esplicitamente FUORI SCOPE.

4. **La raccolta nome forza uno step COGNOME prima di qualunque telefono.**
   `WAITING_NAME` → `WAITING_SURNAME` (righe 1511, 1784, 1878, 1998). Quindi t2 «solo nome» produce *chiedi cognome*, NON *chiedi telefono*: scarto rispetto allo scenario scriptato t2→telefono.

5. **Nessuno stato esistente fa «cattura telefono → torna a CONFIRMING (riepilogo)».**
   `CONFIRMING_PHONE` (`_handle_confirming_phone` **4110**) conferma un numero già catturato e prosegue verso il completamento, non verso il riepilogo. Choke-point unico verificato per un eventuale gate: `process_message` riga **988** (`return self._track_strikes(result, _state_before)`), dove convergono tutti i risultati handler.

## PERCHÉ NON HO IMPLEMENTATO (root-cause, non episodio)
Le due strade per un gate «fedele» sono entrambe bloccate dai vincoli del mandato:
- (A) Riuso `REGISTERING_PHONE` → tocca creazione/persistenza cliente = **BRAINSYNC VIETATO**.
- (B) Nuovo stato `WAITING_PHONE` capture→CONFIRMING → **«nuova feature» / non «stati esistenti»**, e comunque NON risolve lo scarto t2 (step cognome) senza una terza modifica comportamentale (bypass cognome).
Un gate al choke `:988` che instrada name/phone mancanti verso stati esistenti è quindi o non-conforme (persistenza) o non-minimale (nuovo stato + bypass cognome). Non è il «diff piccolo» previsto: il mandato prescrive «se ti scappa di mano, STOP e report». Vincoli applicati: #1 (verifica premessa), #1c (escala, no 3° ciclo), #9 (dissenso con dati), #11 (root-cause), #31 (output CC = specchio del filesystem, vince la realtà).

## DISCORDANZE CON IL MANDATO
- Mandato: «diag Y6 = identity è ramo condizionale … skip su prenotazione+data+servizio in un turno». **Falso**: il nome è gated in IDLE:1374; t1 chiede il nome oggi.
- Mandato FASE CHIUSURA: «criterio M3 = PIENO». **Non certificabile**: PIENO richiederebbe telefono-prima-del-riepilogo, non ottenibile senza (A persistenza vietata) o (B nuova feature + bypass cognome). Runbook aggiornato con lo stato VERIFICATO, non con un PIENO non verificato (#10 verificato>verosimile).

## DECISIONE PER IL GIUDICE (scelta di scope, non tecnica)
Il vero nodo è di ordinamento/architettura, da decidere fuori dal codice protetto:
1. **Accettare l'ordine attuale** (riepilogo → poi telefono in registrazione, PRIMA della creazione booking) come M3-PARZIALE già ratificato (founder D4, runbook righe 138-140) e chiudere M3 così; oppure
2. **Autorizzare esplicitamente** UN nuovo stato plumbing `WAITING_PHONE` (cattura→CONFIRMING, ZERO persistenza/recognition) + il bypass dello step cognome nello scenario prenotazione — cioè rilassare i vincoli «solo stati esistenti / nessuna nuova feature» per questo gate; oppure
3. Rimandare interamente a BRAINSYNC (che possiede identità/persistenza) e lasciare M3 come PARZIALE-con-diagnosi.

Nessuna delle tre è decidibile staticamente da CC senza input founder/giudice (vincolo #3: scope decisions al founder; #1b: fatto terminale esterno).

## CONTEXT
used_pct: vedi C4 nella risposta chat (hook RAW ~52% flaggato gonfiato da MEMORY REGOLA #27; reale stimato ~40-45% post-boot ~18-22%).
