# 🤖 Tauri Plugin Automation Integration (Optional)

## Overview

For E2E testing with WebdriverIO + tauri-driver, the `tauri-plugin-automation` is **optional** in most cases. The standalone `tauri-driver` binary works without it.

However, if you want **programmatic control** over automation from within your Tauri app, you can integrate the plugin.

---

## When to Use the Plugin

Use `tauri-plugin-automation` if you need:

- **Custom automation APIs** exposed to tests
- **Test hooks** within the app (e.g., reset database, seed data)
- **Programmatic control** of WebDriver sessions from Rust

For **standard E2E testing** (what we've implemented), the standalone `tauri-driver` is sufficient.

---

## Integration Steps (If Needed)

### 1. Add Dependency to `Cargo.toml`

```toml
# src-tauri/Cargo.toml

[dependencies]
# ... existing dependencies ...
tauri-plugin-automation = { version = "0.1", optional = true }

[features]
default = ["custom-protocol"]
# Add automation feature for E2E testing
e2e = ["tauri-plugin-automation"]
```

### 2. Register Plugin in `main.rs`

```rust
// src-tauri/src/main.rs

fn main() {
    tauri::Builder::default()
        // ... existing plugins ...
        #[cfg(feature = "e2e")]
        .plugin(tauri_plugin_automation::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 3. Build with E2E Feature

```bash
# Build with automation plugin enabled
cargo build --release --features e2e

# For E2E tests
npm run tauri build -- --features e2e
```

### 4. Add Test-Specific Commands (Optional)

```rust
// src-tauri/src/commands/test_helpers.rs

#[cfg(feature = "e2e")]
#[tauri::command]
pub async fn reset_test_database(pool: State<'_, SqlitePool>) -> Result<(), String> {
    // Delete all test data
    sqlx::query("DELETE FROM appuntamenti WHERE note LIKE '%E2E Test%'")
        .execute(pool.inner())
        .await
        .map_err(|e| e.to_string())?;

    sqlx::query("DELETE FROM clienti WHERE email LIKE '%@test.fluxion.local'")
        .execute(pool.inner())
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}

#[cfg(feature = "e2e")]
#[tauri::command]
pub async fn seed_test_data(pool: State<'_, SqlitePool>) -> Result<(), String> {
    // Insert test data
    // ...
    Ok(())
}
```

### 5. Expose to TypeScript

```typescript
// src/utils/test-helpers.ts

import { invoke } from '@tauri-apps/api/core';

export async function resetTestDatabase(): Promise<void> {
  if (process.env.NODE_ENV !== 'production') {
    await invoke('reset_test_database');
  }
}

export async function seedTestData(): Promise<void> {
  if (process.env.NODE_ENV !== 'production') {
    await invoke('seed_test_data');
  }
}
```

### 6. Use in E2E Tests

```typescript
// e2e/utils/test-helpers.ts

import { invoke } from '@tauri-apps/api/core';

export async function cleanTestData(): Promise<void> {
  await invoke('reset_test_database');
}

export async function seedTestData(): Promise<void> {
  await invoke('seed_test_data');
}
```

---

## Current Setup (No Plugin Needed)

Our E2E tests use **standalone `tauri-driver`** which doesn't require the plugin:

```bash
# tauri-driver runs independently
~/.cargo/bin/tauri-driver

# It launches your app and proxies WebDriver commands
# No code changes needed in your Tauri app
```

**Advantages**:
- ✅ Simpler setup
- ✅ No build-time features needed
- ✅ Works with production builds
- ✅ No app modifications required

**Disadvantages**:
- ❌ No programmatic cleanup/seeding from tests
- ❌ Can't call custom Tauri commands during automation

---

## Recommendation

**For FLUXION**: Stick with standalone `tauri-driver` for now.

**Add plugin later** if you need:
- Database cleanup between tests
- Test data seeding
- Custom automation hooks

---

## Troubleshooting

### Plugin Not Loading

```bash
# Ensure you built with the feature flag
cargo build --release --features e2e

# Check if feature is enabled
cargo tree --features e2e
```

### Commands Not Available

```bash
# Check if commands are registered
# Look for "reset_test_database" in logs
```

---

## References

- [Tauri Plugin System](https://tauri.app/v1/guides/features/plugin)
- [CrabNebula Tauri Driver](https://github.com/crabnebula-dev/tauri-driver)
- [WebdriverIO Tauri Docs](https://webdriver.io/docs/api/tauri)

---

**Note**: This integration is **optional** and **not required** for the current E2E test setup to work.
