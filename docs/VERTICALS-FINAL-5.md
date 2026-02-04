# 📊 VERTICALI FINALI - 5 Settori PMI Italia

**Data**: 2026-02-03  
**Versione**: 2.0 (FINALE)  
**Verticali Confermati**: 5 (eliminato Fitness, nessuna Ristorazione)

---

## ✅ VERTICALI IMPLEMENTATI

| # | Verticale | Icona | Priorità | Entità Principali |
|---|-----------|-------|----------|-------------------|
| 1 | 🚗 **Meccanico/Carrozzeria** | 🔧 | Alta | Veicoli, Interventi, Ricambi |
| 2 | 🏥 **Fisioterapista/Osteopata** | 🏥 | Alta | Anamnesi, Sedute, Valutazioni |
| 3 | 🦷 **Dentista/Odontoiatra** | 🦷 | Alta | Odontogramma, Trattamenti, Impianti |
| 4 | 💇 **Parrucchiere/Barbiere** | 💇 | Alta | Colorazioni, Tagli, Formulazioni |
| 5 | 💆 **Estetista/Centro Benessere** | 💆 | Alta | Analisi Pelle, Trattamenti, Pacchetti |

---

## ❌ VERTICALI ESCLUSI

| Verticale | Motivo Esclusione |
|-----------|-------------------|
| 💪 **Fitness/Palestra** | Fuori scope target (richiesto esplicitamente) |
| 🍽️ **Ristorazione** | Mai considerato - fuori target PMI servizi |

---

## 🏗️ ARCHITETTURA DATABASE (5 Verticali)

```sql
-- ============================================================
-- SCHEMA UNIFICATO - 5 VERTICALI
-- ============================================================

-- 1. CAMPO vertical_type IN CLIENTI (5 valori)
ALTER TABLE clienti ADD COLUMN vertical_type TEXT CHECK (
  vertical_type IN (
    'generico',        -- CRM base senza scheda verticale
    'meccanico',       -- Meccanico + Carrozzeria
    'fisioterapia',    -- Fisio + Osteopatia
    'dentista',        -- Dentista + Odontoiatra
    'parrucchiere',    -- Parrucchiere + Barbiere
    'estetista'        -- Estetista + Centro Benessere
  )
);

-- 2. TABELLA LICENZE_VERTICALI (singleton)
CREATE TABLE licenze_verticali (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  
  -- Verticali abilitati
  meccanico_enabled INTEGER DEFAULT 0,
  fisioterapia_enabled INTEGER DEFAULT 0,
  dentista_enabled INTEGER DEFAULT 0,
  parrucchiere_enabled INTEGER DEFAULT 0,
  estetista_enabled INTEGER DEFAULT 0,
  
  -- Configurazione
  verticali_attivi TEXT, -- JSON ["meccanico", "dentista"]
  license_key TEXT,
  
  updated_at TEXT DEFAULT (datetime('now'))
);

-- 3. TABELLE MECCANICO
CREATE TABLE mec_veicoli (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL REFERENCES clienti(id),
  targa TEXT NOT NULL,
  telaio TEXT,
  tipo TEXT CHECK (tipo IN ('auto','moto','furgone','camion','rimorchio')),
  marca TEXT,
  modello TEXT,
  anno INTEGER,
  km_attuali INTEGER,
  alimentazione TEXT,
  scadenze JSON, -- {bollo, assicurazione, revisione}
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE mec_interventi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  veicolo_id TEXT REFERENCES mec_veicoli(id),
  data TEXT NOT NULL,
  km INTEGER,
  tipo TEXT CHECK (tipo IN ('ordinaria','straordinaria','tagliando','garantia','carrozzeria','elettronica')),
  motivo TEXT,
  diagnosi TEXT,
  lavori JSON,
  ricambi JSON,
  costo_totale REAL,
  garanzia_giorni INTEGER DEFAULT 730,
  fatturato INTEGER DEFAULT 0,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 4. TABELLE FISIOTERAPIA
CREATE TABLE fis_anamnesi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL UNIQUE,
  fisico JSON, -- {altezza, peso, bmi}
  allergie JSON,
  patologie JSON,
  farmaci JSON,
  stile_vita JSON,
  esami JSON,
  contatto_emergenza JSON,
  updated_at TEXT
);

CREATE TABLE fis_sedute (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  durata_minuti INTEGER,
  numero_seduta INTEGER,
  dolore_iniziale INTEGER CHECK (dolore_iniziale BETWEEN 0 AND 10),
  dolore_finale INTEGER,
  valutazione JSON, -- ROM, test, forza
  tecniche JSON,
  esercizi JSON,
  note TEXT,
  costo REAL,
  pagato INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 5. TABELLE DENTISTA
CREATE TABLE den_odontogrammi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  versione INTEGER,
  denti JSON, -- Array 32 denti sistema FDI
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE den_trattamenti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  tipo TEXT,
  denti JSON,
  diagnosi TEXT,
  trattamento_eseguito TEXT,
  materiali JSON,
  costo REAL,
  garanzia_mesi INTEGER,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 6. TABELLE PARRUCCHIERE
CREATE TABLE par_colorazioni (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  tipo TEXT, -- copertura_bianchi, balayage, meches...
  formulazione JSON, -- {marca, base, miscela, ossidante}
  colore_raggiunto TEXT,
  foto_prima TEXT,
  foto_dopo TEXT,
  costo REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE par_tagli (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  tipo_taglio TEXT,
  lunghezza_prima TEXT,
  lunghezza_dopo TEXT,
  tecnica TEXT,
  costo REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 7. TABELLE ESTETISTA
CREATE TABLE est_analisi_pelle (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL UNIQUE,
  data TEXT NOT NULL,
  fototipo INTEGER CHECK (fototipo BETWEEN 1 AND 6),
  tipo_base TEXT,
  condizioni JSON, -- {acne, macchie, rughe, couperose...}
  allergie JSON,
  obiettivi JSON,
  foto_viso JSON,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE est_trattamenti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  tipo TEXT, -- pulizia_viso, massaggio, ceretta...
  aree JSON,
  prodotti JSON,
  durata_minuti INTEGER,
  costo REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 🎙️ VOICE AGENT - SARA PER 5 VERTICALI

### Riconoscimento Automatico

```python
# voice-agent/verticals/classifier.py

VERTICAL_INTENTS = {
    'meccanico': {
        'patterns': [
            r'\b(auto|macchina|veicolo|motore|freno|cambio|olio|tagliando|revisione|gomme|pneumatici)\b',
            r'\b(targa|bollo|assicurazione|carrozzeria|incidente|non parte)\b',
        ],
        'greeting': "Buongiorno, sono Sara dell'officina. Come posso aiutarla con la sua auto?",
        'entities': ['targa', 'marca', 'km', 'problema']
    },
    
    'fisioterapia': {
        'patterns': [
            r'\b(fisio|terapista|osteopata|schiena|collo|ginocchio|spalla|dolore muscolare)\b',
            r'\b(seduta|trattamento|massaggio|riascolto|postura|articolazione)\b',
        ],
        'greeting': "Buongiorno, sono Sara del centro fisioterapico. Mi dica come posso aiutarla.",
        'entities': ['zona_dolore', 'intensita', 'durata']
    },
    
    'dentista': {
        'patterns': [
            r'\b(dentista|denti|dente|carie|otturazione|pulizia|gengive|molare|incisivo)\b',
            r'\b(corona|impianto|apparecchio|sbiancamento|dolore dentale|bocca)\b',
        ],
        'greeting': "Buongiorno, sono Sara dello studio dentistico. Mi dica il motivo della chiamata.",
        'entities': ['numero_dente', 'tipo_dolore', 'trattamento']
    },
    
    'parrucchiere': {
        'patterns': [
            r'\b(capelli|taglio|colore|tinta|shampoo|piega|ricci|lisci|decolorazione)\b',
            r'\b(biondo|more|meches|balayage|taglio|barba|raccolto|acconciatura)\b',
        ],
        'greeting': "Buongiorno, sono Sara del salone. Come posso aiutarla per i suoi capelli?",
        'entities': ['lunghezza', 'colore', 'tecnica']
    },
    
    'estetista': {
        'patterns': [
            r'\b(estetista|viso|corpo|massaggio|ceretta|epilazione|unghie|ciglia|mani|piedi)\b',
            r'\b(pulizia viso|idratare|antiage|manicure|pedicure|sopracciglia|trattamento)\b',
        ],
        'greeting': "Buongiorno, sono Sara del centro estetico. Cosa posso prenotare per lei?",
        'entities': ['zona_corpo', 'trattamento', 'problema']
    }
}
```

### Adattamento per Licenza

```python
# voice-agent/sara_orchestrator.py

class SaraOrchestrator:
    def __init__(self, license_manager):
        self.license = license_manager.get_active_license()
        self.enabled_verticals = self.license.verticals
        self.classifier = VerticalIntentClassifier()
        
    async def handle_call(self, audio_input):
        # 1. Trascrivi audio
        text = await self.stt.transcribe(audio_input)
        
        # 2. Rileva verticale (tra quelli abilitati)
        detected = self.classifier.detect_vertical(text, self.enabled_verticals)
        
        # 3. Carica handler specifico
        handler = VerticalHandlerFactory.create(detected)
        
        # 4. Usa greeting del verticale
        if self.is_new_call():
            return handler.get_greeting()
        
        # 5. Processa intent
        intent = handler.detect_intent(text)
        response = await handler.handle(intent, text)
        
        return response
```

---

## 📊 RIEPILOGO SCHEMA DATI

### Meccanico
| Entità | Campi Chiave | JSON Fields |
|--------|--------------|-------------|
| Veicoli | targa, telaio, km, scadenze | scadenze {bollo, assicurazione, revisione} |
| Interventi | tipo, motivo, costo | lavori[], ricambi[] |

### Fisioterapia
| Entità | Campi Chiave | JSON Fields |
|--------|--------------|-------------|
| Anamnesi | fisico, allergie, patologie | fisico {}, patologie[], farmaci[] |
| Sedute | dolore VAS 0-10, numero_seduta | valutazione {}, tecniche[] |

### Dentista
| Entità | Campi Chiave | JSON Fields |
|--------|--------------|-------------|
| Odontogramma | versione, data | denti[] (32 denti FDI) |
| Trattamenti | tipo, denti coinvolti | denti[], materiali[] |

### Parrucchiere
| Entità | Campi Chiave | JSON Fields |
|--------|--------------|-------------|
| Colorazioni | tipo, colore_raggiunto | formulazione {marca, base, ossidante} |
| Tagli | tipo_taglio, lunghezze | - |

### Estetista
| Entità | Campi Chiave | JSON Fields |
|--------|--------------|-------------|
| Analisi Pelle | fototipo 1-6, tipo_base | condizioni {}, obiettivi[] |
| Trattamenti | tipo, aree, durata | aree[], prodotti[] |

---

## 💰 MODELLO LICENZE (5 Verticali)

```
FLUXION LICENSE TIERS
═══════════════════════════════════════════════════

BASE (€199/lifetime)
├─ CRM Clienti generico
├─ Calendario Appuntamenti
├─ Fatturazione base
└─ 1 Verticale a scelta (5 disponibili)

PROFESSIONAL (€399/lifetime)
├─ Tutto di Base
├─ 2 Verticali simultanei
├─ Voice Agent SARA
├─ Analytics avanzate
└─ Multi-location (3 sedi)

ENTERPRISE (€799/lifetime)
├─ Tutti i 5 Verticali
├─ Unlimited locations
├─ Custom branding
├─ API access
└─ Priority support

ADD-ONS
├─ Verticale extra: +€80
├─ Location extra: +€30/sede
└─ White label: +€200
```

---

## 🚀 PIANO IMPLEMENTAZIONE

### Fase 1: Infrastructure (Comune)
- [ ] Migration vertical_type in clienti
- [ ] Migration licenze_verticali
- [ ] Sistema licenze custom Ed25519
- [ ] Hook useVerticalLicense()

### Fase 2: Meccanico (Reference)
- [ ] DB: mec_veicoli, mec_interventi
- [ ] Rust: models, repository, service
- [ ] React: VeicoliTab, InterventiTab
- [ ] Voice: MeccanicoHandler

### Fase 3: Fisioterapia
- [ ] DB: fis_anamnesi, fis_sedute
- [ ] Rust: domain layer
- [ ] React: AnamnesiTab, SeduteTab
- [ ] Voice: FisioHandler

### Fase 4: Dentista
- [ ] DB: den_odontogrammi, den_trattamenti
- [ ] Rust: domain layer
- [ ] React: Odontogramma component
- [ ] Voice: DentistaHandler

### Fase 5: Parrucchiere
- [ ] DB: par_colorazioni, par_tagli
- [ ] Rust: domain layer
- [ ] React: ColorazioniTab
- [ ] Voice: ParrucchiereHandler

### Fase 6: Estetista
- [ ] DB: est_analisi_pelle, est_trattamenti
- [ ] Rust: domain layer
- [ ] React: AnalisiPelleTab
- [ ] Voice: EstetistaHandler

---

*Documento Finale - 5 Verticali*  
*Data: 2026-02-03*
