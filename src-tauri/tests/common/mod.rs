// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Common Helpers
// Setup database reale, migrations, cleanup
// ═══════════════════════════════════════════════════════════════════

use std::path::PathBuf;
use std::fs;
use sqlx::{SqlitePool, sqlite::SqlitePoolOptions};
use chrono::NaiveDateTime;

/// Crea un database SQLite temporaneo su filesystem
/// Applica tutte le migrations e ritorna il pool connesso
pub async fn create_test_database() -> (SqlitePool, PathBuf) {
    // Crea file temporaneo .db
    let temp_dir = std::env::temp_dir();
    let db_file = temp_dir.join(format!("fluxion_test_{}.db", uuid::Uuid::new_v4()));
    let db_url = format!("sqlite://{}", db_file.display());

    // Crea pool connesso
    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&db_url)
        .await
        .expect("Failed to connect to test database");

    // Applica migrations
    sqlx::migrate!("./migrations")
        .run(&pool)
        .await
        .expect("Failed to run migrations");

    (pool, db_file)
}

/// Cleanup: disconnetti pool e rimuovi file database
pub async fn cleanup_test_database(pool: SqlitePool, db_file: PathBuf) {
    pool.close().await;

    if db_file.exists() {
        fs::remove_file(&db_file).expect("Failed to remove test database file");
    }
}

/// Helper: crea datetime futuro per test
pub fn make_future_datetime() -> NaiveDateTime {
    chrono::NaiveDate::from_ymd_opt(2026, 12, 31)
        .unwrap()
        .and_hms_opt(14, 0, 0)
        .unwrap()
}

/// Helper: crea datetime passato per test
pub fn make_past_datetime() -> NaiveDateTime {
    chrono::NaiveDate::from_ymd_opt(2020, 1, 1)
        .unwrap()
        .and_hms_opt(10, 0, 0)
        .unwrap()
}

/// Helper: insert cliente di test nel DB
pub async fn insert_test_cliente(pool: &SqlitePool, id: &str, nome: &str, cognome: &str) {
    sqlx::query(
        r#"
        INSERT INTO clienti (id, nome, cognome, telefono, email, created_at, updated_at)
        VALUES (?, ?, ?, '3331234567', 'test@example.com', datetime('now'), datetime('now'))
        "#,
    )
    .bind(id)
    .bind(nome)
    .bind(cognome)
    .execute(pool)
    .await
    .expect("Failed to insert test cliente");
}

/// Helper: insert operatore di test nel DB
pub async fn insert_test_operatore(pool: &SqlitePool, id: &str, nome: &str, cognome: &str) {
    sqlx::query(
        r#"
        INSERT INTO operatori (id, nome, cognome, telefono, email, created_at, updated_at)
        VALUES (?, ?, ?, '3331234567', 'operatore@example.com', datetime('now'), datetime('now'))
        "#,
    )
    .bind(id)
    .bind(nome)
    .bind(cognome)
    .execute(pool)
    .await
    .expect("Failed to insert test operatore");
}

/// Helper: insert servizio di test nel DB
pub async fn insert_test_servizio(
    pool: &SqlitePool,
    id: &str,
    nome: &str,
    durata_minuti: i32,
    prezzo: f64,
) {
    sqlx::query(
        r#"
        INSERT INTO servizi (id, nome, durata_minuti, prezzo, categoria, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'Test', datetime('now'), datetime('now'))
        "#,
    )
    .bind(id)
    .bind(nome)
    .bind(durata_minuti)
    .bind(prezzo)
    .execute(pool)
    .await
    .expect("Failed to insert test servizio");
}

/// Helper: insert orario lavoro di test
pub async fn insert_test_orario_lavoro(
    pool: &SqlitePool,
    giorno_settimana: i32,
    ora_inizio: &str,
    ora_fine: &str,
) {
    sqlx::query(
        r#"
        INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'lavoro', datetime('now'), datetime('now'))
        "#,
    )
    .bind(uuid::Uuid::new_v4().to_string())
    .bind(giorno_settimana)
    .bind(ora_inizio)
    .bind(ora_fine)
    .execute(pool)
    .await
    .expect("Failed to insert test orario lavoro");
}

/// Helper: insert festività di test
pub async fn insert_test_festivita(
    pool: &SqlitePool,
    data: &str,
    descrizione: &str,
    ricorrente: bool,
) {
    sqlx::query(
        r#"
        INSERT INTO festività (id, data, descrizione, ricorrente, created_at, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        "#,
    )
    .bind(uuid::Uuid::new_v4().to_string())
    .bind(data)
    .bind(descrizione)
    .bind(if ricorrente { 1 } else { 0 })
    .execute(pool)
    .await
    .expect("Failed to insert test festività");
}
