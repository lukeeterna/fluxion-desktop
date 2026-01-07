# FLUXION - Checklist Test Completa

> **Data**: 2026-01-07
> **Versione**: 0.7.0

---

## SETUP INIZIALE

### 1. Sincronizza codice
```bash
cd /Volumes/MacSSD\ -\ Dati/fluxion
git pull origin master
```

### 2. Avvia applicazione
```bash
npm run tauri dev
```

### 3. (Opzionale) Importa dati demo
```bash
# Se vuoi dati di test precaricati:
sqlite3 ~/Library/Application\ Support/com.fluxion.desktop/fluxion.db < scripts/mock_data.sql
```

---

## TEST 1: SETUP WIZARD

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 1.1 | Avvia app per prima volta | Appare Setup Wizard | ☐ |
| 1.2 | Step 1: Inserisci nome attività | Campo accetta testo | ☐ |
| 1.3 | Step 1: Inserisci P.IVA (11 cifre) | Validazione formato | ☐ |
| 1.4 | Step 1: Seleziona categoria | Dropdown funziona | ☐ |
| 1.5 | Step 2: Inserisci indirizzo completo | Tutti i campi funzionano | ☐ |
| 1.6 | Step 3: Seleziona regime fiscale | Dropdown funziona | ☐ |
| 1.7 | Step 3: FLUXION IA Key (opzionale) | Campo accetta API key | ☐ |
| 1.8 | Step 4: Riepilogo mostra tutti i dati | Dati corretti | ☐ |
| 1.9 | Click "Completa Configurazione" | Wizard si chiude, app parte | ☐ |

---

## TEST 2: DASHBOARD

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 2.1 | Vai su Dashboard (Home) | Pagina carica senza errori | ☐ |
| 2.2 | Verifica "Appuntamenti Oggi" | Mostra numero corretto | ☐ |
| 2.3 | Verifica "Appuntamenti Settimana" | Mostra numero corretto | ☐ |
| 2.4 | Verifica "Clienti Totali" | Mostra conteggio | ☐ |
| 2.5 | Verifica "Clienti VIP" | Mostra conteggio | ☐ |
| 2.6 | Verifica lista appuntamenti oggi | Lista con dettagli | ☐ |

---

## TEST 3: CRM CLIENTI

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 3.1 | Vai su Clienti | Lista clienti visibile | ☐ |
| 3.2 | Click "+ Nuovo Cliente" | Dialog si apre | ☐ |
| 3.3 | Compila nome e cognome | Campi funzionano | ☐ |
| 3.4 | Compila telefono | Validazione formato | ☐ |
| 3.5 | Compila email | Validazione email | ☐ |
| 3.6 | Salva cliente | Cliente appare in lista | ☐ |
| 3.7 | Cerca cliente per nome | Filtro funziona | ☐ |
| 3.8 | Click su cliente esistente | Dialog modifica si apre | ☐ |
| 3.9 | Tab "Fedeltà" (in modifica) | Mostra progress bar visite | ☐ |
| 3.10 | Tab "Pacchetti" (in modifica) | Mostra pacchetti cliente | ☐ |
| 3.11 | Toggle VIP | Badge VIP cambia | ☐ |
| 3.12 | Elimina cliente | Cliente rimosso (soft delete) | ☐ |

---

## TEST 4: SERVIZI

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 4.1 | Vai su Servizi | Lista servizi visibile | ☐ |
| 4.2 | Click "+ Nuovo Servizio" | Dialog si apre | ☐ |
| 4.3 | Inserisci nome servizio | Campo funziona | ☐ |
| 4.4 | Inserisci durata (minuti) | Campo numerico | ☐ |
| 4.5 | Inserisci prezzo | Campo numerico con decimali | ☐ |
| 4.6 | Salva servizio | Servizio appare in lista | ☐ |
| 4.7 | Modifica servizio esistente | Dati si aggiornano | ☐ |
| 4.8 | Elimina servizio | Servizio rimosso | ☐ |

---

## TEST 5: OPERATORI

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 5.1 | Vai su Operatori | Lista operatori visibile | ☐ |
| 5.2 | Click "+ Nuovo Operatore" | Dialog si apre | ☐ |
| 5.3 | Inserisci nome e cognome | Campi funzionano | ☐ |
| 5.4 | Seleziona colore | Color picker funziona | ☐ |
| 5.5 | Salva operatore | Operatore appare in lista | ☐ |
| 5.6 | Modifica operatore | Dati si aggiornano | ☐ |
| 5.7 | Elimina operatore | Operatore rimosso | ☐ |

---

## TEST 6: CALENDARIO & APPUNTAMENTI

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 6.1 | Vai su Calendario | Griglia mensile visibile | ☐ |
| 6.2 | Naviga mese precedente/successivo | Frecce funzionano | ☐ |
| 6.3 | Click su un giorno | Dialog nuovo appuntamento | ☐ |
| 6.4 | Cerca e seleziona cliente | Autocomplete funziona | ☐ |
| 6.5 | Seleziona servizio | Dropdown popola | ☐ |
| 6.6 | Seleziona operatore | Dropdown popola | ☐ |
| 6.7 | Seleziona orario | Time picker funziona | ☐ |
| 6.8 | Salva appuntamento | Appare nel calendario | ☐ |
| 6.9 | Click su appuntamento esistente | Dialog modifica si apre | ☐ |
| 6.10 | Cambia stato (Conferma) | Stato si aggiorna | ☐ |
| 6.11 | Prova conflitto orario | Warning/block appare | ☐ |
| 6.12 | Prova orario fuori lavoro | Warning appare | ☐ |
| 6.13 | Cancella appuntamento | Appuntamento rimosso | ☐ |

---

## TEST 7: IMPOSTAZIONI - ORARI & FESTIVITÀ

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 7.1 | Vai su Impostazioni | Pagina carica | ☐ |
| 7.2 | Sezione "Orari di Lavoro" | Lista giorni visibile | ☐ |
| 7.3 | Click "+ Aggiungi Orario" | Dialog si apre | ☐ |
| 7.4 | Seleziona giorno + orario | Campi funzionano | ☐ |
| 7.5 | Salva orario | Orario appare nella lista | ☐ |
| 7.6 | Elimina orario (X) | Orario rimosso | ☐ |
| 7.7 | Sezione "Festività" | Lista festivi visibile | ☐ |
| 7.8 | Click "+ Aggiungi Festività" | Dialog si apre | ☐ |
| 7.9 | Inserisci data + descrizione | Campi funzionano | ☐ |
| 7.10 | Toggle "Ricorrente" | Checkbox funziona | ☐ |
| 7.11 | Salva festività | Festività appare in lista | ☐ |

---

## TEST 8: PACCHETTI

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 8.1 | Impostazioni → Sezione Pacchetti | Lista pacchetti visibile | ☐ |
| 8.2 | Click "Nuovo Pacchetto" | Dialog si apre | ☐ |
| 8.3 | Inserisci nome pacchetto | Campo funziona | ☐ |
| 8.4 | Seleziona servizi inclusi | Multi-select funziona | ☐ |
| 8.5 | Inserisci % sconto | Campo numerico | ☐ |
| 8.6 | Verifica prezzo calcolato | Prezzo auto-calcolato | ☐ |
| 8.7 | Inserisci validità (giorni) | Campo numerico | ☐ |
| 8.8 | Salva pacchetto | Pacchetto appare in lista | ☐ |
| 8.9 | Vai su cliente → Tab Pacchetti | Lista pacchetti cliente | ☐ |
| 8.10 | Proponi pacchetto a cliente | Stato = "Proposto" | ☐ |
| 8.11 | Conferma acquisto | Stato = "Venduto" | ☐ |
| 8.12 | Usa servizio pacchetto | Contatore incrementa | ☐ |

---

## TEST 9: WHATSAPP QR KIT

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 9.1 | Impostazioni → Sezione WhatsApp QR | 3 QR visibili | ☐ |
| 9.2 | Verifica QR "Prenota" | QR generato | ☐ |
| 9.3 | Verifica QR "Info" | QR generato | ☐ |
| 9.4 | Verifica QR "Sposta" | QR generato | ☐ |
| 9.5 | Click "Modifica messaggio" | Textarea si espande | ☐ |
| 9.6 | Modifica testo messaggio | Testo cambia | ☐ |
| 9.7 | Click "Salva PDF" | PDF scaricato in Downloads | ☐ |
| 9.8 | Apri PDF | QR + testo visibili | ☐ |

---

## TEST 10: WHATSAPP AUTO-RESPONDER

### Setup (in terminale separato)
```bash
cd /Volumes/MacSSD\ -\ Dati/fluxion
npm run whatsapp:start
```

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 10.1 | Terminale: `npm run whatsapp:start` | QR code appare | ☐ |
| 10.2 | Scansiona QR con WhatsApp | Connessione stabilita | ☐ |
| 10.3 | App: Impostazioni → WhatsApp | Status = "Connesso" | ☐ |
| 10.4 | Verifica toggle Auto-Responder | ON/OFF funziona | ☐ |
| 10.5 | Seleziona categoria FAQ | Dropdown funziona | ☐ |
| 10.6 | **Da altro telefono**: invia messaggio test | - | ☐ |
| 10.7 | Messaggio: "Quali sono gli orari?" | Bot risponde con info orari | ☐ |
| 10.8 | Verifica log messaggi in app | Messaggio appare | ☐ |
| 10.9 | Messaggio NON nelle FAQ: "Fate piercing?" | Bot risponde "passo al team" | ☐ |
| 10.10 | Verifica "Apprendimento Bot" | Domanda appare in lista | ☐ |

---

## TEST 11: FAQ LEARNING SYSTEM

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 11.1 | Invia domanda NON nelle FAQ | Bot risponde "non ho info" | ☐ |
| 11.2 | Impostazioni → WhatsApp → Apprendimento | Domanda in lista "Da Salvare" | ☐ |
| 11.3 | Rispondi manualmente da WhatsApp | Risposta tracciata | ☐ |
| 11.4 | In app: vedi risposta operatore | Risposta visibile | ☐ |
| 11.5 | Modifica risposta se necessario | Textarea modificabile | ☐ |
| 11.6 | Click "Salva come FAQ" | Successo, status cambia | ☐ |
| 11.7 | Verifica file `data/faq_custom.md` | Nuova Q&A aggiunta | ☐ |
| 11.8 | Invia stessa domanda di nuovo | Bot risponde correttamente | ☐ |

---

## TEST 12: FLUXION IA (ASSISTENTE)

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 12.1 | Impostazioni → FLUXION IA | Chat interface visibile | ☐ |
| 12.2 | Click "Test API" | "Connessione OK" o errore chiaro | ☐ |
| 12.3 | Seleziona categoria (es. Salone) | Dropdown funziona | ☐ |
| 12.4 | Scrivi domanda: "Quali trattamenti fate?" | Risposta generata | ☐ |
| 12.5 | Verifica confidence badge | % visibile | ☐ |
| 12.6 | Espandi "Fonti" | FAQ sorgente mostrata | ☐ |
| 12.7 | Cambia categoria (es. Auto) | Risposte cambiano contesto | ☐ |

---

## TEST 13: FATTURAZIONE ELETTRONICA

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 13.1 | Vai su Fatture | Lista fatture (o vuota) | ☐ |
| 13.2 | Click "+ Nuova Fattura" | Dialog si apre | ☐ |
| 13.3 | Seleziona cliente | Autocomplete funziona | ☐ |
| 13.4 | Seleziona tipo documento | Dropdown funziona | ☐ |
| 13.5 | Inserisci data | Date picker funziona | ☐ |
| 13.6 | Salva bozza | Fattura in stato "Bozza" | ☐ |
| 13.7 | Click su fattura | Sheet dettaglio si apre | ☐ |
| 13.8 | Aggiungi riga | Dialog riga si apre | ☐ |
| 13.9 | Inserisci descrizione, qta, prezzo | Campi funzionano | ☐ |
| 13.10 | Seleziona aliquota IVA | Dropdown funziona | ☐ |
| 13.11 | Salva riga | Riga appare in fattura | ☐ |
| 13.12 | Verifica totali calcolati | Imponibile, IVA, Totale corretti | ☐ |
| 13.13 | Click "Emetti Fattura" | Stato = "Emessa", XML generato | ☐ |
| 13.14 | Click "Scarica XML" | File XML scaricato | ☐ |
| 13.15 | Verifica contenuto XML | FatturaPA 1.2.2 valido | ☐ |
| 13.16 | Registra pagamento | Data, importo, metodo | ☐ |
| 13.17 | Verifica stato "Pagata" | Se totale pagato = totale fattura | ☐ |

### Impostazioni Fatturazione
| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 13.18 | Fatture → Ingranaggio (impostazioni) | Dialog impostazioni | ☐ |
| 13.19 | Tab "Azienda" | Dati azienda modificabili | ☐ |
| 13.20 | Tab "Fiscale" | Regime, bollo configurabili | ☐ |
| 13.21 | Tab "Banca" | IBAN modificabile | ☐ |
| 13.22 | Salva impostazioni | Dati persistono | ☐ |

---

## TEST 14: FLUXION CARE (DIAGNOSTICA)

| # | Azione | Risultato Atteso | ✓ |
|---|--------|------------------|---|
| 14.1 | Impostazioni → Fluxion Care | Pannello diagnostica visibile | ☐ |
| 14.2 | Verifica versione app | Versione mostrata | ☐ |
| 14.3 | Verifica versione OS | OS mostrato | ☐ |
| 14.4 | Verifica spazio disco | GB liberi mostrati | ☐ |
| 14.5 | Click "Esporta Bundle Supporto" | ZIP creato | ☐ |
| 14.6 | Click "Backup Database" | Backup creato | ☐ |
| 14.7 | Verifica lista backup | Backup appare in lista | ☐ |
| 14.8 | Click "Assistenza Remota" | Istruzioni mostrate | ☐ |

---

## COMANDI UTILI

### Reset Database (se necessario)
```bash
rm ~/Library/Application\ Support/com.fluxion.desktop/fluxion.db
# Riavvia app per creare nuovo DB
```

### Importa Dati Demo
```bash
sqlite3 ~/Library/Application\ Support/com.fluxion.desktop/fluxion.db < scripts/mock_data.sql
```

### Verifica WhatsApp Service
```bash
# In terminale separato
npm run whatsapp:start

# Oppure direttamente
node scripts/whatsapp-service.js start
```

### Verifica FAQ Custom
```bash
cat data/faq_custom.md
```

### Log App
```bash
# macOS
tail -f ~/Library/Logs/com.fluxion.desktop/*.log
```

---

## NOTE FINALI

- **Se un test fallisce**: Annota il numero e l'errore
- **Screenshot**: Fai screenshot degli errori
- **Riavvia app**: Se bloccata, chiudi e riavvia
- **Console DevTools**: Cmd+Shift+I per vedere errori JavaScript

---

*Checklist generata automaticamente - FLUXION v0.7.0*
