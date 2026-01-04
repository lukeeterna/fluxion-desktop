// ═══════════════════════════════════════════════════════════════════
// FLUXION - Support & Diagnostics Commands (Fase 4 - Fluxion Care)
// Export bundle, backup/restore DB, diagnostics panel
// ═══════════════════════════════════════════════════════════════════

use crate::AppState;
use chrono::{DateTime, Local, Utc};
use serde::Serialize;
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;
use tauri::{AppHandle, Manager, State};
use zip::write::SimpleFileOptions;
use zip::ZipWriter;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
pub struct DiagnosticsInfo {
    pub app_version: String,
    pub app_name: String,
    pub os_type: String,
    pub os_version: String,
    pub arch: String,
    pub data_dir: String,
    pub db_path: String,
    pub db_size_bytes: u64,
    pub db_size_human: String,
    pub last_backup: Option<String>,
    pub disk_free_bytes: u64,
    pub disk_free_human: String,
    pub tables_count: i32,
    pub clienti_count: i32,
    pub appuntamenti_count: i32,
    pub collected_at: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct SupportBundleResult {
    pub path: String,
    pub size_bytes: u64,
    pub size_human: String,
    pub contents: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct BackupResult {
    pub path: String,
    pub size_bytes: u64,
    pub created_at: String,
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

fn human_readable_size(bytes: u64) -> String {
    const KB: u64 = 1024;
    const MB: u64 = KB * 1024;
    const GB: u64 = MB * 1024;

    if bytes >= GB {
        format!("{:.2} GB", bytes as f64 / GB as f64)
    } else if bytes >= MB {
        format!("{:.2} MB", bytes as f64 / MB as f64)
    } else if bytes >= KB {
        format!("{:.2} KB", bytes as f64 / KB as f64)
    } else {
        format!("{} B", bytes)
    }
}

fn get_disk_free_space(path: &PathBuf) -> u64 {
    // Platform-specific disk space check
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        if let Ok(output) = Command::new("df")
            .arg("-k")
            .arg(path.to_string_lossy().to_string())
            .output()
        {
            if let Ok(stdout) = String::from_utf8(output.stdout) {
                // Parse df output (second line, fourth column = available KB)
                if let Some(line) = stdout.lines().nth(1) {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if parts.len() >= 4 {
                        if let Ok(kb) = parts[3].parse::<u64>() {
                            return kb * 1024;
                        }
                    }
                }
            }
        }
        0
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        // Use wmic for Windows
        if let Some(drive) = path.to_string_lossy().chars().next() {
            if let Ok(output) = Command::new("wmic")
                .args(&["logicaldisk", "where", &format!("DeviceID='{}':", drive), "get", "FreeSpace"])
                .output()
            {
                if let Ok(stdout) = String::from_utf8(output.stdout) {
                    for line in stdout.lines().skip(1) {
                        if let Ok(bytes) = line.trim().parse::<u64>() {
                            return bytes;
                        }
                    }
                }
            }
        }
        0
    }

    #[cfg(not(any(target_os = "macos", target_os = "windows")))]
    {
        0
    }
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get comprehensive diagnostics information
#[tauri::command]
pub async fn get_diagnostics_info(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<DiagnosticsInfo, String> {
    let pool = &state.db;

    // App info from Cargo.toml
    let app_version = env!("CARGO_PKG_VERSION").to_string();
    let app_name = env!("CARGO_PKG_NAME").to_string();

    // OS info
    let os_type = std::env::consts::OS.to_string();
    let os_version = os_info::get().version().to_string();
    let arch = std::env::consts::ARCH.to_string();

    // Data directory
    let data_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|_| "Unknown".to_string());

    // DB path and size
    let db_path_buf = app
        .path()
        .app_data_dir()
        .map(|p| p.join("fluxion.db"))
        .map_err(|e| format!("Failed to get db path: {}", e))?;
    let db_path = db_path_buf.to_string_lossy().to_string();

    let db_size_bytes = fs::metadata(&db_path_buf)
        .map(|m| m.len())
        .unwrap_or(0);
    let db_size_human = human_readable_size(db_size_bytes);

    // Last backup check
    let backup_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.join("backups"))
        .map_err(|e| format!("Failed to get backup dir: {}", e))?;

    let last_backup = if backup_dir.exists() {
        fs::read_dir(&backup_dir)
            .ok()
            .and_then(|entries| {
                entries
                    .filter_map(|e| e.ok())
                    .filter(|e| {
                        e.path()
                            .extension()
                            .map(|ext| ext == "db")
                            .unwrap_or(false)
                    })
                    .max_by_key(|e| e.metadata().ok().and_then(|m| m.modified().ok()))
                    .map(|e| {
                        e.metadata()
                            .ok()
                            .and_then(|m| m.modified().ok())
                            .map(|t| {
                                DateTime::<Local>::from(t)
                                    .format("%Y-%m-%d %H:%M")
                                    .to_string()
                            })
                            .unwrap_or_else(|| "Unknown".to_string())
                    })
            })
    } else {
        None
    };

    // Disk free space
    let disk_free_bytes = get_disk_free_space(&db_path_buf);
    let disk_free_human = human_readable_size(disk_free_bytes);

    // DB statistics
    let tables_count: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    .fetch_one(pool)
    .await
    .unwrap_or((0,));

    let clienti_count: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) FROM clienti WHERE deleted_at IS NULL"
    )
    .fetch_one(pool)
    .await
    .unwrap_or((0,));

    // Esclude sia soft delete (deleted_at) che stato 'cancellato' (legacy)
    let appuntamenti_count: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) FROM appuntamenti WHERE deleted_at IS NULL AND stato != 'cancellato'",
    )
    .fetch_one(pool)
    .await
    .unwrap_or((0,));

    Ok(DiagnosticsInfo {
        app_version,
        app_name,
        os_type,
        os_version,
        arch,
        data_dir,
        db_path,
        db_size_bytes,
        db_size_human,
        last_backup,
        disk_free_bytes,
        disk_free_human,
        tables_count: tables_count.0,
        clienti_count: clienti_count.0,
        appuntamenti_count: appuntamenti_count.0,
        collected_at: Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string(),
    })
}

/// Export support bundle (ZIP with logs, DB copy, diagnostics)
#[tauri::command]
pub async fn export_support_bundle(
    app: AppHandle,
    state: State<'_, AppState>,
    include_database: bool,
    output_path: String,
) -> Result<SupportBundleResult, String> {
    let output_path = PathBuf::from(output_path);

    // Create ZIP file
    let file = fs::File::create(&output_path)
        .map_err(|e| format!("Failed to create bundle file: {}", e))?;
    let mut zip = ZipWriter::new(file);
    let options = SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated);

    let mut contents = Vec::new();

    // 1. Diagnostics JSON
    let diagnostics = get_diagnostics_info(app.clone(), state.clone()).await?;
    let diagnostics_json = serde_json::to_string_pretty(&diagnostics)
        .map_err(|e| format!("Failed to serialize diagnostics: {}", e))?;

    zip.start_file("diagnostics.json", options)
        .map_err(|e| format!("ZIP error: {}", e))?;
    zip.write_all(diagnostics_json.as_bytes())
        .map_err(|e| format!("ZIP write error: {}", e))?;
    contents.push("diagnostics.json".to_string());

    // 2. System info text
    let system_info = format!(
        "FLUXION Support Bundle\n\
         =======================\n\
         Generated: {}\n\
         App Version: {}\n\
         OS: {} {} ({})\n\
         Data Dir: {}\n\
         DB Size: {}\n\
         Free Disk: {}\n\
         Clients: {}\n\
         Appointments: {}\n",
        diagnostics.collected_at,
        diagnostics.app_version,
        diagnostics.os_type,
        diagnostics.os_version,
        diagnostics.arch,
        diagnostics.data_dir,
        diagnostics.db_size_human,
        diagnostics.disk_free_human,
        diagnostics.clienti_count,
        diagnostics.appuntamenti_count
    );

    zip.start_file("system-info.txt", options)
        .map_err(|e| format!("ZIP error: {}", e))?;
    zip.write_all(system_info.as_bytes())
        .map_err(|e| format!("ZIP write error: {}", e))?;
    contents.push("system-info.txt".to_string());

    // 3. Database copy (optional)
    if include_database {
        let db_path = app
            .path()
            .app_data_dir()
            .map(|p| p.join("fluxion.db"))
            .map_err(|e| format!("Failed to get db path: {}", e))?;

        if db_path.exists() {
            let mut db_file = fs::File::open(&db_path)
                .map_err(|e| format!("Failed to open database: {}", e))?;
            let mut db_contents = Vec::new();
            db_file.read_to_end(&mut db_contents)
                .map_err(|e| format!("Failed to read database: {}", e))?;

            zip.start_file("fluxion.db", options)
                .map_err(|e| format!("ZIP error: {}", e))?;
            zip.write_all(&db_contents)
                .map_err(|e| format!("ZIP write error: {}", e))?;
            contents.push("fluxion.db".to_string());
        }
    }

    // 4. Tauri store/config (if exists)
    let store_path = app
        .path()
        .app_data_dir()
        .map(|p| p.join(".fluxion-store.json"))
        .ok();

    if let Some(store_path) = store_path {
        if store_path.exists() {
            let store_contents = fs::read_to_string(&store_path)
                .unwrap_or_else(|_| "{}".to_string());

            zip.start_file("store-config.json", options)
                .map_err(|e| format!("ZIP error: {}", e))?;
            zip.write_all(store_contents.as_bytes())
                .map_err(|e| format!("ZIP write error: {}", e))?;
            contents.push("store-config.json".to_string());
        }
    }

    // Finalize ZIP
    zip.finish().map_err(|e| format!("Failed to finalize ZIP: {}", e))?;

    // Get final size
    let size_bytes = fs::metadata(&output_path)
        .map(|m| m.len())
        .unwrap_or(0);

    Ok(SupportBundleResult {
        path: output_path.to_string_lossy().to_string(),
        size_bytes,
        size_human: human_readable_size(size_bytes),
        contents,
    })
}

/// Backup database (atomic copy)
#[tauri::command]
pub async fn backup_database(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<BackupResult, String> {
    let pool = &state.db;

    // Source DB path
    let db_path = app
        .path()
        .app_data_dir()
        .map(|p| p.join("fluxion.db"))
        .map_err(|e| format!("Failed to get db path: {}", e))?;

    if !db_path.exists() {
        return Err("Database file not found".to_string());
    }

    // Create backups directory
    let backup_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.join("backups"))
        .map_err(|e| format!("Failed to get backup dir: {}", e))?;

    fs::create_dir_all(&backup_dir)
        .map_err(|e| format!("Failed to create backup directory: {}", e))?;

    // Generate backup filename with timestamp
    let timestamp = Local::now().format("%Y%m%d_%H%M%S");
    let backup_filename = format!("fluxion_backup_{}.db", timestamp);
    let backup_path = backup_dir.join(&backup_filename);
    let temp_path = backup_dir.join(format!("{}.tmp", backup_filename));

    // Checkpoint WAL to ensure data is written to main DB
    sqlx::query("PRAGMA wal_checkpoint(TRUNCATE)")
        .execute(pool)
        .await
        .map_err(|e| format!("WAL checkpoint failed: {}", e))?;

    // Atomic copy: write to temp, then rename
    fs::copy(&db_path, &temp_path)
        .map_err(|e| format!("Failed to copy database: {}", e))?;

    // Verify temp file integrity
    let temp_size = fs::metadata(&temp_path)
        .map(|m| m.len())
        .unwrap_or(0);

    if temp_size == 0 {
        fs::remove_file(&temp_path).ok();
        return Err("Backup file is empty".to_string());
    }

    // Rename temp to final (atomic on most filesystems)
    fs::rename(&temp_path, &backup_path)
        .map_err(|e| format!("Failed to finalize backup: {}", e))?;

    let size_bytes = fs::metadata(&backup_path)
        .map(|m| m.len())
        .unwrap_or(0);

    Ok(BackupResult {
        path: backup_path.to_string_lossy().to_string(),
        size_bytes,
        created_at: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
    })
}

/// Restore database from backup
#[tauri::command]
pub async fn restore_database(
    app: AppHandle,
    backup_path: String,
) -> Result<String, String> {
    let backup_path = PathBuf::from(backup_path);

    if !backup_path.exists() {
        return Err("Backup file not found".to_string());
    }

    // Verify it's a valid SQLite file
    let mut file = fs::File::open(&backup_path)
        .map_err(|e| format!("Failed to open backup: {}", e))?;
    let mut header = [0u8; 16];
    file.read_exact(&mut header)
        .map_err(|e| format!("Failed to read backup header: {}", e))?;

    // SQLite magic header: "SQLite format 3\0"
    if &header[0..15] != b"SQLite format 3" {
        return Err("Invalid SQLite database file".to_string());
    }

    // Target DB path
    let db_path = app
        .path()
        .app_data_dir()
        .map(|p| p.join("fluxion.db"))
        .map_err(|e| format!("Failed to get db path: {}", e))?;

    // Create safety backup of current DB
    let safety_backup = app
        .path()
        .app_data_dir()
        .map(|p| p.join("fluxion_pre_restore.db"))
        .map_err(|e| format!("Failed to get safety backup path: {}", e))?;

    if db_path.exists() {
        fs::copy(&db_path, &safety_backup)
            .map_err(|e| format!("Failed to create safety backup: {}", e))?;
    }

    // Restore: copy backup to main DB
    fs::copy(&backup_path, &db_path)
        .map_err(|e| format!("Failed to restore database: {}", e))?;

    Ok(format!(
        "Database restored successfully. Previous DB saved at: {}",
        safety_backup.to_string_lossy()
    ))
}

/// Get list of available backups
#[tauri::command]
pub async fn list_backups(
    app: AppHandle,
) -> Result<Vec<BackupResult>, String> {
    let backup_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.join("backups"))
        .map_err(|e| format!("Failed to get backup dir: {}", e))?;

    if !backup_dir.exists() {
        return Ok(Vec::new());
    }

    let mut backups = Vec::new();

    for entry in fs::read_dir(&backup_dir).map_err(|e| format!("Failed to read backup dir: {}", e))? {
        let entry = entry.map_err(|e| format!("Failed to read entry: {}", e))?;
        let path = entry.path();

        if path.extension().map(|e| e == "db").unwrap_or(false) {
            let metadata = fs::metadata(&path).ok();
            let size_bytes = metadata.as_ref().map(|m| m.len()).unwrap_or(0);
            let created_at = metadata
                .and_then(|m| m.modified().ok())
                .map(|t| DateTime::<Local>::from(t).format("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_else(|| "Unknown".to_string());

            backups.push(BackupResult {
                path: path.to_string_lossy().to_string(),
                size_bytes,
                created_at,
            });
        }
    }

    // Sort by date (newest first)
    backups.sort_by(|a, b| b.created_at.cmp(&a.created_at));

    Ok(backups)
}

/// Get remote assist instructions (native OS)
#[tauri::command]
pub fn get_remote_assist_instructions() -> Result<RemoteAssistInstructions, String> {
    let os = std::env::consts::OS;

    let (title, steps, button_action) = match os {
        "macos" => (
            "Assistenza Remota macOS (via AnyDesk)",
            vec![
                "1. Scarica AnyDesk da: anydesk.com/it/downloads",
                "2. Apri AnyDesk e nota il tuo ID (9 cifre)",
                "3. Comunica l'ID al supporto tecnico",
                "4. Accetta la richiesta di connessione",
                "5. Il supporto potrà visualizzare il tuo schermo",
                "",
                "Nota: AnyDesk è gratuito per uso personale",
            ],
            "https://anydesk.com/it/downloads/mac",
        ),
        "windows" => (
            "Assistenza Rapida Windows",
            vec![
                "1. Premi Win + Ctrl + Q per aprire Assistenza Rapida",
                "2. Clicca 'Ricevi assistenza'",
                "3. Comunica il codice a 6 cifre al supporto",
                "4. Accetta la richiesta di connessione",
                "5. Il supporto potrà visualizzare il tuo schermo",
            ],
            "ms-quick-assist:",
        ),
        _ => (
            "Assistenza Remota",
            vec![
                "1. Installa un client VNC (es. TigerVNC)",
                "2. Configura la condivisione schermo",
                "3. Comunica l'indirizzo IP al supporto",
            ],
            "",
        ),
    };

    Ok(RemoteAssistInstructions {
        os: os.to_string(),
        title: title.to_string(),
        steps: steps.iter().map(|s| s.to_string()).collect(),
        button_action: button_action.to_string(),
    })
}

#[derive(Debug, Clone, Serialize)]
pub struct RemoteAssistInstructions {
    pub os: String,
    pub title: String,
    pub steps: Vec<String>,
    pub button_action: String,
}
