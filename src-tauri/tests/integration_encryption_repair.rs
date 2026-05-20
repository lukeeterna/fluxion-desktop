// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Encryption Repair (S272)
// BUG-FATT-7 prevention: verify_or_repair_encryption boot step
// detects plaintext residuals after migration marker applied and
// re-encrypts in place. Cross-entity: clienti / operatori / suppliers /
// impostazioni_fatturazione.
// ═══════════════════════════════════════════════════════════════════

use sqlx::{sqlite::SqlitePoolOptions, Row, SqlitePool};
use std::path::PathBuf;

use tauri_app_lib::data_migration::verify_or_repair_encryption;
use tauri_app_lib::encryption::{decrypt_field, encrypt_field, init_encryption_with_salt};

// Deterministic 32-byte salt for this test binary. Each `cargo test --test
// integration_encryption_repair` invocation is its own process → OnceLock
// is fresh; the `let _ =` swallow handles repeat init within the binary.
const TEST_SALT: [u8; 32] = [0xEF; 32];

fn setup_encryption_once() {
    let _ = init_encryption_with_salt("repair-test-pw", "repair-test-dev", &TEST_SALT);
}

fn unique_temp_db_path() -> PathBuf {
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    let pid = std::process::id();
    std::env::temp_dir().join(format!("fluxion-repair-{}-{}.db", pid, nanos))
}

/// Schema minimale che copre le 4 tabelle PII target + marker table.
/// Mirror del subset rilevante delle migrations prod (007/002/016/038).
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

async fn setup() -> (SqlitePool, PathBuf) {
    setup_encryption_once();
    let db_path = unique_temp_db_path();
    let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
    let pool = SqlitePoolOptions::new()
        .max_connections(2)
        .connect(&db_url)
        .await
        .expect("connect temp db");
    seed_minimal_schema(&pool).await;
    (pool, db_path)
}

async fn cleanup(pool: SqlitePool, db_path: PathBuf) {
    pool.close().await;
    let _ = std::fs::remove_file(&db_path);
    let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
    let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
}

async fn insert_marker(pool: &SqlitePool, key: &str) {
    sqlx::query(
        "INSERT INTO encryption_migration_state (migration_key, rows_processed) \
         VALUES (?, 1)",
    )
    .bind(key)
    .execute(pool)
    .await
    .unwrap();
}

// ────────────────────────────────────────────────────────────────────
// S272 Step 3 scenarios
// ────────────────────────────────────────────────────────────────────

/// BUG-FATT-7 regression: row inserito ciphertext correttamente, marker
/// applied, poi UI write path bypassa encryption e sovrascrive una colonna
/// con plaintext. `verify_or_repair_encryption` deve detectare e re-encrypt.
#[tokio::test]
async fn test_repair_detects_and_fixes_plaintext_residual() {
    let (pool, db_path) = setup().await;

    // Seed clienti row tutta ciphertext (post-migration normale).
    let nome_ct = encrypt_field("Mario").unwrap();
    let cognome_ct = encrypt_field("Rossi").unwrap();
    let tel_ct = encrypt_field("3331234567").unwrap();
    sqlx::query(
        "INSERT INTO clienti (id, nome, cognome, telefono) VALUES ('cli-1', ?, ?, ?)",
    )
    .bind(&nome_ct)
    .bind(&cognome_ct)
    .bind(&tel_ct)
    .execute(&pool)
    .await
    .unwrap();
    insert_marker(&pool, "encrypt_clienti_pii_v1").await;

    // Simula BUG-FATT-7: legacy binary scrive plaintext sopra ciphertext.
    sqlx::query("UPDATE clienti SET nome = 'PlainMario' WHERE id = 'cli-1'")
        .execute(&pool)
        .await
        .unwrap();

    let report = verify_or_repair_encryption(&pool).await.expect("repair ok");
    assert_eq!(
        report.plaintext_residuals_repaired, 1,
        "1 row should be detected as plaintext residual"
    );
    assert!(report.total_scanned >= 1);

    // Verify post-repair: nome è ciphertext che decifra al plaintext originale.
    let row = sqlx::query("SELECT nome, cognome, telefono FROM clienti WHERE id = 'cli-1'")
        .fetch_one(&pool)
        .await
        .unwrap();
    let nome: String = row.try_get("nome").unwrap();
    let cognome: String = row.try_get("cognome").unwrap();
    let tel: String = row.try_get("telefono").unwrap();
    assert_ne!(nome, "PlainMario", "nome must be re-encrypted (not plaintext)");
    assert_eq!(decrypt_field(&nome).unwrap(), "PlainMario");
    // Le altre colonne ciphertext devono restare intatte.
    assert_eq!(decrypt_field(&cognome).unwrap(), "Rossi");
    assert_eq!(decrypt_field(&tel).unwrap(), "3331234567");

    cleanup(pool, db_path).await;
}

/// Idempotency: ripetere repair su DB già pulito non deve fare nulla.
#[tokio::test]
async fn test_repair_is_idempotent_on_clean_db() {
    let (pool, db_path) = setup().await;

    // Singleton impostazioni_fatturazione tutto ciphertext + marker applied.
    let denom_ct = encrypt_field("Acme Srl").unwrap();
    let piva_ct = encrypt_field("12345678901").unwrap();
    let ind_ct = encrypt_field("Via Verdi 1").unwrap();
    sqlx::query(
        "INSERT INTO impostazioni_fatturazione (id, denominazione, partita_iva, indirizzo) \
         VALUES ('default', ?, ?, ?)",
    )
    .bind(&denom_ct)
    .bind(&piva_ct)
    .bind(&ind_ct)
    .execute(&pool)
    .await
    .unwrap();
    insert_marker(&pool, "encrypt_impostazioni_fatturazione_pii_v1").await;

    // First pass: 0 repairs su DB già coerente.
    let r1 = verify_or_repair_encryption(&pool).await.expect("first repair");
    assert_eq!(r1.plaintext_residuals_repaired, 0);

    // Snapshot ciphertext post-pass-1.
    let denom_after_1: String =
        sqlx::query_scalar("SELECT denominazione FROM impostazioni_fatturazione WHERE id = 'default'")
            .fetch_one(&pool)
            .await
            .unwrap();

    // Second pass: ancora 0 repairs + ciphertext byte-for-byte identico
    // (NO re-encrypt opportunistico — la funzione deve essere a costo zero
    // sul cammino felice).
    let r2 = verify_or_repair_encryption(&pool).await.expect("second repair");
    assert_eq!(r2.plaintext_residuals_repaired, 0);

    let denom_after_2: String =
        sqlx::query_scalar("SELECT denominazione FROM impostazioni_fatturazione WHERE id = 'default'")
            .fetch_one(&pool)
            .await
            .unwrap();
    assert_eq!(
        denom_after_1, denom_after_2,
        "idempotent: ciphertext must be byte-for-byte identical between passes"
    );

    // E la decifratura resta corretta.
    assert_eq!(decrypt_field(&denom_after_2).unwrap(), "Acme Srl");

    cleanup(pool, db_path).await;
}

/// Tabelle senza marker (pre-migration state) NON devono essere repair-ate:
/// è il job del marker-gated runner, non del safety net.
#[tokio::test]
async fn test_repair_skips_tables_without_marker() {
    let (pool, db_path) = setup().await;

    // Cliente plaintext, NESSUN marker.
    sqlx::query(
        "INSERT INTO clienti (id, nome, cognome, telefono) \
         VALUES ('cli-1', 'PrePlain', 'Cognome', '3331234567')",
    )
    .execute(&pool)
    .await
    .unwrap();

    let report = verify_or_repair_encryption(&pool).await.expect("repair ok");
    assert_eq!(
        report.plaintext_residuals_repaired, 0,
        "no marker ⇒ table skipped ⇒ zero repairs"
    );
    assert_eq!(report.total_scanned, 0);

    // Verifica che la riga sia rimasta intatta (NON è stata cifrata).
    let nome: String = sqlx::query_scalar("SELECT nome FROM clienti WHERE id = 'cli-1'")
        .fetch_one(&pool)
        .await
        .unwrap();
    assert_eq!(nome, "PrePlain", "row must be untouched");

    // Per-table breakdown deve segnalare marker_present=false.
    let clienti_breakdown = report
        .per_table
        .iter()
        .find(|t| t.table == "clienti")
        .expect("clienti breakdown present");
    assert!(!clienti_breakdown.marker_present);
    assert_eq!(clienti_breakdown.scanned, 0);
    assert_eq!(clienti_breakdown.repaired, 0);

    cleanup(pool, db_path).await;
}

/// REGOLA #11 cross-entity: 4 tabelle, 4 plaintext residual, 4 marker
/// applied → 4 repairs in singolo pass. Verifica anche roundtrip completo.
#[tokio::test]
async fn test_repair_cross_entity_4_tables() {
    let (pool, db_path) = setup().await;

    // 4 markers applied (simulating prior successful migrations).
    for key in &[
        "encrypt_clienti_pii_v1",
        "encrypt_operatori_pii_v1",
        "encrypt_suppliers_pii_v1",
        "encrypt_impostazioni_fatturazione_pii_v1",
    ] {
        insert_marker(&pool, key).await;
    }

    // Seed: 1 riga per tabella, con 1 colonna plaintext + altre cifrate
    // (mix realistico — simula UI write parziale).
    let cognome_ct = encrypt_field("CliCognomeCt").unwrap();
    let tel_ct = encrypt_field("3331234567").unwrap();
    sqlx::query(
        "INSERT INTO clienti (id, nome, cognome, telefono) \
         VALUES ('cli-1', 'PlainCli', ?, ?)",
    )
    .bind(&cognome_ct)
    .bind(&tel_ct)
    .execute(&pool)
    .await
    .unwrap();

    let op_cognome_ct = encrypt_field("OpCognomeCt").unwrap();
    sqlx::query("INSERT INTO operatori (id, nome, cognome) VALUES ('op-1', 'PlainOp', ?)")
        .bind(&op_cognome_ct)
        .execute(&pool)
        .await
        .unwrap();

    sqlx::query("INSERT INTO suppliers (id, nome) VALUES ('sup-1', 'PlainSup')")
        .execute(&pool)
        .await
        .unwrap();

    sqlx::query(
        "INSERT INTO impostazioni_fatturazione \
         (id, denominazione, partita_iva, indirizzo) \
         VALUES ('default', 'PlainDenom', '', '')",
    )
    .execute(&pool)
    .await
    .unwrap();

    let report = verify_or_repair_encryption(&pool).await.expect("repair ok");
    assert_eq!(
        report.plaintext_residuals_repaired, 4,
        "1 plaintext residual per table × 4 tables = 4 repairs"
    );
    assert_eq!(report.per_table.len(), 4);
    for t in &report.per_table {
        assert!(t.marker_present, "marker present for table {}", t.table);
        assert_eq!(t.repaired, 1, "{} should have 1 repair", t.table);
    }

    // Roundtrip post-repair su ogni tabella.
    let nome: String = sqlx::query_scalar("SELECT nome FROM clienti WHERE id = 'cli-1'")
        .fetch_one(&pool)
        .await
        .unwrap();
    assert_ne!(nome, "PlainCli");
    assert_eq!(decrypt_field(&nome).unwrap(), "PlainCli");
    // Le colonne già ciphertext devono essere intatte.
    let cognome: String = sqlx::query_scalar("SELECT cognome FROM clienti WHERE id = 'cli-1'")
        .fetch_one(&pool)
        .await
        .unwrap();
    assert_eq!(decrypt_field(&cognome).unwrap(), "CliCognomeCt");

    let op_nome: String = sqlx::query_scalar("SELECT nome FROM operatori WHERE id = 'op-1'")
        .fetch_one(&pool)
        .await
        .unwrap();
    assert_eq!(decrypt_field(&op_nome).unwrap(), "PlainOp");

    let sup_nome: String = sqlx::query_scalar("SELECT nome FROM suppliers WHERE id = 'sup-1'")
        .fetch_one(&pool)
        .await
        .unwrap();
    assert_eq!(decrypt_field(&sup_nome).unwrap(), "PlainSup");

    let denom: String = sqlx::query_scalar(
        "SELECT denominazione FROM impostazioni_fatturazione WHERE id = 'default'",
    )
    .fetch_one(&pool)
    .await
    .unwrap();
    assert_eq!(decrypt_field(&denom).unwrap(), "PlainDenom");

    // Second pass deve trovare 0 residuals (idempotency cross-entity).
    let report2 = verify_or_repair_encryption(&pool).await.expect("repair pass 2");
    assert_eq!(
        report2.plaintext_residuals_repaired, 0,
        "second pass on repaired DB → 0 residuals"
    );

    cleanup(pool, db_path).await;
}
