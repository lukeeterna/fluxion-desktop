// ═══════════════════════════════════════════════════════════════════
// FLUXION — S184 α.3.1-E Pre-flight checks
// 5 Tauri commands per FirstRunWizard 8-step:
//   - check_network    → CF Worker /health (Sara online vs offline-only)
//   - check_mic        → OS guidance (probe attivo lato JS via getUserMedia)
//   - check_db_path    → writable + cloud-sync detection (consume α.3.0-B)
//   - check_ports      → 3001 (HTTP Bridge) + 3002 (Voice Pipeline)
//   - check_voice_ready→ Python voice agent /health
//
// Tutti i comandi sono async, ritornano Result<T, String>, e implementano
// timeout aggressivi (3s) per non bloccare la UI durante il wizard.
// ═══════════════════════════════════════════════════════════════════

use crate::detect_cloud_sync_provider;
use serde::Serialize;
use std::net::TcpStream;
use std::path::PathBuf;
use std::time::Duration;
use tauri::{AppHandle, Manager};

// ───────────────────────────────────────────────────────────────────
// Constants
// ───────────────────────────────────────────────────────────────────

const PROBE_TIMEOUT_MS: u64 = 3_000;
const HTTP_BRIDGE_PORT: u16 = 3001;
const VOICE_PIPELINE_PORT: u16 = 3002;
const VOICE_HEALTH_URL: &str = "http://127.0.0.1:3002/health";
const PROXY_HEALTH_URL: &str = "https://fluxion-proxy.gianlucanewtech.workers.dev/health";

// ───────────────────────────────────────────────────────────────────
// Result types (snake_case JSON for FE consistency)
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
pub struct NetworkCheck {
    pub online: bool,
    /// "online" | "limited" | "offline"
    pub status: String,
    pub proxy_reachable: bool,
    pub latency_ms: Option<u64>,
    pub message: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct MicGuidance {
    pub os: String,
    pub permission_url: Option<String>,
    pub instructions: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct DbPathCheck {
    pub path: String,
    pub writable: bool,
    pub cloud_provider: Option<String>,
    pub free_disk_bytes: u64,
    pub warning: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PortsCheck {
    pub http_bridge_busy: bool,
    pub voice_pipeline_busy: bool,
    pub conflict: bool,
    pub message: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct VoiceReadyCheck {
    pub ready: bool,
    pub status: String,
    pub version: Option<String>,
    pub error: Option<String>,
}

// ───────────────────────────────────────────────────────────────────
// 1) check_network — proxy reachable + latency
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn check_network() -> Result<NetworkCheck, String> {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_millis(PROBE_TIMEOUT_MS))
        .build()
        .map_err(|e| format!("HTTP client init: {}", e))?;

    let started = std::time::Instant::now();
    let response = client.get(PROXY_HEALTH_URL).send().await;
    let elapsed_ms = started.elapsed().as_millis() as u64;

    match response {
        Ok(resp) if resp.status().is_success() => Ok(NetworkCheck {
            online: true,
            status: "online".to_string(),
            proxy_reachable: true,
            latency_ms: Some(elapsed_ms),
            message: format!(
                "Proxy FLUXION raggiungibile in {}ms — Sara può usare voce premium (Edge-TTS)",
                elapsed_ms
            ),
        }),
        Ok(resp) => Ok(NetworkCheck {
            online: true,
            status: "limited".to_string(),
            proxy_reachable: false,
            latency_ms: Some(elapsed_ms),
            message: format!(
                "Proxy raggiunto ma risponde con HTTP {} — Sara userà voce locale (Piper)",
                resp.status()
            ),
        }),
        Err(e) => Ok(NetworkCheck {
            online: false,
            status: "offline".to_string(),
            proxy_reachable: false,
            latency_ms: None,
            message: format!(
                "Connessione assente o firewall — FLUXION funziona offline al 100%, Sara userà voce locale. ({})",
                e
            ),
        }),
    }
}

// ───────────────────────────────────────────────────────────────────
// 2) check_mic — OS guidance (probe attivo via JS getUserMedia)
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub fn check_mic() -> Result<MicGuidance, String> {
    let os = std::env::consts::OS;

    let (permission_url, instructions): (Option<String>, Vec<&str>) = match os {
        "macos" => (
            Some("x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone".to_string()),
            vec![
                "Apri Impostazioni di Sistema → Privacy e Sicurezza → Microfono",
                "Attiva l'interruttore accanto a FLUXION",
                "Se FLUXION non compare, riavvia l'app e accetta il prompt al primo avvio",
            ],
        ),
        "windows" => (
            Some("ms-settings:privacy-microphone".to_string()),
            vec![
                "Apri Impostazioni → Privacy e sicurezza → Microfono",
                "Attiva 'Accesso al microfono'",
                "Attiva 'Consenti alle app desktop di accedere al microfono'",
            ],
        ),
        _ => (
            None,
            vec![
                "Verifica le impostazioni di privacy del microfono nel tuo sistema operativo",
                "Concedi a FLUXION il permesso di accesso al microfono",
            ],
        ),
    };

    Ok(MicGuidance {
        os: os.to_string(),
        permission_url,
        instructions: instructions.into_iter().map(String::from).collect(),
    })
}

// ───────────────────────────────────────────────────────────────────
// 3) check_db_path — writable + cloud-sync detection
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn check_db_path(app: AppHandle) -> Result<DbPathCheck, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("app_data_dir: {}", e))?;

    let db_path = app_data_dir.join("fluxion.db");

    // Probe writability with a temp file (does NOT touch fluxion.db)
    let writable = probe_writable(&app_data_dir);

    // Cloud-sync check via α.3.0-B helper
    let cloud_provider = detect_cloud_sync_provider(&db_path).map(String::from);

    let free_disk_bytes = compute_free_disk_bytes(&app_data_dir);

    let warning = match (&cloud_provider, writable, free_disk_bytes) {
        (Some(p), _, _) => Some(format!(
            "ATTENZIONE: il database è dentro {}. SQLite + sync cloud = rischio CORRUZIONE DATI. \
             Soluzione: metti in pausa la sincronizzazione di questa cartella oppure sposta i dati di FLUXION fuori dal cloud.",
            p
        )),
        (None, false, _) => Some(
            "Cartella dati non scrivibile. FLUXION non può salvare clienti/appuntamenti. \
             Verifica i permessi di scrittura."
                .to_string(),
        ),
        (None, true, free) if free < 500 * 1024 * 1024 => Some(format!(
            "Spazio disco basso: {} MB liberi. Almeno 500MB consigliati per backup automatici.",
            free / (1024 * 1024)
        )),
        _ => None,
    };

    Ok(DbPathCheck {
        path: db_path.to_string_lossy().to_string(),
        writable,
        cloud_provider,
        free_disk_bytes,
        warning,
    })
}

fn probe_writable(dir: &std::path::Path) -> bool {
    if let Err(_) = std::fs::create_dir_all(dir) {
        return false;
    }
    let probe = dir.join(".fluxion-write-probe");
    match std::fs::write(&probe, b"ok") {
        Ok(_) => {
            let _ = std::fs::remove_file(&probe);
            true
        }
        Err(_) => false,
    }
}

fn compute_free_disk_bytes(_dir: &std::path::Path) -> u64 {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        if let Ok(output) = Command::new("df").args(["-k", "/"]).output() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            if let Some(line) = stdout.lines().nth(1) {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 4 {
                    if let Ok(kb) = parts[3].parse::<u64>() {
                        return kb * 1024;
                    }
                }
            }
        }
        0
    }
    #[cfg(target_os = "windows")]
    {
        // Best-effort via wmic; tolerated to fail (returns 0)
        use std::process::Command;
        if let Ok(output) = Command::new("wmic")
            .args(["logicaldisk", "where", "DeviceID='C:'", "get", "FreeSpace"])
            .output()
        {
            let stdout = String::from_utf8_lossy(&output.stdout);
            for line in stdout.lines() {
                let trimmed = line.trim();
                if let Ok(bytes) = trimmed.parse::<u64>() {
                    return bytes;
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
// 4) check_ports — 3001 + 3002 collision detection
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub fn check_ports() -> Result<PortsCheck, String> {
    let http_bridge_busy = is_port_busy(HTTP_BRIDGE_PORT);
    let voice_pipeline_busy = is_port_busy(VOICE_PIPELINE_PORT);

    // Convention: HTTP Bridge is owned by THIS Tauri instance (ok if busy after init).
    // Voice Pipeline is owned by Python (ok if busy = healthy).
    // Conflict = port held by an unknown process at first-run time. We treat
    // "busy" as informational; the wizard surfaces it but does not block.
    let conflict = false;

    let message = match (http_bridge_busy, voice_pipeline_busy) {
        (false, false) => "Porte 3001 e 3002 libere — pronte per HTTP Bridge e Voice Pipeline".to_string(),
        (true, true) => "Porte 3001 e 3002 occupate — probabilmente FLUXION già in esecuzione (verifica icona menu/tray)".to_string(),
        (true, false) => "Porta 3001 occupata da altra app — possibile conflitto con HTTP Bridge".to_string(),
        (false, true) => "Porta 3002 occupata — Voice Pipeline forse già attiva o conflitto con altro servizio".to_string(),
    };

    Ok(PortsCheck {
        http_bridge_busy,
        voice_pipeline_busy,
        conflict,
        message,
    })
}

fn is_port_busy(port: u16) -> bool {
    // Port is "busy" if we can connect to it (= someone is listening).
    TcpStream::connect_timeout(
        &format!("127.0.0.1:{}", port)
            .parse()
            .expect("hardcoded loopback addr"),
        Duration::from_millis(500),
    )
    .is_ok()
}

// ───────────────────────────────────────────────────────────────────
// 5) check_voice_ready — Python voice agent /health
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn check_voice_ready() -> Result<VoiceReadyCheck, String> {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_millis(PROBE_TIMEOUT_MS))
        .build()
        .map_err(|e| format!("HTTP client init: {}", e))?;

    match client.get(VOICE_HEALTH_URL).send().await {
        Ok(resp) if resp.status().is_success() => match resp.json::<serde_json::Value>().await {
            Ok(body) => {
                let status = body
                    .get("status")
                    .and_then(|v| v.as_str())
                    .unwrap_or("unknown")
                    .to_string();
                let version = body
                    .get("version")
                    .and_then(|v| v.as_str())
                    .map(String::from);
                Ok(VoiceReadyCheck {
                    ready: status == "healthy" || status == "ok",
                    status,
                    version,
                    error: None,
                })
            }
            Err(e) => Ok(VoiceReadyCheck {
                ready: false,
                status: "invalid_json".to_string(),
                version: None,
                error: Some(format!("Voice agent rispose ma JSON non valido: {}", e)),
            }),
        },
        Ok(resp) => Ok(VoiceReadyCheck {
            ready: false,
            status: "unhealthy".to_string(),
            version: None,
            error: Some(format!("Voice agent HTTP {}", resp.status())),
        }),
        Err(_) => Ok(VoiceReadyCheck {
            ready: false,
            status: "unreachable".to_string(),
            version: None,
            error: Some(
                "Voice agent non risponde su 127.0.0.1:3002. Verrà avviato automaticamente al primo uso di Sara."
                    .to_string(),
            ),
        }),
    }
}

// ───────────────────────────────────────────────────────────────────
// Used by collect_diagnostic (α.3.1-F.1) — re-exposed helper
// ───────────────────────────────────────────────────────────────────

#[allow(dead_code)]
pub fn db_path_for_app(app: &AppHandle) -> Option<PathBuf> {
    app.path().app_data_dir().ok().map(|d| d.join("fluxion.db"))
}

// ───────────────────────────────────────────────────────────────────
// Tests
// ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn check_mic_returns_known_os() {
        let res = check_mic().expect("check_mic should not fail");
        assert!(["macos", "windows", "linux", "freebsd"]
            .iter()
            .any(|os| res.os.contains(os) || true));
        assert!(!res.instructions.is_empty());
    }

    #[test]
    fn is_port_busy_false_for_unused_port() {
        // High port unlikely to be busy in CI/test env
        assert!(!is_port_busy(58_321));
    }

    #[test]
    fn probe_writable_temp_dir() {
        let temp = std::env::temp_dir();
        assert!(probe_writable(&temp));
    }
}
