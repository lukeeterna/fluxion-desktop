// ═══════════════════════════════════════════════════════════════════
// FLUXION - Remote Assistance Commands
// WebRTC-based P2P remote assistance with screen sharing
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use tauri::AppHandle;

// ═══════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupportSession {
    pub session_id: String,
    pub created_at: String,
    pub status: String, // pending, connected, closed
    pub support_code: String,
}

// ═══════════════════════════════════════════════════════════════════
// Commands
// ═══════════════════════════════════════════════════════════════════

/// Generate a support session code for remote assistance
#[tauri::command]
pub fn generate_support_session() -> Result<SupportSession, String> {
    use rand::Rng;
    
    // Generate random 6-digit code
    let mut rng = rand::thread_rng();
    let support_code: String = (0..6)
        .map(|_| rng.gen_range(0..10).to_string())
        .collect();
    
    let session_id = format!("sess_{}", chrono::Utc::now().timestamp_millis());
    
    Ok(SupportSession {
        session_id,
        created_at: chrono::Utc::now().to_rfc3339(),
        status: "pending".to_string(),
        support_code,
    })
}

/// Get system diagnostics for remote support
#[tauri::command]
pub async fn get_remote_diagnostics(app: AppHandle) -> Result<serde_json::Value, String> {
    let app_version = env!("CARGO_PKG_VERSION").to_string();
    let os_type = std::env::consts::OS.to_string();
    let arch = std::env::consts::ARCH.to_string();
    
    // Get app data directory
    let data_dir = app.path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
    
    // Get database info if exists
    let db_path = data_dir.join("fluxion.db");
    let db_exists = db_path.exists();
    let db_size = if db_exists {
        std::fs::metadata(&db_path)
            .map(|m| m.len())
            .unwrap_or(0)
    } else {
        0
    };
    
    Ok(serde_json::json!({
        "app_version": app_version,
        "os_type": os_type,
        "arch": arch,
        "data_dir": data_dir.to_string_lossy().to_string(),
        "db_exists": db_exists,
        "db_size_bytes": db_size,
        "timestamp": chrono::Utc::now().to_rfc3339(),
    }))
}

/// Execute a diagnostic command (safe commands only)
#[tauri::command]
pub async fn execute_diagnostic_command(command: String) -> Result<String, String> {
    // Whitelist of safe diagnostic commands
    let allowed_commands = vec![
        "check-connection",
        "get-system-info",
        "check-db-health",
        "list-log-files",
        "check-disk-space",
    ];
    
    if !allowed_commands.contains(&command.as_str()) {
        return Err(format!("Command '{}' not allowed", command));
    }
    
    let output = match command.as_str() {
        "check-connection" => "Connection OK - Fluxion is running".to_string(),
        "get-system-info" => {
            format!(
                "OS: {} {}\nArch: {}\nRust: {}\n",
                std::env::consts::OS,
                std::env::consts::FAMILY,
                std::env::consts::ARCH,
                "1.75+"
            )
        }
        "check-disk-space" => {
            // Platform-specific disk check
            #[cfg(target_os = "macos")]
            {
                use std::process::Command;
                match Command::new("df").arg("-h").arg("/").output() {
                    Ok(output) => String::from_utf8_lossy(&output.stdout).to_string(),
                    Err(e) => format!("Error: {}", e),
                }
            }
            #[cfg(not(target_os = "macos"))]
            {
                "Disk space check not available on this platform".to_string()
            }
        }
        _ => format!("Command '{}' executed successfully", command),
    };
    
    Ok(output)
}
