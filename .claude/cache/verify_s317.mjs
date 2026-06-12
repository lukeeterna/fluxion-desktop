import { readFileSync, writeFileSync } from 'node:fs';
import crypto from 'node:crypto';

// D1 prod row (S317, oldest Base, cs_live_ provenance)
const d1 = JSON.parse(readFileSync('/Volumes/MontereyT7/FLUXION/.claude/cache/s317_d1_full.json', 'utf8'));
const row = d1.result[0].results[0];
const payload = row.license_payload;       // exact signed string
const sigB64  = row.license_signature;     // base64 Ed25519 sig

// kid:v1 public key (raw 32 bytes hex) — FLUXION_PUBLIC_KEY_V1_HEX
const pubHex = '0616ecd7a332de86a984dfafa87eb64915c47fecca7a3b82058a2d56e01ad5d9';
const rawPub = Buffer.from(pubHex, 'hex');
// SPKI DER wrap for Ed25519: 302a300506032b6570032100 + 32-byte key
const der = Buffer.concat([Buffer.from('302a300506032b6570032100', 'hex'), rawPub]);
const pubKey = crypto.createPublicKey({ key: der, format: 'der', type: 'spki' });

// Ed25519 verify: algorithm = null, message = exact payload string bytes
const msg = Buffer.from(payload, 'utf8');
const sig = Buffer.from(sigB64, 'base64');
const ok = crypto.verify(null, msg, pubKey, sig);

// Parse payload fields for provenance assertions
const p = JSON.parse(payload);

// Build .lic in Shape C {license_payload, license_signature} (proven == ActivateLicenseV1Input)
const lic = JSON.stringify({ license_payload: payload, license_signature: sigB64 });
writeFileSync('/Volumes/MontereyT7/FLUXION/.claude/cache/s317.lic', lic);

console.log('=== S317 OFFLINE VERIFY (kid:v1, Ed25519 verify_strict-equivalent) ===');
console.log('signature_valid :', ok);
console.log('kid             :', p.kid);
console.log('product         :', p.product);
console.log('session_id      :', p.session_id, '(cs_live_ =', p.session_id.startsWith('cs_live_'), ')');
console.log('license_id      :', p.license_id);
console.log('customer_email  :', p.customer_email);
console.log('payload_bytes   :', msg.length, '| sig_bytes:', sig.length);
console.log('.lic written    : .claude/cache/s317.lic (' + lic.length + ' bytes)');
