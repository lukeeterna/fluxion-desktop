# 📊 RICERCAPPROFONDITA - Tutti i Verticali PMI Italiane

**Data**: 2026-02-03  
**Scopo**: Definire schema dati completo per sistema multi-verticale con sblocco per licenza

---

## 🏢 ANALISI VERTICALI (6 Settori PMI Italia)

### 1. 🚗 AUTOFFICINA / MECCANICO / CARROZZERIA

#### Business Model
- **Clienti**: Proprietari veicoli (B2C) + aziende con flotte (B2B)
- **Frequenza**: Regolare (tagliandi ogni 10-20k km) + emergenze
- **Valore**: €50-500 per intervento, relazione duratura
- **Pain Point**: Tracciare storico veicoli, scadenze, garanzie

#### Entità Chiave
```
CLIENTE (persona)
  └── VEICOLI (1:N)
       └── INTERVENTI (1:N)
            └── VOCI (lavori/ricambi)
```

#### Schema Dati Completo
```typescript
// Anagrafica Veicolo
interface Veicolo {
  // Identificazione
  id: string;
  targa: string;              // AB123CD - IT
  telaio: string;             // VIN (17 char)
  
  // Dati tecnici
  tipo: 'auto' | 'moto' | 'furgone' | 'camion' | 'rimorchio';
  marca: string;              // Fiat, BMW, VW...
  modello: string;            // Panda, X3, Golf...
  versione?: string;          // 1.3 MJT, 320d...
  anno: number;
  immatricolazione?: Date;
  
  // Motore/Trasmissione
  alimentazione: 'benzina' | 'diesel' | 'gpl' | 'metano' | 'ibrido' | 'elettrico';
  cilindrata?: number;        // cc
  kw?: number;                // Potenza
  cv_fiscali?: number;        // Per bollo
  
  // Stato
  km_attuali: number;
  km_inserimento: number;     // Quando entrato in officina
  
  // Scadenze (critico!)
  scadenze: {
    bollo: Date;
    assicurazione: Date;
    revisione: Date;
    tagliando?: Date;         // Prossimo stimato
  };
  
  // Preferenze/Note
  olio_preferito?: string;
    ricambi_preferiti?: string[]; // Marche OEM/Dopo mercato
  note_tecnicihe?: string;    // "Attenzione alla marmitta"
  
  // Relazioni
  proprietario_id: string;    // cliente_id
  
  // Meta
  created_at: Date;
  updated_at: Date;
}

// Intervento (Storico Manutenzione)
interface InterventoMeccanico {
  id: string;
  veicolo_id: string;
  cliente_id: string;
  
  // Contesto
  data: Date;
  km: number;                 // Km al momento
  operatore_id: string;       // Meccanico
  
  // Classificazione
  tipo: 'ordinaria' | 'straordinaria' | 'garantia' | 'carrozzeria' | 'elettronica' | 'tagliando';
  motivo: string;             // "Cambio olio", "Rumore sospensione"
  
  // Diagnostica
  diagnosi?: string;
  cause?: string;
  
  // Lavori effettuati (array)
  lavori: {
    codice?: string;          // Codice interno
    descrizione: string;
    tempo_ore: number;        // Manodopera
    costo_orario: number;
    totale_lavoro: number;
  }[];
  
  // Ricambi utilizzati
  ricambi: {
    codice_oem?: string;
    codice_interno?: string;
    descrizione: string;
    quantita: number;
    prezzo_acquisto?: number; // Margine
    prezzo_vendita: number;
    fornitore?: string;
    giacenza_prelevata: boolean;
  }[];
  
  // Materiali consumabili
  consumabili?: {
    tipo: 'olio_motore' | 'olio_cambio' | 'liquido_freni' | 'refrigerante' | 'grasso';
    quantita: number;
    unita: 'litri' | 'kg';
    marca: string;
    specifica?: string;       // 5W-30, DOT4...
  }[];
  
  // Costi
  costo_manodopera: number;
  costo_ricambi: number;
  costo_consumabili: number;
  sconto_percentuale: number;
  costo_totale: number;
  
  // Garanzia
  garanzia_giorni: number;    // Default 24 mesi legge
  scadenza_garanzia?: Date;
  condizioni_garanzia?: string;
  
  // Documenti
  foto_pre?: string[];        // Path foto
  foto_post?: string[];
  allegati?: string[];        // PDF diagnosi
  
  // Prevenzione
  raccomandazioni?: string[]; // "Cambiare pastiglie tra 5000km"
  prossimo_appuntamento?: Date;
  
  // Fatturazione
  fatturato: boolean;
  numero_fattura?: string;
  
  note_interne?: string;      // Visibile solo staff
  note_cliente?: string;      // Visibile in report
  
  created_at: Date;
  updated_at: Date;
}

// Preventivo (prima diventa intervento)
interface PreventivoMeccanico {
  id: string;
  veicolo_id: string;
  cliente_id: string;
  data: Date;
  scadenza: Date;             // Validità preventivo
  
  descrizione_intervento: string;
  voci: VocePreventivo[];
  
  costo_totale: number;
  approvato: boolean;
  data_approvazione?: Date;
  
  // Se approvato → crea Intervento
  intervento_id?: string;
}
```

#### Voice Agent - Intent Specifici
```
NUOVO_INTERVENTO
├─ "devo fare il tagliando"
├─ "l'auto fa rumore"
├─ "i freni non tengono"
├─ "spia motore accesa"
└─ "ho bucato una gomma"

INFO_MANUTENZIONE
├─ "quando scade il bollo?"
├─ "a quanti km siamo?"
├─ "quando è stata l'ultima revisione?"
└─ "ho ancora garanzia sull'intervento di marzo?"

PREVENTIVO
├─ "quanto costa cambiare la frizione?"
├─ "vorrei un preventivo per la distribuzione"
└─ "che lavori servono per i 100.000km?"

EMERGENZA
├─ "l'auto non si avvia"
├─ "ho avuto un incidente"
└─ "il motore fuma"
```

#### Sblocco Licenza
- **Tier**: `officina` o `meccanico`
- **Feature**: Schema veicoli + interventi + Voice meccanico

---

### 2. 🏥 STUDIO MEDICO / FISIOTERAPISTA / OSTEOPATA

#### Business Model
- **Clienti**: Pazienti (ricorrenti per terapie)
- **Frequenza**: Trattamenti settimanali/bisettanali
- **Valore**: €50-150 a seduta, pacchetti da €300-1000
- **Pain Point**: Storico trattamenti, evoluzione paziente, obiettivi

#### Entità Chiave
```
PAZIENTE
  └── SCHEDA_MEDICA (1:1)
       └── VALUTAZIONI / SEDUTE (1:N)
            └── TRATTAMENTO
```

#### Schema Dati Completo (Tassonomia Profonda)
```typescript
// Scheda Anamnestica Completa
interface SchedaMedica {
  id: string;
  cliente_id: string;
  
  // === DATI ANTROPOMETRICI ===
  fisico: {
    altezza_cm?: number;
    peso_kg?: number;
    bmi?: number;
    circonferenza_vita?: number;
    gruppo_sanguigno?: 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | '0+' | '0-';
  };
  
  // === ALLERGIE & INTOLLERANZE ===
  allergie: {
    tipo: 'farmaco' | 'alimento' | 'ambientale' | 'cutanea' | 'respiratoria';
    agente: string;           // Es: "Penicillina"
    reazione: string;         // Es: "Urticaria diffusa"
    gravita: 'lieve' | 'moderata' | 'grave' | 'anafilassi';
    data_identificazione?: Date;
    note?: string;
  }[];
  
  intolleranze_alimentari?: string[]; // Lattosio, glutine...
  
  // === PATOLOGIE (Storia clinica) ===
  patologie_attuali: {
    codice_icd10?: string;    // Classificazione internazionale
    nome: string;
    data_inizio: Date;
    stato: 'attiva' | 'in_trattamento' | 'cronica' | 'in_remisssione';
    gravita: 'lieve' | 'moderata' | 'grave';
    terapia_in_corso?: string;
    note?: string;
  }[];
  
  patologie_precedenti: {
    nome: string;
    periodo: string;          // "2018-2019"
    esito: 'guarigione' | 'in_remisssione' | 'cronica';
    note?: string;
  }[];
  
  patologie_familiari: {
    parentela: 'padre' | 'madre' | 'fratello' | 'sorella' | 'nonno' | 'nonna' | 'zio' | 'zia';
    patologia: string;
    eta_diagnosi?: number;
    deceduto_per_causa?: boolean;
  }[];
  
  // === FARMACI ===
  farmaci_in_corso: {
    nome_commerciale?: string;
    principio_attivo: string;
    dosaggio: string;         // "500mg"
    frequenza: string;        // "2 volte al giorno"
    orario?: string;          // "mattina e sera"
    data_inizio: Date;
    data_fine_prevista?: Date;
    prescrivente?: string;    // Medico
    motivo: string;
    note?: string;
  }[];
  
  // === STILE DI VITA ===
  stile_vita: {
    fumatore: 'mai' | 'ex' | 'attuale' | 'occasionale';
    anni_fumo?: number;
    sigarette_giorno?: number;
    
    alcol: 'astemio' | 'occasionale' | 'moderato' | 'regolare';
    tipo_alcol?: string[];    // Vino, birra...
    
    attivita_fisica: 'sedentaria' | 'leggera' | 'moderata' | 'intensa';
    sport?: string;
    frequenza_sport?: string;
    
    professione?: string;
    settore?: string;
    mansioni?: string;        // "Molte ore in piedi"
    
    alimentazione?: 'onnivora' | 'vegetariana' | 'vegana' | 'altro';
    sonno_ore?: number;
  };
  
  // === ESAMI DIAGNOSTICI ===
  esami: {
    tipo: 'emocromo' | 'biochimica' | 'ormonale' | 'urine' | 'radiografia' | 'risonanza' | 'tomografia' | 'ecografia' | 'elettrocardiogramma' | 'altro';
    data: Date;
    struttura?: string;
    medico_refertante?: string;
    referto_breve: string;
    valori_anomali?: string[];
    allegati: string[];       // Path file
    
    // Per esami ripetibili
    valori?: {
      parametro: string;
      valore: number;
      unita: string;
      range_riferimento?: string;
      esito: 'normale' | 'alterato' | 'critico';
    }[];
  }[];
  
  // === VACCINAZIONI ===
  vaccinazioni?: {
    vaccino: string;
    data: Date;
    scadenza?: Date;
    richiamo_fatto: boolean;
  }[];
  
  // === NOTE CRITICHE ===
  note_emergenza?: string;    // "Diabetico - in caso di coma..."
  contatto_emergenza?: {
    nome: string;
    telefono: string;
    relazione: string;
  };
  
  // === CONSENSI ===
  consensi: {
    trattamento_dati: boolean;
    comunicazione_terzi: boolean;
    trattamento_immagini?: boolean;
    data: Date;
  };
  
  updated_at: Date;
}

// Valutazione / Seduta (Fisio/Osteo)
interface SedutaTerapeutica {
  id: string;
  cliente_id: string;
  terapeuta_id: string;
  
  data: Date;
  durata_minuti: number;
  numero_seduta: number;      // Progressivo
  
  // Stato iniziale
  dolore_iniziale: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10; // VAS
  area_dolore?: string;       // Descrittivo o body map
  limitazioni_funzionali?: string[];
  
  // Test Funzionali
  valutazione_funzionale?: {
    // Range of Motion (ROM)
    articolazioni_testate: {
      nome: string;           // "Spalla DX"
      movimento: string;      // "Flessione"
      gradi_attuali: number;
      gradi_normali: number;
      deficit_percento: number;
      dolore_durante: boolean;
    }[];
    
    // Forza muscolare (MRC 0-5)
    forza_muscolare?: {
      gruppo_muscolare: string;
      lato: 'dx' | 'sx';
      grado: 0 | 1 | 2 | 3 | 4 | 5;
      note?: string;
    }[];
    
    // Test speciali
    test_speciali?: {
      nome: string;           // "Lachman", "Lasegue"...
      esito: 'positivo' | 'negativo';
      note?: string;
    }[];
    
    // Postura
    valutazione_posturale?: string;
  };
  
  // Trattamento
  tecniche_utilizzate: {
    tecnica: string;          // "Mobilizzazione articolare", "Massaggio"
    area: string;
    durata_minuti: number;
    note?: string;
  }[];
  
  // Esito
  dolore_finale: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
  miglioramento: 'nessuno' | 'minimo' | 'moderato' | 'notevole' | 'completo';
  
  // Piano
  raccomandazioni?: string[]; // "Esercizi da fare a casa"
  esercizi_assegnati?: {
    nome: string;
    descrizione: string;
    ripetizioni: string;
    frequenza: string;
  }[];
  
  prossima_seduta?: Date;
  frequenza_suggerita?: string;
  
  // Obiettivi terapia
  obiettivi_corto_termine?: string[];
  obiettivi_lungo_termine?: string[];
  
  // Note
  note_terapeuta: string;
  note_paziente?: string;
  
  // Fatturazione
  importo: number;
  pagato: boolean;
  
  created_at: Date;
}

// Per medici specialisti
interface VisitaMedica {
  id: string;
  paziente_id: string;
  medico_id: string;
  
  data: Date;
  tipo_visita: 'prima_visita' | 'controllo' | 'urgenza' | 'richiamo' | 'screening';
  
  // Anamnesi visita
  motivo_visita: string;
  anamnesi_remota?: string;   // Copia/incolla da scheda
  anamnesi_prossima?: string; // Sintomi recenti
  
  // Esame obiettivo
  esame_obiettivo: {
    stato_generale?: string;
    parametri_vitali?: {
      pressione?: string;     // "120/80"
      frequenza_cardiaca?: number;
      frequenza_respiratoria?: number;
      temperatura?: number;
      saturazione?: number;
    };
    esame_specific?: string;
  };
  
  // Diagnosi
  diagnosi: {
    codice_icd10?: string;
    descrizione: string;
    tipo: 'principale' | 'secondaria';
  }[];
  
  // Prescrizioni
  prescrizioni?: {
    farmaco: string;
    posologia: string;
    durata: string;
    note?: string;
  }[];
  
  // Indagini
  richieste_esami?: string[];
  richieste_visite_specialistiche?: {
    specialista: string;
    motivo: string;
    urgenza: 'programmata' | 'urgenza' | 'emergenza';
  }[];
  
  // Prognosi e controllo
  prognosi?: string;
  prossimo_controllo?: Date;
  
  // Certificazioni
  certificato_malattia?: {
    data_inizio: Date;
    data_fine: Date;
    giorni: number;
    codice: string;
  };
  
  note: string;
  created_at: Date;
}
```

#### Voice Agent - Intent Specifici
```
PRENOTAZIONE_VISITA
├─ "vorrei prenotare una visita"
├─ "devo fare il controllo"
├─ "ho male alla schiena"
└─ "devo rinnovare la ricetta"

INFO_TRATTAMENTO
├─ "quante sedute mi restano?"
├─ "quando è la prossima?"
├─ "posso saltare questa settimana?"
└─ "che esercizi devo fare?"

EMERGENZA_SANITARIA
├─ "ho un dolore fortissimo"
├─ "la medicina non funziona"
└─ "devo parlare col dottore"

RICETTA_RINNOVO
├─ "mi scade la ricetta"
├─ "ho finito le medicine"
└─ "posso avere il referto?"
```

#### Sblocco Licenza
- **Tier**: `medico`, `fisioterapia`, `osteopatia`
- **Feature**: Scheda anamnestica + sedute/visite + Voice medico

---

### 3. 🦷 STUDIO DENTISTICO

#### Business Model
- **Clienti**: Pazienti (ricorrenti per igiene/controllo)
- **Frequenza**: Igiene ogni 6 mesi, trattamenti su necessità
- **Valore**: €80-150 igiene, €300-3000 protesi/ortodonzia
- **Pain Point**: Odontogramma, storico carie, impianti

#### Schema Dati Completo
```typescript
// Odontogramma (Mappa 32 denti)
interface Odontogramma {
  id: string;
  cliente_id: string;
  
  // Versioning
  data: Date;
  versione: number;
  
  // Denti (sistema FDI 11-18, 21-28, 31-38, 41-48)
  denti: {
    numero: number;           // 11-48 FDI
    nome: string;             // "Incisivo superiore destro"
    
    // Stato attuale
    stato: 'sano' | 'caries' | 'otturato' | 'devitalizzato' | 'corona' | 'impianto' | 'estratt' | 'assente' | 'in_eruzione';
    
    // Superfici (per carie multi-superficie)
    superfici: {
      [key in 'mesiale' | 'distale' | 'vestibolare' | 'linguale' | 'occlusale' | 'palatina']: 
        'sano' | 'caries' | 'otturazione' | 'frattura' | null
    };
    
    // Interventi su questo dente
    storico: {
      data: Date;
      intervento_id: string;
      tipo: string;
      descrizione: string;
    }[];
    
    // Note specifiche
    note?: string;
  }[];
  
  // Annotazioni generali
  note_generali?: string;
  updated_at: Date;
}

// Trattamento Odontoiatrico
interface TrattamentoDentale {
  id: string;
  cliente_id: string;
  dentista_id: string;
  
  data: Date;
  
  // Classificazione
  tipo: 'igiene' | 'otturazione' | 'devitalizzazione' | 'corona' | 'ponte' | 'impianto' | 'protesi' | 'sbiancamento' | 'ortodonzia' | 'parodontale' | 'chirurgia' | 'estetica';
  
  // Denti coinvolti
  denti: {
    numero: number;
    superfici_trattate?: string[];
    nota?: string;
  }[];
  
  // Descrizione
  diagnosi: string;
  trattamento_eseguito: string;
  
  // Materiali
  materiali_utilizzati: {
    tipo: string;             // "Composito", "Ceramica", "Titanio"...
    marca?: string;
    colore?: string;          // Vita shade per corone
    lotto?: string;
    quantita?: number;
  }[];
  
  // Tecnica
  tecnica_applicazione?: string;
  anestesia: boolean;
  tipo_anestesia?: 'topica' | 'infiltrativa' | 'blocco' | 'sedazione';
  
  // Costi
  costo: number;
  sconto?: number;
  
  // Garanzia
  garanzia_mesi?: number;
  scadenza_garanzia?: Date;
  condizioni_garanzia?: string;
  
  // Radiografie
  radiografie?: {
    tipo: 'endorale' | 'panoramica' | 'teleradiografia' | 'cone_beam';
    descrizione?: string;
    allegato: string;
  }[];
  
  // Foto
  foto_intraorali?: string[];
  foto_extraorali?: string[];
  foto_prima_dopo?: {
    prima: string[];
    dopo: string[];
  };
  
  // Prossimi step
  prossimo_appuntamento?: Date;
  richiami?: string[];        // "Controllo in 6 mesi"
  
  note: string;
  created_at: Date;
}

// Impianto (tracciamento specifico)
interface ImpiantoDentale {
  id: string;
  cliente_id: string;
  posizione: number;          // Numero dente
  
  // Dati impianto
  data_inserimento: Date;
  data_carico?: Date;         // Protesi applicata
  
  marca_impianto: string;     // Straumann, Nobel...
  modello?: string;
  diametro_mm?: number;
  lunghezza_mm?: number;
  superficie?: 'liscia' | 'ruvida' | 'idrossiapatite';
  
  // Protesi su impianto
  tipo_protesi?: 'corona_cementata' | 'corona_avvitata' | 'ponte' | 'protesi_totale';
  materiale_protesi?: 'ceramica' | 'zirconia' | 'metallo_ceramica';
  
  // Garanzia impianto
  garanzia_impianto_anni: number;
  garanzia_protesi_anni?: number;
  
  // Manutenzione
  controlli_perimplantari: {
    data: Date;
    sondaggio: number;        // Profondità tasca mm
    mobilita: boolean;
    perdita_ossea?: boolean;
    note: string;
  }[];
  
  note: string;
}

// Ortodonzia
interface TrattamentoOrtodontico {
  id: string;
  cliente_id: string;
  
  tipo_apparecchio: 'fisso' | 'mobile' | 'invisibile' | 'linguale';
  marca?: string;             // Invisalign...
  
  data_inizio: Date;
  data_fine_prevista: Date;
  data_fine_effettiva?: Date;
  
  // Stadio
  stadio_attuale: 'attivo' | 'fine_trattamento' | 'contenizione';
  
  // Aligner (se invisibile)
  numero_alligner_totali?: number;
  aligner_attuale?: number;
  
  // Appuntamenti
  controlli: {
    data: Date;
    attivita: string;         // "Cambio filo", "Attivazione"
    note: string;
    prossimo_controllo: Date;
  }[];
  
  // Risultato
  foto_iniziali?: string[];
  foto_finali?: string[];
  teleradiografie?: string[];
  
  // Contenizione (fase post-trattamento)
  contenizione?: {
    tipo: 'fissa' | 'mobile';
    data_inizio: Date;
    durata_prevista: string;  // "2 anni"
  };
  
  costo_totale: number;
  rate?: {
    numero: number;
    importo: number;
    scadenze: Date[];
  };
}

// Parodontologia
interface ValutazioneParodontale {
  id: string;
  cliente_id: string;
  data: Date;
  
  // Sondaggio parodontale (6 punti per dente)
  sondaggi: {
    dente: number;
    
    mesiale: { profondita_mm: number; sanguinamento: boolean; };
    centro: { profondita_mm: number; sanguinamento: boolean; };
    distale: { profondita_mm: number; sanguinamento: boolean; };
    
    mobilita: 0 | 1 | 2 | 3;
    recessione_gengivale?: number; // mm
    
    classificazione_furca?: 'I' | 'II' | 'III' | null;
  }[];
  
  // Indici
  ipc?: number;               // Indice Placca
  ips?: number;               // Indice Sanguinamento
  
  // Diagnosi
  stadio_malp: 'I' | 'II' | 'III' | 'IV'; // Classificazione
  gravitazione?: 'lieve' | 'moderata' | 'grave';
  
  // Piano
  terapia_proposta: string;
  sedute_necessarie: number;
  
  note: string;
}
```

#### Voice Agent - Intent Specifici
```
PRENOTAZIONE
├─ "vorrei prenotare una pulizia"
├─ "devo fare il controllo"
└─ "ho perso una otturazione"

INFO_TRATTAMENTO
├─ "quanto costa un impianto?"
├─ "l'otturazione fatta a marzo è in garanzia?"
└─ "quando devo tornare per la corona?"

URGENZA_DENTALE
├─ "ho mal di denti fortissimo"
├─ "mi si è rotto un dente"
└─ "sanguinano le gengive"

ORTODONZIA
├─ "mi è caduto il apparecchio"
├─ "ho finito gli alligner"
└─ "il filo mi punge"
```

#### Sblocco Licenza
- **Tier**: `dentista`
- **Feature**: Odontogramma + trattamenti + impianti + Voice dentale

---

### 4. 💪 PALESTRA / PERSONAL TRAINER / STUDIO FITNESS

#### Business Model
- **Clienti**: Iscritti (abbonamenti ricorrenti)
- **Frequenza**: 2-5 volte/settimana
- **Valore**: €30-100/mese abbonamento, €50-80/sessione PT
- **Pain Point**: Tracciare progressi, schede allenamento, rinnovi

#### Schema Dati Completo
```typescript
// Scheda Fitness Completa
interface SchedaFitness {
  id: string;
  cliente_id: string;
  
  // Livello e obiettivi
  livello_attuale: 'sedentario' | 'principiante' | 'intermedio' | 'avanzato' | 'atleta';
  obiettivi_primari: ('perdita_grasso' | 'aumento_muscolare' | 'tonificazione' | 'forza' | 'resistenza' | 'flessibilita' | 'preparazione_gara')[];
  
  // Anamnesi sportiva
  storia_sportiva?: string;   // "Ho praticato nuoto 10 anni"
  infortuni_precedenti?: {
    tipo: string;
    data: Date;
    recupero_completo: boolean;
    note?: string;
  }[];
  
  // Condizioni mediche rilevanti
  controindicazioni?: string[]; // "Problemi al ginocchio"
  
  created_at: Date;
  updated_at: Date;
}

// Misurazioni Corporee (tracking progressi)
interface MisurazioneCorpo {
  id: string;
  cliente_id: string;
  data: Date;
  operatore_id?: string;      // Chi ha fatto la misurazione
  
  // Pesi e composizione
  peso_kg: number;
  altezza_cm?: number;
  bmi?: number;
  
  // Body composition (se bioimpedenziometro)
  massa_grassa_percento?: number;
  massa_muscolare_percento?: number;
  massa_ossea_kg?: number;
  acqua_percento?: number;
  metabolismo_basale_kcal?: number;
  
  // Circonferenze (cm)
  circonferenze: {
    collo?: number;
    spalle?: number;
    torace?: number;
    vita?: number;            // Ombelico
    fianchi?: number;         // Ossa iliache
    braccio_dx?: number;
    braccio_sx?: number;
    avambraccio_dx?: number;
    avambraccio_sx?: number;
    polpaccio_dx?: number;
    polpaccio_sx?: number;
    coscia_dx?: number;
    coscia_sx?: number;
  };
  
  // Plicometria (mm) - se calibro
  pliche?: {
    tricipite?: number;
    bicipite?: number;
    sottoscapolare?: number;
    soprailliaca?: number;
    addominale?: number;
    coscia?: number;
  };
  
  // Foto progresso
  foto?: {
    frontale?: string;
    laterale_dx?: string;
    posteriore?: string;
  };
  
  // Valutazione
  note?: string;
  
  // Target
  peso_target?: number;
  grasso_target?: number;
}

// Scheda Allenamento
interface SchedaAllenamento {
  id: string;
  cliente_id: string;
  trainer_id?: string;
  
  nome: string;               // "Scheda A - Petto/Tricipiti"
  obiettivo_specifico?: string;
  
  // Periodizzazione
  fase?: 'ipertrpofia' | 'forza' | 'definizione' | 'potenza' | 'resistenza';
  durata_prevista_ciclo?: string; // "4 settimane"
  
  // Struttura
  giorni_allenamento: GiornoAllenamento[];
  
  // Note
  note_tecniche?: string;
  note_cliente?: string;
  
  attiva: boolean;
  data_creazione: Date;
  data_attivazione?: Date;
}

interface GiornoAllenamento {
  id: string;
  giorno_settimana: 1 | 2 | 3 | 4 | 5 | 6 | 7; // Lun-Dom
  nome: string;               // "Upper Body", "Leg Day"
  
  gruppi_muscolari: string[]; // ["petto", "tricipiti"]
  
  esercizi: EsercizioInScheda[];
  
  note_giorno?: string;
}

interface EsercizioInScheda {
  id: string;
  ordine: number;
  
  esercizio_base: {
    id: string;
    nome: string;
    gruppo_muscolare: string;
    attrezzo: 'bilanciere' | 'manubri' | 'cavi' | 'corpo_libero' | 'macchinario' | 'kettlebell' | 'altro';
  };
  
  // Parametri lavoro
  serie: number;
  ripetizioni: string;        // "8-10" o "12"
  carico_kg?: number;         // Se prescritto
  rpe_target?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10; // Rate of Perceived Exertion
  
  // Tempo
  tempo?: string;             // "3-1-2-0" (eccentrica-pausa-concentrica-pausa)
  recupero_secondi?: number;
  
  // Tecnica
  note_tecniche?: string;
  varianti?: string[];
  
  // Alternativa
  esercizio_alternativo?: string;
}

// Sessione di Allenamento (log)
interface SessioneAllenamento {
  id: string;
  cliente_id: string;
  scheda_id?: string;
  
  data_inizio: Date;
  data_fine?: Date;
  durata_minuti?: number;
  
  // Contenuto
  esercizi_svolti: {
    esercizio_scheda_id: string;
    esercizio_nome: string;
    
    serie_completate: {
      numero: number;
      ripetizioni_fatte: number;
      carico_usato_kg: number;
      rpe?: number;
      note?: string;
    }[];
    
    completato: boolean;
    note_esercizio?: string;
  }[];
  
  // Sensazioni
  energia_inizio?: 1 | 2 | 3 | 4 | 5; // 1=scarsa, 5=ottima
  energia_fine?: 1 | 2 | 3 | 4 | 5;
  dolore_durante?: boolean;
  tipo_dolore?: string;
  
  // Intensità sessione
  volume_totale: number;      // Serie x Ripetizioni
  carico_totale: number;      // Somma carichi
  
  note_sessione?: string;
}

// Ingressi in struttura
interface AccessoPalestra {
  id: string;
  cliente_id: string;
  data_ora: Date;
  tipo: 'ingresso' | 'uscita';
  
  // Se tornello integrato
  dispositivo?: string;
  metodo_accesso?: 'tessera' | 'qr_code' | 'faccia' | 'manuale';
  
  // Analisi frequentazione
  durata_calcolata_minuti?: number; // Se ha timbrato uscita
}

// Abbonamenti
interface Abbonamento {
  id: string;
  cliente_id: string;
  
  tipo: 'mensile' | 'trimestrale' | 'semestrale' | 'annuale' | '10_ingressi' | 'open';
  data_inizio: Date;
  data_fine: Date;
  
  costo: number;
  pagato: boolean;
  rate?: number;
  
  // Inclusioni
  accessi_inclusi?: number;   // Null = illimitato
  personal_training_incluso?: number; // Ore
  
  attivo: boolean;
  rinnovo_automatico: boolean;
}
```

#### Voice Agent - Intent Specifici
```
PRENOTAZIONE_PT
├─ "vorrei prenotare un personal"
├─ "quando è libero Marco?"
└─ "posso spostare l'allenamento di domani?"

INFO_SCHEDA
├─ "che esercizi devo fare oggi?"
├─ "a quanti kg sono arrivato sullo squat?"
└─ "quando finisce questa scheda?"

RINNOVO
├─ "mi scade l'abbonamento?"
├─ "vorrei rinnovare per 3 mesi"
└─ "posso mettere in pausa?"

DIETA
├─ "ho fame dopo l'allenamento"
├─ "cosa posso mangiare?"
└─ "quante proteine mi servono?"
```

#### Sblocco Licenza
- **Tier**: `fitness`, `personal_trainer`
- **Feature**: Schede allenamento + misurazioni + tracking + Voice fitness

---

### 5. 💇 PARRUCCHIERE / BARBIERE

#### Business Model
- **Clienti**: Regolari (taglio ogni 4-8 settimane)
- **Frequenza**: Elevata, prenotazioni corte
- **Valore**: €15-50 taglio, €50-200 colore
- **Pain Point**: Preferenze cliente, storico colorazioni, prodotti

#### Schema Dati Completo
```typescript
// Analisi Capelli
interface AnalisiCapelli {
  id: string;
  cliente_id: string;
  data: Date;
  
  // Caratteristiche naturali
  tipo_naturale: 'lisci' | 'ondulati' | 'ricci' | 'crepuscolo';
  spessore_filo: 'fini' | 'medi' | 'spessi';
  densita: 'rado' | 'medio' | 'folto';
  porosita: 'bassa' | 'media' | 'alta'; // Quanto assorbono
  
  // Stato attuale
  lunghezza_attuale: 'cortissimi' | 'corti' | 'medio_corti' | 'spalle' | 'scapole' | 'lung' | 'lunghissimi';
  
  // Cuoio capelluto
  cuoio_capelluto: 'normale' | 'secco' | 'grasso' | 'sensibile' | 'forfora' | 'dermatite';
  
  // Trattamenti precedenti
  chemical_history: {
    colorazione: boolean;
    decolorazione: boolean;
    permanente: boolean;
    stiratura: boolean;
    cheratina: boolean;
    data_ultimo?: Date;
  };
  
  // Problemi
  problemi?: ('rottura' | 'doppie_punte' | 'secchezza' | 'opacita' | 'perdita' | 'grigio_prematuro')[];
  
  // Obiettivi
  obiettivi_cliente?: string[]; // "Allungare", "Più volume", "Coprire bianchi"
  
  // Stile vita
  styling_abituale?: string;    // "Lisci ogni giorno", "Naturale"
  frequenza_lavaggio?: string;
  
  // Prodotti consigliati
  prodotti_recommended: string[];
  prodotti_usati?: string[];
  
  note: string;
}

// Colorazione
interface ColorazioneCapelli {
  id: string;
  cliente_id: string;
  data: Date;
  operatore_id: string;
  
  // Motivo
  tipo: 'copertura_bianchi' | 'cambio_colore' | 'riflessi' | 'meches' | 'balayage' | 'shatush' | 'ombre' | 'colore_fantasia' | 'decolorazione' | 'ritocco_radici';
  
  // Formulazione (cruciale!)
  formulazione: {
    marca: string;              // Wella, L'Oreal, Davines...
    linea?: string;
    base?: string;              // "6/0"
    miscela?: string;           // "6/0 + 7/3 + 20vol"
    ossidante?: string;         // "20vol", "30vol"
    rapporto_miscela?: string;  // "1:1.5"
  };
  
  // Tecnica
  tecnica_applicazione: 'totale' | 'ricrescita' | 'mezze' | 'punte' | 'sezioni' | 'freehand';
  aree_specifiche?: string[];
  
  // Durata
  tempo_posa_minuti: number;
  temperatura?: string;
  
  // Risultato
  colore_raggiunto: string;
    tonalita?: string;          // "Biondo dorato caldo"
  
  // Dopo colore
  trattamento_post?: string;    // Olaplex, maschera...
  
  // Pre e Post
  foto_prima?: string[];
  foto_dopo?: string[];
  
  // Manutenzione
  prossima_colorazione?: Date;
  frequenza_suggerita?: string; // "4-5 settimane"
  
  // Costi
  costo: number;
  prodotti_usati_dettaglio?: string[];
  
  // Garanzia/Soddisfazione
  risultato_soddisfacente: boolean;
  note?: string;
}

// Taglio
interface TaglioCapelli {
  id: string;
  cliente_id: string;
  data: Date;
  
  tipo_taglio: 'rinfresco' | 'cambio_look' | 'sfoltimento' | 'scalato' | 'sfilato' | 'bob' | 'lob' | 'pixie' | 'undercut' | 'barba' | 'baffi';
  
  // Prima
  lunghezza_prima?: string;
  
  // Dopo
  lunghezza_dopo?: string;
  forma?: 'squadrata' | 'arrotondata' | 'scalata' | 'asimmetrica';
  frangia?: boolean;
  
  // Tecnica
  tecniche_usate?: string[];    // "Sfoltimento punta pettine", "Rasoio texturizzante"
  
  // Styling
  styling_finale?: string;
  prodotti_styling?: string[];
  
  // Media
  foto_prima?: string[];
  foto_dopo?: string[];
  video_tutorial?: string;      // Come rifare a casa
  
  note: string;
}

// Trattamenti
interface TrattamentoCapelli {
  id: string;
  cliente_id: string;
  data: Date;
  
  tipo: 'idratante' | 'nutriente' | 'ristrutturante' | 'keratina' | 'botox_capelli' | 'laminazione' | 'volumizzante' | 'anticaduta' | 'antiforfora' | 'purificante';
  
  prodotti: {
    marca: string;
    nome: string;
    linea?: string;
  }[];
  
  durata_minuti: number;
  
  // Risultato
  miglioramento_riscontrato?: 'minimo' | 'moderato' | 'notevole';
  
  prossimo_trattamento?: Date;
  frequenza_suggerita?: string;
  
  costo: number;
  note: string;
}

// Preferenze Cliente (accumulato nel tempo)
interface PreferenzeClienteParrucchiere {
  cliente_id: string;
  
  // Stile
  stile_preferito?: 'classico' | 'moderno' | 'alternativo' | 'naturale' | 'sofisticato';
  
  // Colorazione
  colore_naturale?: string;
  colori_preferiti?: string[];
  colori_da_evitare?: string[];
  
  // Tecnica
  ama_cambiare?: boolean;
  fedele_a_tecnica?: string;    // "Sempre balayage"
  
  // Conversazione
  preferenza_conversazione?: 'silenzio' | 'chiacchiere' | 'solo_professionale';
  
  // Servizi abbinati
  servizi_abituali?: string[];  // "Sempre massaggio shampoo 10min"
  
  // Prodotto
  compra_prodotti?: boolean;
  prodotti_in uso?: string[];
  
  // Frequenza
  frequenza_taglio_giorni?: number;
  frequenza_colore_giorni?: number;
  
  // Orari
  preferenza_orario?: 'mattina' | 'pomeriggio' | 'sera';
  giorni_preferiti?: string[];
  
  // Operatore
  operatore_preferito?: string;
  
  note_speciali?: string;       // "Allergica a X prodotto", "Non usa phon"
}
```

#### Voice Agent - Intent Specifici
```
PRENOTAZIONE
├─ "prenota per taglio e colore"
├─ "mi serve un ritocco delle radici"
└─ "posso venire per la barba?"

INFO_COLORAZIONE
├─ "quando ho fatto l'ultimo colore?"
├─ "che formula usi per i miei capelli?"
└─ "posso passare al biondo platino?"

TRATTAMENTO
├─ "i miei capelli sono secchi"
├─ "consigli qualcosa per la forfora?"
└─ "vorrei provare la laminazione"

PRODOTTI
├─ "mi serve lo shampoo che mi hai dato"
├─ "cosa uso per i ricci?"
└─ "avete maschera idratante?"
```

#### Sblocco Licenza
- **Tier**: `parrucchiere`, `barbiere`
- **Feature**: Storico colorazioni/tagli + formulazioni + Voice parrucchiere

---

### 6. 💆 CENTRO ESTETICO / SPA

#### Business Model
- **Clienti**: Regolari (trattamenti ricorrenti)
- **Frequenza**: Mensile/bisettimanale
- **Valore**: €50-150 trattamento, pacchetti €300-1000
- **Pain Point**: Storico pelle, preferenze, pacchetti

#### Schema Dati Completo
```typescript
// Analisi Pelle
interface AnalisiPelle {
  id: string;
  cliente_id: string;
  data: Date;
  estetista_id: string;
  
  // Fototipo (Scala Fitzpatrick I-VI)
  fototipo: 1 | 2 | 3 | 4 | 5 | 6;
  
  // Tipo pelle
  tipo_base: 'normale' | 'secca' | 'grassa' | 'mista' | 'sensibile' | 'acneica' | 'matura' | 'disidratata';
  
  // Condizioni specifiche
  condizioni: {
    disidratata: boolean;
    disgeusia: boolean;       // Grasso eccessivo
    sensibile: boolean;
    couperose: boolean;       // Capillari visibili
    couperose_grave: boolean; // Rosacea
    acne: boolean;
    acne_grado?: 'lieve' | 'moderata' | 'grave';
    macchie: boolean;
    tipo_macchie?: ('sole' | 'ormonali' | 'post_acne' | 'eta')[];
    rughe: boolean;
    rughe_tipo?: ('espressione' | 'gravita' | 'disidratazione')[];
    perdita_tonicita: boolean;
    occhiaie: boolean;
    borse: boolean;
    pori_dilatati: boolean;
    cicatrici: boolean;
    cheratosi?: boolean;
  };
  
  // Allergie/Sensibilità
  allergie_note?: string[];
  ingredienti_evitare?: string[];
  reazioni_precedenti?: string[];
  
  // Stile vita
  esposizione_sole?: 'nessuna' | 'moderata' | 'alta';
  fumatore?: boolean;
  alimentazione?: 'sana' | 'media' | 'scarsa';
  sonno?: 'buono' | 'insufficiente' | 'scarso';
  stress?: 'basso' | 'moderato' | 'alto';
  
  // Routine attuale
  routine_domestica?: string;
  prodotti_usati?: string[];
  
  // Obiettivi
  obiettivi: string[];
  priorità?: string;
  
  // Foto
  foto_viso?: {
    frontale: string;
    sinistra: string;
    destra: string;
  };
  
  note: string;
}

// Trattamento Estetico
interface TrattamentoEstetico {
  id: string;
  cliente_id: string;
  data: Date;
  estetista_id: string;
  
  tipo: 'pulizia_viso' | 'idratazione' | 'nutrizione' | 'antiage' | 'lifting' | 'acne' | 'macchie' | 'couperose' | 'ossigenoterapia' | 'radiofrequenza' | 'laser' | 'ultrasuoni' | 'ionoforesi' | 'dermapen' | 'microdermoabrasione' | 'peeling' | 'massaggio' | 'ceretta' | 'manicure' | 'pedicure' | 'ricostruzione_unghie' | 'extension_ciglia' | 'trucco_semipermanente';
  
  // Aree
  aree_trattate: ('viso' | 'collo' | 'decollete' | 'occhi' | 'labbra' | 'corpo' | 'schiena' | 'gambe' | 'braccia' | 'ascelle' | 'inguine' | 'mani' | 'piedi')[];
  
  // Prodotti
  prodotti_utilizzati: {
    marca: string;
    nome: string;
    linea?: string;
    quantita?: string;
  }[];
  
  // Protocollo
  durata_minuti: number;
  fasi_trattamento?: string[];
  
  // Risultato
  grado_miglioramento?: 1 | 2 | 3 | 4 | 5;
  effetto_immediato?: string;
  reazioni?: ('arrossamento' | 'sensibilita' | 'nessuna')[];
  
  // Raccomandazioni
  consigli_post?: string[];
  prodotti_consigliati?: string[];
  prossimo_appuntamento?: Date;
  frequenza_consigliata?: string;
  
  // Costi
  costo: number;
  
  // Note
  note_tecniche: string;
  note_cliente?: string;
}

// Epilazione (tracciamento specifico)
interface TrattamentoEpilazione {
  id: string;
  cliente_id: string;
  data: Date;
  
  metodo: 'ceretta' | 'filo_arabo' | 'laser' | 'luce_pulsata' | 'elettrocoagulazione';
  
  aree: {
    zona: 'sopracciglia' | 'labbro_superiore' | 'mento' | 'faccia' | 'ascelle' | 'braccia' | 'gambe_intere' | 'mezze_gambe' | 'cosce' | 'inguine_totale' | 'bikini' | 'glutei' | 'schiena' | 'petto' | 'addome';
    tempo_minuti?: number;
    costo?: number;
  }[];
  
  // Per laser/IPL
  seduzione_numero?: number;
  totale_sessioni_previste?: number;
  
  // Per ceretta
  tipo_cera?: 'liposolubile' | 'idrosolubile' | 'cera_tibia' | 'cera_calda';
  marca_cera?: string;
  
  // Reazione
  reazione_pelle?: 'nessuna' | 'lieve_arrossamento' | 'follicolite';
  
  // Prossima
  prossima_epilazione?: Date;
  
  costo_totale: number;
  note: string;
}

// Unghie
interface ServizioUnghie {
  id: string;
  cliente_id: string;
  data: Date;
  
  tipo: 'manicure' | 'manicure_spa' | 'pedicure' | 'pedicure_spa' | 'smalto_semipermanente' | 'ricostruzione_gel' | 'ricostruzione_acrilico' | 'riempimento' | 'copertura' | 'nail_art' | 'decori' | 'rimozione' | 'cura_cuticole';
  
  // Per ricostruzioni
  forma?: 'naturale' | 'squadrata' | 'arrotondata' | 'mandel' | 'stiletto' | 'ballerina' | 'baffo';
  lunghezza?: 'cortissime' | 'corte' | 'medie' | 'lunghe' | 'lunghe';
  
  // Colore/Smalto
  tipo_smalt?: 'classico' | 'semipermanente' | 'gel';
  colore?: string;
  marchio_smalt?: string;
  codice_colore?: string;
  
  // Decorazioni
  decorazioni?: ('glitter' | 'strass' | 'stamping' | 'water_decals' | 'freehand' | 'encapsulated')[];
  
  // Materiali
  marca_gel?: string;
  marca_acrilico?: string;
  
  // Durata
  durata_prevista_giorni?: number; // Quanto dovrebbe durare
  
  costo: number;
  note: string;
  foto?: string[];
}

// Pacchetti
interface PacchettoEstetico {
  id: string;
  cliente_id: string;
  
  nome: string;
  descrizione: string;
  
  // Contenuto
  trattamenti_inclusi: {
    tipo: string;
    quantita: number;
    usati: number;
  }[];
  
  // Validità
  data_acquisto: Date;
  data_scadenza?: Date;
  
  // Costi
  costo_pacchetto: number;
  valore_originale: number;   // Sconto applicato
  
  // Stato
  attivo: boolean;
  completato: boolean;
}
```

#### Voice Agent - Intent Specifici
```
PRENOTAZIONE
├─ "vorrei prenotare una pulizia viso"
├─ "mi serve la ceretta alle gambe"
└─ "posso fare la ricostruzione unghie?"

INFO_PELLE
├─ "che trattamento mi consigli per le macchie?"
├─ "i miei pori sono dilatati"
└─ "ho la pelle sensibile, posso fare il peeling?"

PACCHETTI
├─ "quanti trattamenti mi restano nel pacchetto?"
├─ "vorrei comprare un pacchetto da 10 massaggi"
└─ "il pacchetto scade a marzo?"

RINNOVO
├─ "la mia collega vuole venire"
├─ "fate trattamenti uomo?"
└─ "avete gift card?"
```

#### Sblocco Licenza
- **Tier**: `estetista`, `spa`, `centro_benessere`
- **Feature**: Analisi pelle + trattamenti + pacchetti + Voice estetista

---

## 🏗️ ARCHITETTURA UNIFICATA MULTI-VERTICALE

### Database Schema - Approccio Unico

```sql
-- ============================================================
-- SCHEMA UNIFICATO PER TUTTI I VERTICALI
-- ============================================================

-- 1. CAMPO vertical_type IN CLIENTI
ALTER TABLE clienti ADD COLUMN vertical_type TEXT CHECK (
  vertical_type IN (
    'generico',        -- CRM base senza scheda verticale
    'meccanico',       -- Auto officina
    'medico',          -- Studio medico
    'fisioterapia',    -- Fisio/osteo
    'dentista',        -- Studio dentistico
    'fitness',         -- Palestra/PT
    'parrucchiere',    -- Salone capelli
    'estetista'        -- Centro estetico
  )
);

-- 2. TABELLE SATELLITE PER OGNI VERTICALE
-- Ogni tabella ha foreign key a clienti

-- MECCANICO
CREATE TABLE mec_veicoli (...);
CREATE TABLE mec_interventi (...);
CREATE TABLE mec_preventivi (...);

-- MEDICO/FISIO
CREATE TABLE med_anamnesi (...);
CREATE TABLE med_sedute (...);
CREATE TABLE med_visite (...);

-- DENTISTA
CREATE TABLE den_odontogrammi (...);
CREATE TABLE den_trattamenti (...);
CREATE TABLE den_impianti (...);

-- FITNESS
CREATE TABLE fit_misurazioni (...);
CREATE TABLE fit_schede (...);
CREATE TABLE fit_sessioni (...);

-- PARRUCCHIERE
CREATE TABLE par_colorazioni (...);
CREATE TABLE par_tagli (...);
CREATE TABLE par_trattamenti (...);

-- ESTETISTA
CREATE TABLE est_analisi_pelle (...);
CREATE TABLE est_trattamenti (...);
CREATE TABLE est_pacchetti (...);

-- 3. TABELLA LICENZE_VERTICALI
-- Traccia quali verticali sono attivi per ogni installazione
CREATE TABLE licenze_verticali (
  id INTEGER PRIMARY KEY CHECK (id = 1), -- Singleton
  
  -- Verticali abilitati (BOOLEAN/INTEGER 0/1)
  meccanico_enabled INTEGER DEFAULT 0,
  medico_enabled INTEGER DEFAULT 0,
  fisioterapia_enabled INTEGER DEFAULT 0,
  dentista_enabled INTEGER DEFAULT 0,
  fitness_enabled INTEGER DEFAULT 0,
  parrucchiere_enabled INTEGER DEFAULT 0,
  estetista_enabled INTEGER DEFAULT 0,
  
  -- Configurazione
  verticali_attivi TEXT, -- JSON array ["meccanico", "dentista"]
  
  -- License key reference
  license_key TEXT,
  
  updated_at TEXT DEFAULT (datetime('now'))
);
```

### Pattern Code - Factory + Strategy

```rust
// Rust - Domain Layer

pub enum VerticalType {
  Generico,
  Meccanico,
  Medico,
  Fisioterapia,
  Dentista,
  Fitness,
  Parrucchiere,
  Estetista,
}

pub trait VerticalModule {
  fn vertical_type(&self) -> VerticalType;
  fn get_schema(&self) -> VerticalSchema;
  fn validate_data(&self, data: &JsonValue) -> Result<(), ValidationError>;
  fn get_tabs(&self) -> Vec<TabDefinition>;
}

// Implementazioni
pub struct MeccanicoModule;
impl VerticalModule for MeccanicoModule {
  fn vertical_type(&self) -> VerticalType { VerticalType::Meccanico }
  fn get_tabs(&self) -> Vec<TabDefinition> {
    vec![
      TabDefinition::new("veicoli", "🚗 Veicoli"),
      TabDefinition::new("interventi", "🔧 Interventi"),
      TabDefinition::new("scadenze", "⏰ Scadenze"),
    ]
  }
}

// Factory
pub struct VerticalModuleFactory;
impl VerticalModuleFactory {
  pub fn create(vertical: VerticalType) -> Box<dyn VerticalModule> {
    match vertical {
      VerticalType::Meccanico => Box::new(MeccanicoModule),
      VerticalType::Medico => Box::new(MedicoModule),
      // ... altri
    }
  }
}
```

```typescript
// React - Frontend

interface VerticalConfig {
  type: VerticalType;
  name: string;
  icon: string;
  color: string;
  tabs: TabConfig[];
  voiceIntents: string[];
}

const VERTICALS: Record<VerticalType, VerticalConfig> = {
  meccanico: {
    type: 'meccanico',
    name: 'Autofficina',
    icon: 'Car',
    color: '#3B82F6',
    tabs: [
      { id: 'veicoli', label: 'Veicoli', component: VeicoliTab },
      { id: 'interventi', label: 'Interventi', component: InterventiTab },
      { id: 'scadenze', label: 'Scadenze', component: ScadenzeTab },
    ],
    voiceIntents: ['nuovo_intervento', 'info_veicolo', 'preventivo']
  },
  medico: {
    type: 'medico',
    name: 'Studio Medico',
    icon: 'Stethoscope',
    color: '#EF4444',
    tabs: [
      { id: 'anamnesi', label: 'Anamnesi', component: AnamnesiTab },
      { id: 'visite', label: 'Visite', component: VisiteTab },
      { id: 'esami', label: 'Esami', component: EsamiTab },
    ],
    voiceIntents: ['nuova_visita', 'info_trattamento', 'emergenza']
  },
  // ... altri
};

// Componente dinamico
function SchedaClienteVerticale({ clienteId, verticalType }: Props) {
  const config = VERTICALS[verticalType];
  
  return (
    <VerticalProvider type={verticalType}>
      <Tabs>
        {config.tabs.map(tab => (
          <Tab key={tab.id} value={tab.id}>
            <tab.component clienteId={clienteId} />
          </Tab>
        ))}
      </Tabs>
    </VerticalProvider>
  );
}
```

---

## 🎙️ VOICE AGENT - ARCHITETTURA MULTI-VERTICALE

```python
# Python - Voice Pipeline

class VerticalIntentClassifier:
    """Rileva il verticale dal contesto e dagli intent"""
    
    VERTICAL_INTENTS = {
        'meccanico': {
            'patterns': [
                r'\b(auto|macchina|veicolo|motore|freno|cambio|olio|tagliando|revisione)\b',
                r'\b(gomme|pneumatici|batteria|marmitta|frizione|sospensioni)\b',
            ],
            'entities': ['targa', 'marca_auto', 'km', 'tipo_problema']
        },
        'medico': {
            'patterns': [
                r'\b(dottore|medico|visita|esame|sintomo|dolore|mal di|ricetta)\b',
                r'\b(febbre|influenza|tosse|schiena|pancia|testa|gola)\b',
            ],
            'entities': ['parte_corpo', 'sintomo', 'urgenza', 'farmaco']
        },
        'dentista': {
            'patterns': [
                r'\b(dentista|denti|dente|carie|otturazione|pulizia|dentiere)\b',
                r'\b(gengive|molare|incisivo|corona|impianto|apparecchio)\b',
            ],
            'entities': ['numero_dente', 'tipo_dolore', 'trattamento']
        },
        'fitness': {
            'patterns': [
                r'\b(palestra|allenamento|scheda|pesi|cardio|massa|dimagrire)\b',
                r'\b(personal|trainer|squat|panca|manubri|tapis|corso)\b',
            ],
            'entities': ['obiettivo', 'gruppo_muscolare', 'esercizio']
        },
        'parrucchiere': {
            'patterns': [
                r'\b(capelli|taglio|colore|tinta|shampoo|piega|ricci|lisci)\b',
                r'\b(biondo|more|rosso|decolorazione|meches|taglio|barba)\b',
            ],
            'entities': ['lunghezza_capelli', 'colore_target', 'tecnica']
        },
        'estetista': {
            'patterns': [
                r'\b(estetista|viso|corpo|massaggio|ceretta|unghie|ciglia)\b',
                r'\b(pulizia|idratare|antiage|epilazione|manicure|pedicure)\b',
            ],
            'entities': ['zona_corpo', 'trattamento', 'problema_pelle']
        }
    }
    
    def detect_vertical(self, text: str) -> Optional[str]:
        """Rileva il verticale più probabile dal testo"""
        scores = {}
        for vertical, config in self.VERTICAL_INTENTS.items():
            score = 0
            for pattern in config['patterns']:
                if re.search(pattern, text, re.I):
                    score += 1
            scores[vertical] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return None


class VerticalResponseGenerator:
    """Genera risposte appropriate per il verticale"""
    
    TEMPLATES = {
        'meccanico': {
            'greeting': "Buongiorno, sono Sara dell'officina. Come posso aiutarla con la sua auto?",
            'ask_vehicle': "Mi può dire la targa o il modello del veicolo?",
            'booking_confirm': "Perfetto, la prenoto per il {data} alle {ora}. Ricordi di portare il libretto di manutenzione.",
        },
        'medico': {
            'greeting': "Buongiorno, sono Sara dello studio medico. Mi dica il motivo della chiamata.",
            'ask_symptoms': "Mi descriva i sintomi per capire l'urgenza.",
            'booking_confirm': "La visita è fissata per {data} alle {ora}. Porto con sé gli esami recenti se li ha.",
        },
        # ... altri verticali
    }
```

---

## 📊 RIEPILOGO VERTICALI

| Verticale | Entità Chiave | Tassonomia Profonda | Voice Specifico |
|-----------|---------------|---------------------|-----------------|
| **🚗 Meccanico** | Veicoli, Interventi, Ricambi | Marcè, Modelli, Sistemi auto | Problemi tecnici, Scadenze |
| **🏥 Medico** | Anamnesi, Visite, Esami | ICD-10, Farmaci, Sintomi | Sintomi, Urgenze, Ricette |
| **🦷 Dentista** | Denti, Trattamenti, Impianti | FDI 32 denti, Materiali | Dolori, Tipo trattamento |
| **💪 Fitness** | Schede, Misurazioni, Sessioni | Gruppi muscolari, Esercizi | Obiettivi, Pesi, Forma |
| **💇 Parrucchiere** | Colorazioni, Tagli, Preferenze | Formulazioni colori, Tecniche | Colori, Lunghezze, Stili |
| **💆 Estetista** | Pelle, Trattamenti, Pacchetti | Fototipi, Prodotti, Zone | Trattamenti, Preferenze |

---

## 🎯 SISTEMA DI LICENZE

```
FLUXION LICENSE TIERS
═══════════════════════════════════════════════

BASE (€199/lifetime)
├─ CRM Clienti generico
├─ Calendario Appuntamenti
├─ Fatturazione
└─ 1 Verticale a scelta

PROFESSIONAL (€399/lifetime)  
├─ Tutto di Base
├─ 3 Verticali simultanei
├─ Voice Agent SARA
├─ Analytics avanzate
└─ Multi-location (3 sedi)

ENTERPRISE (€799/lifetime)
├─ Tutti i 6 Verticali
├─ Unlimited locations
├─ Custom branding
├─ API access
└─ Priority support

ADD-ONS
├─ Verticale extra: +€50
├─ Location extra: +€30/sede
└─ White label: +€200
```

---

## 🚀 CONCLUSIONE

Questa ricerca approfondita definisce **6 verticali completi** con:
- ✅ Schemi dati dettagliati e specifici
- ✅ Tassonomie settoriali accurate
- ✅ Voice intents per ogni settore
- ✅ Architettura unificata ma flessibile
- ✅ Sistema licenze per sblocco verticale

**Il sistema permette di:**
1. Attivare solo i verticali della licenza acquistata
2. Avere UI/UX specifica per ogni settore
3. Usare Voice Agent con vocabolario settoriale
4. Aggiungere nuovi verticali senza refactor

---

*Research completata: 2026-02-03*
*Versione: 1.0*
*Prossimo step: Implementazione architettura multi-verticale*
