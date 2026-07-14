# RUNBOOK B3-LIVE — finestra Sara-go (eseguita dal FOUNDER)

> Questa finestra la apri **tu**, con comandi copia-incolla. CC prepara prima e
> raccoglie l'evidenza dopo. La sicurezza NON dipende dal context di CC: il
> ripristino della Sara di produzione è nelle tue mani (`b3_close.sh`, anche due volte).
>
> **Cosa succede quando la finestra è APERTA**: il numero DID **0972536918**
> risponde con la **Sara-go** (engine sperimentale + registrazione WAV) a
> **QUALUNQUE** chiamante, finché non esegui la CHIUSURA. Apri solo quando sei
> pronto a chiamare tu, chiudi appena finito.
>
> Tutti i comandi si lanciano dal terminale del **MacBook** (parlano all'iMac via `ssh imac`).
> Copia UNA riga, premi Invio, leggi l'output atteso, poi passa alla riga dopo.

---

## PRE-FLIGHT già verificato da CC (2026-07-14) — non devi fare nulla qui
- **PF2 voce (EdgeTTS)**: sintesi Isabella OK su iMac → voce **QUALITY** (nessun fallback su voce di sistema). M1 (intelligibilità) coperto lato voce.
- **PF3 credenziali SIP**: `voice-agent/.env` contiene VOIP_SIP_USER / VOIP_SIP_PASS / VOIP_SIP_SERVER (tutte presenti).
- **Capture WAV**: con `SARA_TEST_CAPTURE=1` Sara scrive i WAV in
  `/Volumes/MacSSD - Dati/fluxion/.claude/cache/T-SARA-TURNTAKING/calls/call_<data-ora>.wav` (stereo: L=tu, R=Sara).
- **Disclosure M1 (VERIFICATO a codice)**: il saluto realmente emesso è
  `session_manager.get_greeting():744` = «…Sono Sara, l'assistente virtuale. Come posso aiutarla?»
  → la disclosure **è presente** sul path standard. (Il `warm_greetings():667-668` senza disclosure è
  solo un pre-warmer cache TTS, non il saluto emesso — debito di perf, non compliance.) Eccezione nota:
  il path proattivo G5 (`orchestrator.py:890`) può usare un greeting diverso in cui la disclosure non è
  verificata. In M1 annota semplicemente se hai **sentito** la frase «assistente virtuale».

---

## SEQUENZA A — DRY-RUN (RACCOMANDATO, ~60 secondi, SENZA telefonare)
Serve a provare che apertura e chiusura funzionano, senza fare nessuna chiamata.

1. Guarda lo stato di partenza (deve essere `pjsua2`):
```
ssh imac 'bash /tmp/b3/b3_status.sh'
```
   Atteso: riga con `"engine": "pjsua2"` e `"reg_status": 200`.

2. Apri la finestra (passa a Sara-go):
```
ssh imac 'bash /tmp/b3/b3_open.sh'
```
   Atteso: righe `CHECKPOINT 1..5` e alla fine **`CHECKPOINT GO-UP`**.
   Se invece finisce con `ABORT-RESTORED`: la produzione è già stata ripristinata da sola, fermati e avvisa CC.

3. Verifica che ora giri Sara-go:
```
ssh imac 'bash /tmp/b3/b3_status.sh'
```
   Atteso: `"engine": "go"` e `"reg_status": 200`.

4. Chiudi subito (ripristina produzione):
```
ssh imac 'bash /tmp/b3/b3_close.sh'
```
   Atteso: alla fine **`CHECKPOINT RESTORED`**.

5. Conferma ritorno a produzione:
```
ssh imac 'bash /tmp/b3/b3_status.sh'
```
   Atteso: di nuovo `"engine": "pjsua2"` e `"reg_status": 200`.

Se il DRY-RUN è andato (GO-UP poi RESTORED), sei pronto per la finestra reale.

---

## SEQUENZA B — FINESTRA REALE (con la telefonata)

1. Apri la finestra:
```
ssh imac 'bash /tmp/b3/b3_open.sh'
```
   Attendi **`CHECKPOINT GO-UP`** prima di chiamare.

2. Dal tuo telefono, **chiama il numero 0972536918** ed esegui le 5 mosse (scorecard sotto).
   Una sola chiamata (massimo due). Parla come un cliente vero.

3. Riaggancia. Chiudi la finestra:
```
ssh imac 'bash /tmp/b3/b3_close.sh'
```
   Attendi **`CHECKPOINT RESTORED`**.

4. Conferma produzione ripristinata:
```
ssh imac 'bash /tmp/b3/b3_status.sh'
```
   Atteso: `"engine": "pjsua2"` + `"reg_status": 200`.

Il WAV della chiamata resta su iMac in `.../.claude/cache/T-SARA-TURNTAKING/calls/` — lo raccoglie CC nel mandato successivo (evidenza per il giudice).

---

## SEQUENZA C — EMERGENZA (se qualcosa va storto)
La chiusura è **idempotente**: puoi rilanciarla quante volte vuoi.

1. Ripristina produzione:
```
ssh imac 'bash /tmp/b3/b3_close.sh'
```
2. Se non vedi `CHECKPOINT RESTORED`, **rilancia la stessa riga una seconda volta**:
```
ssh imac 'bash /tmp/b3/b3_close.sh'
```
3. Verifica:
```
ssh imac 'bash /tmp/b3/b3_status.sh'
```
   Deve dire `"engine": "pjsua2"` + `"reg_status": 200`. Se dopo due chiusure non torna, avvisa CC (non toccare altro).

---

## SCORECARD M1-M5 (compila durante/dopo la chiamata)
Segna per ognuna: OK / PARZIALE / FAIL + una nota.

| # | Mossa | Cosa fai / cosa deve fare Sara | Esito | Nota |
|---|-------|--------------------------------|-------|------|
| M1 | Greeting + disclosure | Sara saluta; si capisce bene (voce); dice/non dice «assistente virtuale» | | |
| M2 | Barge-in | La interrompi mentre parla → deve fermarsi e ascoltarti | | |
| M3 | Prenotazione | Chiedi un appuntamento → deve raccogliere nome/servizio/data/ora | | |
| M4 | Silenzio → reprompt | Stai zitto qualche secondo → deve ri-sollecitarti | | |
| M5 | Congedo | Saluti e chiudi → deve congedarsi in modo pulito | | |

---

## Riassunto comandi (i soli 3 che ti servono)
- Stato:  `ssh imac 'bash /tmp/b3/b3_status.sh'`
- Apri:   `ssh imac 'bash /tmp/b3/b3_open.sh'`   → attendi `CHECKPOINT GO-UP`
- Chiudi: `ssh imac 'bash /tmp/b3/b3_close.sh'`  → attendi `CHECKPOINT RESTORED` (rilancia se serve)
