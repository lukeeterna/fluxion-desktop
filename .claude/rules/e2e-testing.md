# Test E2E Obbligatori — NON NEGOZIABILE

OGNI task, OGNI fix, OGNI feature DEVE avere test E2E prima di essere completato.
ZERO eccezioni. "Lo testo dopo" NON ESISTE.

## Per tipo di task

| Tipo | Test |
|------|------|
| Voice Agent | `curl -X POST http://127.0.0.1:3002/api/voice/process` su iMac |
| Frontend React | Navigazione → interazione → risultato visibile |
| Backend Rust | `invoke()` IPC → risposta corretta con dati reali |
| Landing/CF Worker | `curl` endpoint → HTML/JSON corretto |
| DB/Migrations | Query SQL su DB reale → schema + dati ok |

## Formato output
```
OK  [VERTICAL] [SCENARIO]: [INPUT] → [OUTPUT] (LAYER)
WARN [VERTICAL] [SCENARIO]: [INPUT] → [OUTPUT INATTESO] (MOTIVO)
FAIL [VERTICAL] [SCENARIO]: [INPUT] → ERRORE (DETTAGLIO)
```

## Regola
1. Implementa fix/feature
2. Testa E2E (iMac/browser/curl)
3. SOLO SE tutti pass → task completato
4. Se 1 fail → torna a implementare
