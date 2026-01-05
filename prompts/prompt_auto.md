# PROMPT: Genera FAQ per FLUXION-AUTO

## Contesto Sistema

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Officine meccaniche, elettrauto, carrozzerie, gommisti, autolavaggi (1-15 dipendenti) in Italia.

---

## Istruzioni

Genera un file Markdown completo con TUTTE le FAQ tipiche per un'officina/carrozzeria italiana.

**Tono delle risposte:**
- Gentile, competente, rassicurante
- Stile pratico ma cordiale
- Usa emoji con moderazione (1-2 per risposta)
- Risposte brevi e dirette (max 3-4 frasi)
- Mai tecnicismi incomprensibili, spiega in modo semplice

**Formato output richiesto:**

```markdown
# FAQ [Nome Categoria]

## [Sezione]

### [Domanda frequente]
[Risposta gentile]
```

---

## Sezioni OBBLIGATORIE da includere

### 1. ORARI E APERTURA
- Orari apertura (tipici officine italiane: 8:00-12:30, 14:30-18:30)
- Sabato aperto?
- Servizio fuori orario/emergenze
- Pausa pranzo

### 2. PRENOTAZIONI E APPUNTAMENTI
- Serve appuntamento o accesso diretto?
- Come prenotare (telefono, WhatsApp)
- Quanto anticipo per tagliando?
- Posso aspettare mentre lavorate?
- Tempi di attesa medi

### 3. SERVIZI E PREZZI
- **Tagliando** con fasce prezzo per cilindrata:
  - Utilitaria (€120-180)
  - Berlina (€150-220)
  - SUV/Premium (€200-350)
- **Revisione ministeriale** (€45-80)
- **Cambio gomme stagionale** (€40-80)
- **Equilibratura e convergenza** (€30-60)
- **Cambio olio + filtri** (€80-150)
- **Pastiglie freni** (€100-200)
- **Frizione** (€400-800)
- **Distribuzione** (€400-700)
- **Diagnosi computerizzata** (€30-50)
- **Ricarica clima** (€60-100)
- **Carrozzeria**: preventivo gratuito?

### 4. PAGAMENTI
- Metodi accettati
- Pagamento a rate disponibile?
- Finanziamento per riparazioni costose?
- Fattura per detrazione?
- Acconto richiesto?

### 5. TEMPISTICHE
- Quanto tempo per tagliando?
- Quanto tempo per cambio gomme?
- Quanto tempo per riparazioni carrozzeria?
- Auto sostitutiva disponibile?
- Servizio navetta?

### 6. RICAMBI E GARANZIE
- Usate ricambi originali o equivalenti?
- Posso portare i miei ricambi?
- Garanzia sui lavori (quanto dura?)
- Garanzia sui ricambi
- Cosa copre la garanzia?

### 7. PROBLEMI COMUNI E RECLAMI
- La riparazione non ha risolto il problema
- Il preventivo è aumentato
- Il lavoro ha richiesto più tempo del previsto
- Ho trovato un graffio/danno che prima non c'era
- Voglio un secondo parere
- Come fare reclamo

### 8. DOCUMENTI E PRATICHE
- Cosa portare per il tagliando?
- Cosa portare per la revisione?
- Fate pratiche assicurative (sinistri)?
- Perizia per assicurazione?
- Pratiche PRA (passaggi proprietà)?

### 9. DOMANDE SPECIFICHE AUTO
- Come capisco se devo fare il tagliando?
- Ogni quanto va fatta la revisione?
- Spia accesa, cosa faccio?
- Posso rimandare il tagliando?
- Differenza tagliando officina vs concessionaria?
- Gomme invernali obbligatorie?
- Tenete le gomme in deposito?

### 10. VEICOLI SPECIALI
- Lavorate su auto ibride/elettriche?
- Lavorate su moto/scooter?
- Furgoni e veicoli commerciali?
- Auto d'epoca?

### 11. EMERGENZE E SOCCORSO
- Servizio carro attrezzi?
- Assistenza stradale?
- Numero emergenze
- Orari reperibilità

### 12. FIDELITY E PROMOZIONI
- Sconti clienti abituali?
- Promozioni cambio gomme?
- Pacchetti manutenzione?
- Convenzioni aziendali?

---

## Output Atteso

Genera il file `faq_auto.md` completo, con almeno 50 domande/risposte.

Ogni risposta deve essere:
- Pronta per essere inviata via WhatsApp
- Rassicurante (l'auto in officina genera ansia!)
- Con info pratiche e prezzi indicativi

Esempio formato risposta:

```
### Quanto costa un tagliando per la mia auto?
Dipende dal modello! 🚗
- Utilitarie: €120-180
- Berline: €150-220
- SUV: €200-350

Scrivici marca e modello per un preventivo preciso e gratuito!
```
