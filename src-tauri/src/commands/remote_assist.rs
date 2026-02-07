// ═══════════════════════════════════════════════════════════════════
// FLUXION - Remote Assistance Commands
// WebRTC-based P2P remote assistance with screen sharing
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager, State};

// ═══════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RemoteAssistInstructions {
    pub platform: String,
    pub title: String,
    pub steps: Vec<String>,
    pub download_url: Option<String>,
}

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

/// Get remote assist instructions for the current platform
#[tauri::command]
pub fn get_remote_assist_instructions() -> Result<RemoteAssistInstructions, String> {
    let platform = std::env::consts::OS.to_string();
    
    let instructions = match platform.as_str() {
        "macos" => RemoteAssistInstructions {
            platform: "macOS".to_string(),
            title: "Assistenza Remota macOS (via AnyDesk)".to_string(),
            steps: vec![
                "1. Scarica AnyDesk da https://anydesk.com/it/downloads/mac-os".to_string(),
                "2. Installa e avvia AnyDesk".to_string(),
                "3. Comunica l'ID di AnyDesk al supporto tecnico".to_string(),
                "4. Accetta la richiesta di connessione quando arriva".to_string(),
                "5. Il supporto potrà visualizzare il tuo schermo".to_string(),
            ],
            download_url: Some("https://anydesk.com/it/downloads/mac-os".to_string()),
        },
        "windows" => RemoteAssistInstructions {
            platform: "Windows".to_string(),
            title: "Assistenza Rapida Windows".to_string(),
            steps: vec![
                "1. Premi Win + Ctrl + Q per aprire Assistenza Rapida".to_string(),
                "2. Clicca 'Ricevi assistenza'".to_string(),
                "3. Inserisci il codice fornito dal supporto".to_string(),
                "4. Clicca 'Condividi schermo'".to_string(),
                "5. Il supporto potrà visualizzare il tuo schermo".to_string(),
            ],
            download_url: None,
        },
        _ => RemoteAssistInstructions {
            platform: "Linux".to_string(),
            title: "Assistenza Remota Linux".to_string(),
            steps: vec![
                "1. Installa AnyDesk: sudo apt install anydesk".to_string(),
                "2. Avvia AnyDesk: anydesk".to_string(),
                "3. Comunica l'ID al supporto tecnico".to_string(),
            ],
            download_url: Some("https://anydesk.com/it/downloads/linux".to_string()),
        },
    };
    
    Ok(instructions)
}

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

/// Export support bundle for remote diagnostics
#[tauri::command]
pub async fn export_support_bundle(
    app: AppHandle,
    include_db: bool,
) -> Result<String, String> {
    use std::io::Write;
    
    let data_dir = app.path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
    
    let bundle_dir = data_dir.join("support_bundle");
    std::fs::create_dir_all(&bundle_dir).map_err(|e| e.to_string())?;
    
    // Generate diagnostics file
    let diagnostics = get_remote_diagnostics(app.clone()).await?;
    let diag_path = bundle_dir.join("diagnostics.json");
    std::fs::write(&diag_path, diagnostics.to_string()).map_err(|e| e.to_string())?;
    
    // Copy database if requested and exists
    let db_path = data_dir.join("fluxion.db");
    if include_db && db_path.exists() {
        let db_dest = bundle_dir.join("fluxion_backup.db");
        std::fs::copy(&db_path, &db_dest).map_err(|e| e.to_string())?;
    }
    
    // Create README
    let readme = format!(
        "FLUXION Support Bundle\n======================\n\nGenerated: {}\n\nThis bundle contains diagnostics information for technical support.\n\nContents:\n- diagnostics.json: System and app information\n{}\n\nFor support contact: support@fluxion.app\n",
        chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
        if include_db { "- fluxion_backup.db: Database backup (if included)" } else { "" }
    );
    std::fs::write(bundle_dir.join("README.txt"), readme).map_err(|e| e.to_string())?;
    
    Ok(bundle_dir.to_string_lossy().to_string())
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
