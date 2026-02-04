# 🏢 PROMPT KIMI 2.5 - Schede Clienti Verticali per FLUXION

## 🎯 OBIETTIVO

Implementare un sistema di **schede clienti dinamiche e verticali** dove ogni tipologia di PMI (meccanico, medico, dentista, palestra, estetista, parrucchiere) ha una scheda cliente completamente personalizzata con campi specifici, storico dedicato e tassonomia profonda (specialmente in ambito medico).

---

## 🏗️ STACK TECNOLOGICO FLUXION

### Backend
- **Framework**: Tauri 2.x (Rust 1.75+)
- **Database**: SQLite 3.x con SQLx (async)
- **Pattern**: Domain-Driven Design, Repository Pattern
- **Architecture**: Commands → Services → Repositories → Domain

### Frontend
- **Framework**: React 19 + TypeScript 5.x
- **Styling**: Tailwind CSS 4.x + shadcn/ui
- **State**: Zustand (client) + TanStack Query (server)
- **Forms**: React Hook Form + Zod validation

### Voice Agent
- **Language**: Python 3.9+
- **Stack**: FastAPI, Groq LLM, Piper TTS
- **Pattern**: 5-layer RAG pipeline

### Database Schema Base (già esistente)
```sql
-- Tabelle core esistenti
clienti (id, nome, cognome, email, telefono, data_nascita, ...)
servizi (id, nome, categoria, prezzo, durata_minuti, ...)
operatori (id, nome, cognome, ruolo, ...)
appuntamenti (id, cliente_id, servizio_id, data_ora_inizio, ...)
impostazioni (chiave, valore, tipo)
audit_log (GDPR compliant, già implementato)
```

---

## 📋 REQUISITI VERTICALI DETTAGLIATI

### 1. 🚗 AUTOFFICINA / MECCANICO

#### Entità Principali
- **Cliente** (persona fisica)
- **Veicolo** (auto, moto, furgone) - MULTIPLO per cliente
- **Intervento** (lavoro effettuato su un veicolo)

#### Schema Veicolo
```typescript
interface Veicolo {
  id: string;
  cliente_id: string;
  tipo: 'auto' | 'moto' | 'furgone' | 'altro';
  marca: string;           // Fiat, BMW, Toyota...
  modello: string;         // Panda, X3, Yaris...
  anno: number;
  targa: string;           // AB123CD
  telaio: string;          // VIN number
  km: number;              // Kilometraggio attuale
  cilindrata: number;      // cc
  alimentazione: 'benzina' | 'diesel' | 'gpl' | 'metano' | 'elettrico' | 'ibrido';
  ultima_revisione?: Date;
  scadenza_bollo?: Date;
  scadenza_assicurazione?: Date;
  note: string;
  created_at: Date;
}
```

#### Schema Intervento (Storico Manutenzione)
```typescript
interface Intervento {
  id: string;
  veicolo_id: string;
  cliente_id: string;
  data: Date;
  km: number;                    // Km al momento dell'intervento
  tipo: 'tagliando' | 'riparazione' | 'sostituzione' | 'controllo' | 'garantia';
  descrizione: string;
  
  // Dettaglio lavori
  lavori: Lavoro[];              // Array di voci singole
  
  // Componenti
  parti_sostituite: Pezzo[];     // Ricambi usati
  
  // Costi
  costo_ricambi: number;
  costo_lavorazione: number;
  costo_totale: number;
  
  // Garanzia
  garanzia_mesi: number;
  scadenza_garanzia?: Date;
  
  // Documenti
  foto: string[];                // Path foto intervento
  allegati: string[];            // PDF fatture, preventivi
  
  operator_id: string;
  note_interne: string;
}

interface Lavoro {
  descrizione: string;
  ore_lavoro: number;
  costo_orario: number;
  totale: number;
}

interface Pezzo {
  codice_ricambio: string;
  descrizione: string;
  quantita: number;
  prezzo_unitario: number;
  totale: number;
  fornitore?: string;
}
```

#### Tassonomia Meccanica
- **Sistemi**: Motore, Trasmissione, Freni, Sospensioni, Elettronica, Carrozzeria, Climatizzazione
- **Interventi comuni**: Cambio olio, Sostituzione freni, Revisione generale, Diagnostica elettronica

---

### 2. 🏥 STUDIO MEDICO / FISIOTERAPISTA

#### Schema Anamnestico Completo
```typescript
interface SchedaMedica {
  id: string;
  cliente_id: string;
  
  // === ANAGRAFICA MEDICA ===
  altezza_cm?: number;
  peso_kg?: number;
  gruppo_sanguigno?: 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | '0+' | '0-';
  
  // === ALLERGIE E INTOLLERANZE ===
  allergie: Allergia[];          // Farmaci, alimenti, ambientali
  intolleranze: string[];
  
  // === PATOLOGIE ===
  patologie_attuali: Patologia[];
  patologie_precedenti: Patologia[];
  patologie_familiari: PatologiaFamiliare[];
  
  // === FARMACI ===
  farmaci_in_corso: Farmaco[];
  farmaci_precedenti: Farmaco[];
  
  // === STILE DI VITA ===
  fumatore: 'no' | 'ex' | 'si' | 'occasionale';
  alcol: 'no' | 'moderato' | 'regolare';
  attivita_fisica: 'sedentaria' | 'moderata' | 'intensa';
  professione?: string;
  
  // === ESAMI E DOCUMENTI ===
  esami_diagnostici: Esame[];
  documenti_medici: DocumentoMedico[];
  
  // === FISIOTERAPIA SPECIFICO ===
  valutazioni_fisioterapiche: ValutazioneFisio[];
  
  updated_at: Date;
}

interface Allergia {
  tipo: 'farmaco' | 'alimento' | 'ambientale' | 'altro';
  agente: string;                // Es: "Penicillina", "Polline", "Fragole"
  reazione: string;              // Es: "Urticaria", "Shock anafilattico"
  gravita: 'lieve' | 'moderata' | 'grave';
  data_scoperta?: Date;
}

interface Patologia {
  codice_icd10?: string;         // Classificazione internazionale
  nome: string;
  data_inizio?: Date;
  data_fine?: Date;
  stato: 'attiva' | 'in_trattamento' | 'risolta' | 'cronica';
  note: string;
}

interface PatologiaFamiliare {
  parentela: 'padre' | 'madre' | 'fratello' | 'sorella' | 'nonno' | 'nonna' | 'altro';
  patologia: string;
  note?: string;
}

interface Farmaco {
  nome: string;
  principio_attivo: string;
  dosaggio: string;              // Es: "500mg"
  frequenza: string;             // Es: "2 volte al giorno"
  data_inizio: Date;
  data_fine?: Date;
  motivo: string;
  prescritto_da?: string;
}

interface Esame {
  tipo: 'sangue' | 'urine' | 'radiografia' | 'risonanza' | 'tomografia' | 'ecografia' | 'altro';
  data: Date;
  struttura?: string;
  medico_refertante?: string;
  referto_breve: string;
  allegati: string[];            // Path file
  valori?: ValoreEsame[];        // Per esami numerici
}

interface ValoreEsame {
  parametro: string;             // Es: "Glicemia", "Colesterolo totale"
  valore: number;
  unita: string;                 // Es: "mg/dL"
  range_riferimento?: string;    // Es: "70-110"
  esito: 'normale' | 'alterato' | 'critico';
}

interface ValutazioneFisio {
  data: Date;
  fisioterapista_id: string;
  
  // Valutazione funzionale
  scala_dolore: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
  area_dolore: string;           // Descrittivo o mappa
  
  // Range of Motion (ROM)
  articolazioni: Articolazione[];
  
  // Forza muscolare
  forza_muscolare: string;
  
  // Test specifici
  test_effettuati: TestFisio[];
  
  // Piano trattamento
  diagnosi_funzionale: string;
  obiettivi: string[];
  numero_sedute_previste: number;
  frequenza: string;             // Es: "2 volte a settimana"
  
  // Progress
  note: string;
}

interface Articolazione {
  nome: string;                  // Es: "Spalla dx", "Ginocchio sx"
  flessione?: number;            // Gradi
  estensione?: number;
  abduzione?: number;
  adduzione?: number;
  rotazione_interna?: number;
  rotazione_esterna?: number;
  note?: string;
}
```

---

### 3. 🦷 STUDIO DENTISTICO

#### Schema Odontoiatrico
```typescript
interface SchedaDentale {
  id: string;
  cliente_id: string;
  
  // === DIAGRAMMA ODONTOIATRICO ===
  // Mappa dei 32 denti con stato
  denti: Dente[];
  
  // === ANAMNESI ODONTOIATRICA ===
  abitudini: {
    fumatore: boolean;
    bruxismo: boolean;           // Digging dei denti
    succhiamento_dito: boolean;
    respiro_orale: boolean;
    igiene_orale: 'scarsa' | 'sufficiente' | 'buona' | 'ottima';
  };
  
  // === TRATTAMENTI ===
  trattamenti: TrattamentoDentale[];
  
  // === ORTODONZIA ===
  ortodonzia?: {
    in_trattamento: boolean;
    tipo_apparecchio?: 'fisso' | 'mobile' | 'invisibile';
    data_inizio?: Date;
    data_fine_prevista?: Date;
  };
  
  // === PARODONTO ===
  parodontite: boolean;
  sondaggio_parodontale?: SondaggioParo[];
  
  // === IMPIANTI ===
  impianti: Impianto[];
  
  // === DOCUMENTI ===
  radiografie: Radiografia[];
  foto_intraorali: string[];
  modelli_gesso: string[];
  
  updated_at: Date;
}

interface Dente {
  numero: number;                // 1-32 (sistema FDI)
  nome: string;                  // Es: "18 - Terzo molare dx sup"
  stato: 'sano' | 'carie' | 'otturato' | 'devitalizzato' | 'corona' | 'estratt' | 'assente' | 'impianto';
  superfici: {
    mesiale: StatoSuperficie;
    distale: StatoSuperficie;
    vestibolare: StatoSuperficie;
    linguale: StatoSuperficie;
    occlusale: StatoSuperficie;
  };
  note?: string;
}

type StatoSuperficie = 'sano' | 'carie' | 'otturazione' | 'frattura' | null;

interface TrattamentoDentale {
  id: string;
  data: Date;
  denti_coinvolti: number[];
  tipo: 'igiene' | 'otturazione' | 'devitalizzazione' | 'corona' | 'estrazione' | 'impianto' | 'sbiancamento' | 'protesi' | 'parodontale' | 'ortodontico';
  descrizione: string;
  anestesia: boolean;
  materiali_usati: string[];
  costo: number;
  garanzia_mesi: number;
  note: string;
  allegati: string[];
}

interface Impianto {
  id: string;
  posizione: number;             // Numero dente
  data_inserimento: Date;
  marca?: string;
  modello?: string;
  diametro?: number;
  lunghezza?: number;
  carico_immediato: boolean;
  note: string;
}

interface SondaggioParo {
  data: Date;
  dente: number;
  sondaggi: {
    mesiale: { profondita: number; sanguinamento: boolean };
    centrale: { profondita: number; sanguinamento: boolean };
    distale: { profondita: number; sanguinamento: boolean };
  };
  mobilita: 0 | 1 | 2 | 3;
}
```

---

### 4. 💪 PALESTRA / PERSONAL TRAINER

#### Schema Fitness
```typescript
interface SchedaFitness {
  id: string;
  cliente_id: string;
  
  // === COMPOSIZIONE CORPOREA ===
  misurazioni: MisurazioneCorpo[];
  
  // === ANAMNESI SPORTIVA ===
  livello_attivita: 'sedentario' | 'principiante' | 'intermedio' | 'avanzato' | 'atleta';
  obiettivi: ObiettivoFitness[];
  
  // === ALLENAMENTO ===
  scheda_allenamento: Allenamento[];
  
  // === NUTRIZIONE ===
  piani_alimentari: PianoAlimentare[];
  
  // === STORICO ===
  ingressi: IngressoPalestra[];
  
  updated_at: Date;
}

interface MisurazioneCorpo {
  data: Date;
  peso_kg: number;
  altezza_cm: number;
  bmi: number;
  
  // Circonferenze (cm)
  circonferenze: {
    collo: number;
    spalle: number;
    petto: number;
    braccio_dx: number;
    braccio_sx: number;
    vita: number;
    fianchi: number;
    coscia_dx: number;
    coscia_sx: number;
    polpaccio_dx: number;
    polpaccio_sx: number;
  };
  
  // Body composition (se disponibile)
  massa_grassa_percento?: number;
  massa_muscolare_percento?: number;
  massa_ossa_percento?: number;
  acqua_percento?: number;
  
  // Plicometria (mm)
  pliche?: {
    tricipite: number;
    bicipite: number;
    sottoscapolare: number;
    soprailliaca: number;
    addominale: number;
    coscia: number;
  };
  
  note: string;
  operatore_id: string;
}

interface ObiettivoFitness {
  descrizione: string;
  tipo: 'perdita_peso' | 'aumento_massa' | 'tonificazione' | 'resistenza' | 'forza' | 'flexibility' | 'competizione';
  data_inizio: Date;
  data_target?: Date;
  target_numerico?: number;
  completato: boolean;
  data_completamento?: Date;
}

interface Allenamento {
  id: string;
  nome: string;                  // Es: "Scheda A - Petto/Tricipiti"
  livello: 'principiante' | 'intermedio' | 'avanzato';
  obiettivo: string;
  durata_prevista: number;       // Minuti
  
  esercizi: EsercizioScheda[];
  
  data_creazione: Date;
  attiva: boolean;
}

interface EsercizioScheda {
  esercizio_id: string;
  nome: string;
  gruppo_muscolare: string;
  
  // Serie e ripetizioni
  serie: number;
  ripetizioni: string;           // Es: "8-10" o "12"
  recupero_secondi: number;
  
  // Carico
  carico_kg?: number;
  carico_personalizzato?: boolean;
  
  // Tecnica
  tempo_esecuzione?: string;     // Es: "3-1-2-0" (eccentrica-pausa-concentrica-pausa)
  note_tecniche?: string;
  
  ordine: number;
}

interface IngressoPalestra {
  data_ora: Date;
  tipo: 'ingresso' | 'uscita';
  // Per palestre con tornelli automatici
}
```

---

### 5. 💇 PARRUCCHIERE / BARBIERE

#### Schema Capelli
```typescript
interface SchedaCapelli {
  id: string;
  cliente_id: string;
  
  // === CARATTERISTICHE CAPELLI ===
  tipo_capelli: 'lisci' | 'ondulati' | 'ricci' | 'crepuscolo';
  spessore: 'fini' | 'medi' | 'spessi';
  densita: 'rado' | 'medio' | 'folto';
  porosita: 'bassa' | 'media' | 'alta';
  sebo: 'secco' | 'normale' | 'grasso' | 'misto';
  cuoio_capelluto: 'normale' | 'sensibile' | 'irritato' | 'forfora' | 'dermatite';
  
  // === COLORAZIONE ===
  colorazioni: Colorazione[];
  
  // === TRATTAMENTI ===
  trattamenti: TrattamentoCapelli[];
  
  // === STORICO TAGLI ===
  tagli: Taglio[];
  
  // === PRODOTTI CONSIGLIATI ===
  prodotti_usati: string[];      // Reference a prodotti in magazzino
  
  // === FOTO ===
  foto: FotoCapelli[];
  
  updated_at: Date;
}

interface Colorazione {
  id: string;
  data: Date;
  tipo: 'copertura_bianchi' | 'cambio_colore' | 'riflessante' | 'decolorazione' | 'schiariture' | 'balayage' | 'shatush' | 'colore_fantasia';
  
  // Formulazione
  colore_target: string;
  tonalita: string;
  marca_tinta?: string;
  linea_colore?: string;
  formulazione: string;          // Es: "6.0 + 20vol + 1:1.5"
  
  // Tecnica
  tecnica_applicazione: 'totale' | 'ricrescita' | 'mezze' | 'punte' | 'sezioni';
  tempo_posa_minuti: number;
  
  // Risultato
  risultato: 'ottimale' | 'soddisfacente' | 'insoddisfacente';
  note?: string;
  
  // Durata stimata
  prossima_colorazione?: Date;
}

interface TrattamentoCapelli {
  id: string;
  data: Date;
  tipo: 'idratante' | 'ristrutturante' | 'keratina' | 'botox' | ' laminazione' | 'ricostruzione' | 'antiforfora' | 'sebo_regolatore';
  prodotti_usati: string[];
  durata_minuti: number;
  risultato: string;
  prossimo_trattamento?: Date;
}

interface Taglio {
  id: string;
  data: Date;
  tipo_taglio: 'rinfresco' | 'cambio_look' | 'sfoltimento' | 'scalato' | 'lob' | 'bob' | 'undercut' | 'barba' | 'baffi';
  tecnica: string;
  lunghezza_partenza?: string;
  lunghezza_finale?: string;
  foto_prima?: string[];
  foto_dopo?: string[];
  note: string;
}
```

---

### 6. 💆 CENTRO ESTETICO

#### Schema Estetica
```typescript
interface SchedaEstetica {
  id: string;
  cliente_id: string;
  
  // === TIPOLOGIA PELLE ===
  tipo_pelle: 'normale' | 'secca' | 'grassa' | 'mista' | 'sensibile' | 'acneica' | 'matura';
  fototipo: 1 | 2 | 3 | 4 | 5 | 6;  // Scala Fitzpatrick
  
  // === CONDIZIONI ===
  condizioni: {
    disidratata: boolean;
    sensibile: boolean;
    couperose: boolean;
    acne: boolean;
    macchie: boolean;
    rughe: boolean;
    perdita_tonicita: boolean;
    occhiaie: boolean;
    borse: boolean;
  };
  
  // === ALLERGIE ===
  allergie: string[];            // Ingredienti specifici
  intolleranze: string[];
  
  // === TRATTAMENTI ===
  trattamenti: TrattamentoEstetico[];
  
  // === EPILAZIONE ===
  epilazioni: Epilazione[];
  
  // === UNGHIE ===
  servizi_unghie: ServizioUnghie[];
  
  // === MASSAGGI ===
  massaggi: Massaggio[];
  
  // === PACCHETTI ===
  pacchetti_attivi: PacchettoEstetico[];
  
  updated_at: Date;
}

interface TrattamentoEstetico {
  id: string;
  data: Date;
  tipo: 'pulizia_viso' | 'idratazione' | 'antiage' | 'acne' | 'macchie' | 'ossigenoterapia' | 'radiofrequenza' | 'laser' | 'peeling' | 'dermapen' | 'ultrasuoni' | 'ionoforesi';
  
  // Prodotti
  prodotti_usati: {
    nome: string;
    marca: string;
    linea: string;
  }[];
  
  // Protocollo
  durata_minuti: number;
  aree_trattate: string[];
  
  // Valutazione
  grado_miglioramento: 1 | 2 | 3 | 4 | 5;
  note_cliente: string;
  note_operatrice: string;
  
  // Prossimo appuntamento
  frequenza_consigliata_giorni: number;
  prossimo_appuntamento?: Date;
}

interface Epilazione {
  id: string;
  data: Date;
  metodo: 'ceretta' | 'filo' | 'laser' | 'light' | 'elettronico';
  area_corpo: 'sopracciglia' | 'labbro' | 'mento' | 'ascelle' | 'braccia' | 'gambe_intere' | 'mezzegambe' | 'inguine' | 'schiena' | 'petto';
  
  // Per laser/IPL
  numero_sessione?: number;
  totale_sessioni_previste?: number;
  
  // Prodotto
  tipo_cera?: 'liposolubile' | 'idrosolubile' | 'calda';
  marca_cera?: string;
  
  note: string;
  prossima_epilazione?: Date;
}

interface ServizioUnghie {
  id: string;
  data: Date;
  tipo: 'manicure' | 'pedicure' | 'ricostruzione_gel' | 'ricostruzione_acrilico' | 'semipermanente' | 'nail_art' | 'trattamento_cuticole';
  
  // Per ricostruzioni
  lunghezza?: 'cortissime' | 'corte' | 'medie' | 'lunghe';
  forma?: 'squadrata' | 'rotonda' | 'mandel' | 'stiletto' | 'ballerina';
  colore?: string;
  decorazioni?: string[];
  
  // Materiali
  marca_gel?: string;
  marca_smalto?: string;
  
  durata_minuti: number;
  costo: number;
  
  foto?: string[];
  note: string;
}
```

---

## 🏗️ ARCHITETTURA DATABASE PROPOSTA

### Opzione 1: JSON Schema Flessibile (Consigliata)
```sql
-- Tabella principale estesa
ALTER TABLE clienti ADD COLUMN vertical_type TEXT; -- 'meccanico', 'medico', etc.
ALTER TABLE clienti ADD COLUMN vertical_data TEXT; -- JSON con dati specifici

-- Tabelle relazionali per entità complesse
CREATE TABLE clienti_veicoli (...);           -- Per meccanico
CREATE TABLE clienti_storico_medico (...);    -- Per medico/dentista
CREATE TABLE clienti_misurazioni (...);       -- Per palestra/estetica
```

### Opzione 2: EAV (Entity-Attribute-Value)
```sql
CREATE TABLE cliente_attributi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT,
  vertical_type TEXT,
  attributo_nome TEXT,
  attributo_valore TEXT,  -- JSON
  data_type TEXT,         -- 'string', 'number', 'date', 'array', 'object'
  created_at TEXT
);
```

### Opzione 3: Tabelle Separate Complete
Tabelle completamente separate per ogni verticale con relazione 1:1 a clienti.

---

## 📡 API REQUIREMENTS

### Tauri Commands
```rust
// Get scheda verticale
#[tauri::command]
pub async fn get_cliente_scheda(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    vertical_type: String,
) -> Result<VerticalData, String>;

// Update scheda verticale
#[tauri::command]
pub async fn update_cliente_scheda(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    vertical_type: String,
    data: JsonValue,
) -> Result<(), String>;

// CRUD specifici per entità verticali
#[tauri::command] pub async fn add_veicolo(...);
#[tauri::command] pub async fn add_intervento(...);
#[tauri::command] pub async fn add_valutazione_fisio(...);
#[tauri::command] pub async fn add_trattamento_dentale(...);
#[tauri::command] pub async fn add_misurazione_fitness(...);
#[tauri::command] pub async fn add_colorazione(...);
#[tauri::command] pub async fn add_trattamento_estetico(...);
```

---

## 🎨 FRONTEND REQUIREMENTS

### Componenti Verticali
```typescript
// Schede cliente dinamiche
<SchedaCliente verticalType={verticalType} clienteId={id} />

// Componenti specifiche
<SchedaMeccanico veicoli={...} interventi={...} />
<SchedaMedica anamnesi={...} esami={...} />
<SchedaDentale diagrammaDenti={...} trattamenti={...} />
<SchedaFitness misurazioni={...} allenamenti={...} />
<SchedaParrucchiere colorazioni={...} tagli={...} />
<SchedaEstetica pelle={...} trattamenti={...} />

// Componenti condivisi
<TimelineStorico eventi={...} />
<AllegatiDocumenti files={...} />
<GraficoProgresso data={...} />
```

### UI/UX Requirements
1. **Tab Layout**: Sezioni organizzate in tab (Anagrafica, Storico, Documenti, ecc.)
2. **Timeline View**: Visualizzazione cronologica degli interventi/visite
3. **Grafici**: Progressi (fitness, estetica), Andamento (medico)
4. **Diagrammi**: Denti (dentista), Corpo (fisio/fitness), Auto (meccanico)
5. **Quick Actions**: Bottone rapido per "Nuovo intervento", "Nuova visita", ecc.

---

## 🎙️ VOICE AGENT INTEGRATION

### NLU per Verticali
```python
# Intent specifici per verticale
VERTICAL_INTENTS = {
    'meccanico': ['nuovo_intervento', 'prossima_revisione', 'problema_motore', ...],
    'medico': ['nuova_visita', 'prenota_esame', 'referti', ...],
    'dentista': ['nuovo_appuntamento', 'dolore_dente', 'igiene', ...],
    'palestra': ['nuova_scheda', 'prenota_ingresso', 'misurazioni', ...],
    'parrucchiere': ['nuovo_taglio', 'colorazione', 'trattamento', ...],
    'estetista': ['nuovo_trattamento', 'epilazione', 'massaggio', ...]
}

# Entity extraction
EXTRACTORS = {
    'meccanico': ['targa', 'km', 'tipo_problema'],
    'medico': ['sintomi', 'tipo_visita', 'urgenza'],
    'dentista': ['numero_dente', 'tipo_dolore'],
    'palestra': ['obiettivo', 'gruppo_muscolare'],
    'parrucchiere': ['lunghezza', 'colore', 'tecnica'],
    'estetista': ['area_corpo', 'tipo_trattamento']
}
```

---

## 📋 DELIVERABLES ATTESI

1. **Database Schema**: Migration SQL per tutte le tabelle verticali
2. **Domain Model**: Rust structs per tutti i tipi verticali
3. **Repository Layer**: CRUD operations per dati verticali
4. **API Layer**: Tauri commands per frontend
5. **Frontend Components**: React components per ogni scheda verticale
6. **Voice Integration**: NLU patterns per ogni verticale
7. **Documentation**: API docs, usage examples

---

## ⚠️ CONSIDERAZIONI TECNICHE

1. **Performance**: JSON columns indicizzati con SQLite JSON1 extension
2. **Migration**: Strategia per migrare dati esistenti
3. **GDPR**: Campi medici/sensibili già coperti da audit_log implementato
4. **Flexibilità**: Design che permetta nuovi verticali futuri
5. **Validazione**: Zod schemas per validazione TypeScript + Rust

---

**Stack completo fornito. Attendo il piano di implementazione dettagliato.**
