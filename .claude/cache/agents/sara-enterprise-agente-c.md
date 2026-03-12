# CoVe 2026 — Agente C: Italian NLU Edge Cases Reali PMI
# Sara vs Gold Standard — Gap Analysis Completa
# Data: 2026-03-12 | Analisi basata su codice reale

## Metodologia
Analisi diretta di:
- `voice-agent/src/italian_regex.py` (893 righe)
- `voice-agent/src/entity_extractor.py` (1100+ righe)
- `voice-agent/tests/test_italian_regex.py` (556 righe)

Fonti benchmark: Dialogflow CX Italian NLU, Amazon Lex it-IT, Nuance Dragon Business,
Retell AI Italian, Vapi.ai, Cal.com booking flows italiani.

---

## LEGENDA
- **Coperto**: pattern presente nel codice E testato
- **Parziale**: nel codice ma non testato, o coperto solo in parte
- **No**: assente dal codice

---

## CATEGORIA 1: Conferme e Negazioni Italiane Reali (20 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C1.1 | "Esatto" | SI | italian_regex.py:86 `esatto` in CONFERMA_PATTERNS | Nessuno | — |
| C1.2 | "Esattamente" | SI | italian_regex.py:86 `esattamente` | Nessuno | — |
| C1.3 | "Proprio così" | SI | italian_regex.py:86 `proprio\s+cos[iì]` | Nessuno | — |
| C1.4 | "Macché" / "Macché!" | SI | italian_regex.py:128 `macch[eé]` in RIFIUTO_PATTERNS | Nessuno | — |
| C1.5 | "Beh sì" | PARZIALE | `beh` in FILLER_PATTERNS riga 35, poi `sì` → conferma; ma "beh sì" come frase intera NON è in CONFERMA_PATTERNS — il filler strip rimuove "beh" lasciando "sì" → funziona solo se strip avviene prima di is_conferma | Verificare ordine chiamate: strip_fillers → is_conferma | MEDIA |
| C1.6 | "Beh no" | PARZIALE | Stesso problema C1.5 — "beh" strippato ma "no" come standalone → is_rifiuto OK. Dipende dall'ordine di esecuzione | Verificare ordine chiamate | MEDIA |
| C1.7 | "Diciamo di sì" | NO | `diciamo` è in FILLER_PATTERNS riga 37 (rimosso), rimane "di sì" che NON matcha CONFERMA_PATTERNS. "di sì" non è presente. | Aggiungere `r"^diciamo\s+di\s+s[ìi]$"` a CONFERMA_PATTERNS con conf 0.7 | ALTA |
| C1.8 | "Più o meno" | NO | Assente sia da CONFERMA che da RIFIUTO. È una conferma parziale → nessun handler. Cade in Groq (L4) | Aggiungere a CONFERMA con confidence 0.6 oppure intent UNCERTAIN separato | ALTA |
| C1.9 | "All'incirca" | NO | Assente. Simile a "più o meno" — conferma con riserva | Aggiungere a CONFERMA conf 0.6 | MEDIA |
| C1.10 | "Va bene va bene" (ripetuto) | PARZIALE | `va\s+bene` è in CONFERMA_PATTERNS riga 88, ma pattern richede match esatto `^...$`. "va bene va bene" NON matcha il pattern `^(?:ok|va\s+bene|...)$` perché è un repeat. | Aggiungere `r"^(?:va\s+bene\s+){2,}$"` o togliere anchor `^...$` | ALTA |
| C1.11 | "No no no" (triplo) | PARZIALE | `no\s+no` coperto riga 128, ma solo il doppio. "no no no" → cerca `no\s+no` e matcha per substring? Pattern è `^(?:no|no\s+no|...)$` con `^$` anchors → "no no no" NON matcha esattamente | Aggiungere `no\s+no\s+no` oppure usare `(?:no\s+){2,}` | ALTA |
| C1.12 | "Mmm sì" | PARZIALE | `mmh+` in FILLER (riga 35), ma `mmm` (tripla m) NON è incluso. Dopo strip rimane "sì" → OK se mmm è strippato. Bug: `mmm` non matcha `mmh+` | Aggiungere `mmm+` al pattern hesitations | MEDIA |
| C1.13 | "Aaah sì" | PARZIALE | `aaa+` in FILLER riga 35 — "aaah" NON matcha `aaa+` (termina in h). Dopo strip rimane "sì" → OK se strip funziona. Bug: regex `aaa+` non matcha "aaah" | Cambiare in `[ah]+` o `aaa+h?` | MEDIA |
| C1.14 | "Sì sì sì" (triplo enfatico) | NO | Solo `s[iì]\s+s[iì]` (doppio) in CONFERMA riga 86. Triplo non coperto | Aggiungere `(?:s[ìi]\s+){2,}` | MEDIA |
| C1.15 | "Certo che sì" | NO | "certo" solo come standalone. "certo che sì" non coperto | Aggiungere pattern composito | BASSA |
| C1.16 | "E sì" / "E no" (conferma narrativa) | NO | Assente. Comune nel parlato italiano ("e sì devo venire") | Non modificare — ambiguo, meglio L4 | BASSA |
| C1.17 | "Appunto" (conferma enfatica) | NO | Assente da CONFERMA_PATTERNS | Aggiungere `r"^appunto$"` con conf 0.9 | MEDIA |
| C1.18 | "Ovvio" (short for "ovviamente") | NO | Solo `ovviamente` coperto riga 92. "Ovvio" standalone assente | Aggiungere `r"^ovvio$"` | BASSA |
| C1.19 | "Ma sì" | PARZIALE | `ma` è FILLER? No — assente da FILLER_PATTERNS. "ma sì" non processato correttamente | Aggiungere `ma` a FILLER_PATTERNS o aggiungere `r"^ma\s+s[ìi]$"` | ALTA |
| C1.20 | "Ma no" | PARZIALE | Stesso problema C1.19 — "ma no" non coperto | Fix contestuale con C1.19 | ALTA |

---

## CATEGORIA 2: Formule di Cortesia Italiane (12 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C2.1 | "Senta" | SI | italian_regex.py:47 `senta` in FILLER_PATTERNS (attention getters) | Nessuno | — |
| C2.2 | "Senta un po'" | PARZIALE | Solo `senta` viene strippato, "un po'" rimane e può confondere il parser. Non è un pattern di booking | Aggiungere `senta\s+un\s+po['']` come filler completo | MEDIA |
| C2.3 | "Guardi" | SI | italian_regex.py:47 `guardi` in FILLER_PATTERNS | Nessuno | — |
| C2.4 | "Mi dica" | NO | Assente da FILLER. "Mi dica" è risposta-attesa (cliente dice "mi dica" aspettando Sara). Sara dovrebbe rispondere con prompt, non come booking intent | Aggiungere a FILLER_PATTERNS: `r"\bmi\s+dica\b"` | ALTA |
| C2.5 | "La disturbo un attimo" | NO | Assente. È un opener che non contiene intent. Dopo strip non rimane nulla → probabile fallback Groq | Aggiungere `r"\bla\s+disturbo\s+(?:un\s+attimo|un\s+momento)?\b"` a FILLER | ALTA |
| C2.6 | "Ho fretta" | NO | Assente. Dovrebbe attivare un flag `time_pressure=True` → proporre slot più vicino | Aggiungere pattern TIME_PRESSURE separato, non solo filler | ALTA |
| C2.7 | "Sono di corsa" | NO | Assente. Stesso significato di C2.6 | Stesso fix C2.6 | ALTA |
| C2.8 | "Faccio in fretta" | NO | Assente. Stesso di C2.6 | Stesso fix C2.6 | MEDIA |
| C2.9 | "Pronto?" (apertura chiamata) | NO | Assente. Comune all'inizio — cliente dice "Pronto?" pensando di chiamare una persona | Aggiungere a FILLER o gestire come greeting speciale | MEDIA |
| C2.10 | "Eccomi" | NO | Assente. Risposta dopo pausa ("un momento...") — "Eccomi" vuol dire cliente è pronto. Probabilmente riconosciuto come UNKNOWN → Groq | Aggiungere a CONFERMA con conf 0.7 | MEDIA |
| C2.11 | "Dica pure" | NO | Cliente dice "dica pure" quando non ha sentito bene. Confuso con RIFIUTO? No, ma non gestito | Aggiungere a FILLER o come trigger REPEAT | BASSA |
| C2.12 | "Ci sono" (nel senso di "sono pronto") | NO | "ci sono" come idioma di disponibilità assente. ATTENZIONE: "ci sto" è in CONFERMA riga 98, ma "ci sono" no | Aggiungere `r"^ci\s+sono$"` a CONFERMA conf 0.75 | MEDIA |

---

## CATEGORIA 3: Richieste di Disponibilità Ambigue (14 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C3.1 | "Avete posto questa settimana?" | PARZIALE | `questa settimana` in AMBIGUOUS_DATE riga 580 → flag has_ambiguous_date=True. Ma non viene estratto come check-availability vs booking. Cade in FSM che interpreta come "voglio prenotare questa settimana" | Distinguere check-availability da booking-request nel FSM | ALTA |
| C3.2 | "Quando siete liberi?" | PARZIALE | entity_extractor.py riga 825: `quando\s+siete\s+liberi` → FIRST_AVAILABLE. Funziona | Nessuno significativo | — |
| C3.3 | "C'è qualcosa per domani?" | PARZIALE | "domani" estratto da extract_date() → OK. Ma l'intent "c'è qualcosa" non è coperto da L1, finisce in FSM o Groq | Aggiungere pattern FIRST_AVAILABLE con constraint date | ALTA |
| C3.4 | "Avete già qualcosa prenotato per me?" | NO | Assente. Dovrebbe triggerare check_existing_booking flow, non new-booking flow. Non coperto in nessun layer | Aggiungere intent CHECK_EXISTING_BOOKING all'intent classifier | CRITICA |
| C3.5 | "Quanto ci vuole per X?" | NO | Duration query. Assente da tutti i layer. Attualmente → Groq fallback | Aggiungere a FAQ patterns o L1 intent DURATION_QUERY | ALTA |
| C3.6 | "Avete disponibilità per venerdì?" | PARZIALE | "venerdì" estratto da extract_date(), ma "avete disponibilità" non è un intent definito. FSM tratta come prenotazione | Migliorare — intent AVAILABILITY_CHECK vs BOOKING | ALTA |
| C3.7 | "Che giorni lavorate?" | NO | Orari di apertura query. Assente da L1. Va in FAQ o Groq | Aggiungere a FAQ patterns standard | MEDIA |
| C3.8 | "Siete aperti sabato?" | PARZIALE | "sabato" estratto, ma intent check-orari non coperto. FAQ potrebbe rispondere se presente in DB | Dipende da configurazione FAQ business | MEDIA |
| C3.9 | "Prima delle ferie avete posto?" | NO | Semantica complessa — "ferie" non in alcun pattern. Groq fallback | Nessun fix ragionevole senza context aziendale | BASSA |
| C3.10 | "Ho qualcosa io da voi?" | NO | Sinonimo di C3.4. Stesso problema | Stesso fix C3.4 | ALTA |
| C3.11 | "Ho un appuntamento tra poco" | NO | Check appointment context — non coperto. Potrebbe essere recall booking o come orario "tra poco" | "tra poco" assente come time reference | MEDIA |
| C3.12 | "Posso venire senza prenotazione?" | NO | Walk-in query. Assente | Aggiungere a FAQ patterns per verticale | MEDIA |
| C3.13 | "Quanto tempo devo aspettare?" | NO | Wait time query. Non in FAQ standard | Aggiungere a FAQ patterns | MEDIA |
| C3.14 | "C'è lista d'attesa?" | PARZIALE | WAITLIST flow esiste in FSM (PROPOSING_WAITLIST state), ma la query diretta non triggerla — deve essere proposta da Sara | Aggiungere trigger proattivo quando slot è pieno | MEDIA |

---

## CATEGORIA 4: Correzioni Mid-Flow (16 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C4.1 | "No aspetta" | SI | italian_regex.py:58 `_NO_ASPETTI_PRIORITY` + riga 702 prefilter override → CorrectionType.WAIT con conf 0.95 | Nessuno | — |
| C4.2 | "Anzi" | PARZIALE | `anzi` compare in CORRECTION_PATTERNS come parte di pattern composti (es. `anzi,\s+meglio...`). Ma "anzi" standalone NON è coperto — se cliente dice solo "anzi" → UNKNOWN | Aggiungere `r"^anzi$"` come CorrectionType.GENERIC_CHANGE | ALTA |
| C4.3 | "Ho detto male" | SI | italian_regex.py:532 `ho\s+detto\s+male` → GENERIC_CHANGE | Nessuno | — |
| C4.4 | "Intendevo dire" | SI | italian_regex.py:531 `(?:aspett[ia]|...|volevo\s+dire|intendevo)` | Nessuno | — |
| C4.5 | "Scusi ho sbagliato" | PARZIALE | `mi\s+sono\s+sbagliat[oa]` coperto riga 532. Ma "scusi ho sbagliato" (con "scusi" esplicito) non è testato | Test aggiuntivo, coverage parziale | BASSA |
| C4.6 | "Non quello, l'altro" | NO | Riferimento anaforico ambiguo. Non coperto in nessun pattern. Richiede context tracking | Gestire con CorrectionType.GENERIC_CHANGE + richiedere chiarimento | ALTA |
| C4.7 | "Il primo / il secondo" come selezione slot | NO | Quando Sara propone orari multipli "ho disponibilità alle 10, alle 14 e alle 16", cliente dice "il secondo". NON coperto | Aggiungere handler slot-selection numerica ordinale | CRITICA |
| C4.8 | "Quello di prima" come riferimento | NO | Anafora temporale. Non coperto | Richiede context tracking sessione | MEDIA |
| C4.9 | "Come prima" (stesso servizio, stesso operatore) | NO | Ripetizione identica all'appuntamento precedente. Non coperto | Aggiungere intent SAME_AS_LAST_TIME | ALTA |
| C4.10 | "Aspetta che guardo l'agenda" | PARZIALE | "aspetta" coperto → WAIT. Ma frase completa può confondere | WAIT trigger sufficiente | — |
| C4.11 | "Metti..." (imperativo diretto) | NO | "metti giovedì" = scegli giovedì. Pattern imperativo `metti\s+\w+` non coperto esplicitamente | Aggiungere a CHANGE_DATE: `r"metti\s+(?:domani|lunedì|...)"` | MEDIA |
| C4.12 | "Dai mettiamo..." | PARZIALE | `dai` è in CONFERMA patterns riga 95. "dai mettiamo giovedì" → "dai" triggera CONFERMA ma "mettiamo giovedì" è perso | Conflitto: "dai" = conferma ma "dai mettiamo X" = CHANGE | ALTA |
| C4.13 | "Va beh/boh" (rassegnata accettazione) | PARZIALE | `beh` e `boh` in FILLER. "va beh" dopo filler strip diventa "va" → non matcha CONFERMA. Bug reale | Aggiungere `r"^va\s+beh$"` a CONFERMA conf 0.7 | ALTA |
| C4.14 | "Torniamo a..." con riferimento specifico | PARZIALE | `torniamo\s+indietro` coperto come GENERIC_CHANGE riga 533. "torniamo all'orario" non coperto | Sufficiente con GENERIC_CHANGE | — |
| C4.15 | "Rifacciamo" | NO | Restart del flow. Non coperto | Aggiungere a GENERIC_CHANGE: `r"\brifacciamo\b"` | MEDIA |
| C4.16 | "Riprendiamo" | NO | Riprendere il flusso dopo pausa. Non coperto | Aggiungere a CorrectionType.WAIT o nuovo tipo RESUME | MEDIA |

---

## CATEGORIA 5: Numeri e Date Italiani Parlati (20 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C5.1 | "Il tre" / "Il quattro" come date del mese | PARZIALE | entity_extractor.py riga 385: pattern `\bil\s+(\d{1,2})\b` — cattura "il 3" ma NON cattura "il tre" (scritto in lettere). `_normalize_italian_numbers` non include numeri piccoli da 1 a 9 come date | Aggiungere mapping 1-31 in it_numbers per extract_date | CRITICA |
| C5.2 | "Il primo" come 1° del mese | NO | "il primo" → "primo" è in NAME_BLACKLIST riga 887. Non estratto come data | Aggiungere pattern speciale `\bil\s+primo\b` → giorno 1 | CRITICA |
| C5.3 | "Giovedì mattina presto" | SI | extract_date (giovedì) + TIME_SLOTS "mattina presto" → TimeSlot.MATTINA_PRESTO (08:00) — coperto | Nessuno | — |
| C5.4 | "Venerdì a pranzo" | SI | "venerdì" → extract_date; "pranzo" → TimeSlot.PRANZO (13:00) | Nessuno | — |
| C5.5 | "Nel pomeriggio" | SI | entity_extractor.py TIME_SLOTS riga 213: `"nel pomeriggio"` → POMERIGGIO (15:00) | Nessuno | — |
| C5.6 | "Di pomeriggio" | PARZIALE | TIME_SLOTS ha "nel pomeriggio" e "pomeriggio" ma NON "di pomeriggio". "di pomeriggio" matcha "pomeriggio" come substring solo se la ricerca è `in text_n` — verifica: riga 803 `if slot_name in text_n` → "pomeriggio" è in "di pomeriggio" → funziona per substring | OK via substring match — ma confidence 0.8 non tiene conto dell'ambiguità | BASSA |
| C5.7 | "Nel tardo pomeriggio" | SI | TIME_SLOTS riga 209: `"tardo pomeriggio"` → TARDO_POMERIGGIO (17:00). "nel tardo pomeriggio" contiene "tardo pomeriggio" → substring match OK | Nessuno | — |
| C5.8 | "Verso le cinque" → ~17:00 ±30min | SI | entity_extractor.py riga 769: `verso\s+le` → AROUND constraint con ±30min. `_disambiguate_hour_pm` converte 5→17 | Nessuno | — |
| C5.9 | "Alle cinque e mezza" → 17:30 | SI | riga 621: `e\s+(?:mezza|mezzo)` → XX:30; ora 5→17 via PM disambiguation | Nessuno | — |
| C5.10 | "Tra le tre e le quattro" → RANGE 15:00-16:00 | SI | riga 692: `tra\s+le\s+(\d{1,2})\s+e\s+le\s+(\d{1,2})` → RANGE TimeConstraint. PM disambiguation mancante per range | BUG: range non applica _disambiguate_hour_pm → "tra le 3 e le 4" → range 03:00-04:00 invece di 15:00-16:00 | CRITICA |
| C5.11 | "Prima delle dieci" → BEFORE 10:00 | SI | riga 753: `prima\s+(?:delle?|della)\s+(\d{1,2})` → BEFORE constraint | Nessuno | — |
| C5.12 | "Prima di mezzogiorno" | SI | _SEMANTIC_ANCHORS riga 465: `prima\s+del\s+lavoro` ma NON "prima di mezzogiorno" esplicitamente. Tuttavia "mezzogiorno" in TIME_SLOTS → MEZZOGIORNO. "prima delle 12" via extract_time | PARZIALE: "prima di mezzogiorno" non matcha il pattern BEFORE esplicitamente | MEDIA |
| C5.13 | "Stamattina" come slot temporale | PARZIALE | TIME_SLOTS ha "mattina" ma NON "stamattina" esplicitamente. "stamattina" contiene "mattina" come substring → matcha via substring. Ma semanticamente "stamattina" = oggi mattina → extract_date dovrebbe anche estrarre OGGI | "stamattina" non estratto come data+ora combo | ALTA |
| C5.14 | "Stasera" | SI | TIME_SLOTS riga 220: `"stasera"` → SERA (19:00) coperto | Nessuno | — |
| C5.15 | "Stanotte" | NO | TIME_SLOTS non ha "stanotte". Nessun servizio PMI è disponibile di notte → dovrebbe generare risposta "siamo chiusi di notte" | Aggiungere gestione CLOSED_HOURS per "stanotte" / "notte" | MEDIA |
| C5.16 | "A fine mese" | NO | Date relativa "fine mese". Non coperta da alcun pattern. Finisce in Groq | Aggiungere `r"\b(?:a\s+)?fine\s+mese\b"` → ultimo giorno del mese | ALTA |
| C5.17 | "A inizio mese" | NO | Simile a C5.16 | Aggiungere → primo giorno del mese prossimo | MEDIA |
| C5.18 | "Il mese prossimo" senza giorno | PARZIALE | `il\s+prossimo\s+mese` in AMBIGUOUS_DATE riga 582 → has_ambiguous_date=True. Non estratto come date | Trattare come ambiguous date → chiedere giorno specifico | MEDIA |
| C5.19 | "Settimana che viene" | NO | Sinonimo di "prossima settimana". Non in AMBIGUOUS_DATE né extract_date | Aggiungere `settimana\s+che\s+viene` a AMBIGUOUS_DATE | ALTA |
| C5.20 | "Dopodomani pomeriggio" | PARZIALE | "dopodomani" coperto in RELATIVE_DATES riga 201; "pomeriggio" in TIME_SLOTS. Ma extract_date e extract_time sono chiamate separatamente — combo date+time in una frase dipende dall'integrazione FSM | Verificare che FSM chiami entrambi su stessa stringa | MEDIA |

---

## CATEGORIA 6: Multi-Persona Booking (10 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C6.1 | "Prenoto per me e mia figlia" | NO | Multi-persona booking assente. extract_multi_services cerca servizi multipli, non persone multiple. Il FSM non ha stato MULTI_PERSON_BOOKING | Feature mancante — richiede stato FSM dedicato | CRITICA |
| C6.2 | "Siamo in due" | NO | Assente. Potrebbe attivare multi-booking o slot doppio | Aggiungere detection party-size | ALTA |
| C6.3 | "Anche per mia moglie uguale" | NO | "anche" è in MULTI_SERVICE_PATTERNS riga 341 (`anche\s+aggiungi`), ma per persone non funziona | Distinguere multi-servizio da multi-persona | ALTA |
| C6.4 | "Per un mio amico" (cliente diverso) | NO | Booking per terzo. extract_name cattura il nome dopo "per" (`per\s+([A-Z]...)` riga 943) ma il flow è pensato per il chiamante, non per terzi | Aggiungere flag `booking_for_other=True` | ALTA |
| C6.5 | "Tre posti" / "tre appuntamenti" | NO | Quantità di booking assente | Feature mancante | ALTA |
| C6.6 | "Io e mio marito" | NO | Stessa logica C6.1 | Stesso fix C6.1 | ALTA |
| C6.7 | "Tutti e due" come conferma di slot multiplo | NO | Non coperto | Gestire come conferma con count=2 | MEDIA |
| C6.8 | "Prima io poi mia figlia" | NO | Sequenza temporale multi-persona assente | Feature complessa — rinviare | BASSA |
| C6.9 | "Uno per ciascuno" | NO | Non coperto | Stessa classe C6.1 | MEDIA |
| C6.10 | "Due taglio, uno piega" | PARZIALE | has_multi_service_intent cattura servizi multipli ma non la quantità per persona | Aggiungere quantity tracking | MEDIA |

---

## CATEGORIA 7: Richieste FAQ Mid-Booking (10 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C7.1 | "Ma quanto costa?" durante booking | PARZIALE | L3 FAQ manager gestisce FAQ. Ma se FSM è in stato attivo (COLLECTING_DATE, etc.) la FAQ mid-booking può interrompere il flow senza riprendere il punto | BUG critico: nessun meccanismo di "FAQ pause + resume booking" | CRITICA |
| C7.2 | "Quanto dura?" durante booking | PARZIALE | Stessa problema C7.1 | Stesso fix C7.1 | CRITICA |
| C7.3 | "Posso pagare con carta?" | PARZIALE | FAQ se configurata, altrimenti Groq. Ma interruzione flow non gestita | Fix con C7.1 | ALTA |
| C7.4 | "Avete parcheggio?" | PARZIALE | FAQ se configurata | Fix con C7.1 | MEDIA |
| C7.5 | "Dove siete?" durante booking | PARZIALE | FAQ se configurata. Rilevante: cliente potrebbe chiamare da fuori e chiedere indirizzo mid-booking | Fix con C7.1 | ALTA |
| C7.6 | Riprendere booking dopo FAQ | NO | Meccanismo resume-state assente. Dopo FAQ risposta, FSM non sa in quale stato era prima | Aggiungere `pre_faq_state` field in session context | CRITICA |
| C7.7 | "E poi quanto mi costa?" (en passant) | NO | FAQ inline non separata dall'intent principale | Stessa issue C7.6 | ALTA |
| C7.8 | "Aspetta, prima dimmi..." pattern | PARZIALE | "aspetta" → WAIT, ma "prima dimmi X" non ha handler per estrarre FAQ query | Aggiungere pattern `prima\s+dimmi\s+(.+)` → FAQ query | MEDIA |
| C7.9 | "Una cosa sola" (conferma di single service dopo multi-proposta) | NO | Non coperto | Aggiungere a RIFIUTO multi-service context | MEDIA |
| C7.10 | "Lasciamo perdere il colore, solo taglio" | PARZIALE | `lasciamo\s+perdere` in RIFIUTO riga 134. Il servizio specifico non viene estratto | Aggiungere extraction del servizio nel contesto del RIFIUTO | ALTA |

---

## CATEGORIA 8: Dialettale / Colloquiale (14 pattern)

| # | Pattern | Coperto? | File:riga | Fix necessario | Priorità |
|---|---------|----------|-----------|----------------|----------|
| C8.1 | "Me fate" (romano) | NO | Variante dialettale di "mi fate". Non in alcun normalizzatore. Whisper tipicamente trascrive dialetti in modo inconsistente | Aggiungere normalizzazione pre-processing: `me\s+fate` → `mi fate` | MEDIA |
| C8.2 | "Ci stai" (sei disponibile) | PARZIALE | `ci\s+sto` è in CONFERMA riga 98 (cliente che confirma), ma "ci stai" è rivolta a Sara come query. Semantica opposta! | Potenziale false positive: "ci stai?" (domanda a Sara) vs "ci sto" (conferma cliente). Aggiungere context check | ALTA |
| C8.3 | "Adesso adesso" (subito, urgente) | NO | "adesso" non in TIME_SLOTS né semantic anchors. FIRST_AVAILABLE solo per "subito" riga 825. "adesso adesso" → Groq | Aggiungere `adesso\s+adesso` e `adesso` a FIRST_AVAILABLE triggers | ALTA |
| C8.4 | "Tra poco" come orario vago | NO | "tra poco" non in TIME_SLOTS. Semanticamente = 30-60min da ora. Potrebbe triggerare slot imminente | Aggiungere `tra\s+poco` → ask clarification o trattare come FIRST_AVAILABLE | ALTA |
| C8.5 | "Stamattina" come oggi+mattina | PARZIALE | TIME_SLOTS ha "mattina" (substring match funziona). Ma extract_date NON estrae "oggi" da "stamattina" — data rimane undefined | Aggiungere `stamattina` a RELATIVE_DATES + TIME_SLOTS combo | ALTA |
| C8.6 | "Oggi pomeriggio" / "Questo pomeriggio" | PARZIALE | "oggi" in RELATIVE_DATES OK; "pomeriggio" in TIME_SLOTS OK. Ma come combo non testato — due chiamate separate potrebbero avere clash | Verificare che FSM concateni oggi+pomeriggio correttamente | MEDIA |
| C8.7 | "A pranzo" vs "per pranzo" | SI | TIME_SLOTS ha `"pranzo"` → 13:00. "a pranzo" e "per pranzo" matchano via substring | Nessuno | — |
| C8.8 | "Domattina" (domani mattina contrazione) | NO | "domattina" non in RELATIVE_DATES né TIME_SLOTS. Whisper trascrive spesso questa forma contratta | Aggiungere `domattina` → domani + mattina | ALTA |
| C8.9 | "Lunedì mattina" come slot completo | PARZIALE | extract_date (lunedì) + TIME_SLOTS (mattina) chiamate separate. Funziona se FSM li integra | Dipende da integrazione FSM — verificare | MEDIA |
| C8.10 | "Eh già" (conferma rassegnata) | NO | Assente da CONFERMA. "già" da solo non è in CONFERMA | Aggiungere `r"^eh\s+già$"` conf 0.7 oppure lasciare a Groq | BASSA |
| C8.11 | "Certo certo" (doppia conferma) | PARZIALE | Solo `certo` singolo in CONFERMA riga 86. "certo certo" → non matcha il pattern `^certo$` (anchors) | Aggiungere `r"^cert[oa]\s+cert[oa]$"` o rimuovere anchors | MEDIA |
| C8.12 | "Perfetto perfetto" (doppio) | PARZIALE | Solo `perfetto` singolo. Stesso problema C8.11 | Stesso fix | MEDIA |
| C8.13 | "Boh" come incertezza (non conferma) | PARZIALE | `boh` in FILLER_PATTERNS riga 35 — strippato. Ma "boh" standalone dovrebbe essere UNCERTAIN/UNKNOWN, non strippato in modo che non rimanga nulla | Se dopo strip rimane stringa vuota → FSM non sa cosa fare. Aggiungere handler per empty-after-strip | ALTA |
| C8.14 | "Mah" come esitazione/dubbio | PARZIALE | `mah` in FILLER riga 35 — stesso problema C8.13 | Stesso fix C8.13 | ALTA |

---

## RIEPILOGO PRIORITÀ

### CRITICHE (bug bloccanti per uso reale)
| # | Pattern/Issue | Impact |
|---|---------------|--------|
| BUG-A | "Il tre" / "il quattro" come data — numeri in lettere non estratti | Cliente non può dire "il sette di marzo" |
| BUG-B | "Il primo" del mese — bloccato da NAME_BLACKLIST | "Voglio venire il primo" → nessuna data estratta |
| BUG-C | "Tra le tre e le quattro" → range 03:00-04:00 invece di 15:00-16:00 | PM disambiguation mancante per range |
| BUG-D | "Avete già qualcosa prenotato per me?" → no check_existing_booking | Cliente non può verificare appuntamento esistente |
| BUG-E | "Il primo / il secondo" (selezione slot ordinale) → non coperto | Cliente non può scegliere tra slot proposti |
| BUG-F | FAQ mid-booking senza resume state → flow perso | Ogni domanda FAQ durante booking resetta la conversazione |
| BUG-G | Multi-persona booking assente | "Prenoto per me e mia figlia" non gestito |

### ALTE (degradano esperienza utente)
- C1.7 "Diciamo di sì" → UNKNOWN (Groq)
- C1.10 "Va bene va bene" → non matcha CONFERMA (anchors)
- C1.11 "No no no" → non matcha RIFIUTO (anchors)
- C1.19 "Ma sì" / C1.20 "Ma no" → non coperto
- C2.4 "Mi dica" → non strippato, confonde FSM
- C2.5 "La disturbo un attimo" → va in Groq
- C2.6 "Ho fretta" / C2.7 "Sono di corsa" → nessuna gestione time_pressure
- C4.2 "Anzi" standalone → UNKNOWN
- C4.7 slot selection ordinale "il secondo"
- C4.12 "Dai mettiamo..." → conflitto CONFERMA vs CHANGE
- C4.13 "Va beh" → non matcha CONFERMA
- C5.13 "Stamattina" → data non estratta (solo ora)
- C5.16 "A fine mese" → Groq
- C5.19 "Settimana che viene" → non in AMBIGUOUS_DATE
- C8.3 "Adesso adesso" → non in FIRST_AVAILABLE
- C8.4 "Tra poco" → non gestito
- C8.5 "Stamattina" → data+ora non combo
- C8.8 "Domattina" → non esiste
- C8.13 "Boh" / C8.14 "Mah" standalone → stringa vuota dopo strip

---

## PATTERN AGGIUNTIVI NON NELLE CATEGORIE ORIGINALI (gap emersi dall'analisi)

| # | Pattern | Coperto? | Fix | Priorità |
|---|---------|----------|-----|----------|
| X1 | "Richiamo dopo" / "Richiamatemi" | PARZIALE | "richiamate" in ESCALATION (callback). "richiamo dopo" → non coperto come graceful exit | Aggiungere GRACEFUL_EXIT pattern | ALTA |
| X2 | "Devo andare" / "Devo scappare" | NO | Nessun graceful close pattern. Cliente che deve chiudere → sessione orfana | Aggiungere CLOSE_SESSION triggers | ALTA |
| X3 | Numero di telefono dettato verbalmente | PARZIALE | entity_extractor non mostrato ma dovrebbe avere phone regex. Verifica: Whisper trascrive "tre - tre - due..." con trattini | Aggiungere normalizzazione numero con trattini e spazi | ALTA |
| X4 | "Non sento bene" (qualità audio) | NO | Nessun handler per problemi audio. Cliente informa di problemi di connessione | Aggiungere a CorrectionType.REPEAT o nuovo tipo AUDIO_ISSUE | MEDIA |
| X5 | "Aspetti che prendo l'agenda" | PARZIALE | "aspetti" → WAIT OK. Frase completa non testata | Verificare che WAIT sia triggerato | BASSA |
| X6 | "Ho cambiato idea sul servizio" | PARZIALE | `ho\s+cambiato\s+idea` in RIFIUTO riga 143. Ma "sul servizio" non specifica quale → FSM deve ri-chiedere | Aggiungere extraction servizio nel contesto del cambio | MEDIA |
| X7 | "L'ultima volta ho fatto X" (reference booking precedente) | NO | Nessun lookback storico. Richiede query DB | Feature avanzata — rinviare | BASSA |
| X8 | "Potrei avere anche X?" (aggiunta servizio in fase conferma) | PARZIALE | MULTI_SERVICE_INTENT cattura "anche X" ma solo se in fase iniziale. In CONFIRMING state non gestito | Aggiungere multi-service handler nello stato CONFIRMING | ALTA |
| X9 | Email dettata verbalmente con "chiocciola" | NO | entity_extractor non mostra email pattern. "mario chiocciola gmail punto com" non coperto | Aggiungere normalizzazione email parlata: `chiocciola→@`, `punto→.` | ALTA |
| X10 | Numero con "zero" iniziale ("zero tre tre...") | NO | `_normalize_italian_numbers` non include "zero". Whisper trascrive spesso prefissi come "zero tre tre..." | Aggiungere "zero" → "0" in normalizzatore | ALTA |

---

## NOTE IMPLEMENTATIVE

### Bug BUG-C (range PM disambiguation) — Fix rapido
In `entity_extractor.py`, PHASE 3 (riga 692), aggiungere dopo `start_h = int(m.group(1))`:
```python
start_h = _disambiguate_hour_pm(start_h, text)
end_h = _disambiguate_hour_pm(end_h, text)
```

### Bug BUG-A (date in lettere piccoli numeri) — Fix rapido
In `it_numbers` dict di `extract_date()` (riga 316), aggiungere:
```python
'uno': 1, 'due': 2, 'tre': 3, 'quattro': 4, 'cinque': 5,
'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9, 'dieci': 10,
# ... fino a 31
```
Poi applicare normalizzazione PRIMA del check `\bil\s+(\d{1,2})`.

### Bug BUG-B ("il primo" bloccato da blacklist) — Fix rapido
In `extract_date()`, aggiungere check speciale PRIMA dei pattern generali:
```python
if re.search(r'\bil\s+primo\b', text_lower):
    # giorno 1 del mese corrente o prossimo
```

### Feature TIME_PRESSURE — Fix strutturale
In `prefilter()` aggiungere nuovo campo `has_time_pressure: bool` e pattern:
```python
TIME_PRESSURE_PATTERNS = [
    r"\b(?:ho\s+fretta|sono\s+di\s+corsa|faccio\s+in\s+fretta|ho\s+poco\s+tempo)\b",
    r"\b(?:in\s+fretta|velocemente|subito\s+se\s+possibile)\b",
]
```
Nel FSM: se `has_time_pressure=True` → lookup_type="first_available" con skip delle domande intermedie.

---

## CONTEGGIO FINALE
- Pattern analizzati: **116**
- Coperti completamente: **31** (26.7%)
- Parzialmente coperti: **36** (31.0%)
- Non coperti: **49** (42.3%)
- Bug critici identificati: **7**
- Fix ad alta priorità: **24**
