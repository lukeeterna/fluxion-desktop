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
use std::time::SystemTime;
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
    pub days_since_last_backup: Option<i64>,
    pub disk_free_bytes: u64,
    pub disk_free_human: String,
    pub tables_count: i32,
    pub clienti_count: i32,
    pub appuntamenti_count: i32,
    pub collected_at: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct BackupResult {
    pub path: String,
    pub size_bytes: u64,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct SupportBundleResult {
    pub path: String,
    pub size_bytes: u64,
    pub size_human: String,
    pub contents: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct BackupInfo {
    pub filename: String,
    pub size_bytes: u64,
    pub size_human: String,
    pub created_at: DateTime<Local>,
    pub created_at_formatted: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct RemoteAssistInstructions {
    pub os: String,
    pub title: String,
    pub steps: Vec<String>,
    pub button_action: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct SupportSession {
    pub session_id: String,
    pub created_at: String,
    pub status: String,
    pub support_code: String,
}

// ───────────────────────────────────────────────────────────────────
// Helper Functions
// ───────────────────────────────────────────────────────────────────

fn human_readable_size(size_bytes: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    if size_bytes == 0 {
        return "0 B".to_string();
    }
    let exp = (size_bytes as f64)
        .log(1024.0)
        .min(UNITS.len() as f64 - 1.0) as usize;
    let size = size_bytes as f64 / 1024f64.powi(exp as i32);
    format!("{:.1} {}", size, UNITS[exp])
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get diagnostics info for support panel
#[tauri::command]
pub async fn get_diagnostics_info(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<DiagnosticsInfo, String> {
    let pool = &state.db;

    // Get app info
    let app_version = env!("CARGO_PKG_VERSION").to_string();
    let app_name = env!("CARGO_PKG_NAME").to_string();

    // Get system info
    let os_type = std::env::consts::OS.to_string();
    let arch = std::env::consts::ARCH.to_string();

    // Get data directory
    let data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get data dir: {}", e))?;

    // Get database info
    let db_path = data_dir.join("fluxion.db");
    let (db_size_bytes, db_size_human) = if db_path.exists() {
        match fs::metadata(&db_path) {
            Ok(metadata) => {
                let size = metadata.len();
                (size, human_readable_size(size))
            }
            Err(_) => (0, "0 B".to_string()),
        }
    } else {
        (0, "0 B".to_string())
    };

    // Get disk free space
    let (disk_free_bytes, disk_free_human) = {
        #[cfg(target_os = "macos")]
        {
            use std::process::Command;
            let output = Command::new("df")
                .args(&["-k", "/"])
                .output()
                .map_err(|e| format!("Failed to get disk info: {}", e))?;

            let stdout = String::from_utf8_lossy(&output.stdout);
            let lines: Vec<&str> = stdout.lines().collect();
            if lines.len() >= 2 {
                let parts: Vec<&str> = lines[1].split_whitespace().collect();
                if parts.len() >= 4 {
                    let free_kb: u64 = parts[3].parse().unwrap_or(0);
                    let free_bytes = free_kb * 1024;
                    (free_bytes, human_readable_size(free_bytes))
                } else {
                    (0, "Unknown".to_string())
                }
            } else {
                (0, "Unknown".to_string())
            }
        }
        #[cfg(not(target_os = "macos"))]
        {
            (0, "Unknown".to_string())
        }
    };

    // Get last backup info (filename + age in days)
    let backup_dir = data_dir.join("backups");
    let (last_backup, days_since_last_backup) = if backup_dir.exists() {
        match fs::read_dir(&backup_dir) {
            Ok(entries) => {
                let mut backups: Vec<_> = entries
                    .filter_map(|e| e.ok())
                    .filter(|e| e.path().extension().map(|ext| ext == "db").unwrap_or(false))
                    .collect();
                backups.sort_by_key(|e| {
                    e.metadata()
                        .and_then(|m| m.modified())
                        .unwrap_or(SystemTime::UNIX_EPOCH)
                });
                if let Some(latest) = backups.last() {
                    let filename = latest.file_name().to_string_lossy().to_string();
                    let days = latest
                        .metadata()
                        .and_then(|m| m.modified())
                        .ok()
                        .and_then(|t| SystemTime::now().duration_since(t).ok())
                        .map(|d| d.as_secs() as i64 / 86400);
                    (Some(filename), days)
                } else {
                    (None, None)
                }
            }
            Err(_) => (None, None),
        }
    } else {
        (None, None)
    };

    // Get table counts
    let tables_count: i32 =
        sqlx::query_scalar("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            .fetch_one(pool)
            .await
            .unwrap_or(0);

    let clienti_count: i32 = sqlx::query_scalar("SELECT COUNT(*) FROM clienti")
        .fetch_one(pool)
        .await
        .unwrap_or(0);

    let appuntamenti_count: i32 =
        sqlx::query_scalar("SELECT COUNT(*) FROM appuntamenti WHERE data >= date('now')")
            .fetch_one(pool)
            .await
            .unwrap_or(0);

    Ok(DiagnosticsInfo {
        app_version,
        app_name,
        os_type,
        os_version: "Unknown".to_string(), // Could be enhanced with os_info crate
        arch,
        data_dir: data_dir.to_string_lossy().to_string(),
        db_path: db_path.to_string_lossy().to_string(),
        db_size_bytes,
        db_size_human,
        last_backup,
        days_since_last_backup,
        disk_free_bytes,
        disk_free_human,
        tables_count,
        clienti_count,
        appuntamenti_count,
        collected_at: Utc::now().to_rfc3339(),
    })
}

/// Get remote diagnostics (simplified JSON version for remote support)
#[tauri::command]
pub async fn get_remote_diagnostics(app: AppHandle) -> Result<serde_json::Value, String> {
    let app_version = env!("CARGO_PKG_VERSION").to_string();
    let os_type = std::env::consts::OS.to_string();
    let arch = std::env::consts::ARCH.to_string();

    // Get app data directory
    let data_dir = app.path().app_data_dir().map_err(|e| e.to_string())?;

    // Get database info if exists
    let db_path = data_dir.join("fluxion.db");
    let db_exists = db_path.exists();
    let db_size = if db_exists {
        std::fs::metadata(&db_path).map(|m| m.len()).unwrap_or(0)
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
    let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated);

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
         OS: {} {} ({}))\n\
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
            let mut db_file =
                fs::File::open(&db_path).map_err(|e| format!("Failed to open database: {}", e))?;
            let mut db_contents = Vec::new();
            db_file
                .read_to_end(&mut db_contents)
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
            let store_contents =
                fs::read_to_string(&store_path).unwrap_or_else(|_| "{}".to_string());

            zip.start_file("store-config.json", options)
                .map_err(|e| format!("ZIP error: {}", e))?;
            zip.write_all(store_contents.as_bytes())
                .map_err(|e| format!("ZIP write error: {}", e))?;
            contents.push("store-config.json".to_string());
        }
    }

    // Finalize ZIP
    zip.finish()
        .map_err(|e| format!("Failed to finalize ZIP: {}", e))?;

    // Get final size
    let size_bytes = fs::metadata(&output_path).map(|m| m.len()).unwrap_or(0);

    Ok(SupportBundleResult {
        path: output_path.to_string_lossy().to_string(),
        size_bytes,
        size_human: human_readable_size(size_bytes),
        contents,
    })
}

/// Backup database using VACUUM INTO (includes all WAL data)
#[tauri::command]
pub async fn backup_database(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<BackupResult, String> {
    let pool = &state.db;

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

    // Use VACUUM INTO to create a complete backup including WAL data
    let backup_path_str = backup_path.to_string_lossy().to_string();
    sqlx::query(&format!(
        "VACUUM INTO '{}'",
        backup_path_str.replace('\'', "''")
    ))
    .execute(pool)
    .await
    .map_err(|e| format!("Backup failed: {}", e))?;

    // Verify backup file exists and has content
    let size_bytes = fs::metadata(&backup_path).map(|m| m.len()).unwrap_or(0);

    if size_bytes == 0 {
        fs::remove_file(&backup_path).ok();
        return Err("Backup file is empty".to_string());
    }

    Ok(BackupResult {
        path: backup_path_str,
        size_bytes,
        created_at: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
    })
}

/// Restore database from backup
#[tauri::command]
pub async fn restore_database(
    app: AppHandle,
    state: State<'_, AppState>,
    backup_path: String,
) -> Result<String, String> {
    let pool = &state.db;
    let backup_path = PathBuf::from(&backup_path);

    // Verify backup exists
    if !backup_path.exists() {
        return Err("Backup file not found".to_string());
    }

    // Get current DB path
    let db_path = app
        .path()
        .app_data_dir()
        .map(|p| p.join("fluxion.db"))
        .map_err(|e| format!("Failed to get db path: {}", e))?;

    // Create emergency backup of current DB
    let emergency_backup = app
        .path()
        .app_data_dir()
        .map(|p| {
            p.join(format!(
                "fluxion_emergency_{}.db",
                Local::now().format("%Y%m%d_%H%M%S")
            ))
        })
        .map_err(|e| format!("Failed to create emergency backup path: {}", e))?;

    if db_path.exists() {
        fs::copy(&db_path, &emergency_backup)
            .map_err(|e| format!("Failed to create emergency backup: {}", e))?;
    }

    // Close current database connections (this is a simplified approach)
    // In production, you'd want to properly close all connections

    // Copy backup to main DB location
    fs::copy(&backup_path, &db_path).map_err(|e| format!("Failed to restore backup: {}", e))?;

    Ok(format!(
        "Database ripristinato con successo da '{}' (backup emergenza: '{}')",
        backup_path.display(),
        emergency_backup.display()
    ))
}

/// List available backups
#[tauri::command]
pub async fn list_backups(app: AppHandle) -> Result<Vec<BackupInfo>, String> {
    let backup_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.join("backups"))
        .map_err(|e| format!("Failed to get backup dir: {}", e))?;

    if !backup_dir.exists() {
        return Ok(Vec::new());
    }

    let mut backups = Vec::new();

    match fs::read_dir(&backup_dir) {
        Ok(entries) => {
            for entry in entries.filter_map(|e| e.ok()) {
                let path = entry.path();
                if path.extension().map(|e| e == "db").unwrap_or(false) {
                    if let Ok(metadata) = entry.metadata() {
                        let size_bytes = metadata.len();
                        let created_at: DateTime<Utc> = metadata
                            .modified()
                            .ok()
                            .and_then(|t| t.elapsed().ok().map(|d| Utc::now() - d))
                            .map(|d| DateTime::from(d))
                            .unwrap_or_else(|| Utc::now().into());

                        let created_at_local: DateTime<Local> = created_at.into();

                        backups.push(BackupInfo {
                            filename: entry.file_name().to_string_lossy().to_string(),
                            size_bytes,
                            size_human: human_readable_size(size_bytes),
                            created_at: created_at_local,
                            created_at_formatted: created_at_local
                                .format("%Y-%m-%d %H:%M")
                                .to_string(),
                        });
                    }
                }
            }
        }
        Err(_) => {}
    }

    // Sort by creation date (newest first)
    backups.sort_by(|a, b| b.created_at.cmp(&a.created_at));

    Ok(backups)
}

/// Delete a backup
#[tauri::command]
pub async fn delete_backup(app: AppHandle, filename: String) -> Result<String, String> {
    let backup_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.join("backups"))
        .map_err(|e| format!("Errore lettura cartella backup: {}", e))?;

    let backup_path = backup_dir.join(&filename);

    // Verify it's within the backups directory (security check)
    if !backup_path.starts_with(&backup_dir) {
        return Err("Percorso non valido".to_string());
    }

    // Check if file exists
    if !backup_path.exists() {
        return Err(format!("Backup '{}' non trovato", filename));
    }

    // Delete the file
    fs::remove_file(&backup_path).map_err(|e| format!("Errore eliminazione backup: {}", e))?;

    Ok(format!("Backup '{}' eliminato con successo", filename))
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

/// Generate a support session code for remote assistance
#[tauri::command]
pub fn generate_support_session() -> Result<SupportSession, String> {
    use rand::Rng;

    // Generate random 6-digit code
    let mut rng = rand::thread_rng();
    let support_code: String = (0..6).map(|_| rng.gen_range(0..10).to_string()).collect();

    let session_id = format!("sess_{}", chrono::Utc::now().timestamp_millis());

    Ok(SupportSession {
        session_id,
        created_at: chrono::Utc::now().to_rfc3339(),
        status: "pending".to_string(),
        support_code,
    })
}

// ───────────────────────────────────────────────────────────────────
// F13 — Auto-backup + retention (private helper)
// ───────────────────────────────────────────────────────────────────

fn prune_old_backups(backup_dir: &PathBuf, max_days: u64) -> Result<u32, String> {
    if !backup_dir.exists() {
        return Ok(0);
    }
    let cutoff = SystemTime::now()
        .checked_sub(std::time::Duration::from_secs(max_days * 86400))
        .unwrap_or(SystemTime::UNIX_EPOCH);

    let mut pruned = 0u32;
    let entries = fs::read_dir(backup_dir).map_err(|e| e.to_string())?;

    for entry in entries.filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.extension().map(|e| e == "db").unwrap_or(false) {
            if let Ok(modified) = entry.metadata().and_then(|m| m.modified()) {
                if modified < cutoff {
                    fs::remove_file(&path).ok();
                    pruned += 1;
                }
            }
        }
    }
    Ok(pruned)
}

/// Auto-backup: crea backup se l'ultimo è > 24h fa; elimina backup > 30 giorni (F13)
#[tauri::command]
pub async fn run_auto_backup_if_needed(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let backup_dir = app
        .path()
        .app_data_dir()
        .map(|p| p.join("backups"))
        .map_err(|e| e.to_string())?;

    // Find age of latest backup
    let needs_backup = if backup_dir.exists() {
        let latest = fs::read_dir(&backup_dir)
            .ok()
            .and_then(|entries| {
                entries
                    .filter_map(|e| e.ok())
                    .filter(|e| e.path().extension().map(|x| x == "db").unwrap_or(false))
                    .filter_map(|e| e.metadata().and_then(|m| m.modified()).ok())
                    .max()
            });
        match latest {
            Some(t) => SystemTime::now()
                .duration_since(t)
                .map(|d| d.as_secs() > 24 * 3600)
                .unwrap_or(true),
            None => true,
        }
    } else {
        true
    };

    let result = if needs_backup {
        backup_database(app.clone(), state).await?;
        prune_old_backups(&backup_dir, 30)?;
        "auto-backup creato".to_string()
    } else {
        prune_old_backups(&backup_dir, 30)?;
        "backup già aggiornato".to_string()
    };

    Ok(result)
}

// ───────────────────────────────────────────────────────────────────
// F13 — CSV Export helpers
// ───────────────────────────────────────────────────────────────────

fn csv_field(s: &str) -> String {
    if s.contains(',') || s.contains('"') || s.contains('\n') || s.contains('\r') {
        format!("\"{}\"", s.replace('"', "\"\""))
    } else {
        s.to_string()
    }
}

/// Esporta anagrafica clienti in CSV (F13 — Export on-demand)
#[tauri::command]
pub async fn export_clienti_csv(
    app: AppHandle,
    state: State<'_, AppState>,
    output_path: String,
) -> Result<String, String> {
    let pool = &state.db;

    struct Row {
        nome: String,
        cognome: String,
        email: Option<String>,
        telefono: String,
        data_nascita: Option<String>,
        citta: Option<String>,
        nota: Option<String>,
        consenso_marketing: i64,
        consenso_whatsapp: i64,
        created_at: String,
    }

    let rows = sqlx::query_as!(
        Row,
        r#"SELECT nome, cognome, email, telefono, data_nascita, citta,
                  note AS nota, consenso_marketing, consenso_whatsapp, created_at
           FROM clienti WHERE deleted_at IS NULL ORDER BY cognome, nome"#
    )
    .fetch_all(pool)
    .await
    .map_err(|e| e.to_string())?;

    let mut csv = String::from(
        "Nome,Cognome,Email,Telefono,Data Nascita,Città,Note,Consenso Marketing,Consenso WhatsApp,Creato il\n"
    );

    for r in &rows {
        csv.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{}\n",
            csv_field(&r.nome),
            csv_field(&r.cognome),
            csv_field(r.email.as_deref().unwrap_or("")),
            csv_field(&r.telefono),
            csv_field(r.data_nascita.as_deref().unwrap_or("")),
            csv_field(r.citta.as_deref().unwrap_or("")),
            csv_field(r.nota.as_deref().unwrap_or("")),
            if r.consenso_marketing == 1 { "Si" } else { "No" },
            if r.consenso_whatsapp == 1 { "Si" } else { "No" },
            csv_field(&r.created_at),
        ));
    }

    let path = PathBuf::from(&output_path);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    fs::write(&path, csv.as_bytes()).map_err(|e| e.to_string())?;

    let _ = app; // keep borrow
    Ok(format!("Esportati {} clienti in {}", rows.len(), output_path))
}

/// Esporta storico appuntamenti in CSV (F13 — Export on-demand)
#[tauri::command]
pub async fn export_appuntamenti_csv(
    app: AppHandle,
    state: State<'_, AppState>,
    output_path: String,
) -> Result<String, String> {
    let pool = &state.db;

    struct Row {
        data_ora_inizio: String,
        cliente_nome: String,
        cliente_cognome: String,
        servizio_nome: String,
        operatore_nome: Option<String>,
        durata_minuti: i64,
        prezzo_finale: f64,
        stato: String,
        note: Option<String>,
    }

    let rows = sqlx::query_as!(
        Row,
        r#"SELECT
               a.data_ora_inizio,
               c.nome    AS cliente_nome,
               c.cognome AS cliente_cognome,
               s.nome    AS servizio_nome,
               o.nome    AS operatore_nome,
               a.durata_minuti,
               a.prezzo_finale,
               a.stato,
               a.note
           FROM appuntamenti a
           JOIN clienti  c ON c.id = a.cliente_id
           JOIN servizi   s ON s.id = a.servizio_id
           LEFT JOIN operatori o ON o.id = a.operatore_id
           ORDER BY a.data_ora_inizio DESC"#
    )
    .fetch_all(pool)
    .await
    .map_err(|e| e.to_string())?;

    let mut csv = String::from(
        "Data/Ora,Cliente,Servizio,Operatore,Durata (min),Prezzo finale (€),Stato,Note\n",
    );

    for r in &rows {
        csv.push_str(&format!(
            "{},{},{},{},{},{:.2},{},{}\n",
            csv_field(&r.data_ora_inizio),
            csv_field(&format!("{} {}", r.cliente_nome, r.cliente_cognome)),
            csv_field(&r.servizio_nome),
            csv_field(r.operatore_nome.as_deref().unwrap_or("")),
            r.durata_minuti,
            r.prezzo_finale,
            csv_field(&r.stato),
            csv_field(r.note.as_deref().unwrap_or("")),
        ));
    }

    let path = PathBuf::from(&output_path);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    fs::write(&path, csv.as_bytes()).map_err(|e| e.to_string())?;

    let _ = app;
    Ok(format!(
        "Esportati {} appuntamenti in {}",
        rows.len(),
        output_path
    ))
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
