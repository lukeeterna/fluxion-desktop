---
phase: f-sara-nlu-patterns
plan: "03"
type: execute
wave: 3
depends_on:
  - "01"
  - "02"
files_modified:
  - voice-agent/src/italian_regex.py
  - voice-agent/src/entity_extractor.py
  - voice-agent/tests/test_auto_professionale_nlu.py
autonomous: true

must_haves:
  truths:
    - "check_vertical_guardrail(text, 'auto') returns blocked=True for OOS inputs (hair, beauty, medical, wellness) — extended from current 4-pattern set"
    - "check_vertical_guardrail(text, 'auto') returns blocked=False for extended auto sub-verticals (carrozzeria, elettrauto, gommista, revisioni, detailing)"
    - "check_vertical_guardrail(text, 'professionale') returns blocked=True for OOS inputs (hair, beauty, auto/meccanico, medical, wellness)"
    - "check_vertical_guardrail(text, 'professionale') returns blocked=False for all professionale inputs (commercialista, avvocato, consulente, agenzia, architetto)"
    - "DURATION_MAP dict exists in italian_regex.py with duration estimates for all 6 macro-verticals"
    - "OPERATOR_ROLES dict exists in italian_regex.py with role terms per vertical"
    - "extract_vertical_entities(text, 'auto') returns sub_vertical for carrozzeria, elettrauto, gommista, detailing"
    - "extract_vertical_entities(text, 'professionale') returns sub_vertical for commercialista, avvocato, architetto"
    - "pytest test_auto_professionale_nlu.py passes with ≥50 test cases, 0 failures"
  artifacts:
    - path: "voice-agent/src/italian_regex.py"
      provides: "Extended VERTICAL_SERVICES['auto'], new VERTICAL_SERVICES['professionale'], VERTICAL_GUARDRAILS['professionale'], extended VERTICAL_GUARDRAILS['auto'], DURATION_MAP, OPERATOR_ROLES"
      contains: "DURATION_MAP"
    - path: "voice-agent/src/entity_extractor.py"
      provides: "_AUTO_SUB_VERTICAL_KEYWORDS, _PROFESSIONALE_SERVICE_KEYWORDS, elif branches for professionale"
      contains: "_AUTO_SUB_VERTICAL_KEYWORDS"
    - path: "voice-agent/tests/test_auto_professionale_nlu.py"
      provides: "Parametrized test classes for extended auto + professionale guardrails and entity extraction"
      contains: "TestAutoExtendedGuardrails"
  key_links:
    - from: "voice-agent/tests/test_auto_professionale_nlu.py"
      to: "voice-agent/src/italian_regex.py"
      via: "from italian_regex import check_vertical_guardrail, VERTICAL_SERVICES, DURATION_MAP, OPERATOR_ROLES"
      pattern: "check_vertical_guardrail"
    - from: "voice-agent/tests/test_auto_professionale_nlu.py"
      to: "voice-agent/src/entity_extractor.py"
      via: "from entity_extractor import extract_vertical_entities"
      pattern: "extract_vertical_entities"
---

<objective>
Expand Sara's NLU layer with extended auto sub-vertical coverage and complete professionale vertical (zero existing entries). Add DURATION_MAP and OPERATOR_ROLES data structures for FSM enrichment. Extend entity extraction for auto sub-verticals and create professionale entity extraction.

Purpose: Today auto has 13 service groups covering officina_meccanica well but missing carrozzeria/elettrauto/gommista/revisioni/detailing sub-verticals. Professionale (commercialista, avvocato, architetto, consulente, agenzia) has zero coverage at all layers. After this plan, both verticals are complete.

Output: Expanded italian_regex.py (auto extended + professionale new + DURATION_MAP + OPERATOR_ROLES) + entity_extractor.py (auto sub-verticals + professionale) + test_auto_professionale_nlu.py with ≥50 parametrized test cases.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-RESEARCH.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-01-SUMMARY.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-02-SUMMARY.md

@voice-agent/src/italian_regex.py
@voice-agent/src/entity_extractor.py
@voice-agent/tests/test_guardrails.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Extend VERTICAL_SERVICES auto + add professionale, add DURATION_MAP, OPERATOR_ROLES, extend guardrails in italian_regex.py</name>
  <files>voice-agent/src/italian_regex.py</files>
  <action>
Plans 01 and 02 have already run. Read the current state of italian_regex.py to confirm "hair", "beauty", "wellness", "medico" keys exist in VERTICAL_SERVICES and VERTICAL_GUARDRAILS. Target only: extending the existing "auto" dict, adding "professionale" key, adding DURATION_MAP and OPERATOR_ROLES after VERTICAL_SERVICES, extending VERTICAL_GUARDRAILS "auto" and adding "professionale", and adding _GUARDRAIL_RESPONSES entries.

STEP 1 — Extend VERTICAL_SERVICES["auto"].

The existing "auto" dict (lines 280–295) covers: tagliando, riparazione, cambio_olio, freni, gomme, batteria, ac, carrozzeria, elettronica, frizione, sospensioni, scarico, revisione. Extend it with comprehensive Italian sub-vertical terminology. Use your encyclopedic knowledge of Italian automotive service center (officina, carrozzeria, elettrauto, gommista, revisioni, detailing) terminology:

Add new keys to the existing "auto" dict — do NOT duplicate existing keys, only add new ones:
- "carrozzeria_servizi": ["perizia danni", "stima danni", "preventivo carrozzeria", "sostituzione parabrezza", "parabrezza incrinato", "lucidatura carrozzeria", "polish carrozzeria", "verniciatura parziale", "ritocco vernice", "tintura paraurti", "ritiro e consegna", "auto cortesia"]
- "elettrauto": ["diagnosi OBD", "diagnosi centralina", "centralina motore", "impianto hi-fi", "autoradio", "retrocamera", "sensori parcheggio", "GPS tracker", "immobilizer", "impianto GPL", "impianto metano", "convertire GPL", "convertire metano", "quadro strumenti"]
- "gommista_servizi": ["equilibratura ruote", "bilanciatura gomme", "convergenza ruote", "assetto ruote", "cambio stagionale gomme", "deposito gomme", "deposito stagionale", "riparazione foratura", "pressione gomme", "runflat", "TPMS sensori", "cerchi in lega"]
- "revisione_servizi": ["revisione ministeriale", "revisione obbligatoria", "revisione scaduta", "collaudo veicolo", "revisione straordinaria", "bollino blu", "libretto revisione", "data revisione", "revisione periodica"]
- "detailing": ["detailing auto", "lucidatura professionale", "cera auto", "ceramica auto", "protezione ceramica", "trattamento PPF", "wrapping auto", "car wrapping", "pellicola protezione vernice", "lavaggio ad ozono", "ozono abitacolo", "sanificazione ozono", "interno cuoio trattamento", "rivestimento interno", "nano ceramica"]

For "professionale" — create from scratch. Use your encyclopedic knowledge of Italian professional services (commercialista, avvocato, consulente, agenzia immobiliare, architetto, geometra):
- "commercialista": ["dichiarazione dei redditi", "730 dichiarazione", "Unico redditi", "modello F24", "busta paga", "cedolino stipendio", "apertura partita IVA", "apertura P.IVA", "chiusura partita IVA", "consulenza fiscale", "contabilità aziendale", "bilancio d'esercizio", "chiusura bilancio", "liquidazione IVA", "F24", "CU certificazione unica"]
- "avvocato": ["consulenza legale", "consulenza avvocato", "separazione consensuale", "divorzio", "divorzio breve", "contratto di locazione", "contratto di affitto", "tutela consumatori", "recupero crediti", "successione ereditaria", "testamento", "ricorso giudiziario", "parere legale", "mediazione civile", "diritto del lavoro"]
- "consulente": ["consulenza strategica", "business plan", "analisi di mercato", "piano industriale", "consulenza HR", "gestione risorse umane", "formazione aziendale", "audit aziendale", "due diligence", "piano marketing"]
- "agenzia_immobiliare": ["valutazione immobile", "stima immobile", "proposta d'acquisto", "compromesso acquisto", "rogito notarile", "visita immobile", "appuntamento per casa", "mutuo prima casa", "perizia immobiliare", "affitto commerciale", "locazione immobile"]
- "architetto": ["progetto ristrutturazione", "progetto ampliamento", "pratiche comunali", "DIA", "SCIA", "permesso di costruire", "computo metrico", "rendering 3D", "progetto interni", "sopralluogo tecnico", "perizia strutturale", "certificazione energetica"]

After the closing `}` of VERTICAL_SERVICES, and after any aliases from Plans 01/02, add:
```python
# Wave C: auto key unchanged (existing), professionale is new
# Note: professionale has no legacy alias (no prior key existed)
```
No new aliases needed for auto (key unchanged). No legacy alias for professionale.

STEP 2 — Add DURATION_MAP and OPERATOR_ROLES data structures.

After VERTICAL_SERVICES and aliases, add a new section:

```python
# =============================================================================
# 5b. DURATION_MAP — estimated service durations in minutes per vertical
# =============================================================================
# Data-only structure. Used for slot availability checks and FSM confirmation.
# Source: standard Italian service industry durations.
DURATION_MAP: Dict[str, Dict[str, int]] = {
    "hair": {
        "taglio": 30, "taglio_uomo": 20, "taglio_bambino": 25,
        "piega": 45, "colore": 90, "meches": 120, "balayage": 150,
        "trattamento": 45, "permanente": 90, "stiratura": 120,
        "extension": 180, "barba": 20, "barba_stilizzata": 30,
        "fade": 30, "correzione_colore": 120, "tricologo": 60,
        "manicure": 30, "pedicure": 45, "ceretta": 30, "trucco": 60,
        "acconciatura_sposa": 180,
    },
    "beauty": {
        "pulizia_viso": 60, "peeling": 45, "radiofrequenza_viso": 60,
        "dermaplaning": 45, "massaggio_viso": 30, "massaggio_corpo": 60,
        "linfodrenaggio": 60, "anticellulite": 60,
        "gel": 60, "semipermanente_unghie": 45, "nail_art": 75,
        "rimozione_gel": 30, "epilazione_laser": 30,
        "lettino_solare": 15, "circuito_spa": 120, "massaggio_spa": 90,
    },
    "wellness": {
        "abbonamento": 30, "personal_training": 60, "corso_gruppo": 60,
        "yoga": 60, "pilates": 60, "spinning": 45, "crossfit": 60,
        "nuoto": 45, "boxe": 60, "danza": 60, "sala_pesi": 60,
        "massaggio": 60, "sauna": 60, "arti_marziali": 60, "piscina": 45,
    },
    "medico": {
        "visita": 30, "controllo": 20, "esame": 45, "vaccinazione": 15,
        "terapia": 45, "odontoiatria": 60, "oculistica": 30,
        "dermatologia": 30, "cardiologia": 45, "ortopedia": 30,
        "ginecologia": 30, "pediatria": 20, "certificato": 15,
        "fisioterapia": 45, "osteopata": 60, "psicologo": 60,
        "nutrizionista": 45, "podologo": 30,
    },
    "auto": {
        "tagliando": 120, "riparazione": 120, "cambio_olio": 30,
        "freni": 90, "gomme": 60, "batteria": 30, "ac": 60,
        "carrozzeria": 480, "elettronica": 60, "frizione": 240,
        "sospensioni": 180, "scarico": 90, "revisione": 60,
        "carrozzeria_servizi": 480, "elettrauto": 120,
        "gommista_servizi": 60, "revisione_servizi": 60, "detailing": 180,
    },
    "professionale": {
        "commercialista": 60, "avvocato": 60, "consulente": 90,
        "agenzia_immobiliare": 60, "architetto": 90,
    },
}

# =============================================================================
# 5c. OPERATOR_ROLES — role titles per vertical (for operator entity extraction)
# =============================================================================
# Data-only structure. Enables Sara to extract "voglio con la dottoressa" etc.
OPERATOR_ROLES: Dict[str, List[str]] = {
    "hair": ["parrucchiere", "parrucchiera", "stilista", "colorista", "barbiere", "hair stylist",
              "acconciatore", "acconciatrice", "tricologo", "trichiologa"],
    "beauty": ["estetista", "estetologa", "nail artist", "nail technician", "beauty therapist",
                "epilazione laser", "operatrice spa", "massaggiatrice"],
    "wellness": ["personal trainer", "PT", "istruttore", "istruttrice", "coach", "trainer",
                  "insegnante yoga", "maestro yoga", "istruttore crossfit", "bagnino",
                  "maestro arti marziali", "insegnante pilates"],
    "medico": ["dottore", "dottoressa", "medico", "medica", "specialista", "fisioterapista",
                "fisio", "osteopata", "psicologo", "psicologa",
                "psicoterapeuta", "nutrizionista", "dietologa", "podologo", "podologa",
                "dentista", "ortodontista", "cardiologo"],
    "auto": ["meccanico", "carrozziere", "elettrauto", "gommista", "tecnico auto",
              "perito danni", "detailer"],
    "professionale": ["avvocato", "avvocatessa", "commercialista", "consulente", "architetto",
                       "geometra", "agente immobiliare", "notaio"],
}
```

STEP 3 — Extend VERTICAL_GUARDRAILS["auto"] and add VERTICAL_GUARDRAILS["professionale"].

The existing "auto" guardrail list (lines 855–870) blocks salone/palestra/medical patterns. Extend it by APPENDING to the existing list — do NOT replace:
Additional patterns for "auto":
```python
# Beauty OOS (added by Wave C)
r"\b(?:pulizia\s+viso|peeling\s+viso|radiofrequenza\s+(?:viso|corpo))\b",
r"\b(?:epilazione\s+laser|laser\s+diodo|luce\s+pulsata)\b",
r"\b(?:ricostruzione\s+unghie|ricostruzione\s+gel|nail\s+art)\b",
r"\b(?:massaggio\s+(?:ayurvedico|drenante|anticellulite|linfodrenaggio))\b",
# Professionale OOS
r"\b(?:dichiarazione\s+dei\s+redditi|modello\s+730|Unico\s+redditi)\b",
r"\b(?:consulenza\s+(?:fiscale|legale|tributaria))\b",
r"\b(?:apertura\s+partita\s+IVA|apertura\s+P\.?\s*IVA)\b",
```

Add new "professionale" guardrail key (all other verticals are OOS):
```python
"professionale": [
    # Hair OOS
    r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino))\b",
    r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici)\b",
    r"\b(?:messa\s+in\s+piega|piega\s+capelli|balayage\s+capelli)\b",
    r"\b(?:trattamento\s+capelli|extension\s+capelli|cheratina\s+capelli)\b",
    # Beauty OOS
    r"\b(?:pulizia\s+viso|peeling\s+viso|radiofrequenza\s+viso)\b",
    r"\b(?:epilazione\s+laser|luce\s+pulsata|laser\s+diodo)\b",
    r"\b(?:ricostruzione\s+unghie|ricostruzione\s+gel|nail\s+art)\b",
    r"\b(?:ceretta\s+(?:gambe|braccia|inguine)|depilazione\s+(?:laser|integrale))\b",
    # Wellness/palestra OOS
    r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
    r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning))\b",
    r"\b(?:personal\s+trainer|personal\s+training|sala\s+pesi)\b",
    # Medical OOS
    r"\b(?:visita\s+(?:medica|specialistica|cardiologica|dermatologica))\b",
    r"\b(?:esame\s+del\s+sangue|analisi\s+del\s+sangue)\b",
    r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
    r"\b(?:fisioterapia\s+(?:posturale|riabilitativa)|ciclo\s+di\s+fisioterapia)\b",
    # Auto OOS
    r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
    r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi))\b",
    r"\b(?:revisione\s+auto|tagliando\s+auto)\b",
    r"\bfar[ei]?\s+(?:il\s+)?tagliando\b",
    r"\b(?:dal\s+meccanico|portare\s+la\s+macchina)\b",
    r"\b(?:carrozzeria\s+auto|verniciatura\s+auto)\b",
],
```

Add _GUARDRAIL_RESPONSES entry for "professionale":
```python
"professionale": "Mi occupo di prenotazioni per lo studio professionale. Posso aiutarla con consulenze fiscali, legali, immobiliari o architettoniche?",
```

IMPORTANT: Do not touch the existing "salone", "palestra", "medical", "auto" keys. Extend "auto" by appending to its list — do not rewrite it.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.italian_regex import VERTICAL_SERVICES, VERTICAL_GUARDRAILS, DURATION_MAP, OPERATOR_ROLES, check_vertical_guardrail

# Test auto extended services
print('auto new keys present:', 'detailing' in VERTICAL_SERVICES['auto'] and 'elettrauto' in VERTICAL_SERVICES['auto'])

# Test professionale services
print('professionale keys:', list(VERTICAL_SERVICES.get('professionale', {}).keys()))

# Test DURATION_MAP
print('DURATION_MAP verticals:', list(DURATION_MAP.keys()))
print('hair taglio duration:', DURATION_MAP['hair']['taglio'])

# Test OPERATOR_ROLES
print('OPERATOR_ROLES verticals:', list(OPERATOR_ROLES.keys()))
print('medico roles present:', 'fisioterapista' in OPERATOR_ROLES['medico'])

# Test professionale guardrails
r1 = check_vertical_guardrail('voglio fare il tagliando', 'professionale')
print('professionale blocks auto OOS:', r1.blocked)
r2 = check_vertical_guardrail('dichiarazione dei redditi 730', 'professionale')
print('professionale allows commercialista:', not r2.blocked)
r3 = check_vertical_guardrail('consulenza legale separazione', 'professionale')
print('professionale allows avvocato:', not r3.blocked)
"
```
Expected: auto new keys: True, professionale keys listed (5), DURATION_MAP 6 verticals, hair taglio: 30, OPERATOR_ROLES 6 verticals, fisioterapista: True, professionale blocks: True, allows commercialista: True, allows avvocato: True

Also verify that "voglio fare il tagliando" is blocked by the 'hair' guardrail (regression check from Plan 01):
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.italian_regex import check_vertical_guardrail
r = check_vertical_guardrail('voglio fare il tagliando', 'hair')
print('hair blocks tagliando OOS:', r.blocked)
"
```
Expected: hair blocks tagliando OOS: True
  </verify>
  <done>
- VERTICAL_SERVICES["auto"] extended with carrozzeria_servizi, elettrauto, gommista_servizi, revisione_servizi, detailing (5 new groups)
- VERTICAL_SERVICES["professionale"] created with 5 sub-vertical groups and comprehensive Italian synonyms
- DURATION_MAP exists with all 6 macro-vertical keys and service duration estimates
- OPERATOR_ROLES exists with all 6 macro-vertical keys and role title lists
- VERTICAL_GUARDRAILS["auto"] extended with beauty + professionale OOS patterns
- VERTICAL_GUARDRAILS["professionale"] created with 20+ multi-word patterns
- _GUARDRAIL_RESPONSES has "professionale" entry
- Python import succeeds, zero errors
  </done>
</task>

<task type="auto">
  <name>Task 2: Add _AUTO_SUB_VERTICAL_KEYWORDS + _PROFESSIONALE_SERVICE_KEYWORDS and elif branches in entity_extractor.py</name>
  <files>voice-agent/src/entity_extractor.py</files>
  <action>
Plans 01 and 02 have already run. Read current state first. The file now has: sub_vertical field on VerticalEntities, _HAIR_SUB_VERTICAL_KEYWORDS, _BEAUTY_SERVICE_KEYWORDS, _WELLNESS_SUB_VERTICAL_KEYWORDS, extended _MEDICAL_SPECIALTIES, and elif branches for hair/beauty/wellness/medico. This task adds auto sub-vertical detection and professionale entity extraction.

STEP 1 — Add _AUTO_SUB_VERTICAL_KEYWORDS and _PROFESSIONALE_SERVICE_KEYWORDS dicts.

After the _WELLNESS_SUB_VERTICAL_KEYWORDS dict, add:

```python
# =============================================================================
# AUTO SUB-VERTICAL KEYWORDS
# =============================================================================
_AUTO_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "carrozzeria": ["perizia danni", "stima danni", "sostituzione parabrezza", "parabrezza",
                     "lucidatura carrozzeria", "polish", "verniciatura parziale", "ritocco vernice",
                     "tintura paraurti", "auto cortesia", "carrozziere"],
    "elettrauto": ["diagnosi OBD", "centralina motore", "impianto hi-fi", "autoradio",
                    "retrocamera", "sensori parcheggio", "GPS tracker", "immobilizer",
                    "impianto GPL", "impianto metano", "elettrauto"],
    "gommista": ["equilibratura", "bilanciatura gomme", "convergenza", "assetto ruote",
                  "cambio stagionale gomme", "deposito gomme", "foratura", "runflat",
                  "TPMS", "cerchi in lega", "gommista"],
    "revisioni": ["revisione ministeriale", "collaudo", "revisione obbligatoria",
                   "bollino blu", "libretto revisione", "revisione scaduta"],
    "detailing": ["detailing", "cera auto", "ceramica auto", "PPF", "wrapping",
                   "car wrapping", "ozono abitacolo", "sanificazione ozono",
                   "nano ceramica", "protezione ceramica"],
}

# =============================================================================
# PROFESSIONALE SERVICE KEYWORDS
# =============================================================================
_PROFESSIONALE_SERVICE_KEYWORDS: Dict[str, List[str]] = {
    "commercialista": ["dichiarazione dei redditi", "730", "Unico", "modello F24",
                        "busta paga", "apertura partita IVA", "apertura P.IVA",
                        "bilancio", "contabilità", "CU certificazione unica", "liquidazione IVA"],
    "avvocato": ["consulenza legale", "separazione", "divorzio", "contratto di locazione",
                  "contratto di affitto", "recupero crediti", "successione ereditaria",
                  "testamento", "ricorso", "parere legale", "mediazione civile"],
    "consulente": ["consulenza strategica", "business plan", "analisi di mercato",
                    "consulenza HR", "formazione aziendale", "due diligence"],
    "agenzia_immobiliare": ["valutazione immobile", "stima immobile", "proposta d'acquisto",
                              "visita immobile", "appuntamento per casa", "mutuo prima casa",
                              "perizia immobiliare", "affitto commerciale"],
    "architetto": ["progetto ristrutturazione", "DIA", "SCIA", "permesso di costruire",
                    "computo metrico", "rendering 3D", "progetto interni", "sopralluogo tecnico",
                    "certificazione energetica", "pratiche comunali"],
}
```

STEP 2 — Extend the auto elif branch in extract_vertical_entities().

Find the `elif vertical == "auto":` branch. The current branch extracts vehicle_plate and vehicle_brand. Extend it by APPENDING sub-vertical detection AFTER the brand extraction (before the branch ends):

```python
    elif vertical == "auto":
        # [existing targa + brand extraction code — keep unchanged]
        ...
        # NEW: Sub-vertical detection
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _AUTO_SUB_VERTICAL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break
```

Do NOT change the existing targa and brand extraction logic. Only append sub-vertical detection at the end of the auto branch.

STEP 3 — Add elif branch for professionale in extract_vertical_entities().

After the auto elif branch, add:

```python
    elif vertical == "professionale":
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _PROFESSIONALE_SERVICE_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break
```
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.entity_extractor import extract_vertical_entities

# Test auto sub-vertical detection
r1 = extract_vertical_entities('sostituzione parabrezza perizia danni', 'auto')
print('auto carrozzeria:', r1.sub_vertical)

r2 = extract_vertical_entities('diagnosi OBD centralina motore', 'auto')
print('auto elettrauto:', r2.sub_vertical)

r3 = extract_vertical_entities('equilibratura gomme convergenza', 'auto')
print('auto gommista:', r3.sub_vertical)

r4 = extract_vertical_entities('detailing cera ceramica auto', 'auto')
print('auto detailing:', r4.sub_vertical)

# Verify existing targa/brand extraction still works
r5 = extract_vertical_entities('ho la Fiat Panda targa AB123CD', 'auto')
print('auto targa:', r5.vehicle_plate, 'brand:', r5.vehicle_brand)

# Test professionale
r6 = extract_vertical_entities('dichiarazione dei redditi 730', 'professionale')
print('professionale commercialista:', r6.sub_vertical)

r7 = extract_vertical_entities('consulenza legale divorzio', 'professionale')
print('professionale avvocato:', r7.sub_vertical)

r8 = extract_vertical_entities('progetto ristrutturazione SCIA', 'professionale')
print('professionale architetto:', r8.sub_vertical)
"
```
Expected: carrozzeria, elettrauto, gommista, detailing, targa AB123CD + fiat brand, commercialista, avvocato, architetto
  </verify>
  <done>
- _AUTO_SUB_VERTICAL_KEYWORDS dict added with 5 sub-vertical keys
- _PROFESSIONALE_SERVICE_KEYWORDS dict added with 5 sub-vertical keys
- auto elif branch extended with sub-vertical detection (targa/brand extraction unchanged)
- professionale elif branch added
- Python import succeeds, zero errors
  </done>
</task>

<task type="auto">
  <name>Task 3: Create test_auto_professionale_nlu.py with ≥50 parametrized test cases</name>
  <files>voice-agent/tests/test_auto_professionale_nlu.py</files>
  <action>
Create `voice-agent/tests/test_auto_professionale_nlu.py`. Follow the structure from `voice-agent/tests/test_guardrails.py`.

Module-level docstring:
```python
"""
Tests for Wave C NLU patterns: extended auto and professionale verticals.
Phase: f-sara-nlu-patterns
Wave: 3 (sequential after Wave A hair+beauty, Wave B wellness+medico)
Also tests: DURATION_MAP and OPERATOR_ROLES data structures.
"""
```

Include these test classes:

1. **TestAutoExtendedGuardrails**:
   - `test_auto_still_blocks_salone_oos` — parametrize on ≥5 hair inputs (blocked=True) — verify existing patterns still work
     Examples: "taglio capelli donna", "tinta capelli", "messa in piega", "manicure mani", "ceretta gambe completa"
   - `test_auto_still_blocks_palestra_oos` — parametrize on ≥4 wellness inputs
     Examples: "abbonamento mensile palestra", "corso di yoga", "personal trainer", "sala pesi"
   - `test_auto_blocks_beauty_oos` — parametrize on ≥4 new beauty OOS patterns (blocked=True)
     Examples: "pulizia viso profonda", "epilazione laser gambe", "ricostruzione unghie gel", "radiofrequenza viso"
   - `test_auto_blocks_professionale_oos` — parametrize on ≥3 professionale OOS patterns
     Examples: "dichiarazione dei redditi", "consulenza fiscale", "apertura partita IVA"
   - `test_auto_allows_in_scope` — parametrize on ≥15 valid auto inputs (blocked=False)
     Examples: "tagliando scaduto", "cambio olio motore", "freni consumati", "perizia danni carrozzeria", "sostituzione parabrezza", "diagnosi OBD centralina", "impianto GPL", "equilibratura ruote", "convergenza assetto", "cambio stagionale gomme", "revisione ministeriale", "bollino blu", "detailing ceramica", "wrapping car", "ozono abitacolo"

2. **TestProffessionaleGuardrails**:
   - `test_professionale_blocks_hair_oos` — parametrize on ≥5 hair inputs (blocked=True)
   - `test_professionale_blocks_auto_oos` — parametrize on ≥5 auto inputs (blocked=True)
     Examples: "cambio olio", "tagliando auto", "dal meccanico", "revisione auto", "fare il tagliando"
   - `test_professionale_blocks_medical_oos` — parametrize on ≥4 medical inputs (blocked=True)
   - `test_professionale_blocks_wellness_oos` — parametrize on ≥4 wellness inputs (blocked=True)
   - `test_professionale_allows_in_scope` — parametrize on ≥15 valid professionale inputs (blocked=False)
     Examples: "dichiarazione dei redditi 730", "modello F24 pagamento", "apertura partita IVA", "busta paga dipendente", "bilancio aziendale", "consulenza legale", "separazione consensuale", "contratto di locazione", "recupero crediti", "testamento successione", "valutazione immobile", "proposta d'acquisto casa", "visita immobile domani", "progetto ristrutturazione bagno", "SCIA pratiche comunali"

3. **TestAutoEntityExtraction**:
   - `test_auto_sub_vertical_detection` — parametrize on (text, expected_sub_vertical):
     ("perizia danni parabrezza incrinato", "carrozzeria"),
     ("sostituzione parabrezza urgente", "carrozzeria"),
     ("diagnosi OBD centralina motore", "elettrauto"),
     ("impianto GPL conversione", "elettrauto"),
     ("equilibratura gomme convergenza", "gommista"),
     ("cambio stagionale deposito gomme", "gommista"),
     ("revisione ministeriale scaduta", "revisioni"),
     ("bollino blu collaudo", "revisioni"),
     ("detailing ceramica PPF wrapping", "detailing"),
     ("ozono sanificazione abitacolo", "detailing")
   - `test_auto_targa_brand_still_works` — verify vehicle_plate and vehicle_brand still extracted
     Examples: ("ho la Fiat targa AB123CD", "AB123CD", "fiat"), ("Toyota Yaris targata EF456GH", "EF456GH", "toyota")

4. **TestProffessionaleEntityExtraction**:
   - `test_professionale_sub_vertical_detection` — parametrize on (text, expected_sub_vertical):
     ("dichiarazione redditi 730 Unico", "commercialista"),
     ("modello F24 busta paga", "commercialista"),
     ("consulenza legale separazione consensuale", "avvocato"),
     ("contratto di locazione divorzio", "avvocato"),
     ("business plan analisi di mercato", "consulente"),
     ("formazione aziendale due diligence", "consulente"),
     ("valutazione immobile stima", "agenzia_immobiliare"),
     ("visita immobile proposta acquisto", "agenzia_immobiliare"),
     ("progetto ristrutturazione SCIA", "architetto"),
     ("permesso di costruire DIA pratiche", "architetto")

5. **TestDurationMap**:
   - `test_duration_map_has_all_verticals` — verify all 6 keys exist in DURATION_MAP
   - `test_duration_map_values_are_positive_ints` — spot check: hair/taglio=30, auto/cambio_olio=30, medico/visita=30
   - `test_operator_roles_has_all_verticals` — verify all 6 keys exist in OPERATOR_ROLES
   - `test_operator_roles_content` — spot check: "fisioterapista" in medico, "meccanico" in auto, "avvocato" in professionale
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_auto_professionale_nlu.py -v 2>&1 | tail -30
```
Expected: All PASS, 0 failed. Count ≥50 test cases.

Run existing auto guardrail tests for regressions:
```bash
python -m pytest tests/test_guardrails.py tests/test_f02_vertical_fixes.py -v 2>&1 | tail -20
```
Expected: All pass. The original "auto" key guardrail behavior must be unchanged.
  </verify>
  <done>
- test_auto_professionale_nlu.py exists with ≥50 parametrized test cases
- All PASS on MacBook
- TestAutoExtendedGuardrails: ≥31 cases (including regression + new)
- TestProffessionaleGuardrails: ≥33 cases
- TestAutoEntityExtraction: ≥12 cases
- TestProffessionaleEntityExtraction: ≥10 cases
- TestDurationMap: ≥4 cases
- Existing test_guardrails.py passes (auto key unchanged)
  </done>
</task>

</tasks>

<verification>
Run full Wave C verification on MacBook:
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_auto_professionale_nlu.py tests/test_guardrails.py -v 2>&1 | tail -30
```
All tests must pass. Original auto guardrail behavior preserved.
</verification>

<success_criteria>
- VERTICAL_SERVICES["auto"] extended with 5 new sub-vertical groups
- VERTICAL_SERVICES["professionale"] created with 5 groups and comprehensive Italian synonyms
- DURATION_MAP exists with 6 vertical keys and duration estimates (minutes) per service
- OPERATOR_ROLES exists with 6 vertical keys and Italian role title lists
- VERTICAL_GUARDRAILS["auto"] extended with beauty + professionale OOS patterns
- VERTICAL_GUARDRAILS["professionale"] created with 20+ multi-word OOS patterns
- entity_extractor.py: auto sub-vertical detection added, professionale elif branch added
- test_auto_professionale_nlu.py: ≥50 test cases, all PASS on MacBook
- Existing auto guardrail tests pass, no regressions
</success_criteria>

<output>
After completion, create `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-03-SUMMARY.md`
</output>
