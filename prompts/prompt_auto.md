# PROMPT: Genera FAQ per FLUXION-AUTO

> **USA QUESTO PROMPT CON**: Perplexity Pro (Deep Research) o Claude 3.5 Sonnet
> **OUTPUT ATTESO**: File `faq_auto.md` da salvare in `data/`

---

## PARTE 1: Contesto Sistema (per l'AI)

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Officine meccaniche, elettrauto, carrozzerie, gommisti, autolavaggi (1-15 dipendenti) in Italia.

---

## PARTE 2: Variabili Dinamiche dal Database

Le seguenti variabili verranno sostituite automaticamente dal sistema con i dati reali del cliente:

```
{{NOME_ATTIVITA}}     → Nome officina (es: "Autofficina Rossi")
{{INDIRIZZO}}         → Indirizzo completo
{{TELEFONO}}          → Numero telefono
{{WHATSAPP}}          → Numero WhatsApp
{{EMAIL}}             → Email

{{ORARI_SETTIMANALI}} → Orari apertura (es: "Lun-Ven 8:00-12:30, 14:30-18:30")
{{GIORNO_CHIUSURA}}   → Giorno chiusura (es: "Domenica")
{{SABATO_ORARI}}      → Orari sabato (es: "8:00-12:30" o "Chiuso")

{{LISTA_SERVIZI}}     → Lista servizi con prezzi dal DB:
                        - {{servizio.nome}}: €{{servizio.prezzo}} ({{servizio.durata_minuti}} min)

{{LISTA_OPERATORI}}   → Lista meccanici/tecnici:
                        - {{operatore.nome}} - {{operatore.specializzazioni}}

{{METODI_PAGAMENTO}}  → Metodi accettati
{{AUTO_SOSTITUTIVA}}  → Disponibilità auto sostitutiva (Sì/No)
{{CARRO_ATTREZZI}}    → Servizio carro attrezzi (Sì/No + numero)
```

---

## PARTE 3: Istruzioni per Generazione FAQ

**Tono delle risposte:**
- Competente, rassicurante, pratico
- Mai tecnicismi incomprensibili
- Emoji con moderazione (1-2 per risposta, tipo 🚗🔧)
- Risposte brevi (max 3-4 frasi)
- Rassicurante (l'auto in officina genera ansia!)

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

1. **Domande più frequenti** che i clienti fanno alle officine in Italia (2024-2025)
2. **Paure e preoccupazioni** comuni (costi nascosti, tempi, fregature)
3. **Normative**: revisione obbligatoria, tagliando, gomme invernali, AdBlue
4. **Trend**: auto ibride/elettriche, ADAS, diagnostica moderna
5. **Problemi comuni**: spie accese, rumori, consumi anomali
6. **Stagionalità**: cambio gomme, clima, batteria inverno
7. **Garanzie**: cosa copre, cosa no, ricambi originali vs equivalenti

Integra questi insight nelle FAQ per coprire il maggior numero di casi reali.

---

## PARTE 5: Sezioni OBBLIGATORIE

### 1. INFORMAZIONI GENERALI
- Dove siete? Come raggiungervi?
- Orari apertura (usa {{ORARI_SETTIMANALI}})
- Aprite il sabato? (usa {{SABATO_ORARI}})
- Avete servizio emergenze/fuori orario?

### 2. PRENOTAZIONI
- Serve appuntamento o posso venire direttamente?
- Come prenoto? (usa {{WHATSAPP}}, {{TELEFONO}})
- Quanto anticipo serve per tagliando/revisione?
- Posso aspettare mentre lavorate?
- Auto sostitutiva disponibile? (usa {{AUTO_SOSTITUTIVA}})

### 3. SERVIZI E PREZZI
- Che servizi offrite? (usa {{LISTA_SERVIZI}})
- Quanto costa tagliando per [tipo auto]?
- Quanto costa revisione?
- Fate diagnosi computerizzata?
- Lavorate su auto ibride/elettriche?
- Fate carrozzeria?

### 4. TEMPISTICHE
- Quanto tempo per tagliando?
- Quanto tempo per cambio gomme?
- Quanto tempo per riparazioni?
- Mi avvisate quando è pronta?

### 5. PAGAMENTI E PREVENTIVI
- Come posso pagare? (usa {{METODI_PAGAMENTO}})
- Preventivo gratuito?
- Pagamento a rate disponibile?
- Fattura per detrazione?

### 6. RICAMBI E GARANZIE
- Usate ricambi originali o equivalenti?
- Posso portare i miei ricambi?
- Quanto dura la garanzia sui lavori?
- Cosa copre la garanzia?

### 7. EMERGENZE E SOCCORSO
- Avete carro attrezzi? (usa {{CARRO_ATTREZZI}})
- Cosa faccio se resto in panne?
- Numero per emergenze?

### 8. PROBLEMI COMUNI
- Ho una spia accesa, cosa faccio?
- L'auto fa un rumore strano
- Consumo anomalo di olio/carburante
- Batteria scarica
- Climatizzatore non raffredda

### 9. DOCUMENTI
- Cosa devo portare per tagliando?
- Cosa devo portare per revisione?
- Fate pratiche assicurative?

### 10. RECLAMI
- Il problema non è stato risolto
- Il preventivo è aumentato
- Ho trovato un danno che prima non c'era
- Come faccio reclamo?

---

## PARTE 6: Esempio Output Atteso

```markdown
# FAQ {{NOME_ATTIVITA}}

## Informazioni Generali

### Dove vi trovate?
Siamo in {{INDIRIZZO}}! 🚗
Ampio parcheggio disponibile per i clienti.

### Quali sono i vostri orari?
{{ORARI_SETTIMANALI}}
Sabato: {{SABATO_ORARI}}
Chiusi {{GIORNO_CHIUSURA}}.

## Prenotazioni

### Serve appuntamento?
Per tagliandi e revisioni ti consigliamo di prenotare.
Per controlli veloci puoi passare direttamente!
📱 WhatsApp: {{WHATSAPP}}
📞 Telefono: {{TELEFONO}}

## Servizi

### Quanto costa il tagliando?
Dipende dal modello! Il prezzo include:
{{LISTA_SERVIZI}}

Scrivici marca, modello e km per un preventivo preciso e gratuito! 🔧

## Emergenze

### Sono rimasto in panne, cosa faccio?
Niente panico! 🆘
Chiamaci al {{TELEFONO}}, attiviamo subito il carro attrezzi.
Servizio disponibile anche fuori orario.
```

---

## Output Finale

Genera un file `faq_auto.md` completo con:
- Minimo 60 domande/risposte
- Tutte le sezioni obbligatorie
- Variabili {{}} dove i dati sono dinamici
- Risposte rassicuranti (ridurre ansia cliente)
- Copertura problemi tecnici comuni semplificati
