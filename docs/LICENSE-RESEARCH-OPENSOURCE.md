# 🔍 DEEP RESEARCH: Alternative Open Source a Keygen

**Data**: 2026-02-03  
**Scopo**: Trovare soluzione di licensing 100% open source e self-hosted

---

## ❌ Soluzioni Esistenti (Analizzate)

### 1. Keygen.sh (Attuale)
- **Tipo**: Fair Source (non OSI-approved)
- **Self-hosted**: ✅ Sì (Keygen EE)
- **Costo**: Gratuito per self-host ma richiede infrastructure
- **Note**: Enterprise Edition, completo ma non 100% open source

### 2. Lukittu
- **Tipo**: Open source (TypeScript)
- **Self-hosted**: ⚠️ Non ufficialmente supportato
- **Architettura**: Multi-tenant SaaS nativo
- **Verdetto**: ❌ Non adatto - richiede refactoring massivo per single-tenant

### 3. f-license (Go)
- **Repo**: https://github.com/furkansenharputlu/f-license
- **Tipo**: Open source (Go)
- **Features**:
  - Generazione licenze HMAC/RSA
  - Verifica remota e locale
  - MongoDB per storage
  - CLI tool per gestione
  - Attivazione/disattivazione licenze
- **Pros**: Semplice, Go-based, offline verification
- **Cons**: Richiede MongoDB, meno feature di Keygen
- **Verdetto**: ✅ **Candidato valido**

### 4. Licensing.ActivationKeys (.NET)
- **Repo**: https://github.com/SNBSLibs/Licensing.ActivationKeys
- **Tipo**: Open source (.NET)
- **Scope**: Solo libreria client, no server
- **Verdetto**: ❌ Non completo

### 5. Software License Manager (Flask)
- **Repo**: Varie implementazioni su GitHub
- **Tipo**: Open source (Python/Flask)
- **Features**: REST API, MongoDB, Docker
- **Verdetto**: ⚠️ Troppi progetti frammentati, manutenzione incerta

---

## ✅ RACCOMANDAZIONE FINALE

### Opzione A: Keygen EE (Consigliata per stabilità)
Continuare con Keygen in modalità self-hosted (Enterprise Edition).
- **Gratis per uso interno**
- **Feature complete**: activation, offline licenses, floating licenses
- **Documentazione solida**

### Opzione B: f-license (Consigliata per 100% FOSS)
Se vuoi assolutamente 100% open source, f-license è l'opzione migliore.

### Opzione C: Custom License Server (Consigliata per controllo totale)
Implementare un sistema custom semplice basato su:
- **Backend**: Rust/Axum o Go
- **Database**: SQLite (embedded) o PostgreSQL
- **Crypto**: Ed25519 per firme digitali
- **Formato licenza**: JSON firmato + hardware fingerprint

---

## 🏗️ ARCHITETTURA LICENSE CUSTOM (Proposta)

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXION LICENSE SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │  LICENSE     │──────▶  VALIDATION  │                    │
│  │  GENERATOR   │      │  SERVER      │                    │
│  │  (Admin CLI) │      │  (Optional)  │                    │
│  └──────────────┘      └──────────────┘                    │
│         │                         │                         │
│         ▼                         ▼                         │
│  ┌──────────────────────────────────────────────┐          │
│  │           LICENSE FILE FORMAT                │          │
│  │  {                                         │          │
│  │    "key": "XXXX-XXXX-XXXX-XXXX",          │          │
│  │    "verticals": ["meccanico", "dentista"],│          │
│  │    "tier": "professional",                 │          │
│  │    "hardware_hash": "abc123...",          │          │
│  │    "expires": "2027-01-01",               │          │
│  │    "signature": "ed25519..."              │          │
│  │  }                                         │          │
│  └──────────────────────────────────────────────┘          │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────┐          │
│  │         CLIENT VALIDATION (Rust)             │          │
│  │  - Verify signature with public key         │          │
│  │  - Check hardware fingerprint               │          │
│  │  - Check expiration                         │          │
│  │  - Unlock verticals                         │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 IMPLEMENTAZIONE CONSIGLIATA

Dato che vuoi **zero dipendenze esterne** e **100% controllo**, propongo:

### Sistema Ibrido Offline-First

```rust
// src-tauri/src/license/mod.rs

pub struct LicenseManager {
    public_key: Vec<u8>,
    license_cache: Option<License>,
}

pub struct License {
    pub key: String,
    pub tier: LicenseTier,
    pub verticals: Vec<VerticalType>,
    pub hardware_fingerprint: String,
    pub expires_at: Option<DateTime<Utc>>,
    pub signature: Vec<u8>,
}

impl LicenseManager {
    /// Verifica licenza offline
    pub fn verify(&self, license_data: &str) -> Result<License, LicenseError> {
        // 1. Parse JSON
        // 2. Verify Ed25519 signature
        // 3. Check hardware fingerprint
        // 4. Check expiration
        // 5. Return license
    }
    
    /// Genera licenza (solo admin/build tool)
    pub fn generate(
        &self, 
        tier: LicenseTier,
        verticals: Vec<VerticalType>,
        hardware: String,
        duration_days: Option<u32>
    ) -> Result<String, LicenseError> {
        // 1. Build license object
        // 2. Sign with private key
        // 3. Return JSON
    }
}
```

### Vantaggi:
1. **Nessun server richiesto** - Validazione 100% offline
2. **Nessuna dipendenza** - Solo crypto Ed25519
3. **Hardware-locked** - Non condivisibile
4. **Facile distribuzione** - File JSON copiabile
5. **Verticali nel file licenza** - Attivazione selettiva

---

## 📋 DECISIONE RICHIESTA

**Opzione 1**: Continuare con Keygen EE (self-hosted, fair source)
**Opzione 2**: Migrare a f-license (100% open source, MongoDB)
**Opzione 3**: Implementare sistema custom Ed2559 (100% controllo, zero dipendenze)

Quale preferisci? Ti consiglio **Opzione 3** per massima indipendenza.
