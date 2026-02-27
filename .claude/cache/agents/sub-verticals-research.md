# Sub-Verticali FLUXION — Research CoVe 2026
> Scritto: 2026-02-27 | Fonte: dati ISTAT 2024 + ATECO + esperienza di settore
> Usato per: migration 024, wizard step 2, guida-pmi.html, CLAUDE.md

---

## 1. SALONE & HAIR (`salone`)

### 1a. Parrucchiera (`parrucchiera`)
- **Nr attività Italia**: ~80.000 (ATECO 96.02.01)
- **Terminologia**: cliente → "appuntamento per colore", "messa in piega", "trattamento cheratinico"
- **Campi scheda specifici**: formula colore (marca, tono, ossidante, tempo), allergie cute, frequenza visita (ogni X settimane)
- **Sara dialogo**: "Ha la tinta da rifare o solo piega?" / "Vuole anche la maschera ristrutturante come l'ultima volta?"
- **WhatsApp**: "Ciao [nome]! Confermato appuntamento [data] alle [ora] — [servizio]. A presto! 💇‍♀️"

### 1b. Barbiere (`barbiere`)
- **Nr attività Italia**: ~25.000 (rinascita dal 2015, +40% in 10 anni)
- **Terminologia**: "fade", "degradé", "razor", "regolabarba", "hot towel"
- **Campi scheda specifici**: stile taglio preferito (foto/testo), lunghezza clipper (n°), trattamento barba (olio, cera)
- **Sara dialogo**: "Solo taglio o anche la barba?" / "Stesso stile della volta scorsa — fade ai lati con 3 mm?"
- **WhatsApp**: "Ciao [nome]! Ti aspettiamo [data] alle [ora] per [servizio] 💈"

### 1c. Unisex (`unisex`)
- **Nr attività Italia**: ~40.000
- **Terminologia**: mista (taglio donna + taglio uomo + colore)
- **Campi scheda**: flag `tipo_clientela` (uomo/donna/bambino), formula colore (solo se donna)
- **Sara**: gestisce sia "taglio uomo" che "piega + colore" nello stesso flusso

---

## 2. ESTETICA & BEAUTY (`estetica`)

### 2a. Centro Estetico (`centro_estetico`)
- **Nr attività Italia**: ~90.000 (ATECO 96.02.02)
- **Terminologia**: "pulizia viso profonda", "peeling", "radiofrequenza", "pressoterapia", "epilazione cera/laser"
- **Campi scheda specifici**: fototipo (I-VI), tipo pelle (secca/mista/grassa/sensibile), controindicazioni (gravidanza, pacemaker, epilessia), consenso firmato
- **Sara**: "Fa la pulizia viso o un trattamento corpo?" / "Ha già fatto la radiofrequenza da noi?"
- **WhatsApp**: "Ciao [nome]! Appuntamento confermato per [servizio] il [data] alle [ora] ✨"

### 2b. Spa & Benessere (`spa`)
- **Nr attività Italia**: ~8.000
- **Terminologia**: "trattamento ayurvedico", "percorso benessere", "massaggio decontratturante/hot stone/shiatsu", "fango", "talassoterapia"
- **Campi scheda**: allergie agli oli essenziali, patologie muscolo-scheletriche, preferenza pressione massaggio (leggera/media/forte)
- **Sara**: "Massaggio rilassante o decontratturante?" / "Vuole il percorso spa completo o solo il massaggio?"
- **WhatsApp**: "Ciao [nome]! Ti aspettiamo per il tuo momento di relax: [servizio] — [data] ore [ora] 🌿"

### 2c. Nails & Makeup (`nails`)
- **Nr attività Italia**: ~35.000 (nail bar + centri PMU/trucco permanente)
- **Terminologia**: "gel", "semipermanente", "nail art", "microblading", "PMU labbra", "extension ciglia"
- **Campi scheda**: allergie al gel/acrilico, storico trattamenti PMU (colore usato, sessioni), foto risultato
- **Sara**: "Ricostruzione o refill?" / "Il trattamento PMU è per sopracciglia, labbra o eyeliner?"
- **WhatsApp**: "Ciao [nome]! Tutto pronto per [servizio] il [data] alle [ora] 💅"

### 2d. Tatuatore (`tatuatore`)
- **Nr attività Italia**: ~15.000
- **Terminologia**: "seduta", "sketch", "touch up", "flash", "blackwork", "watercolor"
- **Campi scheda**: body_chart JSON (zona corpo tatuata con descrizione), allergie inchiostro, consenso firmato (obbligatorio), foto tatuaggi precedenti
- **Sara**: "È per un nuovo tattoo o un touch up?" / "Avete già concordato il disegno con l'artista?"
- **WhatsApp**: "Ciao [nome]! Seduta confermata con [artista] il [data] alle [ora]. Porta documento d'identità ✍️"

---

## 3. FITNESS & SPORT (`palestra`)

### 3a. Palestra/Centro Fitness (`palestra`)
- **Nr attività Italia**: ~35.000
- **Terminologia**: "abbonamento", "iscrizione", "rinnovo", "lezione", "corso"
- **Campi scheda**: tipo abbonamento (mensile/trimestrale/annuale), scadenza, accessi residui, misurazioni corporee (peso/BF%/masse), scheda allenamento multifase
- **Sara**: "Vuole prenotare una lezione o ha una domanda sull'abbonamento?" / "Il suo abbonamento scade il 15 — vuole rinnovarlo?"
- **WhatsApp**: "Ciao [nome]! Classe [corso] confermata per [data] ore [ora] 💪"

### 3b. Personal Trainer (`personal_trainer`)
- **Nr attività Italia**: ~20.000 (studi privati + freelance con sede fissa)
- **Terminologia**: "sessione", "allenamento", "programma", "obiettivo", "cardio/forza/mobilità"
- **Campi scheda**: obiettivo (dimagrimento/massa/performance/riabilitazione), limitazioni fisiche, 1RM principali esercizi, progressione settimanale
- **Sara**: "È per una sessione con il personal o una lezione di gruppo?" / "Vuole fissare la sessione settimanale di martedì?"
- **WhatsApp**: "Ciao [nome]! Sessione PT confermata [data] ore [ora] con [trainer] 🏋️"

### 3c. Yoga / Pilates / Danza (`yoga_pilates`)
- **Nr attività Italia**: ~18.000
- **Terminologia**: "lezione", "classe", "corso", "livello principiante/intermedio/avanzato", "mat", "reformer"
- **Campi scheda**: livello pratica, patologie che controindicano posture (ernia, protrusioni), tesseramento CSEN/ACSI/UISP
- **Sara**: "Quale corso preferisce — yoga, pilates mat o reformer?" / "Il martedì sera c'è ancora un posto nella classe intermedia"
- **WhatsApp**: "Ciao [nome]! Classe [corso] confermata [data] ore [ora] 🧘"

---

## 4. OFFICINA & VEICOLI (`officina`)

### 4a. Meccanico (`meccanico`)
- **Nr attività Italia**: ~130.000 (ATECO 45.20)
- **Terminologia**: "tagliando", "revisione", "freni", "distribuzione", "olio", "filtri", "diagnosi"
- **Campi scheda veicolo**: targa, marca/modello/anno, km attuali, scadenze (revisione/bollo/assicurazione/RCA), storico interventi con km e data
- **Sara**: "Tagliando o ha un problema specifico?" / "Per la Panda di Rossi ho disponibile martedì mattina"
- **WhatsApp**: "Ciao [nome]! Appuntamento confermato per [veicolo] il [data] ore [ora] 🔧. La sua auto è pronta → WhatsApp automatico fine lavori"

### 4b. Elettrauto (`elettrauto`)
- **Nr attività Italia**: ~8.000
- **Terminologia**: "diagnosi OBD", "centralina", "sensori", "impianto elettrico", "DPF/FAP", "adattamento"
- **Campi scheda veicolo**: stessa anagrafica meccanico + campi specifici: codici DTC registrati, interventi centralina (mappatura, coding), impianto antifurto installato
- **Sara**: "Ha una spia accesa o un problema elettrico specifico?" / "Serve diagnosi completa o ha già il codice errore?"
- **WhatsApp**: "Ciao [nome]! Diagnosi per [veicolo] confermata [data] ore [ora] ⚡"

### 4c. Carrozzeria (`carrozzeria`)
- **Nr attività Italia**: ~22.000
- **Terminologia**: "preventivo danni", "verniciatura", "raddrizzatura", "sinistro", "perizia", "lamiera"
- **Campi scheda veicolo**: stessa anagrafica + campi specifici: foto danni (array URLs), riferimento sinistro/assicurazione, tipo verniciatura (base/metallizzata/perla), preventivo accettato (€)
- **Sara**: "È per un preventivo danni o ha già l'ok dall'assicurazione per procedere?" / "Posso fissarle un appuntamento per la perizia giovedì mattina"
- **WhatsApp**: "Ciao [nome]! Appuntamento confermato per perizia/ritiro [veicolo] il [data] ore [ora] 🚗"

---

## 5. SALUTE ORALE (`odontoiatria`)

### 5a. Odontoiatria (`odontoiatria`)
- **Nr attività Italia**: ~40.000 studi
- **Terminologia**: "visita di controllo", "otturazione", "devitalizzazione", "impianto", "corona", "bridge"
- **Campi scheda**: odontogramma FDI (32 denti × stato), anamnesi medica completa (diabete/ipertensione/anticoagulanti), piano di cura con preventivo, radiografie (link/riferimento), consenso informato firmato
- **Sara**: "Visita di controllo o ha un dolore acuto?" / "Ha urgenza o preferisce un appuntamento nella prossima settimana?"
- **WhatsApp**: "Ciao [nome]! Appuntamento confermato [data] ore [ora] con Dr. [cognome] 🦷. Ricorda di portare eventuale documentazione radiografica."

### 5b. Ortodonzia (`ortodonzia`)
- **Nr attività Italia**: ~8.000 studi specializzati
- **Terminologia**: "controllo apparecchio", "attivazione", "allineatori", "brackets", "contenzione"
- **Campi scheda**: stessa base odontoiatrica + campi specifici: tipo apparecchio (fisso/mobile/allineatori), sequenza fasi trattamento, numero seduta su totale previste
- **Sara**: "È per un controllo dell'apparecchio o ha un problema urgente (filo che punge, bracket staccato)?"
- **WhatsApp**: "Ciao [nome]! Controllo ortodontico confermato [data] ore [ora] 😁"

### 5c. Igienista Dentale (`igienista`)
- **Nr attività Italia**: ~5.000 (studi autonomi) + integrati in studi dentistici
- **Terminologia**: "igiene professionale", "pulizia denti", "sbiancamento", "airflow", "tartaro"
- **Campi scheda**: periodicità controllo (6/12 mesi), indice placca storico, tipo sbiancamento effettuato, sensibilità dentinale
- **Sara**: "È per la pulizia semestrale o ha urgenza?" / "L'ultima pulizia è stata 8 mesi fa — è il momento giusto"
- **WhatsApp**: "Ciao [nome]! Igiene professionale confermata [data] ore [ora] ✨"

---

## 6. SALUTE & RIABILITAZIONE (`fisioterapia`)

### 6a. Fisioterapia (`fisioterapia`)
- **Nr attività Italia**: ~55.000 professionisti, ~20.000 studi
- **Terminologia**: "seduta", "ciclo di trattamento", "riabilitazione", "tecar/laser/ultrasuoni"
- **Campi scheda**: VAS dolore (0-10), zona anatomica (body map), diagnosi medica di riferimento, obiettivi trattamento, diario sessione (esercizi, note, progressi), numero seduta su ciclo
- **Sara**: "È per iniziare un nuovo ciclo o proseguire quello in corso?" / "Ha la prescrizione del medico?"
- **WhatsApp**: "Ciao [nome]! Seduta fisioterapia confermata [data] ore [ora] con [terapista] 🏥"

### 6b. Osteopatia/Chiropratica (`osteopatia`)
- **Nr attività Italia**: ~12.000
- **Terminologia**: "manipolazione", "aggiustamento", "mobilizzazione", "cervicale/lombare/sacrale"
- **Campi scheda**: stessa base fisio + anamnesi specifica osteopatica (postura, respirazione, cicatrici), controindicazioni assolute (osteoporosi grave, tumori, fratture recenti)
- **Sara**: "È la prima visita o un follow-up?" / "Ha già fatto osteopatia in passato o è la prima esperienza?"
- **WhatsApp**: "Ciao [nome]! Seduta osteopatia confermata [data] ore [ora] 🌿"

### 6c. Nutrizione (`nutrizione`)
- **Nr attività Italia**: ~15.000 (nutrizionisti + dietisti)
- **Terminologia**: "visita nutrizionale", "piano alimentare", "bioimpedenziometria", "follow-up", "dieta"
- **Campi scheda**: peso/altezza/BMI storia, composizione corporea (massa magra/grassa/acqua — BIA), obiettivo (dimagrimento/massa/terapeutico), intolleranze/allergie alimentari, patologie correlate (diabete, celiachia, dislipidemia)
- **Sara**: "È per una prima visita o un controllo?" / "Ha obiettivi di perdita peso o è per una patologia specifica?"
- **WhatsApp**: "Ciao [nome]! Visita nutrizionale confermata [data] ore [ora] 🥗. Ricorda: digiuno di 4h e non fare attività fisica nelle 12h precedenti (per BIA)."

### 6d. Podologia (`podologia`)
- **Nr attività Italia**: ~4.000
- **Terminologia**: "visita podologica", "plantare ortopedico", "onicocriptosi", "callo/duroni", "baropodometria"
- **Campi scheda**: calzatura usata, patologie piede (alluci valgi, piede piatto, diabete piede), storico interventi, misura plantare
- **Sara**: "Ha un dolore specifico o viene per la visita di controllo?" / "È la prima visita o ha già i plantari da noi?"
- **WhatsApp**: "Ciao [nome]! Visita podologica confermata [data] ore [ora] 👣"

---

## RIEPILOGO IMPATTO DB

| Sotto-verticale | Schema change vs macro |
|----------------|----------------------|
| parrucchiera/barbiere/unisex | Flag `tipo_clientela` in scheda_capelli (già esiste) |
| spa, nails, tatuatore | Nails/tattoo aggiungono campo `body_chart JSON` |
| personal_trainer, yoga_pilates | Flag `tipo_sessione` in scheda_allenamento |
| elettrauto, carrozzeria | Flag `tipo_intervento` + campi condizionali in scheda_veicolo |
| ortodonzia, igienista | Flag `specializzazione` (no schema change) |
| osteopatia, nutrizione, podologia | Nutrizione aggiunge `composizione_corporea JSON` |

**Totale migrazione**: 1 colonna `sub_verticale TEXT` in `impostazioni` + 3 campi JSON condizionali facoltativi nelle schede verticali esistenti.

---

## NOTE CTO

1. **Non creare tabelle separate** per sotto-verticali — schema unico per macro, campi condizionali in UI
2. **Sub-verticale modifica**: terminologia Sara + template WhatsApp + etichette wizard (non la logica)
3. **Onboarding**: wizard mostra prima macro (6 card), poi sotto-tipo (fino a 4 opzioni)
4. **v1.0 scope**: implementare sub_verticale nel wizard e nella guida; le schede cliniche specifiche (body_chart tattoo, BIA nutrizionista) sono v1.1
