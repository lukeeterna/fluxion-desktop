---
phase: f-sara-nlu-patterns
plan: "02"
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/italian_regex.py
  - voice-agent/src/entity_extractor.py
  - voice-agent/tests/test_wellness_medico_nlu.py
autonomous: true

must_haves:
  truths:
    - "check_vertical_guardrail(text, 'wellness') returns blocked=True for OOS inputs (hair, auto, medical prescriptions, professionale)"
    - "check_vertical_guardrail(text, 'wellness') returns blocked=False for all wellness sub-vertical inputs (personal trainer, yoga, crossfit, piscina, arti marziali)"
    - "check_vertical_guardrail(text, 'medico') returns blocked=True for OOS inputs (hair, beauty, auto, palestra)"
    - "check_vertical_guardrail(text, 'medico') returns blocked=False for all medico sub-vertical inputs (odontoiatra, fisioterapia, psicologo, nutrizionista, osteopata, podologo)"
    - "Legacy keys 'palestra' and 'medical' still work (existing tests unchanged)"
    - "extract_vertical_entities(text, 'medico') returns specialty for fisioterapia, osteopata, psicologo, nutrizionista, podologo"
    - "extract_vertical_entities(text, 'wellness') returns sub_vertical for personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali"
    - "pytest test_wellness_medico_nlu.py passes with ≥50 test cases, 0 failures"
  artifacts:
    - path: "voice-agent/src/italian_regex.py"
      provides: "VERTICAL_SERVICES['wellness'], VERTICAL_SERVICES['medico'], VERTICAL_GUARDRAILS['wellness'], VERTICAL_GUARDRAILS['medico'], legacy aliases palestra/medical"
      contains: "VERTICAL_SERVICES[\"wellness\"]"
    - path: "voice-agent/src/entity_extractor.py"
      provides: "Extended _MEDICAL_SPECIALTIES with fisioterapia/osteopata/psicologo/nutrizionista/podologo, _WELLNESS_SUB_VERTICAL_KEYWORDS, elif wellness/medico branches"
      contains: "fisioterapia"
    - path: "voice-agent/tests/test_wellness_medico_nlu.py"
      provides: "Parametrized test classes for wellness + medico guardrails and entity extraction"
      contains: "TestWellnessGuardrails"
  key_links:
    - from: "voice-agent/tests/test_wellness_medico_nlu.py"
      to: "voice-agent/src/italian_regex.py"
      via: "from italian_regex import check_vertical_guardrail, VERTICAL_SERVICES"
      pattern: "check_vertical_guardrail"
    - from: "voice-agent/tests/test_wellness_medico_nlu.py"
      to: "voice-agent/src/entity_extractor.py"
      via: "from entity_extractor import extract_vertical_entities"
      pattern: "extract_vertical_entities"
---

<objective>
Expand Sara's NLU layer with complete wellness and medico vertical coverage: service synonym tables, guardrail patterns, and entity extraction for all sub-verticals (personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali for wellness; odontoiatra, fisioterapia, psicologo, nutrizionista, osteopata, podologo for medico).

Purpose: Today wellness falls through to "palestra" (legacy key, 6 sub-verticals missing) and medico uses "medical" (legacy key, missing fisioterapia/osteopata/psicologo/nutrizionista/podologo in both services and entity extraction). After this plan, both verticals have full synonym coverage for multi-service detection and correct specialty detection.

Output: Expanded italian_regex.py + entity_extractor.py + test_wellness_medico_nlu.py with ≥50 parametrized test cases, all passing on MacBook (pure Python).
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-RESEARCH.md

@voice-agent/src/italian_regex.py
@voice-agent/src/entity_extractor.py
@voice-agent/tests/test_guardrails.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Expand VERTICAL_SERVICES and VERTICAL_GUARDRAILS for wellness and medico in italian_regex.py</name>
  <files>voice-agent/src/italian_regex.py</files>
  <action>
IMPORTANT: This task operates on the same file as Wave A (Plan 01). Wave A modifies lines 229–295 (VERTICAL_SERVICES) and lines 767–885 (VERTICAL_GUARDRAILS). This task adds to those same sections. If Plan 01 has already run, your changes must be appended AFTER the "beauty" entry. If running in parallel with Plan 01, coordinate by targeting distinct insertion points: add "wellness" and "medico" after "beauty" in both dicts.

Read the current state of italian_regex.py before editing to find the correct insertion point.

STEP 1 — Expand VERTICAL_SERVICES with "wellness" and "medico" keys.

In VERTICAL_SERVICES dict, after the "beauty" key (or after "auto" key if Wave A has not run yet), add:

For "wellness" — use the existing "palestra" dict as the base, then extend comprehensively. Use your encyclopedic knowledge of Italian fitness and wellness center terminology:
```
"wellness": {
    "abbonamento": existing palestra synonyms + add: "abbonamento trimestrale", "abbonamento semestrale", "prova gratuita", "ingresso singolo", "carnet ingressi", "pacchetto ingressi",
    "personal_training": existing + add: "seduta individuale PT", "allenamento domicilio", "programma personalizzato", "scheda allenamento", "valutazione composizione corporea", "plicometria", "test VO2 max", "consulenza fitness",
    "corso_gruppo": existing + add: "lezione collettiva", "corso settimanale", "lezione di prova",
    "yoga": existing + add: "yin yoga", "yoga nidra", "meditazione guidata", "pranayama", "hot yoga", "restorative yoga", "lezione privata yoga", "yoga flow",
    "pilates": existing + add: "pilates posturale", "pilates reformer", "pilates matwork", "lezione privata pilates",
    "spinning": existing,
    "crossfit": existing + add: "WOD", "AMRAP", "EMOM", "metcon", "functional training", "fondamentali crossfit", "open gym", "comp prep", "cross training", "allenamento funzionale",
    "nuoto": existing + add: "corsia riservata", "corso nuoto adulti", "corso baby nuoto", "nuoto libero", "acquacorrida", "master nuoto", "vasca 25m", "vasca 50m",
    "boxe": existing + add: "judo", "karate", "jiu-jitsu", "BJJ", "muay thai", "kickboxing", "MMA", "krav maga", "arte marziale", "kata", "kumite", "randori",
    "danza": existing + add: "corso di ballo", "latin dance", "salsa", "ballroom",
    "sala_pesi": existing + add: "allenamento con i pesi", "free weights", "area pesi liberi", "powerlifting",
    "massaggio": existing + add: "massaggio sportivo post-allenamento", "massaggio recupero",
    "sauna": existing + add: "area umida", "zona relax", "bagno turco palestra",
    NEW "arti_marziali": ["judo", "karate", "jiu-jitsu", "BJJ", "brazilian jiu-jitsu", "muay thai", "kickboxing", "MMA", "arti marziali miste", "krav maga", "kata", "kumite", "randori", "cintura nera", "cintura colorata"],
    NEW "piscina": ["vasca da 25m", "vasca da 50m", "corsia riservata", "nuoto libero", "acquagym", "baby nuoto", "corso nuoto", "acquacorrida", "acqua fitness", "master nuoto", "idrobike"],
}
```

For "medico" — use the existing "medical" dict as the base, then extend comprehensively. Use your encyclopedic knowledge of Italian medical, dental, physiotherapy, and specialist terminology:
```
"medico": {
    "visita": existing medical synonyms + add: "appuntamento dottore", "visita dal medico", "visita di controllo",
    "controllo": existing + add: "follow up", "revisione clinica",
    "esame": existing + add: "esame diagnostico", "esame strumentale", "tac", "scintigrafia", "spirometria",
    "vaccinazione": existing,
    "terapia": existing + add: "ciclo di fisioterapia", "ciclo di cure", "trattamento riabilitativo",
    "odontoiatria": existing + add: "ablazione tartaro", "sbiancamento denti", "bite notturno", "bruxismo", "chirurgia orale", "estrazione del giudizio", "impianto dentale", "corona dentale", "bridge dentale", "invisalign", "aligner dentale", "ortodonzia",
    "oculistica": existing,
    "dermatologia": existing + add: "visita dermatologica mole", "mappatura nei completa", "crioterapia dermatologica",
    "cardiologia": existing + add: "visita cardiologica", "monitoraggio pressione", "test da sforzo",
    "ortopedia": existing + add: "visita ortopedica", "infiltrazione cortisone", "visita colonna vertebrale",
    "ginecologia": existing + add: "colposcopia", "visita senologica", "mammografia",
    "pediatria": existing,
    "certificato": existing,
    NEW "fisioterapia": ["fisioterapia", "fisioterapia posturale", "rieducazione motoria", "riabilitazione", "tecarterapia", "ultrasuoni terapia", "TENS", "cerotti cinesiologici", "kinesiotaping", "linfodrenaggio manuale", "onde d'urto", "dry needling", "mobilizzazione articolare", "manipolazione vertebrale"],
    NEW "osteopata": ["osteopata", "osteopatia", "manipolazione osteopatica", "trattamento cranio-sacrale", "osteopatia viscerale", "manipolazione strutturale", "trattamento osteopatico"],
    NEW "psicologo": ["psicologo", "psicoterapeuta", "psicoterapia", "terapia cognitivo-comportamentale", "TCC", "EMDR", "colloquio di valutazione", "seduta di coppia", "terapia di coppia", "terapia online", "supporto psicologico", "follow-up psicologico"],
    NEW "nutrizionista": ["nutrizionista", "dietologo", "piano alimentare", "dieta personalizzata", "analisi bioimpedenziometrica", "BIA", "consulenza nutrizionale", "alimentazione sportiva", "intolleranze alimentari"],
    NEW "podologo": ["podologo", "podologia", "plantari su misura", "correzione unghia incarnita", "trattamento calli", "verruca plantare", "analisi del passo", "visita podologica"],
}
```

After the closing `}` of VERTICAL_SERVICES, add legacy aliases AFTER any aliases added by Wave A:
```python
VERTICAL_SERVICES["palestra"] = VERTICAL_SERVICES["wellness"]
VERTICAL_SERVICES["medical"] = VERTICAL_SERVICES["medico"]
```

STEP 2 — Expand VERTICAL_GUARDRAILS with "wellness" and "medico" keys.

In VERTICAL_GUARDRAILS, after the "beauty" entry (or after "auto" if Wave A not run), add:

For "wellness" guardrails (blocks: hair taglio/tinta, beauty nail, auto, medical prescriptions/ricette, professionale):
```python
"wellness": [
    # Hair OOS
    r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino|scalato))\b",
    r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici)\b",
    r"\b(?:messa\s+in\s+piega|piega\s+capelli|acconciatura\s+sposa)\b",
    r"\b(?:trattamento\s+capelli|cheratina\s+capelli|extension\s+capelli)\b",
    r"\b(?:balayage\s+capelli|meches\s+capelli)\b",
    # Beauty OOS (beauty treatments — not wellness services)
    r"\b(?:ricostruzione\s+unghie|ricostruzione\s+gel)\b",
    r"\b(?:epilazione\s+laser|laser\s+diodo|luce\s+pulsata)\b",
    r"\b(?:pulizia\s+viso|peeling\s+viso|radiofrequenza\s+viso)\b",
    # Auto OOS
    r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
    r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi))\b",
    r"\b(?:revisione\s+auto|tagliando\s+auto)\b",
    r"\bfar[ei]?\s+(?:il\s+)?tagliando\b",
    r"\b(?:dal\s+meccanico|portare\s+la\s+macchina)\b",
    # Medical prescriptions/ricette OOS (but NOT physiotherapy — valid in wellness context)
    r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
    r"\b(?:visita\s+(?:cardiologica|dermatologica|oculistica|ginecologica))\b",
    r"\b(?:esame\s+del\s+sangue|analisi\s+del\s+sangue)\b",
    r"\b(?:certificato\s+(?:medico|idoneità))\b",
    # Professionale OOS
    r"\b(?:dichiarazione\s+dei\s+redditi|consulenza\s+fiscale|consulenza\s+legale)\b",
    r"\b(?:apertura\s+partita\s+IVA|apertura\s+P\.?\s*IVA)\b",
],
```

For "medico" guardrails (blocks: hair, beauty nail/ceretta, auto, palestra fitness):
```python
"medico": [
    # Hair OOS
    r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino))\b",
    r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici)\b",
    r"\b(?:messa\s+in\s+piega|piega\s+capelli)\b",
    r"\b(?:(?:la\s+|una?\s+|fare\s+(?:la\s+)?|prenotare\s+(?:una?\s+)?)(?:manicure|pedicure)|manicure\s+\w+|pedicure\s+\w+|nail\s+art|semipermanente\s+(?:mani|piedi))\b",
    r"\b(?:ceretta\s+(?:gambe|braccia|inguine|ascelle)|depilazione\s+(?:laser|integrale|corpo|gambe)|epilazione\s+(?:laser|definitiva|gambe|braccia))\b",
    r"\b(?:trucco\s+sposa|acconciatura\s+sposa)\b",
    # Palestra/fitness OOS
    r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
    r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning|zumba))\b",
    r"\b(?:personal\s+trainer|personal\s+training)\b",
    r"\b(?:sala\s+pesi|body\s+building)\b",
    r"\b(?:allenamento\s+(?:funzionale|personalizzato)|scheda\s+allenamento)\b",
    # Auto OOS
    r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
    r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi))\b",
    r"\b(?:revisione\s+auto|tagliando\s+auto|carrozzeria)\b",
    r"\bfar[ei]?\s+(?:il\s+)?tagliando\b",
    r"\b(?:cambiar[ei]|cambia(?:re)?)\s+(?:l['''\u2019]?\s*)?olio\b",
    r"\bfar[ei]?\s+(?:il\s+)?cambio\s+(?:dell['''\u2019]?\s*)?olio\b",
    r"\bdal\s+meccanico\b",
    # Professionale OOS
    r"\b(?:dichiarazione\s+dei\s+redditi|consulenza\s+fiscale|consulenza\s+legale)\b",
],
```

After adding both new keys, add legacy aliases AFTER the dict closing `}` (after any aliases added by Wave A):
```python
VERTICAL_GUARDRAILS["palestra"] = VERTICAL_GUARDRAILS["wellness"]
VERTICAL_GUARDRAILS["medical"] = VERTICAL_GUARDRAILS["medico"]
```

STEP 3 — Add _GUARDRAIL_RESPONSES entries.

In `_GUARDRAIL_RESPONSES`, add before the closing brace:
```python
"wellness": "Mi occupo di prenotazioni per il centro fitness. Posso aiutarla con corsi, abbonamenti, personal training, nuoto o arti marziali?",
"medico": "Mi occupo di prenotazioni per lo studio medico. Posso aiutarla con visite, esami, fisioterapia, odontoiatria o consulenze specialistiche?",
```

IMPORTANT constraints:
- Do NOT remove or change "salone", "palestra", "medical", "auto" existing entries.
- Keep the existing `_GUARDRAIL_COMPILED` derivation unchanged — it automatically picks up new keys.
- After adding "medico" key, `_GUARDRAIL_COMPILED` will have both "medical" (legacy) and "medico" (new). Both work.
- Multi-word patterns only (architectural rule). No single-word guardrail patterns.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.italian_regex import VERTICAL_SERVICES, VERTICAL_GUARDRAILS, check_vertical_guardrail

# Test wellness
print('wellness keys:', list(VERTICAL_SERVICES['wellness'].keys()))
r1 = check_vertical_guardrail('taglio capelli donna', 'wellness')
print('wellness blocks hair OOS:', r1.blocked)
r2 = check_vertical_guardrail('corso di yoga mattutino', 'wellness')
print('wellness allows yoga:', not r2.blocked)

# Test medico
print('medico keys:', list(VERTICAL_SERVICES['medico'].keys()))
r3 = check_vertical_guardrail('abbonamento mensile palestra', 'medico')
print('medico blocks palestra OOS:', r3.blocked)
r4 = check_vertical_guardrail('fisioterapia posturale', 'medico')
print('medico allows fisioterapia:', not r4.blocked)

# Test legacy aliases
print('palestra alias ok:', 'palestra' in VERTICAL_SERVICES and VERTICAL_SERVICES['palestra'] is VERTICAL_SERVICES['wellness'])
print('medical alias ok:', 'medical' in VERTICAL_SERVICES and VERTICAL_SERVICES['medical'] is VERTICAL_SERVICES['medico'])
"
```
Expected: wellness keys listed (15+), wellness blocks hair OOS: True, wellness allows yoga: True, medico keys listed (18+), medico blocks palestra: True, medico allows fisioterapia: True, both aliases True
  </verify>
  <done>
- VERTICAL_SERVICES["wellness"] has ≥15 service groups
- VERTICAL_SERVICES["medico"] has ≥18 service groups (extends medical baseline + fisioterapia/osteopata/psicologo/nutrizionista/podologo)
- Legacy aliases: palestra → wellness, medical → medico in both VERTICAL_SERVICES and VERTICAL_GUARDRAILS
- VERTICAL_GUARDRAILS["wellness"] has ≥18 multi-word patterns
- VERTICAL_GUARDRAILS["medico"] has ≥17 multi-word patterns
- _GUARDRAIL_RESPONSES has entries for "wellness" and "medico"
- Python import succeeds, zero errors
  </done>
</task>

<task type="auto">
  <name>Task 2: Extend _MEDICAL_SPECIALTIES and add _WELLNESS_SUB_VERTICAL_KEYWORDS in entity_extractor.py</name>
  <files>voice-agent/src/entity_extractor.py</files>
  <action>
IMPORTANT: This task operates on the same file as Wave A (Plan 01). Plan 01 adds sub_vertical field to VerticalEntities and adds elif branches for hair/beauty. Read the current state of the file before editing to find the correct state.

STEP 1 — Extend _MEDICAL_SPECIALTIES dict.

Find `_MEDICAL_SPECIALTIES` dict in entity_extractor.py. It currently covers 10 specialties (cardiologia, dermatologia, ortopedia, ginecologia, oculistica, odontoiatria, pediatria, urologia, neurologia, gastroenterologia). Add the missing sub-verticals INSIDE the dict (as new keys):

```python
"fisioterapia": ["fisioterapia", "fisioterapista", "fisio", "riabilitazione", "rieducazione",
                  "tecarterapia", "ultrasuoni terapia", "kinesiotaping", "onde d'urto", "dry needling"],
"osteopata": ["osteopata", "osteopatia", "trattamento osteopatico", "cranio-sacrale",
               "osteopatia viscerale", "manipolazione osteopatica"],
"psicologo": ["psicologo", "psicoterapeuta", "psicoterapia", "TCC", "EMDR", "terapia cognitivo-comportamentale",
               "supporto psicologico", "seduta di coppia", "terapia di coppia"],
"nutrizionista": ["nutrizionista", "dietologo", "dieta personalizzata", "piano alimentare",
                   "BIA", "bioimpedenziometrica", "alimentazione sportiva"],
"podologo": ["podologo", "podologia", "plantari", "unghia incarnita", "calli", "verruca plantare",
              "analisi del passo"],
```

STEP 2 — Add _WELLNESS_SUB_VERTICAL_KEYWORDS dict.

After the _HAIR_SUB_VERTICAL_KEYWORDS and _BEAUTY_SERVICE_KEYWORDS dicts added by Wave A (or after _MEDICAL_SPECIALTIES if Wave A not yet run), insert:

```python
# =============================================================================
# WELLNESS SUB-VERTICAL KEYWORDS
# =============================================================================
_WELLNESS_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "personal_trainer": ["personal trainer", "PT", "personal training", "allenamento personalizzato",
                          "programma personalizzato", "scheda allenamento", "plicometria",
                          "test VO2 max", "valutazione composizione corporea", "allenamento domicilio"],
    "yoga_pilates": ["yoga", "pilates", "yin yoga", "yoga nidra", "hot yoga", "pranayama",
                      "meditazione guidata", "pilates posturale", "pilates reformer", "restorative yoga"],
    "crossfit": ["crossfit", "WOD", "AMRAP", "EMOM", "metcon", "functional training",
                  "fondamentali crossfit", "open gym", "cross training"],
    "piscina": ["piscina", "nuoto", "corsia riservata", "vasca da 25m", "vasca da 50m",
                 "baby nuoto", "acquacorrida", "master nuoto", "nuoto libero", "acquagym"],
    "arti_marziali": ["judo", "karate", "jiu-jitsu", "BJJ", "muay thai", "kickboxing",
                       "MMA", "krav maga", "kata", "kumite", "randori", "arti marziali"],
}
```

STEP 3 — Add elif branches for wellness and medico in extract_vertical_entities().

Find `extract_vertical_entities()`. After the elif branches for hair and beauty (added by Wave A), or after the `elif vertical == "auto":` block if Wave A not run, add:

```python
    elif vertical in ("wellness", "palestra"):
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _WELLNESS_SUB_VERTICAL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    elif vertical in ("medico",):
        # Extended medical specialty detection using _MEDICAL_SPECIALTIES
        # (Same logic as "medical" branch, reuses existing _MEDICAL_SPECIALTIES now extended)
        text_lower_strip = text.strip().lower()
        for specialty, keywords in _MEDICAL_SPECIALTIES.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.specialty = specialty
                    break
            if result.specialty:
                break
        # Urgency and visit_type detection (same as medical)
        for pattern, urgency_level in _MEDICAL_URGENCY_PATTERNS:
            if pattern.search(text):
                result.urgency = urgency_level
                break
        for vtype, pattern in _MEDICAL_VISIT_COMPILED.items():
            if pattern.search(text):
                result.visit_type = vtype
                break
```

Also verify that the existing `if vertical in ("medical", "medico"):` guard (updated in Wave A, or still `if vertical == "medical":`) is correct. If Wave A updated it to `if vertical in ("medical", "medico"):`, remove the new `elif vertical in ("medico",):` branch and instead ensure the combined branch handles both. If Wave A has NOT run, add this guard directly:
- Change `if vertical == "medical":` to `if vertical in ("medical", "medico"):` to handle both keys in one branch.

The safest approach: read the current state of extract_vertical_entities() and conditionally either:
- If the guard is already `if vertical in ("medical", "medico"):` → add only the wellness branch
- If the guard is still `if vertical == "medical":` → update it AND add the wellness branch

Do NOT duplicate medical logic — reuse the existing block by extending the condition.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.entity_extractor import extract_vertical_entities

# Test medico specialty detection (new keys)
r1 = extract_vertical_entities('ho bisogno di fisioterapia posturale', 'medico')
print('medico fisioterapia:', r1.specialty)

r2 = extract_vertical_entities('seduta psicologo con TCC', 'medico')
print('medico psicologo:', r2.specialty)

r3 = extract_vertical_entities('nutrizionista piano alimentare BIA', 'medico')
print('medico nutrizionista:', r3.specialty)

r4 = extract_vertical_entities('podologo unghia incarnita', 'medico')
print('medico podologo:', r4.specialty)

# Test medical legacy key still works
r5 = extract_vertical_entities('visita cardiologica urgente', 'medical')
print('medical legacy specialty:', r5.specialty)
print('medical legacy urgency:', r5.urgency)

# Test wellness sub-vertical
r6 = extract_vertical_entities('corso di yoga nidra', 'wellness')
print('wellness yoga_pilates:', r6.sub_vertical)

r7 = extract_vertical_entities('WOD crossfit domani mattina', 'wellness')
print('wellness crossfit:', r7.sub_vertical)

r8 = extract_vertical_entities('corsia riservata piscina', 'wellness')
print('wellness piscina:', r8.sub_vertical)
"
```
Expected: fisioterapia: fisioterapia, psicologo: psicologo, nutrizionista: nutrizionista, podologo: podologo, medical legacy: cardiologia/urgente, wellness yoga_pilates: yoga_pilates, crossfit: crossfit, piscina: piscina
  </verify>
  <done>
- _MEDICAL_SPECIALTIES extended with fisioterapia, osteopata, psicologo, nutrizionista, podologo
- _WELLNESS_SUB_VERTICAL_KEYWORDS dict added with 5 sub-vertical keys
- extract_vertical_entities() handles wellness/palestra and medico/medical verticals
- Existing medical specialty+urgency+visit_type extraction unaffected
- Python import succeeds, zero errors
  </done>
</task>

<task type="auto">
  <name>Task 3: Create test_wellness_medico_nlu.py with ≥50 parametrized test cases</name>
  <files>voice-agent/tests/test_wellness_medico_nlu.py</files>
  <action>
Create `voice-agent/tests/test_wellness_medico_nlu.py`. Follow the exact structure and import pattern from `voice-agent/tests/test_guardrails.py`.

Module-level docstring:
```python
"""
Tests for Wave B NLU patterns: wellness and medico verticals.
Phase: f-sara-nlu-patterns
Wave: 1 (parallel with Wave A hair+beauty, Wave C auto+professionale)
"""
```

Include these test classes:

1. **TestWellnessGuardrails**:
   - `test_wellness_blocks_hair_oos` — parametrize on ≥6 hair inputs (blocked=True)
     Examples: "taglio capelli donna", "tinta capelli scura", "messa in piega", "extension capelli cheratina", "ritocco radici bianchi", "trattamento capelli keratina"
   - `test_wellness_blocks_auto_oos` — parametrize on ≥5 auto inputs (blocked=True)
     Examples: "cambio olio motore", "tagliando auto scaduto", "cambio gomme invernali", "portare la macchina dal meccanico", "revisione auto ministeriale"
   - `test_wellness_blocks_medical_oos` — parametrize on ≥4 medical prescriptions (blocked=True)
     Examples: "ricetta medica rinnovo", "visita cardiologica urgente", "esame del sangue", "certificato idoneità" — NOTE: "fisioterapia" alone is NOT blocked in wellness (it is a valid service)
   - `test_wellness_allows_in_scope` — parametrize on ≥15 valid wellness inputs (blocked=False)
     Examples: "corso di yoga mattutino", "pilates posturale", "yin yoga", "WOD crossfit", "AMRAP", "personal trainer disponibile", "scheda allenamento personalizzata", "corsia riservata piscina", "baby nuoto corso", "acquacorrida", "judo cintura", "BJJ muay thai", "abbonamento mensile", "sala pesi", "kickboxing"
   - `test_wellness_legacy_palestra_key` — same blocked inputs pass with "palestra" key too (≥5 cases)

2. **TestMedicoGuardrails**:
   - `test_medico_blocks_hair_oos` — parametrize on ≥6 hair inputs (blocked=True)
     Examples: "taglio capelli donna", "tinta capelli biondi", "messa in piega", "la manicure mani", "ceretta gambe completa", "trucco sposa"
   - `test_medico_blocks_palestra_oos` — parametrize on ≥5 palestra inputs (blocked=True)
     Examples: "abbonamento mensile palestra", "corso di yoga", "personal trainer", "sala pesi attrezzata", "allenamento funzionale personalizzato"
   - `test_medico_blocks_auto_oos` — parametrize on ≥4 auto inputs (blocked=True)
     Examples: "cambio olio", "fare il tagliando", "dal meccanico", "cambio gomme invernali"
   - `test_medico_allows_in_scope` — parametrize on ≥15 valid medico inputs (blocked=False)
     Examples: "visita medica", "consulto specialistico", "esame del sangue", "fisioterapia posturale", "ciclo di fisioterapia", "osteopatia manipolazione", "seduta psicologo", "terapia cognitivo-comportamentale", "nutrizionista piano alimentare", "podologia plantari", "dentista pulizia denti", "sbiancamento denti", "psicoterapeuta EMDR", "analisi bioimpedenziometrica BIA", "invisalign aligner"
   - `test_medico_legacy_medical_key` — same blocked inputs pass with "medical" key too (≥5 cases)

3. **TestWellnessEntityExtraction**:
   - `test_wellness_sub_vertical_detection` — parametrize on (text, expected_sub_vertical):
     ("corso di yoga nidra", "yoga_pilates"), ("hot yoga lezione", "yoga_pilates"),
     ("pilates posturale lezione", "yoga_pilates"),
     ("WOD crossfit mattina", "crossfit"), ("AMRAP metcon", "crossfit"),
     ("personal trainer scheda allenamento", "personal_trainer"), ("plicometria test VO2 max", "personal_trainer"),
     ("corsia riservata piscina", "piscina"), ("baby nuoto corso", "piscina"),
     ("judo kata kumite", "arti_marziali"), ("BJJ muay thai", "arti_marziali")
   - `test_wellness_unknown_returns_none` — inputs with no sub-vertical keywords return sub_vertical=None
   - `test_palestra_alias_entity_extraction` — same tests passing vertical="palestra"

4. **TestMedicoEntityExtraction**:
   - `test_medico_specialty_detection` — parametrize on (text, expected_specialty):
     ("fisioterapia posturale", "fisioterapia"), ("tecarterapia trattamento", "fisioterapia"),
     ("seduta psicologo TCC", "psicologo"), ("EMDR terapia", "psicologo"),
     ("nutrizionista BIA analisi", "nutrizionista"), ("piano alimentare personalizzato", "nutrizionista"),
     ("podologo plantari", "podologo"), ("verruca plantare trattamento", "podologo"),
     ("osteopata manipolazione", "osteopata"), ("trattamento cranio-sacrale", "osteopata"),
     ("dentista sbiancamento", "odontoiatria"), ("invisalign aligner", "odontoiatria")
   - `test_medico_legacy_medical_specialty` — same specialty detection works with vertical="medical"
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_wellness_medico_nlu.py -v 2>&1 | tail -30
```
Expected: All tests PASS, 0 failed. Count ≥50 test cases.

Run existing tests for regressions:
```bash
python -m pytest tests/test_guardrails.py tests/test_f02_vertical_fixes.py -v 2>&1 | tail -20
```
Expected: All pass, no regressions.
  </verify>
  <done>
- test_wellness_medico_nlu.py exists with ≥50 parametrized test cases
- All test cases PASS on MacBook
- TestWellnessGuardrails: ≥30 cases
- TestMedicoGuardrails: ≥30 cases
- TestWellnessEntityExtraction: ≥13 cases
- TestMedicoEntityExtraction: ≥14 cases
- Existing tests pass, no regressions
  </done>
</task>

</tasks>

<verification>
Run full verification on MacBook:
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_wellness_medico_nlu.py tests/test_guardrails.py tests/test_f02_vertical_fixes.py tests/test_entity_extractor.py -v 2>&1 | tail -30
```
All tests must pass. No regressions from existing tests.
</verification>

<success_criteria>
- VERTICAL_SERVICES has "wellness" (15+ groups) and "medico" (18+ groups)
- Legacy aliases: palestra → wellness, medical → medico in both dicts
- VERTICAL_GUARDRAILS has "wellness" and "medico" with multi-word patterns only
- _MEDICAL_SPECIALTIES extended with fisioterapia, osteopata, psicologo, nutrizionista, podologo
- _WELLNESS_SUB_VERTICAL_KEYWORDS added with 5 sub-vertical keys
- extract_vertical_entities() handles wellness/palestra and medico/medical
- test_wellness_medico_nlu.py: ≥50 test cases, all PASS
- Existing tests pass, no regressions
</success_criteria>

<output>
After completion, create `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-02-SUMMARY.md`
</output>
