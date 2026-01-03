# Backend Quality Checklist

**Versione**: 1.0
**Ultimo aggiornamento**: 2026-01-03

Checklist obbligatoria per ogni PR/commit backend (Rust/Tauri).

---

## 1. Architettura e Separazione Concerns

- [ ] **Domain Logic**: Business logic SOLO in `src/domain/` (no DB, no HTTP)
- [ ] **Service Layer**: Orchestrazione in `src/services/` (usa repository traits)
- [ ] **Controller Layer**: Tauri commands thin (max 10 righe)
- [ ] **Dependency Injection**: Services ricevono trait, non implementazioni concrete
- [ ] **No Leaky Abstraction**: Domain non conosce SQL/Tauri/Serde

**Esempio CORRETTO**:
```rust
// src/domain/appuntamento_aggregate.rs
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

// src/services/appuntamento_service.rs
pub async fn conferma_appuntamento(&self, id: AppuntamentoId) -> Result<(), ServiceError> {
    let mut app = self.repo.load(id).await?;
    app.conferma()?; // Domain logic
    self.repo.save(&app).await?;
    self.notifier.send_conferma(&app).await?;
    Ok(())
}

// src/commands/appuntamento_commands.rs
#[tauri::command]
pub async fn conferma_appuntamento(id: String, state: State<'_, AppState>) -> Result<AppuntamentoDto, String> {
    state.appuntamento_service
        .conferma_appuntamento(id.parse()?)
        .await
        .map(Into::into)
        .map_err(|e| e.to_string())
}
```

---

## 2. Gestione Errori

- [ ] **Domain Errors**: Enum custom in `src/domain/errors.rs`
- [ ] **Service Errors**: Wrappano domain + infra errors
- [ ] **Controller Errors**: Mappano a `String` per Tauri (o DTO custom error)
- [ ] **No `unwrap()`**: Usa `?` o `expect()` con messaggio descrittivo
- [ ] **No `panic!()` in produzione**: Solo in test
- [ ] **Logging**: `tracing::error!()` per errori critici

**Esempio CORRETTO**:
```rust
// Domain
#[derive(Debug, thiserror::Error)]
pub enum DomainError {
    #[error("Transizione stato non valida: da {from:?} a {to:?}")]
    TransizioneNonValida { from: AppuntamentoStato, to: AppuntamentoStato },

    #[error("Appuntamento nel passato: {data}")]
    AppuntamentoPassato { data: NaiveDateTime },
}

// Service
#[derive(Debug, thiserror::Error)]
pub enum ServiceError {
    #[error("Domain error: {0}")]
    Domain(#[from] DomainError),

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}

// Controller
#[tauri::command]
pub async fn crea_appuntamento(dto: AppuntamentoDto) -> Result<String, String> {
    service.crea(dto)
        .await
        .map(|id| id.to_string())
        .map_err(|e| {
            tracing::error!("Errore creazione appuntamento: {}", e);
            e.to_string() // User-friendly message
        })
}
```

---

## 3. Database e Migrations

- [ ] **Migrations SQLx**: Ogni modifica schema in `migrations/XXX_descrizione.sql`
- [ ] **No SQL raw in service**: Usa repository pattern
- [ ] **Transazioni**: Operazioni multi-step wrappate in transaction
- [ ] **Indexes**: Campi filtrati frequentemente hanno index
- [ ] **Timestamps**: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` su tutte le tabelle
- [ ] **Soft Delete**: `deleted_at TIMESTAMP NULL` invece di `DELETE`

**Esempio CORRETTO**:
```sql
-- migrations/004_appuntamenti_state_machine.sql
CREATE TABLE appuntamenti (
    id TEXT PRIMARY KEY,
    stato TEXT NOT NULL CHECK(stato IN ('Bozza', 'Proposta', 'InAttesaOperatore', 'Confermato', 'Rifiutato', 'Completato', 'Cancellato')),
    cliente_id TEXT NOT NULL,
    operatore_id TEXT NOT NULL,
    data_ora TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);

CREATE INDEX idx_appuntamenti_stato ON appuntamenti(stato);
CREATE INDEX idx_appuntamenti_data_ora ON appuntamenti(data_ora);
```

---

## 4. Testing

- [ ] **Domain Tests**: Unit test puri (no async, no DB)
- [ ] **Service Tests**: Integration test con DB in-memory
- [ ] **Test Coverage**: Minimo 80% per domain layer
- [ ] **Property-Based Testing**: Usa `proptest` per invarianti critici
- [ ] **Test Naming**: `test_<scenario>_<expected_behavior>`

**Esempio CORRETTO**:
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_appuntamento_bozza_conferma_success() {
        let mut app = AppuntamentoAggregate::new_bozza();
        app.proponi().unwrap();
        app.conferma().unwrap();
        assert_eq!(app.stato, AppuntamentoStato::Confermato);
    }

    #[test]
    fn test_appuntamento_bozza_conferma_fails() {
        let mut app = AppuntamentoAggregate::new_bozza();
        let result = app.conferma();
        assert!(result.is_err());
        assert_eq!(app.stato, AppuntamentoStato::Bozza); // Stato non cambia
    }
}
```

---

## 5. Performance

- [ ] **Lazy Loading**: Non caricare relazioni N+1
- [ ] **Pagination**: Query con offset/limit per liste grandi
- [ ] **Async I/O**: Tutte le operazioni DB/HTTP async
- [ ] **Connection Pool**: Usa pool SQLx (no single connection)
- [ ] **Caching**: Cache in-memory per dati read-heavy (festività)

---

## 6. Security

- [ ] **SQL Injection**: ZERO query string interpolation (`format!()`)
- [ ] **Input Validation**: Valida input in controller PRIMA di passare a service
- [ ] **Sensitive Data**: NO log di password/token/PII
- [ ] **File Paths**: Valida path (no `../` traversal)

**Esempio SBAGLIATO**:
```rust
// ❌ SQL INJECTION VULNERABILITY
let query = format!("SELECT * FROM clienti WHERE nome = '{}'", nome);
sqlx::query(&query).fetch_all(&pool).await?;
```

**Esempio CORRETTO**:
```rust
// ✅ Parametrized query
sqlx::query_as::<_, Cliente>("SELECT * FROM clienti WHERE nome = ?")
    .bind(nome)
    .fetch_all(&pool)
    .await?
```

---

## 7. Code Style

- [ ] **Cargo Fmt**: `cargo fmt` passa senza warning
- [ ] **Cargo Clippy**: `cargo clippy -- -D warnings` passa
- [ ] **Naming**: snake_case per variabili/funzioni, PascalCase per tipi
- [ ] **Doc Comments**: `///` per funzioni pubbliche
- [ ] **TODO**: No `TODO` in codice committed (usa issue GitHub)

---

## 8. Tauri Specifico

- [ ] **Commands Async**: Preferire async per I/O
- [ ] **State Management**: Usa `tauri::State` per dependency injection
- [ ] **Events**: Usa `app.emit()` per notifiche real-time
- [ ] **Plugin API**: Usa plugin ufficiali (Dialog, Store, FS)

**Esempio CORRETTO**:
```rust
#[tauri::command]
pub async fn get_appuntamenti(
    state: tauri::State<'_, AppState>,
) -> Result<Vec<AppuntamentoDto>, String> {
    state.appuntamento_service
        .list()
        .await
        .map_err(|e| e.to_string())
}
```

---

## Checklist Pre-Commit

Prima di ogni `git commit`:

```bash
# 1. Format
cargo fmt

# 2. Lint
cargo clippy -- -D warnings

# 3. Test
cargo test

# 4. Build
cargo build --release

# 5. Migration check (se modificato DB)
cd src-tauri && cargo sqlx migrate info
```

---

## Severity Levels

- **CRITICAL** ❌: SQL injection, unwrap in prod, panic, hard-coded secrets
- **HIGH** ⚠️: Missing error handling, N+1 queries, no tests
- **MEDIUM** 💡: No doc comments, clippy warnings, inefficient code
- **LOW** ℹ️: Naming conventions, formatting

**Regola**: CRITICAL blocca merge. HIGH richiede fix in 24h.
