# FLUXION - Benchmark Funzionalità

> **Versione**: 0.7.0 (Fase 7)
> **Data**: 2026-01-07
> **Target**: PMI italiane (1-15 dipendenti)
> **Modello**: Licenza desktop annuale (NO SaaS, NO commissioni)

---

## PANORAMICA PRODOTTO

| Caratteristica | FLUXION |
|----------------|---------|
| **Tipo** | Applicazione desktop nativa |
| **Piattaforme** | Windows 10+, macOS 12+, Linux |
| **Database** | SQLite locale (dati sul TUO computer) |
| **Cloud** | Non richiesto (offline-first) |
| **Costi ricorrenti API** | Zero (WhatsApp locale, IA opzionale) |
| **Privacy** | GDPR-compliant, dati mai su server terzi |

---

## 1. CRM CLIENTI

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Anagrafica completa** | Nome, cognome, telefono, email, note | ✅ |
| **Ricerca veloce** | Filtro real-time su tutti i campi | ✅ |
| **Soft delete** | Clienti eliminati recuperabili | ✅ |
| **Storico appuntamenti** | Visualizza tutti gli appuntamenti del cliente | ✅ |
| **Badge VIP** | Segnala clienti premium | ✅ |
| **Referral tracking** | Traccia chi ha portato il cliente | ✅ |

### Specifiche Tecniche
- Storage: SQLite con indici ottimizzati
- Validazione: Zod schemas frontend + Rust backend
- API: TanStack Query con cache automatica

---

## 2. CALENDARIO & PRENOTAZIONI

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Vista mensile** | Griglia calendario con appuntamenti | ✅ |
| **Creazione rapida** | Click su giorno → nuovo appuntamento | ✅ |
| **Auto-completamento** | Cerca cliente/servizio/operatore | ✅ |
| **Conflict detection** | Avviso sovrapposizione orari | ✅ |
| **Stati appuntamento** | Bozza → Proposto → Confermato → Completato | ✅ |
| **Override manuale** | Forza appuntamento con motivazione (audit trail) | ✅ |
| **Orari di lavoro** | Configura apertura/chiusura per giorno | ✅ |
| **Festività** | Calendario festivi italiani + personalizzati | ✅ |
| **Validazione orari** | Blocca appuntamenti fuori orario | ✅ |

### Workflow Appuntamenti
```
Bozza → Proposto → Confermato Cliente → Confermato Operatore → Completato
                                    ↘ Rifiutato
                                    ↘ Cancellato
```

### Specifiche Tecniche
- State machine: 8 stati con transizioni validate
- Validation: 3 livelli (hard block, warning, suggestion)
- Conflict: Check automatico operatore + orario

---

## 3. SERVIZI & LISTINO

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Catalogo servizi** | Nome, durata, prezzo | ✅ |
| **Durata flessibile** | Da 15 min a 4 ore | ✅ |
| **Prezzi personalizzabili** | Per servizio | ✅ |
| **Associazione operatori** | Quali operatori fanno quale servizio | ✅ |

---

## 4. GESTIONE OPERATORI

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Anagrafica operatori** | Nome, cognome, specializzazioni | ✅ |
| **Colore identificativo** | Per distinguere nel calendario | ✅ |
| **Assegnazione servizi** | Operatore ↔ Servizi abilitati | ✅ |
| **Disponibilità** | Orari per operatore | ✅ |

---

## 5. PROGRAMMA FEDELTÀ

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Tessera timbri digitale** | Conta visite, premio a soglia | ✅ |
| **Progress bar visiva** | "8/10 visite per il premio" | ✅ |
| **Badge VIP** | Cliente premium con vantaggi | ✅ |
| **Soglia personalizzabile** | Default 10, configurabile | ✅ |
| **Incremento automatico** | +1 visita ad appuntamento completato | ✅ |
| **Referral tracking** | "Chi ti ha consigliato?" | ✅ |
| **Top Referrer report** | Classifica clienti che portano amici | ✅ |

### Specifiche Tecniche
- Campi DB: loyalty_visits, loyalty_threshold, is_vip, referral_source
- Incremento: Trigger su stato appuntamento = 'completato'

---

## 6. PACCHETTI & ABBONAMENTI

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Creazione pacchetti** | Es. "5 Massaggi a €180" | ✅ |
| **Composizione servizi** | Seleziona quali servizi include | ✅ |
| **Calcolo sconto automatico** | Inserisci % sconto → calcola prezzo | ✅ |
| **Proposta pacchetto** | Invia proposta al cliente | ✅ |
| **Tracciamento utilizzo** | "Usati 3/5 servizi" | ✅ |
| **Scadenza pacchetto** | Validità in giorni | ✅ |
| **Countdown visivo** | Rosso ≤7gg, Giallo ≤30gg | ✅ |
| **Stati pacchetto** | Proposto → Venduto → In uso → Completato | ✅ |

---

## 7. FATTURAZIONE ELETTRONICA

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Creazione fatture** | Da cliente esistente | ✅ |
| **Tipi documento** | Fattura, Nota di credito, Parcella | ✅ |
| **Righe documento** | Descrizione, quantità, prezzo, IVA | ✅ |
| **Aliquote IVA** | 22%, 10%, 4%, esente (con natura) | ✅ |
| **Bollo virtuale** | Automatico per importi >€77.47 forfettari | ✅ |
| **Numerazione progressiva** | Per anno, automatica | ✅ |
| **XML FatturaPA** | Generazione conforme SDI 1.2.2 | ✅ |
| **Download XML** | Per invio manuale a SDI | ✅ |
| **Stati fattura** | Bozza → Emessa → Pagata/Annullata | ✅ |
| **Tracking pagamenti** | Data, importo, metodo | ✅ |
| **Impostazioni azienda** | P.IVA, CF, regime fiscale, IBAN | ✅ |

### Regimi Fiscali Supportati
- RF01: Ordinario
- RF02: Contribuenti minimi
- RF04: Agricoltura
- RF19: Forfettario (default)

### Specifiche Tecniche
- XML: FatturaPA v1.2.2 compliant
- Validazione: Partita IVA, Codice Fiscale
- Lookup: Codici pagamento SDI (MP01-MP23), Nature IVA (N1-N7)

---

## 8. WHATSAPP INTEGRATION

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **QR Kit** | 3 QR preconfigurati (Prenota, Info, Sposta) | ✅ |
| **Export PDF** | Stampa A4 con QR + testo + logo | ✅ |
| **Personalizzazione messaggio** | Modifica testo predefinito | ✅ |
| **Auto-Responder** | Risposte automatiche intelligenti | ✅ |
| **FLUXION IA** | Risposte basate su FAQ con LLM | ✅ |
| **Confidence threshold** | Passa a operatore se non sicuro | ✅ |
| **FAQ Learning** | Operatore insegna al bot | ✅ |
| **Rate limiting** | Max 60 risposte/ora per utente | ✅ |
| **Log messaggi** | Cronologia ricevuti/inviati | ✅ |

### Come Funziona l'Auto-Responder
```
Cliente scrive → Bot cerca nelle FAQ
  ├─ Confidence ≥50% → Risponde automaticamente
  └─ Confidence <50% → "Passo al team" + salva domanda

Operatore risponde → Sistema traccia
  └─ Click "Salva FAQ" → Bot impara per futuro
```

### Garanzia
- **MAI improvvisa**: Solo dati verificati da FAQ/DB
- **Zero costi API**: WhatsApp Web locale (no Meta API)
- **Privacy**: Nessun dato su server terzi

### Specifiche Tecniche
- Engine: whatsapp-web.js (automazione locale)
- LLM: Groq API (llama-3.1-8b-instant) - opzionale
- Storage: JSONL per messaggi, Markdown per FAQ

---

## 9. ASSISTENTE INTELLIGENTE (FLUXION IA)

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Chat assistente** | Interfaccia conversazionale | ✅ |
| **FAQ per categoria** | Salone, Auto, Wellness, Medical | ✅ |
| **Confidence score** | Mostra affidabilità risposta | ✅ |
| **Fonti citate** | Mostra da quale FAQ viene la risposta | ✅ |
| **Test connessione** | Verifica API key funzionante | ✅ |

### Categorie FAQ Supportate
- **Salone**: Parrucchieri, estetisti, barbieri
- **Auto**: Officine, carrozzerie, elettrauto
- **Wellness**: Palestre, SPA, fisioterapisti
- **Medical**: Studi medici, dentisti

### Specifiche Tecniche
- LLM: Groq (llama-3.1-8b-instant)
- Retrieval: Keyword-based TF-IDF lite
- Costo: ~$0.0001 per risposta

---

## 10. SUPPORTO & DIAGNOSTICA (FLUXION CARE)

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Diagnostica sistema** | Versione app, OS, spazio disco | ✅ |
| **Export Support Bundle** | ZIP con log, config, diagnostica | ✅ |
| **Backup database** | Copia atomica 1-click | ✅ |
| **Restore database** | Ripristino con verifica integrità | ✅ |
| **Lista backup** | Storico con date e dimensioni | ✅ |
| **Remote Assist** | Istruzioni per assistenza remota | ✅ |

### Contenuto Support Bundle
- Versioni (app, OS, Rust, Node)
- Ultimi 500 righe di log
- Configurazione (no dati sensibili)
- Info database (dimensione, tabelle)
- Spazio disco disponibile

---

## 11. SETUP WIZARD

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Onboarding guidato** | 4 step configurazione iniziale | ✅ |
| **Dati attività** | Nome, P.IVA, CF, categoria | ✅ |
| **Sede** | Indirizzo, CAP, città, provincia | ✅ |
| **Configurazione** | Regime fiscale, FLUXION IA key | ✅ |
| **Riepilogo** | Conferma prima di salvare | ✅ |

---

## 12. DASHBOARD & STATISTICHE

### Funzionalità
| Feature | Descrizione | Disponibile |
|---------|-------------|-------------|
| **Appuntamenti oggi** | Contatore real-time | ✅ |
| **Appuntamenti settimana** | Totale 7 giorni | ✅ |
| **Clienti totali** | Contatore attivi | ✅ |
| **Clienti VIP** | Contatore premium | ✅ |
| **Nuovi clienti mese** | Acquisizioni ultimi 30gg | ✅ |
| **Fatturato mese** | Somma fatture emesse | ✅ |
| **Lista appuntamenti oggi** | Con orario, cliente, servizio | ✅ |

---

## CONFRONTO CON COMPETITOR

| Funzionalità | FLUXION | Competitor SaaS |
|--------------|---------|-----------------|
| **Costo mensile** | €0 (licenza annuale) | €30-100/mese |
| **Commissioni prenotazione** | 0% | 1-5% |
| **Dati dove** | Sul TUO computer | Cloud terzi |
| **Offline** | ✅ Funziona sempre | ❌ Richiede internet |
| **WhatsApp** | ✅ Gratuito (locale) | €50-200/mese API |
| **Fatturazione elettronica** | ✅ Inclusa | Extra €10-30/mese |
| **IA Assistente** | ✅ ~€5/mese (opzionale) | €20-50/mese |
| **Multi-sede** | Roadmap | ✅ |
| **App mobile cliente** | Roadmap | ✅ |

---

## STACK TECNOLOGICO

| Componente | Tecnologia |
|------------|------------|
| **Framework** | Tauri 2.x (Rust + WebView) |
| **Frontend** | React 19 + TypeScript |
| **UI** | shadcn/ui + Tailwind CSS 3.4 |
| **Database** | SQLite (locale, embedded) |
| **State** | TanStack Query v5 |
| **LLM** | Groq API (opzionale) |
| **WhatsApp** | whatsapp-web.js (locale) |
| **Build** | Multi-platform (Win/Mac/Linux) |

---

## REQUISITI SISTEMA

| OS | Versione Minima |
|----|-----------------|
| **Windows** | Windows 10 build 1809+ |
| **macOS** | macOS 12 Monterey+ |
| **Linux** | Ubuntu 22.04+ / equivalente |

| Risorsa | Minimo |
|---------|--------|
| **RAM** | 4 GB |
| **Disco** | 500 MB |
| **Internet** | Solo per FLUXION IA (opzionale) |

---

## ROADMAP FUTURA

| Funzionalità | Fase | Priorità |
|--------------|------|----------|
| Voice Agent (chiamate automatiche) | 7 | Alta |
| Integrazione VoIP Ehiweb | 7 | Alta |
| Waitlist con priorità VIP | 8 | Media |
| Sistema licenze + auto-update | 8 | Alta |
| Moduli verticali (Beauty, Auto, Medical) | 9 | Media |
| App mobile cliente | 10 | Bassa |
| Multi-sede | 10 | Bassa |

---

*Documento generato automaticamente - FLUXION v0.7.0*
