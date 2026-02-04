# PROMPT: Sistema 5 Schede Clienti Verticali (FINALE)

**Per**: Kimi Code CLI  
**Scopo**: Implementare 5 verticali PMI con licenza custom Ed25519  
**Stack**: Tauri 2.x + Rust + React 19 + SQLite + Ed25519

---

## 🎯 SPECIFICHE FINALI

### 5 Verticali Confermati
1. 🚗 **Meccanico/Carrozzeria** - Veicoli, interventi, ricambi
2. 🏥 **Fisioterapista/Osteopata** - Anamnesi, sedute, valutazioni
3. 🦷 **Dentista/Odontoiatra** - Odontogramma (32 denti FDI), trattamenti
4. 💇 **Parrucchiere/Barbiere** - Colorazioni (formulazioni), tagli
5. 💆 **Estetista** - Analisi pelle (Fitzpatrick 1-6), trattamenti

### Verticali Esclusi
- ❌ Fitness/Palestra (fuori scope)
- ❌ Ristorazione (mai considerato)

---

## 🔐 SISTEMA LICENZE CUSTOM (Ed25519)

### Architettura Offline-First

```rust
// src-tauri/src/license/mod.rs

pub struct License {
    pub key: String,                    // XXXX-XXXX-XXXX-XXXX
    pub tier: LicenseTier,              // base | professional | enterprise
    pub verticals: Vec<VerticalType>,   // [meccanico, dentista]
    pub hardware_fingerprint: String,   // hash(CPU+MB+Disk)
    pub expires_at: Option<DateTime<Utc>>,
    pub signature: Vec<u8>,             // Ed25519 signature
}

pub struct LicenseManager {
    public_key: [u8; 32],  // Embedded in binary
}

impl LicenseManager {
    /// Verifica licenza 100% offline
    pub fn verify(&self, license_json: &str) -> Result<License, LicenseError> {
        // 1. Parse JSON
        // 2. Verify Ed25519 signature
        // 3. Check hardware fingerprint
        // 4. Check expiration
        // 5. Return unlocked verticals
    }
}
```

### Formato Licenza (JSON)

```json
{
  "key": "FLUX-2026-MECH-DENT",
  "tier": "professional",
  "verticals": ["meccanico", "dentista"],
  "hardware_hash": "a1b2c3d4e5f6...",
  "issued_at": "2026-02-01T00:00:00Z",
  "expires_at": "2027-02-01T00:00:00Z",
  "features": {
    "max_locations": 3,
    "voice_agent": true,
    "offline_mode": true
  },
  "signature": "base64_ed25519_signature..."
}
```

### CLI Generazione Licenze (Admin Tool)

```rust
// tools/license-generator/main.rs
// Compilato separatamente con PRIVATE_KEY

fn main() {
    let args = Args::parse();
    
    let license = License::builder()
        .tier(args.tier)
        .verticals(args.verticals)
        .hardware(args.hardware_id)
        .expires(args.days)
        .sign(&PRIVATE_KEY)
        .build();
    
    println!("{}", serde_json::to_string_pretty(&license).unwrap());
}
```

---

## 🗄️ DATABASE SCHEMA (SQLite)

### Migration 019: Vertical Type
```sql
ALTER TABLE clienti ADD COLUMN vertical_type TEXT CHECK (
  vertical_type IN ('generico', 'meccanico', 'fisioterapia', 'dentista', 'parrucchiere', 'estetista')
);
```

### Migration 020: Licenze
```sql
CREATE TABLE licenze_config (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  meccanico_enabled INTEGER DEFAULT 0,
  fisioterapia_enabled INTEGER DEFAULT 0,
  dentista_enabled INTEGER DEFAULT 0,
  parrucchiere_enabled INTEGER DEFAULT 0,
  estetista_enabled INTEGER DEFAULT 0,
  license_data TEXT, -- JSON licenza attiva
  updated_at TEXT DEFAULT (datetime('now'))
);
```

### Migration 021-025: Tabelle Verticali
Vedere docs/VERTICALS-FINAL-5.md per schema completo.

---

## 📁 STRUTTURA FILE

### Backend Rust
```
src-tauri/src/
├── license/                    # NUOVO: Sistema licenze Ed25519
│   ├── mod.rs
│   ├── models.rs
│   ├── crypto.rs              # Ed25519 verify/sign
│   └── manager.rs
│
├── verticals/                  # NUOVO: 5 verticali
│   ├── mod.rs                  # Registry, factory
│   ├── types.rs                # VerticalType enum
│   ├── meccanico/
│   │   ├── mod.rs
│   │   ├── models.rs           # Veicolo, Intervento
│   │   ├── repository.rs
│   │   └── service.rs
│   ├── fisioterapia/
│   │   ├── mod.rs
│   │   ├── models.rs           # Anamnesi, Seduta
│   │   ├── repository.rs
│   │   └── service.rs
│   ├── dentista/
│   │   ├── mod.rs
│   │   ├── models.rs           # Odontogramma, Trattamento
│   │   ├── repository.rs
│   │   └── service.rs
│   ├── parrucchiere/
│   │   ├── mod.rs
│   │   ├── models.rs           # Colorazione, Taglio
│   │   ├── repository.rs
│   │   └── service.rs
│   └── estetista/
│       ├── mod.rs
│       ├── models.rs           # AnalisiPelle, Trattamento
│       ├── repository.rs
│       └── service.rs
│
└── commands/
    ├── license.rs              # Tauri commands licenza
    └── verticals.rs            # Tauri commands verticali
```

### Frontend React
```
src/
├── verticals/
│   ├── config.ts               # Configurazione 5 verticali
│   ├── registry.ts             # Registro componenti
│   │
│   ├── Meccanico/
│   │   ├── index.tsx
│   │   ├── VeicoliTab.tsx
│   │   ├── InterventiTab.tsx
│   │   ├── ScadenzeTab.tsx
│   │   └── forms/
│   │       ├── VeicoloForm.tsx
│   │       └── InterventoForm.tsx
│   │
│   ├── Fisioterapia/
│   │   ├── index.tsx
│   │   ├── AnamnesiTab.tsx
│   │   ├── SeduteTab.tsx
│   │   └── forms/
│   │       ├── AnamnesiForm.tsx
│   │       └── SedutaForm.tsx
│   │
│   ├── Dentista/
│   │   ├── index.tsx
│   │   ├── OdontogrammaTab.tsx      # Componente grafico 32 denti
│   │   ├── TrattamentiTab.tsx
│   │   └── forms/
│   │       └── TrattamentoForm.tsx
│   │
│   ├── Parrucchiere/
│   │   ├── index.tsx
│   │   ├── ColorazioniTab.tsx
│   │   ├── TagliTab.tsx
│   │   └── forms/
│   │       ├── ColorazioneForm.tsx
│   │       └── TaglioForm.tsx
│   │
│   └── Estetista/
│       ├── index.tsx
│       ├── AnalisiPelleTab.tsx
│       ├── TrattamentiTab.tsx
│       └── forms/
│           ├── AnalisiForm.tsx
│           └── TrattamentoForm.tsx
│
├── components/verticals/
│   ├── VerticalSelector.tsx        # Selezione verticale cliente
│   ├── SchedaClienteVerticale.tsx  # Container principale
│   ├── VerticalBadge.tsx           # Badge verticale attivo
│   └── LicenseStatus.tsx           # Stato licenza
│
├── hooks/
│   ├── useLicense.ts               # Gestione licenza
│   ├── useVertical.ts              # Info verticale corrente
│   └── useVerticalLicense.ts       # Combina license + vertical
│
└── types/verticals.ts              # TypeScript types verticali
```

### Voice Agent Python
```
voice-agent/
├── verticals/
│   ├── __init__.py
│   ├── registry.py                 # Registro handler
│   ├── base.py                     # BaseVerticalHandler
│   ├── classifier.py               # Rilevamento verticale
│   │
│   ├── meccanico.py
│   ├── fisioterapia.py
│   ├── dentista.py
│   ├── parrucchiere.py
│   └── estetista.py
│
└── sara_orchestrator.py            # Entry point con license check
```

---

## 🔧 IMPLEMENTAZIONE DETTAGLIATA

### 1. Sistema Licenze (PRIORITARIO)

```rust
// src-tauri/src/license/crypto.rs

use ed25519_dalek::{VerifyingKey, Signature, Verifier};

pub struct LicenseCrypto {
    public_key: VerifyingKey,
}

impl LicenseCrypto {
    pub fn new(public_key_bytes: &[u8; 32]) -> Result<Self, LicenseError> {
        let public_key = VerifyingKey::from_bytes(public_key_bytes)?;
        Ok(Self { public_key })
    }
    
    pub fn verify(&self, message: &[u8], signature: &[u8; 64]) -> Result<bool, LicenseError> {
        let sig = Signature::from_bytes(signature);
        match self.public_key.verify(message, &sig) {
            Ok(_) => Ok(true),
            Err(_) => Ok(false),
        }
    }
}
```

### 2. Modello Veicolo (Meccanico)

```rust
// src-tauri/src/verticals/meccanico/models.rs

use serde::{Serialize, Deserialize};
use validator::Validate;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct Veicolo {
    pub id: String,
    pub cliente_id: String,
    
    #[validate(regex(path = "TARGA_REGEX", message = "Targa non valida (formato: AB123CD)"))]
    pub targa: String,
    
    #[validate(length(min = 17, max = 17, message = "Telaio (VIN) deve essere 17 caratteri"))]
    pub telaio: Option<String>,
    
    pub tipo: VeicoloTipo,
    pub marca: String,
    pub modello: String,
    pub anno: Option<i32>,
    pub km_attuali: i32,
    pub km_inserimento: i32,
    pub alimentazione: Alimentazione,
    
    pub scadenze: ScadenzeVeicolo,
    pub note: Option<String>,
    
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VeicoloTipo {
    Auto,
    Moto,
    Furgone,
    Camion,
    Rimorchio,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ScadenzeVeicolo {
    pub bollo: Option<DateTime<Utc>>,
    pub assicurazione: Option<DateTime<Utc>>,
    pub revisione: Option<DateTime<Utc>>,
    pub tagliando: Option<DateTime<Utc>>,
}

impl Veicolo {
    pub fn new(cliente_id: &str, targa: &str, marca: &str, modello: &str) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4().to_string(),
            cliente_id: cliente_id.to_string(),
            targa: targa.to_uppercase(),
            telaio: None,
            tipo: VeicoloTipo::Auto,
            marca: marca.to_string(),
            modello: modello.to_string(),
            anno: None,
            km_attuali: 0,
            km_inserimento: 0,
            alimentazione: Alimentazione::Benzina,
            scadenze: ScadenzeVeicolo::default(),
            note: None,
            created_at: now,
            updated_at: now,
        }
    }
    
    /// Verifica se ci sono scadenze imminenti (prossimi 30 giorni)
    pub fn scadenze_imminenti(&self) -> Vec<ScadenzaAlert> {
        // Implementazione
    }
}
```

### 3. Odontogramma (Dentista)

```rust
// src-tauri/src/verticals/dentista/models.rs

/// Sistema FDI: 11-18 (sup dx), 21-28 (sup sx), 31-38 (inf sx), 41-48 (inf dx)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Odontogramma {
    pub id: String,
    pub cliente_id: String,
    pub data: DateTime<Utc>,
    pub versione: u32,
    pub denti: Vec<Dente>,
    pub note_generali: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Dente {
    pub numero: u8,  // 11-48
    pub nome: String,
    pub stato: StatoDente,
    pub superfici: SuperficiDente,
    pub storico: Vec<InterventoDente>,
    pub note: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum StatoDente {
    Sano,
    Caries,
    Otturato,
    Devitalizzato,
    Corona,
    Impianto,
    Estratto,
    Assente,
    InEruzione,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SuperficiDente {
    pub mesiale: Option<StatoSuperficie>,
    pub distale: Option<StatoSuperficie>,
    pub vestibolare: Option<StatoSuperficie>,
    pub linguale: Option<StatoSuperficie>,
    pub occlusale: Option<StatoSuperficie>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum StatoSuperficie {
    Sano,
    Caries,
    Otturazione,
    Frattura,
}

impl Odontogramma {
    /// Crea odontogramma vuoto con 32 denti in stato Sano
    pub fn nuovo(cliente_id: &str) -> Self {
        let denti = (11..=18)
            .chain(21..=28)
            .chain(31..=38)
            .chain(41..=48)
            .map(|n| Dente::nuovo(n))
            .collect();
        
        Self {
            id: Uuid::new_v4().to_string(),
            cliente_id: cliente_id.to_string(),
            data: Utc::now(),
            versione: 1,
            denti,
            note_generali: None,
        }
    }
}
```

---

## 🎙️ VOICE AGENT IMPLEMENTATION

### Base Handler

```python
# voice-agent/verticals/base.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class IntentMatch:
    confidence: float
    intent: str
    entities: Dict[str, Any]
    vertical: str

class BaseVerticalHandler(ABC):
    vertical_name: str
    vertical_id: str
    intent_patterns: Dict[str, List[str]] = {}
    entity_patterns: Dict[str, str] = {}
    
    @abstractmethod
    async def handle_intent(self, intent: str, entities: Dict, context: Dict) -> str:
        pass
    
    def detect_intent(self, text: str) -> Optional[IntentMatch]:
        import re
        
        best_match = None
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            matched_entities = {}
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.I)
                for match in matches:
                    score += 0.3
                    if match.groups():
                        for i, group in enumerate(match.groups()):
                            matched_entities[f'group_{i}'] = group
            
            for entity_name, entity_pattern in self.entity_patterns.items():
                match = re.search(entity_pattern, text, re.I)
                if match:
                    matched_entities[entity_name] = match.group(1)
                    score += 0.2
            
            if score > best_score and score > 0.3:
                best_score = score
                best_match = IntentMatch(
                    confidence=score,
                    intent=intent,
                    entities=matched_entities,
                    vertical=self.vertical_id
                )
        
        return best_match
```

### Handler Meccanico

```python
# voice-agent/verticals/meccanico.py

from .base import BaseVerticalHandler, IntentMatch

class MeccanicoHandler(BaseVerticalHandler):
    vertical_name = "Autofficina"
    vertical_id = "meccanico"
    
    intent_patterns = {
        'nuovo_intervento': [
            r'\b(tagliando|manutenzione|problema|rumore|guasto|non parte)\b',
            r'\b(devo fare|devo portare|c\'è un problema|si è rotto)\b',
        ],
        'info_veicolo': [
            r'\b(quando|a quanti|scade|è scaduto|prossimo)\b.*\b(bollo|assicurazione|revisione|tagliando)\b',
            r'\b(gomme|freni|olio|batteria)\b.*\b(stato|quando)\b',
        ],
        'preventivo': [
            r'\b(quanto costa|preventivo|prezzo|stima|farebbe un prezzo)\b',
        ],
        'emergenza': [
            r'\b(urgente|emergenza|incidente|non si avvia|fumo|scoppiato)\b',
        ],
    }
    
    entity_patterns = {
        'targa': r'\b([A-Z]{2}\d{3}[A-Z]{2})\b',
        'km': r'\b(\d{2,6})\s*(?:km|chilometri)\b',
        'marca': r'\b(fiat|bmw|mercedes|audi|volkswagen|ford|toyota|jeep|renault)\b',
    }
    
    greetings = {
        'initial': "Buongiorno, sono Sara dell'officina. Come posso aiutarla con la sua auto?",
        'returning': "Bentornato! Ha bisogno di fissare un intervento?",
    }
    
    async def handle_intent(self, intent: str, entities: Dict, context: Dict) -> str:
        if intent == 'nuovo_intervento':
            return await self._handle_nuovo_intervento(entities, context)
        elif intent == 'info_veicolo':
            return await self._handle_info_veicolo(entities, context)
        elif intent == 'preventivo':
            return await self._handle_preventivo(entities, context)
        elif intent == 'emergenza':
            return await self._handle_emergenza(entities, context)
        return "Non ho capito bene. Mi può dire che automobile ha e cosa succede?"
    
    async def _handle_emergenza(self, entities: Dict, context: Dict) -> str:
        return (
            "Capisco che è una situazione urgente. "
            "Se l'auto non è in condizioni di muoversi, possiamo organizzare il carro attrezzi. "
            "Mi dica dove si trova e il suo numero di telefono così la facciamo richiamare subito."
        )
```

---

## 📋 CHECKLIST IMPLEMENTAZIONE COMPLETA

### Fase 0: Setup Crypto
- [ ] Aggiungere dipendenza `ed25519-dalek` a Cargo.toml
- [ ] Creare modulo `license/crypto.rs`
- [ ] Implementare verify Ed25519
- [ ] Generare keypair per testing

### Fase 1: Infrastructure
- [ ] Migration 019: vertical_type in clienti
- [ ] Migration 020: licenze_config
- [ ] LicenseManager con cache
- [ ] Hook useLicense()
- [ ] UI LicenseStatus

### Fase 2: Meccanico (Reference)
- [ ] Migration 021: mec_veicoli, mec_interventi
- [ ] Models Veicolo, Intervento
- [ ] Repository CRUD
- [ ] Tauri commands
- [ ] VeicoliTab UI
- [ ] InterventiTab UI
- [ ] Forms
- [ ] Voice handler

### Fase 3: Fisioterapia
- [ ] Migration 022: fis_anamnesi, fis_sedute
- [ ] Models Anamnesi, Seduta
- [ ] Repository
- [ ] Tauri commands
- [ ] AnamnesiTab
- [ ] SeduteTab
- [ ] Voice handler

### Fase 4: Dentista
- [ ] Migration 023: den_odontogrammi, den_trattamenti
- [ ] Models Odontogramma, Trattamento
- [ ] Componente grafico 32 denti
- [ ] Repository
- [ ] UI tabs
- [ ] Voice handler

### Fase 5: Parrucchiere
- [ ] Migration 024: par_colorazioni, par_tagli
- [ ] Models
- [ ] Repository
- [ ] UI
- [ ] Voice handler

### Fase 6: Estetista
- [ ] Migration 025: est_analisi_pelle, est_trattamenti
- [ ] Models
- [ ] Repository
- [ ] UI
- [ ] Voice handler

---

## ✅ CRITERI ACCETTAZIONE

- [ ] Sistema licenze Ed25519 funzionante offline
- [ ] Tutti i 5 verticali implementati
- [ ] Voice Agent riconosce verticali abilitati
- [ ] UI mostra solo verticali della licenza
- [ ] Database migrations completate
- [ ] Tests passanti

---

*Prompt Finale - Implementazione 5 Verticali*  
*Data: 2026-02-03*
