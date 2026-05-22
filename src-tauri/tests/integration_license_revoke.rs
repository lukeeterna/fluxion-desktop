// ═══════════════════════════════════════════════════════════════════
// FLUXION — Integration tests S280 Track A
// Phone-home status sync: revoked/expired propagation from CF Worker
// response → license_cache SQLite DB.
//
// Chiude il gap S279: il Worker ora ritorna `status='revoked'` per
// purchase con refunded=true (phone-home.ts:46-54), ma il client
// frontend cachava solo in localStorage (volatile, clearabile).
// S280 persiste lo status in DB così che get_license_status_ed25519
// veda is_valid=false (per via del match status="revoked" => _ => false
// a license_ed25519.rs:523-534) e tutti i gating feature/vertical
// rifiutino correttamente l'accesso.
// ═══════════════════════════════════════════════════════════════════

mod common;

use common::{cleanup_test_database, create_test_database};
use tauri_app_lib::commands::license_ed25519::internal_sync_license_status_from_phone_home;
use sqlx::{Row, SqlitePool};

/// Seed singleton license_cache (id=1) con stato attivo Pro.
/// Necessario perché tabella ha CHECK(id=1) e fingerprint NOT NULL.
async fn seed_active_pro_license(pool: &SqlitePool) {
    sqlx::query(
        r#"
        INSERT INTO license_cache (id, fingerprint, tier, status, last_validated_at)
        VALUES (1, 'test-fingerprint-sha256', 'pro', 'active', datetime('now', '-7 days'))
        "#,
    )
    .execute(pool)
    .await
    .expect("seed license_cache");
}

/// Leggi (status, tier, last_validated_at) dalla row singleton.
async fn read_row(pool: &SqlitePool) -> (String, String, Option<String>) {
    let row = sqlx::query("SELECT status, tier, last_validated_at FROM license_cache WHERE id = 1")
        .fetch_one(pool)
        .await
        .expect("select license_cache");
    (
        row.get::<String, _>("status"),
        row.get::<String, _>("tier"),
        row.get::<Option<String>, _>("last_validated_at"),
    )
}

#[tokio::test]
async fn test_sync_revoked_persists_status_and_tier_to_db() {
    let (pool, db_file) = create_test_database().await;
    seed_active_pro_license(&pool).await;

    let (status_before, tier_before, ts_before) = read_row(&pool).await;
    assert_eq!(status_before, "active");
    assert_eq!(tier_before, "pro");
    assert!(ts_before.is_some());

    internal_sync_license_status_from_phone_home(&pool, "revoked", "expired")
        .await
        .expect("sync revoked");

    let (status_after, tier_after, ts_after) = read_row(&pool).await;
    assert_eq!(
        status_after, "revoked",
        "status deve essere persistito come 'revoked' in license_cache"
    );
    assert_eq!(
        tier_after, "expired",
        "tier deve essere 'expired' dopo revoke (allinea Worker phone-home response)"
    );
    assert!(
        ts_after.is_some() && ts_after != ts_before,
        "last_validated_at deve essere aggiornato per audit trail"
    );

    cleanup_test_database(pool, db_file).await;
}

#[tokio::test]
async fn test_sync_ok_is_noop_for_status_tier_but_updates_audit_timestamp() {
    let (pool, db_file) = create_test_database().await;
    seed_active_pro_license(&pool).await;

    let (_, _, ts_before) = read_row(&pool).await;

    // Sleep minimo per garantire datetime('now') incrementato (resolution 1s SQLite).
    tokio::time::sleep(std::time::Duration::from_millis(1100)).await;

    internal_sync_license_status_from_phone_home(&pool, "ok", "pro")
        .await
        .expect("sync ok");

    let (status_after, tier_after, ts_after) = read_row(&pool).await;
    assert_eq!(
        status_after, "active",
        "status='ok' dal Worker NON deve sovrascrivere status='active' locale (firma Ed25519 autorevole)"
    );
    assert_eq!(tier_after, "pro", "tier preservato su status='ok'");
    assert!(
        ts_after != ts_before,
        "last_validated_at deve avanzare anche su status='ok' (audit health-check)"
    );

    cleanup_test_database(pool, db_file).await;
}

#[tokio::test]
async fn test_sync_rejects_invalid_status_string() {
    let (pool, db_file) = create_test_database().await;
    seed_active_pro_license(&pool).await;

    let result =
        internal_sync_license_status_from_phone_home(&pool, "garbage-from-fe", "pro").await;
    assert!(result.is_err(), "status non-whitelist deve ritornare Err");
    assert!(
        result.unwrap_err().contains("Invalid phone-home status"),
        "messaggio errore deve identificare la causa"
    );

    // DB intatto dopo Err: nessuna scrittura parziale.
    let (status_after, tier_after, _) = read_row(&pool).await;
    assert_eq!(status_after, "active");
    assert_eq!(tier_after, "pro");

    cleanup_test_database(pool, db_file).await;
}

#[tokio::test]
async fn test_sync_revoked_is_idempotent() {
    let (pool, db_file) = create_test_database().await;
    seed_active_pro_license(&pool).await;

    // Prima chiamata: active → revoked
    internal_sync_license_status_from_phone_home(&pool, "revoked", "expired")
        .await
        .expect("first sync revoked");

    let (status1, tier1, _) = read_row(&pool).await;
    assert_eq!(status1, "revoked");
    assert_eq!(tier1, "expired");

    // Seconda chiamata: stesso payload, no error, stato finale identico
    internal_sync_license_status_from_phone_home(&pool, "revoked", "expired")
        .await
        .expect("second sync revoked (idempotency)");

    let (status2, tier2, _) = read_row(&pool).await;
    assert_eq!(status2, "revoked", "stato terminale stabile su replay");
    assert_eq!(tier2, "expired");

    cleanup_test_database(pool, db_file).await;
}

#[tokio::test]
async fn test_sync_expired_and_invalid_also_propagate() {
    let (pool, db_file) = create_test_database().await;
    seed_active_pro_license(&pool).await;

    // 'expired' (Sara trial scaduto su tier Base, scenario phone-home.ts:67-77)
    internal_sync_license_status_from_phone_home(&pool, "expired", "base")
        .await
        .expect("sync expired");
    let (s, t, _) = read_row(&pool).await;
    assert_eq!(s, "expired");
    assert_eq!(t, "base");

    // 'invalid' (license corrotta lato Worker)
    internal_sync_license_status_from_phone_home(&pool, "invalid", "none")
        .await
        .expect("sync invalid");
    let (s, t, _) = read_row(&pool).await;
    assert_eq!(s, "invalid");
    assert_eq!(t, "none");

    cleanup_test_database(pool, db_file).await;
}
