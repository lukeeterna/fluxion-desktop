// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Fatture (S271)
// Regression test BUG-FATT-3/4/6 via internal_* pool-based functions
// ═══════════════════════════════════════════════════════════════════

mod common;

use common::{cleanup_test_database, create_test_database};
use sqlx::SqlitePool;
use tauri_app_lib::commands::fatture::{
    internal_add_riga_fattura, internal_create_fattura, internal_get_impostazioni_fatturazione,
    internal_save_fattura_xml_to_file, internal_update_impostazioni_fatturazione,
};
use tauri_app_lib::encryption::{encrypt_field, init_encryption_with_salt};

// Deterministic 32-byte salt for integration tests (mirror unit-test pattern
// in encryption.rs). Real installations use a per-installation random salt.
const TEST_SALT: [u8; 32] = [0xAB; 32];

/// Lazy init dell'encryption key globale per la durata del processo di test.
/// ENCRYPTION_KEY è OnceCell: la prima `set` vince, init successive ritornano
/// `Err("Encryption already initialized")` (ignorato qui — `is_encryption_ready`
/// torna true comunque, che è quello che ci serve).
fn setup_test_encryption() {
    let _ = init_encryption_with_salt("test_password_S271", "test_device_S271", &TEST_SALT);
}

/// Cifra e inserisce un cliente di test per chiamate `internal_create_fattura`.
/// I 7 campi PII (nome/cognome/telefono/email/partita_iva/codice_fiscale/indirizzo/pec)
/// sono cifrati con la chiave AES-256-GCM derivata in `setup_test_encryption`.
async fn insert_test_cliente_encrypted(pool: &SqlitePool, id: &str, nome: &str, cognome: &str) {
    let nome_ct = encrypt_field(nome).expect("encrypt nome");
    let cognome_ct = encrypt_field(cognome).expect("encrypt cognome");
    let telefono_ct = encrypt_field("3331234567").expect("encrypt telefono");
    let indirizzo_ct = encrypt_field("Via Test 1").expect("encrypt indirizzo");
    let cap_ct = encrypt_field("85100").expect("encrypt cap");
    let citta_ct = encrypt_field("Potenza").expect("encrypt citta");

    sqlx::query(
        r#"
        INSERT INTO clienti (
            id, nome, cognome, telefono, email,
            partita_iva, codice_fiscale, indirizzo, cap, citta, provincia, pec,
            codice_sdi, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, 'PZ', NULL, '0000000', datetime('now'), datetime('now'))
        "#,
    )
    .bind(id)
    .bind(&nome_ct)
    .bind(&cognome_ct)
    .bind(&telefono_ct)
    .bind(&indirizzo_ct)
    .bind(&cap_ct)
    .bind(&citta_ct)
    .execute(pool)
    .await
    .expect("insert cliente encrypted");
}

/// Imposta impostazioni_fatturazione cifrate (sovrascrive la default seed
/// plaintext lasciata da migration 007). Il regime resta `RF19` (forfettario,
/// nessuna IVA, natura `N2.2`) per coerenza con i seed.
async fn setup_test_impostazioni(pool: &SqlitePool) {
    internal_update_impostazioni_fatturazione(
        pool,
        "Test SRL S271".to_string(),
        "02159940762".to_string(),
        Some("DSTMGN81S12L738L".to_string()),
        "RF19".to_string(),
        "Via Roma 1".to_string(),
        "85100".to_string(),
        "Potenza".to_string(),
        "PZ".to_string(),
        None,
        None,
        None,
        None,
        0.0,
        Some("N2.2".to_string()),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    .await
    .expect("setup impostazioni");
}

// ═══════════════════════════════════════════════════════════════════
// BUG-FATT-3 regression — totale_documento sync dopo add_riga
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_fattura_totale_aggiornato_dopo_add_riga() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;
    setup_test_impostazioni(&pool).await;
    insert_test_cliente_encrypted(&pool, "cli-bugfatt3", "Mario", "Rossi").await;

    // create fattura → no righe → totale 0
    let fattura = internal_create_fattura(
        &pool,
        "cli-bugfatt3".to_string(),
        None,
        "2026-05-20".to_string(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    .await
    .expect("create_fattura");

    assert_eq!(
        fattura.totale_documento, 0.0,
        "fattura appena creata deve avere totale 0"
    );

    // add_riga prezzo_unitario=15.0 quantita=1 → trigger update_fattura_totals
    let _riga = internal_add_riga_fattura(
        &pool,
        fattura.id.clone(),
        "Consulenza S271".to_string(),
        None,
        1.0,
        Some("PZ".to_string()),
        15.0,
        None,
        0.0,
        Some("N2.2".to_string()),
        None,
        None,
    )
    .await
    .expect("add_riga_fattura");

    // re-fetch fattura — backend deve aver propagato totale via internal_update_fattura_totals
    let fattura_aggiornata: tauri_app_lib::commands::fatture::Fattura =
        sqlx::query_as("SELECT * FROM fatture WHERE id = ?")
            .bind(&fattura.id)
            .fetch_one(&pool)
            .await
            .expect("re-fetch fattura");

    assert_eq!(
        fattura_aggiornata.imponibile_totale, 15.0,
        "imponibile_totale deve riflettere prezzo riga (regime forfettario)"
    );
    assert_eq!(
        fattura_aggiornata.iva_totale, 0.0,
        "regime forfettario RF19 → IVA = 0"
    );
    assert_eq!(
        fattura_aggiornata.totale_documento, 15.0,
        "totale_documento deve riflettere riga aggiunta"
    );

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// BUG-FATT-4 regression — telefono in impostazioni_fatturazione encrypted
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_update_impostazioni_telefono_encrypted() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let telefono_plain = "3331234567";

    internal_update_impostazioni_fatturazione(
        &pool,
        "Test SRL".to_string(),
        "02159940762".to_string(),
        Some("DSTMGN81S12L738L".to_string()),
        "RF19".to_string(),
        "Via Test 1".to_string(),
        "85100".to_string(),
        "Potenza".to_string(),
        "PZ".to_string(),
        Some(telefono_plain.to_string()), // <-- telefono PII
        None,
        None,
        None,
        0.0,
        Some("N2.2".to_string()),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    .await
    .expect("update_impostazioni");

    // SELECT raw — bypass decrypt — verifica ciphertext at-rest
    let raw_telefono: Option<String> =
        sqlx::query_scalar("SELECT telefono FROM impostazioni_fatturazione WHERE id = 'default'")
            .fetch_one(&pool)
            .await
            .expect("select raw telefono");
    let raw = raw_telefono.expect("telefono not NULL");

    assert!(
        raw.len() >= 16,
        "telefono ciphertext deve essere ≥16 char (nonce+ciphertext+tag Base64), got len={}",
        raw.len()
    );
    assert_ne!(raw, telefono_plain, "telefono NON deve essere plaintext");

    // Roundtrip: get_impostazioni decifra → torna plaintext
    let imp = internal_get_impostazioni_fatturazione(&pool)
        .await
        .expect("get_impostazioni");
    assert_eq!(
        imp.telefono.as_deref(),
        Some(telefono_plain),
        "decrypt roundtrip telefono"
    );
    assert_eq!(
        imp.denominazione, "Test SRL",
        "decrypt roundtrip denominazione"
    );
    assert_eq!(
        imp.partita_iva, "02159940762",
        "decrypt roundtrip partita_iva"
    );

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// BUG-FATT-6 regression — save XML to file
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_save_fattura_xml_to_file() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;
    setup_test_impostazioni(&pool).await;
    insert_test_cliente_encrypted(&pool, "cli-bugfatt6", "Mario", "Rossi").await;

    let fattura = internal_create_fattura(
        &pool,
        "cli-bugfatt6".to_string(),
        None,
        "2026-05-20".to_string(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    .await
    .expect("create_fattura");

    // Inietta xml_content direttamente (la generazione completa è coperta dal
    // command `emetti_fattura`, fuori scope BUG-FATT-6 che testa il write su FS)
    let xml_payload = "<?xml version=\"1.0\"?><FatturaElettronica><test/></FatturaElettronica>";
    sqlx::query("UPDATE fatture SET xml_content = ? WHERE id = ?")
        .bind(xml_payload)
        .bind(&fattura.id)
        .execute(&pool)
        .await
        .expect("inject xml_content");

    // tempfile path con uuid per evitare race tra test paralleli
    let tmpfile = std::env::temp_dir().join(format!(
        "fluxion_test_xml_{}.xml",
        uuid::Uuid::new_v4()
    ));

    internal_save_fattura_xml_to_file(
        &pool,
        fattura.id.clone(),
        tmpfile.to_string_lossy().to_string(),
    )
    .await
    .expect("save_fattura_xml_to_file");

    assert!(tmpfile.exists(), "file XML deve essere scritto su disco");
    let content = std::fs::read_to_string(&tmpfile).expect("read xml file");
    assert!(
        content.contains("<FatturaElettronica"),
        "xml file content mismatch: {}",
        content
    );

    std::fs::remove_file(&tmpfile).ok();
    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// BUG-FATT-6 edge cases — path validation
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_save_fattura_xml_path_validation() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;
    setup_test_impostazioni(&pool).await;
    insert_test_cliente_encrypted(&pool, "cli-pathval", "Mario", "Rossi").await;

    let fattura = internal_create_fattura(
        &pool,
        "cli-pathval".to_string(),
        None,
        "2026-05-20".to_string(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    .await
    .expect("create_fattura");

    sqlx::query("UPDATE fatture SET xml_content = '<x/>' WHERE id = ?")
        .bind(&fattura.id)
        .execute(&pool)
        .await
        .expect("inject xml");

    // Path senza .xml → reject
    let bad_ext = std::env::temp_dir().join("test_no_ext.txt");
    let r = internal_save_fattura_xml_to_file(
        &pool,
        fattura.id.clone(),
        bad_ext.to_string_lossy().to_string(),
    )
    .await;
    assert!(r.is_err(), "path senza estensione .xml deve fallire");
    assert!(
        r.unwrap_err().contains(".xml"),
        "error message deve menzionare .xml"
    );

    // Path con parent dir inesistente → reject
    let bad_parent = "/nonexistent_dir_xyz_S271/out.xml";
    let r = internal_save_fattura_xml_to_file(
        &pool,
        fattura.id.clone(),
        bad_parent.to_string(),
    )
    .await;
    assert!(r.is_err(), "parent dir inesistente deve fallire");

    cleanup_test_database(pool, db_file).await;
}
