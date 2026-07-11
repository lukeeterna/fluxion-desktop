# VERDETTO D3 — FILLER + NO-HANGUP (utterance non-goodbye) — 🟢 VERDE

> Chiamata `-injectwav /tmp/utter_8k.wav -injectat 2500 -dur 20`, UAC loopback `127.0.0.1:15090`.
> Utterance italiana non-goodbye (8k mono Int16, `say -v Alice`+afconvert):
> "Vorrei prenotare un taglio per domani pomeriggio". `SARA_TEST_CAPTURE=1` entrambi i lati.
> Fix md5 `c1fac303…`. Call answer 19:47:22.8.

## D3 — 🟢 filler ZERO sul gap + nessun hangup di Sara

### (1) BARGE-IN + STT/NLU corretti
```
19:47:25 BARGE-IN: rms=7884 thr=1830 floor=6644 (pre=17 frame)   ← thr=0.4·tx_ref, floor ignorato
19:47:30 [NLU-LLM] intent=PRENOTAZIONE conf=1.00 input='Vorrei prenotare un taglio per domani pomeriggio.'
```
L'utterance barga (thr TX-referenced), STT la trascrive fedele, NLU classifica PRENOTAZIONE.

### (2) FILLER ZERO nel gap fine-utterance → inizio-TTS
Derivato RMS harness (`harness_timeline.md`, rx_rms = TX di Sara):
```
t(s)  rx_rms  injecting
 3.0   3022   true    ← utterance in corso
 4.0      0   true    ← Sara muta (barge → clear_tx)
 5.0      0   true
 6.0      0   false   ← GAP: processing STT→NLU→TTS
 7.0      0   false   ← SILENZIO (nessun filler sul path Go)
 8.0      0   false
 9.0   2295   false   ← TTS risposta parte (19:47:30 'Capisco. Abbiamo Taglio uomo...')
10-14  1640..2350     ← risposta prosegue
15-19     0           ← risposta finita, Sara in ascolto
```
Il gap t=6–8s è a rms 0 = silenzio: nessuna frase filler iniettata (path Go: filler ZERO come atteso).
L'unico log filler è `[B1] Filler pre-synthesis done` della chiamata D1 (pre-sintesi = preparazione,
NON riproduzione); in questa finestra nessun filler PLAYED.

### (3) NO-HANGUP: nessun BYE di Sara prima di -dur
Nessuna riga BYE/HANGUP da Sara in 19:47:22–42. La chiamata termina a 19:47:42 per
`UAC durata max — hangup` (harness -dur 20), NON per congedo di Sara. Su utterance non-goodbye
Sara resta in linea e continua il flusso prenotazione. ✓

## D5 — Cattura ADDENDUM W (REGOLA #32)
- **Lato-Sara**: `call_20260711-194722_SARA-SIDE.wav`.
- **Lato-harness**: `rx.wav` / `tx.wav` / `mix.wav` + `harness_timeline.md`.
- `sara3003_window.log`: finestra adapter (BARGE-IN + NLU + TTS queue).

## ESITO
FILLER 🟢 (gap silenzioso, zero filler Go-path) + NO-HANGUP 🟢 (nessun BYE su non-goodbye).
