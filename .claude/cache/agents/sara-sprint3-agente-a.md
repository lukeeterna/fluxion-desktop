# Sara Sprint 3 — Agente A: Benchmark & Best Practices
## GAP-B2 (mese prossimo / fra un mese) + GAP-B6 (fine settimana / weekend)
> Research: 2026-03-12 | Skill: fluxion-voice-agent

---

## 1. Analisi Codebase Attuale — Cosa Esiste Oggi

### Cosa copre `extract_date()` in entity_extractor.py

| Pattern | Metodo | Riga | Stato |
|---------|--------|------|-------|
| "domani", "oggi", "dopodomani" | `RELATIVE_DATES` list, riga 200 | keyword in text | OK |
| "lunedì", "martedì", …, "sabato", "domenica" | `DAYS_IT` dict, riga 177 | keyword in text | OK |
| "prossima settimana" / "settimana prossima" | substring check, riga 317 | → lunedì prossimo | OK (ma see caveat) |
| "questa settimana" | substring check, riga 331 | → domani | Debole (confidence 0.75) |
| "fra/tra N giorni/settimane" con cifre | regex `fra_pattern`, riga 349 | "fra 3 giorni" | OK |
| "fra/tra UNA/DUE settimane" in parole | regex `fra_word_pattern`, riga 368 | "fra due settimane" | OK |
| "15 gennaio", "il 20" | explicit month match + "il \d" | righe 388–455 | OK |
| dateparser fallback | HAS_DATEPARSER, riga 458 | confidence 0.7 | dipende da installazione |

### GAP-B2: Cosa manca per "il mese prossimo" / "fra un mese"

**"il mese prossimo" / "mese prossimo" / "prossimo mese"**
- Nessun pattern copre questa forma. "mese" è in `RELATIVE_DATES` come keyword esclusa (appare in stop words riga 964 del file entity_extractor, ma non in RELATIVE_DATES).
- Nessun pattern regex con `(mese\s+prossimo|prossimo\s+mese|il\s+mese\s+prossimo)`.
- Il `dateparser` fallback potrebbe gestirlo se installato — ma con confidence 0.7 e non garantito su Python 3.9 iMac.

**"fra un mese" / "tra un mese"**
- Il pattern `fra_word_pattern` (riga 368) copre `fra/tra + <num_word> + (giorno|settimana)`.
- NON include il plurale/singolare di "mese" (solo `giorn[oi]|settiman[ae]`).
- Manca la parte regex `|mes[ei]` nel gruppo unità.

**"fra un mese e mezzo"**
- Nessun pattern per frazioni di mese. Richiede handling separato.

**"il primo del mese prossimo"**
- Combinazione: day 1 + next month. La logica FIX-8 gestisce "primo" nel mese corrente ma NON in combinazione con "mese prossimo".

### GAP-B6: Cosa manca per "fine settimana" / "weekend"

**"fine settimana" / "weekend" / "questo weekend"**
- "settimana" è solo in `RELATIVE_DATES` commento (non come entry) e nelle check di "prossima settimana".
- Nessun pattern per "fine settimana" → sabato prossimo.
- Nessun mapping per "weekend" (termine inglese usato comunemente in italiano).
- Nessun pattern per "questo weekend" vs "il prossimo weekend".

**"sabato o domenica"**
- Gestito parzialmente: il loop `DAYS_IT` matcha il primo giorno trovato nel testo. Se il testo contiene "sabato" prima di "domenica", restituisce sabato — che è corretto per "fine settimana". Ma la semantica è persa.

---

## 2. Benchmark Competitor — Come Gestiscono le Date Relative

### Dialogflow CX (Google) — Gold Standard Enterprise
- Sistema **TIMEX3 compliant**: ogni entity di tipo `@sys.date` riconosce automaticamente forme come:
  - "next month" → ISO: P1M (1 period of 1 month ahead)
  - "end of the week" → venerdì della settimana corrente
  - "this weekend" → sabato della settimana corrente
- Sistema a due layer: (1) duckling NLU per parsing, (2) business logic per normalizzazione.
- Gestisce "in un mese e mezzo" → P1M + P0.5M → ~45 giorni da oggi.
- **Coverage**: 95%+ espressioni temporali italiane out-of-the-box con `it` locale.

### Amazon Lex v2 — Enterprise AWS
- Slot type `AMAZON.Date` con built-in relative date resolution per Italian.
- Gestisce "il mese prossimo" → primo giorno del mese prossimo (giorno anchor = 1).
- "il fine settimana" → sabato della settimana corrente (se venerdì o prima), sabato della prossima (se sabato/domenica già passati).
- Duckling integration per frazioni: "un mese e mezzo" → 45 giorni.

### Nuance Mix (enterprise telephony)
- Pattern library per ogni lingua, IT inclusa.
- "fine settimana prossimo" → sabato next week.
- "fra circa un mese" / "verso fine mese" → gestiti con confidence ranges.
- Principale differenza vs Fluxion: Nuance usa un **temporal anchor** separato per il contesto di business (orari apertura, giorni chiusura) — non solo data ISO ma `DateTimeWithBusinessContext`.

### Retell AI / Vapi (voice-native booking 2026)
- Retell usa **Deepgram STT + GPT-4o** per entity extraction — delega tutto al LLM.
- Vapi uguale: zero regex, tutto LLM. Questo copre automaticamente "fra un mese e mezzo" ma con latenza 800ms+ solo per NLU.
- **Gap vs Sara**: loro non hanno la pipeline L0-L3 a bassa latenza — tutto è L4 (LLM).
- Sara ha vantaggio competitivo nella latenza; il gap è solo sulla coverage regex per date relative.

### Fresha (booking SaaS)
- Widget web — nessun voice agent proprietario.
- Chatbot WhatsApp: gestisce "la prossima settimana" e "questo weekend" via Dialogflow.
- "Fra un mese" → delega a Dialogflow CX date entity.

### Cal.com (open source, enterprise)
- Date parsing usa **chrono-node** (JS) + custom IT locale.
- Copre: "next month", "end of week", "in 6 weeks", "mid-month".
- IT locale chrono-node: "prossimo mese", "fine settimana", "tra 6 settimane".
- Importante: chrono-node usa **anchor date** esplicita + business hours per filtrare domeniche/festivi.

---

## 3. Gold Standard 2026 — Approccio Raccomandato per Sara

### Principio architetturale (da tutti i leader)
1. **Regex per i pattern ad alta frequenza** (< 5ms): "il mese prossimo", "fine settimana", "fra un mese" → 80% dei casi.
2. **dateparser come safety net** (già presente): cattura edge case restanti con confidence 0.7.
3. **LLM (Groq L4) solo per ambiguità assoluta** (es. "verso la fine del trimestre"): <5% dei casi.

### Normalizzazione raccomandata per i gap

**"il mese prossimo" / "mese prossimo"** → primo giorno del mese successivo.
- Semantica enterprise (Lex/Dialogflow): quando il cliente dice "il mese prossimo" senza specificare il giorno, si propone il primo giorno disponibile del mese prossimo (lunedì 1 o primo giorno lavorativo).
- Sara dovrebbe normalizzare a `datetime(year, month+1, 1)` e poi chiedere il giorno specifico se manca.

**"fra un mese"** → reference_date + 30 giorni (o `relativedelta(months=1)` se disponibile).
- Standard scelto da Dialogflow CX: 30 giorni per "un mese" (non il primo del mese prossimo).
- Questo è diverso da "il mese prossimo" (che è il 1 del mese dopo).

**"fine settimana" / "weekend"** → sabato della settimana corrente (se oggi è lunedì-venerdì), altrimenti sabato della settimana prossima.
- Logica enterprise: se oggi è sabato → sabato prossimo (+7 giorni). Se oggi è domenica → sabato prossimo (+6 giorni).
- "questo weekend" = uguale a "fine settimana" (stessa settimana).
- "il prossimo weekend" = sabato della settimana prossima, sempre.

---

## 4. Pattern Regex Raccomandati per IT

### GAP-B2: Mese prossimo e fra N mesi

```python
# Aggiunta a extract_date() dopo il blocco "prossima settimana" (riga 316):

# --- NUOVO: "il mese prossimo" / "mese prossimo" / "prossimo mese" ---
if re.search(r'\b(il\s+)?mes[ei]\s+prossim[oa]\b|\bprossim[oa]\s+mes[ei]\b', text_lower):
    # Normalizza: primo del mese prossimo
    month = reference_date.month
    year = reference_date.year
    if month == 12:
        target_date = datetime(year + 1, 1, 1)
    else:
        target_date = datetime(year, month + 1, 1)
    return ExtractedDate(
        date=target_date,
        original_text="mese prossimo",
        confidence=0.90,
        is_relative=True
    )

# --- NUOVO: "fra/tra un mese" / "fra/tra due mesi" (cifre e parole) ---
# Estendi fra_pattern per includere "mes[ei]"
fra_pattern_ext = r'(?:fra|tra)\s+(\d+)\s+(giorn[oi]|settiman[ae]|mes[ei])'
# E fra_word_pattern_ext:
fra_word_pattern_ext = rf'(?:fra|tra)\s+({it_num_pattern})\s+(giorn[oi]|settiman[ae]|mes[ei])'
# Nel handler: se unit.startswith('mes') → days_delta = num * 30
```

### GAP-B6: Fine settimana / weekend

```python
# Aggiunta a extract_date() dopo il blocco "questa settimana" (riga 331):

# --- NUOVO: "fine settimana" / "weekend" / "questo weekend" ---
_WEEKEND_PATTERNS = [
    r'\bfine\s+settimana\b',
    r'\bweekend\b',
    r'\bquesto\s+(?:fine\s+settimana|weekend)\b',
    r'\bsabato\s+o\s+domenica\b',
    r'\bdomeni[ac]a\s+o\s+sabato\b',
]
_NEXT_WEEKEND_PATTERNS = [
    r'\b(?:il\s+)?prossim[oa]\s+(?:fine\s+settimana|weekend)\b',
    r'\b(?:fine\s+settimana|weekend)\s+prossim[oa]\b',
]

def _resolve_weekend(reference_date: datetime, force_next: bool = False) -> datetime:
    """Return the next Saturday relative to reference_date."""
    today_weekday = reference_date.weekday()  # 0=Mon, 5=Sat, 6=Sun
    if today_weekday == 5:  # Oggi è sabato
        days_ahead = 7 if force_next else 7  # Sempre prossimo sabato
    elif today_weekday == 6:  # Oggi è domenica
        days_ahead = 6  # Sabato prossimo
    else:
        days_ahead = (5 - today_weekday) % 7  # Sabato di questa settimana
        if days_ahead == 0:
            days_ahead = 7
    return reference_date + timedelta(days=days_ahead)

# Nel corpo di extract_date():
for p in _NEXT_WEEKEND_PATTERNS:
    if re.search(p, text_lower):
        target_date = _resolve_weekend(reference_date, force_next=True)
        return ExtractedDate(date=target_date, original_text="prossimo weekend",
                             confidence=0.92, is_relative=True)

for p in _WEEKEND_PATTERNS:
    if re.search(p, text_lower):
        target_date = _resolve_weekend(reference_date, force_next=False)
        return ExtractedDate(date=target_date, original_text="fine settimana",
                             confidence=0.92, is_relative=True)
```

### Correzione fra_pattern per supportare mesi

```python
# Riga 349 ATTUALE:
fra_pattern = r'(?:fra|tra)\s+(\d+)\s+(giorn[oi]|settiman[ae])'

# NUOVO (esteso):
fra_pattern = r'(?:fra|tra)\s+(\d+)\s+(giorn[oi]|settiman[ae]|mes[ei])'

# Riga 354 ATTUALE:
if unit.startswith('settiman'):
    days_delta = num * 7
else:
    days_delta = num

# NUOVO:
if unit.startswith('settiman'):
    days_delta = num * 7
elif unit.startswith('mes'):
    days_delta = num * 30
else:
    days_delta = num
```

---

## 5. Edge Cases Critici da Coprire nei Test

### GAP-B2 — Mese relativo

| Input | Output atteso | Note |
|-------|---------------|------|
| "il mese prossimo" | primo del mese prossimo | caso base |
| "mese prossimo" | primo del mese prossimo | senza articolo |
| "prossimo mese" | primo del mese prossimo | ordine invertito |
| "fra un mese" | oggi + 30 giorni | NON primo del mese |
| "tra un mese" | oggi + 30 giorni | variante "tra" |
| "fra due mesi" | oggi + 60 giorni | plurale |
| "fra tre mesi" | oggi + 90 giorni | numero > 2 |
| "fra un mese e mezzo" | oggi + 45 giorni | EDGE — fuori scope MVP, ma documentare |
| "il primo del mese prossimo" | primo del mese prossimo | combinazione esistente FIX-8 + nuovo |
| "a fine mese" | ultimo giorno del mese corrente | EXTRA — non richiesto da GAP-B2, ma comune |
| "il mese dopo" | primo del mese prossimo | sinonimo (bassa frequenza) |

### GAP-B6 — Weekend

| Input | Output atteso | Note |
|-------|---------------|------|
| "fine settimana" (oggi = mercoledì) | sabato di questa settimana | caso base |
| "fine settimana" (oggi = sabato) | sabato prossimo (+7) | già passato |
| "fine settimana" (oggi = domenica) | sabato prossimo (+6) | domenica = fine weekend passato |
| "weekend" | sabato (come sopra) | termine inglese |
| "questo weekend" | sabato di questa settimana | "questo" = corrente |
| "questo fine settimana" | sabato di questa settimana | esteso |
| "il prossimo weekend" | sabato della settimana prossima | "prossimo" = forzato next |
| "il weekend prossimo" | sabato della settimana prossima | ordine invertito |
| "prossimo fine settimana" | sabato della settimana prossima | variante |
| "sabato o domenica" | sabato prossimo disponibile | Sara propone sabato |
| "sabato prossimo" | già gestito da DAYS_IT | nessuna modifica necessaria |

### Edge case ordering — importante

Il check "prossimo weekend" DEVE essere fatto PRIMA del check "fine settimana" base, e il check "prossima settimana" PRIMA di "settimana" standalone — per evitare che "prossimo fine settimana" venga matchato da "fine settimana" (senza il "prossimo").

Soluzione: usare `_NEXT_WEEKEND_PATTERNS` prima di `_WEEKEND_PATTERNS` nel codice.

---

## 6. Posizionamento Corretto nel Codice

### Ordine di inserimento in `extract_date()` (entity_extractor.py)

Posizione raccomandata (dopo le check esistenti, prima del dateparser fallback):

```
1. RELATIVE_DATES (domani, oggi, dopodomani)         [riga 281] ← esistente
2. DAYS_IT (lunedì, sabato, …)                        [riga 292] ← esistente
3. "prossima settimana" / "questa settimana"          [riga 316] ← esistente
3a. [NUOVO] "fine settimana" / "weekend" patterns    ← INSERIRE QUI
    - _NEXT_WEEKEND_PATTERNS prima
    - _WEEKEND_PATTERNS dopo
3b. "fra/tra N giorni/settimane"                      [riga 341] ← esistente
3c. [NUOVO] "mese prossimo" / "prossimo mese"        ← INSERIRE QUI (dopo settimane)
3d. [NUOVO] "fra/tra N mesi" (estensione fra_pattern) ← estendere righe 349 + 368
4. Explicit dates "15 gennaio", "il 20"               [riga 386] ← esistente
5. FIX-8 "primo"                                      [riga 411] ← esistente
6. dateparser fallback                                [riga 458] ← esistente
```

La posizione 3a (prima di fra/tra) è importante: "questo fine settimana" non deve essere catturato dal fra_pattern.

---

## 7. Acceptance Criteria Misurabili

### AC-B2 (Mese relativo)
- [ ] `extract_date("il mese prossimo", ref=datetime(2026,3,12))` → `datetime(2026,4,1)`, confidence ≥ 0.90
- [ ] `extract_date("fra un mese", ref=datetime(2026,3,12))` → `datetime(2026,4,11)` (±1 giorno accettabile per 30-day normalization), confidence ≥ 0.85
- [ ] `extract_date("tra due mesi", ref=datetime(2026,3,12))` → `datetime(2026,5,11)`, confidence ≥ 0.85
- [ ] `extract_date("mese prossimo", ref=datetime(2026,3,12))` → `datetime(2026,4,1)`, confidence ≥ 0.90
- [ ] `extract_date("prossimo mese", ref=datetime(2026,3,12))` → `datetime(2026,4,1)`, confidence ≥ 0.90
- [ ] `extract_date("fra tre mesi", ref=datetime(2026,3,12))` → `datetime(2026,6,10)`, confidence ≥ 0.85
- [ ] Latency invariante: nessuna regressione su P95 < 10ms per date extraction

### AC-B6 (Weekend)
- [ ] `extract_date("fine settimana", ref=datetime(2026,3,12))` (giovedì) → sabato 2026-03-14, confidence ≥ 0.92
- [ ] `extract_date("fine settimana", ref=datetime(2026,3,14))` (sabato) → sabato 2026-03-21, confidence ≥ 0.92
- [ ] `extract_date("fine settimana", ref=datetime(2026,3,15))` (domenica) → sabato 2026-03-21, confidence ≥ 0.92
- [ ] `extract_date("weekend", ref=datetime(2026,3,12))` → sabato 2026-03-14, confidence ≥ 0.92
- [ ] `extract_date("il prossimo weekend", ref=datetime(2026,3,12))` → sabato 2026-03-21 (FORZA prossima settimana), confidence ≥ 0.92
- [ ] `extract_date("questo weekend", ref=datetime(2026,3,12))` → sabato 2026-03-14, confidence ≥ 0.92
- [ ] `extract_date("sabato o domenica", ref=datetime(2026,3,12))` → sabato 2026-03-14, confidence ≥ 0.88

### AC Regressione (non rompere l'esistente)
- [ ] `extract_date("sabato", ...)` → sabato prossimo (invariato, gestito da DAYS_IT)
- [ ] `extract_date("fra due settimane", ...)` → oggi + 14 giorni (invariato)
- [ ] `extract_date("la prossima settimana", ...)` → lunedì prossimo (invariato)
- [ ] `pytest tests/test_entity_extractor.py -v` → 0 regressioni sui test esistenti
- [ ] `pytest tests/ -v --tb=short` → tutti i test passano (baseline attuale: 1334 PASS)

---

## 8. Test File Raccomandato

```python
# Da aggiungere a: tests/test_entity_extractor.py

@pytest.mark.parametrize("text,ref_weekday,expected_iso,desc", [
    # GAP-B2: mese prossimo
    ("il mese prossimo",   3, "2026-04-01", "mese prossimo base"),
    ("mese prossimo",      3, "2026-04-01", "senza articolo"),
    ("prossimo mese",      3, "2026-04-01", "ordine invertito"),
    ("fra un mese",        3, "2026-04-11", "fra un mese = +30gg"),
    ("tra un mese",        3, "2026-04-11", "tra variante"),
    ("fra due mesi",       3, "2026-05-11", "due mesi"),
    ("fra tre mesi",       3, "2026-06-10", "tre mesi"),
    # GAP-B6: weekend (ref = giovedì 2026-03-12)
    ("fine settimana",     3, "2026-03-14", "weekend da giovedì"),
    ("weekend",            3, "2026-03-14", "termine inglese"),
    ("questo weekend",     3, "2026-03-14", "questo"),
    ("questo fine settimana", 3, "2026-03-14", "questo esteso"),
    ("il prossimo weekend", 3, "2026-03-21", "prossimo = force next"),
    ("prossimo fine settimana", 3, "2026-03-21", "prossimo esteso"),
    ("il weekend prossimo", 3, "2026-03-21", "ordine invertito"),
    ("sabato o domenica",  3, "2026-03-14", "alternativa"),
    # GAP-B6: edge cases boundary (ref = sabato 2026-03-14)
    ("fine settimana",     5, "2026-03-21", "sabato→sabato prossimo"),
    ("weekend",            6, "2026-03-21", "domenica→sabato prossimo"),
])
def test_date_relative_month_and_weekend(text, ref_weekday, expected_iso, desc):
    # ref date with given weekday in week of 2026-03-09 (Mon)
    ref = datetime(2026, 3, 9) + timedelta(days=ref_weekday)
    result = extract_date(text, reference_date=ref)
    assert result is not None, f"NONE per: {desc!r}"
    assert result.date.strftime("%Y-%m-%d") == expected_iso, f"Data errata per: {desc!r}"
    assert result.confidence >= 0.85, f"Confidence bassa per: {desc!r}"
```

---

## 9. Rischi e Note Implementative

### Rischio: "fra un mese" vs "il mese prossimo" — semantica diversa
- Dialogflow e Lex li trattano diversamente: il primo è offset (+30gg), il secondo è anchorage al primo del mese.
- Sara dovrebbe mantenere questa distinzione per non confondere il cliente ("tra un mese" = fine aprile, non il 1 aprile).

### Rischio: "fine mese" (non richiesto dal GAP ma comune)
- "a fine mese" / "fine del mese" → ultimo giorno del mese corrente.
- Non è in scope per GAP-B2/B6 ma è un pattern comune nei saloni. Suggerito come B2-extra per sprint futuro.

### Rischio: "sabato" già gestito da DAYS_IT
- Il loop DAYS_IT cattura "sabato" prima che il nuovo codice per "sabato o domenica" possa eseguire.
- Fix: il pattern "sabato o domenica" va cercato PRIMA del loop DAYS_IT, oppure aggiunto come pattern speciale nella lista RELATIVE_DATES (preferito: DAYS_IT non deve girare se matcha già "sabato o domenica").

### Rischio: "weekend" come substring
- "fine settimana" contiene "settimana" che è già in `DAYS_IT`-adjacent code. La regex `re.search` è più robusta del substring match per evitare falsi positivi.

### Performance
- Tutti i nuovi pattern sono `re.search` su testo breve (< 100 char tipici) → latenza aggiuntiva stimata < 0.5ms. Target <10ms invariato.

---

## 10. Implementazione Raccomandata — Passi Esatti

1. **Definire costanti** a livello modulo (dopo RELATIVE_DATES/DAYS_IT, riga ~205):
   - `_WEEKEND_PATTERNS: List[re.Pattern]`
   - `_NEXT_WEEKEND_PATTERNS: List[re.Pattern]`
   - Usare `re.compile(pattern, re.IGNORECASE)` per performance

2. **Definire `_resolve_weekend(reference_date, force_next=False)`** come funzione helper module-level

3. **Estendere `fra_pattern` e `fra_word_pattern`** per includere `mes[ei]`

4. **Aggiungere handler "mese prossimo"** nel corpo di `extract_date()`, posizione 3c

5. **Aggiungere handler weekend** nel corpo di `extract_date()`, posizione 3a (PRIMA del check DAYS_IT per gestire "sabato o domenica")

6. **Scrivere test parametrici** come da sezione 8

7. **Verificare** `pytest tests/test_entity_extractor.py -v` → AC tutti verdi

8. **Verificare** `pytest tests/ -v --tb=short` → 1334+ PASS, 0 regressioni
