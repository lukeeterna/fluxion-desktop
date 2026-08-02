# CERT-21 — Copione CERTIFICAZIONE Parrucchiere
> Generato: 2026-08-02 | Task: T-CERT-PREP/#46
> Scenario: silenzi + farfugliamenti → E6 escalation (nessun booking)

---

## PRIMA DI CHIAMARE — Checklist

- [ ] iMac acceso, schermo accessibile
- [ ] :3002 UP con `SARA_TEST_CAPTURE=1` (verificato T-CERT-PREP, PID 3057)
- [ ] Telefono in mano (non vivavoce — meglio qualità audio)
- [ ] Orario: mattina/pomeriggio (saluto coerente con greeting)
- [ ] Hai letto questo copione UNA VOLTA INTERA prima di chiamare

---

## NUMERO DA CHIAMARE

```
0972536918
```
Numero EHIWEB — trunk SIP diretto a Sara su iMac (192.168.1.2:3002).

---

## COPIONE (leggi nell'ordine)

### PASSO 1 — Chiama il numero
Componi **0972536918** dal tuo telefono e aspetta risposta.

### PASSO 2 — Saluto Sara
Sara risponde entro 2-3 squilli e dice:

> *"Salone Demo FLUXION, buongiorno! Come posso aiutarla?"*
> (o "buon pomeriggio" / "buonasera" secondo l'ora)

**→ NON rispondere. Rimani in silenzio.**

### PASSO 3 — Silenzio (~25 secondi)
Tieni la linea **senza dire nulla** per circa 25 secondi.

**Cosa deve accadere dopo ~22 secondi:**
> Sara riprompt: *"Pronto, è ancora in linea?"*

Se Sara non lo dice entro 30 secondi → FAIL (annota, non riagganciare ancora).

### PASSO 4 — Nome + 3 farfugliamenti
Dopo il reprompt di Sara, di' il tuo nome una volta chiaro, poi emetti **tre suoni non trascrivibili** separati da brevi pause (~2-3 secondi ciascuno):

```
TU: "Gianluca"    ← nome chiaro una volta
TU: "mmhrrgh"     ← strike 1 (suono indecifrabile)
[attendi risposta Sara]
TU: "pfghhhk"     ← strike 2 (suono indecifrabile)
[attendi risposta Sara]
TU: "xzzhhkk"     ← strike 3 (suono indecifrabile)
```

I suoni devono essere NON parole italiane — sillabe casuali, toni, rumori.
Sara risponderà ogni volta con una domanda (non avanza perché non capisce).

### PASSO 5 — E6 Escalation (terzo strike)
Dopo il terzo suono indecifrabile, Sara dice:

> *"Mi scusi, sto avendo difficoltà a comprenderla.*
> *La faremo richiamare dal salone al più presto. Arrivederci!"*

Poi la chiamata si chiude dal lato Sara (o senti il tono di chiusura).

---

## COSA DEVE ACCADERE (verdetto PASS/FAIL)

| # | Evento atteso | Segnale PASS | Segnale FAIL |
|---|---------------|--------------|--------------|
| A | Reprompt dopo ~22s silenzio | "Pronto, è ancora in linea?" | Nessun reprompt entro 30s |
| B | 3 strike per farfugliamenti | FSM non avanza dopo ogni strike | Sara avanza, chiede data/servizio |
| C | E6 dopo strike 3 | "La faremo richiamare" | "collega" presente nel testo |
| D | Chiusura da Sara | Linea cade / tono congedo | Linea resta aperta |

**PASS** = tutti e 4 gli eventi verificati.
**FAIL** = almeno uno mancante — annota quale, non perdere il log.

---

## COSA NON FARE (fondamentale)

- **NON riagganciare** prima che Sara chiuda — la chiusura deve venire da lei
- **NON aiutare Sara** — non pronunciare parole italiane chiare dopo il nome
- **NON ripetere il nome** se Sara non capisce — lasciala fallire
- **NON dire "sì" o "no"** dopo i farfugliamenti — sono parole riconoscibili
- **NON parlare durante il reprompt** di Sara — aspetta che finisca

---

## DOPO LA CHIAMATA — Raccolta artefatti

Esegui questo **comando unico** su MacBook per raccogliere tutto in un colpo:

```bash
ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no gianlucadistasi@192.168.1.2 "
CALL_DIR='/Volumes/MacSSD - Dati/fluxion/.claude/cache/T-SARA-TURNTAKING/calls';
echo '=== WAV catturati ===';
ls -lth \"\$CALL_DIR\" 2>/dev/null | head -5;
echo '';
echo '=== Log SIP + strike + escalation ===';
grep -E 'CALL_START|CALL_END|E6|strike|escalation|richiamar|IDLE.*reprompt|Pronto.*linea|turno|USER:|SARA:|fsm_state|layer=' /tmp/sara_3002.log 2>/dev/null | tail -60;
echo '';
echo '=== Trascrizione turni ===';
grep -E 'USER:|SARA:' /tmp/sara_3002.log 2>/dev/null | tail -30;
echo '';
echo '=== WAV ultimo file ===';
ls -t \"\$CALL_DIR\"/call_*.wav 2>/dev/null | head -1;
"
```

Copia l'output completo e incollalo al giudice insieme a questo file.

---

## DURATA ATTESA CHIAMATA

~ 1.5-2 minuti totali:
- 0:00-0:10 → saluto Sara + silenzio
- 0:10-0:35 → silenzio fino al reprompt (~22s)
- 0:35-1:00 → nome + 3 farfugliamenti (9-15s)
- 1:00-1:10 → E6 + chiusura Sara

---

## NOTE TECNICHE (non leggere durante la chiamata)

- **SARA_TEST_CAPTURE=1** è attivo (PID 3057, confermato via `ps eww`)
- WAV viene scritto in `.claude/cache/T-SARA-TURNTAKING/calls/call_<ts>.wav` sull'iMac
- Il WAV ha canale L=RX (tua voce) e R=TX (voce Sara), @8kHz stereo PCM16
- Se rx_rms=0 nel log → audio non arrivato (problema RTP/SIP); chiama di nuovo
- IDLE_REPROMPT_S=22.0 (voip_goengine.py:87) — attendi almeno 25s per margine
- E6 testo esatto: "richiamar" ✓ | "collega" assente ✓ (escalation_manager.py:101)
