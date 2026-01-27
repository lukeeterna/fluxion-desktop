# PRD - FLUXION Voice Agent "Sara" (Definitivo)

> **Versione**: 1.0
> **Data**: 2026-01-27
> **Autore**: Claude Code + Gianluca
> **Metodo**: Spec-Driven Development (ispirato BMAD/GSD)

---

## 1. Introduzione

### 1.1 Scopo
Sara e' l'assistente vocale di FLUXION, un gestionale desktop per PMI italiane (saloni, palestre, cliniche, ristoranti). Sara gestisce prenotazioni, risponde a domande frequenti e registra nuovi clienti tramite conversazione vocale in italiano.

### 1.2 Obiettivi
1. **Prenotazione completa** via voce in < 60 secondi (6-8 turni)
2. **Registrazione nuovo cliente** quando non trovato nel DB
3. **Disambiguazione** affidabile quando multipli clienti hanno stesso nome
4. **Cancellazione/Spostamento** appuntamenti esistenti
5. **FAQ** risposte immediate per domande comuni (orari, prezzi, servizi)
6. **Zero dipendenze cloud obbligatorie** - funziona offline (Groq opzionale per LLM)

### 1.3 Non-Goals (fuori scope)
- Multi-lingua (solo italiano)
- Multi-sede
- Pagamenti via voce
- Integrazione calendario esterno (Google Calendar, Outlook)

---

## 2. User Stories

### US-01: Prenotazione cliente esistente
**Come** cliente abituale, **voglio** prenotare un appuntamento parlando con Sara, **in modo che** non debba chiamare o usare un'app.

**Criteri di accettazione:**
- [ ] Sara chiede nome, servizio, data, ora
- [ ] Cerca il cliente nel DB per nome
- [ ] Se trovato 1 solo match: procede direttamente
- [ ] Mostra riepilogo prima di confermare
- [ ] Crea record `appuntamenti` nel DB con `fonte_prenotazione='voice'`
- [ ] Verifica: `SELECT * FROM appuntamenti WHERE fonte_prenotazione='voice'` restituisce record

### US-02: Prenotazione cliente nuovo
**Come** persona mai venuta, **voglio** che Sara mi registri e poi prenda l'appuntamento, **in modo che** non debba fare due passaggi separati.

**Criteri di accettazione:**
- [ ] Sara cerca nome nel DB, non trova match
- [ ] Propone registrazione: "Non ho trovato [nome]. Vuole registrarsi?"
- [ ] Se l'utente dice "si": raccoglie nome, cognome, telefono
- [ ] Crea record `clienti` nel DB via POST `/api/clienti/create`
- [ ] Prosegue automaticamente con il flusso prenotazione (chiede servizio, data, ora)
- [ ] Verifica: `SELECT * FROM clienti WHERE nome='Antonio'` restituisce record

### US-03: Disambiguazione omonimi
**Come** cliente con nome comune (es. "Mario"), **voglio** che Sara mi identifichi correttamente, **in modo che** la prenotazione sia associata al mio profilo.

**Criteri di accettazione:**
- [ ] Se la ricerca restituisce multipli clienti (`ambiguo=true`): chiede data di nascita
- [ ] Se data di nascita corrisponde a 1 cliente: usa quello
- [ ] Se data non corrisponde: fallback a soprannome ("Mario o Marione?")
- [ ] Se soprannome non risolve dopo 2 tentativi: chiede telefono come ultimo fallback
- [ ] Mai prenotare per il cliente sbagliato

### US-04: Cancellazione appuntamento
**Come** cliente, **voglio** cancellare il mio appuntamento parlando con Sara.

**Criteri di accettazione:**
- [ ] Riconosce intent CANCELLAZIONE ("cancella", "disdici", "annulla")
- [ ] Chiede nome per identificare il cliente
- [ ] Cerca appuntamenti futuri del cliente
- [ ] Se 1 appuntamento: chiede conferma cancellazione
- [ ] Se multipli: chiede quale cancellare (mostra lista)
- [ ] POST `/api/appuntamenti/cancel` con l'id corretto
- [ ] Verifica: `SELECT stato FROM appuntamenti WHERE id=?` = 'Cancellato'

### US-05: Spostamento appuntamento
**Come** cliente, **voglio** spostare il mio appuntamento a un'altra data/ora.

**Criteri di accettazione:**
- [ ] Riconosce intent SPOSTAMENTO ("sposta", "cambia", "anticipa", "posticipa")
- [ ] Identifica cliente e appuntamento esistente
- [ ] Chiede nuova data e/o ora
- [ ] Verifica disponibilita' nella nuova fascia
- [ ] POST `/api/appuntamenti/reschedule` con nuova data/ora
- [ ] Verifica: `data_ora_inizio` aggiornata nel DB

### US-06: Domanda FAQ
**Come** potenziale cliente, **voglio** chiedere orari/prezzi/servizi, **in modo che** decida se prenotare.

**Criteri di accettazione:**
- [ ] Riconosce intent INFO/FAQ ("quanto costa", "a che ora aprite", "che servizi fate")
- [ ] Risponde con dati dal verticale configurato (salone, palestra, etc.)
- [ ] Variabili sostituite: {{ORARIO_APERTURA}} -> "09:00" etc.
- [ ] Dopo la risposta FAQ, chiede se vuole prenotare

### US-07: Lista d'attesa
**Come** cliente, **voglio** essere messo in lista d'attesa se non ci sono slot, **in modo che** mi richiamino quando si libera un posto.

**Criteri di accettazione:**
- [ ] Se slot non disponibile: propone lista d'attesa
- [ ] Se accetta: POST `/api/waitlist/add` con priorita' (normale/vip)
- [ ] Conferma inserimento in lista

---

## 3. Flussi Conversazionali

### 3.1 Flusso Principale: Prenotazione (Happy Path)

```
TURNO 1:
  Sara: "Buongiorno! Sono Sara, l'assistente vocale di [NOME_ATTIVITA]. Come posso aiutarla?"
  Utente: "Vorrei prenotare un taglio"

  -> Intent: PRENOTAZIONE
  -> Entity: servizio="taglio"
  -> State: IDLE -> WAITING_NAME

TURNO 2:
  Sara: "Per il taglio! Mi puo' dire il suo nome?"
  Utente: "Antonio Rossi"

  -> Entity: nome="Antonio", cognome="Rossi"
  -> HTTP GET /api/clienti/search?q=Antonio+Rossi
  -> Risultato: 1 cliente trovato (id=42)
  -> State: WAITING_NAME -> WAITING_DATE

TURNO 3:
  Sara: "Piacere Antonio! Per quale giorno desidera prenotare?"
  Utente: "Domani"

  -> Entity: data="2026-01-28"
  -> State: WAITING_DATE -> WAITING_TIME

TURNO 4:
  Sara: "Domani 28 gennaio. A che ora preferisce?"
  Utente: "Alle 10"

  -> Entity: ora="10:00"
  -> HTTP POST /api/appuntamenti/disponibilita {data, servizio}
  -> Slot disponibile
  -> State: WAITING_TIME -> CONFIRMING

TURNO 5:
  Sara: "Riepilogo: Taglio capelli, domani 28 gennaio alle 10:00. Confermo?"
  Utente: "Si confermo"

  -> Intent: CONFERMA
  -> HTTP POST /api/appuntamenti/create {cliente_id, servizio, data, ora}
  -> Record creato nel DB
  -> State: CONFIRMING -> COMPLETED

TURNO 6:
  Sara: "Perfetto! L'appuntamento e' confermato. La aspettiamo domani alle 10. Arrivederci!"
```

### 3.2 Flusso: Cliente Non Trovato -> Registrazione

```
TURNO 2 (dopo nome):
  Utente: "Antonio"

  -> HTTP GET /api/clienti/search?q=Antonio
  -> Risultato: {clienti: [], ambiguo: false}
  -> State: WAITING_NAME -> PROPOSE_REGISTRATION

TURNO 3:
  Sara: "Non ho trovato Antonio tra i nostri clienti. Vuole registrarsi come nuovo cliente?"
  Utente: "Si"

  -> Intent: CONFERMA (nel contesto PROPOSE_REGISTRATION)
  -> State: PROPOSE_REGISTRATION -> REGISTERING_NAME

TURNO 4:
  Sara: "Perfetto! Mi puo' dire nome e cognome completi?"
  Utente: "Antonio Verdi"

  -> Entity: nome="Antonio", cognome="Verdi"
  -> State: REGISTERING_NAME -> REGISTERING_PHONE

TURNO 5:
  Sara: "Mi lascia un numero di telefono?"
  Utente: "333 1234567"

  -> Entity: telefono="3331234567"
  -> State: REGISTERING_PHONE -> REGISTERING_CONFIRM

TURNO 6:
  Sara: "Riepilogo: Antonio Verdi, telefono 333 123 4567. Tutto corretto?"
  Utente: "Si"

  -> HTTP POST /api/clienti/create {nome, cognome, telefono}
  -> Cliente creato (id=99)
  -> State: REGISTERING_CONFIRM -> WAITING_SERVICE

TURNO 7:
  Sara: "Registrazione completata! Ora, quale servizio desidera prenotare?"
  (continua con flusso prenotazione normale)
```

### 3.3 Flusso: Disambiguazione Omonimi

```
TURNO 2:
  Utente: "Mario Rossi"

  -> HTTP GET /api/clienti/search?q=Mario+Rossi
  -> Risultato: {clienti: [{id:1, nome:"Mario"}, {id:2, nome:"Mario"}], ambiguo: true}
  -> State: WAITING_NAME -> DISAMBIGUATING

TURNO 3:
  Sara: "Ho trovato piu' clienti con quel nome. Mi puo' dire la sua data di nascita?"
  Utente: "15 marzo 1985"

  -> HTTP GET /api/clienti/search?q=Mario+Rossi&data_nascita=1985-03-15
  -> Risultato: 1 match (id=1)
  -> State: DISAMBIGUATING -> WAITING_SERVICE (o WAITING_DATE se servizio gia' dato)

  Sara: "Trovato! Mario Rossi. Per quale servizio desidera prenotare?"
```

**Fallback soprannome (se data non corrisponde):**
```
TURNO 3b:
  Utente: "10 gennaio 1980" (data errata)

  -> Nessun match con data
  -> Controlla soprannomi: client1.soprannome="Marione", client2.soprannome=null

  Sara: "Non ho trovato questa data. Per caso la chiamano Mario o Marione?"
  Utente: "Marione"

  -> Match: client1 (soprannome="Marione")
```

### 3.4 Flusso: Cancellazione

```
TURNO 1:
  Utente: "Vorrei cancellare il mio appuntamento"

  -> Intent: CANCELLAZIONE
  -> State: IDLE -> CANCEL_WAITING_NAME

TURNO 2:
  Sara: "Mi puo' dire il suo nome per trovare l'appuntamento?"
  Utente: "Mario Rossi"

  -> Cerca cliente -> Cerca appuntamenti futuri del cliente
  -> Se 1 appuntamento trovato:

TURNO 3:
  Sara: "Ho trovato: Taglio capelli, venerdi' 30 gennaio alle 14:00. Vuole cancellarlo?"
  Utente: "Si"

  -> HTTP POST /api/appuntamenti/cancel {id}

TURNO 4:
  Sara: "Appuntamento cancellato. Posso aiutarla con altro?"
```

### 3.5 Flusso: Spostamento

```
TURNO 1:
  Utente: "Devo spostare l'appuntamento"

  -> Intent: SPOSTAMENTO
  -> State: IDLE -> RESCHEDULE_WAITING_NAME

TURNO 2-3: (identifica cliente e appuntamento come cancellazione)

TURNO 4:
  Sara: "A quale data vuole spostare?"
  Utente: "Lunedi' prossimo alle 16"

  -> Entity: data="2026-02-02", ora="16:00"
  -> Verifica disponibilita'
  -> HTTP POST /api/appuntamenti/reschedule {id, data, ora}

TURNO 5:
  Sara: "Spostato a lunedi' 2 febbraio alle 16:00. La aspettiamo!"
```

### 3.6 Flusso: FAQ + Proposta Prenotazione

```
TURNO 1:
  Utente: "Quanto costa un taglio donna?"

  -> Intent: INFO_PREZZI
  -> FAQ match: "Il taglio donna costa {{PREZZO_TAGLIO_DONNA}}"
  -> Variable substitution: "Il taglio donna costa 25 euro"

TURNO 2:
  Sara: "Il taglio donna costa 25 euro. Vuole prenotare?"
  Utente: "Si"

  -> Entra nel flusso prenotazione con servizio gia' noto
```

---

## 4. State Machine Specification

### 4.1 Stati

| Stato | Descrizione | Dati Richiesti |
|-------|-------------|----------------|
| `IDLE` | In attesa di input | - |
| `WAITING_NAME` | Chiede il nome del cliente | - |
| `WAITING_SERVICE` | Chiede quale servizio | nome, cliente_id |
| `WAITING_DATE` | Chiede la data | servizio |
| `WAITING_TIME` | Chiede l'ora | data |
| `CONFIRMING` | Mostra riepilogo e chiede conferma | tutti i campi |
| `COMPLETED` | Prenotazione creata | booking_id |
| `PROPOSE_REGISTRATION` | Propone registrazione nuovo cliente | nome (non trovato) |
| `REGISTERING_NAME` | Raccoglie nome completo | - |
| `REGISTERING_PHONE` | Raccoglie telefono | nome, cognome |
| `REGISTERING_CONFIRM` | Conferma dati registrazione | nome, cognome, telefono |
| `DISAMBIGUATING` | Chiede data nascita/soprannome | nome, lista_candidati |
| `CANCEL_WAITING_NAME` | Identifica cliente per cancellazione | - |
| `CANCEL_CONFIRMING` | Conferma cancellazione | appuntamento_id |
| `RESCHEDULE_WAITING_NAME` | Identifica cliente per spostamento | - |
| `RESCHEDULE_WAITING_DATE` | Chiede nuova data/ora | appuntamento_id |
| `RESCHEDULE_CONFIRMING` | Conferma spostamento | nuova_data, nuova_ora |
| `WAITLIST_PROPOSE` | Propone lista d'attesa | servizio, data (non disponibile) |

### 4.2 Transizioni

```
IDLE
  ├── intent=PRENOTAZIONE ──────────> WAITING_NAME (o WAITING_SERVICE se nome gia' dato)
  ├── intent=CANCELLAZIONE ─────────> CANCEL_WAITING_NAME
  ├── intent=SPOSTAMENTO ──────────> RESCHEDULE_WAITING_NAME
  ├── intent=INFO/FAQ ──────────────> IDLE (risponde e resta)
  └── intent=CORTESIA ──────────────> IDLE (saluta e resta)

WAITING_NAME
  ├── nome estratto, 1 match DB ───> WAITING_SERVICE (o WAITING_DATE se servizio gia' dato)
  ├── nome estratto, 0 match DB ───> PROPOSE_REGISTRATION
  ├── nome estratto, N match DB ───> DISAMBIGUATING
  └── nome non estratto ───────────> WAITING_NAME (chiede di nuovo)

PROPOSE_REGISTRATION
  ├── intent=CONFERMA (si) ────────> REGISTERING_NAME
  └── intent=RIFIUTO (no) ────────> IDLE ("Va bene, posso aiutarla con altro?")

REGISTERING_NAME -> REGISTERING_PHONE -> REGISTERING_CONFIRM
  ├── intent=CONFERMA ─────────────> WAITING_SERVICE (cliente creato, continua booking)
  └── intent=RIFIUTO ──────────────> REGISTERING_NAME (ricomincia registrazione)

DISAMBIGUATING
  ├── data_nascita match ──────────> WAITING_SERVICE
  ├── soprannome match ────────────> WAITING_SERVICE
  └── max tentativi (2) ──────────> chiede telefono come fallback finale

WAITING_SERVICE -> WAITING_DATE -> WAITING_TIME -> CONFIRMING
  ├── intent=CONFERMA ─────────────> COMPLETED (crea appuntamento)
  ├── intent=RIFIUTO ──────────────> IDLE
  └── "cambia [campo]" ───────────> torna allo stato del campo

WAITING_TIME (slot non disponibile)
  └── no slot ─────────────────────> WAITLIST_PROPOSE

WAITLIST_PROPOSE
  ├── intent=CONFERMA ─────────────> COMPLETED (aggiunto a waitlist)
  └── intent=RIFIUTO ──────────────> WAITING_TIME ("A che altra ora?")

CANCEL_WAITING_NAME -> CANCEL_CONFIRMING
  ├── intent=CONFERMA ─────────────> COMPLETED (appuntamento cancellato)
  └── intent=RIFIUTO ──────────────> IDLE

RESCHEDULE_WAITING_NAME -> RESCHEDULE_WAITING_DATE -> RESCHEDULE_CONFIRMING
  ├── intent=CONFERMA ─────────────> COMPLETED (appuntamento spostato)
  └── intent=RIFIUTO ──────────────> IDLE
```

### 4.3 Slot Filling

| Slot | Estrazione | Validazione | Formato DB |
|------|-----------|-------------|------------|
| `nome` | spaCy NER (PERSON) + regex | Non in blacklist | string |
| `cognome` | Seconda parola dopo nome | >= 2 caratteri | string |
| `servizio` | Fuzzy match vs lista servizi | Esiste nel DB | string (nome) |
| `data` | Regex italiano + dateutil | Non nel passato, non festivo | YYYY-MM-DD |
| `ora` | Regex HH:MM, "alle X" | Dentro orario apertura | HH:MM |
| `telefono` | Estrazione cifre | 10+ cifre, inizia con 3 | string (solo cifre) |
| `data_nascita` | Regex data italiana | Data valida, < oggi | YYYY-MM-DD |

---

## 5. Bug Aperti da Fixare

### BUG-1: Cliente non trovato non propone registrazione (P0)
**Stato attuale**: Orchestrator cerca cliente, se 0 risultati imposta `is_new_client=True` e risposta "Vuole registrarsi?", MA lo stato booking_sm non viene aggiornato correttamente.
**Root cause**: `sm_result.needs_db_lookup` potrebbe non essere `True` in tutti i percorsi. Inoltre manca gestione del "si" dopo la proposta.
**Fix**: Verificare che dopo PROPOSE_REGISTRATION + "si", la state machine transizioni a REGISTERING_NAME.
**File**: `orchestrator.py` linee 573-610, `booking_state_machine.py` stati registrazione
**Test**: Conversazione "Sono Antonio" -> "Si voglio registrarmi" -> deve chiedere nome completo

### BUG-2: Guided Dialog mai attivato (P1)
**Stato attuale**: `guided_dialog.py` (1205 righe) esiste ma non viene mai chiamato dall'orchestrator.
**Root cause**: Linee 268-284 di orchestrator.py, `self.guided_engine` inizializzato ma `process()` non lo usa.
**Fix**: Attivare guided dialog quando `fallback_count >= 2` (utente fuori strada).
**File**: `orchestrator.py`
**Test**: Dire cose senza senso 3 volte -> Sara deve guidare la conversazione

### BUG-3: Disponibilita' slot non verificata prima di conferma (P1)
**Stato attuale**: Codice skeleton per verifica disponibilita'. Non chiama l'endpoint in produzione.
**Fix**: Chiamare POST `/api/appuntamenti/disponibilita` quando utente fornisce data+ora.
**File**: `orchestrator.py` linee 612-626
**Test**: Prenotare slot gia' occupato -> Sara deve dire "non disponibile" e proporre alternative

### BUG-4: Layer 3 NLU sempre skippato (P2)
**Stato attuale**: `orchestrator.py` linea 406 chiama `nlu.process(skip_layer3=True)`.
**Root cause**: Scelta di performance, ma esclude UmBERTo classification.
**Fix**: Skip L3 solo se PyTorch non disponibile. Se disponibile, usarlo.
**File**: `orchestrator.py` linea 406, `italian_nlu.py`
**Test**: Intent recognition accuracy migliore con L3 attivo

### BUG-5: Cancellazione/Spostamento non integrati end-to-end (P1)
**Stato attuale**: Endpoint Rust esistono, intent detection esiste, MA orchestrator non gestisce il flusso completo (cerca appuntamento del cliente, chiede conferma, chiama endpoint).
**Fix**: Implementare `_handle_cancellation()` e `_handle_reschedule()` nell'orchestrator.
**File**: `orchestrator.py`
**Test**: "Voglio cancellare il mio appuntamento" -> cerca, conferma, cancella, verifica DB

### BUG-6: Session state perso su riconnessione (P2)
**Stato attuale**: `booking_sm.context` e' in-memory. Se l'app crasha o l'utente riapre, tutto perso.
**Fix**: Serializzare context in session DB a ogni turno.
**File**: `orchestrator.py`, `booking_state_machine.py`

---

## 6. Requisiti Non-Funzionali

### 6.1 Performance
| Operazione | Target | Attuale |
|------------|--------|---------|
| Intent classification (L0+L1) | < 10ms | ~5ms |
| Entity extraction | < 50ms | ~30ms |
| HTTP Bridge lookup | < 500ms | ~200ms |
| Groq LLM fallback | < 1000ms | ~700ms |
| TTS synthesis | < 500ms | ~150ms (Piper) |
| **End-to-end (voce in -> voce out)** | **< 3s** | **~2s** |

### 6.2 Accuratezza
| Metrica | Target | Attuale |
|---------|--------|---------|
| Intent classification | > 90% | ~85% (senza L3) |
| Entity extraction (nome) | > 95% | ~90% |
| Entity extraction (data) | > 90% | ~85% |
| FAQ retrieval | > 80% | ~75% (solo keyword) |
| STT (Whisper WER) | < 15% | 21.7% |

### 6.3 Robustezza
- Massimo 3 turni di "non ho capito" prima di proporre fallback (testo, operatore umano)
- Ogni errore HTTP Bridge deve produrre un messaggio utente comprensibile
- Nessun crash silenzioso: ogni eccezione loggata e gestita

---

## 7. API Contract (HTTP Bridge)

### 7.1 Endpoint Critici per Voice Agent

| Endpoint | Metodo | Payload | Risposta |
|----------|--------|---------|----------|
| `/api/clienti/search` | GET | `?q=nome&data_nascita=YYYY-MM-DD` | `{clienti: [...], ambiguo: bool}` |
| `/api/clienti/create` | POST | `{nome, cognome?, telefono?, email?}` | `{success, id}` |
| `/api/appuntamenti/disponibilita` | POST | `{data, servizio}` | `{slots: ["HH:MM"]}` |
| `/api/appuntamenti/create` | POST | `{cliente_id, servizio, data, ora, operatore_id?}` | `{success, id}` |
| `/api/appuntamenti/cancel` | POST | `{id}` | `{success}` |
| `/api/appuntamenti/reschedule` | POST | `{id, data, ora}` | `{success}` |
| `/api/operatori/list` | GET | - | `[{id, nome, specializzazioni}]` |
| `/api/waitlist/add` | POST | `{cliente_id, servizio, data_preferita?}` | `{success, id}` |

### 7.2 Field Mapping (Python -> Rust)

| Python Context Key | HTTP Payload Key | Note |
|-------------------|-----------------|------|
| `service` | `servizio` | Orchestrator trasforma |
| `date` | `data` | Formato YYYY-MM-DD |
| `time` | `ora` | Formato HH:MM |
| `client_id` | `cliente_id` | UUID string |
| `operator_id` | `operatore_id` | UUID string (opzionale) |

---

## 8. Milestone di Implementazione

### M1: Fix Registrazione Cliente (Bug Antonio) - CRITICO
**Scope**: Fixare il flusso "cliente non trovato -> registrazione"
**File**: `orchestrator.py`, `booking_state_machine.py`
**Test**: Conversazione completa con "Antonio" -> registrazione -> prenotazione
**Acceptance**: Record creato in tabella `clienti` E poi `appuntamenti`

### M2: Verifica Disponibilita' Slot
**Scope**: Chiamare endpoint disponibilita' prima di confermare
**File**: `orchestrator.py`
**Test**: Prenotare slot occupato -> propone alternative -> waitlist
**Acceptance**: No prenotazioni su slot gia' occupati

### M3: Cancellazione e Spostamento End-to-End
**Scope**: Completare flussi cancellazione e reschedule
**File**: `orchestrator.py`
**Test**: Cancellare e spostare appuntamento via voce, verificare DB
**Acceptance**: `stato='Cancellato'` e `data_ora_inizio` aggiornata

### M4: Guided Dialog Fallback
**Scope**: Attivare guided_dialog quando utente fuori strada
**File**: `orchestrator.py`
**Test**: 3 turni incomprensibili -> Sara guida la conversazione
**Acceptance**: Conversazione non si blocca mai

### M5: Test Automatici Completi
**Scope**: Test pytest per ogni flusso conversazionale di questo PRD
**File**: `voice-agent/tests/test_prd_flows.py`
**Test**: Tutti i flussi sezioni 3.1-3.6 coperti
**Acceptance**: `pytest test_prd_flows.py` -> tutti passano

---

## 9. Architettura Target

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (React)                  │
│  VoiceAgent.tsx -> useVADRecorder -> Audio Chunks    │
└──────────────┬──────────────────────────────────────┘
               │ HTTP (porta 3002)
┌──────────────▼──────────────────────────────────────┐
│              VOICE PIPELINE (Python)                 │
│                                                      │
│  main.py (aiohttp server)                           │
│    ├── /greet         -> Orchestrator.greet()        │
│    ├── /process       -> Orchestrator.process()      │
│    ├── /process-audio -> STT + Orchestrator.process()│
│    ├── /reset         -> Orchestrator.reset()        │
│    └── /api/voice/vad/* -> VAD Handler               │
│                                                      │
│  orchestrator.py (CERVELLO)                         │
│    ├── L0: Special commands (reset, help)            │
│    ├── L1: Intent (regex + NLU)                      │
│    │   ├── PRENOTAZIONE -> booking_state_machine     │
│    │   ├── CANCELLAZIONE -> cancel flow              │
│    │   ├── SPOSTAMENTO -> reschedule flow            │
│    │   ├── INFO/FAQ -> faq_manager                   │
│    │   └── CORTESIA -> greeting response             │
│    ├── L2: Booking State Machine (slot filling)      │
│    ├── L3: FAQ Manager (keyword + semantic)          │
│    ├── L4: Groq LLM (fallback)                       │
│    └── Guided Dialog (fallback dopo 2 fail)          │
│                                                      │
│  Supporto:                                           │
│    ├── disambiguation_handler.py                     │
│    ├── vertical_integration.py                       │
│    ├── tts.py (Chatterbox/Piper/System)              │
│    └── stt.py (Whisper via Groq)                     │
└──────────────┬──────────────────────────────────────┘
               │ HTTP (porta 3001)
┌──────────────▼──────────────────────────────────────┐
│            HTTP BRIDGE (Rust/Tauri)                   │
│  http_bridge.rs -> SQLite (27 endpoint)              │
│    ├── /api/clienti/search                           │
│    ├── /api/clienti/create                           │
│    ├── /api/appuntamenti/create                      │
│    ├── /api/appuntamenti/cancel                      │
│    ├── /api/appuntamenti/reschedule                  │
│    ├── /api/appuntamenti/disponibilita               │
│    ├── /api/operatori/list                           │
│    ├── /api/waitlist/add                             │
│    └── /api/verticale/config                         │
└─────────────────────────────────────────────────────┘
```

---

## 10. Checklist Finale (Definition of Done)

Per ogni milestone:
- [ ] Codice scritto e compilabile
- [ ] Test automatico che copre il flusso
- [ ] Test manuale: conversazione completa funziona
- [ ] Verifica DB: `SELECT` conferma record creati/modificati
- [ ] Type-check TypeScript: `npm run type-check` passa
- [ ] Lint: `npm run lint` passa
- [ ] E2E su iMac: `npx playwright test` passa
- [ ] Nessuna regressione sui 426 test Python esistenti

---

*PRD generato il 2026-01-27. Questo documento e' la fonte di verita' per l'implementazione del Voice Agent definitivo.*
