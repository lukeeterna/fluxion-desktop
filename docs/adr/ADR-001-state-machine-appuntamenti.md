# ADR-001: State Machine per Workflow Appuntamenti

**Status**: Accepted
**Date**: 2026-01-03
**Deciders**: Backend Team, Domain Architect

## Context

L'MVP attuale gestisce gli appuntamenti con logica sparsa tra controller, UI e database. Serve un modello formale che:
- Impedisca transizioni di stato invalide
- Permetta all'operatore di override validazioni
- Renda testabile ogni transizione in isolamento

## Decision

Implementare il workflow appuntamenti come **State Machine** con stati espliciti e transizioni controllate.

### Stati del Sistema

```
Bozza → Proposta → InAttesaOperatore → {Confermato | Rifiutato | Cancellato}
                                              ↓
                                          Completato
```

**Stati**:
- `Bozza`: Cliente sta compilando, nessuna validazione
- `Proposta`: Sistema ha validato, presenta warning/suggerimenti
- `InAttesaOperatore`: Notifica inviata, attesa conferma umana
- `Confermato`: Operatore ha accettato (con/senza override)
- `Rifiutato`: Operatore ha rifiutato
- `Completato`: Servizio erogato
- `Cancellato`: Cliente o operatore ha cancellato

### Transizioni Permesse

| Da                  | A                      | Chi          | Condizione                          |
|---------------------|------------------------|--------------|-------------------------------------|
| Bozza               | Proposta               | Sistema      | Validazioni soft passate            |
| Proposta            | InAttesaOperatore      | Cliente      | Conferma richiesta                  |
| InAttesaOperatore   | Confermato             | Operatore    | Accetta senza warning               |
| InAttesaOperatore   | ConfermatoConOverride  | Operatore    | Accetta forzando validazioni        |
| InAttesaOperatore   | Rifiutato              | Operatore    | Rifiuta                             |
| Confermato          | Completato             | Sistema      | Data/ora superata                   |
| Confermato          | Cancellato             | Cliente/Op.  | Cancellazione pre-appuntamento      |

### Proprietà della State Machine

- **Determinismo**: Ogni transizione ha un solo esito possibile
- **Immutabilità storica**: Stato precedente tracciato in `eventi_dominio`
- **Validazione atomica**: Ogni transizione valida TUTTE le invarianti prima di mutare

## Rationale

**Vantaggi**:
- **Testabilità**: Ogni transizione è una funzione pura testabile
- **Override controllato**: Operatore può forzare, ma lascia traccia (`ConfermatoConOverride`)
- **Zero stati inconsistenti**: Impossibile avere appuntamento "confermato ma senza operatore"

**Alternative considerate**:
- Flag booleani (`is_confermato`, `is_rifiutato`): Porta a stati contraddittori
- Workflow engine esterno: Overkill per questo dominio

## Consequences

**Positivi**:
- Riduzione bug: Impossibile transizione invalida
- Auditabilità: Storico completo in `eventi_dominio`
- Performance: Validazioni costose solo in transizioni specifiche

**Negativi**:
- Più codice upfront (compensato da meno bug)
- Modifiche future richiedono aggiornamento diagramma
