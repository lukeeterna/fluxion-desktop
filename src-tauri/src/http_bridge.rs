// ═══════════════════════════════════════════════════════════════════
// FLUXION - HTTP Bridge for MCP Integration
// Connects MCP Server (5000) to Tauri Commands via HTTP (3001)
// ═══════════════════════════════════════════════════════════════════

use axum::{
    extract::{Json, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tauri::{AppHandle, Manager, WebviewWindow};
use tower_http::cors::{Any, CorsLayer};

// ────────────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
pub struct McpRequest {
    pub command: Option<String>,
    pub params: Option<Value>,
}

#[derive(Debug, Serialize)]
pub struct McpResponse {
    pub success: bool,
    pub data: Option<Value>,
    pub error: Option<String>,
    pub timestamp: String,
}

impl McpResponse {
    fn ok(data: Value) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            timestamp: chrono::Local::now().to_rfc3339(),
        }
    }

    fn err(msg: impl Into<String>) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(msg.into()),
            timestamp: chrono::Local::now().to_rfc3339(),
        }
    }
}

#[derive(Clone)]
pub struct BridgeState {
    pub app: AppHandle,
}

// ────────────────────────────────────────────────────────────────────
// HTTP Bridge Server
// ────────────────────────────────────────────────────────────────────

pub async fn start_http_bridge(
    app: AppHandle,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let state = BridgeState { app };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let router = Router::new()
        // Health & Info
        .route("/health", get(handle_health))
        .route("/api/mcp/ping", post(handle_ping))
        .route("/api/mcp/app-info", post(handle_app_info))
        // Screenshot & DOM
        .route("/api/mcp/screenshot", post(handle_screenshot))
        .route("/api/mcp/dom-content", post(handle_dom_content))
        // Script Execution
        .route("/api/mcp/execute-script", post(handle_execute_script))
        // Input Simulation
        .route("/api/mcp/mouse-click", post(handle_mouse_click))
        .route("/api/mcp/type-text", post(handle_type_text))
        .route("/api/mcp/key-press", post(handle_key_press))
        // Storage
        .route("/api/mcp/storage/get", post(handle_storage_get))
        .route("/api/mcp/storage/set", post(handle_storage_set))
        .route("/api/mcp/storage/clear", post(handle_storage_clear))
        .with_state(state)
        .layer(cors);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3001").await?;

    println!("🌉 HTTP Bridge started on http://127.0.0.1:3001");
    println!("   Endpoints: /health, /api/mcp/*");

    axum::serve(listener, router).await?;

    Ok(())
}

// ────────────────────────────────────────────────────────────────────
// Helper: Get Main Window
// ────────────────────────────────────────────────────────────────────

fn get_main_window(app: &AppHandle) -> Option<WebviewWindow> {
    app.get_webview_window("main")
}

// ────────────────────────────────────────────────────────────────────
// Handler: Health Check
// ────────────────────────────────────────────────────────────────────

async fn handle_health() -> impl IntoResponse {
    (
        StatusCode::OK,
        Json(json!({
            "status": "ok",
            "service": "FLUXION HTTP Bridge",
            "timestamp": chrono::Local::now().to_rfc3339()
        })),
    )
}

// ────────────────────────────────────────────────────────────────────
// Handler: Ping
// ────────────────────────────────────────────────────────────────────

async fn handle_ping(State(_state): State<BridgeState>) -> impl IntoResponse {
    let response = McpResponse::ok(json!({
        "status": "ok",
        "server": "FLUXION",
        "bridge": "HTTP",
        "timestamp": chrono::Local::now().to_rfc3339()
    }));
    (StatusCode::OK, Json(response))
}

// ────────────────────────────────────────────────────────────────────
// Handler: App Info
// ────────────────────────────────────────────────────────────────────

async fn handle_app_info(State(_state): State<BridgeState>) -> impl IntoResponse {
    let response = McpResponse::ok(json!({
        "name": "FLUXION",
        "version": env!("CARGO_PKG_VERSION"),
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH
    }));
    (StatusCode::OK, Json(response))
}

// ────────────────────────────────────────────────────────────────────
// Handler: Screenshot
// ────────────────────────────────────────────────────────────────────

async fn handle_screenshot(State(state): State<BridgeState>) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    match window.outer_size() {
        Ok(size) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "width": size.width,
                "height": size.height,
                "message": "Window dimensions captured. Full screenshot requires screen-capture plugin."
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!(
                "Failed to get window size: {}",
                e
            ))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: DOM Content
// ────────────────────────────────────────────────────────────────────

async fn handle_dom_content(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let selector = req
        .params
        .as_ref()
        .and_then(|p| p.get("selector"))
        .and_then(|s| s.as_str());

    let js = if let Some(sel) = selector {
        format!(
            r#"
            (function() {{
                const el = document.querySelector('{}');
                if (el) {{
                    return el.outerHTML;
                }} else {{
                    return 'Element not found: {}';
                }}
            }})()
            "#,
            sel, sel
        )
    } else {
        r#"
        (function() {
            return document.documentElement.outerHTML;
        })()
        "#
        .to_string()
    };

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "selector": selector,
                "message": "DOM query executed"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("JS execution failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Execute Script
// ────────────────────────────────────────────────────────────────────

async fn handle_execute_script(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let script = req
        .params
        .as_ref()
        .and_then(|p| p.get("script"))
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    if script.is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(McpResponse::err("Script is required")),
        );
    }

    match window.eval(&script) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "message": "Script executed successfully"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Script error: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Mouse Click
// ────────────────────────────────────────────────────────────────────

async fn handle_mouse_click(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let params = req.params.unwrap_or_default();
    let x = params.get("x").and_then(|v| v.as_f64()).unwrap_or(0.0);
    let y = params.get("y").and_then(|v| v.as_f64()).unwrap_or(0.0);
    let button = params
        .get("button")
        .and_then(|v| v.as_str())
        .unwrap_or("left");

    let button_code = match button {
        "right" => 2,
        "middle" => 1,
        _ => 0,
    };

    let js = format!(
        r#"
        (function() {{
            const el = document.elementFromPoint({}, {});
            if (el) {{
                const event = new MouseEvent('click', {{
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: {},
                    clientY: {},
                    button: {}
                }});
                el.dispatchEvent(event);
                return {{ success: true, element: el.tagName, id: el.id, className: el.className }};
            }} else {{
                return {{ success: false, error: 'No element at coordinates' }};
            }}
        }})()
        "#,
        x, y, x, y, button_code
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "x": x,
                "y": y,
                "button": button
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Click simulation failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Type Text
// ────────────────────────────────────────────────────────────────────

async fn handle_type_text(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let text = req
        .params
        .as_ref()
        .and_then(|p| p.get("text"))
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    let escaped_text = text
        .replace('\\', "\\\\")
        .replace('\'', "\\'")
        .replace('\n', "\\n");

    let js = format!(
        r#"
        (function() {{
            const el = document.activeElement;
            if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable)) {{
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {{
                    el.value += '{}';
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }} else {{
                    document.execCommand('insertText', false, '{}');
                }}
                return {{ success: true, element: el.tagName }};
            }} else {{
                return {{ success: false, error: 'No focusable element' }};
            }}
        }})()
        "#,
        escaped_text, escaped_text
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "text": text,
                "length": text.len()
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Type text failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Key Press
// ────────────────────────────────────────────────────────────────────

async fn handle_key_press(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let params = req.params.unwrap_or_default();
    let key = params
        .get("key")
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    let modifiers: Vec<String> = params
        .get("modifiers")
        .and_then(|m| m.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();

    let js = format!(
        r#"
        (function() {{
            const el = document.activeElement || document.body;
            const event = new KeyboardEvent('keydown', {{
                key: '{}',
                code: '{}',
                bubbles: true,
                cancelable: true,
                ctrlKey: {},
                shiftKey: {},
                altKey: {},
                metaKey: {}
            }});
            el.dispatchEvent(event);
            return {{ success: true, key: '{}', element: el.tagName }};
        }})()
        "#,
        key,
        key,
        modifiers.contains(&"Control".to_string()),
        modifiers.contains(&"Shift".to_string()),
        modifiers.contains(&"Alt".to_string()),
        modifiers.contains(&"Meta".to_string()),
        key
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "key": key,
                "modifiers": modifiers
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Key press failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Storage Get
// ────────────────────────────────────────────────────────────────────

async fn handle_storage_get(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let key = req
        .params
        .as_ref()
        .and_then(|p| p.get("key"))
        .and_then(|s| s.as_str());

    let js = if let Some(k) = key {
        format!(
            r#"
            (function() {{
                return localStorage.getItem('{}');
            }})()
            "#,
            k
        )
    } else {
        r#"
        (function() {
            const items = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return JSON.stringify(items);
        })()
        "#
        .to_string()
    };

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "key": key,
                "message": "Check console for localStorage value"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Get localStorage failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Storage Set
// ────────────────────────────────────────────────────────────────────

async fn handle_storage_set(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let params = req.params.unwrap_or_default();
    let key = params
        .get("key")
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();
    let value = params
        .get("value")
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    let escaped_value = value.replace('\\', "\\\\").replace('\'', "\\'");

    let js = format!(
        r#"
        (function() {{
            localStorage.setItem('{}', '{}');
            return true;
        }})()
        "#,
        key, escaped_value
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "key": key,
                "value": value
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Set localStorage failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Storage Clear
// ────────────────────────────────────────────────────────────────────

async fn handle_storage_clear(State(state): State<BridgeState>) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let js = r#"
        (function() {
            localStorage.clear();
            return true;
        })()
    "#;

    match window.eval(js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "message": "localStorage cleared"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!(
                "Clear localStorage failed: {}",
                e
            ))),
        ),
    }
}
