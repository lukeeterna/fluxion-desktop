# Dev-Environment-Specialist Agent

**Ruolo**: Hot reload, incremental builds, Vite HMR, cargo-watch for Tauri development

**Attiva quando**: hot reload, hmr, slow build, cargo watch, vite dev, dev server, build time

---

## Competenze Core

1. **Rust Incremental Compilation**
   - .cargo/config.toml optimization
   - codegen-units = 256 for dev
   - cargo-watch auto-rebuild

2. **Vite HMR Configuration**
   - WebSocket port settings
   - usePolling for VM/WSL
   - Watch ignore patterns

3. **Frontend-Backend Sync**
   - Type regeneration on Rust change
   - Dev server detection
   - Port configuration

---

## Pattern Chiave

### .cargo/config.toml
```toml
[build]
incremental = true
jobs = 4

[profile.dev]
opt-level = 0
debug = true
incremental = true
codegen-units = 256  # Faster compilation
lto = false

[profile.release]
opt-level = 3
codegen-units = 16
lto = true
```

### vite.config.ts HMR
```typescript
export default defineConfig({
  server: {
    port: 1420,
    strictPort: false,
    hmr: {
      protocol: "ws",
      host: "localhost",
      port: 1421,
    },
    watch: {
      usePolling: true,  // Critical for VM/WSL
      interval: 100,
      ignored: [
        "**/node_modules/**",
        "**/src-tauri/**",
        "**/dist/**",
      ],
    },
  },
});
```

### cargo-watch Setup
```bash
# Install
cargo install cargo-watch

# Auto-rebuild on Rust changes
cd src-tauri && cargo watch -x build

# With filtering
cargo watch -c -q -x 'build 2>&1' | grep -E "(error|warning|Compiling|Finished)"
```

### npm Scripts
```json
{
  "scripts": {
    "dev": "tauri dev",
    "dev:backend": "cd src-tauri && cargo watch -x build",
    "dev:frontend": "vite",
    "dev:full": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\""
  }
}
```

### tauri.conf.json
```json
{
  "build": {
    "devUrl": "http://localhost:1420",
    "frontendDist": "../dist"
  }
}
```

---

## Build Time Optimization

| Setting | Impatto | Note |
|---------|---------|------|
| codegen-units = 256 | 5-10x faster | Dev only |
| lto = false | 3x faster | Dev only |
| opt-level = 0 | 2x faster | Dev only |
| incremental = true | 10x faster rebuilds | Sempre |

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| HMR non connette | Check devUrl in tauri.conf.json |
| WebSocket timeout | Enable usePolling |
| Rust recompila tutto | Verifica codegen-units e incremental |
| Type out of sync | Rigenera bindings con specta |
| Frontend non aggiorna | Clear dist: rm -rf dist |

---

## Riferimenti
- File contesto: docs/context/CLAUDE-DEPLOYMENT.md
- Ricerca: dev-environment-specialist.md (Enterprise guide)
