# Architecture Quality Checklist

**Versione**: 1.0
**Ultimo aggiornamento**: 2026-01-03

Checklist per decisioni architetturali e review di sistema.

---

## 1. Domain-Driven Design (DDD)

- [ ] **Aggregates**: Entità root con invarianti consistenti
- [ ] **Value Objects**: Tipi immutabili per concetti domain (es. `AppuntamentoId`)
- [ ] **Domain Events**: Eventi business per notifiche asincrone
- [ ] **Ubiquitous Language**: Nomenclatura condivisa tra business e code
- [ ] **Bounded Contexts**: Separazione logica tra moduli (Calendario, CRM, Fatture)

**Esempio CORRETTO**:
```rust
// ✅ Aggregate root
pub struct AppuntamentoAggregate {
    id: AppuntamentoId,
    stato: AppuntamentoStato,
    eventi: Vec<DomainEvent>,
}

impl AppuntamentoAggregate {
    pub fn conferma(&mut self) -> Result<(), DomainError> {
        self.validate_transizione(AppuntamentoStato::Confermato)?;
        self.stato = AppuntamentoStato::Confermato;
        self.eventi.push(DomainEvent::AppuntamentoConfermato { id: self.id });
        Ok(())
    }

    // ✅ Invariante protetto
    fn validate_transizione(&self, target: AppuntamentoStato) -> Result<(), DomainError> {
        match (&self.stato, &target) {
            (AppuntamentoStato::InAttesaOperatore, AppuntamentoStato::Confermato) => Ok(()),
            _ => Err(DomainError::TransizioneNonValida),
        }
    }
}

// ✅ Value object
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct AppuntamentoId(Uuid);

impl AppuntamentoId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}
```

**Esempio SBAGLIATO (Anemic Domain Model)**:
```rust
// ❌ Struct passivo, logica nei service
pub struct Appuntamento {
    pub id: String,
    pub stato: String, // ❌ String invece di enum
    // Nessun metodo, solo dati
}

// ❌ Service con tutta la logica business
impl AppuntamentoService {
    pub fn conferma(&self, id: String) {
        // ❌ Logica business nel service invece che nel domain
        let app = self.repo.find(id);
        if app.stato == "InAttesaOperatore" {
            app.stato = "Confermato";
            self.repo.save(app);
        }
    }
}
```

---

## 2. Layered Architecture

- [ ] **4 Layer**: Domain → Service → Controller → UI
- [ ] **Dependency Rule**: Layer esterni dipendono da interni (mai viceversa)
- [ ] **Interfaces/Traits**: Service dipende da trait, non da impl
- [ ] **No Skip Layer**: UI non chiama direttamente domain (passa da service)

**Data Flow Corretto**:
```
User Input (UI)
     ↓
Tauri Command (Controller) — validation, deserialization
     ↓
Service Layer — orchestration, transactions
     ↓
Domain Layer — business logic, invariants
     ↓
Repository Trait — abstraction
     ↓
Repository Impl — persistence
     ↓
Database
```

**Dependency Direction**:
```
UI → Controller → Service → Domain
                    ↓
                Repository Trait ← Repository Impl → DB
```

---

## 3. Repository Pattern

- [ ] **Trait Abstraction**: Repository è trait, non struct
- [ ] **Domain Types**: Repository usa domain types, non DB types
- [ ] **No Leaky Abstraction**: Trait non espone SQL/Serde
- [ ] **Transaction Support**: Metodi transaction-aware

**Esempio CORRETTO**:
```rust
// ✅ Repository trait (domain layer)
#[async_trait]
pub trait AppuntamentoRepository: Send + Sync {
    async fn find_by_id(&self, id: AppuntamentoId) -> Result<Option<AppuntamentoAggregate>, RepositoryError>;
    async fn save(&self, aggregate: &AppuntamentoAggregate) -> Result<(), RepositoryError>;
    async fn list(&self) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;
}

// ✅ Implementazione SQLite (infra layer)
pub struct SqliteAppuntamentoRepository {
    pool: SqlitePool,
}

#[async_trait]
impl AppuntamentoRepository for SqliteAppuntamentoRepository {
    async fn find_by_id(&self, id: AppuntamentoId) -> Result<Option<AppuntamentoAggregate>, RepositoryError> {
        let row = sqlx::query_as::<_, AppuntamentoDB>("SELECT * FROM appuntamenti WHERE id = ?")
            .bind(id.to_string())
            .fetch_optional(&self.pool)
            .await?;

        Ok(row.map(AppuntamentoAggregate::from)) // ✅ Mapping DB → Domain
    }
}
```

**Esempio SBAGLIATO**:
```rust
// ❌ Repository ritorna DB types
impl AppuntamentoRepository {
    async fn find(&self, id: String) -> Result<AppuntamentoDB, sqlx::Error> {
        // ❌ Espone dettagli DB (sqlx::Error, AppuntamentoDB)
        sqlx::query_as("SELECT * FROM appuntamenti WHERE id = ?")
            .bind(id)
            .fetch_one(&self.pool)
            .await
    }
}
```

---

## 4. Configuration Management

- [ ] **Externalized Config**: No hard-coded values
- [ ] **YAML/JSON Files**: `config/*.yaml` per business rules
- [ ] **Environment Variables**: `.env` per secrets
- [ ] **Runtime Override**: UI Impostazioni può modificare config
- [ ] **Validation**: Config validato a startup

**Esempio CORRETTO**:
```yaml
# config/validation-rules.yaml
validation_levels:
  hard_block:
    - appuntamento_passato
    - conflict_operatore_stesso_orario

business_rules:
  timeout_conferma_operatore_ore: 24
  massimo_appuntamenti_giorno_per_operatore: 8
  pausa_minima_tra_appuntamenti_minuti: 15
```

```rust
// ✅ Caricamento config a startup
#[derive(Deserialize)]
pub struct ValidationConfig {
    pub validation_levels: ValidationLevels,
    pub business_rules: BusinessRules,
}

impl ValidationConfig {
    pub fn load() -> Result<Self, ConfigError> {
        let content = fs::read_to_string("config/validation-rules.yaml")?;
        let config: Self = serde_yaml::from_str(&content)?;
        config.validate()?; // ✅ Validate config
        Ok(config)
    }
}
```

**Esempio SBAGLIATO**:
```rust
// ❌ Hard-coded business rules
const MAX_APPUNTAMENTI_PER_GIORNO: usize = 8; // ❌ Non configurabile
const TIMEOUT_ORE: u64 = 24; // ❌ Hard-coded
```

---

## 5. State Machine

- [ ] **Explicit States**: Enum per stati, non booleani multipli
- [ ] **Transition Validation**: Validazione transizioni in domain
- [ ] **State History**: Opzionale tracking transizioni (audit)
- [ ] **Event Sourcing**: Opzionale per compliance

**Esempio CORRETTO**:
```rust
// ✅ Explicit state enum
#[derive(Debug, Clone, PartialEq)]
pub enum AppuntamentoStato {
    Bozza,
    Proposta,
    InAttesaOperatore,
    Confermato,
    Rifiutato,
    Completato,
    Cancellato,
}

impl AppuntamentoAggregate {
    pub fn conferma(&mut self) -> Result<(), DomainError> {
        match self.stato {
            AppuntamentoStato::InAttesaOperatore => {
                self.stato = AppuntamentoStato::Confermato;
                Ok(())
            }
            _ => Err(DomainError::TransizioneNonValida {
                from: self.stato.clone(),
                to: AppuntamentoStato::Confermato
            }),
        }
    }
}
```

**Esempio SBAGLIATO**:
```rust
// ❌ Boolean hell
pub struct Appuntamento {
    pub is_confermato: bool,
    pub is_rifiutato: bool,
    pub is_cancellato: bool,
    pub is_completato: bool,
    // ❌ Stati ambigui: cosa significa is_confermato=true e is_rifiutato=true?
}
```

---

## 6. Error Handling Strategy

- [ ] **Domain Errors**: Business errors in domain layer
- [ ] **Infrastructure Errors**: DB/HTTP errors wrappati in service
- [ ] **User-Facing Errors**: Mappati a messaggi friendly in controller
- [ ] **Logging**: Trace infra errors, log domain errors critici

**Error Hierarchy**:
```
DomainError (business logic)
     ↑
ServiceError (wraps domain + infra)
     ↑
ControllerError (user-facing messages)
```

---

## 7. Testing Strategy

- [ ] **Test Pyramid**: Molti unit (domain), alcuni integration (service), pochi E2E
- [ ] **Domain Tests**: 100% coverage (no mocks, puri)
- [ ] **Service Tests**: In-memory DB (SQLite `:memory:`)
- [ ] **E2E Tests**: Tauri WebDriver (critical paths only)

**Coverage Target**:
- Domain Layer: **100%**
- Service Layer: **80%+**
- Controller Layer: **60%+** (integration tests)
- UI Layer: **40%+** (critical user flows)

---

## 8. Performance Requirements

- [ ] **Response Time**: API calls < 100ms (p95)
- [ ] **UI Rendering**: First paint < 500ms
- [ ] **Database**: Indexes su campi filtrati frequentemente
- [ ] **Pagination**: Liste > 50 items con offset/limit
- [ ] **Caching**: In-memory cache per dati read-heavy (festività, orari)

**Performance Budget**:
```yaml
api_response_time_p95: 100ms
ui_first_paint: 500ms
db_query_slow_threshold: 50ms
max_memory_usage: 150MB
```

---

## 9. Security Checklist

- [ ] **Input Validation**: TUTTE le input user validate
- [ ] **SQL Injection**: Zero query string interpolation
- [ ] **XSS**: React auto-escape (no `dangerouslySetInnerHTML`)
- [ ] **File Upload**: Valida mime type e dimensione
- [ ] **Secrets**: NO secrets in git (usa `.env`)

**OWASP Top 10 Coverage**:
- ✅ SQL Injection: Parametrized queries
- ✅ XSS: React auto-escape
- ✅ Broken Auth: (N/A per desktop single-user)
- ✅ Sensitive Data: NO log PII
- ✅ Security Misconfiguration: Config validation

---

## 10. Documentation Standards

- [ ] **ADR**: Decisioni architetturali in `docs/adr/ADR-NNN-nome.md`
- [ ] **Workflow Diagrams**: Mermaid per state machine e flow
- [ ] **API Docs**: Rustdoc per funzioni pubbliche
- [ ] **README**: Quick start per nuovi dev

**ADR Template**:
```markdown
# ADR-NNN: Titolo Decisione

**Status**: Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD

## Context
Problema da risolvere

## Decision
Soluzione scelta

## Rationale
Perché questa soluzione

## Alternatives Considered
Altre opzioni valutate

## Consequences
Impatto positivo/negativo
```

---

## Checklist Review Architettura

Prima di merge feature branch:

- [ ] ADR creato per decisioni architetturali
- [ ] Workflow diagram aggiornato se cambia flow
- [ ] Layer separation rispettata
- [ ] Domain logic testato al 100%
- [ ] Config externalizzato (no hard-coded)
- [ ] Performance budget rispettato
- [ ] Security checklist completata

---

## Severity Levels

- **CRITICAL** ❌: Layer violation, anemic domain, hard-coded secrets
- **HIGH** ⚠️: Missing ADR, no domain tests, SQL in service
- **MEDIUM** 💡: Missing docs, suboptimal performance
- **LOW** ℹ️: Naming inconsistency, missing comments

**Regola**: CRITICAL blocca feature. HIGH richiede fix prima release.
