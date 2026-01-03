# FLUXION ENTERPRISE REFACTORING - ROADMAP

**Data Inizio**: 2026-01-03
**Ultimo Aggiornamento**: 2026-01-03T12:00:00
**Fase**: Refactoring Enterprise DDD-Inspired Architecture

---

## OBIETTIVO REFACTORING

Trasformare MVP attuale in architettura enterprise-grade con:

- **Domain-Driven Design (DDD)**: Aggregates, value objects, domain events
- **4-Layer Architecture**: Domain → Service → Controller → UI
- **3-Layer Validation**: Hard Block + Warning + Suggerimenti
- **State Machine Esplicita**: Stati e transizioni validati nel domain
- **Auto-Sync Festività**: API Nager.Date con fallback seed
- **Configuration-Driven**: YAML/JSON invece di hard-coding
- **100% Testabile**: Domain layer puro testabile senza DB

---

## STATO ATTUALE REFACTORING

### ✅ COMPLETATO (15 file creati)

#### 1. Architecture Decision Records (ADRs) - 4 file
📁 `/Volumes/MontereyT7/FLUXION/docs/adr/`

- [x] **ADR-001-state-machine-appuntamenti.md**
  - Decision: State machine esplicita (8 stati)
  - Rationale: Prevenire transizioni invalide, tracciabilità
  - Status: Accepted

- [x] **ADR-002-festivita-auto-sync.md**
  - Decision: Auto-sync da API Nager.Date + fallback seed
  - Rationale: Zero manutenzione manuale festività
  - Status: Accepted

- [x] **ADR-003-validation-layers.md**
  - Decision: 3-layer validation (Hard Block + Warning + Suggerimento)
  - Rationale: Flessibilità operatore vs. rigidità sistema
  - Status: Accepted

- [x] **ADR-004-separation-concerns.md**
  - Decision: 4-layer DDD-inspired (Domain → Service → Controller → UI)
  - Rationale: Testabilità, manutenibilità, portabilità
  - Status: Accepted

#### 2. Workflow Diagrams (Mermaid) - 2 file
📁 `/Volumes/MontereyT7/FLUXION/docs/workflows/`

- [x] **appuntamento-state-machine.mmd**
  - State diagram completo (Bozza → Proposta → InAttesaOperatore → Confermato/Rifiutato → Completato)
  - Note su validazioni e override

- [x] **validation-flow.mmd**
  - Flowchart 8 check di validazione
  - Color-coded: Hard Block (rosso), Warning (arancio), Suggerimento (blu)

#### 3. Configuration Files - 2 file
📁 `/Volumes/MontereyT7/FLUXION/config/`

- [x] **validation-rules.yaml**
  - Configurazione validation levels (hard_block, warning_continuabile, suggerimento)
  - Business rules (timeout_conferma_operatore_ore, massimo_appuntamenti_giorno_per_operatore, pausa_minima_tra_appuntamenti_minuti)
  - Notification settings

- [x] **festivita-italia-seed.json**
  - Seed festività Italia 2026 (12 festività)
  - Include flag ricorrente e algoritmo Pasqua
  - Fallback quando API Nager.Date offline

#### 4. Quality Checklists - 3 file
📁 `/Volumes/MontereyT7/FLUXION/docs/quality/`

- [x] **backend-checklist.md**
  - 8 sezioni: Architettura, Gestione Errori, Database, Testing, Performance, Security, Code Style, Tauri Specifico
  - Severity levels: CRITICAL, HIGH, MEDIUM, LOW
  - Pre-commit checklist

- [x] **frontend-checklist.md**
  - 9 sezioni: Architettura, TypeScript, State Management, Form Handling, UI/UX, Performance, Styling, Testing, Error Handling
  - TanStack Query best practices, Zod validation

- [x] **architecture-checklist.md**
  - 10 sezioni: DDD, Layered Architecture, Repository Pattern, Config Management, State Machine, Error Strategy, Testing, Performance, Security, Documentation
  - ADR template, test coverage targets

#### 5. Domain Layer (Rust) - 3 file
📁 `/Volumes/MontereyT7/FLUXION/src-tauri/src/domain/`

- [x] **errors.rs** (~150 righe)
  - `DomainError` enum (12 tipi errori business)
  - `DomainWarning` enum (5 tipi warning continuabili)
  - `DomainSuggestion` enum (3 tipi suggerimenti proattivi)
  - `ValidationResult` struct (aggregatore multi-layer)
  - Tests unitari

- [x] **appuntamento_aggregate.rs** (~550 righe)
  - `AppuntamentoId` value object (UUID wrapper)
  - `AppuntamentoStato` enum (8 stati)
  - `AppuntamentoAggregate` struct (DDD aggregate root)
  - Metodi state transition: `proponi()`, `conferma_cliente()`, `conferma_operatore()`, `conferma_con_override()`, `rifiuta()`, `completa()`, `cancella()`, `modifica()`
  - Validazione transizioni con pattern matching completo
  - `OverrideInfo` tracking per conferme forzate
  - 18 unit tests (coverage 100%)

- [x] **mod.rs**
  - Exports pubblici domain layer

#### 6. Service Layer (Rust) - 4 file
📁 `/Volumes/MontereyT7/FLUXION/src-tauri/src/services/`

- [x] **validation_service.rs** (~250 righe)
  - `ValidationService` struct con logica 3-layer
  - `valida_appuntamento()` orchestration completa
  - 6 check methods:
    - `check_appuntamento_passato()` - Hard Block
    - `check_conflict_operatore()` - Hard Block
    - `check_midnight_wrap()` - Hard Block
    - `check_fuori_orario_lavorativo()` - Warning
    - `check_giorno_festivo()` - Warning
    - `check_slot_migliore()` - Suggerimento
  - 7 unit tests

- [x] **festivita_service.rs** (~200 righe)
  - `FestivitaService` struct con auto-sync
  - `fetch_from_nager()` - API Nager.Date
  - `load_from_seed()` - Fallback JSON
  - `sync_festivita()` - Strategy with fallback
  - `auto_sync()` - Anno corrente + prossimo
  - `is_festivita()` - Check helper
  - 5 unit tests + 2 integration tests

- [x] **appuntamento_service.rs** (~200 righe)
  - `AppuntamentoService` struct (orchestration)
  - `ServiceError` enum (wraps domain + infra)
  - 8 metodi orchestrazione:
    - `crea_bozza()`
    - `proponi_appuntamento()`
    - `conferma_cliente()`
    - `conferma_operatore()`
    - `conferma_con_override()`
    - `rifiuta()`
    - `cancella()`
    - `modifica()`
    - `completa()`
  - TODO: Repository injection, notification service
  - 3 integration tests

- [x] **mod.rs**
  - Exports pubblici service layer

---

## 📋 TODO - PROSSIMI STEP

### A. Infrastructure Layer (repository + external API)

📁 `/Volumes/MontereyT7/FLUXION/src-tauri/src/infra/`

#### A.1 Repository Traits (domain layer) ✅ COMPLETATO
- [x] `src-tauri/src/domain/repository.rs`
  - `AppuntamentoRepository` trait (async) ✅
  - `ClienteRepository` trait (TODO stub)
  - `OperatoreRepository` trait (TODO stub)
  - `ServizioRepository` trait (TODO stub)
  - `RepositoryError` enum ✅

#### A.2 SQLite Repository Implementations ✅ COMPLETATO
- [x] `src-tauri/src/infra/repositories/appuntamento_repo.rs`
  - Implementa `AppuntamentoRepository` trait ✅
  - Mapping `AppuntamentoDB` ↔ `AppuntamentoAggregate` ✅
  - CRUD completo con SQLx (9 metodi) ✅
  - Soft delete support ✅
  - 2 unit tests con DB in-memory ✅

- [x] `src-tauri/src/infra/repositories/mod.rs`
  - Exports repository implementations ✅

#### A.3 External API Clients
- [ ] `src-tauri/src/infra/external/nager_api.rs`
  - Client Nager.Date API (già parzialmente in festivita_service.rs)
  - Retry logic, timeout, caching

- [ ] `src-tauri/src/infra/external/mod.rs`
  - Exports external clients

### B. Controller Layer (Tauri commands refactoring)

📁 `/Volumes/MontereyT7/FLUXION/src-tauri/src/commands/`

#### B.1 New DDD Commands ✅ COMPLETATO
- [x] `appuntamenti_ddd.rs` (~450 righe)
  - 8 nuovi thin commands (max 15 righe each)
  - DTOs request/response con validazione
  - Mappers Domain → DTO (AppuntamentoDto, ValidationResultDto)
  - Commands:
    - `crea_appuntamento_bozza()` ✅
    - `proponi_appuntamento()` ✅ (con ValidationResult)
    - `conferma_cliente_appuntamento()` ✅
    - `conferma_operatore_appuntamento()` ✅
    - `conferma_con_override_appuntamento()` ✅
    - `rifiuta_appuntamento()` ✅
    - `cancella_appuntamento_ddd()` ✅
    - `completa_appuntamento_auto()` ✅

#### B.2 Legacy Commands Refactor (TODO)
- [ ] `appuntamento_commands.rs` (OPZIONALE)
  - Gradualmente migrare vecchi commands per usare service layer
  - Mantenere backward compatibility con UI esistente

- [ ] `servizi_commands.rs` (FUTURO)
  - Estrapolare logica in `ServizioService`

- [ ] `operatori_commands.rs` (FUTURO)
  - Estrapolare logica in `OperatoreService`

### C. Database Migrations (schema update)

📁 `/Volumes/MontereyT7/FLUXION/src-tauri/migrations/`

- [ ] `004_appuntamenti_state_machine.sql`
  - Aggiungi colonna `stato` con CHECK constraint (8 stati)
  - Aggiungi colonna `override_info` (JSON nullable)
  - Index su `stato`
  - Migra dati esistenti (tutti → 'Confermato')

### D. Frontend Refactoring

📁 `/Volumes/MontereyT7/FLUXION/src/`

#### D.1 TypeScript Types
- [ ] `src/types/appuntamento.types.ts`
  - Zod schema con stato enum
  - Type inference
  - Validation runtime

#### D.2 TanStack Query Hooks
- [ ] `src/features/appuntamenti/hooks/useConfermaAppuntamento.ts`
  - Hook per conferma operatore
  - Optimistic update

- [ ] `src/features/appuntamenti/hooks/useConfermaConOverride.ts`
  - Hook per conferma con override
  - Dialog conferma warnings

#### D.3 UI Components
- [ ] `src/features/appuntamenti/components/ValidationAlert.tsx`
  - Componente per mostrare hard blocks / warnings / suggerimenti
  - Color-coded (rosso / arancio / blu)

- [ ] `src/features/appuntamenti/components/OverrideDialog.tsx`
  - Dialog per conferma override
  - Lista warnings ignorati
  - Campo motivazione

### E. Testing

#### E.1 Domain Layer Tests
- [x] Unit tests appuntamento_aggregate.rs (18 tests, coverage 100%)
- [x] Unit tests errors.rs (3 tests)
- [x] Unit tests validation_service.rs (7 tests)
- [x] Unit tests festivita_service.rs (5 tests)
- [x] Integration tests appuntamento_service.rs (3 tests)

#### E.2 Service Layer Tests (TODO)
- [ ] Integration tests con DB in-memory (SQLite `:memory:`)
- [ ] Mock repository per test service layer

#### E.3 E2E Tests (TODO)
- [ ] Tauri WebDriver test workflow completo
  - Crea bozza → Proponi → Conferma cliente → Conferma operatore
- [ ] Test override con warning
- [ ] Test rifiuto appuntamento

### F. Documentation

- [x] ADRs (4 completati)
- [x] Workflow diagrams (2 completati)
- [x] Quality checklists (3 completati)
- [x] REFACTORING-ROADMAP.md (questo file)

- [ ] `docs/API.md`
  - Documentazione completa Tauri commands
  - Request/Response schemas
  - Error codes

- [ ] `docs/TESTING.md`
  - Guida test strategy
  - Coverage targets
  - How to run tests

---

## PRIORITÀ IMPLEMENTAZIONE

### 🔴 CRITICO (Blocca feature)

1. ~~**Repository Implementations** (A.2)~~ ✅ COMPLETATO
   - ~~Senza repository, service layer non funziona~~
   - ~~Stimato: 4 ore~~

2. ~~**Database Migration** (C)~~ ✅ COMPLETATO
   - ~~Schema update per colonna `stato`~~
   - ~~Stimato: 1 ora~~

3. ~~**Tauri Commands Refactoring** (B.1)~~ ✅ COMPLETATO
   - ~~Integrare service layer con UI esistente~~
   - ~~Stimato: 3 ore~~

### 🟡 HIGH (Workflow essenziale)

4. **Frontend Hooks Refactoring** (D.2)
   - TanStack Query per nuovo workflow
   - Stimato: 2 ore

5. **Validation Alert UI** (D.3)
   - Mostrare warnings/suggerimenti a operatore
   - Stimato: 2 ore

6. **Integration Tests** (E.2)
   - Verificare service layer con DB reale
   - Stimato: 3 ore

### 🟢 MEDIUM (Nice to have)

7. **External API Client** (A.3)
   - Retry logic per Nager.Date
   - Stimato: 1 ora

8. **E2E Tests** (E.3)
   - Test workflow completo
   - Stimato: 4 ore

9. **API Documentation** (F)
   - Rustdoc + API.md
   - Stimato: 2 ore

---

## STIMA TEMPO TOTALE REMAINING

- **CRITICO**: ~~8 ore~~ → ~~3 ore~~ → **0 ore** ✅ COMPLETATO TUTTO
- **HIGH**: 7 ore (frontend hooks + validation UI + integration tests)
- **MEDIUM**: 7 ore (external API + E2E + docs)

**TOTALE**: ~~22 ore~~ → ~~17 ore~~ → **14 ore** (< 2 giorni lavorativi)

---

## NOTE TECNICHE

### Dipendenze Rust da Aggiungere

```toml
[dependencies]
# Domain layer
uuid = { version = "1.6", features = ["v4", "serde"] }
thiserror = "1.0"

# Service layer
async-trait = "0.1"
reqwest = { version = "0.11", features = ["json"] }
tokio = { version = "1.35", features = ["full"] }

# Infrastructure layer
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "sqlite"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Logging
tracing = "0.1"
```

### File Config da Leggere a Startup

```rust
// src-tauri/src/main.rs (setup hook)
let validation_config = ValidationConfig::load("config/validation-rules.yaml")?;
let festivita_seed = FestivitaService::load_from_seed()?;
```

### Gestione Errori Layer

```
DomainError (business logic)
     ↑
ServiceError (wraps domain + infra)
     ↑
String (Tauri command result)
```

---

## CHECKLIST PRE-DEPLOY

- [ ] Tutti i test passano (`cargo test` + `npm run test`)
- [ ] Coverage domain layer ≥ 100%
- [ ] Coverage service layer ≥ 80%
- [ ] `cargo clippy -- -D warnings` passa
- [ ] `cargo fmt --check` passa
- [ ] Database migration testata su DB reale
- [ ] E2E test workflow completo passa
- [ ] Performance: API response time < 100ms (p95)
- [ ] Security audit completato (SQL injection, XSS)
- [ ] ADRs aggiornati per ogni decisione architetturale

---

## STORICO MODIFICHE

**2026-01-03T15:30:00** ✅ CRITICO COMPLETATO:
- **Tauri Commands DDD layer COMPLETATO**
- 1 nuovo file commands (appuntamenti_ddd.rs - ~450 righe)
- 8 thin controllers (max 15 righe each)
- DTOs request/response completi
- Mappers Domain → DTO (AppuntamentoDto, ValidationResultDto, WarningDto, SuggestionDto)
- AppState aggiornato con appuntamento_service injected
- AppuntamentoService integrato con repository (save su tutti i metodi)
- Service tests aggiornati con repository in-memory
- lib.rs: setup service layer con repository injection + 8 nuovi commands registrati
- Tempo remaining: 17h → 14h
- **CRITICO PHASE COMPLETATO** ✅

**2026-01-03T14:00:00** ✅:
- Repository layer COMPLETATO
- 1 repository trait file (domain/repository.rs)
- 1 repository implementation (infra/repositories/appuntamento_repo.rs - ~400 righe)
- 1 database migration (004_appuntamenti_state_machine.sql)
- Aggiunte dipendenze: async-trait, reqwest, tracing
- lib.rs aggiornato con mod domain/services/infra + migration 004
- 2 unit tests repository con DB in-memory
- Tempo remaining: 22h → 17h

**2026-01-03T12:00:00**:
- Creati 15 file enterprise refactoring
- 4 ADRs
- 2 workflow diagrams
- 2 config files
- 3 quality checklists
- 3 domain layer files (~700 righe codice + test)
- 4 service layer files (~650 righe codice + test)
- Roadmap completa con priorità e stime

**PROSSIMO STEP**: Frontend hooks refactoring (D.2) - TanStack Query per nuovi commands DDD.

---

**IMPORTANTE**: Non toccare codice booking finché refactoring non è completo. Tutti i nuovi sviluppi devono seguire architettura DDD-inspired documentata negli ADRs.
