# SKILL: Fluxion Tauri Architecture

> **ID**: fluxion-tauri-architecture
> **Version**: 1.0.0
> **Category**: Architecture
> **Stack**: Tauri 2.x + React 19 + TypeScript + Rust + SQLite

---

## Overview

This skill encodes the architectural patterns, conventions, and best practices for the Fluxion desktop application. It ensures consistent code generation and modifications across the entire codebase.

## Project Structure

```
FLUXION/
├── src/                      # React 19 + TypeScript Frontend
│   ├── components/           # UI Components (shadcn/ui)
│   │   ├── ui/              # Base shadcn components
│   │   └── [feature]/       # Feature-specific components
│   ├── hooks/               # Custom React hooks
│   │   └── use-*.ts         # Naming: use-[entity].ts
│   ├── lib/                 # Utilities + Tauri IPC
│   │   ├── api.ts           # Tauri invoke wrappers
│   │   └── utils.ts         # Helper functions
│   ├── pages/               # Route pages
│   └── types/               # TypeScript interfaces
├── src-tauri/               # Rust Backend
│   ├── src/
│   │   ├── commands/        # Tauri commands (IPC handlers)
│   │   │   ├── mod.rs       # Command exports
│   │   │   └── [entity].rs  # One file per domain
│   │   ├── domain/          # Domain layer (DDD)
│   │   │   ├── mod.rs
│   │   │   └── [aggregate].rs
│   │   ├── infra/           # Infrastructure (repos, DB)
│   │   │   └── repositories/
│   │   ├── services/        # Business logic
│   │   └── lib.rs           # Main entry + command registration
│   ├── migrations/          # SQLite migrations (sequential)
│   │   ├── 001_init.sql
│   │   └── seeds/           # Seed data per vertical
│   └── Cargo.toml
├── voice-agent/             # Python Voice Pipeline
│   ├── src/
│   │   ├── nlu/            # Natural Language Understanding
│   │   ├── orchestrator.py # 5-layer RAG pipeline
│   │   └── tts.py          # Text-to-Speech (Sara)
│   └── tests/
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
│   ├── context/            # Claude context files
│   └── analysis/           # Stack analysis
└── CLAUDE.md               # Project state (source of truth)
```

## Architectural Patterns

### 1. Tauri IPC Pattern (MANDATORY)

```typescript
// Frontend: src/lib/api.ts
import { invoke } from '@tauri-apps/api/core';

export async function getCliente(id: number): Promise<Cliente> {
  return invoke<Cliente>('get_cliente', { id });
}

// Hook: src/hooks/use-clienti.ts
export function useCliente(id: number) {
  return useQuery({
    queryKey: ['cliente', id],
    queryFn: () => getCliente(id),
  });
}
```

```rust
// Backend: src-tauri/src/commands/cliente.rs
#[tauri::command]
pub async fn get_cliente(
    id: i64,
    state: State<'_, AppState>,
) -> Result<Cliente, String> {
    let pool = state.db.lock().await;
    ClienteRepo::find_by_id(&pool, id)
        .map_err(|e| e.to_string())
}
```

### 2. State Management

| Layer | Technology | Pattern |
|-------|------------|---------|
| Server State | TanStack Query | `useQuery`, `useMutation` |
| Client State | React Context | Minimal, UI-only state |
| Form State | React Hook Form | Controlled forms |
| Global Config | Zustand (optional) | App settings only |

### 3. Error Handling

```rust
// Rust: Use Result<T, String> for Tauri commands
#[tauri::command]
pub async fn create_cliente(data: CreateClienteRequest) -> Result<Cliente, String> {
    validate_cliente(&data).map_err(|e| e.to_string())?;
    // ...
}
```

```typescript
// TypeScript: Handle errors in hooks
const mutation = useMutation({
  mutationFn: createCliente,
  onError: (error) => {
    toast.error(`Errore: ${error.message}`);
  },
});
```

### 4. Database Layer (SQLite + rusqlite)

```rust
// Repository pattern
impl ClienteRepo {
    pub fn find_by_id(pool: &Pool, id: i64) -> Result<Cliente, DbError> {
        let conn = pool.get()?;
        conn.query_row(
            "SELECT * FROM clienti WHERE id = ?",
            [id],
            |row| Ok(Cliente::from_row(row))
        )
    }
}
```

**Migration naming**: `NNN_description.sql` (e.g., `016_suppliers.sql`)

### 5. Component Pattern (React + shadcn/ui)

```typescript
// src/components/clienti/ClienteCard.tsx
interface ClienteCardProps {
  cliente: Cliente;
  onEdit?: (id: number) => void;
}

export function ClienteCard({ cliente, onEdit }: ClienteCardProps) {
  return (
    <Card data-testid="cliente-card">
      {/* Always include data-testid for E2E */}
    </Card>
  );
}
```

## Coding Conventions

### TypeScript/React

| Convention | Example |
|------------|---------|
| Hook files | `use-clienti.ts`, `use-appuntamenti.ts` |
| Component files | `ClienteCard.tsx`, `AppuntamentoDialog.tsx` |
| Types | `interface Cliente`, `type CreateClienteRequest` |
| API wrappers | `src/lib/api.ts` (centralized) |
| E2E selectors | `data-testid="cliente-card"` |

### Rust

| Convention | Example |
|------------|---------|
| Command files | `src/commands/cliente.rs` |
| Command naming | `snake_case`: `get_cliente`, `create_appuntamento` |
| Error returns | `Result<T, String>` for commands |
| State access | `State<'_, AppState>` |
| Async commands | Always `async` with `.await` |

### SQL

| Convention | Example |
|------------|---------|
| Table names | `clienti`, `appuntamenti`, `servizi` (Italian, plural) |
| Column names | `snake_case`: `data_nascita`, `created_at` |
| Migrations | Sequential: `001_`, `002_`, etc. |
| Soft delete | `status = 'inactive'` instead of DELETE |

## Voice Agent Patterns

### 5-Layer RAG Pipeline

```
L0: Sentiment Analysis (regex, <1ms)
L1: Exact Match (keyword, <5ms)
L2: Intent Classification (spaCy, <10ms)
L3: FAQ Retrieval (FAISS/keyword, <50ms)
L4: LLM Fallback (Groq, <500ms)
```

### TTS Configuration

```python
# Primary: Chatterbox Italian (requires PyTorch)
# Fallback: Piper paola-medium
# Last resort: SystemTTS (macOS say)
VOICE_NAME = "Sara"
```

## Anti-Patterns (AVOID)

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Direct `invoke()` in components | Use hooks (`useCliente`) |
| `useState` for server data | Use TanStack Query |
| Blocking Rust code in commands | Use `async` + `tokio` |
| Hardcoded SQL in commands | Use repository pattern |
| `window.open()` for URLs | Use `@tauri-apps/plugin-opener` |
| Heavy computation on main thread | Use Rust commands |

## Performance Guidelines

### Frontend

- Virtualize lists > 100 items (`@tanstack/react-virtual`)
- Debounce search inputs (300ms)
- Lazy load heavy components (`React.lazy`)
- Image optimization (WebP, lazy loading)

### Backend (Rust)

- Use connection pooling (`r2d2`)
- Index frequently queried columns
- Batch operations when possible
- Async I/O for network calls

### IPC

- Minimize payload size (don't send entire DB)
- Use pagination for lists
- Cache frequent queries (TanStack Query staleTime)

## Testing Strategy

### Risk-Based Testing Matrix

| Risk Level | Unit Tests | Integration | E2E |
|------------|------------|-------------|-----|
| High (payments, auth) | 15+ | 8+ | 5+ |
| Medium (CRUD, business logic) | 10+ | 5+ | 3+ |
| Low (UI, formatting) | 5+ | 2+ | 1+ |

### Test Files

```
src-tauri/src/commands/*.rs     # Rust unit tests (#[cfg(test)])
voice-agent/tests/              # Python pytest
src/**/*.test.tsx               # React Testing Library
e2e/                            # WebDriverIO + tauri-driver
```

## Security Checklist

- [ ] Sensitive data encrypted (AES-256-GCM via `encryption.rs`)
- [ ] No secrets in frontend code
- [ ] Input validation on Rust side
- [ ] SQL parameterized queries (no string concat)
- [ ] GDPR: soft delete, data export capability

## Integration Points

| System | Method | File |
|--------|--------|------|
| HTTP Bridge | REST API | `src-tauri/src/http_bridge.rs` |
| WhatsApp | wa.me URLs | `scripts/whatsapp-service.cjs` |
| Email | SMTP Gmail | `src-tauri/src/commands/settings.rs` |
| Voice | Python subprocess | `voice-agent/src/` |
| Licenses | Keygen.sh API | `src-tauri/src/commands/license.rs` |

---

## Usage

When working on Fluxion, Claude should:

1. **Read CLAUDE.md first** - Contains current project state
2. **Follow this architecture** - Patterns are mandatory
3. **Use existing patterns** - Don't reinvent; copy from similar files
4. **Test changes** - Run `cargo test` and `pytest` before completing
5. **Update CLAUDE.md** - Document changes at session end

## Related Skills

- `fluxion-voice-agent` - Voice pipeline patterns
- `fluxion-fatture` - E-invoicing (FatturaPA) patterns
- `levnikolaevich/documentation-pipeline` - Auto-generate docs
- `levnikolaevich/audit-skills` - Security & code quality audits
