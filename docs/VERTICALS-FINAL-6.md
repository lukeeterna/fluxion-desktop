# 📊 VERTICALI FINALI - 6 Settori PMI Italia

**Data**: 2026-02-03  
**Versione**: 3.0 (FINALE)  
**Verticali Confermati**: 6  
**Esclusi**: Ristorazione (mai considerato)

---

## ✅ VERTICALI IMPLEMENTATI

| # | Verticale | Icona | Fase | Entità Principali |
|---|-----------|-------|------|-------------------|
| 1 | 💇 **Parrucchiere/Barbiere** | 💇 | 1 | Colorazioni, Tagli, Formulazioni |
| 2 | 💆 **Estetista/Centro Benessere** | 💆 | 1 | Analisi Pelle, Trattamenti, Pacchetti |
| 3 | 🏥 **Fisioterapista/Osteopata** | 🏥 | 2 | Anamnesi, Sedute, Valutazioni |
| 4 | 🦷 **Dentista/Odontoiatra** | 🦷 | 3 | Odontogramma, Trattamenti, Impianti |
| 5 | 💪 **Fitness/Palestra/Personal** | 💪 | 4 | Schede, Misurazioni, Abbonamenti |
| 6 | 🚗 **Meccanico/Carrozzeria** | 🚗 | 5 | Veicoli, Interventi, Scadenze |

---

## 🔐 SISTEMA LICENZE - 3 TIER LIFETIME

### Modello Economico

```
FLUXION LICENSE SYSTEM - LIFETIME
═══════════════════════════════════════════════════════════════

🏅 BASE (€199 lifetime)
├─ 1 Verticale a scelta
├─ CRM Completo
├─ Calendario Appuntamenti
├─ Fatturazione Base
├─ 1 Location
└─ ❌ Voice Agent (non incluso)

🥈 INTERMEDIA / PROFESSIONAL (€399 lifetime)
├─ 3 Verticali a scelta
├─ Tutto di Base
├─ Analytics Avanzate
├─ Marketing Automation (email/sms)
├─ 3 Locations
└─ ❌ Voice Agent (non incluso)

🥇 FULL / ENTERPRISE (€799 lifetime)
├─ TUTTI i 6 Verticali
├─ Tutto di Intermedia
├─ 🎙️ Voice Agent SARA (incluso)
├─ WhatsApp Business Integration
├─ Multi-location illimitate
├─ White Label (logo custom)
├─ API Access
└─ Priority Support

ADD-ONS (acquistabili separatamente)
├─ Verticale extra: +€99
├─ Voice Agent add-on: +€299
├─ Location extra: +€49/location
└─ White Label add-on: +€199
```

---

## 🗝️ SISTEMA DI SBLOCCO FEATURE

### Schema Licenza Ed25519

```json
{
  "version": 1,
  "key": "FLUX-BASE-2026-XXXX",
  "tier": "base",
  "verticals": ["parrucchiere"],
  "hardware_fingerprint": "sha256:abc123...",
  "issued_at": "2026-02-03T00:00:00Z",
  "features": {
    "max_verticals": 1,
    "max_locations": 1,
    "voice_agent": false,
    "whatsapp_integration": false,
    "marketing_automation": false,
    "analytics_advanced": false,
    "white_label": false,
    "api_access": false
  },
  "signature": "ed25519:base64..."
}
```

### Feature Matrix per Tier

| Feature | Base | Intermedia | Full |
|---------|------|------------|------|
| Verticali | 1 | 3 | 6 (tutti) |
| Locations | 1 | 3 | ∞ |
| CRM | ✅ | ✅ | ✅ |
| Calendario | ✅ | ✅ | ✅ |
| Fatturazione | ✅ | ✅ | ✅ |
| Voice Agent SARA | ❌ | ❌ | ✅ |
| WhatsApp Business | ❌ | ❌ | ✅ |
| Marketing Automation | ❌ | ✅ | ✅ |
| Analytics Avanzate | ❌ | ✅ | ✅ |
| White Label | ❌ | ❌ | ✅ |
| API Access | ❌ | ❌ | ✅ |
| Priority Support | ❌ | ❌ | ✅ |

### Tabella Sblocco Verticali

| Tier | Verticali Sbloccati | Aggiungibili? |
|------|---------------------|---------------|
| Base | 1 a scelta | Sì (+€99 cad.) |
| Intermedia | 3 a scelta | Sì (+€99 cad.) |
| Full | Tutti i 6 | N/A |

---

## 🏗️ DATABASE SCHEMA (6 Verticali)

```sql
-- ============================================================
-- SCHEMA UNIFICATO - 6 VERTICALI + SISTEMA LICENZE
-- ============================================================

-- 1. CAMPO vertical_type IN CLIENTI
ALTER TABLE clienti ADD COLUMN vertical_type TEXT CHECK (
  vertical_type IN (
    'generico',
    'parrucchiere',
    'estetista',
    'fisioterapia',
    'dentista',
    'fitness',
    'meccanico'
  )
);

-- 2. TABELLA LICENZA ATTIVA (singleton)
CREATE TABLE license_config (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  
  -- Tier attivo
  tier TEXT CHECK (tier IN ('base', 'intermedia', 'full')),
  
  -- Verticali abilitati (BOOLEAN)
  parrucchiere_enabled INTEGER DEFAULT 0,
  estetista_enabled INTEGER DEFAULT 0,
  fisioterapia_enabled INTEGER DEFAULT 0,
  dentista_enabled INTEGER DEFAULT 0,
  fitness_enabled INTEGER DEFAULT 0,
  meccanico_enabled INTEGER DEFAULT 0,
  
  -- Feature flags
  voice_agent_enabled INTEGER DEFAULT 0,
  whatsapp_enabled INTEGER DEFAULT 0,
  marketing_enabled INTEGER DEFAULT 0,
  analytics_advanced_enabled INTEGER DEFAULT 0,
  white_label_enabled INTEGER DEFAULT 0,
  api_access_enabled INTEGER DEFAULT 0,
  
  -- Limiti
  max_verticals INTEGER DEFAULT 1,
  max_locations INTEGER DEFAULT 1,
  
  -- Licenza raw
  license_data TEXT,
  license_key TEXT,
  
  updated_at TEXT DEFAULT (datetime('now'))
);

-- 3. TABELLE PARRUCCHIERE (FASE 1)
CREATE TABLE par_colorazioni (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  tipo TEXT, -- copertura_bianchi, balayage, meches, ecc.
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

-- 4. TABELLE ESTETISTA (FASE 1)
CREATE TABLE est_analisi_pelle (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL UNIQUE,
  data TEXT NOT NULL,
  fototipo INTEGER CHECK (fototipo BETWEEN 1 AND 6),
  tipo_base TEXT,
  condizioni JSON, -- {acne, macchie, rughe, couperose, ...}
  allergie JSON,
  obiettivi JSON,
  foto_viso JSON,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE est_trattamenti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOTODELete TEXT NOT NULL,
  tipo TEXT, -- pulizia_viso, massaggio, ceretta, manicure, ...
  aree JSON,
  prodotti JSON,
  durata_minuti INTEGER,
  costo REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 5. TABELLE FISIOTERAPIA (FASE 2)
CREATE TABLE fis_anamnesi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL UNIQUE,
  fisico JSON,
  allergie JSON,
  patologie JSON,
  farmaci JSON,
  stile_vita JSON,
  contatto_emergenza JSON,
  updated_at TEXT
);

CREATE TABLE fis_sedute (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  numero_seduta INTEGER,
  dolore_iniziale INTEGER CHECK (dolore_iniziale BETWEEN 0 AND 10),
  dolore_finale INTEGER,
  valutazione JSON,
  tecniche JSON,
  costo REAL,
  pagato INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 6. TABELLE DENTISTA (FASE 3)
CREATE TABLE den_odontogrammi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  versione INTEGER,
  denti JSON, -- Array 32 denti sistema FDI 11-48
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
  materiali JSON,
  costo REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 7. TABELLE FITNESS (FASE 4)
CREATE TABLE fit_schede (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  nome TEXT,
  obiettivi JSON,
  livello TEXT,
  attiva INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE fit_misurazioni (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data TEXT NOT NULL,
  peso_kg REAL,
  altezza_cm REAL,
  circonferenze JSON,
  pliche JSON,
  foto JSON,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE fit_sessioni (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  data_inizio TEXT NOT NULL,
  esercizi JSON,
  volume_totale REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 8. TABELLE MECCANICO (FASE 5)
CREATE TABLE mec_veicoli (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  targa TEXT NOT NULL,
  telaio TEXT,
  tipo TEXT,
  marca TEXT,
  modello TEXT,
  anno INTEGER,
  km_attuali INTEGER,
  scadenze JSON,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE mec_interventi (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  veicolo_id TEXT,
  data TEXT NOT NULL,
  km INTEGER,
  tipo TEXT,
  motivo TEXT,
  lavori JSON,
  ricambi JSON,
  costo_totale REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 🎙️ VOICE AGENT - SBLOCCO TIER

### Voice Agent Solo in Tier FULL

```python
# voice-agent/main.py

class SaraOrchestrator:
    def __init__(self):
        # Carica config licenza da file condiviso
        self.license = self._load_license_config()
        
    def start(self):
        # Verifica se voice agent è abilitato
        if not self.license.voice_agent_enabled:
            logger.error("Voice Agent richiede licenza FULL")
            sys.exit(1)
        
        # Carica SOLO i verticali abilitati
        self.handlers = VerticalRegistry.load_enabled(
            self.license.enabled_verticals
        )
        
    async def handle_call(self, audio_input):
        # Solo se licenza FULL
        if self.license.tier != 'full':
            return "Funzione non disponibile nel tuo piano."
        
        # ... resto logica
```

### UI - Blocco Voice Agent

```typescript
// src/components/VoiceAgentButton.tsx

export function VoiceAgentButton() {
  const { license } = useLicense();
  
  if (!license.voiceAgentEnabled) {
    return (
      <Button disabled variant="outline">
        🔒 Voice Agent - Solo piano Full
        <UpgradeDialog feature="voice_agent" />
      </Button>
    );
  }
  
  return <Button onClick={startVoiceCall}>🎙️ Chiama Sara</Button>;
}
```

---

## 📊 ROADMAP IMPLEMENTAZIONE

### FASE 1: Parrucchiere + Estetista + Licenze
**Durata**: 4-5 giorni
- [ ] Sistema licenze Ed25519
- [ ] DB tables parrucchiere
- [ ] DB tables estetista
- [ ] Rust domain layer
- [ ] React UI
- [ ] Voice handlers (base, non attivi senza licenza FULL)

### FASE 2: Fisioterapia
**Durata**: 2-3 giorni

### FASE 3: Dentista
**Durata**: 3-4 giorni

### FASE 4: Fitness
**Durata**: 2-3 giorni

### FASE 5: Meccanico
**Durata**: 2-3 giorni

---

*Documento Finale - 6 Verticali con Sistema Licenze 3 Tier*
