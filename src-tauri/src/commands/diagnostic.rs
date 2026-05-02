// ═══════════════════════════════════════════════════════════════════
// FLUXION — S184 α.3.1-F Diagnostic Send-report
// 2 Tauri commands:
//   - collect_diagnostic   → JSON payload privacy-safe (no PII clienti)
//   - send_diagnostic_report → POST a CF Worker /api/v1/diagnostic-report
//                              (Worker → Resend API → fluxion.gestionale@gmail.com)
//
// Privacy: ZERO dati cliente (nomi, telefoni, email, transcript, XML SDI).
// Solo: app version, OS, percorsi anonimizzati, conteggi tabelle, esiti probe.
// ═══════════════════════════════════════════════════════════════════

use crate::commands::preflight::{
    check_db_path, check_network, check_ports, check_voice_ready, DbPathCheck, NetworkCheck,
    PortsCheck, VoiceReadyCheck,
};
use crate::detect_cloud_sync_provider;
use crate::AppState;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tauri::{AppHandle, Manager, State};

// ───────────────────────────────────────────────────────────────────
// Constants
// ───────────────────────────────────────────────────────────────────

const DIAGNOSTIC_REPORT_URL: &str =
    "https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/diagnostic-report";
const SEND_TIMEOUT_MS: u64 = 10_000;
const MAX_USER_MESSAGE_CHARS: usize = 2_000;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
pub struct DiagnosticPayload {
    pub schema_version: u32,
    pub generated_at: String,
    pub app_version: String,
    pub fluxion_env: String,
    pub os: String,
    pub os_version: String,
    pub arch: String,
    pub locale: String,
    pub db_size_bytes: u64,
    pub db_path_anonymized: String,
    pub cloud_sync_provider: Option<String>,
    pub free_disk_bytes: u64,
    pub tables_count: i32,
    pub clienti_count: i32,
    pub appuntamenti_count: i32,
    pub network: NetworkCheck,
    pub db_path_check: DbPathCheck,
    pub ports: PortsCheck,
    pub voice: VoiceReadyCheck,
    pub last_backup_age_days: Option<i64>,
    /// Sentry event IDs raccolti lato JS (passati dal FE a send_diagnostic_report)
    pub sentry_event_ids: Vec<String>,
    /// Hash anonimo della macchina (no PII, solo correlation server-side)
    pub machine_hash: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SendDiagnosticArgs {
    pub user_email: String,
    pub user_message: String,
    pub sentry_event_ids: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize)]
pub struct SendDiagnosticResult {
    pub ok: bool,
    pub ticket_id: Option<String>,
    pub message: String,
}

// ───────────────────────────────────────────────────────────────────
// 1) collect_diagnostic — privacy-safe payload
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn collect_diagnostic(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<DiagnosticPayload, String> {
    let pool = &state.db;

    // App + OS metadata
    let app_version = env!("CARGO_PKG_VERSION").to_string();
    let os = std::env::consts::OS.to_string();
    let arch = std::env::consts::ARCH.to_string();
    let os_version = os_info::get().version().to_string();
    let locale = std::env::var("LANG").unwrap_or_else(|_| "unknown".to_string());
    let fluxion_env =
        std::env::var("FLUXION_ENV").unwrap_or_else(|_| "production".to_string());

    // DB metadata
    let app_data_dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let db_path = app_data_dir.join("fluxion.db");
    let db_size_bytes = std::fs::metadata(&db_path).map(|m| m.len()).unwrap_or(0);
    let cloud_sync_provider = detect_cloud_sync_provider(&db_path).map(String::from);

    // Anonymize DB path: strip user home, keep only "<APPDATA>/fluxion.db"
    let db_path_anonymized = anonymize_path(&db_path.to_string_lossy());

    // Counts (no PII content, only cardinality)
    let tables_count: i32 =
        sqlx::query_scalar("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            .fetch_one(pool)
            .await
            .unwrap_or(0);
    let clienti_count: i32 = sqlx::query_scalar("SELECT COUNT(*) FROM clienti")
        .fetch_one(pool)
        .await
        .unwrap_or(0);
    let appuntamenti_count: i32 = sqlx::query_scalar("SELECT COUNT(*) FROM appuntamenti")
        .fetch_one(pool)
        .await
        .unwrap_or(0);

    // Pre-flight probes (parallel)
    let (network, db_path_check, ports, voice) = tokio::join!(
        check_network(),
        check_db_path(app.clone()),
        async { check_ports() },
        check_voice_ready(),
    );
    let network = network.unwrap_or_else(|_| NetworkCheck {
        online: false,
        status: "unknown".to_string(),
        proxy_reachable: false,
        latency_ms: None,
        message: "probe failed".to_string(),
    });
    let db_path_check = db_path_check.unwrap_or_else(|_| DbPathCheck {
        path: db_path_anonymized.clone(),
        writable: false,
        cloud_provider: cloud_sync_provider.clone(),
        free_disk_bytes: 0,
        warning: Some("probe failed".to_string()),
    });
    let ports = ports.unwrap_or_else(|_| PortsCheck {
        http_bridge_busy: false,
        voice_pipeline_busy: false,
        conflict: false,
        message: "probe failed".to_string(),
    });
    let voice = voice.unwrap_or_else(|_| VoiceReadyCheck {
        ready: false,
        status: "probe_failed".to_string(),
        version: None,
        error: Some("probe failed".to_string()),
    });

    // Last backup age
    let last_backup_age_days = compute_last_backup_age_days(&app_data_dir.join("backups"));

    // Machine hash (stable, non-reversible — for support correlation only)
    let machine_hash = compute_machine_hash();

    let free_disk_bytes = db_path_check.free_disk_bytes;

    Ok(DiagnosticPayload {
        schema_version: 1,
        generated_at: chrono::Utc::now().to_rfc3339(),
        app_version,
        fluxion_env,
        os,
        os_version,
        arch,
        locale,
        db_size_bytes,
        db_path_anonymized,
        cloud_sync_provider,
        free_disk_bytes,
        tables_count,
        clienti_count,
        appuntamenti_count,
        network,
        db_path_check,
        ports,
        voice,
        last_backup_age_days,
        sentry_event_ids: Vec::new(), // populated by send_diagnostic_report
        machine_hash,
    })
}

// ───────────────────────────────────────────────────────────────────
// 2) send_diagnostic_report — POST → CF Worker → Resend
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn send_diagnostic_report(
    app: AppHandle,
    state: State<'_, AppState>,
    args: SendDiagnosticArgs,
) -> Result<SendDiagnosticResult, String> {
    // Validate user email (basic format)
    let email = args.user_email.trim().to_lowercase();
    if !is_valid_email_basic(&email) {
        return Err("Email non valida. Inserisci un indirizzo email corretto.".to_string());
    }

    // Truncate user_message to safe length
    let user_message: String = args
        .user_message
        .chars()
        .take(MAX_USER_MESSAGE_CHARS)
        .collect();
    let user_message = user_message.trim().to_string();

    if user_message.is_empty() {
        return Err(
            "Descrivi brevemente il problema (almeno qualche parola) per aiutarci ad assisterti."
                .to_string(),
        );
    }

    // Collect payload
    let mut payload = collect_diagnostic(app, state).await?;
    if let Some(ids) = args.sentry_event_ids {
        payload.sentry_event_ids = ids
            .into_iter()
            .filter(|s| !s.is_empty() && s.len() <= 64)
            .take(10)
            .collect();
    }

    // POST to CF Worker
    let body = serde_json::json!({
        "user_email": email,
        "user_message": user_message,
        "diagnostic": payload,
    });

    let client = reqwest::Client::builder()
        .timeout(Duration::from_millis(SEND_TIMEOUT_MS))
        .build()
        .map_err(|e| format!("HTTP client init: {}", e))?;

    let response = client
        .post(DIAGNOSTIC_REPORT_URL)
        .header("Content-Type", "application/json")
        .body(body.to_string())
        .send()
        .await
        .map_err(|e| format!("Invio non riuscito (rete?): {}", e))?;

    let status = response.status();
    let resp_text = response
        .text()
        .await
        .unwrap_or_else(|_| "(risposta vuota)".to_string());

    if !status.is_success() {
        return Err(format!(
            "Server risponde HTTP {}. Riprova fra qualche minuto. ({})",
            status,
            resp_text.chars().take(120).collect::<String>()
        ));
    }

    // Parse ticket_id if present (Worker echoes it back)
    let ticket_id = serde_json::from_str::<serde_json::Value>(&resp_text)
        .ok()
        .and_then(|v| {
            v.get("ticket_id")
                .and_then(|s| s.as_str())
                .map(String::from)
        });

    Ok(SendDiagnosticResult {
        ok: true,
        ticket_id,
        message: "Rapporto inviato. Ti risponderemo a fluxion.gestionale@gmail.com entro 24h."
            .to_string(),
    })
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

fn anonymize_path(path: &str) -> String {
    // Replace user home prefix with <HOME>; works on macOS/Linux/Win
    if let Ok(home) = std::env::var("HOME") {
        if !home.is_empty() && path.starts_with(&home) {
            return path.replacen(&home, "<HOME>", 1);
        }
    }
    if let Ok(profile) = std::env::var("USERPROFILE") {
        if !profile.is_empty() && path.starts_with(&profile) {
            return path.replacen(&profile, "<HOME>", 1);
        }
    }
    // Fallback: keep as-is (Tauri app_data_dir is typically under home)
    path.to_string()
}

fn compute_last_backup_age_days(backup_dir: &std::path::Path) -> Option<i64> {
    if !backup_dir.exists() {
        return None;
    }
    let entries = std::fs::read_dir(backup_dir).ok()?;
    let latest = entries
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().map(|ext| ext == "db").unwrap_or(false))
        .filter_map(|e| e.metadata().and_then(|m| m.modified()).ok())
        .max()?;
    let elapsed = std::time::SystemTime::now().duration_since(latest).ok()?;
    Some(elapsed.as_secs() as i64 / 86_400)
}

fn compute_machine_hash() -> String {
    use sha2::{Digest, Sha256};

    // Stable inputs that DO NOT identify the user but DO identify the install
    let mut hasher = Sha256::new();
    hasher.update(std::env::consts::OS.as_bytes());
    hasher.update(std::env::consts::ARCH.as_bytes());
    if let Ok(hostname) = std::env::var("HOSTNAME") {
        hasher.update(hostname.as_bytes());
    }
    if let Ok(user) = std::env::var("USER") {
        // We hash USER to get a stable correlator without storing the username itself.
        hasher.update(user.as_bytes());
    }
    let hash = hasher.finalize();
    hex::encode(&hash[..8]) // 16 hex chars is enough for correlation
}

fn is_valid_email_basic(email: &str) -> bool {
    // Minimal RFC-5322ish: contains @, has dot in domain, no whitespace, length <= 254
    if email.len() > 254 || email.contains(' ') || email.contains('\n') {
        return false;
    }
    let parts: Vec<&str> = email.split('@').collect();
    if parts.len() != 2 {
        return false;
    }
    let (local, domain) = (parts[0], parts[1]);
    !local.is_empty() && domain.contains('.') && !domain.starts_with('.') && !domain.ends_with('.')
}

// ───────────────────────────────────────────────────────────────────
// Tests
// ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn email_basic_validation() {
        assert!(is_valid_email_basic("a@b.com"));
        assert!(is_valid_email_basic("user.name+tag@sub.example.it"));
        assert!(!is_valid_email_basic(""));
        assert!(!is_valid_email_basic("noatsign"));
        assert!(!is_valid_email_basic("two@@at.com"));
        assert!(!is_valid_email_basic("a@b"));
        assert!(!is_valid_email_basic("a @b.com"));
    }

    #[test]
    fn anonymize_strips_home() {
        std::env::set_var("HOME", "/Users/testuser");
        let p = "/Users/testuser/Library/Application Support/fluxion/fluxion.db";
        assert_eq!(
            anonymize_path(p),
            "<HOME>/Library/Application Support/fluxion/fluxion.db"
        );
    }

    #[test]
    fn machine_hash_stable_and_short() {
        let h1 = compute_machine_hash();
        let h2 = compute_machine_hash();
        assert_eq!(h1, h2);
        assert_eq!(h1.len(), 16);
        assert!(h1.chars().all(|c| c.is_ascii_hexdigit()));
    }
}
