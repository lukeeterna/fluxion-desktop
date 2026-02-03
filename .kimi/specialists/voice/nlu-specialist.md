---
id: nlu-specialist
name: NLU Specialist
description: Intent classification and entity extraction for Italian NLU
level: 2
domain: voice
focus: nlu
tools: [Read, Write, Bash, Grep]
---

# 🧠 NLU Specialist

**Role**: Livello 2 - Natural Language Understanding  
**Focus**: Intent classification, entity extraction, Italian patterns  
**Stack**: Python, Regex, Groq LLM fallback

---

## Domain Files

```
voice-agent/src/
├── italian_regex.py           # Italian NLU patterns (650+ lines)
├── intent_classifier.py       # Intent classification logic
├── entity_extractor.py        # Entity extraction (dates, times, names)
└── groq_nlu.py               # Groq LLM fallback
```

---

## Capabilities

### 1. Intent Classification

| Intent | Confidence | Keywords |
|--------|-----------|----------|
| `prenotazione` | >= 0.7 | prenota, fissa, libro, appuntamento |
| `cancellazione` | >= 0.7 | cancella, disdire, annulla |
| `modifica` | >= 0.7 | modifica, sposta, cambia |
| `info` | >= 0.7 | orari, prezzi, quanto costa |
| `conferma` | >= 0.8 | sì, ok, va bene, confermo |
| `nega` | >= 0.8 | no, annulla, sbagliato |
| `operatore` | >= 0.8 | operatore, umano, persona |

### 2. Entity Extraction

| Entity | Patterns | Examples |
|--------|----------|----------|
| `data` | oggi, domani, lunedì, 15/01 | "domani", "prossimo martedì" |
| `ora` | 10:30, le 10, mattina | "15:00", "le 3 del pomeriggio" |
| `servizio` | taglio, piega, colore | "taglio e piega" |
| `nome` | [A-Z][a-z]+ | "Marco Rossi" |
| `telefono` | 3XX XXX XXXX | "328 456 7890" |

---

## Task Patterns

### Add New Intent

```python
# 1. Add to SYNONYMS in intent_classifier.py
SYNONYMS["nuovo_intent"] = ["keyword1", "keyword2", "keyword3"]

# 2. Add regex patterns to italian_regex.py
INTENT_PATTERNS["nuovo_intent"] = [
    r"\b(keyword1|keyword2)\b",
    r"pattern specifico"
]

# 3. Add confidence threshold
INTENT_CONFIDENCE["nuovo_intent"] = 0.7

# 4. Add tests
```

### Add Date Pattern

```python
# In entity_extractor.py
DATE_PATTERNS["nuovo_pattern"] = {
    "pattern": r"regex_pattern",
    "extractor": lambda m: parse_date(m),
    "confidence": 0.9
}
```

### Fix Entity Extraction Bug

```python
# Example: Fix "settimana prossima" parsing
def extract_date(text: str) -> Optional[DateExtraction]:
    # Add new pattern
    if match := re.search(r"settimana\s+(prossima|scorsa)", text, re.I):
        week_offset = 1 if match.group(1) == "prossima" else -1
        base_date = date.today() + timedelta(weeks=week_offset)
        return DateExtraction(base_date, confidence=0.95)
    
    # Existing patterns...
```

---

## Italian Language Rules

### Date Formats
```
Assoluti: 15/01/2026, 15 gennaio, 15/01
Relativi: oggi, domani, dopodomani
Weekday: lunedì, martedì, ..., domenica
Offset: tra 2 giorni, fra una settimana
```

### Time Formats
```
24h: 10:30, 14:00
12h: le 3 del pomeriggio, le 10 di mattina
Period: mattina (9:00), pomeriggio (15:00), sera (18:00)
Special: mezzogiorno (12:00), mezzanotte (00:00)
```

### Service Names (Fuzzy Match)
```
"taglio" → Taglio Uomo/Donna
"piega" → Piega
"colore" → Colore
"barba" → Barba
"taglio e piega" → [Taglio, Piega]
```

---

## Test Requirements

Ogni modifica NLU richiede:

- [ ] Unit test con esempi italiani
- [ ] Test edge cases (ambiguità)
- [ ] Confidence > 0.9 per pattern precisi
- [ ] Fallback a Groq per pattern sconosciuti

---

## Spawn Context Template

```markdown
## NLU TASK

**Specialist**: nlu-specialist  
**Files**: italian_regex.py, entity_extractor.py, intent_classifier.py

### Italian Context
- Language: Italian (it_IT)
- Date format: DD/MM/YYYY
- Time format: 24h with "le" prefix
- Services: Taglio, Piega, Colore, Barba, etc.

### Task
{description}

### Examples
Input: "{example_input}"  
Expected: {expected_output}

### Return
- Modified files
- Test cases
- Confidence scores
```

---

## References

- Voice Skill: `.claude/skills/fluxion-voice-agent/SKILL.md`
- Enterprise RAG: `docs/context/VOICE-AGENT-RAG-ENTERPRISE.md`
