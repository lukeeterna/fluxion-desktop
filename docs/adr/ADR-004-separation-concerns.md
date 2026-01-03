# ADR-004: Architettura DDD-Inspired a Layer Separati

**Status**: Accepted
**Date**: 2026-01-03
**Deciders**: Architecture Team

## Context

L'MVP attuale ha logica business mista in:
- Tauri commands (controller)
- React components (UI)
- Query SQL dirette (no domain layer)

Questo porta a:
- Testing impossibile senza DB
- Duplicazione logica (stessa validazione in Rust e TypeScript)
- Modifica complessa (toccare 4 file per 1 feature)

## Decision

Implementare **architettura a 4 layer** ispirata a Domain-Driven Design:

### Layer 1: Domain (Business Logic Pura)

**Responsabilità**: Definire entità, aggregates, value objects, invarianti di dominio.

**Tecnologia**: Rust structs + traits (zero dipendenze esterne)

**Esempio**:
```rust
// src-tauri/src/domain/appuntamento_aggregate.rs
pub struct AppuntamentoAggregate {
    id: AppuntamentoId,
    stato: AppuntamentoStato,
    // ... fields
}

impl AppuntamentoAggregate {
    pub fn conferma(&mut self) -> Result<(), DomainError> {
        match self.stato {
            AppuntamentoStato::InAttesaOperatore => {
                self.stato = AppuntamentoStato::Confermato;
                Ok(())
            }
            _ => Err(DomainError::TransizioneNonValida)
        }
    }
}
```

**Regole**:
- ❌ NO: Database, HTTP, File I/O
- ✅ SÌ: Business logic, validazioni, state transitions

### Layer 2: Service (Orchestrazione)

**Responsabilità**: Coordinare domain + infra, transaction management.

**Tecnologia**: Rust services con dependency injection

**Esempio**:
```rust
// src-tauri/src/services/appuntamento_service.rs
pub struct AppuntamentoService {
    repo: Box<dyn AppuntamentoRepository>,
    notifier: Box<dyn NotificationService>,
}

impl AppuntamentoService {
    pub async fn conferma_appuntamento(&self, id: AppuntamentoId) -> Result<(), ServiceError> {
        let mut app = self.repo.load(id).await?;
        app.conferma()?; // Domain logic
        self.repo.save(&app).await?;
        self.notifier.send_conferma(&app).await?;
        Ok(())
    }
}
```

**Regole**:
- ✅ Database transactions
- ✅ External API calls
- ❌ Business logic (delegata al domain)

### Layer 3: Controller (Thin API Layer)

**Responsabilità**: Deserializzare input, invocare service, serializzare output.

**Tecnologia**: Tauri commands

**Esempio**:
```rust
// src-tauri/src/commands/appuntamento_commands.rs
#[tauri::command]
pub async fn conferma_appuntamento(
    id: String,
    state: tauri::State<'_, AppState>,
) -> Result<AppuntamentoDto, String> {
    let service = &state.appuntamento_service;
    service.conferma_appuntamento(id.parse()?)
        .await
        .map(|app| app.into())
        .map_err(|e| e.to_string())
}
```

**Regole**:
- ❌ Business logic
- ✅ Input validation (type safety)
- ✅ Error mapping (domain errors → HTTP-like codes)

### Layer 4: UI (Presentazione)

**Responsabilità**: Rendering, user interaction, local state.

**Tecnologia**: React + TanStack Query

**Esempio**:
```typescript
// src/features/appuntamenti/hooks/useConfermaAppuntamento.ts
export function useConfermaAppuntamento() {
  return useMutation({
    mutationFn: (id: string) => invoke('conferma_appuntamento', { id }),
    onSuccess: () => queryClient.invalidateQueries(['appuntamenti']),
  });
}
```

**Regole**:
- ❌ Business logic
- ✅ UI state (modals, forms)
- ✅ Presentation logic (formatting, i18n)

## Data Flow

```
User Input (UI)
     ↓
Tauri Command (Controller) — validation, deserialization
     ↓
Service Layer — orchestration, transactions
     ↓
Domain Layer — business logic, invariants
     ↓
Repository — persistence
     ↓
Database
```

## Rationale

**Vantaggi**:
- **Testabilità**: Domain testabile con unit test puri (no DB)
- **Manutenibilità**: Modifiche localized (business logic solo in domain)
- **Portabilità**: Domain layer riutilizzabile (es. future CLI, API REST)

**Pattern DDD Applicati**:
- Aggregates: `AppuntamentoAggregate` è l'unico entry point per modifiche
- Repositories: Interfaccia traits, impl Postgres nascosta
- Domain Events: `AppuntamentoConfermato` event per notifiche asincrone

**Alternative considerate**:
- Anemic Domain Model: Tutta la logica nei services (antipattern)
- Smart UI: Logica in React (impossibile da testare)

## Consequences

**Positivi**:
- Test coverage: Domain layer testabile al 100% (no mocks)
- Onboarding: Nuovi dev capiscono separation of concerns
- Refactoring: Cambio DB (Postgres → SQLite) tocca solo repository

**Negativi**:
- Più file: 1 feature = 4 file (domain, service, controller, UI)
- Learning curve: Team deve capire DDD basics

## Migration Path da MVP

1. **Fase 1**: Estrarre business logic da commands → domain layer
2. **Fase 2**: Creare service layer per orchestrazione
3. **Fase 3**: Thin commands (solo deserializzazione)
4. **Fase 4**: Refactor UI (no business logic, solo presentazione)

## Testing Strategy

- **Domain Layer**: Unit tests puri (no async, no DB)
- **Service Layer**: Integration tests con DB in-memory
- **Controller Layer**: E2E tests con Tauri test harness
- **UI Layer**: Vitest + React Testing Library
