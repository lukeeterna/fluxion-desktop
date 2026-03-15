# Phase F-SARA-NLU-PATTERNS: Complete NLU Pattern Rewrite — Research

**Researched:** 2026-03-15
**Domain:** Italian NLU / regex patterns / voice agent vertical coverage
**Confidence:** HIGH (all findings from direct codebase audit)

---

## Summary

This research audits the current state of Sara's NLU layer in `italian_regex.py` (921 lines, 12 pattern groups) and `entity_extractor.py` (2064+ lines), then identifies the gap between what exists today and what is needed for complete enterprise-grade coverage across all 6 macro-verticals × 17+ sub-verticals defined in `src/types/setup.ts`.

The codebase currently handles only 4 legacy verticals (`salone`, `palestra`, `medical`, `auto`). The new vertical taxonomy in `setup.ts` uses 6 macros (`hair`, `beauty`, `wellness`, `auto`, `medico`, `professionale`) with 30+ micro-categories. The pattern layer has not been updated to match this taxonomy. Sub-verticals such as `barbiere`, `nail_specialist`, `fisioterapia`, `officina_meccanica`, `carrozzeria`, `commercialista`, and `avvocato` have zero dedicated NLU coverage.

**Primary recommendation:** Expand `VERTICAL_SERVICES`, `VERTICAL_GUARDRAILS`, and `_GUARDRAIL_RESPONSES` in `italian_regex.py` to cover all 6 macro+micro-verticals, and expand `extract_vertical_entities()` in `entity_extractor.py` to emit vertical-specific signals (role, sub-service type, urgency) for the new verticals. Do this in 3 parallel waves (Wave A: hair+beauty, Wave B: wellness+medico, Wave C: auto+professionale), each as an atomic PR with pytest coverage ≥95%.

---

## Current State Audit

### `italian_regex.py` — what exists today

| Group | Lines | Status | Gaps |
|-------|-------|--------|------|
| Filler words | 33–77 | COMPLETE | None |
| Confirmation patterns | 84–119 | COMPLETE | None |
| Rejection patterns | 126–160 | COMPLETE | None |
| Escalation patterns | 168–218 | COMPLETE | None |
| `VERTICAL_SERVICES` dict | 229–295 | PARTIAL | Only 4 verticals; new taxonomy unused |
| Multi-service detection | 299–355 | COMPLETE | Works generically against any synonym list |
| Content filter | 357–479 | COMPLETE | None |
| Correction detection | 481–554 | COMPLETE | None |
| Ambiguous date | 578–600 | COMPLETE | None |
| Flexible scheduling | 603–643 | COMPLETE | None |
| Time pressure | 648–668 | COMPLETE | None |
| `VERTICAL_GUARDRAILS` dict | 767–871 | PARTIAL | Only 4 verticals; new macros return `blocked=False` by default |
| `_GUARDRAIL_RESPONSES` dict | 880–885 | PARTIAL | Only 4 verticals |

### `entity_extractor.py` — what exists today

| Feature | Status | Verticals covered |
|---------|--------|-------------------|
| `extract_vertical_entities()` | PARTIAL | `medical` (specialty+urgency+visit_type), `auto` (targa+brand); all others return empty `VerticalEntities` |
| `_MEDICAL_SPECIALTIES` | GOOD | 10 specialties; missing fisioterapia/osteopata/podologo/nutrizionista |
| `_AUTO_BRANDS` | GOOD | 36 brands |
| Hair/beauty entities | MISSING | None |
| Wellness/fitness entities | MISSING | None |
| Professionale entities | MISSING | None |

### `check_vertical_guardrail()` — vertical key mapping

The function uses string key lookup: `_GUARDRAIL_COMPILED.get(vertical, [])`. Unknown keys return `blocked=False` silently. Today the new macro-vertical IDs (`hair`, `beauty`, `wellness`, `medico`, `professionale`) all fall through as unknown.

The `orchestrator.py` calls `set_vertical(vertical)` which stores `self.verticale_id`. This is the string passed to `check_vertical_guardrail()` and `extract_vertical_entities()`. The mapping from `setup.ts` micro-category values to these runtime IDs is **not yet defined** — a new mapping table is needed.

---

## Gap Analysis by Vertical

### Macro: `hair` (sub: salone_donna, barbiere, salone_unisex, extension_specialist, color_specialist, tricologo)

**VERTICAL_SERVICES today (`salone`):** 17 service groups — covers core well.

**Missing per sub-vertical:**
- `barbiere`: "barba sfumata", "degradè uomo", "fade", "skin fade", "zero ai lati", "ripassata nuca", "contorno barba", "lineetta", "pomata", "cera"
- `extension_specialist`: "extension cheratina", "extension clip", "extension tape", "I-tip", "V-tip", "allungamento volume"
- `color_specialist`: "correzione colore", "decolorazione", "toning", "glossing", "protezione colore", "Olaplex"
- `tricologo`: "tricologia", "trattamento anti-caduta", "plasma ricco di piastrine", "PRP", "peeling cuoio capelluto", "analisi tricologica"
- Regional variants missing: "tagliettino" (Sud), "colpo di sole" plurale, "messa a posto" (informale)

**GUARDRAILS for `hair`:** Needs to block medical/auto/wellness/professionale. Currently `salone` guardrails are close but need updating for new key name and to add beauty OOS patterns.

### Macro: `beauty` (sub: estetista_viso, estetista_corpo, nail_specialist, epilazione_laser, centro_abbronzatura, spa)

**VERTICAL_SERVICES today:** Zero dedicated entries. The `salone` vertical has `manicure`/`pedicure`/`ceretta`/`trucco` as sub-items, but these are legitimate `beauty` services that must be whitelisted (not treated as OOS).

**Missing:**
- `estetista_viso`: "pulizia viso", "peeling", "maschera viso", "radiofrequenza viso", "filler", "biorivitalizzazione", "LED viso", "dermaplaning", "microneedling", "trattamento acne"
- `estetista_corpo`: "massaggio drenante", "massaggio rilassante", "anticellulite", "linfodrenaggio", "bendaggio", "pressoterapia", "cavitazione", "radiofrequenza corpo"
- `nail_specialist`: "gel", "semipermanente", "ricostruzione unghie", "nail art", "copertura", "ripassata gel", "fill-in", "rimozione gel", "forma mandorla", "french"
- `epilazione_laser`: "epilazione laser", "laser diodo", "luce pulsata", "IPL", "epilazione definitiva", "patch test laser"
- `centro_abbronzatura`: "lettino solare", "doccia solare", "autoabbronzante professionale", "abbonamento lettino"
- `spa`: "circuito spa", "massaggio shiatsu", "massaggio ayurvedico", "hammam", "percorso benessere", "day spa", "gift card spa"

**GUARDRAILS for `beauty`:** Must block hair-specific (taglio capelli, tinta), auto, medical, fitness. Currently no guardrails exist for this vertical.

### Macro: `wellness` (sub: palestra, personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali)

**VERTICAL_SERVICES today (`palestra`):** 13 service groups — good baseline.

**Missing per sub-vertical:**
- `personal_trainer`: "pacchetto sedute", "allenamento domicilio", "programma personalizzato", "scheda allenamento", "valutazione composizione corporea", "plicometria", "test VO2 max"
- `yoga_pilates`: "pilates posturale", "yin yoga", "yoga nidra", "meditazione guidata", "pranayama", "hot yoga", "restorative yoga", "lezione privata yoga"
- `crossfit`: "WOD", "AMRAP", "EMOM", "benchmark", "metcon", "fondamentali crossfit", "open gym", "comp prep"
- `piscina`: "vasca da 25m", "vasca da 50m", "corsia riservata", "corso nuoto adulti", "corso baby nuoto", "nuoto libero", "acquacorrida", "master nuoto"
- `arti_marziali`: "judo", "karate", "jiu-jitsu", "BJJ", "muay thai", "kickboxing", "MMA", "cintura", "kata", "kumite", "randori", "cintura nera"
- `fisioterapia` (under `medico` but often standalone): "rieducazione", "riabilitazione", "tecarterapia", "kinesiotaping", "manipolazione vertebrale", "onde d'urto"

**GUARDRAILS for `wellness`:** Must block hair, beauty, auto, medical/farmaci prescriptions, professionale.

### Macro: `medico` (sub: odontoiatra, fisioterapia, medico_generico, specialista, osteopata, podologo, psicologo, nutrizionista)

**VERTICAL_SERVICES today (`medical`):** 13 service groups — reasonable baseline but terminology shallow.

**Missing per sub-vertical:**
- `odontoiatra`: "ablazione tartaro", "sbiancamento denti", "bite", "bruxismo", "chirurgia orale", "cisti", "corona", "bridge", "impianto zigomatico", "invisalign", "aligner"
- `fisioterapia`: "fisioterapia posturale", "tecarterapia", "ultrasuoni", "TENS", "cerotti cinesiologici", "linfodrenaggio manuale", "mobilizzazione articolare", "dry needling"
- `psicologo`: "psicoterapia", "terapia cognitivo-comportamentale", "TCC", "EMDR", "colloquio di valutazione", "seduta di coppia", "terapia online", "follow-up"
- `nutrizionista`: "piano alimentare", "dieta personalizzata", "analisi bioimpedenziometrica", "BIA", "consulenza peso", "alimentazione sportiva"
- `osteopata`: "manipolazione osteopatica", "trattamento cranio-sacrale", "osteopatia viscerale"
- `podologo`: "plantari", "correzione unghia incarnita", "trattamento calli", "verruca plantare", "analisi del passo"

**GUARDRAILS for `medico`:** Must block hair, beauty, auto, wellness/palestra. Today's `medical` guardrails are close but key must be `medico` not `medical`.

**IMPORTANT:** `_MEDICAL_SPECIALTIES` in `entity_extractor.py` is missing: `fisioterapia`, `osteopata`, `podologo`, `psicologo`, `nutrizionista`.

### Macro: `auto` (sub: officina_meccanica, carrozzeria, elettrauto, gommista, revisioni, detailing)

**VERTICAL_SERVICES today (`auto`):** 13 service groups — solid.

**Missing per sub-vertical:**
- `carrozzeria`: "ritiro e consegna", "perizia danni", "stima danni", "sostituzione parabrezza", "lucidatura", "polish", "verniciatura parziale", "tintura paraurti"
- `elettrauto`: "diagnosi OBD", "centralina", "impianto hi-fi", "retrocamera", "GPS", "sensori parcheggio", "immobilizer", "impianto GPL", "impianto metano"
- `gommista`: "equilibratura", "bilanciatura", "convergenza", "assetto", "cambio stagionale", "deposito gomme", "riparazione foratura", "pressione gomme", "runflat"
- `revisioni`: "revisione ministeriale", "collaudo", "revisione straordinaria", "bollino blu", "libretto revisione"
- `detailing`: "lucidatura", "cera", "verniciatura nanotecnologica", "wrapping", "ppf", "protezione ceramica", "lavaggio ad ozono", "interno cuoio"

**GUARDRAILS for `auto`:** Current `auto` guardrail blocks salone/palestra/medical well. Needs new micro-vertical aliases.

### Macro: `professionale` (sub: commercialista, avvocato, consulente, agenzia, architetto)

**VERTICAL_SERVICES today:** Zero entries. Not implemented at all.

**Missing:**
- `commercialista`: "dichiarazione dei redditi", "730", "Unico", "modello F24", "busta paga", "apertura partita IVA", "consulenza fiscale", "chiusura bilancio", "contabilità"
- `avvocato`: "consulenza legale", "separazione consensuale", "divorzio", "contratto di locazione", "tutela consumatori", "recupero crediti", "successione ereditaria", "ricorso", "parere legale"
- `consulente`: "consulenza strategica", "business plan", "analisi di mercato", "consulenza HR", "formazione aziendale"
- `agenzia` (immobiliare): "valutazione immobile", "proposta d'acquisto", "visita immobile", "mutuo", "perizia"
- `architetto`: "progetto ristrutturazione", "pratiche comunali", "DIA", "SCIA", "permesso di costruire", "computo metrico", "rendering 3D"

**GUARDRAILS for `professionale`:** Must block all other verticals. Zero implementation today.

---

## Italian NLU Best Practices

### Regex pattern design for Italian

**HIGH confidence** — verified directly from existing production patterns in `italian_regex.py`.

1. **Multi-word-only rule** (hardcoded architectural decision): Single words MUST NOT be used as guardrail patterns. `\b(?:colore)\b` would block "colore della pelle" in medical context. All guardrail patterns use 2+ word phrases.

2. **Accent variants**: Italian accented vowels appear in two forms in STT output: `è`/`e`, `à`/`a`, `ì`/`i`. Pattern example: `r"luned[iì]"` matches both "lunedì" (proper) and "lunedi" (STT artifact). Apply this to all day names, common words.

3. **Verb form coverage**: Users say "voglio FARE il tagliando" not just "tagliando". Guardrail patterns must cover: bare noun, noun with "fare/portare/prenotare/devo", noun with article. Example from production:
   ```python
   r"\bfar[ei]?\s+(?:il\s+)?tagliando\b"
   r"\b(?:devo|dovrei|vorrei)\s+(?:fare\s+)?(?:il\s+)?tagliando\b"
   ```

4. **Article elision**: Italian articles contract before vowels — `l'auto`, `l'olio`, `dell'auto`. Patterns must use `(?:l[''']?\s*)?` or `(?:l['''\u2019]?\s*)?` for feminine/masculine article before vowel.

5. **STT apostrophe variants**: Whisper sometimes transcribes apostrophes as `'` (straight), `'` (curly), or `\u2019`. Pattern: `[''\u2019]` covers all three.

6. **Context-word guardrails**: Some words are ambiguous across verticals. Pattern approach: only block when word appears with a context qualifier. Example: `manicure` alone is allowed in salone; blocked in medical only when it appears as `(?:la\s+|una?\s+|fare\s+(?:la\s+)?)manicure`.

7. **Regional colloquial forms** (Italian-specific):
   - Nord: "tagliettino" (taglio leggero), "sistemare" (generic = vague)
   - Centro/Sud: "ripassata" (quick trim), "spuntatina" (light trim)
   - All regions: "fate voi" = flexible scheduling (already handled)
   - Roman: "mannaggia", "aoh", "daje" (fillers already covered)
   - Neapolitan: "jamme" (= andiamo), "uagliò" (informal address)
   - Milanese: "sciura/sciur" (formal address, like "signora/signore")

8. **Compound service requests**: `extract_multi_services()` already works generically via substring match against synonym lists. Adding synonyms to `VERTICAL_SERVICES` automatically enables multi-service detection.

9. **Diminutives and augmentatives**: Italian frequently uses `-ino/-ina/-etto/-etta` suffixes informally. "tagliettino" not in current patterns. Add these explicitly — regex cannot reliably derive diminutives.

10. **False-positive risk** — common Italian words that appear in multiple contexts:
    - "trattamento" (salone=hair treatment; medical=medical treatment; beauty=beauty treatment): use vertical-specific context
    - "massaggio" (palestra, spa, fisioterapia): all valid, no cross-blocking needed
    - "seduta" (psicologo, fisioterapia, palestra PT): valid in all — no cross-blocking
    - "visita" (medical only when standalone; avoid blocking "visita il salone" in other contexts)

---

## Architecture Patterns

### Recommended approach: macro-vertical key normalization

The runtime `verticale_id` stored in `VoiceOrchestrator.verticale_id` must match the keys in `VERTICAL_SERVICES`, `VERTICAL_GUARDRAILS`, and `_GUARDRAIL_RESPONSES`. Today there is a mismatch:

| `setup.ts` value | Current runtime key | Status |
|-----------------|---------------------|--------|
| `hair` | `salone` | MISMATCH |
| `beauty` | (none) | MISSING |
| `wellness` | `palestra` | MISMATCH |
| `medico` | `medical` | MISMATCH |
| `auto` | `auto` | MATCH |
| `professionale` | (none) | MISSING |

**Solution A (Recommended):** Add a normalization map in `orchestrator.py` (`_extract_vertical_key()` at line 1655) that maps new keys to expanded dicts, AND add new keys directly to `italian_regex.py`. This is cleanest.

**Solution B:** Keep legacy keys as aliases (`salone` → same as `hair`). Lower complexity but perpetuates confusion.

The planner should go with **Solution A**: add new macro keys + keep legacy aliases for backward compatibility with existing tests.

### Pattern organization in `italian_regex.py`

Current structure (12 groups, all flat). The new vertical service tables will add ~500–800 lines. Recommended structure:

```
# Section 5: VERTICAL_SERVICES
#   - Group 5a: hair (salone_donna, barbiere, salone_unisex, extension_specialist, color_specialist, tricologo)
#   - Group 5b: beauty (estetista_viso, estetista_corpo, nail_specialist, epilazione_laser, centro_abbronzatura, spa)
#   - Group 5c: wellness (palestra, personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali)
#   - Group 5d: medico (odontoiatra, fisioterapia, medico_generico, specialista, osteopata, podologo, psicologo, nutrizionista)
#   - Group 5e: auto (officina_meccanica, carrozzeria, elettrauto, gommista, revisioni, detailing)
#   - Group 5f: professionale (commercialista, avvocato, consulente, agenzia, architetto)
#   Legacy aliases: salone → hair, palestra → wellness, medical → medico

# Section 10: VERTICAL_GUARDRAILS
#   Same 6 macro keys + legacy aliases
```

### Duration map (DURATION_MAP)

Currently `DURATION_MAP` does not exist in `italian_regex.py` — it was referenced in the phase description but not yet implemented. This is a new data structure to add.

Recommended structure:
```python
DURATION_MAP: Dict[str, Dict[str, int]] = {
    "hair": {
        "taglio": 30,
        "taglio_uomo": 20,
        "piega": 45,
        "colore": 90,
        "meches": 120,
        "balayage": 150,
        "trattamento": 45,
        "extension": 180,
        ...
    },
    ...
}
```

This feeds into FSM slot-filling when Sara asks about duration for confirmation or checks slot availability.

### Operator roles per vertical

Currently `entity_extractor.py` extracts operator names via `ExtractedOperator` and `ExtractedOperatorList` (generic person-name extraction). There is no vertical-specific role map. New addition needed:

```python
OPERATOR_ROLES: Dict[str, List[str]] = {
    "hair": ["parrucchiere", "stilista", "colorista", "barbiere", "hair stylist"],
    "beauty": ["estetista", "nail artist", "estetologa", "beauty therapist"],
    "wellness": ["personal trainer", "istruttore", "coach", "insegnante yoga", "maestro"],
    "medico": ["dottore", "dottoressa", "medico", "fisioterapista", "fisio", "osteopata",
               "psicologo", "psicoterapeuta", "nutrizionista", "dietologo"],
    "auto": ["meccanico", "carrozziere", "elettrauto", "gommista"],
    "professionale": ["avvocato", "commercialista", "consulente", "architetto", "geometra"],
}
```

This enables Sara to extract "voglio con la dottoressa" or "con il fisio di giovedì".

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Spelling variants | Levenshtein regex | Already have `Levenshtein` in codebase (import via `thefuzz` or custom `levenshtein_distance`) | Already used for service fuzzy matching in BSM |
| Italian lemmatization | Custom stemmer | Just enumerate explicit forms | spaCy/UmBERTo already optional in L0b; for L0 regex layer, explicit enumeration is faster and more predictable |
| Regional dialect detection | NLP classifier | Explicit pattern lists per dialect | Volume of dialect tokens is small, enumeration reliable |
| Service duration lookup | External API | `DURATION_MAP` dict in `italian_regex.py` | Offline, deterministic, no latency |
| Pattern testing | Custom test runner | `pytest` + `@pytest.mark.parametrize` | Already established pattern in `test_italian_regex.py` |

---

## Common Pitfalls

### Pitfall 1: New macro keys not wired to `orchestrator.py`

**What goes wrong:** `VERTICAL_SERVICES["hair"]` added to `italian_regex.py`, but `orchestrator.py` still passes `verticale_id = "salone"` from old config. New patterns never matched.

**Why it happens:** The runtime vertical key comes from `SetupConfig.macro_categoria` (new) or `SetupConfig.categoria_attivita` (legacy). The mapping in `_extract_vertical_key()` (line 1655) must be updated.

**How to avoid:** Update `_extract_vertical_key()` to handle new macro values. Add legacy aliases. Test with `set_vertical("hair")` in unit tests.

**Warning signs:** Guardrail tests pass but integration tests fail; `check_vertical_guardrail("...", "hair")` returns `blocked=False`.

### Pitfall 2: Guardrail cross-blocking legitimate services

**What goes wrong:** Adding `beauty` OOS patterns to `hair` guardrails that accidentally block "manicure" when the business is a salone that offers manicure.

**Why it happens:** Some saloni offer nail services. The pattern `r"\b(?:manicure)\b"` as a guardrail in `hair` would block legitimate requests.

**How to avoid:** Use the context-word pattern approach (multi-word only). `r"\b(?:ricostruzione\s+unghie|ricostruzione\s+gel)\b"` is unambiguous. `"manicure"` alone stays out of OOS patterns.

### Pitfall 3: `extract_vertical_entities` returning empty for new verticals

**What goes wrong:** New verticals added to `VERTICAL_SERVICES` but `extract_vertical_entities()` in `entity_extractor.py` not updated. The FSM never receives sub-service signals (specialty, role, urgency) for new verticals.

**How to avoid:** Each vertical wave in the PLAN must include both `italian_regex.py` updates AND `entity_extractor.py` updates.

### Pitfall 4: Test parametrize lists not exhaustive

**What goes wrong:** `@pytest.mark.parametrize` list covers 5 synonyms but pattern only tested on "happy path" forms; STT variants like "tagliettino" or "ripassatina" never tested.

**How to avoid:** Each service synonym list in `VERTICAL_SERVICES` must have at least one test case per synonym entry. Use parametrize on the synonym list itself.

### Pitfall 5: Micro-vertical keys not matching `orchestrator.py` calls

**What goes wrong:** `setup.ts` uses `micro_categoria = "fisioterapia"` but orchestrator maps to `"medico"` macro. Guardrail checks against `"fisioterapia"` key which doesn't exist.

**How to avoid:** The runtime vertical key should always be the **macro** key. Micro-category granularity affects `VERTICAL_SERVICES` (which sub-dict to expose) but not the guardrail key. Document this explicitly.

### Pitfall 6: Missing legacy alias breaks existing tests

**What goes wrong:** Renaming `"salone"` key to `"hair"` breaks 40+ existing `test_guardrails.py` tests that use `"salone"`.

**How to avoid:** Keep legacy keys as aliases pointing to same pattern list. In `VERTICAL_GUARDRAILS`, add:
```python
"salone": VERTICAL_GUARDRAILS["hair"],  # legacy alias
"palestra": VERTICAL_GUARDRAILS["wellness"],  # legacy alias
"medical": VERTICAL_GUARDRAILS["medico"],  # legacy alias
```
Add this AFTER the primary dict is defined.

---

## Code Examples

### Pattern for new service group (verified style from production)

```python
# Source: voice-agent/src/italian_regex.py lines 229-295 (VERTICAL_SERVICES pattern)
VERTICAL_SERVICES: Dict[str, Dict[str, List[str]]] = {
    "hair": {
        # --- inherited from salone (unchanged) ---
        "taglio": ["taglio", "sforbiciata", "spuntatina", "accorciare", "taglietto",
                   "capelli", "fare i capelli", "taglio capelli", "sistemare i capelli",
                   "ripassata", "ripassatina"],  # NEW: regional variants
        # --- new: barbiere sub-vertical ---
        "fade": ["fade", "skin fade", "zero ai lati", "sfumatura progressiva",
                 "degradè uomo", "undercut"],
        "barba_stilizzata": ["barba sfumata", "contorno barba", "lineetta",
                             "barba scultura", "beard shaping"],
    },
}
```

### Guardrail with new key + legacy alias (verified approach)

```python
# Source: voice-agent/src/italian_regex.py lines 767-871 (VERTICAL_GUARDRAILS pattern)
VERTICAL_GUARDRAILS: Dict[str, List[str]] = {
    "hair": [
        # blocks: medical
        r"\b(?:visita\s+(?:medica|specialistica|cardiologica))\b",
        # blocks: auto
        r"\b(?:cambio\s+olio|tagliando\s+auto|revisione\s+auto)\b",
        # blocks: wellness (gym only, not beauty treatments)
        r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
        r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning))\b",
        # blocks: professionale
        r"\b(?:dichiarazione\s+dei\s+redditi|consulenza\s+(?:fiscale|legale))\b",
    ],
}

# Legacy alias AFTER primary dict defined:
VERTICAL_GUARDRAILS["salone"] = VERTICAL_GUARDRAILS["hair"]
```

### New vertical entity extraction (verified pattern style from entity_extractor.py)

```python
# Source: voice-agent/src/entity_extractor.py lines 1919-1950 (medical entities pattern)

# --- Hair entities ---
_HAIR_SUB_VERTICAL_KEYWORDS: Dict[str, List[str]] = {
    "barbiere": ["barba", "fade", "sfumatura", "rasatura"],
    "color_specialist": ["balayage", "decolorazione", "correzione colore", "toning"],
    "tricologo": ["caduta capelli", "diradamento", "alopecia", "PRP tricologico"],
    "extension_specialist": ["extension", "allungamento", "cheratina"],
}

# In extract_vertical_entities():
elif vertical in ("hair", "salone"):
    text_lower = text.strip().lower()
    for sub_vert, keywords in _HAIR_SUB_VERTICAL_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                result.sub_vertical = sub_vert
                break
```

### Test parametrize pattern (verified from test_italian_regex.py lines 86-100)

```python
# Source: voice-agent/tests/test_italian_regex.py — TestConferma parametrize pattern
class TestHairGuardrails:
    @pytest.mark.parametrize("text", [
        "vorrei il cambio olio",
        "devo fare il tagliando",
        "prenoto una visita medica",
        "mi iscrivo al corso di yoga",
    ])
    def test_hair_blocks_oos(self, text):
        r = check_vertical_guardrail(text, "hair")
        assert r.blocked is True

    @pytest.mark.parametrize("text", [
        "vorrei un taglio",
        "fare la tinta",
        "balayage capelli",
        "barba sfumata",         # barbiere sub-vertical
        "extension cheratina",   # extension_specialist
    ])
    def test_hair_allows_in_scope(self, text):
        r = check_vertical_guardrail(text, "hair")
        assert r.blocked is False
```

---

## State of the Art

| Old Approach | Current Approach | Status | Impact |
|--------------|------------------|--------|--------|
| 4 legacy verticals | 6 macro × 30+ micro | PLANNED (this phase) | Complete coverage |
| `salone`/`palestra`/`medical`/`auto` keys | `hair`/`beauty`/`wellness`/`medico`/`auto`/`professionale` | NOT YET done | Must add legacy aliases |
| `entity_extractor` covers only medical+auto | All 6 macros | PLANNED | Sara extracts role/sub-type signals |
| No `DURATION_MAP` | `DURATION_MAP: Dict[str, Dict[str, int]]` | PLANNED | Enables slot duration in availability check |
| No operator role map | `OPERATOR_ROLES` per vertical | PLANNED | Sara understands "voglio con il fisio" |

---

## Plan Structure Recommendation

### 3 waves, each an atomic PR

**Wave A — hair + beauty** (highest user volume, most complete existing baseline)
- Files: `italian_regex.py` (sections 5a, 5b, 10 for hair+beauty), `entity_extractor.py` (hair+beauty entities)
- New test file: `test_hair_beauty_nlu.py`
- Legacy aliases: `salone → hair`, `manicure/pedicure remain in both`
- Estimated patterns: ~150 new synonym entries, ~30 guardrail patterns, ~60 test cases

**Wave B — wellness + medico** (second highest volume)
- Files: `italian_regex.py` (sections 5c, 5d, 10 for wellness+medico), `entity_extractor.py` (add fisioterapia/osteopata/psicologo/nutrizionista to `_MEDICAL_SPECIALTIES`)
- New test file: `test_wellness_medico_nlu.py`
- Legacy aliases: `palestra → wellness`, `medical → medico`
- Estimated patterns: ~120 synonym entries, ~25 guardrail patterns, ~50 test cases

**Wave C — auto (extended) + professionale** (completes coverage)
- Files: `italian_regex.py` (sections 5e extended, 5f new, 10 for auto+professionale), `entity_extractor.py` (auto sub-vertical + professionale)
- New test file: `test_auto_professionale_nlu.py`
- Add `DURATION_MAP` and `OPERATOR_ROLES` data structures
- Estimated patterns: ~100 synonym entries, ~20 guardrail patterns, ~40 test cases

**Wave D — integration + orchestrator wiring** (after all 3 waves)
- Update `_extract_vertical_key()` (line 1655) in `orchestrator.py` to handle new macro keys
- Update `_GUARDRAIL_RESPONSES` for all 6 macros
- Update `VerticalEntities` dataclass to add `sub_vertical: Optional[str]` field
- Update `VERTICAL_SERVICES` usages in `set_vertical()` (line 2169)
- End-to-end test: `test_nlu_vertical_integration.py` — one test per macro+micro combination

### Parallelization

Waves A, B, C can be developed by **3 parallel subagents** (each owns one wave's files). Wave D must wait for all 3. The orchestrator should launch A/B/C in parallel, then D after all complete.

### Test coverage strategy

- Coverage target: ≥95% line coverage on `italian_regex.py` sections 5 and 10
- Measure with: `pytest --cov=italian_regex --cov-report=term-missing`
- Structure: one test class per vertical per file, parametrized on synonym list items
- Negative tests: ≥3 "must NOT block" cases per vertical (false positive prevention)
- Positive tests: ≥1 case per synonym entry (false negative prevention)
- Edge cases: empty string, single word, non-Italian input, STT artifact inputs

---

## Integration Points

### `italian_regex.py`

| What to add | Where | Notes |
|-------------|-------|-------|
| `VERTICAL_SERVICES` new keys | After line 295 | `hair`, `beauty`, `wellness`, `medico`, `professionale`; legacy aliases after |
| `DURATION_MAP` | New section after `VERTICAL_SERVICES` | New public constant |
| `OPERATOR_ROLES` | New section after `DURATION_MAP` | New public constant |
| `VERTICAL_GUARDRAILS` new keys | After line 871 | Same 6 macro keys + legacy aliases |
| `_GUARDRAIL_RESPONSES` new keys | After line 885 | Polite redirect per vertical |

### `entity_extractor.py`

| What to add | Where | Notes |
|-------------|-------|-------|
| `sub_vertical` field | `VerticalEntities` dataclass (line 1974) | `Optional[str] = None` |
| `_HAIR_SUB_VERTICAL_KEYWORDS` | After `_MEDICAL_SPECIALTIES` block | New dict |
| `_BEAUTY_SERVICE_KEYWORDS` | New dict | nail/facial/body/laser |
| `_WELLNESS_ROLE_KEYWORDS` | New dict | trainer/instructor role detection |
| Extend `_MEDICAL_SPECIALTIES` | Line 1921 | Add fisioterapia/osteopata/psicologo/nutrizionista |
| Extend `extract_vertical_entities()` | Lines 2001–2037 | Add elif branches for `hair`, `beauty`, `wellness`, `professionale` |

### `orchestrator.py`

| What to update | Line | Notes |
|----------------|------|-------|
| `_extract_vertical_key()` | 1655 | Map `hair`→`hair`, `beauty`→`beauty`, `wellness`→`wellness`, `medico`→`medico`, `professionale`→`professionale`; keep legacy mappings |
| `set_vertical()` | 2165 | No change needed if VERTICAL_SERVICES has both new and legacy keys |
| `create_orchestrator()` | 2765 | No change needed |

### `booking_state_machine.py`

No direct changes needed. BSM uses `VERTICAL_SERVICES` via `services_config` passed at init and updated via `set_vertical()`. Adding new keys to `VERTICAL_SERVICES` automatically extends BSM service matching.

---

## Open Questions

1. **Micro-vertical granularity at runtime**
   - What we know: `macro_categoria` is stored in `SetupConfig`. `micro_categoria` is also stored.
   - What's unclear: Does the orchestrator receive and store `micro_categoria` at startup? Currently `orchestrator.py` only calls `set_vertical(verticale_id)` with the macro. If micro is needed for sub-vertical entity extraction, where does it come from?
   - Recommendation: During Wave D, check if `micro_categoria` is passed to orchestrator init. If not, add it to `_load_business_config()`.

2. **`DURATION_MAP` consumers**
   - What we know: Currently no code uses `DURATION_MAP` — it's proposed new structure.
   - What's unclear: Which FSM state or orchestrator method should read durations to pass to `_check_slot_availability()`?
   - Recommendation: Implement as data-only in this phase. Wire into availability check in a follow-on phase.

3. **Professionale booking model**
   - What we know: Professionale verticals (avvocato, commercialista) bill by time, not service. Booking a "consulenza" is duration-based.
   - What's unclear: Does the existing FSM slot model (service+date+time+operator) work for professionale, or is a different flow needed?
   - Recommendation: For this phase, implement service synonyms and guardrails. Defer FSM changes for professionale to a separate phase.

---

## Sources

### Primary (HIGH confidence — direct code audit)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/italian_regex.py` — full audit of all 12 groups, 921 lines
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/entity_extractor.py` — full audit of `extract_vertical_entities()` and `VerticalEntities`
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/_INDEX.md` — function locations map
- `/Volumes/MontereyT7/FLUXION/src/types/setup.ts` — canonical vertical taxonomy
- `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_guardrails.py` — existing test structure
- `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_italian_regex.py` — existing test patterns

### Secondary (MEDIUM confidence)
- `orchestrator.py` grep results — confirmed `VERTICAL_SERVICES`, `check_vertical_guardrail()`, `extract_vertical_entities()` import points and call sites

---

## Metadata

**Confidence breakdown:**
- Current state audit: HIGH — direct file read
- Gap analysis: HIGH — derived from file audit vs setup.ts taxonomy
- Italian NLU best practices: HIGH — extracted from production pattern decisions in file
- Architecture patterns: HIGH — verified against orchestrator integration points
- Pitfalls: HIGH — derived from existing architectural decisions and known bugs in codebase
- Plan structure: MEDIUM — estimation based on scope analysis, actual effort may vary

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (stable domain; patterns don't change unless voice agent refactored)
