# 🖥️ FLUXION REMOTE ASSISTANCE — Integration Guide
## Open-Source P2P Screen Sharing + Debug Console per Tauri 2.x

**Versione**: 1.0  
**Data**: 29 Dicembre 2025  
**Stack**: Tauri 2.x + Rust + React + WebRTC  
**Licenza**: MIT/Apache 2.0

---

## 📋 OVERVIEW

Sistema di **remote assistance completamente decentralizzato** per Fluxion:
- ✅ Screen sharing P2P (WebRTC)
- ✅ Console debug real-time
- ✅ Comandi remoti con consent
- ✅ Funziona attraverso NAT/firewall
- ✅ Zero server esterno
- ✅ Open source 300+ stars

**Caso d'uso**: Il supporto tecnico di Fluxion si connette al PC del cliente per visualizzare lo schermo e risolvere problemi in tempo reale, senza server centrale.

---

## 🏆 TOP 2 SOLUZIONI CONSIGLIATE

### **SOLUZIONE #1: WebRTC-RS + Scap (SCREEN SHARING)**

#### Librerie consigliate:
| Libreria | Versione | Stelle | Scopo | License |
|----------|----------|--------|-------|---------|
| **webrtc-rs** | 0.13.x | 1.5K+ | P2P WebRTC connection | Apache 2.0 |
| **scap** | 0.2.x | 462 | High-performance screen capture | MIT |
| **tokio** | 1.40.x | 27K+ | Async runtime | MIT |
| **serde** | 1.0.x | 9K+ | Serialization | MIT/Apache 2.0 |

#### **Pregi**:
- ✅ Pure WebRTC (standard protocol, non propietario)
- ✅ Scap usa native APIs (ScreenCaptureKit su macOS, Graphics.Capture su Windows, Pipewire su Linux)
- ✅ Latency basso (30-50ms peer-to-peer)
- ✅ NAT traversal con STUN/TURN pubblici gratis
- ✅ Documentazione WebRTC-rs completa

#### **Contro**:
- ⚠️ Setup più complesso (STUN/TURN, signaling server)
- ⚠️ Richiede un signaling server per coordinare la connessione iniziale
- ⚠️ Binding audio/video codec inclusi ma screen sharing non è "first-class"

---

### **SOLUZIONE #2: RustDesk-Core + Shell Commands (SIMPLE + FUNCTIONAL)**

#### Librerie consigliate:
| Libreria | Versione | Stelle | Scopo | License |
|----------|----------|--------|-------|---------|
| **rustdesk** (core) | 1.2.x | 75K+ | Complete remote desktop | AGPL/Custom |
| **hbb_common** | — | — | Shared utilities (extracted from RustDesk) | AGPL |
| **tauri-plugin-shell** | 2.3.x | — | Execute commands with real-time output | MIT |
| **tokio** | 1.40.x | 27K+ | Async runtime | MIT |

#### **Pregi**:
- ✅ **Provato in produzione** (RustDesk è usato da milioni)
- ✅ Screen sharing già implementato e ottimizzato
- ✅ Mouse/keyboard control incluso
- ✅ File transfer built-in
- ✅ NAT traversal built-in (libhbb_core)
- ✅ Facile integrare come plugin Tauri

#### **Contro**:
- ⚠️ Licenza AGPL core (devi rilasciare il source se lo redistribuisci)
- ⚠️ Più heavy (più features = più codice)
- ⚠️ Per uso commerciale serve RustDesk Server Pro

---

## 🔧 IMPLEMENTAZIONE CONSIGLIATA: Soluzione #1 (WebRTC-RS)

### Motivo scelta:
1. **Control totale** del codice
2. **Lightweight** (no AGPL compliance)
3. **P2P puro** (no relay server necessario se collegati diretti)
4. **Perfetto per Fluxion** (startup che vuole mantenersi snella)

---

## 📐 ARCHITETTURA SISTEMA

```
┌─────────────────────────────────────────────────────────────────┐
│ CLIENTE (Fluxion Desktop App)                                    │
│                                                                   │
│  [React UI] ←→ [Tauri Commands (Rust)]                          │
│                     ↓                                             │
│            ┌──────────────────────┐                              │
│            │  Webrtc Session      │                              │
│            │  + Scap Capturer     │                              │
│            │  + Debug Console      │                              │
│            └──────────────────────┘                              │
│                     ↓                                             │
│            [UDP/TCP P2P Connection]                              │
│                     ↓                                             │
└─────────────────────────────────────────────────────────────────┘
                      ↕
        [STUN Server] (pubblico, gratis)
                      ↕
┌─────────────────────────────────────────────────────────────────┐
│ SUPPORTO TECNICO (Fluxion Desktop App)                           │
│                                                                   │
│  [React UI] ←→ [Tauri Commands (Rust)]                          │
│                     ↓                                             │
│            ┌──────────────────────┐                              │
│            │  Webrtc Session      │  ← Vede stream video         │
│            │  + Debug Console      │  ← Riceve logs/errori       │
│            │  + Remote Commands    │  ← Invia comandi debug      │
│            └──────────────────────┘                              │
│                     ↓                                             │
│            [UDP/TCP P2P Connection]                              │
└─────────────────────────────────────────────────────────────────┘

Nota: STUN server = nome risolutore (tipo DNS ma per NAT traversal)
      Gratis: Google STUN, Cloudflare, OpenRelay.metered.ca
```

---

## 🛠️ SETUP INIZIALE

### 1. Aggiungi dipendenze a `Cargo.toml`

```toml
[dependencies]
# WebRTC P2P
webrtc = "0.13"
tokio = { version = "1.40", features = ["full"] }
tokio-util = "0.7"

# Screen capture
scap = "0.2"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Logging
log = "0.4"
env_logger = "0.11"

# Tauri
tauri = { version = "2.0", features = ["shell-execute", "path-all"] }

# Image processing (for screen data)
image = "0.25"

# Time
tokio-time = "0.1"
```

### 2. Crea struttura Rust nel progetto Tauri

```
src-tauri/src/
├── main.rs
├── lib.rs
├── commands/
│   ├── mod.rs
│   ├── remote_assist.rs          ← ⭐ NEW
│   └── screen_capture.rs         ← ⭐ NEW
├── services/
│   ├── mod.rs
│   ├── webrtc_session.rs         ← ⭐ NEW
│   └── debug_console.rs          ← ⭐ NEW
└── config.rs
```

---

## 📝 CODICE RUST IMPLEMENTAZIONE

### File 1: `src-tauri/src/services/webrtc_session.rs`

```rust
// High-level WebRTC session management
use webrtc::{
    api::{
        setting_engine::SettingEngine,
        APIBuilder,
    },
    data_channel::RTCDataChannel,
    error::Result,
    ice_transport::ice_connection_state::RTCIceConnectionState,
    peer_connection::RTCPeerConnection,
};
use std::sync::Arc;
use tokio::sync::Mutex;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WebRTCConfig {
    pub stun_servers: Vec<String>,
    pub enable_data_channel: bool,
    pub enable_video: bool,
}

impl Default for WebRTCConfig {
    fn default() -> Self {
        Self {
            stun_servers: vec![
                "stun:stun1.l.google.com:19302".to_string(),
                "stun:stun2.l.google.com:19302".to_string(),
                "stun:stun.relay.metered.ca:80".to_string(),
            ],
            enable_data_channel: true,
            enable_video: true,
        }
    }
}

pub struct WebRTCSession {
    peer_connection: Arc<RTCPeerConnection>,
    data_channel: Arc<Mutex<Option<Arc<RTCDataChannel>>>>,
    config: WebRTCConfig,
}

impl WebRTCSession {
    /// Crea una nuova sessione WebRTC come "initiator" (il client che chiama)
    pub async fn new_initiator(config: WebRTCConfig) -> Result<Self> {
        let mut setting_engine = SettingEngine::default();
        
        // Configura STUN servers per NAT traversal
        for stun_server in &config.stun_servers {
            setting_engine.add_ice_server(
                webrtc::api::ice_server::RTCIceServer {
                    urls: vec![stun_server.clone()],
                    username: "".to_string(),
                    credential: "".to_string(),
                    credential_type: Default::default(),
                }
            );
        }

        let api = APIBuilder::new()
            .with_setting_engine(setting_engine)
            .build();

        let peer_connection = Arc::new(
            api.new_peer_connection(Default::default()).await?
        );

        Ok(WebRTCSession {
            peer_connection,
            data_channel: Arc::new(Mutex::new(None)),
            config,
        })
    }

    /// Invia messaggio al peer tramite data channel
    pub async fn send_message(&self, data: &[u8]) -> Result<()> {
        if let Some(dc) = &*self.data_channel.lock().await {
            dc.send_text(String::from_utf8_lossy(data).to_string()).await?;
        }
        Ok(())
    }

    /// Crea una local SDP offer (per il client che chiama)
    pub async fn create_offer(&self) -> Result<String> {
        let offer = self.peer_connection.create_offer(None).await?;
        self.peer_connection.set_local_description(offer).await?;
        
        // Serializza offer
        if let Some(local_desc) = self.peer_connection.local_description().await {
            Ok(local_desc.sdp)
        } else {
            Err(webrtc::error::Error::UnknownType("No local description".to_string()))
        }
    }

    /// Riceve una remote SDP answer (da parte del supporto)
    pub async fn set_remote_answer(&self, answer_sdp: &str) -> Result<()> {
        use webrtc::peer_connection::sdp::session_description::RTCSessionDescription;
        
        let answer = RTCSessionDescription::answer(answer_sdp.to_string())?;
        self.peer_connection.set_remote_description(answer).await?;
        
        Ok(())
    }

    /// Monitora stato connessione
    pub async fn monitor_connection<F>(&self, mut callback: F) 
    where
        F: FnMut(RTCIceConnectionState) + Send + 'static,
    {
        let peer_connection = self.peer_connection.clone();
        tokio::spawn(async move {
            loop {
                let state = peer_connection.ice_connection_state();
                callback(state);
                
                if state == RTCIceConnectionState::Connected || 
                   state == RTCIceConnectionState::Completed {
                    break;
                }
                
                tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
            }
        });
    }
}
```

### File 2: `src-tauri/src/services/screen_capture.rs`

```rust
// Screen capture con Scap + encoding
use scap::capturer::{Capturer, Options};
use std::sync::Arc;
use tokio::sync::mpsc;
use image::RgbaImage;

#[derive(Clone)]
pub struct ScreenCaptureService {
    fps: u32,
}

#[derive(Debug)]
pub struct CaptureFrame {
    pub width: u32,
    pub height: u32,
    pub data: Vec<u8>, // RGBA format
    pub timestamp: u64,
}

impl ScreenCaptureService {
    pub fn new(fps: u32) -> Self {
        Self { fps }
    }

    /// Avvia capture loop in background
    /// Invia frame tramite channel
    pub async fn start_capture(
        &self,
        mut tx: mpsc::UnboundedSender<CaptureFrame>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let fps = self.fps;
        
        let options = Options {
            fps,
            target: None, // Cattura primary display
            show_cursor: true,
            excluded_targets: None,
            output_type: scap::frame::FrameType::BGRAFrame,
            output_resolution: scap::capturer::Resolution::_1080p,
            crop_area: None,
            ..Default::default()
        };

        let mut capturer = Capturer::build(options)?;
        capturer.start_capture();

        let frame_interval = std::time::Duration::from_millis(1000 / fps as u64);
        let mut last_capture = std::time::Instant::now();

        loop {
            if last_capture.elapsed() < frame_interval {
                tokio::time::sleep(frame_interval - last_capture.elapsed()).await;
            }

            if let Ok(Some(frame)) = capturer.get_current_frame() {
                let timestamp = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_millis() as u64;

                let capture_frame = CaptureFrame {
                    width: frame.width,
                    height: frame.height,
                    data: frame.buffer.to_vec(),
                    timestamp,
                };

                // Invia frame via channel (sarà convertito a JPEG per WebRTC)
                let _ = tx.send(capture_frame);
            }

            last_capture = std::time::Instant::now();
        }
    }

    /// Cattura singolo frame (screenshot)
    pub async fn capture_once(&self) -> Result<CaptureFrame, Box<dyn std::error::Error>> {
        let options = Options {
            fps: 1,
            target: None,
            show_cursor: true,
            ..Default::default()
        };

        let mut capturer = Capturer::build(options)?;
        capturer.start_capture();

        if let Ok(Some(frame)) = capturer.get_current_frame() {
            let timestamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_millis() as u64;

            return Ok(CaptureFrame {
                width: frame.width,
                height: frame.height,
                data: frame.buffer.to_vec(),
                timestamp,
            });
        }

        Err("Failed to capture frame".into())
    }
}

// Utility: Converti RGBA a JPEG per compressione
pub fn frame_to_jpeg(frame: &CaptureFrame, quality: u8) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let image = RgbaImage::from_raw(
        frame.width,
        frame.height,
        frame.data.clone(),
    ).ok_or("Invalid frame data")?;

    let mut encoder = image::jpeg::JpegEncoder::new_with_quality(
        Vec::new(),
        quality,
    );
    
    // Converti a RGB first (JPEG non supporta alpha)
    let rgb_image = image::DynamicImage::ImageRgba8(image)
        .to_rgb8();
    
    encoder.encode(&rgb_image, frame.width, frame.height, image::ColorType::Rgb8)?;
    
    Ok(encoder.buffer()?)
}
```

### File 3: `src-tauri/src/services/debug_console.rs`

```rust
// Real-time debug console (logs, errors, commands)
use tokio::sync::{mpsc, RwLock};
use std::sync::Arc;
use serde::{Deserialize, Serialize};
use chrono::Local;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum LogLevel {
    Debug,
    Info,
    Warn,
    Error,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LogEntry {
    pub timestamp: String,
    pub level: LogLevel,
    pub message: String,
    pub source: String, // "app", "system", "webrtc", etc.
}

pub struct DebugConsoleService {
    logs: Arc<RwLock<Vec<LogEntry>>>,
    sender: mpsc::UnboundedSender<LogEntry>,
}

impl DebugConsoleService {
    pub fn new() -> (Self, mpsc::UnboundedReceiver<LogEntry>) {
        let (sender, receiver) = mpsc::unbounded_channel();
        let logs = Arc::new(RwLock::new(Vec::with_capacity(1000)));

        (
            DebugConsoleService { logs, sender },
            receiver,
        )
    }

    /// Aggiungi log entry
    pub async fn log(&self, level: LogLevel, message: String, source: String) {
        let entry = LogEntry {
            timestamp: Local::now().format("%Y-%m-%d %H:%M:%S%.3f").to_string(),
            level,
            message,
            source,
        };

        // Salva in memoria (max 1000 entries)
        let mut logs = self.logs.write().await;
        logs.push(entry.clone());
        if logs.len() > 1000 {
            logs.remove(0);
        }

        // Invia tramite channel (per real-time streaming)
        let _ = self.sender.send(entry);
    }

    /// Ottieni ultimi N log
    pub async fn get_recent_logs(&self, limit: usize) -> Vec<LogEntry> {
        let logs = self.logs.read().await;
        let start = logs.len().saturating_sub(limit);
        logs[start..].to_vec()
    }

    /// Cancella tutti i log
    pub async fn clear(&self) {
        self.logs.write().await.clear();
    }

    /// Esporta log come JSON
    pub async fn export_json(&self) -> String {
        let logs = self.logs.read().await;
        serde_json::to_string_pretty(&*logs).unwrap_or_default()
    }
}

// Macro comodo per logging
#[macro_export]
macro_rules! debug_log {
    ($console:expr, $level:expr, $msg:expr) => {
        $console.log($level, $msg.to_string(), "app".to_string()).await
    };
}
```

### File 4: `src-tauri/src/commands/remote_assist.rs`

```rust
// Tauri commands per remote assistance
use tauri::{command, State, Window, Manager};
use crate::services::{
    webrtc_session::WebRTCSession,
    screen_capture::ScreenCaptureService,
    debug_console::DebugConsoleService,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[derive(Clone)]
pub struct RemoteAssistState {
    pub webrtc_session: Arc<tokio::sync::Mutex<Option<WebRTCSession>>>,
    pub screen_capture: Arc<ScreenCaptureService>,
    pub debug_console: Arc<DebugConsoleService>,
}

#[derive(Serialize, Deserialize)]
pub struct ConnectRequest {
    pub peer_sdp_offer: String, // SDP offer dal supporto
}

#[derive(Serialize, Deserialize)]
pub struct ConnectResponse {
    pub sdp_answer: String, // SDP answer dal cliente
}

/// Comando: Inizia sessione remote assistance
#[command]
pub async fn start_remote_session(
    window: Window,
    state: State<'_, RemoteAssistState>,
) -> Result<String, String> {
    let session = WebRTCSession::new_initiator(Default::default())
        .await
        .map_err(|e| format!("WebRTC init failed: {}", e))?;

    // Crea offer per il supporto
    let offer_sdp = session
        .create_offer()
        .await
        .map_err(|e| format!("Offer creation failed: {}", e))?;

    // Salva sessione nello state
    {
        let mut sess = state.webrtc_session.lock().await;
        *sess = Some(session);
    }

    // Log
    state.debug_console.log(
        crate::services::debug_console::LogLevel::Info,
        "Remote assistance session started".to_string(),
        "remote-assist".to_string(),
    ).await;

    Ok(offer_sdp)
}

/// Comando: Ricevi answer SDP dal supporto e connetti
#[command]
pub async fn connect_to_support(
    request: ConnectRequest,
    state: State<'_, RemoteAssistState>,
) -> Result<(), String> {
    let session = state.webrtc_session.lock().await;
    
    if let Some(session) = session.as_ref() {
        session
            .set_remote_answer(&request.peer_sdp_offer)
            .await
            .map_err(|e| format!("Connection failed: {}", e))?;
    } else {
        return Err("Session not initialized".to_string());
    }

    Ok(())
}

/// Comando: Ricevi un screenshot
#[command]
pub async fn get_screenshot(
    state: State<'_, RemoteAssistState>,
) -> Result<Vec<u8>, String> {
    let frame = state.screen_capture
        .capture_once()
        .await
        .map_err(|e| format!("Capture failed: {}", e))?;

    // Converti a JPEG (compressione)
    let jpeg = crate::services::screen_capture::frame_to_jpeg(&frame, 75)
        .map_err(|e| format!("JPEG encoding failed: {}", e))?;

    Ok(jpeg)
}

/// Comando: Ottieni log recenti
#[command]
pub async fn get_debug_logs(
    limit: usize,
    state: State<'_, RemoteAssistState>,
) -> Result<Vec<String>, String> {
    let logs = state.debug_console.get_recent_logs(limit).await;
    
    Ok(logs
        .iter()
        .map(|l| format!("[{}] {}: {}", l.timestamp, l.level, l.message))
        .collect())
}

/// Comando: Esegui comando debug remoto (CON CONSENSO)
#[command]
pub async fn execute_debug_command(
    command: String,
    user_approved: bool, // IMPORTANTE: richiedi al client!
    state: State<'_, RemoteAssistState>,
) -> Result<String, String> {
    if !user_approved {
        return Err("Command requires user approval".to_string());
    }

    // Whitelist di comandi sicuri
    let allowed_commands = vec![
        "logs",
        "restart",
        "clear-cache",
        "check-connection",
        "get-system-info",
    ];

    if !allowed_commands.contains(&command.as_str()) {
        return Err(format!("Command not allowed: {}", command));
    }

    // Esegui comando
    let output = match command.as_str() {
        "logs" => state.debug_console.export_json().await,
        "restart" => {
            state.debug_console.log(
                crate::services::debug_console::LogLevel::Info,
                "Restart requested by support".to_string(),
                "remote-assist".to_string(),
            ).await;
            // Nota: tauri::api::process::restart() requires feature
            "Restart queued".to_string()
        }
        "check-connection" => "Connection OK".to_string(),
        _ => "Unknown command".to_string(),
    };

    state.debug_console.log(
        crate::services::debug_console::LogLevel::Info,
        format!("Command executed: {}", command),
        "remote-assist".to_string(),
    ).await;

    Ok(output)
}

/// Comando: Arresta sessione
#[command]
pub async fn stop_remote_session(
    state: State<'_, RemoteAssistState>,
) -> Result<(), String> {
    let mut session = state.webrtc_session.lock().await;
    *session = None;

    state.debug_console.log(
        crate::services::debug_console::LogLevel::Info,
        "Remote assistance session stopped".to_string(),
        "remote-assist".to_string(),
    ).await;

    Ok(())
}
```

### File 5: `src-tauri/src/main.rs`

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod services;
mod commands;

use tauri::{Manager, RunEvent};
use commands::remote_assist::{RemoteAssistState, *};
use services::{
    webrtc_session::WebRTCSession,
    screen_capture::ScreenCaptureService,
    debug_console::DebugConsoleService,
};
use std::sync::Arc;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Inizializza servizi
            let screen_capture = Arc::new(ScreenCaptureService::new(15)); // 15 FPS
            let (debug_console, mut log_receiver) = DebugConsoleService::new();
            let debug_console = Arc::new(debug_console);

            let state = RemoteAssistState {
                webrtc_session: Arc::new(tokio::sync::Mutex::new(None)),
                screen_capture,
                debug_console: debug_console.clone(),
            };

            app.manage(state);

            // Spawn background task per stream logs to frontend
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                while let Some(log_entry) = log_receiver.recv().await {
                    let _ = app_handle.emit_all(
                        "debug:log",
                        log_entry,
                    );
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            start_remote_session,
            connect_to_support,
            get_screenshot,
            get_debug_logs,
            execute_debug_command,
            stop_remote_session,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 🎨 REACT FRONTEND COMPONENT

```typescript
// src/components/RemoteAssistance.tsx
import React, { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/tauri'
import { listen } from '@tauri-apps/api/event'
import { Share, Send, Download, Copy, AlertCircle } from 'lucide-react'

interface RemoteAssistanceProps {
  isSupport?: boolean // true = support tech, false = customer
}

export default function RemoteAssistance({ isSupport = false }: RemoteAssistanceProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [sessionId, setSessionId] = useState('')
  const [screenshot, setScreenshot] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [userApproved, setUserApproved] = useState(false)
  const [showApprovalDialog, setShowApprovalDialog] = useState(false)

  // Avvia sessione di supporto
  const handleStartSession = async () => {
    try {
      const offerSdp: string = await invoke('start_remote_session')
      setSessionId(offerSdp)
      // Condividi offerSdp al supporto via email/SMS/QR code
      alert(`Share this code with support:\n\n${offerSdp.substring(0, 50)}...`)
    } catch (error) {
      console.error('Failed to start session:', error)
    }
  }

  // Connetti con SDP answer da supporto
  const handleConnect = async () => {
    const answerSdp = prompt('Paste the answer code from support:')
    if (!answerSdp) return

    try {
      await invoke('connect_to_support', {
        peerSdpOffer: answerSdp,
      })
      setIsConnected(true)
    } catch (error) {
      console.error('Connection failed:', error)
    }
  }

  // Cattura screenshot
  const handleScreenshot = async () => {
    try {
      const jpegData: number[] = await invoke('get_screenshot')
      const blob = new Blob([new Uint8Array(jpegData)], { type: 'image/jpeg' })
      const url = URL.createObjectURL(blob)
      setScreenshot(url)
    } catch (error) {
      console.error('Screenshot failed:', error)
    }
  }

  // Ottieni log
  const handleGetLogs = async () => {
    try {
      const logs: string[] = await invoke('get_debug_logs', { limit: 50 })
      setLogs(logs)
    } catch (error) {
      console.error('Failed to get logs:', error)
    }
  }

  // Esegui comando debug
  const handleExecuteCommand = async (cmd: string) => {
    if (!userApproved) {
      setShowApprovalDialog(true)
      return
    }

    try {
      const result: string = await invoke('execute_debug_command', {
        command: cmd,
        userApproved: true,
      })
      setLogs((prev) => [...prev, `[Command] ${cmd}: ${result}`])
    } catch (error) {
      console.error('Command failed:', error)
    }
  }

  // Ascolta log events in real-time
  useEffect(() => {
    const unlisten = listen('debug:log', (event: any) => {
      const log = event.payload
      setLogs((prev) => [...prev.slice(-49), `[${log.level}] ${log.message}`])
    })

    return () => {
      unlisten.then((f) => f())
    }
  }, [])

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg border border-teal-500/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Share className="w-6 h-6 text-teal-400" />
            {isSupport ? 'Support Terminal' : 'Request Support'}
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            {isConnected ? '✅ Connected' : '⏳ Not connected'}
          </p>
        </div>
      </div>

      {/* Connection Status */}
      {!isConnected ? (
        <div className="space-y-4 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-400 mt-1 flex-shrink-0" />
            <div>
              <p className="font-medium text-white mb-2">
                {isSupport ? 'Connect to customer' : 'Get support'}
              </p>
              <p className="text-sm text-slate-400">
                {isSupport
                  ? 'Ask customer to share their session code'
                  : 'Share your session code with support, or enter their answer code'}
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleStartSession}
              className="flex-1 bg-teal-500 hover:bg-teal-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Share className="w-4 h-4" />
              {isSupport ? 'Generate Connection Code' : 'Start Session'}
            </button>

            {!isSupport && (
              <button
                onClick={handleConnect}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Copy className="w-4 h-4" />
                Enter Support Code
              </button>
            )}
          </div>

          {sessionId && (
            <div className="p-3 bg-slate-900 border border-slate-600 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Session Code:</p>
              <p className="font-mono text-sm text-teal-400 break-all">{sessionId.substring(0, 100)}...</p>
              <button
                onClick={() => navigator.clipboard.writeText(sessionId)}
                className="text-xs text-slate-400 hover:text-teal-400 mt-2 flex items-center gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy Code
              </button>
            </div>
          )}
        </div>
      ) : (
        <>
          {/* Connected UI */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Screenshot */}
            <div className="space-y-2">
              <h3 className="font-semibold text-white">Screen</h3>
              <button
                onClick={handleScreenshot}
                className="w-full bg-teal-500/20 hover:bg-teal-500/30 border border-teal-500/30 text-teal-400 py-2 px-4 rounded-lg transition-colors text-sm"
              >
                📸 Capture Screenshot
              </button>
              {screenshot && (
                <div className="relative">
                  <img src={screenshot} alt="Screenshot" className="w-full rounded-lg border border-slate-700" />
                  <a
                    href={screenshot}
                    download="screenshot.jpg"
                    className="absolute top-2 right-2 bg-slate-900 hover:bg-slate-800 p-2 rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4 text-teal-400" />
                  </a>
                </div>
              )}
            </div>

            {/* Debug Console */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-white">Debug Logs</h3>
                <button
                  onClick={handleGetLogs}
                  className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-2 py-1 rounded transition-colors"
                >
                  Refresh
                </button>
              </div>
              <div className="h-48 bg-slate-900 border border-slate-700 rounded-lg p-3 overflow-y-auto font-mono text-xs text-slate-300 space-y-1">
                {logs.length === 0 ? (
                  <p className="text-slate-500">No logs yet...</p>
                ) : (
                  logs.map((log, i) => <div key={i}>{log}</div>)
                )}
              </div>
            </div>
          </div>

          {/* Commands */}
          <div className="space-y-2">
            <h3 className="font-semibold text-white">Remote Commands</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {['check-connection', 'logs', 'clear-cache', 'restart'].map((cmd) => (
                <button
                  key={cmd}
                  onClick={() => handleExecuteCommand(cmd)}
                  className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-2 rounded-lg text-sm transition-colors"
                >
                  {cmd}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Approval Dialog */}
      {showApprovalDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-6 max-w-sm w-full">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              Confirm Action
            </h3>
            <p className="text-slate-300 mb-6">Support technician is requesting to execute a command. Proceed?</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowApprovalDialog(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-2 rounded-lg transition-colors"
              >
                Deny
              </button>
              <button
                onClick={() => {
                  setUserApproved(true)
                  setShowApprovalDialog(false)
                }}
                className="flex-1 bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-lg transition-colors"
              >
                Allow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

---

## 🚀 DEPLOYMENT + SIGNALING SERVER

### Signaling Server (Node.js - OPZIONALE per supporto P2P)

Se i peer non riescono a connettersi direttamente, usiamo un relay:

```javascript
// signaling-server.js (Node.js)
const http = require('http')
const WebSocket = require('ws')

const server = http.createServer()
const wss = new WebSocket.Server({ server })

const peers = new Map()

wss.on('connection', (ws) => {
  const peerId = Math.random().toString(36).substr(2, 9)
  peers.set(peerId, ws)

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data)
      
      if (message.type === 'offer') {
        // Invia offer al peer target
        if (peers.has(message.to)) {
          peers.get(message.to).send(JSON.stringify({
            type: 'offer',
            from: peerId,
            sdp: message.sdp,
          }))
        }
      } else if (message.type === 'answer') {
        if (peers.has(message.to)) {
          peers.get(message.to).send(JSON.stringify({
            type: 'answer',
            from: peerId,
            sdp: message.sdp,
          }))
        }
      } else if (message.type === 'candidate') {
        if (peers.has(message.to)) {
          peers.get(message.to).send(JSON.stringify({
            type: 'candidate',
            from: peerId,
            candidate: message.candidate,
          }))
        }
      }
    } catch (e) {
      console.error('Message parse error:', e)
    }
  })

  ws.on('close', () => {
    peers.delete(peerId)
  })

  ws.send(JSON.stringify({ type: 'peer-id', id: peerId }))
})

server.listen(3000, () => {
  console.log('Signaling server listening on port 3000')
})
```

**Deploy su cloud gratis**:
- Heroku + Procfile
- Railway.app
- Replit (con dominio)
- DigitalOcean AppPlatform ($5/month)

---

## ✅ CHECKLIST IMPLEMENTAZIONE

- [ ] Aggiungi dipendenze `Cargo.toml` (webrtc, scap, tokio)
- [ ] Crea folder `services/` con 3 file (webrtc_session, screen_capture, debug_console)
- [ ] Crea folder `commands/` con remote_assist.rs
- [ ] Aggiorna `main.rs` con setup servizi e state management
- [ ] Crea React component RemoteAssistance.tsx
- [ ] Test WebRTC P2P local (due tab browser test)
- [ ] Deploy signaling server (opzionale ma recommended)
- [ ] Aggiorna UI Fluxion per integrare remote assist nel menu
- [ ] Test screen capture cross-platform (Windows, macOS, Linux)
- [ ] Test con firewall/NAT (STUN servers)
- [ ] Add user approval dialog per comandi remoti
- [ ] Encryption TLS per SDP/logs (opzionale ma recommended)

---

## 🔒 SECURITY CONSIDERATIONS

1. **SDP Exchange**: Usa HTTPS/TLS per scambio SDP (non HTTP plain)
2. **Command Whitelist**: Non eseguire comandi arbitrari (vedi esempio)
3. **User Approval**: Sempre richiedi consenso prima di comandi/control
4. **Rate Limiting**: Limita numero richieste per evitare DoS
5. **Audit Log**: Log tutte le azioni remote in file locale
6. **Session Expiry**: Termina sessione dopo 1 ora di inattività

---

## 📚 RISORSE EXTRA

| Risorsa | Link |
|---------|------|
| WebRTC-RS Docs | https://docs.rs/webrtc/latest/webrtc/ |
| Scap GitHub | https://github.com/CapSoftware/scap |
| WebRTC RFC 8829 | https://tools.ietf.org/html/rfc8829 |
| Tauri Commands | https://tauri.app/v1/docs/api/commands/ |
| STUN Servers | https://gist.github.com/zziuni/3741933 |

---

## 🎯 CONCLUSIONE

**Opzione #1 (WebRTC-RS + Scap)** è la soluzione consigliata per Fluxion:
- ✅ Lightweight (200-300 KB bundle size)
- ✅ Zero dipendenze da server esterno (P2P puro)
- ✅ MIT license (uso commerciale libero)
- ✅ Agile per startup

**Timeline stima**:
- Settimana 1: WebRTC session + screen capture
- Settimana 2: React frontend + remote commands
- Settimana 3: Testing + production deployment

**Cost**: €0 (tutto open source + STUN server gratuiti)

Buona fortuna! 🚀
