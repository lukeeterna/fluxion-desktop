// ═══════════════════════════════════════════════════════════════════
// FLUXION - License System (Phase 8)
// Keygen.sh integration with 30-day trial, offline caching
// ═══════════════════════════════════════════════════════════════════

use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use sqlx::SqlitePool;
use sysinfo::{CpuExt, System, SystemExt};
use tauri::State;

// ═══════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════

const KEYGEN_ACCOUNT_ID: &str = "b845d2ed-92a4-4048-b2d8-ee625206a5ae";
const KEYGEN_API_URL: &str = "https://api.keygen.sh/v1";
const TRIAL_DAYS: i64 = 30;
const OFFLINE_GRACE_DAYS: i64 = 7;

// ═══════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LicenseStatus {
    pub is_valid: bool,
    pub is_activated: bool,
    pub tier: String,   // "trial", "base", "ia", "expired", "none"
    pub status: String, // "trial", "active", "expired", "suspended"
    pub days_remaining: Option<i32>,
    pub expiry_date: Option<String>,
    pub machine_fingerprint: String,
    pub machine_name: Option<String>,
    pub trial_ends_at: Option<String>,
    pub last_validated_at: Option<String>,
    pub validation_code: String, // "VALID", "TRIAL", "EXPIRED", "NO_LICENSE", etc.
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ActivationResult {
    pub success: bool,
    pub message: String,
    pub tier: Option<String>,
    pub expiry_date: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenValidateRequest {
    meta: KeygenValidateMeta,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenValidateMeta {
    key: String,
    scope: KeygenValidateScope,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenValidateScope {
    fingerprint: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenValidateResponse {
    meta: Option<KeygenResponseMeta>,
    data: Option<KeygenLicenseData>,
    errors: Option<Vec<KeygenError>>,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenResponseMeta {
    valid: bool,
    code: String,
    detail: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct KeygenLicenseData {
    id: String,
    attributes: KeygenLicenseAttributes,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct KeygenLicenseAttributes {
    name: Option<String>,
    key: String,
    expiry: Option<String>,
    status: String,
    metadata: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenError {
    title: String,
    detail: Option<String>,
    code: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenActivateRequest {
    data: KeygenMachineData,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenMachineData {
    #[serde(rename = "type")]
    data_type: String,
    attributes: KeygenMachineAttributes,
    relationships: KeygenMachineRelationships,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenMachineAttributes {
    fingerprint: String,
    name: String,
    platform: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenMachineRelationships {
    license: KeygenRelationship,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenRelationship {
    data: KeygenRelationshipData,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeygenRelationshipData {
    #[serde(rename = "type")]
    data_type: String,
    id: String,
}

// ═══════════════════════════════════════════════════════════════════
// FINGERPRINT GENERATION
// ═══════════════════════════════════════════════════════════════════

/// Generate a stable hardware fingerprint for this machine
/// Uses: hostname, CPU brand, total RAM
pub fn generate_fingerprint() -> String {
    let mut sys = System::new_all();
    sys.refresh_all();

    let hostname = sys.host_name().unwrap_or_else(|| "unknown".to_string());
    let cpu_brand = sys
        .cpus()
        .first()
        .map(|c: &sysinfo::Cpu| c.brand().to_string())
        .unwrap_or_else(|| "unknown".to_string());
    let total_memory = sys.total_memory();

    // Create fingerprint from combined hardware info
    let fingerprint_source = format!("{}:{}:{}", hostname, cpu_brand, total_memory);

    // Hash with SHA-256
    let mut hasher = Sha256::new();
    hasher.update(fingerprint_source.as_bytes());
    let result = hasher.finalize();

    hex::encode(result)
}

/// Get machine name for display
pub fn get_machine_name() -> String {
    let sys = System::new();
    sys.host_name().unwrap_or_else(|| "Unknown".to_string())
}

/// Get platform string for Keygen
pub fn get_platform() -> String {
    #[cfg(target_os = "macos")]
    return "macOS".to_string();
    #[cfg(target_os = "windows")]
    return "Windows".to_string();
    #[cfg(target_os = "linux")]
    return "Linux".to_string();
    #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
    return "Unknown".to_string();
}

// ═══════════════════════════════════════════════════════════════════
// DATABASE OPERATIONS
// ═══════════════════════════════════════════════════════════════════

/// Initialize trial mode if no license exists
async fn init_trial_if_needed(pool: &SqlitePool, fingerprint: &str) -> Result<(), String> {
    // Check if license_cache exists
    let existing: Option<(i32,)> = sqlx::query_as("SELECT id FROM license_cache WHERE id = 1")
        .fetch_optional(pool)
        .await
        .map_err(|e| e.to_string())?;

    if existing.is_none() {
        let now = Utc::now();
        let trial_ends = now + Duration::days(TRIAL_DAYS);

        sqlx::query(
            r#"
            INSERT INTO license_cache (id, fingerprint, tier, status, trial_started_at, trial_ends_at)
            VALUES (1, ?, 'trial', 'trial', ?, ?)
            "#,
        )
        .bind(fingerprint)
        .bind(now.to_rfc3339())
        .bind(trial_ends.to_rfc3339())
        .execute(pool)
        .await
        .map_err(|e| e.to_string())?;

        // Log event
        log_license_event(
            pool,
            "trial_started",
            None,
            fingerprint,
            "trial",
            "TRIAL",
            None,
        )
        .await?;
    }

    Ok(())
}

/// Log a license event to history
async fn log_license_event(
    pool: &SqlitePool,
    event_type: &str,
    license_key: Option<&str>,
    fingerprint: &str,
    tier: &str,
    response_code: &str,
    response_detail: Option<&str>,
) -> Result<(), String> {
    // Mask license key for privacy
    let masked_key = license_key.map(|k| {
        if k.len() > 8 {
            format!("{}...{}", &k[..4], &k[k.len() - 4..])
        } else {
            "****".to_string()
        }
    });

    sqlx::query(
        r#"
        INSERT INTO license_history (event_type, license_key, fingerprint, tier, response_code, response_detail)
        VALUES (?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(event_type)
    .bind(masked_key)
    .bind(fingerprint)
    .bind(tier)
    .bind(response_code)
    .bind(response_detail)
    .execute(pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(())
}

// ═══════════════════════════════════════════════════════════════════
// KEYGEN API CLIENT
// ═══════════════════════════════════════════════════════════════════

/// Validate a license key with Keygen.sh
async fn validate_with_keygen(
    license_key: &str,
    fingerprint: &str,
) -> Result<KeygenValidateResponse, String> {
    let client = reqwest::Client::new();

    let url = format!(
        "{}/accounts/{}/licenses/actions/validate-key",
        KEYGEN_API_URL, KEYGEN_ACCOUNT_ID
    );

    let request_body = KeygenValidateRequest {
        meta: KeygenValidateMeta {
            key: license_key.to_string(),
            scope: KeygenValidateScope {
                fingerprint: fingerprint.to_string(),
            },
        },
    };

    let response = client
        .post(&url)
        .header("Content-Type", "application/vnd.api+json")
        .header("Accept", "application/vnd.api+json")
        .json(&request_body)
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    let response_body: KeygenValidateResponse = response
        .json()
        .await
        .map_err(|e| format!("Parse error: {}", e))?;

    Ok(response_body)
}

/// Activate a machine with Keygen.sh
async fn activate_machine_with_keygen(
    license_id: &str,
    fingerprint: &str,
    machine_name: &str,
    platform: &str,
    license_key: &str,
) -> Result<String, String> {
    let client = reqwest::Client::new();

    let url = format!("{}/accounts/{}/machines", KEYGEN_API_URL, KEYGEN_ACCOUNT_ID);

    let request_body = KeygenActivateRequest {
        data: KeygenMachineData {
            data_type: "machines".to_string(),
            attributes: KeygenMachineAttributes {
                fingerprint: fingerprint.to_string(),
                name: machine_name.to_string(),
                platform: platform.to_string(),
            },
            relationships: KeygenMachineRelationships {
                license: KeygenRelationship {
                    data: KeygenRelationshipData {
                        data_type: "licenses".to_string(),
                        id: license_id.to_string(),
                    },
                },
            },
        },
    };

    // Use license key as bearer token for machine creation
    let response = client
        .post(&url)
        .header("Content-Type", "application/vnd.api+json")
        .header("Accept", "application/vnd.api+json")
        .header("Authorization", format!("License {}", license_key))
        .json(&request_body)
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    if response.status().is_success() {
        let body: serde_json::Value = response.json().await.map_err(|e| e.to_string())?;
        let machine_id = body["data"]["id"].as_str().unwrap_or("").to_string();
        Ok(machine_id)
    } else {
        let body: serde_json::Value = response.json().await.unwrap_or_default();
        let error_detail = body["errors"][0]["detail"]
            .as_str()
            .unwrap_or("Unknown error");
        Err(format!("Activation failed: {}", error_detail))
    }
}

// ═══════════════════════════════════════════════════════════════════
// TAURI COMMANDS
// ═══════════════════════════════════════════════════════════════════

/// Get current license status
#[tauri::command]
pub async fn get_license_status(pool: State<'_, SqlitePool>) -> Result<LicenseStatus, String> {
    let fingerprint = generate_fingerprint();

    // Ensure trial is initialized
    init_trial_if_needed(pool.inner(), &fingerprint).await?;

    // Get cached license
    let cache: Option<(
        Option<String>, // license_key
        Option<String>, // license_id
        Option<String>, // machine_id
        String,         // fingerprint
        String,         // tier
        String,         // status
        Option<String>, // trial_started_at
        Option<String>, // trial_ends_at
        Option<String>, // expiry_date
        Option<String>, // last_validated_at
    )> = sqlx::query_as(
        r#"
        SELECT license_key, license_id, machine_id, fingerprint, tier, status,
               trial_started_at, trial_ends_at, expiry_date, last_validated_at
        FROM license_cache WHERE id = 1
        "#,
    )
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| e.to_string())?;

    let machine_name = get_machine_name();

    match cache {
        Some((
            license_key,
            _license_id,
            _machine_id,
            _fp,
            tier,
            status,
            _trial_started,
            trial_ends_at,
            expiry_date,
            last_validated,
        )) => {
            let now = Utc::now();
            let is_activated = license_key.is_some();

            // Calculate days remaining
            let (days_remaining, effective_expiry) = if status == "trial" {
                if let Some(ref trial_end) = trial_ends_at {
                    if let Ok(end_date) = DateTime::parse_from_rfc3339(trial_end) {
                        let days = (end_date.with_timezone(&Utc) - now).num_days() as i32;
                        (Some(days.max(0)), trial_ends_at.clone())
                    } else {
                        (None, None)
                    }
                } else {
                    (None, None)
                }
            } else if let Some(ref exp) = expiry_date {
                if let Ok(exp_date) = DateTime::parse_from_rfc3339(exp) {
                    let days = (exp_date.with_timezone(&Utc) - now).num_days() as i32;
                    (Some(days.max(0)), expiry_date.clone())
                } else {
                    (None, expiry_date.clone())
                }
            } else {
                (None, None)
            };

            // Determine validity
            let is_valid = match status.as_str() {
                "trial" => days_remaining.map(|d| d > 0).unwrap_or(false),
                "active" => days_remaining.map(|d| d > 0).unwrap_or(true),
                _ => false,
            };

            let validation_code = if !is_valid {
                if status == "trial" {
                    "TRIAL_EXPIRED".to_string()
                } else {
                    "EXPIRED".to_string()
                }
            } else if status == "trial" {
                "TRIAL".to_string()
            } else {
                "VALID".to_string()
            };

            Ok(LicenseStatus {
                is_valid,
                is_activated,
                tier,
                status,
                days_remaining,
                expiry_date: effective_expiry,
                machine_fingerprint: fingerprint,
                machine_name: Some(machine_name),
                trial_ends_at,
                last_validated_at: last_validated,
                validation_code,
            })
        }
        None => {
            // No cache, return no license status
            Ok(LicenseStatus {
                is_valid: false,
                is_activated: false,
                tier: "none".to_string(),
                status: "none".to_string(),
                days_remaining: None,
                expiry_date: None,
                machine_fingerprint: fingerprint,
                machine_name: Some(machine_name),
                trial_ends_at: None,
                last_validated_at: None,
                validation_code: "NO_LICENSE".to_string(),
            })
        }
    }
}

/// Activate a license key
#[tauri::command]
pub async fn activate_license(
    pool: State<'_, SqlitePool>,
    license_key: String,
) -> Result<ActivationResult, String> {
    let fingerprint = generate_fingerprint();
    let machine_name = get_machine_name();
    let platform = get_platform();

    // Validate with Keygen
    let validation = validate_with_keygen(&license_key, &fingerprint).await?;

    if let Some(meta) = &validation.meta {
        if meta.valid {
            // License is valid for this machine
            let license_data = validation.data.clone().ok_or("No license data returned")?;
            let tier = license_data
                .attributes
                .metadata
                .as_ref()
                .and_then(|m| m.get("tier"))
                .and_then(|t| t.as_str())
                .unwrap_or("base")
                .to_string();

            // Update cache
            let now = Utc::now();
            sqlx::query(
                r#"
                UPDATE license_cache SET
                    license_key = ?,
                    license_id = ?,
                    tier = ?,
                    status = 'active',
                    expiry_date = ?,
                    last_validated_at = ?,
                    validation_response = ?,
                    updated_at = ?
                WHERE id = 1
                "#,
            )
            .bind(&license_key)
            .bind(&license_data.id)
            .bind(&tier)
            .bind(&license_data.attributes.expiry)
            .bind(now.to_rfc3339())
            .bind(serde_json::to_string(&validation).ok())
            .bind(now.to_rfc3339())
            .execute(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

            // Log event
            log_license_event(
                pool.inner(),
                "activated",
                Some(&license_key),
                &fingerprint,
                &tier,
                &meta.code,
                meta.detail.as_deref(),
            )
            .await?;

            return Ok(ActivationResult {
                success: true,
                message: "Licenza attivata con successo!".to_string(),
                tier: Some(tier),
                expiry_date: license_data.attributes.expiry,
            });
        } else if meta.code == "NO_MACHINES" || meta.code == "NO_MACHINE" {
            // Need to activate machine first
            let license_data = validation.data.clone().ok_or("No license data returned")?;

            // Try to activate machine
            let machine_id = activate_machine_with_keygen(
                &license_data.id,
                &fingerprint,
                &machine_name,
                &platform,
                &license_key,
            )
            .await?;

            let tier = license_data
                .attributes
                .metadata
                .as_ref()
                .and_then(|m| m.get("tier"))
                .and_then(|t| t.as_str())
                .unwrap_or("base")
                .to_string();

            // Update cache
            let now = Utc::now();
            sqlx::query(
                r#"
                UPDATE license_cache SET
                    license_key = ?,
                    license_id = ?,
                    machine_id = ?,
                    tier = ?,
                    status = 'active',
                    expiry_date = ?,
                    last_validated_at = ?,
                    updated_at = ?
                WHERE id = 1
                "#,
            )
            .bind(&license_key)
            .bind(&license_data.id)
            .bind(&machine_id)
            .bind(&tier)
            .bind(&license_data.attributes.expiry)
            .bind(now.to_rfc3339())
            .bind(now.to_rfc3339())
            .execute(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

            // Log event
            log_license_event(
                pool.inner(),
                "activated",
                Some(&license_key),
                &fingerprint,
                &tier,
                "ACTIVATED",
                Some("Machine registered"),
            )
            .await?;

            return Ok(ActivationResult {
                success: true,
                message: "Licenza attivata con successo!".to_string(),
                tier: Some(tier),
                expiry_date: license_data.attributes.expiry,
            });
        } else {
            // Validation failed
            let detail = meta.detail.clone().unwrap_or_else(|| meta.code.clone());

            // Log event
            log_license_event(
                pool.inner(),
                "activation_failed",
                Some(&license_key),
                &fingerprint,
                "none",
                &meta.code,
                Some(&detail),
            )
            .await?;

            let message = match meta.code.as_str() {
                "EXPIRED" => "La licenza è scaduta. Rinnovala per continuare.",
                "SUSPENDED" => "La licenza è stata sospesa. Contatta il supporto.",
                "TOO_MANY_MACHINES" => {
                    "Hai raggiunto il limite di dispositivi. Disattiva un altro dispositivo."
                }
                "NOT_FOUND" => "Chiave di licenza non valida.",
                _ => &detail,
            };

            return Ok(ActivationResult {
                success: false,
                message: message.to_string(),
                tier: None,
                expiry_date: None,
            });
        }
    }

    // Handle errors
    if let Some(errors) = validation.errors {
        let error_msg = errors
            .first()
            .map(|e| e.detail.clone().unwrap_or_else(|| e.title.clone()))
            .unwrap_or_else(|| "Errore sconosciuto".to_string());

        return Ok(ActivationResult {
            success: false,
            message: error_msg,
            tier: None,
            expiry_date: None,
        });
    }

    Ok(ActivationResult {
        success: false,
        message: "Errore nella validazione della licenza".to_string(),
        tier: None,
        expiry_date: None,
    })
}

/// Deactivate license (release machine slot)
#[tauri::command]
pub async fn deactivate_license(pool: State<'_, SqlitePool>) -> Result<(), String> {
    let fingerprint = generate_fingerprint();

    // Get current machine_id
    let cache: Option<(Option<String>, Option<String>)> =
        sqlx::query_as("SELECT machine_id, license_key FROM license_cache WHERE id = 1")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    if let Some((Some(machine_id), license_key)) = cache {
        // Deactivate machine with Keygen
        let client = reqwest::Client::new();
        let url = format!(
            "{}/accounts/{}/machines/{}",
            KEYGEN_API_URL, KEYGEN_ACCOUNT_ID, machine_id
        );

        if let Some(key) = &license_key {
            let _ = client
                .delete(&url)
                .header("Authorization", format!("License {}", key))
                .send()
                .await;
        }
    }

    // Reset to trial mode
    let now = Utc::now();
    let trial_ends = now + Duration::days(TRIAL_DAYS);

    sqlx::query(
        r#"
        UPDATE license_cache SET
            license_key = NULL,
            license_id = NULL,
            machine_id = NULL,
            tier = 'trial',
            status = 'trial',
            trial_started_at = ?,
            trial_ends_at = ?,
            expiry_date = NULL,
            last_validated_at = NULL,
            validation_response = NULL,
            updated_at = ?
        WHERE id = 1
        "#,
    )
    .bind(now.to_rfc3339())
    .bind(trial_ends.to_rfc3339())
    .bind(now.to_rfc3339())
    .execute(pool.inner())
    .await
    .map_err(|e| e.to_string())?;

    // Log event
    log_license_event(
        pool.inner(),
        "deactivated",
        None,
        &fingerprint,
        "trial",
        "DEACTIVATED",
        None,
    )
    .await?;

    Ok(())
}

/// Force online validation
#[tauri::command]
pub async fn validate_license_online(pool: State<'_, SqlitePool>) -> Result<LicenseStatus, String> {
    let fingerprint = generate_fingerprint();

    // Get cached license key
    let cache: Option<(Option<String>,)> =
        sqlx::query_as("SELECT license_key FROM license_cache WHERE id = 1")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    if let Some((Some(license_key),)) = cache {
        // Validate online
        let validation = validate_with_keygen(&license_key, &fingerprint).await?;

        if let Some(meta) = &validation.meta {
            let now = Utc::now();

            if meta.valid {
                // Update last validated
                sqlx::query(
                    "UPDATE license_cache SET last_validated_at = ?, updated_at = ? WHERE id = 1",
                )
                .bind(now.to_rfc3339())
                .bind(now.to_rfc3339())
                .execute(pool.inner())
                .await
                .map_err(|e| e.to_string())?;

                // Log event
                log_license_event(
                    pool.inner(),
                    "validated",
                    Some(&license_key),
                    &fingerprint,
                    "active",
                    &meta.code,
                    None,
                )
                .await?;
            } else {
                // License no longer valid
                sqlx::query(
                    "UPDATE license_cache SET status = 'expired', updated_at = ? WHERE id = 1",
                )
                .bind(now.to_rfc3339())
                .execute(pool.inner())
                .await
                .map_err(|e| e.to_string())?;

                // Log event
                log_license_event(
                    pool.inner(),
                    "validation_failed",
                    Some(&license_key),
                    &fingerprint,
                    "expired",
                    &meta.code,
                    meta.detail.as_deref(),
                )
                .await?;
            }
        }
    }

    // Return updated status
    get_license_status(pool).await
}

/// Get machine fingerprint (for display)
#[tauri::command]
pub fn get_machine_fingerprint() -> String {
    generate_fingerprint()
}

/// Check if a feature is available for the current license tier
#[tauri::command]
pub async fn check_feature_access(
    pool: State<'_, SqlitePool>,
    feature: String,
) -> Result<bool, String> {
    let status = get_license_status(pool).await?;

    if !status.is_valid {
        return Ok(false);
    }

    // Feature access by tier
    let ia_features = ["voice_agent", "whatsapp_ai", "rag_chat"];

    if ia_features.contains(&feature.as_str()) {
        // IA features require 'ia' tier
        Ok(status.tier == "ia")
    } else {
        // Base features available in trial, base, and ia
        Ok(true)
    }
}
