## Stress verticali — certificazione contenuto Sara

**Run:** stress-verticali:20260731T171055:93741:ba766ed7
**Inizio:** 2026-07-31T17:10:55.249+02:00
**Durata:** 155.8s / budget 1140s
**Endpoint:** http://127.0.0.1:3002
**Health:** HTTP 200 · ok
**VoIP produzione (solo lettura):** HTTP 200 · registered=True
**Cleanup DB:** OK: rimosse 6 fixture e relativi dati
**Verticale ripristinato:** OK: salone ripristinato

| Verticale | Esito | KB | Risposte | Booking | FAQ | Guardrail | Catalogo | Argomentazioni | Latenza | AVG ms | P95 ms | MAX ms | Turni | Durata s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Parrucchiere / Barbiere | FAIL | WARN | OK | FAIL | OK | WARN | WARN | FAIL | OK | 1064 | 1820 | 1820 | 12 | 14.1 |
| Officina Auto | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | OK | OK | 1241 | 2553 | 2553 | 12 | 18.5 |
| Studio Odontoiatrico | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | OK | OK | 1073 | 2042 | 2042 | 12 | 14.2 |
| Studio di Fisioterapia | FAIL | FAIL | FAIL | FAIL | WARN | WARN | FAIL | WARN | FAIL | 2362 | 9501 | 9501 | 13 | 32.0 |
| Palestra / Centro Fitness | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | OK | FAIL | 2969 | 10190 | 10190 | 12 | 39.8 |
| Centro Estetico | FAIL | WARN | OK | FAIL | WARN | WARN | WARN | OK | FAIL | 2765 | 10630 | 10630 | 12 | 37.0 |

### FAIL

#### Parrucchiere / Barbiere — BOOKING — BOOKING Taglio uomo
- Timestamp: 2026-07-31T17:10:59.790+02:00
- Motivo: booking_action=booking_created non osservata
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Che bello! Ok. Per quale giorno ti andrebbe?
    FSM: waiting_date
    LAYER: L2_slot
    LATENCY_MS: 1003.2
    ERROR: ND

#### Parrucchiere / Barbiere — ARGOMENTAZIONI — ARGOMENTAZIONE settoriale
- Timestamp: 2026-07-31T17:11:09.370+02:00
- Motivo: contenuto non pertinente o vuoto
- Evidenza verbatim:
    USER: Perché conviene fare una consulenza prima del colore?
    SARA: Il taglio donna presso Salone Demo FLUXION costa 25 euro e dura circa 45 minuti. È incluso shampoo e asciugatura professionale. Vuole prenotare subito?
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 271.0
    ERROR: ND

#### Officina Auto — BOOKING — BOOKING Tagliando
- Timestamp: 2026-07-31T17:11:14.336+02:00
- Motivo: booking_action=booking_created non osservata
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Che bello! Ok. Per quale giorno ti andrebbe?
    FSM: waiting_date
    LAYER: L2_slot
    LATENCY_MS: 287.2
    ERROR: ND

#### Officina Auto — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T17:11:23.134+02:00
- Motivo: nessun servizio DB riconosciuto (auto.db)
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Potete prenotare: 1) Telefonando al 06 9112233, 2) Via email: info@gommeexpress.it, 3) Di persona. Vi consiglio di prenotare almeno 2-3 giorni prima, soprattutto per interventi complessi.
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 1824.7
    ERROR: ND

#### Studio Odontoiatrico — BOOKING — BOOKING Visita odontoiatrica
- Timestamp: 2026-07-31T17:11:31.430+02:00
- Motivo: booking_action=booking_created non osservata
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Che bello! Perfetto. Per quale giorno ti andrebbe?
    FSM: waiting_date
    LAYER: L2_slot
    LATENCY_MS: 1120.1
    ERROR: ND

#### Studio Odontoiatrico — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T17:11:37.563+02:00
- Motivo: servizio booking 'Visita odontoiatrica' assente da odontoiatra.db
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND

#### Studio di Fisioterapia — BOOKING — BOOKING Seduta fisioterapia
- Timestamp: 2026-07-31T17:11:49.946+02:00
- Motivo: booking_action=booking_created non osservata
- Evidenza verbatim:
    USER: Alle dieci
    SARA: Fantastico! Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?
    FSM: completed
    LAYER: L1_exact
    LATENCY_MS: 1408.6
    ERROR: ND

#### Studio di Fisioterapia — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T17:11:56.343+02:00
- Motivo: domanda catalogo deviata nel booking
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Come ti chiami?
    FSM: waiting_name
    LAYER: L2_slot
    LATENCY_MS: 26.5
    ERROR: ND

#### Studio di Fisioterapia — RISPOSTE — RISPOSTA identità e ambito
- Timestamp: 2026-07-31T17:12:04.450+02:00
- Motivo: risposta contaminata da altro verticale
- Evidenza verbatim:
    USER: Chi siete e di quali servizi vi occupate?
    SARA: Siamo l'Officina Demo FLUXION, un centro di riabilitazione e benessere dove ti aiutiamo a ritrovare la tua forma fisica e mentale ottimale. Noi ci occupiamo di servizi come la fisioterapia, la massoter apia, la terapia manuale, l'elettroterapia, gli ultrasuoni e la riabilitazione post-operatoria. Siamo qui per aiutarti a sentirti meglio e a raggiungere i tuoi obiettivi!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 7944.4
    ERROR: ND

#### Studio di Fisioterapia — LATENZA — LATENZA
- Timestamp: 2026-07-31T17:12:14.118+02:00
- Motivo: 2/13 turni sopra 5000ms
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND

#### Palestra / Centro Fitness — BOOKING — BOOKING Lezione pilates
- Timestamp: 2026-07-31T17:12:19.488+02:00
- Motivo: booking_action=booking_created non osservata
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Che bello! Ok. Per quale giorno ti andrebbe?
    FSM: waiting_date
    LAYER: L2_slot
    LATENCY_MS: 244.5
    ERROR: ND

#### Palestra / Centro Fitness — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T17:12:38.209+02:00
- Motivo: nessun servizio DB riconosciuto (palestra.db)
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Potete prenotare: 1) Tramite la nostra app, 2) Alla reception, 3) Chiamando il 06 9112233. La prenotazione e obbligatoria per corsi come spinning. Cancellazione gratuita fino a 2 ore prima.
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 2711.8
    ERROR: ND

#### Palestra / Centro Fitness — LATENZA — LATENZA
- Timestamp: 2026-07-31T17:12:53.899+02:00
- Motivo: 3/12 turni sopra 5000ms
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND

#### Centro Estetico — BOOKING — BOOKING Pulizia del viso
- Timestamp: 2026-07-31T17:12:59.966+02:00
- Motivo: booking_action=booking_created non osservata
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Che bello! Capito. Per quale giorno ti andrebbe?
    FSM: waiting_date
    LAYER: L2_slot
    LATENCY_MS: 1506.5
    ERROR: ND

#### Centro Estetico — LATENZA — LATENZA
- Timestamp: 2026-07-31T17:13:30.913+02:00
- Motivo: 2/12 turni sopra 5000ms
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND


**Verticale PIÙ PRONTO:** Parrucchiere / Barbiere — minor numero di FAIL e, a parità, P95 migliore.
