# Fluxion Tauri Architecture Skill

## Description
Pattern architetturali per FLUXION - Gestionale desktop con Tauri 2.x + React 19 + Rust + SQLite.

## When to Use
- Quando si crea/modifica codice Rust backend (src-tauri/)
- Quando si crea/modifica componenti React frontend (src/)
- Quando si definiscono comandi IPC Tauri
- Quando si lavora con database SQLite
- Quando si gestisce stato applicazione

## Architecture Patterns

### Stack
- **Desktop**: Tauri 2.x (Rust backend)
- **Frontend**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS 3.4 + shadcn/ui
- **Database**: SQLite (locale, offline-first)
- **State**: React Query + Zustand

### Directory Structure
```
fluxion/
├── src/                      # React frontend
│   ├── components/           # UI components (shadcn/ui)
│   ├── pages/               # Route pages
│   ├── hooks/               # Custom hooks (useCliente, useAppuntamenti)
│   ├── lib/                 # Utilities
│   └── types/               # TypeScript types
├── src-tauri/               # Rust backend
│   ├── src/
│   │   ├── commands/        # Tauri commands (IPC)
│   │   ├── domain/          # Domain models
│   │   ├── repositories/    # DB repositories
│   │   └── services/        # Business logic
│   └── migrations/          # SQLite migrations
└── voice-agent/             # Python voice agent
    ├── src/                 # NLU, TTS, orchestrator
    └── data/                # FAQ, configs
```

### Tauri Command Pattern
```rust
// CORRECT: Async command with proper error handling
#[tauri::command]
pub async fn get_cliente(
    state: tauri::State<'_, AppState>,
    id: i64
) -> Result<Cliente, String> {
    let pool = state.pool.lock().await;
    repository::get_cliente(&pool, id)
        .map_err(|e| e.to_string())
}

// WRONG: Sync command, no error handling
#[tauri::command]
pub fn get_cliente(id: i64) -> Cliente { ... }
```

### Frontend IPC Pattern
```typescript
// CORRECT: Type-safe invoke with error handling
const cliente = await invoke<Cliente>('get_cliente', { id: 123 });

// WRONG: Untyped invoke
const cliente = await invoke('get_cliente', { id: 123 });
```

### State Management
```typescript
// CORRECT: React Query for server state
const { data: clienti } = useQuery({
  queryKey: ['clienti'],
  queryFn: () => invoke<Cliente[]>('list_clienti')
});

// CORRECT: Zustand for UI state
const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen }))
}));
```

### SQLite Patterns
```rust
// CORRECT: Parameterized query
sqlx::query_as!(Cliente, "SELECT * FROM clienti WHERE id = ?", id)

// WRONG: String interpolation (SQL injection)
sqlx::query(&format!("SELECT * FROM clienti WHERE id = {}", id))
```

## Rules
1. SEMPRE usare async/await per comandi Tauri
2. SEMPRE tipizzare invoke<T> nel frontend
3. SEMPRE usare query parametrizzate per SQLite
4. MAI hardcodare credenziali o API keys
5. MAI usare .unwrap() in produzione - usare proper error handling
6. SEMPRE seguire naming convention: snake_case per Rust, camelCase per TS
7. SEMPRE aggiungere data-testid per componenti E2E testabili

## Files to Reference
- `docs/FLUXION-ORCHESTRATOR.md` - Procedure operative
- `docs/FLUXION-DESIGN-BIBLE.md` - Design system
- `src-tauri/src/commands/*.rs` - Existing commands
- `src/hooks/*.ts` - Existing hooks
