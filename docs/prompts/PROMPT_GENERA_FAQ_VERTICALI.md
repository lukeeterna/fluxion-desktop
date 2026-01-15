# PROMPT PER GENERAZIONE FAQ VERTICALI FLUXION

> **ISTRUZIONI**: Copia questo prompt in Perplexity/Claude/ChatGPT per generare i file FAQ necessari.
> **OUTPUT RICHIESTO**: File JSON pronti da salvare in `voice-agent/data/`

---

## CONTESTO

Sto costruendo **FLUXION**, un gestionale desktop italiano per PMI con Voice Agent (Sara).

Il sistema usa FAQ dinamiche con **variabili {{...}}** che vengono sostituite a runtime con dati dal database SQLite del cliente.

### Chiavi Verticali Supportate

| Chiave | Descrizione | File Output |
|--------|-------------|-------------|
| `salone` | Salone Parrucchiere | `faq_salone.json` |
| `wellness` | Palestra/Centro Benessere | `faq_wellness.json` |
| `medical` | Studio Medico/Dentista | `faq_medical.json` |
| `auto` | Officina/Carrozzeria | `faq_auto.json` |

---

## RICHIESTA GENERAZIONE

Per **OGNI verticale**, genera un file JSON con **minimo 20 FAQ** seguendo questo schema:

```json
{
  "id": "faq_[categoria]_[topic]",
  "question": "Domanda naturale in italiano",
  "answer": "Risposta con {{VARIABILI}} per dati dinamici dal DB",
  "category": "pricing|hours|services|booking|policy|payment|facilities|emergency",
  "keywords": ["parole", "chiave", "per", "matching"],
  "variables": ["LISTA_VARIABILI_USATE"]
}
```

### Variabili DB Disponibili

```
{{NOME_ATTIVITA}}        - Nome dell'attività (es: "Salone Maria")
{{INDIRIZZO}}            - Indirizzo completo
{{TELEFONO}}             - Numero telefono
{{EMAIL}}                - Email contatto
{{ORARI_APERTURA}}       - Orari formattati (es: "Lun-Ven 9-18, Sab 9-13")
{{LISTA_SERVIZI}}        - Lista servizi con prezzi
{{LISTA_OPERATORI}}      - Lista operatori/staff
{{METODI_PAGAMENTO}}     - Metodi accettati (es: "contanti, carte, Satispay")
{{PREZZO_[SERVIZIO]}}    - Prezzo specifico servizio
{{DURATA_[SERVIZIO]}}    - Durata in minuti
```

---

## TEMPLATE PER OGNI VERTICALE

### 1. SALONE PARRUCCHIERE (`faq_salone.json`)

Categorie obbligatorie:
- **pricing**: taglio uomo/donna, colore, piega, trattamenti, barba
- **hours**: orari apertura, festività, ultimo appuntamento
- **services**: lista servizi, durate, consigli (balayage, cheratina, ecc)
- **booking**: prenotazione, cancellazione, no-show policy
- **payment**: metodi pagamento, pacchetti prepagati, gift card

Terminologia specifica:
- Balayage, meches, shatush, degradè
- Piega, messa in piega, asciugatura
- Taglio = sforbiciata, spuntatina

### 2. PALESTRA/WELLNESS (`faq_wellness.json`)

Categorie obbligatorie:
- **pricing**: abbonamento mensile/annuale, corsi singoli, PT
- **hours**: orari palestra, orari piscina, corsi
- **services**: lista corsi (yoga, pilates, spinning, crossfit)
- **facilities**: spogliatoi, parcheggio, piscina, sauna
- **policy**: sospensione, disdetta, guest pass, prova gratuita

Terminologia specifica:
- Abbonamento, membership, iscrizione
- Personal trainer = PT
- Sala pesi, area cardio, functional

### 3. STUDIO MEDICO (`faq_medical.json`)

Categorie obbligatorie:
- **pricing**: visita generale, visite specialistiche, ecografie, analisi
- **hours**: orari studio, orari prelievi
- **services**: specialisti disponibili, esami, certificati
- **preparation**: digiuno, documenti da portare
- **policy**: cancellazione (24-48h), no-show, privacy GDPR
- **payment**: SSN/mutue, detrazioni fiscali 19%

Terminologia specifica:
- Visita = appuntamento medico
- Controllo = follow-up
- Prelievo = analisi sangue

⚠️ IMPORTANTE: MAI dare consigli medici. Sempre rimandare a visita.

### 4. OFFICINA/AUTO (`faq_auto.json`)

Categorie obbligatorie:
- **pricing**: tagliando, revisione, diagnosi, cambio gomme
- **hours**: orari officina, urgenze
- **services**: meccanica, elettrauto, carrozzeria, gomme
- **warranty**: garanzia lavori, ricambi
- **emergency**: spia accesa, carro attrezzi, panne

Terminologia specifica:
- Tagliando = manutenzione ordinaria
- Revisione = controllo ministeriale (€66.88 fisso)
- Spia = indicatore cruscotto

---

## OUTPUT RICHIESTO

Genera **4 file JSON separati**, uno per verticale:

```
faq_salone.json     (25+ FAQ)
faq_wellness.json   (20+ FAQ)
faq_medical.json    (20+ FAQ)
faq_auto.json       (20+ FAQ)
```

Ogni file deve essere:
- ✅ JSON valido (array di oggetti)
- ✅ UTF-8 con caratteri italiani corretti
- ✅ Variabili {{...}} per dati dinamici
- ✅ Keywords per matching NLU
- ✅ Categorie per filtering
- ✅ Risposte naturali in italiano (tono professionale ma amichevole)
- ✅ Copertura completa delle domande tipiche del settore

---

## ESEMPIO OUTPUT ATTESO

```json
[
  {
    "id": "faq_prezzo_taglio_donna",
    "question": "Quanto costa un taglio donna?",
    "answer": "Il taglio donna costa {{PREZZO_TAGLIO_DONNA}}€ e dura circa {{DURATA_TAGLIO_DONNA}} minuti. Include shampoo e asciugatura. Vuole prenotare?",
    "category": "pricing",
    "keywords": ["taglio", "donna", "costo", "prezzo", "quanto"],
    "variables": ["PREZZO_TAGLIO_DONNA", "DURATA_TAGLIO_DONNA"]
  },
  {
    "id": "faq_orari",
    "question": "Quali sono i vostri orari?",
    "answer": "Siamo aperti {{ORARI_APERTURA}}. L'ultimo appuntamento è 30 minuti prima della chiusura.",
    "category": "hours",
    "keywords": ["orari", "apertura", "quando", "aperto", "chiuso"],
    "variables": ["ORARI_APERTURA"]
  }
]
```

---

## DOPO LA GENERAZIONE

1. Salva i file in `voice-agent/data/`
2. Claude Code li integra nel sistema RAG
3. Sara potrà rispondere alle FAQ di ogni verticale

---

*FLUXION - Voice Agent Sara - Gennaio 2026*
