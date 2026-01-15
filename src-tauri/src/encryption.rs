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
use pbkdf2::pbkdf2_hmac_array;
use rand::RngCore;
use sha2::Sha256;
use std::sync::OnceLock;

// Key storage (initialized once at app startup)
static ENCRYPTION_KEY: OnceLock<[u8; 32]> = OnceLock::new();

/// Salt for key derivation (should be stored securely per-installation)
const DEFAULT_SALT: &[u8] = b"FLUXION_GDPR_SALT_v1";
const PBKDF2_ITERATIONS: u32 = 100_000;
const NONCE_SIZE: usize = 12;

// =============================================================================
// Key Management
// =============================================================================

/// Initialize encryption with master password
/// Call this once at app startup before any encrypt/decrypt operations
pub fn init_encryption(master_password: &str, device_id: &str) -> Result<(), String> {
    // Combine password and device ID for additional entropy
    let combined = format!("{}:{}", master_password, device_id);

    // Derive key using PBKDF2
    let key = pbkdf2_hmac_array::<Sha256, 32>(
        combined.as_bytes(),
        DEFAULT_SALT,
        PBKDF2_ITERATIONS,
    );

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
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| format!("Failed to create cipher: {}", e))?;

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
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| format!("Failed to create cipher: {}", e))?;

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

    String::from_utf8(plaintext)
        .map_err(|e| format!("Invalid UTF-8 in decrypted data: {}", e))
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

    #[test]
    fn test_encrypt_decrypt_roundtrip() {
        // Initialize with test password
        let _ = init_encryption("test_password_123", "test_device_001");

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
        let _ = init_encryption("test", "device");

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
}
