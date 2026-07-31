## Stress verticali v2 — certificazione contenuto Sara

**Run ID:** stress-v2:20260731T201106:19113:b37fb379
**Commit:** 4ce8b5e3
**Inizio:** 2026-07-31T20:11:06.005+02:00
**Durata:** 135.1s / budget 1140s
**Endpoint:** http://127.0.0.1:3002
**Health:** HTTP 200 · ok
**VoIP:** HTTP 200 · registered=True · reg_status=200
**Preflight:** OK

### Preflight notes

- 1. commit HEAD: 4ce8b5e3
- 2. processo :3002: UP
- 3. /health: HTTP 200 status=ok
- 4. /api/voice/voip/status: HTTP 200
- 5. SIP registered: True
- 6. reg_status: 200
- 7. linea occupata: False
- 8. verticale corrente: ?
- 9. asset E2E: /Volumes/MacSSD - Dati/FLUXION/voice-agent/tests/e2e/test_sara_stress_per_verticale.py — PRESENTE
- 10. DB verticali trovati: ['salone', 'auto', 'odontoiatra', 'fisioterapia', 'palestra', 'beauty']
- 11. DB clienti: /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db
- 12. sintassi script: OK (importato correttamente)

**Cleanup DB:** OK: rimosse 6 fixture e relativi dati
**Verticale ripristinato:** OK: salone ripristinato

| Verticale | Esito | KB | Risposte | Booking | FAQ | Guardrail | Catalogo | Argomentazioni | Latenza | AVG ms | P95 ms | MAX ms | Turni | Durata s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Parrucchiere / Barbiere | FAIL | WARN | OK | FAIL | OK | WARN | WARN | FAIL | OK | 357 | 1227 | 1227 | 12 | 5.5 |
| Officina Auto | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | FAIL | OK | 949 | 2332 | 2332 | 16 | 16.6 |
| Studio Odontoiatrico | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | OK | OK | 882 | 2348 | 2348 | 19 | 18.6 |
| Studio di Fisioterapia | FAIL | FAIL | FAIL | FAIL | WARN | WARN | FAIL | OK | WARN | 1353 | 6844 | 6844 | 11 | 16.2 |
| Palestra / Centro Fitness | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | OK | FAIL | 2032 | 9512 | 10845 | 20 | 42.1 |
| Centro Estetico | FAIL | FAIL | OK | FAIL | WARN | WARN | FAIL | OK | WARN | 1570 | 4201 | 11180 | 22 | 35.8 |

**FAIL_SARA totali:** 15
**FAIL_DRIVER totali:** 0
**WARN totali:** 19

### FAIL — dettaglio

#### [FAIL_SARA] Parrucchiere / Barbiere — BOOKING — BOOKING Taglio uomo
- Timestamp: 2026-07-31T20:11:08.754+02:00
- Motivo: loop FSM: stato 'waiting_date' ripetuto 4x
- Evidenza verbatim:
    USER: martedì 8 settembre 2026
    SARA: Ok. Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?
    FSM: waiting_date
    LAYER: L1_exact
    LATENCY_MS: 256.7
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_date', 'client': {'id': 'cea581ff78907fc156540a9f5123ae4c', 'name': 'Marco', 'phone': '3895521466', 'email': None}, 'booking': {'service': 'taglio_uomo', 'service_display': 'Taglio uomo', 'date': None, 'date_display': None, 'time': None, 'time_display': None, 'operator': None}, 'turns': 2}}
    ERROR: ND

#### [WARN] Parrucchiere / Barbiere — GUARDRAIL — GUARDRAIL fuori competenza
- Timestamp: 2026-07-31T20:11:10.168+02:00
- Motivo: rifiuto non esplicito, ma booking non avviato
- Evidenza verbatim:
    USER: Vorrei il cambio olio
    SARA: Mi occupo di prenotazioni per il salone. Posso aiutarla con taglio, colore, trattamenti o altri servizi capelli?
    FSM: idle
    LAYER: L0_special
    LATENCY_MS: 7.4
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Parrucchiere / Barbiere — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T20:11:10.637+02:00
- Motivo: catalogo parziale: 1/8 servizio
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Il taglio donna presso Salone Demo FLUXION costa 25 euro e dura circa 45 minuti. È incluso shampoo e asciugatura professionale. Vuole prenotare subito?
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 312.3
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Parrucchiere / Barbiere — ARGOMENTAZIONI — ARGOMENTAZIONE settoriale
- Timestamp: 2026-07-31T20:11:11.602+02:00
- Motivo: contenuto non pertinente o vuoto
- Evidenza verbatim:
    USER: Perché conviene fare una consulenza prima del colore?
    SARA: Il taglio donna presso Salone Demo FLUXION costa 25 euro e dura circa 45 minuti. È incluso shampoo e asciugatura professionale. Vuole prenotare subito?
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 224.1
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Officina Auto — BOOKING — BOOKING Tagliando
- Timestamp: 2026-07-31T20:11:20.205+02:00
- Motivo: loop FSM: stato 'waiting_date' ripetuto 4x
- Evidenza verbatim:
    USER: mercoledì 9 settembre 2026
    SARA: Perfetto. Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?
    FSM: waiting_date
    LAYER: L1_exact
    LATENCY_MS: 1634.6
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_date', 'client': {'id': '78bf7eac6e5e3da5cdb730ce7321f0c6', 'name': 'Giulia', 'phone': '3895521467', 'email': None}, 'booking': {'service': 'tagliando', 'service_display': 'Tagliando', 'date': '2093-06-11', 'date_display': 'giovedì 11 giugno', 'time': None, 'time_display': None, 'operator': None}, 'turns': 6}}
    ERROR: ND

#### [WARN] Officina Auto — FAQ — FAQ-1
- Timestamp: 2026-07-31T20:11:21.258+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Quanto costa il tagliando?
    SARA: Il tagliando costa 120 euro e richiede circa 60 minuti.
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 761.8
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Officina Auto — FAQ — FAQ-2
- Timestamp: 2026-07-31T20:11:23.296+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Fate il ritiro a domicilio?
    SARA: Sì, certo! Da noi off riamo il servizio di ritiro a domicilio per i nostri clienti. I nostri tecnici si recheranno direttamente alla sua abitazione per effettuare le rip arazioni o le manutenzioni richieste. Perfetto, segno! Ti aspettiamo!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1876.7
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Officina Auto — FAQ — FAQ-3
- Timestamp: 2026-07-31T20:11:24.770+02:00
- Motivo: risposta presente ma keyword attese non trovate
- Evidenza verbatim:
    USER: Che orari avete?
    SARA: Lun-Sab 09:00-19:00. Ti aspettiamo!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1304.1
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Officina Auto — GUARDRAIL — GUARDRAIL fuori competenza
- Timestamp: 2026-07-31T20:11:24.937+02:00
- Motivo: rifiuto non esplicito, ma booking non avviato
- Evidenza verbatim:
    USER: Vorrei un taglio di capelli
    SARA: Mi occupo di prenotazioni per l'officina. Posso aiutarla con tagliando, riparazioni, cambio gomme o altri servizi auto?
    FSM: idle
    LAYER: L0_special
    LATENCY_MS: 9.2
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Officina Auto — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T20:11:25.422+02:00
- Motivo: nessun servizio DB riconosciuto (auto.db)
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Potete prenotare: 1) Telefonando al 06 9112233, 2) Via email: info@gommeexpress.it, 3) Di persona. Vi consiglio di prenotare almeno 2-3 giorni prima, soprattutto per interventi complessi.
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 321.5
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Officina Auto — ARGOMENTAZIONI — ARGOMENTAZIONE settoriale
- Timestamp: 2026-07-31T20:11:28.206+02:00
- Motivo: domanda informativa deviata nel booking
- Evidenza verbatim:
    USER: Perché è importante fare il tagliando regolarmente?
    SARA: Come ti chiami?
    FSM: waiting_name
    LAYER: L2_slot
    LATENCY_MS: 123.0
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_name', 'client': None, 'booking': {'service': 'tagliando', 'service_display': 'Tagliando', 'date': None, 'date_display': None, 'time': None, 'time_display': None, 'operator': None}, 'turns': 1}}
    ERROR: ND

#### [FAIL_SARA] Studio Odontoiatrico — BOOKING — BOOKING Visita odontoiatrica
- Timestamp: 2026-07-31T20:11:38.263+02:00
- Motivo: FSM=completed ma booking_action.action='booking_in_progress' (atteso booking_created). Sara completa il booking ma non emette l'action corretta.
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Perfetto, prenotazione confermata! Le invieremo la conferma via WhatsApp. Tutto confermato! A giovedì 11 giugno da Officina Demo FLUXION, buona giornata!
    SARA: Specialità: odontoiatria A proposito, abbiamo il pacchetto Abbonamento VIP Mensile: 4 sedute a 120 euro invece di 160. Le interessa?
    FSM: completed
    LAYER: L2_slot
    LATENCY_MS: 588.7
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'completed', 'client': {'id': '8b2a84fe3f270a9b5b41a2591d21fa77', 'name': 'Luca', 'phone': '3895521468', 'email': None}, 'booking': {'service': 'odontoiatria', 'service_display': 'Odontoiatria', 'date': '2093-06-11', 'date_display': 'giovedì 11 giugno', 'time': '10:00', 'time_display': 'alle 10:00', 'operator': None}, 'turns': 9}}
    ERROR: ND

#### [WARN] Studio Odontoiatrico — FAQ — FAQ-2
- Timestamp: 2026-07-31T20:11:40.449+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Gestite le urgenze dentali?
    SARA: Ci mancherebbe! Da noi, siamo sempre pronti ad affrontare le situazioni di emerg enza. Se hai un problema dentale urgente, ti consiglio di chiamare il nostro numero di emergenza. Ti passerò il numero del nostro direttore sanitario, Mario Rossi , che sarà felice di aiutarti. Ti aspettiamo!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1704.0
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Studio Odontoiatrico — FAQ — FAQ-3
- Timestamp: 2026-07-31T20:11:43.210+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Fate anche igiene dentale o pulizia dei denti?
    SARA: Ci mancherebbe! Da noi offriamo anche igiene dentale e pulizia dei denti. La nostra igienista dentale, Anna Bianchi, è esperta in preven zione e può aiutarti a mantenere una buona salute orale. La pulizia dei denti è un servizio fondamentale per pre venire la formazione di tartaro e placca, e può essere effettuata in combinazione con una visita di controllo o come servizio a sé. Ti consiglio di chiedere a Anna di spiegarti meglio i dettag li e le opzioni dispon ibili.
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 2347.8
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': {'service': 'odontoiatria', 'service_display': 'Odontoiatria', 'date': None, 'date_display': None, 'time': None, 'time_display': None, 'operator': None}, 'turns': 0}}
    ERROR: ND

#### [WARN] Studio Odontoiatrico — GUARDRAIL — GUARDRAIL fuori competenza
- Timestamp: 2026-07-31T20:11:43.429+02:00
- Motivo: rifiuto non esplicito, ma booking non avviato
- Evidenza verbatim:
    USER: Vorrei un taglio di capelli
    SARA: Mi occupo di prenotazioni per lo studio dentistico. Posso aiutarla con visite, pulizia denti, otturazioni o sbiancamento?
    FSM: idle
    LAYER: L0_special
    LATENCY_MS: 13.8
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Studio Odontoiatrico — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T20:11:43.432+02:00
- Motivo: servizio booking 'Visita odontoiatrica' assente da odontoiatra.db
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND

#### [FAIL_SARA] Studio di Fisioterapia — BOOKING — BOOKING Seduta fisioterapia
- Timestamp: 2026-07-31T20:11:51.369+02:00
- Motivo: FSM=completed ma booking_action.action='booking_in_progress' (atteso booking_created). Sara completa il booking ma non emette l'action corretta.
- Evidenza verbatim:
    USER: Sì, confermo
    SARA: Che bello! Perfetto, prenotazione confermata! Le invieremo la conferma via WhatsApp. Perfetto, ci vediamo venerdì 7 agosto! A presto da Officina Demo FLUXION!
    SARA: Specialità: fisioterapia A proposito, abbiamo il pacchetto Abbonamento VIP Mensile: 4 sedute a 120 euro invece di 160. Le interessa?
    FSM: completed
    LAYER: L2_slot
    LATENCY_MS: 2875.2
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'completed', 'client': {'id': '7d69749546180e2fbcc573541d5229bf', 'name': 'Elena', 'phone': '3895521469', 'email': None}, 'booking': {'service': 'fisioterapia', 'service_display': 'Fisioterapia', 'date': '2026-08-07', 'date_display': 'venerdì 7 agosto', 'time': '08:30', 'time_display': 'alle 08:30', 'operator': None}, 'turns': 4}}
    ERROR: ND

#### [WARN] Studio di Fisioterapia — FAQ — FAQ-2
- Timestamp: 2026-07-31T20:11:53.536+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Quanto dura una seduta?
    SARA: Una seduta fisioterapia dura quarantacinque minuti.
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1630.6
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Studio di Fisioterapia — GUARDRAIL — GUARDRAIL fuori competenza
- Timestamp: 2026-07-31T20:11:54.143+02:00
- Motivo: rifiuto non esplicito, ma booking non avviato
- Evidenza verbatim:
    USER: Cambio gomme per favore
    SARA: Mi occupo di prenotazioni per lo studio di fisioterapia. Posso aiutarla con sedute, riabilitazione o terapie?
    FSM: idle
    LAYER: L0_special
    LATENCY_MS: 8.6
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Studio di Fisioterapia — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T20:11:54.385+02:00
- Motivo: domanda catalogo deviata nel booking
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Come ti chiami?
    FSM: waiting_name
    LAYER: L2_slot
    LATENCY_MS: 81.0
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_name', 'client': None, 'booking': None, 'turns': 1}}
    ERROR: ND

#### [FAIL_SARA] Studio di Fisioterapia — RISPOSTE — RISPOSTA identità e ambito
- Timestamp: 2026-07-31T20:11:56.000+02:00
- Motivo: risposta contaminata da altro verticale
- Evidenza verbatim:
    USER: Chi siete e di quali servizi vi occupate?
    SARA: Siamo Officina Demo FLUXION, un centro di riabilitazione e benessere dove ti aiutiamo a ritrovare la tua forma fisica e mentale. Noi offriamo una vasta gamma di servizi, tra cui fisioterapia, massoterapia , terapia manuale, elettroterapia, ultrasuoni e riabilitazione post-operatoria. Siamo qui per aiutarti a superare le difficoltà e a raggiungere i tuoi obiettivi di salute e benessere. Ti aspett iamo!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1459.4
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Studio di Fisioterapia — LATENZA — LATENZA
- Timestamp: 2026-07-31T20:12:03.005+02:00
- Motivo: 1 turno sopra 5000ms
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND

#### [FAIL_SARA] Palestra / Centro Fitness — BOOKING — BOOKING Lezione pilates
- Timestamp: 2026-07-31T20:12:19.448+02:00
- Motivo: loop FSM: stato 'waiting_time' ripetuto 4x
- Evidenza verbatim:
    USER: Alle 10:00
    SARA: Benissimo! Il pacchetto Abbonamento VIP Mensile include 4 sedute a 120 euro invece di 160. Le interessa? Mi dica sì o no.
    FSM: waiting_time
    LAYER: L2_slot
    LATENCY_MS: 1225.7
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_time', 'client': {'id': 'b3bc71da97357b653a173776bcbae117', 'name': 'Paolo', 'phone': '3895521470', 'email': None}, 'booking': {'service': 'lezione_pilates', 'service_display': 'Lezione pilates', 'date': '2093-06-11', 'date_display': 'giovedì 11 giugno', 'time': None, 'time_display': None, 'operator': None}, 'turns': 9}}
    ERROR: ND

#### [WARN] Palestra / Centro Fitness — FAQ — FAQ-1
- Timestamp: 2026-07-31T20:12:20.478+02:00
- Motivo: risposta presente ma keyword attese non trovate
- Evidenza verbatim:
    USER: Quanto costa l'abbonamento mensile?
    SARA: Ecco i nostri servizi con i prezzi:
    SARA: - Lezione pilates: €15 (60min)
    SARA: - Lezione yoga: €15 (60min)
    SARA: - Personal training: €40 (60min)
    SARA: - Lezione spinning: €12 (45min)
    SARA: - Lezione zumba: €10 (45min)
    SARA: - Valutazione fisica: €30 (45min)
    SARA: - Massaggio sportivo: €50 (60min)
    SARA: - Lezione crossfit: €15 (60min)
    SARA: Quale ti interessa?
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 851.1
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Palestra / Centro Fitness — FAQ — FAQ-3
- Timestamp: 2026-07-31T20:12:23.621+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Che orari avete?
    SARA: Ecco, da noi Palestra Demo FLUXION, siamo aperti dal lunedì al sabato dalle 9:00 alle 19:00. Perfetto, ad esso sai quando poter venire a allenarti con noi! Ti aspettiamo!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 2610.8
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Palestra / Centro Fitness — GUARDRAIL — GUARDRAIL fuori competenza
- Timestamp: 2026-07-31T20:12:23.788+02:00
- Motivo: rifiuto non esplicito, ma booking non avviato
- Evidenza verbatim:
    USER: Vorrei un taglio di capelli
    SARA: Mi occupo di prenotazioni per la palestra. Posso aiutarla con corsi, abbonamenti o sessioni di personal training?
    FSM: idle
    LAYER: L0_special
    LATENCY_MS: 9.0
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Palestra / Centro Fitness — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T20:12:24.455+02:00
- Motivo: nessun servizio DB riconosciuto (palestra.db)
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Potete prenotare: 1) Tramite la nostra app, 2) Alla reception, 3) Chiamando il 06 9112233. La prenotazione e obbligatoria per corsi come spinning. Cancellazione gratuita fino a 2 ore prima.
    FSM: idle
    LAYER: L3_faq
    LATENCY_MS: 509.5
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Palestra / Centro Fitness — LATENZA — LATENZA
- Timestamp: 2026-07-31T20:12:45.143+02:00
- Motivo: 2/20 turni sopra 5000ms
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND

#### [FAIL_SARA] Centro Estetico — BOOKING — BOOKING Pulizia del viso
- Timestamp: 2026-07-31T20:13:02.730+02:00
- Motivo: loop FSM: stato 'waiting_time' ripetuto 4x
- Evidenza verbatim:
    USER: Alle 10:00
    SARA: Benissimo! Capito. Il pacchetto Abbonamento VIP Mensile include 4 sedute a 120 euro invece di 160. Le interessa? Mi dica sì o no.
    FSM: waiting_time
    LAYER: L2_slot
    LATENCY_MS: 1139.0
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_time', 'client': {'id': '3d765d2fed91dc1538684ea2d2b01f87', 'name': 'Sara', 'phone': '3895521471', 'email': None}, 'booking': {'service': 'pulizia_viso', 'service_display': 'Pulizia viso', 'date': '2093-06-11', 'date_display': 'giovedì 11 giugno', 'time': None, 'time_display': None, 'operator': None}, 'turns': 9}}
    ERROR: ND

#### [WARN] Centro Estetico — FAQ — FAQ-2
- Timestamp: 2026-07-31T20:13:04.238+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Che orari avete?
    SARA: Da noi, gli orari di apertura sono Lunedì-Sabato dalle 09: 00 alle 19:00. Ti aspettiamo!
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1116.7
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Centro Estetico — FAQ — FAQ-3
- Timestamp: 2026-07-31T20:13:05.630+02:00
- Motivo: pertinente ma layer=L4_groq; KB non certificata
- Evidenza verbatim:
    USER: Fate anche massaggi?
    SARA: Sì, ci facciamo anche massaggi! Noi offriamo massaggi rilassanti con Sara Marchetti, nostra massaggiatrice certificata, esperta in tecniche orientali. È un'opzione molto popolare tra i nostri clienti, e ti aiuterà a rilassarti e a sentirsi rigenerato. Vuoi prenotare un appuntamento?
    FSM: idle
    LAYER: L4_groq
    LATENCY_MS: 1225.2
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [WARN] Centro Estetico — GUARDRAIL — GUARDRAIL fuori competenza
- Timestamp: 2026-07-31T20:13:05.797+02:00
- Motivo: rifiuto non esplicito, ma booking non avviato
- Evidenza verbatim:
    USER: Vorrei il cambio olio
    SARA: Mi occupo di prenotazioni per il centro estetico. Posso aiutarla con trattamenti viso, massaggi, nail art, epilazione o spa?
    FSM: idle
    LAYER: L0_special
    LATENCY_MS: 9.3
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'idle', 'client': None, 'booking': None, 'turns': 0}}
    ERROR: ND

#### [FAIL_SARA] Centro Estetico — CATALOGO — CATALOGO servizi vs knowledge base
- Timestamp: 2026-07-31T20:13:05.995+02:00
- Motivo: domanda catalogo deviata nel booking
- Evidenza verbatim:
    USER: Quali servizi posso prenotare con voi? Elencami i principali.
    SARA: Come ti chiami?
    FSM: waiting_name
    LAYER: L2_slot
    LATENCY_MS: 38.5
    BOOKING_ACTION: {'action': 'booking_in_progress', 'context': {'state': 'waiting_name', 'client': None, 'booking': None, 'turns': 1}}
    ERROR: ND

#### [WARN] Centro Estetico — LATENZA — LATENZA
- Timestamp: 2026-07-31T20:13:20.981+02:00
- Motivo: 1 turno sopra 5000ms
- Evidenza verbatim:
    USER: ND
    SARA: ND
    FSM: ND
    LAYER: ND
    LATENCY_MS: ND
    ERROR: ND


**Verticale PIÙ PRONTO:** Parrucchiere / Barbiere
(criteri: meno FAIL_SARA, poi meno FAIL_DRIVER, poi P95 migliore)
