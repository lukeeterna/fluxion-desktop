# PROMPT: Sistema Schede Clienti Multi-Verticali

**Per**: Kimi Code CLI (Claude 3.5 Sonnet / Claude 4 Sonnet)  
**Scopo**: Implementare sistema completo per 6 verticali PMI con sblocco licenza  
**Stack**: Tauri 2.x + Rust + React 19 + SQLite

---

## 🎯 OBIETTIVO

Implementare un sistema di **schede clienti verticali** dove:
- Ogni cliente ha una scheda base CRM + scheda verticale specifica
- I verticali sono **selezionabili via licenza** (non tutti attivi)
- Ogni verticale ha schema dati, UI e Voice Agent specifici
- Il sistema è **estensibile** per futuri verticali

---

## 🏗️ ARCHITETTURA UNIFICATA

### Database Schema

```sql
-- 1. Vertical type in clienti
ALTER TABLE clienti ADD COLUMN vertical_type TEXT CHECK (
  vertical_type IN ('generico', 'meccanico', 'medico', 'fisioterapia', 
                    'dentista', 'fitness', 'parrucchiere', 'estetista')
);

-- 2. Tabella licenze_verticali (singleton)
CREATE TABLE licenze_verticali (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  meccanico_enabled INTEGER DEFAULT 0,
  medico_enabled INTEGER DEFAULT 0,
  fisioterapia_enabled INTEGER DEFAULT 0,
  dentista_enabled INTEGER DEFAULT 0,
  fitness_enabled INTEGER DEFAULT 0,
  parrucchiere_enabled INTEGER DEFAULT 0,
  estetista_enabled INTEGER DEFAULT 0,
  verticali_attivi TEXT, -- JSON array
  license_key TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- 3. Tabelle verticali - MECCANICO
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
  km_inserimento INTEGER,
  alimentazione TEXT,
  scadenze JSON,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE mec_interventi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  veicolo_id TEXT REFERENCES mec_veicoli(id),
  data TEXT NOT NULL,
  km INTEGER,
  tipo TEXT,
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

-- 4. Tabelle verticali - MEDICO/FISIO
CREATE TABLE med_anamnesi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL UNIQUE,
  fisico JSON,
  allergie JSON,
  patologie JSON,
  farmaci JSON,
  stile_vita JSON,
  esami JSON,
  updated_at TEXT
);

CREATE TABLE med_sedute (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  durata_minuti INTEGER,
  numero_seduta INTEGER,
  dolore_iniziale INTEGER,
  dolore_finale INTEGER,
  valutazione JSON,
  tecniche JSON,
  note TEXT,
  costo REAL,
  pagato INTEGER DEFAULT 0
);

-- 5. Tabelle verticali - DENTISTA
CREATE TABLE den_odontogrammi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  versione INTEGER,
  denti JSON,
  note TEXT
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
  note TEXT
);

-- 6. FITNESS, PARRUCCHIERE, ESTETISTA (simile pattern)
-- CREATE TABLE fit_schede (...);
-- CREATE TABLE par_colorazioni (...);
-- CREATE TABLE est_trattamenti (...);
```

---

## 📦 STRUTTURA FILE DA CREARE

### Backend Rust
```
src-tauri/src/
├── verticals/
│   ├── mod.rs              # Registry e factory
│   ├── types.rs            # VerticalType enum
│   ├── license.rs          # Gestione licenze verticali
│   ├── meccanico/
│   │   ├── mod.rs
│   │   ├── models.rs       # Veicolo, Intervento
│   │   ├── repository.rs
│   │   └── service.rs
│   ├── medico/
│   ├── dentista/
│   └── ...
└── commands/verticals.rs   # Tauri commands
```

### Frontend React
```
src/
├── verticals/
│   ├── config.ts
│   ├── Meccanico/
│   │   ├── index.tsx
│   │   ├── VeicoliTab.tsx
│   │   ├── InterventiTab.tsx
│   │   └── forms/
│   └── ...
├── components/verticals/
│   └── SchedaClienteVerticale.tsx
└── hooks/useVerticalLicense.ts
```

### Voice Agent
```
voice-agent/
├── verticals/
│   ├── base.py
│   ├── registry.py
│   ├── meccanico.py
│   ├── medico.py
│   └── ...
```

---

## 🔧 IMPLEMENTAZIONE CHECKLIST

### Fase 1: Infrastructure (Comune)
- [ ] Migration 019: Add vertical_type to clienti
- [ ] Migration 020: Tabella licenze_verticali
- [ ] Tipo Rust: `VerticalType` enum
- [ ] Repository: Licenze verticali
- [ ] Hook React: `useVerticalLicense()`

### Fase 2: MECCANICO (Reference Implementation)
- [ ] Migration 021: mec_veicoli, mec_interventi
- [ ] Model: `Veicolo` con validazione
- [ ] Model: `Intervento` con JSON lavori/ricambi
- [ ] Repository: CRUD veicoli/interventi
- [ ] Service: Business logic
- [ ] Tauri commands
- [ ] React: VeicoliTab + InterventiTab
- [ ] React: Forms (VeicoloForm, InterventoForm)
- [ ] Voice: MeccanicoHandler

### Fase 3: MEDICO (Fisioterapia)
- [ ] Migration: med_anamnesi, med_sedute
- [ ] Models: Anamnesi, Seduta
- [ ] UI: AnamnesiTab, SeduteTab
- [ ] Voice: MedicoHandler

### Fase 4: DENTISTA
- [ ] Migration: den_odontogrammi, den_trattamenti
- [ ] Model: Odontogramma (32 denti)
- [ ] UI: Odontogramma component
- [ ] Voice: DentistaHandler

### Fase 5-7: FITNESS, PARRUCCHIERE, ESTETISTA
(Seguendo stesso pattern)

---

## 📋 SPECIFICHE RUST

### models.rs - Pattern
```rust
use serde::{Deserialize, Serialize};
use validator::Validate;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct Veicolo {
    pub id: String,
    pub cliente_id: String,
    
    #[validate(regex(path = "TARGA_REGEX"))]
    pub targa: String,
    pub telaio: Option<String>,
    pub tipo: VeicoloTipo,
    pub marca: String,
    pub modello: String,
    pub anno: Option<i32>,
    pub km_attuali: i32,
    pub scadenze: ScadenzeVeicolo,
    pub note: Option<String>,
}

impl Veicolo {
    pub fn new(cliente_id: &str, targa: &str, marca: &str, modello: &str) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            cliente_id: cliente_id.to_string(),
            targa: targa.to_string(),
            telaio: None,
            tipo: VeicoloTipo::Auto,
            marca: marca.to_string(),
            modello: modello.to_string(),
            anno: None,
            km_attuali: 0,
            scadenze: ScadenzeVeicolo::default(),
            note: None,
        }
    }
}
```

---

## 📋 SPECIFICHE REACT

### Component Pattern
```typescript
// verticals/Meccanico/VeicoliTab.tsx
import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useVerticalLicense } from '@/hooks/useVerticalLicense';

export function VeicoliTab({ clienteId }: { clienteId: string }) {
  const { isEnabled } = useVerticalLicense('meccanico');
  const [veicoli, setVeicoli] = useState([]);
  
  if (!isEnabled) {
    return <VerticalLockedOverlay vertical="meccanico" />;
  }
  
  // ... implementazione
}
```

---

## 📋 SPECIFICHE VOICE AGENT

### Base Handler Pattern
```python
# verticals/base.py
from abc import ABC, abstractmethod

class BaseVerticalHandler(ABC):
    vertical_name: str = "base"
    vertical_id: str = "generico"
    intent_patterns: Dict[str, List[str]] = {}
    
    @abstractmethod
    async def handle_intent(self, intent: str, entities: Dict, context: Dict) -> str:
        pass
    
    def detect_intent(self, text: str) -> Optional[IntentMatch]:
        # Pattern matching
        pass
```

### Meccanico Handler
```python
# verticals/meccanico.py
class MeccanicoHandler(BaseVerticalHandler):
    vertical_name = "Autofficina"
    vertical_id = "meccanico"
    
    intent_patterns = {
        'nuovo_intervento': [
            r'\b(tagliando|manutenzione|problema|guasto)\b',
        ],
        'info_veicolo': [
            r'\b(scade|prossimo)\b.*\b(bollo|assicurazione)\b',
        ],
    }
    
    async def handle_intent(self, intent: str, entities: Dict, context: Dict) -> str:
        if intent == 'nuovo_intervento':
            return "Che automobile ha e qual è il problema?"
        # ...
```

---

## ✅ CRITERI ACCETTAZIONE

- [ ] Tutte le migration eseguono senza errori
- [ ] Rust compila e tests passano
- [ ] React mostra UI corretta per verticali abilitati
- [ ] Verticali bloccati mostrano overlay upgrade
- [ ] Voice Agent riconosce intent verticali
- [ ] Sistema licenze integrato con esistente

---

## 🎯 SCOPO IMMEDIATO

Implementare **FASE 1 + FASE 2** (Infrastructure + Meccanico completo) come reference implementation per gli altri 5 verticali.
