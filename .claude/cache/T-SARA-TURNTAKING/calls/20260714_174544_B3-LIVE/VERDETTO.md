# VERDETTO — B3-LIVE / T-SARA-TURNTAKING (#34v)

- **Data raccolta**: 2026-07-14 (sessione XS, read-only + evidenza additiva)
- **Finestra**: chiamata reale founder al DID **0972536918**, trunk EHIWEB, ~17:35:20–17:36:52
- **Reperti** (dir `20260714_174544_B3-LIVE/`, md5 verificati L/R):
  - `sara_go.log` `5748de02ae329de7a368fbc3652cc95c` (57418B, effimero /tmp/b3 salvato PRIMA)
  - `restore.sh` `cdcf5308d578414195f0be08537d4499` (934B)
  - `call_20260714-173520.wav` `295336b779d5ae2fca47ea4270722a14` (2.5MB, stereo 8kHz Int16, 79.0s, L=chiamante R=Sara)
- **WAV gate founder**: CONFERMATO «SI è MIA» → **NON** ROSSO-NOWAV. GDPR: unico WAV odierno, nessun terzo da cancellare.

---

## SCORECARD FOUNDER (gate B2) — VERBATIM, nessuna riformulazione CC

| Mossa | Esito | Dichiarazione founder (verbatim) |
|-------|-------|----------------------------------|
| M1 greeting+disclosure | **OK** | «OK» (ha sentito "assistente virtuale", voce chiara) |
| M2 barge-in | **OK** | «OK , UN LEGGERO RITARDO MA VA BENE» |
| M3 prenotazione | **PARZIALE** | «SI MA è STATA MOLTO GENERICA , NON HANCHIESOT , NOME , NUMERO , E RICONOSCIMENTO CHE PRIMA FACEVA PARZIALE» |
| M4 silenzio→reprompt | **PARZIALE** | «ha detto cose a caso PARZIALE» |
| M5 congedo | **FAIL** | «NON H< RIAGGANCIATO , HO DOVUTO CHIUDERE IO , IO HO DETTO GRAZIE ARRIVEDERCI» |

**Domanda intercalari (verbatim founder):** «DOPO che avevi finito ma a sproposito»
→ gli intercalari "Capisco/Ha ragione" NON sono in overlap sulla voce del founder; arrivano DOPO la fine del suo turno, incoerenti.

---

## TIMELINE EVENTI (dal log salvato — orari reali)

| Ora | Evento | Riga |
|-----|--------|------|
| 17:35:06–08 | boot: VAD, EdgeTTS Isabella, NLU groq+cerebras PRIMARY | 1–8 |
| 17:35:08–10 | prefetch cache TTS (frasi pre-generate, non turni reali) | 10–75 |
| 17:35:37 | input=`Vorrei prenotare un taglio per domani pomeriggio.` → intent **PRENOTAZIONE** conf=1.00 | 184 |
| 17:35:38 | Sara: `Capisco. Abbiamo Taglio uomo o Taglio do…` (TTFB 433ms) | 185 |
| 17:35:48 | input=`All'uomo.` → intent PRENOTAZIONE conf=1.00 | 222 |
| 17:35:49 | Sara: `Ha ragione. Benissimo. Perfetto. Allora,…` ← **intercalare a sproposito** ("Ha ragione" su scelta servizio) | 225 |
| 17:35:51 | **BARGE-IN** rms=4662 thr=500 floor=4401 | 233 |
| 17:35:53 | input=`Scusa un attimo.` → intent CORTESIA | 243 |
| 17:36:15 | input=`Allora, stavamo dicendo...` → intent WAITLIST conf=0.80 | 318 |
| 17:36:23 | **BARGE-IN** rms=6086 thr=2520 floor=4758 | 346 |
| 17:36:26 | cerebras HTTP 404 (model_not_found) → fallback groq | 356 |
| 17:36:26 | input=`a rivederci` → intent CORTESIA conf=1.00 → **[S142] Standalone goodbye → exit=True** | 358–359 |
| 17:36:27 | Sara: `Mi scusi. Perfetto. Arrivederci, buona g…` | 362 |
| 17:36:27 | **HANGUP SOPPRESSO (FSM-guard): should_exit ma intent non-congedo ('') — Sara resta in linea** | 366 |
| 17:36:52 | asyncio ERROR Unclosed client session (chiusura lato founder) | 510 |

### RMS timeline WAV (finestre 200ms, thr_rms=500)
- L(chiamante) attivo tot **7.6s** / R(Sara) attivo tot **27.4s** su 79.0s.
- **4 segmenti overlap** (>200ms, entrambi attivi): 11.6→12.8s (1.2s), 13.6→14.2s (0.6s), 24.6→25.0s (0.4s), 29.4→30.2s (0.8s).

---

## ANALISI INTERCALARI (E5, evidence-based)

- **Turn-taking (barge-in / clear_tx)**: FUNZIONA. 2 barge-in registrati (17:35:51, 17:36:23), founder conferma M2=OK con "leggero ritardo". I 4 overlap WAV sono brevi (0.4–1.2s) e temporalmente adiacenti ai barge-in / coda TTS → **residuo di latenza cut**, non doppio-parlato di Sara. Classe **(a) overlap = non riscontrato come problema**.
- **Intercalari "Capisco"/"Ha ragione"** (righe 185, 225): emessi come token di apertura risposta DOPO il turno utente trascritto, talvolta **incoerenti** (es. "Ha ragione" in risposta a `All'uomo.`). Founder verbatim conferma: "DOPO che avevi finito ma a sproposito". Classe **(b) post-turno incoerente = NLU/latenza → stress-test §6.3, NON-gating per turn-taking**.
- **Grado di prova overlap WAV = MEDIO**: soglia RMS fissa (500), allineamento clock WAV↔log approssimato (±~2s), possibile contaminazione da **eco di linea** (canale L può captare la TX di Sara su trunk telefonico) → gli overlap 11.6/13.6/24.6s durante il parlato di Sara sono plausibilmente eco, non doppio-parlato reale. Prova dispositiva = report founder nativo + log, WAV corrobora.

## DIFETTI EMERSI (destinazione, NESSUN fix in questa sessione)

1. **M5 congedo rotto (FAIL)** — root cause identificata a log riga 366: `HANGUP soppresso (FSM-guard): should_exit ma intent non-congedo ('')`. Il goodbye `a rivederci` è rilevato (S142 exit=True) e Sara pronuncia il commiato, ma la FSM-guard sopprime il HANGUP perché l'intent passato è vuoto invece di CONGEDO → Sara resta in linea, founder chiude manualmente. **Contraddizione interna al codice** (S142 exit=True vs FSM-guard intent=''). → gating M5.
2. **M3 prenotazione generica (PARZIALE)** — Sara non chiede nome/numero né esegue riconoscimento cliente ("che prima faceva"). → regressione funzionale, da verificare vs baseline.
3. **M4 silenzio→reprompt (PARZIALE)** — "cose a caso" su silenzio → NLU/reprompt, §6.3.
4. **Intercalari incoerenti** — NLU/latenza, §6.3 (non-gating turn-taking).
5. **cerebras HTTP 404 model_not_found** (riga 356) — provider secondario NLU con modello inesistente; fallback groq regge ma il routing va corretto. [non-gating]

---

## VERDETTO SINTETICO

- **Turn-taking / barge-in**: ✅ regge (M2 OK, 2 barge-in, overlap solo residui/eco). L'ipotesi "intercalari SOPRA la voce" è **FALSIFICATA** dal founder e dal log.
- **Gating aperti**: M5 congedo (FSM-guard sopprime HANGUP), M3 prenotazione generica.
- **Non-gating → stress-test §6.3**: M4 reprompt, intercalari incoerenti, cerebras 404.
- Nessun processo/codice toccato. pjsua2 3002 intatto by-construction.
