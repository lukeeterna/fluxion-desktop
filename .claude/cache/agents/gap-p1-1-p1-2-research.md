# GAP-P1-1 + GAP-P1-2 — Research CoVe 2026
> Agente B — Analisi codebase + gold standard mondiale
> Data: 2026-03-13 | Sprint 5

---

## Contesto Codebase Attuale

**File**: `voice-agent/src/entity_extractor.py`

### Stato attuale `extract_phone()` (riga 1470)

**Pattern correnti**:
```python
r'(?<!\d)(?:\+39[-.\s]?)?3\d{2}[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)'  # Mobile: 333 123 4567
r'(?<!\d)(?:\+39[-.\s]?)?0\d{1,3}[-.\s]?\d{6,8}(?!\d)'           # Landline
```

**`_is_valid_mobile()` — validazione prefisso**:
```python
bare = digits.lstrip('+')
if bare.startswith('0039'):
    bare = bare[4:]
elif bare.startswith('39') and len(bare) > 11:
    bare = bare[2:]
```

**Gap identificati**:
1. Il pattern regex NON matcha `0039 333 1234567` — il prefisso `0039` non è nell'alternanza `(?:\+39[-.\s]?)?`
2. Il pattern NON matcha `39 345 6789012` (senza `+` né `00`) perché la parte mobile richiede `3\d{2}...`
3. `_strip_prefix()` nel Whisper normalizer controlla `len(s) > 11` ma un numero come `393331234567` (12 cifre) funziona, mentre `39345678901` (11 cifre) NON viene stripped
4. `_is_valid_mobile()` gestisce `0039` ma il pattern regex non matcha mai tali formati

### Stato attuale `extract_email()` (riga 1526)

**Pattern corrente**:
```python
pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
match = re.search(pattern, text)
```

**Gap identificati**:
1. `re.search()` trova il PRIMO match nel testo — se viene prima `support@azienda.it` viene estratto quello invece di `mario@gmail.com`
2. Nessuna prioritizzazione keyword (`email`, `mail`, `la mia è`, etc.)
3. Nessuna gestione di STT artifacts (`chiocciola`, `at`, `punto` espansi verbalmente)

---

## GAP-P1-1 — Phone International Formats

### Standard di Riferimento: E.164 + AGCOM Italia 2026

**ITU-T E.164** è lo standard mondiale per la rappresentazione dei numeri telefonici:
- Formato: `+[country_code][subscriber_number]`
- Italia country code: `39`
- Forma canonica E.164 Italia: `+393331234567`

**Allocazioni AGCOM (Autorità per le Garanzie nelle Comunicazioni) — numeri mobili italiani 2026**:
| Prefisso | Operatore | Note |
|----------|-----------|------|
| `31x`    | MVNO/Iliad | Iliad partita da 351 |
| `32x`    | Vodafone   | 320-329 |
| `33x`    | TIM        | 330-339 |
| `34x`    | Vodafone   | 340-349 |
| `34[6-9]`| Wind3/MVNO | |
| `35x`    | Iliad/MVNO | 351 Iliad |
| `36x`    | Fastweb/MVNO | |
| `37x`    | Vodafone/MVNO | |
| `38x`    | Wind3       | 380-389 |
| `39x`    | **RISERVATO** → NON è numero mobile (itinvece prefisso internazionale) |
| `3[1-8]` | ✅ tutti validi — 10 cifre totali |

**Lunghezza standard italiana**:
- Numeri mobili: **10 cifre** (es. `3331234567`)
- Con prefisso paese E.164: **12 cifre** (es. `393331234567`)
- Fissi: 9-11 cifre (esclusi dal voice agent per scelta progettuale)

### Varianti Input Vocale da Supportare

Whisper (STT) può restituire il prefisso internazionale in questi formati:
| Input STT | Esempio | Trattamento |
|-----------|---------|-------------|
| `+39XXXXXXXXXX` | `+393331234567` | Strip `+39` → `3331234567` |
| `+39 XXX XXXXXXX` | `+39 333 1234567` | Strip `+39` + strip spazi |
| `0039XXXXXXXXXX` | `0039333 1234567` | Strip `0039` → `3331234567` |
| `0039 XXX XXXXXXX` | `0039 333 1234567` | Strip `0039` + strip spazi |
| `39XXXXXXXXXX` | `393331234567` | Ambiguo: strip `39` solo se totale >10 cifre |
| `39 XXX XXXXXXX` | `39 333 1234567` | Come sopra |
| Bare 10 cifre | `3331234567` | Già supportato |
| Digit-by-digit | `"tre, tre, tre..."` | Già supportato (Whisper fallback) |

**Caso ambiguo `39XXXXXXXXXX`**: un numero come `393331234567` potrebbe essere:
- `39` (paese) + `3331234567` (mobile) → 10 cifre ✅
- Un numero che inizia con `393` (non assegnato AGCOM) → rigettare

**Regola di disambiguazione**: se stringa inizia con `39` E ha 12 cifre totali E le cifre 3-4 sono `3[1-8]` → strip `39`.

### Algoritmo di Normalizzazione Definitivo (stdlib Python 3.9)

```python
def _normalize_italian_phone(raw: str) -> Optional[str]:
    """
    Normalize Italian phone number to bare 10-digit mobile (no country code).

    Input: qualsiasi formato internazionale o bare
    Output: "3XXXXXXXXX" (10 cifre) oppure None se non valido

    Standard: AGCOM mobile allocation + ITU-T E.164 country 39
    """
    # 1. Strip tutto tranne cifre
    digits = re.sub(r'[^\d]', '', raw)

    if not digits:
        return None

    # 2. Strip prefisso paese
    # Ordine IMPORTANTE: 0039 prima di 39 per evitare doppio strip
    if digits.startswith('0039'):
        digits = digits[4:]
    elif digits.startswith('39') and len(digits) == 12 and digits[2] in '3':
        # 39 + 10-digit mobile: verifica che sia mobile AGCOM (3Xxx)
        candidate = digits[2:]
        if re.match(r'^3[1-9]\d{8}$', candidate):
            digits = candidate

    # 3. Validazione mobile AGCOM: 10 cifre, inizia con 3[1-8]
    if re.match(r'^3[1-8]\d{8}$', digits):
        return digits

    # 4. Fallback: accetta 9 cifre (alcuni numeri storici)
    if re.match(r'^3[1-8]\d{7}$', digits):
        return digits

    return None
```

### Pattern Regex Unificato per `extract_phone()`

Il pattern attuale copre solo `(?:\+39[-.\s]?)?` — non `0039`. Soluzione:

```python
# Gruppo prefisso esteso: +39 | 0039 | 39 (opzionale)
PREFIX = r'(?:(?:\+|00)?39[-.\s]?)?'

# Corpo mobile italiano: 3XX XXX XXXX (vari separatori)
MOBILE_BODY = r'3[1-8]\d[-.\s]?\d{3}[-.\s]?\d{4}'

# Pattern completo con word boundaries
PATTERN_MOBILE = rf'(?<!\d){PREFIX}({MOBILE_BODY})(?!\d)'
```

**Nota**: il pattern deve essere `(?:(?:\+|00)?39[-.\s]?)?` per catturare:
- `+39` (più internazionale)
- `0039` (zero-zero-39, standard europeo rete fissa)
- `39` (bare, senza simbolo)
- `` (assente, bare mobile)

---

## GAP-P1-2 — Email Keyword Priority Extraction

### Standard di Riferimento: RFC 5321 + NLP Entity Anchoring 2026

**RFC 5321 (SMTP)** + **RFC 5322 (Message Format)** definiscono il formato email valido. Per uso pratico (NLU vocale), le librerie world-class (Google NLP, AWS Comprehend, Nuance Mix) usano un subset sicuro:

```
local-part = 1*63(ALPHA / DIGIT / "." / "_" / "%" / "+" / "-")
"@"
domain = 1*(subdomain ".")TLD
TLD = 2*63(ALPHA)
```

Lunghezza totale: max 254 char (RFC 5321 §4.5.3.1.3).

**Regola RFC critical per STT**: il carattere `@` viene detto vocalmente in italiano come:
- `chiocciola` (formale)
- `at` (anglicismo comune)
- `commerciale a` (rarissimo)

### Problema Keyword Priority

Il gold standard per l'entity anchoring NLU (Google Dialogflow CX, Rasa 3.x, Nuance Mix) usa il pattern **"keyword-anchored NER"**: quando un'entità è preceduta da un anchor keyword, ha precedenza sulle altre occorrenze.

**Scenario tipico in voice booking**:
> "Potete scrivere a info@salone.it, la mia mail personale è mario.rossi@gmail.com"

`re.search()` restituisce `info@salone.it` (prima occorrenza) invece di `mario.rossi@gmail.com`.

**Anchor keywords italiane per email (ordinate per priorità)**:
1. `la mia email è` / `la mia mail è` / `la mia e-mail è`
2. `email è` / `mail è` / `e-mail è`
3. `indirizzo email` / `indirizzo mail`
4. `mia email` / `mia mail`
5. `scrivi a` (bassa priorità — può essere indirizzo aziendale)

### Algoritmo di Estrazione con Priority Anchoring

```python
# Regex email RFC-safe per STT (Python 3.9 stdlib)
EMAIL_RFC_PATTERN = r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]{0,62}@[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,63}'

# Keywords anchor ordinate per priorità (alta → bassa)
EMAIL_ANCHOR_KEYWORDS = [
    r'(?:la\s+mia\s+)?(?:e[_-]?mail|mail)\s+(?:è|e|personale\s+è)',
    r'indirizzo\s+(?:e[_-]?mail|mail)\s+(?:è|e)',
    r'(?:e[_-]?mail|mail)\s+(?:è|e)',
    r'mia\s+(?:e[_-]?mail|mail)',
]

def extract_email_with_priority(text: str) -> Optional[str]:
    text_lower = text.lower()

    # 1. Cerca email post-keyword (priority anchoring)
    for anchor_pattern in EMAIL_ANCHOR_KEYWORDS:
        anchor_match = re.search(anchor_pattern, text_lower)
        if anchor_match:
            # Cerca email nel testo DOPO l'anchor
            post_anchor = text[anchor_match.end():]
            email_match = re.search(EMAIL_RFC_PATTERN, post_anchor, re.IGNORECASE)
            if email_match:
                candidate = email_match.group(0).lower()
                if _validate_email(candidate):
                    return candidate

    # 2. Fallback: prima email nel testo (comportamento attuale)
    email_match = re.search(EMAIL_RFC_PATTERN, text, re.IGNORECASE)
    if email_match:
        candidate = email_match.group(0).lower()
        if _validate_email(candidate):
            return candidate

    return None
```

### Gestione STT Artifacts per Email

Whisper può trascrivere la `@` come parola e il `.` come "punto":

| STT output | Normalizzazione |
|------------|-----------------|
| `mario chiocciola gmail punto com` | `mario@gmail.com` |
| `mario at gmail punto com` | `mario@gmail.com` |
| `mario chiocciola gmail.com` | `mario@gmail.com` |
| `mario at gmail.com` | `mario@gmail.com` |

**Pre-processing per STT artifacts** (da applicare prima del regex):
```python
def _normalize_stt_email(text: str) -> str:
    """Expand STT verbal artifacts to email symbols."""
    t = text.lower()
    # @ variants
    t = re.sub(r'\bchiocciola\b', '@', t)
    t = re.sub(r'\b(?<!\w)at(?!\w)\b', '@', t)  # "at" standalone solo
    t = re.sub(r'\bcommerciale\s+a\b', '@', t)
    # . variants (solo in contesto email: tra lettere)
    t = re.sub(r'(?<=[a-z0-9])\s+punto\s+(?=[a-z])', '.', t)
    return t
```

---

## Test Cases

### GAP-P1-1 — Phone Test Cases (15 casi)

```python
PHONE_INTL_TEST_CASES = [
    # FORMAT: (input_text, expected_normalized_digits)

    # --- Formati 0039 (NUOVI - attualmente rotti) ---
    ("0039 333 1234567", "3331234567"),
    ("0039333 1234567", "3331234567"),
    ("00393331234567", "3331234567"),
    ("il mio numero è 0039 345 678 9012", "3456789012"),

    # --- Formato 39 senza simbolo (NUOVI - parzialmente rotti) ---
    ("39 345 6789012", "3456789012"),
    ("393456789012", "3456789012"),

    # --- Formato +39 (esistente, non rompere) ---
    ("+39 333 1234567", "+393331234567"),  # ← comportamento attuale (mantiene +39)
    ("+39333 123 4567", "+393331234567"),

    # --- Bare mobile (esistente, non rompere) ---
    ("333 123 4567", "3331234567"),
    ("3331234567", "3331234567"),

    # --- Varianti spazi estreme ---
    ("+39 3 45 12 34 56 7", "+393451234567"),  # Digit-by-digit con prefisso
    ("0039 3 45 12 34 56 7", "3451234567"),

    # --- AGCOM range mobili (verifica non-landline) ---
    ("il numero è 3451234567", "3451234567"),   # Vodafone range 34x
    ("chiamami al 3801234567", "3801234567"),   # Wind3 range 38x

    # --- Negative cases (deve restituire None) ---
    ("0039 021234567", None),      # 0039 + fisso (deve restituire None)
    ("39 021234567", None),        # 39 + fisso
    ("00390000000000", None),      # 0039 + numero non valido
]
```

**Nota sulla normalizzazione output**: il comportamento attuale mantiene il `+` nei numeri `+39XXX...`. Per coerenza con le future integrazioni WhatsApp (che richiedono formato E.164 con `+`), si raccomanda di normalizzare tutto a:
- **Opzione A**: bare 10 cifre `3XXXXXXXXX` (formato attuale per bare)
- **Opzione B**: E.164 `+39XXXXXXXXX` (formato WA, internazionale)

La raccomandazione è **Opzione A** (bare 10 cifre) per il voice agent, e conversione a E.164 solo al momento dell'invio WA (già gestita da `whatsapp_client.normalize_phone()`).

### GAP-P1-2 — Email Test Cases (12 casi)

```python
EMAIL_PRIORITY_TEST_CASES = [
    # FORMAT: (input_text, expected_email)

    # --- Priority keyword anchoring (NUOVI - attualmente rotti) ---
    (
        "scrivi a support@azienda.it, la mia email è mario@gmail.com",
        "mario@gmail.com"   # ← keyword "email è" ha priorità
    ),
    (
        "contatti: info@salone.it - la mia mail è luigi.bianchi@hotmail.it",
        "luigi.bianchi@hotmail.it"
    ),
    (
        "l'indirizzo email è anna.verdi@libero.it",
        "anna.verdi@libero.it"
    ),
    (
        "per comunicazioni ufficio@studio.it, ma la mia e-mail è personal@gmail.com",
        "personal@gmail.com"
    ),
    (
        "mia mail: mario@email.it",
        "mario@email.it"
    ),

    # --- STT artifacts (NUOVI) ---
    (
        "la mia email è mario chiocciola gmail punto com",
        "mario@gmail.com"
    ),
    (
        "scrivi a mario at gmail.com",
        "mario@gmail.com"
    ),

    # --- Comportamento attuale da non rompere ---
    ("la mia email è mario@email.com", "mario@email.com"),
    ("contattami a test.user@domain.it", "test.user@domain.it"),
    ("MARIO@GMAIL.COM", "mario@gmail.com"),

    # --- Validation (nessun email valido → None) ---
    ("scrivi a support@azienda", None),     # no TLD
    ("email: test..user@gmail.com", None),  # consecutive dots

    # --- TLD italiani speciali ---
    ("la mail è mario@azienda.it", "mario@azienda.it"),
    ("email: info@studio.legal", "info@studio.legal"),   # TLD .legal
]
```

---

## Acceptance Criteria Misurabili

### GAP-P1-1 Phone Normalization

| # | Criterio | Metrica | Target |
|---|----------|---------|--------|
| AC-P1 | `0039XXXXXXXXXX` normalizzato a bare 10 cifre | Test case "0039 333 1234567" | ✅ `3331234567` |
| AC-P2 | `0039 XXX XXXXXXX` normalizzato (spazi) | Test case "0039 345 678 9012" | ✅ `3456789012` |
| AC-P3 | `39XXXXXXXXXX` (senza + né 00) normalizzato | Test case "39 345 6789012" | ✅ `3456789012` |
| AC-P4 | `+39 XXX XXXXXXX` non rotto (backward compat) | Test case "+39 333 1234567" | Comportamento invariato |
| AC-P5 | Bare mobile non rotto | Test case "333 123 4567" | ✅ `3331234567` |
| AC-P6 | `0039` + fisso → None | Test case "0039 021234567" | ✅ `None` |
| AC-P7 | Tutti 15 test cases passano | `pytest test_entity_extractor.py::TestPhoneExtraction` | 15/15 PASS |

### GAP-P1-2 Email Priority Extraction

| # | Criterio | Metrica | Target |
|---|----------|---------|--------|
| AC-E1 | Keyword "email è" post-anchor prioritizzato | Test case multi-email | ✅ priorità corretta |
| AC-E2 | Keyword "mail è" post-anchor prioritizzato | Test case "la mia mail è" | ✅ priorità corretta |
| AC-E3 | Keyword "indirizzo email" post-anchor | Test case "l'indirizzo email è" | ✅ |
| AC-E4 | STT `chiocciola` → `@` | Test case "mario chiocciola gmail punto com" | ✅ `mario@gmail.com` |
| AC-E5 | STT `at` standalone → `@` | Test case "mario at gmail.com" | ✅ `mario@gmail.com` |
| AC-E6 | Fallback senza keyword: prima email | Comportamento attuale | ✅ non rotto |
| AC-E7 | Validazione RFC (consecutive dots, TLD) | Test case "test..user@gmail.com" | ✅ `None` |
| AC-E8 | Tutti 12 test cases passano | `pytest test_entity_extractor.py::TestEmailExtraction` | 12/12 PASS |

---

## Raccomandazioni Implementative

### Ordine di Modifica Suggerito

**1. Modifica `extract_phone()`** — minima invasività:

Estendi il pattern regex aggiungendo `0039` nell'alternanza del prefisso:
```python
# BEFORE
r'(?<!\d)(?:\+39[-.\s]?)?3\d{2}[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)'

# AFTER
r'(?<!\d)(?:(?:\+|00)?39[-.\s]?)?3[1-8]\d[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)'
```

Nota: `3[1-8]` restringe già ai range AGCOM (evita falsi positivi con `39x` non allocati).

Aggiungi anche normalizzazione in `_is_valid_mobile()`:
```python
def _is_valid_mobile(digits: str) -> bool:
    bare = digits.lstrip('+')
    if bare.startswith('0039'):
        bare = bare[4:]
    elif bare.startswith('39') and len(bare) >= 12:  # FIX: era > 11
        candidate = bare[2:]
        if re.match(r'^3[1-8]', candidate):
            bare = candidate
    if bare.startswith('0'):
        return False
    return 9 <= len(bare) <= 11  # FIX: era <= 12, mobile IT max 10 cifre
```

**2. Modifica `extract_email()`** — algoritmo priority anchoring:

Aggiungi pre-processing STT + keyword priority search PRIMA del fallback `re.search()`.
Mantieni la validazione esistente (consecutive dots, TLD) invariata.

**3. Aggiunta test cases** in `test_entity_extractor.py`:
- Aggiungi i 15 casi phone a `PHONE_TEST_CASES`
- Aggiungi i 12 casi email a `EMAIL_TEST_CASES`
- NON modificare test esistenti

### Rischi

| Rischio | Probabilità | Mitigazione |
|---------|-------------|-------------|
| Pattern `39XX` falsi positivi (es. "nel 2039 alle 3") | Media | Aggiungere word boundary `(?<!\d)` già presente |
| `at` keyword cattura "at" in nomi propri (es. "Contatti") | Bassa | Regex `\b(?<!\w)at(?!\w)\b` + contesto email necessario |
| STT artifact `.` come "punto" in testo non email | Bassa | Solo applica in contesto post-`@` o post-keyword email |
| Backward compat test "+39 333 1234567" → "+393331234567" | CERTA | Preservare comportamento: se inizia con `+39`, mantenere `+` nel risultato |

### Note su Dipendenze

- **Nessuna libreria esterna richiesta** — tutto stdlib `re` + Python 3.9
- `phonenumbers` (libphonenumber Python port) risolverebbe tutto con 2 righe ma è dipendenza esterna → scelta progettuale di escluderla è corretta per deployment offline
- Il pattern AGCOM `3[1-8]` è stabile: l'allocazione `39x` per numeri mobili non avverrà (prefisso internazionale riservato ITU)

---

## Riferimenti

- ITU-T E.164: https://www.itu.int/rec/T-REC-E.164/
- AGCOM Piano di Numerazione: https://www.agcom.it/piano-di-numerazione
- RFC 5321 SMTP: https://www.rfc-editor.org/rfc/rfc5321
- RFC 5322 Message Format: https://www.rfc-editor.org/rfc/rfc5322
- Google Dialogflow CX Entity Anchoring: https://cloud.google.com/dialogflow/cx/docs/concept/entity
- Rasa NLU Entity Roles: https://rasa.com/docs/rasa/nlu-training-data/#entity-roles-and-groups
- libphonenumber (Python port): https://github.com/daviddrysdale/python-phonenumbers
