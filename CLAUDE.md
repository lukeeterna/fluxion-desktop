# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: Saloni, palestre, cliniche, officine (1-15 dipendenti)
- **Model**: Licenza LIFETIME desktop (NO SaaS, NO commissioni)
- **Voice**: "Sara" - assistente vocale prenotazioni (5-layer RAG pipeline)
- **License**: Ed25519 offline, 3 tier (Base/Pro/Enterprise), 6 verticali

## Critical Rules
1. Never commit API keys, secrets, or .env files
2. Always TypeScript (never JS), always async Tauri commands
3. Run tests before commit (see `.claude/rules/testing.md` for checklist)
4. A task is NOT complete until code works AND is verified (DB records, E2E)
5. Italian field names in APIs: `servizio`, `data`, `ora`, `cliente_id`
6. Dev on MacBook, test on iMac (192.168.1.7) - Tauri needs macOS 12+
7. Restart voice pipeline on iMac after ANY Python change

## Active Sprint
```yaml
branch: feat/workflow-tools
phase: Implementation Complete - Testing Phase
status: Context 95% - Ready for Build & Test
tests: 955 passing (voice-agent)
next_step: Build verification & E2E testing
```

## Stato Attuale (2026-02-04) - SESSIONE COMPLETATA

### ✅ IMPLEMENTATO OGGI

#### 1. Setup Wizard con Macro/Micro Categorie + Licenza
- **6 Step Wizard**: Dati → Indirizzo → Macro → Micro → Licenza → Config
- **Macro Categorie**: 6 categorie (medico, beauty, hair, auto, wellness, professionale)
- **Micro Categorie**: 40+ sottocategorie mappate
- **Tier Selection**: Trial, Base (€199), Pro (€399), Enterprise (€799)
- **File**: `SetupWizard.tsx`, `setup.ts`, `setup.rs`

#### 2. Schede Cliente Verticali - 3 COMPLETE + 5 PLACEHOLDER

| Scheda | Stato | Feature Principali |
|--------|-------|-------------------|
| **Odontoiatrica** | ✅ COMPLETA | Odontogramma FDI interattivo, anamnesi, allergie, trattamenti |
| **Fisioterapia** | ✅ COMPLETA | Zone corpo, scale VAS/Oswestry/NDI, sedute con progresso |
| **Estetica** | ✅ COMPLETA | Fototipo Fitzpatrick, tipo pelle, allergie, routine skincare |
| Parrucchiere | 📝 Placeholder | Pronto per sviluppo |
| Veicoli | 📝 Placeholder | Pronto per sviluppo |
| Carrozzeria | 📝 Placeholder | Pronto per sviluppo |
| Medica | 📝 Placeholder | Pronto per sviluppo |
| Fitness | 📝 Placeholder | Pronto per sviluppo |

**Database**: Migration 019 con 6 tabelle schede
**API Rust**: 12 comandi CRUD in `schede_cliente.rs`
**Hooks React**: `use-schede-cliente.ts` con React Query

#### 3. Switcher Dinamico (`SchedaClienteDynamic.tsx`)
- Mappa `micro_categoria` → Componente scheda
- Integrazione con sistema licenze (verifica accesso verticale)
- Fallback a SchedaBase o SchedaBloccata

#### 4. Sistema Licenze Ed25519 (Offline)

##### Backend (Rust)
- **File**: `license_ed25519.rs`
- **Features**: Firma Ed25519, hardware-locked, 3 tier, verticali abilitate
- **Comandi**: 7 comandi Tauri (status, activate, verify, fingerprint, check access)
- **Migration**: 020 - Campi Ed25519 in license_cache

##### Frontend (React)
- **Types**: `license-ed25519.ts` - Tipi completi
- **Hooks**: `use-license-ed25519.ts` - React Query hooks
- **UI**: `LicenseManager.tsx` - Gestione licenze completa (3 tab)

##### License Generator (Tool Separato)
- **Path**: `fluxion-license-generator/`
- **Sicurezza**: Contiene chiave PRIVATA - mai committare
- **Comandi**: init, generate, verify, info, fingerprint

### 📁 FILE CREATI (25+ file)

#### Frontend
```
src/types/
  ├── setup.ts [MOD] +Macro/Micro/License
  ├── scheda-cliente.ts [NEW]
  ├── license-ed25519.ts [NEW]
  └── index.ts [NEW]

src/hooks/
  ├── use-schede-cliente.ts [NEW]
  └── use-license-ed25519.ts [NEW]

src/components/
  ├── setup/SetupWizard.tsx [MOD]
  ├── schede-cliente/
  │   ├── SchedaOdontoiatrica.tsx [NEW] ✅
  │   ├── SchedaFisioterapia.tsx [NEW] ✅
  │   ├── SchedaEstetica.tsx [NEW] ✅
  │   ├── SchedaParrucchiere.tsx [NEW]
  │   ├── SchedaVeicoli.tsx [NEW]
  │   ├── SchedaCarrozzeria.tsx [NEW]
  │   ├── SchedaMedica.tsx [NEW]
  │   ├── SchedaFitness.tsx [NEW]
  │   ├── SchedaClienteDynamic.tsx [NEW]
  │   └── index.ts [NEW]
  └── license/
      ├── LicenseManager.tsx [NEW]
      └── index.ts [NEW]
```

#### Backend
```
src-tauri/
  ├── Cargo.toml [MOD] +ed25519-dalek
  ├── src/
  │   ├── lib.rs [MOD] +Migrations 019/020
  │   └── commands/
  │       ├── setup.rs [MOD]
  │       ├── schede_cliente.rs [NEW]
  │       ├── license_ed25519.rs [NEW]
  │       └── mod.rs [MOD]
  └── migrations/
      ├── 019_schede_clienti_verticali.sql [NEW]
      └── 020_license_ed25519.sql [NEW]
```

#### Tool Separato
```
fluxion-license-generator/
  ├── Cargo.toml [NEW]
  ├── src/main.rs [NEW]
  ├── README.md [NEW]
  └── .gitignore [NEW]
```

### 💰 BUSINESS MODEL - TIER LICENZE

| Tier | Prezzo | Verticali | Voice | API | Durata |
|------|--------|-----------|-------|-----|--------|
| Trial | €0 | Tutte | ✅ | ✅ | 30 giorni |
| Base | €199 | 1 | ❌ | ❌ | Lifetime |
| Pro | €399 | 3 | ✅ | ❌ | Lifetime |
| Enterprise | €799 | Tutte | ✅ | ✅ | Lifetime |

### 🔐 SECURITY

1. **License Generator** (`fluxion-license-generator/`)
   - Tool separato con chiave PRIVATA Ed25519
   - Mai committare su repo pubblica
   - Conservare offline/USB cifrata

2. **Chiave Pubblica**: Embedded in `license_ed25519.rs`
   - Placeholder da sostituire con keypair reale

3. **Hardware Lock**: Fingerprint SHA-256
   - Hostname + CPU + RAM + OS

### 📚 DOCUMENTAZIONE CREATA

- `REPORT-EMMEDI-2026-02-04.md` - Report completo implementazione
- `PROMPT-RIPARTENZA-2026-02-04.md` - Prompt per ripartenza
- `fluxion-license-generator/README.md` - Istruzioni tool

## Prossimi Step (Prossima Sessione)

### 1. Build & Test
```bash
cd src-tauri && cargo build    # Verificare errori
npm run tauri dev              # Test app
```

### 2. Setup Chiavi
```bash
cd fluxion-license-generator
cargo run -- init              # Genera keypair
# Copia chiave pubblica in license_ed25519.rs
```

### 3. Test E2E
- [ ] Wizard: seleziona macro → micro → licenza
- [ ] Pagina cliente: carica scheda corretta
- [ ] Scheda odontoiatrica: modifica odontogramma
- [ ] Scheda fisioterapia: aggiungi seduta
- [ ] Scheda estetica: seleziona fototipo
- [ ] Licenza: copia fingerprint → genera → attiva

### 4. Implementazioni Mancanti (Future)
- [ ] SchedaParrucchiere completa (colorazioni, chimica)
- [ ] SchedaVeicoli completa (tagliandi, gomme)
- [ ] SchedaCarrozzeria completa (danni, foto)
- [ ] UI Admin dashboard licenze

## Checkpoint Files (per ripartenza)
- `PROMPT-RIPARTENZA-2026-02-04.md` ⭐ NUOVO - Usa questo!
- `REPORT-EMMEDI-2026-02-04.md` - Report tecnico
- `docs/VERTICALS-FINAL-6.md` - Ricerca verticali
- `fluxion-license-generator/` - Tool licenze

## Context Status
✅ **95%** - Implementation Complete - Ready for Testing
Last save: 2026-02-04 14:50
Action: Build verification & E2E testing
