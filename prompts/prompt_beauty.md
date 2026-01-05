# PROMPT: Genera FAQ per FLUXION-BEAUTY

## Contesto Sistema

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Saloni di parrucchieri, barbieri, centri estetici, nail salon (1-15 dipendenti) in Italia.

---

## Istruzioni

Genera un file Markdown completo con TUTTE le FAQ tipiche per un salone di bellezza italiano.

**Tono delle risposte:**
- Gentile, cordiale, professionale
- Stile Sud Italia (caldo ma non eccessivo)
- Usa emoji con moderazione (1-2 per risposta)
- Risposte brevi e dirette (max 3-4 frasi)
- Mai aggressivo o freddo

**Formato output richiesto:**

```markdown
# FAQ [Nome Categoria]

## [Sezione]

### [Domanda frequente]
[Risposta gentile]

### [Altra domanda]
[Risposta]
```

---

## Sezioni OBBLIGATORIE da includere

### 1. ORARI E APERTURA
- Orari apertura (tipici saloni italiani)
- Giorni di chiusura
- Orari festivi
- Pausa pranzo (se applicabile)

### 2. PRENOTAZIONI
- Come prenotare (telefono, WhatsApp, di persona)
- Quanto anticipo serve
- Prenotazione online disponibile?
- Posso prenotare per più persone?
- Prenotazione last-minute

### 3. SERVIZI E PREZZI
- Lista servizi con fasce prezzo Italia 2025:
  - Taglio uomo (€15-25)
  - Taglio donna (€25-45)
  - Piega (€15-25)
  - Colore (€40-80)
  - Meches/Balayage (€60-120)
  - Trattamenti (cheratina, botox capelli: €50-100)
  - Barba (€10-20)
  - Manicure/Pedicure (€20-40)
  - Extension ciglia (€80-150)
- Durata media servizi
- Listino prezzi disponibile?
- Prezzi bambini/anziani

### 4. PAGAMENTI
- Metodi accettati (contanti, carte, Satispay, PayPal)
- Si accettano buoni/voucher?
- Pagamento anticipato richiesto?
- Possibilità di pagare a rate?

### 5. CANCELLAZIONI E MODIFICHE
- Politica cancellazione (entro 24h?)
- Come modificare appuntamento
- Penali per no-show
- Cosa succede se arrivo in ritardo?

### 6. PROBLEMI COMUNI E RECLAMI
- Non sono soddisfatto del taglio/colore
- Il colore è venuto diverso da come volevo
- Ho avuto una reazione allergica
- Il trattamento non ha funzionato
- Voglio un rimborso
- Come fare un reclamo

### 7. DOMANDE SPECIFICHE SALONE
- Devo lavare i capelli prima di venire?
- Posso portare foto di riferimento?
- Fate consulenza gratuita?
- Allergie e test patch (colore)
- Prodotti usati (marche)
- Vendete prodotti?
- Sconti per clienti abituali?

### 8. FIDELITY E PROMOZIONI
- Programma fedeltà (tessera punti)
- Sconti compleanno
- Pacchetti prepagati
- Promozioni in corso
- Porta un amico

### 9. ACCESSIBILITÀ E COMFORT
- Parcheggio disponibile?
- Accessibile ai disabili?
- Wi-Fi gratuito?
- Posso portare bambini?
- C'è una sala d'attesa?
- Offrite bevande (caffè, acqua)?

### 10. EMERGENZE E CONTATTI
- Numero per urgenze
- Email per comunicazioni
- Social media
- Come raggiungervi

---

## Output Atteso

Genera il file `faq_beauty.md` completo, con almeno 50 domande/risposte.

Ogni risposta deve essere:
- Pronta per essere inviata via WhatsApp
- Gentile e rassicurante
- Con info pratiche concrete

Esempio formato risposta:

```
### Quanto costa un taglio donna?
Il taglio donna parte da €30 e varia in base alla lunghezza e complessità.
Per un preventivo preciso, scrivici una foto dei tuoi capelli! ✂️
Prenota qui: [link]
```
