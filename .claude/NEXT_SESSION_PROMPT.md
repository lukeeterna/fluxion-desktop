# NEXT SESSION — FLUXION S325

> Luke incolla lui il prompt a inizio sessione (validazione FLUXION_MASTER + riconciliazione memorie).
> Qui sotto: stato + i risultati GIÀ ottenuti a fine S324 (NON rifarli).

## STATO
- Branch `audit/e2e-reality-check-s324`, commit audit `8aa4037`. Master intatto. Stash WIP non toccato.
- `AUDIT_E2E_FLUXION.md` = report S324 (5 aree, 13 divergenze, file:riga).

## GIÀ CONFERMATO (parziale validazione, riusare):
### A1 — R-01 Mismatch schema licenza → VERDETTO: interop Worker→Rust NON funziona (FATAL)
Più grave di quanto stimato nell'audit (audit diceva "mai testato E2E"; in realtà non può funzionare):
- Worker firma 6 campi: `{kid, license_id, customer_email, product, session_id, issued_at(int)}` — `fluxion-proxy/src/lib/ed25519-sign.ts:162-169`, sign su UTF-8 bytes :88.
- Rust verifica `serde_json::to_string(&FluxionLicense)` — struct ~11 campi diversi (`version, tier, hardware_fingerprint, expires_at, enabled_verticals, max_operators, features`, `issued_at` come String) — `license_ed25519.rs:335,350`, struct :47-80.
- Byte mai uguali → ogni attivazione ritorna `is_valid=false` (:615). hardware_fingerprint bind DOPO verify (:642), irrilevante.
- Chiavi pubbliche IDENTICHE (non è il problema): `wrangler.toml:27` == `license_ed25519.rs:30` (`c61b3c91...`).

### A2 — R-02 Secret Worker → wrangler.toml NON ha env "production" (solo "test"); `secret list` default mostra:
PRESENTI ✅: `ED25519_PRIVATE_KEY_PKCS8`, `ED25519_PUBLIC_KEY`, `ED25519_PUBLIC_KEY_V1`, `ADMIN_API_SECRET`, `CEREBRAS_API_KEY`, `GROQ_API_KEY`, `LEAD_MAGNET_SIGNING_SECRET`, `LICENSE_RECOVERY_SECRET` (lista troncata a video).
DA RI-VERIFICARE prossima sessione (output tagliato): `STRIPE_WEBHOOK_SECRET`, `STRIPE_SECRET_KEY`, `RESEND_API_KEY` — rilanciare `cd fluxion-proxy && npx wrangler secret list` e leggere lista completa.
NOTA: secret firma è `ED25519_PRIVATE_KEY_PKCS8` (non `ED25519_PRIVATE_KEY` come da prompt) — il prompt A2 cerca nome sbagliato.

## DA FARE (nel prompt che incolla Luke): A3 spot-check, FASE B (B1-B9 conflitti doc/memoria). Tutto read-only, STOP dopo report, nessuna modifica senza yes/no Luke.
