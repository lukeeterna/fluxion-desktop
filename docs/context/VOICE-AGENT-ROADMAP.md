# Voice Agent Roadmap

## Endpoints

| # | Funzionalita | Endpoint | Status |
|---|-------------|----------|--------|
| 1 | Cerca clienti | `/api/clienti/search` | Done |
| 2 | Crea appuntamenti | `/api/appuntamenti/create` | Done |
| 3 | Verifica disponibilita | `/api/appuntamenti/disponibilita` | Done |
| 4 | Lista d'attesa VIP | `/api/waitlist/add` | Done |
| 5 | Disambiguazione data_nascita | `disambiguation_handler.py` | Done |
| 6 | Disambiguazione soprannome | `disambiguation_handler.py` | Done |
| 7 | Registrazione cliente | `/api/clienti/create` | Done |
| 8 | Preferenza operatore | `/api/operatori/list` | Done |
| 9 | Cancella appuntamento | `/api/appuntamenti/cancel` | Done |
| 10 | Sposta appuntamento | `/api/appuntamenti/reschedule` | Done |
| 11 | Guided Dialog fallback | `guided_dialog.py` | Done |

## Flusso Disambiguazione

```
1. "prenotazione per Mario Rossi"
   -> "Ho trovato 2 clienti. Mi puo dire la sua data di nascita?"

2. Data sbagliata (es. "10 gennaio 1980")
   -> "Non ho trovato questa data. Mario o Marione?"

3. "Marione"
   -> "Perfetto, Mario Rossi!" (cliente con soprannome)
```

## FAQ Verticali System

| Verticale | File | FAQ |
|-----------|------|-----|
| salone | `voice-agent/data/faq_salone.json` | 25 |
| wellness | `voice-agent/data/faq_wellness.json` | 24 |
| medical | `voice-agent/data/faq_medical.json` | 24 |
| auto | `voice-agent/data/faq_auto.json` | 23 |
| altro | `voice-agent/data/faq_altro.json` | 10 |

## MCP Server

8 tools, 9 resources, SQLite integration.
See `docs/MCP_SERVER_IMPLEMENTATION.md` for details.

## Test Results (2026-01-29)

- Rust: 40 passed
- Python: 624 passed, 18 pre-existing failures (async)
- TypeScript: type-check PASS, ESLint PASS
- Core voice tests: 273 passing
