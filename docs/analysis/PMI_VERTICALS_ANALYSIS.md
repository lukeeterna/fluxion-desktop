# PMI Verticali Fluxion - Analisi Completa

## SISTEMA BOOKING - Funzionalità Core

### FONDAMENTALE: Interazione Voice Agent ↔ Database

Il Voice Agent **Sara** interagisce direttamente con il database SQLite per gestire tutte le operazioni di booking in tempo reale.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VOICE AGENT BOOKING FLOW                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   UTENTE (telefono)          SARA (Voice Agent)           DATABASE      │
│   ┌─────────────┐           ┌─────────────────┐         ┌───────────┐  │
│   │ "Vorrei     │           │                 │         │           │  │
│   │  prenotare  │──────────▶│  1. Estrae:     │         │ clienti   │  │
│   │  un taglio  │           │     - cliente   │────────▶│ servizi   │  │
│   │  per domani │           │     - servizio  │         │ operatori │  │
│   │  alle 15"   │           │     - data/ora  │◀────────│ orari     │  │
│   └─────────────┘           │                 │         │ appunt.   │  │
│                             │  2. Verifica    │         │ waitlist  │  │
│                             │     disponib.   │         └───────────┘  │
│                             │                 │                        │
│   ┌─────────────┐           │  3. Conferma o  │                        │
│   │ "Perfetto,  │◀──────────│     propone     │                        │
│   │  confermato │           │     alternative │                        │
│   │  domani 15" │           └─────────────────┘                        │
│   └─────────────┘                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Operazioni di Booking Supportate

#### 1. PRENOTAZIONE (`/api/appuntamenti/create`)

```
Intent: PRENOTAZIONE
Entità estratte dal Voice Agent:
├── cliente_id      → SELECT id FROM clienti WHERE ...
├── servizio_id     → SELECT id FROM servizi WHERE nome LIKE '%taglio%'
├── operatore_id    → SELECT id FROM operatori WHERE nome = 'Marco' (opzionale)
├── data            → DATE '2026-01-16'
└── ora             → TIME '15:00'

Verifica disponibilità:
├── Slot libero?    → SELECT * FROM appuntamenti WHERE data = ? AND ora_inizio = ?
├── Operatore OK?   → Competenze + turno attivo
└── Orario apertura? → Controllo su tabella orari
```

**Flusso conversazionale:**
```
Utente: "Vorrei prenotare un taglio per domani pomeriggio"
Sara:   "Certamente! Per che ora preferisce? Abbiamo disponibilità alle 14:00, 15:30 e 17:00"
Utente: "Le 15:30 va bene"
Sara:   "Perfetto! Prenotazione confermata per domani, 16 gennaio, alle 15:30 per un taglio.
         A presto!"
```

#### 2. CANCELLAZIONE (`/api/appuntamenti/cancel`)

```
Intent: CANCELLAZIONE
Entità estratte:
├── cliente_id      → Identificato da nome/telefono
└── appuntamento_id → SELECT id FROM appuntamenti WHERE cliente_id = ? AND data >= date('now')

Azione:
├── UPDATE appuntamenti SET stato = 'cancellato', cancellato_at = datetime('now')
└── INSERT INTO appuntamenti_log (evento = 'CANCELLATO', motivo = ?)
```

**Flusso conversazionale:**
```
Utente: "Devo cancellare l'appuntamento di domani"
Sara:   "Ho trovato il suo appuntamento per domani alle 15:30: taglio con Marco.
         Conferma la cancellazione?"
Utente: "Sì, confermo"
Sara:   "Appuntamento cancellato. Può prenotare nuovamente quando vuole. Arrivederci!"
```

#### 3. SPOSTAMENTO (`/api/appuntamenti/reschedule`)

```
Intent: MODIFICA / SPOSTAMENTO
Entità estratte:
├── appuntamento_id → Appuntamento esistente
├── nuova_data      → DATE richiesta
└── nuova_ora       → TIME richiesta

Azione (transazione):
├── BEGIN TRANSACTION
├── Verifica nuova disponibilità
├── UPDATE appuntamenti SET data = ?, ora_inizio = ?, ora_fine = ?
├── INSERT INTO appuntamenti_log (evento = 'SPOSTATO')
└── COMMIT
```

**Flusso conversazionale:**
```
Utente: "Posso spostare l'appuntamento di domani a giovedì?"
Sara:   "Certo! Giovedì 18 gennaio è disponibile alle 10:00, 14:30 e 16:00.
         Quale preferisce?"
Utente: "Le 14:30"
Sara:   "Perfetto! Ho spostato il suo appuntamento da domani 15:30 a giovedì 18
         alle 14:30. Stesso servizio: taglio con Marco."
```

#### 4. LISTA D'ATTESA (`/api/waitlist/add`)

```
Intent: LISTA_ATTESA (quando nessuno slot disponibile)
Entità estratte:
├── cliente_id
├── servizio_id
├── data_preferita
├── fascia_oraria   → "mattina" | "pomeriggio" | "qualsiasi"
└── priorita        → "normale" | "vip" (basato su cliente.vip_status)

Azione:
├── INSERT INTO waitlist (cliente_id, servizio_id, data_richiesta, fascia, priorita)
└── Trigger automatico quando slot si libera
```

**Flusso conversazionale:**
```
Utente: "Vorrei un appuntamento per sabato mattina"
Sara:   "Mi dispiace, sabato mattina siamo al completo. Posso metterla in lista
         d'attesa? La chiameremo appena si libera un posto."
Utente: "Sì, grazie"
Sara:   "Perfetto! L'ho inserita in lista d'attesa per sabato mattina.
         La contatteremo al più presto se si libera uno slot."
```

### Tabelle Database Coinvolte

| Tabella | Ruolo nel Booking | Campi Chiave |
|---------|-------------------|--------------|
| `clienti` | Anagrafica cliente | id, nome, cognome, telefono, email, data_nascita, soprannome |
| `servizi` | Catalogo servizi | id, nome, prezzo, durata, categoria, attivo |
| `operatori` | Staff disponibile | id, nome, specializzazioni, orario_lavoro |
| `appuntamenti` | Prenotazioni | id, cliente_id, servizio_id, operatore_id, data, ora_inizio, ora_fine, stato |
| `orari` | Orari apertura | giorno, apertura, chiusura, pausa_inizio, pausa_fine |
| `waitlist` | Lista d'attesa | id, cliente_id, servizio_id, data_richiesta, fascia, priorita, notificato |
| `appuntamenti_log` | Audit trail | id, appuntamento_id, evento, timestamp, dettagli |

### HTTP Bridge Endpoints

| Endpoint | Metodo | Scopo |
|----------|--------|-------|
| `/api/clienti/search` | POST | Cerca cliente per nome/telefono |
| `/api/clienti/create` | POST | Registra nuovo cliente |
| `/api/appuntamenti/create` | POST | Crea prenotazione |
| `/api/appuntamenti/cancel` | POST | Cancella appuntamento |
| `/api/appuntamenti/reschedule` | POST | Sposta appuntamento |
| `/api/appuntamenti/disponibilita` | GET | Verifica slot disponibili |
| `/api/waitlist/add` | POST | Aggiungi a lista d'attesa |
| `/api/waitlist/notify` | POST | Notifica slot liberato |
| `/api/operatori/list` | GET | Lista operatori disponibili |
| `/api/servizi/list` | GET | Lista servizi attivi |

### Disambiguazione Cliente

Quando più clienti hanno lo stesso nome:

```
1. "Prenotazione per Mario Rossi"
   → Query: SELECT * FROM clienti WHERE nome = 'Mario' AND cognome = 'Rossi'
   → Risultato: 2 clienti trovati

2. Sara: "Ho trovato 2 clienti con questo nome. Mi può dire la sua data di nascita?"

3. Cliente: "10 marzo 1985"
   → Query: SELECT * FROM clienti WHERE nome = 'Mario' AND cognome = 'Rossi'
            AND data_nascita = '1985-03-10'
   → Risultato: 1 cliente (match!)

4. Se data non corrisponde → Fallback soprannome:
   Sara: "Non ho trovato questa data. È Mario o Marione?"
   → Query: SELECT * FROM clienti WHERE soprannome IN ('Mario', 'Marione')
```

---

## Sistema FAQ Dinamiche con Variabili DB

### IMPORTANTE: Come Funzionano le FAQ

Le FAQ di FLUXION **NON sono testo statico**. Sono template che vengono popolati in tempo reale con i dati del database SQLite del cliente.

```
┌─────────────────────────────────────────────────────────────────┐
│                  ARCHITETTURA FAQ FLUXION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   DATABASE SQLite                    TEMPLATE FAQ               │
│   ┌──────────────────┐              ┌──────────────────┐       │
│   │ servizi          │              │ "Il servizio     │       │
│   │ ├─ nome: Taglio  │──────────────│  {{SERVIZIO}}    │       │
│   │ ├─ prezzo: 18    │              │  costa           │       │
│   │ └─ durata: 30    │              │  {{PREZZO}}€     │       │
│   └──────────────────┘              │  e dura          │       │
│                                     │  {{DURATA}} min" │       │
│                                     └──────────────────┘       │
│                                              │                  │
│                                              ▼                  │
│                                     ┌──────────────────┐       │
│                                     │ OUTPUT FINALE:   │       │
│                                     │ "Il servizio     │       │
│                                     │  Taglio costa    │       │
│                                     │  18€ e dura      │       │
│                                     │  30 min"         │       │
│                                     └──────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Variabili Disponibili

| Variabile | Tabella Source | Query SQL | Esempio Output |
|-----------|----------------|-----------|----------------|
| `{{NOME_ATTIVITA}}` | `setup` | `SELECT business_name FROM setup` | "Salone Maria" |
| `{{INDIRIZZO}}` | `setup` | `SELECT address FROM setup` | "Via Roma 15, Milano" |
| `{{TELEFONO}}` | `setup` | `SELECT phone FROM setup` | "02 1234567" |
| `{{EMAIL}}` | `setup` | `SELECT email FROM setup` | "info@salone.it" |
| `{{VERTICALE}}` | `setup` | `SELECT business_type FROM setup` | "salone" |
| `{{LISTA_SERVIZI}}` | `servizi` | `SELECT nome, prezzo, durata FROM servizi WHERE attivo = 1` | Lista formattata |
| `{{SERVIZIO_PIU_RICHIESTO}}` | `servizi` JOIN `appuntamenti` | Aggregazione per popolarità | "Taglio Donna" |
| `{{ORARI_APERTURA}}` | `orari` | `SELECT giorno, apertura, chiusura FROM orari` | "Lun-Ven 9-19" |
| `{{LISTA_OPERATORI}}` | `operatori` | `SELECT nome, specializzazione FROM operatori WHERE attivo = 1` | "Marco, Sara, Giulia" |
| `{{POLITICA_DISDETTA}}` | `setup` | `SELECT cancellation_policy FROM setup` | "Gratuita entro 24h" |
| `{{METODI_PAGAMENTO}}` | `setup` | `SELECT payment_methods FROM setup` | "Contanti, Carte, Satispay" |

### Esempio Pratico: Salone "Maria Style"

**Dati nel DB:**
```sql
-- Tabella setup
INSERT INTO setup (business_name, address, phone, business_type)
VALUES ('Maria Style', 'Via Garibaldi 42, Torino', '011 5551234', 'salone');

-- Tabella servizi
INSERT INTO servizi (nome, prezzo, durata) VALUES
  ('Taglio Donna', 35, 60),
  ('Taglio Uomo', 18, 30),
  ('Piega', 20, 30),
  ('Colore', 55, 90);

-- Tabella operatori
INSERT INTO operatori (nome, specializzazione) VALUES
  ('Maria', 'Colorista'),
  ('Giulia', 'Taglio donna'),
  ('Marco', 'Barba e uomo');
```

**Template FAQ:**
```markdown
Benvenuto da {{NOME_ATTIVITA}}!
Siamo in {{INDIRIZZO}}.

I nostri servizi:
{{LISTA_SERVIZI}}

Il nostro team: {{LISTA_OPERATORI}}

Per prenotare chiama {{TELEFONO}}.
```

**Output Generato (runtime):**
```markdown
Benvenuto da Maria Style!
Siamo in Via Garibaldi 42, Torino.

I nostri servizi:
- Taglio Donna: €35 (60 min)
- Taglio Uomo: €18 (30 min)
- Piega: €20 (30 min)
- Colore: €55 (90 min)

Il nostro team: Maria (Colorista), Giulia (Taglio donna), Marco (Barba e uomo)

Per prenotare chiama 011 5551234.
```

---

## 1. SALONI DI PARRUCCHIERE

### Info Base
| Campo | Valore |
|-------|--------|
| **Nome IT** | Salone di Parrucchiere / Parrucchiere |
| **Nome EN** | Hair Salon |
| **Codice DB** | `salone` |
| **Categoria** | Beauty & Wellness |
| **Stage** | MVP ✅ |
| **Priorità** | ALTA (già implementato) |

### Servizi Standard (da DB `servizi`)
| Servizio | Prezzo Default | Durata | Variabile |
|----------|----------------|--------|-----------|
| Taglio Uomo | €18 | 30 min | `{{SERVIZIO_TAGLIO_UOMO}}` |
| Taglio Donna | €35 | 60 min | `{{SERVIZIO_TAGLIO_DONNA}}` |
| Piega | €20 | 30 min | `{{SERVIZIO_PIEGA}}` |
| Colore/Tinta | €55 | 90 min | `{{SERVIZIO_COLORE}}` |
| Meches/Balayage | €65-90 | 120 min | `{{SERVIZIO_MECHES}}` |
| Trattamento Ristrutturante | €30 | 45 min | `{{SERVIZIO_TRATTAMENTO}}` |
| Barba | €12 | 20 min | `{{SERVIZIO_BARBA}}` |

### Terminologia Dominio
**Gergo tecnico:**
- Balayage, meches, shatush, degradè
- Tinta, decolorazione, colpi di sole
- Trattamento ricostruttivo, cheratina

**Sinonimi (per NLU):**
| Termine Utente | Mappa a Servizio |
|----------------|------------------|
| "sforbiciata" | Taglio |
| "spuntatina" | Taglio punte |
| "messa in piega" | Piega |
| "colore" | Tinta |

### Business Rules (da `setup`)
- Lead time: 2-3 giorni anticipo
- Cancellazione: gratuita entro 24h (configurabile)
- No-show: dopo 3 volte → anticipo 50%
- Pacchetti prepagati: sconto 15-20%

### FAQ Files
- `voice-agent/data/faq_salone.md`
- `voice-agent/data/faq_salone_test.json` (23 FAQ)

---

## 2. CENTRI BENESSERE / PALESTRE

### Info Base
| Campo | Valore |
|-------|--------|
| **Nome IT** | Centro Benessere / Palestra |
| **Nome EN** | Gym / Fitness Center |
| **Codice DB** | `palestra` / `wellness` |
| **Categoria** | Fitness & Sports |
| **Stage** | MVP ✅ |
| **Priorità** | MEDIA |

### Servizi Standard
| Servizio | Prezzo Default | Durata |
|----------|----------------|--------|
| Abbonamento Mensile | €45 | - |
| Abbonamento Annuale | €400 | - |
| Corso Singolo | €10 | 60 min |
| Personal Training | €50 | 60 min |
| Yoga | incluso | 60 min |
| Pilates | incluso | 60 min |
| Spinning | incluso | 45 min |
| Nuoto/Piscina | incluso | - |

### Terminologia Dominio
| Termine Utente | Significato |
|----------------|-------------|
| "abbonamento" | Membership |
| "corso" | Lezione gruppo |
| "PT" | Personal Trainer |
| "sala pesi" | Area attrezzi |
| "prova" | Trial gratuito |

### Business Rules
- Prova gratuita: 1 settimana
- Sospensione abbonamento: possibile
- Cancellazione corsi: entro 2h prima
- Guest pass: disponibile

### FAQ Files
- `voice-agent/data/faq_palestra_test.json` (10 FAQ)

---

## 3. STUDI MEDICI / DENTISTI

### Info Base
| Campo | Valore |
|-------|--------|
| **Nome IT** | Studio Medico / Dentista |
| **Nome EN** | Medical Clinic / Dental Office |
| **Codice DB** | `studio_medico` / `medical` |
| **Categoria** | Healthcare |
| **Stage** | MVP ✅ |
| **Priorità** | ALTA (compliance sanitario) |

### Servizi Standard
| Servizio | Prezzo Default | Durata |
|----------|----------------|--------|
| Visita Generale | €80 | 30 min |
| Visita Specialistica | €120 | 45 min |
| Ecografia | €60-100 | 30 min |
| Analisi Sangue | €30-80 | 15 min |
| Certificato Medico | €30 | 15 min |

### Business Rules
- Prenotazione: OBBLIGATORIA
- Lead time: 3-7 giorni
- Cancellazione: 48h minimo
- No-show: penale 100%
- Detrazioni fiscali: 19%
- GDPR: Compliance sanitario rigoroso

### FAQ Files
- `voice-agent/data/faq_studio_test.json` (10 FAQ)

---

## 4. OFFICINE / CARROZZERIE

### Info Base
| Campo | Valore |
|-------|--------|
| **Nome IT** | Officina / Carrozzeria |
| **Nome EN** | Auto Repair Shop |
| **Codice DB** | `auto` |
| **Categoria** | Automotive |
| **Stage** | In Progress ⚠️ |
| **Priorità** | MEDIA |

### Servizi Standard
| Servizio | Prezzo | Durata |
|----------|--------|--------|
| Tagliando | Variabile | 2-4h |
| Revisione | €66.88 (fisso) | 1h |
| Cambio Gomme | €40-80 | 1h |
| Diagnosi | €30-50 | 30 min |

### Business Rules
- Preventivo gratuito
- Garanzia lavori: 12-24 mesi
- Ricambi: originali o equivalenti
- Emergenze: servizio H24 (opzionale)

### FAQ Files
- `voice-agent/prompts/prompt_auto.md` (template)

---

## 5. ALTRO / GENERICO

Placeholder per verticali custom. Usa logica generica FLUXION.

---

## Riepilogo Verticali

| # | Verticale | Codice DB | Stage | FAQ | Voice Tests | E2E |
|---|-----------|-----------|-------|-----|-------------|-----|
| 1 | **Salone** | `salone` | ✅ MVP | ✅ 23 | ✅ 20 conv | ✅ |
| 2 | **Palestra** | `palestra` | ✅ MVP | ✅ 10 | ✅ 3 conv | ✅ |
| 3 | **Studio Medico** | `medical` | ✅ MVP | ✅ 10 | ✅ 2 conv | ✅ |
| 4 | **Officina** | `auto` | ⚠️ WIP | ⚠️ Template | ❌ | ❌ |
| 5 | **Altro** | `altro` | ✅ | ❌ | ❌ | ❌ |

---

## UI Configuration

```typescript
// src/types/setup.ts
export const CATEGORIE_ATTIVITA = [
  { value: 'salone', label: 'Salone / Parrucchiere', icon: '💇' },
  { value: 'auto', label: 'Officina / Carrozzeria', icon: '🚗' },
  { value: 'wellness', label: 'Centro Benessere / Palestra', icon: '🧘' },
  { value: 'medical', label: 'Studio Medico / Dentista', icon: '🏥' },
  { value: 'altro', label: 'Altro', icon: '🏢' },
] as const;
```

---

## Prossimi Verticali (Fase 9)

| Verticale | Priorità | Complessità | Note |
|-----------|----------|-------------|------|
| **Estetica** | Alta | Media | Nail, extension, trattamenti |
| **Barbiere** | Media | Bassa | Subset salone, focus uomo |
| **Estetica** | Media | Media | Nail, extension, trattamenti |
| **Fisioterapia** | Alta | Alta | Prescrizioni, SSN |
| **Veterinario** | Media | Media | Animali, vaccini |

---

## Domande per Fase 2

1. Confermi che questi sono tutti i verticali attivi?
2. Priorità fine-tuning: saloni (già MVP) o cliniche (compliance)?
3. Budget GPU per training? (LoRA vs full fine-tuning)
4. Dataset esistente: hai conversazioni reali da clienti?
5. Modello base preferito? (Llama 3.1 8B, Mistral 7B, Qwen?)

---

*Generato: 2026-01-15*
