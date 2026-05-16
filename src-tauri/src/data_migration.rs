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
//   * `clienti`  — S251 (Cat 3 P0 #2 Step D)  — 11 sensitive columns
//   * `operatori` — S255 (P1)                  — 4 sensitive columns
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
//   * `suppliers.*` — S256
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
}
