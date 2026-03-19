# F19 — Deep Research CoVe 2026: Sistema Prenotazioni World-Class per PMI Italiane

> **Data**: 2026-03-19 | **Sessione**: S94
> **Competitor analizzati**: Fresha, Mindbody, Jane App, Vagaro, Timely, Square Appointments, Acuity Scheduling, SimplyBook.me, Booker, Setmore, BookingBee AI, Retell AI, Vapi, SpaVoices, TalkForce AI, Voiceflow
> **Fonti**: Web search multi-query (10+ ricerche parallele)

---

## STATO ATTUALE FLUXION (cosa abbiamo GIA')

| Feature | Status | Dettaglio |
|---------|--------|-----------|
| FSM 23 stati | ✅ | IDLE → COMPLETED con tutti gli stati intermedi |
| Registrazione cliente (nome, cognome, telefono) | ✅ | Flow guidato con Kimi 2.5 |
| Servizi da DB | ✅ | Fuzzy match, multi-servizio detection |
| Operatori da DB | ✅ | Selezione operatore con disponibilità |
| Disambiguazione omonimia | ✅ | Levenshtein ≥70% + data nascita |
| Waitlist con priorità VIP | ✅ | PROPOSING_WAITLIST → WAITLIST_SAVED |
| WhatsApp conferma post-booking | ✅ | wa.me link 1-tap |
| Reminder -24h / -1h | ✅ | Scheduler automatico |
| Cancellazione/spostamento | ✅ | Via voice + da UI |
| FSM backtracking | ✅ | Correzioni durante il flusso |
| Barge-in | ✅ | Interruzione durante TTS |
| Buffer minuti servizio | ✅ (DB) | `buffer_minuti` in tabella `servizi` |
| Stato no_show | ✅ (DB) | `stato = 'no_show'` in appuntamenti |
| Servizi preferiti cliente | ✅ (schema verticale) | `servizi_preferiti` in salone/palestra schema |
| Multi-servizio detection | ✅ (regex) | Pattern "taglio e piega", "colore e trattamento" |

---

## FEATURE MANCANTI — ANALISI COMPLETA

### ═══════════════════════════════════════════════════════════════
### 1. SLOT INTELLIGENCE — Gestione Slot Avanzata
### ═══════════════════════════════════════════════════════════════

#### 1.1 Smart Gap Elimination (Fresha)
- **Competitor**: Fresha (feature "Intelligent Time Slots")
- **Cosa fa**: Quando un cliente prenota online, il sistema NON mostra tutti gli slot liberi. Mostra solo quelli che:
  - Riducono i gap nel calendario (opzione "Reduce calendar gaps")
  - Eliminano i gap mostrando SOLO slot adiacenti ad appuntamenti esistenti (opzione "Eliminate calendar gaps")
- **Perché manca in FLUXION**: Sara propone lo slot libero più vicino senza considerare l'ottimizzazione del calendario. Un booking alle 10:00 e uno alle 14:00 lascia un gap 11:00-14:00 difficile da riempire.
- **Implementazione Sara**: Quando Sara cerca slot disponibili, ordinare per "vicinanza ad appuntamenti esistenti" prima che per "primo disponibile". Query SQL: trova slot che creano gap minimi.
- **Priorità**: **P1** — differenziante significativo, riduce tempo morto operatore
- **Effort**: 2-3 giorni (logica SQL + integrazione FSM)

#### 1.2 Buffer Automatico tra Servizi (Fresha, Mindbody)
- **Competitor**: Fresha ("processing time"), Mindbody ("buffer time between appointments")
- **Cosa fa**: Il sistema aggiunge automaticamente tempo di pulizia/setup tra appuntamenti. Es: tinta ha 30min "processing time" — il cliente resta ma l'operatore può fare altro durante la posa.
- **Perché manca in FLUXION**: Il campo `buffer_minuti` esiste nel DB ma Sara NON lo usa quando propone slot. Il buffer non viene sottratto dalla disponibilità.
- **Implementazione Sara**: Nella query slot disponibili, sommare `durata_minuti + buffer_minuti` per il calcolo della finestra temporale occupata.
- **Priorità**: **P0** — BLOCKER. Senza buffer, Sara può sovrapporre appuntamenti.
- **Effort**: 1 giorno (fix query disponibilità nel bridge HTTP + voice agent)

#### 1.3 Pausa Pranzo / Blocco Fasce Orarie (Fresha, Mindbody)
- **Competitor**: Fresha ("blocked time"), tutti i competitor
- **Cosa fa**: Operatore definisce fasce non prenotabili (pranzo 13-14, uscita anticipata venerdì, etc.)
- **Perché manca in FLUXION**: La tabella `orari_apertura` gestisce apertura/chiusura ma NON fasce bloccate intra-giornaliere per singolo operatore.
- **Implementazione**: Tabella `blocchi_orario` (operatore_id, giorno, ora_inizio, ora_fine, ricorrente, motivo). Sara controlla blocchi prima di proporre slot.
- **Priorità**: **P0** — BLOCKER. Operatori pranzano. Senza questo, Sara prenota durante la pausa.
- **Effort**: 2 giorni (migration DB + logica disponibilità + UI impostazioni)

#### 1.4 Multi-Servizio Combo nella Stessa Sessione (Fresha, Salon Booking System)
- **Competitor**: Fresha, Salon Booking System, Vagaro
- **Cosa fa**: Cliente dice "taglio e colore" → sistema calcola durata totale (30+90=120min), trova slot da 2h, assegna stesso operatore.
- **Perché manca in FLUXION**: Il regex `extract_multi_services` esiste ma la FSM gestisce UN servizio alla volta. Non c'è logica per sommare durate e trovare slot contigui per servizi multipli.
- **Implementazione Sara**: Stato `WAITING_SERVICE` → se multi-servizio, somma durate + buffers, cerca slot unico. Salva N appuntamenti contigui con campo `gruppo_id` per raggrupparli.
- **Priorità**: **P0** — BLOCKER. "Taglio e piega" è la richiesta #1 nei saloni italiani.
- **Effort**: 3-4 giorni (FSM multi-servizio + query disponibilità composita + UI calendario)

---

### ═══════════════════════════════════════════════════════════════
### 2. APPUNTAMENTI RICORRENTI
### ═══════════════════════════════════════════════════════════════

#### 2.1 Ricorrenze Vocali (Acuity, Fresha, Jane App)
- **Competitor**: Acuity Scheduling, Fresha, Jane App (booking up to 1 year in advance)
- **Cosa fa**: "Stessa ora ogni 4 settimane" → crea 12 appuntamenti futuri in un colpo. Se uno slot è occupato, propone alternativa per quel singolo giorno.
- **Perché manca in FLUXION**: Nessun supporto ricorrenze. Ogni prenotazione è one-shot.
- **Implementazione Sara**:
  - Nuovo campo DB: `ricorrenza_id` + tabella `ricorrenze` (frequenza, data_inizio, data_fine, template)
  - Sara rileva pattern vocali: "ogni settimana", "ogni 15 giorni", "ogni mese", "il solito giorno"
  - Crea batch di appuntamenti, propone alternativa se conflitto su specifiche date
  - WhatsApp conferma con lista completa date
- **Priorità**: **P1** — differenziante forte per saloni e fisioterapisti
- **Effort**: 4-5 giorni (DB schema + FSM states + entity extraction + batch creation + UI)

---

### ═══════════════════════════════════════════════════════════════
### 3. PREFERENZE CLIENTE MEMORIZZATE
### ═══════════════════════════════════════════════════════════════

#### 3.1 Operatore Preferito (Vagaro, Fresha, tutti)
- **Competitor**: Tutti i competitor premium
- **Cosa fa**: Sistema ricorda che Mario va SEMPRE da Luca. Alla prossima prenotazione, propone Luca direttamente.
- **Perché manca in FLUXION**: Il campo `servizi_preferiti` esiste nello schema verticale ma NON c'è `operatore_preferito`. Sara non memorizza le preferenze tra sessioni.
- **Implementazione**:
  - Tabella `preferenze_cliente` (cliente_id, tipo, valore) o campo `operatore_preferito_id` in clienti
  - Sara: dopo 2+ booking con stesso operatore → segna come preferito
  - Al prossimo booking: "Vuole sempre con Luca, giusto?"
- **Priorità**: **P1** — alta retention, personalizzazione
- **Effort**: 2 giorni (DB + logica FSM + query)

#### 3.2 "Il Solito" — Servizio Abituale (AI Voice Agents trend 2026)
- **Competitor**: BookingBee AI, SpaVoices, Retell AI (tutti i voice agent 2026 lo fanno)
- **Cosa fa**: Cliente dice "il solito" → sistema propone ultimo servizio + operatore + giorno/ora della settimana abituale.
- **Perché manca in FLUXION**: Nessuna logica per "il solito". L'entity extractor non riconosce il pattern.
- **Implementazione Sara**:
  - Entity extractor: pattern "il solito", "come l'ultima volta", "come sempre", "quello di sempre"
  - Query: ultimi 3 appuntamenti del cliente → estrai servizio, operatore, giorno settimana, ora più frequente
  - Sara propone: "L'ultima volta ha fatto taglio con Marco il giovedì alle 15. Vuole confermare?"
- **Priorità**: **P0** — feature WOW per PMI italiane. Ogni competitor voice 2026 lo ha.
- **Effort**: 2-3 giorni (entity extraction + query history + FSM shortcut)

#### 3.3 Suggerimento Intelligente Post-Servizio (Meevo, SpaVoices)
- **Competitor**: Meevo, SpaVoices, Retell AI ("suggest add-on services during booking")
- **Cosa fa**: "L'ultima volta ha fatto taglio e piega. Vuole aggiungere anche il trattamento alla cheratina?"
- **Perché manca in FLUXION**: Nessun upselling/cross-selling in Sara.
- **Implementazione**:
  - Tabella `servizi_correlati` (servizio_id, servizio_suggerito_id, messaggio)
  - Dopo CONFIRMING, prima di COMPLETED: "Vuole aggiungere anche [servizio correlato]?"
  - Configurabile dal titolare (quali servizi suggerire con quali)
- **Priorità**: **P2** — nice-to-have, aumenta revenue ma non è blocker
- **Effort**: 2-3 giorni (DB + FSM state aggiuntivo + configurazione UI)

---

### ═══════════════════════════════════════════════════════════════
### 4. NO-SHOW MANAGEMENT
### ═══════════════════════════════════════════════════════════════

#### 4.1 Tracking No-Show con Penalità (Mindbody, Square, Fresha)
- **Competitor**: Mindbody (auto no-show dopo 10min, fee automatiche), Square (prepayment + cancellation fee), Fresha (no-show tracking)
- **Cosa fa**:
  - Dopo 10min dalla data appuntamento senza check-in → auto-mark no-show
  - Contatore no-show per cliente (3 no-show = flag/blocco)
  - Deposito richiesto per clienti con storico no-show
  - Email/SMS automatico con policy violazione
- **Perché manca in FLUXION**: Lo stato `no_show` esiste ma è solo un campo testo. Nessun contatore, nessuna automazione, nessuna penalità.
- **Implementazione**:
  - Campo `no_show_count` in `clienti` + auto-increment quando `stato = 'no_show'`
  - Scheduler: dopo X minuti da `data_ora_inizio` senza check-in → auto no-show
  - Sara: se `no_show_count >= 3` → "Le chiediamo gentilmente di confermare 24h prima, dato che in passato ci sono stati problemi di disponibilità"
  - Config: soglia no-show + azione (warning / blocco booking voice / richiedi deposito)
- **Priorità**: **P1** — riduce no-show del 40-55% secondo ricerca. Revenue diretto.
- **Effort**: 3 giorni (DB + scheduler + FSM logic + config UI)

#### 4.2 Deposito / Prepagamento per Servizi Costosi (Square, Acuity)
- **Competitor**: Square Appointments, Acuity, Lunacal
- **Cosa fa**: Per servizi > €X, richiede deposito 20-30% al momento della prenotazione. Card on file per fee cancellazione.
- **Perché manca in FLUXION**: Nessuna integrazione pagamenti.
- **Implementazione**: Non applicabile via voice (Sara non prende carte di credito al telefono). Ma possibile via WhatsApp post-booking: "Per confermare, effettui il deposito di €30 qui: [link Stripe/LemonSqueezy]"
- **Priorità**: **P2** — nice-to-have, complesso, richiede integrazione pagamenti
- **Effort**: 5+ giorni (integrazione Stripe + link pagamento + tracking)

---

### ═══════════════════════════════════════════════════════════════
### 5. LISTA ATTESA AVANZATA
### ═══════════════════════════════════════════════════════════════

#### 5.1 Notifica Automatica Slot Liberato (Fresha, Mindbody)
- **Competitor**: Fresha ("Intelligent Waitlist"), Mindbody (auto-move from waitlist to roster)
- **Cosa fa**: Quando un appuntamento viene cancellato, il sistema:
  1. Cerca chi è in waitlist per quel servizio/operatore/fascia oraria
  2. Invia WhatsApp/SMS: "Si è liberato uno slot per [servizio] [data] [ora]. Vuole confermare?"
  3. First-come-first-served: il primo che conferma prende lo slot
  4. Se nessuno risponde in 2h → notifica il successivo in lista
- **Perché manca in FLUXION**: Waitlist esiste ma è passiva. Il titolare deve controllare manualmente.
- **Implementazione**:
  - Trigger su cancellazione appuntamento → query waitlist per match (servizio, operatore, data, fascia oraria)
  - WhatsApp notifica automatica con link conferma
  - Timer 2h → se no risposta → next in queue
  - Priorità: VIP first, poi per data inserimento waitlist
- **Priorità**: **P1** — feature killer per retention. Fresha la evidenzia come feature premium.
- **Effort**: 3-4 giorni (trigger cancellazione + matching + notifica WA + timer)

#### 5.2 Waitlist per Frequenza Cliente (Mindbody)
- **Competitor**: Mindbody
- **Cosa fa**: Clienti frequenti (≥4 visite/mese) hanno priorità nella waitlist rispetto ai nuovi.
- **Perché manca in FLUXION**: Waitlist ha priorità VIP ma non per frequenza.
- **Implementazione**: Score waitlist = (is_vip * 100) + (visite_ultimo_trimestre * 10) + (giorni_da_ultima_visita * -1)
- **Priorità**: **P2** — nice-to-have
- **Effort**: 1 giorno (query frequenza + score)

---

### ═══════════════════════════════════════════════════════════════
### 6. WALK-IN MANAGEMENT
### ═══════════════════════════════════════════════════════════════

#### 6.1 Gestione Clienti Senza Appuntamento (Waitwhile, Qwaiting, Mindbody)
- **Competitor**: Waitwhile, Qwaiting, Mindbody ("reserve spots for walk-ins")
- **Cosa fa**:
  - Bottone "Walk-in" nel calendario → aggiunge cliente alla coda
  - Stima tempo attesa basata su appuntamenti in corso
  - Slot riservati per walk-in (es: 2 slot/giorno non prenotabili online)
  - Check-in QR code in negozio
- **Perché manca in FLUXION**: Nessun supporto walk-in. Tutto è appointment-based.
- **Implementazione**:
  - `fonte_prenotazione = 'walk_in'` + campo `ordine_arrivo` per coda
  - UI: bottone "Walk-in" nel calendario con form rapido (nome + servizio)
  - Config: N slot riservati per walk-in per operatore/giorno
  - Sara NON gestisce walk-in (è telefonica), ma il calendario sì
- **Priorità**: **P1** — essenziale per saloni e barbieri italiani (molti walk-in)
- **Effort**: 3 giorni (UI calendario + logica coda + config)

---

### ═══════════════════════════════════════════════════════════════
### 7. GROUP BOOKING
### ═══════════════════════════════════════════════════════════════

#### 7.1 Prenotazione Multi-Persona (Fresha, Mindbody, Jane App)
- **Competitor**: Fresha ("multiple clients book together"), Mindbody ("group appointment booking"), Jane App ("group appointments FAQ")
- **Cosa fa**:
  - "Vorrei prenotare per me e mia figlia" → 2 appuntamenti paralleli (2 operatori diversi, stessa ora) o sequenziali (stesso operatore)
  - Conferma unica con dettagli di tutti i partecipanti
  - Split billing possibile
- **Perché manca in FLUXION**: Nessun supporto group booking. FSM gestisce 1 cliente = 1 appuntamento.
- **Implementazione Sara**:
  - Pattern vocali: "per me e [persona]", "siamo in due/tre", "per due persone"
  - `gruppo_booking_id` per raggruppare appuntamenti dello stesso gruppo
  - Sara chiede servizio per ciascun partecipante
  - Cerca slot paralleli (se operatori disponibili) o sequenziali
  - Conferma unica WhatsApp con riepilogo gruppo
- **Priorità**: **P1** — frequente per coppie, madri+figlie, amici
- **Effort**: 4-5 giorni (FSM states + entity extraction + query parallela + WA)

---

### ═══════════════════════════════════════════════════════════════
### 8. CONFERMA MULTICANALE
### ═══════════════════════════════════════════════════════════════

#### 8.1 SMS + Email Conferma/Reminder (Tutti i competitor)
- **Competitor**: TUTTI (Fresha, Mindbody, Jane App, Vagaro, Acuity, Square...)
- **Cosa fa**: Conferma via WhatsApp + SMS + Email. Il cliente sceglie il canale preferito. Reminder su tutti i canali attivi.
- **Perché manca in FLUXION**: Solo WhatsApp (wa.me link). Nessun SMS, nessuna email di conferma.
- **Implementazione**:
  - Email: già abbiamo SMTP settings (migration 017). Aggiungere template email conferma/reminder.
  - SMS: Integrazione gateway SMS italiano (es: Skebby, Messagenet, SMSHosting — ~€0.05/SMS)
  - Preferenza canale in `clienti` (whatsapp, email, sms, tutti)
- **Priorità**: **P1** — non tutti usano WhatsApp. Email è fondamentale per conferme ufficiali.
- **Effort**: 3-4 giorni (template email + SMTP send + preferenza canale + opzionale SMS gateway)

---

### ═══════════════════════════════════════════════════════════════
### 9. SERVIZI CON PREREQUISITI
### ═══════════════════════════════════════════════════════════════

#### 9.1 Prerequisiti Pre-Appuntamento (Jane App, Pabau, IntakeQ)
- **Competitor**: Jane App (intake forms + 24h reminder for incomplete forms), Pabau ("ensure clients complete forms before appointments"), IntakeQ
- **Cosa fa**:
  - Tinta capelli → richiede patch test 48h prima
  - Visita medica → richiede documenti/anamnesi
  - Trattamento estetico → consenso informato
  - Il sistema BLOCCA la prenotazione se il prerequisito non è soddisfatto, oppure invia reminder per completare il prerequisito.
- **Perché manca in FLUXION**: Nessun concetto di prerequisito per servizio.
- **Implementazione**:
  - Tabella `prerequisiti_servizio` (servizio_id, tipo, descrizione, ore_anticipo, obbligatorio)
  - Tipi: `patch_test`, `consenso`, `documenti`, `visita_precedente`, `pausa_minima`
  - Sara: "Per il servizio colore, è necessario il patch test almeno 48 ore prima. L'ha già fatto?"
  - Se no: propone appuntamento patch test prima, poi colore 48h dopo
  - Scheda cliente: tracking prerequisiti completati
- **Priorità**: **P1** — OBBLIGATORIO per verticale cliniche/medici. Differenziante per saloni premium.
- **Effort**: 3-4 giorni (DB + FSM logic + UI gestione prerequisiti)

#### 9.2 Intake Form Pre-Appuntamento (Jane App, Acuity)
- **Competitor**: Jane App, Acuity (intake forms as part of booking flow)
- **Cosa fa**: Link a form online inviato dopo booking, deve essere compilato prima dell'appuntamento. Reminder 24h se non compilato.
- **Perché manca in FLUXION**: Nessun form pre-appuntamento.
- **Implementazione**: WhatsApp post-booking con link a form web (o in-app nella scheda cliente). Questo è più un'estensione UI che voice.
- **Priorità**: **P2** — utile per cliniche, meno per saloni
- **Effort**: 4-5 giorni (form builder + link + tracking completamento)

---

### ═══════════════════════════════════════════════════════════════
### 10. FEATURES AGGIUNTIVE WORLD-CLASS 2026
### ═══════════════════════════════════════════════════════════════

#### 10.1 Conferma Appuntamento Attiva — "Conferma o Cancella" (Tutti)
- **Competitor**: Tutti i competitor premium 2026
- **Cosa fa**: 24h prima, invece di solo reminder, chiede CONFERMA attiva: "Confermi il tuo appuntamento domani alle 15? Rispondi SI o NO". Se NO o nessuna risposta → libera lo slot per waitlist.
- **Perché manca in FLUXION**: Reminder è one-way (solo notifica). Non c'è conferma attiva.
- **Implementazione**: WhatsApp message con risposta attesa. Se "no" → cancella + notifica waitlist. Se timeout 6h → warning al titolare.
- **Priorità**: **P1** — riduce no-show e libera slot per waitlist
- **Effort**: 2-3 giorni (logica conferma + trigger cancellazione + waitlist notify)

#### 10.2 Smart Rebooking — "Vuole fissare il prossimo?" (Fresha, Vagaro)
- **Competitor**: Fresha, Vagaro, tutti i salon software
- **Cosa fa**: Dopo il completamento di un appuntamento, propone immediatamente il prossimo: "Il prossimo taglio tra 4 settimane? Martedì 15 aprile alle 10?"
- **Perché manca in FLUXION**: Nessun rebooking automatico.
- **Implementazione Sara**: Dopo COMPLETED, se il servizio ha `frequenza_suggerita` (es: 4 settimane per taglio), propone il prossimo slot nella stessa fascia oraria.
- **Priorità**: **P1** — aumenta retention drammaticamente
- **Effort**: 2 giorni (campo frequenza_suggerita + logica post-booking)

#### 10.3 Capacity/Resource Management (Mindbody, Jane App)
- **Competitor**: Mindbody, Jane App
- **Cosa fa**: Gestione stanze/postazioni/attrezzature. Es: solo 2 caschi per tinta → max 2 tinte contemporanee anche se ci sono 4 operatori.
- **Perché manca in FLUXION**: Nessun concetto di risorsa condivisa.
- **Implementazione**: Tabella `risorse` (id, nome, tipo, quantità) + `servizi_risorse` (servizio_id, risorsa_id). Query disponibilità controlla sia operatore che risorse.
- **Priorità**: **P2** — nice-to-have per saloni grandi
- **Effort**: 3-4 giorni (DB + logica disponibilità + UI)

#### 10.4 Check-in Digitale (Mindbody, Waitwhile)
- **Competitor**: Mindbody, Waitwhile, Qwaiting
- **Cosa fa**: Cliente arriva → check-in via QR code, tablet, o app → operatore vede "cliente arrivato" nel calendario.
- **Perché manca in FLUXION**: Nessun check-in. Lo stato passa da `confermato` a `completato` manualmente.
- **Implementazione**: Stato intermedio `arrivato` + bottone check-in nel calendario + opzionale QR.
- **Priorità**: **P2** — nice-to-have
- **Effort**: 1-2 giorni (stato + bottone UI)

---

## RIEPILOGO PRIORITA'

### P0 — BLOCKER VENDITA (da fare PRIMA del lancio)
| # | Feature | Effort | Impatto |
|---|---------|--------|---------|
| 1.2 | Buffer automatico tra servizi (Sara usa `buffer_minuti`) | 1 gg | Evita sovrapposizioni |
| 1.3 | Pausa pranzo / blocco fasce orarie operatore | 2 gg | Sara non prenota durante pausa |
| 1.4 | Multi-servizio combo (durata sommata, slot unico) | 3-4 gg | "Taglio e piega" funziona |
| 3.2 | "Il solito" — servizio abituale da storia | 2-3 gg | Feature WOW differenziante |
| **TOT** | | **8-10 gg** | |

### P1 — DIFFERENZIANTI (Sprint 1 post-lancio)
| # | Feature | Effort | Impatto |
|---|---------|--------|---------|
| 1.1 | Smart gap elimination | 2-3 gg | Ottimizza calendario |
| 2.1 | Appuntamenti ricorrenti vocali | 4-5 gg | Saloni, fisioterapisti |
| 3.1 | Operatore preferito memorizzato | 2 gg | Personalizzazione |
| 4.1 | No-show tracking + penalità | 3 gg | -40% no-show |
| 5.1 | Waitlist notifica automatica | 3-4 gg | Slot liberati riempiti |
| 6.1 | Walk-in management | 3 gg | Essenziale barbieri |
| 7.1 | Group booking (2+ persone) | 4-5 gg | Coppie, famiglie |
| 8.1 | Email conferma/reminder | 3-4 gg | Non tutti usano WA |
| 9.1 | Prerequisiti servizio | 3-4 gg | Obbligatorio cliniche |
| 10.1 | Conferma attiva 24h | 2-3 gg | Riduce no-show |
| 10.2 | Smart rebooking post-appuntamento | 2 gg | Retention |
| **TOT** | | **32-38 gg** | |

### P2 — NICE-TO-HAVE (v1.1+)
| # | Feature | Effort | Impatto |
|---|---------|--------|---------|
| 3.3 | Suggerimento servizi correlati (upsell) | 2-3 gg | Revenue |
| 4.2 | Deposito/prepagamento | 5+ gg | Anti no-show premium |
| 5.2 | Waitlist priorità per frequenza | 1 gg | Fidelizzazione |
| 9.2 | Intake form pre-appuntamento | 4-5 gg | Cliniche |
| 10.3 | Capacity/resource management | 3-4 gg | Saloni grandi |
| 10.4 | Check-in digitale | 1-2 gg | UX in-store |
| **TOT** | | **16-20 gg** | |

---

## GOLD STANDARD 2026 — COME SUPERARE I COMPETITOR

### Cosa FA NESSUN competitor (opportunità FLUXION):
1. **Voice-first booking con "il solito"** — nessun competitor vocale riconosce "il solito" in italiano con contesto storico. Questo è il nostro differenziante.
2. **Waitlist attiva via WhatsApp** — Fresha usa email/SMS. In Italia WhatsApp ha penetrazione 95%. La notifica waitlist via WA è superiore.
3. **Voice + Calendar unificati** — Fresha/Mindbody separano il booking vocale (AI receptionist) dal calendario. FLUXION li integra nativamente.
4. **Zero costi ricorrenti per il titolare** — tutti i competitor hanno fee mensili €30-200+. FLUXION lifetime è unico.

### Benchmark latenza (voice agent booking 2026):
- Retell AI: ~600ms response
- Vapi: 500-800ms response
- FLUXION Sara attuale: ~1330ms → target <800ms (da F03 Latency Optimizer)

---

## RACCOMANDAZIONE SPRINT IMMEDIATO

**Sprint P0 (8-10 giorni)**: Feature #1.2 + #1.3 + #1.4 + #3.2
Queste 4 feature sono BLOCKER perché:
- Senza buffer, Sara sovrappone appuntamenti → cliente arrabbiato
- Senza pausa pranzo, Sara prenota durante il pranzo → titolare arrabbiato
- Senza multi-servizio, "taglio e piega" non funziona → il 60% delle richieste salone fallisce
- Senza "il solito", Sara chiede TUTTO ogni volta → cliente abituale si scoccia

**Sprint P1-A (15 giorni)**: Feature #3.1 + #4.1 + #5.1 + #10.1 + #10.2
Queste completano il ciclo di vita del booking (preferenze → prenotazione → conferma → no-show → rebooking).

**Sprint P1-B (17 giorni)**: Feature #1.1 + #2.1 + #6.1 + #7.1 + #8.1 + #9.1
Queste estendono le capabilities per tutti i verticali.

---

## FONTI

- [Fresha Scheduling Features](https://www.fresha.com/for-business/features/scheduling)
- [Fresha Intelligent Time Slots](https://www.fresha.com/help-center/knowledge-base/calendar/496-optimize-online-schedule-availability)
- [Fresha Buffer/Processing Time](https://www.fresha.com/help-center/knowledge-base/catalog/578-add-extra-time-to-services-and-appointments-1)
- [Fresha 2026 New Features](https://www.fresha.com/blog/Up-Next-2026)
- [Mindbody Scheduling](https://www.mindbodyonline.com/business/scheduling)
- [Mindbody Waitlists](https://support.mindbodyonline.com/s/article/203253503-Waitlists)
- [Mindbody Buffer Time](https://support.mindbodyonline.com/s/article/203269783-How-can-I-add-a-buffer-time-between-Appointments)
- [Jane App Features](https://jane.app/features)
- [Jane App Online Booking](https://jane.app/features/online-booking)
- [Jane App Group Appointments](https://jane.app/guide/groups-and-group-appointments-faq)
- [Acuity Recurring Appointments](https://help.acuityscheduling.com/hc/en-us/articles/16676870087565-Offering-recurring-appointments-in-Acuity-Scheduling)
- [Acuity Intake Forms](https://help.acuityscheduling.com/hc/en-us/articles/16676931038093-Client-intake-forms-and-agreements-in-Acuity-Scheduling)
- [Square No-Show Prepayments](https://squareup.com/us/en/the-bottom-line/selling-anywhere/reduce-no-show-appointments-with-our-new-client-prepayments-feature)
- [Retell AI Appointment Booking](https://www.retellai.com/features/book-appointments)
- [Waitwhile Queue Management](https://waitwhile.com/)
- [Appointment Deposit Guide 2026](https://schedulingkit.com/guides/appointment-deposit-guide)
- [Vagaro Features 2026](https://www.getapp.com/retail-consumer-services-software/a/vagaro/)
- [Pabau Medical Forms](https://pabau.com/blog/medical-forms-at-your-healthcare-practice/)
- [BookingBee AI Salon Receptionist](https://bookingbee.ai/10-best-ai-receptionist-for-salons-in-2025/)
- [Meevo Salon AI 2026](https://www.meevo.com/blog/salon-ai-experiences/)
