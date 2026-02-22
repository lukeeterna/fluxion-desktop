// ═══════════════════════════════════════════════════════════════════
// FLUXION - License System Ed25519 (Offline)
// Sistema di licenze completamente offline con firma Ed25519
//
// ARCHITETTURA:
// - Chiave pubblica Ed25519 embedded nel binary
// - Licenza JSON firmata (base64) contiene: fingerprint, tier, expiry, verticals
// - Verifica offline della firma
// - Hardware-locked (fingerprint macchina)
// - 3 tier: Base (€199), Pro (€399), Enterprise (€799) - Lifetime
// ═══════════════════════════════════════════════════════════════════

use base64::Engine;
use chrono::{DateTime, Duration, Utc};
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use sqlx::SqlitePool;
use sysinfo::{CpuExt, System, SystemExt};
use tauri::State;

// ═══════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════

/// Chiave pubblica Ed25519 embedded (hex encoded)
/// Questa è la chiave pubblica del keypair di FLUXION
/// La chiave privata è mantenuta offline dal vendor
pub const FLUXION_PUBLIC_KEY_HEX: &str =
    "c61b3c912cf953e06db979e54b72602da9e3e3cea9554e67a2baa246e7e67d39";

/// Versione del formato licenza
pub const LICENSE_VERSION: &str = "1.0";

/// Trial duration in days
pub const TRIAL_DAYS: i64 = 30;

/// Grace period for offline validation in days
pub const OFFLINE_GRACE_DAYS: i64 = 7;

// ═══════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════

/// Struttura licenza FLUXION
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FluxionLicense {
    /// Versione formato licenza
    pub version: String,

    /// ID univoco licenza
    pub license_id: String,

    /// Tier licenza: trial, base, pro, enterprise
    pub tier: LicenseTier,

    /// Data emissione
    pub issued_at: String,

    /// Data scadenza (opzionale per lifetime)
    pub expires_at: Option<String>,

    /// Hardware fingerprint
    pub hardware_fingerprint: String,

    /// Nome attività/licenziatario
    pub licensee_name: Option<String>,

    /// Email licenziatario
    pub licensee_email: Option<String>,

    /// Verticali abilitati (se tier è enterprise, tutte abilitate)
    pub enabled_verticals: Vec<String>,

    /// Numero massimo di operatori (0 = illimitato)
    pub max_operators: i32,

    /// Funzionalità extra
    pub features: LicenseFeatures,
}

/// Tier licenza
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum LicenseTier {
    Trial,
    Base,
    Pro,
    Enterprise,
}

impl LicenseTier {
    pub fn as_str(&self) -> &'static str {
        match self {
            LicenseTier::Trial => "trial",
            LicenseTier::Base => "base",
            LicenseTier::Pro => "pro",
            LicenseTier::Enterprise => "enterprise",
        }
    }

    pub fn display_name(&self) -> &'static str {
        match self {
            LicenseTier::Trial => "Trial",
            LicenseTier::Base => "FLUXION Base",
            LicenseTier::Pro => "FLUXION Pro",
            LicenseTier::Enterprise => "FLUXION Enterprise",
        }
    }

    pub fn price(&self) -> i32 {
        match self {
            LicenseTier::Trial => 0,
            LicenseTier::Base => 199,
            LicenseTier::Pro => 399,
            LicenseTier::Enterprise => 799,
        }
    }
}

impl std::str::FromStr for LicenseTier {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "trial" => Ok(LicenseTier::Trial),
            "base" => Ok(LicenseTier::Base),
            "pro" => Ok(LicenseTier::Pro),
            "enterprise" => Ok(LicenseTier::Enterprise),
            _ => Err(format!("Tier non valido: {}", s)),
        }
    }
}

/// Funzionalità incluse nella licenza
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LicenseFeatures {
    /// Voice Agent abilitato
    pub voice_agent: bool,

    /// WhatsApp AI abilitato
    pub whatsapp_ai: bool,

    /// RAG Chat abilitato
    pub rag_chat: bool,

    /// Fatturazione elettronica abilitata
    pub fatturazione_pa: bool,

    /// Loyalty avanzato
    pub loyalty_advanced: bool,

    /// API access (solo enterprise)
    pub api_access: bool,

    /// Numero massimo di schede verticali (0 = illimitato)
    pub max_verticals: i32,
}

impl Default for LicenseFeatures {
    fn default() -> Self {
        Self {
            voice_agent: false,
            whatsapp_ai: false,
            rag_chat: false,
            fatturazione_pa: true,
            loyalty_advanced: false,
            api_access: false,
            max_verticals: 1,
        }
    }
}

impl LicenseFeatures {
    pub fn for_tier(tier: &LicenseTier) -> Self {
        match tier {
            LicenseTier::Trial => Self {
                voice_agent: true,
                whatsapp_ai: true,
                rag_chat: true,
                fatturazione_pa: true,
                loyalty_advanced: true,
                api_access: true,
                max_verticals: 99, // Tutte le verticali in trial
            },
            LicenseTier::Base => Self {
                voice_agent: false,
                whatsapp_ai: false,
                rag_chat: false,
                fatturazione_pa: true,
                loyalty_advanced: false,
                api_access: false,
                max_verticals: 1,
            },
            LicenseTier::Pro => Self {
                voice_agent: true,
                whatsapp_ai: true,
                rag_chat: true,
                fatturazione_pa: true,
                loyalty_advanced: true,
                api_access: false,
                max_verticals: 3,
            },
            LicenseTier::Enterprise => Self {
                voice_agent: true,
                whatsapp_ai: true,
                rag_chat: true,
                fatturazione_pa: true,
                loyalty_advanced: true,
                api_access: true,
                max_verticals: 0, // Illimitato
            },
        }
    }
}

/// Licenza con firma (formato completo)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SignedLicense {
    /// Licenza
    pub license: FluxionLicense,

    /// Firma Ed25519 (base64)
    pub signature: String,
}

/// Stato licenza per UI
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LicenseStatus {
    pub is_valid: bool,
    pub is_activated: bool,
    pub tier: String,
    pub tier_display: String,
    pub status: String,
    pub days_remaining: Option<i32>,
    pub expiry_date: Option<String>,
    pub machine_fingerprint: String,
    pub machine_name: Option<String>,
    pub license_id: Option<String>,
    pub licensee_name: Option<String>,
    pub enabled_verticals: Vec<String>,
    pub features: LicenseFeatures,
    pub validation_code: String,
}

/// Risultato attivazione
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActivationResult {
    pub success: bool,
    pub message: String,
    pub tier: Option<String>,
    pub expiry_date: Option<String>,
}

/// Info tier per UI
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TierInfo {
    pub value: String,
    pub label: String,
    pub description: String,
    pub price: i32,
    pub features: Vec<String>,
    pub color: String,
}

// ═══════════════════════════════════════════════════════════════════
// HARDWARE FINGERPRINT
// ═══════════════════════════════════════════════════════════════════

/// Genera fingerprint hardware stabile per questa macchina
pub fn generate_fingerprint() -> String {
    let mut sys = System::new_all();
    sys.refresh_all();

    let hostname = System::host_name().unwrap_or_else(|| "unknown".to_string());
    let cpu_brand = sys
        .cpus()
        .first()
        .map(|c| c.brand().to_string())
        .unwrap_or_else(|| "unknown".to_string());
    let total_memory = sys.total_memory();
    let system_name = System::name().unwrap_or_else(|| "unknown".to_string());

    // Create fingerprint from combined hardware info
    let fingerprint_source = format!(
        "{}:{}:{}:{}",
        hostname, cpu_brand, total_memory, system_name
    );

    // Hash with SHA-256
    let mut hasher = Sha256::new();
    hasher.update(fingerprint_source.as_bytes());
    let result = hasher.finalize();

    hex::encode(result[..16].to_vec()) // Solo primi 16 byte per leggibilità
}

/// Ottieni nome macchina per display
pub fn get_machine_name() -> String {
    System::host_name().unwrap_or_else(|| "Unknown".to_string())
}

// ═══════════════════════════════════════════════════════════════════
// CRYPTO - VERIFICA FIRMA
// ═══════════════════════════════════════════════════════════════════

/// Verifica la firma di una licenza
fn verify_license_signature(license: &FluxionLicense, signature_b64: &str) -> Result<bool, String> {
    // Parse chiave pubblica
    let public_key_bytes =
        hex::decode(FLUXION_PUBLIC_KEY_HEX).map_err(|e| format!("Invalid public key: {}", e))?;

    let public_key = VerifyingKey::from_bytes(
        &public_key_bytes
            .try_into()
            .map_err(|_| "Invalid public key length")?,
    )
    .map_err(|e| format!("Invalid verifying key: {:?}", e))?;

    // Serialize license to canonical JSON
    let license_json = serde_json::to_string(license)
        .map_err(|e| format!("Failed to serialize license: {}", e))?;

    // Decode signature
    let signature_bytes = base64::engine::general_purpose::STANDARD
        .decode(signature_b64)
        .map_err(|e| format!("Invalid signature: {}", e))?;

    let signature = Signature::from_bytes(
        &signature_bytes
            .try_into()
            .map_err(|_| "Invalid signature length")?,
    );

    // Verify
    match public_key.verify(license_json.as_bytes(), &signature) {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}

// ═══════════════════════════════════════════════════════════════════
// DATABASE OPERATIONS
// ═══════════════════════════════════════════════════════════════════

/// Inizializza trial se non esiste licenza
async fn init_trial_if_needed(pool: &SqlitePool, fingerprint: &str) -> Result<(), String> {
    let existing: Option<(i32,)> = sqlx::query_as("SELECT id FROM license_cache WHERE id = 1")
        .fetch_optional(pool)
        .await
        .map_err(|e| e.to_string())?;

    if existing.is_none() {
        let now = Utc::now();
        let trial_ends = now + Duration::days(TRIAL_DAYS);

        sqlx::query(
            r#"
            INSERT INTO license_cache (id, fingerprint, tier, status, trial_started_at, trial_ends_at, is_ed25519)
            VALUES (1, ?, 'trial', 'trial', ?, ?, 1)
            "#,
        )
        .bind(fingerprint)
        .bind(now.to_rfc3339())
        .bind(trial_ends.to_rfc3339())
        .execute(pool)
        .await
        .map_err(|e| e.to_string())?;

        println!("✅ Trial Ed25519 iniziato");
    }

    Ok(())
}

/// Salva licenza verificata nel database
async fn save_license(
    pool: &SqlitePool,
    license: &FluxionLicense,
    signature: &str,
) -> Result<(), String> {
    let enabled_verticals_json =
        serde_json::to_string(&license.enabled_verticals).map_err(|e| e.to_string())?;
    let features_json = serde_json::to_string(&license.features).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO license_cache (
            id, fingerprint, tier, status, license_id, license_data, license_signature,
            licensee_name, licensee_email, enabled_verticals, features,
            issued_at, expiry_date, is_ed25519, updated_at
        ) VALUES (1, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            fingerprint = excluded.fingerprint,
            tier = excluded.tier,
            status = excluded.status,
            license_id = excluded.license_id,
            license_data = excluded.license_data,
            license_signature = excluded.license_signature,
            licensee_name = excluded.licensee_name,
            licensee_email = excluded.licensee_email,
            enabled_verticals = excluded.enabled_verticals,
            features = excluded.features,
            issued_at = excluded.issued_at,
            expiry_date = excluded.expiry_date,
            is_ed25519 = 1,
            updated_at = datetime('now')
        "#,
    )
    .bind(&license.hardware_fingerprint)
    .bind(license.tier.as_str())
    .bind(&license.license_id)
    .bind(serde_json::to_string(license).map_err(|e| e.to_string())?)
    .bind(signature)
    .bind(&license.licensee_name)
    .bind(&license.licensee_email)
    .bind(&enabled_verticals_json)
    .bind(&features_json)
    .bind(&license.issued_at)
    .bind(&license.expires_at)
    .execute(pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(())
}

// ═══════════════════════════════════════════════════════════════════
// TAURI COMMANDS
// ═══════════════════════════════════════════════════════════════════

/// Ottieni stato licenza corrente
#[tauri::command]
pub async fn get_license_status_ed25519(
    pool: State<'_, SqlitePool>,
) -> Result<LicenseStatus, String> {
    let fingerprint = generate_fingerprint();

    // Inizializza trial se necessario
    init_trial_if_needed(pool.inner(), &fingerprint).await?;

    // Leggi licenza dal database
    let cache: Option<(
        String,         // fingerprint
        String,         // tier
        String,         // status
        Option<String>, // license_id
        Option<String>, // license_data
        Option<String>, // enabled_verticals
        Option<String>, // features
        Option<String>, // trial_ends_at
        Option<String>, // expiry_date
        Option<String>, // licensee_name
    )> = sqlx::query_as(
        r#"
        SELECT fingerprint, tier, status, license_id, license_data, 
               enabled_verticals, features, trial_ends_at, expiry_date, licensee_name
        FROM license_cache WHERE id = 1
        "#,
    )
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| e.to_string())?;

    let machine_name = get_machine_name();

    match cache {
        Some((
            fp,
            tier_str,
            status,
            license_id,
            _license_data,
            enabled_vert,
            features_json,
            trial_ends,
            expiry,
            licensee,
        )) => {
            let now = Utc::now();
            let tier = tier_str
                .parse::<LicenseTier>()
                .unwrap_or(LicenseTier::Trial);

            // Calcola giorni rimanenti
            let (days_remaining, effective_expiry) = if status == "trial" {
                if let Some(ref trial_end) = trial_ends {
                    if let Ok(end_date) = DateTime::parse_from_rfc3339(trial_end) {
                        let days = (end_date.with_timezone(&Utc) - now).num_days() as i32;
                        (Some(days.max(0)), trial_ends.clone())
                    } else {
                        (None, None)
                    }
                } else {
                    (None, None)
                }
            } else if let Some(ref exp) = expiry {
                if let Ok(exp_date) = DateTime::parse_from_rfc3339(exp) {
                    let days = (exp_date.with_timezone(&Utc) - now).num_days() as i32;
                    (Some(days.max(0)), expiry.clone())
                } else {
                    (None, expiry.clone())
                }
            } else {
                (None, None) // Lifetime
            };

            // Verifica validità
            let is_valid = match status.as_str() {
                "trial" => days_remaining.map(|d| d > 0).unwrap_or(false),
                "active" => {
                    // Verifica fingerprint per licenze attivate
                    if tier != LicenseTier::Trial && fp != fingerprint {
                        false // Hardware mismatch
                    } else {
                        days_remaining.map(|d| d > 0).unwrap_or(true) // Lifetime se no expiry
                    }
                }
                _ => false,
            };

            let validation_code = if !is_valid {
                if status == "trial" {
                    "TRIAL_EXPIRED"
                } else if fp != fingerprint {
                    "HARDWARE_MISMATCH"
                } else {
                    "EXPIRED"
                }
            } else if status == "trial" {
                "TRIAL"
            } else {
                "VALID"
            }
            .to_string();

            // Parse features
            let features: LicenseFeatures = features_json
                .and_then(|f| serde_json::from_str(&f).ok())
                .unwrap_or_else(|| LicenseFeatures::for_tier(&tier));

            // Parse enabled verticals
            let enabled_verticals: Vec<String> = enabled_vert
                .and_then(|v| serde_json::from_str(&v).ok())
                .unwrap_or_default();

            Ok(LicenseStatus {
                is_valid,
                is_activated: status != "trial" && license_id.is_some(),
                tier: tier.as_str().to_string(),
                tier_display: tier.display_name().to_string(),
                status,
                days_remaining,
                expiry_date: effective_expiry,
                machine_fingerprint: fingerprint,
                machine_name: Some(machine_name),
                license_id,
                licensee_name: licensee,
                enabled_verticals,
                features,
                validation_code,
            })
        }
        None => {
            // Nessuna licenza trovata
            Ok(LicenseStatus {
                is_valid: false,
                is_activated: false,
                tier: "none".to_string(),
                tier_display: "Nessuna Licenza".to_string(),
                status: "none".to_string(),
                days_remaining: None,
                expiry_date: None,
                machine_fingerprint: fingerprint,
                machine_name: Some(machine_name),
                license_id: None,
                licensee_name: None,
                enabled_verticals: vec![],
                features: LicenseFeatures::default(),
                validation_code: "NO_LICENSE".to_string(),
            })
        }
    }
}

/// Attiva una licenza con firma Ed25519
#[tauri::command]
pub async fn activate_license_ed25519(
    pool: State<'_, SqlitePool>,
    license_data: String, // JSON completo con license + signature
) -> Result<ActivationResult, String> {
    let fingerprint = generate_fingerprint();

    // Parse licenza firmata
    let signed_license: SignedLicense = serde_json::from_str(&license_data)
        .map_err(|e| format!("Formato licenza non valido: {}", e))?;

    // Verifica firma
    let is_valid = verify_license_signature(&signed_license.license, &signed_license.signature)
        .map_err(|e| format!("Errore verifica firma: {}", e))?;

    if !is_valid {
        return Ok(ActivationResult {
            success: false,
            message:
                "Firma licenza non valida. Controlla di aver inserito correttamente la chiave."
                    .to_string(),
            tier: None,
            expiry_date: None,
        });
    }

    let license = &signed_license.license;

    // Verifica versione
    if license.version != LICENSE_VERSION {
        return Ok(ActivationResult {
            success: false,
            message: format!("Versione licenza non supportata: {}", license.version),
            tier: None,
            expiry_date: None,
        });
    }

    // Verifica fingerprint hardware
    if license.hardware_fingerprint != fingerprint {
        return Ok(ActivationResult {
            success: false,
            message: format!(
                "Questa licenza è valida solo per un'altra macchina.\\nFingerprint attuale: {}\\nFingerprint licenza: {}",
                fingerprint, license.hardware_fingerprint
            ),
            tier: None,
            expiry_date: None,
        });
    }

    // Verifica scadenza
    if let Some(ref expiry) = license.expires_at {
        if let Ok(exp_date) = DateTime::parse_from_rfc3339(expiry) {
            if exp_date < Utc::now() {
                return Ok(ActivationResult {
                    success: false,
                    message: "Licenza scaduta. Contatta il supporto per rinnovare.".to_string(),
                    tier: None,
                    expiry_date: None,
                });
            }
        }
    }

    // Salva licenza
    save_license(pool.inner(), license, &signed_license.signature).await?;

    Ok(ActivationResult {
        success: true,
        message: format!(
            "Licenza {} attivata con successo!",
            license.tier.display_name()
        ),
        tier: Some(license.tier.as_str().to_string()),
        expiry_date: license.expires_at.clone(),
    })
}

/// Ottieni fingerprint macchina corrente
#[tauri::command]
pub fn get_machine_fingerprint_ed25519() -> String {
    generate_fingerprint()
}

/// Verifica accesso a funzionalità
#[tauri::command]
pub async fn check_feature_access_ed25519(
    pool: State<'_, SqlitePool>,
    feature: String,
) -> Result<bool, String> {
    let status = get_license_status_ed25519(pool).await?;

    if !status.is_valid {
        return Ok(false);
    }

    match feature.as_str() {
        "voice_agent" => Ok(status.features.voice_agent),
        "whatsapp_ai" => Ok(status.features.whatsapp_ai),
        "rag_chat" => Ok(status.features.rag_chat),
        "fatturazione_pa" => Ok(status.features.fatturazione_pa),
        "loyalty_advanced" => Ok(status.features.loyalty_advanced),
        "api_access" => Ok(status.features.api_access),
        _ => Ok(true), // Feature base disponibili
    }
}

/// Verifica accesso a verticale
#[tauri::command]
pub async fn check_vertical_access_ed25519(
    pool: State<'_, SqlitePool>,
    vertical: String,
) -> Result<bool, String> {
    let status = get_license_status_ed25519(pool).await?;

    if !status.is_valid {
        return Ok(false);
    }

    // Enterprise ha accesso a tutto
    if status.tier == "enterprise" {
        return Ok(true);
    }

    // Verifica se la verticale è nella lista abilitata
    Ok(status.enabled_verticals.contains(&vertical))
}

/// Ottieni info tier per UI
#[tauri::command]
pub fn get_tier_info_ed25519() -> Vec<TierInfo> {
    vec![
        TierInfo {
            value: "trial".to_string(),
            label: "Trial 30 giorni".to_string(),
            description: "Prova gratuita con tutte le funzionalità".to_string(),
            price: 0,
            features: vec![
                "Tutte le schede verticali".to_string(),
                "Voice Agent".to_string(),
                "WhatsApp AI".to_string(),
                "Supporto email".to_string(),
            ],
            color: "yellow".to_string(),
        },
        TierInfo {
            value: "base".to_string(),
            label: "FLUXION Base".to_string(),
            description: "Gestionale completo - Lifetime".to_string(),
            price: 199,
            features: vec![
                "CRM Clienti".to_string(),
                "Calendario".to_string(),
                "Fatturazione".to_string(),
                "1 Scheda Verticale".to_string(),
            ],
            color: "blue".to_string(),
        },
        TierInfo {
            value: "pro".to_string(),
            label: "FLUXION Pro".to_string(),
            description: "Gestionale + Voice + 3 Verticali - Lifetime".to_string(),
            price: 399,
            features: vec![
                "Tutto di Base".to_string(),
                "3 Schede Verticali".to_string(),
                "Voice Agent".to_string(),
                "WhatsApp AI".to_string(),
                "Loyalty Avanzato".to_string(),
            ],
            color: "purple".to_string(),
        },
        TierInfo {
            value: "enterprise".to_string(),
            label: "FLUXION Enterprise".to_string(),
            description: "Tutto illimitato - Lifetime".to_string(),
            price: 799,
            features: vec![
                "Tutte le Schede Verticali".to_string(),
                "Voice Agent".to_string(),
                "API Access".to_string(),
                "Supporto Prioritario".to_string(),
                "Personalizzazioni".to_string(),
            ],
            color: "gold".to_string(),
        },
    ]
}

/// Disattiva licenza (ritorna a trial)
#[tauri::command]
pub async fn deactivate_license_ed25519(pool: State<'_, SqlitePool>) -> Result<(), String> {
    let _fingerprint = generate_fingerprint();
    let now = Utc::now();
    let trial_ends = now + Duration::days(TRIAL_DAYS);

    sqlx::query(
        r#"
        UPDATE license_cache SET
            license_id = NULL,
            license_data = NULL,
            license_signature = NULL,
            tier = 'trial',
            status = 'trial',
            trial_started_at = ?,
            trial_ends_at = ?,
            licensee_name = NULL,
            licensee_email = NULL,
            enabled_verticals = '[]',
            features = '{}',
            updated_at = datetime('now')
        WHERE id = 1
        "#,
    )
    .bind(now.to_rfc3339())
    .bind(trial_ends.to_rfc3339())
    .execute(pool.inner())
    .await
    .map_err(|e| e.to_string())?;

    Ok(())
}
