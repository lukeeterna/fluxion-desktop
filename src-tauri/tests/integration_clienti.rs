// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Clienti (S273)
// PII encryption coverage (S249 11 sensitive fields) + search match
// via internal_* pool-based functions
// ═══════════════════════════════════════════════════════════════════

mod common;

use common::{cleanup_test_database, create_test_database};
use tauri_app_lib::commands::clienti::{
    internal_create_cliente, internal_get_cliente, internal_search_clienti,
    internal_update_cliente, CreateClienteInput, UpdateClienteInput,
};
use tauri_app_lib::encryption::init_encryption_with_salt;

// Deterministic 32-byte salt for integration tests (mirror unit-test pattern in
// encryption.rs). Real installations use a per-installation random salt.
const TEST_SALT: [u8; 32] = [0xCD; 32];

/// Lazy init dell'encryption key globale per la durata del processo di test.
/// ENCRYPTION_KEY è OnceCell: la prima `set` vince, init successive ritornano
/// `Err("Encryption already initialized")` (ignorato qui — `is_encryption_ready`
/// torna true comunque, che è quello che ci serve).
fn setup_test_encryption() {
    let _ = init_encryption_with_salt("test_password_S273", "test_device_S273", &TEST_SALT);
}

fn make_input(
    nome: &str,
    cognome: &str,
    telefono: &str,
    email: Option<&str>,
) -> CreateClienteInput {
    CreateClienteInput {
        nome: nome.to_string(),
        cognome: cognome.to_string(),
        soprannome: None,
        telefono: telefono.to_string(),
        email: email.map(|s| s.to_string()),
        data_nascita: None,
        indirizzo: None,
        cap: None,
        citta: None,
        provincia: None,
        codice_fiscale: None,
        partita_iva: None,
        codice_sdi: None,
        pec: None,
        note: None,
        tags: None,
        fonte: None,
        consenso_marketing: None,
        consenso_whatsapp: None,
    }
}

// ═══════════════════════════════════════════════════════════════════
// PII encryption at-rest — verify ciphertext per i 3 campi più critici
// (nome, telefono, email) + decrypt roundtrip via internal_get_cliente.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_create_cliente_encrypts_pii_at_rest() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let nome_plain = "Mario";
    let cognome_plain = "Rossi";
    let telefono_plain = "3331234567";
    let email_plain = "mario.rossi@example.com";

    let created = internal_create_cliente(
        &pool,
        make_input(nome_plain, cognome_plain, telefono_plain, Some(email_plain)),
    )
    .await
    .expect("create_cliente");

    // Return è già decifrato (internal_create_cliente → internal_get_cliente)
    assert_eq!(created.nome, nome_plain);
    assert_eq!(created.cognome, cognome_plain);
    assert_eq!(created.telefono, telefono_plain);
    assert_eq!(created.email.as_deref(), Some(email_plain));

    // SELECT raw — bypass decrypt — verifica ciphertext at-rest
    let raw: (String, String, String, Option<String>) =
        sqlx::query_as("SELECT nome, cognome, telefono, email FROM clienti WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw");

    let (nome_raw, cognome_raw, telefono_raw, email_raw) = raw;
    let email_raw = email_raw.expect("email not NULL");

    // Ciphertext ≥16 char (nonce + ciphertext + tag Base64), diverso da plaintext.
    assert!(
        nome_raw.len() >= 16,
        "nome ciphertext deve essere ≥16 char, got len={}",
        nome_raw.len()
    );
    assert_ne!(nome_raw, nome_plain, "nome NON deve essere plaintext");
    assert!(
        cognome_raw.len() >= 16,
        "cognome ciphertext deve essere ≥16 char, got len={}",
        cognome_raw.len()
    );
    assert_ne!(
        cognome_raw, cognome_plain,
        "cognome NON deve essere plaintext"
    );
    assert!(
        telefono_raw.len() >= 16,
        "telefono ciphertext deve essere ≥16 char, got len={}",
        telefono_raw.len()
    );
    assert_ne!(
        telefono_raw, telefono_plain,
        "telefono NON deve essere plaintext"
    );
    assert!(
        email_raw.len() >= 16,
        "email ciphertext deve essere ≥16 char, got len={}",
        email_raw.len()
    );
    assert_ne!(email_raw, email_plain, "email NON deve essere plaintext");

    // Roundtrip via internal_get_cliente
    let fetched = internal_get_cliente(&pool, &created.id)
        .await
        .expect("get_cliente");
    assert_eq!(fetched.nome, nome_plain);
    assert_eq!(fetched.cognome, cognome_plain);
    assert_eq!(fetched.telefono, telefono_plain);
    assert_eq!(fetched.email.as_deref(), Some(email_plain));

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Update re-encrypts changed PII fields (different ciphertext per AES-GCM
// random nonce, plaintext roundtrip OK).
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_update_cliente_re_encrypts_changed_fields() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let created = internal_create_cliente(
        &pool,
        make_input("Luigi", "Verdi", "3339999999", Some("luigi@old.com")),
    )
    .await
    .expect("create_cliente");

    // Snapshot ciphertext pre-update
    let ct_before: (String, Option<String>) =
        sqlx::query_as("SELECT telefono, email FROM clienti WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw before");
    let (telefono_ct_before, email_ct_before) = ct_before;
    let email_ct_before = email_ct_before.expect("email not NULL pre-update");

    // Update: cambia telefono + email
    let nuovo_telefono = "3402000000";
    let nuova_email = "luigi@new.com";

    let update_input = UpdateClienteInput {
        id: created.id.clone(),
        nome: created.nome.clone(),
        cognome: created.cognome.clone(),
        soprannome: None,
        telefono: nuovo_telefono.to_string(),
        email: Some(nuova_email.to_string()),
        data_nascita: None,
        indirizzo: None,
        cap: None,
        citta: None,
        provincia: None,
        codice_fiscale: None,
        partita_iva: None,
        codice_sdi: None,
        pec: None,
        note: None,
        tags: None,
        fonte: None,
        consenso_marketing: None,
        consenso_whatsapp: None,
    };

    let (before, after) = internal_update_cliente(&pool, update_input)
        .await
        .expect("update_cliente");

    // cliente_before è snapshot plaintext pre-update
    assert_eq!(before.telefono, "3339999999");
    assert_eq!(before.email.as_deref(), Some("luigi@old.com"));
    // cliente_after riflette i nuovi valori plaintext
    assert_eq!(after.telefono, nuovo_telefono);
    assert_eq!(after.email.as_deref(), Some(nuova_email));

    // Ciphertext post-update DEVE essere diverso da pre-update (plaintext nuovo)
    let ct_after: (String, Option<String>) =
        sqlx::query_as("SELECT telefono, email FROM clienti WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw after");
    let (telefono_ct_after, email_ct_after) = ct_after;
    let email_ct_after = email_ct_after.expect("email not NULL post-update");

    assert_ne!(
        telefono_ct_after, telefono_ct_before,
        "telefono ciphertext deve cambiare dopo update con valore diverso"
    );
    assert_ne!(
        email_ct_after, email_ct_before,
        "email ciphertext deve cambiare dopo update con valore diverso"
    );
    // E comunque NON plaintext
    assert_ne!(telefono_ct_after, nuovo_telefono);
    assert_ne!(email_ct_after, nuova_email);
    assert!(telefono_ct_after.len() >= 16);
    assert!(email_ct_after.len() >= 16);

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Search clienti — tier-1 in-memory post-decryption filter funziona
// (SQL LIKE su ciphertext non matcha — verifica che plaintext match OK).
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_search_clienti_matches_decrypted_plaintext() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    internal_create_cliente(
        &pool,
        make_input("Mario", "Rossi", "3331111111", Some("mario@ex.com")),
    )
    .await
    .expect("create Mario");

    internal_create_cliente(
        &pool,
        make_input("Anna", "Bianchi", "3332222222", Some("anna@ex.com")),
    )
    .await
    .expect("create Anna");

    // Search "mario" → 1 hit
    let results = internal_search_clienti(&pool, "mario")
        .await
        .expect("search mario");
    assert_eq!(results.len(), 1, "search 'mario' deve restituire 1 cliente");
    assert_eq!(results[0].nome, "Mario");
    assert_eq!(results[0].cognome, "Rossi");

    // Search per cognome case-insensitive
    let results = internal_search_clienti(&pool, "BIANCHI")
        .await
        .expect("search BIANCHI");
    assert_eq!(results.len(), 1, "search 'BIANCHI' case-insensitive 1 hit");
    assert_eq!(results[0].nome, "Anna");

    // Search per telefono parziale
    let results = internal_search_clienti(&pool, "3332222")
        .await
        .expect("search telefono");
    assert_eq!(
        results.len(),
        1,
        "search telefono parziale deve matchare plaintext post-decrypt"
    );
    assert_eq!(results[0].telefono, "3332222222");

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Search no-match — query inesistente → 0 risultati (non errore).
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_search_clienti_no_match() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    internal_create_cliente(
        &pool,
        make_input("Mario", "Rossi", "3331111111", Some("mario@ex.com")),
    )
    .await
    .expect("create Mario");

    let results = internal_search_clienti(&pool, "xyz_nonexistent_string")
        .await
        .expect("search xyz");
    assert_eq!(
        results.len(),
        0,
        "query inesistente deve restituire 0 risultati"
    );

    cleanup_test_database(pool, db_file).await;
}
