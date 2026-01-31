# Prompt per Kimi 2.5 — Conversational Booking State Machine

Copia tutto il contenuto sotto la linea e incollalo su Kimi 2.5.

---

## Contesto di Sistema

Sto sviluppando **FLUXION**, un gestionale desktop per PMI italiane (saloni, palestre, cliniche). Ha un **voice agent** ("Sara") che simula una **telefonata VoIP** — il cliente chiama, Sara risponde, raccoglie i dati e prenota.

Stack: Python 3.9, state machine deterministica, entity extraction via regex, WhatsApp Web integrato (invio messaggi + chiamate), calendario appuntamenti con disponibilità reale.

## Cosa Devi Generare

Genera un **flusso conversazionale completo** come Python pseudo-code strutturato (dizionario di stati con transizioni, risposte template, e regole di validazione). Il formato deve essere simile a una state machine con questi elementi per ogni stato:

```python
{
    "state": "NOME_STATO",
    "prompt_sara": "Cosa dice Sara al cliente",
    "expected_input": "Cosa si aspetta dal cliente",
    "extraction_rules": ["come estrarre i dati dall'input"],
    "validation": ["regole di validazione"],
    "on_success": "PROSSIMO_STATO",
    "on_failure": "risposta di errore / richiesta ripetizione",
    "on_interrupt": "gestione interruzioni (annulla, operatore, indietro)"
}
```

## Requisiti del Flusso — SEGUI QUEST'ORDINE ESATTO

### FASE 1: Identificazione Cliente (sequenziale, un campo alla volta)

**Stato GREETING:**
- Sara risponde: "Buongiorno, salone [NomeSalone], sono Sara. Come posso aiutarla?"
- Se il cliente dice il nome nel saluto (es. "Ciao sono Gino"), estrarlo e saltare a ASKING_SURNAME
- Se non dice il nome, passare a ASKING_NAME

**Stato ASKING_NAME:**
- Sara chiede: "Mi può dire il suo nome?"
- Estrae SOLO il nome (primo nome), ignorando cognomi e parole non-nome
- Blacklist: saluti ("ciao", "buongiorno", "salve"), interiezioni ("ehi", "eh"), parole comuni ("grazie", "niente")
- Validazione: almeno 2 caratteri, solo lettere (con accenti italiani)
- On success → ASKING_SURNAME

**Stato ASKING_SURNAME:**
- Sara chiede: "Piacere [Nome]! Mi può dire il cognome?"
- CRITICO: NON deve sovrascrivere il nome già estratto. Se il cliente dice "Di Nanni", deve restare come cognome, non sovrascrivere il nome "Gino" con "Di"
- Gestire cognomi composti italiani: "Di Nanni", "De Luca", "Lo Russo", "La Barbera", "D'Angelo"
- On success → CHECKING_CLIENT (lookup DB)

**Stato CHECKING_CLIENT:**
- Cerca nel database per nome+cognome
- Se trovato 1 risultato → salva client_id, saluta "Bentornato [Nome]!" → ASKING_SERVICE
- Se trovati più risultati (omonimi) → disambiguazione (chiedi data di nascita o telefono)
- Se non trovato → ASKING_PHONE (registrazione nuovo cliente)

**Stato ASKING_PHONE:**
- Sara chiede: "Non la trovo tra i nostri clienti. Mi può dare un numero di telefono per registrarla?"
- Estrazione telefono: accetta formati italiani (333 1234567, +39 333 1234567, 3331234567)
- Validazione: 10 cifre (mobile) o formato fisso italiano
- Conferma: "Ho capito [numero formattato], è corretto?"
- On success → registra cliente nel DB → ASKING_SERVICE

### FASE 2: Raccolta Servizi (accetta multipli)

**Stato ASKING_SERVICE:**
- Sara chiede: "Cosa desidera fare oggi?"
- DEVE accettare servizi multipli in una frase:
  - "taglio e barba" → ["Taglio", "Barba"]
  - "taglio, colore e piega" → ["Taglio", "Colore", "Piega"]
  - "vorrei taglio e anche una barba" → ["Taglio", "Barba"]
- Servizi riconosciuti (salone): taglio, piega, colore/tinta, barba, trattamento, cheratina, extension, meches, shatush, balayage
- Sinonimi: "sforbiciata" = taglio, "ritocco" = colore, "messa in piega" = piega
- Se servizio non riconosciuto → "Mi scusi, non ho capito il trattamento. Offriamo: taglio, piega, colore, barba, trattamento. Cosa preferisce?"
- Salvare sia la lista servizi che il display combinato ("Taglio e Barba")
- On success → ASKING_DATE

### FASE 3: Data con Gestione Intelligente del Calendario

**Stato ASKING_DATE:**
- Sara chiede: "Per quando vorrebbe l'appuntamento?"
- Gestire date esplicite: "domani", "lunedì", "15 gennaio", "dopodomani"
- **CASO CRITICO — "la settimana prossima" / "la prossima settimana":**
  - NON chiedere semplicemente "che giorno?"
  - DEVE interrogare il calendario per i giorni disponibili della settimana prossima
  - Risposta tipo: "La settimana prossima abbiamo disponibilità martedì, mercoledì e venerdì. Quale giorno preferisce?"
  - Se nessun giorno disponibile: "Mi dispiace, la settimana prossima siamo al completo. Vuole provare la settimana dopo?"
- Gestire anche: "questa settimana", "tra due settimane", "il mese prossimo"
- Validazione: la data non può essere nel passato
- Validazione: la data non può essere un giorno di chiusura
- On success → ASKING_TIME

**Stato ASKING_TIME:**
- Sara chiede: "A che ora preferisce? Abbiamo disponibilità alle [slot liberi]."
- DEVE mostrare gli slot effettivamente liberi per quella data e quel servizio
- Gestire formati italiani:
  - "alle 15" → 15:00
  - "le 3 del pomeriggio" → 15:00
  - "17 e mezza" → 17:30
  - "dopo le 17" → primo slot >= 17:00
  - "di mattina" → mostra slot mattutini disponibili
  - "nel pomeriggio" → mostra slot pomeridiani disponibili
- Se slot non disponibile → "Quell'ora è occupata. Posso offrirle [alternative]. Quale preferisce?"
- On success → CONFIRMING

### FASE 4: Conferma e Chiusura Chiamata

**Stato CONFIRMING:**
- Sara riepiloga: "Riepilogo: [Nome Cognome], [Servizio/i], [Data display] alle [Ora]. Conferma?"
- Accetta: "sì", "confermo", "va bene", "ok", "perfetto", "esatto"
- Rifiuta: "no", "annulla", "cambia" → chiedi cosa modificare
- Modifica parziale: "cambia l'ora" → torna a ASKING_TIME mantenendo il resto
- On conferma → COMPLETED

**Stato COMPLETED:**
- Sara dice: "Perfetto! Ho prenotato [riepilogo]. Riceverà conferma su WhatsApp. Grazie e arrivederci!"
- AZIONE SISTEMA: invia messaggio WhatsApp di conferma al numero del cliente
- AZIONE SISTEMA: should_exit = True (chiude la chiamata VoIP)
- La sessione FINISCE qui. Nessun follow-up, nessun "posso aiutarla con altro?" — è una telefonata, si chiude.

### FASE 5: Escalation a Operatore

In QUALSIASI momento della conversazione, se il cliente dice:
- "voglio parlare con un operatore"
- "passami qualcuno"
- "fammi parlare con una persona vera"
- "operatore"
- Espressione di frustrazione ripetuta (3+ turni di incomprensione)

**Comportamento:**
- Sara dice: "La metto subito in contatto con un operatore, un attimo..."
- AZIONE SISTEMA: invia WhatsApp al numero del titolare registrato nelle impostazioni: "Richiesta escalation da cliente [Nome]. Richiamarlo al [numero cliente]."
- AZIONE SISTEMA: should_exit = True (chiude la chiamata VoIP)
- La sessione FINISCE — l'operatore richiamerà il cliente

## Regole Globali

1. **Lingua**: Tutto in italiano formale (dare del Lei). "Può ripetere?" non "Puoi ripetere?"
2. **Sequenzialità**: Mai chiedere due informazioni nella stessa domanda. Una domanda → una risposta → prossima domanda
3. **Persistenza**: Se il cliente fornisce info in anticipo (es. "Sono Gino, vorrei un taglio domani"), estrarre TUTTO ma procedere in ordine confermando ciò che manca
4. **Errori STT**: Il sistema usa Speech-to-Text che può sbagliare. Gestire varianti fonetiche: "Gino" / "Gina" / "Dino", "barba" / "Barbara"
5. **Interruzioni**: In ogni stato gestire "annulla" (reset), "indietro" (stato precedente), "operatore" (escalation)
6. **Timeout**: Se il cliente non risponde o dice qualcosa di incomprensibile per 3 turni consecutivi → escalation automatica
7. **Content filter**: Linguaggio offensivo/sessuale → "Questo tipo di linguaggio non è appropriato. La conversazione verrà terminata." + should_exit
8. **WhatsApp**: Dopo ogni prenotazione confermata, SEMPRE inviare conferma WhatsApp. Mai dire "SMS" — il sistema usa solo WhatsApp
9. **Chiusura chiamata**: Dopo COMPLETED o ESCALATION → SEMPRE chiudere la sessione (should_exit=True). È una telefonata, non una chat

## Output Atteso

Genera:
1. **Dizionario completo degli stati** con transizioni, prompt, validazioni
2. **Template delle risposte di Sara** per ogni stato (varianti per naturalezza)
3. **Regole di estrazione** per ogni campo (regex patterns per italiano)
4. **Matrice delle transizioni** (da ogni stato, tutti i possibili percorsi)
5. **Casi edge** documentati (omonimi, cognomi composti, servizi multipli, "settimana prossima", orari ambigui)
6. **Flusso di errore** per ogni stato (cosa succede se l'input è incomprensibile)

Il tutto in Python, pronto per essere integrato in una BookingStateMachine esistente.
