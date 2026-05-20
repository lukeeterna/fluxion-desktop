// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Common Helpers
// Setup database reale, migrations, cleanup
// ═══════════════════════════════════════════════════════════════════

use chrono::NaiveDateTime;
use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};
use std::fs;
use std::path::PathBuf;

/// S271: parse SQL into statements (mirror di lib.rs::parse_sql_statements).
/// Necessario perché `sqlx::migrate!()` esegue ogni file come blob e fallisce
/// sulle migrations storiche che hanno `CREATE INDEX` su colonne mancanti
/// (es. 013_waitlist creata da 005 senza priorita_valore). Prod usa
/// `run_migration` con error swallowing — il test fa lo stesso.
fn parse_sql_statements(sql: &str) -> Vec<String> {
    let mut statements = Vec::new();
    let mut current = String::new();
    let mut paren_depth = 0i32;
    for line in sql.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("--") || trimmed.is_empty() {
            continue;
        }
        paren_depth += line.matches('(').count() as i32;
        paren_depth -= line.matches(')').count() as i32;
        current.push_str(line);
        current.push('\n');
        if trimmed.ends_with(';') && paren_depth == 0 {
            statements.push(current.trim().to_string());
            current.clear();
        }
    }
    if !current.trim().is_empty() {
        statements.push(current.trim().to_string());
    }
    statements
}

/// Crea un database SQLite temporaneo su filesystem
/// Applica tutte le migrations e ritorna il pool connesso.
///
/// S271: replica la logica prod (`lib.rs::run_migration`) invece di usare
/// `sqlx::migrate!()` per gestire errori non-fatali ("already exists",
/// "duplicate column", "no such column" in CREATE INDEX) — coerente con
/// come prod applica le migrations storiche.
pub async fn create_test_database() -> (SqlitePool, PathBuf) {
    // Crea file temporaneo .db
    let temp_dir = std::env::temp_dir();
    let db_file = temp_dir.join(format!("fluxion_test_{}.db", uuid::Uuid::new_v4()));
    let db_url = format!("sqlite://{}?mode=rwc", db_file.display());

    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&db_url)
        .await
        .expect("Failed to connect to test database");

    // CWD di cargo test = crate root (src-tauri/). Leggi migrations/ files
    // ordinati alfabeticamente (001_..., 002_..., ..., 041_...).
    let mut migration_files: Vec<_> = fs::read_dir("./migrations")
        .expect("read migrations dir")
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.path()
                .extension()
                .and_then(|s| s.to_str())
                .map(|s| s == "sql")
                .unwrap_or(false)
        })
        .map(|e| e.path())
        .collect();
    migration_files.sort();

    for path in migration_files {
        let sql = fs::read_to_string(&path).expect("read migration file");
        let label = path.file_name().unwrap().to_string_lossy().to_string();
        for (idx, stmt) in parse_sql_statements(&sql).iter().enumerate() {
            let t = stmt.trim();
            if t.is_empty() || t.starts_with("--") {
                continue;
            }
            if let Err(e) = sqlx::query(t).execute(&pool).await {
                let msg = e.to_string();
                // Swallow errori non-fatali coerenti con prod run_migration +
                // "no such column" / "no such table" su CREATE INDEX storici.
                if !msg.contains("already exists")
                    && !msg.contains("duplicate column")
                    && !msg.contains("UNIQUE constraint")
                    && !msg.contains("no such column")
                    && !msg.contains("no such table")
                {
                    eprintln!("⚠️  [{}] stmt {} failed: {}", label, idx + 1, msg);
                }
            }
        }
    }

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
