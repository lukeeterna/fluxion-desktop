# 🔍 PROMPT: Identificazione Micro-Categorie PMI

**Per**: Kimi Code CLI / Kimi 2.5 / Claude  
**Scopo**: Identificare micro-categoria specifica e customizzare scheda cliente  
**Input**: Dati raccolti dalla PMI durante call/colloquio

---

## 🎯 OBIETTIVO

Analizzare le informazioni raccolte da una PMI (Piccola/Media Impresa del settore servizi) e:
1. **Identificare** la micro-categoria più specifica (es: non solo "dentista" ma "implantologo")
2. **Mappare** i dati clinici/lavorativi specifici necessari
3. **Proporre** una configurazione scheda cliente customizzata
4. **Suggerire** template Voice Agent appropriati

---

## 📥 INPUT RACCOLTO (Esempio)

```json
{
  "conversazione_estratto": "Sono il Dr. Rossi, lavoro in uno studio dentistico a Milano. Facciamo principalmente implantologia e ricostruzione gengivale. Abbiamo 3 studi, facciamo anche ortodonzia invisibile con gli alligner. I nostri pazienti sono adulti 40-65 anni.",
  "servizi_menzionati": ["implantologia", "ricostruzione gengivale", "ortodonzia invisibile"],
  "attrezzature": ["CBCT", "chirurgia guidata"],
  "target_eta": "40-65 anni",
  "location": "Milano",
  "numero_sedi": 3
}
```

---

## 🧠 PROCESSO ANALISI

### Step 1: Identificazione Macro-Categoria

```
INPUT: "implantologia, ricostruzione gengivale, ortodonzia invisibile"

ANALISI:
- Implantologia = odontoiatria specialistica
- Ricostruzione gengivale = parodontologia + implantologia
- Ortodonzia invisibile = ortodonzia
- CBCT = imaging avanzato

MACRO-CATEGORIA: 🦷 DENTISTA
```

### Step 2: Identificazione Micro-Categoria

```
ALBERO DECISIONALE:

DENTISTA
├── Odontoiatra generico? 
│   └── NO (troppo specialistico)
├── Ortodontista puro?
│   └── NO (fa anche implantologia)
├── Implantologo?
│   └── PROBABILMENTE SÌ (focus principale)
├── Parodontologo?
│   └── PARZIALE (ricostruzione gengivale)
└── MULTI-SPECIALISTA
    └── ✅ MATCH MIGLIORE

MICRO-CATEGORIA: "Implantologo con competenze parodontali e ortodontiche"
CODICE: implantologo_multi
```

### Step 3: Mappatura Dati Specifici

```
DATI SCHEDA IMPLANTOLOGO:

□ Odontogramma 32 denti (FDI)
  └── Plus: indicazione implantare per edenti

□ Tabella Impianti
  ├── Posizione (dente 11-48)
  ├── Marca impianto (Straumann, Nobel, etc.)
  ├── Diametro x Lunghezza
  ├── Data inserimento
  ├── Data carico protesico
  ├── Sopraccrescimento (sì/no)
  └── Controlli perimplantari

□ Sondaggio Parodontale
  ├── 6 siti per dente
  ├── Profondità tasche (mm)
  ├── Sanguinamento (sì/no)
  └── Indici: IPC, IPS, MPP

□ Ortodonzia (se presente)
  ├── Tipo allineatori (Invisalign, etc.)
  ├── Numero allineatori
  ├── Allineatore attuale
  └── Scadenza cambio

□ Imaging
  ├── Radiografie endorali
  ├── OPG
  ├── CBCT (specifico implantologia)
  └── Foto intra/extraorali
```

### Step 4: Configurazione Voice Agent

```
INTENT SPECIFICI IMPLANTOLOGO:

pre_implantare_consulto
├─ "vorrei informazioni sugli impianti"
├─ "quanto costa un impianto?"
├─ "ho perso un dente, cosa posso fare?"
└─ "quali marche di impianti usate?"

controllo_perimplantare
├─ "devo fare il controllo all'impianto"
├─ "quando è il prossimo richiamo?"
└─ "il mio impianto fa male"

protesi_carico
├─ "quando mettete la corona?"
├─ "quanto dura l'attesa per la protesi?"
└─ "devo fare il provvisorio?"

emergenza_post_chirurgica
├─ "sanguino dopo l'intervento di ieri"
├─ "il punto si è aperto"
└─ "ho molto gonfiore, è normale?"

TEMPLATES RISPOSTA:
- "Buongiorno, sono Sara dello studio implantologico del Dr. Rossi..."
- "Per un consulto implantare ho bisogno di sapere se ha una recente CBCT..."
- "Il controllo post-operatorio è fondamentale, la prenoto per dopodomani?"
```

---

## 📋 OUTPUT FORMAT

```json
{
  "analisi_input": {
    "macro_categoria": "dentista",
    "micro_categoria": "implantologo_multi",
    "confidenza": 0.92,
    "motivazione": "Combinazione implantologia + parodontologia + ortodonzia indica multi-specialista"
  },
  
  "configurazione_scheda": {
    "schede_abilitate": [
      "odontogramma",
      "impianti",
      "parodontale",
      "ortodonzia",
      "imaging"
    ],
    "campi_custom": [
      {
        "nome": "fattori_rischio_implantare",
        "tipo": "multiselect",
        "opzioni": ["fumatore", "diabetico", "parodontite", "bruxismo"]
      },
      {
        "nome": "tipo_bone",
        "tipo": "select",
        "opzioni": ["I", "II", "III", "IV"]
      }
    ]
  },
  
  "voice_agent_config": {
    "greeting": "Buongiorno, sono Sara dello studio implantologico del Dr. Rossi. Come posso aiutarla?",
    "intents_principali": ["pre_implantare_consulto", "controllo_perimplantare", "protesi_carico"],
    "terminologia": ["impianto", "corona", "carico protesico", "CBCT", "ossointegrazione"],
    "scripts_proposti": 5
  },
  
  "azioni_suggerite": [
    "Abilitare modulo impianti completo",
    "Configurare scadenze controlli perimplantari",
    "Attivare gestione consentimenti specifici chirurgia",
    "Setup flusso pre-post operatorio"
  ]
}
```

---

## 🗂️ LIBRERIA MICRO-CATEGORIE

### 🏥 SETTORE MEDICO-SANITARIO

```yaml
medico_base:
  - medico_famiglia: [cronici, terapie_long_term, esami_periodici]
  - pediatra: [vaccinazioni, percentili, development]
  - geriatra: [polifarmacia, fragilita, CAD, demenza]
  - medico_sportivo: [certificazioni, idoneità, parametri]
  - medico_lavoro: [sorveglianza, infortuni, idoneità]
  
fisioterapia:
  - fisio_ortopedico: [post_chirurgico, traumi, VAS, ROM, WOMAC]
  - fisio_neurologico: [ictus, Parkinson, Barthel, Rankin]
  - fisio_respiratorio: [BPCO, post_COVID, 6MWT, spirometria]
  - fisio_sportivo: [infortuni, Hop_test, Y_balance]
  - fisio_pediatrico: [DSA, PC, GMFM, PEDI]
  - fisio_geriatrico: [cadute, deambulazione, Tinetti, TUG]
  - linfologo: [linfedemi, ulcere, circunferenze]
  - osteopata: [postura, somatiche, FMS, SFMA]
  - chinesiologo: [funzionale, propriocettivo, core]
  - terapista_manuale: [manipolazioni, mobilizzazioni]

dentista:
  - odontoiatra_generico: [conservativa, endodonzia]
  - ortodontista: [apparecchi, aligners, cephalometrico]
  - parodontologo: [gengive, tasche, sondaggio, MPP]
  - implantologo: [impianti, rigenerative, CBCT, chirurgia_guidata]
  - protesista: [corone, ponti, protesi, occlusione]
  - pedodontista: [dentizione_mista, sigillature, comportamentale]
  - endodontista: [canalizzazioni, microscopio]
  - chirurgo_orale: [estrazioni, cisti, biopsie]
  - odontoiatra_estetico: [facette, sbiancamenti, smile_design]
  - gnatologo: [ATM, occlusione, articolatore]

medico_specialista:
  - cardiologo: [ECG, Holter, eco, ipertensione]
  - dermatologo: [dermoscopia, mappatura_nei, acne]
  - ginecologo: [Pap_test, colposcopia, gravidanza]
  - oculista: [OCT, campimetria, cataratta, glaucoma]
  - otorino: [audiometria, sinusite, allergie]
  - urologo: [prostata, calcoli, ecografia]
  - ortopedico: [artrosi, RM, artroscopia]
  - reumatologo: [artrite, autoanticorpi, capillaroscopia]
  - endocrinologo: [diabete, tiroide, OGTT]
  - gastroenterologo: [endoscopia, colonscopia, reflusso]
  - neurologo: [emicrania, RM, EEG, SM]
  - pneumologo: [asma, BPCO, spirometria]
  - allergologo: [prick_test, RAST, desensibilizzazione]
  - medicina_estetica: [botox, filler, laser]
```

### 💇 SETTORE PARRUCCHIERE

```yaml
parrucchiere:
  - salone_donna: [taglio, styling, piega, donna_25_55]
  - barbiere: [taglio_uomo, barba, sfumature, uomo_18_50]
  - salone_unisex: [servizi_misti, famiglie]
  - color_specialist: [balayage, tecniche_avanzate, fashion]
  - extension_specialist: [extension, infoltimento]
  - nail_specialist: [gel, acrilico, nail_art]
  - trucco_permanente: [microblading, PMU]
  - bridal_hair: [sposa, acconciature_evento]
  - oncologico: [parrucche, turbanti, chemio]
  - bio_eco: [prodotti_naturali, clientela_eco]
  - blow_dry_bar: [solo_piega, business_woman]
  - kids_hair: [bambini, famiglie]
```

### 💆 SETTORE ESTETICA

```yaml
estetista:
  - estetista_viso: [pulizia, peeling, antiage, ultrasuoni]
  - estetista_corpo: [massaggi, lipolisi, pressoterapia]
  - epilazione_specialist: [laser, IPL, ceretta, filo]
  - nail_artist: [manicure, pedicure, nail_art]
  - lash_artist: [extension_ciglia, lifting]
  - microblading: [sopracciglia, PMU]
  - centro_massaggi: [rilassante, decontratturante]
  - spa_terme: [fanghi, idroterapia, sauna]
  - dimagrimento: [diete, BIA, plicometro]
  - estetica_oncologica: [trucco_riabilitativo]
  - estetica_materna: [gravidanza, post_parto]
  - tattoo_removal: [rimozione_tatuaggi, laser]
```

### 💪 SETTORE FITNESS

```yaml
fitness:
  - palestra_tradizionale: [bodybuilding, cardio, macchinari]
  - studio_pt: [personal_training, 1_to_1]
  - crossfit_box: [WOD, functional, rig]
  - yoga_studio: [hatha, vinyasa, yin]
  - pilates_studio: [reformer, matwork]
  - cycling_studio: [spinning, indoor_bike]
  - functional_studio: [TRX, calisthenics]
  - centro_dimagrimento: [weight_loss, nutrizione]
  - centro_riabilitativo: [post_infortunio, isocinetici]
  - tennis_padel: [sport_racchetta]
  - piscina: [nuoto, acquafitness]
  - arti_marziali: [karate, judo, boxe]
  - danza_studio: [classica, moderna, hip_hop]
  - climbing_gym: [arrampicata, boulder]
  - posturale: [ginnastica_correttiva]
```

### 🚗 SETTORE MECCANICA

```yaml
meccanico:
  - officina_multimarca: [tagliandi, riparazioni, tutte_marche]
  - officina_specializzata: [marchio_specifico, dealer]
  - carrozzeria: [riparazioni, verniciatura, collisione]
  - centro_revisioni: [revisioni_periodiche, rapido]
  - gommista: [pneumatici, convergenza, bilanciatura]
  - elettrauto: [impianti_elettrici, diagnosi, chiavi]
  - scarichi: [marmitte, FAP, catalizzatori]
  - clima: [aria_condizionata, ricarica]
  - cambi_automatici: [revisione, meccanica_precisione]
  - diesel_specialist: [iniettori, common_rail]
  - vintage_restauro: [auto_epoca, conservativo]
  - motorsport: [preparazione, pista, performance]
  - soccorso_stradale: [traino, emergenze, 24_7]
  - flotte_aziendali: [parco_auto, contratti]
  - moto_officina: [due_ruote, scooter]
  - veicoli_industriali: [camion, bus, agricoli]
  - nautica: [barche, gommoni, motori_marini]
```

---

## 🔧 UTILIZZO DEL PROMPT

### Per ricerca mirata

```
"Trova tutte le estetiste a Milano specializzate in epilazione laser"

PROMPT:
"Sei un ricercatore di mercato. Trova PMI nel settore estetica a Milano
con focus su epilazione laser. Per ogni risultato, identifica:
1. Micro-categoria (estetista_corpo o epilazione_specialist)
2. Servizi specifici offerti
3. Attrezzature utilizzate
4. Target clientela
5. Prezzi medi praticati"
```

### Per customizzazione scheda

```
"Abbiamo appena acquistato Fluxion un fisioterapista sportivo"

PROMPT:
"Input: fisioterapista sportivo, infortuni agonistici, test funzionali
Output: Configurazione scheda cliente specifica con:
1. Micro-categoria: fisio_sportivo
2. Schede abilitate: valutazioni, test, protocolli
3. Campi custom: sport_praticato, livello agonistico
4. Voice intents: infortunio_sportivo, RTP, prevenzione"
```

---

## ✅ QUALITY CHECKLIST

Prima di finalizzare configurazione:

- [ ] Micro-categoria identificata con confidenza > 80%
- [ ] Tutti i servizi offerti mappati in schede
- [ ] Voice Agent ha intents specifici settore
- [ ] Terminologia corretta per il vertical
- [ ] Campi custom rilevanti per la specializzazione
- [ ] Workflow pre/post previsto

---

*Prompt per identificazione micro-categorie PMI*
