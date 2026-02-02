# Prompt per Kimi 2.5 — Bug Fix Strutturali + TTS Italiana per Release v1.0

Copia tutto il contenuto sotto la linea e incollalo su Kimi 2.5.

---

## Contesto di Sistema

Sto sviluppando **FLUXION**, un gestionale desktop per PMI italiane con un **voice agent** ("Sara") che gestisce prenotazioni via VoIP. Siamo a 3 settimane di sviluppo, 910 test passing, ma la conversazione reale con un utente ha rivelato **7 bug strutturali** che rendono Sara inutilizzabile per la release.

Stack: Python 3.9 (iMac runtime, NON aggiornabile), aiohttp, SQLite, pipeline RAG a 5 livelli, state machine deterministica.

## PARTE 1: Bug Fix Strutturali

### Conversazione Reale Fallita (Kekko Zalone)

Ecco la conversazione reale che ha esposto tutti i bug. Leggi TUTTA la conversazione, poi analizza ogni bug.

```
[RESET]
Sara: Buon pomeriggio! Sono Sara, l'assistente vocale. Come posso aiutarla?

Kekko: "Eh sì, sono Kekko, devo prendere appuntamento."
Sara: "Piacere Kekko! Mi dice il cognome?" → (waiting_surname) ✅ OK

Kekko: "Zalone"
Sara: "Non la trovo tra i nostri clienti. Mi dà un numero di telefono?" → (registering_phone) ✅ OK

Kekko: "eh sì e... allora il tuo numero com'è? 3807769822"
Sara: "Ho capito 3807769822, è corretto?" → (confirming_phone) ✅ OK

Kekko: "quello se dici un numero alla volta è meglio, comunque è corretto"
Sara: "Benvenuto Kekko Zalone! Registrazione completata. Che trattamento desidera?" ✅ OK

Kekko: "io mi devo fare la barba mi devo fare i capelli e la tinta"
Sara: "Bene, Colore e Barba! Per quale giorno?"
❌ BUG 1: "capelli" = taglio, ma non è stato estratto. Mancano 1 su 3 servizi.

Kekko: "si colore e barba però mi devo fare pure i capelli"
Sara: "Per quale giorno vorrebbe prenotare?"
❌ BUG 2: Sara ignora COMPLETAMENTE la correzione servizio in WAITING_DATE.
Il cliente sta dicendo "mi manca un servizio" e Sara lo ignora.

Kekko: "senti facciamo la settimana prossima che sta settimana sono impegnato"
Sara: "lunedì 9 febbraio, perfetto. Disponibilità alle 09:00, 10:30..."
❌ BUG 3: "la settimana prossima" dovrebbe mostrare i giorni disponibili,
NON auto-selezionare lunedì. Il codice week_availability esiste ma non viene triggerato.

Kekko: "Senti, per forza lunedì non possiamo fare tra mercoledì e giovedì?"
Sara: "A che ora le andrebbe bene?"
❌ BUG 4: In WAITING_TIME, Sara ignora COMPLETAMENTE la richiesta di cambiare data.
Non c'è back-navigation da WAITING_TIME a WAITING_DATE.

Kekko: "dopo le 17 perché torno e mi devo fare la doccia"
Sara: "Riepilogo: Colore e Barba, lunedì 9 febbraio, alle 17:00. Conferma?"
❌ BUG 5: Data ancora lunedì (il cliente aveva chiesto mer/gio).
Servizi ancora Colore e Barba (manca Taglio).

Kekko: "no allora io lunedì non sono disponibile o mercoledì o giovedì dopo le 17"
Sara: "Perfetto! data → 2026-02-09, ora → 17:30. Confermi ora?"
❌ BUG 6: La correzione in CONFIRMING non funziona. 2026-02-09 è ANCORA lunedì.
"mercoledì" viene ignorato. L'utente dice "no" + nuovo giorno ma la data non cambia.

Kekko: "No, dobbiamo fare mercoledì della settimana prossima."
Sara: "Perfetto! data → 2026-02-04."
❌ BUG 7: "mercoledì della settimana prossima" calcola 2026-02-04 (QUESTA settimana)
invece di 2026-02-11 (PROSSIMA settimana). Il codice ignora "prossima" quando days_ahead > 0.

Kekko: "fam parla con un operatore tu sei un robot non mi capisci"
Sara: "La metto in contatto con un operatore, un attimo..."
⚠️ L'escalation funziona ma il TTS è troppo robotico (macOS "say").
```

### Analisi Tecnica dei Bug

#### BUG 1: "capelli" non estratto come servizio
**File**: `italian_regex.py`, riga 219
**Causa**: La lista sinonimi di "taglio" è:
```python
"taglio": ["taglio", "sforbiciata", "spuntatina", "accorciare", "accorciatina", "taglietto"]
```
Manca: "capelli", "fare i capelli", "taglio capelli", "sistemare i capelli"
**Impatto**: L'utente italiano dice SEMPRE "mi devo fare i capelli" per intendere "taglio". È il sinonimo più comune.

#### BUG 2: Correzione servizio ignorata in WAITING_DATE
**File**: `booking_state_machine.py`, `_handle_waiting_date()`
**Causa**: Quando il SM è in WAITING_DATE, processa SOLO date. Se il cliente dice "mi devo fare pure i capelli", il handler ignora l'aggiunta di servizio.
**Fix necessario**: In WAITING_DATE, se l'input contiene un servizio (e NON una data), tornare a WAITING_SERVICE o aggiungere il servizio senza uscire dallo stato.

#### BUG 3: "settimana prossima" auto-seleziona lunedì
**File**: `entity_extractor.py`, riga 211-216 + `booking_state_machine.py`, `_handle_waiting_date()`
**Causa**: Il flow è:
1. `process_message()` chiama `extract_all()` → `extract_date("settimana prossima")` → restituisce lunedì
2. `_update_context_from_extraction()` setta `self.context.date = "2026-02-09"` (lunedì)
3. `_handle_waiting_date()` vede `self.context.date` già settata → va a WAITING_TIME
4. Il check `is_ambiguous_date()` NON viene mai raggiunto perché la data è già estratta.

**Il problema è nell'ordine**: `extract_all()` estrae la data PRIMA che `is_ambiguous_date()` possa intercettarla.
**Fix necessario**: In `_handle_waiting_date()`, controllare `is_ambiguous_date()` PRIMA di usare `self.context.date` estratta, oppure in `_update_context_from_extraction()` non settare la data se il testo è ambiguo.

#### BUG 4: WAITING_TIME ignora richieste di cambio data
**File**: `booking_state_machine.py`, `_handle_waiting_time()`
**Causa**: L'handler di WAITING_TIME processa SOLO orari. Non ha logica di back-navigation.
```python
def _handle_waiting_time(self, text, extracted):
    if self.context.time:          # ha orario → conferma
        ...
    time = extract_time(text)       # prova estrarre orario
    if time:                        # trovato → conferma
        ...
    return "A che ora le andrebbe?" # fallback: richiedi orario
```
**Fix necessario**: Prima di `extract_time()`, controllare se il testo contiene un giorno/data. Se sì, svuotare `self.context.date` e tornare a WAITING_DATE.

#### BUG 5: Correzione in CONFIRMING non aggiorna data
**File**: `booking_state_machine.py`, `_handle_confirming()`
**Causa**: L'utente dice "no, mercoledì o giovedì, dopo le 17". Il Level 1 di `_handle_confirming` estrae le entità, ma:
1. `extract_date("mercoledì")` ritorna il PRIMO mercoledì trovato (questa settimana)
2. Il contesto "della settimana prossima" è nella frase precedente, non in questa
3. L'anti-cascade guard dopo 2 correzioni dice "Questa è l'ultima modifica" ma la data è sbagliata

#### BUG 6: "mercoledì della settimana prossima" → data sbagliata
**File**: `entity_extractor.py`, righe 187-209
**Causa esatta**:
```python
days_ahead = (weekday - today_weekday) % 7  # (2 - 0) % 7 = 2
if days_ahead == 0:  # FALSE (è 2, non 0)
    if "prossima" in text_lower:  # MAI RAGGIUNTO
        days_ahead = 7
target_date = reference_date + timedelta(days=2)  # QUESTA settimana, NON prossima
```
Il check "prossima" viene fatto SOLO se `days_ahead == 0`. Se il giorno è futuro (mer > lun), il "prossima" viene ignorato.
**Fix**: Il check "prossima/prossimo" deve applicarsi SEMPRE, non solo quando `days_ahead == 0`.

### Cosa Devi Generare (PARTE 1)

Per OGNI bug, genera:
1. **Codice Python corretto** (patch chirurgico, non riscrittura)
2. **Test pytest** che verifica il fix
3. **Spiegazione** di perché il codice originale falliva

Vincoli:
- Python 3.9 (no walrus operator `:=`, no `match/case`)
- I fix devono essere retrocompatibili con i 910 test esistenti
- Ogni fix deve essere un diff minimo (non riscrivere handler interi)
- Usa le stesse convenzioni del codebase: `StateMachineResult`, `BookingState`, `TEMPLATES`

### Priorità di Fix

```
P0 (bloccanti release):
  BUG 6: extract_date "prossima" ignorata → date sbagliate
  BUG 1: "capelli" non è taglio → servizio più comune mancante
  BUG 3: "settimana prossima" bypassa week_availability → auto-seleziona lunedì
  BUG 4: WAITING_TIME non permette cambio data → utente bloccato

P1 (importanti):
  BUG 2: correzione servizio ignorata in WAITING_DATE
  BUG 5: correzioni multiple in CONFIRMING non funzionano bene

P2 (nice-to-have):
  Migliorare anti-cascade guard per gestire meglio 3+ correzioni
```

---

## PARTE 2: TTS Italiana per Release v1.0

### Situazione Attuale

Sara usa **macOS `say`** (voce "Alice") come TTS. Qualità 5/10: robotica, innaturale, pause sbagliate. L'utente si è lamentato esplicitamente ("tu sei un robot").

### Stack Constraints

```
Runtime: Python 3.9.6 su iMac (macOS Monterey 12.x)
NO PyTorch (Python 3.9 non supporta torch 2.x)
NO GPU (iMac Intel 2017)
OK: ONNX Runtime, subprocess, API esterne, pip packages
Pipeline: aiohttp su porta 3002, async
Latenza target: < 500ms per frase
Output: WAV bytes restituiti via HTTP JSON (hex-encoded)
Budget: ragionevole (no enterprise pricing)
```

### Motori Già Valutati e Scartati

| Motore | Stato | Motivo Scarto |
|--------|-------|---------------|
| Kokoro TTS | SCARTATO | Python 3.10+ required, API hallucinate, italiano grade C |
| Chatterbox Italian | DISPONIBILE MA BLOCCATO | Richiede PyTorch (non disponibile su Python 3.9) |
| Piper TTS (Paola) | DISPONIBILE | Qualità 7.5/10, latenza 50ms, ma voce poco naturale |
| macOS "say" (Alice) | ATTIVO | Qualità 5/10, robotica, unica opzione corrente |
| Qwen3-TTS | VALUTATO | Richiede GPU/API, troppo pesante per iMac Intel |

### Cosa Devi Generare (PARTE 2)

Cerca e valuta TUTTE le opzioni TTS italiane disponibili nel 2025-2026 che rispettano i vincoli sopra. Per ogni opzione, fornisci:

1. **Nome e repository/API**
2. **Requisiti**: Python version, dipendenze, GPU/CPU, dimensione modello
3. **Compatibilità Python 3.9**: sì/no, se no perché
4. **Qualità voce italiana**: voto 1-10 con descrizione
5. **Latenza stimata** su CPU Intel (iMac 2017)
6. **Tipo integrazione**: pip install, subprocess, API REST, ONNX
7. **Costo**: gratuito/freemium/pagamento
8. **Codice di integrazione** Python async per la nostra pipeline aiohttp

### Categorie da Esplorare

1. **API Cloud TTS** (Google Cloud TTS, Azure Cognitive Speech, Amazon Polly, ElevenLabs, PlayHT)
   - Pro: qualità alta, facile integrazione
   - Con: latenza rete, costo per carattere, dipendenza internet
   - Valuta: tier gratuiti, costo per 10.000 frasi/mese

2. **Motori Locali ONNX** (Piper voci alternative, VITS/VITS2 italiano, Coqui TTS)
   - Pro: offline, bassa latenza, gratis
   - Con: qualità variabile, setup complesso
   - Valuta: voci italiane disponibili, qualità vs Piper Paola

3. **Motori Locali Python 3.9-compatible** (gTTS online, pyttsx3, edge-tts)
   - Pro: facile integrazione
   - Con: qualità variabile
   - Valuta: edge-tts usa le voci Microsoft gratuitamente?

4. **Soluzioni ibride** (API per prima frase + cache + locale per ripetizioni)

### Output Atteso TTS

Una tabella comparativa DEFINITIVA con:
```
| Motore | Py3.9 | Qualità IT | Latenza | Offline | Costo | Integrazione |
|--------|-------|-----------|---------|---------|-------|-------------|
```

E per il TOP 3 candidati:
- Codice Python completo di integrazione (async, aiohttp-compatible)
- Istruzioni di setup
- Stima costi mensili per ~10.000 frasi
- Sample di codice per test rapido

---

## Output Atteso Complessivo

### Sezione 1: Bug Fix (per ogni bug)
```python
# BUG N: [descrizione]
# File: [path]
# Riga: [numero]

# PRIMA (codice buggato):
...

# DOPO (codice corretto):
...

# TEST:
def test_bug_N_fix():
    ...
```

### Sezione 2: TTS Comparison Matrix
Tabella + codice di integrazione per top 3

### Sezione 3: Piano di Release
Ordine di implementazione, rischi, test checklist per v1.0

## Note Importanti

- Il codice deve funzionare su **Python 3.9.6** senza eccezioni
- Non proporre soluzioni che richiedono PyTorch, Python 3.10+, o GPU
- I fix devono essere **patch chirurgici** — non riscrivere la state machine
- Per il TTS, privilegia **qualità voce italiana** sopra tutto il resto
- La release v1.0 è imminente — servono soluzioni pronte, non prototipi
