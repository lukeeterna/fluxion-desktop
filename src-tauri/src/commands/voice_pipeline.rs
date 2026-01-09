// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Pipeline Commands
// Manage Python voice agent server from Tauri
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{AppHandle, Manager};

// ────────────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize)]
pub struct VoicePipelineStatus {
    pub running: bool,
    pub port: u16,
    pub pid: Option<u32>,
    pub health: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VoiceResponse {
    pub success: bool,
    pub response: Option<String>,
    pub transcription: Option<String>,
    pub intent: Option<String>,
    pub audio_base64: Option<String>,
    pub error: Option<String>,
}

// Global state for voice pipeline process
static VOICE_PROCESS: Mutex<Option<Child>> = Mutex::new(None);
const VOICE_AGENT_PORT: u16 = 3002;

// ────────────────────────────────────────────────────────────────────
// Commands
// ────────────────────────────────────────────────────────────────────

/// Start the voice agent Python server
#[tauri::command]
pub async fn start_voice_pipeline(app: AppHandle) -> Result<VoicePipelineStatus, String> {
    let mut process_guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;

    // Check if already running
    if let Some(ref mut child) = *process_guard {
        match child.try_wait() {
            Ok(Some(_)) => {
                // Process exited, clear it
                *process_guard = None;
            }
            Ok(None) => {
                // Still running
                return Ok(VoicePipelineStatus {
                    running: true,
                    port: VOICE_AGENT_PORT,
                    pid: Some(child.id()),
                    health: None,
                });
            }
            Err(_) => {
                *process_guard = None;
            }
        }
    }

    // Get voice-agent directory
    let resource_dir = app
        .path()
        .resource_dir()
        .map_err(|e| format!("Failed to get resource dir: {}", e))?;

    let voice_agent_dir = resource_dir.join("voice-agent");

    // Try project root if resource dir doesn't have it
    let voice_agent_dir = if voice_agent_dir.exists() {
        voice_agent_dir
    } else {
        // Development: use project root
        std::env::current_dir()
            .map_err(|e| e.to_string())?
            .join("voice-agent")
    };

    if !voice_agent_dir.exists() {
        return Err(format!(
            "Voice agent directory not found: {}",
            voice_agent_dir.display()
        ));
    }

    // Find Python
    let python = find_python().ok_or("Python not found")?;

    // Start voice agent
    let child = Command::new(&python)
        .arg("main.py")
        .arg("--port")
        .arg(VOICE_AGENT_PORT.to_string())
        .current_dir(&voice_agent_dir)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start voice agent: {}", e))?;

    let pid = child.id();
    *process_guard = Some(child);

    println!("🎙️  Voice pipeline started (PID: {})", pid);

    Ok(VoicePipelineStatus {
        running: true,
        port: VOICE_AGENT_PORT,
        pid: Some(pid),
        health: None,
    })
}

/// Stop the voice agent server
#[tauri::command]
pub async fn stop_voice_pipeline() -> Result<bool, String> {
    let mut process_guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;

    if let Some(mut child) = process_guard.take() {
        match child.kill() {
            Ok(_) => {
                println!("🛑 Voice pipeline stopped");
                Ok(true)
            }
            Err(e) => Err(format!("Failed to stop voice agent: {}", e)),
        }
    } else {
        Ok(false)
    }
}

/// Get voice pipeline status
#[tauri::command]
pub async fn get_voice_pipeline_status() -> Result<VoicePipelineStatus, String> {
    // Check process state
    let process_running = {
        let mut process_guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;
        if let Some(ref mut child) = *process_guard {
            match child.try_wait() {
                Ok(Some(_)) => {
                    *process_guard = None;
                    false
                }
                Ok(None) => true,
                Err(_) => {
                    *process_guard = None;
                    false
                }
            }
        } else {
            false
        }
    };

    // Check HTTP health
    let health = if process_running {
        check_voice_health().await.ok()
    } else {
        None
    };

    let pid = {
        let process_guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;
        process_guard.as_ref().map(|c| c.id())
    };

    Ok(VoicePipelineStatus {
        running: process_running,
        port: VOICE_AGENT_PORT,
        pid,
        health,
    })
}

/// Process text through voice pipeline
#[tauri::command]
pub async fn voice_process_text(text: String) -> Result<VoiceResponse, String> {
    let client = reqwest::Client::new();

    let response = client
        .post(format!("http://127.0.0.1:{}/api/voice/process", VOICE_AGENT_PORT))
        .json(&serde_json::json!({ "text": text }))
        .send()
        .await
        .map_err(|e| format!("Voice API request failed: {}", e))?;

    let result: serde_json::Value = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(VoiceResponse {
        success: result["success"].as_bool().unwrap_or(false),
        response: result["response"].as_str().map(String::from),
        transcription: result["transcription"].as_str().map(String::from),
        intent: result["intent"].as_str().map(String::from),
        audio_base64: result["audio_base64"].as_str().map(String::from),
        error: result["error"].as_str().map(String::from),
    })
}

/// Generate greeting from voice agent
#[tauri::command]
pub async fn voice_greet() -> Result<VoiceResponse, String> {
    let client = reqwest::Client::new();

    let response = client
        .post(format!("http://127.0.0.1:{}/api/voice/greet", VOICE_AGENT_PORT))
        .send()
        .await
        .map_err(|e| format!("Voice API request failed: {}", e))?;

    let result: serde_json::Value = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(VoiceResponse {
        success: result["success"].as_bool().unwrap_or(false),
        response: result["response"].as_str().map(String::from),
        transcription: None,
        intent: None,
        audio_base64: result["audio_base64"].as_str().map(String::from),
        error: result["error"].as_str().map(String::from),
    })
}

/// Text-to-speech only
#[tauri::command]
pub async fn voice_say(text: String) -> Result<VoiceResponse, String> {
    let client = reqwest::Client::new();

    let response = client
        .post(format!("http://127.0.0.1:{}/api/voice/say", VOICE_AGENT_PORT))
        .json(&serde_json::json!({ "text": text }))
        .send()
        .await
        .map_err(|e| format!("Voice API request failed: {}", e))?;

    let result: serde_json::Value = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(VoiceResponse {
        success: result["success"].as_bool().unwrap_or(false),
        response: None,
        transcription: None,
        intent: None,
        audio_base64: result["audio_base64"].as_str().map(String::from),
        error: result["error"].as_str().map(String::from),
    })
}

/// Reset voice conversation
#[tauri::command]
pub async fn voice_reset_conversation() -> Result<bool, String> {
    let client = reqwest::Client::new();

    let response = client
        .post(format!("http://127.0.0.1:{}/api/voice/reset", VOICE_AGENT_PORT))
        .send()
        .await
        .map_err(|e| format!("Voice API request failed: {}", e))?;

    let result: serde_json::Value = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(result["success"].as_bool().unwrap_or(false))
}

// ────────────────────────────────────────────────────────────────────
// Helper Functions
// ────────────────────────────────────────────────────────────────────

/// Find Python executable
fn find_python() -> Option<String> {
    // Try python3 first
    if Command::new("python3")
        .arg("--version")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
    {
        return Some("python3".to_string());
    }

    // Try python
    if Command::new("python")
        .arg("--version")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
    {
        return Some("python".to_string());
    }

    None
}

/// Check voice agent health
async fn check_voice_health() -> Result<serde_json::Value, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(2))
        .build()
        .map_err(|e| e.to_string())?;

    let response = client
        .get(format!("http://127.0.0.1:{}/health", VOICE_AGENT_PORT))
        .send()
        .await
        .map_err(|e| format!("Health check failed: {}", e))?;

    response
        .json()
        .await
        .map_err(|e| format!("Failed to parse health response: {}", e))
}
