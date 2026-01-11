# Sessione: Voice Agent Local RAG Fix

**Data**: 2026-01-11T09:00:00
**Fase**: 7 (Voice Agent + WhatsApp)
**Agenti**: rust-backend, voice-engineer

---

## Obiettivo
Correggere Voice Agent per usare RAG locale come prima priorità, Groq solo come fallback.

---

## Bug Risolti

### BUG-V2: Voice Agent Spinner Infinito
**Causa**: Due problemi Python:
1. Sintassi `str | None` non supportata in Python 3.9 (iMac usa 3.9.6)
2. Callbacks (`on_intent`, `on_response`, etc.) inizializzati dentro `load_faq_from_db()` invece di `__init__`

**Fix**:
1. Cambiato `str | None` → `Optional[str]`
2. Spostato callbacks in `__init__`

### Implementazione RAG Locale
- FAQ caricato da `data/faq_salone.md` al startup
- `find_faq_answer()` usa keyword matching
- Groq chiamato solo per intent "prenotazione" o domande complesse
- Fallback response se Groq fallisce

---

## Test Eseguiti

```bash
# Test pricing (local RAG)
curl -X POST 'http://127.0.0.1:3002/api/voice/process' \
  -d '{"text": "Quanto costa un taglio?"}'
# → {"response": "€18, durata 30 minuti", "intent": "informazioni"}

# Test opening hours (local RAG)
curl -X POST 'http://127.0.0.1:3002/api/voice/process' \
  -d '{"text": "Siete aperti la domenica?"}'
# → {"response": "No, siamo chiusi la domenica...", "intent": "unknown"}

# Test booking intent (uses Groq LLM)
curl -X POST 'http://127.0.0.1:3002/api/voice/process' \
  -d '{"text": "Vorrei prenotare un taglio per domani"}'
# → {"response": "...domani è domenica, siamo chiusi...", "intent": "prenotazione"}
```

---

## Commits

| Hash | Descrizione |
|------|-------------|
| `edf8280` | fix(voice): use Optional[str] for Python 3.9 compatibility |
| `6cb777a` | fix(voice): move callbacks to __init__ for proper initialization |

---

## File Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| voice-agent/src/pipeline.py | Fix | Python 3.9 compat + callback init |

---

## Status BUG

| Bug ID | Descrizione | Status |
|--------|-------------|--------|
| BUG-V2 | Spinner infinito | ✅ Risolto |

---

## Prossimi Passi
1. Test Voice Agent da UI (user deve navigare a pagina Voice Agent)
2. WhatsApp: utente deve scansionare QR per attivare
3. Futuro: sistema di apprendimento da risposte operatore
