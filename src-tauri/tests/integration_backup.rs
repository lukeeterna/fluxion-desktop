// ═══════════════════════════════════════════════════════════════════
// FLUXION S278 — Integration Tests Backup/Restore (B-5 Gate 1)
//
// Copre ROADMAP_S183_S190.md SPRINT S184 Step 4-5-6:
//   Step 4 (1.5h): backup integrity (SHA256 pre/post) + WAL checkpoint
//   Step 5 (1.0h): restore round-trip (modifica DB → backup → restore → assert)
//   Step 6 (1.5h): concurrent backup mentre app scrive + corrupted DB recovery
//
// Pattern: replica S271/S273/S275 — pool+tempdir reali, no Tauri AppHandle.
// Usa `internal_backup_database` / `internal_restore_database` (pool/path-based).
// ═══════════════════════════════════════════════════════════════════

mod common;

use common::{cleanup_test_database, create_test_database, insert_test_cliente};
use sha2::{Digest, Sha256};
use sqlx::sqlite::SqlitePoolOptions;
use sqlx::{Row, SqlitePool};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Duration;
use tauri_app_lib::commands::support::{internal_backup_database, internal_restore_database};
use tokio::sync::Notify;

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

/// Compute SHA256 hex digest of a file's raw bytes.
fn sha256_file(path: &Path) -> String {
    let bytes = fs::read(path).expect("read file for hashing");
    let mut hasher = Sha256::new();
    hasher.update(&bytes);
    format!("{:x}", hasher.finalize())
}

/// Compute SHA256 hex digest of a canonical row dump (id|nome|cognome).
/// Robusto a non-determinism del file SQLite (header counters, freelist).
async fn sha256_clienti_canonical(pool: &SqlitePool) -> String {
    let rows = sqlx::query("SELECT id, nome, cognome FROM clienti ORDER BY id")
        .fetch_all(pool)
        .await
        .expect("dump clienti");
    let mut hasher = Sha256::new();
    for r in &rows {
        let id: String = r.get("id");
        let nome: String = r.get("nome");
        let cognome: String = r.get("cognome");
        hasher.update(format!("{}|{}|{}\n", id, nome, cognome).as_bytes());
    }
    format!("{:x}", hasher.finalize())
}

/// Open new pool on file path (per re-attach post-restore).
async fn open_pool(db_path: &Path) -> SqlitePool {
    let url = format!("sqlite://{}?mode=rwc", db_path.display());
    SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&url)
        .await
        .expect("open pool on db file")
}

/// Cleanup helper: rimuove file backup/emergency residui.
fn cleanup_files(paths: &[PathBuf]) {
    for p in paths {
        if p.exists() {
            let _ = fs::remove_file(p);
        }
    }
}

// ───────────────────────────────────────────────────────────────────
// STEP 4 — Backup integrity (SHA256 pre/post) + WAL checkpoint
// ───────────────────────────────────────────────────────────────────

/// Step 4-A: backup produce file SQLite valido con dati identici alla sorgente.
/// Assert: backup_path esiste, size > 0, sha256(canonical_rows) sorgente == backup.
#[tokio::test]
async fn test_backup_creates_valid_sqlite_with_identical_data() {
    let (pool, db_path) = create_test_database().await;
    insert_test_cliente(&pool, "cli-bkp-1", "Mario", "Rossi").await;
    insert_test_cliente(&pool, "cli-bkp-2", "Luigi", "Verdi").await;
    insert_test_cliente(&pool, "cli-bkp-3", "Giuseppe", "Bianchi").await;

    let source_hash = sha256_clienti_canonical(&pool).await;

    // Backup in tempdir dedicato
    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let result = internal_backup_database(&pool, &backup_dir)
        .await
        .expect("backup should succeed");

    let backup_path = PathBuf::from(&result.path);

    // Assertions Step 4-A
    assert!(backup_path.exists(), "backup file deve esistere");
    assert!(result.size_bytes > 0, "backup size deve essere > 0");
    assert!(
        backup_path.to_string_lossy().ends_with(".db"),
        "backup deve avere estensione .db"
    );

    // Verifica dati identici aprendo il backup come pool indipendente
    let backup_pool = open_pool(&backup_path).await;
    let backup_hash = sha256_clienti_canonical(&backup_pool).await;
    assert_eq!(
        source_hash, backup_hash,
        "SHA256 dei dati canonical sorgente == backup"
    );

    backup_pool.close().await;
    cleanup_files(&[backup_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    cleanup_test_database(pool, db_path).await;
}

/// Step 4-B: backup include dati WAL non-checkpointed.
/// Setup: PRAGMA journal_mode=WAL, scrivi righe (queste vivranno in -wal),
/// backup IMMEDIATO senza wal_checkpoint manuale → backup deve contenere le righe.
/// VACUUM INTO esegue checkpoint implicito.
#[tokio::test]
async fn test_backup_includes_uncheckpointed_wal_data() {
    let (pool, db_path) = create_test_database().await;

    // Abilita WAL mode (prod default da lib.rs:208)
    sqlx::query("PRAGMA journal_mode=WAL")
        .execute(&pool)
        .await
        .expect("enable WAL");

    // Insert righe (finiranno in -wal sidecar prima del checkpoint automatico)
    insert_test_cliente(&pool, "cli-wal-1", "Anna", "Neri").await;
    insert_test_cliente(&pool, "cli-wal-2", "Carlo", "Gialli").await;

    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let result = internal_backup_database(&pool, &backup_dir)
        .await
        .expect("backup with WAL should succeed");

    let backup_path = PathBuf::from(&result.path);

    // Apri backup e verifica entrambe le righe presenti (WAL incluso)
    let backup_pool = open_pool(&backup_path).await;
    let count: i64 =
        sqlx::query_scalar("SELECT COUNT(*) FROM clienti WHERE id IN ('cli-wal-1', 'cli-wal-2')")
            .fetch_one(&backup_pool)
            .await
            .expect("count clienti");
    assert_eq!(count, 2, "backup deve contenere righe WAL pre-checkpoint");

    backup_pool.close().await;
    cleanup_files(&[backup_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    cleanup_test_database(pool, db_path).await;
}

// ───────────────────────────────────────────────────────────────────
// STEP 5 — Restore round-trip
// ───────────────────────────────────────────────────────────────────

/// Step 5-A: round-trip backup→modify→restore preserva dati pre-backup.
/// Setup: insert 2 clienti → backup → insert 3° cliente → restore → assert 2 righe (terza scomparsa).
/// Hash canonical pre-backup == hash post-restore.
#[tokio::test]
async fn test_restore_round_trip_preserves_pre_backup_state() {
    let (pool, db_path) = create_test_database().await;
    insert_test_cliente(&pool, "cli-rt-1", "Alfa", "Uno").await;
    insert_test_cliente(&pool, "cli-rt-2", "Beta", "Due").await;

    let pre_backup_hash = sha256_clienti_canonical(&pool).await;

    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let backup_result = internal_backup_database(&pool, &backup_dir)
        .await
        .expect("backup");
    let backup_path = PathBuf::from(&backup_result.path);

    // Modifica post-backup: aggiungi un 3° cliente
    insert_test_cliente(&pool, "cli-rt-3", "Gamma", "Tre").await;
    let post_modify_hash = sha256_clienti_canonical(&pool).await;
    assert_ne!(
        pre_backup_hash, post_modify_hash,
        "hash deve cambiare dopo insert"
    );

    // Chiudi pool prima del restore (fs::copy non può sovrascrivere file aperto su Windows;
    // su Unix SQLite WAL pool va comunque chiuso per evitare cache stale).
    pool.close().await;

    // Restore: copia backup su db_path
    let emergency_dir = std::env::temp_dir().join(format!("fluxion_em_{}", uuid::Uuid::new_v4()));
    fs::create_dir_all(&emergency_dir).expect("mkdir emergency");
    internal_restore_database(&backup_path, &db_path, &emergency_dir).expect("restore");

    // Riapri pool sul DB ripristinato e verifica
    let restored_pool = open_pool(&db_path).await;
    let post_restore_hash = sha256_clienti_canonical(&restored_pool).await;
    assert_eq!(
        pre_backup_hash, post_restore_hash,
        "hash canonical post-restore == pre-backup (terzo cliente sparito)"
    );
    let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM clienti WHERE id LIKE 'cli-rt-%'")
        .fetch_one(&restored_pool)
        .await
        .expect("count");
    assert_eq!(count, 2, "solo 2 righe pre-backup, non 3");

    restored_pool.close().await;
    cleanup_files(&[backup_path, db_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    let _ = fs::remove_dir_all(&emergency_dir);
}

/// Step 5-B: restore crea emergency backup del DB corrente prima di sovrascriverlo.
/// Assert: dopo restore esiste file fluxion_emergency_*.db in emergency_dir,
/// e quel file contiene i dati pre-restore (la modifica che andremo a perdere).
#[tokio::test]
async fn test_restore_creates_emergency_backup_of_current_db() {
    let (pool, db_path) = create_test_database().await;
    insert_test_cliente(&pool, "cli-em-1", "Pre", "Backup").await;

    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let backup_result = internal_backup_database(&pool, &backup_dir)
        .await
        .expect("backup");
    let backup_path = PathBuf::from(&backup_result.path);

    // Modifica per distinguere DB corrente dal backup
    insert_test_cliente(&pool, "cli-em-2", "Post", "Backup").await;
    let pre_restore_hash = sha256_clienti_canonical(&pool).await;
    pool.close().await;

    let emergency_dir = std::env::temp_dir().join(format!("fluxion_em_{}", uuid::Uuid::new_v4()));
    fs::create_dir_all(&emergency_dir).expect("mkdir emergency");

    internal_restore_database(&backup_path, &db_path, &emergency_dir).expect("restore");

    // Trova il file emergency creato
    let emergency_files: Vec<PathBuf> = fs::read_dir(&emergency_dir)
        .expect("read emergency dir")
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .and_then(|n| n.to_str())
                .map(|n| n.starts_with("fluxion_emergency_"))
                .unwrap_or(false)
        })
        .collect();
    assert_eq!(
        emergency_files.len(),
        1,
        "deve esistere esattamente 1 emergency backup"
    );

    // Verifica che emergency contenga i dati PRE-restore (entrambe le righe)
    let em_pool = open_pool(&emergency_files[0]).await;
    let em_hash = sha256_clienti_canonical(&em_pool).await;
    assert_eq!(
        pre_restore_hash, em_hash,
        "emergency backup deve catturare stato DB pre-restore"
    );
    em_pool.close().await;

    cleanup_files(&[backup_path, db_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    let _ = fs::remove_dir_all(&emergency_dir);
}

// ───────────────────────────────────────────────────────────────────
// STEP 6 — Concurrent backup + corrupted DB recovery
// ───────────────────────────────────────────────────────────────────

/// Step 6-A: backup concorrente a scritture non corrompe il file.
/// Setup: WAL mode + Arc<SqlitePool>. Spawn task writer che inserisce in loop
/// mentre eseguiamo backup. Assert: backup file valido, schema integro,
/// almeno le righe pre-spawn presenti (snapshot consistency).
#[tokio::test]
async fn test_concurrent_writes_during_backup_produces_valid_file() {
    let (pool, db_path) = create_test_database().await;
    sqlx::query("PRAGMA journal_mode=WAL")
        .execute(&pool)
        .await
        .expect("enable WAL");

    // Pre-spawn: 5 righe garantite nel backup snapshot
    for i in 0..5 {
        insert_test_cliente(&pool, &format!("cli-pre-{}", i), "Pre", "Spawn").await;
    }

    let pool_arc = Arc::new(pool);
    let stop = Arc::new(Notify::new());

    // Writer task: continua a inserire finché stop non viene notificato
    let writer_pool = Arc::clone(&pool_arc);
    let writer_stop = Arc::clone(&stop);
    let writer = tokio::spawn(async move {
        let mut i = 0u32;
        loop {
            tokio::select! {
                _ = writer_stop.notified() => break i,
                _ = tokio::time::sleep(Duration::from_millis(5)) => {
                    let id = format!("cli-conc-{}", i);
                    let _ = sqlx::query(
                        "INSERT INTO clienti (id, nome, cognome, telefono, email, created_at, updated_at) \
                         VALUES (?, 'Conc', 'Writer', '3331234567', 't@e.com', datetime('now'), datetime('now'))"
                    )
                    .bind(&id)
                    .execute(&*writer_pool)
                    .await;
                    i += 1;
                }
            }
        }
    });

    // Lascia partire qualche INSERT prima del backup
    tokio::time::sleep(Duration::from_millis(50)).await;

    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let backup_result = internal_backup_database(&pool_arc, &backup_dir)
        .await
        .expect("backup concorrente succeeds");

    let backup_path = PathBuf::from(&backup_result.path);

    // Stop writer
    stop.notify_one();
    let inserted = writer.await.expect("writer task");
    eprintln!("writer ha inserito {} righe durante il backup", inserted);

    // Verifica backup integro: apri come pool, COUNT(*), ≥5 righe pre-spawn presenti
    let backup_pool = open_pool(&backup_path).await;

    // Integrity check SQLite ufficiale
    let integrity: String = sqlx::query_scalar("PRAGMA integrity_check")
        .fetch_one(&backup_pool)
        .await
        .expect("integrity_check");
    assert_eq!(
        integrity, "ok",
        "PRAGMA integrity_check deve essere 'ok' su backup concorrente"
    );

    let pre_count: i64 =
        sqlx::query_scalar("SELECT COUNT(*) FROM clienti WHERE id LIKE 'cli-pre-%'")
            .fetch_one(&backup_pool)
            .await
            .expect("count pre");
    assert_eq!(pre_count, 5, "5 righe pre-spawn devono essere nel backup");

    // Le righe concurrent possono essere 0..=N a seconda dello snapshot — non assert preciso,
    // ma assert che lo schema sia integro e nessun garbage
    let conc_count: i64 =
        sqlx::query_scalar("SELECT COUNT(*) FROM clienti WHERE id LIKE 'cli-conc-%'")
            .fetch_one(&backup_pool)
            .await
            .expect("count conc");
    eprintln!("backup snapshot contiene {} righe concurrent", conc_count);
    assert!(
        conc_count >= 0 && conc_count <= inserted as i64,
        "righe conc nel backup ({}) devono essere ≤ inserted ({})",
        conc_count,
        inserted
    );

    backup_pool.close().await;

    let pool_inner = Arc::try_unwrap(pool_arc).unwrap_or_else(|arc| (*arc).clone());
    pool_inner.close().await;
    cleanup_files(&[backup_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    if db_path.exists() {
        let _ = fs::remove_file(&db_path);
    }
}

/// Step 6-B: DB principale corrotto → restore da backup valido recupera DB leggibile.
/// Setup: insert dati, backup, corrompi DB (sovrascrivi primi 1024 bytes con garbage),
/// verifica che pool fail su query → close pool → restore → riapri → verifica dati intatti.
#[tokio::test]
async fn test_corrupted_db_recovered_via_restore() {
    let (pool, db_path) = create_test_database().await;
    insert_test_cliente(&pool, "cli-corr-1", "Pre", "Corruption").await;
    insert_test_cliente(&pool, "cli-corr-2", "Pre", "Corruption").await;

    let pre_corrupt_hash = sha256_clienti_canonical(&pool).await;
    let pre_corrupt_size = fs::metadata(&db_path).map(|m| m.len()).unwrap_or(0);
    assert!(
        pre_corrupt_size > 1024,
        "DB deve avere ≥1KB di header+pagine"
    );

    // Backup PRIMA della corruzione
    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let backup_result = internal_backup_database(&pool, &backup_dir)
        .await
        .expect("backup pre-corruption");
    let backup_path = PathBuf::from(&backup_result.path);

    // Chiudi pool prima di corrompere (rilascia file lock)
    pool.close().await;

    // Corrompi i primi 1024 bytes del DB (SQLite header magic = primi 16 bytes)
    let garbage = vec![0xDEu8; 1024];
    {
        use std::io::{Seek, SeekFrom, Write};
        let mut f = fs::OpenOptions::new()
            .write(true)
            .open(&db_path)
            .expect("open db for corruption");
        f.seek(SeekFrom::Start(0)).expect("seek");
        f.write_all(&garbage).expect("write garbage");
        f.sync_all().expect("sync");
    }

    // Verifica corruzione: aprire pool e query → deve fallire
    let corrupted_pool_url = format!("sqlite://{}?mode=rw", db_path.display());
    let corrupted_attempt = SqlitePoolOptions::new()
        .max_connections(1)
        .connect(&corrupted_pool_url)
        .await;
    if let Ok(pp) = corrupted_attempt {
        let q: Result<i64, _> = sqlx::query_scalar("SELECT COUNT(*) FROM clienti")
            .fetch_one(&pp)
            .await;
        assert!(q.is_err(), "query su DB corrotto deve fallire");
        pp.close().await;
    }
    // (Se il connect stesso fallisce è anche un valido segnale di corruzione)

    // Restore da backup
    let emergency_dir = std::env::temp_dir().join(format!("fluxion_em_{}", uuid::Uuid::new_v4()));
    fs::create_dir_all(&emergency_dir).expect("mkdir emergency");
    internal_restore_database(&backup_path, &db_path, &emergency_dir).expect("restore");

    // Riapri DB → dati devono essere intatti
    let restored_pool = open_pool(&db_path).await;
    let restored_hash = sha256_clienti_canonical(&restored_pool).await;
    assert_eq!(
        pre_corrupt_hash, restored_hash,
        "hash post-restore == pre-corruption (recovery completo)"
    );
    let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM clienti WHERE id LIKE 'cli-corr-%'")
        .fetch_one(&restored_pool)
        .await
        .expect("count");
    assert_eq!(count, 2, "entrambe le righe recuperate via restore");

    // Bonus: integrity_check su DB ripristinato
    let integrity: String = sqlx::query_scalar("PRAGMA integrity_check")
        .fetch_one(&restored_pool)
        .await
        .expect("integrity_check post-restore");
    assert_eq!(integrity, "ok", "integrity_check post-restore == ok");

    restored_pool.close().await;
    cleanup_files(&[backup_path, db_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    let _ = fs::remove_dir_all(&emergency_dir);
}

// ───────────────────────────────────────────────────────────────────
// Bonus: SHA256 file-level del backup è stabile cross-read
// (anti-regression: verifica che `sha256_file` helper sia deterministico)
// ───────────────────────────────────────────────────────────────────

#[tokio::test]
async fn test_backup_file_sha256_stable_across_reads() {
    let (pool, db_path) = create_test_database().await;
    insert_test_cliente(&pool, "cli-stab-1", "Stable", "Hash").await;

    let backup_dir =
        std::env::temp_dir().join(format!("fluxion_bkp_test_{}", uuid::Uuid::new_v4()));
    let result = internal_backup_database(&pool, &backup_dir)
        .await
        .expect("backup");
    let backup_path = PathBuf::from(&result.path);

    // Stesso file letto 3 volte deve produrre stesso hash (file-level determinism)
    let h1 = sha256_file(&backup_path);
    let h2 = sha256_file(&backup_path);
    let h3 = sha256_file(&backup_path);
    assert_eq!(h1, h2, "SHA256 letture ripetute identico (1==2)");
    assert_eq!(h2, h3, "SHA256 letture ripetute identico (2==3)");
    assert_eq!(h1.len(), 64, "SHA256 hex digest = 64 char");

    cleanup_files(&[backup_path]);
    let _ = fs::remove_dir_all(&backup_dir);
    cleanup_test_database(pool, db_path).await;
}
