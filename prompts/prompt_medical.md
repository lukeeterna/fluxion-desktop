# PROMPT: Genera FAQ per FLUXION-MEDICAL

## Contesto Sistema

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Studi medici, studi dentistici, poliambulatori, fisioterapisti, osteopati, nutrizionisti, psicologi (1-15 dipendenti) in Italia.

**IMPORTANTE**: Le risposte NON devono MAI dare consigli medici. Devono sempre invitare a prenotare una visita per valutazione professionale.

---

## Istruzioni

Genera un file Markdown completo con TUTTE le FAQ tipiche per studi medici/dentistici italiani.

**Tono delle risposte:**
- Professionale ma rassicurante
- Empatico (le persone hanno paura/ansia)
- Usa emoji con MOLTA moderazione (max 1 per risposta)
- Risposte brevi e dirette
- Mai allarmista, mai minimizzante
- Rispetta privacy e GDPR

**Formato output richiesto:**

```markdown
# FAQ [Nome Categoria]

## [Sezione]

### [Domanda frequente]
[Risposta gentile]
```

---

## Sezioni OBBLIGATORIE da includere

### 1. ORARI E CONTATTI
- Orari studio (tipici: 9:00-13:00, 15:00-19:00)
- Giorni di apertura
- Urgenze fuori orario
- Numero emergenze
- Email per documentazione

### 2. PRENOTAZIONI
- Come prenotare (telefono, WhatsApp, online)
- Quanto anticipo serve?
- Posso prenotare per familiari?
- Lista d'attesa
- Disdetta appuntamento

### 3. PRIMA VISITA
- Cosa portare:
  - Tessera sanitaria
  - Codice fiscale
  - Referti/esami precedenti
  - Lista farmaci in uso
- Durata prima visita
- Costo prima visita
- Arrivare in anticipo?

### 4. TARIFFE E PAGAMENTI
- **Visite specialistiche** (€80-150)
- **Visita dentistica** (€50-100)
- **Igiene dentale** (€60-100)
- **Otturazione** (€80-150)
- **Estrazione** (€100-200)
- **Impianto dentale** (€800-2000)
- **Ortodonzia** (€2000-5000)
- Convenzioni SSN?
- Assicurazioni convenzionate?
- Pagamento a rate?
- Finanziamento?
- Fattura per detrazione 19%?

### 5. CANCELLAZIONI
- Politica cancellazione (24-48h)
- Penale per mancato preavviso?
- Come spostare appuntamento?
- Ritardo: quanto tollerate?

### 6. PAURA E ANSIA (specialmente dentista)
- Ho paura del dentista, cosa fate?
- Sedazione cosciente disponibile?
- Anestesia fa male?
- Posso portare qualcuno con me?
- Tecniche per ridurre l'ansia

### 7. DOMANDE SPECIFICHE DENTISTA
- Ogni quanto fare controllo?
- Ogni quanto igiene dentale?
- Sbiancamento denti (costo, durata)
- Dente che fa male, è urgente?
- Apparecchio: quanto dura?
- Invisalign disponibile?
- Impianti: sono dolorosi?
- Faccette dentali

### 8. DOMANDE SPECIFICHE MEDICO
- Tempo attesa referti
- Prescrizioni/ricette online?
- Certificati medici
- Visite domiciliari?
- Teleconsulto disponibile?

### 9. EMERGENZE
- Ho dolore forte, cosa faccio?
- Dente rotto/caduto
- Gonfiore improvviso
- Sanguinamento
- Quando andare al pronto soccorso vs studio

### 10. BAMBINI
- A che età prima visita dentistica?
- Come preparare il bambino?
- Sedazione per bambini?
- Ortodonzia pediatrica

### 11. PRIVACY E DOCUMENTAZIONE
- Come richiedere cartella clinica?
- Conservazione dati (GDPR)
- Trasferimento documentazione altro studio
- Consenso informato

### 12. PROBLEMI E RECLAMI
- Il trattamento non ha funzionato
- Ho ancora dolore dopo la cura
- Non sono soddisfatto del risultato estetico
- Complicazioni post-intervento
- Come fare reclamo formale

### 13. CONVENZIONI E AGEVOLAZIONI
- Convenzioni con mutue/fondi sanitari
- SSN: cosa passa?
- Detrazioni fiscali
- Agevolazioni per anziani/disabili

---

## Output Atteso

Genera il file `faq_medical.md` completo, con almeno 50 domande/risposte.

Ogni risposta deve essere:
- Pronta per essere inviata via WhatsApp
- Rassicurante (pazienti ansiosi!)
- MAI diagnosi o consigli medici
- Sempre invito a visita per valutazione

Esempio formato risposta:

```
### Ho paura del dentista, come posso fare?
Capisco perfettamente, non sei solo/a!
Il nostro team è specializzato nel trattare pazienti ansiosi.
Offriamo sedazione cosciente e tecniche di rilassamento.
Prenota una prima visita conoscitiva, parleremo insieme senza alcun obbligo.
```
