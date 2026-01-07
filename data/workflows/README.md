# FLUXION Workflow System

Sistema di state machine per conversazioni WhatsApp.

## File Structure

```
workflows/
├── README.md           ← Questo file
├── intents.json        ← Riconoscimento intent (keywords)
├── identificazione.json ← Identificazione cliente
├── prenotazione.json   ← Workflow prenotazione
├── modifica.json       ← Workflow modifica appuntamento
└── disdetta.json       ← Workflow disdetta
```

## Architecture

### Intent Detection (`intents.json`)
Keyword matching senza LLM. Priorità numerica per disambiguazione.

### State Machine
Ogni workflow è una serie di stati con:
- `message`: Testo da inviare
- `expect`: Tipo di input atteso
- `next`: Stato successivo
- `action`: Operazione DB (opzionale)
- `on_*`: Handler per risultati

### Session Management
- Sessione per numero telefono
- Timeout configurabile
- Context persiste tra stati

## Variables

Template variables `{{nome}}` vengono sostituite da:
1. Context sessione (dati raccolti)
2. Database lookup (cliente, servizi, operatori)
3. Impostazioni salone

## Flow Example

```
Cliente scrive "Ciao voglio prenotare"
  ↓
intents.json → match "prenota" → workflow: prenotazione
  ↓
identificazione.json → phone lookup → cliente trovato
  ↓
prenotazione.json → CHIEDI_SERVIZIO → CHIEDI_GIORNO → ...
  ↓
Appuntamento creato in DB
```

## Implementation Notes

- NO LLM required for booking flow
- Fuzzy matching per nomi servizi/operatori
- Date parsing naturale ("domani", "lunedì prossimo")
- Validazione orari/festività server-side
- Conflict detection automatico

## Testing

Per testare i workflow in console:
```bash
npm run tauri dev
# Apri Impostazioni → WhatsApp → Test Console
```
