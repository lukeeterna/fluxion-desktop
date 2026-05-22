// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Operatori (S274)
// PII encryption coverage (S255 4 sensitive fields) + partial-update
// merge semantics via internal_* pool-based functions.
//
// Pattern: mirror di tests/integration_clienti.rs (S273). Operatori ha
// PII subset (nome/cognome required, email/telefono opt) e nessuna search
// command, quindi 4 test: at-rest encrypt, update re-encrypt, get roundtrip,
// partial-update preserva campi None.
// ═══════════════════════════════════════════════════════════════════

mod common;

use common::{cleanup_test_database, create_test_database};
use tauri_app_lib::commands::operatori::{
    internal_create_operatore, internal_get_operatore, internal_update_operatore,
    CreateOperatoreInput, UpdateOperatoreInput,
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
    let _ = init_encryption_with_salt("test_password_S274", "test_device_S274", &TEST_SALT);
}

fn make_input(
    nome: &str,
    cognome: &str,
    email: Option<&str>,
    telefono: Option<&str>,
) -> CreateOperatoreInput {
    CreateOperatoreInput {
        nome: nome.to_string(),
        cognome: cognome.to_string(),
        email: email.map(|s| s.to_string()),
        telefono: telefono.map(|s| s.to_string()),
        ruolo: None,
        colore: None,
        avatar_url: None,
        attivo: None,
        genere: None,
    }
}

// ═══════════════════════════════════════════════════════════════════
// PII encryption at-rest — verify ciphertext per i 4 campi PII
// (nome, cognome, email, telefono) + decrypt roundtrip via
// internal_get_operatore.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_create_operatore_encrypts_pii_at_rest() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let nome_plain = "Giulia";
    let cognome_plain = "Esposito";
    let email_plain = "giulia.esposito@example.com";
    let telefono_plain = "3398765432";

    let created = internal_create_operatore(
        &pool,
        make_input(
            nome_plain,
            cognome_plain,
            Some(email_plain),
            Some(telefono_plain),
        ),
    )
    .await
    .expect("create_operatore");

    // Return è già decifrato (internal_create_operatore → internal_get_operatore)
    assert_eq!(created.nome, nome_plain);
    assert_eq!(created.cognome, cognome_plain);
    assert_eq!(created.email.as_deref(), Some(email_plain));
    assert_eq!(created.telefono.as_deref(), Some(telefono_plain));

    // SELECT raw — bypass decrypt — verifica ciphertext at-rest
    let raw: (String, String, Option<String>, Option<String>) =
        sqlx::query_as("SELECT nome, cognome, email, telefono FROM operatori WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw");

    let (nome_raw, cognome_raw, email_raw, telefono_raw) = raw;
    let email_raw = email_raw.expect("email not NULL");
    let telefono_raw = telefono_raw.expect("telefono not NULL");

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
        email_raw.len() >= 16,
        "email ciphertext deve essere ≥16 char, got len={}",
        email_raw.len()
    );
    assert_ne!(email_raw, email_plain, "email NON deve essere plaintext");
    assert!(
        telefono_raw.len() >= 16,
        "telefono ciphertext deve essere ≥16 char, got len={}",
        telefono_raw.len()
    );
    assert_ne!(
        telefono_raw, telefono_plain,
        "telefono NON deve essere plaintext"
    );

    // Roundtrip via internal_get_operatore
    let fetched = internal_get_operatore(&pool, &created.id)
        .await
        .expect("get_operatore");
    assert_eq!(fetched.nome, nome_plain);
    assert_eq!(fetched.cognome, cognome_plain);
    assert_eq!(fetched.email.as_deref(), Some(email_plain));
    assert_eq!(fetched.telefono.as_deref(), Some(telefono_plain));

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Update re-encrypts changed PII fields (different ciphertext per AES-GCM
// random nonce + plaintext roundtrip OK).
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_update_operatore_re_encrypts_changed_fields() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let created = internal_create_operatore(
        &pool,
        make_input(
            "Marco",
            "Bianchi",
            Some("marco@old.com"),
            Some("3331111111"),
        ),
    )
    .await
    .expect("create_operatore");

    // Snapshot ciphertext pre-update
    let ct_before: (Option<String>, Option<String>) =
        sqlx::query_as("SELECT email, telefono FROM operatori WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw before");
    let (email_ct_before, telefono_ct_before) = ct_before;
    let email_ct_before = email_ct_before.expect("email not NULL pre-update");
    let telefono_ct_before = telefono_ct_before.expect("telefono not NULL pre-update");

    // Update: cambia email + telefono
    let nuova_email = "marco@new.com";
    let nuovo_telefono = "3402000000";

    let update_input = UpdateOperatoreInput {
        nome: None, // preserve current
        cognome: None,
        email: Some(nuova_email.to_string()),
        telefono: Some(nuovo_telefono.to_string()),
        ruolo: None,
        colore: None,
        avatar_url: None,
        attivo: None,
        genere: None,
    };

    let updated = internal_update_operatore(&pool, &created.id, update_input)
        .await
        .expect("update_operatore");

    // Return plaintext riflette i nuovi valori
    assert_eq!(updated.email.as_deref(), Some(nuova_email));
    assert_eq!(updated.telefono.as_deref(), Some(nuovo_telefono));
    // Nome/cognome NON cambiati (input.nome=None → preserva current)
    assert_eq!(updated.nome, "Marco");
    assert_eq!(updated.cognome, "Bianchi");

    // Ciphertext post-update DEVE essere diverso da pre-update (plaintext nuovo)
    let ct_after: (Option<String>, Option<String>) =
        sqlx::query_as("SELECT email, telefono FROM operatori WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw after");
    let (email_ct_after, telefono_ct_after) = ct_after;
    let email_ct_after = email_ct_after.expect("email not NULL post-update");
    let telefono_ct_after = telefono_ct_after.expect("telefono not NULL post-update");

    assert_ne!(
        email_ct_after, email_ct_before,
        "email ciphertext deve cambiare dopo update con valore diverso"
    );
    assert_ne!(
        telefono_ct_after, telefono_ct_before,
        "telefono ciphertext deve cambiare dopo update con valore diverso"
    );
    // E comunque NON plaintext
    assert_ne!(email_ct_after, nuova_email);
    assert_ne!(telefono_ct_after, nuovo_telefono);
    assert!(email_ct_after.len() >= 16);
    assert!(telefono_ct_after.len() >= 16);

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// internal_get_operatore decifra correttamente i 4 campi PII anche con
// email/telefono = None (Option pass-through).
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_get_operatore_decrypts_with_optional_fields_none() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    // Crea operatore con email + telefono = None
    let created = internal_create_operatore(&pool, make_input("Anna", "Verdi", None, None))
        .await
        .expect("create_operatore");

    assert_eq!(created.email, None);
    assert_eq!(created.telefono, None);

    // Verifica raw che nome/cognome sono cifrati comunque
    let raw: (String, String, Option<String>, Option<String>) =
        sqlx::query_as("SELECT nome, cognome, email, telefono FROM operatori WHERE id = ?")
            .bind(&created.id)
            .fetch_one(&pool)
            .await
            .expect("select raw");
    let (nome_raw, cognome_raw, email_raw, telefono_raw) = raw;

    assert!(nome_raw.len() >= 16, "nome cifrato anche con opt None");
    assert!(
        cognome_raw.len() >= 16,
        "cognome cifrato anche con opt None"
    );
    assert_ne!(nome_raw, "Anna");
    assert_ne!(cognome_raw, "Verdi");
    assert_eq!(email_raw, None, "email rimane NULL");
    assert_eq!(telefono_raw, None, "telefono rimane NULL");

    // Roundtrip
    let fetched = internal_get_operatore(&pool, &created.id)
        .await
        .expect("get_operatore");
    assert_eq!(fetched.nome, "Anna");
    assert_eq!(fetched.cognome, "Verdi");
    assert_eq!(fetched.email, None);
    assert_eq!(fetched.telefono, None);

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Partial update merge semantics — UpdateOperatoreInput ha tutti i campi
// Option; campi None devono PRESERVARE il valore corrente (no overwrite
// con NULL/empty). Regression critica per encryption: se merge fallisce,
// il campo viene ri-cifrato come empty/empty-string e perdiamo il dato.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_update_operatore_partial_input_preserves_unchanged_fields() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let created = internal_create_operatore(
        &pool,
        make_input(
            "Sofia",
            "Russo",
            Some("sofia@original.com"),
            Some("3479998888"),
        ),
    )
    .await
    .expect("create_operatore");

    // Update SOLO ruolo (input.nome/cognome/email/telefono = None)
    let update_input = UpdateOperatoreInput {
        nome: None,
        cognome: None,
        email: None,
        telefono: None,
        ruolo: Some("admin".to_string()),
        colore: None,
        avatar_url: None,
        attivo: None,
        genere: None,
    };

    let updated = internal_update_operatore(&pool, &created.id, update_input)
        .await
        .expect("update_operatore partial");

    // I 4 campi PII devono essere preservati identici al create
    assert_eq!(updated.nome, "Sofia", "nome preservato (input None)");
    assert_eq!(updated.cognome, "Russo", "cognome preservato (input None)");
    assert_eq!(
        updated.email.as_deref(),
        Some("sofia@original.com"),
        "email preservata (input None)"
    );
    assert_eq!(
        updated.telefono.as_deref(),
        Some("3479998888"),
        "telefono preservato (input None)"
    );
    // Solo ruolo è cambiato
    assert_eq!(updated.ruolo, "admin");

    // Roundtrip diretto su raw decrypt — non c'è plaintext residuale.
    let fetched = internal_get_operatore(&pool, &created.id)
        .await
        .expect("get_operatore post-partial-update");
    assert_eq!(fetched.nome, "Sofia");
    assert_eq!(fetched.cognome, "Russo");
    assert_eq!(fetched.email.as_deref(), Some("sofia@original.com"));
    assert_eq!(fetched.telefono.as_deref(), Some("3479998888"));

    cleanup_test_database(pool, db_file).await;
}
