# 🤖 Tauri Plugin Automation Integration

## Overview

The `tauri-plugin-automation` integration requirements **depend on your platform**:

### ⚠️ **macOS (REQUIRED)**
For E2E testing on macOS using CrabNebula WebDriver, the plugin is **REQUIRED** because:
- Standard tauri-driver lacks WKWebView automation support
- CrabNebula's `test-runner-backend` requires the automation plugin to properly instrument the app
- Without it, the backend cannot inject automation hooks into the WKWebView context

### ✅ **Windows/Linux (Optional)**
On Windows and Linux, the plugin is **optional**:
- Standard tauri-driver works natively
- Plugin only needed for custom test hooks or programmatic control

---

## macOS CrabNebula Requirements

**For macOS E2E testing, you MUST:**

1. ✅ Install `@crabnebula/tauri-driver` and `@crabnebula/test-runner-backend` (via npm)
2. ✅ Set `CN_API_KEY` in `.env.e2e`
3. ✅ Integrate `tauri-plugin-automation` in your Rust app (see steps below)
4. ✅ Build with the plugin enabled

Without the plugin, the test-runner-backend cannot properly communicate with your app on macOS.

---

## When to Use the Plugin

Use `tauri-plugin-automation` if you need:

- **macOS E2E testing** (REQUIRED with CrabNebula)
- **Custom automation APIs** exposed to tests
- **Test hooks** within the app (e.g., reset database, seed data)
- **Programmatic control** of WebDriver sessions from Rust

---

## Integration Steps (REQUIRED for macOS, Optional for Windows/Linux)

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

## Current Setup

### macOS (CrabNebula)

**Plugin is REQUIRED** for macOS E2E testing:

```bash
# npm provides the CrabNebula drivers
node_modules/.bin/tauri-driver
node_modules/.bin/test-runner-backend

# test-runner-backend proxies WebDriver → WKWebView automation
# Requires tauri-plugin-automation integrated in app
```

**Setup Requirements**:
- ✅ Plugin integrated in Rust app (see steps above)
- ✅ CrabNebula API key configured
- ✅ Build with automation feature enabled
- ✅ test-runner-backend running

**Advantages**:
- ✅ Enables E2E testing on macOS (otherwise impossible)
- ✅ Full programmatic control via plugin API
- ✅ Can call custom Tauri commands during automation
- ✅ Database cleanup/seeding available

**Disadvantages**:
- ❌ Requires CrabNebula account and API key
- ❌ More complex setup than Windows/Linux

### Windows/Linux (Standard)

**Plugin is OPTIONAL** on these platforms:

```bash
# Standard tauri-driver works natively
# No plugin required for basic E2E testing
```

**Advantages**:
- ✅ Simpler setup (no plugin needed)
- ✅ No API key required
- ✅ Works with production builds as-is

**Disadvantages**:
- ❌ No programmatic cleanup/seeding (unless you add the plugin)
- ❌ Can't call custom Tauri commands during automation (unless you add the plugin)

---

## Recommendation

### For macOS Development
**YOU MUST integrate the plugin** to run E2E tests. Follow the integration steps above and build with the `e2e` feature.

### For Windows/Linux Development
**Start without the plugin** for simplicity. Add it later if you need:
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
- [CrabNebula Test Runner Backend](https://github.com/crabnebula-dev/test-runner-backend)
- [WebdriverIO Tauri Docs](https://webdriver.io/docs/api/tauri)

---

**Note**:
- **macOS**: Plugin integration is **REQUIRED** for E2E testing (CrabNebula requirement)
- **Windows/Linux**: Plugin integration is **OPTIONAL** (only needed for advanced features)
