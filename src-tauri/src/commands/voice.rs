// FLUXION - Voice Commands (Piper TTS)
// Text-to-Speech using Piper (offline, no API costs)

use std::fs;
use std::path::PathBuf;
use std::process::Command;
use tauri::{AppHandle, Manager};

/// Get the Piper installation directory
fn get_piper_dir(app: &AppHandle) -> PathBuf {
    let resource_dir = app.path().resource_dir().unwrap_or_default();
    resource_dir.join("piper")
}

/// Get Piper binary path based on platform
fn get_piper_binary(app: &AppHandle) -> PathBuf {
    let piper_dir = get_piper_dir(app);
    #[cfg(target_os = "windows")]
    {
        piper_dir.join("piper").join("piper.exe")
    }
    #[cfg(not(target_os = "windows"))]
    {
        piper_dir.join("piper").join("piper")
    }
}

/// Get voice model path
fn get_voice_path(app: &AppHandle) -> PathBuf {
    let piper_dir = get_piper_dir(app);
    piper_dir.join("voices").join("it_IT-paola-medium.onnx")
}

/// Check if Piper TTS is installed
#[tauri::command]
pub fn check_piper_installed(app: AppHandle) -> Result<bool, String> {
    let piper_binary = get_piper_binary(&app);
    let voice_path = get_voice_path(&app);

    Ok(piper_binary.exists() && voice_path.exists())
}

/// Get Piper installation status
#[tauri::command]
pub fn get_piper_status(app: AppHandle) -> Result<serde_json::Value, String> {
    let piper_binary = get_piper_binary(&app);
    let voice_path = get_voice_path(&app);

    Ok(serde_json::json!({
        "installed": piper_binary.exists() && voice_path.exists(),
        "piper_path": piper_binary.to_string_lossy(),
        "voice_path": voice_path.to_string_lossy(),
        "piper_exists": piper_binary.exists(),
        "voice_exists": voice_path.exists(),
    }))
}

/// Synthesize text to speech and return audio file path
#[tauri::command]
pub async fn synthesize_speech(
    app: AppHandle,
    text: String,
    output_filename: Option<String>,
) -> Result<String, String> {
    let piper_binary = get_piper_binary(&app);
    let voice_path = get_voice_path(&app);

    if !piper_binary.exists() {
        return Err("Piper not installed. Run: node scripts/setup-piper.js".into());
    }

    if !voice_path.exists() {
        return Err("Italian voice not installed".into());
    }

    // Create output directory
    let cache_dir = app.path().cache_dir().map_err(|e| e.to_string())?;
    let audio_dir = cache_dir.join("fluxion").join("audio");
    fs::create_dir_all(&audio_dir).map_err(|e| e.to_string())?;

    // Generate output filename
    let filename = output_filename
        .unwrap_or_else(|| format!("speech_{}.wav", chrono::Utc::now().timestamp_millis()));
    let output_path = audio_dir.join(&filename);

    // Run Piper
    let mut child = Command::new(&piper_binary)
        .arg("--model")
        .arg(&voice_path)
        .arg("--output_file")
        .arg(&output_path)
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start Piper: {}", e))?;

    // Write text to stdin
    use std::io::Write;
    if let Some(ref mut stdin) = child.stdin {
        stdin
            .write_all(text.as_bytes())
            .map_err(|e| e.to_string())?;
    }
    // Drop stdin to signal EOF
    drop(child.stdin.take());

    let output = child.wait_with_output().map_err(|e| e.to_string())?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Piper failed: {}", stderr));
    }

    Ok(output_path.to_string_lossy().to_string())
}

/// Synthesize and play speech directly
#[tauri::command]
pub async fn speak_text(app: AppHandle, text: String) -> Result<String, String> {
    // First synthesize
    let audio_path = synthesize_speech(app.clone(), text, None).await?;

    // Then play using system audio
    #[cfg(target_os = "macos")]
    {
        Command::new("afplay")
            .arg(&audio_path)
            .spawn()
            .map_err(|e| format!("Failed to play audio: {}", e))?;
    }

    #[cfg(target_os = "windows")]
    {
        Command::new("powershell")
            .args([
                "-c",
                &format!("(New-Object Media.SoundPlayer '{}').PlaySync()", audio_path),
            ])
            .spawn()
            .map_err(|e| format!("Failed to play audio: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        // Try aplay first, then paplay
        let result = Command::new("aplay").arg(&audio_path).spawn();

        if result.is_err() {
            Command::new("paplay")
                .arg(&audio_path)
                .spawn()
                .map_err(|e| format!("Failed to play audio: {}", e))?;
        }
    }

    Ok(audio_path)
}
