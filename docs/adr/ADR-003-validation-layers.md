# ADR-003: Sistema di Validazione a 3 Layer

**Status**: Accepted
**Date**: 2026-01-03
**Deciders**: UX Team, Domain Architect

## Context

L'operatore deve poter creare appuntamenti "eccezionali" (fuori orario, festivi) per clienti VIP o emergenze. Un sistema binario (valido/invalido) sarebbe troppo rigido.

## Decision

Implementare **3 livelli di validazione** con severità crescente:

### Layer 1: Warning (Continuabile)

**Comportamento**: Mostra popup, operatore può procedere con conferma esplicita.

**Casi d'uso**:
- Appuntamento fuori orario lavorativo (es. 20:00)
- Giorno festivo
- Appuntamento oltre mezzanotte
- Cliente con storico pagamenti in ritardo

**UI**:
```
⚠️ Appuntamento fuori orario
L'orario richiesto (20:00) è fuori dalla fascia standard (9:00-18:00).
[Continua Comunque] [Scegli Altro Orario]
```

### Layer 2: Suggerimento (Proattivo)

**Comportamento**: Sistema propone alternativa migliore, ma permette scelta originale.

**Casi d'uso**:
- Slot adiacente libero più lungo
- Orario preferito storico del cliente (es. sempre 10:00)
- Operatore con specializzazione migliore disponibile

**UI**:
```
💡 Suggerimento
Il cliente preferisce appuntamenti alle 10:00 (3/5 storici).
Slot disponibile: Mar 7 Gen, 10:00-11:00
[Usa Suggerimento] [Mantieni 14:00]
```

### Layer 3: Blocco Hard (Invalido)

**Comportamento**: Impossibile procedere, nessun override.

**Casi d'uso**:
- Appuntamento nel passato
- Operatore già impegnato nello stesso slot
- Conflitto fisico: stessa sala prenotata
- Servizio richiede attrezzatura non disponibile

**UI**:
```
❌ Impossibile procedere
L'operatore Mario Rossi è già impegnato il 5 Gen alle 14:00.
[Scegli Altro Operatore] [Scegli Altro Orario]
```

## Validation Flow

```
Input Richiesta
    ↓
Hard Blocks? → Sì → BLOCCO (no override)
    ↓ No
Warnings? → Sì → MOSTRA WARNING (override possibile)
    ↓ No
Suggerimenti? → Sì → MOSTRA SUGGERIMENTO (informativo)
    ↓ No
PROPOSTA OK
```

## Rationale

**Vantaggi**:
- **Flessibilità**: Operatore non bloccato da regole rigide
- **Guida**: Sistema aiuta senza imporre
- **Auditabilità**: Ogni override tracciato in `appuntamento.override_validazioni`

**UX Principles**:
- Warning usa colore arancione (attenzione)
- Suggerimento usa colore blu (informativo)
- Blocco usa colore rosso (errore)

**Alternative considerate**:
- Validazione binaria: Troppo rigida
- Tutto permesso: Caos, nessuna guida

## Consequences

**Positivi**:
- Riduzione errori: Sistema previene solo l'impossibile
- Soddisfazione operatore: Controllo totale con supporto intelligente

**Negativi**:
- Complexity: 3 code path invece di 1
- Testing: Ogni validazione richiede 3 test (warning, suggerimento, blocco)

## Configuration

Regole configurabili in `config/validation-rules.yaml`:

```yaml
validation_levels:
  hard_block:
    - appuntamento_passato
    - conflict_operatore_stesso_orario

  warning_continuabile:
    - fuori_orario_lavorativo
    - giorno_festivo

  suggerimento:
    - slot_migliore_disponibile
    - orario_preferito_cliente
```

Operatore può disabilitare singole validazioni da UI (salvo hard blocks).
