// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Pipeline Commands
// Manage Python voice agent server from Tauri
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::io::Write;
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Mutex;
use tauri::{AppHandle, Manager, State};

// Simple file logger for debugging
fn get_log_path() -> std::path::PathBuf {
    #[cfg(windows)]
    return std::env::var("TEMP")
        .map(|t| std::path::PathBuf::from(t).join("fluxion-voice.log"))
        .unwrap_or_else(|_| std::path::PathBuf::from(r"C:\Temp\fluxion-voice.log"));
    #[cfg(not(windows))]
    return std::path::PathBuf::from("/tmp/fluxion-voice.log");
}

fn log_voice(msg: &str) {
    if let Ok(mut file) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(get_log_path())
    {
        let timestamp = chrono::Local::now().format("%Y-%m-%d %H:%M:%S");
        let _ = writeln!(file, "[{}] {}", timestamp, msg);
    }
    println!("{}", msg);
}

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
static SELF_HEALING_ACTIVE: AtomicBool = AtomicBool::new(false);
const VOICE_AGENT_PORT: u16 = 3002;
const HEALTH_CHECK_INTERVAL_SECS: u64 = 30;
const MAX_RESTART_ATTEMPTS: u32 = 3;

// ────────────────────────────────────────────────────────────────────
// Commands
// ────────────────────────────────────────────────────────────────────

/// Start the voice agent Python server
#[tauri::command]
pub async fn start_voice_pipeline(app: AppHandle) -> Result<VoicePipelineStatus, String> {
    log_voice("========== START VOICE PIPELINE CALLED ==========");

    // Spawn process in a synchronous block to avoid holding MutexGuard across await
    let pid = {
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
                    let pid = child.id();
                    return Ok(VoicePipelineStatus {
                        running: true,
                        port: VOICE_AGENT_PORT,
                        pid: Some(pid),
                        health: None,
                    });
                }
                Err(_) => {
                    *process_guard = None;
                }
            }
        }

        // Load environment variables from .env file
        let voice_agent_dir = find_voice_agent_dir(&app).ok();
        let groq_key = load_groq_key_from_dirs(voice_agent_dir.as_deref());

        if groq_key.is_none() {
            log_voice("❌ GROQ_API_KEY not found");
            return Err("GROQ_API_KEY not found. Set it in .env file.".to_string());
        }
        log_voice("🔑 GROQ_API_KEY loaded");

        // Try sidecar binary first, then fall back to Python
        let key = groq_key.as_deref()
            .ok_or_else(|| "Groq API key non configurata".to_string())?;
        let child = try_start_sidecar(&app, key)
            .or_else(|sidecar_err| {
                log_voice(&format!("Sidecar not available ({}), trying Python...", sidecar_err));
                try_start_python(voice_agent_dir.as_deref(), key)
            })
            .map_err(|e| format!("Failed to start voice agent: {}", e))?;

        let pid = child.id();
        log_voice(&format!("🎙️  Voice pipeline starting (PID: {})", pid));

        // Store process
        *process_guard = Some(child);

        pid
    }; // MutexGuard is dropped here, before any await

    // Wait for server to start and verify it's running
    // Use a separate thread for blocking health checks to avoid tokio runtime conflicts
    let mut attempts = 0;
    const MAX_ATTEMPTS: u32 = 15;

    while attempts < MAX_ATTEMPTS {
        // Use tokio sleep instead of std::thread::sleep in async context
        tokio::time::sleep(std::time::Duration::from_millis(500)).await;
        attempts += 1;

        // Check if process is still running
        {
            let mut guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;
            if let Some(ref mut child) = *guard {
                match child.try_wait() {
                    Ok(Some(status)) => {
                        // Process exited early
                        *guard = None;
                        log_voice(&format!("❌ Voice agent exited with status {}", status));
                        return Err(format!(
                            "Voice agent exited with status {}. Check /tmp/fluxion-voice.log for details.",
                            status
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

        // Try health check using async client (no blocking in async context!)
        log_voice(&format!(
            "🔍 Health check attempt {}/{}",
            attempts, MAX_ATTEMPTS
        ));
        if let Ok(health) = check_voice_health().await {
            log_voice(&format!(
                "✅ Voice pipeline started successfully (PID: {})",
                pid
            ));
            // Start self-healing monitor
            start_self_healing(app.clone());
            return Ok(VoicePipelineStatus {
                running: true,
                port: VOICE_AGENT_PORT,
                pid: Some(pid),
                health: Some(health),
            });
        }
    }

    // Check one more time if process is still alive
    {
        let mut guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;
        if let Some(ref mut child) = *guard {
            match child.try_wait() {
                Ok(Some(status)) => {
                    // Process died
                    *guard = None;
                    log_voice(&format!("❌ Voice agent died with status {}", status));
                    return Err(format!("Voice agent died with status {}", status));
                }
                Ok(None) => {
                    // Still running but no health response - return success anyway
                    log_voice("⚠️ Voice pipeline health check timeout, but process is running");
                }
                Err(e) => {
                    log_voice(&format!("❌ Failed to check process: {}", e));
                }
            }
        } else {
            log_voice("❌ Process handle lost");
            return Err("Voice agent process handle lost".to_string());
        }
    }

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
    // Check process state (for processes started by Tauri)
    let (process_running, pid) = {
        let mut process_guard = VOICE_PROCESS.lock().map_err(|e| e.to_string())?;
        if let Some(ref mut child) = *process_guard {
            match child.try_wait() {
                Ok(Some(_)) => {
                    *process_guard = None;
                    (false, None)
                }
                Ok(None) => (true, Some(child.id())),
                Err(_) => {
                    *process_guard = None;
                    (false, None)
                }
            }
        } else {
            (false, None)
        }
    };

    // ALWAYS check HTTP health - server might be started externally (SSH, manual)
    // This fixes the bug where externally started servers were not detected
    let health = check_voice_health().await.ok();

    // Server is running if:
    // 1. We have a tracked process that's alive, OR
    // 2. The health endpoint responds (externally started server)
    let running = process_running || health.is_some();

    Ok(VoicePipelineStatus {
        running,
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
        .post(format!(
            "http://127.0.0.1:{}/api/voice/process",
            VOICE_AGENT_PORT
        ))
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

/// Process audio through voice pipeline (STT -> NLU -> TTS)
#[tauri::command]
pub async fn voice_process_audio(audio_hex: String) -> Result<VoiceResponse, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(120)) // Audio processing: Whisper STT (~30s) + Groq LLM + TTS
        .build()
        .map_err(|e| format!("Failed to create client: {}", e))?;

    let response = client
        .post(format!(
            "http://127.0.0.1:{}/api/voice/process",
            VOICE_AGENT_PORT
        ))
        .json(&serde_json::json!({ "audio_hex": audio_hex }))
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

/// Generate greeting from voice agent — retry 5x (800ms) se pipeline non ancora pronta
#[tauri::command]
pub async fn voice_greet() -> Result<VoiceResponse, String> {
    let client = reqwest::Client::new();
    let url = format!("http://127.0.0.1:{}/api/voice/greet", VOICE_AGENT_PORT);
    let mut last_err = String::new();
    for attempt in 0..5u8 {
        match client.post(&url).send().await {
            Ok(resp) => {
                let result: serde_json::Value = resp
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse response: {}", e))?;
                return Ok(VoiceResponse {
                    success: result["success"].as_bool().unwrap_or(false),
                    response: result["response"].as_str().map(String::from),
                    transcription: None,
                    intent: None,
                    audio_base64: result["audio_base64"].as_str().map(String::from),
                    error: result["error"].as_str().map(String::from),
                });
            }
            Err(e) if e.is_connect() && attempt < 4 => {
                last_err = e.to_string();
                tokio::time::sleep(std::time::Duration::from_millis(800)).await;
            }
            Err(e) => return Err(format!("Voice API request failed: {}", e)),
        }
    }
    Err(format!(
        "Voice pipeline non raggiungibile dopo 5 tentativi: {}",
        last_err
    ))
}

/// Text-to-speech only
#[tauri::command]
pub async fn voice_say(text: String) -> Result<VoiceResponse, String> {
    let client = reqwest::Client::new();

    let response = client
        .post(format!(
            "http://127.0.0.1:{}/api/voice/say",
            VOICE_AGENT_PORT
        ))
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
        .post(format!(
            "http://127.0.0.1:{}/api/voice/reset",
            VOICE_AGENT_PORT
        ))
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

/// Try to start voice agent from PyInstaller sidecar binary
fn try_start_sidecar(app: &AppHandle, groq_key: &str) -> Result<Child, String> {
    // Tauri sidecar convention: binaries/voice-agent-{target_triple}
    let target = current_target_triple();
    let binary_name = format!("voice-agent-{}", target);

    // Check resource dir (production bundle)
    let mut sidecar_path = None;
    if let Ok(resource_dir) = app.path().resource_dir() {
        let candidate = resource_dir.join("binaries").join(&binary_name);
        if candidate.exists() {
            sidecar_path = Some(candidate);
        }
    }

    // Check src-tauri/binaries (development)
    if sidecar_path.is_none() {
        if let Ok(exe_path) = std::env::current_exe() {
            let mut dir = exe_path
                .parent()
                .unwrap_or_else(|| std::path::Path::new("."))
                .to_path_buf();
            for _ in 0..6 {
                let candidate = dir.join("src-tauri").join("binaries").join(&binary_name);
                if candidate.exists() {
                    sidecar_path = Some(candidate);
                    break;
                }
                if let Some(parent) = dir.parent() {
                    dir = parent.to_path_buf();
                } else {
                    break;
                }
            }
        }
    }

    let path = sidecar_path.ok_or_else(|| format!("Sidecar binary '{}' not found", binary_name))?;

    log_voice(&format!("🎙️  Starting sidecar: {}", path.display()));

    Command::new(&path)
        .arg("--port")
        .arg(VOICE_AGENT_PORT.to_string())
        .env("GROQ_API_KEY", groq_key)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Sidecar spawn failed: {}", e))
}

/// Try to start voice agent from Python source
fn try_start_python(voice_agent_dir: Option<&std::path::Path>, groq_key: &str) -> Result<Child, String> {
    let dir = voice_agent_dir.ok_or("Voice agent directory not found")?;

    let python = find_python(Some(dir)).ok_or_else(|| {
        log_voice("❌ Python not found");
        "Python not found. Install Python 3.x".to_string()
    })?;
    log_voice(&format!("🐍 Python: {}, dir: {}", python, dir.display()));

    Command::new(&python)
        .arg("-u")
        .arg("main.py")
        .arg("--port")
        .arg(VOICE_AGENT_PORT.to_string())
        .current_dir(dir)
        .env("GROQ_API_KEY", groq_key)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Python spawn failed: {}", e))
}

/// Get current platform target triple for sidecar naming
fn current_target_triple() -> &'static str {
    #[cfg(all(target_os = "macos", target_arch = "aarch64"))]
    return "aarch64-apple-darwin";
    #[cfg(all(target_os = "macos", target_arch = "x86_64"))]
    return "x86_64-apple-darwin";
    #[cfg(all(target_os = "windows", target_arch = "x86_64"))]
    return "x86_64-pc-windows-msvc";
    #[cfg(not(any(
        all(target_os = "macos", target_arch = "aarch64"),
        all(target_os = "macos", target_arch = "x86_64"),
        all(target_os = "windows", target_arch = "x86_64"),
    )))]
    return "unknown";
}

/// Load GROQ_API_KEY from env or .env files
fn load_groq_key_from_dirs(voice_agent_dir: Option<&std::path::Path>) -> Option<String> {
    // First check environment variable
    if let Ok(key) = std::env::var("GROQ_API_KEY") {
        if !key.is_empty() {
            return Some(key);
        }
    }
    // Try voice-agent/.env, then project root/.env
    if let Some(dir) = voice_agent_dir {
        if let Some(key) = load_groq_key(&dir.join(".env")) {
            return Some(key);
        }
        if let Some(parent) = dir.parent() {
            if let Some(key) = load_groq_key(&parent.join(".env")) {
                return Some(key);
            }
        }
    }
    None
}

/// Start self-healing background task — health checks every 30s, auto-restart on crash
pub fn start_self_healing(app: AppHandle) {
    if SELF_HEALING_ACTIVE.swap(true, Ordering::SeqCst) {
        return; // Already running
    }

    log_voice("🛡️  Self-healing monitor started (30s interval)");

    tauri::async_runtime::spawn(async move {
        let mut consecutive_failures: u32 = 0;
        let mut restart_count: u32 = 0;

        loop {
            tokio::time::sleep(std::time::Duration::from_secs(HEALTH_CHECK_INTERVAL_SECS)).await;

            // Check if process is tracked
            let has_process = {
                let guard = VOICE_PROCESS.lock().unwrap_or_else(|e| e.into_inner());
                guard.is_some()
            };

            if !has_process {
                // No tracked process — nothing to heal
                consecutive_failures = 0;
                continue;
            }

            // Health check
            match check_voice_health().await {
                Ok(_) => {
                    consecutive_failures = 0;
                }
                Err(_) => {
                    consecutive_failures += 1;
                    log_voice(&format!(
                        "⚠️  Health check failed ({}/3)",
                        consecutive_failures
                    ));

                    if consecutive_failures >= 3 && restart_count < MAX_RESTART_ATTEMPTS {
                        log_voice("🔄 Self-healing: restarting voice pipeline...");

                        // Kill existing process
                        {
                            let mut guard =
                                VOICE_PROCESS.lock().unwrap_or_else(|e| e.into_inner());
                            if let Some(mut child) = guard.take() {
                                let _ = child.kill();
                            }
                        }

                        // Wait for port release
                        tokio::time::sleep(std::time::Duration::from_secs(2)).await;

                        // Restart
                        match start_voice_pipeline(app.clone()).await {
                            Ok(status) => {
                                log_voice(&format!(
                                    "✅ Self-healing restart successful (PID: {:?})",
                                    status.pid
                                ));
                                restart_count += 1;
                                consecutive_failures = 0;
                            }
                            Err(e) => {
                                log_voice(&format!("❌ Self-healing restart failed: {}", e));
                                restart_count += 1;
                            }
                        }

                        if restart_count >= MAX_RESTART_ATTEMPTS {
                            log_voice("❌ Self-healing: max restart attempts reached. Stopping monitor.");
                            break;
                        }
                    }
                }
            }
        }

        SELF_HEALING_ACTIVE.store(false, Ordering::SeqCst);
    });
}

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

    // 4. Windows: APPDATA path
    #[cfg(windows)]
    if let Ok(appdata) = std::env::var("APPDATA") {
        candidates.push(
            std::path::PathBuf::from(&appdata)
                .join("FLUXION")
                .join("voice-agent"),
        );
        candidates.push(
            std::path::PathBuf::from(&appdata)
                .join("fluxion")
                .join("voice-agent"),
        );
    }

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

/// Find Python executable - prioritizes venv if available
fn find_python(voice_agent_dir: Option<&std::path::Path>) -> Option<String> {
    // First, check for venv Python in voice-agent directory
    if let Some(dir) = voice_agent_dir {
        let venv_python = dir.join("venv/bin/python3");
        if venv_python.exists() {
            if Command::new(&venv_python)
                .arg("--version")
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false)
            {
                return Some(venv_python.to_string_lossy().to_string());
            }
        }
        // Also check Windows venv path
        let venv_python_win = dir.join("venv/Scripts/python.exe");
        if venv_python_win.exists() {
            if Command::new(&venv_python_win)
                .arg("--version")
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false)
            {
                return Some(venv_python_win.to_string_lossy().to_string());
            }
        }
    }

    // Try common full paths (OS-specific)
    #[cfg(windows)]
    let full_paths: &[&str] = &[
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        r"C:\Python39\python.exe",
        r"C:\Program Files\Python311\python.exe",
        r"C:\Program Files\Python310\python.exe",
        r"C:\Users\gianluca\AppData\Local\Programs\Python\Python311\python.exe",
    ];
    #[cfg(not(windows))]
    let full_paths: &[&str] = &[
        "/usr/bin/python3",
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/Current/bin/python3",
    ];

    for path in full_paths {
        if std::path::Path::new(path).exists() {
            if Command::new(path)
                .arg("--version")
                .output()
                .map(|o| o.status.success())
                .unwrap_or(false)
            {
                return Some(path.to_string());
            }
        }
    }

    // Fallback to PATH lookup
    if Command::new("python3")
        .arg("--version")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
    {
        return Some("python3".to_string());
    }

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

// ═══════════════════════════════════════════════════════════════════
// Voice Agent Configuration - Greeting Dinamico
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize)]
pub struct VoiceAgentConfig {
    pub nome_attivita: String,
    pub whatsapp_number: Option<String>,
    pub ehiweb_number: Option<String>,
}

/// Get voice agent configuration from database
/// Used by Python voice agent for dynamic greeting
#[tauri::command]
pub async fn get_voice_agent_config(
    pool: State<'_, SqlitePool>,
) -> Result<VoiceAgentConfig, String> {
    // Get nome_attivita
    let nome_attivita: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'nome_attivita'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    // Get whatsapp_number
    let whatsapp_number: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'whatsapp_number'")
            .fetch_optional(pool.inner())
            .await
            .ok()
            .flatten();

    // Get ehiweb_number
    let ehiweb_number: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'ehiweb_number'")
            .fetch_optional(pool.inner())
            .await
            .ok()
            .flatten();

    Ok(VoiceAgentConfig {
        nome_attivita: nome_attivita
            .map(|(v,)| v)
            .unwrap_or_else(|| "FLUXION".to_string()),
        whatsapp_number: whatsapp_number.map(|(v,)| v),
        ehiweb_number: ehiweb_number.map(|(v,)| v),
    })
}

/// Update voice agent configuration
#[tauri::command]
pub async fn update_voice_agent_greeting(
    pool: State<'_, SqlitePool>,
    nome_attivita: String,
) -> Result<(), String> {
    sqlx::query(
        "INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo, updated_at) 
         VALUES ('voice_greeting_name', ?, 'text', datetime('now'))",
    )
    .bind(&nome_attivita)
    .execute(pool.inner())
    .await
    .map_err(|e| e.to_string())?;

    Ok(())
}
