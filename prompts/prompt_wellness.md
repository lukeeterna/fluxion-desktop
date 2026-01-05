# PROMPT: Genera FAQ per FLUXION-WELLNESS

## Contesto Sistema

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Palestre, centri fitness, studi di fisioterapia, SPA, centri benessere, personal trainer, studi pilates/yoga (1-15 dipendenti) in Italia.

---

## Istruzioni

Genera un file Markdown completo con TUTTE le FAQ tipiche per palestre e centri benessere italiani.

**Tono delle risposte:**
- Motivazionale ma non esagerato
- Accogliente, inclusivo (tutte le età e livelli)
- Usa emoji con moderazione (1-2 per risposta)
- Risposte brevi e dirette (max 3-4 frasi)
- Evita gergo fitness incomprensibile

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
- Orari apertura (tipici: 7:00-22:00 o 24h)
- Weekend e festivi
- Orari meno affollati (consiglio)
- Chiusure stagionali (agosto?)

### 2. ABBONAMENTI E PREZZI
- **Tipologie abbonamento:**
  - Giornaliero/ingresso singolo (€10-20)
  - Settimanale (€30-50)
  - Mensile (€40-80)
  - Trimestrale (€100-200)
  - Semestrale (€180-350)
  - Annuale (€300-600)
- Differenza abbonamento base vs premium
- Iscrizione/tessera obbligatoria? (€20-50)
- Sconti studenti/over 65?
- Abbonamento famiglia?
- Prova gratuita disponibile?

### 3. SERVIZI INCLUSI
- Cosa include l'abbonamento base?
- Sala pesi
- Corsi fitness (quali?)
- Piscina/SPA (se presente)
- Spogliatoi e docce
- Armadietti (inclusi o a pagamento?)
- Parcheggio

### 4. SERVIZI EXTRA (a pagamento)
- **Personal trainer** (€30-60/sessione)
- **Fisioterapia** (€40-80/seduta)
- **Massaggi** (€50-100)
- **Valutazione corporea** (€20-50)
- **Scheda personalizzata** (€30-50)
- Corsi speciali
- SPA/Sauna

### 5. PRIMA VISITA
- Cosa portare al primo ingresso?
- Serve certificato medico? (sì per attività agonistica)
- Tour della struttura?
- Scheda allenamento iniziale inclusa?
- Posso provare prima di abbonarmi?

### 6. CANCELLAZIONI E SOSPENSIONI
- Posso sospendere l'abbonamento (ferie, infortunio)?
- Quanto preavviso per disdetta?
- Rimborso se non uso la palestra?
- Trasferimento abbonamento ad altra persona?
- Cambio sede (se catena)?

### 7. CORSI E LEZIONI
- Calendario corsi disponibile?
- Serve prenotare per i corsi?
- Corsi per principianti?
- Zumba, Spinning, Yoga, Pilates, CrossFit...
- Limite partecipanti?
- Cosa succede se non riesco a venire?

### 8. PROBLEMI COMUNI E RECLAMI
- Attrezzatura rotta/occupata
- Troppa gente, non riesco ad allenarmi
- Spogliatoi sporchi
- Istruttore non disponibile
- Voglio disdire prima della scadenza
- Come fare reclamo

### 9. REGOLAMENTO
- Dress code (scarpe da ginnastica obbligatorie?)
- Asciugamano obbligatorio?
- Posso usare il telefono?
- Foto/video permessi?
- Comportamento in sala pesi
- Ospiti/amici ammessi?

### 10. DOMANDE SPECIFICHE FITNESS
- Sono principiante, da dove inizio?
- Quante volte a settimana dovrei venire?
- Meglio pesi o cardio?
- A che età posso iniziare palestra?
- Sono incinta, posso allenarmi?
- Ho problemi di schiena, cosa posso fare?
- Quanto tempo per vedere risultati?

### 11. FISIOTERAPIA (se applicabile)
- Serve prescrizione medica?
- Quante sedute servono?
- Rimborso mutua/assicurazione?
- Trattate [condizione specifica]?

### 12. FIDELITY E PROMOZIONI
- Programma fedeltà?
- Sconti per rinnovo anticipato?
- Promozioni in corso?
- Porta un amico?
- Convenzioni aziendali?

---

## Output Atteso

Genera il file `faq_wellness.md` completo, con almeno 50 domande/risposte.

Ogni risposta deve essere:
- Pronta per essere inviata via WhatsApp
- Motivazionale ma realistica
- Inclusiva (nessuno si deve sentire inadeguato)

Esempio formato risposta:

```
### Sono principiante, posso venire in palestra?
Assolutamente sì! 💪
La palestra è per tutti, non solo per gli esperti.
Il nostro staff ti aiuterà con una scheda adatta al tuo livello.
Vieni a fare una prova gratuita!
```
