# VERDETTO D2 — ECO REGRESSION — 🔴 ROSSO-ECO (regressione, rollback eseguito)

> `-echo -15dB -injectat 9999000 (no inject) -dur 16`, UAC loopback (trunk non toccato).
> Fix sotto test: `voip_goengine.py` md5 `6c8c04c6…` (poi ROLLBACK a `caa813a4…`).

## D2 FALLITO — l'eco -15dB triggera barge E viene trascritto

### Falsi barge sull'eco (2 nel window)
```
18:44:00 BARGE-IN: rms=964 thr=500 floor=59  (pre=17 frame)
18:44:08 BARGE-IN: rms=868 thr=500 floor=137 (pre=17 frame)
```
### STT trascrive l'eco (intent spurio)
```
18:44:02 POST groq/audio/transcriptions 200 OK
18:44:03 [NLU-LLM] intent=CORTESIA conf=1.00 input='Salute!'   ← frammento greeting di Sara
```
### Marker: il floor NON riesce a tracciare i picchi d'eco (root-cause)
```
18:44:05 SPEAKING rms=577 floor=155 thr=500 sustain=9   ← eco>thr → NON folded (regola b) → sustain sale
18:44:06 SPEAKING rms=385 floor=298 thr=746 sustain=0
18:44:08 SPEAKING rms=762 floor=137 thr=500 sustain=5   ← altro picco → falso barge
```

## ROOT-CAUSE (tensione di design, non bug di implementazione)
- I picchi dell'eco -15dB (rms 577→964) superano la soglia BASE `BARGE_IN_MARGIN=500`.
- La regola (b) del fix — «fuori warm-up aggiorna `_echo_floor` SOLO se `rms<=thr`» — impedisce al
  floor di tracciare proprio quei picchi (rms>thr ⇒ non folded) → floor resta ~137 → thr resta base
  500 → l'eco sostenuto >500 accumula SUSTAIN → falso barge + STT dell'eco.
- Il warm-up ~180ms (2.1a) non copre: l'eco è CONTINUO per tutta la greeting, non solo nei primi 180ms;
  ogni nuova utterance rientra in SPEAKING ma i picchi post-warm-up non alzano il floor.
- Il vecchio codice (update floor INCONDIZIONATO) tracciava l'eco fino a ~600-900 → thr=2.5·floor>eco
  → robusto all'eco, MA assorbiva anche il beep reale (floor 0→6663 in 4 frame) → bug b2 (nessun barge).

## TENSIONE IRRISOLTA (per il giudice)
Un solo discriminante `rms>thr` NON separa «picco d'eco della propria voce» (da assorbire nel floor)
da «barge reale del chiamante» (da NON assorbire). Servono più assi discriminanti, es.:
- correlazione RX↔TX (l'eco è una copia ritardata/attenuata del TX di Sara; il barge no) → cancellazione
  d'eco / NLMS, o gating RX su similarità col TX recente;
- soglia adattiva a due livelli: floor traccia SEMPRE l'inviluppo dell'eco atteso da `_current_tx_rms`
  (l'eco ∝ energia TX × attenuazione linea), e il barge = rms sopra `k·max(floor, α·tx_rms_atteso)`;
- il beep di b1/b2 (rms 13943) è ~15× i picchi d'eco (577-964): una soglia assoluta molto più alta
  (es. BARGE_IN_MARGIN ≈ 2000-3000) distinguerebbe questo caso di test, ma NON è robusta a un
  chiamante reale che parla piano (falso-negativo barge) → decisione di design, non da chiudere a caldo.

## ARTEFATTI
- `call_20260711-184359_SARA-SIDE.wav` (rx_rms=325 eco / tx_rms=3425), `rx/tx/mix.wav` harness,
  `harness_timeline.md`, `sara3003_window.log`.

## AZIONE (per mandato FASE 4 ROSSO-ECO)
ROLLBACK `voip_goengine.py` da backup #1d (`caa813a4fb0861a79e5fcd07413063a5`) su repo MacBook E
runtime iMac → STOP → tavolo (giudice/founder). Il default produzione 3002/pjsua2 non è mai stato
toccato. Marker RX (FASE 1) NON sopravvive al rollback (era nello stesso file); l'osservabilità resta
nei log/artefatti di questa sessione.
