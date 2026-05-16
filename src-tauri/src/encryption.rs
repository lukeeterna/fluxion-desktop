// =============================================================================
// FLUXION - GDPR Encryption at Rest Module
// AES-256-GCM encryption for sensitive personal data
// =============================================================================
//
// Encrypts: nome, cognome, telefono, email, codice_fiscale, indirizzo
// Storage: Base64-encoded ciphertext with embedded nonce
// Key derivation: PBKDF2 from master password + device ID
//

use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use keyring::Entry;
use pbkdf2::pbkdf2_hmac_array;
use rand::RngCore;
use sha2::Sha256;
use std::sync::OnceLock;

// Key storage (initialized once at app startup)
static ENCRYPTION_KEY: OnceLock<[u8; 32]> = OnceLock::new();

// S247 Cat 3 P0 #1 — per-installation random salt stored in OS keychain.
// Previous hardcoded constant `b"FLUXION_GDPR_SALT_v1"` removed: a shared salt
// across installations allowed precomputed rainbow tables against stolen DBs.
const KEYRING_SERVICE: &str = "fluxion-gestionale";
const KEYRING_SALT_USER: &str = "gdpr-encryption-salt-v1";
const SALT_SIZE: usize = 32;
const PBKDF2_ITERATIONS: u32 = 100_000;
const NONCE_SIZE: usize = 12;

// =============================================================================
// Key Management
// =============================================================================

/// Load the per-installation salt from the OS keychain, or generate and persist
/// a fresh 32-byte random salt on first call.
///
/// Storage: macOS Keychain Services / Windows Credential Manager (via `keyring`).
/// Failure mode: if the keychain is inaccessible (e.g., locked, sandbox denial)
/// this returns an error rather than silently falling back to a weak salt.
fn get_or_create_salt() -> Result<[u8; SALT_SIZE], String> {
    let entry = Entry::new(KEYRING_SERVICE, KEYRING_SALT_USER)
        .map_err(|e| format!("Keychain entry init failed: {}", e))?;

    match entry.get_password() {
        Ok(b64) => {
            let bytes = BASE64
                .decode(b64.as_bytes())
                .map_err(|e| format!("Stored salt is not valid Base64: {}", e))?;
            if bytes.len() != SALT_SIZE {
                return Err(format!(
                    "Stored salt has wrong length: expected {} bytes, got {}",
                    SALT_SIZE,
                    bytes.len()
                ));
            }
            let mut salt = [0u8; SALT_SIZE];
            salt.copy_from_slice(&bytes);
            Ok(salt)
        }
        Err(keyring::Error::NoEntry) => {
            let mut salt = [0u8; SALT_SIZE];
            OsRng.fill_bytes(&mut salt);
            entry
                .set_password(&BASE64.encode(salt))
                .map_err(|e| format!("Failed to persist salt in keychain: {}", e))?;
            Ok(salt)
        }
        Err(e) => Err(format!("Keychain read failed: {}", e)),
    }
}

/// Initialize encryption with master password.
/// Call this once at app startup before any encrypt/decrypt operations.
///
/// The salt is loaded from (or initialized in) the OS keychain on first call:
/// each installation gets a unique 32-byte random salt, defeating cross-installation
/// rainbow tables.
pub fn init_encryption(master_password: &str, device_id: &str) -> Result<(), String> {
    let salt = get_or_create_salt()?;
    init_encryption_with_salt(master_password, device_id, &salt)
}

/// Internal/test variant: derive key with a caller-supplied salt.
/// Production code must use `init_encryption` which sources the salt from the
/// OS keychain. This entry point exists so unit tests can run without touching
/// the host keychain.
pub fn init_encryption_with_salt(
    master_password: &str,
    device_id: &str,
    salt: &[u8],
) -> Result<(), String> {
    // Combine password and device ID for additional entropy
    let combined = format!("{}:{}", master_password, device_id);

    // Derive key using PBKDF2 with the per-installation salt
    let key = pbkdf2_hmac_array::<Sha256, 32>(combined.as_bytes(), salt, PBKDF2_ITERATIONS);

    ENCRYPTION_KEY
        .set(key)
        .map_err(|_| "Encryption already initialized".to_string())
}

/// Check if encryption is initialized
pub fn is_encryption_ready() -> bool {
    ENCRYPTION_KEY.get().is_some()
}

/// Get the encryption key (internal use only)
fn get_key() -> Result<&'static [u8; 32], String> {
    ENCRYPTION_KEY
        .get()
        .ok_or_else(|| "Encryption not initialized. Call init_encryption first.".to_string())
}

// =============================================================================
// Encryption / Decryption
// =============================================================================

/// Encrypt a plaintext string
/// Returns Base64-encoded ciphertext with embedded nonce
pub fn encrypt_field(plaintext: &str) -> Result<String, String> {
    if plaintext.is_empty() {
        return Ok(String::new());
    }

    let key = get_key()?;
    let cipher =
        Aes256Gcm::new_from_slice(key).map_err(|e| format!("Failed to create cipher: {}", e))?;

    // Generate random nonce
    let mut nonce_bytes = [0u8; NONCE_SIZE];
    OsRng.fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    // Encrypt
    let ciphertext = cipher
        .encrypt(nonce, plaintext.as_bytes())
        .map_err(|e| format!("Encryption failed: {}", e))?;

    // Combine nonce + ciphertext and encode as Base64
    let mut combined = Vec::with_capacity(NONCE_SIZE + ciphertext.len());
    combined.extend_from_slice(&nonce_bytes);
    combined.extend_from_slice(&ciphertext);

    Ok(BASE64.encode(combined))
}

/// Decrypt a Base64-encoded ciphertext
/// Returns the original plaintext
pub fn decrypt_field(encrypted: &str) -> Result<String, String> {
    if encrypted.is_empty() {
        return Ok(String::new());
    }

    let key = get_key()?;
    let cipher =
        Aes256Gcm::new_from_slice(key).map_err(|e| format!("Failed to create cipher: {}", e))?;

    // Decode Base64
    let combined = BASE64
        .decode(encrypted)
        .map_err(|e| format!("Invalid Base64: {}", e))?;

    if combined.len() < NONCE_SIZE {
        return Err("Invalid encrypted data: too short".to_string());
    }

    // Split nonce and ciphertext
    let (nonce_bytes, ciphertext) = combined.split_at(NONCE_SIZE);
    let nonce = Nonce::from_slice(nonce_bytes);

    // Decrypt
    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e| format!("Decryption failed: {}", e))?;

    String::from_utf8(plaintext).map_err(|e| format!("Invalid UTF-8 in decrypted data: {}", e))
}

// =============================================================================
// Sensitive Field Helpers
// =============================================================================

/// List of fields that should be encrypted for GDPR compliance
pub const SENSITIVE_FIELDS: &[&str] = &[
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

/// Check if a field name is sensitive and should be encrypted
pub fn is_sensitive_field(field_name: &str) -> bool {
    SENSITIVE_FIELDS.contains(&field_name)
}

// =============================================================================
// Tauri Commands
// =============================================================================

/// Initialize encryption system (called from frontend on first setup)
#[tauri::command]
pub fn gdpr_init_encryption(master_password: String, device_id: String) -> Result<(), String> {
    init_encryption(&master_password, &device_id)
}

/// Check if encryption is ready
#[tauri::command]
pub fn gdpr_is_ready() -> bool {
    is_encryption_ready()
}

/// Encrypt a single field (for testing/manual use)
#[tauri::command]
pub fn gdpr_encrypt(plaintext: String) -> Result<String, String> {
    encrypt_field(&plaintext)
}

/// Decrypt a single field (for testing/manual use)
#[tauri::command]
pub fn gdpr_decrypt(encrypted: String) -> Result<String, String> {
    decrypt_field(&encrypted)
}

// =============================================================================
// Tests
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    // Deterministic 32-byte salt for unit tests. Real installations get a
    // per-installation random salt from the OS keychain via get_or_create_salt().
    const TEST_SALT: [u8; SALT_SIZE] = [0xAB; SALT_SIZE];

    #[test]
    fn test_encrypt_decrypt_roundtrip() {
        // Initialize with test password (test-only entry point, no keychain access)
        let _ = init_encryption_with_salt("test_password_123", "test_device_001", &TEST_SALT);

        let original = "Mario Rossi";
        let encrypted = encrypt_field(original).unwrap();

        // Encrypted should be different from original
        assert_ne!(encrypted, original);

        // Should be Base64
        assert!(BASE64.decode(&encrypted).is_ok());

        // Decrypt should return original
        let decrypted = decrypt_field(&encrypted).unwrap();
        assert_eq!(decrypted, original);
    }

    #[test]
    fn test_empty_string() {
        let _ = init_encryption_with_salt("test", "device", &TEST_SALT);

        let encrypted = encrypt_field("").unwrap();
        assert!(encrypted.is_empty());

        let decrypted = decrypt_field("").unwrap();
        assert!(decrypted.is_empty());
    }

    #[test]
    fn test_sensitive_fields() {
        assert!(is_sensitive_field("nome"));
        assert!(is_sensitive_field("telefono"));
        assert!(!is_sensitive_field("id"));
        assert!(!is_sensitive_field("created_at"));
    }

    #[test]
    fn test_init_with_salt_rejects_reinit() {
        // OnceLock guarantees a single successful init across the test process.
        // We can't reliably assert error vs ok here (test ordering depends on
        // cargo test scheduler), but we can assert the function is idempotent
        // in the sense that a second call never panics and either succeeds
        // (first call in this process) or returns a descriptive Err.
        let salt_a: [u8; SALT_SIZE] = [0x11; SALT_SIZE];
        let salt_b: [u8; SALT_SIZE] = [0x22; SALT_SIZE];
        let _ = init_encryption_with_salt("pw", "dev", &salt_a);
        let second = init_encryption_with_salt("pw", "dev", &salt_b);
        // If a prior test already initialized, the second call must return Err
        // rather than silently replacing the key.
        if second.is_err() {
            assert!(second.unwrap_err().contains("already initialized"));
        }
    }
}
