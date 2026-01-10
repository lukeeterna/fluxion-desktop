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

    // Get voice-agent directory - try multiple locations
    let voice_agent_dir = find_voice_agent_dir(&app)?;

    println!("🎙️  Voice agent directory: {}", voice_agent_dir.display());

    // Find Python
    let python = find_python().ok_or("Python not found")?;

    // Load environment variables from .env file
    // Try voice-agent/.env first, then project root/.env
    let env_path_local = voice_agent_dir.join(".env");
    let env_path_root = voice_agent_dir.parent().unwrap_or(&voice_agent_dir).join(".env");
    let groq_key = load_groq_key(&env_path_local).or_else(|| load_groq_key(&env_path_root));

    if groq_key.is_none() {
        return Err("GROQ_API_KEY not found. Set it in .env file.".to_string());
    }

    println!("🔑 GROQ_API_KEY loaded from .env");

    // Start voice agent with environment variables
    let child = Command::new(&python)
        .arg("main.py")
        .arg("--port")
        .arg(VOICE_AGENT_PORT.to_string())
        .current_dir(&voice_agent_dir)
        .env("GROQ_API_KEY", groq_key.unwrap())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start voice agent: {}", e))?;

    let pid = child.id();
    println!("🎙️  Voice pipeline starting (PID: {})", pid);

    // Store process and drop lock before async wait
    *process_guard = Some(child);
    drop(process_guard);

    // Wait for server to start and verify it's running
    let mut attempts = 0;
    const MAX_ATTEMPTS: u32 = 10;

    while attempts < MAX_ATTEMPTS {
        std::thread::sleep(std::time::Duration::from_millis(500));
        attempts += 1;

        // Check if process is still running
        {
            let mut guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;
            if let Some(ref mut child) = *guard {
                match child.try_wait() {
                    Ok(Some(status)) => {
                        // Process exited early - read stderr for error
                        let stderr = child.stderr.take();
                        let error_msg = if let Some(mut err) = stderr {
                            use std::io::Read;
                            let mut buf = String::new();
                            err.read_to_string(&mut buf).ok();
                            buf
                        } else {
                            "No error output captured".to_string()
                        };
                        *guard = None;
                        return Err(format!(
                            "Voice agent exited with status {}: {}",
                            status, error_msg.trim()
                        ));
                    }
                    Ok(None) => {
                        // Still running, good
                    }
                    Err(e) => {
                        return Err(format!("Failed to check process status: {}", e));
                    }
                }
            }
        }

        // Try health check
        if let Ok(health) = check_voice_health_sync() {
            println!("✅ Voice pipeline started successfully (PID: {})", pid);
            return Ok(VoicePipelineStatus {
                running: true,
                port: VOICE_AGENT_PORT,
                pid: Some(pid),
                health: Some(health),
            });
        }
    }

    // Timeout but process is running - return success anyway
    println!("⚠️ Voice pipeline health check timeout, but process is running");
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

/// Find voice-agent directory
fn find_voice_agent_dir(app: &AppHandle) -> Result<std::path::PathBuf, String> {
    // List of possible locations to check
    let mut candidates = Vec::new();

    // 1. Resource directory (production)
    if let Ok(resource_dir) = app.path().resource_dir() {
        candidates.push(resource_dir.join("voice-agent"));
    }

    // 2. Current working directory
    if let Ok(cwd) = std::env::current_dir() {
        candidates.push(cwd.join("voice-agent"));
    }

    // 3. Executable directory parent (development on macOS)
    if let Ok(exe_path) = std::env::current_exe() {
        if let Some(exe_dir) = exe_path.parent() {
            // In development: target/debug/tauri-app
            // We need to go up to project root
            let mut dir = exe_dir.to_path_buf();
            for _ in 0..5 {
                candidates.push(dir.join("voice-agent"));
                if let Some(parent) = dir.parent() {
                    dir = parent.to_path_buf();
                } else {
                    break;
                }
            }
        }
    }

    // 4. Known development paths (macOS specific)
    candidates.push(std::path::PathBuf::from("/Volumes/MacSSD - Dati/fluxion/voice-agent"));
    candidates.push(std::path::PathBuf::from("/Volumes/MontereyT7/FLUXION/voice-agent"));

    // Find first existing directory
    for candidate in &candidates {
        if candidate.exists() && candidate.join("main.py").exists() {
            return Ok(candidate.clone());
        }
    }

    // Debug: print all candidates
    let paths: Vec<String> = candidates.iter().map(|p| p.display().to_string()).collect();
    Err(format!(
        "Voice agent directory not found. Tried:\n{}",
        paths.join("\n")
    ))
}

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

/// Synchronous health check for startup verification
fn check_voice_health_sync() -> Result<serde_json::Value, String> {
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(1))
        .build()
        .map_err(|e| e.to_string())?;

    let response = client
        .get(format!("http://127.0.0.1:{}/health", VOICE_AGENT_PORT))
        .send()
        .map_err(|e| format!("Health check failed: {}", e))?;

    response
        .json()
        .map_err(|e| format!("Failed to parse health response: {}", e))
}

/// Load GROQ_API_KEY from .env file
fn load_groq_key(env_path: &std::path::Path) -> Option<String> {
    // First check environment variable
    if let Ok(key) = std::env::var("GROQ_API_KEY") {
        if !key.is_empty() {
            return Some(key);
        }
    }

    // Then try to read from .env file
    if env_path.exists() {
        if let Ok(content) = std::fs::read_to_string(env_path) {
            for line in content.lines() {
                let line = line.trim();
                if line.starts_with("GROQ_API_KEY=") {
                    let key = line.trim_start_matches("GROQ_API_KEY=").trim();
                    if !key.is_empty() {
                        return Some(key.to_string());
                    }
                }
            }
        }
    }

    None
}
