// FLUXION - WhatsApp Commands
// Local WhatsApp automation via whatsapp-web.js (NO API costs!)

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{AppHandle, Manager};

// Global handle to WhatsApp child process
static WHATSAPP_PROCESS: Mutex<Option<Child>> = Mutex::new(None);

#[derive(Debug, Serialize, Deserialize)]
pub struct WhatsAppStatus {
    pub status: String,
    pub timestamp: Option<String>,
    pub phone: Option<String>,
    pub name: Option<String>,
    pub error: Option<String>,
    pub qr: Option<String>, // QR code data for WhatsApp Web login
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
            qr: None,
        });
    }

    let content =
        fs::read_to_string(&status_file).map_err(|e| format!("Failed to read status: {}", e))?;

    serde_json::from_str(&content).map_err(|e| format!("Failed to parse status: {}", e))
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
    let script_path = resource_dir.join("scripts").join("whatsapp-service.cjs");

    // Check if script exists
    if !script_path.exists() {
        // Try from project root (development)
        let dev_script = PathBuf::from("scripts/whatsapp-service.cjs");
        if !dev_script.exists() {
            return Err("WhatsApp service script not found".into());
        }
    }

    // Start the service in background
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args([
                "/C",
                "start",
                "/B",
                "node",
                "scripts/whatsapp-service.cjs",
                "start",
            ])
            .spawn()
            .map_err(|e| format!("Failed to start WhatsApp service: {}", e))?;
    }

    #[cfg(not(target_os = "windows"))]
    {
        Command::new("node")
            .args(["scripts/whatsapp-service.cjs", "start"])
            .spawn()
            .map_err(|e| format!("Failed to start WhatsApp service: {}", e))?;
    }

    Ok("WhatsApp service started. Check status for QR code.".into())
}

/// Auto-start WhatsApp service at app launch (non-blocking)
/// Called from lib.rs setup hook
pub fn auto_start_whatsapp(app: &AppHandle) {
    // Get project directory for script path
    let script_path = get_whatsapp_script_path(app);

    if !script_path.exists() {
        eprintln!("⚠️  WhatsApp service script not found: {:?}", script_path);
        eprintln!("   Run 'npm install' in the project directory to install dependencies");
        return;
    }

    // Check if Node.js is available
    let node_check = Command::new("node").arg("--version").output();

    if node_check.is_err() {
        eprintln!("⚠️  Node.js not found. WhatsApp auto-responder disabled.");
        eprintln!("   Install Node.js to enable WhatsApp functionality.");
        return;
    }

    println!("🟢 Starting WhatsApp service...");

    // Get the directory containing the script
    let script_dir = script_path.parent().unwrap_or(&script_path);
    let project_dir = script_dir.parent().unwrap_or(script_dir);

    // Start Node.js process in background
    let result = Command::new("node")
        .arg(&script_path)
        .arg("start")
        .current_dir(project_dir)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn();

    match result {
        Ok(child) => {
            println!("✅ WhatsApp service started (PID: {})", child.id());

            // Store process handle for cleanup
            if let Ok(mut guard) = WHATSAPP_PROCESS.lock() {
                *guard = Some(child);
            }
        }
        Err(e) => {
            eprintln!("❌ Failed to start WhatsApp service: {}", e);
            eprintln!("   Make sure dependencies are installed: npm install");
        }
    }
}

/// Stop WhatsApp service (cleanup on app exit)
pub fn stop_whatsapp_service() {
    if let Ok(mut guard) = WHATSAPP_PROCESS.lock() {
        if let Some(mut child) = guard.take() {
            println!("🛑 Stopping WhatsApp service...");
            let _ = child.kill();
        }
    }
}

/// Get the path to whatsapp-service.cjs
fn get_whatsapp_script_path(app: &AppHandle) -> PathBuf {
    // 1. Try bundled resources (production)
    if let Ok(resource_dir) = app.path().resource_dir() {
        let bundled_path = resource_dir.join("scripts").join("whatsapp-service.cjs");
        if bundled_path.exists() {
            return bundled_path;
        }
    }

    // 2. Try from current working directory (dev mode - cwd is project root)
    let cwd_path = PathBuf::from("scripts/whatsapp-service.cjs");
    if cwd_path.exists() {
        return cwd_path.canonicalize().unwrap_or(cwd_path);
    }

    // 3. Try from parent of cwd (dev mode - cwd might be src-tauri)
    let parent_path = PathBuf::from("../scripts/whatsapp-service.cjs");
    if parent_path.exists() {
        return parent_path.canonicalize().unwrap_or(parent_path);
    }

    // 4. Try relative to executable (dev mode fallback)
    if let Ok(exe_path) = std::env::current_exe() {
        if let Some(exe_dir) = exe_path.parent() {
            // In dev, exe is in target/debug, script is in project root
            // Go up from target/debug to project root, then to scripts
            for levels in &["../../scripts", "../../../scripts", "../../../../scripts"] {
                let dev_path = exe_dir.join(levels).join("whatsapp-service.cjs");
                if dev_path.exists() {
                    return dev_path.canonicalize().unwrap_or(dev_path);
                }
            }
        }
    }

    // 5. Fallback - return expected path even if not found
    PathBuf::from("scripts/whatsapp-service.cjs")
}

/// Send WhatsApp message (manual copy for now, auto-send when service ready)
#[tauri::command]
pub fn prepare_whatsapp_message(
    phone: String,
    message: String,
) -> Result<serde_json::Value, String> {
    // Format phone number
    let clean_phone = phone
        .chars()
        .filter(|c| c.is_ascii_digit())
        .collect::<String>();

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

    let content =
        fs::read_to_string(&queue_file).map_err(|e| format!("Failed to read queue: {}", e))?;

    serde_json::from_str(&content).map_err(|e| format!("Failed to parse queue: {}", e))
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

// ═══════════════════════════════════════════════════════════════════
// WhatsApp Config Management
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize, Deserialize)]
pub struct WhatsAppConfig {
    #[serde(rename = "autoResponderEnabled")]
    pub auto_responder_enabled: bool,
    #[serde(rename = "faqCategory")]
    pub faq_category: String,
    #[serde(rename = "welcomeMessage")]
    pub welcome_message: String,
    #[serde(rename = "businessName")]
    pub business_name: String,
    #[serde(rename = "responseDelay")]
    pub response_delay: u32,
    #[serde(rename = "maxResponsesPerHour")]
    pub max_responses_per_hour: u32,
}

impl Default for WhatsAppConfig {
    fn default() -> Self {
        Self {
            auto_responder_enabled: true,
            faq_category: "salone".into(),
            welcome_message: "Ciao! Sono l'assistente automatico. Come posso aiutarti?".into(),
            business_name: "FLUXION".into(),
            response_delay: 1000,
            max_responses_per_hour: 60,
        }
    }
}

/// Get WhatsApp config file path
fn get_config_file(app: &AppHandle) -> PathBuf {
    get_wa_session_dir(app).join("config.json")
}

/// Get WhatsApp auto-responder configuration
#[tauri::command]
pub fn get_whatsapp_config(app: AppHandle) -> Result<WhatsAppConfig, String> {
    let config_file = get_config_file(&app);

    if !config_file.exists() {
        let default = WhatsAppConfig::default();
        // Save default config
        let session_dir = get_wa_session_dir(&app);
        fs::create_dir_all(&session_dir).map_err(|e| e.to_string())?;
        fs::write(
            &config_file,
            serde_json::to_string_pretty(&default).unwrap(),
        )
        .map_err(|e| e.to_string())?;
        return Ok(default);
    }

    let content =
        fs::read_to_string(&config_file).map_err(|e| format!("Failed to read config: {}", e))?;

    serde_json::from_str(&content).map_err(|e| format!("Failed to parse config: {}", e))
}

/// Update WhatsApp auto-responder configuration
#[tauri::command]
pub fn update_whatsapp_config(
    app: AppHandle,
    config: serde_json::Value,
) -> Result<WhatsAppConfig, String> {
    let config_file = get_config_file(&app);

    // Load existing config or default
    let mut current = get_whatsapp_config(app.clone()).unwrap_or_default();

    // Merge updates
    if let Some(enabled) = config.get("autoResponderEnabled").and_then(|v| v.as_bool()) {
        current.auto_responder_enabled = enabled;
    }
    if let Some(category) = config.get("faqCategory").and_then(|v| v.as_str()) {
        current.faq_category = category.to_string();
    }
    if let Some(msg) = config.get("welcomeMessage").and_then(|v| v.as_str()) {
        current.welcome_message = msg.to_string();
    }
    if let Some(name) = config.get("businessName").and_then(|v| v.as_str()) {
        current.business_name = name.to_string();
    }
    if let Some(delay) = config.get("responseDelay").and_then(|v| v.as_u64()) {
        current.response_delay = delay as u32;
    }
    if let Some(max) = config.get("maxResponsesPerHour").and_then(|v| v.as_u64()) {
        current.max_responses_per_hour = max as u32;
    }

    // Save updated config
    let session_dir = get_wa_session_dir(&app);
    fs::create_dir_all(&session_dir).map_err(|e| e.to_string())?;
    fs::write(
        &config_file,
        serde_json::to_string_pretty(&current).unwrap(),
    )
    .map_err(|e| format!("Failed to save config: {}", e))?;

    Ok(current)
}

// ═══════════════════════════════════════════════════════════════════
// FAQ Learning System
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize, Deserialize)]
pub struct PendingQuestion {
    pub id: String,
    pub question: String,
    #[serde(rename = "fromPhone")]
    pub from_phone: String,
    #[serde(rename = "fromName")]
    pub from_name: String,
    pub category: String,
    pub timestamp: String,
    pub status: String, // pending | answered | saved_as_faq
    #[serde(rename = "operatorResponse")]
    pub operator_response: Option<String>,
    #[serde(rename = "responseTimestamp")]
    pub response_timestamp: Option<String>,
}

/// Get pending questions file path
fn get_pending_questions_file(app: &AppHandle) -> PathBuf {
    get_wa_session_dir(app).join("pending_questions.jsonl")
}

/// Get all pending questions for operator review
#[tauri::command]
pub fn get_pending_questions(app: AppHandle) -> Result<Vec<PendingQuestion>, String> {
    let file_path = get_pending_questions_file(&app);

    if !file_path.exists() {
        return Ok(vec![]);
    }

    let content = fs::read_to_string(&file_path)
        .map_err(|e| format!("Failed to read pending questions: {}", e))?;

    let questions: Vec<PendingQuestion> = content
        .lines()
        .filter(|line| !line.trim().is_empty())
        .filter_map(|line| serde_json::from_str(line).ok())
        .collect();

    Ok(questions)
}

/// Update a pending question (e.g., mark as saved_as_faq)
#[tauri::command]
pub fn update_pending_question_status(
    app: AppHandle,
    question_id: String,
    new_status: String,
) -> Result<(), String> {
    let file_path = get_pending_questions_file(&app);

    if !file_path.exists() {
        return Err("No pending questions file".into());
    }

    let content = fs::read_to_string(&file_path).map_err(|e| format!("Failed to read: {}", e))?;

    let updated: Vec<String> = content
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| {
            if let Ok(mut q) = serde_json::from_str::<PendingQuestion>(line) {
                if q.id == question_id {
                    q.status = new_status.clone();
                    return serde_json::to_string(&q).unwrap_or_else(|_| line.to_string());
                }
            }
            line.to_string()
        })
        .collect();

    fs::write(&file_path, updated.join("\n") + "\n")
        .map_err(|e| format!("Failed to write: {}", e))?;

    Ok(())
}

/// Delete a pending question
#[tauri::command]
pub fn delete_pending_question(app: AppHandle, question_id: String) -> Result<(), String> {
    let file_path = get_pending_questions_file(&app);

    if !file_path.exists() {
        return Ok(());
    }

    let content = fs::read_to_string(&file_path).map_err(|e| format!("Failed to read: {}", e))?;

    let filtered: Vec<&str> = content
        .lines()
        .filter(|line| {
            if let Ok(q) = serde_json::from_str::<PendingQuestion>(line) {
                return q.id != question_id;
            }
            true
        })
        .collect();

    fs::write(&file_path, filtered.join("\n") + "\n")
        .map_err(|e| format!("Failed to write: {}", e))?;

    Ok(())
}

/// Save a Q&A pair to custom FAQ file
#[tauri::command]
pub fn save_custom_faq(
    _app: AppHandle,
    question: String,
    answer: String,
    section: Option<String>,
) -> Result<(), String> {
    // Use project data directory for custom FAQ
    let data_dir = std::env::current_dir()
        .map_err(|e| e.to_string())?
        .join("data");

    fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;

    let faq_file = data_dir.join("faq_custom.md");
    let section_name = section.unwrap_or_else(|| "Risposte Operatore".to_string());

    // Create file with header if it doesn't exist
    if !faq_file.exists() {
        let header = r#"# FAQ Custom - Aggiunte dall'Operatore

> Questo file contiene le FAQ aggiunte manualmente dall'operatore.
> Il bot le usa per rispondere automaticamente alle domande future.

"#;
        fs::write(&faq_file, header).map_err(|e| e.to_string())?;
    }

    // Read current content
    let mut content =
        fs::read_to_string(&faq_file).map_err(|e| format!("Failed to read FAQ file: {}", e))?;

    // Check if section exists, if not add it
    let section_header = format!("## {}", section_name);
    if !content.contains(&section_header) {
        content.push_str(&format!("\n{}\n\n", section_header));
    }

    // Prepare new entry - clean question/answer
    let clean_question = question.replace([':', '\n'], " ");
    let clean_answer = answer.replace('\n', " ");
    let new_entry = format!("- {}: {}\n", clean_question.trim(), clean_answer.trim());

    // Append after section header
    if let Some(section_pos) = content.find(&section_header) {
        let insert_pos = content[section_pos..]
            .find('\n')
            .map(|p| section_pos + p + 1)
            .unwrap_or(content.len());

        // Find next section or end
        let next_section = content[insert_pos..].find("\n## ");
        let end_pos = next_section
            .map(|p| insert_pos + p)
            .unwrap_or(content.len());

        content.insert_str(end_pos, &new_entry);
    } else {
        content.push_str(&new_entry);
    }

    fs::write(&faq_file, content).map_err(|e| format!("Failed to save FAQ: {}", e))?;

    Ok(())
}

/// Get custom FAQs content
#[tauri::command]
pub fn get_custom_faqs(_app: AppHandle) -> Result<String, String> {
    let data_dir = std::env::current_dir()
        .map_err(|e| e.to_string())?
        .join("data");

    let faq_file = data_dir.join("faq_custom.md");

    if !faq_file.exists() {
        return Ok(String::new());
    }

    fs::read_to_string(&faq_file).map_err(|e| format!("Failed to read custom FAQs: {}", e))
}

/// Get count of pending questions (for badge)
#[tauri::command]
pub fn get_pending_questions_count(app: AppHandle) -> Result<usize, String> {
    let questions = get_pending_questions(app)?;
    Ok(questions
        .iter()
        .filter(|q| q.status == "pending" || q.status == "answered")
        .count())
}
