# FALSIFICATO — Ipotesi confutate FLUXION

**REGOLA**: questo file si APPENDE, non si riscrive mai.
Ogni voce: enunciato ipotizzato → come è stata falsificata → dove sta l'evidenza.
LEDGER.md riporta l'unità in cui è avvenuta la falsificazione.

---

## F-01 — Path HTTP raggiunge E6 e reprompt_timer

**Ipotesi**: il path `/api/voice/process` è sufficiente per testare reprompt su silenzio e tre strike E6.

**Come falsificata**: reprompt_timer (22.0s) e E6_strike_threshold (3) vivono in `voip_goengine.py:87` sulla gamba SIP, non nel path HTTP. L'endpoint HTTP non arma mai il timer e non conta gli strike.

**Evidenza**: `voip_goengine.py:87`, `ROADMAP-PRODUZIONE.md §Infrastruttura verificata`, referto `vos/runs/20260730/b3_promote_r2.md`.

---

## F-02 — VAD è una soglia RMS

**Ipotesi**: il VAD di Sara usa una soglia di energia (RMS) per distinguere parlato da silenzio, quindi rumore bianco e silenzio PCM sono trattati allo stesso modo.

**Come falsificata**: il VAD è Silero, classificatore neurale di frame audio. Rumore bianco e silenzio PCM sono entrambi scartati come non-parlato dalla rete neurale, indipendentemente dall'energia del segnale.

**Evidenza**: `ROADMAP-PRODUZIONE.md §GIÀ FALSIFICATO voce 2`, configurazione `voice-agent/src/voip_goengine.py` (import silero).

---

## F-03 — pjsua2 direct-INVITE è percorribile

**Ipotesi**: è possibile testare Sara via INVITE SIP diretto a pjsua2 senza trunk.

**Come falsificata**: il parser SDP della go engine accetta una sola `m=audio`; pjsua2 ne offre due per configurazione di default del media. L'INVITE diretto produce SDP incompatibile.

**Evidenza**: `ROADMAP-PRODUZIONE.md §GIÀ FALSIFICATO voce 3`, test S244 (trunk EHIWEB): anche con trunk reale, la race clock-thread pjsua2 (`lock.c:279`) era presente → path pjsua2 abbandonato definitivamente.

---

## F-04 — Esistono script INVITE SIP sotto .claude/cache/T-SARA-TURNTAKING/

**Ipotesi**: la directory `.claude/cache/T-SARA-TURNTAKING/` contiene script per testare turntaking via SIP/INVITE.

**Come falsificata**: verifica diretta della directory — tutti gli scenari archiviati usano il path HTTP, nessun script INVITE.

**Evidenza**: `ROADMAP-PRODUZIONE.md §GIÀ FALSIFICATO voce 4`, ls `.claude/cache/T-SARA-TURNTAKING/`.

---

## F-05 — Il fronte rig SIP è chiuso con ripiego su U2

**Ipotesi**: il rig SIP (turntaking via chiamata vocale) è stato completato o accantonato definitivamente, con U2 come alternativa sufficiente.

**Come falsificata**: U2 CERT-21 è gated su FOUNDER (chiamata vocale fisica, una per verticale), non sostituisce il rig SIP automatico. Il fronte rig SIP è aperto come gap noto: nessun harness audio automatico esiste per SIP. U2 e rig SIP sono due gate distinti.

**Evidenza**: `ROADMAP-PRODUZIONE.md §Unità residue U2`, note `.claude/cache/T-SARA-TURNTAKING/`, MEMORY.md REGOLA #23 (CTO guida il test vocale via TTS, non chiama il founder).

---

## F-06 — Il guard skip_for_booking a orchestrator.py:1527 NON esiste o non funziona

**Ipotesi** (implicita in T-BOOKING-DIAG e T-BOOKING-PROVE): il fix Sol (1e6c628f) non aveva introdotto un guard funzionante per SPOSTAMENTO/CANCELLAZIONE in booking context.

**Come falsificata**: dopo riavvio del processo con il codice aggiornato (T-BOOKING-DIAG2, 1a46ede), input data in stato `waiting_date` viene gestito da L2_slot e non intercettato da L1_exact SPOSTAMENTO. Il guard `skip_for_booking` esiste e funziona. Il loop osservato in T-BOOKING-PROVE era dovuto al processo stantio (caricato il 31 luglio, ante-fix Sol).

**Evidenza**: referto `vos/runs/20260801/booking_diag2.md §F1`, commit 1a46ede, `orchestrator.py:1527` (ricerca `skip_for_booking`).

---

## F-07 — La soglia dei 60 giorni è il difetto che blocca il booking

**Ipotesi**: la risposta "Le prenotazioni sono possibili fino a 60 giorni in anticipo" indica che il limite `max_advance_days=60` è configurato troppo stretto rispetto alle date richieste dall'utente.

**Come falsificata**: Sep 8, 2026 cade a 38gg dalla data del test (2026-08-01), dentro il limite 60gg. Il confronto `if days_ahead > 60` NON scatta per quella data. Il trigger è la data corrotta `2077-09-13` prodotta dal booking FSM: 2077-09-13 − 2026-08-01 ≈ 18.669gg >> 60, perciò `availability_checker` restituisce `too_far`. Il difetto è nell'entity extractor/FSM (`booking_action.date = "2077-09-13"`), non nella soglia.

**Evidenza**: referto `vos/runs/20260801/booking_end.md §F1`, `availability_checker.py:227-228`, `availability_checker.py:64`.
