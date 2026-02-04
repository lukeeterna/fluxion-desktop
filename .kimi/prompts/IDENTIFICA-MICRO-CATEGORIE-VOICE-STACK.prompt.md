# 🔍 PROMPT: Identificazione Micro-Categorie PMI + Voice Agent Stack

**Per**: Kimi Code CLI / Kimi 2.5 / Claude  
**Scopo**: Identificare micro-categoria specifica tenendo conto dello stack Voice Agent già implementato  
**Data**: 2026-02-03

---

## 🎯 OBIETTIVO

Analizzare la PMI target e proporre configurazione che sia **COMPATIBILE** con lo stack Voice Agent esistente (4-layer RAG + State Machine + Regex L0), senza richiedere modifiche complesse al sistema vocale.

---

## 🎙️ STACK VOICE AGENT ATTUALE (Analisi)

### Layer 0: Special Commands (Regex Pre-compilati)
**File**: `italian_regex.py` - Matching <1ms

```python
# Comandi gestiti automaticamente da L0:
- CONFERMA: sì, ok, va bene, confermo, certo, perfetto, ottimo
- RIFIUTO: no, annulla, stop, lascia stare, non mi interessa, ci devo pensare
- ESCALATION: operatore, persona vera, parlo con qualcuno, passami il titolare
- FILLER: ehm, uhm, allora, dunque, ecco, insomma, praticamente, per favore
- CONTENT FILTER: inappropriate (3 livelli di severità)
```

### Layer 1: Intent Classifier (Deterministico O(1))
**File**: `intent_classifier.py`

```python
# Intents riconosciuti automaticamente:
IntentCategory.SALUTO          # "ciao", "buongiorno", "salve"
IntentCategory.PRENOTAZIONE    # "vorrei prenotare", "mi serve un appuntamento"
IntentCategory.ANNULAMENTO     # "vorrei annullare", "devo disdire"
IntentCategory.INFO_ORARI      # "che orari avete?", "siete aperti?"
IntentCategory.INFO_PREZZI     # "quanto costa?", "che prezzi fate?"
IntentCategory.FAQ             # domande frequenti
IntentCategory.CHIUSURA        # "grazie", "arrivederci", "buona giornata"
IntentCategory.CAMBIO          # "vorrei cambiare", "posso spostare"
IntentCategory.OPERATORE       # "parlo con un operatore"
IntentCategory.GENERICO        # fallback
```

### Layer 2: Entity Extractor + State Machine
**File**: `entity_extractor.py` + `booking_state_machine.py`

```python
# Entità estratte automaticamente:
- extract_name(): "Mi chiamo Mario Rossi" → Mario Rossi
- extract_date(): "domani", "mercoledì", "15 gennaio" → YYYY-MM-DD
- extract_time(): "alle 3", "15:00" → HH:MM
- extract_service(): "taglio", "colorazione", "massaggio" → servizio
- extract_operator(): "con Marco", "la signora Anna" → operatore

# State Machine stati:
IDLE → WAITING_NAME → WAITING_SERVICE → WAITING_DATE → WAITING_TIME → CONFIRMING → COMPLETED
            ↓
    WAITING_SURNAME (nuovo cliente)
            ↓
    CONFIRMING_PHONE (verifica telefono)
```

### Layer 3: RAG FAQ (Keyword + Semantic)
**File**: `faq_manager.py`

```python
# FAQ recuperate da base di conoscenza
- orari_apertura
- prezzi_listino
- servizi_offerti
- posizione_indirizzo
- politica_annullamento
```

### Layer 4: Groq LLM (Fallback)
**File**: `groq_nlu.py`

```python
# Solo per query complesse non gestite dai layer superiori
- Domande elaborate che richiedono ragionamento
- Contesto multi-turn complesso
- Fallback quando L0-L3 non matchano
```

---

## ⚠️ LIMITAZIONI CONOSCIUTE (Non aggiungere complessità)

### Cosa NON funziona bene attualmente:
1. **Troppi intents vertical-specifici** → il classifier si confonde
2. **Entità complesse** (es: odontogramma, formulazioni colori) → non estratte da regex
3. **Conversazioni multi-servizio** → meglio gestire un servizio per volta
4. **Voice Agent con terminologia medica/tecnica specifica** → richiede training dataset

### Cosa FUNZIONA bene:
1. **Prenotazioni standard** (nome, data, ora, servizio)
2. **Domande FAQ semplici** (orari, prezzi, indirizzo)
3. **Gestione conferme/rifiuti** (flusso binario chiaro)
4. **Escalation a operatore** (sempre disponibile)

---

## 📋 INPUT RACCOLTO PMI

```json
{
  "nome_attivita": "Studio Fisioterapico Movimento",
  "tipo_attivita": "Fisioterapia",
  "servizi_principali": ["riabilitazione post-chirurgica", "fisioterapia sportiva", "osteopatia"],
  "servizi_secondari": ["massaggi decontratturanti", "ginnastica posturale"],
  "target_clientela": "sportivi, post-operatori, anziani",
  "numero_operatori": 3,
  "usa_agenda": true,
  "ha_telefono_fisso": true,
  "durata_media_visita": "45-60 minuti"
}
```

---

## 🧠 PROCESSO ANALISI CON STACK VOICE

### Step 1: Compatibilità Voice Agent

```
ANALISI SERVIZI PMI:
- "riabilitazione post-chirurgica" → OK (servizio singolo)
- "fisioterapia sportiva" → OK (servizio singolo)  
- "osteopatia" → OK (servizio singolo)
- "massaggi decontratturanti" → OK (servizio singolo)
- "ginnastica posturale" → OK (servizio singolo)

COMPATIBILITÀ: ✅ ALTA
Motivo: Tutti servizi prenotabili con (nome + data + ora + servizio)
```

### Step 2: Mappatura a Intent Esistenti

```
SERVIZIO → IntentCategory.PRENOTAZIONE
         → extract_service() cattura "fisioterapia", "massaggio", "osteopatia"

DOMANDA PREZZO → IntentCategory.INFO_PREZZI
               → FAQ: "Quanto costa una seduta di fisioterapia?"

DOMANDA DURATA → IntentCategory.FAQ
               → FAQ: "Quanto dura una seduta?" (45-60 min)

CANCELLAZIONE → IntentCategory.ANNULAMENTO
              → State Machine: CANCELLED
```

### Step 3: Identificazione Micro-Categoria

```
ALBERO DECISIONALE FISIOTERAPIA:

FISIOTERAPIA
├── Solo post-chirurgico? NO (anche sportivo)
├── Solo sportivo? NO (anche post-operatorio)
├── Solo osteopatia? NO (mix)
├── Specializzazione chiara? SÌ (sport + post-chirurgico)
└── MICRO-CATEGORIA: "Fisioterapista sportivo e riabilitativo"
   CODICE: fisio_sport_riab
```

### Step 4: Configurazione COMPATIBILE con Voice Agent

```json
{
  "micro_categoria": "fisio_sport_riab",
  
  "voice_agent_config": {
    "greeting": "Buongiorno, sono Sara dello Studio Movimento. Posso prenotare una seduta di fisioterapia, massaggio o osteopatia. Di cosa ha bisogno?",
    
    "services_mappati": {
      "riabilitazione post-chirurgica": "fisioterapia",
      "fisioterapia sportiva": "fisioterapia",
      "osteopatia": "osteopatia",
      "massaggi decontratturanti": "massaggio",
      "ginnastica posturale": "ginnastica"
    },
    
    "faq_abilitate": [
      "Quanto costa una seduta?",
      "Quanto dura una seduta?",
      "Devo portare qualcosa?",
      "Fate visite a domicilio?",
      "Serve la prescrizione medica?"
    ],
    
    "state_machine": "STANDARD",
    "custom_intents": false,
    "note": "Usa flusso prenotazione standard. Non aggiungere intents vertical-specifici."
  },
  
  "scheda_cliente": {
    "schede_abilitate": ["anamnesi_base", "sedute"],
    
    "campi_semplici": [
      {
        "nome": "tipo_intervento",
        "tipo": "select",
        "opzioni": ["sportivo", "post_chirurgico", "post_traumatico", "cronico"],
        "voice_compatible": true
      },
      {
        "nome": "zona_trattamento",
        "tipo": "text",
        "esempio": "spalla destra, ginocchio, schiena",
        "voice_compatible": true
      }
    ],
    
    "campi_complessi": [
      {
        "nome": "scala_vas_dolore",
        "tipo": "number_0_10",
        "note": "Richiede UI, non voice",
        "voice_compatible": false
      }
    ]
  }
}
```

---

## 📊 MATRICE COMPATIBILITÀ SERVIZI

| Servizio | Prenotazione Voice | Entità Estratte | Complessità |
|----------|-------------------|-----------------|-------------|
| Taglio capelli | ✅ Semplice | servizio, data, ora | BASSA |
| Colorazione | ✅ Semplice | servizio, data, ora | BASSA |
| Massaggio | ✅ Semplice | servizio, data, ora | BASSA |
| Fisioterapia | ✅ Semplice | servizio, data, ora | BASSA |
| Visita dentista | ✅ Semplice | servizio, data, ora | BASSA |
| Personal training | ✅ Semplice | servizio, data, ora | BASSA |
| Tagliando auto | ⚠️ Medio | servizio + targa + km | MEDIA |
| Implantologia | ❌ Complesso | servizio + tipo impianto + quandrant | ALTA |
| Colorazione formula | ❌ Complesso | servizio + formulazione precisa | ALTA |

---

## ✅ CHECKLIST COMPATIBILITÀ

Prima di proporre configurazione:

- [ ] Servizi prenotabili con (nome + data + ora + servizio)?
- [ ] Esiste FAQ per domande comuni (prezzi, orari, durata)?
- [ ] Nessun intent vertical-specifico necessario?
- [ ] Entità estratte dai regex esistenti sufficienti?
- [ ] State Machine standard gestisce il flusso?
- [ ] Fallback a operatore disponibile per casi complessi?

---

## 🗂️ LIBRERIA MICRO-CATEGORIE (Voice-Compatible)

### PARRUCCHIERE (Voice OK)
```yaml
salone_donna:
  servizi: [taglio, piega, colore, meches, balayage]
  voice: semplice
  faq: [prezzi, orari, durata]
  
barbiere:
  servizi: [taglio_uomo, barba, sfumature]
  voice: semplice
  
salone_unisex:
  servizi: [taglio, barba, styling]
  voice: semplice
  
extension_specialist:
  servizi: [extension, infoltimento]
  voice: medio (richiede consulto)
  nota: "Meglio far prenotare consulenza iniziale"
```

### ESTETICA (Voice OK)
```yaml
estetista_viso:
  servizi: [pulizia, peeling, idratazione]
  voice: semplice
  
estetista_corpo:
  servizi: [massaggio, pressoterapia, ceretta]
  voice: semplice
  durata: variabile (30-60 min)
  
epilazione_laser:
  servizi: [laser_diodo, ceretta]
  voice: medio
  nota: "Prima seduta richiede patch test → prenota 'prima visita'"
```

### FISIOTERAPIA (Voice OK)
```yaml
fisio_ortopedico:
  servizi: [fisioterapia, riabilitazione, massaggio]
  voice: semplice
  
fisio_sportivo:
  servizi: [fisioterapia_sport, rieducazione, prevenzione]
  voice: semplice
  
osteopata:
  servizi: [trattamento_osteopatico, manipolazione]
  voice: semplice
```

### DENTISTA (Voice Medio-Complessa)
```yaml
odontoiatra_generico:
  servizi: [pulizia, otturazione, devitalizzazione]
  voice: semplice
  
ortodontista:
  servizi: [apparecchio, allineatori, controllo]
  voice: medio
  nota: "Allineatori richiedono numero allineatore → UI, non voice"
  
implantologo:
  servizi: [implantologia, chirurgia, protesi]
  voice: complesso
  nota: "Richiede sempre consulenza preliminare → prenota 'visita implantare'"
```

### FITNESS (Voice OK)
```yaml
palestra_tradizionale:
  servizi: [abbonamento, personal_training, corsi]
  voice: semplice
  
studio_pt:
  servizi: [personal_training, valutazione]
  voice: semplice
  
yoga_pilates:
  servizi: [lezione, corso, abbonamento]
  voice: semplice
```

### MECCANICO (Voice Medio)
```yaml
officina_multimarca:
  servizi: [tagliando, freni, frizione]
  voice: medio
  richiede: targa (se cliente noto) o targa+modello (se nuovo)
  
revisioni:
  servizi: [revisione_periodica, collaudo]
  voice: semplice
  
carrozzeria:
  servizi: [preventivo, riparazione, verniciatura]
  voice: medio
  nota: "Preventivo richiede foto/visura → prenota 'sopralluogo'"
```

---

## 🔧 OUTPUT FORMAT

```json
{
  "analisi_voice_compatibility": {
    "score": "alta/media/bassa",
    "motivazione": "Servizi prenotabili con flusso standard",
    "rischi": ["eventuali problematiche"]
  },
  
  "micro_categoria": {
    "nome": "nome specifico",
    "codice": "codice_snake_case",
    "servizi_prenotabili": ["lista servizi mappabili a voice"]
  },
  
  "voice_agent_config": {
    "greeting": "frase personalizzata",
    "services_mapping": {"da voice": "a interno"},
    "faq_list": ["domande abilitate"],
    "state_machine": "STANDARD o CUSTOM",
    "custom_intents_necessari": false
  },
  
  "scheda_cliente": {
    "schede_semplici": ["elenco schede UI basic"],
    "schede_complesse": ["elenco schede UI avanzate (no voice)"],
    "campi_voice_compatibili": ["campi gestibili via conversazione"]
  },
  
  "recommendations": [
    "Suggerimenti per configurazione ottimale",
    "Limiti da comunicare al cliente",
    "Eventuali workaround necessari"
  ]
}
```

---

*Prompt con analisi stack Voice Agent attuale*
