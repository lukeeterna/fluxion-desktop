# PROMPT: Genera FAQ per FLUXION-BEAUTY

> **USA QUESTO PROMPT CON**: Perplexity Pro (Deep Research) o Claude 3.5 Sonnet
> **OUTPUT ATTESO**: File `faq_beauty.md` da salvare in `data/`

---

## PARTE 1: Contesto Sistema (per l'AI)

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Saloni di parrucchieri, barbieri, centri estetici, nail salon (1-15 dipendenti) in Italia.

---

## PARTE 2: Variabili Dinamiche dal Database

Le seguenti variabili verranno sostituite automaticamente dal sistema con i dati reali del cliente:

```
{{NOME_ATTIVITA}}     → Nome del salone (es: "Salone Maria")
{{INDIRIZZO}}         → Indirizzo completo
{{TELEFONO}}          → Numero telefono
{{WHATSAPP}}          → Numero WhatsApp
{{EMAIL}}             → Email

{{ORARI_SETTIMANALI}} → Orari apertura (es: "Mar-Sab 9:00-19:00")
{{GIORNO_CHIUSURA}}   → Giorno chiusura (es: "Domenica e Lunedì")

{{LISTA_SERVIZI}}     → Lista servizi con prezzi dal DB:
                        - {{servizio.nome}}: €{{servizio.prezzo}} ({{servizio.durata_minuti}} min)

{{LISTA_OPERATORI}}   → Lista operatori disponibili:
                        - {{operatore.nome}} - {{operatore.specializzazioni}}

{{METODI_PAGAMENTO}}  → Metodi accettati (es: "Contanti, Carte, Satispay")
{{LINK_PRENOTAZIONE}} → Link per prenotare (se presente)
```

---

## PARTE 3: Istruzioni per Generazione FAQ

**Tono delle risposte:**
- Gentile, cordiale, professionale
- Stile caldo Sud Italia (ma non eccessivo)
- Emoji con moderazione (1-2 per risposta)
- Risposte brevi (max 3-4 frasi)
- Usa le variabili {{VARIABILE}} dove appropriato

**Formato output:**

```markdown
# FAQ {{NOME_ATTIVITA}}

## [Sezione]

### [Domanda]
[Risposta con {{VARIABILI}} dove serve]
```

---

## PARTE 4: Deep Research Request (per Perplexity)

**IMPORTANTE**: Prima di generare le FAQ, effettua una ricerca approfondita su:

1. **Domande più frequenti** che i clienti fanno a saloni di bellezza in Italia (2024-2025)
2. **Problemi comuni** e lamentele tipiche del settore beauty
3. **Trend attuali**: trattamenti di tendenza, richieste emergenti
4. **Normative**: regole igieniche, allergie, patch test, GDPR
5. **Competitor**: cosa offrono i migliori saloni? Quali servizi extra?
6. **Stagionalità**: richieste diverse estate/inverno, cerimonie, feste

Integra questi insight nelle FAQ per coprire il maggior numero di casi reali.

---

## PARTE 5: Sezioni OBBLIGATORIE

### 1. INFORMAZIONI GENERALI
- Dove siete? Come raggiungervi?
- Orari apertura
- Parcheggio disponibile?
- Siete accessibili ai disabili?

### 2. PRENOTAZIONI
- Come prenoto? (usa {{WHATSAPP}}, {{TELEFONO}})
- Quanto anticipo serve?
- Posso prenotare online?
- Posso prenotare per più persone?
- Cosa succede se non trovo posto?

### 3. SERVIZI E PREZZI
- Che servizi offrite? (usa {{LISTA_SERVIZI}})
- Quanto costa [servizio]?
- Quanto dura [servizio]?
- Chi sono i vostri operatori? (usa {{LISTA_OPERATORI}})
- Fate consulenza gratuita?

### 4. PAGAMENTI
- Come posso pagare? (usa {{METODI_PAGAMENTO}})
- Accettate buoni regalo?
- Avete pacchetti/abbonamenti?
- Fate sconti?

### 5. CANCELLAZIONI E MODIFICHE
- Come cancello/sposto appuntamento?
- Quanto preavviso serve?
- C'è penale per no-show?
- Sono in ritardo, cosa faccio?

### 6. PROBLEMI E RECLAMI
- Non sono soddisfatto del risultato
- Il colore è diverso da come volevo
- Ho avuto reazione allergica
- Voglio un rimborso
- Come faccio reclamo?

### 7. DOMANDE TECNICHE SPECIFICHE
- Fate test allergia prima del colore?
- Devo lavare i capelli prima?
- Posso portare foto di riferimento?
- Quali prodotti usate?
- Vendete prodotti?

### 8. FIDELITY E PROMOZIONI
- Avete programma fedeltà?
- Sconti compleanno?
- Promozioni in corso?
- Porta un amico?

### 9. SITUAZIONI SPECIALI
- Accettate bambini?
- Servizi per spose/cerimonie?
- Servizi a domicilio?
- Trattate capelli afro/ricci/extension?

---

## PARTE 6: Esempio Output Atteso

```markdown
# FAQ {{NOME_ATTIVITA}}

## Informazioni Generali

### Dove vi trovate?
Siamo in {{INDIRIZZO}}! 📍
Facile da raggiungere, con parcheggio gratuito nelle vicinanze.

### Quali sono i vostri orari?
Siamo aperti {{ORARI_SETTIMANALI}}.
Chiusi {{GIORNO_CHIUSURA}}.

## Prenotazioni

### Come posso prenotare?
Puoi prenotare in diversi modi:
📱 WhatsApp: {{WHATSAPP}}
📞 Telefono: {{TELEFONO}}
Ti consigliamo di prenotare con 2-3 giorni di anticipo!

## Servizi e Prezzi

### Quanto costa un taglio?
Ecco i nostri prezzi:
{{LISTA_SERVIZI}}

Per un preventivo personalizzato, scrivici!

## Problemi

### Non sono soddisfatto del taglio, cosa posso fare?
Ci dispiace molto! 😔
La tua soddisfazione è la nostra priorità.
Contattaci entro 7 giorni e troveremo insieme una soluzione.
Chiamaci al {{TELEFONO}} o scrivici su WhatsApp.
```

---

## Output Finale

Genera un file `faq_beauty.md` completo con:
- Minimo 60 domande/risposte
- Tutte le sezioni obbligatorie
- Variabili {{}} dove i dati sono dinamici
- Risposte pronte per WhatsApp
- Copertura problemi/reclami realistici
