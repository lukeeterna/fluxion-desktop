# S248 — Master Password Flow Decision

**Data**: 2026-05-16 (S248)
**Decisore**: CTO autonomo (mandato S181 — founder NO review su priorità tecniche P0)
**Contesto**: Cat 3 P0 #2 wiring `gdpr_init_encryption` → CRUD clienti. `gdpr_init_encryption(master_password, device_id)` esiste come Tauri command ma mai chiamato dal frontend = dead code. PII in plaintext SQLite. Plan S248 chiede di scegliere fra:
- **A** master_password derivata zero-friction (license_email + machine_uid)
- **B** utente sceglie master password al setup wizard (1-time display + recovery via reset)

## Scelta: **OPZIONE A (raffinata)**

### Decisione finale parametrizzata

```
master_password = license_cache.license_key   (or trial-UUID fallback pre-activation)
device_id       = license_cache.fingerprint   (SHA-256 hardware, già calcolato S015)
salt            = OS keychain (S247, 32-byte random per-installation)
KDF             = PBKDF2-HMAC-SHA256 100k iter (esistente encryption.rs)
```

Entrambi `license_key` + `fingerprint` sono **già presenti** in tabella `license_cache` (migrations 015 + 020 Ed25519). Zero campi nuovi da aggiungere.

### Razionale CTO (rule #4 critica strutturale)

**1. Target PMI italiana 1-15 dip — capability matching**
Founder PMI media NON è in grado di gestire master password sicura. Statisticamente perderebbe la password al primo dimentica → DB cifrato perso → reputational disaster GDPR ("non riesco a recuperare i miei dati cliente"). Opt B introduce friction inaccettabile per il segment.

**2. Threat model realistico FLUXION**
Threat principale: laptop rubato/perso → disk image dump cold (no live RAM, no keychain decryption attiva). Per quel livello, Opt A con per-installation salt random in keychain è sufficiente perché:
- Attaccante con solo disk image (no keychain) → no salt → brute-force PBKDF2 100k iter su input deterministico richiede comunque computazione significativa per ogni DB rubato individualmente (no rainbow table).
- Attaccante con disk image + keychain dump → ha già full device control = game over comunque (può leggere RAM, intercettare runtime).

**3. GDPR Art. 32 compliance baseline**
"Technical measures applied" requisito soddisfatto da AES-256-GCM + PBKDF2 100k + per-installation salt. Non è richiesto user-secret-based encryption per PII business standard (codice fiscale, telefono cliente). Sarebbe richiesto solo per "dati sanitari" categoria speciale (Art. 9) — fuori scope FLUXION 2026 attuale.

**4. Recovery flow gratis**
Reinstallazione su stesso device → stesso `fingerprint` → stessa derived key → decryption automatica. Reinstallazione su nuovo device → fingerprint diverso → key diversa → richiede export/import GDPR (funzione P1 da implementare cmq per DSAR Art. 20).

**5. Edge case license_key change post-attivazione**
Pre-trial: `license_key` = trial-UUID random locale (S015 trial flow esistente).
Post-acquisto: `license_key` = UUID Ed25519 server-generato (S020).
Cambio `license_key` durante upgrade = **rotation event** richiede re-encrypt migration:
- Detect: `init_encryption` con nuovo `license_key` fallisce su `OnceLock::set` (già init).
- Soluzione: rotation command `encryption_rotate_master(old_password, new_password)` letture-decifra-cifra-scrittura atomic transaction.
- Implementazione Task 3 (post-baseline wiring).

### Critica strutturale (4 punti, rule #4)

**Assunzione nascosta**: `license_cache.fingerprint` immutabile per installation. Vero per SHA-256 hardware (CPU+motherboard) MA cambia su:
- Upgrade hardware (es. cambio motherboard) → key persa → migration manuale.
- Macchina virtuale con UUID dinamico → fingerprint instabile.
**Mitigazione**: documentare in HELPDESK + scheda recovery. Trigger automatico re-key prompt se fingerprint mismatch detectato startup.

**Cosa rompe a 30/60/90gg**:
- 30gg: nulla (key deterministica, decryption stable).
- 60gg: primi upgrade hardware utenti → 1-2 ticket support con perdita dati. Mitigation: feature "export plaintext backup" via master license key prima upgrade.
- 90gg: rotazione trial→base license_key su 50%+ utenti che acquistano → rotation command **DEVE** essere implementato prima del flusso Stripe webhook attivazione.

**Pattern errore noti**:
- Pattern "encryption-at-rest senza user-secret" è standard industry (Notion local cache, 1Password Vault keychain-bound, Apple FileVault personal key). NOT a security smell per consumer/SMB target.
- Antipattern: BCrypt/Argon2 PBKDF2 con input completamente noto E senza salt → rainbow table trivial. **NOI siamo OK** perché S247 ha aggiunto per-installation random salt.

**Sovradimensionamento**: nessuno. Opt B sarebbe over-engineered per il segment.

## Implementazione Task 3 — derivata da questa decisione

### Step 1 — Cambia API `init_encryption` (signature breaking, ma frontend ha 0 caller)

Pseudo-rust nuovo command:
```rust
#[tauri::command]
pub async fn gdpr_auto_init_encryption(
    state: State<'_, AppState>,
) -> Result<(), String> {
    let pool = state.pool.lock().await;
    let row: Option<(Option<String>, String)> = sqlx::query_as(
        "SELECT license_key, fingerprint FROM license_cache WHERE id = 1"
    )
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    let (license_key_opt, fingerprint) = row.ok_or_else(||
        "License cache not initialized — run setup wizard first".to_string()
    )?;

    let derived_secret = license_key_opt.unwrap_or_else(||
        // Trial pre-activation fallback: use fingerprint as secret too
        // (key will be re-derived after Stripe activation via rotate command)
        fingerprint.clone()
    );

    init_encryption(&derived_secret, &fingerprint)
}
```

### Step 2 — Startup hook in `lib.rs` `tauri::Builder::default().setup(...)`

Dopo creazione AppState + run migrations, **prima** di registrare commands che toccano clienti:
```rust
.setup(|app| {
    let state = app.state::<AppState>();
    let pool = futures::executor::block_on(state.pool.lock());
    // Run migrations (existing)
    // ...
    drop(pool);
    // Auto-init encryption from license cache (if available)
    let handle = app.handle().clone();
    tauri::async_runtime::spawn(async move {
        if let Err(e) = gdpr_auto_init_encryption(handle.state::<AppState>()).await {
            eprintln!("[FLUXION] Encryption auto-init deferred: {}", e);
            // Defer ok — first cliente CRUD will retry via lazy guard
        }
    });
    Ok(())
})
```

### Step 3 — Lazy retry guard in `commands/clienti.rs` write paths

```rust
async fn ensure_encryption_ready(state: &AppState) -> Result<(), String> {
    if encryption::is_encryption_ready() { return Ok(()); }
    gdpr_auto_init_encryption(state.clone()).await
}
```

Chiamato all'inizio di ogni `clienti_create` / `clienti_update`.

### Step 4 — Rotation command (deferred ma critico pre-Stripe live)

```rust
#[tauri::command]
pub async fn gdpr_rotate_encryption_key(
    state: State<'_, AppState>,
    old_license_key: String,
    new_license_key: String,
) -> Result<u64 /* righe migrate */, String> { /* ... */ }
```

Implementazione: decrypt-all-with-old-key in memory → reinit OnceLock requires process restart workaround → atomic transaction re-encrypt write back. Out-of-scope baseline S248, target S249+.

## Sentry tracing (post-Task 4 if DSN active)

Strumentare:
- `gdpr_auto_init_encryption` → span con result success/defer
- `clienti_create/update` → tag `pii_encrypted=true`
- `gdpr_rotate_encryption_key` → critical span, alert on failure

## Conferma Founder NO required

Per mandato S181 (CTO decide P0/P1/P2 senza review), opzione A è autorizzata. Comunico al founder solo:
1. Recovery flow = ri-attivazione licenza su stesso device, sempre.
2. Export plaintext backup pre-rotation = feature P1 in roadmap.
3. Upgrade hardware = potenziale perdita dati cifrati → mitigation export prima del cambio.

---

**Status decisione**: ✅ DECIDED — procedere implementazione Task 3 con baseline (no rotation in S248).
**Cross-ref VOS**: aggiungere D-05 in `~/venture-os/wiki/projects/FLUXION/DECISIONS.md` post-implementazione live-tested.
