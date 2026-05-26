// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Ed25519 kid:v1 Verify (S292)
//
// Verifica firma Ed25519 (standard WebCrypto-compatible) di license
// payload emesso dal Worker `fluxion-proxy` route `stripe-webhook.ts`.
//
// Interop con `fluxion-proxy/src/lib/ed25519-sign.ts`:
// - Worker firma payload canonicalized (key order esplicito) usando
//   PKCS8 PRIVATE_KEY + algo 'Ed25519' (standard, NON NODE-ED25519).
// - Client (qui) verifica con `ed25519-dalek` `verify_strict`.
//
// kid:v1 pubkey hex (raw 32 bytes):
//   0616ecd7a332de86a984dfafa87eb64915c47fecca7a3b82058a2d56e01ad5d9
//
// PROD migration (S292+): aggiungere kid:v2 mapping qui post-rotation,
// MAI rimuovere kid:v1 senza migrazione client install-base completa.
//
// NOTA: questa è verifica della *firma worker*, separata dal sistema
// legacy `license_ed25519.rs` (FLUXION_PUBLIC_KEY_HEX `c61b3c...` con
// `FluxionLicense` serde struct). I due sistemi coesistono — il legacy
// gestisce trial/activation flow, questo gestisce verify license emessa
// post-checkout Stripe (D1 webhook_events).
// ═══════════════════════════════════════════════════════════════════

use base64::Engine;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde::{Deserialize, Serialize};

// ───────────────────────────────────────────────────────────────────
// Constants
// ───────────────────────────────────────────────────────────────────

/// kid:v1 public key (raw 32 bytes hex) — keypair S290.
/// Privata salvata in CF Worker Secret `ED25519_PRIVATE_KEY_PKCS8`.
pub const FLUXION_PUBLIC_KEY_V1_HEX: &str =
    "0616ecd7a332de86a984dfafa87eb64915c47fecca7a3b82058a2d56e01ad5d9";

// ───────────────────────────────────────────────────────────────────
// Core verify
// ───────────────────────────────────────────────────────────────────

/// Verifica una firma Ed25519 contro payload + kid.
///
/// Ritorna `Ok(true)` se firma valida, `Ok(false)` se invalida.
/// `Err(_)` solo per errori strutturali (kid sconosciuto, base64/hex
/// malformati, lunghezze sbagliate).
pub fn verify_ed25519_signature_dalek(
    payload: &str,
    signature_base64: &str,
    kid: &str,
) -> Result<bool, String> {
    // 1. Map kid → public key hex
    let public_key_hex = match kid {
        "v1" => FLUXION_PUBLIC_KEY_V1_HEX,
        other => return Err(format!("unknown kid: {}", other)),
    };

    // 2. Decode public key
    let public_key_bytes =
        hex::decode(public_key_hex).map_err(|e| format!("Invalid public key hex: {}", e))?;
    let public_key_arr: [u8; 32] = public_key_bytes
        .try_into()
        .map_err(|_| "Invalid public key length (expected 32 bytes)".to_string())?;
    let verifying_key = VerifyingKey::from_bytes(&public_key_arr)
        .map_err(|e| format!("Invalid verifying key: {:?}", e))?;

    // 3. Decode signature
    let signature_bytes = base64::engine::general_purpose::STANDARD
        .decode(signature_base64)
        .map_err(|e| format!("Invalid signature base64: {}", e))?;
    let signature_arr: [u8; 64] = signature_bytes
        .try_into()
        .map_err(|_| "Invalid signature length (expected 64 bytes)".to_string())?;
    let signature = Signature::from_bytes(&signature_arr);

    // 4. Verify strict (RFC 8032 compliant, rejects malleable signatures)
    Ok(verifying_key
        .verify_strict(payload.as_bytes(), &signature)
        .is_ok())
}

// ───────────────────────────────────────────────────────────────────
// Tauri command (FE interop)
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
pub struct VerifyLicenseV1Request {
    pub payload: String,
    pub signature_base64: String,
    pub kid: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct VerifyLicenseV1Response {
    pub kid: String,
    pub valid: bool,
}

/// Tauri command: verifica firma license kid:v1 da FE (debug + activate flow).
///
/// FE usage:
///   const res = await invoke<VerifyLicenseV1Response>(
///     'verify_license_signature_v1',
///     { req: { payload, signature_base64, kid: 'v1' } }
///   );
#[tauri::command]
pub fn verify_license_signature_v1(
    req: VerifyLicenseV1Request,
) -> Result<VerifyLicenseV1Response, String> {
    let kid = req.kid.unwrap_or_else(|| "v1".to_string());
    let valid = verify_ed25519_signature_dalek(&req.payload, &req.signature_base64, &kid)?;
    Ok(VerifyLicenseV1Response { kid, valid })
}

// ───────────────────────────────────────────────────────────────────
// Tests (interop with real Worker output S291 Gate 1)
// ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    /// Real D1 row from S291 evt_1TaKKhIW4bHDTsaHtagaQs1a
    /// Sourced via:
    ///   wrangler d1 execute fluxion-webhook-events-test --env test --remote \
    ///     --command "SELECT license_payload, license_signature FROM webhook_events
    ///                WHERE event_id='evt_1TaKKhIW4bHDTsaHtagaQs1a';"
    /// Verified roundtrip with worker POST /api/v1/verify → {"kid":"v1","valid":true}
    const REAL_PAYLOAD: &str = "{\"kid\":\"v1\",\"license_id\":\"0b707c62b8f32a647ab3bd2204fa9d3e4483454d28af6f6f5f88b10149c20e91\",\"customer_email\":\"fluxion.gestionale@gmail.com\",\"product\":\"base\",\"session_id\":\"cs_test_a1CYEFiXWEhxen333ZaHuuSszuM6Z8f1wsLoafAca7krFXhRiX8g115CXp\",\"issued_at\":1779736145}";
    const REAL_SIG: &str =
        "ToiIWbu45aTrVDSsYaDHG+qTll3UDsVTcfQ66L97zaDNPT0PnVOaS/Kn8KIzS6g3JI/LuVMeMEXPN0nw8oMqAA==";

    #[test]
    fn real_worker_signature_verifies_true() {
        let result = verify_ed25519_signature_dalek(REAL_PAYLOAD, REAL_SIG, "v1")
            .expect("verify should not error on valid input");
        assert!(
            result,
            "Real Worker signature S291 must verify locally (interop dalek ↔ WebCrypto)"
        );
    }

    #[test]
    fn tampered_payload_one_byte_returns_false() {
        // Replace "base" → "prox" (4 bytes same len, content tamper)
        let tampered = REAL_PAYLOAD.replace("\"base\"", "\"prox\"");
        assert_ne!(
            tampered, REAL_PAYLOAD,
            "payload tampering setup must change input"
        );
        let result = verify_ed25519_signature_dalek(&tampered, REAL_SIG, "v1")
            .expect("verify should not error on tampered input");
        assert!(!result, "tampered payload must NOT verify");
    }

    #[test]
    fn tampered_signature_one_byte_returns_false() {
        // Flip bit 0 of first sig byte
        let mut sig_bytes = base64::engine::general_purpose::STANDARD
            .decode(REAL_SIG)
            .unwrap();
        sig_bytes[0] ^= 0x01;
        let tampered_sig = base64::engine::general_purpose::STANDARD.encode(&sig_bytes);
        let result = verify_ed25519_signature_dalek(REAL_PAYLOAD, &tampered_sig, "v1")
            .expect("verify should not error on bit-flipped sig");
        assert!(!result, "1-bit tampered signature must NOT verify");
    }

    #[test]
    fn unknown_kid_returns_err() {
        let result = verify_ed25519_signature_dalek(REAL_PAYLOAD, REAL_SIG, "v99");
        assert!(result.is_err(), "unknown kid must Err, not Ok(false)");
        let err = result.unwrap_err();
        assert!(
            err.contains("unknown kid"),
            "error msg should be diagnostic: {}",
            err
        );
    }

    #[test]
    fn malformed_signature_base64_returns_err() {
        let result = verify_ed25519_signature_dalek(REAL_PAYLOAD, "!!!not-base64!!!", "v1");
        assert!(result.is_err());
    }

    #[test]
    fn wrong_length_signature_returns_err() {
        // Valid base64 but wrong length (32 bytes instead of 64)
        let short_sig = base64::engine::general_purpose::STANDARD.encode([0u8; 32]);
        let result = verify_ed25519_signature_dalek(REAL_PAYLOAD, &short_sig, "v1");
        assert!(result.is_err());
    }

    #[test]
    fn tauri_command_response_shape() {
        let req = VerifyLicenseV1Request {
            payload: REAL_PAYLOAD.to_string(),
            signature_base64: REAL_SIG.to_string(),
            kid: Some("v1".to_string()),
        };
        let res = verify_license_signature_v1(req).expect("command should not error");
        assert_eq!(res.kid, "v1");
        assert!(res.valid);
    }

    #[test]
    fn tauri_command_defaults_kid_to_v1() {
        let req = VerifyLicenseV1Request {
            payload: REAL_PAYLOAD.to_string(),
            signature_base64: REAL_SIG.to_string(),
            kid: None,
        };
        let res = verify_license_signature_v1(req).expect("command should default kid");
        assert_eq!(res.kid, "v1");
        assert!(res.valid);
    }
}
