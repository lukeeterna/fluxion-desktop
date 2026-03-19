# FLUXION Rust Backend — Full Security & Safety Audit (S99)

**Date**: 2026-03-19
**Scope**: All `.rs` files in `src-tauri/src/` (48 files, ~15,000 LOC)
**Auditor**: Claude Opus 4.6 (enterprise code review skill)
**Overall Grade**: B (82/100)
**Verdict**: APPROVE_WITH_SUGGESTIONS

---

## Dimension Scores

| Dimension | Grade | Issues | Weight |
|-----------|-------|--------|--------|
| Security | B (83) | 2 HIGH, 3 MEDIUM | 20% |
| Error Handling | B (85) | 1 HIGH, 2 MEDIUM | 15% |
| Architecture | A (92) | 0 | 12% |
| Performance | B (80) | 2 MEDIUM | 12% |
| Type Safety | A (95) | 0 | 10% |
| Testing | B (82) | 1 MEDIUM | 10% |
| Maintainability | C (72) | 2 MEDIUM | 8% |
| API Design | A (90) | 0 | 5% |
| Database | B (80) | 2 MEDIUM | 4% |
| Concurrency | B (85) | 1 MEDIUM | 2% |
| Accessibility | N/A | - | 1% |
| i18n | N/A | - | 1% |

---

## CRITICAL (must fix)

None found.

---

## HIGH (should fix)

### H1. [Security] `http_bridge.rs:1349-1362` — Groq API key exposed via HTTP endpoint

The `/api/verticale/config` endpoint returns `groq_api_key` in the JSON response body. This endpoint is served on `127.0.0.1:3001` and is intended for the Python voice agent, but it exposes the API key to any local process.

```rust
"groq_api_key": groq_api_key
```

**Risk**: Any local process or malicious browser extension can read the Groq API key by calling `http://127.0.0.1:3001/api/verticale/config`.

**Fix**: Remove `groq_api_key` from the HTTP response. The voice agent already reads it from the environment variable `GROQ_API_KEY` (set in `voice_pipeline.rs`). If the bridge must provide it, add a separate authenticated endpoint or use an IPC mechanism.

---

### H2. [Security] `http_bridge.rs:1835-1843` — SMTP password exposed via HTTP endpoint

The `/api/settings/smtp` endpoint returns `smtp_password` in plaintext in the JSON response.

```rust
"smtp_password": smtp_password,
```

**Risk**: Same as H1 -- any local process can read SMTP credentials.

**Fix**: Never return passwords via HTTP endpoints. If the voice agent needs SMTP access, provide a token-based mechanism or use the Tauri IPC channel instead.

---

### H3. [Security] `http_bridge.rs:269-282` — DOM selector injection via CSS selector

The `handle_dom_content` handler injects a user-supplied CSS selector directly into a JavaScript `format!()` string without sanitization:

```rust
let js = if let Some(sel) = selector {
    format!(
        r#"
        (function() {{
            const el = document.querySelector('{}');
            ...
        }})()
        "#,
        sel, sel
    )
};
```

**Risk**: A malicious caller can inject arbitrary JS via the selector string (e.g., `'); alert('xss`). Since this is `#[cfg(debug_assertions)]` only and localhost-bound, risk is LOW in production but HIGH in development.

**Fix**: Escape single quotes and backslashes in the selector, or pass it via `JSON.parse()` of a properly escaped JSON string.

---

### H4. [Error Handling] `commands/support.rs:414-417` — `VACUUM INTO` with string interpolation

```rust
sqlx::query(&format!(
    "VACUUM INTO '{}'",
    backup_path_str.replace('\'', "''")
))
```

While the path is internally generated (not user-supplied from IPC directly), the `backup_path_str` comes from `app_data_dir()` which is OS-controlled. The single-quote escaping is a partial mitigation, but `VACUUM INTO` does not support parameterized queries in SQLite. This is an acceptable limitation but should be documented.

**Risk**: If `app_data_dir()` path contains unusual characters, backup could fail or write to unexpected location.

**Fix**: Validate the backup path contains only expected characters before interpolating. Add a comment acknowledging this is a known SQLite limitation (VACUUM INTO cannot use bind parameters).

---

### H5. [Security] `commands/voice_pipeline.rs:112-115` — `unwrap()` on `groq_key` after None check

```rust
let child = try_start_sidecar(&app, groq_key.as_deref().unwrap())
    .or_else(|sidecar_err| {
        try_start_python(voice_agent_dir.as_deref(), groq_key.as_deref().unwrap())
    })
```

Although there is a None check at line 105-108 that returns Err early, a race condition or code refactoring could remove that guard. The `unwrap()` calls are technically safe due to the early return, but fragile.

**Fix**: Use `groq_key.as_deref().ok_or("GROQ_API_KEY not found")?` instead of `.unwrap()` for defensive coding.

---

## MEDIUM (fix if possible)

### M1. [Security] `http_bridge.rs:454-476` — Text injection in type-text handler

The `handle_type_text` handler escapes `\`, `'`, and `\n` but not `"` or `${}` template literal syntax. While the bridge is debug-only and localhost-bound, the escaping is incomplete.

**File**: `http_bridge.rs:454-476`
**Fix**: Use `serde_json::to_string()` to safely serialize the text value, then inject the JSON string.

---

### M2. [Database] `commands/clienti.rs:117-122` — `SELECT *` usage

```rust
SELECT * FROM clienti WHERE deleted_at IS NULL
```

This pattern is used extensively across 40+ queries in `clienti.rs`, `fatture.rs`, `operatori.rs`, `cassa.rs`, `orari.rs`, `media.rs`, `voice_calls.rs`, `schede_cliente.rs`, and `servizi.rs`.

**Risk**: Schema changes silently add columns to results, increasing memory usage and risking deserialization failures if struct and table diverge.

**Files affected**: `clienti.rs`, `appuntamenti.rs`, `fatture.rs`, `operatori.rs`, `cassa.rs`, `orari.rs`, `media.rs`, `voice_calls.rs`, `schede_cliente.rs`, `servizi.rs`
**Fix**: Replace `SELECT *` with explicit column lists. Since sqlx `FromRow` handles this at compile time, this is LOW urgency but violates the project's own CLAUDE.md rule ("No SELECT * -- specify columns").

---

### M3. [Error Handling] `commands/fatture.rs:700-703` — `unwrap()` in production code

```rust
fn generate_id() -> String {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    format!("{:032x}", now)
}
```

`duration_since(UNIX_EPOCH)` can only fail if the system clock is before 1970, which is effectively impossible. This is a **safe unwrap** but should use `expect()` with a descriptive message for clarity.

**Fix**: `.expect("system clock before UNIX epoch")` or use `unwrap_or_default()`.

---

### M4. [Maintainability] `lib.rs:167-1028` — Massive migration runner with duplicated code

The `init_database` function is 860+ lines of nearly identical migration-running code. Each migration block (001-034) is copy-pasted with only the migration file path and label changed.

**Fix**: Refactor into a loop over a migration list:
```rust
let migrations = vec![
    ("001", include_str!("../migrations/001_init.sql")),
    ("002", include_str!("../migrations/002_whatsapp_templates.sql")),
    // ...
];
for (label, sql) in migrations {
    run_migration(&pool, label, sql).await?;
}
```

Note: The `run_migration` helper already exists (line 89) but is only used for some migrations. All 34 migrations should use it.

---

### M5. [Error Handling] `commands/loyalty.rs:1197` — `unwrap()` on JSON serialization

```rust
file.write_all(serde_json::to_string_pretty(&queue).unwrap().as_bytes())
```

**Risk**: If the `queue` data contains types that can't be serialized (unlikely with serde_json::Value, but still), this panics.

**File**: `commands/loyalty.rs:1197`, `commands/whatsapp.rs:280`, `commands/whatsapp.rs:362`, `commands/whatsapp.rs:410`
**Fix**: Use `.map_err(|e| e.to_string())?` instead of `.unwrap()`.

---

### M6. [Performance] `commands/faq_template.rs:187,577` — `unwrap()` on `partial_cmp` for f64 sorting

```rust
results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
```

**Risk**: If `score` is `NaN`, `partial_cmp` returns `None` and `unwrap()` panics.

**Fix**: Use `.unwrap_or(std::cmp::Ordering::Equal)` to handle NaN gracefully.

---

### M7. [Concurrency] `commands/voice_pipeline.rs:557` — `unwrap_or_else` on poisoned Mutex

```rust
let guard = VOICE_PROCESS.lock().unwrap_or_else(|e| e.into_inner());
```

This recovers from a poisoned Mutex by extracting the inner value, which is acceptable for a non-critical self-healing background task. However, the pattern should be documented as intentional.

**Fix**: Add a comment explaining the intentional poison recovery.

---

### M8. [Security] `encryption.rs:25` — Hardcoded PBKDF2 salt

```rust
const DEFAULT_SALT: &[u8] = b"FLUXION_GDPR_SALT_v1";
```

A static salt means all installations derive the same key from the same password. The salt should be unique per installation.

**Risk**: If two installations use the same master password, they produce the same derived key. An attacker who compromises one installation's key can decrypt data on any other installation with the same password.

**Fix**: Generate a random salt at first initialization and store it alongside the encrypted data or in a separate config file. The `device_id` parameter partially mitigates this (line 37), but a proper random salt is the standard approach.

---

### M9. [Security] `commands/settings.rs:22-23` — Placeholder OAuth credentials in source

```rust
const GOOGLE_CLIENT_ID: &str = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com";
const GOOGLE_CLIENT_SECRET: &str = "YOUR_GOOGLE_CLIENT_SECRET";
```

These are placeholder values, which is correct. However, when real values are substituted, they will be compiled into the binary. For desktop OAuth (installed apps), Google considers the client_secret non-secret per their documentation, so this is acceptable per Google's guidelines. The comment at line 18-19 correctly documents this.

**Fix**: None needed. The comment is adequate.

---

### M10. [Database] `commands/orari.rs:372` — `unwrap()` on `orari.last()`

```rust
orari.last().unwrap().ora_fine
```

**Risk**: If `orari` is empty, this panics. There is a guard earlier in the function checking `orari.is_empty()`, but if code is refactored, the guard could be removed.

**Fix**: Use `orari.last().map(|o| &o.ora_fine).ok_or("No orari configured")?`.

---

### M11. [Performance] `http_bridge.rs:1319-1365` — N+1 query pattern in verticale_config

The `handle_verticale_config` handler makes 7 sequential database queries (one for each setting). These should be batched into a single query.

**Fix**:
```sql
SELECT chiave, valore FROM impostazioni
WHERE chiave IN ('nome_attivita', 'orario_apertura', 'orario_chiusura', ...)
```

---

## LOW / Suggestions

### L1. [Maintainability] `lib.rs:1480` — Generic `expect()` message on app startup

```rust
.expect("error while running tauri application");
```

This is the only `expect()` in production code. It's acceptable at the top-level app runner since recovery is impossible. Consider a more descriptive message.

---

### L2. [Database] Multiple `SELECT *` queries should specify columns

Per CLAUDE.md rule "No SELECT * -- specify columns", approximately 60 queries use `SELECT *`. While sqlx compile-time checking mitigates runtime risks, explicit column lists improve maintainability and prevent future schema drift issues.

**Scope**: All command files listed in M2.

---

### L3. [Security] `commands/settings.rs:470` — Opening browser with `std::process::Command::new("open")`

```rust
std::process::Command::new("open")
    .arg(&auth_url)
    .spawn()
```

This is macOS-specific. On Windows, this would fail silently. Consider using `tauri_plugin_opener::openUrl()` for cross-platform support.

---

### L4. [Maintainability] Test code uses `unwrap()` extensively

All `unwrap()` calls found in test modules (`#[cfg(test)]`) are acceptable and expected. They were verified to only exist in test contexts for the domain, service, and repository layers.

---

### L5. [Security] HTTP bridge binds to `127.0.0.1:3001` correctly

The HTTP bridge correctly binds to localhost only (line 149 of `http_bridge.rs`), preventing external access. CORS is also restricted to localhost origins. This is good.

---

### L6. [Security] `commands/media.rs:352` — Path traversal prevention is adequate

```rust
let clean = relative_path.replace("..", "").replace('\\', "/");
let abs_path = app_data.join(&clean);
if !abs_path.starts_with(&app_data) { ... }
```

The `starts_with` check is the correct defense. The `..` replacement is an extra layer. Adequate.

---

### L7. [Security] `commands/support.rs:553` — Backup delete path traversal check is adequate

```rust
if !backup_path.starts_with(&backup_dir) {
    return Err("Percorso non valido".to_string());
}
```

Correct path traversal prevention.

---

## Positive Highlights

1. **Parameterized queries everywhere**: All SQL queries use `sqlx::query().bind()` parameterized queries. Zero SQL injection via string interpolation in user-facing commands. The only `format!()` in SQL is in `VACUUM INTO` (which doesn't support bind params) and in `audit_repository.rs:316` (which builds WHERE clauses from internal enums with bind params for values).

2. **Comprehensive audit logging**: The GDPR audit system (`audit.rs`, `audit_service.rs`, `audit_repository.rs`) is well-designed with proper separation of concerns (Command -> Service -> Repository).

3. **DDD architecture in appuntamenti**: The `appuntamenti_ddd.rs` + `domain/appuntamento_aggregate.rs` + service layer demonstrates solid domain-driven design with proper state machine transitions.

4. **Self-healing voice pipeline**: The voice pipeline has a proper health check + auto-restart mechanism with max attempt limits and poisoned mutex recovery.

5. **WAL mode + performance PRAGMAs**: Database initialization correctly sets WAL mode, `synchronous=NORMAL`, `cache_size=-32000`, and `busy_timeout=30000`. This is the gold standard for SQLite in a desktop application.

6. **Ed25519 offline license verification**: The license system uses proper Ed25519 signature verification with hardware fingerprinting. No network dependency for license checks.

7. **Soft deletes everywhere**: All entity deletions use soft delete patterns (`deleted_at` timestamps), preserving data integrity.

8. **Input validation on appointments**: Business hours, holiday checks, conflict detection, and past-date validation are all properly implemented in `appuntamenti.rs`.

9. **Path traversal prevention**: Both `media.rs` and `support.rs` properly validate file paths against directory boundaries using `starts_with()`.

10. **Debug-only features gated**: MCP commands and HTTP bridge are properly gated behind `#[cfg(debug_assertions)]` and `#[cfg(feature = "mcp")]`.

---

## Summary of Findings by Severity

| Severity | Count | Merge Impact |
|----------|-------|-------------|
| CRITICAL | 0 | -- |
| HIGH | 5 | Should fix (H1, H2 are most important) |
| MEDIUM | 11 | Fix if possible |
| LOW | 7 | Nice to have |

### Priority Action Items

1. **H1 + H2**: Remove API keys and passwords from HTTP bridge responses (security)
2. **H5**: Replace `.unwrap()` with `.ok_or()?` in voice pipeline (robustness)
3. **M4**: Refactor migration runner into loop (maintainability, 860 lines of duplication)
4. **M5 + M6**: Replace remaining `.unwrap()` calls in production code with proper error handling
5. **M8**: Generate random salt per installation for GDPR encryption
