// =============================================================================
// FLUXION - One-shot Data Migration Runners (S251 Cat 3 P0 #2 Step D)
// =============================================================================
//
// Re-encrypts PII rows that were inserted by app builds prior to S249, where
// the AES-256-GCM at-rest wiring was added. Required for GDPR compliance on
// upgraded installs: without this runner the DB would contain a mix of
// plaintext and ciphertext for the 11 SENSITIVE_FIELDS.
//
// Invariants:
//   * Idempotent — guarded by `encryption_migration_state` marker (migration
//     038). A successful run inserts the marker; a subsequent invocation
//     observes the marker and short-circuits to `already_applied()`.
//   * Crash-safe — backup via `VACUUM INTO` taken BEFORE any UPDATE; mutation
//     happens in 100-row transactions; marker is the LAST write, so a crash
//     mid-batch leaves the marker absent and the next run resumes (detection
//     reads each field with `decrypt_field` — Ok = ciphertext = skip, Err =
//     plaintext = encrypt).
//   * Cold-start safe — `is_encryption_ready()` must be true before this runs
//     (caller in `lib.rs` only invokes after Step C auto-init). On a fresh
//     install with no `license_cache` row the runner returns an Err the
//     caller logs but does NOT propagate as a crash.
//
// Scope-out (tracked as FIXMEs for S252):
//   * `fatture.cliente_*` snapshot columns (denormalised at invoice time)
//   * `operatori.{nome,cognome,telefono,email}` — separate runner
//   * `suppliers.*` — separate runner
//
// =============================================================================

use chrono::Utc;
use sqlx::{Row, SqlitePool};
use std::path::{Path, PathBuf};

use crate::encryption::{decrypt_field, encrypt_field, is_encryption_ready};

const MIGRATION_KEY: &str = "encrypt_clienti_pii_v1";

/// Columns on `clienti` that hold GDPR-sensitive plaintext on legacy installs.
/// Order is informational; the runner iterates this slice once per row.
const ENCRYPTABLE_COLUMNS: &[&str] = &[
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

/// Re-encrypt every plaintext PII row currently in `clienti`.
///
/// Pre-conditions:
///   * `is_encryption_ready()` returns true (caller invokes only after the
///     Step C auto-init in `lib.rs`).
///   * Migration 038 has been applied (table `encryption_migration_state`
///     exists). This is the responsibility of the caller in `lib.rs`.
///
/// Post-conditions on Ok:
///   * Every row in `clienti` whose sensitive column held plaintext now holds
///     Base64 ciphertext that round-trips through `decrypt_field`.
///   * A backup of the DB at the time of entry exists at
///     `MigrationReport::backup_path` (unless `already_applied == true`).
///   * The marker row `encryption_migration_state.encrypt_clienti_pii_v1`
///     is present.
pub async fn encrypt_clienti_pii(
    pool: &SqlitePool,
    db_path: &Path,
) -> Result<MigrationReport, String> {
    // ── Pre-flight ────────────────────────────────────────────────────────
    if !is_encryption_ready() {
        return Err(
            "encryption not ready, complete setup wizard first".to_string(),
        );
    }

    // ── Idempotency check ─────────────────────────────────────────────────
    let marker: Option<(String,)> = sqlx::query_as(
        "SELECT migration_key FROM encryption_migration_state \
         WHERE migration_key = ?",
    )
    .bind(MIGRATION_KEY)
    .fetch_optional(pool)
    .await
    .map_err(|e| format!("marker lookup failed: {}", e))?;

    if marker.is_some() {
        return Ok(MigrationReport::already_applied());
    }

    // ── Backup via VACUUM INTO ────────────────────────────────────────────
    // VACUUM INTO is the SQLite-blessed atomic backup primitive: it copies
    // the current committed database (NOT including uncommitted WAL frames)
    // into a fresh file. Safe to invoke from sqlx with the pool open because
    // it acquires only a shared lock on the source. Fails if the target
    // file already exists.
    let ts = Utc::now().format("%Y%m%d-%H%M%S").to_string();
    let backup_path = db_path.with_extension(format!("db.pre-encryption-bak-{}", ts));

    if backup_path.exists() {
        return Err(format!(
            "backup target already exists: {}",
            backup_path.display()
        ));
    }

    let backup_path_str = backup_path
        .to_str()
        .ok_or_else(|| "backup path is not valid UTF-8".to_string())?;
    // Escape single quotes for the SQL string literal (filenames almost
    // never contain them but defence in depth is cheap).
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

    let select_cols =
        "id, nome, cognome, telefono, email, codice_fiscale, partita_iva, \
         indirizzo, cap, citta, pec, data_nascita";

    loop {
        // Build the page query. `BATCH_SIZE` is a compile-time constant so we
        // inline it; only `last_id` is bound.
        let select_sql = if last_id.is_empty() {
            format!(
                "SELECT {} FROM clienti ORDER BY id LIMIT {}",
                select_cols, BATCH_SIZE
            )
        } else {
            format!(
                "SELECT {} FROM clienti WHERE id > ? ORDER BY id LIMIT {}",
                select_cols, BATCH_SIZE
            )
        };

        let mut q = sqlx::query(&select_sql);
        if !last_id.is_empty() {
            q = q.bind(&last_id);
        }
        let rows = q
            .fetch_all(pool)
            .await
            .map_err(|e| format!("clienti read failed: {}", e))?;

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
            for col in ENCRYPTABLE_COLUMNS {
                let val_opt: Option<String> = row
                    .try_get::<Option<String>, _>(*col)
                    .ok()
                    .flatten();
                let val = match val_opt {
                    Some(s) if !s.is_empty() => s,
                    _ => continue,
                };
                // Detection heuristic: if `decrypt_field` returns Ok, this
                // value is already ciphertext (Base64 with the right nonce
                // length + valid GCM tag). Err = plaintext → encrypt.
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
                let upd_sql = format!("UPDATE clienti SET {} WHERE id = ?", set_clause);
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

        // Short page = last page (no more rows after last_id).
        if (rows.len() as i64) < BATCH_SIZE {
            break;
        }
    }

    // ── Marker insert (LAST WRITE) ────────────────────────────────────────
    // We deliberately write the marker only after the encryption loop has
    // run to completion. If a crash happens earlier, the marker is absent
    // and the next run resumes (the detection heuristic guarantees rows
    // already encrypted in the partial run are not re-encrypted).
    sqlx::query(
        "INSERT INTO encryption_migration_state \
         (migration_key, rows_processed, backup_path) VALUES (?, ?, ?)",
    )
    .bind(MIGRATION_KEY)
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
        // Just the two tables we touch — keeps the test independent of the
        // full migration chain.
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

    async fn seed_plaintext_rows(pool: &SqlitePool, n: usize) {
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

    #[tokio::test]
    async fn test_encrypt_clienti_pii_basic_and_idempotent() {
        // Best-effort init — OnceLock allows only one successful init per
        // test process; later tests in the same binary may see Err and that
        // is fine, the previously-set key is still active.
        let _ = init_encryption_with_salt("data-mig-test-pw", "data-mig-test-dev", &TEST_SALT);

        let db_path = unique_temp_db_path();
        let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
        let pool = SqlitePoolOptions::new()
            .max_connections(2)
            .connect(&db_url)
            .await
            .expect("connect temp db");

        seed_minimal_schema(&pool).await;
        seed_plaintext_rows(&pool, 10).await;

        // First run: should encrypt all 10 rows, create backup, insert marker.
        let report = encrypt_clienti_pii(&pool, &db_path)
            .await
            .expect("first run ok");
        assert!(!report.already_applied);
        assert_eq!(report.encrypted_rows, 10, "all 10 plaintext rows encrypted");
        assert_eq!(report.skipped_rows, 0);
        let backup = report.backup_path.as_ref().expect("backup path set");
        assert!(backup.exists(), "backup file written to disk");

        // Every stored value should now round-trip through decrypt_field.
        let rows = sqlx::query("SELECT nome, telefono, email FROM clienti")
            .fetch_all(&pool)
            .await
            .unwrap();
        for r in &rows {
            let nome: String = r.try_get("nome").unwrap();
            let tel: String = r.try_get("telefono").unwrap();
            let email: String = r.try_get("email").unwrap();
            // Stored values are no longer plaintext.
            assert!(!nome.starts_with("Nome"), "nome should be ciphertext");
            assert!(!tel.starts_with("33912"), "telefono should be ciphertext");
            // Round-trip must succeed.
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
        .bind(MIGRATION_KEY)
        .fetch_optional(&pool)
        .await
        .unwrap();
        let marker = marker.expect("marker inserted");
        assert_eq!(marker.0, MIGRATION_KEY);
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
        // WAL/SHM siblings if any
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
    }
}

