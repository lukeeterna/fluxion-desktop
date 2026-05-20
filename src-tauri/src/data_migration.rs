// =============================================================================
// FLUXION - One-shot Data Migration Runners (S251 + S255)
// =============================================================================
//
// Re-encrypts PII rows that were inserted by app builds prior to the at-rest
// AES-256-GCM wiring. Required for GDPR compliance on upgraded installs:
// without these runners the DB would contain a mix of plaintext and
// ciphertext for the sensitive columns of each protected table.
//
// Tables covered:
//   * `clienti`                  — S251 (Cat 3 P0 #2 Step D) — 11 sensitive columns
//   * `operatori`                — S255 (P1)                  — 4 sensitive columns
//   * `suppliers`                — S257 (P2)                  — 5 sensitive columns
//   * `impostazioni_fatturazione` — S260 (P4)                  — 8 sensitive columns
//
// Invariants (per runner):
//   * Idempotent — guarded by a `encryption_migration_state` marker
//     (migration 038). A successful run inserts the marker; a subsequent
//     invocation observes the marker and short-circuits to
//     `already_applied()`.
//   * Crash-safe — backup via `VACUUM INTO` taken BEFORE any UPDATE; mutation
//     happens in 100-row transactions; marker is the LAST write, so a crash
//     mid-batch leaves the marker absent and the next run resumes (detection
//     reads each field with `decrypt_field` — Ok = ciphertext = skip, Err =
//     plaintext = encrypt).
//   * Cold-start safe — `is_encryption_ready()` must be true before this runs
//     (caller in `lib.rs` only invokes after Step C auto-init). On a fresh
//     install with no `license_cache` row the runner returns an Err the
//     caller logs but does NOT propagate as a crash.
//   * Backup filename is `{db}.pre-{MIGRATION_KEY}-bak-{TS}`, so two runners
//     firing within the same second never collide on the target path.
//
// Scope-out (tracked for later sessions):
//   * `fatture.cliente_*` snapshot columns (denormalised at invoice time)
//
// =============================================================================

use chrono::Utc;
use sqlx::{Row, SqlitePool};
use std::path::{Path, PathBuf};

use crate::encryption::{decrypt_field, encrypt_field, is_encryption_ready};

// ── Clienti runner constants ────────────────────────────────────────────────

const MIGRATION_KEY_CLIENTI: &str = "encrypt_clienti_pii_v1";

/// Columns on `clienti` that hold GDPR-sensitive plaintext on legacy installs.
const ENCRYPTABLE_COLUMNS_CLIENTI: &[&str] = &[
    "nome",
    "cognome",
    "telefono",
    "email",
    "codice_fiscale",
    "partita_iva",
    "indirizzo",
    "cap",
    "citta",
    "pec",
    "data_nascita",
];

// ── Operatori runner constants (S255) ───────────────────────────────────────

const MIGRATION_KEY_OPERATORI: &str = "encrypt_operatori_pii_v1";

/// Columns on `operatori` that hold GDPR-sensitive plaintext on legacy installs.
/// Sources: migration 002 (`operatori` table schema). `nome`/`cognome` are
/// NOT NULL TEXT; `email`/`telefono` are nullable TEXT.
const ENCRYPTABLE_COLUMNS_OPERATORI: &[&str] = &["nome", "cognome", "telefono", "email"];

// ── Suppliers runner constants (S257) ───────────────────────────────────────

const MIGRATION_KEY_SUPPLIERS: &str = "encrypt_suppliers_pii_v1";

/// Columns on `suppliers` that hold GDPR-sensitive plaintext on legacy installs.
/// Sources: migration 016 (`suppliers` table schema). Only `nome` is NOT NULL;
/// `email`/`telefono`/`indirizzo`/`partita_iva` are nullable.
///
/// `citta`/`cap` are intentionally excluded: low-cardinality, non-personal
/// (city + postcode alone do not identify a natural person under GDPR Art.4).
/// `status`/`created_at`/`updated_at` are operational metadata.
///
/// Migration 040 DROPs the legacy `UNIQUE(nome)` and `UNIQUE(partita_iva)`
/// constraints before this runner fires; dedupe moves to application layer
/// (`commands/supplier.rs::create_supplier` list-decrypt-compare).
const ENCRYPTABLE_COLUMNS_SUPPLIERS: &[&str] =
    &["nome", "email", "telefono", "indirizzo", "partita_iva"];

// ── Impostazioni fatturazione runner constants (S260) ───────────────────────

const MIGRATION_KEY_IMPOSTAZIONI_FATTURAZIONE: &str = "encrypt_impostazioni_fatturazione_pii_v1";

/// Columns on `impostazioni_fatturazione` that hold GDPR-sensitive plaintext on
/// legacy installs (singleton row, `id = 'default'`).
///
/// Sources: migration 007 (`impostazioni_fatturazione` schema). All 8 columns
/// are TEXT; `denominazione/partita_iva/indirizzo` are NOT NULL with default ''
/// (legacy plaintext blanks → pass-through, empty strings are not encrypted),
/// `codice_fiscale/telefono/email/pec/iban` are nullable.
///
/// PII rationale: P.IVA + C.F. (identità fiscale ditta), IBAN (frode bancaria),
/// indirizzo/telefono/email/pec (contattabilità + linkability), denominazione
/// (ragione sociale = identità diretta della founder/persona giuridica).
///
/// Intentionally excluded:
/// - `cap/comune/provincia/nazione` (low-cardinality address components, non-
///   identificativi per Art.4 GDPR — stesso rationale di S257 suppliers).
/// - `bic/nome_banca` (non-personal, low-sensitivity routing metadata).
/// - `fattura24_api_key/aruba_api_key/openapi_api_key` (provider credentials —
///   coperti da scope SDI provider routing in fatture.rs, NON personal data).
/// - `sdi_provider/regime_fiscale/prefisso_numerazione/aliquota_iva_default/
///   natura_iva_default/ultimo_numero/anno_corrente/created_at/updated_at`
///   (operational metadata, NO personal data).
const ENCRYPTABLE_COLUMNS_IMPOSTAZIONI_FATTURAZIONE: &[&str] = &[
    "denominazione",
    "partita_iva",
    "codice_fiscale",
    "indirizzo",
    "telefono",
    "email",
    "pec",
    "iban",
];

// ── Common batching ─────────────────────────────────────────────────────────

/// Page size for the read+update loop. Each batch is its own transaction so a
/// crash mid-loop loses at most BATCH_SIZE rows of progress — and even those
/// are recovered by the detection heuristic on the next run.
const BATCH_SIZE: i64 = 100;

#[derive(Debug)]
pub struct MigrationReport {
    /// Rows where at least one column was rewritten from plaintext to
    /// ciphertext. A row with N plaintext columns still counts as 1.
    pub encrypted_rows: u64,
    /// Rows where every sensitive column was already ciphertext (or NULL/empty).
    pub skipped_rows: u64,
    /// Path to the pre-migration `VACUUM INTO` snapshot. `None` when the
    /// marker was already present and no work (and no backup) was performed.
    pub backup_path: Option<PathBuf>,
    /// True when the marker row was already present on entry.
    pub already_applied: bool,
}

impl MigrationReport {
    fn already_applied() -> Self {
        Self {
            encrypted_rows: 0,
            skipped_rows: 0,
            backup_path: None,
            already_applied: true,
        }
    }
}

// ── Generic core runner ─────────────────────────────────────────────────────

/// Re-encrypt every plaintext PII row currently in `table`, guarded by an
/// idempotency marker keyed by `migration_key`.
///
/// `table` is interpolated into SELECT/UPDATE templates after being validated
/// against a strict identifier whitelist (caller-controlled constants only —
/// never user input). `columns` likewise — both come from compile-time
/// constants at the call site. SQL injection surface = none.
async fn encrypt_table_pii(
    pool: &SqlitePool,
    db_path: &Path,
    migration_key: &str,
    table: &str,
    columns: &[&'static str],
) -> Result<MigrationReport, String> {
    // ── Pre-flight ────────────────────────────────────────────────────────
    if !is_encryption_ready() {
        return Err(
            "encryption not ready, complete setup wizard first".to_string(),
        );
    }

    // Defence-in-depth identifier whitelist. `table` and `columns` already
    // come from compile-time constants in this module, but the runner accepts
    // them by reference so a future caller bug cannot inject SQL.
    fn is_valid_ident(s: &str) -> bool {
        !s.is_empty()
            && s.chars()
                .all(|c| c.is_ascii_alphanumeric() || c == '_')
    }
    if !is_valid_ident(table) {
        return Err(format!("invalid table identifier: {}", table));
    }
    for c in columns {
        if !is_valid_ident(c) {
            return Err(format!("invalid column identifier: {}", c));
        }
    }

    // ── Idempotency check ─────────────────────────────────────────────────
    let marker: Option<(String,)> = sqlx::query_as(
        "SELECT migration_key FROM encryption_migration_state \
         WHERE migration_key = ?",
    )
    .bind(migration_key)
    .fetch_optional(pool)
    .await
    .map_err(|e| format!("marker lookup failed: {}", e))?;

    if marker.is_some() {
        return Ok(MigrationReport::already_applied());
    }

    // ── Backup via VACUUM INTO ────────────────────────────────────────────
    // Filename embeds the migration_key so concurrent runners (clienti +
    // operatori) firing within the same second never collide.
    let ts = Utc::now().format("%Y%m%d-%H%M%S").to_string();
    let backup_path =
        db_path.with_extension(format!("db.pre-{}-bak-{}", migration_key, ts));

    if backup_path.exists() {
        return Err(format!(
            "backup target already exists: {}",
            backup_path.display()
        ));
    }

    let backup_path_str = backup_path
        .to_str()
        .ok_or_else(|| "backup path is not valid UTF-8".to_string())?;
    let escaped = backup_path_str.replace('\'', "''");
    let vacuum_sql = format!("VACUUM INTO '{}'", escaped);
    sqlx::query(&vacuum_sql)
        .execute(pool)
        .await
        .map_err(|e| format!("VACUUM INTO failed: {}", e))?;

    // ── Re-encryption loop ────────────────────────────────────────────────
    // Page by (id > last_id) ORDER BY id — stable, deterministic on retries.
    // OFFSET is unsafe here because UPDATE may move rows between pages.
    let mut encrypted_rows: u64 = 0;
    let mut skipped_rows: u64 = 0;
    let mut last_id: String = String::new();

    let select_cols = {
        let mut s = String::from("id");
        for c in columns {
            s.push_str(", ");
            s.push_str(c);
        }
        s
    };

    loop {
        let select_sql = if last_id.is_empty() {
            format!(
                "SELECT {} FROM {} ORDER BY id LIMIT {}",
                select_cols, table, BATCH_SIZE
            )
        } else {
            format!(
                "SELECT {} FROM {} WHERE id > ? ORDER BY id LIMIT {}",
                select_cols, table, BATCH_SIZE
            )
        };

        let mut q = sqlx::query(&select_sql);
        if !last_id.is_empty() {
            q = q.bind(&last_id);
        }
        let rows = q
            .fetch_all(pool)
            .await
            .map_err(|e| format!("{} read failed: {}", table, e))?;

        if rows.is_empty() {
            break;
        }

        let mut tx = pool
            .begin()
            .await
            .map_err(|e| format!("tx begin failed: {}", e))?;

        for row in &rows {
            let id: String = row
                .try_get::<String, _>("id")
                .map_err(|e| format!("row.id read failed: {}", e))?;

            // Collect (column, new_ciphertext) pairs for the columns whose
            // current value is plaintext. NULL/empty are left alone.
            let mut updates: Vec<(&'static str, String)> = Vec::new();
            for col in columns {
                let val_opt: Option<String> = row
                    .try_get::<Option<String>, _>(*col)
                    .ok()
                    .flatten();
                let val = match val_opt {
                    Some(s) if !s.is_empty() => s,
                    _ => continue,
                };
                if decrypt_field(&val).is_ok() {
                    continue;
                }
                let ct = encrypt_field(&val)
                    .map_err(|e| format!("encrypt {} for id {}: {}", col, id, e))?;
                updates.push((*col, ct));
            }

            if updates.is_empty() {
                skipped_rows += 1;
            } else {
                let set_clause = updates
                    .iter()
                    .map(|(c, _)| format!("{} = ?", c))
                    .collect::<Vec<_>>()
                    .join(", ");
                let upd_sql = format!("UPDATE {} SET {} WHERE id = ?", table, set_clause);
                let mut q = sqlx::query(&upd_sql);
                for (_, v) in &updates {
                    q = q.bind(v);
                }
                q = q.bind(&id);
                q.execute(&mut *tx)
                    .await
                    .map_err(|e| format!("update id {}: {}", id, e))?;
                encrypted_rows += 1;
            }

            last_id = id;
        }

        tx.commit()
            .await
            .map_err(|e| format!("tx commit failed: {}", e))?;

        if (rows.len() as i64) < BATCH_SIZE {
            break;
        }
    }

    // ── Marker insert (LAST WRITE) ────────────────────────────────────────
    sqlx::query(
        "INSERT INTO encryption_migration_state \
         (migration_key, rows_processed, backup_path) VALUES (?, ?, ?)",
    )
    .bind(migration_key)
    .bind(encrypted_rows as i64)
    .bind(backup_path_str)
    .execute(pool)
    .await
    .map_err(|e| format!("marker insert failed: {}", e))?;

    Ok(MigrationReport {
        encrypted_rows,
        skipped_rows,
        backup_path: Some(backup_path),
        already_applied: false,
    })
}

// ── Public per-table entry points ───────────────────────────────────────────

/// Re-encrypt every plaintext PII row currently in `clienti`.
///
/// Pre-conditions / post-conditions: see module docstring.
pub async fn encrypt_clienti_pii(
    pool: &SqlitePool,
    db_path: &Path,
) -> Result<MigrationReport, String> {
    encrypt_table_pii(
        pool,
        db_path,
        MIGRATION_KEY_CLIENTI,
        "clienti",
        ENCRYPTABLE_COLUMNS_CLIENTI,
    )
    .await
}

/// Re-encrypt every plaintext PII row currently in `operatori` (S255 P1.b).
///
/// Pre-conditions / post-conditions: see module docstring. Must be invoked
/// AFTER `encrypt_clienti_pii` returns Ok (lib.rs wires both in sequence on
/// the encryption-ready branch).
pub async fn encrypt_operatori_pii(
    pool: &SqlitePool,
    db_path: &Path,
) -> Result<MigrationReport, String> {
    encrypt_table_pii(
        pool,
        db_path,
        MIGRATION_KEY_OPERATORI,
        "operatori",
        ENCRYPTABLE_COLUMNS_OPERATORI,
    )
    .await
}

/// Re-encrypt every plaintext PII row currently in `suppliers` (S257 P2).
///
/// Pre-conditions / post-conditions: see module docstring. Must be invoked
/// AFTER migration 040 has dropped UNIQUE(nome)/UNIQUE(partita_iva) — encryption
/// would otherwise break the unique-enforcement semantics. Lib.rs wires this
/// after `encrypt_operatori_pii` on the encryption-ready branch.
pub async fn encrypt_suppliers_pii(
    pool: &SqlitePool,
    db_path: &Path,
) -> Result<MigrationReport, String> {
    encrypt_table_pii(
        pool,
        db_path,
        MIGRATION_KEY_SUPPLIERS,
        "suppliers",
        ENCRYPTABLE_COLUMNS_SUPPLIERS,
    )
    .await
}

/// Re-encrypt every plaintext PII row currently in `impostazioni_fatturazione`
/// (S260 P4).
///
/// Singleton table (`id = 'default'`): in practice the runner processes at most
/// 1 row. The generic runner handles 0-row case correctly (loop exits on empty
/// fetch, marker still inserted to avoid re-evaluation on subsequent boots).
///
/// Pre-conditions / post-conditions: see module docstring. Must be invoked AFTER
/// `encrypt_operatori_pii` returns. No schema migration required (no UNIQUE
/// constraints on PII cols, no views referencing them, no LIKE search). Lib.rs
/// wires this after operatori and BEFORE suppliers on the encryption-ready
/// branch (ordering: clienti → operatori → impostazioni_fatturazione → suppliers).
pub async fn encrypt_impostazioni_fatturazione_pii(
    pool: &SqlitePool,
    db_path: &Path,
) -> Result<MigrationReport, String> {
    encrypt_table_pii(
        pool,
        db_path,
        MIGRATION_KEY_IMPOSTAZIONI_FATTURAZIONE,
        "impostazioni_fatturazione",
        ENCRYPTABLE_COLUMNS_IMPOSTAZIONI_FATTURAZIONE,
    )
    .await
}

// ── Verify-or-repair runner (S272 — BUG-FATT-7 prevention) ──────────────────
//
// Background: in S270 the founder edited `impostazioni_fatturazione` from the
// UI using a binary built *before* the encryption wiring landed. The write
// path bypassed `encrypt_field`, so the row reverted to plaintext even
// though the migration marker (`encrypt_impostazioni_fatturazione_pii_v1`)
// was already present in `encryption_migration_state`. Subsequent decrypt
// calls from the fixed binary threw "invalid base64" → P0 outage until a
// manual MCP re-save re-encrypted the row.
//
// The marker-gated migration runners (`encrypt_*_pii`) deliberately do NOT
// re-scan once the marker is present, so they can never recover from this
// class of regression. This function is the safety net: it runs on every
// boot AFTER the migration runners and walks every PII column on tables
// whose marker is present. For each value, `decrypt_field` is the oracle:
// Ok ⇒ ciphertext, skip. Err ⇒ plaintext residual, encrypt and UPDATE in
// place. Matches the detection heuristic used inside `encrypt_table_pii`
// exactly, so the two stages stay coherent.
//
// Tables without a marker are skipped: pre-migration plaintext is the
// migration runner's responsibility, not repair's.

/// Per-table configuration tying a marker migration key to its sentinel PII
/// columns. Compile-time constants only — no SQL injection surface.
struct RepairTarget {
    table: &'static str,
    marker: &'static str,
    columns: &'static [&'static str],
}

const REPAIR_TARGETS: &[RepairTarget] = &[
    RepairTarget {
        table: "clienti",
        marker: MIGRATION_KEY_CLIENTI,
        columns: ENCRYPTABLE_COLUMNS_CLIENTI,
    },
    RepairTarget {
        table: "operatori",
        marker: MIGRATION_KEY_OPERATORI,
        columns: ENCRYPTABLE_COLUMNS_OPERATORI,
    },
    RepairTarget {
        table: "suppliers",
        marker: MIGRATION_KEY_SUPPLIERS,
        columns: ENCRYPTABLE_COLUMNS_SUPPLIERS,
    },
    RepairTarget {
        table: "impostazioni_fatturazione",
        marker: MIGRATION_KEY_IMPOSTAZIONI_FATTURAZIONE,
        columns: ENCRYPTABLE_COLUMNS_IMPOSTAZIONI_FATTURAZIONE,
    },
];

#[derive(Debug, Default)]
pub struct RepairReport {
    /// Total rows inspected across every table whose marker is present.
    pub total_scanned: u64,
    /// Rows where at least one PII column was repaired (plaintext → ciphertext).
    pub plaintext_residuals_repaired: u64,
    /// Per-table breakdown for diagnostics.
    pub per_table: Vec<TableRepair>,
}

#[derive(Debug)]
pub struct TableRepair {
    pub table: &'static str,
    /// True if the migration marker for this table was present (i.e. the table
    /// was actually scanned). False ⇒ migration runner has not yet run, the
    /// repair phase deliberately skipped this table.
    pub marker_present: bool,
    pub scanned: u64,
    pub repaired: u64,
}

/// Detect plaintext residual rows on every PII table whose encryption-migration
/// marker is present, and re-encrypt them in place.
///
/// Designed to run on every boot AFTER the four `encrypt_*_pii` runners.
/// Cheap when nothing is broken: one `SELECT` per table, one `decrypt_field`
/// attempt per non-empty value, zero writes when every value is already
/// ciphertext. Expensive only when a regression actually happened.
///
/// Returns Err only on hard SQL failures or when the encryption key is not
/// initialised. The caller in `lib.rs` treats Err as non-fatal (log + sentry
/// warn) so a transient repair issue cannot break boot.
///
/// Idempotent: a second call on the same DB scans every row again and walks
/// away with `plaintext_residuals_repaired == 0`.
pub async fn verify_or_repair_encryption(
    pool: &SqlitePool,
) -> Result<RepairReport, String> {
    if !is_encryption_ready() {
        return Err("encryption not ready, skipping verify-or-repair".to_string());
    }

    let mut report = RepairReport::default();

    for target in REPAIR_TARGETS {
        // Marker gate: pre-migration tables are not in scope for repair.
        let marker: Option<(String,)> = sqlx::query_as(
            "SELECT migration_key FROM encryption_migration_state \
             WHERE migration_key = ?",
        )
        .bind(target.marker)
        .fetch_optional(pool)
        .await
        .map_err(|e| format!("marker lookup failed for {}: {}", target.table, e))?;

        if marker.is_none() {
            report.per_table.push(TableRepair {
                table: target.table,
                marker_present: false,
                scanned: 0,
                repaired: 0,
            });
            continue;
        }

        let select_cols = {
            let mut s = String::from("id");
            for c in target.columns {
                s.push_str(", ");
                s.push_str(c);
            }
            s
        };
        let select_sql = format!("SELECT {} FROM {}", select_cols, target.table);

        let rows = sqlx::query(&select_sql)
            .fetch_all(pool)
            .await
            .map_err(|e| format!("{} read failed: {}", target.table, e))?;

        let mut t_scanned: u64 = 0;
        let mut t_repaired: u64 = 0;

        for row in &rows {
            t_scanned += 1;
            let id: String = row
                .try_get::<String, _>("id")
                .map_err(|e| format!("{}.id read failed: {}", target.table, e))?;

            // Collect (column, new_ciphertext) pairs for every PII column whose
            // current value is plaintext (decrypt fails). Empty/NULL skipped.
            let mut updates: Vec<(&'static str, String)> = Vec::new();
            for col in target.columns {
                let val_opt: Option<String> = row
                    .try_get::<Option<String>, _>(*col)
                    .ok()
                    .flatten();
                let val = match val_opt {
                    Some(s) if !s.is_empty() => s,
                    _ => continue,
                };
                if decrypt_field(&val).is_ok() {
                    continue;
                }
                // Plaintext residual.
                match encrypt_field(&val) {
                    Ok(ct) => updates.push((*col, ct)),
                    Err(e) => {
                        eprintln!(
                            "⚠️  repair: encrypt failed for {}.{} (id={}): {}",
                            target.table, col, id, e
                        );
                        continue;
                    }
                }
            }

            if updates.is_empty() {
                continue;
            }

            let set_clause = updates
                .iter()
                .map(|(c, _)| format!("{} = ?", c))
                .collect::<Vec<_>>()
                .join(", ");
            let upd_sql = format!(
                "UPDATE {} SET {} WHERE id = ?",
                target.table, set_clause
            );
            let mut q = sqlx::query(&upd_sql);
            for (_, v) in &updates {
                q = q.bind(v);
            }
            q = q.bind(&id);
            q.execute(pool)
                .await
                .map_err(|e| format!("repair update {} id {}: {}", target.table, id, e))?;

            t_repaired += 1;
        }

        report.total_scanned += t_scanned;
        report.plaintext_residuals_repaired += t_repaired;
        report.per_table.push(TableRepair {
            table: target.table,
            marker_present: true,
            scanned: t_scanned,
            repaired: t_repaired,
        });
    }

    Ok(report)
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use crate::encryption::{decrypt_field, init_encryption_with_salt};
    use sqlx::sqlite::SqlitePoolOptions;
    use std::path::PathBuf;

    // Deterministic test salt — matches encryption.rs::tests TEST_SALT shape.
    // OnceLock means only the *first* init in the test process wins; subsequent
    // calls return Err("already initialized") which is benign here.
    const TEST_SALT: [u8; 32] = [0xCD; 32];

    fn unique_temp_db_path() -> PathBuf {
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0);
        let pid = std::process::id();
        std::env::temp_dir().join(format!("fluxion-data-mig-{}-{}.db", pid, nanos))
    }

    async fn seed_minimal_schema(pool: &SqlitePool) {
        sqlx::query(
            "CREATE TABLE clienti (\
                id TEXT PRIMARY KEY,\
                nome TEXT NOT NULL,\
                cognome TEXT NOT NULL,\
                telefono TEXT NOT NULL,\
                email TEXT,\
                codice_fiscale TEXT,\
                partita_iva TEXT,\
                indirizzo TEXT,\
                cap TEXT,\
                citta TEXT,\
                pec TEXT,\
                data_nascita TEXT\
            )",
        )
        .execute(pool)
        .await
        .unwrap();

        sqlx::query(
            "CREATE TABLE operatori (\
                id TEXT PRIMARY KEY,\
                nome TEXT NOT NULL,\
                cognome TEXT NOT NULL,\
                email TEXT,\
                telefono TEXT\
            )",
        )
        .execute(pool)
        .await
        .unwrap();

        // S257 P2: suppliers schema post-migration-040 (no UNIQUE constraints).
        sqlx::query(
            "CREATE TABLE suppliers (\
                id TEXT PRIMARY KEY,\
                nome TEXT NOT NULL,\
                email TEXT,\
                telefono TEXT,\
                indirizzo TEXT,\
                partita_iva TEXT\
            )",
        )
        .execute(pool)
        .await
        .unwrap();

        // S260 P4: impostazioni_fatturazione schema (minimal — only PII cols
        // touched by the runner + `id` PK). Real schema (migration 007) has 27
        // columns but the runner reads/writes only the 8 PII targets.
        sqlx::query(
            "CREATE TABLE impostazioni_fatturazione (\
                id TEXT PRIMARY KEY DEFAULT 'default',\
                denominazione TEXT NOT NULL DEFAULT '',\
                partita_iva TEXT NOT NULL DEFAULT '',\
                codice_fiscale TEXT,\
                indirizzo TEXT NOT NULL DEFAULT '',\
                telefono TEXT,\
                email TEXT,\
                pec TEXT,\
                iban TEXT\
            )",
        )
        .execute(pool)
        .await
        .unwrap();

        sqlx::query(
            "CREATE TABLE encryption_migration_state (\
                migration_key TEXT PRIMARY KEY,\
                applied_at TEXT NOT NULL DEFAULT (datetime('now')),\
                rows_processed INTEGER NOT NULL DEFAULT 0,\
                backup_path TEXT\
            )",
        )
        .execute(pool)
        .await
        .unwrap();
    }

    async fn seed_plaintext_clienti(pool: &SqlitePool, n: usize) {
        for i in 0..n {
            sqlx::query(
                "INSERT INTO clienti (id, nome, cognome, telefono, email) \
                 VALUES (?, ?, ?, ?, ?)",
            )
            .bind(format!("id-{:04}", i))
            .bind(format!("Nome{}", i))
            .bind(format!("Cognome{}", i))
            .bind(format!("33912{:05}", i))
            .bind(format!("user{}@example.it", i))
            .execute(pool)
            .await
            .unwrap();
        }
    }

    async fn seed_plaintext_operatori(pool: &SqlitePool, n: usize) {
        for i in 0..n {
            sqlx::query(
                "INSERT INTO operatori (id, nome, cognome, email, telefono) \
                 VALUES (?, ?, ?, ?, ?)",
            )
            .bind(format!("op-{:04}", i))
            .bind(format!("OpNome{}", i))
            .bind(format!("OpCognome{}", i))
            .bind(format!("op{}@example.it", i))
            .bind(format!("33312{:05}", i))
            .execute(pool)
            .await
            .unwrap();
        }
    }

    async fn seed_plaintext_suppliers(pool: &SqlitePool, n: usize) {
        for i in 0..n {
            sqlx::query(
                "INSERT INTO suppliers (id, nome, email, telefono, indirizzo, partita_iva) \
                 VALUES (?, ?, ?, ?, ?, ?)",
            )
            .bind(format!("sup-{:04}", i))
            .bind(format!("SupNome{}", i))
            .bind(format!("sup{}@example.it", i))
            .bind(format!("33012{:05}", i))
            .bind(format!("Via Roma {}", i))
            .bind(format!("IT{:011}", i))
            .execute(pool)
            .await
            .unwrap();
        }
    }

    /// S260 P4: seed singleton row `id='default'` con 8 cols PII plaintext
    /// (mirror dati founder reali su iMac: denominazione + partita_iva +
    /// codice_fiscale + indirizzo populated; telefono/email/pec/iban valorizzati
    /// per testare round-trip su tutti i campi PII encryptable).
    async fn seed_plaintext_impostazioni_fatturazione(pool: &SqlitePool) {
        sqlx::query(
            "INSERT INTO impostazioni_fatturazione \
             (id, denominazione, partita_iva, codice_fiscale, indirizzo, telefono, email, pec, iban) \
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        )
        .bind("default")
        .bind("Automation Business")
        .bind("02159940762")
        .bind("DSTMGN81S12L738L")
        .bind("Via Roma 1")
        .bind("3331234567")
        .bind("a@b.it")
        .bind("pec@pec.it")
        .bind("IT60X0542811101000000123456")
        .execute(pool)
        .await
        .unwrap();
    }

    #[tokio::test]
    async fn test_encrypt_clienti_pii_basic_and_idempotent() {
        let _ = init_encryption_with_salt("data-mig-test-pw", "data-mig-test-dev", &TEST_SALT);

        let db_path = unique_temp_db_path();
        let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
        let pool = SqlitePoolOptions::new()
            .max_connections(2)
            .connect(&db_url)
            .await
            .expect("connect temp db");

        seed_minimal_schema(&pool).await;
        seed_plaintext_clienti(&pool, 10).await;

        // First run: should encrypt all 10 rows, create backup, insert marker.
        let report = encrypt_clienti_pii(&pool, &db_path)
            .await
            .expect("first run ok");
        assert!(!report.already_applied);
        assert_eq!(report.encrypted_rows, 10, "all 10 plaintext rows encrypted");
        assert_eq!(report.skipped_rows, 0);
        let backup = report.backup_path.as_ref().expect("backup path set");
        assert!(backup.exists(), "backup file written to disk");
        // New backup filename format includes the migration key.
        assert!(
            backup
                .to_string_lossy()
                .contains("encrypt_clienti_pii_v1"),
            "backup filename must embed migration_key: got {}",
            backup.display()
        );

        // Every stored value should now round-trip through decrypt_field.
        let rows = sqlx::query("SELECT nome, telefono, email FROM clienti")
            .fetch_all(&pool)
            .await
            .unwrap();
        for r in &rows {
            let nome: String = r.try_get("nome").unwrap();
            let tel: String = r.try_get("telefono").unwrap();
            let email: String = r.try_get("email").unwrap();
            assert!(!nome.starts_with("Nome"), "nome should be ciphertext");
            assert!(!tel.starts_with("33912"), "telefono should be ciphertext");
            let dec_nome = decrypt_field(&nome).expect("decrypt nome");
            assert!(dec_nome.starts_with("Nome"));
            let dec_tel = decrypt_field(&tel).expect("decrypt telefono");
            assert!(dec_tel.starts_with("33912"));
            let dec_email = decrypt_field(&email).expect("decrypt email");
            assert!(dec_email.contains("@example.it"));
        }

        // Marker present.
        let marker: Option<(String, i64)> = sqlx::query_as(
            "SELECT migration_key, rows_processed FROM encryption_migration_state \
             WHERE migration_key = ?",
        )
        .bind(MIGRATION_KEY_CLIENTI)
        .fetch_optional(&pool)
        .await
        .unwrap();
        let marker = marker.expect("marker inserted");
        assert_eq!(marker.0, MIGRATION_KEY_CLIENTI);
        assert_eq!(marker.1, 10);

        // Second run: idempotent — already_applied, no work.
        let report2 = encrypt_clienti_pii(&pool, &db_path)
            .await
            .expect("second run ok");
        assert!(report2.already_applied);
        assert_eq!(report2.encrypted_rows, 0);
        assert!(report2.backup_path.is_none());

        // Cleanup
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(backup);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
    }

    #[tokio::test]
    async fn test_encrypt_operatori_pii_basic_and_idempotent() {
        let _ = init_encryption_with_salt("data-mig-test-pw", "data-mig-test-dev", &TEST_SALT);

        let db_path = unique_temp_db_path();
        let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
        let pool = SqlitePoolOptions::new()
            .max_connections(2)
            .connect(&db_url)
            .await
            .expect("connect temp db");

        seed_minimal_schema(&pool).await;
        seed_plaintext_operatori(&pool, 5).await;

        // First run: encrypt 5 rows, create backup with key in filename, insert marker.
        let report = encrypt_operatori_pii(&pool, &db_path)
            .await
            .expect("first run ok");
        assert!(!report.already_applied);
        assert_eq!(report.encrypted_rows, 5, "all 5 plaintext rows encrypted");
        assert_eq!(report.skipped_rows, 0);
        let backup = report.backup_path.as_ref().expect("backup path set");
        assert!(backup.exists(), "backup file written to disk");
        assert!(
            backup
                .to_string_lossy()
                .contains("encrypt_operatori_pii_v1"),
            "backup filename must embed migration_key: got {}",
            backup.display()
        );

        // Round-trip every column.
        let rows = sqlx::query("SELECT nome, cognome, email, telefono FROM operatori")
            .fetch_all(&pool)
            .await
            .unwrap();
        for r in &rows {
            let nome: String = r.try_get("nome").unwrap();
            let cognome: String = r.try_get("cognome").unwrap();
            let email: String = r.try_get("email").unwrap();
            let tel: String = r.try_get("telefono").unwrap();
            assert!(!nome.starts_with("OpNome"), "nome should be ciphertext");
            assert!(!cognome.starts_with("OpCognome"), "cognome should be ciphertext");
            assert!(decrypt_field(&nome).unwrap().starts_with("OpNome"));
            assert!(decrypt_field(&cognome).unwrap().starts_with("OpCognome"));
            assert!(decrypt_field(&email).unwrap().contains("@example.it"));
            assert!(decrypt_field(&tel).unwrap().starts_with("33312"));
        }

        // Marker present.
        let marker: Option<(String, i64)> = sqlx::query_as(
            "SELECT migration_key, rows_processed FROM encryption_migration_state \
             WHERE migration_key = ?",
        )
        .bind(MIGRATION_KEY_OPERATORI)
        .fetch_optional(&pool)
        .await
        .unwrap();
        let marker = marker.expect("marker inserted");
        assert_eq!(marker.0, MIGRATION_KEY_OPERATORI);
        assert_eq!(marker.1, 5);

        // Second run: already_applied.
        let report2 = encrypt_operatori_pii(&pool, &db_path)
            .await
            .expect("second run ok");
        assert!(report2.already_applied);
        assert_eq!(report2.encrypted_rows, 0);
        assert!(report2.backup_path.is_none());

        // Cleanup
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(backup);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
    }

    #[tokio::test]
    async fn test_encrypt_suppliers_pii_basic_and_idempotent() {
        let _ = init_encryption_with_salt("data-mig-test-pw", "data-mig-test-dev", &TEST_SALT);

        let db_path = unique_temp_db_path();
        let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
        let pool = SqlitePoolOptions::new()
            .max_connections(2)
            .connect(&db_url)
            .await
            .expect("connect temp db");

        seed_minimal_schema(&pool).await;
        seed_plaintext_suppliers(&pool, 7).await;

        // First run: encrypt 7 rows, create backup with key in filename, insert marker.
        let report = encrypt_suppliers_pii(&pool, &db_path)
            .await
            .expect("first run ok");
        assert!(!report.already_applied);
        assert_eq!(report.encrypted_rows, 7, "all 7 plaintext rows encrypted");
        assert_eq!(report.skipped_rows, 0);
        let backup = report.backup_path.as_ref().expect("backup path set");
        assert!(backup.exists(), "backup file written to disk");
        assert!(
            backup
                .to_string_lossy()
                .contains("encrypt_suppliers_pii_v1"),
            "backup filename must embed migration_key: got {}",
            backup.display()
        );

        // Round-trip every PII column.
        let rows =
            sqlx::query("SELECT nome, email, telefono, indirizzo, partita_iva FROM suppliers")
                .fetch_all(&pool)
                .await
                .unwrap();
        for r in &rows {
            let nome: String = r.try_get("nome").unwrap();
            let email: String = r.try_get("email").unwrap();
            let tel: String = r.try_get("telefono").unwrap();
            let ind: String = r.try_get("indirizzo").unwrap();
            let piva: String = r.try_get("partita_iva").unwrap();
            assert!(!nome.starts_with("SupNome"), "nome should be ciphertext");
            assert!(!ind.starts_with("Via Roma"), "indirizzo should be ciphertext");
            assert!(!piva.starts_with("IT"), "partita_iva should be ciphertext");
            assert!(decrypt_field(&nome).unwrap().starts_with("SupNome"));
            assert!(decrypt_field(&email).unwrap().contains("@example.it"));
            assert!(decrypt_field(&tel).unwrap().starts_with("33012"));
            assert!(decrypt_field(&ind).unwrap().starts_with("Via Roma"));
            assert!(decrypt_field(&piva).unwrap().starts_with("IT"));
        }

        // Marker present.
        let marker: Option<(String, i64)> = sqlx::query_as(
            "SELECT migration_key, rows_processed FROM encryption_migration_state \
             WHERE migration_key = ?",
        )
        .bind(MIGRATION_KEY_SUPPLIERS)
        .fetch_optional(&pool)
        .await
        .unwrap();
        let marker = marker.expect("marker inserted");
        assert_eq!(marker.0, MIGRATION_KEY_SUPPLIERS);
        assert_eq!(marker.1, 7);

        // Second run: already_applied.
        let report2 = encrypt_suppliers_pii(&pool, &db_path)
            .await
            .expect("second run ok");
        assert!(report2.already_applied);
        assert_eq!(report2.encrypted_rows, 0);
        assert!(report2.backup_path.is_none());

        // Cleanup
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(backup);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
    }

    #[tokio::test]
    async fn test_encrypt_impostazioni_fatturazione_pii_basic_and_idempotent() {
        let _ = init_encryption_with_salt("data-mig-test-pw", "data-mig-test-dev", &TEST_SALT);

        let db_path = unique_temp_db_path();
        let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
        let pool = SqlitePoolOptions::new()
            .max_connections(2)
            .connect(&db_url)
            .await
            .expect("connect temp db");

        seed_minimal_schema(&pool).await;
        seed_plaintext_impostazioni_fatturazione(&pool).await;

        // First run: encrypt 1 singleton row, create backup with key in filename,
        // insert marker.
        let report = encrypt_impostazioni_fatturazione_pii(&pool, &db_path)
            .await
            .expect("first run ok");
        assert!(!report.already_applied);
        assert_eq!(
            report.encrypted_rows, 1,
            "singleton row (id='default') encrypted"
        );
        assert_eq!(report.skipped_rows, 0);
        let backup = report.backup_path.as_ref().expect("backup path set");
        assert!(backup.exists(), "backup file written to disk");
        assert!(
            backup
                .to_string_lossy()
                .contains("encrypt_impostazioni_fatturazione_pii_v1"),
            "backup filename must embed migration_key: got {}",
            backup.display()
        );

        // Round-trip every PII column.
        let rows = sqlx::query(
            "SELECT denominazione, partita_iva, codice_fiscale, indirizzo, \
                    telefono, email, pec, iban \
             FROM impostazioni_fatturazione",
        )
        .fetch_all(&pool)
        .await
        .unwrap();
        assert_eq!(rows.len(), 1, "singleton row preserved");
        for r in &rows {
            let denom: String = r.try_get("denominazione").unwrap();
            let piva: String = r.try_get("partita_iva").unwrap();
            let cf: String = r.try_get("codice_fiscale").unwrap();
            let ind: String = r.try_get("indirizzo").unwrap();
            let tel: String = r.try_get("telefono").unwrap();
            let email: String = r.try_get("email").unwrap();
            let pec: String = r.try_get("pec").unwrap();
            let iban: String = r.try_get("iban").unwrap();
            assert!(
                !denom.starts_with("Automation"),
                "denominazione should be ciphertext"
            );
            assert!(!piva.starts_with("02159"), "partita_iva should be ciphertext");
            assert!(!cf.starts_with("DSTMGN"), "codice_fiscale should be ciphertext");
            assert!(!ind.starts_with("Via Roma"), "indirizzo should be ciphertext");
            assert!(!tel.starts_with("33312"), "telefono should be ciphertext");
            assert!(!iban.starts_with("IT60"), "iban should be ciphertext");
            assert_eq!(decrypt_field(&denom).unwrap(), "Automation Business");
            assert_eq!(decrypt_field(&piva).unwrap(), "02159940762");
            assert_eq!(decrypt_field(&cf).unwrap(), "DSTMGN81S12L738L");
            assert_eq!(decrypt_field(&ind).unwrap(), "Via Roma 1");
            assert_eq!(decrypt_field(&tel).unwrap(), "3331234567");
            assert_eq!(decrypt_field(&email).unwrap(), "a@b.it");
            assert_eq!(decrypt_field(&pec).unwrap(), "pec@pec.it");
            assert_eq!(
                decrypt_field(&iban).unwrap(),
                "IT60X0542811101000000123456"
            );
        }

        // Marker present.
        let marker: Option<(String, i64)> = sqlx::query_as(
            "SELECT migration_key, rows_processed FROM encryption_migration_state \
             WHERE migration_key = ?",
        )
        .bind(MIGRATION_KEY_IMPOSTAZIONI_FATTURAZIONE)
        .fetch_optional(&pool)
        .await
        .unwrap();
        let marker = marker.expect("marker inserted");
        assert_eq!(marker.0, MIGRATION_KEY_IMPOSTAZIONI_FATTURAZIONE);
        assert_eq!(marker.1, 1);

        // Second run: already_applied.
        let report2 = encrypt_impostazioni_fatturazione_pii(&pool, &db_path)
            .await
            .expect("second run ok");
        assert!(report2.already_applied);
        assert_eq!(report2.encrypted_rows, 0);
        assert!(report2.backup_path.is_none());

        // Cleanup
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(backup);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
    }
}
