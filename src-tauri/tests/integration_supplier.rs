// ═══════════════════════════════════════════════════════════════════
// FLUXION - Integration Tests Supplier (S275)
// PII encryption coverage (S257 5 sensitive fields: nome required +
// email/telefono/indirizzo/partita_iva opt) + partial-update merge
// semantics via internal_* pool-based functions.
//
// Pattern: mirror di tests/integration_operatori.rs (S274) + tests/
// integration_clienti.rs (S273). Supplier ha 5 PII fields (uno in più
// di operatori per via di indirizzo + partita_iva entrambi opt) e
// dedupe pre-INSERT su nome+partita_iva (Migration 040 ha droppato gli
// UNIQUE SQL — vedi commands/supplier.rs S257 note). Chiude REGOLA #11
// cross-entity 4/4: clienti (S273) + operatori (S274) + supplier
// (S275) + impostazioni_fatturazione (S271 via fatture.rs).
// ═══════════════════════════════════════════════════════════════════

mod common;

use common::{cleanup_test_database, create_test_database};
use tauri_app_lib::commands::supplier::{
    internal_create_supplier, internal_get_supplier, internal_list_suppliers,
    internal_search_suppliers, internal_update_supplier, CreateSupplierRequest,
    UpdateSupplierRequest,
};
use tauri_app_lib::encryption::init_encryption_with_salt;

// Deterministic 32-byte salt for integration tests (mirror unit-test pattern in
// encryption.rs). Real installations use a per-installation random salt.
const TEST_SALT: [u8; 32] = [0xDE; 32];

/// Lazy init dell'encryption key globale per la durata del processo di test.
/// ENCRYPTION_KEY è OnceCell: la prima `set` vince, init successive ritornano
/// `Err("Encryption already initialized")` (ignorato qui — `is_encryption_ready`
/// torna true comunque, che è quello che ci serve).
fn setup_test_encryption() {
    let _ = init_encryption_with_salt("test_password_S275", "test_device_S275", &TEST_SALT);
}

fn make_request(
    nome: &str,
    email: Option<&str>,
    telefono: Option<&str>,
    indirizzo: Option<&str>,
    partita_iva: Option<&str>,
) -> CreateSupplierRequest {
    CreateSupplierRequest {
        nome: nome.to_string(),
        email: email.map(|s| s.to_string()),
        telefono: telefono.map(|s| s.to_string()),
        indirizzo: indirizzo.map(|s| s.to_string()),
        citta: None,
        cap: None,
        partita_iva: partita_iva.map(|s| s.to_string()),
    }
}

// ═══════════════════════════════════════════════════════════════════
// PII encryption at-rest — verify ciphertext per i 5 campi PII
// (nome, email, telefono, indirizzo, partita_iva) + decrypt roundtrip
// via internal_get_supplier.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_create_supplier_encrypts_pii_at_rest() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let nome_plain = "Fornitore Test Srl";
    let email_plain = "info@fornitore.example.com";
    let telefono_plain = "0971123456";
    let indirizzo_plain = "Via dei Mille 42";
    let piva_plain = "01234567890";

    let created = internal_create_supplier(
        &pool,
        make_request(
            nome_plain,
            Some(email_plain),
            Some(telefono_plain),
            Some(indirizzo_plain),
            Some(piva_plain),
        ),
    )
    .await
    .expect("create_supplier");

    // Return è plaintext (la funzione costruisce Supplier dai valori di input).
    assert_eq!(created.nome, nome_plain);
    assert_eq!(created.email.as_deref(), Some(email_plain));
    assert_eq!(created.telefono.as_deref(), Some(telefono_plain));
    assert_eq!(created.indirizzo.as_deref(), Some(indirizzo_plain));
    assert_eq!(created.partita_iva.as_deref(), Some(piva_plain));

    // SELECT raw — bypass decrypt — verifica ciphertext at-rest.
    let raw: (
        String,
        Option<String>,
        Option<String>,
        Option<String>,
        Option<String>,
    ) = sqlx::query_as(
        "SELECT nome, email, telefono, indirizzo, partita_iva FROM suppliers WHERE id = ?",
    )
    .bind(&created.id)
    .fetch_one(&pool)
    .await
    .expect("select raw");

    let (nome_raw, email_raw, telefono_raw, indirizzo_raw, piva_raw) = raw;
    let email_raw = email_raw.expect("email not NULL");
    let telefono_raw = telefono_raw.expect("telefono not NULL");
    let indirizzo_raw = indirizzo_raw.expect("indirizzo not NULL");
    let piva_raw = piva_raw.expect("partita_iva not NULL");

    // Ciphertext ≥16 char (nonce + ciphertext + tag Base64), diverso da plaintext.
    assert!(
        nome_raw.len() >= 16,
        "nome ciphertext deve essere ≥16 char, got len={}",
        nome_raw.len()
    );
    assert_ne!(nome_raw, nome_plain, "nome NON deve essere plaintext");
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
    assert!(
        indirizzo_raw.len() >= 16,
        "indirizzo ciphertext deve essere ≥16 char, got len={}",
        indirizzo_raw.len()
    );
    assert_ne!(
        indirizzo_raw, indirizzo_plain,
        "indirizzo NON deve essere plaintext"
    );
    assert!(
        piva_raw.len() >= 16,
        "partita_iva ciphertext deve essere ≥16 char, got len={}",
        piva_raw.len()
    );
    assert_ne!(
        piva_raw, piva_plain,
        "partita_iva NON deve essere plaintext"
    );

    // Roundtrip via internal_get_supplier
    let fetched = internal_get_supplier(&pool, &created.id)
        .await
        .expect("get_supplier");
    assert_eq!(fetched.nome, nome_plain);
    assert_eq!(fetched.email.as_deref(), Some(email_plain));
    assert_eq!(fetched.telefono.as_deref(), Some(telefono_plain));
    assert_eq!(fetched.indirizzo.as_deref(), Some(indirizzo_plain));
    assert_eq!(fetched.partita_iva.as_deref(), Some(piva_plain));

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Update re-encrypts changed PII fields (different ciphertext per AES-GCM
// random nonce + plaintext roundtrip OK).
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_update_supplier_re_encrypts_changed_fields() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let created = internal_create_supplier(
        &pool,
        make_request(
            "Old Supplier Srl",
            Some("old@supplier.com"),
            Some("0975111111"),
            Some("Via Vecchia 1"),
            Some("00000000001"),
        ),
    )
    .await
    .expect("create_supplier");

    // Snapshot ciphertext pre-update (3 campi che andremo a modificare).
    let ct_before: (Option<String>, Option<String>, Option<String>) = sqlx::query_as(
        "SELECT email, telefono, indirizzo FROM suppliers WHERE id = ?",
    )
    .bind(&created.id)
    .fetch_one(&pool)
    .await
    .expect("select raw before");
    let (email_ct_before, telefono_ct_before, indirizzo_ct_before) = ct_before;
    let email_ct_before = email_ct_before.expect("email not NULL pre-update");
    let telefono_ct_before = telefono_ct_before.expect("telefono not NULL pre-update");
    let indirizzo_ct_before = indirizzo_ct_before.expect("indirizzo not NULL pre-update");

    // Update: cambia email + telefono + indirizzo. nome e p.iva restano current.
    let nuova_email = "new@supplier.com";
    let nuovo_telefono = "0975222222";
    let nuovo_indirizzo = "Via Nuova 99";

    let update = UpdateSupplierRequest {
        nome: None, // preserve current
        email: Some(nuova_email.to_string()),
        telefono: Some(nuovo_telefono.to_string()),
        indirizzo: Some(nuovo_indirizzo.to_string()),
        citta: None,
        cap: None,
        partita_iva: None, // preserve
        status: None,
    };

    let updated = internal_update_supplier(&pool, &created.id, update)
        .await
        .expect("update_supplier");

    // Return plaintext riflette i nuovi valori.
    assert_eq!(updated.email.as_deref(), Some(nuova_email));
    assert_eq!(updated.telefono.as_deref(), Some(nuovo_telefono));
    assert_eq!(updated.indirizzo.as_deref(), Some(nuovo_indirizzo));
    // nome e partita_iva NON cambiati (input None → preserva current).
    assert_eq!(updated.nome, "Old Supplier Srl");
    assert_eq!(updated.partita_iva.as_deref(), Some("00000000001"));

    // Ciphertext post-update DEVE essere diverso da pre-update (plaintext nuovo).
    let ct_after: (Option<String>, Option<String>, Option<String>) = sqlx::query_as(
        "SELECT email, telefono, indirizzo FROM suppliers WHERE id = ?",
    )
    .bind(&created.id)
    .fetch_one(&pool)
    .await
    .expect("select raw after");
    let (email_ct_after, telefono_ct_after, indirizzo_ct_after) = ct_after;
    let email_ct_after = email_ct_after.expect("email not NULL post-update");
    let telefono_ct_after = telefono_ct_after.expect("telefono not NULL post-update");
    let indirizzo_ct_after = indirizzo_ct_after.expect("indirizzo not NULL post-update");

    assert_ne!(
        email_ct_after, email_ct_before,
        "email ciphertext deve cambiare dopo update con valore diverso"
    );
    assert_ne!(
        telefono_ct_after, telefono_ct_before,
        "telefono ciphertext deve cambiare dopo update con valore diverso"
    );
    assert_ne!(
        indirizzo_ct_after, indirizzo_ct_before,
        "indirizzo ciphertext deve cambiare dopo update con valore diverso"
    );
    // E comunque NON plaintext.
    assert_ne!(email_ct_after, nuova_email);
    assert_ne!(telefono_ct_after, nuovo_telefono);
    assert_ne!(indirizzo_ct_after, nuovo_indirizzo);
    assert!(email_ct_after.len() >= 16);
    assert!(telefono_ct_after.len() >= 16);
    assert!(indirizzo_ct_after.len() >= 16);

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// internal_get_supplier decifra correttamente con tutti i campi
// opzionali a None (Option pass-through). nome required resta cifrato.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_get_supplier_decrypts_with_optional_fields_none() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    // Crea supplier con SOLO nome (tutti gli opzionali None).
    let created = internal_create_supplier(&pool, make_request("Minimal Supplier", None, None, None, None))
        .await
        .expect("create_supplier");

    assert_eq!(created.nome, "Minimal Supplier");
    assert_eq!(created.email, None);
    assert_eq!(created.telefono, None);
    assert_eq!(created.indirizzo, None);
    assert_eq!(created.partita_iva, None);

    // Verifica raw che nome è cifrato comunque (anche con opt None).
    let raw: (
        String,
        Option<String>,
        Option<String>,
        Option<String>,
        Option<String>,
    ) = sqlx::query_as(
        "SELECT nome, email, telefono, indirizzo, partita_iva FROM suppliers WHERE id = ?",
    )
    .bind(&created.id)
    .fetch_one(&pool)
    .await
    .expect("select raw");
    let (nome_raw, email_raw, telefono_raw, indirizzo_raw, piva_raw) = raw;

    assert!(nome_raw.len() >= 16, "nome cifrato anche con opt None");
    assert_ne!(nome_raw, "Minimal Supplier");
    assert_eq!(email_raw, None, "email rimane NULL");
    assert_eq!(telefono_raw, None, "telefono rimane NULL");
    assert_eq!(indirizzo_raw, None, "indirizzo rimane NULL");
    assert_eq!(piva_raw, None, "partita_iva rimane NULL");

    // Roundtrip.
    let fetched = internal_get_supplier(&pool, &created.id)
        .await
        .expect("get_supplier");
    assert_eq!(fetched.nome, "Minimal Supplier");
    assert_eq!(fetched.email, None);
    assert_eq!(fetched.telefono, None);
    assert_eq!(fetched.indirizzo, None);
    assert_eq!(fetched.partita_iva, None);

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Partial update merge semantics — UpdateSupplierRequest ha tutti i campi
// Option; campi None devono PRESERVARE il valore corrente (no overwrite
// con NULL/empty). Regression critica per encryption: se merge fallisce,
// il campo viene ri-cifrato come empty e perdiamo il dato.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_update_supplier_partial_input_preserves_unchanged_fields() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let created = internal_create_supplier(
        &pool,
        make_request(
            "Stable Supplier",
            Some("stable@orig.com"),
            Some("0975999888"),
            Some("Via Stabile 7"),
            Some("99999999999"),
        ),
    )
    .await
    .expect("create_supplier");

    // Update SOLO status — tutti i 5 campi PII = None.
    let update = UpdateSupplierRequest {
        nome: None,
        email: None,
        telefono: None,
        indirizzo: None,
        citta: None,
        cap: None,
        partita_iva: None,
        status: Some("inactive".to_string()),
    };

    let updated = internal_update_supplier(&pool, &created.id, update)
        .await
        .expect("update_supplier partial");

    // I 5 campi PII devono essere preservati identici al create.
    assert_eq!(updated.nome, "Stable Supplier", "nome preservato (input None)");
    assert_eq!(
        updated.email.as_deref(),
        Some("stable@orig.com"),
        "email preservata (input None)"
    );
    assert_eq!(
        updated.telefono.as_deref(),
        Some("0975999888"),
        "telefono preservato (input None)"
    );
    assert_eq!(
        updated.indirizzo.as_deref(),
        Some("Via Stabile 7"),
        "indirizzo preservato (input None)"
    );
    assert_eq!(
        updated.partita_iva.as_deref(),
        Some("99999999999"),
        "partita_iva preservata (input None)"
    );
    // Solo status è cambiato.
    assert_eq!(updated.status, "inactive");

    // Roundtrip diretto su raw decrypt — non c'è plaintext residuale.
    let fetched = internal_get_supplier(&pool, &created.id)
        .await
        .expect("get_supplier post-partial-update");
    assert_eq!(fetched.nome, "Stable Supplier");
    assert_eq!(fetched.email.as_deref(), Some("stable@orig.com"));
    assert_eq!(fetched.telefono.as_deref(), Some("0975999888"));
    assert_eq!(fetched.indirizzo.as_deref(), Some("Via Stabile 7"));
    assert_eq!(fetched.partita_iva.as_deref(), Some("99999999999"));

    cleanup_test_database(pool, db_file).await;
}

// ═══════════════════════════════════════════════════════════════════
// Search (tier-1) matcha plaintext decifrato — verifica che `LIKE` non
// si applica al ciphertext e che il filtro in-memory funziona su nome.
// Bonus: testa internal_list_suppliers + internal_search_suppliers in
// stesso flow.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_search_suppliers_matches_decrypted_plaintext() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    internal_create_supplier(
        &pool,
        make_request("Alfa Forniture", Some("a@example.com"), None, None, None),
    )
    .await
    .expect("create alfa");
    internal_create_supplier(
        &pool,
        make_request("Beta Logistica", Some("b@example.com"), None, None, None),
    )
    .await
    .expect("create beta");
    internal_create_supplier(
        &pool,
        make_request("Gamma Trade", Some("g@example.com"), None, None, None),
    )
    .await
    .expect("create gamma");

    // list_suppliers (active) ritorna tutti i 3, ordinati per plaintext.
    let all = internal_list_suppliers(&pool, false)
        .await
        .expect("list_suppliers");
    assert_eq!(all.len(), 3);
    assert_eq!(all[0].nome, "Alfa Forniture");
    assert_eq!(all[1].nome, "Beta Logistica");
    assert_eq!(all[2].nome, "Gamma Trade");

    // Search "beta" matcha solo Beta Logistica.
    let matches = internal_search_suppliers(&pool, "beta")
        .await
        .expect("search beta");
    assert_eq!(matches.len(), 1);
    assert_eq!(matches[0].nome, "Beta Logistica");

    // Search "@example.com" matcha tutti e 3 (email decifrata).
    let by_email = internal_search_suppliers(&pool, "@example.com")
        .await
        .expect("search email");
    assert_eq!(by_email.len(), 3);

    // Search query vuota → ritorna tutti capped a 20.
    let empty_q = internal_search_suppliers(&pool, "")
        .await
        .expect("search empty");
    assert_eq!(empty_q.len(), 3);

    // Search no match.
    let no_match = internal_search_suppliers(&pool, "zzz_inexistent")
        .await
        .expect("search no-match");
    assert!(no_match.is_empty());

    cleanup_test_database(pool, db_file).await;
}
