<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-17 · Chiusura ordinata mandato #34v (M3-GATE-MIN — gate identità pre-conferma).
> Restore point pre-overwrite = `git show HEAD:HANDOFF.md` (file tracked).

## STATO CORRENTE

**Mandato #34v — M3-GATE-MIN (taglia S): 🔴 ROSSO strutturale in F1 (pre-rig) — PREMESSA FALSIFICATA. STOP-and-report autorizzato dal mandato. Nessun codice FSM modificato. F2 rig NON eseguito (niente da provare).**

- GATE-0 verde all'avvio: porcelain = solo `M tools/VectCutAPI` · HEAD==origin==`c54ec270`.
- Commit chiusura: `9030e263` (pushed) · **HEAD==origin/master==`9030e263`** · residuo albero = SOLO `M tools/VectCutAPI` (gitlink pointer-only, carve-out autorizzato).
- Report giudice completo: `.claude/cache/T-SARA-TURNTAKING/REPORT_GIUDICE_B3-M3-GATE-MIN_20260717.md`.

**Verifica premessa (tutte su `voice-agent/src/booking_state_machine.py`):**
- **Nome GIÀ gated** prima di CONFIRMING → `_handle_idle:1374` (`if not client_name:` → `WAITING_NAME`/`ask_name` 1379/1437-1440). t1 «Sara chiede il nome» = comportamento ATTUALE, non da aggiungere. → la diag Y6 «identity skippata» è FALSA.
- **Riepilogo CONFIRMING senza telefono** → `_format_confirm_booking:751-769` (solo nome + servizio/data/ora).
- **Telefono raccolto POST-conferma e legato a persistenza cliente (= BRAINSYNC, VIETATO)** → `PROPOSE_REGISTRATION` `:3638` → `REGISTERING_PHONE` `:3960` → `CONFIRMING_PHONE:4044` → creazione cliente.
- **Step cognome forzato** → `WAITING_NAME`→`WAITING_SURNAME` (1511/1784/1878/1998): t2 «nome» → chiede *cognome*, non *telefono*.
- **Choke-point unico** per un eventuale gate = `process_message:988`.
- **Conclusione**: «riusa stati esistenti» impossibile senza toccare persistenza (vietata) o introdurre nuovo stato (fuori mandato) + bypass cognome (terza modifica). Non è il «diff piccolo» previsto → STOP.

**FASE CHIUSURA eseguita:** runbook `RUNBOOK_B3.md` M3 aggiornato con esito VERIFICATO — **M3 resta PARZIALE-con-diagnosi, NON promosso a PIENO** (#10 verificato>verosimile). Nessun PIENO non verificato scritto.

## DISCORDANZE / CONTRADDIZIONI APERTE

1. **Mandato vs realtà — «diag Y6 identity skippata»**: FALSO, nome gated in `idle:1374`.
2. **Mandato FASE CHIUSURA «criterio M3 = PIENO»**: non certificabile senza persistenza-vietata o nuovo-stato-fuori-mandato → runbook riflette lo stato reale (PARZIALE), non il PIENO richiesto. Reality-wins (#31).
3. **Commit `9030e263` ha un 3° file non nel `git add` esplicito**: `vos-out/decisions.jsonl` (+1) aggiunto da hook pre-commit VOS. Append-only lossless (escluso #1d), benigno.
4. **Context**: hook RAW ~55% (MEMORY REGOLA #27 lo flagga gonfiato; reale stimato ~40-45%). json non letto → used_pct non misurabile con precisione.

## PROSSIMA DIRETTIVA OPERATIVA

**Decisione di SCOPE al giudice/founder** (non tecnica — vincolo #3). Il nodo M3-GATE-MIN è di ordinamento/architettura, 3 opzioni (dettaglio in report §DECISIONE):
1. **Accettare l'ordine attuale** (riepilogo → poi telefono in registrazione, PRIMA della creazione booking) come M3-PARZIALE già ratificato (founder D4, `RUNBOOK_B3.md:138-140`) e chiudere M3 così.
2. **Autorizzare esplicitamente** un nuovo stato plumbing `WAITING_PHONE` (cattura→CONFIRMING, ZERO persistenza/recognition) + bypass dello step cognome nello scenario prenotazione — cioè rilassare i vincoli «solo stati esistenti / nessuna nuova feature» per questo gate.
3. **Rimandare a BRAINSYNC** (che possiede identità/persistenza) e lasciare M3 PARZIALE-con-diagnosi.

Il prossimo prompt CC dipende dalla scelta del giudice. NB: la finestra live B3 (M1..M5 via `PRECALL_CHECKLIST_B3.md`, chiamata a 0972536918) resta un binario separato pronto, indipendente da M3-GATE-MIN.
