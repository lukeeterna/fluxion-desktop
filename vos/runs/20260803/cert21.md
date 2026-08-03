# CERT-21 — Referto evidenza e giudizio
**Data**: 2026-08-03 | **Unità**: T-CERT-RACCOLTA/#48 | **Corsia**: MACCHINA  
**Base commit**: 989c8c6 | **vos_check.sh**: 7/8 (FAIL check e — NEXT_SESSION_PROMPT.md presente; check g PASS)

---

## GATE-0

- HEAD atteso 989c8c6: **PASS** (`git log --oneline -1` = `989c8c62`)
- Modifiche non committate: `src-tauri/fluxion.db*` (db runtime), `tools/VectCutAPI` (submodule), `vos-out/decisions.jsonl` — tutte ammissibili dal carve-out
- `vos_check.sh`: 7/8 PASS. **FAIL check (e)**: `NEXT_SESSION_PROMPT.md` presente nel repo. Il check (g) (runtime iMac HEAD == origin/master) è PASS. Poiché il fail riguarda check (e) e non (g), l'evidenza è valida e si procede; la discordanza è dichiarata qui.

---

## F1 — L'EVIDENZA ESISTE

**File WAV identificato**:
- Nome: `call_20260803-162144.wav`
- Path iMac: `/Volumes/MacSSD - Dati/fluxion/.claude/cache/T-SARA-TURNTAKING/calls/`
- Dimensione: 3.632.044 bytes (3,46 MB)
- Durata: 113,5 secondi (≈ 1 min 54 sec) — calcolato via `wave.getnframes()/rate` (frames=908.000, rate=8000 Hz)
- Formato: PCM 16-bit, stereo, 8000 Hz
- Ora di creazione: 3 Ago 16:23 (iMac)
- Conferma da log (riga 76848): `capture WAV-giudice scritto: ... call_20260803-162144.wav (rx_rms=1440 tx_rms=2827 bytes_stereo=3632000)`

**Il WAV è < 5 MB: copiato in `vos/runs/20260803/call_20260803-162144.wav`.**

---

## F2 — TRASCRIZIONE TURNO PER TURNO

Fonte: `/tmp/sara_3002.log` su iMac, righe 76367–76848.

| Ora | Chi | STT / NLU input | Risposta Sara (VERBATIM) |
|-----|-----|-----------------|--------------------------|
| 16:21:44 | — | CALL_START caller=79.98.45.133:5060 | — |
| 16:21:47 | SARA | — | "Salone Demo FLUXION, buon pomeriggio! Sono Sara, l'assistente virtuale. Come posso aiutarla?" |
| 16:21:57–16:22:18 | FOUNDER | *silenzio* (22s LISTENING, rms=8) | — |
| 16:22:18 | SARA | IDLE 22s → reprompt | "Pronto, è ancora in linea?" |
| 16:22:25 | FOUNDER | `. Gianluca.` (ALTRO, conf=1.00) | (nessuna risposta diretta — raccolta nome, dispatch silenzioso) |
| 16:22:33 | FOUNDER | `Gianluca` (ALTRO, conf=1.00, state=WAITING_NAME) | "Capisco. Ok. Piacere Gianluca. E di cognome?" |
| 16:22:49–16:22:52 | FOUNDER | `ebbiNNsgLlZlZgLlA` (Low confidence/regex fallback, acoustic_frustration=0.70, state=WAITING_SURNAME) | "Ha ragione. Non la trovo tra i nostri clienti, Gianluca. Mi dà un numero di telefono per registrarla?" |
| 16:23:01 | FOUNDER | BARGE-IN | *(Sara interrotta)* |
| 16:23:05 | FOUNDER | `wvgBWrFbNUJbKvgvGjNVVNgIbNWMXvbNVVpNWMgMgWmgVkVgNnWMgBvgNVvNWMgVNVNmGVNWMgVgNVNb` (Low confidence/regex, acoustic_frustration=0.66, state=REGISTERING_PHONE — **STRIKE 1**) | "Mi dispiace. Mi ripete il numero di telefono, per cortesia?" |
| 16:23:08 | FOUNDER | BARGE-IN | *(Sara interrotta)* |
| 16:23:13 | FOUNDER | `IORRIOIOWIOWAWOWAWA ALLA ALLA ALLA ALLA AKRAA AH HA HA` (OSCENITA conf=0.80, acoustic_frustration=0.70, state=REGISTERING_PHONE — **STRIKE 2**) | "Comprendo. Mi ripete il numero di telefono, per cortesia?" |
| 16:23:22 | FOUNDER | BARGE-IN | *(Sara interrotta)* |
| 16:23:25 | FOUNDER | `AIAAAARGHH, IATGUGAUA` (OSCENITA conf=0.80, acoustic_frustration=0.73, state=REGISTERING_PHONE — **STRIKE 3 → E6**) | "Mi scusi, sto avendo difficoltà a comprenderla. La faremo richiamare dal salone al più presto. Arrivederci!" |
| 16:23:38 | SARA | HANGUP ricevuto da Python → CALL_END | *(chiamata chiusa da Sara/Python)* |

---

## F3 — I QUATTRO CRITERI

### a) REPROMPT dopo silenzio prolungato
**PROVA LOG** (riga 76485):
```
16:22:18 [voip_goengine] INFO: IDLE: 22s di silenzio chiamante → reprompt
```
Il saluto Sara è andato in coda TX a 16:21:47. L'ascolto silenzioso (rms=8) va da 16:21:57 a 16:22:18 = 21s di silenzio post-greeting. Dal call start (16:21:44) al reprompt: **~34 secondi**. Il fondatore riferisce "circa 25 secondi" — compatibile con il tempo soggettivo escludendo il saluto iniziale.
Reprompt pronunciato: **"Pronto, è ancora in linea?"**

**RISPOSTA: SI**

---

### b) I tre farfugliamenti hanno prodotto strike 1, 2 e 3 distinti e progressivi?
**PROVA LOG** (righe 76508, 76752, 76796 → dispatch; 76606, 76728, 76804 → NLU; 76733, 76768, 76812 → turno loggato):
- Strike 1 (16:23:05–16:23:08): `wvgBWrFbNUJb...` Low confidence → "Mi dispiace. Mi ripete il numero di telefono?"
- Strike 2 (16:23:13–16:23:17): `IORRIOIOWIOWAWOWAWA...` OSCENITA → "Comprendo. Mi ripete il numero di telefono?"
- Strike 3 (16:23:25–16:23:28): `AIAAAARGHH, IATGUGAUA` OSCENITA → E6 trigger

I tre sono NLU dispatch separati, ciascuno con STT indipendente, risposta progressivamente diversa (dispiace → comprendo → E6). Il contatore interno raggiunge 3 e scatta E6.

**NOTA**: il log non emette etichette esplicite `STRIKE 1 / STRIKE 2 / STRIKE 3` ma le tre invocazioni distinte + il trigger E6 su conteggio=3 dimostrano la progressione.

**RISPOSTA: SI**

---

### c) Al terzo strike è scattata l'escalation E6?
**PROVA LOG** (riga 76806):
```
16:23:28 [src.booking_state_machine] INFO: [E6] 3-strike escalation triggered in registering_phone
```
Immediato a follow del terzo NLU OSCENITA.

**RISPOSTA: SI**

---

### d) Il congedo contiene «richiamar» e NON «collega»?
**PROVA LOG** (riga 76809):
```
16:23:28 [src.tts_engine] INFO: [EdgeTTSEngine] TTS done: ... text='Mi scusi, sto avendo difficoltà a comprenderla. La faremo richiamare dal salone al più presto. Arrivederci!'
```
- Contiene "**richiamare**" ✓ (radice «richiamar» presente)
- NON contiene "collega" ✓ (assente nel testo)

**RISPOSTA: SI**

---

### e) La chiusura è stata avviata da Sara, non dal chiamante?
**PROVA LOG** (righe 76844–76846):
```
16:23:38 time=... msg="HANGUP ricevuto da Python"
16:23:38 time=... msg="CALL_END emesso"
16:23:38 [voip_goengine] INFO: CALL_END
```
Il HANGUP è "ricevuto da Python" (cioè Python ha chiuso il canale SIP), non inviato dal chiamante. Il founder non ha riagganciato (copione: "nessun riaggancio da parte del founder"). Sara ha pronunciato "Arrivederci!" e poi la pipeline Python ha terminato la chiamata.

**RISPOSTA: SI**

---

## TABELLA RIASSUNTIVA CRITERI

| Criterio | Risposta | Riga di prova |
|----------|----------|---------------|
| a) REPROMPT dopo silenzio | **SI** | `76485: IDLE: 22s di silenzio chiamante → reprompt` (sec ~34 dal call start) |
| b) 3 strike distinti e progressivi | **SI** | Righe 76508/76752/76796 dispatch + 76606/76728/76804 NLU + 76733/76768/76812 turno |
| c) E6 al terzo strike | **SI** | `76806: [E6] 3-strike escalation triggered in registering_phone` |
| d) «richiamar» presente, «collega» assente | **SI** | `76809: 'La faremo richiamare dal salone...'` |
| e) Chiusura avviata da Sara | **SI** | `76844: HANGUP ricevuto da Python` |

---

## F4 — QUALITÀ DELLA LINEA

**WAV**: 113,5s, stereo 8kHz PCM, rx_rms=1440 tx_rms=2827. Nessuna interruzione nel log (CALL_END lineare). Il founder ha eseguito 3 BARGE-IN (16:23:01, 16:23:08, 16:23:22), tutti correttamente rilevati dal VAD.

**Latenze fine-utterance → audio-out per turno** (da log `[TARATURA] latenza fine-utterance→audio-out`):

| Turno | Ora | Input rilevato | Latenza |
|-------|-----|----------------|---------|
| T1 | 16:22:25–16:22:27 | `. Gianluca.` (ALTRO) | 1483 ms |
| T2 | 16:22:33–16:22:36 | `Gianluca` (ALTRO) | 2882 ms |
| T3 | 16:22:52–16:22:55 | farfuglio cognome | 2652 ms |
| T4 | 16:23:05–16:23:08 | STRIKE 1 (Low conf) | 3317 ms |
| T5 | 16:23:13–16:23:17 | STRIKE 2 (OSCENITA) | 3333 ms |
| T6 | 16:23:25–16:23:29 | STRIKE 3 (OSCENITA → E6) | 3255 ms |

**Target dichiarato**: <800ms (voice-agent-details.md). Tutti i turni sono ampiamente sopra target. Il T1 (1483ms) è il migliore; T4-T6 intorno a 3300ms probabilmente per TTS Edge-TTS (TTFB ~400-600ms + download 500-1800ms + NLU 200-500ms).

Nessun frame drop o silenzio anomalo nel canale RTP (rtp_silence cresce linearmente, nessun buco).

---

## F5 — COMPORTAMENTI INATTESI

1. **Latenze tutte > 800ms**: nessun turno rispetta il target <800ms documentato. T4-T6 superano 3s. Il fondatore percepisce lunghe pause (coerente col copione).
2. **Farfuglio cognome trattato come tentativo valido**: il farfuglio su WAITING_SURNAME (`ebbiNNsgLlZlZgLlA`) non ha generato uno strike — è stato processato come cognome non trovato nel DB e ha fatto avanzare la FSM a `new_client_phone`. Questo è comportamento corretto della FSM ma significa che il conteggio "tre farfugliamenti" del copione include in realtà: 1 cognome farfugliato (state-advance) + 3 farfugliamenti in `registering_phone` (strikes). Totale input non leggibili: 4 (non 3). Nessun impatto sul verdetto.
3. **Sara risponde "Comprendo"** al secondo farfuglio OSCENITA. La risposta è formalmente corretta (cortesia + retry), ma semanticamente strana a fronte di urla/suoni gutturali (`IORRIOIOWIOWAWOWAWA ALLA ALLA...`). Non pregiudica il criterio.
4. **acoustic_frustration rilevata ma non escalata autonomamente**: il modulo `acoustic_frustration` ha segnalato score 0.66/0.70/0.73 ma non ha triggerato un percorso separato — il conteggio strike FSM ha guidato la logica. Comportamento atteso e corretto.
5. **`NEXT_SESSION_PROMPT.md` presente** (check vos_check.sh e): non impatta la chiamata ma causa FAIL 7/8. Da rimuovere nella prossima sessione.

---

CERT-21: SUPERATA
