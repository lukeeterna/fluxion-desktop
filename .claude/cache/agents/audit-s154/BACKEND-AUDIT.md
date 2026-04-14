# FLUXION Backend Audit Report — S154

**Date**: 2026-04-14
**Scope**: `src-tauri/src/` — All Rust backend code
**Auditor**: backend-architect agent (Opus 4.6)
**Files analyzed**: 47 `.rs` files across commands/, domain/, services/, infra/

---

## Executive Summary

The codebase is in good shape for a v1.0 desktop app. The domain layer (DDD aggregates, audit) is well-architected. The license system is cryptographically sound. The main issues are cosmetic unwrap()s in production paths (LOW/MEDIUM severity) and blocking filesystem I/O inside async command handlers (MEDIUM).

**Launch-blocking issues: 0**
**Should-fix before launch: 5**
**Nice-to-have improvements: 12**

---

## 1. unwrap() IN PRODUCTION PATHS

### Methodology
Searched all 47 `.rs` files. Excluded anything inside `#[cfg(test)]` blocks. The following files have `#[cfg(test)]` boundaries:
- `encryption.rs:180`, `audit_service.rs:562`, `festivita_service.rs:166`, `appuntamento_service.rs:191`, `validation_service.rs:211`, `audit_repository.rs:571`, `rag.rs:464`, `analytics.rs:656`, `appuntamento_aggregate.rs:445`, `appuntamento_repo.rs:392`, `errors.rs:175`, `audit.rs:437`

All unwrap() calls within those `#[cfg(test)]` modules are acceptable and excluded from findings.

### PRODUCTION unwrap() Findings

| File:Line | Severity | Description | Fix |
|-----------|----------|-------------|-----|
| `commands/whatsapp.rs:280` | **MEDIUM** | `serde_json::to_string_pretty(&queue).unwrap()` — serializing a `Vec<serde_json::Value>` that was just constructed. Theoretically infallible but bad practice. | Replace with `.map_err(\|e\| format!("JSON serialize error: {e}"))?` |
| `commands/whatsapp.rs:362` | **MEDIUM** | `serde_json::to_string_pretty(&default).unwrap()` — serializing `WhatsAppConfig::default()`. Same issue. | `.map_err(...)? ` |
| `commands/whatsapp.rs:410` | **MEDIUM** | `serde_json::to_string_pretty(&current).unwrap()` — serializing updated config. | `.map_err(...)?` |
| `commands/loyalty.rs:1197` | **MEDIUM** | `serde_json::to_string_pretty(&queue).unwrap()` — serializing message queue. | `.map_err(...)?` |
| `commands/fatture.rs:701` | **MEDIUM** | `SystemTime::now().duration_since(UNIX_EPOCH).unwrap()` — This will panic if system clock is before 1970 (extremely unlikely but not impossible on misconfigured machines). | Replace with `.unwrap_or_default()` or `.map_err()?` |
| `commands/faq_template.rs:187` | **LOW** | `b.score.partial_cmp(&a.score).unwrap()` — score is `f64`. If NaN, this panics. | Use `.unwrap_or(std::cmp::Ordering::Equal)` |
| `commands/faq_template.rs:577` | **LOW** | Same NaN-unsafe `partial_cmp().unwrap()` | Same fix |
| `commands/rag.rs:316` | **LOW** | `strip_prefix("faq_").unwrap()` — guarded by `starts_with("faq_")` on line 313. Safe but not idiomatic. | Use `if let Some(cat) = name.strip_prefix(...)` chain |
| `commands/rag.rs:318` | **LOW** | `strip_suffix(".md").unwrap()` — guarded by `ends_with(".md")`. Safe. | Same |
| `commands/rag.rs:332` | **LOW** | Same pattern in dev path branch | Same |
| `commands/rag.rs:334` | **LOW** | Same pattern in dev path branch | Same |
| `commands/orari.rs:372` | **LOW** | `orari.last().unwrap()` — guarded by `orari.is_empty()` check at line 339. Safe. | Could use `orari.last().unwrap_or(&prima_fascia)` for safety |
| `services/festivita_service.rs:67` | **LOW** | `date.and_hms_opt(0,0,0).unwrap()` — `and_hms_opt(0,0,0)` on a valid NaiveDate is always Some. Theoretically safe. | Could use `.expect("midnight is valid")` or handle |

### Verdict: **PASS with 5 MEDIUM findings**

All MEDIUM findings are `serde_json::to_string_pretty().unwrap()` on types that are trivially serializable. They will never panic in practice, but they violate the zero-unwrap-in-production rule. The fatture.rs `SystemTime` unwrap is the most real risk (system clock issues).

---

## 2. IPC COMMAND ERROR HANDLING

### Methodology
Searched all `#[tauri::command]` handlers. Verified return types and error handling patterns.

### Findings

All command handlers return `Result<T, String>` — consistent pattern. No `panic!()` found anywhere in commands/. No `.expect()` calls in commands/.

**Sync commands (pub fn instead of pub async fn)**:
- `commands/whatsapp.rs` — 11 sync commands (file I/O only, no DB)
- `commands/rag.rs` — 3 sync commands (load_faqs, list_faq_categories, quick_faq_search)
- `commands/voice.rs` — 2 sync commands (check_piper_installed, get_piper_status)
- `commands/license.rs` — 1 sync command (get_machine_fingerprint)
- `commands/license_ed25519.rs` — 2 sync commands (get_machine_fingerprint_ed25519, get_tier_info_ed25519)
- `commands/support.rs` — 2 sync commands (get_remote_assist_instructions, generate_support_session)
- `commands/remote_assist.rs` — 1 sync command (generate_support_session)
- `commands/mcp.rs` — 2 sync commands (debug only, gated by `#[cfg(debug_assertions)]`)

| File:Line | Severity | Description | Fix |
|-----------|----------|-------------|-----|
| `commands/whatsapp.rs` (11 cmds) | **LOW** | Sync commands doing `std::fs` file I/O. Fine for small config files, but technically blocks the async runtime's thread briefly. | Convert to async with `tokio::fs` if perf matters |
| `commands/rag.rs` (3 cmds) | **LOW** | Sync commands reading FAQ markdown files from disk. Files are small. | Low priority |

### Verdict: **PASS**

All commands use `Result<T, String>` consistently. The sync commands are justified (no DB access, small file I/O). The only risk is brief blocking of the Tauri async runtime on file reads, which is negligible for the file sizes involved.

---

## 3. ASYNC CORRECTNESS

### tokio::spawn Analysis

| File:Line | Handling | Assessment |
|-----------|----------|------------|
| `commands/settings.rs:458` | Spawns OAuth callback handler. Errors are emitted via `app.emit("gmail-oauth-error", ...)`. Result of the spawn is discarded (no `.await`). | **PASS** — fire-and-forget is intentional; errors surface via event |
| `commands/whatsapp.rs:726` | Spawns WA confirmation send. Uses `match` on result with `eprintln!` on error. | **PASS** — fire-and-forget for non-critical WA notification |
| `lib.rs:297` | Spawns auto-backup on startup. Error logged with `eprintln!`. | **PASS** — non-fatal, correctly labeled |
| `lib.rs:321` | Spawns HTTP bridge (debug_assertions only). Error logged. | **PASS** — debug-only |

### Blocking I/O in Async Functions

| File:Line | Severity | Description | Fix |
|-----------|----------|-------------|-----|
| `commands/media.rs:125` | **MEDIUM** | `std::fs::write()` inside `async fn save_media_image` — writes potentially large image files (base64 decoded). Could block tokio worker thread. | Use `tokio::fs::write()` |
| `commands/media.rs:201-203` | **MEDIUM** | Two `std::fs::write()` calls inside `async fn save_media_video` — writes video + thumbnail. | Use `tokio::fs::write()` |
| `commands/media.rs:323` | **LOW** | `std::fs::remove_file()` in `async fn delete_media` | Use `tokio::fs::remove_file()` |
| `commands/media.rs:360` | **LOW** | `std::fs::read()` in `async fn read_media_file` | Use `tokio::fs::read()` |
| `commands/voice_pipeline.rs:799` | **LOW** | `std::fs::read_to_string()` reading `.env` file. Small file. | Low priority |

### std::thread::sleep

No `std::thread::sleep` calls found in production code. Only a comment at `voice_pipeline.rs:136` recommending `tokio::sleep` instead. **PASS**.

### Verdict: **PASS with 2 MEDIUM findings**

The media.rs blocking writes are the most concerning — writing large images/videos via `std::fs::write` in an async handler will block the tokio worker thread. With Tauri's default single-threaded runtime, this could cause brief UI freezes during media upload.

---

## 4. ED25519 LICENSE SYSTEM (B12)

### Public Key

```rust
pub const FLUXION_PUBLIC_KEY_HEX: &str =
    "c61b3c912cf953e06db979e54b72602da9e3e3cea9554e67a2baa246e7e67d39";
```

**Hardcoded in binary**: Yes. This is the correct approach for Ed25519 verification. The public key is meant to be public. The private signing key must remain offline at the vendor.

### Verification Flow Analysis

1. `activate_license_ed25519()` receives JSON with `{license, signature}`
2. Parses `SignedLicense` struct
3. Calls `verify_license_signature()`:
   - Deserializes public key from hex constant
   - Canonicalizes license to JSON via `serde_json::to_string()`
   - Decodes base64 signature
   - Calls `ed25519_dalek::VerifyingKey.verify()` on the canonical JSON bytes
4. Verifies `license.version == "1.0"`
5. Verifies `license.hardware_fingerprint == local_fingerprint`
6. Checks expiry date
7. Saves to SQLite `license_cache`

| Check | Status | Notes |
|-------|--------|-------|
| Signature verification | **PASS** | Standard Ed25519 verify flow |
| Hardware fingerprint lock | **PASS** | SHA-256 of hostname:cpu:memory:os |
| Canonical serialization | **CAUTION** | Uses `serde_json::to_string()` — JSON field ordering depends on struct definition order. This is stable in Rust (serde preserves declaration order), but the signing server MUST use the exact same serialization. |
| Expiry validation | **PASS** | Checked before activation |
| Version check | **PASS** | Rejects unknown versions |

### Binary Modification Risk

| Vector | Risk | Mitigation |
|--------|------|------------|
| Patch public key | **HIGH** | Attacker replaces embedded hex string with their own key, signs their own licenses. No mitigation (standard issue for offline software). | 
| Patch `is_valid` check | **HIGH** | Attacker NOPs out the validity check in the binary. No mitigation for offline desktop apps. |
| Modify SQLite directly | **MEDIUM** | Set `status='active'`, `tier='enterprise'` in `license_cache`. App trusts DB on startup. | 

**Assessment**: The license system is as strong as offline desktop licensing can be. There is no rate limiting on activation attempts (there doesn't need to be — verification is purely local/offline). The real protection is that the private key never leaves the vendor, and cracking Ed25519 is computationally infeasible. Binary patching is the expected attack vector for desktop apps and cannot be prevented without online checks or code signing with anti-tamper (which would add costs).

| File:Line | Severity | Description | Fix |
|-----------|----------|-------------|-----|
| `license_ed25519.rs:669` | **LOW** | `get_machine_fingerprint_ed25519()` is sync (not async). Acceptable since it does CPU-only work (no I/O). | No fix needed |
| `license_ed25519.rs:484` | **LOW** | `tier_str.parse::<LicenseTier>().unwrap_or(LicenseTier::Trial)` — gracefully falls back to Trial. | **PASS** — correct defensive code |
| `license_ed25519.rs:541-546` | **LOW** | `unwrap_or_else` and `unwrap_or_default` for features/verticals parsing. | **PASS** — correct defensive defaults |
| N/A | **INFO** | No rate limiting on activation. Not needed for offline system. | N/A |
| N/A | **INFO** | Hardware fingerprint includes total_memory which changes if RAM is upgraded. Customer would need new license. | Document in support FAQ |
| N/A | **MEDIUM** | DB-level bypass: attacker can modify `license_cache` table directly with SQLite editor. | Consider adding HMAC integrity check on cached license data |

### Verdict: **PASS**

The Ed25519 system is well-implemented. The canonical JSON serialization is the one subtle risk — if the signing server ever changes field ordering, existing licenses would fail verification.

---

## 5. DATABASE PATTERNS — SQL INJECTION

### Methodology
Searched for `format!()` containing SQL keywords across all `.rs` files.

### Findings

| File:Line | Severity | Description | Assessment |
|-----------|----------|-------------|------------|
| `infra/repositories/audit_repository.rs:273-284` | **SAFE** | `format!()` builds SQL with `WHERE` clause from `build_query_conditions()`. The conditions are hardcoded strings like `"user_id = ?"`, `"entity_type = ?"`. All actual values are bound via `.bind()`. No user input is interpolated into SQL. | **PASS** |
| `infra/repositories/audit_repository.rs:316` | **SAFE** | Same pattern for COUNT query. | **PASS** |

All other SQL queries in the codebase use `sqlx::query()` / `sqlx::query_as()` with `?` placeholders and `.bind()`. No raw string interpolation of user input into SQL was found.

### Verdict: **PASS**

The audit repository's dynamic query builder is the only place using `format!()` with SQL, and it correctly uses parameterized conditions with `?` placeholders. All values are bound via the type-safe `.bind()` API.

---

## 6. ERROR TYPES

### Analysis

The codebase uses two error strategies:

**1. Domain layer (well-structured)**:
- `domain/errors.rs`: `DomainError` enum with `#[derive(Error)]` (thiserror) — typed errors for business logic
- `domain/repository.rs`: `RepositoryError` enum — typed errors for data access
- `services/festivita_service.rs`: `FestivitaError` enum — typed errors for holiday service

**2. Command layer (stringly-typed)**:
- All `#[tauri::command]` handlers return `Result<T, String>`
- Errors are converted via `.map_err(|e| e.to_string())` or `.map_err(|e| format!("context: {e}"))`
- 535 occurrences of `map_err(` across 29 command files

| Assessment | Severity | Description |
|-----------|----------|-------------|
| Stringly-typed errors at IPC boundary | **INFO** | This is actually correct for Tauri. The IPC serialization requires `Serialize`-able errors, and `String` is the simplest approach. Tauri does not support custom error types over the IPC bridge without additional wrapper types. |
| Inconsistent error context | **LOW** | Some errors use `e.to_string()` (no context) while others use `format!("context: {e}")`. The format style is better. | 
| Domain errors properly typed | **PASS** | The DDD layer uses proper `thiserror` enums. |

### Verdict: **PASS**

The dual strategy (typed errors in domain, String errors at IPC boundary) is the standard Tauri pattern. The domain layer is well-structured with thiserror. The IPC layer would benefit from consistent error context messages, but this is not launch-blocking.

---

## Overall Verdicts

| Category | Verdict | Blockers | Should-Fix |
|----------|---------|----------|------------|
| 1. unwrap() in production | **PASS** | 0 | 5 MEDIUM |
| 2. IPC command error handling | **PASS** | 0 | 0 |
| 3. Async correctness | **PASS** | 0 | 2 MEDIUM |
| 4. Ed25519 licensing | **PASS** | 0 | 1 MEDIUM (DB integrity) |
| 5. SQL injection | **PASS** | 0 | 0 |
| 6. Error types | **PASS** | 0 | 0 |

---

## Recommended Fixes (Priority Order)

### P1 — Should Fix Before Launch (5 items)

1. **media.rs: Use tokio::fs for large writes** (lines 125, 201-203)
   - Images/videos can be MB-sized. `std::fs::write` in async blocks the tokio worker.
   - Fix: `tokio::fs::write(&abs_path, &bytes).await.map_err(...)?`

2. **whatsapp.rs/loyalty.rs: Replace serde_json unwrap()** (lines 280, 362, 410, 1197)
   - Replace `.unwrap()` with `.map_err(|e| format!("JSON error: {e}"))?`
   - 4 occurrences across 2 files

3. **fatture.rs:701: SystemTime unwrap**
   - Replace `.unwrap()` with `.unwrap_or_default()` 

4. **faq_template.rs: NaN-safe float comparison** (lines 187, 577)
   - Replace `.unwrap()` with `.unwrap_or(std::cmp::Ordering::Equal)`

5. **license_ed25519: Document canonical JSON constraint**
   - The signing server MUST produce the same JSON field order as `serde_json::to_string(&FluxionLicense{...})`.
   - Add a comment documenting this dependency.

### P2 — Nice to Have (7 items)

6. rag.rs: Use `if let Some` chains instead of `strip_prefix().unwrap()` (4 occurrences)
7. media.rs: Convert remaining `std::fs::remove_file` / `std::fs::read` to tokio::fs (2 occurrences)
8. license_ed25519: Add HMAC integrity check on `license_cache` table to prevent SQLite editing bypass
9. license_ed25519: Document that RAM upgrades change hardware fingerprint
10. orari.rs:372: Use `unwrap_or` instead of `unwrap` even though guarded (defensive coding)
11. festivita_service.rs:67: Use `.expect("midnight is always valid")` instead of bare `.unwrap()`
12. Consistent error context: standardize on `format!("domain: {e}")` pattern across all `.map_err` calls

---

## Architecture Strengths

- **DDD layer**: Proper aggregate pattern with state machine for appuntamenti
- **Migration runner**: Idempotent, well-ordered, includes 34 migrations
- **WAL mode**: Correctly enabled with busy_timeout, foreign_keys ON
- **License system**: Sound Ed25519 verification with hardware fingerprint lock
- **No panic!, no expect()**: Zero instances in command handlers
- **No SQL injection**: All queries use parameterized statements
- **Feature gating**: MCP/debug commands gated with `#[cfg(debug_assertions)]`
- **Proper cleanup**: Window destroy event stops WhatsApp service
- **Error handling**: 535 proper `.map_err()` calls across 29 command files
