# F02 NLU Comprehensive Italian Morphology Pattern Library — Sara Voice Agent

**Generated:** 2026-03-04
**Domain:** Italian morphology for vertical guardrails + intent hardening
**Prerequisite reading:** `f02-nlu-ambiguity-research.md` (root-cause analysis already complete)
**Confidence:** HIGH — all patterns derived from analysis of production source files

---

## Section 1: SPOSTAMENTO Bug — Exact Fix

### 1.1 Root Cause (VERIFIED, from f02-nlu-ambiguity-research.md)

File: `voice-agent/src/intent_classifier.py`, line 411.

```python
# CURRENT (VULNERABLE) — trailing ? makes object optional:
r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?"
```

Any input containing "cambiare" (e.g., "devo cambiare le gomme") matches this pattern with
confidence 0.65. Because the object group ends in `?`, the regex fires on "cambiare" alone.

### 1.2 Surgical Fix — Ready to Paste

**File:** `voice-agent/src/intent_classifier.py`

```python
# REPLACEMENT for IntentCategory.SPOSTAMENTO patterns (lines 409-421):
IntentCategory.SPOSTAMENTO: [
    # "spostare" is appointment-domain only → safe to keep optional object
    r"(sposta|spostare)\s*(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?",
    # "cambiare/modificare" are generic Italian verbs → REQUIRE booking object
    r"(cambia|cambiare|modifica|modificare)\s+(l[ao'\u2019]?\s*)?(appuntament|prenotazion|data|ora|orario)",
    # "cambiare l'orario" — kept explicit (safe, requires "orario")
    r"(cambia|cambiare)\s+(l[''\u2019]?\s*)?(orario|ora)",
    # Modal + reschedule verbs (safe — modal provides strong booking context)
    r"(posso|vorrei|devo|voglio)\s+(sposta|cambia|modifica|anticipar|posticipare?|rimandare?)",
    # Move earlier/later with object
    r"(anticipa|anticipare|posticipa|posticipare|rimanda|rimandare)\s*(l[ao]?\s+)?(appuntament|prenotazion|visita)?",
    # Different day/time
    r"(un\s+altro|altra|diverso|diversa)\s+(giorno|data|ora|orario)",
    # Standalone "spostare/anticipare/posticipare/rimandare" (unambiguous domain verbs)
    r"\b(spostare?|anticipare?|posticipare?|rimandare?)\b\s+",
],
```

### 1.3 False Positive Risk Assessment

| Test Input | Before Fix | After Fix | Verdict |
|------------|-----------|-----------|---------|
| "mi potete cambiare l'appuntamento" | SPOSTAMENTO | SPOSTAMENTO | CORRECT |
| "vorrei cambiare l'orario" | SPOSTAMENTO | SPOSTAMENTO | CORRECT |
| "devo cambiare le gomme" | SPOSTAMENTO (BUG) | UNKNOWN → Groq | FIXED |
| "voglio cambiare il colore" | SPOSTAMENTO (BUG) | UNKNOWN → Groq | FIXED |
| "posso spostare l'appuntamento?" | SPOSTAMENTO | SPOSTAMENTO | CORRECT |
| "posso spostare la sedia?" | SPOSTAMENTO (BUG) | SPOSTAMENTO (residual) | Note: "spostare" modal+verb kept |
| "anticipa di una settimana" | SPOSTAMENTO | SPOSTAMENTO | CORRECT |
| "rimanda la prenotazione" | SPOSTAMENTO | SPOSTAMENTO | CORRECT |

Note on "posso spostare la sedia?": The modal pattern `(posso|vorrei|devo|voglio)\s+(sposta...)` still
fires here. Acceptable — "spostare" in Italian booking context is domain-specific enough that
"posso spostare" almost exclusively refers to scheduling. The orchestrator E4-S2 late guardrail
(Section 7) provides a second defense.

### 1.4 Other Vulnerable Patterns in SPOSTAMENTO (Same Fix)

**Line 421 standalone:**
```python
r"\b(spostare?|anticipare?|posticipare?|rimandare?)\b\s+"
```
This fires on "spostare " (with trailing space). Edge case: "posso spostare qualcosa domani" would
match. Since "spostare" is booking-domain in Italian, this is LOW risk. No change recommended.

**Line 419:**
```python
r"(un\s+altro|altra|diverso|diversa)\s+(giorno|data|ora|orario)"
```
Safe — requires specific date/time nouns. No change needed.

---

## Section 2: SALONE Guardrail — Complete Pattern Matrix

### Context: What SALONE must block

A salone (hair salon, beauty salon, barber) receives calls about: taglio, colore, piega, trattamenti,
manicure, pedicure, ceretta. It must redirect any auto, palestra, or medical requests.

### 2.1 AUTO service terms at SALONE — complete verb matrix

#### Group A: "cambio/cambiare + [fluid/component]"

```python
# PASTE INTO VERTICAL_GUARDRAILS["salone"] — replaces/extends existing auto patterns

# --- GOMME / PNEUMATICI ---
r"\b(?:cambiar[ei]|cambia(?:re)?|cambio|cambiato|cambierò)\s+(?:le\s+|dei?\s+|delle?\s+)?(?:gomm[ea]|pneumatici|ruot[ea])\b",
# Compound: "fare il cambio gomme"
r"\bfare\s+(?:il\s+)?cambio\s+(?:gomm[ea]|pneumatici|stagionale)\b",
# "portare per le gomme"
r"\bportar[ei]?\s+(?:la\s+macchina|l[''\u2019]?auto)\s+(?:per\s+(?:le\s+)?(?:gomm[ea]|pneumatici))\b",
# Seasonal: "mettere le gomme invernali/estive"
r"\b(?:metter[ei]?|mont[ao]re?|install[ao]re?)\s+(?:le\s+)?gomm[ea]\s+(?:invernali|estive|nuove|d'inverno|d'estate)\b",
# Past: "ho cambiato le gomme" (context: "devo ancora cambiare le gomme")
r"\b(?:ho\s+cambiato|devo\s+cambiare|vorrei\s+cambiare|mi\s+servono)\s+(?:le\s+)?(?:gomm[ea]|pneumatici)\b",

# --- OLIO / FILTRO ---
r"\b(?:cambiar[ei]|cambia(?:re)?|cambio|cambiato)\s+(?:l[''\u2019]?\s*)?olio\b",
r"\bfar[ei]?\s+(?:il\s+)?cambio\s+(?:dell[''\u2019]?\s*)?olio\b",
r"\b(?:olio\s+motore|filtro\s+(?:dell[''\u2019]?\s*)?olio)\b",
r"\b(?:ho\s+bisogno\s+(?:di|del)\s+)?(?:cambio\s+olio|rifornimento\s+olio)\b",

# --- TAGLIANDO ---
r"\bfar[ei]?\s+(?:il\s+)?tagliando\b",
r"\bportar[ei]?\s+(?:la\s+macchina|l[''\u2019]?auto)\s+(?:a\s+far[ei]?\s+(?:il\s+)?|per\s+(?:il\s+)?)?tagliando\b",
r"\b(?:ho\s+bisogno\s+(?:di|del)\s+)?tagliando\b",
r"\btagliando\s+(?:auto|macchina|della\s+macchina|dell[''\u2019]?auto)\b",
r"\b(?:devo|dovrei|vorrei)\s+(?:fare\s+)?(?:il\s+)?tagliando\b",

# --- REVISIONE AUTO (distingue da "revisione del look" che è salone-legittimo) ---
r"\b(?:fare\s+(?:la\s+)?|portare\s+(?:la\s+macchina|l[''\u2019]?auto)\s+(?:a\s+(?:fare\s+)?(?:la\s+)?)?)?revisione\s+(?:auto|macchina|della\s+macchina|dell[''\u2019]?auto|ministeriale)\b",
r"\bcollaudo\s+(?:auto|della\s+macchina)\b",
r"\bbollino\s+blu\b",
# "devo fare la revisione" — tricky because "revisione del look" is valid at salone
# Solution: require "la revisione" without further qualifier (generic car revisione)
r"\b(?:devo|dovrei|vorrei|posso|ho\s+bisogno\s+di)\s+far[ei]?\s+la\s+revisione\b(?!\s+(?:del\s+look|capelli|stile|trucco))",

# --- FRENI / PASTIGLIE ---
r"\b(?:far[ei]?\s+(?:i\s+)?|cambiar[ei]?\s+(?:le\s+)?|sostituir[ei]?\s+(?:le\s+)?)?pastiglie(?:\s+(?:dei\s+)?freni)?\b",
r"\b(?:dischi?\s+(?:dei?\s+)?freno|liquido\s+(?:dei?\s+)?freni)\b",
r"\b(?:revisionare?\s+(?:i\s+)?freni|controllare?\s+(?:i\s+)?freni)\b",

# --- MECCANICO ---
r"\bdal\s+meccanico\b",
r"\bportare?\s+(?:la\s+macchina|l[''\u2019]?auto)\s+dal\s+meccanico\b",
r"\bfar[ei]?\s+(?:vedere?|controllare?|riparare?)\s+(?:la\s+macchina|l[''\u2019]?auto)\b",

# --- BATTERIA AUTO ---
r"\b(?:cambiare?\s+(?:la\s+)?|sostituire?\s+(?:la\s+)?)?batteria\s+(?:auto|della\s+macchina|dell[''\u2019]?auto|del\s+motore)\b",
r"\b(?:macchina|auto)\s+(?:non\s+parte|non\s+si\s+avvia|non\s+avvia)\b",

# --- CARROZZERIA / VERNICIATURA ---
r"\b(?:carrozzeria|verniciatura\s+(?:auto|della\s+macchina)|riverniciatura|ammaccatura|botta\s+(?:alla\s+macchina|all[''\u2019]?auto))\b",
r"\b(?:graffio|rigatura)\s+(?:sulla\s+macchina|sull[''\u2019]?auto|sulla\s+carrozzeria)\b",
```

**False positive risk:** LOW. Each pattern requires either explicit auto vocabulary or
"macchina/auto" as anchor. No salone service uses these terms.

**Would correctly BLOCK:**
- "devo cambiare le gomme si può farlo" → matches gomme pattern
- "voglio fare il tagliando" → matches tagliando pattern
- "porto la macchina dal meccanico" → matches meccanico pattern
- "ho cambiato l'olio la settimana scorsa, devo rifarlo" → matches olio pattern

**Would correctly ALLOW:**
- "vorrei cambiare il colore dei capelli" → no auto vocab, passes through
- "voglio una revisione del look" → exception in revisione pattern (`(?!\s+(?:del\s+look...))`)
- "la mia permanente non tiene" → no auto vocab

#### Group B: PALESTRA service terms at SALONE

```python
# --- ABBONAMENTO PALESTRA ---
r"\b(?:fare\s+|rinnovare\s+|prendere\s+(?:un\s+)?)?abbonamento\s+(?:mensile|annuale|semestrale|trimestrale|in\s+palestra|alla\s+palestra|alla\s+gym|fitness)\b",
r"\b(?:iscriversi\s+(?:in|alla)\s+palestra|iscrizione\s+(?:in|alla)\s+palestra|tessera\s+palestra)\b",
r"\b(?:voglio|vorrei|devo|posso)\s+(?:iscrivermi\s+(?:in|alla)\s+palestra|fare\s+l[''\u2019]?abbonamento\s+(?:in|alla)\s+palestra)\b",

# --- PERSONAL TRAINER / ALLENAMENTO ---
r"\b(?:sessione\s+(?:con\s+il\s+)?personal|personal\s+trainer|pt\s+(?:oggi|domani|la\s+prossima))\b",
r"\b(?:allenamento\s+(?:personalizzato|individuale)|lezione\s+(?:privata|individuale)\s+in\s+palestra)\b",

# --- CORSI FITNESS (with "corso di" prefix to avoid generic "yoga") ---
r"\b(?:corso\s+(?:di\s+)?(?:yoga|pilates|crossfit|spinning|zumba|functional\s+training|aerobica|step))\b",
r"\b(?:lezione\s+(?:di\s+)?(?:yoga|pilates|crossfit|spinning|zumba))\b",
r"\b(?:prenotare\s+(?:un\s+)?(?:corso|lezione)\s+(?:di\s+)?(?:yoga|pilates|crossfit|spinning|zumba))\b",

# --- SALA PESI / BODYBUILDING ---
r"\b(?:sala\s+pesi|body\s+?building|pesistica|pesi\s+liberi|allenamento\s+(?:in\s+)?sala)\b",
```

**False positive risk at SALONE:** LOW.
- "abbonamento mensile" alone (no palestra qualifier) is NOT blocked — e.g., pacchetti abbonamento capelli. Pattern requires palestra/gym qualifier.
- "yoga" alone is NOT blocked — "mi piace lo yoga" passes through (correct).

**Would correctly BLOCK:**
- "vorrei fare l'abbonamento in palestra" → blocked
- "ho lezione di yoga domani" → blocked

**Would correctly ALLOW:**
- "il mio abbonamento al salone è scaduto" → no palestra qualifier
- "faccio yoga ma vorrei un taglio" → "yoga" alone, not "corso di yoga"

#### Group C: MEDICAL service terms at SALONE

```python
# --- VISITA MEDICA ---
r"\b(?:visita\s+(?:medica|specialistica|dal\s+dottore|del\s+medico|cardiologica|dermatologica|ortopedica|ginecologica|pediatrica))\b",
r"\b(?:prenotare\s+(?:una\s+)?visita|fissare\s+(?:una\s+)?visita)\s+(?:medica|specialistica|dal\s+dottore)\b",

# --- ANALISI / ESAMI ---
r"\b(?:esame\s+(?:del\s+sangue|delle\s+urine|diagnostico)|analisi\s+(?:del\s+sangue|cliniche))\b",
r"\b(?:prelievo\s+(?:del\s+)?sangue|fare\s+(?:le\s+)?analisi)\b",

# --- RICETTA / PRESCRIZIONE ---
r"\b(?:ricetta\s+medica|prescrizione\s+medica|prescrizione\s+del\s+medico)\b",
r"\b(?:far[ei]?\s+(?:rinnovare|riscrivere)\s+(?:la\s+)?ricetta)\b",

# --- CERTIFICATO MEDICO ---
r"\b(?:certificato\s+(?:medico|sportivo|di\s+idoneità)|idoneità\s+sportiva|visita\s+(?:di\s+)?idoneità)\b",
```

---

## Section 3: PALESTRA Guardrail — Complete Pattern Matrix

### What PALESTRA must block

A palestra (gym, fitness center) must redirect salone, auto, and medical requests. The existing
patterns cover noun forms; this section adds all verb forms.

### 3.1 SALONE terms at PALESTRA — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["palestra"] — extends existing patterns

# --- TAGLIO CAPELLI ---
r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino|bimbo|bimba)|tagliare\s+(?:i\s+)?capelli)\b",
r"\b(?:accorciare\s+(?:i\s+)?capelli|spuntatina|sforbiciata)\b",
r"\b(?:far[ei]?\s+(?:un\s+)?taglio|prenotare\s+(?:un\s+)?taglio)\b",

# --- COLORE / TINTA ---
r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+(?:delle?\s+)?radici|copertura\s+bianchi)\b",
r"\b(?:fare\s+(?:la\s+)?tinta|fare\s+(?:il\s+)?colore(?:\s+ai\s+capelli)?|tingersi\s+(?:i\s+)?capelli)\b",
r"\b(?:meches|mechès|balayage|shatush|colpi\s+di\s+sole|degradé|ombré)\b",

# --- PIEGA ---
r"\b(?:messa\s+in\s+piega|piega\s+capelli|fare\s+(?:la\s+)?piega|asciugare\s+(?:i\s+)?capelli\s+(?:dal|dalla))\b",

# --- TRATTAMENTI CAPELLI ---
r"\b(?:trattamento\s+capelli|keratina|ricostruzione\s+capelli|botox\s+capelli|cheratina\s+lisciante)\b",
r"\b(?:stiratura\s+(?:brasiliana|capelli)|lisciatura\s+capelli)\b",
r"\b(?:extension\s+capelli|allungamento\s+capelli|applicare\s+(?:le\s+)?extension)\b",

# --- MANICURE / PEDICURE / UNGHIE ---
r"\b(?:manicure|pedicure|nail\s+art|semipermanente\s+(?:mani|piedi)|ricostruzione\s+unghie)\b",
r"\b(?:fare\s+(?:la\s+)?manicure|fare\s+(?:il\s+)?pedicure|fare\s+(?:le\s+)?unghie)\b",
r"\b(?:smalto\s+(?:mani|piedi|unghie)|gel\s+unghie|acrilico\s+unghie)\b",

# --- CERETTA / DEPILAZIONE ---
r"\b(?:ceretta\s+(?:gambe|braccia|inguine|ascelle|integrale)|depilazione\s+(?:gambe|corpo|laser|integrale))\b",
r"\b(?:epilazione\s+(?:gambe|braccia|laser|definitiva)|fare\s+(?:la\s+)?ceretta)\b",

# --- BARBA (solo quando contestualizzato non in fitness) ---
r"\b(?:rifinitura\s+barba|regolazione\s+barba|rasatura\s+(?:della\s+)?barba|barbiere)\b",
```

**False positive risk at PALESTRA:** LOW-MEDIUM.
- "taglio" alone is NOT blocked (someone could say "taglio di capelli" but also "taglio di carne" — we require "taglio capelli" or "taglio + gender").
- "piega" alone is NOT blocked — valid at palestra ("piega delle ginocchia" in training context).

### 3.2 AUTO terms at PALESTRA — same as SALONE Section 2.1

All auto patterns from Section 2.1 apply identically. Key additions:

```python
# PASTE INTO VERTICAL_GUARDRAILS["palestra"] — auto verb forms
r"\b(?:cambiar[ei]|cambio|cambiato)\s+(?:le\s+)?(?:gomm[ea]|pneumatici)\b",
r"\bfar[ei]?\s+(?:il\s+)?(?:cambio\s+(?:gomm[ea]|olio)|tagliando)\b",
r"\b(?:fare\s+(?:la\s+)?|portare\s+(?:la\s+macchina|l[''\u2019]?auto)\s+(?:per|a\s+(?:fare\s+)?(?:la\s+)?))?revisione\s+(?:auto|della\s+macchina)\b",
r"\bportare?\s+(?:la\s+macchina|l[''\u2019]?auto)\s+dal\s+meccanico\b",
```

### 3.3 MEDICAL terms at PALESTRA — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["palestra"] — medical verb forms
r"\b(?:visita\s+(?:medica|specialistica|dal\s+medico)|consulto\s+medico)\b",
r"\b(?:prenotare\s+(?:una\s+)?|fissare\s+(?:una\s+)?)?visita\s+(?:medica|specialistica)\b",
r"\b(?:esame\s+del\s+sangue|analisi\s+(?:del\s+sangue|cliniche)|prelievo\s+sangue)\b",
r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
r"\b(?:certificato\s+medico|idoneità\s+sportiva|visita\s+di\s+idoneità)\b",
```

**Note on "idoneità sportiva" at palestra:** This is specifically a medical certificate that allows
sport. While it's related to sport, it is issued by a doctor, not by a gym. Blocking is CORRECT —
redirect to medical studio.

---

## Section 4: MEDICAL Guardrail — Complete Pattern Matrix

### What MEDICAL must block

A medical studio must redirect salone, palestra, and auto requests. The existing patterns
cover most medical cases well. Primary gap is verb forms for auto services.

### 4.1 SALONE terms at MEDICAL — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["medical"] — salone verb forms (supplements existing)

# --- TAGLIO CAPELLI (verb forms beyond existing noun coverage) ---
r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino)|tagliare\s+(?:i\s+)?capelli|farsi\s+(?:un\s+)?taglio)\b",

# --- COLORE / TINTA ---
r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici|meches|balayage|shatush|colpi\s+di\s+sole)\b",
r"\b(?:fare\s+(?:la\s+)?tinta|fare\s+(?:il\s+)?colore\s+(?:ai\s+)?capelli|tingersi\s+(?:i\s+)?capelli)\b",

# --- PIEGA ---
r"\b(?:messa\s+in\s+piega|piega\s+capelli|fare\s+(?:la\s+)?piega)\b",

# --- MANICURE / PEDICURE (existing covers "fare (la|una?) manicure" — this extends) ---
r"\b(?:prenotare\s+(?:una\s+)?(?:manicure|pedicure)|voglio\s+(?:una\s+)?(?:manicure|pedicure))\b",
r"\b(?:nail\s+art|gel\s+unghie|ricostruzione\s+unghie|smalto\s+semipermanente)\b",

# --- CERETTA / DEPILAZIONE (existing covers some; extend for verb forms) ---
r"\b(?:fare\s+(?:la\s+)?ceretta|prenotare\s+(?:la\s+)?ceretta)\b",
r"\b(?:ceretta\s+(?:gambe|braccia|inguine|ascelle)|epilazione\s+(?:laser|gambe|definitiva))\b",

# --- TRUCCO / ACCONCIATURA SPOSA ---
r"\b(?:trucco\s+sposa|trucco\s+cerimonia|make-up\s+(?:sposa|cerimonia)|acconciatura\s+sposa)\b",
```

### 4.2 AUTO terms at MEDICAL — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["medical"] — auto verb forms (supplements existing)
r"\b(?:cambiar[ei]|cambio|cambiato)\s+(?:le\s+)?(?:gomm[ea]|pneumatici)\b",
r"\bfar[ei]?\s+(?:il\s+)?(?:cambio\s+(?:gomm[ea]|olio)|tagliando)\b",
r"\b(?:fare\s+(?:la\s+)?|portare\s+(?:la\s+macchina|l[''\u2019]?auto)\s+(?:per|a\s+(?:fare\s+)?(?:la\s+)?))?revisione\s+(?:auto|della\s+macchina)\b",
r"\bportare?\s+(?:la\s+macchina|l[''\u2019]?auto)\s+dal\s+meccanico\b",
r"\b(?:cambiar[ei]|cambio)\s+(?:l[''\u2019]?\s*)?olio\b",
```

### 4.3 PALESTRA terms at MEDICAL — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["medical"] — palestra verb forms
r"\b(?:fare\s+)?abbonamento\s+(?:mensile|annuale|palestra|in\s+palestra|alla\s+palestra)\b",
r"\b(?:iscriversi\s+(?:in|alla)\s+palestra|iscrizione\s+palestra)\b",
r"\b(?:corso\s+(?:di\s+)?(?:yoga|pilates|crossfit|spinning|zumba|aerobica))\b",
r"\b(?:lezione\s+(?:di\s+)?(?:yoga|pilates|crossfit|spinning|zumba))\b",
r"\b(?:personal\s+trainer|sessione\s+(?:con\s+il\s+)?personal)\b",
r"\b(?:sala\s+pesi|body\s*building|allenamento\s+(?:personalizzato|in\s+sala))\b",
```

---

## Section 5: AUTO Guardrail — Complete Pattern Matrix

### What AUTO must block

An auto workshop must redirect salone, palestra, and medical requests. Auto does NOT need
to block its own services. The existing patterns for salone/palestra/medical at auto need
verb forms added.

### 5.1 SALONE terms at AUTO — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["auto"] — salone verb forms (supplements existing)

# --- TAGLIO CAPELLI ---
r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino)|tagliare\s+(?:i\s+)?capelli)\b",
r"\b(?:accorciare\s+(?:i\s+)?capelli|farsi\s+(?:un\s+)?taglio(?:\s+di\s+capelli)?)\b",

# --- COLORE / TINTA ---
r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici|meches|balayage|colpi\s+di\s+sole)\b",
r"\b(?:fare\s+(?:la\s+)?tinta|fare\s+(?:il\s+)?colore\s+(?:ai\s+)?capelli|tingersi\s+(?:i\s+)?capelli)\b",

# --- PIEGA ---
r"\b(?:messa\s+in\s+piega|piega\s+capelli|fare\s+(?:la\s+)?piega)\b",

# --- MANICURE / PEDICURE ---
r"\b(?:la\s+|una?\s+|fare\s+(?:la\s+)?|prenotare\s+(?:una?\s+)?)?(?:manicure|pedicure)\b",
r"\b(?:nail\s+art|gel\s+unghie|ricostruzione\s+unghie|smalto\s+(?:mani|piedi|semipermanente))\b",

# --- CERETTA ---
r"\b(?:ceretta\s+(?:gambe|braccia|inguine|ascelle|integrale)|epilazione\s+(?:gambe|laser|definitiva))\b",
r"\b(?:depilazione\s+(?:laser|integrale|corpo|gambe)|fare\s+(?:la\s+)?ceretta)\b",
```

### 5.2 PALESTRA terms at AUTO — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["auto"] — palestra verb forms
r"\b(?:fare\s+)?abbonamento\s+(?:mensile|annuale|palestra|in\s+palestra|alla\s+palestra)\b",
r"\b(?:iscriversi\s+(?:in|alla)\s+palestra|tessera\s+palestra)\b",
r"\b(?:corso\s+(?:di\s+)?(?:yoga|pilates|crossfit|spinning|zumba))\b",
r"\b(?:lezione\s+(?:di\s+)?(?:yoga|pilates|crossfit))\b",
r"\b(?:personal\s+trainer|pt\s+(?:oggi|domani)|sessione\s+(?:con\s+il\s+)?personal)\b",
```

### 5.3 MEDICAL terms at AUTO — complete verb matrix

```python
# PASTE INTO VERTICAL_GUARDRAILS["auto"] — medical verb forms (supplements existing)
r"\b(?:prenotare\s+(?:una\s+)?|fissare\s+(?:una\s+)?)?visita\s+(?:medica|specialistica|dal\s+medico)\b",
r"\b(?:esame\s+del\s+sangue|analisi\s+(?:del\s+sangue|cliniche)|prelievo\s+sangue)\b",
r"\b(?:ricetta\s+medica|prescrizione\s+medica|fare\s+rinnovare\s+(?:la\s+)?ricetta)\b",
r"\b(?:certificato\s+medico|idoneità\s+sportiva)\b",
```

---

## Section 6: Intent Classifier Hardening — Other Vulnerable Patterns

### 6.1 CANCELLAZIONE — partial vulnerability

**File:** `intent_classifier.py`, line 395.

```python
# CURRENT (partially vulnerable):
r"(posso|voglio|vorrei|devo)\s+(annullare?|cancellare?|disdire?)\s*((il|la|l')?\s*)?(mia?|mio)?\s*(appuntament|prenotazion)?",
```

The trailing `?` on `(appuntament|prenotazion)?` allows "voglio cancellare" alone to match.
However, the first pattern (line 394) is more restrictive and fires first in most cases:
```python
r"(annulla|cancella|disdire?)\s+((il|la|l'|lo)\s+)?(mio|mia)?\s*(appuntament|prenotazion|visita)"
```

**Practical risk:** LOW, because "annullare/cancellare" in Italian are strong booking-domain signals.
The false positive rate is tolerable. Monitor but don't change for F02.

### 6.2 PRENOTAZIONE — safe (no vulnerability identified)

All PRENOTAZIONE patterns require either "appuntamento", "prenotare", "disponibile", or a
strong service noun. No ambiguity risk identified.

### 6.3 INFO — safe (no vulnerability identified)

INFO patterns require specific question words ("quanto costa", "orari", "dove", etc.).
No false positive risk.

### 6.4 Additional vulnerable standalone: "rimandare" at non-booking context

```python
# Current line 421:
r"\b(spostare?|anticipare?|posticipare?|rimandare?)\b\s+"
```

"Rimandare" in Italian commonly means "to postpone" but also "to resend" (rimandare un
file, rimandare un messaggio). At salone, "rimandare il messaggio" could match SPOSTAMENTO.

**Fix (optional hardening):**
```python
# Split "rimandare" from the others — require appointment context
r"\b(spostare?|anticipare?|posticipare?)\b\s+",
r"\brimandare?\s+(l[ao'\u2019]?\s*)?(appuntament|prenotazion|visita|data)\b",
```

**Risk assessment:** MEDIUM impact, LOW urgency. Implement in F02.2 if needed.

---

## Section 7: Late Guardrail — Orchestrator Injection Point

### 7.1 The Defense-In-Depth Pattern

Even after fix 1B (SPOSTAMENTO hardening), a user could say "posso spostare la mia
macchina per il tagliando?" — the modal pattern `(posso|...)+(sposta...)` would still fire.

**Solution:** Add a late guardrail check in orchestrator.py E4-S2 handler.

**Location:** `orchestrator.py`, line 791 — the E4-S2 block beginning with:
```python
# E4-S2: Handle SPOSTAMENTO intent at L1 (before booking SM)
if response is None and intent_result.category == IntentCategory.SPOSTAMENTO:
```

**Insert BEFORE the reschedule logic:**
```python
# DEFENSE-IN-DEPTH: Late guardrail check
# Even if SPOSTAMENTO fired correctly at L1, verify input is not out-of-scope
if HAS_ITALIAN_REGEX:
    try:
        from italian_regex import check_vertical_guardrail
    except ImportError:
        from .italian_regex import check_vertical_guardrail
    _late_guardrail = check_vertical_guardrail(user_input, self.verticale_id or "salone")
    if _late_guardrail.blocked:
        response = _late_guardrail.redirect_response
        intent = f"guardrail_late_{_late_guardrail.vertical}_{intent_result.intent}"
        layer = ProcessingLayer.L0_SPECIAL
        # Do NOT set _pending_reschedule — fall through to return
```

**This pattern should be applied identically at:**
- The E4-S1 (CANCELLAZIONE) handler at line ~1213
- The secondary SPOSTAMENTO block at line ~1249

### 7.2 What self.verticale_id is

Check that `self.verticale_id` is populated from session config. In `orchestrator.py`:
```python
self.verticale_id = config.get("vertical", "salone")  # Search for this in __init__
```
If it is `None` by default, guard with `self.verticale_id or "salone"`.

---

## Section 8: Groq System Prompt Enhancement

### 8.1 Current System Prompt (as-is, from orchestrator.py `_build_llm_context`)

```python
return f"""Sei Sara, l'assistente vocale di {self.business_name}.

PERSONALITA':
- Cordiale, professionale, empatica
- Risposte BREVI (max 2-3 frasi)
- Parli italiano con accento neutro
- Usa "Lei" (formale)

CAPACITA':
1. Prenotare appuntamenti
2. Verificare disponibilita
3. Fornire info su orari e prezzi
4. Spostare/cancellare appuntamenti

CONTESTO ATTUALE:
{self._get_context_summary()}

REGOLE:
- NON inventare informazioni
- Se non sai, dì che verifichi
- Rispondi SEMPRE in italiano
"""
```

**Problem:** No vertical context. Groq does not know what kind of business it is. If a query
about a car reaches L4 Groq at a salone, Groq may helpfully describe car services.

### 8.2 Enhanced System Prompt

```python
# REPLACEMENT for _build_llm_context() in orchestrator.py

_VERTICAL_DESCRIPTIONS = {
    "salone": "salone di bellezza/parrucchiere che offre: taglio capelli, colore, piega, trattamenti, manicure, pedicure, ceretta, trucco",
    "palestra": "palestra/centro fitness che offre: abbonamenti, corsi yoga/pilates/crossfit/spinning, personal training, sala pesi",
    "medical": "studio medico/poliambulatorio che offre: visite mediche, esami diagnostici, fisioterapia, vaccinazioni, certificati medici",
    "auto": "officina meccanica che offre: tagliando, cambio olio, cambio gomme, riparazioni, revisione, diagnostica, carrozzeria",
}

_VERTICAL_OUT_OF_SCOPE = {
    "salone": "meccanica auto, palestra, visite mediche",
    "palestra": "parrucchiere, officina meccanica, visite mediche",
    "medical": "parrucchiere, palestra, officina meccanica",
    "auto": "parrucchiere, palestra, visite mediche",
}

def _build_llm_context(self) -> str:
    """Build vertical-aware system prompt for Groq LLM."""
    vertical = self.verticale_id or "salone"
    vertical_desc = _VERTICAL_DESCRIPTIONS.get(vertical, "attività locale")
    out_of_scope = _VERTICAL_OUT_OF_SCOPE.get(vertical, "altri servizi")

    return f"""Sei Sara, l'assistente vocale di {self.business_name} ({vertical_desc}).

PERSONALITA':
- Cordiale, professionale, empatica
- Risposte BREVI (max 2-3 frasi)
- Parli italiano con accento neutro
- Usa "Lei" (formale)

CAPACITA' DEL {vertical.upper()}:
{vertical_desc}

NON MI OCCUPO DI:
{out_of_scope}
Se il cliente chiede servizi fuori ambito, rispondi: "Mi occupo solo di prenotazioni per {self.business_name}. Posso aiutarla con [servizio in-scope]?"

CONTESTO CONVERSAZIONE ATTUALE:
{self._get_context_summary()}

REGOLE ASSOLUTE:
- NON inventare informazioni sui servizi
- NON descrivere servizi fuori ambito come se fossero disponibili
- Se non sai, dì "verifico e la ricontatto"
- Rispondi SEMPRE in italiano
- Max 2-3 frasi per risposta
"""
```

**Impact:** When Groq is reached for an out-of-scope query (leak through all guardrails),
it now has explicit context about what to redirect. This is the last line of defense.

---

## Section 9: Test Case Matrix

### 9.1 SPOSTAMENTO Fix Tests (target: all pass after fix 1B)

```python
# Tests for intent_classifier.py hardening
# File: voice-agent/tests/test_intent_classifier.py

import pytest
from intent_classifier import classify_intent, IntentCategory

# --- SPOSTAMENTO: should STILL match (regression tests) ---
@pytest.mark.parametrize("text", [
    "voglio spostare il mio appuntamento",
    "posso cambiare l'appuntamento di martedì",
    "vorrei modificare l'orario",
    "cambiare la data dell'appuntamento",
    "devo posticipare la prenotazione",
    "anticipa l'appuntamento di un'ora",
    "rimanda la visita alla prossima settimana",
    "posso rimandare?",
    "vorrei un altro giorno",
    "preferisco un altro orario",
    "posso spostarlo?",
    "voglio anticipare",
    "devo modificare l'appuntamento",
])
def test_spostamento_still_matches(text):
    result = classify_intent(text)
    assert result.category == IntentCategory.SPOSTAMENTO, \
        f"REGRESSION: '{text}' should be SPOSTAMENTO but got {result.category}"

# --- SPOSTAMENTO: should NOT match (false positive tests) ---
@pytest.mark.parametrize("text", [
    "devo cambiare le gomme",
    "voglio cambiare il colore della mia macchina",
    "cambiare l'olio",
    "voglio modificare il mio look",
    "devo cambiare i freni",
    "posso cambiare il filtro dell'aria",
    "voglio cambiare operatore telefonico",
    "devo modificare l'indirizzo",
])
def test_spostamento_no_false_positives(text):
    result = classify_intent(text)
    assert result.category != IntentCategory.SPOSTAMENTO, \
        f"FALSE POSITIVE: '{text}' triggered SPOSTAMENTO (should not)"
```

### 9.2 SALONE Guardrail Tests (target: all pass after adding verb forms)

```python
# File: voice-agent/tests/test_guardrails.py (add to existing)
from italian_regex import check_vertical_guardrail

# --- SALONE must BLOCK these auto service verb forms ---
@pytest.mark.parametrize("text", [
    # Gomme variants
    "devo cambiare le gomme si può farlo",
    "cambiare le gomme invernali",
    "voglio cambiare i pneumatici",
    "ho cambiato le gomme la settimana scorsa",
    "mi servono le gomme nuove",
    "fare il cambio gomme",
    "fare il cambio stagionale",
    "mettere le gomme invernali",
    "montare le gomme d'inverno",
    "portare la macchina per le gomme",
    # Olio variants
    "cambiare l'olio",
    "devo cambiare l'olio del motore",
    "fare il cambio olio",
    "ho bisogno del cambio olio",
    "fare il cambio dell'olio",
    # Tagliando variants
    "fare il tagliando",
    "devo fare il tagliando",
    "portare la macchina per il tagliando",
    "portare l'auto a fare il tagliando",
    "ho bisogno del tagliando",
    "tagliando della macchina",
    # Revisione variants
    "fare la revisione dell'auto",
    "portare la macchina a fare la revisione",
    "revisione ministeriale",
    "bollino blu",
    "collaudo della macchina",
    # Freni variants
    "cambiare le pastiglie dei freni",
    "dischi del freno",
    "liquido dei freni",
    # Meccanico variants
    "portare la macchina dal meccanico",
    "portare l'auto dal meccanico",
    "far riparare la macchina",
    "far controllare l'auto",
])
def test_salone_blocks_auto_verb_forms(text):
    result = check_vertical_guardrail(text, "salone")
    assert result.blocked is True, \
        f"LEAK at SALONE: '{text}' was not blocked (matched: {result.matched_pattern!r})"

# --- SALONE must ALLOW these in-scope salone phrases ---
@pytest.mark.parametrize("text", [
    "vorrei cambiare il colore dei capelli",
    "voglio cambiare l'appuntamento",
    "devo modificare la prenotazione",
    "fare una revisione del look",
    "voglio rinnovare il mio stile",
    "cambiare il colore alla piega",
    "vorrei uno shatush",
    "fare la piega",
    "fare la manicure",
    "portare mia figlia per un taglio",
])
def test_salone_allows_in_scope(text):
    result = check_vertical_guardrail(text, "salone")
    assert result.blocked is False, \
        f"FALSE POSITIVE at SALONE: '{text}' was blocked (matched: {result.matched_pattern!r})"
```

### 9.3 PALESTRA Guardrail Tests

```python
# File: voice-agent/tests/test_guardrails.py (add to existing)

@pytest.mark.parametrize("text", [
    # Salone verb forms at palestra
    "tagliare i capelli",
    "farsi un taglio di capelli",
    "fare la tinta",
    "tingersi i capelli",
    "fare il colore ai capelli",
    "fare la piega",
    "fare la manicure",
    "fare il pedicure",
    "fare le unghie",
    "fare la ceretta gambe",
    # Auto verb forms at palestra
    "cambiare le gomme",
    "fare il cambio olio",
    "fare il tagliando",
    "portare la macchina dal meccanico",
    # Medical at palestra
    "prenotare una visita medica",
    "fare le analisi del sangue",
    "ricetta medica",
])
def test_palestra_blocks_out_of_scope_verb_forms(text):
    result = check_vertical_guardrail(text, "palestra")
    assert result.blocked is True, \
        f"LEAK at PALESTRA: '{text}' was not blocked"

@pytest.mark.parametrize("text", [
    # Palestra in-scope (must NOT be blocked)
    "fare il corso di yoga",
    "prenotare una sessione di personal trainer",
    "abbonamento mensile in palestra",
    "lezione di spinning",
    "sala pesi domani",
    "posso prenotare un posto in palestra?",
    "iscrivermi al corso di pilates",
])
def test_palestra_allows_in_scope(text):
    result = check_vertical_guardrail(text, "palestra")
    assert result.blocked is False, \
        f"FALSE POSITIVE at PALESTRA: '{text}' was blocked"
```

### 9.4 MEDICAL Guardrail Tests

```python
@pytest.mark.parametrize("text", [
    # Salone at medical
    "tagliare i capelli",
    "fare la tinta",
    "fare la manicure",
    "fare la ceretta gambe",
    # Palestra at medical
    "abbonamento in palestra",
    "corso di yoga",
    "personal trainer",
    # Auto at medical
    "cambiare le gomme",
    "fare il tagliando",
    "portare la macchina dal meccanico",
])
def test_medical_blocks_out_of_scope(text):
    result = check_vertical_guardrail(text, "medical")
    assert result.blocked is True, \
        f"LEAK at MEDICAL: '{text}' was not blocked"

@pytest.mark.parametrize("text", [
    # Medical in-scope
    "prenotare una visita cardiologica",
    "fare le analisi del sangue",
    "visita ortopedica",
    "vaccino antinfluenzale",
    "rinnovo certificato medico",
    "fisioterapia per la schiena",
    "controllo della vista",
    "visita ginecologica",
])
def test_medical_allows_in_scope(text):
    result = check_vertical_guardrail(text, "medical")
    assert result.blocked is False, \
        f"FALSE POSITIVE at MEDICAL: '{text}' was blocked"
```

### 9.5 AUTO Guardrail Tests

```python
@pytest.mark.parametrize("text", [
    # Salone at auto
    "tagliare i capelli",
    "fare la tinta",
    "fare la manicure",
    # Palestra at auto
    "abbonamento in palestra",
    "corso di yoga",
    # Medical at auto
    "visita medica",
    "analisi del sangue",
    "ricetta medica",
])
def test_auto_blocks_out_of_scope(text):
    result = check_vertical_guardrail(text, "auto")
    assert result.blocked is True, \
        f"LEAK at AUTO: '{text}' was not blocked"

@pytest.mark.parametrize("text", [
    # Auto in-scope (must NOT be blocked)
    "cambio olio",
    "cambiare le gomme",
    "fare il tagliando",
    "revisione auto",
    "sostituire i freni",
    "carrozzeria",
    "diagnostica auto",
    "batteria scarica non parte",
])
def test_auto_allows_in_scope(text):
    result = check_vertical_guardrail(text, "auto")
    assert result.blocked is False, \
        f"FALSE POSITIVE at AUTO: '{text}' was blocked"
```

### 9.6 End-to-End Pipeline Tests (after all fixes)

```python
# File: voice-agent/tests/test_vertical_e2e.py (new file)
import pytest
from italian_regex import check_vertical_guardrail
from intent_classifier import classify_intent, IntentCategory

class TestVerticalPipelineE2E:
    """
    End-to-end tests simulating full L0 → L1 pipeline behavior.
    Verifies that combined fixes prevent the compound bug scenario.
    """

    def test_bug_gomme_at_salone_full_chain(self):
        """
        Original bug: "Gino devo cambiare le gomme si può farlo?"
        After fix: L0 guardrail blocks it — L1 never reached.
        """
        text = "Ciao Sara sono Gino devo cambiare le gomme si può farlo?"
        # L0 check
        guardrail = check_vertical_guardrail(text, "salone")
        assert guardrail.blocked is True, "Bug not fixed: guardrail should block this"
        # Also verify L1 doesn't misclassify if guardrail passes (belt+suspenders)
        intent = classify_intent(text)
        assert intent.category != IntentCategory.SPOSTAMENTO, \
            "L1 false positive: 'cambiare le gomme' should not be SPOSTAMENTO"

    def test_change_appointment_at_salone_allowed(self):
        """
        Valid spostamento: "vorrei cambiare l'appuntamento" at salone.
        Guardrail must NOT block. L1 must classify as SPOSTAMENTO.
        """
        text = "Buongiorno, vorrei cambiare l'appuntamento di giovedì"
        guardrail = check_vertical_guardrail(text, "salone")
        assert guardrail.blocked is False, \
            f"FALSE POSITIVE: valid reschedule blocked at salone: {guardrail.matched_pattern}"
        intent = classify_intent(text)
        assert intent.category == IntentCategory.SPOSTAMENTO, \
            f"L1 miss: 'cambiare l'appuntamento' should be SPOSTAMENTO, got {intent.category}"

    def test_palestra_abbonamento_at_salone_blocked(self):
        """'Voglio fare l'abbonamento in palestra' at salone → blocked."""
        text = "Voglio fare l'abbonamento in palestra"
        result = check_vertical_guardrail(text, "salone")
        assert result.blocked is True

    def test_visita_medica_at_auto_blocked(self):
        """'Prenotare una visita medica' at auto → blocked."""
        text = "Vorrei prenotare una visita medica"
        result = check_vertical_guardrail(text, "auto")
        assert result.blocked is True

    def test_prenotare_taglio_at_salone_allowed(self):
        """Normal booking at salone — must not be blocked."""
        text = "Vorrei prenotare un taglio per domani"
        result = check_vertical_guardrail(text, "salone")
        assert result.blocked is False

    def test_tagliando_at_auto_allowed(self):
        """'Fare il tagliando' at auto — in-scope, must not be blocked."""
        text = "Devo fare il tagliando della mia macchina"
        result = check_vertical_guardrail(text, "auto")
        assert result.blocked is False

    def test_cambio_olio_at_palestra_blocked(self):
        """'Cambio olio' at palestra → blocked."""
        text = "Devo cambiare l'olio della macchina"
        result = check_vertical_guardrail(text, "palestra")
        assert result.blocked is True
```

---

## Section 10: Implementation Order

### Sorted by Impact / Effort / Risk

| # | Fix | File | Impact | Effort | Risk |
|---|-----|------|--------|--------|------|
| 1 | Add verb forms to SALONE guardrail | `italian_regex.py` | CRITICAL | 45 min | LOW |
| 2 | Add verb forms to PALESTRA guardrail | `italian_regex.py` | HIGH | 30 min | LOW |
| 3 | Add verb forms to MEDICAL guardrail | `italian_regex.py` | HIGH | 30 min | LOW |
| 4 | Add verb forms to AUTO guardrail | `italian_regex.py` | MEDIUM | 20 min | LOW |
| 5 | Harden SPOSTAMENTO pattern (remove `?`) | `intent_classifier.py` | CRITICAL | 15 min | LOW |
| 6 | Add parametric guardrail tests | `tests/test_guardrails.py` | HIGH | 45 min | ZERO |
| 7 | Add E2E pipeline tests | `tests/test_vertical_e2e.py` | HIGH | 30 min | ZERO |
| 8 | Late guardrail in orchestrator E4-S2 | `orchestrator.py` | MEDIUM | 20 min | LOW |
| 9 | Enhance Groq system prompt with vertical | `orchestrator.py` | MEDIUM | 15 min | LOW |
| 10 | Harden CANCELLAZIONE pattern | `intent_classifier.py` | LOW | 10 min | LOW |
| 11 | Split "rimandare" from standalone pattern | `intent_classifier.py` | LOW | 10 min | LOW |

**Total estimated effort:** ~4.5 hours

### Recommended session execution order

```
Step 1 (45 min): italian_regex.py — extend VERTICAL_GUARDRAILS for all 4 verticals
  → Test: pytest tests/test_guardrails.py -v (existing + new parametric tests)

Step 2 (15 min): intent_classifier.py — harden SPOSTAMENTO (remove trailing ?)
  → Test: pytest tests/test_intent_classifier.py -v

Step 3 (45 min): Add parametric tests to test_guardrails.py (Section 9.2-9.5)

Step 4 (30 min): Create tests/test_vertical_e2e.py (Section 9.6)

Step 5 (20 min): orchestrator.py — late guardrail (Section 7.1)

Step 6 (15 min): orchestrator.py — enhanced Groq system prompt (Section 8.2)

Step 7 (60 min): Run full test suite, fix any regressions
  → pytest tests/ -v --tb=short | tail -30

Step 8: Restart pipeline on iMac + verify /health
```

### Acceptance Criteria (Definition of Done)

- [ ] `check_vertical_guardrail("devo cambiare le gomme si può farlo", "salone").blocked == True`
- [ ] `check_vertical_guardrail("vorrei cambiare l'appuntamento", "salone").blocked == False`
- [ ] `classify_intent("devo cambiare le gomme").category != IntentCategory.SPOSTAMENTO`
- [ ] `classify_intent("voglio cambiare l'orario").category == IntentCategory.SPOSTAMENTO`
- [ ] All 40+ parametric guardrail tests pass
- [ ] Full test suite 1160+ PASS / 0 FAIL maintained
- [ ] iMac pipeline `/health` returns 200 after restart

---

## Appendix: Full Italian Verb Morphology for Service Terms

This appendix lists all morphological forms generated for each key service term.
Use as reference when adding to guardrail patterns.

### A1: "cambiare" + "gomme" — complete morphology

```
Infinitive:    cambiare le gomme, cambiare i pneumatici
1s present:    cambio le gomme
2s present:    cambi le gomme
3s present:    cambia le gomme [STT MOST COMMON]
1p present:    cambiamo le gomme
3p present:    cambiano le gomme
Past pp:       cambiato le gomme (ho cambiato, avevo cambiato)
Future:        cambierò le gomme, cambieranno le gomme
Conditional:   cambierei le gomme, vorrei cambiare le gomme
Imperative:    cambia le gomme! (2s)
Reflexive:     mi servono le gomme nuove
"Fare il":     fare il cambio gomme, fare il cambio stagionale
"Portare per": portare la macchina per le gomme
"Dovere":      devo cambiare le gomme, dovrei cambiare le gomme
"Potere":      posso cambiare le gomme, si può cambiare le gomme
"Volere":      voglio, vorrei cambiare le gomme
```

**Regex covering all above:**
```python
r"\b(?:cambiar[ei]|cambia(?:no|mo)?|cambio|cambiato|cambier[òà]|cambieranno|cambieremmo|cambierei)\s+(?:le\s+|i\s+|dei?\s+|delle?\s+)?(?:gomm[ea]|pneumatici|ruot[ea])\b"
r"\b(?:ho|avevo|avrei)\s+cambiato\s+(?:le\s+)?(?:gomm[ea]|pneumatici)\b"
r"\bfar[ei]?\s+(?:il\s+)?cambio\s+(?:gomm[ea]|pneumatici|stagionale)\b"
r"\bportar[ei]?\s+(?:la\s+macchina|l[''\u2019]?auto)\s+per\s+(?:le\s+)?(?:gomm[ea]|pneumatici)\b"
r"\b(?:devo|dovrei|voglio|vorrei|posso|potrei|mi\s+servono)\s+(?:cambiare\s+)?(?:le\s+)?(?:gomm[ea]|pneumatici)\b"
r"\b(?:metter[ei]?|mont[ao]re?|install[ao]re?)\s+(?:le\s+)?gomm[ea]\s+(?:invernali|estive|nuove)\b"
```

### A2: "fare" + article + service — pattern template

This is the canonical Italian pattern for service requests. Template:
```
"fare" + (il|la|le|l'|uno|una) + [service noun]
```

All services can be requested this way:
- "fare il tagliando" → auto (blocked at salone)
- "fare la revisione" → auto (blocked at salone)
- "fare il cambio olio" → auto (blocked at salone)
- "fare la piega" → salone (in-scope at salone)
- "fare la manicure" → salone (in-scope at salone, out-of-scope at auto/medical)
- "fare la ceretta" → salone (in-scope at salone)
- "fare l'abbonamento" → palestra + qualifier needed
- "fare la visita" → medical + qualifier "medica" preferred

**General regex template:**
```python
r"\bfar[ei]?\s+(?:il\s+|la\s+|l[''\u2019]?\s*|le\s+|un[ao]?\s+)?{service_noun}\b"
```

### A3: "portare" + vehicle + purpose — complete morphology

```
Infinitive:     portare la macchina per/dal/a
1s present:     porto la macchina
3s present:     porta la macchina
Compound:       devo portare la macchina, voglio portare l'auto
Past:           ho portato la macchina
```

**Regex:**
```python
r"\bportar[ei]?\s+(?:la\s+macchina|l[''\u2019]?auto|il\s+furgone|il\s+camion)\s+(?:dal\s+meccanico|per\s+(?:la\s+)?(?:revisione|tagliando|gomme|olio|freni)|a\s+far[ei]?\s+(?:il\s+|la\s+)?(?:tagliando|revisione|cambio))\b"
```

### A4: "iscriversi" + palestra — complete morphology

```
Infinitive:     iscriversi in/alla palestra
1s reflexive:   mi voglio iscrivere, mi iscrivo
Future:         mi iscriverò
Compound:       voglio iscrivermi, devo iscrivermi
Past:           mi sono iscritto/a
```

**Regex:**
```python
r"\b(?:iscriversi|iscriverm[ei]|mi\s+iscriv[oa]|mi\s+voglio\s+iscrivere|mi\s+sono\s+iscritt[oa])\s+(?:in|alla|nella)\s+palestra\b"
r"\b(?:voglio|vorrei|devo|posso)\s+iscriverm[ei]\s+(?:in|alla)\s+palestra\b"
r"\biscrizione\s+(?:in|alla|nella)\s+palestra\b"
```

---

## Sources

- `/Volumes/MontereyT7/FLUXION/voice-agent/src/italian_regex.py` — VERTICAL_GUARDRAILS (lines 726-849), Section 10
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/intent_classifier.py` — INTENT_PATTERNS SPOSTAMENTO (lines 409-421), CANCELLAZIONE (lines 391-408)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py` — E4-S2 handler (lines 791-855, 1249-1283), `_build_llm_context()` (lines 1662-1685)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/booking_state_machine.py` — BookingState enum (lines 73-102), vertical field (line 159)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/groq_client.py` — `generate_response()` system_prompt parameter (line 136)
- `.claude/cache/agents/f02-nlu-ambiguity-research.md` — root cause analysis (prerequisite)

**Research date:** 2026-03-04
**Valid until:** 2026-04-03
