# PROMPT: Genera FAQ per FLUXION-WELLNESS

> **USA QUESTO PROMPT CON**: Perplexity Pro (Deep Research) o Claude 3.5 Sonnet
> **OUTPUT ATTESO**: File `faq_wellness.md` da salvare in `data/`

---

## PARTE 1: Contesto Sistema (per l'AI)

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Palestre, centri fitness, fisioterapisti, SPA, personal trainer, studi pilates/yoga (1-15 dipendenti) in Italia.

---

## PARTE 2: Variabili Dinamiche dal Database

**⚠️ REGOLA FONDAMENTALE**: MAI inserire dati fissi (prezzi, orari, servizi).
Usa SOLO variabili {{}} che verranno sostituite dal DB.
Se un dato non è disponibile, la risposta deve invitare a contattare un operatore umano.

```
{{NOME_ATTIVITA}}     → Nome centro (es: "Fitness Club Roma")
{{INDIRIZZO}}         → Indirizzo completo
{{TELEFONO}}          → Numero telefono
{{WHATSAPP}}          → Numero WhatsApp
{{EMAIL}}             → Email

{{ORARI_SETTIMANALI}} → Orari apertura
{{GIORNO_CHIUSURA}}   → Giorno chiusura

{{LISTA_SERVIZI}}     → Lista servizi/corsi con prezzi dal DB:
                        - {{servizio.nome}}: €{{servizio.prezzo}} ({{servizio.durata_minuti}} min)

{{LISTA_ABBONAMENTI}} → Tipi abbonamento dal DB:
                        - {{abbonamento.nome}}: €{{abbonamento.prezzo}}/{{abbonamento.durata}}

{{LISTA_OPERATORI}}   → Lista trainer/fisioterapisti:
                        - {{operatore.nome}} - {{operatore.specializzazioni}}

{{METODI_PAGAMENTO}}  → Metodi accettati
{{HA_PISCINA}}        → Sì/No
{{HA_SPA}}            → Sì/No
{{HA_PARCHEGGIO}}     → Sì/No
```

**Se un dato non è nel DB**, rispondi:
> "Per questa informazione ti consiglio di contattarci direttamente al {{TELEFONO}} o su WhatsApp {{WHATSAPP}}. Un nostro operatore ti risponderà subito!"

---

## PARTE 3: Istruzioni per Generazione FAQ

**Tono delle risposte:**
- Motivazionale ma non esagerato
- Inclusivo (tutte le età e livelli)
- Emoji con moderazione (💪🏋️‍♀️)
- Risposte brevi (max 3-4 frasi)
- MAI giudicante, MAI escludente

**Formato output:**

```markdown
# FAQ {{NOME_ATTIVITA}}

## [Sezione]

### [Domanda]
[Risposta con {{VARIABILI}} - se dato mancante, invita a contattare operatore]
```

---

## PARTE 4: Deep Research Request (per Perplexity)

**IMPORTANTE**: Prima di generare le FAQ, effettua una ricerca approfondita su:

1. **Domande più frequenti** che i clienti fanno a palestre/centri benessere in Italia
2. **Barriere all'ingresso**: paura di essere giudicati, non sapersi muovere, età
3. **Normative**: certificato medico, assicurazione, GDPR
4. **Trend fitness 2024-2025**: functional training, HIIT, recovery, mindfulness
5. **Problemi comuni**: affollamento, attrezzature occupate, igiene
6. **Fisioterapia**: domande su rimborsi, prescrizioni, numero sedute
7. **Abbonamenti**: sospensioni, disdette, trasferimenti, rimborsi

Integra questi insight nelle FAQ per coprire il maggior numero di casi reali.

---

## PARTE 5: Sezioni OBBLIGATORIE

### 1. INFORMAZIONI GENERALI
- Dove siete?
- Orari apertura (usa {{ORARI_SETTIMANALI}})
- Parcheggio? (usa {{HA_PARCHEGGIO}})
- Accessibilità disabili?

### 2. ABBONAMENTI E PREZZI
- Che abbonamenti avete? (usa {{LISTA_ABBONAMENTI}})
- Posso fare una prova gratuita?
- Sconti studenti/anziani?
- Come funziona l'iscrizione?

### 3. SERVIZI
- Che servizi offrite? (usa {{LISTA_SERVIZI}})
- Avete personal trainer? (usa {{LISTA_OPERATORI}})
- Avete piscina/SPA? (usa {{HA_PISCINA}}, {{HA_SPA}})
- Che corsi fate?

### 4. PRIMA VISITA
- Cosa devo portare?
- Serve certificato medico?
- Come funziona il primo giorno?
- Mi fate vedere la struttura?

### 5. PAGAMENTI
- Come posso pagare? (usa {{METODI_PAGAMENTO}})
- Pagamento a rate?
- Posso sospendere l'abbonamento?
- Come disdico?

### 6. CORSI E PRENOTAZIONI
- Come prenoto un corso?
- Serve prenotare per la sala pesi?
- Posso portare un amico?
- Orari meno affollati?

### 7. PROBLEMI E RECLAMI
- Attrezzatura rotta/sporca
- Spogliatoi non puliti
- Troppa gente
- Voglio disdire anticipatamente
- Come faccio reclamo?

### 8. DOMANDE DA PRINCIPIANTI
- Non ho mai fatto palestra, posso venire?
- Ho paura di essere giudicato
- A che età si può iniziare?
- Quante volte devo venire?

### 9. FISIOTERAPIA (se applicabile)
- Serve prescrizione?
- Quante sedute servono?
- Rimborso mutua/assicurazione?

---

## PARTE 6: Esempio Output Atteso

```markdown
# FAQ {{NOME_ATTIVITA}}

## Informazioni Generali

### Dove vi trovate?
Siamo in {{INDIRIZZO}}! 📍
{{#if HA_PARCHEGGIO}}Parcheggio gratuito disponibile.{{/if}}

### Quali sono i vostri orari?
{{ORARI_SETTIMANALI}}
Chiusi {{GIORNO_CHIUSURA}}.

## Abbonamenti

### Che abbonamenti avete?
Ecco le nostre opzioni:
{{LISTA_ABBONAMENTI}}

Per scegliere quello giusto per te, contattaci! Ti aiutiamo a trovare la soluzione migliore.

## Prima Visita

### Non ho mai fatto palestra, posso venire lo stesso?
Assolutamente sì! 💪
Siamo qui per tutti, dai principianti agli esperti.
Il nostro staff ti accoglierà e ti guiderà passo passo.
Nessun giudizio, solo supporto!

## Problemi

### Voglio disdire l'abbonamento, come faccio?
Per le disdette contatta direttamente il nostro staff:
📱 WhatsApp: {{WHATSAPP}}
📞 Telefono: {{TELEFONO}}
Ti spiegheremo la procedura e le eventuali condizioni.
```

---

## Output Finale

Genera un file `faq_wellness.md` completo con:
- Minimo 60 domande/risposte
- Tutte le sezioni obbligatorie
- SOLO variabili {{}} per dati dinamici
- Se dato non disponibile → "contatta operatore"
- Tono inclusivo e motivazionale
