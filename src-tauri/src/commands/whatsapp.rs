// FLUXION - WhatsApp Commands
// Local WhatsApp automation via whatsapp-web.js (NO API costs!)

use std::fs;
use std::path::PathBuf;
#[allow(unused_imports)]
use std::process::Command;
use tauri::{AppHandle, Manager};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct WhatsAppStatus {
    pub status: String,
    pub timestamp: Option<String>,
    pub phone: Option<String>,
    pub name: Option<String>,
    pub error: Option<String>,
}

/// Get WhatsApp session directory
fn get_wa_session_dir(app: &AppHandle) -> PathBuf {
    let data_dir = app.path().app_data_dir().unwrap_or_default();
    data_dir.join(".whatsapp-session")
}

/// Get WhatsApp status file path
fn get_status_file(app: &AppHandle) -> PathBuf {
    get_wa_session_dir(app).join("status.json")
}

/// Check WhatsApp connection status
#[tauri::command]
pub fn get_whatsapp_status(app: AppHandle) -> Result<WhatsAppStatus, String> {
    let status_file = get_status_file(&app);

    if !status_file.exists() {
        return Ok(WhatsAppStatus {
            status: "not_initialized".into(),
            timestamp: None,
            phone: None,
            name: None,
            error: None,
        });
    }

    let content = fs::read_to_string(&status_file)
        .map_err(|e| format!("Failed to read status: {}", e))?;

    serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse status: {}", e))
}

/// Check if WhatsApp is ready to send messages
#[tauri::command]
pub fn is_whatsapp_ready(app: AppHandle) -> Result<bool, String> {
    let status = get_whatsapp_status(app)?;
    Ok(status.status == "ready")
}

/// Start WhatsApp service (spawns background process)
#[tauri::command]
pub async fn start_whatsapp_service(app: AppHandle) -> Result<String, String> {
    let resource_dir = app.path().resource_dir().map_err(|e| e.to_string())?;
    let script_path = resource_dir.join("scripts").join("whatsapp-service.js");

    // Check if script exists
    if !script_path.exists() {
        // Try from project root (development)
        let dev_script = PathBuf::from("scripts/whatsapp-service.js");
        if !dev_script.exists() {
            return Err("WhatsApp service script not found".into());
        }
    }

    // Start the service in background
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/C", "start", "/B", "node", "scripts/whatsapp-service.js", "start"])
            .spawn()
            .map_err(|e| format!("Failed to start WhatsApp service: {}", e))?;
    }

    #[cfg(not(target_os = "windows"))]
    {
        Command::new("node")
            .args(["scripts/whatsapp-service.js", "start"])
            .spawn()
            .map_err(|e| format!("Failed to start WhatsApp service: {}", e))?;
    }

    Ok("WhatsApp service started. Check status for QR code.".into())
}

/// Send WhatsApp message (manual copy for now, auto-send when service ready)
#[tauri::command]
pub fn prepare_whatsapp_message(
    phone: String,
    message: String,
) -> Result<serde_json::Value, String> {
    // Format phone number
    let clean_phone = phone.chars().filter(|c| c.is_ascii_digit()).collect::<String>();

    // Generate WhatsApp URL
    let encoded_message = urlencoding::encode(&message);
    let wa_url = format!("https://wa.me/{}?text={}", clean_phone, encoded_message);

    Ok(serde_json::json!({
        "phone": clean_phone,
        "message": message,
        "url": wa_url,
        "instruction": "Click the link or copy message to send manually"
    }))
}

/// Get pending messages from queue
#[tauri::command]
pub fn get_pending_messages(app: AppHandle) -> Result<Vec<serde_json::Value>, String> {
    let queue_file = get_wa_session_dir(&app).join("message_queue.json");

    if !queue_file.exists() {
        return Ok(vec![]);
    }

    let content = fs::read_to_string(&queue_file)
        .map_err(|e| format!("Failed to read queue: {}", e))?;

    serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse queue: {}", e))
}

/// Add message to queue (for batch sending)
#[tauri::command]
pub fn queue_whatsapp_message(
    app: AppHandle,
    phone: String,
    message: String,
    template_name: Option<String>,
) -> Result<String, String> {
    let session_dir = get_wa_session_dir(&app);
    fs::create_dir_all(&session_dir).map_err(|e| e.to_string())?;

    let queue_file = session_dir.join("message_queue.json");

    // Read existing queue
    let mut queue: Vec<serde_json::Value> = if queue_file.exists() {
        let content = fs::read_to_string(&queue_file).unwrap_or_default();
        serde_json::from_str(&content).unwrap_or_default()
    } else {
        vec![]
    };

    // Add new message
    let msg_id = format!("msg_{}", chrono::Utc::now().timestamp_millis());
    queue.push(serde_json::json!({
        "id": msg_id,
        "phone": phone,
        "message": message,
        "template": template_name,
        "status": "pending",
        "created_at": chrono::Utc::now().to_rfc3339(),
    }));

    // Save queue
    fs::write(&queue_file, serde_json::to_string_pretty(&queue).unwrap())
        .map_err(|e| e.to_string())?;

    Ok(msg_id)
}

/// Get received messages log
#[tauri::command]
pub fn get_received_messages(
    app: AppHandle,
    limit: Option<usize>,
) -> Result<Vec<serde_json::Value>, String> {
    let messages_file = get_wa_session_dir(&app).join("messages.jsonl");

    if !messages_file.exists() {
        return Ok(vec![]);
    }

    let content = fs::read_to_string(&messages_file)
        .map_err(|e| format!("Failed to read messages: {}", e))?;

    let messages: Vec<serde_json::Value> = content
        .lines()
        .filter_map(|line| serde_json::from_str(line).ok())
        .collect();

    let limit = limit.unwrap_or(100);
    let start = messages.len().saturating_sub(limit);

    Ok(messages[start..].to_vec())
}
