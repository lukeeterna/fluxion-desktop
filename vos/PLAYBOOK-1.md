# PLAYBOOK-1 — T-AUTORUN v1 (#34v)

> Catena headless: FIX-OBS → FIX-A → FIX-C → SUITE.
> Ogni STEP è un processo CC headless FRESCO. Il runner `vos/autorun.sh` legge questo file.
> STOP-ON-RED: uno step ROSSO o >30 min ferma la catena.

## REGOLE COMUNI A OGNI STEP (il runner le antepone al prompt di ogni step)

```
- porcelain carve-out: l'unico residuo tollerato non-tuo è "M tools/VectCutAPI". NON toccarlo.
- add SOLO i path esplicitamente dichiarati da questo step. MAI git add -A.
- niente telefono / niente trunk EHIWEB / niente chiamate reali.
- niente deploy o riavvii su :3002 di produzione. Rig high-port only.
- MAI toccare tools/VectCutAPI, .claude/SARA_STRESS_TEST_PATTERNS.md, cache calls/ in scrittura.
- MAI --dangerously-skip-permissions o equivalenti totali.
- MAI history rewrite / filter-repo.
- SEGRETI: solo nomi, mai valori.
- report dello step con PROVE (righe di log reali) e "ND" dove il log non arriva. MAI stime.
- niente cat integrali di file grandi.
- chiudi SEMPRE il tuo output con la riga (come ULTIMA riga) "VERDETTO: VERDE" oppure
  "VERDETTO: ROSSO <motivo>". Il runner decide leggendo l'ultima riga "VERDETTO:"; se manca
  o supera 30 min, lo step e' ROSSO e la catena si ferma (stop-on-red).
```

---

## STEP 1 — FIX-OBS

**PATH consentiti (add):** `voice-agent/src/voip_goengine.py`, `voice-agent/src/tts_engine.py`, `voice-agent/src/` (solo logger/observability), `vos/runs/<data>/1-FIX-OBS/`

Capitolato:
- (a) **capture WAV**: perché `SARA_TEST_CAPTURE=1` (`b3_open.sh:60`) non produce `.wav` — TRAPPOLA nota: la env va esportata al harness E al processo Sara. Verifica la propagazione env nel launcher e con `ps eww` sull'avvio di prova; fix minimale + PROVA su rig (`launch_rig.sh`, una inject → rx/tx/mix scritti).
- (b) **logger**: TTS≥160ch · timestamp fine-utterance · slot-result NLU per turno · al boot log di reprompt-timer/VAD/soglia E6 con `file:riga`.
- (c) **disclosure STATICA**: template greeting «buonasera! Sono Sar…» integrale + verdetto «assistente virtuale sì/no» + `file:riga` (nessuna modifica al testo).

**VERDE =** WAV provato su rig + esempi nuove righe log + verdetto disclosure.

---

## STEP 2 — FIX-A E6-EXIT

**PATH consentiti (add):** `voice-agent/src/booking_state_machine.py`, `voice-agent/src/` (FSM-guard/reply), `vos/runs/<data>/2-FIX-A/`

Capitolato:
- La FSM-guard deve permettere l'HANGUP quando `should_exit` ha origine escalation E6.
- Sostituire «La passo subito a un collega» con congedo onesto configurabile (es. «Mi scusi, sto avendo difficoltà: la faremo richiamare dal salone. Arrivederci!»).
- Eliminare il doppio prefisso empatico (mai due prefissi concatenati).
- PROVA su rig: 3 inject garbage → E6 → messaggio onesto → BYE ≤2s da fine TTS.

**VERDE =** BYE su escalation provato + zero doppi prefissi nel log di prova.

---

## STEP 3 — FIX-C NAME-GATE

**PATH consentiti (add):** `voice-agent/src/booking_state_machine.py`, `voice-agent/src/` (name-gate/NLU-slot), `vos/runs/<data>/3-FIX-C/`

Capitolato:
- Un bare-name catturato in IDLE non diventa MAI `client_name` senza conferma esplicita («La registro come X, corretto?»); su diniego → `ask_name`.
- PROVA su rig: inject «Buonasera» come primo turno → NON registrato come nome; inject «Marco Rossi» → conferma → registrato.

**VERDE =** entrambe le prove a log.

---

## STEP 4 — SUITE v1

**PATH consentiti (add):** `voice-agent/tools/suite/`, `vos/runs/<data>/4-SUITE/`

Capitolato:
- Runner di scenari in `voice-agent/tools/suite/` che concatena su rig high-port: smoke · congedo (X2) · name-gate («Buonasera») · escalation E6 (3 garbage) · silenzio→reprompt · barge-in · dettatura numero (inject cifre pulite).
- Riusa il catalogo `SARA_STRESS_TEST_PATTERNS.md` e i 13 scenari archiviati come riferimento (READ-ONLY).
- Output: `suite_report.md` con PASS/FAIL per scenario + estratti log.
- WAV: gli scenari scrivono i `.wav` volatili in `vos/runs/<data>/4-SUITE/audio/` (gitignorata,
  restano locali). Committa SOLO **un** wav campione della run in STEPDIR root (es. `sample.wav`)
  + i report testuali. I WAV delle chiamate reali in `calls/` restano tracciati come da convenzione.

**VERDE =** suite eseguita end-to-end; i FAIL veri restano FAIL dichiarati.
