---
phase: f-sara-nlu-patterns
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/italian_regex.py
  - voice-agent/src/entity_extractor.py
  - voice-agent/tests/test_hair_beauty_nlu.py
autonomous: true

must_haves:
  truths:
    - "check_vertical_guardrail(text, 'hair') returns blocked=True for OOS inputs (auto, medical, fitness)"
    - "check_vertical_guardrail(text, 'hair') returns blocked=False for all hair sub-vertical inputs (barbiere, color, extension, tricologo)"
    - "check_vertical_guardrail(text, 'beauty') returns blocked=True for OOS inputs (hair taglio, auto, medical)"
    - "check_vertical_guardrail(text, 'beauty') returns blocked=False for all beauty sub-vertical inputs (estetista viso, nail, epilazione laser, spa)"
    - "Legacy key 'salone' still works (40+ existing tests pass unchanged)"
    - "extract_vertical_entities(text, 'hair') returns sub_vertical field for barbiere/color/extension/tricologo inputs"
    - "extract_vertical_entities(text, 'beauty') returns sub_vertical field for nail/viso/corpo/laser inputs"
    - "pytest test_hair_beauty_nlu.py passes with ≥60 test cases, 0 failures"
  artifacts:
    - path: "voice-agent/src/italian_regex.py"
      provides: "VERTICAL_SERVICES['hair'], VERTICAL_SERVICES['beauty'], VERTICAL_GUARDRAILS['hair'], VERTICAL_GUARDRAILS['beauty'], legacy aliases salone/medical-cross"
      contains: "VERTICAL_SERVICES[\"hair\"]"
    - path: "voice-agent/src/entity_extractor.py"
      provides: "VerticalEntities.sub_vertical field, _HAIR_SUB_VERTICAL_KEYWORDS, _BEAUTY_SERVICE_KEYWORDS, elif hair/beauty branches in extract_vertical_entities()"
      contains: "sub_vertical"
    - path: "voice-agent/tests/test_hair_beauty_nlu.py"
      provides: "Parametrized test classes for hair + beauty guardrails and entity extraction"
      contains: "TestHairGuardrails"
  key_links:
    - from: "voice-agent/tests/test_hair_beauty_nlu.py"
      to: "voice-agent/src/italian_regex.py"
      via: "from italian_regex import check_vertical_guardrail, VERTICAL_SERVICES"
      pattern: "check_vertical_guardrail"
    - from: "voice-agent/tests/test_hair_beauty_nlu.py"
      to: "voice-agent/src/entity_extractor.py"
      via: "from entity_extractor import extract_vertical_entities"
      pattern: "extract_vertical_entities"
---

<objective>
Expand Sara's NLU layer with complete hair and beauty vertical coverage: service synonym tables, guardrail patterns, and entity extraction for all sub-verticals (barbiere, color_specialist, extension_specialist, tricologo for hair; estetista_viso, estetista_corpo, nail_specialist, epilazione_laser, centro_abbronzatura, spa for beauty).

Purpose: Today hair services fall through to "salone" (legacy key, incomplete) and beauty has zero dedicated entries. After this plan, both verticals have full synonym coverage for multi-service detection and guardrails that correctly block OOS requests without false-positives.

Output: Expanded italian_regex.py + entity_extractor.py + test_hair_beauty_nlu.py with ≥60 parametrized test cases, all passing on MacBook (no iMac needed for this plan — pure Python, no Tauri).
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-RESEARCH.md

@voice-agent/src/italian_regex.py
@voice-agent/src/entity_extractor.py
@voice-agent/tests/test_guardrails.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Expand VERTICAL_SERVICES and VERTICAL_GUARDRAILS for hair and beauty in italian_regex.py</name>
  <files>voice-agent/src/italian_regex.py</files>
  <action>
STEP 1 — Expand VERTICAL_SERVICES.

Read the existing "salone" entry (lines 230–249). After the closing brace of the "auto" sub-dict (line 295, before the closing `}` of VERTICAL_SERVICES), insert two new top-level keys: "hair" and "beauty".

Use your encyclopedic knowledge of Italian hair salon and beauty terminology to generate comprehensive synonym lists for each service group. Every synonym must be a string a real Italian client would say to a phone voice agent (including STT artifacts, regional colloquialisms, and diminutives).

For "hair", include these service groups with comprehensive Italian synonyms (use the existing "salone" groups as the base, then extend):
- "taglio": keep all existing salone taglio synonyms + add: "tagliettino", "ripassatina", "messa a posto", "spuntina", "accorciatina capelli", "sistemare le punte", "punte danneggiate"
- "taglio_uomo": keep existing + add: "taglio maschile corto", "capelli corti uomo"
- "taglio_bambino": keep existing
- "piega": keep existing
- "colore": keep existing
- "meches": keep existing
- "balayage": keep existing
- "trattamento": keep existing
- "permanente": keep existing
- "stiratura": keep existing
- "extension": keep existing + add: "extension cheratina", "extension clip", "extension tape", "I-tip", "V-tip", "allungamento volume", "allungamento cheratina"
- "barba": keep existing
- "manicure": keep existing (manicure is legitimate in salone — do NOT move to beauty-only)
- "pedicure": keep existing
- "ceretta": keep existing
- "trucco": keep existing
- "acconciatura_sposa": keep existing
- NEW "fade": ["fade", "skin fade", "zero ai lati", "sfumatura progressiva", "degradè uomo", "undercut", "effetto dissolvenza", "rasatura laterale"]
- NEW "barba_stilizzata": ["barba sfumata", "contorno barba", "lineetta barba", "barba scultura", "beard shaping", "rifinire la barba", "definire la barba"]
- NEW "correzione_colore": ["correzione colore", "decolorazione", "toning capelli", "glossing", "protezione colore", "Olaplex", "trattamento Olaplex", "trattamento decolorante", "schiaritura capelli", "riflessante"]
- NEW "tricologo": ["tricologia", "trattamento anti-caduta", "caduta capelli", "diradamento capelli", "plasma ricco di piastrine", "PRP tricologico", "PRP capelli", "peeling cuoio capelluto", "analisi tricologica", "mesoterapia capelli"]

For "beauty", create from scratch (zero existing entries today). Include these service groups:
- "pulizia_viso": ["pulizia viso", "pulizia profonda", "pulizia del viso", "viso pulito", "comedoni", "punti neri", "trattamento acne", "trattamento viso"]
- "peeling": ["peeling viso", "peeling chimico", "peeling enzimatico", "esfoliazione viso"]
- "radiofrequenza_viso": ["radiofrequenza viso", "rf viso", "rassodamento viso", "lifting viso", "trattamento lifting", "filler viso", "biorivitalizzazione", "LED viso", "luce LED"]
- "dermaplaning": ["dermaplaning", "microneedling", "trattamento microneedling", "mesoterapia viso", "needling"]
- "massaggio_viso": ["massaggio viso", "massaggio rilassante viso", "drenaggio viso", "linfodrenaggio viso", "maschera viso", "maschera idratante"]
- "massaggio_corpo": ["massaggio rilassante", "massaggio drenante", "massaggio anticellulite", "massaggio decontratturante corpo", "massaggio ayurvedico", "massaggio shiatsu corpo", "massaggio svedese"]
- "linfodrenaggio": ["linfodrenaggio", "drenaggio linfatico", "pressoterapia", "bendaggio drenante", "bendaggio corpo", "cavitazione", "radiofrequenza corpo"]
- "anticellulite": ["trattamento anticellulite", "cellulite", "endo-sfera", "crio trattamento", "crioterapia corpo"]
- "gel": ["gel unghie", "ricostruzione gel", "allungamento gel", "unghie in gel", "refill gel", "fill-in gel", "copertura gel", "unghie gel"]
- "semipermanente_unghie": ["semipermanente unghie", "smalto semipermanente", "gel semipermanente", "semipermanente mani", "semipermanente piedi", "ripassata semipermanente"]
- "nail_art": ["nail art", "decorazioni unghie", "ricostruzione unghie", "forma mandorla", "forma stiletto", "forma coffin", "french manicure", "french unghie", "nail art 3D"]
- "rimozione_gel": ["rimozione gel", "rimozione semipermanente", "sciogliere gel", "togliere il gel"]
- "epilazione_laser": ["epilazione laser", "laser diodo", "luce pulsata", "IPL", "epilazione definitiva", "depilazione laser", "pulsed light", "patch test laser", "laser ascelle", "laser inguine", "laser gambe"]
- "lettino_solare": ["lettino solare", "doccia solare", "abbronzatura artificiale", "autoabbronzante professionale", "abbonamento lettino", "solarium"]
- "circuito_spa": ["circuito spa", "percorso benessere", "day spa", "spa di coppia", "hammam", "bagno turco", "jacuzzi", "vasca idromassaggio spa", "gift card spa"]
- "massaggio_spa": ["massaggio ayurvedico", "massaggio hawaiano", "hot stone massage", "massaggio pietre calde", "massaggio rilassante spa", "trattamento corpo spa"]

After all "beauty" entries, add legacy aliases OUTSIDE the VERTICAL_SERVICES dict (after the closing `}`):
```python
# Legacy aliases — keep for backward compatibility with existing tests
VERTICAL_SERVICES["salone"] = VERTICAL_SERVICES["hair"]
```
Note: "palestra" alias stays as-is (handled in Wave B), "medical" alias in Wave B, "auto" unchanged.

STEP 2 — Expand VERTICAL_GUARDRAILS.

Read the existing guardrail dict (lines 767–871). After the closing `}` of VERTICAL_GUARDRAILS and BEFORE `_GUARDRAIL_COMPILED`, insert two new keys: "hair" and "beauty".

For "hair" guardrails (blocks: auto/officina, medical/clinica, wellness/palestra, professionale):
Use multi-word patterns only (architectural rule). Generate comprehensive patterns covering every way an Italian client would request OOS services:
```python
"hair": [
    # Auto/officina OOS
    r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
    r"\b(?:cambio\s+gomme|gomme\s+(?:invernali|estive|nuove)|pneumatici\s+(?:invernali|estivi|nuovi))\b",
    r"\b(?:pastiglie\s+freni|dischi\s+freno|liquido\s+freni)\b",
    r"\b(?:revisione\s+auto|tagliando\s+auto|collaudo\s+auto)\b",
    r"\b(?:verniciatura\s+auto|ammaccatura\s+auto|carrozzeria\s+auto)\b",
    r"\b(?:centralina\s+auto|diagnostica\s+auto|spia\s+motore)\b",
    r"\bfar[ei]?\s+(?:il\s+)?tagliando\b",
    r"\b(?:cambiar[ei]|cambia(?:re)?)\s+(?:l['''\u2019]?\s*)?olio\b",
    r"\b(?:portare?\s+(?:la\s+macchina|l['''\u2019]?auto)|dal\s+meccanico)\b",
    # Medical OOS
    r"\b(?:visita\s+(?:medica|specialistica|cardiologica|dermatologica|oculistica))\b",
    r"\b(?:esame\s+del\s+sangue|analisi\s+del\s+sangue|prelievo\s+sangue)\b",
    r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
    r"\b(?:certificato\s+(?:medico|sportivo)|idoneità\s+sportiva)\b",
    # Wellness/palestra OOS
    r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
    r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning|zumba))\b",
    r"\b(?:personal\s+trainer|personal\s+training|allenamento\s+personalizzato)\b",
    r"\b(?:sala\s+pesi|body\s+building|pesistica)\b",
    # Professionale OOS
    r"\b(?:dichiarazione\s+dei\s+redditi|modello\s+730|Unico\s+redditi)\b",
    r"\b(?:consulenza\s+fiscale|consulenza\s+legale|consulenza\s+tributaria)\b",
    r"\b(?:apertura\s+partita\s+IVA|apertura\s+P\.?\s*IVA)\b",
],
```

For "beauty" guardrails (blocks: hair taglio/tinta, auto, medical prescriptions, wellness/palestra):
```python
"beauty": [
    # Hair-specific OOS (taglio capelli is NOT beauty — it is hair vertical)
    r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino|scalato|corto))\b",
    r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici|copertura\s+bianchi)\b",
    r"\b(?:messa\s+in\s+piega|piega\s+capelli|acconciatura\s+sposa)\b",
    r"\b(?:trattamento\s+capelli|cheratina\s+capelli|keratina\s+lisciante)\b",
    r"\b(?:extension\s+capelli|allungamento\s+capelli)\b",
    r"\b(?:balayage\s+capelli|meches\s+capelli|colpi\s+di\s+sole\s+capelli)\b",
    # Auto OOS
    r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
    r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi))\b",
    r"\b(?:revisione\s+auto|tagliando\s+auto)\b",
    r"\bfar[ei]?\s+(?:il\s+)?tagliando\b",
    r"\b(?:dal\s+meccanico|portare\s+la\s+macchina)\b",
    # Medical prescriptions OOS
    r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
    r"\b(?:visita\s+(?:medica|specialistica|ginecologica|cardiologica))\b",
    r"\b(?:esame\s+del\s+sangue|analisi\s+mediche)\b",
    # Palestra OOS
    r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
    r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning))\b",
    r"\b(?:personal\s+trainer|sala\s+pesi|body\s+building)\b",
    # Professionale OOS
    r"\b(?:dichiarazione\s+dei\s+redditi|consulenza\s+fiscale|consulenza\s+legale)\b",
],
```

After adding both new keys, add legacy alias AFTER the dict closing brace (before `_GUARDRAIL_COMPILED`):
```python
VERTICAL_GUARDRAILS["salone"] = VERTICAL_GUARDRAILS["hair"]
```

STEP 3 — Expand _GUARDRAIL_RESPONSES.

In `_GUARDRAIL_RESPONSES` dict (lines 880–885), add entries for "hair" and "beauty" BEFORE the closing brace:
```python
"hair": "Mi occupo di prenotazioni per il salone. Posso aiutarla con taglio, colore, trattamenti capelli, o altri servizi?",
"beauty": "Mi occupo di prenotazioni per il centro estetico. Posso aiutarla con trattamenti viso, massaggi, nail art, epilazione o spa?",
```

IMPORTANT constraints:
- DO NOT remove or change any existing "salone", "palestra", "medical", "auto" entries anywhere.
- DO NOT use single-word guardrail patterns (multi-word rule is mandatory).
- For accent variants in patterns use [iì] for words ending in accented -i (e.g., `martedì`).
- Use `[''\u2019]` for apostrophes in article elisions (`l['''\u2019]?auto`).
- After adding VERTICAL_SERVICES["salone"] = VERTICAL_SERVICES["hair"] alias, regenerate `_GUARDRAIL_COMPILED` — verify it is derived from VERTICAL_GUARDRAILS which now includes "salone" alias.
  </action>
  <verify>
Run on MacBook (pure Python, no iMac needed):
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "from src.italian_regex import VERTICAL_SERVICES, VERTICAL_GUARDRAILS, check_vertical_guardrail; print('hair keys:', list(VERTICAL_SERVICES['hair'].keys())); print('beauty keys:', list(VERTICAL_SERVICES['beauty'].keys())); r=check_vertical_guardrail('voglio fare il tagliando', 'hair'); print('OOS blocked:', r.blocked)"
```
Expected: hair keys listed (20+), beauty keys listed (15+), OOS blocked: True

Also verify legacy alias still works:
```bash
python -c "from src.italian_regex import VERTICAL_SERVICES, VERTICAL_GUARDRAILS; print('salone alias ok:', 'salone' in VERTICAL_SERVICES and VERTICAL_SERVICES['salone'] is VERTICAL_SERVICES['hair'])"
```
Expected: salone alias ok: True
  </verify>
  <done>
- VERTICAL_SERVICES["hair"] has ≥20 service groups with ≥5 synonyms each
- VERTICAL_SERVICES["beauty"] has ≥15 service groups with ≥4 synonyms each
- VERTICAL_SERVICES["salone"] is an alias to VERTICAL_SERVICES["hair"] (legacy compat)
- VERTICAL_GUARDRAILS["hair"] has ≥20 multi-word patterns
- VERTICAL_GUARDRAILS["beauty"] has ≥18 multi-word patterns
- VERTICAL_GUARDRAILS["salone"] is an alias to VERTICAL_GUARDRAILS["hair"]
- _GUARDRAIL_RESPONSES has entries for "hair" and "beauty"
- Python import succeeds with zero errors
  </done>
</task>

<task type="auto">
  <name>Task 2: Add sub_vertical field to VerticalEntities and implement hair + beauty entity extraction in entity_extractor.py</name>
  <files>voice-agent/src/entity_extractor.py</files>
  <action>
STEP 1 — Add sub_vertical field to VerticalEntities dataclass.

Find the VerticalEntities dataclass at line 1974. Add one new field after the existing `vehicle_brand` field:
```python
# Sub-vertical detected (hair/beauty/wellness/medico/auto/professionale sub-type)
sub_vertical: Optional[str] = None
```
The full updated dataclass should look like:
```python
@dataclass
class VerticalEntities:
    """Vertical-specific entities extracted from user input."""
    # Medical
    specialty: Optional[str] = None
    urgency: Optional[str] = None
    visit_type: Optional[str] = None
    # Auto
    vehicle_plate: Optional[str] = None
    vehicle_brand: Optional[str] = None
    # Sub-vertical (all verticals)
    sub_vertical: Optional[str] = None
```

STEP 2 — Add keyword dicts for hair and beauty sub-verticals.

After the existing `_MEDICAL_SPECIALTIES` dict block (search for `_MEDICAL_SPECIALTIES`), insert two new dicts:

```python
# =============================================================================
# HAIR SUB-VERTICAL KEYWORDS
# =============================================================================
_HAIR_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "barbiere": ["barba sfumata", "contorno barba", "fade", "skin fade", "zero ai lati",
                 "sfumatura progressiva", "degradè uomo", "undercut", "rasatura laterale",
                 "lineetta barba", "barba scultura", "beard shaping"],
    "color_specialist": ["correzione colore", "decolorazione", "toning capelli", "glossing",
                         "Olaplex", "trattamento Olaplex", "schiaritura capelli", "riflessante",
                         "balayage", "shatush", "ombré", "degradé colore"],
    "tricologo": ["caduta capelli", "diradamento capelli", "alopecia", "PRP tricologico",
                  "PRP capelli", "plasma ricco di piastrine", "peeling cuoio capelluto",
                  "analisi tricologica", "mesoterapia capelli", "trattamento anti-caduta"],
    "extension_specialist": ["extension cheratina", "extension clip", "extension tape",
                              "I-tip", "V-tip", "allungamento volume", "allungamento cheratina",
                              "extension capelli"],
}

# =============================================================================
# BEAUTY SERVICE KEYWORDS
# =============================================================================
_BEAUTY_SERVICE_KEYWORDS: Dict[str, List[str]] = {
    "estetista_viso": ["pulizia viso", "pulizia profonda", "peeling viso", "radiofrequenza viso",
                       "LED viso", "dermaplaning", "microneedling", "filler viso",
                       "biorivitalizzazione", "trattamento acne", "maschera viso"],
    "estetista_corpo": ["massaggio drenante", "massaggio anticellulite", "linfodrenaggio",
                        "pressoterapia", "bendaggio drenante", "cavitazione",
                        "radiofrequenza corpo", "endo-sfera", "massaggio rilassante corpo"],
    "nail_specialist": ["ricostruzione gel", "gel unghie", "semipermanente unghie", "nail art",
                        "fill-in gel", "rimozione gel", "forma mandorla", "forma coffin",
                        "french manicure", "ricostruzione unghie", "allungamento gel"],
    "epilazione_laser": ["epilazione laser", "laser diodo", "luce pulsata", "IPL",
                         "epilazione definitiva", "depilazione laser", "patch test laser"],
    "spa": ["circuito spa", "day spa", "hammam", "percorso benessere", "spa di coppia",
            "hot stone massage", "massaggio ayurvedico", "bagno turco"],
}
```

STEP 3 — Extend extract_vertical_entities() with hair and beauty branches.

Find `extract_vertical_entities()` at line 1986. In the function body, find the `elif vertical == "auto":` block (around line 2026) and ADD two new elif branches AFTER it (before `return result`):

```python
    elif vertical in ("hair", "salone"):
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _HAIR_SUB_VERTICAL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break

    elif vertical == "beauty":
        # Sub-vertical detection via keyword match
        text_lower_strip = text.strip().lower()
        for sub_vert, keywords in _BEAUTY_SERVICE_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower_strip:
                    result.sub_vertical = sub_vert
                    break
            if result.sub_vertical:
                break
```

Also update the existing `elif vertical == "medical":` block to also match `"medico"` (preparation for Wave B):
Change: `if vertical == "medical":`
To: `if vertical in ("medical", "medico"):`

Similarly update `elif vertical == "auto":` — leave as-is (auto key unchanged).

IMPORTANT: Do NOT modify any existing medical or auto extraction logic. Only add the new elif branches and update the "medical" key check.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.entity_extractor import extract_vertical_entities, VerticalEntities
# Test sub_vertical field exists
e = VerticalEntities()
print('sub_vertical field:', e.sub_vertical)

# Test hair entity extraction
r1 = extract_vertical_entities('voglio fare il fade e la barba sfumata', 'hair')
print('hair sub_vertical:', r1.sub_vertical)

r2 = extract_vertical_entities('mi interessa la correzione colore con Olaplex', 'hair')
print('color_specialist:', r2.sub_vertical)

# Test beauty entity extraction
r3 = extract_vertical_entities('vorrei fare la pulizia viso', 'beauty')
print('beauty sub_vertical:', r3.sub_vertical)

r4 = extract_vertical_entities('ricostruzione gel unghie forma mandorla', 'beauty')
print('nail_specialist:', r4.sub_vertical)

# Verify legacy 'salone' key still works
r5 = extract_vertical_entities('extension cheratina', 'salone')
print('salone legacy sub_vertical:', r5.sub_vertical)
"
```
Expected: sub_vertical field: None, hair sub_vertical: barbiere, color_specialist: color_specialist, beauty sub_vertical: estetista_viso, nail_specialist: nail_specialist, salone legacy sub_vertical: extension_specialist
  </verify>
  <done>
- VerticalEntities dataclass has sub_vertical: Optional[str] = None field
- _HAIR_SUB_VERTICAL_KEYWORDS dict exists with 4 sub-vertical keys
- _BEAUTY_SERVICE_KEYWORDS dict exists with 5 sub-vertical keys
- extract_vertical_entities() has elif branch for hair/salone
- extract_vertical_entities() has elif branch for beauty
- Existing medical and auto extraction unchanged
- Python import succeeds with zero errors
  </done>
</task>

<task type="auto">
  <name>Task 3: Create test_hair_beauty_nlu.py with ≥60 parametrized test cases</name>
  <files>voice-agent/tests/test_hair_beauty_nlu.py</files>
  <action>
Create a new test file at `voice-agent/tests/test_hair_beauty_nlu.py`. Follow the exact structure and import pattern from `voice-agent/tests/test_guardrails.py` (read it first).

The test file must contain:

1. **TestHairGuardrails** — test class for hair vertical guardrails:
   - `test_hair_blocks_auto_oos` — parametrize on ≥8 auto-related inputs that MUST be blocked
     Examples: "voglio fare il tagliando", "cambio olio dell'auto", "portare la macchina dal meccanico", "cambio gomme invernali", "revisione auto scaduta", "pastiglie freni da sostituire", "ammaccatura sul paraurti", "diagnostica auto"
   - `test_hair_blocks_medical_oos` — parametrize on ≥6 medical inputs
     Examples: "visita medica urgente", "esame del sangue domani", "ricetta medica rinnovo", "visita dermatologica", "certificato sportivo", "analisi del sangue"
   - `test_hair_blocks_palestra_oos` — parametrize on ≥5 wellness inputs
     Examples: "abbonamento mensile palestra", "corso di yoga mattutino", "personal trainer disponibile", "sala pesi riservata", "corso di crossfit"
   - `test_hair_allows_in_scope` — parametrize on ≥15 valid hair inputs that MUST NOT be blocked
     Examples: "vorrei un taglio", "fare la tinta capelli", "balayage naturale", "barba sfumata", "skin fade", "zero ai lati", "extension cheratina", "correzione colore con Olaplex", "trattamento anti-caduta", "messa in piega", "tagliettino alle punte", "ripassatina nuca", "acconciatura sposa", "stiratura brasiliana", "permanente capelli"
   - `test_hair_legacy_salone_key` — verify "salone" key gives same results as "hair" for same inputs (≥5 inputs)

2. **TestBeautyGuardrails** — test class for beauty vertical guardrails:
   - `test_beauty_blocks_hair_oos` — parametrize on ≥7 hair-specific inputs that MUST be blocked
     Examples: "taglio capelli donna", "tinta capelli scura", "messa in piega", "extension capelli", "ritocco radici bianchi", "trattamento cheratina capelli", "balayage capelli corti"
   - `test_beauty_blocks_auto_oos` — parametrize on ≥5 auto inputs
     Examples: "cambio olio motore", "revisione auto", "tagliando auto", "pneumatici invernali", "dal meccanico domani"
   - `test_beauty_blocks_medical_oos` — parametrize on ≥4 medical inputs
     Examples: "ricetta medica rinnovo", "visita medica urgente", "esame del sangue", "visita ginecologica"
   - `test_beauty_allows_in_scope` — parametrize on ≥15 valid beauty inputs that MUST NOT be blocked
     Examples: "pulizia viso profonda", "peeling enzimatico", "radiofrequenza viso", "dermaplaning", "massaggio drenante", "linfodrenaggio gambe", "pressoterapia", "ricostruzione unghie gel", "nail art decorazioni", "epilazione laser gambe", "laser diodo ascelle", "circuito spa", "hammam", "massaggio anticellulite", "semipermanente mani"

3. **TestHairEntityExtraction** — test class for entity extraction:
   - `test_hair_sub_vertical_detection` — parametrize on (text, expected_sub_vertical) tuples:
     ("barba sfumata contorno", "barbiere"), ("fade e zero ai lati", "barbiere"),
     ("correzione colore con Olaplex", "color_specialist"), ("decolorazione capelli", "color_specialist"),
     ("caduta capelli analisi tricologica", "tricologo"), ("PRP capelli", "tricologo"),
     ("extension cheratina I-tip", "extension_specialist"), ("allungamento volume capelli", "extension_specialist")
   - `test_hair_unknown_returns_none` — verify inputs with no sub-vertical keywords return sub_vertical=None
   - `test_salone_alias_entity_extraction` — same as hair tests but passing vertical="salone"

4. **TestBeautyEntityExtraction** — test class for beauty entity extraction:
   - `test_beauty_sub_vertical_detection` — parametrize on (text, expected_sub_vertical) tuples:
     ("pulizia viso profonda", "estetista_viso"), ("radiofrequenza viso lifting", "estetista_viso"),
     ("massaggio drenante anticellulite", "estetista_corpo"), ("linfodrenaggio gambe", "estetista_corpo"),
     ("ricostruzione unghie gel", "nail_specialist"), ("fill-in gel unghie", "nail_specialist"),
     ("epilazione laser diodo", "epilazione_laser"), ("IPL patch test", "epilazione_laser"),
     ("circuito spa hammam", "spa"), ("massaggio ayurvedico spa", "spa")
   - `test_beauty_unknown_returns_none` — verify inputs with no sub-vertical keywords return sub_vertical=None

Use `pytest.mark.parametrize` for all test methods. Follow the existing pattern from `test_guardrails.py` for imports and class structure. Do NOT use `unittest.TestCase` — use plain pytest classes.

Add a module-level docstring:
```python
"""
Tests for Wave A NLU patterns: hair and beauty verticals.
Phase: f-sara-nlu-patterns
Wave: 1 (parallel with Wave B wellness+medico, Wave C auto+professionale)
"""
```
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_hair_beauty_nlu.py -v 2>&1 | tail -30
```
Expected: All tests PASSED, 0 failed. Count ≥60 test cases total.

Also run existing guardrail tests to confirm no regressions:
```bash
python -m pytest tests/test_guardrails.py -v 2>&1 | tail -20
```
Expected: All existing tests pass (legacy "salone" key must still work).
  </verify>
  <done>
- test_hair_beauty_nlu.py exists with ≥60 parametrized test cases
- All test cases PASS on MacBook
- TestHairGuardrails: ≥34 cases (blocked + allowed)
- TestBeautyGuardrails: ≥21 cases (blocked + allowed)
- TestHairEntityExtraction: ≥11 cases
- TestBeautyEntityExtraction: ≥12 cases
- Existing test_guardrails.py still passes (no regressions)
  </done>
</task>

</tasks>

<verification>
Run full verification on MacBook (no iMac needed for Wave 1 — pure Python):
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_hair_beauty_nlu.py tests/test_guardrails.py tests/test_entity_extractor.py tests/test_vertical_entity_extractor.py -v 2>&1 | tail -30
```
All tests must pass. Existing test counts must not decrease (currently 0 failures in these files).
</verification>

<success_criteria>
- VERTICAL_SERVICES has "hair" (20+ groups) and "beauty" (15+ groups) with comprehensive Italian synonyms
- "salone" is an alias to "hair" in both VERTICAL_SERVICES and VERTICAL_GUARDRAILS
- VERTICAL_GUARDRAILS has "hair" (20+ multi-word patterns) and "beauty" (18+ multi-word patterns)
- VerticalEntities.sub_vertical field added
- extract_vertical_entities() handles hair/salone and beauty verticals
- test_hair_beauty_nlu.py: ≥60 test cases, all PASS on MacBook
- Existing test_guardrails.py passes without regressions
</success_criteria>

<output>
After completion, create `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-01-SUMMARY.md`
</output>
