// ─── Ed25519 Signature Verification via WebCrypto ──────────────────
// Uses NODE-ED25519 algorithm (Cloudflare Workers extension)

/**
 * Verify an Ed25519 signature against the FLUXION public key.
 *
 * @param publicKeyHex - 32-byte public key as hex string
 * @param signatureBase64 - Base64-encoded Ed25519 signature
 * @param message - The signed message bytes (UTF-8 encoded license JSON)
 * @returns true if signature is valid
 */
export async function verifyEd25519(
  publicKeyHex: string,
  signatureBase64: string,
  message: Uint8Array,
): Promise<boolean> {
  try {
    // Convert hex public key to bytes
    const publicKeyBytes = hexToBytes(publicKeyHex);

    // Import as CryptoKey
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      publicKeyBytes,
      // NODE-ED25519 is a Cloudflare Workers extension to WebCrypto
      { name: 'NODE-ED25519', namedCurve: 'NODE-ED25519' } as CryptoKeyKeyAlgorithm,
      false,
      ['verify'],
    );

    // Decode base64 signature
    const signatureBytes = base64ToBytes(signatureBase64);

    // Verify
    const isValid = await crypto.subtle.verify(
      'NODE-ED25519',
      cryptoKey,
      signatureBytes,
      message,
    );

    return isValid;
  } catch {
    return false;
  }
}

// ─── Helpers ───────────────────────────────────────────────────────

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}

function base64ToBytes(base64: string): Uint8Array {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}
