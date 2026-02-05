# PROMPT RIPARTENZA - FLUXION Voice Agent & Schede Verticali
**Data**: 04/02/2026  
**Per uso**: Inizio nuova sessione con Kimi/Claude

---

## 🎯 CONTESTO PROGETTO

Sto sviluppando **FLUXION**, un sistema di gestione appuntamenti per PMI italiane con **Voice Agent integrato** e **schede cliente verticali** specifiche per settore.

### Architettura Stack
- **Backend Voice Agent**: Python (Layer 0 Regex, State Machine, Booking Manager)
- **Frontend**: React + TypeScript + Tauri (Rust)
- **Database**: SQLite (migrations in `src-tauri/migrations/`)
- **Comunicazione**: WhatsApp Business API
- **License**: Ed25519 offline, hardware-locked

---

## 📁 FILE ESISTENTI (Implementati Oggi)

### Setup & Configurazione
```
src/types/setup.ts                      ✅ Macro/Micro categorie, License tiers
src/components/setup/SetupWizard.tsx    ✅ 6 step wizard (Dati→Indirizzo→Macro→Micro→Licenza→Config)
src-tauri/src/commands/setup.rs         ✅ Salvataggio macro/micro/tier
```

### Schede Cliente Verticali
```
src/types/scheda-cliente.ts             ✅ Types: Odontoiatrica, Fisioterapia, Estetica, Parrucchiere, Veicoli, Carrozzeria

src/components/schede-cliente/
├── SchedaOdontoiatrica.tsx             ✅ COMPLETA (odontogramma, anamnesi, allergie, trattamenti)
├── SchedaFisioterapia.tsx              ✅ COMPLETA (zone, scale VAS/Oswestry, sedute, diagnosi)
├── SchedaEstetica.tsx                  ✅ COMPLETA (fototipo, tipo pelle, allergie, routine)
├── SchedaParrucchiere.tsx              📝 Placeholder
├── SchedaVeicoli.tsx                   📝 Placeholder
├── SchedaCarrozzeria.tsx               📝 Placeholder
├── SchedaMedica.tsx                    📝 Placeholder
├── SchedaFitness.tsx                   📝 Placeholder
├── SchedaClienteDynamic.tsx            ✅ Switcher con check licenza
└── index.ts                            ✅ Exports

src/hooks/use-schede-cliente.ts         ✅ React Query hooks per tutte le schede
```

### API Rust (Tauri)
```
src-tauri/src/commands/schede_cliente.rs    ✅ 12 comandi: get/upsert per ogni scheda
src-tauri/src/commands/mod.rs               ✅ Export moduli
src-tauri/src/lib.rs                        ✅ Registrati comandi + migrations 019/020
```

### Database Migrations
```
src-tauri/migrations/019_schede_clienti_verticali.sql    ✅ Tabelle 6 schede
src-tauri/migrations/020_license_ed25519.sql             ✅ Campi licenza Ed25519
```

### Sistema Licenze Ed25519
```
src-tauri/Cargo.toml                        ✅ Dipendenza ed25519-dalek
src-tauri/src/commands/license_ed25519.rs   ✅ Comandi: status, activate, verify, fingerprint
src/types/license-ed25519.ts                ✅ Types: FluxionLicense, SignedLicense, TierInfo
src/hooks/use-license-ed25519.ts            ✅ Hooks: useLicenseStatus, useActivateLicense, etc.
src/components/license/
├── LicenseManager.tsx                      ✅ UI completa gestione licenze
└── index.ts                                ✅ Exports
```

### License Generator (Tool Separato)
```
fluxion-license-generator/                  ⚠️ SEPARATO - contiene chiave PRIVATA
├── Cargo.toml                              ✅
├── src/main.rs                             ✅ CLI keygen completo
├── README.md                               ✅ Documentazione
├── .gitignore                              ✅ Esclude chiavi
└── examples/example-license.json           ✅ Esempio formato
```

---

## 🏗️ STRUTTURA DATABASE

### Tabelle Schede (Migration 019)

**schede_odontoiatriche**:
```sql
id, cliente_id, odontogramma (JSON), prima_visita, ultima_visita,
spazzolino, filo_interdentale, collutorio, allergia_lattice,
allergia_anestesia, otturazioni (JSON), estrazioni (JSON), ...
```

**schede_fisioterapia**:
```sql
id, cliente_id, motivo_primo_accesso, data_inizio_terapia,
diagnosi_medica, diagnosi_fisioterapica, zona_principale,
zone_secondarie (JSON), valutazione_iniziale (JSON),
scale_valutazione (JSON), sedute_effettuate (JSON), ...
```

**schede_estetica**:
```sql
id, cliente_id, fototipo, tipo_pelle, allergie_prodotti (JSON),
allergie_profumi, allergie_henne, trattamenti_precedenti (JSON),
problematiche_viso (JSON), gravidanza, allattamento, ...
```

*(e altre 3 tabelle: schede_parrucchiere, schede_veicoli, schede_carrozzeria)*

### License Cache (Migration 020)
```sql
license_data (TEXT),        -- JSON licenza
license_signature (TEXT),   -- Firma base64
licensee_name, licensee_email,
enabled_verticals (JSON),   -- ["odontoiatrica", "estetica"]
features (JSON),            -- {voice_agent: true, ...}
is_ed25519 (INTEGER)        -- 1 = Ed25519, 0 = Keygen legacy
```

---

## 🔧 COMANDI TAURI DISPONIBILI

### Setup
- `get_setup_status` → SetupStatus
- `get_setup_config` → SetupConfig
- `save_setup_config` → void

### Schede Cliente
- `get_scheda_odontoiatrica` → SchedaOdontoiatrica | null
- `upsert_scheda_odontoiatrica` → string (id)
- `get_scheda_fisioterapia` → SchedaFisioterapia | null
- `upsert_scheda_fisioterapia` → string (id)
- `get_scheda_estetica` → SchedaEstetica | null
- `upsert_scheda_estetica` → string (id)
- *(e altri 6 comandi per parrucchiere, veicoli, carrozzeria)*

### Licenze Ed25519
- `get_license_status_ed25519` → LicenseStatus
- `activate_license_ed25519(licenseData: string)` → ActivationResult
- `deactivate_license_ed25519` → void
- `get_machine_fingerprint_ed25519` → string
- `check_feature_access_ed25519(feature: string)` → boolean
- `check_vertical_access_ed25519(vertical: string)` → boolean
- `get_tier_info_ed25519` → TierInfo[]

---

## 🎨 COMPONENTI REACT DISPONIBILI

### Setup
```tsx
import { SetupWizard } from './components/setup/SetupWizard';
// 6 step wizard completo
```

### Schede Cliente
```tsx
import { 
  SchedaClienteDynamic,    // Switcher automatico
  SchedaOdontoiatrica,     // Completa
  SchedaFisioterapia,      // Completa
  SchedaEstetica,          // Completa
  SchedaParrucchiere,      // Placeholder
  SchedaVeicoli,           // Placeholder
  SchedaCarrozzeria,       // Placeholder
} from './components/schede-cliente';

// Uso switcher automatico
<SchedaClienteDynamic clienteId="123" />

// Uso specifico
<SchedaOdontoiatrica clienteId="123" />
```

### Licenze
```tsx
import { LicenseManager } from './components/license';
<LicenseManager />  // UI completa gestione licenze
```

### Hooks
```tsx
import { useSchedaOdontoiatrica, useSaveSchedaOdontoiatrica } from './hooks/use-schede-cliente';
import { useLicenseStatusEd25519, useActivateLicenseEd25519 } from './hooks/use-license-ed25519';
```

---

## 💰 SISTEMA LICENZE

### Tier
| Tier | Prezzo | Verticali | Voice | API |
|------|--------|-----------|-------|-----|
| Trial | Gratis | Tutte | ✅ | ✅ | 30gg |
| Base | €199 | 1 | ❌ | ❌ | Lifetime |
| Pro | €399 | 3 | ✅ | ❌ | Lifetime |
| Enterprise | €799 | Tutte | ✅ | ✅ | Lifetime |

### Mapping Verticali → Schede
```typescript
const VERTICALE_PER_MICRO_CATEGORIA = {
  'odontoiatra': 'odontoiatrica',
  'fisioterapia': 'fisioterapia',
  'osteopata': 'fisioterapia',
  'estetista_viso': 'estetica',
  'salone_donna': 'parrucchiere',
  'officina_meccanica': 'veicoli',
  'carrozzeria': 'carrozzeria',
  'palestra': 'fitness',
  // ... (40+ mapping)
};
```

---

## 🔐 SECURITY NOTES

1. **License Generator** (`fluxion-license-generator/`):
   - Contiene chiave PRIVATA Ed25519
   - MAI committare su repo pubblica
   - Conservare offline/USB cifrata

2. **Chiave Pubblica**:
   - Embedded in `license_ed25519.rs` come `FLUXION_PUBLIC_KEY_HEX`
   - Placeholder da sostituire con keypair reale

3. **Hardware Fingerprint**:
   - SHA-256(hostname + CPU + RAM + OS)
   - Unico per macchina, non clonabile

---

## ✅ CHECKLIST PROSSIMA SESSIONE

### Build & Test
- [ ] `cd src-tauri && cargo build` - Verificare errori
- [ ] Sostituire `FLUXION_PUBLIC_KEY_HEX` con chiave pubblica reale
- [ ] `npm run tauri dev` - Test app completa

### Test E2E
- [ ] Wizard setup: seleziona macro → micro → licenza
- [ ] Pagina cliente: carica scheda corretta
- [ ] Scheda odontoiatrica: modifica odontogramma, salva
- [ ] Scheda fisioterapia: aggiungi seduta, salva
- [ ] Scheda estetica: seleziona fototipo, salva
- [ ] Licenza: copia fingerprint, genera licenza (tool), attiva

### Implementazioni Mancanti
- [ ] Completare SchedaParrucchiere (colorazioni, chimica)
- [ ] Completare SchedaVeicoli (tagliandi, gomme)
- [ ] Completare SchedaCarrozzeria (danni, foto)
- [ ] UI Admin: dashboard licenze attive

---

## 📚 REFERENZE

### Documentazione
- `REPORT-EMMEDI-2026-02-04.md` - Report completo implementazione
- `fluxion-license-generator/README.md` - Istruzioni keygen
- `CLAUDE.md` - Contesto progetto

### Mockup & Design
- `docs/MOCKUP-SCHEDE-CLIENTE.md` - Visione UI schede
- `docs/VERTICALS-FINAL-6.md` - Ricerca settori

---

## ❓ DOMANDE FREQUENTI

**Q: Come si genera una licenza per un cliente?**
A: 
1. Cliente copia fingerprint da Impostazioni > Licenza
2. Vendor esegue: `cd fluxion-license-generator && cargo run -- generate --fingerprint <fp> --tier pro`
3. Invia file `license.json` al cliente
4. Cliente carica file in app > Attiva

**Q: Cosa succede se cambio PC?**
A: Il fingerprint cambia, serve nuova licenza. Contattare supporto per trasferimento.

**Q: Posso usare Keygen.sh vecchio?**
A: Sì, è mantenuto per retrocompatibilità. Il nuovo sistema è preferito quando `is_ed25519 = 1`.

---

## 🚀 COMANDO RAPIDO

```bash
# Build veloce
cd src-tauri && cargo check

# Test app
npm run tauri dev

# Genera licenza (tool separato)
cd fluxion-license-generator
cargo run -- init  # Prima volta solo
cargo run -- generate --tier pro --fingerprint "abc123..."
```

---

**INIZIA LA SESSIONE CON**: "Continuiamo da dove abbiamo lasciato. Verifichiamo la build e testiamo il sistema."
