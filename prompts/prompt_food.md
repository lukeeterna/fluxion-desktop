# PROMPT: Genera FAQ per FLUXION-FOOD

## Contesto Sistema

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Ristoranti, pizzerie, trattorie, bar, pasticcerie, gelaterie, pub, enoteche (1-15 dipendenti) in Italia.

---

## Istruzioni

Genera un file Markdown completo con TUTTE le FAQ tipiche per ristoranti/bar italiani.

**Tono delle risposte:**
- Accogliente, caloroso, "come a casa"
- Stile conviviale Sud Italia
- Usa emoji con moderazione (1-2 per risposta, tema food)
- Risposte brevi che invogliano a venire
- Mai freddo o burocratico

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
- Orari pranzo (tipico: 12:00-15:00)
- Orari cena (tipico: 19:00-23:00)
- Giorno di chiusura
- Cucina: fino a che ora ordini?
- Festivi e vigilie
- Ferie estive/invernali

### 2. PRENOTAZIONI
- Serve prenotare?
- Come prenotare (telefono, WhatsApp)
- Quanto anticipo per weekend?
- Prenotazione gruppi (quante persone?)
- Caparra richiesta per gruppi?
- Cancellazione prenotazione

### 3. MENU E PREZZI
- Menu disponibile online?
- Range prezzi:
  - Antipasti (€8-15)
  - Primi (€10-18)
  - Secondi (€12-25)
  - Pizza (€7-15)
  - Dolci (€5-10)
  - Caffè/bevande
- Menu degustazione?
- Menu pranzo/business lunch?
- Menu bambini?
- Porzioni abbondanti?

### 4. DIETE E ALLERGIE
- Opzioni vegetariane?
- Opzioni vegane?
- Piatti senza glutine?
- Gestione allergeni (obbligatorio per legge)
- Posso chiedere modifiche ai piatti?
- Intolleranza lattosio?

### 5. PAGAMENTI
- Metodi accettati (contanti, carte, Satispay)
- Ticket restaurant?
- Pagamento separato (comande divise)?
- Mancia: uso italiano (non obbligatoria)

### 6. ASPORTO E DELIVERY
- Fate asporto?
- Consegna a domicilio?
- App delivery (JustEat, Deliveroo, Glovo)?
- Minimo ordine per delivery?
- Tempi di consegna?
- Packaging eco-friendly?

### 7. SERVIZI SPECIALI
- Tavoli all'aperto/giardino?
- Sala privata per eventi?
- Feste di compleanno?
- Cene aziendali?
- Catering esterno?
- Torta personalizzata?

### 8. BAMBINI E FAMIGLIE
- Seggioloni disponibili?
- Menu bambini?
- Fasciatoio?
- Spazio giochi?
- Bambini benvenuti a cena tardi?

### 9. ANIMALI
- Cani ammessi?
- Solo dehors o anche interno?
- Ciotola acqua disponibile?

### 10. ACCESSIBILITÀ E COMFORT
- Parcheggio?
- Accessibile ai disabili?
- Aria condizionata/riscaldamento?
- Wi-Fi gratuito?
- Prese per caricare telefono?

### 11. DOMANDE SUL LOCALE
- Quanti posti avete?
- C'è rumore/musica?
- Dress code?
- Posso vedere il locale prima di prenotare?

### 12. PROBLEMI E RECLAMI
- Il piatto non era come mi aspettavo
- Attesa troppo lunga
- Conto sbagliato
- Ho trovato qualcosa nel piatto
- Servizio scortese
- Come fare reclamo

### 13. PRODOTTI E SPECIALITÀ
- Quali sono i piatti tipici/signature?
- Ingredienti locali/km zero?
- Vini: carta vini disponibile?
- Birre artigianali?
- Prodotti vendita (olio, vino, conserve)?

### 14. EVENTI E PROMOZIONI
- Serate a tema?
- Musica dal vivo?
- Happy hour?
- Promozioni in corso?
- Programma fedeltà?

---

## Output Atteso

Genera il file `faq_food.md` completo, con almeno 50 domande/risposte.

Ogni risposta deve essere:
- Pronta per essere inviata via WhatsApp
- Che faccia venire fame/voglia di venire!
- Accogliente come un invito a casa

Esempio formato risposta:

```
### Avete opzioni senza glutine?
Certamente! 🍝
Abbiamo diversi piatti naturalmente senza glutine e pasta gluten-free.
Avvisaci quando prenoti così lo chef preparerà tutto con la massima attenzione.
Ti aspettiamo!
```
