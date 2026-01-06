# PROMPT: Genera FAQ per FLUXION-MEDICAL

> **USA QUESTO PROMPT CON**: Perplexity Pro (Deep Research) o Claude 3.5 Sonnet
> **OUTPUT ATTESO**: File `faq_medical.md` da salvare in `data/`

---

## PARTE 1: Contesto Sistema (per l'AI)

Stai generando un file FAQ per **FLUXION**, un gestionale desktop per PMI italiane.

**Stack tecnico:**
- Desktop app: Tauri 2.x + React 19 + TypeScript
- Database: SQLite locale
- WhatsApp: Automazione locale con whatsapp-web.js (NO API a pagamento)
- RAG: Le FAQ verranno usate come knowledge base per rispondere automaticamente ai clienti via WhatsApp
- Voice Agent: Le stesse FAQ alimenteranno un assistente vocale (Groq Whisper + Piper TTS)

**Target**: Studi medici, studi dentistici, poliambulatori, fisioterapisti, osteopati, nutrizionisti, psicologi (1-15 dipendenti) in Italia.

**⚠️ IMPORTANTE**: Le risposte NON devono MAI dare consigli medici o diagnosi.
Devono SEMPRE invitare a prenotare una visita per valutazione professionale.

---

## PARTE 2: Variabili Dinamiche dal Database

**⚠️ REGOLA FONDAMENTALE**: MAI inserire dati fissi (prezzi, orari, servizi).
Usa SOLO variabili {{}} che verranno sostituite dal DB.
Se un dato non è disponibile, la risposta deve invitare a contattare un operatore umano.

```
{{NOME_ATTIVITA}}     → Nome studio (es: "Studio Dentistico Bianchi")
{{INDIRIZZO}}         → Indirizzo completo
{{TELEFONO}}          → Numero telefono
{{WHATSAPP}}          → Numero WhatsApp
{{EMAIL}}             → Email
{{PEC}}               → PEC (se presente)

{{ORARI_SETTIMANALI}} → Orari apertura
{{GIORNO_CHIUSURA}}   → Giorno chiusura

{{LISTA_SERVIZI}}     → Lista visite/trattamenti con prezzi dal DB:
                        - {{servizio.nome}}: €{{servizio.prezzo}} ({{servizio.durata_minuti}} min)

{{LISTA_OPERATORI}}   → Lista medici/specialisti:
                        - Dr./Dott.ssa {{operatore.nome}} - {{operatore.specializzazioni}}

{{METODI_PAGAMENTO}}  → Metodi accettati
{{CONVENZIONI_SSN}}   → Convenzioni SSN (Sì/No + dettagli)
{{CONVENZIONI_MUTUE}} → Lista mutue/assicurazioni convenzionate
{{NUMERO_EMERGENZE}}  → Numero per urgenze (se diverso)
```

**Se un dato non è nel DB**, rispondi:
> "Per questa informazione la invitiamo a contattarci al {{TELEFONO}} o su WhatsApp {{WHATSAPP}}. La nostra segreteria le risponderà al più presto."

**Se la domanda richiede valutazione medica**, rispondi:
> "Per una valutazione accurata è necessaria una visita con il nostro specialista. Prenoti un appuntamento e saremo lieti di aiutarla."

---

## PARTE 3: Istruzioni per Generazione FAQ

**Tono delle risposte:**
- Professionale ma rassicurante
- Empatico (pazienti spesso ansiosi)
- Emoji con MOLTA moderazione (max 1)
- Risposte brevi ma complete
- MAI allarmista, MAI minimizzante
- MAI diagnosi o consigli medici

**Formato output:**

```markdown
# FAQ {{NOME_ATTIVITA}}

## [Sezione]

### [Domanda]
[Risposta con {{VARIABILI}} - MAI consigli medici]
```

---

## PARTE 4: Deep Research Request (per Perplexity)

**IMPORTANTE**: Prima di generare le FAQ, effettua una ricerca approfondita su:

1. **Domande più frequenti** che i pazienti fanno a studi medici/dentistici in Italia
2. **Paure comuni**: paura del dolore, aghi, dentista, diagnosi
3. **Normative**: GDPR sanitario, consenso informato, cartella clinica
4. **Aspetti economici**: detrazioni fiscali 19%, convenzioni, pagamenti rateali
5. **Dentista specifico**: sedazione, anestesia, bambini, impianti, ortodonzia
6. **Emergenze**: quando è urgente vs quando può aspettare
7. **Privacy**: accesso ai dati, trasferimento cartella, GDPR

Integra questi insight nelle FAQ per coprire il maggior numero di casi reali.

---

## PARTE 5: Sezioni OBBLIGATORIE

### 1. INFORMAZIONI GENERALI
- Dove siete?
- Orari apertura (usa {{ORARI_SETTIMANALI}})
- Come raggiungervi?
- Parcheggio disponibile?

### 2. PRENOTAZIONI
- Come prenoto? (usa {{WHATSAPP}}, {{TELEFONO}})
- Quanto anticipo serve?
- Posso prenotare per familiari?
- Lista d'attesa?
- Come disdico?

### 3. PRIMA VISITA
- Cosa devo portare?
- Quanto dura la prima visita?
- Quanto costa? (usa {{LISTA_SERVIZI}})
- Devo venire a digiuno?

### 4. TARIFFE E PAGAMENTI
- Quanto costano le visite? (usa {{LISTA_SERVIZI}})
- Come posso pagare? (usa {{METODI_PAGAMENTO}})
- Convenzioni SSN? (usa {{CONVENZIONI_SSN}})
- Assicurazioni/mutue? (usa {{CONVENZIONI_MUTUE}})
- Pagamento a rate?
- Fattura per detrazione fiscale?

### 5. PAURA E ANSIA
- Ho paura del dentista/degli aghi
- Fate sedazione?
- L'anestesia fa male?
- Posso portare qualcuno con me?

### 6. EMERGENZE
- Ho dolore forte, cosa faccio?
- È urgente o può aspettare?
- Numero emergenze (usa {{NUMERO_EMERGENZE}})
- Orari reperibilità?

### 7. DOMANDE SPECIFICHE DENTISTA
- Ogni quanto devo fare controllo?
- Sbiancamento denti
- Impianti dentali
- Apparecchio/Invisalign
- Dente che fa male

### 8. DOMANDE SPECIFICHE MEDICO
- Tempo attesa referti?
- Prescrizioni online?
- Certificati medici?
- Visite domiciliari?

### 9. BAMBINI
- A che età prima visita?
- Come preparo mio figlio?
- Avete esperienza con bambini?

### 10. PRIVACY E DOCUMENTI
- Come richiedo la mia cartella?
- Trasferimento ad altro studio?
- I miei dati sono al sicuro?

### 11. RECLAMI
- Non sono soddisfatto del trattamento
- Ho ancora dolore dopo la cura
- Come faccio reclamo?

---

## PARTE 6: Esempio Output Atteso

```markdown
# FAQ {{NOME_ATTIVITA}}

## Informazioni Generali

### Dove vi trovate?
Siamo in {{INDIRIZZO}}.
{{#if HA_PARCHEGGIO}}Parcheggio disponibile per i pazienti.{{/if}}

### Quali sono i vostri orari?
{{ORARI_SETTIMANALI}}
Chiusi {{GIORNO_CHIUSURA}}.

## Prenotazioni

### Come posso prenotare una visita?
Può prenotare in diversi modi:
📱 WhatsApp: {{WHATSAPP}}
📞 Telefono: {{TELEFONO}}
📧 Email: {{EMAIL}}

La nostra segreteria le confermerà l'appuntamento.

## Paura e Ansia

### Ho molta paura del dentista, cosa posso fare?
Comprendiamo perfettamente, non è solo/a!
Il nostro team è formato per accogliere pazienti ansiosi.
Offriamo sedazione cosciente e tecniche di rilassamento.
Prenoti una prima visita conoscitiva: parleremo insieme senza alcun obbligo.

## Emergenze

### Ho un forte dolore, cosa devo fare?
In caso di dolore acuto, ci contatti immediatamente:
📞 {{NUMERO_EMERGENZE}}

Se siamo chiusi e il dolore è insopportabile, si rechi al Pronto Soccorso più vicino.
Non assuma farmaci senza aver consultato un medico.

## Tariffe

### Quanto costa una visita?
Le nostre tariffe:
{{LISTA_SERVIZI}}

Per un preventivo personalizzato, prenoti una prima visita.
Rilasciamo fattura per detrazione fiscale del 19%.
```

---

## Output Finale

Genera un file `faq_medical.md` completo con:
- Minimo 60 domande/risposte
- Tutte le sezioni obbligatorie
- SOLO variabili {{}} per dati dinamici
- MAI consigli medici o diagnosi
- Tono professionale e rassicurante
- Se dato non disponibile → "contatta segreteria"
